"""
Treino do detector de cedulas: uma CNN pequena treinada do zero.

Le as imagens de dataset/<classe>/ (ImageFolder mapeia cada pasta para uma
classe automaticamente), separa em treino/validacao, aplica data augmentation
apenas no treino e salva o melhor modelo em modelo.pt.

Uso:
    python treinar.py                 # padroes sensatos
    python treinar.py --epocas 30     # treina por mais tempo
    python treinar.py --tamanho 160   # imagens maiores (mais lento)

O checkpoint salvo (modelo.pt) guarda os pesos, os nomes das classes e o
tamanho da imagem, para o script de deteccao reconstruir tudo sozinho.
"""

import argparse

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from torchvision.datasets import ImageFolder

from localizacao import recortar_nota


class RecorteNota:
    """Transform que recorta a nota (CV classica) antes do resto do pipeline.

    Recebe e devolve uma PIL Image. Se nao achar nota (ex.: bancada vazia),
    devolve a imagem original inalterada. Aplicado no treino E na validacao,
    para que o modelo sempre veja a nota recortada -- igual ao que a deteccao
    ao vivo faz.
    """

    def __init__(self, area_min=0.02):
        self.area_min = area_min

    def __call__(self, img):
        bgr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
        recorte = recortar_nota(bgr, self.area_min)
        if recorte is None:
            return img
        return Image.fromarray(cv2.cvtColor(recorte, cv2.COLOR_BGR2RGB))


def parse_args():
    p = argparse.ArgumentParser(description="Treino da CNN detectora de cedulas.")
    p.add_argument("--dataset", type=str, default="dataset", help="Pasta raiz do dataset")
    p.add_argument("--saida-modelo", type=str, default="modelo.pt", help="Arquivo de saida do modelo")
    p.add_argument("--epocas", type=int, default=25, help="Numero de epocas")
    p.add_argument("--batch", type=int, default=32, help="Tamanho do batch")
    p.add_argument("--lr", type=float, default=1e-3, help="Taxa de aprendizado")
    p.add_argument("--tamanho", type=int, default=192, help="Lado da imagem (quadrada) na entrada")
    p.add_argument("--val-split", type=float, default=0.2, help="Fracao para validacao (0-1)")
    p.add_argument("--seed", type=int, default=42, help="Semente para reprodutibilidade")
    return p.parse_args()


def escolher_dispositivo():
    """Usa a GPU da Apple (MPS) se houver; senao CUDA; senao CPU."""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def construir_transforms(tamanho):
    """Transforms de treino (com augmentation) e de validacao (limpo)."""
    # Media/desvio simples (0.5) porque a rede e treinada do zero.
    normalizar = transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])

    treino = transforms.Compose([
        RecorteNota(),  # recorta a nota antes de tudo (mesma logica da deteccao)
        transforms.RandomResizedCrop(tamanho, scale=(0.7, 1.0)),
        transforms.RandomRotation(20),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        # ColorJitter ataca a variacao de exposicao/white balance.
        # brightness como tupla (min, max): so ESCURECE (0.5x a 1.0x), nunca
        # clareia -- as fotos ja estao muito bright, entao nao faz sentido
        # aumentar o brilho e estourar ainda mais para o branco.
        # Um pouco mais de contraste ajuda a "recuperar" imagens lavadas.
        transforms.ColorJitter(brightness=(0.5, 1.0), contrast=0.4, saturation=0.2),
        transforms.ToTensor(),
        normalizar,
    ])

    validacao = transforms.Compose([
        RecorteNota(),  # mesmo recorte, sem augmentation
        transforms.Resize((tamanho, tamanho)),
        transforms.ToTensor(),
        normalizar,
    ])
    return treino, validacao


def carregar_dados(args):
    """Monta os DataLoaders de treino e validacao com o mesmo split de indices.

    Cria duas visoes do mesmo diretorio (uma com augmentation, outra sem) e
    aplica o split por indices, garantindo que a validacao nao veja augmentation.
    """
    tf_treino, tf_val = construir_transforms(args.tamanho)
    ds_treino_full = ImageFolder(args.dataset, transform=tf_treino)
    ds_val_full = ImageFolder(args.dataset, transform=tf_val)

    n = len(ds_treino_full)
    if n == 0:
        raise SystemExit(f"Nenhuma imagem encontrada em '{args.dataset}'.")

    gerador = torch.Generator().manual_seed(args.seed)
    indices = torch.randperm(n, generator=gerador).tolist()
    n_val = int(n * args.val_split)
    idx_val, idx_treino = indices[:n_val], indices[n_val:]

    ds_treino = Subset(ds_treino_full, idx_treino)
    ds_val = Subset(ds_val_full, idx_val)

    dl_treino = DataLoader(ds_treino, batch_size=args.batch, shuffle=True)
    dl_val = DataLoader(ds_val, batch_size=args.batch, shuffle=False)
    return dl_treino, dl_val, ds_treino_full.classes


class CNNPequena(nn.Module):
    """CNN compacta: 3 blocos convolucionais + classificador."""

    def __init__(self, num_classes):
        super().__init__()

        def bloco(entrada, saida):
            return nn.Sequential(
                nn.Conv2d(entrada, saida, kernel_size=3, padding=1),
                nn.BatchNorm2d(saida),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
            )

        self.features = nn.Sequential(
            bloco(3, 16),    # -> 16 canais, metade da resolucao
            bloco(16, 32),   # -> 32 canais
            bloco(32, 64),   # -> 64 canais
            nn.AdaptiveAvgPool2d((4, 4)),  # fixa a saida em 4x4 (independe do tamanho)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def rodar_epoca(modelo, loader, criterio, dispositivo, otimizador=None):
    """Roda uma epoca. Se 'otimizador' for None, roda em modo avaliacao."""
    treinando = otimizador is not None
    modelo.train() if treinando else modelo.eval()

    perda_total, acertos, total = 0.0, 0, 0
    contexto = torch.enable_grad() if treinando else torch.no_grad()
    with contexto:
        for imgs, rotulos in loader:
            imgs, rotulos = imgs.to(dispositivo), rotulos.to(dispositivo)
            if treinando:
                otimizador.zero_grad()
            saidas = modelo(imgs)
            perda = criterio(saidas, rotulos)
            if treinando:
                perda.backward()
                otimizador.step()

            perda_total += perda.item() * imgs.size(0)
            acertos += (saidas.argmax(1) == rotulos).sum().item()
            total += imgs.size(0)

    return perda_total / total, acertos / total


def main():
    args = parse_args()
    torch.manual_seed(args.seed)

    dispositivo = escolher_dispositivo()
    print(f"Dispositivo: {dispositivo}")

    dl_treino, dl_val, classes = carregar_dados(args)
    print(f"Classes: {classes}")
    n_treino, n_val = len(dl_treino.dataset), len(dl_val.dataset)  # type: ignore[arg-type]
    print(f"Treino: {n_treino} imagens | Validacao: {n_val} imagens")

    modelo = CNNPequena(num_classes=len(classes)).to(dispositivo)
    criterio = nn.CrossEntropyLoss()
    otimizador = torch.optim.Adam(modelo.parameters(), lr=args.lr)

    melhor_acc = 0.0
    for epoca in range(1, args.epocas + 1):
        perda_tr, acc_tr = rodar_epoca(modelo, dl_treino, criterio, dispositivo, otimizador)
        perda_val, acc_val = rodar_epoca(modelo, dl_val, criterio, dispositivo)

        marca = ""
        if acc_val >= melhor_acc:
            melhor_acc = acc_val
            torch.save({
                "state_dict": modelo.state_dict(),
                "classes": classes,
                "tamanho": args.tamanho,
            }, args.saida_modelo)
            marca = "  <- melhor (salvo)"

        print(f"Epoca {epoca:2d}/{args.epocas} | "
              f"treino: perda {perda_tr:.3f} acc {acc_tr:.3f} | "
              f"val: perda {perda_val:.3f} acc {acc_val:.3f}{marca}")

    print(f"\nConcluido. Melhor acuracia de validacao: {melhor_acc:.3f}")
    print(f"Modelo salvo em: {args.saida_modelo}")


if __name__ == "__main__":
    main()

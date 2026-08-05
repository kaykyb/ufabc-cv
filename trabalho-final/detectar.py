"""
Deteccao ao vivo: roda o modelo treinado no feed da camera em tempo real.

Carrega modelo.pt (pesos + nomes das classes + tamanho da imagem), classifica
cada frame e mostra a previsao na tela. Se a classe prevista for uma cedula
com confianca acima do limiar, destaca "DETECTADA" e fala o valor em voz alta
(TTS), com debounce: a mesma nota so e repetida depois de --debounce segundos;
uma nota diferente e anunciada na hora.

Uso:
    python detectar.py                 # camera WC056, modelo.pt
    python detectar.py --limiar 0.9    # exige mais confianca para acusar deteccao
    python detectar.py --sem-voz       # desliga o anuncio falado

Teclas:
    q/ESC   sai
"""

import argparse
import platform
import shutil
import subprocess
import time

import cv2
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

# Reaproveita a arquitetura do treino, os utilitarios de camera da captura e a
# localizacao classica (mesma usada no treino para recortar a nota).
from treinar import CNNPequena, escolher_dispositivo
from capturar import resolver_camera
from localizacao import caixa_rotacionada, recortar_nota

# O que falar para cada classe detectada.
FALAS = {
    "nota_2": "dois reais",
    "nota_5": "cinco reais",
    "nota_10": "dez reais",
    "nota_20": "vinte reais",
    "nota_50": "cinquenta reais",
    "nota_100": "cem reais",
    "nota_200": "duzentos reais",
}


def criar_falador():
    """Retorna uma funcao falar(texto) nao bloqueante, ou None se nao houver TTS.

    No macOS usa o comando 'say' do sistema; em outros sistemas tenta o
    'espeak'. O processo roda em paralelo (Popen) para nao travar o laco de
    deteccao enquanto a frase e falada.
    """
    if platform.system() == "Darwin":
        return lambda texto: subprocess.Popen(["say", texto])
    if shutil.which("espeak"):
        return lambda texto: subprocess.Popen(["espeak", "-v", "pt-br", texto])
    return None


def parse_args():
    p = argparse.ArgumentParser(description="Deteccao ao vivo de cedulas.")
    p.add_argument("--camera", type=int, default=None,
                   help="Indice da camera. Se omitido, procura pela --nome-camera.")
    p.add_argument("--nome-camera", type=str, default="WC056",
                   help="Nome (ou parte) da camera a procurar no macOS (padrao: WC056)")
    p.add_argument("--modelo", type=str, default="modelo.pt", help="Arquivo do modelo treinado")
    p.add_argument("--limiar", type=float, default=0.8,
                   help="Confianca minima para acusar deteccao de cedula (0-1)")
    p.add_argument("--area-min", type=float, default=0.02,
                   help="Area minima da nota como fracao do frame, p/ localizar (0-1)")
    p.add_argument("--debounce", type=float, default=7.0,
                   help="Segundos ate repetir a fala da MESMA nota (padrao: 7)")
    p.add_argument("--sem-voz", action="store_true",
                   help="Desliga o anuncio falado (TTS)")
    return p.parse_args()


def carregar_modelo(caminho, dispositivo):
    """Carrega o checkpoint e reconstroi o modelo em modo avaliacao."""
    ckpt = torch.load(caminho, map_location=dispositivo)
    classes = ckpt["classes"]
    tamanho = ckpt["tamanho"]

    modelo = CNNPequena(num_classes=len(classes)).to(dispositivo)
    modelo.load_state_dict(ckpt["state_dict"])
    modelo.eval()
    return modelo, classes, tamanho


def construir_transform(tamanho):
    """Mesmo pre-processamento da validacao no treino (sem augmentation)."""
    return transforms.Compose([
        transforms.Resize((tamanho, tamanho)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
    ])


def prever(frame_bgr, modelo, transform, classes, dispositivo):
    """Classifica um frame (BGR do OpenCV). Retorna (classe, confianca)."""
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    tensor = transform(Image.fromarray(frame_rgb)).unsqueeze(0).to(dispositivo)
    with torch.no_grad():
        probs = F.softmax(modelo(tensor), dim=1)[0]
    idx = int(probs.argmax().item())
    return classes[idx], float(probs[idx].item())


def main():
    args = parse_args()

    dispositivo = escolher_dispositivo()
    print(f"Dispositivo: {dispositivo}")

    modelo, classes, tamanho = carregar_modelo(args.modelo, dispositivo)
    print(f"Modelo carregado. Classes: {classes} | tamanho de entrada: {tamanho}")

    transform = construir_transform(tamanho)

    falador = None if args.sem_voz else criar_falador()
    if not args.sem_voz and falador is None:
        print("TTS indisponivel neste sistema (sem 'say'/'espeak'); seguindo sem voz.")

    # Estado do debounce da fala: a mesma nota so e repetida depois de
    # args.debounce segundos; uma nota diferente e falada imediatamente.
    fala_classe = None
    fala_momento = 0.0

    indice_camera = resolver_camera(args)
    cap = cv2.VideoCapture(indice_camera)
    if not cap.isOpened():
        raise SystemExit(f"Nao consegui abrir a camera {indice_camera}. Tente --camera N.")

    janela = "Deteccao de cedulas"
    cv2.namedWindow(janela, cv2.WINDOW_NORMAL)
    print("Janela aberta. Foco nela e q/ESC para sair.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Falha ao ler frame. Encerrando.")
                break

            # Recorta a nota (mesma logica do treino). Sem nota na bancada ->
            # 'vazio' direto, sem passar pela rede.
            recorte = recortar_nota(frame, args.area_min)
            if recorte is None:
                classe, conf = "vazio", 1.0
            else:
                classe, conf = prever(recorte, modelo, transform, classes, dispositivo)

            # Considera "deteccao" quando a classe e uma cedula com confianca alta.
            eh_cedula = classe.startswith("nota_")
            detectou = eh_cedula and conf >= args.limiar

            # Anuncio falado com debounce.
            if detectou and falador is not None:
                agora = time.monotonic()
                if classe != fala_classe or agora - fala_momento >= args.debounce:
                    falador(FALAS.get(classe, classe))
                    fala_classe = classe
                    fala_momento = agora

            cor = (0, 255, 0) if detectou else (0, 165, 255) if eh_cedula else (200, 200, 200)

            # Desenha a caixa (segue a rotacao) so quando ha deteccao.
            caixa = caixa_rotacionada(frame, args.area_min) if detectou else None
            if caixa is not None:
                cv2.drawContours(frame, [caixa], 0, (0, 255, 0), 3)

            texto = f"{classe}: {conf * 100:.0f}%"
            if detectou:
                texto = f"{classe.replace('nota_', 'NOTA ')} DETECTADA ({conf * 100:.0f}%)"

            h, w = frame.shape[:2]
            cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
            cv2.putText(frame, texto, (12, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, cor, 2)

            cv2.imshow(janela, frame)
            if (cv2.waitKey(1) & 0xFF) in (ord("q"), 27):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

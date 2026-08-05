"""
Captura de imagens para o dataset do detector de cedulas.

Cenario: camera fixa em tripe sobre uma bancada preta.
Voce posiciona a cedula (girando, movendo, virando frente/verso) e aperta
uma tecla para salvar cada frame na classe ativa.

Uso basico:
    python capturar.py                 # abre a camera 0, classe inicial nota_50
    python capturar.py --camera 1      # usa outra camera
    python capturar.py --classe vazio  # comeca capturando o fundo vazio

Teclas (durante a execucao):
    ESPACO  salva o frame atual na classe ativa
    1..8    troca a classe ativa (ver legenda na tela)
    u       desfaz (apaga o ultimo arquivo salvo)
    g       liga/desliga a guia de enquadramento central
    q/ESC   sai
"""

import argparse
import json
import os
import platform
import subprocess
from datetime import datetime

import cv2

# Ordem fixa das classes -> mapeada para as teclas 1..8.
# Editar aqui para adicionar/remover cedulas. As pastas so sao criadas
# quando voce salva a primeira imagem naquela classe.
CLASSES = [
    "vazio",
    "nota_2",
    "nota_5",
    "nota_10",
    "nota_20",
    "nota_50",
    "nota_100",
    "nota_200",
]


def listar_cameras_macos():
    """Retorna a lista de nomes de cameras no macOS, na ordem do AVFoundation.

    Essa ordem coincide com o indice usado pelo OpenCV (backend AVFoundation),
    entao a posicao na lista serve como indice para cv2.VideoCapture.
    """
    try:
        saida = subprocess.check_output(
            ["system_profiler", "SPCameraDataType", "-json"],
            text=True, stderr=subprocess.DEVNULL,
        )
        dados = json.loads(saida).get("SPCameraDataType", [])
        return [cam.get("_name", "") for cam in dados]
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        return []


def encontrar_camera_por_nome(nome):
    """Procura uma camera cujo nome contenha 'nome' (sem diferenciar maiusculas).

    Retorna o indice (posicao na lista) ou None se nao encontrar.
    So funciona no macOS; em outros sistemas retorna None.
    """
    if platform.system() != "Darwin" or not nome:
        return None
    nomes = listar_cameras_macos()
    for idx, n in enumerate(nomes):
        if nome.lower() in n.lower():
            return idx
    return None


def resolver_camera(args):
    """Decide qual indice de camera usar a partir dos argumentos."""
    # --camera explicito sempre tem prioridade.
    if args.camera is not None:
        return args.camera

    idx = encontrar_camera_por_nome(args.nome_camera)
    if idx is not None:
        print(f"Camera '{args.nome_camera}' encontrada no indice {idx}.")
        return idx

    print(f"Camera '{args.nome_camera}' nao encontrada; usando indice 0. "
          f"(Force com --camera N se precisar.)")
    return 0


def parse_args():
    p = argparse.ArgumentParser(description="Captura de imagens do dataset de cedulas.")
    p.add_argument("--camera", type=int, default=None,
                   help="Indice da camera. Se omitido, procura pela --nome-camera.")
    p.add_argument("--nome-camera", type=str, default="WC056",
                   help="Nome (ou parte) da camera a procurar no macOS (padrao: WC056)")
    p.add_argument("--classe", type=str, default="nota_50",
                   help="Classe ativa inicial (padrao: nota_50)")
    p.add_argument("--saida", type=str, default="dataset",
                   help="Pasta raiz do dataset (padrao: dataset)")
    p.add_argument("--largura", type=int, default=None,
                   help="Forcar largura do frame. Se omitido, usa a resolucao nativa da camera.")
    p.add_argument("--altura", type=int, default=None,
                   help="Forcar altura do frame. Se omitido, usa a resolucao nativa da camera.")
    p.add_argument("--travar", action="store_true",
                   help="Desliga auto-exposicao e auto-white-balance (fixa a imagem).")
    p.add_argument("--exposicao", type=float, default=None,
                   help="Valor manual de exposicao (implica --travar). Ajuste testando.")
    p.add_argument("--wb-temp", type=int, default=None,
                   help="Temperatura manual do white balance em Kelvin (implica --travar).")
    return p.parse_args()


def configurar_camera(cap, args):
    """Tenta travar exposicao/white balance da camera e reporta o que foi aceito.

    Obs.: o suporte a essas propriedades depende da camera e do backend do
    OpenCV. No macOS (AVFoundation) muitas nao funcionam; nesse caso a saida
    mostra que o valor nao mudou e o jeito confiavel e travar por fora
    (app 'Webcam Settings' ou uvc-util) ou fixar a iluminacao.
    """
    travar = args.travar or args.exposicao is not None or args.wb_temp is not None
    if not travar:
        return

    print("Tentando travar exposicao/white balance...")

    # 0.25 = manual na maioria dos backends; 0.75 = auto. (Semantica varia.)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    cap.set(cv2.CAP_PROP_AUTO_WB, 0)

    if args.exposicao is not None:
        cap.set(cv2.CAP_PROP_EXPOSURE, args.exposicao)
    if args.wb_temp is not None:
        cap.set(cv2.CAP_PROP_WB_TEMPERATURE, args.wb_temp)

    # Le de volta para o usuario ver se a camera realmente aceitou.
    print(f"  auto_exposure -> {cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)}")
    print(f"  exposure      -> {cap.get(cv2.CAP_PROP_EXPOSURE)}")
    print(f"  auto_wb       -> {cap.get(cv2.CAP_PROP_AUTO_WB)}")
    print(f"  wb_temperature-> {cap.get(cv2.CAP_PROP_WB_TEMPERATURE)}")
    print("  Se os valores nao mudaram, a camera/backend nao suporta via OpenCV "
          "(trave por fora: app 'Webcam Settings' / uvc-util, ou fixe a luz).")


def contar_existentes(saida, classe):
    """Quantas imagens ja existem na pasta da classe (para o contador da tela)."""
    pasta = os.path.join(saida, classe)
    if not os.path.isdir(pasta):
        return 0
    return sum(1 for f in os.listdir(pasta) if f.lower().endswith(".jpg"))


def salvar_frame(frame, saida, classe):
    """Salva o frame na pasta da classe com nome unico (timestamp + ms). Retorna o caminho."""
    pasta = os.path.join(saida, classe)
    os.makedirs(pasta, exist_ok=True)
    agora = datetime.now()
    nome = f"{classe}_{agora.strftime('%Y%m%d_%H%M%S')}_{agora.microsecond // 1000:03d}.jpg"
    caminho = os.path.join(pasta, nome)
    cv2.imwrite(caminho, frame)
    return caminho


def desenhar_hud(frame, classe_ativa, total_classe, ultimo_salvo, mostrar_guia):
    """Desenha as informacoes e a legenda de teclas sobre uma copia do frame."""
    h, w = frame.shape[:2]
    vis = frame.copy()

    # Guia de enquadramento central (nao afeta a imagem salva).
    if mostrar_guia:
        cx0, cy0 = int(w * 0.20), int(h * 0.15)
        cx1, cy1 = int(w * 0.80), int(h * 0.85)
        cv2.rectangle(vis, (cx0, cy0), (cx1, cy1), (0, 200, 0), 1)

    # Faixa escura no topo para dar contraste ao texto.
    cv2.rectangle(vis, (0, 0), (w, 70), (0, 0, 0), -1)
    cv2.putText(vis, f"Classe ativa: {classe_ativa}  (salvas: {total_classe})",
                (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(vis, "ESPACO=salvar  1-8=trocar classe  u=desfazer  g=guia  q=sair",
                (10, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # Legenda das teclas de classe no rodape.
    legenda = "  ".join(f"[{i + 1}]{c}" for i, c in enumerate(CLASSES))
    cv2.rectangle(vis, (0, h - 28), (w, h), (0, 0, 0), -1)
    cv2.putText(vis, legenda, (10, h - 9),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    if ultimo_salvo:
        cv2.putText(vis, f"salvo: {os.path.basename(ultimo_salvo)}",
                    (10, h - 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    return vis


def main():
    args = parse_args()

    if args.classe not in CLASSES:
        raise SystemExit(f"Classe '{args.classe}' invalida. Opcoes: {', '.join(CLASSES)}")

    indice_camera = resolver_camera(args)
    cap = cv2.VideoCapture(indice_camera)
    if not cap.isOpened():
        raise SystemExit(f"Nao consegui abrir a camera {indice_camera}. "
                         f"Tente outro indice com --camera.")
    # So forca a resolucao se o usuario pedir explicitamente; caso contrario,
    # mantem a resolucao nativa da camera.
    if args.largura is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.largura)
    if args.altura is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.altura)

    configurar_camera(cap, args)

    classe_ativa = args.classe
    total = contar_existentes(args.saida, classe_ativa)
    ultimo_salvo = None
    mostrar_guia = True

    largura_real = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura_real = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera {indice_camera} aberta em {largura_real}x{altura_real}.")
    print(f"Salvando em: {os.path.abspath(args.saida)}")
    print("Janela aberta. Foco nela e use as teclas (q/ESC para sair).")

    janela = "Captura de cedulas"
    cv2.namedWindow(janela, cv2.WINDOW_NORMAL)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Falha ao ler frame da camera. Encerrando.")
                break

            vis = desenhar_hud(frame, classe_ativa, total, ultimo_salvo, mostrar_guia)
            cv2.imshow(janela, vis)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla in (ord("q"), 27):  # q ou ESC
                break
            elif tecla == ord(" "):  # salvar o frame ORIGINAL (sem o HUD)
                ultimo_salvo = salvar_frame(frame, args.saida, classe_ativa)
                total += 1
                print(f"[{total}] {ultimo_salvo}")
            elif tecla == ord("g"):
                mostrar_guia = not mostrar_guia
            elif tecla == ord("u"):  # desfazer ultimo save
                if ultimo_salvo and os.path.exists(ultimo_salvo):
                    os.remove(ultimo_salvo)
                    print(f"Removido: {ultimo_salvo}")
                    total = max(0, total - 1)
                    ultimo_salvo = None
                else:
                    print("Nada para desfazer.")
            elif ord("1") <= tecla <= ord("8"):  # trocar classe
                idx = tecla - ord("1")
                if idx < len(CLASSES):
                    classe_ativa = CLASSES[idx]
                    total = contar_existentes(args.saida, classe_ativa)
                    ultimo_salvo = None
                    print(f"Classe ativa: {classe_ativa} (salvas: {total})")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

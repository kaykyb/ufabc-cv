"""
Localizacao da cedula por visao computacional classica (sem rede).

Como a nota e a unica coisa clara sobre a bancada preta, um threshold de Otsu
separa nota (branco) do fundo (preto). O maior contorno e a nota.

Usado tanto no treino (para recortar a nota antes de classificar) quanto na
deteccao (para desenhar a caixa e recortar) -- assim os dois enxergam a mesma
coisa.
"""

import cv2


def _maior_contorno(frame_bgr, area_min_frac):
    """Retorna o maior contorno claro sobre fundo preto, ou None se for pequeno."""
    cinza = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    cinza = cv2.GaussianBlur(cinza, (5, 5), 0)
    _, mascara = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None

    maior = max(contornos, key=cv2.contourArea)
    h, w = frame_bgr.shape[:2]
    if cv2.contourArea(maior) < area_min_frac * w * h:
        return None
    return maior


def caixa_rotacionada(frame_bgr, area_min_frac=0.02):
    """4 pontos do retangulo rotacionado (para desenhar), ou None."""
    contorno = _maior_contorno(frame_bgr, area_min_frac)
    if contorno is None:
        return None
    return cv2.boxPoints(cv2.minAreaRect(contorno)).astype(int)


def recortar_nota(frame_bgr, area_min_frac=0.02, pad=0.05):
    """Recorta a nota (bounding box com uma folga 'pad'), ou None se nao achar."""
    contorno = _maior_contorno(frame_bgr, area_min_frac)
    if contorno is None:
        return None

    x, y, w, h = cv2.boundingRect(contorno)
    H, W = frame_bgr.shape[:2]
    p = int(pad * max(w, h))
    x0, y0 = max(0, x - p), max(0, y - p)
    x1, y1 = min(W, x + w + p), min(H, y + h + p)
    return frame_bgr[y0:y1, x0:x1]

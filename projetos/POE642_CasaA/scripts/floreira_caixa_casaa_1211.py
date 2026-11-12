"""A floreira do banho master do 1º Pavimento da Casa A na caixa do PDF (12/11).

Usuário, vendo o 12K: "CORRIJA AS FOLHAS DE VIDRO PARA SE ENCONTRAREM, CORRIJA O CONTORNO DA FLOREIRA E NÃO DEIXE AS
PLANTAS VERDES PASSAREM PELAS JANELAS". A floreira entre a janela da fachada (x 1345,3) e a janela do banho (x 1376,7),
de parede a parede (y 1463,9 a 1631,1): 167,2 x 31,4 px, 5,3 vezes mais comprida que larga. A caixa da imagem gerada no
Higgsfield (gpt_image_2, job 9f219839) é 4 vezes; antes ela entrava 35 px de largo, por cima da janela do banho, e as
folhas passavam da caixa. Aqui:
  - o fundo branco sai (o branco ligado à borda), como na primeira versão;
  - só a caixa fica (as folhas param na borda de fora da caixa, que encosta nas janelas e nas paredes);
  - a caixa fica comprida pelo miolo, sem achatar as plantas: costuras verticais de menor energia (seam carving, a
    inserção) passam pela terra e pela forração entre as touceiras (as folhas grandes custam caro e as pontas da caixa
    são proibidas) e cada costura é duplicada, até a proporção do PDF.
  python3 floreira_caixa_casaa_1211.py <saída do Higgsfield (PNG)>
grava `biblioteca-objetos/03-primeiro-pavimento/banho-master/floreira-espada-de-sao-jorge-e-folhagem.png`.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

SAIDA = (Path(__file__).resolve().parent.parent / "biblioteca-objetos" / "03-primeiro-pavimento" / "banho-master" /
         "floreira-espada-de-sao-jorge-e-folhagem.png")
CAIXA_IA = (261, 247, 2453, 792)          # a caixa na imagem do Higgsfield (x0, y0, x1, y1; a borda de baixo inclusa)
CAIXA_PDF = (167.2, 31.4)                 # comprimento x largura no PDF (px da final)
Q = {"escala": 0.5, "pontas": 34, "planta": 40.0, "folha": 160.0}


def recorte(im):
    """(cor, alfa 0 a 1): o fundo branco ligado à borda sai, a borda com o alfa pelo branco e a cor sem o branco."""
    d = 255 - im.min(axis=2)
    bg = (d <= 8).astype(np.uint8)
    _, lab = cv2.connectedComponents(bg)
    borda = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fundo = np.isin(lab, list(borda))
    a = (~fundo).astype(np.float32)
    perto = cv2.dilate(fundo.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~fundo
    a[perto] = np.clip((d[perto] - 4) / 22, 0, 1)
    m = a > 0.02
    cor = im.copy()
    cor[m] = np.clip((im[m] - (1 - a[m, None]) * 255) / a[m, None], 0, 255)
    return cor, a


def energia(cor):
    g = cv2.cvtColor(cor.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    e = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)) + np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))
    hsv = cv2.cvtColor(cor.astype(np.uint8), cv2.COLOR_BGR2HSV)
    planta = (hsv[..., 0] >= 25) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 55) & (hsv[..., 2] > 55)
    grande = cv2.morphologyEx(planta.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8)) > 0
    e += Q["planta"] * planta + Q["folha"] * (cv2.dilate(grande.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
    p = Q["pontas"]
    e[:, :p] = 1e6
    e[:, -p:] = 1e6
    return e


def costuras(e, k):
    """As k costuras verticais de menor energia (tiradas uma a uma), nos índices de coluna da imagem original."""
    h, w = e.shape
    idx = np.tile(np.arange(w), (h, 1))
    E = e.copy()
    saida = []
    for _ in range(k):
        hh, ww = E.shape
        M = E.copy()
        volta = np.zeros((hh, ww), np.int32)
        for r in range(1, hh):
            L = np.concatenate([[np.inf], M[r - 1, :-1]])
            R = np.concatenate([M[r - 1, 1:], [np.inf]])
            st = np.stack([L, M[r - 1], R])
            a = np.argmin(st, axis=0)
            M[r] += st[a, np.arange(ww)]
            volta[r] = a - 1
        j = int(np.argmin(M[-1]))
        cam = np.zeros(hh, np.int32)
        for r in range(hh - 1, -1, -1):
            cam[r] = j
            if r > 0:
                j += volta[r, j]
        saida.append(idx[np.arange(hh), cam].copy())
        fica = np.ones((hh, ww), bool)
        fica[np.arange(hh), cam] = False
        E = E[fica].reshape(hh, ww - 1)
        idx = idx[fica].reshape(hh, ww - 1)
    return saida


def main():
    im = cv2.imread(sys.argv[1]).astype(np.float32)
    cor, a = recorte(im)
    x0, y0, x1, y1 = CAIXA_IA
    P = np.dstack([cor, a * 255])[y0:y1 + 1, x0:x1]
    P = cv2.resize(P, None, fx=Q["escala"], fy=Q["escala"], interpolation=cv2.INTER_AREA)
    h, w = P.shape[:2]
    k = int(round(h * CAIXA_PDF[0] / CAIXA_PDF[1])) - w
    dup = np.zeros((h, w), np.int32)
    for c in costuras(energia(P[..., :3]), k):
        dup[np.arange(h), c] += 1
    out = np.zeros((h, w + k, 4), np.float32)
    for r in range(h):
        linha = []
        for c in range(w):
            linha.append(P[r, c])
            if dup[r, c]:
                linha.append((P[r, c] + P[r, min(c + 1, w - 1)]) / 2)
        out[r] = np.array(linha[:w + k])
    cv2.imwrite(str(SAIDA), np.clip(np.round(out), 0, 255).astype(np.uint8))
    print(f"    {SAIDA} {out.shape[1]}x{out.shape[0]} ({k} costuras; {out.shape[1] / out.shape[0]:.3f}:1)")


if __name__ == "__main__":
    main()

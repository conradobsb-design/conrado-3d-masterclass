#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do 1º Pavimento da Casa E (POE 642).

O render (Nano Banana Pro, 2000 x 1116, fundo branco: base v3 + prompt v1) manteve a escala da base:
a base 16:9 reduzida ao tamanho do render cai nele quase pela identidade (escala 0,9997 x 1,0085). Os
retoques são feitos no quadro do render, como no Térreo; o Térreo esmaecido em volta entra depois,
pelo `entorno_esmaecido.py`, com o 1º Pavimento sobreposto integralmente.

Itens (o mapa está em POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_erros.jpg):
1. Banho master, floreira: o PDF tem uma floreira com plantas ao longo da janela da parede da
   esquerda, no alto (três plantas da ARQ_LAYOUT HUMANIZAÇÃO); o motor deixou o piso liso. Entram as
   plantas tropicais do jardim interno do Térreo aprovado (um trecho dele, girado para correr na
   vertical), no retângulo do PDF, com borda suave, contorno fino da floreira (como o jardim interno
   do Térreo) e uma sombra curta no piso.
2. Banho master, chuveiros: o PDF tem dois chuveiros de teto (os quadradinhos da ARQ_LOUÇAS E
   METAIS); o motor pôs uma ducha de parede com braço e um registro no piso. Os dois saem (quartzito
   tecido do próprio banho, na luz do piso em volta) e entram as duas placas de teto de 30 cm da Casa
   A aprovada, nos centros do PDF, com sombra curta.

Uso (da pasta POE642_CasaA/scripts/):
  python3 retoque_1pav_casae.py ../../POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_render.png \\
      --saida ../../POE642_CasaE/renders --nome POE642_CasaE_PH_1Pavimento_v1_retocado
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))

from retoque_terreo_casad import CHUVEIROS_BHM  # noqa: E402
from retoque_terreo_casac import CHUVEIRO_TETO, SS  # noqa: E402
from retoque_subsolo_casad import apagar_largo  # noqa: E402

BASE = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png"
TERREO = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado.png"
VIS, BASE_LARG, TELA_LARG, TELA_ALT = 1800, 6001, 6905, 3884   # prévia de 1800 px, base e tela 16:9


def alinhar_base(render):
    """Base 16:9 reduzida ao tamanho do render e levada a ele por SIFT + afim (como nas outras casas)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return A


def vis2r(A, forma, x, y):
    """Ponto da prévia de 1800 px (as coordenadas da config_bases.json) no quadro do render."""
    bx = (x * BASE_LARG / VIS + (TELA_LARG - BASE_LARG) // 2) * forma[1] / TELA_LARG
    by = (y * BASE_LARG / VIS) * forma[0] / TELA_ALT
    return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]


def sombra(out, mascara, ret, desloc=(-1.0, 1.0), sigma=0.8, forca=0.3):
    """Sombra curta de uma peça (máscara 0..1 na janela ret), para baixo e à esquerda, como as do render."""
    x0, y0, x1, y1 = ret
    M = np.float32([[1, 0, desloc[0]], [0, 1, desloc[1]]])
    s = cv2.GaussianBlur(cv2.warpAffine(mascara.astype(np.float32), M, mascara.shape[::-1]), (0, 0), sigma)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - forca * s * (1 - mascara))[..., None], 0, 255).astype(np.uint8)
    return out


# item 1: floreira do banho master (prévia de 1800 px: as três plantas do PDF, 807,3 a 823,4 x 239,6 a
# 284,7); a fonte é um trecho do jardim interno do Térreo aprovado (render de 2000 px), girado
FLOREIRA = {"vis": (807.3, 239.6, 823.4, 284.7), "fonte": (1048, 550, 1094, 566), "borda": 0.7,
            "sombra": {"desloc": (-0.8, 1.2), "sigma": 1.0, "forca": 0.25},
            "contorno": ((88, 92, 96), 0.45)}       # borda da floreira em traço fino, como no Térreo


def floreira(out, A):
    q = FLOREIRA
    (x0, y0), (x1, y1) = vis2r(A, out.shape, *q["vis"][:2]), vis2r(A, out.shape, *q["vis"][2:])
    w, h = x1 - x0, y1 - y0
    fx0, fy0, fx1, fy1 = q["fonte"]
    t = cv2.imread(str(TERREO))[fy0:fy1, fx0:fx1]
    t = np.rot90(t, -1)                                   # a faixa do jardim passa a correr na vertical
    rx0, ry0 = int(np.floor(x0)) - 3, int(np.floor(y0)) - 3
    rx1, ry1 = int(np.ceil(x1)) + 4, int(np.ceil(y1)) + 4
    ww, hh = rx1 - rx0, ry1 - ry0
    # a peça a 8x, no lugar exato (frações de px), e reduzida por área
    big = np.zeros((hh * SS, ww * SS, 3), np.float32)
    m = np.zeros((hh * SS, ww * SS), np.float32)
    px0, py0 = int(round((x0 - rx0) * SS)), int(round((y0 - ry0) * SS))
    pw, ph = int(round(w * SS)), int(round(h * SS))
    big[py0:py0 + ph, px0:px0 + pw] = cv2.resize(t.astype(np.float32), (pw, ph), interpolation=cv2.INTER_CUBIC)
    m[py0:py0 + ph, px0:px0 + pw] = 1
    m = cv2.GaussianBlur(m, (0, 0), q["borda"] * SS)
    a = cv2.resize(m, (ww, hh), interpolation=cv2.INTER_AREA)
    cor = cv2.resize(big * m[..., None], (ww, hh), interpolation=cv2.INTER_AREA) / np.maximum(a[..., None], 1e-6)
    out = sombra(out, a, (rx0, ry0, rx1, ry1), **q["sombra"])
    reg = out[ry0:ry1, rx0:rx1].astype(np.float32)
    reg = reg * (1 - a[..., None]) + cor * a[..., None]
    cc, larg = q["contorno"]
    linha = np.zeros((hh * SS, ww * SS), np.uint8)
    cv2.rectangle(linha, (px0, py0), (px0 + pw, py0 + ph), 255, max(1, int(round(larg * SS))), cv2.LINE_AA)
    al = cv2.resize(linha.astype(np.float32) / 255, (ww, hh), interpolation=cv2.INTER_AREA)[..., None]
    out[ry0:ry1, rx0:rx1] = np.clip(reg * (1 - al) + np.float32(cc) * al, 0, 255).astype(np.uint8)
    print(f"    floreira com plantas em ({x0:.1f}, {y0:.1f}) a ({x1:.1f}, {y1:.1f})")
    return out


# item 2: chuveiros de teto do banho master. Saem a ducha de parede (com o braço até a parede da
# direita) e o registro do piso; entram as placas nos centros dos quadradinhos do PDF (prévia de 1800 px)
CHUVEIROS = {"tirar": [(992, 388, 1010, 401), (974, 404, 986, 420)], "janela": (958, 372, 1012, 422),
             "fontes": [(930, 300, 968, 336), (968, 300, 1000, 330)],
             "centros_vis": [(868.9, 414.05), (896.45, 414.05)], "lado": 9.4}


def placa_teto(out, cx, cy, lado):
    """Placa quadrada de chuveiro de teto (a da Casa A, 30 cm) com a sombra curta aprovada."""
    s = CHUVEIROS_BHM["sombra"]
    x0, y0 = int(np.floor(cx - lado / 2)) - 3, int(np.floor(cy - lado / 2)) - 3
    x1, y1 = int(np.ceil(cx + lado / 2)) + 4, int(np.ceil(cy + lado / 2)) + 4
    w, h = x1 - x0, y1 - y0
    p0x, p0y = int(round((cx - lado / 2 - x0) * SS)), int(round((cy - lado / 2 - y0) * SS))
    lp = int(round(lado * SS))
    m = np.zeros((h * SS, w * SS), np.float32)
    m[p0y:p0y + lp, p0x:p0x + lp] = 1
    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    cor = np.zeros((h * SS, w * SS, 3), np.float32)
    cor[p0y:p0y + lp, p0x:p0x + lp] = cv2.resize(img[hy0:hy1, hx0:hx1], (lp, lp), interpolation=cv2.INTER_CUBIC)
    a = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA)
    c = cv2.resize(cor, (w, h), interpolation=cv2.INTER_AREA) / np.maximum(a[..., None], 1e-6)
    out = sombra(out, a, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + c * a[..., None], 0, 255).astype(np.uint8)
    return out


def chuveiros(out, A):
    q = CHUVEIROS
    x0, y0, x1, y1 = q["janela"]
    m = np.zeros((y1 - y0, x1 - x0), bool)
    for tx0, ty0, tx1, ty1 in q["tirar"]:
        m[ty0 - y0:ty1 - y0, tx0 - x0:tx1 - x0] = True
    out = apagar_largo(out, q["janela"], m, q["fontes"], sigma=3.0, borda=0.8, lum_min=110)
    for xv, yv in q["centros_vis"]:
        cx, cy = vis2r(A, out.shape, xv, yv)
        out = placa_teto(out, cx, cy, q["lado"])
        print(f"    placa de teto em ({cx:.1f}, {cy:.1f})")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    A = alinhar_base(orig)
    print("[1] banho master: floreira com plantas junto à janela")
    out = floreira(out, A)
    print("[2] banho master: dois chuveiros de teto")
    out = chuveiros(out, A)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

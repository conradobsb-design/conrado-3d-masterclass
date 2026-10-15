#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Térreo da Casa E (POE 642).

O render (Nano Banana Pro, 2000 x 1116) manteve a escala da base: a base 16:9 reduzida ao tamanho do
render cai nele quase pela identidade (escala 0,9998 x 1,0066, deslocamento de 0,3 e -2,8 px). Os
retoques são feitos no quadro do render, como nas outras casas.

Itens (o mapa está em POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_erros.jpg):
1. Lote: a vegetação que o motor passou para fora do lote (à esquerda, embaixo e no alto à
   direita) sai, e as linhas tracejadas do lote, que ele apagou, voltam: fora do lote fica a base
   alinhada (o branco, a linha tracejada da esquerda, a da direita e o retângulo tracejado embaixo).
   Os muros de cima e de baixo, onde as folhas passavam por cima, voltam ao preto (cada linha do
   muro vira a mediana dela num trecho limpo).
2. Faixa à direita dos pisantes: a faixa em Bege Bahia que o motor inventou entre o gramado e a
   linha tracejada da direita (fora do gramado, branca no PDF) volta ao branco da base, no mesmo
   passo do item 1.

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/retoque_terreo_casae.py POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_render.webp \
      --saida POE642_CasaE/renders --nome POE642_CasaE_PH_Terreo_v1_retocado
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/

BASE = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png"


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
    al = cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    return A, al


# lote no quadro do render: o gramado vai de x = 141 a 1798; o muro de cima ocupa as linhas 0 a 5
# (de 142 a 1798) e o de baixo as linhas 932 a 937 (de 141 a 1851, até a linha tracejada da direita).
# Fora: x < 141, x >= 1799 acima do muro de baixo (a faixa entre o gramado e a linha tracejada da
# direita, onde o motor pôs o Bege Bahia), e tudo abaixo do muro de baixo
LOTE = {
    "x_esq": 141, "x_dir": 1799, "x_muro_baixo": 1852,
    "muro_cima": (0, 6), "muro_baixo": (932, 938),
    # trecho limpo (sem folhas) de onde sai a mediana de cada linha do muro
    "limpo_cima": (450, 1450), "limpo_baixo": (450, 1300),
}


def lote(out, base):
    q = LOTE
    xe, xd, xb = q["x_esq"], q["x_dir"], q["x_muro_baixo"]
    (c0, c1), (b0, b1) = q["muro_cima"], q["muro_baixo"]
    a, b = q["limpo_cima"]
    out[c0:c1, xe:xd] = np.median(out[c0:c1, a:b], axis=1).astype(np.uint8)[:, None]
    a, b = q["limpo_baixo"]
    out[b0:b1, xe:xb] = np.median(out[b0:b1, a:b], axis=1).astype(np.uint8)[:, None]
    fora = np.zeros(out.shape[:2], bool)
    fora[:, :xe] = True
    fora[:b0, xd:] = True
    fora[b0:b1, xb:] = True
    fora[b1:, :] = True
    out[fora] = base[fora]
    print(f"    muros de cima e de baixo sem as folhas; fora do lote: base ({int(fora.sum())} px)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    A, base = alinhar_base(orig)
    print("[1, 2] lote: vegetação fora do lote, linhas tracejadas e faixa à direita dos pisantes")
    out = lote(out, base)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Retoque sem IA do render do Térreo da Casa C (prompt v3). A imagem final é o render.

Os erros são corrigidos um a um, na ordem combinada com o usuário.

1. Chuveiros de teto: o motor deixou os boxes vazios. Cada um recebe a placa quadrada aprovada
   na Casa A (banho 3 do 1º Pavimento, 11 x 11 px, a mesma escala), no centro do símbolo do PDF
   (quadrado de 20 cm da layer ARQ_LOUÇAS E METAIS, levado ao render pela base alinhada).
2. Plantas fora do lote: o motor deixou palmeiras passando da linha tracejada em todo o lado
   esquerdo e do muro nos cantos de cima e de baixo à esquerda. Fora do lote volta a ser o que a
   base tem (fundo branco e linha tracejada); os dois trechos de muro cobertos pelas folhas são
   refeitos com o próprio muro do render, um pouco à direita. A vegetação termina no lote.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_terreo_casac.py RENDER.webp --saida PASTA --nome NOME
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/

BASE = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Terreo_v3_texturas_16x9.png"
# lote no render: linha tracejada da esquerda e muros de cima e de baixo
LOTE = {"x_esq": 155, "muro_cima": (24, 32), "muro_baixo": (952, 958)}
# trecho com folhas por cima dos muros (x) e coluna limpa de onde o muro é copiado
MURO_COBERTO = {"x": (150, 262), "coluna_limpa": 300}
CHUVEIRO_TETO = (RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final2.png", (1160, 214, 1171, 225))
CHUVEIROS = {
    "BH master 1": (411.2, 187.9),
    "BH 3": (630.5, 149.8),
    "BH 2": (868.4, 149.8),
    "BH 1": (1016.1, 149.8),
    "BH master 2": (442.3, 484.6),
}


def chuveiros_teto(out):
    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    cab = img[hy0:hy1, hx0:hx1]
    for nome, (cx, cy) in CHUVEIROS.items():
        px, py = round(cx - (hx1 - hx0 - 1) / 2), round(cy - (hy1 - hy0 - 1) / 2)
        out[py:py + cab.shape[0], px:px + cab.shape[1]] = cab
        print(f"    {nome}: chuveiro de teto em ({cx}, {cy})")
    return out


def alinhar_base(render):
    """Base 16:9 reduzida e levada ao render por SIFT + afim."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))


def fora_do_lote(out, base):
    H, W = out.shape[:2]
    x0 = LOTE["x_esq"]
    (c0, c1), (b0, b1) = LOTE["muro_cima"], LOTE["muro_baixo"]
    fora = np.zeros((H, W), bool)
    fora[:, :x0] = True                                   # à esquerda da linha tracejada
    fora[:c0, :MURO_COBERTO["x"][1]] = True               # acima do muro de cima, no canto
    fora[b1:, :MURO_COBERTO["x"][1]] = True               # abaixo do muro de baixo, no canto
    mudou = fora & (np.abs(out.astype(int) - base.astype(int)).max(axis=2) > 40)
    out[fora] = base[fora]
    # muros: as folhas passavam por cima; o muro volta, copiado da coluna limpa do próprio render
    mx0, mx1 = MURO_COBERTO["x"]
    xl = MURO_COBERTO["coluna_limpa"]
    for y0, y1 in ((c0, c1), (b0, b1)):
        out[y0:y1, max(mx0, x0):mx1] = out[y0:y1, xl:xl + 1]
    print(f"    {int(mudou.sum())} px de folhas fora do lote; muros refeitos em x {max(mx0, x0)}-{mx1}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] chuveiros de teto")
    out = chuveiros_teto(out)
    print("[2] plantas fora do lote")
    out = fora_do_lote(out, alinhar_base(orig))

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[3] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Retoque sem IA do render do Térreo da Casa C (prompt v3). A imagem final é o render.

Os erros são corrigidos um a um, na ordem combinada com o usuário.

1. Chuveiros de teto: o motor deixou os boxes vazios. Cada um recebe a placa quadrada aprovada
   na Casa A (banho 3 do 1º Pavimento, 11 x 11 px, a mesma escala), no centro do símbolo do PDF
   (quadrado de 20 cm da layer ARQ_LOUÇAS E METAIS, levado ao render pela base alinhada).

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

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[2] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

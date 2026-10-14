#!/usr/bin/env python3
"""Junta as pranchas de entrega da Casa A num PDF para o cliente, uma prancha por página.

Ordem: Subsolo, Térreo e 1º Pavimento (de baixo para cima, como na folha de layout do
cliente). A página tem 420 mm de largura (a largura do A3) e a altura segue a proporção da
prancha, e as imagens entram sem recompressão.

Uso:
  python pdf_entrega.py --entrega ../entrega
"""
import argparse
from pathlib import Path

import pymupdf

AQUI = Path(__file__).resolve().parent
ORDEM = ["Subsolo", "Terreo", "1Pavimento"]
LARGURA_MM = 420


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entrega", type=Path, default=AQUI.parent / "entrega")
    ap.add_argument("--nome", default="POE642_CasaA_Plantas_Humanizadas.pdf")
    args = ap.parse_args()

    doc = pymupdf.open()
    for chave in ORDEM:
        img = args.entrega / f"POE642_CasaA_PH_{chave}_entrega.png"
        pix = pymupdf.Pixmap(str(img))
        w = LARGURA_MM / 25.4 * 72
        h = w * pix.height / pix.width
        page = doc.new_page(width=w, height=h)
        page.insert_image(page.rect, filename=str(img))
        print(f"{chave}: {pix.width}x{pix.height} px -> {LARGURA_MM} x {h / 72 * 25.4:.1f} mm")
    doc.set_metadata({
        "title": "Casa A – Plantas Humanizadas (Subsolo, Térreo e 1º Pavimento)",
        "author": "New Air · Render 3D · Conrado Cortez",
        "subject": "Paulo Octávio · ML 10 – Conjunto 02, Lotes 17, Unidade A",
        "keywords": "planta humanizada, layout, Casa A",
    })
    saida = args.entrega / args.nome
    doc.save(str(saida), garbage=4, deflate=True)
    print(saida, f"{saida.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

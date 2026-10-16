#!/usr/bin/env python3
"""Junta as pranchas de entrega de uma casa num PDF para o cliente, uma prancha por página.

Ordem: a da chave 'entrega.pdf.ordem' da config da casa (na Casa A, Subsolo, Térreo e
1º Pavimento, de baixo para cima, como na folha de layout do cliente). A página tem 420 mm
de largura (a largura do A3) e a altura segue a proporção da prancha, e as imagens entram
sem recompressão.

Uso:
  python pdf_entrega.py                                          # Casa A
  python pdf_entrega.py --config ../../POE642_CasaB/config_bases.json
  # uma opção para o cliente: outra prancha para um pavimento, outro nome e outro título
  python pdf_entrega.py --config ../../POE642_CasaE/config_bases.json \
      --prancha 1Pavimento=../../POE642_CasaE/entrega/POE642_CasaE_PH_1Pavimento_entrega_pb.png \
      --nome POE642_CasaE_Plantas_Humanizadas_opcao_PB.pdf --titulo "Casa E – ... (opção P&B)"
"""
import argparse
import json
from pathlib import Path

import pymupdf

AQUI = Path(__file__).resolve().parent
CONFIG_PADRAO = AQUI / "config_bases.json"      # Casa A
LARGURA_MM = 420


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=CONFIG_PADRAO, help="config da casa (chave 'entrega')")
    ap.add_argument("--entrega", type=Path, default=None, help="padrão: a pasta_entrega da config")
    ap.add_argument("--nome", default=None, help="padrão: entrega.pdf.nome da config")
    ap.add_argument("--prancha", action="append", default=[], metavar="PAVIMENTO=ARQUIVO",
                    help="usa esta prancha no lugar da padrão do pavimento (ex.: uma das opções); pode repetir")
    ap.add_argument("--titulo", default=None, help="padrão: entrega.pdf.titulo da config")
    args = ap.parse_args()
    trocas = dict(item.split("=", 1) for item in args.prancha)
    ent = json.loads(args.config.read_text())["entrega"]
    pdf = ent["pdf"]
    args.entrega = args.entrega or args.config.resolve().parent / ent["pasta_entrega"]
    args.nome = args.nome or pdf["nome"]

    doc = pymupdf.open()
    for chave in pdf["ordem"]:
        img = Path(trocas[chave]) if chave in trocas else args.entrega / f"{ent['prefixo']}_PH_{chave}_entrega.png"
        pix = pymupdf.Pixmap(str(img))
        w = LARGURA_MM / 25.4 * 72
        h = w * pix.height / pix.width
        page = doc.new_page(width=w, height=h)
        page.insert_image(page.rect, filename=str(img))
        print(f"{chave}: {pix.width}x{pix.height} px -> {LARGURA_MM} x {h / 72 * 25.4:.1f} mm")
    doc.set_metadata({
        "title": args.titulo or pdf["titulo"],
        "author": "New Air · Render 3D · Conrado Cortez",
        "subject": pdf["assunto"],
        "keywords": pdf["palavras"],
    })
    saida = args.entrega / args.nome
    doc.save(str(saida), garbage=4, deflate=True)
    print(saida, f"{saida.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Duas opções de montagem do 1º Pavimento da Casa E (POE 642) para o cliente, em 3840 px.

Pedido do usuário (16/10/26): "vou apresentar ao cliente duas opções: em preto e branco e só com as
linhas do PDF. prepare as duas opções."

Nas duas, o render retocado do 1º Pavimento sem rótulos (`retoque_1pav_casae.py`) vai ao quadro 16:9 comum
(SIFT + afim contra a base v3) e entra por cima integralmente, na pegada da base, como no
`entorno_esmaecido.py`; a área branca abaixo da sala íntima (`--fora`) mostra o entorno. Depois, os nomes e
as áreas dos ambientes são escritos de novo na resolução final (`retoque_1pav_casae.rotulos_ambientes`, as
mesmas regras: posição do PDF, sobre móvel no piso livre, preto, 30% maior que o PDF), nítidos.
- Opção P&B: o entorno é o render aprovado do Térreo, 75% mais claro e sem saturação.
- Opção linhas: o entorno é o PDF do Térreo só em linhas, sem render: a página desenhada com as camadas de
  piso (ARQ_CONTRAPISO: cores e hachuras), das curvas de nível, dos textos e das zonas desligadas, sem o
  título nem os números da escada, em cinza (paredes cinza-claro, traços cinza-médio). O Térreo e o 1º
  Pavimento têm a mesma página e o mesmo recorte, então o PDF do Térreo cai direto no quadro comum.

Uso (da pasta POE642_CasaA/scripts/):
  python3 opcoes_1pav_casae.py
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from PIL import Image

from entorno_esmaecido import contexto_render, sobrepor
from gerar_bases import Raster, em_16x9, ocultar_layers
from rodape_entrega import no_quadro_comum
import retoque_1pav_casae as R

CASA = R.RAIZ / "POE642_CasaE"
CIMA = CASA / "renders/POE642_CasaE_PH_1Pavimento_v1_retocado_sem_rotulos.png"
BASE_CIMA = CASA / "bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png"
TERREO = CASA / "renders/POE642_CasaE_PH_Terreo_v1_retocado.png"
BASE_TERREO = CASA / "bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png"
PDF_TERREO = R.RAIZ / "_pdfs_cliente/642 - TÉRREO - CASA E.pdf"
FORA = [(912, 752, 1096, 816)]              # área branca abaixo da sala íntima (px de uma prévia de 2000 px)
LINHAS = {"ocultas": ["ARQ_TERRENO PLANEJADO", "ARQ_CONTRAPISO", "DOC_TEXTOS", "ARQ_ZONA"],
          "forca": 0.7}                     # 0: branco; 1: o traço do PDF (preto)


def quadro_pdf(pg, cfg, larg_tela, alt_tela, larg_sem_tela, alt_sem_tela, W):
    """Ponto do PDF -> px do quadro 16:9 na largura W (recorte, zoom, margem da tela 16:9)."""
    r = Raster(pg, cfg["recorte"], cfg["largura_px"], 0)
    dx, dy = (larg_tela - larg_sem_tela) // 2, (alt_tela - alt_sem_tela) // 2
    k = W / larg_tela

    def f(x, y):
        px, py = r.para_px(pymupdf.Point(x, y))
        return (px + dx) * k, (py + dy) * k
    return f


def contexto_linhas(W, H):
    q = LINHAS
    cfg = json.loads(R.CONFIG.read_text())
    doc = pymupdf.open(PDF_TERREO)
    ocultar_layers(doc, q["ocultas"])
    pg = doc[0]
    r = Raster(pg, cfg["recorte"], cfg["largura_px"], 0)
    img = np.asarray(r.render(pg).convert("L")).copy()
    # sem os textos que sobram fora das camadas desligadas (título, escala, números da escada)
    for x0, y0, x1, y1, *_ in pg.get_text("words"):
        (a, b), (c, d) = r.para_px(pymupdf.Point(x0, y0)), r.para_px(pymupdf.Point(x1, y1))
        img[max(int(b) - 2, 0):int(np.ceil(d)) + 2, max(int(a) - 2, 0):int(np.ceil(c)) + 2] = 255
    tela = np.asarray(em_16x9(Image.fromarray(img).convert("RGB")).convert("L"), np.float32)
    tela = cv2.resize(tela, (W, H), interpolation=cv2.INTER_AREA)
    t = 255 - (255 - tela) * q["forca"]
    return np.repeat(t[..., None], 3, axis=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--largura", type=int, default=3840)
    ap.add_argument("--saida", type=Path, default=CASA / "renders")
    args = ap.parse_args()
    W = args.largura
    base = cv2.imread(str(BASE_CIMA))
    lt, at = base.shape[1], base.shape[0]
    H = round(at * W / lt)
    base = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA)
    cima = cv2.cvtColor(np.asarray(no_quadro_comum(Image.open(CIMA).convert("RGB"), BASE_CIMA,
                                                   "1º Pavimento", W)), cv2.COLOR_RGB2BGR)
    # rótulos no quadro final: PDF do 1º Pavimento -> quadro 16:9 na largura W
    cfg = json.loads(R.CONFIG.read_text())
    pg1 = pymupdf.open(R.PDF)[cfg["pavimentos"]["1Pavimento"]["pagina"]]
    hb, wb = cv2.imread(str(R.BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg1, cfg, lt, at, wb, hb, W)
    rot = R.rotulos_pdf(pg1)

    opcoes = {
        "pb": ("Térreo esmaecido em preto e branco", contexto_render(TERREO, BASE_TERREO, W, 0.75, 0.0)),
        "linhas": ("Térreo só com as linhas do PDF", contexto_linhas(W, H)),
    }
    args.saida.mkdir(parents=True, exist_ok=True)
    for chave, (desc, t) in opcoes.items():
        print(f"[{chave}] {desc}")
        out = sobrepor(base, t, FORA, cima)
        out = R.rotulos_ambientes(out, rot, p2q, escala_desvio=W / 2000)
        nome = args.saida / f"POE642_CasaE_PH_1Pavimento_v1_final_{chave}.png"
        cv2.imwrite(str(nome), out)
        cv2.imwrite(str(nome.with_name(nome.stem + "_preview.jpg")),
                    cv2.resize(out, (2000, round(2000 * H / W)), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {nome}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Opções de montagem do 1º Pavimento da Casa E (POE 642) para o cliente, em 3840 px.

Pedido do usuário (16/10/26): "vou apresentar ao cliente duas opções: em preto e branco e só com as
linhas do PDF. prepare as duas opções." Depois (19/10/26), com uma planta de referência: "referência com o
piso inferior mais 'nublado'. Usaremos para as plantas dos 1º pavimentos das casas" (opção nublado).

Nas duas, o render retocado do 1º Pavimento sem rótulos (`retoque_1pav_casae.py`) vai ao quadro 16:9 comum
(SIFT + afim contra a base v3) e entra por cima integralmente, na pegada da base, como no
`entorno_esmaecido.py`; a área branca abaixo da sala íntima (`--fora`) mostra o entorno. Depois, os nomes e
as áreas dos ambientes são escritos de novo na resolução final (`retoque_1pav_casae.rotulos_ambientes`, as
mesmas regras: posição do PDF, sobre móvel no piso livre, preto, 30% maior que o PDF), nítidos.
- Opção P&B: o entorno é o render aprovado do Térreo, 75% mais claro e sem saturação.
- Opção nublado: o mesmo render, sob um véu branco de 70%, com a cor dele (80% da saturação) e um leve
  desfoque, como na referência do usuário (`entorno_esmaecido.NUBLADO`).
- Opção linhas: o entorno é o PDF do Térreo só em linhas, sem render: a página desenhada com as camadas de
  piso (ARQ_CONTRAPISO: cores e hachuras), das curvas de nível, dos textos e das zonas desligadas, sem o
  título nem os números da escada, em cinza (paredes cinza-claro, traços cinza-médio). O Térreo e o 1º
  Pavimento têm a mesma página e o mesmo recorte, então o PDF do Térreo cai direto no quadro comum.

Desde 20/10/26 (pente fino do 1º Pavimento): o alinhamento do 1º Pavimento vem da versão entregue (CIMA_APROVADO),
e o setor branco da porta pequena à direita do vazio do hall mostra o entorno (SETOR_PORTA, R3); os vazios mostram o
Térreo de baixo, nevoado, com o X e o vidro por cima (nevoar_vazios).

Desde 21/10/26, no fim do pente fino: o nublado é a opção única (seção 16 das regras) e sai sem sufixo,
POE642_CasaE_PH_1Pavimento_v1_final.png, como o Subsolo e o Térreo. As opções P&B e linhas ficam no histórico e
saem só quando pedidas (`--opcao pb`, `--opcao linhas`), com o sufixo.

Uso (da pasta POE642_CasaA/scripts/):
  python3 opcoes_1pav_casae.py                 # o nublado (a imagem final)
  python3 opcoes_1pav_casae.py --opcao pb --opcao linhas   # as opções antigas, com sufixo
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage
import pymupdf
from PIL import Image

from entorno_esmaecido import NUBLADO, contexto_render, sobrepor
from gerar_bases import Raster, em_16x9, ocultar_layers
from rodape_entrega import no_quadro_comum
import retoque_1pav_casae as R

CASA = R.RAIZ / "POE642_CasaE"
CIMA = CASA / "renders/POE642_CasaE_PH_1Pavimento_v1_retocado_sem_rotulos.png"
# o alinhamento do 1º Pavimento ao quadro comum é medido nesta versão fixa (a entregue até 20/10/26, sem
# rótulos) e aplicado ao retocado atual: um retoque novo não muda o afim, e a montagem muda só onde ele mexeu
# (sem isso, cada retoque refazia o SIFT e a pegada inteira saía reamostrada)
CIMA_APROVADO = CASA / "renders/POE642_CasaE_PH_1Pavimento_v1_retocado_aprovado.png"
BASE_CIMA = CASA / "bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png"
TERREO = CASA / "renders/POE642_CasaE_PH_Terreo_v1_retocado.png"
BASE_TERREO = CASA / "bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png"
PDF_TERREO = R.RAIZ / "_pdfs_cliente/642 - TÉRREO - CASA E.pdf"
# áreas brancas de fora presas na pegada (px de uma prévia de 2000 px): abaixo da sala íntima, e a faixa
# abaixo da parede de baixo da suíte 3, fechada pela linha fina do PDF (lá o render tinha uma barra cinza);
# esta começa abaixo da parede, para não pegar a escrivaninha da suíte (branca na base)
# e o setor branco da porta pequena à direita do vazio do hall, do lado de fora, que o arco fechava (R3,
# pente fino de 20/10/26, item 1: sem o arco, o setor some e aparece o entorno; a folha fica). Nele, os px do
# traço cinza do arco (o da base, que fecha a pegada, e o do render) recebem o entorno depois da montagem; a
# parede, escura, fica. A base não muda: sem o arco, o caixilho saía da pegada (deixava de ser área fechada)
SETOR_PORTA = (1297, 690, 1315, 712)
FORA = [(912, 752, 1096, 816), (822, 800, 912, 816), SETOR_PORTA]
# vazios com o Térreo nevoado (pente fino do 1º Pavimento, 20/10/26, item 15; usuário: "Mostrar a jardineira de
# baixo mais nevoada", no vazio sob a escada, sobre o jardim de inverno, e "Mostrar o andar de baixo nevoado", no
# vazio do hall): o branco dos vazios (item 5 do retoque, pedido de 16/10) passa a mostrar o Térreo de baixo, no
# mesmo entorno da montagem; o X tracejado, o guarda-corpo de vidro e a folha da pivotante ficam por cima, como
# um papel transparente (o Térreo multiplicado pelo tom deles). Os vazios são o cinza da base v3 (cor, área
# mínima em px de 3840, folga em px); o peso vem do branco do render (de "claro" a 255)
VAZIOS = {"cor": 74, "tol": 12, "area": 1500, "folga": 3, "claro": (205, 245)}
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


def mascara_vazios(base):
    """Os vazios do 1º Pavimento no quadro da montagem: o cinza da base v3, fechado e com os furos (o X claro)
    preenchidos, com uma folga."""
    q = VAZIOS
    cinza = np.abs(base.astype(int) - q["cor"]).max(axis=2) < q["tol"]
    n, lab, st, _ = cv2.connectedComponentsWithStats(cinza.astype(np.uint8), connectivity=8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > q["area"]]).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    m = ndimage.binary_fill_holes(m).astype(np.uint8)
    return cv2.dilate(m, np.ones((2 * q["folga"] + 1,) * 2, np.uint8)) > 0


def nevoar_vazios(out, t, cima, vazios):
    """No branco dos vazios, o Térreo de baixo (t, o entorno da montagem); os traços do render (X, vidro, folha)
    ficam por cima, multiplicados."""
    lo, hi = VAZIOS["claro"]
    w = vazios * np.clip((cima.min(axis=2).astype(np.float32) - lo) / (hi - lo), 0, 1)
    w = cv2.GaussianBlur(w, (0, 0), 0.6) * vazios
    nev = t * np.clip(cima.astype(np.float32) / 250, 0, 1)
    return np.clip(out * (1 - w[..., None]) + nev * w[..., None], 0, 255).astype(np.uint8)


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
    ap.add_argument("--opcao", action="append", choices=["pb", "linhas", "nublado"], default=None,
                    help="só estas opções (pode repetir; padrão: o nublado, a opção única desde 21/10/26)")
    args = ap.parse_args()
    W = args.largura
    base = cv2.imread(str(BASE_CIMA))
    lt, at = base.shape[1], base.shape[0]
    H = round(at * W / lt)
    base = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA)
    sx0, sy0, sx1, sy1 = (int(v * W / 2000) for v in SETOR_PORTA)
    s_min = base[sy0:sy1, sx0:sx1].min(axis=2)
    arco = cv2.dilate(((s_min > 60) & (s_min < 245)).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    arco &= cv2.dilate((s_min <= 60).astype(np.uint8), np.ones((9, 9), np.uint8)) == 0    # a borda da parede fica
    vazios = mascara_vazios(base)
    cima = cv2.cvtColor(np.asarray(no_quadro_comum(Image.open(CIMA).convert("RGB"), BASE_CIMA, "1º Pavimento", W,
                                                   referencia=Image.open(CIMA_APROVADO).convert("RGB"))),
                        cv2.COLOR_RGB2BGR)
    # rótulos no quadro final: PDF do 1º Pavimento -> quadro 16:9 na largura W
    cfg = json.loads(R.CONFIG.read_text())
    pg1 = pymupdf.open(R.PDF)[cfg["pavimentos"]["1Pavimento"]["pagina"]]
    hb, wb = cv2.imread(str(R.BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg1, cfg, lt, at, wb, hb, W)
    rot = R.rotulos_pdf(pg1)

    opcoes = {
        "pb": ("Térreo esmaecido em preto e branco", lambda: contexto_render(TERREO, BASE_TERREO, W, 0.75, 0.0)),
        "linhas": ("Térreo só com as linhas do PDF", lambda: contexto_linhas(W, H)),
        "nublado": ("Térreo nublado, com a cor dele", lambda: contexto_render(TERREO, BASE_TERREO, W, **NUBLADO)),
    }
    opcoes = {k: v for k, v in opcoes.items() if k in (args.opcao or ["nublado"])}
    args.saida.mkdir(parents=True, exist_ok=True)
    for chave, (desc, contexto) in opcoes.items():
        print(f"[{chave}] {desc}")
        t = contexto()
        out = sobrepor(base, t, FORA, cima)
        out[sy0:sy1, sx0:sx1][arco] = np.clip(t[sy0:sy1, sx0:sx1][arco], 0, 255).astype(np.uint8)
        out = nevoar_vazios(out, t, cima, vazios)
        out = R.rotulos_ambientes(out, rot, p2q, escala_desvio=W / 2000)
        nome = args.saida / ("POE642_CasaE_PH_1Pavimento_v1_final.png" if chave == "nublado"
                             else f"POE642_CasaE_PH_1Pavimento_v1_final_{chave}.png")
        cv2.imwrite(str(nome), out)
        cv2.imwrite(str(nome.with_name(nome.stem + "_preview.jpg")),
                    cv2.resize(out, (2000, round(2000 * H / W)), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {nome}")


if __name__ == "__main__":
    main()

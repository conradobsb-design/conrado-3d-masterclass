#!/usr/bin/env python3
"""Conferência item a item das plantas da Casa A (POE 642) contra o PDF do cliente, como na Casa E.

Pedido do usuário (19/10/26): "vamos fazer a conferência de item a item do render da casa A, conforme fizemos
com a casa E. Pegar o PDF da casa A e rever item a item com o render." Cada pavimento foi comparado lado a lado
com o PDF (`_pdfs_cliente/642 - <PAVIMENTO> - CASA A.pdf`), os dois no quadro comum. As divergências ficam em
`ITENS` (pontos em px de uma prévia de 2000 px do quadro comum) e o script desenha o mapa numerado de cada
pavimento, com a legenda embaixo: `renders/POE642_CasaA_PH_<Pavimento>_conferencia.jpg`.

Uso (da pasta POE642_CasaA/scripts/):
  python3 conferencia_casaa.py            # os três mapas
  python3 conferencia_casaa.py Terreo
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import rotulos_casaa as A
from rodape_entrega import FONTES, no_quadro_comum

LARGURA = 3840
VERMELHO = (205, 40, 40)
# recorte de cada mapa (px de 2000 do quadro comum), em volta da planta
RECORTE = {"Terreo": (360, 150, 1450, 1015), "1Pavimento": (620, 150, 1450, 880), "Subsolo": (540, 440, 1260, 875)}

# (número, texto, pontos em px de 2000 do quadro comum)
ITENS = {
    "Terreo": [
        (1, "Pilares redondos da varanda e o pilar junto ao gourmet em marrom; no PDF são os pilares estruturais "
            "(no padrão da Casa E, pretos como as paredes)", [(809, 301), (809, 473), (657, 650), (642, 847)]),
        (2, "Sala de estar: falta a poltrona da direita e os dois vasos de plantas junto ao sofá; o sofá curvo "
            "do PDF acompanha o tapete pela esquerda, o render o pôs ao longo do alto", [(1104, 243), (1027, 226)]),
        (3, "Estar sob a projeção do pavimento superior: no PDF são 4 poltronas em X com a mesa triangular no "
            "centro; o render fez uma mesa retangular com 6 cadeiras", [(1051, 390)]),
        (4, "Sala de jantar: a mesa do PDF é oval (pontas arredondadas); a do render é retangular chanfrada",
         [(1055, 510)]),
        (5, "Lavabo: falta o vaso sanitário (no alto, à direita) e o X tracejado da claraboia; no lugar, uma peça "
            "estranha com um arco", [(1205, 195)]),
        (6, "Escritório: no PDF a mesa tem uma cadeira em cima (de escritório) e duas embaixo; o render pôs "
            "duas em cima", [(1287, 215)]),
        (7, "Banho da varanda: uma bacia sanitária no lugar do chuveiro (o PDF tem a ducha e a divisória do box)",
         [(868, 828)]),
        (8, "Jardim (4,79 m²): sem plantas; o PDF tem três touceiras", [(825, 873)]),
        (9, "Área de serviço: a escada caracol saiu só como um traço fino sobre o granito (o PDF tem os degraus "
            "em leque e o corrimão)", [(1029, 818)]),
        (10, "Área de serviço: a porta da direita, no alto, está sem o arco", [(1050, 775)]),
        (11, "Quarto do motorista: a cama virou um bloco lilás, sem lençol nem travesseiro", [(1260, 612)]),
        (12, "Banho do motorista: o chuveiro e a divisória do box viraram um bloco lilás", [(1186, 655)]),
    ],
    "1Pavimento": [
        (1, "Suíte 3: os criados-mudos do PDF são redondos; os do render são quadrados", [(864, 188), (950, 188)]),
        (2, "Suíte 3: falta o banco ao pé da cama", [(907, 254)]),
        (3, "Suíte 2: falta o banco ao pé da cama", [(919, 558)]),
        (4, "Suíte master: falta o banco ao pé da cama", [(784, 681)]),
        (5, "Suíte 1: falta o banco ao pé das camas", [(1272, 749)]),
        (6, "Quarto de serviço: faltam a cama de solteiro e o criado-mudo (no lugar, uma faixa de madeira com "
            "dois quadrados claros)", [(1013, 730)]),
        (7, "Banho master: a banheira do PDF é oval; a do render é retangular de cantos arredondados", [(760, 781)]),
    ],
    "Subsolo": [
        (1, "Banho de serviço: faltam o chuveiro (na parede da esquerda) e a divisória de vidro do box",
         [(590, 480)]),
        # usuário (19/10/26): o banco é horizontal; a faixa vertical à esquerda é o piso da piscina, a passagem
        # da sauna para a piscina ("não é em L")
        (2, "Sauna: o banco horizontal do PDF, ao longo da parede de baixo, virou piso na v6, por decisão anterior "
            "(a faixa vertical à esquerda é a passagem da sauna para a piscina e fica como piso)", [(670, 840)]),
    ],
}


def fonte(peso, tam):
    return ImageFont.truetype(str(FONTES / f"Inter-{peso}.otf"), tam)


def quebrar(texto, f, largura, d):
    linhas, atual = [], ""
    for p in texto.split():
        t = f"{atual} {p}".strip()
        if d.textlength(t, font=f) > largura and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    return linhas + [atual]


def mapa(chave, saida):
    import json
    cfg = json.loads(A.CONFIG.read_text())
    q = A.PAVIMENTOS[chave]
    base = (A.CONFIG.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][chave]["base"]).resolve()
    img = no_quadro_comum(Image.open(A.CASA / q["render"]).convert("RGB"), base, chave, LARGURA)
    k = LARGURA / 2000
    x0, y0, x1, y1 = RECORTE[chave]
    img = img.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k)))
    d = ImageDraw.Draw(img)
    fn = fonte("SemiBold", 34)
    for n, _, pontos in ITENS[chave]:
        for x, y in pontos:
            cx, cy = (x - x0) * k, (y - y0) * k
            d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), outline=VERMELHO, width=5)
            d.text((cx + 30, cy - 34), str(n), font=fn, fill=VERMELHO, stroke_width=3, stroke_fill=(255, 255, 255))
    # legenda
    W = img.width
    fl = fonte("Regular", 30)
    blocos = [quebrar(f"{n}. {t}", fl, W - 80, d) for n, t, _ in ITENS[chave]]
    alt = 40 + sum(44 * len(b) + 14 for b in blocos)
    leg = Image.new("RGB", (W, alt), (255, 255, 255))
    dl = ImageDraw.Draw(leg)
    y = 30
    for b in blocos:
        for li in b:
            dl.text((40, y), li, font=fl, fill=(30, 30, 30))
            y += 44
        y += 14
    final = Image.new("RGB", (W, img.height + alt), (255, 255, 255))
    final.paste(img, (0, 0))
    final.paste(leg, (0, img.height))
    nome = saida / f"POE642_CasaA_PH_{chave}_conferencia.jpg"
    final.save(nome, quality=88)
    print(f"    {nome} ({len(ITENS[chave])} itens)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimentos", nargs="*", default=list(ITENS))
    ap.add_argument("--saida", type=Path, default=A.CASA / "renders")
    args = ap.parse_args()
    for ch in args.pavimentos:
        print(f"[{ch}] mapa da conferência")
        mapa(ch, args.saida)


if __name__ == "__main__":
    main()

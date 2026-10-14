#!/usr/bin/env python3
"""Rodapé de entrega das plantas humanizadas da Casa A (POE 642), um por pavimento.

Segue o carimbo da folha de layout do cliente (642-ARQ-EX-001): norte, título "LAYOUT – …",
quadro de áreas, dados do projeto, autoria e marca do cliente. Não leva cotas.

Uso:
  python rodape_entrega.py --saida ../entrega                    # só os três rodapés (3840 px)
  python rodape_entrega.py --saida ../entrega --render 1Pavimento=../renders/x.png
      # também a prancha: render + rodapé na largura do render
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "entrega" / "assets"
FONTES = Path("/usr/share/fonts/opentype/inter")

PAVIMENTOS = {
    "Subsolo": {"titulo": "SUBSOLO", "linha_area": 0},
    "Terreo": {"titulo": "TÉRREO", "linha_area": 1},
    "1Pavimento": {"titulo": "1º PAVIMENTO", "linha_area": 2},
}
AREAS = [("SUBSOLO", "160,40 m²"), ("TÉRREO", "427,40 m²"), ("1º PAVIMENTO", "263,25 m²"), ("TOTAL", "851,05 m²")]
PROJETO = [
    ("CLIENTE", "PAULO OCTÁVIO"),
    ("ENDEREÇO", "ML 10 – CONJUNTO 02, LOTES 17, UNIDADE A"),
    ("PROJETO", "CASA A · UNIDADE AUTÔNOMA \"A\""),
    ("DATA INICIAL", "18/05/2023"),
]
EQUIPE = "RUAN BRAGA E MARCELA CAMPEDELLI"

LARGURA, ALTURA = 3840, 440
TINTA = (38, 38, 38)
CINZA = (128, 128, 128)
FIO = (214, 214, 214)
DESTAQUE = (239, 231, 218)   # bege claro, o mesmo tom quente do render
BRANCO = (255, 255, 255)


def fonte(peso, tamanho):
    return ImageFont.truetype(str(FONTES / f"Inter-{peso}.otf"), tamanho)


def texto(d, xy, s, f, cor, espaco=0.0, ancora="ls"):
    """Texto com espaçamento entre letras (em fração do tamanho da fonte)."""
    x, y = xy
    passo = f.size * espaco
    largura = sum(f.getlength(c) for c in s) + passo * (len(s) - 1)
    if ancora[0] == "r":
        x -= largura
    elif ancora[0] == "m":
        x -= largura / 2
    for c in s:
        d.text((x, y), c, font=f, fill=cor, anchor="l" + ancora[1])
        x += f.getlength(c) + passo
    return largura


def largura_txt(s, f, espaco=0.0):
    return sum(f.getlength(c) for c in s) + f.size * espaco * (len(s) - 1)


def colar(base, img, x, y, altura=None, largura=None):
    if altura:
        img = img.resize((round(img.width * altura / img.height), altura), Image.LANCZOS)
    elif largura:
        img = img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)
    base.alpha_composite(img, (round(x), round(y)))
    return img.size


def rodape(chave):
    pav = PAVIMENTOS[chave]
    im = Image.new("RGBA", (LARGURA, ALTURA), BRANCO + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, LARGURA, 7), fill=TINTA)                       # filete forte do carimbo
    topo, base_y = 80, ALTURA - 60
    divisorias = [1040, 1640, 2800, 3330]
    for x in divisorias:
        d.line((x, topo, x, base_y), fill=FIO, width=3)

    # 1. norte + título
    colar(im, Image.open(ASSETS / "norte.png").convert("RGBA"), 90, topo + 10, altura=250)
    x0 = 340
    titulo = f"LAYOUT – {pav['titulo']}"
    f_t = fonte("Regular", 66)
    while largura_txt(titulo, f_t, 0.06) > divisorias[0] - x0 - 50:
        f_t = fonte("Regular", f_t.size - 2)
    texto(d, (x0, topo + 95), titulo, f_t, TINTA, 0.06)
    texto(d, (x0, topo + 165), "PLANTA HUMANIZADA", fonte("Medium", 32), CINZA, 0.22)
    texto(d, (x0, topo + 215), "BASE: PLANTA BAIXA 1:100", fonte("Regular", 27), CINZA, 0.12)
    texto(d, (x0, topo + 257), "IMAGEM ILUSTRATIVA · SEM COTAS E SEM ESCALA", fonte("Regular", 22), CINZA, 0.10)

    # 2. quadro de áreas
    ax0, ax1 = divisorias[0] + 70, divisorias[1] - 70
    texto(d, (ax0, topo + 18), "ÁREAS", fonte("Medium", 26), CINZA, 0.25)
    linha_h, y = 58, topo + 48
    for i, (nome, valor) in enumerate(AREAS):
        total = i == len(AREAS) - 1
        if i == pav["linha_area"]:
            d.rectangle((ax0 - 18, y, ax1 + 18, y + linha_h - 6), fill=DESTAQUE)
        if total:
            d.line((ax0 - 18, y - 3, ax1 + 18, y - 3), fill=TINTA, width=2)
        peso = "SemiBold" if (i == pav["linha_area"] or total) else "Regular"
        f = fonte(peso, 31)
        texto(d, (ax0, y + 40), nome, f, TINTA, 0.08)
        texto(d, (ax1, y + 40), valor, f, TINTA, 0.04, ancora="rs")
        y += linha_h

    # 3. dados do projeto
    px0 = divisorias[1] + 70
    f_c = fonte("Regular", 56)
    texto(d, (px0, topo + 62), f"CASA A – {pav['titulo']}", f_c, TINTA, 0.06)
    f_l, f_v = fonte("Regular", 25), fonte("Medium", 29)
    y = topo + 130
    for rotulo, valor in PROJETO:
        texto(d, (px0, y), rotulo, f_l, CINZA, 0.16)
        texto(d, (px0 + 270, y), valor, f_v, TINTA, 0.05)
        y += 54

    # 4. autoria
    dx0, dx1 = divisorias[2] + 60, divisorias[3] - 60
    colar(im, Image.open(ASSETS / "logo_denise_zuba.png").convert("RGBA"), dx0, topo + 20, largura=dx1 - dx0)
    texto(d, (dx0, topo + 205), "AUTORIA DO PROJETO", fonte("Medium", 22), CINZA, 0.2)
    texto(d, (dx0, topo + 243), "ARQUITETOS ASSISTENTES", fonte("Regular", 20), CINZA, 0.16)
    f_e = fonte("Medium", 23)
    while largura_txt(EQUIPE, f_e, 0.05) > dx1 - dx0:
        f_e = fonte("Medium", f_e.size - 1)
    texto(d, (dx0, topo + 278), EQUIPE, f_e, TINTA, 0.05)

    # 5. cliente
    lx0, lx1 = divisorias[3] + 70, LARGURA - 80
    logo = Image.open(ASSETS / "logo_paulo_octavio.png").convert("RGBA")
    w = lx1 - lx0
    h = round(logo.height * w / logo.width)
    colar(im, logo, lx0, (topo + base_y) / 2 - h / 2 - 10, largura=w)
    return im.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", type=Path, default=AQUI.parent / "entrega")
    ap.add_argument("--render", action="append", default=[], metavar="PAVIMENTO=ARQUIVO",
                    help="monta a prancha render + rodapé (pode repetir)")
    args = ap.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    feitos = {}
    for chave in PAVIMENTOS:
        r = rodape(chave)
        caminho = args.saida / f"POE642_CasaA_rodape_{chave}.png"
        r.save(caminho)
        feitos[chave] = r
        print(caminho, r.size)
    for item in args.render:
        chave, arq = item.split("=", 1)
        render = Image.open(arq).convert("RGB")
        rod = feitos[chave].resize((render.width, round(ALTURA * render.width / LARGURA)), Image.LANCZOS)
        prancha = Image.new("RGB", (render.width, render.height + rod.height), BRANCO)
        prancha.paste(render, (0, 0))
        prancha.paste(rod, (0, render.height))
        caminho = args.saida / f"POE642_CasaA_PH_{chave}_entrega.png"
        prancha.save(caminho)
        print(caminho, prancha.size)


if __name__ == "__main__":
    main()

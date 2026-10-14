#!/usr/bin/env python3
"""Rodapé de entrega das plantas humanizadas da Casa A (POE 642), um por pavimento.

Segue o carimbo da folha de layout do cliente (642-ARQ-EX-001): norte, título "LAYOUT – …",
quadro de áreas, dados do projeto, assinatura do render (New Air) e marca do cliente. Não leva cotas.

As pranchas têm todas o mesmo tamanho e a planta no mesmo lugar: cada render é alinhado
(SIFT + afim) à base do seu pavimento, e as três bases saem do mesmo enquadramento da folha
do cliente (a piscina cai no mesmo pixel nas três). Assim, vistas em sequência, uma planta
fica exatamente "dentro" da outra.

Uso:
  python rodape_entrega.py --saida ../entrega                    # só os três rodapés (3840 px)
  python rodape_entrega.py --saida ../entrega --render Terreo=../renders/t.png --render 1Pavimento=../renders/p.png
      # também as pranchas: render alinhado ao quadro comum + rodapé
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "entrega" / "assets"
FONTES = ASSETS / "fontes"   # Inter (licença SIL OFL), junto do projeto para rodar em qualquer máquina

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
    ("DATA INICIAL", "14/10/26"),
]
ASSINATURA = ["RENDER 3D", "PROJETOS COM IA", "CONRADO CORTEZ"]

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
    texto(d, (x0, topo + 215), "BASE: PLANTA BAIXA", fonte("Regular", 27), CINZA, 0.12)
    texto(d, (x0, topo + 257), "IMAGEM ILUSTRATIVA", fonte("Regular", 22), CINZA, 0.10)

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

    # 4. assinatura do render: logo da New Air e, embaixo, as três linhas, centralizados no bloco
    dx0, dx1 = divisorias[2], divisorias[3]
    meio = (dx0 + dx1) / 2
    logo_na = Image.open(ASSETS / "logo_new_air.png").convert("RGBA")
    h_na = 150
    w_na = round(logo_na.width * h_na / logo_na.height)
    colar(im, logo_na, meio - w_na / 2, topo + 8, altura=h_na)
    marinho = (20, 37, 60)                               # o azul da marca
    texto(d, (meio, topo + 205), ASSINATURA[0], fonte("Medium", 24), CINZA, 0.22, ancora="ms")
    texto(d, (meio, topo + 243), ASSINATURA[1], fonte("Medium", 24), CINZA, 0.22, ancora="ms")
    texto(d, (meio, topo + 288), ASSINATURA[2], fonte("SemiBold", 30), marinho, 0.12, ancora="ms")

    # 5. cliente
    lx0, lx1 = divisorias[3] + 70, LARGURA - 80
    logo = Image.open(ASSETS / "logo_paulo_octavio.png").convert("RGBA")
    w = lx1 - lx0
    h = round(logo.height * w / logo.width)
    colar(im, logo, lx0, (topo + base_y) / 2 - h / 2 - 10, largura=w)
    return im.convert("RGB")


BASES = {"Terreo": "POE642_CasaA_BASE_Terreo_v6_16x9.png",
         "1Pavimento": "POE642_CasaA_BASE_1Pavimento_v3_16x9.png",
         "Subsolo": "POE642_CasaA_BASE_Subsolo_v4_16x9.png"}


def no_quadro_comum(render, chave, largura):
    """Leva o render para o quadro da base 16:9 (o mesmo nos três pavimentos), na largura dada."""
    base = cv2.imread(str(AQUI.parent / "bases" / BASES[chave]))
    r = cv2.cvtColor(np.asarray(render), cv2.COLOR_RGB2BGR)
    if r.shape[1] != largura:
        r = cv2.resize(r, (largura, round(r.shape[0] * largura / r.shape[1])), interpolation=cv2.INTER_AREA)
    altura = round(base.shape[0] * largura / base.shape[1])
    base_red = cv2.resize(base, (largura, altura), interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(12000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base_red, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(r, cv2.COLOR_BGR2GRAY), None)
    bons = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.75 * b.distance]
    src = np.float32([k1[m.queryIdx].pt for m in bons])
    dst = np.float32([k2[m.trainIdx].pt for m in bons])
    A, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=2.5)   # base -> render
    res = np.linalg.norm(src @ A[:, :2].T + A[:, 2] - dst, axis=1)[inl.ravel() == 1]
    print(f"    {chave}: {int(inl.sum())} pontos, erro mediano {np.median(res):.2f} px")
    al = cv2.warpAffine(r, cv2.invertAffineTransform(A), (largura, altura),
                        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    return Image.fromarray(cv2.cvtColor(al, cv2.COLOR_BGR2RGB))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", type=Path, default=AQUI.parent / "entrega")
    ap.add_argument("--render", action="append", default=[], metavar="PAVIMENTO=ARQUIVO",
                    help="monta a prancha render + rodapé (pode repetir)")
    ap.add_argument("--largura", type=int, default=2000, help="largura das pranchas em px (a mesma nas três)")
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
        render = no_quadro_comum(Image.open(arq).convert("RGB"), chave, args.largura)
        rod = feitos[chave].resize((render.width, round(ALTURA * render.width / LARGURA)), Image.LANCZOS)
        prancha = Image.new("RGB", (render.width, render.height + rod.height), BRANCO)
        prancha.paste(render, (0, 0))
        prancha.paste(rod, (0, render.height))
        caminho = args.saida / f"POE642_CasaA_PH_{chave}_entrega.png"
        prancha.save(caminho)
        print(caminho, prancha.size)


if __name__ == "__main__":
    main()

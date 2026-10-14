#!/usr/bin/env python3
"""Rodapé de entrega das plantas humanizadas (POE 642), um por pavimento, para cada casa.

Segue o carimbo da folha de layout do cliente (642-ARQ-EX-001): norte, título "LAYOUT – …",
quadro de áreas, dados do projeto, assinatura do render (New Air) e marca do cliente. Não leva cotas.

As pranchas têm todas o mesmo tamanho e a planta no mesmo lugar: cada render é alinhado
(SIFT + afim) à base do seu pavimento, e as bases saem do mesmo enquadramento da folha
do cliente (na Casa A, a piscina cai no mesmo pixel nas três). Assim, vistas em sequência,
uma planta fica exatamente "dentro" da outra.

Os dados de cada casa (pavimentos, áreas, projeto, bases) ficam na chave 'entrega' da
config_bases.json da casa; sem --config, vale a da Casa A.

Uso:
  python rodape_entrega.py                                       # só os rodapés da Casa A (3840 px)
  python rodape_entrega.py --render Terreo=../renders/t.png --render 1Pavimento=../renders/p.png
      # também as pranchas: render alinhado ao quadro comum + rodapé
  python rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --render Subsolo=../../POE642_CasaB/renders/s.png
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "entrega" / "assets"
FONTES = ASSETS / "fontes"   # Inter (licença SIL OFL), junto do projeto para rodar em qualquer máquina

CONFIG_PADRAO = AQUI / "config_bases.json"      # Casa A
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


def rodape(ent, chave):
    pav = ent["pavimentos"][chave]
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
    areas = ent["areas"]
    for i, (nome, valor) in enumerate(areas):
        total = i == len(areas) - 1
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
    texto(d, (px0, topo + 62), f"{ent['casa']} – {pav['titulo']}", f_c, TINTA, 0.06)
    f_l, f_v = fonte("Regular", 25), fonte("Medium", 29)
    y = topo + 130
    for rotulo, valor in ent["projeto"]:
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


def no_quadro_comum(render, base_png, chave, largura):
    """Leva o render para o quadro da base 16:9 (o mesmo em todos os pavimentos), na largura dada."""
    base = cv2.imread(str(base_png))
    r = cv2.cvtColor(np.asarray(render), cv2.COLOR_RGB2BGR)
    if r.shape[1] != largura:
        # reduzir com INTER_AREA; ampliar (ex.: render 2K numa prancha de 3840 px) com Lanczos
        interp = cv2.INTER_AREA if r.shape[1] > largura else cv2.INTER_LANCZOS4
        r = cv2.resize(r, (largura, round(r.shape[0] * largura / r.shape[1])), interpolation=interp)
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
    ap.add_argument("--config", type=Path, default=CONFIG_PADRAO, help="config da casa (chave 'entrega')")
    ap.add_argument("--saida", type=Path, default=None, help="padrão: a pasta_entrega da config")
    ap.add_argument("--render", action="append", default=[], metavar="PAVIMENTO=ARQUIVO",
                    help="monta a prancha render + rodapé (pode repetir)")
    ap.add_argument("--largura", type=int, default=None,
                    help="largura das pranchas em px, a mesma em todos os pavimentos (padrão: entrega.largura_prancha, ou 2000)")
    args = ap.parse_args()
    ent = json.loads(args.config.read_text())["entrega"]
    raiz = args.config.resolve().parent
    args.saida = args.saida or raiz / ent["pasta_entrega"]
    args.largura = args.largura or ent.get("largura_prancha", 2000)
    args.saida.mkdir(parents=True, exist_ok=True)
    feitos = {}
    for chave in ent["pavimentos"]:
        r = rodape(ent, chave)
        caminho = args.saida / f"{ent['prefixo']}_rodape_{chave}.png"
        r.save(caminho)
        feitos[chave] = r
        print(caminho, r.size)
    for item in args.render:
        chave, arq = item.split("=", 1)
        base_png = raiz / ent["pasta_bases"] / ent["pavimentos"][chave]["base"]
        render = no_quadro_comum(Image.open(arq).convert("RGB"), base_png, chave, args.largura)
        rod = feitos[chave].resize((render.width, round(ALTURA * render.width / LARGURA)), Image.LANCZOS)
        prancha = Image.new("RGB", (render.width, render.height + rod.height), BRANCO)
        prancha.paste(render, (0, 0))
        prancha.paste(rod, (0, render.height))
        caminho = args.saida / f"{ent['prefixo']}_PH_{chave}_entrega.png"
        prancha.save(caminho)
        print(caminho, prancha.size)


if __name__ == "__main__":
    main()

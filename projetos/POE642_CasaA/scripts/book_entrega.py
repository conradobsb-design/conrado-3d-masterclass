#!/usr/bin/env python3
"""O book de entrega das plantas humanizadas das Casas A a E (POE 642), no modelo editorial (Modelo 2, escolhido pelo
usuário em 29/10/26: "modelo 2").

A3 deitado (420 x 297 mm), páginas desenhadas a 200 dpi e juntadas num PDF:
  capa (um recorte ampliado da planta) · sumário · por casa: abertura (número, nome, texto de apresentação, quadro de
  áreas e um recorte ampliado), uma página por pavimento (a planta aprovada, sem o rodapé técnico, com o norte e a área)
  e uma página de detalhes (dois recortes ampliados com a legenda) · contracapa (créditos e a nota de planta ilustrativa).

As plantas vêm das pranchas de entrega aprovadas (`POE642_Casa?/entrega/POE642_Casa?_PH_<pavimento>_entrega.png`, a
parte de cima, 3840 x 2160): nada é redesenhado. Os textos de apresentação só listam o programa pelos nomes dos ambientes
dos PDFs do cliente (`_pdfs_cliente`), sem número de vagas nem posição dos ambientes; são provisórios até o texto da
Paulo Octávio.

Áreas: as do cliente (as da prancha); sem dado, "não informado" e sem total (Casas D e E), como no quadro das pranchas.

Uso:
  python3 book_entrega.py              # grava POE642_Book/POE642_Book_Plantas_Humanizadas.pdf e a prévia (uma folha)
  python3 book_entrega.py --paginas    # e também cada página em JPG (POE642_Book/paginas, fora do git), para conferir
"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
PROJ = AQUI.parents[1]
SAIDA = PROJ / "POE642_Book"
ASSETS = PROJ / "POE642_CasaA" / "entrega" / "assets"

W, H = 3307, 2339                       # A3 deitado a 200 dpi
S = W / 1600                            # o desenho foi feito numa página de 1600 px de largura
VERM = (189, 27, 32)                    # o vermelho da identidade do cliente (#BD1B20)
GRAF = (33, 37, 41)
CINZA = (120, 124, 128)
CREME = (244, 241, 236)
PEDRA = (190, 180, 168)
NOTA = ("Plantas humanizadas ilustrativas. Mobiliário, equipamentos, objetos e paisagismo são sugestões de decoração "
        "e não fazem parte do contrato.")

CASAS = {
    "A": {"pavs": ["Subsolo", "Térreo", "1º Pavimento"],
          "areas": [("Subsolo", "160,40 m²"), ("Térreo", "427,40 m²"), ("1º Pavimento", "263,25 m²"), ("Total", "851,05 m²")],
          "texto": ("No térreo, a varanda, a sala de estar e a sala de jantar, o escritório, a cozinha, a área gourmet, a"
                   " piscina com prainha e spa e a garagem. No 1º pavimento, a suíte master, mais três suítes e a sala "
                   "íntima. No subsolo, academia, sauna e banhos.")},
    "B": {"pavs": ["Subsolo", "Térreo"],
          "areas": [("Térreo", "638,70 m²"), ("Subsolo", "79,05 m²"), ("Total", "717,75 m²")],
          "texto": ("No térreo, o living e o jantar com o jardim de inverno, a varanda gourmet, a piscina com prainha e "
                   "spa, a suíte master, mais três suítes, a sala íntima e a garagem. No subsolo, academia, sauna, "
                   "ducha, depósito e garagem.")},
    "C": {"pavs": ["Subsolo", "Térreo"],
          "areas": [("Térreo", "798,89 m²"), ("Subsolo", "113,81 m²"), ("Total", "912,70 m²")],
          "texto": ("No térreo, o estar, o jantar, a sala de TV e dois jardins de inverno, o gourmet e a varanda gourmet,"
                   " a piscina com prainha e spa, a suíte master, três quartos, o escritório e a garagem. No subsolo, "
                   "academia, sauna, depósito e varanda.")},
    "D": {"pavs": ["Subsolo", "Térreo"],
          "areas": [("Térreo", "não informado"), ("Subsolo", "não informado")],
          "texto": ("No térreo, o living e o jantar, a varanda gourmet, a piscina com prainha e spa, o gourmet e a "
                   "cozinha, a suíte master, duas suítes, a suíte com escritório, a sala íntima e a garagem. No subsolo,"
                   " academia, sauna, vestiário e depósito.")},
    "E": {"pavs": ["Subsolo", "Térreo", "1º Pavimento"],
          "areas": [("Subsolo", "não informado"), ("Térreo", "não informado"), ("1º Pavimento", "não informado")],
          "texto": ("No térreo, o living e a sala de jantar, a varanda, a piscina com prainha e spa, a área gourmet, o "
                   "escritório e a garagem. No 1º pavimento, a suíte master, mais quatro suítes e a sala íntima. No "
                   "subsolo, academia, sauna, vestiário e piscina.")},
}
ARQ = {"Subsolo": "Subsolo", "Térreo": "Terreo", "1º Pavimento": "1Pavimento"}
ROMANO = {"A": "01", "B": "02", "C": "03", "D": "04", "E": "05"}

# os recortes ampliados (px na planta de 3840 x 2160), conferidos um a um com a legenda (os nomes dos ambientes à vista)
CAPA = ("B", "Térreo", (250, 560, 1450, 1240))
ABERTURA = {
    "A": ("Térreo", (1500, 330, 2200, 1250), "Sala de estar e varanda"),
    "B": ("Térreo", (1560, 700, 2220, 1570), "Living, jantar e jardim de inverno"),
    "C": ("Térreo", (1700, 780, 2400, 1700), "Jardim de inverno e jantar"),
    "D": ("Térreo", (1800, 680, 2440, 1530), "Living e jantar"),
    "E": ("Térreo", (1600, 800, 2200, 1590), "Living e sala de jantar"),
}
DETALHES = {
    "A": [("Térreo", (700, 380, 1450, 1130), "Piscina, prainha e deck"),
          ("1º Pavimento", (1330, 1100, 1970, 1740), "Suíte master · 1º Pavimento")],
    "B": [("Térreo", (600, 800, 1500, 1700), "Varanda gourmet e piscina"),
          ("Térreo", (940, 340, 1600, 1000), "Suíte master")],
    "C": [("Térreo", (1640, 1000, 2440, 1800), "Estar"),
          ("Térreo", (740, 480, 1300, 1040), "Suíte master")],
    "D": [("Térreo", (900, 460, 1800, 1360), "Piscina e varanda gourmet"),
          ("Térreo", (1400, 1150, 2050, 1800), "Sala íntima e suítes")],
    "E": [("Térreo", (640, 880, 1400, 1640), "Piscina e varanda"),
          ("1º Pavimento", (1380, 450, 1900, 970), "Suíte master · 1º Pavimento")],
}


def z(v):
    return int(round(v * S))


_fontes = {}


def F(peso, t):
    k = (peso, t)
    if k not in _fontes:
        _fontes[k] = ImageFont.truetype(str(ASSETS / "fontes" / f"Inter-{peso}.otf"), z(t))
    return _fontes[k]


_plantas = {}


def planta(c, pav):
    k = (c, pav)
    if k not in _plantas:
        im = cv2.imread(str(PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{ARQ[pav]}_entrega.png"))
        _plantas[k] = cv2.cvtColor(im[:2160], cv2.COLOR_BGR2RGB)
    return _plantas[k]


def recorte(c, pav, caixa):
    x0, y0, x1, y1 = caixa
    return Image.fromarray(planta(c, pav)[y0:y1, x0:x1])


def caixa_planta(c, pav):
    """O enquadramento da página. Térreo e 1º Pavimento: o lote (tudo o que não é branco) somado nos dois, a mesma caixa
    na mesma escala e posição (as pranchas compartilham as coordenadas), para o leitor ver um pavimento sobre o outro.
    Subsolo: o que está desenhado, com as peças do Térreo nevoadas inteiras (as manchas cheias; a hachura do lote e as
    linhas finas somem na abertura), com folga; no lote inteiro o subsolo ficava pequeno demais para ler os rótulos."""
    if pav == "Subsolo":
        m = (planta(c, pav).min(axis=2) < 250).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
        n, _, st, _ = cv2.connectedComponentsWithStats(m)
        ok = [i for i in range(1, n) if st[i, 4] > 2000]
        caixas = [(st[i, 0], st[i, 1], st[i, 0] + st[i, 2], st[i, 1] + st[i, 3]) for i in ok]
        f = 120
    else:
        caixas = []
        for p in CASAS[c]["pavs"]:
            if p != "Subsolo":
                ys, xs = np.nonzero(planta(c, p).min(axis=2) < 235)
                caixas.append((xs.min(), ys.min(), xs.max(), ys.max()))
        f = 20
    x0, y0 = min(k[0] for k in caixas), min(k[1] for k in caixas)
    x1, y1 = max(k[2] for k in caixas), max(k[3] for k in caixas)
    hh, ww = planta(c, pav).shape[:2]
    return max(0, x0 - f), max(0, y0 - f), min(ww, x1 + f), min(hh, y1 + f)


def caixa_cor(c, pav):
    """Só o que tem cor (o gramado e a casa), para as miniaturas do sumário: sem a faixa branca até a linha do lote."""
    a = planta(c, pav).astype(np.int16)
    m = ((a.max(axis=2) - a.min(axis=2)) > 22).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def caber(img, w, h, fundo):
    im = img.copy()
    k = min(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    tela = Image.new("RGB", (w, h), fundo)
    tela.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return tela


def cobrir(img, w, h):
    k = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * k + 1), int(img.height * k + 1)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def texto(d, xy, s, f, cor=GRAF, track=0, anchor="la"):
    """Texto em px da página de 1600 (xy em unidades do desenho), com espaçamento entre letras (`track`)."""
    x, y = z(xy[0]), z(xy[1])
    if not track:
        d.text((x, y), s, font=f, fill=cor, anchor=anchor)
        return
    larg = sum(d.textlength(ch, font=f) + z(track) for ch in s) - z(track)
    if anchor[0] == "r":
        x -= larg
    elif anchor[0] == "m":
        x -= larg / 2
    for ch in s:
        d.text((x, y), ch, font=f, fill=cor, anchor="l" + anchor[1])
        x += d.textlength(ch, font=f) + z(track)


def linha(d, x0, y0, x1, y1, cor, larg=1):
    d.line((z(x0), z(y0), z(x1), z(y1)), fill=cor, width=max(1, z(larg)))


def pagina(fundo=CREME):
    im = Image.new("RGB", (W, H), fundo)
    return im, ImageDraw.Draw(im)


def rodape(d, n, cor=CINZA):
    texto(d, (60, 1085), "PLANTAS HUMANIZADAS  ·  CASAS A — E", F("Regular", 11), cor, track=2.5)
    texto(d, (1540, 1085), f"{n:02d}", F("Medium", 14), cor, anchor="ra")


# ---------------------------------------------------------------------------------------------------------------------
def capa():
    c, pav, cx = CAPA
    im = cobrir(recorte(c, pav, cx), W, H)
    v = Image.new("RGB", (W, z(440)), (20, 20, 20))
    m = Image.linear_gradient("L").resize((W, z(440))).point(lambda p: int(p * 0.78))
    im.paste(v, (0, H - z(440)), m)
    d = ImageDraw.Draw(im)
    texto(d, (90, 1131 - 300), "CASAS A — E", F("Light", 30), (235, 235, 235), track=14)
    texto(d, (88, 1131 - 248), "Plantas Humanizadas", F("Light", 92), (255, 255, 255))
    texto(d, (92, 1131 - 112), "ML 10 · CONJUNTO 02 · LOTE 17", F("Regular", 17), (215, 215, 215), track=6)
    texto(d, (1510, 1131 - 112), "PAULO OCTÁVIO", F("SemiBold", 17), (255, 255, 255), track=6, anchor="ra")
    return im


def sumario(paginas):
    im, d = pagina()
    texto(d, (90, 110), "Sumário", F("Light", 64))
    linha(d, 92, 205, 190, 205, VERM, 3)
    for i, ln in enumerate(["Cinco casas no mesmo lote, apresentadas pavimento",
                            "por pavimento, com recortes ampliados dos ambientes."]):
        texto(d, (92, 240 + i * 34), ln, F("Light", 21), (80, 80, 80))
    y = 380
    for c in "ABCDE":
        texto(d, (92, y), ROMANO[c], F("Light", 40), PEDRA)
        texto(d, (190, y + 2), f"Casa {c}", F("Light", 36))
        texto(d, (192, y + 52), "  ·  ".join(CASAS[c]["pavs"]), F("Regular", 15), CINZA, track=1)
        texto(d, (700, y + 14), f"{paginas[c]:02d}", F("Medium", 20), GRAF, anchor="ra")
        linha(d, 92, y + 92, 700, y + 92, (222, 216, 208), 1)
        y += 128
    # as cinco casas no térreo, à direita, alinhadas pela margem
    th, xr, y = 150, 1540, 110
    for c in "ABCDE":
        x0, y0, x1, y1 = caixa_cor(c, "Térreo")
        mini = Image.fromarray(planta(c, "Térreo")[y0:y1, x0:x1])
        mini = mini.resize((int(mini.width * z(th) / mini.height), z(th)), Image.LANCZOS)
        im.paste(mini, (z(xr) - mini.width, z(y)))
        texto(d, (xr - mini.width / S - 24, y + th / 2), f"Casa {c}", F("Regular", 15), CINZA, anchor="rm")
        y += th + 42
    rodape(d, 2)
    return im


def quebrar(d, s, f, larg):
    linhas, ln = [], ""
    for p in s.split():
        t = (ln + " " + p).strip()
        if d.textlength(t, font=f) > z(larg) and ln:
            linhas.append(ln)
            ln = p
        else:
            ln = t
    return linhas + [ln]


def abertura(c, n):
    im, d = pagina()
    pav, cx, leg = ABERTURA[c]
    x0 = W // 2 - z(60)
    im.paste(cobrir(recorte(c, pav, cx), W - x0, H), (x0, 0))
    # a legenda da foto na coluna do texto (sobre a foto, cobria os rótulos da planta)
    texto(d, (92, 1131 - 112), f"NA IMAGEM  ·  {leg.upper()}", F("Regular", 12), CINZA, track=2.5)
    texto(d, (90, 110), ROMANO[c], F("Light", 120), PEDRA)
    texto(d, (88, 282), f"Casa {c}", F("Light", 96))
    linha(d, 92, 412, 200, 412, VERM, 3)
    for i, ln in enumerate(quebrar(d, CASAS[c]["texto"], F("Light", 21), 590)):
        texto(d, (92, 452 + i * 34), ln, F("Light", 21), (70, 70, 70))
    y = 700
    for nome, val in CASAS[c]["areas"]:
        tot = nome == "Total"
        texto(d, (92, y), nome.upper(), F("Regular", 14), CINZA, track=3)
        texto(d, (330, y - 5), val, F("Medium" if tot else "Light", 23), VERM if tot else GRAF)
        y += 46
    texto(d, (92, 1131 - 75), "  ·  ".join(CASAS[c]["pavs"]), F("Regular", 15), GRAF, track=2)
    return im


def pavimento(c, pav, n):
    im, d = pagina()
    x0, y0, x1, y1 = caixa_planta(c, pav)
    pw, ph = 1140, 980
    im.paste(Image.new("RGB", (z(pw), z(ph)), (255, 255, 255)), (z(60), z(70)))
    im.paste(caber(Image.fromarray(planta(c, pav)[y0:y1, x0:x1]), z(pw - 40), z(ph - 40), (255, 255, 255)),
             (z(80), z(90)))
    xr = 1250
    texto(d, (xr, 100), f"Casa {c}", F("Light", 58))
    texto(d, (xr + 2, 182), pav.upper(), F("Medium", 16), GRAF, track=4)
    area = dict(CASAS[c]["areas"]).get(pav, "não informado")
    texto(d, (xr + 2, 212), area, F("Light", 22), CINZA)
    linha(d, xr + 2, 262, xr + 92, 262, VERM, 3)
    # o quadro de áreas da casa, com o pavimento da página em destaque
    y = 300
    for nome, val in CASAS[c]["areas"]:
        este = nome == pav
        tot = nome == "Total"
        cor = VERM if este else (GRAF if tot else CINZA)
        texto(d, (xr + 2, y), nome.upper(), F("SemiBold" if este else "Regular", 12), cor, track=2.5)
        texto(d, (1540, y - 3), val, F("Medium" if (este or tot) else "Light", 16), cor, anchor="ra")
        linha(d, xr + 2, y + 30, 1540, y + 30, (222, 216, 208), 1)
        y += 46
    norte = Image.open(ASSETS / "norte.png").convert("RGBA")
    k = z(56) / norte.height
    norte = norte.resize((int(norte.width * k), z(56)), Image.LANCZOS)
    fundo = Image.new("RGBA", norte.size, CREME + (255,))
    fundo.alpha_composite(norte)
    im.paste(fundo.convert("RGB"), (z(xr + 2), z(860)))
    texto(d, (xr + 2, 945), "Planta ilustrativa. Mobiliário, objetos e", F("Regular", 12), CINZA)
    texto(d, (xr + 2, 965), "paisagismo são sugestões de decoração.", F("Regular", 12), CINZA)
    rodape(d, n)
    return im


def detalhes(c, n):
    im, d = pagina()
    texto(d, (60, 70), f"Casa {c}", F("Light", 40))
    texto(d, (62, 128), "DETALHES", F("Medium", 14), CINZA, track=4)
    linha(d, 62, 160, 140, 160, VERM, 3)
    lado, y0 = 690, 200
    for i, (pav, cx, leg) in enumerate(DETALHES[c]):
        x = 60 + i * (lado + 100)
        im.paste(cobrir(recorte(c, pav, cx), z(lado), z(lado)), (z(x), z(y0)))
        texto(d, (x, y0 + lado + 26), leg, F("Light", 22), GRAF)
    rodape(d, n)
    return im


def contracapa():
    im, d = pagina(GRAF)
    texto(d, (90, 130), "Plantas Humanizadas", F("Light", 54), (255, 255, 255))
    texto(d, (92, 210), "CASAS A — E", F("Regular", 16), (200, 200, 200), track=6)
    linha(d, 92, 250, 190, 250, VERM, 3)
    y = 320
    for rot, val in [("CLIENTE", "Paulo Octávio"), ("ENDEREÇO", "ML 10 – Conjunto 02, Lote 17, Unidades A, B, C, D e E"),
                     ("CONTEÚDO", "12 plantas humanizadas: Subsolo, Térreo e 1º Pavimento"),
                     ("PLANTAS HUMANIZADAS", "New Air · Render 3D · Conrado Cortez"), ("DATA", "Outubro de 2026")]:
        texto(d, (92, y), rot, F("Regular", 13), (170, 170, 170), track=3)
        texto(d, (92, y + 26), val, F("Light", 24), (255, 255, 255))
        y += 92
    for i, ln in enumerate([NOTA[:96].rsplit(" ", 1)[0], NOTA[len(NOTA[:96].rsplit(" ", 1)[0]) + 1:]]):
        texto(d, (92, 1131 - 120 + i * 24), ln, F("Regular", 14), (170, 170, 170))
    logo = Image.open(ASSETS / "logo_new_air.png").convert("RGBA")
    k = z(70) / logo.height
    logo = logo.resize((int(logo.width * k), z(70)), Image.LANCZOS)
    claro = Image.new("RGBA", (logo.width + z(40), logo.height + z(30)), (255, 255, 255, 255))
    claro.alpha_composite(logo, (z(20), z(15)))
    im.paste(claro.convert("RGB"), (W - z(90) - claro.width, z(130)))
    return im


def montar(paginas=False):
    SAIDA.mkdir(exist_ok=True)
    if paginas:
        (SAIDA / "paginas").mkdir(exist_ok=True)
    ordem = [("capa", capa)]
    # o número da página de cada casa, para o sumário: capa 1, sumário 2, depois as casas
    n, paginas_casa, corpo = 3, {}, []
    for c in "ABCDE":
        paginas_casa[c] = n
        corpo.append((f"casa{c}_abertura", lambda c=c, n=n: abertura(c, n)))
        n += 1
        for pav in CASAS[c]["pavs"]:
            corpo.append((f"casa{c}_{ARQ[pav]}", lambda c=c, pav=pav, n=n: pavimento(c, pav, n)))
            n += 1
        corpo.append((f"casa{c}_detalhes", lambda c=c, n=n: detalhes(c, n)))
        n += 1
    ordem += [("sumario", lambda: sumario(paginas_casa))] + corpo + [("contracapa", contracapa)]
    doc = pymupdf.open()
    th = []
    for i, (nome, f) in enumerate(ordem, 1):
        img = f()
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=90, subsampling=0, dpi=(200, 200))
        if paginas:
            (SAIDA / "paginas" / f"{i:02d}_{nome}.jpg").write_bytes(buf.getvalue())
        pg = doc.new_page(width=420 / 25.4 * 72, height=297 / 25.4 * 72)
        pg.insert_image(pg.rect, stream=buf.getvalue())
        th.append(img.resize((480, 340), Image.LANCZOS))
        print(f"  {i:02d} {nome}")
    doc.set_metadata({"title": "Plantas Humanizadas · Casas A–E · ML 10, Conjunto 02, Lote 17",
                      "author": "New Air · Render 3D · Conrado Cortez", "subject": "Book de entrega (POE 642)",
                      "keywords": "plantas humanizadas, Paulo Octávio, Casas A a E"})
    pdf = SAIDA / "POE642_Book_Plantas_Humanizadas.pdf"
    doc.save(str(pdf), garbage=4, deflate=True)
    print(pdf, f"{pdf.stat().st_size / 1e6:.1f} MB, {len(ordem)} páginas")
    # a prévia: todas as páginas numa folha
    cols = 6
    linhas = (len(th) + cols - 1) // cols
    folha = Image.new("RGB", (cols * 500 + 20, linhas * 360 + 20), (228, 226, 222))
    for i, t in enumerate(th):
        folha.paste(t, (20 + (i % cols) * 500, 20 + (i // cols) * 360))
    folha.save(SAIDA / "POE642_Book_previa.jpg", quality=88)


if __name__ == "__main__":
    montar(paginas="--paginas" in sys.argv)

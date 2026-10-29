"""Auditoria de 26/10: as 11 especificações do usuário conferidas nas 12 plantas (Casas A a E).

Só aponta; não altera nenhuma imagem (o usuário aprova antes). Cada planta ganha um mapa numerado sobre a
prancha de entrega (coordenadas em px do quadro 3840 x 2160), com a legenda embaixo, colorida por especificação:

  E1 soleiras · E2 armários com cabides · E3 sentido da escada (S/D) · E4 seta na entrada principal · E5 boxes
  E6 raios das portas · E7 rótulos (fora dos objetos, branco ou preto) · E8 escada mais demarcada
  E9 bancada x piso da mesma cor · E10 paredes cinza-escuro e pilares pretos · E11 escala dos pisos

    python auditoria_2610.py            # os 12 mapas
    python auditoria_2610.py D Terreo   # uma planta
"""
import json
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from opcoes_1pav_casae import quadro_pdf  # noqa: E402
from retoque_1pav_casae import rotulos_pdf  # noqa: E402
from rodape_entrega import FONTES  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
NOME_PDF = {"Terreo": "TÉRREO", "Subsolo": "SUBSOLO", "1Pavimento": "1º PAVIMENTO"}
TITULO = {"Terreo": "Térreo", "Subsolo": "Subsolo", "1Pavimento": "1º Pavimento"}
COR = {"E1": (120, 120, 120), "E2": (150, 60, 170), "E3": (0, 110, 200), "E4": (220, 30, 30),
       "E5": (0, 150, 150), "E6": (120, 120, 120), "E7": (230, 120, 0), "E8": (0, 110, 200),
       "E9": (40, 150, 40), "E10": (40, 40, 40), "E11": (160, 110, 40), "EXTRA": (200, 0, 120)}

GERAL = ("E10 paredes: todas pretas (RGB 2 a 17) -> cinza-escuro; pilares -> preto. E6 raios: nenhum raio de porta "
         "visível (conforme). E1 soleiras: todas as portas conferem com o PDF (conforme).")

ESCADA = "triângulo (R14) -> sentido S/D e degraus mais demarcados"
ARMARIO = "armário cortado sem cabides -> cabides como nos closets"
BOX = "box só como linha tracejada/fraca -> vidro contínuo"
BANCADA = "bancada da mesma cor do piso -> borda/sombra mais marcada que o piso"

ITENS = {
    ("A", "Subsolo"): [
        ("E3", f"Escada do deck: {ESCADA}", [(1069, 1092)]),
        ("E7", "BANHO SERV.: rótulo dentro da área do chuveiro, sobre o box -> para o piso livre junto à porta",
         [(1135, 895)]),
    ],
    ("A", "Terreo"): [
        ("E4", "Entrada principal (porta pivotante do hall externo, acesso pelos pisantes do leste): sem seta",
         [(2530, 815)]),
        ("E3", f"Pisantes do deck (degraus 12 a 19): {ESCADA}", [(814, 534)]),
        ("E3", f"Escada do deck: {ESCADA}", [(914, 1096)]),
        ("E3", f"Escada interna do jardim: {ESCADA}", [(2268, 948)]),
        ("E3", "Escada caracol: sem indicação de sentido -> S/D", [(1977, 1572)]),
        ("E2", f"Q. motorista: {ARMARIO}", [(2517, 1150)]),
        ("E5", f"B. motorista: {BOX}", [(2308, 1260)]),
        ("E7", "LAVABO: a área (A: 4,05 m²) encosta na bancada -> deslocar para a esquerda", [(2300, 445)]),
        ("E9", f"Lavabo: {BANCADA}", [(2340, 485)]),
        ("E7", "SALA DE ESTAR: rótulo sobre o tapete redondo (a confirmar: tapete conta como objeto?)",
         [(2051, 543)]),
    ],
    ("A", "1Pavimento"): [
        ("E3", f"Escada interna (20 degraus): {ESCADA}", [(2272, 975)]),
        ("E3", "Escada caracol da saleta: sem indicação de sentido -> S/D", [(1967, 1518)]),
        ("E2", f"Quarto serv.: {ARMARIO}", [(2100, 1395)]),
        ("E5", f"Banho master: {BOX}", [(1430, 1560)]),
        ("E7", "BANHO 3 e B. SERVIÇO: rótulos encostados na linha do box -> para o piso livre",
         [(2160, 430), (2160, 1455)]),
        ("E9", f"Banhos 1, 2, 3, master e B. serviço: {BANCADA}",
         [(2516, 1279), (1766, 909), (2094, 389), (1601, 1610), (2236, 1550)]),
        ("E7", "SALA ÍNTIMA: rótulo sobre o tapete (a confirmar: tapete conta como objeto?)", [(2085, 1000)]),
        ("EXTRA", "Linha tracejada vertical espúria (x = 1472) atravessando a suíte master e o banho master; "
                  "não existe no PDF do 1º Pav. -> remover", [(1472, 1300), (1472, 1500)]),
    ],
    ("B", "Subsolo"): [
        ("E3", f"Escada da ducha (o PDF marca S): {ESCADA}", [(750, 637)]),
        ("E5", f"BH sauna: {BOX}", [(1247, 720)]),
        ("E9", f"BH serviço e BH sauna: {BANCADA}", [(1380, 360), (1344, 652)]),
    ],
    ("B", "Terreo"): [
        ("E4", "Entrada principal (porta pivotante entre o HALL e o HALL INTERNO, acesso pelos pisantes do leste): "
               "sem seta", [(2625, 995)]),
        ("E10", "Pilares redondos da garagem / quarto do motorista em cinza (130) -> preto",
         [(2813, 1384), (2815, 1501)]),
        ("E3", f"Pisantes NO, escada 1-9 da varanda e pisantes O: {ESCADA}", [(684, 643), (1081, 832), (608, 917)]),
        ("E9", f"Banhos master, 1, 2 e 3, lavabo, lavatório gourmet e ilha gourmet: {BANCADA}",
         [(1398, 346), (1849, 496), (2741, 540), (2607, 914), (2265, 841), (1323, 1627), (1423, 1351)]),
    ],
    ("C", "Subsolo"): [
        ("E3", f"Escada externa (2 triângulos): {ESCADA}", [(605, 910)]),
        ("E5", f"BH academia: {BOX}", [(865, 860)]),
        ("E9", f"BH academia: {BANCADA}", [(964, 811)]),
    ],
    ("C", "Terreo"): [
        ("E4", "Entrada principal (porta pivotante do HALL DE ENTRADA, acesso pelos pisantes do leste): sem seta",
         [(2760, 1324)]),
        ("E3", f"Escada da varanda master ao deck e escada 10-20: {ESCADA}", [(569, 965), (861, 1024)]),
        ("E2", f"Quarto externo: {ARMARIO}", [(3195, 811)]),
        ("E5", f"BH serviço: {BOX}", [(2665, 530)]),
        ("E7", "BH SERVIÇO: rótulo sobre a linha do box -> para o piso livre", [(2630, 565)]),
        ("E9", f"BH master 1 e 2, BH 1, 2 e 3, lavabos masc., fem. e social: {BANCADA}",
         [(775, 477), (662, 901), (1836, 371), (1782, 371), (1089, 371), (1216, 1565), (1520, 1569), (2381, 1108)]),
    ],
    ("D", "Subsolo"): [
        ("E3", f"Escada: {ESCADA}", [(992, 1288)]),
        ("E2", f"DCE 1: {ARMARIO}", [(910, 1015)]),
        ("E5", f"WC DCE: {BOX}", [(888, 1045)]),
    ],
    ("D", "Terreo"): [
        ("E4", "Entrada principal (porta pivotante do hall, acesso pelos pisantes do leste): sem seta",
         [(2675, 1058)]),
        ("E3", f"Escada do deck e pisantes da esquerda: {ESCADA}", [(992, 1288), (763, 928)]),
        ("E2", f"Suíte 3/escritório, DCE e módulo do closet master: {ARMARIO}",
         [(2167, 1470), (2507, 665), (967, 1660)]),
        ("E5", "Banho master sem vidro de box; banhos 1, 2 e 3 com o box só tracejado -> vidro contínuo",
         [(860, 1690), (1150, 1690), (2100, 1690), (2230, 1690)]),
        ("E9", f"Lavabo, banho master e banhos 1, 2 e 3 (bancada areia sobre piso bege): {BANCADA}",
         [(2592, 1270), (862, 1580), (1109, 1586), (2136, 1586), (2181, 1586)]),
    ],
    ("E", "Subsolo"): [
        ("E3", f"Escada da circulação (19 degraus, 2 triângulos): {ESCADA}", [(1302, 447)]),
        ("E2", f"DCE: {ARMARIO}", [(1680, 622)]),
        ("E7", "WC DCE 2: rótulo dentro da área do chuveiro -> para o piso livre", [(1900, 602)]),
        ("E9", f"WC DCE 2: {BANCADA}", [(1930, 510)]),
    ],
    ("E", "Terreo"): [
        ("E4", "Entrada principal (porta pivotante do HALL DE ENTRADA, acesso pelos pisantes do leste): sem seta",
         [(2565, 1430)]),
        ("E3", f"Escada da circulação gourmet, escada interna e escada externa do deck: {ESCADA}",
         [(1163, 447), (2202, 1005), (735, 1380)]),
        ("E2", f"DCE: {ARMARIO}", [(2239, 560)]),
        ("E5", f"WC DCE 1: {BOX}", [(2440, 552)]),
        ("E7", "WC DCE 1: rótulo dentro da área do chuveiro -> para o piso livre", [(2415, 530)]),
        ("E9", f"BH gourmet (bancada = granito do piso), WC DCE 1 e lavabo: {BANCADA}",
         [(1399, 574), (2459, 608), (2351, 1305)]),
    ],
    ("E", "1Pavimento"): [
        ("E3", f"Escada interna: {ESCADA}", [(1889, 1004)]),
        ("E9", f"Banhos master, 1, 2, 3 e 4 (bancada clara sobre o porcelanato claro): {BANCADA}",
         [(1927, 522), (2414, 955), (2416, 590), (1564, 1188), (1549, 1236)]),
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


def recorte(casa, pav):
    """A área construída: os rótulos dos ambientes do PDF no quadro, com folga."""
    cp = RAIZ / ("POE642_CasaA/scripts/config_bases.json" if casa == "A" else f"POE642_Casa{casa}/config_bases.json")
    cfg = json.loads(cp.read_text())
    pg = pymupdf.open(RAIZ / "_pdfs_cliente" / f"642 - {NOME_PDF[pav]} - CASA {casa}.pdf")[cfg["pavimentos"][pav]["pagina"]]
    base = (cp.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][pav]["base"]).resolve()
    sem = base.with_name(base.name.replace("_16x9", ""))
    lt, at = Image.open(base).size
    wb, hb = Image.open(sem).size
    f = quadro_pdf(pg, cfg, lt, at, wb, hb, 3840)
    pts = [f(*c) for n, _, c, _ in rotulos_pdf(pg) if not any(s in n for s in ("TÉRREO", "SUBSOLO", "PAVIMENTO", "Ref."))]
    pts = [p for p in pts if 0 < p[0] < 3840 and 0 < p[1] < 2160]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return max(0, int(min(xs)) - 230), max(0, int(min(ys)) - 200), min(3840, int(max(xs)) + 230), min(2160, int(max(ys)) + 200)


def mapa(casa, pav):
    pasta = RAIZ / f"POE642_Casa{casa}"
    img = Image.open(pasta / "entrega" / f"POE642_Casa{casa}_PH_{pav}_entrega.png").convert("RGB").crop((0, 0, 3840, 2160))
    x0, y0, x1, y1 = recorte(casa, pav)
    itens = ITENS[(casa, pav)]
    for _, _, pontos in itens:
        for x, y in pontos:
            x0, y0, x1, y1 = min(x0, x - 60), min(y0, y - 60), max(x1, x + 60), max(y1, y + 60)
    img = img.crop((x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    fn = fonte("SemiBold", 30)
    for n, (e, _, pontos) in enumerate(itens, 1):
        for x, y in pontos:
            cx, cy = x - x0, y - y0
            d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), outline=COR[e], width=5)
            d.text((cx + 24, cy - 32), str(n), font=fn, fill=COR[e], stroke_width=3, stroke_fill=(255, 255, 255))
    W = max(img.width, 1800)
    ft, fl, fb = fonte("SemiBold", 40), fonte("Regular", 30), fonte("SemiBold", 30)
    blocos = [quebrar(GERAL, fl, W - 80, d)]
    blocos += [quebrar(f"{n}. [{e}] {t}", fl, W - 80, d) for n, (e, t, _) in enumerate(itens, 1)]
    alt = 110 + sum(44 * len(b) + 14 for b in blocos)
    final = Image.new("RGB", (W, img.height + alt), (255, 255, 255))
    final.paste(img, ((W - img.width) // 2, 0))
    dl = ImageDraw.Draw(final)
    y = img.height + 30
    dl.text((40, y), f"Casa {casa} · {TITULO[pav]} · auditoria das especificações de 26/10", font=ft, fill=(20, 20, 20))
    y += 70
    for k, b in enumerate(blocos):
        cor = (90, 90, 90) if k == 0 else COR[itens[k - 1][0]]
        for i, li in enumerate(b):
            dl.text((40, y), li, font=fb if (k and i == 0) else fl, fill=cor if (k and i == 0) else (30, 30, 30))
            y += 44
        y += 14
    saida = pasta / "renders" / f"POE642_Casa{casa}_PH_{pav}_auditoria_2610.jpg"
    final.save(saida, quality=88)
    print(f"{saida.relative_to(RAIZ)} ({len(itens)} itens)")


if __name__ == "__main__":
    alvo = [(sys.argv[1], sys.argv[2])] if len(sys.argv) > 2 else list(ITENS)
    for casa, pav in alvo:
        mapa(casa, pav)

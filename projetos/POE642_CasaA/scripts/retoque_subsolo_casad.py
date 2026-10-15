#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Subsolo da Casa D (POE 642).

O render (Nano Banana Pro, 2000 x 1116) saiu fiel no layout, mas aproximou a planta (~2,73 x a
base reduzida a 2000 px). Os retoques são feitos no quadro do render, como no Térreo; no fim, a
imagem vai para o quadro comum das bases (a mesma folha e o mesmo enquadramento do Térreo), para
a planta do Subsolo cair exatamente sob a do Térreo.

Itens (o mapa está em POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_v1_erros.jpg):
1. Depósito: a faixa areia que o motor pôs junto à parede da esquerda (um armário que não existe no
   PDF) vira o granito do piso.
2. Depósito: as juntas de placas gigantes (~1,9 m) e as quatro manchas claras do granito saem; o piso
   fica contínuo, como no DCE 1 e no WC DCE (pedido do usuário).
3. WC DCE: o piso da área do chuveiro (acima da divisória) saiu mais claro e acinzentado; volta ao tom
   do granito do resto do banheiro (ganho por canal, a textura do render fica).
4. WC DCE: o símbolo do CAD (quadrado, braço e o toco na parede) vira o chuveiro do Térreo: ducha
   quadrada (a placa aprovada da Casa A), braço cromado até a parede da esquerda e canopla, na
   geometria do PDF.
5. DCE 1: o armário até o teto (o da linha diagonal) saiu quase branco; vira a madeira areia dos
   armários até o teto do Térreo, com o veio no comprido, sem a diagonal e sem sombra. A mancha
   clara do piso junto ao criado-mudo sai, como as do depósito.
6. Sauna: o braço do banco em L que o motor subiu junto ao vidro sai; ali volta o piso de Bege Bahia.
7. Sauna: o banco, que o motor fez em madeira, fica em Bege Bahia (pedido do usuário), em dois tons
   mais escuros, como na base: o degrau da frente (0,93) e o assento junto à parede (0,88), com as
   linhas do PDF (bordas e a linha dupla de cada nível, layer ARQ_ELEMENTOS FIXOS).
8. Ducha da antessala: o símbolo do CAD (quadrado, braço e a cruz branca sobre a parede) vira o
   chuveiro, com o braço saindo da parede de baixo; a parede volta ao preto.
9. Box do vestiário: o mesmo, com o braço saindo da parede da direita; o toco da cruz que passou
   para o vinílico da academia sai.
10. Vestiário: a cuba da bancada saiu só com o contorno cinza; vira uma cuba branca de verdade (aba,
    bacia com a borda mais escura indo ao fundo claro, válvula cromada), com a torneira cromada
    saindo da faixa junto à parede, na geometria do PDF (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS).
11. Esteiras: os letreiros que o motor escreveu nas lonas saem (sem texto na planta); fica a lona.
12. Pátio: a parede tracejada dupla de fora (à esquerda, embaixo e no alto), que o motor apagou ou
    cortou, volta: os traços do PDF (ARQ_PAREDE, fora da planta) desenhados no quadro comum.

Escala (pedido do usuário): a imagem final sai no quadro comum das bases (3840 x 2160, a folha 16:9
inteira, o mesmo das pranchas), com a planta exatamente sob a do Térreo; fora da planta, o fundo é
branco puro. Saídas: _retocado (quadro do render) e _final (quadro comum).

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/retoque_subsolo_casad.py POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_v1_render.webp \
      --saida POE642_CasaD/renders --nome POE642_CasaD_PH_Subsolo_v1_retocado
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))

from retoque_terreo_casac import CHUVEIRO_TETO, CROMO, CROMO_CLARO, CROMO_ESCURO, SS  # noqa: E402
from retoque_terreo_casab import LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO  # noqa: E402
from retoque_terreo_casad import interpolar, textura  # noqa: E402
from texturizar_base import quilting  # noqa: E402

BASE = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Subsolo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Subsolo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Subsolo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - SUBSOLO - CASA D.pdf"
CONFIG = RAIZ / "POE642_CasaD/config_bases.json"


def alinhar_base(render):
    """Base 16:9 reduzida ao tamanho do render e levada a ele por SIFT + afim (como no Térreo)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return A


def pdf_cadeia(A, forma_render):
    """Página do PDF e a conversão PDF -> render pela mesma cadeia da base (recorte, largura da base,
    tela 16:9, redução ao tamanho do render e o afim A)."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Subsolo"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sx, sy = forma_render[1] / wt, forma_render[0] / ht

    def p2r(x, y):
        bx, by = ((x - clip.x0) * zoom + (wt - wb) // 2) * sx, ((y - clip.y0) * zoom + (ht - hb) // 2) * sy
        return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]

    return pg, p2r


# trechos limpos do granito do depósito, entre as juntas do motor (px do render)
GRANITO = [(1110, 60, 1176, 220), (1192, 60, 1326, 220), (1192, 240, 1326, 380)]

FAIXA_DEPOSITO = {
    "ret": (1046, 42, 1132, 257),          # janela: a faixa e um trecho do granito à direita
    "faixa": (1049, 44, 1104, 256),        # a faixa areia, até a sombra da borda direita
    "lum_min": 45,                         # a parede (escura) não entra na luz nem muda
}

JUNTAS_DEPOSITO = {
    "ret": (1046, 42, 1398, 498),          # o depósito inteiro (até a parede da academia)
    "faixas": [(1180, 44, 1185, 497), (1332, 44, 1337, 497),        # juntas verticais (x 1182 e 1334)
               (1100, 226, 1396, 231), (1143, 387, 1373, 392)],     # horizontais (y 228 e 389)
    "manchas": [(1112, 252, 9, 8), (1092, 305, 9, 10), (1130, 305, 9, 9), (1204, 422, 9, 10)],
    "lum": (45, 200),                      # só o granito e as juntas mudam; a parede e os arcos ficam
    "folha": (1141, 479, 1199, 488),       # a folha da porta no fim da escada (com o contorno) não muda
}

BOX_WC = {
    "box": (711, 45, 809, 104),            # piso do box do WC DCE, acima da divisória cinza
    "ref": (712, 114, 808, 245),           # o granito do resto do banheiro
    "lum": (50, 130),                      # só o piso entra na conta (sem louças nem paredes)
}

# chuveiros na geometria do PDF (px do render), com a placa aprovada da Casa A, como no Térreo;
# a escala do render é ~2,73 x a do Térreo, então sombra e brilho crescem na mesma proporção
SOMBRA_CHUVEIRO = {"desloc": (-2.7, 2.7), "sigma": 2.2, "forca": 0.3}
CHUVEIRO_WC = {
    "nome": "WC DCE",
    "lum_max": 130,                                       # a luz vem só do granito, sem o branco do símbolo
                                                          # (nos pisos de Bege Bahia, 235: o piso tem ~215)
    "apagar": [(711, 67, 754, 92)],                       # o quadrado, o braço e o toco junto à parede
    "fontes": [(714, 48, 730, 66), (756, 48, 806, 100), (714, 93, 750, 103)],
    "parede": (699, 72, 711, 87),                         # o toco branco que entrou na parede
    "ducha": (733.4, 70.8, 750.2, 87.5),
    "braco": (709.6, 78.1, 741.8, 80.2),                  # do centro da ducha à face da parede
    "canopla": (709.6, 76.4, 711.4, 81.9),
    "janela": (698, 62, 760, 98),
}

# armário até o teto do DCE 1: a madeira areia dos armários do Térreo retocado (aprovado), ampliada
# na razão entre as escalas dos dois renders, que é o mesmo aspecto que ela tem na prancha
TERREO_RETOCADO = RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png"
ARMARIO_DCE = {
    "ret": (824, 45, 925, 90),             # o miolo; os contornos escuros da direita e de baixo ficam
    # (trecho do Térreo, giro em graus): o da direita da suíte 2 (veio em pé, girado) e o do DCE
    "fontes": [((1128, 740, 1143, 797), 90), ((1297, 332, 1324, 346), 0)],
    "escala": 2.73,
    "mancha": (921, 192, 9, 8),            # mancha clara no granito, acima do criado-mudo
    "janela_mancha": (906, 178, 945, 204),
    "fontes_piso": [(840, 110, 900, 180), (840, 200, 880, 240)],
}

# sauna (px do render, da geometria do PDF): o miolo é refeito inteiro em Bege Bahia tecido do pátio
# (o mesmo tom do piso da sauna no render), na luz do piso que já era Bege Bahia
SAUNA = {
    "miolo": (597, 889, 846, 1073),        # entre o caixilho do vidro, as paredes e a linha da porta
    "fontes": [(330, 430, 450, 620), (450, 430, 560, 620), (330, 640, 450, 830), (450, 640, 560, 830)],
    "luz": (660, 890, 845, 970),           # o piso que já era Bege Bahia
    "banco": (609.1, 973.3, 846.9, 1073.6),
    "degrau_ate": 1023.5,                  # o degrau da frente vai até aqui; daí para baixo, o assento
    "tons": (0.93, 0.88),
    # (pontos, escurecimento): bordas de cada nível e a linha dupla de dentro (ARQ_ELEMENTOS FIXOS)
    "linhas": [([(846.9, 973.3), (609.1, 973.3), (609.1, 1073.6)], 0.62),
               ([(609.1, 1023.5), (846.9, 1023.5)], 0.62),
               ([(846.9, 981.4), (618.3, 981.4), (618.3, 1073.7)], 0.78),
               ([(618.3, 1031.9), (846.9, 1031.9)], 0.78)],
    "largura": 1.2,
}

CHUVEIRO_DUCHA = {
    "nome": "ducha da antessala",
    "lum_min": 150,                                       # a luz só do Bege Bahia, sem a borda da parede
    "apagar": [(894, 1030, 918, 1073), (884, 1063, 928, 1073)],   # quadrado, braço e a cruz acima da parede
    "fontes": [(863, 1032, 890, 1070), (918, 1032, 945, 1070), (965, 990, 1045, 1065)],
    "parede": (884, 1073, 928, 1088),                     # a cruz branca pintada sobre a parede de baixo
    "ducha": (897.3, 1032.9, 914.1, 1049.6),
    "braco": (904.6, 1041.2, 906.7, 1073.0),
    "canopla": (902.9, 1071.3, 908.4, 1073.2),
    "janela": (888, 1026, 924, 1080),
}
CHUVEIRO_BOX = {
    "nome": "box do vestiário",
    "lum_min": 150,                                       # a luz só do Bege Bahia, sem a borda da parede
    "apagar": [(1278, 1009, 1322, 1048)],
    "fontes": [(1276, 992, 1318, 1010), (1240, 1048, 1318, 1072)],
    "parede": (1322, 1006, 1336, 1052),                   # a cruz (e o nicho) sobre a parede da direita
    "alem": [(1336, 1023, 1343, 1036)],                   # o toco da cruz no vinílico da academia
    "fontes_alem": [(1345, 985, 1440, 1065)],
    "ducha": (1281.7, 1021.5, 1298.5, 1038.2),
    "braco": (1290.1, 1028.8, 1322.0, 1030.9),
    "canopla": (1320.3, 1027.1, 1322.3, 1032.5),
    "janela": (1272, 1014, 1330, 1046),
}

CUBA_VEST = {
    "bacia": (1080.5, 989.6, 1106.8, 1044.6),   # a cuba retangular; à esquerda, a faixa da torneira
    "raio": 3.5, "aba": 2.6, "fundo": 5.0,       # canto, largura da aba e da borda da bacia até o fundo
    "valvula": (1093.65, 1017.1, 2.0),
    # torneira: sobre a bancada clara o cromado some (como no lavatório do Térreo): contorno escuro e
    # sombra curta (dx, dy, sigma, força)
    "base": ((1076.0, 1017.65), 2.6), "bica": (1076.0, 1089.5, 1017.65), "larg_bica": 2.6,
    "escuro": (92, 96, 100), "sombra": (1.6, 1.6, 2.0, 0.35),
    "janela": (1062, 982, 1114, 1052),
}

LETREIROS = {
    # (janela, caixa das letras): as letras são os px claros (> 100) da caixa, com 2 px de folga
    "lonas": [((1138, 780, 1183, 822), (1142, 788, 1153, 813)), ((1223, 777, 1268, 820), (1227, 785, 1238, 810))],
    "fontes": [(1150, 812, 1175, 836), (1238, 812, 1262, 836)],
    "lum": (60, 100),                      # a luz vem só da lona (sem os trilhos nem as letras)
}

QUADRO = {"largura": 3840, "altura": 2160, "ss": 2}
TRACEJADO = {
    "largura": 1.1, "cor": (62, 64, 66),   # o traço do tracejado que o motor manteve, na escala final
    # fora da planta (vis de 1800 px): à esquerda do pátio, abaixo dele e a faixa de cima do pátio
    "fora": lambda x, y: x < 160 or y > 944 or (639 < y < 649.5 and x < 275),
}


def apagar_largo(out, ret, mascara, fontes, sigma=4.0, borda=0.8, lum_min=None, lum_max=None, escuros=False):
    """Como o apagar do Térreo, para áreas largas: a luz do entorno (por canal) vem da convolução
    normalizada em várias escalas (interpolar), que cobre o miolo da máscara; com lum_min, a parede
    (escura) não entra na luz e não muda (com escuros=True, os traços escuros dentro da máscara, como o
    contorno de um símbolo, também mudam); com lum_max, peças claras (folhas de porta) não entram na luz."""
    x0, y0, x1, y1 = ret
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    claro = reg.mean(axis=2) > lum_min if lum_min is not None else np.ones((h, w), bool)
    m = cv2.GaussianBlur(mascara.astype(np.float32), (0, 0), borda) if borda else mascara.astype(np.float32)
    m = np.maximum(m, mascara.astype(np.float32))
    if not escuros:
        m *= claro
    amostra = ~mascara & claro
    if lum_max is not None:
        amostra &= reg.mean(axis=2) < lum_max
    luz = interpolar(reg, amostra, sigma)
    tex = textura(out, fontes, h, w)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - m[..., None]) + tex * luz * m[..., None], 0, 255).astype(np.uint8)
    return out


def faixa_deposito(out):
    q = FAIXA_DEPOSITO
    x0, y0, x1, y1 = q["ret"]
    fx0, fy0, fx1, fy1 = q["faixa"]
    m = np.zeros((y1 - y0, x1 - x0), bool)
    m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = True
    out = apagar_largo(out, q["ret"], m, GRANITO, sigma=4.0, borda=0.8, lum_min=q["lum_min"])
    print("    faixa areia do depósito fora; granito no lugar")
    return out


def juntas_deposito(out):
    q = JUNTAS_DEPOSITO
    x0, y0, x1, y1 = q["ret"]
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for fx0, fy0, fx1, fy1 in q["faixas"]:
        m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = 1
    for mx, my, mw, mh in q["manchas"]:
        cv2.ellipse(m, (mx + mw // 2 - x0, my + mh // 2 - y0), (mw // 2 + 3, mh // 2 + 3), 0, 0, 360, 1, -1)
    lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    m = m.astype(bool) & (lum > q["lum"][0]) & (lum < q["lum"][1])
    fx0, fy0, fx1, fy1 = q["folha"]
    m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = False
    out = apagar_largo(out, q["ret"], m, GRANITO, sigma=2.0, borda=0.6, lum_min=q["lum"][0], lum_max=110)
    print(f"    juntas e manchas do depósito fora: {int(m.sum())} px")
    return out


def piso_box_wc(out):
    q = BOX_WC
    reg = out.astype(np.float32)

    def mediana(r):
        x0, y0, x1, y1 = r
        p = reg[y0:y1, x0:x1].reshape(-1, 3)
        lum = p.mean(axis=1)
        return np.median(p[(lum > q["lum"][0]) & (lum < q["lum"][1])], axis=0)

    ganho = mediana(q["ref"]) / mediana(q["box"])
    x0, y0, x1, y1 = q["box"]
    b = reg[y0:y1, x0:x1]
    piso = (b.mean(axis=2) > 45)[..., None]
    out[y0:y1, x0:x1] = np.clip(np.where(piso, b * ganho, b), 0, 255).astype(np.uint8)
    print(f"    piso do box do WC DCE no tom do granito (ganho BGR {np.round(ganho, 3)})")
    return out


def desenhar_chuveiro(out, d, sombra=SOMBRA_CHUVEIRO):
    """Chuveiro visto de cima, como o do WC DCE do Térreo: sombra curta, ducha quadrada (a placa da
    Casa A), braço cromado (horizontal ou vertical, um retângulo do PDF) do centro da ducha à face da
    parede, com o brilho no eixo, e a canopla na parede."""
    wx0, wy0, wx1, wy1 = d["janela"]
    h, w = wy1 - wy0, wx1 - wx0
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def ret_ss(r):
        return (int(round((r[0] - wx0) * SS)), int(round((r[1] - wy0) * SS)),
                int(round((r[2] - wx0) * SS)), int(round((r[3] - wy0) * SS)))

    def pintar(mascara, cor):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    dx0, dy0, dx1, dy1 = ret_ss(d["ducha"])
    ducha = np.zeros((h * SS, w * SS), np.uint8)
    cv2.rectangle(ducha, (dx0, dy0), (dx1, dy1), 255, -1)
    M = np.float32([[1, 0, sombra["desloc"][0] * SS], [0, 1, sombra["desloc"][1] * SS]])
    sb = cv2.GaussianBlur(cv2.warpAffine(ducha.astype(np.float32), M, (w * SS, h * SS)), (0, 0), sombra["sigma"] * SS) / 255
    reg *= (1 - sombra["forca"] * cv2.resize(sb, (w, h), interpolation=cv2.INTER_AREA))[..., None]
    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    placa = cv2.resize(img[hy0:hy1, hx0:hx1], (dx1 - dx0, dy1 - dy0), interpolation=cv2.INTER_CUBIC)
    cor = np.zeros((h * SS, w * SS, 3), np.uint8)
    cor[dy0:dy1, dx0:dx1] = placa
    a = cv2.resize(ducha.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    c = cv2.resize(cor.astype(np.float32) * (ducha[..., None] / 255), (w, h), interpolation=cv2.INTER_AREA) / np.maximum(a, 1e-6)
    reg = reg * (1 - a) + c * a
    bx0, by0, bx1, by1 = ret_ss(d["braco"])
    braco = np.zeros_like(ducha)
    cv2.rectangle(braco, (bx0, by0), (bx1, by1), 255, -1)
    brilho = np.zeros_like(ducha)
    if bx1 - bx0 >= by1 - by0:                       # braço horizontal: brilho ao longo de x
        yc = (by0 + by1) // 2 - SS // 4
        cv2.line(brilho, (bx0, yc), (bx1, yc), 255, max(1, SS // 2))
    else:
        xc = (bx0 + bx1) // 2 - SS // 4
        cv2.line(brilho, (xc, by0), (xc, by1), 255, max(1, SS // 2))
    pintar(braco, CROMO_ESCURO)
    pintar(brilho, CROMO_CLARO)
    cx0, cy0, cx1, cy1 = ret_ss(d["canopla"])
    canopla = np.zeros_like(ducha)
    cv2.rectangle(canopla, (cx0, cy0), (cx1, cy1), 255, -1)
    pintar(canopla, CROMO)
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    return out


def trocar_chuveiro(out, q):
    """O símbolo do CAD sai (piso tecido do próprio ambiente, na luz do entorno), a parede volta ao
    preto onde o símbolo entrou nela, e entra o chuveiro desenhado."""
    pad = 8                                          # margem de piso em volta: a luz vem dela
    for x0, y0, x1, y1 in q["apagar"]:
        m = np.zeros((y1 - y0 + 2 * pad, x1 - x0 + 2 * pad), bool)
        m[pad:-pad, pad:-pad] = True
        out = apagar_largo(out, (x0 - pad, y0 - pad, x1 + pad, y1 + pad), m, q["fontes"], sigma=2.0, borda=0.0,
                           lum_min=q.get("lum_min", 45), lum_max=q.get("lum_max", 235), escuros=True)
    if q.get("parede"):
        # a parede volta ao preto onde o símbolo entrou nela, no preto do miolo da própria parede em
        # volta (praticamente 0, desvio < 1): o retalho inteiro, sem fantasma do contorno da cruz
        x0, y0, x1, y1 = q["parede"]
        e = 12
        viz = out[y0 - e:y1 + e, x0 - e:x1 + e].reshape(-1, 3)
        dentro = np.zeros((y1 - y0 + 2 * e, x1 - x0 + 2 * e), bool)
        dentro[e:-e, e:-e] = True
        miolo = viz[(viz.astype(np.float32).mean(axis=1) <= 5) & ~dentro.ravel()]
        out[y0:y1, x0:x1] = np.median(miolo, axis=0).astype(np.uint8)
    for x0, y0, x1, y1 in q.get("alem", []):
        m = np.zeros((y1 - y0 + 2 * pad, x1 - x0 + 2 * pad), bool)
        m[pad:-pad, pad:-pad] = True
        out = apagar_largo(out, (x0 - pad, y0 - pad, x1 + pad, y1 + pad), m, q["fontes_alem"], sigma=2.0,
                           borda=0.0, lum_min=45, lum_max=200, escuros=True)
    out = desenhar_chuveiro(out, q)
    print(f"    {q['nome']}: símbolo do CAD fora; ducha, braço e canopla do PDF")
    return out


def armario_dce(out):
    q = ARMARIO_DCE
    img = cv2.imread(str(TERREO_RETOCADO))
    fontes = []
    for (x0, y0, x1, y1), giro in q["fontes"]:
        t = img[y0:y1, x0:x1]
        if giro:
            t = np.rot90(t)
        t = cv2.resize(t, None, fx=q["escala"], fy=q["escala"], interpolation=cv2.INTER_CUBIC).astype(np.float32)
        fontes += [np.ascontiguousarray(v) for v in (t, t[:, ::-1], t[::-1, :], t[::-1, ::-1])]
    x0, y0, x1, y1 = q["ret"]
    tex = quilting(fontes, y1 - y0, x1 - x0, p=24, sobra=8, candidatos=600)[:y1 - y0, :x1 - x0]
    out[y0:y1, x0:x1] = np.clip(tex, 0, 255).astype(np.uint8)
    jx0, jy0, jx1, jy1 = q["janela_mancha"]
    mx, my, mw, mh = q["mancha"]
    m = np.zeros((jy1 - jy0, jx1 - jx0), np.uint8)
    cv2.ellipse(m, (mx + mw // 2 - jx0, my + mh // 2 - jy0), (mw // 2 + 3, mh // 2 + 3), 0, 0, 360, 1, -1)
    out = apagar_largo(out, q["janela_mancha"], m.astype(bool), q["fontes_piso"], sigma=2.0, borda=0.6,
                       lum_min=45, lum_max=110)
    print("    armário até o teto do DCE 1 em madeira areia, sem a diagonal; mancha do piso fora")
    return out


def sauna(out):
    q = SAUNA
    x0, y0, x1, y1 = q["miolo"]
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    amostra = np.zeros((h, w), bool)
    lx0, ly0, lx1, ly1 = q["luz"]
    amostra[ly0 - y0:ly1 - y0, lx0 - x0:lx1 - x0] = reg[ly0 - y0:ly1 - y0, lx0 - x0:lx1 - x0].mean(axis=2) > 170
    luz = interpolar(reg, amostra, 6.0)
    novo = textura(out, q["fontes"], h, w, p=24) * luz
    bx0, by0, bx1, by1 = q["banco"]
    yy, xx = np.mgrid[y0:y1, x0:x1] + 0.5
    no_banco = (xx >= bx0) & (xx <= bx1) & (yy >= by0)
    novo[no_banco & (yy < q["degrau_ate"])] *= q["tons"][0]
    novo[no_banco & (yy >= q["degrau_ate"])] *= q["tons"][1]
    for pts, k in q["linhas"]:
        m = np.zeros((h * SS, w * SS), np.uint8)
        p = np.int32([[round((px - x0) * SS), round((py - y0) * SS)] for px, py in pts])
        cv2.polylines(m, [p], False, 255, max(1, int(round(q["largura"] * SS))), cv2.LINE_AA)
        a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        novo = novo * (1 - a) + novo * k * a
    out[y0:y1, x0:x1] = np.clip(novo, 0, 255).astype(np.uint8)
    print("    sauna: braço do L fora; banco em Bege Bahia em dois tons, com as linhas do PDF")
    return out


def cuba_vestiario(out):
    q = CUBA_VEST
    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def px(v, o=0.0):
        return int(round((v - o) * SS))

    def pintar(mascara, cor, forca=1.0):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None] * forca
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    def ret_arred(b, raio):
        m = np.zeros((h * SS, w * SS), np.uint8)
        bx0, by0, bx1, by1 = px(b[0], wx0), px(b[1], wy0), px(b[2], wx0), px(b[3], wy0)
        rr = min(px(raio), (bx1 - bx0) // 2, (by1 - by0) // 2)
        cv2.rectangle(m, (bx0 + rr, by0), (bx1 - rr, by1), 255, -1)
        cv2.rectangle(m, (bx0, by0 + rr), (bx1, by1 - rr), 255, -1)
        for cx, cy in ((bx0 + rr, by0 + rr), (bx1 - rr, by0 + rr), (bx0 + rr, by1 - rr), (bx1 - rr, by1 - rr)):
            cv2.circle(m, (cx, cy), rr, 255, -1)
        return m

    def circulo(cx, cy, r):
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.circle(m, (px(cx, wx0), px(cy, wy0)), max(1, px(r)), 255, -1)
        return m

    bx0, by0, bx1, by1 = q["bacia"]
    pintar(ret_arred(q["bacia"], q["raio"]), LOUCA_CONTORNO)
    pintar(ret_arred((bx0 + 0.9, by0 + 0.9, bx1 - 0.9, by1 - 0.9), q["raio"] - 0.9), LOUCA)
    passos = 8
    for i in range(passos):                       # bacia: a borda mais escura indo ao fundo claro
        k = i / (passos - 1)
        cor = tuple(BACIA_BORDA[c] * (1 - k) + BACIA_FUNDO[c] * k for c in range(3))
        ins = q["aba"] + k * q["fundo"]
        pintar(ret_arred((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(1.0, q["raio"] - k * 2)), cor)
    vx, vy, vr = q["valvula"]
    pintar(circulo(vx, vy, vr), CROMO_ESCURO)
    pintar(circulo(vx, vy, vr * 0.7), CROMO_CLARO)
    tx0, tx1, ty = q["bica"]
    (ox, oy), r = q["base"]
    sdx, sdy, ssig, sforca = q["sombra"]
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.line(m, (px(tx0 + sdx, wx0), px(ty + sdy, wy0)), (px(tx1 + sdx, wx0), px(ty + sdy, wy0)), 255, px(q["larg_bica"]))
    cv2.circle(m, (px(ox + sdx, wx0), px(oy + sdy, wy0)), px(r), 255, -1)
    sb = cv2.resize(cv2.GaussianBlur(m.astype(np.float32), (0, 0), ssig * SS) / 255, (w, h), interpolation=cv2.INTER_AREA)
    reg *= (1 - sforca * sb)[..., None]
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.line(m, (px(tx0, wx0), px(ty, wy0)), (px(tx1, wx0), px(ty, wy0)), 255, px(q["larg_bica"]))
    pintar(m, q["escuro"])
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.line(m, (px(tx0, wx0), px(ty, wy0)), (px(tx1 - 0.6, wx0), px(ty, wy0)), 255, px(q["larg_bica"] - 1.0))
    pintar(m, CROMO)
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.line(m, (px(tx0, wx0), px(ty - 0.4, wy0)), (px(tx1 - 0.8, wx0), px(ty - 0.4, wy0)), 255, max(1, px(0.5)))
    pintar(m, CROMO_CLARO)
    pintar(circulo(ox, oy, r), q["escuro"])
    pintar(circulo(ox, oy, r - 0.6), CROMO)
    pintar(circulo(ox - 0.4, oy - 0.4, r * 0.45), CROMO_CLARO)
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    vestiário: cuba branca com válvula e torneira cromada, na geometria do PDF")
    return out


def letreiros(out):
    q = LETREIROS
    total = 0
    for janela, caixa in q["lonas"]:
        x0, y0, x1, y1 = janela
        cx0, cy0, cx1, cy1 = caixa
        lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        m[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] = (lum[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] > q["lum"][1])
        m = cv2.dilate(m, np.ones((5, 5), np.uint8)).astype(bool)
        m[:cy0 - y0] = False
        m[cy1 - y0:] = False
        m[:, :cx0 - x0] = False
        m[:, cx1 - x0:] = False
        total += int(m.sum())
        out = apagar_largo(out, janela, m, q["fontes"], sigma=2.0, borda=0.6, lum_min=q["lum"][0],
                           lum_max=q["lum"][1], escuros=True)
    print(f"    letreiros das esteiras fora: {total} px")
    return out


def no_quadro(out, A):
    """O render retocado vai para o quadro comum (a base 16:9 na largura das pranchas) pelo inverso da
    cadeia base -> render (a base reduzida ao tamanho do render, não uniforme, e o afim A), com 2 x
    de superamostragem; fora da planta (a mancha da base chapada, com folga), o fundo fica branco."""
    q = QUADRO
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sxr, syr = out.shape[1] / wt, out.shape[0] / ht
    WF, HF, s = q["largura"], q["altura"], q["ss"]
    sxf, syf = WF * s / wt, HF * s / ht
    D = np.float64([[sxr / sxf, 0, 0], [0, syr / syf, 0], [0, 0, 1]])
    M = (np.vstack([A, [0, 0, 1]]) @ D)[:2]                    # quadro (2 x) -> render
    grande = cv2.warpAffine(out, M, (WF * s, HF * s), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP,
                            borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    final = cv2.resize(grande, (WF, HF), interpolation=cv2.INTER_AREA)
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), (WF, HF), interpolation=cv2.INTER_NEAREST)
    nb = (chapada.min(axis=2) < 245).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb)
    planta = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 5000])
    planta = cv2.dilate(planta.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    final[~planta] = 255
    print(f"    quadro comum {WF} x {HF}: planta da base com folga de 3 px; fundo branco fora dela")
    return final


def tracejado(final):
    """Traços do tracejado de fora (ARQ_PAREDE) do PDF, direto no quadro comum (sem o afim do render)."""
    q = TRACEJADO
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Subsolo"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    HF, WF = final.shape[:2]
    kv = clip.width / cfg["largura_visualizacao"]

    def vis(p):
        return (p.x - clip.x0) / kv, (p.y - clip.y0) / kv

    def quadro(p):
        return [int(round(((p.x - clip.x0) * zoom + (wt - wb) // 2) * WF / wt * SS)),
                int(round(((p.y - clip.y0) * zoom + (ht - hb) // 2) * HF / ht * SS))]

    m = np.zeros((HF * SS, WF * SS), np.uint8)
    n = 0
    for d in pg.get_drawings():
        if d.get("layer") != "ARQ_PAREDE" or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] == "l" and q["fora"](*vis(it[1])) and q["fora"](*vis(it[2])):
                cv2.line(m, quadro(it[1]), quadro(it[2]), 255, max(1, int(round(q["largura"] * SS))), cv2.LINE_AA)
                n += 1
    a = cv2.resize(m.astype(np.float32) / 255, (WF, HF), interpolation=cv2.INTER_AREA)[..., None]
    final[:] = np.clip(final * (1 - a) + np.array(q["cor"], np.float32) * a, 0, 255).astype(np.uint8)
    print(f"    tracejado de fora do pátio: {n} traços do PDF")
    return final


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] depósito: faixa areia inventada")
    out = faixa_deposito(out)
    print("[2] depósito: juntas gigantes e manchas claras")
    out = juntas_deposito(out)
    print("[3] WC DCE: piso do box no tom do granito")
    out = piso_box_wc(out)
    print("[4] WC DCE: chuveiro")
    out = trocar_chuveiro(out, CHUVEIRO_WC)
    print("[5] DCE 1: armário até o teto")
    out = armario_dce(out)
    print("[6, 7] sauna: braço do banco em L e banco em Bege Bahia")
    out = sauna(out)
    print("[8] ducha da antessala: chuveiro")
    out = trocar_chuveiro(out, CHUVEIRO_DUCHA)
    print("[9] box do vestiário: chuveiro")
    out = trocar_chuveiro(out, CHUVEIRO_BOX)
    print("[10] vestiário: cuba da bancada")
    out = cuba_vestiario(out)
    print("[11] esteiras: letreiros nas lonas")
    out = letreiros(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")

    print("[escala] quadro comum das bases, com a planta sob a do Térreo")
    final = no_quadro(out, alinhar_base(orig))
    print("[12] pátio: tracejado de fora")
    final = tracejado(final)
    nome_final = args.nome.replace("_retocado", "") + "_final"
    cv2.imwrite(str(args.saida / f"{nome_final}.png"), final)
    print(f"[fim] {args.saida / (nome_final + '.png')}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Retoque sem IA do render do Térreo da Casa D (prompt v1). A imagem final é o render.

Os itens são corrigidos um a um, na ordem pedida pelo usuário.

1. Porta pivotante principal (entre o hall de entrada e o estar): o motor cortou a folha no
   alinhamento da parede; no PDF ela vai de ponta a ponta, passando para o lado do hall até o arco
   pequeno. A folha é estendida com o próprio trecho dela (mesmas linhas) até o fim do PDF, onde o
   arco pequeno do render já começa. Mesmo caso da Casa C.
2. Chuveiros do banho master: o motor ligou os dois chuveiros numa barra de parede a parede. No PDF
   (ARQ_LOUÇAS E METAIS) são duas duchas quadradas de ~19 cm, cada uma num braço que sai da parede
   lateral (a da esquerda e a da direita). A barra sai, com o texto ilegível que o motor pôs junto à
   parede de baixo (as linhas viram o piso limpo de cima, em espelho, que já tem a sombra da parede
   da direita), e entram as duchas na placa aprovada da Casa A
   reduzida, com sombra curta, o braço cromado da parede até o centro da ducha e a canopla na parede.
3. Armários até o teto (no PDF, os retângulos com diagonal da layer DOC_LINHAS E PROJEÇÕES): 16
   retângulos (closet do master, suítes 1 e 2, circulação, cozinha, serviço, DCE e gourmet). O
   motor os fez como móveis de meia altura, com sombra projetada no piso. A sombra sai: em cada face
   livre que dá para piso, o escurecimento é medido (mediana ao longo da face, por canal, até o
   patamar do piso), ajustado por um modelo suave (o tom de cada régua do vinílico fica) e refinado
   ponto a ponto ao longo da face (penumbra nas pontas); onde duas sombras se encontram (cantos
   internos) vale a mais escura, sem somar; a borda da face repete a linha seguinte já limpa. O
   tampo fica no tom areia dos armários da Casa C, com o veio do próprio armário do render (pedido
   do usuário: só o tom muda; o sombreado de caixa das bordas sai); onde o motor fez caixa lisa,
   quartzo ou caixa branca, o veio vem do armário da direita da suíte 2. Contorno fino nas faces
   livres. Embaixo dos dois armários junto a uma bancada (canto de cima da cozinha e o vizinho ao
   gás), a sombra é funda e emenda na da bancada: o piso é refeito em granito tecido dos trechos
   limpos, com a borda da sombra da bancada em diagonal (luz de cima à direita) e, na cozinha, a
   sombra da parede da direita continuando.
4. Área molhada da bancada da pia da cozinha: o retângulo da layer ARQ_BANCADAS em volta das cubas
   é demarcado em traço cinza fino, como na Casa C, nos lados livres (esquerda e embaixo; em cima é
   a parede e à direita, o armário do canto).
5. Eletrodomésticos da cozinha: os dois volumes ao lado do armário do canto (no PDF, sem diagonal)
   ficam em inox; a caixa do render fica (sombreado, borda das portas, divisória e sombra) e só o tom
   muda, para aço escovado levemente frio, com riscos verticais sutis. O do canto é armário (areia).
6. Porta de correr do abrigo de gás: o motor fez uma soleira cinza larga no vão de cima. As linhas
   dela viram o piso do abrigo (as de baixo, em espelho) e entra a porta do PDF (ARQ_PAREDE): duas
   folhas em planos diferentes na espessura da parede (a da esquerda por fora, a da direita por
   dentro), com montantes e batentes, em 8x, e a sombra curta da folha de dentro.
7. Carros: o motor fez os três em prata; cada um ganha um tom (pedido do usuário): grafite, branco
   perolado e azul-marinho. Na silhueta de cada carro (o que não é o granito quente do piso, mais a
   borda misturada), uma curva de tom leva a luminância do prata à da tinta, mantendo a ordem do
   render (vidros mais escuros que a lataria, reflexos); a cor entra só nos tons médios e claros e
   as lanternas ficam.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_terreo_casad.py RENDER.webp --saida PASTA --nome NOME
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
from retoque_terreo_casac import COZINHA as COZINHA_C  # noqa: E402
from texturizar_base import quilting  # noqa: E402

BASE = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - TÉRREO - CASA D.pdf"
CONFIG = RAIZ / "POE642_CasaD/config_bases.json"

# porta pivotante principal: linhas da folha, trecho da folha copiado e a parte que faltou (até o
# fim da folha no PDF, onde o arco pequeno do render começa)
PIVOTANTE = {"linhas": (567, 571), "fonte_x": 1240, "de": 1267, "ate": 1282}
# chuveiros do banho master: a barra do motor (com os registros, a sombra e o texto ilegível que o
# motor escreveu junto à parede de baixo), refeita com as linhas limpas de cima (em espelho); duchas,
# braços e canoplas do PDF (ARQ_LOUÇAS E METAIS, em px do render)
CHUVEIROS_BHM = {
    "barra": (403, 882, 458, 902),
    "emenda": 0,
    "duchas": [
        {"nome": "esquerda", "ducha": (411.9, 886.1, 418.0, 892.3), "braco": (403.0, 415.0, 889.2),
         "canopla": (403.0, 888.2, 404.0, 890.2)},
        {"nome": "direita", "ducha": (442.7, 886.2, 448.8, 892.4), "braco": (445.7, 457.7, 889.3),
         "canopla": (456.7, 888.3, 457.7, 890.3)},
    ],
    "larg_braco": 0.8,
    "sombra": {"desloc": (-1.0, 1.0), "sigma": 0.8, "forca": 0.3},
}

# armários até o teto: no PDF, os retângulos com uma diagonal (layer DOC_LINHAS E PROJEÇÕES, traço
# 0,57). Retângulo de cada um em px do render (a diagonal levada pela cadeia da base).
ARMARIOS = [
    ("closet do master, braço de cima", (267.8, 810.1, 351.8, 828.7)),
    ("closet do master, braço da esquerda", (267.7, 828.7, 286.4, 903.3)),
    ("closet do master, braço de baixo", (286.4, 884.7, 395.2, 903.3)),
    ("circulação, à direita do banho master", (497.8, 862.9, 516.6, 903.3)),
    ("à esquerda do banho 1", (544.5, 810.1, 563.3, 903.3)),
    ("suíte 1, braço em pé", (568.0, 737.0, 586.6, 799.2)),
    ("suíte 1, braço deitado", (586.7, 737.0, 624.0, 755.7)),
    ("suíte 2, braço deitado", (1065.6, 737.0, 1121.7, 755.6)),
    ("suíte 2, braço em pé", (1103.0, 755.6, 1121.6, 799.2)),
    ("suíte 2, à direita", (1126.2, 737.0, 1145.0, 799.2)),
    ("cozinha, canto de baixo", (945.3, 319.5, 970.2, 344.4)),
    ("cozinha, canto de cima", (1062.7, 189.9, 1089.7, 210.1)),          # o motor fez quartzo
    ("serviço, junto ao WC DCE", (1198.5, 266.0, 1238.9, 286.2)),
    ("serviço, vizinho ao gás", (1280.9, 189.9, 1330.8, 211.6)),
    ("DCE, embaixo", (1294.8, 329.8, 1325.9, 348.4)),
    ("gourmet", (787.7, 224.1, 808.2, 239.6)),                          # o motor fez caixa branca
]
ARMARIO = {
    # areia: o tom do painel laqueado da Casa C (o dos armários da cozinha de lá, aprovado). O veio
    # é o do próprio armário do render (pedido do usuário): só o tom muda
    "fonte_areia": (RAIZ / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_retocado.png", COZINHA_C["fonte_areia"]),
    # veio: a luminância do armário sobre ela mesma desfocada; o limite tira o sombreado de caixa
    # que o motor fez nas bordas (lia como móvel baixo) e deixa o veio, que é sutil
    "sigma_veio": 3.0, "veio_lim": (0.92, 1.08),
    # px a mais embaixo, onde o render ainda tem a borda clara (da bancada ou da caixa do motor)
    "ajuste": {"cozinha, canto de cima": (0, 0, 0, 1), "serviço, vizinho ao gás": (0, 0, 0, 1)},
    # onde o motor não fez armário de madeira (caixa lisa com sombreado de móvel baixo, quartzo ou
    # caixa branca), o veio vem de outro armário do render (o da direita da suíte 2, alto: o veio
    # é vertical, como em todos os armários do render, e só se repete na largura, em espelho)
    "veio_emprestado": (1128, 740, 1143, 797),
    "sem_veio": ["cozinha, canto de baixo", "cozinha, canto de cima", "serviço, junto ao WC DCE",
                 "serviço, vizinho ao gás", "gourmet"],
    # faces junto a uma bancada: a sombra embaixo do armário é funda e emenda na da bancada; o
    # granito granulado não aguenta ser clareado tanto. O piso é refeito (ver PISO_SOB_ARMARIO)
    "manter_piso": [("cozinha, canto de cima", "baixo"), ("serviço, vizinho ao gás", "baixo")],
    "contorno": COZINHA_C["contorno"],
    # sombra que o motor projetou no piso: faixa medida a partir de cada face livre (até D px); a
    # referência é o patamar do piso logo depois da sombra
    "faixa": 22, "limiar": 0.97, "alem": 6, "suave": 2,
}

# piso refeito embaixo dos armários que encostam numa bancada: faixa de H linhas abaixo do armário,
# em granito tecido (image quilting) dos trechos limpos; a borda da sombra da bancada fica em
# diagonal (a luz vem de cima à direita), com penumbra curta; a sombra da parede da direita (medida
# logo abaixo da faixa, coluna a coluna) continua; trechos protegidos (a folha da porta) ficam
PISO_SOB_ARMARIO = {
    "fontes": [(1240, 240, 1290, 262), (1000, 300, 1060, 318)],
    # (armário, linhas, sombra da parede ao lado continua, trechos protegidos)
    "faixas": [("cozinha, canto de cima", 20, True, []),
               ("serviço, vizinho ao gás", 26, False, [(1303, 219, 1331, 222), (1329, 215, 1336, 220)])],
    "penumbra": 3.0, "emenda": 6, "medida": 16,
}

# área molhada da bancada da pia da cozinha (PDF, ARQ_BANCADAS): traço cinza fino, como na Casa C,
# nos lados livres (a esquerda e embaixo; em cima é a parede e à direita, o armário do canto)
AREA_MOLHADA = {
    "pontos": [(975.7, 190.5), (975.7, 209.5), (1062.1, 209.5)],
    "traco": COZINHA_C["traco"], "larg_traco": COZINHA_C["larg_traco"], "forca_traco": COZINHA_C["forca_traco"],
}

# eletrodomésticos da cozinha (os dois volumes do PDF, ao lado do armário do canto): em inox. A caixa
# do render fica (sombreado, borda das portas, divisória e sombra); só o tom muda, com escovado sutil
INOX = {
    "janela": (971, 317, 1024, 346),
    "cor": (186, 184, 181),                     # BGR: aço escovado, levemente frio
    "lum": (70.0, 150.0),                       # luminância: granito (0) .. caixa (1), nas bordas
    "escovado": 0.025, "semente": 642,
}

# porta de correr do abrigo de gás (PDF, ARQ_PAREDE, em px do render): duas folhas em planos
# diferentes na espessura da parede de cima (a da esquerda por fora, a da direita por dentro), com
# os montantes nas pontas e os batentes. O motor fez uma soleira cinza larga: as linhas dela viram o
# piso do abrigo (as de baixo, em espelho), com a sombra curta das folhas
PORTA_GAS = {
    "soleira": (1335, 185, 1370, 193),
    "folhas": [(1336.7, 185.2, 1352.5, 186.5), (1352.5, 186.5, 1368.4, 187.7)],
    "montantes": [(1336.7, 1338.2), (1351.0, 1352.5), (1352.5, 1354.1), (1366.9, 1368.4)],
    "batentes": [(1335.4, 185.2, 1336.7, 186.8), (1368.4, 185.2, 1369.7, 186.8)],
    "janela": (1332, 182, 1373, 196),
    "folha": (196, 199, 202), "montante": (150, 154, 158), "contorno": (85, 92, 98), "larg_contorno": 0.3,
    "sombra": (0.80, 0.90, 0.96),                # linhas logo abaixo da folha de dentro
}

# carros da garagem: o motor fez os três em prata. Cada um ganha um tom (pedido do usuário). Na
# silhueta do carro (o que não é o granito quente do piso), uma curva de tom leva a luminância do
# prata à da tinta, mantendo a ordem do render (vidros mais escuros que a lataria, reflexos); a cor
# entra só nos tons médios e claros (o vidro escuro fica neutro)
CARROS = {
    # (nome, caixa, curva: ("escurecer", base, faixa, expoente) ou ("clarear", ini, fim, força), cor BGR)
    "carros": [("esquerda", (1388, 246, 1458, 398), ("escurecer", 26.0, 74.0, 1.6), (1.02, 1.0, 0.98)),   # grafite
               ("meio", (1475, 243, 1542, 391), ("clarear", 130.0, 195.0, 0.55), (0.99, 1.0, 1.01)),     # branco perolado
               ("direita", (1557, 236, 1633, 407), ("escurecer", 18.0, 52.0, 1.4), (1.34, 0.96, 0.74))],  # azul-marinho
    "quente": 16, "lum_min": 90.0, "claro": 125.0, "fecho": 9, "reflexo": 0.6, "cor_lum": (70.0, 140.0),
    "lanterna": (40, 120),                      # R - B e R mínimos: lanternas e faróis âmbar ficam
}

def alinhar_base(render):
    """Base 16:9 reduzida e levada ao render por SIFT + afim; também a base chapada (v2)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), render.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    return (cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255)),
            cv2.warpAffine(chapada, A, render.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255)),
            A)


def pdf_cadeia(A, forma_render):
    """Página do PDF e a conversão PDF -> render pela mesma cadeia da base (recorte, largura da
    base, tela 16:9, redução ao tamanho do render e o afim A)."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Terreo"]["pagina"]]
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


def pivotante(out):
    q = PIVOTANTE
    y0, y1 = q["linhas"]
    de, ate, fx = q["de"], q["ate"], q["fonte_x"]
    out[y0:y1, de:ate] = out[y0:y1, fx:fx + ate - de]
    print(f"    porta pivotante: folha estendida até o fim do PDF (x {ate})")
    return out


def chuveiros_bhm(out):
    q = CHUVEIROS_BHM
    x0, y0, x1, y1 = q["barra"]
    n = y1 - y0
    out[y0:y1, x0:x1] = out[y0 - n:y0, x0:x1][::-1]          # piso limpo de cima, em espelho
    e = q["emenda"]
    for k in range(e):                                        # emenda suave embaixo
        t = (k + 1) / (e + 1)
        y = y1 - e + k
        out[y, x0:x1] = np.clip(out[y, x0:x1] * (1 - t) + out[y1 + k, x0:x1] * t, 0, 255).astype(np.uint8)

    wx0, wy0, wx1, wy1 = x0, y0, x1, y1
    h, w = wy1 - wy0, wx1 - wx0

    def px(v, o=0.0):
        return int(round((v - o) * SS))

    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def pintar(mascara, cor):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    s = q["sombra"]
    for d in q["duchas"]:
        dx0, dy0, dx1, dy1 = d["ducha"]
        ducha = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(ducha, (px(dx0, wx0), px(dy0, wy0)), (px(dx1, wx0), px(dy1, wy0)), 255, -1)
        M = np.float32([[1, 0, s["desloc"][0] * SS], [0, 1, s["desloc"][1] * SS]])
        sombra = cv2.GaussianBlur(cv2.warpAffine(ducha.astype(np.float32), M, (w * SS, h * SS)), (0, 0),
                                  s["sigma"] * SS) / 255
        reg *= (1 - s["forca"] * cv2.resize(sombra, (w, h), interpolation=cv2.INTER_AREA))[..., None]

        placa = cv2.resize(img[hy0:hy1, hx0:hx1], (px(dx1 - dx0), px(dy1 - dy0)), interpolation=cv2.INTER_CUBIC)
        cor = np.zeros((h * SS, w * SS, 3), np.uint8)
        cor[px(dy0, wy0):px(dy0, wy0) + placa.shape[0], px(dx0, wx0):px(dx0, wx0) + placa.shape[1]] = placa
        a = cv2.resize(ducha.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        c = cv2.resize(cor.astype(np.float32) * (ducha[..., None] / 255), (w, h), interpolation=cv2.INTER_AREA)
        c = c / np.maximum(a, 1e-6)
        reg = reg * (1 - a) + c * a

        bx0, bx1, by = d["braco"]                             # braço por cima da ducha, até o centro
        braco = np.zeros_like(ducha)
        cv2.line(braco, (px(bx0, wx0), px(by, wy0)), (px(bx1, wx0), px(by, wy0)), 255, px(q["larg_braco"]))
        brilho = np.zeros_like(ducha)
        cv2.line(brilho, (px(bx0, wx0), px(by - 0.1, wy0)), (px(bx1, wx0), px(by - 0.1, wy0)), 255, max(1, px(0.3)))
        pintar(braco, CROMO_ESCURO)
        pintar(brilho, CROMO_CLARO)
        cx0, cy0, cx1, cy1 = d["canopla"]
        canopla = np.zeros_like(ducha)
        cv2.rectangle(canopla, (px(cx0, wx0), px(cy0, wy0)), (px(cx1, wx0), px(cy1, wy0)), 255, -1)
        pintar(canopla, CROMO)
        print(f"    banho master, chuveiro da {d['nome']}: ducha, braço da parede e canopla do PDF")
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    return out


def eh_parede(px):
    return (px.max(axis=-1) <= 45) & ((px.max(axis=-1).astype(int) - px.min(axis=-1)) <= 8)


def parede_grossa(chapada):
    """Paredes da base chapada sem os traços finos (bordas e diagonais dos armários, linhas do PDF)."""
    return cv2.morphologyEx(eh_parede(chapada).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0


def modelo_sombra(r):
    """Sombra suave e crescente em d (1 = sem sombra), ajustada à razão medida r(d), d >= 1:
    s(d) = 1 - A * max(0, 1 - (d - 1) / L) ** p. O tom de cada régua do piso não entra no modelo
    e fica na imagem."""
    d = np.arange(1, len(r), dtype=np.float32)
    A = np.arange(0.0, 0.81, 0.01)[:, None, None, None]
    L = np.arange(1.0, len(r) + 0.1, 0.5)[None, :, None, None]
    P = np.array([0.6, 0.8, 1.0, 1.3, 1.7, 2.2, 3.0])[None, None, :, None]
    s = 1 - A * np.clip(1 - (d - 1) / L, 0, 1) ** P
    e = ((s - r[1:]) ** 2).sum(axis=-1)
    i = np.unravel_index(np.argmin(e), e.shape)
    return np.concatenate([[1.0], s[i]])


def armarios(out, chapada):
    """Armários até o teto: tampo em areia, sem sombra no piso; contorno nas faces livres."""
    q = ARMARIO
    img = cv2.imread(str(q["fonte_areia"][0]))
    fx0, fy0, fx1, fy1 = q["fonte_areia"][1]
    t = img[fy0:fy1, fx0:fx1]
    retangulos = [tuple(int(round(v)) + d for v, d in zip(r, q["ajuste"].get(nome, (0, 0, 0, 0))))
                  for nome, r in ARMARIOS]
    ocupado = np.zeros(out.shape[:2], bool)
    for x0, y0, x1, y1 in retangulos:
        ocupado[y0:y1, x0:x1] = True
    grossa = parede_grossa(chapada)
    branco = chapada.min(axis=-1) >= 245
    piso = ~branco & ~grossa & ~ocupado                    # o que pode ter a sombra do motor
    D = q["faixa"]
    lados = {"esquerda": (slice(None), 0), "direita": (slice(None), -1), "cima": (0, slice(None)),
             "baixo": (-1, slice(None))}
    # sombra de todas as faces, medida no render antes do retoque; onde duas se sobrepõem (cantos
    # internos) vale a mais escura, sem somar (sombra sobre sombra não escurece mais)
    S = np.ones(out.shape, np.float32)
    orig = out.copy()
    relatorio, bordas = [], []
    for (nome, _), (x0, y0, x1, y1) in zip(ARMARIOS, retangulos):
        faces = {"cima": (y0 - 1, (x0, x1), "y", -1), "baixo": (y1, (x0, x1), "y", 1),
                 "esquerda": (x0 - 1, (y0, y1), "x", -1), "direita": (x1, (y0, y1), "x", 1)}
        livres, sombras = [], []
        for lado, (c0, (a, b), eixo, passo) in faces.items():
            fora = [c0 + passo * k for k in range(0, 3)]
            g = grossa[fora, a:b] if eixo == "y" else grossa[a:b, fora]
            oc = ocupado[c0, a:b] if eixo == "y" else ocupado[a:b, c0]
            if g.mean() > 0.5 or oc.mean() > 0.5:
                continue
            livres.append(lado)
            pi = piso[fora, a:b] if eixo == "y" else piso[a:b, fora]
            if pi.mean() < 0.5 or (nome, lado) in q["manter_piso"]:
                continue

            def mascara(k, a, b):
                """Piso na linha k da faixa; nas 2 primeiras (a borda, que a base marca com traço
                ou com o branco do armário) vale o piso da linha 2."""
                c, c2 = c0 + passo * k, c0 + passo * 2
                if eixo == "y":
                    m = piso[c, a:b] if k >= 2 else piso[c2, a:b] & ~grossa[c, a:b] & ~ocupado[c, a:b]
                else:
                    m = piso[a:b, c] if k >= 2 else piso[a:b, c2] & ~grossa[a:b, c] & ~ocupado[a:b, c]
                return c, m

            # perfil por canal: mediana ao longo da face (sem 2 px nas pontas), só no piso
            a2, b2 = a + 2, b - 2
            perfil = np.full((D, 3), np.nan, np.float32)
            for k in range(D):
                c, m = mascara(k, a2, b2)
                v = orig[c, a2:b2] if eixo == "y" else orig[a2:b2, c]
                if m.sum() >= 3:
                    perfil[k] = np.median(v[m].astype(np.float32), axis=0)
            lum = perfil.mean(axis=1)
            if np.isnan(lum[:4]).any():
                continue
            # patamar: onde o piso para de clarear (cresce menos de 2% nas 3 linhas seguintes)
            dp = next((d for d in range(2, D - 3) if np.nanmax(lum[d + 1:d + 4]) - lum[d] < 0.02 * lum[d]), D - 3)
            ref = np.nanmedian(perfil[dp:dp + 4], axis=0)
            r = perfil[:dp] / ref
            if np.nanmin(r[1:].mean(axis=1)) >= q["limiar"] and abs(r[0].mean() - 1) < 1 - q["limiar"]:
                continue
            s = np.ones((D, 3), np.float32)
            for ch in range(3):
                s[:dp, ch] = modelo_sombra(np.nan_to_num(r[:, ch], nan=1.0))
                s[0, ch] = r[0, ch]                       # borda: a razão medida (traço do motor)
            # sombra local, ponto a ponto ao longo da face (inclusive um pouco além das pontas, na
            # penumbra): a razão entre o perfil local e o mediano, normalizada pelo patamar (o tom
            # da régua), suavizada ao longo da face
            e0, e1 = max(a - q["alem"], 0), b + q["alem"]
            n = e1 - e0
            loc = np.full((dp + 4, n, 3), np.nan, np.float32)
            msk = np.zeros((dp + 4, n), bool)
            for k in range(dp + 4):
                c, m = mascara(k, e0, e1)
                v = orig[c, e0:e1] if eixo == "y" else orig[e0:e1, c]
                loc[k][m] = v[m]
                msk[k] = m
            med = np.concatenate([perfil[:dp], np.repeat(ref[None], 4, axis=0)])
            Q = loc / med[:, None, :]
            Q = Q / np.nanmedian(Q[dp:], axis=0, keepdims=True)
            Qs = np.ones_like(Q)
            h2 = q["suave"]
            for k in range(dp):                           # mediana móvel: guarda a borda da penumbra
                for i in range(n):
                    j = Q[k, max(i - h2, 0):i + h2 + 1]
                    j = j[np.isfinite(j).all(axis=1)]
                    if len(j):
                        Qs[k, i] = np.median(j, axis=0)
            dentro = np.zeros(n, bool)
            dentro[a - e0:b - e0] = True
            for k in range(1, dp):
                c, m = mascara(k, e0, e1)
                sl = np.clip(s[k][None] * Qs[k], 0.25, 1.0)
                alvo = S[c, e0:e1] if eixo == "y" else S[e0:e1, c]
                alvo[m] = np.minimum(alvo[m], sl[m])
            # borda da face (o traço escuro ou claro do motor): repete a linha seguinte, já sem sombra
            c, m = mascara(0, a, b)
            bordas.append((eixo, c, c + passo, a, b, m))
            sombras.append(f"{lado} ({1 - s[1:].mean(axis=1).min():.0%}, {dp} px)")
        relatorio.append((nome, livres, sombras))
    out[:] = np.clip(out.astype(np.float32) / S, 0, 255).astype(np.uint8)
    for eixo, c, c1, a, b, m in bordas:
        if eixo == "y":
            out[c, a:b][m] = out[c1, a:b][m]
        else:
            out[a:b, c][m] = out[a:b, c1][m]

    areia = t.reshape(-1, 3).astype(np.float32).mean(axis=0)
    Y = orig.astype(np.float32).mean(axis=2)

    def veio(x0, y0, x1, y1):
        """Veio do armário do render: a luminância sobre a dela mesma desfocada (sem o degradê)."""
        y = Y[y0:y1, x0:x1]
        base = cv2.GaussianBlur(y, (0, 0), q["sigma_veio"], borderType=cv2.BORDER_REFLECT)
        return np.clip(y / np.maximum(base, 1), *q["veio_lim"])

    for (nome, livres, sombras), (x0, y0, x1, y1) in zip(relatorio, retangulos):
        h, w = y1 - y0, x1 - x0
        if nome in q["sem_veio"]:
            vx0, vy0, vx1, vy1 = q["veio_emprestado"]
            v = veio(vx0, vy0, vx1, vy1)
            v = np.concatenate([v, v[::-1]] * (h // (2 * v.shape[0]) + 1), axis=0)[:h]
            v = np.concatenate([v, v[:, ::-1]] * (w // (2 * v.shape[1]) + 1), axis=1)[:, :w]
        else:
            v = veio(x0, y0, x1, y1)
        reg = areia[None, None] * v[..., None]
        borda = np.zeros((h, w), bool)
        for lado in livres:
            borda[lados[lado]] = True
        reg[borda] *= q["contorno"]
        m = ~grossa[y0:y1, x0:x1]
        alvo = out[y0:y1, x0:x1]
        alvo[m] = np.clip(reg[m], 0, 255).astype(np.uint8)
        print(f"    {nome}: {w}x{h} px em areia ({'veio emprestado' if nome in q['sem_veio'] else 'veio do render'}); "
              f"contorno: {', '.join(livres) or '-'}; sombra tirada: {', '.join(sombras) or '-'}")
    return out


def piso_sob_armario(out, chapada):
    q = PISO_SOB_ARMARIO
    grossa = parede_grossa(chapada)
    fontes = []
    for x0, y0, x1, y1 in q["fontes"]:
        f = out[y0:y1, x0:x1].astype(np.float32)
        fontes += [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    ref = np.mean([f.reshape(-1, 3).mean(axis=0) for f in fontes], axis=0)
    rects = dict((nome, r) for nome, r in ARMARIOS)
    for nome, H, parede, protegidos in q["faixas"]:
        ax0, _, ax1, ay1 = rects[nome]
        ajuste = ARMARIO["ajuste"].get(nome, (0, 0, 0, 0))
        cx0, cx1, cy1 = int(round(ax0)) + ajuste[0], int(round(ax1)) + ajuste[2], int(round(ay1)) + ajuste[3]
        x0, x1, y0, y1 = cx0 - H, cx1, cy1, cy1 + H
        tex = quilting(fontes, y1 - y0, x1 - x0, p=12, sobra=4, candidatos=500)[:y1 - y0, :x1 - x0]
        # sombra da parede (e só ela): fator por coluna medido logo abaixo da faixa
        baixo = out[y1:y1 + q["medida"], x0:x1].astype(np.float32).mean(axis=0)
        if parede:
            f = np.clip(baixo / ref, 0, 1)
            f = np.stack([np.convolve(f[:, c], np.ones(5) / 5, "same") for c in range(3)], axis=1)
            f[:2], f[-2:] = f[2], f[-3]
            tex = tex * f[None]
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        a = np.clip((xx - cx0 + (yy - cy1)) / q["penumbra"] + 0.5, 0, 1)     # borda diagonal
        a *= np.clip((y1 - 0.5 - yy) / q["emenda"], 0, 1)                    # emenda embaixo
        a[grossa[y0:y1, x0:x1]] = 0
        for px0, py0, px1, py1 in protegidos:
            a[max(py0 - y0, 0):max(py1 - y0, 0), max(px0 - x0, 0):max(px1 - x0, 0)] = 0
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + tex * a[..., None], 0, 255).astype(np.uint8)
        print(f"    {nome}: piso refeito embaixo ({x1 - x0}x{H} px), sem a sombra do armário")
    return out


def area_molhada(out):
    q = AREA_MOLHADA
    xs, ys = [x for x, _ in q["pontos"]], [y for _, y in q["pontos"]]
    jx0, jy0, jx1, jy1 = int(min(xs)) - 2, int(min(ys)) - 1, int(max(xs)) + 3, int(max(ys)) + 3
    h, w = jy1 - jy0, jx1 - jx0
    f = np.zeros((h * SS, w * SS), np.uint8)
    pts = np.array([[int(round((x - jx0) * SS)), int(round((y - jy0) * SS))] for x, y in q["pontos"]], np.int32)
    cv2.polylines(f, [pts], False, 255, max(1, int(round(q["larg_traco"] * SS))))
    a = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None] * q["forca_traco"]
    reg = out[jy0:jy1, jx0:jx1].astype(np.float32)
    out[jy0:jy1, jx0:jx1] = np.clip(reg * (1 - a) + np.array(q["traco"], np.float32) * a, 0, 255).astype(np.uint8)
    print("    área molhada da bancada da pia demarcada (lados livres: esquerda e embaixo)")
    return out


def inox(out):
    q = INOX
    x0, y0, x1, y1 = q["janela"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    Y = reg.mean(axis=2)
    a = np.clip((Y - q["lum"][0]) / (q["lum"][1] - q["lum"][0]), 0, 1)[..., None]
    ref = np.median(Y[a[..., 0] >= 1])
    rng = np.random.default_rng(q["semente"])
    riscos = cv2.GaussianBlur(rng.normal(0, 1, (1, x1 - x0)).astype(np.float32), (0, 0), 0.7)
    riscos = 1 + q["escovado"] * riscos / max(float(riscos.std()), 1e-6)
    aco = np.array(q["cor"], np.float32)[None, None] * (Y / ref)[..., None] * riscos[..., None]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + aco * a, 0, 255).astype(np.uint8)
    print("    eletrodomésticos da cozinha em inox (o armário do canto fica em areia)")
    return out


def porta_gas(out):
    q = PORTA_GAS
    x0, y0, x1, y1 = q["soleira"]
    n = y1 - y0
    out[y0:y1, x0:x1] = out[y1:y1 + n, x0:x1][::-1]       # piso do abrigo, em espelho
    yb = int(np.ceil(q["folhas"][1][3]))
    for k, f in enumerate(q["sombra"]):
        out[yb + k, x0:x1] = np.clip(out[yb + k, x0:x1] * f, 0, 255).astype(np.uint8)

    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0

    def px(v, o):
        return int(round((v - o) * SS))

    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def pintar(mascara, cor):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    lc = max(1, px(q["larg_contorno"], 0))
    for fx0, fy0, fx1, fy1 in q["folhas"]:
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(m, (px(fx0, wx0), px(fy0, wy0)), (px(fx1, wx0), px(fy1, wy0)), 255, -1)
        pintar(m, q["folha"])
    for mx0, mx1 in q["montantes"]:
        fy0, fy1 = next((f[1], f[3]) for f in q["folhas"] if f[0] - 0.01 <= mx0 and mx1 <= f[2] + 0.01)
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(m, (px(mx0, wx0), px(fy0, wy0)), (px(mx1, wx0), px(fy1, wy0)), 255, -1)
        pintar(m, q["montante"])
    m = np.zeros((h * SS, w * SS), np.uint8)
    for fx0, fy0, fx1, fy1 in q["folhas"] + q["batentes"]:
        cv2.rectangle(m, (px(fx0, wx0), px(fy0, wy0)), (px(fx1, wx0), px(fy1, wy0)), 255, lc)
    pintar(m, q["contorno"])
    m = np.zeros((h * SS, w * SS), np.uint8)
    for bx0, by0, bx1, by1 in q["batentes"]:
        cv2.rectangle(m, (px(bx0, wx0), px(by0, wy0)), (px(bx1, wx0), px(by1, wy0)), 255, -1)
    pintar(m, q["contorno"])
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    abrigo de gás: soleira do motor fora; porta de correr do PDF (duas folhas em dois planos)")
    return out


def carros(out):
    q = CARROS
    for nome, (x0, y0, x1, y1), curva, cor in q["carros"]:
        reg = out[y0:y1, x0:x1].astype(np.float32)
        Y = reg.mean(axis=2)
        frio = np.abs(reg[..., 2] - reg[..., 0]) < q["quente"]          # o granito é quente (R > B)
        sil = ((frio & (Y > q["lum_min"])) | (Y > q["claro"])).astype(np.uint8)   # o granito nunca é tão claro
        sil = cv2.morphologyEx(sil, cv2.MORPH_CLOSE, np.ones((q["fecho"], q["fecho"]), np.uint8))
        cont, _ = cv2.findContours(sil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        sil = np.zeros_like(sil)
        cv2.drawContours(sil, [max(cont, key=cv2.contourArea)], -1, 1, -1)
        sil = cv2.dilate(sil, np.ones((3, 3), np.uint8))         # a borda misturada com o piso também
        lanterna = (reg[..., 2] - reg[..., 0] > q["lanterna"][0]) & (reg[..., 2] > q["lanterna"][1])
        a = cv2.GaussianBlur((sil * ~lanterna).astype(np.float32), (0, 0), 0.6)[..., None]
        topo = np.percentile(Y[sil > 0], 97)
        if curva[0] == "escurecer":
            _, base, faixa, ex = curva
            Yn = base + faixa * np.clip(Y / topo, 0, 1) ** ex
            Yn += q["reflexo"] * np.clip(Y - topo, 0, None)
        else:
            _, ini_, fim_, forca = curva
            s = np.clip((Y - ini_) / (fim_ - ini_), 0, 1)
            Yn = Y + forca * s * s * (3 - 2 * s) * (250 - Y)
        lo, hi = q["cor_lum"]
        sc = np.clip((Y - lo) / (hi - lo), 0, 1)[..., None]
        unid = np.array(cor, np.float32)[None, None]
        novo = Yn[..., None] * (1 + sc * (unid - 1))
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + novo * a, 0, 255).astype(np.uint8)
        print(f"    carro da {nome}: curva {curva[0]}, cor {cor}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] porta pivotante principal")
    out = pivotante(out)
    print("[2] chuveiros do banho master")
    out = chuveiros_bhm(out)
    print("[3] armários até o teto")
    _, chapada, _ = alinhar_base(orig)
    out = armarios(out, chapada)
    out = piso_sob_armario(out, chapada)
    print("[4] área molhada da bancada da pia")
    out = area_molhada(out)
    print("[5] eletrodomésticos em inox")
    out = inox(out)
    print("[6] porta de correr do abrigo de gás")
    out = porta_gas(out)
    print("[7] carros em tons diferentes")
    out = carros(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

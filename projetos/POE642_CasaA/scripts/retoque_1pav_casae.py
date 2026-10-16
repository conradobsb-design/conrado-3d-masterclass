#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do 1º Pavimento da Casa E (POE 642).

O render (Nano Banana Pro, 2000 x 1116, fundo branco: base v3 + prompt v1) manteve a escala da base:
a base 16:9 reduzida ao tamanho do render cai nele quase pela identidade (escala 0,9997 x 1,0085). Os
retoques são feitos no quadro do render, como no Térreo; o Térreo esmaecido em volta entra depois,
pelo `entorno_esmaecido.py`, com o 1º Pavimento sobreposto integralmente.

Itens (o mapa está em POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_erros.jpg):
1. Banho master, floreira: o PDF tem uma floreira com plantas ao longo da janela da parede da
   esquerda, no alto (três plantas da ARQ_LAYOUT HUMANIZAÇÃO); o motor deixou o piso liso. Entram as
   plantas tropicais do jardim interno do Térreo aprovado (um trecho dele, girado para correr na
   vertical), no retângulo do PDF, com borda suave, contorno fino da floreira (como o jardim interno
   do Térreo) e uma sombra curta no piso.
2. Banho master, chuveiros: o PDF tem dois chuveiros de teto (os quadradinhos da ARQ_LOUÇAS E
   METAIS); o motor pôs uma ducha de parede com braço e um registro no piso. Os dois saem (quartzito
   tecido do próprio banho, na luz do piso em volta) e entram as duas placas de teto de 30 cm da Casa
   A aprovada, nos centros do PDF, com sombra curta.
3. (Sem retoque.) Banhos das duas suítes da esquerda: as bacias parecem uma peça só atravessando a
   parede, mas o PDF desenha assim mesmo: duas bacias suspensas, costas com costas na parede entre os
   banhos. O render ficou fiel.
4. Copinha: o motor pintou a bancada em areia, como o armário ao lado, e não pôs a cuba. A bancada
   do PDF (da parede da esquerda ao armário) vira o Bege Bahia da varanda da esquerda do próprio
   render, na luz da bancada do render; a cuba redonda da Casa A entra no círculo do PDF (34 cm),
   com a torneira atrás, no cromo das cubas do Térreo, e uma sombra curta bem leve.
5. Vazios (abaixo da escada e no hall): o motor deixou o cinza-escuro liso. Entra o X tracejado do PDF
   (cada traço da DOC_LINHAS E PROJEÇÕES na posição exata), fino, no cinza claro das linhas dos vazios
   da base (#BDBDBD), só sobre o cinza do vazio.
6. Arcos das portas: o motor desenhou as folhas, mas nenhum arco. Entram os 12 arcos do PDF (curvas da
   ARQ_PAREDE) no padrão aprovado no Térreo (cinza (160, 161, 160), traço de 0,45 px); sobre o vazio do
   hall, no cinza claro do X, com a folha da porta pivotante P1 do Térreo, que também faltava.

Uso (da pasta POE642_CasaA/scripts/):
  python3 retoque_1pav_casae.py ../../POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_render.png \\
      --saida ../../POE642_CasaE/renders --nome POE642_CasaE_PH_1Pavimento_v1_retocado
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

from retoque_terreo_casad import CHUVEIROS_BHM  # noqa: E402
from retoque_terreo_casac import CHUVEIRO_TETO, CROMO, CROMO_CLARO, CROMO_ESCURO, SS  # noqa: E402
from retoque_subsolo_casad import apagar_largo  # noqa: E402
from retoque_terreo_casad import textura  # noqa: E402

BASE = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png"
TERREO = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado.png"
BASE_CHAPADA = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - 1º PAVIMENTO - CASA E.pdf"
CONFIG = RAIZ / "POE642_CasaE/config_bases.json"
VIS, BASE_LARG, TELA_LARG, TELA_ALT = 1800, 6001, 6905, 3884   # prévia de 1800 px, base e tela 16:9


def alinhar_base(render):
    """Base 16:9 reduzida ao tamanho do render e levada a ele por SIFT + afim (como nas outras casas)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return A


def vis2r(A, forma, x, y):
    """Ponto da prévia de 1800 px (as coordenadas da config_bases.json) no quadro do render."""
    bx = (x * BASE_LARG / VIS + (TELA_LARG - BASE_LARG) // 2) * forma[1] / TELA_LARG
    by = (y * BASE_LARG / VIS) * forma[0] / TELA_ALT
    return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]


def pdf_cadeia(A, forma_render):
    """Página do PDF e as conversões PDF -> render e render -> PDF pela mesma cadeia da base (recorte,
    largura da base, tela 16:9, redução ao tamanho do render e o afim A), como no Térreo."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["1Pavimento"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sx, sy = forma_render[1] / wt, forma_render[0] / ht
    Ai = np.linalg.inv(np.vstack([A, [0, 0, 1]]))

    def p2r(x, y):
        bx, by = ((x - clip.x0) * zoom + (wt - wb) // 2) * sx, ((y - clip.y0) * zoom + (ht - hb) // 2) * sy
        return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]

    def r2p(x, y):
        bx, by, _ = Ai @ [x, y, 1]
        return (bx / sx - (wt - wb) // 2) / zoom + clip.x0, (by / sy - (ht - hb) // 2) / zoom + clip.y0

    return pg, p2r, r2p


def caixa_render(d, p2r):
    (x0, y0), (x1, y1) = p2r(d["rect"].x0, d["rect"].y0), p2r(d["rect"].x1, d["rect"].y1)
    return x0, y0, x1, y1


def sombra(out, mascara, ret, desloc=(-1.0, 1.0), sigma=0.8, forca=0.3):
    """Sombra curta de uma peça (máscara 0..1 na janela ret), para baixo e à esquerda, como as do render."""
    x0, y0, x1, y1 = ret
    M = np.float32([[1, 0, desloc[0]], [0, 1, desloc[1]]])
    s = cv2.GaussianBlur(cv2.warpAffine(mascara.astype(np.float32), M, mascara.shape[::-1]), (0, 0), sigma)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - forca * s * (1 - mascara))[..., None], 0, 255).astype(np.uint8)
    return out


# item 1: floreira do banho master (prévia de 1800 px: as três plantas do PDF, 807,3 a 823,4 x 239,6 a
# 284,7); a fonte é um trecho do jardim interno do Térreo aprovado (render de 2000 px), girado
FLOREIRA = {"vis": (807.3, 239.6, 823.4, 284.7), "fonte": (1048, 550, 1094, 566), "borda": 0.7,
            "sombra": {"desloc": (-0.8, 1.2), "sigma": 1.0, "forca": 0.25},
            "contorno": ((88, 92, 96), 0.45)}       # borda da floreira em traço fino, como no Térreo


def floreira(out, A):
    q = FLOREIRA
    (x0, y0), (x1, y1) = vis2r(A, out.shape, *q["vis"][:2]), vis2r(A, out.shape, *q["vis"][2:])
    w, h = x1 - x0, y1 - y0
    fx0, fy0, fx1, fy1 = q["fonte"]
    t = cv2.imread(str(TERREO))[fy0:fy1, fx0:fx1]
    t = np.rot90(t, -1)                                   # a faixa do jardim passa a correr na vertical
    rx0, ry0 = int(np.floor(x0)) - 3, int(np.floor(y0)) - 3
    rx1, ry1 = int(np.ceil(x1)) + 4, int(np.ceil(y1)) + 4
    ww, hh = rx1 - rx0, ry1 - ry0
    # a peça a 8x, no lugar exato (frações de px), e reduzida por área
    big = np.zeros((hh * SS, ww * SS, 3), np.float32)
    m = np.zeros((hh * SS, ww * SS), np.float32)
    px0, py0 = int(round((x0 - rx0) * SS)), int(round((y0 - ry0) * SS))
    pw, ph = int(round(w * SS)), int(round(h * SS))
    big[py0:py0 + ph, px0:px0 + pw] = cv2.resize(t.astype(np.float32), (pw, ph), interpolation=cv2.INTER_CUBIC)
    m[py0:py0 + ph, px0:px0 + pw] = 1
    m = cv2.GaussianBlur(m, (0, 0), q["borda"] * SS)
    a = cv2.resize(m, (ww, hh), interpolation=cv2.INTER_AREA)
    cor = cv2.resize(big * m[..., None], (ww, hh), interpolation=cv2.INTER_AREA) / np.maximum(a[..., None], 1e-6)
    out = sombra(out, a, (rx0, ry0, rx1, ry1), **q["sombra"])
    reg = out[ry0:ry1, rx0:rx1].astype(np.float32)
    reg = reg * (1 - a[..., None]) + cor * a[..., None]
    cc, larg = q["contorno"]
    linha = np.zeros((hh * SS, ww * SS), np.uint8)
    cv2.rectangle(linha, (px0, py0), (px0 + pw, py0 + ph), 255, max(1, int(round(larg * SS))), cv2.LINE_AA)
    al = cv2.resize(linha.astype(np.float32) / 255, (ww, hh), interpolation=cv2.INTER_AREA)[..., None]
    out[ry0:ry1, rx0:rx1] = np.clip(reg * (1 - al) + np.float32(cc) * al, 0, 255).astype(np.uint8)
    print(f"    floreira com plantas em ({x0:.1f}, {y0:.1f}) a ({x1:.1f}, {y1:.1f})")
    return out


# item 2: chuveiros de teto do banho master. Saem a ducha de parede (com o braço até a parede da
# direita) e o registro do piso; entram as placas nos centros dos quadradinhos do PDF (prévia de 1800 px)
CHUVEIROS = {"tirar": [(992, 388, 1010, 401), (974, 404, 986, 420)], "janela": (958, 372, 1012, 422),
             "fontes": [(930, 300, 968, 336), (968, 300, 1000, 330)],
             "centros_vis": [(868.9, 414.05), (896.45, 414.05)], "lado": 9.4}


def placa_teto(out, cx, cy, lado):
    """Placa quadrada de chuveiro de teto (a da Casa A, 30 cm) com a sombra curta aprovada."""
    s = CHUVEIROS_BHM["sombra"]
    x0, y0 = int(np.floor(cx - lado / 2)) - 3, int(np.floor(cy - lado / 2)) - 3
    x1, y1 = int(np.ceil(cx + lado / 2)) + 4, int(np.ceil(cy + lado / 2)) + 4
    w, h = x1 - x0, y1 - y0
    p0x, p0y = int(round((cx - lado / 2 - x0) * SS)), int(round((cy - lado / 2 - y0) * SS))
    lp = int(round(lado * SS))
    m = np.zeros((h * SS, w * SS), np.float32)
    m[p0y:p0y + lp, p0x:p0x + lp] = 1
    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    cor = np.zeros((h * SS, w * SS, 3), np.float32)
    cor[p0y:p0y + lp, p0x:p0x + lp] = cv2.resize(img[hy0:hy1, hx0:hx1], (lp, lp), interpolation=cv2.INTER_CUBIC)
    a = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA)
    c = cv2.resize(cor, (w, h), interpolation=cv2.INTER_AREA) / np.maximum(a[..., None], 1e-6)
    out = sombra(out, a, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + c * a[..., None], 0, 255).astype(np.uint8)
    return out


def chuveiros(out, A):
    q = CHUVEIROS
    x0, y0, x1, y1 = q["janela"]
    m = np.zeros((y1 - y0, x1 - x0), bool)
    for tx0, ty0, tx1, ty1 in q["tirar"]:
        m[ty0 - y0:ty1 - y0, tx0 - x0:tx1 - x0] = True
    out = apagar_largo(out, q["janela"], m, q["fontes"], sigma=3.0, borda=0.8, lum_min=110)
    for xv, yv in q["centros_vis"]:
        cx, cy = vis2r(A, out.shape, xv, yv)
        out = placa_teto(out, cx, cy, q["lado"])
        print(f"    placa de teto em ({cx:.1f}, {cy:.1f})")
    return out


# item 4: copinha. O motor pintou a bancada em areia, como o armário ao lado, e não pôs a cuba. A
# bancada do PDF (ARQ_BANCADAS, da parede da esquerda ao armário) vira o Bege Bahia da varanda da
# esquerda do próprio render, na luz da bancada do render (perfil por linha, com o brilho junto à
# parede); a cuba redonda da Casa A entra no círculo do PDF, com a torneira atrás (lado da parede)
COPINHA = {"bancada_pdf": (1672.2, 1096.41, 1828.97, 1130.03), "fontes": [(622, 380, 712, 520), (622, 540, 712, 680)],
           "lum_parede": 10.0, "cuba_pdf": (1810.92, 1110.57, 9.64), "torneira_pdf": (1810.92, 1125.5),
           "bacia": 0.80, "sombra": {"desloc": (-0.8, 1.0), "sigma": 0.8, "forca": 0.2}}


def bancada_copinha(out, p2r):
    q = COPINHA
    (bx0, by0), (bx1, by1) = p2r(*q["bancada_pdf"][:2]), p2r(*q["bancada_pdf"][2:])
    # janela com um px de folga em cima, embaixo e à esquerda (as bordas do render, entre a bancada,
    # a linha da frente e as paredes, entram pela luminância); à direita, o fim exato do PDF
    x0, y0, x1, y1 = int(np.floor(bx0)) - 1, int(np.floor(by0)) - 1, int(np.ceil(bx1)), int(np.ceil(by1)) + 1
    h, w = y1 - y0, x1 - x0
    cob = np.ones((h, w), np.float32)
    cob[:, -1] = bx1 - (x1 - 1)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    L = reg.mean(axis=2)
    # areia do render por linha (mediana); as linhas de borda usam a linha cheia mais próxima
    med = np.median(reg[:, 2:-2], axis=1)
    cheia = med.mean(axis=1) > 0.9 * med.mean(axis=1).max()
    idx = np.flatnonzero(cheia)
    areia = med[idx[np.abs(np.arange(h)[:, None] - idx[None]).argmin(axis=1)]]
    Ls = areia.mean(axis=1)
    m = cob * np.clip((L - q["lum_parede"]) / (Ls[:, None] - q["lum_parede"]), 0, 1)
    fontes = q["fontes"]
    bege = np.mean([out[fy0:fy1, fx0:fx1].reshape(-1, 3).astype(np.float32).mean(axis=0)
                    for fx0, fy0, fx1, fy1 in fontes], axis=0)
    tex = textura(out, fontes, h, w, p=12)
    alvo = tex * bege * (Ls / Ls[cheia].mean())[:, None, None]
    out[y0:y1, x0:x1] = np.clip(reg + m[..., None] * (alvo - areia[:, None, :]), 0, 255).astype(np.uint8)
    print(f"    bancada em Bege Bahia de ({bx0:.1f}, {by0:.1f}) a ({bx1:.1f}, {by1:.1f})")
    return out


def cuba_redonda(out, cx, cy, R, tx, ty, bacia, s):
    """A cuba redonda da Casa A (retoque_base_1pav.py, 3b): borda de louça, bacia, contorno fino, ralo e a
    torneira atrás (base redonda e bica até o centro, no cromo das cubas do Térreo), em 8x; com uma
    sombra curta, bem leve."""
    n = int(np.ceil(2 * max(R, abs(ty - cy), abs(tx - cx)) + 12))
    ox, oy = int(np.floor(cx - n / 2)), int(np.floor(cy - n / 2))
    big = np.zeros((n * SS, n * SS, 4), np.float32)
    c = (int(round((cx - ox) * SS)), int(round((cy - oy) * SS)))
    Rs = int(round(R * SS))
    cv2.circle(big, c, Rs, (238, 239, 240, 1.0), -1, cv2.LINE_AA)                              # borda da louça
    cv2.circle(big, c, int(Rs * bacia), (250, 250, 250, 1.0), -1, cv2.LINE_AA)                 # bacia
    cv2.circle(big, c, Rs, (168, 170, 172, 1.0), max(1, int(round(0.5 * SS))), cv2.LINE_AA)   # contorno fino
    cv2.circle(big, c, int(Rs * bacia), (205, 207, 209, 1.0), max(1, int(round(0.35 * SS))), cv2.LINE_AA)
    cv2.circle(big, c, max(2, int(round(0.7 * SS))), (150, 152, 155, 1.0), -1, cv2.LINE_AA)  # ralo
    t0 = (int(round((tx - ox) * SS)), int(round((ty - oy) * SS)))
    t1 = (c[0], int(round(c[1] + Rs * 0.15)))
    # torneira no cromo das cubas do Térreo (acabamentos_finais.cuba): base redonda e bica
    for larg, cor in ((0.78, CROMO_ESCURO), (0.48, CROMO), (0.2, CROMO_CLARO)):
        cv2.line(big, t0, t1, (*cor, 1.0), max(1, int(round(larg * SS))), cv2.LINE_AA)
    for raio, cor in ((0.86, CROMO_ESCURO), (0.72, CROMO), (0.42, CROMO_CLARO)):
        cv2.circle(big, t0, max(1, int(round(raio * SS))), (*cor, 1.0), -1, cv2.LINE_AA)
    peq = cv2.resize(big, (n, n), interpolation=cv2.INTER_AREA)
    a = peq[..., 3]
    out = sombra(out, a, (ox, oy, ox + n, oy + n), s["desloc"], s["sigma"], s["forca"])
    reg = out[oy:oy + n, ox:ox + n].astype(np.float32)
    cor = peq[..., :3] / np.maximum(a[..., None], 1e-6)
    out[oy:oy + n, ox:ox + n] = np.clip(reg * (1 - a[..., None]) + cor * a[..., None], 0, 255).astype(np.uint8)
    return out


def copinha(out, p2r):
    q = COPINHA
    out = bancada_copinha(out, p2r)
    cxp, cyp, rp = q["cuba_pdf"]
    cx, cy = p2r(cxp, cyp)
    R = np.hypot(*np.subtract(p2r(cxp + rp, cyp), (cx, cy)))
    tx, ty = p2r(*q["torneira_pdf"])
    out = cuba_redonda(out, cx, cy, R, tx, ty, q["bacia"], q["sombra"])
    print(f"    cuba redonda em ({cx:.1f}, {cy:.1f}), diâmetro {2 * R:.1f} px; torneira em ({tx:.1f}, {ty:.1f})")
    return out


# item 5: vazios (abaixo da escada e no hall). O motor deixou os dois em cinza-escuro liso; o PDF tem
# o X tracejado (cada traço é um segmento da DOC_LINHAS E PROJEÇÕES). Os traços entram nas posições
# exatas, finos, no cinza claro das linhas dos vazios da base (#BDBDBD), só sobre o cinza do vazio
VAZIOS = {"vis": [(875.6, 565.4, 1060.2, 605.6), (1062.3, 716.4, 1200.5, 850.5)],
          "camada": "DOC_LINHAS E PROJEÇÕES", "cor": (189, 189, 189), "largura": 0.7, "cinza": (68.0, 14.0)}


def vazios(out, A, pg, p2r, r2p):
    q = VAZIOS
    tracos = [d for d in pg.get_drawings() if d.get("layer") == q["camada"]]
    for v in q["vis"]:
        (x0, y0), (x1, y1) = vis2r(A, out.shape, *v[:2]), vis2r(A, out.shape, *v[2:])
        clip = pymupdf.Rect(*r2p(x0, y0), *r2p(x1, y1))
        x0, y0, x1, y1 = int(np.floor(x0)) - 4, int(np.floor(y0)) - 4, int(np.ceil(x1)) + 4, int(np.ceil(y1)) + 4
        tela = np.zeros(((y1 - y0) * SS, (x1 - x0) * SS), np.uint8)
        n = 0
        for d in tracos:
            if not d["rect"].intersects(clip):
                continue
            for it in d["items"]:
                if it[0] != "l":
                    continue
                (ax, ay), (bx, by) = p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)
                cv2.line(tela, (int(round((ax - x0) * SS)), int(round((ay - y0) * SS))),
                         (int(round((bx - x0) * SS)), int(round((by - y0) * SS))), 255,
                         max(1, int(round(q["largura"] * SS))), cv2.LINE_AA)
                n += 1
        a = cv2.resize(tela.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        reg = out[y0:y1, x0:x1].astype(np.float32)
        c, tol = q["cinza"]
        a *= np.abs(reg - c).max(axis=2) < tol                      # só sobre o cinza do vazio
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None], 0, 255).astype(np.uint8)
        print(f"    vazio em ({x0}, {y0}) a ({x1}, {y1}): {n} traços do X")
    return out


# item 6: arcos das portas. O motor desenhou as folhas, mas nenhum arco. Entram as curvas da ARQ_PAREDE
# do PDF no padrão aprovado no Térreo (retoque_terreo_casae.ARCOS: cinza (160, 161, 160), traço de
# 0,45 px); sobre o cinza do vazio do hall, no cinza claro do X; as paredes (escuras) não mudam. A porta
# pivotante P1 do hall do Térreo, vista pelo vazio, também ficou sem a folha (retângulo branco da
# ARQ_PAREDE, dos dois lados do pivô): entra cheia, no mesmo cinza
ARCOS = {"cor": (160, 161, 160), "larg": 0.45, "min_px": 6, "parede": 45,
         "folhas_pdf": [(2122.6, 1526.6, 2271.7, 1529.4)]}


def pintar_traco(out, f, ret, q):
    """Traço desenhado em 8x (f) na janela ret: cinza fino no piso, cinza claro do X sobre o vazio;
    as paredes (escuras) não mudam."""
    x0, y0, x1, y1 = ret
    a = cv2.resize(f.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    a *= reg.mean(axis=2) > q["parede"]
    c, tol = VAZIOS["cinza"]
    vazio = (np.abs(reg - c).max(axis=2) < tol)[..., None]
    cor = np.where(vazio, np.float32(VAZIOS["cor"]), np.float32(q["cor"]))
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + cor * a[..., None], 0, 255).astype(np.uint8)
    return out


def arcos_portas(out, pg, p2r):
    q = ARCOS
    n = 0
    for d in pg.get_drawings():
        if d.get("layer") != "ARQ_PAREDE" or not any(it[0] == "c" for it in d["items"]):
            continue
        x0, y0, x1, y1 = caixa_render(d, p2r)
        if max(x1 - x0, y1 - y0) < q["min_px"]:
            continue
        x0, y0, x1, y1 = int(x0) - 4, int(y0) - 4, int(np.ceil(x1)) + 5, int(np.ceil(y1)) + 5
        h, w = y1 - y0, x1 - x0
        f = np.zeros((h * SS, w * SS), np.uint8)
        for it in d["items"]:
            if it[0] == "c":
                pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
                tt = np.linspace(0, 1, 80)[:, None]
                c = (1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1] + 3 * (1 - tt) * tt ** 2 * pp[2] + tt ** 3 * pp[3]
                cv2.polylines(f, [np.round((c - [x0, y0]) * SS).astype(np.int32)], False, 255,
                              max(1, int(round(q["larg"] * SS))), cv2.LINE_AA)
        out = pintar_traco(out, f, (x0, y0, x1, y1), q)
        n += 1
    for fx0, fy0, fx1, fy1 in q["folhas_pdf"]:
        canto = np.array([p2r(fx0, fy0), p2r(fx1, fy0), p2r(fx1, fy1), p2r(fx0, fy1)])
        x0, y0 = np.floor(canto.min(axis=0)).astype(int) - 3
        x1, y1 = np.ceil(canto.max(axis=0)).astype(int) + 3
        h, w = y1 - y0, x1 - x0
        f = np.zeros((h * SS, w * SS), np.uint8)
        cv2.fillConvexPoly(f, np.round((canto - [x0, y0]) * SS).astype(np.int32), 255, cv2.LINE_AA)
        out = pintar_traco(out, f, (x0, y0, x1, y1), q)
        print(f"    folha da porta pivotante do hall em ({x0}, {y0}) a ({x1}, {y1})")
    print(f"    {n} arcos de porta em cinza fino")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    A = alinhar_base(orig)
    print("[1] banho master: floreira com plantas junto à janela")
    out = floreira(out, A)
    print("[2] banho master: dois chuveiros de teto")
    out = chuveiros(out, A)
    pg, p2r, r2p = pdf_cadeia(A, out.shape)
    print("[4] copinha: bancada em Bege Bahia e cuba redonda")
    out = copinha(out, p2r)
    print("[5] vazios: X tracejado claro")
    out = vazios(out, A, pg, p2r, r2p)
    print("[6] arcos das portas em cinza fino")
    out = arcos_portas(out, pg, p2r)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

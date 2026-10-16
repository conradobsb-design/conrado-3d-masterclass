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
5. Vazios (abaixo da escada, sobre o jardim de inverno do Térreo, e no hall de entrada): o motor deixou o
   cinza-escuro liso. Ficam brancos (pedido do usuário), como os vazios da Casa A, com o X tracejado do PDF
   (cada traço da DOC_LINHAS E PROJEÇÕES na posição exata) em cinza médio e o guarda-corpo de vidro do PDF
   (ARQ_ELEMENTOS FIXOS) que isola os vazios, no vidro fino aprovado.
6. Arcos das portas: o motor desenhou as folhas, mas nenhum arco. Entram os 12 arcos do PDF (curvas da
   ARQ_PAREDE) no padrão aprovado no Térreo (cinza (160, 161, 160), traço de 0,45 px); sobre o vazio do
   hall, com a folha da porta pivotante P1 do Térreo, que também faltava.
7. Cortinas (pedido do usuário): as linhas onduladas do PDF ao longo das janelas das suítes (10 trechos,
   160 arcos) entram nas posições exatas como cortina de linho off-white, em traço fino, com a sombra
   curta aprovada.
8. (Sem retoque, pedido do usuário.) Os três vasos de planta que o motor pôs nas varandas ficam.
9. Shaft (pedido do usuário): o retângulo e o X tracejado do PDF dentro da parede grossa de cima da
   suíte master (10 traços da DOC_LINHAS E PROJEÇÕES), que somem no preto, entram em cinza, finos.
10. Fachadas das suítes (pedido do usuário: cortinas, portas de correr de vidro finas e delicadas e
    brises em bronze): o motor fez um caixilho largo e cinza em toda a faixa da janela e nenhum brise. A
    faixa da parede é refeita pelo PDF (parede em preto, vão como soleira no Bege Bahia da varanda), com
    as folhas de correr do PDF (pares de meias-folhas e montantes) e as janelas dos banhos no vidro fino;
    o sombreado do caixilho no piso de dentro some. Os brises (as colunas da ARQ_ELEMENTOS FIXOS na
    fachada da esquerda e na borda de fora das varandas da direita) entram como faixa de bronze. Roda
    antes das cortinas.
11. Cubas no lugar do PDF (pedidos do usuário: "cuba posicionada mais à direita da bancada da pia";
    "ambas as cubas estão mais à esquerda, do que centralizadas nas bancadas"): a cuba do render, com a
    torneira, vai para o centro do recorte do PDF: nos banhos das suítes da direita, 10,8 e 10,7 px para
    a direita; nos dois banhos da esquerda (costas com costas), 9,7 px para a esquerda. Onde estava, o
    tampo limpo do lado, espelhado, na luz do tampo.
12. Bancos em frente às camas (pedido do usuário): os cinco bancos do PDF (ARQ_LAYOUT HUMANIZAÇÃO, na
    largura da cama), no pé de cada cama do render, com a folga do PDF (o motor fez as camas 3 a 5 px
    mais compridas; a da master, 22 px), no banco de madeira em ripas aprovado no Térreo.

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


# item 5: vazios (abaixo da escada, sobre o jardim de inverno do Térreo, e no hall de entrada). O motor
# deixou os dois em cinza-escuro liso. A pedido do usuário ficam brancos, como os vazios aprovados da
# Casa A (250), com o X tracejado do PDF (cada traço é um segmento da DOC_LINHAS E PROJEÇÕES) em cinza
# médio, como o da Casa A, e o guarda-corpo de vidro que isola os vazios (os retângulos de 2 cm da
# ARQ_ELEMENTOS FIXOS, na base e à esquerda do vazio da escada e à esquerda do vazio do hall), no vidro
# fino aprovado (vidro, contorno). O cinza do render vira branco; nos lados com guarda-corpo, o vazio
# vai até o vidro do PDF (o motor deixou o piso entrar até 4 px); as paredes (escuras) não mudam
VAZIOS = {"vazios": [{"vis": (875.6, 565.4, 1060.2, 605.6),
                      "guardas": [(1657.3, 1292.6, 1984.0, 1293.7), (1657.3, 1217.9, 1658.4, 1293.7)]},
                     {"vis": (1062.3, 716.4, 1200.5, 850.5), "guardas": [(1986.3, 1487.2, 1987.4, 1697.0)]}],
          "camada": "DOC_LINHAS E PROJEÇÕES", "branco": 250, "cor": (147, 147, 147), "largura": 0.7,
          "cinza": (68.0, 16.0), "parede": 40, "faixa": 6,
          "vidro": (222, 218, 210), "alfa_vidro": 0.85, "contorno": (70, 72, 74), "larg_contorno": 0.5,
          "larg_guarda": 1.6}


def vazios(out, A, pg, p2r, r2p):
    q = VAZIOS
    tracos = [d for d in pg.get_drawings() if d.get("layer") == q["camada"]]
    for v in q["vazios"]:
        (vx0, vy0), (vx1, vy1) = vis2r(A, out.shape, *v["vis"][:2]), vis2r(A, out.shape, *v["vis"][2:])
        clip = pymupdf.Rect(*r2p(vx0, vy0), *r2p(vx1, vy1))
        x0, y0, x1, y1 = int(np.floor(vx0)) - 8, int(np.floor(vy0)) - 8, int(np.ceil(vx1)) + 8, int(np.ceil(vy1)) + 8
        h, w = y1 - y0, x1 - x0
        reg = out[y0:y1, x0:x1].astype(np.float32)

        def tela_ret(rx0, ry0, rx1, ry1):
            f = np.zeros((h * SS, w * SS), np.uint8)
            cv2.rectangle(f, (int(round((rx0 - x0) * SS)), int(round((ry0 - y0) * SS))),
                          (int(round((rx1 - x0) * SS)) - 1, int(round((ry1 - y0) * SS)) - 1), 255, -1)
            return f

        def reduz(f):
            return cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

        # o branco: o cinza do render (perto do retângulo) e, nos lados com guarda-corpo, a faixa até o vidro
        c, tol = q["cinza"]
        perto = reduz(tela_ret(vx0 - 2, vy0 - 2, vx1 + 2, vy1 + 2)) > 0.5
        m = ((np.abs(reg - c).max(axis=2) < tol) & perto).astype(np.float32)
        guardas = []
        for g in v["guardas"]:
            (gx0, gy0), (gx1, gy1) = p2r(*g[:2]), p2r(*g[2:])
            guardas.append((gx0, gy0, gx1, gy1))
            k = q["faixa"]
            if gy1 - gy0 > gx1 - gx0:                                   # vertical: o vazio à direita
                f = tela_ret(gx1, max(gy0, vy0), gx1 + k, min(gy1, vy1))
            else:                                                       # horizontal: o vazio acima
                f = tela_ret(max(gx0, vx0), gy0 - k, min(gx1, vx1), gy0)
            m = np.maximum(m, reduz(f) * (reg.mean(axis=2) > q["parede"]))
        reg = reg * (1 - m[..., None]) + q["branco"] * m[..., None]
        # o X tracejado, só sobre o branco do vazio
        f = np.zeros((h * SS, w * SS), np.uint8)
        n = 0
        for d in tracos:
            if not d["rect"].intersects(clip):
                continue
            for it in d["items"]:
                if it[0] != "l":
                    continue
                (ax, ay), (bx, by) = p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)
                cv2.line(f, (int(round((ax - x0) * SS)), int(round((ay - y0) * SS))),
                         (int(round((bx - x0) * SS)), int(round((by - y0) * SS))), 255,
                         max(1, int(round(q["largura"] * SS))), cv2.LINE_AA)
                n += 1
        a = (reduz(f) * m)[..., None]
        reg = reg * (1 - a) + np.float32(q["cor"]) * a
        # guarda-corpo de vidro: faixa fina centrada no retângulo do PDF (2 cm), vidro e contorno
        for gx0, gy0, gx1, gy1 in guardas:
            e = q["larg_guarda"] / 2
            if gy1 - gy0 > gx1 - gx0:
                xc = (gx0 + gx1) / 2
                r_ = (xc - e, gy0, xc + e, gy1)
            else:
                yc = (gy0 + gy1) / 2
                r_ = (gx0, yc - e, gx1, yc + e)
            a = (reduz(tela_ret(*r_)) * q["alfa_vidro"])[..., None]
            reg = reg * (1 - a) + np.float32(q["vidro"]) * a
            f = np.zeros((h * SS, w * SS), np.uint8)
            cv2.rectangle(f, (int(round((r_[0] - x0) * SS)), int(round((r_[1] - y0) * SS))),
                          (int(round((r_[2] - x0) * SS)), int(round((r_[3] - y0) * SS))), 255,
                          max(1, int(round(q["larg_contorno"] * SS))))
            a = reduz(f)[..., None]
            reg = reg * (1 - a) + np.float32(q["contorno"]) * a
        out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    vazio em ({vx0:.1f}, {vy0:.1f}) a ({vx1:.1f}, {vy1:.1f}): branco, {n} traços do X, "
              f"{len(guardas)} guarda-corpo(s) de vidro")
    return out


# item 6: arcos das portas. O motor desenhou as folhas, mas nenhum arco. Entram as curvas da ARQ_PAREDE
# do PDF no padrão aprovado no Térreo (retoque_terreo_casae.ARCOS: cinza (160, 161, 160), traço de
# 0,45 px), também sobre o branco do vazio do hall; as paredes (escuras) não mudam. A porta
# pivotante P1 do hall do Térreo, vista pelo vazio, também ficou sem a folha (retângulo branco da
# ARQ_PAREDE, dos dois lados do pivô): entra cheia, no mesmo cinza
ARCOS = {"cor": (160, 161, 160), "larg": 0.45, "min_px": 6, "parede": 45,
         "folhas_pdf": [(2122.6, 1526.6, 2271.7, 1529.4)]}


def pintar_traco(out, f, ret, q):
    """Traço desenhado em 8x (f) na janela ret, em cinza fino; as paredes (escuras) não mudam."""
    x0, y0, x1, y1 = ret
    a = cv2.resize(f.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    a *= reg.mean(axis=2) > q["parede"]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None], 0, 255).astype(np.uint8)
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


# item 7: cortinas (pedido do usuário). O PDF tem as linhas onduladas ao longo das janelas das suítes
# (10 trechos, 160 arcos da ARQ_LOUÇAS E METAIS em traço de 0,85); o motor não desenhou. Entram as
# ondas exatas do PDF como cortina de linho off-white (a dos prompts da Casa A: "leves, finas e rentes
# ao vidro"), num traço fino, com a sombra curta aprovada; as paredes (escuras) não mudam
CORTINAS = {"camada": "ARQ_LOUÇAS E METAIS", "traco_pdf": 0.85, "cor": (210, 221, 230), "larg": 0.85,
            "sombra": {"desloc": (-0.8, 1.0), "sigma": 0.7, "forca": 0.3}, "parede": 45}


def cortinas(out, pg, p2r):
    q = CORTINAS
    arcos = [d for d in pg.get_drawings() if d.get("layer") == q["camada"] and d.get("color") == (0.0, 0.0, 0.0)
             and abs((d.get("width") or 0) - q["traco_pdf"]) < 0.01]
    # trechos: arcos que se tocam
    trechos = []
    for d in arcos:
        b = pymupdf.Rect(d["rect"]) + (-1.5, -1.5, 1.5, 1.5)
        for t in trechos:
            if any(b.intersects(e["rect"]) for e in t):
                t.append(d)
                break
        else:
            trechos.append([d])
    for t in trechos:
        pts = []
        for d in t:
            for it in d["items"]:
                if it[0] == "c":
                    pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
                    tt = np.linspace(0, 1, 24)[:, None]
                    pts.append((1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1] + 3 * (1 - tt) * tt ** 2 * pp[2]
                               + tt ** 3 * pp[3])
                elif it[0] == "l":
                    pts.append(np.array([p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)]))
        todos = np.vstack(pts)
        x0, y0 = np.floor(todos.min(axis=0)).astype(int) - 4
        x1, y1 = np.ceil(todos.max(axis=0)).astype(int) + 5
        h, w = y1 - y0, x1 - x0
        f = np.zeros((h * SS, w * SS), np.uint8)
        for c in pts:
            cv2.polylines(f, [np.round((c - [x0, y0]) * SS).astype(np.int32)], False, 255,
                          max(1, int(round(q["larg"] * SS))), cv2.LINE_AA)
        a = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
        a *= out[y0:y1, x0:x1].astype(np.float32).mean(axis=2) > q["parede"]
        s = q["sombra"]
        out = sombra(out, a, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None], 0, 255).astype(np.uint8)
    print(f"    {len(trechos)} trechos de cortina ({len(arcos)} arcos do PDF)")
    return out


# item 10: fachadas das suítes (pedido do usuário: "temos 3 camadas: cortinas, portas de vidro finas e
# delicadas de correr e brises em bronze"; "brise de bronze mais a externa da fachada"; "portas/folhas de
# vidro de correr nas varandas, mais finas e melhor representadas"). O motor desenhou um caixilho largo
# e cinza em toda a faixa da janela e nenhum brise. A faixa da parede é refeita pelo PDF (ARQ_PAREDE):
# parede (cinza no PDF) em preto, vão (branco no PDF) como soleira no Bege Bahia da varanda; por cima,
# as folhas de correr do PDF (cada par de meias-folhas, com os montantes das pontas) e as janelas dos
# banhos, finas, no vidro aprovado; o sombreado do caixilho no piso de dentro some (a luz do piso logo
# ao lado). Os brises (colunas de lâminas da ARQ_ELEMENTOS FIXOS: na fachada da esquerda e na borda de
# fora das varandas da direita; lâminas de 0,9 px, finas demais para desenhar uma a uma sem moiré) entram
# como uma faixa de bronze com as bordas escuras, um brilho no meio e a sombra curta aprovada
FACHADAS = {
    "faixas": [{"nome": "esquerda", "x": (1204.48, 1215.82), "y": (760.0, 1690.0), "dentro": +1},
               {"nome": "direita", "x": (2233.46, 2241.96), "y": (875.0, 1445.0), "dentro": -1}],
    "brises": [(1199.94, 733.7, 1203.91, 1682.2), (2316.2, 753.0, 2320.2, 1450.3)],
    "fontes_bege": [(622, 380, 712, 520), (622, 540, 712, 680)],
    "parede": (12, 12, 15), "dentro_px": 4, "ref_px": (5, 10),
    "vidro": (222, 218, 210), "alfa_vidro": 0.9, "montante": (150, 153, 156), "contorno": (88, 90, 93),
    "larg_contorno": 0.35, "brilho_vidro": (240, 240, 238), "larg_brilho": 0.25,
    "bronze": (74, 106, 139), "bronze_borda": (44, 66, 90), "bronze_brilho": (112, 146, 180),
    "larg_bronze_borda": 0.35, "larg_bronze_brilho": 0.4,
    "sombra": {"desloc": (-0.8, 1.0), "sigma": 0.8, "forca": 0.3},
}


def fachadas(out, pg, p2r):
    q = FACHADAS
    D = pg.get_drawings()

    def canto(r):
        return np.array([p2r(r[0], r[1]), p2r(r[2], r[1]), p2r(r[2], r[3]), p2r(r[0], r[3])])

    bege = np.mean([out[fy0:fy1, fx0:fx1].reshape(-1, 3).astype(np.float32).mean(axis=0)
                    for fx0, fy0, fx1, fy1 in q["fontes_bege"]], axis=0)
    for fa in q["faixas"]:
        bx0, bx1 = fa["x"]
        fy0, fy1 = fa["y"]
        dentro = [d for d in D if d.get("layer") == "ARQ_PAREDE" and d["type"] == "f"
                  and d["rect"].x0 >= bx0 - 0.05 and d["rect"].x1 <= bx1 + 0.05 and fy0 <= d["rect"].y0 <= fy1]
        paredes = [d["rect"] for d in dentro if d["fill"][0] < 0.5]
        brancos = [d["rect"] for d in dentro if d["fill"][0] > 0.9]
        cx = np.array([canto((bx0, fy0, bx1, fy1))])[0]
        x0, y0 = np.floor(cx.min(axis=0)).astype(int) - 2
        x1, y1 = np.ceil(cx.max(axis=0)).astype(int) + 2
        x0w, x1w = (x0, x1 + q["ref_px"][1] + 2) if fa["dentro"] > 0 else (x0 - q["ref_px"][1] - 2, x1)
        h, w = y1 - y0, x1w - x0w

        def tela(polis, linha=None):
            f = np.zeros((h * SS, w * SS), np.uint8)
            for p in polis:
                pp = np.round((p - [x0w, y0]) * SS).astype(np.int32)
                if linha is None:
                    cv2.fillConvexPoly(f, pp, 255, cv2.LINE_AA)
                else:
                    cv2.polylines(f, [pp], True, 255, max(1, int(round(linha * SS))), cv2.LINE_AA)
            return cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]

        reg = out[y0:y1, x0w:x1w].astype(np.float32)
        # trechos da fachada: intervalos de y com desenho na faixa (onde não há, como nos banhos da
        # direita, que avançam até a varanda, a faixa não existe)
        trechos = []
        for r in sorted(paredes + brancos, key=lambda r: r.y0):
            if trechos and r.y0 <= trechos[-1][1] + 2.0:
                trechos[-1][1] = max(trechos[-1][1], r.y1)
            else:
                trechos.append([r.y0, r.y1])
        faixa = tela([canto((bx0, ta, bx1, tb)) for ta, tb in trechos])[..., 0]
        cols = np.flatnonzero(faixa.max(axis=0) > 0.5)
        borda = cols.max() + 1 if fa["dentro"] > 0 else cols.min() - 1
        k, (r0, r1) = q["dentro_px"], q["ref_px"]
        if fa["dentro"] > 0:
            alvo, ref = slice(borda, borda + k), slice(borda + r0, borda + r1)
        else:
            alvo, ref = slice(borda - k + 1, borda + 1), slice(borda - r1 + 1, borda - r0 + 1)
        L = reg.mean(axis=2)
        lr = cv2.GaussianBlur(np.median(L[:, ref], axis=1)[:, None], (0, 0), 2.0)[:, 0]
        la = cv2.GaussianBlur(L[:, alvo].mean(axis=1)[:, None], (0, 0), 2.0)[:, 0]
        ganho = np.clip(lr / np.maximum(la, 1), 1.0, 1.3)
        # só nas linhas de vão (sem parede na borda de dentro da faixa)
        muro = tela([canto(r) for r in paredes])[..., 0]
        lado = slice(max(borda - 3, 0), borda) if fa["dentro"] > 0 else slice(borda + 1, borda + 4)
        vao = (faixa[:, lado].max(axis=1) > 0.5) & (muro[:, lado].max(axis=1) < 0.05)
        ganho = np.where(vao, ganho, 1.0)
        reg[:, alvo] *= ganho[:, None, None]
        # a faixa: soleira de Bege Bahia no vão, parede em preto, folhas e janelas de vidro
        tex = textura(out, q["fontes_bege"], h, w, p=12) * bege
        a = faixa[..., None]
        reg = reg * (1 - a) + tex * a
        a = muro[..., None] * faixa[..., None]
        reg = reg * (1 - a) + np.float32(q["parede"]) * a
        # folhas de correr: pares de meias-folhas (1,42 de largura) lado a lado, com os montantes das
        # pontas (os brancos da largura da folha logo acima e abaixo)
        meias = sorted([r for r in brancos if abs(r.width - 1.42) < 0.05 and r.height > 20], key=lambda r: (r.y0, r.x0))
        folhas = []
        for i in range(0, len(meias) - 1):
            m0, m1 = meias[i], meias[i + 1]
            if abs(m0.y0 - m1.y0) < 0.1 and abs(m0.x1 - m1.x0) < 0.05:
                folhas.append((m0.x0, m0.y0, m1.x1, m0.y1))
        n_jan = 0
        for fx0_, fy0_, fx1_, fy1_ in folhas:
            mont = [r for r in brancos if abs(r.x0 - fx0_) < 0.05 and abs(r.x1 - fx1_) < 0.05 and r.height < 6
                    and (abs(r.y1 - fy0_) < 0.05 or abs(r.y0 - fy1_) < 0.05)]
            ya = min([fy0_] + [r.y0 for r in mont])
            yb = max([fy1_] + [r.y1 for r in mont])
            a = tela([canto((fx0_, fy0_, fx1_, fy1_))]) * q["alfa_vidro"]
            reg = reg * (1 - a) + np.float32(q["vidro"]) * a
            for r in mont:
                a = tela([canto((r.x0, r.y0, r.x1, r.y1))])
                reg = reg * (1 - a) + np.float32(q["montante"]) * a
            xm = (fx0_ + fx1_) / 2
            a = tela([np.array([p2r(xm, fy0_), p2r(xm, fy1_)])], q["larg_brilho"])
            reg = reg * (1 - a) + np.float32(q["brilho_vidro"]) * a
            a = tela([canto((fx0_, ya, fx1_, yb))], q["larg_contorno"])
            reg = reg * (1 - a) + np.float32(q["contorno"]) * a
        # janelas dos banhos: o vidro (branco mais largo que uma meia-folha, dentro do vão), com contorno
        for r in brancos:
            if 3.5 < r.width < 5 and r.height > 40:
                a = tela([canto((r.x0, r.y0, r.x1, r.y1))]) * q["alfa_vidro"]
                reg = reg * (1 - a) + np.float32(q["vidro"]) * a
                a = tela([canto((r.x0, r.y0, r.x1, r.y1))], q["larg_contorno"])
                reg = reg * (1 - a) + np.float32(q["contorno"]) * a
                n_jan += 1
        out[y0:y1, x0w:x1w] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    fachada da {fa['nome']}: {len(paredes)} trechos de parede, {len(folhas)} folhas de correr, "
              f"{n_jan} janelas de banho")
    # brises de bronze
    for r in q["brises"]:
        c = canto(r)
        x0, y0 = np.floor(c.min(axis=0)).astype(int) - 4
        x1, y1 = np.ceil(c.max(axis=0)).astype(int) + 4
        h, w = y1 - y0, x1 - x0

        def tela(polis, linha=None):
            f = np.zeros((h * SS, w * SS), np.uint8)
            for p in polis:
                pp = np.round((p - [x0, y0]) * SS).astype(np.int32)
                if linha is None:
                    cv2.fillConvexPoly(f, pp, 255, cv2.LINE_AA)
                else:
                    cv2.polylines(f, [pp], False, 255, max(1, int(round(linha * SS))), cv2.LINE_AA)
            return cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

        a = tela([c])
        s = q["sombra"]
        out = sombra(out, a, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
        reg = out[y0:y1, x0:x1].astype(np.float32)
        reg = reg * (1 - a[..., None]) + np.float32(q["bronze"]) * a[..., None]
        xm = (r[0] + r[2]) / 2
        a = tela([np.array([p2r(xm, r[1]), p2r(xm, r[3])])], q["larg_bronze_brilho"])[..., None]
        reg = reg * (1 - a) + np.float32(q["bronze_brilho"]) * a
        a = tela([np.array([p2r(r[0], r[1]), p2r(r[0], r[3])]), np.array([p2r(r[2], r[1]), p2r(r[2], r[3])])],
                 q["larg_bronze_borda"])[..., None]
        reg = reg * (1 - a) + np.float32(q["bronze_borda"]) * a
        out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    brises de bronze de ({c[:, 0].min():.1f}, {c[:, 1].min():.1f}) a ({c[:, 0].max():.1f}, {c[:, 1].max():.1f})")
    return out


# item 11: cubas dos banhos das suítes da direita (pedido do usuário: "cuba posicionada mais à direita
# da bancada da pia"). No PDF a cuba fica no lado direito da bancada, junto ao vaso (ARQ_BANCADAS: o
# recorte de 28 x 24 do PDF, centro em x 1259,8 do render); o motor a pôs no meio (centro em 1249,0).
# A cuba do próprio render, com a torneira, vai para o centro do PDF (deslocamento com subpixel, borda
# suave); onde ela estava, o tampo limpo do lado, espelhado, na luz do tampo em volta
CUBAS_BANHOS = [
    {"nome": "banho da suíte de cima", "cuba": (1240, 292, 1258, 307), "dx": 1259.8 - 1249.0, "fonte_x": (1258, 1268)},
    {"nome": "banho da suíte de baixo", "cuba": (1241, 484, 1259, 497), "dx": 1259.7 - 1249.0, "fonte_x": (1259, 1268)},
    # banhos da esquerda, costas com costas (pedido do usuário: "ambas as cubas estão mais à esquerda, do
    # que centralizadas nas bancadas"): no PDF a cuba fica no lado esquerdo da bancada (centro em x 806,5);
    # o motor a centralizou (centro em 816,1)
    {"nome": "banho da esquerda, de cima", "cuba": (807, 609, 825, 623), "dx": 806.45 - 816.1, "fonte_x": (798, 807)},
    {"nome": "banho da esquerda, de baixo", "cuba": (807, 630, 825, 645), "dx": 806.45 - 816.1, "fonte_x": (798, 807)},
]


def cubas_banhos(out, orig):
    for q in CUBAS_BANHOS:
        cx0, cy0, cx1, cy1 = q["cuba"]
        sprite = orig[cy0:cy1, cx0:cx1].copy()
        # o tampo onde a cuba estava: o trecho limpo à direita, nas mesmas linhas, espelhado na horizontal,
        # na luz do tampo interpolada entre as colunas logo à esquerda e logo à direita
        fx0, fx1 = q["fonte_x"]
        fonte = orig[cy0:cy1, fx0:fx1].astype(np.float32)
        h, w = cy1 - cy0, cx1 - cx0
        tex = np.concatenate([fonte, fonte[:, ::-1]] * (w // (2 * fonte.shape[1]) + 1), axis=1)[:, :w]
        tex = tex / tex.mean(axis=1, keepdims=True)
        esq = orig[cy0:cy1, cx0 - 2:cx0].astype(np.float32).mean(axis=1)
        dir_ = orig[cy0:cy1, cx1:cx1 + 2].astype(np.float32).mean(axis=1)
        tt = np.linspace(0, 1, w)[None, :, None]
        luz = esq[:, None, :] * (1 - tt) + dir_[:, None, :] * tt
        out[cy0:cy1, cx0:cx1] = np.clip(tex * luz, 0, 255).astype(np.uint8)
        # a cuba no lugar do PDF: deslocada com subpixel, borda suave de 1 px
        nx0 = int(np.floor(cx0 + q["dx"])) - 1
        W = w + 3
        M = np.float32([[1, 0, cx0 + q["dx"] - nx0], [0, 1, 0]])
        peca = cv2.warpAffine(sprite.astype(np.float32), M, (W, h), flags=cv2.INTER_LINEAR)
        a = np.zeros((h * SS, w * SS), np.float32)
        a[SS:-SS, SS:-SS] = 1
        a = cv2.GaussianBlur(a, (0, 0), 0.6 * SS)
        a = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
        a = cv2.warpAffine(a, M, (W, h), flags=cv2.INTER_LINEAR)[..., None]
        reg = out[cy0:cy1, nx0:nx0 + W].astype(np.float32)
        out[cy0:cy1, nx0:nx0 + W] = np.clip(reg * (1 - a) + peca * a, 0, 255).astype(np.uint8)
        print(f"    {q['nome']}: cuba {abs(q['dx']):.1f} px para a {'direita' if q['dx'] > 0 else 'esquerda'}, "
              f"no centro do PDF")
    return out


# item 12: bancos em frente às camas (pedido do usuário: "faltando os bancos em frente às camas"). O PDF
# tem um banco (ARQ_LAYOUT HUMANIZAÇÃO) no pé de cada cama das cinco suítes, na largura da cama, a 1,6 px
# dela; o motor não desenhou nenhum e fez as camas um pouco mais compridas (3 a 5 px; a da master, 22 px).
# Cada banco fica no pé da cama do render (a linha de sombra do pé, na coluna do meio), com a folga do
# PDF, na largura e na altura do PDF: o banco de madeira aprovado no Térreo (retoque_terreo_casae.
# BANCO_VARANDA: a madeira da mesa de jantar do Térreo, em ripas, contorno e sombra curta), em 3 ripas
BANCOS = {"camada": "ARQ_LAYOUT HUMANIZAÇÃO", "altura_pdf": 22.7, "busca": 32, "folga": 1.0, "ripas": 3}


def bancos_camas(out, pg, p2r):
    from retoque_terreo_casae import BANCO_VARANDA, colar, linha_aa
    q, bv = BANCOS, BANCO_VARANDA
    lay = [d["rect"] for d in pg.get_drawings() if d.get("layer") == q["camada"] and d["type"] == "f"
           and len(d["items"]) == 4]
    bancos = [r for r in lay if abs(r.height - q["altura_pdf"]) < 0.5 and 70 < r.width < 130]
    a, b, c, d = bv["fonte_madeira"]
    madeira = cv2.rotate(cv2.imread(str(TERREO))[b:d, a:c], cv2.ROTATE_90_CLOCKWISE)   # veio no comprido
    L = out.astype(np.float32).mean(axis=2)
    forma = out.shape[:2]
    n = 0
    for B in bancos:
        camas = [r for r in lay if abs(r.width - B.width) < 1.5 and abs(r.x0 - B.x0) < 1.5 and r.height > 80
                 and (abs(r.y1 - B.y0) < 6 or abs(r.y0 - B.y1) < 6)]
        if not camas:
            continue                                   # os aparadores (sem cama encostada) ficam
        cama = camas[0]
        abaixo = abs(cama.y1 - B.y0) < 6               # o banco abaixo da cama (o pé embaixo)
        (bx0, by0), (bx1, by1) = p2r(B.x0, B.y0), p2r(B.x1, B.y1)
        alt = by1 - by0
        xc = int(round((bx0 + bx1) / 2))
        col = L[:, xc - 6:xc + 7].mean(axis=1)
        # pé da cama no render: a primeira queda depois do edredom (abaixo de 88% dele), no mínimo local
        # logo em seguida (a borda do tapete, mais escura, fica mais adiante)
        passo = 1 if abaixo else -1
        ya = int(round(p2r(cama.x0, cama.y1 if abaixo else cama.y0)[1])) - 4 * passo
        edredom = col[ya]
        y = ya
        while abs(y - ya) < q["busca"] and col[y] > 0.88 * edredom:
            y += passo
        janela = [y + k * passo for k in range(4)]
        pe = janela[int(np.argmin([col[v] for v in janela]))]
        if abaixo:
            by0 = pe + q["folga"]
            by1 = by0 + alt
        else:
            by1 = pe - q["folga"] + 1
            by0 = by1 - alt
        ret = (bx0, by0, bx1, by1)
        x0, y0 = int(np.floor(bx0)) - 4, int(np.floor(by0)) - 4
        x1, y1 = int(np.ceil(bx1)) + 4, int(np.ceil(by1)) + 4
        m = np.zeros(((y1 - y0) * SS, (x1 - x0) * SS), np.uint8)
        cv2.rectangle(m, (int(round((bx0 - x0) * SS)), int(round((by0 - y0) * SS))),
                      (int(round((bx1 - x0) * SS)) - 1, int(round((by1 - y0) * SS)) - 1), 255, -1)
        mm = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        s = bv["sombra"]
        out = sombra(out, mm, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
        hh, ww = int(np.ceil(alt)), int(np.ceil(bx1 - bx0))
        out = colar(out, madeira[:hh, :ww], ret)
        for k in range(1, q["ripas"]):
            y = by0 + k * alt / q["ripas"]
            a_ = linha_aa(forma, [(bx0, y), (bx1, y)], bv["larg_junta"])[..., None] * bv["forca_junta"]
            out[:] = np.clip(out * (1 - a_) + np.float32(bv["junta"]) * a_, 0, 255).astype(np.uint8)
        a_ = linha_aa(forma, [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], bv["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a_) + np.float32(bv["contorno"]) * a_, 0, 255).astype(np.uint8)
        n += 1
        print(f"    banco em ({bx0:.1f}, {by0:.1f}) a ({bx1:.1f}, {by1:.1f}); pé da cama do render em {pe}")
    print(f"    {n} bancos de madeira no pé das camas")
    return out


# item 9: shaft (pedido do usuário: "preciso da marcação em x para sinalizar o shaft ... em cor cinza").
# O PDF tem um shaft dentro da parede grossa de cima da suíte master: o retângulo e o X tracejado da
# DOC_LINHAS E PROJEÇÕES (10 segmentos), que somem no preto da parede. Entram em cinza, finos, só
# sobre a parede
SHAFT = {"pdf": (1216.0, 736.5, 1252.5, 754.6), "camada": "DOC_LINHAS E PROJEÇÕES", "cor": (147, 147, 147),
         "largura": 0.6, "parede": 40}


def shaft(out, pg, p2r):
    q = SHAFT
    caixa = pymupdf.Rect(*q["pdf"])
    segs = [(p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)) for d in pg.get_drawings()
            if d.get("layer") == q["camada"] and d["rect"] in caixa for it in d["items"] if it[0] == "l"]
    pts = np.array([p for s in segs for p in s])
    x0, y0 = np.floor(pts.min(axis=0)).astype(int) - 3
    x1, y1 = np.ceil(pts.max(axis=0)).astype(int) + 4
    h, w = y1 - y0, x1 - x0
    f = np.zeros((h * SS, w * SS), np.uint8)
    for (ax, ay), (bx, by) in segs:
        cv2.line(f, (int(round((ax - x0) * SS)), int(round((ay - y0) * SS))),
                 (int(round((bx - x0) * SS)), int(round((by - y0) * SS))), 255,
                 max(1, int(round(q["largura"] * SS))), cv2.LINE_AA)
    a = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    a *= reg.mean(axis=2) < q["parede"]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None], 0, 255).astype(np.uint8)
    print(f"    shaft em ({x0}, {y0}) a ({x1}, {y1}): {len(segs)} traços em cinza")
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
    print("[7] cortinas nas janelas das suítes")
    print("[10] fachadas das suítes: brises de bronze e portas de correr de vidro finas")
    out = fachadas(out, pg, p2r)
    out = cortinas(out, pg, p2r)
    print("[11] cubas dos banhos no lugar do PDF")
    out = cubas_banhos(out, orig)
    print("[12] bancos de madeira no pé das camas")
    out = bancos_camas(out, pg, p2r)
    print("[9] shaft: X em cinza na parede")
    out = shaft(out, pg, p2r)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

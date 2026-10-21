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
   Depois, R3 (regras de 19/10/26, pente fino do 1º Pavimento de 20/10, item 1): os arcos saem todos
   (ARCOS["sem_arco"]); ficam as folhas e os batentes, e a folha da pivotante P1 vista pelo vazio.
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
    mais compridas; a da master, 22 px), estofados em bege (pedidos do usuário): almofadas com o tecido, o
    volume e as costuras da almofada do sofá da sala íntima, trama fina e a sombra curta.
13. Torneira de piso da banheira do banho master (pedido do usuário): a do PDF (base redonda de ~16 cm
    logo fora da borda, no canto de cima à esquerda, e a bica em diagonal sobre a banheira), na mesma
    posição relativa à banheira do render (maior que a do PDF), no cromo aprovado, com sombra curta.
14. Nomes e áreas dos ambientes (pedidos do usuário: nome + área do PDF, na posição e no tamanho do PDF,
    um pouco maior, em preto, legível; no granito marrom, cinza): cada linha dos 23 rótulos do PDF igual
    (texto, posição do PDF, corpo do PDF 30% maior), em Inter Regular preta; os seis que caem sobre móvel
    vão ao piso livre mais próximo (autorizado pelo usuário). Sai também `_sem_rotulos.png`.

Pente fino pelas regras (20/10/26; o mapa está em POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_pente_fino_mapa.jpg):
- item 1, R3: o item 6 deixa de desenhar os arcos (ARCOS["sem_arco"]); a floreira (item 1 de 16/10) passa a vir do
  Térreo aprovado de 15/10 (TERREO_FLOREIRA), de onde ela saiu;
- item 2, escada (R14): o travertino limpo do Térreo aprovado na caixa do PDF e as linhas do `escada_linhas` do Térreo
  (19 pisos, triângulo no topo apontando a descida, esmaecida depois do corte do Térreo, como a escada que desce de lá);
- item 3, boxes em folha contínua de parede a parede (BOXES): o traço do motor sai e entra o vidro do box do Térreo;
- item 10, cortinas como no Térreo (CORTINAS_LINHO): a cortina de linho da biblioteca nos 10 trechos do PDF, no lugar
  das ondas do item 7, com o trilho de parede a parede em cada quarto;
- itens 9 e 7, portas, janelas e vidros finos (ESQUADRIAS_1P): como o item 8 do pente fino do Térreo, nas janelas dos
  banhos, da sala íntima e do vazio do hall, nas folhas das portas e nas portas de correr (a da rouparia, item 7), com a
  parede do render protegida na limpeza e as folhas em branco com contorno fino;
- item 11, vinílico na escala (VINILICO): réguas de 20 cm desenhadas com o veio do próprio vinílico do render, na luz e
  no tom do lugar, e o vinílico escurecido mais claro;
- item 4, banhos 3 e 4 (BANHOS_34): sem os discos, os registros e a cápsula do motor; os dois nichos, as duchas
  quadradas com o braço da parede do meio e os dois vasos suspensos, costas com costas, do PDF, como no Subsolo;
- item 5, guarda-roupas com cabides (GUARDA_ROUPAS, R11): o closet master e os closets 1 a 4, abertos, vistos de cima,
  com as portas do lado do closet;
- item 6, projeções em tracejado (PROJECOES_1P, R8): o shaft entre o elevador e a rouparia (vão branco com o X), o
  retângulo com X da rouparia e os X rasos do fundo do banho master;
- item 8, soleiras (SOLEIRAS_1P, R13): nos vãos brancos do PDF (banhos 1 a 4, banho master e rouparia), em Bege
  Bahia, com as faces da parede em cinza fino; nas suítes o vinílico atravessa;
- item 16, quartzito dos banhos como a referência do quadro de 19/10 (`_texturas/originais/quartzito_aura.jpg`): a
  parte pêssego de cada px vai ao tom da foto, e a chapa da biblioteca entra na escala, só na luz (QUARTZITO).

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
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))

from retoque_terreo_casad import CHUVEIROS_BHM  # noqa: E402
from retoque_terreo_casac import CHUVEIRO_TETO, CROMO, CROMO_CLARO, CROMO_ESCURO, SS  # noqa: E402
from retoque_subsolo_casad import apagar_largo  # noqa: E402
from retoque_terreo_casad import textura  # noqa: E402

BASE = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png"
TERREO = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado.png"
# a fonte da floreira (item 1) é o Térreo aprovado de 15/10, de onde ela saiu: o retocado do Térreo mudou depois
# (pente fino de 20/10, jardim só no verde), e a floreira mudaria junto, fora do item pedido
TERREO_FLOREIRA = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado_aprovado.png"
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
    t = cv2.imread(str(TERREO_FLOREIRA))[fy0:fy1, fx0:fx1]
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
# R3 (regras de 19/10/26: "Nunca mostrar o arco da porta"; pente fino do 1º Pavimento, 20/10/26, item 1): com
# "sem_arco", os arcos não são desenhados (o motor não fez nenhum: volta o piso do render) e fica só a folha da
# pivotante P1 do hall
ARCOS = {"cor": (160, 161, 160), "larg": 0.45, "min_px": 6, "parede": 45, "sem_arco": True,
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
        if q["sem_arco"] or d.get("layer") != "ARQ_PAREDE" or not any(it[0] == "c" for it in d["items"]):
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
    print(f"    {n} arcos de porta em cinza fino" + (" (R3: sem arcos)" if q["sem_arco"] else ""))
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


# item 10 do pente fino de 20/10/26: cortinas como no Térreo (usuário: "representar as cortinas da mesma forma que fizemos
# no terreo"). O item 7 (as ondas do PDF em zigue-zague branco) dá lugar à cortina de linho da biblioteca
# (`_blocos/blocos.cortina`, aprovada em 20/10), posta com o `pousar_cortina` do Térreo: em cada um dos 10 trechos de linha
# ondulada do PDF, o pano (com o eixo do tecido no eixo da linha do PDF, na mesma extensão: a meia distância, como lá) e,
# em cada quarto, o trilho de parede a parede, do lado do vidro (regra de 20/10: "trilhos da cortina tem que ser de fora
# a fora"). O fim do trilho é a parede preta do render ao longo da cortina, numa coluna "dentro" px para dentro do quarto
# ("parede": média abaixo disso, em "seguidos" px); os trilhos do mesmo lado que se sobrepõem viram um só. O vidro fica à esquerda na fachada da esquerda e à direita na da direita.
CORTINAS_LINHO = {"parede": 55, "seguidos": 3, "busca_m": 6.0, "dentro": 3}


def trechos_cortina(pg):
    """Os trechos de linha ondulada do PDF (arcos que se tocam), cada um como os pontos de controle em pt."""
    q = CORTINAS
    arcos = [d for d in pg.get_drawings() if d.get("layer") == q["camada"] and d.get("color") == (0.0, 0.0, 0.0)
             and abs((d.get("width") or 0) - q["traco_pdf"]) < 0.01]
    trechos = []
    for d in arcos:
        b = pymupdf.Rect(d["rect"]) + (-1.5, -1.5, 1.5, 1.5)
        for t in trechos:
            if any(b.intersects(e["rect"]) for e in t):
                t.append(d)
                break
        else:
            trechos.append([d])
    out = []
    for t in trechos:
        pts = np.array([(v.x, v.y) for d in t for it in d["items"] for v in it[1:] if hasattr(v, "x")])
        out.append(pts)
    return out


def cortinas_linho(out, pg, p2r):
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    from retoque_terreo_casae import pousar_cortina
    q = CORTINAS_LINHO
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    k = 8
    busca = int(q["busca_m"] * px_m)
    panos, trilhos = [], []
    for pts in trechos_cortina(pg):
        xe = float(np.median(pts[:, 0]))                     # o eixo do tecido (as ondas são verticais nas fachadas)
        (ex, ey0), (_, ey1) = p2r(xe, float(pts[:, 1].min())), p2r(xe, float(pts[:, 1].max()))
        vidro = "esquerda" if xe < 1700 else "direita"
        # a coluna da busca, um pouco para dentro do quarto: no eixo do tecido, colado ao vidro, os montantes escuros das
        # folhas de correr paravam a busca antes da parede
        dentro = int(round(ex)) + (q["dentro"] if vidro == "esquerda" else -q["dentro"])
        escuro = out[:, dentro].astype(np.float32).mean(axis=1) < q["parede"]

        def ate_parede(y, passo):
            n = 0
            for yy in range(int(round(y)), int(round(y)) + passo * busca, passo):
                n = n + 1 if escuro[yy] else 0
                if n >= q["seguidos"]:
                    return yy - passo * (q["seguidos"] - 1) - passo * 0.5
            return y
        panos.append((vidro, ex, ey0, ey1))
        trilhos.append([vidro, ex, ate_parede((ey0 + ey1) / 2, -1), ate_parede((ey0 + ey1) / 2, +1)])
    # o trilho de cada quarto: os do mesmo lado que se sobrepõem viram um só, de parede a parede (a busca de um pano pode
    # parar antes, num objeto escuro junto à fachada)
    unidos = []
    for v, ex, t0, t1 in sorted(trilhos, key=lambda t: (t[0], t[2])):
        if unidos and unidos[-1][0] == v and t0 < unidos[-1][3] - 2:
            unidos[-1][2], unidos[-1][3] = min(unidos[-1][2], t0), max(unidos[-1][3], t1)
        else:
            unidos.append([v, ex, t0, t1])
    for v, ex, t0, t1 in unidos:
        cor, al = blocos.cortina((t1 - t0) / px_m, px_m * k, com_pano=False)
        pousar_cortina(out, cor, al, ex, t0, k, v)
    for v, ex, ey0, ey1 in panos:
        cor, al = blocos.cortina((ey1 - ey0) / px_m, px_m * k, com_trilho=False)
        pousar_cortina(out, cor, al, ex, ey0, k, v)
    print(f"    {len(panos)} panos de linho nos trechos do PDF e {len(unidos)} trilhos de parede a parede: "
          + ", ".join(f"{v} y {t0:.0f} a {t1:.0f}" for v, _, t0, t1 in unidos))
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
# PDF, na largura e na altura do PDF. Primeiro entrou o banco de madeira em ripas do Térreo; a pedido do
# usuário ficou estofado em bege, com a sombra curta do banco do Térreo (BANCO_VARANDA)
BANCOS = {"camada": "ARQ_LAYOUT HUMANIZAÇÃO", "altura_pdf": 22.7, "busca": 32, "folga": 1.0,
          # estofado bege (pedidos do usuário: "use o tom bege"; "precisam ter textura de estofados"):
          # almofadas lado a lado com o tecido, o volume e as costuras da almofada do meio do assento do
          # sofá da sala íntima do próprio render (normalizada, no bege), na proporção dela (uma almofada a
          # cada 1,7 vez a altura do banco), e um contorno bege escuro, fino
          # mais uma trama fina de tecido (ruído suave, 4%), para o estofado não ficar liso
          "bege": (156, 182, 207), "fonte_almofada": (1001, 633, 1034, 654), "proporcao": 1.7, "relevo": 1.8,
          "trama": (0.04, 0.5), "semente": 642,
          "contorno": (112, 132, 156), "larg_contorno": 0.45}


def bancos_camas(out, pg, p2r):
    from retoque_terreo_casae import BANCO_VARANDA, colar, linha_aa
    q, bv = BANCOS, BANCO_VARANDA
    lay = [d["rect"] for d in pg.get_drawings() if d.get("layer") == q["camada"] and d["type"] == "f"
           and len(d["items"]) == 4]
    bancos = [r for r in lay if abs(r.height - q["altura_pdf"]) < 0.5 and 70 < r.width < 130]
    fx0, fy0, fx1, fy1 = q["fonte_almofada"]
    almofada = out[fy0:fy1, fx0:fx1].astype(np.float32)
    almofada = 1 + q["relevo"] * (almofada / almofada.reshape(-1, 3).mean(axis=0) - 1)
    L = out.astype(np.float32).mean(axis=2)
    forma = out.shape[:2]
    rng = np.random.default_rng(q["semente"])
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
        hh, ww = int(np.ceil(alt)) * SS, int(np.ceil(bx1 - bx0)) * SS
        secoes = max(1, int(round((bx1 - bx0) / (q["proporcao"] * alt))))
        cortes = np.linspace(0, ww, secoes + 1).astype(int)
        peca = np.concatenate([cv2.resize(almofada, (int(b_ - a_), hh), interpolation=cv2.INTER_CUBIC)
                               for a_, b_ in zip(cortes[:-1], cortes[1:])], axis=1)
        amp, sig = q["trama"]
        trama = cv2.GaussianBlur(rng.normal(0, 1, (hh, ww)).astype(np.float32), (0, 0), sig * SS)
        trama = 1 + amp * trama / max(trama.std(), 1e-6)
        peca = np.clip(peca * trama[..., None] * np.float32(q["bege"]), 0, 255)
        peca = cv2.resize(peca, (ww // SS, hh // SS), interpolation=cv2.INTER_AREA)
        out = colar(out, peca, ret)
        a_ = linha_aa(forma, [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a_) + np.float32(q["contorno"]) * a_, 0, 255).astype(np.uint8)
        n += 1
        print(f"    banco em ({bx0:.1f}, {by0:.1f}) a ({bx1:.1f}, {by1:.1f}), {secoes} almofadas; pé da cama do render em {pe}")
    print(f"    {n} bancos estofados em bege no pé das camas")
    return out


# item 13: torneira de piso da banheira do banho master (pedido do usuário: "faltou a torneira de piso da
# banheira"). No PDF (ARQ_LOUÇAS E METAIS) ela fica no canto de cima, à esquerda, da banheira: a base
# redonda (9 de diâmetro, ~16 cm) logo fora da borda e a bica em diagonal sobre a banheira. A banheira do
# render é maior que a do PDF; a base vai à mesma posição relativa ao contorno dela (a elipse ajustada ao
# branco da banheira), no tamanho do PDF, no cromo aprovado e com a sombra curta das placas de teto
TORNEIRA_BANHEIRA = {"banheira_pdf": (1588.2, 657.7, 1639.0, 753.2), "base_pdf": (1591.3, 655.9, 1600.3, 664.9),
                     "bica_pdf": (1595.1, 659.6, 1607.6, 672.1), "janela": (925, 225, 990, 315),
                     "alavanca": 2.0, "larg_bica": 0.9, "larg_alavanca": 0.7}


def torneira_banheira(out, p2r):
    q = TORNEIRA_BANHEIRA
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    branco = ((reg.mean(axis=2) > 200) & (reg.max(axis=2) - reg.min(axis=2) < 30)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(branco)
    m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    m = ndimage.binary_fill_holes(cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    (ecx, ecy), (ew, eh), _ = cv2.fitEllipse(max(cs, key=cv2.contourArea))
    ecx, ecy, ea, eb = ecx + wx0, ecy + wy0, ew / 2, eh / 2
    (b0x, b0y), (b1x, b1y) = p2r(*q["banheira_pdf"][:2]), p2r(*q["banheira_pdf"][2:])
    pcx, pcy, pa, pb = (b0x + b1x) / 2, (b0y + b1y) / 2, (b1x - b0x) / 2, (b1y - b0y) / 2
    (s0x, s0y), (s1x, s1y) = p2r(*q["base_pdf"][:2]), p2r(*q["base_pdf"][2:])
    bcx, bcy, raio = (s0x + s1x) / 2, (s0y + s1y) / 2, (s1x - s0x) / 2
    k1x, k1y = p2r(*q["bica_pdf"][2:])
    bica = np.array([k1x - bcx, k1y - bcy])                       # da base à ponta da bica (para baixo e à direita)
    # a base na mesma posição relativa à elipse da banheira do render
    tx, ty = ecx + (bcx - pcx) / pa * ea, ecy + (bcy - pcy) / pb * eb
    ux = bica / np.linalg.norm(bica)
    ponta = np.array([tx, ty]) + bica
    alav = np.array([tx, ty]) - ux * q["alavanca"]
    x0, y0 = int(np.floor(min(tx - raio, alav[0]))) - 4, int(np.floor(min(ty - raio, alav[1]))) - 4
    x1, y1 = int(np.ceil(ponta[0])) + 5, int(np.ceil(ponta[1])) + 5
    h, w = y1 - y0, x1 - x0
    cor = np.zeros((h * SS, w * SS, 3), np.float32)
    alfa = np.zeros((h * SS, w * SS), np.float32)

    def p(v):
        return int(round((v[0] - x0) * SS)), int(round((v[1] - y0) * SS))

    def pinta(forma, c):
        mm = forma > 0
        cor[mm] = c
        alfa[mm] = 1

    def linha(a, b, larg, c):
        f = np.zeros(alfa.shape, np.uint8)
        cv2.line(f, p(a), p(b), 255, max(1, int(round(larg * SS))), cv2.LINE_8)
        pinta(f, c)

    def circulo(c0, r, c):
        f = np.zeros(alfa.shape, np.uint8)
        cv2.circle(f, p(c0), max(1, int(round(r * SS))), 255, -1, cv2.LINE_8)
        pinta(f, c)

    base = np.array([tx, ty])
    linha(base, ponta, q["larg_bica"], CROMO_ESCURO)                # bica
    linha(base, ponta, q["larg_bica"] * 0.6, CROMO)
    linha(base, ponta - ux * 0.3, q["larg_bica"] * 0.22, CROMO_CLARO)
    circulo(ponta, q["larg_bica"] * 0.6, CROMO_ESCURO)
    circulo(base, raio, CROMO_ESCURO)                              # base redonda
    circulo(base, raio * 0.82, CROMO)
    circulo(base - ux * raio * 0.3, raio * 0.35, CROMO_CLARO)
    linha(base, alav, q["larg_alavanca"], CROMO_ESCURO)            # alavanca
    linha(base, alav, q["larg_alavanca"] * 0.55, CROMO)
    a = cv2.resize(alfa, (w, h), interpolation=cv2.INTER_AREA)
    c = cv2.resize(cor * alfa[..., None], (w, h), interpolation=cv2.INTER_AREA) / np.maximum(a[..., None], 1e-6)
    s = CHUVEIROS_BHM["sombra"]
    out = sombra(out, a, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + c * a[..., None], 0, 255).astype(np.uint8)
    print(f"    banheira do render: elipse em ({ecx:.1f}, {ecy:.1f}), semi-eixos {ea:.1f} x {eb:.1f} "
          f"(PDF {pa:.1f} x {pb:.1f}); torneira em ({tx:.1f}, {ty:.1f}), base de {2 * raio:.1f} px")
    return out


# item 14: nomes e áreas dos ambientes (pedido do usuário: "insira as cotas nos ambientes"; escolheu
# "nome + área do PDF"; depois: "tem que ficar no tamanho de como está no PDF"; "na cor preta; no granito
# marrom, cinza"; "um pouco maior a fonte"; "na mesma posição [do PDF] e com leitura visível"). Cada linha
# do rótulo do PDF entra igual: o mesmo texto ("SUÍTE 1", "A: 17 m" e o "2" sobrescrito), na mesma posição
# (a origem da linha no PDF) e no corpo do PDF (8 pt; 5,3 pt no "2") levado à escala da imagem e 30%
# maior, em Inter Regular, desenhado em 4x e reduzido, em preto; os que caem sobre móvel vão ao piso livre
ROTULOS = {"fonte": "Regular", "ss": 4,
           # cor (pedido do usuário): preto no piso; no granito marrom, cinza (neste pavimento não há granito)
           "cor": (20, 20, 20), "cor_granito": (150, 150, 150),
           # regra R6 (usuário, 19/10/26: "Apresentar os rótulos em branco quando for piso marrom granito"): o branco
           # que os pavimentos passam a usar, um por vez (cor_granito=ROTULOS["branco"])
           "branco": (250, 250, 250),
           # corpo um pouco maior que o do PDF (pedido do usuário: "e um pouco maior a fonte")
           "escala": 1.3,
           # o "2" do m²: logo depois do fim do "m" medido na Inter, com esta folga (fração do corpo da linha), na
           # altura do PDF (pente fino do Térreo da Casa E, 20/10/26: na posição do PDF, ele encostava no "m" quando
           # os números eram largos e se afastava com os "1" estreitos, como em "7,11")
           "folga_m2": 0.07,
           # (nome, centro do rótulo do PDF no render de 2000 px, desvio em px desse render)
           # na posição do PDF (pedido do usuário: "preciso que estejam na mesma posição e com leitura
           # visível"); os que caem sobre móvel vão ao piso livre mais próximo ("nesses casos em que o escrito
           # fica sobre algum mobiliário, está autorizado deslocar para outro local do piso"):
           # (nome, centro do rótulo do PDF no render de 2000 px, desvio em px desse render)
           "ajustes": [("SUÍTE MASTER", (813.7, 395.2), (6, 26)),       # sobre o banco: abaixo, fora do tapete e do pufe
                       # na ponta da banheira; logo abaixo (8) ainda encostava nela (usuário, 20/10/26: "O escrito do
                       # banho master não pode ficar sobre a banheira"): no meio do piso livre entre ela e o box
                       ("BANHO MASTER", (961.0, 302.1), (0, 35)),
                       # colado no vaso, logo acima (usuário, 20/10/26: "afasta um pouco o rótulo do sanitário"): no
                       # meio do piso livre até a parede de baixo, com a folga do banho 4 até o vaso dele (~15 px de 3840)
                       ("BANHO 3", (785.1, 659.4), (0, 7)),
                       ("SALA ÍNTIMA", (949.1, 670.9), (-13, 0)),       # no braço do sofá: à esquerda
                       ("CLOSET 2", (1192.8, 319.8), (4, 0)),           # na borda do armário: à direita
                       ("CLOSET 3", (873.5, 655.2), (-5, 0)),           # na borda do armário: à esquerda
                       ("COPINHA", (1107.1, 482.9), (0, -20))]}         # sobre a bancada: no piso em frente


def rotulos_pdf(pg):
    """Os rótulos dos ambientes do PDF: o nome, as linhas logo abaixo ("A: 17 m" e o "2") e o centro do
    bloco; cada linha com o texto, o corpo (pt) e a origem (pontos do PDF)."""
    spans = [(s["text"].strip(), s["size"], pymupdf.Rect(s["bbox"]), s["origin"])
             for b in pg.get_text("dict")["blocks"] for li in b.get("lines", []) for s in li["spans"]
             if s["text"].strip()]
    out = []
    for i, (t, tam, r, o) in enumerate(spans):
        if tam < 7.5 or t.startswith("A:") or not any(c.isalpha() for c in t) or "PAVIMENTO" in t or "ESC." in t:
            continue
        linhas, caixa = [(t, tam, o)], pymupdf.Rect(r)
        if i + 1 < len(spans) and spans[i + 1][0].startswith("A:") and spans[i + 1][2].y0 - r.y1 < 2:
            linhas.append((spans[i + 1][0], spans[i + 1][1], spans[i + 1][3]))
            caixa |= spans[i + 1][2]
            if i + 2 < len(spans) and spans[i + 2][0] == "2" and spans[i + 2][1] < 6:
                linhas.append((spans[i + 2][0], spans[i + 2][1], spans[i + 2][3]))
        out.append((t, linhas, ((caixa.x0 + caixa.x1) / 2, (caixa.y0 + caixa.y1) / 2), caixa))
    # nome em duas linhas no PDF ("LIVING E SALA DE" / "JANTAR"): a linha de cima, sozinha e logo acima da
    # outra, entra no mesmo rótulo (separadas, cada parte crescia em volta do próprio centro e se encostavam)
    juntos = []
    for r in out:
        if juntos:
            t0, l0, _, k0 = juntos[-1]
            t1, l1, _, k1 = r
            if len(l0) == 1 and 0 <= k1.y0 - k0.y1 < 3 and abs((k0.x0 + k0.x1) / 2 - (k1.x0 + k1.x1) / 2) < 10:
                k = pymupdf.Rect(k0) | k1
                juntos[-1] = (f"{t0} {t1}", l0 + l1, ((k.x0 + k.x1) / 2, (k.y0 + k.y1) / 2), k)
                continue
        juntos.append(r)
    return juntos


def rotulos_ambientes(img, rotulos, pdf2img, escala_desvio=None, granito=None, ajustes=None, cor_granito=None):
    """Escreve os rótulos do PDF na imagem (BGR), no corpo do PDF levado à escala dela (pdf2img leva um
    ponto do PDF à imagem); granito: máscara (bool, no quadro da imagem) do granito marrom, onde o texto
    fica cinza; ajustes: os desvios de outro pavimento (o padrão é o deste). Cada ajuste é (nome, centro em
    px de 2000, desvio em px de 2000[, opções]); as opções são o corpo (um número) ou um dicionário com
    "corpo", "quebra" (o nome em mais linhas, cada uma centrada no nome do PDF, para ambiente estreito) e
    "cor"."""
    from PIL import Image, ImageDraw, ImageFont
    from rodape_entrega import FONTES
    q = ROTULOS
    H, W = img.shape[:2]
    escala_desvio = W / 2000 if escala_desvio is None else escala_desvio
    (ax_, ay_), (bx_, by_) = pdf2img(0, 0), pdf2img(100, 0)
    px_pt = np.hypot(bx_ - ax_, by_ - ay_) / 100                # px da imagem por ponto do PDF
    ss = q["ss"]
    out = img.astype(np.float32)
    for nome, linhas, (pcx, pcy), caixa in rotulos:
        cx, cy = pdf2img(pcx, pcy)
        dx, dy, e, opc = 0.0, 0.0, q["escala"], {}
        # um ajuste pode trazer também o corpo do rótulo (o do PDF, 1.0, onde o 1,3x não cabe no piso livre)
        for n, (axx, ayy), d, *extra in (q["ajustes"] if ajustes is None else ajustes):
            if n == nome and np.hypot(cx - axx * W / 2000, cy - ayy * W / 2000) < 25 * W / 2000:
                dx, dy = d[0] * escala_desvio, d[1] * escala_desvio
                opc = extra[0] if extra and isinstance(extra[0], dict) else ({"corpo": extra[0]} if extra else {})
                e = opc.get("corpo", e)
        linhas = [(t, tam, o, "ls") for t, tam, o in linhas]
        if "quebra" in opc:
            # o nome em mais linhas, centradas no nome do PDF, no espaçamento do nome à área; o bloco fica
            # centrado no mesmo ponto
            _, tam0, (_, oy0), _ = linhas[0]
            passo = linhas[1][2][1] - oy0 if len(linhas) > 1 else 1.33 * tam0
            extra_n = len(opc["quebra"]) - 1
            sobe, xm = extra_n * passo / 2, (caixa.x0 + caixa.x1) / 2
            linhas = ([(p, tam0, (xm, oy0 - sobe + k * passo), "ms") for k, p in enumerate(opc["quebra"])]
                      + [(t, tam, (ox, oy - sobe + extra_n * passo), a) for t, tam, (ox, oy), a in linhas[1:]])
            caixa = pymupdf.Rect(caixa.x0, caixa.y0 - sobe, caixa.x1, caixa.y1 + sobe)
        (x0, y0), (x1, y1) = pdf2img(caixa.x0, caixa.y0), pdf2img(caixa.x1, caixa.y1)
        x0, x1 = cx + (x0 - cx) * e, cx + (x1 - cx) * e
        y0, y1 = cy + (y0 - cy) * e, cy + (y1 - cy) * e
        # folga larga: a Inter é mais larga que a fonte do PDF (sem ela, "CLOSET MASTER" saía cortado)
        fx, fy = 0.35 * (x1 - x0) + 4, 0.35 * (y1 - y0) + 4
        x0, y0 = int(np.floor(x0 + dx - fx)), int(np.floor(y0 + dy - fy))
        x1, y1 = int(np.ceil(x1 + dx + fx)), int(np.ceil(y1 + dy + fy))
        tela = Image.new("L", ((x1 - x0) * ss, (y1 - y0) * ss), 0)
        d = ImageDraw.Draw(tela)
        fim_area = None                                            # onde termina o "A: ... m" (px de ss)
        for texto, tam, (ox, oy), ancora in linhas:
            corpo = max(4, int(round(tam * px_pt * e * ss)))
            f = ImageFont.truetype(str(FONTES / f"Inter-{q['fonte']}.otf"), corpo)
            gx, gy = pdf2img(ox, oy)
            gx, gy = cx + (gx - cx) * e, cy + (gy - cy) * e          # as linhas afastam na mesma escala
            px_, py_ = (gx + dx - x0) * ss, (gy + dy - y0) * ss
            if texto == "2" and fim_area is not None:               # o "2" do m², logo depois do "m"
                px_ = fim_area[0] + q["folga_m2"] * fim_area[1]
            d.text((px_, py_), texto, font=f, fill=255, anchor=ancora)
            fim_area = (px_ + d.textlength(texto, font=f), corpo) if texto.startswith("A:") and ancora == "ls" \
                else None
        a = np.asarray(tela.resize((x1 - x0, y1 - y0), Image.LANCZOS), np.float32)[..., None] / 255
        no_granito = granito is not None and granito[max(y0, 0):y1, max(x0, 0):x1].mean() > 0.5
        cor = np.float32(opc.get("cor", (cor_granito or q["cor_granito"]) if no_granito else q["cor"]))
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + cor * a
    return np.clip(out, 0, 255).astype(np.uint8)


# item 2 do pente fino de 20/10/26: escada com linhas e o triângulo de orientação (regras de 19/10: "escadas com linhas",
# R14; e, de 20/10, a do Térreo: "o esmaecimento parcial da escada que desce, a partir da linha diagonal discriminada no
# PDF base"). O motor desenhou ~10 degraus, e o PDF tem 19 pisos mais o patamar (a mesma escada do Térreo, mesma caixa e
# mesmos bocéis nos dois PDFs). Ela desce da esquerda para a direita (o "D" do PDF à esquerda; no Térreo, sobe da direita
# para a esquerda).
# - o piso: o travertino limpo do Térreo aprovado logo abaixo do jardim (veio no sentido dos pisos), na caixa do PDF, como
#   a limpeza da escada do Térreo (itens 18 e 21 de lá), com borda suave;
# - as linhas: `retoque_terreo_casae.escada_linhas`, com a cadeia deste PDF: bocel em linha suave e sombra curta no degrau
#   de baixo (à direita), o triângulo no topo (à esquerda) apontando a descida; o PDF deste pavimento não tem corte, e,
#   como na escada que desce do Térreo, ela fica viva até o corte do outro pavimento (o do Térreo, entre o 7º e o 8º
#   degrau, contados da direita) e esmaecida depois (0,45, com os bocéis e as sombras, sem tracejado: fica por baixo)
ESCADA = {"fonte": (600, 976),     # linha e coluna do Térreo aprovado que caem no canto de cima, à esquerda, da escada
          "linhas": {"nome": "interna, desce da esquerda para a direita", "pdf": (1659.2, 1138.5, 1984.0, 1221.4),
                     "bocels": [1677.9 + 17.0 * k for k in range(18)], "baixo": "direita", "inicio": "esquerda",
                     "corte": [(1840.5, 1138.5), (1859.3, 1176.2), (1863.1, 1183.8), (1882.2, 1222.0)],
                     "viva": "esquerda", "apos": "esmaecida", "esmaecer": 0.45}}


def escada_r14(out, p2r):
    from retoque_terreo_casae import escada_linhas
    q = ESCADA
    e = q["linhas"]
    ex0, ey0, ex1, ey1 = e["pdf"]
    canto = np.array([p2r(ex0, ey0), p2r(ex1, ey0), p2r(ex1, ey1), p2r(ex0, ey1)])
    x0, y0 = np.floor(canto.min(axis=0)).astype(int) - 2
    x1, y1 = np.ceil(canto.max(axis=0)).astype(int) + 2
    m = np.zeros(((y1 - y0) * SS, (x1 - x0) * SS), np.uint8)
    cv2.fillConvexPoly(m, np.round((canto - [x0, y0]) * SS).astype(np.int32), 255, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)[..., None]
    ax, ay = canto[0]
    fr, fc = q["fonte"]
    t = cv2.imread(str(TERREO_FLOREIRA))
    r0, c0 = fr + (y0 - int(round(ay))), fc + (x0 - int(round(ax)))
    src = t[r0:r0 + (y1 - y0), c0:c0 + (x1 - x0)].astype(np.float32)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + src * a, 0, 255).astype(np.uint8)
    print(f"    escada: travertino limpo do Térreo aprovado na caixa do PDF ({x0}, {y0}) a ({x1}, {y1})")
    return escada_linhas(out, None, e, p2r=p2r)


# item 3 do pente fino de 20/10/26: boxes em folha contínua, de parede a parede (R10: "Folha contínua também no 1º
# Pavimento da Casa E, onde o box está incompleto"; usuário: "complementar os boxes de banhos de forma contínua, fora a
# fora"). No PDF (ARQ_LOUÇAS E METAIS) cada box vai de uma parede à outra; o motor fez só trechos (nos banhos 1 e 2, até o
# meio; nos 3 e 4, sem as pontas; no master, falhado). O traço do motor sai (numa faixa de 2,5 px em volta do eixo do
# PDF, cada px que foge da média dos dois lados, a 5 px, vira essa média) e entra o vidro do box do banho gourmet do
# Térreo: linha clara fina, sem montantes nem marcas no meio, com a borda cinza fina e a sombra suave do lado do
# chuveiro. Eixo do vidro e lado do chuveiro (+1: x ou y crescente) em pt do PDF
BOXES = {"boxes": [("banho master", (1621.7, 907.5, 1719.8, 907.5), +1),
                   ("banho 2", (2247.2, 764.9, 2247.2, 865.8), +1),
                   ("banho 1", (2247.5, 1113.6, 2247.5, 1214.5), +1),
                   ("banho 4", (1276.4, 1286.5, 1276.4, 1370.4), -1),
                   ("banho 3", (1276.4, 1382.9, 1276.4, 1466.8), -1)],
         "faixa": 2.5, "lado": 5, "foge": 12,
         "vidro": (226, 229, 230), "larg": 0.8, "borda": (150, 153, 155), "larg_borda": 0.3,
         "sombra": {"d": 1.2, "sigma": 1.0, "forca": 0.22}}


def boxes_continuos(out, p2r):
    from retoque_terreo_casae import linha_aa
    q = BOXES
    forma = out.shape[:2]
    for nome, (fx0, fy0, fx1, fy1), lado in q["boxes"]:
        (a, b), (c, d) = p2r(fx0, fy0), p2r(fx1, fy1)
        vert = abs(c - a) < abs(d - b)
        im = out.astype(np.float32)
        # o traço do motor: na faixa do eixo, o que foge da média dos dois lados
        if vert:
            xc = (a + c) / 2
            ys = np.arange(int(np.floor(min(b, d))), int(np.ceil(max(b, d))) + 1)
            for xx in range(int(np.floor(xc - q["faixa"])), int(np.ceil(xc + q["faixa"])) + 1):
                viz = (im[ys, xx - q["lado"]] + im[ys, xx + q["lado"]]) / 2
                foge = np.abs(im[ys, xx] - viz).max(axis=1) > q["foge"]
                im[ys[foge], xx] = viz[foge]
        else:
            yc = (b + d) / 2
            xs = np.arange(int(np.floor(min(a, c))), int(np.ceil(max(a, c))) + 1)
            for yy in range(int(np.floor(yc - q["faixa"])), int(np.ceil(yc + q["faixa"])) + 1):
                viz = (im[yy - q["lado"], xs] + im[yy + q["lado"], xs]) / 2
                foge = np.abs(im[yy, xs] - viz).max(axis=1) > q["foge"]
                im[yy, xs[foge]] = viz[foge]
        out = np.clip(im, 0, 255).astype(np.uint8)
        # o vidro, de parede a parede, com a sombra e a borda do lado do chuveiro
        def eixo(desl):
            return ([(a + desl, b), (c + desl, d)] if vert else [(a, b + desl), (c, d + desl)])
        s = q["sombra"]
        sm = cv2.GaussianBlur(linha_aa(forma, eixo(lado * s["d"]), q["larg"]), (0, 0), s["sigma"])
        out = np.clip(out * (1 - s["forca"] * sm)[..., None], 0, 255).astype(np.uint8)
        al = linha_aa(forma, eixo(0), q["larg"])[..., None]
        out = np.clip(out * (1 - al) + np.float32(q["vidro"]) * al, 0, 255).astype(np.uint8)
        al = linha_aa(forma, eixo(lado * q["larg"] / 2), q["larg_borda"])[..., None]
        out = np.clip(out * (1 - al) + np.float32(q["borda"]) * al, 0, 255).astype(np.uint8)
        print(f"    box do {nome}: vidro contínuo de ({a:.1f}, {b:.1f}) a ({c:.1f}, {d:.1f})")
    return out


# itens 9 e 7 do pente fino de 20/10/26: portas, janelas e vidros finos (usuário, 21/10: "melhorar as representações de
# portas e janelas e vidros"), como o item 8 do pente fino do Térreo (`retoque_terreo_casae.esquadria_desenhar`): os
# brancos finos da ARQ_PAREDE de cada zona abaixo (vidros, folhas e caixilhos) são limpos numa faixa de 3 px
# (`esquadria_limpar_1p`, com a parede do render protegida; opções por zona: "faixa" de cada lado, "fonte" de um lado
# só, "vao" para as peças largas e "extra" para limpar antes) e redesenhados pelo PDF, em 8x: paredes em preto,
# peitoril em Bege Bahia onde há vidro no vão, caixilho em alumínio claro, vidro no vidro aprovado, os traços do PDF em
# cinza médio fino; por fim, as folhas (1,6 a 2,5 pt) em branco suave com contorno fino, como as portas do Subsolo da
# Casa E. Entram as janelas com caixilho largo e cinza do motor (banho master, banhos 1 e 2, sala íntima e vazio do
# hall), as folhas das portas de giro (suítes, banhos e closet master), as portas de correr do banho master (embutida)
# e do closet master, e a da rouparia (item 7: o render tinha só duas peças cinza nos batentes). Ficam as fachadas das
# suítes, refeitas em 16/10 (item 10), a folha da pivotante do vazio (item 6), as portas do elevador e os retângulos
# brancos nas paredes dos banhos.
ESQUADRIAS_1P = {"zonas": [("janela do banho master (E24)", (1529.0, 653.0, 1538.0, 722.0)),
                           ("janela do banho 2 (E23)", (2306.0, 786.0, 2317.0, 845.0), {"faixa": (3, 1)}),
                           ("janela do banho 1 (E23)", (2306.0, 1134.0, 2317.0, 1194.0), {"faixa": (3, 1)}),
                           ("janela da sala íntima (E17)", (1538.0, 1593.0, 1620.0, 1605.0)),
                           ("janela da sala íntima (E20)", (1886.0, 1696.0, 1985.0, 1710.0)),
                           ("janelas do vazio do hall (E8 e E9)", (2086.0, 1646.0, 2243.0, 1735.0), {"faixa": (1, 3)}),
                           ("porta do closet master (P13)", (1725.0, 783.0, 1738.0, 876.0),
                            {"vao": {"faixa": (3, 0), "fonte": "antes"},
                             "extra": [((1734.6, 816.5, 1743.5, 843.0), (0, 1), "depois")]}),
                           ("portas do banho master (P11 e P12)", (1529.0, 805.0, 1547.0, 961.0)),
                           ("portas dos banhos 2 e 1", (2119.0, 858.0, 2172.0, 1212.0)),
                           ("portas das suítes", (1478.0, 1057.0, 1532.0, 1484.0)),
                           ("portas das suítes 2 e 1", (1991.0, 1085.0, 2045.0, 1448.0)),
                           ("portas dos banhos 4 e 3", (1356.0, 1289.0, 1404.0, 1464.0)),
                           ("porta de correr da rouparia (P10)", (1877.0, 993.0, 1941.0, 1006.0))],
                 "tol": 0.5, "verde_max": 10,
                 "folha": (236, 237, 236), "contorno": (96, 98, 100), "larg_contorno": 0.35}


def esquadria_limpar_1p(img, r, p2r, parede, faixa, fonte=None):
    """Como `retoque_terreo_casae.esquadria_limpar` (o piso logo fora da faixa, espelhado), com quatro ajustes para o
    1º Pavimento: parede é só o escuro grosso que não é verde (o das floreiras vale como fonte; os pontos e traços
    escuros finos, do motor e das floreiras, não são parede); do lado de
    uma parede, vem o piso mais perto do outro lado, não o espelhado (o de longe era mais claro e virava uma faixa
    branca junto à parede); a parede do render fora do retângulo do PDF fica (a faixa comia a face da parede junto às
    folhas e na porta embutida); e a faixa pode ser
    diferente de cada lado (antes, depois), para não apagar o brise de madeira junto à fachada, e vir de um lado só
    (`fonte`), para o vão da porta ficar no piso de um dos cômodos."""
    (u0, v0), (u1, v1) = p2r(r.x0, r.y0), p2r(r.x1, r.y1)
    fa, fb = faixa
    hor = (u1 - u0) >= (v1 - v0)
    if hor:
        X0, X1, Y0, Y1 = int(np.floor(u0)), int(np.ceil(u1)), int(np.floor(v0)) - fa, int(np.ceil(v1)) + fb
        meio = (v0 + v1) / 2
        for y in range(Y0, Y1):
            antes = fonte == "antes" or (fonte is None and y < meio)
            a, b = (2 * Y0 - y - 1, Y1 + y - Y0) if antes else (2 * Y1 - y - 1, Y0 - Y1 + y)
            novo = np.where(parede[a, X0:X1, None], img[b, X0:X1], img[a, X0:X1])
            f = parede[y, X0:X1] & (y + 1 <= v0 + 0.25 or y >= v1 - 0.25)
            img[y, X0:X1] = np.where(f[:, None], img[y, X0:X1], novo)
    else:
        X0, X1, Y0, Y1 = int(np.floor(u0)) - fa, int(np.ceil(u1)) + fb, int(np.floor(v0)), int(np.ceil(v1))
        meio = (u0 + u1) / 2
        for x in range(X0, X1):
            antes = fonte == "antes" or (fonte is None and x < meio)
            a, b = (2 * X0 - x - 1, X1 + x - X0) if antes else (2 * X1 - x - 1, X0 - X1 + x)
            novo = np.where(parede[Y0:Y1, a, None], img[Y0:Y1, b], img[Y0:Y1, a])
            f = parede[Y0:Y1, x] & (x + 1 <= u0 + 0.25 or x >= u1 - 0.25)
            img[Y0:Y1, x] = np.where(f[:, None], img[Y0:Y1, x], novo)


def esquadrias_1pav(out, pg, p2r):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    import retoque_terreo_casae as T
    q, qt = ESQUADRIAS_1P, T.ESQUADRIAS
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    D = pg.get_drawings()
    par = [d for d in D if d.get("layer") == "ARQ_PAREDE"]
    t = q["tol"]
    el = []
    for d in par:
        if d["type"] != "f" or not d["fill"] or min(d["fill"]) < 0.9:
            continue
        r = d["rect"]
        if max(r.width, r.height) < qt["comprimento_min"] or min(r.width, r.height) > qt["espessura_max"]:
            continue
        if any(z0 - t <= r.x0 and r.x1 <= z2 + t and z1 - t <= r.y0 and r.y1 <= z3 + t
               for _, (z0, z1, z2, z3), *_ in q["zonas"]):
            el.append(r)
    # grupos: vizinhos da mesma direção (como no Térreo)
    pai = list(range(len(el)))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i
    j = qt["junta"]
    for i, ra in enumerate(el):
        for k in range(i + 1, len(el)):
            rb = el[k]
            if ((ra.width >= ra.height) == (rb.width >= rb.height) and ra.x0 - j <= rb.x1 and rb.x0 - j <= ra.x1
                    and ra.y0 - j <= rb.y1 and rb.y0 - j <= ra.y1):
                pai[raiz(i)] = raiz(k)
    grupos = {}
    for i, r in enumerate(el):
        grupos.setdefault(raiz(i), []).append(r)
    img = out.astype(np.float32)
    # parede: o escuro grosso que não é verde (as paredes do render puxam para o marrom; as floreiras, para o verde)
    verde = img[..., 1] - np.maximum(img[..., 0], img[..., 2])
    parede = ((img.mean(axis=2) < qt["escuro"]) & (verde < q["verde_max"])).astype(np.uint8)
    parede = cv2.morphologyEx(parede, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0

    def opcoes(r):
        for _, (z0, z1, z2, z3), *o in q["zonas"]:
            if z0 - t <= r.x0 and r.x1 <= z2 + t and z1 - t <= r.y0 and r.y1 <= z3 + t:
                o = o[0] if o else {}
                return {**o, **o.get("vao", {})} if min(r.width, r.height) > 3.2 else o
        return {}
    padrao = (qt["faixa_px"],) * 2
    for _, _, *o in q["zonas"]:
        for ret, faixa, fonte in (o[0].get("extra", []) if o else []):
            esquadria_limpar_1p(img, pymupdf.Rect(*ret), p2r, parede, faixa, fonte)
    zonas = []
    for rs in grupos.values():
        for r in rs:
            o = opcoes(r)
            esquadria_limpar_1p(img, r, p2r, parede, o.get("faixa", padrao), o.get("fonte"))
        zonas.append((min(r.x0 for r in rs), min(r.y0 for r in rs), max(r.x1 for r in rs), max(r.y1 for r in rs)))
    for z in zonas:
        T.esquadria_desenhar(img, z, par, p2r, px_m, textura)
    # as folhas, como as portas do Subsolo: branco suave, com contorno fino mais escuro que o dos vidros (no quartzito
    # claro, a folha no cinza do Térreo sumia)
    nf = 0
    for r in el:
        if not 1.6 < min(r.width, r.height) < 2.5:
            continue
        (u0, v0), (u1, v1) = p2r(r.x0, r.y0), p2r(r.x1, r.y1)
        J0, K0, J1, K1 = int(u0) - 2, int(v0) - 2, int(np.ceil(u1)) + 2, int(np.ceil(v1)) + 2
        h, w = K1 - K0, J1 - J0
        f = np.zeros((h * SS, w * SS), np.uint8)
        p0 = (round((u0 - J0) * SS), round((v0 - K0) * SS))
        p1 = (round((u1 - J0) * SS), round((v1 - K0) * SS))
        reg = img[K0:K1, J0:J1]
        for larg, cor in ((-1, q["folha"]), (max(1, round(q["larg_contorno"] * SS)), q["contorno"])):
            f[:] = 0
            cv2.rectangle(f, p0, p1, 255, larg)
            a = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
            reg = reg * (1 - a) + np.float32(cor) * a
        img[K0:K1, J0:J1] = reg
        nf += 1
    print(f"    {len(el)} vidros, folhas e caixilhos do PDF em {len(zonas)} esquadrias, finos; {nf} folhas em branco")
    return np.clip(img, 0, 255).astype(np.uint8)


# item 11 do pente fino de 20/10/26: vinílico na escala (usuário, 21/10: "precisamos corrigir a escala do vinílico"; R4:
# réguas de ~20 cm, em tons alternados, como na planta de referência). O motor fez réguas de ~40 cm. Nas áreas de
# vinílico da base chapada (as linhas da hachura do PDF fechadas), só no que é piso no render:
# - piso: o marrom do vinílico (fora tapetes e móveis claros); os objetos no tom da madeira (mesinhas, almofadas) saem
#   por fugir da luz do piso: mais claros, ou mais escuros com outra cor (a sombra escurece sem mudar a cor e fica);
#   os nós e riscos pequenos do motor ficam como piso;
# - a luz do lugar: a média do piso, mais larga atravessando as réguas (o tom de cada régua velha sai) que ao longo
#   delas; o tom do render fica (#A8784F, escolhido em 16/10);
# - as réguas, desenhadas em 4x (`reguas_vinilico`): 20 cm de largura, 1,2 a 1,8 m de comprimento, em fiadas com as
#   juntas de topo desencontradas, cada uma num tom (claro ou escuro, alternando), com o veio do próprio vinílico do
#   render (o detalhe fino ao longo das réguas, de um trecho limpo, sem junta velha no meio) e as juntas em linha fina.
#   O vinílico da biblioteca (da referência, de 26 px/m) ficava borrado e em blocos na escala do render.
# - por fim (usuário, 21/10: "clareia um pouquinho o vinílico onde está escurecido"): onde a luz larga do piso fica
#   abaixo da mediana, ela sobe 70% do caminho.
VINILICO = {"cor_chapada": (79, 120, 168), "tol": 6, "fechar": 5, "croma_min": 30, "lum": (50, 215),
            "claro": 25, "escuro": 32, "matiz": 0.10, "objeto_min": 30,
            "sig_ao_longo_m": 0.25, "sig_atravessando_m": 0.45,
            "regua_m": 0.20, "comprimento_m": (1.2, 1.8), "tom": (0.015, 0.045), "junta": 0.95, "junta_larg": 0.4,
            "veio_sig": (8.0, 1.5), "veio_forca": 1.0, "costura": 0.95, "ss": 4, "semente": 3,
            "clarear": 0.7, "clarear_sig_m": 1.0}


def reguas_vinilico(h, w, px_m, veio, limpo, rng):
    """O desenho do vinílico (média 1), h x w px: fiadas horizontais de réguas, em 4x e reduzido."""
    q = VINILICO
    k = q["ss"]
    larg = q["regua_m"] * px_m
    D = np.ones((h * k, w * k), np.float32)
    J = np.ones_like(D)
    hj = int(np.ceil(larg)) + 2
    ys, xs = np.nonzero(limpo)
    jl = max(1, int(round(q["junta_larg"] * k)))

    def colar(dst, pedaco, b0, a0):
        sb, sa = max(0, -b0), max(0, -a0)
        b0, a0 = max(0, b0), max(0, a0)
        hh, ww = min(dst.shape[0] - b0, pedaco.shape[0] - sb), min(dst.shape[1] - a0, pedaco.shape[1] - sa)
        if hh > 0 and ww > 0:
            dst[b0:b0 + hh, a0:a0 + ww] = pedaco[sb:sb + hh, sa:sa + ww]

    y = -rng.uniform(0, larg)
    while y < h:
        x = -rng.uniform(0, q["comprimento_m"][1] * px_m)
        b0, b1 = int(round(y * k)), int(round((y + larg) * k))
        while x < w:
            comp = rng.uniform(*q["comprimento_m"]) * px_m
            a0, a1 = int(round(x * k)), int(round((x + comp) * k))
            cl = int(np.ceil(comp)) + 2
            jan = None
            for _ in range(400):
                i = rng.integers(len(ys))
                cy, cx = ys[i], xs[i]
                if cy + hj > limpo.shape[0] or cx + cl > limpo.shape[1] or not limpo[cy:cy + hj, cx:cx + cl].all():
                    continue
                cand = veio[cy:cy + hj, cx:cx + cl]
                if cand.mean(axis=1).min() > q["costura"]:
                    jan = cand
                    break
            if jan is None:
                jan = np.ones((hj, cl), np.float32)
            tom = 1 + rng.choice((-1, 1)) * rng.uniform(*q["tom"])
            pedaco = cv2.resize(jan, (cl * k, hj * k), interpolation=cv2.INTER_CUBIC)[k:k + b1 - b0, k:k + a1 - a0]
            colar(D, tom * (1 + q["veio_forca"] * (pedaco - 1)), b0, a0)
            colar(J, np.full((b1 - b0, jl), q["junta"], np.float32), b0, a0)
            x += comp
        colar(J, np.full((jl, w * k), q["junta"], np.float32), b0, 0)
        y += larg
    return cv2.resize(D * J, (w, h), interpolation=cv2.INTER_AREA)


def vinilico_escala(out, A, p2r):
    q = VINILICO
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    vin = (np.abs(chapada.astype(np.int32) - np.array(q["cor_chapada"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    vin = cv2.morphologyEx(vin, cv2.MORPH_CLOSE, np.ones((q["fechar"], 1), np.uint8)) > 0
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    im = out.astype(np.float32)
    lum, croma = im.mean(axis=2), im[..., 2] - im[..., 0]
    piso = vin & (croma >= q["croma_min"]) & (lum >= q["lum"][0]) & (lum <= q["lum"][1])
    sx, sy = q["sig_ao_longo_m"] * px_m, q["sig_atravessando_m"] * px_m

    def luz(m):
        mf = m.astype(np.float32)
        return (cv2.GaussianBlur(im * mf[..., None], (0, 0), sigmaX=sx, sigmaY=sy)
                / np.maximum(cv2.GaussianBlur(mf, (0, 0), sigmaX=sx, sigmaY=sy), 1e-4)[..., None])
    L0 = luz(piso)
    razao = im / np.maximum(L0, 1)
    fora = ((im - L0).max(axis=2) > q["claro"]) | (((L0 - im).max(axis=2) > q["escuro"])
                                                  & (razao.max(axis=2) - razao.min(axis=2) > q["matiz"]))
    n, lab, st, _ = cv2.connectedComponentsWithStats((fora & piso).astype(np.uint8), connectivity=8)
    fora = (st[:, cv2.CC_STAT_AREA] >= q["objeto_min"])[lab] & (lab > 0)
    piso &= ~cv2.dilate(fora.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    piso = cv2.morphologyEx(piso.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    mf = piso.astype(np.float32)
    L = luz(piso)
    # o veio: o detalhe fino do vinílico do render, ao longo das réguas
    vs, vy = q["veio_sig"]
    veio = lum / np.maximum(cv2.GaussianBlur(lum, (0, 0), sigmaX=vs, sigmaY=vy), 1)
    limpo = cv2.erode(piso.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    ys, xs = np.nonzero(piso)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    D = reguas_vinilico(y1 - y0, x1 - x0, px_m, veio, limpo, np.random.default_rng(q["semente"]))
    novo = im.copy()
    novo[y0:y1, x0:x1] = L[y0:y1, x0:x1] * D[..., None]
    al = (cv2.GaussianBlur(mf, (0, 0), 0.7) * piso)[..., None]
    novo = im * (1 - al) + novo * al
    # onde o piso está escurecido (closet master, rouparia, closets 1 e 2, a circulação junto a eles), a luz larga
    # (~1 m) sobe parte do caminho até a mediana do piso, em todo o vinílico (com o que está sobre ele)
    sg = q["clarear_sig_m"] * px_m
    Lg = cv2.GaussianBlur(lum * mf, (0, 0), sg) / np.maximum(cv2.GaussianBlur(mf, (0, 0), sg), 1e-4)
    ref = float(np.median(Lg[piso]))
    g = 1 + q["clarear"] * np.maximum(0, ref - Lg) / np.maximum(Lg, 1)
    av = cv2.GaussianBlur(vin.astype(np.float32), (0, 0), 1.0)
    novo *= (1 + (g - 1) * av)[..., None]
    out = np.clip(novo, 0, 255).astype(np.uint8)
    print(f"    vinílico: {int(piso.sum())} px em réguas de {100 * q['regua_m']:.0f} cm, a {px_m:.2f} px/m; "
          f"o escurecido sobe {100 * q['clarear']:.0f}% do caminho até a luz mediana ({ref:.0f}), até "
          f"+{100 * (g[vin].max() - 1):.0f}%")
    return out


# item 4 do pente fino de 20/10/26: banhos 3 e 4. O motor fez as duchas como discos redondos, com registros soltos até
# a parede, e o vaso como uma cápsula só, atravessando a parede entre os dois banhos (mais comprida que o vaso do PDF);
# a parede ficou com um bloco cinza no lugar dos dois nichos. No PDF (ARQ_LOUÇAS E METAIS): em cada banho, a ducha
# quadrada com o braço saindo da parede entre eles, e dois vasos suspensos, costas com costas, cada um no seu banho.
# - depois do quartzito (`banhos34_limpar`): o disco, os registros e a cápsula saem. Fica a luz do piso em volta
#   (convolução normalizada, sem paredes nem peças), com o desenho da chapa do piso logo ao lado, na mesma coluna,
#   longe da parede do meio. Antes do quartzito, a média do piso dele mudava e mexia no tom dos outros banhos;
# - em seguida (`banhos34_pecas`): os dois nichos do PDF na parede (o miolo da parede em preto entre eles), e
#   as peças como as aprovadas no Subsolo da Casa E (`retoque_subsolo_casae.chuveiro` e `vaso`): ducha quadrada (a placa
#   da Casa A), braço cromado e canopla; vaso em louça com volume, contorno fino, sombra curta e o tampo fechado, com a
#   dobradiça junto à parede.
BANHOS_34 = {"limpar": [((1235.0, 1336.0, 1256.0, 1371.0), -1), ((1235.0, 1382.3, 1256.0, 1417.0), 1),
                        ((1289.0, 1330.0, 1321.0, 1371.0), -1), ((1289.0, 1382.3, 1321.0, 1424.0), 1)],
             "pecas": [((1239.6, 1343.5, 1250.8, 1354.8), (1244.5, 1348.0, 1245.9, 1370.4),
                        (1243.5, 1370.4, 1246.9, 1371.0)),
                       ((1239.7, 1398.5, 1250.9, 1409.7), (1244.6, 1382.9, 1246.0, 1405.3),
                        (1243.6, 1382.3, 1247.0, 1382.9))],
             "vasos": [((1295.2, 1341.9, 1315.2, 1371.0), "baixo"), ((1294.9, 1382.3, 1314.9, 1411.4), "cima")],
             "nichos": [(1233.9, 1371.0, 1256.4, 1376.2), (1233.9, 1377.8, 1256.4, 1382.3)],
             "escuro": 60, "fuga": 25, "sig_px": 3.0, "nicho_tom": 0.93, "nicho_borda": (128, 131, 133)}


def banhos34_limpar(out, p2r):
    q = BANHOS_34
    im = out.astype(np.float32)
    # as paredes (o escuro grosso; os pontos escuros dos registros do motor saem com as peças)
    escuro = cv2.morphologyEx((im.max(axis=2) < q["escuro"]).astype(np.uint8), cv2.MORPH_OPEN,
                              np.ones((3, 3), np.uint8))
    escuro = cv2.dilate(escuro, np.ones((3, 3), np.uint8)).astype(bool)
    m = np.zeros(escuro.shape, bool)
    caixas = []
    for r, dy_pt in q["limpar"]:
        (a, b), (c, d) = p2r(r[0], r[1]), p2r(r[2], r[3])
        x0, y0, x1, y1 = int(np.floor(a)), int(np.floor(b)), int(np.ceil(c)), int(np.ceil(d))
        m[y0:y1, x0:x1] = True
        caixas.append((x0, y0, x1, y1, int(round(dy_pt * (y1 - y0 + 2)))))
    m &= ~escuro
    # o piso em volta: fora as peças, as paredes, o nicho cinza, as bancadas e o vidro do box (o que foge do tom)
    ok = ~cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~escuro
    ys, xs = np.nonzero(m)
    jan = np.zeros_like(ok)
    jan[max(0, ys.min() - 25):ys.max() + 25, max(0, xs.min() - 25):xs.max() + 25] = True
    tom = np.median(im[ok & jan], axis=0)
    ok &= np.abs(im - tom).max(axis=2) <= q["fuga"]
    okf = ok.astype(np.float32)

    def luz(s):
        w = cv2.GaussianBlur(okf, (0, 0), s)
        return cv2.GaussianBlur(im * okf[..., None], (0, 0), s) / np.maximum(w, 1e-6)[..., None], w
    # longe de qualquer piso limpo (o meio da cápsula, junto ao nicho), a luz vem de mais longe
    L, w = luz(q["sig_px"])
    L2, _ = luz(3 * q["sig_px"])
    perto = np.clip(w / 0.05, 0, 1)[..., None]
    L = L * perto + L2 * (1 - perto)
    # o desenho da chapa vem do piso logo ao lado, longe da parede do meio (a mesma coluna), na luz do lugar
    novo = im.copy()
    for x0, y0, x1, y1, dy in caixas:
        alvo = m[y0:y1, x0:x1]
        dono = im[y0 + dy:y1 + dy, x0:x1]
        limpo = ok[y0 + dy:y1 + dy, x0:x1]
        det = np.where(limpo[..., None], dono / np.maximum(L[y0 + dy:y1 + dy, x0:x1], 1), 1)
        novo[y0:y1, x0:x1][alvo] = (L[y0:y1, x0:x1] * det)[alvo]
    print(f"    banhos 3 e 4: {int(m.sum())} px de discos, registros e da cápsula do vaso viram o quartzito ao lado")
    return np.clip(novo, 0, 255).astype(np.uint8)


def banhos34_pecas(out, pg, p2r):
    import retoque_subsolo_casae as Sb
    q = BANHOS_34
    tl = Sb.Tela(out, p2r, (q["nichos"][0][0], q["nichos"][0][1], q["nichos"][1][2], q["nichos"][1][3]))
    tl.pintar(tl.ret((q["nichos"][0][0], q["nichos"][0][1], q["nichos"][1][2], q["nichos"][1][3])), (12, 12, 15))
    for r in q["nichos"]:
        m = tl.ret(r)
        tl.pintar(m, tuple(q["nicho_tom"] * c for c in QUARTZITO["tom"]))
        tl.contorno(m, 0.3, q["nicho_borda"])
    out = tl.gravar()
    for ducha, braco, canopla in q["pecas"]:
        out = Sb.chuveiro(out, p2r, ducha, braco, canopla)
    for caixa, parede in q["vasos"]:
        out = Sb.vaso(out, pg, p2r, caixa, parede)
    print("    banhos 3 e 4: os dois nichos, as duchas quadradas com o braço da parede e os dois vasos do PDF")
    return out


# item 5 do pente fino de 20/10/26: guarda-roupas com cabides (R11) no closet master (dois) e nos closets 1 a 4. O
# motor fez caixas lisas de marcenaria. Cada trecho reto do PDF (ARQ_LAYOUT HUMANIZAÇÃO: o retângulo de cada diagonal;
# os em L são dois trechos) recebe o `_texturas/elementos.guarda_roupa` (visto de cima, aberto: moldura branca fina
# com contorno cinza, miolo cinza-claro, mais escuro junto às portas, e cabides em traços cinza a cada ~12 cm), no
# tamanho do PDF, em 4x, com as portas do lado do vinílico do closet (o lado comprido que encosta nele). A rouparia, o
# armário da copinha e o do banho master ficam em marcenaria (R11 é só para guarda-roupa). Os tons (usuário, 21/10: "o
# tom dos armários guarda-roupas, pode ser bege dentro e na borda o ocre"): o miolo em bege, a moldura em ocre; e o
# cabideiro ("tem uma barra metallica no meio do armario para prender o cabide"), de lateral a lateral.
GUARDA_ROUPAS = {"pecas": [(1738.0, 761.5, 1984.0, 795.5), (1738.0, 863.6, 1984.0, 897.6),       # closet master
                           (1992.5, 764.4, 2026.5, 866.4), (2026.5, 764.4, 2111.6, 798.4),       # closet 2
                           (1992.5, 1113.0, 2026.5, 1215.1), (2026.5, 1113.0, 2111.6, 1147.0),   # closet 1
                           (1411.4, 1339.8, 1530.5, 1371.0), (1496.4, 1285.9, 1530.5, 1339.8),   # closet 4
                           (1411.4, 1382.3, 1530.5, 1413.5), (1496.4, 1413.5, 1530.5, 1467.4)],  # closet 3
                 "ss": 4, "semente": 11,
                 "miolo": (191, 212, 228), "moldura": (88, 148, 196)}   # BGR: bege dentro, ocre na borda (21/10)


def guarda_roupas(out, A, p2r):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from elementos import guarda_roupa
    q = GUARDA_ROUPAS
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    vin = (np.abs(chapada.astype(np.int32) - np.array(VINILICO["cor_chapada"])).max(axis=2) <= VINILICO["tol"])
    vin = vin.astype(np.float32)
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    S = q["ss"]
    im = out.astype(np.float32)
    lados = []
    for i, (x0, y0, x1, y1) in enumerate(q["pecas"]):
        (u0, v0), (u1, v1) = p2r(x0, y0), p2r(x1, y1)
        i0, j0, i1, j1 = int(round(u0)), int(round(v0)), int(round(u1)), int(round(v1))
        if (x1 - x0) >= (y1 - y0):
            lado = {"baixo": vin[j1 + 1:j1 + 4, i0 + 2:i1 - 2].mean(), "cima": vin[j0 - 4:j0 - 1, i0 + 2:i1 - 2].mean()}
        else:
            lado = {"direita": vin[j0 + 2:j1 - 2, i1 + 1:i1 + 4].mean(), "esquerda": vin[j0 + 2:j1 - 2, i0 - 4:i0 - 1].mean()}
        lado = max(lado, key=lado.get)
        lados.append(lado)
        comp, prof = max(x1 - x0, y1 - y0) / 56.69, min(x1 - x0, y1 - y0) / 56.69
        cor, alfa = guarda_roupa(comp, prof, px_m * S, semente=q["semente"] + i, miolo=q["miolo"], moldura=q["moldura"],
                                 barra=True)
        k = {"baixo": 0, "direita": 1, "cima": 2, "esquerda": 3}[lado]
        cor, alfa = np.ascontiguousarray(np.rot90(cor, k)), np.ascontiguousarray(np.rot90(alfa, k))
        X0, Y0, X1, Y1 = int(np.floor(u0)), int(np.floor(v0)), int(np.ceil(u1)), int(np.ceil(v1))
        tw, th = int(round((u1 - u0) * S)), int(round((v1 - v0) * S))
        ox, oy = int(round((u0 - X0) * S)), int(round((v0 - Y0) * S))
        grande = np.zeros(((Y1 - Y0) * S, (X1 - X0) * S, 3), np.float32)
        ag = np.zeros(grande.shape[:2], np.float32)
        grande[oy:oy + th, ox:ox + tw] = cv2.resize(cor, (tw, th), interpolation=cv2.INTER_AREA)
        ag[oy:oy + th, ox:ox + tw] = cv2.resize(alfa, (tw, th), interpolation=cv2.INTER_AREA)
        cr = cv2.resize(grande, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        ar = cv2.resize(ag, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
        im[Y0:Y1, X0:X1] = im[Y0:Y1, X0:X1] * (1 - ar) + cr
    print(f"    {len(q['pecas'])} trechos de guarda-roupa com cabides (portas: {', '.join(lados)})")
    return np.clip(im, 0, 255).astype(np.uint8)


# item 6 do pente fino de 20/10/26: projeções em tracejado (R8: "projeções ... shaft com X ... em tracejado bem
# visível"). Os traços da DOC_LINHAS E PROJEÇÕES que o motor apagou, desenhados como no PDF, por cima de tudo menos das
# paredes pretas, no traço das projeções do Térreo (0,6 px, força 0,85):
# - o shaft estreito entre o elevador e a rouparia: no PDF, um vão entre duas paredes, com o X; o motor fez ali uma
#   faixa de marcenaria. O vão fica branco, como os vazios, com o X em cinza médio, como o deles;
# - o retângulo com X na rouparia, sobre o vinílico: em cinza claro (o cinza médio sumia na madeira);
# - os X rasos no fundo do banho master (sobre o vaso e o box), sobre o quartzito: em cinza médio.
PROJECOES_1P = {"camada": "DOC_LINHAS E PROJEÇÕES",
                "vao_branco": (1833.0, 906.1, 1848.7, 996.8), "branco": 250, "escuro": 60,
                "grupos": [((1832.5, 905.5, 1849.0, 997.5), (147, 147, 147)),          # shaft
                           ((1886.0, 943.0, 1933.5, 990.0), (226, 226, 226)),          # rouparia
                           ((1538.5, 974.0, 1608.0, 997.5), (150, 150, 150)),          # banho master: vaso
                           ((1615.0, 974.0, 1726.5, 997.5), (150, 150, 150))],         # banho master: box
                "largura": 0.6, "forca": 0.85, "parede": 40}


def projecoes_1pav(out, pg, p2r):
    q = PROJECOES_1P
    im = out.astype(np.float32)
    (a, b), (c, d) = p2r(*q["vao_branco"][:2]), p2r(*q["vao_branco"][2:])
    x0, y0, x1, y1 = int(round(a)), int(round(b)), int(round(c)), int(round(d))
    reg = im[y0:y1, x0:x1]
    vao = reg.max(axis=2) > q["escuro"]
    reg[vao] = q["branco"]
    tracos = [dd for dd in pg.get_drawings() if dd.get("layer") == q["camada"]]
    n = 0
    for caixa, cor in q["grupos"]:
        cx = pymupdf.Rect(*caixa)
        segs = [(p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)) for dd in tracos if dd["rect"] in cx
                for it in dd["items"] if it[0] == "l"]
        pts = np.array([p for sg in segs for p in sg])
        X0, Y0 = np.floor(pts.min(axis=0)).astype(int) - 3
        X1, Y1 = np.ceil(pts.max(axis=0)).astype(int) + 4
        h, w = Y1 - Y0, X1 - X0
        f = np.zeros((h * SS, w * SS), np.uint8)
        for (ax, ay), (bx, by) in segs:
            cv2.line(f, (int(round((ax - X0) * SS)), int(round((ay - Y0) * SS))),
                     (int(round((bx - X0) * SS)), int(round((by - Y0) * SS))), 255,
                     max(1, int(round(q["largura"] * SS))), cv2.LINE_AA)
        al = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * q["forca"]
        reg = im[Y0:Y1, X0:X1]
        al *= reg.mean(axis=2) >= q["parede"]
        im[Y0:Y1, X0:X1] = reg * (1 - al[..., None]) + np.float32(cor) * al[..., None]
        n += len(segs)
    print(f"    projeções: o vão do shaft em branco ({int(vao.sum())} px) e {n} traços do PDF em {len(q['grupos'])} grupos")
    return np.clip(im, 0, 255).astype(np.uint8)


# item 8 do pente fino de 20/10/26: soleiras (R13: "a soleira é o vão da porta na espessura da parede deixado em
# branco, entre os batentes; onde o piso de um dos lados atravessa o vão, não há soleira"). Conferidas porta a porta no
# PDF (o vão entre os dois batentes da ARQ_PAREDE, e o que a base tem dentro dele): nas portas dos banhos 1 a 4, do
# banho master (a embutida, P11, e a do closet master, P13) e da rouparia (P10), o vão é branco: há soleira; nas das
# suítes, o vinílico atravessa, e na P12 do banho master, o quartzito: não há. Cada soleira, como no Térreo e no
# Subsolo da casa: o vão exato do PDF em Bege Bahia na escala (o desenho da biblioteca, no tom da referência), com as
# duas faces da parede (os lados compridos) em traço cinza fino; a folha embutida da P11, dentro do vão, fica por cima.
SOLEIRAS_1P = {"pdf": [(2111.6, 811.7, 2120.1, 861.6),     # banho 2
                       (2111.6, 1160.4, 2120.1, 1210.3),   # banho 1
                       (1402.9, 1290.8, 1411.4, 1335.0),   # banho 4
                       (1402.9, 1418.3, 1411.4, 1462.5),   # banho 3
                       (1726.1, 795.7, 1734.6, 863.7),     # banho master / closet master (P13)
                       (1524.8, 797.5, 1539.0, 865.6),     # suíte master / banho master (P11, embutida)
                       (1878.7, 996.8, 1926.3, 1005.3)],   # rouparia (P10)
               "folha_dentro": [(1530.7, 806.0, 1533.0, 868.4)]}   # a folha da P11, por cima da soleira


def soleiras_1pav(out, p2r):
    import retoque_terreo_casae as T
    q, qt = SOLEIRAS_1P, T.SOLEIRAS
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    k = SS
    for r in q["pdf"]:
        (x0, y0), (x1, y1) = p2r(r[0], r[1]), p2r(r[2], r[3])
        X0, Y0, X1, Y1 = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1, int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 2
        h, w = Y1 - Y0, X1 - X0
        m = np.zeros((h * k, w * k), np.uint8)
        u0, v0, u1, v1 = (int(round((x0 - X0) * k)), int(round((y0 - Y0) * k)), int(round((x1 - X0) * k)),
                          int(round((y1 - Y0) * k)))
        m[v0:v1, u0:u1] = 255
        f = np.zeros_like(m)
        e = max(1, int(round(qt["linha_px"] * k)))
        if (x1 - x0) >= (y1 - y0):
            f[v0:v0 + e, u0:u1] = 255
            f[v1 - e:v1, u0:u1] = 255
        else:
            f[v0:v1, u0:u0 + e] = 255
            f[v0:v1, u1 - e:u1] = 255
        for fr in q["folha_dentro"]:
            (fa, fb), (fc, fd) = p2r(fr[0], fr[1]), p2r(fr[2], fr[3])
            ia, ib = int(round((fa - X0) * k)) - 1, int(round((fb - Y0) * k))
            ic, id_ = int(round((fc - X0) * k)) + 1, int(round((fd - Y0) * k))
            m[max(0, ib):max(0, id_), max(0, ia):max(0, ic)] = 0
        al = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        fl = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        Tx = textura("bege_bahia", px_m, h, w, semente=qt["semente"]).astype(np.float32)
        Tx = (1 + qt["forca"] * (Tx / Tx.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(T.BEGE["tom"])
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg = reg * (1 - al) + Tx * al
        reg = reg * (1 - fl) + np.float32(qt["linha"]) * fl
        out[Y0:Y1, X0:X1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    {len(q['pdf'])} soleiras de Bege Bahia no vão branco do PDF, com as faces da parede em cinza fino")
    return out


# item 16 do pente fino de 20/10/26: quartzito dos banhos como a referência (usuário: "Textura do quartzito está errada -
# é um tom mais entre o branco e o cinza"; "quartzito dos banhos está no quadro de referências já enviado": a foto do
# quadro de 19/10, `_texturas/originais/quartzito_aura.jpg`, chapa de 3,00 m, RGB ~221, 215, 211). Os cinco banhos
# saíram no pêssego da legenda (#EAD4BF). Nas áreas de quartzito da base chapada:
# - o tom: a parte pêssego de cada px vai ao tom da foto. A fração de piso de cada px vem da cor pêssego (R - B, contra a
#   do piso): no piso, ela é 1, e numa sombra ela cai junto com o R - B, de modo que a troca acompanha a luz; na borda
#   suavizada de louças, vidros, placas e metais (mistura de branco com pêssego), só a parte pêssego muda (uma razão
#   de cor igual para todos deixava um halo azulado nessas bordas);
# - o desenho: a chapa da biblioteca, só na luz (sem a cor: o tom pedido é entre o branco e o cinza, e a foto tem uma
#   faixa bege), na escala do render, no piso limpo (fora dos traços e objetos medidos antes da troca de tom: o vidro
#   dos boxes, que é quase do tom novo, fica)
QUARTZITO = {"cor_chapada": (191, 212, 234), "tol": 6, "folga": 2, "tom": (211, 215, 221), "fracao_max": 1.2,
             "forca": 1.0, "semente": 1, "sig_m": 0.25, "tracos": 10}


def quartzito_referencia(out, A):
    from texturas_escala import retexturizar, nconv, textura
    q = QUARTZITO
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    qz = np.abs(chapada.astype(np.int32) - np.array(q["cor_chapada"])).max(axis=2) <= q["tol"]
    _, p2r, _ = pdf_cadeia(A, out.shape)
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    im = out.astype(np.float32)
    # os traços e objetos, medidos no pêssego (antes da troca de tom)
    L = nconv(im, qz.astype(np.float32), 0.25 * px_m)
    tracos = cv2.dilate((np.abs(im - L).max(axis=2) > q["tracos"]).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    piso = qz & ~tracos
    pessego = im[piso].mean(axis=0)
    # a fração de piso de cada px (pela cor pêssego), numa faixa um pouco maior que a da chapada (cantos junto às paredes)
    area = cv2.dilate(qz.astype(np.uint8), np.ones((2 * q["folga"] + 1,) * 2, np.uint8)) > 0
    croma = (im[..., 2] - im[..., 0]) / (pessego[2] - pessego[0])
    fr = np.clip(croma, 0, q["fracao_max"]) * area
    im = im + fr[..., None] * (np.float32(q["tom"]) - pessego)
    out = np.clip(im, 0, 255).astype(np.uint8)

    def chapa(h, w):
        T = textura("quartzito_aura", px_m, h, w, semente=q["semente"]).astype(np.float32)
        return np.repeat(T.mean(axis=2, keepdims=True), 3, axis=2)
    out, npx = retexturizar(out, piso, "quartzito_aura", px_m, forca=q["forca"], sig_m=q["sig_m"], pronta=chapa,
                            cor=q["tom"])
    print(f"    quartzito: {int((fr > 0).sum())} px no tom da foto; {npx} px no desenho da chapa, a {px_m:.2f} px/m")
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
    print("[pente fino 11] vinílico na escala: réguas de 20 cm, como a referência (R4)")
    out = vinilico_escala(out, A, p2r)
    print("[4] copinha: bancada em Bege Bahia e cuba redonda")
    out = copinha(out, p2r)
    print("[pente fino 2] escada com linhas, triângulo no topo e esmaecida depois do corte do Térreo (R14)")
    out = escada_r14(out, p2r)
    print("[5] vazios: X tracejado claro")
    out = vazios(out, A, pg, p2r, r2p)
    print("[6] portas: sem os arcos (R3), com a folha da pivotante do hall")
    out = arcos_portas(out, pg, p2r)
    print("[7] cortinas nas janelas das suítes")
    print("[10] fachadas das suítes: brises de bronze e portas de correr de vidro finas")
    out = fachadas(out, pg, p2r)
    # pente fino de 20/10, item 10: a cortina de linho da biblioteca, como no Térreo, no lugar das ondas do item 7
    out = cortinas_linho(out, pg, p2r)
    print("[11] cubas dos banhos no lugar do PDF")
    out = cubas_banhos(out, orig)
    print("[12] bancos em bege no pé das camas")
    out = bancos_camas(out, pg, p2r)
    print("[13] torneira de piso da banheira do banho master")
    out = torneira_banheira(out, p2r)
    print("[9] shaft: X em cinza na parede")
    out = shaft(out, pg, p2r)
    print("[pente fino 16] quartzito dos banhos como a referência (o tom e a chapa da foto)")
    out = quartzito_referencia(out, A)
    print("[pente fino 4] banhos 3 e 4: discos, registros e a cápsula do vaso saem; nichos, duchas e vasos do PDF")
    out = banhos34_limpar(out, p2r)
    out = banhos34_pecas(out, pg, p2r)
    print("[pente fino 9 e 7] portas, janelas e vidros finos, pelo PDF")
    out = esquadrias_1pav(out, pg, p2r)
    print("[pente fino 8] soleiras no vão branco do PDF (R13)")
    out = soleiras_1pav(out, p2r)
    print("[pente fino 5] guarda-roupas com cabides nos closets (R11)")
    out = guarda_roupas(out, A, p2r)
    print("[pente fino 3] boxes em folha contínua, de parede a parede (R10)")
    out = boxes_continuos(out, p2r)
    print("[pente fino 6] projeções em tracejado: shaft, rouparia e banho master (R8)")
    out = projecoes_1pav(out, pg, p2r)

    args.saida.mkdir(parents=True, exist_ok=True)
    # sem rótulos: a imagem que vai à montagem com o Térreo esmaecido (os rótulos são escritos de novo na
    # resolução da prancha, nítidos)
    cv2.imwrite(str(args.saida / f"{args.nome}_sem_rotulos.png"), out)
    print("[14] nomes e áreas dos ambientes (do PDF)")
    rot = rotulos_pdf(pg)
    out = rotulos_ambientes(out, rot, p2r)
    print(f"    {len(rot)} rótulos")
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Térreo da Casa E (POE 642).

O render (Nano Banana Pro, 2000 x 1116) manteve a escala da base: a base 16:9 reduzida ao tamanho do
render cai nele quase pela identidade (escala 0,9998 x 1,0066, deslocamento de 0,3 e -2,8 px). Os
retoques são feitos no quadro do render, como nas outras casas.

Itens (o mapa está em POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_erros.jpg):
1. Lote: a vegetação que o motor passou para fora do lote (à esquerda, embaixo e no alto à
   direita) sai, e as linhas tracejadas do lote, que ele apagou, voltam: fora do lote fica a base
   alinhada (o branco, a linha tracejada da esquerda, a da direita e o retângulo tracejado embaixo).
   Os muros de cima e de baixo, onde as folhas passavam por cima, voltam ao preto (cada linha do
   muro vira a mediana dela num trecho limpo).
2. Faixa à direita dos pisantes: a faixa em Bege Bahia que o motor inventou entre o gramado e a
   linha tracejada da direita (fora do gramado, branca no PDF) volta ao branco da base, no mesmo
   passo do item 1.
3. Jardim interno: as plantas, que o motor espalhou para fora da floreira (por cima da escada e no
   travertino em volta, com a sombra delas), ficam só no retângulo da floreira do PDF; fora dele
   voltam a escada (os degraus tracejados, da mesma coluna logo acima, e a linha diagonal, que segue
   até a floreira) e o travertino (da mesma coluna, mais abaixo: os veios correm na vertical), e a
   borda da floreira entra em traço fino.
4. Tapete do estar da varanda: o motor fez um tapete redondo; no PDF ele é orgânico (polígono branco
   da layer ARQ_MOBILIÁRIO), com um recorte em volta da ponta esquerda do sofá. O tapete toma a forma
   do PDF: o que sai vira travertino (as mesmas colunas da faixa limpa acima do tapete, pois os veios
   correm na vertical, na luz do travertino em volta e com a sombra dos móveis), o que entra vira
   tapete tecido do próprio tapete; sofá, poltronas, mesas e aparador ficam; borda fina por fora.
5. Varanda: as quatro barras a 45° à esquerda das poltronas (ARQ_ELEMENTOS FIXOS), que o motor
   apagou, voltam na geometria do PDF (cada uma, o retângulo girado da mancha do PDF), no cinza em que
   aparecem na base, com volume leve, contorno fino e sombra curta no piso.
6. Elevador: o motor fez a caixa num piso de pedra clara com um contorno de cabine solto no meio.
   Como nas Casas C e D: caixa branca e a cabine do Subsolo da Casa B aprovado (porta embaixo, como
   no PDF), ocupando a caixa inteira, com 1 a 2 px de folga; as folhas da porta e a soleira ficam.

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/retoque_terreo_casae.py POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_render.webp \
      --saida POE642_CasaE/renders --nome POE642_CasaE_PH_Terreo_v1_retocado
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

from retoque_terreo_casad import interpolar, textura  # noqa: E402

SS = 8                             # superamostragem dos traços desenhados
BASE = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - TÉRREO - CASA E.pdf"
CONFIG = RAIZ / "POE642_CasaE/config_bases.json"


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
    al = cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    return A, al


def pdf_cadeia(A, forma_render):
    """Página do PDF e as conversões PDF -> render e render -> PDF pela mesma cadeia da base (recorte,
    largura da base, tela 16:9, redução ao tamanho do render e o afim A)."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Terreo"]["pagina"]]
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
    """Caixa (x0, y0, x1, y1) de um desenho do PDF no quadro do render."""
    (x0, y0), (x1, y1) = p2r(d["rect"].x0, d["rect"].y0), p2r(d["rect"].x1, d["rect"].y1)
    return x0, y0, x1, y1


def mascara_pdf(janela, A, forma_render, filtro):
    """Máscara (0..1, no quadro do render) dos desenhos do PDF escolhidos por filtro(d), preenchidos,
    levados ao render pela mesma cadeia da base. Os desenhos são refeitos numa página nova (o MuPDF
    não desliga as layers deste PDF no raster) e rasterizados em alta resolução."""
    pg, p2r, r2p = pdf_cadeia(A, forma_render)
    nova = pymupdf.open()
    pn = nova.new_page(width=pg.rect.width, height=pg.rect.height)
    sh = pn.new_shape()
    for d in pg.get_drawings():
        if not filtro(d):
            continue
        for it in d["items"]:
            if it[0] == "l":
                sh.draw_line(it[1], it[2])
            elif it[0] == "c":
                sh.draw_bezier(it[1], it[2], it[3], it[4])
            elif it[0] == "re":
                sh.draw_rect(it[1])
            elif it[0] == "qu":
                sh.draw_quad(it[1])
        sh.finish(fill=(0, 0, 0), color=None, closePath=d.get("closePath", True), even_odd=d.get("even_odd", False))
    sh.commit()
    x0, y0, x1, y1 = janela
    a, b = r2p(x0 - 2, y0 - 2), r2p(x1 + 2, y1 + 2)
    ret = pymupdf.Rect(a[0], a[1], b[0], b[1])
    zp = 60
    pix = pn.get_pixmap(clip=ret, matrix=pymupdf.Matrix(zp, zp), alpha=False, colorspace=pymupdf.csGRAY)
    img = 255 - np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    src = [(0, 0), (pix.width, 0), (0, pix.height)]
    dst = [(p2r(ret.x0 + u / zp, ret.y0 + v / zp)[0] - x0, p2r(ret.x0 + u / zp, ret.y0 + v / zp)[1] - y0) for u, v in src]
    M = cv2.getAffineTransform(np.float32(src), np.float32(dst))
    return cv2.warpAffine(np.ascontiguousarray(img).astype(np.float32) / 255, M, (x1 - x0, y1 - y0),
                          flags=cv2.INTER_AREA, borderValue=0)


# lote no quadro do render: o gramado vai de x = 141 a 1798; o muro de cima ocupa as linhas 0 a 5
# (de 142 a 1798) e o de baixo as linhas 932 a 937 (de 141 a 1851, até a linha tracejada da direita).
# Fora: x < 141, x >= 1799 acima do muro de baixo (a faixa entre o gramado e a linha tracejada da
# direita, onde o motor pôs o Bege Bahia), e tudo abaixo do muro de baixo
LOTE = {
    "x_esq": 141, "x_dir": 1799, "x_muro_baixo": 1852,
    "muro_cima": (0, 6), "muro_baixo": (932, 938),
    # trecho limpo (sem folhas) de onde sai a mediana de cada linha do muro
    "limpo_cima": (450, 1450), "limpo_baixo": (450, 1300),
}


def lote(out, base):
    q = LOTE
    xe, xd, xb = q["x_esq"], q["x_dir"], q["x_muro_baixo"]
    (c0, c1), (b0, b1) = q["muro_cima"], q["muro_baixo"]
    a, b = q["limpo_cima"]
    out[c0:c1, xe:xd] = np.median(out[c0:c1, a:b], axis=1).astype(np.uint8)[:, None]
    a, b = q["limpo_baixo"]
    out[b0:b1, xe:xb] = np.median(out[b0:b1, a:b], axis=1).astype(np.uint8)[:, None]
    fora = np.zeros(out.shape[:2], bool)
    fora[:, :xe] = True
    fora[:b0, xd:] = True
    fora[b0:b1, xb:] = True
    fora[b1:, :] = True
    out[fora] = base[fora]
    print(f"    muros de cima e de baixo sem as folhas; fora do lote: base ({int(fora.sum())} px)")
    return out


# jardim interno (item 3): a floreira do PDF no quadro do render (a borda escura da terra no render
# cai nela), a escada logo acima (degraus tracejados verticais de 497 a 542, com a linha horizontal
# em 523, e a diagonal de (1079, 498) a (1094, 527), que no PDF vai até a floreira)
JARDIM = {
    "floreira": (977, 543, 1155, 582), "janela": (950, 490, 1185, 615),
    # a fonte da escada fica abaixo da sombra do louceiro (497 a 499) e acima da linha horizontal;
    # deslocamentos (dy, dx): primeiro só na vertical (o tracejado repete a cada ~6,5 px), depois
    # também de dois degraus (~18,6 px) para os lados, onde a diagonal ocupa a fonte
    "escada": (977, 497, 1155, 543), "fonte_escada": (500, 523),
    "desloc_escada": [(dy, 0) for dy in (13, 26, 20, 7, 14, 19)] + [(dy, dx) for dy in (13, 7, 20) for dx in (-19, 19, -28, 28)],
    "desloc_trav": (64, 80, 96, 112),
    "diagonal": ((1079, 498), (1094, 527)), "diag_fim_y": 543, "cor_diag": (128, 142, 158),
    # plantas: verdes ou escuras; sombra: mais escura que o travertino limpo da mesma coluna (veios
    # verticais), perto das plantas e fora da escada
    "verde": 2, "escuro": 110, "ref_trav": (620, 680), "sombra": 7, "alcance_sombra": 12,
    "borda": {"cor": (78, 80, 80), "larg": 0.9, "forca": 0.85},
}


def linha_aa(forma, pts, larg, fechada=False):
    """Máscara (0 a 1) de uma polilinha, desenhada em SS x e reduzida."""
    h, w = forma
    m = np.zeros((h * SS, w * SS), np.uint8)
    p = np.int32(np.round(np.float64(pts) * SS))
    cv2.polylines(m, [p], fechada, 255, max(1, int(round(larg * SS))), cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def jardim_interno(out):
    q = JARDIM
    fx0, fy0, fx1, fy1 = q["floreira"]
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = out[wy0:wy1, wx0:wx1].astype(int)
    lum = reg.mean(axis=2)
    planta = (reg[..., 1] > reg[..., 2] + q["verde"]) | (lum < q["escuro"])
    dentro = np.zeros(lum.shape, bool)
    dentro[fy0 - wy0:fy1 - wy0, fx0 - wx0:fx1 - wx0] = True
    sx0, sy0, sx1, sy1 = q["escada"]
    escada = np.zeros(lum.shape, bool)
    escada[sy0 - wy0:sy1 - wy0, sx0 - wx0:sx1 - wx0] = True
    # a mancha das plantas (ligada à floreira) e a sombra delas no travertino, em volta
    n, lab = cv2.connectedComponents(planta.astype(np.uint8))
    ligada = np.isin(lab, np.unique(lab[dentro & planta])) & (lab > 0)
    r0, r1 = q["ref_trav"]
    ref = np.median(out[r0:r1, wx0:wx1].astype(np.float32).mean(axis=2), axis=0)[None, :]
    k = 2 * q["alcance_sombra"] + 1
    perto = cv2.dilate(ligada.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    m = cv2.dilate(ligada.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    m |= perto & (lum < ref - q["sombra"]) & ~escada
    m |= perto & planta                                  # pontas soltas de folha
    # na escada, o halo claro em volta das folhas também sai (a fonte é a própria escada, limpa)
    m |= escada & (cv2.dilate(ligada.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
    m &= ~dentro
    f0, f1 = q["fonte_escada"]
    m[:f1 + 1 - wy0] &= ~escada[:f1 + 1 - wy0]          # as plantas não sobem acima da linha horizontal
    # escada: a mesma coluna, alguns degraus de tracejado acima (sem a diagonal e sem as plantas);
    # travertino: a mesma coluna, mais abaixo, onde não há planta nem sombra
    (dx0, dy0), (dx1, dy1) = q["diagonal"]
    incl = (dx1 - dx0) / (dy1 - dy0)
    ys, xs = np.mgrid[wy0:wy1, wx0:wx1]
    na_diag = np.abs(xs - (dx0 + (ys - dy0) * incl)) < 5
    orig = out.copy()
    n_esc = n_trav = 0
    for y, x in zip(*np.nonzero(m)):
        Y, X = y + wy0, x + wx0
        if escada[y, x]:
            for dy, dx in q["desloc_escada"]:
                fy, fx = Y - dy, X + dx
                if f0 <= fy < f1 and sx0 <= fx < sx1 and not na_diag[fy - wy0, fx - wx0] and not m[fy - wy0, fx - wx0]:
                    out[Y, X] = orig[fy, fx]
                    n_esc += 1
                    break
        else:
            for d in q["desloc_trav"]:
                fy = Y + d
                if fy >= wy1 or not m[fy - wy0, x]:
                    out[Y, X] = orig[fy, X]
                    n_trav += 1
                    break
    # a diagonal segue da linha horizontal até a floreira
    a = linha_aa(out.shape[:2], [(dx0 + (f1 + 0.5 - dy0) * incl, f1 + 0.5),
                                 (dx0 + (q["diag_fim_y"] - dy0) * incl, q["diag_fim_y"])], 1.0)[..., None] * 0.8
    out[:] = np.clip(out * (1 - a) + np.float32(q["cor_diag"]) * a, 0, 255).astype(np.uint8)
    # borda da floreira
    b = q["borda"]
    a = linha_aa(out.shape[:2], [(fx0 + 0.5, fy0 + 0.5), (fx1 - 0.5, fy0 + 0.5), (fx1 - 0.5, fy1 - 0.5),
                                 (fx0 + 0.5, fy1 - 0.5)], b["larg"], fechada=True)[..., None] * b["forca"]
    out[:] = np.clip(out * (1 - a) + np.float32(b["cor"]) * a, 0, 255).astype(np.uint8)
    print(f"    plantas fora da floreira: {n_esc} px de escada e {n_trav} px de travertino refeitos; diagonal e borda")
    return out


# tapete do estar da varanda (item 4): o redondo do render é uma elipse; o do PDF, o polígono branco
# da ARQ_MOBILIÁRIO com esta caixa no quadro do render
TAPETE = {
    "janela": (826, 652, 986, 806),
    "pdf": (839.7, 668.0, 965.6, 796.9),
    "velho": ((904.5, 732.0), (60.5, 65.0)),
    "fonte_tapete": [(915, 677, 937, 695), (930, 738, 950, 748), (940, 700, 952, 725)],
    "fonte_travertino": (622, 664),          # linhas limpas acima do tapete (as mesmas colunas)
    # móveis: os polígonos brancos do PDF em volta (sofá, poltronas, mesas, aparador, mesinhas e
    # vasos), com 2 px de folga, e os traços escuros do render junto deles
    "camadas_moveis": ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO", "DOC_TEXTOS"), "escuro": 150,
    "borda": 0.95,
}


def tapete(out, A):
    q = TAPETE
    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    novo = mascara_pdf(q["janela"], A, out.shape, lambda d: d.get("fill") == (1.0, 1.0, 1.0) and
                       d.get("layer") == "ARQ_MOBILIÁRIO" and
                       max(abs(u - v) for u, v in zip(caixa_render(d, p2r), q["pdf"])) <= 1.5)
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    Y = cv2.GaussianBlur(reg.mean(axis=2), (0, 0), 0.8)
    yy, xx = np.mgrid[wy0:wy1, wx0:wx1].astype(np.float32) + 0.5
    (cx, cy), (ax, ay) = q["velho"]
    velho = ((xx - cx) / ax) ** 2 + ((yy - cy) / ay) ** 2 <= 1.0
    def movel(d):
        c = caixa_render(d, p2r)
        return (d.get("fill") == (1.0, 1.0, 1.0) and d.get("layer") in q["camadas_moveis"] and
                max(abs(u - v) for u, v in zip(c, q["pdf"])) > 1.5 and
                c[2] > wx0 and c[0] < wx1 and c[3] > wy0 and c[1] < wy1)

    pecas = cv2.dilate((mascara_pdf(q["janela"], A, out.shape, movel) > 0.3).astype(np.uint8), np.ones((5, 5), np.uint8))
    pecas = (pecas > 0) | (cv2.dilate(pecas, np.ones((5, 5), np.uint8)) > 0) & (Y < q["escuro"])
    sai = velho & (novo < 0.5) & ~pecas
    entra = ~velho & (novo > 0.0) & ~pecas
    # travertino: as mesmas colunas da faixa limpa acima, repetida em espelho na vertical, na luz do
    # travertino em volta; a sombra dos móveis no tapete passa para o travertino (só escurece)
    f0, f1 = q["fonte_travertino"]
    faixa = out[f0:f1, wx0:wx1].astype(np.float32)
    n = f1 - f0
    idx = np.arange(h) % (2 * n)
    trav = faixa[np.where(idx < n, idx, 2 * n - 1 - idx)]
    limpo = ~velho & ~pecas & (novo < 0.01) & (Y > 195)
    luz = interpolar(cv2.GaussianBlur(Y, (0, 0), 1.0) / np.maximum(cv2.GaussianBlur(trav.mean(axis=2), (0, 0), 1.0), 1),
                     limpo, 2.0)
    tap_med = np.median(Y[velho & ~pecas & (novo > 0.5)])
    sombra = np.clip(cv2.GaussianBlur(Y, (0, 0), 1.5) / tap_med, 0.7, 1.0)
    trav = trav * (luz * sombra)[..., None]
    cor = np.median(np.concatenate([out[b:d, a:c].reshape(-1, 3) for a, b, c, d in q["fonte_tapete"]]).astype(np.float32), axis=0)
    tap = textura(out, q["fonte_tapete"], h, w, p=8) * cor
    a_sai = (np.clip(1 - novo, 0, 1) * (cv2.dilate(sai.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) * ~pecas)[..., None]
    reg = reg * (1 - a_sai) + trav * a_sai
    a_ent = (novo * entra)[..., None]
    reg = reg * (1 - a_ent) + tap * a_ent
    borda = np.clip(cv2.dilate(novo, np.ones((3, 3), np.uint8)) - novo, 0, 1) * ~pecas
    reg *= (1 - (1 - q["borda"]) * borda)[..., None]
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    tapete no contorno orgânico do PDF ({int(sai.sum())} px saem, {int(entra.sum())} px entram)")
    return out


# barras a 45° da varanda (item 5): os quadradinhos brancos da ARQ_ELEMENTOS FIXOS nesta janela
BARRAS = {
    "janela": (618, 643, 658, 770),
    "cor": (148, 150, 153), "volume": 0.06,        # cinza da base; mais claro na face de cima
    "contorno": (70, 72, 74), "larg_contorno": 0.5, "traco_pdf": 0.6,
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35},
}


def poligono_aa(forma, pts):
    """Máscara (0 a 1) de um polígono preenchido, desenhado em SS x e reduzido."""
    h, w = forma
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round(np.float64(pts) * SS))], 255, cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def barras(out, A):
    q = BARRAS
    wx0, wy0, wx1, wy1 = q["janela"]
    pg, p2r, _ = pdf_cadeia(A, out.shape)

    def dentro(d):
        x0, y0, x1, y1 = caixa_render(d, p2r)
        return wx0 < x0 and x1 < wx1 and wy0 < y0 and y1 < wy1

    m = mascara_pdf(q["janela"], A, out.shape, lambda d: d.get("layer") == "ARQ_ELEMENTOS FIXOS" and
                    d["type"] == "f" and d.get("fill") == (1.0, 1.0, 1.0) and dentro(d))
    n, lab = cv2.connectedComponents((m > 0.5).astype(np.uint8))
    forma = out.shape[:2]
    s = q["sombra"]
    # cada barra: o retângulo girado da mancha; a largura vem da área (o retângulo dos centros dos px
    # fica fino demais), mais o traço do contorno do PDF (0,57 pt), e é a mediana das quatro
    rets = []
    for i in range(1, n):
        ys, xs = np.nonzero(lab == i)
        (cx, cy), (a, b), ang = cv2.minAreaRect(np.float32(np.c_[xs + wx0 + 0.5, ys + wy0 + 0.5]))
        comp = max(a, b) + 1
        rets.append(((cx, cy), comp, float(m[lab == i].sum()) / comp + q["traco_pdf"], ang, a >= b))
    larg = float(np.median([r[2] for r in rets]))
    for i, ((cx, cy), comp, _, ang, deitado) in enumerate(rets, 1):
        a, b = (comp, larg) if deitado else (larg, comp)
        cantos = cv2.boxPoints(((cx, cy), (a, b), ang))
        # sombra curta no piso (só escurece)
        sombra = cv2.GaussianBlur(poligono_aa(forma, cantos + np.float32(s["desloc"])), (0, 0), s["sigma"])
        out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
        # a barra: cinza com a face de cima um pouco mais clara (gradiente na largura)
        al = poligono_aa(forma, cantos)
        yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
        u = np.float32([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
        lado = u if a < b else np.float32([-u[1], u[0]])      # direção da largura
        t = np.clip(((xx - cx) * lado[0] + (yy - cy) * lado[1]) / max(min(a, b) / 2, 0.5), -1, 1)
        t *= -np.sign(lado[1] + 1e-6)                           # +1 na face de cima
        cor = np.float32(q["cor"])[None, None, :] * (1 + q["volume"] * t)[..., None]
        out[:] = np.clip(out * (1 - al[..., None]) + cor * al[..., None], 0, 255).astype(np.uint8)
        c = linha_aa(forma, cantos, q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - c) + np.float32(q["contorno"]) * c, 0, 255).astype(np.uint8)
        print(f"    barra {i}: centro ({cx:.1f}, {cy:.1f}), {max(a, b):.1f} x {min(a, b):.1f} px, {ang:.0f}°")
    return out


# elevador (item 6): o vão da caixa entre as paredes (no quadro do render) e a cabine do Subsolo da
# Casa B aprovado, a mesma das Casas C e D; lá a porta já fica embaixo, como aqui (sem girar)
ELEVADOR = {
    "interior": (1018, 370, 1067, 415),
    "cabine": (1020, 372, 1066, 414),          # ocupa a caixa, com 1-2 px de folga (como na Casa D)
    "branco": (255, 255, 255),
    "fonte": (RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final.png", (3116, 1011, 3276, 1162)),
}


def elevador(out):
    q = ELEVADOR
    x0, y0, x1, y1 = q["interior"]
    out[y0:y1, x0:x1] = q["branco"]
    arq, (fx0, fy0, fx1, fy1) = q["fonte"]
    cabine = cv2.imread(str(arq))[fy0:fy1, fx0:fx1]
    cx0, cy0, cx1, cy1 = q["cabine"]
    out[cy0:cy1, cx0:cx1] = cv2.resize(cabine, (cx1 - cx0, cy1 - cy0), interpolation=cv2.INTER_AREA)
    print(f"    elevador: caixa branca e a cabine do Subsolo da Casa B ({cx1 - cx0}x{cy1 - cy0} px)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    A, base = alinhar_base(orig)
    print("[1, 2] lote: vegetação fora do lote, linhas tracejadas e faixa à direita dos pisantes")
    out = lote(out, base)
    print("[3] jardim interno: plantas só na floreira")
    out = jardim_interno(out)
    print("[4] tapete do estar da varanda no contorno orgânico do PDF")
    out = tapete(out, A)
    print("[5] varanda: as quatro barras a 45° do PDF")
    out = barras(out, A)
    print("[6] elevador: cabine ocupando a caixa")
    out = elevador(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

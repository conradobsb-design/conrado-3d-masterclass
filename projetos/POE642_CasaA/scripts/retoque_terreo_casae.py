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
7. CPD: o vaso sanitário que o motor pôs junto à parede da direita (no PDF o CPD não tem louça) sai,
   com a sombra; ali volta o granito tecido do próprio CPD, na luz do piso em volta.
8. Área de serviço: as duas máquinas do PDF (dois quadrados da ARQ_LAYOUT HUMANIZAÇÃO ao lado do
   tanque duplo), que o motor juntou num bloco de madeira, voltam como as máquinas em inox do Térreo
   da Casa D aprovado (cada uma, a metade do par de lá, no quadrado do PDF), com sombra curta; o resto
   do bloco vira o granito tecido do piso.
9. Área de serviço descoberta: o X tracejado do PDF (layer DOC_LINHAS E PROJEÇÕES: as duas
   diagonais e a linha de baixo), que o motor apagou, volta como a projeção sobre a garagem e a área
   descoberta da Casa D: cinza e traço fino, só sobre o granito.
10. DCE: o motor fez a cama como uma laje de pedra, o criado-mudo como um armário alto e o armário
    até o teto (o da diagonal) como uma pia. As três peças do render saem (granito tecido do próprio
    quarto; paredes, janela e porta ficam) e entram as do DCE do Térreo aprovado da Casa D, nos
    retângulos do PDF: a cama de solteiro (girada, cabeceira na parede da direita, como o travesseiro
    do PDF) e o criado-mudo, com sombra curta, e o armário até o teto em areia com veio, sem sombra de
    móvel baixo e com contorno fino.
11. WC DCE 1: o motor pôs um segundo vaso no alto, onde o PDF tem o chuveiro. O vaso sai (Bege Bahia
    tecido do próprio WC, na luz do piso em volta; a linha do box fica) e entra o chuveiro do PDF como
    o do WC DCE da Casa D (ducha quadrada com a placa da Casa A, braço cromado até a parede da direita
    e canopla, com sombra curta).
12. Arcos das portas sobre o granito (pedido do usuário): como nas Casas C e D, em cinza e traço fino.
    O motor quase não os fez (só o do DCE, apagado e escuro); o arco escuro que houver sai (granito
    tecido, só no granito da base chapada) e entra o arco cinza fino das curvas do PDF (ARQ_PAREDE).
13. Pontos claros do granito (pedido do usuário: muitos, espalhados; tirar alguns): os pontinhos
    claros de 2 a 16 px que o motor salpicou no Marrom Tabaco saem onde se destacam (30 ou mais acima
    do granito em volta); ficam os mais fracos e o grão fino. Cada um vira o granito de um trecho
    vizinho sem ponto, colado com borda suave.
14. Pilar à direita do lavabo (pedido do usuário): o retângulo cinza da ARQ_ELEMENTOS FIXOS, que o
    motor fez como uma peça cinza-taupe com folhas por cima, é um pilar: fica no preto das paredes,
    na geometria do PDF (alto, cobre as folhas).
15. Lavabo (pedido do usuário): cuba esculpida, com a torneira vindo do lado esquerdo. A cuba branca e
    a torneira preta que o motor pôs no meio da bancada saem (quartzo tecido da própria bancada, na luz
    dela); na metade esquerda da bancada do PDF entra a cuba esculpida no próprio quartzo: o fundo
    inclinado escurece para trás, onde fica a fenda do ralo, as bordas de cima e da direita fazem uma
    sombra curta para dentro, e um traço fino marca a borda. A torneira do PDF sai da parede da
    esquerda: canopla e bica cromadas, com brilho e sombra curta.
16. Escritório (pedido do usuário): atrás do sofá é um arranjo de flores (o círculo do PDF, ARQ_LAYOUT
    HUMANIZAÇÃO); o motor fez uma bola verde. Entra o arranjo com a estrelítzia do próprio jardim do
    render (folhas em leque e as flores laranja, as mesmas do paisagismo), reduzida ao círculo do
    PDF, com borda suave e sombra curta.
17. Louceiro (pedido do usuário): veios aparentes de marcenaria. O motor deixou a madeira lisa; o veio
    vem do tampo da mesa de jantar do próprio render (veio no comprido), girado para correr no
    comprimento do louceiro e realçado, como no mobiliário do DCE da Casa D; o tom e as bordas ficam.
18. Escada interna (pedido do usuário): só sombreamento que denota a subida, da direita para a
    esquerda, sem linhas. O travertino da escada é refeito sem os tracejados dos degraus, a linha de
    corte e a diagonal (as mesmas colunas do travertino limpo abaixo da floreira, veios verticais); os
    19 pisos do PDF (9,33 px) clareiam para cima (a escada sobe da direita para a esquerda: o de baixo,
    à direita, é o mais escuro) e cada espelho joga uma sombra curta no piso de baixo, à direita dele,
    inclusive o primeiro, no piso da sala.
19. Jardim de inverno (pedido do usuário): as plantas saem levemente da floreira, sem exagero: nunca
    por cima da escada (a borda de cima fica), um pouco para os lados (até ~3 px) e um pouco mais para
    baixo (até ~6 px), com a borda das folhas irregular; as folhas voltam do render original, por
    cima do traço da floreira, com uma sombra curta desenhada no travertino. Entram poucas flores tropicais coloridas (as estrelítzias
    do jardim do render, laranja, e as mesmas em vermelho, rosa e amarelo), espalhadas.

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

from retoque_terreo_casad import desenhar_chuveiro, interpolar, textura  # noqa: E402
from retoque_subsolo_casad import apagar_largo  # noqa: E402
from retoque_terreo_casac import CROMO, CROMO_CLARO, CROMO_ESCURO  # noqa: E402

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


# vaso inventado no CPD (item 7): a caixa do vaso e da sombra dele (a parede da direita começa em
# x = 1290) e trechos limpos do granito do CPD (à direita da folha da porta, que fica em x ~1245)
VASO_CPD = {
    "janela": (1240, 368, 1290, 418), "vaso": (1259, 391, 1290, 414),
    "fontes": [(1249, 372, 1286, 390), (1249, 391, 1258, 417)],
}


def vaso_cpd(out):
    q = VASO_CPD
    wx0, wy0, wx1, wy1 = q["janela"]
    vx0, vy0, vx1, vy1 = q["vaso"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    m[vy0 - wy0:vy1 - wy0, vx0 - wx0:vx1 - wx0] = True
    out = apagar_largo(out, q["janela"], m, q["fontes"], sigma=3.0, lum_min=40, escuros=True)
    print(f"    vaso do CPD: {int(m.sum())} px de granito tecido")
    return out


# máquinas da área de serviço (item 8): o bloco de madeira do render, os dois quadrados do PDF e as
# máquinas em inox do Térreo retocado da Casa D (o par fica em x 1143-1190, y 191-216; a divisória
# em 1166)
MAQUINAS = {
    "bloco": (1078, 289, 1128, 317), "janela": (1010, 289, 1150, 345),
    "fontes_granito": [(1032, 318, 1115, 334), (1130, 300, 1148, 340)],
    "quadrados": [(1079.8, 291.6, 1101.5, 313.4), (1103.3, 291.6, 1125.0, 313.4)],
    "fonte": (RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png",
              [(1143, 191, 1166, 216), (1167, 191, 1190, 216)]),
    "contorno": (70, 70, 72), "larg_contorno": 0.4,
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35},
}


def maquinas(out):
    q = MAQUINAS
    wx0, wy0, wx1, wy1 = q["janela"]
    bx0, by0, bx1, by1 = q["bloco"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    m[by0 - wy0:by1 - wy0, bx0 - wx0:bx1 - wx0] = True
    # a parede de cima (preta) fica
    m &= out[wy0:wy1, wx0:wx1].mean(axis=2) > 35
    out = apagar_largo(out, q["janela"], m, q["fontes_granito"], sigma=3.0, lum_min=40, escuros=False)
    arq, fontes = q["fonte"]
    casad = cv2.imread(str(arq))
    forma = out.shape[:2]
    s = q["sombra"]
    for (x0, y0, x1, y1), (fx0, fy0, fx1, fy1) in zip(q["quadrados"], fontes):
        cantos = np.float32([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        sombra = cv2.GaussianBlur(poligono_aa(forma, cantos + np.float32(s["desloc"])), (0, 0), s["sigma"])
        out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
        # a máquina de lá, levada ao quadrado do PDF (subpixel, por afim)
        maq = casad[fy0:fy1, fx0:fx1].astype(np.float32)
        M = cv2.getAffineTransform(np.float32([(0, 0), (fx1 - fx0, 0), (0, fy1 - fy0)]),
                                   np.float32([(x0, y0), (x1, y0), (x0, y1)]))
        img = cv2.warpAffine(maq, M, forma[::-1], flags=cv2.INTER_AREA)
        al = poligono_aa(forma, cantos)[..., None]
        out[:] = np.clip(out * (1 - al) + img * al, 0, 255).astype(np.uint8)
        c = linha_aa(forma, cantos, q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - c) + np.float32(q["contorno"]) * c, 0, 255).astype(np.uint8)
    print(f"    área de serviço: bloco de madeira em granito tecido e as duas máquinas em inox da Casa D")
    return out


# X tracejado da área de serviço descoberta (item 9): os traços da DOC_LINHAS E PROJEÇÕES na janela,
# no estilo da projeção da garagem da Casa D (cinza claro, traço fino, só sobre o granito)
X_DESCOBERTA = {
    "janela": (1012, 216, 1160, 284), "layer": "DOC_LINHAS E PROJEÇÕES",
    "cor": (160, 161, 160), "larg": 0.45, "forca": 0.7,
    "granito_lum": (35.0, 115.0),
}


def x_descoberta(out, A):
    q = X_DESCOBERTA
    x0, y0, x1, y1 = q["janela"]
    h, w = y1 - y0, x1 - x0
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    pts = []
    for d in pg.get_drawings():
        if d.get("layer") != q["layer"] or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] == "l":
                a, b = p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)
                if all(x0 <= u <= x1 and y0 <= v <= y1 for u, v in (a, b)):
                    pts.append((a, b))
    m = np.zeros((h * SS, w * SS), np.uint8)
    for a, b in pts:
        cv2.line(m, [int(round((a[0] - x0) * SS)), int(round((a[1] - y0) * SS))],
                 [int(round((b[0] - x0) * SS)), int(round((b[1] - y0) * SS))], 255,
                 max(1, int(round(q["larg"] * SS))), cv2.LINE_AA)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    Y = reg.mean(axis=2)
    lo, hi = q["granito_lum"]
    gran = ((Y > lo) & (Y < hi) & (reg[..., 2] > reg[..., 0])).astype(np.float32)
    a = (cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * gran * q["forca"])[..., None]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.float32(q["cor"]) * a, 0, 255).astype(np.uint8)
    print(f"    área de serviço descoberta: X tracejado do PDF ({len(pts)} traços)")
    return out


# DCE (item 10): o que o motor fez (laje, armário alto e pia) sai, e entram as peças do DCE do Térreo
# retocado da Casa D (aprovado) nos retângulos do PDF (ARQ_LAYOUT HUMANIZAÇÃO); a cama e o
# criado-mudo de lá estão em pé (cabeceira em cima): giradas no sentido horário, a cabeceira fica à
# direita, onde o PDF tem o travesseiro
DCE = {
    "janela": (1150, 250, 1250, 332),
    "limpar": [(1177, 255, 1245, 299), (1156, 288, 1179, 327)],
    "fontes_granito": [(1214, 299, 1240, 325)],
    "fonte": RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png",
    # (nome, recorte na Casa D, giro, retângulo do PDF no render, sombra de móvel baixo)
    "pecas": [("cama", (1338, 271, 1369, 334), cv2.ROTATE_90_CLOCKWISE, (1179.1, 254.6, 1243.2, 284.4), True),
              ("criado-mudo", (1323, 272, 1334, 285), cv2.ROTATE_90_CLOCKWISE, (1229.9, 285.4, 1242.4, 296.3), True),
              ("armário até o teto", (1295, 330, 1326, 349), cv2.ROTATE_90_COUNTERCLOCKWISE,
               (1159.2, 290.3, 1176.3, 324.5), False)],
    "contorno": (70, 72, 74), "larg_contorno": 0.4,
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35},
}


def colar(out, img, ret):
    """Leva img ao retângulo ret (x0, y0, x1, y1, em px do render, subpixel) por afim, com a borda
    antisserrilhada."""
    x0, y0, x1, y1 = ret
    h, w = img.shape[:2]
    M = cv2.getAffineTransform(np.float32([(0, 0), (w, 0), (0, h)]), np.float32([(x0, y0), (x1, y0), (x0, y1)]))
    forma = out.shape[:2]
    im = cv2.warpAffine(img.astype(np.float32), M, forma[::-1], flags=cv2.INTER_AREA)
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])[..., None]
    out[:] = np.clip(out * (1 - al) + im * al, 0, 255).astype(np.uint8)
    return out


def sombra_curta(out, ret, s):
    x0, y0, x1, y1 = ret
    cantos = np.float32([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]) + np.float32(s["desloc"])
    sombra = cv2.GaussianBlur(poligono_aa(out.shape[:2], cantos), (0, 0), s["sigma"])
    out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
    return out


def dce(out):
    q = DCE
    wx0, wy0, wx1, wy1 = q["janela"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    for x0, y0, x1, y1 in q["limpar"]:
        m[y0 - wy0:y1 - wy0, x0 - wx0:x1 - wx0] = True
    out = apagar_largo(out, q["janela"], m, q["fontes_granito"], sigma=3.0, lum_min=40, escuros=False)
    casad = cv2.imread(str(q["fonte"]))
    for nome, (fx0, fy0, fx1, fy1), giro, ret, sombra in q["pecas"]:
        if sombra:
            out = sombra_curta(out, ret, q["sombra"])
        out = colar(out, cv2.rotate(casad[fy0:fy1, fx0:fx1], giro), ret)
        x0, y0, x1, y1 = ret
        c = linha_aa(out.shape[:2], [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - c) + np.float32(q["contorno"]) * c, 0, 255).astype(np.uint8)
        print(f"    DCE, {nome}: a da Casa D em ({x0:.1f}, {y0:.1f}) - ({x1:.1f}, {y1:.1f})")
    return out


# WC DCE 1 (item 11): o vaso que o motor pôs onde o PDF tem o chuveiro (a parede da direita começa em
# x = 1289; a linha do box, que fica, nas linhas 280-281) e o chuveiro do PDF (ARQ_LOUÇAS E METAIS),
# no mesmo desenho do WC DCE da Casa D (a mesma geometria, quase)
WC_DCE = {
    "janela": (1248, 254, 1292, 286), "vaso": (1263, 257, 1289, 280),
    "fontes": [(1251, 258, 1264, 279), (1251, 283, 1270, 299)],
    # a luz vem só do piso limpo (~200-212): sem a linha do box nem a borda da parede, que escureciam
    "lum_min": 192,
    "chuveiro": {"nome": "WC DCE 1", "ducha": (1275.0, 264.4, 1281.2, 270.5), "braco": (1278.1, 1289.7, 267.5),
                 "canopla": (1288.9, 266.5, 1290.1, 268.5)},
    "sombra": {"desloc": (-1.0, 1.0), "sigma": 0.8, "forca": 0.3},
}


def wc_dce(out):
    q = WC_DCE
    wx0, wy0, wx1, wy1 = q["janela"]
    vx0, vy0, vx1, vy1 = q["vaso"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    m[vy0 - wy0:vy1 - wy0, vx0 - wx0:vx1 - wx0] = True
    out = apagar_largo(out, q["janela"], m, q["fontes"], sigma=3.0, lum_min=q["lum_min"], lum_max=235, escuros=True)
    out = desenhar_chuveiro(out, q["janela"], q["chuveiro"], sombra=q["sombra"])
    print("    WC DCE 1: vaso inventado fora; chuveiro do PDF (ducha, braço e canopla)")
    return out


# arcos das portas sobre o granito (item 12, pedido do usuário): o padrão das Casas C e D (cinza
# (160, 161, 160) e traço de 0,45 px na escala do Térreo), só onde a base chapada é granito
ARCOS = {"granito": (50, 66, 90), "tol": 12, "fracao": 0.3, "min_px": 8,
         "cor": (160, 161, 160), "larg": 0.45, "faixa": 1.5, "escuro": 55,
         "fontes_granito": [(700, 160, 900, 200), (1300, 160, 1450, 200)]}


def arcos_granito(out, A):
    """Arcos das portas (curvas da ARQ_PAREDE) sobre o granito: o arco escuro do render sai (px
    escuros numa faixa em volta da curva do PDF, só no granito da base chapada) e entra o cinza fino."""
    q = ARCOS
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    gran = (np.abs(chapada.astype(np.int32) - np.array(q["granito"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    gran = cv2.morphologyEx(gran, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))   # fecha os traços finos
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    n = 0
    for d in pg.get_drawings():
        if d.get("layer") != "ARQ_PAREDE" or not any(it[0] == "c" for it in d["items"]):
            continue
        x0, y0, x1, y1 = caixa_render(d, p2r)
        x0, y0, x1, y1 = int(x0) - 4, int(y0) - 4, int(np.ceil(x1)) + 5, int(np.ceil(y1)) + 5
        if max(x1 - x0, y1 - y0) < q["min_px"] or x0 < 0 or y0 < 0 or x1 > out.shape[1] or y1 > out.shape[0]:
            continue
        g = gran[y0:y1, x0:x1].astype(bool)
        if g.mean() < q["fracao"]:
            continue
        h, w = y1 - y0, x1 - x0
        curvas = []
        for it in d["items"]:
            if it[0] == "c":
                pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
                tt = np.linspace(0, 1, 80)[:, None]
                curvas.append((1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1] + 3 * (1 - tt) * tt ** 2 * pp[2]
                              + tt ** 3 * pp[3])

        def traco(larg):
            f = np.zeros((h * SS, w * SS), np.uint8)
            for c in curvas:
                cv2.polylines(f, [np.round((c - [x0, y0]) * SS).astype(np.int32)], False, 255,
                              max(1, int(round(larg * SS))), cv2.LINE_AA)
            return cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

        lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m = (traco(2 * q["faixa"]) > 0.05) & g & (lum < q["escuro"])
        if m.any():
            m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & g
            out = apagar_largo(out, (x0, y0, x1, y1), m, q["fontes_granito"], sigma=2.0, borda=0.0,
                               lum_min=45, lum_max=130, escuros=True)
        a = (traco(q["larg"]) * g)[..., None]
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.array(q["cor"], np.float32) * a, 0, 255).astype(np.uint8)
        n += 1
    print(f"    {n} arcos de porta sobre o granito em cinza fino")
    return out


# pontos claros do granito (item 13, pedido do usuário): pontinhos compactos (2 a 16 px, caixa de
# até 5 x 5) mais claros que o granito em volta (mediana de 11 px), no render original e onde o
# retoque não mexeu (assim os traços desenhados, arcos e X, nunca entram); saem os de contraste >= 30
PONTOS = {"limiar": 18, "sai": 30, "area": (2, 16), "caixa": 5, "mediana": 11, "margem": 2,
          "desloc": [(7, 0), (-7, 0), (0, 7), (0, -7), (7, 7), (-7, -7), (7, -7), (-7, 7), (12, 0), (-12, 0),
                     (0, 12), (0, -12)]}


def pontos_granito(out, orig, A):
    q = PONTOS
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    gran = (np.abs(chapada.astype(np.int32) - np.array(ARCOS["granito"])).max(axis=2) <= ARCOS["tol"]).astype(np.uint8)
    gran = cv2.morphologyEx(gran, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    igual = (np.abs(out.astype(np.int16) - orig.astype(np.int16)).max(axis=2) == 0).astype(np.uint8)
    ok = (cv2.erode(gran, np.ones((7, 7), np.uint8)) > 0) & (cv2.erode(igual, np.ones((7, 7), np.uint8)) > 0)
    Y = orig.astype(np.float32).mean(axis=2)
    d = Y - cv2.medianBlur(orig, q["mediana"]).astype(np.float32).mean(axis=2)
    claro = (d > q["limiar"]) & ok
    n, lab, st, _ = cv2.connectedComponentsWithStats(claro.astype(np.uint8), connectivity=8)
    a0, a1 = q["area"]
    todos = np.zeros(claro.shape, bool)
    sair = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if not (a0 <= area <= a1 and w <= q["caixa"] and h <= q["caixa"]):
            continue
        todos |= lab == i
        if d[lab == i].max() >= q["sai"]:
            sair.append((x, y, w, h, i))
    proibido = cv2.dilate(todos.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    H, W = Y.shape
    feitos = 0
    e = q["margem"]
    for x, y, w, h, i in sair:
        x0, y0, x1, y1 = x - e, y - e, x + w + e, y + h + e
        ponto = (lab[y0:y1, x0:x1] == i).astype(np.float32)
        al = np.maximum(cv2.GaussianBlur(cv2.dilate(ponto, np.ones((3, 3), np.uint8)), (0, 0), 0.7), ponto)[..., None]
        for dx, dy in q["desloc"]:
            sx0, sy0, sx1, sy1 = x0 + dx, y0 + dy, x1 + dx, y1 + dy
            if sx0 < 0 or sy0 < 0 or sx1 > W or sy1 > H:
                continue
            if not ok[sy0:sy1, sx0:sx1].all() or proibido[sy0:sy1, sx0:sx1].any():
                continue
            reg = out[y0:y1, x0:x1].astype(np.float32)
            fonte = out[sy0:sy1, sx0:sx1].astype(np.float32)
            out[y0:y1, x0:x1] = np.clip(reg * (1 - al) + fonte * al, 0, 255).astype(np.uint8)
            feitos += 1
            break
    print(f"    granito: {feitos} de {len(sair)} pontos claros fortes fora (os mais fracos ficam)")
    return out


# pilar à direita do lavabo (item 14, pedido do usuário): o retângulo cinza da ARQ_ELEMENTOS FIXOS
# no quadro do render; o preto é o da parede do lavabo logo à esquerda
PILAR = {"ret": (1296.0, 667.6, 1373.8, 687.8), "parede": (1291, 660, 1295, 683)}


def pilar(out):
    q = PILAR
    a, b, c, d = q["parede"]
    viz = out[b:d, a:c].reshape(-1, 3)
    preto = np.median(viz[viz.astype(np.float32).mean(axis=1) < 40], axis=0).astype(np.float32)
    x0, y0, x1, y1 = q["ret"]
    al = poligono_aa(out.shape[:2], [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])[..., None]
    out[:] = np.clip(out * (1 - al) + preto * al, 0, 255).astype(np.uint8)
    print(f"    pilar: ({x0}, {y0}) - ({x1}, {y1}) no preto das paredes {preto.astype(int).tolist()}")
    return out


# lavabo (item 15, pedido do usuário): a bancada do render vai de x 1199 a 1251 e de y 667 a 682 (a
# parede da esquerda termina em 1196 e a de baixo começa em 683); a cuba e a torneira do motor ficam
# em x 1218-1239. A cuba esculpida ocupa a metade esquerda do PDF (até 1226,4) com ~2 px de borda,
# e a torneira do PDF (ARQ_LOUÇAS E METAIS) sai da parede da esquerda, na altura do meio da cuba
LAVABO = {
    # a cuba e a torneira do motor saem: as mesmas linhas de quartzo limpo da própria bancada (a luz de
    # cada linha fica), à esquerda e à direita em espelho
    "bancada": (1199, 667, 1252, 683),
    "copias": [((1218, 1227), (1205, 1214), False), ((1227, 1239), (1240, 1252), True)],
    "cuba": (1201.0, 668.8, 1224.6, 680.6),
    "inclinacao": 0.12,                       # o fundo escurece até 12% junto à fenda (atrás)
    "sombra_borda": (0.16, 1.4),               # força e largura da sombra das bordas de cima e da direita
    "luz_borda": 0.04,
    "fenda": {"cor": (92, 94, 98), "larg": 0.8, "recuo": 1.3},
    "contorno": (150, 150, 150), "larg_contorno": 0.4, "forca_contorno": 0.6,
    "torneira": {"canopla": (1198.4, 672.6, 1200.3, 676.8), "bica": (1199.5, 1207.5), "larg": 1.2},
    "sombra": {"desloc": (-1.0, 1.0), "sigma": 0.8, "forca": 0.3},
}


def lavabo(out):
    q = LAVABO
    bx0, by0, bx1, by1 = q["bancada"]
    for (a0, a1), (f0, f1), espelho in q["copias"]:
        fonte = out[by0:by1, f0:f1]
        out[by0:by1, a0:a1] = fonte[:, ::-1] if espelho else fonte
    forma = out.shape[:2]
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
    x0, y0, x1, y1 = q["cuba"]
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    # fundo inclinado: escurece de frente (em cima) para trás (embaixo, junto à parede)
    f = 1 - q["inclinacao"] * np.clip((yy - y0) / (y1 - y0), 0, 1)
    # sombra curta das bordas de cima e da direita (a luz vem de cima e da direita) e luz nas outras
    s, w = q["sombra_borda"]
    f *= 1 - s * np.exp(-np.clip(yy - y0, 0, None) / w) - s * np.exp(-np.clip(x1 - xx, 0, None) / w)
    f *= 1 + q["luz_borda"] * (np.exp(-np.clip(xx - x0, 0, None) / w) + np.exp(-np.clip(y1 - yy, 0, None) / w))
    f = 1 + (f - 1) * al
    out[:] = np.clip(out * f[..., None], 0, 255).astype(np.uint8)
    fd = q["fenda"]
    a = linha_aa(forma, [(x0 + 1.5, y1 - fd["recuo"]), (x1 - 1.5, y1 - fd["recuo"])], fd["larg"])[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(fd["cor"]) * a, 0, 255).astype(np.uint8)
    a = linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], q["larg_contorno"], fechada=True)[..., None] * q["forca_contorno"]
    out[:] = np.clip(out * (1 - a) + np.float32(q["contorno"]) * a, 0, 255).astype(np.uint8)
    # torneira: canopla na parede da esquerda e a bica cromada até o meio da cuba
    tq = q["torneira"]
    yc = (y0 + y1) / 2
    bica = [(tq["bica"][0], yc), (tq["bica"][1], yc)]
    sb = q["sombra"]
    sombra = cv2.GaussianBlur(linha_aa(forma, [(u + sb["desloc"][0], v + sb["desloc"][1]) for u, v in bica], tq["larg"]),
                              (0, 0), sb["sigma"])
    out[:] = np.clip(out * (1 - sb["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
    for pts, larg, cor in ((bica, tq["larg"], CROMO_ESCURO),
                           ([(tq["bica"][0], yc - 0.15), (tq["bica"][1] - 0.3, yc - 0.15)], 0.35, CROMO_CLARO)):
        a = linha_aa(forma, pts, larg)[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(cor) * a, 0, 255).astype(np.uint8)
    cx0, cy0, cx1, cy1 = tq["canopla"]
    a = poligono_aa(forma, [(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)])[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(CROMO) * a, 0, 255).astype(np.uint8)
    print("    lavabo: cuba do motor fora; cuba esculpida no quartzo e torneira saindo da parede da esquerda")
    return out


# arranjo de flores do escritório (item 16): o círculo do PDF e a estrelítzia do jardim do próprio
# render (centro da touceira com duas flores laranja), no quadro do render
ARRANJO = {"centro": (1275.95, 606.2), "raio": 7.2, "fonte": ((1582, 899), 17),
           "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35}}


def arranjo(out, orig):
    q = ARRANJO
    (cx, cy), r = q["centro"], q["raio"]
    (fx, fy), fr = q["fonte"]
    fonte = orig[fy - fr:fy + fr, fx - fr:fx + fr]
    forma = out.shape[:2]
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
    disco = np.clip(r + 0.5 - np.hypot(xx - cx, yy - cy), 0, 1)
    s = q["sombra"]
    sombra = cv2.GaussianBlur(np.clip(r + 0.5 - np.hypot(xx - cx - s["desloc"][0], yy - cy - s["desloc"][1]), 0, 1),
                              (0, 0), s["sigma"])
    # a bola verde do motor sai junto: a sombra e o arranjo cobrem o círculo dela
    out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
    out = colar_disco(out, fonte, (cx, cy), r, disco)
    print(f"    escritório: arranjo de flores (estrelítzia do jardim) no círculo do PDF, raio {r} px")
    return out


def colar_disco(out, img, centro, r, alfa):
    """Leva img (quadrada) ao quadrado de lado 2r em volta do centro, por afim, com a máscara alfa."""
    cx, cy = centro
    h, w = img.shape[:2]
    M = cv2.getAffineTransform(np.float32([(0, 0), (w, 0), (0, h)]),
                               np.float32([(cx - r, cy - r), (cx + r, cy - r), (cx - r, cy + r)]))
    im = cv2.warpAffine(img.astype(np.float32), M, out.shape[1::-1], flags=cv2.INTER_AREA)
    a = alfa[..., None]
    out[:] = np.clip(out * (1 - a) + im * a, 0, 255).astype(np.uint8)
    return out


# veio do louceiro (item 17): a madeira lisa do louceiro no quadro do render e o tampo da mesa de
# jantar (veio vertical, sem cadeiras), como os veios do DCE da Casa D
VEIO_LOUCEIRO = {"peca": (984, 471, 1147, 490), "fonte": (885, 505, 914, 589),
                 "realce": 2.2, "sigma": 3.0, "lim": (0.85, 1.15), "borda": 1}


def veio_louceiro(out, orig):
    q = VEIO_LOUCEIRO
    a, b, c, d = q["fonte"]
    Y = orig[b:d, a:c].astype(np.float32).mean(axis=2)
    v = Y / np.maximum(cv2.GaussianBlur(Y, (0, 0), q["sigma"], borderType=cv2.BORDER_REFLECT), 1)
    v = np.clip(1 + q["realce"] * (v - 1), *q["lim"])
    g = cv2.rotate(v, cv2.ROTATE_90_CLOCKWISE)                       # veio no comprimento (em x)
    x0, y0, x1, y1 = q["peca"]
    h, w = y1 - y0, x1 - x0
    g = np.concatenate([g, g[::-1]] * (h // (2 * g.shape[0]) + 1), axis=0)[:h]
    g = np.concatenate([g, g[:, ::-1]] * (w // (2 * g.shape[1]) + 1), axis=1)[:, :w]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    base = cv2.GaussianBlur(reg, (0, 0), 1.2)
    e = q["borda"]
    novo = reg.copy()
    novo[e:-e, e:-e] = (base * g[..., None])[e:-e, e:-e]
    out[y0:y1, x0:x1] = np.clip(novo, 0, 255).astype(np.uint8)
    print(f"    louceiro: veio da mesa de jantar, realce {q['realce']}")
    return out


# escada interna (item 18, pedido do usuário): os degraus do PDF (ARQ_ESCADAS E RAMPAS) no quadro do
# render; sobe da direita (piso mais baixo) para a esquerda
ESCADA = {
    "x": (976.4, 1154.6), "n": 19, "linhas": (497, 543),
    "fonte": 600,                              # 1ª linha do travertino limpo abaixo da floreira
    "escurece": 0.10,                          # o piso de baixo (à direita) fica 10% mais escuro
    "sombra": (0.18, 2.0),                     # força e decaimento (px) da sombra de cada espelho
    "fim_sombra": 1163,                        # a sombra do 1º espelho no piso da sala vai até aqui
}


def escada(out):
    q = ESCADA
    xa, xb = q["x"]
    y0, y1 = q["linhas"]
    xi0, xi1 = int(np.floor(xa)), int(np.ceil(xb))
    f0 = q["fonte"]
    out[y0:y1, xi0:xi1] = out[f0:f0 + (y1 - y0), xi0:xi1]
    passo = (xb - xa) / q["n"]
    forca, dec = q["sombra"]
    xs = np.arange(xi0, q["fim_sombra"], dtype=np.float32)
    sub = (xs[:, None] + (np.arange(8, dtype=np.float32)[None, :] + 0.5) / 8)       # 8 amostras por px
    k = np.floor((sub - xa) / passo)
    na_escada = (sub >= xa) & (sub < xb)
    f = np.where(na_escada, 1 - q["escurece"] * np.clip(k, 0, q["n"] - 1) / (q["n"] - 1), 1.0)
    # sombra de cada espelho no piso de baixo, à direita dele (o 1º, em xb, cai no piso da sala)
    borda = xa + np.clip(np.floor((sub - xa) / passo), 0, q["n"]) * passo
    dist = sub - borda
    tem = (sub > xa + passo) | (sub >= xb)
    f *= np.where(tem & (sub < q["fim_sombra"]), 1 - forca * np.exp(-dist / dec), 1.0)
    f = f.mean(axis=1)
    out[y0:y1, xi0:q["fim_sombra"]] = np.clip(out[y0:y1, xi0:q["fim_sombra"]] * f[None, :, None], 0, 255).astype(np.uint8)
    print(f"    escada: {q['n']} pisos de {passo:.2f} px, sem linhas; sobe da direita para a esquerda")
    return out


# jardim de inverno (item 19, pedido do usuário): quanto as folhas podem sair da floreira (px, com
# uma borda irregular entre o mínimo e o máximo) e as flores (o centro da estrelítzia no render, o
# raio do recorte, onde entra na floreira e o tom: o laranja do render ou girado para outra cor)
JARDIM_FORA = {
    "lados": (1.5, 3.5), "baixo": (3.0, 6.5), "semente": 642,
    "flores": {"fonte": [((1671, 540), 9), ((1773, 605), 9), ((1582, 905), 9), ((1440, 722), 8)],
               "pos": [((1002, 557), 0, None), ((1046, 571), 1, "vermelho"), ((1089, 554), 2, None),
                       ((1121, 572), 3, "rosa"), ((1143, 556), 0, "amarelo")],
               "giro_matiz": {"vermelho": -9, "rosa": -20, "amarelo": 9}, "escala": 0.85},
}


def jardim_flores(out, orig):
    q = JARDIM_FORA
    j = JARDIM
    fx0, fy0, fx1, fy1 = j["floreira"]
    wx0, wy0, wx1, wy1 = j["janela"]
    reg = orig[wy0:wy1, wx0:wx1].astype(np.float32)
    lum = reg.mean(axis=2)
    ri = reg.astype(int)
    planta = (ri[..., 1] > ri[..., 2] + j["verde"]) | (lum < j["escuro"])
    dentro = np.zeros(lum.shape, bool)
    dentro[fy0 - wy0:fy1 - wy0, fx0 - wx0:fx1 - wx0] = True
    n, lab = cv2.connectedComponents(planta.astype(np.uint8))
    ligada = np.isin(lab, np.unique(lab[dentro & planta])) & (lab > 0)
    r0, r1 = j["ref_trav"]
    ref = np.median(orig[r0:r1, wx0:wx1].astype(np.float32).mean(axis=2), axis=0)[None, :]
    k = 2 * j["alcance_sombra"] + 1
    perto = cv2.dilate(ligada.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    folha = cv2.dilate(ligada.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    sombra = perto & (lum < ref - j["sombra"]) & ~folha
    # quanto pode sair: borda irregular (ruído suave) entre o mínimo e o máximo de cada lado
    rng = np.random.default_rng(q["semente"])
    h, w = lum.shape
    ys, xs = np.mgrid[wy0:wy1, wx0:wx1].astype(np.float32) + 0.5

    def ruido(n_, a, b):
        v = cv2.GaussianBlur(rng.normal(0, 1, (1, n_)).astype(np.float32), (0, 0), 4.0)[0]
        v = (v - v.min()) / max(float(np.ptp(v)), 1e-6)
        return a + (b - a) * v

    baixo = ruido(w, *q["baixo"])[None, :]
    esq = ruido(h, *q["lados"])[:, None]
    dir_ = ruido(h, *q["lados"])[:, None]
    # folga de cada px até o limite (o menor dos três lados); as pontas somem num degradê de 2 px, em
    # vez de um corte seco (que lia como papel rasgado)
    folga = np.minimum(np.minimum(fy1 + baixo - ys, xs - (fx0 - esq)), fx1 + dir_ - xs)
    pode = (ys >= fy0 + 1.5) & (folga > 0)
    miolo = (ys > fy0 + 1.5) & (ys < fy1 - 1.5) & (xs > fx0 + 1.5) & (xs < fx1 - 1.5)
    faixa = pode & ~miolo
    suave = np.clip(folga / 2.0, 0, 1)
    # só as folhas voltam (a sombra antiga do render, larga, borrava a borda); a sombra é desenhada:
    # curta, embaixo e à esquerda das folhas que saem, só no travertino
    fora = faixa & ligada & ~(dentro & ~faixa)            # só px de folha (sem o halo claro do render)
    a = fora.astype(np.float32)
    a = np.maximum(cv2.GaussianBlur(a, (0, 0), 0.5), a) * faixa * suave
    cur = out[wy0:wy1, wx0:wx1].astype(np.float32)
    tudo = np.maximum(dentro.astype(np.float32), a)
    M = np.float32([[1, 0, -1.5], [0, 1, 1.5]])
    sb = cv2.GaussianBlur(cv2.warpAffine(tudo, M, (w, h)), (0, 0), 1.0) * (1 - tudo) * (ys > fy0 + 2)
    cur *= (1 - 0.35 * sb)[..., None]
    a = a[..., None]
    out[wy0:wy1, wx0:wx1] = np.clip(cur * (1 - a) + reg * a, 0, 255).astype(np.uint8)
    # flores: o laranja da estrelítzia (pétalas e bico), recortado com borda suave e girado de matiz
    fq = q["flores"]
    forma = out.shape[:2]
    for (px, py), i, cor in fq["pos"]:
        (sx, sy), sr = fq["fonte"][i]
        rec = orig[sy - sr:sy + sr + 1, sx - sr:sx + sr + 1]
        hsv = cv2.cvtColor(rec, cv2.COLOR_BGR2HSV).astype(np.float32)
        b_, g_, r_ = [rec[..., c].astype(np.float32) for c in range(3)]
        flor = np.clip((r_ - g_ - 35) / 30, 0, 1) * np.clip((r_ - 120) / 40, 0, 1)
        flor = cv2.GaussianBlur(flor, (0, 0), 0.5)
        if cor:
            hsv[..., 0] = (hsv[..., 0] + fq["giro_matiz"][cor]) % 180
            if cor == "rosa":
                hsv[..., 1] *= 0.8
        img = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        s = fq["escala"]
        lado = rec.shape[0]
        M = cv2.getAffineTransform(np.float32([(0, 0), (lado, 0), (0, lado)]),
                                   np.float32([(px - lado * s / 2, py - lado * s / 2), (px + lado * s / 2, py - lado * s / 2),
                                               (px - lado * s / 2, py + lado * s / 2)]))
        im = cv2.warpAffine(img, M, forma[::-1], flags=cv2.INTER_AREA)
        al = cv2.warpAffine(flor, M, forma[::-1], flags=cv2.INTER_AREA)[..., None]
        out[:] = np.clip(out * (1 - al) + im * al, 0, 255).astype(np.uint8)
    print(f"    jardim de inverno: folhas um pouco para fora (sem a escada) e {len(fq['pos'])} flores tropicais")
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
    print("[7] CPD: vaso inventado")
    out = vaso_cpd(out)
    print("[8] área de serviço: as duas máquinas")
    out = maquinas(out)
    print("[9] área de serviço descoberta: X tracejado")
    out = x_descoberta(out, A)
    print("[10] DCE: cama, criado-mudo e armário até o teto")
    out = dce(out)
    print("[11] WC DCE 1: vaso a mais no lugar do chuveiro")
    out = wc_dce(out)
    print("[12] arcos das portas sobre o granito")
    out = arcos_granito(out, A)
    print("[13] pontos claros do granito")
    out = pontos_granito(out, orig, A)
    print("[14] pilar à direita do lavabo")
    out = pilar(out)
    print("[15] lavabo: cuba esculpida, torneira da esquerda")
    out = lavabo(out)
    print("[16] escritório: arranjo de flores")
    out = arranjo(out, orig)
    print("[17] louceiro: veio de marcenaria")
    out = veio_louceiro(out, orig)
    print("[18] escada: sombreamento de subida, sem linhas")
    out = escada(out)
    print("[19] jardim de inverno: um pouco para fora, com flores")
    out = jardim_flores(out, orig)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

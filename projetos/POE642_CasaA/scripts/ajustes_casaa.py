#!/usr/bin/env python3
"""Ajustes, sem IA, das imagens aprovadas da Casa A (POE 642) depois da conferência com o PDF da Casa A.

A conferência (`conferencia_casaa.py`, mapas `renders/POE642_CasaA_PH_<Pavimento>_conferencia.jpg`) listou as
divergências entre as imagens aprovadas e os PDFs do cliente da Casa A. Cada item corrigido entra aqui, um por
vez, no quadro da imagem aprovada (2000 px). A saída é `renders/<imagem aprovada>_ajustes.png`, que é a que vai
aos nomes e áreas (`rotulos_casaa.py`), às pranchas e ao PDF.

Itens:
  Subsolo 1. Banho de serviço (pedido do usuário, 19/10/26): o chuveiro e as duas folhas de vidro do box, do PDF,
     como os aprovados da Casa E.
  Subsolo 2. Sauna (pedido do usuário, 19/10/26: "Eu quero que você traga esse banco de volta"). O banco do PDF
     é horizontal, ao longo da parede de baixo, de parede a parede; a faixa vertical à esquerda, no tom do piso
     da piscina, é a passagem da sauna para a piscina e fica como piso ("o banco não é em L"). Na v6 o banco
     tinha virado piso: sobrou só uma faixa um pouco mais clara, sem a borda. Ele volta como o banco aprovado
     da sauna da Casa E: o travertino da própria faixa, a borda marcada por uma linha fina, uma sombra discreta
     no piso, que é mais baixo, e um brilho leve na quina do banco.
  Subsolo 3. Escada que desce do deck (pedido do usuário, 19/10/26): depois da linha de corte do PDF (a
     diagonal, que não é desenhada), os degraus no travertino do Subsolo, visíveis; antes dela, esmaecidos.
  Subsolo 4. Portas de vidro da academia (pedido do usuário, 19/10/26): para a circulação e para o hall, as
     folhas de vidro do PDF, claras e finas como o vidro da sauna, no lugar do traço preto do motor.
  Subsolo 5. Janelas (pedido do usuário, 19/10/26): a do banho de serviço e a da circulação para o depósito, na
     geometria do PDF (peitoril, faces da parede, vidro, caixilhos e retornos), no lugar da peça cinza do motor.
  Subsolo 6. Circulação (pedido do usuário, 19/10/26): sai o traço preto ao longo da borda esquerda, que o PDF
     não tem.
  Subsolo 7. Depósito e circulação interna (pedido do usuário, 19/10/26): o piso sem as juntas das placas, contínuo,
     com a textura do próprio render, na luz dele.
  Subsolo 8. Banhos feminino e masculino (pedido do usuário, 19/10/26): as cubas no tamanho do PDF (calhas quase da
     largura da bancada), como as cubas aprovadas da Casa E.
  Subsolo 9. Boxes dos chuveiros (pedido do usuário, 19/10/26): na ducha ao lado da sauna e no banho feminino, as
     folhas de vidro de correr do PDF, como as do box do banho de serviço.
  Subsolo 10. Divisória entre os banhos feminino e masculino (pedido do usuário, 19/10/26): não é parede; entra como
     no PDF (camada das bancadas), peça clara no tom das bancadas, com as peças finas em cinza.
  Subsolo 11. Bege Bahia (pedido do usuário, 19/10/26): a área de circulação (era travertino), o depósito e a
     circulação interna no Bege Bahia aprovado (o do 1º Pavimento, que foi ao Térreo), com a sombra do render; a
     escada do deck tira dele a textura do degrau.
  Subsolo 12. Banho de serviço (pedido do usuário, 19/10/26): a bancada da pia e a cuba, nas medidas do PDF, no
     padrão das cubas aprovadas.
  Subsolo 13. Escada do deck (pedido do usuário, 19/10/26): abaixo dela, entre o deck e a circulação, o gramado do
     Térreo, no lugar do branco.
  Térreo 1. Pilares (pedido do usuário, 19/10/26): os três redondos da varanda e o quadrado junto ao gourmet,
     em marrom no render, no preto das paredes e na geometria do PDF, como o pilar do Térreo da Casa E.
  Térreo 2. Sala de estar (pedido do usuário, 19/10/26): o sofá curvo do PDF acompanhando o tapete pela esquerda,
     com as almofadas, a poltrona da direita e a mesinha na ponta do sofá (clones do render).
  Térreo, rejuntes (pedido do usuário, 19/10/26): o travertino do piso interno contínuo, sem as juntas nem os
     degraus de tom das placas, com a textura e a luz do próprio render.
  Térreo 8. Jardim de 4,79 m² (pedido do usuário, 19/10/26): verde, com o gramado do Térreo e as três touceiras do
     PDF (clones da palmeira em estrela do jardim lateral do render).
  Térreo, tanques (pedido do usuário, 19/10/26): na área de serviço, a bancada com os dois tanques de louça e as
     torneiras de parede, nas medidas do PDF.
  Térreo, gás (pedidos do usuário, 19/10/26): o piso em granito marrom e a porta de duas folhas com os arcos.
  Térreo, porta do jardim (pedido do usuário, 19/10/26): a folha e o arco da porta do jardim para a área descoberta.
  Térreo, portões (pedido do usuário, 19/10/26): os portões de correr dos dois lados da área descoberta, do PDF.

Uso (da pasta POE642_CasaA/scripts/):
  python3 ajustes_casaa.py Subsolo     # -> ../renders/POE642_CasaA_PH_Subsolo_final_ajustes.png (+ _camada.png)
  python3 ajustes_casaa.py Terreo      # -> ../renders/POE642_CasaA_PH_Terreo_final_bege_barlavento_ajustes.png
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
CASA = AQUI.parent
APROVADAS = {"Subsolo": CASA / "renders/POE642_CasaA_PH_Subsolo_final.png",
             "Terreo": CASA / "renders/POE642_CasaA_PH_Terreo_final_bege_barlavento.png"}

# Subsolo 2: o banco da sauna, em px da imagem aprovada (2000 x 1116). As faces de dentro das paredes da
# esquerda, da direita e de baixo foram medidas na imagem (625,0; 717,5; 845,3); a borda do banco é a linha do
# PDF (830,3 no quadro comum), levada à imagem pelo afim da base (-3,6 px em y), e coincide com o fim da
# sombra que a v6 já tinha junto à porta.
# Os números da sauna da Casa E (sombra 0,14 em 1 px, linha 0,22 em 0,35 px) quase não aparecem aqui: esta
# imagem tem 2000 px e é ampliada para 3840 na prancha. A borda fica um pouco mais marcada e o tampo do banco 3%
# mais claro, para ler como uma peça mais alta que o piso, ainda discreto.
BANCO_SAUNA = {"ret": (625.0, 826.7, 717.5, 845.3),
               "sombra": (0.18, 1.6),        # no piso, acima da borda: força e alcance (px)
               "brilho": (0.05, 0.45),       # na quina do banco: força e largura (px)
               "linha": ((70, 78, 86), 0.35, 0.6),   # cor, força e largura (px)
               "clarear": 1.03}              # tampo do banco


# o Bege Bahia aprovado da Casa A: o mármore das varandas do 1º Pavimento (os mesmos trechos que foram ao Térreo,
# `retoque_bege_bahia_terreo.FONTES_1PAV`), tecido por image quilting
BEGE_1PAV = CASA / "renders/POE642_CasaA_PH_1Pavimento_v7_final2.png"


def textura_bege(alto, largo, semente=642):
    from retoque_bege_bahia_terreo import quilting, FONTES_1PAV
    p1 = cv2.imread(str(BEGE_1PAV)).astype(np.float32)
    fontes = []
    for x0, y0, x1, y1 in FONTES_1PAV:
        f = p1[y0:y1, x0:x1]
        fontes += [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    return quilting(fontes, alto, largo, p=36, sobra=10, rng=np.random.default_rng(semente))


def cobertura_linhas(y0, y1, ya, yb, n=16):
    """Fração de cada linha de pixel (ya..yb-1) coberta pela faixa [y0, y1) em y."""
    ys = np.arange(ya, yb)[:, None] - 0.5 + (np.arange(n)[None, :] + 0.5) / n
    return ((ys >= y0) & (ys < y1)).mean(axis=1)


def cobertura_colunas(x0, x1, xa, xb):
    xs = np.arange(xa, xb).astype(np.float64)
    return np.clip(np.minimum(xs + 0.5, x1) - np.maximum(xs - 0.5, x0), 0, 1)


def banco_sauna(out):
    q = BANCO_SAUNA
    x0, yb, x1, y1 = q["ret"]
    xa, xb = int(np.floor(x0)), int(np.ceil(x1))
    forca, alcance = q["sombra"]
    ya, yz = int(np.floor(yb - alcance - 1)), int(np.ceil(yb + 2))
    # o tampo do banco, um pouco mais claro que o piso
    yt = int(np.ceil(yb))
    tampo = out[yt:int(np.ceil(y1)), xa:xb].astype(np.float32)
    cxt = cobertura_colunas(x0, x1, xa, xb)[None, :, None]
    out[yt:int(np.ceil(y1)), xa:xb] = np.clip(np.round(tampo * (1 + (q["clarear"] - 1) * cxt)), 0, 255).astype(np.uint8)
    reg = out[ya:yz, xa:xb].astype(np.float32)
    cx = cobertura_colunas(x0, x1, xa, xb)[None, :, None]
    # sombra no piso, acima da borda, mais forte junto a ela (seis faixas, como na Casa E)
    for k in range(6):
        c = cobertura_linhas(yb - alcance * (k + 1) / 6, yb, ya, yz)[:, None, None]
        reg *= 1 - forca / 6 * c * cx
    # brilho leve na quina do banco
    fb, lb = q["brilho"]
    c = cobertura_linhas(yb, yb + lb, ya, yz)[:, None, None] * cx
    reg = reg * (1 - fb * c) + 255 * fb * c
    # a linha fina da borda
    cor, fl, lg = q["linha"]
    c = cobertura_linhas(yb - lg / 2, yb + lg / 2, ya, yz)[:, None, None] * cx
    reg = reg * (1 - fl * c) + np.asarray(cor, np.float32) * fl * c
    out[ya:yz, xa:xb] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    banco da sauna: borda em y {yb} px, de x {x0} a {x1} (linha, sombra no piso e brilho na quina)")
    return out


# Subsolo 3. Escada que desce do deck para a circulação em frente à academia (pedido do usuário, 19/10/26): "tem
# uma linha diagonal discriminando até onde tem o esmaecimento [...] até o terceiro degrau de uma pessoa que está
# vindo de cima para baixo é esmaecido. Do terceiro degrau, depois dessa linha diagonal, já tem que ter a cor do
# subsolo, a cor do degrau, a cor da textura do degrau, de forma visível. [...] essa linha em diagonal não precisa
# estar desenhada". A diagonal é a linha de corte da escada no PDF da Casa A (ARQ_ESCADAS E RAMPAS); antes dela,
# vindo do deck, os degraus ficam como estão (esmaecidos, com o deck). Depois dela, os degraus são refeitos com a
# textura do travertino da circulação, na cor creme da escada (a da legenda), nos espelhos do PDF (a v6 tinha um
# degrau a menos no fim), sem linhas e
# com o sombreamento de descida aprovado nas Casas D e E: cada degrau um pouco mais escuro que o de cima e a
# sombra curta de cada espelho no degrau de baixo, à direita dele (a escada desce da esquerda para a direita).
# Medidas do PDF no quadro comum (2000 px), levadas à imagem pelo afim da base (x' = 0,99911 x - 0,000617 y +
# 1,542; y' = 0,000113 x + 0,99973 y - 3,617): diagonal de (479,9; 551,0) a (498,7; 588,6), espelhos em x 489,2
# a 563,9 (o último é a borda com a circulação). Topo e base: as bordas que a imagem já tem (y 548 e 585,5).
ESCADA = {"diagonal": ((480.67, 547.29), (499.44, 584.88)),
          "espelhos": [480.66, 489.96, 499.25, 508.64, 517.93, 527.22, 536.61, 545.90, 555.19, 564.58],
          "faixa_y": (548.6, 585.2),
          # a textura do degrau: o Bege Bahia da circulação (item 11; antes, o travertino que o motor tinha feito
          # nela), num trecho do tamanho deste (largura x altura, px)
          "fonte": (110, 170),
          # a cor do degrau: o creme da legenda desta escada (#D8CDB4, `retangulos` do Subsolo na config), no tom
          # em que o travertino da base (#DCD9CA) saiu nesta imagem (ganho por canal 1,017; 1,001; 1,044, BGR)
          "cor": (183, 205, 226),
          "escurecer": 0.06,                 # do degrau de cima ao de baixo
          "sombra": (0.25, 2.5)}             # força e alcance (px), à direita de cada espelho


def escada(out):
    q = ESCADA
    (dx0, dy0), (dx1, dy1) = q["diagonal"]
    esp = np.asarray(q["espelhos"])
    ya0, ya1 = q["faixa_y"]
    forca, alc = q["sombra"]
    xa, xb = int(np.floor(esp[0])) - 1, int(np.ceil(esp[-1] + alc)) + 1
    ya, yb = int(np.floor(ya0)), int(np.ceil(ya1))
    h, w = yb - ya, xb - xa
    ss = 8
    sub = (np.arange(ss) + 0.5) / ss - 0.5
    X = (np.arange(xa, xb)[:, None] + sub[None, :]).reshape(-1)          # subamostras em x
    Y = (np.arange(ya, yb)[:, None] + sub[None, :]).reshape(-1)
    XX, YY = np.meshgrid(X, Y)
    dentro = (YY >= ya0) & (YY < ya1) & (XX < esp[-1])
    xd = dx0 + (YY - dy0) * (dx1 - dx0) / (dy1 - dy0)
    dentro &= XX > xd                                                    # depois da linha de corte
    k = np.searchsorted(esp, XX) - 1                                     # degrau: entre os espelhos k e k+1
    dentro &= k >= 0
    n = len(esp) - 1
    tom = 1 - q["escurecer"] * np.clip(k, 0, n - 1) / (n - 1)
    d = XX - esp[np.clip(k, 0, n - 1)]
    fator = tom * (1 - forca * np.clip(1 - d / alc, 0, 1))
    # a circulação, logo depois do último espelho, também recebe a sombra curta dele (fica com a textura dela)
    circ = (YY >= ya0) & (YY < ya1) & (XX >= esp[-1]) & (XX < esp[-1] + alc)
    fcirc = 1 - forca * np.clip(1 - (XX - esp[-1]) / alc, 0, 1)

    def por_pixel(m):
        return m.reshape(h, ss, w, ss).mean(axis=(1, 3))

    reg = out[ya:yb, xa:xb].astype(np.float32)
    novo = reg * (1 - por_pixel(dentro))[..., None]
    src = textura_bege(q["fonte"][1], q["fonte"][0], semente=643)
    src *= np.asarray(q["cor"], np.float32) / src.reshape(-1, 3).mean(axis=0)
    for j in range(n):
        m = dentro & (k == j)
        c = por_pixel(m)
        if c.max() == 0:
            continue
        f = por_pixel(np.where(m, fator, 0)) / np.maximum(c, 1e-6)
        # um trecho diferente do travertino para cada degrau, para não repetir
        sx, sy = (7 + 23 * j) % (src.shape[1] - w), (11 + 37 * j) % (src.shape[0] - h)
        tex = src[sy:sy + h, sx:sx + w]
        novo += (c * f)[..., None] * tex
    c = por_pixel(circ)
    f = por_pixel(np.where(circ, fcirc, 1))
    novo = novo * (1 - c)[..., None] + (reg * f[..., None]) * c[..., None]
    out[ya:yb, xa:xb] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    print(f"    escada: degraus depois da linha de corte no creme da escada, com a textura do travertino ({int(por_pixel(dentro).sum())} px), "
          f"sem linhas, com o sombreamento de descida")
    return out


# Subsolo 1. Banho de serviço (pedido do usuário, 19/10/26: "siga com o chuveiro do banho de serviço"): faltavam o
# chuveiro e o vidro do box. No PDF da Casa A (ARQ_LOUÇAS E METAIS), o chuveiro sai da parede da esquerda (canopla,
# braço e ducha) e o box é fechado por duas folhas de vidro de correr, sobrepostas, da parede da esquerda até 982,3
# pt; o resto, até a parede da direita, é a passagem. Entram como os aprovados da Casa E (`chuveiro` e `vidro_box`
# do `retoque_subsolo_casae.py`): a ducha quadrada de 20 cm (11,2 pt), centrada na ducha do PDF, o braço cromado
# até a parede e a canopla; e cada folha de vidro fina, com as bordas finas. Pontos do PDF (pt), levados à imagem
# pelo quadro comum e pelo afim da base.
CHUVEIRO_SERV = {"ducha": (933.2, 1086.4, 944.4, 1097.6),    # centro (938,8; 1092,0): a ducha do PDF
                 "braco": (930.5, 1091.3, 938.8, 1092.8),
                 "canopla": (929.9, 1090.4, 930.5, 1093.6),
                 "vidros": [(929.9, 1121.8, 971.6, 1123.2), (940.6, 1123.2, 982.3, 1124.6)]}
# quadro comum (2000 px) -> imagem aprovada de cada pavimento (SIFT entre a base e a imagem, no quadro comum)
AFIM_QR = {"Subsolo": ((0.99911, -0.000617, 1.542), (0.000113, 0.99973, -3.617)),     # o do banco e da escada
           "Terreo": ((1.01177, -0.000681, 0.608099), (-0.000652, 1.009677, -7.747429))}  # 45 pontos, 0,6 px


def pdf_pavimento(chave):
    """A página do PDF da Casa A do pavimento e a função pt do PDF -> px da imagem aprovada."""
    import json
    import pymupdf
    import rotulos_casaa as A
    from opcoes_1pav_casae import quadro_pdf
    cfg = json.loads(A.CONFIG.read_text())
    q = A.PAVIMENTOS[chave]
    base = (A.CONFIG.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][chave]["base"]).resolve()
    pg = pymupdf.open(A.RAIZ / "_pdfs_cliente" / q["pdf"])[cfg["pavimentos"][chave]["pagina"]]
    at, lt = cv2.imread(str(base), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(A.CASA / q["sem_tela"]), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg, cfg, lt, at, wb, hb, 2000)
    (a, b, c), (d, e, f) = AFIM_QR[chave]

    def p2r(x, y):
        qx, qy = p2q(x, y)
        return a * qx + b * qy + c, d * qx + e * qy + f
    return pg, p2r


def chuveiro_servico(out):
    from retoque_subsolo_casae import chuveiro, vidro_box
    q = CHUVEIRO_SERV
    _, p2r = pdf_pavimento("Subsolo")
    for r in q["vidros"]:
        out = vidro_box(out, p2r, r)
    out = chuveiro(out, p2r, q["ducha"], q["braco"], q["canopla"])
    (x0, y0), (x1, y1) = p2r(*q["ducha"][:2]), p2r(*q["ducha"][2:])
    print(f"    banho de serviço: chuveiro na parede da esquerda (ducha em x {x0:.1f}-{x1:.1f}, y {y0:.1f}-{y1:.1f} px) "
          f"e as duas folhas de vidro do box")
    return out


# Subsolo 4. Portas de vidro da academia (pedido do usuário, 19/10/26: "portas de vidro não pretas da sauna da casa
# A"): nos dois lados da academia, para a circulação e para o hall, o motor fez as portas de correr como um traço
# preto com dentes. No PDF da Casa A (ARQ_PAREDE) são folhas de vidro de 2,83 pt (~1,6 px), duas a duas
# desencontradas: quatro do lado da circulação (as do meio mais para dentro da academia) e duas do lado do hall,
# com o batente fino em cima e embaixo. O traço preto sai (em cada linha de pixel, o piso de cada lado continua
# em espelho: o travertino da circulação, a madeira da academia, a soleira e o travertino do hall), e as folhas
# entram como o vidro da sauna: claras, com a borda fina, e a linha do meio do PDF (as duas metades da folha).
PORTAS_ACADEMIA = {
    "lados": [
        # faixa a limpar (px da imagem: x0, x1, linhas y0..y1), folhas e batentes (pt do PDF)
        {"nome": "da circulação", "faixa": (690, 705, 548, 779),
         "folhas": [(1145.32, 1233.19, 1148.15, 1340.62), (1148.15, 1336.09, 1150.99, 1443.52),
                    (1148.15, 1443.52, 1150.99, 1550.95), (1145.32, 1546.42, 1148.15, 1653.85)],
         "batentes": [(1145.32, 1230.92, 1156.66, 1233.19), (1145.32, 1653.85, 1156.66, 1656.12)]},
        {"nome": "do hall", "faixa": (972, 985, 548, 624),
         "folhas": [(1662.64, 1233.19, 1664.91, 1301.79), (1660.37, 1301.79, 1662.64, 1370.39)],
         "batentes": [(1660.37, 1230.92, 1666.89, 1233.19), (1655.55, 1230.92, 1660.37, 1232.34),
                      (1660.37, 1370.39, 1666.89, 1372.65), (1655.55, 1371.24, 1660.37, 1372.65)]}],
    # o traço do motor: o trecho abaixo desta luminância em volta do px mais escuro de cada linha (no fim do lado
    # da circulação ele é cinza, ~65 a 100), mais 1 px de cada lado, a borda dele
    "escuro": 120,
    # o vidro: claro, com a borda fina e escura (como a da sauna, que se lê) e a linha do meio mais clara
    "vidro": (226, 228, 228), "borda": ((70, 72, 74), 0.35), "meio": ((168, 171, 173), 0.25),
    "aluminio": (150, 153, 156)}


def tirar_traco(out, faixa, escuro):
    """Apaga o traço escuro de cada linha da faixa: os px de cada lado do meio dele recebem, em espelho, o piso
    do seu lado."""
    x0, x1, y0, y1 = faixa
    n = 0
    for y in range(y0, y1 + 1):
        lum = out[y, x0:x1].astype(np.float32).mean(axis=1)
        i = int(np.argmin(lum))
        if lum[i] >= escuro:
            continue
        a, b = i, i                          # o trecho escuro em volta do px mais escuro da linha
        while a > 0 and lum[a - 1] < escuro:
            a -= 1
        while b < len(lum) - 1 and lum[b + 1] < escuro:
            b += 1
        a, b = max(a - 1, 0), min(b + 1, x1 - x0 - 1)
        meio = (a + b) / 2
        for i in range(a, b + 1):
            if i <= meio:
                out[y, x0 + i] = out[y, x0 + a - 1 - (i - a)]
            else:
                out[y, x0 + i] = out[y, x0 + b + 1 + (b - i)]
            n += 1
    return n


def portas_academia(out):
    from retoque_subsolo_casae import Tela
    q = PORTAS_ACADEMIA
    _, p2r = pdf_pavimento("Subsolo")
    for lado in q["lados"]:
        n = tirar_traco(out, lado["faixa"], q["escuro"])
        caixa = [f(v) for f, v in zip((min, min, max, max), zip(*(lado["folhas"] + lado["batentes"])))]
        tl = Tela(out, p2r, caixa)
        for b in lado["batentes"]:
            m = tl.ret(b)
            tl.pintar(m, q["aluminio"])
            tl.contorno(m, *q["borda"][::-1])
        for f in lado["folhas"]:
            m = tl.ret(f)
            tl.pintar(m, q["vidro"])
            xm = (f[0] + f[2]) / 2
            tl.pintar(m & tl.ret((xm - 0.25, f[1], xm + 0.25, f[3])), q["meio"][0])
            tl.contorno(m, q["borda"][1], q["borda"][0])
        out = tl.gravar()
        print(f"    lado {lado['nome']}: traço preto apagado ({n} px, o piso de cada lado), "
              f"{len(lado['folhas'])} folhas de vidro e {len(lado['batentes'])} batentes do PDF")
    return out


# Subsolo 5. Janelas (pedido do usuário, 19/10/26: "melhore o aspecto das janelas"): a do banho de serviço (para a
# circulação) e a da circulação para o depósito. O motor fez cada uma como uma peça cinza de cantos arredondados,
# com a borda grossa e borrada, um pouco para fora da parede. No PDF da Casa A (ARQ_PAREDE) é o vão na parede com o
# vidro fino no meio, os caixilhos nas pontas, os retornos da parede e as faces da parede passando pelo vão (o
# peitoril). Entram nessa geometria: o peitoril claro (o quartzo das bancadas), as duas faces em linha fina, o
# vidro como o das portas da academia, os caixilhos em alumínio e os retornos no preto das paredes; acima e
# abaixo do vão, a parede preta. Fora do vão, a borda escura da peça do motor volta ao piso do lado.
JANELAS = [
    {"nome": "do banho de serviço",
     "vao": (1009.25, 1066.51, 1017.76, 1111.87),
     "paredes": [(1009.25, 1060.0, 1017.76, 1066.51), (1009.25, 1111.87, 1017.76, 1118.0),
                 (1013.22, 1066.51, 1017.76, 1068.21), (1013.22, 1110.17, 1017.76, 1111.87)],
     "faces": [(1009.25, 1066.51, 1111.87), (1017.76, 1068.21, 1110.17)],
     "caixilhos": [(1010.39, 1066.51, 1013.22, 1068.5), (1010.39, 1109.88, 1013.22, 1111.87)],
     "vidro": (1010.39, 1068.5, 1014.64, 1109.88)},
    {"nome": "da circulação para o depósito",
     "vao": (1145.32, 1077.85, 1156.66, 1134.54),
     "paredes": [(1145.32, 1071.0, 1156.66, 1077.85), (1145.32, 1134.54, 1156.66, 1141.0),
                 (1145.32, 1077.85, 1149.85, 1079.55), (1152.69, 1077.85, 1156.66, 1079.55),
                 (1145.32, 1132.84, 1149.85, 1134.54), (1152.69, 1132.84, 1156.66, 1134.54)],
     "faces": [(1145.32, 1079.55, 1132.84), (1156.66, 1079.55, 1132.84)],
     "caixilhos": [(1149.85, 1077.85, 1152.69, 1079.83), (1149.85, 1132.56, 1152.69, 1134.54)],
     "vidro": (1148.44, 1079.83, 1152.69, 1132.56)}]
JANELA = {"peitoril": (225, 232, 236),     # BGR de #ECE8E1, o quartzo das bancadas
          "face": ((90, 92, 94), 0.35),    # cor e largura (px) das faces da parede no vão
          "fora": (1.6, 25)}               # faixa fora do vão (px) e quanto mais escura que o piso vira piso


def limpar_fora(out, x0, x1, y0, y1, faixa, limiar):
    """Nos px logo fora do vão (de cada lado), o que é bem mais escuro que o piso logo adiante vira esse piso."""
    for y in range(int(np.floor(y0)), int(np.ceil(y1))):
        for lado, borda in ((-1, x0), (1, x1)):
            xs = [int(np.floor(borda - faixa)) + i for i in range(int(np.ceil(faixa)) + 1)] if lado < 0 else \
                 [int(np.floor(borda)) + i for i in range(int(np.ceil(faixa)) + 1)]
            xs = [x for x in xs if (x + 0.5 < borda if lado < 0 else x + 0.5 > borda)]
            ref = out[y, xs[0] - 3:xs[0] - 1] if lado < 0 else out[y, xs[-1] + 2:xs[-1] + 4]
            piso = ref.astype(np.float32).mean(axis=0)
            for x in xs:
                if out[y, x].astype(np.float32).mean() < piso.mean() - limiar:
                    out[y, x] = np.clip(np.round(piso), 0, 255).astype(np.uint8)


def janelas(out):
    from retoque_subsolo_casae import Tela
    q, pa = JANELA, PORTAS_ACADEMIA
    _, p2r = pdf_pavimento("Subsolo")
    k = 0.5483                               # px por pt nesta imagem
    for j in JANELAS:
        (x0, y0), (x1, y1) = p2r(*j["vao"][:2]), p2r(*j["vao"][2:])
        limpar_fora(out, x0, x1, y0, y1, *q["fora"])
        caixa = [f(v) for f, v in zip((min, min, max, max), zip(*(j["paredes"] + [j["vao"]])))]
        tl = Tela(out, p2r, caixa)
        viz = tl.reg.reshape(-1, 3)
        preto = np.median(viz[viz.mean(axis=1) < 40], axis=0)
        tl.pintar(tl.ret(j["vao"]), q["peitoril"])
        for r in j["paredes"]:
            tl.pintar(tl.ret(r), preto)
        cor, larg = q["face"]
        for x, fy0, fy1 in j["faces"]:
            tl.pintar(tl.ret((x - larg / k / 2, fy0, x + larg / k / 2, fy1)), cor)
        for r in j["caixilhos"]:
            m = tl.ret(r)
            tl.pintar(m, pa["aluminio"])
            tl.contorno(m, pa["borda"][1], pa["borda"][0])
        v = j["vidro"]
        m = tl.ret(v)
        tl.pintar(m, pa["vidro"])
        xm = (v[0] + v[2]) / 2
        tl.pintar(m & tl.ret((xm - 0.25, v[1], xm + 0.25, v[3])), pa["meio"][0])
        tl.contorno(m, pa["borda"][1], pa["borda"][0])
        out = tl.gravar()
        print(f"    janela {j['nome']}: vão x {x0:.1f}-{x1:.1f}, y {y0:.1f}-{y1:.1f} px; peitoril, faces, vidro, "
              f"caixilhos e retornos do PDF")
    return out


# Subsolo 6. Traço preto no fim da circulação (pedido do usuário, 19/10/26: "Esse traço preto no fim da área de
# circulação não existe"): ao longo da borda esquerda da circulação, ~5 px para dentro do travertino, o motor fez
# um traço preto vertical, da escada do deck até a parede de baixo. No PDF da Casa A a circulação só termina (a
# borda do piso, sem linha). O traço sai como o das portas da academia: em cada linha, o travertino de cada lado
# continua em espelho.
TRACO_CIRCULACAO = {"faixa": (566, 584, 585, 845), "escuro": 140}   # px da imagem: x0, x1, linhas y0..y1 (846: a parede)


def traco_circulacao(out):
    n = tirar_traco(out, TRACO_CIRCULACAO["faixa"], TRACO_CIRCULACAO["escuro"])
    print(f"    traço preto da borda da circulação apagado ({n} px, o travertino de cada lado)")
    return out


# Subsolo 7. Juntas do depósito e da circulação interna (pedido do usuário, 19/10/26: "As marcações de juntas não
# existem na área de depósito e nem na circulação interna (entre banho de serviço e depósito)"). O piso desses dois
# ambientes (Bege Bahia na legenda) saiu como placas de ~44 x 22 px, cada uma num tom, com a junta marcada (linhas
# em x 661, 749, 793, 837, 880 e 925 e em y 478, 496 e 522). O piso volta contínuo, com a textura do próprio
# render: tecida (image quilting, como o Bege Bahia aprovado do Térreo) de miolos de placas, cada miolo normalizado
# pelo seu tom, e posta na luz do render (o tom médio do piso em volta, suavizado o bastante para as placas
# sumirem e a sombra junto às paredes ficar). Ficam como estão as paredes, a porta do depósito com o arco e a peça
# junto à parede de baixo.
JUNTAS = {
    # ambientes (px da imagem: x0, y0, x1, y1), por dentro das paredes e das janelas
    "areas": [(702, 455, 974, 541), (626, 455, 695, 538)],
    # miolos de placas, longe das juntas, das paredes, da porta e da sombra da parede da direita
    "fontes": [(753, 458, 790, 476), (797, 458, 834, 476), (841, 458, 877, 476), (884, 458, 921, 476),
               (753, 499, 790, 520), (797, 499, 834, 520), (841, 499, 877, 520), (884, 499, 921, 520),
               (797, 525, 834, 539), (841, 525, 877, 539)],
    "proteger": [(699, 524, 746, 545)],      # a peça junto à parede de baixo do depósito (com a sua sombra)
    "piso_min": 100,                         # abaixo disso é parede ou peça
    "linha": 18,                             # traço fino mais escuro que o piso em volta (o arco da porta)
    "luz_sigma": (14, 8),                    # suavização da luz (x, y): mais que uma placa, menos que a sala
    "p": 12}


def juntas(out):
    from retoque_bege_bahia_terreo import quilting
    q = JUNTAS
    fontes = []
    for x0, y0, x1, y1 in q["fontes"]:
        g = out[y0:y1, x0:x1].astype(np.float32)
        g = g / g.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    for k, (x0, y0, x1, y1) in enumerate(q["areas"]):
        reg = out[y0:y1, x0:x1].astype(np.float32)
        lum = reg.mean(axis=2)
        piso = lum >= q["piso_min"]
        piso &= lum - cv2.GaussianBlur(lum, (0, 0), 2) > -q["linha"]          # o arco e outros traços finos
        for a, b, c, d in q["proteger"]:
            piso[max(b - y0, 0):max(d - y0, 0), max(a - x0, 0):max(c - x0, 0)] = False
        piso = cv2.erode(piso.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        m = piso.astype(np.float32)
        sx, sy = q["luz_sigma"]
        luz = cv2.GaussianBlur(reg * m[..., None], (0, 0), sigmaX=sx, sigmaY=sy) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sigmaX=sx, sigmaY=sy), 1e-3)[..., None]
        tex = quilting(fontes, y1 - y0, x1 - x0, p=q["p"], sobra=max(3, q["p"] // 3), candidatos=600,
                       rng=np.random.default_rng(642 + k))
        a = cv2.GaussianBlur(m, (0, 0), 0.5) * m
        novo = reg * (1 - a[..., None]) + tex * luz * a[..., None]
        out[y0:y1, x0:x1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
        print(f"    {'depósito' if k == 0 else 'circulação interna'}: piso contínuo, sem juntas ({int(piso.sum())} px)")
    return out


# Subsolo 8. Cubas dos banhos feminino e masculino (pedido do usuário, 19/10/26: "as cubas dos banhos femininos e
# masculinos são maiores"). O motor fez em cada bancada uma cuba branca pequena (~16 x 10 px). No PDF da Casa A
# (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS) a cuba é uma calha de ~32 x 15 px, quase da largura da bancada e de toda
# a profundidade, com uma faixa plana junto à parede do fundo, onde fica a torneira. Entra nessa geometria, como
# as cubas aprovadas da Casa E (`retoque_subsolo_casae.bancada_cuba`): a louça branca com o contorno fino, a
# bacia escurecendo da borda ao fundo, a válvula no meio e a torneira cromada saindo da parede, com a sombra
# curta. A bancada do render fica.
CUBAS_BANHOS = [
    {"nome": "feminino", "cuba": (1307.18, 1748.53, 1366.14, 1775.17), "bacia": (1308.31, 1749.66, 1365.0, 1768.37),
     "torneira": (1335.61, 1762.87, 1337.71, 1772.25)},
    {"nome": "masculino", "cuba": (1573.35, 1748.53, 1639.68, 1775.17), "bacia": (1574.48, 1749.66, 1638.55, 1768.37),
     "torneira": (1606.32, 1762.87, 1608.41, 1772.25)}]


def cubas_banhos(out):
    from retoque_subsolo_casae import (Tela, SOMBRA, LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO, CROMO,
                                       CROMO_CLARO, CROMO_ESCURO, SS)
    _, p2r = pdf_pavimento("Subsolo")
    for q in CUBAS_BANHOS:
        tl = Tela(out, p2r, q["cuba"])
        x0, y0, x1, y1 = q["cuba"]
        tl.pintar(tl.ret(q["cuba"], 1.0), LOUCA_CONTORNO)
        tl.pintar(tl.ret((x0 + 0.8, y0 + 0.8, x1 - 0.8, y1 - 0.8), 0.8), LOUCA)
        bx0, by0, bx1, by1 = q["bacia"]
        for i in range(6):                   # a bacia, da borda ao fundo
            k = i / 5
            cor = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
            ins = 0.6 + k * 3.0
            tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.6, 1.6 - k)), cor)
        vx, vy = tl.pt((bx0 + bx1) / 2, (by0 + by1) / 2)
        v = tl.vazia()
        cv2.circle(v, (int(vx), int(vy)), int(1.1 * SS), 255, -1)
        tl.pintar(v, CROMO_ESCURO)
        tx0, ty0, tx1, ty1 = q["torneira"]   # vem da parede do fundo (embaixo)
        m = tl.ret(q["torneira"], 0.8)
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, CROMO_ESCURO)
        tl.pintar(tl.ret((tx0 + 0.3, ty0 + 0.4, (tx0 + tx1) / 2, ty1 - 0.4), 0.4), CROMO_CLARO)
        base = tl.vazia()
        cx, cy = tl.pt((tx0 + tx1) / 2, ty1)
        cv2.circle(base, (int(cx), int(cy)), int(1.0 * SS), 255, -1)
        tl.pintar(base, CROMO)
        out = tl.gravar()
        (a, b), (c, d) = p2r(x0, y0), p2r(x1, y1)
        print(f"    cuba do banho {q['nome']}: x {a:.1f}-{c:.1f}, y {b:.1f}-{d:.1f} px, com a torneira da parede do fundo")
    return out


# Subsolo 9. Boxes dos chuveiros (pedido do usuário, 19/10/26: "faltando a representação dos boxes dos chuveiros, em
# vidro"): a ducha ao lado da sauna e o chuveiro do banho feminino. No PDF da Casa A (ARQ_LOUÇAS E METAIS) cada box
# é de correr: o trilho tracejado de parede a parede e duas folhas de vidro desencontradas; onde não há folha é a
# entrada do box (na ducha, à direita; no banho feminino, embaixo). O render não tem o vidro: na ducha, nada; no
# banho feminino, um traço escuro de cima a baixo, que sai (o travertino de cada lado continua). As folhas entram
# como as do box do banho de serviço (`vidro_box`, aprovado): cada uma na metade do trilho do PDF (1,4 pt), fina,
# clara e com a borda fina.
BOXES = [
    {"nome": "ducha ao lado da sauna",
     "folhas": [(1196.34, 1719.9, 1240.85, 1721.32), (1207.67, 1721.32, 1252.12, 1722.73)]},
    {"nome": "chuveiro do banho feminino", "traco": (846, 862, 786, 844),   # px da imagem: x0, x1, linhas y0..y1
     "folhas": [(1434.45, 1664.62, 1435.87, 1721.88), (1433.03, 1678.5, 1434.45, 1735.7)]}]


def boxes(out):
    from retoque_subsolo_casae import vidro_box
    _, p2r = pdf_pavimento("Subsolo")
    for q in BOXES:
        n = tirar_traco(out, q["traco"], 130) if "traco" in q else 0
        for f in q["folhas"]:
            out = vidro_box(out, p2r, f)
        print(f"    box da {q['nome']}: {len(q['folhas'])} folhas de vidro do PDF" +
              (f"; traço escuro do render apagado ({n} px)" if n else ""))
    return out


# Subsolo 10. Divisória entre os banhos feminino e masculino (pedido do usuário, 19/10/26: "essa divisória não é
# parede. é outra coisa!"). O motor a fez como parede preta (~3 px). No PDF da Casa A ela não está na camada das
# paredes: está na das bancadas (ARQ_BANCADAS), com o miolo branco (na ARQ_PAREDE o trecho é branco, vão) e as
# peças finas em cinza por dentro, em degrau, como as placas de pedra das bancadas, com ~19 cm no total. Entra na
# geometria do PDF como peça clara, no tom das bancadas do render, com a borda fina e as peças finas do PDF em
# cinza; o registro pequeno do lado do banho feminino (ARQ_LOUÇAS E METAIS), cromado. O preto do motor sai antes
# (o piso de cada lado continua); em cima e embaixo ficam as paredes.
DIVISORIA = {"caixa": (1490.01, 1664.62, 1500.78, 1775.17),
             "traco": (882, 894, 786, 845),          # px da imagem: x0, x1, linhas y0..y1 (o preto do motor)
             # as peças finas (pt do PDF): as cinzas da ARQ_BANCADAS e a placa da direita (as linhas de 0,85 pt)
             "pecas": [(1490.01, 1664.62, 1493.98, 1665.76), (1491.71, 1665.76, 1492.85, 1692.97),
                       (1490.01, 1692.97, 1496.81, 1694.1), (1495.68, 1694.1, 1496.81, 1775.17),
                       (1490.01, 1774.04, 1495.68, 1775.17), (1494.05, 1664.62, 1495.18, 1692.97)],
             "registro": (1490.79, 1675.11, 1491.71, 1682.49),
             "pedra": (192, 209, 222),               # BGR da bancada do banho feminino no render
             "peca": (138, 141, 143), "borda": ((120, 122, 124), 0.3)}


def divisoria(out):
    from retoque_subsolo_casae import Tela, CROMO
    q = DIVISORIA
    n = tirar_traco(out, q["traco"], 120)
    _, p2r = pdf_pavimento("Subsolo")
    tl = Tela(out, p2r, q["caixa"])
    m = tl.ret(q["caixa"])
    tl.pintar(m, q["pedra"])
    for r in q["pecas"]:
        tl.pintar(tl.ret(r), q["peca"])
    tl.contorno(m, q["borda"][1], q["borda"][0])
    tl.pintar(tl.ret(q["registro"]), CROMO)
    out = tl.gravar()
    (a, b), (c, d) = p2r(*q["caixa"][:2]), p2r(*q["caixa"][2:])
    print(f"    divisória: preto do motor apagado ({n} px); peça clara do PDF em x {a:.1f}-{c:.1f}, y {b:.1f}-{d:.1f} px")
    return out


# Subsolo 11. Bege Bahia (pedido do usuário, 19/10/26: "esse piso da circulação é marmore bege bahia. Inclusive melhore
# a representação do bege bahia no depósito e na área de circulação"). A circulação ao longo da academia (do pé da
# escada do deck até a parede de baixo, a "área de circulação") tinha saído em travertino, e o depósito e a
# circulação interna num bege fosco, sem cara de mármore. Os três passam ao Bege Bahia aprovado da Casa A: o mármore
# das varandas do 1º Pavimento, que já foi ao Térreo (`textura_bege`), na cor dele, com a sombra suave do render
# (como no Térreo: a textura nova escurece onde o piso do render era mais escuro que o piso em volta, até 14%). A
# escada que desce do deck (item 3) passa a tirar a textura do degrau do mesmo Bege Bahia, no creme dela.
BEGE = {
    "areas": [
        # nome, caixa (px da imagem), semente; a faixa vai até as folhas de vidro da academia (o x de cada linha)
        ("área de circulação", (565, 543, 697, 846), 651),
        ("depósito", (695, 455, 974, 541), 652),          # com a soleira da porta, na parede da circulação interna
        ("circulação interna", (626, 455, 695, 538), 653)],
    "fora": [(619, 779, 700, 846),           # a sauna, com o vidro dela
             (694, 455, 702, 495),           # a janela da circulação para o depósito (item 5)
             (700, 529, 734, 546)],          # a folha da porta do depósito e a peça junto à parede de baixo
    "piso": (100, 245),                      # luminância do piso (fora: paredes, peças escuras e o branco do papel)
    # o arco da porta do depósito: o traço fino volta por cima do Bege Bahia, como escurecimento relativo (a razão
    # entre cada px e a mediana do piso em volta, na imagem de antes deste item)
    "arcos": [(700, 494, 737, 530)],
    "sombra": (0.86, 6)}                     # escurecimento máximo e suavização da luz (px)


def bege_bahia(out):
    q = BEGE
    folhas = [f for lado in PORTAS_ACADEMIA["lados"] if "circulação" in lado["nome"] for f in lado["folhas"]]
    _, p2r = pdf_pavimento("Subsolo")
    lim = [(p2r(f[0], f[1])[1], p2r(f[2], f[3])[1], p2r(f[0], f[1])[0]) for f in folhas]   # y0, y1, x da folha
    for nome, (x0, y0, x1, y1), semente in q["areas"]:
        reg = out[y0:y1, x0:x1].astype(np.float32)
        lum = reg.mean(axis=2)
        m = (lum >= q["piso"][0]) & (lum <= q["piso"][1])
        ys, xs = np.mgrid[y0:y1, x0:x1]
        for a, b, c, d in q["fora"]:
            m &= ~((xs >= a) & (xs < c) & (ys >= b) & (ys < d))
        if nome == "área de circulação":
            xmax = np.full(y1 - y0, 694.9)
            for fy0, fy1, fx in lim:
                k = (np.arange(y0, y1) + 0.5 >= fy0) & (np.arange(y0, y1) + 0.5 < fy1)
                xmax[k] = fx
            m &= xs + 0.5 <= xmax[:, None]
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
        mf = m.astype(np.float32)
        lum_m = cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), 7).astype(np.float32)
        sig = q["sombra"][1]
        viz = cv2.GaussianBlur(lum_m * mf, (0, 0), sig) / np.maximum(cv2.GaussianBlur(mf, (0, 0), sig), 1e-3)
        sombra = np.clip(viz / float(np.median(lum[m])), q["sombra"][0], 1.0)[..., None]
        tex = textura_bege(y1 - y0, x1 - x0, semente) * sombra
        for a, b, c, d in q["arcos"]:
            k = (xs >= a) & (xs < c) & (ys >= b) & (ys < d)
            if k.any():
                razao = np.clip(lum / np.maximum(cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), 7), 1), 0.4, 1.0)
                tex[k] *= np.where(razao < 0.97, razao, 1.0)[k][:, None]
        a = (cv2.GaussianBlur(mf, (0, 0), 0.5) * mf)[..., None]
        out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - a) + tex * a), 0, 255).astype(np.uint8)
        print(f"    {nome}: Bege Bahia do 1º Pavimento ({int(m.sum())} px), com a sombra suave do render")
    return out


# Subsolo 12. Bancada e cuba do banho de serviço (pedido do usuário, 19/10/26: "faltou a bancada da pia, com a cuba;
# ambos em suas respectivas dimensões"). O motor fez só um quadrado claro junto à parede da esquerda. No PDF da Casa
# A a bancada (ARQ_BANCADAS) tem 22,7 x 51,0 pt (~12 x 28 px), da parede da esquerda, com um recorte onde entra a
# cuba (ARQ_LOUÇAS E METAIS): quadrada, de cantos arredondados, 22,6 pt (~12 px), avançando além da bancada, com a
# bacia à direita e a torneira monocomando no lado da parede, a bica para a direita. Entram nessas medidas, no padrão
# das cubas aprovadas (item 8 e Casa E): a bancada no tom das bancadas do render, com a borda fina e a sombra curta;
# a cuba de louça com o contorno fino, a bacia escurecendo da borda ao fundo e a válvula; a torneira cromada.
BANCADA_SERV = {"bancada": (929.88, 1168.56, 952.56, 1219.58),
                "cuba": (936.73, 1182.77, 959.32, 1205.37),
                "bacia": (942.88, 1185.0, 957.1, 1203.14),
                "torneira": (938.6, 1192.65, 948.38, 1195.49),
                # o quadrado claro do motor passava ~1,5 px da bancada do PDF, para a direita: volta ao piso
                "limpar": (589, 593, 512, 542)}       # px da imagem: x0, x1, linhas y0..y1


def bancada_servico(out):
    from retoque_subsolo_casae import (Tela, SOMBRA, LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO, CROMO,
                                       CROMO_CLARO, CROMO_ESCURO, SS)
    q = BANCADA_SERV
    x0, x1, y0, y1 = q["limpar"]
    for y in range(y0, y1 + 1):              # o que sobra do quadrado do motor: o piso logo à direita
        piso = out[y, x1 + 1:x1 + 4].astype(np.float32).mean(axis=0)
        for x in range(x0, x1 + 1):
            if out[y, x].astype(np.float32).mean() > piso.mean() + 20:
                out[y, x] = np.round(piso).astype(np.uint8)
    _, p2r = pdf_pavimento("Subsolo")
    caixa = (q["bancada"][0], q["bancada"][1], q["cuba"][2], q["bancada"][3])
    tl = Tela(out, p2r, caixa)
    b = tl.ret(q["bancada"])
    tl.sombra(b, **SOMBRA)
    tl.pintar(b, DIVISORIA["pedra"])
    tl.contorno(b, 0.35, (150, 153, 155))
    c = tl.ret(q["cuba"], 2.0)
    tl.sombra(c, **SOMBRA)
    tl.pintar(c, LOUCA_CONTORNO)
    cx0, cy0, cx1, cy1 = q["cuba"]
    tl.pintar(tl.ret((cx0 + 0.8, cy0 + 0.8, cx1 - 0.8, cy1 - 0.8), 1.6), LOUCA)
    bx0, by0, bx1, by1 = q["bacia"]
    for i in range(6):                       # a bacia, da borda ao fundo
        k = i / 5
        cor = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
        ins = 0.4 + k * 2.6
        tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.6, 1.8 - k)), cor)
    vx, vy = tl.pt((bx0 + bx1) / 2 + 1.5, (by0 + by1) / 2)
    v = tl.vazia()
    cv2.circle(v, (int(vx), int(vy)), int(1.1 * SS), 255, -1)
    tl.pintar(v, CROMO_ESCURO)
    tx0, ty0, tx1, ty1 = q["torneira"]       # monocomando no lado da parede, a bica para a direita
    m = tl.ret(q["torneira"], 0.8)
    tl.sombra(m, **SOMBRA)
    tl.pintar(m, CROMO_ESCURO)
    tl.pintar(tl.ret((tx0 + 0.4, ty0 + 0.4, tx1 - 0.4, (ty0 + ty1) / 2), 0.4), CROMO_CLARO)
    base = tl.vazia()
    cx, cy = tl.pt(tx0 + 1.2, (ty0 + ty1) / 2)
    cv2.circle(base, (int(cx), int(cy)), int(1.0 * SS), 255, -1)
    tl.pintar(base, CROMO)
    out = tl.gravar()
    (a, b_), (c_, d) = p2r(*q["bancada"][:2]), p2r(*q["bancada"][2:])
    (e, f), (g, h) = p2r(*q["cuba"][:2]), p2r(*q["cuba"][2:])
    print(f"    banho de serviço: bancada x {a:.1f}-{c_:.1f}, y {b_:.1f}-{d:.1f} px; cuba x {e:.1f}-{g:.1f}, y {f:.1f}-{h:.1f} px")
    return out


# Subsolo 13. Gramado junto à escada do deck (pedido do usuário, 19/10/26: "ao termino dos degraus no sentido do subsolo,
# ou seja, a escada desce, no último degrau, após ele, há um gramado, que separa o último degrau da área de circulação
# do subsolo", com o recorte da prancha do Térreo). Abaixo da escada que desce do deck, entre a borda do deck
# esmaecido e a circulação, a prancha do Subsolo estava em branco; no Térreo ali é o gramado. Entra o gramado do
# próprio Térreo aprovado, no mesmo lugar (as duas imagens vão ao quadro comum, e o afim de uma à outra passa por ele),
# na cor dele, só onde o Subsolo está em branco: da escada até a parede de baixo do Subsolo, da borda esquerda do
# deck esmaecido até a circulação. A borda com o branco é suave (a parte branca de cada px).
GRAMADO_ESCADA = {"caixa": (376, 584, 575, 849),    # px da imagem do Subsolo: x0, y0, x1, y1
                  "branco": (230, 250)}             # rampa da borda: mínimo do px de 230 (nada) a 250 (tudo)


def gramado_escada(out):
    q = GRAMADO_ESCADA
    m = lambda k: np.vstack([np.float64(AFIM_QR[k]), [0, 0, 1]])
    s2t = m("Terreo") @ np.linalg.inv(m("Subsolo"))          # px do Subsolo -> px do Térreo
    terreo = cv2.imread(str(APROVADAS["Terreo"]))
    x0, y0, x1, y1 = q["caixa"]
    gx, gy = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
    mx = (s2t[0, 0] * gx + s2t[0, 1] * gy + s2t[0, 2]).astype(np.float32)
    my = (s2t[1, 0] * gx + s2t[1, 1] * gy + s2t[1, 2]).astype(np.float32)
    grama = cv2.remap(terreo, mx, my, cv2.INTER_LINEAR).astype(np.float32)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    lo, hi = q["branco"]
    a = np.clip((reg.min(axis=2) - lo) / (hi - lo), 0, 1)
    verde = (grama[..., 1] > grama[..., 2] + 8) & (grama[..., 1] > grama[..., 0] + 8)
    a *= cv2.GaussianBlur(verde.astype(np.float32), (0, 0), 0.7)
    out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - a[..., None]) + grama * a[..., None]), 0, 255).astype(np.uint8)
    # na emenda com a circulação sobrava o px claro da borda dela (contra o branco): vira a média dos dois lados
    for y in range(y0, y1):
        xs = np.nonzero(a[y - y0] > 0.5)[0]
        if len(xs):
            xl = x0 + xs.max()
            if xl + 2 < out.shape[1] and out[y, xl + 1].mean() > out[y, xl + 2].mean() + 12:
                out[y, xl + 1] = ((out[y, xl].astype(np.float32) + out[y, xl + 2]) / 2).astype(np.uint8)
    print(f"    gramado do Térreo abaixo da escada: {int((a > 0.5).sum())} px (x {x0}-{x1}, y {y0}-{y1})")
    return out


# Térreo 1. Pilares (pedido do usuário, 19/10/26: "siga com os pilares do térreo"): os três pilares redondos da
# varanda e o quadrado junto ao gourmet, que o motor fez em marrom, são os pilares estruturais do PDF da Casa A
# (camada EST - Pilar) e ficam no preto das paredes, como o pilar do Térreo da Casa E (`retoque_terreo_casae.pilar`),
# na geometria do PDF (o contorno preenchido de cada pilar, levado à imagem), com a borda antisserrilhada. O
# marrom do motor sai um pouco maior que o PDF (raio ~7,3 px contra 6,3 px, ~1 px a mais no quadrado): o anel de
# marrom que sobra fora do contorno do PDF volta ao piso de cada pixel (tira-se só a parte marrom da mistura).
PILARES = {"camada": "EST - Pilar",
           "parede": (770, 740, 900, 870),   # paredes do banho da varanda e do WC (px da imagem): o preto
           "janela": 14,                     # meia janela em volta de cada pilar (px)
           "fundo": (3, 8),                  # anel de fundo: distância ao contorno do PDF (px)
           "sigma": 2.5,                     # suavização do fundo de cada lugar (px)
           "anel": 2.5,                      # até onde, fora do contorno do PDF, o marrom do motor vai (px)
           "w_min": 0.15,                    # abaixo disso é o veio do piso, não o marrom
           "residuo": 30}                    # só é marrom o que está na mistura marrom-fundo


def pilares(out):
    from retoque_terreo_casae import poligono_aa
    q = PILARES
    a, b, c, d = q["parede"]
    viz = out[b:d, a:c].reshape(-1, 3)
    preto = np.median(viz[viz.astype(np.float32).mean(axis=1) < 40], axis=0).astype(np.float32)
    pg, p2r = pdf_pavimento("Terreo")
    n = 0
    for dr in pg.get_drawings():
        if dr.get("layer") != q["camada"] or dr["type"] != "f":
            continue                         # o círculo só traçado é o eixo da escada caracol
        pts = [p2r(it[1].x, it[1].y) for it in dr["items"]]
        al = poligono_aa(out.shape[:2], pts)
        ys, xs = np.nonzero(al)
        cx, cy = int(np.average(xs, weights=al[ys, xs])), int(np.average(ys, weights=al[ys, xs]))
        k = q["janela"]
        sl = np.s_[cy - k:cy + k + 1, cx - k:cx + k + 1]
        reg, alr = out[sl].astype(np.float32), al[sl]
        # o marrom do motor e o fundo em volta: cada pixel do anel é fundo + w (marrom - fundo). O fundo é o de
        # cada lugar (média suave dos pixels de fora, sem os pretos), porque em volta do pilar do gourmet há piso,
        # grama e a folha da porta; um fundo único clareava a borda de cima
        marrom = np.median(reg[alr > 0.99], axis=0)
        dist = cv2.distanceTransform((alr < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        fm = ((dist > q["fundo"][0]) & (dist < q["fundo"][1]) & (reg.mean(axis=2) > 60)).astype(np.float32)
        fundo = (cv2.GaussianBlur(reg * fm[..., None], (0, 0), q["sigma"])
                 / np.maximum(cv2.GaussianBlur(fm, (0, 0), q["sigma"]), 1e-4)[..., None])
        v = marrom - fundo
        w = np.clip(((reg - fundo) * v).sum(axis=2) / np.maximum((v * v).sum(axis=2), 1), 0, 1)
        w[np.linalg.norm(reg - (fundo + w[..., None] * v), axis=2) >= q["residuo"]] = 0
        w[(dist > q["anel"]) | (w < q["w_min"]) | (reg[..., 1] > reg[..., 2])] = 0   # longe, veio ou grama (verde)
        reg -= w[..., None] * v              # o marrom sai, fica o piso
        reg = reg * (1 - alr[..., None]) + preto * alr[..., None]
        out[sl] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        x0, y0 = np.min(pts, axis=0)
        x1, y1 = np.max(pts, axis=0)
        forma = "redondo" if len(pts) > 4 else "quadrado"
        print(f"    pilar {forma}: ({x0:.1f}, {y0:.1f}) - ({x1:.1f}, {y1:.1f}) px; marrom {marrom.astype(int).tolist()} "
              f"-> preto; anel fora do PDF: {float((w * (1 - alr)).sum()):.0f} px de marrom de volta ao piso")
        n += 1
    print(f"    {n} pilares no preto das paredes {preto.astype(int).tolist()}")
    return out



# Térreo 2. Sala de estar (pedido do usuário, 19/10/26: "siga com o item 2 do térreo"). No PDF da Casa A (camada ARQ_LAYOUT
# HUMANIZAÇÃO) o sofá curvo acompanha o tapete redondo pela esquerda, das 12h às 7h, com o encosto na borda do tapete
# (um pouco para fora dela) e o assento em C; sobre o assento, duas almofadas e duas almofadas redondas com pregas (os
# círculos com raios, que a conferência leu como vasos); na ponta de cima do sofá, uma mesinha redonda; à direita, a
# poltrona voltada para a mesa de centro. O motor pôs o sofá ao longo do alto do tapete, até a direita, sem a mesinha
# e sem a poltrona. Sem IA:
# 1. o sofá do motor sai: o tapete volta, copiado em volta do centro dele, no mesmo raio (a borda do tapete fica
#    contínua), de um setor livre à direita, em espelho;
# 2. o sofá do PDF entra no estilo do do render (o tecido creme, o rolo do encosto mais claro, a face do encosto que
#    escurece no vinco com o assento, a borda da frente arredondada e a sombra suave no tapete, da luz do alto à
#    direita, como a da mesa de centro); as divisões do encosto do PDF viram costura fina;
# 3. as almofadas do PDF, com volume e sombra curta; as redondas com as pregas e o botão;
# 4. a poltrona da direita é a poltrona de baixo à direita do render, girada para o contorno do PDF (o ângulo que
#    melhor cobre o contorno, com o encosto para a borda do tapete); a mesinha é a mesinha redonda entre as poltronas
#    de baixo; o pufe/mesinha do render junto ao sofá (o contorno grosso do PDF ali) volta por cima. Cada clone com a
#    sombra nova, na mesma luz.
SALA = {"caixa": (995, 180, 1145, 330),                  # janela de trabalho (px da imagem)
        "tapete": ((1073.27, 255.73), 62.91),           # centro e raio (o círculo da ARQ_MOBILIÁRIO)
        # o sofá do motor (px da imagem), com folga para a sombra dele
        "sofa_velho": [(1026.7, 213.3), (1038.3, 205.0), (1055.0, 200.0), (1073.3, 198.0), (1093.3, 198.7),
                       (1108.3, 203.3), (1118.0, 209.7), (1122.0, 218.3), (1119.3, 227.0), (1112.0, 232.3),
                       (1100.0, 234.0), (1086.7, 231.7), (1075.0, 229.7), (1063.3, 230.0), (1050.0, 231.7),
                       (1040.0, 233.7), (1032.7, 236.0), (1028.7, 240.7), (1028.7, 255.0), (1024.3, 260.3),
                       (1015.3, 261.7), (1007.0, 259.3), (1004.0, 252.0), (1004.3, 240.0), (1008.0, 231.0),
                       (1015.3, 224.3), (1021.7, 218.3)],
        "setor_livre": (-40.0, 15.0),                    # graus, anti-horário a partir do leste
        "pufe": ((1036.7, 251.7), 7.2),
        # pontos dentro de cada parte do sofá (px da imagem); a face do encosto é a região de 20 a 40 mil px (8x)
        "encosto": [(1052.5, 194.5), (1025.9, 211.2), (1009.7, 238.7)],
        "assento": [(1072.3, 213.5), (1030.1, 241.6)],
        "almofadas": [[(1052.8, 202.8), (1054.8, 207.0)], [(1022.2, 244.0), (1017.7, 242.4)]],
        "redondas": [((1044.1, 213.4), 4.7), ((1032.55, 223.05), 4.9)],
        "cores": {"assento": (206, 212, 232), "encosto": (213, 219, 237), "face": (204, 210, 229),
                  "almofada": (211, 217, 237)},       # BGR, do sofá e das almofadas do render
        "sombra": [(-1.4, 1.4, 2.0, 0.30), (0, 0, 0.9, 0.14)],   # dx, dy, sigma (px), força: no tapete
        "poltrona": {"fonte": (1815, 752, 1865, 805), "destino": (1865, 638, 1925, 698),   # pt do PDF
                     "angulo": 226.5, "desvio": (-3.09, 1.95)},
        "mesinha": {"fonte": ((1069.7, 294.5), 6.1), "destino": (1095.5, 222.05)}}


def caminhos_pdf(d, p2r, passos=16):
    """Polilinhas (px da imagem) de um desenho do PDF, uma por subcaminho; as curvas são amostradas."""
    out, atual, ult = [], [], None
    for it in d["items"]:
        if it[0] not in ("l", "c"):
            continue
        a, b = it[1], it[-1]
        if ult is None or abs(a.x - ult.x) + abs(a.y - ult.y) > 0.05:
            if atual:
                out.append(atual)
            atual = [p2r(a.x, a.y)]
        if it[0] == "l":
            atual.append(p2r(b.x, b.y))
        else:
            c1, c2 = it[2], it[3]
            for t in np.linspace(0, 1, passos)[1:]:
                x = (1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * c1.x + 3 * (1 - t) * t ** 2 * c2.x + t ** 3 * b.x
                y = (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * c1.y + 3 * (1 - t) * t ** 2 * c2.y + t ** 3 * b.y
                atual.append(p2r(x, y))
        ult = b
    if atual:
        out.append(atual)
    return [np.float64(c) for c in out]


def sala_estar(out):
    q = SALA
    pg, p2r = pdf_pavimento("Terreo")
    SS = 8
    X0, Y0, X1, Y1 = q["caixa"]
    W, H = (X1 - X0) * SS, (Y1 - Y0) * SS
    (CX, CY), R = q["tapete"]
    fonte = out[Y0:Y1, X0:X1].astype(np.float32)
    reg = fonte.copy()
    org = out.astype(np.float32)

    def ss(c):
        return np.int32(np.round((np.asarray(c, np.float64) - [X0, Y0]) * SS))

    def red(m):
        return cv2.resize(m.astype(np.float32) / (255 if m.dtype == np.uint8 else 1), (X1 - X0, Y1 - Y0),
                          interpolation=cv2.INTER_AREA)

    def dist(m):
        return cv2.distanceTransform((m > 0).astype(np.uint8), cv2.DIST_L2, 5) / SS

    def lisa(t):
        return t * t * (3 - 2 * t)

    def pintar(cor, tom, m):
        nonlocal reg
        a = red(m)[..., None]
        c = cv2.resize(np.float32(cor)[None, None] * tom[..., None] * (m[..., None] / 255.0), (X1 - X0, Y1 - Y0),
                       interpolation=cv2.INTER_AREA)
        reg = reg * (1 - a) + c

    def sombra(m, dx, dy, sig, forca):
        nonlocal reg
        sh = cv2.warpAffine(m.astype(np.float32) / 255, np.float32([[1, 0, dx * SS], [0, 1, dy * SS]]), (W, H))
        reg *= (1 - forca * red(cv2.GaussianBlur(sh, (0, 0), sig * SS) * (1 - m / 255.0)))[..., None]

    # 1. o sofá do motor sai: o tapete, copiado em volta do centro, do setor livre (em espelho)
    mv = np.zeros((Y1 - Y0, X1 - X0), np.uint8)
    cv2.fillPoly(mv, [np.int32(np.round(np.float64(q["sofa_velho"]) - [X0, Y0]))], 1)
    mv = cv2.dilate(mv, np.ones((3, 3), np.uint8)).astype(bool)
    ys, xs = np.mgrid[Y0:Y1, X0:X1] + 0.5
    rr, th = np.hypot(xs - CX, ys - CY), np.degrees(np.arctan2(CY - ys, xs - CX))
    (pcx, pcy), pr = q["pufe"]
    buraco = mv & (np.hypot(xs - pcx, ys - pcy) > pr + 1.3) & (rr <= R + 1.0)
    A0, A1 = q["setor_livre"]
    larg = A1 - A0
    t = np.mod(th - A0, 2 * larg)
    ts = np.radians(A0 + np.where(t < larg, t, 2 * larg - t))
    copia = cv2.remap(fonte, (CX + rr * np.cos(ts) - X0 - 0.5).astype(np.float32),
                      (CY - rr * np.sin(ts) - Y0 - 0.5).astype(np.float32), cv2.INTER_LINEAR)
    a = cv2.GaussianBlur(buraco.astype(np.float32), (0, 0), 0.6)[..., None] * (rr <= R + 1.0)[..., None]
    reg = reg * (1 - a) + copia * a

    # 2. o sofá do PDF: contorno, linhas (barreiras entre as partes) e as partes
    ds = [d for d in pg.get_drawings() if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO"
          and d["rect"].x0 >= 1685 and d["rect"].x1 <= 1850 and d["rect"].y0 >= 578 and d["rect"].y1 <= 730]
    contorno = next(d for d in ds if d["type"] == "f" and d["rect"].width > 100)
    sofa = np.zeros((H, W), np.uint8)
    cv2.fillPoly(sofa, [ss(np.vstack(caminhos_pdf(contorno, p2r, 24)))], 255)
    bar = np.zeros((H, W), np.uint8)
    cost = np.zeros((H, W), np.uint8)
    for d in ds:
        r_ = d["rect"]
        if d["type"] != "s" or r_.x0 < 1690 or (r_.x0 > 1780 and r_.y0 > 680):    # sem a planta e a mesa de centro
            continue
        for c in caminhos_pdf(d, p2r, 24):
            cv2.polylines(bar, [ss(c)], False, 255, 3)
            if 4 < max(r_.width, r_.height) < 9 and r_.x0 > 1700 and r_.y0 < 650:     # as divisões do encosto
                cv2.polylines(cost, [ss(c)], False, 255, 3)
    _, lab = cv2.connectedComponents(((sofa > 0) & (bar == 0)).astype(np.uint8), connectivity=4)

    def regiao(pts=(), ks=()):
        ks = list(ks)
        for x, y in pts:
            j, i = int((y - Y0) * SS), int((x - X0) * SS)
            v = lab[j - 6:j + 7, i - 6:i + 7].ravel()
            ks.append(np.bincount(v[v > 0]).argmax())
        return cv2.dilate(np.isin(lab, ks).astype(np.uint8) * 255, np.ones((5, 5), np.uint8)) & sofa

    areas = np.bincount(lab.ravel())
    encosto = regiao(q["encosto"])
    face = regiao(ks=[k for k in range(1, len(areas)) if 20000 < areas[k] < 40000])
    assento = regiao(q["assento"])
    alm = [regiao(p) for p in q["almofadas"]]
    circ = np.zeros((H, W), np.uint8)
    for c, r_ in q["redondas"]:
        cv2.circle(circ, tuple(ss(c)), int(r_ * SS), 255, -1)
    cor = q["cores"]
    for par in q["sombra"]:
        sombra(sofa, *par)
    base = assento | alm[0] | alm[1] | (circ & sofa)
    pintar(cor["assento"], 0.80 + 0.20 * lisa(np.clip(dist(sofa) / 5.0, 0, 1)), base)          # a frente arredondada
    d_ass = cv2.distanceTransform((assento == 0).astype(np.uint8), cv2.DIST_L2, 5) / SS
    pintar(cor["face"], 0.78 + 0.22 * lisa(np.clip(d_ass / 2.0, 0, 1)), face)                 # escurece no vinco
    pintar(cor["encosto"], 0.80 + 0.20 * lisa(np.clip(dist(encosto) / 1.8, 0, 1)), encosto)   # o rolo
    d_face = cv2.distanceTransform((face == 0).astype(np.uint8), cv2.DIST_L2, 5) / SS
    reg *= (1 - 0.22 * red(np.clip(1 - d_face / 1.4, 0, 1) * (assento > 0)))[..., None]       # o vinco no assento
    reg *= (1 - 0.18 * red(cost & encosto))[..., None]                                           # as costuras

    # 3. as almofadas
    for m in alm:
        m = cv2.erode(m, np.ones((3, 3), np.uint8))
        sombra(m, -0.6, 0.6, 0.8, 0.22)
        pintar(cor["almofada"], 0.86 + 0.14 * lisa(np.clip(dist(m) / 2.4, 0, 1)), m)
    for (cx, cy), r_ in q["redondas"]:
        m = np.zeros((H, W), np.uint8)
        cv2.circle(m, tuple(ss((cx, cy))), int(r_ * SS), 255, -1)
        sombra(m, -0.6, 0.6, 0.8, 0.22)
        pintar(cor["almofada"], 0.86 + 0.14 * lisa(np.clip(dist(m) / 2.6, 0, 1)), m)
        pregas = np.zeros((H, W), np.uint8)
        for k in range(8):
            ang = np.radians(22.5 + 45 * k)
            cv2.line(pregas, tuple(ss((cx, cy))), tuple(ss((cx + 0.92 * r_ * np.cos(ang), cy + 0.92 * r_ * np.sin(ang)))),
                     255, 2)
        reg *= (1 - 0.12 * red(pregas & m))[..., None]
        botao = np.zeros((H, W), np.uint8)
        cv2.circle(botao, tuple(ss((cx, cy))), int(0.55 * SS), 255, -1)
        reg *= (1 - 0.25 * red(botao))[..., None]

    # 4. os clones do render, cada um com a sombra nova
    gx, gy = np.meshgrid(np.arange(W) / SS + X0 + 0.5 / SS, np.arange(H) / SS + Y0 + 0.5 / SS)
    gx1, gy1 = np.meshgrid(np.arange(X1 - X0) + X0 + 0.5, np.arange(Y1 - Y0) + Y0 + 0.5)

    def clonar(dentro, c_src, c_dst, ang, par):
        nonlocal reg
        ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
        ux, uy = gx - c_dst[0], gy - c_dst[1]
        m = dentro(c_src[0] + ca * ux + sa * uy, c_src[1] - sa * ux + ca * uy).astype(np.uint8) * 255
        sombra(m, *par)
        ux, uy = gx1 - c_dst[0], gy1 - c_dst[1]
        cor_ = cv2.remap(org, (c_src[0] + ca * ux + sa * uy - 0.5).astype(np.float32),
                         (c_src[1] - sa * ux + ca * uy - 0.5).astype(np.float32), cv2.INTER_CUBIC)
        a = red(m)[..., None]
        reg = reg * (1 - a) + cor_ * a

    def poli(caixa):
        d = next(d for d in pg.get_drawings() if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and d["type"] == "f"
                 and d["rect"].x0 >= caixa[0] and d["rect"].x1 <= caixa[2] and d["rect"].y0 >= caixa[1]
                 and d["rect"].y1 <= caixa[3])
        return np.vstack(caminhos_pdf(d, p2r, 16))
    qp = q["poltrona"]
    pf, pdst = poli(qp["fonte"]), poli(qp["destino"])
    mpf = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mpf, [ss(pf)], 255)
    mpf = cv2.dilate(mpf, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * 0.9 * SS) + 1,) * 2))

    def na_poltrona(sx, sy):
        return mpf[np.clip(((sy - Y0) * SS).astype(int), 0, H - 1), np.clip(((sx - X0) * SS).astype(int), 0, W - 1)] > 0

    def no_circulo(c, r_):
        return lambda sx, sy: np.hypot(sx - c[0], sy - c[1]) <= r_
    clonar(na_poltrona, pf.mean(axis=0), pdst.mean(axis=0) + qp["desvio"], qp["angulo"], (-1.2, 1.2, 1.6, 0.28))
    (mc, mr), mdst = q["mesinha"]["fonte"], q["mesinha"]["destino"]
    clonar(no_circulo(mc, mr), mc, mdst, 0.0, (-0.8, 0.8, 1.0, 0.28))
    clonar(no_circulo((pcx, pcy), pr), (pcx, pcy), (pcx, pcy), 0.0, (-0.8, 0.8, 1.0, 0.25))
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    sala de estar: sofá do motor fora ({int(buraco.sum())} px de tapete de volta); sofá curvo do PDF pela "
          f"esquerda do tapete, com 2 almofadas e 2 redondas; poltrona da direita (girada {qp['angulo']}°) e mesinha")
    return out




# Térreo 8. Jardim de 4,79 m² (pedido do usuário, 19/10/26: "aqui é um jardim verde com plantas"; item 8 da
# conferência). O motor fez o jardim como piso claro, vazio. No PDF da Casa A ele tem a forração (as setinhas da
# hachura de grama) até a faixa de piso junto à porta da direita, e três touceiras. Entra o gramado do próprio Térreo
# (um trecho do gramado ao lado, do tamanho do canteiro), com a sombra curta das paredes em volta (a luz vem do alto à
# direita, como no resto da prancha), e as três touceiras, nas posições e no tamanho do PDF: clones da palmeira em
# estrela do jardim lateral do render (já sobre a grama, com a sua sombra), recortada do gramado pela cor, cada uma
# girada e espelhada para não repetir, com uma sombra curta a mais no canteiro.
JARDIM = {"canteiro": (783.0, 856.0, 890.0, 897.8),       # px da imagem: do PDF (a faixa à direita fica piso)
          "fonte_grama": (600, 885),                      # canto do trecho do gramado ao lado (px)
          "grama_ref": (600, 885, 720, 935),              # gramado limpo: a cor de referência para recortar a planta
          "parede_sombra": (0.22, 2.2),                   # força e alcance da sombra das paredes (px)
          # touceiras: centro (px), raio no PDF (px), planta-fonte (centro, raio) e giro (graus) / espelho
          "touceiras": [((805.6, 877.4), 14.5, ((1500.0, 485.0), 26.0), 15, False),
                        ((835.5, 876.7), 14.5, ((1500.0, 485.0), 26.0), 130, True),
                        ((866.7, 876.7), 14.5, ((1500.0, 485.0), 26.0), 250, False)],
          "sombra": (-1.2, 1.2, 1.2, 0.30)}


def jardim(out):
    q = JARDIM
    x0, y0, x1, y1 = q["canteiro"]
    xa, ya, xb, yb = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    reg = out[ya:yb, xa:xb].astype(np.float32)
    fx, fy = q["fonte_grama"]
    grama = out[fy:fy + yb - ya, fx:fx + xb - xa].astype(np.float32)
    a = (cobertura_colunas(x0, x1, xa, xb)[None, :] * cobertura_linhas(y0, y1, ya, yb)[:, None])[..., None]
    # sombra das paredes: mais forte junto à de cima e à da direita (a luz vem do alto à direita)
    forca, alc = q["parede_sombra"]
    ys = np.arange(ya, yb)[:, None] + 0.5
    xs = np.arange(xa, xb)[None, :] + 0.5
    som = np.maximum(np.clip(1 - (ys - y0) / alc, 0, 1), np.clip(1 - (x1 - xs) / alc, 0, 1) * 0.6)
    som = np.maximum(som, np.clip(1 - (xs - x0) / alc, 0, 1) * 0.5)
    som = np.maximum(som, np.clip(1 - (y1 - ys) / alc, 0, 1) * 0.5)
    grama *= (1 - forca * som)[..., None]
    out[ya:yb, xa:xb] = np.clip(np.round(reg * (1 - a) + grama * a), 0, 255).astype(np.uint8)
    # a planta-fonte: o que não é gramado (distância de cor ao gramado limpo, em Lab), com a borda suave
    fonte = cv2.imread(str(APROVADAS["Terreo"]))
    lab = cv2.cvtColor(fonte, cv2.COLOR_BGR2LAB).astype(np.float32)
    gx0, gy0, gx1, gy1 = q["grama_ref"]
    gref = lab[gy0:gy1, gx0:gx1].reshape(-1, 3)
    mu, sd = gref.mean(axis=0), np.maximum(gref.std(axis=0), 1)
    z = np.sqrt((((cv2.GaussianBlur(lab, (0, 0), 1.0) - mu) / sd) ** 2).sum(axis=2))
    planta = cv2.GaussianBlur((cv2.GaussianBlur((z > 2.2).astype(np.float32), (0, 0), 1.5) > 0.4).astype(np.float32),
                              (0, 0), 0.6)
    fonte = fonte.astype(np.float32)
    for (cx_, cy_), raio, ((sx, sy), sr), giro, espelho in q["touceiras"]:
        k = raio / sr
        t = np.radians(giro)
        R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]) * k
        if espelho:
            R = R @ np.diag([-1, 1])
        Ri = np.linalg.inv(R)                               # destino -> fonte: p_fonte = s + Ri (p - c)
        ja, jb = int(cx_ - raio - 4), int(cx_ + raio + 5)
        ia, ib = int(cy_ - raio - 4), int(cy_ + raio + 5)
        t0 = np.array([sx, sy]) - Ri @ np.array([cx_, cy_]) + Ri @ np.array([ja, ia])
        M = np.hstack([Ri, t0[:, None]]).astype(np.float32)
        cor = cv2.warpAffine(fonte, M, (jb - ja, ib - ia), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP)
        m = cv2.warpAffine(planta, M, (jb - ja, ib - ia), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        yy, xx = np.mgrid[ia:ib, ja:jb] + 0.5
        m *= np.clip((raio + 1.0 - np.hypot(xx - cx_, yy - cy_)) / 2.0, 0, 1)   # só a planta-fonte, sem vizinhas
        sdx, sdy, ssig, sf = q["sombra"]
        sh = cv2.warpAffine(m, np.float32([[1, 0, sdx], [0, 1, sdy]]), (jb - ja, ib - ia))
        sh = cv2.GaussianBlur(sh, (0, 0), ssig) * (1 - m)
        jan = out[ia:ib, ja:jb].astype(np.float32) * (1 - sf * sh)[..., None]
        jan = jan * (1 - m[..., None]) + cor * m[..., None]
        out[ia:ib, ja:jb] = np.clip(np.round(jan), 0, 255).astype(np.uint8)
    print(f"    jardim: gramado do Térreo em x {x0}-{x1}, y {y0}-{y1} px, com a sombra das paredes; "
          f"{len(q['touceiras'])} touceiras do PDF (a palmeira em estrela do jardim lateral)")
    return out


# Térreo, tanques (pedido do usuário, 19/10/26: "aqui são dois tanques de água com torneiras, na área de serviço"). O
# motor fez duas peças lilás com um símbolo estranho. No PDF da Casa A (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS) é a bancada
# junto à parede de cima, com dois tanques de louça lado a lado: cada um com o esfregador (a faixa de cima, com a borda
# de baixo arredondada) e a bacia funda, e a torneira de parede no meio, a bica descendo até o esfregador. Entram
# nessas medidas, no padrão das cubas aprovadas: a bancada no quartzo claro das bancadas, com a borda fina e a sombra
# curta; cada tanque de louça branca com o contorno fino, as nervuras do esfregador, a bacia escurecendo da borda ao
# fundo e a válvula; a torneira cromada, da parede.
TANQUES = {"bancada": [(1530.83, 1605.1, 1610.77, 1642.51), (1610.77, 1605.1, 1613.03, 1644.78)],
           "tanques": [{"caixa": (1532.7, 1610.37, 1568.64, 1640.64), "esfregador": (1533.66, 1611.33, 1567.68, 1622.67),
                        "bacia": (1533.66, 1618.13, 1567.68, 1639.68), "torneira": (1549.99, 1605.1, 1551.35, 1618.36)},
                       {"caixa": (1572.39, 1610.37, 1608.33, 1640.64), "esfregador": (1573.35, 1611.33, 1607.37, 1622.67),
                        "bacia": (1573.35, 1618.13, 1607.37, 1639.68), "torneira": (1589.67, 1605.1, 1591.04, 1618.36)}],
           "nervuras": 5}


def tanques(out):
    from retoque_subsolo_casae import (Tela, SOMBRA, LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO, CROMO,
                                       CROMO_CLARO, CROMO_ESCURO, QUARTZO, SS)
    q = TANQUES
    _, p2r = pdf_pavimento("Terreo")
    caixa = (q["bancada"][0][0], q["bancada"][0][1], q["bancada"][1][2], q["bancada"][1][3])
    tl = Tela(out, p2r, caixa)
    for b in q["bancada"]:
        m = tl.ret(b)
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, QUARTZO)
        tl.contorno(m, 0.35, (150, 153, 155))
    for t in q["tanques"]:
        x0, y0, x1, y1 = t["caixa"]
        c = tl.ret(t["caixa"], 3.0)
        tl.sombra(c, dx=-0.4, dy=0.4, sigma=0.5, forca=0.2)
        tl.pintar(c, LOUCA_CONTORNO)
        tl.pintar(tl.ret((x0 + 0.8, y0 + 0.8, x1 - 0.8, y1 - 0.8), 2.6), LOUCA)
        bx0, by0, bx1, by1 = t["bacia"]
        for i in range(6):                   # a bacia, da borda ao fundo
            k = i / 5
            cor = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
            ins = 0.5 + k * 3.2
            tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.8, 2.6 - k)), cor)
        ex0, ey0, ex1, ey1 = t["esfregador"]  # o esfregador: plano, um pouco acima da bacia, com as nervuras
        e = tl.ret(t["esfregador"], 2.6)
        tl.sombra(e, dx=0, dy=0.5, sigma=0.4, forca=0.25)
        tl.pintar(e, LOUCA)
        tl.contorno(e, 0.3, LOUCA_CONTORNO)
        n = q["nervuras"]
        for k in range(1, n + 1):
            xk = ex0 + 3 + (ex1 - ex0 - 6) * k / (n + 1)
            tl.pintar(tl.ret((xk - 0.3, ey0 + 2.5, xk + 0.3, ey1 - 2.0)), BACIA_BORDA, 0.8)
        vx, vy = tl.pt((bx0 + bx1) / 2, (by0 + by1) / 2 + 3)
        v = tl.vazia()
        cv2.circle(v, (int(vx), int(vy)), int(1.1 * SS), 255, -1)
        tl.pintar(v, CROMO_ESCURO)
        tx0, ty0, tx1, ty1 = t["torneira"]  # da parede de cima, descendo até o esfregador
        m = tl.ret(t["torneira"], 0.6)
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, CROMO_ESCURO)
        tl.pintar(tl.ret((tx0 + 0.25, ty0, (tx0 + tx1) / 2, ty1 - 0.4), 0.3), CROMO_CLARO)
        base = tl.vazia()
        cx, cy = tl.pt((tx0 + tx1) / 2, ty0 + 1.0)
        cv2.circle(base, (int(cx), int(cy)), int(1.0 * SS), 255, -1)
        tl.pintar(base, CROMO)
    out = tl.gravar()
    (a, b), (c, d) = p2r(*caixa[:2]), p2r(*caixa[2:])
    print(f"    área de serviço: bancada x {a:.1f}-{c:.1f}, y {b:.1f}-{d:.1f} px, com os dois tanques e as torneiras do PDF")
    return out


# Térreo, gás (pedidos do usuário, 19/10/26: "piso da área do Gás é marrom granito" e "faltando a representação da
# porta do gás e seu arco"). O motor fez o piso do gás em lilás e a porta como uma faixa cinza, sem folhas nem arcos.
# No PDF da Casa A o gás tem porta de duas folhas, que abrem para a área de serviço descoberta. Entram: o granito
# marrom da área de serviço (um trecho limpo dela, no tom dela), do fundo do gás até a face de fora da parede; e as
# duas folhas abertas, nas medidas do PDF, com os arcos finos (como as portas aprovadas, `desenhar_porta`), mais
# escuros que os do granito, para lerem sobre a pedra portuguesa.
GAS = {"piso": (899.3, 836.9, 932.4, 855.7),          # px da imagem: dentro das paredes do PDF, até a face de fora
       "fonte_granito": (940, 826),                   # canto de um trecho limpo do granito da área de serviço (px)
       "portas": [((1501.24, 1789.35, 1503.5, 1811.85), (1501.24, 1786.51, 1529.41, 1814.69)),
                  ((1555.32, 1789.35, 1557.59, 1811.85), (1529.41, 1786.51, 1557.59, 1814.69))],
       "arco_pedra": ((92, 94, 96), 0.5)}             # cor e largura do arco sobre a pedra portuguesa


def porta_pdf(out, pg, p2r, folha, arco, cor_arco, larg):
    """Folha (retângulo do PDF, em pt) e arco (bbox da curva do PDF) de uma porta, como as aprovadas
    (`retoque_subsolo_casae.desenhar_porta`), com a cor e a largura do arco dadas."""
    import retoque_subsolo_casae as RS
    RS.PORTA["arco"]["_ajuste"] = (cor_arco, larg)
    return RS.desenhar_porta(out, pg, p2r, folha, arco, "_ajuste")


def gas(out):
    q = GAS
    x0, y0, x1, y1 = q["piso"]
    xa, ya, xb, yb = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    fx, fy = q["fonte_granito"]
    gran = out[fy:fy + yb - ya, fx:fx + xb - xa].astype(np.float32)
    a = (cobertura_colunas(x0, x1, xa, xb)[None, :] * cobertura_linhas(y0, y1, ya, yb)[:, None])[..., None]
    reg = out[ya:yb, xa:xb].astype(np.float32)
    out[ya:yb, xa:xb] = np.clip(np.round(reg * (1 - a) + gran * a), 0, 255).astype(np.uint8)
    pg, p2r = pdf_pavimento("Terreo")
    for folha, arco in q["portas"]:
        out = porta_pdf(out, pg, p2r, folha, arco, *q["arco_pedra"])
    print(f"    gás: piso de granito em x {x0}-{x1}, y {y0}-{y1} px; porta de duas folhas com os arcos do PDF")
    return out


# Térreo, porta do jardim (pedido do usuário, 19/10/26: "faltando também as duas portas da área de jardim e seus
# arcos"). No PDF da Casa A o jardim de 4,79 m² abre para a área de serviço descoberta por uma porta de uma folha, no
# vão da parede da direita, que abre para fora; a folha aberta fica junto à parede de baixo (as duas folhas vizinhas
# são as do gás, já feitas). O render tinha só o vão. Entra a folha aberta e o arco, como a porta do gás.
PORTA_JARDIM = {"folha": (1502.48, 1854.26, 1542.17, 1856.53), "arco": (1499.65, 1811.17, 1545.0, 1856.53)}


def porta_jardim(out):
    pg, p2r = pdf_pavimento("Terreo")
    out = porta_pdf(out, pg, p2r, PORTA_JARDIM["folha"], PORTA_JARDIM["arco"], *GAS["arco_pedra"])
    print("    jardim: porta de uma folha para a área descoberta, com o arco do PDF")
    return out


# Térreo, portões (pedido do usuário, 19/10/26: "representar os portões, de ambos os lados, da área descoberta"). No
# PDF da Casa A (ARQ_PAREDE) cada lado da área de serviço descoberta tem um portão de correr de duas folhas
# desencontradas, com os batentes nas pontas: à esquerda, para o gramado; à direita, para o acesso de pedestres. O
# render tinha só uma faixa clara com uma borda escura. A faixa sai (em cada linha, o piso de cada lado continua em
# espelho: a grama e a pedra portuguesa) e entram as folhas nas medidas do PDF, em metal (o alumínio das portas de
# vidro do Subsolo), com a borda fina escura e a linha do meio de cada folha.
PORTOES = {
    "lados": [
        {"nome": "esquerdo", "faixa": (891, 899, 903, 1005),     # px da imagem: x0, x1, linhas y0..y1
         "folhas": [(1493.98, 1873.82, 1496.81, 1967.36), (1491.14, 1962.83, 1493.98, 2056.37)],
         "batentes": [(1491.14, 1871.55, 1499.65, 1873.82), (1491.14, 2056.37, 1499.65, 2058.64)]},
        {"nome": "direito", "faixa": (1006, 1012, 857, 1005),
         "folhas": [(1695.24, 1788.78, 1698.07, 1924.84), (1698.07, 1920.31, 1700.91, 2056.37)],
         "batentes": [(1692.41, 1786.51, 1700.91, 1788.78), (1692.41, 2056.37, 1700.91, 2058.64)]}],
    "metal": (150, 153, 156), "borda": ((70, 72, 74), 0.35), "meio": ((112, 115, 118), 0.3)}


def refazer_faixa(out, faixa):
    """Uma faixa vertical (x0..x1, linhas y0..y1) some: cada metade recebe, em espelho, o que está do seu lado."""
    x0, x1, y0, y1 = faixa
    meio = (x0 + x1) / 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            out[y, x] = out[y, x0 - 1 - (x - x0)] if x <= meio else out[y, x1 + 1 + (x1 - x)]


def portoes(out):
    from retoque_subsolo_casae import Tela
    q = PORTOES
    _, p2r = pdf_pavimento("Terreo")
    for lado in q["lados"]:
        refazer_faixa(out, lado["faixa"])
        caixa = [f(v) for f, v in zip((min, min, max, max), zip(*(lado["folhas"] + lado["batentes"])))]
        tl = Tela(out, p2r, caixa)
        for r in lado["folhas"] + lado["batentes"]:
            m = tl.ret(r)
            tl.sombra(m, dx=-0.5, dy=0.5, sigma=0.5, forca=0.25)
        for r in lado["batentes"]:
            m = tl.ret(r)
            tl.pintar(m, q["metal"])
            tl.contorno(m, q["borda"][1], q["borda"][0])
        for f in lado["folhas"]:
            m = tl.ret(f)
            tl.pintar(m, q["metal"])
            xm = (f[0] + f[2]) / 2
            tl.pintar(m & tl.ret((xm - 0.3, f[1], xm + 0.3, f[3])), q["meio"][0])
            tl.contorno(m, q["borda"][1], q["borda"][0])
        out = tl.gravar()
        print(f"    portão {lado['nome']}: faixa do motor refeita; {len(lado['folhas'])} folhas e "
              f"{len(lado['batentes'])} batentes do PDF")
    return out


# Térreo, rejuntes (pedido do usuário, 19/10/26: "Precisamos remover os rejuntes"; escopo escolhido por ele: o piso
# interno do Térreo). O travertino da varanda, das salas, do hall interno, da área gourmet e dos cômodos saiu em
# placas grandes, com a junta marcada (linhas finas verticais e horizontais) e cada placa num tom. O piso volta
# contínuo, com a textura do próprio render e na luz dele:
# - onde: o travertino da legenda (#DCD9CA na base v6, levada à imagem pelo afim do Térreo), sem a escada interna;
#   dentro dele, só o que é piso pela cor (claro e quente como o travertino). Ficam os móveis, os tapetes, as
#   paredes, os traços desenhados (os do PDF: tracejados de projeção, arcos e folhas de porta, escadas; e o que for
#   muito mais escuro que o piso em volta) e um anel de 3 px em volta de tudo isso;
# - a textura: miolos de 32 px do próprio piso sem junta vertical (os veios horizontais do travertino ficam, são a
#   textura), sem os pontinhos escuros, cada um dividido pela luz do lugar, tecidos por image quilting;
# - a luz: o tom do piso em volta, suavizado (sigma 12 px) o bastante para os degraus de tom entre placas sumirem;
#   as sombras dos móveis ficam (o que é 2 a 7% ou mais mais escuro que a luz do lugar);
# - no anel em volta dos móveis e dos traços, o piso original fica, no tom do piso refeito ao lado; o que sobrou de
#   junta vertical ali vira a média dos dois lados.
REJUNTES = {"legenda": (0xCA, 0xD9, 0xDC), "tol": 8,      # travertino na base (BGR)
            "fora": [(1185, 462, 1335, 556)],             # a escada interna (px da imagem: x0, y0, x1, y1)
            "piso": {"L": (140, 214), "quente": (22, 44), "sat": (20, 46)},
            "camadas_desenho": ("DOC_LINHAS E PROJEÇÕES", "ARQ_PAREDE", "ARQ_ESCADAS E RAMPAS", "ARQ_PERGOLADO"),
            "traco": 35,                                  # traço desenhado: mais escuro que a mediana 9 px por isto
            "anel": 7, "janela": 32, "luz": 12}


def rejuntes(out):
    import json
    from retoque_bege_bahia_terreo import quilting
    q = REJUNTES
    import rotulos_casaa as A
    cfg = json.loads(A.CONFIG.read_text())
    base = cv2.imread(str((A.CONFIG.parent / cfg["entrega"]["pasta_bases"] /
                           cfg["entrega"]["pavimentos"]["Terreo"]["base"]).resolve()))
    b2 = cv2.resize(base, (2000, round(base.shape[0] * 2000 / base.shape[1])), interpolation=cv2.INTER_NEAREST)
    trav = (np.abs(b2.astype(int) - q["legenda"]).max(axis=2) <= q["tol"]).astype(np.uint8)
    T = cv2.warpAffine(trav, np.float32(AFIM_QR["Terreo"]), (out.shape[1], out.shape[0]), flags=cv2.INTER_NEAREST)
    for x0, y0, x1, y1 in q["fora"]:
        T[y0:y1, x0:x1] = 0
    T = cv2.erode(T, np.ones((3, 3), np.uint8)).astype(bool)
    rf = out.astype(np.float32)
    L = cv2.GaussianBlur(rf.mean(axis=2), (0, 0), 0.5)
    sat, quente = rf.max(axis=2) - rf.min(axis=2), rf[..., 2] - rf[..., 0]
    pp = q["piso"]
    piso = T & (rf.mean(axis=2) >= pp["L"][0]) & (rf.mean(axis=2) <= pp["L"][1]) & (quente >= pp["quente"][0]) & \
        (quente <= pp["quente"][1]) & (sat >= pp["sat"][0]) & (sat <= pp["sat"][1])
    # os traços desenhados ficam: os do PDF (tracejados de projeção, arcos e folhas de porta, escadas, pergolado),
    # rasterizados e levados à imagem, com 2 px de folga; e o que for muito mais escuro que o piso em volta (as
    # juntas do motor chegam a -25; os traços, a -40 ou mais)
    import pymupdf
    pg, p2r = pdf_pavimento("Terreo")
    doc = pg.parent
    for u in doc.layer_ui_configs():
        doc.set_layer_ui_config(u["number"], action=0 if u["text"] in q["camadas_desenho"] else 2)
    Z = 4
    pix = doc[pg.number].get_pixmap(matrix=pymupdf.Matrix(Z, Z), alpha=False)
    des = (np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).min(axis=2) < 200).astype(np.uint8)
    src = np.float32([[100, 100], [1500, 100], [100, 1500]])
    M = np.vstack([cv2.getAffineTransform(src, np.float32([p2r(*pt) for pt in src])), [0, 0, 1]]) @ np.diag([1 / Z, 1 / Z, 1])
    des = cv2.warpAffine(des * 255, M[:2], (out.shape[1], out.shape[0]), flags=cv2.INTER_AREA) > 20
    forte = (L - cv2.medianBlur(out, 9).astype(np.float32).mean(axis=2)) < -q["traco"]
    piso &= ~cv2.dilate((des | forte).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    piso = cv2.morphologyEx(piso.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (q["anel"], q["anel"]))
    nucleo = piso & ~cv2.dilate((T & ~piso).astype(np.uint8), k).astype(bool)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    med5 = cv2.medianBlur(out, 5).astype(np.float32)
    campo = nconv(med5, nucleo.astype(np.float32), q["luz"])
    d = np.clip(1 - nconv(med5, piso.astype(np.float32), 1.5).mean(axis=2) / np.maximum(campo.mean(axis=2), 1), 0, 1)
    t = np.clip((d - 0.02) / 0.05, 0, 1)
    fator = 1 - d * t * t * (3 - 2 * t)                    # as sombras dos móveis

    dv = L - 0.5 * (np.roll(L, 2, axis=1) + np.roll(L, -2, axis=1))
    J = q["janela"]
    ys, xs = np.nonzero(nucleo)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    cob = cv2.blur(nucleo.astype(np.float32), (J, J), anchor=(0, 0), borderType=cv2.BORDER_CONSTANT)
    usados, fontes = [], []
    for yy in range(y0, y1 - J, 6):
        for xx in range(x0, x1 - J, 6):
            if cob[yy, xx] >= 0.98 and (dv[yy:yy + J, xx:xx + J] < -1.2).mean(axis=0).max() < 0.5 and \
                    all(abs(yy - a) >= 24 or abs(xx - b) >= 24 for a, b in usados):
                usados.append((yy, xx))
    for yy, xx in usados:
        g = rf[yy:yy + J, xx:xx + J].copy()
        md = med5[yy:yy + J, xx:xx + J]
        pinta = (md.mean(axis=2) - g.mean(axis=2)) > 7
        g[pinta] = md[pinta]
        g = g / campo[yy:yy + J, xx:xx + J]
        g = g / g.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(g), np.ascontiguousarray(g[:, ::-1])]
    tex = quilting(fontes, y1 - y0, x1 - x0, p=30, sobra=9, candidatos=500, rng=np.random.default_rng(642))
    novo = rf.copy()
    novo[y0:y1, x0:x1] = tex * campo[y0:y1, x0:x1] * fator[y0:y1, x0:x1, None]
    a = (cv2.GaussianBlur(nucleo.astype(np.float32), (0, 0), 0.7) * nucleo)[..., None]
    res = rf * (1 - a) + novo * a
    # no anel em volta dos móveis e dos traços, o piso original fica, mas no tom novo: a razão entre o piso refeito e
    # o original ali perto (as placas tinham tons diferentes; sem isso a borda do anel marca um degrau)
    wn = nucleo.astype(np.float32)
    den = cv2.GaussianBlur(wn, (0, 0), 4)
    razao = cv2.GaussianBlur(res * wn[..., None], (0, 0), 4) / np.maximum(cv2.GaussianBlur(rf * wn[..., None], (0, 0), 4), 1)
    razao = np.where(den[..., None] > 0.05, razao, 1.0)
    anel = (piso & ~nucleo).astype(np.float32)[..., None] * (1 - a)
    res = res * (1 - anel) + res * razao * anel
    # o que sobrou de junta vertical no anel em volta dos móveis: a média dos dois lados (2 px)
    Lo = res.mean(axis=2)
    c = ((Lo - 0.5 * (np.roll(Lo, 2, axis=1) + np.roll(Lo, -2, axis=1)) < -1.2) & piso).astype(np.float32)
    fv = cv2.filter2D(c, -1, np.ones((20, 1), np.float32) / 20) >= 0.7
    fv = cv2.dilate(fv.astype(np.uint8), np.ones((10, 1), np.uint8)).astype(bool) & (c > 0) & T
    fv = cv2.dilate(fv.astype(np.uint8), np.ones((1, 2), np.uint8)).astype(bool) & piso
    yv, xv = np.nonzero(fv)
    res[yv, xv] = 0.5 * (res[yv, np.clip(xv - 2, 0, None)] + res[yv, np.clip(xv + 2, None, out.shape[1] - 1)])
    out[:] = np.clip(np.round(res), 0, 255).astype(np.uint8)
    print(f"    rejuntes: travertino {int(T.sum())} px, piso {int(piso.sum())} px, refeito {int(nucleo.sum())} px "
          f"({len(usados)} miolos de {J} px); resto de junta vertical no anel: {len(yv)} px")
    return out


# A ordem da lista é a de execução: o piso do depósito sem juntas (7) e o Bege Bahia (11) vêm antes da escada (3),
# para a sombra do último espelho cair no Bege Bahia, e antes dos itens que apagam traços em espelho (4 e 6), para
# o piso de cada lado já ser o Bege Bahia.
ITENS = {"Subsolo": [("1", "banho de serviço: o chuveiro e o vidro do box", chuveiro_servico),
                     ("2", "sauna: o banco horizontal de volta", banco_sauna),
                     ("7", "depósito e circulação interna: piso contínuo, sem juntas", juntas),
                     ("11", "Bege Bahia na área de circulação, no depósito e na circulação interna", bege_bahia),
                     ("3", "escada: depois da linha de corte, os degraus na cor e textura do Subsolo", escada),
                     ("4", "portas de vidro da academia: folhas de vidro claras, não pretas", portas_academia),
                     ("5", "janelas: vão, peitoril, vidro e caixilhos do PDF, no lugar da peça cinza", janelas),
                     ("6", "circulação: sem o traço preto na borda", traco_circulacao),
                     ("8", "banhos feminino e masculino: as cubas grandes do PDF", cubas_banhos),
                     ("9", "boxes de vidro: ducha ao lado da sauna e banho feminino", boxes),
                     ("10", "divisória entre os banhos: peça clara do PDF, não parede", divisoria),
                     ("12", "banho de serviço: bancada e cuba nas medidas do PDF", bancada_servico),
                     ("13", "gramado depois do último degrau da escada do deck", gramado_escada)],
         "Terreo": [("1", "pilares da varanda e do gourmet em preto, como as paredes", pilares),
                    ("2", "sala de estar: o sofá curvo do PDF, a poltrona da direita e a mesinha", sala_estar),
                    ("rejuntes", "piso interno sem os rejuntes: o travertino contínuo", rejuntes),
                    ("8", "jardim de 4,79 m²: verde, com as três touceiras do PDF", jardim),
                    ("tanques", "área de serviço: a bancada com os dois tanques e as torneiras", tanques),
                    ("gas", "gás: piso de granito e a porta de duas folhas com os arcos", gas),
                    ("porta_jardim", "jardim: a porta para a área descoberta, com o arco", porta_jardim),
                    ("portoes", "área descoberta: os portões de correr dos dois lados", portoes)]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(ITENS))
    ap.add_argument("--saida", type=Path, default=CASA / "renders")
    args = ap.parse_args()
    orig = cv2.imread(str(APROVADAS[args.pavimento]))
    out = orig.copy()
    for n, desc, f in ITENS[args.pavimento]:
        print(f"[{args.pavimento} {n}] {desc}")
        out = f(out)
    nome = args.saida / f"{APROVADAS[args.pavimento].stem}_ajustes.png"
    cv2.imwrite(str(nome), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(nome.with_name(nome.stem + "_camada.png")), np.dstack([out, alfa]))
    print(f"[fim] {nome}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

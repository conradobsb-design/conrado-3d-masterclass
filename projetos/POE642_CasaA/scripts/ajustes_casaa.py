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
  Térreo 9. Escada caracol (pedido do usuário, 19/10/26): os degraus 1 a 7, até o corte, cheios, em madeira, com o
     corrimão; o resto esmaecido.
  Térreo, portas no granito (pedidos do usuário, 19/10/26): as quatro portas de giro sobre o granito com a folha do
     PDF e o arco em cinza fino, como de regra.
  Térreo, eletrodomésticos (pedido do usuário, 19/10/26): os quadrados do PDF da cozinha, do gourmet e da área de
     serviço com o inox aprovado da Casa D.
  Térreo, bancada gourmet (pedido do usuário, 19/10/26): a área molhada e a divisória do PDF em traço fino, a cuba em
     inox e a torneira gourmet, no lugar das duas caixas do motor.
  Térreo, bancada da cozinha (pedido do usuário, 19/10/26): em quartzo com o desenho de pedra, com a área molhada, as
     duas cubas em inox e as torneiras do PDF.
  Térreo 3. Estar sob a projeção (pedido do usuário, 19/10/26): no lugar da mesa de jantar do motor, as 4 poltronas em
     X e a mesa triangular do PDF, com o X tracejado por cima.
  Térreo 5. Lavabo (pedido do usuário, 19/10/26): bancada de quartzo com a cuba esculpida e a torneira, o vaso
     suspenso e o tracejado da claraboia, nas medidas do PDF.
  Térreo, porta pivotante (pedido do usuário, 19/10/26): a folha até a ponta do PDF, no hall externo, e o arco
     pequeno do lado de lá.
  Térreo, escada interna (pedido do usuário, 19/10/26): os degraus 1 a 7 cheios até a linha de corte, com o
     sombreamento de subida, sem linhas; do 8º em diante esmaecida; o jardim em volta no gramado aprovado.
  Térreo 11 e 12. Motorista (pedido do usuário, 19/10/26): a cama de solteiro, a bancada com a cuba de apoio e a
     torneira, as folhas de vidro do box e o chuveiro, no lugar dos blocos lilás do motor.
  Térreo, carros (pedido do usuário, 19/10/26): cada carro numa cor (branco perolado, grafite, azul-marinho, a
     paleta da Casa D) e os três levemente desalinhados, como na Casa E.
  Térreo, sem arcos (decisão do usuário, 19/10/26, com as plantas de referência dos elementos: "remover os arcos,
     escadas com linhas"): os arcos de todas as portas saem (os do motor e os desenhados nos itens acima); as folhas
     ficam. Na porta camarão da varanda, sai também o cinza que o motor pôs entre cada folha e o arco.

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
SS_E = 8                                   # supersampling dos desenhos do estar sob a projeção


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


# Térreo 9. Escada caracol da área de serviço (pedido do usuário, 19/10/26: "vamos melhorar a representação dessa
# escada caracol. somente uma parte será representada, sendo a outra esmaecida. note onde o arco está em destaque, a
# qual é a área que fica bem destacada, ao contrário da área tracejada"; item 9 da conferência). O motor fez só um
# círculo com doze raios escuros sobre o granito. No PDF da Casa A (ARQ_ESCADAS E RAMPAS e ARQ_ELEMENTOS FIXOS) a
# escada sobe da direita (o "S"), no sentido anti-horário: os degraus 1 a 7, até a linha de corte, são cheios, com o
# corrimão de madeira cheio por fora; o resto (8 em diante, acima do corte) é tracejado. Entra assim:
# - o círculo do motor sai: o granito em volta, tecido de trechos limpos dele (image quilting), na luz do lugar;
# - degraus 1 a 7 (de 0° a 131,4°, os raios do PDF): pisos de madeira clara (a da mesa do render, com o veio no
#   sentido do raio), do pilar central à borda, com o sombreamento de subida das escadas aprovadas (cada degrau um
#   pouco mais claro que o de baixo e a sombra curta de cada espelho no degrau de baixo), sem linhas; o corrimão de
#   madeira por fora, cheio; a sombra curta da escada no granito;
# - degraus 8 em diante: os mesmos pisos, esmaecidos (misturados ao granito), com os espelhos em traço claro;
# - o pilar central, em metal.
CARACOL = {"centro": (1756.4, 1718.5), "r_corrimao": (50.5, 53.4), "r_piso": 50.5, "r_pilar": 4.0,   # pt do PDF
           "angulos": [0.0, 18.0, 36.4, 55.2, 74.2, 93.3, 112.5, 131.4],      # os raios cheios do PDF (graus)
           "fontes_granito": [(960, 786, 1010, 846)],    # trecho limpo do granito, à esquerda da escada (px)
           "madeira": (1053, 337, 1073, 360),                                 # trecho limpo da mesa (px)
           "tom": (0.86, 1.0), "espelho": (0.35, 2.2),     # degrau 1 a 7; sombra do espelho: força e alcance (px)
           "esmaecer": 0.22, "espelho_esm": ((170, 170, 170), 0.25),
           "corrimao": ((52, 92, 138), (30, 50, 70)), "pilar": (88, 90, 92),
           "sombra": (-1.0, 1.0, 1.2, 0.35)}


def caracol(out):
    from retoque_bege_bahia_terreo import quilting
    q = CARACOL
    _, p2r = pdf_pavimento("Terreo")
    cx, cy = p2r(*q["centro"])
    k = p2r(q["centro"][0] + 100, q["centro"][1])[0] - cx
    k /= 100                                               # px por pt
    Rc0, Rc1 = q["r_corrimao"][0] * k, q["r_corrimao"][1] * k
    Rp, rn = q["r_piso"] * k, q["r_pilar"] * k
    SS = 8
    x0, y0 = int(cx - Rc1 - 6), int(cy - Rc1 - 6)
    x1, y1 = int(cx + Rc1 + 7), int(cy + Rc1 + 7)
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    # 1. o granito: tecido de trechos limpos, na luz do lugar (a média do anel em volta do disco)
    fontes = []
    for a, b, c, d in q["fontes_granito"]:
        g = out[b:d, a:c].astype(np.float32)
        g = g / g.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    tex = quilting(fontes, h, w, p=16, sobra=5, candidatos=500, rng=np.random.default_rng(6420))
    yy, xx = np.mgrid[y0:y1, x0:x1] + 0.5
    rr = np.hypot(xx - cx, yy - cy)
    th = np.degrees(np.arctan2(cy - yy, xx - cx)) % 360
    lum = reg.mean(axis=2)
    anel = (rr > Rc1 + 1.5) & (rr < Rc1 + 6) & (lum > 35) & (lum < 120)   # só o granito (sem a parede e a porta)
    luz = np.median(reg[anel], axis=0)
    disco = np.clip(Rc1 + 1.5 - rr, 0, 1)[..., None]
    reg = reg * (1 - disco) + tex * luz * disco
    granito = reg.copy()

    # coberturas em SS x
    def em_ss(f):
        ys, xs = np.mgrid[y0 * SS:y1 * SS, x0 * SS:x1 * SS]
        return f((xs + 0.5) / SS, (ys + 0.5) / SS)
    R_ss = em_ss(lambda X, Y: np.hypot(X - cx, Y - cy))
    T_ss = em_ss(lambda X, Y: np.degrees(np.arctan2(cy - Y, X - cx)) % 360)

    def red(m):
        return cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    ang = q["angulos"]
    passo = (ang[-1] - ang[0]) / (len(ang) - 1)
    bordas = ang + [ang[-1] + passo * i for i in range(1, 40) if ang[-1] + passo * i < 360] + [360.0]
    a0, b0, a1, b1 = q["madeira"]
    mad = cv2.imread(str(APROVADAS["Terreo"]))[b0:b1, a0:a1].astype(np.float32)
    # piso de cada degrau: a madeira no sistema (raio, ângulo), veio no sentido do raio
    u = np.clip((rr - rn) / (Rp - rn), 0, 1) * (mad.shape[0] - 1)
    piso = np.zeros_like(reg)
    for i in range(len(bordas) - 1):
        t0, t1 = bordas[i], bordas[i + 1]
        dentro = (th >= t0) & (th < t1)
        v = ((th - t0) / (t1 - t0) * (mad.shape[1] - 1) + 7 * i) % (mad.shape[1] - 1)
        cor = cv2.remap(mad, v.astype(np.float32), u.astype(np.float32), cv2.INTER_LINEAR)
        piso[dentro] = cor[dentro]
    na_escada = red((R_ss > rn) & (R_ss <= Rp))
    nvis = len(ang) - 1
    vis_ss = (T_ss >= ang[0]) & (T_ss < ang[-1])
    vis = red(vis_ss & (R_ss <= Rc1)) 
    # 2. a parte esmaecida (acima do corte): o piso misturado ao granito, os espelhos em traço claro
    e = q["esmaecer"]
    a_esm = (na_escada * (1 - red(vis_ss)))[..., None] * e
    reg = reg * (1 - a_esm) + piso * a_esm
    cor_e, larg_e = q["espelho_esm"]
    for t in bordas[nvis:-1]:
        lin = (np.abs(((T_ss - t + 180) % 360) - 180) * np.pi / 180 * R_ss < larg_e / 2) & (R_ss > rn) & (R_ss <= Rp)
        al = red(lin)[..., None] * 0.45
        reg = reg * (1 - al) + np.float32(cor_e) * al
    # 3. a parte cheia: a sombra curta da escada no granito, os pisos com o sombreamento de subida, o corrimão
    sdx, sdy, ssig, sf = q["sombra"]
    m = red(vis_ss & (R_ss <= Rc1))
    sh = cv2.GaussianBlur(cv2.warpAffine(m, np.float32([[1, 0, sdx], [0, 1, sdy]]), (w, h)), (0, 0), ssig) * (1 - m)
    reg *= (1 - sf * sh)[..., None]
    tmin, tmax = q["tom"]
    forca, alc = q["espelho"]
    fator = np.ones((h * SS, w * SS), np.float32)
    for i in range(nvis):
        t0, t1 = ang[i], ang[i + 1]
        dentro = (T_ss >= t0) & (T_ss < t1)
        tom = tmin + (tmax - tmin) * i / (nvis - 1)
        dist = (t1 - T_ss) * np.pi / 180 * R_ss          # distância (px) ao espelho do degrau de cima
        f = tom * (1 - forca * np.clip(1 - dist / alc, 0, 1)) if i < nvis - 1 else np.full_like(dist, tom)
        fator = np.where(dentro, f, fator)
    a_vis = (red(vis_ss & (R_ss > rn) & (R_ss <= Rp)))[..., None]
    reg = reg * (1 - a_vis) + piso * red(np.where(vis_ss, fator, 1))[..., None] * a_vis
    corr = vis_ss & (R_ss > Rc0) & (R_ss <= Rc1)
    reg = reg * (1 - red(corr)[..., None]) + np.float32(q["corrimao"][0]) * red(corr)[..., None]
    borda = vis_ss & (np.abs(R_ss - Rc1) < 0.25)
    reg = reg * (1 - red(borda)[..., None]) + np.float32(q["corrimao"][1]) * red(borda)[..., None]
    # 4. o pilar central, em metal, com um brilho
    pil = R_ss <= rn
    reg = reg * (1 - red(pil)[..., None]) + np.float32(q["pilar"]) * red(pil)[..., None]
    bri = np.hypot(em_ss(lambda X, Y: X - cx + rn * 0.3), em_ss(lambda X, Y: Y - cy + rn * 0.3)) <= rn * 0.35
    reg = reg * (1 - 0.5 * red(bri)[..., None]) + 200 * 0.5 * red(bri)[..., None]
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    caracol: centro ({cx:.1f}, {cy:.1f}) px, raio {Rc1:.1f} px; degraus 1 a {nvis} cheios "
          f"({ang[0]}° a {ang[-1]}°), {len(bordas) - 1 - nvis} esmaecidos")
    return out


# Térreo, portas no granito (pedidos do usuário, 19/10/26: "melhorar a representação dos arcos e portas. lembrando que
# os arcos das portas no marrom granito são em cinza, com traço fino" e, no banho do motorista, "o arco da porta de
# entrada [...] está imperceptível, devendo ser em cinza, como de regra"). As quatro portas de giro sobre o granito (a
# da cozinha para a área de serviço, a da despensa, a do banho e a do quarto do motorista): o motor fez as folhas
# grossas e um pouco fora do lugar, e os arcos não se viam. A folha do motor sai (os px claros na faixa dela viram o
# granito logo ao lado, do lado de fora da faixa) e entram a folha e o arco do PDF, como as portas aprovadas, o arco
# no cinza fino da regra (160, 161, 160; 0,45 px), o das Casas C, D e E.
PORTAS_GRANITO = {"portas": [  # (nome, folha, arco), em pt do PDF
    ("cozinha para a área de serviço", (1766.11, 1613.6, 1817.13, 1615.87), (1766.11, 1613.6, 1817.13, 1664.62)),
    ("despensa", (1832.72, 1678.8, 1834.99, 1718.48), (1832.72, 1678.8, 1872.41, 1718.48)),
    ("banho do motorista", (2103.43, 1455.43, 2143.11, 1457.69), (2103.43, 1418.01, 2143.11, 1457.69)),
    ("quarto do motorista", (2274.08, 1415.17, 2276.34, 1466.2), (2225.32, 1415.17, 2276.34, 1466.2))],
    "arco": ((160, 161, 160), 0.45), "claro": 30, "faixa": 3}


def portas_granito(out):
    q = PORTAS_GRANITO
    pg, p2r = pdf_pavimento("Terreo")
    for nome, folha, arco in q["portas"]:
        (a, b), (c, d) = p2r(*folha[:2]), p2r(*folha[2:])
        horiz = (c - a) > (d - b)
        f = q["faixa"]
        x0, y0 = int(np.floor(a)) - (1 if horiz else f), int(np.floor(b)) - (f if horiz else 1)
        x1, y1 = int(np.ceil(c)) + (1 if horiz else f), int(np.ceil(d)) + (f if horiz else 1)
        reg = out[y0:y1, x0:x1].astype(np.float32)
        lum = reg.mean(axis=2)
        gran = np.median(lum[lum < np.percentile(lum, 50)])
        claro = lum > gran + q["claro"]
        claro = cv2.dilate(claro.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        ys, xs = np.nonzero(claro)
        n = 0
        for y, x in zip(ys + y0, xs + x0):
            cands = [(y, x + f + 2), (y, x - f - 2)] if not horiz else [(y + f + 2, x), (y - f - 2, x)]
            melhor = min(cands, key=lambda t: abs(out[t].astype(np.float32).mean() - gran))
            out[y, x] = out[melhor]
            n += 1
        out = porta_pdf(out, pg, p2r, folha, arco, *q["arco"])
        print(f"    porta {nome}: folha do motor fora ({n} px); folha e arco do PDF, arco em cinza fino")
    return out


# Térreo, eletrodomésticos (pedido do usuário, 19/10/26: "eletrodomésticos em inox", na fileira de baixo da cozinha
# e do gourmet). O motor fez os volumes no lilás dos armários. No PDF (ARQ_LAYOUT HUMANIZAÇÃO), os quadrados sem
# diagonal são eletrodomésticos: dois no fim da bancada do gourmet, dois na cozinha e as duas máquinas da área de
# serviço. Cada um recebe o inox aprovado da Casa D, levado ao quadrado do PDF, com a sombra curta e o contorno fino,
# como na cozinha e nas máquinas da Casa E: na cozinha e no gourmet, as metades do par da cozinha da Casa D; na área
# de serviço, as máquinas de lá. O volume do motor passa até 2 px do quadrado do PDF (para fora): o inox cobre os
# dois, para não sobrar uma moldura lilás.
INOX = {"quadrados": [  # (onde, quadrado em pt, qual fonte)
    ("gourmet", (1559.67, 1548.4, 1605.02, 1593.76), 0), ("gourmet", (1607.37, 1548.4, 1652.72, 1593.76), 1),
    ("cozinha", (1672.56, 1548.4, 1717.92, 1593.76), 0), ("cozinha", (1717.92, 1548.4, 1763.27, 1593.76), 1),
    ("área de serviço", (1615.87, 1607.93, 1655.55, 1647.61), 2), ("área de serviço", (1661.22, 1607.93, 1700.91, 1647.61), 3)],
    "fonte": (CASA.parent / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png",
              [(972, 319, 996, 345), (998, 319, 1022, 345),        # o par da cozinha
               (1143, 191, 1166, 216), (1167, 191, 1190, 216)]),   # as máquinas da área de serviço
    "contorno": (70, 72, 74), "larg_contorno": 0.4,
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.3},
    "claro": 150.0, "alcance": 2.5}           # o volume do motor: px claros (lilás) junto ao quadrado, até 2,5 px


def bloco_render(Y, r, claro, alcance):
    """Bordas (subpixel) do volume claro do render em volta do retângulo r do PDF (px): em cada lado, da borda do
    PDF para fora, enquanto o px é claro (passando por cima de um px mais escuro entre dois claros: o brilho da quina
    do volume), até o alcance; o px de transição entra pela fração. Nunca menor que o PDF."""
    x0, y0, x1, y1 = r
    ph = Y[int(y0 + (y1 - y0) * 0.3):int(y1 - (y1 - y0) * 0.3), :].mean(axis=0)
    pv = Y[:, int(x0 + (x1 - x0) * 0.3):int(x1 - (x1 - x0) * 0.3)].mean(axis=1)

    def lado(p, borda, passo):
        i = int(np.floor(borda + 0.5)) - (1 if passo > 0 else 0)
        def cabe(k):
            return abs(i + k * passo + 0.5 - borda) <= alcance

        while cabe(1) and (p[i + passo] >= claro or (cabe(2) and p[i + 2 * passo] >= claro)):
            i += passo
        if not cabe(1):
            return borda
        v, fora, luz = p[i + passo], p[i + 2 * passo], p[i]
        c = float(np.clip((v - fora) / (luz - fora), 0, 1)) if luz > fora < v else 0.0
        return min(i - c, borda) if passo < 0 else max(i + 1 + c, borda)

    return lado(ph, x0, -1), lado(pv, y0, -1), lado(ph, x1, 1), lado(pv, y1, 1)


def inox(out):
    from retoque_terreo_casae import colar, sombra_curta, linha_aa
    q = INOX
    _, p2r = pdf_pavimento("Terreo")
    arq, fontes = q["fonte"]
    casad = cv2.imread(str(arq))
    forma = out.shape[:2]
    feitos = {}
    Y = out.astype(np.float32).mean(axis=2)
    for onde, quad, f in q["quadrados"]:
        (x0, y0), (x1, y1) = p2r(*quad[:2]), p2r(*quad[2:])
        x0, y0, x1, y1 = bloco_render(Y, (x0, y0, x1, y1), q["claro"], q["alcance"])
        out = sombra_curta(out, (x0, y0, x1, y1), q["sombra"])
        fx0, fy0, fx1, fy1 = fontes[f]
        out = colar(out, casad[fy0:fy1, fx0:fx1], (x0, y0, x1, y1))
        a = linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(q["contorno"]) * a, 0, 255).astype(np.uint8)
        feitos[onde] = feitos.get(onde, 0) + 1
    print("    eletrodomésticos em inox: " + ", ".join(f"{n} no {k}" if k != "área de serviço" else f"{n} na {k}"
                                                     for k, n in feitos.items()))
    return out


# Térreo, bancada gourmet (pedido do usuário, 19/10/26: "melhore a representação da área molhada e divisoria da
# bancada"). O motor fez, no braço de baixo da bancada, duas caixas: uma com um "texto" ilegível e outra com a cuba.
# No PDF (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS): a área molhada é o retângulo em volta da cuba, a 2,3 pt da borda da
# bancada e da ponta, até a parede; a divisória é a linha que corta a área molhada de lado a lado, interrompida pela
# cuba; a cuba é retangular, de aba fina; a torneira gourmet tem a base e a alavanca junto à parede e a mola até a
# bica, sobre a cuba. As duas caixas saem (a bancada logo à esquerda, coluna a coluna, na mesma luz) e entram: a área
# molhada e a divisória em traço cinza fino (o da área molhada das Casas C e D), com a área 3% mais escura que a
# bancada para se ler como uma zona; a cuba em inox (aba, bacia da borda ao fundo, contorno) e a torneira cromada,
# com a sombra curta.
GOURMET = {
    "limpar": (866, 923, 729, 750), "desloc": 60, "esfumar": 3,   # px: x0, x1, y0, y1; de onde vem a bancada
    "area_molhada": (1443.52, 1559.17, 1554.07, 1596.59),         # pt; o lado de baixo é a parede
    "divisoria": 1576.75,
    "cuba": (1492.85, 1564.28, 1534.8, 1589.22), "bacia": (1493.98, 1565.41, 1533.66, 1588.09),
    "bica": ((1513.75, 1580.3), 3.1), "mola": (1514.52, 1579.35, 1516.23, 1591.69),
    "base": ((1515.35, 1591.9), 1.4), "alavanca": (1510.9, 1590.6, 1513.75, 1593.1),
    "traco": ((140, 142, 144), 0.4, 0.7),                         # cor, largura (px), força
    "tom_area": 0.97,                                              # a área molhada, um pouco mais escura que a bancada
    "aba": (222, 221, 218), "contorno": (120, 124, 128), "bacia_cor": ((166, 165, 162), (202, 201, 198))}


def gourmet(out):
    from retoque_subsolo_casae import Tela, SOMBRA, CROMO, CROMO_CLARO, CROMO_ESCURO, SS
    q = GOURMET
    x0, x1, y0, y1 = q["limpar"]
    d, e = q["desloc"], q["esfumar"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    fonte = out[y0:y1, x0 - d:x1 - d].astype(np.float32)
    w = x1 - x0
    a = np.clip(np.minimum(np.arange(w) + 1, w - np.arange(w)) / e, 0, 1)[None, :, None]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + fonte * a, 0, 255).astype(np.uint8)

    _, p2r = pdf_pavimento("Terreo")
    ax0, ay0, ax1, ay1 = q["area_molhada"]
    tl = Tela(out, p2r, (ax0 - 3, ay0 - 3, ax1 + 3, ay1))
    cor, larg, forca = q["traco"]

    def linha(p0, p1):
        m = tl.vazia()
        a_, b_ = tl.pt(*p0), tl.pt(*p1)
        cv2.line(m, (int(round(a_[0])), int(round(a_[1]))), (int(round(b_[0])), int(round(b_[1]))), 255,
                 max(1, int(round(larg * SS))))
        return m

    area = tl.ret(q["area_molhada"])
    tl.reg *= (1 - (1 - q["tom_area"]) * tl.reduzir(area))[..., None]
    cx0, cy0, cx1, cy1 = q["cuba"]
    for p0, p1 in [((ax0, ay1), (ax0, ay0)), ((ax0, ay0), (ax1, ay0)), ((ax1, ay0), (ax1, ay1)),
                   ((ax0, q["divisoria"]), (cx0, q["divisoria"])), ((cx1, q["divisoria"]), (ax1, q["divisoria"]))]:
        tl.pintar(linha(p0, p1), cor, forca)

    c = tl.ret(q["cuba"], 1.0)
    tl.sombra(c, **SOMBRA)
    tl.pintar(c, q["aba"])
    bx0, by0, bx1, by1 = q["bacia"]
    borda, fundo = q["bacia_cor"]
    for i in range(6):                       # a bacia, da borda ao fundo
        k = i / 5
        tom = tuple(borda[j] * (1 - k) + fundo[j] * k for j in range(3))
        ins = k * 3.6
        tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.6, 1.4 - k)), tom)
    tl.contorno(c, 0.3, q["contorno"])

    mx0, my0, mx1, my1 = q["mola"]           # a mola, da base à bica
    m = tl.ret(q["mola"], 0.8)
    tl.sombra(m, **SOMBRA)
    tl.pintar(m, CROMO_ESCURO)
    tl.pintar(tl.ret((mx0 + 0.2, my0, (mx0 + mx1) / 2, my1), 0.3), CROMO_CLARO, 0.7)
    for (px_, py_), r, tom in [(q["base"][0], q["base"][1], CROMO), (q["bica"][0], q["bica"][1], CROMO)]:
        disco = tl.vazia()
        u, v = tl.pt(px_, py_)
        cv2.circle(disco, (int(round(u)), int(round(v))), int(round(r * 0.5483 * SS)), 255, -1)
        tl.sombra(disco, **SOMBRA)
        tl.pintar(disco, tom)
        tl.contorno(disco, 0.25, CROMO_ESCURO)
    (u, v), r = tl.pt(*q["bica"][0]), q["bica"][1]
    face = tl.vazia()                        # a face da bica, com o arejador
    cv2.circle(face, (int(round(u)), int(round(v))), int(round(r * 0.6 * 0.5483 * SS)), 255, -1)
    tl.pintar(face, CROMO_ESCURO)
    lv = tl.ret(q["alavanca"], 0.5)
    tl.sombra(lv, **SOMBRA)
    tl.pintar(lv, CROMO)
    tl.contorno(lv, 0.25, CROMO_ESCURO)
    out = tl.gravar()
    print("    bancada gourmet: caixas do motor fora; área molhada e divisória em traço fino, cuba em inox e torneira")
    return out


# Térreo, bancada da cozinha (pedido do usuário, 19/10/26: "melhore as representações das pias e bancada, com a área
# molhada bem representada. além disso, preciso de aspecto de bancada de pedra na cozinha"). O motor fez a bancada da
# parede da direita no lilás dos armários, chapada, com duas cubas borradas. No prompt, todas as bancadas são de
# quartzo claro, com pontilhado fino. No PDF (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS): a bancada vai da parede de cima à de
# baixo; a área molhada é o retângulo em volta das duas cubas, até a parede; as cubas são retangulares, de aba fina; em
# cada uma, a válvula e a torneira de bica reta, com a base e a alavanca junto à parede.
# Entram: a bancada em pedra, o quartzo do próprio render (o da ilha e da bancada gourmet) com o desenho do Bege Bahia
# aprovado (manchas em nuvem e pontinhos) só na luz, para se ler como pedra clara; a área molhada como na
# bancada gourmet (traço cinza fino e 3% mais escura); as cubas em inox e as torneiras cromadas, com a sombra curta.
COZINHA_PIAS = {
    "bancada": (1888.0, 1395.33, 1922.01, 1670.29),               # pt, da parede de cima à de baixo
    "quartzo": (216, 219, 233), "contraste": 1.8, "semente": 645,  # BGR do quartzo da ilha no render
    "area_molhada": (1890.26, 1477.54, 1922.01, 1615.3),           # o lado da direita é a parede
    "cubas": [((1891.96, 1484.91, 1916.91, 1521.19), (1893.1, 1486.04, 1915.78, 1520.06)),
              ((1891.96, 1530.26, 1916.91, 1566.54), (1893.1, 1531.39, 1915.78, 1565.41))],
    "valvula": 3.1, "valvulas": [(1908.0, 1502.9), (1908.0, 1548.26)],
    "bicas": [(1908.59, 1501.43, 1919.74, 1502.61), (1908.59, 1546.79, 1919.74, 1547.96)],
    "bases": [(1917.63, 1500.49, 1920.69, 1503.55), (1917.63, 1545.85, 1920.69, 1548.91)],
    "alavancas": [(1918.3, 1504.1, 1920.0, 1505.6), (1918.3, 1549.4, 1920.0, 1551.0)]}


def cozinha_pias(out):
    from retoque_subsolo_casae import Tela, SOMBRA, CROMO, CROMO_CLARO, CROMO_ESCURO, SS
    q, g = COZINHA_PIAS, GOURMET
    _, p2r = pdf_pavimento("Terreo")
    tl = Tela(out, p2r, q["bancada"])
    b = tl.ret(q["bancada"])
    tl.sombra(b, **SOMBRA)
    tex = textura_bege(tl.h, tl.w, q["semente"])
    lum = tex.mean(axis=2)
    rel = 1 + q["contraste"] * (lum / lum.mean() - 1)
    pedra = np.float32(q["quartzo"])[None, None] * rel[..., None]
    a = tl.reduzir(b)[..., None]
    tl.reg = tl.reg * (1 - a) + pedra * a
    tl.contorno(b, 0.35, (150, 153, 155))

    ax0, ay0, ax1, ay1 = q["area_molhada"]
    area = tl.ret(q["area_molhada"])
    tl.reg *= (1 - (1 - g["tom_area"]) * tl.reduzir(area))[..., None]
    cor, larg, forca = g["traco"]
    for p0, p1 in [((ax1, ay0), (ax0, ay0)), ((ax0, ay0), (ax0, ay1)), ((ax0, ay1), (ax1, ay1))]:
        m = tl.vazia()
        u0, u1 = tl.pt(*p0), tl.pt(*p1)
        cv2.line(m, (int(round(u0[0])), int(round(u0[1]))), (int(round(u1[0])), int(round(u1[1]))), 255,
                 max(1, int(round(larg * SS))))
        tl.pintar(m, cor, forca)

    borda, fundo = g["bacia_cor"]
    for aba, bacia in q["cubas"]:
        c = tl.ret(aba, 1.4)
        tl.sombra(c, **SOMBRA)
        tl.pintar(c, g["aba"])
        bx0, by0, bx1, by1 = bacia
        for i in range(6):                   # a bacia, da borda ao fundo
            k = i / 5
            tom = tuple(borda[j] * (1 - k) + fundo[j] * k for j in range(3))
            ins = k * 3.6
            tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.6, 1.2 - k)), tom)
        tl.contorno(c, 0.3, g["contorno"])
    for vx, vy in q["valvulas"]:
        u, v = tl.pt(vx, vy)
        for r, tom in [(q["valvula"], CROMO), (q["valvula"] * 0.65, CROMO_ESCURO)]:
            m = tl.vazia()
            cv2.circle(m, (int(round(u)), int(round(v))), int(round(r * 0.5483 * SS)), 255, -1)
            tl.pintar(m, tom)
    for bica, base, alav in zip(q["bicas"], q["bases"], q["alavancas"]):
        m = tl.ret(bica, 0.6)
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, CROMO_ESCURO)
        tx0, ty0, tx1, ty1 = bica
        tl.pintar(tl.ret((tx0 + 0.3, ty0 + 0.2, tx1 - 0.3, (ty0 + ty1) / 2), 0.3), CROMO_CLARO)
        for peca, tom in [(base, CROMO), (alav, CROMO_ESCURO)]:
            m = tl.ret(peca, 0.4)
            tl.sombra(m, **SOMBRA)
            tl.pintar(m, tom)
            tl.contorno(m, 0.25, CROMO_ESCURO)
    out = tl.gravar()
    print("    bancada da cozinha: quartzo com o desenho de pedra, área molhada, duas cubas em inox e torneiras")
    return out


# Térreo 3. Estar sob a projeção do pavimento superior (pedido do usuário, 19/10/26: "melhorar a representação dessa
# área. não é mesa de jantar. área de estar."). O motor pôs uma mesa retangular com 6 cadeiras. No PDF (ARQ_LAYOUT
# HUMANIZAÇÃO e ARQ_MOBILIÁRIO) são 4 poltronas em X, voltadas para uma mesa triangular de cantos arredondados no
# centro, sob o X tracejado da projeção (DOC_LINHAS E PROJEÇÕES). Sem IA:
# 1. a mesa e as cadeiras do motor saem, com as sombras: o travertino volta, tecido (image quilting) de um trecho
#    limpo dele ao lado, na luz do lugar (a do piso em volta);
# 2. as poltronas são as do PDF (poltronas de encosto curvo, que abraça o assento até os braços), no estilo do sofá
#    aprovado da sala: o contorno do PDF cheio, dividido pelas linhas dele em assento e encosto com os braços (cada
#    parte com o volume arredondado e o vinco nas linhas), nas cores do sofá, com a sombra na mesma luz (as poltronas
#    do render têm outro desenho);
# 3. a mesa triangular, no contorno do PDF, no carvalho da mesa do motor (o veio no comprido), com o contorno fino e
#    a sombra curta;
# 4. o X tracejado volta por cima, como o render o desenha: os traços do PDF, no passo e na fase dos traços do render
#    em volta, na cor e na largura deles.
ESTAR_PROJ = {
    "apagar": (1026, 332, 1107, 443),                         # px: a mesa e as cadeiras do motor, com as sombras
    "janela": (996, 312, 1132, 458),                          # px: o quadrado da projeção
    "fonte_piso": (1137, 330, 1177, 450),                     # px: travertino limpo, à direita do quadrado
    "poltronas": [(1703.75, 859.16, 1773.19, 928.52), (1816.11, 858.86, 1885.46, 928.31),
                  (1814.96, 947.8, 1884.4, 1017.15), (1704.62, 947.57, 1773.97, 1017.02)],   # pt (contornos do PDF)
    "mesa": (1777.07, 914.87, 1819.33, 955.39),               # pt
    "fonte_madeira": (1053, 338, 1083, 361),                  # px da imagem aprovada: o tampo da mesa do motor
    "sombra_poltrona": [(-1.4, 1.4, 2.0, 0.30), (0, 0, 0.9, 0.14)], "sombra_mesa": (-1.0, 1.0, 1.2, 0.28),
    "vinco": 0.18,                                            # as linhas do PDF, no tecido
    "contorno_mesa": ((70, 96, 128), 0.35),
    "traco": {"cor": (112, 116, 120), "larg": 1.25, "forca": 0.62}}


def estar_projecao(out):
    from retoque_bege_bahia_terreo import quilting
    q = ESTAR_PROJ
    pg, p2r = pdf_pavimento("Terreo")
    orig = cv2.imread(str(APROVADAS["Terreo"]))
    X0, Y0, X1, Y1 = q["janela"]
    H, W = (Y1 - Y0) * SS_E, (X1 - X0) * SS_E
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    h, w = reg.shape[:2]

    def ss(pts):
        return np.int32(np.round((np.asarray(pts) - (X0, Y0)) * SS_E))

    def red(m):
        return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

    def poli(caixa, camada):
        d = next(d for d in pg.get_drawings() if d.get("layer") == camada and d["type"] == "f"
                 and d["rect"].x0 >= caixa[0] - 0.5 and d["rect"].x1 <= caixa[2] + 0.5
                 and d["rect"].y0 >= caixa[1] - 0.5 and d["rect"].y1 <= caixa[3] + 0.5)
        return np.vstack(caminhos_pdf(d, p2r, 16))

    # os traços do X, do PDF (cada traço é uma linha da DOC_LINHAS E PROJEÇÕES)
    tracos = []
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") == "DOC_LINHAS E PROJEÇÕES" and r.width > 5 and r.height > 5 and \
                abs(r.width - r.height) < 0.2 and r.width < 11:
            (a, b), (c, e) = p2r(r.x0, r.y0), p2r(r.x1, r.y1)
            if X0 <= a and c <= X1 and Y0 <= b and e <= Y1:
                it = d["items"][0]
                tracos.append((np.float64(p2r(it[1].x, it[1].y)), np.float64(p2r(it[2].x, it[2].y))))
    Yo = out.astype(np.float32).mean(axis=2)
    ax0, ay0, ax1, ay1 = q["apagar"]

    # 4 (medida antes de apagar): a fase dos traços do render em cada diagonal, fora da área apagada
    def perfil_escuro(pts):
        return np.float32([float(cv2.getRectSubPix(Yo, (1, 1), (float(x), float(y)))[0, 0]) for x, y in pts])

    fases = {}
    for sentido in (1, -1):
        seg = [t for t in tracos if np.sign((t[1][0] - t[0][0]) * (t[1][1] - t[0][1])) == sentido]
        u = seg[0][1] - seg[0][0]
        u = u / np.hypot(*u)
        if u[1] < 0:
            u = -u
        melhor = (-1e9, 0.0)
        for desl in np.arange(-5.5, 5.51, 0.25):
            sc = 0.0
            for a, b in seg:
                a2, b2 = a + desl * u, b + desl * u
                fora = lambda p: not (ax0 - 2 <= p[0] <= ax1 + 2 and ay0 - 2 <= p[1] <= ay1 + 2)
                if not (fora(a2) and fora(b2)):
                    continue
                dentro = [a2 + (b2 - a2) * k for k in np.linspace(0.15, 0.85, 7)]
                vao = [b2 + u * k for k in (0.9, 1.5, 2.1)]
                sc += perfil_escuro(vao).mean() - perfil_escuro(dentro).mean()
            melhor = max(melhor, (sc, desl))
        fases[sentido] = (melhor[1], u)
        print(f"    traços da diagonal {'\\' if sentido > 0 else '/'}: fase do render {melhor[1]:+.2f} px ao longo dela")

    # 1. a mesa e as cadeiras do motor saem: o travertino tecido, na luz do lugar
    med = cv2.medianBlur(out, 7).astype(np.float32)
    apaga = np.zeros(out.shape[:2], bool)
    apaga[ay0:ay1, ax0:ax1] = True
    riscos = np.zeros(out.shape[:2], np.uint8)
    for a, b in tracos:
        cv2.line(riscos, tuple(np.int32(np.round(a))), tuple(np.int32(np.round(b))), 255, 3)
    riscos = cv2.dilate(riscos, np.ones((7, 7), np.uint8)) > 0
    piso = np.zeros_like(apaga)
    piso[Y0:Y1, X0:X1] = True
    piso &= ~cv2.dilate(apaga.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~riscos & (Yo > 185)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    peso = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 10)
    campo = np.where((peso > 0.05)[..., None], nconv(med, piso.astype(np.float32), 10),
                     nconv(med, piso.astype(np.float32), 30))   # no meio da área apagada, a luz de mais longe
    fx0, fy0, fx1, fy1 = q["fonte_piso"]
    campo_f = nconv(med, np.ones(out.shape[:2], np.float32), 10)[fy0:fy1, fx0:fx1]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32) / campo_f
    f = f / f.reshape(-1, 3).mean(axis=0)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    tex = quilting(fontes, ay1 - ay0, ax1 - ax0, p=24, sobra=8, candidatos=400, rng=np.random.default_rng(646))
    novo = out.astype(np.float32)
    novo[ay0:ay1, ax0:ax1] = tex[:ay1 - ay0, :ax1 - ax0] * campo[ay0:ay1, ax0:ax1]
    a = np.zeros(out.shape[:2], np.float32)
    a[ay0:ay1, ax0:ax1] = 1
    a = cv2.GaussianBlur(a, (0, 0), 1.2) * apaga + apaga * 0
    a = np.maximum(a, cv2.erode(apaga.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32))
    novo = out.astype(np.float32) * (1 - a[..., None]) + novo * a[..., None]
    reg = novo[Y0:Y1, X0:X1].copy()

    gx, gy = np.meshgrid(np.arange(W) / SS_E + X0 + 0.5 / SS_E, np.arange(H) / SS_E + Y0 + 0.5 / SS_E)
    gx1, gy1 = np.meshgrid(np.arange(w) + X0 + 0.5, np.arange(h) + Y0 + 0.5)

    def sombra(m, dx, dy, sig, forca):
        nonlocal reg
        sm = cv2.warpAffine(m.astype(np.float32) / 255, np.float32([[1, 0, dx * SS_E], [0, 1, dy * SS_E]]), (W, H))
        sm = cv2.resize(cv2.GaussianBlur(sm, (0, 0), sig * SS_E), (w, h), interpolation=cv2.INTER_AREA)
        reg *= (1 - forca * sm * (1 - red(m)))[..., None]

    # 2. as poltronas do PDF, no estilo do sofá aprovado
    cores = SALA["cores"]

    def lisa(t):
        return t * t * (3 - 2 * t)

    def pintar(cor, tom, m):
        nonlocal reg
        c = cv2.resize(np.float32(cor)[None, None] * tom[..., None] * (m[..., None] / 255.0), (w, h),
                       interpolation=cv2.INTER_AREA)
        a = red(m)
        reg = reg * (1 - a[..., None]) + c

    for k, caixa in enumerate(q["poltronas"]):
        ds = [d for d in pg.get_drawings() if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO"
              and d["rect"].x0 >= caixa[0] - 0.5 and d["rect"].x1 <= caixa[2] + 0.5
              and d["rect"].y0 >= caixa[1] - 0.5 and d["rect"].y1 <= caixa[3] + 0.5]
        corpo = np.zeros((H, W), np.uint8)
        for d in ds:
            if d["type"] == "f":
                for c in caminhos_pdf(d, p2r, 16):
                    cv2.fillPoly(corpo, [ss(c)], 255)
        linhas = np.zeros((H, W), np.uint8)
        for d in ds:
            if d["type"] == "s":
                for c in caminhos_pdf(d, p2r, 16):
                    cv2.polylines(linhas, [ss(c)], False, 255, 2)
        linhas &= corpo
        for par in q["sombra_poltrona"]:
            sombra(corpo, *par)
        n, lab, st, _ = cv2.connectedComponentsWithStats(((corpo > 0) & (linhas == 0)).astype(np.uint8), connectivity=4)
        assento = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        partes = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 4 * SS_E * SS_E]
        perto = cv2.dilate(np.isin(lab, partes).astype(np.uint8), np.ones((5, 5), np.uint8))
        resto = (corpo > 0) & ~np.isin(lab, partes) & (perto == 0)     # sobras finas: vão com o encosto
        for i in partes:
            m = ((lab == i) | (cv2.dilate((lab == i).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & (linhas > 0))
            m = (m & (corpo > 0)).astype(np.uint8) * 255
            dist = cv2.distanceTransform(m, cv2.DIST_L2, 5) / SS_E
            if i == assento:
                pintar(cores["assento"], 0.80 + 0.20 * lisa(np.clip(dist / 3.0, 0, 1)), m)
            else:
                pintar(cores["encosto"], 0.80 + 0.20 * lisa(np.clip(dist / 1.8, 0, 1)), m)
        if resto.any():
            m = resto.astype(np.uint8) * 255
            pintar(cores["encosto"], np.full((H, W), 0.85, np.float32), m)
        reg *= (1 - q["vinco"] * red(linhas))[..., None]
        print(f"    poltrona {k + 1}: contorno do PDF, {len(partes)} partes (assento {st[assento, cv2.CC_STAT_AREA] / SS_E ** 2:.0f} px)")

    # 3. a mesa triangular em carvalho
    pm = poli(q["mesa"], "ARQ_MOBILIÁRIO")
    mm = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mm, [ss(pm)], 255)
    sombra(mm, *q["sombra_mesa"])
    a0, b0, a1, b1 = q["fonte_madeira"]
    mx0, my0 = pm.min(axis=0)
    mx1, my1 = pm.max(axis=0)
    M = cv2.getAffineTransform(np.float32([(0, 0), (a1 - a0, 0), (0, b1 - b0)]),
                               np.float32([(mx0 - X0 - 1, my0 - Y0 - 1), (mx1 - X0 + 1, my0 - Y0 - 1), (mx0 - X0 - 1, my1 - Y0 + 1)]))
    madeira = cv2.warpAffine(orig[b0:b1, a0:a1].astype(np.float32), M, (w, h), flags=cv2.INTER_AREA,
                             borderMode=cv2.BORDER_REFLECT)
    al = red(mm)[..., None]
    reg = reg * (1 - al) + madeira * al
    cor, larg = q["contorno_mesa"]
    borda = mm & ~cv2.erode(mm, np.ones((max(1, int(round(larg * SS_E))),) * 2, np.uint8))
    al = red(borda)[..., None]
    reg = reg * (1 - al) + np.float32(cor) * al

    # 4. o X tracejado por cima, na fase do render
    t = q["traco"]
    risco = np.zeros((H, W), np.uint8)
    for a, b in tracos:
        sentido = np.sign((b[0] - a[0]) * (b[1] - a[1]))
        desl, u = fases[sentido]
        a2, b2 = a + desl * u, b + desl * u
        meio = (a2 + b2) / 2
        if not (ax0 - 6 <= meio[0] <= ax1 + 6 and ay0 - 6 <= meio[1] <= ay1 + 6):
            continue
        cv2.line(risco, tuple(ss(a2)), tuple(ss(b2)), 255, max(1, int(round(t["larg"] * SS_E))))
    al = red(risco)[..., None] * t["forca"]
    # só dentro da área refeita (fora dela, os traços do render ficam)
    dentro = cv2.GaussianBlur(apaga[Y0:Y1, X0:X1].astype(np.float32), (0, 0), 0.8)[..., None]
    reg = reg * (1 - al * dentro) + np.float32(t["cor"]) * al * dentro
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    estar sob a projeção: mesa e 6 cadeiras do motor fora; 4 poltronas em X e a mesa triangular do PDF")
    return out


# Térreo 5. Lavabo (pedido do usuário, 19/10/26: "melhorar cuba e sua posição e tamanho. representar a bancada da
# cuba. representar o sanitário. representar e gerar o rótulo da claraboia"). O motor pôs no alto uma peça estranha
# com um arco e um bloco claro (onde ficam a projeção da claraboia e o vaso) e, à direita, uma cuba branca solta,
# menor que a bancada e longe da parede. No PDF (ARQ_BANCADAS, ARQ_LOUÇAS E METAIS e DOC_LINHAS E PROJEÇÕES): a
# bancada vai da parede da direita até 1,6 m de fundo, com a cuba esculpida (a bacia, com a fenda do ralo junto à
# parede, e um friso atrás) e a torneira saindo da parede; o vaso suspenso na parede da direita, no alto; a projeção
# da claraboia é o retângulo tracejado com o X, no alto do lavabo, com a nota "PROJ. CLARABOIA" logo abaixo. Entram:
# 1. o piso do lavabo de volta onde estavam as peças do motor (travertino tecido do próprio lavabo, na luz dele);
# 2. a bancada em quartzo (como a da cozinha), com a cuba esculpida no próprio quartzo, como a do lavabo aprovado da
#    Casa E: o fundo escurece para a fenda, junto à parede; as bordas de cima e da direita fazem sombra curta para
#    dentro; traço fino na borda; e a torneira cromada saindo da parede;
# 3. o vaso suspenso no contorno do PDF, como os aprovados (louça com volume e o tampo fechado);
# 4. o tracejado da claraboia, como o do estar sob a projeção; o rótulo vem em `rotulos_casaa.py`.
LAVABO_A = {
    "limpar": [(1189, 179, 1236, 198), (1210, 201, 1236, 240)],     # px: as peças do motor, com as sombras
    "fonte_piso": (1191, 199, 1209, 236),                           # px: piso limpo do lavabo, à esquerda
    "sala": (2021.22, 561.94, 2106.26, 715.01),                     # pt: o lavabo, por dentro das paredes
    "bancada": (2077.92, 615.8, 2106.26, 670.23), "cuba": (2079.05, 616.94, 2099.46, 669.09),
    "fenda": 2100.03,                                               # pt: x da fenda do ralo (o friso do PDF)
    "torneira": (2096.65, 644.89, 2104.59, 646.81), "canopla": (2104.59, 643.9, 2106.26, 647.8),
    "vaso": (2077.15, 577.45, 2106.26, 597.46),
    "inclinacao": 0.12, "sombra_borda": (0.16, 1.4), "luz_borda": 0.04,
    "cor_fenda": (92, 94, 98), "contorno_cuba": ((150, 150, 150), 0.4, 0.6)}


def lavabo_a(out):
    from retoque_bege_bahia_terreo import quilting
    from retoque_subsolo_casae import Tela, SOMBRA, CROMO, CROMO_CLARO, CROMO_ESCURO, vaso, SS
    from retoque_terreo_casae import poligono_aa, linha_aa
    q, qc = LAVABO_A, COZINHA_PIAS
    pg, p2r = pdf_pavimento("Terreo")
    (sx0, sy0), (sx1, sy1) = p2r(*q["sala"][:2]), p2r(*q["sala"][2:])

    # 1. o piso de volta
    apaga = np.zeros(out.shape[:2], bool)
    for x0, y0, x1, y1 in q["limpar"]:
        apaga[y0:y1, x0:x1] = True
    sala = np.zeros_like(apaga)
    sala[int(np.ceil(sy0)) + 1:int(sy1) - 1, int(np.ceil(sx0)) + 1:int(sx1) - 1] = True
    Yo = out.astype(np.float32).mean(axis=2)
    piso = sala & ~cv2.dilate(apaga.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & \
        (Yo > cv2.medianBlur(out, 9).astype(np.float32).mean(axis=2) - 12)
    med = cv2.medianBlur(out, 5).astype(np.float32)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    peso = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 6)
    campo = np.where((peso > 0.05)[..., None], nconv(med, piso.astype(np.float32), 6),
                     nconv(med, piso.astype(np.float32), 15))
    fx0, fy0, fx1, fy1 = q["fonte_piso"]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32) / nconv(med, piso.astype(np.float32), 6)[fy0:fy1, fx0:fx1]
    f = f / f.reshape(-1, 3).mean(axis=0)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    ys, xs = np.nonzero(apaga)
    by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    tex = quilting(fontes, by1 - by0, bx1 - bx0, p=14, sobra=5, candidatos=300, rng=np.random.default_rng(647))
    novo = out.astype(np.float32)
    novo[by0:by1, bx0:bx1] = tex[:by1 - by0, :bx1 - bx0] * campo[by0:by1, bx0:bx1]
    a = (cv2.GaussianBlur(apaga.astype(np.float32), (0, 0), 0.8) * apaga)[..., None]
    out[:] = np.clip(out * (1 - a) + novo * a, 0, 255).astype(np.uint8)

    # 2. a bancada em quartzo, a cuba esculpida e a torneira
    tl = Tela(out, p2r, q["bancada"])
    b = tl.ret(q["bancada"])
    tl.sombra(b, **SOMBRA)
    tex = textura_bege(tl.h, tl.w, 648)
    lum = tex.mean(axis=2)
    pedra = np.float32(qc["quartzo"])[None, None] * (1 + qc["contraste"] * (lum / lum.mean() - 1))[..., None]
    a = tl.reduzir(b)[..., None]
    tl.reg = tl.reg * (1 - a) + pedra * a
    tl.contorno(b, 0.35, (150, 153, 155))
    out = tl.gravar()
    forma = out.shape[:2]
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
    (x0, y0), (x1, y1) = p2r(*q["cuba"][:2]), p2r(*q["cuba"][2:])
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    fa = 1 - q["inclinacao"] * np.clip((xx - x0) / (x1 - x0), 0, 1)       # o fundo desce para a parede
    s_, w_ = q["sombra_borda"]
    fa *= 1 - s_ * np.exp(-np.clip(yy - y0, 0, None) / w_) - s_ * np.exp(-np.clip(x1 - xx, 0, None) / w_)
    fa *= 1 + q["luz_borda"] * (np.exp(-np.clip(xx - x0, 0, None) / w_) + np.exp(-np.clip(y1 - yy, 0, None) / w_))
    fa = 1 + (fa - 1) * al
    out[:] = np.clip(out * fa[..., None], 0, 255).astype(np.uint8)
    xf = p2r(q["fenda"], q["cuba"][1])[0]
    a = linha_aa(forma, [(xf, y0 + 1.5), (xf, y1 - 1.5)], 0.8)[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(q["cor_fenda"]) * a, 0, 255).astype(np.uint8)
    cor, larg, forca = q["contorno_cuba"]
    a = linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], larg, fechada=True)[..., None] * forca
    out[:] = np.clip(out * (1 - a) + np.float32(cor) * a, 0, 255).astype(np.uint8)
    (tx0, ty0), (tx1, ty1) = p2r(*q["torneira"][:2]), p2r(*q["torneira"][2:])
    yc, lt = (ty0 + ty1) / 2, ty1 - ty0
    bica = [(tx1, yc), (tx0, yc)]
    sb = cv2.GaussianBlur(linha_aa(forma, [(u - 1.0, v + 1.0) for u, v in bica], lt), (0, 0), 0.8)
    out[:] = np.clip(out * (1 - 0.3 * sb)[..., None], 0, 255).astype(np.uint8)
    for pts, lg, c in ((bica, lt, CROMO_ESCURO), ([(tx1 - 0.3, yc - 0.15), (tx0, yc - 0.15)], 0.35, CROMO_CLARO)):
        a = linha_aa(forma, pts, lg)[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(c) * a, 0, 255).astype(np.uint8)
    (cx0, cy0), (cx1, cy1) = p2r(*q["canopla"][:2]), p2r(*q["canopla"][2:])
    a = poligono_aa(forma, [(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)])[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(CROMO) * a, 0, 255).astype(np.uint8)

    # 3. o vaso suspenso
    out = vaso(out, pg, p2r, q["vaso"], "direita")

    # 4. o tracejado da claraboia (por cima do vaso, como no PDF)
    t = ESTAR_PROJ["traco"]
    ax0, ay0, ax1, ay1 = q["sala"]
    risco = np.zeros(forma, np.float32)
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") == "DOC_LINHAS E PROJEÇÕES" and r.x0 >= ax0 - 0.1 and r.x1 <= ax1 + 0.1 and \
                r.y0 >= ay0 - 0.1 and r.y1 <= ay1 + 0.1 and max(r.width, r.height) > 3:
            it = d["items"][0]
            risco = np.maximum(risco, linha_aa(forma, [p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)], t["larg"]))
    risco *= sala
    a = (risco * t["forca"])[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(t["cor"]) * a, 0, 255).astype(np.uint8)
    print("    lavabo: peças do motor fora; bancada de quartzo com cuba esculpida e torneira; vaso suspenso; "
          "tracejado da claraboia")
    return out


# Térreo, porta pivotante (pedido do usuário, 19/10/26: "melhorar a representação da porta pivotante, mostrando-a até
# o hall externo com seus respectivos arcos"). O motor parou a folha no batente entre os dois halls e só fez o arco
# grande, no hall interno. No PDF (ARQ_PAREDE) a folha passa do pivô e entra 0,65 m no hall externo, e esse trecho
# tem o arco pequeno, do lado de lá. A folha e o arco grande do render ficam (estão no lugar do PDF); entram, no
# mesmo desenho deles: o resto da folha até a ponta do PDF (as três linhas da folha do render: contorno, miolo claro,
# contorno, com o contorno na ponta) e o arco pequeno, do fim da folha ao batente de cima, centrado no pivô, no
# cinza e na largura do arco grande.
PIVOTANTE = {"pivo": (2201.22, 877.44), "ponta": (2238.08, 877.44), "topo": (2201.22, 840.59),   # pt
             "folha_render": (1240, 1280, 351, 354),     # px: x0, x1, linhas da folha do render (contorno, miolo, contorno)
             "inicio": 1288.5,                            # px: onde a folha do render para (no batente)
             "arco": ((118, 121, 124), 1.0, 0.75)}        # cor, largura (px) e força: o arco grande do render


def pivotante(out):
    from retoque_terreo_casae import linha_aa
    q = PIVOTANTE
    _, p2r = pdf_pavimento("Terreo")
    (px, py), (ex, _), (_, ty) = p2r(*q["pivo"]), p2r(*q["ponta"]), p2r(*q["topo"])
    x0, x1, y0, y1 = q["folha_render"]
    linhas = np.median(out[y0:y1, x0:x1].astype(np.float32), axis=1)        # BGR de cada linha da folha
    forma = out.shape[:2]
    # o resto da folha: as três linhas, com a cobertura de subpixel na ponta, e o contorno da ponta
    xi = q["inicio"]
    for k, y in enumerate(range(y0, y1)):
        a = linha_aa(forma, [(xi, y + 0.5), (ex, y + 0.5)], 1.0)
        a[y, :] = np.clip(a[y, :], 0, 1)
        a[:y, :] = 0
        a[y + 1:, :] = 0
        out[:] = np.clip(out * (1 - a[..., None]) + linhas[k] * a[..., None], 0, 255).astype(np.uint8)
    a = linha_aa(forma, [(ex - 0.5, y0), (ex - 0.5, y1)], 1.0)[..., None]
    out[:] = np.clip(out * (1 - a) + linhas[0] * a, 0, 255).astype(np.uint8)
    # o arco pequeno, do fim da folha ao batente de cima
    r = ex - px
    cor, larg, forca = q["arco"]
    pts = [(px + r * np.cos(t), py - r * np.sin(t)) for t in np.linspace(0, np.pi / 2 * (py - ty) / r, 60)]
    a = linha_aa(forma, pts, larg)[..., None] * forca
    out[:] = np.clip(out * (1 - a) + np.float32(cor) * a, 0, 255).astype(np.uint8)
    print(f"    porta pivotante: folha até a ponta do PDF (x {xi:.1f} a {ex:.1f} px) e o arco pequeno no hall externo "
          f"(raio {r:.1f} px)")
    return out


# Térreo, escada interna e o jardim em volta (pedido do usuário, 19/10/26: "vamos melhorar a representação da escada.
# não há uma barreira de subida. precisamos representar a parte colorida até o 7 degrau, onde tem a linha em diagonal.
# sendo esmaecida a partir desse degrau, pois já está na região do 1º pavimento. e a área verde ao redor precisa ter
# um aspecto melhor"). O motor fez a escada em U inteira cheia, com as linhas dos degraus e um retângulo de traço
# por cima (a "barreira"), e o jardim num verde chapado. No PDF (ARQ_ESCADAS E RAMPAS) a escada sobe do degrau 1, à
# esquerda do lanço de cima, para a direita; a linha de corte (o traço em diagonal com o X) passa no 7º degrau; do 8º
# em diante (o resto do lanço de cima, o patamar e o lanço de baixo) é tracejado, acima do corte. O jardim (17,46 m²)
# inclui a área da escada: ela sobe de dentro dele. Sem IA, como a escada caracol:
# 1. o jardim inteiro (com a área da escada) vira o gramado aprovado (o da grama ao lado do jardim de 4,79 m², tecido
#    por image quilting, no tom dele), com a sombra curta das paredes;
# 2. os degraus 1 a 7, até a linha de corte, cheios: o travertino do piso interno (tecido de um trecho limpo), com o
#    sombreamento de subida das escadas aprovadas, sem linhas: cada degrau um pouco mais claro que o de baixo (de 0,86
#    a 1) e a sombra curta de cada espelho no degrau de baixo; e a sombra curta da escada no gramado;
# 3. do 8º degrau em diante, os mesmos pisos esmaecidos sobre o gramado (30%), com os espelhos e o contorno em traço
#    claro;
# 4. a linha de corte do PDF (o traço com o X), fina.
ESCADA_INT = {
    "caixa": (1180, 455, 1335, 575),                          # px: o jardim com a escada (até o vidro da direita)
    "lanco1": (2021.22, 1094.86, 2174.3, 1162.89), "lanco2": (2021.22, 1185.57, 2174.3, 1253.6),
    "patamar": (2174.3, 1094.86, 2242.33, 1253.6),            # pt
    "espelhos": [2038.23, 2055.24, 2072.25, 2089.26, 2106.26, 2123.27, 2140.28, 2157.29],   # pt: entre os degraus
    "cheios": 7,                                              # degraus cheios: até o corte, no 7º
    "corte_caixa": (2118, 1090, 2162, 1166),                  # pt: onde ficam os traços da linha de corte
    "fonte_grama": (600, 885, 720, 935),                      # px da imagem aprovada: o gramado limpo
    "fonte_piso": (1137, 330, 1177, 450),                     # px: travertino limpo
    "piso": (186, 198, 217),                                  # BGR: o travertino dos degraus do render
    "tom": (0.86, 1.0), "espelho": (0.35, 2.2), "esmaecer": 0.30, "espelho_esm": ((170, 170, 170), 0.35),
    "parede": (0.22, 2.5), "sombra": (-1.0, 1.0, 1.2, 0.35), "corte": ((90, 92, 94), 0.5)}


def escada_interna(out):
    from retoque_bege_bahia_terreo import quilting
    from retoque_terreo_casae import poligono_aa, linha_aa
    q = ESCADA_INT
    pg, p2r = pdf_pavimento("Terreo")
    X0, Y0, X1, Y1 = q["caixa"]
    forma = out.shape[:2]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    h, w = reg.shape[:2]

    def ret_px(r):
        (a, b), (c, d) = p2r(*r[:2]), p2r(*r[2:])
        return a - X0, b - Y0, c - X0, d - Y0

    def poli(pts):
        return poligono_aa(forma, [(x, y) for x, y in pts])[Y0:Y1, X0:X1]

    def ret_aa(r):
        a, b, c, d = ret_px(r)
        return poli([(a + X0, b + Y0), (c + X0, b + Y0), (c + X0, d + Y0), (a + X0, d + Y0)])

    escada = np.maximum.reduce([ret_aa(q[k]) for k in ("lanco1", "lanco2", "patamar")])
    verde = (reg[..., 1] - reg[..., 2] > 6) & (reg[..., 1] - reg[..., 0] > 6)
    jardim = cv2.morphologyEx((verde | (escada > 0.01)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    jardim = jardim.astype(bool) & (reg.mean(axis=2) > 25)     # as paredes ficam

    # 1. o gramado aprovado
    ap = cv2.imread(str(APROVADAS["Terreo"])).astype(np.float32)
    fx0, fy0, fx1, fy1 = q["fonte_grama"]
    g = ap[fy0:fy1, fx0:fx1]
    cor_grama = np.median(g.reshape(-1, 3), axis=0)
    g = g / g.reshape(-1, 3).mean(axis=0)
    fontes = [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    tex = quilting(fontes, h, w, p=30, sobra=10, candidatos=400, rng=np.random.default_rng(649))[:h, :w]
    grama = tex * cor_grama
    parede = (~jardim) & (reg.mean(axis=2) < 70)
    dist = cv2.distanceTransform((~parede).astype(np.uint8), cv2.DIST_L2, 5)
    forca, alc = q["parede"]
    grama *= (1 - forca * np.clip(1 - dist / alc, 0, 1))[..., None]
    aj = cv2.GaussianBlur(jardim.astype(np.float32), (0, 0), 0.6) * jardim
    reg = reg * (1 - aj[..., None]) + grama * aj[..., None]

    # o travertino dos degraus
    fx0, fy0, fx1, fy1 = q["fonte_piso"]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32)
    f = f / cv2.GaussianBlur(f, (0, 0), 8)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    piso = quilting(fontes, h, w, p=24, sobra=8, candidatos=300, rng=np.random.default_rng(650))[:h, :w] * np.float32(q["piso"])

    # a parte cheia: do degrau 1 até a linha de corte
    corte = []
    for d in pg.get_drawings():
        r = d["rect"]
        cx0, cy0, cx1, cy1 = q["corte_caixa"]
        if d.get("layer") == "ARQ_ESCADAS E RAMPAS" and d["type"] == "s" and r.x0 >= cx0 and r.x1 <= cx1 and \
                r.y0 >= cy0 and r.y1 <= cy1 and r.width > 1 and r.height > 1:
            it = d["items"][0]
            corte.append([p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)])
    longos = sorted([c for c in corte if np.hypot(c[1][0] - c[0][0], c[1][1] - c[0][1]) > 8],
                    key=lambda c: min(c[0][1], c[1][1]))
    a1, c1 = longos[0], longos[-1]                            # o primeiro e o último trecho da diagonal
    a1 = sorted(a1, key=lambda p: p[1])
    c1 = sorted(c1, key=lambda p: p[1])
    l0, t0, _, b0 = ret_px(q["lanco1"])
    cheio = poli([(l0 + X0, t0 + Y0), (a1[0][0], t0 + Y0), a1[1], c1[0], (c1[1][0], b0 + Y0), (l0 + X0, b0 + Y0)])
    cheio = np.minimum(cheio, escada)
    esm = np.clip(escada - cheio, 0, 1)

    # 2. os degraus cheios, com o sombreamento de subida e a sombra curta no gramado
    xs = np.arange(w)[None, :] + 0.5
    bordas = [p2r(x, q["lanco1"][1])[0] - X0 for x in [q["lanco1"][0]] + q["espelhos"][:q["cheios"]]]
    tom0, tom1 = q["tom"]
    fator = np.ones((h, w), np.float32)
    n = q["cheios"]
    for k in range(n):
        xa = bordas[k]
        xb = bordas[k + 1] if k + 1 < len(bordas) else w
        dentro = (xs >= xa) & (xs < xb)
        fator = np.where(dentro, tom0 + (tom1 - tom0) * k / (n - 1), fator)
        if k + 1 < len(bordas):                               # a sombra do espelho de cima neste degrau
            sf, sl = q["espelho"]
            fator = np.where(dentro, fator * (1 - sf * np.exp(-np.clip(xb - xs, 0, None) / sl)), fator)
    dx, dy, sig, frc = q["sombra"]
    som = cv2.GaussianBlur(cv2.warpAffine(cheio, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h)), (0, 0), sig)
    reg *= (1 - frc * som * (1 - cheio))[..., None]
    reg = reg * (1 - cheio[..., None]) + piso * fator[..., None] * cheio[..., None]

    # 3. do 8º em diante, esmaecido sobre o gramado, com os espelhos e o contorno claros
    k_ = q["esmaecer"]
    reg = reg * (1 - k_ * esm[..., None]) + piso * k_ * esm[..., None]
    cor, frc = q["espelho_esm"]
    traco = np.zeros(forma, np.float32)
    for lanco in ("lanco1", "lanco2"):
        _, y0, _, y1 = q[lanco]
        for x in q["espelhos"] + [q["lanco1"][2]]:
            traco = np.maximum(traco, linha_aa(forma, [p2r(x, y0), p2r(x, y1)], 0.5))
    for k in ("lanco1", "lanco2", "patamar"):
        x0, y0, x1, y1 = q[k]
        traco = np.maximum(traco, linha_aa(forma, [p2r(x0, y0), p2r(x1, y0), p2r(x1, y1), p2r(x0, y1)], 0.5, fechada=True))
    traco = traco[Y0:Y1, X0:X1] * (esm > 0.5)
    reg = reg * (1 - frc * traco[..., None]) + np.float32(cor) * frc * traco[..., None]

    # 4. a linha de corte
    cor, larg = q["corte"]
    lc = np.zeros(forma, np.float32)
    for c in corte:
        lc = np.maximum(lc, linha_aa(forma, c, larg))
    lc = lc[Y0:Y1, X0:X1][..., None]
    reg = reg * (1 - lc) + np.float32(cor) * lc
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    escada interna: degraus 1 a {n} cheios até o corte, o resto esmaecido ({k_:.0%}) sobre o gramado "
          f"aprovado; sem a barreira do motor")
    return out


# Térreo 11 e 12. Quarto e banho do motorista (pedido do usuário, 19/10/26: "representar a cama no quarto do
# motorista. representar a cuba e bancada da pia corretamente no banho do motorista. representar o box e o chuveiro
# adequadamente. o rótulo do quarto do motorista está no local errado"; o arco da porta do banho já foi, nas portas no
# granito). O motor fez a cama e o box como blocos lilás e a pia como uma cuba solta, sem bancada. No PDF
# (ARQ_LAYOUT HUMANIZAÇÃO, ARQ_BANCADAS e ARQ_LOUÇAS E METAIS):
# - a cama de solteiro encostada na parede de cima, com o travesseiro e o edredom com a ponta dobrada;
# - no banho, a bancada na parede de cima e na da direita, com a cuba quadrada de apoio (passa da frente da
#   bancada) e a torneira saindo da parede de cima;
# - o box ocupa a ponta da esquerda, até as duas folhas de vidro de correr, com o chuveiro de braço na parede de cima.
# Sem IA: os blocos do motor viram o granito (tecido de um trecho limpo do quarto, na luz do lugar) e entram, na
# geometria do PDF: a cama (lençol e edredom brancos com volume, a ponta dobrada mostrando o avesso, o travesseiro, a
# sombra curta); a bancada de quartzo com a cuba de louça, a válvula e a torneira cromada; as folhas de vidro do box
# e o chuveiro, como os aprovados. O rótulo do quarto vai para o lado da cama, como no PDF (`rotulos_casaa.py`).
MOTORISTA = {
    "limpar": [(1188, 631, 1211, 678), (1233, 630, 1257, 649), (1259, 576, 1293, 642)],   # px: box, pia, cama
    "fonte_granito": (1292, 585, 1316, 640),
    "cama": (2152.75, 1288.75, 2203.78, 1396.46), "travesseiro": (2156.15, 1292.15, 2200.37, 1315.96),
    "edredom": (2154.45, 1313.69, 2202.08, 1394.76), "dobra": (2191.87, 1313.69, 2202.08, 1323.9),
    "cores_cama": {"base": (196, 202, 210), "edredom": (228, 232, 237), "travesseiro": (238, 241, 244),
                   "avesso": (206, 212, 219), "contorno": (150, 154, 158)},
    "bancada": (2103.57, 1381.16, 2143.25, 1403.83), "cuba": (2112.11, 1388.0, 2134.7, 1410.6),
    "torneira": (2121.99, 1389.87, 2124.83, 1399.65), "valvula": ((2123.4, 1404.0), 1.3),
    "folhas": [(2060.2, 1421.69, 2060.77, 1466.14), (2061.05, 1410.42, 2061.62, 1454.87)],
    "chuveiro": {"ducha": (2039.2, 1388.2, 2042.9, 1391.9), "braco": (2040.5, 1381.8, 2041.7, 1389.2),
                 "canopla": (2039.6, 1381.2, 2042.5, 1381.8)}}


def motorista(out):
    from retoque_bege_bahia_terreo import quilting
    from retoque_subsolo_casae import (Tela, SOMBRA, LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO, CROMO,
                                       CROMO_CLARO, CROMO_ESCURO, QUARTZO, SS, vidro_box, chuveiro)
    q = MOTORISTA
    _, p2r = pdf_pavimento("Terreo")

    # os blocos do motor viram o granito
    apaga = np.zeros(out.shape[:2], bool)
    for x0, y0, x1, y1 in q["limpar"]:
        apaga[y0:y1, x0:x1] = True
    Yo = out.astype(np.float32).mean(axis=2)
    piso = ~cv2.dilate(apaga.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (Yo > 25) & (Yo < 110)
    med = cv2.medianBlur(out, 5).astype(np.float32)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    peso = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 6)
    campo = np.where((peso > 0.05)[..., None], nconv(med, piso.astype(np.float32), 6), nconv(med, piso.astype(np.float32), 18))
    fx0, fy0, fx1, fy1 = q["fonte_granito"]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32) / campo[fy0:fy1, fx0:fx1]
    f = f / f.reshape(-1, 3).mean(axis=0)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    novo = out.astype(np.float32)
    for k, (x0, y0, x1, y1) in enumerate(q["limpar"]):
        tex = quilting(fontes, y1 - y0, x1 - x0, p=16, sobra=5, candidatos=300, rng=np.random.default_rng(651 + k))
        novo[y0:y1, x0:x1] = tex[:y1 - y0, :x1 - x0] * campo[y0:y1, x0:x1]
    a = (cv2.GaussianBlur(apaga.astype(np.float32), (0, 0), 0.7) * apaga)[..., None]
    a *= (Yo > 25)[..., None]                                   # as paredes ficam
    out[:] = np.clip(out * (1 - a) + novo * a, 0, 255).astype(np.uint8)

    # a cama
    c = q["cores_cama"]
    tl = Tela(out, p2r, q["cama"])
    base = tl.ret(q["cama"], 0.8)
    tl.sombra(base, dx=-1.2, dy=1.2, sigma=1.4, forca=0.32)
    tl.pintar(base, c["base"])
    ed = tl.ret(q["edredom"], 1.2)
    dx0, dy0, dx1, dy1 = q["dobra"]
    tri = tl.vazia()                                            # a ponta dobrada (o avesso do edredom)
    pts = np.int32([tl.pt(dx0, dy0), tl.pt(dx1, dy1), tl.pt(dx1, dy0)])
    cv2.fillPoly(tri, [pts], 255)
    ed_sem = ed & ~tri
    dist = cv2.distanceTransform(ed_sem, cv2.DIST_L2, 5) / SS
    tom = 0.88 + 0.12 * np.clip(dist / 3.0, 0, 1)
    a_ = tl.reduzir(ed_sem)[..., None]
    cor = cv2.resize(np.float32(c["edredom"])[None, None] * tom[..., None] * (ed_sem[..., None] / 255.0), (tl.w, tl.h),
                     interpolation=cv2.INTER_AREA)
    tl.reg = tl.reg * (1 - a_) + cor
    tl.pintar(tri & ed, c["avesso"])
    dobra = tl.vazia()
    cv2.line(dobra, tuple(pts[0]), tuple(pts[1]), 255, max(1, int(0.5 * SS)))
    tl.sombra(dobra, dx=-0.4, dy=0.4, sigma=0.4, forca=0.25)
    tl.pintar(dobra & ed, c["contorno"], 0.6)
    tv = tl.ret(q["travesseiro"], 1.6)
    tl.sombra(tv, dx=-0.5, dy=0.5, sigma=0.6, forca=0.22)
    dist = cv2.distanceTransform(tv, cv2.DIST_L2, 5) / SS
    tom = 0.86 + 0.14 * np.clip(dist / 2.2, 0, 1)
    a_ = tl.reduzir(tv)[..., None]
    cor = cv2.resize(np.float32(c["travesseiro"])[None, None] * tom[..., None] * (tv[..., None] / 255.0), (tl.w, tl.h),
                     interpolation=cv2.INTER_AREA)
    tl.reg = tl.reg * (1 - a_) + cor
    tl.contorno(base, 0.3, c["contorno"])
    out = tl.gravar()

    # a bancada, a cuba de apoio e a torneira da parede de cima
    tl = Tela(out, p2r, (q["bancada"][0], q["bancada"][1], q["bancada"][2], q["cuba"][3]))
    b = tl.ret(q["bancada"])
    tl.sombra(b, **SOMBRA)
    tl.pintar(b, QUARTZO)
    tl.contorno(b, 0.35, (150, 153, 155))
    cb = tl.ret(q["cuba"], 2.4)
    tl.sombra(cb, **SOMBRA)
    tl.pintar(cb, LOUCA_CONTORNO)
    x0, y0, x1, y1 = q["cuba"]
    tl.pintar(tl.ret((x0 + 0.8, y0 + 0.8, x1 - 0.8, y1 - 0.8), 2.0), LOUCA)
    for i in range(6):                       # a bacia, da borda ao fundo
        k = i / 5
        tom = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
        ins = 2.0 + k * 3.0
        tl.pintar(tl.ret((x0 + ins, y0 + ins, x1 - ins, y1 - ins), max(0.6, 1.8 - k)), tom)
    (vx, vy), vr = q["valvula"]
    u, v = tl.pt(vx, vy)
    m = tl.vazia()
    cv2.circle(m, (int(u), int(v)), int(vr * 0.5483 * SS), 255, -1)
    tl.pintar(m, CROMO_ESCURO)
    tx0, ty0, tx1, ty1 = q["torneira"]
    m = tl.ret(q["torneira"], 0.6)
    tl.sombra(m, **SOMBRA)
    tl.pintar(m, CROMO_ESCURO)
    tl.pintar(tl.ret((tx0 + 0.3, ty0, (tx0 + tx1) / 2, ty1 - 0.4), 0.3), CROMO_CLARO)
    m = tl.vazia()
    u, v = tl.pt((tx0 + tx1) / 2, ty0 + 0.9)
    cv2.circle(m, (int(u), int(v)), int(1.0 * SS), 255, -1)
    tl.pintar(m, CROMO)
    out = tl.gravar()

    # o box: as duas folhas de vidro de correr e o chuveiro
    for folha in q["folhas"]:
        out = vidro_box(out, p2r, folha)
    ch = q["chuveiro"]
    out = chuveiro(out, p2r, ch["ducha"], ch["braco"], ch["canopla"])
    print("    motorista: blocos do motor em granito; cama com travesseiro e a ponta dobrada; bancada com a cuba de "
          "apoio e a torneira; box com as folhas de vidro e o chuveiro")
    return out


# Térreo, carros (pedido do usuário, 19/10/26: "mude as cores, deixe cada carro com uma única cor e deixe os carros
# desalinhados"). O motor fez o da esquerda branco e os outros dois no mesmo lilás, alinhados. Como nas Casas D e E
# (aprovadas): cada carro numa cor só, a da paleta da Casa D (branco perolado, grafite, azul-marinho), por uma curva
# de tom na luminância do próprio carro (a ordem do render fica: vidros mais escuros que a lataria, reflexos), com a
# cor só nos tons médios e claros (o vidro escuro fica neutro); e cada um com um deslocamento e um giro leves, para
# quebrar o alinhamento: o carro sai com a sombra dele (o granito volta, tecido por image quilting de trechos limpos
# do granito, na luz do lugar) e entra no lugar novo, com a sombra curta.
CARROS_A = {
    "janela": (1150, 680, 1420, 853),                         # px: a garagem (sem a pedra portuguesa de baixo)
    "fontes_granito": [(1292, 585, 1316, 640), (1234, 712, 1248, 842)],   # px: o quarto do motorista e o meio do vão
    # (nome, curva: ("escurecer", base, faixa, expoente) ou ("clarear", ini, fim, força), cor BGR, (dx, dy, giro))
    "carros": [("esquerda", ("clarear", 150.0, 215.0, 0.35), (0.99, 1.0, 1.01), (-1.0, 5.0, -2.0)),     # branco perolado
               ("meio", ("escurecer", 26.0, 74.0, 1.6), (1.02, 1.0, 0.98), (1.5, -4.0, 1.5)),           # grafite
               ("direita", ("escurecer", 18.0, 52.0, 1.4), (1.34, 0.96, 0.74), (-1.5, 3.0, -1.0))],     # azul-marinho
    "lum_carro": 95.0, "fecho": 9, "reflexo": 0.6, "cor_lum": (70.0, 140.0),
    "lanterna": (70, 140),                                    # R - B (e R - G) e R mínimos: só luz vermelha ou âmbar
    "folga": 31, "x_max": 1410,                               # o que sai: o carro e a sombra dele (até o jardim)
    "sombra": {"desloc": (-2.0, 2.0), "sigma": 1.5, "forca": 0.4}}


def carros_a(out):
    from scipy import ndimage
    from retoque_bege_bahia_terreo import quilting
    q = CARROS_A
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    Y = reg.mean(axis=2)
    m = cv2.morphologyEx((Y > q["lum_carro"]).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((q["fecho"],) * 2, np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    ids = sorted([i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 1500], key=lambda i: cen[i, 0])
    silhuetas = [ndimage.binary_fill_holes(lab == i) for i in ids]
    assert len(silhuetas) == len(q["carros"]), f"{len(silhuetas)} carros achados"
    # 1. cada carro numa cor só
    pintado = reg.copy()
    for sil, (nome, curva, cor, _) in zip(silhuetas, q["carros"]):
        lanterna = (reg[..., 2] - reg[..., 0] > q["lanterna"][0]) & (reg[..., 2] > q["lanterna"][1]) & \
            (reg[..., 2] - reg[..., 1] > q["lanterna"][0])
        topo = np.percentile(Y[sil], 97)
        if curva[0] == "escurecer":
            _, base, faixa, ex = curva
            Yn = base + faixa * np.clip(Y / topo, 0, 1) ** ex + q["reflexo"] * np.clip(Y - topo, 0, None)
        else:
            _, ini_, fim_, forca = curva
            t = np.clip((Y - ini_) / (fim_ - ini_), 0, 1)
            Yn = Y + forca * t * t * (3 - 2 * t) * (250 - Y)
        lo, hi = q["cor_lum"]
        sc = np.clip((Y - lo) / (hi - lo), 0, 1)[..., None]
        novo = Yn[..., None] * (1 + sc * (np.float32(cor)[None, None] - 1))
        a = (sil & ~lanterna)[..., None]
        pintado = np.where(a, novo, pintado)
        print(f"    carro da {nome}: curva {curva[0]}, cor {cor}")
    # 2. os carros saem: o granito tecido dos vãos, na luz do lugar
    tudo = np.zeros(Y.shape, bool)
    for s_ in silhuetas:
        tudo |= s_
    sai = cv2.dilate(tudo.astype(np.uint8), np.ones((q["folga"],) * 2, np.uint8)) > 0
    sai[:, q["x_max"] - wx0:] = False
    apaga = np.zeros(out.shape[:2], bool)
    apaga[wy0:wy1, wx0:wx1] = sai
    Yo = out.astype(np.float32).mean(axis=2)
    janela = np.zeros_like(apaga)
    janela[wy0:wy1, wx0:wx1] = True
    piso = janela & ~cv2.dilate(apaga.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (Yo > 25) & (Yo < 110)
    med = cv2.medianBlur(out, 5).astype(np.float32)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    peso = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 10)
    campo = np.where((peso > 0.05)[..., None], nconv(med, piso.astype(np.float32), 10),
                     nconv(med, piso.astype(np.float32), 30))
    fontes = []
    for fx0, fy0, fx1, fy1 in q["fontes_granito"]:
        f = out[fy0:fy1, fx0:fx1].astype(np.float32) / cv2.GaussianBlur(med[fy0:fy1, fx0:fx1], (0, 0), 6)
        f = f / f.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    tex = quilting(fontes, wy1 - wy0, wx1 - wx0, p=14, sobra=5, candidatos=400, rng=np.random.default_rng(652))
    novo_g = out.astype(np.float32)
    novo_g[wy0:wy1, wx0:wx1] = tex[:wy1 - wy0, :wx1 - wx0] * campo[wy0:wy1, wx0:wx1]
    a = (cv2.GaussianBlur(apaga.astype(np.float32), (0, 0), 1.0) * apaga)[..., None]
    out[:] = np.clip(out * (1 - a) + novo_g * a, 0, 255).astype(np.uint8)
    # 3. e entram no lugar novo, com o giro leve e a sombra curta
    h, w = Y.shape
    s = q["sombra"]
    for sil, (nome, _, _, (dx, dy, ang)) in zip(silhuetas, q["carros"]):
        ys, xs = np.nonzero(sil)
        c = (float(xs.mean()), float(ys.mean()))
        M = cv2.getRotationMatrix2D(c, ang, 1.0)
        M[:, 2] += (dx, dy)
        alfa = cv2.warpAffine(cv2.GaussianBlur(sil.astype(np.float32), (0, 0), 0.5), M, (w, h), flags=cv2.INTER_LINEAR)
        img = cv2.warpAffine(pintado, M, (w, h), flags=cv2.INTER_LINEAR)
        S = np.float32([[1, 0, s["desloc"][0]], [0, 1, s["desloc"][1]]])
        sb = cv2.GaussianBlur(cv2.warpAffine(alfa, S, (w, h)), (0, 0), s["sigma"]) * (1 - alfa)
        r = out[wy0:wy1, wx0:wx1].astype(np.float32) * (1 - s["forca"] * sb)[..., None]
        a = np.clip(alfa, 0, 1)[..., None]
        out[wy0:wy1, wx0:wx1] = np.clip(r * (1 - a) + img * a, 0, 255).astype(np.uint8)
    print(f"    garagem: {len(silhuetas)} carros, cada um numa cor, com deslocamento e giro leves")
    return out


# Térreo, sem arcos (decisão do usuário, 19/10/26, com as plantas de referência dos elementos, que não desenham o
# arco das portas: "remover os arcos, escadas com linhas"). Todos os arcos de porta do PDF da Casa A (as curvas da
# ARQ_PAREDE: 16 portas de giro, a pivotante com o arco grande e o pequeno, e as 12 da porta camarão da varanda)
# saem da imagem, os do motor e os que os itens acima desenharam no lugar do PDF; as folhas e os batentes ficam.
# - Portas de giro (o arco é um quarto de círculo): o círculo pelas pontas e pelo meio do arco, levado à imagem. Na
#   faixa de ±3 px em volta dele, onde o traço passa (o que difere do piso de dentro e de fora da faixa, na mesma
#   direção), a faixa inteira vira a textura do mesmo piso logo depois dela, na mesma direção (de quatro afastamentos,
#   o mais parecido com o piso em volta), com a borda suave: não fica fantasma do traço nem do halo claro dele. Onde
#   nenhum afastamento serve (o traço passa junto a um móvel), inpaint. Ficam de fora a folha e o batente (as retas
#   do centro às pontas do arco) e o que é preto.
# - Porta camarão (os arcos rasos, de 0,5 m): o motor pintou de cinza o setor entre cada folha e o arco. O setor
#   inteiro, menos as folhas pretas, vira travertino tecido de trechos limpos da varanda, normalizado, vezes o campo de
#   luz do piso em volta (convolução normalizada). Ficam as folhas em zigue-zague, as sombras delas e o trilho.
SEM_ARCOS = {"camada": "ARQ_PAREDE", "tol": 3.0, "limiar": 7, "inpaint": 18, "raso": 1.6,
             "camarao_fontes": [(705, 632, 765, 700), (690, 778, 760, 806)]}     # x0, y0, x1, y1 (px)


def sem_arcos(out):
    from retoque_bege_bahia_terreo import quilting
    q = SEM_ARCOS
    pg, p2r = pdf_pavimento("Terreo")
    im = out.copy()
    res = out.astype(np.float32)
    H, W = out.shape[:2]
    T = q["tol"]

    def bez(p, t):
        return sum(((1 - t) ** (3 - i)) * (t ** i) * [1, 3, 3, 1][i] * np.array([p[i].x, p[i].y]) for i in range(4))

    def circulo(a, b, c):
        (x1, y1), (x2, y2), (x3, y3) = a, b, c
        A = np.array([[x2 - x1, y2 - y1], [x3 - x1, y3 - y1]]) * 2
        cx, cy = np.linalg.solve(A, [x2 ** 2 - x1 ** 2 + y2 ** 2 - y1 ** 2, x3 ** 2 - x1 ** 2 + y3 ** 2 - y1 ** 2])
        return cx, cy, np.hypot(x1 - cx, y1 - cy)

    camarao = np.zeros((H, W), bool)
    n_giro = n_px = 0
    for d in pg.get_drawings():
        if d.get("layer") != q["camada"]:
            continue
        for it in d["items"]:
            if it[0] != "c":
                continue
            P0, Pm, P3 = (np.array(p2r(*bez(it[1:], t))) for t in (0, 0.5, 1))
            cx, cy, R = circulo(P0, Pm, P3)
            am = np.arctan2(Pm[1] - cy, Pm[0] - cx)

            def rel(a):
                return (a - am + np.pi) % (2 * np.pi) - np.pi
            lim0, lim3 = sorted((rel(np.arctan2(P0[1] - cy, P0[0] - cx)), rel(np.arctan2(P3[1] - cy, P3[0] - cx))))
            x0, x1 = int(max(0, cx - R - T - 2)), int(min(W, cx + R + T + 3))
            y0, y1 = int(max(0, cy - R - T - 2)), int(min(H, cy + R + T + 3))
            yy, xx = np.mgrid[y0:y1, x0:x1]
            r = np.hypot(xx - cx, yy - cy)
            ang = rel(np.arctan2(yy - cy, xx - cx))
            faixa = (np.abs(r - R) <= T) & (ang > lim0) & (ang < lim3)
            # a folha e o batente (as retas do centro às pontas) e o que é preto ficam
            prot = np.zeros(faixa.shape, bool)
            for E in (P0, P3):
                u = (E - (cx, cy)) / R
                prot |= (np.abs((xx - cx) * u[1] - (yy - cy) * u[0]) < 1.8) & ((xx - cx) * u[0] + (yy - cy) * u[1] > 0)
            reg = res[y0:y1, x0:x1]
            prot |= reg.mean(axis=2) < 55
            bb = d["rect"]
            if max(bb.width, bb.height) / max(1e-3, min(bb.width, bb.height)) >= q["raso"]:
                camarao[y0:y1, x0:x1] |= (((r <= R + T) & (ang > lim0 - 0.05) & (ang < lim3 + 0.05)) | faixa) & ~prot
                continue

            def amostra(rr):
                k = rr / np.maximum(r, 1e-3)
                return cv2.remap(im.astype(np.float32), (cx + (xx - cx) * k).astype(np.float32),
                                 (cy + (yy - cy) * k).astype(np.float32), cv2.INTER_CUBIC)
            bg = (amostra(R + T + 2) + amostra(R - T - 2)) / 2
            achado = faixa & (np.abs(reg - bg).max(axis=2) > q["limiar"]) & ~prot
            if not achado.any():
                continue
            perto = cv2.dilate(achado.astype(np.uint8), np.ones((2 * int(T) + 3,) * 2, np.uint8)).astype(bool)
            peso = np.clip((T + 1.0 - np.abs(r - R)) / 2.0, 0, 1) * (perto & ~prot & (ang > lim0) & (ang < lim3))
            cands = [amostra(r + k) for k in (2 * T + 2, -(2 * T + 2), 3 * T + 3, -(3 * T + 3))]
            dists = np.stack([np.abs(c - bg).max(axis=2) for c in cands])
            src = np.take_along_axis(np.stack(cands), dists.argmin(axis=0)[None, ..., None], axis=0)[0]
            ruim = (dists.min(axis=0) > q["inpaint"]) & (peso > 0)
            if ruim.any():
                pint = cv2.inpaint(np.clip(reg, 0, 255).astype(np.uint8), ruim.astype(np.uint8), 2, cv2.INPAINT_TELEA)
                src = np.where(ruim[..., None], pint.astype(np.float32), src)
            reg[:] = reg * (1 - peso[..., None]) + src * peso[..., None]
            n_giro += 1
            n_px += int((peso > 0).sum())
    print(f"    portas de giro: {n_giro} arcos fora ({n_px} px)")
    # porta camarão: o setor de cada arco raso vira travertino tecido, na luz do lugar
    escuro = cv2.dilate((im.astype(np.float32).mean(axis=2) < 70).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    cam = camarao & ~escuro
    if cam.any():
        ys, xs = np.nonzero(cam)
        bx0, by0, bx1, by1 = xs.min() - 8, ys.min() - 8, xs.max() + 9, ys.max() + 9
        fontes = [im[b:d, a:c].astype(np.float32) for a, b, c, d in q["camarao_fontes"]]
        tex = quilting(fontes, by1 - by0, bx1 - bx0, p=14, sobra=5, candidatos=300,
                       rng=np.random.default_rng(652))[:by1 - by0, :bx1 - bx0]
        tex = tex / cv2.GaussianBlur(tex, (0, 0), 8)
        med = cv2.medianBlur(im, 5).astype(np.float32)[by0:by1, bx0:bx1]
        piso = (~cam[by0:by1, bx0:bx1] & ~escuro[by0:by1, bx0:bx1]).astype(np.float32)
        campo = cv2.GaussianBlur(med * piso[..., None], (0, 0), 4) / \
            np.maximum(cv2.GaussianBlur(piso, (0, 0), 4), 1e-4)[..., None]
        a = np.maximum(cv2.GaussianBlur(cam[by0:by1, bx0:bx1].astype(np.float32), (0, 0), 0.6), cam[by0:by1, bx0:bx1])
        a = (a * ~escuro[by0:by1, bx0:bx1])[..., None]
        res[by0:by1, bx0:bx1] = res[by0:by1, bx0:bx1] * (1 - a) + tex * campo * a
        print(f"    porta camarão: o setor dos arcos rasos de volta ao travertino ({int(cam.sum())} px)")
    return np.clip(res, 0, 255).astype(np.uint8)


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
                    ("portoes", "área descoberta: os portões de correr dos dois lados", portoes),
                    ("9", "escada caracol: degraus 1 a 7 cheios, o resto esmaecido", caracol),
                    ("portas_granito", "portas no granito: folhas do PDF e arcos em cinza fino", portas_granito),
                    ("inox", "eletrodomésticos em inox (cozinha, gourmet e área de serviço)", inox),
                    ("gourmet", "bancada gourmet: área molhada, divisória, cuba e torneira", gourmet),
                    ("cozinha_pias", "bancada da cozinha em pedra: área molhada, cubas e torneiras", cozinha_pias),
                    ("3", "estar sob a projeção: 4 poltronas em X e a mesa triangular, não mesa de jantar", estar_projecao),
                    ("5", "lavabo: bancada com a cuba esculpida, vaso suspenso e a claraboia", lavabo_a),
                    ("pivotante", "porta pivotante: a folha até o hall externo e o arco pequeno", pivotante),
                    ("escada_interna", "escada interna: cheia até o corte, esmaecida depois; o jardim em volta", escada_interna),
                    ("11-12", "motorista: a cama, a bancada com a cuba, o box e o chuveiro", motorista),
                    ("carros", "garagem: cada carro numa cor e os três levemente desalinhados", carros_a),
                    ("sem_arcos", "portas sem os arcos (as folhas ficam); porta camarão sem o cinza", sem_arcos)]}


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

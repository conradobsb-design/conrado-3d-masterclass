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
  Térreo 1. Pilares (pedido do usuário, 19/10/26): os três redondos da varanda e o quadrado junto ao gourmet,
     em marrom no render, no preto das paredes e na geometria do PDF, como o pilar do Térreo da Casa E.

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
          "fonte": (580, 600, 690, 770),     # travertino da circulação (px da imagem): a textura do degrau
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
    fx0, fy0, fx1, fy1 = q["fonte"]
    src = out[fy0:fy1, fx0:fx1].astype(np.float32)
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


ITENS = {"Subsolo": [("1", "banho de serviço: o chuveiro e o vidro do box", chuveiro_servico),
                     ("2", "sauna: o banco horizontal de volta", banco_sauna),
                     ("3", "escada: depois da linha de corte, os degraus na cor e textura do Subsolo", escada),
                     ("4", "portas de vidro da academia: folhas de vidro claras, não pretas", portas_academia),
                     ("5", "janelas: vão, peitoril, vidro e caixilhos do PDF, no lugar da peça cinza", janelas),
                     ("6", "circulação: sem o traço preto na borda", traco_circulacao),
                     ("7", "depósito e circulação interna: piso contínuo, sem juntas", juntas),
                     ("8", "banhos feminino e masculino: as cubas grandes do PDF", cubas_banhos),
                     ("9", "boxes de vidro: ducha ao lado da sauna e banho feminino", boxes)],
         "Terreo": [("1", "pilares da varanda e do gourmet em preto, como as paredes", pilares)]}


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

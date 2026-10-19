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

Uso (da pasta POE642_CasaA/scripts/):
  python3 ajustes_casaa.py Subsolo     # -> ../renders/POE642_CasaA_PH_Subsolo_final_ajustes.png (+ _camada.png)
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
CASA = AQUI.parent
APROVADAS = {"Subsolo": CASA / "renders/POE642_CasaA_PH_Subsolo_final.png"}

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
# quadro comum (2000 px) -> imagem aprovada do Subsolo (o mesmo afim do banco e da escada)
AFIM_QR = ((0.99911, -0.000617, 1.542), (0.000113, 0.99973, -3.617))


def p2r_subsolo():
    import json
    import pymupdf
    import rotulos_casaa as A
    from opcoes_1pav_casae import quadro_pdf
    cfg = json.loads(A.CONFIG.read_text())
    q = A.PAVIMENTOS["Subsolo"]
    base = (A.CONFIG.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"]["Subsolo"]["base"]).resolve()
    pg = pymupdf.open(A.RAIZ / "_pdfs_cliente" / q["pdf"])[cfg["pavimentos"]["Subsolo"]["pagina"]]
    at, lt = cv2.imread(str(base), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(A.CASA / q["sem_tela"]), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg, cfg, lt, at, wb, hb, 2000)
    (a, b, c), (d, e, f) = AFIM_QR

    def p2r(x, y):
        qx, qy = p2q(x, y)
        return a * qx + b * qy + c, d * qx + e * qy + f
    return p2r


def chuveiro_servico(out):
    from retoque_subsolo_casae import chuveiro, vidro_box
    q = CHUVEIRO_SERV
    p2r = p2r_subsolo()
    for r in q["vidros"]:
        out = vidro_box(out, p2r, r)
    out = chuveiro(out, p2r, q["ducha"], q["braco"], q["canopla"])
    (x0, y0), (x1, y1) = p2r(*q["ducha"][:2]), p2r(*q["ducha"][2:])
    print(f"    banho de serviço: chuveiro na parede da esquerda (ducha em x {x0:.1f}-{x1:.1f}, y {y0:.1f}-{y1:.1f} px) "
          f"e as duas folhas de vidro do box")
    return out


ITENS = {"Subsolo": [("1", "banho de serviço: o chuveiro e o vidro do box", chuveiro_servico),
                     ("2", "sauna: o banco horizontal de volta", banco_sauna),
                     ("3", "escada: depois da linha de corte, os degraus na cor e textura do Subsolo", escada)]}


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

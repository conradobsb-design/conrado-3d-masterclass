"""Casa A Térreo, revisão do usuário de 25/11 (2ª leva, com os recortes do 12K).

1. "corrija a soleira e a representação das janelas do wc e da janela do banho varanda": as duas janelas sobre o JARDIM
   (4,79 m²) eram várias faixas paralelas. O vão de cada uma (entre os tocos de parede, 1630,6–1643,0) recebe a soleira
   (peitoril) limpa no tom das soleiras do GÁS e da área de serviço, e a folha do PDF (1636,8–1639,7, de quina a quina)
   no padrão: perfil cinza claro, vidro claro e a linha fina.
2. "corrija o entorno do piso" (os bancos da área gourmet): o piso em volta do banco de ripas tinha um halo claro (um
   retângulo mais claro, com a borda à esquerda e embaixo): o anel em volta do banco recebe o piso logo ao lado.
3. "remova esse traço preto solto ao lado do brise": a barra preta no canto do piso claro, entre os dois tracejados do
   pergolado, sai. Acima da borda do piso claro entra o bege da mesma linha (à direita do 2º tracejado); abaixo, o piso
   claro das linhas de baixo (a borda da esquerda segue reta), com o perfil da borda medido nas colunas limpas à direita.
   O fim do tracejado da esquerda (o gancho que encostava na barra) recebe o próprio tracejado, um passo acima.
4. "corrija o entorno do piso" (o DECK DE MADEIRA, só nos 12K: na final as tábuas estão inteiras): acima do rótulo
   DECK DE MADEIRA faltavam duas juntas entre as tábuas: cada uma recebe a junta da mesma tábua mais à direita, na altura
   medida dos dois lados (a junta segue sem degrau). Em volta do DESCE PARA O SUBSOLO (o remendo de um rótulo antigo,
   com outro tom, as juntas faltando e restos de letras) as tábuas, de junta a junta, recebem as tábuas de cima, deslocadas
   um número inteiro de tábuas (as juntas medidas na imagem); as letras do rótulo voltam por cima, com a borda refeita
   sobre o piso novo (sem halo).

5. "corrigir essas falhas" (o vidro fixo da varanda, junto à grama, onde encontra a parede de cima): na ponta do vidro
   havia restos de suportes (os ganchos cromados abaixo do vidro e uma peça curva no pé da parede) e a faixa clara do
   piso passava da face da parede. A ponta, até a face da parede (medida em cada imagem), recebe o próprio vidro e o
   piso da mesma linha à esquerda; o pé da parede recebe a sombra da mesma parede mais à direita.

Final, prancha e 12K A e B (cada item pelo registro local; o deck só nos 12K).

  python3 terreo_casaa_2511b.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vidros_claros_1911 as VC  # noqa: E402
from subsolo_casaa_juncao_portas_2511 import copiar  # noqa: E402
from terreo_casaa_2511 import soleira, tom_soleira  # noqa: E402

PLANTA = "A_Terreo"

JANELAS = [((1550.1, 1630.6, 1606.2, 1643.0), [(1549.5, 1636.8, 1606.8, 1639.7)]),     # WC
           ((1618.8, 1630.6, 1674.9, 1643.0), [(1618.2, 1636.8, 1675.5, 1639.7)])]     # banho varanda
BANCO = [((1343.0, 1396.5, 1355.6, 1517.5), (-14.0, 0.0)),       # à esquerda do banco de ripas
         ((1355.6, 1509.6, 1396.0, 1517.5), (0.0, 9.0)),         # embaixo
         ((1391.6, 1396.5, 1396.0, 1509.6), (6.0, 0.0)),         # à direita
         ((1355.6, 1396.5, 1391.6, 1400.4), (0.0, -5.0))]        # em cima
BRISE_BARRA = (1221.3, 1203.5, 1231.0, 1212.0)    # a barra preta (e a sua sombra), entre os dois tracejados
BRISE_DX = 14.0                                    # o bege da mesma linha, à direita do 2º tracejado
BRISE_DY = 5.0                                     # o piso claro das linhas de baixo
BRISE_LIMPAS = (1234.0, 1243.0)                    # colunas limpas à direita: o perfil da borda bege/claro
BRISE_TRACEJADO = ((1219.0, 1203.5, 1221.3, 1208.0), 7.0)   # o fim do tracejado da esquerda e o passo dele
BRISE_PE = ((1219.0, 1207.8, 1221.3, 1208.9), 2.5)          # o pé da barra embaixo do tracejado: o bege logo abaixo
# DECK DE MADEIRA: as juntas que faltavam (x0, x1, y aproximado da junta, dx da junta inteira à direita)
DECK_JUNTAS = [(783.0, 888.0, 715.5, 100.0), (802.0, 868.0, 727.5, 80.0)]
JUNTA_MEIA = 3.5                                   # a faixa da junta: ±3,5 px da final
# DESCE PARA O SUBSOLO: de junta a junta (aproximadas), da borda da grama à faixa clara da escada
DESCE = dict(x=(722.0, 902.0), juntas=(1066.4, 1113.5), tabuas=4, medir=(740.0, 890.0),
             letras=805.0)        # as letras do rótulo começam à direita daqui (à esquerda: restos do remendo antigo)
# o vidro fixo de cima: a ponta junto à parede (px da final): a busca da face, a do pé e os deslocamentos das fontes
VIDRO_TOPO = dict(face=(1586.0, 1596.0, 345.0, 348.0), pe=(1611.0, 1626.0, 344.0, 358.0), abaixo=337.0,
                  dx_esq=-6.0, dx_dir=18.0, larg=5.0, pe_larg=16.0)
SO_12K = {"deck"}         # na final as tábuas do deck estão inteiras: o deck só nos 12K
ITENS = {
    "janelas": (1540.0, 1622.0, 1685.0, 1650.0),
    "banco": (1270.0, 1385.0, 1410.0, 1525.0),
    "brise": (1190.0, 1180.0, 1260.0, 1240.0),
    "deck": (727.0, 560.0, 1080.0, 1110.0),
    "vidro_topo": (1560.0, 325.0, 1650.0, 362.0),
}


def P_(escala, origem):
    return lambda x, y: (int(round((x - origem[0]) * escala)), int(round((y - origem[1]) * escala)))


def junta_y(img, xa, xb, y, escala, origem, raio=3.0):
    """A altura (px da final, subpixel) da junta mais escura perto de `y`, nas colunas xa..xb."""
    P = P_(escala, origem)
    a, b0 = P(xa, y - raio)
    b, b1 = P(xb, y + raio)
    perfil = img[b0:b1, a:b].astype(np.float32).mean(axis=(1, 2))
    k = int(np.argmin(perfil))
    if 0 < k < len(perfil) - 1:
        y0, y1, y2 = perfil[k - 1], perfil[k], perfil[k + 1]
        k = k + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-9)
    return origem[1] + (b0 + k + 0.5) / escala


def juntas_deck(img, escala, origem):
    """As juntas que faltavam acima do DECK DE MADEIRA: a faixa da junta recebe a mesma tábua mais à direita, com a
    junta levada (subpixel) da altura dela à altura das juntas dos dois lados da falha."""
    P = P_(escala, origem)
    for x0, x1, y, dx in DECK_JUNTAS:
        ye = junta_y(img, x0 - 18.0, x0 - 2.0, y, escala, origem)           # a junta à esquerda da falha
        yd = junta_y(img, x1 + 2.0, x1 + 18.0, y, escala, origem)           # e à direita
        yf = junta_y(img, x0 + dx, x1 + dx, y, escala, origem)              # a da fonte
        A0, B0 = P(x0, min(ye, yd) - JUNTA_MEIA)
        A1, B1 = P(x1, max(ye, yd) + JUNTA_MEIA)
        H, W = B1 - B0, A1 - A0
        xs = origem[0] + (np.arange(A0, A1, dtype=np.float32) + 0.5) / escala
        alvo = ye + (yd - ye) * np.clip((xs - x0) / (x1 - x0), 0, 1)       # a junta, reta de um lado ao outro
        mx = np.broadcast_to(np.arange(A0, A1, dtype=np.float32)[None, :] + dx * escala, (H, W))
        my = np.arange(B0, B1, dtype=np.float32)[:, None] + (yf - alvo)[None, :] * escala
        nova = cv2.remap(img, np.ascontiguousarray(mx, np.float32), np.ascontiguousarray(my, np.float32),
                         cv2.INTER_CUBIC).astype(np.float32)
        reg = img[B0:B1, A0:A1].astype(np.float32)
        a = np.ones((H, W), np.float32)
        mh, mv = max(1, int(round(4.0 * escala))), max(1, int(round(1.0 * escala)))
        a[:, :mh] *= np.linspace(0, 1, mh, dtype=np.float32)[None, :]
        a[:, -mh:] *= np.linspace(1, 0, mh, dtype=np.float32)[None, :]
        a[:mv] *= np.linspace(0, 1, mv, dtype=np.float32)[:, None]
        a[-mv:] *= np.linspace(1, 0, mv, dtype=np.float32)[:, None]
        img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + nova * a[..., None], 0, 255).astype(np.uint8)
        print(f"      junta {y:.1f}: esquerda {ye:.2f}, direita {yd:.2f}, fonte {yf:.2f}")
    return img


def letras_por_cima(velho, novo, escala, so=None):
    """As letras do rótulo (o cinza escuro de `velho`) por cima do piso `novo`, com a borda antialiased refeita: a
    cobertura de cada pixel sai do fundo antigo (as letras tiradas por inpaint) e a cor da letra entra sobre o novo."""
    L = velho.mean(2)
    nucleo = L < 80
    if so is not None:
        nucleo &= so
    n, lab, st, _ = cv2.connectedComponentsWithStats(nucleo.astype(np.uint8))
    nucleo = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 10 * escala * escala])
    if nucleo.sum() < 10:
        return novo
    cor = np.median(velho[nucleo], axis=0)
    r = max(1, int(round(0.9 * escala)))
    zona = cv2.dilate(nucleo.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    fundo = cv2.inpaint(np.clip(velho, 0, 255).astype(np.uint8), cv2.dilate(zona, np.ones((3, 3), np.uint8)),
                        max(3, r), cv2.INPAINT_TELEA).astype(np.float32)
    Lf = fundo.mean(2)
    alfa = np.clip((Lf - L) / np.maximum(Lf - float(cor.mean()), 20.0), 0, 1) * (zona > 0)
    return novo * (1 - alfa[..., None]) + cor[None, None, :] * alfa[..., None]


def borda_x(img, xa, xb, y0, y1, escala, origem, escuro_esq):
    """A borda vertical (px da final) entre xa e xb: onde a luminância média das linhas y0..y1 cruza o meio."""
    P = P_(escala, origem)
    a, b0 = P(xa, y0)
    b, b1 = P(xb, y1)
    perfil = img[b0:b1, a:b].astype(np.float32).mean(axis=(0, 2))
    meio = 0.5 * (perfil[:3].mean() + perfil[-3:].mean())
    acima = perfil > meio if escuro_esq else perfil < meio
    k = int(np.argmax(acima))
    return origem[0] + (a + k) / escala


def desce(img, escala, origem):
    """Em volta do DESCE PARA O SUBSOLO: de junta a junta, as tábuas de cima (um número inteiro de tábuas), da borda da
    grama à faixa clara da escada; as letras voltam por cima. As juntas da fonte são levadas, coluna a coluna, às
    juntas de cima e de baixo da falha (as juntas do deck têm pequenos degraus de meio px)."""
    P = P_(escala, origem)
    yt = junta_y(img, *DESCE["medir"], DESCE["juntas"][0], escala, origem)
    yb = junta_y(img, *DESCE["medir"], DESCE["juntas"][1], escala, origem)
    per = (DESCE["juntas"][1] - DESCE["juntas"][0]) / DESCE["tabuas"]
    ys = junta_y(img, *DESCE["medir"], yt - DESCE["tabuas"] * per, escala, origem)     # a junta da fonte
    xg = borda_x(img, DESCE["x"][0], DESCE["x"][0] + 12.0, yt, yb, escala, origem, escuro_esq=True)   # grama | deck
    xc = borda_x(img, DESCE["x"][1] - 12.0, DESCE["x"][1], yt + 1.0, yt + 10.0, escala, origem,   # deck | faixa
                 escuro_esq=True)                                                 # (acima das letras)
    x0, x1 = xg - 1.0, xc - 0.15
    # as juntas coluna a coluna (faixas de 8 px da final): em cima e embaixo da falha, e as duas da fonte
    cx = np.arange(x0 + 4.0, x1 - 3.0, 8.0)
    med = lambda v: np.array([junta_y(img, c - 4.0, c + 4.0, v, escala, origem, raio=2.5) for c in cx])
    from scipy.ndimage import median_filter
    sm = lambda v: median_filter(v, size=7, mode="nearest")       # as juntas são retas: só o degrau fica
    top, bot, s0 = sm(med(yt)), sm(med(yb)), sm(med(ys))
    s1 = sm(med(ys + (yb - yt)))
    m = 0.6
    A0, B0 = P(x0, yt - m - 0.6)
    A1, B1 = P(x1, yb + m + 0.6)
    H, W = B1 - B0, A1 - A0
    xs = origem[0] + (np.arange(A0, A1, dtype=np.float32) + 0.5) / escala
    f = lambda v: np.interp(xs, cx, v).astype(np.float32)
    top, bot, s0, s1 = f(top), f(bot), f(s0), f(s1)
    yy = origem[1] + (np.arange(B0, B1, dtype=np.float32) + 0.5) / escala
    ysrc = s0[None, :] + (yy[:, None] - top[None, :]) * ((s1 - s0) / (bot - top))[None, :]
    my = (ysrc - origem[1]) * escala - 0.5
    mx = np.broadcast_to(np.arange(A0, A1, dtype=np.float32)[None, :], (H, W))
    src = cv2.remap(img, np.ascontiguousarray(mx, np.float32), np.ascontiguousarray(my, np.float32),
                    cv2.INTER_CUBIC).astype(np.float32)
    reg = img[B0:B1, A0:A1].astype(np.float32)
    a = np.clip((yy[:, None] - (top[None, :] - m)) / (2 * m), 0, 1) * np.clip(((bot[None, :] + m) - yy[:, None]) / (2 * m), 0, 1)
    # nas juntas de cima e de baixo, o que for mais escuro que a junta da fonte (o contorno do remendo antigo) sai
    perto = (np.abs(yy[:, None] - top[None, :]) < 1.6) | (np.abs(yy[:, None] - bot[None, :]) < 1.6)
    resto = (reg.mean(2) < src.mean(2) - 25) & perto
    resto = cv2.dilate(resto.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & perto
    a[resto] = 1.0
    novo = reg * (1 - a[..., None]) + src * a[..., None]
    novo = letras_por_cima(reg, novo, escala, so=np.broadcast_to(xs[None, :] >= DESCE["letras"], (H, W)))
    img[B0:B1, A0:A1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    print(f"      DESCE: juntas {yt:.2f} a {yb:.2f}, fonte {ys:.2f}; x {x0:.1f} a {x1:.1f}; "
          f"juntas em cima {top.min():.2f}-{top.max():.2f}, fonte {s0.min():.2f}-{s0.max():.2f}")
    return img


def brise(img, escala, origem):
    P = P_(escala, origem)
    # o fim do tracejado da esquerda: o próprio tracejado, um passo acima (o gancho que encostava na barra sai)
    (x0, y0, x1, y1), passo = BRISE_TRACEJADO
    A0, B0 = P(x0, y0)
    A1, B1 = P(x1, y1)
    d = int(round(passo * escala))
    img[B0:B1, A0:A1] = img[B0 - d:B1 - d, A0:A1]
    (x0, y0, x1, y1), desce_ = BRISE_PE
    A0, B0 = P(x0, y0)
    A1, B1 = P(x1, y1)
    d = int(round(desce_ * escala))
    img[B0:B1, A0:A1] = img[B0 + d:B1 + d, A0:A1]
    # a barra: acima da borda, o bege da mesma linha (à direita); abaixo, o piso claro de baixo, com o perfil da borda
    x0, y0, x1, y1 = BRISE_BARRA
    A0, B0 = P(x0, y0)
    A1, B1 = P(x1, y1)
    dx, dy = int(round(BRISE_DX * escala)), int(round(BRISE_DY * escala))
    R0, R1 = P(BRISE_LIMPAS[0], 0)[0], P(BRISE_LIMPAS[1], 0)[0]
    reg = img[B0:B1, A0:A1].astype(np.float32)
    bege = img[B0:B1, A0 + dx:A1 + dx].astype(np.float32)
    lim = img[B0:B1, R0:R1].astype(np.float32)
    lim_dy = img[B0 + dy:B1 + dy, R0:R1].astype(np.float32)
    claro = img[B0 + dy:B1 + dy, A0:A1].astype(np.float32) + np.median(lim - lim_dy, axis=1)[:, None, :]
    lum = lim.mean(axis=(1, 2))
    n = max(2, int(round(3 * escala)))
    acima = img[B0 - n:B0, R0:R1].astype(np.float32).mean()
    abaixo = img[B1:B1 + n, R0:R1].astype(np.float32).mean()
    meio = 0.5 * (acima + abaixo)
    i = int(np.argmax(lum > meio))
    e = i - 1 + (meio - lum[i - 1]) / max(lum[i] - lum[i - 1], 1e-3) if i > 0 else 0.0
    yy = np.arange(reg.shape[0], dtype=np.float32) + 0.5
    w = np.clip((yy - (e + 0.5)) / max(1.0, escala) + 0.5, 0, 1)
    novo = bege * (1 - w[:, None, None]) + claro * w[:, None, None]
    mv = max(1, int(round(0.5 * escala)))
    a = np.ones(reg.shape[0], np.float32)
    a[:mv] = np.linspace(0, 1, mv + 2, dtype=np.float32)[1:-1]
    a[-mv:] = np.linspace(1, 0, mv + 2, dtype=np.float32)[1:-1]
    img[B0:B1, A0:A1] = np.clip(reg * (1 - a[:, None, None]) + novo * a[:, None, None], 0, 255).astype(np.uint8)
    print(f"      brise: borda bege/claro em {origem[1] + (B0 + e + 0.5) / escala:.2f}")
    return img


def copia_h(img, caixa, dx, escala, origem):
    """A caixa (px da final) recebe a mesma linha deslocada dx (sem esfumar: as estruturas são horizontais)."""
    P = P_(escala, origem)
    A0, B0 = P(caixa[0], caixa[1])
    A1, B1 = P(caixa[2], caixa[3])
    d = int(round(dx * escala))
    img[B0:B1, A0:A1] = img[B0:B1, A0 + d:A1 + d]
    return img


def vidro_topo(img, escala, origem):
    """A ponta do vidro fixo de cima junto à parede: a face e o pé da parede medidos na imagem. À esquerda da face, abaixo
    do vidro, só os pixels que destoam do piso da mesma linha (os suportes, a faixa que passava da face) recebem o piso
    logo à esquerda; embaixo da parede, a sombra da mesma parede mais à direita."""
    v = VIDRO_TOPO
    P = P_(escala, origem)
    a0, b0 = P(v["face"][0], v["face"][2])
    a1, b1 = P(v["face"][1], v["face"][3])
    prof = img[b0:b1, a0:a1].astype(np.float32).mean(axis=(0, 2))
    parede = float(np.median(prof[-max(2, int(2 * escala)):]))
    k = len(prof) - 1
    while k > 0 and prof[k - 1] < parede + 18:
        k -= 1
    xf = origem[0] + (a0 + k) / escala
    c0, d0 = P(v["pe"][0], v["pe"][2])
    c1, d1 = P(v["pe"][1], v["pe"][3])
    col = img[d0:d1, c0:c1].astype(np.float32).mean(axis=(1, 2))
    j = int(np.argmax(col > parede + 30))
    yb = origem[1] + (d0 + j) / escala
    # os suportes: até a face, os pixels que destoam do piso (e do vidro) da mesma linha logo à esquerda
    A0, B0 = P(xf - v["larg"], v["abaixo"])
    A1, B1 = P(xf, yb + 3.0)
    d = int(round(v["dx_esq"] * escala))
    reg = img[B0:B1, A0:A1].astype(np.float32)
    src = img[B0:B1, A0 + d:A1 + d].astype(np.float32)
    # o piso escurece rente à parede (a sombra): a fonte leva o degradê de cada linha, medido à esquerda e prolongado
    G0 = P(xf - v["larg"] - 14.0, 0)[0]
    viz = img[B0:B1, G0:A0].astype(np.float32).mean(2)
    xs = np.arange(G0, A0, dtype=np.float32)
    xm = xs.mean()
    incl = ((viz - viz.mean(1, keepdims=True)) * (xs - xm)[None, :]).sum(1) / ((xs - xm) ** 2).sum()
    incl = np.minimum(incl, 0.0)                       # só escurece em direção à parede
    xa = np.arange(A0, A1, dtype=np.float32)
    nivel = viz.mean(1, keepdims=True) + incl[:, None] * (xa[None, :] - xm)
    nivel_src = viz.mean(1, keepdims=True) + incl[:, None] * (xa[None, :] + d - xm)
    src = src * np.clip(nivel / np.maximum(nivel_src, 1.0), 0.7, 1.1)[..., None]
    dif = reg.mean(2) - src.mean(2)
    destoa = ((np.abs(reg - src).max(2) > 22) | (dif > 8)).astype(np.uint8)          # (e o claro que descia rente à face)
    r = max(1, int(round(0.5 * escala)))
    destoa = cv2.dilate(destoa, np.ones((2 * r + 1, 2 * r + 1), np.uint8))
    a = np.clip(cv2.GaussianBlur(destoa.astype(np.float32), (0, 0), max(0.5, 0.3 * escala)) * 1.5, 0, 1)
    img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + src * a[..., None], 0, 255).astype(np.uint8)
    # o pé da parede (a peça curva e o risco escuro): a mesma parede mais à direita, da última linha da parede para baixo
    A0, B0 = P(xf, yb - 0.8)
    A1, B1 = P(xf + v["pe_larg"], yb + 3.5)
    d = int(round(v["dx_dir"] * escala))
    reg = img[B0:B1, A0:A1].astype(np.float32)
    src = img[B0:B1, A0 + d:A1 + d].astype(np.float32)
    w = np.ones(reg.shape[1], np.float32)
    mh = max(1, int(round(3.0 * escala)))
    w[-mh:] = np.linspace(1, 0, mh, dtype=np.float32)
    img[B0:B1, A0:A1] = np.clip(reg * (1 - w[None, :, None]) + src * w[None, :, None], 0, 255).astype(np.uint8)
    # a sombra do pé dobra a quina suave (2 px à esquerda da face, só no piso abaixo da parede)
    A0, B0 = P(xf - 2.0, yb)
    A1, B1 = P(xf, yb + 3.5)
    reg = img[B0:B1, A0:A1].astype(np.float32)
    src = img[B0:B1, A0 + d:A1 + d].astype(np.float32)
    w = np.linspace(0, 1, reg.shape[1] + 2, dtype=np.float32)[1:-1]
    img[B0:B1, A0:A1] = np.clip(reg * (1 - w[None, :, None]) + src * w[None, :, None], 0, 255).astype(np.uint8)
    print(f"      vidro de cima: face da parede {xf:.2f}, pé {yb:.2f}; {int((a > 0.5).sum())} px dos suportes")
    return img


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    if nome == "janelas":
        cor = tom_soleira(img, escala, origem)            # o tom da soleira nova do GÁS
        traco = 0.5 if escala <= 1.5 else min(0.5, EP.TRACO_12K / escala)
        for vao, folha in JANELAS:
            img = soleira(img, vao, cor, escala, origem)
            img = VC.redesenhar(img, folha, escala=escala, origem=origem, traco=traco, inpaint=False)
    elif nome == "banco":
        for c, d in BANCO:
            img = copiar(img, c, d, escala, origem)
    elif nome == "brise":
        img = brise(img, escala, origem)
    elif nome == "vidro_topo":
        img = vidro_topo(img, escala, origem)
    elif nome == "deck":
        img = juntas_deck(img, escala, origem)
        img = desce(img, escala, origem)
    return img


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in ITENS:
            if nome not in SO_12K:
                im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome, (x0, y0, x1, y1) in ITENS.items():
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

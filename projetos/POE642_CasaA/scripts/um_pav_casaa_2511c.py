"""Casa A 1º Pavimento, 3ª leva de 25/11 (pedidos do usuário com os recortes do 12K B).

- **Escada em U** ("sim, faça os degraus em transparência na escada em U"): o trecho do lance à esquerda da linha de
  corte, que era o vão branco, com os degraus no tom dos degraus cheios (os de agora, na pedra do Térreo) a 58%, como a
  caracol, e as linhas dos degraus finas (cheias, como no PDF); os guarda-corpos, a linha de corte e o contorno por cima.
- **Vazio da sala íntima** ("remover esse borrado na parte branca"; depois, "mantenha o mobiliario" e "mantenha
  transparente o mobiliario e demais"): sai só a mancha cinza no alto, junto à parede e ao guarda-corpo (o branco de logo
  abaixo, em espelho); os móveis do Térreo em transparência e o X ficam, nos dois vazios.
- **Piso abaixo do vazio da sala íntima** ("corrigir esses erros no piso"): os tracinhos da linha de projeção antiga logo
  abaixo do guarda-corpo saem (o travertino refeito na faixa, com a luz do piso em volta).
- **Guarda-corpo do vazio grande** ("corrigir o guarda corpo"): as duas linhas soltas e as manchas escuras entre a
  circulação e o vazio saem; o travertino da circulação até a borda da laje (2255,9) e o guarda-corpo de vidro fino
  (1,2 px, como os do vazio da sala íntima e da escada) na borda, com a sombra curta no piso.
- **Parede** ("corrigir a parede"): a parede entre a circulação e o vazio grande trazia, do lado do vazio, uma faixa
  escura com um filete claro e a curva no alto; a face da parede reta na linha do PDF (2255,9), com o vazio do lado em
  espelho (os móveis em transparência ficam).
- **Caracol** ("essa região em volta da escada é de mesmo piso do restante" e "somente nessa área"): o trecho de cima à
  direita, junto aos degraus que chegam (do guarda-corpo do raio de 90° à saleta, da porta de correr ao guarda-corpo em
  L), no Bege Bahia da saleta, sem a linha que o separava dela; o resto em volta da escada continua vão.
- **Banho master, janela da floreira** ("corrigir a soleira da janela"): a soleira em travertino um tom abaixo do piso,
  de um batente ao outro, com a face de fora em linha fina; as três folhas de correr do PDF (escalonadas) em vidro claro
  com o contorno fino preto e o filete do meio; os arremates de cima e de baixo no tom do caixilho.
- **Banho master, banheira** ("corrigir a torneira da banheira e a banheira"): o travertino refeito na pegada (saem os
  arcos claros da banheira antiga e o recorte da ponta), a banheira oval da biblioteca de novo no lugar do PDF e o
  misturador de piso desenhado em planta pelo PDF (o corpo, as duas alavancas, a ducha e a bica sobre a borda), em metal
  escovado, com a sombra curta (a peça da biblioteca era uma foto de frente).

Final, prancha e 12K A e B.

  python3 um_pav_casaa_2511c.py [item ...]
"""
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vetor_2511 as V               # noqa: E402
import terreo_casaa_2511d as D       # noqa: E402
import um_pav_casaa_2511b as B       # noqa: E402

PLANTA = "A_1Pavimento"


def _reg(img, caixa, s, origem, folga=2):
    jan = V.janela(img, caixa, s, origem, folga=folga)
    X0, Y0, X1, Y1 = jan
    return jan, img[Y0:Y1, X0:X1].astype(np.float32)


def _gravar(img, jan, reg):
    X0, Y0, X1, Y1 = jan
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
ESCADA_T = dict(caixa=(2250.0, 908.0, 2420.0, 992.0), amostra=(2262.0, 1030.0, 2410.0, 1075.0), opac=0.58,
                linha=0.30, linha_a=0.75, linha_esc=0.66)


def escada_u_transp(img, s, origem, q=ESCADA_T):
    E = D.ESCADA
    jan, reg = _reg(img, q["caixa"], s, origem)
    a_sup = V.cob([V.ret(*E["sup"])], jan, s, origem)
    x0s, y0s, _, y1s = E["sup"]
    esq = [(x0s, y0s)] + [tuple(p) for p in E["quebra"]] + [(x0s, y1s)]
    a_t = V.cob([esq], jan, s, origem) * a_sup
    # o tom dos degraus cheios de agora (o lance de baixo)
    ax0, ay0, ax1, ay1 = V.janela(img, q["amostra"], s, origem, folga=0)
    am = img[ay0:ay1, ax0:ax1].reshape(-1, 3).astype(np.float32)
    La = am.mean(1)
    tom = np.median(am[(La > 120) & (La < 235)], axis=0)
    L = reg.mean(2)
    a = a_t * np.clip((L - 175.0) / 30.0, 0, 1)                    # as linhas escuras ficam por cima
    reg = reg * (1 - q["opac"] * a[..., None]) + tom * (q["opac"] * a)[..., None]
    lin = np.zeros(a.shape, np.float32)
    for xl in E["xs_sup"][1:-1]:
        lin = np.maximum(lin, V.cob([V.ret(xl - q["linha"] / 2, y0s, xl + q["linha"] / 2, y1s)], jan, s, origem))
    reg = V.compor(reg, lin * a_t * q["linha_a"], tom * q["linha_esc"])
    return _gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
# Os vazios: o desenho de dentro (os móveis e as paredes do Térreo em transparência, o X) fica ("mantenha o mobiliario",
# "mantenha transparente o mobiliario e demais"); sai só a mancha cinza no alto do vazio da sala íntima (o branco de logo
# abaixo, em espelho) e, no vazio grande, a faixa colada à parede e o filete junto ao guarda-corpo (o branco do lado, em
# espelho).
VAZIO_A = dict(mancha=[(1950.0, 611.0), (2026.6, 611.0), (2026.6, 609.0), (2108.0, 609.0), (2108.0, 626.0),
                       (1950.0, 626.0)], pena=1.5,
               piso=(2035.6, 882.5, 2158.5, 892.5), piso_luz=[(2040.0, 892.5, 2150.0, 905.0),
                                                            (2158.5, 884.0, 2175.0, 905.0)])
VAZIO_B = dict(faixas=[(2255.9, 402.6, 2261.5, 612.0), (2255.9, 612.0, 2257.6, 878.3)],
               piso=(2245.6, 610.6, 2254.7, 878.6), piso_luz=[(2226.0, 615.0, 2245.0, 875.0)],
               vidro=(2254.7, 610.6, 2255.9, 878.8), vidro_cor=(238, 236, 231), borda_cor=(112, 112, 110),
               borda=0.24, sombra=0.16)


def _espelho(img, r, s, origem, lado, pena=0.0):
    """O retângulo r coberto pelo trecho vizinho em espelho ("baixo": o de logo abaixo; "dir": o de logo à direita)."""
    jan = V.janela(img, r, s, origem, folga=0)
    X0, Y0, X1, Y1 = jan
    if lado == "baixo":
        n = Y1 - Y0
        fonte = img[Y1:Y1 + n, X0:X1][::-1].astype(np.float32)
    else:
        n = X1 - X0
        fonte = img[Y0:Y1, X1:X1 + n][:, ::-1].astype(np.float32)
    a = V.cob([V.ret(*r)], jan, s, origem)
    if pena:
        k = pena * s
        x0, y0, x1, y1 = r
        dentro = V.cob([V.ret(x0 + pena, y0, x1 - pena, y1 - pena)], jan, s, origem)
        a = np.maximum(dentro, cv2.GaussianBlur(dentro, (0, 0), max(0.5, k / 2))) * a
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    reg = V.compor(reg, a, fonte)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def vazio_a(img, s, origem, q=VAZIO_A):
    # sob a parede e sob o guarda-corpo (sem tocar neles): o branco de logo abaixo, em espelho na linha de baixo,
    # com a borda suave dos lados e embaixo
    pol = q["mancha"]
    xs_ = [p_[0] for p_ in pol]
    ys_ = [p_[1] for p_ in pol]
    jan = V.janela(img, (min(xs_), min(ys_), max(xs_), max(ys_)), s, origem, folga=0)
    X0, Y0, X1, Y1 = jan
    n = Y1 - Y0
    fonte = img[Y1:Y1 + n, X0:X1][::-1].astype(np.float32)
    a = V.cob([pol], jan, s, origem)
    e = q["pena"]
    x0, x1, yb = min(xs_), max(xs_), max(ys_)
    dentro = V.cob([[(x0 + e, p_[1]) if p_[0] == x0 else ((x1 - e, p_[1]) if p_[0] == x1 else p_) for p_ in
                     [(x, (yb - e if y == yb else y)) for x, y in pol]]], jan, s, origem)
    a = np.maximum(dentro, cv2.GaussianBlur(dentro, (0, 0), max(0.5, e * s / 2))) * a
    reg = V.compor(img[Y0:Y1, X0:X1].astype(np.float32), a, fonte)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    # os tracinhos no piso logo abaixo do guarda-corpo
    return D.refazer_piso(img, s, origem, [V.ret(*q["piso"])], ref_luz=[V.ret(*r) for r in q["piso_luz"]], pena=0.8)


def vazio_b(img, s, origem, q=VAZIO_B):
    # a faixa colada à parede e o filete junto ao guarda-corpo: o vazio do lado, em espelho
    for r in q["faixas"]:
        img = _espelho(img, r, s, origem, "dir")
    # o piso da circulação até a borda da laje (sem as linhas soltas do guarda-corpo de antes)
    img = D.refazer_piso(img, s, origem, [V.ret(*q["piso"])], ref_luz=[V.ret(*r) for r in q["piso_luz"]], pena=0.6)
    jan, reg = _reg(img, (2240.0, 600.0, 2262.0, 884.0), s, origem, folga=int(2 * s) + 2)
    H, W = reg.shape[:2]
    x0, y0, x1, y1 = q["vidro"]
    e = q["borda"]
    af = V.cob([V.ret(x0, y0, x1, y1)], jan, s, origem)
    dentro = V.cob([V.ret(x0 + e, y0 + e, x1 - e, y1 - e)], jan, s, origem)
    piso = V.cob([V.ret(*q["piso"])], jan, s, origem)
    sb = cv2.GaussianBlur(af, (0, 0), max(0.6 * s, 0.5))
    Ms = np.float32([[1, 0, -0.6 * s], [0, 1, 0.8 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - af) * piso
    reg *= (1 - q["sombra"] * sb)[..., None]
    reg = V.compor(reg, dentro, np.float32(q["vidro_cor"]))
    reg = V.compor(reg, np.clip(af - dentro, 0, 1), np.float32(q["borda_cor"]))
    return _gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
# A área em volta da caracol no Bege Bahia da saleta (o mesmo tecido da varanda de 39 m² de `piso_servico`).
CARACOL_P = dict(caixa=(1908.0, 1492.0, 2052.0, 1636.0),
                 # só o trecho de cima à direita ("somente nessa área"): do guarda-corpo do raio de 90° à saleta, da
                 # porta de correr ao trecho de cima do guarda-corpo em L; o resto em volta da escada fica vão
                 zona=V.ret(1983.6, 1497.2, 2046.6, 1565.4), costura=(2044.4, 1497.0, 2049.6, 1566.0),
                 c=(1977.4, 1571.6), R=56.0, topo=1500.2, lum=150.0, sat=40.0, sombra_px=3.0, semente=27,
                 # o que fica: o guarda-corpo em L (o trecho de cima e o de baixo) e o do raio de 90° até a parede
                 fica=[(2040.6, 1565.4, 2046.3, 1631.6), (2031.0, 1565.4, 2046.3, 1570.2),
                       (1979.0, 1496.5, 1983.6, 1517.0)])


def caracol_piso(img, s, origem, q=CARACOL_P):
    jan, reg = _reg(img, q["caixa"], s, origem)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    r = np.hypot(xs[None, :] - q["c"][0], ys[:, None] - q["c"][1])
    L = reg.mean(2)
    sat = reg.max(2) - reg.min(2)
    fica = V.cob([V.ret(*f) for f in q["fica"]], jan, s, origem) > 0.05
    # tudo o que é área (o cinza, o anel claro em volta da escada, os restos), menos o que fica; junto à porta de
    # correr (no alto) só o que tem a cor do piso
    perto = np.broadcast_to(ys[:, None] < q["topo"], (H, W))
    piso = (V.cob([q["zona"]], jan, s, origem) > 0.5) & ~fica
    piso &= ~perto | ((L >= q["lum"]) & (sat <= q["sat"]))
    # a linha que separava a área da saleta: inteira
    piso |= (V.cob([V.ret(*q["costura"])], jan, s, origem) > 0.5) & ~fica
    # fora do círculo da escada (o contorno dela fica), com a borda suave
    borda = np.clip(r - q["R"] + 0.5, 0, 1) if s < 2 else np.clip((r - q["R"]) * s + 0.5, 0, 1)
    piso &= borda > 0
    ref = float(np.median(L[piso]))
    dist = cv2.distanceTransform(piso.astype(np.uint8), cv2.DIST_L2, 5) / max(s, 1e-3)
    luz = np.clip(cv2.GaussianBlur(L, (0, 0), max(0.5, 0.5 * s)) / ref, 0.6, 1.0)
    w = np.clip(1 - dist / q["sombra_px"], 0, 1)
    luz = 1 - w * (1 - luz)
    T = B.G._quilt(img, s, origem, B.SERVICO["fonte"], H, W, semente=q["semente"])
    # o tom do Bege Bahia da saleta de agora (a faixa logo à direita), para a área emendar sem degrau de cor
    sx0, sy0, sx1, sy1 = V.janela(img, (2052.0, 1505.0, 2100.0, 1560.0), s, origem, folga=0)
    sal = img[sy0:sy1, sx0:sx1].reshape(-1, 3).astype(np.float32)
    Ls = sal.mean(1)
    alvo = np.median(sal[(Ls > 150) & (Ls < 240)], axis=0)
    T = T * (alvo / np.maximum(np.median(T.reshape(-1, 3), axis=0), 1))[None, None, :]
    a = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), max(0.4, 0.35 * s)) * piso * borda
    reg = reg * (1 - a[..., None]) + (T * luz[..., None]) * a[..., None]
    return _gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
# A janela da floreira do banho master (ARQ_PAREDE do PDF): o vão de 1376,7 a 1387,5 x 1463,9 a 1631,1; as folhas de
# correr escalonadas (de dentro para fora) e os arremates de cima e de baixo.
JANELA = dict(caixa=(1372.0, 1458.0, 1392.0, 1636.0), vao=(1376.7, 1463.9, 1387.5, 1631.1),
              piso_luz=(1398.0, 1536.0, 1500.0, 1560.0), soleira=0.90,
              arremates=[(1378.5, 1463.9, 1387.5, 1466.3), (1378.5, 1628.7, 1387.5, 1631.1)],
              folhas=[(1384.5, 1466.3, 1387.5, 1523.6), (1381.5, 1518.8, 1384.5, 1576.2),
                      (1378.5, 1571.4, 1381.5, 1628.7)],
              vidro=(233, 236, 236), caixilho=(206, 207, 206), linha=(38, 38, 38), larg=0.22, face=(70, 72, 74))


def janela_floreira(img, s, origem, q=JANELA):
    jan, reg = _reg(img, q["caixa"], s, origem)
    # a soleira: o travertino do piso do banho um tom abaixo, com o veio
    TT = D.piso_tt(jan, s)
    px0, py0, px1, py1 = V.janela(img, q["piso_luz"], s, origem, folga=0)
    pl = img[py0:py1, px0:px1].reshape(-1, 3).astype(np.float32)
    TTl = D.piso_tt((px0, py0, px1, py1), s).reshape(-1, 3)
    k = np.median(pl, axis=0) / np.maximum(np.median(TTl, axis=0), 1)
    sol = TT * (k * q["soleira"])[None, None, :]
    a_v = V.cob([V.ret(*q["vao"])], jan, s, origem)
    reg = V.compor(reg, a_v, sol)
    # a face de fora (junto à floreira)
    x0, y0, x1, y1 = q["vao"]
    reg = V.compor(reg, V.cob([V.ret(x0, y0, x0 + 0.3, y1)], jan, s, origem) * 0.9, q["face"])
    e = q["larg"]

    def caixa_(r, cor, meio=False):
        nonlocal reg
        af = V.cob([V.ret(*r)], jan, s, origem)
        dentro = V.cob([V.ret(r[0] + e, r[1] + e, r[2] - e, r[3] - e)], jan, s, origem)
        reg = V.compor(reg, dentro, np.float32(cor))
        reg = V.compor(reg, np.clip(af - dentro, 0, 1), np.float32(q["linha"]))
        if meio:
            xm = (r[0] + r[2]) / 2
            reg = V.compor(reg, V.cob([V.ret(xm - e / 2, r[1] + e, xm + e / 2, r[3] - e)], jan, s, origem) * 0.8,
                           np.float32(q["linha"]))
    for r in q["arremates"]:
        caixa_(r, q["caixilho"])
    for r in q["folhas"]:
        caixa_(r, q["vidro"], meio=True)
    return _gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
# A banheira: o travertino refeito na pegada, a banheira oval da biblioteca no lugar e o misturador de piso do PDF.
BANHEIRA = dict(zona=(1393.0, 1467.2, 1514.0, 1532.0),
                luz=[(1392.0, 1532.0, 1516.0, 1546.0), (1514.0, 1468.0, 1530.0, 1540.0)],
                peca=("banho-master/banheira-oval-a", 1460.0, 1499.0, 96.0, 48.0, 0.0, "movel"),
                # o misturador (ARQ_LOUÇAS E METAIS): (x0, y0, x1, y1, raio do canto)
                corpo=(1400.3, 1494.3, 1403.3, 1505.0, 1.2), ducha=(1397.8, 1495.9, 1400.3, 1503.4, 1.0),
                alavancas=[(1403.3, 1495.9, 1405.7, 1498.9, 0.7), (1403.3, 1500.4, 1405.7, 1503.4, 0.7)],
                bica=(1401.0, 1498.9, 1419.0, 1500.4, 0.75), saida=(1417.6, 1499.65, 0.55),
                metal=(196.0, 199.0, 202.0), brilho=(238.0, 240.0, 242.0), sombra_metal=(128.0, 131.0, 135.0),
                contorno=(96.0, 98.0, 101.0), sombra=0.30)


def _arred(r, jan, s, origem, n=10):
    """O retângulo de cantos arredondados (x0, y0, x1, y1, raio) como polígono."""
    x0, y0, x1, y1, rr = r
    rr = min(rr, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for cx, cy, a0 in ((x1 - rr, y0 + rr, -90), (x1 - rr, y1 - rr, 0), (x0 + rr, y1 - rr, 90), (x0 + rr, y0 + rr, 180)):
        for t in np.linspace(a0, a0 + 90, n):
            pts.append((cx + rr * np.cos(np.radians(t)), cy + rr * np.sin(np.radians(t))))
    return V.cob([pts], jan, s, origem)


def _metal(reg, jan, s, origem, r, q, eixo):
    """Uma peça de metal escovado em planta: o tom, o brilho no eixo comprido, as bordas mais escuras, o contorno."""
    a = _arred(r, jan, s, origem)
    x0, y0, x1, y1, _ = r
    xs, ys = V.coords(jan, s, origem)
    if eixo == "x":                                 # comprida em x: o brilho numa faixa em y
        t = (ys[:, None] - (y0 + y1) / 2) / max((y1 - y0) / 2, 1e-3) + 0 * xs[None, :]
    else:
        t = (xs[None, :] - (x0 + x1) / 2) / max((x1 - x0) / 2, 1e-3) + 0 * ys[:, None]
    t = np.clip(np.abs(t + 0.25), 0, 1)               # a luz de cima à esquerda
    cor = (np.float32(q["brilho"]) * (1 - t[..., None]) ** 2 + np.float32(q["metal"]) * (1 - (1 - t[..., None]) ** 2))
    cor = cor * (1 - 0.35 * t[..., None] ** 3) + np.float32(q["sombra_metal"]) * 0.35 * t[..., None] ** 3
    reg = reg * (1 - a[..., None]) + cor * a[..., None]
    e = 0.2
    dentro = _arred((x0 + e, y0 + e, x1 - e, y1 - e, max(r[4] - e, 0.1)), jan, s, origem)
    return V.compor(reg, np.clip(a - dentro, 0, 1) * 0.85, q["contorno"]), a


def banheira(img, s, origem, q=BANHEIRA):
    img = D.refazer_piso(img, s, origem, [V.ret(*q["zona"])], ref_luz=[V.ret(*r) for r in q["luz"]], pena=1.2)
    jan, reg = _reg(img, (1388.0, 1462.0, 1520.0, 1538.0), s, origem, folga=int(4 * s) + 2)
    nome, cx, cy, w, h, ang, som = q["peca"]
    reg = B.pousar_peca(reg, jan, s, origem, nome, cx, cy, w, h, ang, som)
    # o misturador: a sombra curta de tudo, depois as peças (a ducha e o corpo, as alavancas, a bica por cima)
    partes = [(q["ducha"], "y"), (q["corpo"], "y")] + [(r, "x") for r in q["alavancas"]] + [(q["bica"], "x")]
    tudo = np.zeros(reg.shape[:2], np.float32)
    for r, _ in partes:
        tudo = np.maximum(tudo, _arred(r, jan, s, origem))
    H, W = tudo.shape
    sb = cv2.GaussianBlur(tudo, (0, 0), max(0.5 * s, 0.5))
    Ms = np.float32([[1, 0, 0.7 * s], [0, 1, 0.9 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - tudo)
    reg *= (1 - q["sombra"] * sb)[..., None]
    for r, eixo in partes:
        reg, _ = _metal(reg, jan, s, origem, r, q, eixo)
    # a saída da bica (o furo escuro na ponta)
    xo, yo, ro = q["saida"]
    furo = [(xo + ro * np.cos(t), yo + ro * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 24)]
    reg = V.compor(reg, V.cob([furo], jan, s, origem) * 0.8, (70, 72, 75))
    return _gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
ITENS = {"escada_u_transp": (2245.0, 905.0, 2420.0, 995.0), "vazio_a": (1870.0, 600.0, 2165.0, 900.0),
         "vazio_b": (2235.0, 335.0, 2615.0, 885.0), "caracol_piso": (1905.0, 1490.0, 2055.0, 1640.0),
         "janela_floreira": (1365.0, 1455.0, 1400.0, 1640.0), "banheira": (1385.0, 1460.0, 1525.0, 1540.0)}
FUNC = {"escada_u_transp": escada_u_transp, "vazio_a": vazio_a, "vazio_b": vazio_b, "caracol_piso": caracol_piso,
        "janela_floreira": janela_floreira, "banheira": banheira}


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def refazer_do_head(nome):
    """Refaz um item sobre o trecho do último commit (na final, na prancha e nos 12K), para trocar o que já foi aplicado."""
    c, pav = PLANTA.split("_")
    x0, y0, x1, y1 = ITENS[nome]
    rel = EP.PLANTAS[PLANTA][0]
    head = EP.git_img(rel, "HEAD")
    im = cv2.imread(str(EP.PROJ / rel))
    im[int(y0):int(y1), int(x0):int(x1)] = head[int(y0):int(y1), int(x0):int(x1)]
    im = item(im, nome)
    cv2.imwrite(str(EP.PROJ / rel), im)
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = im
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in os.environ.get("OPCOES", "AB"):
        r12 = f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(EP.PROJ / r12)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        h12 = EP.git_img(r12, "HEAD")
        mapa, cc = EP.registro_12k(head, cv2.cvtColor(h12, cv2.COLOR_BGR2GRAY), dz,
                                   (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
        A, B_ = mapa(x0, y0)
        ex_ = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
        ey_ = (mapa(x0, y0 + 1000.0)[1] - B_) / 1000.0
        sx = (ex_ * (x1 - x0) + ey_ * (y1 - y0)) / ((x1 - x0) + (y1 - y0))
        org = (x0 - A / sx, y0 - B_ / sx)
        X0, Y0, X1, Y1 = V.janela(im, (x0, y0, x1, y1), sx, org, folga=4)
        im[Y0:Y1, X0:X1] = h12[Y0:Y1, X0:X1]
        del h12
        im = item(im, nome, sx, org)
        print(f"   {op}: {nome} refeito sobre o HEAD (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(EP.PROJ / r12, quality=95, subsampling=0, dpi=dpi)
        del im


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
    if not os.environ.get("SO_12K"):
        for f in EP.PLANTAS[PLANTA]:
            im = cv2.imread(str(EP.PROJ / f))
            for nome in nomes:
                im = item(im, nome)
            cv2.imwrite(str(EP.PROJ / f), im)
            if f == EP.PLANTAS[PLANTA][0]:
                novo = im
        pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
        pr = cv2.imread(str(pf))
        pr[:2160] = novo
        cv2.imwrite(str(pf), pr)
    else:                                          # o registro contra a final de antes (a do último commit)
        base = EP.git_img(EP.PLANTAS[PLANTA][0], "HEAD")
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            x0, y0, x1, y1 = ITENS[nome]
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
            A, B_ = mapa(x0, y0)
            ex_ = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            ey_ = (mapa(x0, y0 + 1000.0)[1] - B_) / 1000.0
            sx = (ex_ * (x1 - x0) + ey_ * (y1 - y0)) / ((x1 - x0) + (y1 - y0))
            im = item(im, nome, sx, (x0 - A / sx, y0 - B_ / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--refazer":
        for n in sys.argv[2:]:
            refazer_do_head(n)
    else:
        main(sys.argv[1:] or None)

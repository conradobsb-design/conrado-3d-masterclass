"""Casa B Térreo, 2ª leva de 26/11 (os recortes do 12K B).

- **Armários do louceiro e da despensa** ("corrigir essas falhas brancas. manter o preenchimento dos armários e paredes
  corretamente"): no alto de cada armário (e da bancada da área de serviço), junto à parede, cada linha até a 1ª limpa
  na sua mediana (o chanfro fica, os pontinhos saem); a parede e as bordas do armário ficam. E o friso de baixo do
  armário baixo do louceiro e da despensa ("corrija essas falhas nos armarios do louceiro e despensa"), linha a linha.
- **Portões da área de serviço descoberta** ("corrigir essas falhas no piso e nos brises"): na faixa das três lâminas,
  o piso refeito (acima da divisa do PDF, 1678,1, o piso marrom de logo acima; abaixo, a pedra portuguesa de logo
  abaixo) e as lâminas de novo pelo PDF (ARQ_ELEMENTOS FIXOS), no grafite das paredes, com a sombra curta, sem o halo
  branco; o pontinho branco no alto da parede da direita sai.
- **Quarto de serviço, a janela de baixo** ("corrigir as folhas de vidro e o piso"): entre as paredes do PDF (1932,4 a
  2022,0), na espessura da parede (1666,1 a 1678,1), a soleira de pedra no travertino mais escuro e as duas folhas de
  correr do PDF no vidro claro, sem contorno; os postes cromados das pontas viram parede; a sombra e a borda da folha
  abaixo da parede saem (o piso de logo abaixo).
- **BH serviço, a janela de baixo** ("corrigir essa soleira. ela tem a espessura da parede"): a soleira só na espessura
  da parede (1666,1 a 1678,1, entre as paredes do PDF, 1850,6 a 1882,9), em pedra no travertino mais escuro, com o vidro
  do PDF por cima; o que passava da parede, em cima e embaixo, vira o piso de logo ao lado.
- **Piscina, a borda da esquerda** ("corrigir essa borda na piscina, junto ao contorno"): o friso claro e serrilhado
  entre o contorno escuro e a borda de travertino recebe a própria borda de logo à direita (os veios seguem na linha) e o
  contorno fica reto, coluna a coluna no perfil mediano dele.
- **Suíte master**: o piso das espreguiçadeiras refeito tábua a tábua ("corrigir o piso significa deixar as tábuas
  alinhadas e completas"), as fileiras alinhadas com as de baixo, e o tapete logo acima da sobra da coberta.
- **Suítes 1 e 3, o entorno da cama**: a moldura da base bege de ponta a ponta (sem o cinza translúcido nem o degradê).
- **Banquetas da bancada gourmet** ("vamos manter as banquetas sob a bancada"): a sombra do tampo nelas, junto à borda.

Final, prancha e 12K A e B (cada item pelo registro local).

  python3 terreo_casab_2611b.py [item ...]
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
import terreo_casaa_2511g as G       # noqa: E402
import um_pav_casaa_2511c as C       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import um_pav_casaa_2511e as E       # noqa: E402
import terreo_casab_2611 as T        # noqa: E402

PLANTA = "B_Terreo"
DZ = T.DZ
SOLEIRA = T.SOLEIRA


def copiar(img, s, origem, r, d, lados="", pena=1.0):
    return T.copiar(img, s, origem, r, d, lados, pena)


def cor_de(img, s, origem, r):
    jan, reg = C._reg(img, r, s, origem, folga=0)
    return tuple(float(v) for v in np.median(reg.reshape(-1, 3), axis=0))


def pintar(img, s, origem, rets, cor):
    return T.pintar(img, s, origem, rets, cor)


# ----------------------------------------------------------------------------------------------------------------------
# as colunas de cada peça (px da final, medidas na final: de moldura a moldura); as linhas medidas na imagem: do fim
# da parede de cima até a 1ª linha limpa do armário (o tom do miolo), cada linha na sua mediana
ARMARIOS = {"armario_louceiro": (1830.8, 1860.8), "armario_despensa": (2018.8, 2042.8),
            "bancada_servico": (2051.6, 2081.6)}
ARMARIO_Y = (1361.0, 1384.0)


def _armario(nome):
    def f(img, s, origem, cols=ARMARIOS[nome]):
        x0, x1 = cols
        y0, y1 = ARMARIO_Y
        jan, reg = C._reg(img, (x0, y0, x1, y1), s, origem, folga=0)
        xs, ys = V.coords(jan, s, origem)
        miolo = (xs >= x0 + 3.0) & (xs <= x1 - 2.0)
        Lm = reg[:, miolo].mean(2)
        prof = np.median(Lm, axis=1)
        iw = 0
        while iw < len(prof) - 1 and prof[iw + 1] < 120:
            iw += 1
        if prof[0] >= 120:
            return img
        lint = float(np.median(prof[(ys >= 1376.0) & (ys <= 1382.0)]))
        # limpa: a linha no tom do miolo e sem pontinhos (menos de 1% dos px fora do tom)
        limpa = [(abs(prof[i] - lint) < 6) and ((np.abs(Lm[i] - lint) > 14).mean() < 0.05) for i in range(len(prof))]
        ic = iw + 1
        while ic < len(prof) - 3 and not all(limpa[ic + k] for k in range(3)):
            ic += 1
        # da parede até a 1ª linha limpa: cada linha na sua mediana (o chanfro fica, os pontinhos saem)
        for i in range(iw + 1, ic):
            reg[i, miolo] = np.median(reg[i, miolo], axis=0).astype(reg.dtype)
        # nas molduras (fora do miolo) os pontinhos claros descem ao tom da própria coluna logo abaixo
        lado = (xs >= x0 + 1.5) & ~miolo
        if lado.any() and ic > iw + 1:
            ref = np.median(reg[ic:ic + 8][:, lado].astype(np.float32), axis=0)
            reg[iw + 1:ic, lado] = np.minimum(reg[iw + 1:ic][:, lado].astype(np.float32), ref[None] + 4.0).astype(reg.dtype)
        return C._gravar(img, jan, reg)
    return f


# a borda de cima do armário baixo (abaixo dos rótulos LOUCEIRO e DESPENSA): o friso (luz, tampo, sulco escuro) com
# manchas claras e pontinhos no 12K -> cada linha do friso na sua mediana, de canto a canto
FRISOS = {"friso_louceiro": (1861.0, 1933.3), "friso_despensa": (1941.4, 2020.6)}
FRISO_Y = (1465.0, 1472.5)


def _friso(nome):
    def f(img, s, origem, cols=FRISOS[nome]):
        x0, x1 = cols
        jan, reg = C._reg(img, (x0, FRISO_Y[0], x1, FRISO_Y[1]), s, origem, folga=0)
        xs, ys = V.coords(jan, s, origem)
        dentro = (xs >= x0) & (xs <= x1)
        sub = reg[:, dentro]
        L = sub.astype(np.float32).mean(2)
        prof = np.median(L, axis=1)
        plano = float(np.median(prof[ys >= 1470.3]))
        i0 = next((i for i in range(len(prof)) if prof[i] > 140), None)
        if i0 is None:
            return img
        isu = next((i for i in range(i0, len(prof)) if prof[i] < 125), None)
        if isu is None:
            return img

        def limpa(i):
            return abs(prof[i] - plano) < 5 and (np.abs(L[i] - plano) > 14).mean() < 0.05
        i1 = isu
        while i1 < len(prof) - 2 and not (limpa(i1 + 1) and limpa(i1 + 2)):
            i1 += 1
        for i in range(i0, i1 + 1):
            sub[i] = np.median(sub[i], axis=0).astype(reg.dtype)
        reg[:, dentro] = sub
        return C._gravar(img, jan, reg)
    return f


# ----------------------------------------------------------------------------------------------------------------------
PORTAO = dict(piso_cima=((2141.8, 1668.5, 2203.6, 1678.1), (0.0, -11.0), "ltr"),
              piso_baixo=((2141.8, 1678.1, 2203.6, 1689.5), (0.0, 12.0), "lrb"),
              laminas=[[(2143.8, 1675.3), (2159.7, 1684.2), (2161.1, 1681.6), (2145.2, 1672.7)],
                       [(2163.4, 1675.0), (2179.3, 1684.4), (2180.8, 1681.8), (2164.9, 1672.5)],
                       [(2184.2, 1683.8), (2186.3, 1685.9), (2199.0, 1673.2), (2196.8, 1671.1)]],
              cor=(78.0, 78.0, 80.0), sombra=0.30,
              ponto=(2203.9, 1665.4, 2208.6, 1669.2), ponto_cor=(2207.0, 1670.5, 2212.0, 1676.5))


def portao(img, s, origem, q=PORTAO):
    for k in ("piso_cima", "piso_baixo"):
        r, d, lados = q[k]
        img = copiar(img, s, origem, r, d, lados, pena=1.2)
    img = pintar(img, s, origem, [q["ponto"]], cor_de(img, s, origem, q["ponto_cor"]))
    jan, reg = C._reg(img, (2138.0, 1667.0, 2206.0, 1691.0), s, origem, folga=int(2 * s) + 2)
    H, W = reg.shape[:2]
    a = np.clip(sum(V.cob([p], jan, s, origem) for p in q["laminas"]), 0, 1)
    sb = cv2.GaussianBlur(a, (0, 0), max(0.7 * s, 0.6))
    Ms = np.float32([[1, 0, 0.6 * s], [0, 1, 0.8 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - a)
    reg = reg * (1 - q["sombra"] * sb)[..., None]
    reg = V.compor(reg, a, np.float32(q["cor"]))
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
JANELAS = {
    "janela_quarto_servico": dict(
        piso=[((1932.4, 1678.1, 2022.0, 1684.2), (0.0, 6.8), "lrb")],
        parede=[(1923.8, 1666.1, 1932.4, 1678.1), (2022.0, 1666.1, 2031.2, 1678.1)],
        parede_cor=(1906.0, 1668.5, 1916.0, 1675.5),
        soleira=(1932.4, 1666.1, 2022.0, 1678.1),
        folhas=[[(1934.8, 1672.1, 1979.6, 1675.1)], [(1974.8, 1675.1, 2019.6, 1678.1)]]),
    "janela_bh_servico": dict(
        piso=[((1845.5, 1661.0, 1888.0, 1666.1), (0.0, -6.0), "lrt"),
              ((1845.5, 1678.1, 1888.0, 1683.6), (0.0, 6.2), "lrb"),
              # a sombra rente à parede, embaixo, de volta sob os trechos de parede (a de logo ao lado)
              ((1843.6, 1678.1, 1850.6, 1681.2), (-9.0, 0.0), "lb"), ((1882.9, 1678.1, 1889.9, 1681.2), (9.0, 0.0), "rb")],
        parede=[(1843.6, 1666.1, 1850.6, 1678.1), (1882.9, 1666.1, 1889.9, 1678.1)],
        parede_cor=(1834.0, 1668.5, 1841.0, 1675.5),
        soleira=(1850.6, 1666.1, 1882.9, 1678.1),
        folhas=[[(1850.6, 1671.8, 1882.9, 1674.8)]]),
}


def _janela(nome):
    def f(img, s, origem, q=JANELAS[nome]):
        cor = cor_de(img, s, origem, q["parede_cor"])
        for r, d, lados in q["piso"]:
            img = copiar(img, s, origem, r, d, lados, pena=1.2)
        img = pintar(img, s, origem, q["parede"], cor)
        img = G.soleira_trav(img, s, origem, [q["soleira"]], q=SOLEIRA)
        return T.vidros(img, s, origem, T._caixa([q["soleira"]]), q["folhas"])
    return f


# ----------------------------------------------------------------------------------------------------------------------
BORDA = dict(caixa=(609.0, 1100.0, 625.0, 1370.0), contorno=(614.0, 616.98), friso=(616.3, 620.2), friso_d=4.2)


def borda_piscina(img, s, origem, q=BORDA):
    x0, y0, x1, y1 = q["caixa"]
    jan, reg = C._reg(img, q["caixa"], s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    L = reg.mean(2)
    prof = np.median(L, axis=0)
    c0, c1 = q["contorno"]
    # o contorno (a linha cinza e o filete escuro à direita, que falha em trechos): cada coluna na sua mediana; a grama
    # à esquerda fica com a textura dela
    idx = np.where((xs >= c0) & (xs <= c1))[0]
    if len(idx) == 0:
        return img
    i0, i1 = idx.min(), idx.max()
    perfil = np.median(reg[:, i0:i1 + 1], axis=0)
    # o friso: a borda de logo à direita
    f0, f1 = q["friso"]
    img = copiar(img, s, origem, (max(f0, xs[i1] + 0.5 / s), y0, f1, y1), (q["friso_d"], 0.0), "rtb", pena=1.0)
    jan, reg = C._reg(img, q["caixa"], s, origem, folga=0)
    reg[:, i0:i1 + 1] = perfil[None]
    return C._gravar(img, jan, reg)



# ----------------------------------------------------------------------------------------------------------------------
# Suíte master, o piso das espreguiçadeiras: "corrigir o piso significa deixar as tábuas alinhadas e completas". O piso
# de madeira entre a cortina, a parede, o armário e a fileira de baixo é refeito tábua a tábua: as fileiras no passo do
# piso (7 px da final; as divisas em 390, 396, ... 508, alinhadas com as de baixo, que ficam), cada tábua um trecho sem
# emenda das 4 fileiras limpas logo abaixo (515-543), cortado inteiro (70-135 px, a 1ª e a última cortadas pela borda),
# virado ou não, as emendas desencontradas das da fileira de cima. As peças ficam (espreguiçadeiras, mesinhas,
# poltrona; e a cortina e a parede pela cor), com a sombra curta delas no piso novo.
def _arred(x0, y0, x1, y1, rt, rb, n=6):
    pts = []
    for cx, cy, r, a0 in ((x1 - rt, y0 + rt, rt, -90), (x1 - rb, y1 - rb, rb, 0), (x0 + rb, y1 - rb, rb, 90),
                          (x0 + rt, y0 + rt, rt, 180)):
        for k in range(n + 1):
            a = np.deg2rad(a0 + 90.0 * k / n)
            pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return pts


PISO_MASTER = dict(
    zona=(975.0, 390.0, 1203.0, 508.0), passo=7.0, y_divisa=508.0,
    fontes=[(515.0, [(983.0, 1080.0), (1082.0, 1238.0)]), (522.0, [(983.0, 1158.0), (1160.0, 1238.0)]),
            (529.0, [(983.0, 1116.0), (1118.0, 1202.0)]), (536.0, [(983.0, 1039.0), (1041.0, 1238.0)])],
    tabua=(70.0, 135.0), desencontro=18.0,
    pecas=[_arred(1041.0, 409.0, 1084.0, 500.0, 7.0, 1.5), _arred(1107.0, 409.0, 1150.0, 500.0, 7.0, 1.5),
           V.ret(1023.6, 445.6, 1059.4, 469.2), V.ret(1130.6, 448.5, 1167.3, 473.3),
           V.ret(1169.4, 461.0, 1203.0, 488.3), V.ret(1183.0, 458.2, 1203.0, 492.6)],
    sombra=0.22, semente=11)


def piso_master(img, s, origem, q=PISO_MASTER):
    rng = np.random.default_rng(q["semente"])
    zx0, zy0, zx1, zy1 = q["zona"]
    jan = V.janela(img, (zx0, zy0 - 2.0, 1240.0, 545.0), s, origem, folga=int(3 * s) + 2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]

    def cx(x):                                       # coluna/linha da janela para uma coordenada da final
        return int(round((x - origem[0]) * s)) - X0

    def cy(y):
        return int(round((y - origem[1]) * s)) - Y0

    m = 1 if s > 1.5 else 0                          # no 12K a divisa é macia: a tira sem a meia-tinta
    tiras = []
    for ya, runs in q["fontes"]:
        a, b = cy(ya) + m, cy(ya + q["passo"]) - m
        for xa, xb in runs:
            tiras.append((a, b, cx(xa) + m, cx(xb) - m))
    novo = reg.copy()                                # fora das fileiras novas, o que já está (para o desfoque das divisas)
    juntas = np.zeros((H, W), np.float32)
    divisas = np.zeros((H, W), np.float32)
    ant = []
    y = zy0 - 1.0                                    # a 1ª fileira [389, 396); a linha 389 (sombra da parede) fica
    while y < zy1 - 0.5:
        ta, tb = max(cy(y), 0), cy(y + q["passo"])
        hh = tb - ta
        pos = zx0 - rng.uniform(0.0, q["tabua"][1] * 0.8)
        cortes = []
        ultimo = None
        xcur = cx(zx0)
        while pos < zx1:
            for _ in range(40):
                L = rng.uniform(*q["tabua"])
                fim = pos + L
                if all(abs(fim - j) >= q["desencontro"] for j in ant) or fim >= zx1:
                    break
            fim = min(pos + L, zx1)
            px0, px1 = max(cx(max(pos, zx0)), 0), min(cx(fim), W)
            w = px1 - px0
            if w <= 0:
                pos = fim
                continue
            for _ in range(60):
                i = int(rng.integers(len(tiras)))
                a, b, c0, c1 = tiras[i]
                if c1 - c0 >= w + 2 and i != ultimo:
                    break
            else:
                raise ValueError(f"tábua de {w} px sem fonte")
            off = int(rng.integers(c0, c1 - w + 1))
            peca = reg[a:b, off:off + w]
            if rng.random() < 0.5:
                peca = peca[:, ::-1]
            peca = cv2.resize(peca, (w, hh), interpolation=cv2.INTER_LINEAR) if peca.shape[0] != hh else peca
            novo[ta:tb, px0:px1] = peca
            if fim < zx1:
                cortes.append(fim)
                juntas[ta:tb, max(px1 - 1, 0):min(px1 + 1, W)] = 1.0
            ultimo = i
            pos = fim
        divisas[max(tb - 1, 0):min(tb + 1, H)] = 1.0
        ant = cortes
        y += q["passo"]
    if s > 1.5:                                       # a emenda e a divisa macias como no 12K
        k = 0.35 * s
        vb = cv2.GaussianBlur(novo, (0, 0), sigmaX=0.01, sigmaY=k)
        hb = cv2.GaussianBlur(novo, (0, 0), sigmaX=k, sigmaY=0.01)
        wd = cv2.GaussianBlur(divisas, (0, 0), 0.6 * s)[..., None]
        wj = cv2.GaussianBlur(juntas, (0, 0), 0.6 * s)[..., None]
        wd = np.clip(wd / max(wd.max(), 1e-6), 0, 1)
        wj = np.clip(wj / max(wj.max(), 1e-6), 0, 1)
        novo = novo * (1 - wd) + vb * wd
        novo = novo * (1 - wj) + hb * wj
    # o que fica: as peças (geometria, 0,6 px de folga) e, junto à cortina, à parede e ao armário, o que não é madeira
    # (pouca saturação); no meio do piso os riscos cinzas soltos saem
    pecas = V.cob(q["pecas"], jan, s, origem)
    hsv = cv2.cvtColor(np.clip(reg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    xs, ys = V.coords(jan, s, origem)
    beira = (xs[None, :] < 990.0) | (ys[:, None] < 391.0) | (xs[None, :] > 1201.0)
    nao_mad = ((hsv[..., 1] < 60) & beira).astype(np.float32)
    kd = max(3, int(round(0.6 * s)) * 2 + 1)
    fica = np.maximum(pecas, np.clip(cv2.dilate(nao_mad, np.ones((kd, kd), np.uint8)), 0, 1))
    fica = np.maximum(fica, cv2.GaussianBlur(fica, (0, 0), 0.3 * s))
    # a sombra curta das peças no piso novo (a luz vem de cima à direita)
    M = np.float32([[1, 0, -0.9 * s], [0, 1, 0.8 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(pecas, M, (W, H)), (0, 0), 0.9 * s) * (1 - pecas)
    novo *= (1 - q["sombra"] * sb)[..., None]
    zona = V.cob([V.ret(zx0, zy0 - 1.0, zx1, zy1)], jan, s, origem)
    # o tom: a mediana do piso velho da zona (fora das peças) no novo
    livre = (zona > 0.99) & (fica < 0.01)
    g = float(np.median(reg[livre].mean(1)) / max(np.median(novo[livre].mean(1)), 1.0))
    novo *= float(np.clip(g, 0.96, 1.04))
    a = (zona * (1 - fica))[..., None]
    reg = reg * (1 - a) + novo * a
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img



# Suíte master, o tapete logo acima da sobra da coberta (do lado esquerdo da cama): um retalho claro, mais largo que a
# sombra da cama, entre o tapete e a sobra -> o tapete e a sombra da cama de logo acima, descidos
TAPETE_MASTER = dict(ret=(1046.5, 704.0, 1051.5, 711.8), d=(0.0, -7.5))


def tapete_master(img, s, origem, q=TAPETE_MASTER):
    return copiar(img, s, origem, q["ret"], q["d"], "ltr", pena=1.0)



# Suíte 1, o entorno da cama (cabeceira à esquerda): a moldura da base era de dois materiais, bege junto à cabeceira e
# cinza translúcido (o tapete aparecendo) do meio da cama até o pé, com um degrau onde um vira o outro, em cima e em
# baixo -> a moldura bege de ponta a ponta: em cada linha da faixa, a mediana do trecho bege junto à cabeceira; no pé,
# a mesma moldura de cima a baixo. O edredom e a manta (pela cor) ficam por cima.
CAMA_S1 = dict(fonte_x=(1958.0, 1981.0), x=(1983.0, 2065.3),
               faixas=[(382.25, 385.0, 384.35), (499.0, 501.8, None)], pe=(2062.8, 2065.3, 382.25, 501.8))


def cama_suite1(img, s, origem, q=CAMA_S1):
    jan, reg = C._reg(img, (1950.0, 378.0, 2070.0, 506.0), s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    regf = reg.astype(np.float32)
    hsv = cv2.cvtColor(reg, cv2.COLOR_BGR2HSV).astype(np.float32)
    Lr = regf.mean(2)
    fica = ((Lr > 205) & (hsv[..., 1] < 50)) | ((regf[..., 2] - regf[..., 1] > 35) & (regf[..., 2] > 90))
    fx = (xs >= q["fonte_x"][0]) & (xs <= q["fonte_x"][1])
    tx = (xs >= q["x"][0]) & (xs < q["x"][1])
    bege = None
    for y0, y1, ysomb in q["faixas"]:
        linhas = np.where((ys >= y0) & (ys < y1))[0]
        for i in linhas:
            cor = np.median(regf[i, fx], axis=0)
            if ysomb is not None and ys[i] >= ysomb:          # sobre o edredom, a sombra curta da moldura
                cor = np.median(regf[linhas[0]:linhas[0] + max(1, int(round(1.5 * s))), fx].reshape(-1, 3), axis=0) * 0.80
            elif ysomb is not None and bege is None:
                bege = np.median(regf[linhas[0]:linhas[0] + max(1, int(round(2.0 * s))), fx].reshape(-1, 3), axis=0)
            regf[i, tx] = cor                                  # a faixa toda (o edredom e a manta começam depois)
    px0, px1, py0, py1 = q["pe"]
    mx = (xs >= px0) & (xs < px1)
    for i in np.where((ys >= py0) & (ys < py1))[0]:
        m = mx & ~fica[i]
        regf[i, m] = bege
    reg[:] = np.clip(np.round(regf), 0, 255).astype(np.uint8)
    return C._gravar(img, jan, reg)



# Suíte 3, o entorno da cama (cabeceira embaixo, contra a parede): as laterais da moldura eram bege só junto à
# cabeceira; ao longo do colchão, cinza-rosado, escurecendo num degradê logo antes da cabeceira (a sombra velha dos
# travesseiros), e o pé num terceiro tom -> as duas laterais e o pé na bege das laterais da cabeceira.
CAMA_S3 = dict(fonte_y=(796.5, 812.0), esq=(2460.3, 2463.3), dir=(2577.3, 2580.0), y=(712.4, 795.0),
               topo=(710.9, 712.4), fontes_x=[(2460.4, 2462.1), (2577.5, 2579.6)])


def cama_suite3(img, s, origem, q=CAMA_S3):
    jan, reg = C._reg(img, (2455.0, 706.0, 2585.0, 815.0), s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    regf = reg.astype(np.float32)
    fy = (ys >= q["fonte_y"][0]) & (ys <= q["fonte_y"][1])
    cores = [np.median(regf[fy][:, (xs >= a) & (xs <= b)].reshape(-1, 3), axis=0) for a, b in q["fontes_x"]]
    cor = (cores[0] + cores[1]) / 2.0
    ly = (ys >= q["y"][0]) & (ys < q["y"][1])
    for a, b in (q["esq"], q["dir"]):
        mx = (xs >= a) & (xs < b)
        regf[np.ix_(ly, mx)] = cor
    borda = (xs >= q["esq"][1] - 0.5) & (xs < q["esq"][1])       # a beira de dentro da lateral esquerda, um pouco mais escura
    regf[np.ix_(ly, borda)] = cor * 0.9
    ty = (ys >= q["topo"][0]) & (ys < q["topo"][1])
    tx = (xs >= q["esq"][0]) & (xs < q["dir"][1])
    regf[np.ix_(ty, tx)] = cor
    reg[:] = np.clip(np.round(regf), 0, 255).astype(np.uint8)
    return C._gravar(img, jan, reg)



# As banquetas da bancada gourmet ("vamos manter as banquetas sob a bancada"): já cortadas na borda (cerca de 40% sob o
# tampo), mas sem a sombra do tampo pareciam encostadas na frente -> a sombra do tampo na parte de fora, junto à borda,
# como na Casa A (`terreo_casaa_2511d.gourmet`: 0,32, caindo em 1,6 px), só na madeira e na palha (não no piso claro).
BANQUETAS = dict(caixa=(1290.0, 1292.0, 1560.0, 1319.3), sombra=0.32, queda=1.6)


def banquetas(img, s, origem, q=BANQUETAS):
    jan, reg = C._reg(img, q["caixa"], s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    regf = reg.astype(np.float32)
    d = np.clip(q["caixa"][3] - ys, 0, None)
    som = q["sombra"] * np.exp(-d / q["queda"])
    Lb = regf.mean(2)
    # a madeira e a palha (bem mais saturadas que o travertino, que aqui chega a R-B 35)
    cadeira = ((regf[..., 2] - regf[..., 0] > 55) | (Lb < 120)).astype(np.float32)
    cadeira = cv2.GaussianBlur(cadeira, (0, 0), 0.4 * s)
    regf *= (1 - som[:, None] * cadeira)[..., None]
    reg[:] = np.clip(np.round(regf), 0, 255).astype(np.uint8)
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
FUNC = {"portao": portao, "borda_piscina": borda_piscina, "piso_master": piso_master, "tapete_master": tapete_master,
        "cama_suite1": cama_suite1, "cama_suite3": cama_suite3, "banquetas": banquetas}
ITENS = {"portao": (2128.0, 1655.0, 2218.0, 1702.0), "borda_piscina": (600.0, 1090.0, 640.0, 1380.0),
         "piso_master": (975.0, 385.0, 1240.0, 545.0), "tapete_master": (1020.0, 680.0, 1080.0, 740.0),
         "cama_suite1": (1925.0, 345.0, 2140.0, 545.0), "cama_suite3": (2420.0, 670.0, 2660.0, 850.0),
         "banquetas": (1280.0, 1285.0, 1570.0, 1345.0)}
for n in ARMARIOS:
    FUNC[n] = _armario(n)
    ITENS[n] = T._caixa([(ARMARIOS[n][0], ARMARIO_Y[0], ARMARIOS[n][1], ARMARIO_Y[1])], 14.0)
for n in FRISOS:
    FUNC[n] = _friso(n)
    ITENS[n] = T._caixa([(FRISOS[n][0], FRISO_Y[0], FRISOS[n][1], FRISO_Y[1])], 14.0)
for n in JANELAS:
    FUNC[n] = _janela(n)
    ITENS[n] = T._caixa([JANELAS[n]["soleira"]], 16.0)


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
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
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            sx, org, cc = DD._registro(base, cinza, DZ, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

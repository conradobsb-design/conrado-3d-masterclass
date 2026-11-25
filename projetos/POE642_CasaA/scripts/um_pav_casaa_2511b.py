"""Casa A 1º Pavimento, 2ª leva de 25/11 (pedidos do usuário com os recortes do 12K B).

- **Cortinas** ("atualize as cortinas conforme estamos usando"): a C4 das Casas B a E nos 4 trilhos do PDF (Suíte
  Master, Suítes 2 e 3 e a do banho), pela própria `cortinas_padrao_casad_1611.aplicar` (o linho em ondas a 0,82, o
  trilho grafite do lado do vidro, 0,22 m de pano, até a ponta da parede e 0,15 m além); o pano de antes sai (o piso
  logo de dentro, em espelho, fora das paredes do PDF). Na final a própria função; ela anota limpezas e pousos e o 12K
  repete as mesmas contas na escala dele. A poltrona da suíte que encosta no vão fica por cima da cortina.
- **Escada em U** ("melhorar o aspecto desses degraus"): a mesma escada do Térreo (`terreo_casaa_2511d.ESCADA`),
  vista de cima: o lance que chega (com o DESCE), o patamar e o começo do lance de baixo, à direita da linha de corte,
  na pedra dos degraus do Térreo, com o veio ao comprido, o bocel fino, a sombra curta e o patamar numa pedra só; os
  guarda-corpos de vidro e a linha de corte finos; o vão à esquerda do corte como está; os rótulos por cima.
- **Caracol** ("restante dos degraus na transparência"): a volta que faltava (de 93,55° a 1°, hoje branca) com os
  degraus no tom dos degraus a 58% (como os de cima no Térreo, opção 1), os raios do PDF cheios até o corte (93,55°,
  111,33°, 129,08°) e tracejados depois; o contorno, o pilar, o guarda-corpo e o D por cima.
- **Piso do Quarto de Serviço, da Saleta e do B. Serviço** ("definir o piso a ser utilizado aqui nessas áreas"): o
  Bege Bahia das varandas (image quilting do trecho da varanda de 39 m²), na máscara de cor do piso de cada ambiente
  (fora a cama, o criado, as folhas, o armário, a caracol, a porta de correr, o vidro do box, a bancada e a folha da
  porta; o vaso, o chuveiro e o puxador saem pela cor), com a sombra rente às peças, os pontinhos claros do piso
  antigo dentro e os rótulos de volta (as paredes não entram como letra).
- **Sala íntima** ("vamos alterar o tom do tapete para não se confundir com o piso. e aproveita e corrigi o encosto do
  sofá que está quebrado e perdido com o piso"): o travertino refeito na pegada do tapete, do sofá, das mesinhas e da
  poltrona (a luz medida no piso em volta) e as peças de novo, na pose da instalação (`biblioteca_1pav_casaa_1211`):
  o tapete no taupe da opção A (`terreo_casaa_1011.TAPETES_1111`, o tom já escolhido para os tapetes que não se
  confundem com o piso), o sofá em L inteiro com a sombra de volume (o encosto da direita volta contínuo e se lê sobre o
  travertino), as mesinhas, a poltrona e a mesa de centro de nogueira (o tampo da própria imagem).
- **Bancada da cuba de entrada** ("vamos corrigir o material da bancada e definir os seus limites"): o tampo no
  travertino da bancada (1912,6 a 1990,2 x 1287,8 a 1323,6), um pouco mais escuro que o piso, com o contorno fino, o
  rodabanca e a sombra curta; a cuba redonda e a torneira da biblioteca por cima.

Final, prancha e 12K A e B.

  python3 um_pav_casaa_2511b.py [item ...]
"""
import contextlib
import io
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
import proposta_caracol_terreo_casaa_2511 as PC   # noqa: E402

PLANTA = "A_1Pavimento"
PX_M_ = 59.70590031258779


def _bib():
    with contextlib.redirect_stdout(io.StringIO()):
        import biblioteca_1pav_casaa_1211 as P1
        import biblioteca_terreo_casaa_1211 as BT
    return P1, BT


def pousar_peca(reg, jan, s, origem, nome, cx, cy, w, h, ang, sombra, extra=None, P=None):
    P1, BT = _bib()
    X0, Y0 = jan[0], jan[1]
    if P is None:
        P, w, h = P1.preparar(nome, w, h, extra)
    BT.pousar(reg, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, w * s, h * s, ang, BT.SOMBRAS[sombra],
              PX_M_ * s)
    return reg


# ----------------------------------------------------------------------------------------------------------------------
TAUPE = (128.0, 145.0, 160.0)                      # BGR, `terreo_casaa_1011.TAPETES_1111["opcoes"]["A"]`
SALA = dict(
    zona=(2026.0, 944.0, 2184.0, 1238.0),
    # onde medir a luz do travertino: as faixas de piso livre em volta
    ref_luz=[(2010.0, 950.0, 2026.0, 1236.0), (2184.0, 950.0, 2200.0, 1236.0), (2030.0, 1238.0, 2180.0, 1252.0)],
    mesa=(2054.4, 1042.6, 2094.0, 1120.0),
    pecas=[("sala-intima/tapete", 2096.0, 1099.0, 262.0, 120.0, 90.0, "tapete", ("tom",) + TAUPE),
           ("sala-intima/sofa-l-a", 2115.5, 1054.5, 119.0, 209.0, 0.0, "movel", "anti_t"),
           ("mesa", None, None, None, None, None, "mesa", None),
           ("sala-intima/mesa-lateral", 2044.0, 992.0, 18.0, None, 0.0, "baixa", None),
           ("sala-intima/mesa-lateral", 2100.0, 1140.0, 18.0, None, 0.0, "baixa", None),
           ("sala-intima/mesa-lateral", 2140.5, 1188.5, 27.0, None, 0.0, "baixa", None),
           ("sala-intima/poltrona-a", 2089.0, 1192.5, 54.0, 56.0, -150.0, "movel", None)])


def sala_intima(img, s, origem, q=SALA):
    # o tampo da mesa de centro (o da imagem, já nítido) antes de refazer o piso
    x0, y0, x1, y1 = q["mesa"]
    X0, Y0, X1, Y1 = V.janela(img, (x0 + 0.6, y0 + 0.6, x1 - 0.6, y1 - 0.6), s, origem, folga=0)
    tampo = img[Y0:Y1, X0:X1].astype(np.float32)
    Pm = np.dstack([tampo, np.full(tampo.shape[:2], 255.0, np.float32)])
    z = q["zona"]
    zona = [V.ret(*z)]
    img = D.refazer_piso(img, s, origem, zona, ref_luz=[V.ret(*r) for r in q["ref_luz"]], letras=True, pena=2.0)
    jan = V.janela(img, z, s, origem, folga=int(4 * s) + 2)
    J0, K0, J1, K1 = jan
    reg = img[K0:K1, J0:J1].astype(np.float32)
    for nome, cx, cy, w, h, ang, som, extra in q["pecas"]:
        if nome == "mesa":
            reg = pousar_peca(reg, jan, s, origem, None, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, som,
                              P=Pm)
        else:
            reg = pousar_peca(reg, jan, s, origem, nome, cx, cy, w, h, ang, som, extra)
    img[K0:K1, J0:J1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# A bancada da cuba de entrada ("vamos corrigir o material da bancada e definir os seus limites"): o tampo do PDF
# (ARQ_BANCADAS, 1912,6 a 1990,2 x 1287,8 a 1323,6, junto às paredes da esquerda e de baixo) no travertino das bancadas
# dos banhos (o do piso a 84%, o veio no comprido), com o contorno fino um tom abaixo, a faixa da rodabanca junto à
# parede e a sombra curta no piso dos lados livres (em cima e à direita); por cima, a cuba de apoio redonda e a torneira
# da biblioteca (`banho-master/cuba-entrada`: só a louça e o metal), no círculo do PDF, com a torneira do lado da
# parede.
BANCADA = dict(ret=(1912.6, 1287.8, 1990.2, 1323.6), rodabanca=(1912.6, 1322.4, 1990.2, 1323.6),
               escurecer=0.84, contorno=0.70, larg=0.25, rodabanca_tom=0.62,
               sombra=0.22, sombra_d=(0.6, -0.6), sombra_sig=0.9,
               cuba_c=(1931.65, 1305.65), cuba_d=20.3)
_CUBA = {}


def _cuba_entrada():
    """A louça e a torneira da `cuba-entrada` (o branco ligado à bacia, os furos fechados), a bacia (centro, diâmetro)
    em px do PNG."""
    if "P" not in _CUBA:
        P1, _ = _bib()
        P = cv2.imread(str(P1.BIB / "banho-master/cuba-entrada.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)
        B_, R_, A_ = P[..., 0], P[..., 2], P[..., 3]
        branco = ((A_ > 200) & ((R_ - B_) < 14)).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(branco, 8)
        k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        m = (lab == k).astype(np.uint8)
        cont, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cheio = np.zeros_like(m)
        cv2.drawContours(cheio, cont, -1, 1, -1)
        x, y, w, h = cv2.boundingRect(cheio)
        Q = P[y:y + h, x:x + w].copy()
        alfa = cv2.GaussianBlur(cheio[y:y + h, x:x + w].astype(np.float32), (0, 0), 0.8)
        Q[..., 3] = np.minimum(Q[..., 3], alfa * 255)
        # a bacia: a parte larga (a linha mais larga da máscara), o diâmetro e o centro
        larg = cheio[y:y + h, x:x + w].sum(axis=1)
        diam = float(larg.max())
        yb = h - 1 - int(np.argmax(larg[::-1] > 0))            # o fundo da bacia
        _CUBA["P"], _CUBA["diam"], _CUBA["cy"] = np.ascontiguousarray(Q), diam, yb - diam / 2
    return _CUBA["P"], _CUBA["diam"], _CUBA["cy"]


def bancada_entrada(img, s, origem, q=BANCADA):
    P1, BT = _bib()
    r = q["ret"]
    jan = V.janela(img, (r[0] - 4, r[1] - 4, r[2] + 4, r[3] + 4), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    a = V.cob([V.ret(*r)], jan, s, origem)
    # a sombra no piso dos lados livres
    dx, dy = q["sombra_d"]
    sh = V.cob([V.ret(r[0] + dx, r[1] + dy, r[2] + dx, r[3] + dy)], jan, s, origem)
    sh = cv2.GaussianBlur(sh, (0, 0), max(0.6, q["sombra_sig"] * s)) * (1 - a)
    reg *= (1 - q["sombra"] * sh)[..., None]
    # o tampo de travertino, o contorno e a rodabanca
    pedra = D.piso_tt(jan, s, giro=False) * q["escurecer"]
    e = q["larg"]
    d = V.cob([V.ret(r[0] + e, r[1] + e, r[2] - e, r[3] - e)], jan, s, origem)
    reg = V.compor(reg, a, pedra)
    reg = V.compor(reg, np.clip(a - d, 0, 1), pedra * q["contorno"])
    reg = V.compor(reg, V.cob([V.ret(*q["rodabanca"])], jan, s, origem), pedra * q["rodabanca_tom"])
    # a cuba e a torneira (girada: a torneira para a parede de baixo)
    P, diam, cyb = _cuba_entrada()
    k = q["cuba_d"] / diam
    h, w = P.shape[:2]
    off = (cyb - h / 2) * k                                   # o centro da bacia abaixo do centro do PNG
    cx, cy = q["cuba_c"][0], q["cuba_c"][1] + off              # girada 180°: o centro da peça abaixo da bacia
    BT.pousar(reg, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, w * k * s, h * k * s, 180.0,
              BT.SOMBRAS["baixa"], PX_M_ * s)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# O piso do quarto de serviço, da saleta e do B. serviço ("definir o piso a ser utilizado aqui nessas áreas"): no PDF as
# três têm o preenchimento das varandas (o Bege Bahia, `README`: "Bege Bahia (quarto de serviço, saleta, B. serviço)"),
# mas saíam num bege rosado e manchado, sem leitura de material. O Bege Bahia das varandas do próprio 1º Pavimento (a
# trama da varanda de 39 m², por image quilting, no tom dela), em todo o piso livre dos três ambientes, até a borda das
# peças (a cama, o criado, o armário, a caracol e o vão em L em volta dela, as portas e soleiras, o box, o vaso e a
# bancada ficam); as sombras rentes às peças e às paredes ficam (a luz de antes só a 4 px delas); as manchas saem; os
# rótulos voltam por cima.
SERVICO = dict(
    zonas=[(1912.6, 1332.5, 2118.0, 1487.8), (2052.9, 1487.8, 2112.6, 1496.7), (2046.0, 1496.7, 2163.3, 1631.1),
           (2163.3, 1437.0, 2246.9, 1571.4)],
    fora=[(1913.0, 1333.0, 1975.0, 1454.0), (1975.0, 1333.0, 2013.0, 1362.0),          # a cama e o criado
          (2106.0, 1331.0, 2110.8, 1388.0), (2106.0, 1433.5, 2110.8, 1488.5),         # as folhas
          (2117.6, 1332.5, 2156.0, 1488.0),                                           # o armário
          (1912.0, 1496.7, 2046.5, 1632.0),                                           # a caracol e o vão em L
          (1970.0, 1486.0, 2035.0, 1498.0),                                           # a porta de correr da saleta
          (2163.3, 1480.5, 2247.0, 1486.0),                                           # o vidro do box
          (2221.5, 1528.0, 2247.0, 1572.0),                                           # a bancada
          (2162.0, 1557.5, 2207.0, 1565.0)],                                          # a folha da porta
    # o vaso, o chuveiro e o puxador saem pela cor (brancos e cinzas, sem o bege)
    fonte=(2600.0, 1420.0, 2720.0, 1580.0),                                           # a varanda de 39 m²
    rb=(10.0, 42.0), lum=(150.0, 246.0), sombra_px=4.0, semente=25)


def piso_servico(img, s, origem, q=SERVICO):
    zs = q["zonas"]
    x0, y0 = min(r[0] for r in zs), min(r[1] for r in zs)
    x1, y1 = max(r[2] for r in zs), max(r[3] for r in zs)
    jan = V.janela(img, (x0, y0, x1, y1), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    zona = V.cob([V.ret(*r) for r in zs], jan, s, origem) > 0.5
    fora = V.cob([V.ret(*r) for r in q["fora"]], jan, s, origem) > 0.02
    L = reg.mean(2)
    rb = reg[..., 2] - reg[..., 0]
    cor = (rb >= q["rb"][0]) & (rb <= q["rb"][1]) & (L >= q["lum"][0]) & (L <= q["lum"][1])
    piso = zona & ~fora & cor
    # os furinhos do piso (o grão, as manchas) fechados; os pedaços soltos fora
    k = max(1, int(round(0.6 * s)))
    piso = cv2.morphologyEx(piso.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((2 * k + 1,) * 2, np.uint8)).astype(bool)
    piso &= zona & ~fora
    n, lab, st, _ = cv2.connectedComponentsWithStats(piso.astype(np.uint8), 8)
    grandes = np.zeros(n, bool)
    grandes[1:] = st[1:, cv2.CC_STAT_AREA] > 40 * s * s
    piso = grandes[lab]
    # os pontinhos claros do piso antigo (fora da faixa de cor) entram no piso novo
    livre = zona & ~fora
    n, lab, st, _ = cv2.connectedComponentsWithStats((livre & ~piso).astype(np.uint8), 8)
    furo = np.zeros(n, bool)
    furo[1:] = st[1:, cv2.CC_STAT_AREA] < 4 * s * s
    claro = np.zeros(n, bool)
    if n > 1:
        claro[1:] = np.bincount(lab.ravel(), weights=L.ravel(), minlength=n)[1:] / np.maximum(st[1:, cv2.CC_STAT_AREA], 1) > 200
    piso |= (furo & claro)[lab]
    # a luz: 1 longe das peças; perto delas (a sombra rente), a de antes sobre o piso livre de longe
    ref = float(np.median(L[piso]))
    dist = cv2.distanceTransform(piso.astype(np.uint8), cv2.DIST_L2, 5) / max(s, 1e-3)
    luz = np.clip(cv2.GaussianBlur(L, (0, 0), max(0.5, 0.5 * s)) / ref, 0.5, 1.0)
    w = np.clip(1 - dist / q["sombra_px"], 0, 1)
    luz = 1 - w * (1 - luz)
    T = G._quilt(img, s, origem, q["fonte"], H, W, semente=q["semente"])
    novo = T * luz[..., None]
    a = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), max(0.4, 0.35 * s)) * piso
    out = reg * (1 - a[..., None]) + novo * a[..., None]
    # os rótulos de volta
    # (as paredes, pedaços escuros grandes, não são letras)
    esc = ((ref - L) > 80.0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(esc, 8)
    big = np.zeros(n, bool)
    big[1:] = st[1:, cv2.CC_STAT_AREA] > 150 * s * s
    r = max(1, int(round(1.0 * s)))
    parede = cv2.dilate(big[lab].astype(np.uint8), np.ones((2 * r + 1,) * 2, np.uint8)) > 0
    at, corl = V.letras(reg, zona & ~fora & ~parede, escala=s, ref=ref, dif=80.0, piso_dif=30.0, area_min=0.8)
    out = V.compor(out, at, corl)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# A caracol da saleta ("restante dos degraus na transparência"): a mesma escada do Térreo (o centro, o raio e os
# degraus de 17,85° do PDF). Os degraus que chegam a este nível (de 1° a 93,55°) ficam como estão; o resto da volta,
# hoje branco, ganha os degraus no tom dos degraus a 58% (como os de cima no Térreo, opção 1), com os raios do PDF:
# cheios até o corte (93,55°, 111,33° e 129,08°), tracejados depois (de 147,27° a 341,51°). As linhas escuras (o
# contorno, o pilar, o guarda-corpo, o D) ficam por cima.
CARACOL = dict(janela=(1918.0, 1512.0, 2037.0, 1632.0), ini=93.55, fim=360.9, opac=0.58,
               cheios=(93.55, 111.33, 129.08),
               tracejados=(147.27, 164.68, 182.33, 199.68, 217.24, 234.79, 252.39, 270.06, 287.8, 305.63, 323.54,
                           341.51),
               amostra=dict(r=(14.0, 46.0), t=(10.0, 68.0)), linha_esc=0.80)


def caracol(img, s, origem, q=CARACOL):
    G_ = PC.G
    jan = V.janela(img, q["janela"], s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    L = reg.mean(2)
    # o tom dos degraus que já estão (no miolo de cada um, longe dos raios)
    xs, ys = V.coords(jan, s, origem)
    dx, dy = xs[None, :] - G_["c"][0], ys[:, None] - G_["c"][1]
    r = np.hypot(dx, dy)
    th = np.degrees(np.arctan2(-dy, dx)) % 360.0
    longe = np.ones(r.shape, bool)
    for a in (4.12, 22.04, 39.95, 57.85, 75.72):
        d = np.radians((th - a + 180) % 360 - 180)
        longe &= np.abs(r * np.sin(d)) > 1.6
    am = q["amostra"]
    sel = longe & (r > am["r"][0]) & (r < am["r"][1]) & (th > am["t"][0]) & (th < am["t"][1]) & (L > 110) & (L < 215)
    tom = np.median(reg[sel], axis=0)
    # a volta que falta, na transparência
    T = PC.Tela(reg.shape[:2], s, origem, X0, Y0)
    T.X0, T.Y0, T.org = X0, Y0, origem
    vao = (T.r > G_["rc"] + 0.3) & (T.r < G_["R"] - 0.2) & (PC.ang_rel(T.t, q["ini"]) < (q["fim"] - q["ini"]))
    a = T.reduz(vao) * np.clip((L - 175.0) / 30.0, 0, 1)          # as linhas escuras ficam por cima
    reg = reg * (1 - q["opac"] * a[..., None]) + tom * (q["opac"] * a)[..., None]
    # os raios: cheios até o corte, tracejados depois (no tom da linha dos degraus, sob a mesma transparência)
    linha = tom * q["linha_esc"] * 0.82
    cheio = np.zeros(T.r.shape, bool)
    for ang in q["cheios"]:
        cheio |= (PC.dist_raio(T, ang) < 0.16) & (np.abs(PC.ang_rel(T.t, ang + 180) - 180) < 90) \
            & (T.r > G_["rc"] + 0.4) & (T.r < G_["R"] - 0.2)
    trac = np.zeros(T.r.shape, bool)
    for ang in q["tracejados"]:
        trac |= PC.tracejado(T, ang, larg=0.30, r1=G_["R"] - 0.2)
    reg = PC.compor(reg, T.reduz(cheio) * 0.75, linha)
    reg = PC.compor(reg, T.reduz(trac) * 0.72, PC.COR["traco"])
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# A escada em U ("melhorar o aspecto desses degraus"): a mesma escada do Térreo (`terreo_casaa_2511d.ESCADA`, a
# geometria do PDF), vista de cima. Cheios: o lance de baixo (o que chega a este nível, com o DESCE), o patamar e o
# começo do lance de cima, à direita da linha de corte; à esquerda do corte, o vão branco fica como está. As pedras como
# as do Térreo: o tom dos degraus de lá (na cor de cada imagem), o veio do travertino ao comprido de cada degrau, um
# pouco diferente em cada pedra, o bocel em linha fina com a sombra curta no degrau de baixo e a luz na quina; o
# patamar numa pedra só, sem as manchas. Os guarda-corpos de vidro e a linha de corte redesenhados finos; os rótulos
# (DESCE PARA O HALL INTERNO, a seta e o D) voltam por cima.
ESCADA_U = dict(caixa=(2246.0, 906.0, 2496.0, 1090.0), tom_terreo=(161.0, 175.0, 185.0),
                amostra=(2262.0, 1030.0, 2410.0, 1075.0), tex_m=1.2, tex_ganho=0.50,
                bocel=dict(larg=0.28, escuro=0.30, sombra=0.11, sombra_px=1.3, luz=0.05),
                vidro=(238, 236, 231), vidro_borda=(112, 112, 110), borda_larg=0.24, gc_sombra=0.16,
                corte=(78, 78, 78), corte_larg=0.30)


def escada_u(img, s, origem, q=ESCADA_U):
    E = D.ESCADA
    jan = V.janela(img, q["caixa"], s, origem)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    a_sup = V.cob([V.ret(*E["sup"])], jan, s, origem)
    a_pat = V.cob([V.ret(*E["pat"])], jan, s, origem)
    a_inf = V.cob([V.ret(*E["inf"])], jan, s, origem)
    direita = [tuple(p) for p in E["quebra"]] + [(E["sup"][2], E["sup"][3]), (E["sup"][2], E["sup"][1])]
    a_cheia = np.clip(a_inf + a_pat + V.cob([direita], jan, s, origem) * a_sup, 0, 1)
    # o tom: o dos degraus do Térreo, na cor desta imagem (a razão entre os degraus de hoje aqui e na final)
    L = reg.mean(2)
    ax0, ay0, ax1, ay1 = V.janela(img, q["amostra"], s, origem, folga=0)
    am = img[ay0:ay1, ax0:ax1].reshape(-1, 3).astype(np.float32)
    La = am.mean(1)
    cur = np.median(am[(La > 150) & (La < 235)], axis=0)
    ref_final = np.float32([188.0, 199.0, 210.0])                  # os degraus de hoje na final (medidos)
    tom = np.float32(q["tom_terreo"]) * cur / ref_final
    med = float(np.median(La[(La > 150) & (La < 235)]))
    # os rótulos da parte cheia, para voltar por cima
    faixa = ((ys > E["inf"][1] + 3.0) & (ys < E["inf"][3] - 3.0))[:, None]
    at, cor_t = V.letras(reg, (a_inf > 0.5) & faixa, escala=s, ref=med, dif=90.0, piso_dif=35.0)
    # as pedras
    lado = max(16, int(round(q["tex_m"] * D.PX_M * s)))
    T2 = D._tex("travertino_opcao_2.png", lado)
    Tl = T2.mean(2)
    Tl = Tl / Tl.mean()
    p = T2.shape[0]
    rng = np.random.default_rng(6421)
    Dg = np.empty_like(reg)
    Dg[:] = tom
    jj, ii = np.arange(X0, X1), np.arange(Y0, Y1)
    pedras = [(ax, E["sup"][1], bx, E["sup"][3]) for ax, bx in zip(E["xs_sup"][:-1], E["xs_sup"][1:])]
    pedras += [(ax, E["inf"][1], bx, E["inf"][3]) for ax, bx in zip(E["xs_inf"][:-1], E["xs_inf"][1:])]
    pedras.append(E["pat"])
    for pr in pedras:
        a = V.cob([V.ret(*pr)], jan, s, origem)
        if not (a > 0).any():
            continue
        dx, dy = rng.integers(0, p, 2)
        f = 1.0 + rng.uniform(-0.015, 0.015)
        tl = Tl[np.mod(ii + dy, p)[:, None], np.mod(jj + dx, p)[None, :]]
        Dg = V.compor(Dg, a, tom[None, None, :] * (f * (1 + q["tex_ganho"] * (tl - 1)))[..., None])
    # o bocel (o lance de cima desce para a esquerda, o de baixo para a direita, a partir deste nível)
    b = q["bocel"]
    fator = np.ones((H, W), np.float32)
    for xs_l, lim, lado_s in ((E["xs_sup"][1:], E["sup"], -1), (E["xs_inf"][1:], E["inf"], +1)):
        lin = (ys >= lim[1]) & (ys <= lim[3])
        for xl in xs_l:
            d = (xs - xl) * lado_s
            som = np.where(d > 0, np.exp(-d / b["sombra_px"]), 0.0) * b["sombra"]
            luz = np.where((d < 0) & (d > -0.6), b["luz"], 0.0)
            fator[lin] *= (1 - som + luz)[None, :].astype(np.float32)
            a_l = V.cob([V.ret(xl - b["larg"] / 2, lim[1], xl + b["larg"] / 2, lim[3])], jan, s, origem)
            fator *= (1 - b["escuro"] * a_l)
    Dg = Dg * fator[..., None]
    out = reg * (1 - a_cheia[..., None]) + Dg * a_cheia[..., None]
    # os guarda-corpos de vidro (sobre a parte cheia; sobre o vão fica o de hoje)
    for r in E["gc"]:
        af = V.cob([V.ret(*r)], jan, s, origem) * a_cheia
        if not (af > 0).any():
            continue
        x0, y0, x1, y1 = r
        e = q["borda_larg"]
        dentro = V.cob([V.ret(x0 + e, y0 + e, x1 - e, y1 - e)], jan, s, origem) * a_cheia
        borda = np.clip(af - dentro, 0, 1)
        sb = cv2.GaussianBlur(af, (0, 0), max(0.6 * s, 0.5))
        Ms = np.float32([[1, 0, 0.6 * s], [0, 1, 0.8 * s]])
        sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - af) * a_cheia
        out *= (1 - q["gc_sombra"] * sb)[..., None]
        out = V.compor(out, dentro, np.float32(q["vidro"]))
        out = V.compor(out, borda, np.float32(q["vidro_borda"]))
    # a linha de corte (a diagonal com a quebra em Z)
    qb = E["quebra"]
    a_c = np.zeros((H, W), np.float32)
    for p0, p1 in zip(qb[:-1], qb[1:]):
        a_c = np.maximum(a_c, V.cob([V.seg(p0, p1, q["corte_larg"])], jan, s, origem))
    out = V.compor(out, a_c * 0.9, q["corte"])
    out = V.compor(out, at, cor_t)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# As cortinas ("atualize as cortinas conforme estamos usando"): a C4 das Casas B, C, D e E
# (`cortinas_padrao_casad_1611.aplicar`, o linho em ondas a 0,82 com o trilho grafite do lado do vidro, 0,22 m de pano,
# até a ponta da parede de cada lado e 0,15 m além dela onde a parede segue), nos trechos de cortina do PDF. Na final a
# própria função (no quadro da Casa A, 3840 px); ela anota cada limpeza (o pano de antes sai: o piso logo de dentro,
# em espelho, só fora das paredes do PDF) e cada pouso, e o 12K repete as mesmas contas na escala dele.
_CORT = {}


def _plano_cortinas():
    """Roda a C4 na final e guarda o resultado, as limpezas (o, v, A0, A1, S0, S1) e os pousos da cortina."""
    if "plano" in _CORT:
        return _CORT["plano"]
    import inspect
    import textwrap
    import final3840_casaa as FA
    import cortinas_padrao_casad_1611 as CP
    import pedidos_terreo_casac_1311 as PT
    import biblioteca_terreo_casaa_1211 as BT
    src = textwrap.dedent(inspect.getsource(PT.cortinas))
    alvo = "        alvo[livre_] = fonte[livre_]\n"
    assert alvo in src
    src = src.replace(alvo, alvo + "        _OPS.append((o, v, A0, A1, S0, S1))\n").replace("def cortinas(", "def _cortinas_reg(")
    ops, pousos = [], []
    ns = dict(PT.__dict__)
    ns["_OPS"] = ops
    exec(compile(src, PT.__file__, "exec"), ns)
    orig_c, orig_p = PT.cortinas, BT.pousar

    def pousar(out, P, cx, cy, wt, ht, ang, sombras, px_m, *a, **k):
        pousos.append((P.copy(), cx, cy, wt, ht, ang, [dict(s_) for s_ in sombras], px_m))
        return orig_p(out, P, cx, cy, wt, ht, ang, sombras, px_m, *a, **k)
    PT.cortinas, BT.pousar = ns["_cortinas_reg"], pousar
    try:
        Q = FA.QuadroA("1Pavimento")
        base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
        with contextlib.redirect_stdout(io.StringIO()):
            par = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") and max(d["fill"]) < 0.6,
                              ss=2)
            res = CP.aplicar(Q, base.copy(), q=dict(CP.CORTINAS_D, extra=[]))
    finally:
        PT.cortinas, BT.pousar = orig_c, orig_p
    _CORT["plano"] = (res, ops, pousos, (par > 0.3).astype(np.float32))
    return _CORT["plano"]


# o que fica por cima da cortina nova (a poltrona da suíte, que encosta no vão): o creme da peça na caixa
PROTEGE = {2: dict(caixa=(1613.0, 1010.0, 1645.0, 1075.0), lum=170.0, rb=(12.0, 58.0))}


def _protegidos(img, s, origem, sel):
    out = []
    for i in sel:
        if i not in PROTEGE:
            continue
        q = PROTEGE[i]
        jan = V.janela(img, q["caixa"], s, origem, folga=0)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1].copy()
        f = reg.astype(np.float32)
        Lp, rbp = f.mean(2), f[..., 2] - f[..., 0]
        m = ((Lp > q["lum"]) & (rbp > q["rb"][0]) & (rbp < q["rb"][1])).astype(np.uint8)
        k = max(1, int(round(0.6 * s)))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((2 * k + 1,) * 2, np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)          # só a peça (o maior pedaço)
        if n < 2:
            continue
        m = lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        out.append((jan, reg, m))
    return out


def _repor(img, prot):
    for (X0, Y0, X1, Y1), reg, m in prot:
        img[Y0:Y1, X0:X1][m] = reg[m]
    return img


def cortinas(img, s, origem, idx=None):
    """As cortinas (todas, ou só a de índice `idx`, na ordem do plano)."""
    res, ops, pousos, par = _plano_cortinas()
    sel = range(len(ops)) if idx is None else [idx]
    prot = _protegidos(img, s, origem, sel)
    if s < 2:                                      # a final: os px que a própria função mudou, em volta deste trilho
        base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
        mud = np.any(res != base, axis=2)
        if idx is not None:
            o, v, A0, A1, S0, S1 = ops[idx]
            P, cx, cy, wt, ht = pousos[idx][:5]
            x0, x1 = int(cx - wt / 2 - 12), int(cx + wt / 2 + 12)
            y0, y1 = int(cy - ht / 2 - 12), int(cy + ht / 2 + 12)
            caixa = np.zeros_like(mud)
            caixa[max(y0, 0):y1, max(x0, 0):x1] = True
            mud &= caixa
        img[mud] = res[mud]
        return _repor(img, prot)
    H, W = img.shape[:2]
    for i in sel:
        o, v, A0, A1, S0, S1 = ops[i]
        # o, "v": colunas A (x) e linhas S (y); o, "h": a imagem transposta (linhas = x, colunas = y)
        ia, ib = (0, 1) if o == "v" else (1, 0)
        a0 = int(round((A0 - origem[ia]) * s))
        a1 = int(round((A1 - origem[ia]) * s))
        s0 = int(round((S0 - origem[ib]) * s))
        s1 = int(round((S1 - origem[ib]) * s))
        n = a1 - a0
        im = img if o == "v" else img.transpose(1, 0, 2)
        if not (0 <= s0 < s1 <= im.shape[0] and n > 0 and a0 - n >= 0 and a1 + n <= im.shape[1]):
            continue
        fonte = (im[s0:s1, a1:a1 + n] if v == "esquerda" else im[s0:s1, a0 - n:a0])[:, ::-1].copy()
        # as paredes do PDF (a máscara da final, levada ao 12K)
        rr, cc = np.mgrid[s0:s1, a0:a1].astype(np.float32)
        fx, fy = (cc, rr) if o == "v" else (rr, cc)
        mx = ((fx + 0.5) / s + origem[0] - 0.5).astype(np.float32)
        my = ((fy + 0.5) / s + origem[1] - 0.5).astype(np.float32)
        pq = cv2.remap(par, mx, my, cv2.INTER_LINEAR, borderValue=0) > 0.5
        alvo = im[s0:s1, a0:a1]
        alvo[~pq] = fonte[~pq]
    import biblioteca_terreo_casaa_1211 as BT
    o_ = img.astype(np.float32)
    for i in sel:
        P, cx, cy, wt, ht, ang, sombras, px_m = pousos[i]
        o_ = BT.pousar(o_, P, (cx - origem[0]) * s, (cy - origem[1]) * s, wt * s, ht * s, ang, sombras, px_m * s)
    img[:] = np.clip(np.round(o_), 0, 255).astype(np.uint8)
    return _repor(img, prot)


# ----------------------------------------------------------------------------------------------------------------------
ITENS = {"cortina_1": (2505.0, 1320.0, 2560.0, 1585.0), "cortina_2": (1590.0, 330.0, 1650.0, 610.0),
         "cortina_3": (1590.0, 995.0, 1650.0, 1220.0), "cortina_4": (1340.0, 1205.0, 1395.0, 1470.0),
         "escada_u": (2240.0, 900.0, 2500.0, 1095.0), "caracol": (1905.0, 1490.0, 2050.0, 1640.0), "piso_servico": (1905.0, 1328.0, 2250.0, 1635.0), "sala_intima": (2010.0, 940.0, 2200.0, 1252.0), "bancada_entrada": (1895.0, 1275.0, 2005.0, 1335.0)}
FUNC = {"cortina_1": lambda im, s, o: cortinas(im, s, o, 0), "cortina_2": lambda im, s, o: cortinas(im, s, o, 1),
        "cortina_3": lambda im, s, o: cortinas(im, s, o, 2), "cortina_4": lambda im, s, o: cortinas(im, s, o, 3),
        "escada_u": escada_u, "caracol": caracol, "sala_intima": sala_intima, "bancada_entrada": bancada_entrada, "piso_servico": piso_servico}


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
    for f in ([] if os.environ.get("SO_12K") else EP.PLANTAS[PLANTA]):
        im = cv2.imread(str(EP.PROJ / f))
        for nome in nomes:
            im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    if not os.environ.get("SO_12K"):
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
            A, B = mapa(x0, y0)
            # a escala: a de x e a de y, pesadas pela largura e pela altura da caixa (numa caixa estreita e alta,
            # como a de uma cortina, a de x sozinha erra)
            ex_ = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            ey_ = (mapa(x0, y0 + 1000.0)[1] - B) / 1000.0
            sx = (ex_ * (x1 - x0) + ey_ * (y1 - y0)) / ((x1 - x0) + (y1 - y0))
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

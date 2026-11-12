"""As peças da biblioteca do usuário no Térreo da Casa A (12/11).

Usuário: "eu também quero que você me faça a proposta para substituição dos elementos, né, baseado na biblioteca de
objetos. Vamos concentrar os esforços agora na planta do térreo"; a proposta (a planta de hoje ao lado das peças,
`renders/POE642_CasaA_PH_Terreo_1211_proposta_biblioteca_{1,2,3}.jpg`) foi aprovada com "OK"; depois, "NÃO ALTERE OS
CARROS. DEXE COMO ESTAR" (a garagem fica). Os vasos do lavabo, do WC e do banho varanda ficam marrons (sem escolha do
usuário entre o marrom de 26/10 e o branco da biblioteca, fica o de hoje). Vendo a instalação: "PRECISA DIMINUIR O
TAMANHO DA CHURRASQUEIRA PARA CABER NA BANCADA SEM FICAR POR CIMA DA PAREDE" (a grelha de 62 x 32 px, dentro da bancada,
e a beira clara da antiga junto à parede no tom da bancada: `beira_da_churrasqueira`) e "AS BANQUETAS FICAM PARCIALMENTE
POR DEBAIXO DA BANCADA, NÃO SOBRE ELAS" (as banquetas da gourmet e da ilha com cerca de 40% sob o tampo: `corte`).

A biblioteca (`biblioteca-objetos/02-terreo`, PNG com transparência, vista de cima, gerados no Higgsfield; no repositório,
só as peças usadas aqui) entra peça a peça no lugar da que ela substitui (a composição não muda): o centro, o tamanho e o
giro de cada uma vêm do PDF (as caixas das peças e as poses das poltronas das rodadas anteriores) ou, onde a final
diverge do PDF, da peça da final. Em cada ambiente:
  1. a pegada das peças antigas (com a sombra) volta ao piso de cada lugar: o travertino, o tapete da varanda, o Bege
     Bahia, o marrom e as bancadas, cada um tecido das suas fontes e emendado ao piso de fora
     (`pedidos_terreo_casaa_2910.piso_refeito`); as paredes, as plantas, os móveis que ficam e os rótulos não mudam;
  2. as peças novas, giradas e na escala (renderizadas a 4 x e reduzidas em área), com a sombra curta da luz do alto à
     direita (a das poltronas da Casa E, a das mesas de tampo grande, ou a rente das peças baixas); as cadeiras e
     banquetas por baixo da mesa e da bancada, como antes;
  3. os tracejados finos (os vazios e o pergolado) de volta por cima, da camada do 12K (`..._12K_tracejados.png`).

O mesmo desenho vai ao 12K (`pecas_12k`, chamado pelo `ampliacao_12k_terreo_casaa.montar12k`): as peças na escala do
12K (os PNG da biblioteca têm resolução de sobra) sobre o piso da entrada ampliada nas zonas refeitas.

  python3 biblioteca_terreo_casaa_1211.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final do Térreo e os antes e depois
`renders/POE642_CasaA_PH_Terreo_1211b_<ambiente>_antes_depois.jpg`.
"""

import argparse
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                    # noqa: E402

RAIZ_GIT = AQUI.parent.parent.parent
R = AQUI.parent / "renders"
FINAL = R / "POE642_CasaA_PH_Terreo_final_rotulos.png"
ENTRADA = R / "POE642_CasaA_PH_Terreo_12K_entrada_ia.png"
TRACOS = R / "POE642_CasaA_PH_Terreo_12K_tracejados.png"
BIB = AQUI.parent / "biblioteca-objetos" / "02-terreo"
ANTES_COMMIT = "baf4362"
X0E, YIAE = 166, 98                              # a entrada da IA na final: (x - 166, y - 98)

# as sombras (m): a das poltronas da Casa E (`final3840_casae.POLTRONAS_TE` para uma peça de ~0,85 m), a das mesas de
# tampo grande (`pedidos_terreo_casaa_2910.SOMBRA_MESA_TA`), a rente das peças baixas e a dos tapetes
SOMBRAS = {"movel": [{"dx": -0.05, "dy": 0.05, "sig": 0.06, "forca": 0.34},
                     {"dx": 0.0, "dy": 0.0, "sig": 0.025, "forca": 0.18}],
           "mesa": [{"dx": -0.05, "dy": 0.05, "sig": 0.06, "forca": 0.24},
                    {"dx": -0.015, "dy": 0.015, "sig": 0.02, "forca": 0.22}],
           "baixa": [{"dx": -0.012, "dy": 0.012, "sig": 0.015, "forca": 0.22}],
           "tapete": [{"dx": -0.01, "dy": 0.01, "sig": 0.02, "forca": 0.10}],
           None: []}
TRAVERTINO = [(1526, 358, 1580, 556), (1885, 884, 2155, 924)]           # `pedidos_terreo_casaa_2910.PISO_TA`


def girar_pt(fx, fy):
    """O giro (graus, anti-horário na tela) que leva a frente do PNG (para baixo) à direção (fx, fy) da tela."""
    return float(np.degrees(np.arctan2(fx, fy)))


def ret(x0, y0, x1, y1, m=0):
    return ("ret", (x0 - m, y0 - m, x1 + m, y1 + m))


def disco(cx, cy, r):
    return ("disco", (cx, cy, r))


def caixa_rot(cx, cy, w, h, ang, m=0):
    return ("rot", (cx, cy, w + 2 * m, h + 2 * m, ang))


# Cada ambiente: as zonas refeitas (pegada das peças antigas, com folga para a sombra) e as fontes do piso de cada uma,
# as caixas que ficam (plantas, móveis que não mudam) e as peças novas, na ordem de desenho:
# (png, cx, cy, largura, altura, giro, sombra, corte) — largura e altura do PNG antes do giro (px da final); altura None:
# na proporção do PNG; corte: (eixo, valor, lado) — a peça não passa da borda da bancada ou da mesa.
AMBIENTES = {
    "varanda_estar": {
        "zonas": [([("pdf", ((1715, 369, 1829, 494), 6)), ("polt", (("varanda, de cima", "varanda, de baixo"), 4)),
                    ret(1650.4, 539.3, 1769.8, 566.1, 9),
                    ret(1670.3, 435.4, 1739.8, 516.3, 8), ret(1610.3, 460.6, 1628.3, 478.5, 7),
                    ret(1699.1, 383.6, 1717.0, 401.5, 6)], None)],
        "tapete": {"caixa": (1618.0, 396.5, 1797.2, 545.7), "fontes": [(1645, 516, 1695, 538), (1748, 506, 1793, 540)]},
        "manter": [(1786, 352, 1846, 445)],
        "pecas": [("varanda/poltrona-externa-a", 1614.7, 429.7, 49, None, girar_pt(1, 0), "movel", None),
                  ("varanda/poltrona-externa-a", 1614.7, 511.0, 49, None, girar_pt(1, 0), "movel", None),
                  ("varanda/sofa-curvo-externo", 1772.0, 433.0, 152, None, girar_pt(-0.89, 0.46), "movel", None),
                  ("lounge-dos-brises/banco-brises", 1710.1, 552.7, 119, 30, 0.0, "movel", None),
                  ("varanda/mesa-centro-seixo", 1692.5, 456.5, 46, 40, 30.0, "mesa", None),
                  ("varanda/mesa-centro-seixo", 1713.5, 484.5, 66, 42, -55.0, "mesa", None),
                  ("lounge-dos-brises/mesa-lateral-externa", 1619.3, 469.5, 18, None, 0.0, "baixa", None),
                  ("lounge-dos-brises/mesa-lateral-externa", 1708.0, 392.5, 18, None, 0.0, "baixa", None)]},
    "sala_estar": {
        # (12/11) com o sofá menor, a pegada do de antes (206 px, 50,8°) também volta ao piso: o sofá antigo do render,
        # maior que o do PDF, ficava escondido por ele
        "zonas": [([disco(2035.9, 502.35, 126.0), ("pdf", ((1876, 372, 2080, 531), 6)),
                    ("peca", ("sala-de-estar/sofa-curvo-render-casa-a", 1966.0, 447.0, 206, girar_pt(0.775, 0.632), 4)),
                    ("polt", (("sala de estar, à direita do tapete", "sala de estar, embaixo, à esquerda",
                               "sala de estar, embaixo, à direita"), 3))], None)],
        "manter": [(1878, 368, 1924, 432)],
        "pecas": [("sala-de-estar/tapete-redondo-render-v2", 2035.9, 502.35, 239, None, 0.0, "tapete", None),
                  # (12/11, usuário: "DIMUNUIR O TAMANHO DO SOFÁ"; "TALVEZ ROTACIONANDO O SOFÁ, RESOLVA") o sofá no
                  # contorno do sofá do PDF: o giro, o tamanho e o centro de maior sobreposição com ele (86% -> 87%;
                  # antes, 206 px no giro de 50,8°, 65%): 15° no sentido horário e 10% menor
                  ("sala-de-estar/sofa-curvo-render-casa-a", 1982.0, 443.0, 186, None, girar_pt(0.775, 0.632) - 15.0,
                   "movel", None),
                  # (12/11, "Revisão de poltronas e rotação necessária") a frente na normal da linha entre os pés da
                  # frente do símbolo do PDF ((2098;448) e (2128;492)): -56° (antes -72,5°, a pose de 29/10)
                  ("sala-de-estar/poltrona-creme-madeira-render", 2122.95, 465.15, 50, None, girar_pt(-0.83, 0.56),
                   "movel", None),
                  ("sala-de-estar/poltrona-oliva-render-v2", 1993.35, 581.0, 44, None, 180.0, "movel", None),
                  ("sala-de-estar/poltrona-oliva-render-v2", 2064.95, 581.0, 44, None, 180.0, "movel", None),
                  ("sala-de-estar/mesa-centro-seixo-render-v2", 2041.25, 507.25, 72, 43, 0.0, "mesa", None),
                  ("sala-de-estar/mesa-apoio-escura", 2077.95, 438.3, 21, None, 0.0, "baixa", None),
                  ("sala-de-estar/mesa-apoio-escura", 2029.2, 576.0, 21, None, 0.0, "baixa", None),
                  ("sala-de-estar/mesa-apoio-escura", 1952.0, 548.0, 22, None, 0.0, "baixa", None)]},
    "estar_projecao": {
        "zonas": [([ret(1921.5, 666.4, 1994.7, 739.4, 5), ret(2039.8, 666.1, 2112.9, 739.2, 5),
                    ret(2038.7, 759.7, 2111.8, 832.7, 5), ret(1922.4, 759.5, 1995.5, 832.6, 5),
                    ret(1690.2, 659.8, 1768.2, 737.8, 4), ret(1690.2, 760.2, 1768.2, 838.3, 4),
                    ret(1736.0, 738.5, 1756.8, 759.4, 5)], None)],
        "manter": [(1996, 722, 2046, 771)],                                  # a mesa triangular fica
        "pecas": [("sala-de-estar/poltrona-caramelo-render-v2", 1958.1, 702.9, 52, None, girar_pt(0.71, 0.71),
                   "movel", None),
                  ("sala-de-estar/poltrona-caramelo-render-v2", 2076.35, 702.65, 52, None, girar_pt(-0.71, 0.71),
                   "movel", None),
                  ("sala-de-estar/poltrona-caramelo-render-v2", 2075.25, 796.2, 52, None, girar_pt(-0.71, -0.71),
                   "movel", None),
                  ("sala-de-estar/poltrona-caramelo-render-v2", 1958.95, 796.05, 52, None, girar_pt(0.71, -0.71),
                   "movel", None),
                  ("varanda/poltrona-externa-b", 1729.2, 698.8, 56, None, girar_pt(-0.6, 0.8), "movel", None),
                  ("varanda/poltrona-externa-b", 1729.2, 799.25, 56, None, girar_pt(-0.6, -0.8), "movel", None),
                  ("lounge-dos-brises/mesa-lateral-externa", 1746.4, 748.95, 21, None, 0.0, "baixa", None)]},
    "mesas_redondas": {"zonas": [([disco(1687.2, 951.0, 92.0), disco(1681.6, 1129.8, 92.0)], None)],
                       "pecas": "mesas_redondas"},
    "jantar": {
        "zonas": [([ret(1936.0, 943.0, 2113.0, 1018.0, 7), ret(1914.0, 920.0, 2137.0, 1040.0, 0),
                    ret(1939.9, 1075.8, 2118.9, 1105.7, 6)], None)],
        "manter": [(1878, 1055, 1922, 1102)],
        "pecas": "jantar"},
    "escritorio": {
        "zonas": [([ret(2415, 424, 2533, 474, 6), ret(2454, 400, 2492, 424, 5), ret(2427, 474, 2460, 494, 5),
                    ret(2488, 474, 2521, 494, 5), ret(2529.4, 521.8, 2583.0, 578.1, 7),
                    ret(2509.6, 554.5, 2536.0, 583.3, 5)], None)],
        "pecas": [("escritorio/cadeira-escritorio", 2473.0, 415.0, 34, None, 0.0, "movel", None),
                  ("escritorio/cadeira-visitante", 2444.0, 484.0, 30, None, 180.0, "movel", None),
                  ("escritorio/cadeira-visitante", 2505.0, 484.0, 30, None, 180.0, "movel", None),
                  ("escritorio/mesa-a", 2474.0, 449.0, 118, 50, 0.0, "mesa", None),
                  ("escritorio/poltrona-leitura", 2556.2, 549.95, 48, None, girar_pt(-0.7, -0.7), "movel", None),
                  ("escritorio/mesa-lateral", 2522.8, 568.9, 26, None, 0.0, "baixa", None)]},
    "gourmet_cozinha": {
        "zonas": [([ret(1488, 1238, 1740, 1270, 0)], None),
                  ([ret(1943, 1212, 2049, 1245, 0)], [(1880, 1330, 1950, 1400), (2050, 1340, 2100, 1400)]),
                  ([ret(1966.9, 1284.8, 2019.4, 1314.6, 1)], [(1940, 1288, 1963, 1314), (2024, 1288, 2046, 1314)]),
                  ([ret(1611.6, 1297.9, 1664.2, 1327.8, 1)], [(1575, 1296, 1606, 1330), (1670, 1296, 1700, 1330)]),
                  ([ret(1512, 1401, 1593, 1442, 1)], [(1600, 1400, 1640, 1440), (1650, 1400, 1690, 1440)])],
        "pecas": "gourmet_cozinha"},
    "lounge_brises": {
        "zonas": [([ret(1268.5, 1287.7, 1332.1, 1351.3, 6), ret(1280, 1392, 1310, 1517, 6),
                    ret(1354, 1399, 1391, 1508, 6), ret(1288.7, 1558.4, 1417.6, 1611.4, 7)],
                   [(1330, 1200, 1470, 1280), (1420, 1300, 1470, 1540)])],
        "pecas": [("lounge-dos-brises/poltrona-brises", 1300.3, 1319.5, 50, None, girar_pt(0.71, 0.71), "movel",
                   None),
                  ("lounge-dos-brises/banco-brises", 1295.0, 1454.5, 125, 31, 90.0, "movel", None),
                  ("lounge-dos-brises/banco-externo", 1372.5, 1453.5, 109, 36, 90.0, "movel", None),
                  ("lounge-dos-brises/poltrona-brises", 1313.75, 1584.9, 50, None, 180.0, "movel", None),
                  ("lounge-dos-brises/poltrona-brises", 1392.6, 1584.9, 50, None, 180.0, "movel", None),
                  ("lounge-dos-brises/mesa-lateral-externa", 1353.65, 1582.7, 21, None, 0.0, "baixa", None)]},
    "piscina": {"zonas": "espreguicadeiras", "pecas": "espreguicadeiras"},
    "banhos": {
        "zonas": [([ret(1669, 1591, 1681, 1603, 1)], [(1640, 1572, 1664, 1590), (1640, 1606, 1664, 1620)]),
                  ([ret(2271, 1215, 2284, 1233, 1)], [(2255, 1236, 2268, 1258), (2286, 1236, 2300, 1258)]),
                  ([ret(2308.8, 1216.2, 2331.3, 1248.9, 2)], [(2255, 1236, 2268, 1258), (2286, 1236, 2300, 1258)]),
                  ([ret(2421.3 - 30, 1175.5 - 60, 2421.3 + 30, 1175.5 + 60, 0)], [(2452, 1236, 2492, 1300)])],
        "pecas": "banhos"},
    # (12/11, usuário: "MELHORE A REPRESENTAÇÃO DESSE VASO") a bacia do lavabo: o bloco marrom chapado sai (o piso do
    # lavabo de logo abaixo) e entra a bacia Carrara da biblioteca no retângulo do PDF (a caixa acoplada junto à parede
    # da direita, a frente para a esquerda), no marrom-escuro dos vasos do Térreo (`marrom`)
    "lavabo": {"zonas": [([ret(2312, 366, 2346, 394)], [(2259, 408, 2313, 427)])],
               "pecas": [("lavabo/cuba-esculpida-poros-render", 2330.55, 438.65, 57.3, 29.9, -90.0, "baixa", "lavabo"),
                         ("lavabo/bacia-carrara", 2330.1, 380.15, 21.1, 30.6, -90.0, "baixa", "marrom")]},
}


# ----------------------------------------------------------------------------------------------------------------------
def quieto(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


def ler_png(nome):
    P = cv2.imread(str(BIB / f"{nome}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def esticar_lados(P, alvo_aspecto, miolo=(0.2, 0.8)):
    """A cuba esculpida mais comprida: as faixas lisas dos lados esticadas, o miolo (a cuba e a torneira) igual."""
    h, w = P.shape[:2]
    a, b = int(w * miolo[0]), int(w * miolo[1])
    extra = alvo_aspecto * h - w
    if extra <= 0:
        return P
    lados = []
    for f in (P[:, :a], P[:, b:]):
        nw = max(1, int(round(f.shape[1] + extra / 2)))
        lados.append(cv2.resize(f, (nw, h), interpolation=cv2.INTER_CUBIC))
    Q = np.concatenate([lados[0], P[:, a:b], lados[1]], axis=1)
    Q[..., 3] = np.clip(Q[..., 3], 0, 255)
    return np.ascontiguousarray(Q)


def so_louca(P, croma=24):
    """A cuba compacta sem a pedra bege em volta: só o branco da louça, o cromado e o ralo (pouco croma)."""
    c = P[..., :3]
    m = ((c.max(axis=2) - c.min(axis=2)) < croma) & (P[..., 3] > 128)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros(m.shape, bool)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 0.01 * m.size:
            keep |= lab == i
    keep = cv2.morphologyEx(keep.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)).astype(bool)
    Q = P.copy()
    Q[..., 3] = np.where(keep, P[..., 3], 0)
    ys, xs = np.nonzero(Q[..., 3] > 0)
    Q = Q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Q[..., 3] = cv2.GaussianBlur(Q[..., 3], (0, 0), 1.0)
    return np.ascontiguousarray(Q)


MARROM_VASO = (57, 75, 101)                     # BGR: o marrom-escuro dos vasos do Térreo (o da final de 26/10)


def marrom(P, cor=MARROM_VASO, faixa=(0.80, 1.22), traco=2.2):
    """A louça branca da biblioteca no marrom-escuro dos vasos: o tom `cor` na luz da louça, com o branco da peça
    levado à `faixa` (do p5 ao p95 da luz) e as linhas do desenho (a borda da tampa, a caixa, o assento) reforçadas
    (`traco`: o px menos a média de perto); no marrom, o pouco contraste do branco sumia."""
    Q = P.copy()
    L = P[..., :3].mean(axis=2)
    a = P[..., 3] > 128
    p5, p95 = np.percentile(L[a], [5, 95])
    f = faixa[0] + (faixa[1] - faixa[0]) * (L - p5) / max(p95 - p5, 1.0)
    f += traco * (L - cv2.GaussianBlur(L, (0, 0), 3.0)) / 255
    Q[..., :3] = np.clip(np.float32(cor)[None, None] * np.clip(f, 0.55, 1.3)[..., None], 0, 255)
    return Q


def preparar(nome, larg, alt, extra=None):
    P = ler_png(nome)
    if extra == "marrom":
        P = marrom(P)
    if extra == "lavabo":
        P = esticar_lados(P, larg / alt)
    elif extra == "louca":
        P = so_louca(P)
    h, w = P.shape[:2]
    if alt is None:
        alt = larg * h / w
    return P, float(larg), float(alt)


def pousar(out, P, cx, cy, wt, ht, ang, sombras, px_m, nao=None, ss=4):
    """P (BGRA) com o centro em (cx, cy), wt x ht (antes do giro), girado `ang` graus (anti-horário na tela), sobre
    `out` (float32), com as sombras (m) por baixo; `nao` (bool, no quadro): os px que não mudam."""
    H, W = out.shape[:2]
    pm = P.copy()
    pm[..., :3] *= pm[..., 3:4] / 255
    tw, th = max(1, int(round(wt * ss))), max(1, int(round(ht * ss)))
    r = cv2.resize(pm, (tw, th), interpolation=cv2.INTER_AREA)
    marg = int(np.ceil(max([abs(s["dx"]) + abs(s["dy"]) + 3 * s["sig"] for s in sombras] + [0]) * px_m)) + 3
    lado = int(np.ceil(np.hypot(wt, ht))) + 2 * marg + 2
    x0, y0 = int(np.floor(cx - lado / 2)), int(np.floor(cy - lado / 2))
    M = cv2.getRotationMatrix2D((tw / 2, th / 2), float(ang), 1.0)
    M[0, 2] += (cx - x0) * ss - tw / 2
    M[1, 2] += (cy - y0) * ss - th / 2
    can = cv2.warpAffine(r, M, (lado * ss, lado * ss), flags=cv2.INTER_LINEAR, borderValue=0)
    small = cv2.resize(can, (lado, lado), interpolation=cv2.INTER_AREA)
    cor, a = small[..., :3], np.clip(small[..., 3] / 255, 0, 1)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + lado, W), min(y0 + lado, H)
    if xb <= xa or yb <= ya:
        return out
    cor, a = cor[ya - y0:yb - y0, xa - x0:xb - x0], a[ya - y0:yb - y0, xa - x0:xb - x0]
    reg = out[ya:yb, xa:xb].astype(np.float32)
    for s in sombras:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, s["sig"] * px_m))
        Ms = np.float32([[1, 0, s["dx"] * px_m], [0, 1, s["dy"] * px_m]])
        sh = cv2.warpAffine(sh, Ms, (sh.shape[1], sh.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        reg *= (1 - s["forca"] * sh)[..., None]
    reg = reg * (1 - a[..., None]) + cor
    if nao is not None:
        n = nao(xa, ya, xb, yb) if callable(nao) else nao[ya:yb, xa:xb]
        reg[n] = out[ya:yb, xa:xb][n]
    out[ya:yb, xa:xb] = reg if out.dtype == np.float32 else np.clip(np.round(reg), 0, 255).astype(out.dtype)
    return out


CAMADAS_PECAS = ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_LOUÇAS E METAIS")
_Q = {}


def _quadro():
    if "Q" not in _Q:
        _Q["Q"] = quieto(FA.QuadroA, "Terreo")
    return _Q["Q"]


def mascara_formas(formas, forma):
    H, W = forma
    m = np.zeros((H, W), np.uint8)
    for tipo, v in formas:
        if tipo == "pdf":
            # a pegada da peça antiga: o preenchimento do PDF das peças que cabem na caixa (px), com a folga da sombra
            Q = _quadro()
            (x0, y0, x1, y1), mg = v

            def dentro(d, x0=x0, y0=y0, x1=x1, y1=y1):
                if d.get("layer") not in CAMADAS_PECAS:
                    return False
                r = d["rect"]
                (a, b), (c, e) = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
                return min(a, c) >= x0 and max(a, c) <= x1 and min(b, e) >= y0 and max(b, e) <= y1
            k = (Q.preencher(dentro, ss=2) > 0.02).astype(np.uint8)
            m |= cv2.dilate(k, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * mg + 1,) * 2))
            continue
        if tipo == "peca":
            # (12/11) a pegada de uma peça da biblioteca numa pose (o sofá de antes, maior que o do PDF), com a folga
            nome, cx, cy, wt, ang, mg = v
            P, wt_, ht_ = preparar(nome, wt, None)
            Pa = P.astype(np.float32).copy()
            Pa[..., :3] = 255
            k = pousar(np.zeros((H, W, 3), np.float32), Pa, cx, cy, wt_, ht_, ang, [], 59.7, ss=2)[..., 0] > 127
            m |= cv2.dilate(k.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * mg + 1,) * 2))
            continue
        if tipo == "polt":
            import pedidos_terreo_casaa_2910 as PT
            nomes, mg = v
            k = PT._pegada_poltronas(_quadro(), nomes, forma).astype(np.uint8)
            m |= cv2.dilate(k, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * mg + 1,) * 2))
            continue
        if tipo == "ret":
            x0, y0, x1, y1 = v
            m[max(int(np.floor(y0)), 0):int(np.ceil(y1)), max(int(np.floor(x0)), 0):int(np.ceil(x1))] = 1
        elif tipo == "disco":
            cv2.circle(m, (int(round(v[0])), int(round(v[1]))), int(round(v[2])), 1, -1)
        elif tipo == "pol":
            pts, mg = v
            k = np.zeros((H, W), np.uint8)
            cv2.fillPoly(k, [np.round(pts).astype(np.int32)], 1)
            m |= cv2.dilate(k, np.ones((2 * mg + 1,) * 2, np.uint8))
        else:
            cx, cy, w, h, ang = v
            pts = cv2.boxPoints(((cx, cy), (w, h), -ang)).astype(np.int32)
            cv2.fillPoly(m, [pts], 1)
    return m.astype(bool)


# ----------------------------------------------------------------------------------------------------------------------
# as peças que dependem do PDF: as mesas redondas e as cadeiras, o jantar, a cozinha e o gourmet, as espreguiçadeiras e
# os banhos (o chuveiro quadrado com o braço até a parede)
def _pdf_grupos(Q):
    """As caixas giradas (px) das peças do PDF nas camadas de móveis e louças: {(camada, cx, cy): (w, h, ang)}."""
    camadas = ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_LOUÇAS E METAIS")
    return [d for d in Q.desenhos if d.get("layer") in camadas]


def mesas_redondas():
    mesas = [(1687.2, 951.0), (1681.6, 1129.8)]
    cadeiras = [(1688.1, 898.3), (1641.5, 925.2), (1734.6, 925.2), (1641.5, 978.9), (1734.6, 978.9),
                (1688.1, 1005.8), (1682.4, 1077.4), (1635.9, 1104.3), (1729.0, 1104.3), (1635.9, 1158.0),
                (1729.0, 1158.0), (1682.4, 1184.9)]
    pecas = []
    for x, y in cadeiras:
        mx, my = min(mesas, key=lambda m: np.hypot(m[0] - x, m[1] - y))
        v = np.array([mx - x, my - y])
        v /= np.linalg.norm(v)
        pecas.append(("varanda/cadeira-mesa-redonda", x, y, 34, None, girar_pt(*v), "movel", None))
    for mx, my in mesas:
        pecas.append(("varanda/mesa-redonda", mx, my, 95.5, None, 0.0, "mesa", None))
    return pecas


def jantar():
    pecas = []
    for x in (1978.2, 2026.0, 2073.8):
        pecas.append(("sala-de-jantar/cadeira-jantar-oliva-render", x, 938.4, 30, None, 0.0, "movel", None))
        pecas.append(("sala-de-jantar/cadeira-jantar-oliva-render", x, 1022.1, 30, None, 180.0, "movel", None))
    pecas.append(("sala-de-jantar/cadeira-jantar-oliva-render", 1930.4, 980.3, 30, None, girar_pt(1, 0), "movel",
                  None))
    pecas.append(("sala-de-jantar/cadeira-jantar-oliva-render", 2121.6, 980.3, 30, None, girar_pt(-1, 0), "movel",
                  None))
    pecas.append(("sala-de-jantar/mesa-jantar-madeira-render", 2024.5, 980.5, 177, 75, 0.0, "mesa", None))
    pecas.append(("sala-de-jantar/aparador", 2029.4, 1090.7, 179, 30, 0.0, "movel", None))
    return pecas


def gourmet_cozinha():
    pecas = []
    # as banquetas parcialmente por baixo da bancada (usuário: "AS BANQUETAS FICAM PARCIALMENTE POR DEBAIXO DA BANCADA,
    # NÃO SOBRE ELAS"): ~40% do assento sob a bancada (a borda dela em y 1270,5 no gourmet e 1245,5 na ilha), o encosto
    # para fora; a bancada por cima
    for x in (1512.0, 1562.0, 1612.0, 1662.0, 1712.0):                       # `terreo_casaa_1011.BANQUETAS_TA`
        pecas.append(("area-gourmet/banqueta-b", x, 1268.5, 25, None, 0.0, "movel", ("y", 1270.5, ">")))
    for x in (1960.3, 1996.1, 2032.0):
        pecas.append(("cozinha/banqueta-ilha", x, 1243.5, 24, None, 0.0, "movel", ("y", 1245.5, ">")))
    pecas.append(("cozinha/cooktop-quatro-bocas", 1993.15, 1299.7, 31, 29, 0.0, None, None))
    pecas.append(("cozinha/cooktop-quatro-bocas", 1637.9, 1312.85, 31, 29, 0.0, None, None))
    # a churrasqueira menor, dentro da bancada (usuário: "PRECISA DIMINUIR O TAMANHO DA CHURRASQUEIRA PARA CABER NA
    # BANCADA SEM FICAR POR CIMA DA PAREDE"): a bancada vai de y 1401 a 1442 (a parede começa em 1443); a grelha com
    # ~75% do tamanho, no meio dela, a 4-5 px da borda e da parede
    pecas.append(("area-gourmet/grelha-churrasqueira", 1552.5, 1421.0, 62, 32, 0.0, None, None))
    pecas.append(("area-gourmet/cuba-franke-misturador-unic", 1721.5, 1422.5, 43, 27, 180.0, None, None))
    for cy in (1344.5, 1392.3):                                              # as 2 cubas da pia (torneira na parede)
        pecas.append(("area-de-servico/cuba-franke-inox-link", 2134.9, cy, 38.2, 30.3, -90.0, None, None))
    for cx in (1760.3, 1802.1):                                              # os 2 tanques da área de serviço
        pecas.append(("area-de-servico/cuba-franke-inox-link", cx, 1471.7, 37.9, 35.4, 0.0, None, None))
    return pecas


def espreguicadeiras(Q):
    import pedidos_terreo_casaa_2910 as PT
    q = PT.ESPREG_TA
    caixas = []
    for r in q["pecas_pt"]:
        d = next(d for d in Q.desenhos if d.get("layer") == q["camada"] and d["type"] == "f"
                 and max(abs(a - b) for a, b in zip(d["rect"], r)) < 0.5)
        pts = np.float32([Q.p2q(*p) for p in PT._poligono_pt(d)])
        (cx, cy), (w, h), a = cv2.minAreaRect(pts)
        caixa = cv2.boxPoints(((cx, cy), (w, h), a))
        lados = [caixa[(i + 1) % 4] - caixa[i] for i in range(4)]
        longo = max(lados, key=np.linalg.norm)
        u = longo / np.linalg.norm(longo)
        if u[0] < 0:
            u = -u                                                           # a cabeceira para a direita (no alto)
        comp, larg = max(w, h), min(w, h)
        caixas.append((float(cx), float(cy), float(larg), float(comp), u, pts))
    return caixas


def chuveiro_braco(placa_c, parede, placa_px):
    """O chuveiro quadrado da biblioteca com o braço até a parede: (P, cx, cy, wt, ht, giro). `parede`: o px da face da
    parede na direção do braço (x ou y), com a direção ('dir', 'cima')."""
    P = ler_png("banho-varanda/chuveiro-quadrado-parede")
    a = P[..., 3] > 128
    larg_linha = a.sum(axis=1)
    lmax = larg_linha.max()
    y_placa = int(np.argmax(larg_linha > 0.6 * lmax))                        # onde começa a placa
    s = placa_px / lmax
    dist, eixo = parede
    alcance = abs(dist - (placa_c[0] if eixo == "dir" else placa_c[1])) - placa_px / 2
    braco_px = max(1.0, alcance / s)
    can = P[:y_placa]
    corpo = P[y_placa:]
    hc = can.shape[0]
    # o braço (as linhas de cima até a placa) esticado ou encurtado até alcançar a parede
    can = cv2.resize(can, (can.shape[1], max(2, int(round(braco_px)))), interpolation=cv2.INTER_AREA
                     if braco_px < hc else cv2.INTER_CUBIC)
    P2 = np.ascontiguousarray(np.concatenate([can, corpo], axis=0))
    P2[..., 3] = np.clip(P2[..., 3], 0, 255)
    h2, w2 = P2.shape[:2]
    wt, ht = w2 * s, h2 * s
    # o centro do PNG: a placa no lugar e o braço para a parede
    desloc = (ht / 2) - (corpo.shape[0] * s / 2)
    if eixo == "dir":
        return P2, placa_c[0] + desloc, placa_c[1], wt, ht, -90.0
    return P2, placa_c[0], placa_c[1] - desloc, wt, ht, 0.0


# ----------------------------------------------------------------------------------------------------------------------
def tracos():
    tr = cv2.imread(str(TRACOS))
    import terreo_casaa_1011 as TA
    import regras_1211_casaa as RG
    alfa = tr[..., 0].astype(np.float32) / 255
    sai = RG.claraboia_sai("Terreo")            # o X da claraboia, que saiu (12/11): os resíduos da camada não voltam
    if sai is not None:
        alfa[sai] = 0
    cor = np.where(tr[..., 1] > 127, np.float32(TA.FINOS_TA["claro"][0]), np.float32(TA.FINOS_TA["escuro"][0]))
    return alfa, cor


def rotulos(img):
    """Os rótulos (o que a final tem de diferente da entrada da IA, só nas caixas dos rótulos do 12K): ficam."""
    import json
    ent = cv2.imread(str(ENTRADA)).astype(np.int16)
    E = img.astype(np.int16).copy()
    E[YIAE:YIAE + ent.shape[0], X0E:X0E + ent.shape[1]] = ent
    d = np.abs(img.astype(np.int16) - E).max(axis=2) > 8
    alfa, _ = tracos()
    d &= cv2.dilate((alfa > 0.02).astype(np.uint8), np.ones((5, 5), np.uint8)) == 0
    Q = _quadro()
    caixas = np.zeros(d.shape, np.uint8)
    dados = json.loads((R / "POE642_CasaA_PH_Terreo_12K_dados.json").read_text())
    for b in dados["rotulos"]:
        u, v = Q.p2q(*b["pdf"])
        cx, cy = u + b["desvio"][0], v + b["desvio"][1]
        mw = 4.2 * len(b["nome"]) + 12
        cv2.rectangle(caixas, (int(cx - mw), int(cy - 22)), (int(cx + mw), int(cy + 24)), 1, -1)
    d &= caixas.astype(bool)
    return cv2.dilate(d.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)


def tecido(img, zona, fontes, semente, p_px=10):
    """O tapete de novo na `zona`: o tecido das fontes (a trama), no tom do tapete em volta, com a beira suave."""
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import texturas
    H, W = zona.shape
    ys, xs = np.nonzero(zona)
    y0, y1, x0, x1 = max(ys.min() - 4, 0), min(ys.max() + 5, H), max(xs.min() - 4, 0), min(xs.max() + 5, W)
    fs = []
    for a, b, c, d in fontes:
        f_ = img[b:d, a:c]
        fs += [f_, np.ascontiguousarray(f_[:, ::-1])]
    tec = texturas.quilting(fs, y1 - y0, x1 - x0, p=p_px, sobra=max(3, p_px // 3),
                            rng=np.random.default_rng(semente))[:y1 - y0, :x1 - x0].astype(np.float32)
    I = img[y0:y1, x0:x1].astype(np.float32)
    Z = zona[y0:y1, x0:x1]
    med = np.median(np.concatenate([f_.reshape(-1, 3) for f_ in fs]).astype(np.float32), axis=0)
    anel = cv2.dilate(Z.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~Z
    ok = anel & (np.abs(I - med).max(axis=2) < 30)
    if ok.sum() > 20:
        tec += (np.median(I[ok], axis=0) - np.median(tec[Z], axis=0))
    al = np.clip(cv2.GaussianBlur(Z.astype(np.float32), (0, 0), 0.8) * 1.6, 0, 1)
    al = np.maximum(al, Z.astype(np.float32))[..., None]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(np.round(I * (1 - al) + tec * al), 0, 255).astype(np.uint8)
    return out


def aplicar(antes):
    import pedidos_terreo_casaa_2910 as PT
    Q = quieto(FA.QuadroA, "Terreo")
    px_m = Q.px_m
    forma = antes.shape[:2]
    out = antes.copy()
    par = PT._paredes_fixas(Q, forma)
    rot = rotulos(antes)
    alfa_tr, cor_tr = tracos()
    zona_total = np.zeros(forma, bool)
    desenho = []
    REGISTRO.clear()
    REGISTRO.update({"pecas": [], "nao": np.zeros(forma, bool), "pecas_m": np.zeros(forma, bool)})
    sem = 4100
    plantas_caixas = []
    for nome, amb in AMBIENTES.items():
        manter = mascara_formas([ret(*b) for b in amb.get("manter", [])], forma)
        if nome in ("varanda_estar", "sala_estar", "jantar"):
            # as plantas em vaso ao lado das peças: o piso é refeito por baixo e a planta da final volta por cima
            # (`plantas_de_volta`), com a copa inteira
            plantas_caixas += amb.get("manter", [])
            manter = np.zeros(forma, bool)
        zonas = amb["zonas"]
        pecas = amb["pecas"]
        if zonas == "espreguicadeiras":
            cx_ = espreguicadeiras(Q)
            zonas = [([("pol", (c[5], 10)) for c in cx_], [(1340, 455, 1470, 522), (1474, 560, 1504, 720)])]
            pecas = [("deck-piscina/espreguicadeira-madeira-render", c[0], c[1], c[2] * 0.96, c[3],
                      float(np.degrees(np.arctan2(-c[4][0], -c[4][1]))), "movel", None) for c in cx_]
        elif isinstance(pecas, str):
            pecas = {"mesas_redondas": mesas_redondas, "jantar": jantar, "gourmet_cozinha": gourmet_cozinha,
                     "banhos": lambda: []}[pecas]()
        for formas, fontes in zonas:
            z = mascara_formas(formas, forma) & ~par & ~rot & ~manter
            if not z.any():
                continue
            tap = amb.get("tapete")
            if tap:
                dentro = mascara_formas([ret(*tap["caixa"])], forma)
                dentro = cv2.erode(dentro.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
                partes = [(z & dentro, tap["fontes"]), (z & ~dentro, fontes or TRAVERTINO)]
            else:
                partes = [(z, fontes or TRAVERTINO)]
            for i, (zz, ff) in enumerate(partes):
                if tap and i == 0 and zz.any():
                    out = tecido(out, zz, ff, sem)                           # o tapete: a trama, sem a membrana
                    sem += 1
                    continue
                if zz.any():
                    lado = min(min(f[2] - f[0], f[3] - f[1]) for f in ff)
                    p_px = int(max(8, min(PT.PISO_TA["p_px"], lado // 2)))
                    out = PT.piso_refeito(out, zz, sem, q=dict(PT.PISO_TA, fontes_px=ff, p_px=p_px))
                    sem += 1
            if tap:
                # a sombra da borda do tapete de volta onde a zona passou por ela (uma faixa de 3 px por fora, 0,92)
                dentro = mascara_formas([ret(*tap["caixa"])], forma)
                faixa = cv2.dilate(dentro.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~dentro & z
                f = cv2.GaussianBlur(faixa.astype(np.float32), (0, 0), 1.0)
                out = np.clip(np.round(out.astype(np.float32) * (1 - 0.08 * f)[..., None]), 0, 255).astype(np.uint8)
            zona_total |= z
        desenho.append((nome, pecas, manter))
    # as peças, ambiente a ambiente
    o = out.astype(np.float32)
    for nome, pecas, manter in desenho:
        for png, cx, cy, wt, ht, ang, sombra, corte in pecas:
            extra = corte if corte in ("lavabo", "marrom") else None
            P, wt, ht = preparar(png, wt, ht, extra)
            nao = manter | rot | par
            if isinstance(corte, tuple):
                eixo, v, lado = corte
                yy, xx = np.mgrid[0:forma[0], 0:forma[1]]
                c_ = (yy if eixo == "y" else xx) >= v if lado == ">" else (yy if eixo == "y" else xx) <= v
                nao = nao | c_
            o = pousar(o, P, cx, cy, wt, ht, ang, SOMBRAS[sombra], px_m, nao=nao)
            REGISTRO["pecas"].append([png, cx, cy, wt, ht, ang, extra, corte if isinstance(corte, tuple) else None])
            REGISTRO["pecas_m"] |= mascara_formas([caixa_rot(cx, cy, wt, ht, ang, 2)], forma)
        REGISTRO["nao"] |= manter | rot | par
        if nome == "banhos":
            n0 = len(REGISTRO["pecas"])
            o = _banhos(o, px_m, manter | rot | par)
            for _, cx, cy, wt, ht, ang, _, _ in REGISTRO["pecas"][n0:]:
                REGISTRO["pecas_m"] |= mascara_formas([caixa_rot(cx, cy, wt, ht, ang, 2)], forma)
    o, REGISTRO["plantas"] = plantas_de_volta(o, antes, plantas_caixas, px_m)
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    out = beira_da_churrasqueira(out)
    # os tracejados finos de volta por cima, só nas zonas refeitas
    a = (alfa_tr * zona_total)[..., None]
    out = np.clip(np.round(out.astype(np.float32) * (1 - a) + cor_tr[..., None] * a), 0, 255).astype(np.uint8)
    # no 12K, o tapete da varanda inteiro vem da final (a trama igual de ponta a ponta, sem remendos)
    tapete = mascara_formas([ret(*AMBIENTES["varanda_estar"]["tapete"]["caixa"], 2)], forma)
    # e as plantas junto das peças inteiras da final (a IA tinha desenhado outra copa: a emenda cortava a planta)
    plantas = cv2.dilate(REGISTRO["plantas"].astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    REGISTRO["zona"] = (((zona_total | REGISTRO["pecas_m"] | tapete) & ~REGISTRO["nao"]) | plantas) & ~rot & ~par
    print(f"    biblioteca do Térreo: {int(zona_total.sum())} px de piso refeito; "
          f"{sum(len(p) if isinstance(p, list) else 0 for _, p, _ in desenho)} peças fixas mais as do PDF")
    return out


REGISTRO = {}


def plantas_de_volta(o, antes, caixas, px_m):
    """As plantas em vaso (nas caixas) da final de antes por cima de tudo: o alfa pelo verde das folhas
    (G - (R + B) / 2), com a sombra curta delas."""
    H, W = o.shape[:2]
    alfa = np.zeros((H, W), np.float32)
    I = antes.astype(np.float32)
    for x0, y0, x1, y1 in caixas:
        x0, y0, x1, y1 = int(x0), int(y0), int(np.ceil(x1)), int(np.ceil(y1))
        b, g, r = I[y0:y1, x0:x1, 0], I[y0:y1, x0:x1, 1], I[y0:y1, x0:x1, 2]
        a = np.clip((g - (r + b) / 2 - 4) / 14, 0, 1)
        a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        alfa[y0:y1, x0:x1] = np.maximum(alfa[y0:y1, x0:x1], a)
    sh = cv2.GaussianBlur(alfa, (0, 0), 0.03 * px_m)
    sh = cv2.warpAffine(sh, np.float32([[1, 0, -0.03 * px_m], [0, 1, 0.03 * px_m]]), (W, H))
    o = o * (1 - 0.25 * sh)[..., None]
    o = o * (1 - alfa[..., None]) + I * alfa[..., None]
    return o, alfa > 0.05


def beira_da_churrasqueira(out, y=(1438, 1445), x=(1506, 1600), ref=(1600, 1645)):
    """A beira clara da grelha antiga (encostada na parede) sai: nessas linhas, o px claro volta ao tom da mesma linha
    fora da grelha."""
    for yy in range(*y):
        med = np.median(out[yy, ref[0]:ref[1]].astype(np.float32), axis=0)
        seg = out[yy, x[0]:x[1]]
        claro = seg.astype(np.int16).min(axis=1) > 120
        seg[claro] = np.round(med).astype(np.uint8)
    return out
REG_JSON = R / "POE642_CasaA_PH_Terreo_12K_biblioteca.json"
REG_MASC = R / "POE642_CasaA_PH_Terreo_12K_biblioteca_zona.png"       # azul: a zona refeita; verde: o que não muda


def salvar_registro():
    import json
    REG_JSON.write_text(json.dumps({"pecas": REGISTRO["pecas"]}, ensure_ascii=False, indent=0))
    m = np.zeros(REGISTRO["zona"].shape + (3,), np.uint8)
    m[..., 0] = REGISTRO["zona"] * 255
    m[..., 1] = REGISTRO["nao"] * 255
    cv2.imwrite(str(REG_MASC), m)


def pecas_12k(final, entrada, out, s, X0, Yia, Ya3, px_m=59.70590031258779):
    """As peças da biblioteca no 12K (`ampliacao_12k_terreo_casaa.montar12k`, antes dos tracejados e dos textos): na
    zona refeita, a final nova (sem os rótulos: ali vale a entrada da IA) ampliada em Lanczos sobre a saída da IA; por
    cima, cada peça nítida, do PNG na escala do 12K (a sombra já vem da final ampliada)."""
    import json
    if not REG_JSON.exists():
        return out
    reg = json.loads(REG_JSON.read_text())
    mk = cv2.imread(str(REG_MASC))
    zona, nao = mk[..., 0] > 127, mk[..., 1] > 127
    H, W = out.shape[:2]
    eh, ew = entrada.shape[:2]
    B = final.copy()
    B[Yia:Yia + eh, X0:X0 + ew][~zona[Yia:Yia + eh, X0:X0 + ew]] = entrada[~zona[Yia:Yia + eh, X0:X0 + ew]]
    n, lab, st, _ = cv2.connectedComponentsWithStats(zona.astype(np.uint8))
    for i in range(1, n):
        x, y, w, h = st[i, :4]
        fx0, fy0, fx1, fy1 = max(x - 8, 0), max(y - 8, 0), min(x + w + 8, final.shape[1]), min(y + h + 8,
                                                                                            final.shape[0])
        U0, V0 = max(int(np.floor((fx0 - X0) * s)), 0), max(int(np.floor((fy0 - Ya3) * s)), 0)
        U1, V1 = min(int(np.ceil((fx1 - X0) * s)), W), min(int(np.ceil((fy1 - Ya3) * s)), H)
        if U1 <= U0 or V1 <= V0:
            continue
        Mw = np.array([[1 / s, 0, U0 / s + X0 - fx0], [0, 1 / s, V0 / s + Ya3 - fy0]], np.float64)
        src = cv2.warpAffine(B[fy0:fy1, fx0:fx1], Mw, (U1 - U0, V1 - V0),
                             flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        src = src.astype(np.float32)
        src = src + 0.4 * (src - cv2.GaussianBlur(src, (0, 0), 0.6 * s))
        z = (lab[fy0:fy1, fx0:fx1] == i).astype(np.float32)
        al = cv2.warpAffine(z, Mw, (U1 - U0, V1 - V0), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        al = np.clip(cv2.GaussianBlur(al, (0, 0), 0.7 * s), 0, 1)[..., None]
        r = out[V0:V1, U0:U1].astype(np.float32)
        out[V0:V1, U0:U1] = np.clip(np.round(r * (1 - al) + src * al), 0, 255).astype(np.uint8)
    out = bancadas_12k(out, s, X0, Ya3)
    for png, cx, cy, wt, ht, ang, extra, corte in reg["pecas"]:
        if isinstance(png, list):
            P = chuveiro_braco(tuple(png[1]), (png[2][0], png[2][1]), 14.0)[0]
        else:
            P = preparar(png, wt, ht, extra)[0]

        def nao_fn(xa, ya, xb, yb, corte=corte):
            fy = np.clip(np.floor(np.arange(ya, yb) / s + Ya3).astype(int), 0, nao.shape[0] - 1)
            fx = np.clip(np.floor(np.arange(xa, xb) / s + X0).astype(int), 0, nao.shape[1] - 1)
            m = nao[fy[:, None], fx[None, :]]
            if corte:
                eixo, v, lado = corte
                cont = (np.arange(ya, yb) / s + Ya3)[:, None] if eixo == "y" else (np.arange(xa, xb) / s + X0)[None]
                m = m | ((cont >= v) if lado == ">" else (cont <= v))
            return m
        out = pousar(out, P, (cx - X0) * s, (cy - Ya3) * s, wt * s, ht * s, ang, [], px_m * s, nao=nao_fn)
    out = beira_da_churrasqueira_12k(out, s, X0, Ya3)
    print(f"    biblioteca no 12K: {len(reg['pecas'])} peças nítidas sobre a zona refeita")
    return out


# as bancadas de granito e de Dekton onde saíram a grelha e os cooktops antigos: no 12K, o tecido do próprio granito da
# saída da IA (a final ampliada é lisa demais ao lado do pontilhado da IA), no tom do entorno, com a beira suave
BANCADAS_12K = [((1511, 1400, 1594, 1443), [(1600, 1402, 1640, 1438), (1650, 1402, 1690, 1438)]),
                ((1610, 1296, 1666, 1330), [(1575, 1296, 1606, 1330), (1670, 1296, 1700, 1330)]),
                ((1965, 1283, 2021, 1316), [(1940, 1288, 1963, 1314), (2024, 1288, 2046, 1314)])]


def bancadas_12k(out, s, X0, Ya3, q=None):
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import texturas
    q = q or BANCADAS_12K
    H, W = out.shape[:2]

    def caixa(r):
        return (max(int(np.floor((r[0] - X0) * s)), 0), max(int(np.floor((r[1] - Ya3) * s)), 0),
                min(int(np.ceil((r[2] - X0) * s)), W), min(int(np.ceil((r[3] - Ya3) * s)), H))
    for i, (zr, fontes) in enumerate(q):
        u0, v0, u1, v1 = caixa(zr)
        fs = []
        for f in fontes:
            a, b, c, d = caixa(f)
            fs += [out[b:d, a:c].copy(), np.ascontiguousarray(out[b:d, a:c][:, ::-1])]
        lado = min(min(f.shape[:2]) for f in fs)
        p = int(max(16, min(48, lado // 2)))
        tec = texturas.quilting(fs, v1 - v0, u1 - u0, p=p, sobra=max(4, p // 3),
                                rng=np.random.default_rng(5200 + i))[:v1 - v0, :u1 - u0].astype(np.float32)
        med_f = np.median(np.concatenate([f.reshape(-1, 3) for f in fs]).astype(np.float32), axis=0)
        tec += med_f - np.median(tec.reshape(-1, 3), axis=0)
        al = np.zeros((v1 - v0, u1 - u0), np.float32)
        b_ = int(round(1.2 * s))
        al[b_:-b_, b_:-b_] = 1
        al = cv2.GaussianBlur(al, (0, 0), 0.6 * s)[..., None]
        reg = out[v0:v1, u0:u1].astype(np.float32)
        out[v0:v1, u0:u1] = np.clip(np.round(reg * (1 - al) + tec * al), 0, 255).astype(np.uint8)
    return out


def beira_da_churrasqueira_12k(out, s, X0, Ya3, y=(1437.0, 1446.0), x=(1506.0, 1600.0), ref=(1600.0, 1645.0)):
    """A beira clara da grelha antiga junto à parede, na saída da IA: o px claro volta ao tom da mesma linha fora dela."""
    v0, v1 = int(np.floor((y[0] - Ya3) * s)), int(np.ceil((y[1] - Ya3) * s))
    u0, u1 = int(np.floor((x[0] - X0) * s)), int(np.ceil((x[1] - X0) * s))
    r0, r1 = int(np.floor((ref[0] - X0) * s)), int(np.ceil((ref[1] - X0) * s))
    for vv in range(v0, v1):
        med = np.median(out[vv, r0:r1].astype(np.float32), axis=0)
        seg = out[vv, u0:u1]
        claro = seg.astype(np.int16).min(axis=1) > 110
        seg[claro] = np.round(med).astype(np.uint8)
    return out


def _banhos(o, px_m, nao):
    # o chuveiro quadrado com o braço até a parede: banho varanda (parede à direita) e banho do motorista (parede no alto)
    for placa, parede in (((1675.0, 1597.0), (1697.5, "dir")), ((2277.5, 1226.0), (1215.0, "cima"))):
        P, cx, cy, wt, ht, ang = chuveiro_braco(placa, parede, 14.0)
        o = pousar(o, P, cx, cy, wt, ht, ang, SOMBRAS["baixa"], px_m, nao=nao)
        REGISTRO["pecas"].append([["chuveiro", list(placa), list(parede)], cx, cy, wt, ht, ang, None, None])
    # o banho do motorista: o vaso e a cuba (a louça da cuba compacta, sem a pedra bege, na bancada de granito)
    for png, cx, cy, wt, ht, extra, sombra in (
            ("banho-do-motorista/bacia-monte-carlo-sem-valvula", 2320.05, 1232.55, 22.5, 32.7, None, "baixa"),
            ("banho-do-motorista/cuba-compacta", 2363.5, 1235.5, 24.0, None, "louca", None),
            ("quarto-do-motorista/cama-solteiro-a", 2421.3, 1175.5, 53.7, 113.4, None, "movel")):
        P, wt, ht = preparar(png, wt, ht, extra)
        o = pousar(o, P, cx, cy, wt, ht, 0.0, SOMBRAS[sombra], px_m, nao=nao)
        REGISTRO["pecas"].append([png, cx, cy, wt, ht, 0.0, extra, None])
    return o


# ----------------------------------------------------------------------------------------------------------------------
ANTES_DEPOIS = {"varanda_estar": (1570, 340, 1860, 600), "sala_estar": (1860, 340, 2190, 640),
                "estar_projecao": (1670, 640, 2130, 850), "mesas_redondas": (1570, 840, 1800, 1240),
                "jantar": (1880, 880, 2160, 1120), "escritorio": (2330, 350, 2610, 620),
                "gourmet_cozinha": (1480, 1200, 2170, 1520), "lounge_brises": (1180, 1180, 1490, 1660),
                "piscina": (1320, 500, 1500, 740), "banhos_motorista": (1580, 1460, 2560, 1320 + 300)}


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(3.0, 1100 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        for im, t in ((a, "ANTES"), (b, "DEPOIS")):
            cv2.putText(im, t, (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 5)
            cv2.putText(im, t, (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (30, 30, 30), 2)
        M = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), b])
        p = R / f"POE642_CasaA_PH_Terreo_1211b_{nome}_antes_depois.jpg"
        cv2.imwrite(str(p), M, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {p.name}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes", type=Path)
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    if a.antes:
        antes = cv2.imread(str(a.antes))
    else:
        dado = subprocess.run(["git", "show", f"{ANTES_COMMIT}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"],
                              cwd=RAIZ_GIT, capture_output=True, check=True).stdout
        antes = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    print("[Térreo] as peças da biblioteca")
    out = aplicar(antes)
    saida = a.saida or FINAL
    cv2.imwrite(str(saida), out)
    print(f"    {saida}; {int((out != antes).any(axis=2).sum())} px mudaram")
    if not a.saida:
        salvar_registro()
        antes_depois(antes, out)


if __name__ == "__main__":
    main()

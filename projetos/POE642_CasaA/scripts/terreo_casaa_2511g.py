"""Casa A Térreo, 7ª leva de 25/11 (os recortes do 12K B): a cuba do banho do motorista, as soleiras no travertino, as
manchas do piso (hall, escritório, gourmet, lavatório, escada do jardim, área de serviço, despensa), os tracejados da
projeção do pavimento superior e as folhas de duas portas.

- **Cuba do banho do motorista** ("corrija essa cuba"): a louça vinha recortada com a borda borrada (sem a cuba funda,
  sem a borda) e um halo claro no granito. A bancada do PDF (2342,6 a 2384,4 x 1216,1 a 1240,0) de novo no granito
  marrom da gourmet (`terreo_casaa_2511d.gourmet`: o mesmo tom, o mosqueado e os pontinhos, o contorno fino); por cima,
  a louça da `banho-do-motorista/cuba-compacta.png` (só a louça e a torneira, a borda nítida) no lugar da instalação,
  com a sombra curta; o piso embaixo da bancada (onde a louça antiga passava) refeito, o rótulo por cima.
- **Soleiras** ("altere as soleiras para um tom mais escuro do travertino, não é bege bahia"): todas as que estavam no
  bege (GÁS, a porta de correr e as janelas do WC e do banho varanda; a porta e a janela do lavabo; a porta e as
  janelas do escritório) no travertino do piso a 84%, o veio ao comprido da soleira, o contorno fino um tom abaixo; as
  folhas e os tocos de parede de volta por cima.
- **Manchas** ("remova a mancha em volta da parede", "corrija essas manchas em volta da bancada e parede", "corrija
  também essa mancha", "corrija essas manchas no piso também", "corrija esses erros no piso, tanto em frente as
  maquinas quanto atras da porta"): o piso refeito com a luz do piso em volta, até as paredes, as bancadas e as peças
  (sem emenda ali; a emenda suave só no piso aberto): a ponta da parede de baixo do escritório; a faixa cinza à
  esquerda da bancada gourmet e do lavatório, a ponta da parede do lavatório e o toco da direita; a faixa à esquerda do
  guarda-corpo da escada do jardim (o rótulo SALA DE JANTAR por cima); no piso marrom (a trama do próprio piso, por
  image quilting de um trecho limpo), o retângulo claro em volta das máquinas de lavar e o de trás da porta da área de
  serviço.
- **Projeção do pavimento superior** ("remova esses erros no piso"): no canto do tracejado (a seta grossa onde as três
  linhas se encontram), os restos do texto apagado (os quadradinhos) e a mancha junto ao armário: o piso refeito e os
  traços do PDF redesenhados finos (0,55 px, o cinza dos outros tracejados).
- **Portas**: a folha comprida de baixo do escritório ("corrija a falha na porta, mantendo o mesmo tom sobre ela do
  início ao fim") redesenhada inteira no padrão das folhas (opaca, o mesmo tom do começo ao fim); a da despensa ("corrija
  a representação aqui também"), que tinha a borda serrilhada e a mancha escura ao lado, com o piso marrom refeito em
  volta e a folha e o batente redesenhados.

Final, prancha e 12K A e B.

  python3 terreo_casaa_2511g.py [item ...]
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
import terreo_casaa_2511e as E       # noqa: E402

PLANTA = "A_Terreo"
PX_M_ = 59.70590031258779
MARROM_FONTE = (1925.0, 1467.0, 1978.0, 1486.0)       # o piso marrom limpo da área de serviço (acima do SOBE)


# ----------------------------------------------------------------------------------------------------------------------
def _pena(jan, s, origem, r, lados, pena):
    """A cobertura do retângulo r com a emenda suave (pena, px da final) só nos lados abertos ('l', 't', 'r', 'b')."""
    a = V.cob([V.ret(*r)], jan, s, origem)
    xs, ys = V.coords(jan, s, origem)
    fx = np.ones_like(xs)
    fy = np.ones_like(ys)
    if "l" in lados:
        fx = np.minimum(fx, np.clip((xs - r[0]) / pena, 0, 1))
    if "r" in lados:
        fx = np.minimum(fx, np.clip((r[2] - xs) / pena, 0, 1))
    if "t" in lados:
        fy = np.minimum(fy, np.clip((ys - r[1]) / pena, 0, 1))
    if "b" in lados:
        fy = np.minimum(fy, np.clip((r[3] - ys) / pena, 0, 1))
    return a * fy[:, None] * fx[None, :]


def _quilt(img, s, origem, fonte, H, W, semente=3):
    sys.path.insert(0, str(EP.PROJ / "_texturas"))
    import texturas
    X0, Y0, X1, Y1 = V.janela(img, fonte, s, origem, folga=0)
    F = img[Y0:Y1, X0:X1]
    lisa = cv2.GaussianBlur(F.astype(np.float32), (0, 0), 5.0 * s)
    Fd = np.clip(F.astype(np.float32) / np.maximum(lisa, 1) * F.reshape(-1, 3).mean(0), 0, 255).astype(np.uint8)
    p = max(6, int(round(7 * s)))
    return texturas.quilting([Fd, np.ascontiguousarray(Fd[:, ::-1]), np.ascontiguousarray(Fd[::-1])], H, W, p=p,
                             sobra=max(3, p // 3), rng=np.random.default_rng(semente))[:H, :W].astype(np.float32)


def refazer(img, s, origem, zonas, objetos=(), textura="trav", sombra=0.10, letras=False, tol=0.08, luz_sig=10.0,
            pena=3.0):
    """O piso de novo nas zonas [(retângulo, lados abertos)], menos os objetos (retângulos), com a luz do piso em volta
    (o valor mais frequente da razão imagem/textura, alisado). textura: 'trav' (o travertino) ou ('quilt', fonte)."""
    rets = [z[0] for z in zonas] + list(objetos)
    x0 = min(r[0] for r in rets)
    y0 = min(r[1] for r in rets)
    x1 = max(r[2] for r in rets)
    y1 = max(r[3] for r in rets)
    jan = V.janela(img, (x0, y0, x1, y1), s, origem, folga=int(6 * s) + 2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    az = np.zeros((H, W), np.float32)
    dentro = np.zeros((H, W), np.float32)
    for r, lados in zonas:                         # a soma (as zonas vizinhas sem a fresta na divisa)
        az = np.clip(az + _pena(jan, s, origem, r, lados, pena), 0, 1)
        dentro = np.clip(dentro + V.cob([V.ret(*r)], jan, s, origem), 0, 1)
    ao = V.cob([V.ret(*r) for r in objetos], jan, s, origem) if objetos else np.zeros((H, W), np.float32)
    if textura == "trav":
        TT = D.piso_tt(jan, s)
    else:
        TT = _quilt(img, s, origem, textura[1], H, W)
    Lr = reg.mean(2)
    r_ = Lr / np.maximum(TT.mean(2), 1.0)
    livre = (dentro > 0.99) & (ao < 0.01)
    h, e = np.histogram(r_[livre], bins=80, range=(0.6, 1.4))
    h = np.convolve(h, np.ones(5) / 5, mode="same")
    med = float(e[np.argmax(h)] + (e[1] - e[0]) / 2)
    ok = livre & (np.abs(r_ - med) < tol)
    sig = luz_sig * s
    num = cv2.GaussianBlur(np.where(ok, r_, 0).astype(np.float32), (0, 0), sig)
    den = cv2.GaussianBlur(ok.astype(np.float32), (0, 0), sig)
    luz = np.where(den > 1e-3, num / np.maximum(den, 1e-3), med)
    novo = TT * luz[..., None]
    if objetos and sombra:
        Ms = np.float32([[1, 0, 0.7 * s], [0, 1, 0.9 * s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(ao, Ms, (W, H)), (0, 0), max(1.1 * s, 0.6)) * (1 - ao)
        novo *= (1 - sombra * sb)[..., None]
    a = az * (1 - ao)
    out = reg * (1 - a[..., None]) + novo * a[..., None]
    if letras:
        z = (dentro > 0.5) & (ao < 0.5)
        at, cor = V.letras(reg, z, escala=s, ref=float(np.median(Lr[livre])), dif=80.0, piso_dif=30.0, area_min=0.8)
        out = V.compor(out, at, cor)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Soleiras no travertino mais escuro
SOLEIRA_T = dict(escurecer=0.84, contorno=0.70, larg=0.22)


def soleira_trav(img, s, origem, rets, cantos=(), q=SOLEIRA_T):
    for r in rets:
        giro = (r[3] - r[1]) > (r[2] - r[0])           # a vertical com o veio na vertical
        jan = V.janela(img, r, s, origem, folga=2)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1].astype(np.float32)
        pedra = D.piso_tt(jan, s, giro=giro) * q["escurecer"]
        a = V.cob([V.ret(*r)], jan, s, origem)
        e = q["larg"]
        d = V.cob([V.ret(r[0] + e, r[1] + e, r[2] - e, r[3] - e)], jan, s, origem)
        reg = V.compor(reg, a, pedra)
        reg = V.compor(reg, np.clip(a - d, 0, 1), pedra * q["contorno"])
        img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    if cantos:
        img = D.pintar_rets(img, s, origem, list(cantos), (53, 53, 53))
    return img


def soleiras_servico(img, s, origem):
    for q in D.SOLEIRAS.values():
        img = soleira_trav(img, s, origem, q["rets"], q["cantos"])
        img = D.folhas(img, s, origem, q["folhas"])
    return img


LAVABO_SOL = dict(porta=(2263.0, 514.5, 2320.1, 523.5))


def soleiras_lavabo(img, s, origem):
    q = D.LAVABO
    img = soleira_trav(img, s, origem, [LAVABO_SOL["porta"]])
    img = soleira_trav(img, s, origem, [q["jan_soleira"]])
    return D.folhas(img, s, origem, q["jan_folhas"])


def soleiras_escritorio(img, s, origem):
    q = D.ESCRITORIO
    img = soleira_trav(img, s, origem, q["soleiras"])
    return D.folhas(img, s, origem, q["folhas"])


# a ponta da parede de baixo do escritório, do lado do hall (a mancha em volta)
def mancha_escritorio(img, s, origem):
    return refazer(img, s, origem, [((2328.0, 586.0, 2345.2, 624.0), "ltb"), ((2345.2, 610.3, 2380.0, 624.0), "rb")])


# ----------------------------------------------------------------------------------------------------------------------
# Cuba do banho do motorista
MOTORISTA = dict(bancada=(2342.6, 1216.1, 2384.4, 1240.0), piso=(2342.8, 1240.0, 2384.2, 1256.5),
                 cuba=("banho-do-motorista/cuba-compacta", 2363.5, 1235.5, 24.0))


def _louca(P, croma=24):
    """A louça (o branco e o cromado, pouco croma) da cuba da biblioteca, sem a pedra bege, com a borda nítida."""
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
    Q[..., 3] = cv2.GaussianBlur(Q[..., 3], (0, 0), 0.6)
    return np.ascontiguousarray(Q)


def cuba_motorista(img, s, origem, q=MOTORISTA):
    B = E._b1211()
    # o piso embaixo da bancada (onde a louça antiga passava)
    img = refazer(img, s, origem, [(q["piso"], "lb")], letras=True)
    # a bancada no granito marrom da gourmet
    x0, y0, x1, y1 = q["bancada"]
    g = dict(D.GOURMET, u=[(x0, y0), (x1, y0), (x1, y1), (x0, y1)], pecas=[],
             banquetas=(x0, y0 - 2.0, x0 + 1.0, y0 - 1.0), sombra_banq=0.0)
    img = D.gourmet(img, s, origem, g)
    # a louça da biblioteca, nítida, com a sombra curta
    nome, cx, cy, w = q["cuba"]
    P = _louca(B.ler_png(nome))
    ht = w * P.shape[0] / P.shape[1]
    jan = V.janela(img, (cx - w, cy - ht, cx + w, cy + ht), s, origem, folga=4)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    B.pousar(reg, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, w * s, ht * s, 0.0, B.SOMBRAS["baixa"],
             PX_M_ * s)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Projeção do pavimento superior: o canto do tracejado
# Os oito cantos dos dois X de projeção (sala de estar 1878,6-2151,4 e varanda 1512,5-1873,5, de 610,1 a 878,8): a seta
# grossa no vértice e os quadradinhos (restos de texto) saem; o tracejado do PDF volta fino. Sem tocar no filete (1512,5)
# nem no vidro entre a varanda e a sala (1873,5-1878,6).
PROJ_CANTOS = [
    [((2090.0, 593.0, 2160.0, 641.0), "ltrb"), ((2160.0, 610.6, 2201.0, 624.0), "lrb")],   # sala, cima à direita
    [((1879.0, 595.0, 1906.0, 634.0), "trb")],                                              # sala, cima à esquerda
    [((1879.0, 856.0, 1910.0, 893.0), "trb")],                                              # sala, baixo à esquerda
    [((2118.0, 836.0, 2180.0, 899.0), "ltrb")],                                             # sala, baixo à direita
    [((1513.3, 594.0, 1542.0, 633.0), "trb")],                                              # varanda, cima à esquerda
    [((1835.0, 585.0, 1873.0, 634.0), "ltb")],                                              # varanda, cima à direita
    [((1513.3, 856.0, 1540.0, 900.0), "trb")],                                              # varanda, baixo à esquerda
    [((1835.0, 855.0, 1873.0, 898.0), "ltb")]]                                              # varanda, baixo à direita
# o traço como o tracejado que fica (medido: 2 px a 141 na final; ~0,8 px da final a 117 no 12K)
PROJECAO = dict(cantos=PROJ_CANTOS, larg=0.78, cor=(117, 117, 117), larg_final=2.0, cor_final=(141, 141, 141))
_SEG = {}


def _segmentos():
    """As linhas da camada de projeções do PDF (px da final)."""
    if "s" not in _SEG:
        Q = EP.quadro(PLANTA)
        out = []
        for d in Q.desenhos:
            if "PROJE" not in (d["layer"] or "") or d["type"] != "s":
                continue
            for it in d["items"]:
                if it[0] == "l":
                    out.append((tuple(Q.p2q(it[1].x, it[1].y)), tuple(Q.p2q(it[2].x, it[2].y))))
        _SEG["s"] = out
    return _SEG["s"]


def projecao(img, s, origem, q=PROJECAO):
    for zonas in q["cantos"]:
        img = refazer(img, s, origem, zonas)
        caixa = (min(z[0][0] for z in zonas), min(z[0][1] for z in zonas),
                 max(z[0][2] for z in zonas), max(z[0][3] for z in zonas))
        jan = V.janela(img, caixa, s, origem, folga=2)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1].astype(np.float32)
        dentro = np.zeros(reg.shape[:2], np.float32)
        for r, _ in zonas:
            dentro = np.maximum(dentro, V.cob([V.ret(*r)], jan, s, origem))
        a = np.zeros(reg.shape[:2], np.float32)
        for p, r in _segmentos():
            if (max(p[0], r[0]) < caixa[0] - 1 or min(p[0], r[0]) > caixa[2] + 1 or
                    max(p[1], r[1]) < caixa[1] - 1 or min(p[1], r[1]) > caixa[3] + 1):
                continue
            a = np.maximum(a, V.cob([V.seg(p, r, q["larg"] if s > 1.5 else q["larg_final"])], jan, s, origem))
        reg = V.compor(reg, a * dentro, q["cor"] if s > 1.5 else q["cor_final"])
        img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Portas
PORTA_LONGA = dict(folha=(2288.4, 684.1, 2484.3, 687.1), sobras=[((2286.0, 682.0, 2487.0, 684.1), (0.0, -3.2)),
                                                                   ((2286.0, 687.1, 2487.0, 690.6), (0.0, 3.8))])


def porta_longa(img, s, origem, q=PORTA_LONGA):
    for r, d in q["sobras"]:                      # a folha antiga (um pouco mais larga) sai: o piso do lado
        img = D.copiar(img, s, origem, r, d)
    return D.folhas(img, s, origem, [q["folha"]])


DESPENSA = dict(
    # o piso marrom: acima da ponta da parede (o resto do batente da porta de serviço), ao lado do toco e atrás da folha
    zonas=[((2035.5, 1504.0, 2060.0, 1514.7), "ltr"), ((2049.9, 1514.7, 2060.0, 1520.6), "r"),
           ((2050.2, 1529.8, 2070.0, 1578.0), "rb"), ((2057.0, 1520.6, 2070.0, 1529.8), "r")],
    # sem batente (R 406): a parede de cima a baixo, copiada da própria parede mais abaixo (o mesmo contorno e a sombra)
    parede=((2040.2, 1514.7, 2050.6, 1536.0), (0.0, 28.0)),
    topo=((2040.9, 1514.7), (2049.9, 1514.7)),               # a ponta reta, na linha da folha fechada da porta de serviço
    # o toco até a face da folha, copiado da parede de cima da despensa (mesma espessura, 1520,6 a 1529,6)
    toco=((2049.0, 1520.2, 2057.3, 1530.0), (2106.0 - 2049.0, 0.0)),
    toco_fim=((2057.3, 1520.6), (2057.3, 1529.6)),
    # do outro lado, a ponta da parede de cima vai até a ponta da folha fechada (2099,1)
    ponta=((2095.5, 1517.0, 2103.0, 1533.0), (3.0, 0.0)),
    folhas=[(2057.3, 1529.6, 2059.7, 1571.4)],
    contorno=dict(larg=0.62, cor=(34.0, 34.0, 36.0)))


def _colar(img, s, origem, r, d, lados="", pena=1.2):
    """O retângulo r recebe a imagem deslocada d (px da final), com a emenda suave só nos lados de lados."""
    jan = V.janela(img, r, s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    dx, dy = int(round(d[0] * s)), int(round(d[1] * s))
    fonte = img[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    a = _pena(jan, s, origem, r, lados, pena) if lados else V.cob([V.ret(*r)], jan, s, origem)
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + fonte * a[..., None]), 0, 255).astype(np.uint8)
    return img


def _traco(img, s, origem, p, q, larg, cor):
    jan = V.janela(img, (min(p[0], q[0]) - 1, min(p[1], q[1]) - 1, max(p[0], q[0]) + 1, max(p[1], q[1]) + 1),
                   s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    reg = V.compor(reg, V.cob([V.seg(p, q, larg)], jan, s, origem), cor)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def despensa(img, s, origem, q=DESPENSA):
    img = refazer(img, s, origem, q["zonas"], textura=("quilt", MARROM_FONTE))
    img = _colar(img, s, origem, *q["parede"], lados="b", pena=1.5)
    img = _colar(img, s, origem, *q["toco"])
    img = _colar(img, s, origem, *q["ponta"], lados="ltb", pena=1.5)
    c = q["contorno"]
    img = _traco(img, s, origem, *q["topo"], c["larg"], c["cor"])
    img = _traco(img, s, origem, *q["toco_fim"], c["larg"], c["cor"])
    return D.folhas(img, s, origem, q["folhas"])


SERVICO = dict(maquinas=(1828.6, 1452.6, 1924.0, 1506.0), maquinas_obj=(1829.0, 1454.9, 1918.5, 1496.7),
               porta_zona=(1972.0, 1452.6, 2040.6, 1472.0), porta=(1987.2, 1460.9, 2040.9, 1463.3))


def servico_piso(img, s, origem, q=SERVICO):
    img = refazer(img, s, origem, [(q["maquinas"], "rb")], objetos=[q["maquinas_obj"]],
                  textura=("quilt", MARROM_FONTE), sombra=0.16)
    img = refazer(img, s, origem, [(q["porta_zona"], "lb")], textura=("quilt", MARROM_FONTE))
    return D.folhas(img, s, origem, [q["porta"]])


# ----------------------------------------------------------------------------------------------------------------------
# Manchas no travertino junto às bancadas, às paredes e ao guarda-corpo
def gourmet_manchas(img, s, origem):
    img = refazer(img, s, origem, [((1452.0, 1262.0, 1476.6, 1514.0), "ltb"),
                                   ((1476.6, 1496.8, 1500.0, 1514.0), "rb")])
    return refazer(img, s, origem, [((1594.0, 1484.0, 1608.0, 1508.0), "ltb"),
                                    ((1608.0, 1494.6, 1617.4, 1508.0), "b")])


def escada_manchas(img, s, origem):
    return refazer(img, s, origem, [((2224.0, 893.0, 2243.7, 1108.0), "ltb")], letras=True)


ITENS = {"cuba_motorista": (2330.0, 1205.0, 2395.0, 1265.0),
         "soleiras_servico": (1540.0, 1625.0, 1915.0, 1650.0),
         "soleiras_lavabo": (2255.0, 340.0, 2340.0, 530.0),
         "soleiras_escritorio": (2335.0, 335.0, 2610.0, 600.0),
         "mancha_escritorio": (2320.0, 580.0, 2380.0, 630.0),
         "porta_longa": (2280.0, 670.0, 2490.0, 700.0),
         "despensa": (2030.0, 1500.0, 2110.0, 1580.0),
         "servico_piso": (1820.0, 1445.0, 2050.0, 1510.0),
         "gourmet_manchas": (1450.0, 1255.0, 1625.0, 1515.0),
         "escada_manchas": (2220.0, 888.0, 2262.0, 1112.0)}
for _k, _zs in enumerate(PROJ_CANTOS):         # um item por canto (o registro do 12K local)
    ITENS[f"projecao_{_k + 1}"] = (min(z[0][0] for z in _zs) - 4, min(z[0][1] for z in _zs) - 4,
                                   max(z[0][2] for z in _zs) + 4, max(z[0][3] for z in _zs) + 4)
FUNC = {"cuba_motorista": cuba_motorista, "soleiras_servico": soleiras_servico, "soleiras_lavabo": soleiras_lavabo,
        "soleiras_escritorio": soleiras_escritorio, "mancha_escritorio": mancha_escritorio,
        "porta_longa": porta_longa, "despensa": despensa, "servico_piso": servico_piso,
        "gourmet_manchas": gourmet_manchas, "escada_manchas": escada_manchas}
for _k, _zs in enumerate(PROJ_CANTOS):
    FUNC[f"projecao_{_k + 1}"] = (lambda zs: lambda img, s, origem: projecao(img, s, origem, dict(PROJECAO, cantos=[zs])))(_zs)


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
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

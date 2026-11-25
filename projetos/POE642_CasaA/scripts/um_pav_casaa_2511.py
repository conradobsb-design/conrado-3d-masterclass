"""Casa A 1º Pavimento, levantamento de 25/11 ("ok, pode aplicar os 4"; a folha em
`renders/POE642_CasaA_PH_1Pavimento_2511_levantamento.jpg`).

1. **Vasos sanitários** (Banho 1, 2, 3 e o WC do Banho Master): o vaso vinha quebrado (o contorno solto, o miolo
   cortado). O piso de travertino refeito na pegada (até a parede atrás do vaso) e a bacia Carrara da biblioteca
   (`03-primeiro-pavimento/banho-*/bacia-carrara`) de novo, na pose da instalação (`biblioteca_1pav_casaa_1211`), com a
   sombra rente.
2. **Aparadores com a TV** (Suíte Master e Suíte 3): o aparador vinha translúcido e a TV borrada. O aparador do PDF em
   madeira sólida (a bancada das suítes da biblioteca, como na Suíte 2), o piso vinílico refeito onde o translúcido
   passava do aparador e, na Suíte 3, a escrivaninha de volta onde ele a cobria; a TV desenhada nítida (o corpo
   grafite, o fio claro da frente, a sombra curta): na Suíte Master e na Suíte 2 no retângulo do PDF, na Suíte 3 (sem
   TV no PDF) sobre o aparador, o mais perto do eixo da cama.
3. **Sala íntima**: a mesa de centro de nogueira com a borda nítida (o tampo da própria imagem, sem a borda borrada,
   no retângulo da mesa, com a sombra das mesas), o tapete refeito no anel borrado em volta; o resto de contorno
   cinza na ponta do sofá sai (o travertino com a luz do piso em volta).
4. **Vão na parede junto à escada** (2545,5 a 2760,4 x 890,7 a 902,6): o miolo com ruído; o vão como os outros
   (o claro liso, o contorno fino preto e o X tracejado fino do PDF).

Final, prancha e 12K A e B.

  python3 um_pav_casaa_2511.py [item ...]
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
import terreo_casaa_2511g as G       # noqa: E402

PLANTA = "A_1Pavimento"
PX_M_ = 59.70590031258779


def _bib():
    with contextlib.redirect_stdout(io.StringIO()):
        import biblioteca_1pav_casaa_1211 as P1
        import biblioteca_terreo_casaa_1211 as BT
    return P1, BT


def _pousar(img, s, origem, nome, cx, cy, w, h, ang, sombra, extra=None, recorte=None):
    """A peça da biblioteca do 1º Pavimento no lugar; com `recorte` (retângulo, px da final), só ali."""
    P1, BT = _bib()
    P, wt, ht = P1.preparar(nome, w, h, extra)
    m = max(wt, ht) * 0.75 + 6
    jan = V.janela(img, (cx - m, cy - m, cx + m, cy + m), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    novo = reg.copy()
    BT.pousar(novo, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, wt * s, ht * s, ang, BT.SOMBRAS[sombra],
              PX_M_ * s)
    if recorte is not None:
        a = V.cob([V.ret(*recorte)], jan, s, origem)[..., None]
        novo = reg * (1 - a) + novo * a
    img[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    return img


def _copiar(img, s, origem, r, d, lados="", pena=1.0):
    """O retângulo r recebe a imagem deslocada d (px da final), com a emenda suave nos lados de `lados`."""
    jan = V.janela(img, r, s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    dx, dy = int(round(d[0] * s)), int(round(d[1] * s))
    fonte = img[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    a = G._pena(jan, s, origem, r, lados, pena) if lados else V.cob([V.ret(*r)], jan, s, origem)
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + fonte * a[..., None]), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os vasos: (zona do piso refeito, lados abertos), a pose da bacia (biblioteca_1pav_casaa_1211)
VASOS = {
    "vaso_banho3": (((2141.0, 371.6, 2169.5, 409.0), "lrb"), ("banho-3/bacia-carrara", 2154.5, 386.5, 21.1, 30.7, 0.0)),
    "vaso_banho2": (((1692.0, 891.2, 1721.5, 929.0), "lrb"), ("banho-2/bacia-carrara", 1706.5, 906.0, 21.1, 30.7, 0.0)),
    "vaso_banho1": (((2499.0, 1196.5, 2533.4, 1228.0), "ltb"),
                    ("banho-1/bacia-carrara", 2518.5, 1210.5, 21.1, 30.7, -90.0)),
    "vaso_master": (((1689.0, 1590.0, 1718.0, 1624.4), "ltr"),
                    ("banho-master/bacia-carrara", 1703.5, 1609.5, 21.1, 30.7, 180.0)),
}


def vaso(img, s, origem, q):
    (zona, lados), (nome, cx, cy, w, h, ang) = q
    img = G.refazer(img, s, origem, [(zona, lados)])
    return _pousar(img, s, origem, nome, cx, cy, w, h, ang, "baixa")


# ----------------------------------------------------------------------------------------------------------------------
# 2. Os aparadores e as TVs
TV = dict(corpo=(34.0, 33.0, 32.0), frente=(78.0, 76.0, 74.0), frente_larg=0.45, sombra=0.28,
          sombra_d=(-0.4, 0.7), sombra_sig=0.6)
APARADORES = {
    # o aparador do PDF (1387,1 a 1625,9 x 1216,1 a 1234,0); o translúcido ia de 1386 a 1625 e até 1236
    "aparador_master": dict(faixas=[((1383.0, 1233.6, 1629.0, 1238.8), (0.0, 7.0), "lrb"),
                                    ((1383.0, 1216.1, 1387.4, 1234.0), (-6.0, 0.0), "lt")],
                            peca=("suite-2/bancada-suites", 1506.5, 1225.05, 238.8, 17.9, 0.0, "baixa"),
                            tv=(1465.7, 1216.1, 1546.2, 1219.1)),
    # o aparador do PDF (1727,5 a 1870,8 x 580,2 a 598,1) por cima da escrivaninha (1624,3 a 1781,2 x 562,3 a 598,1);
    # o translúcido ia de 1703,6; a TV (sem TV no PDF) sobre o aparador, o mais perto do eixo da cama (1742)
    "aparador_suite3": dict(faixas=[((1781.2, 576.5, 1874.0, 580.4), (0.0, -6.0), "lrt"),
                                    ((1870.6, 576.5, 1874.0, 598.1), (5.0, 0.0), "rt")],
                            mesa=(("suite-3/bancada-suites", 1702.5, 580.0, 157.0, 35.8, 0.0, "mesa"),
                                  (1698.0, 568.0, 1730.0, 598.1)),
                            peca=("suite-2/bancada-suites", 1799.15, 589.15, 143.3, 17.9, 0.0, "baixa"),
                            tv=(1730.0, 595.1, 1810.5, 598.1)),
    # a Suíte 2: o aparador de novo (a TV velha, borrada, sai) e a TV nítida no retângulo do PDF
    "aparador_suite2": dict(faixas=[], peca=("suite-2/bancada-suites", 1765.5, 1014.5, 155.2, 14.9, 0.0, "baixa"),
                            tv=(1725.4, 1007.1, 1805.9, 1010.1)),
}


def desenhar_tv(img, s, origem, r, q=TV):
    jan = V.janela(img, (r[0] - 3, r[1] - 3, r[2] + 3, r[3] + 3), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    a = V.cob([V.ret(*r)], jan, s, origem)
    dx, dy = q["sombra_d"]
    sh = V.cob([V.ret(r[0] + dx, r[1] + dy, r[2] + dx, r[3] + dy)], jan, s, origem)
    sh = cv2.GaussianBlur(sh, (0, 0), max(0.5, q["sombra_sig"] * s)) * (1 - a)
    reg *= (1 - q["sombra"] * sh)[..., None]
    reg = V.compor(reg, a, q["corpo"])
    fr = V.cob([V.ret(r[0] + 0.6, r[3] - q["frente_larg"], r[2] - 0.6, r[3])], jan, s, origem)
    reg = V.compor(reg, fr, q["frente"])
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def aparador(img, s, origem, q):
    for r, d, lados in q["faixas"]:
        img = _copiar(img, s, origem, r, d, lados)
    if "mesa" in q:
        (nome, cx, cy, w, h, ang, som), rec = q["mesa"]
        img = _pousar(img, s, origem, nome, cx, cy, w, h, ang, som, recorte=rec)
    nome, cx, cy, w, h, ang, som = q["peca"]
    img = _pousar(img, s, origem, nome, cx, cy, w, h, ang, som)
    return desenhar_tv(img, s, origem, q["tv"])


# ----------------------------------------------------------------------------------------------------------------------
# 3. A sala íntima
MESA = dict(ret=(2054.4, 1042.6, 2094.0, 1120.0), miolo=2.2, anel=2.8)
RESTO_SOFA = [(2156.0, 1159.0, 2182.0, 1180.0)]   # à direita da borda do tapete, abaixo do braço do sofá


def mesa_centro(img, s, origem, q=MESA):
    P1, BT = _bib()
    x0, y0, x1, y1 = q["ret"]
    m = q["miolo"]
    # o tampo: o miolo da própria imagem (sem a borda borrada), esticado ao retângulo da mesa
    X0, Y0, X1, Y1 = V.janela(img, (x0 + m, y0 + m, x1 - m, y1 - m), s, origem, folga=0)
    tampo = img[Y0:Y1, X0:X1].copy()
    # o anel borrado em volta: o tapete de perto (as faixas deslocadas para fora)
    k = q["anel"]
    img = _copiar(img, s, origem, (x0 - k, y0 - k, x1 + k, y0 + 1.2), (0.0, -(k + 4.0)), "lrt", 1.0)
    img = _copiar(img, s, origem, (x0 - k, y1 - 1.2, x1 + k, y1 + k), (0.0, k + 4.0), "lrb", 1.0)
    img = _copiar(img, s, origem, (x0 - k, y0, x0 + 1.2, y1), (-(k + 4.0), 0.0), "ltb", 1.0)
    img = _copiar(img, s, origem, (x1 - 1.2, y0, x1 + k, y1), (k + 4.0, 0.0), "rtb", 1.0)
    P = np.dstack([tampo.astype(np.float32), np.full(tampo.shape[:2], 255.0, np.float32)])
    w, h = x1 - x0, y1 - y0
    jan = V.janela(img, (x0 - 6, y0 - 6, x1 + 6, y1 + 6), s, origem, folga=2)
    J0, K0, J1, K1 = jan
    reg = img[K0:K1, J0:J1].astype(np.float32)
    BT.pousar(reg, P, ((x0 + x1) / 2 - origem[0]) * s - J0, ((y0 + y1) / 2 - origem[1]) * s - K0, w * s, h * s, 0.0,
              BT.SOMBRAS["mesa"], PX_M_ * s)
    # o contorno fino do tampo, um tom abaixo
    a = V.cob([V.ret(x0, y0, x1, y1)], jan, s, origem)
    e = cv2.erode((a > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8))
    borda = ((a > 0.5) & (e == 0)).astype(np.float32) * 0.35
    reg = reg * (1 - borda[..., None]) + (reg * 0.6) * borda[..., None]
    img[K0:K1, J0:J1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def sala_intima(img, s, origem):
    img = mesa_centro(img, s, origem)
    return G.refazer(img, s, origem, [(RESTO_SOFA[0], "rb")])


# ----------------------------------------------------------------------------------------------------------------------
# 4. O vão na parede junto à escada
VAO = dict(ret=(2545.5, 890.7, 2760.4, 902.6), claro=(240.0, 241.0, 241.0), contorno=(40.0, 40.0, 42.0),
           larg=0.5, x_cor=(117.0, 117.0, 117.0), x_larg=0.6, x_cor_final=(160.0, 160.0, 160.0), x_larg_final=0.8)


def vao(img, s, origem, q=VAO):
    r = q["ret"]
    jan = V.janela(img, (r[0] - 1, r[1] - 1, r[2] + 1, r[3] + 1), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    a = V.cob([V.ret(*r)], jan, s, origem)
    reg = V.compor(reg, a, q["claro"])
    Q = EP.quadro(PLANTA)
    xa = np.zeros(reg.shape[:2], np.float32)
    for d in Q.desenhos:
        if "PROJE" not in (d["layer"] or "") or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            p, t = Q.p2q(it[1].x, it[1].y), Q.p2q(it[2].x, it[2].y)
            if min(p[0], t[0]) >= r[0] - 0.5 and max(p[0], t[0]) <= r[2] + 0.5 and \
                    min(p[1], t[1]) >= r[1] - 0.5 and max(p[1], t[1]) <= r[3] + 0.5:
                xa = np.maximum(xa, V.cob([V.seg(p, t, q["x_larg"] if s > 1.5 else q["x_larg_final"])],
                                          jan, s, origem))
    reg = V.compor(reg, xa * a, q["x_cor"] if s > 1.5 else q["x_cor_final"])
    c = q["larg"]
    lados = [V.seg((r[0], r[1]), (r[2], r[1]), c), V.seg((r[0], r[3]), (r[2], r[3]), c),
             V.seg((r[0], r[1]), (r[0], r[3]), c), V.seg((r[2], r[1]), (r[2], r[3]), c)]
    reg = V.compor(reg, V.cob(lados, jan, s, origem), q["contorno"])
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
ITENS = {"vaso_banho3": (2135.0, 365.0, 2175.0, 415.0), "vaso_banho2": (1686.0, 885.0, 1727.0, 935.0),
         "vaso_banho1": (2493.0, 1190.0, 2540.0, 1234.0), "vaso_master": (1683.0, 1584.0, 1724.0, 1630.0),
         "aparador_master": (1378.0, 1205.0, 1635.0, 1245.0), "aparador_suite3": (1690.0, 555.0, 1880.0, 605.0),
         "aparador_suite2": (1680.0, 1000.0, 1850.0, 1028.0), "sala_intima": (2040.0, 1030.0, 2185.0, 1185.0),
         "vao": (2535.0, 880.0, 2770.0, 912.0)}
FUNC = {k: (lambda q: lambda img, s, o: vaso(img, s, o, q))(v) for k, v in VASOS.items()}
FUNC.update({k: (lambda q: lambda img, s, o: aparador(img, s, o, q))(v) for k, v in APARADORES.items()})
FUNC.update({"sala_intima": sala_intima, "vao": vao})


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

"""Casa C Térreo, 9ª leva de 26/11: os contornos dos tapetes do estar e os adornos das mesas de freijó.

Pedidos do usuário (recortes do 12K B):

- **Tapete manchado do estar da direita** ("definir contorno do tapete."): a beira do tapete se desfazia no travertino
  (a trama manchada sumindo aos poucos, em franja, uns 5 a 9 px). Agora a beira é a do desenho do PDF (o polígono do
  tapete, 92 lados), nítida: numa faixa de 8 px de cada lado da linha, dentro o tapete (o próprio tapete espelhado de
  dentro para fora, sem emenda) e fora o travertino (na luz do piso em volta), com a sombra rente do tapete. As peças
  sobre a beira (o sofá curvo, as poltronas, as mesinhas de nogueira, as plantas) ficam como estão, com a sombra delas
  de volta na faixa refeita.
- **Tapete retangular do estar da esquerda** ("contorno do tapete marcado"): a barra de 3 px no tom do tapete (0,84),
  como a do tapete da sala TV (`terreo_casac_2611c`), em volta do retângulo do PDF, por baixo das peças (as poltronas
  azuis, os sofás e as mesinhas seixo ficam por cima).
- **Mesas de centro de freijó** ("colocar adornos sobre as mesas"): os adornos da biblioteca
  (`../biblioteca-objetos/02-terreo/sala-de-estar/adornos/`), sem repetir os da mesa redonda do estar da direita: na
  mesa de cima, a pilha de livros de linho bege e a bandeja de nogueira com o nó de cerâmica; na de baixo, o vaso com
  o ramo verde e o livro de linho sálvia. Cada peça com a sombra curta para baixo e à esquerda (como na Casa B).
- **Claraboia da varanda master** ("corrija o piso dentro do tracejado. esse tracejado é só para sinalizar a
  claraboia"): dentro do tracejado havia um retângulo claro e liso (o véu do vinílico antigo); agora é o travertino da
  varanda, na luz do travertino em volta, e o tracejado cinza fino fica.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611i.py [itens]
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
import esquadrias_pretas_1911 as EP              # noqa: E402
import vetor_2511 as V                           # noqa: E402
import terreo_casaa_2511d as D                   # noqa: E402
import terreo_casaa_2511g as G                   # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import terreo_casac_2611h as H                   # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]
PX_M = 59.7059

MANCHADO = dict(pdf=53916, faixa=8.0, sombra=0.12, sombra_sig=1.2, sombra_d=(-0.6, 0.6),
                fonte=(2152.0, 1372.0, 2195.0, 1400.0),
                creme=dict(png="sala-de-estar/poltrona-curva-boucle-almofada", pose=(2340.993, 1378.047, 42.389 * 1.25,
                                                                                      -59.583)))
RETANGULAR = dict(ret=(1713.3, 1342.2, 2011.9, 1551.2), borda=3.0, tom=0.84, amostra=(1758.0, 1490.0, 1798.0, 1526.0),
                  desvio=38.0)
PASTA = EP.PROJ / "POE642_CasaA/biblioteca-objetos/02-terreo/sala-de-estar/adornos"
ADORNOS = [                      # (peça, px/m do PNG, centro x, centro y, giro em graus), na ordem de baixo para cima
    ("livros-bege-a.png", 920.0, 1826.0, 1419.0, -8.0),
    ("bandeja-nogueira-d.png", 920.0, 1884.0, 1419.0, 0.0),
    ("no-ceramica-d.png", 920.0, 1884.5, 1418.5, 25.0),
    ("vaso-ramo-verde-d.png", 920.0, 1829.0, 1461.0, 0.0),
    ("livro-linho-salvia-e.png", 986.0 / 0.30, 1885.0, 1461.0, -15.0),
]
SOMBRA_ADORNO = 0.32
# a claraboia da varanda master (o tracejado do PDF: 736,0 a 950,8 x 255,4 a 294,6): dentro dele, o véu claro e liso do
# vinílico antigo (742 a 944 x 263 a 289) vira o travertino da varanda, na luz do travertino entre o véu e o tracejado
CLARABOIA = dict(veu=(740.5, 261.0, 945.8, 290.4),
                 luz=[(738.0, 256.8, 949.0, 260.6), (738.0, 290.8, 949.0, 293.4), (737.4, 256.8, 740.2, 293.4),
                      (946.2, 256.8, 949.4, 293.4)])


# ----------------------------------------------------------------------------------------------------------------------
_POLI = {}


def _poligono(idx):
    if idx not in _POLI:
        Q = EP.quadro(PLANTA)
        d = Q.desenhos[idx]
        pts = []
        for it in d["items"]:
            if it[0] == "l":
                for p in it[1:3]:
                    q = Q.p2q(p.x, p.y)
                    if not pts or np.hypot(q[0] - pts[-1][0], q[1] - pts[-1][1]) > 1e-6:
                        pts.append(q)
        _POLI[idx] = np.float64(pts)
    return _POLI[idx]


def _alfa_peca(P, jan, s, origem, cx, cy, wt, ht, giro, forma):
    X0, Y0 = jan[0], jan[1]
    Pw = P.copy()
    Pw[..., :3] = 255.0
    px, py = (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0
    return BT.pousar(np.zeros(forma + (3,), np.float32), Pw, px, py, wt * s, ht * s, giro, [], PX_M * s)[..., 0] / 255


def _pecas_estar(reg, jan, s, origem, q):
    """As peças sobre a beira do tapete manchado: o sofá curvo, as 2 poltronas e a poltrona curva (os alfas das poses),
    as mesinhas de nogueira e as plantas (pela cor)."""
    forma = reg.shape[:2]
    al = np.zeros(forma, np.float32)
    cx, cy, wt, ht, g = H.CURVO["pose"]
    al = np.maximum(al, _alfa_peca(BT.ler_png(H.CURVO["png"]), jan, s, origem, cx, cy, wt, ht, g, forma))
    P = BT.ler_png(H.POLTRONAS["png"])
    for x0, y0, x1, y1 in H.POLTRONAS["caixas"]:
        hh = y1 - y0
        al = np.maximum(al, _alfa_peca(P, jan, s, origem, (x0 + x1) / 2, (y0 + y1) / 2, hh * P.shape[1] / P.shape[0],
                                       hh, 0.0, forma))
    c = q["creme"]
    P = BT.ler_png(c["png"])
    cx, cy, L, g = c["pose"]
    al = np.maximum(al, _alfa_peca(P, jan, s, origem, cx, cy, L * P.shape[1] / P.shape[0], L, g, forma))
    u8 = np.clip(reg, 0, 255).astype(np.uint8)
    hsv = cv2.cvtColor(u8, cv2.COLOR_BGR2HSV)
    b, g_, r = reg[..., 0], reg[..., 1], reg[..., 2]
    madeira = (reg.mean(2) < 125) & (r > g_ + 8) & (g_ > b) & (r - b > 45)
    verde = (hsv[..., 0] >= 28) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 60) & (hsv[..., 2] > 25)
    k = max(1, int(round(1.5 * s)))
    cor = cv2.morphologyEx((madeira | verde).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((2 * k + 1,) * 2, np.uint8))
    cor = cv2.dilate(cor, np.ones((2 * k + 1,) * 2, np.uint8)).astype(np.float32)
    return np.clip(al, 0, 1), cor


def tapete_manchado(img, s, origem, q=MANCHADO):
    poli = _poligono(q["pdf"])
    f = q["faixa"]
    x0, y0 = poli.min(0) - f - 10
    x1, y1 = poli.max(0) + f + 10
    jan = V.janela(img, (x0, y0, x1, y1), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    Hh, W = reg.shape[:2]
    # o tapete do PDF, nítido (4x por px)
    ss = 4
    p = np.int32(np.round(((poli - np.float64(origem)) * s - np.float64([X0, Y0])) * ss * 16))
    m = np.zeros((Hh * ss, W * ss), np.uint8)
    cv2.fillPoly(m, [p], 255, lineType=cv2.LINE_AA, shift=4)
    A = cv2.resize(m.astype(np.float32) / 255, (W, Hh), interpolation=cv2.INTER_AREA)
    dentro = (A > 0.5).astype(np.uint8)
    d_in = cv2.distanceTransform(dentro, cv2.DIST_L2, 5)
    d_out = cv2.distanceTransform(1 - dentro, cv2.DIST_L2, 5)
    F = f * s
    faixa = ((d_in < F) & (dentro > 0)) | ((d_out < F) & (dentro == 0))
    # as peças (fora da faixa refeita)
    al, cor = _pecas_estar(reg, jan, s, origem, q)
    prot = np.clip(np.maximum(cv2.dilate((al > 0.02).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32),
                              cor), 0, 1)
    # dentro: o tapete espelhado de dentro para fora (na linha d = F), sem emenda
    dd = cv2.GaussianBlur(d_in, (0, 0), 1.5 * s)
    gx = cv2.Sobel(dd, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(dd, cv2.CV_32F, 0, 1, ksize=3)
    n = np.maximum(np.hypot(gx, gy), 1e-6)
    gx, gy = gx / n, gy / n
    passo = 2.0 * (F - np.minimum(d_in, F))
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    mx, my = (xx + gx * passo).astype(np.float32), (yy + gy * passo).astype(np.float32)
    esp = cv2.remap(reg, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    esp_prot = cv2.remap(prot, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=1)
    T = G._quilt(img, s, origem, q["fonte"], Hh, W, semente=2611)
    T = T / np.maximum(T.reshape(-1, 3).mean(0), 1) * np.median(reg[(d_in > 2 * F) & (prot < 0.5)], axis=0)
    w = np.clip(esp_prot, 0, 1)[..., None]
    rug = esp * (1 - w) + T * w
    # fora: o travertino na luz do piso em volta (o anel de F a 2F fora do tapete, sem as peças)
    TT = D.piso_tt(jan, s)
    r_ = reg.mean(2) / np.maximum(TT.mean(2), 1.0)
    ok = (d_out >= F) & (d_out < 2.5 * F) & (dentro == 0) & (prot < 0.5)
    med = float(np.median(r_[ok]))
    ok &= np.abs(r_ - med) < 0.08
    sig = 10.0 * s
    num = cv2.GaussianBlur(np.where(ok, r_, 0).astype(np.float32), (0, 0), sig)
    den = cv2.GaussianBlur(ok.astype(np.float32), (0, 0), sig)
    luz = np.where(den > 1e-3, num / np.maximum(den, 1e-3), med)
    trav = TT * luz[..., None]
    # a sombra rente do tapete, só fora
    sdx, sdy = q["sombra_d"]
    M = np.float32([[1, 0, sdx * s], [0, 1, sdy * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(A, M, (W, Hh)), (0, 0), q["sombra_sig"] * s) * (1 - A)
    trav *= (1 - q["sombra"] * sb)[..., None]
    novo = rug * A[..., None] + trav * (1 - A[..., None])
    # a sombra das peças de volta sobre o que foi refeito
    for sh in BT.SOMBRAS["movel"]:
        a_s = cv2.GaussianBlur(al, (0, 0), max(0.3, sh["sig"] * PX_M * s))
        Ms = np.float32([[1, 0, sh["dx"] * PX_M * s], [0, 1, sh["dy"] * PX_M * s]])
        a_s = cv2.warpAffine(a_s, Ms, (W, Hh))
        novo *= (1 - sh["forca"] * a_s * (1 - al))[..., None]
    k = cv2.GaussianBlur(faixa.astype(np.float32), (0, 0), 0.8 * s) * (1 - prot)
    out = reg * (1 - k[..., None]) + novo * k[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
def tapete_retangular(img, s, origem, q=RETANGULAR):
    """A barra de 3 px no tom do tapete, por baixo das peças (as que fogem da cor do tapete e os sofás E1)."""
    x0, y0, x1, y1 = q["ret"]
    b = q["borda"]
    jan = V.janela(img, (x0 - 3, y0 - 3, x1 + 3, y1 + 3), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    A = V.cob([V.ret(x0, y0, x1, y1)], jan, s, origem)
    Ain = V.cob([V.ret(x0 + b, y0 + b, x1 - b, y1 - b)], jan, s, origem)
    xs, ys = V.coords(jan, s, origem)
    am = q["amostra"]
    sel = ((xs >= am[0]) & (xs <= am[2]))[None, :] & ((ys >= am[1]) & (ys <= am[3]))[:, None]
    base = np.median(reg[sel], axis=0)
    # as peças: os sofás E1 (as poses de 2611h) e o que foge da cor do tapete (as poltronas azuis, as mesinhas seixo)
    al = np.zeros(forma, np.float32)
    for nome in ("sofa3", "sofa2"):
        P, cx, cy, wt, ht = H._pose(H.SOFAS[nome])
        al = np.maximum(al, _alfa_peca(P, jan, s, origem, cx, cy, wt, ht, H.SOFAS[nome]["giro"], forma))
    foge = (np.linalg.norm(reg - base[None, None], axis=2) > q["desvio"]).astype(np.uint8)
    k = max(1, int(round(0.8 * s)))
    foge = cv2.morphologyEx(foge, cv2.MORPH_OPEN, np.ones((2 * k + 1,) * 2, np.uint8))
    foge = cv2.dilate(foge, np.ones((2 * k + 1,) * 2, np.uint8)).astype(np.float32)
    prot = np.clip(np.maximum(al, foge), 0, 1)
    prot = cv2.GaussianBlur(prot, (0, 0), 0.5 * s)
    fx = np.clip(A - Ain, 0, 1) * (1 - prot)
    cor = base * q["tom"]
    out = reg * (1 - fx[..., None]) + cor[None, None, :] * fx[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
def _colar(reg, jan, s, origem, png, ppm, cx, cy, giro):
    X0, Y0, X1, Y1 = jan
    Hh, W = reg.shape[:2]
    T = cv2.imread(str(PASTA / png), cv2.IMREAD_UNCHANGED).astype(np.float32)
    a = T[..., 3] / 255.0
    pre = np.dstack([T[..., :3] * a[..., None], a])
    k = PX_M * s / ppm
    if k < 1:
        pre = cv2.resize(pre, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        k = 1.0
    pc = ((pre.shape[1] - 1) / 2.0, (pre.shape[0] - 1) / 2.0)
    tx, ty = (cx - origem[0]) * s - 0.5 - X0, (cy - origem[1]) * s - 0.5 - Y0
    M = cv2.getRotationMatrix2D(pc, giro, k)
    M[0, 2] += tx - pc[0]
    M[1, 2] += ty - pc[1]
    w = cv2.warpAffine(pre, M, (W, Hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    al = np.clip(w[..., 3], 0, 1)
    cor = w[..., :3] / np.maximum(al, 1e-4)[..., None]
    Ms = np.float32([[1, 0, -0.6 * s], [0, 1, 0.8 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(al, Ms, (W, Hh)), (0, 0), 0.7 * s) * (1 - al)
    reg = reg * (1 - SOMBRA_ADORNO * sb)[..., None]
    return reg * (1 - al[..., None]) + cor * al[..., None]


def adornos_freijo(img, s, origem):
    jan = V.janela(img, (1795.0, 1398.0, 1918.0, 1482.0), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    for png, ppm, cx, cy, giro in ADORNOS:
        reg = _colar(reg, jan, s, origem, png, ppm, cx, cy, giro)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def claraboia(img, s, origem, q=CLARABOIA):
    return D.refazer_piso(img, s, origem, [V.ret(*q["veu"])], ref_luz=[V.ret(*r) for r in q["luz"]], pena=1.2,
                          luz_sig=12.0, tol=0.10)


FUNC = {"tapete_manchado": tapete_manchado, "tapete_retangular": tapete_retangular, "adornos_freijo": adornos_freijo,
        "claraboia": claraboia}
ITENS = {"tapete_manchado": (2090.0, 1320.0, 2385.0, 1595.0), "tapete_retangular": (1680.0, 1330.0, 2045.0, 1610.0),
         "adornos_freijo": (1780.0, 1390.0, 1930.0, 1490.0), "claraboia": (720.0, 240.0, 965.0, 310.0)}


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

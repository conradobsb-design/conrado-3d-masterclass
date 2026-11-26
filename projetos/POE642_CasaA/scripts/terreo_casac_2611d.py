"""Casa C Térreo, 4ª leva de 26/11: a gourmet (cuba, bordas da bancada, banquetas e rótulo).

Pedidos do usuário (recortes do 12K B):

- "corrigir cuba de inox e rotulo": a cuba da bancada de trás (o desenho antigo, com a faixa escura embaixo e a torneira
  borrada) sai (o granito de 50 px à direita, entre a cuba e a churrasqueira) e entra a cuba Franke com o misturador da
  biblioteca (`area-gourmet/cuba-franke-misturador-unic`) no retângulo do PDF (38,2 x 26,3 px; as faixas lisas dos
  lados esticadas, o miolo igual). O rótulo GOURMET / A: 24,95 m² perde o retângulo de fundo (o piso de 100 px à
  esquerda, na luz da beira) e os pontinhos depois do m²; as letras ficam por cima.
- "remover linha tecnica na borda da bancada": o fio cinza de 1 a 3 px em todas as bordas da bancada em U (a frente da
  bancada de trás, o fim dela junto às geladeiras, a perna da esquerda, o topo e a ponta direita da ilha, a borda de
  baixo e a de fora) sai: o granito e o piso de cada lado vêm de 4 px para dentro e para fora; na borda fica a face do
  granito 1 px mais escura e, onde o piso está embaixo ou à esquerda, a sombra curta.
- "melhorar a representação das banquetas e empurrá-las para debaixo da bancada": as 6 banquetas B (o assento de corda e
  o encosto de madeira, da biblioteca) de novo no 12K na resolução dele, no mesmo espaçamento, ~55% sob o tampo (antes
  ~40%): à mostra ficam o encosto e a beira do assento; o travertino embaixo de novo (sem as banquetas e as sombras
  antigas); o tampo por cima e a sombra dele nas banquetas.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611d.py [itens]
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
import um_pav_casaa_2511 as U                    # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import terreo_casac_2611 as T0                   # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]
PX_M = 59.7059

CUBA = dict(limpa=(1289.5, 934.0, 1335.0, 973.6), d=(50.0, 0.0), ret=(1292.9, 940.9, 1331.1, 967.2),
            png="area-gourmet/cuba-franke-misturador-unic")
# as bordas: (orientação, posição da borda, extensão, lado da bancada (-1: acima/à esquerda, +1: abaixo/à direita),
# meia-largura do fio (lado de menor coordenada, lado de maior), sombra no piso)
E_BAIXO = 1156.4
BORDAS = [("v", 1282.2, (972.9, 1086.5), -1, (2.4, 1.8), 0.0),       # a perna da esquerda (o piso à direita)
          ("h", 972.9, (1282.2, 1509.2), -1, (1.3, 2.1), 0.16),       # a frente da bancada de trás (o piso embaixo)
          ("v", 1509.2, (933.0, 972.9), -1, (1.6, 2.8), 0.0),         # o fim dela junto às geladeiras
          ("h", 1086.5, (1282.2, 1563.0), +1, (1.7, 1.5), 0.0),       # o topo da ilha (o piso em cima)
          ("v", 1563.0, (1086.5, E_BAIXO), -1, (3.5, 2.2), 0.0),      # a ponta direita da ilha
          ("v", 1231.0, (978.5, E_BAIXO), +1, (2.2, 1.0), 0.20)]      # a borda de fora (o travertino à esquerda)
BAIXO = dict(e=E_BAIXO, x=(1231.0, 1563.0), meia=1.8, zona=(1226.0, E_BAIXO, 1568.0, 1184.0), sombra=0.22)
BANQUETAS = dict(png="area-gourmet/banqueta-b", larg=25.0, x=(1231.4, 1562.8), n=6, dy=-0.8)
ROTULO = dict(zona=(1390.0, 1008.0, 1480.0, 1054.0), d=(-100.0, 0.0), letra="clara",
              pontinhos=(1463.5, 1031.0, 1481.0, 1052.0))
FACE = 0.9
K_COPIA = 4.0


# ----------------------------------------------------------------------------------------------------------------------
def borda(img, s, origem, o, e, ext, lado, meia, sombra=0.0, face=FACE, so_bancada=False):
    """O fio da borda sai: as linhas (ou colunas) do fio vêm de K_COPIA px para dentro de cada lado; a face do granito
    (1 px) mais escura e a sombra curta no piso."""
    k = K_COPIA
    a, b = ext
    m0, m1 = meia
    if o == "h":
        caixa = (a - 2, e - m0 - k - 3, b + 2, e + m1 + k + 6)
    else:
        caixa = (e - m0 - k - 6, a - 2, e + m1 + k + 3, b + 2)
    jan = V.janela(img, caixa, s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    if o == "v":
        reg = reg.transpose(1, 0, 2)
    xs, ys = V.coords(jan, s, origem)
    cruz, longo = (ys, xs) if o == "h" else (xs, ys)
    K = int(round(k * s))
    t = cruz - e
    novo = reg.copy()
    n = reg.shape[0]
    for r in range(n):
        if -m0 <= t[r] < 0:
            if so_bancada and lado > 0:
                continue
            src = r - K
        elif 0 <= t[r] <= m1:
            if so_bancada and lado < 0:
                continue
            src = r + K
        else:
            continue
        if 0 <= src < n:
            novo[r] = reg[src]
    # a face do granito
    if lado < 0:
        fa = np.clip(np.minimum(t + 1.0, -t) * s, 0, 1) * (t < 0)
    else:
        fa = np.clip(np.minimum(t + 0.0, 1.0 - t) * s, 0, 1) * (t >= 0)
    fa = np.clip(fa, 0, 1)
    novo *= (1 - (1 - face) * fa)[:, None, None]
    if sombra:
        d = np.where(lado < 0, t, -t)                    # a distância para o lado do piso
        sb = np.where(d >= 0, sombra * np.exp(-d / 1.3), 0.0)
        novo *= (1 - sb)[:, None, None]
    w = np.clip(np.minimum(longo - a, b - longo) * s + 0.5, 0, 1)[None, :, None]
    out = reg * (1 - w) + novo * w
    if o == "v":
        out = out.transpose(1, 0, 2)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def bordas(img, s, origem):
    for o, e, ext, lado, meia, sombra in BORDAS:
        img = borda(img, s, origem, o, e, ext, lado, meia, sombra)
    return img


def cuba(img, s, origem, q=CUBA):
    img = U._copiar(img, s, origem, q["limpa"], q["d"], lados="lr", pena=1.2)
    x0, y0, x1, y1 = q["ret"]
    P = BT.ler_png(q["png"])
    P = BT.esticar_lados(P, (x1 - x0) / (y1 - y0), miolo=(0.18, 0.82))
    return _pousar(img, s, origem, P, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, None)


def _pousar(img, s, origem, P, cx, cy, wt, ht, ang, sombra, reg_jan=None):
    m = max(wt, ht) * 0.75 + 8
    jan = V.janela(img, (cx - m, cy - m, cx + m, cy + m), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    reg = BT.pousar(reg, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, wt * s, ht * s, ang,
                    BT.SOMBRAS[sombra] if sombra else [], PX_M * s)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def ilha_baixo(img, s, origem, q=BAIXO, qb=BANQUETAS):
    e = q["e"]
    xa, xb = q["x"]
    # o travertino embaixo (sem as banquetas e as sombras antigas) e o granito no lado de cima do fio
    img = G.refazer(img, s, origem, [(q["zona"], "lrb")], pena=2.5)
    img = borda(img, s, origem, "h", e, (xa, xb), -1, (q["meia"], 0.0), 0.0, so_bancada=True)
    jan = V.janela(img, (xa - 6, e - 30, xb + 6, e + 22), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    tampo = img[Y0:Y1, X0:X1].astype(np.float32)
    # as banquetas
    passo = (qb["x"][1] - qb["x"][0]) / qb["n"]
    P = BT.ler_png(qb["png"])
    h, w = P.shape[:2]
    wt = qb["larg"]
    ht = wt * h / w
    for i in range(qb["n"]):
        cx = qb["x"][0] + passo * (i + 0.5)
        img = _pousar(img, s, origem, P, cx, e + qb["dy"], wt, ht, 180.0, "movel")
    # o tampo por cima e a sombra dele
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    a = V.cob([V.ret(xa, e - 40, xb, e)], jan, s, origem)[..., None]
    reg = reg * (1 - a) + tampo * a
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    dd = Y - e
    dentro_x = np.clip(np.minimum(X - (xa - 1.0), (xb - 1.0) - X) * s + 0.5, 0, 1)
    sb = np.where(dd >= 0, q["sombra"] * np.exp(-dd / 1.5), 0.0) * dentro_x
    reg *= (1 - sb)[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def rotulo(img, s, origem, q=ROTULO, anel=3.0, sig=10.0, pena=3.0):
    """Como `terreo_casac_2611.rotulo` (o piso de outro trecho, as letras claras de volta por cima), com a luz casada
    pela beira inteira da zona: a razão imagem/fonte no anel de `anel` px junto à beira, levada para dentro por
    convolução normalizada (sig px), sem o degrau do retângulo."""
    img = U._copiar(img, s, origem, q["pontinhos"], q["d"], lados="lrtb", pena=1.5)
    zx0, zy0, zx1, zy1 = q["zona"]
    jan = V.janela(img, q["zona"], s, origem, folga=int(2 * s) + 2)
    X0, Y0, X1, Y1 = jan
    dx, dy = int(round(q["d"][0] * s)), int(round(q["d"][1] * s))
    F = img[Y0:Y1, X0:X1].astype(np.float32)
    S_ = img[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    L = F.mean(2)
    k = max(int(round(0.45 * s)), 1)
    letra = ((L > 175) & (np.abs(F[..., 2] - F[..., 0]) < 40)).astype(np.uint8)
    letra = cv2.dilate(letra, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    fundo = cv2.inpaint(np.clip(F, 0, 255).astype(np.uint8), letra, max(3, 2 * k), cv2.INPAINT_TELEA).astype(np.float32)
    Lf = fundo.mean(2)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    dist = np.minimum.reduce([X - zx0, zx1 - X, Y - zy0, zy1 - Y])
    dentro = dist >= 0
    beira = (dist >= 0) & (dist < anel) & (letra == 0)
    Fb = cv2.GaussianBlur(F, (0, 0), 1.2 * s)
    Sb = cv2.GaussianBlur(S_, (0, 0), 1.2 * s)
    r = Fb / np.maximum(Sb, 1.0)
    g = beira.astype(np.float32)
    num = cv2.GaussianBlur(r * g[..., None], (0, 0), sig * s)
    den = cv2.GaussianBlur(g, (0, 0), sig * s)[..., None]
    luz = num / np.maximum(den, 1e-4)
    S2 = S_ * luz
    Ltxt = float(np.percentile(L[dentro], 99.5))
    a = np.clip((L - Lf) / np.where(np.abs(Ltxt - Lf) < 1, 1.0, Ltxt - Lf), 0, 1) * (letra > 0)
    w = np.clip(dist / pena, 0, 1)
    out = F + ((1 - a) * w)[..., None] * (S2 - fundo)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def gourmet(img, s, origem):
    img = cuba(img, s, origem)
    img = bordas(img, s, origem)
    img = ilha_baixo(img, s, origem)
    return rotulo(img, s, origem)


FUNC = {"gourmet": gourmet}
ITENS = {"gourmet": (1222.0, 925.0, 1575.0, 1190.0)}


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

"""Casa C Térreo, 2ª leva de 26/11: a sombra uniforme dos degraus da escada DESCE PARA O SUBSOLO.

Usuário (sobre o recorte do 12K B da escada, ao lado do BH master 2): "corrija o sombreamento de descida das escadas
conforme fizemos no subsolo". A escada é a mesma do Subsolo (os degraus 1 a 10, largos, e o L), vista de cima, com os
degraus 11 a 20 estreitos, em pé, junto ao BH master 2. Antes, a faixa escura junto a cada espelho tinha de 2 a 6 px,
com um fio preto em algumas bordas (768 e 798), e nos degraus estreitos o degradê ia de ponta a ponta do piso.

O mesmo perfil do Subsolo (`subsolo_casac_2611c.PERFIL`: r(d) = 1 - 0,36 exp(-d / 1,8), até 9 px da borda, constante
ao longo de cada uma), no piso mais baixo junto ao espelho do degrau seguinte:

- **bordas deitadas** (achadas na final: o patamar em 738 e os degraus em 768, 798, 828, 858, 888, 919, de 366,8 a
  634,4, onde começa a parede do BH master 2; 949, de 443; 979, de 473): o Bege Bahia do próprio degrau 10 px antes;
- **bordas em pé do L** (443, de 949 a 1097, e 473, de 979 a 1097, com o canto arredondado) e a do degrau 10 para o 11
  (694, de 979 a 1067,5): o Bege Bahia 10 px à esquerda;
- **degraus estreitos 11 a 20** (bordas em 712, 730, 748, 766, 784, 801, 819, 837, 855 e 873, de 979 a 1067,5): cada
  piso fica num tom só (o da faixa clara logo depois do espelho de trás, coluna a coluna, guardando o desenho da pedra)
  e recebe o mesmo perfil junto ao espelho da frente.

As letras sobre as faixas (o ▲ D do degrau 9 e o ◀ D do degrau 20) ficam por cima; nas colunas do ▲ D a fonte do Bege
Bahia vem de 30 px à esquerda. Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611b.py
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
import um_pav_casaa_2511d as DD      # noqa: E402
import subsolo_casac_2611c as DG     # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
PERFIL = DG.PERFIL
X1W = 634.4
HORIZ = [(738.0, 366.8, X1W), (768.0, 366.8, X1W), (798.0, 366.8, X1W), (828.0, 366.8, X1W), (858.0, 366.8, X1W),
         (888.0, 366.8, X1W), (919.0, 366.8, X1W), (949.0, 443.0, X1W), (979.0, 473.0, X1W)]
VERT = [(443.0, 949.0, 1097.0), (473.0, 979.0, 1097.0)]          # (x da borda, y do canto, y do fim)
VERT_RETO = [(694.0, 979.5, 1067.5)]                              # (x da borda, y de cima, y de baixo)
ESTREITOS = dict(bordas=[694.0, 712.0, 730.0, 748.0, 766.0, 784.0, 801.0, 819.0, 837.0, 855.0, 873.0],
                 y=(979.5, 1067.5), claro=(0.6, 4.6))
LETRAS = [dict(caixa=(558.0, 946.0, 578.0, 976.0), dx=-30.0, y=(939.0, 980.0)),       # ▲ D do degrau 9
          dict(caixa=(854.0, 988.0, 877.0, 1035.0), dx=0.0, y=(0.0, 0.0))]           # ◀ D do degrau 20
JANELA = (355.0, 700.0, 880.0, 1100.0)


def _letras(reg, X, Y):
    """O alfa das letras (escuras) dentro das caixas de LETRAS."""
    L = reg.mean(2)
    a = np.zeros(L.shape, np.float32)
    for le in LETRAS:
        lx0, ly0, lx1, ly1 = le["caixa"]
        cx = (X >= lx0) & (X <= lx1) & (Y >= ly0) & (Y <= ly1)
        a = np.maximum(a, np.clip((165.0 - L) / 60.0, 0, 1) * cx)
    return a


def degraus(img, s, origem, q=PERFIL):
    jan = V.janela(img, JANELA, s, origem, folga=int(14 * s) + 2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    k = int(round(q["fonte"] * s))
    lim = q["D"] + q["pena"]
    acima = np.zeros_like(reg)
    acima[k:] = reg[:-k]
    esq = np.zeros_like(reg)
    esq[:, k:] = reg[:, :-k]
    for le in LETRAS:
        if le["dx"] == 0:
            continue
        lx0, ly0, lx1, ly1 = le["caixa"]
        kx = int(round(-le["dx"] * s))
        acima_l = np.zeros_like(reg)
        acima_l[k:, kx:] = reg[:-k, :-kx]
        wl = np.clip(np.minimum(X - lx0, lx1 - X) / 2.0 + 0.5, 0, 1) * (Y > le["y"][0]) * (Y < le["y"][1])
        acima = acima * (1 - wl[..., None]) + acima_l * wl[..., None]
    dist = np.full((H, W), np.inf, np.float32)
    tipo = np.zeros((H, W), np.uint8)
    for ye, xa, xb in HORIZ:
        m = (Y < ye) & (Y > ye - lim) & (X >= xa) & (X <= xb)
        d = ye - Y
        sel = m & (d < dist)
        dist[sel] = d[sel]
        tipo[sel] = 0
    for xe, yc, yb in VERT:
        d = np.where(Y >= yc, xe - X, np.hypot(xe - X, yc - Y))
        m = (X < xe) & (X > xe - lim) & (Y > yc - lim) & (Y <= yb) & (d < lim)
        sel = m & (d < dist)
        dist[sel] = d[sel]
        tipo[sel] = 1
    for xe, ya, yb in VERT_RETO:
        d = xe - X
        m = (X < xe) & (X > xe - lim) & (Y >= ya) & (Y <= yb)
        sel = m & (d < dist)
        dist[sel] = d[sel]
        tipo[sel] = 1
    dentro = np.isfinite(dist)
    dd = np.where(dentro, dist, lim)
    w = np.clip((lim - dd) / q["pena"], 0, 1) * dentro
    fonte = np.where((tipo == 1)[..., None], esq, acima)
    novo = fonte * DG._r(dd)[..., None]
    out = reg * (1 - w[..., None]) + novo * w[..., None]
    # os degraus estreitos: cada piso num tom só (coluna a coluna) e o perfil junto ao espelho da frente
    e = ESTREITOS["bordas"]
    ya, yb = ESTREITOS["y"]
    linhas = (ys >= ya) & (ys <= yb)
    let = _letras(reg, X, Y)
    for i in range(len(e) - 1):
        xa, xb = e[i], e[i + 1]
        cols = (xs > xa) & (xs < xb)
        if not cols.any() or not linhas.any():
            continue
        sub = reg[np.ix_(linhas, cols)]
        Ls = sub.mean(2)
        sem = let[np.ix_(linhas, cols)] < 0.05
        colm = np.array([np.median(Ls[sem[:, j], j]) if sem[:, j].sum() > 5 else np.median(Ls[:, j])
                         for j in range(Ls.shape[1])], np.float32)
        xc = xs[cols]
        cl = (xc >= xa + ESTREITOS["claro"][0]) & (xc <= xa + ESTREITOS["claro"][1])
        alvo = float(np.median(colm[cl])) if cl.any() else float(colm.max())
        g = alvo * DG._r(xb - xc) / np.maximum(colm, 1.0)
        out[np.ix_(linhas, cols)] = sub * g[None, :, None]
    # as letras por cima
    a = let[..., None]
    out = out * (1 - a) + reg * a
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


FUNC = {"degraus": degraus}
ITENS = {"degraus": (355.0, 720.0, 890.0, 1105.0)}


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

"""Casa B Térreo, 3ª leva de 26/11: as banquetas da bancada gourmet empurradas para baixo da bancada.

Usuário (sobre as banquetas cortadas na borda, com cerca de 40% sob o tampo): "isso, empurre para baixo da bancada".
As 5 banquetas descem 6 px da final (10 cm): o assento fica quase todo sob o tampo e aparecem o encosto e a frente do
assento, junto à borda. Em cada uma, na faixa entre o travertino de cima e a borda da bancada (1300,5 a 1319,0):

- a banqueta e a sombra curta dela (a madeira e a palha pela cor; a sombra, o travertino mais escuro e sem saturação,
  rente a ela) saem, e o travertino das mesmas linhas, do vão limpo logo à direita (14 a 23 px do meio), espelhado de
  lado a lado, ocupa o lugar (a mesma luz junto à bancada; os veios horizontais seguem);
- a banqueta volta 6 px abaixo: a madeira e a palha como eram, a sombra como a razão dela sobre o travertino de antes;
- o que passa da borda some sob o tampo (a bancada não muda);
- e a sombra do tampo na parte de fora, junto à borda (`terreo_casab_2611b.banquetas`), de novo nas peças que chegaram
  à borda.

Final, prancha e 12K A e B (cada banqueta pelo registro local).

  python3 terreo_casab_2611c.py
"""
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
import um_pav_casaa_2511c as C       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import terreo_casab_2611b as B       # noqa: E402

PLANTA = "B_Terreo"
DZ = B.DZ
SOB = dict(xs=[1321.5, 1370.0, 1420.0, 1470.0, 1519.0], meia=23.0, y0=1300.5, borda=1319.0, desce=6.0, fonte=19.0,
           vao=(14.0, 23.0))


def banquetas_sob(img, s, origem, q=SOB):
    for xc in q["xs"]:
        caixa = (xc - q["meia"], q["y0"] - q["fonte"] - 1.0, xc + q["meia"], q["borda"] + 1.0)
        jan, reg = C._reg(img, caixa, s, origem, folga=0)
        xs, ys = V.coords(jan, s, origem)
        H, W = reg.shape[:2]
        faixa = (ys >= q["y0"]) & (ys < q["borda"])
        L = reg.mean(2)
        sat = reg.max(2) - reg.min(2)
        corpo = ((reg[..., 2] - reg[..., 0] > 55) | (L < 150)) & faixa[:, None]
        trav = ~corpo & faixa[:, None]
        Lp = float(np.median(L[trav])) if trav.any() else 210.0
        perto = cv2.dilate(corpo.astype(np.uint8), np.ones((int(8 * s) | 1, int(8 * s) | 1), np.uint8)).astype(bool)
        sombra = trav & perto & (L < Lp - 6) & (sat < 45)          # só a sombra curta, rente à banqueta
        k = max(3, int(round(0.6 * s)) * 2 + 1)
        m = cv2.dilate((corpo | sombra).astype(np.uint8), np.ones((k, k), np.uint8)).astype(np.float32)
        m *= faixa[:, None]
        am = np.clip(cv2.GaussianBlur(m, (0, 0), 0.4 * s), 0, 1) * faixa[:, None]
        # o travertino das mesmas linhas (a mesma luz junto à bancada), do vão limpo à direita da banqueta, espelhado
        # de lado a lado (os veios são horizontais e seguem na emenda)
        limpo = reg.copy()
        gap = np.where((xs >= xc + q["vao"][0]) & (xs <= xc + q["vao"][1]))[0]
        n = len(gap)
        idx = np.arange(W) % (2 * n)
        idx = np.where(idx < n, idx, 2 * n - 1 - idx)
        src = reg[:, gap[idx]]
        limpo = limpo * (1 - am[..., None]) + src * am[..., None]
        # a banqueta de novo, `desce` px abaixo
        d = int(round(q["desce"] * s))
        ab = np.clip(cv2.GaussianBlur(corpo.astype(np.float32), (0, 0), 0.35 * s), 0, 1)
        razao = np.clip(reg / np.maximum(limpo, 1.0), 0.45, 1.0)
        razao = np.where(m[..., None] > 0, razao, 1.0)
        ab_d = np.zeros_like(ab)
        ab_d[d:] = ab[:-d]
        reg_d = np.zeros_like(reg)
        reg_d[d:] = reg[:-d]
        raz_d = np.ones_like(razao)
        raz_d[d:] = razao[:-d]
        novo = limpo * raz_d
        novo = novo * (1 - ab_d[..., None]) + reg_d * ab_d[..., None]
        reg[faixa] = novo[faixa]
        img = C._gravar(img, jan, reg)
    return B.banquetas(img, s, origem)


FUNC = {"banquetas_sob": banquetas_sob}
ITENS = {"banquetas_sob": (1280.0, 1285.0, 1570.0, 1345.0)}


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

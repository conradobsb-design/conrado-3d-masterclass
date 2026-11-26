"""Casa B Térreo, 5ª leva de 26/11: uma mesa de centro em nogueira e as poltronas do mesmo tamanho.

- **Mesa de centro em nogueira** ("use o tom nogueira em uma das mesas", as duas mesas retangulares de madeira clara
  sobre o tapete da varanda): a de trás (1318 a 1406 x 834 a 869) na nogueira da biblioteca da Casa D (um trecho liso
  da `mesa-centro-nogueira-adorno-d`, o veio no comprido, como as mesinhas seixo da Casa C), com a luz e as bordas da
  mesa de antes (a razão da luminosidade dela sobre a mediana, alisada); a da frente fica no freijó claro.
- **Poltronas do mesmo tamanho** ("deixe essas poltronas no mesmo tamanho"): as duas poltronas terracota do living
  (44 x 48 px) eram menores que as duas da varanda (46 x 52, de assento branco); as do living crescem 7% em volta do
  meio delas (a peça inteira, pela cor terracota e o casco dela), o resto fica.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casab_2611e.py [item ...]
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
RAIZ = EP.PROJ
MESA = dict(ret=(1317.8, 833.8, 1406.2, 869.4),
            nogueira=(RAIZ / "POE642_CasaD/biblioteca-objetos/02-terreo/living/mesa-centro-nogueira-adorno-d.png",
                      (165, 565, 390, 800)), luz_sig=0.8)
POLTRONAS = dict(caixas=[(1686.0, 834.0, 1746.0, 896.0), (1686.0, 905.0, 1746.0, 967.0)], k=1.07)


def mesa_nogueira(img, s, origem, q=MESA):
    x0, y0, x1, y1 = q["ret"]
    jan, reg = C._reg(img, (x0 - 2, y0 - 2, x1 + 2, y1 + 2), s, origem, folga=0)
    H, W = reg.shape[:2]
    a = V.cob([V.ret(*q["ret"])], jan, s, origem)
    p, (tx0, ty0, tx1, ty1) = q["nogueira"]
    T = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)[ty0:ty1, tx0:tx1, :3].astype(np.float32)
    # a madeira na caixa da mesa (o veio horizontal, no comprido da mesa)
    ys, xs = np.where(a > 0.01)
    bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    w, h = bx1 - bx0, by1 - by0
    k = max(w / T.shape[1], h / T.shape[0])
    Tm = cv2.resize(T, (int(np.ceil(T.shape[1] * k)), int(np.ceil(T.shape[0] * k))), interpolation=cv2.INTER_AREA)
    tex = np.empty_like(reg)
    tex[:] = Tm.reshape(-1, 3).mean(0)
    tex[by0:by1, bx0:bx1] = Tm[:h, :w]
    # a luz e as bordas da mesa de antes (a razão da luminosidade, alisada para não trazer o veio claro)
    L = reg.mean(2)
    med = float(np.median(L[a > 0.99]))
    f = np.clip(cv2.GaussianBlur(L / max(med, 1.0), (0, 0), q["luz_sig"] * s), 0.55, 1.25)
    novo = tex * f[..., None]
    reg = reg * (1 - a[..., None]) + novo * a[..., None]
    return C._gravar(img, jan, reg)


def poltronas_iguais(img, s, origem, q=POLTRONAS):
    for caixa in q["caixas"]:
        jan, reg = C._reg(img, caixa, s, origem, folga=0)
        H, W = reg.shape[:2]
        hsv = cv2.cvtColor(np.clip(reg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
        t = ((hsv[..., 0] <= 20) & (hsv[..., 1] > 90) & (hsv[..., 2] > 80)).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(t)
        if n < 2:
            continue
        i = 1 + int(np.argmax(st[1:, 4]))
        pts = np.argwhere(lab == i)[:, ::-1].astype(np.int32)
        casco = np.zeros((H, W), np.uint8)
        cv2.fillConvexPoly(casco, cv2.convexHull(pts), 1)
        kd = max(3, int(round(0.5 * s)) * 2 + 1)
        casco = cv2.dilate(casco, np.ones((kd, kd), np.uint8))
        ys, xs = np.where(casco > 0)
        cx, cy = (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0
        k = q["k"]
        M = np.float32([[k, 0, cx * (1 - k)], [0, k, cy * (1 - k)]])
        maior = cv2.warpAffine(reg, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        am = cv2.warpAffine(casco.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR)
        am = np.clip(cv2.GaussianBlur(am, (0, 0), 0.35 * s), 0, 1)
        # a sombra curta da poltrona maior (como a de antes: para baixo e à esquerda)
        Ms = np.float32([[1, 0, -0.8 * s], [0, 1, 1.0 * s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(am, Ms, (W, H)), (0, 0), 1.0 * s) * (1 - am)
        reg = reg * (1 - 0.18 * sb)[..., None]
        reg = reg * (1 - am[..., None]) + maior * am[..., None]
        img = C._gravar(img, jan, reg)
    return img


FUNC = {"mesa_nogueira": mesa_nogueira, "poltronas_iguais": poltronas_iguais}
ITENS = {"mesa_nogueira": (1280.0, 820.0, 1420.0, 925.0), "poltronas_iguais": (1660.0, 820.0, 1770.0, 980.0)}


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

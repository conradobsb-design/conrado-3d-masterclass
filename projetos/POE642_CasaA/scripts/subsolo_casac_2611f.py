"""Casa C Subsolo, 6ª leva de 26/11: a sombra do filete entre o Bege Bahia e o travertino da varanda.

Usuário (sobre o recorte do filete que desce do pilar redondo até o 1º degrau): "aqui é um filete que também precisa
de um sombreamento do lado do travertino".

O filete (a faixa clara de 634,3 a 636,8, de 320,5 a 737,0) fica; o tracejado cinza técnico logo ao lado (637 a 638,5)
vira o próprio travertino de logo à direita (os veios correm na horizontal); e o travertino, junto ao filete, recebe a
mesma faixa de sombra dos degraus (`subsolo_casac_2611c`: r(d) = 1 - 0,36 exp(-d / 1,8), d a distância ao filete em px da
final, a faixa nova passando para a de antes de 7 a 9 px), uniforme de ponta a ponta; no pé, junto ao 1º degrau, ela
soma com a do patamar (o canto um pouco mais escuro).

Final, prancha e 12K A e B (pelo registro local).

  python3 subsolo_casac_2611f.py
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
import um_pav_casaa_2511d as DD      # noqa: E402
import subsolo_casac_2611 as A       # noqa: E402
import subsolo_casac_2611c as DG     # noqa: E402

PLANTA = A.PLANTA
DZ = A.DZ
FILETE = dict(borda=636.8, y=(320.5, 737.0), tracejado=((636.8, 320.5, 639.3, 737.0), (2.6, 0.0), "r"))


def filete_sombra(img, s, origem, q=FILETE, p=DG.PERFIL):
    r, d, lados = q["tracejado"]
    img = A.copiar(img, s, origem, r, d, lados, pena=0.6)
    xe = q["borda"]
    y0, y1 = q["y"]
    lim = p["D"] + p["pena"]
    jan = V.janela(img, (xe - 1, y0, xe + lim + 1, y1), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    dist = X - xe
    m = (dist > 0) & (dist < lim) & (Y >= y0) & (Y <= y1)
    # a passagem nas pontas de cima e de baixo (meio px), para não cortar seco
    pv = np.clip(np.minimum(Y - y0, y1 - Y) / 0.5, 0, 1)
    w = np.clip((lim - dist) / p["pena"], 0, 1) * m * pv
    fator = DG._r(np.maximum(dist, 0))
    reg = reg * (1 - w[..., None]) + (reg * fator[..., None]) * w[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"filete_sombra": filete_sombra}
ITENS = {"filete_sombra": (600.0, 330.0, 680.0, 745.0)}


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

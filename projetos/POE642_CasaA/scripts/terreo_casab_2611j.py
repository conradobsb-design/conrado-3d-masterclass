"""Casa B Térreo, 10ª leva de 26/11: adornos também na mesa de centro do living.

Usuário: "coloque adornos também na mesa do living". A mesa orgânica de madeira clara do living (a gota, 1795 a 1905 x
861 a 929, a ponta à esquerda e a parte larga à direita) recebe adornos da biblioteca, em par com os da varanda
(`terreo_casab_2611i`) sem repetir as peças:

- na parte larga, a bandeja redonda de nogueira (a da mesa de pedra verde da biblioteca da Casa D) com o nó de cerâmica
  (o da mesa de espelho da Casa D) sobre ela (centro 1874 x 894);
- mais para o meio, a pilha de livros "ART" (a da mesa de nogueira da Casa D), girada 10° (centro 1835 x 895).

Os recortes ficam em `../biblioteca-objetos/02-terreo/sala-de-estar/adornos/` (bandeja-nogueira-d, no-ceramica-d,
livros-art-d), na escala de 920 px/m das mesas de origem; na planta, 60 px/m, com a sombra curta para baixo e à
esquerda (como em 2611i).

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casab_2611j.py
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
import terreo_casab_2611b as B       # noqa: E402
import terreo_casab_2611i as I       # noqa: E402

PLANTA = "B_Terreo"
DZ = B.DZ
ADORNOS = [                      # (peça, px/m do PNG, centro x, centro y, giro em graus), na ordem de baixo para cima
    ("livros-art-d.png", 920.0, 1835.0, 895.0, 10.0),
    ("bandeja-nogueira-d.png", 920.0, 1874.0, 894.0, 0.0),
    ("no-ceramica-d.png", 920.0, 1874.5, 893.5, 25.0),
]


def adornos_living(img, s, origem):
    jan = V.janela(img, (1785.0, 850.0, 1915.0, 940.0), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    for png, ppm, cx, cy, giro in ADORNOS:
        reg = I._colar(reg, jan, s, origem, png, ppm, cx, cy, giro)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"adornos_living": adornos_living}
ITENS = {"adornos_living": (1760.0, 830.0, 1950.0, 960.0)}


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

"""Casa B Térreo, 11ª leva de 26/11: adornos também na mesa de centro da sala íntima.

Usuário: "coloque adornos também na mesa da sala íntima". A mesa redonda de madeira da sala íntima (centro 1699 x 458,
Ø 56 px, 0,93 m) recebe adornos da biblioteca sem repetir os da varanda (`terreo_casab_2611i`) e do living
(`terreo_casab_2611j`):

- o vaso branco com ramo verde (o da mesa de pedra verde da biblioteca da Casa D), o vaso perto do meio da mesa e o
  ramo para cima e à direita, as folhas dentro do tampo (centro do recorte 1709 x 452);
- o livro de linho verde-sálvia (o da varanda principal da biblioteca da Casa E), girado 20°, embaixo e à esquerda do
  vaso (centro 1687 x 467).

Os recortes ficam em `../biblioteca-objetos/02-terreo/sala-de-estar/adornos/` (vaso-ramo-verde-d, 920 px/m;
livro-linho-salvia-e, 986 px para 0,30 m); na planta, 60 px/m, com a sombra curta para baixo e à esquerda (como em
2611i).

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casab_2611k.py
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
    ("livro-linho-salvia-e.png", 986.0 / 0.30, 1687.0, 467.0, -20.0),
    ("vaso-ramo-verde-d.png", 920.0, 1709.0, 452.0, 0.0),
]


def adornos_sala_intima(img, s, origem):
    jan = V.janela(img, (1660.0, 420.0, 1740.0, 500.0), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    for png, ppm, cx, cy, giro in ADORNOS:
        reg = I._colar(reg, jan, s, origem, png, ppm, cx, cy, giro)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"adornos_sala_intima": adornos_sala_intima}
ITENS = {"adornos_sala_intima": (1620.0, 380.0, 1780.0, 540.0)}


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

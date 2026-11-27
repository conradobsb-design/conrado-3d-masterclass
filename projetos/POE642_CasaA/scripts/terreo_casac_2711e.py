"""Casa C Térreo, 27/11 (5): a soleira da porta principal num tom só, de fora a fora.

- **Soleira da porta principal** ("a soleira da porta principal é no mesmo tom de fora a fora"): acima da folha
  pivotante, entre a ponta da parede e a folha, a soleira era uma faixa mais clara e mais estreita, com o piso do hall
  ao lado. Agora esse trecho repete, linha a linha, a soleira de travertino escuro de baixo da folha, na mesma largura
  (a espessura da parede). A folha, a parede e o piso em volta ficam.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2711e.py [itens]
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
import um_pav_casaa_2511d as DD                  # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]

# a soleira: x da parede (2700 a 2713); o trecho de cima (da ponta da parede à folha) recebe as linhas do trecho de
# baixo da folha, `desce` unidades mais abaixo
SOLEIRA = dict(x=(2700.0, 2713.0), y=(1246.4, 1293.8), desce=54.0)
ITENS = {"soleira_principal": (2660.0, 1200.0, 2760.0, 1460.0)}


def soleira_principal(img, s=1.0, origem=(0.0, 0.0), q=SOLEIRA):
    def px(v, o): return int(round((v - o) * s))
    X0, X1 = px(q["x"][0], origem[0]), px(q["x"][1], origem[0])
    Y0, Y1 = px(q["y"][0], origem[1]), px(q["y"][1], origem[1])
    F0 = px(q["y"][0] + q["desce"], origem[1])
    img[Y0:Y1, X0:X1] = img[F0:F0 + (Y1 - Y0), X0:X1]
    return img


def item(img, nome, s=1.0, origem=(0.0, 0.0)):
    return globals()[nome](img, s, origem)


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

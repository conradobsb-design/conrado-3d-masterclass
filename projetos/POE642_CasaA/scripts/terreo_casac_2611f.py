"""Casa C Térreo, 6ª leva de 26/11: as folhas das portas de correr ligadas à parede e entre si.

Usuário (sobre a porta da sala TV e as da adega e do escritório, refeitas em `terreo_casac_2611e`): "essas portas
precisam estar conectadas com a parede. e também entre si. do contrário, passa a impressão que estão soltas".

- **Sala TV / circulação** (2 folhas): as folhas do PDF de ponta a ponta, a de cima da parede de cima (671,4) até 794,7
  e a de baixo de 789,9 até a parede de baixo (913,2), em trilhos lado a lado, sobrepostas 4,8 px na junta (antes cada
  folha parava 6 a 7 px antes da parede e havia 3 px de vão entre elas). As folhas antigas saem (o travertino de novo na
  faixa da porta) e as novas entram no padrão das esquadrias (`terreo_casaa_2511d.folhas`: o perfil claro, o vidro claro
  e o contorno fino), como as da adega e do escritório.
- **Adega e escritório** (4 folhas): a 1ª folha sobe até a parede de cima (929,6) e a 4ª desce até a de baixo (1189,4),
  sobre a soleira; as do meio já se encostam (sobrepostas nas juntas 1-2 e 3-4, de ponta a ponta na 2-3).

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611f.py [itens]
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
import terreo_casaa_2511d as D                   # noqa: E402
import terreo_casaa_2511g as G                   # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]

SALA_TV = dict(limpa=(1631.5, 670.8, 1641.2, 913.2),
               folhas=[(1634.5, 670.8, 1637.4, 794.7), (1637.4, 789.9, 1640.4, 913.2)])
CORRER = dict(folhas=[(2273.4, 929.6, 2276.3, 998.9), (2276.3, 994.1, 2279.3, 1059.5),
                      (2276.3, 1059.5, 2279.3, 1124.9), (2273.4, 1120.1, 2276.3, 1189.4)],
              dxs={"adega": 0.0, "escritorio": 286.6})


def sala_tv(img, s, origem, q=SALA_TV):
    img = G.refazer(img, s, origem, [(q["limpa"], "lr")], pena=1.0)
    return D.folhas(img, s, origem, q["folhas"])


def correr(img, s, origem, q=CORRER):
    for dx in q["dxs"].values():
        img = D.folhas(img, s, origem, [(r[0] + dx, r[1], r[2] + dx, r[3]) for r in q["folhas"]])
    return img


FUNC = {"sala_tv": sala_tv, "correr": correr}
ITENS = {"sala_tv": (1615.0, 655.0, 1660.0, 930.0), "correr": (2262.0, 915.0, 2580.0, 1205.0)}


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

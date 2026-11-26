"""Casa A 1º Pavimento, 26/11 (o recorte do 12K B: "ficou um detalhe para corrigir no primeiro pavimento").

- **Muro de baixo** (a divisa, à direita, fora da casa): o vão branco no meio da faixa cinza do muro (2845 a 2867, de
  1924 a 1935 px da final) sai; linha a linha, o vão recebe o tom do próprio muro de logo ao lado (a faixa tem o
  degradê de cima para baixo e é igual ao longo de x). Na varredura do muro inteiro, só esse vão era falha (os outros
  pontos claros na linha eram a folhagem acima do muro).

Final, prancha e 12K A e B.

  python3 um_pav_casaa_2611.py [muro]
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
import um_pav_casaa_2511c as C       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402

PLANTA = "A_1Pavimento"
MURO = dict(vao=(2842.5, 1923.5, 2870.5, 1935.5), fontes=[(2832.0, 2840.0), (2873.0, 2881.0)])


def muro(img, s, origem, q=MURO):
    jan, reg = C._reg(img, (2826.0, 1916.0, 2888.0, 1944.0), s, origem, folga=int(2 * s) + 2)
    xs, _ = V.coords(jan, s, origem)
    fonte = np.zeros(xs.shape, bool)
    for a, b in q["fontes"]:
        fonte |= (xs >= a) & (xs <= b)
    perfil = np.median(reg[:, fonte], axis=1)
    a = V.cob([V.ret(*q["vao"])], jan, s, origem)[..., None]
    reg = reg * (1 - a) + perfil[:, None, :] * a
    return C._gravar(img, jan, reg)


ITENS = {"muro": (2826.0, 1900.0, 2888.0, 1960.0)}
FUNC = {"muro": muro}


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
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            sx, org, cc = DD._registro(base, cinza, dz, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

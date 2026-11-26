"""Casa B Térreo, 4ª leva de 26/11: a beira das espreguiçadeiras da prainha sem o verde-água antigo.

Usuário (com o recorte das duas espreguiçadeiras de resina na prainha): "corrija o contorno para que não apareça o tom
antigo". Em `prainha_cinza_casab_2611` as espreguiçadeiras ficaram fora do cinza com 1 px de folga; a água rente a
elas (na final, 1 px; no 12K, o halo claro de uns 2 px) ficou no verde-água de antes. Agora, num anel de 4 px em volta
de cada uma (por fora da moldura, 930 a 1045 x 1152 a 1190 e 1229 a 1267), o que ainda é verde-água (matiz 70 a 100,
saturação 12 ou mais) vai para o tom da água cinza logo em volta (a mediana da faixa de 4 a 10 px, canal a canal, com a
textura e as juntas de antes): sem o verde e sem o halo claro.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casab_2611d.py
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
BEIRA = dict(pecas=[(930.0, 1152.0, 1045.0, 1190.0), (930.0, 1229.0, 1045.0, 1267.0)], anel=4.0, faixa=10.0,
             matiz=(70, 100), sat=12)


def beira_espreguicadeiras(img, s, origem, q=BEIRA):
    for r in q["pecas"]:
        a = q["faixa"] + 2.0
        jan, reg = C._reg(img, (r[0] - a, r[1] - a, r[2] + a, r[3] + a), s, origem, folga=0)
        peca = V.cob([V.ret(*r)], jan, s, origem)
        e = q["anel"]
        anel = V.cob([V.ret(r[0] - e, r[1] - e, r[2] + e, r[3] + e)], jan, s, origem) * (1 - peca)
        f = q["faixa"]
        fora = V.cob([V.ret(r[0] - f, r[1] - f, r[2] + f, r[3] + f)], jan, s, origem) * (1 - anel) * (1 - peca)
        hsv = cv2.cvtColor(np.clip(reg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
        verde = (hsv[..., 0] >= q["matiz"][0]) & (hsv[..., 0] <= q["matiz"][1]) & (hsv[..., 1] >= q["sat"])
        agua = (hsv[..., 0] > q["matiz"][1]) & (hsv[..., 0] < 130)                 # a água cinza (azulada) de hoje
        alvo = (fora > 0.99) & agua
        w = (anel > 0.5) & verde
        if not w.any() or alvo.sum() < 20:
            continue
        ganho = np.median(reg[alvo], axis=0) / np.maximum(np.median(reg[w], axis=0), 1.0)
        ws = np.clip(cv2.GaussianBlur(w.astype(np.float32), (0, 0), 0.35 * s), 0, 1) * (anel > 0.01)
        novo = reg * ganho[None, None, :]
        reg = reg * (1 - ws[..., None]) + novo * ws[..., None]
        img = C._gravar(img, jan, reg)
    return img


FUNC = {"beira_espreguicadeiras": beira_espreguicadeiras}
ITENS = {"beira_espreguicadeiras": (910.0, 1130.0, 1070.0, 1290.0)}


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

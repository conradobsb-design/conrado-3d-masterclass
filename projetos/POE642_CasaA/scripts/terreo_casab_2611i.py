"""Casa B Térreo, 9ª leva de 26/11: os adornos da opção 1 sobre as mesas de centro da varanda.

Usuário (sobre `POE642_CasaB_PH_Terreo_2611_adornos_mesas_opcoes.jpg`): "aplique a opção 1". Livros e flores secas:

- na mesa de nogueira (de trás, 1318 a 1406 x 834 a 869): a pilha de dois livros de linho bege, girada 8°, à
  esquerda (centro 1343 x 851,5), e o vaso de cerâmica orgânico com flores secas à direita (centro 1384 x 850), os dois
  da mesa de centro redonda de nogueira da biblioteca da Casa A;
- na mesa de freijó (da frente, 1290 a 1377 x 874 a 909): a tigela clara da mesa de espelho da biblioteca da Casa D
  (centro 1352 x 891,5).

Os recortes (vista de cima, fundo transparente) ficam em
`../biblioteca-objetos/02-terreo/sala-de-estar/adornos/` (livros-bege-a, vaso-flores-secas-a, tigela-clara-d), na
escala de 920 px/m das mesas de origem; aqui, 60 px/m. Cada peça com a sombra curta para baixo e à esquerda.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casab_2611i.py
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

PLANTA = "B_Terreo"
DZ = B.DZ
PASTA = EP.PROJ / "POE642_CasaA/biblioteca-objetos/02-terreo/sala-de-estar/adornos"
PX_M = 60.0                     # px da final por metro (Casa B)
ADORNOS = [                      # (peça, px/m do PNG, centro x, centro y, giro em graus)
    ("livros-bege-a.png", 920.0, 1343.0, 851.5, -8.0),
    ("vaso-flores-secas-a.png", 920.0, 1384.0, 850.0, 0.0),
    ("tigela-clara-d.png", 920.0, 1352.0, 891.5, 0.0),
]
SOMBRA = 0.32


def _colar(reg, jan, s, origem, png, ppm, cx, cy, giro):
    X0, Y0, X1, Y1 = jan
    H, W = reg.shape[:2]
    T = cv2.imread(str(PASTA / png), cv2.IMREAD_UNCHANGED).astype(np.float32)
    a = T[..., 3] / 255.0
    pre = np.dstack([T[..., :3] * a[..., None], a])
    k = PX_M * s / ppm
    if k < 1:                                        # reduzir antes de girar (sem serrilhado)
        pre = cv2.resize(pre, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        k = 1.0
    pc = ((pre.shape[1] - 1) / 2.0, (pre.shape[0] - 1) / 2.0)
    tx, ty = (cx - origem[0]) * s - 0.5 - X0, (cy - origem[1]) * s - 0.5 - Y0
    M = cv2.getRotationMatrix2D(pc, giro, k)
    M[0, 2] += tx - pc[0]
    M[1, 2] += ty - pc[1]
    w = cv2.warpAffine(pre, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    al = np.clip(w[..., 3], 0, 1)
    cor = w[..., :3] / np.maximum(al, 1e-4)[..., None]
    Ms = np.float32([[1, 0, -0.6 * s], [0, 1, 0.8 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(al, Ms, (W, H)), (0, 0), 0.7 * s) * (1 - al)
    reg = reg * (1 - SOMBRA * sb)[..., None]
    return reg * (1 - al[..., None]) + cor * al[..., None]


def adornos_mesas(img, s, origem):
    jan = V.janela(img, (1300.0, 820.0, 1420.0, 925.0), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    for png, ppm, cx, cy, giro in ADORNOS:
        reg = _colar(reg, jan, s, origem, png, ppm, cx, cy, giro)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"adornos_mesas": adornos_mesas}
ITENS = {"adornos_mesas": (1270.0, 815.0, 1430.0, 930.0)}


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

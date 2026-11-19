"""A escada "SOBE PARA O DECK" da Casa A Subsolo: o lance acima do corte transparente (19/11, o usuário: "os degraus
devem estar transparentes e não brancos, se lembra?" — a regra da escada principal da Casa E, 17/11:
`escada_principal_casae_1711`).

À esquerda da diagonal de corte do PDF ((921,4; 1057,9) a (957,5; 1130,1), com o símbolo de quebra) os degraus estavam
brancos. Agora aparece o piso de baixo (o Bege Bahia da varanda do Subsolo, um recorte do mesmo piso) e, por cima, só o
desenho dos degraus de antes, transparente (`VISTA`): as quinas aparecem de leve, sem o branco. Final (e a
manuscrita), prancha e 12K A e B (registro local).

  python3 escada_subsolo_casaa_1911.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402

PLANTA = "A_Subsolo"
CAIXA = (895.0, 1050.0, 968.0, 1134.0)                                              # px da final
LANCE = [(903.0, 1058.4), (922.1, 1058.4), (957.5, 1129.4), (903.0, 1129.4)]        # acima do corte
PISO_D = (230.0, 100.0)            # o Bege Bahia da varanda (o mesmo recorte, 230 px à direita e 100 abaixo)
VISTA = 0.55


def aplicar(img, X0, Y0, s):
    """`img` na grade (px da final * s + (X0, Y0))."""
    P = lambda x, y: (x * s + X0, y * s + Y0)
    a0, b0 = P(CAIXA[0], CAIXA[1])
    a1, b1 = P(CAIXA[2], CAIXA[3])
    A0, B0, A1, B1 = int(a0), int(b0), int(np.ceil(a1)), int(np.ceil(b1))
    H, W = B1 - B0, A1 - A0
    k = 8
    pts = np.array([[(P(x, y)[0] - A0) * k, (P(x, y)[1] - B0) * k] for x, y in LANCE])
    m = np.zeros((H * k, W * k), np.uint8)
    cv2.fillPoly(m, [np.round(pts).astype(np.int32)], 255)
    a = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    reg = img[B0:B1, A0:A1].astype(np.float32)
    dx, dy = int(round(PISO_D[0] * s)), int(round(PISO_D[1] * s))
    piso = img[B0 + dy:B1 + dy, A0 + dx:A1 + dx].astype(np.float32)
    dentro = a > 0.99
    med = np.median(reg[dentro].reshape(-1, 3), axis=0)
    novo = piso + VISTA * (reg - med[None, None])
    out = reg * (1 - a[..., None]) + novo * a[..., None]
    img[B0:B1, A0:A1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def main():
    c, pav = PLANTA.split("_")
    antes = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        im = aplicar(im, 0.0, 0.0, 1.0)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in "AB":
        f = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(f)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        mapa, cc = EP.registro_12k(antes, cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), dz, (800, 960, 1400, 1360))
        X0, Y0 = mapa(0.0, 0.0)
        s = (mapa(1000.0, 0.0)[0] - X0) / 1000.0
        im = aplicar(im, X0, Y0, s)
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(f, quality=95, subsampling=0, dpi=dpi)
        print(f"   {f.name}: registro {cc:.3f}")
        del im


if __name__ == "__main__":
    main()

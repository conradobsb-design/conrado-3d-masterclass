"""A porta de correr do HALL da Casa A Subsolo (19/11, o usuário: "subsolo casa A - corrigir porta do hall").

As duas folhas (a de cima no trilho de dentro, a de baixo no de fora) estavam desiguais: a de cima meio vidro, meio
escura, a de baixo toda cinza-escura. Passam ao padrão das esquadrias (`vidros_claros_1911`): cada folha com o perfil
cinza claro, o vidro claro e a sua linha preta fina por fora; o contorno antigo (o retângulo em volta das duas) sai.
Final (e a manuscrita), prancha e 12K A e B.

  python3 porta_hall_subsolo_1911.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vidros_claros_1911 as VC  # noqa: E402

PLANTA = "A_Subsolo"
FOLHAS = [[(1878.2, 1060.9, 1879.4, 1131.9), (1879.4, 1060.9, 1880.6, 1131.9)],    # a de cima (trilho de dentro)
          [(1875.8, 1133.1, 1877.0, 1204.2), (1877.0, 1133.1, 1878.2, 1204.2)]]    # a de baixo (trilho de fora)
UNIAO = FOLHAS[0] + FOLHAS[1]


def porta(img, g, escala=1.0, origem=(0.0, 0.0), traco=0.5, inpaint=True):
    """As duas folhas: o preto antigo em volta da porta sai uma vez só; depois cada folha é desenhada."""
    x0, y0, x1, y1 = EP.caixa(UNIAO)
    m = int(np.ceil(5 * escala)) + 2
    X0, Y0 = max(int((x0 - origem[0]) * escala) - m, 0), max(int((y0 - origem[1]) * escala) - m, 0)
    X1 = min(int(np.ceil((x1 - origem[0]) * escala)) + m, img.shape[1])
    Y1 = min(int(np.ceil((y1 - origem[1]) * escala)) + m, img.shape[0])
    reg = img[Y0:Y1, X0:X1]
    org = (origem[0] + X0 / escala, origem[1] + Y0 / escala)
    dentro = np.zeros(reg.shape[:2], bool)
    for f in FOLHAS:
        dentro |= VC.forma(f, escala, org, reg.shape[:2], dil=0.01)
    perto = VC.forma(UNIAO, escala, org, reg.shape[:2], dil=3.0)
    preto = ((reg.astype(np.float32).mean(2) < 75) & perto & ~dentro).astype(np.uint8)
    if preto.any():
        preto = cv2.dilate(preto, np.ones((3, 3), np.uint8))
        img[Y0:Y1, X0:X1] = cv2.inpaint(reg.copy(), preto, max(2, int(round(1.5 * escala))), cv2.INPAINT_TELEA)
    for f in FOLHAS:
        img = VC.redesenhar_base(img, f, escala=escala, origem=origem, traco=traco, inpaint=False)
    return img


def main():
    c, pav = PLANTA.split("_")
    VC.redesenhar_base = VC.redesenhar
    antes = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        im = porta(im, UNIAO)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    # 12K: o lugar da porta como em vidros_claros_1911.doze_k (o desenho troca pelo das duas folhas)
    VC.redesenhar = porta
    VC.doze_k(PLANTA, antes, [UNIAO])
    VC.redesenhar = VC.redesenhar_base


if __name__ == "__main__":
    main()

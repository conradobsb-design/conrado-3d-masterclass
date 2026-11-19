"""A folha de correr da porta do DEPÓSITO da Casa A Subsolo, quina a quina com a parede (19/11, o usuário: "olhando do
alto a porta do depósito, parece que ela está fora da quina a quina com a parede. o contorno deixou dois lados extremos
claros").

A folha (no render, uma barra clara com as pontas arredondadas, 1346-1399, meio px acima da face da parede) passa a
retângulo de 1346 (a face do bloco da parede) a 1399, com a borda de baixo na face da parede (y = 1024): vidro claro,
perfil cinza e a linha fina em volta da folha toda (sem as pontas claras de fora). Final (e a manuscrita), prancha e 12K.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vidros_claros_1911 as VC  # noqa: E402

PLANTA = "A_Subsolo"
FOLHA = [(1346.0, 1021.5, 1399.0, 1024.0)]
VELHA = (1346.0, 1020.0, 1402.0, 1027.0)          # a folha antiga com o contorno e as pontas (px da final)


def folha(img, g, escala=1.0, origem=(0.0, 0.0), traco=0.5, inpaint=True):
    a0, b0 = int((VELHA[0] - origem[0]) * escala), int((VELHA[1] - origem[1]) * escala)
    a1, b1 = int(np.ceil((VELHA[2] - origem[0]) * escala)), int(np.ceil((VELHA[3] - origem[1]) * escala))
    m = int(np.ceil(3 * escala))
    A0, B0, A1, B1 = max(a0 - m, 0), max(b0 - m, 0), min(a1 + m, img.shape[1]), min(b1 + m, img.shape[0])
    reg = img[B0:B1, A0:A1].copy()
    lum = reg.astype(np.float32).mean(2)
    cor = reg.astype(np.float32).max(2) - reg.astype(np.float32).min(2)
    parede = (lum > 60) & (lum < 105) & (cor < 18)
    mask = np.zeros(lum.shape, np.uint8)
    mask[b0 - B0:b1 - B0, a0 - A0:a1 - A0] = 1          # a folha antiga inteira (à direita da face do bloco)
    img[B0:B1, A0:A1] = cv2.inpaint(reg, mask, max(2, int(round(1.5 * escala))), cv2.INPAINT_TELEA)
    return VC.redesenhar_base(img, FOLHA, escala=escala, origem=origem, traco=traco, inpaint=False)


def main():
    c, pav = PLANTA.split("_")
    VC.redesenhar_base = VC.redesenhar
    antes = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        im = folha(im, FOLHA)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    VC.redesenhar = folha
    VC.doze_k(PLANTA, antes, [[(1351.0, 1022.0, 1393.0, 1025.5)]])      # o lugar pela folha antiga
    VC.redesenhar = VC.redesenhar_base


if __name__ == "__main__":
    main()

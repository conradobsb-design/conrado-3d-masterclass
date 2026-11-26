"""Casa C Subsolo, 7ª leva de 26/11: a parede nas duas pontas da fachada de vidro da academia.

Usuário (sobre os recortes do 12K): "corrigir a parede" (o pé da fachada, junto à porta do depósito) e "corrigir a parede
para não deixar a soleira sobrepor ela" (o topo, junto ao canto da parede da academia).

Pelo PDF, as duas paredes são retas de ponta a ponta: a de baixo (1052,3 a ... x 737,1 a 746,0) passa por baixo da
fachada com o topo em 737,1, e a de cima tem a face de baixo em 331 até o canto (1076,4), com a soleira da fachada logo
abaixo dela.

- **o topo**: a soleira (e a folha de vidro ao lado) subia até 331,0 e cobria o pé da parede, que em toda a varanda
  termina em 332,3 (a beira da parede e o contorno escuro de 331,3 a 332,1); agora o pé da parede passa por cima da
  soleira e do vidro até o canto, refeito pela mesma parede 25 px à esquerda (no canto, o contorno da face da direita desce
  até ele), e a soleira começa logo abaixo dele; junto à soleira, o travertino até 334,2 vem do mesmo lugar (sai o risquinho claro do canto); o brilho claro da folha de vidro que entrava na parede (a 1075,
  de 325 a 331) vira a parede de logo acima;
- **o pé**: a parede de 1052,4 a 1084,5 refeita pela mesma parede 32 px à direita (o topo reto em 737, sem o dente junto
  à fachada nem as marcas claras das folhas de vidro; a face de baixo reta, com o contorno e a sombra desde a ponta
  junto à porta do depósito); a linha clara das folhas de vidro logo acima da parede, sobre a madeira (1076 a 1083), vira
  a madeira de 32 px à direita.

Final, prancha e 12K A e B (pelo registro local).

  python3 subsolo_casac_2611g.py
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
import um_pav_casaa_2511d as DD      # noqa: E402
import subsolo_casac_2611 as A       # noqa: E402

PLANTA = A.PLANTA
DZ = A.DZ
TOPO = dict(brilho=((1074.6, 323.5, 1075.95, 330.85), (0.0, -6.0), "t"),
            pe_esq=((1056.5, 330.3, 1063.5, 334.2), (-25.0, 0.0), "lb"),
            pe=((1063.5, 330.3, 1076.2, 332.6), (-25.0, 0.0), "b"),
            face=((1075.95, 330.3, 1076.75, 332.2), (0.0, -4.0), ""))
PE = dict(parede=((1052.4, 736.95, 1084.5, 748.4), (32.0, 0.0), "rb"),
          vidro=((1075.6, 736.3, 1083.5, 737.2), (32.0, 0.0), "lrt"))


def parede_topo(img, s, origem, q=TOPO):
    # o brilho da folha de vidro dentro da parede vira a parede de logo acima; o pé da parede (a beira e o contorno
    # escuro) passa por cima da soleira e do vidro até o canto, como é na parede logo à esquerda
    for chave, pena in (("brilho", 0.6), ("pe_esq", 0.5), ("pe", 0.5), ("face", 0.5)):
        r, d, lados = q[chave]
        img = A.copiar(img, s, origem, r, d, lados, pena=pena)
    return img


def parede_pe(img, s, origem, q=PE):
    img = A.copiar(img, s, origem, *q["parede"], pena=0.8)
    return A.copiar(img, s, origem, *q["vidro"], pena=0.4)


FUNC = {"parede_topo": parede_topo, "parede_pe": parede_pe}
ITENS = {"parede_topo": (1020.0, 290.0, 1100.0, 360.0), "parede_pe": (1030.0, 705.0, 1130.0, 770.0)}


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

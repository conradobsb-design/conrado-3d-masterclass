"""Casa C Subsolo, 2ª leva de 26/11: as soleiras no travertino mais escuro.

Usuário, sobre o creme das soleiras de `subsolo_casac_2611` ("esses pisos já foram atualizados?", "pode utilizar o
travertino mais escuro"): todas as soleiras desta planta na pedra do travertino mais escuro, sem contorno (o padrão do
Subsolo da Casa B, `G.soleira_trav` a 84%):

- os vãos dos vidros e o peitoril da janela do box: os itens `vidro_sauna`, `fachada_academia` e `janela_box` de
  `subsolo_casac_2611` de novo, agora com a pedra (a soleira cobre a de antes; os vidros e o contorno da janela voltam
  por cima, iguais);
- as três portas (sauna, BH academia e depósito), que vinham em creme com os dois fios cinza do contorno: a pedra de
  parede a parede (o vão medido na imagem, onde a parede está meio pixel ao lado do PDF), e os fios que passavam da face
  da parede viram o piso de logo ao lado (menos onde está a folha da porta).

Final, prancha e 12K A e B (cada item pelo registro local).

  python3 subsolo_casac_2611b.py [item ...]
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
# (a soleira, [(o fio de fora, o deslocamento do piso que o cobre, os lados com emenda suave)])
PORTAS = {
    "soleira_sauna": ((814.0, 750.5, 823.0, 795.0),
                      [((812.9, 750.5, 814.0, 795.0), (-2.2, 0.0), "l"),
                       ((823.0, 750.5, 824.1, 792.6), (2.2, 0.0), "r")]),          # a folha da porta em 792,9
    "soleira_bh": ((888.0, 753.4, 897.0, 804.4),
                   [((886.9, 753.4, 888.0, 804.4), (-2.2, 0.0), "l"),
                    ((897.0, 756.2, 898.1, 804.4), (2.2, 0.0), "r")]),             # a folha da porta até 755,8
    "soleira_deposito": ((1001.5, 737.0, 1052.5, 746.0),
                         [((1001.5, 735.9, 1052.5, 737.0), (0.0, -2.2), "t"),
                          ((1005.0, 746.0, 1052.5, 747.1), (0.0, 2.2), "b")]),     # a folha da porta em 1001 a 1004
}


def _porta(nome):
    def f(img, s, origem, q=PORTAS[nome]):
        sol, fios = q
        for r, d, lados in fios:
            img = A.copiar(img, s, origem, r, d, lados, pena=0.6)
        return A.soleira(img, s, origem, [sol])
    return f


FUNC = {n: A.FUNC[n] for n in ("vidro_sauna", "fachada_academia", "janela_box")}
ITENS = {n: A.ITENS[n] for n in FUNC}
for _n in PORTAS:
    FUNC[_n] = _porta(_n)
ITENS["soleira_sauna"] = (800.0, 740.0, 840.0, 805.0)
ITENS["soleira_bh"] = (875.0, 742.0, 915.0, 812.0)
ITENS["soleira_deposito"] = (990.0, 725.0, 1065.0, 760.0)


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

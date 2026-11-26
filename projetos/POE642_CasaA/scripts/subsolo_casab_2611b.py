"""Casa B Subsolo, 2ª leva de 26/11 (os recortes do 12K B, sobre `subsolo_casab_2611.py`).

- **Portas quina a quina** ("corrigir portas: deixá-las quina a quina com a parede. não pode estar flutuando"): nas 4
  portas de giro (circulação para a sauna, circulação para o BH sauna, BH serviço e depósito), no lugar dos batentes, a
  parede: do toco de parede até a face da folha (a quina da folha, do lado da dobradiça, na quina da parede) e, do outro
  lado, da ponta da folha fechada (o comprimento da folha do PDF) até o toco de baixo; a soleira fica entre as duas.
- **BH sauna, a parede da ducha** ("preencha a parede de fora a fora, sem esse vão em frente ao chuveiro. deixe o
  chuveiro encostado na parede"): o nicho (1148,5 a 1153,2 x 722,7 a 746,6) vira parede, com a face reta; a canopla
  da ducha em metal escovado encostada na face da parede, o braço como está.
- **BH sauna, a bancada** ("corrija o tom da bancada para que fique uniforme, preservando a cuba"): o granito da
  bancada (o trecho de cima, a volta da cuba, o lado da torneira e o trecho de baixo) no tom do trecho de cima: a luz
  local (a média alisada, só na bancada) trocada pelo tom de lá, o grão da pedra fica; a bacia da cuba e a torneira
  ficam como estão; a barra cinza da frente vai até o alto como no PDF (671,2), no lugar do trecho claro de baixo da
  cuba.
- **Sauna, as pontas do vidro** ("o vidro não pode penetrar na parede, mas sim encostar nela"): o vidro de cima termina
  na face da parede da direita (1060,4) e o vertical na de baixo (704,6); a parede volta sobre a ponta que entrava.

Final, prancha e 12K A e B (cada item pelo registro local).

  python3 subsolo_casab_2611b.py [item ...]
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
import subsolo_casab_2611 as B1      # noqa: E402

PLANTA = "B_Subsolo"
DZ = B1.DZ

# ----------------------------------------------------------------------------------------------------------------------
# (a parede do lado da dobradiça, até a face da folha; a do outro lado, da ponta da folha fechada até o toco)
PORTAS = {"porta_circ_sauna": [(1144.3, 613.6, 1153.2, 616.7), (1144.3, 658.5, 1153.2, 661.6)],
          "porta_circ_bh_sauna": [(1233.9, 610.0, 1245.8, 613.7), (1233.9, 661.5, 1245.8, 664.6)],
          "porta_bh_servico": [(1439.8, 332.9, 1448.8, 336.1), (1439.8, 371.9, 1448.8, 375.1)],
          "porta_deposito": [(1511.5, 329.9, 1520.5, 333.1), (1511.5, 374.9, 1520.5, 378.1)]}


def _porta(nome):
    return lambda img, s, origem: B1.pintar(img, s, origem, PORTAS[nome])


NICHO = dict(parede=(1148.3, 722.5, 1153.2, 746.8), canopla=(1153.2, 732.7, 1155.3, 737.7, 0.35))


def nicho_parede(img, s, origem, q=NICHO):
    img = B1.pintar(img, s, origem, [q["parede"]])
    jan, reg = C._reg(img, (1146.0, 728.0, 1160.0, 742.0), s, origem, folga=int(2 * s) + 2)
    reg, _ = C._metal(reg, jan, s, origem, q["canopla"], DD.BOX, "y")
    return C._gravar(img, jan, reg)


BANCADA = dict(pedra=[(1338.3, 607.4, 1358.8, 621.2), (1326.2, 621.2, 1358.8, 671.4), (1343.3, 671.2, 1358.8, 704.3)],
               fica=[(1327.6, 621.8, 1346.4, 669.0), (1345.8, 641.5, 1358.8, 651.5)],
               ref=(1340.0, 608.5, 1357.0, 619.5), sig=2.0, pena=0.5,
               barra=(1337.8, 671.0, 1343.5, 676.6), barra_desloc=6.5)


def barra_inteira(img, s, origem, q=BANCADA):
    """A barra cinza da frente (ARQ_BANCADAS 1338,2 a 1343,2, de 671,2 a 704,3) até o alto, como no PDF: o trecho claro
    acima dela (a faixa de baixo da cuba) coberto pela própria barra, deslocada de baixo."""
    x0, y0, x1, y1 = q["barra"]
    jan, reg = C._reg(img, (x0 - 1, y0 - 1, x1 + 1, y1 + q["barra_desloc"] + 1), s, origem, folga=int(2 * s) + 2)
    fonte = np.roll(reg, -int(round(q["barra_desloc"] * s)), axis=0)
    a = V.cob([V.ret(*q["barra"])], jan, s, origem)[..., None]
    return C._gravar(img, jan, reg * (1 - a) + fonte * a)


def bancada_bh_sauna(img, s, origem, q=BANCADA):
    img = barra_inteira(img, s, origem, q)
    jan, reg = C._reg(img, (1322.0, 603.0, 1362.0, 708.0), s, origem, folga=int(4 * s) + 2)
    m = V.cob([V.ret(*r) for r in q["pedra"]], jan, s, origem)
    f = V.cob([V.ret(*r) for r in q["fica"]], jan, s, origem)
    m = np.clip(m - f, 0, 1)
    mr = V.cob([V.ret(*q["ref"])], jan, s, origem)
    alvo = (reg * mr[..., None]).sum((0, 1)) / max(mr.sum(), 1.0)
    sig = q["sig"] * s
    num = cv2.GaussianBlur(reg * m[..., None], (0, 0), sig)
    den = cv2.GaussianBlur(m, (0, 0), sig)[..., None]
    luz = num / np.maximum(den, 1e-3)
    novo = reg - luz + alvo[None, None, :]
    d = cv2.distanceTransform((m > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / max(s, 1e-3)
    a = (m * np.clip(d / q["pena"], 0, 1))[..., None]
    return C._gravar(img, jan, reg * (1 - a) + novo * a)


SAUNA_PONTAS = [(1060.4, 597.3, 1064.8, 606.4), (958.5, 704.6, 966.5, 708.0)]


def sauna_pontas(img, s, origem):
    return B1.pintar(img, s, origem, SAUNA_PONTAS)


# ----------------------------------------------------------------------------------------------------------------------
ITENS = {"porta_circ_sauna": (1138.0, 606.0, 1162.0, 668.0), "porta_circ_bh_sauna": (1226.0, 604.0, 1254.0, 670.0),
         "porta_bh_servico": (1432.0, 326.0, 1456.0, 380.0), "porta_deposito": (1504.0, 324.0, 1528.0, 384.0),
         "nicho_parede": (1140.0, 714.0, 1164.0, 756.0), "bancada_bh_sauna": (1320.0, 600.0, 1364.0, 710.0),
         "sauna_pontas": (945.0, 590.0, 1075.0, 715.0)}
FUNC = {"nicho_parede": nicho_parede, "bancada_bh_sauna": bancada_bh_sauna, "sauna_pontas": sauna_pontas}
FUNC.update({n: _porta(n) for n in PORTAS})


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

"""1º Pavimento da Casa E, 17/11 ("Você está usando a cortina padrão que a gente vem utilizando? Se não, tem que trocar
todos onde tem cortina pela cortina que a gente utiliza"): as cortinas das 5 suítes, que eram a linha fina de 11/11 (e,
na master, só os pedacinhos franzidos), na C4 do Térreo da E e da D (`cortinas_padrao_casad_1611.aplicar`): o linho em
ondas com o trilho grafite do lado do vidro, nos trechos do PDF (`final3840_casac.trechos_cortina_tc`: 10 trechos, os
da mesma janela unidos num trilho só, de parede a parede), o pano de 0,22 m, o linho 0,82 e a sombra inteira; o pano e o
trilho de antes saem (o piso de logo de dentro, em espelho). O Térreo da E já está na C4 (f5eb397) e o Subsolo não tem
cortina no PDF. Não há 12K do 1º Pavimento da E.

  python3 cortinas_1pav_casae_1711.py [--saida <png>]
"""
import argparse
import sys
from pathlib import Path

import cv2

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
FINAL = AQUI.parents[1] / "POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_final.png"


def main():
    import final3840_casae as FE
    import cortinas_padrao_casad_1611 as CP
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida")
    a = ap.parse_args()
    Q = FE.QuadroE("1Pavimento")
    out = CP.aplicar(Q, cv2.imread(str(FINAL)), q=dict(CP.CORTINAS_D, extra=[]))
    cv2.imwrite(a.saida or str(FINAL), out)


if __name__ == "__main__":
    main()

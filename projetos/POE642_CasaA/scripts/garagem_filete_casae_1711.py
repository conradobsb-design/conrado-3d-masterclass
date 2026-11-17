"""A linha da laje da garagem do Térreo da Casa E num filete contínuo (17/11, usuário: "CORRIGE AQUI. TEM UM FILETE COMO
DIZ NA RECOMENDAÇÃO DA IMAGEM ANEXA"; a recomendação do cliente: "Representar essas linhas na cor cinza ou preta sem ser
tracejada"), na final e direto nos 12K A e B.

A projeção tracejada tinha saído (`bege_garagem_terreo_casae_1711`, "não haverá tracejado para projeções"); a linha
volta como filete contínuo, na reta do PDF (a cadeia "laje da garagem (1)", y 485,9), da face da parede da esquerda
até a linha da borda da garagem à direita, no mesmo cinza escuro e na mesma espessura dela (1 px da final).

  python3 garagem_filete_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 garagem_filete_casae_1711.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
import danae_foto as DF                                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"

# px da final: o filete (da face da parede até a linha da borda da garagem) e a cor da linha da borda
FILETE = {"ret": (2487.5, 485.4, 3038.0, 486.4), "cor": (64, 66, 69)}
CAIXAS = ((2465, 455, 2545, 520), (2990, 455, 3070, 520))     # as duas pontas, para o ajuste local no 12K


def aplicar(img, mp, q=FILETE):
    out = img.copy()
    if mp.ref is not None:
        # o ajuste local: a média das duas pontas (a quina da parede e a linha da borda)
        ms = [mp.local(out, c) for c in CAIXAS]
        mp = Mapa(mp.s, (float(np.mean([m.t[0] for m in ms])), float(np.mean([m.t[1] for m in ms]))))
    CB.pintar(out, mp, [(q["ret"], "ret", q["cor"], 0)])
    print("    garagem: a linha da laje num filete contínuo cinza escuro, da parede à borda da garagem")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa()))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

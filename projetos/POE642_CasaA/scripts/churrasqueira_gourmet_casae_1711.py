"""Térreo da Casa E, 17/11 ("Diminua um pouco o tamanho da churrasqueira"): a grelha da bancada de trás da gourmet
(`pedidos_terreo_casae_1611.GOURMET`, "grelha_px" 62) a 82% do tamanho, no mesmo centro; a bancada de granito marrom
tabaco em volta (a de logo à direita da grelha, deslocada, com as beiras de cima e de baixo). Na final e direto nos 12K A
e B (o afim afinado na caixa).

  python3 churrasqueira_gourmet_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 churrasqueira_gourmet_casae_1711.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
# px da final: a grelha (o quadro de fora), o deslocamento da bancada limpa e a escala
Q = {"grelha": (1105.4, 603.8, 1168.4, 644.4), "fonte_dx": 68.0, "escala": 0.82, "nitidez": 0.7, "caixa": (1080, 585, 1260, 660)}


def aplicar(img, m, q=Q):
    out = img.copy()
    x0, y0, x1, y1 = m.ret(q["grelha"])
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    grelha = img[Y0:Y1, X0:X1].copy()
    dx = int(round(q["fonte_dx"] * m.s))
    out[Y0:Y1, X0:X1] = img[Y0:Y1, X0 + dx:X1 + dx]
    k = q["escala"]
    w, h = X1 - X0, Y1 - Y0
    nw, nh = int(round(w * k)), int(round(h * k))
    peq = cv2.resize(grelha, (nw, nh), interpolation=cv2.INTER_AREA).astype(np.float32)
    # as barras finas perdem contraste na redução: um reforço leve de nitidez (unsharp)
    peq = np.clip(peq + q["nitidez"] * (peq - cv2.GaussianBlur(peq, (0, 0), 0.8 * max(1.0, m.s / 2))), 0,
                  255).astype(np.uint8)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a, b = int(round(cx - nw / 2)), int(round(cy - nh / 2))
    out[b:b + nh, a:a + nw] = peq
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa()))
        print("    gourmet: a churrasqueira a 82%, centrada no módulo, a bancada em volta")
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp.local(img, Q["caixa"]))
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

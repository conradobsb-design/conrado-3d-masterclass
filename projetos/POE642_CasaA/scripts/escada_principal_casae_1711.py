"""A escada principal do Térreo da Casa E: o lance acima do corte transparente (17/11, usuário: "A parte que não for do
nível desse pavimento, você tem que deixar transparente. O degrau não pode ficar branco."), na final e direto nos 12K
A e B.

No PDF (ARQ_ESCADAS E RAMPAS) os degraus deste nível são os cheios, à direita da linha de corte (a diagonal de
(2065,6; 960,6) a (2109,25; 1047,9)); à esquerda dela os degraus são tracejados: é o lance que já passou do plano de
corte. No render esse lance estava em degraus brancos. Agora, à esquerda da diagonal, aparece o piso de baixo (o
travertino do Térreo, o de logo abaixo do jardim, num tom só e com os veios deitados) e, por cima dele, só o desenho
dos degraus de antes, transparente (o quanto cada px dos degraus brancos difere do tom deles, a `VISTA`): as quinas
dos degraus aparecem de leve, sem o branco. A borda do jardim embaixo desse lance fica contínua como a do lance de
baixo (sem o tracejado).

  python3 escada_principal_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 escada_principal_casae_1711.py final
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

# px da final
CAIXA = (1860, 940, 2235, 1065)
LANCE = [(1877.0, 960.6), (2065.6, 960.6), (2109.25, 1047.3), (1877.0, 1047.3)]   # acima do corte
PISO_D = (0, 170)            # o travertino de logo abaixo do jardim (o mesmo recorte, 170 px abaixo)
VISTA = 0.55                 # quanto do desenho dos degraus fica por cima do piso
BORDA = {"faixa": (1877.0, 1047.9, 2109.0, 1049.6), "fonte_x": (2118.0, 2212.0)}   # a borda do jardim


def _alfa_poli(m, pts, X0, Y0, forma):
    k = 8
    P = np.array([[(m.x(x) - X0) * k, (m.y(y) - Y0) * k] for x, y in pts], np.float64)
    A = np.zeros((forma[0] * k, forma[1] * k), np.uint8)
    cv2.fillPoly(A, [np.round(P).astype(np.int32)], 255)
    return cv2.resize(A, (forma[1], forma[0]), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def aplicar(img, mp):
    out = img.copy()
    m = mp.local(out, CAIXA) if mp.ref is not None else mp
    s = m.s
    X0, Y0, X1, Y1 = m.reti(CAIXA)
    forma = (Y1 - Y0, X1 - X0)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    a = _alfa_poli(m, LANCE, X0, Y0, forma)
    dy = int(round(PISO_D[1] * s))
    piso = out[Y0 + dy:Y1 + dy, X0:X1].astype(np.float32)
    dentro = a > 0.99
    med = np.median(reg[dentro].reshape(-1, 3), axis=0)
    novo = piso + VISTA * (reg - med[None, None])
    reg = reg * (1 - a[..., None]) + novo * a[..., None]
    # a borda do jardim embaixo do lance de cima: a do lance de baixo, contínua (sem o tracejado)
    bx0, by0, bx1, by1 = m.reti(BORDA["faixa"])
    fx0, fx1 = int(round(m.x(BORDA["fonte_x"][0]))), int(round(m.x(BORDA["fonte_x"][1])))
    fonte = np.median(out[by0:by1, fx0:fx1].astype(np.float32), axis=1)          # o perfil vertical da borda
    faixa = np.repeat(fonte[:, None, :], bx1 - bx0, axis=1)
    fb = np.zeros(forma, np.float32)
    fb[by0 - Y0:by1 - Y0, bx0 - X0:bx1 - X0] = 1
    fb = cv2.GaussianBlur(fb, (0, 0), 0.4 * s) * fb
    cheio = reg.copy()
    cheio[by0 - Y0:by1 - Y0, bx0 - X0:bx1 - X0] = faixa
    reg = reg * (1 - fb[..., None]) + cheio * fb[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    escada principal: o lance acima do corte transparente (o travertino por baixo, os degraus a "
          f"{int(VISTA * 100)}%), a borda do jardim contínua")
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

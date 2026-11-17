"""Térreo da Casa E, 17/11 ("Revise o armário do DCE"): em 16/11, o passo dos armários lisos
(`pedidos_terreo_casae_1611.armarios`, "DCE": (2236, 556, 2264, 612)) pintou um retângulo cor de armário fora do lugar,
por cima do guarda-roupa aberto com cabides (no retângulo do PDF, `final3840_casae.ARMARIO_DCE_TER_E`) e da folha da
porta. O retângulo sai: o guarda-roupa e a folha voltam inteiros e o resto vira o piso marrom de hoje.

- Na final: o guarda-roupa e a folha de antes de 16/11 (a final de bfbf5c3^, só dentro dos retângulos deles) e o piso
  de hoje copiado de perto no resto.
- Nos 12K A e B (não há 12K de antes): o guarda-roupa continuado de baixo para cima a partir da parte que ficou inteira
  (abaixo de y 615,6), no passo dos cabides (7,14 px da final), e o friso de cima no tom do friso que ficou; a folha da
  mesma forma, do pé até a ponta dela (y 586); o piso de hoje de perto no resto.

  python3 armario_dce_casae_1711.py final
  python3 armario_dce_casae_1711.py doze [--opcao AB]
"""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from instalacao_terreo_casad_1711 import _remenda           # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
REPO = RAIZ.parent
ANTES = "bfbf5c3^"

# px da final
Q = {"sobra": (2232.5, 555.0, 2266.5, 615.6),          # o retângulo pintado em 16/11, com o contorno e a sombra
     "armario": (2225.5, 563.6, 2257.9, 629.0),          # o guarda-roupa aberto (friso, fundo claro, cabides, varão)
     "folha": (2257.9, 586.0, 2267.5, 629.0),            # a folha da porta, aberta junto ao guarda-roupa
     "inteiro_y": 615.6,                                  # daqui para baixo, o guarda-roupa e a folha ficaram inteiros
     "passo": 7.14,                                       # o passo dos cabides
     "friso": (2227.0, 563.6, 2234.5, 564.8),             # a amostra do friso de cima (a parte que ficou)
     "piso": [((2257.9, 555.0, 2266.5, 586.0), (9.0, 0.0)), ((2232.5, 555.0, 2257.9, 563.6), (0.0, -7.0))],
     "caixa": (2200, 540, 2290, 640)}


def _dentro(r, X, Y, m):
    a = m.ret(r)
    return (X + 0.5 >= a[0]) & (X + 0.5 < a[2]) & (Y + 0.5 >= a[1]) & (Y + 0.5 < a[3])


def final(img, q=Q):
    out = img.copy()
    pre = cv2.imdecode(np.frombuffer(subprocess.run(
        ["git", "-C", str(REPO), "show", f"{ANTES}:projetos/POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"],
        capture_output=True, check=True).stdout, np.uint8), cv2.IMREAD_COLOR)
    m = Mapa()
    for r, d in q["piso"]:
        _remenda(out, m, r, [d], None)
    x0, y0, x1, y1 = (int(round(v)) for v in q["sobra"])
    Y, X = np.mgrid[y0:y1, x0:x1]
    peca = _dentro(q["armario"], X, Y, m) | _dentro(q["folha"], X, Y, m)
    out[y0:y1, x0:x1][peca] = pre[y0:y1, x0:x1][peca]
    return out


def _continua(out, m, r, ate, passo):
    """O retângulo r (px da final) refeito de baixo para cima, linha a linha, a partir de `ate` (a parte inteira), cada
    linha copiada da que está `passo` abaixo (em px da imagem, no passo dos cabides)."""
    X0, X1 = int(round(m.x(r[0]))), int(round(m.x(r[2])))
    Yt, Yb = int(round(m.y(r[1]))), int(round(m.y(ate)))
    p = passo * m.s
    for Yi in range(Yb - 1, Yt - 1, -1):
        ys = Yi + p
        a, f = int(np.floor(ys)), ys - np.floor(ys)
        out[Yi, X0:X1] = np.clip(np.round(out[a, X0:X1] * (1 - f) + out[a + 1, X0:X1] * f), 0, 255).astype(np.uint8)


def doze(img, mp, q=Q):
    out = img.copy()
    m = mp.local(out, q["caixa"])
    for r, d in q["piso"]:
        _remenda(out, m, r, [d], None)
    a, f = q["armario"], q["folha"]
    _continua(out, m, (q["sobra"][0], a[1], a[2], q["inteiro_y"]), q["inteiro_y"], q["passo"])
    _continua(out, m, (f[0], f[1], q["sobra"][2], q["inteiro_y"]), q["inteiro_y"], q["passo"])
    # o friso de cima do guarda-roupa, no tom do que ficou
    fx0, fy0, fx1, fy1 = m.reti(q["friso"])
    cor = np.median(out[fy0:fy1, fx0:fx1].reshape(-1, 3), axis=0)
    X0, X1 = int(round(m.x(q["sobra"][0]))), int(round(m.x(a[2])))
    out[fy0:fy1, X0:X1] = cor.astype(np.uint8)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), final(fin))
        print("    DCE: o retângulo de 16/11 fora; o guarda-roupa com cabides e a folha inteiros")
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = doze(img, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

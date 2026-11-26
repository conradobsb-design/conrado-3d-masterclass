"""Casa C Térreo (26/11): o tom da água rasa (a prainha e o banco do spa) e o degradê da escada da prainha.

Usuário: "alterar o tom da prainha e spa onde é mais raso e reequilibrar o degradê da escada que desce para a piscina".

- **O raso** (a prainha e o banco em volta do spa), que estava no verde-água claro, vai ao cinza equilibrado do fundo,
  o mesmo das Casas A e B (`prainha_cinza_casaa_2511.RASO`: o matiz +34°, a saturação a 85%, a luminosidade a 80%;
  a água e o fundo de `piscinas_sobrias_1911`, `FUNDO["C"]`). O pastilhado, os reflexos, as bordas e os rótulos
  ficam.
- **Os 4 degraus** entre a prainha e a parte funda (`piscinas_sobrias_1911.DEGRAUS["C"]`: x 653 a 915, as linhas de
  cima em 1427, 1439, 1451 e 1463 e o fundo em 1475) saem do raso para a regra própria: cada degrau no tom do raso novo
  mais k/5 do caminho até o fundo (k = 1 a 4), em passos iguais, pelo ganho de cor de cada degrau (a mediana do degrau
  levada ao tom novo: o pastilhado e a sombra do espelho de cada degrau ficam). Antes o degradê partia do verde-água e
  os passos eram desiguais (a luminosidade 209, 187, 170, 156, 139 e 130 no fundo).

Final, prancha e 12K A e B (pelo registro local).

  python3 piscina_casac_2611.py
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
import esquadrias_pretas_1911 as EP      # noqa: E402
import vetor_2511 as V                   # noqa: E402
import um_pav_casaa_2511d as DD          # noqa: E402
import piscinas_sobrias_1911 as PS       # noqa: E402
import prainha_cinza_casaa_2511 as P     # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
CAIXA = (615.0, 1285.0, 1125.0, 1665.0)
X0D, X1D, YS = PS.DEGRAUS["C"]
REF = dict(raso=(675.0, 1318.0, 905.0, 1420.0), fundo=(670.0, 1495.0, 1080.0, 1625.0))


def piscina(img, s, origem):
    jan = V.janela(img, CAIXA, s, origem, folga=0)
    X0, Y0, X1, Y1 = jan
    sub = img[Y0:Y1, X0:X1].copy()
    xs, ys = V.coords(jan, s, origem)
    # os retângulos do fundo em px do recorte
    rets = []
    for x0, y0, x1, y1, lados in PS.FUNDO["C"]:
        rets.append(((x0 - origem[0]) * s - X0, (y0 - origem[1]) * s - Y0,
                     (x1 - origem[0]) * s - X0, (y1 - origem[1]) * s - Y0, lados))
    rets = [tuple(int(round(v)) for v in r[:4]) + (r[4],) for r in rets]
    agua = PS.agua(sub, s).astype(bool)
    wr, _ = P.peso_raso(sub, rets, s)
    # os degraus saem do raso (têm a regra própria)
    deg_x = (xs >= X0D - 1.0) & (xs <= X1D + 1.0)
    deg_y = (ys >= YS[0] - 0.5) & (ys < YS[-1] + 0.5)
    deg = deg_y[:, None] & deg_x[None, :]
    wr = wr * (1 - deg)
    novo = PS.aplicar(sub, wr, P.RASO).astype(np.float32)

    def _med(r, base):
        m = ((xs >= r[0]) & (xs <= r[2]))[None, :] & ((ys >= r[1]) & (ys <= r[3]))[:, None] & agua
        L = base.mean(2)
        m &= (L > np.percentile(L[m], 8)) & (L < np.percentile(L[m], 85))     # sem os reflexos e as letras
        return np.median(base[m], axis=0)

    R = _med(REF["raso"], novo)
    F = _med(REF["fundo"], novo)
    n = len(YS) - 1
    for k in range(n):
        y0, y1 = YS[k], YS[k + 1]
        faixa = ((ys >= y0 - 0.5) & (ys < y1 - 0.5))[:, None] & deg_x[None, :] & agua
        miolo = ((ys >= y0 + 2.0) & (ys < y1 - 1.0))[:, None] & ((xs >= X0D + 12) & (xs <= X1D - 12))[None, :] & agua
        M = np.median(novo[miolo], axis=0)
        T = R + (F - R) * (k + 1) / (n + 1)
        g = (T / np.maximum(M, 1.0)).astype(np.float32)
        novo[faixa] = novo[faixa] * g[None, :]
    img[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    return img


FUNC = {"piscina": piscina}
ITENS = {"piscina": CAIXA}


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

"""Casa B Térreo, 7ª leva de 26/11: o piso em volta da poltrona redonda da varanda sem as falhas.

Usuário: "corrija as falhas do piso em volta da poltrona". Em `terreo_casab_2611f.poltrona_redonda` a poltrona velha e a
sombra dela saíram por um disco de travertino novo (36 px em volta de 1144,5 x 939, até antes do tapete); os veios e a
luz do disco não casavam com o piso em volta: aparecia o círculo (mais claro na final, com a emenda em arco no 12K).
Agora o disco inteiro (e 1,5 px de folga) é refeito linha a linha com o próprio piso de fora dele, que é o de antes: os
veios do travertino são horizontais, então cada linha recebe a mesma linha do piso logo à esquerda (de 1078 em
diante, antes da borda da piscina), espelhada a partir da beira do disco, e, perto da beira direita, a linha do piso
logo à direita (até 1184, antes do tapete), espelhada, com a passagem esfumada de uma para a outra; sem emenda nas
beiras e com a mesma luz. A poltrona da biblioteca e a sombra curta dela voltam por cima, iguais.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casab_2611g.py
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
import vetor_2511 as V               # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import terreo_casab_2611b as B       # noqa: E402
import terreo_casab_2611f as F       # noqa: E402

PLANTA = "B_Terreo"
DZ = B.DZ
PISO = dict(folga=1.5, esq=1078.0, dir=1184.0)


def _espelho(n, k):
    """Os índices 0..n-1 espelhados, de vai e volta, para k passos."""
    i = np.arange(k) % (2 * n)
    return np.where(i < n, i, 2 * n - 1 - i)


def piso_poltrona(img, s, origem, q=PISO, P=F.POLTRONA):
    cx, cy = P["centro"]
    zx, zy = cx + P["desvio"][0], cy + P["desvio"][1]
    R = P["raio"] + q["folga"]
    zona = [(min(zx + R * np.cos(a), P["xmax"] + q["folga"]), zy + R * np.sin(a))
            for a in np.linspace(0, 2 * np.pi, 96, endpoint=False)]
    jan = V.janela(img, (q["esq"] - 2, zy - R - 4, q["dir"] + 2, zy + R + 4), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    Z = V.cob([zona], jan, s, origem) > 0.01
    novo = reg.copy()
    cols = np.arange(W)
    for r in np.where(Z.any(axis=1))[0]:
        c = np.where(Z[r])[0]
        c0, c1 = c.min(), c.max()
        n = c1 - c0 + 1
        nl = int(np.sum((xs >= q["esq"]) & (cols < c0)))
        nr = int(np.sum((xs < q["dir"]) & (cols > c1)))
        if nl < 2:
            continue
        esq = reg[r, c0 - 1 - _espelho(nl, n)]                       # a linha de fora à esquerda, espelhada
        if nr >= 2:
            dire = reg[r, (c1 + 1 + _espelho(nr, n))[::-1]]           # e a de fora à direita, espelhada
            t = np.clip((np.arange(n) - (n - 1 - 3 * nr)) / max(3 * nr, 1), 0, 1)
            t = t * t * (3 - 2 * t)
        else:
            dire, t = esq, np.zeros(n)
        novo[r, c0:c1 + 1] = esq * (1 - t)[:, None] + dire * t[:, None]
    # a beira do disco esfumada (0,6 px) para dentro
    a = np.clip(cv2.GaussianBlur(Z.astype(np.float32), (0, 0), 0.6 * s), 0, 1) * Z
    reg = reg * (1 - a[..., None]) + novo * a[..., None]
    # a poltrona e a sombra curta dela por cima, como em 2611f
    al, cor = F._poltrona_camada(jan, s, origem, P)
    Ms = np.float32([[1, 0, -1.2 * s], [0, 1, 1.4 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(al, Ms, (W, H)), (0, 0), 1.5 * s) * (1 - al)
    reg = reg * (1 - P["sombra"] * sb)[..., None]
    reg = reg * (1 - al[..., None]) + cor * al[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"piso_poltrona": piso_poltrona}
ITENS = {"piso_poltrona": (1095.0, 895.0, 1195.0, 985.0)}             # o mesmo registro da poltrona (2611f)


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

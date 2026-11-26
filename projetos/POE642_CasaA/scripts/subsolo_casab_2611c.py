"""Casa B Subsolo, 3ª leva de 26/11 (o recorte do 12K B: "corrija o piso e seus contornos").

- **BH serviço e o box dele**: o piso manchado, com as faixas claras junto às paredes e ao vidro, sai; o travertino novo
  (`terreo_casaa_2511d.refazer_piso`, a textura e o px/m das outras plantas, no 12K a escala desta) de face a face das
  paredes do PDF: o banho de 1368,2 a 1439,8 (até o vidro do box, 1440,1, abaixo de 391,3) e de 328,6 a 439,1; o box de
  1443,1 a 1511,5 e de 391,3 a 439,1. Ficam a bancada com a cuba, a bacia, a folha da porta, a folha de vidro do box e o
  chuveiro (com a sombra curta deles no piso novo; a ponta da cuba que passa da bancada também) e o rótulo por cima (as
  letras pela forma, recompostas no piso novo; a janela do rótulo só nas letras, fora a bancada de granito).
- **Academia, as pontas do vidro** ("corrija essa extremidade"): o tampão claro da esquadria de antes, entre a parede e
  o vidro, em cima e embaixo, vira parede (no PDF a parede vai até o vidro: 446,3 e 597,3); o fio escuro de antes, rente
  à soleira do lado da academia, coberto pela madeira de logo ao lado.

Final, prancha e 12K A e B.

  python3 subsolo_casab_2611c.py
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
import terreo_casaa_2511d as D       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import subsolo_casab_2611 as B1      # noqa: E402

PLANTA = "B_Subsolo"
DZ = B1.DZ

PISO = dict(zona=[(1368.2, 328.6, 1439.8, 439.1), (1439.6, 391.3, 1440.4, 439.1), (1443.1, 391.3, 1511.5, 439.1)],
            objetos=[(1367.8, 328.4, 1393.2, 392.2),      # a bancada com a cuba
                     (1403.6, 335.8, 1439.8, 339.0),      # a folha da porta
                     (1439.7, 391.0, 1443.5, 438.8)],     # a folha de vidro do box
            # a bacia e o chuveiro pela forma (o que não é o bege do piso), devolvidos por cima do piso novo
            pecas=[(1367.8, 400.0, 1404.0, 432.0), (1480.5, 407.0, 1511.5, 422.0),
                   (1390.0, 345.0, 1397.5, 373.0)],      # a ponta da cuba que passa da bancada, com a sombra
            croma=20.0, sombra=0.13,
            rotulo=(1400.0, 376.0, 1438.0, 408.0),        # só as letras (fora a bancada de granito, mais escura)
            luz=[(1396.0, 342.0, 1436.0, 398.0), (1405.0, 432.0, 1436.0, 438.0), (1446.0, 394.0, 1478.0, 437.0)])


def piso_bh_servico(img, s, origem, q=PISO):
    # as peças (a bacia, o chuveiro, a ponta da cuba): os px fora do bege do piso (o branco da louça, o cinza do metal e o contorno)
    jan = V.janela(img, (1362.0, 340.0, 1516.0, 436.0), s, origem, folga=int(2 * s) + 2)
    X0, Y0, X1, Y1 = jan
    antes = img[Y0:Y1, X0:X1].astype(np.float32).copy()
    caixa = V.cob([V.ret(*r) for r in q["pecas"]], jan, s, origem) > 0.5
    croma = antes[..., 2] - antes[..., 0]                    # R - B: o piso bege é quente
    m = (caixa & (croma < q["croma"])).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= max(4, int(2 * s * s))]).astype(np.float32)
    a = cv2.GaussianBlur(m, (0, 0), max(0.35 * s, 0.35))
    a = np.maximum(a, m)
    # o rótulo: as letras (mais escuras que o piso) pela forma, recompostas por cima do piso novo
    jr = V.janela(img, q["rotulo"], s, origem, folga=2)
    R0, S0, R1, S1 = jr
    rot = img[S0:S1, R0:R1].astype(np.float32).copy()
    Lr = rot.mean(2)
    Lf = float(np.median(Lr))
    Lt = float(np.percentile(Lr, 1.0))
    ar = np.clip((Lf - 12.0 - Lr) / max(Lf - 12.0 - Lt, 1.0), 0, 1)
    cor_txt = np.median(rot[ar > 0.85], axis=0) if (ar > 0.85).any() else np.float32([40, 40, 40])
    img = D.refazer_piso(img, s, origem, [V.ret(*r) for r in q["zona"]], objetos=[V.ret(*r) for r in q["objetos"]],
                         sombra=0.10, letras=False, ref_luz=[V.ret(*r) for r in q["luz"]], pena=0.3)
    nr = img[S0:S1, R0:R1].astype(np.float32)
    img[S0:S1, R0:R1] = np.clip(np.round(nr * (1 - ar[..., None]) + cor_txt * ar[..., None]), 0, 255).astype(np.uint8)
    novo = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = m.shape
    sb = cv2.GaussianBlur(m, (0, 0), max(0.7 * s, 0.6))
    Ms = np.float32([[1, 0, 0.6 * s], [0, 1, 0.8 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - a)
    novo *= (1 - q["sombra"] * sb)[..., None]
    novo = novo * (1 - a[..., None]) + antes * a[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    return img


# as pontas do vidro da academia ("corrija essa extremidade"): o tampão claro da esquadria de antes, entre a parede e
# o vidro, em cima e embaixo, vira parede (no PDF a parede vai até 446,3 e começa em 597,3); o fio escuro da esquadria
# de antes, rente à soleira do lado da academia, coberto pela madeira de logo ao lado
ACADEMIA_PONTAS = dict(parede=[(1358.2, 441.0, 1369.8, 446.4), (1358.4, 597.2, 1368.3, 604.6)],
                       fio=(1368.0, 446.4, 1369.8, 603.4))


def academia_pontas(img, s, origem, q=ACADEMIA_PONTAS):
    img = B1.madeira_ao_lado(img, s, origem, q["fio"])
    return B1.pintar(img, s, origem, q["parede"])


ITENS = {"piso_bh_servico": (1362.0, 322.0, 1516.0, 446.0), "academia_pontas": (1352.0, 436.0, 1378.0, 610.0)}
FUNC = {"piso_bh_servico": piso_bh_servico, "academia_pontas": academia_pontas}


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

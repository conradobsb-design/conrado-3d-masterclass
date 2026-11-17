"""A mesa do escritório do Térreo da Casa E com as cadeiras nos lados certos (17/11, usuário: "Aqui no escritório você vai
trocar e deixar uma cadeira de escritório do outro lado da mesa e do outro lado você vai deixar as outras duas
poltroninhas brancas. É o contrário, aqui você inverteu. Onde tem uma é a do escritório, onde tem duas é a poltrona
que você colocou do lado errado."), na final e direto nos 12K A e B.

O retângulo da mesa e das cadeiras volta ao travertino limpo (o da circulação acima do jantar, num tom só); no lado de
cima (onde ia uma), a cadeira de escritório de couro, virada para a mesa e 1/3 sob o tampo; no lado de baixo (onde iam
duas), as duas poltroninhas de madeira e linho claro, viradas para a mesa e 1/3 sob o tampo; a mesa da E por cima, no
mesmo lugar, com a sombra curta.

  python3 escritorio_mesa_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 escritorio_mesa_casae_1711.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import biblioteca_terreo_casaa_1211 as BT                   # noqa: E402
import danae_foto as DF                                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
BIB = RAIZ / "POE642_CasaE/biblioteca-objetos/02-terreo"

# px da final (a mesa e os lados dela: `mobiliario_terreo_casae_1611.ESCRITORIO_E`)
CAIXA = (2300, 940, 2470, 1095)
PISO = {"ret": (2326.0, 962.0, 2452.0, 1078.0), "fonte": (1741.0, 834.0), "suave": 3.0}
MESA = {"png": BIB / "escritorio/mesa-escritorio-e.png", "ret": (2338.0, 996.0, 2439.0, 1038.0)}
ESCRITORIO = {"png": BIB / "escritorio/cadeira-escritorio.png", "larg": 34.0, "lugares": ((2385.5, 996.0),)}
VISITA = {"png": BIB / "sala-de-jantar/cadeira-jantar-madeira-e.png", "larg": 30.0,
          "lugares": ((2364.0, 1038.0), (2414.0, 1038.0))}


def _png(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def piso(out, m, q=PISO):
    s = m.s
    rm = m.ret(q["ret"])
    X0, Y0 = int(np.floor(rm[0])), int(np.floor(rm[1]))
    X1, Y1 = int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    forma = (Y1 - Y0, X1 - X0)
    yy = np.arange(forma[0], dtype=np.float32)[:, None]
    xx = np.arange(forma[1], dtype=np.float32)[None, :]
    k = q["suave"] * s
    a = (np.clip((yy + 0.5 - (rm[1] - Y0)) / k, 0, 1) * np.clip(((rm[3] - Y0) - yy - 0.5) / k, 0, 1)
         * np.clip((xx + 0.5 - (rm[0] - X0)) / k, 0, 1) * np.clip(((rm[2] - X0) - xx - 0.5) / k, 0, 1))
    a = a * alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    dx = int(round(m.x(q["fonte"][0]) - rm[0]))
    dy = int(round(m.y(q["fonte"][1]) - rm[1]))
    novo = out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)


def pecas(out, m):
    s = m.s
    o = out.astype(np.float32)
    px_m = DF.PX_M * s

    def cx_(x):
        return m.x(x) - 0.5

    def cy_(y):
        return m.y(y) - 0.5
    # a de escritório no lado de cima, virada para baixo (para a mesa), 1/3 sob o tampo
    Pc = _png(ESCRITORIO["png"])
    lc = ESCRITORIO["larg"]
    ac = lc * Pc.shape[0] / Pc.shape[1]
    for cx, yt in ESCRITORIO["lugares"]:
        BT.pousar(o, Pc, cx_(cx), cy_(yt - ac / 2 + ac / 3), lc * s, ac * s, BT.girar_pt(0.0, 1.0),
                  BT.SOMBRAS["movel"], px_m)
    # as duas poltroninhas claras no lado de baixo, viradas para cima (para a mesa), 1/3 sob o tampo
    Pv = _png(VISITA["png"])
    lv = VISITA["larg"]
    av = lv * Pv.shape[0] / Pv.shape[1]
    for cx, yb in VISITA["lugares"]:
        BT.pousar(o, Pv, cx_(cx), cy_(yb + av / 2 - av / 3), lv * s, av * s, BT.girar_pt(0.0, -1.0),
                  BT.SOMBRAS["movel"], px_m)
    x0, y0, x1, y1 = MESA["ret"]
    BT.pousar(o, _png(MESA["png"]), cx_((x0 + x1) / 2), cy_((y0 + y1) / 2), (x1 - x0) * s, (y1 - y0) * s, 0.0,
              BT.SOMBRAS["mesa"], px_m)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)


def aplicar(img, mp):
    out = img.copy()
    m = mp.local(out, CAIXA) if mp.ref is not None else mp
    piso(out, m)
    pecas(out, m)
    print("    escritório: a cadeira de escritório no lado de uma, as duas poltroninhas claras no lado de duas, a mesa "
          "por cima, o piso em volta limpo")
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

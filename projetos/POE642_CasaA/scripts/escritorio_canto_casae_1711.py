"""O canto de baixo do escritório do Térreo da Casa E (17/11, usuário: "Aqui a gente vai trocar o vaso com as plantas.
E eu quero que corrija já o entorno do piso. E também quero que troque essa mesa redonda pelo Tom Nogueira."), na
final e direto nos 12K A e B.

- `piso`: o canto inteiro (da parede da esquerda à cortina, do rótulo à parede de baixo) volta ao travertino limpo, o
  de logo abaixo do jardim do living (o mesmo tom só, com os veios deitados), com a sombra curta rente às paredes:
  saem os remendos claros em volta da mesinha, a mancha cinza em volta da poltrona e a barra branca e a faixa cinza
  junto à cortina;
- `cortina`: a cortina por trás do vaso de antes, refeita pela de cima (4 ondas acima: o mesmo desenho);
- `pecas`: a poltrona arredondada da E de volta, no lugar e no giro de antes, com a sombra curta; a mesinha redonda no
  círculo do PDF em nogueira (o tampo da mesa lateral de metal e madeira do living, em círculo, com o aro de metal
  escuro); o vaso com folhagem da biblioteca (o do hall de entrada) no círculo do PDF, no lugar do vaso de antes.

  python3 escritorio_canto_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 escritorio_canto_casae_1711.py final
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

# px da final
CAIXA = (2285, 1080, 2485, 1195)
PISO = {"ret": (2296.4, 1109.0, 2458.0, 1186.6), "fonte": (1900.0, 1130.0), "topo_suave": 3.0,
        "paredes": {"esquerda": 2296.4, "baixo": 1186.6}, "sombra_parede": (0.10, 2.0)}
CORTINA = {"ret": (2458.0, 1104.0, 2472.0, 1186.6), "onda": 18.0, "ondas": 4}
POLTRONA = {"png": BIB / "escritorio/poltrona-intima-e.png", "centro": (2398.0, 1146.0), "larg": 50.0,
            "frente": (-1.0, -1.0)}
MESINHA = {"png": BIB / "living/mesa-lateral-metal-madeira.png", "ret": (2301.7, 1138.5, 2331.6, 1168.4),
           "miolo": 0.10, "aro": 0.035}
VASO = {"png": BIB / "hall-de-entrada/vaso-folhagem-a.png", "ret": (2435.3, 1156.4, 2464.2, 1185.3)}


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
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    # o topo (junto ao rótulo) entra aos poucos; o resto vai até as paredes e a cortina
    yy = np.arange(forma[0], dtype=np.float32)[:, None]
    a = a * np.clip((yy + 0.5 - (rm[1] - Y0)) / (q["topo_suave"] * s), 0, 1)
    fx, fy = q["fonte"]
    dx = int(round(m.x(fx) - rm[0]))
    dy = int(round(m.y(fy) - rm[1]))
    novo = out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    # a sombra curta rente às paredes (a da esquerda e a de baixo)
    xx = np.arange(forma[1], dtype=np.float32)[None, :]
    de = (xx + 0.5) - (m.x(q["paredes"]["esquerda"]) - X0)
    db = (m.y(q["paredes"]["baixo"]) - Y0) - (yy + 0.5)
    f, d0 = q["sombra_parede"]
    sb = f * (np.exp(-np.maximum(de, 0) / (d0 * s)) + np.exp(-np.maximum(db, 0) / (d0 * s)))
    novo *= (1 - np.clip(sb, 0, 0.3))[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)


def cortina(out, m, q=CORTINA):
    s = m.s
    X0, Y0, X1, Y1 = m.reti(q["ret"])
    base = q["onda"] * q["ondas"] * s
    # o deslocamento de 4 ondas exato no próprio desenho: o que melhor casa a faixa de logo acima do trecho
    ref = out[Y0 - int(30 * s):Y0, X0:X1].astype(np.float32)
    melhor, dym = None, int(round(base))
    for dy in range(int(round(base - 3 * s)), int(round(base + 3 * s)) + 1):
        src = out[Y0 - int(30 * s) - dy:Y0 - dy, X0:X1].astype(np.float32)
        e = float(((ref - src) ** 2).mean())
        if melhor is None or e < melhor:
            melhor, dym = e, dy
    novo = out[Y0 - dym:Y1 - dym, X0:X1].copy()
    h = Y1 - Y0
    w = np.clip((np.arange(h, dtype=np.float32) + 0.5) / (3 * s), 0, 1)[:, None, None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(out[Y0:Y1, X0:X1] * (1 - w) + novo * w), 0, 255).astype(np.uint8)
    return dym


def _mesinha_nogueira(q=MESINHA, lado=600):
    P = _png(q["png"])
    h, w = P.shape[:2]
    k = q["miolo"]
    tampo = P[int(h * k):int(h * (1 - k)), int(w * k):int(w * (1 - k)), :3]
    tampo = cv2.resize(tampo, (lado, lado), interpolation=cv2.INTER_AREA)
    # o aro: o metal escuro da borda da mesa lateral
    borda = P[:max(2, int(h * 0.02)), :, :3].reshape(-1, 3)
    aro = np.median(borda[P[:max(2, int(h * 0.02)), :, 3].reshape(-1) > 200], axis=0) \
        if (P[:max(2, int(h * 0.02)), :, 3] > 200).any() else np.float32([40, 40, 42])
    yy, xx = np.mgrid[0:lado, 0:lado].astype(np.float32)
    r = np.hypot(xx + 0.5 - lado / 2, yy + 0.5 - lado / 2)
    R = lado / 2 - 1
    alfa = np.clip(R - r + 0.5, 0, 1)
    em_aro = np.clip(r - (R - q["aro"] * lado) + 0.5, 0, 1)[..., None]
    cor = tampo * (1 - em_aro) + aro[None, None] * em_aro
    return np.dstack([cor, alfa * 255]).astype(np.float32)


def pecas(out, m):
    s = m.s
    o = out.astype(np.float32)
    px_m = DF.PX_M * s

    def cx_(x):
        return m.x(x) - 0.5

    def cy_(y):
        return m.y(y) - 0.5
    Pp = _png(POLTRONA["png"])
    lp = POLTRONA["larg"]
    BT.pousar(o, Pp, cx_(POLTRONA["centro"][0]), cy_(POLTRONA["centro"][1]), lp * s, lp * Pp.shape[0] / Pp.shape[1] * s,
              BT.girar_pt(*POLTRONA["frente"]), BT.SOMBRAS["movel"], px_m)
    x0, y0, x1, y1 = MESINHA["ret"]
    BT.pousar(o, _mesinha_nogueira(), cx_((x0 + x1) / 2), cy_((y0 + y1) / 2), (x1 - x0) * s, (y1 - y0) * s, 0.0,
              BT.SOMBRAS["mesa"], px_m)
    x0, y0, x1, y1 = VASO["ret"]
    Pv = _png(VASO["png"])
    BT.pousar(o, Pv, cx_((x0 + x1) / 2), cy_((y0 + y1) / 2), (x1 - x0) * s, (y1 - y0) * s, 0.0,
              BT.SOMBRAS["movel"], px_m)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)


def aplicar(img, mp):
    out = img.copy()
    m = mp.local(out, CAIXA) if mp.ref is not None else mp
    piso(out, m)
    dy = cortina(out, m)
    pecas(out, m)
    print(f"    escritório: o canto no travertino limpo, a cortina por trás do vaso refeita ({dy} px acima), a poltrona "
          "de volta, a mesinha redonda em nogueira e o vaso com folhagem da biblioteca")
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

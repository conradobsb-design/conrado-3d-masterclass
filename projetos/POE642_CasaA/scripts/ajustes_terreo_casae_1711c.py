"""Térreo da Casa E, 17/11, ajustes do usuário (2ª leva), na final e direto nos 12K A e B:

1. `parede` ("CORRIJA ESSA PAREDE", a da direita da área de serviço descoberta): a parede refeita lisa no cinza das
   paredes, na união das peças do PDF (ARQ_PAREDE) da quina de cima até a de baixo: saem os fios escuros entre as
   peças (o vertical dentro da parede e o horizontal na quina) e a face fica reta; o risco branco no piso junto à quina
   de dentro sai (o piso de logo abaixo);
2. `porta` ("CORRIJA A FALHA NA PORTA", a pivotante do hall): onde o tracejado do hall cruza a folha, a folha estava
   cortada; a folha volta inteira (a dela de logo ao lado) e o tracejado passa por baixo;
3. `vaso_hall` ("CORRIJA A FALHA EM VOLTA DO VASO"): o círculo claro do remendo em volta do vaso do hall e o
   pontinho cinza saem: o entorno volta ao travertino limpo (o de logo abaixo do jardim do living) e o vaso com
   folhagem volta no mesmo lugar, com a sombra curta;
4. `chuveiro` ("FALTOU O CANO DO CHUVEIRO DE PAREDE", o box do BH gourmet): o braço cromado do PDF (ARQ_LOUÇAS E
   METAIS), da cabeça quadrada até a parede de baixo, com a canopla na parede e a sombra curta;
5. `gas` ("AQUI NÃO TEM SOLEIRA", o abrigo de GÁS): a faixa clara da soleira na abertura sai; o piso de dentro do
   abrigo vai até a face de fora (a faixa limpa dele, abaixo do rótulo, espelhada).

  python3 ajustes_terreo_casae_1711c.py doze [--opcao AB] [--passos ...]   (antes da final: a final de antes é a ref.)
  python3 ajustes_terreo_casae_1711c.py final [--passos ...]
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
import instalacao_terreo_casad_1711 as ID                   # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
BIB = RAIZ / "POE642_CasaE/biblioteca-objetos/02-terreo"

# px da final
PAREDE = {"caixa": (2190, 410, 2250, 650), "busca": (2205, 420, 2245, 640), "cor": (80, 80, 80),
          "risco": (2208.5, 435.3, 2216.6, 438.8), "risco_d": [(0, 5), (0, 7)]}
PORTA = {"caixa": (2340, 1340, 2540, 1395), "ret": (2414.0, 1367.4, 2442.0, 1374.2), "d": (30, 0)}
VASO_HALL = {"caixa": (2300, 1490, 2420, 1590), "ret": (2316.0, 1503.0, 2402.0, 1573.5), "fonte": (1900.0, 1132.0),
             "suave": 4.0, "pilar": (2290.0, 1548.6, 2326.1, 1600.0),
             "png": BIB / "hall-de-entrada/vaso-folhagem-a.png", "centro": (2359.5, 1544.5),
             "diam": 50.0, "sombra": [{"dx": -0.02, "dy": 0.02, "sig": 0.04, "forca": 0.24},
                                      {"dx": 0.0, "dy": 0.0, "sig": 0.02, "forca": 0.14}]}
CHUVEIRO = {"caixa": (1215, 535, 1300, 600), "braco": (1258.7, 571.0, 1260.2, 586.7),
            "canopla": (1257.7, 585.9, 1261.3, 587.4), "cromo": (206, 208, 211), "cromo_brilho": (238, 239, 241),
            "cromo_borda": (118, 121, 126), "sombra": 0.22}
GAS = {"caixa": (1940, 405, 2030, 475), "ret": (1960.5, 423.0, 2006.2, 437.0),
       "fontes": [(1956.0, 450.0, 2012.0, 456.0)]}


def _png(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def _pecas_parede(q=PAREDE):
    import final3840_casae as FE
    Q = FE.QuadroE("Terreo")
    X0, Y0, X1, Y1 = q["busca"]
    rs = []
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or d["type"] != "f" or not d.get("fill") or min(d["fill"]) > 0.5:
            continue
        r = d["rect"]
        a, b = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        x0, y0, x1, y1 = min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])
        if x1 >= X0 and x0 <= X1 and y1 >= Y0 and y0 <= Y1:
            rs.append((max(x0, X0), max(y0, Y0), min(x1, X1), min(y1, Y1)))
    return rs


def parede(out, m, q=PAREDE):
    rs = _pecas_parede(q)
    X0, Y0, X1, Y1 = m.reti(q["busca"])
    X0, Y0, X1, Y1 = X0 - 2, Y0 - 2, X1 + 2, Y1 + 2
    forma = (Y1 - Y0, X1 - X0)
    a = np.zeros(forma, np.float32)
    for r in rs:
        rm = m.ret(r)
        a += alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    a = np.clip(a, 0, 1)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + np.float32(q["cor"]) * a), 0, 255).astype(np.uint8)
    ID._remenda(out, m, q["risco"], q["risco_d"], None, 0)
    print(f"    área descoberta: a parede da direita lisa ({len(rs)} peças do PDF), sem os fios; o risco branco saiu")


def porta(out, m, q=PORTA):
    ID._remenda(out, m, q["ret"], [q["d"]], None, 0)
    print("    hall: a folha da pivotante inteira onde o tracejado cruzava")


def vaso_hall(out, m, q=VASO_HALL):
    s = m.s
    rm = m.ret(q["ret"])
    X0, Y0 = int(np.floor(rm[0])), int(np.floor(rm[1]))
    X1, Y1 = int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    forma = (Y1 - Y0, X1 - X0)
    yy = np.arange(forma[0], dtype=np.float32)[:, None]
    xx = np.arange(forma[1], dtype=np.float32)[None, :]
    k = q["suave"] * s
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    a = a * (np.clip((yy + 0.5 - (rm[1] - Y0)) / k, 0, 1) * np.clip((xx + 0.5 - (rm[0] - X0)) / k, 0, 1)
             * np.clip(((rm[2] - X0) - xx - 0.5) / k, 0, 1))
    # só o piso claro muda (a parede escura da esquerda e a soleira de baixo ficam)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    # o que fica: o pilar da esquerda (o retângulo dele); a mancha cinza junto a ele entra no piso novo
    pr = m.ret(q["pilar"])
    a = a * (1 - alfa_ret((pr[0] - X0, pr[1] - Y0, pr[2] - X0, pr[3] - Y0), forma))
    dx = int(round(m.x(q["fonte"][0]) - rm[0]))
    dy = int(round(m.y(q["fonte"][1]) - rm[1]))
    novo = out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)
    o = out.astype(np.float32)
    cx, cy = q["centro"]
    d = q["diam"]
    BT.pousar(o, _png(q["png"]), m.x(cx + 0.5) - 0.5, m.y(cy + 0.5) - 0.5, d * s, d * s, 0.0, q["sombra"],
              DF.PX_M * s)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print("    hall: o entorno do vaso no travertino limpo, o vaso de volta")


def chuveiro(out, m, q=CHUVEIRO):
    import correcoes_terreo_casab_1611 as CB
    s = m.s
    x0, y0, x1, y1 = q["braco"]
    e = 0.35
    # a sombra curta do braço, para a direita e para baixo
    rm = m.ret((x0, y0, x1, y1))
    X0, Y0, X1, Y1 = int(rm[0]) - 4, int(rm[1]) - 4, int(np.ceil(rm[2])) + 6, int(np.ceil(rm[3])) + 6
    forma = (Y1 - Y0, X1 - X0)
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    M = np.float32([[1, 0, 0.7 * s], [0, 1, 0.5 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), 0.6 * s) * (1 - a)
    out[Y0:Y1, X0:X1] = np.clip(np.round(out[Y0:Y1, X0:X1].astype(np.float32) * (1 - q["sombra"] * sb)[..., None]),
                                0, 255).astype(np.uint8)
    CB.pintar(out, m, [((x0 - e, y0, x1 + e, y1), "ret", q["cromo_borda"], 0), ((x0, y0, x1, y1), "ret", q["cromo"], 0),
                       ((x0 + 0.15, y0, x0 + 0.6, y1), "ret", q["cromo_brilho"], 0)])
    cx0, cy0, cx1, cy1 = q["canopla"]
    CB.pintar(out, m, [((cx0 - e, cy0 - e, cx1 + e, cy1), "ret", q["cromo_borda"], 0),
                       ((cx0, cy0, cx1, cy1), "ret", q["cromo"], 0)])
    print("    BH gourmet: o braço cromado do chuveiro até a parede de baixo, com a canopla")


def gas(out, m, q=GAS):
    s = m.s
    X0, Y0, X1, Y1 = m.reti(q["ret"])
    h, w = Y1 - Y0, X1 - X0
    tiras = []
    for f in q["fontes"]:
        a0, b0, a1, b1 = m.reti(f)
        tiras.append(out[b0:b1, a0:a1])
    fonte = np.concatenate(tiras, axis=0)
    while fonte.shape[0] < h:
        fonte = np.concatenate([fonte, fonte[::-1]], axis=0)
    fonte = fonte[:h]
    if fonte.shape[1] < w:
        fonte = cv2.copyMakeBorder(fonte, 0, 0, 0, w - fonte.shape[1], cv2.BORDER_REFLECT_101)
    fonte = fonte[:, :w].astype(np.float32)
    rm = m.ret(q["ret"])
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), (h, w))[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + fonte * a), 0, 255).astype(np.uint8)
    print("    abrigo de gás: sem a soleira, o piso de dentro até a face de fora")


PASSOS = {"parede": (parede, PAREDE), "porta": (porta, PORTA), "vaso_hall": (vaso_hall, VASO_HALL),
          "chuveiro": (chuveiro, CHUVEIRO), "gas": (gas, GAS)}


def aplicar(img, mp, passos=tuple(PASSOS)):
    out = img.copy()
    for p in passos:
        f, q = PASSOS[p]
        m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
        f(out, m)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    ap.add_argument("--passos", default=",".join(PASSOS))
    a = ap.parse_args()
    passos = a.passos.split(",")
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa(), passos))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, passos)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

"""Térreo da Casa E, 17/11 ("Vamos trocar esses mobiliários", a varanda): a proposta, antes da instalação. A varanda
limpa (as 2 mesas redondas com as 12 cadeiras, o sofá, as 2 poltronas, a mesa de centro, o banco e a mesa lateral saem; o
Bege Bahia de perto no lugar, `mobiliario_terreo_casae_1611.piso`) e 3 alternativas montadas na própria planta, nas
posições do PDF (`mobiliario_terreo_casae_1611.VARANDA`), com as peças das bibliotecas já aprovadas nas outras casas. As
plantas, os pivotantes e os pilares ficam. Só a proposta: a final não muda.

  python3 proposta_varanda_casae_1711.py [--saida <pasta>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
BIB = {"A": RAIZ / "POE642_CasaA/biblioteca-objetos/02-terreo", "D": RAIZ / "POE642_CasaD/biblioteca-objetos/02-terreo",
       "E": RAIZ / "POE642_CasaE/biblioteca-objetos/02-terreo"}

# px da final (o PDF, como `mobiliario_terreo_casae_1611.VARANDA`; a mesa de centro e o banco medidos na final)
LUGARES = {"centro": (1376, 1363, 1474, 1396), "banco": (1358, 1447, 1493, 1483),
           # a amostra limpa do Bege Bahia (a de `PISOS["bege"]` pega o rótulo da varanda, que foi para lá depois) e o
           # rótulo, que fica
           "bege": (1480, 1150, 1560, 1225), "rotulo": (1266, 1174, 1334, 1212),
           "limpar": [(1300, 1222, 1548, 1322), (1255, 1328, 1336, 1466), (1342, 1350, 1508, 1496),
                      (1524, 1248, 1582, 1300)]}

ALTERNATIVAS = [
    ("1. Como a varanda da Casa D",
     {"sofa": ("D", "varanda-gourmet/sofa-curvo-almofadas-terracota-d", 180), "poltrona": ("D", "living/poltrona-concha-d"),
      "centro": ("D", "varanda-gourmet/mesa-centro-seixo-d"), "lateral": ("D", "varanda-gourmet/mesa-lateral-externa"),
      "banco": ("D", "propostas-1711/banco-B1"),
      "mesa": ("D", "varanda-gourmet/mesa-redonda-gourmet-d"), "cadeira": ("D", "varanda-gourmet/cadeira-gourmet-fibra-d")},
     ["sofá curvo de linho com as almofadas terracota", "2 poltronas concha de linho", "mesa de centro seixo (travertino)",
      "mesa lateral de madeira", "banco B1 (nogueira e couro conhaque)", "mesas redondas de nogueira, cadeiras de fibra"]),
    ("2. Como a varanda da Casa A",
     {"sofa": ("A", "varanda/sofa-curvo-externo", 0), "poltrona": ("A", "varanda/poltrona-externa-a"),
      "centro": ("A", "varanda/mesa-centro-seixo"), "lateral": ("D", "varanda-gourmet/mesa-lateral-externa"),
      "banco": ("D", "propostas-1711/banco-B1"),
      "mesa": ("A", "varanda/mesa-redonda"), "cadeira": ("A", "varanda/cadeira-mesa-redonda")},
     ["sofá curvo de teca com almofadas creme", "2 poltronas de corda e teca", "mesa de centro seixo (travertino)",
      "mesa lateral de madeira", "banco B1 (nogueira e couro conhaque)", "mesas redondas de teca, cadeiras de corda"]),
    ("3. Linho e nogueira, como o living da E",
     {"sofa": ("D", "living/sofa-living-d", 0), "poltrona": ("E", "living/poltrona-creme-madeira-render"),
      "centro": ("E", "living/mesa-centro-gota-e"), "lateral": ("E", "living/mesa-lateral-metal-madeira"),
      "banco": ("D", "propostas-1711/banco-B1"),
      "mesa": ("E", "varanda/mesa-redonda-varanda-e"), "cadeira": ("E", "varanda/cadeira-gourmet-creme-madeira")},
     ["sofá reto de linho", "2 poltronas creme com aro de madeira (as do living)", "mesa de centro gota em nogueira",
      "mesa lateral de metal e madeira", "banco B1 (nogueira e couro conhaque)",
      "mesas redondas de nogueira, cadeiras creme e madeira"]),
]


def ler(casa, rel):
    p = BIB[casa] / f"{rel}.png"
    if not p.exists():
        p = RAIZ / f"POE642_Casa{casa}/biblioteca-objetos/02-terreo/{rel}.png"
    P = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if P.shape[2] == 3:                                   # fundo branco: o alfa pela distância ao branco
        d = (255 - P.astype(np.int16)).max(-1)
        a = np.clip((d - 18) / 22.0, 0, 1) * 255
        P = np.dstack([P, a.astype(np.uint8)])
    P = P.astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 8)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def limpar(Q, img, par):
    import mobiliario_terreo_casae_1611 as M
    H, W = img.shape[:2]
    q = M.VARANDA
    M.PISOS["bege"] = LUGARES["bege"]
    buraco = np.zeros((H, W), bool)
    for mesa, cads in q["mesas"]:
        buraco |= M.ret(mesa, 6)((H, W))
        for c in cads:
            buraco |= M.ret(c, 6)((H, W))
        x0, y0, x1, y1 = mesa
        buraco |= M.objeto_imagem(img, (x0 - 44, y0 - 44, x1 + 44, y1 + 44), "bege", limiar=24, folga=3)
    for cx in LUGARES["limpar"]:
        buraco |= M.objeto_imagem(img, cx, "bege", limiar=24, folga=3)
    vidro = M.ret((1577, 1240, 1600, 1580))((H, W))
    plantas = M.ret((1510, 1436, 1590, 1566))((H, W))
    rotulo = M.ret(LUGARES["rotulo"])((H, W))
    fica = vidro | plantas | rotulo
    return M.piso(img, buraco & ~fica, "bege", par, nao_luz=fica)


def montar(out, par, pecas):
    import mobiliario_terreo_casae_1611 as M
    import mobiliario_terreo_casac_1311 as MB
    q = M.VARANDA
    Pc, Pm = ler(*pecas["cadeira"]), ler(*pecas["mesa"])
    for mesa, cads in q["mesas"]:
        mx, my, mw, mh = M.centro(mesa)
        for c in cads:
            cx, cy, w, h = M.centro(c)
            lado = 0.95 * min(w, h)
            out = M.pousar(out, Pc, cx, cy, lado, lado * Pc.shape[0] / Pc.shape[1], MB.frente((mx - cx, my - cy)),
                           "movel", par)
        out = M.pousar(out, Pm, mx, my, (mw + mh) / 2, (mw + mh) / 2, 0.0, "mesa", par)
    casa, rel, giro = pecas["sofa"]
    Ps = ler(casa, rel)
    sx, sy, sw, sh = M.centro(q["sofa"])
    ht = sw * Ps.shape[0] / Ps.shape[1]
    out = M.pousar(out, Ps, sx, q["sofa"][1] + ht / 2, sw, ht, giro, "movel", par)
    Pp = ler(*pecas["poltrona"])
    for c in q["poltronas"]:
        cx, cy, w, h = M.centro(c)
        lado = 1.05 * min(w, h)
        out = M.pousar(out, Pp, cx, cy, lado * Pp.shape[1] / Pp.shape[0], lado, MB.frente((1, 0)), "movel", par)
    # a mesa de centro no meio do vão entre o sofá e o banco, cabendo em 0,98 x 0,62 do vão (as orgânicas são quase
    # redondas; a do PDF era uma faixa estreita)
    Pt = ler(*pecas["centro"])
    x0, y0, x1, y1 = LUGARES["centro"]
    topo, base = q["sofa"][1] + ht, LUGARES["banco"][1]
    k = min((x1 - x0) / Pt.shape[1], 0.62 * (base - topo) / Pt.shape[0])
    out = M.pousar(out, Pt, (x0 + x1) / 2, (topo + base) / 2, Pt.shape[1] * k, Pt.shape[0] * k, 0.0, "mesa", par)
    Pb = ler(*pecas["banco"])
    x0, y0, x1, y1 = LUGARES["banco"]
    out = M.pousar(out, Pb, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, "movel", par)
    lx, ly, ll = q["mesa_lateral"]
    out = M.pousar(out, ler(*pecas["lateral"]), lx, ly, ll, ll, 0.0, "mesa", par)
    return out


def main():
    import final3840_casae as FE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", default=str(RAIZ / "POE642_CasaE/renders"))
    a = ap.parse_args()
    Q = FE.QuadroE("Terreo")
    par = FE.paredes_pdf(Q) > 0.5
    img = cv2.imread(str(FINAL))
    limpa = limpar(Q, img, par)
    saida = Path(a.saida)
    cv2.imwrite(str(saida / "varanda_limpa.png"), limpa[820:1600, 1180:1620])
    for i, (nome, pecas, _) in enumerate(ALTERNATIVAS, 1):
        out = montar(limpa.copy(), par, pecas)
        cv2.imwrite(str(saida / f"varanda_alt{i}.png"), out[820:1600, 1180:1620])
        print(f"    {nome}")


if __name__ == "__main__":
    main()

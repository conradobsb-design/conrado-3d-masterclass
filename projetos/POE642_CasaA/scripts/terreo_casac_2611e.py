"""Casa C Térreo, 5ª leva de 26/11: o JARDIM 1, a porta de correr da sala TV, as janelas da fachada de baixo e as portas
de correr da adega e do escritório.

Pedidos do usuário (recortes do 12K B):

- JARDIM 1 ("melhorar o contorno, janela à direita e o filete que separa do piso na parte de baixo"):
  - o contorno: as beiras da grama (a de cima com o fio escuro e os pontinhos verde-claros, a da esquerda com as manchas
    claras, a da direita e a de baixo) refeitas com a própria grama de 7 px para dentro, retas nas paredes do PDF; a
    sombra curta das paredes de cima e da direita na grama;
  - a janela da direita (o vão do PDF, 1231,4 a 1240,4 x 835,6 a 913,2) como as janelas do box do Subsolo: a soleira no
    travertino escuro, o vidro no meio da espessura, o contorno preto fino e o montante;
  - o filete de baixo: uma faixa de 3 px (5 cm) no travertino escuro das soleiras entre a grama e o piso, na linha do PDF
    (978,9), de parede a parede.
- Porta de correr entre a sala TV e a circulação ("aqui é apenas uma folha, já representada com contorno em preto. o
  resto sai"): ficam as 2 folhas com o contorno preto; saem os batentes (as barras brancas com o fio preto nas pontas, os
  frisos claros dentro das paredes) e as manchas cinza junto às folhas (no topo, na junta e embaixo): o travertino de
  novo e as paredes no cinza delas.
- "melhorar o aspecto das soleiras" (as 3 janelas da fachada de baixo, junto à grama): cada vão do PDF (de face a face da
  parede, 20 cm) no travertino escuro das soleiras, o vidro no meio, o contorno preto fino e o montante (como a janela do
  box do Subsolo); o fio cinza e os traços escuros do piso logo acima do vão saem.
- "vamos melhorar a representação das portas de correr" (adega e escritório, 4 folhas em 2 trilhos cada): a soleira no
  travertino escuro de parede a parede e as 4 folhas do PDF redesenhadas no padrão das esquadrias (o perfil claro, o
  vidro claro e o contorno fino, `terreo_casaa_2511d.folhas`, as portas de correr da Casa A); as folhas antigas (2 px à
  esquerda) e os frisos claros dentro das paredes das pontas saem.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611e.py [itens]
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
import esquadrias_pretas_1911 as EP              # noqa: E402
import vetor_2511 as V                           # noqa: E402
import terreo_casaa_2511d as D                   # noqa: E402
import terreo_casaa_2511g as G                   # noqa: E402
import um_pav_casaa_2511 as U                    # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402
import terreo_casac_2611 as T0                   # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]
PAREDE = (80.0, 80.0, 80.0)
PERFIL = (34.0, 34.0, 36.0)

JARDIM = dict(beiras=[((1121.0, 835.6, 1127.5, 975.9), (7.0, 0.0), "r"),
                      ((1121.0, 835.6, 1231.4, 841.5), (0.0, 7.0), "b"),
                      ((1225.5, 835.6, 1231.4, 975.9), (-7.0, 0.0), "l"),
                      ((1121.0, 969.5, 1231.4, 975.9), (0.0, -7.0), "t")],
              grama=(1121.0, 835.6, 1231.4, 975.9), sombra=0.28, sombra_px=2.2,
              janela=dict(vao=(1231.4, 835.6, 1240.4, 913.2), vidro=(1236.15, 835.6, 1237.75, 913.2), montante=874.4),
              filete=(1121.0, 975.9, 1231.4, 978.9))
FOLHA_TV = dict(paredes=[(1628.2, 663.0, 1641.4, 670.8), (1628.0, 913.2, 1642.4, 921.5)],
                folhas=[(1633.8, 677.8, 1638.0, 791.0), (1636.7, 793.6, 1641.1, 907.2)],
                zonas=[[((1627.0, 670.8, 1641.6, 678.0), "lrb")],
                       [((1630.0, 787.5, 1637.0, 798.5), "lrtb"), ((1637.0, 789.0, 1643.0, 795.5), "rtb")],
                       [((1627.0, 903.0, 1641.6, 913.2), "lrt")]])
FACHADA = dict(vaos=[(1237.4, 1641.6, 1273.2, 1653.6), (1327.0, 1641.6, 1413.5, 1653.6),
                     (1550.5, 1641.6, 1628.1, 1653.6)],
               vidro=(1647.25, 1648.85), piso=(1637.6, 1641.6), d_piso=(0.0, -4.0))
CORRER = dict(soleira=(2273.4, 929.6, 2282.3, 1189.4),
              # as folhas antigas (desenhadas 2 px à esquerda) e os frisos claros dentro das paredes de cima e de baixo
              limpa=(2268.5, 921.0, 2273.4, 1198.0), paredes=[(2273.4, 921.0, 2280.5, 929.8), (2273.4, 1189.2, 2280.5, 1198.0)],
              folhas=[(2273.4, 933.5, 2276.3, 998.9), (2276.3, 994.1, 2279.3, 1059.5),
                      (2276.3, 1059.5, 2279.3, 1124.9), (2273.4, 1120.1, 2276.3, 1185.5)],
              dxs={"adega": 0.0, "escritorio": 286.6})
TRACO = 0.5
MONTANTE = 0.8


# ----------------------------------------------------------------------------------------------------------------------
def _janela(img, s, origem, vao, vidro, montante, horizontal):
    """O vão de janela como a do box do Subsolo (`subsolo_casac_2611.janela_box`): a soleira no travertino escuro, o vidro
    no meio, o contorno preto fino e o montante."""
    x0, y0, x1, y1 = vao
    img = T0.soleira(img, s, origem, [vao])
    img = T0.vidros(img, s, origem, (x0 - 3, y0 - 3, x1 + 3, y1 + 3), [[vidro]])
    t, m = TRACO, MONTANTE / 2
    linhas = [(x0, y0, x1, y0 + t), (x0, y1 - t, x1, y1), (x0, y0, x0 + t, y1), (x1 - t, y0, x1, y1)]
    if montante is not None:
        linhas.append((montante - m, y0, montante + m, y1) if horizontal else (x0, montante - m, x1, montante + m))
    return T0.pintar(img, s, origem, linhas, PERFIL)


def jardim(img, s, origem, q=JARDIM):
    for r, d, lados in q["beiras"]:
        img = U._copiar(img, s, origem, r, d, lados=lados, pena=2.0)
    # a sombra das paredes de cima e da direita na grama
    x0, y0, x1, y1 = q["grama"]
    jan = V.janela(img, q["grama"], s, origem, folga=0)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    d = np.minimum(Y - y0, x1 - X)
    dentro = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
    reg *= (1 - q["sombra"] * np.exp(-np.maximum(d, 0) / q["sombra_px"]) * dentro)[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    j = q["janela"]
    img = _janela(img, s, origem, j["vao"], j["vidro"], j["montante"], horizontal=False)
    return T0.soleira(img, s, origem, [q["filete"]])


def folha_tv(img, s, origem, q=FOLHA_TV):
    img = T0.pintar(img, s, origem, q["paredes"], PAREDE)
    for zonas in q["zonas"]:
        img = G.refazer(img, s, origem, zonas, objetos=q["folhas"], sombra=0.0, pena=1.0)
    return img


def fachada(img, s, origem, q=FACHADA):
    va, vb = q["vidro"]
    for x0, y0, x1, y1 in q["vaos"]:
        img = U._copiar(img, s, origem, (x0, q["piso"][0], x1, q["piso"][1]), q["d_piso"], lados="lrt", pena=1.2)
        img = _janela(img, s, origem, (x0, y0, x1, y1), (x0, va, x1, vb), (x0 + x1) / 2, horizontal=True)
    return img


def correr(img, s, origem, q=CORRER):
    for dx in q["dxs"].values():
        a, b, c, d = q["limpa"]
        img = G.refazer(img, s, origem, [((a + dx, b, c + dx, d), "ltb")], pena=1.2)
        img = T0.pintar(img, s, origem, [(r[0] + dx, r[1], r[2] + dx, r[3]) for r in q["paredes"]], PAREDE)
        a, b, c, d = q["soleira"]
        img = T0.soleira(img, s, origem, [(a + dx, b, c + dx, d)])
        img = D.folhas(img, s, origem, [(r[0] + dx, r[1], r[2] + dx, r[3]) for r in q["folhas"]])
    return img


FUNC = {"jardim": jardim, "folha_tv": folha_tv, "fachada": fachada, "correr": correr}
ITENS = {"jardim": (1108.0, 822.0, 1250.0, 990.0), "folha_tv": (1615.0, 655.0, 1660.0, 930.0),
         "fachada": (1225.0, 1625.0, 1640.0, 1665.0), "correr": (2262.0, 915.0, 2580.0, 1205.0)}


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

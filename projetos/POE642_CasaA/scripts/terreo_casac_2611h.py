"""Casa C Térreo, 8ª leva de 26/11: os sofás e as poltronas do estar.

Pedidos do usuário (recortes do 12K B): "corrigir sofá, encosto e braço" (os dois sofás do estar da esquerda), "corrigir
encosto do sofá" e "corrigir borda do sofá" (o sofá curvo do estar da direita), "e os outros sofás?".

O problema dos três é o mesmo do braço do sofá da sala TV (`terreo_casac_2611g`): um remendo de piso antigo, feito em
volta das peças, passou por cima da beira delas. No sofá de 3 lugares, uma faixa clara de 5 px comia a parte de fora dos
dois braços e o encosto de baixo; no de 2 lugares, o encosto (o lado direito) e as pontas dos braços sumiam sob um
recorte ondulado de travertino; no sofá curvo, a ponta do encosto e a beira de fora junto aos vasos estavam cortadas
retas.

- **Sofá de 3 lugares e sofá de 2 lugares** (E1, `propostas-estar-c/e1_sofa3` e `e1_sofa2`): o travertino de novo em
  volta de cada um (só no piso, fora do tapete e das mesinhas seixo), e a peça inteira pousada de novo no retângulo do
  PDF, na mesma escala de `proposta_estar_casac_1311`, com a sombra curta só no piso refeito (no tapete fica a de antes).
- **Sofá curvo** (`sala-de-estar/sofa-curvo-render-casa-a`, no encaixe de `mobiliario_terreo_casac_1311`): a peça inteira
  de novo por cima, no tom do linho de antes; as folhas da planta do vaso ao lado voltam por cima do encosto.
- **As 2 poltronas de cima do estar da direita** ("corrigir encosto das poltronas"; a de linho greige com pés de
  nogueira de `revisao_terreo_casac_1411`): o encosto estava cortado no topo (os pés de trás ficavam fora da concha) e a
  beira esfiapada; o travertino de novo em volta da parte de cima e a poltrona inteira pousada de novo na mesma pose.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611h.py [itens]
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
import um_pav_casaa_2511d as DD                  # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]
PX_M = 59.7059
BIB_E = Path(__file__).resolve().parent.parent / "biblioteca-objetos/02-terreo/sala-de-estar/propostas-estar-c"
SEIXOS = [(1716.0, 1530.0, 1751.0, 1590.0), (1973.0, 1526.0, 2010.0, 1586.0)]
SOFAS = {
    "sofa3": dict(png="e1_sofa3", ret=(1758.0, 1532.5, 1966.9, 1598.2), giro=180.0,
                  piso=[((1751.0, 1551.8, 1973.0, 1606.0), "lrb")], objetos=SEIXOS),
    "sofa2": dict(png="e1_sofa2", ret=(1979.4, 1376.5, 2033.2, 1513.8), giro=-90.0,
                  piso=[((2012.6, 1370.0, 2040.0, 1520.5), "rtb")], objetos=[]),
}
ESTICAR = 1.25
# as 2 poltronas de linho greige de cima (`revisao_terreo_casac_1411.poltronas_oliva`: o centro e a altura do retângulo
# do PDF); o piso refeito só na parte de cima, fora do tapete
POLTRONAS = dict(png="sala-de-estar/poltrona-greige-linho-pes-nogueira",
                 caixas=[(2162.68, 1314.83, 2209.15, 1364.04), (2225.05, 1314.83, 2271.53, 1364.04)], piso_y1=1342.0)
# o sofá curvo (`mobiliario_terreo_casac_1311.estar`: o encaixe no contorno do PDF) e a caixa da planta do vaso ao lado,
# cujas folhas ficam por cima do encosto
CURVO = dict(png="sala-de-estar/sofa-curvo-render-casa-a", pose=(2262.7515, 1539.8685, 185.4482, 99.9448, 200.0),
             planta=(2318.0, 1528.0, 2392.0, 1614.0))


# ----------------------------------------------------------------------------------------------------------------------
def _pose(q):
    P = cv2.imread(str(BIB_E / f"{q['png']}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)
    h, w = P.shape[:2]
    x0, y0, x1, y1 = q["ret"]
    L, Dd = (x1 - x0, y1 - y0) if q["giro"] in (0.0, 180.0) else (y1 - y0, x1 - x0)
    kL, kD = L / w, Dd / h
    k0 = min(kL, kD)
    kL, kD = min(kL, k0 * ESTICAR), min(kD, k0 * ESTICAR)
    return P, (x0 + x1) / 2, (y0 + y1) / 2, w * kL, h * kD


def repousar(img, s, origem, P, cx, cy, wt, ht, giro, zonas, objetos=(), sombra="movel"):
    """O piso de novo nas zonas (fora dos objetos e da peça) e a peça inteira por cima; a sombra dela só no piso refeito."""
    img = G.refazer(img, s, origem, zonas, objetos=list(objetos) + [_caixa(cx, cy, wt, ht, giro)], sombra=0.0,
                    pena=1.5)
    m = max(wt, ht) * 0.6 + 10
    jan = V.janela(img, (cx - m, cy - m, cx + m, cy + m), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    px, py = (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0
    novo = BT.pousar(reg.copy(), P, px, py, wt * s, ht * s, giro, BT.SOMBRAS[sombra], PX_M * s)
    Pw = P.copy()
    Pw[..., :3] = 255.0
    a = BT.pousar(np.zeros_like(reg), Pw, px, py, wt * s, ht * s, giro, [], PX_M * s)[..., 0] / 255.0
    z = np.zeros(a.shape, np.float32)
    for r, _l in zonas:
        z = np.maximum(z, V.cob([V.ret(*r)], jan, s, origem))
    if objetos:
        z *= 1 - np.clip(V.cob([V.ret(*r) for r in objetos], jan, s, origem), 0, 1)
    k = np.maximum(a, z)[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - k) + novo * k), 0, 255).astype(np.uint8)
    return img


def _caixa(cx, cy, wt, ht, giro):
    c, s_ = abs(np.cos(np.radians(giro))), abs(np.sin(np.radians(giro)))
    W, H = wt * c + ht * s_, wt * s_ + ht * c
    return (cx - W / 2, cy - H / 2, cx + W / 2, cy + H / 2)


def sofa(img, s, origem, nome):
    q = SOFAS[nome]
    P, cx, cy, wt, ht = _pose(q)
    return repousar(img, s, origem, P, cx, cy, wt, ht, q["giro"], q["piso"], q["objetos"])


def curvo(img, s, origem, q=CURVO):
    """O sofá curvo inteiro de novo por cima (a ponta do encosto e a beira de fora, cortadas pelo remendo do piso); as
    folhas da planta do vaso ao lado voltam por cima dele."""
    P = BT.ler_png(q["png"])
    cx, cy, wt, ht, g = q["pose"]
    m = max(wt, ht) * 0.6 + 10
    jan = V.janela(img, (cx - m, cy - m, cx + m, cy + m), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    px, py = (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0
    novo = BT.pousar(reg.copy(), P, px, py, wt * s, ht * s, g, [], PX_M * s)
    Pw = P.copy()
    Pw[..., :3] = 255.0
    a = BT.pousar(np.zeros_like(reg), Pw, px, py, wt * s, ht * s, g, [], PX_M * s)[..., 0] / 255.0
    # no tom do sofá de antes (o linho claro; as almofadas marrons fora da conta)
    dentro = (a > 0.97) & (reg.mean(2) > 170) & (novo.mean(2) > 150)
    ganho = np.median(reg[dentro], axis=0) / np.maximum(np.median(novo[dentro], axis=0), 1.0)
    novo = reg * (1 - a[..., None]) + (novo - reg * (1 - a[..., None])) * ganho[None, None, :]
    hsv = cv2.cvtColor(np.clip(reg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    verde = ((hsv[..., 0] >= 28) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 60)).astype(np.float32)
    verde *= V.cob([V.ret(*q["planta"])], jan, s, origem)
    r = max(1, int(round(0.6 * s)))
    verde = cv2.dilate(verde, np.ones((2 * r + 1, 2 * r + 1), np.uint8))
    verde = cv2.GaussianBlur(verde, (0, 0), 0.5 * s)
    k = (a * (1 - verde))[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - k) + novo * k), 0, 255).astype(np.uint8)
    return img


def poltronas(img, s, origem, q=POLTRONAS):
    P = BT.ler_png(q["png"])
    for x0, y0, x1, y1 in q["caixas"]:
        hh = y1 - y0
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        img = repousar(img, s, origem, P, cx, cy, hh * P.shape[1] / P.shape[0], hh, 0.0,
                       [((x0 - 7.0, y0 - 8.0, x1 + 7.0, q["piso_y1"]), "ltr")])
    return img


FUNC = {"sofa3": lambda img, s, o: sofa(img, s, o, "sofa3"), "sofa2": lambda img, s, o: sofa(img, s, o, "sofa2"),
        "curvo": curvo, "poltronas": poltronas}
ITENS = {"sofa3": (1700.0, 1500.0, 2030.0, 1615.0), "sofa2": (1960.0, 1360.0, 2060.0, 1530.0),
         "curvo": (2150.0, 1430.0, 2400.0, 1625.0), "poltronas": (2140.0, 1295.0, 2300.0, 1380.0)}


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

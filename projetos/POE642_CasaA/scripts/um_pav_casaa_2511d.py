"""Casa A 1º Pavimento, 4ª leva de 25/11 (pedidos do usuário com os recortes do 12K B).

- **Guarda-corpo do vazio grande** ("aqui tem um guarda corpo" e "mantenha o mesmo padrão de guarda corpo"): o mesmo
  desenho do guarda-corpo do vazio da sala íntima (ARQ_ELEMENTOS FIXOS: as duas linhas finas cinza a 1,2 px uma da
  outra com o vidro azulado entre elas), na borda da laje (2254,7 a 2255,9), da parede ao muro de baixo.
- **Box do chuveiro do banho master** ("represente melhor esse box de vidro"): os vidros do PDF (ARQ_LOUÇAS E METAIS)
  redesenhados no mesmo padrão: a folha fixa (1388,4 a 1460,5) e a de correr (1405,3 a 1477,4) em trilhos lado a lado,
  cada uma com o vidro azulado e as bordas finas, as pontas fechadas; o puxador na ponta da folha de correr. A faixa de
  antes (as linhas claras soltas) sai (o travertino refeito por baixo). No pé do box, junto à parede, os registros do PDF
  (dois, cada um com as duas alavancas) em metal escovado no lugar das manchas cinzas, e as outras manchas fora.
- **WC do banho master** ("represente melhor o box e a porta"): a divisória do PDF (ARQ_BANCADAS, 4 cm) inteira, da
  parede de cima à de baixo, com o braço de cima até 1685,7, na cor das paredes e de borda nítida (o resto borrado em
  volta sai); a porta de giro do PDF (folha de 0,80 m aberta junto à parede da direita, de 1547,5 a 1595,3) em madeira,
  no tom das folhas das portas do banho, com o contorno fino e a sombra curta.

Final, prancha e 12K A e B.

  python3 um_pav_casaa_2511d.py [item ...]
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
import esquadrias_pretas_1911 as EP  # noqa: E402
import vetor_2511 as V               # noqa: E402
import terreo_casaa_2511d as D       # noqa: E402
import um_pav_casaa_2511c as C       # noqa: E402

PLANTA = "A_1Pavimento"
# o padrão dos guarda-corpos e dos vidros (medido no guarda-corpo do vazio da sala íntima)
LINHA_VIDRO = (142.0, 144.0, 145.0)
VIDRO = (205.0, 219.0, 231.0)


def _vidro(reg, jan, s, origem, r, eixo, larg=0.30):
    """Um vidro em planta no padrão do guarda-corpo: as duas bordas finas cinza e o azulado entre elas, as pontas
    fechadas. eixo "v": o vidro corre em y (as bordas em x0 e x1); "h": corre em x (as bordas em y0 e y1)."""
    x0, y0, x1, y1 = r
    meio = V.cob([V.ret(*r)], jan, s, origem)
    reg = V.compor(reg, meio, np.float32(VIDRO))
    h = larg / 2
    if eixo == "v":
        bordas = [V.ret(x0 - h, y0, x0 + h, y1), V.ret(x1 - h, y0, x1 + h, y1),
                  V.ret(x0 - h, y0 - h, x1 + h, y0 + h), V.ret(x0 - h, y1 - h, x1 + h, y1 + h)]
    else:
        bordas = [V.ret(x0, y0 - h, x1, y0 + h), V.ret(x0, y1 - h, x1, y1 + h),
                  V.ret(x0 - h, y0 - h, x0 + h, y1 + h), V.ret(x1 - h, y0 - h, x1 + h, y1 + h)]
    a = np.zeros(meio.shape, np.float32)
    for b in bordas:
        a = np.maximum(a, V.cob([b], jan, s, origem))
    return V.compor(reg, a, np.float32(LINHA_VIDRO))


# ----------------------------------------------------------------------------------------------------------------------
# como o do vazio da sala íntima na imagem: a linha cinza, o vidro azulado e a linha cinza, cada um com ~1 px da final
GUARDA = dict(caixa=(2248.0, 606.0, 2262.0, 882.0), vidro=(2254.1, 610.6, 2257.0, 878.8), linha=0.9,
              antes=(2254.2, 610.6, 2257.0, 878.8), branco_de=(2257.4, 610.6, 2259.6, 878.8))


def guarda_b(img, s, origem, q=GUARDA):
    jan, reg = C._reg(img, q["caixa"], s, origem)
    # o vidro de antes (o claro com as bordas escuras) sai: à esquerda o piso fica, à direita o branco do vazio
    x0, y0, x1, y1 = q["antes"]
    xm = q["vidro"][2]
    fx0, fy0, fx1, fy1 = V.janela(img, q["branco_de"], s, origem, folga=0)
    branco = np.median(img[fy0:fy1, fx0:fx1].reshape(-1, 3).astype(np.float32), axis=0)
    reg = V.compor(reg, V.cob([V.ret(xm, y0, x1, y1)], jan, s, origem), branco)
    gx0, gy0, gx1, gy1 = q["vidro"]
    e = q["linha"]
    reg = V.compor(reg, V.cob([V.ret(*q["vidro"])], jan, s, origem), np.float32(VIDRO))
    reg = V.compor(reg, V.cob([V.ret(gx0, gy0, gx0 + e, gy1), V.ret(gx1 - e, gy0, gx1, gy1)], jan, s, origem),
                   np.float32(LINHA_VIDRO))
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
BOX = dict(faixa=(1387.9, 1563.6, 1528.2, 1570.4), faixa_luz=[(1392.0, 1554.0, 1526.0, 1563.4),
                                                               (1392.0, 1570.6, 1526.0, 1580.0)],
           fixo=(1388.4, 1564.8, 1460.5, 1566.9), correr=(1405.3, 1566.9, 1477.4, 1569.0), borda=0.6,
           puxador=(1473.3, 1565.0, 1474.3, 1570.2, 0.4),
           pe=(1388.2, 1620.8, 1528.0, 1630.9), pe_luz=[(1392.0, 1608.0, 1526.0, 1620.5)],
           registros=[1419.4, 1490.6],
           metal=(196.0, 199.0, 202.0), brilho=(238.0, 240.0, 242.0), sombra_metal=(128.0, 131.0, 135.0),
           contorno=(96.0, 98.0, 101.0), sombra=0.28)


def box_chuveiro(img, s, origem, q=BOX):
    img = D.refazer_piso(img, s, origem, [V.ret(*q["faixa"])], ref_luz=[V.ret(*r) for r in q["faixa_luz"]], pena=0.5)
    img = D.refazer_piso(img, s, origem, [V.ret(*q["pe"])], ref_luz=[V.ret(*r) for r in q["pe_luz"]], pena=0.8)
    jan, reg = C._reg(img, (1384.0, 1560.0, 1532.0, 1633.0), s, origem, folga=int(2 * s) + 2)
    H, W = reg.shape[:2]
    # os vidros (a folha de correr por dentro, a fixa por fora) e o puxador
    reg = _vidro(reg, jan, s, origem, q["fixo"], "h", larg=q["borda"])
    reg = _vidro(reg, jan, s, origem, q["correr"], "h", larg=q["borda"])
    pecas = [(q["puxador"], "y")]
    # os registros no pé do box (o espelho junto à parede e as duas alavancas)
    for x in q["registros"]:
        pecas.append(((x - 1.0, 1629.8, x + 8.2, 1631.0, 0.4), "x"))
        pecas.append(((x + 0.6, 1626.6, x + 1.7, 1630.2, 0.5), "y"))
        pecas.append(((x + 4.6, 1626.6, x + 5.7, 1630.2, 0.5), "y"))
    tudo = np.zeros((H, W), np.float32)
    for r, _ in pecas:
        tudo = np.maximum(tudo, C._arred(r, jan, s, origem))
    sb = cv2.GaussianBlur(tudo, (0, 0), max(0.5 * s, 0.5))
    Ms = np.float32([[1, 0, 0.6 * s], [0, 1, -0.7 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - tudo)
    reg *= (1 - q["sombra"] * sb)[..., None]
    for r, eixo in pecas:
        reg, _ = C._metal(reg, jan, s, origem, r, q, eixo)
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
WC = dict(limpa=[(1670.7, 1546.9, 1674.6, 1631.0), (1670.7, 1546.9, 1690.0, 1551.2), (1685.7, 1542.6, 1689.6, 1546.9),
                 (1668.3, 1541.8, 1689.6, 1544.5), (1727.6, 1542.6, 1736.3, 1600.5), (1719.5, 1542.2, 1736.3, 1550.0)],
          limpa_luz=[(1676.0, 1552.0, 1725.0, 1590.0), (1676.0, 1530.0, 1725.0, 1541.0)],
          divisoria=[(1668.3, 1544.5, 1670.7, 1631.1), (1670.7, 1544.5, 1685.7, 1546.9)], parede=(80.0, 80.0, 80.0),
          folha=(1731.6, 1547.5, 1734.0, 1595.3), madeira=(120.0, 148.0, 181.0), contorno=(84.0, 100.0, 120.0),
          sombra=0.22)


def wc(img, s, origem, q=WC):
    # o borrado em volta da divisória e a folha de antes saem (o travertino do WC)
    img = D.refazer_piso(img, s, origem, [V.ret(*r) for r in q["limpa"]], ref_luz=[V.ret(*r) for r in q["limpa_luz"]],
                         pena=0.6)
    jan, reg = C._reg(img, (1664.0, 1540.0, 1740.0, 1634.0), s, origem, folga=int(2 * s) + 2)
    H, W = reg.shape[:2]
    # a divisória inteira, na cor das paredes, com a borda nítida
    reg = V.compor(reg, V.cob([V.ret(*r) for r in q["divisoria"]], jan, s, origem), np.float32(q["parede"]))
    # a folha da porta: a sombra curta, a madeira com o veio ao comprido, o contorno fino
    af = V.cob([V.ret(*q["folha"])], jan, s, origem)
    sb = cv2.GaussianBlur(af, (0, 0), max(0.6 * s, 0.5))
    Ms = np.float32([[1, 0, -0.7 * s], [0, 1, 0.6 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - af)
    reg *= (1 - q["sombra"] * sb)[..., None]
    xs, ys = V.coords(jan, s, origem)
    veio = 1.0 + 0.05 * np.sin(xs[None, :] * 7.3) * np.cos(ys[:, None] * 0.21) + 0 * ys[:, None]
    mad = np.float32(q["madeira"])[None, None, :] * veio[..., None]
    reg = reg * (1 - af[..., None]) + mad * af[..., None]
    x0, y0, x1, y1 = q["folha"]
    e = 0.24
    dentro = V.cob([V.ret(x0 + e, y0 + e, x1 - e, y1 - e)], jan, s, origem)
    reg = V.compor(reg, np.clip(af - dentro, 0, 1), np.float32(q["contorno"]))
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
ITENS = {"guarda_b": (2244.0, 600.0, 2266.0, 885.0), "box_chuveiro": (1384.0, 1556.0, 1534.0, 1636.0),
         "wc": (1660.0, 1536.0, 1742.0, 1636.0)}
FUNC = {"guarda_b": guarda_b, "box_chuveiro": box_chuveiro, "wc": wc}


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def _registro(base, cinza, dz, caixa):
    x0, y0, x1, y1 = caixa
    mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
    A, B_ = mapa(x0, y0)
    ex_ = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
    ey_ = (mapa(x0, y0 + 1000.0)[1] - B_) / 1000.0
    sx = (ex_ * (x1 - x0) + ey_ * (y1 - y0)) / ((x1 - x0) + (y1 - y0))
    return sx, (x0 - A / sx, y0 - B_ / sx), cc


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
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            sx, org, cc = _registro(base, cinza, dz, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

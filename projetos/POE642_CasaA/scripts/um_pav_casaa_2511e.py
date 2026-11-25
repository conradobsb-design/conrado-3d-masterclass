"""Casa A 1º Pavimento, 5ª leva de 25/11 (pedidos do usuário com os recortes do 12K B).

- **Vidros sem linha técnica** ("tem que ser box e folhas de vidro sem linha técnica"): todas as folhas desta leva
  (`folhas_vidro`) no vidro claro dos boxes (`boxes_claros_1911.VIDRO`), sem contorno: um pouco mais escuro junto às
  faces e mais claro no meio (a espessura do vidro), com a sombra curta no piso.
- **WC do banho master** ("porta de vidro e traz esquadria no tom vidro, em vez de preta"): a divisória em L (a do PDF,
  da parede de cima à de baixo, com o braço de cima até 1685,7) deixa de ser cinza de parede e vira uma peça de vidro
  só; a porta de giro (a folha de 0,80 m aberta junto à parede da direita) deixa de ser madeira e vira uma folha de
  vidro, presa ("essa porta não pode ficar solta"): a folha sobe até o batente do PDF (1733,4 a 1736,4, de 1544,5 a
  1546,9), em vidro com ela, numa peça só encostada na parede, e a dobradiça de metal escovado prende a folha ao
  batente e à parede (sai o pontinho claro que havia na parede ali). O piso em volta é refeito; o canto da parede de baixo junto à divisória volta a ser parede, linha a linha pela
  parede de logo ao lado (a 4ª leva tinha deixado ali um dente de piso).
- **Box do chuveiro do banho master** ("faz com o box fechado e no lugar da esquadria preta à direita, deixe-a em
  vidro"): a folha de correr passa para a posição fechada (de 1456,3 até o vidro da direita, sobrepondo a fixa), com o
  puxador na ponta; a peça escura da direita (ARQ_BANCADAS, 1528,4 a 1530,8, do vidro de cima à parede de baixo) vira
  uma folha de vidro, e o piso em volta é refeito. As folhas de antes, com as bordas cinza, saem.

Final, prancha e 12K A e B.

  python3 um_pav_casaa_2511e.py [item ...]
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
import um_pav_casaa_2511d as DD      # noqa: E402

PLANTA = "A_1Pavimento"


VIDRO_H = dict(tinta=(218.0, 214.0, 204.0), alfa=0.88, borda=0.90, meio=1.04, sombra=0.16)


def folhas_vidro(reg, jan, s, origem, folhas, q=VIDRO_H):
    """Folhas de vidro humanizadas, sem linha técnica: cada folha (uma lista de retângulos, a união é uma peça só) no
    vidro claro dos boxes (`boxes_claros_1911.VIDRO`), um pouco mais escuro junto às faces e mais claro no meio (a
    espessura do vidro), com a sombra curta no piso. Sem contorno."""
    H, W = reg.shape[:2]
    cobs = []
    for rets in folhas:
        a = np.zeros((H, W), np.float32)
        for r in rets:
            a = np.maximum(a, V.cob([V.ret(*r)], jan, s, origem))
        cobs.append(a)
    # as sombras de todas antes dos vidros
    tudo = np.max(cobs, axis=0)
    sb = cv2.GaussianBlur(tudo, (0, 0), max(0.6 * s, 0.5))
    Ms = np.float32([[1, 0, 0.5 * s], [0, 1, 0.6 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - tudo)
    reg = reg * (1 - q["sombra"] * sb)[..., None]
    for rets, a in zip(folhas, cobs):
        meia = min(min(r[2] - r[0], r[3] - r[1]) for r in rets) / 2 * s
        d = cv2.distanceTransform((a > 0.5).astype(np.uint8), cv2.DIST_L2, 3)
        t = np.clip((d - 0.5) / max(meia, 0.5), 0, 1)
        g = q["borda"] + (q["meio"] - q["borda"]) * np.sqrt(t)
        cor = np.float32(q["tinta"])[None, None, :] * g[..., None]
        k = (q["alfa"] * a)[..., None]
        reg = reg * (1 - k) + cor * k
    return reg


# ----------------------------------------------------------------------------------------------------------------------
WC = dict(limpa=[(1666.8, 1543.2, 1672.2, 1631.0), (1666.8, 1543.2, 1687.0, 1548.2), (1729.0, 1543.6, 1735.0, 1597.6)],
          limpa_luz=[(1676.0, 1552.0, 1725.0, 1590.0), (1676.0, 1530.0, 1725.0, 1541.0)],
          parede_de_baixo=(1670.7, 1624.3, 1676.4, 1631.1), parede_fonte=(1677.0, 1683.0),
          divisoria=[(1668.3, 1544.5, 1670.7, 1631.1), (1670.7, 1544.5, 1685.7, 1546.9)],
          folha=(1731.6, 1544.5, 1734.0, 1595.3), batente=(1733.4, 1544.5, 1736.4, 1546.9),
          dobradica=(1731.9, 1545.0, 1736.4, 1546.4, 0.35), parede_lado=(1736.3, 1543.8, 1738.6, 1547.8),
          parede_lado_fonte=(1549.0, 1554.0))


def wc_vidro(img, s, origem, q=WC):
    # a divisória escura e a folha de madeira saem (o travertino do WC e do banho)
    img = D.refazer_piso(img, s, origem, [V.ret(*r) for r in q["limpa"]], ref_luz=[V.ret(*r) for r in q["limpa_luz"]],
                         pena=0.6)
    jan, reg = C._reg(img, (1664.0, 1540.0, 1740.0, 1634.0), s, origem, folga=int(2 * s) + 2)
    # o canto da parede de baixo, junto à divisória: linha a linha, a parede de logo ao lado (a mesma borda)
    xs, ys = V.coords(jan, s, origem)
    fonte = (xs >= q["parede_fonte"][0]) & (xs <= q["parede_fonte"][1])
    perfil = np.median(reg[:, fonte], axis=1)
    a = V.cob([V.ret(*q["parede_de_baixo"])], jan, s, origem)[..., None]
    reg = reg * (1 - a) + perfil[:, None, :] * a
    # a parede da direita junto ao batente, coluna a coluna pela parede de logo abaixo (sai o pontinho claro)
    fonte_y = (ys >= q["parede_lado_fonte"][0]) & (ys <= q["parede_lado_fonte"][1])
    perfil_x = np.median(reg[fonte_y], axis=0)
    a = V.cob([V.ret(*q["parede_lado"])], jan, s, origem)[..., None]
    reg = reg * (1 - a) + perfil_x[None, :, :] * a
    # a divisória em L (uma peça só) e a folha da porta presa ao batente junto à parede (uma peça só), de vidro, sem
    # linha técnica
    reg = folhas_vidro(reg, jan, s, origem, [q["divisoria"], [q["folha"], q["batente"]]])
    # a dobradiça: a chapa de metal que prende a folha ao batente e à parede, com a sombra curta
    H, W = reg.shape[:2]
    r = q["dobradica"]
    a = C._arred(r, jan, s, origem)
    sb = cv2.GaussianBlur(a, (0, 0), max(0.5 * s, 0.5))
    Ms = np.float32([[1, 0, 0.5 * s], [0, 1, 0.6 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - a)
    reg *= (1 - DD.BOX["sombra"] * sb)[..., None]
    reg, _ = C._metal(reg, jan, s, origem, r, DD.BOX, "x")
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
BOX = dict(DD.BOX, correr=(1456.3, 1566.9, 1528.4, 1569.0), puxador=(1523.3, 1565.0, 1524.3, 1570.2, 0.4),
           lateral=(1528.4, 1565.4, 1530.8, 1631.1), lateral_limpa=(1527.3, 1563.4, 1531.4, 1630.9),
           lateral_luz=[(1500.0, 1572.0, 1526.0, 1594.0), (1533.0, 1570.0, 1545.0, 1592.0)])


def box_fechado(img, s, origem, q=BOX):
    # os vidros de cima de antes e a peça escura da direita saem (o travertino refeito)
    img = D.refazer_piso(img, s, origem, [V.ret(*q["faixa"])], ref_luz=[V.ret(*r) for r in q["faixa_luz"]], pena=0.5)
    img = D.refazer_piso(img, s, origem, [V.ret(*q["lateral_limpa"])], ref_luz=[V.ret(*r) for r in q["lateral_luz"]],
                         pena=0.4)
    jan, reg = C._reg(img, (1384.0, 1560.0, 1534.0, 1633.0), s, origem, folga=int(2 * s) + 2)
    H, W = reg.shape[:2]
    # o vidro da direita (do vidro de cima à parede de baixo), a folha fixa e a de correr fechada (até o vidro da
    # direita), sem linha técnica
    reg = folhas_vidro(reg, jan, s, origem, [[q["lateral"]], [q["fixo"]], [q["correr"]]])
    # o puxador na ponta da folha de correr, com a sombra curta
    r = q["puxador"]
    a = C._arred(r, jan, s, origem)
    sb = cv2.GaussianBlur(a, (0, 0), max(0.5 * s, 0.5))
    Ms = np.float32([[1, 0, 0.6 * s], [0, 1, -0.7 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - a)
    reg *= (1 - q["sombra"] * sb)[..., None]
    reg, _ = C._metal(reg, jan, s, origem, r, q, "y")
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
ITENS = {"wc_vidro": (1660.0, 1536.0, 1742.0, 1636.0), "box_fechado": (1384.0, 1556.0, 1536.0, 1636.0)}
FUNC = {"wc_vidro": wc_vidro, "box_fechado": box_fechado}


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
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            sx, org, cc = DD._registro(base, cinza, dz, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

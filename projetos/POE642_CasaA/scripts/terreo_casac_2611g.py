"""Casa C Térreo, 7ª leva de 26/11: a porta da sala de almoço, o tapete e o sofá da sala TV, o aparador da circulação e o
pano de vidro entre a varanda gourmet e o estar.

Pedidos do usuário (recortes do 12K B):

- **Sala de almoço** ("aqui é uma porta", a abertura de cima para a garagem): em 661b927 as duas aberturas foram fechadas
  como janela ("representar como janela fechada" valia para a folha que atravessa a passagem, a de baixo). A de cima volta
  a ser porta: a soleira escura fica, o vidro do meio sai, e a folha pivotante do PDF entra aberta a 90° (2639,1 a 2722,7
  x 689,0 a 692,0), no padrão das folhas da Casa C (o perfil claro com o contorno preto fino, como a pivotante do hall e
  a do lavabo, `terreo_casaa_2511d.folhas`).
- **Sala TV**:
  - "corrigir o tapete em volta da mesa": em volta das mesas de centro, o aro claro e a meia-lua cinza (o remendo de
    `terreo_casac_2611c` e a sombra forte da mesa) saem: o tapete de novo num anel de 9 px (a trama sintetizada da
    amostra limpa do próprio tapete, na luz casada pela beira de fora), e a sombra das mesas mais curta e mais leve;
  - "corrigir sofá e tapete" / "o braço do sofá ... complete para que não vejamos o piso" / "o braço do sofá da sala TV
    está quebrado": o braço direito do sofá perdia a metade de fora nos últimos 25 px antes da parede (o travertino
    aparecia ali); agora o braço inteiro vai até a parede (o próprio braço de cima, copiado). A barra de baixo do tapete
    chega ao braço (parava 11 px antes), o filete claro entre o braço e o tapete e o halo cinza em cima do braço viram
    tapete, e o resto do contorno antigo embaixo do braço sai. A barra da direita e a poltrona por cima dela ficam como
    estavam ("atenção aqui": a poltrona sobre a borda do tapete não é tocada);
  - "dar mais textura ao tapete": a trama do tapete (o detalhe fino, acima de 1,4 px) 2 vezes mais marcada, no tapete
    inteiro menos as peças por cima (o sofá, as mesas, a poltrona) e a barra.
- **Aparador da circulação** ("corrigir falha no móvel, adorno e piso"): o aparador da biblioteca com os objetos
  (`hall/aparador-freijo-objetos`) tinha sido encurtado com um corte seco (a emenda vertical no tampo) e os galhos secos
  do vaso viravam manchas escuras na escala da planta. Agora: a madeira inteira de novo (as pontas da peça e um trecho
  limpo esticado na horizontal, o veio é horizontal), sem emenda; o vaso sem os galhos (a boca escura limpa), o livro e
  a tigela inteiros, com a sombra deles, nas mesmas posições relativas; o piso em volta (o halo cinza embaixo e à
  esquerda) de novo, com a sombra curta do aparador.
- **Pano de vidro varanda gourmet / estar** ("corrigir as folhas de vidro"): o fixo e as 2 folhas de correr do PDF (o
  fixo no trilho de dentro da parede de cima até 1343,1; a 1ª folha no trilho do meio de 1338,3 a 1479,2; a 2ª no de
  fora de 1474,5 até a parede de baixo), sobrepostas nas juntas e ligadas às paredes, no padrão das portas de correr da
  casa; saem as folhas antigas (a folha fantasma cinza à esquerda, os perfis claros nas juntas e nas pontas, a linha do
  contrapiso).

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611g.py [itens]
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
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import terreo_casac_2611 as T0                   # noqa: E402
import terreo_casac_2611c as TC                  # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]
PX_M = 59.7059

ALMOCO = dict(vao=(2703.3, 671.3, 2712.2, 756.3), folha=(2639.1, 689.0, 2722.7, 692.0))
# o pano de vidro entre a varanda gourmet e o estar (PDF): o fixo no trilho de dentro, de parede a parede com a 1ª folha
# de correr, e as 2 folhas de correr nos trilhos do meio e de fora, sobrepostas 4,8 px nas juntas
VIDRO_GOURMET = dict(limpa=(1626.6, 1199.8, 1647.5, 1617.8),
                     folhas=[(1634.5, 1199.8, 1637.4, 1343.1), (1637.4, 1338.3, 1640.4, 1479.2),
                             (1640.4, 1474.5, 1643.4, 1617.8)])

MESAS = [(1438.45, 770.7, 35.85), (1474.25, 776.65, 23.85)]
TAPETE = dict(interior=(1318.5, 709.5, 1551.5, 888.5), amostra=(1320.0, 712.0, 1392.0, 790.0),
              anel=9.0, beira=4.0, luz_sig=6.0, sombra=0.16, sombra_d=(-0.8, 1.0), sombra_sig=1.3,
              ganho=1.0, detalhe_sig=1.4, semente=7,
              sofa=[(1319.5, 795.5, 1381.5, 906.0), (1319.5, 847.0, 1531.9, 912.7)],
              # o trecho da barra de baixo que faltava, do braço do sofá até onde ela parava
              barra=(1531.9, 1543.5),
              laterais=[(1506.5, 844.7, 10.0)],
              poltrona=[(1583.8, 801.4), (1580.1, 800.2), (1545.4, 819.5), (1543.4, 823.9), (1556.4, 843.0),
                        (1561.4, 848.4), (1570.5, 855.4), (1574.4, 856.5), (1586.5, 852.6), (1592.4, 848.2),
                        (1597.0, 840.1), (1597.0, 837.9), (1593.3, 821.7)],
              filete=((1531.8, 849.0, 1535.6, 888.5), (6.0, 0.0), "rtb"),
              halo=((1516.0, 843.0, 1531.0, 848.6), (0.0, -12.0), "lrt"),
              resto=((1531.8, 891.5, 1541.0, 906.0), "rb"),
              # o braço direito do sofá até a parede (a metade de fora sumia nos últimos 25 px): o próprio braço de cima
              braco=((1514.2, 884.0, 1531.9, 912.7), (0.0, -27.0), "t"))
APARADOR = dict(ret=(2313.8, 1200.0, 2433.0, 1223.6), zona=(2306.0, 1199.8, 2435.5, 1233.0),
                png="hall/aparador-freijo-objetos",
                # na peça (px dela): os blocos de madeira lisa que cobrem cada objeto (a, b, desloc.) e os objetos
                # (centro x, centro y, meia-largura, meia-altura, forma)
                # a madeira: as pontas da peça e, entre elas, um trecho limpo (sem objetos) esticado na horizontal (o veio
                # é horizontal); os galhos do vaso saem (inpaint dos traços escuros finos, fora da boca do vaso)
                pontas=40, limpo=(580, 1100), boca=(405, 185, 23), galhos=(330, 92, 560, 330),
                objetos=[(432, 205, 108, 108, "disco"), (1315, 197, 200, 160, "ret"), (2185, 203, 122, 122, "disco")],
                pena=18)


# ----------------------------------------------------------------------------------------------------------------------
def porta_almoco(img, s, origem, q=ALMOCO):
    img = T0.soleira(img, s, origem, [q["vao"]])
    return D.folhas(img, s, origem, [q["folha"]])


def vidro_gourmet(img, s, origem, q=VIDRO_GOURMET):
    img = G.refazer(img, s, origem, [(q["limpa"], "lr")], pena=1.2)
    return D.folhas(img, s, origem, q["folhas"])


# ----------------------------------------------------------------------------------------------------------------------
def _discos(X, Y, mesas, extra=0.0, pena=0.6):
    a = np.zeros(X.shape, np.float32)
    for cx, cy, r in mesas:
        a = np.maximum(a, np.clip((r + extra - np.hypot(X - cx, Y - cy)) / pena + 0.5, 0, 1))
    return a


def _poli(X, Y, pts, s):
    m = np.zeros(X.shape, np.uint8)
    x0, y0 = X[0, 0], Y[0, 0]
    p = np.int32([[(x - x0) * s * 4, (y - y0) * s * 4] for x, y in pts])
    cv2.fillPoly(m, [p], 1, shift=2)
    return m.astype(np.float32)


def tapete_mesas(img, s, origem, q=TAPETE):
    """O anel em volta das mesas de centro: a trama do tapete sintetizada da amostra limpa, na luz da beira de fora."""
    r_ext = max(r for *_c, r in MESAS) + q["anel"] + q["beira"] + 4
    caixa = (min(cx - r for cx, _cy, r in MESAS) - q["anel"] - q["beira"] - 4,
             min(cy - r for _cx, cy, r in MESAS) - q["anel"] - q["beira"] - 4,
             max(cx + r for cx, _cy, r in MESAS) + q["anel"] + q["beira"] + 4,
             max(cy + r for _cx, cy, r in MESAS) + q["anel"] + q["beira"] + 4)
    del r_ext
    jan = V.janela(img, caixa, s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    mesa = _discos(X, Y, MESAS, 0.0)
    zona = _discos(X, Y, MESAS, q["anel"], pena=2.0) * (1 - mesa)
    fora = (_discos(X, Y, MESAS, q["anel"] + q["beira"]) > 0.5) & (_discos(X, Y, MESAS, q["anel"] + 0.5) < 0.5)
    T = G._quilt(img, s, origem, q["amostra"], H, W, semente=q.get("semente", 2611))
    r = cv2.GaussianBlur(reg, (0, 0), 1.0 * s) / np.maximum(cv2.GaussianBlur(T, (0, 0), 1.0 * s), 1.0)
    g = fora.astype(np.float32)
    luz = cv2.GaussianBlur(r * g[..., None], (0, 0), q["luz_sig"] * s) / \
        np.maximum(cv2.GaussianBlur(g, (0, 0), q["luz_sig"] * s)[..., None], 1e-4)
    novo = T * luz
    out = reg * (1 - zona[..., None]) + novo * zona[..., None]
    # a sombra das mesas, mais curta e mais leve
    sdx, sdy = q["sombra_d"]
    M = np.float32([[1, 0, sdx * s], [0, 1, sdy * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(mesa, M, (W, H)), (0, 0), q["sombra_sig"] * s) * (1 - mesa)
    out *= (1 - q["sombra"] * sb)[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def tapete_sofa(img, s, origem, q=TAPETE):
    r, d, lados = q["halo"]
    img = U._copiar(img, s, origem, r, d, lados=lados, pena=1.2)
    r, d, lados = q["filete"]
    img = U._copiar(img, s, origem, r, d, lados=lados, pena=1.0)
    r, lados = q["resto"]
    img = G.refazer(img, s, origem, [(r, lados)], pena=1.5)
    # só o trecho que faltava da barra de baixo (o resto da barra e a poltrona por cima dela ficam como estão)
    xa, xb = q["barra"]
    x0, y0, x1, y1 = TC.TAPETE_TV["ret"]
    fora = [(x0 - 5, y0 - 5, x1 + 5, y1 - 4), (x0 - 5, y1 + 0.5, x1 + 5, y1 + 5),
            (x0 - 5, y0 - 5, xa, y1 + 5), (xb, y0 - 5, x1 + 5, y1 + 5)]
    return TC.tapete_tv(img, s, origem, q=dict(TC.TAPETE_TV, sofa=fora))


def braco_sofa(img, s, origem, q=TAPETE):
    r, d, lados = q["braco"]
    return U._copiar(img, s, origem, r, d, lados=lados, pena=1.5)


def tapete_textura(img, s, origem, q=TAPETE):
    jan = V.janela(img, q["interior"], s, origem, folga=0)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    pecas = np.clip(V.cob([V.ret(*r) for r in q["sofa"]], jan, s, origem), 0, 1)
    pecas = np.maximum(pecas, _discos(X, Y, [(cx, cy, r + 1.2) for cx, cy, r in MESAS]))
    pecas = np.maximum(pecas, _discos(X, Y, q["laterais"]))
    pecas = np.maximum(pecas, _poli(X, Y, q["poltrona"], s))
    pecas = cv2.dilate(pecas, np.ones((3, 3), np.uint8)) if s > 1.5 else pecas
    pecas = cv2.GaussianBlur(pecas, (0, 0), 0.6 * s)
    dentro = V.cob([V.ret(*q["interior"])], jan, s, origem)
    w = np.clip(dentro - pecas, 0, 1)
    sig = q["detalhe_sig"] * s
    base = cv2.GaussianBlur(reg, (0, 0), sig)
    novo = base + (reg - base) * (1 + q["ganho"])
    out = reg * (1 - w[..., None]) + novo * w[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def sala_tv(img, s, origem):
    img = tapete_mesas(img, s, origem)
    img = tapete_sofa(img, s, origem)
    img = tapete_textura(img, s, origem)
    return braco_sofa(img, s, origem)


# ----------------------------------------------------------------------------------------------------------------------
_PECA = {}


def _aparador(q=APARADOR):
    """A peça da biblioteca na proporção do PDF: a madeira (as pontas e o trecho limpo esticado na horizontal) e os
    objetos inteiros (com a sombra deles) por cima, nas posições relativas da peça; o vaso sem os galhos secos."""
    if "p" in _PECA:
        return _PECA["p"]
    P = BT.ler_png(q["png"])
    h, w = P.shape[:2]
    x0, y0, x1, y1 = q["ret"]
    W2 = int(round(h * (x1 - x0) / (y1 - y0)))
    k = W2 / w
    # os galhos: traços escuros finos (black-hat) em volta do vaso, menos a boca
    gx0, gy0, gx1, gy1 = q["galhos"]
    rgb = np.clip(P[gy0:gy1, gx0:gx1, :3], 0, 255).astype(np.uint8)
    cinza = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    bh = cv2.morphologyEx(cinza, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    m = (bh > 14).astype(np.uint8)
    bx, by, br = q["boca"]
    yy, xx = np.mgrid[gy0:gy1, gx0:gx1]
    m[np.hypot(xx - bx, yy - by) < br] = 0
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    P = P.copy()
    P[gy0:gy1, gx0:gx1, :3] = cv2.inpaint(rgb, m, 6, cv2.INPAINT_TELEA).astype(np.float32)
    # a boca do vaso sem as hastes: o escuro dela, com a beira suave
    d = np.hypot(xx - bx, yy - by)
    reg = P[gy0:gy1, gx0:gx1, :3]
    escuro = np.median(reg[(d < br) & (cinza < np.percentile(cinza[d < br], 25))], axis=0)
    a = np.clip((br - d) / 3.0, 0, 1)[..., None]
    P[gy0:gy1, gx0:gx1, :3] = reg * (1 - a) + escuro[None, None] * a
    # a madeira
    pt = q["pontas"]
    la, lb = q["limpo"]
    meio = cv2.resize(P[:, la:lb], (W2 - 2 * pt, h), interpolation=cv2.INTER_CUBIC)
    out = np.concatenate([P[:, :pt], meio, P[:, w - pt:]], axis=1)
    pe = q["pena"]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for cx, cy, mx, my, forma in q["objetos"]:
        if forma == "disco":
            dist = mx - np.hypot(xx - cx, yy - cy)
        else:
            dist = np.minimum(mx - np.abs(xx - cx), my - np.abs(yy - cy))
        alfa = np.clip(dist / pe, 0, 1)
        dxp = int(round(cx * k - cx))
        ys_, xs_ = np.nonzero(alfa > 0)
        xa, xb, ya, yb = xs_.min(), xs_.max() + 1, ys_.min(), ys_.max() + 1
        al = alfa[ya:yb, xa:xb, None]
        out[ya:yb, xa + dxp:xb + dxp] = out[ya:yb, xa + dxp:xb + dxp] * (1 - al) + P[ya:yb, xa:xb] * al
    _PECA["p"] = np.ascontiguousarray(out)
    return _PECA["p"]


def aparador(img, s, origem, q=APARADOR):
    img = G.refazer(img, s, origem, [(q["zona"], "lrb")], objetos=[q["ret"]], sombra=0.0, pena=2.0)
    x0, y0, x1, y1 = q["ret"]
    P = _aparador(q)
    m = max(x1 - x0, y1 - y0) * 0.6 + 8
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    jan = V.janela(img, (cx - m, cy - m, cx + m, cy + m), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    reg = BT.pousar(reg, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, (x1 - x0) * s, (y1 - y0) * s, 0.0,
                    BT.SOMBRAS["movel"], PX_M * s)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"porta_almoco": porta_almoco, "sala_tv": sala_tv, "aparador": aparador, "vidro_gourmet": vidro_gourmet}
ITENS = {"porta_almoco": (2630.0, 660.0, 2730.0, 770.0), "sala_tv": (1300.0, 695.0, 1600.0, 910.0),
         "aparador": (2295.0, 1185.0, 2450.0, 1240.0), "vidro_gourmet": (1615.0, 1185.0, 1660.0, 1630.0)}


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

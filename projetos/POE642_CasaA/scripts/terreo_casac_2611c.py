"""Casa C Térreo, 3ª leva de 26/11: cozinha, circulação, BH master 1 e sala TV.

Pedidos do usuário (recortes do 12K B):

- **cozinha** ("corrigir torneiras e erro abaixo das cubas"): as 2 torneiras eram borrões cinza; agora a torneira do
  PDF em planta (a base redonda junto à parede, a alavanca para a direita e a bica comprida até perto do ralo), em
  cromado (o cilindro com o brilho no meio e a borda mais escura), com a sombra curta; o borrão velho sai (a pedra de
  cima vem de 12 px ao lado, o fundo da cuba de 9 px à esquerda). Embaixo de cada cuba, na frente da bancada, havia
  um fio marrom-escuro (o contorno antigo da cuba): a faixa entre a cuba e a frente da bancada vem do mesmo Danae à
  direita das cubas (`CUBAS["faixa"]`), com a frente da bancada igual à do resto.
- **armário da circulação** ("remover linhas técnicas do móvel"): o armário de 1660 a 2168 tinha o contorno duplo (o
  fio de dentro a 3 px da borda) e a barra escura embaixo; agora a cor sólida dos armários das casas (a mesma de
  `correcoes_terreo_casab_1611.armarios`: o tom de armário, a face 0,86 na borda de 1 px e a sombra curta).
- **BH master 1** ("corrigir vaso"): o retângulo branco e os restos cinza do vaso antigo saem (o travertino de novo,
  com o tracejado do box de volta nos traços que ficam à vista); a bacia Carrara da biblioteca no contorno do PDF
  (21,1 x 30,7 px, a caixa acoplada junto à parede de cima).
- **sala TV**:
  - "corrigir móvel e suas extremidades": o rack (as pontas tortas, a sombra borrada embaixo da TV) refeito no
    retângulo do PDF, na cor sólida dos armários, com a TV em grafite por cima; o travertino em volta de novo;
  - "marcar bordas do tapete": a barra de 3 px (5 cm) num tom só (o do tapete a 84%, como na Casa B) na borda da
    trama do tapete (de 1316 a 1554 e de 707 a 891, 2 a 5 px para dentro do contorno do PDF), por baixo do sofá;
  - "melhore a representação dessas mesas redondas. entre freijó e nogueira": as mesas de centro (o par de alturas
    diferentes) em tom e sobretom, a grande em nogueira por cima da pequena em freijó, e as 2 mesinhas laterais em
    nogueira (as madeiras e o desenho das mesinhas seixo e redondas do estar, `correcoes_terreo_casac_1711`); o tapete
    em volta das mesas velhas (o aro cinza e a sombra) refeito com o próprio tapete;
  - "corrigir poltrona e sua representação": a poltrona branca com os restos cinza em volta vira a poltrona de leitura
    da biblioteca (bouclé off-white, a da Casa B), no contorno do PDF (49 px de fundo, o encosto para baixo e para a
    direita, a frente para o tapete), no tom do sofá; o piso em volta de novo (o travertino fora do tapete, o tapete de
    cima dentro dele);
  - "corrigir vaso e plantas e sua representação": o vaso de folhagem A de novo no círculo do PDF, sem o borrão claro
    em volta (o travertino de novo).

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611c.py [itens]
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
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import correcoes_terreo_casac_1711 as CC         # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]
PX_M = 59.7059
COR_ARMARIO = (129.0, 160.0, 189.0)      # `revisao_terreo_casac_1311.COZINHA["cor_armario"]`
FACE = 0.86
SOMBRA_ARM = 0.22

# ----------------------------------------------------------------------------------------------------------------------
CUBAS = dict(dx=47.9,                                          # da cuba 1 para a 2
             faixa=[((2256.5, 288.95, 2301.0, 292.3), (95.0, 0.0)), ((2304.5, 288.95, 2350.0, 292.3), (48.0, 0.0))],
             # o borrão da torneira: a pedra de cima e o fundo da cuba (r, d) — d da cuba 2 em `d2`
             pedra=(2274.0, 255.0, 2285.0, 262.6), d_pedra=(12.0, 0.0), d2_pedra=(-12.0, 0.0),
             fundo=(2275.3, 262.4, 2282.7, 271.8), d_fundo=(-9.0, 0.0),
             # a torneira do PDF (px da final, cuba 1)
             base=(2278.4, 260.2), base_r=1.7, bica=((2278.4, 260.2), (2278.4, 270.6)), bica_r=0.62,
             alavanca=((2278.4, 260.2), (2281.9, 260.2)), alavanca_r=0.5,
             cromo=(198.0, 200.0, 203.0), brilho=(246.0, 247.0, 248.0), borda=(112.0, 114.0, 118.0),
             sombra=0.30, sombra_d=(-0.6, 0.9), sombra_sig=0.55)
ARMARIO_CIRC = (1659.6, 671.4, 2168.4, 714.6)                 # a borda de cima é a parede
RACK = dict(zona=(1318.0, 579.2, 1562.0, 610.0), rack=(1332.9, 578.8, 1544.9, 602.7),
            tv=(1387.9, 578.8, 1484.0, 581.8), grafite=(54.0, 54.0, 58.0), contorno=(36.0, 36.0, 40.0))
BHM1 = dict(zona=(842.0, 328.0, 886.0, 366.0), tracejado=(354.2, 356.9), bacia=(864.25, 343.15, 21.1, 31.1),
            caixa=(853.7, 327.6, 874.8, 358.7))
TAPETE_TV = dict(ret=(1315.5, 706.5, 1554.5, 891.5), borda=3.0, tom=0.84,
                 sofa=[(1319.5, 795.5, 1381.5, 905.0), (1319.5, 855.5, 1543.0, 905.0)],
                 amostra=(1330.0, 712.0, 1395.0, 785.0))
MESAS_TV = dict(grande=(1438.45, 770.7, 35.85), pequena=(1474.25, 776.65, 23.85),
                d_grande=(-78.0, -22.0), d_pequena=(48.0, -38.0), folga=6.0,
                laterais=[(1506.5, 844.7, 8.95), (1600.9, 805.8, 8.95)])
POLTRONA_TV = dict(png="escritorio/poltrona-leitura", centro=(1573.4, 832.0), alto=49.0, giro=209.3,
                   tapete=((1540.5, 800.0, 1556.6, 866.0), (0.0, -88.0)),
                   piso=((1556.6, 793.0, 1617.0, 873.0), "trb"), sofa=(1400.0, 870.0, 1500.0, 885.0), ganho=1.04)
VASO_TV = dict(c=(1277.8, 875.9), d=50.0, zona_r=33.0, xmax=1311.0, sofa_x=1319.0)


# ----------------------------------------------------------------------------------------------------------------------
def _pousar(img, s, origem, P, cx, cy, wt, ht, ang, sombra):
    m = max(wt, ht) * 0.75 + 8
    jan = V.janela(img, (cx - m, cy - m, cx + m, cy + m), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    reg = BT.pousar(reg, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, wt * s, ht * s, ang,
                    BT.SOMBRAS[sombra] if sombra else [], PX_M * s)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def _solido(img, s, origem, r, cor, lados_face="lrb", sombra=SOMBRA_ARM):
    """O retângulo r na cor sólida, com a face mais escura (1 px) nos lados de `lados_face` e a sombra curta."""
    x0, y0, x1, y1 = r
    jan = V.janela(img, (x0 - 6, y0 - 6, x1 + 6, y1 + 6), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    a = V.cob([V.ret(*r)], jan, s, origem)
    e = 1.0
    mi = (x0 + (e if "l" in lados_face else 0), y0 + (e if "t" in lados_face else 0),
          x1 - (e if "r" in lados_face else 0), y1 - (e if "b" in lados_face else 0))
    miolo = V.cob([V.ret(*mi)], jan, s, origem)
    M = np.float32([[1, 0, -1.0 * s], [0, 1, 1.3 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (W, H)), (0, 0), 1.1 * s) * (1 - a)
    reg = reg * (1 - sombra * sb)[..., None]
    c = np.float32(cor)
    face = a - miolo
    reg = reg * (1 - face[..., None]) + c * FACE * face[..., None]
    reg = reg * (1 - miolo[..., None]) + c * miolo[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def _capsula(X, Y, p, q, r):
    """A distância (px da final) ao segmento pq menos r, e a posição transversal t (-1..1)."""
    p, q = np.float64(p), np.float64(q)
    d = q - p
    L2 = float(d @ d)
    u = np.clip(((X - p[0]) * d[0] + (Y - p[1]) * d[1]) / max(L2, 1e-9), 0, 1)
    cx, cy = p[0] + u * d[0], p[1] + u * d[1]
    dist = np.hypot(X - cx, Y - cy) - r
    n = np.array([-d[1], d[0]]) / np.sqrt(max(L2, 1e-9))
    t = ((X - cx) * n[0] + (Y - cy) * n[1]) / r
    return dist, np.clip(t, -1, 1)


# ----------------------------------------------------------------------------------------------------------------------
def cubas(img, s, origem, q=CUBAS):
    for r, d in q["faixa"]:
        img = U._copiar(img, s, origem, r, d, lados="lr", pena=1.0)
    for k in range(2):
        dx = q["dx"] * k
        r = q["pedra"]
        img = U._copiar(img, s, origem, (r[0] + dx, r[1], r[2] + dx, r[3]), q["d2_pedra"] if k else q["d_pedra"],
                        lados="lr", pena=0.8)
        r = q["fundo"]
        img = U._copiar(img, s, origem, (r[0] + dx, r[1], r[2] + dx, r[3]), q["d_fundo"], lados="lrb", pena=0.8)
        img = _torneira(img, s, origem, dx, q)
    return img


def _torneira(img, s, origem, dx, q):
    bx, by = q["base"]
    jan = V.janela(img, (bx + dx - 4, by - 4, bx + dx + 6, q["bica"][1][1] + 4), s, origem, folga=3)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs - dx, ys)
    cromo, brilho, borda = (np.float32(q[k]) for k in ("cromo", "brilho", "borda"))

    def alfa(dist):
        return np.clip(0.5 - dist * s, 0, 1).astype(np.float32)

    pecas = []
    for p, r_ in (("alavanca", q["alavanca_r"]), ("bica", q["bica_r"])):
        dist, t = _capsula(X, Y, q[p][0], q[p][1], r_)
        luz = np.exp(-((t + 0.25) / 0.38) ** 2)                 # o brilho no meio, um pouco para a esquerda
        esc = np.clip(np.abs(t) - 0.55, 0, 1) / 0.45            # a borda do cilindro
        cor = cromo + (brilho - cromo) * luz[..., None] * 0.9
        cor = cor * (1 - esc[..., None]) + borda * esc[..., None]
        pecas.append((alfa(dist), cor))
    rr = np.hypot(X - bx, Y - by)
    dist = rr - q["base_r"]
    t = np.clip(rr / q["base_r"], 0, 1)
    luz = np.exp(-(np.hypot(X - bx + 0.45, Y - by + 0.45) / 0.75) ** 2)
    esc = np.clip(t - 0.7, 0, 1) / 0.3
    cor = cromo + (brilho - cromo) * luz[..., None]
    cor = cor * (1 - esc[..., None]) + borda * esc[..., None]
    pecas.append((alfa(dist), cor))
    tot = np.zeros(reg.shape[:2], np.float32)
    for a, _c in pecas:
        tot = np.maximum(tot, a)
    H, W = tot.shape
    sdx, sdy = q["sombra_d"]
    M = np.float32([[1, 0, sdx * s], [0, 1, sdy * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(tot, M, (W, H)), (0, 0), q["sombra_sig"] * s) * (1 - tot)
    reg = reg * (1 - q["sombra"] * sb)[..., None]
    for a, c in pecas:
        reg = reg * (1 - a[..., None]) + c * a[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def armario_circ(img, s, origem):
    return _solido(img, s, origem, ARMARIO_CIRC, COR_ARMARIO, "lrb")


def rack(img, s, origem, q=RACK):
    img = G.refazer(img, s, origem, [(q["zona"], "lrb")], objetos=[q["rack"]], sombra=0.0, pena=3.0)
    img = _solido(img, s, origem, q["rack"], COR_ARMARIO, "lrb")
    # a TV em grafite, a sombra curta para baixo
    x0, y0, x1, y1 = q["tv"]
    jan = V.janela(img, (x0 - 4, y0 - 1, x1 + 4, y1 + 4), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    a = V.cob([V.ret(*q["tv"])], jan, s, origem)
    mi = V.cob([V.ret(x0 + 0.4, y0, x1 - 0.4, y1 - 0.4)], jan, s, origem)
    M = np.float32([[1, 0, -0.5 * s], [0, 1, 0.9 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (W, H)), (0, 0), 0.6 * s) * (1 - a)
    reg = reg * (1 - 0.30 * sb)[..., None]
    reg = reg * (1 - a[..., None]) + np.float32(q["contorno"]) * a[..., None]
    reg = reg * (1 - mi[..., None]) + np.float32(q["grafite"]) * mi[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def vaso_bhm1(img, s, origem, q=BHM1):
    x0, y0, x1, y1 = q["zona"]
    jan = V.janela(img, q["zona"], s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    antes = img[Y0:Y1, X0:X1].astype(np.float32)
    img = G.refazer(img, s, origem, [(q["zona"], "lrb")], pena=2.5)
    # o tracejado do box de volta (os traços escuros na faixa dele), fora da bacia
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    ta, tb = q["tracejado"]
    cx0, _cy0, cx1, _cy1 = q["caixa"]
    faixa = (Y >= ta) & (Y <= tb) & ((X < cx0 + 0.5) | (X > cx1 - 0.5))
    dif = reg.mean(2) - antes.mean(2)
    w = np.clip((dif - 18.0) / 25.0, 0, 1) * faixa
    reg = reg * (1 - w[..., None]) + antes * w[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    cx, cy, bw, bh = q["bacia"]
    P, wt, ht = B1.preparar("banho-master/bacia-carrara", bw, bh)
    return _pousar(img, s, origem, P, cx, cy, wt, ht, 0.0, "baixa")


# ----------------------------------------------------------------------------------------------------------------------
def _disco(img, s, origem, cx, cy, r, d, pena=1.5):
    """O disco (cx, cy, r) recebe a imagem deslocada d (px da final), com a beira suave."""
    jan = V.janela(img, (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    dx, dy = int(round(d[0] * s)), int(round(d[1] * s))
    fonte = img[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    a = np.clip((r - np.hypot(X - cx, Y - cy)) / pena + 0.5, 0, 1)[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + fonte * a), 0, 255).astype(np.uint8)
    return img


def _mesa(img, s, origem, cx, cy, r, madeira, limpa=0.0):
    """A mesa redonda (o tampo de `correcoes_terreo_casac_1711._tampo`) na madeira pedida; com `limpa` (px), o aro em
    volta inpintado antes (as mesinhas pequenas)."""
    f = r + limpa + 8
    jan = V.janela(img, (cx - f, cy - f, cx + f, cy + f), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1]
    t = np.linspace(0, 2 * np.pi, 144, endpoint=False)
    pts = [((cx + r * np.cos(a) - origem[0]) * s, (cy + r * np.sin(a) - origem[1]) * s) for a in t]
    if limpa:
        xs, ys = V.coords(jan, s, origem)
        X, Y = np.meshgrid(xs, ys)
        bur = (np.hypot(X - cx, Y - cy) < r + limpa).astype(np.uint8)
        reg = cv2.inpaint(np.ascontiguousarray(reg), bur, max(3, int(3 * s)), cv2.INPAINT_TELEA)
    R = reg.astype(np.float32)
    q = dict(CC.SEIXOS, nogueira_a=CC.SEIXOS_NOG_A, freijo_c=(CC.SEIXOS["freijo"][0], (24, 24, 632, 168)), _s=s)
    CC._tampo(R, X0, Y0, pts, madeira, q)
    img[Y0:Y1, X0:X1] = np.clip(np.round(R), 0, 255).astype(np.uint8)
    return img


def vaso_tv(img, s, origem, q=VASO_TV):
    cx, cy = q["c"]
    R = q["zona_r"]
    zona = [(min(cx + R * np.cos(a), q["xmax"]), cy + R * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 96, endpoint=False)]
    img = D.refazer_piso(img, s, origem, [zona], objetos=(), sombra=0.0)
    P, wt, ht = B1.preparar("sala-intima/vaso-folhagem-a", q["d"], q["d"])
    return _pousar(img, s, origem, P, cx, cy, wt, ht, 0.0, "movel")


def tapete_tv(img, s, origem, q=TAPETE_TV):
    x0, y0, x1, y1 = q["ret"]
    b = q["borda"]
    jan = V.janela(img, (x0 - 2, y0 - 2, x1 + 2, y1 + 2), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    A = V.cob([V.ret(*q["ret"])], jan, s, origem)
    Ain = V.cob([V.ret(x0 + b, y0 + b, x1 - b, y1 - b)], jan, s, origem)
    sofa = np.clip(V.cob([V.ret(*r) for r in q["sofa"]], jan, s, origem), 0, 1)
    fx = np.clip(A - Ain, 0, 1) * (1 - sofa)
    xs, ys = V.coords(jan, s, origem)
    am = q["amostra"]
    sel = ((xs >= am[0]) & (xs <= am[2]))[None, :] & ((ys >= am[1]) & (ys <= am[3]))[:, None]
    cor = np.median(reg[sel], axis=0) * q["tom"]
    reg = reg * (1 - fx[..., None]) + cor[None, None, :] * fx[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def mesas_tv(img, s, origem, q=MESAS_TV):
    for nome in ("grande", "pequena"):
        cx, cy, r = q[nome]
        img = _disco(img, s, origem, cx, cy, r + q["folga"], q["d_" + nome])
    cx, cy, r = q["pequena"]
    img = _mesa(img, s, origem, cx, cy, r, "freijo_c")     # sem a beira escura da foto
    cx, cy, r = q["grande"]
    img = _mesa(img, s, origem, cx, cy, r, "nogueira")
    for cx, cy, r in q["laterais"]:
        img = _mesa(img, s, origem, cx, cy, r, "nogueira_a", limpa=2.6)
    return img


def poltrona_piso(img, s, origem, q=POLTRONA_TV):
    r, d = q["tapete"]
    img = U._copiar(img, s, origem, r, d, lados="tb", pena=2.0)
    r, lados = q["piso"]
    return G.refazer(img, s, origem, [(r, lados)], pena=3.0)


def poltrona_tv(img, s, origem, q=POLTRONA_TV):
    P = BT.ler_png(q["png"]) if (BT.BIB / f"{q['png']}.png").exists() else B1.ler_png(q["png"])
    jan = V.janela(img, q["sofa"], s, origem, folga=0)
    X0, Y0, X1, Y1 = jan
    cor = np.median(img[Y0:Y1, X0:X1].reshape(-1, 3).astype(np.float32), axis=0) * q["ganho"]
    a = P[..., 3] > 200
    P = P.copy()
    P[..., :3] = np.clip(P[..., :3] * (cor / np.maximum(np.median(P[..., :3][a], axis=0), 1))[None, None], 0, 255)
    h, w = P.shape[:2]
    ht = q["alto"]
    wt = ht * w / h
    cx, cy = q["centro"]
    return _pousar(img, s, origem, P, cx, cy, wt, ht, q["giro"], "movel")


def sala_tv(img, s, origem):
    img = vaso_tv(img, s, origem)
    img = poltrona_piso(img, s, origem)
    img = mesas_tv(img, s, origem)
    img = tapete_tv(img, s, origem)
    return poltrona_tv(img, s, origem)


FUNC = {"cubas": cubas, "armario_circ": armario_circ, "rack": rack, "vaso_bhm1": vaso_bhm1, "sala_tv": sala_tv}
ITENS = {"cubas": (2245.0, 245.0, 2360.0, 300.0), "armario_circ": (1650.0, 660.0, 2180.0, 725.0),
         "rack": (1310.0, 568.0, 1570.0, 615.0), "vaso_bhm1": (830.0, 318.0, 898.0, 372.0),
         "sala_tv": (1240.0, 695.0, 1620.0, 905.0)}


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

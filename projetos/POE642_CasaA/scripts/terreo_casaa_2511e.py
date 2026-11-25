"""Casa A Térreo, 5ª leva de 25/11 (os recortes do 12K B): o banho varanda, o sofá curvo da varanda e a cuba do lavabo.

- **Banho varanda** ("corrigir mancha do piso e chuveiro de acordo com a biblioteca"): o piso do banho refeito inteiro
  (o travertino novo com a luz do lugar, sem as manchas da direita e de baixo, sem o fantasma do chuveiro antigo), em
  dois trechos (acima e abaixo do vidro do box); a bacia, a folha da porta, o nicho da parede e o vidro ficam, o rótulo
  volta por cima. O chuveiro: o quadrado de parede da biblioteca (`banho-varanda/chuveiro-quadrado-parede.png`), o
  crivo endireitado (a foto é em perspectiva: o trapézio vira o quadrado de 0,20 m do PDF), o braço esticado até a
  parede da direita, a canopla na parede; o contorno fino escuro (o cromado claro sobre o travertino claro sumia) e a
  sombra curta.

Final, prancha e 12K A e B.

  python3 terreo_casaa_2511e.py [item ...]
"""
import json
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

PLANTA = "A_Terreo"
BIB = D.BIB
PX_M_ = 59.70590031258779


# ----------------------------------------------------------------------------------------------------------------------
# Banho varanda
BANHO_VARANDA = dict(
    zonas=[(1617.5, 1459.6, 1697.0, 1563.2), (1617.5, 1567.0, 1697.0, 1629.0)],   # acima e abaixo do vidro do box
    bacia=(1646.6, 1458.0, 1668.0, 1490.8, 10.7),
    objetos=[(1616.0, 1543.2, 1672.0, 1549.0),      # a folha da porta
             (1610.0, 1580.3, 1619.4, 1605.4),      # o nicho da parede da esquerda
             (1618.5, 1590.6, 1623.2, 1595.2)],     # o registro
    crivo=(1668.7, 1591.2, 1680.5, 1603.0), parede=1697.0,
    png=BIB / "02-terreo/banho-varanda/chuveiro-quadrado-parede.png",
    contorno=(96, 98, 102), contorno_larg=0.22, sombra=0.30)
_CH = {}


def _chuveiro_png(q=BANHO_VARANDA):
    """O chuveiro da biblioteca montado em planta: a canopla (linhas 16-75 da foto), o tubo (76-195) e o crivo (196-383,
    um trapézio pela perspectiva, endireitado no quadrado), o tubo no comprimento até a parede; girado com o braço para
    a direita. Devolve (rgb, alfa, retângulo em px da final)."""
    if "p" in _CH:
        return _CH["p"]
    P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
    rgb, a = P[..., :3], P[..., 3:] / 255.0
    Pm = np.concatenate([rgb * a, a], 2)                     # pré-multiplicado (sem a franja do fundo)
    W = Pm.shape[1]
    cx0, cx1 = 13.0, 291.0                                   # o crivo na foto (a largura de cima)
    u = (cx1 - cx0) / (q["crivo"][2] - q["crivo"][0])        # px da foto por px da final
    lado = cx1 - cx0
    src = np.float32([[13, 196], [291, 196], [282, 384], [22, 384]])
    dst = np.float32([[13, 0], [291, 0], [291, lado], [13, lado]])
    crivo = cv2.warpPerspective(Pm, cv2.getPerspectiveTransform(src, dst), (W, int(round(lado))),
                                flags=cv2.INTER_LINEAR)
    canopla = Pm[16:76]
    comp = (q["parede"] - q["crivo"][2]) * u - canopla.shape[0]   # o tubo até a canopla na parede
    tubo = cv2.resize(Pm[76:196], (W, max(2, int(round(comp)))), interpolation=cv2.INTER_LINEAR)
    M = np.concatenate([canopla, tubo, crivo], 0)
    M = np.rot90(M, 3).copy()                                # o braço (o alto da foto) para a direita
    e = max(1, int(round(q["contorno_larg"] * u)))
    pad = e + 2
    M = cv2.copyMakeBorder(M, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    al = np.clip(M[..., 3], 0, 1)
    cor = M[..., :3] / np.maximum(al, 1e-3)[..., None]
    # o contorno fino escuro em volta (o cromado claro some no travertino claro)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * e + 1, 2 * e + 1))
    anel = np.clip(cv2.dilate(al, k) - al, 0, 1)
    cor = (cor * al[..., None] + np.float32(q["contorno"]) * anel[..., None]) / np.maximum(al + anel, 1e-3)[..., None]
    al = np.clip(al + anel, 0, 1)
    h, w = al.shape
    x0 = q["crivo"][0] - pad / u
    y0 = q["crivo"][1] - (cx0 + pad) / u                     # as colunas da foto viram as linhas (o giro)
    r = (x0, y0, x0 + w / u, y0 + h / u)
    _CH["p"] = (cor.astype(np.float32), al.astype(np.float32), r)
    return _CH["p"]


def banho_varanda(img, escala, origem, q=BANHO_VARANDA):
    x0, y0, x1, y1, rb = q["bacia"]
    objs = [D._ret_arred(x0, y0, x1, y1, rb)] + [V.ret(*r) for r in q["objetos"]]
    for z in q["zonas"]:
        img = D.refazer_piso(img, escala, origem, [V.ret(*z)], objetos=objs, sombra=0.10, letras=True, luz_sig=12.0)
    rgb, a, r = _chuveiro_png(q)
    img = D.pousar(img, escala, origem, rgb, a, r, q["sombra"])
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Varanda ("corrigir tapete, sofá e piso atrás da sofá"): o piso atrás do sofá (da parede ao tapete, e à direita do
# tapete até o vidro) refeito inteiro, sem a faixa cinza junto à parede e as manchas atrás do sofá; o tapete inteiro de
# novo (a trama do próprio tapete costurada por image quilting, num tom só, sem o retângulo claro e as sombras soltas
# dos remendos); por cima, as peças da biblioteca nos mesmos lugares (`biblioteca_terreo_casaa_1211`: as 2 poltronas,
# o sofá curvo, o banco, as 2 mesas de centro e as 2 mesinhas), com as sombras de lá, só no piso e no tapete refeitos:
# o sofá volta inteiro (a madeira das costas, que o recorte das plantas tinha cortado); as 2 palmeiras-ráfis de volta.
VARANDA = dict(
    zonas=[(1605.0, 353.5, 1870.0, 396.4), (1797.2, 396.4, 1870.0, 530.0)],   # acima do tapete; à direita dele
    pena=3.0,                                         # a emenda suave na esquerda (x = 1605) e embaixo (y = 530)
    tapete=(1618.0, 396.4, 1797.2, 545.7),
    fontes=[(1640.0, 399.0, 1695.0, 436.0), (1640.0, 500.0, 1688.0, 530.0), (1722.0, 516.0, 1790.0, 531.0)],
    p=10.0, semente=11)


def _b1211():
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        import biblioteca_terreo_casaa_1211 as B
    return B


def _pecas_varanda():
    B = _b1211()
    g = B.girar_pt
    return B, [("varanda/poltrona-externa-a", 1614.7, 429.7, 49, None, g(1, 0), "movel"),
               ("varanda/poltrona-externa-a", 1614.7, 511.0, 49, None, g(1, 0), "movel"),
               ("varanda/sofa-curvo-externo", 1772.0, 433.0, 152, None, g(-0.89, 0.46), "movel"),
               ("lounge-dos-brises/banco-brises", 1710.1, 552.7, 119, 30, 0.0, "movel"),
               ("varanda/mesa-centro-seixo", 1692.5, 456.5, 46, 40, 30.0, "mesa"),
               ("varanda/mesa-centro-seixo", 1713.5, 484.5, 66, 42, -55.0, "mesa"),
               ("lounge-dos-brises/mesa-lateral-externa", 1619.3, 469.5, 18, None, 0.0, "baixa"),
               ("lounge-dos-brises/mesa-lateral-externa", 1708.0, 392.5, 18, None, 0.0, "baixa")]


def _faixa(xs, a, b, pena):
    """1 dentro de [a, b], subindo em `pena` a partir de a (se a não é None) e descendo até b (se b não é None)."""
    f = np.ones_like(xs)
    if a is not None:
        f = np.minimum(f, np.clip((xs - a) / pena, 0, 1))
    if b is not None:
        f = np.minimum(f, np.clip((b - xs) / pena, 0, 1))
    return f


def _piso_m(reg, TT, a, livre, tol=0.07, luz_sig=12.0, escala=1.0):
    """O travertino novo (TT vezes a luz do lugar) no alfa a; a luz: a razão imagem/textura nos px livres perto do
    valor mais frequente, alisada."""
    r = reg.mean(2) / np.maximum(TT.mean(2), 1.0)
    h, e = np.histogram(r[livre], bins=80, range=(0.6, 1.4))
    h = np.convolve(h, np.ones(5) / 5, mode="same")
    med = float(e[np.argmax(h)] + (e[1] - e[0]) / 2)
    ok = livre & (np.abs(r - med) < tol)
    sig = luz_sig * escala
    num = cv2.GaussianBlur(np.where(ok, r, 0).astype(np.float32), (0, 0), sig)
    den = cv2.GaussianBlur(ok.astype(np.float32), (0, 0), sig)
    luz = np.where(den > 1e-3, num / np.maximum(den, 1e-3), med)
    return reg * (1 - a[..., None]) + (TT * luz[..., None]) * a[..., None]


def _tecido_tapete(img, escala, origem, q=VARANDA):
    """A trama do tapete (image quilting das fontes, cada uma sem o degradê de luz), no tom mediano delas, do tamanho
    do tapete (px da imagem, a partir do canto de cima à esquerda da janela do tapete)."""
    sys.path.insert(0, str(EP.PROJ / "_texturas"))
    import texturas
    fs, todos = [], []
    for f in q["fontes"]:
        X0, Y0, X1, Y1 = V.janela(img, f, escala, origem, folga=0)
        P = img[Y0:Y1, X0:X1].astype(np.float32)
        todos.append(P.reshape(-1, 3))
        lisa = cv2.GaussianBlur(P, (0, 0), 4.0 * escala)
        P = P / np.maximum(lisa, 1.0) * P.reshape(-1, 3).mean(0)
        fs += [np.clip(P, 0, 255).astype(np.uint8), np.ascontiguousarray(np.clip(P[:, ::-1], 0, 255).astype(np.uint8))]
    alvo = np.median(np.concatenate(todos), axis=0)
    jan = V.janela(img, q["tapete"], escala, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    p = max(8, int(round(q["p"] * escala)))
    tec = texturas.quilting(fs, Y1 - Y0, X1 - X0, p=p, sobra=max(3, p // 3),
                            rng=np.random.default_rng(q["semente"]))[:Y1 - Y0, :X1 - X0].astype(np.float32)
    tec *= (alvo / np.maximum(np.median(tec.reshape(-1, 3), axis=0), 1.0))[None, None]
    return tec, jan


def varanda(img, escala, origem, q=VARANDA):
    B, pecas = _pecas_varanda()
    s = escala
    zonas = [V.ret(*z) for z in q["zonas"]]
    jan = V.janela(img, D._bbox(zonas + [V.ret(*q["tapete"])] + [V.ret(1585.0, 380.0, 1775.0, 575.0)]), s, origem,
                   folga=int(8 * s) + 2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    # as peças (o alfa, no lugar da biblioteca): fora da medida da luz
    can = np.zeros((H, W, 3), np.float32)
    for nome, cx, cy, w, h, ang, _ in pecas:
        P, wt, ht = B.preparar(nome, w, h)
        P = P.copy()
        P[..., :3] = 255
        B.pousar(can, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, wt * s, ht * s, ang, [], PX_M_ * s)
    alfa = can[..., 0] / 255.0
    for cx, cy, r, _ in D.PLANTAS["pecas"][:2]:
        alfa = np.maximum(alfa, V.cob([D._circulo(cx, cy, r + 2.0, 64)], jan, s, origem))
    # 1. o piso atrás do sofá
    a1 = V.cob([zonas[0]], jan, s, origem) * _faixa(xs, q["zonas"][0][0], None, q["pena"])[None, :]
    a2 = V.cob([zonas[1]], jan, s, origem) * _faixa(ys, None, q["zonas"][1][3], q["pena"])[:, None]
    az = np.clip(a1 + a2, 0, 1)
    livre = (az > 0.99) & (cv2.dilate((alfa > 0.05).astype(np.uint8), np.ones((5, 5), np.uint8)) == 0)
    reg = _piso_m(reg, D.piso_tt(jan, s), az, livre, escala=s)
    # 2. o tapete inteiro
    tec, tj = _tecido_tapete(img, s, origem, q)
    at = V.cob([V.ret(*q["tapete"])], jan, s, origem)
    T = np.zeros_like(reg)
    T[tj[1] - Y0:tj[3] - Y0, tj[0] - X0:tj[2] - X0] = tec
    reg = reg * (1 - at[..., None]) + T * at[..., None]
    # 3. as peças por cima, com as sombras só no que foi refeito
    nao = (az <= 0.0) & (at <= 0.0)
    for nome, cx, cy, w, h, ang, som in pecas:
        P, wt, ht = B.preparar(nome, w, h)
        B.pousar(reg, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, wt * s, ht * s, ang, B.SOMBRAS[som],
                 PX_M_ * s, nao=nao)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    # 4. as palmeiras-ráfis de volta
    for cx, cy, r, g in D.PLANTAS["pecas"][:2]:
        rgb, a = D._png(D.PLANTAS["png"])
        rgb, a = D._gira(rgb, a, g)
        img = D.pousar(img, s, origem, rgb, a, (cx - r, cy - r, cx + r, cy + r), D.PLANTAS["sombra"])
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Lavabo ("corrigir manchas escura e borda da cuba"): a faixa escura no piso à esquerda da bancada (a sombra velha
# dura e a mancha junto ao rótulo) refeita no travertino com a luz do lugar, o rótulo por cima; a peça de cima da
# bancada (a da cuba) de novo no travertino do piso um pouco mais escuro, com a luz da cuba esculpida da biblioteca
# (`lavabo/cuba-esculpida-poros-render.png`, esticada nos lados e girada como em `biblioteca_terreo_casaa_1211`),
# sem os poros da foto (a mediana): a borda da cuba nítida em qualquer escala, no lugar da luz borrada da final
# antiga ampliada; a torneira da biblioteca por cima.
LAVABO_CUBA = dict(
    piso=(2305.0, 404.0, 2316.6, 470.0), piso_luz=(2286.0, 404.0, 2312.0, 470.0),
    peca=(2315.6, 410.0, 2345.4, 467.4), baixo=(2327.5, 467.4, 2345.4, 514.5),
    cuba=("lavabo/cuba-esculpida-poros-render", 2330.55, 438.65, 57.3, 29.9, -90.0, "lavabo"),
    escurecer=0.90, mediana=7, borda=0.22)


def lavabo_cuba(img, escala, origem, q=LAVABO_CUBA):
    B = _b1211()
    s = escala
    # o piso à esquerda da bancada
    img = D.refazer_piso(img, s, origem, [V.ret(*q["piso"])], objetos=[V.ret(*q["baixo"])], sombra=0.0,
                         letras=True, luz_sig=10.0, tol=0.06, ref_luz=[V.ret(*q["piso_luz"])])
    # a luz da cuba esculpida (a foto sem os poros), no lugar da biblioteca
    nome, cx, cy, w, h, ang, extra = q["cuba"]
    P, wt, ht = B.preparar(nome, w, h, extra)
    L = P[..., :3].mean(2)
    Lm = cv2.medianBlur(np.clip(L, 0, 255).astype(np.uint8), q["mediana"]).astype(np.float32)
    cor = P[..., :3]
    croma = cor.max(2) - cor.min(2)
    metal = ((croma < 14) & (L < 215) & (P[..., 3] > 128)).astype(np.float32)
    metal = cv2.morphologyEx(metal, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    jan = V.janela(img, q["peca"], s, origem, folga=3)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    cxw, cyw = (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0
    camadas = []
    for canal in (np.dstack([Lm, Lm, Lm, P[..., 3]]), np.dstack([metal * 255] * 3 + [P[..., 3]]),
                  np.dstack([cor, P[..., 3]])):
        can = np.zeros((H, W, 3), np.float32)
        B.pousar(can, canal.astype(np.float32), cxw, cyw, wt * s, ht * s, ang, [], PX_M_ * s)
        camadas.append(can)
    luz, mt, cor_r = camadas[0][..., 0], np.clip(camadas[1][..., 0] / 255.0, 0, 1), camadas[2]
    ap = V.cob([V.ret(*q["peca"])], jan, s, origem)
    dentro = (ap > 0.99) & (mt < 0.05) & (luz > 1)
    hh, e = np.histogram(luz[dentro], bins=128, range=(0, 256))
    topo = float(e[np.argmax(np.convolve(hh, np.ones(3) / 3, mode="same"))] + 1.0)
    sh = np.where(luz > 1, luz / max(topo, 1.0), 1.0)
    x0, y0, x1, y1 = q["peca"]
    miolo = V.cob([V.ret(x0 + 1.2, y0 + 1.2, x1 - 1.2, y1 - 1.2)], jan, s, origem)
    sh = 1.0 + (sh - 1.0) * miolo                   # a beira da foto (o chanfro escuro) fica de fora
    TT = D.piso_tt(jan, s, giro=True)
    pedra = TT * (q["escurecer"] * sh)[..., None]
    out = V.compor(reg, ap, pedra)
    # a torneira da biblioteca (as cores da foto, onde é metal)
    out = V.compor(out, mt * ap, cor_r)
    # a beira da peça um tom abaixo (como as outras peças da bancada)
    e_ = 0.25
    borda = np.clip(ap - V.cob([V.ret(x0 + e_, y0 + e_, x1 - e_, y1 - e_)], jan, s, origem), 0, 1)
    out = out * (1 - q["borda"] * borda)[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


ITENS = {"banho_varanda": (1605.0, 1450.0, 1710.0, 1640.0),
         "varanda": (1590.0, 345.0, 1875.0, 570.0),
         "lavabo_cuba": (2295.0, 400.0, 2350.0, 525.0)}
FUNC = {"banho_varanda": banho_varanda, "varanda": varanda, "lavabo_cuba": lavabo_cuba}


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
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            x0, y0, x1, y1 = ITENS[nome]
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

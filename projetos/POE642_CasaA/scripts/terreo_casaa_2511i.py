"""Casa A Térreo, 9ª leva de 25/11: as almofadas das poltronas da sala de estar e o tracejado da borda do tapete do
jantar ("sim, limpe as almofadas e tire o tracejado do tapete").

- **Almofadas**: nas quatro poltronas de couro caramelo da sala de estar, cada almofada tinha uma mancha creme (mais
  amarelada que o linho) com um fiapo cinza dentro, o resto de um traço apagado. O miolo de cada poltrona (almofadas
  e assento) de novo da peça da biblioteca, na pose da instalação, com o ajuste fino do deslocamento pela imagem; o
  couro e a sombra ficam. Os quadradinhos junto às poltronas e o resto claro à esquerda do trançado da poltrona de
  cima da varanda saem (o que destoa do entorno, refeito pelo entorno).
- **Tapete do jantar**: logo abaixo da borda reta de baixo do tapete redondo (e dos dois lados inclinados vizinhos),
  uma linha cinza (o contorno do tapete no PDF); a faixa de piso logo abaixo da borda refeita com o travertino de logo
  abaixo (deslocado), a borda do tapete fica.

Final, prancha e 12K A e B.

  python3 terreo_casaa_2511i.py [item ...]
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

PLANTA = "A_Terreo"
POLTRONAS = [(1925.0, 668.0, 1995.0, 738.0), (2040.0, 668.0, 2110.0, 738.0),
             (1925.0, 760.0, 1995.0, 830.0), (2040.0, 760.0, 2110.0, 830.0)]
PX_M_ = 59.70590031258779
MIOLO = dict(janela=34.0, desl_max=2.5, recuo=0.9, pena=0.35)
VARANDA_RESTO = (1689.5, 698.0, 1695.0, 712.5)   # à esquerda do trançado, na sombra
# os quadradinhos (restos de texto, o miolo cinza com o contorno claro) junto às poltronas da sala de estar
RESTOS_ESTAR = [(1970.5, 717.5, 1976.5, 723.5), (2056.0, 711.5, 2061.5, 721.5), (1949.5, 823.2, 1966.0, 828.5),
                (1961.5, 811.0, 1967.0, 815.5)]
# a borda de baixo do tapete do jantar (os três lados do polígono do PDF) e a faixa logo abaixo
TAPETE_BORDA = dict(lados=[((2019.9, 620.7), (2030.5, 621.6)), ((2030.5, 621.6), (2041.3, 621.6)),
                           ((2041.3, 621.6), (2051.9, 620.7))],
                    x0=2018.0, x1=2054.0, alt=1.25, dy=1.6, pena=1.5)


def _b1211():
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        import biblioteca_terreo_casaa_1211 as B
    return B


def _pecas_estar():
    """As quatro poltronas na ordem de POLTRONAS."""
    B = _b1211()
    g = B.girar_pt
    n = "sala-de-estar/poltrona-caramelo-render-v2"
    return B, [(n, 1958.1, 702.9, 52, None, g(0.71, 0.71)), (n, 2076.35, 702.65, 52, None, g(-0.71, 0.71)),
               (n, 1958.95, 796.05, 52, None, g(0.71, -0.71)), (n, 2075.25, 796.2, 52, None, g(-0.71, -0.71))]


def poltrona_limpa(img, s, origem, peca, q=MIOLO):
    """O miolo (almofadas e assento) da poltrona da biblioteca de novo, no lugar da instalação (`biblioteca_terreo_
    casaa_1211`), com o ajuste fino do deslocamento pela imagem; o couro em volta e a sombra ficam."""
    B, _ = _pecas_estar()
    nome, cx, cy, w, h, ang = peca
    m = q["janela"]
    jan = V.janela(img, (cx - m, cy - m, cx + m, cy + m), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    P, wt, ht = B.preparar(nome, w, h)
    can = np.zeros((H, W, 3), np.float32)
    B.pousar(can, P, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, wt * s, ht * s, ang, [], PX_M_ * s)
    Pa = P.copy()
    Pa[..., :3] = 255
    al = np.zeros((H, W, 3), np.float32)
    B.pousar(al, Pa, (cx - origem[0]) * s - X0, (cy - origem[1]) * s - Y0, wt * s, ht * s, ang, [], PX_M_ * s)
    alfa = al[..., 0] / 255.0
    # o ajuste fino: a correlação de fase entre a peça nova e a imagem, só dentro da peça
    g0 = cv2.cvtColor(np.clip(reg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) * alfa
    g1 = cv2.cvtColor(np.clip(can, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) * alfa
    jn = cv2.createHanningWindow((W, H), cv2.CV_32F)
    (dx, dy), _ = cv2.phaseCorrelate(g1 * jn, g0 * jn)
    if abs(dx) > q["desl_max"] * s or abs(dy) > q["desl_max"] * s:
        dx = dy = 0.0
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    can = cv2.warpAffine(can, M, (W, H), flags=cv2.INTER_LINEAR)
    alfa = cv2.warpAffine(alfa, M, (W, H), flags=cv2.INTER_LINEAR)
    # só o miolo: o tecido (não o couro caramelo) da peça nova, recuado da borda do couro
    Bc, Rc = can[..., 0], can[..., 2]
    tecido = (alfa > 0.98) & ((Rc - Bc) < 45)
    k = max(1, int(round(q["recuo"] * s)))
    couro = cv2.dilate(((alfa > 0.5) & ~tecido).astype(np.uint8), np.ones((2 * k + 1,) * 2, np.uint8)).astype(bool)
    miolo = (tecido & ~couro).astype(np.float32)
    miolo = cv2.GaussianBlur(miolo, (0, 0), max(0.5, q["pena"] * s)) * tecido
    novo = can / np.maximum(alfa, 1e-3)[..., None]
    out = reg * (1 - miolo[..., None]) + novo * miolo[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img, (dx / s, dy / s)


def almofadas(img, s, origem):
    _, pecas = _pecas_estar()
    for p in pecas:
        img, _ = poltrona_limpa(img, s, origem, p)
    return img


def restos_estar(img, s, origem, rets=RESTOS_ESTAR, dif=10.0, viz=9.0, passadas=3):
    """Nos retângulos, o que destoa do entorno (mais claro ou mais escuro que a mediana de perto), menos o couro e o
    trançado, refeito pelo entorno (inpaint), em três passadas (as seguintes pegam as sobras); o couro e o trançado não
    entram no preenchimento (no lugar deles, só para o inpaint, o tom do piso em volta)."""
    for r in rets:
        jan = V.janela(img, r, s, origem, folga=int(6 * s) + 2)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1].copy()
        dentro = V.cob([V.ret(*r)], jan, s, origem) > 0.5
        kk = max(1, int(round(0.5 * s)))
        k2 = max(1, int(round(0.8 * s)))
        for _ in range(passadas):
            f = reg.astype(np.float32)
            L = f.mean(2)
            rb = f[..., 2] - f[..., 0]
            k = max(5, int(round(viz * s)) | 1)
            dev = np.abs(L - _mediana(L, k))
            peca = (rb > 45) | ((rb > 22) & (L < 160))            # o couro caramelo e o trançado (a sombra fica)
            peca_d = cv2.dilate(peca.astype(np.uint8), np.ones((2 * kk + 1,) * 2, np.uint8)).astype(bool)
            m = ((dev > dif) & dentro & ~peca).astype(np.uint8)
            m = cv2.dilate(m, np.ones((2 * k2 + 1,) * 2, np.uint8)) & (dentro & ~peca).astype(np.uint8)
            if not m.any():
                break
            tmp = reg.copy()
            livre = (~peca_d & (m == 0)).astype(np.float32)
            sg = max(1.0, 1.5 * s)                              # o tom do piso de perto (a sombra junto à peça)
            num = cv2.GaussianBlur(reg.astype(np.float32) * livre[..., None], (0, 0), sg)
            den = cv2.GaussianBlur(livre, (0, 0), sg)[..., None]
            perto = np.clip(num / np.maximum(den, 1e-3), 0, 255).astype(np.uint8)
            troca = peca_d & (m == 0)
            tmp[troca] = perto[troca]
            novo = cv2.inpaint(tmp, m * 255, max(1.5, 1.2 * s), cv2.INPAINT_TELEA)
            reg[m > 0] = novo[m > 0]
        img[Y0:Y1, X0:X1] = reg
    return img


def _mediana(x, k):
    return cv2.medianBlur(np.ascontiguousarray(np.clip(x, 0, 255).astype(np.uint8)), k).astype(np.float32)


def poltrona_varanda(img, s, origem):
    return restos_estar(img, s, origem, [VARANDA_RESTO])


def tapete_borda(img, s, origem, q=TAPETE_BORDA):
    jan = V.janela(img, (q["x0"], 618.0, q["x1"], 627.0), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    yb = np.full(xs.shape, np.nan, np.float32)
    for (ax, ay), (bx, by) in q["lados"]:
        sel = (xs >= ax) & (xs <= bx)
        yb[sel] = ay + (by - ay) * (xs[sel] - ax) / (bx - ax)
    yb = np.where(np.isnan(yb), np.interp(xs, [q["x0"], q["x1"]], [620.5, 620.5]), yb)
    dyb = ys[:, None] - yb[None, :]
    a = np.clip(dyb / 0.25, 0, 1) * np.clip((q["alt"] - dyb) / 0.3, 0, 1)
    fx = np.clip((xs - q["x0"]) / q["pena"], 0, 1) * np.clip((q["x1"] - xs) / q["pena"], 0, 1)
    a = a * fx[None, :]
    d = int(round(q["dy"] * s))
    fonte = np.roll(reg, -d, axis=0)
    out = reg * (1 - a[..., None]) + fonte * a[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


ITENS = {f"almofadas_{k + 1}": c for k, c in enumerate(POLTRONAS)}
ITENS.update({"restos_estar": (1945.0, 705.0, 2070.0, 830.0),
              "poltrona_varanda": (1680.0, 690.0, 1705.0, 720.0),
         "tapete_borda": (2010.0, 612.0, 2062.0, 630.0)})
FUNC = {"poltrona_varanda": poltrona_varanda, "tapete_borda": tapete_borda, "restos_estar": restos_estar}
for _k in range(len(POLTRONAS)):                   # uma poltrona por item (o registro do 12K local)
    FUNC[f"almofadas_{_k + 1}"] = (lambda k: lambda img, s, origem: poltrona_limpa(img, s, origem,
                                                                                   _pecas_estar()[1][k])[0])(_k)


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

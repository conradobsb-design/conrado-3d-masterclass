"""Casa C Subsolo, 4ª leva de 26/11: a jardineira entre a escada SOBE PARA O JARDIM e a sauna.

Usuário (sobre o recorte do 12K B da jardineira): "melhorar a representação dessas bordas e manter um único material" e
"melhorar a representação de plantas em uma escala menor, colocar plantas em distâncias iguais".

Antes: a borda de cima era de travertino (com veios) e as outras três de pedra clara granulada, com fios marrons e
cinzas na beira de dentro; dentro, um maciço de folhas grandes, sem ritmo.

Agora, na caixa do PDF (ARQ_PAISAGISMO, 664,2 a 694,0 x 737,1 a 978,9, borda de 6 px; o lado da sauna até 695,0, onde
a parede está na imagem):
- **a borda** inteira numa pedra só, a pedra clara dos lados (a cor mediana dela, do lado esquerdo, de 760 a 960, com
  grão fino e manchas largas bem leves, geradas), sem os fios; a beira de fora com um traço fino um tom abaixo (para
  separar do piso claro) e a de dentro reta;
- **o plantio**: terra escura (gerada, com grão fino e manchas largas), mais escura junto à borda (a sombra da pedra), e
  os arbustos densos da biblioteca (`arbusto-verde-denso`, da Casa D), na escala dos degraus ("estamos aplicando a escala
  correta da vegetação de plantas, levando em consideração os degraus como referência?"): a jardineira acompanha os 8
  degraus de 0,50 m (30 px) e leva uma planta no meio de cada degrau, a distâncias iguais (0,50 m), de 15 px (0,25 m,
  meio degrau, dentro dos 0,30 m da jardineira), cada uma girada, com a sombra curta para baixo e à esquerda.

E o tracejado claro no alto do 1º degrau, junto ao canto da jardineira ("remova esse tracejado claro"): a faixa clara
com traços marrons (de 634 a 663,6, 738 a 740) vira o próprio degrau de logo abaixo.

Final, prancha e 12K A e B (pelo registro local).

  python3 subsolo_casac_2611d.py [item ...]
"""
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
import um_pav_casaa_2511d as DD      # noqa: E402
import subsolo_casac_2611 as A       # noqa: E402

PLANTA = A.PLANTA
DZ = A.DZ
JARD = dict(fora=(664.2, 737.1, 695.0, 978.9), dentro=(670.2, 743.0, 688.1, 972.9),
            fonte=(665.4, 760.0, 669.0, 960.0),               # a pedra clara do lado esquerdo, sem as beiras
            traco=0.55, traco_tom=0.88,                       # a beira de fora: um traço fino um tom abaixo
            terra=(44.0, 56.0, 70.0), sombra=0.42, sombra_l=1.3,
            planta="POE642_CasaD/biblioteca-objetos/02-terreo/jardins-e-floreiras/arbusto-verde-denso.png",
            # uma planta por degrau, no meio de cada um (os 8 degraus ao lado da jardineira, bordas em 738, 768, 798, 828,
            # 858, 888, 919, 949 e 979: degraus de 30 px, 0,50 m), de 15 px (0,25 m, meio degrau)
            centros=(753.0, 783.0, 813.0, 843.0, 873.0, 903.5, 934.0, 964.0), diam=15.0, sombra_p=0.30)



def _pedra(reg, jan, s, origem, q, semente=5):
    """A borda: a pedra clara, uma só, na cor mediana da pedra dos lados de antes (a fonte), com grão fino e manchas
    largas bem leves (geradas: sem a repetição nem o espelho de um recorte)."""
    xs, ys = V.coords(jan, s, origem)
    fx0, fy0, fx1, fy1 = q["fonte"]
    cx = np.where((xs >= fx0) & (xs <= fx1))[0]
    cy = np.where((ys >= fy0) & (ys <= fy1))[0]
    cor = np.median(reg[cy.min():cy.max() + 1, cx.min():cx.max() + 1].reshape(-1, 3), axis=0)
    H, W = reg.shape[:2]
    rng = np.random.default_rng(semente)
    fino = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), max(0.3 * s, 0.4))
    medio = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), max(0.9 * s, 0.7))
    largo = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), max(3.0 * s, 1.5))
    fino /= max(fino.std(), 1e-6)
    medio /= max(medio.std(), 1e-6)
    largo /= max(largo.std(), 1e-6)
    return np.float32(cor)[None, None, :] * (1 + 0.022 * fino + 0.014 * medio + 0.012 * largo)[..., None]


def _terra(H, W, s, q, semente=7):
    rng = np.random.default_rng(semente)
    g = rng.normal(0, 1, (H, W)).astype(np.float32)
    fino = cv2.GaussianBlur(g, (0, 0), max(0.35 * s, 0.4))
    largo = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), max(1.6 * s, 1.0))
    fino /= max(fino.std(), 1e-6)
    largo /= max(largo.std(), 1e-6)
    base = np.float32(q["terra"])[None, None, :]
    return base * (1 + 0.10 * fino + 0.07 * largo)[..., None]


def _colar(reg, jan, s, origem, T, diam_png, diam, cx, cy, giro, sombra):
    X0, Y0, X1, Y1 = jan
    H, W = reg.shape[:2]
    a = T[..., 3] / 255.0
    pre = np.dstack([T[..., :3] * a[..., None], a]).astype(np.float32)
    k = diam * s / diam_png
    if k < 1:
        pre = cv2.resize(pre, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        k = 1.0
    pc = ((pre.shape[1] - 1) / 2.0, (pre.shape[0] - 1) / 2.0)
    tx, ty = (cx - origem[0]) * s - 0.5 - X0, (cy - origem[1]) * s - 0.5 - Y0
    M = cv2.getRotationMatrix2D(pc, giro, k)
    M[0, 2] += tx - pc[0]
    M[1, 2] += ty - pc[1]
    w = cv2.warpAffine(pre, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    al = np.clip(w[..., 3], 0, 1)
    cor = w[..., :3] / np.maximum(al, 1e-4)[..., None]
    Ms = np.float32([[1, 0, -0.6 * s], [0, 1, 0.8 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(al, Ms, (W, H)), (0, 0), 0.7 * s) * (1 - al)
    reg = reg * (1 - sombra * sb)[..., None]
    return reg * (1 - al[..., None]) + cor * al[..., None]


def jardineira(img, s, origem, q=JARD):
    ox0, oy0, ox1, oy1 = q["fora"]
    ix0, iy0, ix1, iy1 = q["dentro"]
    jan = V.janela(img, (ox0 - 3, oy0 - 3, ox1 + 3, oy1 + 3), s, origem, folga=int(2 * s) + 2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    a_fora = V.cob([V.ret(*q["fora"])], jan, s, origem)
    a_dentro = V.cob([V.ret(*q["dentro"])], jan, s, origem)
    # a borda: uma pedra só, com a média de antes dos lados
    pedra = _pedra(reg, jan, s, origem, q)
    borda = np.clip(a_fora - a_dentro, 0, 1)
    # a beira de fora: um traço fino um tom abaixo
    t = q["traco"]
    a_in = V.cob([V.ret(ox0 + t, oy0 + t, ox1 - t, oy1 - t)], jan, s, origem)
    rim = np.clip(a_fora - a_in, 0, 1)
    pedra = pedra * (1 - (1 - q["traco_tom"]) * rim)[..., None]
    reg = reg * (1 - borda[..., None]) + pedra * borda[..., None]
    # o plantio: a terra, mais escura junto à borda
    terra = _terra(H, W, s, q)
    d = np.minimum.reduce([X - ix0, ix1 - X, Y - iy0, iy1 - Y])
    terra = terra * (1 - q["sombra"] * np.exp(-np.maximum(d, 0) / q["sombra_l"]))[..., None]
    reg = reg * (1 - a_dentro[..., None]) + terra * a_dentro[..., None]
    # os arbustos, a distâncias iguais no eixo
    T = cv2.imread(str(EP.PROJ / q["planta"]), cv2.IMREAD_UNCHANGED)
    al = T[..., 3] > 20
    yy, xx = np.where(al)
    diam_png = float(max(xx.max() - xx.min(), yy.max() - yy.min()))
    cyT, cxT = (yy.min() + yy.max()) / 2.0, (xx.min() + xx.max()) / 2.0
    # o recorte centrado na planta (o giro em torno do centro dela)
    m = int(max(T.shape[:2]))
    Tc = np.zeros((m, m, 4), np.uint8)
    oy, ox = int(round(m / 2 - cyT)), int(round(m / 2 - cxT))
    y0s, x0s = max(0, -oy), max(0, -ox)
    y1s, x1s = min(T.shape[0], m - oy), min(T.shape[1], m - ox)
    Tc[y0s + oy:y1s + oy, x0s + ox:x1s + ox] = T[y0s:y1s, x0s:x1s]
    rng = np.random.default_rng(11)
    giros = rng.uniform(0, 360, len(q["centros"]))
    cx = (ix0 + ix1) / 2
    for i, cy in enumerate(q["centros"]):
        reg = _colar(reg, jan, s, origem, Tc.astype(np.float32), diam_png, q["diam"], cx, cy, giros[i], q["sombra_p"])
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# o tracejado claro no alto do 1º degrau, de 634 a 663,6 (o trecho embaixo do travertino, até a jardineira): o próprio
# degrau de logo abaixo ("remova esse tracejado claro")
TRACEJADO = ((633.4, 737.95, 664.2, 740.3), (0.0, 2.6), "lb")


def tracejado_degrau(img, s, origem, q=TRACEJADO):
    r, d, lados = q
    return A.copiar(img, s, origem, r, d, lados, pena=0.8)


FUNC = {"jardineira": jardineira, "tracejado_degrau": tracejado_degrau}
ITENS = {"jardineira": (650.0, 725.0, 710.0, 990.0), "tracejado_degrau": (600.0, 715.0, 690.0, 765.0)}


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

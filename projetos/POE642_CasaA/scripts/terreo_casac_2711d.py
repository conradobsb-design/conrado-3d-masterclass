"""Casa C Térreo, 27/11 (4): a manta fina da referência do usuário, atravessada nos pés da cama e caindo dos dois lados.

O usuário mandou uma foto ("a manta pode ser assim"): uma manta fina de tecido, em taupe/greige, jogada atravessada
nos pés da cama, com as pregas soltas, caindo pelas laterais. No lugar da manta de tricô grosso de
`terreo_casac_2711c`, nas três camas (suíte master, quarto 3 e quarto 1):

- as camas voltam ao estado de antes da manta de tricô (o commit 2007d2c, com o corte de `terreo_casac_2711` desfeito
  pelos pixels de a93c155, como em `terreo_casac_2711c`);
- entra a manta fina gerada no Higgsfield em 4K a partir da foto, sem fundo
  (`../biblioteca-objetos/03-primeiro-pavimento/mantas/manta-fina-taupe.png`): uma faixa de lado a lado sobre os pés,
  um pouco torta, passando da beira dos dois lados da cama; a parte que cai fica mais escura, com a dobra clara na beira
  do colchão e a sombra no piso. O que sobra da manta antiga fora da nova vira edredom ou tapete (quilting da própria
  cama e do tapete, no tom local), como em `terreo_casac_2711c`.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2711d.py
"""
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
import terreo_casaa_2511g as G                   # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402
import terreo_casac_2711c as C                   # noqa: E402

PLANTA = C.PLANTA
DZ = C.DZ
ANTES_DO_TRICO = "2007d2c"             # as camas antes da manta de tricô (com o corte de terreo_casac_2711)
JANELAS = {"suite_master": (880.0, 560.0, 1110.0, 760.0), "quarto3": (1280.0, 360.0, 1460.0, 520.0),
           "quarto1": (1990.0, 360.0, 2180.0, 540.0)}
MANTA_PNG = EP.PROJ / "POE642_CasaA/biblioteca-objetos/03-primeiro-pavimento/mantas/manta-fina-taupe.png"
# por cama: como em terreo_casac_2711c.CAMAS, com as duas beiras por onde a manta cai
CAMAS_NOVAS_RET = {"quarto2_a": (1449.6, 371.6, 1563.4, 430.0), "quarto2_b": (1449.6, 471.3, 1563.4, 530.0),
                   "servico": (2480.8, 604.5, 2593.6, 662.6), "externo": (3049.9, 752.5, 3160.6, 810.4)}
CAMAS = {
    "suite_master": dict(C.CAMAS["suite_master"], cama=(946.4, 588.6, 1066.6, 710.4),
                         beira=[("x", 946.4, -1), ("x", 1066.6, 1)], centro=(1006.0, 689.0), comp=138.0, giro=-3.0),
    "quarto3": dict(C.CAMAS["quarto3"], cama=(1315.2, 380.6, 1427.0, 484.4),
                    beira=[("y", 380.6, -1), ("y", 484.4, 1)], centro=(1332.0, 432.5), comp=118.0, giro=92.5),
    "quarto1": dict(C.CAMAS["quarto1"], cama=(2030.0, 404.4, 2155.0, 521.2),
                    beira=[("y", 404.4, -1), ("y", 521.2, 1)], centro=(2049.0, 462.8), comp=136.0, giro=-92.5),
}


def _manta_solteiro(ret, livres, cabeca):
    """A manta fina na cama de solteiro: atravessada perto dos pés, caindo pelos lados livres (os que não encostam na
    parede), um pouco torta."""
    x0, y0, x1, y1 = ret
    sobra = 7.5
    ini = y0 - (sobra if "cima" in livres else 0.0)
    fim = y1 + (sobra if "baixo" in livres else 0.0)
    cx = x1 - 22.0 if cabeca == "esq" else x0 + 22.0
    beira = [("y", y0, -1)] * ("cima" in livres) + [("y", y1, 1)] * ("baixo" in livres)
    return dict(cama=ret, velha=(0.0, 0.0, 0.0, 0.0), beira=beira, centro=(cx, (ini + fim) / 2), comp=fim - ini,
                giro=(92.0 if cabeca == "esq" else -92.0), edredom=(x0 + 30, y0 + 10, x1 - 30, y1 - 10),
                tapete=(x0 + 30, y0 + 10, x1 - 30, y1 - 10))


CAMAS.update({
    "quarto2_a": _manta_solteiro(CAMAS_NOVAS_RET["quarto2_a"], ("cima", "baixo"), "esq"),
    "quarto2_b": _manta_solteiro(CAMAS_NOVAS_RET["quarto2_b"], ("cima", "baixo"), "esq"),
    "servico": _manta_solteiro(CAMAS_NOVAS_RET["servico"], ("cima",), "esq"),       # embaixo, a parede
    "externo": _manta_solteiro(CAMAS_NOVAS_RET["externo"], ("cima",), "dir"),       # embaixo, a parede
})
# a sombra fina da beira da cama onde a manta velha a cobria; o caimento encurtado (a parte de fora da beira a 35%);
# o tom discreto (greige claro, perto do edredom) com as pregas mais suaves; a parte que cai um pouco mais escura
CAI = dict(borda_cama=0.16, so_fora=True, encurta=0.35, tom_alvo=(168.0, 181.0, 196.0), contraste=0.72, escurece=0.26, cai_px=2.2,
           sombra=0.30)


# a cama nova (Higgsfield 4K, sem fundo, a cabeceira para cima no PNG): por cama, o retângulo da roupa de cama (da
# cabeceira aos pés), o lado da cabeceira, o tom da roupa de cama (multiplica; None = o do PNG) e o tom das almofadas
# da frente (None = o greige do PNG); as variações de tom por quarto são as de 13/11 (camas_casac_1311)
CAMA_PNG = {k: EP.PROJ / f"POE642_CasaA/biblioteca-objetos/03-primeiro-pavimento/camas-novas/cama-nova-{k}.png"
            for k in ("king", "solteiro")}
RGB = lambda r, g, b: (float(b), float(g), float(r))
CAMAS_NOVAS = {
    "suite_master": dict(ret=(946.4, 588.6, 1066.6, 710.4), cabeca="cima", tom=None, almofada=None, base=True,
                         # a curva do edredom antigo à direita, sobre o tapete: o tapete de novo (amostra ao lado)
                         limpar=[((1065.0, 626.0, 1069.4, 660.0), "lrtb", (1069.6, 628.0, 1079.0, 676.0))]),
    "quarto3": dict(ret=(1315.2, 380.6, 1427.0, 484.4), cabeca="dir", tom=None, almofada=RGB(206, 184, 180), base=True),
    "quarto1": dict(ret=(2030.0, 404.4, 2155.0, 521.2), cabeca="dir", tom=RGB(238, 226, 208), almofada=RGB(196, 199, 182),
                    base=True),
    # as camas de solteiro no mesmo modelo (o usuário: "as outras camas de solteiro seguem o mesmo modelo da cama de casal")
    # quarto 2: a base da cama antiga sobrava embaixo (entre a cama e o criado): o piso de tábuas de novo
    "quarto2_a": dict(ret=(1449.6, 371.6, 1563.4, 430.0), cabeca="esq", tom=None, almofada=None, png="solteiro", base=True,
                      limpar=[((1444.2, 429.4, 1478.0, 433.3), "rb", (1480.0, 430.4, 1530.0, 437.6))]),
    "quarto2_b": dict(ret=(1449.6, 471.3, 1563.4, 530.0), cabeca="esq", tom=None, almofada=None, png="solteiro", base=True,
                      limpar=[((1444.2, 529.4, 1504.0, 534.2), "rb", (1506.0, 530.4, 1556.0, 537.6))]),
    "servico": dict(ret=(2480.8, 604.5, 2593.6, 662.6), cabeca="esq", tom=None, almofada=None, png="solteiro", base=True),
    "externo": dict(ret=(3049.9, 752.5, 3160.6, 810.4), cabeca="dir", tom=None, almofada=None, png="solteiro", base=True),
}
SOMBRA_CAMA = dict(d=(-0.6, 0.8), sig=1.0, forca=0.22)
# o colchão sob a roupa de cama das de casal (base=True): o retângulo inteiro, cantos arredondados, no branco do lençol;
# o PNG deixa vazios os cantos ao lado dos travesseiros e a beira macia do edredom, onde aparecia a cama antiga
BASE = dict(raio=2.6, borda=0.9, escurece=0.07)
_CAMA = {}


def _cama_png(tipo="king"):
    if tipo not in _CAMA:
        P = cv2.imread(str(CAMA_PNG[tipo]), cv2.IMREAD_UNCHANGED).astype(np.float32)
        ys, xs = np.nonzero(P[..., 3] > 8)
        _CAMA[tipo] = P[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return _CAMA[tipo]


# almofadas da frente do PNG king (cabeceira em cima): canto, meio do lado, canto... em sentido horário
ALMOFADAS_KING = (
    ((0.073, 0.127), (0.280, 0.146), (0.486, 0.129), (0.475, 0.214), (0.484, 0.299), (0.280, 0.288), (0.0825, 0.300), (0.094, 0.214)),
    ((0.514, 0.127), (0.718, 0.146), (0.922, 0.131), (0.900, 0.215), (0.909, 0.300), (0.712, 0.289), (0.514, 0.300), (0.525, 0.214)),
)


def _tingir(P, q):
    """O tom da roupa de cama (o branco multiplicado) e o das almofadas da frente (o greige do PNG levado ao tom)."""
    P = P.copy()
    rgb = P[..., :3]
    a = P[..., 3] > 127
    # o linho greige das almofadas da frente: o contorno das duas almofadas do PNG king (cantos e meio de cada lado,
    # em fração da largura e da altura), lados em curva; a cor sozinha pegava a sombra dos travesseiros brancos
    alm = np.zeros(a.shape, np.uint8)
    if q.get("png", "king") == "king":
        H, W = a.shape
        for pol in ALMOFADAS_KING:
            pts = []
            for i in range(4):
                A, M, B = np.float32(pol[2 * i]), np.float32(pol[2 * i + 1]), np.float32(pol[(2 * i + 2) % 8])
                Cq = 2 * M - (A + B) / 2
                for t in np.linspace(0, 1, 24, endpoint=False):
                    pts.append((1 - t) ** 2 * A + 2 * (1 - t) * t * Cq + t ** 2 * B)
            pts = np.round(np.float32(pts) * (W, H) * 8).astype(np.int32)
            cv2.fillPoly(alm, [pts], 1, lineType=cv2.LINE_AA, shift=3)
    alm = alm > 0
    if q["almofada"] is not None and alm.any():
        med = np.median(rgb[alm], axis=0)
        m = cv2.GaussianBlur(alm.astype(np.float32), (0, 0), 2.0)[..., None]
        rgb[:] = rgb * (1 - m) + rgb / np.maximum(med, 1) * np.float32(q["almofada"]) * m
    if q["tom"] is not None:
        branco = np.percentile(rgb[a & ~alm], 90, axis=0)
        m = 1 - cv2.GaussianBlur(alm.astype(np.float32), (0, 0), 2.0)[..., None]
        rgb[:] = rgb * (1 - m) + rgb / np.maximum(branco, 1) * np.float32(q["tom"]) * m
    P[..., :3] = np.clip(rgb, 0, 255)
    return P


def cama_nova(img, s, origem, nome, q=None):
    q = q or CAMAS_NOVAS[nome]
    r = q["ret"]
    for zona, lados, fonte in q.get("limpar", ()):
        img = G.refazer(img, s, origem, [(zona, lados)], textura=("quilt", fonte), tol=0.06, luz_sig=6.0, pena=1.2)
    jan = V.janela(img, (r[0] - 6, r[1] - 6, r[2] + 6, r[3] + 6), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    P = _tingir(_cama_png(q.get("png", "king")), q)
    hh, ww = P.shape[:2]
    faixa = P[int(0.36 * hh):int(0.40 * hh), int(0.2 * ww):int(0.8 * ww)]     # a dobra do lençol, sob os travesseiros
    lencol = np.median(faixa[faixa[..., 3] > 240][:, :3], axis=0)
    if q["cabeca"] == "dir":
        P = np.ascontiguousarray(np.rot90(P, k=-1))     # a cabeceira (o alto do PNG) para a direita
    elif q["cabeca"] == "esq":
        P = np.ascontiguousarray(np.rot90(P, k=1))      # a cabeceira para a esquerda
    w, h = (r[2] - r[0]) * s, (r[3] - r[1]) * s
    k = 3                                              # supersampling da borda
    Pr = cv2.resize(P, (max(2, int(round(w * k))), max(2, int(round(h * k)))), interpolation=cv2.INTER_AREA)
    Pr[..., :3] *= Pr[..., 3:4] / 255
    M = np.float32([[1, 0, ((r[0] - origem[0]) * s - X0) * k], [0, 1, ((r[1] - origem[1]) * s - Y0) * k]])
    can = cv2.warpAffine(Pr, M, (W * k, H * k), flags=cv2.INTER_LINEAR, borderValue=0)
    can = cv2.resize(can, (W, H), interpolation=cv2.INTER_AREA)
    cor, a = can[..., :3], np.clip(can[..., 3] / 255, 0, 1)
    if q.get("base"):
        xs, ys = V.coords(jan, s, origem)
        X, Y = np.meshgrid(xs, ys)
        rr = BASE["raio"]
        ddx = np.maximum(np.maximum(r[0] + rr - X, X - (r[2] - rr)), 0)
        ddy = np.maximum(np.maximum(r[1] + rr - Y, Y - (r[3] - rr)), 0)
        dentro = rr - np.hypot(ddx, ddy)                                   # unidades para dentro da borda
        b = np.clip(dentro * s + 0.5, 0, 1).astype(np.float32)
        tom = lencol[None, None] * (1 - BASE["escurece"] * np.clip(1 - dentro / BASE["borda"], 0, 1))[..., None]
        cor = cor + tom * ((1 - a) * b)[..., None]
        a = a + (1 - a) * b
    dx, dy = SOMBRA_CAMA["d"]
    Ms = np.float32([[1, 0, dx * s], [0, 1, dy * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, Ms, (W, H)), (0, 0), SOMBRA_CAMA["sig"] * s) * (1 - a)
    reg = reg * (1 - SOMBRA_CAMA["forca"] * sb)[..., None]
    reg = reg * (1 - a[..., None]) + cor
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def preparar(img, antigo, antigo0, s, origem, nome):
    """A cama como antes da manta de tricô: a janela da cama de ANTES_DO_TRICO e, nela, o corte desfeito."""
    X0, Y0, X1, Y1 = V.janela(img, JANELAS[nome], s, origem, folga=0)
    img[Y0:Y1, X0:X1] = antigo[Y0:Y1, X0:X1]
    return C.restaurar(img, antigo0, s, origem, {nome: C.CORTE[nome]})


def manta(img, s, origem, nome):
    C.MANTA_PNG = MANTA_PNG
    C._ASSET.clear()
    camas, cai = C.CAMAS, dict(C.CAI)
    C.CAMAS = CAMAS
    C.CAI.update(CAI)
    try:
        return C.manta(img, s, origem, nome)
    finally:
        C.CAMAS = camas
        C.CAI.clear()
        C.CAI.update(cai)
        C._ASSET.clear()


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        a1, a0 = C._git_img(f, ANTES_DO_TRICO), C._git_img(f)
        for nome in CAMAS_NOVAS:
            if nome in JANELAS:
                im = preparar(im, a1, a0, 1.0, (0.0, 0.0), nome)
            im = cama_nova(im, 1.0, (0.0, 0.0), nome)
            im = manta(im, 1.0, (0.0, 0.0), nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    for op in os.environ.get("OPCOES", "AB"):
        rel = f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(EP.PROJ / rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        a1, a0 = C._git_img(rel, ANTES_DO_TRICO), C._git_img(rel)
        for nome in CAMAS_NOVAS:
            r = CAMAS_NOVAS[nome]["ret"]
            j = JANELAS.get(nome, (r[0] - 40, r[1] - 40, r[2] + 40, r[3] + 40))
            sx, org, cc = DD._registro(base, cinza, DZ, j)
            if nome in JANELAS:
                im = preparar(im, a1, a0, sx, org, nome)
            im = cama_nova(im, sx, org, nome)
            im = manta(im, sx, org, nome)
            print(f"   {op}: cama nova + manta fina {nome} (registro {cc:.3f}, escala {sx:.3f})")
        del a1, a0
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(EP.PROJ / rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

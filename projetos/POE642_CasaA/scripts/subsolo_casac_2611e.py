"""Casa C Subsolo, 5ª leva de 26/11: a bancada e a cuba do BH academia.

Usuário (sobre o recorte do 12K B): "corrija cuba e bancada". Antes: o granito do motor antigo, com os salpicos brancos
numa grade (fileiras e colunas), um fio cinza por fora na beira da frente e na de baixo, e a cuba esculpida como um
caixote, com uma régua clara à direita e a torneira num bloco cinza.

O material fica o granito marrom aprovado na auditoria de 26/10, agora o da referência do usuário
(`fontes_procedurais.granito_referencia`: a base marrom com nuvens e lascas de 2 a 55 mm, na escala de cada imagem):
- **a bancada** no retângulo do PDF (947,6 a 980,0 x 746,0 a 876,9: até a face da parede como está na imagem), a beira
  da frente e a de baixo (a testeira do PDF) um tom abaixo, a sombra curta no piso; o fio cinza de fora vira o piso de
  logo ao lado (nas linhas da folha da porta, o de logo abaixo);
- **a cuba esculpida** no granito, no retângulo de baixo do PDF (a aba 950,8 a 977,1 x 793,1 a 831,2, polida, um pouco
  mais clara; a bacia 952,0 a 975,9 x 794,3 a 830,0, de cantos arredondados, mais funda, com a sombra por dentro junto
  às bordas de cima e da direita e o contorno fino), a válvula cromada no meio;
- **a torneira** cromada saindo da parede (a base redonda e o bico até o meio da bacia), com o brilho e a sombra curta.

Final, prancha e 12K A e B (pelo registro local).

  python3 subsolo_casac_2611e.py
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
import fontes_procedurais as FP      # noqa: E402
import subsolo_casac_2611 as A       # noqa: E402

PLANTA = A.PLANTA
DZ = A.DZ
PX_M = 60.0
CROMO = {"escuro": (122, 126, 130), "meio": (190, 193, 196), "claro": (238, 240, 242), "contorno": (88, 92, 96)}
BANC = dict(ret=(947.6, 746.0, 980.0, 876.9), testeira=1.2, testeira_tom=0.86, sombra=0.28,
            fio=[((945.6, 746.0, 947.6, 751.0), (-3.4, 0.0), "l"), ((945.6, 757.5, 947.6, 878.9), (-3.4, 0.0), "l"),
                 ((945.6, 751.0, 947.6, 757.5), (0.0, 7.0), "l"), ((945.6, 876.9, 980.0, 878.9), (0.0, 2.6), "b")],
            aba=(950.8, 793.1, 977.1, 831.2), aba_tom=1.07,
            bacia=(952.0, 794.3, 975.9, 830.0), bacia_r=2.2, bacia_tom=0.80, bacia_sombra=(0.38, 2.4),
            bacia_contorno=(34.0, 44.0, 58.0), bacia_contorno_l=0.35,
            valvula=1.1, torneira_base=(978.4, 812.15, 1.35), torneira_bico=(969.0, 811.45, 978.4, 812.85))


def _arred(x0, y0, x1, y1, r, n=10):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for a in np.linspace(a0, a0 + 90, n):
            pts.append((cx + r * np.cos(np.radians(a)), cy + r * np.sin(np.radians(a))))
    return pts


def _disco(cx, cy, r, n=48):
    return [(cx + r * np.cos(t), cy + r * np.sin(t)) for t in np.linspace(0, 2 * np.pi, n, endpoint=False)]


def _sombra(reg, a, s, forca, dx=-0.6, dy=0.8, sig=0.7):
    H, W = a.shape
    Ms = np.float32([[1, 0, dx * s], [0, 1, dy * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, Ms, (W, H)), (0, 0), max(sig * s, 0.5)) * (1 - a)
    return reg * (1 - forca * sb)[..., None]


def bancada_bh(img, s, origem, q=BANC):
    for r, d, lados in q["fio"]:
        img = A.copiar(img, s, origem, r, d, lados, pena=0.6)
    x0, y0, x1, y1 = q["ret"]
    jan = V.janela(img, (x0 - 4, y0 - 1, x1 + 1, y1 + 4), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    G = FP.granito_referencia(H, W, PX_M * s, semente=642).astype(np.float32)
    # a bancada, com a sombra curta no piso e a testeira (a beira da frente e a de baixo) um tom abaixo
    a = V.cob([V.ret(*q["ret"])], jan, s, origem)
    reg = _sombra(reg, a, s, q["sombra"])
    t = q["testeira"]
    a_in = V.cob([V.ret(x0 + t, y0, x1, y1 - t)], jan, s, origem)
    testeira = np.clip(a - a_in, 0, 1)
    pedra = G * (1 - (1 - q["testeira_tom"]) * testeira)[..., None]
    reg = reg * (1 - a[..., None]) + pedra * a[..., None]
    # a cuba esculpida: a aba polida, a bacia mais funda com a sombra por dentro (no alto e à direita) e o contorno fino
    a_aba = V.cob([V.ret(*q["aba"])], jan, s, origem)
    bx0, by0, bx1, by1 = q["bacia"]
    a_bac = V.cob([_arred(bx0, by0, bx1, by1, q["bacia_r"])], jan, s, origem)
    reg = reg * (1 - (a_aba * (1 - a_bac))[..., None]) + (G * q["aba_tom"]) * (a_aba * (1 - a_bac))[..., None]
    d = np.minimum.reduce([X - bx0, bx1 - X, Y - by0, by1 - Y])
    lado = np.clip(((X - bx0) / (bx1 - bx0) + (by1 - Y) / (by1 - by0)) / 2, 0, 1)
    f, alc = q["bacia_sombra"]
    prof = 1 - f * np.clip(1 - np.maximum(d, 0) / alc, 0, 1) * (0.45 + 0.55 * lado)
    bacia = G * q["bacia_tom"] * prof[..., None]
    reg = reg * (1 - a_bac[..., None]) + bacia * a_bac[..., None]
    lc = q["bacia_contorno_l"]
    a_bin = V.cob([_arred(bx0 + lc, by0 + lc, bx1 - lc, by1 - lc, max(q["bacia_r"] - lc, 0.5))], jan, s, origem)
    contorno = np.clip(a_bac - a_bin, 0, 1) * 0.75
    reg = V.compor(reg, contorno, q["bacia_contorno"])
    # a válvula
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    a_v = V.cob([_disco(cx, cy, q["valvula"])], jan, s, origem)
    a_vi = V.cob([_disco(cx, cy, q["valvula"] - 0.3)], jan, s, origem)
    reg = V.compor(reg, a_v, CROMO["contorno"])
    reg = V.compor(reg, a_vi, CROMO["meio"])
    # a torneira: o bico e a base redonda na parede, com a sombra curta e o brilho
    tb = q["torneira_bico"]
    a_b = V.cob([_arred(*tb, 0.6)], jan, s, origem)
    bx, by, br = q["torneira_base"]
    a_base = V.cob([_disco(bx, by, br)], jan, s, origem)
    a_t = np.clip(a_b + a_base, 0, 1)
    reg = _sombra(reg, a_t, s, 0.32, dx=-0.5, dy=0.6, sig=0.5)
    reg = V.compor(reg, a_t, CROMO["contorno"])
    a_b_in = V.cob([_arred(tb[0] + 0.25, tb[1] + 0.25, tb[2], tb[3] - 0.25, 0.4)], jan, s, origem)
    reg = V.compor(reg, a_b_in, CROMO["escuro"])
    a_brilho = V.cob([V.ret(tb[0] + 0.6, tb[1] + 0.3, tb[2] - 0.3, (tb[1] + tb[3]) / 2)], jan, s, origem)
    reg = V.compor(reg, a_brilho * 0.9, CROMO["claro"])
    a_base_in = V.cob([_disco(bx, by, br - 0.3)], jan, s, origem)
    reg = V.compor(reg, a_base_in, CROMO["meio"])
    a_hl = V.cob([_disco(bx + 0.3 * br, by - 0.3 * br, 0.45 * br)], jan, s, origem)
    reg = V.compor(reg, a_hl * 0.8, CROMO["claro"])
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"bancada_bh": bancada_bh}
ITENS = {"bancada_bh": (930.0, 740.0, 995.0, 890.0)}


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

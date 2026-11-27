"""Casa C Térreo, 27/11 (6): os pedidos antigos que a conferência item a item achou abertos no 12K B.

A conferência dos 127 pedidos da Casa C Térreo (lista mestra, conversa inteira) no último 12K B entregue achou
itens não feitos e pela metade; cada função abaixo é um deles, com o número do item da lista:

- **lote_esq, lote_dir, lote_topo** (item 23, "REMOVA ESSE TRACEJADO EM VOLTA DA PLANTA"): os traços cinza-azulados da divisa do lote na
  borda esquerda (toda a altura), na borda direita (sobre o pisante grande) e os tiquinhos escuros acima do muro de
  cima saem; fica o fundo (a sombra suave da planta) e a beira da grama reta.
- **porta_lavabo** (item 74, "porta do lavabo é no tom escuro de ponta a ponta", 14/11): a folha tinha voltado a ser
  só o contorno preto com o miolo claro; o miolo volta ao tom escuro do contorno, de ponta a ponta.
- **pivotante** (item 21, "MANTENHA O MESMO MATERIAL PARA PORTA DE FORA A FORA", 13/11): a folha pivotante do hall
  tinha dois miolos (travertino até x 2706, vidro cinza-azulado depois); agora é o vidro cinza-azulado de ponta a ponta.
- **claraboia_bhm1** e **claraboia_box2** (itens 3, 19 e 45, "FICOU FALTANDO A DELIMITAÇÃO DAS CLARABOIAS CONFORME
  ORIENTAÇÃO" e "CORRIJA O INTERIOR DESSE BOX. APENAS O TRACEJADO DA CLARABOIA E O RESTANTE PISO"): os restos escuros do
  tracejado antigo junto às paredes e a linha velha voltam a ser piso (quilting do próprio piso, no tom em volta), a
  face das paredes fica limpa e o retângulo da claraboia é tracejado de novo, em cinza fino, nos quatro lados (menos
  sobre a bacia e o vidro do box). No box do BH master 2 o miolo inteiro fica num piso só.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2711f.py [itens]
"""
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP              # noqa: E402
import vetor_2511 as V                           # noqa: E402
import terreo_casaa_2511g as G                   # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
BRANCO = (255.0, 255.0, 255.0)


def _reg(img, s, o, r, folga=3):
    jan = V.janela(img, r, s, o, folga=folga)
    X0, Y0, X1, Y1 = jan
    return jan, img[Y0:Y1, X0:X1].astype(np.float32)


def _por(img, jan, reg):
    X0, Y0, X1, Y1 = jan
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def _tracejado(reg):
    """Os px do tracejado da divisa: claros a médios, sem a cor da grama (verde) nem a do pisante (bege)."""
    b, g, r = reg[..., 0], reg[..., 1], reg[..., 2]
    L = reg.mean(2)
    grama = (g > b + 10) & (L < 190)
    bege = (r - b) > 16
    return (L > 105) & (L < 248) & ~grama & ~bege


# a divisa do lote: as faixas da borda esquerda e da direita (x, y) e a faixa de cima (acima do muro)
LOTE = dict(esq=(293.0, 297.6, 40.0, 1862.0), dir=(3511.6, 3516.0, 1150.0, 1862.0), topo=(294.0, 3516.0, 44.0, 53.6))


def _copia_x(img, s, o, faixa, desloc, quais):
    """Os px `quais(reg)` da faixa (x0, x1, y0, y1) recebem os px `desloc` unidades ao lado (a grama vizinha)."""
    x0, x1, y0, y1 = faixa
    jan, reg = _reg(img, s, o, (x0, y0, x1, y1), folga=0)
    X0, Y0, X1, Y1 = jan
    d = int(round(desloc * s))
    viz = img[Y0:Y1, X0 + d:X1 + d].astype(np.float32)
    m = quais(reg)
    reg[m] = viz[m]
    return _por(img, jan, reg)


def lote_esq(img, s=1.0, o=(0.0, 0.0), q=LOTE):
    """Borda esquerda: abaixo do muro, tudo à esquerda da grama (x < 296,85) é fundo; a franja azulada que o tracejado
    deixou na beira da grama recebe a grama de 1,5 unidade ao lado."""
    x0, x1, y0, y1 = q["esq"]
    # o fundo: a sombra suave da planta, coluna a coluna (o percentil 90 ao longo da borda, onde o tracejado não está)
    jan, reg = _reg(img, s, o, (288.0, 63.8, 296.85, y1), folga=0)
    perfil = np.percentile(reg, 90, axis=0)
    reg[:] = perfil[None]
    img = _por(img, jan, reg)
    azul = lambda r: (r[..., 0] > r[..., 1] - 2) & (r.mean(2) < 200)
    return _copia_x(img, s, o, (296.85, 297.8, 63.8, y1), 1.6, azul)


def lote_dir(img, s=1.0, o=(0.0, 0.0), q=LOTE):
    """Borda direita: o tracejado sobre a beira do pisante e o fundo vira branco; as manchinhas claras na beira da
    grama recebem a grama de 3 unidades à esquerda."""
    x0, x1, y0, y1 = q["dir"]
    jan, reg = _reg(img, s, o, (x0, y0, x1, y1), folga=0)
    m = _tracejado(reg)
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    m &= _tracejado(reg) | (reg.mean(2) > 200)
    reg[m] = BRANCO
    img = _por(img, jan, reg)
    clara = lambda r: (r.mean(2) > 135) & (r.mean(2) < 250) & (r[..., 1] > r[..., 0] + 4)
    return _copia_x(img, s, o, (3507.0, 3513.4, y0, y1), -3.0, clara)


def lote_topo(img, s=1.0, o=(0.0, 0.0), q=LOTE):
    """Em cima: os tiquinhos são trechos mais escuros na primeira unidade do muro; cada linha do topo do muro volta à
    cor do muro naquela linha (a mediana em 60 unidades em volta)."""
    x0, x1, y0, y1 = q["topo"]
    jan, reg = _reg(img, s, o, (x0, 52.6, x1, 55.2), folga=0)
    L = reg.mean(2)
    k = max(3, int(60 * s) | 1)
    for i in range(reg.shape[0]):
        med = np.stack([ndimage.median_filter(reg[i, :, c], size=k, mode="nearest") for c in range(3)], -1)
        Lm = med.mean(1)
        m = (np.abs(L[i] - Lm) > 12) & (Lm < 200)
        reg[i, m] = med[m]
    return _por(img, jan, reg)


def _faixa_perfil(img, s, o, miolo, amostra_x, eixo="h"):
    """O miolo (x0, y0, x1, y1) de uma folha recebe, de ponta a ponta, o perfil transversal mediano da amostra
    (x0a, x1a): a mesma cor e os mesmos filetes da parte boa da folha."""
    x0, y0, x1, y1 = miolo
    jan, reg = _reg(img, s, o, miolo, folga=0)
    ja, ra = _reg(img, s, o, (amostra_x[0], y0, amostra_x[1], y1), folga=0)
    perfil = np.median(ra, axis=1)
    reg[:] = perfil[:, None, :]
    return _por(img, jan, reg)


# a folha da porta do lavabo: o miolo (entre o contorno preto) no tom escuro do contorno, de ponta a ponta
PORTA_LAVABO = dict(miolo=(2404.55, 1173.25, 2474.75, 1176.05), cor=(36.0, 35.0, 37.0))
# a folha pivotante do hall: o miolo inteiro no vidro cinza-azulado da ponta da direita
PIVOTANTE = dict(miolo=(2574.35, 1295.28, 2751.85, 1298.12), amostra=(2722.0, 2746.0))


def porta_lavabo(img, s=1.0, o=(0.0, 0.0), q=PORTA_LAVABO):
    jan, reg = _reg(img, s, o, q["miolo"], folga=1)
    a = V.cob([V.ret(*q["miolo"])], jan, s, o)[..., None]
    reg = reg * (1 - a) + np.float32(q["cor"]) * a
    return _por(img, jan, reg)


def pivotante(img, s=1.0, o=(0.0, 0.0), q=PIVOTANTE):
    return _faixa_perfil(img, s, o, q["miolo"], q["amostra"])


TRACO = dict(cor=(128.0, 128.0, 128.0), larg=0.8, traco=6.0, vao=4.0)     # o tracejado das claraboias (13/11)


def _tracejar(img, s, o, ret, evitar=(), q=TRACO, lados="tlrb"):
    """O retângulo `ret` tracejado (cinza fino), menos onde há peça (`evitar`, retângulos)."""
    x0, y0, x1, y1 = ret
    jan = V.janela(img, (x0 - 2, y0 - 2, x1 + 2, y1 + 2), s, o, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    polys = []
    for lado, (p0, p1) in zip("tlrb", (((x0, y0), (x1, y0)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1)),
                                        ((x0, y1), (x1, y1)))):
        if lado not in lados:
            continue
        p0, p1 = np.float64(p0), np.float64(p1)
        L = np.hypot(*(p1 - p0))
        d = (p1 - p0) / L
        t = 0.0
        while t < L:
            t1 = min(t + q["traco"], L)
            polys.append(V.seg(tuple(p0 + d * t), tuple(p0 + d * t1), q["larg"]))
            t = t1 + q["vao"]
    a = np.clip(V.cob(polys, jan, s, o), 0, 1)
    if evitar:
        a *= 1 - np.clip(V.cob([V.ret(*r) for r in evitar], jan, s, o), 0, 1)
    reg = reg * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def _claraboia(img, s, o, q):
    """Os restos do tracejado antigo (faixas junto às paredes e a linha velha) voltam a ser piso (quilting da amostra,
    no tom do piso em volta), menos as peças; depois o retângulo novo, tracejado em cinza fino."""
    img = G.refazer(img, s, o, q["zonas"], objetos=q.get("objetos", ()), textura=("quilt", q["fonte"]), tol=0.07,
                    luz_sig=6.0, pena=0.8)
    for r in q.get("paredes", ()):                 # a face das paredes em volta, limpa, no cinza da parede ao lado
        img = _parede(img, s, o, r, q["parede_amostra"])
    return _tracejar(img, s, o, q["ret"], q.get("objetos", ()))


def _parede(img, s, o, r, amostra):
    ja, ra = _reg(img, s, o, amostra, folga=0)
    cor = np.median(ra.reshape(-1, 3), axis=0)
    jan, reg = _reg(img, s, o, r, folga=1)
    a = V.cob([V.ret(*r)], jan, s, o)[..., None]
    reg = reg * (1 - a) + cor[None, None] * a
    return _por(img, jan, reg)


# BH master 1 (item 19): paredes em x 750,0 e 895,2 e y 326,4; a bacia e o vidro do box ficam
CLARA_BHM1 = dict(zonas=[((750.0, 326.4, 895.2, 332.2), "b"), ((750.0, 326.4, 752.6, 362.0), "r"),
                         ((892.6, 326.4, 895.2, 362.0), "l"), ((750.0, 350.2, 895.2, 357.2), "tb")],
                  objetos=[(853.0, 326.0, 876.2, 361.5), (827.4, 326.0, 831.8, 361.5), (757.5, 326.0, 772.0, 334.0)],
                  fonte=(775.0, 333.0, 825.0, 349.0), ret=(750.9, 327.3, 894.3, 355.1),
                  paredes=[(748.0, 323.4, 897.5, 326.4), (747.8, 326.4, 750.0, 359.0), (895.2, 326.4, 897.6, 359.0)],
                  parede_amostra=(760.0, 319.0, 840.0, 324.0))
# o box do BH master 2 (itens 19 e 45): o miolo inteiro num piso só, entre as paredes (y 907,1 e 967,2; x 889,5)
CLARA_BOX2 = dict(zonas=[((866.6, 907.1, 889.5, 967.2), "l")], objetos=[],
                  fonte=(870.6, 911.0, 884.6, 962.0), ret=(868.4, 907.7, 888.9, 966.6),
                  paredes=[(866.0, 904.6, 891.6, 907.1), (866.0, 967.2, 891.6, 969.6), (889.5, 904.6, 891.6, 969.6)],
                  parede_amostra=(845.0, 900.0, 865.0, 905.0))


def claraboia_bhm1(img, s=1.0, o=(0.0, 0.0), q=CLARA_BHM1):
    return _claraboia(img, s, o, q)


def claraboia_box2(img, s=1.0, o=(0.0, 0.0), q=CLARA_BOX2):
    return _claraboia(img, s, o, q)


# o retângulo de registro de cada correção no 12K (a janela que se mexe pode ser maior)
ITENS = {"lote_esq": (300.0, 100.0, 700.0, 600.0), "lote_dir": (3150.0, 1100.0, 3480.0, 1500.0),
         "lote_topo": (1200.0, 60.0, 2200.0, 400.0),
         "porta_lavabo": (2380.0, 1120.0, 2500.0, 1230.0), "pivotante": (2560.0, 1200.0, 2780.0, 1460.0),
         "claraboia_bhm1": (735.0, 300.0, 910.0, 400.0), "claraboia_box2": (800.0, 880.0, 910.0, 990.0)}
JANELA = {"lote_esq": (290.0, 40.0, 300.0, 1865.0), "lote_dir": (3508.0, 1148.0, 3520.0, 1865.0),
          "lote_topo": (292.0, 42.0, 3518.0, 56.0)}


def item(img, nome, s=1.0, origem=(0.0, 0.0)):
    return globals()[nome](img, s, origem)


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

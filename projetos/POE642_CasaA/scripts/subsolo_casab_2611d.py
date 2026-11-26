"""Casa B Subsolo, 4ª leva de 26/11 (o recorte do 12K B: "não ficou bom esse remendo não. melhor juntar as duas paredes e
fechar mais bonita").

- **Academia, os cantos do vidro**: no lugar do bloco de parede de `subsolo_casab_2611c.academia_pontas` (um retângulo
  à parte, mais largo que a parede vertical, com emenda dos dois lados), as duas paredes se juntam num L só:
  - **em cima**: a parede vertical (à esquerda do BH serviço, 1359,1 a 1368,2) desce até a base da parede horizontal
    (de baixo do BH serviço, 439,1 a 448,9, com o fio escuro de baixo); dentro do L, o tom da parede horizontal linha a
    linha (o perfil dela logo à direita) com o contorno da vertical coluna a coluna (o perfil dela logo acima): o
    contorno de fora (a face da esquerda e a de baixo) contínuo, sem contorno do lado de dentro; a sobra do bloco à
    esquerda da face (1358,2 a 1359,1) volta a ser piso; a soleira e o vidro começam na base da parede;
  - **embaixo**: a parede horizontal (da esquerda, 597,3 a 607,1) entra até a face da direita da parede vertical (que
    desce, 1359,1 a 1368,8, com o contorno escuro da direita); o mesmo L: o tom da horizontal linha a linha, o contorno
    da vertical (o perfil dela logo abaixo) coluna a coluna; a emenda entre a parede de antes e o bloco (1357 a 1359)
    some na própria parede; à direita, na altura do L, a face da vertical e a madeira rente a ela vêm de logo abaixo
    (no lugar da faixa clara de madeira copiada de antes).

Final, prancha e 12K A e B (cada canto pelo registro local).

  python3 subsolo_casab_2611d.py [item ...]
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
import um_pav_casaa_2511c as C       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import subsolo_casab_2611 as B1      # noqa: E402

PLANTA = "B_Subsolo"
DZ = B1.DZ


def _faixa(v, a, b):
    return (v >= a) & (v <= b)


def _perfis(reg, xs, ys, q):
    """P_h: o perfil da parede horizontal linha a linha (a mediana das colunas de `fonte_h`); P_v: o da vertical coluna
    a coluna (a mediana das linhas de `fonte_v`); o desvio da vertical em relação ao miolo dela (o contorno)."""
    P_h = np.median(reg[:, _faixa(xs, *q["fonte_h"])], axis=1)
    P_v = np.median(reg[_faixa(ys, *q["fonte_v"])], axis=0)
    mi_h = np.median(P_h[_faixa(ys, *q["miolo_h"])], axis=0)
    mi_v = np.median(P_v[_faixa(xs, *q["miolo_v"])], axis=0)
    return P_h, P_v - mi_v[None], mi_h, mi_v


def _rampa(ys, a, b):
    """0 em a, 1 em b (linear): onde o tom do L passa ao da parede que continua (sem degrau na emenda)."""
    return np.clip((ys - a) / (b - a), 0, 1)[:, None]


CIMA = dict(caixa=(1350.0, 430.0, 1384.0, 452.0),
            fonte_h=(1373.5, 1379.5), fonte_v=(434.0, 437.8), miolo_h=(441.0, 443.5), miolo_v=(1361.5, 1366.5),
            sem_contorno_h=441.2,          # acima disso, dentro do L, o contorno de cima da horizontal sai (miolo)
            sem_contorno_v=1367.6,         # à direita disso, o contorno da direita da vertical sai (dentro do L)
            face_v=1359.35,                # à esquerda disso, a coluna da face (sem o piso de fora misturado)
            vertical=1368.2,               # a face de dentro da vertical: à direita, a horizontal como é
            rampa=(443.0, 439.0),          # de 443 para cima, o miolo passa ao tom da vertical
            L=(1359.0, 439.0, 1372.5, 448.95),
            piso=(1357.6, 440.0, 1359.3, 448.0), piso_desloc=3.0)


def canto_cima(img, s, origem, q=CIMA):
    jan, reg = C._reg(img, q["caixa"], s, origem, folga=int(2 * s) + 2)
    xs, ys = V.coords(jan, s, origem)
    # a sobra do bloco à esquerda da face: o piso de logo à esquerda
    fonte = np.roll(reg, int(round(q["piso_desloc"] * s)), axis=1)
    a = V.cob([V.ret(*q["piso"])], jan, s, origem)[..., None]
    reg = reg * (1 - a) + fonte * a
    P_h, dev, mi_h, mi_v = _perfis(reg, xs, ys, q)
    P_h2 = P_h.copy()
    P_h2[ys < q["sem_contorno_h"]] = mi_h
    P_h2 = P_h2 + (mi_v - mi_h)[None] * _rampa(ys, *q["rampa"])   # em cima, o tom da vertical que desce
    dev[xs > q["sem_contorno_v"]] = 0
    i0 = int(np.argmax(xs >= q["face_v"]))
    dev[xs < q["face_v"]] = dev[i0]
    dentro = (xs < q["vertical"])[None, :, None]
    val = np.where(dentro, P_h2[:, None] + dev[None], P_h[:, None] + 0 * dev[None])
    a = V.cob([V.ret(*q["L"])], jan, s, origem)[..., None]
    return C._gravar(img, jan, reg * (1 - a) + val * a)


BAIXO = dict(caixa=(1342.0, 592.0, 1376.0, 622.0),
             fonte_h=(1347.0, 1353.0), fonte_v=(611.0, 619.0), miolo_h=(600.0, 603.5), miolo_v=(1361.0, 1366.0),
             sem_contorno_h=(597.7, 604.6),   # fora disso, dentro do L, as bordas da horizontal saem (miolo)
             sem_contorno_v=1360.2,           # à esquerda disso, a face da esquerda da vertical sai (dentro do L)
             rampa=(603.5, 607.1),          # de 603,5 para baixo, o miolo passa ao tom da vertical
             L=(1359.0, 597.3, 1369.15, 607.1),
             emenda=(1354.0, 597.0, 1359.0, 607.1),
             # a face da direita (o contorno escuro e a madeira rente a ele) na altura do L: a da própria vertical, de
             # logo abaixo (no lugar da faixa clara de madeira copiada de antes)
             face=(1367.6, 597.3, 1369.7, 607.1), face_pena=1.0, face_desloc=11.0)


def canto_baixo(img, s, origem, q=BAIXO):
    jan, reg = C._reg(img, q["caixa"], s, origem, folga=int(2 * s) + 2)
    xs, ys = V.coords(jan, s, origem)
    P_h, dev, mi_h, mi_v = _perfis(reg, xs, ys, q)
    P_h2 = P_h.copy()
    a0, a1 = q["sem_contorno_h"]
    P_h2[(ys < a0) | (ys > a1)] = mi_h
    P_h2 = P_h2 + (mi_v - mi_h)[None] * _rampa(ys, *q["rampa"])   # embaixo, o tom da vertical que continua
    dev[xs < q["sem_contorno_v"]] = 0
    val = P_h2[:, None] + dev[None]
    # a emenda entre a parede de antes e o bloco: a própria horizontal
    a = V.cob([V.ret(*q["emenda"])], jan, s, origem)[..., None]
    reg = reg * (1 - a) + P_h[:, None] * a
    a = V.cob([V.ret(*q["L"])], jan, s, origem)[..., None]
    reg = reg * (1 - a) + val * a
    fonte = np.roll(reg, -int(round(q["face_desloc"] * s)), axis=0)
    x0, y0, x1, y1 = q["face"]
    a = V.cob([V.ret(x0, y0, x1 + q["face_pena"], y1)], jan, s, origem)
    a = a * np.clip((x1 + q["face_pena"] - xs) / q["face_pena"], 0, 1)[None]   # a madeira se funde à de antes
    a = a[..., None]
    return C._gravar(img, jan, reg * (1 - a) + fonte * a)


ITENS = {"canto_cima": (1340.0, 425.0, 1390.0, 465.0), "canto_baixo": (1340.0, 585.0, 1390.0, 625.0)}
FUNC = {"canto_cima": canto_cima, "canto_baixo": canto_baixo}


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

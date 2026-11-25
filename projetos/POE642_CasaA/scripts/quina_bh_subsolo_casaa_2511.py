"""Casa A Subsolo: a quina dos tocos de parede das portas do BH. FEM. e do BH. MASC. (25/11).

Usuário (com o recorte da porta do BH. MASC. no 12K): "as portas devem encostar na quina". As folhas já nascem na face
do toco (`folhas_bh_subsolo_casaa_2511`), mas no render o pé de cada toco termina arredondado, com um dente: no último
~1,5 px da final a parede afina ~1 px. Entre a quina da folha e a da parede ficava um vão de piso.

O dente é fechado com a própria parede logo acima dele (a linha do toco acima do dente, repetida para baixo, com a
sombra da face): a face do toco desce reta até o pé e a quina fica em ângulo reto, na quina da folha. Só os pixels claros (piso) do dente mudam; a folha e a sua linha ficam.
Final (e a manuscrita), prancha e 12K A e B.

  python3 quina_bh_subsolo_casaa_2511.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
from folhas_bh_subsolo_casaa_2511 import FOLHAS, quina  # noqa: E402

PLANTA = "A_Subsolo"
DENTE = 2.0          # px da final: a altura (acima do pé) e a largura (da face para dentro) do dente fechado


def fechar(img, nome, escala=1.0, origem=(0.0, 0.0)):
    f = FOLHAS[nome]
    fx, fy, par, _ = quina(img, f, escala, origem)
    P = lambda x, y: (int(round((x - origem[0]) * escala)), int(round((y - origem[1]) * escala)))
    # o dente: entre a face e DENTE px para dentro da parede, do pé até DENTE px acima
    x0, x1 = (fx - DENTE, fx + 0.15) if f["lado"] > 0 else (fx - 0.15, fx + DENTE)
    A0, B0 = P(x0, fy - DENTE)
    A1, B1 = P(x1, fy)
    reg = img[B0:B1, A0:A1].astype(np.float32)
    # a parede logo acima do dente: as linhas acima dele (a mediana delas, coluna a coluna), repetidas para baixo
    S0 = P(0, fy - DENTE - 0.8)[1]
    linha = np.median(img[S0:B0, A0:A1].astype(np.float32), axis=0)
    cor = np.median(linha, axis=0)
    claro = reg.mean(2) > float(cor.mean()) + 25
    a = claro.astype(np.float32)
    img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + linha[None, :, :] * a[..., None], 0, 255).astype(np.uint8)
    print(f"      {nome}: quina ({fx:.1f}, {fy:.1f}); {int(claro.sum())} px do dente fechados")
    return img


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in FOLHAS:
            im = fechar(im, nome)
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
        for nome, f in FOLHAS.items():
            x0, x1 = f["caixa"]
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 100, 1409, int(x1) + 100, 1672))
            A, B = mapa(x0, 1509.0)
            sx = (mapa(x0 + 1000.0, 1509.0)[0] - A) / 1000.0
            im = fechar(im, nome, sx, (x0 - A / sx, 1509.0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

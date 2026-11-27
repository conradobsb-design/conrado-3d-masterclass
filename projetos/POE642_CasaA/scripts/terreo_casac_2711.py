"""Casa C Térreo, 27/11: os dois pendentes da revisão das camas.

- **Suíte master, restos da cama antiga junto à cabeceira**: abaixo da cabeceira, de cada lado dos travesseiros, ficava
  uma faixa clara da cama antiga (a cama nova é mais estreita ali: o colchão vai de 952 a 1061, a cabeceira de 947 a
  1069). Agora é o piso de madeira, nas mesmas fileiras de tábuas (o piso de fora dos criados-mudos, na mesma altura),
  com a sombra do vão entre o criado e a cama (o ganho coluna a coluna do piso logo abaixo).
- **Mantas dentro da cama**: a manta de tricô caída passava da beira em três camas (a suíte master pela esquerda, o
  quarto 3 por baixo e o quarto 1 por cima). Agora ela termina 2 px dentro da beira: a beira do edredom e o tapete de
  fora vêm da própria cama e do tapete ao lado (na mesma linha da beira, onde não há manta), e a manta ganha a sombra
  fina do corte, como um tecido dobrado sobre a cama.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2711.py [itens]
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
import um_pav_casaa_2511 as U                    # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]

# (retângulo a preencher, deslocamento da fonte: o piso de fora dos criados, nas mesmas linhas)
CABECEIRA = [((941.5, 579.4, 947.0, 606.6), (-45.0, 0.0)), ((947.0, 586.4, 952.3, 606.6), (-45.0, 0.0)),
             ((1069.2, 579.4, 1075.6, 606.6), (45.0, 0.0)), ((1060.8, 586.4, 1069.2, 606.6), (49.0, 0.0))]
# por cama: (retângulo copiado = a faixa da beira com a parte de fora, deslocamento ao longo da beira, lado da manta
# para a sombra do corte: "dir" = a manta fica à direita do retângulo, etc.)
MANTAS = {
    "manta_master": [((939.0, 663.0, 950.9, 688.0), (0.0, -33.0), "dir"),
                     ((939.0, 688.0, 950.9, 709.4), (0.0, -58.6), "dir")],
    "manta_quarto3": [((1314.8, 480.6, 1338.0, 491.0), (42.0, 0.0), "cima"),
                      ((1338.0, 480.6, 1360.0, 491.0), (34.0, 0.0), "cima")],
    "manta_quarto1": [((2030.5, 392.5, 2054.0, 406.0), (48.0, 0.0), "baixo"),
                      ((2054.0, 392.5, 2079.0, 406.0), (38.0, 0.0), "baixo")],
}
SOMBRA_CORTE = dict(forca=0.16, larg=0.9)


# ----------------------------------------------------------------------------------------------------------------------
def cabeceira_master(img, s, origem, q=CABECEIRA):
    for r, d in q:
        x0, y0, x1, y1 = r
        jan = V.janela(img, (x0 + min(d[0], 0) - 2, y0 - 2, x1 + max(d[0], 0) + 2, y1 + 6), s, origem, folga=2)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1].astype(np.float32)
        H, W = reg.shape[:2]
        M = np.float32([[1, 0, -d[0] * s], [0, 1, -d[1] * s]])           # a fonte em r + d
        fonte = cv2.warpAffine(reg, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # o ganho de cada coluna: o piso logo abaixo do retângulo (com a sombra do vão) sobre o piso da fonte
        xs, ys = V.coords(jan, s, origem)
        lin = (ys >= y1 + 0.6) & (ys <= y1 + 3.0)
        g = reg[lin].mean(0) / np.maximum(fonte[lin].mean(0), 1.0)
        g = cv2.GaussianBlur(g[None].astype(np.float32), (0, 0), max(0.6 * s, 0.5))[0]
        novo = fonte * g[None, :, :]
        a = V.cob([V.ret(*r)], jan, s, origem)
        a = cv2.GaussianBlur(a, (0, 0), 0.35 * s)
        img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)
    return img


def _sombra_corte(img, s, origem, r, lado, q=SOMBRA_CORTE):
    """A sombra fina do corte da manta, do lado dela, junto ao retângulo copiado."""
    x0, y0, x1, y1 = r
    L = q["larg"]
    faixa = {"dir": (x1, y0, x1 + L, y1), "esq": (x0 - L, y0, x0, y1),
             "baixo": (x0, y1, x1, y1 + L), "cima": (x0, y0 - L, x1, y0)}[lado]
    jan = V.janela(img, faixa, s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    d = {"dir": X - x1, "esq": x0 - X, "baixo": Y - y1, "cima": y0 - Y}[lado]
    dentro = V.cob([V.ret(*faixa)], jan, s, origem)
    k = q["forca"] * np.clip(1 - d / L, 0, 1) * dentro
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - k)[..., None]), 0, 255).astype(np.uint8)
    return img


def _manta(img, s, origem, copias):
    for r, d, lado in copias:
        img = U._copiar(img, s, origem, r, d, lados="", pena=0.6)
    for r, d, lado in copias:
        img = _sombra_corte(img, s, origem, r, lado)
    return img


FUNC = {"cabeceira_master": cabeceira_master}
FUNC.update({k: (lambda img, s, o, c=v: _manta(img, s, o, c)) for k, v in MANTAS.items()})
ITENS = {"cabeceira_master": (880.0, 560.0, 1140.0, 640.0), "manta_master": (900.0, 600.0, 1100.0, 740.0),
         "manta_quarto3": (1280.0, 370.0, 1450.0, 500.0), "manta_quarto1": (2000.0, 380.0, 2180.0, 540.0)}


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

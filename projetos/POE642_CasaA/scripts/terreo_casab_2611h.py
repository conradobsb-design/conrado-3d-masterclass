"""Casa B Térreo, 8ª leva de 26/11: as bordas dos tapetes da varanda e do living em cor sólida.

Usuário: "as bordas dos tapetes são cores sólidas". Em `terreo_casab_2611f` a barra de 3 px (5 cm) de cada tapete era o
próprio tecido escurecido, com as listras e a trama dele. Agora a barra é um tom só, liso: a mediana da barra de
antes, em cada imagem (final e 12K), pintada na faixa entre o contorno do PDF e 3 px para dentro, pela cobertura exata
(a beira de fora e a de dentro sem serrilhado). As peças por cima ficam (a mesma proteção de 2611f: sofás, mesas,
banco, poltronas e o pufe).

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casab_2611h.py
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
import terreo_casab_2611b as B       # noqa: E402
import terreo_casab_2611f as F       # noqa: E402

PLANTA = "B_Terreo"
DZ = B.DZ


def _borda(nome):
    def f(img, s, origem, q=F.TAPETES[nome]):
        x0, y0, x1, y1 = q["ret"]
        b = q["borda"]
        m = 24.0                                 # as poltronas que passam do contorno, inteiras
        jan, reg = C._reg(img, (x0 - m, y0 - m, x1 + m, y1 + m), s, origem, folga=0)
        P = F._protecao(reg, jan, s, origem, q["objetos"])
        A = V.cob([V.ret(*q["ret"])], jan, s, origem)
        Ain = V.cob([V.ret(x0 + b, y0 + b, x1 - b, y1 - b)], jan, s, origem)
        fx = np.clip(A - Ain, 0, 1) * (1 - P)
        cheio = fx > 0.99
        if cheio.sum() < 20:
            return img
        cor = np.median(reg[cheio], axis=0)
        reg = reg * (1 - fx[..., None]) + cor[None, None, :] * fx[..., None]
        return C._gravar(img, jan, reg)
    return f


FUNC, ITENS = {}, {}
for _n, _q in F.TAPETES.items():
    FUNC["borda_" + _n] = _borda(_n)
    ITENS["borda_" + _n] = F.ITENS[_n]


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

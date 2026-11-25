"""Casa A Subsolo: o contorno na folha das portas do BH. FEM. e do BH. MASC. (25/11).

Usuário (com o recorte das duas folhas no 12K): "corrija o contorno para ficar na porta." No 12K a folha do render
(a barra clara, com a sombra à esquerda e embaixo) estava até 1,5 px da final à direita do lugar do PDF, e o contorno
fino (da rodada de 19/11) ficou entre as duas: metade na folha, metade no piso.

A folha do render, a sombra e o contorno saem (a pedra do próprio banho ao lado, deslocada) e cada folha é desenhada
pelo PDF no padrão das esquadrias (`vidros_claros_1911`): perfil cinza claro, vidro claro e a linha fina por fora,
encostada na folha. Final (e a manuscrita), prancha e 12K A e B.

  python3 folhas_bh_subsolo_casaa_2511.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vidros_claros_1911 as VC  # noqa: E402
from subsolo_casaa_juncao_portas_2511 import copiar  # noqa: E402

PLANTA = "A_Subsolo"
# (folha do PDF, caixa da folha antiga com a sombra e o contorno, deslocamento da pedra que entra no lugar) — px da final
FOLHAS = {
    "fem": ([(1497.6, 1514.7, 1500.0, 1568.4)], (1495.3, 1515.0, 1502.6, 1571.2), (8.0, 0.0)),
    "masc": ([(1859.4, 1514.7, 1861.8, 1568.4)], (1856.9, 1515.0, 1864.2, 1571.2), (-8.0, 0.0)),
}


def folha(img, nome, escala=1.0, origem=(0.0, 0.0)):
    g, velha, desloc = FOLHAS[nome]
    img = copiar(img, velha, desloc, escala, origem, protege=True)
    traco = 0.5 if escala <= 1.5 else min(0.5, EP.TRACO_12K / escala)
    return VC.redesenhar(img, g, escala=escala, origem=origem, traco=traco, inpaint=False)


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in FOLHAS:
            im = folha(im, nome)
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
        for nome, (_, (x0, y0, x1, y1), _) in FOLHAS.items():
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 100, int(y0) - 100, int(x1) + 100, int(y1) + 100))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = folha(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: folha {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

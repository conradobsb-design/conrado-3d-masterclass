"""Casa B Térreo: a prainha e o banco do spa no cinza equilibrado do fundo, como na Casa A (26/11).

Usuário (com o recorte do SPA e da PRAINHA): "corrigir o tom das áreas mais rasas da piscina conforme fizemos na casa A".
O mesmo de `prainha_cinza_casaa_2511.py` (o raso ao matiz e à saturação do fundo e a 80% da luminosidade: `RASO`): a
água e o fundo vêm de `piscinas_sobrias_1911` (a máscara da água e os retângulos do fundo da Casa B, `FUNDO["B"]`); a
parte rasa é a água menos o fundo, com a franja de 1 px da beira. As duas espreguiçadeiras da prainha (dentro da água,
na máscara de buracos fechados) ficam como estão: as peças creme (o matiz amarelado com alguma saturação) achadas pela
cor, cada uma no retângulo dela, com 1 px de folga. O pastilhado, os reflexos, as bordas e os rótulos ficam.

Final, prancha e 12K A e B (no 12K, as divisas achadas na final, levadas pelo registro).

  python3 prainha_cinza_casab_2611.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import piscinas_sobrias_1911 as PS  # noqa: E402
import prainha_cinza_casaa_2511 as P  # noqa: E402

PLANTA = "B_Terreo"
RASO = P.RASO
MARGEM = P.MARGEM
MOVEL = dict(h=(8, 45), s=12, v=110, area=120.0)     # a área mínima em px da final


def moveis(img, rasa, escala=1.0, q=MOVEL):
    """As peças creme dentro da água rasa (as espreguiçadeiras): o retângulo de cada uma, com 1 px de folga. Só as
    peças inteiras na água (a borda de Bege, o deck e o piso em volta ficam fora)."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, Sat, V = [hsv[..., i] for i in range(3)]
    m = ((H >= q["h"][0]) & (H <= q["h"][1]) & (Sat >= q["s"]) & (V >= q["v"])).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    out = np.zeros(m.shape, np.float32)
    f = int(round(1.0 * escala))
    for i in range(1, n):
        if st[i, 4] < q["area"] * escala * escala:
            continue
        if rasa[lab == i].mean() < 0.95:
            continue
        x, y, w, h = st[i, :4]
        out[max(y - f, 0):y + h + f, max(x - f, 0):x + w + f] = 1
    return out


def recorte(img, rets, escala=1.0, q=RASO):
    a0 = max(int(min(r[0] for r in rets) - MARGEM * escala), 0)
    b0 = max(int(min(r[1] for r in rets) - MARGEM * escala), 0)
    a1 = min(int(max(r[2] for r in rets) + MARGEM * escala), img.shape[1])
    b1 = min(int(max(r[3] for r in rets) + MARGEM * escala), img.shape[0])
    loc = [(x0 - a0, y0 - b0, x1 - a0, y1 - b0, l) for x0, y0, x1, y1, l in rets]
    sub = img[b0:b1, a0:a1]
    wr, finais = P.peso_raso(sub, loc, escala)
    mv = moveis(sub, wr > 0.5, escala)
    wr = wr * (1 - cv2.GaussianBlur(mv, (0, 0), 0.4 * escala))
    return (a0, b0, a1, b1), PS.aplicar(sub, wr, q), [(x0 + a0, y0 + b0, x1 + a0, y1 + b0) for x0, y0, x1, y1 in finais]


def main():
    c, pav = PLANTA.split("_")
    rets = PS.FUNDO["B"]
    orig = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    finais = None
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        (x0, y0, x1, y1), novo, fin = recorte(im, rets)
        im[y0:y1, x0:x1] = novo
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            finais, final = fin, im
        print(f, fin)
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = final
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    a0 = int(min(r[0] for r in finais)) - MARGEM
    b0 = int(min(r[1] for r in finais)) - MARGEM
    a1 = int(max(r[2] for r in finais)) + MARGEM
    b1 = int(max(r[3] for r in finais)) + MARGEM
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        mapa, cc = PS.registro_12k(orig, cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), dz, (a0, b0, a1, b1))
        r12 = []
        for x0, y0, x1, y1 in finais:
            X0, Y0 = mapa(x0, y0)
            X1, Y1 = mapa(x1, y1)
            r12.append((int(round(X0)), int(round(Y0)), int(round(X1)), int(round(Y1)), ""))
        (x0, y0, x1, y1), novo, _ = recorte(im, r12, escala=dz["s"])
        im[y0:y1, x0:x1] = novo
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        print(rel.name, "registro", round(cc, 4))
        del im


if __name__ == "__main__":
    main()

"""Casa A Térreo: a prainha e o banco do spa num cinza equilibrado, como o fundo da piscina ao lado (25/11).

Usuário (com o recorte do SPA e da PRAINHA): "vamos equilibrar mais esse tom para o cinza, nem tão claro e nem tão
escuro, como o fundo ao lado". Na rodada de 19/11 (`piscinas_sobrias_1911`) só a água funda (a piscina e o miolo do spa)
foi para o azul-acinzentado sóbrio; a prainha e o banco em volta do spa ficaram no verde-água claro.

A água rasa passa ao matiz e à saturação do fundo (o matiz +34°, a saturação a 85%: a mesma do fundo) e a meio caminho
na luminosidade (80%: entre o raso claro e o fundo escuro; o fundo fica um pouco mais escuro, para a profundidade seguir
legível). O pastilhado, os reflexos, as bordas e os rótulos ficam. A água e o fundo vêm de `piscinas_sobrias_1911` (a
máscara da água e os retângulos do fundo, com as divisas ajustadas à mudança de tom); a parte rasa é a água menos o
fundo, com a franja de 1 px da beira (ainda verde-água) junto.

Final (e a manuscrita, se houver), prancha e 12K A e B (no 12K, as divisas achadas na final, levadas pelo registro).

  python3 prainha_cinza_casaa_2511.py
  python3 prainha_cinza_casaa_2511.py --opcoes      # só a amostra com as três luminosidades (86%, 80%, 74%)
"""
import argparse
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

PLANTA = "A_Terreo"
RASO = {"dh": 34, "fs": 0.85, "fv": 0.80}
MARGEM = 30
ANTES = "7976768"     # o último commit com a prainha verde-água (para a amostra --opcoes)


def peso_raso(img, rets, escala=1.0):
    """1 na água rasa (a prainha, o banco do spa), 0 no fundo e fora da água; a franja verde-água da beira entra."""
    w, M, finais = PS.peso_fundo(img, rets, escala)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    agua_tom = (hsv[..., 0] >= 75) & (hsv[..., 0] <= 105) & (hsv[..., 1] >= 15)
    k = max(3, int(round(1.0 * escala)) * 2 + 1)
    beira = cv2.dilate(M, np.ones((k, k), np.uint8)).astype(bool) & agua_tom
    Md = M.astype(bool) | beira
    wr = np.clip(cv2.GaussianBlur(Md.astype(np.float32), (0, 0), 0.5 * escala) * Md - w, 0, 1)
    return wr, finais


def recorte(img, rets, escala=1.0, q=RASO):
    a0 = max(int(min(r[0] for r in rets) - MARGEM * escala), 0)
    b0 = max(int(min(r[1] for r in rets) - MARGEM * escala), 0)
    a1 = min(int(max(r[2] for r in rets) + MARGEM * escala), img.shape[1])
    b1 = min(int(max(r[3] for r in rets) + MARGEM * escala), img.shape[0])
    loc = [(x0 - a0, y0 - b0, x1 - a0, y1 - b0, l) for x0, y0, x1, y1, l in rets]
    sub = img[b0:b1, a0:a1]
    wr, finais = peso_raso(sub, loc, escala)
    return (a0, b0, a1, b1), PS.aplicar(sub, wr, q), [(x0 + a0, y0 + b0, x1 + a0, y1 + b0) for x0, y0, x1, y1 in finais]


def opcoes():
    import subprocess
    rel = str(Path(EP.PLANTAS[PLANTA][0]))
    base = cv2.imdecode(np.frombuffer(subprocess.run(["git", "show", f"{ANTES}:projetos/{rel}"], cwd=EP.PROJ,
                                                     capture_output=True, check=True).stdout, np.uint8), cv2.IMREAD_COLOR)
    rets = PS.FUNDO["A"]
    (a0, b0, a1, b1), _, _ = recorte(base, rets)
    painel = [base[b0:b1, a0:a1]]
    for fv in (0.86, 0.80, 0.74):
        painel.append(recorte(base, rets, q=dict(RASO, fv=fv))[1])
    out = EP.PROJ / "POE642_CasaA/renders/POE642_CasaA_PH_Terreo_2511_prainha_opcoes.jpg"
    cv2.imwrite(str(out), np.hstack(painel), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(out)


def main():
    c, pav = PLANTA.split("_")
    rets = PS.FUNDO["A"]
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--opcoes", action="store_true")
    if ap.parse_args().opcoes:
        opcoes()
    else:
        main()

"""O JPG em 12K da Casa C (Subsolo e Térreo; 13/11, "ME TRAGA O 12K E DEMAIS"; os créditos liberados: "Pode gastar
creditos").

Mais simples que o roteiro das Casas A e B (sem a IA generativa nos pisos: nada muda de lugar nem de desenho):
  1. `preparar <pav>`: o recorte A3 deitado (4961 x 3508) da planta na final de 3840 px: a caixa do que não é branco, a
     margem da A3 (`MARGEM`), completado no branco até a proporção da A3; grava a entrada do Topaz e os dados do recorte.
  2. A entrada no Topaz (High Fidelity V2), a 12288 x 8689.
  3. `montar <pav> <saída do Topaz>`: a saída no tamanho certo, os tons da final (a baixa frequência da entrada,
     ampliada), o fundo fora da planta em branco puro; o JPG (qualidade 95, 743 dpi na A3) e as conferências.

  python3 ampliacao_12k_casac.py preparar Subsolo|Terreo
  python3 ampliacao_12k_casac.py montar Subsolo|Terreo <saída do Topaz>
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
E = CASA_C / "entrega"
A3 = (4961, 3508)
L, H = 12288, 8689
MARGEM = 150 / 4961                      # a margem da A3 (fração da largura), como nas Casas A e B
TOM_SIGMA_PX = 2.5
FUNDO_FOLGA_PX = 3
CONFERENCIA = {"Subsolo": {"academia": (1150, 250, 1650, 750), "sauna_bh": (680, 720, 1000, 980),
                           "escadas": (360, 680, 900, 1120)},
               "Terreo": {"suites": (800, 300, 2200, 800), "estar": (1600, 1150, 2400, 1650),
                          "cozinha_garagem": (2150, 250, 3300, 830), "piscina_deck": (600, 950, 1150, 1700)}}


def final(pav):
    return R / f"POE642_CasaC_PH_{pav}_final_rotulos.png"


def entrada(pav):
    return R / f"POE642_CasaC_PH_{pav}_12K_entrada_topaz.png"


def dados(pav):
    return R / f"POE642_CasaC_PH_{pav}_12K_dados.json"


def preparar(pav):
    img = cv2.imread(str(final(pav)))
    Hf, Wf = img.shape[:2]
    nb = (img.astype(np.int16).min(axis=2) < 245)
    ys, xs = np.nonzero(nb)
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    w, h = x1 - x0, y1 - y0
    # a largura do recorte com a margem; a altura pela proporção da A3 (ou o contrário, se a planta for alta)
    Wc = w / (1 - 2 * MARGEM)
    Hc = Wc * A3[1] / A3[0]
    if Hc < h / (1 - 2 * MARGEM * A3[0] / A3[1]):
        Hc = h / (1 - 2 * MARGEM * A3[0] / A3[1])
        Wc = Hc * A3[0] / A3[1]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    X0, Y0 = cx - Wc / 2, cy - Hc / 2
    Wi, Hi = int(round(Wc)), int(round(Hc))
    M = np.float64([[1, 0, -X0], [0, 1, -Y0]])
    ent = cv2.warpAffine(img, M, (Wi, Hi), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT,
                         borderValue=(255, 255, 255))
    cv2.imwrite(str(entrada(pav)), ent)
    dados(pav).write_text(json.dumps({"planta": [x0, y0, x1, y1], "X0": X0, "Y0": Y0, "Wc": Wc, "Hc": Hc,
                                      "entrada": [Wi, Hi]}, indent=1) + "\n")
    print(f"[{pav}] a planta {x0},{y0} a {x1},{y1}; o recorte A3 {Wi}x{Hi} a partir de ({X0:.1f}, {Y0:.1f}) "
          f"({L / Wc:.3f}x no 12K) -> {entrada(pav).name}")


def montar(pav, saida_topaz):
    from PIL import Image
    d = json.loads(dados(pav).read_text())
    img = cv2.imread(str(final(pav)))
    ent = cv2.imread(str(entrada(pav)))
    Wi, Hi = ent.shape[1], ent.shape[0]
    ia = cv2.imread(str(saida_topaz))
    print(f"[{pav}] a saída do Topaz: {ia.shape[1]}x{ia.shape[0]}; o JPG: {L}x{H} ({L / d['Wc']:.3f}x a final)")
    out = ia if ia.shape[:2] == (H, L) else cv2.resize(ia, (L, H), interpolation=cv2.INTER_LANCZOS4)
    del ia
    # os tons da final: a baixa frequência da entrada, ampliada, em faixas
    peq = cv2.resize(out, (Wi, Hi), interpolation=cv2.INTER_AREA).astype(np.float32)
    corr = cv2.GaussianBlur(ent.astype(np.float32), (0, 0), TOM_SIGMA_PX) - cv2.GaussianBlur(peq, (0, 0), TOM_SIGMA_PX)
    corr = cv2.resize(corr, (L, H), interpolation=cv2.INTER_CUBIC)
    # o fundo: o branco ligado à borda da entrada, branco puro
    g = cv2.cvtColor(ent, cv2.COLOR_BGR2GRAY)
    fundo = (g >= 250).astype(np.uint8)
    n, lab = cv2.connectedComponents(fundo)
    bordas = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    fundo = np.isin(lab, bordas[bordas > 0]).astype(np.uint8)
    kk = 2 * FUNDO_FOLGA_PX + 1
    fundo = cv2.erode(fundo, np.ones((kk, kk), np.uint8)).astype(np.float32)
    fa = cv2.GaussianBlur(cv2.resize(fundo, (L, H), interpolation=cv2.INTER_LINEAR), (0, 0), 2.0)
    for y in range(0, H, 1024):
        reg = out[y:y + 1024].astype(np.float32) + corr[y:y + 1024]
        f_ = fa[y:y + 1024, :, None]
        reg = reg * (1 - f_) + 255 * f_
        out[y:y + 1024] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    del corr, fa
    saida = E / f"POE642_CasaC_PH_{pav}_12K_opcao_A.jpg"
    dpi = int(round(L / (420 / 25.4)))
    Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(saida, quality=95, subsampling=0, dpi=(dpi, dpi),
                                                               optimize=True)
    cv2.imwrite(str(R / f"POE642_CasaC_PH_{pav}_12K_opcao_A_previa.jpg"),
                cv2.resize(out, (2000, round(2000 * H / L)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
    s = L / d["Wc"]
    for nome, (x0, y0, x1, y1) in CONFERENCIA[pav].items():
        u0, v0 = int(round((x0 - d["X0"]) * s)), int(round((y0 - d["Y0"]) * s))
        u1, v1 = int(round((x1 - d["X0"]) * s)), int(round((y1 - d["Y0"]) * s))
        cr = out[max(v0, 0):v1, max(u0, 0):u1]
        ref = cv2.resize(img[y0:y1, x0:x1], (cr.shape[1], cr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
        par = np.hstack([ref, np.full((cr.shape[0], 24, 3), 255, np.uint8), cr])
        cv2.imwrite(str(R / f"POE642_CasaC_PH_{pav}_12K_opcao_A_conferencia_{nome}.jpg"),
                    cv2.resize(par, (par.shape[1] // 3, par.shape[0] // 3), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {saida} {L}x{H} ({dpi} dpi na A3), {saida.stat().st_size / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=["preparar", "montar"])
    ap.add_argument("pav", choices=["Subsolo", "Terreo"])
    ap.add_argument("saida_topaz", nargs="?")
    a = ap.parse_args()
    if a.acao == "preparar":
        preparar(a.pav)
    else:
        montar(a.pav, a.saida_topaz)


if __name__ == "__main__":
    sys.exit(main())

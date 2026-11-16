"""O JPG em 12K da Casa D (Subsolo e Térreo; 16/11, usuário: "Aprovado o Subsolo da casa D. Rode as versões 12k"), pelo
roteiro da Casa C (`ampliacao_12k_casac`, as mesmas etapas e os mesmos parâmetros).

Mais simples que o roteiro das Casas A e B (sem a IA generativa nos pisos: nada muda de lugar nem de desenho):
  1. `preparar <pav>`: o recorte A3 deitado (4961 x 3508) da planta na final de 3840 px: a caixa do que não é branco, a
     margem da A3 (`MARGEM`), completado no branco até a proporção da A3; grava a entrada do Topaz e os dados do recorte.
  2. A entrada no Topaz (High Fidelity V2), a 12288 x 8689.
  3. `montar <pav> <saída do Topaz>`: a saída no tamanho certo, os tons da final (a baixa frequência da entrada,
     ampliada), o fundo fora da planta em branco puro; o JPG (qualidade 95, 743 dpi na A3) e as conferências.

  python3 ampliacao_12k_casad.py preparar Subsolo|Terreo [--opcao B]
  python3 ampliacao_12k_casad.py montar Subsolo|Terreo <saída do Topaz> [--opcao B]

A opção B: a entrada do Topaz sem os rótulos nem as descrições das escadas (`rotulos_kalam_casad.preparar`, que grava
os dados das linhas) e, no 12K, os textos na Kalam (`rotulos_kalam_casac.desenhar`, com esses dados); o recorte e os
tons são os da opção A (`preparar` da A antes).
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
CASA_D = AQUI.parents[1] / "POE642_CasaD"
R = CASA_D / "renders"
E = CASA_D / "entrega"
A3 = (4961, 3508)
L, H = 12288, 8689
MARGEM = 150 / 4961                      # a margem da A3 (fração da largura), como nas Casas A e B
TOM_SIGMA_PX = 2.5
FUNDO_FOLGA_PX = 3
# os trechos de conferência (px da final): a final ampliada ao lado do 12K
CONFERENCIA = {"Subsolo": {"academia_portas": (700, 1250, 1300, 1620), "sauna_vestiario": (840, 1570, 1320, 1790),
                           "dce_escada": (560, 960, 1160, 1350), "elevador_deposito": (1080, 960, 1580, 1500)},
               "Terreo": {"suites": (300, 300, 1500, 900), "estar_jantar": (1500, 900, 2500, 1500),
                          "cozinha_servico": (1900, 300, 2900, 900), "piscina_deck": (300, 1100, 1300, 1900)}}


def final(pav):
    return R / f"POE642_CasaD_PH_{pav}_final_rotulos.png"


def entrada(pav, opcao="A"):
    return R / f"POE642_CasaD_PH_{pav}_12K_entrada_topaz{'' if opcao == 'A' else '_opcao_B'}.png"


def dados(pav):
    return R / f"POE642_CasaD_PH_{pav}_12K_dados.json"


def rotulos_12k(pav):
    """Os rótulos que o 12K redesenha nítidos (a entrada do Topaz vai sem eles): nenhum na Casa D."""
    return []


def kalam(pav):
    return R / f"POE642_CasaD_PH_{pav}_rotulos_kalam.json"


def preparar(pav, opcao="A"):
    if opcao == "B":
        # a opção B: a final sem os rótulos nem as descrições das escadas (`rotulos_kalam_casad.preparar`), que voltam
        # na Kalam no 12K; os dados das linhas vão para `kalam(pav)`
        import rotulos_kalam_casad as KD
        img, linhas = KD.preparar(pav, cv2.imread(str(final(pav))))
        kalam(pav).write_text(json.dumps(linhas, ensure_ascii=False, indent=1) + "\n")
    else:
        img = cv2.imread(str(final(pav)))
        for r in rotulos_12k(pav):
            img = r["apaga"](img)
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
    cv2.imwrite(str(entrada(pav, opcao)), ent)
    if opcao == "B":
        print(f"[{pav}] a entrada da opção B (sem textos) -> {entrada(pav, opcao).name}")
        return
    dados(pav).write_text(json.dumps({"planta": [x0, y0, x1, y1], "X0": X0, "Y0": Y0, "Wc": Wc, "Hc": Hc,
                                      "entrada": [Wi, Hi]}, indent=1) + "\n")
    print(f"[{pav}] a planta {x0},{y0} a {x1},{y1}; o recorte A3 {Wi}x{Hi} a partir de ({X0:.1f}, {Y0:.1f}) "
          f"({L / Wc:.3f}x no 12K) -> {entrada(pav).name}")


def montar(pav, saida_topaz, opcao="A"):
    from PIL import Image
    d = json.loads(dados(pav).read_text())
    img = cv2.imread(str(final(pav)))
    ent = cv2.imread(str(entrada(pav, opcao)))
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
    if opcao == "B":
        import rotulos_kalam_casac as K
        K.dados = kalam
        K.desenhar(out, pav, L / d["Wc"], d["X0"], d["Y0"])
    elif rotulos_12k(pav):
        import revisao_terreo_casac_1411 as R14
        for r in rotulos_12k(pav):
            R14.desenhar_linhas(out, r["linhas"], r["cor"], s=L / d["Wc"], X0=d["X0"], Y0=d["Y0"])
        print(f"    {len(rotulos_12k(pav))} rótulo(s) redesenhado(s) nítido(s) no 12K")
    saida = E / f"POE642_CasaD_PH_{pav}_12K_opcao_{opcao}.jpg"
    dpi = int(round(L / (420 / 25.4)))
    Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(saida, quality=95, subsampling=0, dpi=(dpi, dpi),
                                                               optimize=True)
    cv2.imwrite(str(R / f"POE642_CasaD_PH_{pav}_12K_opcao_{opcao}_previa.jpg"),
                cv2.resize(out, (2000, round(2000 * H / L)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
    s = L / d["Wc"]
    for nome, (x0, y0, x1, y1) in CONFERENCIA[pav].items():
        u0, v0 = int(round((x0 - d["X0"]) * s)), int(round((y0 - d["Y0"]) * s))
        u1, v1 = int(round((x1 - d["X0"]) * s)), int(round((y1 - d["Y0"]) * s))
        cr = out[max(v0, 0):v1, max(u0, 0):u1]
        ref = cv2.resize(img[y0:y1, x0:x1], (cr.shape[1], cr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
        par = np.hstack([ref, np.full((cr.shape[0], 24, 3), 255, np.uint8), cr])
        cv2.imwrite(str(R / f"POE642_CasaD_PH_{pav}_12K_opcao_{opcao}_conferencia_{nome}.jpg"),
                    cv2.resize(par, (par.shape[1] // 3, par.shape[0] // 3), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {saida} {L}x{H} ({dpi} dpi na A3), {saida.stat().st_size / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=["preparar", "montar"])
    ap.add_argument("pav", choices=["Subsolo", "Terreo"])
    ap.add_argument("saida_topaz", nargs="?")
    ap.add_argument("--opcao", choices=("A", "B"), default="A")
    a = ap.parse_args()
    if a.acao == "preparar":
        preparar(a.pav, a.opcao)
    else:
        montar(a.pav, a.saida_topaz, a.opcao)


if __name__ == "__main__":
    sys.exit(main())

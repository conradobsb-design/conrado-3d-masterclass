#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Térreo da Casa E (POE 642).

O render (Nano Banana Pro, 2000 x 1116) manteve a escala da base: a base 16:9 reduzida ao tamanho do
render cai nele quase pela identidade (escala 0,9998 x 1,0066, deslocamento de 0,3 e -2,8 px). Os
retoques são feitos no quadro do render, como nas outras casas.

Itens (o mapa está em POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_erros.jpg):
1. Lote: a vegetação que o motor passou para fora do lote (à esquerda, embaixo e no alto à
   direita) sai, e as linhas tracejadas do lote, que ele apagou, voltam: fora do lote fica a base
   alinhada (o branco, a linha tracejada da esquerda, a da direita e o retângulo tracejado embaixo).
   Os muros de cima e de baixo, onde as folhas passavam por cima, voltam ao preto (cada linha do
   muro vira a mediana dela num trecho limpo).
2. Faixa à direita dos pisantes: a faixa em Bege Bahia que o motor inventou entre o gramado e a
   linha tracejada da direita (fora do gramado, branca no PDF) volta ao branco da base, no mesmo
   passo do item 1.
3. Jardim interno: as plantas, que o motor espalhou para fora da floreira (por cima da escada e no
   travertino em volta, com a sombra delas), ficam só no retângulo da floreira do PDF; fora dele
   voltam a escada (os degraus tracejados, da mesma coluna logo acima, e a linha diagonal, que segue
   até a floreira) e o travertino (da mesma coluna, mais abaixo: os veios correm na vertical), e a
   borda da floreira entra em traço fino.

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/retoque_terreo_casae.py POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_render.webp \
      --saida POE642_CasaE/renders --nome POE642_CasaE_PH_Terreo_v1_retocado
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/

SS = 8                             # superamostragem dos traços desenhados
BASE = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png"


def alinhar_base(render):
    """Base 16:9 reduzida ao tamanho do render e levada a ele por SIFT + afim (como nas outras casas)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    al = cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    return A, al


# lote no quadro do render: o gramado vai de x = 141 a 1798; o muro de cima ocupa as linhas 0 a 5
# (de 142 a 1798) e o de baixo as linhas 932 a 937 (de 141 a 1851, até a linha tracejada da direita).
# Fora: x < 141, x >= 1799 acima do muro de baixo (a faixa entre o gramado e a linha tracejada da
# direita, onde o motor pôs o Bege Bahia), e tudo abaixo do muro de baixo
LOTE = {
    "x_esq": 141, "x_dir": 1799, "x_muro_baixo": 1852,
    "muro_cima": (0, 6), "muro_baixo": (932, 938),
    # trecho limpo (sem folhas) de onde sai a mediana de cada linha do muro
    "limpo_cima": (450, 1450), "limpo_baixo": (450, 1300),
}


def lote(out, base):
    q = LOTE
    xe, xd, xb = q["x_esq"], q["x_dir"], q["x_muro_baixo"]
    (c0, c1), (b0, b1) = q["muro_cima"], q["muro_baixo"]
    a, b = q["limpo_cima"]
    out[c0:c1, xe:xd] = np.median(out[c0:c1, a:b], axis=1).astype(np.uint8)[:, None]
    a, b = q["limpo_baixo"]
    out[b0:b1, xe:xb] = np.median(out[b0:b1, a:b], axis=1).astype(np.uint8)[:, None]
    fora = np.zeros(out.shape[:2], bool)
    fora[:, :xe] = True
    fora[:b0, xd:] = True
    fora[b0:b1, xb:] = True
    fora[b1:, :] = True
    out[fora] = base[fora]
    print(f"    muros de cima e de baixo sem as folhas; fora do lote: base ({int(fora.sum())} px)")
    return out


# jardim interno (item 3): a floreira do PDF no quadro do render (a borda escura da terra no render
# cai nela), a escada logo acima (degraus tracejados verticais de 497 a 542, com a linha horizontal
# em 523, e a diagonal de (1079, 498) a (1094, 527), que no PDF vai até a floreira)
JARDIM = {
    "floreira": (977, 543, 1155, 582), "janela": (950, 490, 1185, 615),
    # a fonte da escada fica abaixo da sombra do louceiro (497 a 499) e acima da linha horizontal;
    # deslocamentos (dy, dx): primeiro só na vertical (o tracejado repete a cada ~6,5 px), depois
    # também de dois degraus (~18,6 px) para os lados, onde a diagonal ocupa a fonte
    "escada": (977, 497, 1155, 543), "fonte_escada": (500, 523),
    "desloc_escada": [(dy, 0) for dy in (13, 26, 20, 7, 14, 19)] + [(dy, dx) for dy in (13, 7, 20) for dx in (-19, 19, -28, 28)],
    "desloc_trav": (64, 80, 96, 112),
    "diagonal": ((1079, 498), (1094, 527)), "diag_fim_y": 543, "cor_diag": (128, 142, 158),
    # plantas: verdes ou escuras; sombra: mais escura que o travertino limpo da mesma coluna (veios
    # verticais), perto das plantas e fora da escada
    "verde": 2, "escuro": 110, "ref_trav": (620, 680), "sombra": 7, "alcance_sombra": 12,
    "borda": {"cor": (78, 80, 80), "larg": 0.9, "forca": 0.85},
}


def linha_aa(forma, pts, larg, fechada=False):
    """Máscara (0 a 1) de uma polilinha, desenhada em SS x e reduzida."""
    h, w = forma
    m = np.zeros((h * SS, w * SS), np.uint8)
    p = np.int32(np.round(np.float64(pts) * SS))
    cv2.polylines(m, [p], fechada, 255, max(1, int(round(larg * SS))), cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def jardim_interno(out):
    q = JARDIM
    fx0, fy0, fx1, fy1 = q["floreira"]
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = out[wy0:wy1, wx0:wx1].astype(int)
    lum = reg.mean(axis=2)
    planta = (reg[..., 1] > reg[..., 2] + q["verde"]) | (lum < q["escuro"])
    dentro = np.zeros(lum.shape, bool)
    dentro[fy0 - wy0:fy1 - wy0, fx0 - wx0:fx1 - wx0] = True
    sx0, sy0, sx1, sy1 = q["escada"]
    escada = np.zeros(lum.shape, bool)
    escada[sy0 - wy0:sy1 - wy0, sx0 - wx0:sx1 - wx0] = True
    # a mancha das plantas (ligada à floreira) e a sombra delas no travertino, em volta
    n, lab = cv2.connectedComponents(planta.astype(np.uint8))
    ligada = np.isin(lab, np.unique(lab[dentro & planta])) & (lab > 0)
    r0, r1 = q["ref_trav"]
    ref = np.median(out[r0:r1, wx0:wx1].astype(np.float32).mean(axis=2), axis=0)[None, :]
    k = 2 * q["alcance_sombra"] + 1
    perto = cv2.dilate(ligada.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    m = cv2.dilate(ligada.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    m |= perto & (lum < ref - q["sombra"]) & ~escada
    m |= perto & planta                                  # pontas soltas de folha
    # na escada, o halo claro em volta das folhas também sai (a fonte é a própria escada, limpa)
    m |= escada & (cv2.dilate(ligada.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
    m &= ~dentro
    f0, f1 = q["fonte_escada"]
    m[:f1 + 1 - wy0] &= ~escada[:f1 + 1 - wy0]          # as plantas não sobem acima da linha horizontal
    # escada: a mesma coluna, alguns degraus de tracejado acima (sem a diagonal e sem as plantas);
    # travertino: a mesma coluna, mais abaixo, onde não há planta nem sombra
    (dx0, dy0), (dx1, dy1) = q["diagonal"]
    incl = (dx1 - dx0) / (dy1 - dy0)
    ys, xs = np.mgrid[wy0:wy1, wx0:wx1]
    na_diag = np.abs(xs - (dx0 + (ys - dy0) * incl)) < 5
    orig = out.copy()
    n_esc = n_trav = 0
    for y, x in zip(*np.nonzero(m)):
        Y, X = y + wy0, x + wx0
        if escada[y, x]:
            for dy, dx in q["desloc_escada"]:
                fy, fx = Y - dy, X + dx
                if f0 <= fy < f1 and sx0 <= fx < sx1 and not na_diag[fy - wy0, fx - wx0] and not m[fy - wy0, fx - wx0]:
                    out[Y, X] = orig[fy, fx]
                    n_esc += 1
                    break
        else:
            for d in q["desloc_trav"]:
                fy = Y + d
                if fy >= wy1 or not m[fy - wy0, x]:
                    out[Y, X] = orig[fy, X]
                    n_trav += 1
                    break
    # a diagonal segue da linha horizontal até a floreira
    a = linha_aa(out.shape[:2], [(dx0 + (f1 + 0.5 - dy0) * incl, f1 + 0.5),
                                 (dx0 + (q["diag_fim_y"] - dy0) * incl, q["diag_fim_y"])], 1.0)[..., None] * 0.8
    out[:] = np.clip(out * (1 - a) + np.float32(q["cor_diag"]) * a, 0, 255).astype(np.uint8)
    # borda da floreira
    b = q["borda"]
    a = linha_aa(out.shape[:2], [(fx0 + 0.5, fy0 + 0.5), (fx1 - 0.5, fy0 + 0.5), (fx1 - 0.5, fy1 - 0.5),
                                 (fx0 + 0.5, fy1 - 0.5)], b["larg"], fechada=True)[..., None] * b["forca"]
    out[:] = np.clip(out * (1 - a) + np.float32(b["cor"]) * a, 0, 255).astype(np.uint8)
    print(f"    plantas fora da floreira: {n_esc} px de escada e {n_trav} px de travertino refeitos; diagonal e borda")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    A, base = alinhar_base(orig)
    print("[1, 2] lote: vegetação fora do lote, linhas tracejadas e faixa à direita dos pisantes")
    out = lote(out, base)
    print("[3] jardim interno: plantas só na floreira")
    out = jardim_interno(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

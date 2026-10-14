#!/usr/bin/env python3
"""Retoque sem IA do render do Subsolo da Casa C (prompt v3). A imagem final é o render.

1. Bege Bahia: o motor clareou o mármore (cerca de 235/224/212 contra 226/211/200 do aprovado).
   O pátio, os degraus largos, o caminho e o depósito recebem o mesmo Bege Bahia da base: o das
   varandas do 1º Pavimento da Casa A, tecido por image quilting na escala do render.
   - As áreas vêm da base chapada (v2, cor #E8E8E8), alinhada ao render por SIFT.
   - Contornos, a porta do depósito e as plantas da floreira ficam como estão.
   - Nos pixels de borda (linha ou fundo branco misturados com a pedra), só a parte da pedra
     muda de tom.
2. Sentido de descida dos degraus largos: o motor pôs a sombra embaixo de cada aresta, o que lê
   como descida para baixo. A descida é para cima, rumo ao pátio (definido pelo usuário).
   - Cada aresta é redesenhada sobre o Bege Bahia novo, na mesma posição e com o mesmo traço.
   - O perfil da aresta (linha, sombra e filete de luz) é espelhado em torno da linha: a sombra
     passa para cima e o filete de luz para baixo.
   A escada curta numerada (esmaecida) não muda.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_subsolo_casac_v3.py RENDER.webp --saida PASTA --nome NOME
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))
from texturizar_base import quilting  # noqa: E402

BASE_CHAPADA = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Subsolo_v2_16x9.png"
BASE_TEXTURAS = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Subsolo_v3_texturas_16x9.png"
COR_BEGE_BAHIA = 232                                    # #E8E8E8 na base chapada
FONTE_BEGE_BAHIA = (RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final2.png",
                    [(1350, 582, 1452, 848), (648, 636, 698, 848)])
DEGRAUS = {"x": (191, 336), "y": (386, 520)}            # degraus largos, até a floreira
PLANTAS = (300, 360, 400, 530)                          # onde ficam as plantas da floreira
PEDRA_L = (205, 246)                                    # luminância da pedra lisa no render
PINTA_MAX = 20                                          # px: mancha escura menor que isso é do mármore
LINHA_DIF = 10                                          # quanto a linha é mais escura que a pedra em volta
JANELA = 8                                              # px de cada lado da aresta no espelho


def alinhar(render):
    """Afim base 16:9 (reduzida a 2000 px) → render."""
    base = cv2.resize(cv2.imread(str(BASE_TEXTURAS)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(8000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    p1 = np.float32([k1[a.queryIdx].pt for a in pares])
    p2 = np.float32([k2[a.trainIdx].pt for a in pares])
    A, inl = cv2.estimateAffine2D(p1, p2, ransacReprojThreshold=2.0)
    print(f"    alinhamento: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return A


def area_bege_bahia(render, A):
    base = cv2.imread(str(BASE_CHAPADA))
    m = (np.abs(base.astype(np.int32) - COR_BEGE_BAHIA).max(axis=2) <= 4).astype(np.float32)
    m = cv2.resize(m, render.shape[1::-1], interpolation=cv2.INTER_AREA)
    m = cv2.warpAffine(m, A, render.shape[1::-1], flags=cv2.INTER_LINEAR)
    # fecha as linhas tracejadas e a seta da base (ficam dentro da área)
    return cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0


def plantas(render):
    a = render.astype(np.int32)
    b, g, r = a[..., 0], a[..., 1], a[..., 2]
    v = ((g > r + 3) & (g > b)) | (a.mean(axis=2) < 80)
    lim = np.zeros(v.shape, bool)
    x0, y0, x1, y1 = PLANTAS
    lim[y0:y1, x0:x1] = True
    v = ndimage.binary_fill_holes(ndimage.binary_closing(v & lim, iterations=2))
    return ndimage.binary_dilation(v, iterations=1)


def textura(forma, caixa):
    img = cv2.imread(str(FONTE_BEGE_BAHIA[0])).astype(np.float32)
    fontes = []
    for x0, y0, x1, y1 in FONTE_BEGE_BAHIA[1]:
        t = img[y0:y1, x0:x1]
        fontes += [np.ascontiguousarray(v) for v in (t, t[:, ::-1], t[::-1, :], t[::-1, ::-1])]
    x0, y0, x1, y1 = caixa
    tex = np.zeros(forma, np.float32)
    tex[y0:y1, x0:x1] = quilting(fontes, y1 - y0, x1 - x0, p=48, sobra=12, candidatos=1200)
    return tex


def relevo_degraus(L, livre):
    """Mapa multiplicativo dos degraus largos: arestas do render com o perfil espelhado."""
    x0, x1 = DEGRAUS["x"]
    y0, y1 = DEGRAUS["y"]
    K = np.ones(L.shape, np.float32)
    sub = np.where(livre[y0:y1, x0:x1], L[y0:y1, x0:x1], np.nan)
    m = np.nanmedian(sub, axis=1)
    escuras = np.nonzero(m < 180)[0]
    grupos = []
    for y in escuras:
        if grupos and y - grupos[-1][-1] <= 2:
            grupos[-1].append(y)
        else:
            grupos.append([y])
    for g in grupos:
        c = y0 + g[int(np.argmin(m[g]))]                   # a linha mais escura da aresta
        liso = np.nanmedian(m[c - y0 - 7:c - y0 - 2])      # piso liso logo acima (sem sombra)
        perfil = np.clip(m[c - y0 - JANELA:c - y0 + JANELA + 1] / liso, 0.45, 1.06)
        for d in range(-JANELA, JANELA + 1):                # linha c+d recebe o que estava em c-d
            K[c + d, x0:x1] *= perfil[JANELA - d]
    print(f"    degraus largos: {len(grupos)} arestas com a sombra virada para o pátio")
    return K


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    a = orig.astype(np.float32)
    L = a.mean(axis=2)
    print("[1] áreas de Bege Bahia")
    A = alinhar(orig)
    area = area_bege_bahia(orig, A)
    verde = plantas(orig)
    area &= ~verde
    ys, xs = np.nonzero(area)
    caixa = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    print("[2] linhas que ficam (contornos, porta do depósito)")
    x0, x1 = DEGRAUS["x"]
    y0, y1 = DEGRAUS["y"]
    deg = np.zeros(area.shape, bool)
    deg[y0:y1, x0:x1] = True
    deg &= area
    # traço mais escuro que a pedra em volta (mediana local, sem as nuvens do mármore); as
    # pintinhas e os veios finos do mármore do render saem, as linhas (compridas) ficam
    med = np.median(L[area])
    fundo = cv2.medianBlur(np.where(area & (L > 200) & (L < 246), L, med).astype(np.uint8), 11)
    escuro = area & ~deg & (L < fundo.astype(np.float32) - LINHA_DIF)
    junto = ndimage.binary_closing(escuro, structure=np.ones((3, 3))) | escuro
    lab, n = ndimage.label(junto, structure=np.ones((3, 3)))
    tam = ndimage.sum(junto, lab, range(1, n + 1))
    linhas = ndimage.binary_dilation(np.isin(lab, np.nonzero(tam > PINTA_MAX)[0] + 1), iterations=1)
    print(f"    {int((tam > PINTA_MAX).sum())} linhas, {int((tam <= PINTA_MAX).sum())} pintinhas")
    pedra = area & ~linhas & (L <= PEDRA_L[1]) & (a[..., 2] >= a[..., 1] - 2)
    tom_render = np.median(a[pedra & (L >= PEDRA_L[0])], axis=0)

    print("[3] textura do Bege Bahia aprovado")
    T = textura(a.shape, caixa)
    print(f"    render {tom_render[::-1].round()} → aprovado {np.median(T[pedra], axis=0)[::-1].round()} (RGB)")

    print("[4] arestas dos degraus largos")
    K = relevo_degraus(L, deg)

    out = a.copy()
    troca = pedra | deg
    out[troca] = (T * K[..., None])[troca]
    # bordas: linha ou fundo branco misturados com a pedra; só a parte da pedra muda de tom
    anel = ndimage.binary_dilation(area, iterations=2) & ~troca & ~verde
    ls = tom_render.mean()
    w = np.where(L < ls, np.clip((L - 110) / (ls - 110), 0, 1), np.clip((255 - L) / (255 - ls), 0, 1))
    w[~anel] = 0
    out += (T - tom_render) * w[..., None] * (T.sum(axis=2) > 0)[..., None]
    out = np.clip(out, 0, 255).astype(np.uint8)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[5] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

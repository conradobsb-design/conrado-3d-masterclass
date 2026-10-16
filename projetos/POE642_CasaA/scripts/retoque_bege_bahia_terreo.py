#!/usr/bin/env python3
"""Iguala o Bege Bahia do render do Térreo ao do 1º Pavimento, sem mexer em mais nada.

As áreas de Bege Bahia são as do cinza-claro #E8E8E8 da base v6 do Térreo, alinhada ao
render por SIFT e transformação afim. São as pedras de acesso, o hall externo, o deck e a
varanda (onde não é travertino), a escada escalonada para o deck de madeira e o lance sob o
spa, que desce para o subsolo. Nessas áreas, a textura do render é trocada pela do mármore
das varandas do 1º Pavimento:

1. tecida por image quilting (Efros e Freeman), com recortes da varanda da suíte 1 e da
   varanda da suíte master, espelhados para variar os veios;
2. as linhas da base (bordas de degrau, tracejado do pergolado, contornos) ficam fora da
   troca, com folga de 2 px, e o desenho do render nesses pontos não muda;
3. a sombra suave do render (em volta das espreguiçadeiras, por exemplo) é mantida: a
   textura nova é escurecida onde o render original era mais escuro que o piso em volta.

Uso:
  python retoque_bege_bahia_terreo.py RENDER_TERREO BASE_TERREO_v6_16x9 RENDER_1PAV --saida PASTA
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

# trechos limpos de Bege Bahia no render do 1º Pavimento (px num render de 2000 px)
FONTES_1PAV = [(1350, 582, 1452, 848),   # varanda da suíte 1
               (648, 636, 698, 848)]     # varanda da suíte master
BEGE_LEGENDA = 232                       # #E8E8E8 na base


def afim(origem, destino):
    sift = cv2.SIFT_create(12000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(origem, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(destino, cv2.COLOR_BGR2GRAY), None)
    bons = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.75 * b.distance]
    src = np.float32([k1[m.queryIdx].pt for m in bons])
    dst = np.float32([k2[m.trainIdx].pt for m in bons])
    A, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=2.5)
    res = np.linalg.norm(src @ A[:, :2].T + A[:, 2] - dst, axis=1)[inl.ravel() == 1]
    print(f"    {int(inl.sum())} pontos, erro mediano {np.median(res):.2f} px")
    return A


def costura_minima(erro):
    """Caminho vertical de menor erro (programação dinâmica) -> máscara à esquerda do corte."""
    h, w = erro.shape
    custo = erro.copy()
    for i in range(1, h):
        esq = np.r_[np.inf, custo[i - 1, :-1]]
        dir_ = np.r_[custo[i - 1, 1:], np.inf]
        custo[i] += np.minimum(np.minimum(esq, custo[i - 1]), dir_)
    caminho = np.zeros(h, int)
    caminho[-1] = int(np.argmin(custo[-1]))
    for i in range(h - 2, -1, -1):
        j = caminho[i + 1]
        lo, hi = max(0, j - 1), min(w, j + 2)
        caminho[i] = lo + int(np.argmin(custo[i, lo:hi]))
    mask = np.zeros((h, w), bool)
    for i, j in enumerate(caminho):
        mask[i, :j] = True
    return mask


def quilting(fontes, alto, largo, p=36, sobra=10, candidatos=500, rng=None):
    rng = rng or np.random.default_rng(642)
    passo = p - sobra
    ny = int(np.ceil((alto - sobra) / passo))
    nx = int(np.ceil((largo - sobra) / passo))
    out = np.zeros((ny * passo + sobra, nx * passo + sobra, 3), np.float32)
    pos = [(k, y, x) for k, f in enumerate(fontes)
           for y in range(0, f.shape[0] - p + 1, 2) for x in range(0, f.shape[1] - p + 1, 2)]
    for iy in range(ny):
        for ix in range(nx):
            y, x = iy * passo, ix * passo
            esc = [pos[i] for i in rng.integers(0, len(pos), candidatos)]
            blocos = np.stack([fontes[k][yy:yy + p, xx:xx + p] for k, yy, xx in esc])
            alvo = out[y:y + p, x:x + p]
            erro = np.zeros(len(esc), np.float32)
            if ix > 0:
                erro += ((blocos[:, :, :sobra] - alvo[None, :, :sobra]) ** 2).sum(axis=(1, 2, 3))
            if iy > 0:
                erro += ((blocos[:, :sobra, :] - alvo[None, :sobra, :]) ** 2).sum(axis=(1, 2, 3))
            if ix == 0 and iy == 0:
                escolha = 0
            else:
                ok = np.nonzero(erro <= erro.min() * 1.1 + 1e-6)[0]
                escolha = int(rng.choice(ok))
            bloco = blocos[escolha].copy()
            usar = np.ones((p, p), bool)
            if ix > 0:
                e = ((bloco[:, :sobra] - alvo[:, :sobra]) ** 2).sum(axis=2)
                usar[:, :sobra] &= ~costura_minima(e)
            if iy > 0:
                e = ((bloco[:sobra, :] - alvo[:sobra, :]) ** 2).sum(axis=2).T
                usar[:sobra, :] &= ~costura_minima(e).T
            alvo[usar] = bloco[usar]
    return out[:alto, :largo]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render_terreo", type=Path)
    ap.add_argument("base_terreo", type=Path)
    ap.add_argument("render_1pav", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    args = ap.parse_args()

    r = cv2.imread(str(args.render_terreo))
    H, W = r.shape[:2]
    e = W / 2000
    base = cv2.imread(str(args.base_terreo))
    s = W / base.shape[1]
    base_red = cv2.resize(base, (W, round(base.shape[0] * s)), interpolation=cv2.INTER_AREA)
    print("[1] alinhando a base v6 ao render do Térreo")
    A = afim(base_red, r)
    bw = cv2.warpAffine(base_red, A, (W, H), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255)).astype(int)

    print("[2] áreas de Bege Bahia da base")
    bege = (np.abs(bw - BEGE_LEGENDA).max(axis=2) <= 6).astype(np.uint8)
    n, rot, st, _ = cv2.connectedComponentsWithStats(bege, 8)
    area_min = int(800 * e * e)        # tira os respingos do mesmo cinza nos móveis de dentro da casa
    grandes = np.isin(rot, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= area_min])
    # a base diz ONDE é Bege Bahia; o contorno exato vem do próprio render (o piso claro do
    # render), para a troca chegar até a borda das pedras sem deixar moldura do piso antigo
    regiao = cv2.morphologyEx(grandes.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cheio = regiao.copy()
    contornos, _ = cv2.findContours(regiao, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(cheio, contornos, -1, 1, thickness=cv2.FILLED)
    buracos = cheio.astype(bool) & ~regiao.astype(bool)            # móveis sobre o piso (espreguiçadeiras)
    perto = cv2.dilate(regiao, np.ones((7, 7), np.uint8)).astype(bool)
    regiao_ext = cv2.dilate(regiao, np.ones((5, 5), np.uint8)).astype(bool)
    perto &= ~cv2.dilate(buracos.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    rf = r.astype(int)
    lum_r = rf.mean(axis=2)
    claro = (lum_r >= 192) & (rf.max(axis=2) - rf.min(axis=2) <= 32) & (rf[..., 2] >= rf[..., 0] - 2)
    # traço escuro do render só fica se for desenho da base (borda de degrau, tracejado do
    # pergolado, contorno); as pintas escuras do piso antigo, que a base não tem, saem
    linhas_base = cv2.dilate((bw.min(axis=2) < 200).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    linha_r = cv2.dilate(((lum_r < 185) & linhas_base).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    mascara = perto & claro & ~linha_r
    # só o que encosta na área da base (descarta manchas claras soltas fora dela)
    n2, rot2, _, _ = cv2.connectedComponentsWithStats(mascara.astype(np.uint8), 8)
    tocam = np.unique(rot2[mascara & regiao.astype(bool)])
    mascara = np.isin(rot2, tocam[tocam > 0])
    # as pintas escuras do piso antigo também saem: manchinhas pequenas e soltas, longe de
    # qualquer linha da base (borda de degrau, tracejado e contorno ficam)
    escuro = (perto & ~claro & ~linhas_base).astype(np.uint8)
    n3, rot3, st3, _ = cv2.connectedComponentsWithStats(escuro, 8)
    lado_max = max(3, int(round(9 * e)))
    pintas = [i for i in range(1, n3) if st3[i, cv2.CC_STAT_AREA] <= 45 * e * e
              and max(st3[i, cv2.CC_STAT_WIDTH], st3[i, cv2.CC_STAT_HEIGHT]) <= lado_max]
    pintas = cv2.dilate(np.isin(rot3, pintas).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    mascara |= pintas & regiao_ext & ~linhas_base
    print(f"    {int(mascara.sum())} px")

    print("[3] tecendo a textura do 1º Pavimento")
    p1 = cv2.imread(str(args.render_1pav)).astype(np.float32)
    e1 = p1.shape[1] / 2000
    fontes = []
    for x0, y0, x1, y1 in FONTES_1PAV:
        f = p1[int(y0 * e1):int(y1 * e1), int(x0 * e1):int(x1 * e1)]
        fontes += [f, f[:, ::-1], f[::-1, :], f[::-1, ::-1]]
    ys, xs = np.nonzero(mascara)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    textura = quilting(fontes, y1 - y0, x1 - x0, p=int(36 * e1), sobra=int(10 * e1))

    print("[4] aplicando com a sombra suave do render")
    lum = r.astype(np.float32).mean(axis=2)
    m = mascara.astype(np.float32)
    # média só sobre o piso: a grama e a água em volta não escurecem a borda das pedras
    viz = cv2.GaussianBlur(lum * m, (0, 0), 4 * e) / np.maximum(cv2.GaussianBlur(m, (0, 0), 4 * e), 1e-3)
    ref = float(np.median(lum[mascara]))
    sombra = np.clip(viz / ref, 0.86, 1.0)[..., None]
    novo = r.astype(np.float32).copy()
    novo[y0:y1, x0:x1] = textura
    novo *= sombra
    alfa = cv2.GaussianBlur(mascara.astype(np.float32), (0, 0), 0.7)[..., None]
    out = (r * (1 - alfa) + novo * alfa).clip(0, 255).astype(np.float32)
    # o piso que fica entre as linhas (degraus estreitos, bordas) recebe só o tom novo,
    # para não sobrar o rosado antigo ao lado da textura nova; as linhas escuras não mudam
    delta = textura.reshape(-1, 3).mean(axis=0) - r[mascara].reshape(-1, 3).mean(axis=0)
    resto = perto & ~mascara & (lum_r >= 170) & (rf.max(axis=2) - rf.min(axis=2) <= 32) & regiao_ext
    out[resto] += delta
    out = out.clip(0, 255).astype(np.uint8)
    alfa = np.maximum(alfa, resto[..., None].astype(np.float32))

    args.saida.mkdir(parents=True, exist_ok=True)
    nome = args.render_terreo.stem + "_bege"
    cv2.imwrite(str(args.saida / f"{nome}.png"), out)
    cv2.imwrite(str(args.saida / f"{nome}_camada.png"), np.dstack([out, (alfa[..., 0] * 255).astype(np.uint8)]))
    fora = (np.abs(out.astype(int) - r.astype(int)).max(axis=2) > 3) & ~cv2.dilate(mascara.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    print(f"[5] {args.saida / (nome + '.png')} ({W}x{H}); px alterados fora das áreas: {int(fora.sum())}")


if __name__ == "__main__":
    main()

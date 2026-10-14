#!/usr/bin/env python3
"""Retoque sem IA do render final do 1º Pavimento a partir da base v3, alinhada por SIFT.

1. Escada em U: o motor errou a linha de descida (as pontas viraram arcos de porta) e o
   número de degraus. As linhas do render saem por inpaint, e entram as linhas da base:
   degraus, linha de descida, círculo de partida e seta. A textura de travertino fica.
2. Escada caracol: na parte branca (os 3/4 do piso de baixo) entram as linhas da base,
   ou seja, os degraus, o arco central e as marcas. Entram também as bordas da abertura
   em volta.
3. Entorno: tudo fora do 1º pavimento (fora dos retângulos 'manter_bbox_vis' do
   esmaecer) passa a ser a base, esmaecida. Isso inclui as pedras de acesso ao hall
   externo, o pergolado tracejado, a piscina, o deck e os contornos.

Uso:
  python retoque_base_1pav.py RENDER BASE_V3_16x9 --saida PASTA [--config config_bases.json]
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
LARGURA_VIS = 1800
BASE_LARGURA_SEM_MARGEM = 6001


def afim(origem, destino, n=10000, razao=0.75, tol=2.5):
    sift = cv2.SIFT_create(n)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(origem, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(destino, cv2.COLOR_BGR2GRAY), None)
    bons = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < razao * b.distance]
    src = np.float32([k1[m.queryIdx].pt for m in bons])
    dst = np.float32([k2[m.trainIdx].pt for m in bons])
    A, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=tol)
    res = np.linalg.norm(src @ A[:, :2].T + A[:, 2] - dst, axis=1)[inl.ravel() == 1]
    print(f"    {int(inl.sum())} pontos, erro mediano {np.median(res):.2f} px")
    return np.vstack([A, [0, 0, 1]])


def lum(img):
    return img.astype(np.float32).mean(axis=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("base", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--config", type=Path, default=AQUI / "config_bases.json")
    args = ap.parse_args()

    r = cv2.imread(str(args.render))
    base = cv2.imread(str(args.base))
    H, W = r.shape[:2]
    pav = json.loads(args.config.read_text())["pavimentos"]["1Pavimento"]

    print("[1] alinhando a base ao render")
    s = W / base.shape[1]
    base_red = cv2.resize(base, (W, round(base.shape[0] * s)), interpolation=cv2.INTER_AREA)
    A_b = afim(base_red, r)                              # base reduzida -> render
    T = A_b @ np.diag([s, s, 1])                         # base em px reais -> render
    # reduz primeiro com média (INTER_AREA) e só depois aplica a afim, quase identidade:
    # o warpAffine não faz média, e as linhas finas da base sumiriam aos pedaços
    bw = cv2.warpAffine(base_red, A_b[:2], (W, H), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))
    k = BASE_LARGURA_SEM_MARGEM / LARGURA_VIS
    margem = (base.shape[1] - BASE_LARGURA_SEM_MARGEM) / 2

    def vis_px(x, y):
        return (T @ np.array([x * k + margem, y * k, 1]))[:2]

    esc = np.sqrt(abs(np.linalg.det(T[:2, :2]))) * k     # px do render por unidade da prévia
    out = r.copy()
    alterado = np.zeros((H, W), bool)

    # 2. escada em U -------------------------------------------------------------------
    print("[2] escada em U: linhas da base sobre o travertino do render")
    x0, y0 = vis_px(1080, 481)
    x1, y1 = vis_px(1231, 597)
    x0, y0, x1, y1 = int(x0), int(y0), int(np.ceil(x1)), int(np.ceil(y1))
    trav_base = np.array([202, 217, 220], np.float32)  # #DCD9CA em BGR
    sub_b = bw[y0:y1, x0:x1].astype(np.float32)
    perto = np.abs(sub_b - trav_base).max(axis=2) < 14
    linha_b = (lum(bw[y0:y1, x0:x1]) < 200) & ((sub_b.max(axis=2) - sub_b.min(axis=2)) < 30)
    # área do degrau: travertino da base com as linhas entre um degrau e outro
    area = cv2.morphologyEx((perto | linha_b).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    vazio = lum(bw[y0:y1, x0:x1]) < 95                # cinza-escuro dos vazios e paredes
    area = area.astype(bool) & ~cv2.dilate(vazio.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    sub_r = out[y0:y1, x0:x1]
    # as linhas do render também são apagadas numa faixa em volta da área (as pontas dos degraus
    # encostam na borda clara da escada), sem tocar no cinza-escuro dos vazios
    limpar = cv2.dilate(area.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (lum(sub_r) > 150)
    mediana = cv2.medianBlur(sub_r, 7).astype(np.float32)
    linhas_r = ((lum(mediana) - lum(sub_r)) > 10) & limpar
    linhas_r = cv2.dilate(linhas_r.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & limpar
    cor_linha = np.array([98, 104, 112], np.float32)   # cinza-taupe escuro, o mesmo tom das linhas do render (BGR)
    limpo = cv2.inpaint(sub_r, linhas_r.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    # linhas da base medidas na resolução cheia: o traço de 2 px vira cobertura parcial no render,
    # que é reforçada para a linha ficar com o peso das linhas do render
    lb = lum(base)
    neutro_b = (base.max(axis=2).astype(int) - base.min(axis=2)) < 30
    linha_full = ((lb > 90) & (lb < 200) & neutro_b).astype(np.float32)
    linha_red = cv2.resize(linha_full, (base_red.shape[1], base_red.shape[0]), interpolation=cv2.INTER_AREA)
    cobertura = cv2.warpAffine(linha_red, A_b[:2], (W, H), flags=cv2.INTER_LINEAR)[y0:y1, x0:x1]
    alfa = np.clip(cobertura * 1.7, 0, 0.85)[..., None] * area[..., None]
    novo = limpo.astype(np.float32) * (1 - alfa) + cor_linha.astype(np.float32) * alfa
    out[y0:y1, x0:x1] = np.where(area[..., None], novo, limpo).astype(np.uint8)
    alterado[y0:y1, x0:x1] |= area | linhas_r
    print(f"    {int(linhas_r.sum())} px de linha do render apagados")

    # 3. escada caracol --------------------------------------------------------------
    print("[3] escada caracol: linhas da base na parte branca")
    circ = pav["esmaecer"]["clarear_circulos"][0]
    cx, cy = vis_px(*circ["centro_vis"])
    raio = 30.0 * esc
    yy, xx = np.ogrid[:H, :W]
    disco = (xx - cx) ** 2 + (yy - cy) ** 2 <= (raio - 1.2) ** 2
    quarto = (xx >= cx) & (yy <= cy)
    tres_quartos = disco & ~quarto
    out[tres_quartos] = bw[tres_quartos]
    alterado |= tres_quartos
    # bordas da abertura em volta (as linhas da base mais escuras que o piso)
    ax0, ay0 = vis_px(896.7, 808.2)
    ax1, ay1 = vis_px(966.5, 877.6)
    aberta = np.zeros((H, W), bool)
    aberta[int(ay0):int(np.ceil(ay1)), int(ax0):int(np.ceil(ax1))] = True
    aberta &= ~((xx - cx) ** 2 + (yy - cy) ** 2 <= (raio + 1.5) ** 2)
    piso_b = 232.0
    lb = lum(bw)
    alfa = np.clip((piso_b - lb) / (piso_b - 120) * 1.5, 0, 1) * aberta
    neutro = (bw.max(axis=2).astype(int) - bw.min(axis=2)) < 12
    alfa *= neutro
    out = (out.astype(np.float32) * (1 - alfa[..., None]) + np.array([120, 118, 116], np.float32) * alfa[..., None]).astype(np.uint8)
    alterado |= alfa > 0.05

    # 4. entorno = base --------------------------------------------------------------
    print("[4] entorno: base esmaecida fora do 1º pavimento")
    manter = np.zeros((H, W), np.uint8)
    for bx0, by0, bx1, by1 in pav["esmaecer"]["manter_bbox_vis"]:
        p = np.array([vis_px(bx0, by0), vis_px(bx1, by0), vis_px(bx1, by1), vis_px(bx0, by1)], np.int32)
        cv2.fillConvexPoly(manter, p, 1)
    fora = cv2.GaussianBlur((1 - manter).astype(np.float32), (0, 0), 0.6)[..., None]
    out = (out.astype(np.float32) * (1 - fora) + bw.astype(np.float32) * fora).astype(np.uint8)
    alterado |= fora[..., 0] > 0.02

    args.saida.mkdir(parents=True, exist_ok=True)
    nome = args.render.stem.replace("_final", "") + "_final2"
    cv2.imwrite(str(args.saida / f"{nome}.png"), out)
    cv2.imwrite(str(args.saida / f"{nome}_camada.png"),
                np.dstack([out, (alterado * 255).astype(np.uint8)]))
    print(f"[5] {args.saida / (nome + '.png')} ({W}x{H})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Leva os elementos de um render para a base em alta resolução: a base vira a imagem final.

O motor devolve a planta em 2K, e a casa ocupa só uma parte do quadro, então os detalhes ficam
pequenos. A base tem a mesma folha em 6905 px, com paredes, vidros, portas e escadas nítidas e
fiéis ao PDF. Este script mantém a base como imagem final e só traz do render o que ele
acrescentou de bom: os objetos fotorrealistas (aparelhos, louças, bancadas, elevador).

1. Alinha o render à base 16:9 (SIFT + afim) e o leva para a resolução da base (Lanczos).
2. Apaga da base os desenhos que serão trocados (aparelhos e louças em traço), refazendo o piso
   por image quilting a partir de um trecho limpo do mesmo piso.
3. Recorta cada objeto do render (máscara por cor: os aparelhos são neutros sobre a madeira; as
   louças, claras sobre a pedra), gira ou espelha quando a base desenha em outra posição, e
   cola no retângulo exato que a base ocupa.
4. 'copiar' traz um trecho do render tal como está (ex.: a cabine do elevador), só onde a base é
   branca dentro do retângulo, para as paredes da base continuarem nítidas.
5. Onde o render não tem um elemento para trocar, fica o que a base tem (chuveiros, peças
   brancas, projeções, o entorno esmaecido, as escadas).

A config fica em config_bases.json, no pavimento, na chave 'elementos_do_render'; os
retângulos estão na prévia de 1800 px (vis).

Uso:
  python elementos_do_render.py PAVIMENTO RENDER BASE_16x9 --config CONFIG.json --saida PASTA --nome NOME
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

from texturizar_base import quilting

AQUI = Path(__file__).resolve().parent
BASE_SEM_MARGEM = 6001


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento")
    ap.add_argument("render", type=Path)
    ap.add_argument("base", type=Path, help="base 16:9 (a que foi para o motor)")
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text())
    op = cfg["pavimentos"][args.pavimento]["elementos_do_render"]
    base = cv2.imread(str(args.base))
    H, W = base.shape[:2]
    k = BASE_SEM_MARGEM / cfg["largura_visualizacao"] * H / 3884
    margem = (W - BASE_SEM_MARGEM * H / 3884) / 2

    def px(b):
        x0, y0, x1, y1 = b
        return int(round(x0 * k + margem)), int(round(y0 * k)), int(round(x1 * k + margem)), int(round(y1 * k))

    print("[1] alinhando o render à base")
    r = cv2.imread(str(args.render))
    s = r.shape[1] / W
    A = afim(cv2.resize(base, (r.shape[1], round(H * s)), interpolation=cv2.INTER_AREA), r)
    T = np.vstack([A, [0, 0, 1]]) @ np.diag([s, s, 1])
    rw = cv2.warpAffine(r, np.linalg.inv(T)[:2], (W, H), flags=cv2.INTER_LANCZOS4, borderValue=(255, 255, 255))
    borrado = cv2.GaussianBlur(rw, (0, 0), 2.0)
    rw = cv2.addWeighted(rw, 1.6, borrado, -0.6, 0)          # nitidez depois da ampliação

    out = base.astype(np.float32)

    print("[2] apagando os desenhos que serão trocados")
    for ap_ in op.get("apagar", []):
        alvo = np.zeros((H, W), np.uint8)
        for b in ap_["bbox_vis"]:
            x0, y0, x1, y1 = px(b)
            alvo[y0:y1, x0:x1] = 1
        # o desenho é o que não é piso dentro do retângulo: diferença para o piso de origem
        fx0, fy0, fx1, fy1 = px(ap_["piso_vis"])
        fonte = base[fy0:fy1, fx0:fx1].astype(np.float32)
        ys, xs = np.nonzero(alvo)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        p = min(48, fonte.shape[0] - 1, fonte.shape[1] - 1)
        tex = quilting([fonte, fonte[::-1, :]] if ap_.get("so_espelho_vertical", True) else [fonte], y1 - y0, x1 - x0,
                       p=p, sobra=max(6, p // 4))
        m = alvo[y0:y1, x0:x1].astype(bool)
        out[y0:y1, x0:x1][m] = tex[m]
        print(f"    {ap_['nome']}: {int(m.sum())} px")

    print("[2b] bancadas brancas da base em quartzo claro")
    for pt in op.get("pintar", []):
        x0, y0, x1, y1 = px(pt["bbox_vis"])
        bloco = base[y0:y1, x0:x1].astype(np.int32)
        m = bloco.min(axis=2) >= pt.get("so_onde_base_clara", 235)
        cor = np.array([int(pt["cor"][5:7], 16), int(pt["cor"][3:5], 16), int(pt["cor"][1:3], 16)], np.float32)
        ruido = np.random.default_rng(7).normal(0, 2.0, m.shape)[..., None]   # pontilhado sutil do quartzo
        out[y0:y1, x0:x1][m] = (cor + ruido)[m]
        print(f"    {pt['nome']}: {int(m.sum())} px")

    print("[3] colando os objetos do render")
    hsv = cv2.cvtColor(rw, cv2.COLOR_BGR2HSV).astype(np.int32)
    lum = rw.astype(np.float32).mean(axis=2)
    for el in op.get("objetos", []):
        x0, y0, x1, y1 = px(el["de_vis"])
        sub, sh, sl = rw[y0:y1, x0:x1].astype(np.float32), hsv[y0:y1, x0:x1], lum[y0:y1, x0:x1]
        if el.get("mascara") == "neutro":            # aparelhos: neutros (preto, grafite, cromo) sobre madeira
            m = (sh[..., 1] < el.get("sat_max", 70)) | (sl < 80)
        elif el.get("mascara") == "claro":           # louças: brancas sobre pedra
            # limiar de Otsu entre a louça e o piso (as paredes pretas ficam de fora da conta)
            v = sl[sl > 60].astype(np.uint8)
            lim, _ = cv2.threshold(v.reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            m = (sl > el.get("lum_min", lim)) & (sh[..., 1] < 45)
        else:                                        # retângulo inteiro (ex.: bancada com cuba)
            m = np.ones(sl.shape, bool)
        if el.get("mascara") in ("neutro", "claro"):
            m = ndimage.binary_closing(m, iterations=3)
            m = ndimage.binary_fill_holes(m)
            lab, n = ndimage.label(m)
            if n > 1:
                tam = ndimage.sum(m, lab, range(1, n + 1))
                m = np.isin(lab, [i + 1 for i, t in enumerate(tam) if t >= 0.08 * tam.max()])
        alfa = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
        spr = np.dstack([sub, alfa])
        g = el.get("girar", 0) // 90
        if g:
            spr = np.rot90(spr, -g)                   # girar no sentido horário
        if el.get("espelhar"):
            spr = spr[:, ::-1]
        for alvo in el["para_vis"]:
            tx0, ty0, tx1, ty1 = px(alvo)
            peca = cv2.resize(np.ascontiguousarray(spr), (tx1 - tx0, ty1 - ty0), interpolation=cv2.INTER_CUBIC)
            a = np.clip(peca[..., 3:4], 0, 1)
            out[ty0:ty1, tx0:tx1] = out[ty0:ty1, tx0:tx1] * (1 - a) + peca[..., :3] * a
        print(f"    {el['nome']}: {len(el['para_vis'])}x")

    print("[4] trechos copiados do render")
    for cp in op.get("copiar", []):
        x0, y0, x1, y1 = px(cp["bbox_vis"])
        bloco = base[y0:y1, x0:x1].astype(np.int32)
        m = (bloco.min(axis=2) >= cp.get("so_onde_base_clara", 235))
        m = ndimage.binary_erosion(m, iterations=2)
        a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)[..., None]
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + rw[y0:y1, x0:x1] * a
        print(f"    {cp['nome']}: {int(m.sum())} px")

    args.saida.mkdir(parents=True, exist_ok=True)
    final = np.clip(out, 0, 255).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), final)
    print(f"[5] {args.saida / (args.nome + '.png')} ({W}x{H})")


if __name__ == "__main__":
    main()

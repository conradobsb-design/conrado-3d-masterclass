#!/usr/bin/env python3
"""Prévia de texturas na base: troca as cores chapadas da legenda pelas texturas aprovadas.

Cada cor da legenda (ex.: #E8E8E8 Bege Bahia) é preenchida com a textura do mesmo material
tirada de um render já aprovado (ex.: as varandas do 1º Pavimento da Casa A). Assim o motor
recebe na própria base o aspecto de cada piso, e não só uma cor.

- Só mudam os pixels da cor da legenda, e só dentro das áreas com cor cheia ('manter_bbox_vis'
  do passo de esmaecer): linhas, paredes, vidros, portas, móveis e o entorno esmaecido ficam.
- A textura é tecida por image quilting (Efros e Freeman) a partir dos trechos de origem, na
  escala do render (a base tem a mesma folha, em resolução maior), e depois ampliada.
- 'escurecer' deixa um tom um pouco mais escuro (ex.: o banco da sauna, para continuar se
  lendo como banco).

A config fica em config_bases.json, no pavimento, na chave 'texturas'.

Uso:
  python texturizar_base.py PAVIMENTO BASE.png --config CONFIG.json --saida PASTA
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
LARGURA_RENDER = 2000              # escala dos trechos de origem (renders aprovados)
LARGURA_16x9 = 6905                # a mesma folha na base 16:9
BASE_SEM_MARGEM = 6001             # a base antes da margem 16:9


def hex_bgr(h):
    h = h.lstrip("#")
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.int32)


def costura_minima(erro):
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


def quilting(fontes, alto, largo, p=36, sobra=10, candidatos=400, rng=None):
    rng = rng or np.random.default_rng(642)
    passo = p - sobra
    ny = max(1, int(np.ceil((alto - sobra) / passo)))
    nx = max(1, int(np.ceil((largo - sobra) / passo)))
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
            escolha = 0 if ix == 0 and iy == 0 else int(rng.choice(np.nonzero(erro <= erro.min() * 1.1 + 1e-6)[0]))
            bloco = blocos[escolha].copy()
            usar = np.ones((p, p), bool)
            if ix > 0:
                usar[:, :sobra] &= ~costura_minima(((bloco[:, :sobra] - alvo[:, :sobra]) ** 2).sum(axis=2))
            if iy > 0:
                usar[:sobra, :] &= ~costura_minima(((bloco[:sobra, :] - alvo[:sobra, :]) ** 2).sum(axis=2).T).T
            alvo[usar] = bloco[usar]
    return out[:alto, :largo]


def em_16x9(img):
    h, w = img.shape[:2]
    nw = round(h * 16 / 9) if w / h < 16 / 9 else w
    nh = h if w / h < 16 / 9 else round(w * 9 / 16)
    tela = np.full((nh, nw, 3), 255, np.uint8)
    tela[(nh - h) // 2:(nh - h) // 2 + h, (nw - w) // 2:(nw - w) // 2 + w] = img
    return tela


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento")
    ap.add_argument("base", type=Path, help="base sem margem (ex.: ..._BASE_Subsolo_v2.png)")
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", default=None, help="nome do arquivo de saída, sem extensão")
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text())
    pav = cfg["pavimentos"][args.pavimento]
    base = cv2.imread(str(args.base))
    H, W = base.shape[:2]
    vis = W / cfg["largura_visualizacao"]
    # px da base por px do render aprovado: a folha inteira tem 2000 px no render e 6905 px na base 16:9
    fator = LARGURA_16x9 / LARGURA_RENDER * W / BASE_SEM_MARGEM

    # sem entorno esmaecido (ex.: o Térreo), a planta inteira tem cor cheia
    permitido = np.zeros((H, W), bool) if "esmaecer" in pav else np.ones((H, W), bool)
    for x0, y0, x1, y1 in pav.get("esmaecer", {}).get("manter_bbox_vis", []):
        permitido[int(y0 * vis):int(np.ceil(y1 * vis)), int(x0 * vis):int(np.ceil(x1 * vis))] = True

    out = base.astype(np.float32)
    bi = base.astype(np.int32)
    tol = pav["texturas"].get("tolerancia", 12)
    for mat in pav["texturas"]["materiais"]:
        mask = np.zeros((H, W), bool)
        for cor in mat["cores"]:
            mask |= np.abs(bi - hex_bgr(cor)).max(axis=2) <= tol
        mask &= permitido
        if "bbox_vis" in mat:
            lim = np.zeros((H, W), bool)
            x0, y0, x1, y1 = mat["bbox_vis"]
            lim[int(y0 * vis):int(np.ceil(y1 * vis)), int(x0 * vis):int(np.ceil(x1 * vis))] = True
            mask &= lim
        if not mask.any():
            print(f"{mat['nome']}: nenhuma área")
            continue
        fontes = []
        for f in mat["fontes"]:
            img = cv2.imread(str(RAIZ / f["arquivo"])).astype(np.float32)
            e = img.shape[1] / LARGURA_RENDER
            for x0, y0, x1, y1 in f["bbox"]:
                t = img[int(y0 * e):int(y1 * e), int(x0 * e):int(x1 * e)]
                if e != 1:
                    t = cv2.resize(t, (round(t.shape[1] / e), round(t.shape[0] / e)), interpolation=cv2.INTER_AREA)
                if mat.get("girar"):
                    t = np.rot90(t, mat["girar"] // 90)
                variantes = [t, t[::-1, :]] if mat.get("so_espelho_vertical") else [t, t[:, ::-1], t[::-1, :], t[::-1, ::-1]]
                fontes += [np.ascontiguousarray(v) for v in variantes]
        ys, xs = np.nonzero(mask)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        alto, largo = int(np.ceil((y1 - y0) / fator)) + 2, int(np.ceil((x1 - x0) / fator)) + 2
        p = min(36, min(f.shape[0] for f in fontes) - 1, min(f.shape[1] for f in fontes) - 1)
        tex = quilting(fontes, alto, largo, p=p, sobra=max(4, p // 4))
        tex = cv2.resize(tex, (round(largo * fator), round(alto * fator)), interpolation=cv2.INTER_CUBIC)[:y1 - y0, :x1 - x0]
        tex *= mat.get("escurecer", 1.0)
        sub = out[y0:y1, x0:x1]
        m = mask[y0:y1, x0:x1]
        sub[m] = tex[m]
        print(f"{mat['nome']}: {int(mask.sum())} px")

    out = np.clip(out, 0, 255).astype(np.uint8)
    args.saida.mkdir(parents=True, exist_ok=True)
    nome = args.nome or args.base.stem + "_texturas"
    cv2.imwrite(str(args.saida / f"{nome}.png"), out)
    cv2.imwrite(str(args.saida / f"{nome}_16x9.png"), em_16x9(out))
    print(args.saida / f"{nome}.png", f"({W}x{H})")


if __name__ == "__main__":
    main()

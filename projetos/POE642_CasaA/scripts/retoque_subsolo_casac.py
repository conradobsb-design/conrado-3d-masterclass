#!/usr/bin/env python3
"""Retoque sem IA do render do Subsolo da Casa C (prompt v1). A imagem final é o render.

1. Marca vermelha: o traço que o usuário desenhou sobre os degraus largos sai, refeito com a
   mesma linha da imagem um pouco ao lado (os degraus são faixas horizontais iguais).
2. Sentido de descida dos degraus largos: o motor desenhou cada degrau com a linha escura e a
   sombra logo abaixo dela, o que lê como descida para baixo. A descida é para cima, rumo ao
   pátio (definido pelo usuário). Para cada aresta, a sombra de baixo é desfeita e a mesma
   sombra vai para cima da linha. A aresta vertical do L (junto ao caminho) recebe o mesmo
   tratamento: a sombra passa da direita para a esquerda.
   A escada curta numerada (esmaecida) não muda: o ajuste é só nos degraus largos da esquerda.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_subsolo_casac.py RENDER.webp --saida PASTA --nome NOME
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

DEGRAUS = {"x": (191, 329), "y": (374, 520)}          # degraus largos (sem a floreira)
ARESTA_V = {"x": 231, "y": (488, 570)}                # aresta vertical do L, junto ao caminho
SOMBRA = 7                                            # px de sombra junto a cada aresta


def tirar_vermelho(img):
    a = img.astype(int)
    red = (a[..., 2] > 140) & (a[..., 2] - a[..., 1] > 60) & (a[..., 2] - a[..., 0] > 60)
    red = cv2.dilate(red.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    x0, x1 = DEGRAUS["x"]
    out = img.copy()
    for y in np.nonzero(red.any(axis=1))[0]:
        xs = np.nonzero(red[y])[0]
        w = xs.max() - xs.min() + 6
        for x in xs:
            fx = x - w if x - w >= x0 + 1 else x + w
            out[y, x] = img[y, fx]
    print(f"    marca vermelha: {int(red.sum())} px")
    return out


def perfil(L, e, colunas):
    """Sombra média abaixo da aresta e: razão entre cada linha e o piso liso mais abaixo."""
    m = L[:, colunas].mean(axis=1)
    liso = m[e + 9:e + 13].mean()
    return np.clip(m[e + 1:e + 1 + SOMBRA] / liso, 0.5, 1.0)


def inverter_degraus(img):
    out = img.astype(np.float32)
    L = out.mean(axis=2)
    x0, x1 = DEGRAUS["x"]
    y0, y1 = DEGRAUS["y"]
    # arestas: linhas escuras (núcleo de 1 a 2 px) na média das colunas
    m = L[y0:y1, x0:x1].mean(axis=1)
    escuras = np.nonzero(m < 200)[0] + y0
    grupos = []
    for y in escuras:
        if grupos and y - grupos[-1][-1] <= 1:
            grupos[-1].append(y)
        else:
            grupos.append([y])
    arestas = []
    for g in grupos:
        # núcleo da linha: só as linhas quase tão escuras quanto a mais escura (a primeira linha
        # da sombra e o antisserrilhado de cima ficam de fora)
        mg = m[np.array(g) - y0]
        nucleo = [y for y, v in zip(g, mg) if v <= mg.min() + 15]
        e0, e1 = nucleo[0], nucleo[-1]
        colunas = [x for x in range(x0, x1) if L[e0:e1 + 1, x].min() < 185]
        if len(colunas) < 20:
            continue
        arestas.append((e0, e1, colunas, perfil(L, e1, colunas)))
    for e0, e1, colunas, r in arestas:                       # desfaz a sombra de baixo
        for d, k in enumerate(r, 1):
            out[e1 + d, colunas] /= k
    for e0, e1, colunas, r in arestas:                       # e põe a mesma sombra em cima
        for d, k in enumerate(r, 1):
            out[e0 - d, colunas] *= k
    print(f"    degraus largos: {len(arestas)} arestas com a sombra invertida")

    # aresta vertical do L: sombra da direita para a esquerda
    xa = ARESTA_V["x"]
    ya, yb = ARESTA_V["y"]
    linhas = [y for y in range(ya, yb) if L[y, xa] < 175]
    if linhas:
        mm = L[linhas].mean(axis=0)
        liso = mm[xa + 9:xa + 13].mean()
        r = np.clip(mm[xa + 1:xa + 1 + SOMBRA] / liso, 0.5, 1.0)
        for d, k in enumerate(r, 1):
            out[linhas, xa + d] /= k
        for d, k in enumerate(r, 1):
            out[linhas, xa - d] *= k
        print(f"    aresta vertical do L: {len(linhas)} linhas")
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    print("[1] marca vermelha")
    img = tirar_vermelho(orig)
    print("[2] sentido de descida dos degraus largos")
    img = inverter_degraus(img)
    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), img)
    print(f"[3] {args.saida / (args.nome + '.png')}")


if __name__ == "__main__":
    main()

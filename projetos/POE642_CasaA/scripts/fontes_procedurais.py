#!/usr/bin/env python3
"""Fontes de textura geradas por código, para materiais sem render aprovado de onde tirar o trecho.

Saem na escala dos renders (folha inteira com 2000 px de largura: ~3,2 cm por px), como os
trechos de renders que o texturizar_base.py usa; ele tece e amplia para a base.

- pedra portuguesa caramelo (Casa E, acesso de veículos): pedrinhas de ~6,5 cm em tons de caramelo,
  ocre e creme, com juntas finas de areia; desenhadas em 4 x (diagrama de Voronoi) e reduzidas;
- bronze fosco (Casa E, bancos): bronze escuro com escovado fino e manchas suaves.

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/fontes_procedurais.py POE642_CasaE/bases/fontes
"""
import sys
from pathlib import Path

import cv2
import numpy as np

CM_POR_PX = 3.2          # escala dos renders (2000 px de largura)


def pedra_portuguesa(lado=420, pedra_cm=6.5, ss=4, semente=642):
    rng = np.random.default_rng(semente)
    n = lado * ss
    passo = pedra_cm / CM_POR_PX * ss                     # px (em ss) entre centros de pedras
    gx, gy = np.meshgrid(np.arange(0, n + passo, passo), np.arange(0, n + passo, passo))
    pts = np.stack([gx.ravel(), gy.ravel()], 1) + rng.uniform(-0.42, 0.42, (gx.size, 2)) * passo
    # Voronoi: a pedra de cada px é o centro mais próximo (via rótulos de distância)
    marcas = np.zeros((n, n), np.int32)
    dentro = (pts[:, 0] >= 0) & (pts[:, 0] < n) & (pts[:, 1] >= 0) & (pts[:, 1] < n)
    pts = pts[dentro]
    sementes = np.ones((n, n), np.uint8)
    for i, (x, y) in enumerate(pts.astype(int)):
        sementes[y, x] = 0
        marcas[y, x] = i + 1
    _, lab = cv2.distanceTransformWithLabels(sementes, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(sementes == 0)
    idx = np.zeros(lab.max() + 1, np.int32)
    idx[lab[ys, xs]] = marcas[ys, xs]
    pedra = idx[lab]
    # cor de cada pedra: caramelo com variação, algumas ocre mais escuras e algumas creme
    paleta = np.array([[98, 148, 194], [78, 120, 166], [118, 166, 206], [150, 188, 216], [88, 136, 184]], np.float32)  # BGR
    pesos = np.array([0.42, 0.2, 0.18, 0.06, 0.14])
    escolha = rng.choice(len(paleta), size=len(pts) + 1, p=pesos)
    cores = paleta[escolha] * rng.uniform(0.94, 1.05, (len(pts) + 1, 1))
    img = cores[pedra]
    # juntas: a borda de cada pedra, em areia clara
    borda = (cv2.dilate(pedra.astype(np.float32), np.ones((3, 3))) != cv2.erode(pedra.astype(np.float32), np.ones((3, 3))))
    img[borda] = img[borda] * 0.55 + np.array([140, 168, 192], np.float32) * 0.45
    # leve relevo dentro de cada pedra (o centro um pouco mais claro)
    dist = cv2.distanceTransform((~borda).astype(np.uint8), cv2.DIST_L2, 3)
    img *= (0.95 + 0.05 * np.clip(dist / (passo * 0.35), 0, 1))[..., None]
    return cv2.resize(np.clip(img, 0, 255).astype(np.uint8), (lado, lado), interpolation=cv2.INTER_AREA)


def bronze_fosco(lado=240, semente=642):
    rng = np.random.default_rng(semente)
    base = np.array([74, 96, 118], np.float32)                 # BGR de #76604A
    escovado = cv2.GaussianBlur(rng.normal(0, 1, (lado, lado)).astype(np.float32), (0, 0), sigmaX=6, sigmaY=0.5)
    manchas = cv2.GaussianBlur(rng.normal(0, 1, (lado, lado)).astype(np.float32), (0, 0), 18)
    f = 1 + 0.015 * escovado / (escovado.std() + 1e-6) + 0.035 * manchas / (manchas.std() + 1e-6)
    return np.clip(base[None, None, :] * f[..., None], 0, 255).astype(np.uint8)


def em_2000(img):
    """Repete a fonte até 2000 px de largura: o texturizar_base.py lê a escala de cada arquivo pela
    largura (a de um render inteiro), e o trecho usado é o primeiro ladrilho (bbox 0, 0, lado, lado)."""
    return np.tile(img, (1, -(-2000 // img.shape[1]), 1))[:, :2000]


def main():
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(saida / "pedra_portuguesa_caramelo.png"), em_2000(pedra_portuguesa()))
    cv2.imwrite(str(saida / "bronze_fosco.png"), em_2000(bronze_fosco()))
    print(saida / "pedra_portuguesa_caramelo.png", saida / "bronze_fosco.png")


if __name__ == "__main__":
    main()

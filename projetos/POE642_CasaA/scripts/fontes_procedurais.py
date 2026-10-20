#!/usr/bin/env python3
"""Fontes de textura geradas por código, para materiais sem render aprovado de onde tirar o trecho.

Saem na escala dos renders (folha inteira com 2000 px de largura: ~3,2 cm por px), como os
trechos de renders que o texturizar_base.py usa; ele tece e amplia para a base.

- pedra portuguesa caramelo (Casa E, acesso de veículos): pedrinhas de ~6,5 cm em tons de caramelo,
  ocre e creme, com juntas finas de areia; desenhadas em 4 x (diagrama de Voronoi) e reduzidas;
- bronze fosco (Casa E, bancos): bronze escuro com escovado fino e manchas suaves;
- Barlavento (Portobello, linha que reproduz a pedra hijau, peças de 14,5 x 14,5 cm; Casa E,
  piscinas, pedido do usuário): `barlavento` devolve a textura relativa (média 1) de uma área já
  no tamanho do render: peças de tons verde-acinzentados e azulados alternados (variação sutil), grão
  fino dentro de cada peça e juntas finas um pouco mais escuras, sem manchas; o retoque multiplica
  pela cor da água e pela luz;
- quartzito Aura (Casa E, banhos do 1º Pavimento; a cor pêssego claro #EAD4BF da legenda do
  cliente): placas de 90 x 90 cm com variação sutil de tom, nuvens suaves e veios finos e fluidos
  (claros e alguns dourados), juntas finas um pouco mais escuras.

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/fontes_procedurais.py POE642_CasaE/bases/fontes
"""
import sys
from pathlib import Path

import cv2
import numpy as np

CM_POR_PX = 3.2          # escala dos renders (2000 px de largura)


def pedra_portuguesa(lado=420, pedra_cm=6.5, ss=4, semente=642, cm_por_px=CM_POR_PX, junta=None):
    """junta: None, as juntas finas de areia clara (base v3); ou (largura em px da imagem, fator de escurecimento), para
    a pedra se ler na imagem final, onde cada pedra tem poucos px."""
    rng = np.random.default_rng(semente)
    n = lado * ss
    passo = pedra_cm / cm_por_px * ss                     # px (em ss) entre centros de pedras
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
    k = 3 if junta is None else max(3, int(round(junta[0] * ss)) | 1)
    borda = (cv2.dilate(pedra.astype(np.float32), np.ones((k, k))) != cv2.erode(pedra.astype(np.float32), np.ones((k, k))))
    if junta is None:
        img[borda] = img[borda] * 0.55 + np.array([140, 168, 192], np.float32) * 0.45
    else:
        img[borda] = img[borda] * junta[1]
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


def barlavento(alto, largo, cm_por_px=CM_POR_PX, peca_cm=14.5, ss=8, semente=642):
    """Textura relativa (BGR, média 1) do Barlavento Caribbean visto sob a água, no tamanho alto x
    largo (px do render): grade de peças de peca_cm, cada uma num tom da pedra hijau (verde-acinzentado
    a azulado), com o grão fino da pedra e as juntas finas um pouco mais escuras."""
    rng = np.random.default_rng(semente)
    lado = peca_cm / cm_por_px * ss                       # px (em ss) por peça
    H, W = alto * ss, largo * ss
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    i, j = (yy // lado).astype(np.int32), (xx // lado).astype(np.int32)
    ni, nj = int(i.max()) + 1, int(j.max()) + 1
    # tons da hijau (BGR, relativos): verde-acinzentado, verde, azulado e um mais claro
    paleta = np.array([[1.00, 1.00, 1.00], [0.98, 1.005, 0.985], [1.02, 0.995, 0.96], [1.015, 1.02, 1.02],
                       [0.985, 0.985, 1.005]], np.float32)
    pesos = np.array([0.34, 0.24, 0.2, 0.12, 0.1])
    tom = paleta[rng.choice(len(paleta), size=(ni, nj), p=pesos)] * rng.uniform(0.975, 1.025, (ni, nj, 1)).astype(np.float32)
    img = tom[i, j]
    # mesclado da pedra: só o grão fino dentro da peça (sem manchas grandes nem pintas escuras: o
    # usuário achou que davam aspecto de sujo)
    for sigma, amp in ((0.18 * lado, 0.02), (0.06 * lado, 0.02)):
        r = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sigma)
        img *= (1 + amp * r / max(float(r.std()), 1e-6))[..., None]
    # juntas: 6% da peça em cada borda
    fy, fx = (yy % lado) / lado, (xx % lado) / lado
    junta = (np.minimum(np.minimum(fy, 1 - fy), np.minimum(fx, 1 - fx)) < 0.06)
    img[junta] *= 0.94
    img = cv2.resize(img, (largo, alto), interpolation=cv2.INTER_AREA)
    return img / img.reshape(-1, 3).mean(axis=0)


def quartzito_aura(lado=420, placa_cm=90.0, ss=4, semente=642):
    rng = np.random.default_rng(semente)
    n = lado * ss
    base = np.array([191, 212, 234], np.float32)               # BGR de #EAD4BF
    passo = placa_cm / CM_POR_PX * ss
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    i, j = (yy // passo).astype(np.int32), (xx // passo).astype(np.int32)
    tom = rng.uniform(0.99, 1.01, (int(i.max()) + 1, int(j.max()) + 1)).astype(np.float32)
    f = tom[i, j]
    nuvem = cv2.GaussianBlur(rng.normal(0, 1, (n, n)).astype(np.float32), (0, 0), 0.9 * passo)
    f = f * (1 + 0.010 * nuvem / max(float(nuvem.std()), 1e-6))
    # veios: faixas finas de um campo ondulado (direção de ~30 graus, deformado por ruído suave)
    ruido = cv2.GaussianBlur(rng.normal(0, 1, (n, n)).astype(np.float32), (0, 0), 1.2 * passo)
    ruido /= max(float(ruido.std()), 1e-6)
    campo = (-xx * np.sin(0.52) + yy * np.cos(0.52)) / (1.3 * passo) + 0.55 * ruido
    veio = np.exp(-((np.abs(np.sin(np.pi * campo))) / 0.03) ** 2)
    claro = veio * (cv2.GaussianBlur(rng.normal(0, 1, (n, n)).astype(np.float32), (0, 0), 0.25 * passo) > -0.2)
    img = base[None, None, :] * f[..., None]
    img = img + claro[..., None] * np.float32([14, 12, 9])                    # veios claros, creme
    dourado = veio * (cv2.GaussianBlur(rng.normal(0, 1, (n, n)).astype(np.float32), (0, 0), 0.25 * passo) > 1.1)
    img = img * (1 - 0.06 * dourado[..., None] * np.float32([1.6, 1.0, 0.4]))  # alguns dourados
    # juntas finas entre as placas (~0,6 cm)
    fy, fx = (yy % passo), (xx % passo)
    junta = np.minimum(np.minimum(fy, passo - fy), np.minimum(fx, passo - fx)) < 0.1 * ss
    img[junta] *= 0.93
    img = cv2.resize(img, (lado, lado), interpolation=cv2.INTER_AREA)
    return np.clip(img, 0, 255).astype(np.uint8)


def em_2000(img):
    """Repete a fonte até 2000 px de largura: o texturizar_base.py lê a escala de cada arquivo pela
    largura (a de um render inteiro), e o trecho usado é o primeiro ladrilho (bbox 0, 0, lado, lado)."""
    return np.tile(img, (1, -(-2000 // img.shape[1]), 1))[:, :2000]


def main():
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(saida / "pedra_portuguesa_caramelo.png"), em_2000(pedra_portuguesa()))
    cv2.imwrite(str(saida / "bronze_fosco.png"), em_2000(bronze_fosco()))
    cv2.imwrite(str(saida / "quartzito_aura.png"), em_2000(quartzito_aura()))
    print(saida / "pedra_portuguesa_caramelo.png", saida / "bronze_fosco.png", saida / "quartzito_aura.png")


if __name__ == "__main__":
    main()

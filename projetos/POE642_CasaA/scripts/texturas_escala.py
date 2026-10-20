#!/usr/bin/env python3
"""Texturas na escala real nos renders retocados, em qualquer casa (POE 642).

Regras do usuário (19/10/26, para todas as casas): "textura, imprescindível que seja representada na escala" (R1) e as
texturas de referência que devem "simular pedra, não porcelanato" (`projetos/_texturas/`).

`retexturizar(out, mascara, nome, px_por_m, forca)` troca o desenho do piso na máscara pelo da biblioteca, na escala do
render, e mantém a luz e a cor do lugar:
- a luz do lugar é a média local do próprio piso (convolução normalizada, raio ~25 cm), sem o que não é piso: o que é
  mais escuro que ela (traços, contornos de folhas, objetos, sombras de peças), com folga de 2 px; os riscos claros que
  o motor deixa (até +30) viram piso;
- o desenho é o da textura da biblioteca (`_texturas/texturas.textura`, na escala px_por_m), só o detalhe abaixo de
  ~25 cm (dividido pela média local dela), levemente suavizado (o grão abaixo de 1 px vira ruído), com a força dada;
- novo = luz do lugar x (1 + força x (detalhe - 1)), com a borda suave.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_texturas"))
from texturas import textura  # noqa: E402


def nconv(img, m, sig):
    return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]


def retexturizar(out, mascara, nome, px_por_m, forca=0.6, sig_m=0.25, semente=1, pronta=None, cor=None,
                 suavizar=0.8):
    """pronta: em vez da textura da biblioteca, uma função (alto, largo) -> textura BGR já na escala (ex.: o mesmo piso
    aprovado de outro pavimento da casa); o desenho inteiro dela entra (dividido pela média), não só o detalhe.
    cor: o tom médio do material (BGR); a luz do lugar é levada a ele, mantendo as variações de luz (sombras, cantos).
    suavizar: o desfoque do desenho (px), para o grão abaixo de 1 px não virar ruído."""
    im = out.astype(np.float32)
    m = cv2.erode(mascara.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    sig = sig_m * px_por_m
    L = nconv(im, m.astype(np.float32), sig)
    nao = ((L - im).max(axis=2) > 12) | ((im - L).max(axis=2) > 30)
    nao = cv2.dilate(nao.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    piso = m & ~nao
    if not piso.any():
        return out, 0
    L = nconv(im, piso.astype(np.float32), sig)
    if cor is not None:
        L = L / im[piso].mean(axis=0) * np.asarray(cor, np.float32)
    ys, xs = np.nonzero(piso)
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    if pronta is not None:
        T = pronta(by1 - by0, bx1 - bx0).astype(np.float32)
        det = T / T.reshape(-1, 3).mean(axis=0)
    else:
        T = textura(nome, px_por_m, by1 - by0, bx1 - bx0, semente=semente).astype(np.float32)
        det = (cv2.GaussianBlur(T, (0, 0), suavizar) if suavizar else T) / np.maximum(cv2.GaussianBlur(T, (0, 0), sig), 1)
    novo = im.copy()
    novo[by0:by1, bx0:bx1] = L[by0:by1, bx0:bx1] * (1 + forca * (det - 1))
    a = (cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 0.7) * piso)[..., None]
    return np.clip(im * (1 - a) + novo * a, 0, 255).astype(np.uint8), int(piso.sum())


def trocar_grama(out, mascara, px_por_m, cor=None, semente=1, sig_luz_m=1.5, sig_sombra_m=0.25, sombra_limiar=0.93,
                 suavizar=0.6):
    """A grama do motor (grão fino de carpete, manchas fora de escala) vira a da referência (`_texturas`, na escala):
    - a luz larga do lugar (raio sig_luz_m), levada ao tom `cor` (BGR), se dado;
    - as sombras (das plantas, dos muros): a razão entre a luz curta (sig_sombra_m) e a larga, só onde escurece mais que
      sombra_limiar (as manchas suaves do motor, de +-7%, saem; as sombras ficam);
    - o desenho inteiro da textura da biblioteca (grão e manchas de 0,5 a 1 m), dividido pela média larga dela.
    Ao contrário de `retexturizar`, nada da máscara é descartado por fugir da luz local (o grão da grama do motor foge
    em toda parte)."""
    im = out.astype(np.float32)
    m = mascara.astype(np.float32)
    Lg = nconv(im, m, sig_luz_m * px_por_m)
    Lc = nconv(im, m, sig_sombra_m * px_por_m)
    razao = (Lc.mean(axis=2) + 1) / (Lg.mean(axis=2) + 1)
    sombra = np.minimum(1.0, razao / sombra_limiar)
    if cor is not None:
        Lg = Lg / im[mascara].mean(axis=0) * np.asarray(cor, np.float32)
    ys, xs = np.nonzero(mascara)
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    T = textura("grama", px_por_m, by1 - by0, bx1 - bx0, semente=semente).astype(np.float32)
    if suavizar:
        T = cv2.GaussianBlur(T, (0, 0), suavizar)
    det = T / T.reshape(-1, 3).mean(axis=0)
    novo = im.copy()
    novo[by0:by1, bx0:bx1] = (Lg * sombra[..., None])[by0:by1, bx0:bx1] * det
    a = (cv2.GaussianBlur(m, (0, 0), 0.7) * m)[..., None]
    return np.clip(im * (1 - a) + novo * a, 0, 255).astype(np.uint8), int(mascara.sum())


def mascara_grama(out, gramado, croma=None):
    """A grama de verdade dentro do gramado da base (`gramado`, bool): sem as plantas e com a borda junto aos pisos.
    - plantas: o que não é grama (cor fora da da grama, escuro, claro ou com folhagem), em manchas de 120 px ou mais,
      só a mais de 4 px da borda do gramado (junto aos pisos a cor e a folhagem são falsas), fechadas (17 px) e com os
      vãos pequenos entre folhas (< 1500 px) incluídos;
    - grama: os px verdes no tom da grama, com a vizinhança medida só nos px verdes (a borda dos pisos não conta), até
      3 px fora do gramado da base; os buracos pequenos (< 120 px) no meio dela entram.
    croma: a cromaticidade (b, r) da grama; sem ela, a mediana dos px verdes do gramado."""
    from scipy import ndimage
    gramD = cv2.dilate(gramado.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    im = out.astype(np.float32)
    b, g, r = im[..., 0], im[..., 1], im[..., 2]
    Y = im.mean(axis=2)
    verde = (g > r + 4) & (g > b + 12) & (Y < 115)
    s0 = im.sum(axis=2) + 1
    if croma is None:
        sel = gramado & verde
        croma = (float(np.median(b[sel] / s0[sel])), float(np.median(r[sel] / s0[sel])))
    f = cv2.GaussianBlur(im, (0, 0), 0.8)
    s = f.sum(axis=2) + 1
    d = np.hypot(f[..., 0] / s - croma[0], f[..., 2] / s - croma[1])
    est = cv2.GaussianBlur(np.abs(cv2.GaussianBlur(Y, (0, 0), 1.0) - cv2.GaussianBlur(Y, (0, 0), 3.0)), (0, 0), 1.5)
    folha = (d >= 0.03) | (f.mean(axis=2) <= 35) | (f.mean(axis=2) >= 140) | (est >= 9)
    longe = cv2.distanceTransform(gramado.astype(np.uint8), cv2.DIST_L2, 5) > 4
    nao = cv2.morphologyEx((gramado & folha & longe).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(nao, 8)
    planta = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 120])
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))
    planta = cv2.morphologyEx(planta.astype(np.uint8), cv2.MORPH_CLOSE, k).astype(bool) & gramado
    buracos = ndimage.binary_fill_holes(planta) & ~planta
    n, lab, st, _ = cv2.connectedComponentsWithStats(buracos.astype(np.uint8), 8)
    planta |= np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] < 1500])
    planta = cv2.dilate(planta.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    vf = verde.astype(np.float32)
    fv = np.dstack([cv2.GaussianBlur(im[..., c] * vf, (0, 0), 0.8) for c in range(3)]) / \
        np.maximum(cv2.GaussianBlur(vf, (0, 0), 0.8), 1e-4)[..., None]
    sv = fv.sum(axis=2) + 1
    dv = np.hypot(fv[..., 0] / sv - croma[0], fv[..., 2] / sv - croma[1])
    Lv = fv.mean(axis=2)
    grama = verde & (dv < 0.03) & (Lv > 35) & (Lv < 102) & gramD & ~planta
    inv = gramado & ~grama & ~planta
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv.astype(np.uint8), 8)
    grama |= np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] < 120])
    return grama, planta

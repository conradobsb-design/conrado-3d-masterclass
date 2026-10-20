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

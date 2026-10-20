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


def pedra_portuguesa_foto(px_por_m, alto, largo, buraco=0.55):
    """A pedra portuguesa da foto de referência do usuário (19/10/26), vista de cima (`_texturas/pedra_portuguesa.jpg`,
    largura real em `texturas.json`), na escala px_por_m e no tom da foto, cobrindo alto x largo. As pedras soltas muito
    escuras (buracos: mais escuras que `buraco` x a luz em volta) viram a média em volta; a foto é espelhada em blocos de
    2 x 2 (2,28 x 3,34 m), para os leques se encontrarem sem emenda."""
    import json
    tex = Path(__file__).resolve().parents[2] / "_texturas"
    q = json.loads((tex / "texturas.json").read_text())["materiais"]["pedra_portuguesa"]
    foto = cv2.imread(str(tex / q["arquivo"])).astype(np.float32)
    lum = foto.mean(axis=2)
    escuro = (lum < buraco * cv2.GaussianBlur(lum, (0, 0), 25)).astype(np.uint8)
    escuro = cv2.dilate(escuro, np.ones((7, 7), np.uint8))
    foto = cv2.inpaint(np.clip(foto, 0, 255).astype(np.uint8), escuro, 9, cv2.INPAINT_TELEA).astype(np.float32)
    w = max(2, int(round(q["largura_m"] * px_por_m)))
    h = max(2, int(round(w * foto.shape[0] / foto.shape[1])))
    t = cv2.resize(foto, (w, h), interpolation=cv2.INTER_AREA)
    bloco = np.vstack([np.hstack([t, t[:, ::-1]]), np.hstack([t[::-1], t[::-1, ::-1]])])
    reps = (alto // bloco.shape[0] + 1, largo // bloco.shape[1] + 1, 1)
    return np.tile(bloco, reps)[:alto, :largo]


def pedra_portuguesa_leque(px_por_m, alto, largo, raio_m=1.2, pedra_m=0.07, junta_m=0.012, ss=3, semente=642):
    """A pedra portuguesa da foto de referência (19/10/26) desenhada por código, para se ler na escala da planta: as
    pedras de ~7 cm assentadas em leque (escamas de raio `raio_m`, em fiadas desencontradas, com as pedras ao longo de
    arcos concêntricos), contornos levemente irregulares, juntas claras de areia e as cores sorteadas das pedras da
    própria foto (bege, cinza e rosado). Devolve BGR float32 (alto x largo), no tom da foto."""
    import json
    tex = Path(__file__).resolve().parents[2] / "_texturas"
    q = json.loads((tex / "texturas.json").read_text())["materiais"]["pedra_portuguesa"]
    foto = cv2.imread(str(tex / q["arquivo"])).astype(np.float32)
    lum = foto.mean(axis=2)
    rng = np.random.default_rng(semente)
    k = px_por_m * ss
    H, W = alto * ss, largo * ss
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    def ruido(sig):                                               # campo suave, em px de ss
        n = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sig)
        return n / (n.std() + 1e-6)
    X = X + ruido(0.03 * k) * 0.008 * k                           # contornos irregulares (~8 mm)
    Y = Y + ruido(0.03 * k) * 0.008 * k
    R = raio_m * k
    jb = np.floor(Y / R)
    melhor = np.full((H, W), -1e9, np.float32)
    leque = np.zeros((H, W), np.int64)
    rr = np.zeros((H, W), np.float32)
    th = np.zeros((H, W), np.float32)
    for dj in (-1, 0, 1):                                         # a fiada de baixo cobre a de cima (escamas)
        j = jb + dj
        cx0 = (j % 2) * R
        i = np.round((X - cx0) / (2 * R))
        cx, cy = cx0 + i * 2 * R, j * R
        d = np.hypot(X - cx, Y - cy)
        ok = (d < R * 1.0) & (j > melhor)
        melhor = np.where(ok, j, melhor)
        leque = np.where(ok, (j.astype(np.int64) * 100003 + i.astype(np.int64)), leque)
        rr = np.where(ok, d, rr)
        th = np.where(ok, np.arctan2(Y - cy, X - cx), th)
    s = pedra_m * k
    anel = np.floor(rr / s)
    rc = (anel + 0.5) * s
    desloc = (np.sin(anel * 12.9898 + leque % 997) * 43758.5453) % 1.0      # cada anel começa num ponto
    pos = th * rc / s + desloc
    ang = np.floor(pos)
    ident = (leque * 1000 + anel.astype(np.int64)) * 100000 + ang.astype(np.int64)
    _, inv = np.unique(ident, return_inverse=True)
    inv = inv.reshape(H, W)
    # juntas: borda radial (entre anéis) e angular (entre pedras), e a borda das escamas
    fr = rr / s - anel
    fa = pos - ang
    jt = junta_m / pedra_m / 2
    junta = (fr < jt) | (fr > 1 - jt) | (fa < jt) | (fa > 1 - jt) | (rr > R - junta_m * k)
    # cores das pedras: amostras do miolo das pedras da foto (sem as juntas claras nem os buracos escuros)
    lb = cv2.GaussianBlur(lum, (0, 0), 2)
    miolo = (lb > np.percentile(lb, 15)) & (lb < np.percentile(lb, 70))
    ys, xs = np.nonzero(miolo)
    sel = rng.integers(0, len(ys), inv.max() + 1)
    cores = cv2.GaussianBlur(foto, (0, 0), 2)[ys[sel], xs[sel]]
    img = cores[inv]
    img *= (0.97 + 0.06 * np.clip(np.minimum(np.minimum(fr, 1 - fr), np.minimum(fa, 1 - fa)) * 4, 0, 1))[..., None]
    areia = np.percentile(foto.reshape(-1, 3), 92, axis=0)
    img[junta] = areia
    return cv2.resize(img, (largo, alto), interpolation=cv2.INTER_AREA)


def trocar_pedra_portuguesa(out, mascara, px_por_m, pedra_cm=7.0, semente=642, sig_luz_m=1.5, sig_sombra_m=0.25,
                            sombra_limiar=0.93, contraste=1.0, junta=(0.6, 0.78), fonte="foto"):
    """A pedra portuguesa do motor (pedras de 12 a 15 cm, fora da regra) vira a da regra, de 6 a 8 cm (R1; seção 3 do
    POE642_REGRAS.md): as pedras caramelo, ocre e creme com juntas de areia do `fontes_procedurais.pedra_portuguesa`,
    desenhadas na escala da imagem (`pedra_cm`, a px_por_m), sobre a luz larga do lugar (no tom que já está lá) e com as
    sombras dele, como em `trocar_grama`. Na imagem final (3840 px) as pedras de 7 cm têm ~4 px e se leem; no render de
    2000 px, ~2 px. `junta`: (largura em px, escurecimento) das juntas entre as pedras.
    fonte="foto" (escolha do usuário, 20/10/26: "opção 1, tom da foto"): o desenho e o tom da foto de referência
    (`pedra_portuguesa_foto`), com a luz relativa do lugar (sombras e variações), em vez do caramelo procedural."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import fontes_procedurais as fp
    im = out.astype(np.float32)
    m = mascara.astype(np.float32)
    Lg = nconv(im, m, sig_luz_m * px_por_m)
    Lc = nconv(im, m, sig_sombra_m * px_por_m)
    sombra = np.minimum(1.0, ((Lc.mean(axis=2) + 1) / (Lg.mean(axis=2) + 1)) / sombra_limiar)
    ys, xs = np.nonzero(mascara)
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    if fonte in ("foto", "leque"):
        P = (pedra_portuguesa_leque if fonte == "leque" else pedra_portuguesa_foto)(px_por_m, by1 - by0, bx1 - bx0)
        Lg = Lg / Lg[mascara].mean(axis=0)                        # só a luz relativa do lugar; o tom é o da foto
    else:
        P = fp.pedra_portuguesa(lado=max(by1 - by0, bx1 - bx0), pedra_cm=pedra_cm, semente=semente,
                                cm_por_px=100.0 / px_por_m, junta=junta).astype(np.float32)[:by1 - by0, :bx1 - bx0]
    media = P.reshape(-1, 3).mean(axis=0)
    det = 1 + contraste * (P / media - 1)
    if fonte in ("foto", "leque"):
        det = det * media
    novo = im.copy()
    novo[by0:by1, bx0:bx1] = (Lg * sombra[..., None])[by0:by1, bx0:bx1] * det
    a = (cv2.GaussianBlur(m, (0, 0), 0.7) * m)[..., None]
    return np.clip(im * (1 - a) + novo * a, 0, 255).astype(np.uint8), int(mascara.sum())


"""Desenho vetorial nítido em qualquer escala (a final de 3840 px ou os 12K), pelas coordenadas da final (px).

As peças são polígonos em px da final; `escala` e `origem` levam ao px da imagem: X = (x - origem[0]) * escala.
A cobertura vem de um raster supersampleado (fillPoly com subpixel) reduzido por área: bordas antisserrilhadas.
"""
import cv2
import numpy as np


def P_(escala, origem):
    return lambda x, y: ((x - origem[0]) * escala, (y - origem[1]) * escala)


def janela(img, caixa, escala, origem, folga=2):
    """A caixa (px da final) em px inteiros da imagem, com folga, dentro da imagem."""
    x0, y0, x1, y1 = caixa
    H, W = img.shape[:2]
    X0 = max(int(np.floor((x0 - origem[0]) * escala)) - folga, 0)
    Y0 = max(int(np.floor((y0 - origem[1]) * escala)) - folga, 0)
    X1 = min(int(np.ceil((x1 - origem[0]) * escala)) + folga, W)
    Y1 = min(int(np.ceil((y1 - origem[1]) * escala)) + folga, H)
    return X0, Y0, X1, Y1


def ret(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def seg(p, q, larg):
    """O traço de p a q (px da final) com a largura larg (px da final), como polígono."""
    p, q = np.float64(p), np.float64(q)
    d = q - p
    n = np.hypot(*d)
    if n == 0:
        return ret(p[0] - larg / 2, p[1] - larg / 2, p[0] + larg / 2, p[1] + larg / 2)
    t = np.array([-d[1], d[0]]) / n * larg / 2
    return [tuple(p + t), tuple(q + t), tuple(q - t), tuple(p - t)]


def _eh_ret(p):
    a = np.asarray(p, np.float64)
    if a.shape != (4, 2):
        return False
    xs, ys = sorted(set(np.round(a[:, 0], 6))), sorted(set(np.round(a[:, 1], 6)))
    return len(xs) == 2 and len(ys) == 2


def _cob_1d(n, z0, a, b):
    """A cobertura de cada px (de z0 a z0+n-1) pelo intervalo [a, b] (px da imagem)."""
    k = np.arange(z0, z0 + n, dtype=np.float64)
    return np.clip(np.minimum(k + 1, b) - np.maximum(k, a), 0, 1).astype(np.float32)


def cob(polys, jan, escala, origem, ss=8):
    """A cobertura (0..1) dos polígonos (px da final) na janela (X0, Y0, X1, Y1) da imagem: os retângulos exatos
    (a área), os outros num raster supersampleado; a união por soma limitada a 1 (peças vizinhas não se sobrepõem)."""
    X0, Y0, X1, Y1 = jan
    W, H = X1 - X0, Y1 - Y0
    out = np.zeros((H, W), np.float32)
    outros = []
    for p in polys:
        if _eh_ret(p):
            a = np.asarray(p, np.float64)
            ax0, ax1 = (a[:, 0].min() - origem[0]) * escala, (a[:, 0].max() - origem[0]) * escala
            ay0, ay1 = (a[:, 1].min() - origem[1]) * escala, (a[:, 1].max() - origem[1]) * escala
            out += np.outer(_cob_1d(H, Y0, ay0, ay1), _cob_1d(W, X0, ax0, ax1))
        else:
            outros.append(p)
    if outros:
        sh = 4
        can = np.zeros((H * ss, W * ss), np.uint8)
        for p in outros:                            # um a um: sobrepostos não se anulam (par-ímpar)
            a = np.asarray(p, np.float64)
            u = ((a[:, 0] - origem[0]) * escala - X0) * ss - 0.5
            v = ((a[:, 1] - origem[1]) * escala - Y0) * ss - 0.5
            pt = np.round(np.stack([u, v], 1) * (1 << sh)).astype(np.int32)
            cv2.fillPoly(can, [pt], 255, lineType=cv2.LINE_8, shift=sh)
        out += cv2.resize(can.astype(np.float32) / 255.0, (W, H), interpolation=cv2.INTER_AREA)
    return np.clip(out, 0, 1)


def compor(reg, a, cor):
    """reg (float) com a cor (BGR ou imagem) por cima, no alfa a."""
    cor = np.asarray(cor, np.float32)
    return reg * (1 - a[..., None]) + cor * a[..., None]


def coords(jan, escala, origem):
    """As coordenadas (px da final) do centro de cada coluna e de cada linha da janela."""
    X0, Y0, X1, Y1 = jan
    xs = (np.arange(X0, X1) + 0.5) / escala + origem[0]
    ys = (np.arange(Y0, Y1) + 0.5) / escala + origem[1]
    return xs, ys


def letras(reg, zona, dif=60.0, folga=None, escala=1.0, ref=None, area_min=5.0, piso_dif=0.0):
    """As letras escuras (os rótulos) da região, para pôr de volta por cima de um desenho novo: o alfa e a cor.
    zona: a máscara (bool) onde procurar; dif: quanto mais escuro que o fundo a letra é (o fundo: `ref`, a luminância
    do fundo liso, ou a mediana em volta); area_min: a área mínima de cada pedaço (px da final), sem os pontinhos."""
    g = cv2.cvtColor(np.clip(reg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    if ref is None:
        k = max(3, int(round(9 * escala)) | 1)
        fundo0 = cv2.medianBlur(g.astype(np.uint8), k).astype(np.float32)
    else:
        fundo0 = np.full(g.shape, float(ref), np.float32)
    nucleo = (fundo0 - g > dif) & zona
    n, lab, st, _ = cv2.connectedComponentsWithStats(nucleo.astype(np.uint8), 8)
    ok = np.zeros(n, bool)
    ok[1:] = st[1:, cv2.CC_STAT_AREA] >= area_min * escala * escala
    nucleo = ok[lab]
    if not nucleo.any():
        return np.zeros(g.shape, np.float32), np.zeros(3, np.float32)
    r = max(1, int(round((folga if folga is not None else 0.8) * escala)))
    m = cv2.dilate(nucleo.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    fundo = cv2.inpaint(np.clip(g, 0, 255).astype(np.uint8), m, max(3, r * 2), cv2.INPAINT_TELEA).astype(np.float32)
    Lt = float(np.percentile(g[nucleo], 5))
    a = np.clip((fundo - g - piso_dif) / np.maximum(fundo - Lt - piso_dif, 1.0), 0, 1) * (m > 0)
    cor = np.median(reg[nucleo & (a > 0.85)], axis=0) if (nucleo & (a > 0.85)).any() else np.median(reg[nucleo], axis=0)
    return a.astype(np.float32), cor.astype(np.float32)

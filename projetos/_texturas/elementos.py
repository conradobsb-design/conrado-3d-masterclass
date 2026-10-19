#!/usr/bin/env python3
"""Guarda-roupas, escadas, box e portas como nas plantas de referência do usuário (POE 642, todas as casas).

Pedido do usuário (19/10/26), com duas plantas de um duplex (`originais/referencia_elementos_superior.png` e
`..._inferior.png`): "referencia dos guarda-roupas e escadas, box e portas". Escala medida nelas pelas camas
(casal 1,58 x 2,00 m = 57 x 72 px; solteiro 0,95 m = 36 px): 36 px/m.

O que se vê nelas, e como cada função desenha (em metros, na escala do render, px_por_m):
- `guarda_roupa`: o armário visto de cima, aberto: moldura branca fina (as portas e as laterais) com contorno
  cinza, o miolo cinza-claro das roupas, mais escuro junto às portas, e os cabides em traços cinza de través, a
  cada ~12 cm, com pequenas diferenças de comprimento e de tom, como roupas.
- `escada`: degraus claros, sem traço preto: em cada bocel uma linha cinza suave e, logo depois, um degradê de
  sombra de ~10 cm no degrau de baixo. Depois do corte, os degraus que passam por cima ficam esmaecidos, só com
  os bocéis em linha pontilhada (a projeção), e o corrimão é uma linha fina.
- `box`: o piso do banho contínuo, o vidro do box como linha fina clara (reflexo) com uma sombra cinza ao lado,
  e o chuveiro de teto como um disco cinza a ~35 cm da parede, com o braço curto até ela.
- `porta_correr`: o caixilho como faixa branca de 5 cm com contorno cinza, as folhas em duas linhas cinza
  sobrepostas por dentro, e os batentes (nas pontas e no encontro das folhas) em quadradinhos brancos de 8 cm
  com contorno, saindo do caixilho; `porta_giro`: a folha branca fina, aberta a 90°, com o arco cinza fino
  (regra das casas: arcos em cinza fino) e o batente.

Cada função devolve (BGR float32, alfa 0 a 1), na horizontal; para aplicar, girar e pousar no render.

Uso:
  python3 elementos.py      # cartela_elementos.jpg: a referência ao lado da nossa versão, na escala da prancha
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
SS = 4                              # supersampling do desenho
REF_PX_M = 36


def _px(v_m, px_m):
    return max(1, int(round(v_m * px_m)))


def _reduz(t, W, H):
    return cv2.resize(t, (W, H), interpolation=cv2.INTER_AREA)


def _retangulo(t, x0, y0, x1, y1, cor):
    t[int(round(y0)):int(round(y1)), int(round(x0)):int(round(x1))] = cor


def _contorno(t, x0, y0, x1, y1, cor, e):
    _retangulo(t, x0, y0, x1, y0 + e, cor)
    _retangulo(t, x0, y1 - e, x1, y1, cor)
    _retangulo(t, x0, y0, x0 + e, y1, cor)
    _retangulo(t, x1 - e, y0, x1, y1, cor)


def guarda_roupa(comp_m, prof_m, px_m, semente=1):
    """Comprimento na horizontal, portas embaixo (y maior)."""
    rng = np.random.default_rng(semente)
    W, H = _px(comp_m, px_m), _px(prof_m, px_m)
    k = px_m * SS
    w, h = W * SS, H * SS
    yy = np.linspace(0, 1, h)[:, None]
    t = np.zeros((h, w, 3), np.float32)
    t[:] = (216 - 40 * yy ** 1.4)[..., None] * np.ones((1, w, 1))           # fundo claro, junto às portas escuro
    # cabides: traços cinza de través, a cada ~12 cm, com pequenas diferenças (roupas)
    x = rng.uniform(0.05, 0.09) * k
    sig = 0.007 * k
    xs = np.arange(w)[None, :]
    while x < w - 0.05 * k:
        y0 = int(rng.uniform(0.12, 0.20) * h)
        y1 = int(rng.uniform(0.78, 0.88) * h)
        perfil = np.exp(-0.5 * ((xs - x) / sig) ** 2)
        t[y0:y1] -= (rng.uniform(38, 52) * perfil)[..., None]
        x += rng.uniform(0.10, 0.14) * k
    # moldura: laterais e fundo finos, as portas uma faixa branca de 2,5 cm; contorno cinza
    e = 0.02 * k
    _retangulo(t, 0, h - 0.025 * k, w, h, (238, 238, 240))
    _retangulo(t, 0, 0, e, h, (234, 234, 236))
    _retangulo(t, w - e, 0, w, h, (234, 234, 236))
    _retangulo(t, 0, 0, w, e * 0.6, (226, 226, 228))
    _contorno(t, 0, 0, w, h, (160, 160, 162), max(1, 0.006 * k))
    return _reduz(t, W, H), np.ones((H, W), np.float32)


def escada(larg_m, n, piso_m, px_m, corte, cor=(222, 222, 226), esmaecer=0.8):
    """n degraus subindo para cima (o 1º embaixo); de `corte` em diante, a projeção pontilhada, esmaecida."""
    W, H = _px(larg_m, px_m), _px(n * piso_m, px_m)
    k = px_m * SS
    w, h = W * SS, H * SS
    t = np.zeros((h, w, 3), np.float32)
    t[:] = cor
    p = piso_m * k
    for i in range(n):
        yb = h - i * p                      # borda de baixo do degrau i; o bocel do degrau i+1 é yb - p
        y_boc = yb - p
        if i + 1 >= n:
            break
        if i + 1 < corte:
            # bocel: linha cinza suave; sombra no degrau de baixo (y maior), ~10 cm
            sombra = np.linspace(1, 0, int(0.10 * k))[:, None, None] ** 1.6
            y0 = int(y_boc)
            t[y0:y0 + len(sombra)] -= 26 * sombra
            _retangulo(t, 0, y_boc - 0.006 * k, w, y_boc + 0.006 * k, (176, 176, 180))
    # depois do corte: esmaecido, bocéis pontilhados
    yc = h - (corte - 1) * p
    t[:int(yc)] = 255 - (255 - t[:int(yc)]) * esmaecer
    traco, vao = 0.03 * k, 0.025 * k
    for i in range(corte - 1, n - 1):
        y = h - (i + 1) * p
        x = 0.0
        while x < w:
            _retangulo(t, x, y - 0.006 * k, min(w, x + traco), y + 0.006 * k, (158, 158, 162))
            x += traco + vao
    # corrimão: linha fina junto à borda livre (direita)
    _retangulo(t, w - 0.05 * k, int(yc), w - 0.04 * k, h, (150, 150, 154))
    x = 0.0
    while x < yc:
        _retangulo(t, w - 0.05 * k, x, w - 0.04 * k, min(yc, x + traco), (190, 190, 194))
        x += traco + vao
    _contorno(t, 0, 0, w, h, (170, 170, 174), max(1, 0.005 * k))
    return _reduz(t, W, H), np.ones((H, W), np.float32)


def box(larg_m, comp_m, vidro_m, px_m, piso=(214, 214, 216)):
    """O banho na horizontal: o box à direita do vidro (a `vidro_m` da esquerda), o chuveiro no meio dele."""
    W, H = _px(comp_m, px_m), _px(larg_m, px_m)
    k = px_m * SS
    w, h = W * SS, H * SS
    t = np.zeros((h, w, 3), np.float32)
    t[:] = piso
    xv = vidro_m * k
    # sombra suave do vidro no piso do box, a linha cinza e o reflexo claro
    s = np.linspace(1, 0, int(0.06 * k))[None, :, None] ** 1.5
    t[:, int(xv):int(xv) + s.shape[1]] -= 14 * s
    _retangulo(t, xv - 0.008 * k, 0, xv + 0.004 * k, h, (172, 176, 180))
    _retangulo(t, xv - 0.016 * k, 0, xv - 0.008 * k, h, (238, 240, 242))
    # chuveiro de teto: disco cinza, a 35 cm da parede do fundo (direita), com o braço até ela
    cx, cy, r = w - 0.35 * k, h * 0.5, 0.09 * k
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot(xx - cx, yy - cy)
    _retangulo(t, cx, cy - 0.008 * k, w, cy + 0.008 * k, (168, 168, 172))
    disco = d < r
    t[disco] = (205 - 35 * (d[disco] / r) ** 2)[:, None] * np.ones((1, 3))
    anel = (d >= r) & (d < r + 0.008 * k)
    t[anel] = (150, 150, 154)
    return _reduz(t, W, H), np.ones((H, W), np.float32)


def porta_correr(larg_m, px_m, folhas=2):
    """Trilho branco fino com as folhas sobrepostas e os batentes em quadradinhos, na horizontal."""
    W, H = _px(larg_m, px_m), _px(0.14, px_m)
    k = px_m * SS
    w, h = W * SS, H * SS
    t = np.zeros((h, w, 3), np.float32)
    a = np.zeros((h, w), np.float32)
    cy = h / 2
    # o caixilho: faixa branca de 5 cm com contorno cinza; as folhas, duas linhas cinza por dentro, sobrepostas
    _retangulo(t, 0, cy - 0.025 * k, w, cy + 0.025 * k, (160, 162, 164))
    _retangulo(t, 0.004 * k, cy - 0.021 * k, w - 0.004 * k, cy + 0.021 * k, (247, 248, 249))
    _retangulo(a, 0, cy - 0.025 * k, w, cy + 0.025 * k, 1)
    lf = w / folhas + 0.04 * k
    for i in range(folhas):
        x0 = max(0, i * (w / folhas) - (0.04 * k if i else 0))
        off = (-1 if i % 2 == 0 else 1) * 0.008 * k
        _retangulo(t, x0 + 0.05 * k, cy + off - 0.002 * k, min(w, x0 + lf) - 0.05 * k, cy + off + 0.002 * k,
                   (176, 178, 180))
    # batentes nas pontas e o encontro das folhas: quadradinhos brancos com contorno, saindo do caixilho
    for xc in [0.04 * k, w - 0.04 * k] + [w * i / folhas for i in range(1, folhas)]:
        x0 = min(max(0, xc - 0.04 * k), w - 0.08 * k)
        _retangulo(t, x0, cy - 0.05 * k, x0 + 0.08 * k, cy + 0.05 * k, (160, 162, 164))
        _retangulo(t, x0 + 0.005 * k, cy - 0.045 * k, x0 + 0.075 * k, cy + 0.045 * k, (250, 250, 250))
        _retangulo(a, x0, cy - 0.05 * k, x0 + 0.08 * k, cy + 0.05 * k, 1)
    return _reduz(t, W, H), _reduz(a, W, H)


def porta_giro(larg_m, px_m):
    """O vão na horizontal (parede embaixo, em y = larg); a folha aberta a 90° na esquerda, o arco cinza fino."""
    W = H = _px(larg_m + 0.06, px_m)
    k = px_m * SS
    w, h = W * SS, H * SS
    t = np.zeros((h, w, 3), np.float32)
    a = np.zeros((h, w), np.float32)
    e = 0.035 * k
    xd, yb = 0.03 * k, h - 0.01 * k                  # dobradiça
    L = larg_m * k
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot(xx - xd, yy - yb)
    arco = (np.abs(d - L) < 0.004 * k) & (xx >= xd) & (yy <= yb)
    t[arco] = (160, 161, 160)
    a[arco] = 1
    _retangulo(t, xd, yb - L, xd + e, yb, (168, 170, 172))
    _retangulo(t, xd + 0.004 * k, yb - L + 0.004 * k, xd + e - 0.004 * k, yb - 0.004 * k, (247, 247, 248))
    _retangulo(a, xd, yb - L, xd + e, yb, 1)
    return _reduz(t, W, H), _reduz(a, W, H)


def cartela():
    import sys
    sys.path.insert(0, str(AQUI.parent / "POE642_CasaA" / "scripts"))
    from PIL import ImageDraw, ImageFont
    from rodape_entrega import FONTES
    px_m = json.loads((AQUI / "texturas.json").read_text())["escala_prancha_px_por_m"]
    sup = np.asarray(Image.open(AQUI / "originais/referencia_elementos_superior.png").convert("RGB"))[..., ::-1]
    inf = np.asarray(Image.open(AQUI / "originais/referencia_elementos_inferior.png").convert("RGB"))[..., ::-1]
    H = 300

    def caber(a, h=H, wmax=520):
        f = min(h / a.shape[0], wmax / a.shape[1])
        return cv2.resize(a.astype(np.float32), (round(a.shape[1] * f), round(a.shape[0] * f)),
                          interpolation=cv2.INTER_CUBIC)

    def sobre_piso(cor, alfa, piso=(214, 214, 216), m=12):
        h, w = alfa.shape
        f = np.full((h + 2 * m, w + 2 * m, 3), piso, np.float32)
        f[m:m + h, m:m + w] = cor * alfa[..., None] + f[m:m + h, m:m + w] * (1 - alfa[..., None])
        return f

    def amp(a, f=2):
        return cv2.resize(a, None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST)

    gr = sobre_piso(*guarda_roupa(2.4, 0.6, px_m))
    es = sobre_piso(*escada(1.0, 14, 0.28, px_m, corte=8))
    es = cv2.rotate(es, cv2.ROTATE_90_COUNTERCLOCKWISE)
    bx = sobre_piso(*box(1.2, 2.5, 1.5, px_m))
    pc = sobre_piso(*porta_correr(2.4, px_m))
    pg = sobre_piso(*porta_giro(0.8, px_m))
    portas = np.full((max(pc.shape[0], pg.shape[0]), pc.shape[1] + 30 + pg.shape[1], 3), 255, np.float32)
    portas[:pc.shape[0], :pc.shape[1]] = pc
    portas[:pg.shape[0], pc.shape[1] + 30:] = pg
    linhas = [
        ("1. Guarda-roupa  ·  referência (closet da suíte; armário do quarto)  |  a nossa, 2,40 x 0,60 m, na escala "
         "da prancha e ampliada 2 x",
         [caber(sup[17:46, 122:168], 140), caber(sup[133:234, 232:258]), gr, amp(gr)]),
        ("2. Escada  ·  referência (vista de cima; o lance que sobe, com a projeção pontilhada)  |  a nossa: 14 "
         "degraus de 28 cm, corte no 8º, e ampliada 2 x",
         [caber(sup[16:92, 166:260]), caber(inf[22:107, 280:397]), es, amp(es)]),
        ("3. Box  ·  referência (banho da suíte; banho de baixo)  |  o nosso, 1,20 x 2,50 m, e ampliado 2 x",
         [caber(sup[128:234, 102:170]), caber(inf[133:242, 213:287]), bx, amp(bx)]),
        ("4. Portas  ·  referência (porta de correr do terraço; janela de correr do quarto)  |  as nossas: de "
         "correr de 2,40 m e de giro de 0,80 m (com o arco cinza fino), e ampliadas 2 x",
         [caber(inf[122:142, 142:212], 120), caber(sup[224:240, 180:245], 120), portas, amp(portas)]),
    ]
    blocos = []
    for titulo, pecas in linhas:
        alto = max(p.shape[0] for p in pecas)
        larg = 40 + sum(p.shape[1] + 30 for p in pecas)
        b = np.full((alto + 70, larg, 3), 255, np.float32)
        x = 40
        for p in pecas:
            b[60:60 + p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1] + 30
        blocos.append((titulo, b))
    larg = max(b.shape[1] for _, b in blocos)
    tela = np.full((80 + sum(b.shape[0] for _, b in blocos), larg, 3), 255, np.float32)
    y, pos = 80, []
    for titulo, b in blocos:
        tela[y:y + b.shape[0], :b.shape[1]] = b
        pos.append((y, titulo))
        y += b.shape[0]
    im = Image.fromarray(np.clip(tela, 0, 255).astype(np.uint8)[..., ::-1])
    d = ImageDraw.Draw(im)
    d.text((40, 24), "Elementos de referência · POE 642 · todas as casas",
           font=ImageFont.truetype(str(FONTES / "Inter-Medium.otf"), 30), fill=(40, 40, 40))
    f2 = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 20)
    for y, titulo in pos:
        d.text((40, y + 14), titulo, font=f2, fill=(60, 60, 60))
    im.save(AQUI / "cartela_elementos.jpg", quality=92)
    print(AQUI / "cartela_elementos.jpg", im.size)


if __name__ == "__main__":
    cartela()

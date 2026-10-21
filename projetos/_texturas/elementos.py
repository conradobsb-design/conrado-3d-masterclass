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
  com contorno, saindo do caixilho; `porta_giro`: a folha branca fina, aberta a 90°, sem o arco (decisão do
  usuário, 19/10/26: "remover os arcos, escadas com linhas"; com `arco=True`, o arco cinza fino da regra antiga).
- Escadas com linhas (mesma decisão): o bocel em linha cinza suave, como na referência.
- Triângulo de orientação no início da escada (usuário, 19/10/26): cheio, cinza-escuro, 24 x 26 cm, no meio da
  largura, a 10 cm do início, com a ponta no sentido do percurso: subida, no 1º degrau, para quem sobe a partir do
  pavimento; descida, no topo, para quem desce (`escada(..., triangulo="sobe" | "desce")`).
- Roupa de cama, como mais uma opção (usuário, 19/10/26, com a mesma planta: "use as referencias de roupa de cama.
  como mais uma opção. ainda não aplique"): só a referência, na cartela, sem função de desenho ainda. Na cama de
  casal, lençol e edredom brancos com a dobra branca junto aos travesseiros, uma manta bordô (RGB ~118, 81, 85)
  atravessada na metade dos pés, com dobras suaves, dois travesseiros bordô na frente de dois cinza-claros e os
  criados redondos de madeira com abajur branco; na de solteiro, a cama de madeira com o criado embutido, o
  edredom branco com uma faixa bordô atravessada, um travesseiro bordô sobre um cinza e a manta cinza-clara na
  cabeceira.

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


def guarda_roupa(comp_m, prof_m, px_m, semente=1, miolo=None, moldura=None):
    """Comprimento na horizontal, portas embaixo (y maior). miolo e moldura (BGR): os tons do fundo e da moldura (o
    fundo leva o mesmo sombreado e os cabides; o contorno é a moldura mais escura); sem eles, o cinza da referência."""
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
    if miolo is not None:
        t = t / 216 * np.asarray(miolo, np.float32)
    # moldura: laterais e fundo finos, as portas uma faixa branca de 2,5 cm; contorno cinza
    e = 0.02 * k
    cor = (lambda f: tuple(f * c for c in moldura)) if moldura is not None else None
    _retangulo(t, 0, h - 0.025 * k, w, h, cor(1.0) if cor else (238, 238, 240))
    _retangulo(t, 0, 0, e, h, cor(0.98) if cor else (234, 234, 236))
    _retangulo(t, w - e, 0, w, h, cor(0.98) if cor else (234, 234, 236))
    _retangulo(t, 0, 0, w, e * 0.6, cor(0.95) if cor else (226, 226, 228))
    _contorno(t, 0, 0, w, h, cor(0.68) if cor else (160, 160, 162), max(1, 0.006 * k))
    return _reduz(t, W, H), np.ones((H, W), np.float32)


TRIANGULO = {"base_m": 0.24, "altura_m": 0.26, "recuo_m": 0.10, "cor": (88, 88, 92)}


def triangulo_escada(t, k, w, y_ponta, para_cima):
    """O triângulo de orientação no início da escada (usuário, 19/10/26: "precisamos do triangulo como símbolo de
    orientação no inicio de escadas, indicando o sentido ora subida ora descida, a depender da situação"): cheio,
    cinza-escuro, no meio da largura, com a ponta no sentido do percurso de quem chega por este pavimento."""
    q = TRIANGULO
    cx, b, a = w / 2, q["base_m"] * k / 2, q["altura_m"] * k
    yb = y_ponta + (a if para_cima else -a)
    pts = np.int32(np.round([(cx, y_ponta), (cx - b, yb), (cx + b, yb)]))
    cv2.fillPoly(t, [pts], q["cor"], lineType=cv2.LINE_8)


def escada(larg_m, n, piso_m, px_m, corte=None, cor=(222, 222, 226), esmaecer=0.8, triangulo=None):
    """n degraus subindo para cima (o 1º embaixo); de `corte` em diante, a projeção pontilhada, esmaecida (corte=None:
    a escada inteira cheia). triangulo="sobe": no 1º degrau, apontando para cima (quem está neste pavimento sobe);
    "desce": no último, apontando para baixo (quem está no pavimento de cima desce)."""
    corte = n + 1 if corte is None else corte
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
    yc = max(0.0, h - (corte - 1) * p)
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
    rec = TRIANGULO["recuo_m"] * k
    if triangulo == "sobe":
        triangulo_escada(t, k, w, h - rec - TRIANGULO["altura_m"] * k, True)
    elif triangulo == "desce":
        triangulo_escada(t, k, w, rec + TRIANGULO["altura_m"] * k, False)
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


def porta_giro(larg_m, px_m, arco=False):
    """O vão na horizontal (parede embaixo, em y = larg); a folha aberta a 90° na esquerda (com arco=True, também o
    arco cinza fino da regra antiga)."""
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
    if arco:
        tr = (np.abs(d - L) < 0.004 * k) & (xx >= xd) & (yy <= yb)
        t[tr] = (160, 161, 160)
        a[tr] = 1
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
    es = sobre_piso(*escada(1.0, 14, 0.28, px_m, corte=8, triangulo="sobe"))
    es = cv2.rotate(es, cv2.ROTATE_90_COUNTERCLOCKWISE)
    ed = sobre_piso(*escada(1.0, 14, 0.28, px_m, triangulo="desce"))
    ed = cv2.rotate(ed, cv2.ROTATE_90_COUNTERCLOCKWISE)
    escadas = np.full((es.shape[0] + 20 + ed.shape[0], es.shape[1], 3), 255, np.float32)
    escadas[:es.shape[0]] = es
    escadas[es.shape[0] + 20:] = ed
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
        ("2. Escada  ·  referência  |  a nossa, 14 degraus de 28 cm: em cima, quem sobe (triângulo no 1º degrau, "
         "corte no 8º); embaixo, quem desce (triângulo no topo); e ampliadas 2 x",
         [caber(sup[16:92, 166:260]), caber(inf[22:107, 280:397]), escadas, amp(escadas)]),
        ("3. Box  ·  referência (banho da suíte; banho de baixo)  |  o nosso, 1,20 x 2,50 m, e ampliado 2 x",
         [caber(sup[128:234, 102:170]), caber(inf[133:242, 213:287]), bx, amp(bx)]),
        ("4. Portas  ·  referência (porta de correr do terraço; janela de correr do quarto)  |  as nossas: de "
         "correr de 2,40 m e de giro de 0,80 m (sem arco), e ampliadas 2 x",
         [caber(inf[122:142, 142:212], 120), caber(sup[224:240, 180:245], 120), portas, amp(portas)]),
        ("5. Roupa de cama (opção, ainda não aplicada)  ·  referência: cama de casal da suíte e de solteiro do quarto",
         [caber(sup[24:118, 30:122]), caber(sup[134:232, 170:213])]),
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

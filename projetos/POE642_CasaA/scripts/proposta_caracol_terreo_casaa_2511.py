"""Casa A Térreo: 3 opções para a escada helicoidal (25/11), só a proposta, para a escolha.

Usuário, com o recorte do 12K B (o rótulo SOBE PARA O 1º PAVIMENTO, o ▶ e o S): "me traga 3 opções de representação da
escada helicoidal, levando em consideração o sentido que sobe, representando os degraus desse nível e a transparência
do nível superior".

A geometria é a do PDF (ARQ_ESCADAS E RAMPAS): o centro em (1977,4; 1571,6) px da final, o raio de 55 px (3,3 m de
diâmetro... na escala da final, 0,92 m de raio), o pilar central de 4,4 px, os degraus de 17,85° (21 numerados, uma volta
inteira). Sobe no sentido anti-horário (na tela): o degrau 1 à direita, logo acima do S, e o 7 à esquerda no alto. O
PDF desenha cheios os degraus até o corte do nível (as linhas de 4,1° a 146,9°, o arranque e os degraus 1 a 7) e
tracejados os de cima (8 a 21). Hoje o ▶ aponta para fora (para a direita), não no sentido da subida, e o meio de baixo
mostra o travertino do piso por dentro do círculo.

As três opções, no recorte do 12K B (letra Kalam), com o piso da garagem refeito por baixo da escada:
  1. Corte clássico: os degraus deste nível cheios, cada um com o bocel fino e a sombra curta do degrau de cima; a
     linha de quebra no corte; os degraus de cima transparentes (o piso aparece sob um véu claro leve), só com os
     tracejados; a linha de caminhamento do círculo do arranque até a seta no corte, o S no arranque.
  2. Subida em degradê: os degraus clareiam conforme sobem (a altura lida pelo tom); depois do corte continuam em vidro
     fosco (o piso aparece atrás), com as arestas finas; a linha de caminhamento em espiral pela volta inteira, cheia
     neste nível e tracejada em cima, a seta na chegada ao 1º pavimento, o S no arranque.
  3. Gráfica: os degraus deste nível num tom só, separados por frestas claras, o contorno nítido; os de cima só em
     tracejado sobre o piso (transparência total, como no PDF); o ▶ no primeiro degrau, girado no sentido da subida,
     com o S ao lado.

  python3 proposta_caracol_terreo_casaa_2511.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import terreo_casaa_2511d as D       # noqa: E402

PLANTA = "A_Terreo"
G = dict(c=(1977.4, 1571.6), R=55.0, rc=4.4, a0=4.1, passo=17.85, n_vis=8, n_tot=21, rcam=30.0)
CAIXA = (1905.0, 1478.0, 2050.0, 1640.0)          # o recorte (px da final)
PISO_FONTE = (1902.0, 1520.0, 1922.0, 1600.0)     # o piso da garagem, à esquerda da escada
COR = dict(degrau=(153.0, 171.0, 191.0), linha=(62.0, 66.0, 72.0), traco=(84.0, 88.0, 94.0), pilar=(38.0, 38.0, 40.0),
           texto=(37.0, 40.0, 40.0), fresta=(222.0, 228.0, 232.0))
FONTE_K = EP.PROJ / "POE642_CasaA/entrega/assets/fontes/Kalam-Regular.woff"
FONTE_T = EP.PROJ / "POE642_CasaA/entrega/assets/fontes/Poppins-Medium.ttf"
FONTE_TL = EP.PROJ / "POE642_CasaA/entrega/assets/fontes/Poppins-Regular.ttf"
SS = 4


class Tela:
    """As coordenadas (px da final) de cada subpixel do recorte (SS x SS por px da imagem)."""

    def __init__(self, shape, escala, origem, X0, Y0):
        H, W = shape
        self.H, self.W, self.s = H, W, escala
        u = (np.arange(W * SS) + 0.5) / SS + X0
        v = (np.arange(H * SS) + 0.5) / SS + Y0
        self.x = (u / escala + origem[0])[None, :]
        self.y = (v / escala + origem[1])[:, None]
        cx, cy = G["c"]
        self.dx, self.dy = self.x - cx, self.y - cy
        self.r = np.hypot(self.dx, self.dy)
        self.t = np.degrees(np.arctan2(-self.dy, self.dx)) % 360.0     # anti-horário na tela

    def reduz(self, m):
        m = m.astype(np.float32)
        return cv2.resize(m, (self.W, self.H), interpolation=cv2.INTER_AREA)


def ang_rel(t, a):
    """O ângulo de t a partir de a, em [0, 360)."""
    return (t - a) % 360.0


def dist_raio(T, a):
    """A distância (px da final) de cada ponto à semirreta do centro no ângulo a (só do lado de fora do pilar)."""
    d = np.radians(ang_rel(T.t, a))
    d = np.where(d > np.pi, d - 2 * np.pi, d)
    return np.where(np.abs(d) < np.pi / 2, T.r * np.abs(np.sin(d)), T.r)


def tracejado(T, a, t_on=2.2, t_off=1.6, larg=0.32, r0=None, r1=None):
    """O raio tracejado no ângulo a (o traço ao longo do raio)."""
    r0 = G["rc"] + 0.6 if r0 is None else r0
    r1 = G["R"] if r1 is None else r1
    ok = (dist_raio(T, a) < larg / 2) & (np.abs(ang_rel(T.t, a + 180) - 180) < 90) & (T.r > r0) & (T.r < r1)
    return ok & (((T.r - r0) % (t_on + t_off)) < t_on)


def arco(T, r, t0, t1, larg=0.32, t_on=None, t_off=1.6):
    """O arco de raio r de t0 a t1 (anti-horário), cheio ou tracejado (t_on, t_off em px ao longo do arco)."""
    ok = (np.abs(T.r - r) < larg / 2) & (ang_rel(T.t, t0) <= ang_rel(t1, t0))
    if t_on:
        s_ = np.radians(ang_rel(T.t, t0)) * r
        ok &= (s_ % (t_on + t_off)) < t_on
    return ok


def seta_tri(T, p, d, comp=4.2, larg=3.4):
    """O triângulo cheio com a ponta em p, apontando na direção d (px da final)."""
    d = np.asarray(d, np.float64) / np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    base = np.asarray(p) - d * comp
    a, b = base + n * larg / 2, base - n * larg / 2
    pts = [np.asarray(p), a, b]

    def lado(p1, p2):
        return (p2[0] - p1[0]) * (T.y - p1[1]) - (p2[1] - p1[1]) * (T.x - p1[0])
    s1, s2, s3 = lado(pts[0], pts[1]), lado(pts[1], pts[2]), lado(pts[2], pts[0])
    return ((s1 >= 0) & (s2 >= 0) & (s3 >= 0)) | ((s1 <= 0) & (s2 <= 0) & (s3 <= 0))


def ponto(t, r):
    cx, cy = G["c"]
    return np.array([cx + r * np.cos(np.radians(t)), cy - r * np.sin(np.radians(t))])


def tangente(t):
    """A direção da subida (anti-horária na tela) no ângulo t."""
    return np.array([-np.sin(np.radians(t)), -np.cos(np.radians(t))])


def compor(reg, a, cor):
    a = np.clip(a, 0, 1)[..., None]
    return reg * (1 - a) + np.asarray(cor, np.float32) * a


def texto(reg, T, txt, centro, corpo, cor, fonte=FONTE_K, reforco=0.25, giro=0.0):
    """O texto (Kalam) centrado em `centro` (px da final), corpo em px da final."""
    s = T.s
    f = ImageFont.truetype(str(fonte), max(6, int(round(corpo * s * 4))))
    x0, y0, x1, y1 = f.getbbox(txt)
    w, h = x1 - x0 + 40, y1 - y0 + 40
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).text((20 - x0, 20 - y0), txt, font=f, fill=255,
                            stroke_width=max(0, int(round(reforco * s * 4))), stroke_fill=255)
    if giro:
        im = im.rotate(giro, resample=Image.BICUBIC, expand=True)
    a = np.asarray(im, np.float32) / 255.0
    a = cv2.resize(a, (max(1, a.shape[1] // 4), max(1, a.shape[0] // 4)), interpolation=cv2.INTER_AREA)
    X0, Y0 = T.X0, T.Y0
    cxp = (centro[0] - T.org[0]) * s - X0
    cyp = (centro[1] - T.org[1]) * s - Y0
    ox, oy = int(round(cxp - a.shape[1] / 2)), int(round(cyp - a.shape[0] / 2))
    H, W = reg.shape[:2]
    xa, ya, xb, yb = max(ox, 0), max(oy, 0), min(ox + a.shape[1], W), min(oy + a.shape[0], H)
    sub = a[ya - oy:yb - oy, xa - ox:xb - ox]
    reg[ya:yb, xa:xb] = compor(reg[ya:yb, xa:xb], sub, cor)
    return reg


# ----------------------------------------------------------------------------------------------------------------------
def base(reg, T, piso):
    """O piso da garagem sob a escada inteira (e um pouco além do círculo)."""
    dentro = T.reduz(T.r <= G["R"] + 2.8)
    return compor(reg, dentro, 0) + piso * dentro[..., None]


def degraus_vis(T):
    """O índice do degrau deste nível (0 = o arranque, 1..7) em cada subpixel, ou -1."""
    rel = ang_rel(T.t, G["a0"])
    k = np.floor(rel / G["passo"]).astype(np.int32)
    ok = (T.r > G["rc"]) & (T.r <= G["R"]) & (k < G["n_vis"])
    return np.where(ok, k, -1)


def cima(T):
    rel = ang_rel(T.t, G["a0"])
    return (T.r > G["rc"]) & (T.r <= G["R"]) & (rel >= G["n_vis"] * G["passo"])


def de_cima():
    """Os raios (os índices) que ficam na parte de cima, depois do corte (sem os que caem sobre os degraus deste
    nível: o 20 e o 21 passam por cima do arranque e do degrau 1)."""
    return [i for i in range(G["n_vis"], G["n_tot"] + 1)
            if ang_rel(limites(i), G["a0"]) >= G["n_vis"] * G["passo"] - 1e-6 or i == G["n_vis"]]


def limites(i):
    return (G["a0"] + i * G["passo"]) % 360.0


def pilar(reg, T):
    reg = compor(reg, T.reduz(T.r <= G["rc"]), COR["pilar"])
    return compor(reg, T.reduz(np.abs(T.r - G["rc"] * 0.62) < 0.25) * 0.35, (120, 120, 122))


def polilinha(T, pts, larg):
    """Os segmentos entre os pontos (px da final), com a largura larg."""
    ok = np.zeros(T.r.shape, bool)
    for p, q in zip(pts[:-1], pts[1:]):
        p, q = np.asarray(p, np.float64), np.asarray(q, np.float64)
        d = q - p
        L2 = max(float(d @ d), 1e-9)
        u = np.clip(((T.x - p[0]) * d[0] + (T.y - p[1]) * d[1]) / L2, 0, 1)
        ok |= np.hypot(T.x - p[0] - u * d[0], T.y - p[1] - u * d[1]) < larg / 2
    return ok


def quebra(T, a, larg=0.34):
    """A linha de quebra (o corte do nível) no raio a: reta com o Z no meio."""
    rm = (G["rc"] + G["R"]) / 2
    n = np.array([np.sin(np.radians(a)), np.cos(np.radians(a))])        # a normal ao raio (na tela)
    pts = [ponto(a, G["rc"]), ponto(a, rm - 1.8), ponto(a, rm - 0.7) + n * 2.2, ponto(a, rm + 0.7) - n * 2.2,
           ponto(a, rm + 1.8), ponto(a, G["R"] + 1.2)]
    return polilinha(T, pts, larg)


# ----------------------------------------------------------------------------------------------------------------------
def opcao1(reg, T, TT, piso):
    reg = base(reg, T, piso)
    k = degraus_vis(T)
    # os de cima: o piso sob um véu claro leve, os tracejados
    up = T.reduz(cima(T))
    reg = compor(reg, up * 0.38, COR["degrau"])
    tr = np.zeros(k.shape, bool)
    for i in de_cima():
        tr |= tracejado(T, limites(i))
    tr |= arco(T, G["R"], limites(G["n_vis"]), G["a0"], t_on=2.2)
    reg = compor(reg, T.reduz(tr) * 0.85, COR["traco"])
    # os deste nível: o degrau com a textura leve, a sombra curta do degrau de cima, o bocel
    tom = TT / np.maximum(TT.reshape(-1, 3).mean(0), 1.0)
    pedra = np.float32(COR["degrau"]) * (0.55 + 0.45 * tom)
    som = np.zeros(k.shape, np.float32)
    for i in range(G["n_vis"]):
        d = dist_raio(T, limites(i + 1))
        lado = (k == i)
        som = np.maximum(som, np.where(lado, np.exp(-d / 1.5), 0))
    luz = T.reduz((1 - 0.26 * som) * (k >= 0))
    claro = np.zeros(k.shape, np.float32)
    for i in range(G["n_vis"]):
        claro += np.where(k == i, 1.0 + 0.012 * i, 0)
    claro = T.reduz(claro)
    av = T.reduz(k >= 0)
    deg = pedra * (luz / np.maximum(av, 1e-3) * claro / np.maximum(av, 1e-3))[..., None]
    reg = compor(reg, av, 0) + deg * av[..., None]
    bocel = np.zeros(k.shape, bool)
    for i in range(1, G["n_vis"]):
        bocel |= (dist_raio(T, limites(i)) < 0.17) & (k >= 0)
    bocel |= (dist_raio(T, limites(0)) < 0.17) & (np.abs(ang_rel(T.t, limites(0)) - 2) < 30) & (T.r <= G["R"])
    bocel |= arco(T, G["R"] - 0.15, G["a0"], limites(G["n_vis"]), larg=0.36)
    reg = compor(reg, T.reduz(bocel), COR["linha"])
    reg = compor(reg, T.reduz(quebra(T, limites(G["n_vis"]))), COR["linha"])
    reg = pilar(reg, T)
    # a linha de caminhamento: o círculo no arranque, a seta no corte
    t0, t1 = G["a0"] + 3.0, limites(G["n_vis"]) - 5.0
    cam = arco(T, G["rcam"], t0 + 2.4, t1 - 1.0, larg=0.28)
    circ = np.abs(np.hypot(T.x - ponto(t0, G["rcam"])[0], T.y - ponto(t0, G["rcam"])[1]) - 1.25) < 0.16
    ponta = ponto(t1 + 2.0, G["rcam"])
    st = seta_tri(T, ponta, tangente(t1), comp=3.6, larg=2.8)
    reg = compor(reg, T.reduz(cam | circ | st), COR["linha"])
    reg = texto(reg, T, "S", tuple(ponto(G["a0"] - 9.0, G["rcam"] + 1.0)), 6.2, COR["texto"])
    return reg


def opcao2(reg, T, TT, piso):
    reg = base(reg, T, piso)
    rel = ang_rel(T.t, G["a0"])
    dentro = (T.r > G["rc"]) & (T.r <= G["R"])
    i = np.floor(rel / G["passo"]).astype(np.int32)
    vis = dentro & (i < G["n_vis"])
    up = dentro & ~vis
    tom = TT / np.maximum(TT.reshape(-1, 3).mean(0), 1.0)
    pedra = np.float32(COR["degrau"]) * (0.55 + 0.45 * tom)
    # o tom pela altura: do arranque (mais fundo) ao corte (mais claro)
    f = 0.86 + 0.24 * np.clip(i / max(G["n_vis"] - 1, 1), 0, 1)
    fv = T.reduz(np.where(vis, f, 0))
    av = T.reduz(vis)
    reg = compor(reg, av, 0) + pedra * (fv / np.maximum(av, 1e-3))[..., None] * av[..., None]
    # os de cima em vidro fosco: o piso atrás, clareado, as arestas finas
    au = T.reduz(up)
    reg = compor(reg, au * 0.36, (238, 238, 234))
    ar_up = np.zeros(i.shape, bool)
    ar_vis = np.zeros(i.shape, bool)
    for j in range(1, G["n_tot"] + 1):
        a = limites(j)
        lin = (dist_raio(T, a) < 0.15) & dentro & (np.abs(ang_rel(T.t, a + 180) - 180) < 90)
        if j in de_cima():
            ar_up |= lin & up
        elif j <= G["n_vis"]:
            ar_vis |= lin & vis
    reg = compor(reg, T.reduz(ar_up) * 0.55, (150, 154, 160))
    reg = compor(reg, T.reduz(ar_vis), COR["linha"])
    borda_v = arco(T, G["R"] - 0.15, G["a0"], limites(G["n_vis"]), larg=0.36)
    borda_u = arco(T, G["R"] - 0.15, limites(G["n_vis"]), G["a0"], larg=0.30)
    reg = compor(reg, T.reduz(borda_v), COR["linha"])
    reg = compor(reg, T.reduz(borda_u) * 0.6, (150, 154, 160))
    reg = compor(reg, T.reduz((dist_raio(T, G["a0"]) < 0.17) & dentro & (np.abs(ang_rel(T.t, G["a0"])) < 90)),
                 COR["linha"])
    reg = pilar(reg, T)
    # a linha de caminhamento em espiral: cheia neste nível, tracejada em cima, a seta na chegada
    t_ini = G["a0"] + 3.0
    tot = G["n_tot"] * G["passo"] - 8.0
    rr = lambda t: 33.5 - 9.0 * np.clip(ang_rel(t, t_ini) / tot, 0, 1)     # noqa: E731
    relc = ang_rel(T.t, t_ini)
    alvo = rr(T.t)
    linha = (np.abs(T.r - alvo) < 0.15) & (relc <= tot - 1.0) & (relc > 2.0)
    cheia = linha & (relc <= G["n_vis"] * G["passo"] - 3.0)
    s_ = np.radians(relc) * alvo
    trac = linha & ~cheia & ((s_ % 3.4) < 2.0)
    circ = np.abs(np.hypot(T.x - ponto(t_ini, rr(t_ini))[0], T.y - ponto(t_ini, rr(t_ini))[1]) - 1.25) < 0.16
    t_fim = t_ini + tot
    ponta = ponto(t_fim + 1.5, rr(t_fim))
    st = seta_tri(T, ponta, tangente(t_fim) + np.array([0.0, 0.0]), comp=3.6, larg=2.8)
    reg = compor(reg, T.reduz(cheia | circ | st), COR["linha"])
    reg = compor(reg, T.reduz(trac) * 0.9, COR["traco"])
    reg = texto(reg, T, "S", tuple(ponto(G["a0"] - 9.0, 34.5)), 6.2, COR["texto"])
    return reg


def opcao3(reg, T, TT, piso):
    reg = base(reg, T, piso)
    k = degraus_vis(T)
    av = T.reduz(k >= 0)
    reg = compor(reg, av, COR["degrau"])
    # as frestas claras entre os degraus e o contorno nítido
    fr = np.zeros(k.shape, bool)
    for i in range(1, G["n_vis"]):
        fr |= (dist_raio(T, limites(i)) < 0.22) & (k >= 0)
    reg = compor(reg, T.reduz(fr), COR["fresta"])
    cont = arco(T, G["R"] - 0.15, G["a0"], limites(G["n_vis"]), larg=0.36)
    for a in (G["a0"], limites(G["n_vis"])):
        cont |= (dist_raio(T, a) < 0.18) & (T.r <= G["R"]) & (T.r > G["rc"]) & (np.abs(ang_rel(T.t, a + 180) - 180) < 90)
    reg = compor(reg, T.reduz(cont), COR["linha"])
    # os de cima: só o tracejado sobre o piso
    tr = np.zeros(k.shape, bool)
    for i in de_cima():
        tr |= tracejado(T, limites(i), larg=0.36)
    tr |= arco(T, G["R"], limites(G["n_vis"]), G["a0"], larg=0.36, t_on=2.2)
    reg = compor(reg, T.reduz(tr), (226, 228, 230))
    reg = pilar(reg, T)
    # o ▶ no primeiro degrau, no sentido da subida, e o S ao lado
    tm = G["a0"] + G["passo"] * 0.55
    p = ponto(tm + 7.0, 33.0)
    st = seta_tri(T, p, tangente(tm), comp=8.0, larg=7.0)
    reg = compor(reg, T.reduz(st), (28, 28, 30))
    reg = texto(reg, T, "S", tuple(ponto(G["a0"] - 8.0, 34.5)), 6.2, COR["texto"])
    return reg


# ----------------------------------------------------------------------------------------------------------------------
def main():
    c, pav = PLANTA.split("_")
    final = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_B.jpg"
    im = cv2.cvtColor(np.array(Image.open(rel).convert("RGB")), cv2.COLOR_RGB2BGR)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    x0, y0, x1, y1 = CAIXA
    mapa, cc = EP.registro_12k(final, cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), dz,
                               (int(x0) - 40, int(y0) - 40, int(x1) + 40, int(y1) + 40))
    A, B = mapa(x0, y0)
    s = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
    org = (x0 - A / s, y0 - B / s)
    X0, Y0 = int(round((x0 - org[0]) * s)), int(round((y0 - org[1]) * s))
    X1, Y1 = int(round((x1 - org[0]) * s)), int(round((y1 - org[1]) * s))
    atual = im[Y0:Y1, X0:X1].copy()
    # o piso da garagem: image quilting do trecho à esquerda da escada
    sys.path.insert(0, str(EP.PROJ / "_texturas"))
    import texturas
    fx0, fy0, fx1, fy1 = PISO_FONTE
    F = im[int((fy0 - org[1]) * s):int((fy1 - org[1]) * s), int((fx0 - org[0]) * s):int((fx1 - org[0]) * s)]
    lisa = cv2.GaussianBlur(F.astype(np.float32), (0, 0), 6.0 * s)
    Fd = np.clip(F.astype(np.float32) / np.maximum(lisa, 1) * F.reshape(-1, 3).mean(0), 0, 255).astype(np.uint8)
    p = int(round(8 * s))
    piso = texturas.quilting([Fd, np.ascontiguousarray(Fd[:, ::-1]), np.ascontiguousarray(Fd[::-1])],
                             Y1 - Y0, X1 - X0, p=p, sobra=max(3, p // 3),
                             rng=np.random.default_rng(5))[:Y1 - Y0, :X1 - X0].astype(np.float32)
    T = Tela(atual.shape[:2], s, org, X0, Y0)
    T.X0, T.Y0, T.org = X0, Y0, org
    TT = D.piso_tt((X0, Y0, X1, Y1), s, giro=True)
    paineis = [("Atual", "", atual)]
    textos = [("Opção 1 · corte clássico", ["degraus deste nível cheios, com bocel", "e sombra do degrau de cima; corte em",
                                            "quebra; os de cima transparentes", "(véu leve + tracejado); seta no corte"]),
              ("Opção 2 · subida em degradê", ["o tom clareia conforme sobe; acima do",
                                               "corte, vidro fosco (o piso aparece);",
                                               "caminhamento em espiral pela volta", "inteira, seta na chegada ao 1º pav."]),
              ("Opção 3 · gráfica", ["degraus deste nível num tom só, com", "frestas claras e contorno nítido; os de",
                                     "cima só tracejados sobre o piso;", "a seta no 1º degrau, no sentido da subida"])]
    for (tit, desc), fn in zip(textos, (opcao1, opcao2, opcao3)):
        reg = fn(atual.astype(np.float32).copy(), T, TT, piso)
        paineis.append((tit, desc, np.clip(np.round(reg), 0, 255).astype(np.uint8)))
    # a prancha das opções
    h, w = atual.shape[:2]
    gap, topo, rod = 24, 64, 150
    folha = Image.new("RGB", (4 * w + 5 * gap, h + topo + rod + gap), (255, 255, 255))
    dr = ImageDraw.Draw(folha)
    ft, fl = ImageFont.truetype(str(FONTE_T), 26), ImageFont.truetype(str(FONTE_TL), 19)
    for j, (tit, desc, pim) in enumerate(paineis):
        x = gap + j * (w + gap)
        folha.paste(Image.fromarray(cv2.cvtColor(pim, cv2.COLOR_BGR2RGB)), (x, topo))
        dr.text((x, 18), tit, font=ft, fill=(30, 30, 30))
        for n, linha in enumerate(desc):
            dr.text((x, topo + h + 14 + n * 27), linha, font=fl, fill=(70, 70, 70))
    if not paineis[0][1]:
        dr.text((gap, topo + h + 14), "a seta aponta para fora, não no sentido", font=fl, fill=(70, 70, 70))
        dr.text((gap, topo + h + 41), "da subida; o travertino aparece dentro", font=fl, fill=(70, 70, 70))
        dr.text((gap, topo + h + 68), "do círculo, embaixo à direita", font=fl, fill=(70, 70, 70))
    out = EP.PROJ / "POE642_CasaA/renders/POE642_CasaA_PH_Terreo_2511_helicoidal_opcoes.jpg"
    folha.save(out, quality=93)
    print(out, folha.size, "registro", round(cc, 3), "escala", round(s, 3))


if __name__ == "__main__":
    main()

r"""O paisagismo do gramado (usuário, 11/11: "a área verde precisa ter coerencia entre arvores e arbustos, 80% da área
é grama. se conseguir melhorar o aspecto da grama, trazendo mais realismo, também é bem vindo").

- As plantas num desenho só: as árvores da biblioteca (`_texturas/vegetacao/arvore_*`, nítidas) e, no lugar dos arbustos
  borrados (`arbusto_1..3`, recortes de 86 px da referência), o arbusto nítido da biblioteca de blocos
  (`_blocos/recortes/arbusto.png`) em três verdes do mesmo grupo das copas das árvores, com alguns floridos (o
  `planta_flores` com as flores em branco, como as sebes da referência do quintal). A mesma luz para todas: a sombra
  para baixo e à esquerda (`_texturas/texturas.json`, `vegetacao.sombra`), a das árvores sobre os arbustos.
- 80% do gramado é grama: os canteiros ocupam ~20% (`alvo`). Duas composições: `A`, um canteiro contínuo junto aos
  muros, com a borda de dentro orgânica e alargado nos cantos, onde ficam as 4 árvores; `B`, maciços (meias-elipses
  encostadas nos muros), 4 nos cantos com as árvores e os outros só de arbustos.
- A grama (`grama_realista`): o mesmo padrão (cor e escala da referência do usuário de 07/11), com a variação de tom
  em manchas largas (de 1,5 a 9 m, como num gramado de verdade visto do alto), um pouco mais de contraste no fio (o
  desvio da referência é ~15, o da textura tecida ~8) e a sombra de contato junto aos muros e aos canteiros.
"""
import json
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]

PAISAGISMO = {
    "alvo": 0.20,                                   # a fração do gramado em canteiro (o resto, 80%, grama)
    "semente": 1111,
    # os verdes dos arbustos: o tom médio (BGR) de cada variedade, no grupo das copas das árvores da biblioteca
    "verdes": {"verde_escuro": (52, 92, 62), "verde_oliva": (58, 108, 92), "verde_azulado": (78, 108, 70)},
    "flor_branca": (226, 234, 238),
    "arbusto_m": (0.9, 1.4), "florido": 0.0, "denso": 0.62,
    "arvore_m": (3.2, 3.8),
    "canteiro": {"fundo": (34, 52, 46), "fundo_ruido": 0.10, "borda_px": 1.6},
    "A": {"faixa_m": 0.85, "faixa_var_m": 0.35, "var_escala_m": 7.0, "canto_m": 2.6},
    "B": {"comp_m": (7.5, 10.5), "fundo_m": (2.2, 3.0), "canto_m": 3.2},
    "grama": {"manchas": [(1.5, 0.035), (4.0, 0.045), (9.0, 0.035)], "matiz": (5.0, 3.0), "fio": 1.35,
              "fio_sig_m": 0.25, "contato_m": 0.45, "contato": 0.16, "canteiro_contato": 0.10},
}


# ----------------------------------------------------------------------------------------------------------------------
def ruido(shape, escala_px, rng):
    """Ruído suave (desvio 1) na escala dada."""
    h, w = shape
    ph, pw = max(3, int(h / escala_px) + 3), max(3, int(w / escala_px) + 3)
    n = cv2.resize(rng.standard_normal((ph, pw)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    n = cv2.GaussianBlur(n, (0, 0), max(0.5, escala_px / 4))
    return (n - n.mean()) / max(float(n.std()), 1e-6)


def _sprite(nome):
    for p in (RAIZ / "_texturas" / "vegetacao" / f"{nome}.png", RAIZ / "_blocos" / "recortes" / f"{nome}.png"):
        if p.exists():
            a = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
            break
    cor = a[..., :3].astype(np.float32)
    al = a[..., 3].astype(np.float32) / 255
    ys, xs = np.nonzero(al > 0.05)
    cor, al = cor[ys.min():ys.max() + 1, xs.min():xs.max() + 1], al[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    d = 2 * np.sqrt((al > 0.5).sum() / np.pi)
    return cor, al, d


def _tingir(cor, al, alvo, mistura=0.85):
    L = cor.mean(axis=2)
    Lm = float(L[al > 0.5].mean())
    novo = np.float32(alvo)[None, None, :] * (L / Lm)[..., None]
    return cor * (1 - mistura) + novo * mistura


def _flor_branca(cor, al, branco, folha):
    """O `planta_flores` com as flores (o rosa) em branco e as folhas no verde dado."""
    rosa = np.clip((cor[..., 2] - cor[..., 1] - 15) / 30, 0, 1)
    rosa = cv2.GaussianBlur(rosa, (0, 0), 0.7)
    L = cor.mean(axis=2)
    Lf = float(L[(rosa > 0.5) & (al > 0.5)].mean()) if ((rosa > 0.5) & (al > 0.5)).any() else 200.0
    flor = np.float32(branco)[None, None, :] * np.clip(L / Lf, 0.6, 1.1)[..., None]
    verde = _tingir(cor, al, folha, 0.9)
    return verde * (1 - rosa[..., None]) + flor * rosa[..., None]


def _colocar(cor, al, d0, d_px, giro):
    k = d_px / d0
    h, w = al.shape
    lado = int(np.ceil(max(h, w) * k * 1.05)) + 4
    M = cv2.getRotationMatrix2D((w / 2, h / 2), giro, k)
    M[0, 2] += lado / 2 - w / 2
    M[1, 2] += lado / 2 - h / 2
    c = cv2.warpAffine(cor, M, (lado, lado), flags=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = cv2.warpAffine(al, M, (lado, lado), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return c, np.clip(a, 0, 1)


def _somar(alvo, peca, cx, cy, op="max"):
    """Põe `peca` (2D) com o centro em (cx, cy) em `alvo` (2D), pelo máximo."""
    h, w = peca.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(alvo.shape[1], x0 + w), min(alvo.shape[0], y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return None
    sl = (slice(fy0, fy1), slice(fx0, fx1))
    ps = (slice(fy0 - y0, fy1 - y0), slice(fx0 - x0, fx1 - x0))
    return sl, ps


def _camada(fundo, pecas, limite, sombra_cfg):
    """Uma camada de plantas (cada uma: cor, alfa, cx, cy, d_px): primeiro a sombra de todas (o máximo), depois as
    copas, todas recortadas no `limite` (alfa 0..1)."""
    H, W = fundo.shape[:2]
    S = np.zeros((H, W), np.float32)
    for c, a, cx, cy, d in pecas:
        s = cv2.GaussianBlur(a, (0, 0), max(0.5, sombra_cfg["desfoque"] * d)) * sombra_cfg["opacidade"]
        r = _somar(S, s, cx + sombra_cfg["dx"] * d, cy + sombra_cfg["dy"] * d)
        if r:
            sl, ps = r
            S[sl] = np.maximum(S[sl], s[ps])
    S *= limite
    fundo *= (1 - 0.65 * S)[..., None]
    for c, a, cx, cy, d in pecas:
        r = _somar(S, a, cx, cy)
        if r:
            sl, ps = r
            aa = (a[ps] * limite[sl])[..., None]
            fundo[sl] = fundo[sl] * (1 - aa) + c[ps] * aa
    return fundo


# ----------------------------------------------------------------------------------------------------------------------
def grama_realista(img, m, px_m, q=None, canteiro=None, muro=None, rng=None):
    """A grama do padrão com a variação de tom em manchas largas, mais contraste no fio e a sombra de contato junto
    aos muros (`muro`, bool) e aos canteiros (`canteiro`, bool). Só nos px de `m`."""
    q = q or PAISAGISMO["grama"]
    rng = rng or np.random.default_rng(PAISAGISMO["semente"])
    out = img.astype(np.float32).copy()
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = out[y0:y1, x0:x1]
    mm = m[y0:y1, x0:x1]
    # o fio: o detalhe fino com um pouco mais de contraste
    base = cv2.GaussianBlur(sub, (0, 0), q["fio_sig_m"] * px_m)
    sub = base + (sub - base) * q["fio"]
    # as manchas: a luz em três escalas e o matiz (mais amarelado / mais azulado) numa quarta
    f = np.ones(mm.shape, np.float32)
    for esc, amp in q["manchas"]:
        f += amp * ruido(mm.shape, esc * px_m, rng)
    sub = sub * f[..., None]
    t = ruido(mm.shape, q["matiz"][0] * px_m, rng) * q["matiz"][1]
    sub[..., 0] -= t * 0.6
    sub[..., 2] += t * 0.4
    # o contato: mais escuro junto aos muros e aos canteiros (a distância dentro da grama)
    if muro is not None or canteiro is not None:
        escuro = np.zeros(mm.shape, np.float32)
        for msk, forca in ((muro, q["contato"]), (canteiro, q["canteiro_contato"])):
            if msk is None or not msk[y0:y1, x0:x1].any():
                continue
            dist = cv2.distanceTransform((~msk[y0:y1, x0:x1]).astype(np.uint8), cv2.DIST_L2, 5)
            escuro = np.maximum(escuro, forca * np.exp(-dist / (q["contato_m"] * px_m)))
        sub = sub * (1 - escuro)[..., None]
    # o tom médio da grama fica o de antes (usuário: "preserve 80% da área em grama realista no tom que já temos"):
    # a mediana fora da sombra de contato volta à mediana de antes
    longe = mm & (escuro < 0.01) if (muro is not None or canteiro is not None) else mm
    antes = np.median(img[y0:y1, x0:x1][longe].astype(np.float32), axis=0)
    agora = np.median(sub[longe], axis=0)
    sub = sub * (antes / np.maximum(agora, 1))[None, None, :]
    out[y0:y1, x0:x1] = np.where(mm[..., None], sub, out[y0:y1, x0:x1])
    return out


def _cabe(ok, cx, cy, r):
    H, W = ok.shape
    if cx - r < 0 or cy - r < 0 or cx + r >= W or cy + r >= H:
        return False
    yy, xx = np.ogrid[int(cy - r):int(cy + r) + 1, int(cx - r):int(cx + r) + 1]
    disco = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
    return bool(ok[int(cy - r):int(cy + r) + 1, int(cx - r):int(cx + r) + 1][disco].all())


def canteiros(m, lote, px_m, opcao, arvores_px, q=None, rng=None):
    """A máscara dos canteiros (bool) dentro do gramado `m`: `A` a faixa junto aos muros do `lote` (x0, y0, x1, y1),
    alargada em volta das árvores; `B` os maciços. Ajusta a largura até ~`alvo` do gramado."""
    q = q or PAISAGISMO
    rng = rng or np.random.default_rng(q["semente"])
    H, W = m.shape
    x0, y0, x1, y1 = lote
    yy, xx = np.mgrid[0:H, 0:W]
    dm = np.minimum.reduce([xx - x0, x1 - xx, yy - y0, y1 - yy]).astype(np.float32)
    var = ruido((H, W), q["A"]["var_escala_m"] * px_m, rng)
    alvo = q["alvo"] * m.sum()
    if opcao == "A":
        a = q["A"]
        canto = np.zeros((H, W), bool)
        for cx, cy in arvores_px:
            canto |= (xx - cx) ** 2 + (yy - cy) ** 2 <= (a["canto_m"] * px_m) ** 2
        lo, hi = 0.2, 3.0
        for _ in range(18):                         # a largura média que dá o alvo
            f = (lo + hi) / 2
            c = m & ((dm < (f * a["faixa_m"] + a["faixa_var_m"] * var) * px_m) | canto)
            lo, hi = (f, hi) if c.sum() < alvo else (lo, f)
        return c
    b = q["B"]
    # os maciços: encostados nos muros, os 4 dos cantos (com as árvores) e os outros ao longo dos muros, onde o
    # gramado tem fundo para eles
    centros = []
    for cx, cy in arvores_px:
        centros.append((cx, cy, b["canto_m"], b["canto_m"], 0.0))
    passos = []
    for (ax, ay), (bx, by), nx, ny in (((x0, y0), (x1, y0), 0, 1), ((x0, y1), (x1, y1), 0, -1),
                                       ((x0, y0), (x0, y1), 1, 0), ((x1, y0), (x1, y1), -1, 0)):
        L = np.hypot(bx - ax, by - ay)
        t = rng.uniform(6, 9) * px_m
        while t < L - 4 * px_m:
            passos.append((ax + (bx - ax) * t / L, ay + (by - ay) * t / L, nx, ny))
            t += rng.uniform(11, 15) * px_m
    rng.shuffle(passos)
    c = np.zeros((H, W), bool)
    for cx, cy, rx, ry, _ in centros:
        c |= m & (((xx - cx) / (rx * px_m)) ** 2 + ((yy - cy) / (ry * px_m)) ** 2 <= 1)
    for wx, wy, nx, ny in passos:
        if c.sum() >= alvo:
            break
        comp = rng.uniform(*b["comp_m"]) / 2 * px_m
        fundo = rng.uniform(*b["fundo_m"]) * px_m
        if any(np.hypot(wx - u, wy - v) < 6 * px_m for u, v in arvores_px):
            continue
        # o eixo ao longo do muro e o fundo para dentro do lote
        al_x, al_y = (1, 0) if nx == 0 else (0, 1)
        u = (xx - wx) * al_x + (yy - wy) * al_y
        v = (xx - wx) * nx + (yy - wy) * ny
        forma = (u / comp) ** 2 + (np.maximum(v, 0) / fundo) ** 2 <= 1 + 0.12 * var
        novo = m & forma & (v >= -2)
        if novo.sum() < 0.5 * np.pi * comp * fundo * 0.5:      # o gramado não tem fundo aqui
            continue
        c |= novo
    return c


def paisagismo(img, m, px_m, lote, arvores, opcao="A", q=None, limite=None, rotulos_fora=None):
    """O gramado (`m`) com a grama realista, os canteiros e as plantas. `arvores`: [(nome, (cx, cy), d_m)] (os
    lugares das 4 árvores; o tamanho vem de `arvore_m`). Devolve (imagem float32, máscara dos canteiros)."""
    q = q or PAISAGISMO
    rng = np.random.default_rng(q["semente"])
    sombra = json.loads((RAIZ / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    ok = cv2.erode(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    # as árvores: no lugar de antes, andando para dentro se a copa não couber
    H, W = m.shape
    pos = []
    for i, (nome, (cx, cy), _) in enumerate(arvores):
        d = rng.uniform(*q["arvore_m"])
        r = d / 2 * px_m * 0.75
        for passo in range(0, 160, 8):
            ux = cx + (passo if cx < W / 2 else -passo)
            uy = cy + (passo if cy < H / 2 else -passo)
            if _cabe(ok, ux, uy, r):
                pos.append((nome, ux, uy, d))
                break
    cant = canteiros(m, lote, px_m, opcao, [(x, y) for _, x, y, _ in pos], q, rng)
    # a sombra de contato: junto a tudo o que não é grama (muros, casa, pisos) e aos canteiros
    out = grama_realista(img, m, px_m, q["grama"], canteiro=cant, muro=~m, rng=rng)
    # o chão do canteiro: a sombra verde-escura sob as folhagens, com a borda macia
    cf = q["canteiro"]
    chao = np.float32(cf["fundo"])[None, None, :] * (1 + cf["fundo_ruido"] * ruido((H, W), 0.4 * px_m, rng))[..., None]
    ac = cv2.GaussianBlur(cant.astype(np.float32), (0, 0), cf["borda_px"]) * m
    out = out * (1 - ac[..., None]) + chao * ac[..., None]
    # os arbustos: os sprites tingidos nas três variedades e os floridos
    cor0, al0, d0 = _sprite("arbusto")
    fcor, fal, fd0 = _sprite("planta_flores")
    variedades = {k: _tingir(cor0, al0, v) for k, v in q["verdes"].items()}
    nomes_v = list(variedades)
    pecas = []
    dentro = cv2.erode(cant.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    pts = np.argwhere(dentro)
    rng.shuffle(pts)
    feitos = []
    alvo_n = int(cant.sum() / (np.pi * (np.mean(q["arbusto_m"]) / 2 * px_m) ** 2) / q["denso"] * 1.0)
    # um verde por trecho (as variedades em grupos, não salpicadas)
    grupo = ruido((H, W), 5 * px_m, rng)
    for yx in pts:
        if len(feitos) >= alvo_n:
            break
        cy, cx = float(yx[0]), float(yx[1])
        d = rng.uniform(*q["arbusto_m"]) * px_m
        if any((cx - u) ** 2 + (cy - v) ** 2 < (q["denso"] * (d + e) / 2) ** 2 for u, v, e in feitos):
            continue
        if any(np.hypot(cx - x, cy - y) < 0.3 * dd * px_m for _, x, y, dd in pos):
            continue
        feitos.append((cx, cy, d))
        g = grupo[int(cy), int(cx)]
        if rng.random() < q["florido"]:
            c, a = _colocar(_flor_branca(fcor, fal, q["flor_branca"], q["verdes"]["verde_escuro"]), fal, fd0,
                            d * 0.85, rng.uniform(0, 360))
        else:
            k = nomes_v[0] if g < -0.4 else (nomes_v[1] if g < 0.5 else nomes_v[2])
            c, a = _colocar(variedades[k], al0, d0, d, rng.uniform(0, 360))
        pecas.append((c, a, cx, cy, d))
    pecas.sort(key=lambda p: p[3])
    lim = limite if limite is not None else cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.7)
    out = _camada(out, pecas, lim, sombra)
    # as árvores por cima (a sombra delas sobre os arbustos e a grama)
    arv = []
    for nome, cx, cy, d in pos:
        c, a, dd0 = _sprite(nome)
        c2, a2 = _colocar(c, a, dd0, d * px_m, rng.uniform(0, 360))
        arv.append((c2, a2, cx, cy, d * px_m))
    out = _camada(out, arv, lim, sombra)
    print(f"    paisagismo {opcao}: canteiros em {cant.sum() / m.sum() * 100:.1f}% do gramado "
          f"({cant.sum() / px_m ** 2:.0f} de {m.sum() / px_m ** 2:.0f} m²), {len(pecas)} arbustos, {len(arv)} árvores")
    return out, cant

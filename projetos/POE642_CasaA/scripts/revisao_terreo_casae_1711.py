"""Térreo da Casa E, 17/11, na final e direto nos 12K A (Inter) e B (Kalam), no afim afinado em cada caixa. As escolhas
do usuário sobre a proposta da varanda, os tracejados e o levantamento de 17/11:

1. `levantamento` (o levantamento de 17/11, `POE642_CasaE_PH_Terreo_1711_levantamento.jpg`; usuário: os quatro itens):
   - faixas escuras: na cozinha, o piso escuro antigo dos dois lados da folha de correr (entre os dois tocos de parede);
     na despensa, a faixa escura entre a parede e a folha (o fio da parede fica); na garagem, a linha escura contínua
     que atravessava o piso (o lugar dela é a projeção da laje da garagem, que volta tracejada no item 3);
     o piso do lado no lugar (`instalacao_terreo_casad_1711._remenda`);
   - DCE: a mancha escura junto ao criado-mudo sai e o criado-mudo (em granito pintado) vai à cor sólida dos armários
     da E (a do louceiro), no retângulo do PDF até a parede, com o fio e a sombra curta;
   - living: o pontilhado por dentro das cortinas da fachada (a coluna x 1599) e os 6 pontinhos soltos no travertino.
2. `varanda` (usuário: "3. Linho e nogueira"): a alternativa 3 da proposta (`proposta_varanda_casae_1711`): o sofá
   reto de linho, as 2 poltronas creme com aro de madeira, a mesa de centro gota de nogueira, a mesa lateral de metal e
   madeira, o banco B1, as mesas redondas de nogueira com as cadeiras creme e madeira. No 12K, o piso limpo é o da final
   (a baixa frequência) com o grão do Bege Bahia limpo do próprio 12K, e as peças vão direto na escala do 12K.
3. `tracejados` (usuário: "Térreo no cinza fino"): o X do hall (escuro) e o X da área de serviço descoberta (branco)
   em cinza e 0,8 px, o traço do 1º Pavimento (`revisao_1pav_casae_1711`): cinza 128 no fundo claro, cinza 200 no
   escuro; o traço antigo sai (o piso deslocado na perpendicular, só onde ele destoa), os rótulos ficam; os trechos
   novos só onde o antigo estava (os vãos dos rótulos ficam). A projeção da laje da garagem (`TRACEJADOS_TE`, a 1ª
   linha), que estava em linha contínua escura, volta tracejada, no cinza do fundo escuro.

  python3 revisao_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 revisao_terreo_casae_1711.py final
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
KALAM = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_rotulos_kalam.json"

# 1. (retângulo px da final, deslocamentos da fonte px, filtro de `_remenda`, limiar)
LEVANTAMENTO = {
    "cozinha": [((1572.5, 646.0, 1583.5, 744.0), [(-12, 0), (-16, 0)], None, 0),
                ((1587.5, 646.0, 1590.5, 744.0), [(6, 0), (9, 0)], None, 0),
                ((1583.5, 737.0, 1587.5, 744.0), [(8, 0), (10, 0)], None, 0)],
    "despensa": [((2226.5, 716.0, 2232.5, 759.0), [(11, 0), (14, 0)], "escuro", 20)],
    "DCE (mancha)": [((2355.0, 553.0, 2361.5, 569.0), [(-9, 0), (-13, 0)], "escuro", 10)],
    "garagem": [((2489.5, 483.5, 3036.5, 488.5), [(0, -6), (0, 7)], "escuro", 12)],
    "living (pontilhado)": [((1597.5, 985.0, 1601.5, 1295.0), [(4, 0), (5, 0)], "escuro", 6)],
    "travertino (pontinhos)": [((x - 1.5, y - 1.5, x + w + 1.5, y + h + 1.5), [(7, 0), (-7, 0), (0, -8)], "escuro", 10)
                               for x, y, w, h in ((1692, 851, 3, 7), (1794, 875, 3, 9), (1850, 883, 3, 6),
                                                  (1811, 934, 2, 5), (1869, 983, 3, 3), (1793, 1234, 2, 8))]}
# o criado-mudo do DCE (o retângulo do PDF, px, até a face da parede) na cor sólida dos armários da E (o louceiro)
CRIADO = {"ret": (2361.5, 554.0, 2386.9, 574.9), "cor": (129, 160, 189), "fio": (111, 138, 163), "fio_px": 0.6,
          "sombra": 0.28}

# 3. os grupos do PDF (`final3840_casae._tracos_te`) e a projeção da garagem (o nome e o trecho em x, px)
TRACEJADOS = {"grupos": {"hall": ("DOC 45.0°", "DOC 90.0°", "DOC 138.5°"),
                         "área de serviço descoberta": ("DOC 0.0°", "DOC 15.0°", "DOC 158.5°")},
              # (17/11, usuário: "tire. não haverá tracejado para projeções") a projeção da laje da garagem não volta
              "garagem": None,
              "caixas": {"hall": (2215, 1315, 2495, 1595), "área de serviço descoberta": (1940, 420, 2230, 550),
                         "garagem": (2480, 466, 3046, 506)},
              "rotulos": ("HALL DE ENTRADA", "ÁREA DE SERVIÇO DESCOBERTA"),
              "cinza": (128, 128, 128), "cinza_escuro": (200, 200, 200), "limiar": 120, "larg_px": 0.8,
              "limpa_px": 1.9, "desloc_px": 4.5, "destoa": 8, "passo_px": 0.5, "ss": 4}


def _local(out, mp, caixa):
    return mp.local(out, caixa) if mp.ref is not None else mp


def _caixa(r, folga=25):
    return (int(r[0]) - folga, int(r[1]) - folga, int(np.ceil(r[2])) + folga, int(np.ceil(r[3])) + folga)


def _afim(m):
    """O afim 2 x 3 (índices de px) da final à imagem: i' = s i + t."""
    return np.float32([[m.s, 0, m.t[0]], [0, m.s, m.t[1]]])


# ----------------------------------------------------------------------------------------------------------------------
def levantamento(out, mp, q=LEVANTAMENTO, c=CRIADO):
    import instalacao_terreo_casad_1711 as ID
    for nome, itens in q.items():
        for r, ds, filtro, lim in itens:
            m = _local(out, mp, _caixa(r))
            ID._remenda(out, m, r, ds, filtro, lim)
    m = _local(out, mp, _caixa(c["ret"]))
    CB.sombra(out, m, c["ret"], c["sombra"], dx=-0.8, dy=0.8, sigma=0.8)
    CB.pintar(out, m, [(c["ret"], "ret", c["cor"], 0), (c["ret"], "contorno", c["fio"], c["fio_px"])])
    print(f"    levantamento: {', '.join(q)}; o criado-mudo do DCE na cor sólida dos armários")


# ----------------------------------------------------------------------------------------------------------------------
def _buraco_varanda(img, par):
    """A máscara do que sai da varanda (px da final), como `proposta_varanda_casae_1711.limpar`, e o que fica."""
    import mobiliario_terreo_casae_1611 as M
    import proposta_varanda_casae_1711 as PV
    H, W = img.shape[:2]
    q = M.VARANDA
    M.PISOS["bege"] = PV.LUGARES["bege"]
    buraco = np.zeros((H, W), bool)
    for mesa, cads in q["mesas"]:
        buraco |= M.ret(mesa, 6)((H, W))
        for cc in cads:
            buraco |= M.ret(cc, 6)((H, W))
        x0, y0, x1, y1 = mesa
        buraco |= M.objeto_imagem(img, (x0 - 44, y0 - 44, x1 + 44, y1 + 44), "bege", limiar=24, folga=3)
    for cx in PV.LUGARES["limpar"]:
        buraco |= M.objeto_imagem(img, cx, "bege", limiar=24, folga=3)
    fica = M.ret((1577, 1240, 1600, 1580))((H, W)) | M.ret((1510, 1436, 1590, 1566))((H, W)) | \
        M.ret(PV.LUGARES["rotulo"])((H, W))
    return buraco & ~fica & ~par, fica


def _texto(img, caixa, escuro=110):
    """Os px de texto (escuros) da caixa (px da imagem), com 2 px de folga."""
    x0, y0, x1, y1 = (max(int(v), 0) for v in caixa)
    m = np.zeros(img.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = img[y0:y1, x0:x1].astype(np.float32).mean(-1) < escuro
    return cv2.dilate(m, np.ones((5, 5), np.uint8)).astype(bool)


def varanda(out, mp, ref, Q, par):
    import mobiliario_terreo_casae_1611 as M
    import proposta_varanda_casae_1711 as PV
    pecas = PV.ALTERNATIVAS[2][1]
    if mp.ref is None:
        limpa = PV.limpar(Q, out, par)
        print(f"    varanda: {PV.ALTERNATIVAS[2][0]}")
        return PV.montar(limpa, par, pecas)
    import biblioteca_terreo_casaa_1211 as BT
    import mobiliario_terreo_casac_1311 as MB
    buraco, fica = _buraco_varanda(ref, par)
    limpa = M.piso(ref, buraco, "bege", par, nao_luz=fica)
    m = mp.local(out, (1240, 1180, 1600, 1520))
    s, A = m.s, _afim(m)
    ys, xs = np.nonzero(buraco)
    fx0, fy0, fx1, fy1 = xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7
    X0, Y0 = int(np.floor(s * fx0 + m.t[0])), int(np.floor(s * fy0 + m.t[1]))
    X1, Y1 = int(np.ceil(s * fx1 + m.t[0])), int(np.ceil(s * fy1 + m.t[1]))
    Ar = A.copy()
    Ar[0, 2] -= X0
    Ar[1, 2] -= Y0
    w, h = X1 - X0, Y1 - Y0
    sig = 0.5 * s
    LF = cv2.GaussianBlur(cv2.warpAffine(limpa.astype(np.float32), Ar, (w, h), flags=cv2.INTER_CUBIC), (0, 0), sig)
    mk = cv2.warpAffine(buraco.astype(np.float32), Ar, (w, h), flags=cv2.INTER_LINEAR) > 0.5
    # o grão do Bege Bahia limpo do próprio 12K (a amostra da proposta), em espelho até cobrir a região
    sx0, sy0, sx1, sy1 = m.reti(PV.LUGARES["bege"])
    S = out[sy0:sy1, sx0:sx1].astype(np.float32)
    G = S - cv2.GaussianBlur(S, (0, 0), sig)
    G = np.concatenate([G, G[:, ::-1]], axis=1)
    G = np.concatenate([G, G[::-1]], axis=0)
    G = np.tile(G, (h // G.shape[0] + 1, w // G.shape[1] + 1, 1))[:h, :w]
    novo = LF + G
    # o texto do rótulo (a Inter no A, a Kalam no B) fica
    texto = np.zeros(out.shape[:2], bool)
    for r in _protegidos(("VARANDA",)):
        texto |= _texto(out, m.reti(r))
    mk &= ~texto[Y0:Y1, X0:X1]
    a = np.clip(cv2.GaussianBlur(mk.astype(np.float32), (0, 0), 0.4 * s) * 1.3, 0, 1) * mk
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)
    print(f"    varanda (12K): o piso limpo da final com o grão do Bege Bahia do 12K ({int(mk.sum())} px)")

    def nao12(xa, ya, xb, yb):
        Ab = A.copy()
        Ab[0, 2] -= xa
        Ab[1, 2] -= ya
        return cv2.warpAffine(par.astype(np.uint8), Ab, (xb - xa, yb - ya), flags=cv2.INTER_NEAREST) > 0

    guarda = M.pousar

    def pousar12(o, P, cx, cy, wt, ht, ang, sombra, _par):
        return BT.pousar(o, P, m.x(cx), m.y(cy), wt * s, ht * s, ang, BT.SOMBRAS[sombra] if sombra else [],
                         MB.PX_M * s, nao=nao12)
    M.pousar = pousar12
    try:
        out = PV.montar(out, par, pecas)
    finally:
        M.pousar = guarda
    print(f"    varanda (12K): {PV.ALTERNATIVAS[2][0]}, as peças na escala do 12K")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def _lum(img, xs, ys):
    H, W = img.shape[:2]
    xi = np.clip(np.round(xs - 0.5).astype(int), 0, W - 1)
    yi = np.clip(np.round(ys - 0.5).astype(int), 0, H - 1)
    return img[yi, xi].astype(np.float32).mean(-1)


def _linhas(Q, ref, q=TRACEJADOS):
    """{grupo: (sinal, cor, [(u0, v0, u1, v1) px da final])}: os trechos do PDF de cada grupo onde o traço antigo
    estava (o sinal: -1 escuro, +1 claro), a cor nova pelo fundo; a garagem, todos os trechos fora das paredes."""
    import final3840_casae as FE
    FE.paredes_pdf(Q)
    pe = cv2.dilate((Q._par > 0.3).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    tr = dict(FE._tracos_te(Q))
    d, p = q["desloc_px"], q["passo_px"]
    out = {}

    def px(t):
        (u0, v0), (u1, v1) = Q.p2q(t[0], t[1]), Q.p2q(t[2], t[3])
        return u0, v0, u1, v1

    def fundo(segs):
        L = []
        for u0, v0, u1, v1 in segs:
            c = max(np.hypot(u1 - u0, v1 - v0), 1e-6)
            nx, ny = -(v1 - v0) / c, (u1 - u0) / c
            f = np.linspace(0, 1, max(2, int(c)))
            for k in (d, -d):
                L.append(_lum(ref, u0 + (u1 - u0) * f + nx * k, v0 + (v1 - v0) * f + ny * k))
        return float(np.median(np.concatenate(L)))
    def inteira(n):
        """A linha inteira da cadeia `n` (px): a reta do 1º trecho, do primeiro ao último ponto, 3 px a mais."""
        ss_ = [px(t) for t in tr[n]]
        u0, v0, u1, v1 = ss_[0]
        c = np.hypot(u1 - u0, v1 - v0)
        ex, ey = (u1 - u0) / c, (v1 - v0) / c
        ts = [(x - u0) * ex + (y - v0) * ey for a, b, c_, d_ in ss_ for x, y in ((a, b), (c_, d_))]
        t0, t1 = min(ts) - 3, max(ts) + 3
        return (u0 + ex * t0, v0 + ey * t0, u0 + ex * t1, v0 + ey * t1)
    # a caixa do texto dos rótulos (px da final, 2 px de folga): as letras escuras na reta não são traço
    rots = {b["nome"]: b["linhas"] for b in json.loads(KALAM.read_text())}
    textos = [(meio - larg / 2 - 2, base - alt - 3, meio + larg / 2 + 2, base + 4)
              for nome in q["rotulos"] for _, meio, base, alt, larg in rots[nome]]

    def no_texto(xs, ys):
        m = np.zeros(xs.shape, bool)
        for a, b, c_, d_ in textos:
            m |= (xs >= a) & (xs <= c_) & (ys >= b) & (ys <= d_)
        return m
    for grupo, nomes in q["grupos"].items():
        segs = [inteira(n) for n in nomes]
        amostras = []
        for u0, v0, u1, v1 in segs:
            c = np.hypot(u1 - u0, v1 - v0)
            nx, ny = -(v1 - v0) / c, (u1 - u0) / c
            f = np.arange(0, c + 1e-6, p) / c
            xs, ys = u0 + (u1 - u0) * f, v0 + (v1 - v0) * f
            L0 = _lum(ref, xs, ys)
            La, Lb = _lum(ref, xs + nx * d, ys + ny * d), _lum(ref, xs - nx * d, ys - ny * d)
            amostras.append((u0, v0, u1, v1, f, L0, La, Lb))
        dif = np.concatenate([L0 - (La + Lb) / 2 for *_, L0, La, Lb in amostras])
        sinal = 1 if np.median(dif[np.abs(dif) > q["destoa"]]) > 0 else -1
        partes = []
        for u0, v0, u1, v1, f, L0, La, Lb in amostras:
            ok = (sinal * (L0 - La) > q["destoa"]) & (sinal * (L0 - Lb) > q["destoa"])
            ok &= ~no_texto(u0 + (u1 - u0) * f, v0 + (v1 - v0) * f)
            ok = ok & ~pe[np.clip(np.round(v0 + (v1 - v0) * f - 0.5).astype(int), 0, pe.shape[0] - 1),
                          np.clip(np.round(u0 + (u1 - u0) * f - 0.5).astype(int), 0, pe.shape[1] - 1)]
            i = 0
            while i < len(ok):
                if not ok[i]:
                    i += 1
                    continue
                j = i
                while j + 1 < len(ok) and ok[j + 1]:
                    j += 1
                if (f[j] - f[i]) * np.hypot(u1 - u0, v1 - v0) >= 1.5:
                    partes.append((u0 + (u1 - u0) * f[i], v0 + (v1 - v0) * f[i],
                                   u0 + (u1 - u0) * f[j], v0 + (v1 - v0) * f[j]))
                i = j + 1
        cor = q["cinza"] if fundo(segs) >= q["limiar"] else q["cinza_escuro"]
        out[grupo] = (sinal, cor, segs, partes)
    if not q.get("garagem"):
        return out
    nome, xa, xb = q["garagem"]
    segs = []
    for t in tr[nome]:
        u0, v0, u1, v1 = px(t)
        if min(u0, u1) >= xa and max(u0, u1) <= xb and not pe[int((v0 + v1) / 2), int((u0 + u1) / 2)]:
            segs.append((u0, v0, u1, v1))
    cor = q["cinza"] if fundo(segs) >= q["limiar"] else q["cinza_escuro"]
    out["garagem"] = (0, cor, [], segs)
    return out


def _protegidos(nomes=TRACEJADOS["rotulos"]):
    """As caixas (px da final) dos rótulos `nomes`, com folga para a Kalam (mais larga)."""
    rots = {b["nome"]: b["linhas"] for b in json.loads(KALAM.read_text())}
    cx = []
    for nome in nomes:
        for _, meio, base, alt, larg in rots[nome]:
            cx.append((meio - 0.65 * larg - 4, base - alt - 7, meio + 0.65 * larg + 4, base + 5))
    return cx


def _alfa_kalam(nomes, x0, y0, W, H):
    """O alfa e a cor dos rótulos `nomes` na Kalam, como `rotulos_kalam_casac.desenhar` os escreve no 12K B, numa
    janela (x0, y0, W, H) do 12K."""
    import rotulos_kalam_casac as K
    import rotulos_manuscritos_casaa as RM
    from PIL import Image, ImageDraw, ImageFont
    d = json.loads((RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_12K_dados.json").read_text())
    s, X0, Y0 = 12288 / d["Wc"], d["X0"], d["Y0"]
    rots = json.loads(KALAM.read_text())
    k_alt = RM._altura_maiuscula(RM.FONTE)
    ref = ImageFont.truetype(str(RM.FONTE), 200)

    def corpo(cap):
        return cap * K.ALTURA / (k_alt / 200)
    tetos = [larg / max(ref.getlength(t) * corpo(cap) / 200, 1e-6)
             for b in rots for t, mx, base, cap, larg in b["linhas"] or []]
    f_glob = min(1.0, max(K.TETO_MIN, min(tetos)))
    ss = 4
    alfa, cor = np.zeros((H, W), np.float32), np.zeros((H, W, 3), np.float32)
    for b in rots:
        if b["nome"] not in nomes:
            continue
        for t, mx, base, cap, larg in b["linhas"]:
            c = corpo(cap)
            c *= min(f_glob, larg / max(ref.getlength(t) * c / 200, 1e-6))
            f = ImageFont.truetype(str(RM.FONTE), max(4, int(round(c * s * ss))))
            u, v = (mx - X0) * s - x0, (base - Y0) * s - y0
            tela = Image.new("L", (W * ss, H * ss), 0)
            ImageDraw.Draw(tela).text((u * ss, v * ss), t, font=f, fill=255, anchor="ms")
            a = np.asarray(tela.resize((W, H), Image.LANCZOS), np.float32) / 255
            cor[a > alfa] = b["cor"]
            alfa = np.maximum(alfa, a)
    return alfa, cor


def tracejados(out, mp, ref, Q, linhas, q=TRACEJADOS, kalam=False):
    import final3840_casae as FE
    FE.paredes_pdf(Q)
    par = Q._par > 0.3
    prot = _protegidos(q["rotulos"])
    n_l = n_t = 0
    for grupo, (sinal, cor, segs, partes) in linhas.items():
        m = _local(out, mp, q["caixas"][grupo])
        s, A = m.s, _afim(m)
        x0, y0, x1, y1 = m.reti(q["caixas"][grupo])
        H, W = y1 - y0, x1 - x0
        Ar = A.copy()
        Ar[0, 2] -= x0
        Ar[1, 2] -= y0
        reg = out[y0:y1, x0:x1].copy()
        paredes = cv2.dilate(cv2.warpAffine(par.astype(np.uint8), Ar, (W, H), flags=cv2.INTER_NEAREST),
                             np.ones((3, 3), np.uint8)).astype(bool)
        guarda = np.zeros((H, W), bool)
        # no 12K B, a Kalam: os traços antigos passavam por baixo dela (a entrada do Topaz era a final sem textos); o
        # traço sai também embaixo das letras, que voltam por cima do piso limpo
        ak, ck = _alfa_kalam(q["rotulos"], x0, y0, W, H) if kalam else (None, None)
        for r in ([] if kalam else prot):
            a, b, c, d = m.ret(r)
            guarda[max(int(b) - y0, 0):max(int(np.ceil(d)) - y0, 0), max(int(a) - x0, 0):max(int(np.ceil(c)) - x0, 0)] = True
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        X, Y = xx + x0 + 0.5, yy + y0 + 0.5                       # coordenadas de borda (as de `Mapa`)
        # o traço antigo sai: o px deslocado na perpendicular (de um lado ou do outro), só onde ele destoa
        if sinal:
            L = reg.astype(np.float32).mean(-1)
            novo, feito = reg.copy(), np.zeros((H, W), bool)
            for u0, v0, u1, v1 in segs:
                a0, b0, a1, b1 = m.x(u0), m.y(v0), m.x(u1), m.y(v1)
                c = max(np.hypot(a1 - a0, b1 - b0), 1e-6)
                ex, ey = (a1 - a0) / c, (b1 - b0) / c
                t = (X - a0) * ex + (Y - b0) * ey
                dist = np.abs((X - a0) * -ey + (Y - b0) * ex)
                banda = (dist <= q["limpa_px"] * s) & (t >= -s) & (t <= c + s) & ~paredes & ~guarda & ~feito
                if not banda.any():
                    continue
                for k in (q["desloc_px"] * s, -q["desloc_px"] * s):
                    sx = np.round(xx - ey * k).astype(int)
                    sy = np.round(yy + ex * k).astype(int)
                    ok = banda & (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
                    ok[ok] &= ~paredes[sy[ok], sx[ok]]
                    if ak is not None:
                        ok[ok] &= ak[sy[ok], sx[ok]] < 0.02
                        ok[ok] &= (sinal * (L[ok] - L[sy[ok], sx[ok]]) > q["destoa"] * 0.5) | (ak[ok] > 0.02)
                    else:
                        ok[ok] &= sinal * (L[ok] - L[sy[ok], sx[ok]]) > q["destoa"] * 0.5
                    novo[ok] = reg[sy[ok], sx[ok]]
                    feito |= ok
                    banda &= ~ok
            if ak is not None:
                sel = feito & (ak > 0.02)
                a_ = ak[sel][:, None]
                novo[sel] = np.clip(np.round(novo[sel].astype(np.float32) * (1 - a_) + ck[sel] * a_), 0,
                                    255).astype(np.uint8)
            n_l += int(feito.sum())
            reg = novo
        # os trechos novos: cinza, finos, com o antisserrilhado (ss)
        S = q["ss"]
        alfa = np.zeros((H * S, W * S), np.uint8)
        for u0, v0, u1, v1 in partes:
            p0 = (int(round((m.x(u0) - x0) * S)), int(round((m.y(v0) - y0) * S)))
            p1 = (int(round((m.x(u1) - x0) * S)), int(round((m.y(v1) - y0) * S)))
            cv2.line(alfa, p0, p1, 255, max(1, int(round(q["larg_px"] * s * S))), cv2.LINE_AA)
        a = cv2.resize(alfa.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA) * ~paredes
        r = reg.astype(np.float32)
        r = r * (1 - a[..., None]) + np.float32(cor) * a[..., None]
        out[y0:y1, x0:x1] = np.clip(np.round(r), 0, 255).astype(np.uint8)
        n_t += len(partes)
    print(f"    tracejados: o traço antigo tirado ({n_l} px) e {n_t} trechos novos em cinza, "
          f"{q['larg_px']} px na final: " + ", ".join(f"{g} ({'cinza ' + str(c[0])})" for g, (_, c, _, _) in
                                                     linhas.items()))


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(img, mp, ref, kalam=False):
    import final3840_casae as FE
    Q = FE.QuadroE("Terreo")
    par = FE.paredes_pdf(Q) > 0.5
    linhas = _linhas(Q, ref)
    out = img.copy()
    levantamento(out, mp)
    out = varanda(out, mp, ref, Q, par)
    tracejados(out, mp, ref, Q, linhas, kalam=kalam)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada", help="final: a final de entrada (o padrão é a própria final)")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa(), fin))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, fin, kalam=(op == "B"))
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

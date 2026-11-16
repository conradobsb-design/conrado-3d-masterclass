"""Os pedidos de 16/11 (2ª leva) no Térreo da Casa D, chamados de `biblioteca_terreo_casad_1511.aplicar` e de
`alternativa1_terreo_casad_1611`:

- o estar do jantar: o tapete redondo novo (`living/tapete-redondo-trama-greige-d`, gerado no Higgsfield em 2K) no
  círculo do tapete de antes (usuário: "melhore a representação desse tapete"); as duas mesinhas redondas laterais no
  tom da mesa de centro de nogueira (`mesinha`: o painel liso do tampo dela, sem o adorno);
- o living e a varanda (`tapete_novo`): o tapete do living na trama clara da biblioteca (usuário: "o tapete não está
  aparecendo aqui"), o da varanda no próprio tecido (a amostra limpa dele, sem emenda) com as bordas nítidas
  (usuário: "corrija essas falhas nas bordas laterais do tapete"); as peças que ficam voltam por cima;
- a suíte master: o tapete da biblioteca da Casa D por baixo da cama (`tapete_master`), o contorno nítido da cama
  (`contorno_cama`) e o armário liso no lugar do recamier (em `biblioteca_terreo_casad_1511.ARMARIOS`);
- os painéis pivotantes da gourmet em brises como na Casa A (`brises`);
- o contorno das geladeiras sem o piso antigo (`geladeiras`);
- as pedras (pisantes) em Bege Bahia levigado, cada uma com a aresta e a sombra curta na grama (`pedras`); as
  floreiras com a borda e as plantas da floreira baixa da biblioteca (`floreiras`);
- a suíte 3: a mesa redonda em nogueira, o piso entre o vidro e o painel de madeira no vinílico da suíte e o painel em
  ripado de nogueira, destacado (`suite3`);
- o aparador do living em nogueira escuro (`aparador`);
- as paredes atrás das portas dos banhos 2 e 3 (`paredes_banhos`);
- a margem branca sem o tracejado em volta da planta e o muro de baixo sem a ponta que sobrava (`margem`).
"""
import contextlib
import io
from pathlib import Path

import cv2
import numpy as np

import mobiliario_terreo_casac_1311 as MB
import regras_terreo_casab_1311 as RT

AQUI = Path(__file__).resolve().parent
BIB_D = AQUI.parents[1] / "POE642_CasaD" / "biblioteca-objetos" / "02-terreo"
PAREDE = (80, 80, 80)


def _rgba(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 8)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def _cob(r, X0, Y0, w, h):
    import um_pav_casaa_1111 as U
    return U._cobertura(r, X0, Y0, w, h)


# ----------------------------------------------------------------------------------------------------------------------
# as mesinhas redondas no tom da mesa de centro de nogueira do estar do jantar (o painel liso do tampo, abaixo do livro)
MESINHA_D = {"png": "../../POE642_CasaD/biblioteca-objetos/02-terreo/living/mesa-centro-nogueira-adorno-d.png",
             "patch": (0.36, 0.76, 0.54, 0.94), "borda": 0.78, "folga_px": 1.0}


def png_mesinha(q=MESINHA_D):
    import revisao_terreo_casac_1511 as R15
    return R15._png_mesinha(dict(R15.MESINHA, png=q["png"], patch=q["patch"], borda=q["borda"]))


def mesinha(Q, out, par, i, q=MESINHA_D):
    x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
    D = ((x1 - x0) + (y1 - y0)) / 2 + q["folga_px"]
    return MB.pousar(out, png_mesinha(q), (x0 + x1) / 2, (y0 + y1) / 2, D, D, 0.0, "baixa", par)


# ----------------------------------------------------------------------------------------------------------------------
# os tapetes
def tapete_amostra(img, amostra, w, h, ss=2, borda=0.90):
    """O tapete w x h px (em `ss`) no próprio tecido: a amostra limpa sem emenda, a beira de 1 px um tom abaixo."""
    import materiais_terreo_casac_1311 as MT
    x0, y0, x1, y1 = amostra
    W, H = int(round(w * ss)), int(round(h * ss))
    T = MT.sem_emenda(img[y0:y1, x0:x1].astype(np.float32), H, W)
    T[:ss] *= borda
    T[-ss:] *= borda
    T[:, :ss] *= borda
    T[:, -ss:] *= borda
    return np.dstack([T, np.full((H, W), 255, np.float32)]).astype(np.float32)


def caixa_uniao(m_img, caixa, folga=0.5):
    """A caixa (px) que cobre o tapete do PDF e o da imagem (`m_img`, bool)."""
    ys, xs = np.nonzero(m_img)
    return (min(float(xs.min()), caixa[0]) - folga, min(float(ys.min()), caixa[1]) - folga,
            max(float(xs.max() + 1), caixa[2]) + folga, max(float(ys.max() + 1), caixa[3]) + folga)


def tapete_novo(Q, out, par, P, caixa, ficam=()):
    """O tapete P (RGBA) esticado na `caixa` (px), deitado ou em pé como ela, com a sombra de tapete; as peças `ficam`
    (as do render que não saem) voltam por cima."""
    x0, y0, x1, y1 = caixa
    w, h = x1 - x0, y1 - y0
    deitado_P = P.shape[1] >= P.shape[0]
    g, wt, ht = (0.0, w, h) if deitado_P == (w >= h) else (90.0, h, w)
    antes = out.copy()
    out = MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, wt, ht, g, "tapete", par)
    if ficam:
        # só os px da peça (diferentes do tapete de antes em volta dela): o anel do tapete de antes sai
        f = RT.dilatar(MB.contorno(Q, list(ficam))[1], 1)
        X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
        caixa = np.zeros(f.shape, bool)
        caixa[Y0:Y1, X0:X1] = True
        ref = np.median(antes[caixa & ~RT.dilatar(f, 3)].reshape(-1, 3).astype(np.float32), axis=0)
        peca = f & (np.abs(antes.astype(np.float32) - ref).max(axis=2) > 24)
        peca = cv2.morphologyEx(peca.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
        # o miolo de cada peça inteiro (as partes claras dela, como as células do banco ripado, também ficam)
        miolo = cv2.erode(MB.contorno(Q, list(ficam))[1].astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        volta = (peca & f) | miolo
        out[volta] = antes[volta]
    return out


# a suíte master (usuário: "melhore o contorno da cama e o tapete dessa suite master"): o tapete de trama da biblioteca
# da Casa D no retângulo do PDF (ARQ_LOUÇAS E METAIS 65642), antes da cama (a cama, os criados e o armário por cima)
TAPETE_MASTER = {"pdf": 65642, "png": "suite-master/tapete", "folga_px": 1.0}


def tapete_master(Q, out, par, q=TAPETE_MASTER):
    x0, y0, x1, y1 = RT.caixa_pdf(Q, q["pdf"])
    f = q["folga_px"]
    out = tapete_novo(Q, out, par, _rgba(BIB_D / f"{q['png']}.png"), (x0 - f, y0 - f, x1 + f, y1 + f))
    print("    suíte master: o tapete de trama da biblioteca da Casa D no retângulo do PDF, por baixo da cama")
    return out


# o contorno da cama: o fio escuro junto à silhueta (por fora), em cima da sombra
CONTORNO_CAMA = {"camas": ("suíte master",), "fio": 0.80, "beira_px": 1.6, "falha": 22}


def contorno_cama(out, par, q=CONTORNO_CAMA):
    import alternativa1_terreo_casad_1611 as A1
    import biblioteca_terreo_casad_1511 as TD
    o = out.astype(np.float32)
    camas = [(nome, c, giro, tipo, tom) for nome, c, giro, tipo, _, tom, _ in TD.CAMAS]
    camas.append(("DCE", TD.DCE["caixa"], TD.DCE["giro"], "solteiro", TD.DCE["tom"]))
    for nome, (x0, y0, x1, y1), giro, tipo, tom in camas:
        if nome not in q["camas"]:
            continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        comp, larg = (y1 - y0, x1 - x0) if giro in (0.0, 180.0) else (x1 - x0, y1 - y0)
        if nome == "DCE":
            P = A1.cama_png(tipo, A1._cor_quarto(tom), y1 - y0, x1 - x0)
            larg, comp = x1 - x0, y1 - y0
        else:
            P = A1.cama_png(tipo, A1._cor_quarto(tom), comp, larg)
        al = RT._alfa_peca(P, cx, cy, larg, comp, giro, par.shape).astype(np.float32)
        al = np.clip(al / max(float(al.max()), 1e-6), 0, 1)
        # a beira de dentro sem falhas: os px escuros demais na faixa da beira (os pontinhos da moldura) no tom dela
        dentro = (al > 0.5).astype(np.uint8)
        d = cv2.distanceTransform(np.pad(dentro, 1), cv2.DIST_L2, 3)[1:-1, 1:-1]
        faixa = (d > 0) & (d <= q["beira_px"])
        if faixa.any():
            L = o.mean(axis=2)
            med = np.median(o[faixa], axis=0)
            falha = faixa & (L < float(np.mean(med)) - q["falha"])
            o[falha] = med
        anel = np.clip(cv2.dilate(al, np.ones((3, 3), np.uint8)) - al, 0, 1) * ~par
        o *= (1 - (1 - q["fio"]) * anel)[..., None]
    print(f"    camas: o fio do contorno ({', '.join(q['camas'])})")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# os painéis pivotantes da gourmet (usuário: "não é assim os paineis pivotantes. representar igual ao da casa A, em
# forma de brises"): as 2 folhas do PDF abertas a 45°, cada uma no meio do seu trecho, no desenho dos brises do lounge da
# Casa A (a lâmina quase preta de 4,5 px com as pontas redondas, a 45° do alto à esquerda para baixo à direita, e a
# sombra larga e esfumada deslocada para a esquerda); a faixa das folhas fechadas de antes volta ao piso de cada lado
BRISES = {"x": (1390.5, 1396.5), "y": (558.0, 702.0), "n": 2, "comp": 0.93, "esp_px": 4.5, "cor": (15, 17, 21),
          "sombra": {"dx": -13.0, "dy": 3.0, "larg_px": 9.0, "sigma": 3.5, "fator": (0.86, 0.78, 0.77), "forca": 0.85},
          "ss": 8}


def brises(out, par, q=BRISES):
    out = out.copy()
    x0, x1 = q["x"]
    y0, y1 = q["y"]
    xm = (x0 + x1) / 2
    a, b, m = int(np.floor(x0)) - 1, int(np.ceil(x1)) + 1, int(round(xm))
    Y0, Y1 = int(np.floor(y0)), int(np.ceil(y1))
    novo = out[Y0:Y1].copy()
    novo[:, a:m] = out[Y0:Y1, 2 * a - m:a][:, ::-1]
    novo[:, m:b] = out[Y0:Y1, b:2 * b - m][:, ::-1]
    livre = ~par[Y0:Y1, a:b]
    out[Y0:Y1, a:b][livre] = novo[:, a:b][livre]
    ss, sh = q["ss"], q["sombra"]
    X0, X1, YA, YB = int(xm - 50), int(xm + 50), int(y0 - 20), int(y1 + 20)
    M = np.zeros(((YB - YA) * ss, (X1 - X0) * ss), np.uint8)
    S = np.zeros_like(M)
    passo = (y1 - y0) / q["n"]
    L = q["comp"] * passo
    c = s = np.sqrt(0.5)

    def p(x, y):
        return int(round((x - X0) * ss)), int(round((y - YA) * ss))
    for k in range(q["n"]):
        cy = y0 + passo * (k + 0.5)
        ax, ay, bx, by = xm - L / 2 * c, cy - L / 2 * s, xm + L / 2 * c, cy + L / 2 * s
        cv2.line(M, p(ax, ay), p(bx, by), 255, int(round(q["esp_px"] * ss)), cv2.LINE_AA)
        cv2.line(S, p(ax + sh["dx"], ay + sh["dy"]), p(bx + sh["dx"], by + sh["dy"]), 255,
                 int(round(sh["larg_px"] * ss)), cv2.LINE_AA)
    al = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, YB - YA), interpolation=cv2.INTER_AREA)
    sa = cv2.resize(S.astype(np.float32) / 255, (X1 - X0, YB - YA), interpolation=cv2.INTER_AREA)
    sa = cv2.GaussianBlur(sa, (0, 0), sh["sigma"]) * sh["forca"] * ~par[YA:YB, X0:X1]
    reg = out[YA:YB, X0:X1].astype(np.float32)
    reg *= 1 - sa[..., None] * (1 - np.float32(sh["fator"]))[None, None]
    reg = reg * (1 - al[..., None]) + np.float32(q["cor"]) * al[..., None]
    out[YA:YB, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# as geladeiras (usuário: "melhore o contorno em volta das geladeiras. remova manchas do antigo piso"): o granito da
# cozinha refeito na volta das duas (`folga_px`; a amostra limpa logo acima, tecida, a beira esfumada em 2 px) e as
# geladeiras inox G2 de novo por cima, com a sombra curta
GELADEIRAS = {"folga_px": 7, "granito_px": (1866, 590, 1958, 614), "beira_px": 2.0, "semente": 1612}


def geladeiras(Q, out, par, q=GELADEIRAS):
    import biblioteca_terreo_casad_1511 as TD
    cx_ = TD.COZINHA["geladeiras"]
    f = q["folga_px"]
    X0, Y0 = int(np.floor(min(c[0] for c in cx_))) - f, int(np.floor(min(c[1] for c in cx_))) - f
    X1, Y1 = int(np.ceil(max(c[2] for c in cx_))) + f, int(np.ceil(max(c[3] for c in cx_))) + f
    h, w = Y1 - Y0, X1 - X0
    T = TD._tecido(out, q["granito_px"], h, w, q["semente"])[:h, :w]
    m = np.zeros((h + 2, w + 2), np.uint8)
    m[1:-1, 1:-1] = 1
    d = cv2.distanceTransform(m, cv2.DIST_L2, 3)[1:-1, 1:-1]
    a = np.clip(d / q["beira_px"], 0, 1) * ~par[Y0:Y1, X0:X1]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    reg = reg * (1 - a[..., None]) + T * a[..., None]
    out = out.copy()
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    P = MB.ler("cozinha/geladeira-inox")
    for x0, y0, x1, y1 in cx_:
        ht = y1 - y0 - 1
        wt = min(x1 - x0 - 2, ht * P.shape[1] / P.shape[0])
        out = MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, wt, ht, 180.0, "movel", par)
    print(f"    geladeiras: o granito refeito na volta ({f} px, sem o piso antigo) e as 2 G2 por cima, com a sombra curta")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# as pedras (usuário: "melhorar a representação das pedras e da floreira"): os pisantes do PDF (EST_LAJE), os 7 de cima
# (junto à cozinha) e os 8 do hall de entrada, em Bege Bahia levigado (a textura da borda da piscina, um trecho dela
# por pedra, o tom de cada uma um pouco diferente), a aresta do lado da luz (que vem do alto à direita) um tom acima e a
# do outro um tom abaixo, e a sombra curta na grama para baixo e para a esquerda; a pedra cobre a de antes inteira
PEDRAS = {"ids": (33333, 32187, 31041, 29901, 28758, 27615, 26602,
                  2821, 9589, 11341, 13073, 14806, 16536, 18309, 20066),
          "tom": (0.965, 1.025), "luz": 1.05, "escuro": 0.86, "sombra": (0.42, (-1.4, 1.4), 1.3), "busca_px": 5,
          "semente": 1613}


def _creme(reg):
    r = reg.astype(np.int16)
    return (r.mean(axis=2) > 150) & (r[..., 1] - r[..., 0] < 40)


def pedras(Q, out, par, q=PEDRAS):
    import pedidos_terreo_casad_1611 as PD
    rng = np.random.default_rng(q["semente"])
    o = out.astype(np.float32)
    caixas = []
    for i in q["ids"]:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        b = q["busca_px"]
        X0, Y0, X1, Y1 = int(x0) - b, int(y0) - b, int(np.ceil(x1)) + b, int(np.ceil(y1)) + b
        cr = _creme(out[Y0:Y1, X0:X1])
        n, lab, st, _ = cv2.connectedComponentsWithStats(cr.astype(np.uint8))
        if n > 1:
            k = 1 + int(np.argmax(st[1:, 4]))
            a, bb, c, d = st[k, 0] + X0, st[k, 1] + Y0, st[k, 0] + st[k, 2] + X0, st[k, 1] + st[k, 3] + Y0
            x0, y0, x1, y1 = min(x0, a), min(y0, bb), max(x1, c), max(y1, d)
        caixas.append((x0, y0, x1, y1))
    H = int(np.ceil(max(c[3] - c[1] for c in caixas))) + 16
    W = int(np.ceil(max(c[2] - c[0] for c in caixas))) * 3 + 16
    T = PD._bege_levigado(H, W, PD.BORDA_PISCINA)
    f, (dx, dy), sig = q["sombra"]
    for x0, y0, x1, y1 in caixas:
        X0, Y0, X1, Y1 = int(np.floor(x0)) - 6, int(np.floor(y0)) - 6, int(np.ceil(x1)) + 6, int(np.ceil(y1)) + 6
        w, h = X1 - X0, Y1 - Y0
        A = _cob((x0, y0, x1, y1), X0, Y0, w, h)
        topo = A - _cob((x0, y0 + 1, x1, y1), X0, Y0, w, h)
        dir_ = A - _cob((x0, y0, x1 - 1, y1), X0, Y0, w, h)
        baixo = A - _cob((x0, y0, x1, y1 - 1), X0, Y0, w, h)
        esq = A - _cob((x0 + 1, y0, x1, y1), X0, Y0, w, h)
        ox = int(rng.integers(0, max(W - w, 1)))
        tex = T[:h, ox:ox + w] * rng.uniform(*q["tom"])
        fat = 1 + (q["luz"] - 1) * np.clip(topo + dir_, 0, 1) - (1 - q["escuro"]) * np.clip(baixo + esq, 0, 1)
        tex = tex * fat[..., None]
        sb = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h)), (0, 0), sig)
        reg = o[Y0:Y1, X0:X1]
        livre = ~par[Y0:Y1, X0:X1]
        reg *= (1 - f * sb * (1 - A) * livre)[..., None]
        reg[:] = reg * (1 - A[..., None]) + tex * A[..., None]
    print(f"    pedras: os {len(caixas)} pisantes em Bege Bahia levigado, com a aresta e a sombra curta na grama")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


# as floreiras junto à cozinha e à área de serviço (ARQ_PAREDE; px): a borda (o topo e as laterais, fora o miolo) no tom
# da borda da floreira baixa da biblioteca da Casa D, com o fio por fora e a sombra curta para dentro; no miolo, o miolo
# de plantas da floreira baixa (a terra e as folhagens), na altura do miolo, repetido em espelho ao longo dela
FLOREIRAS = {"pecas": [{"fora": (1867.7, 343.8, 2036.5, 362.6), "dentro": (1873.1, 350.0, 2031.1, 362.6)},
                       {"fora": (2287.4, 343.8, 2458.0, 362.6), "dentro": (2293.7, 350.0, 2451.7, 362.6)}],
             "png": BIB_D / "jardim-do-lavabo" / "floreira-baixa.png", "fio": 0.80, "sombra_dentro": 0.30, "ss": 4}


def _miolo_floreira(P):
    """O miolo da floreira baixa (sem a borda): as linhas e colunas onde o verde e a terra são a maioria."""
    rgb = P[..., :3]
    r = rgb.astype(np.int16)
    planta = ((r[..., 1] - r[..., 2] > 6) | (r.mean(axis=2) < 110)) & (P[..., 3] > 200)
    lin = np.nonzero(planta.mean(axis=1) > 0.5)[0]
    col = np.nonzero(planta.mean(axis=0) > 0.5)[0]
    borda = rgb[(P[..., 3] > 200) & ~planta].reshape(-1, 3)
    return rgb[lin.min():lin.max() + 1, col.min():col.max() + 1].astype(np.float32), np.median(borda, axis=0)


def floreiras(out, par, q=FLOREIRAS):
    P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED)
    miolo, cor_borda = _miolo_floreira(P)
    o = out.astype(np.float32)
    for fl in q["pecas"]:
        fx0, fy0, fx1, fy1 = fl["fora"]
        dx0, dy0, dx1, dy1 = fl["dentro"]
        X0, Y0, X1, Y1 = int(np.floor(fx0)) - 2, int(np.floor(fy0)) - 2, int(np.ceil(fx1)) + 2, int(np.ceil(fy1))
        w, h = X1 - X0, Y1 - Y0
        Af = _cob(fl["fora"], X0, Y0, w, h)
        Ad = _cob(fl["dentro"], X0, Y0, w, h)
        borda = np.clip(Af - Ad, 0, 1)
        # o miolo: as plantas na altura do miolo, em espelho ao longo dele
        hm = dy1 - dy0
        k = hm / miolo.shape[0]
        tira = cv2.resize(miolo, (max(int(round(miolo.shape[1] * k)), 4), max(int(round(hm)), 2)),
                          interpolation=cv2.INTER_AREA)
        reps = int(np.ceil((dx1 - dx0) / tira.shape[1])) + 1
        linha = np.hstack([tira if j % 2 == 0 else tira[:, ::-1] for j in range(reps)])
        mi = np.zeros((h, w, 3), np.float32)
        ix0, iy0 = int(np.floor(dx0)) - X0, int(np.floor(dy0)) - Y0
        hh = min(linha.shape[0], h - iy0)
        ww = min(linha.shape[1], w - ix0)
        mi[iy0:iy0 + hh, ix0:ix0 + ww] = linha[:hh, :ww]
        # a sombra da borda no miolo (a luz do alto à direita: a borda de cima e a da esquerda fazem sombra)
        sb = cv2.GaussianBlur(cv2.warpAffine(Af - Ad, np.float32([[1, 0, -0.8], [0, 1, 1.2]]), (w, h)), (0, 0), 0.8)
        mi *= (1 - q["sombra_dentro"] * sb * Ad)[..., None]
        # a borda: o tom da borda da biblioteca, uma leve textura, o fio por fora
        rng = np.random.default_rng(1614)
        tx = 1 + 0.03 * cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.7)
        cb = np.float32(cor_borda)[None, None] * tx[..., None]
        fio = np.clip(Af - _cob((fx0 + 0.7, fy0 + 0.7, fx1 - 0.7, fy1), X0, Y0, w, h), 0, 1)
        cb = cb * (1 - (1 - q["fio"]) * fio)[..., None]
        reg = o[Y0:Y1, X0:X1]
        reg[:] = reg * (1 - Ad[..., None]) + mi * Ad[..., None]
        reg[:] = reg * (1 - borda[..., None]) + cb * borda[..., None]
    print(f"    floreiras: as {len(q['pecas'])} com a borda da floreira baixa da biblioteca e o miolo de folhagens dela")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# a suíte 3 / escritório, a fachada da direita (usuário: "melhorar a representação da mesa. melhorar a representação do
# piso entre a folha de vidro e o painel de madeira. melhorar a representação do painel de madeira, deixando um pouco
# mais destacado que o piso ao lado dele"): a mesa redonda de apoio (ARQ_LAYOUT 104187) em nogueira; a faixa entre a
# folha de vidro e o painel (x 2515 a 2524, até a linha do contrapiso do PDF) no vinílico da suíte (a amostra limpa da
# suíte, sem emenda, as réguas em pé como as dela); o painel (x 2524 a 2532,2) no ripado de nogueira das folhas de madeira
# do 1º Pavimento da Casa A (`um_pav_casaa_1111.FOLHAS_1P`), com o contorno e a sombra curta para fora (na grama)
SUITE3 = {"mesa": 104187, "piso": (2515, 1339, 2524, 1496), "vinilico_px": (2425, 1560, 2470, 1640),
          "painel": (2524.0, 1339.5, 2532.2, 1494.5), "semente": 1615}


def _folha_madeira(o, r, lado, qa, rng):
    import um_pav_casaa_1111 as U
    vert = lado in ("x-", "x+")
    X0, Y0 = int(np.floor(r[0])) - 4, int(np.floor(r[1])) - 4
    X1, Y1 = int(np.ceil(r[2])) + 4, int(np.ceil(r[3])) + 4
    w, h = X1 - X0, Y1 - Y0
    reg = o[Y0:Y1, X0:X1]
    A = U._cobertura(r, X0, Y0, w, h)
    dx, dy = {"x-": (-1.0, 0.6), "x+": (1.0, 0.6), "y-": (-0.6, -1.0), "y+": (0.6, 1.0)}[lado]
    sb = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h)), (0, 0), 0.9)
    reg *= (1 - qa["sombra"] * sb * (1 - A))[..., None]
    ys = (np.arange(h, dtype=np.float32) + Y0 + 0.5)[:, None] * np.ones((1, w), np.float32)
    xs = (np.arange(w, dtype=np.float32) + X0 + 0.5)[None, :] * np.ones((h, 1), np.float32)
    veio = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0),
                            sigmaX=0.6 if vert else 6.0, sigmaY=6.0 if vert else 0.6)
    veio /= max(float(veio.std()), 1e-6)
    rel = np.clip(((xs - r[0]) / max(r[2] - r[0], 1e-3)) if vert else ((ys - r[1]) / max(r[3] - r[1], 1e-3)), 0, 1)
    luz = 1 + qa["luz"] * (rel - 0.5) * (-1 if lado in ("x-", "y-") else 1)
    cor = np.float32(qa["madeira"])[None, None] * (luz * (1 + qa["veio"] * veio))[..., None]
    fase = np.mod((ys - r[1]) if vert else (xs - r[0]), qa["ripa_px"])
    jt = np.clip(1 - np.abs(fase - qa["junta_px"] / 2) / (qa["junta_px"] / 2 + 0.5), 0, 1) * qa["junta_forca"]
    cor = cor * (1 - jt[..., None]) + np.float32(qa["junta"]) * jt[..., None]
    cp = qa["contorno_px"]
    dentro = U._cobertura((r[0] + cp, r[1] + cp, r[2] - cp, r[3] - cp), X0, Y0, w, h)
    reg[:] = reg * (1 - A[..., None]) + cor * A[..., None]
    borda = np.clip(A - dentro, 0, 1)[..., None]
    reg[:] = reg * (1 - borda) + np.float32(qa["contorno"]) * borda


def suite3(Q, out, par, q=SUITE3):
    import materiais_terreo_casac_1311 as MT
    import um_pav_casaa_1111 as U
    out = mesinha(Q, out, par, q["mesa"], dict(MESINHA_D, folga_px=1.5))
    x0, y0, x1, y1 = q["piso"]
    a0, b0, a1, b1 = q["vinilico_px"]
    T = MT.sem_emenda(out[b0:b1, a0:a1].astype(np.float32), y1 - y0, x1 - x0)
    out = out.copy()
    livre = ~par[y0:y1, x0:x1]
    reg = out[y0:y1, x0:x1]
    reg[livre] = np.clip(np.round(T[livre]), 0, 255).astype(np.uint8)
    o = out.astype(np.float32)
    _folha_madeira(o, q["painel"], "x+", U.FOLHAS_1P, np.random.default_rng(q["semente"]))
    print("    suíte 3: a mesa redonda em nogueira; o piso entre o vidro e o painel no vinílico da suíte; o painel em "
          "ripado de nogueira, com o contorno e a sombra curta na grama")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# o aparador do living (usuário: "esse armário no tom nogueira escuro"; ARQ_MOBILIÁRIO 97337, px): a madeira (os px de
# madeira dentro da peça, fora o contorno cinza, a linha da frente e o puxador) no nogueira escuro, com o veio dela (a luz
# de cada px em relação à mediana)
APARADOR = {"pdf": 97337, "cor": (40, 60, 92), "gama": 0.9, "sat_min": 14}


def aparador(Q, out, q=APARADOR):
    x0, y0, x1, y1 = RT.caixa_pdf(Q, q["pdf"])
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    r = reg.astype(np.int16)
    madeira = (r[..., 2] - r[..., 0] >= q["sat_min"]) & (r.mean(axis=2) > 90)
    L = reg.mean(axis=2)
    med = float(np.median(L[madeira]))
    rel = np.clip(L / max(med, 1.0), 0.5, 1.6) ** q["gama"]
    novo = np.float32(q["cor"])[None, None] * rel[..., None]
    reg[madeira] = novo[madeira]
    out = out.copy()
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    aparador do living: em nogueira escuro ({int(madeira.sum())} px)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# as paredes atrás das portas dos banhos 2 e 3 (usuário: "corrija as paredes atras das portas"; px): a faixa de piso
# entre a face da parede e a folha aberta vira parede (a face reta até a folha), e os dentes escuros de 2 px sob a parede
# de cima, junto às portas, voltam ao piso de logo abaixo
PAREDES_BANHOS = {"paredes": [((2046, 1551, 2050, 1599), "banho 2: atrás da folha, junto à parede da esquerda"),
                              ((2222, 1551, 2270, 1555), "banho 3: atrás da folha, junto à parede de cima")],
                  "dentes": [((2103, 1551, 2117, 1553), 2), ((2199, 1551, 2217, 1553), 2)]}


def paredes_banhos(out, q=PAREDES_BANHOS):
    out = out.copy()
    for (x0, y0, x1, y1), _ in q["paredes"]:
        out[y0:y1, x0:x1] = PAREDE
    for (x0, y0, x1, y1), dy in q["dentes"]:
        out[y0:y1, x0:x1] = out[y0 + dy:y1 + dy, x0:x1]
    print("    banhos 2 e 3: a parede atrás das folhas abertas, reta até a folha; os dentes escuros sob a parede, no piso")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# a margem (usuário: "remova esse tracejado em volta da planta e corrija essa falha no final do muro, removendo esse
# final que sobra"): fora do terreno (px; o muro de cima de x 362 a 3372, de y 135 a 146, o de baixo até y 1939), tudo
# branco: o tracejado do limite e a ponta do muro de baixo que passava da grama até o tracejado; a ponta do muro de baixo
# no x da do muro de cima, com a mesma passagem para o branco
MARGEM = {"x": (362, 3374), "y": (134, 1940), "muro_baixo_y": (1926, 1940), "ponta": [(3372, 0.5), (3373, 0.88)]}


def margem(out, q=MARGEM):
    out = out.copy()
    (xa, xb), (ya, yb) = q["x"], q["y"]
    out[:ya] = 255
    out[yb:] = 255
    out[:, :xa] = 255
    out[:, xb:] = 255
    m0, m1 = q["muro_baixo_y"]
    for x, t in q["ponta"]:
        ref = out[m0:m1, x - 1 - (x - q["ponta"][0][0])].astype(np.float32)
        out[m0:m1, x] = np.clip(np.round(ref * (1 - t) + 255 * t), 0, 255).astype(np.uint8)
    print("    margem: sem o tracejado em volta da planta; o muro de baixo termina com a grama, como o de cima")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# as banquetas da gourmet (usuário: "remova esse tracejado, tanto em cima das banquetas, quanto embaixo delas. não há
# tracejado aqui"): o lugar das banquetas de antes recebe o deck de uma amostra limpa logo abaixo (sem emenda, com a
# costura das bordas), no lugar do piso copiado de 25 px abaixo (que trazia as duas linhas tracejadas e um tom mais
# escuro); e, no fim, o que sobrar de traço claro na faixa logo abaixo da ilha sai (por inpaint, só os px mais claros
# que o deck em volta)
def piso_amostra(out, c, par, amostra, folga=1):
    import biblioteca_subsolo_casaa_1211 as BS
    import materiais_terreo_casac_1311 as MT
    x0, y0 = int(np.floor(c[0])) - folga, int(np.floor(c[1])) - folga
    x1, y1 = int(np.ceil(c[2])) + folga, int(np.ceil(c[3])) + folga
    a0, b0, a1, b1 = amostra
    T = MT.sem_emenda(out[b0:b1, a0:a1].astype(np.float32), y1 - y0, x1 - x0)
    novo = BS.costura(out, np.clip(np.round(T), 0, 255).astype(np.uint8), x0, y0, x1, y1, par)
    livre = ~par[y0:y1, x0:x1]
    out[y0:y1, x0:x1][livre] = novo[livre]
    return out


TRACEJADO_ILHA = {"caixa": (1465, 685, 1670, 701), "limiar": 14}


def tracejado_ilha(out, q=TRACEJADO_ILHA):
    x0, y0, x1, y1 = q["caixa"]
    reg = np.ascontiguousarray(out[y0:y1, x0:x1])
    L = reg.astype(np.float32).mean(axis=2)
    fundo = cv2.medianBlur(np.clip(L, 0, 255).astype(np.uint8), 9).astype(np.float32)
    m = (L > fundo + q["limiar"]).astype(np.uint8)
    m = cv2.dilate(m, np.ones((2, 2), np.uint8))
    out = out.copy()
    if m.any():
        out[y0:y1, x0:x1] = cv2.inpaint(reg, m * 255, 2, cv2.INPAINT_TELEA)
    print(f"    gourmet: sem o tracejado junto às banquetas ({int(m.sum())} px)")
    return out


def franjas(out, par, caixa, larg=5, folga_y=3):
    """As faixas de `larg` px dos lados esquerdo e direito do tapete (`caixa`, px), por fora, recebem o piso de logo
    além delas, em espelho (as franjas tracejadas do tapete de antes, que ficavam fora do novo)."""
    x0, y0, x1, y1 = caixa
    a, b = int(np.floor(x0)), int(np.ceil(x1))
    Y0, Y1 = int(np.floor(y0)) - folga_y, int(np.ceil(y1)) + folga_y
    out = out.copy()
    for c0, c1, f0 in ((a - larg, a, a - 2 * larg), (b, b + larg, b + larg)):
        fonte = out[Y0:Y1, f0:f0 + larg][:, ::-1]
        livre = ~par[Y0:Y1, c0:c1]
        out[Y0:Y1, c0:c1][livre] = fonte[livre]
    return out

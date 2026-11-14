"""O padrão das portas dos quartos (14/11, usuário, com o recorte da suíte master da Casa B: "ESSE É O PADRÃO PARA UTILIZAR
EM TODOS OS QUARTOS DE ESQUADRIA DE VIDRO E PORTA DE MADEIRA EXTERNA, DIVIDIDOS EM FOLHAS DE ACORDO COM A SUA RESPECTIVA
DEFINIÇÃO. ADOTE PARA TODAS AS CASAS.").

Os vãos dos quartos com a porta de vidro de correr e, por fora dela, as folhas de madeira de correr: no PDF, 4 trilhos
de folhas (as peças brancas finas da ARQ_PAREDE, cada folha num trilho, em degrau): os 2 de fora (do lado oposto ao piso
laranja do quarto) são a madeira, os 2 de dentro o vidro. O desenho:
- a faixa do vão (das folhas de fora às de dentro) no piso do quarto (as linhas do piso de logo depois da faixa, do lado
  do quarto, espelhadas: as mesmas réguas e o mesmo tom; a cortina, se houver, é pulada);
- as folhas de vidro claras, com as duas faces finas em cinza e a sombra curta (`final3840_casab.BOXES_VIDRO`), sem
  perfil preto;
- as folhas de cada grupo (madeira, vidro) se encontram: a folga do PDF entre as duas, no comprimento, vira uma
  sobreposição curta onde elas trocam de trilho (`_encontrar`, "AS FOLHAS ... PRECISAM SE ENCONTRAR");
- as folhas de madeira no ripado de nogueira das folhas do 1º Pavimento da Casa A e do Térreo da Casa B
  (`um_pav_casaa_1111.FOLHAS_1P`: as ripas marcadas, o veio no comprido, a luz, o contorno e a sombra curta para fora).

  vaos_pdf(Q) -> os vãos achados; aplicar(Q, img, vaos) -> a imagem
"""

import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

LARANJA = (0.8, 0.6, 0.4)                  # o piso dos quartos no PDF (#CC9966)
PADRAO = {"folha_min_px": 30, "esp_px": (2.0, 3.6), "peca_min_px": 20, "d_perp_px": 16, "gap_px": 12,
          "lado_px": 12, "piso_rb": 40, "piso_lum": 178, "piso_ok": 0.85, "piso_linhas": 6, "busca_px": 40, "piso_tol": 32, "sobrepor_px": 3.0,
          "semente": 1418}


def _folhas(Q, q=PADRAO):
    H, W, ss = Q.H, Q.W, 4
    m = np.zeros((H * ss, W * ss), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or not d.get("fill") or min(d["fill"]) < 0.95:
            continue
        R = d["rect"]
        a, b = Q.p2q(R.x0, R.y0), Q.p2q(R.x1, R.y1)
        x0, y0, x1, y1 = min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])
        if min(x1 - x0, y1 - y0) > q["esp_px"][1] - 0.2 or max(x1 - x0, y1 - y0) < q["peca_min_px"]:
            continue
        cv2.rectangle(m, (int(x0 * ss), int(y0 * ss)), (int(np.ceil(x1 * ss)) - 1, int(np.ceil(y1 * ss)) - 1), 255, -1)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
    out = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        x0, y0, x1, y1 = x / ss, y / ss, (x + w) / ss, (y + h) / ss
        L, T = max(x1 - x0, y1 - y0), min(x1 - x0, y1 - y0)
        if L >= q["folha_min_px"] and q["esp_px"][0] <= T <= q["esp_px"][1] and a / (w * h) > 0.85:
            out.append((x0, y0, x1, y1))
    return out


def _grupos(folhas, q=PADRAO):
    usados = [False] * len(folhas)
    grupos = []
    for i, f in enumerate(folhas):
        if usados[i]:
            continue
        hor = (f[2] - f[0]) > (f[3] - f[1])
        g = [i]
        usados[i] = True
        mudou = True
        while mudou:
            mudou = False
            for j, h in enumerate(folhas):
                if usados[j] or ((h[2] - h[0]) > (h[3] - h[1])) != hor:
                    continue
                for k in g:
                    a = folhas[k]
                    if hor:
                        ov = min(a[2], h[2]) - max(a[0], h[0]) > -q["gap_px"]
                        pp = abs((a[1] + a[3]) / 2 - (h[1] + h[3]) / 2) <= q["d_perp_px"]
                    else:
                        ov = min(a[3], h[3]) - max(a[1], h[1]) > -q["gap_px"]
                        pp = abs((a[0] + a[2]) / 2 - (h[0] + h[2]) / 2) <= q["d_perp_px"]
                    if ov and pp:
                        g.append(j)
                        usados[j] = True
                        mudou = True
                        break
        grupos.append((hor, [folhas[k] for k in g]))
    return grupos


def _trilho(hor, f):
    return (f[1] + f[3]) / 2 if hor else (f[0] + f[2]) / 2


def vaos_pdf(Q, q=PADRAO):
    """Os vãos de 4 trilhos junto ao piso laranja: {"hor", "madeira": [rects], "vidro": [rects], "fora": -1|+1 (o lado
    de fora: -1 em cima/à esquerda), "faixa": (x0, y0, x1, y1)}."""
    lar = Q.preencher(lambda d: d.get("layer") == "ARQ_CONTRAPISO" and d.get("fill")
                      and max(abs(a - b) for a, b in zip(d["fill"], LARANJA)) < 0.03, ss=2) > 0.5
    vaos = []
    for hor, fs in _grupos(_folhas(Q, q), q):
        cs = sorted(_trilho(hor, f) for f in fs)
        trilhos = []
        for c in cs:
            if not trilhos or c - trilhos[-1][-1] > 1.6:
                trilhos.append([c])
            else:
                trilhos[-1].append(c)
        if len(trilhos) != 4:
            continue
        t = [float(np.mean(x)) for x in trilhos]
        x0 = min(f[0] for f in fs)
        y0 = min(f[1] for f in fs)
        x1 = max(f[2] for f in fs)
        y1 = max(f[3] for f in fs)
        lp = q["lado_px"]
        if hor:
            xm = int((x0 + x1) / 2)
            antes = lar[max(int(y0 - lp), 0), xm - 20:xm + 20].mean()
            depois = lar[min(int(y1 + lp), lar.shape[0] - 1), xm - 20:xm + 20].mean()
        else:
            ym = int((y0 + y1) / 2)
            antes = lar[ym - 20:ym + 20, max(int(x0 - lp), 0)].mean()
            depois = lar[ym - 20:ym + 20, min(int(x1 + lp), lar.shape[1] - 1)].mean()
        if max(antes, depois) < 0.5:
            continue                                         # nenhum lado é quarto
        fora = -1 if depois > antes else +1
        corte = (t[1] + t[2]) / 2
        mad = [f for f in fs if (_trilho(hor, f) < corte) == (fora < 0)]
        vid = [f for f in fs if (_trilho(hor, f) < corte) != (fora < 0)]
        vaos.append({"hor": hor, "madeira": mad, "vidro": vid, "fora": fora, "faixa": (x0, y0, x1, y1)})
    return vaos


def _paredes(Q):
    return Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                       and max(d["fill"]) < 0.6, ss=2) > 0.3


def _faixa_piso(out, v, par, q=PADRAO):
    """A faixa do vão no piso do quarto: as linhas (ou colunas) do piso de logo depois dela, do lado do quarto, a partir
    da primeira que é piso (a cortina é pulada), espelhadas."""
    x0, y0, x1, y1 = v["faixa"]
    X0, X1 = int(np.floor(x0)), int(np.ceil(x1))
    Y0, Y1 = int(np.floor(y0)) - 1, int(np.ceil(y1)) + 1
    if not v["hor"]:
        X0, X1 = int(np.floor(x0)) - 1, int(np.ceil(x1)) + 1
        Y0, Y1 = int(np.floor(y0)), int(np.ceil(y1))
    T = out if v["hor"] else np.ascontiguousarray(out.transpose(1, 0, 2))
    P = par if v["hor"] else par.T
    if not v["hor"]:
        X0, X1, Y0, Y1 = Y0, Y1, X0, X1
    I = T.astype(np.int16)
    piso = ((I[..., 2] - I[..., 0]) > q["piso_rb"]) & (I.mean(axis=2) < q["piso_lum"])
    para = 1 if v["fora"] < 0 else -1                        # o lado do quarto: depois (para baixo) ou antes
    y = Y1 if para > 0 else Y0 - 1
    ini = None
    for k in range(q["busca_px"]):
        yy = y + para * k
        bloco = [yy + para * j for j in range(q["piso_linhas"])]
        if all(piso[b, X0:X1].mean() >= q["piso_ok"] for b in bloco):
            ini = yy
            break
    if ini is None:
        return 0
    h = q["piso_linhas"] * 3
    # as colunas cuja fonte é piso em todas as linhas usadas (não um criado, um tapete); as outras pegam a mais perto
    fontes = [ini + para * j for j in range(h)]
    bloco = I[fontes, X0:X1]                                  # (h, w, 3)
    med = np.median(bloco.reshape(-1, 3), axis=0)
    ok = np.all(np.abs(bloco - med).max(axis=2) <= q["piso_tol"], axis=0)
    if not ok.any():
        return 0
    boas = np.nonzero(ok)[0]
    col = boas[np.abs(np.arange(X1 - X0)[:, None] - boas[None, :]).argmin(axis=1)] + X0
    n = 0
    linhas = range(Y1 - 1, Y0 - 1, -1) if para > 0 else range(Y0, Y1)
    for k, yy in enumerate(linhas):
        j = k % (2 * h)
        sy = ini + para * (j if j < h else 2 * h - 1 - j)
        m = ~P[yy, X0:X1]
        T[yy, X0:X1][m] = T[sy, col][m]
        n += int(m.sum())
    if not v["hor"]:
        out[:] = T.transpose(1, 0, 2)
    return n


def _cobertura(r, X0, Y0, w, h):
    xs = np.arange(X0, X0 + w, dtype=np.float32)
    ys = np.arange(Y0, Y0 + h, dtype=np.float32)
    cx = np.clip(np.minimum(xs + 1, r[2]) - np.maximum(xs, r[0]), 0, 1)
    cy = np.clip(np.minimum(ys + 1, r[3]) - np.maximum(ys, r[1]), 0, 1)
    return cy[:, None] * cx[None, :]


def _vidro(o, r, hor, fora):
    import final3840_casab as F
    qv = F.BOXES_VIDRO
    X0, Y0 = int(np.floor(r[0])) - 3, int(np.floor(r[1])) - 3
    X1, Y1 = int(np.ceil(r[2])) + 4, int(np.ceil(r[3])) + 4
    w, h = X1 - X0, Y1 - Y0
    A = _cobertura(r, X0, Y0, w, h)
    fp = qv["face_px"]
    if hor:
        dentro = _cobertura((r[0], r[1] + fp, r[2], r[3] - fp), X0, Y0, w, h)
    else:
        dentro = _cobertura((r[0] + fp, r[1], r[2] - fp, r[3]), X0, Y0, w, h)
    faces = np.clip(A - dentro, 0, 1)
    dx, dy = (0.0, 0.9 * fora * -1) if hor else (0.9 * fora * -1, 0.0)
    sb = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, -0.9 if hor else dx], [0, 1, dy if not hor else 0.9]]),
                                         (w, h)), (0, 0), 0.8)
    reg = o[Y0:Y1, X0:X1]
    reg *= (1 - qv["sombra"] * sb * (1 - A))[..., None]
    reg[:] = reg * (1 - A[..., None]) + np.float32(qv["vidro"]) * A[..., None]
    reg[:] = reg * (1 - faces[..., None]) + np.float32(qv["face"]) * faces[..., None]


def _madeira(o, r, hor, fora, rng):
    import um_pav_casaa_1111 as U
    qa = U.FOLHAS_1P
    vert = not hor
    f = qa["folga_px"] * 0.7
    r = (r[0] - f, r[1], r[2] + f, r[3]) if vert else (r[0], r[1] - f, r[2], r[3] + f)
    X0, Y0 = int(np.floor(r[0])) - 4, int(np.floor(r[1])) - 4
    X1, Y1 = int(np.ceil(r[2])) + 4, int(np.ceil(r[3])) + 4
    w, h = X1 - X0, Y1 - Y0
    reg = o[Y0:Y1, X0:X1]
    A = _cobertura(r, X0, Y0, w, h)
    dx, dy = ((-1.0 if fora < 0 else 1.0), 0.6) if vert else (-0.6, (-1.0 if fora < 0 else 1.0))
    sb = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h)), (0, 0), 0.9)
    reg *= (1 - qa["sombra"] * sb * (1 - A))[..., None]
    ys = (np.arange(h, dtype=np.float32) + Y0 + 0.5)[:, None] * np.ones((1, w), np.float32)
    xs = (np.arange(w, dtype=np.float32) + X0 + 0.5)[None, :] * np.ones((h, 1), np.float32)
    veio = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0),
                            sigmaX=0.6 if vert else 6.0, sigmaY=6.0 if vert else 0.6)
    veio /= max(float(veio.std()), 1e-6)
    rel = np.clip(((xs - r[0]) / max(r[2] - r[0], 1e-3)) if vert else ((ys - r[1]) / max(r[3] - r[1], 1e-3)), 0, 1)
    luz = 1 + qa["luz"] * (rel - 0.5) * (-1 if fora < 0 else 1)
    cor = np.float32(qa["madeira"])[None, None] * (luz * (1 + qa["veio"] * veio))[..., None]
    fase = np.mod((ys - r[1]) if vert else (xs - r[0]), qa["ripa_px"])
    jt = np.clip(1 - np.abs(fase - qa["junta_px"] / 2) / (qa["junta_px"] / 2 + 0.5), 0, 1) * qa["junta_forca"]
    cor = cor * (1 - jt[..., None]) + np.float32(qa["junta"]) * jt[..., None]
    cp = qa["contorno_px"]
    dentro = _cobertura((r[0] + cp, r[1] + cp, r[2] - cp, r[3] - cp), X0, Y0, w, h)
    reg[:] = reg * (1 - A[..., None]) + cor * A[..., None]
    borda = np.clip(A - dentro, 0, 1)[..., None]
    reg[:] = reg * (1 - borda) + np.float32(qa["contorno"]) * borda


def _encontrar(fs, hor, ov):
    """As folhas do mesmo grupo (madeira ou vidro), em trilhos vizinhos, se encontram como na referência (o recorte da
    suíte master da Casa B; usuário: "AS FOLHAS DAS PORTAS DE MADEIRA PRECISAM SE ENCONTRAR, BEM COMO AS FOLHAS DE VIDRO
    ENTRE ELAS"): a folga do PDF entre uma e a seguinte, no comprimento, vira uma sobreposição de `ov` px (cada uma vai
    até passar `ov` / 2 do meio da folga)."""
    a, b = (0, 2) if hor else (1, 3)
    fs = sorted([list(f) for f in fs], key=lambda f: f[a])
    for i in range(len(fs) - 1):
        f, g = fs[i], fs[i + 1]
        meio = (f[b] + g[a]) / 2
        f[b] = max(f[b], meio + ov / 2)
        g[a] = min(g[a], meio - ov / 2)
    return [tuple(f) for f in fs]


def aplicar(Q, img, vaos, q=PADRAO):
    out = img.copy()
    par = _paredes(Q)
    rng = np.random.default_rng(q["semente"])
    n = 0
    for v in vaos:
        n += _faixa_piso(out, v, par, q)
    o = out.astype(np.float32)
    for v in vaos:
        for r in _encontrar(v["vidro"], v["hor"], q["sobrepor_px"]):
            _vidro(o, r, v["hor"], v["fora"])
        for r in _encontrar(v["madeira"], v["hor"], q["sobrepor_px"]):
            _madeira(o, r, v["hor"], v["fora"], rng)
    nm = sum(len(v["madeira"]) for v in vaos)
    nv = sum(len(v["vidro"]) for v in vaos)
    print(f"    portas dos quartos: {len(vaos)} vãos, {nm} folhas de madeira em ripado por fora e {nv} folhas de vidro "
          f"claras, a faixa do vão no piso do quarto ({n} px)")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)

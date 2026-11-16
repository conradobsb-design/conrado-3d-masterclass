"""Os pedidos de 16/11 no Térreo da Casa D, além do mobiliário da Alternativa 1 (`alternativa1_terreo_casad_1611`).

- `bancada_intima` (usuário, no recorte da bancada com a cuba junto à parede da suíte 2, na sala íntima: "vamos
  melhorar a representação dessa bancada com essa pia. quero o realismo que estamos entregando. use a biblioteca para
  aqui. não há menor chance de termos essas linhas técnicas de contorno. aqui é planta humanizada."): a bancada do PDF
  (ARQ_BANCADAS, 0,60 x 2,20 m) inteira no travertino da cuba esculpida da biblioteca da Casa D
  (`banho-gourmet/cuba-travertino-gourmet`), a cuba esculpida com a torneira no lugar da cuba redonda do PDF (a
  torneira do lado da parede), a aresta da face livre um tom abaixo e a sombra curta no piso; as linhas técnicas e o
  quadradinho de antes somem por baixo.
- `borda_piscina` (usuário, com o recorte da piscina: "vamos fazer a borda de forma decente. use o mármore bege bahia
  para fazer."): a borda (capa) de 0,30 m em volta da água (a piscina, a prainha e o spa do PDF, ARQ_CONTRAPISO azul),
  as faixas entre os tanques inclusive, em placas de Bege Bahia (o do Subsolo da Casa A, levigado: as manchas largas
  pela metade, um tom mais claro que o deck), com as juntas finas a cada 0,60 m, o fio da junta com o deck e a quina
  clara junto à água.
- `arandelas` (usuário: "na suite master da casa D, temos luminárias de parede. represente-as com realismo. se for o
  caso, gere no higgsfield uma em 2k"): a arandela articulada preta do 3D da suíte master (gerada no Higgsfield em 2K,
  `suite-master/arandela-articulada-preta-d`), presa na parede da cabeceira, o braço até o criado e a cúpula sobre ele, no
  lugar do abajur.
"""
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
BIB_D = AQUI.parents[1] / "POE642_CasaD" / "biblioteca-objetos" / "02-terreo"

BANCADA_INTIMA = {"ret": (1759.6, 1552.3, 1795.4, 1682.1),
                  "png": BIB_D / "banho-gourmet" / "cuba-travertino-gourmet.png",
                  # a peça girada (a parede à direita): as linhas (fração da altura) da pedra lisa
                  "liso_frac": (0.04, 0.26), "ss": 8, "aresta": 0.84, "aresta_px": 1.2,
                  # o contorno técnico de antes à esquerda da bancada: o vinílico de `dx` px à esquerda
                  "limpa": (1755, 1549, 1760, 1684), "limpa_dx": -7,
                  # (16/11, usuário: "é para representar a cuba redonda apenas. remova aquele quadrado ali que tem o ponto
                  # de interrogação e deixe embaixo dele um refrigerador") a cuba redonda de sobrepor do PDF (os 2 círculos
                  # da ARQ_LOUÇAS: a borda e o bojo), branca, com o misturador de parede (a parede à direita, a bica para
                  # a esquerda), e o refrigerador de inox da biblioteca (Casa A) na ponta de baixo, 0,60 m, os puxadores
                  # para a sala
                  "cuba": {"borda": (1766.4, 1565.2, 1786.7, 1585.5), "bojo": (1767.6, 1566.4, 1785.4, 1584.3),
                           "ralo": (1776.5, 1575.4, 1.1), "corpo": (1789.2, 1574.0, 1794.8, 1576.8),
                           "bica": (1783.6, 1574.75, 1789.2, 1576.05), "janela": (1760, 1558, 1796, 1592)},
                  "geladeira": {"png": AQUI.parents[1] / "POE642_CasaA" / "biblioteca-objetos" / "02-terreo" / "cozinha" /
                                "geladeira-inox.png", "ret": (1759.6, 1646.1, 1795.4, 1682.1), "puxador_px": 1.6}}
LOUCA = {"borda": (243, 244, 245), "bojo": (236, 237, 239), "fio": (150, 152, 156), "aresta": (206, 208, 211),
         "ralo": (150, 154, 158), "cromo": ((132, 134, 138), (232, 234, 237)), "sombra": (-0.6, 0.6, 0.6, 0.30)}

BORDA_PISCINA = {"agua": [(918.0, 509.0, 1096.0, 969.0), (1096.0, 509.0, 1264.0, 800.0), (1114.0, 818.0, 1264.0, 969.0)],
                 "larg_px": 18, "junta_px": 36, "amostra": (1120, 1110, 1320, 1310),
                 "final_a": AQUI.parents[1] / "POE642_CasaA" / "renders" / "POE642_CasaA_PH_Subsolo_final_rotulos.png",
                 # (16/11, usuário: "essa borda tem que ser sem traços, de forma lisa"; "as bordas da piscina devem ser no
                 # marmore bege bahia com um levemente escurecida para dar ideia de autorelevo") lisa, sem as juntas e sem
                 # o fio com o deck, um tom abaixo do deck (o alto-relevo), a quina junto à água um pouco mais clara
                 "levigado": 0.5, "claro": 0.95, "junta": 1.0, "fio_deck": 0.97, "quina": 1.03, "beira_agua": 0.80}

ARANDELAS = {"png": BIB_D / "suite-master" / "arandela-articulada-preta-d.png", "criados": (97046, 97058),
             "cupula_m": 0.26}


def _rgba(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 8)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def _cuba_redonda(out, par, q, lc=LOUCA, ss=8):
    """A cuba branca de sobrepor redonda (a borda e o bojo do PDF) com o fio, o bojo com a sombra suave, o ralo, e o
    misturador cromado de parede (o corpo junto à parede, a bica para dentro da cuba), em `ss` x."""
    A0, B0, A1, B1 = q["janela"]
    w, h = (A1 - A0) * ss, (B1 - B0) * ss
    X, Y = np.meshgrid(A0 + (np.arange(w) + 0.5) / ss, B0 + (np.arange(h) + 0.5) / ss)
    base = cv2.resize(out[B0:B1, A0:A1].astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)

    def mistura(img, a, cor):
        a = np.clip(a, 0, 1)[..., None]
        return img * (1 - a) + (cor if np.ndim(cor) == 3 else np.float32(cor)) * a

    def circ(r):
        x0, y0, x1, y1 = r
        return np.hypot(X - (x0 + x1) / 2, Y - (y0 + y1) / 2) - (x1 - x0 + y1 - y0) / 4

    def ret(r, raio):
        x0, y0, x1, y1 = r
        cx, cy, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - raio, (y1 - y0) / 2 - raio
        dx, dy = np.abs(X - cx) - hx, np.abs(Y - cy) - hy
        return np.hypot(np.maximum(dx, 0), np.maximum(dy, 0)) + np.minimum(np.maximum(dx, dy), 0) - raio

    sdx, sdy, sig, forca = lc["sombra"]
    db = circ(q["borda"])
    sh = cv2.GaussianBlur((np.hypot(X - sdx - (q["borda"][0] + q["borda"][2]) / 2,
                                    Y - sdy - (q["borda"][1] + q["borda"][3]) / 2) <
                           (q["borda"][2] - q["borda"][0]) / 2).astype(np.float32), (0, 0), sig * ss)
    base = base * (1 - forca * sh)[..., None]
    base = mistura(base, (db < 0).astype(np.float32), lc["borda"])
    base = mistura(base, (np.abs(db) < 0.28).astype(np.float32) * 0.85, lc["fio"])
    dj = circ(q["bojo"])
    bx0, by0, bx1, by1 = q["bojo"]
    rb = (bx1 - bx0) / 2
    cxb, cyb = (bx0 + bx1) / 2, (by0 + by1) / 2
    lado = np.clip(((Y - cyb) * -1 + (X - cxb)) / (rb * 1.414), -1, 1)            # o lado de cima e da direita
    perto = np.clip(1 - (-dj) / 3.0, 0, 1)
    tom = 1 - 0.07 * perto - 0.12 * np.clip(lado, 0, 1) * perto
    base = mistura(base, (dj < 0).astype(np.float32), np.float32(lc["bojo"])[None, None] * tom[..., None])
    base = mistura(base, (np.abs(dj) < 0.22).astype(np.float32) * 0.7, lc["aresta"])
    rx, ry, rr = q["ralo"]
    dr = np.hypot(X - rx, Y - ry)
    base = mistura(base, (dr < rr).astype(np.float32), lc["ralo"])
    c0, c1 = np.float32(lc["cromo"][0]), np.float32(lc["cromo"][1])
    for r_, raio in ((q["corpo"], 0.9), (q["bica"], 0.6)):
        d = ret(r_, raio)
        sh = cv2.GaussianBlur((ret((r_[0] - sdx, r_[1] - sdy, r_[2] - sdx, r_[3] - sdy), raio) < 0)
                              .astype(np.float32), (0, 0), sig * ss)
        base = base * (1 - 0.35 * sh * (d >= 0))[..., None]
        meio = (r_[1] + r_[3]) / 2
        t = np.clip(1 - np.abs(Y - meio) / ((r_[3] - r_[1]) / 2), 0, 1) ** 0.8
        base = mistura(base, (d < 0).astype(np.float32), c0[None, None] + (c1 - c0)[None, None] * t[..., None])
    bx = q["bica"][0]                                                  # a ponta da bica (à esquerda), um tom abaixo
    base = mistura(base, ((np.abs(X - (bx + 0.35)) < 0.35) & (np.abs(Y - (q["bica"][1] + q["bica"][3]) / 2) < 0.6))
                   .astype(np.float32) * 0.8, c0 * 0.9)
    novo = cv2.resize(base, (A1 - A0, B1 - B0), interpolation=cv2.INTER_AREA)
    out = out.copy()
    reg = out[B0:B1, A0:A1].astype(np.float32)
    fora = par[B0:B1, A0:A1][..., None]
    out[B0:B1, A0:A1] = np.clip(np.round(np.where(fora, reg, novo)), 0, 255).astype(np.uint8)
    return out


def bancada_intima(out, par, q=BANCADA_INTIMA):
    import mobiliario_terreo_casac_1311 as MB
    out = out.copy()
    x0, y0, x1, y1 = q["limpa"]
    out[y0:y1, x0:x1] = out[y0:y1, x0 + q["limpa_dx"]:x1 + q["limpa_dx"]]
    a0, b0, a1, b1 = q["ret"]
    ss = q["ss"]
    Wb, Hb = int(round((a1 - a0) * ss)), int(round((b1 - b0) * ss))
    R = np.rot90(_rgba(q["png"]), -1)                                  # o fundo (a torneira) para a direita
    k = Wb / R.shape[1]
    R = cv2.resize(np.ascontiguousarray(R), (Wb, int(round(R.shape[0] * k))), interpolation=cv2.INTER_AREA)
    h = R.shape[0]
    r0, r1 = (int(f * h) for f in q["liso_frac"])
    liso = R[r0:r1, :, :3]
    reps = []
    while sum(p.shape[0] for p in reps) < Hb:                          # a pedra lisa repetida em espelho
        reps.append(liso if len(reps) % 2 == 0 else liso[::-1])
    T = np.concatenate(reps, axis=0)[:Hb].copy()
    # a aresta da face livre (à esquerda) e das pontas um tom abaixo
    e = max(1, int(round(q["aresta_px"] * ss)))
    T[:, :e] *= q["aresta"]
    T[:e // 2 + 1] *= 0.5 + 0.5 * q["aresta"]
    T[-(e // 2 + 1):] *= 0.5 + 0.5 * q["aresta"]
    P = np.dstack([T, np.full(T.shape[:2], 255, np.float32)])
    out = MB.pousar(out, P, (a0 + a1) / 2, (b0 + b1) / 2, a1 - a0, b1 - b0, 0.0, "movel", par)
    out = _cuba_redonda(out, par, q["cuba"])
    g = q["geladeira"]
    G = np.rot90(_rgba(g["png"]), -1)                                  # a frente (os puxadores) para a esquerda
    gx0, gy0, gx1, gy1 = g["ret"]
    ext = g["puxador_px"]                                              # os puxadores saem da face da bancada
    corpo = 0.89                                                       # a fração do PNG sem os puxadores
    Lw = (gx1 - gx0) / corpo
    out = MB.pousar(out, np.ascontiguousarray(G), gx1 - Lw / 2 - ext * 0, (gy0 + gy1) / 2, Lw, gy1 - gy0, 0.0,
                    "movel", par)
    print("    sala íntima: a bancada no travertino da biblioteca, sem as linhas técnicas; a cuba redonda de sobrepor do "
          "PDF com o misturador de parede e o refrigerador de inox na ponta, os puxadores para a sala")
    return out


def _bege_levigado(H, W, q):
    import materiais_terreo_casac_1311 as MT
    A = cv2.imread(str(q["final_a"]))
    a0, b0, a1, b1 = q["amostra"]
    T = MT.sem_emenda(A[b0:b1, a0:a1].astype(np.float32), H, W)
    lf = cv2.GaussianBlur(T, (0, 0), 10)
    T = T - q["levigado"] * (lf - lf.reshape(-1, 3).mean(axis=0))
    return T * q["claro"]


def borda_piscina(out, q=BORDA_PISCINA):
    o = out.astype(np.float32)
    H, W = out.shape[:2]
    agua = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in q["agua"]:
        agua[int(round(y0)):int(round(y1)), int(round(x0)):int(round(x1))] = 1
    w = q["larg_px"]
    perto = cv2.dilate(agua, np.ones((2 * w + 1, 2 * w + 1), np.uint8))
    capa = (perto > 0) & (agua == 0)
    ys, xs = np.nonzero(capa)
    Y0, Y1, X0, X1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    T = _bege_levigado(Y1 - Y0, X1 - X0, q)
    reg = o[Y0:Y1, X0:X1]
    m = capa[Y0:Y1, X0:X1]
    ag = agua[Y0:Y1, X0:X1] > 0
    # o lado de cada px da capa: água em cima ou embaixo (faixa deitada: juntas em pé) ou dos lados (juntas deitadas)
    k = np.ones((2 * w + 1, 1), np.uint8)
    vert = cv2.dilate(ag.astype(np.uint8), k) > 0                       # água a até w px na vertical
    hori = cv2.dilate(ag.astype(np.uint8), k.T) > 0
    jy, jx = np.mgrid[0:Y1 - Y0, 0:X1 - X0]
    junta = (m & vert & ~hori & (((jx + X0 - 918) % q["junta_px"]) == 0)) | \
            (m & hori & ~vert & (((jy + Y0 - 509) % q["junta_px"]) == 0))
    T = T * np.where(junta, q["junta"], 1.0)[..., None]
    # o fio da junta com o deck (a borda de fora da capa) e a quina clara junto à água
    fora = m & (cv2.dilate((~m & ~ag).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    quina = m & (cv2.dilate(ag.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    T = T * np.where(fora, q["fio_deck"], 1.0)[..., None] * np.where(quina, q["quina"], 1.0)[..., None]
    reg[m] = T[m]
    # a beira da água: o fio escuro do desnível, logo dentro da água
    beira = ag & (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    reg[beira] *= q["beira_agua"]
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    piscina: a borda de {w / 59.7:.2f} m em placas de Bege Bahia levigado em volta da piscina, da prainha e do "
          f"spa (as faixas entre os tanques inclusive), as juntas a cada {q['junta_px'] / 59.7:.2f} m, o fio com o deck e "
          "a quina junto à água")
    return out


def _parede_mais_perto(out, cx, cy, maximo=80):
    """A face da parede mais perto do ponto, nas 4 direções: (distância px, direção (dx, dy))."""
    melhor = None
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        for t in range(1, maximo):
            x, y = int(round(cx + dx * t)), int(round(cy + dy * t))
            if not (0 <= x < out.shape[1] and 0 <= y < out.shape[0]):
                break
            if np.abs(out[y, x].astype(int) - 80).max() <= 6:
                if melhor is None or t < melhor[0]:
                    melhor = (t, (dx, dy))
                break
    return melhor


def arandela_png(L_px, cup_px, q=ARANDELAS):
    """A arandela deitada (a placa à esquerda, a cúpula à direita) com a cúpula de `cup_px` e `L_px` da placa ao meio da
    cúpula: o braço encurtado (as colunas do meio do braço saem) ou alongado."""
    P = _rgba(q["png"])
    h, w = P.shape[:2]
    escuro = (P[..., 3] > 128) & (P[..., :3].mean(axis=2) < 90)
    cont = escuro.sum(axis=0).astype(np.float32)
    nucleo = np.nonzero(cont > 0.85 * cont.max())[0]
    dc = float(nucleo.mean())                                          # o meio da cúpula
    r = h / 2.0
    k = cup_px / h
    L_png = L_px / k                                                   # quanto deve ter, no PNG, da placa ao meio da cúpula
    placa = int(np.nonzero(cont > 0.25 * cont.max())[0].min())
    braco0 = placa + int(0.06 * w)                                     # depois da placa
    braco1 = int(dc - r) - 4                                           # antes da cúpula
    tirar = int(round(dc - L_png))
    if tirar > 0 and braco1 - braco0 > tirar + 4:
        meio = (braco0 + braco1) // 2
        P = np.concatenate([P[:, :meio - tirar // 2], P[:, meio + (tirar - tirar // 2):]], axis=1)
    elif tirar < 0:
        meio = (braco0 + braco1) // 2
        col = P[:, meio:meio + 1]
        P = np.concatenate([P[:, :meio], np.repeat(col, -tirar, axis=1), P[:, meio:]], axis=1)
    return np.ascontiguousarray(P), k


def arandelas(Q, out, par, q=ARANDELAS):
    import mobiliario_terreo_casac_1311 as MB
    import regras_terreo_casab_1311 as RT
    if not Path(q["png"]).exists():
        print("    suíte master: arandelas (o PNG ainda não está na biblioteca)")
        return out
    px_m = 59.7
    cup = q["cupula_m"] * px_m
    for i in q["criados"]:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        t, (dx, dy) = _parede_mais_perto(out, cx, cy)
        L = t - 0.5                                                    # da face da parede ao meio do criado
        P, k = arandela_png(L, cup)
        Lt, Ht = P.shape[1] * k, P.shape[0] * k
        # o meio da peça: da parede, metade do comprimento para dentro; o giro leva a placa (a esquerda do PNG) à parede
        mx, my = cx + dx * (t - Lt / 2), cy + dy * (t - Lt / 2)
        g = {(0, -1): -90.0, (0, 1): 90.0, (-1, 0): 0.0, (1, 0): 180.0}[(dx, dy)]
        out = MB.pousar(out, P, mx, my, Lt, Ht, g, "mesa", par)
    print(f"    suíte master: as {len(q['criados'])} arandelas articuladas pretas do 3D, presas na parede da cabeceira, "
          f"a cúpula de {q['cupula_m']:.2f} m sobre o criado, no lugar do abajur")
    return out

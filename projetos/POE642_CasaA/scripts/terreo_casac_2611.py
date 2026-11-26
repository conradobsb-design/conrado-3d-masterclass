"""Casa C Térreo, levantamento de 26/11 aplicado (o usuário: "sim", os 8 itens), mais as portas da sala de almoço.

Itens (a folha `../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_2611_levantamento.jpg`), na ordem em que entram:

- **soleiras** (8): as soleiras das portas sociais no travertino mais escuro (`terreo_casaa_2511g.soleira_trav`, a
  pedra a 84%, como no Subsolo): de face a face da parede, pelos batentes do PDF (BH 1, 2 e 3, BH master 1 e 2, closet
  master 2, quartos 1, 2 e 3, suíte master, lavabo e lavabos masc. e fem.) e a do hall de entrada; as da cozinha e do
  serviço ficam no tom da bancada.
- **almoco** (usuário, sobre a folha que atravessa a passagem para a garagem: "representar como janela fechada"): as
  duas portas de giro entre a sala de almoço e a garagem, desenhadas abertas (a barra para os dois lados), fechadas no
  vão: o piso de volta onde as barras estavam (o travertino no lado da sala, o marrom da garagem), a soleira no
  travertino escuro e a folha de vidro claro no meio do vão, de ponta a ponta.
- **janelas** (3): as janelas pequenas dos banhos (BH 3, 2 e 1 em cima, as duas laterais do box do BH master 1, BH
  master 2 em cima, BH externo e BH serviço) como a de baixo do BH master 2: o vão na parede, o vidro claro do meio
  com o caixilho escuro e o montante preto no meio; o que sobrava para dentro dos banhos (o "T" do montante, os frisos
  cinza) vira o piso de logo ao lado.
- **box_bhm1** e **topo_porta** (4): o box do BH master 1 em vidro claro, a frente de parede a parede com as duas portas
  fechadas e a divisória entre o chuveiro e o vaso (`um_pav_casaa_2511e.folhas_vidro`), no lugar dos perfis cromados
  (o piso de volta por baixo); no topo da porta da varanda, as letrinhas dentro da parede viram a parede.
- **ilha** e **pontinhos** (5 e 6): o risco branco com contorno preto ao longo da ilha da cozinha (um retângulo branco
  sem traço no PDF) vira a pedra da ilha de logo à esquerda; os pontinhos brancos do piso marrom da cozinha e da
  gourmet (manchinhas claras de até ~3 px da final) viram o marrom de em volta (a mediana), fora dos rótulos.
- **estar** (7): a ponta direita do sofá de 3 lugares (o braço, o contorno e a sombra de contato, cortados por um
  retângulo de travertino) refeita pela ponta esquerda espelhada (o sofá é simétrico); o arco cinza solto em volta do
  sofá curvo (a linha fina de 2341, 1534 até 2276, 1588, ajustada num círculo) vira o travertino (a textura do piso na
  luz de em volta).
- **bancadas** (2): a bancada do lavabo (junto à adega) e a da área de serviço no granito da referência
  (`fontes_procedurais.granito_referencia`, o do BH academia do Subsolo), a beira da frente um tom abaixo, sem a
  moldura; no lavabo, a cuba esculpida no granito (aba polida, bacia funda com a sombra por dentro, válvula) e a
  torneira cromada saindo da parede; na área de serviço as duas cubas de inox e as torneiras ficam.
- **rotulos** (1): o retângulo de fundo atrás das letras (deck e piso marrom): o fundo de cada rótulo refeito com o
  mesmo piso de outro lugar (no deck, 6 tábuas abaixo ou 110 px ao lado, as tábuas alinhadas; no marrom, um trecho
  limpo da mesma área ou da garagem), na luz do entorno, e as letras de volta por cima pela cobertura de cada uma.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2611.py [itens]
"""
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vetor_2511 as V               # noqa: E402
import terreo_casaa_2511d as D       # noqa: E402
import terreo_casaa_2511g as G       # noqa: E402
import um_pav_casaa_2511 as U        # noqa: E402
import um_pav_casaa_2511c as C       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import um_pav_casaa_2511e as E       # noqa: E402
import fontes_procedurais as FP      # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]                     # o travertino novo, o 12K na escala desta planta
PX_M = 59.7059
PAREDE = (80.0, 80.0, 80.0)
PERFIL = (34.0, 34.0, 36.0)
VIDRO_J = (232.0, 234.0, 236.0)      # o vidro da janela de baixo do BH master 2 (a referência)
SOLEIRA = dict(escurecer=0.84, contorno=1.0, larg=0.22)


def copiar(img, s, origem, r, d, lados, pena=1.0):
    return U._copiar(img, s, origem, r, d, lados, pena)


def pintar(img, s, origem, rets, cor):
    x0 = min(r[0] for r in rets) - 1
    y0 = min(r[1] for r in rets) - 1
    x1 = max(r[2] for r in rets) + 1
    y1 = max(r[3] for r in rets) + 1
    jan, reg = C._reg(img, (x0, y0, x1, y1), s, origem)
    reg = V.compor(reg, V.cob([V.ret(*r) for r in rets], jan, s, origem), np.float32(cor))
    return C._gravar(img, jan, reg)


def soleira(img, s, origem, rets):
    return G.soleira_trav(img, s, origem, rets, q=SOLEIRA)


# ----------------------------------------------------------------------------------------------------------------------
# 8. As soleiras (de face a face, pelos batentes do PDF)
SOLEIRAS = {
    "bh3": (1114.4, 426.6, 1172.3, 435.5), "bh2": (1705.5, 426.6, 1763.4, 435.5), "bh1": (1854.8, 426.6, 1912.7, 435.5),
    "bhm1": (830.8, 569.9, 888.7, 578.8), "q3": (1245.7, 569.9, 1303.7, 578.8), "q2": (1627.9, 569.9, 1685.8, 578.8),
    "lavabo": (2395.1, 811.7, 2459.1, 820.6), "q1": (1804.6, 599.5, 1813.6, 657.5),
    "suite": (1231.4, 757.3, 1240.4, 821.3), "bhm2": (807.5, 837.9, 816.4, 895.9),
    "clm2": (888.1, 837.9, 897.1, 895.9), "lavM": (1318.0, 1503.7, 1327.0, 1555.7),
    "lavF": (1413.5, 1503.7, 1422.5, 1555.7), "hall": (2700.3, 1299.0, 2712.2, 1424.6)}


def soleiras(img, s, origem, nomes=None):
    for k, r in SOLEIRAS.items():
        if nomes is None or k in nomes:
            img = soleira(img, s, origem, [r])
    return img


# ----------------------------------------------------------------------------------------------------------------------
# As portas da sala de almoço para a garagem, fechadas (como janela)
ALMOCO = dict(
    portas=[dict(vao=(2703.3, 671.3, 2712.2, 756.3), barra=(2637.0, 686.0, 2725.5, 694.5)),
            dict(vao=(2703.3, 807.3, 2712.2, 917.8), barra=(2647.0, 850.5, 2759.0, 864.5))],
    folha=1.6)                                           # a espessura da folha de vidro (px da final)


def almoco(img, s, origem, q=ALMOCO):
    for p in q["portas"]:
        vx0, vy0, vx1, vy1 = p["vao"]
        bx0, by0, bx1, by1 = p["barra"]
        # o lado da sala: o travertino refeito no lugar da barra (com uma folga em volta para a luz)
        img = G.refazer(img, s, origem, [((bx0, by0, vx0, by1), "ltb")], pena=1.0)
        # o lado da garagem: o marrom de logo acima, na luz da beira (a barra tem ~6 a 11 px)
        h = by1 - by0
        img = copiar_casado(img, s, origem, (vx1, by0, bx1, by1), (0.0, -(h + 3.0)), pena=2.0)
        # o vão: a soleira escura e a folha fechada no meio, de ponta a ponta
        img = soleira(img, s, origem, [p["vao"]])
        cx = (vx0 + vx1) / 2
        f = q["folha"] / 2
        img = vidros(img, s, origem, (vx0 - 2, vy0 - 2, vx1 + 2, vy1 + 2), [[(cx - f, vy0, cx + f, vy1)]])
    return img


def copiar_casado(img, s, origem, r, d, pena=2.0, anel=3.0):
    """O retângulo r recebe a imagem deslocada d, na luz do entorno (o ganho por canal medido no anel em volta de r)."""
    x0, y0, x1, y1 = r
    jan = V.janela(img, (x0 - anel - 1, y0 - anel - 1, x1 + anel + 1, y1 + anel + 1), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    dx, dy = int(round(d[0] * s)), int(round(d[1] * s))
    F = img[Y0:Y1, X0:X1].astype(np.float32)
    S_ = img[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    dd = np.maximum.reduce([x0 - X, X - x1, y0 - Y, Y - y1])           # > 0 fora do retângulo
    ring = (dd > 0.5) & (dd < anel)
    g = np.median(F[ring], axis=0) / np.maximum(np.median(S_[ring], axis=0), 1.0)
    w = np.clip((-dd + pena) / pena, 0, 1)
    out = F * (1 - w[..., None]) + S_ * g[None, None, :] * w[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def vidros(img, s, origem, caixa, folhas):
    jan, reg = C._reg(img, caixa, s, origem, folga=int(2 * s) + 2)
    reg = E.folhas_vidro(reg, jan, s, origem, folhas)
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
# 3. As janelas pequenas dos banhos (como a de baixo do BH master 2)
# vão do PDF, o lado de dentro do banho (para limpar o que sobrava), e os lados abertos da emenda
JANELAS = {
    "bh3": dict(vao=(1194.0, 331.0, 1227.2, 337.0), limpar=[((1191.0, 323.5, 1230.5, 331.0), (0.0, -7.0), "lrt")]),
    "bh2": dict(vao=(1651.5, 331.0, 1684.8, 336.0), limpar=[((1648.5, 323.5, 1688.0, 331.0), (0.0, -7.0), "lrt")]),
    "bh1": dict(vao=(1934.4, 331.0, 1967.6, 336.5), limpar=[((1931.5, 323.5, 1970.5, 331.0), (0.0, -7.0), "lrt")]),
    "bhm2": dict(vao=(691.0, 828.4, 741.8, 836.2), limpar=[((688.0, 822.5, 745.0, 828.4), (0.0, -6.0), "lrt"),
                                                          ((688.0, 836.2, 745.0, 841.0), (0.0, 5.5), "lrb")]),
    "ext": dict(vao=(2931.5, 811.7, 2956.6, 817.7), limpar=[((2928.5, 804.5, 2960.0, 811.7), (0.0, -7.0), "lrt")]),
    "serv": dict(vao=(2653.7, 662.4, 2700.3, 668.4), limpar=[((2650.5, 655.5, 2703.5, 662.4), (0.0, -7.0), "lrt")]),
    "m1e": dict(vao=(744.8, 378.6, 750.8, 409.8), parede=[(742.0, 378.6, 744.8, 409.8)],
                limpar=[((737.0, 390.5, 742.0, 400.0), (-5.0, 0.0), "ltb"),
                        ((750.8, 376.0, 756.0, 407.5), (5.0, 0.0), "rtb")]),
    "m1d": dict(vao=(894.1, 378.6, 900.0, 409.8), parede=[(900.0, 378.6, 904.8, 409.8)],
                limpar=[((888.5, 376.0, 894.1, 407.5), (-5.0, 0.0), "ltb")]),
}


def janela(img, s, origem, q):
    for r, d, lados in q["limpar"]:
        img = copiar(img, s, origem, r, d, lados, pena=0.8)
    x0, y0, x1, y1 = q["vao"]
    img = pintar(img, s, origem, [q["vao"]] + q.get("parede", []), PAREDE)
    w, h = x1 - x0, y1 - y0
    if w >= h:                                   # deitada: o vidro no meio da espessura, o montante em pé
        a, b = 0.18 * h, 0.15 * h
        vid = (x0 + 0.25, y0 + a, x1 - 0.25, y1 - b)
        cx = (x0 + x1) / 2
        mont = (cx - 0.5, y0 + 0.2, cx + 0.5, y1 - b)
    else:
        a, b = 0.16 * w, 0.16 * w
        vid = (x0 + a, y0 + 0.25, x1 - b, y1 - 0.25)
        cy = (y0 + y1) / 2
        mont = (x0 + a, cy - 0.5, x1 - b, cy + 0.5)
    img = pintar(img, s, origem, [vid], VIDRO_J)
    return pintar(img, s, origem, [mont], PERFIL)


def janelas(img, s, origem, nomes=None):
    for k, q in JANELAS.items():
        if nomes is None or k in nomes:
            img = janela(img, s, origem, q)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 4. O box do BH master 1 e o topo da porta da varanda
BOX = dict(zonas=[((750.8, 406.5, 894.1, 415.0), "tb"),            # a frente: os perfis cromados
                  ((821.5, 326.5, 836.5, 352.8), "lr"),             # a divisória (sem o tracejado da claraboia)
                  ((821.5, 357.2, 836.5, 406.5), "lr")],
           folhas=[[(750.8, 409.8, 894.1, 411.6)], [(828.2, 328.2, 830.0, 409.8)]])
TOPO = dict(letras=((775.0, 570.8, 792.5, 575.2), (-18.0, 0.0), "lr"))


def box_bhm1(img, s, origem, q=BOX):
    img = G.refazer(img, s, origem, q["zonas"], pena=1.0)
    caixa = (748.0, 325.0, 897.0, 414.0)
    return vidros(img, s, origem, caixa, q["folhas"])


def _mediana(img, s, origem, r):
    jan, reg = C._reg(img, r, s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    m = (xs[None, :] >= r[0]) & (xs[None, :] <= r[2]) & (ys[:, None] >= r[1]) & (ys[:, None] <= r[3])
    return np.median(reg[m], axis=0).astype(np.float32)


def topo_porta(img, s, origem, q=TOPO):
    r, d, lados = q["letras"]
    return copiar(img, s, origem, r, d, lados, pena=1.0)


# ----------------------------------------------------------------------------------------------------------------------
# 5 e 6. A ilha da cozinha e os pontinhos do piso marrom
ILHA = ((2283.0, 365.5, 2293.4, 557.5), (-11.0, 0.0), "lt")
PONTOS = dict(zonas=[(2205.0, 285.0, 2470.0, 662.0), (1228.0, 918.0, 1648.0, 1162.0)],
              rotulos=[(2318.0, 500.0, 2410.0, 552.0), (1355.0, 1000.0, 1445.0, 1060.0)],
              dif=26.0, area=7.0)


def ilha(img, s, origem, q=ILHA):
    r, d, lados = q
    return copiar(img, s, origem, r, d, lados, pena=0.6)


def pontinhos(img, s, origem, q=PONTOS):
    for z in q["zonas"]:
        jan = V.janela(img, z, s, origem, folga=int(3 * s) + 2)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1]
        k = max(5, int(round(2.6 * s)) | 1)
        med = cv2.medianBlur(reg, k).astype(np.float32)
        f = reg.astype(np.float32)
        L, Lm = f.mean(2), med.mean(2)
        marrom = ((med[..., 2] - med[..., 0]) > 22) & (Lm > 55) & (Lm < 165)
        spk = ((L - Lm) > q["dif"]) & marrom
        xs, ys = V.coords(jan, s, origem)
        dentro = (xs[None, :] >= z[0]) & (xs[None, :] <= z[2]) & (ys[:, None] >= z[1]) & (ys[:, None] <= z[3])
        for r in q["rotulos"]:
            dentro &= ~((xs[None, :] >= r[0]) & (xs[None, :] <= r[2]) & (ys[:, None] >= r[1]) & (ys[:, None] <= r[3]))
        spk &= dentro
        n, lb, st, _ = cv2.connectedComponentsWithStats(spk.astype(np.uint8), 8)
        ok = st[:, cv2.CC_STAT_AREA] <= q["area"] * s * s
        ok[0] = False
        m = ok[lb]
        kk = max(1, int(round(0.5 * s)))
        m = cv2.dilate(m.astype(np.uint8), np.ones((2 * kk + 1, 2 * kk + 1), np.uint8)) > 0
        m &= dentro & marrom
        f[m] = med[m]
        img[Y0:Y1, X0:X1] = np.clip(np.round(f), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 7. O estar: o braço do sofá e o arco solto do sofá curvo
BRACO = dict(zona=(1963.5, 1549.0, 1974.0, 1604.5), eixo2=3725.6, pena=1.2)   # o espelho da ponta esquerda do sofá
ARCO = dict(pontos=[(2341.0, 1534.0), (2336.0, 1542.0), (2331.0, 1550.0), (2326.0, 1556.0), (2321.0, 1562.0),
                    (2316.0, 1566.0), (2311.0, 1570.0), (2305.0, 1574.0), (2299.0, 1578.0), (2292.0, 1582.0),
                    (2283.0, 1586.0), (2276.0, 1588.0)],
            busca=4.5, caixa=(2262.0, 1495.0, 2362.0, 1597.0), x=(2272.0, 2356.0), y=(1500.0, 1591.0), sig=4.0)


def braco(img, s, origem, q=BRACO):
    """A ponta direita do sofá de 3 lugares (o braço, o contorno e a sombra de contato, que o retângulo de travertino
    cortava) pela ponta esquerda, espelhada (o sofá é simétrico; o travertino tem os veios na horizontal)."""
    jan = V.janela(img, q["zona"], s, origem, folga=int(2 * s) + 2)
    X0, Y0, X1, Y1 = jan
    xs, ys = V.coords(jan, s, origem)
    mx = ((q["eixo2"] - xs) - origem[0]) * s - 0.5
    my = (ys - origem[1]) * s - 0.5
    MX, MY = np.meshgrid(mx.astype(np.float32), my.astype(np.float32))
    fonte = cv2.remap(img, MX, MY, cv2.INTER_LINEAR).astype(np.float32)
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    a = G._pena(jan, s, origem, q["zona"], "ltrb", q["pena"])[..., None]
    return C._gravar(img, jan, reg * (1 - a) + fonte * a)


def _circulo(pts):
    P = np.array(pts, float)
    A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
    b = (P ** 2).sum(1)
    cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
    return cx, cy, np.sqrt(c + cx * cx + cy * cy)


def arco(img, s, origem, q=ARCO):
    """A linha cinza solta: os px cinza (sem a cor quente do travertino, nem verdes) na faixa de +-`busca` px do círculo
    ajustado aos pontos (no 12K a linha anda até 2 px da final), um pouco dilatados, viram o travertino."""
    cx, cy, R = _circulo(q["pontos"])
    jan, reg = C._reg(img, q["caixa"], s, origem, folga=2)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    dist = np.abs(np.hypot(X - cx, Y - cy) - R)
    xa, xb = q["x"]
    ya, yb = q["y"]
    faixa = (dist < q["busca"]) & (X >= xa) & (X <= xb) & (Y >= ya) & (Y <= yb)
    L = reg.mean(2)
    rb = reg[..., 2] - reg[..., 0]
    verde = reg[..., 1] > reg[..., 2] - 4
    linha = faixa & (rb < 21) & (L < 214) & ~verde
    k = max(1, int(round(0.6 * s)))
    linha = cv2.dilate(linha.astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
    linha &= faixa & ~verde
    a = cv2.GaussianBlur(linha.astype(np.float32), (0, 0), max(0.35 * s, 0.5))
    a = np.clip(a * 1.8, 0, 1) * (dist < q["busca"] + 1)
    TT = D.piso_tt(jan, s).astype(np.float32)
    trav = (rb > 22) & (L > 165) & ~linha & (dist < 9.0) & ~verde
    r_ = L / np.maximum(TT.mean(2), 1.0)
    sig = q["sig"] * s
    num = cv2.GaussianBlur(np.where(trav, r_, 0).astype(np.float32), (0, 0), sig)
    den = cv2.GaussianBlur(trav.astype(np.float32), (0, 0), sig)
    luz = num / np.maximum(den, 1e-3)
    novo = TT * luz[..., None]
    reg = reg * (1 - a[..., None]) + novo * a[..., None]
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
# 2. As bancadas de granito
CROMO = {"escuro": (122, 126, 130), "meio": (190, 193, 196), "claro": (238, 240, 242), "contorno": (88, 92, 96)}
LAVABO = dict(rets=[(2365.9, 1028.5, 2396.3, 1187.9), (2365.9, 1072.9, 2399.9, 1144.6)],
              frente=[(2395.1, 1028.5, 2396.3, 1072.9), (2398.7, 1072.9, 2399.9, 1144.6),
                      (2395.1, 1144.6, 2396.3, 1187.9)],
              aba=(2370.1, 1085.9, 2397.6, 1130.1), bacia=(2371.3, 1087.1, 2396.4, 1128.9),
              torneira_base=(2367.4, 1108.4, 1.35), torneira_bico=(2367.6, 1107.7, 2378.0, 1109.1), semente=643)
SERVICO = dict(rets=[(2655.5, 343.0, 2700.3, 492.2)], frente=[(2655.5, 343.0, 2656.7, 492.2)],
               manter=[(2659.0, 354.5, 2694.5, 392.5), (2659.0, 396.0, 2694.5, 433.5),
                       (2691.5, 368.5, 2700.3, 377.5), (2691.5, 410.5, 2700.3, 419.5)], semente=644)
BANC = dict(testeira_tom=0.86, aba_tom=1.07, bacia_r=2.2, bacia_tom=0.80, bacia_sombra=(0.38, 2.4),
            bacia_contorno=(34.0, 44.0, 58.0), bacia_contorno_l=0.35, valvula=1.1)


def _arred(x0, y0, x1, y1, r, n=10):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for a in np.linspace(a0, a0 + 90, n):
            pts.append((cx + r * np.cos(np.radians(a)), cy + r * np.sin(np.radians(a))))
    return pts


def _disco(cx, cy, r, n=48):
    return [(cx + r * np.cos(t), cy + r * np.sin(t)) for t in np.linspace(0, 2 * np.pi, n, endpoint=False)]


def bancada(img, s, origem, q, p=BANC):
    caixa = (min(r[0] for r in q["rets"]) - 2, min(r[1] for r in q["rets"]) - 2,
             max(r[2] for r in q["rets"]) + 2, max(r[3] for r in q["rets"]) + 2)
    jan = V.janela(img, caixa, s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    orig = reg.copy()
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    Gr = FP.granito_referencia(H, W, PX_M * s, semente=q["semente"]).astype(np.float32)
    a = np.zeros((H, W), np.float32)
    for r in q["rets"]:
        a = np.maximum(a, V.cob([V.ret(*r)], jan, s, origem))
    fr = np.zeros((H, W), np.float32)
    for r in q["frente"]:
        fr = np.maximum(fr, V.cob([V.ret(*r)], jan, s, origem))
    pedra = Gr * (1 - (1 - p["testeira_tom"]) * fr)[..., None]
    reg = reg * (1 - a[..., None]) + pedra * a[..., None]
    if "bacia" in q:
        a_aba = V.cob([V.ret(*q["aba"])], jan, s, origem)
        bx0, by0, bx1, by1 = q["bacia"]
        a_bac = V.cob([_arred(bx0, by0, bx1, by1, p["bacia_r"])], jan, s, origem)
        k = (a_aba * (1 - a_bac))[..., None]
        reg = reg * (1 - k) + (Gr * p["aba_tom"]) * k
        d = np.minimum.reduce([X - bx0, bx1 - X, Y - by0, by1 - Y])
        lado = np.clip(((bx1 - X) / (bx1 - bx0) + (by1 - Y) / (by1 - by0)) / 2, 0, 1)   # a parede à esquerda
        f, alc = p["bacia_sombra"]
        prof = 1 - f * np.clip(1 - np.maximum(d, 0) / alc, 0, 1) * (0.45 + 0.55 * lado)
        reg = reg * (1 - a_bac[..., None]) + (Gr * p["bacia_tom"] * prof[..., None]) * a_bac[..., None]
        lc = p["bacia_contorno_l"]
        a_bin = V.cob([_arred(bx0 + lc, by0 + lc, bx1 - lc, by1 - lc, max(p["bacia_r"] - lc, 0.5))], jan, s, origem)
        reg = V.compor(reg, np.clip(a_bac - a_bin, 0, 1) * 0.75, p["bacia_contorno"])
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        reg = V.compor(reg, V.cob([_disco(cx, cy, p["valvula"])], jan, s, origem), CROMO["contorno"])
        reg = V.compor(reg, V.cob([_disco(cx, cy, p["valvula"] - 0.3)], jan, s, origem), CROMO["meio"])
        tb = q["torneira_bico"]
        a_b = V.cob([_arred(*tb, 0.6)], jan, s, origem)
        tx, ty, tr = q["torneira_base"]
        a_t = np.clip(a_b + V.cob([_disco(tx, ty, tr)], jan, s, origem), 0, 1)
        H2, W2 = a_t.shape
        Ms = np.float32([[1, 0, -0.5 * s], [0, 1, 0.6 * s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(a_t, Ms, (W2, H2)), (0, 0), max(0.5 * s, 0.5)) * (1 - a_t)
        reg = reg * (1 - 0.32 * sb)[..., None]
        reg = V.compor(reg, a_t, CROMO["contorno"])
        reg = V.compor(reg, V.cob([_arred(tb[0] + 0.25, tb[1] + 0.25, tb[2] - 0.25, tb[3] - 0.25, 0.4)], jan, s,
                                  origem), CROMO["escuro"])
        reg = V.compor(reg, V.cob([V.ret(tb[0] + 0.3, tb[1] + 0.3, tb[2] - 0.6, (tb[1] + tb[3]) / 2)], jan, s, origem)
                       * 0.9, CROMO["claro"])
        reg = V.compor(reg, V.cob([_disco(tx, ty, tr - 0.3)], jan, s, origem), CROMO["meio"])
        reg = V.compor(reg, V.cob([_disco(tx + 0.3 * tr, ty - 0.3 * tr, 0.45 * tr)], jan, s, origem) * 0.8,
                       CROMO["claro"])
    for r in q.get("manter", []):                          # as cubas de inox e as torneiras de antes
        k = V.cob([V.ret(*r)], jan, s, origem)[..., None]
        reg = reg * (1 - k) + orig * k
    return C._gravar(img, jan, reg)


def bancadas(img, s, origem, nomes=None):
    for k, q in (("lavabo", LAVABO), ("servico", SERVICO)):
        if nomes is None or k in nomes:
            img = bancada(img, s, origem, q)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os rótulos com o retângulo de fundo
# zona (px da final), deslocamento da fonte do piso, cor das letras ('escura' no deck, 'clara' no marrom)
ROTULOS = {
    "desce_jardim": dict(zona=(876.5, 984.0, 1016.5, 1047.0), d=(0.0, 72.0), letra="escura"),
    "deck": dict(zona=(816.0, 1158.0, 910.0, 1207.0), d=(110.0, 0.0), letra="escura"),
    "area_servico": dict(zona=(2512.0, 360.0, 2650.0, 410.0), d=(0.0, 55.0), letra="clara"),
    "qto_servico": dict(zona=(2512.0, 553.0, 2613.0, 600.0), d=(0.0, -126.0), letra="clara"),
    "quarto_externo": dict(zona=(3051.5, 695.0, 3134.0, 749.0), d=(128.0, 0.0), letra="clara"),
    "garagem": dict(zona=(3027.0, 478.0, 3100.0, 517.0), d=(0.0, 62.0), letra="clara"),
}


def rotulo(img, s, origem, q):
    zx0, zy0, zx1, zy1 = q["zona"]
    jan = V.janela(img, q["zona"], s, origem, folga=int(2 * s) + 2)
    X0, Y0, X1, Y1 = jan
    dx, dy = int(round(q["d"][0] * s)), int(round(q["d"][1] * s))
    F = img[Y0:Y1, X0:X1].astype(np.float32)
    S_ = img[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    L = F.mean(2)
    k = max(int(round(0.45 * s)), 1)
    if q["letra"] == "escura":
        letra = (L < 95).astype(np.uint8)
    else:
        letra = ((L > 175) & (np.abs(F[..., 2] - F[..., 0]) < 40)).astype(np.uint8)
    letra = cv2.dilate(letra, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    fundo = cv2.inpaint(np.clip(F, 0, 255).astype(np.uint8), letra, max(3, 2 * k), cv2.INPAINT_TELEA).astype(np.float32)
    Lf = fundo.mean(2)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    dentro = (X >= zx0) & (X <= zx1) & (Y >= zy0) & (Y <= zy1)
    borda = dentro & (np.minimum.reduce([X - zx0, zx1 - X, Y - zy0, zy1 - Y]) < 2.5) & (letra == 0)
    if borda.sum() > 30:                                       # a luz da fonte casada com a da beira da zona
        S_ = S_ * (np.median(F[borda], axis=0) / np.maximum(np.median(S_[borda], axis=0), 1.0))[None, None, :]
    if q["letra"] == "escura":
        Ltxt = float(np.percentile(L[dentro], 0.5))
    else:
        Ltxt = float(np.percentile(L[dentro], 99.5))
    a = np.clip((L - Lf) / np.where(np.abs(Ltxt - Lf) < 1, 1.0, Ltxt - Lf), 0, 1) * (letra > 0)
    w = np.clip(np.minimum.reduce([X - zx0, zx1 - X, Y - zy0, zy1 - Y]) / 1.5, 0, 1)
    out = F + ((1 - a) * w)[..., None] * (S_ - fundo)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def rotulos(img, s, origem, nomes=None):
    for k, q in ROTULOS.items():
        if nomes is None or k in nomes:
            img = rotulo(img, s, origem, q)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Os itens e o registro local de cada um no 12K (a caixa de cada trecho)
def _f(fn, *args):
    return lambda img, s, origem: fn(img, s, origem, *args)


FUNC, ITENS = {}, {}
for k, r in SOLEIRAS.items():
    FUNC[f"soleira_{k}"] = _f(soleiras, [k])
    ITENS[f"soleira_{k}"] = (r[0] - 30, r[1] - 30, r[2] + 30, r[3] + 30)
FUNC["almoco"] = almoco
ITENS["almoco"] = (2620.0, 650.0, 2780.0, 935.0)
for k, q in JANELAS.items():
    FUNC[f"janela_{k}"] = _f(janelas, [k])
    v = q["vao"]
    ITENS[f"janela_{k}"] = (v[0] - 30, v[1] - 30, v[2] + 30, v[3] + 30)
FUNC["box_bhm1"] = box_bhm1
ITENS["box_bhm1"] = (735.0, 315.0, 910.0, 425.0)
FUNC["topo_porta"] = topo_porta
ITENS["topo_porta"] = (745.0, 545.0, 830.0, 605.0)
FUNC["ilha"] = ilha
ITENS["ilha"] = (2240.0, 350.0, 2340.0, 570.0)
FUNC["pontinhos_cozinha"] = lambda img, s, o: pontinhos(img, s, o, dict(PONTOS, zonas=[PONTOS["zonas"][0]]))
ITENS["pontinhos_cozinha"] = (2195.0, 275.0, 2480.0, 672.0)
FUNC["pontinhos_gourmet"] = lambda img, s, o: pontinhos(img, s, o, dict(PONTOS, zonas=[PONTOS["zonas"][1]]))
ITENS["pontinhos_gourmet"] = (1218.0, 908.0, 1658.0, 1172.0)
FUNC["braco"] = braco
ITENS["braco"] = (1900.0, 1500.0, 2020.0, 1625.0)
FUNC["arco"] = arco
ITENS["arco"] = (2260.0, 1480.0, 2390.0, 1625.0)
FUNC["bancada_lavabo"] = _f(bancadas, ["lavabo"])
ITENS["bancada_lavabo"] = (2330.0, 1010.0, 2440.0, 1205.0)
FUNC["bancada_servico"] = _f(bancadas, ["servico"])
ITENS["bancada_servico"] = (2620.0, 330.0, 2730.0, 505.0)
for k, q in ROTULOS.items():
    FUNC[f"rotulo_{k}"] = _f(rotulos, [k])
    z = q["zona"]
    ITENS[f"rotulo_{k}"] = (z[0] - 30, z[1] - 30, z[2] + 30, z[3] + 30)


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so or any(n.startswith(p + "_") for p in so)]
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in nomes:
            im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            sx, org, cc = DD._registro(base, cinza, DZ, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

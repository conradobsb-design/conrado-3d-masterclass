"""Térreo da Casa B, as correções de 16/11 e 17/11 vendo o 12K (depois das bancadas de Danae, `danae_bancadas_1611.py
B_Terreo`), na final e direto nos 12K A e B, cada peça desenhada na escala de cada imagem:

1. `porta_cozinha` ("APROVEITA E CORRIJA ESSA FALHA NA PORTA DE CORRER DA COZINHA"): a folha de correr da passagem da
   gourmet para a cozinha e os 2 batentes do vão, de novo pelo PDF (o de cima na ponta do toco de parede: "ELE É NA
   PAREDE, NÃO AO LADO"), no padrão das esquadrias da Casa B (o branco com o
   contorno preto fino, `regras_terreo_casab_1311.ESQUADRIAS_TB`); antes, o piso em volta da folha (no 12K, a folha
   virou um tubo de contorno grosso, com um nó na ponta de cima, um ponto claro ao lado e uma mancha laranja embaixo).
2. `cubas_lavatorio` ("CORRIJA A LATERAL DA CUBA DO LAVATÓRIO"): nas 2 cubas esculpidas do lavatório gourmet, o lado
   direito do trecho que passa da bancada era uma coluna clara e neutra (no 12K, uma fresta); ele recebe o lado esquerdo
   em espelho (o fio escuro e o piso de fora), cuba a cuba.
3. `armarios` ("CORRIJA O TOM DOS ARMARIOS DO TERREO DA CASA B, PARA O TOM QUE DEFINIMOS DESDE A CASA A. REMOVENDO
   VEIOS E DEIXANDO A COR SÓLIDA"): os 7 armários de madeira com veio (o aparador do living, o do alto da suíte 3, os
   da suíte master e da sala íntima, os 2 de costas entre as suítes 1 e 2 e o de baixo da suíte 1), nos retângulos do
   PDF, na cor sólida dos armários (`revisao_terreo_casac_1311.COZINHA`: o miolo liso, a face um tom abaixo, a sombra
   curta); o que é cadeira por cima (o couro) fica. Os de closet seguem com os cabides; o louceiro e a despensa já são
   lisos (num tom rosado) e ficam.
4. `portas_servico` ("CORRIJA ESSAS FALHAS AO REDOR DAS PORTAS"): as folhas de giro do BH serviço e do quarto de serviço,
   abertas junto à parede de cima: o traço escuro tracejado que corria embaixo de cada uma (o resto da folha antiga)
   sai, a folha é desenhada de novo na madeira dela, com o contorno fino e a sombra curta; os pontinhos claros do piso
   do quarto junto ao vão saem.
5. `maquinas` ("CORRIJA PISO NO CONTORNO DAS MÁQUINAS DE LAVAR. CORRIJA A ESCALA DAS MÁQUINAS PARA CABER ACIMA DA
   BANCADA"; "NÃO ENCUBRA AS MAQUINAS"): o piso atrás das máquinas (um retângulo mais escuro) vem de um trecho limpo do
   piso da área de serviço, no tom do piso em volta; as 2 máquinas, tiradas da própria imagem, voltam no tamanho do PDF
   (0,60 m), centradas na largura da bancada dos tanques e acima dela, visíveis, com a sombra curta.
6. `cuba_bh_servico` ("SUBSTITUA PELA CUBA DA BIBLIOTECA"): a cuba do BH serviço pela cuba de serviço da biblioteca
   (`POE642_CasaA/biblioteca-objetos/01-subsolo/banho-de-servico/cuba-servico-granito.png`: só a louça e a torneira,
   tiradas do granito da foto), com a torneira para a parede, como no PDF; a cuba antiga sai (o granito da bancada e o
   piso de logo ao lado).

  python3 correcoes_terreo_casab_1611.py final [--saida <png>]
  python3 correcoes_terreo_casab_1611.py doze [--opcao AB] [--saida <jpg com {}>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                          # noqa: E402
from janela_pia_casaa_1611 import alfa_contorno, alfa_ret, compor   # noqa: E402

FINAL = DF.PLANTAS["B_Terreo"]
DOZE = DF.DOZE_K["B_Terreo"]
RAIZ = AQUI.parents[1]

PRETO = (34, 34, 36)                              # o contorno das esquadrias da Casa B (ESQUADRIAS_TB["perfil"])
BRANCO = (236, 236, 234)
PORTA_COZINHA = {"folha": (1550.6, 1449.7, 1553.0, 1524.3),
                 # (17/11, usuário: "ESSE BATENTE FICOU FORA DA PAREDE. ELE É NA PAREDE, NÃO AO LADO") o de cima na
                 # ponta do toco de parede (na largura dele na final, x 1548,75 a 1562,3), não à esquerda dele como no
                 # PDF; o de baixo na ponta da parede de baixo
                 "batentes": [(1548.75, 1400.4, 1562.3, 1401.9), (1538.4, 1473.5, 1551.2, 1475.0)],
                 # o toco reto até o batente (a quina de baixo à esquerda dele tinha um dente marrom), na cor da parede
                 "parede": [(1548.75, 1393.6, 1552.5, 1400.4)], "parede_amostra": (1553.0, 1384.0, 1560.0, 1392.0),
                 # (o retângulo, o deslocamento da fonte do piso)
                 "limpa": [((1550.5, 1444.0, 1559.0, 1530.0), (9.0, 0.0)),
                           ((1538.0, 1442.0, 1550.5, 1473.3), (21.0, 0.0)),
                           # onde ficava o batente de cima (e a tirinha de parede à esquerda do toco) e o borrão claro
                           # sob ele no 12K: o piso de logo abaixo
                           ((1536.0, 1398.6, 1550.2, 1408.0), (0.0, 10.0)),
                           ((1550.2, 1402.0, 1564.0, 1408.0), (0.0, 9.0))]}
# as cubas: (coluna da borda esquerda, coluna da borda direita) do trecho que passa da bancada, as linhas
CUBAS_LAV = {"cubas": [(1278, 1310), (1339, 1370)], "linhas": (1608, 1618), "faixa": 3}
ARMARIOS = {"aparador do living": (1790.7, 1246.8, 1909.5, 1275.5),
            "suíte 3 (alto)": (2442.2, 621.2, 2597.5, 651.1),
            "suíte master": (1204.0, 388.3, 1233.8, 510.6),
            "sala íntima": (1562.3, 349.5, 1592.1, 510.7),
            "suíte 1 (parede da direita)": (2210.1, 362.2, 2239.9, 517.5),
            "suíte 2 (parede da esquerda)": (2248.9, 362.2, 2281.1, 517.5),
            "suíte 1 (embaixo)": (2031.0, 582.4, 2171.3, 612.2)}
PORTAS_SERVICO = {"folhas": {"BH serviço": (1866.8, 1506.4, 1902.6, 1508.8),
                             "quarto de serviço": (2001.1, 1506.4, 2042.9, 1508.8)},
                  "limpa": [((1864.8, 1500.6, 1902.5, 1514.5), (0.0, 15.0)),
                            ((1999.1, 1500.6, 2042.8, 1514.5), (0.0, 15.0)),
                            ((1911.6, 1508.0, 1917.0, 1541.0), (7.0, 0.0))],
                  "madeira": (128, 160, 196), "borda": 0.62, "borda_px": 0.4, "sombra": 0.28}
MAQUINAS = {"area": (2199.0, 1370.0, 2241.7, 1461.6), "fonte": (2104.0, 1372.0, 2183.0, 1428.0),
            "ref": (2187.0, 1380.0, 2198.0, 1450.0), "suave_px": 3.0,
            "novas": [(2201.1, 1376.2, 2236.9, 1412.0), (2201.1, 1417.7, 2236.9, 1453.6)], "sombra": 0.25}
CUBA_BHS = {"png": RAIZ / "POE642_CasaA/biblioteca-objetos/01-subsolo/banho-de-servico/cuba-servico-granito.png",
            "cuba": (1838.2, 1519.9, 1861.9, 1543.7), "apaga": (1835.0, 1516.0, 1866.0, 1548.0),
            "bancada_x1": 1856.0, "dy_granito": 16.0, "dx_piso": 12.0, "sombra": 0.25}


class Mapa:
    """A final levada à imagem: u' = s (u - 1/2) + t + 1/2 (px de borda; s = 1, t = 0: a própria final)."""

    def __init__(self, s=1.0, t=(0.0, 0.0)):
        self.s, self.t = s, t

    def x(self, u):
        return self.s * (u - 0.5) + self.t[0] + 0.5

    def y(self, v):
        return self.s * (v - 0.5) + self.t[1] + 0.5

    def ret(self, r):
        return (self.x(r[0]), self.y(r[1]), self.x(r[2]), self.y(r[3]))

    def reti(self, r):
        return tuple(int(round(v)) for v in self.ret(r))


def copia(out, fonte, mp, r, d):
    """O retângulo r (px da final) recebe a fonte deslocada d (px da final), na escala da imagem."""
    x0, y0, x1, y1 = mp.reti(r)
    dx, dy = int(round(d[0] * mp.s)), int(round(d[1] * mp.s))
    out[y0:y1, x0:x1] = fonte[y0 + dy:y1 + dy, x0 + dx:x1 + dx]


def pintar(out, mp, pecas, folga=6):
    """Pinta [(ret px da final, 'ret'|'contorno', cor, largura px da final)] por cobertura exata, numa caixa só."""
    rs = [mp.ret(p[0]) for p in pecas]
    f = int(np.ceil(folga * mp.s))
    X0, Y0 = int(min(r[0] for r in rs)) - f, int(min(r[1] for r in rs)) - f
    X1, Y1 = int(max(r[2] for r in rs)) + f, int(max(r[3] for r in rs)) + f
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    for (r, tipo, cor, larg), rm in zip(pecas, rs):
        loc = (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)
        a = alfa_ret(loc, forma) if tipo == "ret" else alfa_contorno(loc, larg * mp.s, forma)
        reg = compor(reg, a, cor)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def sombra(out, mp, r, forca, dx=0.8, dy=1.0, sigma=0.9, fora=True):
    """A sombra curta do retângulo r (px da final) no que está em volta."""
    rm = mp.ret(r)
    f = int(np.ceil(6 * mp.s))
    X0, Y0, X1, Y1 = int(rm[0]) - f, int(rm[1]) - f, int(rm[2]) + f, int(rm[3]) + f
    forma = (Y1 - Y0, X1 - X0)
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    M = np.float32([[1, 0, dx * mp.s], [0, 1, dy * mp.s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), sigma * mp.s)
    if fora:
        sb *= (1 - a)
    reg = out[Y0:Y1, X0:X1].astype(np.float32) * (1 - forca * sb)[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def porta_cozinha(out, mp, q=PORTA_COZINHA):
    fonte = out.copy()
    for r, d in q["limpa"]:
        copia(out, fonte, mp, r, d)
    x0, y0, x1, y1 = mp.reti(q["parede_amostra"])
    cor = tuple(float(v) for v in np.median(fonte[y0:y1, x0:x1].reshape(-1, 3), axis=0))
    pecas = [(r, "ret", cor, 0) for r in q["parede"]]
    for r in [q["folha"]] + q["batentes"]:
        pecas += [(r, "ret", BRANCO, 0), (r, "contorno", PRETO, 0.5)]
    pintar(out, mp, pecas)
    print("    porta de correr da cozinha: a folha e os 2 batentes do PDF, no branco com o contorno preto fino")


def cubas_lavatorio(out, mp, q=CUBAS_LAV):
    y0, y1 = q["linhas"]
    for esq, dir_ in q["cubas"]:
        eixo = (esq + dir_ + 1) / 2                       # o meio do trecho (px de borda)
        u0, u1 = esq - (q["faixa"] - 1), esq + 1          # as colunas do lado esquerdo (o fio e o piso de fora)
        U0, U1 = int(round(mp.x(u0))), int(round(mp.x(u1)))
        V0, V1 = int(round(mp.y(y0))), int(round(mp.y(y1)))
        A = mp.x(eixo)
        D0 = int(round(2 * A - U1))
        out[V0:V1, D0:D0 + (U1 - U0)] = out[V0:V1, U0:U1][:, ::-1]
    print(f"    lavatório gourmet: o lado direito das {len(q['cubas'])} cubas com o fio do lado esquerdo, em espelho")


def armarios(out, mp, q=ARMARIOS):
    import revisao_terreo_casac_1311 as RC
    c = RC.COZINHA
    for nome, r in q.items():
        rm = mp.ret(r)
        f = int(np.ceil(6 * mp.s))
        X0, Y0, X1, Y1 = int(rm[0]) - f, int(rm[1]) - f, int(rm[2]) + f, int(rm[3]) + f
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        forma = reg.shape[:2]
        loc = (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)
        a = alfa_ret(loc, forma)
        e = mp.s
        miolo = alfa_ret((loc[0] + e, loc[1] + e, loc[2] - e, loc[3] - e), forma)
        # o couro das cadeiras por cima fica
        im = reg
        couro = ((im[..., 2] - im[..., 0]) > 85) & (im[..., 2] > 110)
        couro = cv2.dilate(couro.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        a = a * ~couro
        miolo = miolo * ~couro
        M = np.float32([[1, 0, -1.0 * mp.s], [0, 1, 1.3 * mp.s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), 1.1 * mp.s) * (1 - a)
        reg = reg * (1 - c["sombra"] * sb)[..., None]
        cor = np.float32(c["cor_armario"])
        reg = compor(reg, a - miolo, cor * c["face"])
        reg = compor(reg, miolo, cor)
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    armários na cor sólida das casas (sem o veio): {', '.join(q)}")


def portas_servico(out, mp, q=PORTAS_SERVICO):
    fonte = out.copy()
    for r, d in q["limpa"]:
        copia(out, fonte, mp, r, d)
    for nome, r in q["folhas"].items():
        sombra(out, mp, r, q["sombra"], dx=0.0, dy=0.9, sigma=0.6)
        borda = tuple(v * q["borda"] for v in q["madeira"])
        pintar(out, mp, [(r, "ret", q["madeira"], 0), (r, "contorno", borda, q["borda_px"])])
    print(f"    portas de giro do serviço: o traço velho sob as folhas e os pontinhos do piso saem; as folhas de novo "
          f"({', '.join(q['folhas'])})")


def _piso_tecido(fonte, mp, r_fonte, h, w):
    """Um trecho h x w de piso a partir do retângulo limpo `r_fonte` (px da final): a fonte e o espelho dela, em pé e
    deitada, até cobrir."""
    x0, y0, x1, y1 = mp.reti(r_fonte)
    P = fonte[y0:y1, x0:x1].astype(np.float32)
    lin = np.concatenate([P, P[::-1]], axis=0)
    while lin.shape[0] < h:
        lin = np.concatenate([lin, lin], axis=0)
    col = np.concatenate([lin, lin[:, ::-1]], axis=1)
    while col.shape[1] < w:
        col = np.concatenate([col, col], axis=1)
    return col[:h, :w]


def maquinas(out, mp, q=MAQUINAS):
    fonte = out.copy()
    X0, Y0, X1, Y1 = mp.reti(q["area"])
    reg = fonte[Y0:Y1, X0:X1].astype(np.float32)
    # as máquinas de hoje: o branco esmaltado e o aro cinza (neutros e claros), em componentes grandes
    lum = reg.mean(axis=2)
    sat = reg.max(axis=2) - reg.min(axis=2)
    m = (lum > 150) & (sat < 35)
    m = ndimage.binary_fill_holes(cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)))
    lab, n = ndimage.label(m)
    sprites = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        mm = lab[sl] == i + 1
        if mm.sum() < 300 * mp.s * mp.s:
            continue
        sprites.append((sl[0].start, reg[sl].copy(), mm.astype(np.float32)))
    sprites.sort(key=lambda t: t[0])
    if len(sprites) != len(q["novas"]):
        raise SystemExit(f"máquinas: achei {len(sprites)}, esperava {len(q['novas'])}")
    # o piso: um trecho limpo da área de serviço, no tom do piso logo à esquerda, com a emenda macia
    h, w = Y1 - Y0, X1 - X0
    T = _piso_tecido(fonte, mp, q["fonte"], h, w)
    # a luz linha a linha da faixa de piso logo à esquerda (suavizada), para não ficar emenda
    rx0, _, rx1, _ = mp.reti(q["ref"])
    ref = cv2.GaussianBlur(fonte[Y0:Y1, rx0:rx1].astype(np.float32).mean(axis=1, keepdims=True), (0, 0), 6 * mp.s)
    tm = cv2.GaussianBlur(T.mean(axis=1, keepdims=True), (0, 0), 6 * mp.s)
    T += (ref - tm)
    rampa = np.clip(np.arange(w, dtype=np.float32) / max(q["suave_px"] * mp.s, 1.0), 0, 1)[None, :, None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - rampa) + T * rampa), 0, 255).astype(np.uint8)
    # as máquinas no tamanho do PDF, acima da bancada
    for (_, S, mm), r in zip(sprites, q["novas"]):
        sombra(out, mp, r, q["sombra"])
        rm = mp.ret(r)
        bx0, by0 = int(np.floor(rm[0])), int(np.floor(rm[1]))
        bw, bh = int(round(rm[2] - rm[0])), int(round(rm[3] - rm[1]))
        Sz = cv2.resize(S, (bw, bh), interpolation=cv2.INTER_AREA)
        az = cv2.resize(cv2.GaussianBlur(mm, (0, 0), 0.6), (bw, bh), interpolation=cv2.INTER_AREA)[..., None]
        dst = out[by0:by0 + bh, bx0:bx0 + bw].astype(np.float32)
        out[by0:by0 + bh, bx0:bx0 + bw] = np.clip(np.round(dst * (1 - az) + Sz * az), 0, 255).astype(np.uint8)
    print("    máquinas de lavar: o piso de trás sem o retângulo escuro; as 2 no tamanho do PDF (0,60 m), acima da "
          "bancada dos tanques, visíveis")


_CUBA = {}


def _cuba_bib(q=CUBA_BHS):
    """A louça e a torneira da cuba de serviço da biblioteca (sem o granito da foto), giradas com a torneira para a
    esquerda: (rgb, alfa, a caixa da louça dentro da imagem)."""
    if "P" not in _CUBA:
        P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
        rgb, al = P[..., :3], P[..., 3] / 255
        lum = rgb.mean(axis=2)
        sat = rgb.max(axis=2) - rgb.min(axis=2)
        m = (lum > 140) & (sat < 40) & (al > 0.5)
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = ndimage.binary_fill_holes(m)
        lab, n = ndimage.label(m)
        tam = ndimage.sum(m, lab, range(1, n + 1))
        louca = lab == (int(np.argmax(tam)) + 1)
        ys, xs = np.nonzero(louca)
        lx0, ly0, lx1, ly1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        # a torneira: os componentes claros e neutros logo acima da louça, dentro da largura dela
        tor = np.zeros(m.shape, bool)
        alto = 0.45 * (ly1 - ly0)
        for i, sl in enumerate(ndimage.find_objects(lab)):
            if i + 1 == int(np.argmax(tam)) + 1:
                continue
            if sl[1].start >= lx0 and sl[1].stop <= lx1 and sl[0].stop >= ly0 - alto and sl[0].start < ly0:
                tor[sl] |= lab[sl] == i + 1
        mm = (louca | tor).astype(np.float32)
        ys, xs = np.nonzero(mm)
        X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        rgb, mm = rgb[Y0:Y1, X0:X1], mm[Y0:Y1, X0:X1]
        caixa = (lx0 - X0, ly0 - Y0, lx1 - X0, ly1 - Y0)
        # girada 90° no sentido anti-horário: a torneira (em cima) vai para a esquerda
        rgb, mm = np.rot90(rgb).copy(), np.rot90(mm).copy()
        h0 = Y1 - Y0
        caixa = (caixa[1], (X1 - X0) - caixa[2], caixa[3], (X1 - X0) - caixa[0])
        _CUBA["P"] = (rgb, mm, caixa, h0)
    return _CUBA["P"]


def cuba_bh_servico(out, mp, q=CUBA_BHS):
    fonte = out.copy()
    ax0, ay0, ax1, ay1 = q["apaga"]
    bx = q["bancada_x1"]
    meio = (ay0 + ay1) / 2
    # a cuba antiga sai: o granito da bancada (de cima e de baixo) e o piso de logo ao lado
    copia(out, fonte, mp, (ax0, ay0, bx, meio), (0.0, -q["dy_granito"]))
    copia(out, fonte, mp, (ax0, meio, bx, ay1), (0.0, q["dy_granito"]))
    copia(out, fonte, mp, (bx, ay0, ax1, ay1), (q["dx_piso"], 0.0))
    # a cuba da biblioteca: a louça no retângulo do PDF (o lado comprido), a torneira para a parede
    rgb, mm, (lx0, ly0, lx1, ly1), _ = _cuba_bib(q)
    cx0, cy0, cx1, cy1 = mp.ret(q["cuba"])
    k = (cy1 - cy0) / (ly1 - ly0)                       # a louça na altura do retângulo do PDF
    W, H = int(round(rgb.shape[1] * k)), int(round(rgb.shape[0] * k))
    # a louça encostada à direita do retângulo do PDF, no meio dele na altura
    X0 = int(round(cx1 - lx1 * k))
    Y0 = int(round((cy0 + cy1) / 2 - (ly0 + ly1) / 2 * k))
    S = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_AREA)
    a = cv2.resize(mm, (W, H), interpolation=cv2.INTER_AREA)
    # a sombra curta da louça
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, 0.8 * mp.s], [0, 1, 1.0 * mp.s]]), (W, H)), (0, 0),
                          0.9 * mp.s) * (1 - a)
    dst = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    dst = dst * (1 - q["sombra"] * sb)[..., None]
    dst = dst * (1 - a[..., None]) + S * a[..., None]
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(dst), 0, 255).astype(np.uint8)
    print("    BH serviço: a cuba de serviço da biblioteca (a louça e a torneira), a torneira para a parede")


PASSOS = (porta_cozinha, cubas_lavatorio, armarios, portas_servico, maquinas, cuba_bh_servico)


def aplicar(img, mp):
    out = img.copy()
    for f in PASSOS:
        f(out, mp)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    final = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(final, Mapa()))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        doze = cv2.imread(str(f))
        M = DF.afim_12k(final, doze)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        out = aplicar(doze, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

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

7. `louceiro_despensa` ("SIM, PASSE O LOUCEIRO E A DESPENSA PARA O TOM PADRÃO"): os armários em L do louceiro e da
   despensa (os polígonos da ARQ_LAYOUT HUMANIZAÇÃO), do rosado na cor sólida dos armários, como os outros (o que
   foge do rosado por cima fica).
8. `porta_adega` ("CORRIJA ESSE RESIDUO DE PISO ANTIGO ABAIXO DA PORTA"): a folha de giro da área de serviço, aberta
   junto à parede de baixo da adega, como as do serviço (o traço velho tracejado embaixo sai, a folha de novo).
9. `gourmet_altura` ("SE NÃO TEM FALHA, SÓ DÊ A IDEIA DE QUE A BANCADA ESTÁ MAIS ALTA DO QUE O PISO"): na frente da
   bancada de trás da gourmet (a da cuba e da grelha), o fio escuro da quina, um brilho de 1 px na beira do tampo e a
   sombra curta no piso à frente.
10. `lavabo_bancada` ("CORRIJA A BANCADA NO TOM DA CUBA"): no lavabo, a peça de bancada abaixo da cuba esculpida (mais
   clara, com pontinhos e riscos) no tom da cuba: a luz suave dela, sem os pontinhos e riscos, no tom mediano da
   pedra da cuba (a regra da Casa A), com o grão fino dessa pedra.

11. `pia_sala_intima` ("PRECISAMOS MELHORAR A REPRESENTAÇÃO DESSA BANCADA E PIA, SEM LINHA TÉCNICA. AQUI É PLANTA
   HUMANIZADAS"): a bancada estreita do bar da sala íntima sem o retângulo de linha técnica (a pedra limpa do alto
   dela, em espelho, de ponta a ponta) e a cuba redonda chapada pela cuba redonda da biblioteca
   (`03-primeiro-pavimento/banho-master/cuba-entrada.png`, só a louça e a torneira), no círculo do PDF, a torneira para
   a parede.
12. `banco_deck` ("REMOVA ESSE TRAÇO BRANCO NA PARTE DE BAIXO DO BANCO"): a linha clara sob o banco do pé do deck (a
   linha 1710, x 615 a 897) vira a grama de logo abaixo.

13. `armario_quarto_servico` ("ESSE ARMARIO DO QUARTO DE SERVIÇO NÃO É COM CABIDES?", e depois "NÃO É DE CABIDES
   MESMO"): o armário do quarto de serviço (o retângulo da ARQ_LAYOUT HUMANIZAÇÃO, 0,90 x 0,50 m, junto à parede da
   esquerda), que era um bloco cinza, liso na cor sólida dos armários, como os outros (`armarios`).

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


LOUCEIRO_DESPENSA = {"louceiro": [(1830.9, 1490.0), (1830.9, 1370.5), (1860.8, 1370.5), (1860.8, 1466.1),
                                  (1933.9, 1466.1), (1933.9, 1490.0)],
                     "despensa": [(1939.9, 1490.0), (1939.9, 1466.1), (2019.0, 1466.1), (2019.0, 1370.5),
                                  (2042.9, 1370.5), (2042.9, 1490.0)],
                     "outro": 40.0}
PORTA_ADEGA = dict(PORTAS_SERVICO, folhas={"área de serviço (junto à adega)": (2126.5, 1297.4, 2180.2, 1299.8)},
                   limpa=[((2124.5, 1290.6, 2180.1, 1306.5), (0.0, 16.0))])
GOURMET_ALTURA = {"frente": (1296.5, 1486.0, 1538.4), "sombra_px": 4.5, "sombra": 0.30, "fio_px": 0.6, "fio": 0.62,
                  "brilho_px": 1.2, "brilho": 1.07}
LAVABO_BANCADA = {"peca": (2251.9, 853.7, 2270.4, 898.8), "ref": (2253.8, 799.0, 2258.6, 818.0), "borda_px": 1.0}

PIA_SALA_INTIMA = {"interior": (1563.5, 586.5, 1594.5, 727.5), "fonte": (1563.5, 588.0, 1594.5, 652.0),
                   "cuba": (1567.8, 662.5, 1588.1, 682.8),
                   "png": RAIZ / "POE642_CasaA/biblioteca-objetos/03-primeiro-pavimento/banho-master/cuba-entrada.png",
                   "sat_max": 18, "lum_min": 110, "sombra": 0.25}
BANCO_DECK = {"traco": (615.0, 1709.6, 897.0, 1711.0), "dy": 3.0}
ARMARIO_QS = {"ret": (1911.5, 1552.5, 1941.6, 1606.2)}


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


def armarios(out, mp, q=ARMARIOS, couro=True):
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
        if couro:
            pele = ((im[..., 2] - im[..., 0]) > 85) & (im[..., 2] > 110)
            pele = cv2.dilate(pele.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
            a = a * ~pele
            miolo = miolo * ~pele
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


def _alfa_poli(pts, forma, encolhe=0.0, ss=8):
    """A cobertura do polígono (px da imagem) e a do miolo (o polígono encolhido `encolhe` px)."""
    hi = np.zeros((forma[0] * ss, forma[1] * ss), np.uint8)
    cv2.fillPoly(hi, [np.int32(np.round(np.float64(pts) * ss))], 255)
    a = cv2.resize(hi.astype(np.float32) / 255, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
    k = int(round(encolhe * ss))
    if k > 0:
        hi = cv2.erode(hi, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
    m = cv2.resize(hi.astype(np.float32) / 255, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
    return a, m


def louceiro_despensa(out, mp, q=LOUCEIRO_DESPENSA):
    import revisao_terreo_casac_1311 as RC
    c = RC.COZINHA
    for nome in ("louceiro", "despensa"):
        pts = [(mp.x(x), mp.y(y)) for x, y in q[nome]]
        f = int(np.ceil(6 * mp.s))
        X0, Y0 = int(min(p[0] for p in pts)) - f, int(min(p[1] for p in pts)) - f
        X1, Y1 = int(max(p[0] for p in pts)) + f, int(max(p[1] for p in pts)) + f
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        forma = reg.shape[:2]
        a, miolo = _alfa_poli([(x - X0, y - Y0) for x, y in pts], forma, encolhe=mp.s)
        # o que foge do rosado por cima (as folhas, os textos) fica
        rosa = np.median(reg[miolo > 0.99], axis=0)
        outro = np.linalg.norm(reg - rosa, axis=2) > q["outro"]
        outro = cv2.dilate(outro.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        a, miolo = a * ~outro, miolo * ~outro
        M = np.float32([[1, 0, -1.0 * mp.s], [0, 1, 1.3 * mp.s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), 1.1 * mp.s) * (1 - a)
        reg = reg * (1 - c["sombra"] * sb)[..., None]
        cor = np.float32(c["cor_armario"])
        reg = compor(reg, a - miolo, cor * c["face"])
        reg = compor(reg, miolo, cor)
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    louceiro e despensa: os armários em L do rosado na cor sólida dos armários")


def porta_adega(out, mp, q=PORTA_ADEGA):
    portas_servico(out, mp, q)


def gourmet_altura(out, mp, q=GOURMET_ALTURA):
    x0, yf, x1 = q["frente"]
    L = q["sombra_px"]
    X0, X1 = int(np.floor(mp.x(x0))), int(np.ceil(mp.x(x1)))
    Y0, Y1 = int(np.floor(mp.y(yf - L))) - 1, int(np.ceil(mp.y(yf + q["brilho_px"]))) + 2
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    cx = alfa_ret((mp.x(x0) - X0, 0, mp.x(x1) - X0, forma[0]), forma)
    # a sombra no piso à frente: mais forte junto à quina
    v = np.arange(forma[0], dtype=np.float32) + 0.5 + Y0
    d = np.clip((mp.y(yf) - v) / (L * mp.s), 0, 1)
    w = np.where(v < mp.y(yf), (1 - d) ** 2, 0.0)[:, None] * cx
    reg = reg * (1 - q["sombra"] * w)[..., None]
    # o brilho na beira do tampo e o fio escuro da quina
    br = alfa_ret((mp.x(x0) - X0, mp.y(yf) - Y0, mp.x(x1) - X0, mp.y(yf + q["brilho_px"]) - Y0), forma)
    reg = reg * (1 + (q["brilho"] - 1) * br)[..., None]
    e = q["fio_px"] / 2
    fi = alfa_ret((mp.x(x0) - X0, mp.y(yf - e) - Y0, mp.x(x1) - X0, mp.y(yf + e) - Y0), forma)
    reg = reg * (1 - (1 - q["fio"]) * fi)[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    gourmet: a bancada de trás mais alta que o piso (o fio da quina, o brilho do tampo, a sombra no piso)")


def lavabo_bancada(out, mp, q=LAVABO_BANCADA):
    """A peça no tom da cuba: a luz suave dela (a mediana e o desfoque só por dentro, sem os pontinhos e riscos) levada ao
    tom mediano da pedra da cuba (`ref`, a faixa ao lado da cuba, sem a torneira), com o grão fino dessa faixa; o
    contorno da peça fica."""
    b = q["borda_px"]
    x0, y0, x1, y1 = q["peca"]
    rm = mp.ret((x0 + b, y0 + b, x1 - b, y1 - b))
    X0, Y0, X1, Y1 = int(np.floor(rm[0])) - 2, int(np.floor(rm[1])) - 2, int(np.ceil(rm[2])) + 2, int(np.ceil(rm[3])) + 2
    sub = out[Y0:Y1, X0:X1].copy()
    reg = sub.astype(np.float32)
    forma = reg.shape[:2]
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    dentro = (a > 0.5).astype(np.float32)
    k = max(5, int(round(5 * mp.s)) | 1)
    med = cv2.medianBlur(sub, k).astype(np.float32)
    sg = 3.0 * mp.s
    luz = cv2.GaussianBlur(med * dentro[..., None], (0, 0), sg) / np.maximum(cv2.GaussianBlur(dentro, (0, 0), sg), 1e-3)[..., None]
    rx0, ry0, rx1, ry1 = mp.reti(q["ref"])
    F = out[ry0:ry1, rx0:rx1].astype(np.float32)
    ref = np.median(F.reshape(-1, 3), axis=0)
    luz *= ref / np.maximum(np.median(luz[dentro > 0], axis=0), 1)
    grao = F - cv2.GaussianBlur(F, (0, 0), 1.5 * mp.s)
    while grao.shape[0] < forma[0]:
        grao = np.concatenate([grao, grao[::-1]], axis=0)
    while grao.shape[1] < forma[1]:
        grao = np.concatenate([grao, grao[:, ::-1]], axis=1)
    T = luz + 0.8 * grao[:forma[0], :forma[1]]
    reg = reg * (1 - a[..., None]) + T * a[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    lavabo: a bancada abaixo da cuba no tom da cuba, sem os pontinhos e riscos")


def _cuba_redonda(q=PIA_SALA_INTIMA):
    """A louça e a torneira da cuba redonda da biblioteca (sem a pedra da foto), giradas com a torneira para a esquerda:
    (rgb, alfa, a caixa da louça)."""
    if "R" not in _CUBA:
        P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
        rgb, al = P[..., :3], P[..., 3] / 255
        lum = rgb.mean(axis=2)
        sat = rgb.max(axis=2) - rgb.min(axis=2)
        m = (lum > q["lum_min"]) & (sat < q["sat_max"]) & (al > 0.5)
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = ndimage.binary_fill_holes(m)
        lab, n = ndimage.label(m)
        tam = ndimage.sum(m, lab, range(1, n + 1))
        i_l = int(np.argmax(tam)) + 1
        louca = lab == i_l
        ys, xs = np.nonzero(louca)
        lx0, ly0, lx1, ly1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        mm = louca.copy()
        alto = 0.45 * (ly1 - ly0)
        for i, sl in enumerate(ndimage.find_objects(lab)):
            if i + 1 == i_l:
                continue
            if sl[1].start >= lx0 and sl[1].stop <= lx1 and sl[0].stop >= ly0 - alto and sl[0].start < ly0 + 0.2 * (ly1 - ly0):
                mm[sl] |= lab[sl] == i + 1
        mm = mm.astype(np.float32)
        ys, xs = np.nonzero(mm)
        X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        rgb, mm = rgb[Y0:Y1, X0:X1], mm[Y0:Y1, X0:X1]
        caixa = (lx0 - X0, ly0 - Y0, lx1 - X0, ly1 - Y0)
        rgb, mm = np.rot90(rgb).copy(), np.rot90(mm).copy()
        W0 = X1 - X0
        caixa = (caixa[1], W0 - caixa[2], caixa[3], W0 - caixa[0])
        _CUBA["R"] = (rgb, mm, caixa)
    return _CUBA["R"]


def pia_sala_intima(out, mp, q=PIA_SALA_INTIMA):
    fonte = out.copy()
    # a bancada limpa: a pedra do alto dela (sem a linha técnica), em espelho, de ponta a ponta
    X0, Y0, X1, Y1 = mp.reti(q["interior"])
    fx0, fy0, fx1, fy1 = mp.reti(q["fonte"])
    F = fonte[fy0:fy1, fx0:fx1].astype(np.float32)
    lin = F
    while lin.shape[0] < Y1 - Y0:
        lin = np.concatenate([lin, lin[::-1]], axis=0)
    T = cv2.resize(lin[:Y1 - Y0], (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA) if lin.shape[1] != X1 - X0 \
        else lin[:Y1 - Y0]
    out[Y0:Y1, X0:X1] = np.clip(np.round(T), 0, 255).astype(np.uint8)
    # a cuba redonda da biblioteca no círculo do PDF, a torneira para a parede (à esquerda)
    rgb, mm, (lx0, ly0, lx1, ly1) = _cuba_redonda(q)
    cx0, cy0, cx1, cy1 = mp.ret(q["cuba"])
    k = ((cx1 - cx0) + (cy1 - cy0)) / ((lx1 - lx0) + (ly1 - ly0))
    W, H = int(round(rgb.shape[1] * k)), int(round(rgb.shape[0] * k))
    BX = int(round((cx0 + cx1) / 2 - (lx0 + lx1) / 2 * k))
    BY = int(round((cy0 + cy1) / 2 - (ly0 + ly1) / 2 * k))
    S = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_AREA)
    a = cv2.resize(mm, (W, H), interpolation=cv2.INTER_AREA)
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, 0.8 * mp.s], [0, 1, 1.0 * mp.s]]), (W, H)), (0, 0),
                          0.9 * mp.s) * (1 - a)
    dst = out[BY:BY + H, BX:BX + W].astype(np.float32)
    dst = dst * (1 - q["sombra"] * sb)[..., None]
    dst = dst * (1 - a[..., None]) + S * a[..., None]
    out[BY:BY + H, BX:BX + W] = np.clip(np.round(dst), 0, 255).astype(np.uint8)
    print("    sala íntima: a bancada do bar sem a linha técnica e a cuba redonda da biblioteca (louça e torneira)")


def banco_deck(out, mp, q=BANCO_DECK):
    fonte = out.copy()
    copia(out, fonte, mp, q["traco"], (0.0, q["dy"]))
    print("    deck: o traço claro sob o banco vira grama")


def armario_quarto_servico(out, mp, q=ARMARIO_QS):
    armarios(out, mp, {"quarto de serviço": q["ret"]}, couro=False)


PASSOS = (porta_cozinha, cubas_lavatorio, armarios, portas_servico, maquinas, cuba_bh_servico,
          louceiro_despensa, porta_adega, gourmet_altura, lavabo_bancada, pia_sala_intima, banco_deck,
          armario_quarto_servico)
NOVOS_1711C = (pia_sala_intima, banco_deck, armario_quarto_servico)
NOVOS_1711 = (louceiro_despensa, porta_adega, gourmet_altura, lavabo_bancada)


def aplicar(img, mp, passos=PASSOS):
    out = img.copy()
    for f in passos:
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

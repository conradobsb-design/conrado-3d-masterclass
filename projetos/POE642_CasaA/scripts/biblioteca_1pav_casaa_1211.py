"""As peças da biblioteca do usuário no 1º Pavimento da Casa A (12/11).

Usuário: "Vamos revisar os mobiliários do 1° pavimento da casa A"; a proposta (a planta de hoje ao lado das peças,
`renders/POE642_CasaA_PH_1Pavimento_1211_proposta_biblioteca_{1,2,3}.jpg`) aprovada com "OK, pode aplicar as
recomendadas". Nas três perguntas abertas, o que a proposta recomendava: as camas da biblioteca (A, creme) no lugar
das de manta bordô; os vasos sanitários brancos (a bacia Carrara); os closets como estão (os cabides).

Como no Térreo (`biblioteca_terreo_casaa_1211`, de onde vêm `pousar`, `preparar`, as sombras e a ampliação no 12K): a
peça da biblioteca entra no retângulo da peça do PDF (o centro, o tamanho e o giro dele), sem mudar a composição; a
pegada da antiga, com a sombra, volta ao piso do lugar antes (`PT.piso_refeito`, o tecido de fontes achadas no mesmo
piso do ambiente, `fontes_auto`: o vinílico, o travertino ou o tapete que fica, cada parte com o seu); o que fica (as
cadeiras de madeira e linho, o laptop, os bancos aos pés das camas, a mesa de centro de nogueira) não muda ou volta
recortado por cima (`recolar`). A biblioteca: `biblioteca-objetos/03-primeiro-pavimento` (no git, só as peças usadas).

Os desvios da proposta (do PDF): os criados da suíte 2 são retangulares no PDF (o retangular da biblioteca, não o
redondo); a banheira é a oval sem metal com o misturador de piso no lugar do PDF (a "render" traz o metal no meio do
lado comprido); o sofá em L da biblioteca espelhado (`anti_t`) para o L do PDF (o lado longo junto à parede da direita).

  python3 biblioteca_1pav_casaa_1211.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final, o registro do 12K e os antes e
depois `renders/POE642_CasaA_PH_1Pavimento_1211b_<ambiente>_antes_depois.jpg`.
"""

import argparse
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import biblioteca_terreo_casaa_1211 as BT       # noqa: E402

R = AQUI.parent / "renders"
RAIZ_GIT = AQUI.parent.parent.parent
FINAL = R / "POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png"
BIB = AQUI.parent / "biblioteca-objetos" / "03-primeiro-pavimento"
ANTES_COMMIT = "127eabc"
REG_JSON = R / "POE642_CasaA_PH_1Pavimento_12K_biblioteca.json"
REG_MASC = R / "POE642_CasaA_PH_1Pavimento_12K_biblioteca_zona.png"
PX_M = 59.70590031258779
SOMBRAS = BT.SOMBRAS
girar_pt = BT.girar_pt

# os tapetes que ficam (as camas e os criados das suítes 1, 2 e 3 em cima deles): a parte da pegada dentro deles volta
# ao tapete, não ao piso
TAPETES_FICAM = [(1637, 388, 1846, 525), (1662, 1045, 1871, 1164), (2284, 1398, 2493, 1529)]

# Cada peça: (png, cx, cy, larg, alt, giro, sombra, extra) em px da final (larg x alt antes do giro; alt None: a
# proporção do PNG); extra: None, "lavabo" (os lados esticados), "anti_t" (o PNG espelhado na antidiagonal), ou
# ("cuba", c) (a cuba esculpida na bancada: os lados esticados e o miolo a c do começo do comprimento).
# zonas: os retângulos (px) da pegada das antigas, já com a folga da sombra; manter: o que não é refeito.
AMBIENTES = {
    "sala_intima": {
        "zonas": [(2030, 960, 2162, 1236), (2050, 944, 2181, 1165), (1989, 888, 2054, 953)],
        "manter": [],
        "pecas": [
            ("sala-intima/tapete", 2096.0, 1099.0, 262.0, 120.0, 90.0, "tapete", None),
            ("sala-intima/sofa-l-a", 2115.5, 1054.5, 119.0, 209.0, 0.0, "movel", "anti_t"),
            # (12/11, usuário: "Tem mesa redonda sobre o sofá, em vez de estar ao redor") o sofá da biblioteca é mais
            # fundo que o do PDF (a chaise até y 1022, o braço desde x 2111): as mesas laterais do PDF caíam sobre ele;
            # vão ao lado: à esquerda da chaise, no tapete, e por fora do braço, junto à ponta da mesa de centro
            ("sala-intima/mesa-lateral", 2044.0, 992.0, 18.0, None, 0.0, "baixa", None),
            ("sala-intima/mesa-lateral", 2100.0, 1140.0, 18.0, None, 0.0, "baixa", None),
            ("sala-intima/mesa-lateral", 2140.5, 1188.5, 27.0, None, 0.0, "baixa", None),
            # (12/11, "Revisão de poltronas e rotação necessária") a frente na normal da borda reta do assento do
            # PDF (2064,5;1183,6)-(2097,6;1164,5), para a mesa de centro: -150° (antes, para cima e à direita)
            ("sala-intima/poltrona-a", 2089.0, 1192.5, 54.0, 56.0, -150.0, "movel", None),
            ("sala-intima/vaso-folhagem-a", 2021.5, 920.5, 54.0, None, 0.0, "movel", None)],
        # a mesa de centro de nogueira (a da final) volta por cima do tapete novo
        "recolar": [((2054, 1042, 2095, 1121), "movel")]},
    "suite_master": {
        "zonas": [(1395, 1263, 1616, 1419), (1438, 1317, 1574, 1460), (1390, 1421, 1622, 1457),
                  (1615, 1338, 1705, 1427)],
        "manter": [(1617, 1382, 1644, 1419)],               # as duas mesinhas redondas ficam
        "pecas": [
            ("suite-master/tapete", 1505.5, 1341.0, 209.0, 143.3, 0.0, "tapete", None),
            ("suite-master/cama-king-a", 1506.0, 1388.5, 124.2, 130.8, 180.0, "movel", None),
            # (12/11, "GERE UM BANCO NOVO NO HIGGSFIELD") o banco aos pés da cama, gerado para a biblioteca
            ("suite-master/banco-pe-de-cama", 1506.0, 1308.0, 95.5, 23.9, 0.0, "movel", None),
            ("suite-master/criado-retangular-vista-superior", 1417.0, 1439.0, 41.8, 23.9, 0.0, "movel", "tom_bancada"),
            ("suite-master/criado-retangular-vista-superior", 1595.0, 1439.0, 41.8, 23.9, 0.0, "movel", "tom_bancada"),
            # (12/11, revisão das poltronas) a frente para o pufe, na normal da borda reta do assento do PDF
            # (1640,7;1381,8)-(1674,3;1362,4): -150° (antes, para baixo e à esquerda, com o encosto para o pufe)
            ("suite-master/poltrona", 1671.0, 1394.0, 54.0, 56.0, -150.0, "movel", None),
            ("suite-master/pufe", 1653.0, 1363.0, 42.0, 22.0, 35.0, "baixa", None)],
        "abajures": [(1417.0, 1439.0, 19.0), (1595.0, 1439.0, 19.0)],
        "recolar": []},
    "suite_1": {
        "zonas": [(2304, 1447, 2372, 1574), (2409, 1447, 2477, 1574), (2269, 1541, 2512, 1573),
                  (2359, 1329, 2517, 1372), (2297, 1424, 2374, 1453), (2402, 1424, 2479, 1453)],
        "manter": [(2456, 1369, 2498, 1395)],               # a cadeira de madeira e linho (fora da mesa)
        "pecas": [
            ("suite-1/bancada-suites", 2438.0, 1350.5, 149.3, 35.8, 0.0, "mesa", None),
            ("suite-1/cama-solteiro-a", 2338.0, 1510.5, 59.7, 119.4, 180.0, "movel", None),
            ("suite-1/cama-solteiro-a", 2443.0, 1510.5, 59.7, 119.4, 180.0, "movel", None),
            ("suite-1/banco-pe-de-cama-solteiro", 2338.0, 1439.0, 53.7, 17.9, 0.0, "movel", None),
            ("suite-1/banco-pe-de-cama-solteiro", 2443.0, 1439.0, 53.7, 17.9, 0.0, "movel", None),
            ("suite-1/criado-retangular-vista-superior", 2289.0, 1557.0, 32.8, 23.9, 0.0, "movel", "tom_bancada"),
            ("suite-1/criado-retangular-vista-superior", 2390.5, 1557.0, 32.8, 23.9, 0.0, "movel", "tom_bancada"),
            ("suite-1/criado-retangular-vista-superior", 2492.0, 1557.0, 32.8, 23.9, 0.0, "movel", "tom_bancada")],
        # o laptop (o da final) volta por cima da bancada nova
        # (o retângulo do laptop, cheio: o recorte pela diferença levava a sombra e o tampo antigos em volta)
        "abajures": [(2289.0, 1557.0, 17.0), (2390.5, 1557.0, 17.0), (2492.0, 1557.0, 17.0)],
        "recolar": [((2466, 1338, 2488, 1360), "baixa", "cheio")]},
    "suite_2": {
        "zonas": [(1702, 1081, 1829, 1209), (1664, 1177, 1868, 1209), (1619, 1014, 1675, 1070),
                  (1684, 1003, 1847, 1026), (1704, 1054, 1822, 1088)],
        "manter": [(1664, 1012, 1685, 1034)],               # a mesinha redonda
        "pecas": [
            ("suite-2/bancada-suites", 1765.5, 1014.5, 155.2, 14.9, 0.0, "baixa", None),
            ("suite-2/cama-casal-a", 1765.5, 1145.0, 119.4, 119.4, 180.0, "movel", None),
            ("suite-master/banco-pe-de-cama", 1765.5, 1072.0, 95.5, 23.9, 0.0, "movel", None),
            ("suite-1/criado-retangular-vista-superior", 1684.5, 1193.0, 32.8, 23.9, 0.0, "movel", "tom_bancada"),
            ("suite-1/criado-retangular-vista-superior", 1847.5, 1193.0, 32.8, 23.9, 0.0, "movel", "tom_bancada"),
            ("sala-intima/poltrona-a", 1647.0, 1042.0, 48.0, 48.0, girar_pt(0.75, 0.66), "movel", None)],
        # a TV (a linha escura do PDF sobre o rack) volta por cima da bancada nova
        # (o alfa pelo escuro: só a linha da TV, sem o rack claro em volta)
        "abajures": [(1684.5, 1193.0, 17.0), (1847.5, 1193.0, 17.0)],
        "recolar": [((1724, 1010, 1807, 1016), None, "escuro")]},
    "suite_3": {
        # (o pé da cama antiga ia até y 485, por cima do banco do PDF: a zona vai até o banco, y 486)
        "zonas": [(1676, 339, 1808, 486), (1637, 340, 1848, 384), (1620, 558, 1785, 602), (1666, 472, 1810, 522)],
        # a cadeira de madeira e linho (a parte de fora da mesa) e o rack da TV, que o PDF põe na frente da mesa
        "manter": [(1642, 535, 1687, 562), (1704, 579, 1873, 600)],
        "pecas": [
            ("suite-3/bancada-suites", 1702.5, 580.0, 157.0, 35.8, 0.0, "mesa", None),
            ("suite-3/cama-casal-a", 1742.0, 408.0, 124.2, 130.8, 0.0, "movel", None),
            ("suite-master/banco-pe-de-cama", 1742.0, 488.0, 95.5, 23.9, 0.0, "movel", None),
            ("suite-3/criado-redondo", 1658.5, 362.0, 35.8, 35.8, 0.0, "movel", None),
            ("suite-3/criado-redondo", 1826.0, 362.0, 35.8, 35.8, 0.0, "movel", None)],
        "abajures": [(1658.5, 362.0, 19.0), (1826.0, 362.0, 19.0)],
        "recolar": []},
    "quarto_servico": {
        "zonas": [(1910, 1330, 1977, 1457)],
        "manter": [],
        "pecas": [("quarto-de-servico/cama-solteiro-a", 1943.5, 1393.5, 59.7, 119.4, 0.0, "movel", None)],
        "recolar": []},
    "banho_master": {
        "zonas": [(1406, 1469, 1514, 1529), (1394, 1490, 1422, 1510), (1689, 1590, 1718, 1629),
                  (1413, 1588, 1434, 1609), (1484, 1588, 1505, 1609)],
        "manter": [],
        "pecas": [
            # (12/11, "VAMOS ALTERAR ESSA VEGETAÇÃO MAIS ALTA POR" + foto de espada-de-são-jorge e folhagem alta) a
            # floreira gerada no Higgsfield (gpt_image_2, job 9f219839): a mesma caixa, com a caixa no lugar da antiga
            # (166,4 x 35,0 px, centro 1369,2/1546,5); as folhas do lado do vidro param na borda da caixa
            ("banho-master/floreira-espada-de-sao-jorge-e-folhagem", 1365.13, 1546.5, 166.35, 43.35, 90.0, "baixa",
             None),
            ("banho-master/banheira-oval-a", 1460.0, 1499.0, 96.0, 48.0, 0.0, "movel", None),
            ("banho-master/misturador-piso-banheira-render", 1407.0, 1500.0, 14.0, 19.0, 90.0, "baixa", None),
            ("banho-master/bancada-dupla-esculpida-render-v2", 1599.0, 1613.0, 137.3, 35.8, 180.0, "baixa", None),
            ("banho-master/bacia-carrara", 1703.5, 1609.5, 21.1, 30.7, 180.0, "baixa", None),
            ("banho-master/chuveiro-quadrado", 1423.5, 1598.0, 13.0, 13.0, 0.0, "baixa", None),
            ("banho-master/chuveiro-quadrado", 1495.0, 1598.0, 13.0, 13.0, 0.0, "baixa", None)],
        "recolar": []},
    "banhos": {
        "zonas": [(2499, 1196, 2537, 1225), (2453, 1116, 2473, 1150), (1692, 887, 1721, 925),
                  (1637, 889, 1657, 923), (2140, 367, 2169, 406), (2204, 421, 2224, 441)],
        "manter": [],
        "pecas": [
            # banho 1: a bancada na parede da direita, a cuba a 54 px do alto (o PDF)
            ("banho-1/cuba-esculpida-travertino", 2516.0, 1279.0, 89.6, 35.8, -90.0, "baixa", ("cuba", 54.0)),
            ("banho-1/bacia-carrara", 2518.5, 1210.5, 21.1, 30.7, -90.0, "baixa", None),
            (("banho-1/chuveiro-quadrado-parede", (2463.0, 1140.5), (1118.0, "cima")), 0, 0, 0, 0, 0, "baixa", None),
            # banho 2: a bancada na parede de cima
            ("banho-2/cuba-esculpida-travertino", 1766.0, 909.0, 71.7, 35.8, 0.0, "baixa", ("cuba", 35.85)),
            ("banho-2/bacia-carrara", 1706.5, 906.0, 21.1, 30.7, 0.0, "baixa", None),
            (("banho-2/chuveiro-quadrado-parede", (1646.5, 913.5), (891.0, "cima")), 0, 0, 0, 0, 0, "baixa", None),
            # banho 3
            ("banho-3/cuba-esculpida-travertino", 2094.5, 389.0, 71.7, 35.8, 0.0, "baixa", ("cuba", 35.85)),
            ("banho-3/bacia-carrara", 2154.5, 386.5, 21.1, 30.7, 0.0, "baixa", None),
            ("banho-3/chuveiro-quadrado", 2214.0, 431.0, 12.0, 12.0, 0.0, "baixa", None)],
        "recolar": []},
    "banho_servico": {
        "zonas": [(2210, 1492, 2250, 1522), (2212, 1526, 2250, 1574), (2229, 1452, 2250, 1468)],
        "manter": [],
        "pecas": [
            ("banho-de-servico/cuba-servico-granito", 2234.5, 1550.5, 41.8, 23.9, -90.0, "baixa", "lavabo"),
            ("banho-de-servico/bacia-monte-carlo-sem-valvula", 2230.5, 1507.0, 22.5, 32.8, -90.0, "baixa", None),
            (("banho-de-servico/chuveiro-redondo-parede", (2238.0, 1460.5), (2247.0, "dir")), 0, 0, 0, 0, 0,
             "baixa", None)],
        "recolar": []},
}


def ler_png(nome):
    P = cv2.imread(str(BIB / f"{nome}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


# (12/11, usuário: "Melhore a representação dos criados das suítes") os criados retangulares da biblioteca saíam no tom
# do vinílico e sumiam no piso: vão ao tom da madeira das bancadas das suítes (`bancada-suites`, a mediana BGR), com o
# veio deles; a sombra de volume ("movel"); os redondos num círculo de 0,60 m, como no PDF (o PNG não é quadrado); e
# um abajur visto de cima em cada um (`abajur`: a cúpula de linho com a borda, o miolo aceso e a sombra curta).
TOM_BANCADA = (52.0, 107.0, 169.0)
ABAJUR = {"cupula": (214, 226, 234), "borda": 0.80, "miolo_r": 0.46, "dentro": (150, 196, 226), "luz": (225, 245, 255),
          "luz_r": 0.22, "sombra": 0.32, "sombra_px": (-1.6, 1.6, 1.4)}
MIOLO_CUBA = (0.15, 0.85)      # a cuba nos PNG da biblioteca vai de 16% a 84% da largura: só os lados lisos esticam


def cuba_na_bancada(P, L, D, c):
    """A cuba esculpida na bancada de L x D px com o miolo da cuba a c px do começo: os lados esticados até o comprimento
    em que a cuba fica no meio e o excesso cortado do lado de lá."""
    h, w = P.shape[:2]
    L2 = 2 * max(c, L - c)
    Q = BT.esticar_lados(P, L2 / D, miolo=MIOLO_CUBA)
    wq = Q.shape[1]
    corte = int(round((L2 - L) / L2 * wq))
    if c < L / 2:
        Q = Q[:, :wq - corte]
    else:
        Q = Q[:, corte:]
    return np.ascontiguousarray(Q)


def preparar(nome, larg, alt, extra=None):
    P = ler_png(nome)
    if extra == "tom_bancada":                    # a madeira das bancadas, com o veio do criado
        a = P[..., 3] > 200
        med = np.median(P[..., :3][a], axis=0)
        P = P.copy()
        P[..., :3] = np.clip(P[..., :3] * (np.float32(TOM_BANCADA) / np.maximum(med, 1))[None, None], 0, 255)
    elif extra == "anti_t":
        P = np.ascontiguousarray(np.transpose(P, (1, 0, 2))[::-1, ::-1])
    elif extra == "lavabo":
        P = BT.esticar_lados(P, larg / alt, miolo=MIOLO_CUBA)
    elif isinstance(extra, (tuple, list)) and extra[0] == "cuba":
        P = cuba_na_bancada(P, larg, alt, extra[1])
    h, w = P.shape[:2]
    if alt is None:
        alt = larg * h / w
    return P, float(larg), float(alt)


def chuveiro(nome, placa_c, parede, placa_px=12.0):
    """O chuveiro de parede da biblioteca (o braço em cima, a placa ou o crivo embaixo) com o braço até a parede:
    (P, cx, cy, larg, alt, giro); parede = (px da face, 'cima' ou 'dir')."""
    P = ler_png(nome)
    a = P[..., 3] > 128
    larg_linha = a.sum(axis=1)
    lmax = larg_linha.max()
    y_placa = int(np.argmax(larg_linha > 0.6 * lmax))
    s = placa_px / lmax
    dist, eixo = parede
    alcance = abs(dist - (placa_c[0] if eixo == "dir" else placa_c[1])) - placa_px / 2
    braco = max(1.0, alcance / s)
    can, corpo = P[:y_placa], P[y_placa:]
    can = cv2.resize(can, (can.shape[1], max(2, int(round(braco)))),
                     interpolation=cv2.INTER_AREA if braco < can.shape[0] else cv2.INTER_CUBIC)
    P2 = np.ascontiguousarray(np.concatenate([can, corpo], axis=0))
    h2, w2 = P2.shape[:2]
    wt, ht = w2 * s, h2 * s
    desloc = ht / 2 - corpo.shape[0] * s / 2
    if eixo == "dir":
        return P2, placa_c[0] + desloc, placa_c[1], wt, ht, -90.0
    return P2, placa_c[0], placa_c[1] - desloc, wt, ht, 0.0


def abajur(out, cx, cy, D, s=1.0, X0=0.0, Y0=0.0, q=None, ss=8):
    """O abajur visto de cima no criado (centro e diâmetro em px da final; u = (x - X0) s): a sombra curta, a cúpula de
    linho clara com a borda fina, o miolo (o dentro da cúpula, aceso) e a luz no meio, em 8x."""
    q = q or ABAJUR
    R = D / 2 * s
    u, v = (cx - X0) * s, (cy - Y0) * s
    m_ = int(np.ceil(R + 4 * s)) + 2
    x0, y0 = int(np.floor(u)) - m_, int(np.floor(v)) - m_
    w = h = 2 * m_ + 1
    H, W = out.shape[:2]
    if x0 < 0 or y0 < 0 or x0 + w > W or y0 + h > H:
        return out
    yy, xx = np.mgrid[0:h * ss, 0:w * ss]
    dx, dy = (xx + 0.5) / ss + x0 - u, (yy + 0.5) / ss + y0 - v
    r = np.hypot(dx, dy) / R

    def red(a):
        return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    disco = red(r <= 1.0)
    sx, sy, sg = q["sombra_px"]
    sb = cv2.GaussianBlur(cv2.warpAffine(disco, np.float32([[1, 0, sx * s], [0, 1, sy * s]]), (w, h)), (0, 0), sg * s)
    reg = out[y0:y0 + h, x0:x0 + w].astype(np.float32)
    reg *= (1 - q["sombra"] * sb * (1 - disco))[..., None]
    # a cúpula: o linho claro, um pouco mais escuro para a borda (a curva), com a luz de cima à direita
    luz = 1.0 - 0.10 * np.clip(r, 0, 1) ** 2 + 0.04 * (dx - dy) / (np.hypot(dx, dy) + 1e-3) * np.clip(r, 0, 1)
    cup = np.float32(q["cupula"])[None, None] * red(luz)[..., None]
    reg = reg * (1 - disco[..., None]) + cup * disco[..., None]
    # o miolo: o dentro da cúpula, aceso (o âmbar claro), e a luz no meio
    mi = red(r <= q["miolo_r"])[..., None]
    t = np.clip(red(r) / q["miolo_r"], 0, 1)[..., None]
    dentro = np.float32(q["luz"])[None, None] * (1 - t) + np.float32(q["dentro"])[None, None] * t
    reg = reg * (1 - mi) + dentro * mi
    # as bordas finas: a de fora e a do miolo
    lt = 0.06
    anel = red((np.abs(r - 1.0) < lt) | (np.abs(r - q["miolo_r"]) < lt * 0.8))[..., None]
    reg = reg * (1 - anel * (1 - q["borda"]))
    out[y0:y0 + h, x0:x0 + w] = np.clip(np.round(reg), 0, 255).astype(out.dtype) if out.dtype != np.float32 \
        else reg
    return out


_Q = {}


def quadro():
    if "Q" not in _Q:
        import um_pav_casaa_1111 as U
        with contextlib.redirect_stdout(io.StringIO()):
            _Q["Q"] = U.quadro()
    return _Q["Q"]


def materiais(forma):
    """(vinílico, travertino, tapetes que ficam, objetos do PDF) (bool, no quadro)."""
    import um_pav_casaa_1111 as U
    Q = quadro()
    q = U.PISOS_1111E
    vin = (Q.chapada == q["vinilico"]["chapada"]).all(axis=2)
    trav = (Q.chapada == q["travertino"]["chapada"]).all(axis=2)
    tap = np.zeros(forma, bool)
    for x0, y0, x1, y1 in TAPETES_FICAM:
        tap[y0 + 1:y1 - 1, x0 + 1:x1 - 1] = True
    with contextlib.redirect_stdout(io.StringIO()):
        pdf = U._objetos_pdf(Q, q["camadas_pdf"], 2)
    return vin, trav, tap, pdf


def fontes_auto(material, livre, zona, n=2, lado=28, alcance=160):
    """Até n caixas de `lado` px no `material` livre (fora dos objetos, da zona e das paredes), perto da zona: os pontos
    mais longe de qualquer coisa que não é piso, dentro de `alcance` px da zona."""
    ys, xs = np.nonzero(zona)
    H, W = zona.shape
    y0, y1 = max(ys.min() - alcance, 0), min(ys.max() + alcance, H)
    x0, x1 = max(xs.min() - alcance, 0), min(xs.max() + alcance, W)
    m = (material & livre)[y0:y1, x0:x1].astype(np.uint8)
    if m.sum() < lado * lado:
        return []
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    caixas = []
    for _ in range(n):
        v = float(dist.max())
        if v < 6:
            break
        yy, xx = np.unravel_index(int(np.argmax(dist)), dist.shape)
        r = int(min(lado // 2, v - 1))
        caixas.append((x0 + xx - r, y0 + yy - r, x0 + xx + r, y0 + yy + r))
        dist[max(yy - 3 * r, 0):yy + 3 * r, max(xx - 3 * r, 0):xx + 3 * r] = 0
    return caixas


def recolar(antes, caixa, cheio=None, limiar=26):
    """O recorte da peça que fica (`caixa`, px) da final de antes, com o alfa pelo que foge do fundo (a mediana da borda
    da caixa), ou a caixa inteira (`cheio`, o retângulo exato da peça): (P BGRA, cx, cy, larg, alt)."""
    x0, y0, x1, y1 = caixa
    reg = antes[y0:y1, x0:x1].astype(np.float32)
    if cheio == "escuro":                         # uma peça escura (a TV): o alfa pelo escuro, contra o claro em volta
        L = reg.mean(axis=2)
        ref = float(np.percentile(L, 90))
        a = np.clip((ref - L) / max(ref - float(L.min()), 1.0) * 1.3 - 0.15, 0, 1)
        P = np.concatenate([reg, (a * 255)[..., None]], axis=2).astype(np.float32)
        return P, (x0 + x1) / 2, (y0 + y1) / 2, float(x1 - x0), float(y1 - y0)
    if cheio:
        P = np.concatenate([reg, np.full(reg.shape[:2] + (1,), 255, np.float32)], axis=2)
        return P, (x0 + x1) / 2, (y0 + y1) / 2, float(x1 - x0), float(y1 - y0)
    borda = np.concatenate([reg[0], reg[-1], reg[:, 0], reg[:, -1]])
    fundo = np.median(borda, axis=0)
    dif = np.abs(reg - fundo).max(axis=2)
    a = np.clip((dif - limiar * 0.5) / (limiar * 0.5), 0, 1)
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    P = np.concatenate([reg, (a * 255)[..., None]], axis=2).astype(np.float32)
    return P, (x0 + x1) / 2, (y0 + y1) / 2, float(x1 - x0), float(y1 - y0)


def rotulos(forma):
    """Os rótulos e as anotações do 1º Pavimento (os dados do 12K), com 2 px de folga: não são refeitos nem cobertos."""
    import ampliacao_12k_1pav_casaa as Z1
    Z = Z1.Z
    Q = quadro()
    d = json.loads(Z.DADOS.read_text())
    m = np.zeros(forma, bool)
    for b in d["rotulos"]:
        m |= Z.alfa_rotulo(Q, b, forma) > 0.02
    for t, dd, _ in d["anotacoes"]:
        m |= Z.alfa_anotacao(t, dd, forma) > 0.02
    return cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)


def aplicar(antes):
    import pedidos_terreo_casaa_2910 as PT
    Q = quadro()
    BT._Q["Q"] = Q                                # as formas do PDF (`mascara_formas`) no quadro do 1º Pavimento
    forma = antes.shape[:2]
    out = antes.copy()
    par = PT._paredes_fixas(Q, forma) | rotulos(forma)
    vin, trav, tap, pdf = materiais(forma)
    zona_total = np.zeros(forma, bool)
    for amb in AMBIENTES.values():
        for x0, y0, x1, y1 in amb["zonas"]:
            zona_total[y0:y1, x0:x1] = True
    zona_total &= ~par
    manter_total = np.zeros(forma, bool)
    for amb in AMBIENTES.values():
        for x0, y0, x1, y1 in amb["manter"]:
            manter_total[y0:y1, x0:x1] = True
    zona_total &= ~manter_total
    livre = ~pdf & ~par & ~cv2.dilate(zona_total.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    REGISTRO.clear()
    REGISTRO.update({"pecas": [], "nao": manter_total | par, "pecas_m": np.zeros(forma, bool)})
    out = piso_de_volta(Q, antes, zona_total, tap, pdf, par, livre)
    # 2. as peças, ambiente a ambiente; o que fica volta recortado por cima
    o = out.astype(np.float32)
    nao = par
    for nome, amb in AMBIENTES.items():
        for png, cx, cy, wt, ht, ang, sombra, extra in amb["pecas"]:
            if isinstance(png, tuple):
                P, cx, cy, wt, ht, ang = chuveiro(png[0], png[1], png[2])
                reg = [list(png[:1]) + [list(png[1]), list(png[2])], cx, cy, wt, ht, ang, None]
            else:
                P, wt, ht = preparar(png, wt, ht, extra)
                reg = [png, cx, cy, wt, ht, ang, extra]
            o = BT.pousar(o, P, cx, cy, wt, ht, ang, SOMBRAS[sombra], PX_M, nao=nao | manter_total)
            REGISTRO["pecas"].append(reg)
            REGISTRO["pecas_m"] |= BT.mascara_formas([BT.caixa_rot(cx, cy, wt, ht, ang, 2)], forma)
        for cx_, cy_, d_ in amb.get("abajures", []):
            o = abajur(o, cx_, cy_, d_)
            REGISTRO["pecas"].append(["abajur", cx_, cy_, d_])
        for caixa, sombra, *cheio in amb.get("recolar", []):
            cheio = cheio[0] if cheio else None
            P, cx, cy, wt, ht = recolar(antes, caixa, cheio)
            o = BT.pousar(o, P, cx, cy, wt, ht, 0.0, SOMBRAS[sombra], PX_M, nao=nao)     # (None: sem sombra)
            REGISTRO["pecas_m"] |= BT.mascara_formas([BT.ret(*caixa, 2)], forma)
            # no 12K, o recorte volta por cima das peças nítidas (senão o tapete novo cobria a mesa de centro)
            REGISTRO["pecas"].append(["recolar", list(caixa), cheio])
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    REGISTRO["zona"] = (zona_total | REGISTRO["pecas_m"]) & ~REGISTRO["nao"]
    print(f"    biblioteca do 1º Pavimento: {int(zona_total.sum())} px de piso refeito; "
          f"{len(REGISTRO['pecas'])} peças")
    return out


REGISTRO = {}

BEGE = (232, 232, 232)
# onde o piso é Bege Bahia na zona: o quarto e o banho de serviço (na planta-base, os tapetes e partes dos móveis usam o
# mesmo cinza 232; só as manchas que tocam estas caixas são piso)
BEGE_AMBIENTES = [(1880, 1300, 2150, 1520), (2190, 1430, 2265, 1590)]


def _bege_piso(C):
    m = (C == BEGE).all(axis=2)
    n_, lab_, st_, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    caixa = np.zeros(m.shape, bool)
    for x0, y0, x1, y1 in BEGE_AMBIENTES:
        caixa[y0:y1, x0:x1] = True
    ok = np.zeros(n_, bool)
    ok[np.unique(lab_[m & caixa])] = True
    ok[0] = False
    return ok[lab_]


def piso_de_volta(Q, antes, zona, tap, pdf, par, livre):
    """A pegada das peças antigas volta ao piso do lugar. Na planta-base os móveis e os tapetes são brancos: cada px da
    zona fora dos tapetes que ficam leva o material do piso mais perto (vinílico, travertino ou Bege Bahia). O vinílico
    e o travertino saem do próprio gerador dos pisos (`um_pav_casaa_1111.pisos_1111e`, a mesma semente e a mesma
    paginação, com a zona marcada no material na planta-base e a luz do entorno por baixo): as réguas continuam. O Bege
    Bahia e os tapetes que ficam, do tecido do próprio material (`PT.piso_refeito`, fontes no mesmo tom)."""
    import copy
    import pedidos_terreo_casaa_2910 as PT
    import um_pav_casaa_1111 as U
    qp = U.PISOS_1111E
    C = Q.chapada
    cores = [tuple(qp["vinilico"]["chapada"]), tuple(qp["travertino"]["chapada"]), BEGE]
    dists = []
    for c in cores:
        # o Bege Bahia, só o dos ambientes de serviço (o px junto da cama ia para o cinza 232 de um móvel ou de um
        # tapete e saía branco); o vinílico e o travertino têm cores só deles (e vêm picados entre os móveis)
        m = _bege_piso(C) if c == BEGE else (C == c).all(axis=2)
        dists.append(cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 5))
    qual = np.argmin(np.stack(dists), axis=0)
    zr = zona & tap
    zp = zona & ~tap
    out = antes.copy()
    # vinílico e travertino: o gerador
    gerado = zp & (qual < 2)
    if gerado.any():
        chap2 = C.copy()
        for k in (0, 1):
            chap2[gerado & (qual == k)] = cores[k]
        # a luz por baixo: só o piso de verdade em volta (vinílico ou travertino, fora das peças e da zona) serve de
        # fonte; o resto perto da zona (a cama antiga sobre o tapete, o tapete, os móveis) também é apagado, senão o
        # branco da cama antiga puxava a luz e o vinílico refeito saía claro junto dela
        piso_ok = ((C == cores[0]).all(axis=2) | (C == cores[1]).all(axis=2)) & ~zona & ~pdf & ~par
        perto = cv2.dilate(zona.astype(np.uint8), np.ones((41, 41), np.uint8)).astype(bool)
        tapa = (perto & ~piso_ok) | cv2.dilate(gerado.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        base2 = cv2.inpaint(antes, tapa.astype(np.uint8) * 255, 5, cv2.INPAINT_TELEA)
        Q2 = copy.copy(Q)
        Q2.chapada = chap2
        n, lab, st, _ = cv2.connectedComponentsWithStats(gerado.astype(np.uint8))
        forcar = list(qp["forcar_px"]) + [(int(x) - 1, int(y) - 1, int(x + w) + 1, int(y + h) + 1)
                                           for x, y, w, h, _ in st[1:]]
        with contextlib.redirect_stdout(io.StringIO()):
            R = U.pisos_1111e(Q2, base2, dict(qp, forcar_px=forcar))
        al = cv2.GaussianBlur(gerado.astype(np.float32), (0, 0), 0.6)
        al = np.maximum(al, gerado.astype(np.float32))[..., None]
        out = np.clip(np.round(out.astype(np.float32) * (1 - al) + R.astype(np.float32) * al), 0, 255).astype(np.uint8)
    # Bege Bahia e tapetes: o tecido
    I = antes.astype(np.float32)
    zd = cv2.dilate(zona.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    sem = 6100
    partes = [(zp & (qual == 2), _bege_piso(C) & livre)]
    for x0, y0, x1, y1 in TAPETES_FICAM:
        r_ = np.zeros(zona.shape, bool)
        r_[y0 + 1:y1 - 1, x0 + 1:x1 - 1] = True
        if not (zr & r_).any():
            continue
        dentro = r_ & ~zd & ~par
        med = np.median(I[dentro], axis=0)
        perto = np.abs(I - med).max(axis=2) < 18                  # o tapete, sem o que está em cima dele
        partes.append((zr & r_, dentro & perto))
    for zz, fonte in partes:
        n, lab = cv2.connectedComponents(zz.astype(np.uint8))
        for i in range(1, n):
            z = lab == i
            if z.sum() < 4:
                continue
            ff = fontes_auto(fonte, ~zd, z, lado=24, alcance=220)
            if not ff:
                continue
            lado = min(min(f[2] - f[0], f[3] - f[1]) for f in ff)
            p_px = int(max(6, min(16, lado // 2)))
            out = PT.piso_refeito(out, z, sem, q=dict(PT.PISO_TA, fontes_px=ff, p_px=p_px, tom_tol=40))
            sem += 1
    return out



def salvar_registro():
    REG_JSON.write_text(json.dumps({"pecas": REGISTRO["pecas"]}, ensure_ascii=False, indent=0))
    m = np.zeros(REGISTRO["zona"].shape + (3,), np.uint8)
    m[..., 0] = REGISTRO["zona"] * 255
    m[..., 1] = REGISTRO["nao"] * 255
    cv2.imwrite(str(REG_MASC), m)


def pecas_12k(final, entrada, out, s, X0, Yia, Ya3, px_m=PX_M):
    """No 12K do 1º Pavimento (`ampliacao_12k_terreo_casaa.montar12k`, antes dos tracejados e dos textos): na zona
    refeita, a final nova ampliada sobre a saída da IA; por cima, cada peça nítida, do PNG na escala do 12K."""
    if not REG_JSON.exists():
        return out
    reg = json.loads(REG_JSON.read_text())
    antes = None
    if any(it[0] == "recolar" for it in reg["pecas"]):
        # os recortes do que fica vêm da final de antes (como na final; na nova, o fundo já é o tapete e a bancada
        # novos e o recorte levava o contorno ou o fundo antigo)
        rel = FINAL.relative_to(RAIZ_GIT)
        dado = subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"], capture_output=True,
                              check=True).stdout
        antes = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    mk = cv2.imread(str(REG_MASC))
    zona, nao = mk[..., 0] > 127, mk[..., 1] > 127
    H, W = out.shape[:2]
    n, lab, st, _ = cv2.connectedComponentsWithStats(zona.astype(np.uint8))
    for i in range(1, n):
        x, y, w, h = st[i, :4]
        fx0, fy0 = max(x - 8, 0), max(y - 8, 0)
        fx1, fy1 = min(x + w + 8, final.shape[1]), min(y + h + 8, final.shape[0])
        U0, V0 = max(int(np.floor((fx0 - X0) * s)), 0), max(int(np.floor((fy0 - Ya3) * s)), 0)
        U1, V1 = min(int(np.ceil((fx1 - X0) * s)), W), min(int(np.ceil((fy1 - Ya3) * s)), H)
        if U1 <= U0 or V1 <= V0:
            continue
        Mw = np.array([[1 / s, 0, U0 / s + X0 - fx0], [0, 1 / s, V0 / s + Ya3 - fy0]], np.float64)
        src = cv2.warpAffine(final[fy0:fy1, fx0:fx1], Mw, (U1 - U0, V1 - V0),
                             flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        src = src.astype(np.float32)
        src = src + 0.4 * (src - cv2.GaussianBlur(src, (0, 0), 0.6 * s))
        z = (lab[fy0:fy1, fx0:fx1] == i).astype(np.float32)
        al = cv2.warpAffine(z, Mw, (U1 - U0, V1 - V0), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        al = np.clip(cv2.GaussianBlur(al, (0, 0), 0.7 * s), 0, 1)[..., None]
        r = out[V0:V1, U0:U1].astype(np.float32)
        out[V0:V1, U0:U1] = np.clip(np.round(r * (1 - al) + src * al), 0, 255).astype(np.uint8)
    out = tapetes_12k(final, out, s, X0, Ya3, zona)
    for item in reg["pecas"]:
        if item[0] == "abajur":
            out = abajur(out, item[1], item[2], item[3], s, X0, Ya3)
            continue
        if item[0] == "recolar":
            # o que ficou, recortado da final (sobre as peças novas), por cima das peças nítidas
            P, cx, cy, wt, ht = recolar(antes, item[1], item[2] if len(item) > 2 else None)
            P = np.clip(cv2.resize(P, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4), 0, 255)  # sem serrilhar
            ang, extra, png = 0.0, None, None
        else:
            png, cx, cy, wt, ht, ang, extra = item
        if png is None:
            pass
        elif isinstance(png, list):
            P = chuveiro(png[0], tuple(png[1]), tuple(png[2]))[0]
        else:
            P = preparar(png, wt, ht, tuple(extra) if isinstance(extra, list) else extra)[0]

        def nao_fn(xa, ya, xb, yb):
            fy = np.clip(np.floor(np.arange(ya, yb) / s + Ya3).astype(int), 0, nao.shape[0] - 1)
            fx = np.clip(np.floor(np.arange(xa, xb) / s + X0).astype(int), 0, nao.shape[1] - 1)
            return nao[fy[:, None], fx[None, :]]
        out = BT.pousar(out, P, (cx - X0) * s, (cy - Ya3) * s, wt * s, ht * s, ang, [], px_m * s, nao=nao_fn)
    print(f"    biblioteca no 12K do 1º Pavimento: {len(reg['pecas'])} peças nítidas sobre a zona refeita")
    return out


def tapetes_12k(final, out, s, X0, Ya3, zona):
    """No 12K, a pegada das peças antigas sobre os tapetes que ficam: o tecido do próprio tapete da saída da IA (a final
    ampliada é lisa e clara ao lado da trama da IA, e a emenda aparecia), no tom do tapete, com a beira suave."""
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import texturas
    H, W = out.shape[:2]
    F = final.astype(np.float32)
    zd = cv2.dilate(zona.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    for i, (x0, y0, x1, y1) in enumerate(TAPETES_FICAM):
        r_ = np.zeros(zona.shape, bool)
        r_[y0 + 2:y1 - 2, x0 + 2:x1 - 2] = True
        zr = zona & r_
        if zr.sum() < 20:
            continue
        dentro = r_ & ~zd
        med = np.median(F[dentro], axis=0)
        fonte = dentro & (np.abs(F - med).max(axis=2) < 18)
        ff = fontes_auto(fonte, ~zd, zr, n=3, lado=26, alcance=220)
        if not ff:
            continue
        ys, xs = np.nonzero(zr)
        fx0, fy0, fx1, fy1 = xs.min() - 3, ys.min() - 3, xs.max() + 4, ys.max() + 4
        U0, V0 = max(int(np.floor((fx0 - X0) * s)), 0), max(int(np.floor((fy0 - Ya3) * s)), 0)
        U1, V1 = min(int(np.ceil((fx1 - X0) * s)), W), min(int(np.ceil((fy1 - Ya3) * s)), H)
        fs = []
        for a, b, c, d in ff:
            u0, v0 = int(round((a - X0) * s)), int(round((b - Ya3) * s))
            u1, v1 = int(round((c - X0) * s)), int(round((d - Ya3) * s))
            f_ = out[v0:v1, u0:u1]
            fs += [f_.copy(), np.ascontiguousarray(f_[:, ::-1])]
        lado = min(min(f.shape[:2]) for f in fs)
        p = int(max(16, min(48, lado // 2)))
        tec = texturas.quilting(fs, V1 - V0, U1 - U0, p=p, sobra=max(4, p // 3),
                                rng=np.random.default_rng(7300 + i))[:V1 - V0, :U1 - U0].astype(np.float32)
        med_f = np.median(np.concatenate([f.reshape(-1, 3) for f in fs]).astype(np.float32), axis=0)
        tec += med_f - np.median(tec.reshape(-1, 3), axis=0)
        Mw = np.array([[1 / s, 0, U0 / s + X0 - fx0], [0, 1 / s, V0 / s + Ya3 - fy0]], np.float64)
        al = cv2.warpAffine(zr[fy0:fy1, fx0:fx1].astype(np.float32), Mw, (U1 - U0, V1 - V0),
                            flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        al = np.clip(cv2.GaussianBlur(al, (0, 0), 0.6 * s), 0, 1)[..., None]
        reg = out[V0:V1, U0:U1].astype(np.float32)
        out[V0:V1, U0:U1] = np.clip(np.round(reg * (1 - al) + tec * al), 0, 255).astype(np.uint8)
    return out


ANTES_DEPOIS = {"sala_intima": (1980, 880, 2190, 1240), "suite_master": (1380, 1250, 1720, 1470),
                "suite_1": (2260, 1320, 2520, 1590), "suite_2": (1610, 990, 1880, 1215),
                "suite_3": (1615, 330, 1860, 610), "quarto_servico": (1900, 1320, 2030, 1465),
                "banho_master": (1335, 1455, 1730, 1645), "banhos": (2380, 1105, 2555, 1330),
                "banho_2": (1620, 880, 1810, 935), "banho_3": (2050, 360, 2235, 445),
                "banho_servico": (2190, 1440, 2260, 1585)}


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(3.0, 1100 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        for im, t in ((a, "ANTES"), (b, "DEPOIS")):
            cv2.putText(im, t, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 4, cv2.LINE_AA)
            cv2.putText(im, t, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 30, 30), 2, cv2.LINE_AA)
        sep = np.full((a.shape[0], 16, 3), 255, np.uint8)
        cv2.imwrite(str(R / f"POE642_CasaA_PH_1Pavimento_1211b_{nome}_antes_depois.jpg"), np.hstack([a, sep, b]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes", type=Path)
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    if a.antes:
        antes = cv2.imread(str(a.antes))
    else:
        rel = FINAL.relative_to(RAIZ_GIT)
        dado = subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"], capture_output=True,
                              check=True).stdout
        antes = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    depois = aplicar(antes)
    destino = a.saida or FINAL
    cv2.imwrite(str(destino), depois)
    print(f"    {destino}")
    if not a.saida:
        salvar_registro()
        antes_depois(antes, depois)


if __name__ == "__main__":
    main()

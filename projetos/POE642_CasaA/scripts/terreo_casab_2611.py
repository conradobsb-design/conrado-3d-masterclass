"""Casa B Térreo, 26/11: o levantamento no 12K B aplicado ("ok, pode aplicar os 5";
`../../POE642_CasaB/renders/POE642_CasaB_PH_Terreo_2611_levantamento.jpg`).

1. **Vidros sem linha técnica**: o vidro de antes (a barra cinza cromada com o contorno; no banho master, os de entre a
   ducha e o vaso em preto) sai, coberto pelo piso de logo ao lado (a faixa deslocada, do lado livre), e as folhas do
   PDF entram no vidro claro dos boxes, sem contorno (`um_pav_casaa_2511e.folhas_vidro`), de parede a parede: o banho
   master (as duas divisórias de correr, 4 folhas cada, e os dois vidros fixos entre a ducha e o vaso), os Banhos 1, 2 e
   3, os dois BH gourmet, o BH serviço e o BH motorista (os boxes de correr, 2 folhas); a frente da adega: a soleira de
   pedra no travertino mais escuro (a faixa da esquadria do PDF) e o vidro fixo por cima; o fio escuro de antes, logo
   abaixo, coberto pelo piso de logo abaixo.
2. **Nichos** (os 15 retângulos do PDF nas paredes dos banhos, que vinham como ferragem cromada com puxador): a parede de
   fora a fora, no cinza dela e nas faces dela (medidas na própria imagem, logo acima e abaixo do nicho), e o piso do
   lado do banho, onde a ferragem passava da parede, coberto pelo piso de logo ao lado.
3. **Vasos** (banho master, os dois; Banhos 1, 2 e 3): o vaso quebrado sai (o travertino refeito na pegada, até a
   parede de trás) e entra a bacia Carrara da biblioteca (`biblioteca_1pav_casaa_1211`), na pose do PDF (21,1 x 30,7,
   de costas para a parede), com a sombra rente.
4. **Passagem do closet master para a sala íntima**: a faixa cinza translúcida com contorno vira soleira de pedra no
   travertino mais escuro (o vão do PDF, 1550,3 a 1562,3 x 510,7 a 576,4); a parede quina a quina: do toco de cima até a
   face da folha aberta (517,9) e, embaixo, da ponta da folha fechada (54,9 de folha: 572,8) até o toco.
5. **Pontas do vidro entre a varanda e o living**: o tampão da esquadria (a barra com contorno e o bloco cinza) sai; a
   parede de cima reta até a face dela (776,4) e a de baixo a partir de 1245,2, no cinza e com as faces da própria
   parede; o vidro (o da varanda, como está) estendido até encostar em cada uma; o piso no resto do tampão.

Final, prancha e 12K A e B (cada item pelo registro local).

  python3 terreo_casab_2611.py [item ...]
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

PLANTA = "B_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]                     # o travertino novo: a textura e o px/m da Casa A, o 12K na escala desta planta
PAREDE = (80.0, 80.0, 80.0)
SOLEIRA = dict(escurecer=0.84, contorno=1.0, larg=0.22)


def copiar(img, s, origem, r, d, lados, pena=1.0):
    return U._copiar(img, s, origem, r, d, lados, pena)


def pintar(img, s, origem, rets, cor=PAREDE):
    x0 = min(r[0] for r in rets) - 1
    y0 = min(r[1] for r in rets) - 1
    x1 = max(r[2] for r in rets) + 1
    y1 = max(r[3] for r in rets) + 1
    jan, reg = C._reg(img, (x0, y0, x1, y1), s, origem)
    reg = V.compor(reg, V.cob([V.ret(*r) for r in rets], jan, s, origem), np.float32(cor))
    return C._gravar(img, jan, reg)


def vidros(img, s, origem, caixa, folhas):
    jan, reg = C._reg(img, caixa, s, origem, folga=int(2 * s) + 2)
    reg = E.folhas_vidro(reg, jan, s, origem, folhas)
    return C._gravar(img, jan, reg)


def _caixa(rets, m=3.0):
    return (min(r[0] for r in rets) - m, min(r[1] for r in rets) - m, max(r[2] for r in rets) + m,
            max(r[3] for r in rets) + m)


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os vidros: (o retângulo do vidro velho, o deslocamento do piso que o cobre, os lados com emenda suave), as folhas
VIDROS = {
    "vidro_master": dict(
        apagar=[((1321.9, 364.5, 1327.9, 501.8), (7.2, 0.0), "lr"), ((1468.6, 364.5, 1474.2, 501.8), (-7.2, 0.0), "lr"),
                ((1245.8, 442.6, 1321.9, 447.6), (0.0, -5.6), "tb"),
                ((1474.2, 442.6, 1550.3, 447.6), (0.0, -5.6), "tb")],
        folhas=[[(1323.4, 364.5, 1324.9, 407.1)], [(1324.9, 402.9, 1326.4, 445.5)],
                [(1324.9, 446.1, 1326.4, 475.7)], [(1323.4, 471.5, 1324.9, 501.8)],
                [(1471.2, 364.5, 1472.7, 407.1)], [(1469.8, 402.9, 1471.3, 445.5)],
                [(1469.8, 446.1, 1471.3, 475.7)], [(1471.2, 471.5, 1472.7, 501.8)],
                [(1245.8, 444.4, 1323.4, 445.8)], [(1472.7, 444.4, 1550.3, 445.8)]]),
    "vidro_banho1": dict(apagar=[((1830.9, 404.6, 1932.4, 411.2), (0.0, -7.6), "tb")],
                         folhas=[[(1830.9, 406.4, 1883.8, 407.9)], [(1879.6, 407.9, 1932.4, 409.4)]]),
    "vidro_banho2": dict(apagar=[((2657.9, 405.6, 2759.4, 412.2), (0.0, -7.6), "tb")],
                         folhas=[[(2657.9, 407.4, 2710.8, 408.9)], [(2706.6, 408.9, 2759.4, 410.4)]]),
    "vidro_banho3": dict(apagar=[((2731.3, 842.1, 2737.9, 931.7), (-7.6, 0.0), "lr")],
                         folhas=[[(2734.6, 842.1, 2736.1, 889.0)], [(2733.1, 884.8, 2734.6, 931.7)]]),
    "vidro_gourmet_esq": dict(apagar=[((1108.5, 1602.6, 1210.0, 1609.2), (0.0, 7.6), "tb")],   # de baixo (o rótulo em cima)
                              folhas=[[(1108.5, 1604.4, 1161.3, 1605.9)], [(1157.1, 1605.9, 1210.0, 1607.4)]]),
    "vidro_gourmet_dir": dict(apagar=[((1436.9, 1602.8, 1538.4, 1609.4), (0.0, 7.6), "tb")],
                              folhas=[[(1436.9, 1604.6, 1489.7, 1606.1)], [(1485.5, 1606.1, 1538.4, 1607.6)]]),
    "vidro_bh_servico": dict(apagar=[((1830.9, 1609.1, 1902.6, 1615.7), (0.0, 7.6), "tb")],
                             folhas=[[(1830.9, 1610.9, 1868.9, 1612.4)], [(1864.7, 1612.4, 1902.6, 1613.9)]]),
    "vidro_bh_motorista": dict(apagar=[((2852.0, 1504.9, 2858.5, 1576.5), (-7.6, 0.0), "lr")],
                               folhas=[[(2855.2, 1504.9, 2856.7, 1542.8)], [(2853.8, 1538.6, 2855.3, 1576.5)]]),
}
# o fio escuro de antes, logo abaixo da faixa (1197 a 1198,5), coberto pelo piso de logo abaixo
ADEGA = dict(soleira=(2044.7, 1182.5, 2238.2, 1194.4), vidro=(2044.7, 1187.2, 2238.2, 1190.2),
             fio=((2045.0, 1194.4, 2238.0, 1199.8), (0.0, 6.0)))


def _vidro(nome):
    def f(img, s, origem, q=VIDROS[nome]):
        for r, d, lados in q["apagar"]:
            img = copiar(img, s, origem, r, d, lados)
        return vidros(img, s, origem, _caixa([r for f_ in q["folhas"] for r in f_]), q["folhas"])
    return f


def vidro_adega(img, s, origem, q=ADEGA):
    r, d = q["fio"]
    img = copiar(img, s, origem, r, d, "lrb", pena=1.0)
    img = G.soleira_trav(img, s, origem, [q["soleira"]], q=SOLEIRA)
    return vidros(img, s, origem, _caixa([q["vidro"]]), [[q["vidro"]]])


# ----------------------------------------------------------------------------------------------------------------------
# 2. Os nichos: o retângulo do PDF, o eixo da parede ("v": parede em pé), os lados com a ferragem passando para o piso
#    ("+": à direita / embaixo; "-": à esquerda / em cima) e a largura dessa faixa de piso
NICHOS = {
    "nicho_banho2_dir": ((2759.4, 363.9, 2767.1, 393.7), "v", {"-": 6.0}),
    "nicho_banho1_esq": ((1825.3, 365.6, 1830.9, 395.5), "v", {"+": 6.0}),
    "nicho_master_esq": ((1239.8, 379.4, 1245.8, 415.2), "v", {"+": 6.0}),
    "nicho_master_dir": ((1550.3, 379.6, 1558.1, 414.0), "v", {"-": 6.0}),
    "nicho_banho1_dir": ((1932.4, 434.9, 1938.4, 476.7), "v", {"-": 6.0}),
    "nicho_banho2_esq": ((2651.1, 441.4, 2657.9, 483.2), "v", {"+": 6.0}),
    "nicho_master_wc_esq": ((1245.8, 501.8, 1289.4, 507.6), "h", {}),
    "nicho_master_wc_dir": ((1506.7, 501.8, 1550.3, 507.3), "h", {}),
    "nicho_banho3_cima": ((2590.5, 836.2, 2632.2, 842.1), "h", {"+": 7.5}),
    "nicho_banho3_baixo": ((2759.4, 931.7, 2789.3, 939.3), "h", {"-": 6.5}),
    "nicho_gourmet_dir_dir": ((1538.4, 1550.2, 1543.9, 1594.3), "v", {"-": 6.0}),
    "nicho_gourmet_esq_esq": ((1099.5, 1550.3, 1108.5, 1594.4), "v", {"+": 6.0}),
    "nicho_gourmet_esq_dir": ((1210.0, 1623.4, 1215.9, 1647.3), "v", {"-": 6.0}),
    "nicho_gourmet_dir_esq": ((1431.6, 1624.4, 1436.9, 1648.3), "v", {"+": 6.0, "-": 8.5}),
    "nicho_bh_servico": ((1902.6, 1633.3, 1908.1, 1651.2), "v", {"-": 6.0}),
}
# o piso da faixa: o travertino novo (luz do piso em volta), menos no BH serviço (o piso marrom: o de logo ao lado)
NICHO_COPIA = {"nicho_bh_servico"}
# as faces do PDF, sem medir: os nichos rentes ao canto (a medida cairia dentro da outra parede)
NICHO_PDF = {"nicho_master_wc_esq", "nicho_master_wc_dir"}
# as faces da parede no PDF (o preenchimento cinza da ARQ_PAREDE que encosta nas pontas do nicho)
FACES_PDF = {(2759.4, 363.9, 2767.1, 393.7): (2759.4, 2769.6), (1825.3, 365.6, 1830.9, 395.5): (1823.8, 1830.9),
             (1239.8, 379.4, 1245.8, 415.2): (1235.6, 1245.8), (1550.3, 379.6, 1558.1, 414.0): (1550.3, 1560.5),
             (1932.4, 434.9, 1938.4, 476.7): (1932.4, 1939.6), (2651.1, 441.4, 2657.9, 483.2): (2647.8, 2657.9),
             (1245.8, 501.8, 1289.4, 507.6): (501.8, 508.9), (1506.7, 501.8, 1550.3, 507.3): (501.8, 508.9),
             (2590.5, 836.2, 2632.2, 842.1): (835.0, 842.1), (2759.4, 931.7, 2789.3, 939.3): (931.7, 941.8),
             (1538.4, 1550.2, 1543.9, 1594.3): (1538.4, 1548.5), (1099.5, 1550.3, 1108.5, 1594.4): (1095.3, 1108.5),
             (1210.0, 1623.4, 1215.9, 1647.3): (1210.0, 1217.1), (1431.6, 1624.4, 1436.9, 1648.3): (1429.7, 1436.9),
             (1902.6, 1633.3, 1908.1, 1651.2): (1902.6, 1909.8)}
NICHO_M = 3.5          # a folga ao longo da parede (a ferragem passa um pouco das pontas do nicho)


def _faces(img, s, origem, r, eixo):
    """As faces da parede (px da final, no eixo perpendicular) e o cinza dela, medidos logo antes e logo depois do
    nicho: o trecho escuro contínuo que contém o nicho, a face na meia altura entre a parede e o que vem fora."""
    x0, y0, x1, y1 = r
    p0, p1, a0, a1 = (x0, x1, y0, y1) if eixo == "v" else (y0, y1, x0, x1)
    caixa = (p0 - 12, a0 - 5, p1 + 12, a1 + 5) if eixo == "v" else (a0 - 5, p0 - 12, a1 + 5, p1 + 12)
    jan, reg = C._reg(img, caixa, s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    L = reg.mean(2)
    if eixo == "h":
        L = L.T
        reg = reg.transpose(1, 0, 2)
        xs, ys = ys, xs
    # agora: linhas = ao longo da parede (ys), colunas = perpendicular (xs)
    amostra = ((ys >= a0 - 4.0) & (ys <= a0 - 1.5)) | ((ys >= a1 + 1.5) & (ys <= a1 + 4.0))
    prof = np.median(L[amostra], axis=0)
    q0, q1 = FACES_PDF.get(r, (p0, p1))
    miolo = (xs >= q0 + 0.8) & (xs <= q1 - 0.8)
    parede_ref = float(np.median(prof[miolo])) if miolo.any() else 80.0
    centro = int(np.argmin(np.abs(xs - (q0 + q1) / 2)))
    escuro = prof < parede_ref + 16          # o piso marrom (do BH serviço) fica fora
    if not escuro[centro]:
        return (q0, q1), np.float32(PAREDE)
    i0 = centro
    while i0 > 0 and escuro[i0 - 1]:
        i0 -= 1
    i1 = centro
    while i1 < len(prof) - 1 and escuro[i1 + 1]:
        i1 += 1
    parede = float(np.median(prof[i0:i1 + 1]))
    cor = np.median(reg[amostra][:, miolo].reshape(-1, 3), axis=0) if miolo.any() else np.float32(PAREDE)

    def cruza(i_dentro, passo):
        j = i_dentro + passo
        fora = float(np.median(prof[max(0, j):max(0, j) + 3])) if passo > 0 else float(np.median(prof[max(0, j - 2):j + 1]))
        if abs(fora - parede) < 40:          # pouco contraste (o piso marrom): a face do PDF
            return q0 if passo < 0 else q1
        thr = (parede + fora) / 2
        a, b = prof[i_dentro], prof[j]
        t = (thr - a) / (b - a) if b != a else 0.5
        return float(xs[i_dentro] + passo * np.clip(t, 0, 1) / s)

    f0 = cruza(i0, -1) if i0 > 0 else p0
    f1 = cruza(i1, +1) if i1 < len(prof) - 1 else p1
    # a parede do PDF manda: o trecho escuro pode seguir numa peça escura colada (a face fica a até 2,5 px da do PDF)
    f0 = float(np.clip(f0, q0 - 2.5, q0 + 2.5))
    f1 = float(np.clip(f1, q1 - 2.5, q1 + 2.5))
    return (f0, f1), cor.astype(np.float32)


def _nicho(nome):
    def f(img, s, origem, q=NICHOS[nome]):
        r, eixo, lados = q
        (f0, f1), cor = _faces(img, s, origem, r, eixo)
        if nome in NICHO_PDF:
            f0, f1 = FACES_PDF[r]
        x0, y0, x1, y1 = r
        a0, a1 = (y0, y1) if eixo == "v" else (x0, x1)
        m = NICHO_M
        for lado, hw in lados.items():
            if eixo == "v":
                fx = (f1, a0 - m, f1 + hw, a1 + m) if lado == "+" else (f0 - hw, a0 - m, f0, a1 + m)
                d = (hw + 1.0, 0.0) if lado == "+" else (-(hw + 1.0), 0.0)
                ld = "rtb" if lado == "+" else "ltb"
            else:
                fx = (a0 - m, f1, a1 + m, f1 + hw) if lado == "+" else (a0 - m, f0 - hw, a1 + m, f0)
                d = (0.0, hw + 1.0) if lado == "+" else (0.0, -(hw + 1.0))
                ld = "blr" if lado == "+" else "tlr"
            if nome in NICHO_COPIA:
                img = copiar(img, s, origem, fx, d, ld, pena=1.2)
            else:
                # a luz: a faixa de logo depois (sem a parede)
                lx = (fx[0] + d[0], fx[1] + d[1], fx[2] + d[0], fx[3] + d[1])
                img = D.refazer_piso(img, s, origem, [V.ret(*fx)], ref_luz=[V.ret(*lx)], pena=0.8)
        pr = (f0, a0 - m + 0.5, f1, a1 + m - 0.5) if eixo == "v" else (a0 - m + 0.5, f0, a1 + m - 0.5, f1)
        return pintar(img, s, origem, [pr], tuple(float(c) for c in cor))
    return f


# ----------------------------------------------------------------------------------------------------------------------
# 3. Os vasos: a pegada do PDF (21,1 x 30,7), a parede de trás ("l", "r", "t", "b"), o giro da bacia
VASOS = {
    "vaso_master_esq": ((1245.8, 464.4, 1276.5, 485.5), "l", 90.0),
    "vaso_master_dir": ((1519.6, 464.4, 1550.3, 485.5), "r", -90.0),
    "vaso_banho1": ((1830.9, 425.6, 1861.6, 446.6), "l", 90.0),
    "vaso_banho2": ((2728.8, 428.5, 2759.4, 449.6), "r", -90.0),
    "vaso_banho3": ((2698.1, 901.0, 2719.2, 931.7), "b", 180.0),
}
VASO_FOLGA = 3.0


def _vaso(nome):
    def f(img, s, origem, q=VASOS[nome]):
        (x0, y0, x1, y1), atras, ang = q
        k = VASO_FOLGA
        zona = (x0 - (0 if atras == "l" else k), y0 - (0 if atras == "t" else k),
                x1 + (0 if atras == "r" else k), y1 + (0 if atras == "b" else k))
        lados = "".join(c for c in "ltrb" if c != atras)
        img = G.refazer(img, s, origem, [(zona, lados)])
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return U._pousar(img, s, origem, "banho-2/bacia-carrara", cx, cy, 21.1, 30.7, ang, "baixa")
    return f


# ----------------------------------------------------------------------------------------------------------------------
# 4. A passagem do closet master
CLOSET = dict(soleira=(1550.3, 510.7, 1562.3, 576.4), parede=[(1550.3, 510.7, 1562.3, 517.9), (1550.3, 572.8, 1562.3, 576.4)])


def soleira_closet(img, s, origem, q=CLOSET):
    img = G.soleira_trav(img, s, origem, [q["soleira"]], q=SOLEIRA)
    return pintar(img, s, origem, q["parede"])


# ----------------------------------------------------------------------------------------------------------------------
# 5. As pontas do vidro da varanda: a parede (o trecho de parede de logo ao lado, deslocado), o piso no resto do tampão,
#    o vidro de logo ao lado estendido até a parede
PONTAS = {
    "ponta_varanda_cima": dict(parede=((1548.6, 766.0, 1562.3, 776.4), (-14.0, 0.0)),
                               piso=((1549.0, 776.4, 1558.6, 781.0), (0.0, 6.0)),
                               vidro=((1558.4, 776.4, 1563.0, 786.0), (0.0, 11.0))),
    "ponta_varanda_baixo": dict(parede=((1549.6, 1245.2, 1562.3, 1253.0), (0.0, 10.0)),
                                piso=((1554.0, 1236.0, 1564.5, 1245.2), (0.0, -9.5)),
                                vidro=((1549.6, 1233.0, 1554.2, 1245.2), (0.0, -12.0))),
}


def _ponta(nome):
    def f(img, s, origem, q=PONTAS[nome]):
        r, d = q["piso"]
        img = copiar(img, s, origem, r, d, "lrtb" if False else ("lrb" if d[1] > 0 else "lrt"), pena=1.0)
        r, d = q["vidro"]
        img = copiar(img, s, origem, r, d, "", pena=1.0)
        r, d = q["parede"]
        return copiar(img, s, origem, r, d, "", pena=1.0)
    return f


# ----------------------------------------------------------------------------------------------------------------------
FUNC = {}
ITENS = {}
for n in NICHOS:
    FUNC[n] = _nicho(n)
    ITENS[n] = _caixa([NICHOS[n][0]], 14.0)
for n in VIDROS:
    FUNC[n] = _vidro(n)
    ITENS[n] = _caixa([r for r, _, _ in VIDROS[n]["apagar"]], 14.0)
FUNC["vidro_adega"] = vidro_adega
ITENS["vidro_adega"] = _caixa([ADEGA["soleira"]], 14.0)
for n in VASOS:
    FUNC[n] = _vaso(n)
    ITENS[n] = _caixa([VASOS[n][0]], 14.0)
FUNC["soleira_closet"] = soleira_closet
ITENS["soleira_closet"] = _caixa([CLOSET["soleira"]], 14.0)
for n in PONTAS:
    FUNC[n] = _ponta(n)
    ITENS[n] = _caixa([PONTAS[n]["parede"][0], PONTAS[n]["vidro"][0]], 16.0)


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
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

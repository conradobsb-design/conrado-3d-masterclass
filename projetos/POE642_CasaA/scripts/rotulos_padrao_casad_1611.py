"""Os rótulos do Térreo da Casa D no padrão das casas (16/11, usuário: "Os rótulos também precisam estar centralizados,
alinhados no que for possível, padronizados... Eu não quero que os rótulos chamem a atenção, eles têm que estar bem
organizados, como a gente já vem feito aí na casa A, B, C e D... A gente vai seguir esse padrão para todas as casas").

O padrão (o dos rótulos do motor e dos Subsolos refeitos): Inter Regular; o nome e a área ("A: xx m²") em duas linhas,
15 px entre as bases; um corpo só, o da altura de maiúscula de 8 px dos rótulos do PDF (10,95 px; `normal`), e 7 px só
onde o ambiente não cabe a linha (`pequeno`: louceiro, despensa, WC DCE); o escuro (20, 20, 20) nos pisos claros e o
claro (236, 236, 236) nos granitos e no gramado. Cada rótulo no meio do espaço livre do ambiente, e as fileiras
alinhadas pela base da 1ª linha: suítes e closets das suítes (1500), banhos (1636), closets da master (1644),
circulações (1364), suíte master e sala íntima (1387), living e hall (1016), cozinha e gourmet (572), área de serviço,
louceiro e garagem (437), lavabo e o jardim dele (1252). As descrições das escadas ficam (o padrão delas é outro).

`aplicar(img)`: todos os rótulos de antes saem (os do motor, achados pela forma como na opção B, e os que a revisão de
15/11 escreveu; `rotulos_kalam_casac.apagar`) e entram os da tabela. `linhas()` dá as linhas para a opção B (Kalam).
"""
import contextlib
import io

import cv2
import numpy as np

ESCURO, CLARO = (20, 20, 20), (236, 236, 236)
CORPOS = {"normal": (10.95, 15.0), "pequeno": (9.6, 13.1)}            # (corpo px, entrelinha px)
# (nome, linhas, (meio x, base da 1ª linha) px, corpo, cor)
ROTULOS_T = [
    ("SUÍTE MASTER", ("SUÍTE MASTER", "A: 46,51 m²"), (1022.0, 1387.0), "normal", ESCURO),
    ("SALA ÍNTIMA", ("SALA ÍNTIMA", "A: 43,25 m²"), (1664.0, 1387.0), "normal", ESCURO),
    ("CIRCULAÇÃO (master)", ("CIRCULAÇÃO", "A: 6,23 m²"), (1300.0, 1364.0), "normal", ESCURO),
    ("CIRCULAÇÃO (suítes)", ("CIRCULAÇÃO", "A: 8,06 m²"), (1992.0, 1364.0), "normal", ESCURO),
    ("CLOSET (suíte 1)", ("CLOSET", "A: 3,60 m²"), (1162.5, 1500.0), "normal", ESCURO),
    ("SUÍTE 1", ("SUÍTE 1", "A: 24,62 m²"), (1342.0, 1500.0), "normal", ESCURO),
    ("SUÍTE 2", ("SUÍTE 2", "A: 24,6 m²"), (1951.5, 1500.0), "normal", ESCURO),
    ("CLOSET (suíte 2)", ("CLOSET", "A: 3,60 m²"), (2082.0, 1500.0), "normal", ESCURO),
    ("SUÍTE 3/ESCRITÓRIO", ("SUÍTE 3/ESCRITÓRIO", "A: 33,03 m²"), (2388.0, 1500.0), "normal", ESCURO),
    ("CLOSET (master)", ("CLOSET", "A: 12,31 m²"), (655.0, 1644.0), "normal", ESCURO),
    ("CLOSET (master 2)", ("CLOSET", "A: 6,32 m²"), (1019.5, 1644.0), "normal", ESCURO),
    ("BANHO MASTER", ("BANHO MASTER", "A: 5,3 m²"), (868.0, 1636.0), "normal", ESCURO),
    ("BANHO 1", ("BANHO 1", "A: 5,73 m²"), (1161.5, 1636.0), "normal", ESCURO),
    ("BANHO 2", ("BANHO 2", "A: 5,73 m²"), (2085.5, 1636.0), "normal", ESCURO),
    ("BANHO 3", ("BANHO 3", "A: 5,73 m²"), (2224.5, 1636.0), "normal", ESCURO),
    ("JARDIM (sala íntima)", ("JARDIM", "A: 5,5 m²"), (1634.0, 1710.0), "normal", CLARO),
    ("ELEVADOR", ("ELEVADOR",), (1393.0, 1279.0), "normal", ESCURO),
    ("LIVING/JANTAR", ("LIVING/JANTAR", "A: 110,03 m²"), (2099.5, 1016.0), "normal", ESCURO),
    ("HALL DE ENTRADA", ("HALL DE ENTRADA", "A: 17,79 m²"), (2536.0, 1016.0), "normal", ESCURO),
    ("VARANDA GOURMET", ("VARANDA GOURMET", "A: 60,13 m²"), (1590.0, 926.0), "normal", ESCURO),
    ("DECK PISCINA", ("DECK PISCINA", "A: 137,46 m²"), (1070.5, 1081.0), "normal", ESCURO),
    ("PISCINA", ("PISCINA", "A: 23,02 m²"), (1003.5, 703.0), "normal", ESCURO),
    ("PRAINHA", ("PRAINHA", "A: 13,72 m²"), (1184.5, 631.0), "normal", ESCURO),
    ("SPA", ("SPA", "A: 6,29 m²"), (1194.0, 884.0), "normal", ESCURO),
    ("ADEGA", ("ADEGA", "A: 4,08 m²"), (2428.5, 849.0), "normal", ESCURO),
    ("LAVABO", ("LAVABO", "A: 4,48 m²"), (2541.0, 1252.0), "normal", ESCURO),
    ("JARDIM (lavabo)", ("JARDIM",), (2661.0, 1252.0), "normal", CLARO),
    ("GÁS", ("GÁS",), (2599.0, 392.0), "normal", CLARO),
    ("BANHO GOURMET", ("BANHO GOURMET", "A: 8,51 m²"), (1628.0, 395.0), "normal", CLARO),
    ("GOURMET", ("GOURMET", "A: 25,51 m²"), (1570.0, 572.0), "normal", CLARO),
    ("COZINHA", ("COZINHA", "A: 25,49 m²"), (1953.0, 572.0), "normal", CLARO),
    ("ÁREA DE SERVIÇO", ("ÁREA DE SERVIÇO", "A: 16,82 m²"), (2370.5, 437.0), "normal", CLARO),
    ("GARAGEM", ("GARAGEM", "A: 62,95 m²"), (2893.5, 437.0), "normal", CLARO),
    ("LOUCEIRO", ("LOUCEIRO", "A: 2,73 m²"), (2134.5, 437.0), "pequeno", CLARO),
    ("DESPENSA", ("DESPENSA", "A: 2,59 m²"), (2134.5, 611.0), "pequeno", CLARO),
    ("DCE TÉRREO", ("DCE TÉRREO", "A: 6 m²"), (2525.0, 588.0), "normal", ESCURO),
    # o WC DCE no espaço livre de cima (entre a bacia e o box), e não dentro do box
    ("WC DCE TÉRREO", ("WC DCE", "TÉRREO", "A: 3,75 m²"), (2446.0, 577.0), "pequeno", ESCURO),
    ("ÁREA DESCOBERTA", ("ÁREA DESCOBERTA",), (2281.0, 634.0), "normal", CLARO),
]
# as manchas do piso antigo (os quadradinhos bege) no piso de quartzito do WC DCE: px (a caixa do banho), o que é
# bege e pequeno sai pelo inpaint (a barra de toalha, comprida, fica)
WC_DCE_MANCHAS = {"caixa": (2386, 528, 2476, 668), "rb": 22, "lum": (140, 235), "area_max": 60, "lado_max": 12}
# os restos do rótulo do motor que a busca não pega (os pontinhos claros à esquerda do "A:" do JARDIM da sala íntima,
# px): o que é claro sai pelo inpaint (a grama em volta)
RESIDUOS_T = [((1595, 1712, 1609, 1731), 150)]


def fonte():
    from rodape_entrega import FONTES
    return str(FONTES / "Inter-Regular.otf")


def linhas(q=ROTULOS_T):
    """[(nome, [(texto, fonte, corpo, meio x, base)], cor)]: os rótulos da tabela."""
    f = fonte()
    out = []
    for nome, ls, (cx, b0), tam, cor in q:
        corpo, e = CORPOS[tam]
        out.append((nome, [(t, f, corpo, cx, b0 + i * e) for i, t in enumerate(ls)], list(cor)))
    return out


def _camadas_antes(img):
    """As camadas (alfa, cor) dos rótulos de antes: os que a revisão de 15/11 escreveu, o ² do SPA e os do motor (a busca
    da opção B), fora as descrições das escadas."""
    import biblioteca_terreo_casad_1511 as TD
    import rotulos_kalam_casac as KC
    import rotulos_kalam_casad as KD
    forma = img.shape[:2]
    camadas, caixas = [], []
    for nome, ll, cor in KD.escritos_1511("Terreo"):
        if nome.startswith("escada"):
            continue
        a = KC._alfa_texto_linhas(ll, forma, None)
        camadas.append((a, tuple(cor)))
        ys, xs = np.nonzero(a > 0.02)
        caixas.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    q = TD.SPA_M2
    camadas.append((KC._alfa_texto_linhas([("²", fonte(), q["corpo"], q["cx"], q["base"])], forma, None),
                    tuple(q["cor"])))
    KC.quadro = KD.quadro
    with contextlib.redirect_stdout(io.StringIO()):
        _, rots = KC.achar("Terreo", img)
    for b in rots:
        if b["nome"] in KD.REESCRITOS_T or b["nome"].startswith("escada"):
            continue
        ys, xs = np.nonzero(b["_alfa"] > 0.02)
        c_ = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        if any(min(c_[2], c[2]) > max(c_[0], c[0]) and min(c_[3], c[3]) > max(c_[1], c[1]) for c in caixas):
            continue
        camadas.append((b["_alfa"], tuple(b["cor"])))
    return camadas


def manchas_wc_dce(img, q=WC_DCE_MANCHAS):
    x0, y0, x1, y1 = q["caixa"]
    reg = img[y0:y1, x0:x1]
    I = reg.astype(np.int16)
    lum = I.mean(axis=2)
    bege = ((I[..., 2] - I[..., 0]) > q["rb"]) & (lum > q["lum"][0]) & (lum < q["lum"][1])
    n, lab, st, _ = cv2.connectedComponentsWithStats(bege.astype(np.uint8), connectivity=8)
    m = np.zeros(bege.shape, np.uint8)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a <= q["area_max"] and max(w, h) <= q["lado_max"]:
            m[lab == i] = 255
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    out = img.copy()
    out[y0:y1, x0:x1] = cv2.inpaint(np.ascontiguousarray(reg), m, 3, cv2.INPAINT_TELEA)
    return out, int((m > 0).sum())


def residuos(img, q=RESIDUOS_T):
    out = img.copy()
    for (x0, y0, x1, y1), lum in q:
        reg = np.ascontiguousarray(out[y0:y1, x0:x1])
        m = cv2.dilate((reg.astype(np.int16).mean(axis=2) > lum).astype(np.uint8) * 255, np.ones((3, 3), np.uint8))
        out[y0:y1, x0:x1] = cv2.inpaint(reg, m, 3, cv2.INPAINT_TELEA)
    return out


def aplicar(img):
    import revisao_terreo_casac_1411 as R14
    import rotulos_kalam_casac as KC
    camadas = _camadas_antes(img)
    out = KC.apagar(img, camadas)
    out, n = manchas_wc_dce(out)
    out = residuos(out)
    for _, ll, cor in linhas():
        out = R14.desenhar_linhas(out, ll, tuple(cor))
    print(f"    rótulos: os {len(camadas)} de antes saem; os {len(ROTULOS_T)} do padrão (Inter, 8 px de maiúscula, 7 nos "
          f"ambientes pequenos; as fileiras alinhadas); o piso do WC DCE sem as manchas bege ({n} px)")
    return out

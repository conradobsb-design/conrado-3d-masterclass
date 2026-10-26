#!/usr/bin/env python3
"""A final do 1º Pavimento da Casa A refeita na resolução da prancha (3840 px, ~59,7 px/m), com a auditoria de 26/10/26.

A lista do 1º Pavimento apresentada ao usuário (mapa `renders/POE642_CasaA_PH_1Pavimento_auditoria_2610_v2.jpg`) e
aprovada, com as respostas dele (26/10/26): "A. Sim." (os banhos 1, 2, 3 e master com a bancada em travertino bruto um
pouco mais escuro que o piso) e "B. mantem"; depois, no mesmo dia: "No banho 1 e 2 e 3 e master, a(s) cuba(s) é(são) em
mármore travertino bruto e o sanitário branco. No banho serviço a cuba é branca, com bancada da pia em marrom granito e
sanitário branco." (o B. serviço como o banho de serviço do Subsolo aprovado):
1. as paredes em cinza 80 (E10);
2. a escada em U sem os triângulos e sem linhas, os degraus marcados pelo sombreamento, com o D do PDF; os degraus 1 a 7
   do Térreo novo (E3, E8);
3. a caracol da saleta, idem (E3, E8);
4. o armário do quarto de serviço com os cabides (E2);
5. os boxes em vidro contínuo com o trilho (E5);
6. os chuveiros pelo PDF, no padrão do Subsolo e do Térreo;
7. os rótulos BANHO 3 e B. SERVIÇO longe da linha do box; SALA ÍNTIMA fora do tapete (E7);
8. as bancadas dos banhos mais marcadas que o piso (E9; resposta A), as cubas em travertino bruto e os vasos brancos;
   no B. serviço, a bancada em granito marrom, a cuba branca e o vaso branco;
9. os pisos na escala (E11): travertino bruto (circulação, sala íntima, banhos), o vinílico nas réguas das Casas B a D,
   o Bege Bahia na escala (quarto de serviço, saleta, B. serviço; as varandas ficam);
10. a linha tracejada da suíte master e do banho master (tida como espúria): no PDF, é o contorno de dentro da cobertura
    (ARQ_CONTRAPISO, x = 1281,4 pt); fica, como projeção (perguntado, o usuário respondeu "mantem");
11. as projeções tracejadas evidentes, em preto nos fundos claros e em branco nos escuros (R8);
12. o Térreo nublado refeito a partir do Térreo novo; na descida da escada em U, a linha de corte do Térreo (a diagonal)
    desenhada e a parte do Térreo nublada (usuário, 26/10/26).
Em toda troca de piso, a limpeza dos contornos do Térreo (seção 3 das regras).

A imagem de partida é a do pavimento com os ajustes no quadro de 3840 px, antes do Térreo nublado
(`rotulos_casaa.no_quadro_fixo`, com a pegada, as janelas e a troca do Térreo); o Térreo nublado entra no fim, a partir da
final nova do Térreo (`final3840_casaa_terreo.py`), sem as letras das escadas, a seta e os rótulos.

Uso (da pasta POE642_CasaA/scripts/):
  python3 final3840_casaa_1pav.py                  # a final do 1º Pavimento com os rótulos
  python3 final3840_casaa_1pav.py --de escada_u    # recomeça de uma etapa (as anteriores ficam em cache)
  python3 final3840_casaa_1pav.py --ate pisos      # para numa etapa
  python3 final3840_casaa_1pav.py --de rotulos --antes antes.png   # e os antes e depois de cada item
Saída: `renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png`, que vai ao `rodape_entrega.py --no-quadro`.
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casaa as FA                     # noqa: E402
import final3840_casaa_terreo as T               # noqa: E402

F, A, AJ = FA.F, FA.A, FA.AJ
CASA, ETAPAS, PT_PX = FA.CASA, FA.ETAPAS, FA.PT_PX
tela, sombra_q, ret_aa = FA.tela, FA.sombra_q, FA.ret_aa
perto_de, caixas, nconv2 = T.perto_de, T.caixas, T.nconv2


# ----------------------------------------------------------------------------------------------------------------------
# 0. A partida: a imagem com os ajustes do pavimento no quadro (o afim da aprovada), antes do Térreo nublado, e as
# máscaras levadas pelo mesmo afim (a pegada do pavimento, as janelas e a troca do Térreo), em cache.
def inicial(Q):
    from PIL import Image
    ETAPAS.mkdir(parents=True, exist_ok=True)
    c, cm = ETAPAS / "1Pavimento_ini.png", ETAPAS / "1Pavimento_mascaras.npz"
    if c.exists() and cm.exists():
        z = np.load(cm)
        Q.pegada, Q.janelas, Q.troca = z["pegada"], z["janelas"], z["troca"]
        return cv2.imread(str(c))
    q = A.PAVIMENTOS["1Pavimento"]
    img, peg, (jan, tro) = A.no_quadro_fixo(
        Image.open(CASA / q["render"]).convert("RGB"), Image.open(CASA / q["aprovada"]).convert("RGB"), Q.base,
        "1Pavimento", mascara=cv2.imread(str(CASA / q["nublado"]), cv2.IMREAD_GRAYSCALE),
        extras=[cv2.imread(str(CASA / m), cv2.IMREAD_GRAYSCALE) for m in q["terreo"]])
    Q.pegada, Q.janelas, Q.troca = peg, jan, tro
    np.savez_compressed(cm, pegada=peg, janelas=jan, troca=tro)
    cv2.imwrite(str(c), img)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os pisos na escala (item 9, E11), cada um na sua cor da base chapada, só dentro da pegada do pavimento, com a limpeza
# dos contornos do Térreo (até a borda de cada peça, px a px: `T.alfa_objetos`; a sombra passa como luz; as peças
# cheias da base, as esquadrias e as portas ficam; os px de traço da base entram; a divisa com o outro piso fica):
# - o travertino bruto do Térreo e do Subsolo na circulação, na sala íntima e nos banhos 1, 2, 3 e master (eram o
#   travertino antigo, rosado); nos banhos, as bancadas, as cubas, os vasos e os chuveiros a refazer (`refaz`) viram piso
#   antes, e as linhas dos boxes antigos (finas e compridas, ao longo dos boxes do PDF, `boxes_px`) também;
# - o vinílico nas réguas das Casas B a D (`retoque_1pav_casae.reguas_vinilico`, ~10 a 12 cm, com as emendas), no tom do
#   vinílico de hoje, nas suítes e nos closets (eram as réguas largas e borradas do render de 2000 px);
# - o Bege Bahia das Casas B a D na escala, no tom das varandas (o padrão do Bege Bahia), no quarto de serviço, na saleta
#   e no B. serviço (os pisos ligados aos `sementes`); as varandas ficam.
PISOS_1P = {
    "travertino": {"cores": [(202, 217, 220)], "fechar": 3, "area_obj": 40, "sig_luz": 0.8, "sig_base_m": 0.8,
                   "limiar": 0.05, "sig_m": 3.0, "semente": 2720,
                   "alfa": dict(T.TRAV_T["alfa"])},
    "vinilico": {"cores": [(79, 120, 168), (97, 128, 158)], "fechar": 3, "area_obj": 40, "sig_luz": 1.2,
                 "sig_base_m": 0.8, "limiar": 0.12, "sig_m": 2.0, "semente": 2721,
                 "alfa": dict(T.TRAV_T["alfa"], croma=(0.03, 0.06), claro=(1.08, 1.15), escuro=(0.55, 0.45),
                              buraco_max=4000, forte=(0.08, 1.18, 0.5), fraca=(0.02, 0.04, 1.14))},
    "bege": {"cores": [(232, 232, 232)], "fechar": 3, "area_obj": 40, "sig_luz": 0.8, "sig_base_m": 0.8,
             "limiar": 0.05, "sig_m": 2.0, "semente": 2722, "contraste": 0.55,
             "sementes": [(1960, 1400), (2040, 1580), (2200, 1520)],
             "alfa": dict(T.TRAV_T["alfa"])},
}
# as peças brancas que ficam (quadro): a banheira do master tem a borda de cima clara como o travertino novo, e o alfa a
# tomava por piso; a mancha clara e neutra (sem o rosa do piso de hoje) que contém a semente fica inteira
PECAS_BRANCAS_1P = {"banheira master": (1460, 1500), "min": 150, "croma": 10}
# as peças dos banhos que são refeitas (pt): as bancadas, os vasos e os chuveiros (com `refaz_px` de folga)
BANHOS_1P = {
    "master": {"bancada": (1332.7, 1741.2, 1463.1, 1775.2),
               "cubas": [{"cuba": (1351.5, 1745.7, 1382.1, 1767.8), "bacia": (1352.6, 1746.8, 1380.9, 1766.7),
                          "torneira": (1365.7, 1761.7, 1367.8, 1769.0), "base": (1366.75, 1770.05, 1.5)},
                         {"cuba": (1413.8, 1745.7, 1444.4, 1767.8), "bacia": (1414.9, 1746.8, 1443.3, 1766.7),
                          "torneira": (1428.1, 1761.7, 1430.2, 1769.0), "base": (1429.15, 1770.05, 1.5)}],
               "vaso": ((1486.8, 1740.4, 1506.8, 1769.5), "baixo"),
               "chuveiros": [{"ducha": (1225.1, 1738.4, 1236.3, 1749.6)}, {"ducha": (1293.1, 1738.4, 1304.3, 1749.6)}],
               "registros": [(1229.3, 1771.0, 1232.1, 1775.2), (1297.3, 1771.0, 1300.2, 1775.2)]},
    "banho 1": {"bancada": (2250.8, 1398.2, 2284.8, 1483.2),
                "cubas": [{"cuba": (2255.4, 1433.9, 2277.5, 1464.5), "bacia": (2256.5, 1435.0, 2276.3, 1463.4),
                           "torneira": (2271.4, 1448.1, 2278.6, 1450.2), "base": (2279.75, 1449.2, 1.5)}],
                "vaso": ((2255.7, 1365.5, 2284.8, 1385.5), "direita"),
                "chuveiros": [{"ducha": (2212.6, 1303.8, 2223.8, 1315.0), "braco": (2217.5, 1288.2, 2218.9, 1310.6),
                               "canopla": (2216.5, 1287.6, 2219.9, 1288.2)}]},
    "banho 2": {"bancada": (1522.3, 1072.2, 1590.4, 1106.2),
                "cubas": [{"cuba": (1541.0, 1079.6, 1571.6, 1101.7), "bacia": (1542.2, 1080.7, 1570.5, 1100.5),
                           "torneira": (1555.3, 1078.0, 1557.4, 1085.6), "base": (1556.35, 1077.3, 1.5)}],
                "vaso": ((1489.6, 1072.2, 1509.7, 1101.3), "cima"),
                "chuveiros": [{"ducha": (1437.4, 1088.4, 1448.6, 1099.6), "braco": (1442.2, 1072.8, 1443.7, 1095.1),
                               "canopla": (1441.3, 1072.2, 1444.7, 1072.8)}]},
    "banho 3": {"bancada": (1834.1, 579.0, 1902.2, 613.0),
                "cubas": [{"cuba": (1852.9, 586.4, 1883.5, 608.4), "bacia": (1854.0, 587.5, 1882.3, 607.3),
                           "torneira": (1867.1, 584.5, 1869.2, 592.4), "base": (1868.15, 584.05, 1.5)}],
                "vaso": ((1914.8, 579.0, 1934.9, 608.1), "cima"),
                "chuveiros": [{"ducha": (1975.9, 630.0, 1987.1, 641.2)}],
                "registros": [(2007.5, 660.3, 2011.6, 667.7)]},
    # o B. serviço como o banho de serviço do Subsolo (usuário, 26/10/26): a bancada em granito marrom (o polígono do
    # PDF, com o recorte da cuba de semiencaixe), a cuba branca, a torneira na borda de trás (a bica sobre a bacia), o
    # vaso branco e a descarga na parede
    "B. serviço": {"bancada": (1990.0, 1678.8, 2012.7, 1718.5), "pedra": "granito",
                   "cubas": [{"cuba": (1983.3, 1687.3, 2005.9, 1709.9), "torneira": (1994.6, 1697.9, 2003.0, 1699.4),
                              "base": (2003.0, 1698.65, 1.4)}],
                   "vaso": ((1981.6, 1646.9, 2012.7, 1668.2), "direita"), "descarga": (2010.2, 1654.4, 2012.7, 1660.7),
                   "chuveiros": [{"ducha": (2001.9, 1611.8, 2005.7, 1615.4),
                                  "braco": (2004.7, 1613.0, 2012.1, 1614.2), "canopla": (2012.1, 1612.2, 2012.7, 1615.0)}]},
    "refaz_px": 6, "boxes_px": 12, "sobra_px": 14,
}


def pecas_brancas(im):
    q = PECAS_BRANCAS_1P
    neutro = ((im.min(axis=2) > q["min"]) & (np.ptp(im, axis=2) < q["croma"])).astype(np.uint8)
    _, lab = cv2.connectedComponents(neutro, connectivity=8)
    m = np.zeros(neutro.shape, bool)
    for v in q.values():
        if isinstance(v, tuple) and lab[v[1], v[0]] > 0:
            m |= lab == lab[v[1], v[0]]
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    return T.manchas(m, 1, 10 ** 6)


def refaz_banhos(Q):
    rets = []
    for b in BANHOS_1P.values():
        if not isinstance(b, dict):
            continue
        rets += [b["bancada"]] if "bancada" in b else []
        rets += [c["cuba"] for c in b.get("cubas", [])]
        rets += [b["vaso"][0]] if "vaso" in b else []
        rets += [c["ducha"] for c in b.get("chuveiros", [])]
    return caixas(Q, rets, BANHOS_1P["refaz_px"]) & (FA.paredes_pdf(Q) < 0.5)


def faixas_boxes(Q):
    """As faixas em volta dos boxes do PDF (as folhas e o trilho, com `boxes_px`), cada uma com o sentido do box."""
    out = []
    for b in AJ.folhas_box(Q.pg):
        a0 = min(min(f[0] if b["hor"] else f[1] for f in b["folhas"]), min(t[0] for t in b["trilho"]))
        a1 = max(max(f[2] if b["hor"] else f[3] for f in b["folhas"]), max(t[1] for t in b["trilho"]))
        r = (a0, b["meio"], a1, b["meio"]) if b["hor"] else (b["meio"], a0, b["meio"], a1)
        out.append((caixas(Q, [r], BANHOS_1P["boxes_px"]), b["hor"]))
    return out


def textura_piso(Q, nome, h, w, semente, tom):
    if nome == "travertino":
        return T.travertino_t(Q, h, w, semente)
    if nome == "bege":
        D = T.bege_bahia(Q, h, w, semente) / np.float32(FA.PISOS_A["Bege Bahia"]["tom"])
        return (1 + PISOS_1P["bege"]["contraste"] * (D - 1)) * np.float32(tom)
    from retoque_1pav_casae import reguas_vinilico
    rr = np.random.default_rng(semente)
    veio = cv2.GaussianBlur(rr.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.30 * Q.px_m, sigmaY=0.7)
    veio = 1 + 0.035 * veio / max(veio.std(), 1e-6)
    D = reguas_vinilico(h, w, Q.px_m, veio, np.ones((h, w), bool), np.random.default_rng(semente))
    return np.float32(tom) * (D / max(float(D.mean()), 1e-6))[..., None]


def cor_piso(Q, nome):
    q = PISOS_1P[nome]
    m = np.zeros((Q.H, Q.W), bool)
    for c in q["cores"]:
        m |= np.all(Q.chapada == np.uint8(c), axis=2)
    m = F.fechar(m, q["fechar"]) & (Q.pegada > 127)
    if q.get("sementes"):
        n, lab = cv2.connectedComponents(m.astype(np.uint8), connectivity=4)
        m = np.isin(lab, [lab[y, x] for x, y in q["sementes"] if lab[y, x] > 0])
    return m


def trocar_piso(Q, img, nome, outros):
    q = PISOS_1P[nome]
    im = img.astype(np.float32)
    ch = cor_piso(Q, nome)
    cru = ch.copy()
    branco = np.all(Q.chapada == 255, axis=2) & perto_de(ch, 7)
    vizinho = perto_de(outros, 2) & ~cru                    # a divisa com o outro piso fica (a outra troca a faz)
    refaz = (refaz_banhos(Q) & perto_de(ch, 7)) if nome in ("travertino", "bege") else np.zeros_like(ch)
    onde = (ch | branco | refaz | T.traco_chapada(Q, ch)) & (FA.paredes_pdf(Q) < 0.5) & ~vizinho
    L = F.luz_robusta(im, ch & ~perto_de(branco, 2), 1.0 * Q.px_m)
    lum = im.mean(axis=2)
    a = T.alfa_objetos(im, L, onde, q["area_obj"], q["alfa"])
    # no Térreo, os traços da DOC_LINHAS ficavam com o piso antigo (até o redesenho); aqui os que ficam na pegada são
    # todos redesenhados nas projeções, e os do render, com o piso antigo, viravam tracinhos claros junto às guardas
    a[T.pecas_cheias(Q) & ~refaz] = 1
    if nome == "travertino":
        a[pecas_brancas(im)] = 1
    if refaz.any():
        # as louças antigas que passam da caixa a refazer (o motor as desenhou fora do lugar do PDF): as manchas de
        # objeto que tocam a caixa e cabem nela com `sobra_px` de folga
        perto_r = perto_de(refaz, BANHOS_1P["sobra_px"])
        n, lab, st, _ = cv2.connectedComponentsWithStats((onde & (a >= 0.5)).astype(np.uint8), 8)
        toca = np.unique(lab[refaz & (lab > 0)])
        for i in toca:
            mi = lab == i
            if not (mi & ~perto_r).any():
                a[perto_de(mi, 1) & onde] = 0
                refaz |= mi
        # as linhas dos boxes antigos: o que é objeto, fino e comprido ao longo do box, vira piso
        for faixa, hor in faixas_boxes(Q):
            obj = (onde & faixa & (a > 0.12)).astype(np.uint8)
            n, lab, st, _ = cv2.connectedComponentsWithStats(obj, 8)
            for i in range(1, n):
                w_, h_ = st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
                if (hor and h_ <= 5 and w_ >= 12) or (not hor and w_ <= 5 and h_ >= 12):
                    a[perto_de(lab == i, 1) & onde] = 0
    a[refaz] = 0
    # em volta das peças refeitas, a sombra das antigas sai (as novas trazem a sua)
    halo = (perto_de(refaz, BANHOS_1P["sobra_px"]) & ~refaz & onde & (a < 0.5)) if refaz.any() else refaz
    limpo = onde & (a < 0.5) & ~refaz & ~halo
    mf = limpo.astype(np.float32)
    perto = nconv2(lum, mf, q["sig_luz"], onde=onde)
    base = nconv2(lum, mf, q["sig_base_m"] * Q.px_m)
    larga = nconv2(lum, mf, q["sig_m"] * Q.px_m)
    k = larga / np.median(larga[limpo])
    sh = np.clip(perto / np.maximum(base, 1) + q["limiar"], 0, 1) * k
    liso = refaz | halo
    if liso.any():
        # a luz ali continua a do piso limpo de volta (inpaint só a partir dele: paredes e peças não entram)
        ys, xs = np.nonzero(perto_de(liso, 6))
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        lp = lum.copy()
        lp[y0:y1, x0:x1] = cv2.inpaint(np.clip(lum[y0:y1, x0:x1], 0, 255).astype(np.uint8),
                                       (~limpo[y0:y1, x0:x1]).astype(np.uint8), 5, cv2.INPAINT_TELEA).astype(np.float32)
        lp = cv2.GaussianBlur(lp, (0, 0), 1.5)
        sh[liso] = (np.clip(lp / np.maximum(base, 1) + q["limiar"], 0, 1) * k)[liso]
    tom = np.median(im[limpo & cru & ~perto_de(~cru, 6)], axis=0)
    m = onde & (a < 1)
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    novo = im.copy()
    novo[y0:y1, x0:x1] = textura_piso(Q, nome, y1 - y0, x1 - x0, q["semente"], tom) * sh[y0:y1, x0:x1, None]
    a3 = np.where(m, a, 1)[..., None]
    out = im * a3 + novo * (1 - a3)
    print(f"    {nome}: {(m & (a < 0.5)).sum() / Q.px_m ** 2:.1f} m² de piso novo, até a borda das peças (as peças ficam: "
          f"{(onde & (a >= 0.5)).sum() / Q.px_m ** 2:.1f} m²); tom {tuple(int(v) for v in tom)}")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def pisos(Q, img):
    cores = {n: cor_piso(Q, n) for n in PISOS_1P}
    out = img
    for nome in PISOS_1P:
        outros = np.zeros_like(cores[nome])
        for n2, m2 in cores.items():
            if n2 != nome:
                outros |= m2
        out = trocar_piso(Q, out, nome, outros)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 2. O armário do quarto de serviço (item 4, E2): o retângulo com a diagonal da DOC_LINHAS (0,60 x 2,60 m, junto à parede
# do B. serviço) aberto, visto de cima, com os cabides e o cabideiro de metal, como os guarda-roupas dos closets da Casa A
# e o do quarto do motorista do Térreo (`elementos.guarda_roupa`, os tons da Casa E), com as portas do lado do quarto
# (à esquerda) e a sombra curta no piso.
ARMARIO = {"armario": (1890.8, 1491.7, 1924.8, 1639.1), "portas": "esquerda", "sombra": 0.30, "ss": 4, "semente": 43}


def armario(Q, img):
    guardar = dict(T.MOTORISTA)
    try:
        T.MOTORISTA.update(ARMARIO)
        out = guarda_roupa(Q, img)
    finally:
        T.MOTORISTA.clear()
        T.MOTORISTA.update(guardar)
    return out


def guarda_roupa(Q, img):
    """O guarda-roupa de `T.MOTORISTA` (a primeira metade de `T.motorista`, sem o box)."""
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from elementos import guarda_roupa as gr
    from retoque_1pav_casae import GUARDA_ROUPAS
    q = T.MOTORISTA
    out = np.ascontiguousarray(img.copy())
    r = q["armario"]
    tl = tela(out, Q, r, folga=6)
    sombra_q(tl, tl.ret(r), forca=q["sombra"], dist=1.4, sigma=1.4)
    out = tl.gravar()
    x0, y0, x1, y1 = r
    (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
    S = q["ss"]
    comp, prof = max(x1 - x0, y1 - y0) / 56.69, min(x1 - x0, y1 - y0) / 56.69
    cor, alfa = gr(comp, prof, Q.px_m * S, semente=q["semente"], miolo=GUARDA_ROUPAS["miolo"],
                   moldura=GUARDA_ROUPAS["moldura"], barra=True)
    k = {"baixo": 0, "direita": 1, "cima": 2, "esquerda": 3}[q["portas"]]
    cor, alfa = np.ascontiguousarray(np.rot90(cor, k)), np.ascontiguousarray(np.rot90(alfa, k))
    X0, Y0, X1, Y1 = int(np.floor(u0)), int(np.floor(v0)), int(np.ceil(u1)), int(np.ceil(v1))
    tw, th = int(round((u1 - u0) * S)), int(round((v1 - v0) * S))
    ox, oy = int(round((u0 - X0) * S)), int(round((v0 - Y0) * S))
    grande = np.zeros(((Y1 - Y0) * S, (X1 - X0) * S, 3), np.float32)
    ag = np.zeros(grande.shape[:2], np.float32)
    grande[oy:oy + th, ox:ox + tw] = cv2.resize(cor, (tw, th), interpolation=cv2.INTER_AREA)
    ag[oy:oy + th, ox:ox + tw] = cv2.resize(alfa, (tw, th), interpolation=cv2.INTER_AREA)
    cr = cv2.resize(grande, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    ar = cv2.resize(ag, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - ar) + cr, 0, 255).astype(np.uint8)
    print(f"    armário com os cabides e o cabideiro ({comp:.2f} x {prof:.2f} m), portas à {q['portas']}")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 3. Os banhos (itens 5, 6 e 8; resposta A do usuário: "Sim."), pelo PDF: a bancada no travertino bruto mais marcado das
# bancadas (um pouco mais escuro que o piso, com a borda no tom escurecido da pedra e a sombra curta, E9); a cuba
# esculpida no mesmo travertino bruto (usuário, 26/10/26: "a(s) cuba(s) é(são) em mármore travertino bruto"), com a borda
# um pouco mais clara, a bacia mais funda com a sombra por dentro e o contorno no tom escurecido da pedra (`TRAV_CUBA`,
# a rotina da cuba de granito, `FA.cuba_pedra`), e a torneira cromada; o vaso em louça branca ("o sanitário branco");
# os chuveiros na placa cromada com os furinhos (os de teto sem o braço; o registro na parede); as muretas do banho
# master (a do box e a do WC, cinza da ARQ_BANCADAS no PDF) em cinza 80, como as paredes; os boxes do PDF em vidro
# contínuo, com a sombra curta e o trilho no vão (`FA.boxes`, os cinco do pavimento). O B. serviço (`"pedra":
# "granito"`) como o banho de serviço do Subsolo aprovado: a bancada em granito marrom no polígono do PDF, a cuba branca
# de semiencaixe, o vaso branco e a descarga.
TRAV_CUBA = dict(FA.GRANITO_CUBA, rim=1.05, bacia=0.82, sombra_bacia=(0.36, 2.2), contorno=(104, 117, 133))
MURETAS = [(1330.5, 1712.8, 1332.7, 1775.2), (1463.4, 1693.0, 1465.6, 1776.9), (1465.6, 1693.0, 1479.8, 1695.2)]


def chuveiro(Q, out, c):
    """O chuveiro do PDF: com o braço e a canopla, como os do Subsolo; os de teto, só a placa."""
    if "braco" in c:
        return FA.chuveiro(Q, out, c)
    x0, y0, x1, y1 = c["ducha"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    meio = (cx - 0.3, cy - 0.3, cx + 0.3, cy + 0.3)
    return FA.chuveiro(Q, out, dict(c, braco=meio, canopla=meio))


def poligono_bancada(Q, r):
    """O polígono da bancada da ARQ_BANCADAS no PDF com o retângulo r (pt), com o recorte da cuba."""
    for d in Q.desenhos:
        k = d["rect"]
        if d.get("layer") == "ARQ_BANCADAS" and d["type"] in ("f", "fs") and \
                max(abs(k.x0 - r[0]), abs(k.y0 - r[1]), abs(k.x1 - r[2]), abs(k.y1 - r[3])) < 0.3:
            return [(p.x, p.y) for it in d["items"] for p in it[1:] if hasattr(p, "x")]
    return None


def banhos(Q, img):
    tb = FA.BANHOS["trav_bancada"]
    out = np.ascontiguousarray(img.copy())
    a = np.zeros((Q.H, Q.W), np.float32)
    for r in MURETAS:
        a = np.maximum(a, ret_aa(Q, r))
    out = np.clip(out * (1 - a[..., None]) + np.float32(FA.PAREDES_A["cor"]) * a[..., None], 0, 255).astype(np.uint8)

    def travertino(s):
        return lambda tl: np.float32(tb["tom"]) * FA.travertino_bruto(Q, tl.h, tl.w, s, **FA.TRAVERTINO["bancada"])[..., None]
    for i, (nome, b) in enumerate((k, v) for k, v in BANHOS_1P.items() if isinstance(v, dict)):
        feito = []
        if b.get("pedra") == "granito":
            out = FA.bancada_pedra(Q, out, b["bancada"], lambda tl, s=2730 + i: FA._granito(Q, tl, s), 0.62, 0.6, 0.34,
                                   poli=poligono_bancada(Q, b["bancada"]))
            for c in b["cubas"]:
                out = FA.cuba_branca(Q, out, c["cuba"])
                out = FA.torneira(Q, out, c["torneira"], c["base"])
            feito.append(f"bancada em granito marrom com {len(b['cubas'])} cuba(s) branca(s)")
        elif "bancada" in b:
            out = FA.bancada_pedra(Q, out, b["bancada"], travertino(2730 + i), tb["borda"], tb["larg"], tb["sombra"])
            for j, c in enumerate(b["cubas"]):
                out = FA.cuba_pedra(Q, out, c, travertino(2740 + 10 * i + j), TRAV_CUBA)
                out = FA.torneira(Q, out, c["torneira"], c["base"])
            feito.append(f"bancada em travertino bruto com {len(b['cubas'])} cuba(s) em travertino bruto")
        if "vaso" in b:
            out = FA.vaso(Q, out, b["vaso"][0], b["vaso"][1])
            feito.append("vaso branco")
        if "descarga" in b:
            out = FA.placa_cromada(Q, out, b["descarga"])
        for c in b.get("chuveiros", []):
            out = chuveiro(Q, out, c)
        for r in b.get("registros", []):
            out = FA.placa_cromada(Q, out, r)
        feito.append(f"{len(b.get('chuveiros', []))} chuveiro(s)")
        print(f"    {nome}: " + ", ".join(feito))
    return FA.boxes(Q, out)


# ----------------------------------------------------------------------------------------------------------------------
# 4. As paredes em cinza 80 (item 1, E10), como no Subsolo e no Térreo: os preenchimentos pretos da ARQ_PAREDE do PDF,
# com antialias, e a franja preta antiga em volta (o que passa do PDF) refeita com o que está em volta. Sem o limite de
# tamanho do Térreo (lá, as faixas de mais de 300 pt eram os muros do lote): aqui, as paredes compridas da suíte master,
# do banho master e da sala íntima são preenchimentos de mais de 300 pt e ficavam pretas.
PAREDES_1P = dict(FA.PAREDES_A, divisoria=None, encostos=[], max_pt=np.inf)


def paredes(Q, img):
    return FA.paredes(Q, img, PAREDES_1P)


# ----------------------------------------------------------------------------------------------------------------------
# 5. As escadas (itens 2 e 3, E3, E8): sem os triângulos (R14) e sem linhas (usuário, 26/10/26: "não precisa constar
# linhas, mas sim sombras denotando que o sentido é de subida"), como as do Térreo novo: cada degrau um pouco mais claro
# que o de baixo e a sombra curta de cada espelho no degrau de baixo; o D do PDF em Inter SemiBold (`T.letra`).
# 5a. A escada em U: do 1º Pavimento, ela desce (o D no degrau 19, junto ao piso da circulação): o lance de baixo da
# esquerda para a direita (19 a 11), o patamar (10) e o lance de cima da direita para a esquerda (9 a 1). Os degraus 1 a
# 7, até o corte do Térreo, são o Térreo nublado (no fim, `nublado`, recortados pela linha de corte); do 8 ao 19, o travertino bruto do piso, no tom do
# piso em volta (o degrau 19 no tom do piso, os de baixo um pouco mais escuros). O vão entre os lances fica (o Térreo
# nublado), com o contorno fino; as linhas de percurso, os bocéis e o triângulo saem.
ESCADA_U_1P = {"lanco1": (2021.22, 1094.86, 2174.3, 1162.89), "patamar": (2174.3, 1094.86, 2242.33, 1253.6),
               "lanco2": (2019.52, 1185.57, 2174.3, 1253.6),
               "espelhos1": [2021.22, 2038.23, 2055.24, 2072.25, 2089.26, 2106.26, 2123.27, 2140.28, 2157.29, 2174.3],
               "espelhos2": [2174.3, 2157.29, 2140.28, 2123.27, 2106.26, 2089.26, 2072.25, 2055.24, 2038.23, 2019.52],
               "piso_ref": (1985.0, 1190.0, 2012.0, 1250.0),       # pt: o travertino da circulação, à esquerda
               "tom": (0.88, 1.0), "tom_degrau": 0.015, "espelho": T.ESCADA_U["espelho"], "semente": 2750,
               "contorno": ((132, 138, 147), 0.9), "texto": "D", "centro": ((2019.52 + 2038.23) / 2, 1219.58)}


def escada_u(Q, img):
    q = ESCADA_U_1P
    l1, pa, l2 = q["lanco1"], q["patamar"], q["lanco2"]
    caixa = (l2[0], l1[1], pa[2], l2[3])
    out = np.ascontiguousarray(img.copy())
    tl = tela(out, Q, caixa, folga=4)
    X, Y = tl.grade()
    a = np.maximum.reduce([tl.reduzir(tl.ret(r)) for r in (l1, pa, l2)])
    # o degrau (1 a 19) e o espelho do degrau de cima de cada px
    s = np.zeros(X.shape, np.int32)
    d_esp = np.full(X.shape, np.inf)
    e1, e2 = q["espelhos1"], q["espelhos2"]
    em1 = (Y >= l1[1]) & (Y <= l1[3]) & (X < l1[2])
    for k in range(9):
        m = em1 & (X >= e1[k]) & (X < e1[k + 1]) if k else em1 & (X < e1[1])
        s[m], d_esp[m] = k + 1, (e1[k + 1] - X[m]) * PT_PX
    mp = (X >= pa[0])
    s[mp] = 10
    dp = np.where((Y >= l2[1]) & (Y <= l2[3]), (X - pa[0]) * PT_PX, np.inf)
    d_esp[mp] = dp[mp]
    em2 = (Y >= l2[1]) & (X < pa[0]) & ~em1
    for j in range(9):
        m = em2 & (X <= e2[j]) & (X > e2[j + 1]) if j < 8 else em2 & (X <= e2[j])
        s[m], d_esp[m] = 11 + j, (X[m] - e2[j + 1]) * PT_PX       # o 19: o espelho é a borda do piso
    t0, t1 = q["tom"]
    rng = np.random.default_rng(q["semente"])
    tons = 1 + rng.uniform(-q["tom_degrau"], q["tom_degrau"], 20)
    tons[19] = 1.0
    fs, alc = q["espelho"]
    f = (t0 + (t1 - t0) * (np.clip(s, 1, 19) - 1) / 18) * tons[np.clip(s, 1, 19)]
    f *= 1 - fs * np.exp(-np.maximum(d_esp, 0) / alc)
    # o travertino bruto, no tom do piso em volta (o degrau 19 = o piso)
    (u0, v0), (u1, v1) = Q.p2q(*q["piso_ref"][:2]), Q.p2q(*q["piso_ref"][2:])
    ref = img[int(v0):int(v1), int(u0):int(u1)].reshape(-1, 3).astype(np.float32).mean(axis=0)
    Tx = T.travertino_t(Q, tl.h, tl.w, q["semente"])
    Tx *= ref / Tx.reshape(-1, 3).mean(axis=0)
    tl.reg = tl.reg * (1 - a[..., None]) + Tx * f[..., None] * a[..., None]
    # o contorno do vão entre os lances, fino
    cor, larg = q["contorno"]
    c = tl.reduzir(tl.linha([(l1[0], l1[3]), (pa[0], l1[3]), (pa[0], l2[1]), (l2[0], l2[1])], larg))
    tl.reg = tl.reg * (1 - c[..., None]) + np.float32(cor) * c[..., None]
    out = tl.gravar()
    out = T.letra(Q, out, q["texto"], centro_q=Q.p2q(*q["centro"]))
    print(f"    escada em U: 19 degraus sem linhas e sem triângulo, em travertino bruto no tom do piso, com o "
          f"sombreamento de subida (os degraus 1 a 7 entram no Térreo nublado); o {q['texto']} no degrau 19")
    return out


# 5b. A caracol da saleta: o trecho do 1º Pavimento (o quarto cheio, de 0,6° a 93,1°, cinco degraus até o anel do
# corrimão, a 52 pt) no travertino e no tom da caracol do Térreo novo (`T.CARACOL`), sobe no sentido anti-horário
# (desce no horário, o D do PDF no degrau junto ao 0°): cada degrau um pouco mais claro que o de baixo e a sombra curta
# do espelho do de cima. O resto do círculo fica branco limpo, sem os bocéis (na final, o Térreo nublado, com a caracol
# dele por baixo); as guardas (a 0° e a 93,1°), o anel e o pilar ficam.
CARACOL_1P = {"centro": (1756.4, 1718.5), "r_pilar": 4.0, "r_anel": 52.0, "cheio": [0.6, 19.1, 37.6, 56.1, 74.6, 93.1],
              "tons": (0.88, 1.0), "guarda_px": 1.8, "branco": (250, 250, 250), "anel": ((147, 147, 147), 0.9),
              "semente": 2751, "texto": "D", "origem": (1782.3, 1714.6)}


def caracol(Q, img):
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from texturas import textura
    q, qt = CARACOL_1P, T.CARACOL
    cx, cy = q["centro"]
    R = q["r_anel"] + 4
    out = np.ascontiguousarray(img.copy())
    tl = tela(out, Q, (cx - R, cy - R, cx + R, cy + R), folga=3)
    # px: o pt de cada px (para o branco e as guardas)
    X, Y = tl.grade()
    r1 = np.hypot(X - cx, Y - cy)
    th1 = np.degrees(np.arctan2(-(Y - cy), X - cx)) % 360
    c0, c1 = q["cheio"][0], q["cheio"][-1]
    g = q["guarda_px"] / PT_PX
    guardas = np.zeros(X.shape, bool)
    for t in (0.0, c1):
        c, s_ = np.cos(np.radians(t)), np.sin(np.radians(t))
        guardas |= (np.abs((X - cx) * s_ + (Y - cy) * c) < g) & ((X - cx) * c - (Y - cy) * s_ > 0)
    guardas &= r1 > q["r_pilar"]
    L = tl.reg.mean(axis=2)
    vazio = ~((th1 >= c0 - 1) & (th1 <= c1 + 1)) & (r1 > q["r_pilar"] + 1.5 / PT_PX) & ~guardas & (
        (r1 < q["r_anel"] + 1.5 / PT_PX) | ((r1 < q["r_anel"] + 2.0 / PT_PX) & (L > 120)))
    tl.reg[vazio] = np.float32(q["branco"])
    # ss: o trecho cheio
    S = 8
    ys, xs = np.mgrid[0:tl.h * S, 0:tl.w * S].astype(np.float32)
    (ax, ay), (bx, by) = Q.q2p(tl.x0, tl.y0), Q.q2p(tl.x0 + 1, tl.y0 + 1)
    Xs, Ys = ax + (xs + 0.5) / S * (bx - ax), ay + (ys + 0.5) / S * (by - ay)
    r = np.hypot(Xs - cx, Ys - cy)
    th = np.degrees(np.arctan2(-(Ys - cy), Xs - cx)) % 360
    bordas = np.array(q["cheio"])
    k = np.clip(np.searchsorted(bordas, th) - 1, 0, len(bordas) - 2)
    n = len(bordas) - 1
    t0, t1 = q["tons"]
    f = t0 + (t1 - t0) * k / (n - 1)
    fs, alc = qt["espelho"]
    dist = (bordas[np.minimum(k + 1, n)] - th) * np.pi / 180 * r * PT_PX           # px até o espelho do de cima
    f = f * np.where(k < n - 1, 1 - fs * np.exp(-np.maximum(dist, 0) / alc), 1.0)
    cheio = (r >= q["r_pilar"]) & (r <= q["r_anel"]) & (th > c0) & (th < c1)

    def red(m):
        return cv2.resize(m.astype(np.float32), (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    a_cheio = red(cheio) * ~guardas
    fr = red(f * cheio) / np.maximum(red(cheio), 1e-4)
    Tx = textura("travertino", Q.px_m, tl.h, tl.w, semente=q["semente"]).astype(np.float32)
    Tx = (1 + qt["textura"] * (Tx / Tx.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(qt["tom"])
    tl.reg = tl.reg * (1 - a_cheio[..., None]) + (Tx * fr[..., None]) * a_cheio[..., None]
    # o anel do corrimão, inteiro, e o pilar preto
    cor, larg = q["anel"]
    an = red(np.abs(r - q["r_anel"]) <= larg / PT_PX / 2)
    tl.reg = tl.reg * (1 - an[..., None]) + np.float32(cor) * an[..., None]
    ap = red(r < q["r_pilar"])[..., None]
    tl.reg = tl.reg * (1 - ap) + np.float32(qt["pilar"]) * ap
    out = tl.gravar()
    out = T.letra(Q, out, q["texto"], origem_pt=q["origem"])
    print(f"    caracol: {n} degraus do 1º Pavimento sem linhas e sem triângulo, no travertino da caracol do Térreo, com o "
          f"sombreamento de subida; o resto do círculo em branco limpo (o Térreo nublado); o {q['texto']} do PDF")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 6. O Térreo nublado (item 12), refeito a partir da final nova do Térreo (`final3840_casaa_terreo.py`, as etapas até a
# caracol: sem as letras das escadas, as projeções, a seta e os rótulos), como `rotulos_casaa.nublar`: fora da pegada
# do pavimento; nas `janelas` (os vazios, o poço da escada em U e a abertura da caracol), onde é branco; e, inteiro, no
# trecho da escada em U que já é do Térreo.
# Usuário, 26/10/26: "na descida da escada U é preciso saber onde ela fica nevoada, já no terreo. representando aquela
# linha em diagonal e enovoar a parte que pertence ao terreo": o trecho do Térreo é o dos degraus 1 a 7 até a linha de
# corte do PDF do Térreo (a diagonal com a quebra em zigue-zague, ARQ_ESCADAS E RAMPAS), recortado por ela mesma (antes,
# a `troca` do ajuste de 2000 px, sem a quebra); por cima, a própria linha de corte, fina e em cinza escuro, de lado a
# lado do lance.
CORTE_U = {"linha": [(2122.99, 1094.86), (2138.38, 1125.07), (2146.88, 1125.07), (2133.68, 1132.68), (2142.18, 1132.68),
                     (2157.29, 1162.89)],                                          # pt, do PDF do Térreo
           "lado_terreo": [(2021.22, 1162.89), (2021.22, 1094.86)],                # o resto do trecho do Térreo
           "cor": (64, 64, 64), "larg_px": 1.2}
TERREO_ETAPAS = ("deck", "pisantes", "escada_u", "caracol")


def terreo_sem_letras():
    """A final nova do Térreo até a caracol, sem as letras das escadas (em cache)."""
    c, base = ETAPAS / "Terreo_nublado_base.png", ETAPAS / "Terreo_paredes.png"
    if c.exists() and base.exists() and c.stat().st_mtime >= base.stat().st_mtime:
        return cv2.imread(str(c))
    QT = FA.QuadroA("Terreo")
    if not base.exists():
        T.final_3840(salvar=False, ate="paredes")
    img = cv2.imread(str(base))
    letra = T.letra
    T.letra = lambda Q, out, *a, **k: out
    try:
        for nome, f in T.passos_terreo(QT, None):
            if nome in TERREO_ETAPAS:
                img = f(img)
    finally:
        T.letra = letra
    cv2.imwrite(str(c), img)
    return img


def corte_u(Q, ss=8):
    """O trecho da escada em U que é do Térreo (0 a 1, no quadro), recortado pela linha de corte."""
    q = CORTE_U
    pts = np.float32([Q.p2q(x, y) for x, y in q["linha"] + q["lado_terreo"]])
    x0, y0 = np.floor(pts.min(axis=0)).astype(int) - 2
    x1, y1 = np.ceil(pts.max(axis=0)).astype(int) + 2
    m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((pts - (x0, y0)) * ss))], 255)
    a = np.zeros((Q.H, Q.W), np.float32)
    a[y0:y1, x0:x1] = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    return a


def linha_corte(Q, img, ss=8):
    q = CORTE_U
    pts = np.float32([Q.p2q(x, y) for x, y in q["linha"]])
    x0, y0 = np.floor(pts.min(axis=0)).astype(int) - 3
    x1, y1 = np.ceil(pts.max(axis=0)).astype(int) + 3
    m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
    cv2.polylines(m, [np.int32(np.round((pts - (x0, y0)) * ss))], False, 255, max(1, int(round(q["larg_px"] * ss))),
                  cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)[..., None]
    out = img.copy()
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.float32(q["cor"]) * a, 0, 255).astype(np.uint8)
    return out


def nublado(Q, img):
    print("    o Térreo final novo (até a caracol, sem as letras), no quadro:")
    terreo = terreo_sem_letras()
    troca = np.round(corte_u(Q) * 255).astype(np.uint8)
    out = A.tracejado_lote(A.nublar(img, Q.pegada, terreo, Q.janelas, troca), Q.pg, Q.p2q)
    out = linha_corte(Q, out)
    print("    escada em U: os degraus 1 a 7 no Térreo nublado, recortados pela linha de corte do Térreo, desenhada "
          "por cima")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 7. As projeções tracejadas evidentes (item 11, R8; usuário, 26/10/26: "Em fundos escuros, faça a projeção com tom
# branco; para tons claros, marque-as com tom preto tracejado"), como no Térreo (`T.preto_branco`), por cima do nublado:
# - ARQ_CONTRAPISO: a cobertura (o contorno de fora e o de dentro), as retas aprovadas em 21/10 (`AJ.PROJECOES_1PAV`);
#   a de x = 1281,4 pt (no quarto e no banho master) é o contorno de dentro da cobertura no PDF (item 10: não é espúria;
#   perguntado, o usuário respondeu "mantem");
# - ARQ_PERGOLADO: a grade do pergolado da varanda;
# - DOC_LINHAS E PROJEÇÕES: os X e os contornos dos dois vazios (dentro da pegada; ficam de fora os afastamentos e o
#   lote, mais de `max_doc_pt`, e os X do elevador, do shaft e o da viga sobre a janela da escada, `fora_q`).
# Os traços são os do próprio PDF (os que caem nas retas aprovadas).
PROJ_1P = dict(T.PROJ, fora_q=[(2250, 1100, 2420, 1230), (2560, 870, 2770, 925)], tol_pt=0.6, traco_max_pt=12.5)


def tracos_nas_retas(Q, camada, cor, retas, q):
    out = []
    for d in Q.desenhos:
        if d.get("layer") != camada or d["type"] != "s" or (cor is not None and d.get("color") != cor):
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            x0, y0, x1, y1 = it[1].x, it[1].y, it[2].x, it[2].y
            if np.hypot(x1 - x0, y1 - y0) > q["traco_max_pt"]:
                continue
            for a0, b0, a1, b1 in retas:
                t = q["tol_pt"]
                if b0 == b1 and abs(y0 - b0) < t and abs(y1 - b0) < t and min(a0, a1) - t <= min(x0, x1) \
                        and max(x0, x1) <= max(a0, a1) + t:
                    out.append((x0, y0, x1, y1))
                    break
                if a0 == a1 and abs(x0 - a0) < t and abs(x1 - a0) < t and min(b0, b1) - t <= min(y0, y1) \
                        and max(y0, y1) <= max(b0, b1) + t:
                    out.append((x0, y0, x1, y1))
                    break
    return out


def projecoes(Q, img):
    q, qa = PROJ_1P, AJ.PROJECOES_1PAV
    tracos, nomes = [], []
    for camada, cor in qa["camadas"]:
        retas = [tuple(np.ravel(r)[:4]) for r in AJ.retas_tracejadas(Q.pg, camada, cor, qa["traco_max_pt"],
                                                                      qa["junta_pt"], qa["min_tracos"])]
        t = tracos_nas_retas(Q, camada, cor, retas, q)
        tracos += t
        nomes.append(f"{len(t)} da {camada} ({len(retas)} retas)")
    doc = T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"])
    par = FA.paredes_pdf(Q)

    def total(k):
        return sum(e for k2, e, _ in doc if k2[1] == k[1] and abs(k2[2] - k[2]) <= 2)
    n_doc = 0
    for k, ext, segs in doc:
        if total(k) > q["max_doc_pt"]:
            continue
        xm, ym = Q.p2q(*np.mean([((x0 + x1) / 2, (y0 + y1) / 2) for x0, y0, x1, y1 in segs], axis=0))
        if Q.pegada[int(ym), int(xm)] < 128 or par[int(ym), int(xm)] > 0.5 or \
                any(a <= xm <= c and b <= ym <= d for a, b, c, d in q["fora_q"]):
            continue
        tracos += segs
        n_doc += len(segs)
    nomes.append(f"{n_doc} da DOC_LINHAS")
    out, n_b = T.preto_branco(Q, img, tracos, q)
    a = par[..., None]                                       # nas paredes o traço some (como no ajuste aprovado)
    out = np.clip(np.round(out * (1 - a) + img * a), 0, 255).astype(np.uint8)
    print(f"    projeções tracejadas: {len(tracos)} traços do PDF ({', '.join(nomes)}), {len(tracos) - n_b} em preto "
          f"(fundo claro) e {n_b} em branco (fundo escuro); nas paredes, somem")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 8. Os rótulos, como na final aprovada (`rotulos_casaa.final_rotulos`: o corpo do PDF ampliado, os desvios aprovados,
# branco no granito), com os desvios novos do item 7 (E7), em `AJUSTES_1P` (centro e desvio em px de 2000):
# - BANHO 3: encostava na linha do box; no meio do piso seco, abaixo da bancada e do vaso;
# - B. SERVIÇO: o "A:" caía na linha do box; no meio do piso do box, no corpo do PDF (1,0), longe da linha, do chuveiro
#   e do registro;
# - SALA ÍNTIMA: estava no tapete ("O tapete conta como objeto, sim"); no piso livre acima do sofá, entre a planta e a
#   porta do banho.
AJUSTES_1P = {"BANHO 3": ("BANHO 3", (1121.1, 226.3), (-18.5, 4.9)),
              "B. SERVIÇO": ("B. SERVIÇO", (1142.1, 779.6), (5.4, -18.7), 1.0),
              "SALA ÍNTIMA": ("SALA ÍNTIMA", (1083.4, 552.2), (31.2, -72.6))}


def rotulos(Q, img):
    import retoque_1pav_casae as R1
    q = A.PAVIMENTOS["1Pavimento"]
    rot = [r for r in R1.rotulos_pdf(Q.pg) if r[0] in q.get("incluir", ()) or not any(f in r[0] for f in A.FORA)]
    ajustes = [AJUSTES_1P.get(a[0], a) for a in q["ajustes"]] + [a for n, a in AJUSTES_1P.items()
                                                                if n not in [b[0] for b in q["ajustes"]]]
    out = R1.rotulos_ambientes(img, rot, Q.p2q, escala_desvio=A.LARGURA / 2000,
                               granito=A.granito(img, q.get("granito_lum_max")), ajustes=ajustes,
                               cor_granito=R1.ROTULOS["branco"])
    print(f"    {len(rot)} rótulos, com os desvios aprovados; " + ", ".join(AJUSTES_1P) + " longe do box e do tapete")
    return out


def passos_1pav(Q):
    return [
        ("pisos", lambda im: pisos(Q, im)),
        ("armario", lambda im: armario(Q, im)),
        ("banhos", lambda im: banhos(Q, im)),
        ("paredes", lambda im: paredes(Q, im)),
        ("escada_u", lambda im: escada_u(Q, im)),
        ("caracol", lambda im: caracol(Q, im)),
        ("nublado", lambda im: nublado(Q, im)),
        ("projecoes", lambda im: projecoes(Q, im)),
        ("rotulos", lambda im: rotulos(Q, im)),
    ]


# O antes e o depois de cada item (a final aprovada até aqui, com os rótulos, e a nova), recortes no quadro (px)
ANTES_DEPOIS = {"planta": (1120, 260, 2800, 1740), "pisos": (1600, 300, 2620, 1000),
                "banho_master": (1330, 1420, 1760, 1670), "banho_1": (2420, 1080, 2580, 1340),
                "banho_2": (1600, 840, 1840, 980), "banho_3": (2040, 350, 2280, 500),
                "b_servico": (2110, 1410, 2290, 1590), "armario": (2080, 1310, 2300, 1510),
                "escada_u": (2220, 880, 2530, 1110), "caracol": (1880, 1470, 2080, 1670),
                "sala_intima": (1960, 860, 2270, 1230), "projecoes": (1380, 1120, 1780, 1700)}


def antes_depois(antes, depois, max_lado=1800, chaves=None):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        if chaves is not None and nome not in chaves:
            continue
        a, d = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        lado = (x1 - x0) <= (y1 - y0) * 1.3
        junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), d]) if lado else \
            np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), d])
        k = min(3.0, max_lado / max(junto.shape[:2]))
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
        arq = CASA / "renders" / f"POE642_CasaA_PH_1Pavimento_2610_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {arq.name}")


def final_3840(salvar=True, de=None, ate=None):
    """A final de 3840 px com os rótulos. de: recomeça desta etapa (a anterior vem do cache); ate: para nela."""
    Q = FA.QuadroA("1Pavimento")
    ini = inicial(Q)
    passos = passos_1pav(Q)
    nomes = [n for n, _ in passos]
    i0 = nomes.index(de) if de else 0
    i1 = nomes.index(ate) + 1 if ate else len(passos)
    img = cv2.imread(str(ETAPAS / f"1Pavimento_{nomes[i0 - 1]}.png")) if i0 > 0 else ini
    for nome, f in passos[i0:i1]:
        t0 = time.time()
        img = f(img)
        print(f"  [{nome}] {time.time() - t0:.0f} s", flush=True)
        cv2.imwrite(str(ETAPAS / f"1Pavimento_{nome}.png"), img)
    if salvar and ate is None and i1 == len(passos):
        nome = CASA / "renders" / "POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png"
        cv2.imwrite(str(nome), img)
        prev = cv2.resize(img, (2000, round(img.shape[0] * 2000 / img.shape[1])), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(nome.with_name(nome.stem + "_preview.jpg")), prev, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {nome} {img.shape[1]}x{img.shape[0]}")
    return Q, img


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--antes", help="a final aprovada antes destes itens (PNG): gera os antes e depois")
    a = ap.parse_args()
    Q, img = final_3840(de=a.de, ate=a.ate)
    if a.antes:
        antes_depois(cv2.imread(a.antes), img)

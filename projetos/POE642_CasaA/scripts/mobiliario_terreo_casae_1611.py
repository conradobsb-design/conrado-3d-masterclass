"""O mobiliário do Térreo da Casa E pela biblioteca da Casa E (16/11), a proposta aprovada.

Usuário: "VAMOS ALTERAR TODO O MOBILIARIO E REVER AMBIENTE POR AMBIENTE"; sobre a proposta
(`POE642_CasaE/renders/POE642_CasaE_PH_Terreo_1611_mobiliario_{1,2,3}.jpg`): "1. SIM 2. SIM 3. COMO HOJE 4. ENTRAM AS 2"
(o tapete redondo azul-marinho do 3D, gerado no Higgsfield; as cadeiras do jantar com o assento azul-marinho; a cozinha
como hoje, no Dekton Danae e na cor padrão de armário; as 2 espreguiçadeiras de madeira no deck).

Entra como o passo `mobiliario` de `pedidos_terreo_casae_1611` (antes dos rótulos). As peças vão nos desenhos do PDF
(os índices de `FE.QuadroE("Terreo").desenhos`, camadas ARQ_LAYOUT HUMANIZAÇÃO, ARQ_MOBILIÁRIO, ARQ_LOUÇAS E METAIS e
ARQ_BANCADAS; px da final de 3840): a peça de antes sai (a silhueta do PDF e a da imagem, com folga), o piso é refeito
pela amostra limpa do próprio piso (`alternativa1_terreo_casad_1611.refazer`: o desenho da amostra na luz do entorno) e a
peça da biblioteca entra com a sombra do padrão (`mobiliario_terreo_casac_1311.pousar`).
"""
from pathlib import Path

import cv2
import numpy as np

import alternativa1_terreo_casad_1611 as A1
import final3840_casae as FE
import mobiliario_terreo_casac_1311 as MB
import regras_terreo_casab_1311 as RT

AQUI = Path(__file__).resolve().parent
BIB_E = AQUI.parents[1] / "POE642_CasaE" / "biblioteca-objetos" / "02-terreo"

# as amostras limpas dos pisos (px, na imagem antes dos rótulos)
PISOS = {"travertino": (1880, 1182, 1940, 1232), "bege": (1205, 1165, 1295, 1230), "bege_gourmet": (1070, 790, 1110, 830),
         "marrom": (1612, 712, 1660, 752), "marrom_garagem": (2600, 822, 2680, 870), "marrom_gourmet": (1450, 655, 1500, 700),
         "cinza_wc": (2400, 600, 2440, 626), "grama": (2040, 1056, 2090, 1082), "danae": (1600, 498, 1640, 532),
         "danae_ilha": (1690, 615, 1740, 650), "danae_gourmet": (1180, 718, 1230, 760), "tabaco": (1170, 606, 1235, 638)}
AZUL_MARINHO = (88, 46, 26)          # BGR, o azul das cadeiras e do tapete do 3D da Casa E
NOGUEIRA = (50, 76, 112)             # BGR, a nogueira da mesa do jantar de hoje (nota 23 do cliente)

# ---------------------------------------------------------------------------------------------------------------------
# os desenhos do PDF (índices) e as caixas (px)
LIVING = {"tapete": 59791, "mesa_gota": 87026, "banco": 87055, "sofa": (1646, 1418, 1830, 1532),
          "poltronas": ((1695, 1289, 1742, 1336), (1636, 1341, 1683, 1387)), "mesa_lateral": (1672.0, 1318.0, 26.0),
          "vaso": ((1843, 1462, 1914, 1526), 58.0), "pilar": (1606, 1481, 1634, 1509),
          "tapete_png": "living/tapete-redondo-azul-marinho-e"}
ESTAR_JANELA = {"mesa": 79631, "poltronas": (79764, 79678, 79635, 79721), "caixa": (1932, 1345, 2089, 1489)}
JANTAR = {"mesa": (1689, 962, 1761, 1153), "cadeiras": ((1709, 948, 1742, 978), (1709, 1141, 1742, 1171),
                                                        (1669, 984, 1698, 1017), (1669, 1023, 1698, 1056),
                                                        (1669, 1063, 1698, 1095), (1669, 1104, 1698, 1137),
                                                        (1752, 984, 1782, 1017), (1752, 1023, 1782, 1056),
                                                        (1752, 1063, 1782, 1095), (1752, 1104, 1782, 1137)),
          "zona": (1655, 940, 1790, 1180), "arranjo": (1723, 1060, 16), "larg": 28.0}
VARANDA = {"mesas": (((1368, 888, 1463, 983), ((1398, 864, 1433, 898), (1352, 891, 1387, 926), (1444, 891, 1479, 926),
                                               (1352, 944, 1387, 979), (1444, 944, 1479, 979), (1398, 972, 1433, 1006))),
                     ((1368, 1062, 1463, 1158), ((1398, 1040, 1433, 1074), (1352, 1067, 1387, 1102),
                                                 (1444, 1067, 1479, 1102), (1352, 1120, 1387, 1155),
                                                 (1444, 1120, 1479, 1155), (1398, 1148, 1433, 1182)))),
           "sofa": (1319, 1235, 1522, 1305), "poltronas": ((1271, 1338, 1318, 1386), (1271, 1398, 1318, 1446)),
           "mesa_lateral": (1550.0, 1268.0, 30.0), "vaso": ((1521, 1448, 1580, 1550), 44.0)}
GOURMET_E = {"ilha": (1170, 711, 1445, 777), "banquetas_x": (1200, 1236, 1271.5, 1307, 1343, 1379, 1415),
             "cooktop": (1342, 714, 1394, 744), "cuba": (1241, 610, 1280, 640), "bancada_tras": (1094, 602, 1342, 645)}
COZINHA_E = {"ilha": (1680, 609, 1859, 687), "banquetas_x": (1714, 1750, 1786, 1821.5),
             "cooktop": (1774, 611, 1827, 641), "cuba": (1731, 500, 1808, 530), "bancada": (1594, 495, 1945, 535)}
BANQUETA = {"lado": 25.0, "sob": 0.4}
BH_GOURMET = {"bancada": (1352, 562, 1446, 587), "cuba_x": 1384.0, "bacia": (1315, 557, 1336, 587),
              "chuveiro": (1259.0, 562.0, 18.0), "chuveiro_velho": (1259, 565, 10)}
LAVABO_GOURMET = {"bancada": (988, 502, 1015, 633), "cuba_y": 531.0, "bacia": (1166, 498, 1187, 528)}
LAVABO = {"bancada": (2302, 1293, 2400, 1318), "cuba_x": 2329.0, "bacia": (2433, 1288, 2454, 1319)}
SERVICO = {"tanque": (1975, 568, 2052, 604), "lavadoras": ((2073, 565, 2115, 608), (2118, 565, 2160, 608))}
DCE = {"cama": (2264, 495, 2387, 552)}
WC_DCE = {"bacia": (2446, 560, 2476, 581), "chuveiro": (2459.0, 520.0, 16.0), "chuveiro_velho": (2446, 512, 2478, 528),
          "bancada": (2447, 591, 2476, 629), "miolo": (2397, 545, 2475, 628)}
ESCRITORIO_E = {"mesa": (2338, 996, 2439, 1038), "cadeiras": ((2364.0, 1038.0), (2414.0, 1038.0)),
                "visita": (2385.5, 996.0), "grupo": 88863, "chaise": 84202, "poltrona": (2398.0, 1146.0, 50.0),
                "zona": (2334, 970, 2443, 1064)}
HALL = {"aparador": (2271, 1327, 2421, 1359), "vaso": ((2333, 1518, 2386, 1571), 50.0)}
ADEGA = {"topo": (2082, 752, 2217, 775), "lados": ((2082, 775, 2106, 817), (2193, 775, 2217, 817))}
ELEVADOR = {"cabine": (1957, 718, 2048, 808)}
GARAGEM = {"carros": ((2549, 538, 2667, 803), (2705, 538, 2822, 803), (2856, 538, 2974, 803))}
# o deck: as 2 espreguiçadeiras entraram (16/11, "ENTRAM AS 2") e saíram (16/11, revisão do Térreo: "TIRE AS
# ESPREGUIÇADEIRAS DO DECK"); o deck fica vazio, como no PDF
DECK = {"espreguicadeiras": (), "larg": 42.0, "comp": 116.0}
JARDIM_E = {"plantas": (("jardim-interno/touceira-costela-de-adao", (1935.0, 1086.0), 32.0),
                        ("jardim-interno/palmeira-leque", (2160.0, 1088.0), 30.0)),
            "velhas": ((1935, 1086, 20), (2160, 1088, 20))}


# ---------------------------------------------------------------------------------------------------------------------
def ler(rel):
    P = cv2.imread(str(BIB_E / f"{rel}.png"), cv2.IMREAD_UNCHANGED)
    if P.shape[2] == 3:
        P = np.dstack([P, np.full(P.shape[:2], 255, np.uint8)])
    P = P.astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 8)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def ret(caixa, folga=0):
    def f(forma):
        m = np.zeros(forma, bool)
        x0, y0, x1, y1 = caixa
        m[max(int(y0) - folga, 0):int(np.ceil(y1)) + folga, max(int(x0) - folga, 0):int(np.ceil(x1)) + folga] = True
        return m
    return f


def disco(cx, cy, r, forma):
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]]
    return np.hypot(xx - cx, yy - cy) <= r


def piso(out, buraco, amostra, par, nao_luz=None):
    """O piso da amostra no buraco; as paredes (e `nao_luz`: a ilha, as peças que ficam) não dão a luz do piso."""
    excl = RT.dilatar(par, 1) if nao_luz is None else (RT.dilatar(par, 1) | nao_luz)
    return A1.refazer(out, buraco & ~par, [(None, PISOS[amostra])], ficam=excl)


def centro(c):
    x0, y0, x1, y1 = c
    return (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0


def pdf(Q, ids, d=0):
    m = MB.contorno(Q, list(ids))[1]
    return RT.dilatar(m, d) if d else m


def esticada(P, L, D, cols, pos, ss=4, borda=0.04):
    """A bancada com a cuba (P, a torneira em cima): `cols` (frações) da cuba, que não estica; os dois lados lisos
    repetidos em espelho (a pedra sem esticar), a beira de fora (`borda`) nas pontas; a cuba centrada em `pos` (fração
    de L). Devolve o PNG (BGRA) de L x D px (x ss)."""
    H, W = P.shape[:2]
    k = D * ss / H
    Q = cv2.resize(P, (max(1, round(W * k)), round(D * ss)), interpolation=cv2.INTER_AREA)
    W2 = Q.shape[1]
    c0, c1 = round(cols[0] * W2), round(cols[1] * W2)
    b = max(1, round(borda * W2))
    cuba = Q[:, c0:c1]
    Lt = round(L * ss)
    esq_t = max(b + 1, round(pos * Lt - cuba.shape[1] / 2))
    dir_t = max(b + 1, Lt - esq_t - cuba.shape[1])

    def lado(liso, borda_px, alvo, ponta_esq):
        miolo = alvo - borda_px.shape[1]
        rep = np.concatenate([liso, liso[:, ::-1]], axis=1)
        rep = np.tile(rep, (1, miolo // rep.shape[1] + 2, 1))[:, :miolo]
        return np.concatenate([borda_px, rep], axis=1) if ponta_esq else np.concatenate([rep, borda_px], axis=1)
    esq = lado(Q[:, b:c0], Q[:, :b], esq_t, True)
    dir_ = lado(Q[:, c1:W2 - b][:, ::-1], Q[:, W2 - b:], dir_t, False)
    return np.ascontiguousarray(np.concatenate([esq, cuba, dir_], axis=1))


def pousar(out, P, cx, cy, wt, ht, ang, sombra, par):
    return MB.pousar(out, P, cx, cy, wt, ht, ang, sombra, par)


def tingir_tecido(P, cor, sat_madeira=70):
    """O tecido de P (tudo o que não é a madeira: o laranja saturado) no tom `cor`; a madeira fica."""
    hsv = cv2.cvtColor(np.clip(P[..., :3], 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    madeira = (hsv[..., 1] >= sat_madeira) & (hsv[..., 0] >= 4) & (hsv[..., 0] <= 30)
    madeira = cv2.morphologyEx(madeira.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    m = (P[..., 3] > 120) & ~madeira
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    return A1.tingir(P, m, cor, gama=0.8)


def tingir_madeira(P, cor):
    m = P[..., 3] > 200
    return A1.tingir(P, m, cor, gama=0.9)


def objeto_imagem(img, caixa, amostra, limiar=26, folga=3):
    """Os px da caixa que não são o piso da amostra (a peça de antes como está na imagem, com a sombra), com folga."""
    x0, y0, x1, y1 = caixa
    a0, b0, a1, b1 = PISOS[amostra]
    ref = img[b0:b1, a0:a1].reshape(-1, 3).astype(np.float32).mean(axis=0)
    sub = cv2.GaussianBlur(img[y0:y1, x0:x1].astype(np.float32), (0, 0), 1.0)
    d = np.linalg.norm(sub - ref, axis=2) > limiar
    m = np.zeros(img.shape[:2], bool)
    m[y0:y1, x0:x1] = d
    return RT.dilatar(m, folga)


def objeto_verde(img, caixa, folga=3):
    """As folhas (o verde) da caixa, com folga: a planta de antes como está na imagem."""
    x0, y0, x1, y1 = caixa
    s = cv2.GaussianBlur(img[y0:y1, x0:x1], (0, 0), 0.8).astype(np.int16)
    v = (s[..., 1] > s[..., 2] + 6) & (s[..., 1] > s[..., 0] + 6)
    m = np.zeros(img.shape[:2], bool)
    m[y0:y1, x0:x1] = v
    return RT.dilatar(m, folga)


# ---------------------------------------------------------------------------------------------------------------------
def living(Q, out, par, q=LIVING):
    H, W = out.shape[:2]
    pilar = ret(q["pilar"])((H, W))
    # a cortina C4 e o caixilho junto ao vidro de baixo ficam (o tapete passa por baixo deles)
    cortina = ret((1592, 1528, 2096, 1560))((H, W))           # a cortina C4 da fachada inteira (16/11)
    par2 = par | pilar | cortina
    # o tapete redondo, o sofá, as poltronas, as mesas, o banco e o vaso de antes saem; o travertino volta
    (x0, y0), (x1, y1) = RT._caixa(Q, Q.desenhos[q["tapete"]])
    tcx, tcy, R = (x0 + x1) / 2, (y0 + y1) / 2, ((x1 - x0) + (y1 - y0)) / 4
    buraco = disco(tcx, tcy, R + 8, (H, W))
    for c in (q["sofa"], *q["poltronas"]):
        buraco |= ret(c, 8)((H, W))
    buraco |= objeto_imagem(out, (1600, 1280, 1880, 1537), "travertino", limiar=30, folga=4) & disco(tcx, tcy, R + 30, (H, W))
    vcx, vcy, vw, vh = centro(q["vaso"][0])
    buraco |= disco(vcx, vcy, max(vw, vh) / 2 + 6, (H, W))
    out = piso(out, buraco, "travertino", par2)
    # o tapete azul-marinho do 3D (Higgsfield), no círculo do PDF
    Pt = ler(q["tapete_png"])
    out = pousar(out, Pt, tcx, tcy, 2 * R, 2 * R, 0.0, "tapete", par2)
    # o sofá curvo de linho no desenho do PDF (os assentos para a mesa)
    Ps = ler("living/sofa-curvo-living-e")
    sx, sy, sw, sh = centro(q["sofa"])
    out = pousar(out, Ps, sx, sy, sw * 1.02, sw * 1.02 * Ps.shape[0] / Ps.shape[1], 180.0, "movel", par2)
    # as poltronas creme com o aro de madeira, viradas para a mesa gota
    mg = RT.caixa_pdf(Q, q["mesa_gota"])
    gx, gy = (mg[0] + mg[2]) / 2, (mg[1] + mg[3]) / 2
    Pp = ler("living/poltrona-creme-madeira-render")
    for c in q["poltronas"]:
        cx, cy, w, h = centro(c)
        lado = 0.98 * min(w, h)
        g = round(MB.frente((gx - cx, gy - cy)) / 45.0) * 45.0
        out = pousar(out, Pp, cx, cy, lado * Pp.shape[1] / Pp.shape[0], lado, g, "movel", par2)
    # a mesa gota em nogueira, no desenho do PDF
    Pg = ler("living/mesa-centro-gota-e")
    gw, gh = mg[2] - mg[0], mg[3] - mg[1]
    out = pousar(out, Pg, gx, gy, gh, gw, 90.0, "mesa", par2)
    # o banco de madeira do PDF (o freijó do aparador) e a mesa lateral entre as poltronas
    b = RT.caixa_pdf(Q, q["banco"])
    Pb = ler("hall-de-entrada/aparador-freijo")
    out = pousar(out, Pb, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, b[3] - b[1], b[2] - b[0], 90.0, "mesa", par2)
    mx, my, ml = q["mesa_lateral"]
    out = pousar(out, ler("living/mesa-lateral-metal-madeira"), mx, my, ml, ml, 0.0, "mesa", par2)
    # o vaso de folhagem da E
    Pv = ler("hall-de-entrada/vaso-folhagem-a")
    out = pousar(out, Pv, vcx, vcy, q["vaso"][1], q["vaso"][1], 0.0, "movel", par2)
    print("    living: o tapete redondo azul-marinho (Higgsfield), o sofá curvo de linho, 2 poltronas creme com aro de "
          "madeira, a mesa gota, o banco de freijó, a mesa lateral e o vaso de folhagem")
    return out


def estar_janela(Q, out, par, q=ESTAR_JANELA):
    H, W = out.shape[:2]
    buraco = pdf(Q, [q["mesa"], *q["poltronas"]], 6) | objeto_imagem(out, q["caixa"], "travertino", limiar=30, folga=4)
    out = piso(out, buraco, "travertino", par)
    mx, my, mw, mh = centro(RT.caixa_pdf(Q, q["mesa"]))
    Pp = ler("living/poltrona-creme-madeira-render")
    for i in q["poltronas"]:
        cx, cy, w, h = centro(RT.caixa_pdf(Q, i))
        lado = 0.95 * min(w, h)
        g = MB.frente((mx - cx, my - cy))
        out = pousar(out, Pp, cx, cy, lado * Pp.shape[1] / Pp.shape[0], lado, g, "movel", par)
    D_ = (mw + mh) / 2
    out = pousar(out, ler("varanda/mesa-redonda-varanda-e"), mx, my, D_, D_, 0.0, "mesa", par)
    print("    estar da janela: a mesa redonda de nogueira e as 4 poltronas creme com aro de madeira")
    return out


def jantar(Q, out, par, q=JANTAR):
    H, W = out.shape[:2]
    ax, ay, ar = q["arranjo"]
    fonte = out.copy()
    zona = ret(q["zona"])((H, W))
    out = piso(out, zona, "travertino", par)
    Pc = tingir_tecido(ler("sala-de-jantar/cadeira-a"), AZUL_MARINHO)
    x0, y0, x1, y1 = q["mesa"]
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    for c in q["cadeiras"]:
        cx, cy, _, _ = centro(c)
        d = np.array([np.sign(mx - cx), 0.0]) if (cx < x0 or cx > x1) else np.array([0.0, np.sign(my - cy)])
        g = MB.frente(d)
        # 1/3 sob o tampo: a cadeira encosta na mesa
        lar = q["larg"]
        alt = lar * Pc.shape[0] / Pc.shape[1]
        if d[0] != 0:
            cx = (x0 - alt / 2 + alt / 3) if d[0] > 0 else (x1 + alt / 2 - alt / 3)
        else:
            cy = (y0 - alt / 2 + alt / 3) if d[1] > 0 else (y1 + alt / 2 - alt / 3)
        out = pousar(out, Pc, cx, cy, lar, alt, g, "movel", par)
    Pm = tingir_madeira(ler("sala-de-jantar/mesa-jantar-retangular-e"), NOGUEIRA)
    out = pousar(out, Pm, mx, my, y1 - y0, x1 - x0, 90.0, "mesa", par)
    # o arranjo de centro de hoje volta por cima (as folhas: o verde da caixa)
    sub = fonte[ay - ar:ay + ar, ax - ar:ax + ar].astype(np.int16)
    # o arranjo é verde-oliva (G ~ R, bem acima do B); a nogueira tem o R bem acima do G
    verde = (sub[..., 1] >= sub[..., 2] - 6) & (sub[..., 1] > sub[..., 0] + 15) & disco(ar, ar, ar - 2, sub.shape[:2])
    verde = cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    verde = cv2.dilate(verde, np.ones((3, 3), np.uint8)) > 0
    a = cv2.GaussianBlur(verde.astype(np.float32), (0, 0), 0.7)[..., None]
    reg = out[ay - ar:ay + ar, ax - ar:ax + ar].astype(np.float32)
    out[ay - ar:ay + ar, ax - ar:ax + ar] = np.clip(reg * (1 - a) + sub * a, 0, 255).astype(np.uint8)
    print(f"    jantar: a mesa retangular da E em nogueira e as {len(q['cadeiras'])} cadeiras estofadas com o assento "
          "azul-marinho, alinhadas e 1/3 sob o tampo; o arranjo de centro fica")
    return out


def varanda(Q, out, par, q=VARANDA):
    H, W = out.shape[:2]
    Pc = ler("varanda/cadeira-redonda-varanda-e")
    Pm = ler("varanda/mesa-redonda-varanda-e")
    for mesa, cads in q["mesas"]:
        buraco = ret(mesa, 6)((H, W))
        for c in cads:
            buraco |= ret(c, 6)((H, W))
        x0, y0, x1, y1 = mesa
        buraco |= objeto_imagem(out, (x0 - 44, y0 - 44, x1 + 44, y1 + 44), "bege", limiar=24, folga=3)
        out = piso(out, buraco, "bege", par)
        mx, my, mw, mh = centro(mesa)
        for c in cads:
            cx, cy, w, h = centro(c)
            lado = 0.95 * min(w, h)
            out = pousar(out, Pc, cx, cy, lado, lado * Pc.shape[0] / Pc.shape[1], MB.frente((mx - cx, my - cy)),
                         "movel", par)
        out = pousar(out, Pm, mx, my, (mw + mh) / 2, (mw + mh) / 2, 0.0, "mesa", par)
    # o estar: o sofá da E, as poltronas de corda para a mesa de centro, a mesa lateral
    buraco = ret(q["sofa"], 6)((H, W)) | objeto_imagem(out, (1300, 1220, 1540, 1320), "bege", limiar=30, folga=3)
    buraco |= objeto_imagem(out, (1255, 1325, 1335, 1460), "bege", limiar=30, folga=3)
    for c in q["poltronas"]:
        buraco |= ret(c, 6)((H, W))
    vcx, vcy, vw, vh = centro(q["vaso"][0])
    vidro = ret((1577, 1430, 1600, 1580))((H, W))
    buraco |= ret((1510, 1436, 1577, 1566))((H, W))     # as 2 plantas de antes com a sombra delas
    out = piso(out, buraco & ~vidro, "bege", par, nao_luz=vidro)
    sx, sy, sw, sh = centro(q["sofa"])
    Ps = ler("varanda/sofa-varanda-e")
    out = pousar(out, Ps, sx, sy, sw, sw * Ps.shape[0] / Ps.shape[1], 0.0, "movel", par)
    Pp = ler("varanda/poltrona-externa-b")
    for c in q["poltronas"]:
        cx, cy, w, h = centro(c)
        lado = 0.98 * min(w, h)
        out = pousar(out, Pp, cx, cy, lado * Pp.shape[1] / Pp.shape[0], lado, MB.frente((1, 0)), "movel", par)
    lx, ly, ll = q["mesa_lateral"]
    out = pousar(out, ler("varanda/mesa-lateral-externa"), lx, ly, ll, ll, 0.0, "mesa", par)
    Pv = ler("varanda/vaso-folhagem-b")
    for dy in (-0.25, 0.25):                         # as 2 plantas do PDF, uma sobre a outra
        out = pousar(out, Pv, vcx, vcy + dy * vh, q["vaso"][1], q["vaso"][1], 0.0, "movel", par)
    print("    varanda: as 2 mesas redondas da E com as 12 cadeiras redondas creme; o sofá da E, as 2 poltronas de "
          "corda, a mesa lateral externa e o vaso de folhagem (a mesa de centro e o banco de madeira ficam)")
    return out


def banquetas(out, par, ilha, xs, piso_nome, antes_ilha):
    """As banquetas da E no x do PDF, 40% do assento sob o tampo (a parte de baixo do tampo não aparece), o encosto
    para fora; as de antes saem (a faixa embaixo da ilha) e o piso volta."""
    H, W = out.shape[:2]
    x0, y0, x1, y1 = ilha
    lado = BANQUETA["lado"]
    faixa = np.zeros((H, W), bool)
    faixa[y1:y1 + 30, x0 - 4:x1 + 4] = True
    out = piso(out, faixa, piso_nome, par, nao_luz=ret(ilha, 2)((H, W)))
    # a sombra curta da ilha no piso refeito
    k = np.arange(8, dtype=np.float32)
    out[y1:y1 + 8, x0 - 2:x1 + 2] = np.clip(out[y1:y1 + 8, x0 - 2:x1 + 2].astype(np.float32)
                                            * (1 - 0.22 * np.exp(-k / 2.2))[:, None, None], 0, 255).astype(np.uint8)
    P = ler("area-gourmet/banqueta-varanda-e")
    alt = lado * P.shape[0] / P.shape[1]
    cy = y1 + alt / 2 - BANQUETA["sob"] * lado
    ilha_px = out[y0 - 2:y1, x0 - 2:x1 + 2].copy()
    for x in xs:
        out = pousar(out, P, x, cy, lado, alt, MB.frente((0, -1)), "movel", par)
    out[y0 - 2:y1, x0 - 2:x1 + 2] = ilha_px
    return out


def peca_no_lugar(out, par, caixa, rel, piso_nome, ang=0.0, sombra="baixa", folga=3, wt=None, ht=None, P=None):
    H, W = out.shape[:2]
    out = piso(out, ret(caixa, folga)((H, W)), piso_nome, par)
    cx, cy, w, h = centro(caixa)
    P = ler(rel) if P is None else P
    return pousar(out, P, cx, cy, w if wt is None else wt, h if ht is None else ht, ang, sombra, par)


def gourmet(Q, out, par, q=GOURMET_E):
    antes = out.copy()
    out = banquetas(out, par, q["ilha"], q["banquetas_x"], "bege_gourmet", antes)
    # o cooktop de 4 bocas (a pedra da ilha em volta)
    x0, y0, x1, y1 = q["cooktop"]
    fora = ~ret(q["ilha"])(out.shape[:2])                 # o piso em volta da ilha não dá a luz da pedra
    out = piso(out, ret(q["cooktop"], 2)(out.shape[:2]) & ~fora, "danae_gourmet", par, nao_luz=fora)
    lado = y1 - y0
    out = pousar(out, ler("area-gourmet/cooktop-quatro-bocas"), (x0 + x1) / 2, (y0 + y1) / 2, lado * 1.15, lado, 0.0,
                 "baixa", par)
    # a cuba Franke com o misturador na bancada de trás (o marrom tabaco em volta)
    x0, y0, x1, y1 = q["cuba"]
    out = piso(out, ret(q["cuba"], 2)(out.shape[:2]), "tabaco", par)
    out = pousar(out, ler("area-gourmet/cuba-franke-misturador-unic"), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0,
                 0.0, "baixa", par)
    # a grelha da E na churrasqueira (a caixa da de hoje)
    import pedidos_terreo_casae_1611 as PE
    g = PE.GOURMET
    (a, b), (c, d) = Q.p2q(*g["churrasqueira_pt"][:2]), Q.p2q(*g["churrasqueira_pt"][2:])
    P = ler("area-gourmet/grelha-churrasqueira")
    wt = g["grelha_px"]
    out = pousar(out, P, (a + c) / 2, (b + d) / 2, wt, wt * P.shape[0] / P.shape[1], 0.0, "baixa", par)
    print("    gourmet: as 7 banquetas da E (40% sob o tampo), o cooktop de 4 bocas, a cuba Franke com o misturador e "
          "a grelha da E")
    return out


def cozinha(Q, out, par, q=COZINHA_E):
    antes = out.copy()
    out = banquetas(out, par, q["ilha"], q["banquetas_x"], "marrom", antes)
    x0, y0, x1, y1 = q["cooktop"]
    fora = ~ret(q["ilha"])(out.shape[:2])
    out = piso(out, ret(q["cooktop"], 2)(out.shape[:2]) & ~fora, "danae_ilha", par, nao_luz=fora)
    lado = y1 - y0
    out = pousar(out, ler("cozinha/cooktop-quatro-bocas"), (x0 + x1) / 2, (y0 + y1) / 2, lado * 1.15, lado, 0.0,
                 "baixa", par)
    x0, y0, x1, y1 = q["cuba"]
    out = piso(out, ret(q["cuba"], 3)(out.shape[:2]), "danae", par)
    P = ler("cozinha/cuba-franke-dupla-vista-superior")
    out = pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2 + 1, 66.0, 34.0, 0.0, "baixa", par)
    print("    cozinha: as 4 banquetas conhaque da E (40% sob o tampo), o cooktop de 4 bocas e a cuba Franke dupla com "
          "o misturador; a ilha em Dekton Danae e os armários ficam")
    return out


def banhos(Q, out, par):
    H, W = out.shape[:2]
    # BH gourmet: a bancada inteira de travertino com a cuba esculpida, a bacia no marrom, o chuveiro quadrado
    q = BH_GOURMET
    x0, y0, x1, y1 = q["bancada"]
    P = esticada(ler("banho-gourmet/cuba-travertino-gourmet"), x1 - x0, y1 - y0, (0.27, 0.71),
                 1 - (q["cuba_x"] - x0) / (x1 - x0))          # girada 180°: a esquerda do PNG fica à direita
    out = pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente((0, -1)), "baixa", par)
    out = peca_no_lugar(out, par, q["bacia"], "banho-gourmet/bacia-escura-render", "marrom_gourmet",
                        MB.frente((0, -1)), "baixa", folga=3)
    cx, cy, r = q["chuveiro_velho"]
    out = piso(out, disco(cx, cy, r, (H, W)), "marrom_gourmet", par)
    cx, cy, ld = q["chuveiro"]
    out = pousar(out, ler("banho-gourmet/chuveiro-quadrado"), cx, cy, ld, ld, 0.0, "baixa", par)
    # lavabo gourmet: a cuba esculpida da E na bancada inteira (a parede à esquerda), a bacia no marrom
    q = LAVABO_GOURMET
    x0, y0, x1, y1 = q["bancada"]
    P = esticada(ler("lavabo-gourmet/cuba-social-e"), y1 - y0, x1 - x0, (0.20, 0.80),
                 (y1 - q["cuba_y"]) / (y1 - y0))              # girada 90° anti-horário: a esquerda do PNG fica embaixo
    out = pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, MB.frente((1, 0)), "baixa", par)
    out = peca_no_lugar(out, par, q["bacia"], "lavabo-gourmet/bacia-escura-render", "marrom_gourmet",
                        MB.frente((0, 1)), "baixa", folga=3)
    # lavabo: a cuba esculpida da E na bancada inteira (a parede embaixo), a bacia no marrom
    q = LAVABO
    x0, y0, x1, y1 = q["bancada"]
    P = esticada(ler("lavabo/cuba-social-e"), x1 - x0, y1 - y0, (0.20, 0.80), 1 - (q["cuba_x"] - x0) / (x1 - x0))
    out = pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente((0, -1)), "baixa", par)
    out = peca_no_lugar(out, par, q["bacia"], "lavabo/bacia-escura-render", "travertino", MB.frente((0, -1)), "baixa",
                        folga=6)
    print("    banhos: BH gourmet (a bancada de travertino com a cuba esculpida, a bacia no marrom, o chuveiro "
          "quadrado), lavabo gourmet e lavabo (a cuba esculpida da E, a bacia no marrom)")
    return out


def servico(Q, out, par):
    H, W = out.shape[:2]
    q = SERVICO
    x0, y0, x1, y1 = q["tanque"]
    out = piso(out, ret(q["tanque"], 2)((H, W)), "tabaco", par)
    out = pousar(out, ler("area-de-servico/tanque-duplo-inox"), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0,
                 "baixa", par)
    Pt = ler("area-de-servico/torneira-deca-link-1167")
    for tx in (x0 + (x1 - x0) * 0.27, x0 + (x1 - x0) * 0.73):
        out = pousar(out, Pt, tx, y0 + 6, 3.0, 13.0 * 0.6, 0.0, None, par)
    Pl = ler("area-de-servico/lavadora-tampa-superior")
    for c in q["lavadoras"]:
        out = peca_no_lugar(out, par, c, None, "marrom", 0.0, "movel", folga=3, P=Pl,
                            wt=(c[2] - c[0]) - 1, ht=(c[3] - c[1]) - 1)
    # DCE: a cama de solteiro de linho da E (a cabeceira à direita)
    x0, y0, x1, y1 = DCE["cama"]
    out = piso(out, ret(DCE["cama"], 4)((H, W)), "marrom", par)
    Pc = ler("quarto-dce-1/cama-solteiro-e")
    out = pousar(out, Pc, (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, MB.frente((-1, 0)), "movel", par)
    # WC DCE: o piso sem as manchas, a bacia Monte Carlo, o chuveiro Acqua Plus, a cuba no São Gabriel
    q = WC_DCE
    x0, y0, x1, y1 = q["miolo"]
    sub = out[y0:y1, x0:x1].astype(np.int16)
    mancha = sub[..., 2] - sub[..., 0] > 18                   # as manchas quentes no cinza (o vidro do box fica)
    m = np.zeros((H, W), bool)
    m[y0:y1, x0:x1] = mancha
    m[538:547] = False
    livre = ~(ret(q["bacia"], 3)((H, W)) | ret(q["bancada"], 2)((H, W)))
    out = piso(out, RT.dilatar(m, 2) & livre, "cinza_wc", par)
    out = peca_no_lugar(out, par, q["bacia"], "banho-dce-1/bacia-monte-carlo-sem-valvula", "cinza_wc",
                        MB.frente((-1, 0)), "baixa", folga=3, wt=21.0, ht=31.0)
    out = piso(out, ret(q["chuveiro_velho"])((H, W)), "cinza_wc", par)
    cx, cy, ld = q["chuveiro"]
    out = pousar(out, ler("banho-dce-1/chuveiro-acqua-plus"), cx, cy, ld, ld, 0.0, "baixa", par)
    x0, y0, x1, y1 = q["bancada"]
    P = esticada(ler("banho-dce-1/cuba-dce-gabriel-e"), y1 - y0, x1 - x0, (0.29, 0.68), 0.5)
    out = pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, MB.frente((-1, 0)), "baixa", par)
    print("    serviço: o tanque duplo inox com as torneiras Deca Link, a lavadora e a secadora; DCE: a cama de solteiro "
          "da E; WC DCE: o piso sem as manchas, a bacia Monte Carlo, o chuveiro Acqua Plus e a cuba no São Gabriel")
    return out


def escritorio(Q, out, par, q=ESCRITORIO_E):
    H, W = out.shape[:2]
    buraco = ret(q["zona"])((H, W)) | pdf(Q, [q["chaise"]], 5)
    buraco |= objeto_imagem(out, (2336, 1100, 2440, 1192), "travertino", limiar=30, folga=3)
    planta = disco(2449.5, 1171.0, 15.0, (H, W)) | ret((2457, 1100, 2472, 1192))((H, W))  # o vaso do canto e a cortina
    out = piso(out, buraco & ~planta, "travertino", par, nao_luz=planta)
    x0, y0, x1, y1 = q["mesa"]
    Pc = ler("escritorio/cadeira-escritorio")
    lar = 34.0
    alt = lar * Pc.shape[0] / Pc.shape[1]
    for cx, yb in q["cadeiras"]:
        out = pousar(out, Pc, cx, yb + alt / 2 - alt / 3, lar, alt, MB.frente((0, -1)), "movel", par)
    Pv = ler("sala-de-jantar/cadeira-jantar-madeira-e")
    lv = 30.0
    av = lv * Pv.shape[0] / Pv.shape[1]
    vx, vy = q["visita"]
    out = pousar(out, Pv, vx, vy - av / 2 + av / 3, lv, av, MB.frente((0, 1)), "movel", par)
    out = pousar(out, ler("escritorio/mesa-escritorio-e"), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, "mesa",
                 par)
    px, py, pl = q["poltrona"]
    Pp = ler("escritorio/poltrona-intima-e")
    out = pousar(out, Pp, px, py, pl, pl * Pp.shape[0] / Pp.shape[1], MB.frente((-1, -1)), "movel", par)
    print("    escritório: a mesa da E, as 2 cadeiras de couro 1/3 sob o tampo, a de visita de madeira e linho; a "
          "poltrona arredondada da E no lugar da chaise (a mesinha e o vaso ficam)")
    return out


def hall_e_outros(Q, out, par):
    H, W = out.shape[:2]
    # hall: o aparador em freijó e o vaso de folhagem
    out = peca_no_lugar(out, par, HALL["aparador"], "hall-de-entrada/aparador-freijo", "travertino", 0.0, "mesa",
                        folga=3)
    (c, ld) = HALL["vaso"]
    cx, cy, w, h = centro(c)
    out = piso(out, disco(cx, cy, max(w, h) / 2 + 5, (H, W)), "travertino", par)
    out = pousar(out, ler("hall-de-entrada/vaso-folhagem-a"), cx, cy, ld, ld, 0.0, "movel", par)
    # adega: o módulo de garrafas da E no U do PDF
    Pa = ler("adega/armario-adega-e")
    x0, y0, x1, y1 = ADEGA["topo"]
    out = pousar(out, Pa, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, None, par)
    for x0, y0, x1, y1 in ADEGA["lados"]:
        out = pousar(out, Pa, (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, 90.0, None, par)
    # elevador: a cabine em aço da E
    x0, y0, x1, y1 = ELEVADOR["cabine"]
    out = pousar(out, ler("elevador/cabine-elevador-e"), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, None,
                 par)
    # garagem: os 3 sedãs prata da E
    Pg = ler("garagem/sedan-prata")
    for c in GARAGEM["carros"]:
        x0, y0, x1, y1 = c
        buraco = objeto_imagem(out, (x0 - 14, y0 - 14, x1 + 14, y1 + 14), "marrom_garagem", limiar=28, folga=4)
        out = piso(out, buraco, "marrom_garagem", par)
        out = pousar(out, Pg, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, "movel", par)
    # deck: as 2 espreguiçadeiras de madeira (a cabeceira para a piscina)
    Pe = ler("deck-de-pedra/espreguicadeira-madeira-render")
    for cx, cy in DECK["espreguicadeiras"]:
        out = pousar(out, Pe, cx, cy, DECK["larg"], DECK["comp"], 0.0, "movel", par)
    # jardim interno: a costela-de-adão e a palmeira-leque do 3D, pequenas, sobre a grama
    for cx, cy, r in JARDIM_E["velhas"]:
        out = piso(out, disco(cx, cy, r, (H, W)), "grama", par)
    for rel, (cx, cy), ld in JARDIM_E["plantas"]:
        out = pousar(out, ler(rel), cx, cy, ld, ld, 0.0, "baixa", par)
    print("    hall: o aparador em freijó e o vaso; adega: as garrafas da E no U; elevador: a cabine da E; garagem: os 3 "
          "sedãs prata da E; deck vazio (sem as espreguiçadeiras); jardim interno: a costela-de-adão e a "
          "palmeira-leque")
    return out


def aplicar(Q, img):
    par = FE.paredes_pdf(Q) > 0.5
    out = img.copy()
    for f in (living, estar_janela, jantar, varanda, gourmet, cozinha, banhos, servico, escritorio, hall_e_outros):
        out = f(Q, out, par)
    return out

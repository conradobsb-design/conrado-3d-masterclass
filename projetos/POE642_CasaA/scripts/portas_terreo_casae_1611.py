"""As portas (quina a quina), as soleiras e as esquadrias do Térreo da Casa E (16/11).

Usuário: "Vamos revisar as portas para saber se elas estão fazendo quina aqui naquela parede, soleiras e as esquadrias
também." O levantamento porta a porta contra o PDF
(`POE642_CasaE/renders/POE642_CasaE_PH_Terreo_1611_portas_esquadrias_revisao.jpg`), e o OK: "Prossiga". Entra como o
passo `portas` de `pedidos_terreo_casae_1611` (depois do Danae, antes dos rótulos). Os px são os da final de 3840; os
retângulos do PDF (ARQ_PAREDE) vêm de `final3840_casae.QuadroE("Terreo")`.

- P1 despensa: a folha inteira (a do render parava a 1/3), no perfil da própria folha, até a ponta do PDF.
- P2 a P7: os batentes do PDF (as peças brancas finas na ponta da parede, junto à dobradiça) viram parede, até a face da
  folha (a regra de 12/11 das Casas A a D: "não há batentes, apenas parede. porta com a quina da parede").
- P8 gás: a folha até a quina (sem a mancha branca na ponta), os batentes e os marcos em parede, a soleira no vão.
- P9 entrada (pivotante): a folha num tom só, de ponta a ponta do PDF (2362,7 a 2519,7); a soleira de face a face no
  vão da fachada, com as faces finas (a da Casa C); o toco no cinza das paredes.
- E1 fachada do living: os pontinhos escuros entre as folhas de correr e os resíduos do canto esquerdo saem.
- E3 janelas do escritório: no vão, a soleira e as duas folhas de correr do PDF no alumínio claro das janelas da casa
  (de montante a montante); os blocos brancos saem.
- E4 janelas da cozinha e da área de serviço: as roldanas e os pontos escuros sobre as folhas saem.
- E5 WC DCE: as manchas claras do piso antigo em volta do box e do chuveiro saem (o cinza dos banhos da Casa D).
Não mudam (conferidos): o vidro entre a varanda e o living (a linha escura é o trilho grafite da cortina C4), a garagem,
o CPD, o DCE, o WC DCE, o lavabo, o box do BH gourmet e o vidro fixo da entrada; o lavabo gourmet sem soleira (nota 7).
"""
import contextlib
import io

import cv2
import numpy as np

import final3840_casae as FE

PAREDE = (80, 80, 80)
SS = 8
# o perfil da folha de cada porta de giro (px): a folha do PDF e as linhas (ou colunas) de onde vem o perfil
FOLHAS = {"P1 despensa": {"folha": (2233.7, 713.7, 2236.1, 758.1), "eixo": "v", "perfil": (716, 721), "cols": (2231, 2239)},
          "P8 gás": {"folha": (2005.3, 381.4, 2007.7, 423.2), "eixo": "v", "perfil": (392, 408), "cols": (2002, 2011)}}
# os batentes e marcos (ARQ_PAREDE, brancos) que viram parede, por porta
BATENTES = {"P2 lavabo gourmet": [(1082.2, 581.8, 1091.2, 587.2)],
            "P8 gás": [(1958.4, 422.0, 1960.5, 436.3), (2007.1, 422.0, 2012.5, 436.3), (1955.2, 422.0, 1959.9, 423.2),
                       (1955.2, 435.1, 1959.3, 436.3)]}
# os batentes perto da dobradiça achados no PDF: (dobradiça, raio da busca px)
DOBRADICAS = {"P3 BH gourmet": (1446.4, 498.0), "P4 cozinha → área de serviço": (1954.0, 700.0),
              "P5 cozinha → circulação": (1936.2, 811.3), "P6 circulação → área descoberta": (2030.1, 435.1),
              "P7 área descoberta → área de serviço": (2212.3, 556.6)}
SOLEIRAS = {"P8 gás": (1960.5, 423.2, 2007.1, 435.1), "P9 entrada": (2476.4, 1329.0, 2488.4, 1487.2),
            "E3 escritório": (2476.4, 983.9, 2488.4, 1122.4)}
SOLEIRA = {"amostra": (1945, 650, 1952, 690), "fio": 0.80}
ENTRADA = {"folha": (2362.7, 2519.7), "linhas": (1368, 1374), "perfil_x": (2495, 2513),
           "parede": [(2476.4, 1327.8, 2488.4, 1329.0), (2476.4, 1487.2, 2488.4, 1496.2)]}
ESCRITORIO = {"folhas": [(2482.4, 983.9, 2485.4, 1055.5), (2485.4, 1050.7, 2488.4, 1122.4)],
              "marcos": [(2476.4, 981.5, 2488.4, 983.9), (2476.4, 1122.4, 2488.4, 1124.8)],
              "aluminio": (200, 201, 203), "borda": (150, 152, 155)}
# (caixa px, o que sai): os pontos escuros pequenos, por inpaint do entorno (`lum_max`, `area_max` px)
PONTOS = [((1572, 1534, 1600, 1556), "E1 canto esquerdo da fachada do living", 150, 40, (1578, 1552, 1586, 1563))]
# as folhinhas soltas (o verde da planta de antes) no canto esquerdo da fachada do living
VERDES = [(1576, 1532, 1592, 1553)]
# (caixa px, o que sai, desvio, altura máx., largura máx.): as manchas pequenas sobre as folhas (as roldanas, os
# encontros) saem pela mediana na horizontal (a folha é igual ao longo dela); os montantes, altos, ficam
BOLHAS = [((1700, 1544, 1724, 1560), "E1 encontro das folhas (1)", 18, 13, 8),
          ((1955, 1544, 1978, 1560), "E1 encontro das folhas (2)", 18, 13, 8),
          ((1595, 481, 1945, 501), "E4 janela da cozinha", 16, 8, 9),
          ((1955, 543, 2195, 566), "E4 janela da área de serviço", 16, 8, 9)]
WC_DCE = {"caixa": (2396, 506, 2477, 560), "quente": 10, "lum_max": 238, "chuveiro": (2459.0, 520.0, 9.0),
          "box_faixa": (2394, 536, 2477, 557),
          # os dois vidros de correr do box (ARQ_LOUÇAS E METAIS), no fio cinza fino
          "vidros": [((2395.9, 542.2), (2438.2, 542.2)), ((2406.8, 543.1), (2449.2, 543.1))], "fio": (150, 152, 156)}


def _poligono(out, r, cor, ss=SS):
    import biblioteca_terreo_casad_1511 as TD
    x0, y0, x1, y1 = r
    return TD._poligono(out, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], tuple(float(v) for v in cor), ss)


def _soleira(out, r, cor, fio):
    import portas_revisao_casad_1611 as PR
    return PR._soleira(out, r, cor, fio, SS)


def folha_perfil(out, q):
    """A folha inteira do PDF no perfil da própria folha (as colunas `cols` nas linhas `perfil`, a mediana)."""
    x0, y0, x1, y1 = q["folha"]
    c0, c1 = q["cols"]
    r0, r1 = q["perfil"]
    perfil = np.median(out[r0:r1, c0:c1].astype(np.float32), axis=0)            # (colunas, 3)
    fundo = np.median(np.concatenate([out[r0:r1, c0 - 4:c0], out[r0:r1, c1:c1 + 4]], axis=1).reshape(-1, 3), axis=0)
    dif = np.linalg.norm(perfil - fundo, axis=1) > 12
    ya, yb = int(np.floor(y0)), int(np.ceil(y1))
    novo = out.copy()
    for j, c in enumerate(range(c0, c1)):
        if dif[j]:
            novo[ya:yb, c] = np.clip(perfil[j], 0, 255).astype(np.uint8)
    # a ponta do PDF macia (a fração do último px)
    fr = y1 - np.floor(y1)
    if fr > 0:
        lin = int(np.floor(y1))
        novo[lin] = np.clip(out[lin] * (1 - fr) + novo[lin] * fr, 0, 255).astype(np.uint8)
    return novo


def batentes_pdf(Q, hx, hy, raio=4.5):
    """Os retângulos brancos pequenos da ARQ_PAREDE (os batentes e marcos) a até `raio` px da dobradiça."""
    rs = []
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or d["type"] not in ("f", "fs") or not d.get("fill") or min(d["fill"]) < 0.9:
            continue
        pts = np.concatenate([np.asarray(c) for c in Q.caminhos(d)])
        (x0, y0), (x1, y1) = pts.min(0), pts.max(0)
        if max(x1 - x0, y1 - y0) > 6.5:
            continue
        dx = max(x0 - hx, 0, hx - x1)
        dy = max(y0 - hy, 0, hy - y1)
        if np.hypot(dx, dy) <= raio:
            rs.append((float(x0), float(y0), float(x1), float(y1)))
    return rs


def _inpaint(out, m, r=2):
    return cv2.inpaint(out, m.astype(np.uint8) * 255, r, cv2.INPAINT_TELEA)


def pontos(out, caixa, lum_max, area_max, fica=None):
    x0, y0, x1, y1 = caixa
    sub = out[y0:y1, x0:x1].astype(np.int16)
    escuro = sub.mean(axis=2) < lum_max
    n, lab, st, _ = cv2.connectedComponentsWithStats(escuro.astype(np.uint8), 8)
    m = np.zeros(escuro.shape, bool)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a <= area_max and max(w, h) <= 12:
            m |= lab == i
    if fica is not None:
        fx0, fy0, fx1, fy1 = fica
        m[max(fy0 - y0, 0):max(fy1 - y0, 0), max(fx0 - x0, 0):max(fx1 - x0, 0)] = False
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    M = np.zeros(out.shape[:2], bool)
    M[y0:y1, x0:x1] = m
    return _inpaint(out, M), int(m.sum())


def bolhas(out, caixa, desvio, hmax, wmax):
    """As manchas pequenas (altura <= hmax, largura <= wmax) que fogem da mediana horizontal da faixa saem por ela."""
    x0, y0, x1, y1 = caixa
    sub = out[y0:y1, x0:x1]
    med = cv2.medianBlur(np.ascontiguousarray(sub), 1) if False else None
    k = 2 * wmax + 1
    med = np.stack([ndi_median(sub[..., c], k) for c in range(3)], axis=2)
    dev = np.abs(sub.astype(np.int16) - med.astype(np.int16)).max(axis=2) > desvio
    n, lab, st, _ = cv2.connectedComponentsWithStats(dev.astype(np.uint8), 8)
    m = np.zeros(dev.shape, bool)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if h <= hmax and w <= wmax:
            m |= lab == i
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    novo = sub.copy()
    novo[m] = med[m]
    out = out.copy()
    out[y0:y1, x0:x1] = novo
    return out, int(m.sum())


def ndi_median(ch, k):
    from scipy.ndimage import median_filter
    return median_filter(ch, size=(1, k), mode="nearest")


def parede_pdf_perto(Q, out, hx, hy, r=5.0):
    """A parede do PDF (com o antialias dele) a até `r` px da dobradiça: a ponta da parede do render vai até a do PDF."""
    FE.paredes_pdf(Q)
    a = np.clip(Q._par, 0, 1)
    X0, Y0, X1, Y1 = int(hx - r - 1), int(hy - r - 1), int(hx + r + 2), int(hy + r + 2)
    yy, xx = np.mgrid[Y0:Y1, X0:X1]
    w = a[Y0:Y1, X0:X1] * (np.hypot(xx - hx, yy - hy) <= r)
    w = np.where(w > 0.5, 1.0, w)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out = out.copy()
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - w) + np.float32(PAREDE) * w, 0, 255).astype(np.uint8)
    return out


def aplicar(Q, img):
    out = img.copy()
    feito = []
    # P1 e P8: as folhas inteiras
    for nome, q in FOLHAS.items():
        out = folha_perfil(out, q)
        feito.append(nome + ": a folha inteira")
    # P2 a P7: os batentes em parede
    for nome, rs in BATENTES.items():
        for r in rs:
            out = _poligono(out, r, PAREDE)
    for nome, (hx, hy) in DOBRADICAS.items():
        rs = batentes_pdf(Q, hx, hy)
        for r in rs:
            out = _poligono(out, r, PAREDE)
        out = parede_pdf_perto(Q, out, hx, hy)
        feito.append(f"{nome}: {len(rs)} batente(s) em parede")
    out = parede_pdf_perto(Q, out, 1091.2, 582.5)
    # as soleiras (o claro das soleiras da casa, com as faces finas)
    x0, y0, x1, y1 = SOLEIRA["amostra"]
    cor = tuple(float(v) for v in np.median(img[y0:y1, x0:x1].reshape(-1, 3), axis=0))
    for nome, r in SOLEIRAS.items():
        out = _soleira(out, r, cor, SOLEIRA["fio"])
    # P9: a parede do toco e dos marcos; a folha num tom só, de ponta a ponta
    q = ENTRADA
    for r in q["parede"]:
        out = _poligono(out, r, PAREDE)
    l0, l1 = q["linhas"]
    p0, p1 = q["perfil_x"]
    perfil = np.median(img[l0:l1, p0:p1].astype(np.float32), axis=1)               # (linhas, 3)
    xa, xb = q["folha"]
    for j, y in enumerate(range(l0, l1)):
        out[y, int(np.ceil(xa)):int(np.floor(xb))] = np.clip(perfil[j], 0, 255).astype(np.uint8)
        for xf, fr in ((int(np.floor(xa)), np.ceil(xa) - xa), (int(np.floor(xb)), xb - np.floor(xb))):
            out[y, xf] = np.clip(out[y, xf] * (1 - fr) + perfil[j] * fr, 0, 255).astype(np.uint8)
    feito.append("P9 entrada: a folha num tom só, a soleira de face a face, o toco em parede")
    # E3: as folhas das janelas do escritório sobre a soleira; os marcos em parede
    q = ESCRITORIO
    for r in q["marcos"]:
        out = _poligono(out, r, PAREDE)
    for r in q["folhas"]:
        out = _poligono(out, r, q["borda"])
        x0, y0, x1, y1 = r
        out = _poligono(out, (x0 + 0.6, y0 + 0.6, x1 - 0.6, y1 - 0.6), q["aluminio"])
    feito.append("E3 escritório: soleira e 2 folhas de correr no alumínio claro")
    # E1 e E4: os pontos escuros e as manchas pequenas sobre as folhas
    for caixa, nome, lum, area, fica in PONTOS:
        out, n = pontos(out, caixa, lum, area, fica)
        feito.append(f"{nome}: {n} px")
    for x0, y0, x1, y1 in VERDES:
        sub = out[y0:y1, x0:x1].astype(np.int16)
        v = (sub[..., 1] > sub[..., 2] + 4) | ((sub.max(axis=2) - sub.min(axis=2) > 22) & (sub.mean(axis=2) < 170))
        M = np.zeros(out.shape[:2], bool)
        M[y0:y1, x0:x1] = cv2.dilate(v.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        out = _inpaint(out, M)
        feito.append(f"E1 folhinhas no canto: {int(M.sum())} px")
    for caixa, nome, dv, hm, wm in BOLHAS:
        out, n = bolhas(out, caixa, dv, hm, wm)
        feito.append(f"{nome}: {n} px")
    # E5: o WC DCE sem as manchas claras
    import mobiliario_terreo_casae_1611 as ME
    q = WC_DCE
    x0, y0, x1, y1 = q["caixa"]
    sub = out[y0:y1, x0:x1].astype(np.int16)
    quente = ((sub[..., 2] - sub[..., 0]) > q["quente"]) & (sub.mean(axis=2) < q["lum_max"])
    H, W = out.shape[:2]
    m = np.zeros((H, W), bool)
    m[y0:y1, x0:x1] = quente
    cx, cy, rr = q["chuveiro"]
    yy, xx = np.mgrid[0:H, 0:W]
    m &= np.hypot(xx - cx, yy - cy) > rr
    # a faixa do box de antes (os traços cinza partidos) também sai: os vidros voltam pelo PDF
    bx0, by0, bx1, by1 = q["box_faixa"]
    faixa = np.zeros((H, W), bool)
    faixa[by0:by1, bx0:bx1] = True
    lum = out.astype(np.int16).mean(axis=2)
    m |= faixa & (lum < 212)
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    m &= np.hypot(xx - cx, yy - cy) > rr
    # o piso cinza da amostra, no tom médio do piso livre do banho (o banho é uniforme: sem a luz do entorno, que
    # puxava a sombra das paredes para dentro)
    par = FE.paredes_pdf(Q) > 0.5
    m &= ~par
    ax0, ay0, ax1, ay1 = ME.PISOS["cinza_wc"]
    amostra = out[ay0:ay1, ax0:ax1].astype(np.float32)
    T = np.concatenate([amostra, amostra[:, ::-1]], axis=1)
    T = np.concatenate([T, T[::-1]], axis=0)
    T = np.tile(T, ((y1 - y0) // T.shape[0] + 2, (x1 - x0) // T.shape[1] + 2, 1))[:y1 - y0, :x1 - x0]
    livre = ~m[y0:y1, x0:x1] & ~par[y0:y1, x0:x1] & (out[y0:y1, x0:x1].astype(np.int16).mean(axis=2) > 195)
    alvo = np.median(out[y0:y1, x0:x1][livre].reshape(-1, 3).astype(np.float32), axis=0)
    T = T * (alvo / np.maximum(T.reshape(-1, 3).mean(axis=0), 1))
    sub = out[y0:y1, x0:x1].copy()
    mm = m[y0:y1, x0:x1]
    sub[mm] = np.clip(T[mm], 0, 255).astype(np.uint8)
    out = out.copy()
    out[y0:y1, x0:x1] = sub
    M = np.zeros((H * SS, W * SS), np.uint8)
    for p0, p1 in q["vidros"]:
        cv2.line(M, tuple(int(round(v * SS)) for v in p0), tuple(int(round(v * SS)) for v in p1), 255,
                 max(1, int(round(0.8 * SS))), cv2.LINE_AA)
    al = cv2.resize(M.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)[..., None]
    out = np.clip(out.astype(np.float32) * (1 - al) + np.float32(q["fio"]) * al, 0, 255).astype(np.uint8)
    feito.append(f"E5 WC DCE: {int(m.sum())} px de manchas; os 2 vidros do box no fio cinza")
    print("    portas e esquadrias: " + "; ".join(feito))
    return out

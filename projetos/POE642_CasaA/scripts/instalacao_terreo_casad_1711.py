"""Térreo da Casa D, a 2ª leva de 17/11 (depois de `correcoes_terreo_casad_1711.py`), na final e direto nos 12K A e B, no
afim afinado ali (`correcoes_terreo_casab_1611.Mapa.local`):

1. `banco_b1` ("B1 E L2, PODE INSTALAR"): o banco do living (o retângulo da ARQ_MOBILIÁRIO 98058, à direita do tapete)
   pelo B1 gerado no Higgsfield (`propostas-1711/banco-B1`: estrutura de nogueira e assento de couro conhaque), em pé no
   retângulo do PDF, com a sombra curta; antes, o banco de linho sai (o tapete de logo à esquerda).
2. `arandelas_l2`: as arandelas pretas da suíte master pela L2 (`propostas-1711/luminaria-L2`: cúpula de linho e latão),
   a cúpula de 0,26 m sobre cada criado (a de antes, no mesmo lugar), o braço de latão até a parede da cabeceira e a
   placa de latão de topo na face da parede; antes, a arandela preta sai (o tampo do criado em volta, por inpaint).
3. `soleira_garagem` ("AQUI É UMA SOLEIRA. NÃO É AMADEIRADA"): a faixa entre o piso da garagem e o hall de entrada, que
   saía em madeira, na soleira de Bege Bahia das outras portas (a da cozinha para o living, com as faces finas).
4. `vao_hall_garagem` ("AQUI NÃO TEM SOLEIRA. VEJA NO 3D"; "ONDE REMOVEREMOS A SOLEIRA, FICARÁ PISO DA GARAGEM"): a faixa
   clara no vão da porta do hall para a garagem sai: o piso da garagem entra no vão (em espelho) até a face do hall; a
   folha aberta fica.
5. `painel_garagem` ("REFAÇA O PAINEL AMADEIRADO, CONFORME ADOTAMOS EM OUTRAS ÁREAS DA CASA"): o painel em pé na beira
   da garagem, junto à grama, no ripado de nogueira das janelas (`correcoes_terreo_casad_1711._ripado`).
6. `paineis_pivotantes` ("SÃO PAINEIS AMADEIRADOS ... AS DIMENSÕES ESTÃO OK, APENAS TROQUE PARA O REVESTIMENTO QUE
   ADOTAMOS"): os 2 painéis pivotantes da gourmet (as lâminas a 45° de `pedidos_terreo_casad_1611b.BRISES`), nas mesmas
   medidas, do preto para o ripado de nogueira (as juntas na largura, a luz, o contorno); a sombra fica.
7. `piso_banho_gourmet` ("VAMOS CORRIGIR ESSAS FALHAS NO PISO? ... RESÍDUOS DO PISO MAIS ESCURO"): a faixa do piso escuro
   antigo rente à parede de cima (sob as janelas e acima da prateleira) e a marca preta junto dela pelo piso claro de logo
   abaixo; a linha pontilhada de pé à esquerda e a emenda de pé à direita, pelos dois lados em espelho.
8. `portas_servico` ("REVISE AS PORTAS E PAREDES ... RESTOS DE PISOS ANTIGOS MAIS ESCUROS ... PAREDES ATRÁS DAS PORTAS"):
   a borda escura da parede de dentro do louceiro e da despensa, que sumia atrás das folhas, de volta (a mesma de cima e
   de baixo); o piso escuro antigo ao lado das folhas (louceiro, despensa, a de correr da área de serviço, as 2 da área
   descoberta e a do WC DCE) e as manchinhas do louceiro e da área descoberta pelo piso de perto; a folha de correr da
   área de serviço redesenhada reta (branca, contorno fino).
9. `poltrona_varanda` ("CORRIJA ESSE BORRÃO VERTICAL EM VOLTA DA POLTRONA"): a faixa borrada de pé na beira do tapete,
   acima e abaixo da poltrona de fibra da direita do estar da varanda, pelo Bege Bahia de logo à direita.
10. `mesa_escritorio` ("MELHORE O CONTORNO DO NOGUEIRA NA MESA DO ESCRITÓRIO"): a borda cinza à direita do tampo e o
   resto claro da mesa antiga embaixo (e à esquerda) pelo piso de madeira de perto; o contorno fino e a sombra curta do
   tampo de nogueira no retângulo do PDF.

  python3 instalacao_terreo_casad_1711.py final [--saida <png>]
  python3 instalacao_terreo_casad_1711.py doze [--opcao AB] [--saida <jpg com {}>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
import correcoes_terreo_casad_1711 as CD                    # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

FINAL = DF.PLANTAS["D_Terreo"]
DOZE = DF.DOZE_K["D_Terreo"]
RAIZ = AQUI.parents[1]
PROP = RAIZ / "POE642_CasaD/biblioteca-objetos/02-terreo/propostas-1711"

BANCO = {"png": PROP / "banco-B1.png", "ret": (2205.6, 1104.8, 2241.5, 1212.3), "limpa_dx": -42.0, "sombra": 0.32}
ARANDELAS = {"png": PROP / "luminaria-L2.png", "cupula": (506.0, 620.0, 390.0), "diam_px": 15.5,
             "criados": [(760.3, 1517.9, 793.1, 1551.0), (926.4, 1517.9, 959.3, 1551.0)], "parede_y": 1552.6,
             "latao": (84, 136, 160), "latao_esc": (50, 86, 110), "braco_px": 1.2, "placa": (7.0, 1.3),
             "sombra": 0.30}
SOLEIRA = {"alvo": (2517.0, 792.0, 2617.0, 802.0), "fonte": (1992.0, 675.6, 2084.0, 685.6)}
VAO_HALL = {"faixa": (2430.6, 706.6, 2441.0, 770.0), "espelho_x": 2441.0,
            # a quina escura da parede de cima, que caía no meio do piso da garagem
            "quina": ((2439.0, 706.6, 2444.5, 712.5), [(6, 0), (8, 0)])}
PAINEL_GARAGEM = ((3180.4, 467.5, 3184.8, 631.0), "x+")
PIVOTANTES = {"x": (1390.5, 1396.5), "y": (558.0, 702.0), "n": 2, "comp": 0.93, "esp_px": 4.5, "cobre_px": 0.9}
# os remendos: (retângulo px da final, os deslocamentos da fonte px da final, em ordem, o filtro dos px trocados)
BANHO_G = {"caixa": (1380, 360, 1720, 470),
           "remendos": [((1450.0, 370.5, 1504.0, 376.6), [(0, 8), (0, 10)], "marrom"),
                        ((1504.0, 370.5, 1559.5, 375.5), [(0, 13), (0, 15)], "marrom"),
                        ((1559.5, 370.5, 1642.0, 376.6), [(0, 8), (0, 10)], "marrom"),
                        ((1556.5, 373.5, 1568.0, 381.0), [(0, 8), (0, 10), (8, 0)], "escuro"),
                        # a faixa escura antiga sob a prateleira (a tábua clara fica)
                        ((1503.5, 378.4, 1559.5, 382.8), [(0, 6), (0, 8)], "marrom"),
                        # o toco marrom em cima da parede do box
                        ((1557.5, 419.5, 1567.5, 427.0), [(0, -8), (0, -10)], "marrom")],
           "tracos": [((1446.0, 377.0, 1446.0, 466.0), 2.5), ((1558.0, 382.0, 1558.0, 426.0), 3.5)]}
SERVICO = {"caixa": (2085, 380, 2400, 690),
           # a borda escura da parede (o retângulo, a amostra do tom dela logo acima/abaixo)
           "bordas": [((2099.9, 441.5, 2102.0, 488.2), (2100.0, 404.0, 2102.0, 438.0)),
                      ((2099.9, 565.5, 2102.0, 614.5), (2100.0, 618.0, 2102.0, 646.0))],
           "remendos": [((2106.6, 445.0, 2109.0, 489.5), [(2.5, 0)], "marrom"),
                        ((2106.6, 565.0, 2109.0, 596.0), [(2.5, 0)], "marrom"),
                        ((2106.6, 596.0, 2109.0, 609.0), [(0, -13)], "marrom"),
                        ((2195.6, 483.5, 2199.4, 547.0), [(5, 0), (7, 0)], "marrom"),
                        ((2200.4, 567.5, 2202.0, 609.5), [(-5, 0), (-6, 0)], "marrom"),
                        ((2204.8, 567.5, 2208.4, 609.5), [(5, 0), (8, 0), (6, 6)], "marrom"),
                        ((2200.0, 610.4, 2208.6, 614.5), [(0, 5), (0, 7)], "marrom"),
                        ((2289.4, 567.5, 2292.0, 609.5), [(-5, 0), (-7, 0)], "marrom"),
                        ((2294.6, 567.5, 2298.4, 610.4), [(5, 0), (7, 0)], "marrom"),
                        ((2289.6, 610.4, 2298.4, 614.5), [(0, 5), (0, 7)], "marrom"),
                        ((2375.4, 628.5, 2377.6, 666.0), [(-5, 0)], None),
                        ((2104.0, 399.5, 2160.0, 426.5), [(6, 0), (-6, 0), (0, 5)], "escuro"),
                        ((2243.0, 569.0, 2256.0, 581.0), [(6, 0), (-6, 0)], "escuro")],
           # a folha de correr entre o corredor do louceiro e a área de serviço
           "folha": {"limpa": ((2192.4, 487.0, 2193.8, 545.6), (-4.0, 0.0)), "ret": (2193.0, 486.6, 2195.4, 545.4),
                     "cor": (222, 222, 222), "contorno": (118, 118, 118), "contorno_px": 0.35}}
# a faixa (x px da final) acima e abaixo da poltrona (linhas), o Bege Bahia limpo (dx), as colunas de fora (o tapete à
# esquerda, o Bege Bahia à direita) que dão a sombra da poltrona, e as linhas limpas delas (longe da poltrona)
POLTRONA = {"caixa": (1660, 1010, 1760, 1135), "x": (1707.0, 1719.2), "linhas": [(1030.0, 1050.3), (1097.8, 1118.0)],
            "dx": 30.0, "esq": 1704.0, "dir": 1720.0, "limpo": [(1012.0, 1028.0), (1120.0, 1132.0)]}
ESCRITORIO = {"mesa": (2362.5, 1553.8, 2410.3, 1673.2), "caixa": (2340, 1540, 2440, 1695),
              "limpa": [((2410.3, 1550.5, 2414.2, 1594.0), (4.5, 0)), ((2410.3, 1634.0, 2414.2, 1680.0), (4.5, 0)),
                        ((2359.5, 1673.2, 2414.2, 1680.0), (0, 7.5)), ((2359.6, 1604.0, 2362.5, 1623.0), (-5, 0)),
                        ((2359.6, 1662.5, 2362.5, 1673.2), (-5, 0))],
              "contorno": (30, 38, 50), "contorno_px": 0.55, "sombra": 0.22}


def _local(out, mp, caixa):
    return mp.local(out, caixa) if mp.ref is not None else mp


def _rgba(png, limiar=29, encolhe=0.006):
    """A peça no fundo branco: a maior peça (pela distância ao branco), sem furos, encolhida um pouco (a franja clara da
    sombra do fundo fica de fora); o antisserrilhado vem da redução."""
    P = cv2.imread(str(png))
    d = (255 - P.astype(np.int16)).max(-1)
    n, lab, st, _ = cv2.connectedComponentsWithStats((d > limiar).astype(np.uint8), 8)
    peca = ndimage.binary_fill_holes(lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))))
    ys, xs = np.nonzero(peca)
    k = max(1, int(round(encolhe * max(np.ptp(ys), np.ptp(xs)))))
    a = cv2.erode(peca.astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)).astype(np.float32)
    return P[ys.min():ys.max() + 1, xs.min():xs.max() + 1], a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def _pousar(out, rgb, alfa, r, sombra=0.0, s=1.0):
    """A peça (rgb, alfa) esticada no retângulo r (px da imagem, fracionário), com a sombra curta embaixo."""
    x0, y0, x1, y1 = r
    f = int(np.ceil(4 * s)) + 2
    X0, Y0, X1, Y1 = int(np.floor(x0)) - f, int(np.floor(y0)) - f, int(np.ceil(x1)) + f, int(np.ceil(y1)) + f
    w, h = X1 - X0, Y1 - Y0
    ph, pw = rgb.shape[:2]
    sx, sy = (x1 - x0) / pw, (y1 - y0) / ph
    # a peça reduzida antes (INTER_AREA) para o afim não serrilhar, pré-multiplicada pelo alfa (sem a franja do fundo
    # branco na borda); os centros dos px casados (borda u -> u')
    kw, kh = max(2, int(round(pw * sx * 2))), max(2, int(round(ph * sy * 2)))
    a32 = alfa.astype(np.float32)
    R2 = cv2.resize(rgb.astype(np.float32) * a32[..., None], (kw, kh), interpolation=cv2.INTER_AREA)
    A2 = cv2.resize(a32, (kw, kh), interpolation=cv2.INTER_AREA)
    ax, ay = (x1 - x0) / kw, (y1 - y0) / kh
    M = np.float32([[ax, 0, x0 - X0 + 0.5 * ax - 0.5], [0, ay, y0 - Y0 + 0.5 * ay - 0.5]])
    Rw = cv2.warpAffine(R2, M, (w, h), flags=cv2.INTER_LINEAR)
    Aw = cv2.warpAffine(A2, M, (w, h), flags=cv2.INTER_LINEAR)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    if sombra:
        Ms = np.float32([[1, 0, -1.0 * s], [0, 1, 1.3 * s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(Aw, Ms, (w, h)), (0, 0), 1.2 * s) * (1 - Aw)
        reg *= (1 - sombra * sb)[..., None]
    reg = reg * (1 - Aw[..., None]) + Rw
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def banco_b1(out, mp, q=BANCO):
    r = q["ret"]
    m = _local(out, mp, (int(r[0]) - 25, int(r[1]) - 25, int(r[2]) + 25, int(r[3]) + 25))
    # o banco de antes sai: o tapete de logo à esquerda
    CB.copia(out, out.copy(), m, (r[0] - 1.5, r[1] - 2.0, r[2] + 0.5, r[3] + 2.5), (q["limpa_dx"], 0.0))
    rgb, a = _rgba(q["png"])
    rgb, a = cv2.rotate(rgb, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(a, cv2.ROTATE_90_CLOCKWISE)
    _pousar(out, rgb, a, m.ret(r), q["sombra"], m.s)
    print("    living: o banco B1 (nogueira e couro conhaque) no retângulo do PDF")


def arandelas_l2(out, mp, q=ARANDELAS):
    P = cv2.imread(str(q["png"]))
    cx, cy, R = q["cupula"]
    cup = P[int(cy - R):int(cy + R), int(cx - R):int(cx + R)]
    hh, ww = cup.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww]
    disco = (np.hypot(xx - ww / 2 + 0.5, yy - hh / 2 + 0.5) <= R).astype(np.float32)
    # a cúpula com o braço para baixo (a parede da cabeceira fica abaixo dos criados)
    cup, disco = cv2.rotate(cup, cv2.ROTATE_180), cv2.rotate(disco, cv2.ROTATE_180)
    for c in q["criados"]:
        m = _local(out, mp, (int(c[0]) - 25, int(c[1]) - 25, int(c[2]) + 25, int(c[3]) + 25))
        ccx, ccy = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
        # a arandela preta sai: os px escuros e neutros do meio do criado até a parede
        X0, Y0 = int(m.x(ccx - 11)), int(m.y(c[1]))
        X1, Y1 = int(np.ceil(m.x(ccx + 11))), int(np.ceil(m.y(q["parede_y"] - 0.4)))
        reg = out[Y0:Y1, X0:X1]
        I = reg.astype(np.int16)
        preto = ((I.max(-1) - I.min(-1)) < 22) & (I.mean(-1) < 100)
        preto = cv2.dilate(preto.astype(np.uint8), np.ones((3, 3), np.uint8))
        out[Y0:Y1, X0:X1] = cv2.inpaint(np.ascontiguousarray(reg), preto, max(3, int(3 * m.s)), cv2.INPAINT_TELEA)
        # o braço de latão do centro da cúpula à parede, e a placa na face da parede
        bw = q["braco_px"]
        CB.sombra(out, m, (ccx - bw / 2, ccy, ccx + bw / 2, q["parede_y"]), q["sombra"], dx=-0.8, dy=0.8, sigma=0.7)
        CB.pintar(out, m, [((ccx - bw / 2, ccy, ccx + bw / 2, q["parede_y"]), "ret", q["latao"], 0),
                           ((ccx - bw / 2, ccy, ccx + bw / 2, q["parede_y"]), "contorno", q["latao_esc"], 0.3)])
        pl, pe = q["placa"]
        placa = (ccx - pl / 2, q["parede_y"] - pe, ccx + pl / 2, q["parede_y"])
        CB.pintar(out, m, [(placa, "ret", q["latao"], 0), (placa, "contorno", q["latao_esc"], 0.3)])
        # a cúpula de linho por cima
        d = q["diam_px"]
        _pousar(out, cup, disco, m.ret((ccx - d / 2, ccy - d / 2, ccx + d / 2, ccy + d / 2)), q["sombra"], m.s)
    print("    suíte master: as 2 arandelas L2 (cúpula de linho, braço e placa de latão) sobre os criados")


def soleira_garagem(out, mp, q=SOLEIRA):
    a = q["alvo"]
    m = _local(out, mp, (int(a[0]) - 20, int(a[1]) - 20, int(a[2]) + 20, int(a[3]) + 20))
    fx0, fy0, fx1, fy1 = (int(round(v)) for v in m.ret(q["fonte"]))
    src = out[fy0:fy1, fx0:fx1].copy()
    ax0, ay0, ax1, ay1 = (int(round(v)) for v in m.ret(a))
    h, w = ay1 - ay0, ax1 - ax0
    src = cv2.resize(src, (src.shape[1], h), interpolation=cv2.INTER_AREA)
    tira = np.concatenate([src, src[:, ::-1]] * (w // (2 * src.shape[1]) + 2), axis=1)[:, :w]
    out[ay0:ay1, ax0:ax1] = tira
    print("    hall: a soleira junto à garagem em Bege Bahia (a das outras portas), sem a madeira")


def vao_hall_garagem(out, mp, q=VAO_HALL):
    r = q["faixa"]
    m = _local(out, mp, (int(r[0]) - 25, int(r[1]) - 10, int(r[2]) + 15, int(r[3]) + 10))
    x0, y0, x1, y1 = (int(round(v)) for v in m.ret(r))
    e = int(round(m.x(q["espelho_x"])))
    fonte = out.copy()
    for x in range(x0, x1):
        out[y0:y1, x] = fonte[y0:y1, 2 * e - 1 - x]
    _remenda(out, m, q["quina"][0], q["quina"][1], "escuro")
    print("    hall: o vão da porta para a garagem sem a soleira (o piso da garagem até a face do hall)")


def painel_garagem(out, mp, q=PAINEL_GARAGEM):
    import um_pav_casaa_1111 as U
    r, lado = q
    m = _local(out, mp, (int(r[0]) - 30, int(r[1]) - 20, int(r[2]) + 30, int(r[3]) + 20))
    CD._ripado(out, m, r, lado, U.FOLHAS_1P, np.random.default_rng(1731))
    print("    garagem: o painel junto à grama no ripado de nogueira")


def _tabua(out, m, p0, p1, larg, qa, rng, ss=4):
    """Uma tábua girada (de p0 a p1, px da final, a largura em px da final) no ripado de nogueira: as juntas na largura,
    a luz de um lado, o contorno fino."""
    s = m.s
    P0, P1 = np.array([m.x(p0[0]), m.y(p0[1])]), np.array([m.x(p1[0]), m.y(p1[1])])
    v = P1 - P0
    Lp = float(np.hypot(*v))
    t = v / Lp
    n_ = np.array([-t[1], t[0]])
    W = larg * s
    f = int(np.ceil(W + 3 * s)) + 2
    X0, Y0 = int(np.floor(min(P0[0], P1[0]))) - f, int(np.floor(min(P0[1], P1[1]))) - f
    X1, Y1 = int(np.ceil(max(P0[0], P1[0]))) + f, int(np.ceil(max(P0[1], P1[1]))) + f
    hh, ww = (Y1 - Y0) * ss, (X1 - X0) * ss
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    px, py = X0 + (xx + 0.5) / ss - P0[0], Y0 + (yy + 0.5) / ss - P0[1]
    u = px * t[0] + py * t[1]
    w_ = px * n_[0] + py * n_[1]
    dentro = (u >= 0) & (u <= Lp) & (np.abs(w_) <= W / 2)
    rel = np.clip(w_ / W + 0.5, 0, 1)
    veio = cv2.GaussianBlur(rng.normal(0, 1, (hh, ww)).astype(np.float32), (0, 0), 1.2 * ss)
    veio /= max(float(veio.std()), 1e-6)
    luz = 1 + qa["luz"] * (rel - 0.5)
    cor = np.float32(qa["madeira"])[None, None] * (luz * (1 + 0.5 * qa["veio"] * veio))[..., None]
    fase = np.mod(u, qa["ripa_px"] * s)
    jp = qa["junta_px"] * s
    jt = np.clip(1 - np.abs(fase - jp / 2) / (jp / 2 + 0.5 / ss), 0, 1) * qa["junta_forca"]
    cor = cor * (1 - jt[..., None]) + np.float32(qa["junta"]) * jt[..., None]
    cp = qa["contorno_px"] * s
    borda = dentro & ((u < cp) | (u > Lp - cp) | (np.abs(w_) > W / 2 - cp))
    cor[borda] = np.float32(qa["contorno"])
    A = cv2.resize(dentro.astype(np.float32), (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    C = cv2.resize(cor * dentro[..., None], (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    reg = reg * (1 - A[..., None]) + C
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def paineis_pivotantes(out, mp, q=PIVOTANTES):
    import um_pav_casaa_1111 as U
    m = _local(out, mp, (1355, 545, 1430, 715))
    xm = (q["x"][0] + q["x"][1]) / 2
    passo = (q["y"][1] - q["y"][0]) / q["n"]
    L = q["comp"] * passo
    c = s = np.sqrt(0.5)
    e = q["esp_px"] / 2                                        # o arremate redondo da lâmina preta
    for k in range(q["n"]):
        cy = q["y"][0] + passo * (k + 0.5)
        p0 = (xm - (L / 2 + e) * c, cy - (L / 2 + e) * s)
        p1 = (xm + (L / 2 + e) * c, cy + (L / 2 + e) * s)
        _tabua(out, m, p0, p1, q["esp_px"] + q["cobre_px"], U.FOLHAS_1P, np.random.default_rng(1740 + k))
    print("    gourmet: os 2 painéis pivotantes no ripado de nogueira, nas mesmas medidas")


def _remenda(out, m, r, ds, filtro="marrom", lim=12):
    """O retângulo r (px da final) refeito com o piso de perto: cada px marcado pelo filtro ("marrom": o piso escuro
    antigo, quente e mais escuro que o piso; "escuro": qualquer mancha mais escura; uma função da região; None: todos)
    recebe o px deslocado pelo primeiro d de ds (px da final) que caia num piso limpo (o tom da 1ª fonte ± lim)."""
    s = m.s
    rm = m.ret(r)
    X0, Y0, X1, Y1 = int(np.floor(rm[0])), int(np.floor(rm[1])), int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    h, w = Y1 - Y0, X1 - X0
    A = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), (h, w))
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    fontes = []
    for d in ds:
        dx, dy = int(round(d[0] * s)), int(round(d[1] * s))
        fontes.append(out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32))
    Lf = float(np.median(fontes[0].mean(-1)))
    L, quente = reg.mean(-1), reg[..., 2] - reg[..., 0]
    if filtro is None:
        marca = np.ones((h, w), bool)
    elif filtro == "marrom":
        marca = (quente > 12) & (L < Lf - lim)
    elif filtro == "escuro":
        marca = L < Lf - lim
    else:
        marca = filtro(reg)
    if filtro is not None:
        k = max(1, int(round(0.5 * s)))
        marca = cv2.dilate(marca.astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
    novo, feito = reg.copy(), np.zeros((h, w), bool)
    for F in fontes:
        ok = marca & ~feito
        if filtro is not None:
            ok &= np.abs(F.mean(-1) - Lf) < max(lim, 14)
        novo[ok], feito = F[ok], feito | ok
    a = A * feito
    if filtro is not None and s > 1.5:
        a = A * np.clip(cv2.GaussianBlur(feito.astype(np.float32), (0, 0), 0.35 * s) * 1.6, 0, 1)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)


def piso_banho_gourmet(out, mp, q=BANHO_G):
    m = _local(out, mp, q["caixa"])
    for r, ds, filtro in q["remendos"]:
        _remenda(out, m, r, ds, filtro)
    rc = m.reti(q["caixa"])
    par = CB._Paredes(out, rc, m.s)
    for sg, e in q["tracos"]:
        CB._apaga_traco(out, m, sg, e, par)
    print("    banho gourmet: o piso escuro antigo rente à parede de cima, a marca preta, a linha pontilhada e a emenda")


def portas_servico(out, mp, q=SERVICO):
    m = _local(out, mp, q["caixa"])
    for r, amostra in q["bordas"]:
        x0, y0, x1, y1 = m.reti(amostra)
        cor = tuple(float(v) for v in np.median(out[y0:y1, x0:x1].reshape(-1, 3), axis=0))
        CB.pintar(out, m, [(r, "ret", cor, 0)])
    for r, ds, filtro in q["remendos"]:
        _remenda(out, m, r, ds, filtro)
    f = q["folha"]
    _remenda(out, m, f["limpa"][0], [f["limpa"][1]], None)
    CB.pintar(out, m, [(f["ret"], "ret", f["cor"], 0), (f["ret"], "contorno", f["contorno"], f["contorno_px"])])
    print("    serviço: paredes atrás das folhas do louceiro e da despensa, o piso escuro antigo junto das folhas, as "
          "manchinhas, a folha de correr reta")


def poltrona_varanda(out, mp, q=POLTRONA):
    """A faixa refeita no Bege Bahia limpo, com a sombra da poltrona na faixa pela razão (tom/tom limpo) das colunas de
    fora, interpolada de um lado ao outro."""
    m = _local(out, mp, q["caixa"])
    s = m.s
    fonte = out.copy()
    Lf = fonte.astype(np.float32).mean(-1)

    def coluna(u):
        a, b = int(np.floor(m.x(u))), max(int(np.floor(m.x(u))) + 1, int(np.ceil(m.x(u + 1))))
        return Lf[:, a:b].mean(1)
    cl, cr = coluna(q["esq"]), coluna(q["dir"])
    limpo = np.concatenate([np.arange(int(m.y(a)), int(m.y(b))) for a, b in q["limpo"]])
    rl, rr = np.clip(cl / np.median(cl[limpo]), 0, 1), np.clip(cr / np.median(cr[limpo]), 0, 1)
    rl = cv2.GaussianBlur(rl[:, None], (1, 0), sigmaX=0.1, sigmaY=0.8 * s).ravel()
    rr = cv2.GaussianBlur(rr[:, None], (1, 0), sigmaX=0.1, sigmaY=0.8 * s).ravel()
    dx = int(round(q["dx"] * s))
    for y0, y1 in q["linhas"]:
        rm = m.ret((q["x"][0], y0, q["x"][1], y1))
        X0, Y0, X1, Y1 = int(np.floor(rm[0])), int(np.floor(rm[1])), int(np.ceil(rm[2])), int(np.ceil(rm[3]))
        A = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), (Y1 - Y0, X1 - X0))
        F = fonte[Y0:Y1, X0 + dx:X1 + dx].astype(np.float32)
        t = np.clip((np.arange(X0, X1) + 0.5 - rm[0]) / (rm[2] - rm[0]), 0, 1)[None, :]
        razao = rl[Y0:Y1, None] * (1 - t) + rr[Y0:Y1, None] * t
        novo = F * razao[..., None]
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - A[..., None]) + novo * A[..., None]), 0, 255).astype(np.uint8)
    print("    varanda: a faixa borrada acima e abaixo da poltrona da direita pelo Bege Bahia de perto")


def mesa_escritorio(out, mp, q=ESCRITORIO):
    m = _local(out, mp, q["caixa"])
    for r, d in q["limpa"]:
        _remenda(out, m, r, [d], None)
    CB.sombra(out, m, q["mesa"], q["sombra"])
    CB.pintar(out, m, [(q["mesa"], "contorno", q["contorno"], q["contorno_px"])])
    print("    escritório: o tampo de nogueira sem a borda cinza e o resto da mesa antiga, com o contorno fino")


PASSOS = (banco_b1, arandelas_l2, soleira_garagem, vao_hall_garagem, painel_garagem, paineis_pivotantes,
          piso_banho_gourmet, portas_servico, poltrona_varanda, mesa_escritorio)


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
        mp.ref = final
        out = aplicar(doze, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

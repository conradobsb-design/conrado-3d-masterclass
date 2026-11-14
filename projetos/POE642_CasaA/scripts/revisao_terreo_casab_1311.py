"""A revisão do 12K do Térreo da Casa B (13/11): os apontamentos do usuário sobre o 12K, na final e no 12K.

Chamado no fim do `regras_terreo_casab_1311.aplicar` (`aplicar(RT, Q, out, par, reg)`; `RT` é o próprio módulo das
regras, passado para não importar uma 2ª cópia dele quando ele roda como script). As peças desenhadas aqui entram no
registro do 12K com o tipo "rv_..." e são redesenhadas nítidas na escala dele (`peca_12k`); a cama da suíte 3, copiada
da suíte 1, vem da saída do Topaz (`copias_12k`).
- **Banco do deck (`BANCO`; "CORRIJA O ACABAMENTO DO BANCO E SEU CONTORNO"; "O BANCO TEM UM TOM ÚNICO, SEM VARIAÇÃO. TOM
  SÓLIDO BRONZE"):** o L do PDF (0,80 m) no bronze dos brises, chapado, com o fio escuro da borda (as réguas de madeira
  da 1ª rodada saíram); o contorno de fora no cinza 80 de 2 px, como o da borda de baixo do deck.
- **Borda de cima do deck (`CONTORNO_DECK`; "CORRIJA O ACABAMENTO SUPERIOR DO PISO DE MADEIRA DO DECK"):** o mesmo
  contorno cinza 80 de 2 px na borda de cima (o deck encostava direto no travertino) e no trecho da direita até a
  parede.
- **Piscina (`PISCINA`; "O AZUL SÓ PODE IR ATÉ A DIVISÓRIA MAIS À ESQUERDA"):** a faixa azul entre o deck (a linha do
  PDF) e o vidro da esquerda vira a madeira do deck (as tábuas continuam, a mesma linha 4 px antes).
- **Lavatório gourmet (`BANCADA_LAV`; "SUBSTITUA A BANCADA DO LAVATÓRIO POR TRAVERTINO, IGUAL DA CUBA ESCULPIDA"):** a
  bancada do PDF em travertino no tom da cuba esculpida (os veios deitados, os poros), o fio da borda; as 2 cubas
  esculpidas de volta por cima.
- **Batentes (`BATENTES_EXTRA`, `batentes`; "REMOVA O BATENTE DA PORTA DA DESPENSA", "AO APARECER UM VÃO ENTRE O
  BATENTE E A PORTA, COMPLETE COM PAREDE"):** nas 25 portas de giro do PDF, os batentes (as peças brancas finas na ponta
  da parede, junto ao arco) viram parede, até a face da folha quando ela encosta (quina com quina).
- **Porta de correr da cozinha (`CORRER_COZ`; "CORRIJA AS FALHAS DA PORTA DE CORRER, DEIXANDO COM PERFEITO
  ACABAMENTO"):** a folha (o vidro com o perfil preto) redesenhada reta, o piso embaixo dela sem os pontinhos; a
  parede fica como no PDF ("NÃO AUMENTE A PAREDE").
- **Porta do banho da suíte 2 (`FOLHA_B2`):** as manchas escuras entre a folha e a parede saem (o piso de cima); a folha
  redesenhada (a madeira clara das folhas, com o fio).
- **Paredes do louceiro, da despensa e da área de serviço (`FAIXA_PAREDE`; "CORRIJA O ACABAMENTO DESSAS PAREDES"):** as
  sombras sujas embaixo da parede saem (o piso logo abaixo); os batentes, pela regra de cima.
- **Cama da suíte 3 (`CAMA_S3`; "CORRIJA O CONTORNO DA CAMA DA SUÍTE 3"):** a cama da suíte 3 era montada em faixas
  desencontradas; entra a da suíte 1 (a mesma, 2,00 x 2,00 m), girada com a cabeceira embaixo, com a sombra curta.
- **Refrigerador (`REFRIGERADOR`; "FALTOU REPRESENTAR O REFRIGERADOR NO VÃO"):** o do PDF (1,40 x 0,75 m) no vão
  junto ao BH gourmet, com a geladeira inox G2 da cozinha, a frente (os puxadores) para a varanda.
- **Quarto de serviço (`QUARTO_SERV`; "CORRIJA CONTORNO DA CAMA, JANELAS DO QUARTO DE SERVIÇO"):** a moldura marrom em
  volta da cama sai (o piso), a sombra curta da cama; a janela de 2 folhas de correr redesenhada pelo PDF (os marcos, o
  peitoril claro, as folhas com o perfil preto e o vidro claro).

  python3 revisao_terreo_casab_1311.py --antes-depois <commit>
grava os antes e depois da final e do 12K (A) contra o `<commit>`.
"""

import argparse
import contextlib
import io
import json
import subprocess
import sys
import types
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402

PX_M = B1.PX_M
K = 8                         # px por px da final nos desenhos daqui (o 12K é 3,6x)
PAREDE = (80, 80, 80)
PERFIL = (34, 34, 36)         # o preto das esquadrias (`regras_terreo_casab_1311.ESQUADRIAS_TB`)

BANCO = {"poli": [(615.9, 1378.6), (663.6, 1378.6), (663.6, 1660.1), (896.5, 1660.1), (896.5, 1707.9),
                  (615.9, 1707.9)],
         "canto": ((615.9, 1707.9), (663.6, 1660.1)),        # a esquadria a 45°: acima dela, réguas em pé
         "regua_m": 0.10, "junta_m": 0.008, "tom": (56, 81, 110), "var": 0.05, "veio": 0.045,
         "junta": 0.62, "fio": (30, 42, 55), "fio_px": 0.6, "luz": 1.18, "luz_px": 0.9, "semente": 1311,
         # (usuário: "O BANCO TEM UM TOM ÚNICO, SEM VARIAÇÃO. TOM SÓLIDO BRONZE") o bronze dos brises da Casa B (a
         # mediana das 2 linhas do brise da fachada), chapado, só com o fio escuro da borda
         "solido": True, "bronze": (47, 71, 104), "fio_solido": (28, 40, 56)}
CONTORNO_DECK = {"cor": PAREDE, "rets": [(613.9, 1376.6, 1095.5, 1378.6),     # a borda de cima (deck e banco)
                                         (1093.5, 1378.6, 1095.5, 1475.0),     # a da direita, até a parede
                                         (613.9, 1378.6, 615.9, 1709.9),       # a de fora do banco
                                         (613.9, 1707.9, 898.5, 1709.9),
                                         (896.5, 1701.0, 898.5, 1709.9)]}
PISCINA = {"x": 747.2, "y": (890, 1093), "vidro_lum": 80, "busca_px": 9, "azul": 30}
# (usuário: "TEMOS UMA DUPLICAÇÃO ERRADA AQUI ... NO LAVATORIO GOURMET") entre a bancada e a janela ficavam as bases das
# torneiras e as bordas das cubas de antes (no 12K, torneiras em dobro): a faixa (`faixa_y`) sob as cubas (`faixa_x`)
# com o perfil de uma coluna limpa (`faixa_ref_x`)
BANCADA_LAV = {"c": (1218.9, 1618.3, 1427.9, 1641.3), "tom": (188, 207, 225), "fio": 0.80, "semente": 1311,
               "faixa_y": (1641, 1646), "faixa_x": [(1222, 1267), (1273, 1374), (1380, 1425)], "faixa_ref_x": (1238, 1266),
               "veio": 0.010, "faixa": 0.016, "poros": 6, "poro_esc": 0.05, "forca": 0.8,
               "cubas": ["banho-1/cuba-esculpida-travertino"]}
BATENTES_EXTRA = []            # (x0, y0, x1, y1) px a mais, se a busca não pegar
# (usuário: "NÃO FOI ISSO QUE EU PEDI. ERA SÓ PARA MELHORAR O ASPECTO DA PORTA ... NÃO AUMENTE A PAREDE") só a folha
# e o piso embaixo dela; a parede fica como no PDF
CORRER_COZ = {"parede": [],
              "folha": (1646.5, 1289.9, 1757.5, 1292.9), "vidro": (222, 224, 225), "perfil_px": 0.55,
              "limpa": (1640, 1293, 1765, 1301), "desloc_px": 9}
FOLHA_B2 = {"folha": (2657.9, 602.5, 2705.7, 604.8), "madeira": (118, 145, 177), "fio": 0.78,
            "limpa": (2659, 605, 2707, 608), "fonte_dy": -9}
FAIXA_PAREDE = {"px": (1822, 1371, 2253, 1378), "dy": 9, "escuro": 14}
CAMA_S3 = {"de": (1945.8, 382.0, 2065.2, 501.4), "para": (2460.0, 711.6, 2579.4, 831.0), "margem": 1.0}
QUARTO_SERV = {"cama": (1916.8, 1611.0, 2036.2, 1664.2), "anel_px": 5, "grao_px": (1925, 1515, 1995, 1545), "nao": (1902, 1666, 2044, 1690),
               "janela": {"vao": (1932.4, 1666.1, 2022.0, 1678.1),
                          "marcos": [(1932.4, 1666.1, 1934.8, 1678.1), (2019.6, 1666.1, 2022.0, 1678.1)],
                          "folhas": [((1934.8, 1672.1, 1979.6, 1675.1), (1939.6, 1974.8)),
                                     ((1974.8, 1675.1, 2019.6, 1678.1), (1979.6, 2014.8))],
                          "peitoril": (210, 221, 238), "vidro": (226, 230, 232), "marco": (236, 238, 240),
                          "perfil_px": 0.55}}
# (13/11, "FALTOU REPRESENTAR O REFRIGERADOR NO VÃO") o refrigerador do PDF (ARQ_LAYOUT, 1,40 x 0,75 m) no vão junto
# ao BH gourmet: a geladeira inox G2 da cozinha (o tampo escovado, a frente com os 2 puxadores) para a varanda, em cima
REFRIGERADOR = {"png": "02-terreo/cozinha/geladeira-inox.png", "c": (1117.4, 1481.0, 1201.0, 1525.8), "rot": 2}
# (usuário: "A REPRESENTAÇÃO DAS PORTAS DE CORRER FICARAM MUITO ERRADAS. CORRIJA!", com o recorte do PDF) a parede de
# baixo do banho master pelo PDF: os 2 bolsos em cinza (as portas de correr telescópicas, 2 folhas de cada lado: a do
# bolso e a do vão), os nichos brancos das pontas, os 2 batentes do vão; o piso da suíte por baixo do cinza que passava
# da face (`piso_px`)
PORTAS_BM = {"parede": [(1236.2, 503.6, 1244.0, 508.9), (1289.4, 501.8, 1344.8, 503.6), (1235.6, 508.9, 1344.8, 510.7),
                        (1244.0, 503.6, 1344.8, 508.9), (1452.3, 501.8, 1506.7, 503.6), (1452.3, 508.9, 1550.3, 510.7),
                        (1452.3, 503.6, 1550.3, 508.9), (1550.3, 503.6, 1552.1, 508.9),
                        (1344.8, 501.8, 1346.6, 507.2), (1450.5, 501.8, 1452.3, 507.2)],
             "nichos": [(1245.8, 501.8, 1289.4, 507.6), (1506.7, 501.8, 1550.3, 507.3)],
             "folhas": [(1296.8, 507.5, 1344.8, 510.4), (1452.3, 507.5, 1500.4, 510.4), (1341.8, 507.8, 1392.6, 510.1),
                        (1404.5, 507.8, 1455.3, 510.1)],
             "vao": (1346.6, 501.8, 1450.5, 507.8), "vao_fonte_dy": -9,
             "piso_px": (1234, 511, 1556, 519), "nicho": (232, 234, 236), "folha": (236, 238, 240), "perfil_px": 0.5}
# (usuário: "CORRIGIR O PISO E PAREDE", o hall junto à suíte 3) a face da parede de cima reta em y 943,6 (do PDF; o render
# a encurtava depois de x 2452); o toco de parede e o caixilho de vidro emoldurado abaixo dele pelo PDF; o piso do hall
# interno no retângulo mais claro do render (o PDF muda de piso só em x 2537), sem a linha clara sob o vaso
# (14/11, "CORRIJA A SOLEIRA DA PORTA PRINCIPAL, ELA VAI DE FORA A FORA. CORRIJA TAMBÉM A PAREDE DE CIMA, ONDE A PORTA E
# A SOLEIRA ENCOSTA"; "ISSO ESTÁ ME PARECENDO UM VIDRO TAMBÉM SOBRE A SOLEIRA"; "E DO OUTRO LADO DA PORTA TAMBÉM") nos
# dois lados da porta pivotante o PDF tem a mesma peça: o vidro fixo (a lâmina de 3 px, a das folhas de vidro das
# varandas) no caixilho, em pé sobre a soleira (os tracejados são as bordas da soleira por baixo). A soleira vai da
# parede de cima (o toco, y 955,6) à de baixo (y 1182,5); os vidros por cima dela no vidro claro (`final3840_casab
# .BOXES_VIDRO`); o toco reto, com as bordas limpas. Antes (13/11) o de cima era um caixilho branco e, embaixo, a final
# tinha parede no lugar do vidro.
HALL = {"parede": [(2410.0, 938.0, 2526.6, 943.6), (2526.55, 943.63, 2538.49, 955.57)],
        "toco_limpo": [((2523, 944, 2527, 956), -6), ((2539, 945, 2544, 956), 6)],
        # (linhas, colunas, de onde: "v" a linha de cima da fonte / "h" o deslocamento em x): a soleira vem da parte
        # livre (de cima para baixo); o piso dos lados, da coluna do lado (o tom continua); o tracejado de fora, que
        # começa em x 2541, y 1182, vai até a parede
        # ("r": a coluna do piso do lado repetida, onde a planta está perto)
        "soleira": [((955, 986), (2527, 2539), "v", 1020), ((955, 986), (2539, 2545), "h", 6),
                    ((955, 986), (2525, 2527), "r", 2524),
                    ((1152, 1183), (2527, 2539), "v", 1100), ((1152, 1181), (2520, 2527), "h", -8),
                    ((1181, 1183), (2518, 2527), "v", 1178), ((1152, 1180), (2539, 2545), "h", 6),
                    ((1180, 1183), (2539, 2541), "h", 3)],
        "parede_baixo": (2517.6, 1182.47, 2538.49, 1185.0),
        "vidros": [(2529.54, 955.57, 2532.52, 985.43), (2529.54, 1152.61, 2532.52, 1182.47)],
        "piso": (2448, 944, 2526, 1009), "piso_fonte": (2386, 946, 2446, 1006)}
ANTES_DEPOIS = {"deck_banco": (600, 1360, 1110, 1720), "piscina_faixa": (720, 880, 800, 1110),
                "lavatorio": (1200, 1590, 1450, 1665), "suite_master_piso": (1015, 385, 1215, 505),
                "cortina_suite2": (2240, 320, 2560, 360), "porta_banho2": (2630, 585, 2720, 625),
                "porta_correr_cozinha": (1580, 1265, 1770, 1305), "paredes_louceiro_despensa": (1815, 1350, 2260, 1420),
                "cama_suite3": (2440, 695, 2600, 845), "quarto_servico": (1900, 1598, 2050, 1685),
                "refrigerador": (1085, 1460, 1235, 1545),
                "portas_banho_master": (1225, 470, 1570, 530),
                "hall_piso_parede": (2400, 920, 2570, 1025)}


# ----------------------------------------------------------------------------------------------------------------------
def _cob1(a0, a1, n, o):
    """A cobertura (0..1) de [a0, a1) em cada um dos n sub-px (1/K) a partir de o."""
    c = (np.arange(n) + 0.5) / K + o
    return np.clip(np.minimum(c + 0.5 / K, a1) - np.maximum(c - 0.5 / K, a0), 0, 1 / K) * K


def _ret(r, X0, Y0, w, h):
    x0, y0, x1, y1 = r
    return np.outer(_cob1(y0, y1, h * K, Y0), _cob1(x0, x1, w * K, X0)).astype(np.float32)


def _poli(pts, X0, Y0, w, h):
    m = np.zeros((h * K, w * K), np.uint8)
    p = np.int32(np.round((np.float32(pts) - [X0, Y0]) * K * 16))
    cv2.fillPoly(m, [p], 255, cv2.LINE_AA, shift=4)
    return m.astype(np.float32) / 255


def _compor(Cp, A, m, cor):
    m = m[..., None]
    Cp[:] = np.float32(cor)[None, None] * m + Cp * (1 - m)
    A[:] = m[..., 0] + A * (1 - m[..., 0])


def _caixa(c, folga=1):
    x0, y0, x1, y1 = c
    X0, Y0 = int(np.floor(x0)) - folga, int(np.floor(y0)) - folga
    X1, Y1 = int(np.ceil(x1)) + folga, int(np.ceil(y1)) + folga
    return X0, Y0, X1 - X0, Y1 - Y0


def _bgra(Cp, A):
    C = Cp / np.maximum(A, 1e-6)[..., None]
    return np.dstack([C, A * 255]).astype(np.float32)


def vetor_desenho(it):
    """Os retângulos ({"t": "ret", "c", "cor"}), os contornos ({"t": "fio", "c", "cor", "px"}) e os polígonos
    ({"t": "poli", "pts", "cor"}) de `it["prims"]`, em K x; (P, cx, cy, larg, alt)."""
    X0, Y0, w, h = _caixa(it["c"])
    Cp = np.zeros((h * K, w * K, 3), np.float32)
    A = np.zeros((h * K, w * K), np.float32)
    for p in it["prims"]:
        if p["t"] == "ret":
            m = _ret(p["c"], X0, Y0, w, h)
        elif p["t"] == "poli":
            m = _poli(p["pts"], X0, Y0, w, h)
        else:                                   # "fio": o contorno de dentro do retângulo, `px` de largura
            x0, y0, x1, y1 = p["c"]
            e = p["px"]
            m = np.clip(_ret(p["c"], X0, Y0, w, h) - _ret((x0 + e, y0 + e, x1 - e, y1 - e), X0, Y0, w, h), 0, 1)
        _compor(Cp, A, m, p["cor"])
    return _bgra(Cp, A), X0 + w / 2, Y0 + h / 2, float(w), float(h)


def banco_desenho(it, q=BANCO):
    """O banco do deck em réguas de madeira (K x): (P, cx, cy, larg, alt)."""
    pts = np.float32(q["poli"])
    X0, Y0, w, h = _caixa((pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()))
    H, W = h * K, w * K
    rng = np.random.default_rng(q["semente"])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x, y = (xx + 0.5) / K + X0, (yy + 0.5) / K + Y0
    (ax, ay), (bx, by) = q["canto"]
    em_pe = ((bx - ax) * (y - ay) - (by - ay) * (x - ax)) < 0         # acima da diagonal do canto: o braço de pé
    if q.get("solido"):
        a = _poli(pts, X0, Y0, w, h)
        C = np.empty((H, W, 3), np.float32)
        C[:] = np.float32(q["bronze"])
        er = cv2.erode((a > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8),
                       iterations=max(1, int(round(q["fio_px"] * K / 1.5))))
        fio = np.clip(a - cv2.GaussianBlur(er.astype(np.float32), (0, 0), 0.6), 0, 1)
        C = C * (1 - fio[..., None]) + np.float32(q["fio_solido"])[None, None] * fio[..., None]
        P = np.dstack([C, a * 255]).astype(np.float32)
        return P, X0 + w / 2, Y0 + h / 2, float(w), float(h)
    rg, jt = q["regua_m"] * PX_M, q["junta_m"] * PX_M
    u = np.where(em_pe, x - pts[0, 0], y - pts[2, 1])                 # a coordenada através das réguas
    v = np.where(em_pe, y, x)                                         # a do comprimento
    n = np.floor(u / rg).astype(np.int32)
    f = u - n * rg
    tons = 1 + q["var"] * rng.standard_normal(64).astype(np.float32)
    ton = tons[np.clip(n, 0, 63) + np.where(em_pe, 0, 32) % 64]
    # o veio: ruído esticado no comprimento de cada braço
    r1 = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), sigmaX=0.6 * K, sigmaY=14 * K)
    r2 = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), sigmaX=14 * K, sigmaY=0.6 * K)
    veio = np.where(em_pe, r1 / max(r1.std(), 1e-6), r2 / max(r2.std(), 1e-6))
    L = ton * (1 + q["veio"] * veio)
    junta = np.clip(1 - np.minimum(f, rg - f) / max(jt, 1e-3), 0, 1)                 # 1 na junta
    L = L * (1 - (1 - q["junta"]) * junta)
    C = np.float32(q["tom"])[None, None] * L[..., None]
    a = _poli(pts, X0, Y0, w, h)
    # a luz na quina de dentro (o tampo pega a luz do alto à direita) e o fio escuro da borda
    lp = q["luz_px"]
    luz = np.clip(_ret((663.6 - lp, 1378.6, 663.6, 1660.1 + lp), X0, Y0, w, h)
                  + _ret((663.6 - lp, 1660.1, 896.5, 1660.1 + lp), X0, Y0, w, h), 0, 1)
    C = C * (1 + (q["luz"] - 1) * luz[..., None])
    er = cv2.erode((a > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8),
                   iterations=max(1, int(round(q["fio_px"] * K / 1.5))))
    fio = np.clip(a - cv2.GaussianBlur(er.astype(np.float32), (0, 0), 0.6), 0, 1)
    C = C * (1 - fio[..., None]) + np.float32(q["fio"])[None, None] * fio[..., None]
    P = np.dstack([np.clip(C, 0, 255), a * 255]).astype(np.float32)
    return P, X0 + w / 2, Y0 + h / 2, float(w), float(h)


def bancada_desenho(it, q=BANCADA_LAV):
    """A bancada do lavatório em travertino no tom da cuba esculpida (K x): (P, cx, cy, larg, alt)."""
    x0, y0, x1, y1 = q["c"]
    X0, Y0, w, h = _caixa(q["c"])
    Qk = types.SimpleNamespace(px_m=PX_M * K)
    with contextlib.redirect_stdout(io.StringIO()):
        D = FA.travertino_bruto(Qk, h * K, w * K, q["semente"], q["veio"], q["faixa"], q["poros"], q["poro_esc"],
                                forca=q["forca"])
    D = D / float(np.mean(D))
    C = np.float32(q["tom"])[None, None] * D[..., None]
    a = _ret(q["c"], X0, Y0, w, h)
    fio = np.clip(a - _ret((x0 + 0.5, y0 + 0.5, x1 - 0.5, y1), X0, Y0, w, h), 0, 1)     # a borda (sem a da parede)
    C = C * (1 - (1 - q["fio"]) * fio[..., None])
    P = np.dstack([np.clip(C, 0, 255), a * 255]).astype(np.float32)
    return P, X0 + w / 2, Y0 + h / 2, float(w), float(h)


def peca_12k(it):
    """(P, cx, cy, larg, alt, giro, sombras) dos tipos daqui, para o `pecas_12k` (e para a final, em `pousar`)."""
    if it["tipo"] == "rv_vetor":
        P, cx, cy, w, h = vetor_desenho(it)
    elif it["tipo"] == "rv_banco":
        P, cx, cy, w, h = banco_desenho(it)
    elif it["tipo"] == "rv_bancada":
        P, cx, cy, w, h = bancada_desenho(it)
    else:
        return None
    return P, cx, cy, w, h, 0.0, BT.SOMBRAS[it.get("sombra")]


def pousar(out, it, par=None):
    P, cx, cy, w, h, ang, sb = peca_12k(it)
    o = BT.pousar(out.astype(np.float32), P, cx, cy, w, h, ang, sb, PX_M, nao=par)
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def deck(out, par, reg):
    # o banco de antes (e o contorno claro dele) sai inteiro: o banco novo cobre o L do PDF; por fora, o contorno
    it = {"tipo": "rv_banco", "sombra": None}
    out = pousar(out, it, None)
    reg["pecas"].append(it)
    prims = [{"t": "ret", "c": r, "cor": CONTORNO_DECK["cor"]} for r in CONTORNO_DECK["rets"]]
    rs = np.float32(CONTORNO_DECK["rets"])
    it = {"tipo": "rv_vetor", "nome": "contorno_deck", "c": [float(rs[:, 0].min()), float(rs[:, 1].min()),
                                                              float(rs[:, 2].max()), float(rs[:, 3].max())],
          "prims": prims}
    out = pousar(out, it, None)
    reg["pecas"].append(it)
    print("    deck: o banco no bronze dos brises, chapado, com o fio da borda, e o contorno cinza 80 de 2 px na borda de "
          "cima, na da direita e por fora do banco")
    return out


def piscina(out, q=PISCINA):
    x = int(np.ceil(q["x"] - 0.5))
    n = 0
    for y in range(*q["y"]):
        lum = out[y, x:x + q["busca_px"]].astype(np.float32).mean(axis=1)
        esc = np.nonzero(lum < q["vidro_lum"])[0]
        if not len(esc):
            continue
        c = x + int(esc[0])
        lin = out[y, x:c].astype(np.int16)
        if not len(lin) or not ((lin[:, 0] - lin[:, 2]) > q["azul"]).any():
            continue
        d = c - x
        out[y, x:c] = out[y, x - d:c - d]
        n += 1
    print(f"    piscina: a faixa azul à esquerda do vidro virou o deck ({n} linhas)")
    return out


def bancada_lavatorio(out, par, reg, q=BANCADA_LAV):
    it = {"tipo": "rv_bancada", "sombra": None}
    out = pousar(out, it, par)
    # as cubas de volta por cima (e a bancada antes delas no registro do 12K)
    idx = [i for i, p in enumerate(reg["pecas"]) if p.get("tipo") == "bib" and p.get("png") in q["cubas"]
           and q["c"][0] <= p["cx"] <= q["c"][2] and q["c"][1] - 12 <= p["cy"] <= q["c"][3]]
    for i in idx:
        out = _RT["m"].pousar_bib(out, reg["pecas"][i], par)
    reg["pecas"].insert(min(idx) if idx else len(reg["pecas"]), it)
    y0, y1 = q["faixa_y"]
    ref = np.median(out[y0:y1, q["faixa_ref_x"][0]:q["faixa_ref_x"][1]].astype(np.float32), axis=1)
    for xa, xb in q["faixa_x"]:
        out[y0:y1, xa:xb] = np.round(ref[:, None, :]).astype(np.uint8)
    print(f"    lavatório gourmet: a bancada em travertino no tom da cuba esculpida, as {len(idx)} cubas por cima")
    return out


_RT = {}


def _arcos(Q):
    res = []
    for i, d in enumerate(Q.desenhos):
        if d.get("layer") != "ARQ_PAREDE" or d["type"] != "s" or not any(it[0] == "c" for it in d["items"]):
            continue
        x0, y0, x1, y1 = _q2(Q, d["rect"])
        w, h = x1 - x0, y1 - y0
        if 18 <= w <= 80 and 18 <= h <= 80 and abs(w - h) < 0.35 * max(w, h):
            res.append((x0, y0, x1, y1))
    return res


def _q2(Q, r):
    a = Q.p2q(r.x0, r.y0)
    b = Q.p2q(r.x1, r.y1)
    return min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])


def batentes(Q, out, par, reg, extra=BATENTES_EXTRA):
    """Os batentes das portas de giro viram parede: as peças brancas finas da ARQ_PAREDE perto do arco, com a parede
    (o cinza da final) de um lado, até a face da folha quando ela encosta."""
    arcos = _arcos(Q)
    brancos = []
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or d["type"] != "f" or not d.get("fill") or min(d["fill"]) < 0.95:
            continue
        brancos.append(_q2(Q, d["rect"]))
    folhas = [b for b in brancos if max(b[2] - b[0], b[3] - b[1]) >= 20 and min(b[2] - b[0], b[3] - b[1]) <= 3.6]
    I = out.astype(np.int16)
    cinza = (np.abs(I - np.int16(PAREDE)).max(axis=2) <= 14)
    rets = []
    for (ax0, ay0, ax1, ay1) in arcos:
        for b in brancos:
            x0, y0, x1, y1 = b
            w, h = x1 - x0, y1 - y0
            if not (1.4 <= min(w, h) <= 3.6 and 5.0 <= max(w, h) <= 14):
                continue
            if x1 < ax0 - 12 or x0 > ax1 + 12 or y1 < ay0 - 12 or y0 > ay1 + 12:
                continue
            # a parede de um dos lados (no sentido da largura do batente)
            X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
            if w < h:
                lados = [cinza[Y0 + 1:Y1 - 1, X0 - 2:X0].mean() if X0 >= 2 else 0, cinza[Y0 + 1:Y1 - 1, X1:X1 + 2].mean()]
            else:
                lados = [cinza[Y0 - 2:Y0, X0 + 1:X1 - 1].mean() if Y0 >= 2 else 0, cinza[Y1:Y1 + 2, X0 + 1:X1 - 1].mean()]
            if max(lados) < 0.6:
                continue
            r = [x0, y0, x1, y1]
            # a folha que encosta na ponta do batente: a parede vai até a face de lá dela
            for f in folhas:
                if w < h and abs(f[1] - y1) < 0.7 and f[0] < x1 + 0.7 and f[2] > x0 - 0.7 and (f[2] - f[0]) < 4:
                    r[0], r[2] = min(r[0], f[0]), max(r[2], f[2])
                if w < h and abs(f[3] - y0) < 0.7 and f[0] < x1 + 0.7 and f[2] > x0 - 0.7 and (f[2] - f[0]) < 4:
                    r[0], r[2] = min(r[0], f[0]), max(r[2], f[2])
                if w >= h and abs(f[0] - x1) < 0.7 and f[1] < y1 + 0.7 and f[3] > y0 - 0.7 and (f[3] - f[1]) < 4:
                    r[1], r[3] = min(r[1], f[1]), max(r[3], f[3])
                if w >= h and abs(f[2] - x0) < 0.7 and f[1] < y1 + 0.7 and f[3] > y0 - 0.7 and (f[3] - f[1]) < 4:
                    r[1], r[3] = min(r[1], f[1]), max(r[3], f[3])
            if r not in rets:
                rets.append(r)
    rets += [list(r) for r in extra]
    for r in rets:                               # um desenho por batente (todos juntos, a caixa seria a planta)
        it1 = {"tipo": "rv_vetor", "nome": "batente", "c": [float(v) for v in r],
               "prims": [{"t": "ret", "c": [float(v) for v in r], "cor": PAREDE}]}
        out = pousar(out, it1, None)
        reg["pecas"].append(it1)
    print(f"    batentes: {len(rets)} viraram parede (nas {len(arcos)} portas de giro do PDF), até a face da folha")
    return out


def correr_cozinha(out, reg, q=CORRER_COZ):
    x0, y0, x1, y1 = q["limpa"]
    d = q["desloc_px"]
    out[y0:y1, x0:x1] = out[y0 + d:y1 + d, x0:x1]
    f = q["folha"]
    prims = [{"t": "ret", "c": list(r), "cor": PAREDE} for r in q["parede"]]
    prims += [{"t": "ret", "c": list(f), "cor": q["vidro"]},
              {"t": "fio", "c": list(f), "cor": PERFIL, "px": q["perfil_px"]}]
    rs = np.float32(list(q["parede"]) + [f])
    it = {"tipo": "rv_vetor", "nome": "porta_correr_cozinha",
          "c": [float(rs[:, 0].min()), float(rs[:, 1].min()), float(rs[:, 2].max()), float(rs[:, 3].max())],
          "prims": prims}
    out = pousar(out, it, None)
    reg["pecas"].append(it)
    print("    porta de correr da cozinha: a folha reta, com o perfil preto; o piso embaixo sem os pontinhos (a parede "
          "como estava)")
    return out


def folha_banho2(out, reg, q=FOLHA_B2):
    x0, y0, x1, y1 = q["limpa"]
    d = q["fonte_dy"]
    out[y0:y1, x0:x1] = out[y0 + d:y1 + d, x0:x1]
    f = q["folha"]
    fio = tuple(float(v) * q["fio"] for v in q["madeira"])
    it = {"tipo": "rv_vetor", "nome": "folha_banho2", "c": list(f),
          "prims": [{"t": "ret", "c": list(f), "cor": q["madeira"]},
                    {"t": "fio", "c": list(f), "cor": fio, "px": 0.5}]}
    out = pousar(out, it, None)
    reg["pecas"].append(it)
    print("    banho da suíte 2: as manchas entre a folha e a parede saíram; a folha redesenhada")
    return out


def faixa_parede(out, par, q=FAIXA_PAREDE):
    x0, y0, x1, y1 = q["px"]
    d = q["dy"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    fonte = out[y0 + d:y1 + d, x0:x1].astype(np.float32)
    Lr, Lf = reg.mean(axis=2), fonte.mean(axis=2)
    I = fonte.astype(np.int16)
    piso_f = (np.abs(I - np.int16(PAREDE)).max(axis=2) > 14) & ~par[y0 + d:y1 + d, x0:x1]
    m = (Lr < Lf - q["escuro"]) & piso_f & ~par[y0:y1, x0:x1]
    m = cv2.dilate(m.astype(np.uint8), np.ones((1, 3), np.uint8)) > 0
    m &= piso_f & ~par[y0:y1, x0:x1]
    reg[m] = fonte[m]
    out[y0:y1, x0:x1] = reg.astype(np.uint8)
    print(f"    paredes do louceiro, da despensa e da área de serviço: {int(m.sum())} px de sombra suja embaixo da "
          "parede viraram o piso")
    return out


def _copia_m(de, para, margem):
    """A matriz (destino -> origem) da cama girada 90° anti-horário (a cabeceira da esquerda vai para baixo)."""
    sx0, sy0, sx1, _ = de
    dx0, dy0, _, _ = para
    Wd = sx1 - sx0
    return np.array([[0, -1, sx0 + Wd + dy0], [1, 0, sy0 - dx0]], np.float64)


def cama_suite3(out, reg, q=CAMA_S3):
    de, para = q["de"], q["para"]
    X0, Y0, w, h = _caixa(para, 3)
    M = _copia_m(de, para, q["margem"])
    Mw = M.copy()
    Mw[:, 2] += M[:, 0] * X0 + M[:, 1] * Y0
    src = cv2.warpAffine(out, Mw, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                         borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    a = _ret(para, X0, Y0, w, h)
    a = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
    reg_ = out[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    for sb in BT.SOMBRAS["movel"]:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, sb["sig"] * PX_M))
        Ms = np.float32([[1, 0, sb["dx"] * PX_M], [0, 1, sb["dy"] * PX_M]])
        sh = cv2.warpAffine(sh, Ms, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)
        reg_ *= (1 - sb["forca"] * sh * (1 - a))[..., None]
    reg_ = reg_ * (1 - a[..., None]) + src * a[..., None]
    out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg_), 0, 255).astype(np.uint8)
    reg.setdefault("copias", []).append({"de": list(de), "para": list(para), "margem": q["margem"]})
    print("    suíte 3: a cama da suíte 1 (a mesma, 2,00 x 2,00 m), girada com a cabeceira embaixo, a sombra curta")
    return out


def copias_12k(out, base, s, X0, Ya3, reg_json):
    """As cópias (a cama da suíte 3) no 12K: da saída do Topaz (`base`), giradas, por cima."""
    if not reg_json.exists():
        return out
    for c in json.loads(reg_json.read_text()).get("copias", []):
        de, para = c["de"], c["para"]
        x0, y0, x1, y1 = para
        U0, V0 = int(np.floor((x0 - X0) * s)) - 4, int(np.floor((y0 - Ya3) * s)) - 4
        U1, V1 = int(np.ceil((x1 - X0) * s)) + 4, int(np.ceil((y1 - Ya3) * s)) + 4
        w, h = U1 - U0, V1 - V0
        M = _copia_m(de, para, c["margem"])
        # destino 12K (U, V) -> destino final (x, y) -> origem final -> origem 12K
        A = np.array([[1 / s, 0, U0 / s + X0], [0, 1 / s, V0 / s + Ya3], [0, 0, 1]], np.float64)
        B = np.array([[s, 0, -X0 * s], [0, s, -Ya3 * s], [0, 0, 1]], np.float64)
        Mf = np.vstack([M, [0, 0, 1]])
        T = (B @ Mf @ A)[:2]
        src = cv2.warpAffine(base, T, (w, h), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP,
                             borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        xs = (np.arange(w) + 0.5 + U0) / s + X0
        ys = (np.arange(h) + 0.5 + V0) / s + Ya3
        cx = np.clip(np.minimum(xs + 0.5 / s, x1) - np.maximum(xs - 0.5 / s, x0), 0, 1 / s) * s
        cy = np.clip(np.minimum(ys + 0.5 / s, y1) - np.maximum(ys - 0.5 / s, y0), 0, 1 / s) * s
        a = np.outer(cy, cx).astype(np.float32)
        r_ = out[V0:V1, U0:U1].astype(np.float32)
        out[V0:V1, U0:U1] = np.clip(np.round(r_ * (1 - a[..., None]) + src * a[..., None]), 0, 255).astype(np.uint8)
    return out


def quarto_servico(out, par, reg, q=QUARTO_SERV):
    # a moldura marrom em volta da cama: o anel de fora vira o piso (o de longe, sem o desenho fino, mais o grão dele)
    x0, y0, x1, y1 = q["cama"]
    e = q["anel_px"]
    X0, Y0, w, h = _caixa(q["cama"], e + 12)
    a = cv2.resize(_ret(q["cama"], X0, Y0, w, h), (w, h), interpolation=cv2.INTER_AREA)
    anel = (cv2.resize(_ret((x0 - e, y0 - e, x1 + e, y1 + e), X0, Y0, w, h), (w, h),
                       interpolation=cv2.INTER_AREA) > 0.01) & (a < 0.999)
    nx0, ny0, nx1, ny1 = q["nao"]
    sub_par = par[Y0:Y0 + h, X0:X0 + w].copy()
    yy, xx = np.mgrid[Y0:Y0 + h, X0:X0 + w]
    janela = (xx >= nx0) & (xx < nx1) & (yy >= ny0) & (yy < ny1)
    anel &= ~sub_par & ~janela
    reg_ = out[Y0:Y0 + h, X0:X0 + w].copy()
    I = reg_.astype(np.int16)
    parede = np.abs(I - np.int16(PAREDE)).max(axis=2) <= 14
    piso = ~anel & (a < 0.01) & ~sub_par & ~janela & ~parede
    # o anel vem só do piso de fora (a cama, as paredes, a janela e o armário claro também entram na máscara, para não
    # servirem de fonte), mais o grão de um trecho limpo do piso do quarto (`grao_px`)
    claro = I.mean(axis=2) > 150
    anel &= ~claro
    piso &= ~claro
    mask = (~piso).astype(np.uint8) * 255
    novo = cv2.inpaint(reg_, mask, 5, cv2.INPAINT_TELEA).astype(np.float32)
    gx0, gy0, gx1, gy1 = q["grao_px"]
    G = out[gy0:gy1, gx0:gx1].astype(np.float32)
    G = G - cv2.GaussianBlur(G, (0, 0), 2.5)
    G = np.concatenate([G, G[:, ::-1]], axis=1)
    G = np.concatenate([G, G[::-1]], axis=0)
    G = np.tile(G, (h // G.shape[0] + 1, w // G.shape[1] + 1, 1))[:h, :w]
    novo += G
    reg_[anel] = np.clip(novo[anel], 0, 255).astype(np.uint8)
    # a sombra curta da cama no piso
    r2 = reg_.astype(np.float32)
    for sb in BT.SOMBRAS["movel"]:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, sb["sig"] * PX_M))
        Ms = np.float32([[1, 0, sb["dx"] * PX_M], [0, 1, sb["dy"] * PX_M]])
        sh = cv2.warpAffine(sh, Ms, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)
        r2 *= (1 - sb["forca"] * sh * (1 - a) * ~sub_par)[..., None]
    out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(r2), 0, 255).astype(np.uint8)
    # a janela
    j = q["janela"]
    prims = [{"t": "ret", "c": list(j["vao"]), "cor": j["peitoril"]}]
    for m_ in j["marcos"]:
        prims += [{"t": "ret", "c": list(m_), "cor": j["marco"]},
                  {"t": "fio", "c": list(m_), "cor": PERFIL, "px": j["perfil_px"]}]
    for f, (g0, g1) in j["folhas"]:
        prims += [{"t": "ret", "c": list(f), "cor": PERFIL},
                  {"t": "ret", "c": [g0, f[1] + j["perfil_px"], g1, f[3] - j["perfil_px"]], "cor": j["vidro"]}]
    it = {"tipo": "rv_vetor", "nome": "janela_quarto_servico", "c": list(j["vao"]), "prims": prims}
    out = pousar(out, it, None)
    reg["pecas"].append(it)
    print("    quarto de serviço: a moldura marrom em volta da cama virou o piso (a sombra curta da cama); a janela de 2 "
          "folhas de correr redesenhada pelo PDF")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def refrigerador(out, par, reg, q=REFRIGERADOR):
    it = {"tipo": "png", "png": q["png"], "rot": q["rot"], "c": list(q["c"]), "sombra": "movel"}
    out = _RT["m"].pousar_peca(out, it, BT.SOMBRAS["movel"], par)
    reg["pecas"].append(it)
    print("    varanda gourmet: o refrigerador inox no vão junto ao BH gourmet, a frente para a varanda")
    return out


def portas_banho_master(RT, Q, out, par, reg, q=PORTAS_BM):
    # o vão: o piso do banho logo acima (os restos das folhas e o borrão entre elas saem)
    x0, y0, x1, y1 = [int(round(v)) for v in q["vao"]]
    d = q["vao_fonte_dy"]
    out[y0:y1 + 2, x0:x1] = out[y0 + d:y1 + 2 + d, x0:x1]
    # o piso da suíte por baixo do cinza que passava da face da parede
    px0, py0, px1, py1 = q["piso_px"]
    I = out[py0:py1, px0:px1].astype(np.int16)
    cinza = (np.abs(I - np.int16(PAREDE)).max(axis=2) <= 22) | ((I.max(axis=2) - I.min(axis=2)) < 12)
    bur = np.zeros(par.shape, bool)
    bur[py0:py1, px0:px1] = cinza
    if bur.any():
        out = BS_quieto(RT.piso_reguas, Q, out, bur, sigmas=(4, 8, 16, 32, 64))
    prims = [{"t": "ret", "c": list(r), "cor": PAREDE} for r in q["parede"]]
    for r in q["nichos"]:
        prims += [{"t": "ret", "c": list(r), "cor": q["nicho"]}, {"t": "fio", "c": list(r), "cor": (150, 150, 150),
                                                                   "px": 0.4}]
    for r in q["folhas"]:
        prims += [{"t": "ret", "c": list(r), "cor": q["folha"]},
                  {"t": "fio", "c": list(r), "cor": PERFIL, "px": q["perfil_px"]}]
    rs = np.float32(q["parede"] + q["folhas"])
    it = {"tipo": "rv_vetor", "nome": "portas_banho_master",
          "c": [float(rs[:, 0].min()), float(rs[:, 1].min()), float(rs[:, 2].max()), float(rs[:, 3].max())],
          "prims": prims}
    out = pousar(out, it, None)
    reg["pecas"].append(it)
    print("    banho master: a parede de baixo pelo PDF (os 2 bolsos, os nichos, os batentes), as 4 folhas das portas de "
          "correr telescópicas; o piso da suíte por baixo do cinza que passava da face")
    return out


def BS_quieto(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


def hall(out, par, reg, q=HALL):
    import paisagismo_terreo_casab_1311 as PJ
    x0, y0, x1, y1 = q["piso"]
    fx0, fy0, fx1, fy1 = q["piso_fonte"]
    I = out.astype(np.int16)
    trav = (I.mean(axis=2) > 165) & ((I.max(axis=2) - I.min(axis=2)) < 45)
    m = np.zeros(par.shape, bool)
    m[y0:y1, x0:x1] = True
    nao = ~trav & ~m                      # o que não é travertino em volta (a parede, a linha preta) não dá o tom
    m &= ~RT_dil(par, 1)
    out = PJ.preencher(out, m, out[fy0:fy1, fx0:fx1].copy(), anel_px=8, nao=nao)
    # as bordas do toco: o piso dos lados (o escuro e o degrau de 1 px que o render deixava)
    for (x0, y0, x1, y1), dx in q["toco_limpo"]:
        out[y0:y1, x0:x1] = out[y0:y1, x0 + dx:x1 + dx]
    # a soleira de parede a parede: nos dois vãos dos vidros fixos, a soleira (e o piso dos lados) da parte livre
    for (y0, y1), (x0, x1), modo, d in q["soleira"]:
        out[y0:y1, x0:x1] = (out[d:d + (y1 - y0), x0:x1] if modo == "v" else out[y0:y1, d:d + 1] if modo == "r"
                             else out[y0:y1, x0 + d:x1 + d])
    from final3840_casab import BOXES_VIDRO as BV
    prims = [{"t": "ret", "c": list(r), "cor": PAREDE} for r in q["parede"] + [q["parede_baixo"]]]
    for v in q["vidros"]:
        prims += [{"t": "ret", "c": list(v), "cor": BV["vidro"]},
                  {"t": "fio", "c": list(v), "cor": BV["face"], "px": BV["face_px"]}]
    it = {"tipo": "rv_vetor", "nome": "hall_parede", "c": [2410.0, 938.0, 2539.1, 1185.0], "prims": prims}
    out = pousar(out, it, None)
    reg["pecas"].append(it)
    print("    hall: a face da parede reta pelo PDF e o toco reto; a soleira da porta principal de parede a parede, com os "
          "2 vidros fixos por cima (vidro claro); o piso do hall interno no retângulo claro, sem a linha sob o vaso")
    return out


def RT_dil(m, r):
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)) > 0


def aplicar(RT, Q, out, par, reg):
    _RT["m"] = RT
    out = refrigerador(out, par, reg)
    out = deck(out, par, reg)
    out = piscina(out)
    out = bancada_lavatorio(out, par, reg)
    out = batentes(Q, out, par, reg)
    out = correr_cozinha(out, reg)
    out = folha_banho2(out, reg)
    out = faixa_parede(out, par)
    out = portas_banho_master(RT, Q, out, par, reg)
    out = hall(out, par, reg)
    out = cama_suite3(out, reg)
    out = quarto_servico(out, par, reg)
    return out


def antes_depois(commit):
    import regras_terreo_casab_1311 as RT
    raiz = RT.RAIZ_GIT
    E = RT.CASA_B / "entrega"

    def de_git(rel):
        dado = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=raiz, capture_output=True, check=True).stdout
        return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    fa = de_git(RT.FINAL.relative_to(raiz).as_posix())
    fd = cv2.imread(str(RT.FINAL))
    ka = de_git((E / "POE642_CasaB_PH_Terreo_12K_opcao_A.jpg").relative_to(raiz).as_posix())
    kd = cv2.imread(str(E / "POE642_CasaB_PH_Terreo_12K_opcao_A.jpg"))
    # o 12K na final: o casamento do miolo (a mesma conta do conf12k)
    s = ka.shape[1] / 3426.0
    peq = cv2.resize(kd, None, fx=1 / s, fy=1 / s, interpolation=cv2.INTER_AREA)
    hh, ww = peq.shape[:2]
    pt = peq[hh // 3:hh // 3 + 300, ww // 3:ww // 3 + 400]
    r = cv2.matchTemplate(fd, pt, cv2.TM_CCOEFF_NORMED)
    _, _, _, loc = cv2.minMaxLoc(r)
    X0, Y0 = loc[0] - ww // 3, loc[1] - hh // 3
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        U0, V0, U1, V1 = int((x0 - X0) * s), int((y0 - Y0) * s), int((x1 - X0) * s), int((y1 - Y0) * s)
        a, b = ka[V0:V1, U0:U1], kd[V0:V1, U0:U1]
        k = min(1.0, 1500 / max(a.shape[1], 1), 900 / max(a.shape[0], 1))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        lado = a.shape[1] <= a.shape[0] * 1.6
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b]) if lado else \
            np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "12K ANTES | DEPOIS" if lado else "12K ANTES (em cima) | DEPOIS (embaixo)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = RT.R / f"POE642_CasaB_PH_Terreo_1311_revisao12k_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois (12K A, contra {commit}): {', '.join(ANTES_DEPOIS)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes-depois", required=True)
    antes_depois(ap.parse_args().antes_depois)


if __name__ == "__main__":
    main()

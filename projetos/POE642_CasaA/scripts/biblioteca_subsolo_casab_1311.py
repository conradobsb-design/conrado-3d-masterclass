"""As peças da biblioteca no Subsolo da Casa B (13/11).

Usuário: "VAMOS REVISAR OS MOBILIÁRIOS DO SUBSOLO DA CASA B"; a proposta
(`POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_1311_proposta_biblioteca_{1,2}.jpg`) aprovada com "OK, PODE APLICAR AS
RECOMENDADAS". As recomendadas são as escolhas aprovadas no Subsolo da Casa A (`biblioteca_subsolo_casaa_1211.py`, de
onde vêm as funções) e os chuveiros desenhados em planta do 1º Pavimento da Casa A (`chuveiros_planta_casaa_1211.py`):
- **Sauna:** o banco reto de travertino da biblioteca nos dois bancos do PDF (`final3840_casab.SAUNA_F`: o da frente e o
  de trás, com o espelho entre eles, que fica), cada um no tom do banco de antes (as pontas na escala da altura, o meio
  esticado); a sombra de contato e o pé ficam.
- **BH sauna:** a cuba esculpida da biblioteca esculpida no granito da bancada (`biblioteca_subsolo_casaa_1211.
  cuba_esculpida`, como nos BH. FEM./MASC. da Casa A: o sombreado da peça, as bordas chanfradas e a sombra por dentro,
  sobre o granito de referência, no tom do granito da bancada, e a torneira cromada dela), no retângulo da cuba do PDF
  com a faixa até a parede (a parede à direita: a peça girada); a bacia Carrara branca no retângulo do vaso do PDF (a
  caixa na parede da direita), o piso de antes refeito por baixo do vaso marrom (o travertino logo à esquerda, com a
  costura).
- **BH serviço:** a bancada no polígono do PDF com o granito da cuba de serviço da biblioteca e a cuba branca com a
  torneira dela (`biblioteca_subsolo_casaa_1211.servico`, o BH. SERV. da Casa A; a parede à esquerda); a bacia Monte
  Carlo (sem válvula) no retângulo do vaso do PDF (a caixa na parede da esquerda).
- **Chuveiros:** os desenhos em planta (`-planta`): o quadrado de parede na ducha do deck (`ajustes_casab.
  CHUVEIRO_DUCHA`, o braço para a parede de baixo) e no chuveiro ao lado da sauna (o braço para a parede da esquerda);
  o redondo de parede no chuveiro ao lado do BH serviço (o braço para a parede da direita); a placa no quadrado do PDF,
  o braço até a parede; os de antes saem (o piso do lado, com a costura); a sombra `chuveiro`.
- **Academia:** na proposta, sem troca; depois (usuário: "E O SUPINO? QUERO QUE TROQUE, MANTENDO A BOLA") as 2
  esteiras (`esteira-a`), as 2 bicicletas (`bicicleta-b`) e o supino (`banco-supino`) da biblioteca, no tamanho da Casa
  A (esteiras 1,76 x 0,77 m, bicicletas 1,23 x 0,51 m, supino 1,60 x 2,04 m, com a barra alongada como lá), cada um com
  o meio no meio do símbolo do PDF da Casa B, o console para a esquerda e o supino espelhado (a barra à direita do
  banco, como no PDF); a sombra curta da Casa A. Os aparelhos de antes saem com a sombra: o vinílico volta com as
  mesmas réguas (`reguas_academia`) vezes a luz do piso em volta. A bola e o armário ficam.
No 12K (`ampliacao_12k_subsolo_casab.montar12k`, `pecas_12k`): o que mudou na final (`REG_MASC`) vem da final ampliada
sobre a saída do Topaz e, por cima, as peças de PNG (bancos, bacias, chuveiros e aparelhos) nítidas na escala do 12K.

  python3 biblioteca_subsolo_casab_1311.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final, o registro do 12K e os antes e
depois `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_1311_<trecho>_antes_depois.jpg`.
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
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402

CASA_B = AQUI.parents[1] / "POE642_CasaB"
R = CASA_B / "renders"
FINAL = R / "POE642_CasaB_PH_Subsolo_final_rotulos.png"
REG_JSON = R / "POE642_CasaB_PH_Subsolo_12K_biblioteca.json"
REG_MASC = R / "POE642_CasaB_PH_Subsolo_12K_biblioteca_zona.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "df9a29e"
PX_M = B1.PX_M

# a sauna: os dois bancos (pt), o da frente e o de trás, entre eles o espelho (fica)
SAUNA = {"png": "sauna/banco-reto-travertino.png", "pontas": 60, "erosao_px": 3}
# o BH sauna: a cuba (pt: a cuba do PDF e a faixa da bancada até a parede, com a torneira), o miolo da bacia da cuba
# (pt) e a semente do granito; a bancada de granito em volta (pt), para o tom
BHS = {"cuba_pt": (1139.7, 817.4, 1168.7, 862.7), "bacia_pt": (1142.2, 820.4, 1161.3, 859.7),
       "bancada_pt": [(1150.0, 802.1, 1169.9, 816.3), (1153.5, 863.8, 1169.9, 895.2)], "semente": 1311,
       "croma_cromo": 20, "lum_cromo": 110,
       # a cuba branca de antes passava do retângulo do PDF (1 a 3 px): antes da nova, a sobra vai ao piso (o
       # travertino logo à esquerda) e, junto à parede, ao granito da bancada logo acima e logo abaixo (px)
       "sobra_piso_px": (1322, 618, 1338.3, 676), "sobra_bancada_px": [((1338.3, 618.4, 1359.2, 622.4), -1),
                                                                        ((1338.3, 670.0, 1359.2, 674.6), 1)]}
# as bacias: o retângulo do vaso do PDF (pt), o giro do PNG (a caixa em cima no PNG) e o piso por baixo
BACIAS = [
    {"nome": "BH sauna", "png": "banho-feminino-academia/bacia-carrara.png", "pt": (1140.8, 914.0, 1169.9, 934.0),
     "giro": "cw", "piso": ("desloc", -1, 0)},       # a caixa na parede da direita; o travertino logo à esquerda
    {"nome": "BH serviço", "png": "banho-de-servico/bacia-monte-carlo-sem-valvula.png",
     "pt": (1178.4, 610.0, 1209.5, 631.4), "giro": "ccw", "piso": ("inpaint",)},   # a caixa na parede da esquerda
]
# o BH serviço (para `biblioteca_subsolo_casaa_1211.servico`): a bancada (o polígono do PDF) e a cuba (pt)
SERVICO = {"cuba": (1182.3, 556.4, 1204.9, 579.0), "bancada": (1178.4, 538.5, 1201.4, 598.3)}
# os chuveiros (pt): a placa do PDF, a face da parede onde o braço chega e o lado; o desenho em planta; o trecho de
# antes (pt, a placa, o braço e a canopla) e de onde vem o piso que o cobre (o deslocamento em px)
CHUVEIROS = [
    # (13/11, "CORRIJA O PISO AO INCLUIR NOVO CHUVEIRO") na ducha do deck, o chuveiro de antes não é mais desenhado
    # (`pedidos_subsolo_casab_1211.DECK_SB["chuveiro"]`): o deck por baixo é o do gerador, sem remendo (`antes_pt` None)
    {"nome": "ducha do deck", "png": "banho-1/chuveiro-quadrado-parede-planta",
     "placa_pt": (747.5, 930.4, 758.7, 941.6), "parede": (958.2, "baixo"), "antes_pt": None},
    {"nome": "chuveiro ao lado da sauna", "png": "banho-1/chuveiro-quadrado-parede-planta",
     "placa_pt": (990.5, 918.7, 1001.7, 929.9), "parede": (974.3, "esq"),
     "antes_pt": (974.9, 918.7, 1001.7, 929.9), "piso_dx": 0, "piso_dy": -1},
    {"nome": "chuveiro ao lado do BH serviço", "png": "banho-de-servico/chuveiro-redondo-parede-planta",
     "placa_pt": (1287.0, 615.1, 1298.2, 626.3), "parede": (1314.4, "dir"),
     "antes_pt": (1287.0, 615.1, 1313.8, 626.3), "piso_dx": -1, "piso_dy": 0},
]
LIMPA_PX = 2
# a academia (13/11, "E O SUPINO? QUERO QUE TROQUE, MANTENDO A BOLA"): as 2 esteiras, as 2 bicicletas e o supino da
# biblioteca no tamanho da Casa A (`biblioteca_subsolo_casaa_1211.ACADEMIA`, de onde vêm a escala, o banco de 1,60 m e
# a barra do supino: esteiras 1,76 x 0,77 m, bicicletas 1,23 x 0,51 m, supino 1,60 x 2,04 m), cada um com o meio no
# meio do símbolo do PDF da Casa B (`pdf_px`: a caixa dos traços da ARQ_LAYOUT HUMANIZAÇÃO, px do quadro; os símbolos
# têm o tamanho dos da Casa A), o console para a esquerda (o giro da Casa A); o supino espelhado (a barra à direita do
# banco, como no PDF da Casa B). Os aparelhos de antes (os da final da Casa A de 744adec, colados pelos pedidos:
# `pedidos_subsolo_casab_1211.ACADEMIA_SB`) saem com a sombra (`folga_px` em volta): o vinílico volta com as mesmas
# réguas (as do `vinilico_foto.trocar` da academia, a mesma semente) vezes a luz do piso em volta (a média normalizada,
# cada vez mais larga: `luz_sigmas`). A bola (um disco de `bola_px` em volta dela fica intocado) e o armário ficam.
ACADEMIA = {
    "pecas": [
        {"nome": "esteira de cima", "png": "academia/esteira-a.png", "pdf_px": (1534.7, 455.0, 1630.2, 496.8)},
        {"nome": "esteira de baixo", "png": "academia/esteira-a.png", "pdf_px": (1535.3, 512.7, 1630.8, 554.5)},
        {"nome": "bicicleta de cima", "png": "academia/bicicleta-b.png", "pdf_px": (1422.4, 464.8, 1473.2, 485.7)},
        {"nome": "bicicleta de baixo", "png": "academia/bicicleta-b.png", "pdf_px": (1422.4, 532.4, 1473.2, 553.3)},
        {"nome": "supino", "png": "academia/banco-supino.png", "pdf_px": (1434.5, 604.2, 1515.1, 706.9),
         "espelho": True},
    ],
    "folga_px": 6, "bola_px": 28, "desvio": 18, "luz_sigmas": (4.0, 8.0, 16.0, 32.0), "fechar_px": 3,
    # as réguas pegas têm de ser as do piso: a alta frequência da razão (final / réguas) no piso, no máximo
    "razao_max": 0.005,
}
ANTES_DEPOIS = {"sauna": (950, 690, 1150, 775), "bh_sauna": (1295, 598, 1368, 752), "ducha_deck": (860, 690, 965, 775),
                "chuveiro_sauna": (1140, 712, 1200, 758), "bh_servico": (1358, 322, 1410, 432),
                "chuveiro_bh_servico": (1438, 398, 1522, 432), "academia": (1395, 440, 1700, 780)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            _Q["Q"] = F.Quadro("Subsolo")
    return _Q["Q"]


_Q = {}


def px(Q, r):
    return BS.caixa_px(Q, r)


def piso_desloc(out, c, par, dx, dy, folga=1):
    """O retângulo c (px) recebe o piso de `dx` x a largura (ou `dy` x a altura) ao lado, com a costura das bordas."""
    x0, y0 = int(np.floor(c[0])) - folga, int(np.floor(c[1])) - folga
    x1, y1 = int(np.ceil(c[2])) + folga, int(np.ceil(c[3])) + folga
    w, h = x1 - x0, y1 - y0
    ox, oy = dx * (w + 2), dy * (h + 2)
    novo = np.ascontiguousarray(out[y0 + oy:y1 + oy, x0 + ox:x1 + ox])
    # o que não é piso no trecho copiado (uma letra de rótulo, um metal) sai, refeito pelo piso em volta
    med = np.median(novo.reshape(-1, 3).astype(np.int16), axis=0)
    fora = np.abs(novo.astype(np.int16) - med).max(axis=2) > 24
    if fora.any():
        fora = cv2.dilate(fora.astype(np.uint8), np.ones((3, 3), np.uint8))
        novo = cv2.inpaint(novo, fora, 3, cv2.INPAINT_TELEA)
    novo = BS.costura(out, novo, x0, y0, x1, y1, par)
    caixa = ~par[y0:y1, x0:x1]
    out[y0:y1, x0:x1][caixa] = novo[caixa]
    return out


def piso_inpaint(out, c, par, folga=1):
    x0, y0 = int(np.floor(c[0])) - folga, int(np.floor(c[1])) - folga
    x1, y1 = int(np.ceil(c[2])) + folga, int(np.ceil(c[3])) + folga
    m = np.zeros(out.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = 1
    m[par] = 0
    X0, Y0, X1, Y1 = x0 - 12, y0 - 12, x1 + 12, y1 + 12
    sub = cv2.inpaint(np.ascontiguousarray(out[Y0:Y1, X0:X1]), m[Y0:Y1, X0:X1] * 255, 5, cv2.INPAINT_TELEA)
    out[Y0:Y1, X0:X1][m[Y0:Y1, X0:X1] > 0] = sub[m[Y0:Y1, X0:X1] > 0]
    return out


def banco(out, c, antes, q=SAUNA):
    """O banco reto de travertino no retângulo c (px), no tom do banco de antes (o miolo)."""
    e = q["erosao_px"]
    x0, y0, x1, y1 = (int(np.ceil(c[0])) + e, int(np.ceil(c[1])) + e, int(np.floor(c[2])) - e, int(np.floor(c[3])) - e)
    tom = np.median(antes[y0:y1, x0:x1].reshape(-1, 3), axis=0)
    return _banco_12k(c, tom, q)


def cuba_bhs(Q, out, q=BHS):
    """A cuba esculpida no granito, com a parede à direita: feita na janela girada (a parede embaixo, como nos banhos
    da Casa A) e girada de volta; depois, no tom do granito da bancada em volta (fora a torneira cromada)."""
    c = px(Q, q["cuba_pt"])
    b = px(Q, q["bacia_pt"])
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    out = piso_desloc(out, q["sobra_piso_px"], par, -1, 0, folga=0)
    for r, dy in q["sobra_bancada_px"]:
        out = piso_desloc(out, r, par, 0, dy, folga=0)
    X0, Y0, X1, Y1 = int(np.floor(c[0])) - 8, int(np.floor(c[1])) - 8, int(np.ceil(c[2])) + 8, int(np.ceil(c[3])) + 8
    reg = np.ascontiguousarray(out[Y0:Y1, X0:X1])
    h = Y1 - Y0
    rot = np.ascontiguousarray(cv2.rotate(reg, cv2.ROTATE_90_CLOCKWISE))      # a parede da direita vai para baixo

    def r2(r):                               # (x0, y0, x1, y1) da janela -> a janela girada (x' = h - y, y' = x)
        return (h - (r[3] - Y0), r[0] - X0, h - (r[1] - Y0), r[2] - X0)
    Qr = types.SimpleNamespace(p2q=lambda x, y: (x, y), px_m=Q.px_m)
    rot = BS.cuba_esculpida(Qr, rot, {"cuba": r2(c), "bacia": r2(b)}, q["semente"])
    novo = cv2.rotate(rot, cv2.ROTATE_90_COUNTERCLOCKWISE).astype(np.float32)
    # o tom do granito da bancada de antes (as partes da bancada fora da cuba)
    ref = []
    for r in q["bancada_pt"]:
        a, b_, cc, d = [int(round(t)) for t in px(Q, r)]
        ref.append(out[b_ + 2:d - 2, a + 2:cc - 2].reshape(-1, 3))
    ref = np.median(np.concatenate(ref).astype(np.float32), axis=0)
    xa, ya, xb, yb = [int(round(t)) for t in c]
    jan = novo[ya - Y0:yb - Y0, xa - X0:xb - X0]
    croma = jan.max(axis=2) - jan.min(axis=2)
    cromo = (croma < q["croma_cromo"]) & (jan.mean(axis=2) > q["lum_cromo"])
    gran = ~cromo
    k = ref / np.maximum(np.median(jan[gran], axis=0), 1)
    jan[gran] = np.clip(jan[gran] * k, 0, 255)
    novo[ya - Y0:yb - Y0, xa - X0:xb - X0] = jan
    out[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    print(f"    BH sauna: cuba esculpida da biblioteca no granito da bancada (BGR {np.round(ref).astype(int)}), "
          "a torneira cromada dela, girada para a parede da direita")
    return out


def chuveiro_pos(nome, placa_c, parede, placa_px):
    """O chuveiro de parede desenhado (`chuveiros_planta_casaa_1211`): o braço até a parede, que pode estar em cima,
    embaixo, à esquerda ou à direita (P, cx, cy, larg, alt, giro); o PNG de pé, o braço em cima."""
    P = B1.ler_png(nome)
    a = P[..., 3] > 128
    larg_linha = a.sum(axis=1)
    lmax = larg_linha.max()
    y_placa = int(np.argmax(larg_linha > 0.6 * lmax))
    tubo = larg_linha[:y_placa][larg_linha[:y_placa] > 0].min()
    while y_placa > 0 and tubo * 1.2 < larg_linha[y_placa - 1] <= larg_linha[y_placa]:
        y_placa -= 1
    s = placa_px / lmax
    dist, lado = parede
    centro = placa_c[0] if lado in ("esq", "dir") else placa_c[1]
    alcance = abs(dist - centro) - placa_px / 2
    braco = max(1.0, alcance / s)
    can, corpo = P[:y_placa], P[y_placa:]
    can = cv2.resize(can, (can.shape[1], max(2, int(round(braco)))),
                     interpolation=cv2.INTER_AREA if braco < can.shape[0] else cv2.INTER_CUBIC)
    P2 = np.ascontiguousarray(np.concatenate([can, corpo], axis=0))
    wt, ht = P2.shape[1] * s, P2.shape[0] * s
    desloc = ht / 2 - corpo.shape[0] * s / 2
    cx, cy = placa_c
    if lado == "cima":
        return P2, cx, cy - desloc, wt, ht, 0.0
    if lado == "baixo":
        return P2, cx, cy + desloc, wt, ht, 180.0
    if lado == "dir":
        return P2, cx + desloc, cy, wt, ht, -90.0
    return P2, cx - desloc, cy, wt, ht, 90.0


def peca_bacia(v):
    return BS.girar(BS.ler_png(v["png"]), v["giro"])


def aparelho(p):
    """O aparelho da biblioteca (BGRA) e a caixa dele (px), como na Casa A (`biblioteca_subsolo_casaa_1211.academia`:
    a barra do supino alongada até a do PDF repetindo as colunas da barra e do travessão do rack, o giro com o console
    para a esquerda, a caixa do PDF ampliada em volta do meio), no símbolo do PDF da Casa B; o supino espelhado."""
    a = next(x for x in BS.ACADEMIA["pecas"] if x["png"] == p["png"])
    c = p["pdf_px"]
    P = BS.ler_png(p["png"], cortar=False)
    if "barra" in a:
        a0, a1 = a["barra"]
        ys, xs = np.nonzero(P[..., 3] > 0)
        larg, alt = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        d = max(0, int(round(((c[3] - c[1]) / (c[2] - c[0]) * alt - larg) / 2)))

        def col(x):
            return np.repeat(P[:, x:x + 1], d, axis=1)
        P = np.concatenate([P[:, :a0], col(a0), P[:, a0:a1], col(a1), P[:, a1:]], axis=1)
    ys, xs = np.nonzero(P[..., 3] > 0)
    P = BS.girar(np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1]), BS.ACADEMIA["giro"])
    if p.get("espelho"):
        P = np.ascontiguousarray(P[:, ::-1])
    x0, y0, x1, y1 = c
    e = a["escala"] if "escala" in a else a["largura_m"] * PX_M / (x1 - x0)
    cx, cy, mw, mh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * e / 2, (y1 - y0) * e / 2
    return P, (cx - mw, cy - mh, cx + mw, cy + mh)


def reguas_academia(Q, antes):
    """As réguas do vinílico da academia (BGR float32) e o canto (x, y) delas no quadro: as do `vinilico_foto.trocar`
    dos pedidos (a mesma conta, só para pegar as réguas; a imagem que ele devolve não é usada)."""
    import pedidos_subsolo_casab_1211 as PS
    import um_pav_casaa_1111 as U
    import vinilico_foto as V
    H, W = antes.shape[:2]
    m = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in PS.ACADEMIA_SB["limpar_px"]:
        m[y0:y1, x0:x1] = True
    pegas = []
    orig = U._reguas_amostra

    def espiao(h, w, px_m, qv, rng):
        T = orig(h, w, px_m, qv, rng)
        f = sys._getframe(1).f_locals
        pegas.append((T if f["deitado"] else np.ascontiguousarray(T.transpose(1, 0, 2)), f["x"], f["y"]))
        return T
    U._reguas_amostra = espiao
    try:
        BS.quieto(V.trocar, Q, antes, [(124, 162, 200)], apagar=m, incluir=m)
    finally:
        U._reguas_amostra = orig
    cx, cy = np.mean([[(p["pdf_px"][0] + p["pdf_px"][2]) / 2, (p["pdf_px"][1] + p["pdf_px"][3]) / 2]
                      for p in ACADEMIA["pecas"]], axis=0)
    for T, x, y in pegas:
        if x <= cx < x + T.shape[1] and y <= cy < y + T.shape[0]:
            return T, x, y
    raise RuntimeError("as réguas da academia não foram achadas")


def academia(Q, out, antes, par, q=ACADEMIA):
    """Os aparelhos de antes saem (o vinílico de volta) e os da biblioteca entram, com a sombra curta da Casa A."""
    import pedidos_subsolo_casab_1211 as PS
    import vinilico_foto as V
    H, W = out.shape[:2]
    T, ox, oy = reguas_academia(Q, antes)
    h, w = T.shape[:2]
    reg = out[oy:oy + h, ox:ox + w].astype(np.float32)
    Lr = reg / np.maximum(T, 1)
    # a. o buraco: os aparelhos de antes (o alfa deles, como os pedidos colaram) e a sombra, dentro da academia
    A = PS._final_a(PS.ACADEMIA_SB)
    velho = np.zeros((H, W), bool)
    for (ax0, ay0, ax1, ay1), (cx, cy), esp in PS.ACADEMIA_SB["pecas"]:
        al = PS._alfa_aparelho(A[ay0:ay1, ax0:ax1])
        if esp:
            al = al[:, ::-1]
        hh, ww = al.shape
        X0, Y0 = int(round(cx - ww / 2)), int(round(cy - hh / 2))
        velho[Y0:Y0 + hh, X0:X0 + ww] |= al > 0.02
    k = 2 * q["folga_px"] + 1
    buraco = cv2.dilate(velho.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    # a sala: o vinílico da base com os buracos dos símbolos do PDF fechados (os pedais das bicicletas são cheios no PDF)
    f = 2 * q["fechar_px"] + 1
    sala = ndimage.binary_fill_holes(cv2.morphologyEx(V.mascara_vinilico(Q, [(124, 162, 200)]).astype(np.uint8),
                                                      cv2.MORPH_CLOSE, np.ones((f, f), np.uint8)) > 0)
    bx, by = PS.ACADEMIA_SB["bola"]["centro_px"]
    yy, xx = np.ogrid[0:H, 0:W]
    bola = np.hypot(xx - bx, yy - by) <= q["bola_px"]
    buraco &= sala & ~par & ~bola
    assert not buraco[:oy].any() and not buraco[oy + h:].any() and not buraco[:, :ox].any() and \
        not buraco[:, ox + w:].any(), "o buraco passa das réguas"
    b = buraco[oy:oy + h, ox:ox + w]
    # b. o piso que vale para a luz: na sala, fora do buraco, no tom das réguas vezes a luz larga (sem rótulo, bola,
    # armário e batentes)
    s_ = (sala & ~par)[oy:oy + h, ox:ox + w]
    num, den = BS.nconv(Lr, s_ & ~b, 12.0)
    E = T * num / np.maximum(den, 1e-4)
    valido = s_ & ~b & (np.abs(reg - E).max(axis=2) <= q["desvio"])
    g = Lr.mean(axis=2)
    alta = float(np.median(np.abs(g - cv2.GaussianBlur(g, (0, 0), 2.0))[valido]))
    if alta > q["razao_max"]:
        raise RuntimeError(f"as réguas pegas não são as do piso (alta frequência da razão {alta:.4f})")
    # c. o vinílico de volta no buraco: as réguas vezes a luz do piso em volta (média normalizada, cada vez mais larga)
    L = np.zeros_like(Lr)
    falta = b.copy()
    for sig in q["luz_sigmas"]:
        num, den = BS.nconv(Lr, valido, sig)
        ok = falta & (den[..., 0] > 0.05)
        L[ok] = (num / np.maximum(den, 1e-6))[ok]
        falta &= ~ok
        if not falta.any():
            break
    reg[b] = (T * L)[b]
    out[oy:oy + h, ox:ox + w] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    academia: os aparelhos de antes saem; o vinílico de volta em {int(b.sum())} px (as réguas da academia, "
          f"alta frequência da razão no piso {alta:.4f}, vezes a luz do piso em volta)")
    # d. os aparelhos da biblioteca
    pecas = []
    for p in q["pecas"]:
        P, cc = aparelho(p)
        out = BS.compor(out, P, cc, sombra=BS.ACADEMIA["sombra"], nao=par)
        pecas.append({"tipo": "aparelho", "png": p["png"], "pdf_px": list(p["pdf_px"]),
                      "espelho": bool(p.get("espelho")), "c": list(cc)})
        print(f"    academia: {p['nome']} ({Path(p['png']).stem}{', espelhado' if p.get('espelho') else ''}) em "
              f"{cc[2] - cc[0]:.1f} x {cc[3] - cc[1]:.1f} px ({(cc[2] - cc[0]) / PX_M:.2f} x "
              f"{(cc[3] - cc[1]) / PX_M:.2f} m), o meio em ({(cc[0] + cc[2]) / 2:.1f}, {(cc[1] + cc[3]) / 2:.1f})")
    return out, pecas


def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    reg = {"pecas": []}
    # 1. a sauna: os dois bancos
    b = F.SAUNA_F["Subsolo"]
    x0p, y0p, x1p, y1p = b["pt"]
    e0, e1 = b["espelho_pt"]
    for nome, r in (("frente", (x0p, y0p, x1p, e0)), ("trás", (x0p, e1, x1p, y1p))):
        c = px(Q, r)
        P, tom = banco(out, c, antes)
        out = BS.compor(out, P, c, nao=par)
        reg["pecas"].append({"tipo": "banco", "c": list(c), "tom": [float(t) for t in tom]})
        print(f"    sauna: banco reto de travertino da biblioteca (o de {nome}), no tom do de antes "
              f"(BGR {np.round(tom).astype(int)})")
    # 2. o BH sauna: a cuba esculpida no granito
    out = cuba_bhs(Q, out)
    # 3. o BH serviço: bancada e cuba (a função do BH. SERV. da Casa A, com os retângulos da Casa B)
    FAb = types.SimpleNamespace(**{k: getattr(FA, k) for k in ("_dentro", "bancada_pedra", "paredes_pdf")},
                                BANHOS={"servico": SERVICO})
    out = BS.servico(Q, out, FAb)
    # 4. as bacias: o piso por baixo da antiga e a nova no retângulo do vaso do PDF
    for v in BACIAS:
        c = px(Q, v["pt"])
        if v["piso"][0] == "desloc":
            out = piso_desloc(out, c, par, v["piso"][1], v["piso"][2])
        else:
            out = piso_inpaint(out, c, par)
        out = BS.compor(out, peca_bacia(v), c, nao=par)
        reg["pecas"].append({"tipo": "bacia", "png": v["png"], "giro": v["giro"], "c": list(c)})
        print(f"    {v['nome']}: {Path(v['png']).stem} branca no retângulo do vaso do PDF")
    # 5. os chuveiros: os de antes viram piso, os desenhados entram
    for ch in CHUVEIROS:
        if ch["antes_pt"] is not None:
            a = px(Q, ch["antes_pt"])
            a = (a[0] - LIMPA_PX, a[1] - LIMPA_PX, a[2] + LIMPA_PX, a[3] + LIMPA_PX)
            out = piso_desloc(out, a, par, ch["piso_dx"], ch["piso_dy"], folga=0)
        pl = px(Q, ch["placa_pt"])
        pc = ((pl[0] + pl[2]) / 2, (pl[1] + pl[3]) / 2)
        lado = ch["parede"][1]
        u, v_ = Q.p2q(ch["parede"][0], ch["parede"][0])
        dist = u if lado in ("esq", "dir") else v_
        placa = ((pl[2] - pl[0]) + (pl[3] - pl[1])) / 2
        P, cx, cy, wt, ht, ang = chuveiro_pos(ch["png"], pc, (dist, lado), placa)
        o = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, ang, B1.SOMBRAS["chuveiro"], PX_M, nao=par)
        out = np.clip(np.round(o), 0, 255).astype(np.uint8)
        reg["pecas"].append({"tipo": "chuveiro", "png": ch["png"], "placa_c": list(pc), "parede": [dist, lado],
                             "placa_px": placa})
        print(f"    {ch['nome']}: {Path(ch['png']).stem}, o braço até a parede ({lado})")
    # 6. a academia: os aparelhos da biblioteca no tamanho da Casa A (a bola fica)
    out, pecas = academia(Q, out, antes, par)
    reg["pecas"] += pecas
    # 7. (14/11, "COMPLETE O CONTORNO PRETO ATÉ A PAREDE DEBAIXO. FALTOU UM PEQUENO TRECHO DA ÚLTIMA RIPA DE MADEIRA") o
    # contorno da borda esquerda do deck da ducha (o cinza das paredes, 3 px) desce até a parede de baixo
    out = contorno_ducha(out)
    return out, reg, par


# o contorno da borda esquerda do deck da ducha: as colunas (px) e de onde até onde (a parede de baixo inclusa)
CONTORNO_DUCHA = {"x": (759, 762), "y": (765, 777), "canto_x": 762, "canto_y": (770, 777), "cor": (80, 80, 80)}


def contorno_ducha(out, q=CONTORNO_DUCHA):
    x0, x1 = q["x"]
    y0, y1 = q["y"]
    out[y0:y1, x0:x1] = np.uint8(q["cor"])
    c0, c1 = q["canto_y"]
    out[c0:c1, q["canto_x"]] = np.uint8(q["cor"])
    print(f"    ducha: o contorno da borda esquerda do deck até a parede de baixo (y {y0} a {y1})")
    return out


def salvar_registro(antes, depois, reg, par):
    zona = cv2.dilate((np.abs(antes.astype(np.int16) - depois.astype(np.int16)).max(axis=2) > 2).astype(np.uint8),
                      np.ones((5, 5), np.uint8)).astype(bool)
    m = np.zeros(antes.shape, np.uint8)
    m[..., 0] = zona * 255
    m[..., 1] = par * 255
    cv2.imwrite(str(REG_MASC), m)
    REG_JSON.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n")
    print(f"    {REG_JSON.name}: {len(reg['pecas'])} peças; zona {int(zona.sum())} px")


def pecas_12k(final, out, s, X0, Ya3, reg_json=None, reg_masc=None, peca=None):
    """No 12K do Subsolo da Casa B (`ampliacao_12k_subsolo_casab.montar12k`, antes dos rótulos): o que mudou na final
    vem da final ampliada; por cima, as peças de PNG nítidas na escala do 12K. Também para o Térreo
    (`regras_terreo_casab_1311`): o registro e a zona dele (`reg_json`, `reg_masc`) e `peca(it)`, que desenha os tipos
    novos ((P, cx, cy, larg, alt, giro, sombras) ou None para os daqui)."""
    reg_json, reg_masc = reg_json or REG_JSON, reg_masc or REG_MASC
    if not reg_json.exists():
        return out
    reg = json.loads(reg_json.read_text())
    mk = cv2.imread(str(reg_masc))
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
        r_ = out[V0:V1, U0:U1].astype(np.float32)
        out[V0:V1, U0:U1] = np.clip(np.round(r_ * (1 - al) + src * al), 0, 255).astype(np.uint8)

    def nao_fn(xa, ya, xb, yb):
        fy = np.clip(np.floor(np.arange(ya, yb) / s + Ya3).astype(int), 0, nao.shape[0] - 1)
        fx = np.clip(np.floor(np.arange(xa, xb) / s + X0).astype(int), 0, nao.shape[1] - 1)
        return nao[fy[:, None], fx[None, :]]
    for it in reg["pecas"]:
        r = peca(it) if peca is not None else None
        if r is not None:
            P, cx, cy, wt, ht, ang, sb = r
            out = BT.pousar(out, P, (cx - X0) * s, (cy - Ya3) * s, wt * s, ht * s, ang, sb, PX_M * s, nao=nao_fn)
            continue
        if it["tipo"] == "chuveiro":
            P, cx, cy, wt, ht, ang = chuveiro_pos(it["png"], tuple(it["placa_c"]), tuple(it["parede"]),
                                                  it["placa_px"])
        else:
            c = it["c"]
            if it["tipo"] == "banco":
                P, _ = _banco_12k(c, it["tom"])
            elif it["tipo"] == "aparelho":
                P, _ = aparelho(it)
            else:
                P = BS.girar(BS.ler_png(it["png"]), it["giro"])
            cx, cy, wt, ht, ang = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2, c[2] - c[0], c[3] - c[1], 0.0
        out = BT.pousar(out, P, (cx - X0) * s, (cy - Ya3) * s, wt * s, ht * s, ang, [], PX_M * s, nao=nao_fn)
    print(f"    {reg_json.name}: {len(reg['pecas'])} peças nítidas no 12K, sobre a zona refeita")
    return out


def _banco_12k(c, tom, q=SAUNA):
    P = BS.ler_png(q["png"])
    sy = (c[3] - c[1]) / P.shape[0]
    alvo = (c[2] - c[0]) / sy
    p = q["pontas"]
    P = BS.esticar(P, 1, [(0, p, None), (p, P.shape[1] - p, alvo - 2 * p), (P.shape[1] - p, P.shape[1], None)])
    m = P[..., 3] > 250
    P[..., :3] = np.clip(P[..., :3] * (np.float32(tom) / np.median(P[..., :3][m], axis=0)), 0, 255)
    return P, tom


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(6.0, 900 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaB_PH_Subsolo_1311_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


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
    depois, reg, par = aplicar(antes)
    cv2.imwrite(str(a.saida or FINAL), depois)
    print(f"    {a.saida or FINAL}")
    if not a.saida:
        salvar_registro(antes, depois, reg, par)
        antes_depois(antes, depois)


if __name__ == "__main__":
    main()

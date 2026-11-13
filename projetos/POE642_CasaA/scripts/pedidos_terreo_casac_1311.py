"""Os post-its do cliente no Térreo da Casa C (13/11, quadro "POE 642 - Revisão de Imagens").

Sobre a final com a 1ª leva da biblioteca (`biblioteca_terreo_casac_1311`, commit `ANTES_COMMIT`):
- **"Representar as claraboias apenas com as linhas de fora, sem o X no meio para ficar mais discreto. Usar um tom
  cinza e as linhas mais fininhas. Padronizar para as outras plantas que tiverem claraboia."** (`claraboias`): as 5
  claraboias do PDF (DOC_LINHAS E PROJEÇÕES: a da varanda master, a do BH master 1, as dos closets master 1 e 2 e a do
  box do BH master 2) perdem o X e o tracejado grosso (preto ou branco: o tracejado de antes sai, o piso tapado por
  baixo, fora os contornos das esquadrias); entra só o retângulo de fora, tracejado, em cinza médio (128), ~0,8 px.
- **"Representar guarda-corpo das varandas"** (`guarda_corpo`): a lâmina de vidro que já estava na borda das varandas
  (clara demais, sumia no travertino) redesenhada como o guarda-corpo de vidro do deck da Casa A
  (`pedidos_terreo_casaa_1211c.vidro_ret`: o vidro, as duas faces em linha fina mais escura, o brilho e a sombra
  curta), de parede a parede: na varanda master (em cima e na lateral, até a parede do BH master 2), na varanda e na
  varanda 1.
- **"Colocar a seta em todas as escadas e a descrição"** (`escadas`): o triângulo no 1º degrau de quem desce, com a
  ponta para onde desce, o D logo abaixo dele, e "DESCE PARA O / SUBSOLO": nos degraus largos (no patamar de baixo) e
  na escada estreita (no deck, junto ao 1º degrau).
- **"Fazer as mesmas mudanças que foram apontadas no subsolo da casa A e que cabem para essa casa"** (`portas`): as
  portas de giro quina com quina na ponta da parede ("E AS PORTAS PRECISAM FAZER QUINA A QUINA COM A PAREDE. ISSO É
  REGRA PARA TODAS AS PLANTAS"), sem os marcos, com a folha de madeira clara e a soleira (`pedidos_subsolo_casab_1211.
  portas_sb`); as portas achadas no PDF (o arco e a folha da ARQ_PAREDE), as de parede deitada na imagem transposta.

  python3 pedidos_terreo_casac_1311.py [--antes <png>] [--saida <png>]
"""

import argparse
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casab as F                      # noqa: E402
import final3840_casac as C                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402
import regras_terreo_casab_1311 as RT            # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import pedidos_subsolo_casac_1311 as PS          # noqa: E402

CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Terreo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "c9d7643"
PX_M = B1.PX_M

# as claraboias (px: o retângulo de fora do PDF) e a cor do tracejado de antes (preto sobre a pedra, branco sobre a
# madeira); o novo: cinza médio, fino, tracejado (traço e vão, px)
CLARABOIAS = [{"nome": "varanda master", "ret": (736.0, 255.4, 950.8, 294.6), "antes": "preto"},
              {"nome": "BH master 1", "ret": (750.8, 328.0, 894.1, 355.1), "antes": "preto"},
              {"nome": "closet master 1", "ret": (950.8, 410.2, 980.0, 488.2), "antes": "branco", "miolo": True},
              {"nome": "closet master 2", "ret": (967.4, 867.9, 1039.4, 898.1), "antes": "branco", "miolo": True},
              {"nome": "box do BH master 2", "ret": (868.4, 907.2, 888.1, 966.9), "antes": "preto"}]
TRACO = {"cor": (128, 128, 128), "larg_px": 0.8, "traco_px": 6.0, "vao_px": 4.0, "ss": 8, "busca_px": 4,
         "miolo_tol": 5.0}
# os guarda-corpos (px): (x0, x1) na borda de cima (y) e a lateral da varanda master (x, y0, y1)
GUARDA = {"y": 247.0, "trechos_x": [(639.0, 1065.0), (1253.0, 1626.0), (1994.0, 2163.0)],
          "lateral": (637.0, 247.0, 827.0)}
# as escadas: o triângulo (px, a ponta para onde desce), a letra (a caixa da de antes, de onde vem o degrau que a
# cobre, e o topo da nova) e a descrição (centro x, base da 1ª linha)
ESCADAS = [
    {"nome": "degraus largos", "triangulo": [(563.0, 959.5), (573.0, 959.5), (568.0, 950.5)],
     "s_px": (558, 955, 580, 976), "s_fonte": (30, 0), "letra": "D", "letra_topo": 962.0,
     "texto": ("DESCE PARA O", "SUBSOLO"), "centro_x": 590.0, "base_y": 1004.0, "fundo": None},
    {"nome": "escada estreita", "triangulo": [(869.5, 1002.0), (869.5, 1013.0), (859.0, 1007.5)],
     "s_px": None, "texto": ("DESCE PARA O", "SUBSOLO"), "centro_x": 940.0, "base_y": 1012.0, "fundo": None},
]
# as portas: o arco e a folha da ARQ_PAREDE (`portas_pdf`); a parede (`esp_px`) e o vão dos marcos (`marco_px`) em
# volta da dobradiça; a soleira no bege das soleiras de antes (a mediana do vão `soleira_px`)
# (o BH externo e o louceiro 1: a busca das pontas da parede na imagem erra ali, e a soleira saía do vão; ficam como
# estavam)
PORTAS = {"esp_px": 9.0, "marco_px": 3.0, "soleira_px": (746, 846, 752, 888), "r_min": 20, "r_max": 80,
          "pular": ("porta em (2900, 719)", "porta em (652, 2253)")}
# "Tirar o contorno dos mobiliários" (os armários dos closets e dos quartos: os retângulos com diagonal da DOC_LINHAS):
# o traço laranja em volta de cada módulo vira o creme do próprio armário (a mediana dos px creme em volta)
ARMARIOS = {"croma_min": 40, "lum": (95, 178), "creme_lum": 185, "creme_croma": 45, "faixa_px": 2.6, "viz_px": 4}
# ---- 2ª leva de post-its (13/11, "Mais da casa C térreo")
# "Representar demarcação com piso.": no vão de grama entre o fim do caminho e a fileira de pisantes de baixo, um
# pisante de Bege Bahia na largura do caminho, com as juntas de grama dos pisantes (`junta_px`); o desenho vem do pisante
# de baixo (as metades de cima e de baixo, para ficarem as duas bordas)
PISANTE = {"x": (475, 574), "vao_y": (1666, 1745), "junta_px": 11, "fonte_y": (1745, 1827)}
# "Trocar essa representação do jardim de inverno" (as setas no jardim de inverno, no jardim 1 e na floreira junto à
# adega): como o jardim de 4,79 m² da Casa A e os jardins do Térreo da Casa B (`pedidos_terreo_casab_1211.jardins_tb`):
# a grama do gramado com a sombra de contato junto às paredes e poucas plantas menores, em tamanhos diferentes; os
# rótulos brancos ficam; nos dois de inverno, o X dos painéis fino e claro; a floreira com a terra e arbustos verdes
# iguais, com o mesmo espaço entre eles
JARDINS = {
    "jardins": {
        "inverno": {"caixa_px": (1775, 934, 2024, 1190), "x_doc": True, "rotulo_px": (1840, 985, 1972, 1026),
                    "plantas": [("palmeira_1", (1812, 972), 0.9), ("palmeira_3", (1988, 1152), 0.75),
                                ("arbusto_3", (1808, 1158), 0.45), ("arbusto_3", (1992, 968), 0.40)]},
        "inverno_2": {"caixa_px": (1892, 824, 2024, 918), "x_doc": True, "rotulo_px": (1922, 840, 2024, 890),
                      "plantas": [("palmeira_3", (1912, 900), 0.6), ("arbusto_3", (2006, 904), 0.36)]},
        "jardim_1": {"caixa_px": (1124, 839, 1230, 978), "rotulo_px": (1145, 900, 1212, 934),
                     "plantas": [("palmeira_3", (1152, 866), 0.7), ("arbusto_3", (1205, 960), 0.40)]}},
    "contato": (0.20, 3.0), "semente": 1311, "gramado_px": (620, 1700, 700, 1740), "branco": (250, 250, 250),
    "floreira": {"px": (2367, 932, 2464, 966), "n": 4, "d_m": 0.38, "terra": (34, 44, 56), "terra_ruido": 0.18,
                 "verde": (60, 102, 88)}}
# a gourmet: "Geral: Não precisa representar os armários inferiores ou superiores." (as divisões dos módulos na bancada
# de trás saem: as linhas cinza finas dentro do tampo; a borda do tampo fica); "Representar a churrasqueira" (a grelha da
# Casa A no módulo do meio, na profundidade do tampo com folga); "Alinhar as geladeiras" (as duas na geladeira inox G2,
# a frente para a gourmet, encostadas na parede, no mesmo alinhamento); "Acrescentar uma 5/6 banquetas" (6 banquetas B
# na face de baixo da ilha, viradas para ela, ~40% por baixo do tampo)
GOURMET = {"linhas_h": [(952, 1241, 1509), (970, 1283, 1369)], "linhas_v": [(1280, 1284), (1368, 1375), (1450, 1454)],
           "tampo_y": (933, 972), "pia_px": (1290, 938, 1334, 969), "desloc_px": 6,
           "grelha": {"png": "area-gourmet/grelha-churrasqueira", "cx": 1411.5, "cy": 952.0, "alt": 30.0},
           "geladeiras": {"png": "02-terreo/cozinha/geladeira-inox.png", "xs": [(1520.0, 1567.7), (1573.2, 1620.9)],
                          "y0": 933.0, "alt": 47.7, "limpa_px": (1516, 933, 1626, 990)},
           "banquetas": {"png": "area-gourmet/banqueta-b", "larg": 25.0, "borda_y": 1155.9, "x": (1231.4, 1562.8),
                         "n": 6}}
# "Trocar as cortinas pelo modelo padrão que escolhemos" (a C4 da Casa B: o linho em ondas com o trilho grafite do lado
# do vidro, `regras_terreo_casab_1311.cortina_desenho`) "e siga a orientação do post it" ("Pode deixar a cortina
# ultrapassar um pouco as laterais da janela."): os trechos do PDF (`final3840_casac.trechos_cortina_tc`: os da ARQ_LOUÇAS
# E METAIS e os do estar, na ARQ_MOBILIÁRIO) até a ponta da parede de cada lado do vão (até `busca_px`; mais longe, o
# trecho fica no tamanho do PDF), os da mesma janela unidos; onde a parede segue na mesma linha, a cortina passa
# `alem_m` dela, do lado de dentro (a cortina toda chega para dentro do ambiente o que precisa para não pisar na parede);
# onde a parede vira (um canto), ela para no vão
CORTINAS = {"busca_px": 110, "junta_px": 120, "alem_m": 0.15, "dentro_px": 3, "limpa": (4.0, 5.5), "face_px": 18}
# ---- 3ª leva (13/11, "Segue mais orientações do térreo da casa C")
# "Aqui tem que representar dois painéis pivotantes" (o vão entre a ponta da parede do jardim 1 e o fim da bancada da
# gourmet, do lado da varanda gourmet): dois painéis de madeira clara (o desenho das folhas das portas: o veio no
# comprido, o contorno e a sombra curta), fechados, na linha logo fora da bancada, cada um com o ponto do pivô
# "Geral: Não precisa representar os armários inferiores ou superiores com essa linha acima da bancada": também na
# cozinha, a divisão do módulo das cubas (a linha em pé no tampo); a borda da bancada fica
PIVOTANTES = {"x": (1224.5, 1230.0), "y": (979.0, 1156.0), "junta_px": 1.5, "pivo_frac": 0.18, "pivo_r": 1.3,
              "pivo_cor": (52, 60, 70), "semente": 1313}
LINHAS_COZINHA = [("v", 2408, 2412, 257, 291), ("h", 2203, 2409, 289, 291)]
ANTES_DEPOIS = {"claraboias_master": (620, 230, 1240, 1000), "armarios": (1040, 330, 2070, 560),
                "pisante": (420, 1500, 720, 1860), "jardins": (1100, 800, 2480, 1200), "gourmet": (1210, 900, 1660, 1200),
                "cortinas_estar": (1850, 1560, 2160, 1700), "cortinas_master": (740, 540, 860, 860),
                "cortinas_quartos": (1150, 300, 2200, 380), "cortinas_hall": (2330, 1420, 2730, 1680),
                "pivotantes": (1150, 940, 1330, 1190), "cozinha_bancada": (2160, 245, 2480, 300), "varandas": (1060, 215, 2200, 300),
                "escadas": (500, 880, 1060, 1080)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            C.contexto_c()
            _Q["Q"] = F.Quadro("Terreo")
    return _Q["Q"]


_Q = {}


# ----------------------------------------------------------------------------------------------------------------------
def _segmentos_doc(Q, ret, folga=3.0):
    x0, y0, x1, y1 = ret
    segs = []
    for d in Q.desenhos:
        if d.get("layer") != "DOC_LINHAS E PROJEÇÕES":
            continue
        for c in Q.caminhos(d):
            c = np.asarray(c)
            if c[:, 0].min() >= x0 - folga and c[:, 0].max() <= x1 + folga and c[:, 1].min() >= y0 - folga and \
                    c[:, 1].max() <= y1 + folga:
                segs.append(c)
    return segs


def _tracejado(M, p0, p1, X0, Y0, q, ss):
    (ax, ay), (bx, by) = p0, p1
    L = float(np.hypot(bx - ax, by - ay))
    ux, uy = (bx - ax) / L, (by - ay) / L
    t = 0.0
    while t < L:
        t1 = min(t + q["traco_px"], L)
        a = ((ax + ux * t - X0) * ss, (ay + uy * t - Y0) * ss)
        b = ((ax + ux * t1 - X0) * ss, (ay + uy * t1 - Y0) * ss)
        cv2.line(M, tuple(int(round(v)) for v in a), tuple(int(round(v)) for v in b), 255,
                 max(1, int(round(q["larg_px"] * ss))), cv2.LINE_AA)
        t += q["traco_px"] + q["vao_px"]


def claraboias(Q, out, qs=CLARABOIAS, q=TRACO):
    H, W = out.shape[:2]
    esq = np.zeros((H, W), np.uint8)                       # os contornos das esquadrias ficam
    for cs in RT._tracos_esquadrias(Q):
        for c in cs:
            cv2.polylines(esq, [np.int32(np.round(np.asarray(c)))], False, 1, 1)
    esq = cv2.dilate(esq, np.ones((5, 5), np.uint8)) > 0
    for cl in qs:
        x0, y0, x1, y1 = cl["ret"]
        X0, Y0, X1, Y1 = int(x0) - 12, int(y0) - 12, int(np.ceil(x1)) + 13, int(np.ceil(y1)) + 13
        # a. o tracejado de antes: perto das linhas do PDF, o preto (ou o branco) pouco colorido
        m = np.zeros((Y1 - Y0, X1 - X0), np.uint8)
        for c in _segmentos_doc(Q, cl["ret"]):
            cv2.polylines(m, [np.int32(np.round(c - [X0, Y0]))], False, 1, 2 * q["busca_px"] + 1)
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        lum, croma = reg.mean(axis=2), reg.max(axis=2) - reg.min(axis=2)
        if cl["antes"] == "preto":
            tr = (lum < 105) & (croma < 30)
        else:
            tr = (lum > 195) & (croma < 30)
        # (sobre a madeira, o branco também dentro do retângulo: os traços do render não caem exatamente no PDF)
        dentro = np.zeros_like(m)
        dentro[int(y0) - Y0 - 2:int(np.ceil(y1)) - Y0 + 3, int(x0) - X0 - 2:int(np.ceil(x1)) - X0 + 3] = 1
        tr &= ((m > 0) | ((dentro > 0) & (cl["antes"] == "branco"))) & ~esq[Y0:Y1, X0:X1]
        tr = cv2.dilate(tr.astype(np.uint8), np.ones((3, 3), np.uint8))
        tr &= ~esq[Y0:Y1, X0:X1]
        sub = cv2.inpaint(np.ascontiguousarray(out[Y0:Y1, X0:X1]), tr * 255, 3, cv2.INPAINT_TELEA)
        out[Y0:Y1, X0:X1][tr > 0] = sub[tr > 0]
        # o miolo da claraboia de antes (um véu claro, liso, sobre o vinílico): as réguas do vinílico de volta, vezes a
        # luz do piso em volta (`regras_terreo_casab_1311.piso_reguas`)
        if cl.get("miolo"):
            bur = np.zeros((H, W), bool)
            bur[int(y0) - 1:int(np.ceil(y1)) + 2, int(x0) - 1:int(np.ceil(x1)) + 2] = True
            escuro = cv2.dilate((out.astype(np.float32).mean(axis=2) < 110).astype(np.uint8), np.ones((5, 5), np.uint8))
            bur &= escuro == 0                              # os rótulos logo abaixo ficam
            out = BS.quieto(RT.piso_reguas, Q, out, bur)
        # b. só o retângulo de fora, tracejado, cinza e fino
        ss = q["ss"]
        M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
        for p0, p1 in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            _tracejado(M, p0, p1, X0, Y0, q, ss)
        a = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        out = PS._pintar(out, a, X0, Y0, q["cor"])
        print(f"    claraboia ({cl['nome']}): o X e o tracejado {cl['antes']} saem ({int(tr.sum())} px); só o "
              f"retângulo de fora, tracejado, em cinza {q['cor'][0]}, {q['larg_px']} px")
    return out


def guarda_corpo(out, q=GUARDA):
    import pedidos_terreo_casaa_1211c as PA
    import terreo_casaa_1011 as TA
    # (mais legível que a lâmina de antes, que sumia no travertino): 3 px, as faces mais escuras, sem transparência
    qv = dict(TA.ESCADAS_TA["jardim"]["vidro"], larg_min_px=3.0, contorno=(84, 88, 92), alfa=1.0, linha_px=0.7)
    y = q["y"]
    for x0, x1 in q["trechos_x"]:
        out = PA.vidro_ret(out, (x0, y - 1.5, x1, y + 1.5), qv)
    x, ya, yb = q["lateral"]
    T = np.ascontiguousarray(out.transpose(1, 0, 2))
    T = PA.vidro_ret(T, (ya + 1.5, x - 1.5, yb, x + 1.5), qv)
    out = np.ascontiguousarray(T.transpose(1, 0, 2))
    print(f"    guarda-corpo: a lâmina de vidro nas {len(q['trechos_x'])} bordas de cima das varandas e na lateral da "
          "varanda master, de parede a parede")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def portas_pdf(Q, q=PORTAS):
    """As portas de giro do PDF: cada arco da ARQ_PAREDE (o quarto de círculo) com a folha (o retângulo branco fino do
    mesmo comprimento) num canto dele; a porta no formato de `pedidos_subsolo_casab_1211.PORTAS_SB` (a folha deitada:
    a parede em pé; a folha em pé vai à imagem transposta)."""
    def q2(r):
        a, b = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        return min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])
    arcos, folhas = [], []
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE":
            continue
        x0, y0, x1, y1 = q2(d["rect"])
        w, h = x1 - x0, y1 - y0
        if d["type"] == "s" and any(it[0] == "c" for it in d["items"]) and q["r_min"] <= w <= q["r_max"] and \
                abs(w - h) < 1.5:
            pts = np.concatenate([np.asarray(c) for c in Q.caminhos(d)])
            meio = pts[len(pts) // 2]
            # o centro do arco (a dobradiça): o canto da caixa mais longe do meio do arco
            cantos = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
            centro = max(cantos, key=lambda c: np.hypot(c[0] - meio[0], c[1] - meio[1]))
            arcos.append((x0, y0, x1, y1, centro))
        if d["type"] in ("f", "fs") and d.get("fill") and min(d["fill"]) > 0.9 and 1.8 <= min(w, h) <= 3.2 and \
                q["r_min"] <= max(w, h) <= q["r_max"]:
            folhas.append((x0, y0, x1, y1))
    em_pe, deitadas, sem = [], [], []
    for ax0, ay0, ax1, ay1, (cx, cy) in arcos:
        Rr = ax1 - ax0
        best = None
        for f in folhas:
            fx0, fy0, fx1, fy1 = f
            if abs(max(fx1 - fx0, fy1 - fy0) - Rr) > 2.5:
                continue
            dd = min(np.hypot(cx - px, cy - py) for px in (fx0, fx1) for py in (fy0, fy1))
            if dd < 3.5 and (best is None or dd < best[0]):
                best = (dd, f, (cx, cy))
        if best is None:
            sem.append((ax0, ay0, ax1, ay1))
            continue
        _, (fx0, fy0, fx1, fy1), (hx, hy) = best
        deitada = (fx1 - fx0) > (fy1 - fy0)
        if not deitada:                                     # na imagem transposta: x <-> y
            ax0, ay0, ax1, ay1 = ay0, ax0, ay1, ax1
            fx0, fy0, fx1, fy1 = fy0, fx0, fy1, fx1
            hx, hy = hy, hx
        lado = +1 if abs(ax0 - hx) < abs(ax1 - hx) else -1
        dobra = "topo" if abs(ay0 - hy) < abs(ay1 - hy) else "base"
        e, mk = q["esp_px"], q["marco_px"]
        parede = (hx - e, hx) if lado > 0 else (hx, hx + e)
        if dobra == "topo":
            topo, base = hy - mk, hy + Rr + mk
        else:
            topo, base = hy - Rr - mk, hy + mk
        p = {"nome": f"porta em ({(ax0 + ax1) / 2:.0f}, {(ay0 + ay1) / 2:.0f})", "parede": parede, "topo": topo,
             "base": base, "folha": (fx0, fy0, fx1, fy1), "dobra": dobra, "lado": lado, "soleira": True}
        (em_pe if deitada else deitadas).append(p)
    return em_pe, deitadas, sem


def portas(Q, out, q=PORTAS):
    import pedidos_subsolo_casab_1211 as PB
    em_pe, deitadas, sem = portas_pdf(Q, q)
    x0, y0, x1, y1 = q["soleira_px"]
    sol = tuple(float(v) for v in np.median(out[y0:y1, x0:x1].reshape(-1, 3), axis=0))
    base = dict(PB.PORTAS_SB, tique_px=(0, 0, 0, 0), soleira=sol)
    feitas, falhas = [], []

    def uma(img, p):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                novo = PB.portas_sb(Q, img.copy(), q=dict(base, portas=[p]))
            feitas.append(p["nome"])
            return novo
        except Exception as ex:                             # noqa: BLE001
            falhas.append(f"{p['nome']} ({type(ex).__name__})")
            return img
    for p in em_pe:
        if p["nome"] not in q.get("pular", ()):
            out = uma(out, p)
    T = np.ascontiguousarray(out.transpose(1, 0, 2))
    for p in deitadas:
        if p["nome"] not in q.get("pular", ()):
            T = uma(T, p)
    out = np.ascontiguousarray(T.transpose(1, 0, 2))
    print(f"    portas: {len(feitas)} portas de giro quina com quina na ponta da parede (sem os marcos, a folha de "
          f"madeira clara, a soleira): {', '.join(feitas)}")
    if falhas:
        print(f"      não deu (ficam como estão): {', '.join(falhas)}")
    print(f"      {len(sem)} arcos sem a folha do PDF ficam como estão: "
          f"{', '.join(f'({(a + c) / 2:.0f}, {(b + d) / 2:.0f})' for a, b, c, d in sem)}")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def escadas(out, qs=ESCADAS):
    for q in qs:
        out = _escada(out, q, q.get("letra", "D"))
    return out


def _escada(out, q, letra):
    from PIL import ImageFont
    from rodape_entrega import FONTES
    from cliente_subsolo_casaa_0511 import _alfa_texto
    import final3840_casaa as FA
    e = FA.ESCADA_A
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), e["corpo_px"] * 4)
    if q["s_px"] is not None:
        x0, y0, x1, y1 = q["s_px"]
        dx, dy = q["s_fonte"]
        reg = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        s_ = cv2.dilate((reg < 150).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        ys, xs = np.nonzero(s_)
        out[ys + y0, xs + x0] = out[ys + y0 + dy, xs + x0 + dx]
        pts = np.float32(q["triangulo"])
        cx = float(pts[:, 0].min() + pts[:, 0].max()) / 2
        l_, t_, r_, b_ = fonte.getbbox(letra, anchor="ls")
        ox, oy = cx - (l_ + r_) / 8, q["letra_topo"] - t_ / 4
        W, H = int((r_ - l_) / 4) + 12, e["corpo_px"] * 3
        X0, Y0 = int(ox) - 4, int(oy) - e["corpo_px"] * 2
        out = PS._pintar(out, _alfa_texto(letra, fonte, e["corpo_px"], ox, oy, (X0, Y0, W, H)), X0, Y0, e["cor_texto"])
    pts = np.float32(q["triangulo"])
    bx0, by0 = np.floor(pts.min(axis=0)).astype(int) - 2
    bx1, by1 = np.ceil(pts.max(axis=0)).astype(int) + 3
    out = PS._pintar(out, PS._alfa_poligono(pts, bx0, by0, bx1 - bx0, by1 - by0), bx0, by0, PS.COR_SETA)
    larg = [fonte.getlength(t) / 4 for t in q["texto"]]
    for i, (linha, lw) in enumerate(zip(q["texto"], larg)):
        tx, ly = q["centro_x"] - lw / 2, q["base_y"] + i * PS.ENTRELINHA
        W, H = int(lw) + 12, e["corpo_px"] * 3
        X0, Y0 = int(tx) - 4, int(ly) - e["corpo_px"] * 2
        out = PS._pintar(out, _alfa_texto(linha, fonte, e["corpo_px"], tx, ly, (X0, Y0, W, H)), X0, Y0,
                         e["cor_texto"])
    print(f"    {q['nome']}: a seta no 1º degrau de quem desce{', o ' + letra + ' logo abaixo dela' if q['s_px'] else ''}"
          f" e \"{' / '.join(q['texto'])}\"")
    return out


def armarios(Q, out, q=ARMARIOS):
    """O traço laranja na borda de cada módulo de armário (a faixa de dentro do retângulo do PDF, até `faixa_px` da
    borda) vira o creme do próprio módulo (a média dos px creme vizinhos); fora do retângulo, o piso fica."""
    H, W = out.shape[:2]
    f = out.astype(np.float32)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    creme_g = (lum >= q["creme_lum"]) & (croma <= q["creme_croma"])
    laranja = (croma >= q["croma_min"]) & (lum >= q["lum"][0]) & (lum <= q["lum"][1])
    total = 0
    for d in Q.desenhos:
        if d.get("layer") != "DOC_LINHAS E PROJEÇÕES":
            continue
        for c in Q.caminhos(d):
            c = np.asarray(c)
            w, h = np.ptp(c[:, 0]), np.ptp(c[:, 1])
            if not (min(w, h) > 3 and max(w, h) > 20):      # a diagonal do armário: a caixa dela é a do módulo
                continue
            x0, y0 = c.min(0)
            x1, y1 = c.max(0)
            e = int(np.ceil(q["faixa_px"])) + 4
            X0, Y0, X1, Y1 = int(np.floor(x0)) - e, int(np.floor(y0)) - e, int(np.ceil(x1)) + e, int(np.ceil(y1)) + e
            yy, xx = np.mgrid[Y0:Y1, X0:X1] + 0.5
            dentro = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
            # a distância à borda do retângulo, dos dois lados (o traço do render cai até ~2 px fora do PDF)
            dx_ = np.maximum(np.maximum(x0 - xx, xx - x1), 0)
            dy_ = np.maximum(np.maximum(y0 - yy, yy - y1), 0)
            fora = np.hypot(dx_, dy_)
            borda = np.where(dentro, np.minimum.reduce([xx - x0, x1 - xx, yy - y0, y1 - yy]), fora)
            cr = dentro & creme_g[Y0:Y1, X0:X1]
            perto = cv2.dilate(cr.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
            tr = (borda <= q["faixa_px"]) & laranja[Y0:Y1, X0:X1] & perto
            if not tr.any() or cr.sum() < 20:
                continue
            k = 2 * q["viz_px"] + 1
            reg = f[Y0:Y1, X0:X1]
            num = cv2.blur(reg * cr[..., None], (k, k))
            den = cv2.blur(cr.astype(np.float32), (k, k))[..., None]
            cor = num / np.maximum(den, 1e-4)
            ok = tr & (den[..., 0] > 0.1)
            reg[ok] = cor[ok]
            total += int(ok.sum())
    print(f"    armários: o contorno laranja na borda dos módulos sai ({total} px), no creme deles")
    return np.clip(np.round(f), 0, 255).astype(np.uint8)




def cortinas(Q, out, reg=None, q=CORTINAS):
    import ajustes_casab as AB
    qc = RT.CORTINAS_TB
    with contextlib.redirect_stdout(io.StringIO()):
        with F.em_quadro(Q):
            trechos = C.trechos_cortina_tc(Q.chave, AB.trechos_cortina_b)
    par = BS.quieto(lambda: Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill")
                                          and max(d["fill"]) < 0.6, ss=2) > 0.3)
    alem = q["alem_m"] * Q.px_m
    # 1. cada trecho até a ponta da parede de cada lado (do lado de dentro, a `dentro_px` do eixo)
    res = []
    for o, vidro, ex, e0, e1 in trechos:
        pq = par if o == "v" else par.T
        v = vidro if o == "v" else {"cima": "esquerda", "baixo": "direita"}[vidro]
        # a ponta da parede: na linha do lado de dentro (os batentes, um canto) ou na do lado do vidro (a parede que
        # segue na mesma linha da janela), a que vier primeiro
        X = int(round(ex))
        sv = -1 if v == "esquerda" else 1                   # o lado do vidro
        cols = [X - sv * q["dentro_px"]] + [X + sv * k for k in range(2, 8)]

        def ate(y, passo):
            for yy in range(int(round(y)), int(round(y)) + passo * q["busca_px"], passo):
                if pq[yy, cols].any():
                    return yy - passo * 0.5, True
            return None, False
        a0, ok0 = ate(e0, -1)
        a1, ok1 = ate(e1, 1)
        res.append([o, v, float(ex), a0 if ok0 else e0, a1 if ok1 else e1, ok0, ok1])
    # os trechos da mesma janela (a mesma linha) que se sobrepõem depois de levados às paredes: unidos
    unidos = []
    for r in sorted(res, key=lambda t: (t[0], t[1], t[3])):
        def sem_parede(u, r):                           # entre os dois painéis da mesma linha, nenhuma parede
            pq = par if r[0] == "v" else par.T
            X = int(round(r[2]))
            a, b = int(np.floor(min(u[4], r[3]))), int(np.ceil(max(u[4], r[3])))
            return b - a <= q["junta_px"] and not pq[a:b + 1, X - 4:X + 5].any()
        u = next((u for u in unidos if u[:2] == r[:2] and abs(u[2] - r[2]) < 3 and r[4] > u[3] - 2
                  and (r[3] < u[4] + 2 or sem_parede(u, r))), None)
        if u:
            if r[3] < u[3]:
                u[3], u[5] = r[3], r[5]
            if r[4] > u[4]:
                u[4], u[6] = r[4], r[6]
        else:
            unidos.append(list(r))
    # 2. a passagem além do vão e o recuo para dentro
    feitos, alem_n = 0, 0
    for o, v, ex, t0, t1, ok0, ok1 in unidos:
        pq = par if o == "v" else par.T
        im = out if o == "v" else out.transpose(1, 0, 2)
        prof = qc["prof_px"]
        c0 = ex - qc["vidro_px"] if v == "esquerda" else ex + qc["vidro_px"] - prof
        X = int(round(ex))
        desloc = 0.0
        pontas = []
        for t, ok, passo in ((t0, ok0, -1), (t1, ok1, 1)):
            if not ok:
                pontas.append(t)
                continue
            tt = int(round(t + passo * 3))
            col = pq[tt, X - q["face_px"]:X + q["face_px"] + 1]
            idx = np.nonzero(col)[0]
            if not len(idx):
                pontas.append(t)
                continue
            face = (X - q["face_px"] + idx.max() + 1) if v == "esquerda" else (X - q["face_px"] + idx.min())
            d_ = max(0.0, face - c0) if v == "esquerda" else min(0.0, face - (c0 + prof))
            desloc = max(desloc, d_, key=abs) if abs(d_) <= 6 else desloc
            pontas.append((t, passo, face))
        a0_, a1_ = c0 + desloc, c0 + desloc + prof
        fim = []
        for p in pontas:
            if not isinstance(p, tuple):
                fim.append(p)
                continue
            t, passo, face = p
            # a faixa da cortina além do vão: livre da parede (a parede segue na linha) ou não (um canto)
            ys = np.arange(int(round(t)), int(round(t + passo * alem)), passo)
            xs = np.arange(int(np.floor(a0_)), int(np.ceil(a1_)))
            livre = not pq[np.ix_(ys, xs)].any() if len(ys) else False
            if livre:
                fim.append(t + passo * alem)
                alem_n += 1
            else:
                fim.append(t)
        T0, T1 = fim
        # o pano e o trilho de antes saem (só no vão): o piso logo do lado de dentro, em espelho
        b0 = ex - q["limpa"][0] if v == "esquerda" else ex - q["limpa"][1]
        b1 = ex + q["limpa"][1] if v == "esquerda" else ex + q["limpa"][0]
        A0, A1 = int(np.floor(b0)), int(np.ceil(b1))
        S0, S1 = int(np.floor(t0)), int(np.ceil(t1))
        n = A1 - A0
        livre_ = ~pq[S0:S1, A0:A1]
        if v == "esquerda":
            fonte = im[S0:S1, A1:A1 + n][:, ::-1].copy()
        else:
            fonte = im[S0:S1, A0 - n:A0][:, ::-1].copy()
        alvo = im[S0:S1, A0:A1]
        alvo[livre_] = fonte[livre_]
        it = {"tipo": "cortina", "o": o, "v": v, "ex": ex + desloc, "t0": T0, "t1": T1}
        P, cx, cy, wt, ht = RT.cortina_desenho(it, qc)
        o_ = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, 0.0, BT.SOMBRAS["movel"][1:], PX_M)
        out = np.clip(np.round(o_), 0, 255).astype(np.uint8)
        if reg is not None:
            reg.append(it)
        feitos += 1
    print(f"    cortinas: {feitos} trilhos com a cortina de linho em ondas (a C4, o trilho grafite do lado do vidro); "
          f"{alem_n} pontas passam {q['alem_m']:.2f} m além do vão, do lado de dentro")
    return out

# ----------------------------------------------------------------------------------------------------------------------
# A 2ª leva de post-its
def pisante(out, q=PISANTE):
    x0, x1 = q["x"]
    a, b = q["vao_y"]
    j = q["junta_px"]
    y0, y1 = a + j, b - j
    h = y1 - y0
    f0, f1 = q["fonte_y"]
    meio = h // 2
    pedra = np.concatenate([out[f0:f0 + meio, x0:x1], out[f1 - (h - meio):f1, x0:x1]], axis=0)
    out[y0:y1, x0:x1] = pedra
    print(f"    o pisante de Bege Bahia no vão do caminho (x {x0}-{x1}, y {y0}-{y1}), com as juntas de grama de {j} px")
    return out


def jardins(Q, img, q=JARDINS):
    import json as _json
    import paisagismo as PG
    import terreo_casaa_1011 as TC
    import final3840_casaa_terreo as FT
    sys.path.insert(0, str(AQUI.parents[1] / "_texturas"))
    from texturas import textura
    from scipy import ndimage
    out = img.astype(np.float32)
    rng = np.random.default_rng(q["semente"])
    sombra = _json.loads((AQUI.parents[1] / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    par_pdf = BS.quieto(lambda: Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                                              and max(d["fill"]) < 0.6, ss=2) > 0.3)
    cadeias = BS.quieto(FT.cadeias_tracejadas, Q, ["DOC_LINHAS E PROJEÇÕES"], min_n=2, min_ext=20)
    for nome, e in q["jardins"].items():
        x0, y0, x1, y1 = e["caixa_px"]
        M = np.zeros(img.shape[:2], bool)
        M[y0:y1, x0:x1] = True
        M &= ~PS._dil(par_pdf, 1)
        I = np.clip(np.round(out), 0, 255).astype(np.int16)
        geo = np.zeros(img.shape[:2], np.uint8)
        if e.get("x_doc"):
            for _, _, ss in cadeias:
                for s_ in ss:
                    (u0, v0), (u1, v1) = Q.p2q(s_[0], s_[1]), Q.p2q(s_[2], s_[3])
                    cv2.line(geo, (int(round(u0)), int(round(v0))), (int(round(u1)), int(round(v1))), 1, 2)
        claros = (I.mean(axis=2) > 150) & ((I.max(axis=2) - I.min(axis=2)) < 22) & M & ~PS._dil(geo > 0, 2)
        n_, lab_, st_, _ = cv2.connectedComponentsWithStats(claros.astype(np.uint8), 8)
        fios = np.isin(lab_, [i for i in range(1, n_) if max(st_[i, 2], st_[i, 3]) >= 25])
        M &= ~PS._dil(fios, 1)
        a0, b0, a1, b1 = e["rotulo_px"]
        txt = np.zeros(img.shape[:2], bool)
        txt[b0:b1, a0:a1] = ((I.mean(axis=2) > 185) & ((I.max(axis=2) - I.min(axis=2)) < 35))[b0:b1, a0:a1]
        if e.get("x_doc"):
            branco = txt.copy()
            txt &= ~(geo > 0)
            txt = (ndimage.binary_closing(txt, np.ones((3, 3))) & branco) | txt
        txt = PS._dil(txt, 1) & (I.mean(axis=2) > 120)
        h, w = y1 - y0, x1 - x0
        G = textura("grama_padrao", Q.px_m, h, w, semente=q["semente"] + len(nome)).astype(np.float32)
        # no tom do gramado do lote (a mediana dele, `gramado_px`): a textura sozinha saía oliva, mais escura
        ga, gb, gc, gd = q["gramado_px"]
        alvo = np.median(img[gb:gd, ga:gc].reshape(-1, 3).astype(np.float32), axis=0)
        G *= (alvo / np.maximum(np.median(G.reshape(-1, 3), axis=0), 1))[None, None]
        dist = cv2.distanceTransform(M[y0:y1, x0:x1].astype(np.uint8), cv2.DIST_L2, 5)
        k, alc = q["contato"]
        G *= (1 - k * np.exp(-dist / alc))[..., None]
        reg = out[y0:y1, x0:x1]
        mm = M[y0:y1, x0:x1]
        reg[mm] = G[mm]
        tmp = out.copy()
        for pl, (cx, cy), d in e["plantas"]:
            TC._pousar(tmp, pl, cx, cy, d, Q.px_m)
        a = cv2.GaussianBlur(cv2.erode(M.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.6)
        out = tmp * a[..., None] + out * (1 - a[..., None])
        # os rótulos brancos de volta, pelo alfa (o branco sobre as plantas escuras de antes), na caixa do rótulo
        lum0 = img[b0:b1, a0:a1].astype(np.float32).mean(axis=2)
        cr0 = (img[b0:b1, a0:a1].max(axis=2).astype(np.int16) - img[b0:b1, a0:a1].min(axis=2))
        al = np.clip((lum0 - 95.0) / (240.0 - 95.0), 0, 1) * (cr0 < 50)
        al[al < 0.12] = 0
        if e.get("x_doc"):
            al *= ~(geo[b0:b1, a0:a1] > 0) | (lum0 > 200)
        out[b0:b1, a0:a1] = out[b0:b1, a0:a1] * (1 - al[..., None]) + np.float32(q["branco"]) * al[..., None]
        txt = np.zeros(img.shape[:2], bool)
        txt[b0:b1, a0:a1] = al > 0.12
        if e.get("x_doc"):
            segs = []
            for _, _, ss in cadeias:
                for s_ in ss:
                    u, v = Q.p2q((s_[0] + s_[2]) / 2, (s_[1] + s_[3]) / 2)
                    if x0 <= u <= x1 and y0 <= v <= y1:
                        segs.append(s_)
            fq = TC.FINOS_TA
            pq = dict(FT.PROJ, larg_px=fq["larg_px"], preto=fq["escuro"], branco=fq["claro"], limiar=fq["limiar"])
            o8 = np.clip(np.round(out), 0, 255).astype(np.uint8)
            novo, _ = BS.quieto(FT.preto_branco, Q, o8, segs, pq)
            tapa = PS._dil(txt, TC.FINOS_TA["folga_rotulo"])
            novo[tapa] = o8[tapa]
            out = novo.astype(np.float32)
        print(f"    jardim {nome}: a grama da Casa A e {len(e['plantas'])} plantas menores"
              + ("; o X dos painéis fino e claro" if e.get("x_doc") else ""))
    f = q["floreira"]
    x0, y0, x1, y1 = f["px"]
    h, w = y1 - y0, x1 - x0
    terra = np.float32(f["terra"])[None, None] * (1 + f["terra_ruido"] * PG.ruido((h, w), 2.0, rng))[..., None]
    out[y0:y1, x0:x1] = terra
    cor0, al0, d0 = PG._sprite("arbusto")
    var = PG._tingir(cor0, al0, f["verde"])
    dpx = f["d_m"] * Q.px_m
    passo = w / f["n"]
    pecas = []
    for i in range(f["n"]):
        c, a_ = PG._colocar(var, al0, d0, dpx, rng.uniform(0, 360))
        pecas.append((c, a_, x0 + passo * (i + 0.5), (y0 + y1) / 2, dpx))
    lim = np.zeros(img.shape[:2], np.float32)
    lim[y0:y1, x0:x1] = 1
    out = PG._camada(out, pecas, lim, sombra)
    print(f"    floreira junto à adega: a terra e {f['n']} arbustos verdes iguais, com o mesmo espaço entre eles")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def gourmet(Q, out, q=GOURMET):
    par = BS.quieto(lambda: __import__("final3840_casaa").paredes_pdf(Q)) > 0.3
    # a. as divisões dos módulos na bancada de trás: as linhas finas (cinza claro sobre o granito) saem, cada uma com o
    # granito logo ao lado (`desloc_px`); a borda do tampo (junto à parede e na frente) e o fim dele junto às geladeiras
    # ficam
    d_ = q["desloc_px"]
    px0, py0, px1, py1 = q["pia_px"]
    n = 0
    for y, xa, xb in q["linhas_h"]:
        for x in range(xa, xb):
            if px0 <= x < px1 and py0 <= y < py1:
                continue
            out[y - 1:y + 2, x] = out[y - 1 + d_ - 3:y + 2 + d_ - 3, x] if y + d_ < q["tampo_y"][1] else \
                out[y - 1 - d_:y + 2 - d_, x]
            n += 3
    ta, tb = q["tampo_y"]
    for xa, xb in q["linhas_v"]:
        w_ = xb - xa
        for y in range(ta, tb):
            if px0 <= xa < px1 and py0 <= y < py1:
                continue
            out[y, xa:xb] = out[y, xb + 2:xb + 2 + w_]
            n += w_
    print(f"    gourmet: as divisões dos armários na bancada de trás saem ({len(q['linhas_h'])} deitadas, "
          f"{len(q['linhas_v'])} em pé, {n} px); o tampo liso, as bordas ficam")
    # b. a churrasqueira
    g = q["grelha"]
    P = RT.ler_peca("02-terreo/" + g["png"] + ".png")
    wt = g["alt"] * P.shape[1] / P.shape[0]
    it = RT.item_bib("BT", g["png"], g["cx"], g["cy"], wt, g["alt"], 0.0, None, None)
    out = RT.pousar_bib(out, it, par)
    print(f"    gourmet: a grelha da churrasqueira da Casa A ({wt:.0f} x {g['alt']:.0f} px) no módulo do meio do tampo")
    # c. as geladeiras alinhadas
    ge = q["geladeiras"]
    a, b, c, d = ge["limpa_px"]
    out = __import__("biblioteca_subsolo_casab_1311").piso_desloc(out, (a, b, c, d), par, 0, 1, folga=0)
    for gx0, gx1 in ge["xs"]:
        it = {"tipo": "png", "png": ge["png"], "c": [gx0, ge["y0"], gx1, ge["y0"] + ge["alt"]], "sombra": "movel"}
        out = RT.pousar_peca(out, it, __import__("biblioteca_terreo_casaa_1211").SOMBRAS["movel"], par)
    print(f"    gourmet: as 2 geladeiras inox alinhadas (topo em y {ge['y0']:.0f}, {ge['alt']:.1f} px), a frente para a "
          "gourmet")
    # d. as banquetas na face de baixo da ilha
    bq = q["banquetas"]
    xa, xb = bq["x"]
    passo = (xb - xa) / bq["n"]
    antes = out.copy()
    yb = bq["borda_y"]
    for i in range(bq["n"]):
        cx = xa + passo * (i + 0.5)
        it = RT.item_bib("BT", bq["png"], cx, yb + 2.7, bq["larg"], None, 180.0, "movel", None)
        out = RT.pousar_bib(out, it, par)
    Y = int(np.floor(yb))
    fr = yb - Y                                          # o tampo por cima (a parte da banqueta sob ele não aparece)
    X0, X1 = int(xa) - 2, int(np.ceil(xb)) + 3
    out[Y - 30:Y, X0:X1] = antes[Y - 30:Y, X0:X1]
    out[Y, X0:X1] = np.clip(np.round(antes[Y, X0:X1] * fr + out[Y, X0:X1] * (1 - fr)), 0, 255).astype(np.uint8)
    print(f"    gourmet: {bq['n']} banquetas B na face de baixo da ilha, viradas para ela, ~40% por baixo do tampo")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# A 3ª leva
def pivotantes(out, q=PIVOTANTES):
    import pedidos_terreo_casaa_2910 as PT
    import um_pav_casaa_1111 as U
    qf = U.RETOQUES_1111F["folha"]
    ss = 8
    rng = np.random.default_rng(q["semente"])
    x0, x1 = q["x"]
    ya, yb = q["y"]
    meio = (ya + yb) / 2
    for fy0, fy1 in ((ya, meio - q["junta_px"] / 2), (meio + q["junta_px"] / 2, yb)):
        FX0, FY0 = int(np.floor(x0)) - 3, int(np.floor(fy0)) - 3
        fw, fh = int(np.ceil(x1)) + 3 - FX0, int(np.ceil(fy1)) + 3 - FY0
        mk = PT._ret_arred((x0, fy0, x1, fy1), qf["raio_px"], FX0, FY0, fh, fw, ss)
        al = cv2.resize(mk, (fw, fh), interpolation=cv2.INTER_AREA)
        sx, sy, sg = qf["sombra_px"]
        sb = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, sx], [0, 1, sy]]), (fw, fh)), (0, 0), sg)
        r_ = out[FY0:FY0 + fh, FX0:FX0 + fw].astype(np.float32)
        r_ *= (1 - qf["sombra"] * sb * (1 - al))[..., None]
        out[FY0:FY0 + fh, FX0:FX0 + fw] = np.clip(np.round(r_), 0, 255).astype(np.uint8)
        n_ = cv2.GaussianBlur(rng.normal(0, 1, mk.shape).astype(np.float32), (0, 0), sigmaX=0.6 * ss, sigmaY=6.0 * ss)
        n_ = 1 + qf["veio"] * n_ / max(float(n_.std()), 1e-6)
        out = PT._pintar(out, FX0, FY0, fw, fh, ss, mk, np.float32(qf["madeira"])[None, None] * n_[..., None])
        borda = np.clip(mk - cv2.erode(mk, np.ones((5, 5), np.uint8)), 0, 1) * qf["contorno_alfa"]
        out = PT._pintar(out, FX0, FY0, fw, fh, ss, borda,
                         np.float32(qf["contorno"])[None, None] * np.ones_like(borda)[..., None])
        # o pivô: um ponto escuro a `pivo_frac` do comprimento, a partir da ponta de cima do painel
        cx, cy = (x0 + x1) / 2, fy0 + q["pivo_frac"] * (fy1 - fy0)
        Mp = np.zeros((fh * ss, fw * ss), np.uint8)
        cv2.circle(Mp, (int(round((cx - FX0) * ss)), int(round((cy - FY0) * ss))), int(round(q["pivo_r"] * ss)), 255, -1,
                   cv2.LINE_AA)
        Mp = Mp.astype(np.float32) / 255
        out = PT._pintar(out, FX0, FY0, fw, fh, ss, Mp, np.float32(q["pivo_cor"])[None, None] * np.ones_like(Mp)[..., None])
    print(f"    gourmet: os 2 painéis pivotantes de madeira clara no vão junto à bancada (y {ya:.0f}-{yb:.0f}), fechados, "
          "com o ponto do pivô")
    return out


def linhas_cozinha(out, qs=LINHAS_COZINHA):
    for o, a, b, y0, y1 in qs:
        if o == "v":
            w_ = b - a
            out[y0:y1, a:b] = out[y0:y1, b + 3:b + 3 + w_]
        else:                                           # a linha deitada: o granito logo acima
            h_ = y1 - y0
            out[y0:y1, a:b] = out[y0 - 3 - h_:y0 - 3, a:b]
    print(f"    cozinha: a divisão do módulo das cubas no tampo sai ({len(qs)} linhas); a borda da bancada fica")
    return out

# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    out = claraboias(Q, out)
    out = armarios(Q, out)
    out = portas(Q, out)
    out = cortinas(Q, out)
    out = guarda_corpo(out)
    out = escadas(out)
    out = pisante(out)
    out = jardins(Q, out)
    out = gourmet(Q, out)
    out = pivotantes(out)
    out = linhas_cozinha(out)
    return out


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(3.0, 1000 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        lado = a.shape[1] <= a.shape[0] * 1.6
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b]) if lado else \
            np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS" if lado else "ANTES (em cima) | DEPOIS (embaixo)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaC_PH_Terreo_1311_postits_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def final_de(commit):
    dado = subprocess.run(["git", "show", f"{commit}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"], cwd=RAIZ_GIT,
                          capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes) if a.antes else final_de(ANTES_COMMIT)
    depois = aplicar(antes)
    if a.saida:
        cv2.imwrite(a.saida, depois)
        print(f"    {a.saida}")
        return
    cv2.imwrite(str(FINAL), depois)
    print(f"    {FINAL.name}")
    antes_depois(antes, depois)


if __name__ == "__main__":
    main()

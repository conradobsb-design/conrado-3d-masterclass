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
import pedidos_subsolo_casac_1311 as PS          # noqa: E402

CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Terreo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "c9d7643"

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
ANTES_DEPOIS = {"claraboias_master": (620, 230, 1240, 1000), "armarios": (1040, 330, 2070, 560), "varandas": (1060, 215, 2200, 300),
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


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    out = claraboias(Q, out)
    out = armarios(Q, out)
    out = portas(Q, out)
    out = guarda_corpo(out)
    out = escadas(out)
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

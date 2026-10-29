"""Casa B, Subsolo: os pedidos de 29/10/26, antes do OK da Casa B.

1. O Térreo nevoado (`nevoado_sb`). Pedido do usuário, vendo o Subsolo: "preciso que represente nevoado as partes que
constam no pdf, correspondente fora do subsolo. o resto do terreno permanece hachurado." O PDF do Subsolo desenha, fora
do subsolo, peças do Térreo: a pedra grande e as 6 lajes da descida (ARQ_CONTRAPISO, o bege a 50%), o deck em L abaixo
da ducha (ARQ_CONTRAPISO) e os 8 degraus da escada que desce ao deck (ARQ_ESCADAS E RAMPAS). Os dois PDFs têm as mesmas
coordenadas e os dois quadros, o mesmo enquadramento (`Quadro.p2q`): essas peças saem da final do Térreo, sem as letras
D das escadas, no nublado do Térreo nas plantas de cima (`entorno_esmaecido.NUBLADO`: desfoque leve, 80% da saturação,
70% de branco), recortadas pelo contorno delas no PDF do Subsolo. A escada da ducha e o deck da ducha são do Subsolo e
ficam como estão; o resto do lote continua na hachura.

2. A conferência apresentada com o Térreo nevoado (OK do usuário: "altere"):
   - os rótulos DEPÓSITO, ACADEMIA e SAUNA no meio do piso livre (`rotulos_centro_sb`), pela regra dos rótulos
     centralizados do Térreo (`revisao_casab_2910.rotulos_centro_tb`);
   - o armário junto ao shaft, na academia, na marcenaria areia com o veio, como o armário da cozinha do Térreo
     (`revisao_casab_2910.marcenaria_tb`).

Uso (uma vez cada; o padrão lê e grava a final do Subsolo):
  python3 subsolo_casab_2910.py [--antes <png>] [--terreo <png>] [--saida <png>]    # 1, sobre a final de f6ea4b6
  python3 subsolo_casab_2910.py --revisao [--antes <png>] [--saida <png>]            # 2, sobre a final de 2cad7fa
"""
import argparse
import re
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casab as F                     # noqa: E402
import final3840_casad as D                     # noqa: E402
import revisao_casab_2910 as RB                 # noqa: E402
from entorno_esmaecido import NUBLADO           # noqa: E402

RENDERS = F.B.CASA_B / "renders"
SUBSOLO_B = RENDERS / "POE642_CasaB_PH_Subsolo_final_rotulos.png"
TERREO_B = RENDERS / "POE642_CasaB_PH_Terreo_final_rotulos.png"

# As peças do Térreo no PDF do Subsolo (o rect de cada preenchimento, em pt) e as do Subsolo que encostam nelas e ficam
# (os 5 degraus da escada da ducha, que avançam 1,7 pt sobre a pedra grande, e o deck da ducha).
NEVOADO_SB = {
    "pecas_pt": [(251.4, 793.6, 517.9, 1064.6), (194.8, 807.8, 251.4, 977.9), (163.5, 830.5, 206.1, 1034.6),
                 (279.8, 901.3, 347.8, 1133.8), (336.5, 929.7, 370.5, 1122.4), (370.5, 912.7, 427.2, 1162.1),
                 (413.0, 975.0, 447.0, 1145.1),
                 (447.0, 963.7, 732.2, 1264.2)]
                + [(x0, 963.7, x1, 1071.4) for x0, x1 in [(728.8, 752.2), (752.2, 775.6), (775.6, 799.0), (799.0, 822.3),
                                                          (822.3, 845.7), (845.7, 869.1), (869.1, 892.5), (892.5, 917.6)]],
    "ficam_pt": [(516.2, 793.6, 534.9, 881.5), (534.9, 793.6, 551.9, 881.5), (551.9, 793.6, 568.9, 881.5),
                 (568.9, 793.6, 585.9, 881.5), (585.9, 793.6, 602.9, 881.5), (602.9, 793.6, 787.2, 963.7)],
    "ss": 4,
    # as letras D do Térreo (F.LETRA_F, cinza 45): o px escuro e neutro, em manchas do tamanho de uma letra
    "letra": {"escuro_max": 120, "neutro_max": 30, "lado_max_px": 30, "folga_px": 2, "raio_px": 3},
}


def _desenhos(Q, rets, tol=0.15):
    ds = []
    for alvo in rets:
        ach = [d for d in Q.desenhos if d.get("fill") is not None
               and max(abs(a - b) for a, b in zip(tuple(d["rect"]), alvo)) <= tol]
        assert ach, f"peça {alvo} não achada no PDF do Subsolo"
        ds.append(ach[0])
    return ds


def _sem_letras(t, caixa, q):
    """O Térreo sem as letras D das escadas: as manchas de px escuros e neutros do tamanho de uma letra, pintadas com o
    entorno (inpaint)."""
    x0, y0, x1, y1 = caixa
    r = t[y0:y1, x0:x1]
    escuro = (r.max(axis=2) < q["escuro_max"]) & (r.max(axis=2).astype(int) - r.min(axis=2) < q["neutro_max"])
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(escuro.astype(np.uint8), np.ones((5, 5), np.uint8)))
    m = np.zeros(escuro.shape, np.uint8)
    for i in range(1, n):
        if st[i, 2] <= q["lado_max_px"] and st[i, 3] <= q["lado_max_px"]:
            m[(lab == i) & escuro] = 255
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * q["folga_px"] + 1,) * 2))
    out = t.copy()
    out[y0:y1, x0:x1] = cv2.inpaint(r, m, q["raio_px"], cv2.INPAINT_TELEA)
    return out, int((m > 0).sum())


def _nublar(t, W):
    n = NUBLADO
    t = cv2.GaussianBlur(t.astype(np.float32), (0, 0), n["desfoque"] * W / 3840)
    cinza = t.mean(axis=2, keepdims=True)
    t = cinza + (t - cinza) * n["saturacao"]
    return 255 - (255 - t) * (1 - n["clarear"])


def nevoado_sb(Q, img, terreo, q=NEVOADO_SB):
    pecas, ficam = _desenhos(Q, q["pecas_pt"]), _desenhos(Q, q["ficam_pt"])
    X0, Y0, X1, Y1 = D._caixa_px(Q, [d["rect"] for d in pecas], folga=(6, 6))
    w, h, ss = X1 - X0, Y1 - Y0, q["ss"]
    m = D._mascara_pdf(Q, pecas, X0, Y0, w, h, ss)
    m[D._mascara_pdf(Q, ficam, X0, Y0, w, h, ss) > 0] = 0
    a = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
    t, n_letra = _sem_letras(terreo, (X0, Y0, X1, Y1), q["letra"])
    nv = _nublar(t[Y0:Y1, X0:X1], Q.W)
    out = img.copy()
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + nv * a), 0, 255).astype(np.uint8)
    print(f"    {len(pecas)} peças do Térreo no PDF do Subsolo, nevoadas ({int((a[..., 0] > 0.5).sum())} px), sem as "
          f"letras D ({n_letra} px); a escada e o deck da ducha ficam")
    return out


# 2a. Os rótulos no meio do piso livre (como no Térreo, `revisao_casab_2910.rotulos_centro_tb`): a rodada de 26/10 de novo
# sobre a etapa sem rótulos (`Subsolo_hachura`, com um espião em `R1.rotulos_ambientes`) dá a etapa `Subsolo_rotulos` sem
# 1 px de diferença, e com ela o texto de cada rótulo. Os de `mover` saem (o fundo sem rótulos, só onde a final ainda é a
# etapa) e voltam a partir do meio do piso livre do recinto (fechado também pelos vidros, menos os objetos); os outros
# ficam e são obstáculo. O banco da sauna (os dois níveis, ARQ_CONTRAPISO, fora das camadas de obstáculo) também:
# o meio da sauna é o do piso acima dele.
ROTULOS_CENTRO_SB = {"mover": ("DEPÓSITO", "ACADEMIA", "SAUNA"), "folga_px": 1,
                     "obstaculos_pt": [(798.5, 895.7, 965.8, 952.4)]}

# 2b. O armário junto ao shaft (ARQ_LAYOUT HUMANIZAÇÃO, 0,60 x 2,00 m; a diagonal tracejada da DOC_LINHAS é a do armário
# alto), na marcenaria areia do armário da cozinha do Térreo: o veio no comprido, o contorno fino, sem sombra.
MARCENARIA_SB = dict(RB.MARCENARIA_TB, semente=2912,
                     pecas=[("armário junto ao shaft, na academia", [(1481.7, 731.3, 1515.7, 844.7)])])


def rotulos_centro_sb(Q, img, q=ROTULOS_CENTRO_SB):
    import retoque_1pav_casae as R1
    rf = F.ROTULOS_F
    base = cv2.imread(str(F.ETAPAS / "Subsolo_hachura.png"))
    etapa = cv2.imread(str(F.ETAPAS / "Subsolo_rotulos.png"))
    rot = F.B.rotulos_casab(Q.pg, Q.p2q2000) + [r for r in R1.rotulos_pdf(Q.pg) if r[0] == "SHAFT"]
    cap = {}
    orig = R1.rotulos_ambientes

    def espia(im, rot_, p2q, **kw):
        cap["rot"], cap["aj"] = rot_, kw["ajustes"]
        return orig(im, rot_, p2q, **kw)
    R1.rotulos_ambientes = espia
    try:
        refeita = F.rotulos(Q, base.copy(), rot, Q.q["ajustes"], granito=F.A.granito(base, Q.q.get("granito_lum_max", 125)))
    finally:
        R1.rotulos_ambientes = orig
    assert not (refeita != etapa).any(), "a rodada de 26/10 não bate mais com a etapa: os textos antigos não são conhecidos"
    esc = Q.W / 2000
    granito = F.A.granito(base, Q.q.get("granito_lum_max", 125))
    mascaras = []
    for r1, aj in zip(cap["rot"], cap["aj"]):
        so = orig(base.copy(), [r1], Q.p2q, escala_desvio=esc, granito=granito, ajustes=[aj],
                  cor_granito=R1.ROTULOS["branco"], halo=None)
        mascaras.append(np.abs(so.astype(np.int16) - base.astype(np.int16)).max(axis=2) > 0)
    busca = [Q.p2q(r[2][0], r[2][1]) for r in cap["rot"]]
    amb = F.ambientes_rotulos(Q, busca, todas=True)
    obst = Q.preencher(lambda d: d.get("layer") in rf["obstaculos"], ss=2, fs=True) > 0.05
    tr = np.zeros(obst.shape, np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in rf["obstaculos"] and d["type"] == "s":
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c))], False, 1, 2)
    obst |= tr.astype(bool)
    for r in q["obstaculos_pt"]:
        x0_, y0_, x1_, y1_ = F.ret_q(Q, r)
        obst[y0_:y1_ + 1, x0_:x1_ + 1] = True
    igual = (img == etapa).all(axis=2)
    out = img.copy()
    mover, pontos, obst_pt, n_px = [], {}, list(q["obstaculos_pt"]), 0
    for i, (r1, m) in enumerate(zip(cap["rot"], mascaras)):
        ys, xs = np.nonzero(m)
        if r1[0] not in q["mover"]:
            a, b = Q.q2p(xs.min() - 4, ys.min() - 4), Q.q2p(xs.max() + 4, ys.max() + 4)
            obst_pt.append((a[0], a[1], b[0], b[1]))
            continue
        md = cv2.dilate(m.astype(np.uint8), np.ones((2 * q["folga_px"] + 1,) * 2, np.uint8)) > 0
        sai = md & igual
        out[sai] = base[sai]
        n_px += int(sai.sum())
        reg = amb == i + 1
        livre = reg & ~obst
        ry, rx = np.nonzero(livre if livre.sum() > 0.05 * reg.sum() else reg)
        cx, cy = rx.mean(), ry.mean()
        if not reg[int(round(cy)), int(round(cx))]:
            ry, rx = np.nonzero(reg)
            j = int(np.argmin((rx - cx) ** 2 + (ry - cy) ** 2))
            cx, cy = rx[j], ry[j]
        area = [float(m_.group(1).replace(",", ".")) for t_ in r1[1] for m_ in [re.search(r"A:\s*([\d,]+)", t_[0])] if m_]
        print(f"      {r1[0]}: o texto em ({xs.mean():.0f}, {ys.mean():.0f}) px, o meio do piso livre em ({cx:.0f}, "
              f"{cy:.0f}) px; o recinto com {reg.sum() / Q.px_m ** 2:.2f} m² (o rótulo diz {area[0] if area else '?'})")
        pontos[(r1[0], round(r1[2][0]), round(r1[2][1]))] = Q.q2p(cx, cy)
        mover.append(r1)
    obst0 = rf.get("obstaculos_pt", {})
    F.ROTULOS_F = dict(rf, pontos=dict(rf["pontos"], **{Q.chave: pontos}),
                       obstaculos_pt=dict(obst0, **{Q.chave: list(obst0.get(Q.chave, ())) + obst_pt}))
    nomes = {r[0] for r in mover}
    try:
        out = F.rotulos(Q, out, [r for r in rot if r[0] in nomes], [a for a in Q.q["ajustes"] if a[0] in nomes],
                        granito=F.A.granito(out, Q.q.get("granito_lum_max", 125)))
    finally:
        F.ROTULOS_F = rf
    print(f"    rótulos: {', '.join(r[0] for r in mover)} no meio do piso livre (o texto antigo saiu: {n_px} px); "
          f"{len(cap['rot']) - len(mover)} ficam")
    return out


def revisao_sb(Q, img):
    return rotulos_centro_sb(Q, RB.marcenaria_tb(Q, img, MARCENARIA_SB))


# 3. Os pedidos de 29/10 vendo o Subsolo depois da conferência (usuário, com os recortes):
# 3a. "remova a linha atrás da porta. parece que tem outra porta" (BH sauna): entre a folha aberta (ARQ_PAREDE,
# 1062,2-1107,5 x 809,2-811,5 pt) e a face da parede de cima, o traço claro de uma folha antiga da base (y 607-612 px), que
# já vinha das etapas do motor. Sai com o travertino de logo abaixo da folha (os estratos são deitados: `dy` px).
LINHA_PORTA_BHS_SB = {"px": (1250, 607, 1297, 613), "dy": 10}

# 3b. "corrija a parede atrás da porta. tem um dente que não existe. a parede é retilínea" (depósito): sobre a folha aberta
# da porta do depósito (1322,9-1362,6 pt), a face da parede de cima subia ~3 px (o revestimento do PDF, de 1,7 pt, saía
# como piso) e, no vão da porta, o canto da parede saía em branco. A face volta reta, na linha da parede ao lado
# (`modelo_x`: as linhas do fim da parede, a face escura e o fio, copiadas coluna a coluna). Embaixo do vão, o começo da
# parede de baixo (585,3 pt, 378 px) também saía em branco até 383 px: vira a parede (`pe_px`, a linha `pe_modelo_y`).
PAREDE_DEPOSITO_SB = {"px": (1511, 1565), "linhas": (325, 330), "modelo_x": 1570, "pe_px": (1511, 378, 1521, 383),
                      "pe_modelo_y": 386}

# 3c. "representa a soleira. não pode ficar no tom branco." (depósito): o vão da porta na parede entre a circulação e o
# depósito (1314,4-1322,9 x 539,9-585,3 pt) não entrou na busca dos vãos brancos (o branco do vão emenda no branco da
# circulação no PDF, como o Louceiro 2 da Casa C) e ficou no branco. Agora a soleira de Bege Bahia com as faces em cinza
# fino (R13) e, por cima, os batentes do PDF (as barras de cima e de baixo e as peças dos lados).
SOLEIRA_DEPOSITO_SB = {"nome": "do depósito (soleira)", "soleira": (1314.4, 539.9, 1322.9, 585.3),
                       "batentes": [(1314.4, 541.3, 1322.9, 543.3), (1314.4, 581.9, 1322.9, 583.9),
                                    (1313.3, 538.2, 1314.4, 542.2), (1322.9, 538.8, 1324.1, 542.8),
                                    (1313.3, 583.0, 1314.4, 587.0), (1322.9, 582.4, 1324.1, 586.4)],
                       "folhas": [], "montante_pt": 0.6}

# 3d. "represente melhor essas folhas de vidro e corrija imperfeições" (o vidro fixo em L da sauna): o vão da parede saía
# em faixas escuras e com um resto claro no canto de cima. Agora como o vidro fixo em L da sauna do Subsolo da Casa A
# (aprovado em 26/10, `final3840_casaa.portas_vidro`): o vão da parede (os dois braços do PDF, o bege a 50% da ARQ_PAREDE)
# em Bege Bahia sem as faces, o caixilho branco entre as faces escuras com a linha do vidro no meio, nos dois braços, e os
# montantes do canto e das pontas, até as paredes.
VIDRO_SAUNA_SB = {"nome": "da sauna (vidro fixo)",
                  "soleiras": [(787.2, 793.6, 888.1, 802.1), (787.2, 802.1, 798.5, 895.7)], "faces": False,
                  "batentes": [],
                  "postes": [(791.7, 798.2, 796.6, 803.0), (886.1, 798.2, 888.1, 801.0), (791.7, 895.4, 794.6, 897.4)],
                  "folhas": [((796.6, 798.2, 886.1, 801.0), "x"), ((791.7, 803.0, 794.6, 895.4), "y")],
                  "montante_pt": 0.0, "linhas": {"cor": (48, 50, 52), "faces_px": 0.9, "meio_px": 0.7, "largura_min_px": 4.8}}

# Depois, com o recorte do canto de cima do vidro (usuário: "remova esse \"arco\" no piso"): no canto de fora do vão
# (787,2 x 793,6 pt), um traço escuro da base em L, de canto redondo: no topo do vão (y 596 px) e descendo pela borda do
# deck (x 954 px) até 606 px. Sai pelo entorno (inpaint): o Bege Bahia da garagem e do vão, a madeira do deck.
ARCO_VAO_SAUNA_SB = {"px": [(955, 596, 967, 597), (955, 597, 957, 598), (954, 597, 955, 607)], "raio_px": 2}

# 3e. "represente melhor esses degraus da sauna com o efeito sombra de cada um deles em forma de bancos": os dois níveis
# (o da frente, 895,7-924,0 pt, e o de trás, junto à parede, 926,3-952,4; o espelho entre eles, 924,0-926,3) refeitos no
# mesmo travertino bruto (`F.bancos_sauna`, a mesma textura), cada um mais claro que o de baixo (`nivel`), com a sombra de
# contato de cada banco no de baixo (no piso, à frente do banco da frente; no banco da frente, à frente do de trás:
# `sombra`), o espelho na sombra (`espelho`), o fio escuro do pé de cada banco e o brilho fino da quina (`quina`).
BANCOS_SAUNA_SB = {"nivel": (1.0, 1.035, 1.075), "sombra": {"larg_m": 0.07, "forca": 0.30}, "espelho": 0.80,
                   "pe": {"cor": (112, 110, 104), "larg_px": 0.8, "forca": 0.55}, "quina": {"larg_px": 0.8, "forca": 0.10},
                   "parede_max": 110}

# 3f. "padronize como do terreo. e represente melhor o rótulo" (o elevador): a cabine era a do Subsolo de 26/10 (a
# referência das Casas C, D e E), mais escura, com o painel cinza, sem os corrimãos dos lados nem as folhas. O PDF do
# Subsolo tem a caixa do elevador nas mesmas coordenadas da do Térreo (INS_INSTALAÇÕES HIDRÁULICAS, 1527,1-1606,4 x
# 766,6-842,4 pt) e a porta no mesmo vão: a cabine de aço do Térreo (`revisao_casab_2910.ELEVADOR_TB`), a mesma. O
# rótulo ELEVADOR volta no meio da cabine, no corpo e no preto dos rótulos (`rotulos_centro_sb`).


def linha_porta_bhs_sb(img, q=LINHA_PORTA_BHS_SB):
    x0, y0, x1, y1 = q["px"]
    out = img.copy()
    out[y0:y1, x0:x1] = img[y0 + q["dy"]:y1 + q["dy"], x0:x1]
    print(f"    BH sauna: o traço atrás da folha sai ({x1 - x0}x{y1 - y0} px), com o travertino de {q['dy']} px abaixo")
    return out


def parede_deposito_sb(img, q=PAREDE_DEPOSITO_SB):
    (x0, x1), (y0, y1), xm = q["px"], q["linhas"], q["modelo_x"]
    out = img.copy()
    out[y0:y1, x0:x1] = img[y0:y1, xm:xm + 1]
    a, b, c, d = q["pe_px"]
    out[b:d, a:c] = img[q["pe_modelo_y"], a:c][None]
    print(f"    depósito: a face da parede de cima reta sobre a porta ({x1 - x0} px, as linhas {y0}-{y1 - 1} da parede ao lado)")
    return out


def portas_vidro_sb(Q, img, portas):
    import final3840_casaa as FA
    pv = FA.PORTAS_VIDRO
    FA.PORTAS_VIDRO = dict(pv, portas=portas)
    try:
        return FA.portas_vidro(Q, np.ascontiguousarray(img.copy()))
    finally:
        FA.PORTAS_VIDRO = pv


def arco_vao_sauna_sb(img, q=ARCO_VAO_SAUNA_SB):
    m = np.zeros(img.shape[:2], np.uint8)
    for x0, y0, x1, y1 in q["px"]:
        m[y0:y1, x0:x1] = 255
    print(f"    sauna: o traço em L no canto de fora do vão sai ({int((m > 0).sum())} px, pelo entorno)")
    return cv2.inpaint(img, m, q["raio_px"], cv2.INPAINT_TELEA)


def bancos_sauna_sb(Q, img, q=BANCOS_SAUNA_SB):
    import final3840_casaa as FA
    from retoque_terreo_casae import linha_aa
    s, b = F.SAUNA_F, F.SAUNA_F[Q.chave]
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_CONTRAPISO" and d.get("fill") and
                    all(abs(v - w) < 0.5 for v, w in zip((d["rect"].x0, d["rect"].y0, d["rect"].x1, d["rect"].y1),
                                                         b["pt"])), fs=False)
    x0, y0, x1, y1 = F.ret_q(Q, b["pt"])
    x0, y0, x1, y1 = x0 - 2, y0 - 2, x1 + 2, y1 + 2
    sm = q["sombra"]["larg_m"] * Q.px_m
    ys0 = int(y0 - 4 * sm)                                     # a sombra no piso, à frente do banco da frente
    px0, py0, px1, py1 = F.ret_q(Q, b["piso_pt"])
    cor = np.median(img[py0:py1, px0:px1].reshape(-1, 3).astype(np.float32), axis=0)
    T = cor * FA.travertino_bruto(Q, y1 - y0, x1 - x0, s["semente"], forca=s["veio"], **FA.TRAVERTINO["bancada"])[..., None]
    yf = Q.p2q(b["pt"][0], b["pt"][1])[1]                      # a frente do banco da frente
    ye0 = Q.p2q(b["pt"][0], b["espelho_pt"][0])[1]             # o espelho
    ye1 = Q.p2q(b["pt"][0], b["espelho_pt"][1])[1]
    yy = np.arange(ys0, y1, dtype=np.float32)[:, None]
    n0, n1, n2 = q["nivel"]
    nivel = np.where(yy >= ye1, n2, np.where(yy >= ye0, n1 * q["espelho"], np.where(yy >= yf, n1, n0)))
    f = q["sombra"]["forca"]
    sombra = np.where(yy < yf, 1 - f * np.exp(-(yf - yy) / sm), 1.0) * \
        np.where((yy >= yf) & (yy < ye0), 1 - f * np.exp(-(ye0 - yy) / sm), 1.0)
    out = img.astype(np.float32)
    # o banco (no travertino bruto) e, no piso à frente dele, só a sombra; nada nas paredes em volta
    reg = out[ys0:y1, x0:x1]
    al = a[ys0:y1, x0:x1, None]
    parede = (reg.max(axis=2, keepdims=True) < q["parede_max"])
    novo_banco = np.concatenate([np.zeros((y0 - ys0, x1 - x0, 3), np.float32), T]) * nivel[..., None]
    xa, xb = Q.p2q(b["pt"][0], 0)[0] - x0, Q.p2q(b["pt"][2], 0)[0] - x0
    X = np.arange(x1 - x0, dtype=np.float32)[None, :]
    no_x = ((X >= xa) & (X <= xb))[..., None]
    piso_sombra = reg * sombra[..., None]
    reg[:] = np.where(parede, reg, np.where(no_x & (yy[..., None] < yf), piso_sombra, reg))
    reg[:] = np.where(parede, reg, reg * (1 - al) + novo_banco * sombra[..., None] * al)
    # o fio do pé de cada banco (a frente de cada nível) e o brilho fino da quina, logo atrás dele
    h, w = reg.shape[:2]
    for yl in (yf, ye1):
        ln = linha_aa((h, w), [(xa, yl - ys0), (xb, yl - ys0)], q["pe"]["larg_px"])[..., None] * q["pe"]["forca"] * al
        reg[:] = reg * (1 - ln) + np.float32(q["pe"]["cor"]) * ln
        lq = linha_aa((h, w), [(xa, yl - ys0 + 1.2), (xb, yl - ys0 + 1.2)], q["quina"]["larg_px"])[..., None] * al
        reg[:] = reg * (1 + q["quina"]["forca"] * lq)
    print(f"    sauna: os dois bancos em níveis (piso, frente, trás: {n0}, {n1}, {n2}), com a sombra de contato de cada um "
          f"no de baixo ({q['sombra']['larg_m'] * 100:.0f} cm), o espelho na sombra, o pé e a quina")
    return np.clip(out, 0, 255).astype(np.uint8)


def elevador_sb(Q, img):
    import final3840_casaa as FA
    guarda = FA.ELEVADOR
    FA.ELEVADOR = dict(FA.ELEVADOR, **RB.ELEVADOR_TB)
    try:
        out = FA.elevador(Q, np.ascontiguousarray(img.copy()))
    finally:
        FA.ELEVADOR = guarda
    print("    elevador: a cabine de aço do Térreo (o mesmo desenho, nas mesmas coordenadas do PDF)")
    return out


def pedidos_sb(Q, img):
    out = linha_porta_bhs_sb(img)
    out = parede_deposito_sb(out)
    out = portas_vidro_sb(Q, out, [SOLEIRA_DEPOSITO_SB, VIDRO_SAUNA_SB])
    out = arco_vao_sauna_sb(out)
    out = bancos_sauna_sb(Q, out)
    out = elevador_sb(Q, out)
    return rotulos_centro_sb(Q, out, dict(ROTULOS_CENTRO_SB, mover=("ELEVADOR",), obstaculos_pt=[]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--revisao", action="store_true", help="os 2 itens da conferência (sobre a final de 2cad7fa)")
    ap.add_argument("--pedidos", action="store_true", help="os pedidos vendo o Subsolo (sobre a final de 29ce96b)")
    ap.add_argument("--antes", default=str(SUBSOLO_B))
    ap.add_argument("--terreo", default=str(TERREO_B))
    ap.add_argument("--saida", default=str(SUBSOLO_B))
    a = ap.parse_args()
    Q = F.Quadro("Subsolo")
    img = cv2.imread(a.antes)
    assert img.shape == (Q.H, Q.W, 3)
    if a.pedidos:
        out = pedidos_sb(Q, img)
    elif a.revisao:
        out = revisao_sb(Q, img)
    else:
        terreo = cv2.imread(a.terreo)
        assert terreo.shape == img.shape
        out = nevoado_sb(Q, img, terreo)
    cv2.imwrite(a.saida, out)
    print("ok:", a.saida)

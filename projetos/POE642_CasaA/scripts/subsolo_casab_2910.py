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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--revisao", action="store_true", help="os 2 itens da conferência (sobre a final de 2cad7fa)")
    ap.add_argument("--antes", default=str(SUBSOLO_B))
    ap.add_argument("--terreo", default=str(TERREO_B))
    ap.add_argument("--saida", default=str(SUBSOLO_B))
    a = ap.parse_args()
    Q = F.Quadro("Subsolo")
    img = cv2.imread(a.antes)
    assert img.shape == (Q.H, Q.W, 3)
    if a.revisao:
        out = revisao_sb(Q, img)
    else:
        terreo = cv2.imread(a.terreo)
        assert terreo.shape == img.shape
        out = nevoado_sb(Q, img, terreo)
    cv2.imwrite(a.saida, out)
    print("ok:", a.saida)

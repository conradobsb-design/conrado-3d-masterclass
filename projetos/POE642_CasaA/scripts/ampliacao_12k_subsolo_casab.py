"""O JPG em 12K do Subsolo da Casa B (usuário, 12/11/26: "gere os 12K do subsolo da casa B"; regras de 10/11: "GERE A
IMAGEM EM 12K JPG. ISSO É REGRA PARA TODAS AS PLANTAS" e as duas letras, A na Inter e B na Kalam).

O roteiro dos 12K da Casa A (`ampliacao_12k_terreo_casaa.py`, de onde vêm o recorte, o alinhamento e o desenho dos
rótulos em 12K, e `ampliacao_12k_1pav_casaa.py`, de onde vem a correção pelas peças):
  1. `preparar --passos <pasta>`: a entrada da IA sem textos. Parte do passo `academia` de
     `pedidos_subsolo_casab_1211.py` (a final antes dos rótulos dos ambientes); a seta e o "SOBE PARA O / JARDIM" saem
     (o trecho da escada vem do passo `ralo` só com o S tirado); o ELEVADOR sai pela conta do alfa
     (`ampliacao_a3_casaa.tirar`, o desenho achado na final, correlação 0,99); o X do shaft sai (o vão no fundo claro).
     Os rótulos (os 8 de `POE642_CasaB_PH_Subsolo_rotulos_1211.json`, gravados pelo passo `rotulos`, e o ELEVADOR), a
     escada e o shaft vão para os dados, para o 12K. A entrada é o recorte da planta em 16:9 com a margem da A3.
  2. A entrada no Nano Banana Pro (4K, 16:9), com o prompt de ampliação fiel (`PROMPT`).
  3. `corrigir`: da IA ficam só os pisos (Bege Bahia, travertino bruto e vinílico, no que é piso: a cor da base, fora
     das peças do PDF e no tom do piso do lugar); todo o resto da casa (paredes, portas, soleiras, louças, bancadas, os
     bancos da sauna, os aparelhos, a bola, o armário, a escada, o elevador) e o deck da ducha (a IA entortou as
     juntas das tábuas) voltam da entrada ampliada.
  4. A saída corrigida no Topaz (High Fidelity V2), a 12288 de largura.
  5. `montar12k --opcao AB`: a saída do Topaz alinhada à entrada, na A3 deitada (12288 x 8689); os tons da final; o
     fundo fora da planta em branco puro; o X tracejado do shaft; os rótulos, a seta e a descrição da escada
     desenhados direto em 12K (A na Inter, B na Kalam).

  python3 ampliacao_12k_subsolo_casab.py preparar --passos <pasta dos passos de pedidos_subsolo_casab_1211.py>
  python3 ampliacao_12k_subsolo_casab.py diferencas <saída do Nano Banana Pro>
  python3 ampliacao_12k_subsolo_casab.py corrigir <saída do Nano Banana Pro> <corrigida>
  python3 ampliacao_12k_subsolo_casab.py montar12k <saída do Topaz> [--opcao AB]
"""

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                    # noqa: E402
import final3840_casab as F                     # noqa: E402
import ampliacao_a3_casaa as AM                 # noqa: E402
import ampliacao_12k_terreo_casaa as Z          # noqa: E402
import pedidos_subsolo_casab_1211 as PS         # noqa: E402
import retoque_1pav_casae as R1                 # noqa: E402

CASA_B = AQUI.parents[1] / "POE642_CasaB"
R = CASA_B / "renders"
FINAL = PS.FINAL
ENTRADA_IA = R / "POE642_CasaB_PH_Subsolo_12K_entrada_ia.png"
DADOS = R / "POE642_CasaB_PH_Subsolo_12K_dados.json"
SAIDA = CASA_B / "entrega" / "POE642_CasaB_PH_Subsolo_12K_opcao_{opcao}.jpg"

# o ELEVADOR (o rótulo da cabine, do motor; achado na final: corpo e desvio do desenho de `rotulos_ambientes` que casa
# com o escuro dela, correlação 0,988)
ELEVADOR = {"nome": "ELEVADOR", "opc": {"corpo": 1.3}, "desvio": [2.0, 8.0], "cor": [20, 20, 20]}
# o trecho da escada (px da final): vem do passo `ralo` só com o S tirado (a seta e a descrição saem)
ESCADA_PX = (625, 620, 775, 735)

PROMPT = ("High-fidelity 4K upscale of the reference image, which is a top-down architectural humanized floor plan of a "
          "basement (orthographic, viewed straight from above). Reproduce the reference EXACTLY: identical composition, "
          "framing, layout, scale and position of every element; same dark gray walls and thin dark perimeter line, "
          "the round pillar, door leaves and thresholds, glass partitions, the stair steps, the wooden shower deck "
          "with the shower, the sauna with its two tiered benches, the bathroom fixtures and washbasins, the gym "
          "equipment (two treadmills, two exercise bikes, the weight bench), the pilates ball in its wall holder, the "
          "cabinet, the elevator, the shaft and the pure white background. Do not add, remove, move, rotate, resize "
          "or redesign anything. Do not add any text, labels, numbers, arrows, triangles, symbols, dashed lines, cars "
          "or people. Only increase resolution and detail: crisp straight wall edges and lines, sharp object edges, "
          "and fine realistic material textures matching the existing colors and tones exactly: smooth light beige "
          "marble (Bege Bahia) with soft low-contrast veining in the garage and corridors, light raw travertine with "
          "fine horizontal veining in the sauna, the sauna bathroom and the storage room, warm wood vinyl planks "
          "(thin crisp joints, fine wood grain) in the gym, and warm wood deck boards (same direction and tone). "
          "Keep colors, brightness and contrast the same as the reference. Clean, photographic architectural "
          "presentation quality, no artifacts, no noise.")

# os pisos (a cor na base chapada) onde a IA fica; o resto da casa volta da entrada (`corrigir`)
PISOS_12K = {"pisos": ((232, 232, 232), (202, 217, 220), (201, 217, 220), (124, 162, 200), (99, 136, 174),
                       (76, 106, 138)),
             "desvio": 30, "croma": 0.035, "r": (0.55, 1.2), "pdf_folga_px": 2, "borda_px": 2,
             # os bancos da sauna (ARQ_CONTRAPISO, na cor do travertino): voltam da entrada, com os níveis e os fios
             "pecas_pt": [F.SAUNA_F["Subsolo"]["pt"]]}
# `tom_sigma_px`: os tons da IA casados com os da entrada (a baixa frequência, px da entrada) antes de juntar, para não
# ficar halo junto às peças que voltam da entrada. Ambiente por ambiente (os pisos ligados, na escala da entrada): se a
# cor da IA (desfocada `cor_sigma_px`) foge da entrada mais que `sala_max` na mediana (ΔE no Lab), o piso do ambiente
# todo volta da entrada (na saída de 12/11, job 85520e81: a IA acinzentou o BH serviço, escureceu o BH sauna e a sauna
# e pôs bancos de madeira em L nela; a garagem e a academia ficaram perto, ΔE 6 e 13). Nos que ficam, onde a estrutura
# (o passa-banda) foge mais que `estrutura`, a IA inventou algo: volta da entrada (com `folga_px`).
# `da_entrada_px` (px da final): pisos que voltam sempre da entrada, passem ou não no ΔE. O deck da ducha (usuário,
# 12/11: "as linhas das tábuas de madeira não podem sair tortas"): a IA redesenhou as juntas, onduladas e com outra
# paginação, no mesmo tom (ΔE baixo); na entrada, as tábuas retas da final.
CORRECAO = {"nitidez": (0.6, 1.2), "borda_px": 2.0, "tom_sigma_px": 2.5, "cor_sigma_px": 2.0, "sala_max": 15.0,
            "sala_min_px": 300, "estrutura": 8.0, "folga_px": 3,
            "da_entrada_px": {"deck da ducha": (760, 597, 960, 773)}}
CONFERENCIA = {"garagem_escada": (630, 240, 1380, 790), "sauna_bh_sauna": (950, 575, 1350, 785),
               "academia": (1360, 440, 1835, 785), "bh_servico_deposito": (1360, 300, 1840, 540)}


def quadro():
    with contextlib.redirect_stdout(io.StringIO()):
        return F.Quadro("Subsolo")


def rotulos_b(Q):
    """Os rótulos do PDF do Subsolo da Casa B (os textos trocados como no motor), no lugar dos da Casa A em
    `ampliacao_a3_casaa._rotulos` (o desenho em 12K da Casa A procura o rótulo por ali)."""
    return F.textos_rotulos(F.B.rotulos_casab(Q.pg, Q.p2q2000) + [r for r in R1.rotulos_pdf(Q.pg) if r[0] == "SHAFT"])


def _usar_rotulos_b(Q):
    rot = rotulos_b(Q)
    AM._rotulos = lambda Q_: rot
    return rot


def _escada_dados():
    """A seta (o triângulo) e as linhas da descrição, em px da final, como `pedidos_subsolo_casab_1211.escada_sb` as
    desenha: [(texto, x da origem, y da base, x do meio)], o corpo e a cor."""
    from PIL import ImageFont
    from rodape_entrega import FONTES
    e, q = FA.ESCADA_A, PS.ESCADA_SB
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), e["corpo_px"] * 4)
    larg = [fonte.getlength(t) / 4 for t in q["texto"]]
    cx = min(q["centro_x"], q["x_max"] - max(larg) / 2)
    linhas = [[t, cx - lw / 2, q["base_y"] + i * q["entrelinha_px"], cx] for i, (t, lw) in enumerate(zip(q["texto"], larg))]
    pts = np.float32(q["triangulo"])
    letra = ({"texto": q["letra"], "cx": float(pts[:, 0].min() + pts[:, 0].max()) / 2,
              "topo": float(pts[:, 1].max()) + q["letra_folga_px"]} if q.get("letra") else None)
    return {"tri": [list(map(float, p)) for p in q["triangulo"]], "cor_seta": list(q["cor_seta"]), "linhas": linhas,
            "corpo": e["corpo_px"], "cor": list(e["cor_texto"]), "fonte": e["fonte"], "letra": letra}


# ----------------------------------------------------------------------------------------------------------------------
def preparar(passos):
    Q = quadro()
    _usar_rotulos_b(Q)
    final = cv2.imread(str(FINAL))
    base = cv2.imread(str(Path(passos) / "passo_academia.png"))
    ralo = cv2.imread(str(Path(passos) / "passo_ralo.png"))
    # a escada: o passo `ralo` só com o S tirado (o mesmo de `escada_sb`)
    q = PS.ESCADA_SB
    x0, y0, x1, y1 = q["s_px"]
    reg = ralo[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    s_ = cv2.dilate((reg < 150).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    ys, xs = np.nonzero(s_)
    sem_s = ralo.copy()
    sem_s[ys + y0, xs + x0] = ralo[ys + y0 + q["desloc_s"], xs + x0]
    a0, b0, a1, b1 = ESCADA_PX
    base[b0:b1, a0:a1] = sem_s[b0:b1, a0:a1]
    # o shaft: o vão no fundo claro, sem o X (volta em 12K)
    import um_pav_casaa_1111 as U
    sx0, sy0, sx1, sy1 = PS.SHAFT_SB["px"]
    base[sy0:sy1, sx0:sx1] = np.uint8(U.SHAFTS_1P["fundo"])
    # o ELEVADOR: pela conta do alfa
    rots = json.loads(PS.ROTULOS_JSON.read_text())
    r_el = [r for r in rotulos_b(Q) if r[0] == "ELEVADOR"][0]
    el = dict(ELEVADOR, pdf=[float(v) for v in r_el[2]])
    a_el = Z.alfa_rotulo(Q, el, final.shape[:2])
    limpa = AM.tirar(base, [(a_el, tuple(el["cor"]))], Z.G12["cheio"])
    rots = rots + [el]
    rc = Z.recortes(final)
    X0, Wc, Yia, Hia = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"]
    cv2.imwrite(str(ENTRADA_IA), limpa[Yia:Yia + Hia, X0:X0 + Wc])
    esc = _escada_dados()
    DADOS.write_text(json.dumps({"rotulos": rots, "escada": esc, "shaft_px": list(PS.SHAFT_SB["px"]), "recortes": rc},
                                ensure_ascii=False, indent=1) + "\n")
    # conferência: os rótulos desenhados de volta sobre a limpa, contra a final
    camadas = [(Z.alfa_rotulo(Q, b, final.shape[:2]), tuple(b["cor"])) for b in rots]
    volta = AM.pintar(limpa, camadas)
    caixa = np.zeros(final.shape[:2], bool)
    for a, _ in camadas:
        caixa |= cv2.dilate((a > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    dif = np.abs(volta.astype(np.int16) - final.astype(np.int16)).max(axis=2)
    print(f"[Subsolo da Casa B] {len(rots)} rótulos ({', '.join(b['nome'] for b in rots)}); o redesenho contra a final, "
          f"nas caixas dos rótulos: {int(((dif > 24) & caixa).sum())} px com mais de 24 de diferença")
    x0, y0, x1, y1 = rc["planta"]
    cv2.imwrite(str(R / "POE642_CasaB_PH_Subsolo_12K_sem_textos.jpg"),
                np.vstack([final[y0:y1, x0:x1], limpa[y0:y1, x0:x1]]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    a planta {x0},{y0} - {x1},{y1}; o recorte da IA {X0},{Yia} {Wc}x{Hia} (16:9)")
    print(f"    {ENTRADA_IA}")


# ----------------------------------------------------------------------------------------------------------------------
def diferencas(saida_ia):
    Z.ENTRADA_IA, Z.DADOS, Z.R, Z.PAV = ENTRADA_IA, DADOS, R, "Subsolo"
    m = Z.diferencas(saida_ia)
    viz = Z.R / "POE642_CasaA_PH_Subsolo_12K_diferencas.jpg"
    if viz.exists():
        viz.rename(R / "POE642_CasaB_PH_Subsolo_12K_diferencas.jpg")
    return m


def mascara_pecas(Q):
    """Dentro da casa, o que não é piso (a mesma conta de `ampliacao_12k_1pav_casaa._mascara_1p`)."""
    import um_pav_casaa_1111 as U
    q = PISOS_12K
    img = cv2.imread(str(FINAL))
    piso = np.zeros(img.shape[:2], bool)
    pdf = U._objetos_pdf(Q, U.PISOS_1111E["camadas_pdf"], q["pdf_folga_px"])
    par = U.dilatar(FA.paredes_pdf(Q) > 0.3, 1)
    I = img.astype(np.float32)
    n = I / np.maximum(I.sum(axis=2, keepdims=True), 1)
    extra = np.zeros(img.shape[:2], bool)                 # a faixa e a circulação do BH serviço (o Bege da garagem)
    x0, y0, x1, y1 = PS.PISOS_SB["faixa_px"]
    extra[y0:y1, x0:x1] = True
    for x0, y0, x1, y1 in PS.PISOS_SB["bege_incluir_px"]:
        extra[y0:y1, x0:x1] = True
    for cor in q["pisos"]:
        mat = (Q.chapada == cor).all(axis=2)
        if cor == (232, 232, 232):
            mat |= extra
        mat &= ~par
        L = F.luz_robusta(img, mat & ~pdf, 0.5 * Q.px_m, desvio=q["desvio"])
        nL = L / np.maximum(L.sum(axis=2, keepdims=True), 1)
        r = I.mean(axis=2) / np.maximum(L.mean(axis=2), 1)
        piso |= mat & ~pdf & (np.abs(n - nL).max(axis=2) < q["croma"]) & (r > q["r"][0]) & (r < q["r"][1])
    for p in q["pecas_pt"]:
        a, b, c, d = F.ret_q(Q, p)
        piso[b - 2:d + 3, a - 2:c + 3] = False
    piso = cv2.morphologyEx(piso.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    piso = cv2.erode(piso, np.ones((2 * q["borda_px"] + 1,) * 2, np.uint8)) > 0
    casa = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < 254
    casa = cv2.dilate(casa.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    return casa & ~piso


def corrigir_ia(saida_ia, destino):
    q = CORRECAO
    ia = cv2.imread(str(saida_ia))
    entrada = cv2.imread(str(ENTRADA_IA))
    rc = json.loads(DADOS.read_text())["recortes"]
    X0, Yia = rc["X0"], rc["Yia"]
    Hi, Wi = ia.shape[:2]
    Hc, Wc = entrada.shape[:2]
    M = Z._alinhar(ia, entrada)
    Tm = (np.diag([Wi / Wc, Hi / Hc, 1.0]) @ np.vstack([M.astype(np.float64), [0, 0, 1]]))[:2]
    ref = cv2.warpAffine(entrada, Tm, (Wi, Hi), flags=cv2.INTER_LANCZOS4, borderValue=(255, 255, 255)).astype(np.float32)
    f_, r_ = q["nitidez"]
    ref = np.clip(ref + f_ * (ref - cv2.GaussianBlur(ref, (0, 0), r_)), 0, 255)
    # os tons da IA casados com os da entrada (a baixa frequência)
    k_ = Wi / Wc
    sg = q["tom_sigma_px"] * k_
    iaf = ia.astype(np.float32)
    iaf = np.clip(iaf + cv2.GaussianBlur(ref, (0, 0), sg) - cv2.GaussianBlur(iaf, (0, 0), sg), 0, 255)
    # onde a IA foge da entrada (na escala da entrada): o ambiente todo pela cor, o trecho pela estrutura
    peq = cv2.warpAffine(ia, Tm, (Wc, Hc), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP, borderValue=(255, 255, 255))
    sd = q["cor_sigma_px"]
    lab_i = cv2.GaussianBlur(cv2.cvtColor(peq, cv2.COLOR_BGR2LAB).astype(np.float32), (0, 0), sd)
    lab_e = cv2.GaussianBlur(cv2.cvtColor(entrada, cv2.COLOR_BGR2LAB).astype(np.float32), (0, 0), sd)
    de = np.sqrt(((lab_i - lab_e) ** 2).sum(axis=2))
    Q = quadro()
    pec = mascara_pecas(Q)[Yia:Yia + Hc, X0:X0 + Wc]
    piso = (cv2.cvtColor(entrada, cv2.COLOR_BGR2GRAY) < 250) & ~pec
    n, lab, st, _ = cv2.connectedComponentsWithStats(piso.astype(np.uint8), 4)
    fora = np.zeros(piso.shape, bool)
    salas = []
    for i in range(1, n):
        mi = lab == i
        med = float(np.median(de[mi]))
        if st[i, cv2.CC_STAT_AREA] < q["sala_min_px"] or med > q["sala_max"]:
            fora |= mi
        if st[i, cv2.CC_STAT_AREA] >= q["sala_min_px"]:
            salas.append((int(st[i, 0]) + X0, int(st[i, 1]) + Yia, int(st[i, cv2.CC_STAT_AREA]), round(med, 1),
                          med <= q["sala_max"]))
    for nome, (x0, y0, x1, y1) in q["da_entrada_px"].items():
        cx = np.zeros(piso.shape, bool)
        cx[max(y0 - Yia, 0):y1 - Yia, max(x0 - X0, 0):x1 - X0] = True
        fora |= cx & piso
        print(f"      {nome}: da entrada ({int((cx & piso).sum())} px)")

    def banda(x):
        g = cv2.cvtColor(x, cv2.COLOR_BGR2LAB).astype(np.float32)
        return cv2.GaussianBlur(g, (0, 0), 1.0) - cv2.GaussianBlur(g, (0, 0), 6.0)
    bd = cv2.GaussianBlur(np.abs(banda(peq) - banda(entrada)).max(axis=2), (0, 0), 3.0) > q["estrutura"]
    kd = 2 * q["folga_px"] + 1
    inv = cv2.dilate((bd & piso & ~fora).astype(np.uint8), np.ones((kd, kd), np.uint8)) > 0
    dv = (fora | inv).astype(np.float32)
    mq = np.maximum(pec.astype(np.float32), dv)
    for x_, y_, a_, med, ok in salas:
        print(f"      piso em ({x_}, {y_}), {a_} px: ΔE mediano {med} -> {'da IA' if ok else 'da entrada'}")
    m = cv2.warpAffine(mq, Tm, (Wi, Hi), flags=cv2.INTER_LINEAR)
    m = cv2.GaussianBlur(m, (0, 0), q["borda_px"] * Wi / Wc / 2.7)[..., None]
    out = np.clip(np.round(iaf * (1 - m) + ref * m), 0, 255).astype(np.uint8)
    cv2.imwrite(str(destino), out)
    print(f"    a saída da IA corrigida: da IA só os pisos (nos tons da entrada), o resto da casa e o que a IA inventou "
          f"no piso ({int(inv.sum())} px) da entrada ({float(mq.mean()):.0%} do recorte): {destino}")


# ----------------------------------------------------------------------------------------------------------------------
def _shaft_12k(out, caixa, s, X0, Ya3):
    """O X tracejado do shaft (o de `pedidos_subsolo_casab_1211.armario_shaft_sb`) direto em 12K."""
    import um_pav_casaa_1111 as U
    q = U.SHAFTS_1P
    x0, y0, x1, y1 = [(v - o) * s for v, o in zip(caixa, (X0, Ya3, X0, Ya3))]
    bx, by = int(x0) - 4, int(y0) - 4
    w, h = int(np.ceil(x1)) + 4 - bx, int(np.ceil(y1)) + 4 - by
    reg = out[by:by + h, bx:bx + w].astype(np.float32)
    cobre = U._cobertura((x0, y0, x1, y1), bx, by, w, h)
    reg = reg * (1 - cobre[..., None]) + np.float32(q["fundo"]) * cobre[..., None]
    ss = 4
    M = np.zeros((h * ss, w * ss), np.uint8)
    r = q["recuo_px"] * s
    traco, vao = q["traco_px"] * s, q["vao_px"] * s
    passo = traco + vao
    for (ax, ay), (bx2, by2) in (((x0 + r, y0 + r), (x1 - r, y1 - r)), ((x1 - r, y0 + r), (x0 + r, y1 - r))):
        cx, cy = (ax + bx2) / 2, (ay + by2) / 2
        L = np.hypot(bx2 - ax, by2 - ay) / 2
        ux, uy = (bx2 - ax) / (2 * L), (by2 - ay) / (2 * L)
        kmax = int(np.ceil(L / passo)) + 1
        for kk in range(-kmax, kmax + 1):
            t0, t1 = max(kk * passo - traco / 2, -L), min(kk * passo + traco / 2, L)
            if t1 - t0 < 0.4 * s:
                continue
            p0 = ((cx + ux * t0 - bx) * ss, (cy + uy * t0 - by) * ss)
            p1 = ((cx + ux * t1 - bx) * ss, (cy + uy * t1 - by) * ss)
            cv2.line(M, tuple(int(round(v)) for v in p0), tuple(int(round(v)) for v in p1), 255,
                     max(1, int(round(q["x_px"] * s * ss))), cv2.LINE_AA)
    al = cv2.resize(M.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * cobre
    reg = reg * (1 - al[..., None]) + np.float32(q["x"]) * al[..., None]
    out[by:by + h, bx:bx + w] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def _escada_12k(out, esc, s, X0, Ya3, opcao, reforco):
    """A seta (o triângulo cheio) e a descrição da escada direto em 12K: A na Inter (a fonte e o corpo da final), B na
    Kalam (a mesma altura das maiúsculas x 1,12, sem passar da largura que a linha tinha na Inter)."""
    from PIL import ImageFont
    from rodape_entrega import FONTES
    import rotulos_manuscritos_casaa as RM
    pts = (np.float32(esc["tri"]) - [X0, Ya3]) * s
    bx0, by0 = np.floor(pts.min(axis=0)).astype(int) - 3
    bx1, by1 = np.ceil(pts.max(axis=0)).astype(int) + 4
    ss = 8
    m = np.zeros(((by1 - by0) * ss, (bx1 - bx0) * ss), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((pts - [bx0, by0]) * ss))], 255, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[by0:by1, bx0:bx1].astype(np.float32)
    out[by0:by1, bx0:bx1] = np.clip(np.round(reg * (1 - a) + np.float32(esc["cor_seta"]) * a), 0, 255).astype(np.uint8)
    corpo = esc["corpo"] * s
    if opcao == "A":
        fonte = ImageFont.truetype(str(FONTES / esc["fonte"]), int(round(corpo * 4)))
        for texto, tx, ly, _ in esc["linhas"]:
            ox, oy = (tx - X0) * s, (ly - Ya3) * s
            W = int(fonte.getlength(texto) / 4) + int(4 * s)
            H = int(corpo * 3)
            X, Y = int(ox) - int(2 * s), int(oy) - int(corpo * 2)
            al = AM._alfa_texto(texto, fonte, ox, oy, (X, Y, W, H), ss=4)[..., None]
            reg = out[Y:Y + H, X:X + W].astype(np.float32)
            out[Y:Y + H, X:X + W] = np.clip(np.round(reg * (1 - al) + np.float32(esc["cor"]) * al), 0,
                                            255).astype(np.uint8)
        lt = esc.get("letra")
        if lt:                                          # (13/11, "COLOQUE O S ABAIXO DA SETA") o S sob a seta
            l_, t_, r_, b_ = fonte.getbbox(lt["texto"], anchor="ls")
            ox, oy = (lt["cx"] - X0) * s - (l_ + r_) / 8, (lt["topo"] - Ya3) * s - t_ / 4
            W, H = int((r_ - l_) / 4) + int(12 * s), int(corpo * 3)
            X, Y = int(ox) - int(4 * s), int(oy) - int(corpo * 2)
            al = AM._alfa_texto(lt["texto"], fonte, ox, oy, (X, Y, W, H), ss=4)[..., None]
            reg = out[Y:Y + H, X:X + W].astype(np.float32)
            out[Y:Y + H, X:X + W] = np.clip(np.round(reg * (1 - al) + np.float32(esc["cor"]) * al), 0,
                                            255).astype(np.uint8)
        return
    k = RM._altura_maiuscula(FONTES / esc["fonte"]) / RM._altura_maiuscula(RM.FONTE) * RM.MANUSCRITA["altura"]
    fi = ImageFont.truetype(str(FONTES / esc["fonte"]), 400)
    fk = ImageFont.truetype(str(RM.FONTE), 400)
    teto = min(fi.getlength(t) / max(fk.getlength(t) * k, 1e-6) for t, *_ in esc["linhas"])
    itens = [(t, corpo * k * min(1.0, teto), (cx - X0) * s, (ly - Ya3) * s, "ms") for t, _, ly, cx in esc["linhas"]]
    Z._desenhar_janela(out, itens, tuple(esc["cor"]), reforco)
    lt = esc.get("letra")
    if lt:                                              # o S sob a seta, na Kalam (como `ampliacao_a3_casaa.letra_kalam`)
        ck = corpo * k * min(1.0, teto)
        ft = ImageFont.truetype(str(RM.FONTE), max(4, int(round(ck * 4))))
        l_, t_, r_, b_ = ft.getbbox(lt["texto"], anchor="ls")
        Z._desenhar_janela(out, [(lt["texto"], ck, (lt["cx"] - X0) * s - (l_ + r_) / 8,
                                  (lt["topo"] - Ya3) * s - t_ / 4, "ls")], tuple(esc["cor"]), reforco)


def montar12k(saida_topaz, largura=None, opcao="A"):
    from PIL import Image
    import rotulos_manuscritos_casaa as RM
    q = Z.G12
    L = largura or q["largura"]
    Wa0, Ha0 = q["a3"]
    Hh = int(round(L * Ha0 / Wa0))
    Q = quadro()
    _usar_rotulos_b(Q)
    img = cv2.imread(str(FINAL))
    entrada = cv2.imread(str(ENTRADA_IA))
    d = json.loads(DADOS.read_text())
    rc, rots, esc = d["recortes"], d["rotulos"], d["escada"]
    X0, Wc, Yia, Hia = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"]
    Ya3 = Yia + (Hia - Wc * Ha0 / Wa0) / 2
    s = L / Wc
    ia = cv2.imread(str(saida_topaz))
    Hi, Wi = ia.shape[:2]
    print(f"[Subsolo da Casa B, opção {opcao}] a saída ampliada: {Wi}x{Hi}; o JPG: {L}x{Hh} ({s:.3f}x a final)")
    M = Z._alinhar(ia, entrada)
    Au = np.array([[1 / s, 0, 0], [0, 1 / s, Ya3 - Yia], [0, 0, 1]], np.float64)
    Tm = (np.diag([Wi / Wc, Hi / Hia, 1.0]) @ np.vstack([M.astype(np.float64), [0, 0, 1]]) @ Au)[:2]
    out = cv2.warpAffine(ia, Tm, (L, Hh), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    del ia
    # os tons da final: a baixa frequência na escala da entrada, ampliada (em faixas)
    hb = int(round(Hh / s))
    ref0 = cv2.warpAffine(entrada, np.array([[1, 0, 0], [0, 1, -(Ya3 - Yia)]], np.float64), (Wc, hb),
                          flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255)).astype(np.float32)
    peq = cv2.resize(out, (Wc, hb), interpolation=cv2.INTER_AREA).astype(np.float32)
    sg = q["tom_sigma_px"]
    corr = cv2.resize(cv2.GaussianBlur(ref0, (0, 0), sg) - cv2.GaussianBlur(peq, (0, 0), sg), (L, Hh),
                      interpolation=cv2.INTER_CUBIC)
    for y in range(0, Hh, 1024):
        out[y:y + 1024] = np.clip(np.round(out[y:y + 1024].astype(np.float32) + corr[y:y + 1024]), 0, 255
                                  ).astype(np.uint8)
    del corr
    # o fundo: branco puro fora da planta (o branco ligado à borda da final)
    Fq = np.array([[s, 0, -s * X0], [0, s, -s * Ya3]], np.float64)
    gq = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fundo = (gq >= 254).astype(np.uint8)
    _, lab = cv2.connectedComponents(fundo)
    fundo = (lab == lab[0, 0]).astype(np.uint8)
    kk = 2 * q["fundo_folga_px"] + 1
    fundo = cv2.erode(fundo, np.ones((kk, kk), np.uint8)).astype(np.float32)
    sf = 2.0 * L / Wa0
    for y in range(0, Hh, 1024):
        y1 = min(Hh, y + 1024)
        pad = int(4 * sf) + 2
        ya, yb = max(0, y - pad), min(Hh, y1 + pad)
        Ft = Fq.copy()
        Ft[1, 2] -= ya
        fa = cv2.warpAffine(fundo, Ft, (L, yb - ya), flags=cv2.INTER_LINEAR, borderValue=1.0)
        fa = cv2.GaussianBlur(fa, (0, 0), sf)[y - ya:y1 - ya, :, None]
        out[y:y1] = np.clip(np.round(out[y:y1].astype(np.float32) * (1 - fa) + 255 * fa), 0, 255).astype(np.uint8)
    # (13/11, "OK, PODE APLICAR AS RECOMENDADAS") as peças da biblioteca (`biblioteca_subsolo_casab_1311`): o que
    # mudou na final vem dela ampliada, e as peças de PNG por cima, nítidas
    import biblioteca_subsolo_casab_1311 as BB
    out = BB.pecas_12k(img, out, s, X0, Ya3)
    # o shaft, os rótulos, a seta e a descrição da escada
    _shaft_12k(out, d["shaft_px"], s, X0, Ya3)
    meia = q["janela_px"] * s
    reforco = RM.MANUSCRITA["reforco_px"] * s

    def janela(cx, cy):
        return (max(0, int(cx - meia)), max(0, int(cy - meia / 2)), min(L, int(cx + meia)), min(Hh, int(cy + meia / 2)))
    if opcao == "B":
        fk, fk_est = Z.fator_manuscrita(Q, rots, s, X0, Ya3)
        print(f"    Kalam: o mesmo fator {fk:.3f} em todos os rótulos"
              + (f" (menos {', '.join(f'{n} {v:.3f}' for n, v in fk_est.items())})" if fk_est else ""))
    for b in rots:
        if opcao == "B":
            Z._desenhar_janela(out, Z._itens_manuscrita(Q, b, s, X0, Ya3, fator=fk_est.get(b["nome"], fk)),
                               tuple(b["cor"]), reforco)
            continue
        u, v = Q.p2q(*b["pdf"])
        cx, cy = (u + b["desvio"][0] - X0) * s, (v + b["desvio"][1] - Ya3) * s
        bx, by, bx1, by1 = janela(cx, cy)
        a = Z.alfa_rotulo(Q, b, (by1 - by, bx1 - bx), s, X0 + bx / s, Ya3 + by / s)[..., None]
        reg = out[by:by1, bx:bx1].astype(np.float32)
        out[by:by1, bx:bx1] = np.clip(np.round(reg * (1 - a) + np.float32(b["cor"]) * a), 0, 255).astype(np.uint8)
    _escada_12k(out, esc, s, X0, Ya3, opcao, reforco)
    saida = Path(str(SAIDA).format(opcao=opcao))
    saida.parent.mkdir(parents=True, exist_ok=True)
    dpi = int(round(L / (420 / 25.4)))
    Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(saida, quality=q["qualidade"], subsampling=0,
                                                               dpi=(dpi, dpi), optimize=True)
    cv2.imwrite(str(R / f"POE642_CasaB_PH_Subsolo_12K_opcao_{opcao}_previa.jpg"),
                cv2.resize(out, (2000, round(2000 * Hh / L)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
    for nome, (x0, y0, x1, y1) in CONFERENCIA.items():
        u0, v0, u1, v1 = [int(round(t_)) for t_ in ((x0 - X0) * s, (y0 - Ya3) * s, (x1 - X0) * s, (y1 - Ya3) * s)]
        cr = out[v0:v1, u0:u1]
        ref = cv2.resize(img[y0:y1, x0:x1], (cr.shape[1], cr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
        par = np.hstack([ref, np.full((cr.shape[0], 24, 3), 255, np.uint8), cr])
        cv2.imwrite(str(R / f"POE642_CasaB_PH_Subsolo_12K_opcao_{opcao}_conferencia_{nome}.jpg"),
                    cv2.resize(par, (par.shape[1] // 2, par.shape[0] // 2), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {saida} {L}x{Hh} ({dpi} dpi na A3), {saida.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="etapa", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("--passos", required=True, help="a pasta dos passos de pedidos_subsolo_casab_1211.py")
    d_ = sub.add_parser("diferencas")
    d_.add_argument("saida_ia", type=Path)
    c_ = sub.add_parser("corrigir")
    c_.add_argument("saida_ia", type=Path)
    c_.add_argument("destino", type=Path)
    m_ = sub.add_parser("montar12k")
    m_.add_argument("saida_topaz", type=Path)
    m_.add_argument("--largura", type=int, default=None)
    m_.add_argument("--opcao", choices=("A", "B", "AB"), default="AB")
    a = ap.parse_args()
    if a.etapa == "preparar":
        preparar(a.passos)
    elif a.etapa == "diferencas":
        diferencas(a.saida_ia)
    elif a.etapa == "corrigir":
        corrigir_ia(a.saida_ia, a.destino)
    else:
        for op in a.opcao:
            montar12k(a.saida_topaz, a.largura, op)

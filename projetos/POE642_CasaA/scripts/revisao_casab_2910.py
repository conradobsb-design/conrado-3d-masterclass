"""Casa B, Térreo: a revisão de 29/10/26 sobre a final aprovada.

Revisão trecho a trecho contra o PDF e as REGRAS, apresentada com o mapa
(`POE642_CasaB/renders/POE642_CasaB_PH_Terreo_2910_revisao_mapa.jpg`); OK do usuário: "aprovados os itens", e no item 2:
"desenhe as folhas como na casa C, aplicando o mesmo padrão". A final da Casa B não sai mais só do motor
(`final3840_casab.final_3840`): depois dele vieram as cortinas franzidas (`cortinas_franzidas.py`) e os acertos da
piscina (tom, bordas retas, vidros da borda). Então os 8 itens entram aqui, como retoques locais sobre a final, com as
mesmas funções da Casa C (`final3840_casac`), cada uma com a configuração da Casa B:

1. varanda gourmet: as 12 cadeiras das duas mesas redondas no conjunto padrão de couro (`jogos_varanda_tc`);
2. as portas das suítes (master, 1, 2 e 3) com as folhas do plano de fora em brise de bronze escovado e as de dentro em
   vidro (`brises_suites_tc`); a sala íntima, que não é suíte, fica em vidro;
3-6. a "segunda linha" junto à folha das portas do banho 1, do banho 3, do BH motorista e do banho master (para o closet);
7. o contorno limpo das cadeiras das mesas da suíte master e das suítes 1 e 2 (`cadeiras_contorno_tc`);
8. os rótulos dos dois jardins sem o tracejado embaixo do texto (como na Casa C) e o do JARDIM fora da planta.

Uso (uma vez, sobre a final aprovada de 175b56e; o cache das etapas do motor da Casa B, de 26/10, dá o fundo dos
jardins sem os rótulos e sem o tracejado):
  python3 revisao_casab_2910.py [--antes <png>] [--saida <png>]

Depois, a adega (usuário, 29/10/26, com o recorte: "as garrafas estão em escala? Me parece que não."): a prateleira de
vinhos refeita com as garrafas na escala real (`ajustes_casab.adega_b`, agora em metros), só dentro dela (a sombra dela
no piso a final já tem). Uma vez, sobre a final de 0b25351:
  python3 revisao_casab_2910.py --adega [--antes <png>] [--saida <png>]

Depois, os pedidos de 29/10/26 vendo a final (`pedidos_tb`): a trama em todos os tapetes, a mesa redonda do hall em
madeira, a mesa de jantar escura com as cadeiras do padrão, os tampos da varanda em marrom, a madeira dos criados-mudos
e das mesas de apoio, os recamiers e o cobre-leito da suíte master, as máquinas da área de serviço em inox e a janela da
pia da cozinha só com as duas folhas. Uma vez, sobre a final de d83aee4:
  python3 revisao_casab_2910.py --pedidos [--antes <png>] [--saida <png>]
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
import final3840_casac as Cc                    # noqa: E402
import final3840_casad as D                     # noqa: E402

FINAL_B = F.B.CASA_B / "renders" / "POE642_CasaB_PH_Terreo_final_rotulos.png"

# Item 1: as mesas redondas da varanda gourmet (ARQ_MOBILIÁRIO, 1,80 m) e as cadeiras do PDF, que na Casa B estão na
# ARQ_MOBILIÁRIO (na Casa C, na ARQ_LAYOUT HUMANIZAÇÃO). O conjunto do bloco entra na escala da mesa do PDF.
JOGOS_VARANDA_TB = dict(Cc.JOGOS_VARANDA_TC, mesas_pt=[(1000.3, 1318.2, 1102.3, 1420.3), (1195.0, 1318.2, 1297.0, 1420.3)],
                        camada="ARQ_MOBILIÁRIO")

# Item 2: as folhas do plano de fora (o do lado da varanda ou do terraço) das portas de correr das suítes. No PDF, cada
# folha são duas tiras brancas de 1,4 pt da ARQ_PAREDE, coladas, como na Casa C. Suítes 1 e 2: a fachada de cima (o lado
# de fora em cima), 2 folhas por plano; suíte 3: a lateral direita (fora à direita), 2 por plano; suíte master: a
# lateral esquerda (fora à esquerda), 3 por plano, em degrau.
BRISES_SUITES_TB = dict(Cc.BRISES_SUITES_TC, folhas_pt={
    "Suíte 1": [(1729.4, 527.2, 1863.2, 530.0), (1867.8, 530.0, 2001.6, 532.8)],
    "Suíte 2": [(2149.0, 527.2, 2282.8, 530.0), (2010.6, 530.0, 2144.4, 532.8)],
    "Suíte 3": [(2397.3, 823.1, 2400.1, 914.7), (2400.1, 919.2, 2402.9, 1010.8)],
    "Suíte Master": [(787.2, 602.0, 790.0, 709.7), (790.0, 714.2, 792.9, 822.0), (792.9, 826.5, 795.7, 934.2)]})

# Item 2, depois (usuário, vendo a final: "são apenas 4 folhas: duas de bronze na parte externa e duas de vidro na parte
# interna. não há mais que 4. Corrija."; na suíte 3: "aqui também"; na suíte master: "esse é o exemplo correto. mas tem um
# erro entre as folhas da última (na parte de baixo). me parece que tem uma cortina entre a folha de bronze e de vidro."):
# entre o plano de fora e o de dentro, o render deixava faixas cinza e contornos claro/escuro (os caixilhos antigos), que
# liam como mais folhas, e no trecho de baixo da master um pedaço do desenho da cortina. Como na master (o exemplo do
# usuário): o bronze, um filete do piso do quarto e o vidro fino. Em cada trecho (pt: a folha de fora e a de dentro), a
# faixa das duas folhas e do vão entre elas é refeita com a madeira do quarto (a cor de cada linha no comprido das
# réguas, `busca_px` adiante, pulando a cortina e o que não é madeira), a folha de dentro em vidro fino (o miolo claro e as
# bordas cinza, como as outras esquadrias da Casa B) e, depois, as de fora em bronze (`brises_suites_tc`). `lado`: de que
# lado do eixo da espessura fica o quarto. A sala íntima, com o mesmo desenho e em vidro, fica com as 4 folhas de vidro.
VAOS_SUITES_TB = {"portas": {
    "Suíte 1": ("y", 1, [((1729.4, 527.2, 1863.2, 530.0), (1729.4, 541.3, 1862.1, 544.2)),
                         ((1867.8, 530.0, 2001.6, 532.8), (1866.6, 538.5, 1999.3, 541.3))]),
    "Suíte 2": ("y", 1, [((2010.6, 530.0, 2144.4, 532.8), (2021.4, 541.3, 2149.8, 544.2)),
                         ((2149.0, 527.2, 2282.8, 530.0), (2154.4, 538.5, 2282.8, 541.3))]),
    "Suíte 3": ("x", -1, [((2397.3, 823.1, 2400.1, 914.7), (2385.9, 823.1, 2388.8, 914.7)),
                          ((2400.1, 919.2, 2402.9, 1010.8), (2388.8, 919.2, 2391.6, 1010.8))]),
    "Suíte Master": ("x", 1, [((787.2, 602.0, 790.0, 709.7), (795.7, 602.0, 798.5, 709.7)),
                              ((790.0, 714.2, 792.9, 822.0), (798.5, 714.2, 801.4, 822.0)),
                              ((792.9, 826.5, 795.7, 934.2), (801.4, 826.5, 804.2, 934.2))]),
    "Sala íntima": ("y", 1, [((1369.4, 527.2, 1483.7, 530.0), (1369.4, 538.5, 1483.7, 541.3)),
                             ((1488.2, 530.0, 1602.4, 532.8), (1488.2, 541.3, 1602.4, 544.2))])},
    "vidro_fora": ("Sala íntima",), "busca_px": 40, "amostra_px": 3, "liso_px": {"y": 21, "x": 1},
    "vidro": (219, 216, 211), "borda": (176, 177, 179), "larg_borda_px": 0.9, "ss": 8}


def _madeira(px):
    """O px é da madeira do quarto: amarronzado (R bem acima de B) e no tom médio (a cortina e a sombra dela, claras e
    mais neutras, ficam de fora)."""
    m = px.mean(axis=-1)
    return (px[..., 2].astype(np.int16) - px[..., 0] > 35) & (m > 100) & (m < 165)


def vaos_suites_tb(Q, img):
    q = VAOS_SUITES_TB
    out = img.copy()
    k = q["ss"]
    n = 0
    for nome, (eixo, lado, pares) in q["portas"].items():
        v = out if eixo == "y" else out.transpose(1, 0, 2)          # a espessura nas linhas
        for fora, dentro in pares:
            rs = []
            for r in (fora, dentro):
                (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
                rs.append((a, b, c, d) if eixo == "y" else (b, a, d, c))   # (comprido0, esp0, comprido1, esp1)
            (fa0, fe0, fa1, fe1), (da0, de0, da1, de1) = rs
            c0, c1 = int(np.ceil(max(fa0, da0))), int(np.floor(min(fa1, da1)))
            e0 = int(np.floor(min(fe0, de0))) - (1 if lado < 0 else 0)
            e1 = int(np.ceil(max(fe1, de1))) + (1 if lado > 0 else 0)
            # a cor da madeira em cada linha das réguas: os primeiros px de madeira adiante, para dentro do quarto
            passos = range(e1, e1 + q["busca_px"]) if lado > 0 else range(e0 - 1, e0 - 1 - q["busca_px"], -1)
            col = v[list(passos), c0:c1]                                  # (busca, comprido, 3)
            ok = _madeira(col)
            cores = np.zeros((c1 - c0, 3), np.float32)
            todas = col[ok]
            med = np.median(todas, axis=0) if len(todas) else np.float32((128, 140, 160))
            for j in range(c1 - c0):
                bons = col[ok[:, j], j][:q["amostra_px"]]
                cores[j] = np.median(bons, axis=0) if len(bons) else med
            # no comprido das réguas (as portas de cima: a faixa corre junto com elas) o tom é alisado, sem as emendas de
            # uma régua para a outra; nas laterais, as réguas cruzam a faixa e cada linha fica com a sua
            janela = q["liso_px"][eixo]
            if janela > 1:
                cores = cv2.blur(cv2.medianBlur(np.ascontiguousarray(np.round(cores)[:, None].astype(np.uint8)),
                                                janela).astype(np.float32), (1, janela))[:, 0]
            v[e0:e1, c0:c1] = np.clip(np.round(cores), 0, 255).astype(np.uint8)[None]
            # as folhas de vidro (a de dentro; na sala íntima, as duas)
            vidros = [(da0, de0, da1, de1)] + ([(fa0, fe0, fa1, fe1)] if nome in q["vidro_fora"] else [])
            for (a0, s0, a1, s1) in vidros:
                X0, Y0 = int(np.floor(a0)) - 2, int(np.floor(s0)) - 2
                X1, Y1 = int(np.ceil(a1)) + 2, int(np.ceil(s1)) + 2
                h, w = Y1 - Y0, X1 - X0

                def ret(x0_, y0_, x1_, y1_):
                    m = np.zeros((h * k, w * k), np.uint8)
                    cv2.rectangle(m, (int(round((x0_ - X0) * k)), int(round((y0_ - Y0) * k))),
                                  (int(round((x1_ - X0) * k)) - 1, int(round((y1_ - Y0) * k)) - 1), 255, -1)
                    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
                eb = q["larg_borda_px"]
                A, M = ret(a0, s0, a1, s1), ret(a0 + eb, s0 + eb, a1 - eb, s1 - eb)
                reg = v[Y0:Y1, X0:X1].astype(np.float32)
                reg = reg * (1 - A) + np.float32(q["borda"]) * A
                reg = reg * (1 - M) + np.float32(q["vidro"]) * M
                v[Y0:Y1, X0:X1] = np.clip(reg, 0, 255).astype(np.uint8)
            n += 1
    print(f"    portas das suítes: {n} trechos com o vão entre os planos na madeira do quarto e a folha de dentro em vidro "
          f"fino (só as 4 folhas de cada porta; 6 na master, como no PDF)")
    return out


# Itens 3 a 6: a "segunda linha" junto à folha aberta (o contorno fino de uma folha que a limpeza das esquadrias deixou
# entre a folha e a face da parede, como a do Louceiro 2 da Casa C). Em px da final (x0, y0, x1, y1), com o deslocamento
# (dx, dy) de onde vem o piso: o travertino e a madeira na mesma linha (os estratos e as réguas são deitados); no banho
# 3, as linhas logo abaixo (à direita, junto à parede, há uma peça clara). No BH motorista, só o fio de dentro: o de
# fora (x 2968) é a face da parede, que segue abaixo da porta.
FOLHAS_LINHAS_TB = [("banho 1", (1929, 478, 1933, 528), (-12, 0)),
                    ("banho 3", (2535, 843, 2578, 847), (0, 4)),
                    ("BH motorista", (2965, 1506, 2966, 1541), (-14, 0)),
                    ("banho master", (1507, 515, 1551, 518), (-50, 0))]

# Item 7: as cadeiras das mesas (pt): cadeira e mesa. A da suíte master está na ARQ_MOBILIÁRIO.
CADEIRAS_MESAS_TB = [("suíte 1", (1832.2, 759.6, 1868.4, 798.1), (1807.7, 779.4, 1940.9, 807.8)),
                     ("suíte 2", (2026.6, 587.2, 2065.0, 623.4), (2014.6, 570.4, 2045.2, 717.8)),
                     ("suíte master", (998.5, 656.7, 1042.3, 698.5), (1022.5, 595.2, 1050.8, 711.3))]

# Item 8: os dois jardins (caixas em px da final). O fundo sem os rótulos vem da etapa `seta` do cache (a anterior aos
# rótulos) e o tracejado embaixo do texto (a `folga_px` dele) volta à etapa `escadas` (a anterior às projeções); o
# traço que encosta no texto sai inteiro, sem deixar toco (cada traço é o miolo dele, acima de `forte` de diferença,
# até `traco_max_px`, com 1 px de halo: os do X do jardim de inverno se cruzam e não saem juntos). Os rótulos dos jardins vão no ponto do PDF, sem
# busca (`F.ROTULOS_F["livres"]`); o JARDIM passa a rótulo fixo, em branco, no ponto `pt` (o centro do texto): no meio
# do jardim, entre as duas plantas e entre os dois pares de tracejados, mais para baixo.
ROTULOS_JARDINS_TB = {"caixas_px": {"JARDIM DE INVERNO": (2030, 760, 2240, 960), "JARDIM": (2390, 1180, 2550, 1300)},
                      "folga_px": 4, "forte": 60, "traco_max_px": 120, "fixos": {"JARDIM": {"pt": (2224.5, 1422.1)}}}


def folhas_linhas_tb(img):
    out = img.copy()
    for nome, (x0, y0, x1, y1), (dx, dy) in FOLHAS_LINHAS_TB:
        out[y0:y1, x0:x1] = img[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
        print(f"    {nome}: a linha junto à folha sai ({x1 - x0}x{y1 - y0} px), com o piso de ({dx}, {dy}) px")
    return out


def rotulos_jardins_tb(Q, img):
    import retoque_1pav_casae as R1
    q = ROTULOS_JARDINS_TB
    seta = cv2.imread(str(F.ETAPAS / "Terreo_seta.png"))
    esc = cv2.imread(str(F.ETAPAS / "Terreo_escadas.png"))
    caixa = np.zeros(img.shape[:2], bool)
    for x0, y0, x1, y1 in q["caixas_px"].values():
        caixa[y0:y1, x0:x1] = True
    base = img.copy()
    base[caixa] = seta[caixa]
    rot = F.B.rotulos_casab(Q.pg, Q.p2q2000) + [r for r in R1.rotulos_pdf(Q.pg) if r[0] == "SHAFT"]
    rf = F.ROTULOS_F
    F.ROTULOS_F = dict(rf, livres=tuple(n for n in rf["livres"] if n not in q["fixos"]),
                       fixos=dict(rf.get("fixos", {}), **{Q.chave: dict(rf.get("fixos", {}).get(Q.chave, {}), **q["fixos"])}),
                       brancos=dict(rf.get("brancos", {}), **{Q.chave: tuple(rf.get("brancos", {}).get(Q.chave, ()))
                                                               + tuple(q["fixos"])}))
    try:
        def uma(im):
            return F.rotulos(Q, im, rot, Q.q["ajustes"], granito=F.A.granito(im, Q.q.get("granito_lum_max", 125)))
        out1 = uma(base)
        texto = (np.abs(out1.astype(np.int16) - base.astype(np.int16)).max(axis=2) > 10) & caixa
        perto = cv2.dilate(texto.astype(np.uint8), np.ones((2 * q["folga_px"] + 1,) * 2, np.uint8)) > 0
        dif = np.abs(seta.astype(np.int16) - esc.astype(np.int16)).max(axis=2)
        trac = (dif > 0) & caixa
        forte = ((dif > q["forte"]) & caixa).astype(np.uint8)            # o miolo de cada traço, separado dos outros
        n, lab, st, _ = cv2.connectedComponentsWithStats(forte, connectivity=4)
        tocam = [i for i in np.unique(lab[perto & (forte > 0)]) if i > 0 and st[i, 4] <= q["traco_max_px"]]
        inteiros = cv2.dilate(np.isin(lab, tocam).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        sob = trac & (perto | inteiros)
        base[sob] = esc[sob]
        print(f"    jardins: {int(sob.sum())} px de tracejado embaixo dos textos voltam ao fundo; os rótulos de novo")
        out2 = uma(base)
    finally:
        F.ROTULOS_F = rf
    out = img.copy()
    out[caixa] = out2[caixa]
    return out


def adega_tb(img):
    Q = F.Quadro("Terreo")
    with F.em_quadro(Q):
        return F.B.adega_b(img, sombra_fora=False)


# ----------------------------------------------------------------------------------------------------------------------
# Os pedidos de 29/10/26 depois da revisão (`pedidos_tb`), uma vez, sobre a final de d83aee4 (as folhas e a adega):
# os tapetes, as mesas (hall, jantar e varanda) e as cadeiras do jantar, a madeira dos criados-mudos e das mesas de
# apoio, os recamiers e a cama da suíte master, as máquinas da área de serviço e a janela da pia da cozinha.

# 1. Os tapetes (usuário: "aplique textura em todos os tapetes"): a trama do tapete da Casa D (`D.tapete_trama_d`: o
# relevo do tapete do bloco `conjunto_estar_tapete` da biblioteca na escala, multiplicado só nos px do tapete, sem mudar o
# tom médio) nos 7 tapetes do PDF da Casa B: os dois estares (varanda gourmet e living), a sala íntima e os das 4 suítes.
# Nos estares, a cor do tapete é a mediana de todo o miolo; nos outros, a da faixa junto à borda (a cama e o sofá cobrem
# o miolo).
TAPETES_TB = dict(D.TAPETE_TRAMA_D, tapetes_pt=[("varanda", (1006.6, 987.6, 1290.1, 1186.1)),
                                                ("living", (1507.7, 973.7, 1791.2, 1172.1)),
                                                ("sala íntima", (1451.5, 566.4, 1593.6, 719.4)),
                                                ("suíte master", (848.0, 781.7, 1013.0, 934.8)),
                                                ("suíte 1", (1736.3, 566.4, 1900.7, 719.4)),
                                                ("suíte 2", (2122.2, 556.9, 2275.2, 739.4)),
                                                ("suíte 3", (2203.9, 879.3, 2374.0, 1004.0))],
                  miolo=("varanda", "living"))

# A madeira das peças novas (a mesa do hall, os criados-mudos e as mesas de apoio): o veio desenhado (ruído alongado no
# sentido das fibras: `veio_m` ao longo, `fio_m` através, e as faixas largas e suaves de `faixas_m`), no tom de cada peça
# (`TONS_TB`, BGR), com o chanfro (a quina virada para a luz, no alto à direita, mais clara; a do outro lado, mais
# escura) e o aro fino escuro da silhueta. A nogueira e o castanho são os da referência da mesa do hall (o centro e os
# painéis); o marrom, o da mesa da referência 2 (os tampos da varanda); o freijó, o das peças claras; o ocre (usuário,
# nos criados-mudos da suíte master: "criados mudos em tom madeira ocre."), o mel amarelado.
MADEIRA_TB = {"ss": 8, "veio_m": 0.12, "fio_m": 0.003, "veio": 0.05, "faixas_m": (0.35, 0.025), "faixas": 0.035,
              "chanfro_m": 0.012, "chanfro": 0.12, "aro_px": 0.7, "aro": 0.35, "semente": 2910}
TONS_TB = {"nogueira": (44, 64, 96), "castanho": (92, 124, 160), "marrom": (54, 78, 114), "freijo": (104, 144, 188),
           "ocre": (62, 124, 182)}


def _veio_tb(rng, h, w, ang, px_m, ss):
    """O fator do veio (em volta de 1) num campo h x w (em ss), com as fibras no ângulo `ang` (graus, anti-horário)."""
    q = MADEIRA_TB
    L = int(np.ceil(np.hypot(h, w))) + 8
    k = px_m * ss

    def alongado(sx, sy):
        n = cv2.GaussianBlur(rng.normal(0, 1, (L, L)).astype(np.float32), (0, 0), sigmaX=sx, sigmaY=sy)
        return n / max(float(n.std()), 1e-6)
    v = 1 + q["veio"] * alongado(q["veio_m"] * k, max(q["fio_m"] * k, 0.6)) \
        + q["faixas"] * alongado(q["faixas_m"][0] * k, q["faixas_m"][1] * k)
    v = cv2.warpAffine(v, cv2.getRotationMatrix2D((L / 2, L / 2), ang, 1.0), (L, L), borderMode=cv2.BORDER_REFLECT)
    y0, x0 = (L - h) // 2, (L - w) // 2
    return v[y0:y0 + h, x0:x0 + w]


def _relevo_tb(M, px_m, ss):
    """O chanfro e o aro de uma peça (a máscara `M` em ss): o fator de luz, em ss."""
    q = MADEIRA_TB
    dist = cv2.distanceTransform((M > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / ss          # em px do quadro
    larg = q["chanfro_m"] * px_m
    bv = np.clip(dist / larg, 0, 1)
    gy, gx = np.gradient(cv2.GaussianBlur(bv, (0, 0), 0.4 * ss))
    luz = np.clip((gy - gx) * larg * ss * q["chanfro"], -0.25, 0.25)
    return (1 + luz) * (1 - q["aro"] * np.clip(1 - dist / q["aro_px"], 0, 1))


def _pintar_tb(img, X0, Y0, w, h, ss, M, cor):
    """A `cor` (BGR, em ss) nos px da máscara `M` (0 a 1, em ss), levadas ao quadro em área (a borda antisserrilhada)."""
    def red(x):
        return cv2.resize(x, (w, h), interpolation=cv2.INTER_AREA)
    a = red(M)
    c = red(cor * M[..., None]) / np.maximum(a, 1e-4)[..., None]
    reg = img[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    img[Y0:Y0 + h, X0:X0 + w] = np.clip(reg * (1 - a[..., None]) + c * a[..., None], 0, 255).astype(np.uint8)
    return img


def _sombra_piso_tb(img, X0, Y0, a, px_m, sombras=None):
    """A sombra macia e a de contato (`D.SOMBRA_JOGOS_D`) do alfa `a` (no quadro, com o canto em X0, Y0) no piso, fora da
    peça; `a` já com a folga para a sombra."""
    luz = np.ones(a.shape, np.float32)
    for s in sombras or D.SOMBRA_JOGOS_D:
        d = np.float32([[1, 0, s["dx_m"] * px_m], [0, 1, s["dy_m"] * px_m]])
        luz *= 1 - cv2.GaussianBlur(cv2.warpAffine(a, d, a.shape[::-1], flags=cv2.INTER_LINEAR), (0, 0),
                                    s["sig_m"] * px_m) * s["forca"]
    h, w = a.shape
    reg = img[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    img[Y0:Y0 + h, X0:X0 + w] = np.clip(reg * (1 - (1 - luz) * (1 - a))[..., None], 0, 255).astype(np.uint8)
    return img


def _desenho_tb(Q, camada, r, tipos=("f", "fs")):
    return next(d for d in Q.desenhos if d.get("layer") == camada and d["type"] in tipos
                and max(abs(a - b) for a, b in zip(d["rect"], r)) < 0.5)


# 2. A mesa redonda do hall (usuário, com a referência de uma mesa redonda: "preciso do efeito de madeira. mandei uma
# referência de mesa para você pegar os tons. sendo ao centro um tom mais fechado e os outros três divisórias mais
# claro."): o tampo do PDF (ARQ_MOBILIÁRIO, 1,80 m) dividido pelas linhas dele (ARQ_MOBILIÁRIO e ARQ_LAYOUT HUMANIZAÇÃO):
# as partes do centro (o círculo do meio e o anel em volta, até `centro_r` do raio) e o aro da borda (além de `aro_r`)
# na nogueira escura da referência; os três painéis de fora no castanho mais claro, cada um com o veio na tangente (no
# meio do painel). As linhas viram o friso entre as peças (o vão, `friso`, em `friso_px`); a borda tem o chanfro e o
# aro. A sombra no piso fica a da final.
MESA_HALL_TB = {"caixa_pt": (1855.0, 1180.0, 1965.0, 1290.0), "centro_r": 0.45, "aro_r": 0.93,
                "escuro": "nogueira", "claro": "castanho", "friso": 0.55, "friso_px": 0.45}


def mesa_hall_tb(Q, img):
    from scipy import ndimage
    q, ss = MESA_HALL_TB, MADEIRA_TB["ss"]
    cx0, cy0, cx1, cy1 = q["caixa_pt"]
    ds = [d for d in Q.desenhos if d.get("layer") in ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO")
          and cx0 <= d["rect"].x0 and d["rect"].x1 <= cx1 and cy0 <= d["rect"].y0 and d["rect"].y1 <= cy1]
    tampo = max((d for d in ds if d["type"] in ("f", "fs")), key=lambda d: d["rect"].width)
    X0, Y0, X1, Y1 = F.ret_q(Q, q["caixa_pt"])
    w, h = X1 - X0, Y1 - Y0
    M = D._mascara_pdf(Q, [tampo], X0, Y0, w, h, ss).astype(np.float32) / 255
    Lm = D._mascara_pdf(Q, [d for d in ds if d["type"] == "s"], X0, Y0, w, h, ss, traco_px=q["friso_px"]) > 0
    ys, xs = np.nonzero(M > 0.5)
    cx, cy, R = xs.mean(), ys.mean(), (xs.max() - xs.min()) / 2
    yy, xx = np.mgrid[:h * ss, :w * ss]
    rr = np.hypot(xx - cx, yy - cy) / R
    n, lab = cv2.connectedComponents(((M > 0.5) & ~Lm).astype(np.uint8), connectivity=4)
    rng = np.random.default_rng(MADEIRA_TB["semente"])
    cor = np.zeros((h * ss, w * ss, 3), np.float32)
    feito = np.zeros((h * ss, w * ss), bool)
    claros = 0
    for i in range(1, n):
        mi = lab == i
        if mi.sum() < 4 * ss * ss:
            continue
        rm = rr[mi].mean()
        if q["centro_r"] <= rm <= q["aro_r"]:
            yi, xi = np.nonzero(mi)
            ang = -(np.degrees(np.arctan2(yi.mean() - cy, xi.mean() - cx)) + 90)
            tom = TONS_TB[q["claro"]]
            claros += 1
        else:
            ang, tom = 0.0, TONS_TB[q["escuro"]]
        cor[mi] = np.float32(tom) * _veio_tb(rng, h * ss, w * ss, ang, Q.px_m, ss)[mi][:, None]
        feito |= mi
    # os frisos e as lascas pequenas tomam a madeira do vizinho mais perto
    _, (iy, ix) = ndimage.distance_transform_edt(~feito, return_indices=True)
    cor = cor[iy, ix]
    fr = cv2.GaussianBlur(Lm.astype(np.float32), (0, 0), 0.35 * ss)
    cor *= (1 - q["friso"] * np.clip(fr / max(float(fr.max()), 1e-6), 0, 1))[..., None]
    cor *= _relevo_tb(M, Q.px_m, ss)[..., None]
    print(f"    mesa redonda do hall: o centro e o aro em nogueira, os {claros} painéis em castanho, com o veio e os frisos")
    return _pintar_tb(img.copy(), X0, Y0, w, h, ss, M, cor)


# 3-4. A mesa de jantar (usuário: "vamos aplicar o tom mais fechado na mesa") e os tampos das duas mesas redondas da
# varanda ("tampos da mesa em um tom mais marrom igual a imagem de referência 2"): o veio que o tampo já tem (a luz de
# cada px sobre a mediana do tampo, na potência `gama`) no tom novo, dentro do preenchimento do PDF recuado `recuo_px`
# (o contorno fica).
TAMPOS_TB = {"tampos": [("mesa de jantar", (1537.2, 1280.3, 1735.6, 1348.4), "nogueira"),
                        ("mesa redonda da varanda, à esquerda", (1000.3, 1318.2, 1102.3, 1420.3), "marrom"),
                        ("mesa redonda da varanda, à direita", (1195.0, 1318.2, 1297.0, 1420.3), "marrom")],
             "gama": 1.3, "recuo_px": 1.0, "ss": 4}


def tampos_tb(Q, img):
    q, ss = TAMPOS_TB, TAMPOS_TB["ss"]
    out = img.copy()
    for nome, r, tom in q["tampos"]:
        d = _desenho_tb(Q, "ARQ_MOBILIÁRIO", r)
        X0, Y0, X1, Y1 = F.ret_q(Q, r)
        X0, Y0, X1, Y1 = X0 - 2, Y0 - 2, X1 + 2, Y1 + 2
        w, h = X1 - X0, Y1 - Y0
        M = D._mascara_pdf(Q, [d], X0, Y0, w, h, ss)
        n = 2 * int(round(q["recuo_px"] * ss)) + 1
        M = cv2.erode(M, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n)))
        a = cv2.resize(M.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        Y = reg.mean(axis=2)
        med = float(np.median(Y[a[..., 0] > 0.99]))
        novo = np.float32(TONS_TB[tom]) * ((Y / med) ** q["gama"])[..., None]
        out[Y0:Y1, X0:X1] = np.clip(reg * (1 - a) + novo * a, 0, 255).astype(np.uint8)
        print(f"    {nome}: o tampo em {tom}, com o veio dele")
    return out


# 3. As cadeiras da mesa de jantar (usuário: "trazer as cadeiras que utilizamos nas casas, mas com o assento mais escuro
# igual a imagem 2 de referencia"): as da mesa de jantar da Casa D (`D.jantar_d`: a cadeira com o quadro de madeira da
# mesa de 10 lugares da biblioteca, `mesa_jantar_10`, na largura de cada cadeira do PDF, de frente para a mesa, 1/3 sob o
# tampo, com a sombra dele), as 10 do PDF (as 4 de cada lado e as das cabeceiras, de até 35 pt; o lado de cada uma pela
# posição relativa à mesa, `lado_norm`: a mesa é oval e as cabeceiras ficam dentro da caixa dela; o tampo que fica por
# cima delas é a oval do PDF, `mesa_pdf`, não a caixa); o assento no ameixa
# escuro da referência 2 (`absoluto`: o tom na luz da foto). As antigas saem com o travertino ao lado, na mesma linha
# (até `passos` cadeiras adiante, para achar um trecho sem peças).
JANTAR_TB = dict(D.JANTAR_TD, mesa_pt=(1537.2, 1280.3, 1735.6, 1348.4), lado_pt=(26.0, 35.0), lado_norm=True, passos=5,
                 mesa_pdf=True,
                 linho={"tom": (60, 50, 86), "gama": 1.0, "sat_madeira": (0.30, 0.15), "absoluto": True})


# 5. As máquinas sob a bancada da área de serviço (usuário: "adicionar o tom metalico inox aos eletrodomestico que estão
# sob a bancada"; depois: "os eletrodomesticos ficam parcialmente para fora, o restante fica sob a bancada, dentro da
# bancada. vamos mostrar apenas as pontas dos eletrodomesticos"): no PDF, os dois quadrados de 0,60 m da ARQ_LAYOUT
# HUMANIZAÇÃO (a lavadora e a secadora, de frente para a esquerda, com a linha da porta em `frente_pt`) sob a bancada,
# saindo dela pela frente. Só a ponta que sai (até a borda da bancada, `bancada_x_pt`) entra em inox escovado (o aço da
# Casa B, `F.PECAS["louca"]["inox"]`), o escovado no comprido, o painel da porta um tom acima, o chanfro, o contorno
# fino e a sombra curta; o resto fica sob a bancada.
INOX_TB = {"maquinas_pt": [(1963.6, 1533.1, 1997.6, 1567.1), (1963.6, 1572.6, 1997.6, 1606.6)], "frente_pt": 1967.0,
           "bancada_x_pt": 1969.2, "cor": (196, 199, 202), "escovado": 0.015, "painel": 1.05,
           "contorno": (112, 116, 120), "aro": 0.45, "ss": 8, "semente": 41}


def maquinas_inox_tb(Q, img):
    q, ss = INOX_TB, INOX_TB["ss"]
    out = img.copy()
    rng = np.random.default_rng(q["semente"])
    for r in q["maquinas_pt"]:
        X0, Y0, X1, Y1 = F.ret_q(Q, r)
        f = 6
        X0, Y0, X1, Y1 = X0 - f, Y0 - f, X1 + f, Y1 + f
        w, h = X1 - X0, Y1 - Y0
        (a0, b0), (a1, b1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        M = np.zeros((h * ss, w * ss), np.float32)
        xb = Q.p2q(q["bancada_x_pt"], 0)[0]
        M[int(round((b0 - Y0) * ss)):int(round((b1 - Y0) * ss)),
          int(round((a0 - X0) * ss)):int(round((min(a1, xb) - X0) * ss))] = 1
        a1x = cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA)
        out = _sombra_piso_tb(out, X0, Y0, a1x, Q.px_m, [F.PECAS["sombra"] | {"dx_m": -F.PECAS["sombra"]["dist_m"],
                                                                             "dy_m": F.PECAS["sombra"]["dist_m"]}])
        risco = cv2.GaussianBlur(rng.normal(0, 1, (h * ss, 1)).astype(np.float32), (0, 0), 0.4 * ss)
        risco = 1 + q["escovado"] * risco / max(float(risco.std()), 1e-6)
        cor = np.float32(q["cor"]) * np.repeat(risco, w * ss, axis=1)[..., None]
        xf = (Q.p2q(q["frente_pt"], 0)[0] - X0) * ss
        cor[:, :int(round(xf))] *= q["painel"]
        cor *= _relevo_tb(M, Q.px_m, ss)[..., None]
        cor = cor * (1 - q["aro"] * (M - cv2.erode(M, np.ones((ss // 2 + 1,) * 2, np.uint8))))[..., None] \
            + np.float32(q["contorno"]) * q["aro"] * (M - cv2.erode(M, np.ones((ss // 2 + 1,) * 2, np.uint8)))[..., None]
        out = _pintar_tb(out, X0, Y0, w, h, ss, M, cor)
    print(f"    área de serviço: as pontas das {len(q['maquinas_pt'])} máquinas, para fora da bancada, em inox escovado")
    return out


# 6. A janela da pia da cozinha (usuário: "corrigir as folhas de vidro da pia da cozinha. são apenas duas folhas"; depois:
# "na cozinha, aqui é uma janela com duas folhas, por isso precisa ter a base da janela em forma de 'soleira'") e a porta de
# correr da área de serviço para a área descoberta ("estamos sem a soleira. insira-a."): no vão do PDF (a espessura da
# parede, entre os batentes), a soleira de Bege Bahia (`final3840_casaa.soleira_bege`, com as faces da parede em cinza
# fino) e, por cima, os batentes e as duas folhas de correr do PDF, cada uma no plano dela, finas (alumínio com o vidro
# no meio, `final3840_casaa.portas_vidro`). Na janela, a soleira cobre o caixilho antigo da metade da direita (o tubo
# claro que lia como uma terceira folha); na porta, a folha do render era um tubo grosso da espessura da parede: as
# linhas dele que passam do vão (`limpa_px`: px, e de que lado vem o granito, em espelho) voltam ao granito.
SOLEIRAS_TB = {
    "limpa_px": [((2122, 1561, 2198, 1565), "cima"), ((2122, 1574, 2158, 1577), "baixo")],
    "portas": [
        {"nome": "janela da pia da cozinha", "soleira": (1393.2, 1808.4, 1567.3, 1819.8),
         "batentes": [(1391.0, 1808.4, 1393.2, 1819.8), (1567.3, 1808.4, 1569.6, 1819.8)],
         "folhas": [((1393.2, 1814.1, 1482.5, 1816.9), "x"), ((1478.0, 1816.9, 1567.3, 1819.8), "x")],
         "montante_pt": 0.6},
        {"nome": "de correr da área de serviço para a área descoberta", "soleira": (1829.8, 1712.0, 1964.1, 1720.6),
         "batentes": [(1827.5, 1712.0, 1829.8, 1720.6), (1964.1, 1712.0, 1966.4, 1720.6)],
         "folhas": [((1894.7, 1712.0, 1964.1, 1714.9), "x"), ((1829.8, 1714.9, 1899.2, 1717.7), "x")],
         "montante_pt": 0.6}]}


def soleiras_tb(Q, img):
    import final3840_casaa as FA
    q = SOLEIRAS_TB
    out = img.copy()
    for (x0, y0, x1, y1), lado in q["limpa_px"]:
        for y in range(y0, y1):
            out[y, x0:x1] = img[2 * y0 - 1 - y if lado == "cima" else 2 * y1 - 1 - y, x0:x1]
    pv = FA.PORTAS_VIDRO
    FA.PORTAS_VIDRO = dict(pv, portas=q["portas"])
    try:
        out = FA.portas_vidro(Q, out)
    finally:
        FA.PORTAS_VIDRO = pv
    return out


# 15. A ilha da varanda gourmet (usuário, com o recorte da ilha com o cooktop: "não existe essas linhas cinzas no meio da
# bancada. isso denota um degrau, o qual não existe."): no PDF, uma tira branca de 2,2 pt da ARQ_BANCADAS de ponta a
# ponta da ilha (1112,7 a 1349,6 x 1499,0 a 1501,2 pt), que o render desenhou como duas linhas cinza. As linhas dela
# (`faixa_px`, entre a borda esquerda da ilha e a parede) recebem o granito de logo acima, em espelho; o tom das duas
# metades da ilha já é o mesmo.
LINHA_ILHA_TB = {"faixa_px": (1301, 1339, 1548, 1344)}


def linha_ilha_tb(img):
    x0, y0, x1, y1 = LINHA_ILHA_TB["faixa_px"]
    out = img.copy()
    for y in range(y0, y1):
        out[y, x0:x1] = img[2 * y0 - 1 - y, x0:x1]
    print(f"    ilha da varanda gourmet: a linha do meio da bancada sai ({x1 - x0}x{y1 - y0} px), sem degrau")
    return out


# 16. As espreguiçadeiras da prainha (usuário: "melhore a representação dessas espreguiçadeiras. dando um efeito que está
# dentro da água. melhore o contorno dela também."): o render as deixava chapadas, com o contorno cinza grosso, uma sombra
# serrilhada e restos claros em volta. Em volta de cada uma (`zona_px` além da peça do PDF), a água é tecida de novo com
# a água limpa da prainha (`fonte_px`, image quilting da biblioteca de texturas, sem direção), no tom da água em volta.
# Por cima: a sombra no fundo da prainha, vista pela água (deslocada para baixo e à esquerda, macia e azulada); o corpo
# submerso, um pouco maior que o tampo (`corpo_px`), num branco esverdeado translúcido, com a água ainda aparecendo; a
# linha d'água, um fio claro e quebrado junto ao tampo; e o tampo em off-white com volume (a borda que cai, sem o
# contorno grosso, só o aro fino), o encosto (a parte menor, do lado de `encosto`) um tom abaixo e o vinco entre ele e o
# assento.
ESPREGUICADEIRAS_TB = {"pecas_pt": [(761.8, 1317.2, 871.8, 1359.0), (761.8, 1390.3, 871.8, 1432.2)],
                       "camada": "ARQ_LAYOUT HUMANIZAÇÃO", "vinco_x_pt": 828.0, "encosto": "dir",
                       "zona_px": 14, "fonte_px": (900, 1111, 1074, 1142), "p_px": 14, "semente": 2912,
                       "tampo": (238, 240, 241), "volume": {"larg_m": 0.05, "forca": 0.16}, "encosto_tom": 0.95,
                       "vinco": 0.22, "aro": 0.30, "ss": 8,
                       "sombra": {"dx_m": -0.13, "dy_m": 0.13, "sig_m": 0.06, "forca": 0.55, "tinta": (0.65, 0.85, 1.00)},
                       "corpo_px": 2.0, "corpo": {"cor": (222, 232, 214), "alfa": 0.50},
                       "linha": {"alfa": 0.45, "larg_px": 0.8}}


def espreguicadeiras_tb(Q, img):
    sys.path.insert(0, str(F.B.RAIZ / "_texturas"))
    import texturas
    q, ss = ESPREGUICADEIRAS_TB, ESPREGUICADEIRAS_TB["ss"]
    out = img.astype(np.float32)
    rng = np.random.default_rng(q["semente"])
    fx0, fy0, fx1, fy1 = q["fonte_px"]
    fonte = img[fy0:fy1, fx0:fx1]
    agua_med = np.median(fonte.reshape(-1, 3).astype(np.float32), axis=0)
    for k, r in enumerate(q["pecas_pt"]):
        d = _desenho_tb(Q, q["camada"], r)
        z = q["zona_px"]
        X0, Y0, X1, Y1 = F.ret_q(Q, r)
        X0, Y0, X1, Y1 = X0 - z - 8, Y0 - z - 8, X1 + z + 8, Y1 + z + 8
        w, h = X1 - X0, Y1 - Y0
        M = D._mascara_pdf(Q, [d], X0, Y0, w, h, ss).astype(np.float32) / 255

        def red(x):
            return cv2.resize(x, (w, h), interpolation=cv2.INTER_AREA)
        a1 = red(M)
        # 1. a água de novo na zona, tecida com a água limpa, no tom da água de fora da zona
        zona = cv2.dilate((a1 > 0.01).astype(np.uint8), np.ones((2 * z + 1,) * 2, np.uint8)).astype(np.float32)
        tec = texturas.quilting(texturas.variantes(fonte, False), h, w, p=q["p_px"], sobra=max(3, q["p_px"] // 3),
                                rng=np.random.default_rng(q["semente"] + k))[:h, :w].astype(np.float32)
        reg = out[Y0:Y1, X0:X1]
        fora = cv2.erode(1 - zona, np.ones((3, 3), np.uint8)) > 0.5
        tom = np.median(reg[fora], axis=0) if fora.any() else agua_med
        tec *= (tom / np.maximum(tec.reshape(-1, 3).mean(axis=0), 1))[None, None, :]
        al = cv2.GaussianBlur(zona, (0, 0), 1.5)
        al = np.maximum(al, zona * (cv2.erode(zona, np.ones((5, 5), np.uint8))))
        agua = reg * (1 - al[..., None]) + tec * al[..., None]
        # 2. a sombra no fundo, pela água
        s = q["sombra"]
        dsl = np.float32([[1, 0, s["dx_m"] * Q.px_m], [0, 1, s["dy_m"] * Q.px_m]])
        sb = cv2.GaussianBlur(cv2.warpAffine(a1, dsl, (w, h)), (0, 0), s["sig_m"] * Q.px_m) * s["forca"]
        agua *= 1 - sb[..., None] * np.float32(s["tinta"])[None, None, :]     # mais no vermelho: a sombra azulada
        # 3. o corpo submerso, maior que o tampo, translúcido, e a linha d'água junto ao tampo
        kc = 2 * int(round(q["corpo_px"] * ss)) + 1
        Mc = cv2.GaussianBlur(cv2.dilate(M, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kc, kc))), (0, 0), 0.6 * ss)
        ac = red(Mc) * (1 - a1) * q["corpo"]["alfa"]
        agua = agua * (1 - ac[..., None]) + np.float32(q["corpo"]["cor"]) * ac[..., None]
        kl = 2 * int(round(q["linha"]["larg_px"] * ss)) + 1
        anel = cv2.dilate(M, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kl, kl))) - M
        quebra = cv2.GaussianBlur(rng.normal(0, 1, M.shape).astype(np.float32), (0, 0), 3.0 * ss)
        quebra = np.clip(0.5 + quebra / max(float(quebra.std()), 1e-6), 0, 1)
        al_l = red(anel * quebra) * q["linha"]["alfa"]
        agua = agua * (1 - al_l[..., None]) + 250.0 * al_l[..., None]
        # 4. o tampo: off-white, a borda que cai, o encosto um tom abaixo, o vinco e o aro fino
        dist = cv2.distanceTransform((M > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / ss / Q.px_m
        vol = 1 - q["volume"]["forca"] * (1 - np.minimum(1, dist / q["volume"]["larg_m"])) ** 2
        xs = (np.arange(w * ss) + 0.5) / ss + X0
        xv = Q.p2q(q["vinco_x_pt"], 0)[0]
        enc = (xs > xv) if q["encosto"] == "dir" else (xs < xv)
        fator = vol * np.where(enc[None, :], q["encosto_tom"], 1.0)
        vinco = np.exp(-((xs - xv) / 0.9) ** 2)[None, :]
        fator *= 1 - q["vinco"] * vinco
        ruido = cv2.GaussianBlur(rng.normal(0, 1, M.shape).astype(np.float32), (0, 0), 0.5 * ss)
        fator *= 1 + 0.008 * ruido / max(float(ruido.std()), 1e-6)
        aro = M - cv2.erode(M, np.ones((ss // 2 + 1,) * 2, np.uint8))
        fator *= 1 - q["aro"] * aro
        cor = np.float32(q["tampo"])[None, None, :] * fator[..., None]
        tampo = red(cor * M[..., None]) / np.maximum(a1, 1e-4)[..., None]
        out[Y0:Y1, X0:X1] = agua * (1 - a1[..., None]) + tampo * a1[..., None]
    print(f"    prainha: {len(q['pecas_pt'])} espreguiçadeiras na água (a água refeita, a sombra no fundo, o corpo submerso, "
          f"a linha d'água e o tampo com volume)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# 17. O sofá em L do estar do living (usuário, com o recorte do sofá: "mantenha a textura do recamier do sofá para o todo do
# sofá. pode escurecer mais um pouco para distoar do tapete."): a chaise (o recamier, dentro do retângulo do tapete e no
# tom dele) tinha recebido a trama do tapete (item 1), e o resto do sofá não. As três peças do PDF (os dois módulos e a
# chaise, ARQ_MOBILIÁRIO) voltam ao que eram antes da trama e recebem, inteiras, a mesma trama (a do tapete do bloco
# `conjunto_estar_tapete`, na escala, com a força e o limite de `TAPETES_TB`), no tom `tom` (BGR), um pouco abaixo do
# tapete do living: cada px na luz que tinha (sobre a mediana do sofá), com os traços das almofadas.
SOFA_LIVING_TB = {"pecas_pt": [(1545.9, 937.0, 1640.6, 1004.4), (1640.6, 937.0, 1735.3, 1004.4),
                               (1735.3, 937.0, 1802.8, 1051.5)],
                  "camada": "ARQ_MOBILIÁRIO", "tom": (184, 192, 203), "semente": 31, "ss": 4}


def sofa_living_tb(Q, img, antes):
    sys.path.insert(0, str(F.B.RAIZ / "_texturas"))
    import texturas
    q, qt, ss = SOFA_LIVING_TB, TAPETES_TB, SOFA_LIVING_TB["ss"]
    ds = [_desenho_tb(Q, q["camada"], r) for r in q["pecas_pt"]]
    rs = [d["rect"] for d in ds]
    X0, Y0, X1, Y1 = F.ret_q(Q, (min(r.x0 for r in rs), min(r.y0 for r in rs), max(r.x1 for r in rs),
                                  max(r.y1 for r in rs)))
    X0, Y0, X1, Y1 = X0 - 1, Y0 - 1, X1 + 1, Y1 + 1
    w, h = X1 - X0, Y1 - Y0
    a = cv2.resize(D._mascara_pdf(Q, ds, X0, Y0, w, h, ss).astype(np.float32) / 255, (w, h),
                   interpolation=cv2.INTER_AREA)[..., None]
    # a trama do tapete, na escala (como `D.tapete_trama_d`)
    foto = cv2.imread(str(F.B.RAIZ / "_blocos" / "recortes" / f"{qt['recorte']}.png"))
    x0, y0, x1, y1 = qt["trecho"]
    L = foto[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    rel = L / cv2.GaussianBlur(L, (0, 0), qt["sigma_px"])
    e = Q.px_m / qt["px_m_foto"]
    rel = cv2.resize(rel, None, fx=e, fy=e, interpolation=cv2.INTER_AREA)
    u8 = np.repeat(np.clip((rel - 1) * 510 + 128, 0, 255).astype(np.uint8)[..., None], 3, axis=2)
    tec = texturas.quilting(texturas.variantes(u8, True), h, w, p=qt["p_px"], sobra=max(3, qt["p_px"] // 3),
                            rng=np.random.default_rng(q["semente"]))[:h, :w]
    t = np.clip(qt["forca"] * (tec[..., 0].astype(np.float32) - 128) / 510, -qt["limite"], qt["limite"])
    base = antes[Y0:Y1, X0:X1].astype(np.float32)
    med = np.median(base[a[..., 0] > 0.99], axis=0)
    novo = base * (np.float32(q["tom"]) / np.maximum(med, 1))[None, None, :] * (1 + t)[..., None]
    out = img.copy()
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - a) + novo * a, 0, 255).astype(np.uint8)
    print(f"    sofá do estar do living: as {len(ds)} peças com a trama da chaise, no tom um pouco abaixo do tapete")
    return out


# 18. As folhas de bronze da porta da sala íntima (usuário, com o recorte da porta da fachada de cima: "ficou faltando as
# folhas de bronze. adicione-as."): na revisão (item 2), a sala íntima, que não é suíte, ficou com as 4 folhas de vidro
# (`VAOS_SUITES_TB["vidro_fora"]`); agora as duas do plano de fora em bronze, como nas suítes (`Cc.brises_suites_tc`),
# por cima do vidro de fora; as de dentro ficam de vidro.
BRISES_SALA_INTIMA_TB = dict(BRISES_SUITES_TB, folhas_pt={"Sala íntima": [(1369.4, 527.2, 1483.7, 530.0),
                                                                         (1488.2, 530.0, 1602.4, 532.8)]})


# 19. O mobiliário da sala íntima (usuário, com o recorte da sala: "melhore o aspecto desse mobiliario: poltrona com
# apoio, sofá, mesa de centro, mesa na quina do sofá. mais humanizado possível"): os estofados (o sofá em L, as 6 peças
# do PDF num estofado só; a poltrona de concha; o pufe de apoio) no estofado das poltronas da Casa D (`D.estofado_d`:
# linho off-white com volume e trama, os traços de dentro como vincos, sem o contorno técnico), com a sombra macia e a
# de contato no piso; depois, as mesas (a de centro e a lateral quadrada no tom que já têm, a da quina do sofá em freijó)
# em madeira com o veio, o chanfro e a sombra (`pecas_madeira_tb`). Só valem os traços desenhados depois dos
# preenchimentos da peça (os de antes ficam escondidos no PDF, como a linha de x = 1593,6 que corta o sofá todo); na
# poltrona, o arco do encosto vem em segmentos de 1 a 3 pt, então todos viram vinco (`vinco_min_pt` 0; os do contorno
# caem na borda, onde o vinco não entra).
SALA_INTIMA_TB = {
    "camada": "ARQ_LAYOUT HUMANIZAÇÃO", "cor": (202, 212, 221), "semente": 79,
    "estofados": [("sofá", [(1552.9, 622.8, 1600.7, 711.4), (1495.6, 572.5, 1600.7, 622.8), (1600.7, 572.5, 1609.2, 622.8),
                            (1600.7, 622.8, 1609.2, 711.4), (1552.9, 566.8, 1609.2, 572.5), (1552.9, 711.4, 1609.2, 719.9)]),
                  ("poltrona", [(1459.7, 754.3, 1515.0, 810.4)], {"vinco_min_pt": 0.0}),
                  ("pufe", [(1442.7, 783.0, 1462.4, 802.9)])],
    "mesas": [{"nome": "mesa de centro da sala íntima", "camada": "ARQ_LAYOUT HUMANIZAÇÃO",
               "pt": (1465.7, 634.5, 1519.3, 688.3), "tom": "atual"},
              {"nome": "mesa da quina do sofá da sala íntima", "camada": "ARQ_LAYOUT HUMANIZAÇÃO",
               "pt": (1489.6, 566.2, 1509.2, 586.0), "tom": "freijo"},
              {"nome": "mesa lateral da poltrona da sala íntima", "camada": "ARQ_LAYOUT HUMANIZAÇÃO",
               "pt": (1438.6, 733.8, 1479.8, 775.0), "tom": "atual", "veio_graus": 45.0}]}


def sala_intima_tb(Q, img):
    return pecas_madeira_tb(Q, estofados_pdf_tb(Q, img, SALA_INTIMA_TB, "sala íntima"), pecas=SALA_INTIMA_TB["mesas"])


def estofados_pdf_tb(Q, img, q, onde):
    me = D.MOVEIS_TD
    out = img.copy()
    rng = np.random.default_rng(q["semente"])
    f = int(np.ceil(max(abs(s["dx_m"]) + 3 * s["sig_m"] for s in D.SOMBRA_JOGOS_D) * Q.px_m)) + 2
    for nome, rets, *op in q["estofados"]:
        op = op[0] if op else {}
        fills = [_desenho_tb(Q, q["camada"], r) for r in rets]
        z = (min(r[0] for r in rets), min(r[1] for r in rets), max(r[2] for r in rets), max(r[3] for r in rets))
        s0 = min(d.get("seqno", 0) for d in fills)
        pc = [d for d in Q.desenhos if d.get("layer") == q["camada"] and d["type"] == "s" and D._dentro_pt(d["rect"], z)
              and d.get("seqno", 0) > s0]
        tr = [d for d in pc if max(d["rect"].width, d["rect"].height) >= me["costura_min_pt"]]
        vmin = op.get("vinco_min_pt", me["estofado"]["vinco_min_pt"])
        vs = [d for d in pc if max(d["rect"].width, d["rect"].height) >= vmin]
        X0, Y0, X1, Y1 = D._caixa_px(Q, [d["rect"] for d in fills])
        X0, Y0, X1, Y1 = X0 - f, Y0 - f, X1 + f, Y1 + f
        M = D._mascara_pdf(Q, fills, X0, Y0, X1 - X0, Y1 - Y0, 4).astype(np.float32) / 255
        out = _sombra_piso_tb(out, X0, Y0, cv2.resize(M, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA), Q.px_m)
        out = D.estofado_d(Q, out, fills, tr, q["cor"], rng, vincos=vs)
        print(f"    {onde}, {nome}: estofado em linho com volume, trama e vincos, com a sombra no piso")
    return out


# 25. O sofá aos pés da cama da suíte 1 e os dois bancos aos pés das camas de solteiro da suíte 2 (usuário, com o recorte
# das duas suítes: "aplique a humanização no sofá em frente a cama e nos dois bancos em frente as camas de solteiro"): o
# estofado da sala íntima (`estofados_pdf_tb`: linho com volume, trama e os traços de dentro do PDF como costuras e
# vincos, com a sombra no piso), na silhueta de cada peça (ARQ_LAYOUT HUMANIZAÇÃO).
ESTOFADOS_SUITES_TB = {"camada": "ARQ_LAYOUT HUMANIZAÇÃO", "cor": (202, 212, 221), "semente": 81,
                       "estofados": [("sofá aos pés da cama", [(1847.2, 589.0, 1892.4, 698.8)]),
                                     ("banco de cima, aos pés da cama de solteiro", [(2145.1, 563.4, 2167.8, 617.3)]),
                                     ("banco de baixo, aos pés da cama de solteiro", [(2145.1, 673.6, 2167.8, 727.4)])]}


# 7-9. As peças de madeira: o criado-mudo redondo do quarto do motorista (usuário: "adicione textura de madeira ao criado
# mudo do quarto do motorista"), os dois criados-mudos da suíte master ("melhorar a representação dos criados mudos e do
# cobreleito da suite master") e as duas mesas de apoio dos recamiers ("melhorar a representação desses recamiers e
# mesas de apoio. textura, revestimento, sombra de integração ao solo"): cada peça do PDF em madeira (o veio no
# comprido dela), com o chanfro, o aro e os frisos dos traços de dentro do PDF; a sombra macia e a de contato no piso
# (as dos jogos da varanda da Casa D). Nas mesas de apoio (em C, o tampo sobre o assento do recamier e a lateral com o
# vão da alça), o vão (`vaos`) fica escuro, na sombra do tampo.
PECAS_MADEIRA_TB = [
    {"nome": "criado-mudo do quarto do motorista", "camada": "ARQ_LAYOUT HUMANIZAÇÃO",
     "pt": (2672.4, 1599.7, 2694.8, 1622.4), "tom": "freijo"},
    {"nome": "criado-mudo da suíte master, à esquerda", "camada": "ARQ_LOUÇAS E METAIS",
     "pt": (831.4, 920.5, 868.8, 945.0), "tom": "ocre"},
    {"nome": "criado-mudo da suíte master, à direita", "camada": "ARQ_LOUÇAS E METAIS",
     "pt": (989.1, 920.5, 1026.5, 945.0), "tom": "ocre"},
    {"nome": "mesa de apoio do recamier da esquerda", "camada": "ARQ_MOBILIÁRIO", "pt": (851.1, 649.3, 885.1, 672.0),
     "tom": "freijo", "vaos": [(879.5, 651.6, 882.9, 669.7)], "sobre": True},
    {"nome": "mesa de apoio do recamier da direita", "camada": "ARQ_MOBILIÁRIO", "pt": (953.0, 652.5, 987.0, 675.2),
     "tom": "freijo", "vaos": [(955.2, 654.8, 958.6, 672.9)], "sobre": True}]
FRISO_TB = {"larg_px": 0.45, "forca": 0.30, "vao": 0.45}


def pecas_madeira_tb(Q, img, nomes=None, pecas=None):
    """`pecas`: a lista (`PECAS_MADEIRA_TB` por padrão); com `tom` "atual", a madeira fica no tom que a peça já tem (a
    mediana do miolo dela)."""
    q, ss = pecas or PECAS_MADEIRA_TB, MADEIRA_TB["ss"]
    out = img.copy()
    rng = np.random.default_rng(MADEIRA_TB["semente"] + 1)
    for p in q:
        if nomes and not p["nome"].startswith(tuple(nomes)):
            continue
        d = _desenho_tb(Q, p["camada"], p["pt"])
        r = p["pt"]
        tracos = [t for t in Q.desenhos if t.get("layer") == p["camada"] and t["type"] == "s"
                  and r[0] - 0.5 <= t["rect"].x0 and t["rect"].x1 <= r[2] + 0.5
                  and r[1] - 0.5 <= t["rect"].y0 and t["rect"].y1 <= r[3] + 0.5]
        X0, Y0, X1, Y1 = F.ret_q(Q, r)
        f = int(np.ceil(max(abs(s["dx_m"]) + 3 * s["sig_m"] for s in D.SOMBRA_JOGOS_D) * Q.px_m)) + 2
        X0, Y0, X1, Y1 = X0 - f, Y0 - f, X1 + f, Y1 + f
        w, h = X1 - X0, Y1 - Y0
        M = D._mascara_pdf(Q, [d], X0, Y0, w, h, ss).astype(np.float32) / 255
        a1x = cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA)
        if p.get("sobre"):                      # sobre o assento: só a sombra curta
            s_ = F.PECAS["sombra"]
            out = _sombra_piso_tb(out, X0, Y0, a1x, Q.px_m,
                                  [{"dx_m": -s_["dist_m"] * 1.5, "dy_m": s_["dist_m"] * 1.5, "sig_m": s_["sig_m"],
                                    "forca": 0.40}])
        else:
            out = _sombra_piso_tb(out, X0, Y0, a1x, Q.px_m)
        largo = (r[2] - r[0]) >= (r[3] - r[1])
        if p["tom"] == "atual":
            mi = cv2.resize(cv2.erode(M, np.ones((3 * ss,) * 2, np.uint8)), (w, h), interpolation=cv2.INTER_AREA) > 0.99
            tom = np.median(img[Y0:Y1, X0:X1][mi].astype(np.float32), axis=0)
        else:
            tom = np.float32(TONS_TB[p["tom"]])
        cor = tom * _veio_tb(rng, h * ss, w * ss, p.get("veio_graus", 0.0 if largo else 90.0), Q.px_m, ss)[..., None]
        if tracos:
            fr = D._mascara_pdf(Q, tracos, X0, Y0, w, h, ss, traco_px=FRISO_TB["larg_px"]).astype(np.float32) / 255
            fr = cv2.GaussianBlur(fr, (0, 0), 0.3 * ss) * cv2.erode(M, np.ones((ss + 1,) * 2, np.uint8))
            cor *= (1 - FRISO_TB["forca"] * np.clip(fr / max(float(fr.max()), 1e-6), 0, 1))[..., None]
        for v in p.get("vaos", ()):
            V = np.zeros_like(M)
            (va, vb), (vc, vd) = Q.p2q(v[0], v[1]), Q.p2q(v[2], v[3])
            V[int(round((vb - Y0) * ss)):int(round((vd - Y0) * ss)), int(round((va - X0) * ss)):int(round((vc - X0) * ss))] = 1
            V = cv2.GaussianBlur(V, (0, 0), 0.3 * ss)
            reg = cv2.resize(out[Y0:Y1, X0:X1].astype(np.float32), (w * ss, h * ss), interpolation=cv2.INTER_LINEAR)
            cor = cor * (1 - V[..., None]) + reg * FRISO_TB["vao"] * V[..., None]
        cor *= _relevo_tb(M, Q.px_m, ss)[..., None]
        out = _pintar_tb(out, X0, Y0, w, h, ss, M, cor)
        print(f"    {p['nome']}: em madeira ({p['tom']}), com o veio, o chanfro e a sombra no piso")
    return out


# 8. Os recamiers da suíte master (o mesmo pedido): as peças da ARQ_LOUÇAS E METAIS de cada um (o assento, o encosto, o
# braço de fora) num estofado só, no linho off-white com volume e a trama (`D.estofado_d`, o das poltronas da Casa D),
# os traços de dentro como vincos (as partes ficam legíveis, sem linha marcada), e a sombra macia e a de contato no
# piso; a mesa de apoio de cada um vem depois, por cima (item 7-9).
RECAMIERS_TB = {"caixas_pt": [(859.0, 606.0, 908.5, 701.0), (930.5, 606.0, 980.0, 701.0)],
                "camada": "ARQ_LOUÇAS E METAIS", "cor": (202, 212, 221), "semente": 77}


def recamiers_tb(Q, img):
    q = RECAMIERS_TB
    out = img.copy()
    rng = np.random.default_rng(q["semente"])
    me = D.MOVEIS_TD
    for z in q["caixas_pt"]:
        pc = [d for d in Q.desenhos if d.get("layer") == q["camada"] and D._dentro_pt(d["rect"], z)]
        fills = [d for d in pc if d["type"] in ("f", "fs")]
        tr = [d for d in pc if d["type"] == "s" and max(d["rect"].width, d["rect"].height) >= me["costura_min_pt"]]
        vs = [d for d in pc if d["type"] == "s" and max(d["rect"].width, d["rect"].height) >= me["estofado"]["vinco_min_pt"]]
        X0, Y0, X1, Y1 = D._caixa_px(Q, [d["rect"] for d in fills])
        f = int(np.ceil(max(abs(s["dx_m"]) + 3 * s["sig_m"] for s in D.SOMBRA_JOGOS_D) * Q.px_m)) + 2
        X0, Y0, X1, Y1 = X0 - f, Y0 - f, X1 + f, Y1 + f
        M = D._mascara_pdf(Q, fills, X0, Y0, X1 - X0, Y1 - Y0, 4).astype(np.float32) / 255
        out = _sombra_piso_tb(out, X0, Y0, cv2.resize(M, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA), Q.px_m)
        out = D.estofado_d(Q, out, fills, tr, q["cor"], rng, vincos=vs)
    print(f"    recamiers da suíte master: {len(q['caixas_pt'])} estofados em linho com volume e trama, com a sombra no piso")
    return out


# 11. As duas poltronas à direita do tapete do estar da varanda (usuário: "substitua essas duas poltronas pela poltrona
# padrão que adotamos nas outras casas, a de referencia é aquela da sala intima da casa E."): como na Casa D
# (`D.poltronas_modelo_e_d`), a concha de estofado creme recortada da final do 1º Pavimento da Casa E
# (`final3840_casae._modelo_poltrona_1p`), no centro e no maior lado da peça do PDF (ARQ_MOBILIÁRIO), com a abertura do
# assento virada para a mesa de centro (`frente`) e a sombra e o contato das poltronas da Casa E. O buraco da antiga (a
# peça com `folga_px` e a sombra dela, `sombra_px`, para baixo e à esquerda) é refeito linha a linha, porque o tapete
# listrado e o travertino em estratos correm deitados: no tapete, o trecho da mesma linha mais perto à esquerda (até
# `busca_px`) que seja todo tapete livre (sem as peças do PDF de até `objetos_m2`, com `perto_px` de folga para a sombra
# delas; onde não há, o trecho livre mais perto, `recurso_px`, em vai e vem); fora dele, o da mesma linha à direita, no
# travertino da legenda do PDF; a borda escura do tapete
# (`borda_px`, as colunas a partir da linha do PDF), na mesma coluna, da linha limpa mais perto.
POLTRONAS_VARANDA_TB = {"pecas": [((1262.7, 1006.5, 1311.3, 1055.4), (-0.95, 0.31)),
                                  ((1257.8, 1087.7, 1306.4, 1136.6), (-0.97, -0.26))],
                        "camada": "ARQ_MOBILIÁRIO", "tapete_pt": (1006.6, 987.6, 1290.1, 1186.1), "borda_px": 4,
                        "objetos_m2": 10.0, "perto_px": 6, "folga_px": 5, "sombra_px": 3, "esfuma_px": 2,
                        "busca_px": 200, "recurso_px": 12}


def poltronas_varanda_tb(Q, img):
    import final3840_casae as E
    import retoque_terreo_casae as T
    q, qe = POLTRONAS_VARANDA_TB, E.POLTRONAS_TE
    H, W = img.shape[:2]
    out = img.astype(np.float32)
    zona = np.zeros((H, W), bool)
    buraco = np.zeros((H, W), bool)
    k = 2 * q["folga_px"] + 1
    s = q["sombra_px"]
    for r, _ in q["pecas"]:
        a = Q.preencher(lambda d, r=r: d.get("layer") == q["camada"] and D._dentro_pt(d["rect"], r))
        m = cv2.dilate((a > 0.05).astype(np.uint8), np.ones((k, k), np.uint8))
        m |= cv2.warpAffine(m, np.float32([[1, 0, -s], [0, 1, s]]), (W, H))
        buraco |= m.astype(bool)
    # as outras peças do PDF (o sofá, a mesa de centro, o pufe; não o tapete), com folga para a sombra delas
    m_pt = abs(Q.p2q(1, 0)[0] - Q.p2q(0, 0)[0]) / Q.px_m                # m por pt
    obj = Q.preencher(lambda d: d.get("layer") in F.CAMADAS_PECAS and d["type"] in ("f", "fs")
                      and d["rect"].width * d["rect"].height * m_pt ** 2 < q["objetos_m2"])
    k = 2 * q["perto_px"] + 1
    proibido = cv2.dilate(((obj > 0.05) | buraco).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    x0, y0, _, y1 = F.ret_q(Q, q["tapete_pt"])
    lx = int(np.floor(Q.p2q(q["tapete_pt"][2], 0)[0]))          # a 1ª coluna da borda escura
    lb = lx + q["borda_px"]
    trav = cv2.erode(Q.cor(next(pz[1] for pz in F.PISOS[Q.chave] if pz[3] == "travertino"), tol=6).astype(np.uint8),
                     np.ones((5, 5), np.uint8)) > 0
    fonte = out.copy()
    n_tap = n_fora = n_borda = 0
    for y in np.unique(np.nonzero(buraco)[0]):
        xs = np.nonzero(buraco[y])[0]
        for parte, (a, b), passo in (("tapete", (x0, lx), -1), ("fora", (lb, W), 1)):
            sel = xs[(xs >= a) & (xs < b)]
            if not len(sel) or not (y0 <= y < y1 or parte == "fora"):
                continue
            ha, hb = sel.min(), sel.max() + 1
            achou = False
            for d in range(1, q["busca_px"]):
                fa, fb = ha + passo * d, hb + passo * d
                if fa < a or fb > b:
                    break
                ok = ~proibido[y, fa:fb] & (True if parte == "tapete" else trav[y, fa:fb])
                if ok.all():
                    fonte[y, ha:hb] = out[y, fa:fb]
                    achou = True
                    break
            if not achou:
                # sem trecho livre do comprimento do buraco (o sofá ocupa a linha): o trecho livre mais perto, em vai
                # e vem (a lista corre deitada; o que sobra fica quase todo sob a poltrona nova)
                livre = ~proibido[y, a:b] & (True if parte == "tapete" else trav[y, a:b])
                xs_l = np.nonzero(livre)[0] + a
                xs_l = xs_l[(xs_l < ha) if passo < 0 else (xs_l >= hb)]
                if len(xs_l):
                    ref = xs_l.max() if passo < 0 else xs_l.min()
                    run = [ref]
                    while (run[-1] + passo) in set(xs_l.tolist()) and len(run) < q["recurso_px"]:
                        run.append(run[-1] + passo)
                    vv = run + run[-2:0:-1] if len(run) > 2 else run
                    for i, x in enumerate(range(ha, hb) if passo > 0 else range(hb - 1, ha - 1, -1)):
                        fonte[y, x] = out[y, vv[i % len(vv)]]
                    achou = True
            if achou:
                if parte == "tapete":
                    n_tap += hb - ha
                else:
                    n_fora += hb - ha
        bx = xs[(xs >= lx) & (xs < lb)]
        if len(bx) and y0 <= y < y1:
            for d in range(1, q["busca_px"]):
                for yy in (y - d, y + d):
                    if y0 <= yy < y1 and not proibido[yy, lx:lb].any():
                        fonte[y, lx:lb] = out[yy, lx:lb]
                        n_borda += lb - lx
                        break
                else:
                    continue
                break
    e = q["esfuma_px"]
    al = cv2.GaussianBlur(cv2.dilate(buraco.astype(np.uint8), np.ones((2 * e + 1,) * 2, np.uint8)).astype(np.float32),
                          (0, 0), e / 2)
    al[buraco] = 1
    out = out * (1 - al[..., None]) + fonte * al[..., None]
    cor, a_m = E._modelo_poltrona_1p(qe)
    fx, fy = qe["modelo"]["frente"]
    for r, (dx, dy) in q["pecas"]:
        (ax, ay), (bx_, by) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        cx, cy, t = (ax + bx_) / 2, (ay + by) / 2, max(bx_ - ax, by - ay)
        ang = np.degrees(np.arctan2(dx, dy) - np.arctan2(fx, fy))
        c2, a2 = E._girar_peca(cor, a_m, t / max(a_m.shape), ang)
        T.pousar_planta(out, c2, a2, float(cx), float(cy), t, qe["sombra"])
        T.pousar_planta(out, c2, a2, float(cx), float(cy), t, qe["sombra_contato"])
    print(f"    {len(q['pecas'])} poltronas do estar da varanda no modelo da sala íntima da Casa E (o fundo da antiga: "
          f"{n_tap} px de tapete, {n_fora} de travertino e {n_borda} da borda, das mesmas linhas e colunas)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# 12. A poltrona redonda à esquerda do tapete do estar da varanda (usuário: "traga a textura e revestimento estofada para
# essa poltrona"): a peça do PDF (o assento redondo e o encosto, ARQ_MOBILIÁRIO) no estofado das poltronas da Casa D
# (`D.estofado_d`: o linho off-white com volume e trama, os traços de dentro como vincos, sem o contorno técnico).
POLTRONA_REDONDA_TB = {"pt": (940.0, 1090.3, 993.3, 1142.8), "camada": "ARQ_MOBILIÁRIO", "semente": 78}


def poltrona_redonda_tb(Q, img):
    q, me = POLTRONA_REDONDA_TB, D.MOVEIS_TD
    pc = [d for d in Q.desenhos if d.get("layer") == q["camada"] and D._dentro_pt(d["rect"], q["pt"])]
    fills = [d for d in pc if d["type"] in ("f", "fs")]
    tr = [d for d in pc if d["type"] == "s" and max(d["rect"].width, d["rect"].height) >= me["costura_min_pt"]]
    vs = [d for d in pc if d["type"] == "s" and max(d["rect"].width, d["rect"].height) >= me["estofado"]["vinco_min_pt"]]
    out = D.estofado_d(Q, img.copy(), fills, tr, RECAMIERS_TB["cor"], np.random.default_rng(q["semente"]), vincos=vs)
    print("    poltrona redonda do estar da varanda: estofado em linho com volume e trama")
    return out


# 13. As duas poltronas à esquerda do tapete do estar do living (usuário: "para essas duas poltronas, deixe os encostos
# em tom vinho/bordô"): cada peça do PDF (ARQ_MOBILIÁRIO) dividida pelos traços dela: o encosto (a almofada curva das
# costas e a casca de fora, as partes com o centro a menos de `encosto_x` da largura, do lado das costas, e as tiras
# finas da casca até a ponta dos braços, até `casca_px` de espessura) no bordô (`tom`, na luz que a peça já tem: a de
# cada px sobre a mediana do encosto, na potência `gama`); os braços e o assento ficam.
# Depois (usuário, com o recorte das duas: "aplique textura no assento e estofado nos braços da poltrona"): a peça toda
# vira estofado, como as outras poltronas (`D.estofado_d`: volume, trama e os traços de dentro como vincos), cada parte
# com o volume dela (os traços de `costura_min_pt` para cima separam o assento, os braços, a almofada e a casca): o
# assento e os braços no linho das poltronas da varanda e dos recamiers (`linho`), o encosto no mesmo bordô, agora
# também com volume e trama (`estofado_d` em cada tom, juntos pela máscara do encosto).
ENCOSTOS_LIVING_TB = {"pecas_pt": [(1487.9, 1026.0, 1527.5, 1070.8), (1487.9, 1093.0, 1527.5, 1137.8)],
                      "camada": "ARQ_MOBILIÁRIO", "encosto_x": 0.42, "casca_px": 1.6, "tom": (70, 60, 116),
                      "gama": 1.0, "ss": 8, "linho": RECAMIERS_TB["cor"], "semente": 13}


def encostos_living_tb(Q, img):
    q, ss = ENCOSTOS_LIVING_TB, ENCOSTOS_LIVING_TB["ss"]
    out = img.copy()
    for r in q["pecas_pt"]:
        d = _desenho_tb(Q, q["camada"], r)
        tr = [t for t in Q.desenhos if t.get("layer") == q["camada"] and t["type"] == "s" and D._dentro_pt(t["rect"], r)]
        X0, Y0, X1, Y1 = F.ret_q(Q, r)
        X0, Y0, X1, Y1 = X0 - 2, Y0 - 2, X1 + 2, Y1 + 2
        w, h = X1 - X0, Y1 - Y0
        M = D._mascara_pdf(Q, [d], X0, Y0, w, h, ss) > 0
        L = D._mascara_pdf(Q, tr, X0, Y0, w, h, ss, traco_px=0.4) > 0
        n, lab, st, cen = cv2.connectedComponentsWithStats((M & ~L).astype(np.uint8), connectivity=4)
        a0 = (Q.p2q(r[0], 0)[0] - X0) * ss
        larg = (Q.p2q(r[2], 0)[0] - Q.p2q(r[0], 0)[0]) * ss
        enc = np.zeros(M.shape, bool)
        for i in range(1, n):
            fino = min(st[i, 2], st[i, 3]) <= q["casca_px"] * ss * 2       # a casca de fora, até a ponta dos braços
            if (cen[i][0] - a0) / larg < q["encosto_x"] or fino:
                enc |= lab == i
        # os traços entre duas partes do encosto e os de fora dele entram no tom (o traço vira o vinco escuro do bordô)
        viz = cv2.dilate(enc.astype(np.uint8), np.ones((int(0.8 * ss) * 2 + 1,) * 2, np.uint8)).astype(bool)
        resto = cv2.dilate(((M & ~L) & ~enc).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        enc_t = (enc | (viz & L & ~resto) | (viz & ~M)) & cv2.dilate(M.astype(np.uint8), np.ones((ss + 1,) * 2,
                                                                                               np.uint8)).astype(bool)
        a = cv2.resize(enc_t.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        Yl = reg.mean(axis=2)
        miolo = cv2.resize(cv2.erode(enc.astype(np.uint8), np.ones((ss + 1,) * 2, np.uint8)).astype(np.float32),
                           (w, h), interpolation=cv2.INTER_AREA) > 0.99
        med = float(np.median(Yl[miolo])) if miolo.any() else float(Yl.max())
        novo = np.float32(q["tom"]) * (np.clip(Yl / med, 0, 1.3) ** q["gama"])[..., None]
        if q.get("linho"):
            me = D.MOVEIS_TD
            cs = [t for t in tr if max(t["rect"].width, t["rect"].height) >= me["costura_min_pt"]]
            vs = [t for t in tr if max(t["rect"].width, t["rect"].height) >= me["estofado"]["vinco_min_pt"]]
            rng = np.random.default_rng(q["semente"])
            lin = D.estofado_d(Q, out.copy(), [d], cs, q["linho"], rng, vincos=vs)[Y0:Y1, X0:X1].astype(np.float32)
            novo = D.estofado_d(Q, out.copy(), [d], cs, q["tom"], rng, vincos=vs)[Y0:Y1, X0:X1].astype(np.float32)
            reg = lin
        out[Y0:Y1, X0:X1] = np.clip(reg * (1 - a) + novo * a, 0, 255).astype(np.uint8)
    print(f"    {len(q['pecas_pt'])} poltronas do estar do living: o encosto em bordô"
          + (", o assento e os braços em linho, tudo estofado com volume e trama" if q.get("linho") else ""))
    return out


# 14. As floreiras dos caixotes dos banhos na fachada de cima (usuário, com o recorte da fachada: "nesses retangulos em
# branco dos banhos, temos floreiras."): os dois caixotes do banho master, o do banho 1 e o do banho 2 (o miolo branco
# dentro da parede, pt) com as floreiras da Casa D (`D.floreiras_td`: o fundo de casca, os seixos e as plantas da
# biblioteca, `C.floreira_lavabo_t`), uma planta a cada `passo_m` do caixote.
FLOREIRAS_TB = dict(D.FLOREIRAS_TD, miolos_pt=[(1069.0, 525.6, 1128.8, 544.6), (1284.5, 525.6, 1345.3, 544.6),
                                               (1624.5, 525.6, 1708.0, 544.6), (2409.7, 525.6, 2493.2, 543.6)],
                    passo_m=0.145, semente=2911)


# 10. A cama da suíte master (o mesmo pedido, no cobre-leito): a cama do motor (`F.cama_master`) refeita sobre a final,
# só ela (o banco aos pés e a sombra de fora ficam): o cobre-leito em matelassê com o relevo de cada losango
# (`acolchoado`), e o rolo do cobre-leito dobrado no mesmo matelassê, com mais volume nas pontas (as dobras soltas do
# desenho do PDF, que liam como "calombos" chapados, passam a ter a queda do tecido).
CAMA_MASTER_TB = dict(F.CAMA_MASTER_F, so_cama=True, acolchoado=0.06, rolo_vol=(0.05, 0.24))


# 20. O piso sob a cortina de baixo da suíte 3 (usuário, com o recorte da cortina: "embaixo dessa cortina, existe algo que
# não deve ser representado. corrija-a com o piso vinilico"): junto ao criado-mudo, um desenho antigo em barras cinza
# (px 2627-2641 × 800-819) passava por baixo do pano. Ali o vinílico volta (as tábuas correm na horizontal, então cada
# linha vem da mesma linha, da faixa limpa entre o vidro e o caixilho, `fonte_x`), o contorno do tapete e o trilho seguem
# retos (as `linhas_x`, da linha de cima) e o pano de linho é pousado de novo por cima, o mesmo da rodada das cortinas
# (`blocos.cortina` + `pousar_cortina` no quadro; refeito sobre a final ele bate com o de lá: 1 nível nos px opacos).
PISO_CORTINA_TB = {"caixa_px": (2627, 800, 2642, 820), "linhas_x": (2627, 2638), "linha_fonte_y": 795,
                   "fonte_x": (2646, 2654), "trecho": (2634.6, 748.2)}


def piso_cortina_tb(Q, img):
    from retoque_terreo_casae import pousar_cortina
    sys.path.insert(0, str(F.B.RAIZ / "_blocos"))
    import blocos
    q = PISO_CORTINA_TB
    x0, y0, x1, y1 = q["caixa_px"]
    f0, f1 = q["fonte_x"]
    out = img.copy()
    for x in range(x0, x1):
        out[y0:y1, x] = img[q["linha_fonte_y"], x] if x in q["linhas_x"] else img[y0:y1, f0 + (x - x0) % (f1 - f0)]
    with F.em_quadro(Q):
        k = F.AJ.CORTINAS_1PAV["ss"]
        o, vidro, ex, e0, e1 = min((t for t in F.B.trechos_cortina_b(Q.chave) if t[0] == "v"),
                                   key=lambda t: abs(t[2] - q["trecho"][0]) + abs(t[3] - q["trecho"][1]))
        cor, al = blocos.cortina((e1 - e0) / Q.px_m, Q.px_m * k, com_trilho=False)
        pano = out.copy()
        pousar_cortina(pano, cor, al, ex, e0, k, vidro)
    out[y0:y1, x0:x1] = pano[y0:y1, x0:x1]
    print(f"    suíte 3, cortina de baixo: vinílico no lugar do desenho antigo ({(x1 - x0) * (y1 - y0)} px) e o pano de "
          f"novo por cima")
    return out


# 21. O armário ao lado dos refrigeradores da cozinha (usuário, com o recorte do rótulo da cozinha: "aqui é um armário. ao
# lado dos refrigeradores. deve ser representado com tom apropriado, não marrom granito"): o retângulo da ARQ_BANCADAS
# junto aos dois refrigeradores saía com o granito do piso por dentro. Entra como armário até o teto (REGRAS, seção 7):
# a marcenaria areia com o veio no comprido, o tom da prateleira da adega (`ajustes_casab.ADEGA_B`), o contorno fino e
# sem a sombra de móvel baixo. Depois (usuário: "use esse mesmo tom de marcenaria usado no armario da cozinha para o
# louceiro e despensa"): os dois armários em L do louceiro e da despensa (ARQ_LAYOUT HUMANIZAÇÃO), cada braço com o veio
# no comprido dele e o contorno fino só por fora do L.
MARCENARIA_TB = {"madeira": F.B.ADEGA_B["madeira"], "contorno": F.B.ADEGA_B["contorno"], "larg_px": 0.6, "veio": 0.06,
                 "ss": 4, "semente": 2911,
                 "pecas": [("armário ao lado dos refrigeradores", [(1580.1, 1530.4, 1609.2, 1557.4)]),
                           ("armário em L do louceiro", [(1617.8, 1527.8, 1646.1, 1641.2), (1646.1, 1618.5, 1715.5, 1641.2)]),
                           ("armário em L da despensa", [(1796.3, 1527.8, 1819.0, 1641.2), (1721.2, 1618.5, 1796.3, 1641.2)])]}


def marcenaria_tb(Q, img, q=None):
    q = q or MARCENARIA_TB
    k = q["ss"]
    out = img.copy()
    rng = np.random.default_rng(q["semente"])
    for nome, bracos in q["pecas"]:
        cx = [Q.p2q(r[0], r[1]) + Q.p2q(r[2], r[3]) for r in bracos]
        wx0, wy0 = int(min(c[0] for c in cx)) - 3, int(min(c[1] for c in cx)) - 3
        wx1, wy1 = int(np.ceil(max(c[2] for c in cx))) + 3, int(np.ceil(max(c[3] for c in cx))) + 3
        h, w = wy1 - wy0, wx1 - wx0
        reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
        tudo = np.zeros((h * k, w * k), np.uint8)
        for X0, Y0, X1, Y1 in cx:
            r = (X0 - wx0, Y0 - wy0, X1 - wx0, Y1 - wy0)
            al = F.B.ret_aa((h, w), r)
            vertical = (r[3] - r[1]) > (r[2] - r[0])
            ve = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0),
                                  sigmaX=0.6 if vertical else 9, sigmaY=9 if vertical else 0.6)
            mad = np.float32(q["madeira"])[None, None] * (1 + q["veio"] * ve / max(ve.std(), 1e-6))[..., None]
            reg = reg * (1 - al[..., None]) + mad * al[..., None]
            cv2.rectangle(tudo, (int(round(r[0] * k)), int(round(r[1] * k))),
                          (int(round(r[2] * k)) - 1, int(round(r[3] * k)) - 1), 255, -1)
        lb = max(1, int(round(q["larg_px"] * k)))
        anel = (tudo & ~cv2.erode(tudo, np.ones((2 * lb + 1,) * 2, np.uint8))).astype(np.float32) / 255
        c = cv2.resize(anel, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - c) + np.float32(q["contorno"]) * c
        out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    {nome}: marcenaria areia com o veio no comprido, contorno fino, sem sombra")
    return out


# 22. A sombra da descida nos blocos de pedra à esquerda do deck (usuário, com o recorte das lajes: "algumas pedras perderam
# o efeito de sombra na descida. corrija!"): na auditoria de 26/10 (E8) os blocos perderam a linha do bocel e o degrau
# ficou marcado só pela sombra curta de cada bloco sobre os de baixo, para baixo e à esquerda (a luz do alto à direita,
# `F.degraus_blocos`). Nas bordas de cima e da direita das lajes, sobre a pedra grande, o degrau sumia. Agora cada bloco
# deixa também a sombra de contato em volta (a máscara dele crescida `cresce_m` e esfumada `sig_m`), só sobre os blocos
# pintados antes dele (os de baixo) e fora dos de depois; onde a sombra direcional já existe (a mesma conta de lá), só
# entra o que falta, e as bordas que já estavam boas não mudam.
SOMBRA_BLOCOS_TB = {"cresce_m": 0.02, "sig_m": 0.03, "forca": 0.30}

# Depois (usuário, com o recorte das três lajes da direita: "o segundo degrau deve estar sobre o terceiro, dando o efeito
# de descida de uma pedra para outra."; e, esclarecendo: "a pedra do meio precisa estar sobre a da esquerda. não mexa na
# pedra da direita com a do meio."): a laje do meio (370,5-427,2 pt) estava abaixo da da esquerda (336,5-370,5), que o PDF
# desenha depois: as duas só encostam, e a sombra de contato da da esquerda caía sobre a do meio, ao contrário da
# descida. Depois, na pedra grande e na laje à esquerda dela (194,8-251,4 pt): "aqui acontece o mesmo erro: a da direita
# deve sobrepor a da esquerda e não o contrário." `sobre`: os pares (a de cima, a de baixo) pedidos; a ordem de pintura
# nova é a ordenação que respeita esses pares e, nos blocos que se sobrepõem de fato (mais de `sobrepoe_px` px em ss), a
# ordem do PDF (as lajes da direita continuam sobre a pedra grande; a da direita, sobre a do meio), com o empate pela
# ordem do PDF. Os blocos são refeitos como em `F.degraus_blocos` (a mesma textura e o mesmo tom de cada um, a sombra
# curta), na ordem do PDF e na nova, e a final recebe a razão entre as duas nos px que mudam (o que veio depois por
# cima, multiplicado, fica); a sombra de contato segue a nova ordem.
ORDEM_BLOCOS_TB = {"sobre": [((370.5, 912.7, 427.2, 1162.1), (336.5, 929.7, 370.5, 1122.4)),
                             ((251.4, 793.6, 517.9, 1064.6), (194.8, 807.8, 251.4, 977.9))],
                   "sobrepoe_px": 16}


def _blocos_tb(Q):
    b, k = F.BLOCOS_F, F.BLOCOS_F["ss"]
    cx0, cy0, cx1, cy1 = b["caixa_pt"]
    blocos = sorted([d for d in Q.desenhos if d.get("layer") == "ARQ_CONTRAPISO" and d["type"] == "f" and d.get("fill")
                     and len(d["items"]) == 4 and cx0 <= d["rect"].x0 and d["rect"].x1 <= cx1 and cy0 <= d["rect"].y0
                     and d["rect"].y1 <= cy1], key=lambda d: d.get("seqno", 0))
    X0, Y0, X1, Y1 = F.ret_q(Q, b["caixa_pt"])
    w, h = X1 - X0, Y1 - Y0
    ms = []
    for d in blocos:
        m = np.zeros((h * k, w * k), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * k)) for c in Q.caminhos(d) if len(c) >= 3], 255)
        ms.append(m.astype(np.float32) / 255)
    n = len(blocos)
    pares = {}                                     # (a de baixo, a de cima)
    for i in range(n):
        for j in range(i + 1, n):
            if np.minimum(ms[i], ms[j]).sum() > ORDEM_BLOCOS_TB["sobrepoe_px"]:
                pares[(i, j)] = True
    for cima_pt, baixo_pt in ORDEM_BLOCOS_TB["sobre"]:
        ic, ib = [next(i for i, d in enumerate(blocos) if all(abs(v - u) < 0.2 for v, u in
                                                             zip((d["rect"].x0, d["rect"].y0, d["rect"].x1, d["rect"].y1), r)))
                  for r in (cima_pt, baixo_pt)]
        pares.pop((ic, ib), None)
        pares[(ib, ic)] = True
    ordem, feitos = [], set()
    while len(ordem) < n:                          # a ordenação, o empate pela ordem do PDF
        i = min(i for i in range(n) if i not in feitos and all(a in feitos for a, b_ in pares if b_ == i))
        ordem.append(i)
        feitos.add(i)
    return blocos, (X0, Y0, X1, Y1), ms, ordem


def ordem_blocos_tb(Q, img):
    sys.path.insert(0, str(F.B.RAIZ / "_texturas"))
    from texturas import textura
    b, k = F.BLOCOS_F, F.BLOCOS_F["ss"]
    blocos, (X0, Y0, X1, Y1), ms, ordem = _blocos_tb(Q)
    w, h = X1 - X0, Y1 - Y0
    s, d_ = b["sombra"], b["sombra"]["dist_m"] * Q.px_m * k
    rng = np.random.default_rng(b["semente"])
    tom = [1 + b["tom"] * rng.uniform(-1, 1) for _ in blocos]          # o tom de cada bloco, na ordem do PDF

    def reduzir(a):
        return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    pecas = []
    for i, mf in enumerate(ms):
        sb = reduzir(cv2.GaussianBlur(cv2.warpAffine(mf, np.float32([[1, 0, -d_], [0, 1, d_]]), (w * k, h * k)),
                                      (0, 0), s["sig_m"] * Q.px_m * k)) * s["forca"]
        tex = textura(b["pedra"], Q.px_m, h, w, semente=b["semente"] + i).astype(np.float32) * tom[i]
        pecas.append((reduzir(mf), sb, tex))
    base = img[Y0:Y1, X0:X1].astype(np.float32)

    def pintar(seq):
        reg = base.copy()
        for i in seq:
            a, sb, tex = pecas[i]
            reg *= (1 - sb * (1 - a))[..., None]
            reg = reg * (1 - a[..., None]) + tex * a[..., None]
        return reg
    velho, novo = pintar(range(len(blocos))), pintar(ordem)
    muda = np.abs(novo - velho).max(axis=2) > 0.5
    razao = np.clip(novo / np.maximum(velho, 1.0), 0.2, 5.0)
    reg = base.copy()
    reg[muda] *= razao[muda]
    out = img.copy()
    out[Y0:Y1, X0:X1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    degraus em blocos: a ordem de pintura {ordem} (os pares pedidos; {int(muda.sum())} px)")
    return out


def sombra_blocos_tb(Q, img):
    q, b, k = SOMBRA_BLOCOS_TB, F.BLOCOS_F, F.BLOCOS_F["ss"]
    blocos, (X0, Y0, X1, Y1), ms, ordem = _blocos_tb(Q)
    w, h = X1 - X0, Y1 - Y0
    s, d_ = b["sombra"], b["sombra"]["dist_m"] * Q.px_m * k

    def reduzir(a):
        return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    fator = np.ones((h, w), np.float32)
    cr = max(1, int(round(q["cresce_m"] * Q.px_m * k)))
    for j, i in enumerate(ordem):
        mf = ms[i]
        a = reduzir(mf)
        antes, depois = [ms[t] for t in ordem[:j]], [ms[t] for t in ordem[j + 1:]]
        baixo = reduzir(np.maximum.reduce(antes)) if antes else np.zeros((h, w), np.float32)
        cima = reduzir(np.maximum.reduce(depois)) if depois else np.zeros((h, w), np.float32)
        dire = reduzir(cv2.GaussianBlur(cv2.warpAffine(mf, np.float32([[1, 0, -d_], [0, 1, d_]]), (w * k, h * k)),
                                        (0, 0), s["sig_m"] * Q.px_m * k)) * s["forca"]
        cont = reduzir(cv2.GaussianBlur(cv2.dilate(mf, np.ones((2 * cr + 1,) * 2, np.uint8)), (0, 0),
                                        q["sig_m"] * Q.px_m * k)) * q["forca"]
        falta = np.clip(cont - dire, 0, 1) * baixo * (1 - a) * (1 - cima)
        fator *= 1 - falta
    out = img.copy()
    out[Y0:Y1, X0:X1] = np.clip(img[Y0:Y1, X0:X1].astype(np.float32) * fator[..., None], 0, 255).astype(np.uint8)
    print(f"    degraus em blocos: a sombra de contato de cada um dos {len(blocos)} blocos sobre os de baixo, nas bordas "
          f"em que a sombra curta não chegava ({int((fator < 0.97).sum())} px)")
    return out


# 23. O elevador (usuário, com o recorte da cabine: "melhore a representação do elevador. me parece que ficou cortado"): no
# Térreo, a cabine era a do Subsolo aprovado colada numa caixa (`ajustes_casab.ELEVADOR`, 1521,0-1591,5 x 769,0-853,0 pt)
# que não é a do PDF do Térreo (1527,1-1606,4 x 766,6-842,4): a cabine saía deslocada para a esquerda e acabava 15 pt
# antes da parede da direita, com o piso antigo em volta. Agora a cabine de aço das Casas A e C (`final3840_casaa.
# elevador`) no desenho do PDF do Térreo (INS_INSTALAÇÕES HIDRÁULICAS): as paredes e o piso da cabine, a porta
# telescópica embaixo (o vão e as 4 folhas), os corrimãos nas três paredes sem porta, o poço entre as paredes do PDF e a
# soleira em inox no vão da parede de baixo, com as faces dos batentes. O rótulo volta na rodada dos rótulos (24).
ELEVADOR_TB = {"externo": (1527.1, 766.6, 1606.4, 842.4), "interno": (1531.6, 771.1, 1601.8, 837.9),
               "vao": (1549.7, 837.9, 1583.7, 842.4),
               "folhas": [(1532.8, 839.6, 1549.7, 841.3), (1546.9, 839.6, 1563.9, 841.3),
                          (1569.6, 839.6, 1586.5, 841.3), (1583.7, 839.6, 1600.7, 841.3)],
               "soleira": (1546.9, 842.4, 1586.6, 853.1), "anel": (1524.2, 759.6, 1609.2, 844.6),
               "corrimaos": ("esquerda", "cima", "direita"), "faces_soleira": "v"}


def elevador_tb(Q, img):
    import final3840_casaa as FA
    guarda = FA.ELEVADOR
    FA.ELEVADOR = dict(FA.ELEVADOR, **ELEVADOR_TB)
    try:
        return FA.elevador(Q, np.ascontiguousarray(img.copy()))
    finally:
        FA.ELEVADOR = guarda


# 24. Os rótulos (usuário, com o recorte da garagem: "revise todos os rótulos para que não fique sobre objetos. quero também
# que eles estejam centralizados"): até aqui cada um ia ao lugar livre mais perto do ponto do PDF (`F.rotulos`), e os
# carros, que não estão nas camadas de obstáculo do PDF, ficavam por baixo do da garagem. Agora a busca parte do meio do
# piso livre do recinto (como os da adega e da despensa da Casa D): o recinto de cada rótulo fechado também pelos vidros,
# caixilhos e batentes (`F.ambientes_rotulos(todas=True)`; sem eles, a suíte se juntava à varanda pela porta de vidro e
# o centro caía lá fora), menos os móveis do PDF e os carros (`carros_pt`), e o centro desse piso livre (se cai fora do
# recinto, o ponto dele mais perto); dali, o lugar livre mais perto, dentro do ambiente (`F.rotulos`, com os carros como
# obstáculo). O texto antigo sai com o fundo da etapa anterior aos rótulos (`Terreo_seta`; a rodada de 26/10 refeita
# sobre ela dá a etapa `Terreo_rotulos` sem 1 px de diferença, então cada texto é conhecido), nos px em que a final está
# entre o texto antigo e esse fundo (a soma das distâncias até `entre` vezes a de um ao outro, mais `tol`: o texto
# esmaecido por uma rodada depois sai; o que foi desenhado por cima, como a cabine nova do elevador, fica). Ficam como
# estão os dos jardins (sobre as plantas, em branco, pedidos de 29/10), os das piscinas (no meio da água, que mudou de
# tom depois) e o SHAFT (no X). Os ambientes abertos para o terreno (o hall de entrada, o deck, a garagem) não fecham:
# o recinto achado passa de `vazou` vezes a área escrita no rótulo, e a busca parte do ponto do PDF, como antes (agora
# com os carros como obstáculo). Na garagem, o ponto do PDF está sobre o carro do meio e o rótulo encostava no capô: a
# busca parte do meio da faixa livre acima dos carros, sobre o do meio (`pontos_px`, entre o tracejado, a 1293 px, e o
# capô, a 1372 px). No quarto do motorista, o piso livre entre a cama e a parede tem ~1 m e o nome numa linha ia até o
# criado-mudo redondo (2 px dele): em duas linhas, no mesmo corpo (`opcoes`, as opções do rótulo, como os ajustes à mão).
ROTULOS_CENTRO_TB = {"manter": ("JARDIM DE INVERNO", "JARDIM", "SPA", "PISCINA", "PRAINHA", "SHAFT"),
                     "entre": 1.15, "tol": 12, "folga_px": 1, "vazou": 1.6, "pontos_px": {"GARAGEM": (2534, 1331)},
                     "opcoes": {"QUARTO MOTORISTA": {"quebra": ["QUARTO", "MOTORISTA"]}}}


def rotulos_centro_tb(Q, img):
    import retoque_1pav_casae as R1
    q, rf = ROTULOS_CENTRO_TB, F.ROTULOS_F
    seta = cv2.imread(str(F.ETAPAS / "Terreo_seta.png"))
    etapa = cv2.imread(str(F.ETAPAS / "Terreo_rotulos.png"))
    rot = F.B.rotulos_casab(Q.pg, Q.p2q2000) + [r for r in R1.rotulos_pdf(Q.pg) if r[0] == "SHAFT"]
    # a rodada de 26/10 de novo, sobre a etapa sem rótulos: o lugar e o corpo de cada um
    cap = {}
    orig = R1.rotulos_ambientes

    def espia(im, rot_, p2q, **kw):
        cap["rot"], cap["aj"] = rot_, kw["ajustes"]
        return orig(im, rot_, p2q, **kw)
    R1.rotulos_ambientes = espia
    try:
        refeita = F.rotulos(Q, seta.copy(), rot, Q.q["ajustes"], granito=F.A.granito(seta, Q.q.get("granito_lum_max", 125)))
    finally:
        R1.rotulos_ambientes = orig
    assert not (refeita != etapa).any(), "a rodada de 26/10 não bate mais com a etapa: os textos antigos não são conhecidos"
    esc = Q.W / 2000
    # o texto de cada rótulo antigo (só ele, sobre a etapa sem rótulos) e a caixa dele
    mascaras = []
    for r1, aj in zip(cap["rot"], cap["aj"]):
        so = orig(seta.copy(), [r1], Q.p2q, escala_desvio=esc, granito=F.A.granito(seta, Q.q.get("granito_lum_max", 125)),
                  ajustes=[aj], cor_granito=R1.ROTULOS["branco"], halo=None)
        mascaras.append(np.abs(so.astype(np.int16) - seta.astype(np.int16)).max(axis=2) > 0)
    # o recinto de cada rótulo (fechado também pelas esquadrias) e o piso livre dele
    pontos0 = rf["pontos"].get(Q.chave, {})
    busca = [Q.p2q(*pontos0[r[0]]) if r[0] in pontos0 else Q.p2q(r[2][0], r[2][1]) for r in cap["rot"]]
    amb = F.ambientes_rotulos(Q, busca, todas=True)
    obst = Q.preencher(lambda d: d.get("layer") in rf["obstaculos"], ss=2, fs=True) > 0.05
    tr = np.zeros(obst.shape, np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in rf["obstaculos"] and d["type"] == "s":
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c))], False, 1, 2)
    obst |= tr.astype(bool)
    for r in F.TERREO["carros_pt"]:
        x0_, y0_, x1_, y1_ = F.ret_q(Q, r)
        obst[y0_:y1_ + 1, x0_:x1_ + 1] = True
    de = np.abs(img.astype(np.int16) - etapa.astype(np.int16)).sum(axis=2)
    ds = np.abs(img.astype(np.int16) - seta.astype(np.int16)).sum(axis=2)
    entre = de + ds <= np.abs(etapa.astype(np.int16) - seta.astype(np.int16)).sum(axis=2) * q["entre"] + q["tol"]
    out = img.copy()
    mover, pontos, obst_pt, n_px = [], dict(pontos0), list(F.TERREO["carros_pt"]), 0
    for i, (r1, m) in enumerate(zip(cap["rot"], mascaras)):
        ys, xs = np.nonzero(m)
        if r1[0] in q["manter"]:
            a, b = Q.q2p(xs.min() - 4, ys.min() - 4), Q.q2p(xs.max() + 4, ys.max() + 4)
            obst_pt.append((a[0], a[1], b[0], b[1]))
            continue
        # o texto antigo sai: o fundo sem rótulos onde a final está entre o texto antigo e esse fundo
        md = cv2.dilate(m.astype(np.uint8), np.ones((2 * q["folga_px"] + 1,) * 2, np.uint8)) > 0
        sai = md & entre
        out[sai] = seta[sai]
        n_px += int(sai.sum())
        if r1[0] in q["pontos_px"]:
            pontos[(r1[0], round(r1[2][0]), round(r1[2][1]))] = Q.q2p(*q["pontos_px"][r1[0]])
            mover.append(r1)
            continue
        reg = amb == i + 1
        area = [float(m_.group(1).replace(",", ".")) for t in r1[1] for m_ in [re.search(r"A:\s*([\d,]+)", t[0])] if m_]
        if area and reg.sum() / Q.px_m ** 2 > q["vazou"] * area[0]:
            mover.append(r1)                        # o recinto vazou para o terreno: a busca parte do ponto do PDF
            continue
        livre = reg & ~obst
        ry, rx = np.nonzero(livre if livre.sum() > 0.05 * reg.sum() else reg)
        cx, cy = rx.mean(), ry.mean()
        if not reg[int(round(cy)), int(round(cx))]:
            ry, rx = np.nonzero(reg)
            j = int(np.argmin((rx - cx) ** 2 + (ry - cy) ** 2))
            cx, cy = rx[j], ry[j]
        pontos[(r1[0], round(r1[2][0]), round(r1[2][1]))] = Q.q2p(cx, cy)
        mover.append(r1)
    obst0 = rf.get("obstaculos_pt", {})
    F.ROTULOS_F = dict(rf, pontos=dict(rf["pontos"], **{Q.chave: pontos}),
                       obstaculos_pt=dict(obst0, **{Q.chave: list(obst0.get(Q.chave, ())) + obst_pt}))
    nomes = {r[0] for r in mover}
    try:
        aj = [a for a in Q.q["ajustes"] if a[0] in nomes]
        for r1 in mover:                            # as opções pedidas (o último ajuste do mesmo rótulo vale)
            if r1[0] in q["opcoes"]:
                cx_, cy_ = Q.p2q(r1[2][0], r1[2][1])
                aj.append((r1[0], (cx_ / esc, cy_ / esc), (0.0, 0.0), q["opcoes"][r1[0]]))
        out = F.rotulos(Q, out, [r for r in rot if r[0] in nomes], aj,
                        granito=F.A.granito(out, Q.q.get("granito_lum_max", 125)))
    finally:
        F.ROTULOS_F = rf
    print(f"    rótulos: {len(mover)} no centro do ambiente (ou no livre mais perto dele), os carros como obstáculo; "
          f"o texto antigo saiu ({n_px} px); {len(cap['rot']) - len(mover)} ficam (jardins, piscinas e SHAFT)")
    return out


# 26. O matelassê nas outras camas (usuário: "aplique o hachurado do cobre leito da cama da suite às demais camas."): o
# cobre-leito da suíte master (`F.cama_master` com `acolchoado`) tem o pesponto em losangos de 12 cm e o relevo de cada
# losango (a luz do alto à direita). Nas outras seis camas (a roupa de cama da biblioteca, `ajustes_casab.CAMAS_B`), o
# mesmo matelassê, multiplicado sobre o edredom: da dobra do lençol aos pés, menos a manta ou faixa bordô atravessada
# (as medidas de `elementos.ROUPA_CAMA` de cada tipo, com `folga_m`), dentro do colchão (a `borda` das camas); os
# travesseiros, as almofadas, a dobra e a manta ficam lisos. O losango na mesma grade do PDF da master.
MATELASSE_TB = {"passo_m": 0.12, "pesponto": 0.045, "largura_pt": 0.35, "acolchoado": CAMA_MASTER_TB["acolchoado"],
                "folga_m": 0.015, "ss": 4, "fora": ("suíte master",)}


def matelasse_camas_tb(Q, img):
    sys.path.insert(0, str(F.B.RAIZ / "_texturas"))
    import elementos
    q, k = MATELASSE_TB, MATELASSE_TB["ss"]
    out = img.astype(np.float32)
    (ax, ay), (bx, by) = Q.q2p(0, 0), Q.q2p(1000, 1000)
    sx_, sy_ = (bx - ax) / 1000, (by - ay) / 1000                 # pt por px
    passo = q["passo_m"] * 56.69
    feitas = []
    for nome, r, cab, tipo in F.B.CAMAS_B["camas"]:
        if nome in q["fora"]:
            continue
        p_ = elementos.ROUPA_CAMA[tipo]
        e = F.B.CAMAS_B["borda"]
        (u0, v0), (u1, v1) = Q.p2q(r[0] + e, r[1] + e), Q.p2q(r[2] - e, r[3] - e)
        X0, Y0, X1, Y1 = int(np.floor(u0)) - 1, int(np.floor(v0)) - 1, int(np.ceil(u1)) + 2, int(np.ceil(v1)) + 2
        w, h = X1 - X0, Y1 - Y0
        xs = X0 + (np.arange(w * k)[None, :] + 0.5) / k
        ys = Y0 + (np.arange(h * k)[:, None] + 0.5) / k
        xpt, ypt = ax + xs * sx_, ay + ys * sy_
        dentro = ((xs >= u0) & (xs <= u1) & (ys >= v0) & (ys <= v1)).astype(np.float32)
        comp = ((u1 - u0) if cab in ("esq", "dir") else (v1 - v0)) / Q.px_m
        X = {"esq": (xs - u0), "dir": (u1 - xs), "baixo": (v1 - ys), "cima": (ys - v0)}[cab] / Q.px_m
        X = np.broadcast_to(X, dentro.shape)
        m0, m1 = p_["manta"][0] * comp, p_["manta"][1] * comp
        f_ = q["folga_m"]
        zona = dentro * (X >= p_["dobra"][1] + f_) * ~((X > m0 - f_) & (X < m1 + f_))
        u, v = (xpt + ypt) / passo, (xpt - ypt) / passo
        lp = q["largura_pt"]
        pesp = np.maximum(np.exp(-((u - np.round(u)) * passo / lp) ** 2), np.exp(-((v - np.round(v)) * passo / lp) ** 2))
        alt = np.minimum(np.abs(u - np.round(u)), np.abs(v - np.round(v))) * 2
        alt = cv2.GaussianBlur(np.clip(alt, 0, 1).astype(np.float32) ** 0.6, (0, 0), 0.3 * k)
        gy, gx = np.gradient(alt * passo * Q.px_m / 56.69 * k)
        fator = (1 - q["pesponto"] * pesp) * (1 + q["acolchoado"] * np.clip(gx * 0.7 - gy * 0.7, -1, 1))
        zona = cv2.GaussianBlur(zona.astype(np.float32), (0, 0), 0.4 * k)
        f = cv2.resize((1 + zona * (fator - 1)).astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
        out[Y0:Y1, X0:X1] *= f[..., None]
        feitas.append(nome)
    print(f"    matelassê da suíte master no edredom das outras camas ({'; '.join(feitas)})")
    return np.clip(out, 0, 255).astype(np.uint8)


def pedidos_tb(img):
    Q = F.Quadro("Terreo")
    antes = img
    img = D.tapete_trama_d(Q, img, q=TAPETES_TB)
    img = sofa_living_tb(Q, img, antes)
    img = poltronas_varanda_tb(Q, img)
    img = poltrona_redonda_tb(Q, img)
    img = encostos_living_tb(Q, img)
    img = D.floreiras_td(Q, img, FLOREIRAS_TB)
    img = mesa_hall_tb(Q, img)
    img = tampos_tb(Q, img)
    img = D.jantar_d(Q, img, img, q=JANTAR_TB)
    img = maquinas_inox_tb(Q, img)
    img = soleiras_tb(Q, img)
    img = linha_ilha_tb(img)
    img = espreguicadeiras_tb(Q, img)
    img = Cc.brises_suites_tc(Q, img, BRISES_SALA_INTIMA_TB)
    img = sala_intima_tb(Q, img)
    img = F.cama_master(Q, img, CAMA_MASTER_TB)
    img = recamiers_tb(Q, img)
    img = pecas_madeira_tb(Q, img)
    img = piso_cortina_tb(Q, img)
    img = marcenaria_tb(Q, img)
    img = estofados_pdf_tb(Q, img, ESTOFADOS_SUITES_TB, "suíte 1 e suíte 2")
    img = matelasse_camas_tb(Q, img)
    img = ordem_blocos_tb(Q, img)
    img = sombra_blocos_tb(Q, img)
    img = elevador_tb(Q, img)
    return rotulos_centro_tb(Q, img)


def revisao_casab_2910(img):
    Q = F.Quadro("Terreo")
    img = folhas_linhas_tb(img)
    img = Cc.brises_suites_tc(Q, vaos_suites_tb(Q, img), BRISES_SUITES_TB)
    img = Cc.cadeiras_contorno_tc(Q, img, CADEIRAS_MESAS_TB, camadas=("ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_MOBILIÁRIO"))
    img = Cc.jogos_varanda_tc(Q, img, JOGOS_VARANDA_TB)
    return rotulos_jardins_tb(Q, img)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", default=str(FINAL_B))
    ap.add_argument("--saida", default=str(FINAL_B))
    ap.add_argument("--adega", action="store_true", help="só a adega com as garrafas na escala (depois da revisão)")
    ap.add_argument("--pedidos", action="store_true", help="os pedidos de 29/10 depois da revisão (sobre d83aee4)")
    a = ap.parse_args()
    out = (adega_tb if a.adega else pedidos_tb if a.pedidos else revisao_casab_2910)(cv2.imread(a.antes))
    cv2.imwrite(a.saida, out)
    print(f"    {a.saida}")

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
# painéis); o marrom, o da mesa da referência 2 (os tampos da varanda); o freijó, o das peças claras.
MADEIRA_TB = {"ss": 8, "veio_m": 0.12, "fio_m": 0.003, "veio": 0.05, "faixas_m": (0.35, 0.025), "faixas": 0.035,
              "chanfro_m": 0.012, "chanfro": 0.12, "aro_px": 0.7, "aro": 0.35, "semente": 2910}
TONS_TB = {"nogueira": (44, 64, 96), "castanho": (92, 124, 160), "marrom": (54, 78, 114), "freijo": (104, 144, 188)}


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
# sob a bancada"): no PDF, os dois quadrados de 0,60 m da ARQ_LAYOUT HUMANIZAÇÃO (a lavadora e a secadora, de frente para
# a esquerda, com a linha da porta em `frente_pt`) sob a bancada; o render os cobria com ela e só a faixa da frente
# aparecia. Entram em inox escovado (o aço da Casa B, `F.PECAS["louca"]["inox"]`), o escovado no comprido (de trás para
# a frente), o painel da frente um tom acima, o dos comandos (atrás, `comandos`, da fração da profundidade) um abaixo,
# o chanfro, o contorno fino e a sombra curta; a bancada fica nas sobras.
INOX_TB = {"maquinas_pt": [(1963.6, 1533.1, 1997.6, 1567.1), (1963.6, 1572.6, 1997.6, 1606.6)], "frente_pt": 1967.0,
           "cor": (196, 199, 202), "escovado": 0.015, "painel": 1.05, "comandos": (0.80, 0.94, 0.94),
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
        M[int(round((b0 - Y0) * ss)):int(round((b1 - Y0) * ss)), int(round((a0 - X0) * ss)):int(round((a1 - X0) * ss))] = 1
        a1x = cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA)
        out = _sombra_piso_tb(out, X0, Y0, a1x, Q.px_m, [F.PECAS["sombra"] | {"dx_m": -F.PECAS["sombra"]["dist_m"],
                                                                             "dy_m": F.PECAS["sombra"]["dist_m"]}])
        risco = cv2.GaussianBlur(rng.normal(0, 1, (h * ss, 1)).astype(np.float32), (0, 0), 0.4 * ss)
        risco = 1 + q["escovado"] * risco / max(float(risco.std()), 1e-6)
        cor = np.float32(q["cor"]) * np.repeat(risco, w * ss, axis=1)[..., None]
        xf = (Q.p2q(q["frente_pt"], 0)[0] - X0) * ss
        cor[:, :int(round(xf))] *= q["painel"]
        c0, c1, fc = q["comandos"]
        cor[:, int(round((a0 - X0 + c0 * (a1 - a0)) * ss)):int(round((a0 - X0 + c1 * (a1 - a0)) * ss))] *= fc
        cor *= _relevo_tb(M, Q.px_m, ss)[..., None]
        cor = cor * (1 - q["aro"] * (M - cv2.erode(M, np.ones((ss // 2 + 1,) * 2, np.uint8))))[..., None] \
            + np.float32(q["contorno"]) * q["aro"] * (M - cv2.erode(M, np.ones((ss // 2 + 1,) * 2, np.uint8)))[..., None]
        out = _pintar_tb(out, X0, Y0, w, h, ss, M, cor)
    print(f"    área de serviço: as {len(q['maquinas_pt'])} máquinas sob a bancada em inox escovado")
    return out


# 6. A janela da pia da cozinha (usuário: "corrigir as folhas de vidro da pia da cozinha. são apenas duas folhas"): no
# PDF, duas folhas de correr (a da esquerda no plano de dentro, a da direita no de fora); no render, na metade da
# direita, entre a borda da bancada e a folha, ficou um tubo claro (o caixilho antigo), que lia como uma terceira folha.
# As linhas dele (`faixa_px`, entre os batentes) recebem o granito da bancada logo acima da linha da borda dela, em
# espelho e vai e vem nas linhas `fonte_y` (mais acima fica a borda das cubas), como na metade da esquerda.
JANELA_PIA_TB = {"faixa_px": (1685, 1666, 1777, 1673), "fonte_y": (1661, 1665)}


def janela_pia_tb(img):
    q = JANELA_PIA_TB
    out = img.copy()
    x0, y0, x1, y1 = q["faixa_px"]
    a, b = q["fonte_y"]
    vaivem = list(range(b - 1, a - 1, -1)) + list(range(a + 1, b - 1))
    for i, y in enumerate(range(y0, y1)):
        out[y, x0:x1] = img[vaivem[i % len(vaivem)], x0:x1]
    print(f"    janela da pia da cozinha: o caixilho antigo entre a bancada e as folhas sai ({x1 - x0}x{y1 - y0} px); "
          f"ficam as duas folhas")
    return out


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
     "pt": (831.4, 920.5, 868.8, 945.0), "tom": "nogueira"},
    {"nome": "criado-mudo da suíte master, à direita", "camada": "ARQ_LOUÇAS E METAIS",
     "pt": (989.1, 920.5, 1026.5, 945.0), "tom": "nogueira"},
    {"nome": "mesa de apoio do recamier da esquerda", "camada": "ARQ_MOBILIÁRIO", "pt": (851.1, 649.3, 885.1, 672.0),
     "tom": "freijo", "vaos": [(879.5, 651.6, 882.9, 669.7)], "sobre": True},
    {"nome": "mesa de apoio do recamier da direita", "camada": "ARQ_MOBILIÁRIO", "pt": (953.0, 652.5, 987.0, 675.2),
     "tom": "freijo", "vaos": [(955.2, 654.8, 958.6, 672.9)], "sobre": True}]
FRISO_TB = {"larg_px": 0.45, "forca": 0.30, "vao": 0.45}


def pecas_madeira_tb(Q, img, nomes=None):
    q, ss = PECAS_MADEIRA_TB, MADEIRA_TB["ss"]
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
        cor = np.float32(TONS_TB[p["tom"]]) * _veio_tb(rng, h * ss, w * ss, 0.0 if largo else 90.0, Q.px_m, ss)[..., None]
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
        print(f"    {p['nome']}: em {p['tom']}, com o veio, o chanfro e a sombra no piso")
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


# 10. A cama da suíte master (o mesmo pedido, no cobre-leito): a cama do motor (`F.cama_master`) refeita sobre a final,
# só ela (o banco aos pés e a sombra de fora ficam): o cobre-leito em matelassê com o relevo de cada losango
# (`acolchoado`), e o rolo do cobre-leito dobrado no mesmo matelassê, com mais volume nas pontas (as dobras soltas do
# desenho do PDF, que liam como "calombos" chapados, passam a ter a queda do tecido).
CAMA_MASTER_TB = dict(F.CAMA_MASTER_F, so_cama=True, acolchoado=0.06, rolo_vol=(0.05, 0.24))


def pedidos_tb(img):
    Q = F.Quadro("Terreo")
    img = D.tapete_trama_d(Q, img, q=TAPETES_TB)
    img = mesa_hall_tb(Q, img)
    img = tampos_tb(Q, img)
    img = D.jantar_d(Q, img, img, q=JANTAR_TB)
    img = maquinas_inox_tb(Q, img)
    img = janela_pia_tb(img)
    img = F.cama_master(Q, img, CAMA_MASTER_TB)
    img = recamiers_tb(Q, img)
    return pecas_madeira_tb(Q, img)


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

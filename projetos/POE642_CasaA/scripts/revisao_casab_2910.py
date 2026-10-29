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


def revisao_casab_2910(img):
    Q = F.Quadro("Terreo")
    img = folhas_linhas_tb(img)
    img = Cc.brises_suites_tc(Q, img, BRISES_SUITES_TB)
    img = Cc.cadeiras_contorno_tc(Q, img, CADEIRAS_MESAS_TB, camadas=("ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_MOBILIÁRIO"))
    img = Cc.jogos_varanda_tc(Q, img, JOGOS_VARANDA_TB)
    return rotulos_jardins_tb(Q, img)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", default=str(FINAL_B))
    ap.add_argument("--saida", default=str(FINAL_B))
    a = ap.parse_args()
    out = revisao_casab_2910(cv2.imread(a.antes))
    cv2.imwrite(a.saida, out)
    print(f"    {a.saida}")

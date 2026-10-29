"""Casa A: pedidos de 29/10/26 na revisão das três plantas, como retoques locais sobre as finais aprovadas.

1º Pavimento, as portas das suítes para as varandas (usuário, durante a revisão: "note que é o mesmo caso da casa B: 4
folhas na varanda, sendo duas de vidro e duas de bronze. Essas precisam estar representadas corretamente."; depois: "e que
cobrem o banho master: as de bronze. percebeu?"). No PDF, como nas Casas B e C, cada folha são duas tiras brancas de
1,4 pt da ARQ_PAREDE, coladas, em dois planos: o de fora (do lado da varanda) e o de dentro. A final tinha as quatro em
vidro, com os caixilhos antigos do render entre os planos. Como na Casa B (`revisao_casab_2910`): a faixa entre os dois
planos refeita com o piso do quarto (`piso_entre_folhas_ta`), a folha de dentro em vidro fino e as de fora em brise de
bronze escovado (`final3840_casac.brises_suites_tc`). Suítes 1, 2 e 3 e a suíte master (o quarto); na suíte master, as
duas folhas de fora que seguem na frente do banho master (do lado da floreira, sem folha de dentro) também em bronze.

Uso (uma vez, sobre a final aprovada do 1º Pavimento):
  python3 revisao_casaa_2910.py --portas [--antes <png>] [--saida <png>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casaa as FA                    # noqa: E402
import final3840_casac as Cc                    # noqa: E402
import revisao_casab_2910 as RB                 # noqa: E402

FINAL_1PAV = FA.CASA / "renders" / "POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png"

# As folhas (pt do PDF), em pares (a de fora, a de dentro) por trecho. Suítes 3, 2 e master: a varanda à esquerda, o
# quarto à direita (lado +1); suíte 1: a varanda à direita (lado -1). Todas nas paredes verticais (eixo x).
VAOS_SUITES_TA = dict(RB.VAOS_SUITES_TB, portas={
    "Suíte 3": ("x", 1, [((1389.1, 565.9, 1391.9, 670.2), (1403.3, 565.9, 1406.1, 670.2)),
                         ((1391.9, 674.8, 1394.8, 779.1), (1400.4, 674.8, 1403.3, 779.1))]),
    "Suíte 2": ("x", 1, [((1391.9, 1181.8, 1394.8, 1271.6), (1403.3, 1189.5, 1406.1, 1275.4)),
                         ((1389.1, 1276.1, 1391.9, 1365.9), (1400.4, 1280.0, 1403.3, 1365.9))]),
    "Suíte Master": ("x", 1, [((1151.0, 1399.3, 1153.8, 1487.0), (1165.2, 1399.3, 1168.0, 1497.9)),
                              ((1153.8, 1491.6, 1156.7, 1579.3), (1162.3, 1502.5, 1165.2, 1601.1))]),
    "Suíte 1": ("x", -1, [((2301.9, 1496.2, 2304.7, 1590.4), (2293.4, 1498.5, 2296.2, 1591.5)),
                          ((2304.7, 1594.9, 2307.5, 1689.0), (2290.5, 1596.0, 2293.4, 1689.0))])},
    vidro_fora=())

BRISES_SUITES_TA = dict(Cc.BRISES_SUITES_TC, folhas_pt={
    "Suíte 3": [(1389.1, 565.9, 1391.9, 670.2), (1391.9, 674.8, 1394.8, 779.1)],
    "Suíte 2": [(1391.9, 1181.8, 1394.8, 1271.6), (1389.1, 1276.1, 1391.9, 1365.9)],
    "Suíte Master": [(1151.0, 1399.3, 1153.8, 1487.0), (1153.8, 1491.6, 1156.7, 1579.3)],
    "Banho Master": [(1153.8, 1588.4, 1156.7, 1676.1), (1151.0, 1680.6, 1153.8, 1768.4)],
    "Suíte 1": [(2301.9, 1496.2, 2304.7, 1590.4), (2304.7, 1594.9, 2307.5, 1689.0)]})


# O piso entre as folhas (usuário: "e atenção ao piso entre as folhas de vidro e de bronze"). Na Casa B, a faixa entre os
# planos ia na cor média da madeira de cada linha; aqui ela ficava chapada (as réguas do 1º Pavimento correm no comprido
# da faixa, que é estreita) e os encontros das folhas guardavam os nós dos caixilhos antigos. Então, em cada porta, a
# faixa inteira, da face de fora da folha de fora à de dentro da folha de dentro (com `folga_dentro_px` para o quarto, que
# leva os nós), em todo o vão (do começo da primeira folha ao fim da última), recebe um bloco de réguas do próprio quarto,
# limpo, do mesmo tamanho (ali junto, a cortina cobre o piso em muitas linhas). Do lado de fora, `folga_fora_px` px junto
# à face recebem o piso da varanda da mesma linha, um pouco mais longe (`fora_de_px`), no lugar dos fios do caixilho
# antigo. Depois, o vidro fino de dentro e o bronze de fora.
PISO_ENTRE_FOLHAS_TA = {"folga_dentro_px": 3, "folga_fora_px": 3, "fora_de_px": 8, "busca_px": 260, "tol_cor": 28}


def piso_entre_folhas_ta(Q, img, q=None, p=None):
    q, p = q or VAOS_SUITES_TA, p or PISO_ENTRE_FOLHAS_TA
    out = img.copy()
    for nome, (eixo, lado, pares) in q["portas"].items():
        def px(r):
            (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
            return a, b, c, d
        fora = [px(f) for f, _ in pares]
        dentro = [px(d) for _, d in pares]
        L0 = int(np.floor(min(r[1] for r in fora + dentro)))
        L1 = int(np.ceil(max(r[3] for r in fora + dentro)))
        if lado > 0:                                              # o quarto à direita, a varanda à esquerda
            t_fora = int(np.floor(min(r[0] for r in fora)))
            z0, z1 = t_fora, int(np.ceil(max(r[2] for r in dentro))) + p["folga_dentro_px"]
        else:
            t_fora = int(np.ceil(max(r[2] for r in fora)))
            z0, z1 = int(np.floor(min(r[0] for r in dentro))) - p["folga_dentro_px"], t_fora
        w = z1 - z0
        # a fonte: um bloco de réguas limpo do próprio quarto, do tamanho da faixa (`w` x o vão), procurado no piso livre ao
        # lado (`busca_px` para dentro e para cima e para baixo): só madeira do piso, a até `tol_cor` da cor mediana dela
        # (fora a cortina, a sombra dela, os tapetes e as camas); o mais limpo e, entre os limpos, o mais perto da porta
        H = L1 - L0
        y0b, y1b = max(0, L0 - p["busca_px"]), min(out.shape[0], L1 + p["busca_px"])
        x0b, x1b = (z1, z1 + p["busca_px"]) if lado > 0 else (z0 - p["busca_px"], z0)
        reg = out[y0b:y1b, x0b:x1b]
        mad = RB._madeira(reg)
        med = np.median(reg[mad], axis=0)
        mad &= np.abs(reg.astype(np.int16) - med).max(axis=-1) <= p["tol_cor"]
        frac = cv2.boxFilter(mad.astype(np.float32), -1, (w, H), anchor=(0, 0), normalize=True,
                             borderType=cv2.BORDER_CONSTANT)[:reg.shape[0] - H + 1, :reg.shape[1] - w + 1]
        yy, xx = np.mgrid[0:frac.shape[0], 0:frac.shape[1]]
        dist = np.abs(yy + y0b - L0) + (xx if lado > 0 else frac.shape[1] - 1 - xx)
        nota = np.where(frac >= frac.max() - 0.01, -dist, -1e9)
        i, j = np.unravel_index(np.argmax(nota), nota.shape)
        bloco = reg[i:i + H, j:j + w].copy()
        best = (x0b + j, float(frac[i, j]))
        out[L0:L1, z0:z1] = bloco
        k, de = p["folga_fora_px"], p["fora_de_px"]
        if lado > 0:
            out[L0:L1, t_fora - k:t_fora] = out[L0:L1, t_fora - k - de:t_fora - de]
        else:
            out[L0:L1, t_fora:t_fora + k] = out[L0:L1, t_fora + de:t_fora + k + de]
        print(f"    {nome}: o piso entre as folhas com um bloco de réguas do quarto ({best[1]:.0%} de madeira limpa)")
    return out


def vidros_dentro_ta(Q, img, q=None):
    """As folhas de dentro em vidro fino (o miolo claro e as bordas cinza), como na Casa B."""
    q = q or VAOS_SUITES_TA
    out, k, eb = img.copy(), q["ss"], q["larg_borda_px"]
    for nome, (eixo, lado, pares) in q["portas"].items():
        for _, r in pares:
            (a0, s0), (a1, s1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
            X0, Y0, X1, Y1 = int(np.floor(a0)) - 2, int(np.floor(s0)) - 2, int(np.ceil(a1)) + 2, int(np.ceil(s1)) + 2
            h, w = Y1 - Y0, X1 - X0

            def ret(x0_, y0_, x1_, y1_):
                m = np.zeros((h * k, w * k), np.uint8)
                cv2.rectangle(m, (int(round((x0_ - X0) * k)), int(round((y0_ - Y0) * k))),
                              (int(round((x1_ - X0) * k)) - 1, int(round((y1_ - Y0) * k)) - 1), 255, -1)
                return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
            A, M = ret(a0, s0, a1, s1), ret(a0 + eb, s0 + eb, a1 - eb, s1 - eb)
            reg = out[Y0:Y1, X0:X1].astype(np.float32)
            reg = reg * (1 - A) + np.float32(q["borda"]) * A
            reg = reg * (1 - M) + np.float32(q["vidro"]) * M
            out[Y0:Y1, X0:X1] = np.clip(reg, 0, 255).astype(np.uint8)
    return out


def portas_suites_ta(Q, img):
    img = vidros_dentro_ta(Q, piso_entre_folhas_ta(Q, img))
    return Cc.brises_suites_tc(Q, img, BRISES_SUITES_TA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portas", action="store_true")
    ap.add_argument("--antes", type=Path, default=FINAL_1PAV)
    ap.add_argument("--saida", type=Path, default=FINAL_1PAV)
    a = ap.parse_args()
    if not a.portas:
        ap.error("indique o pedido: --portas")
    Q = FA.QuadroA("1Pavimento")
    img = cv2.imread(str(a.antes))
    out = portas_suites_ta(Q, img)
    cv2.imwrite(str(a.saida), out)
    print(a.saida)


if __name__ == "__main__":
    main()

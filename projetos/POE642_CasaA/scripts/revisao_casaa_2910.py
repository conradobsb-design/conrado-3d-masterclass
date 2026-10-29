"""Casa A: pedidos de 29/10/26 na revisão das três plantas, como retoques locais sobre as finais aprovadas.

1º Pavimento, as portas das suítes para as varandas (usuário, durante a revisão: "note que é o mesmo caso da casa B: 4
folhas na varanda, sendo duas de vidro e duas de bronze. Essas precisam estar representadas corretamente."; depois: "e que
cobrem o banho master: as de bronze. percebeu?"). No PDF, como nas Casas B e C, cada folha são duas tiras brancas de
1,4 pt da ARQ_PAREDE, coladas, em dois planos: o de fora (do lado da varanda) e o de dentro. A final tinha as quatro em
vidro, com os caixilhos antigos do render entre os planos. Como na Casa B (`revisao_casab_2910`): a faixa entre os dois
planos refeita com o piso do quarto (`piso_entre_folhas_ta`), a folha de dentro em vidro fino (`vidros_dentro_ta`) e as
de fora em brise de bronze escovado (`bronzes_fora_ta`, o bronze de `final3840_casac.brises_suites_tc`). Suítes 1, 2 e 3 e a suíte master (o quarto); na suíte master, as
duas folhas de fora que seguem na frente do banho master (do lado da floreira, sem folha de dentro) também em bronze.

Depois, as junções (usuário: "Preciso que as portas de vidro tanto de vidro quanto de bronze tenhas as junções, na
origem e na extremidade conectando as duas de seus respectivos matérias (vidro com vidro e bronze com bronze)"): as peças
do PDF entre o batente e a primeira folha, no encontro das duas folhas e entre a última folha e o batente, no material do
plano (`JUNCOES_TA`). Cada plano sai como uma peça só: as folhas e as junções na mesma máscara, com um contorno só.

Uso (sobre a final aprovada do 1º Pavimento, a de antes das portas: a do commit 29588a5, `git show 29588a5:projetos/
POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png`):
  python3 revisao_casaa_2910.py --portas --antes <png da final aprovada> [--saida <png>]
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

# As folhas de fora, em bronze, por plano. Na suíte master, o plano de fora segue do quarto para o banho master: as duas
# folhas do quarto e as duas da frente do banho (do lado da floreira, sem folha de dentro).
BRISES_SUITES_TA = dict(Cc.BRISES_SUITES_TC, folhas_pt={
    "Suíte 3": [(1389.1, 565.9, 1391.9, 670.2), (1391.9, 674.8, 1394.8, 779.1)],
    "Suíte 2": [(1391.9, 1181.8, 1394.8, 1271.6), (1389.1, 1276.1, 1391.9, 1365.9)],
    "Suíte Master": [(1151.0, 1399.3, 1153.8, 1487.0), (1153.8, 1491.6, 1156.7, 1579.3),
                     (1153.8, 1588.4, 1156.7, 1676.1), (1151.0, 1680.6, 1153.8, 1768.4)],
    "Suíte 1": [(2301.9, 1496.2, 2304.7, 1590.4), (2304.7, 1594.9, 2307.5, 1689.0)]})

# As junções (pt do PDF): as peças de 2,8 x 4,5 pt da ARQ_PAREDE em cada plano, na origem (do batente à primeira folha),
# no encontro das duas folhas (as duas peças lado a lado, uma sob o fim de uma folha e outra sobre o começo da outra:
# o degrau de um trilho para o outro) e na extremidade (da última folha ao batente). Na suíte master, entre a folha de
# fora do quarto e a do banho, duas peças em fila (1579,3 a 1588,4); na suíte 1 e na suíte 2, a peça da origem de fora
# encosta no guarda-corpo de vidro da varanda, que segue (a peça ao lado dela, sob o guarda-corpo, fica com ele).
# `batentes`: as faces dos batentes (y, pt) de cima e de baixo, até onde vai o piso entre as folhas.
JUNCOES_TA = {
    "Suíte 3": {"fora": [(1389.1, 561.4, 1391.9, 565.9), (1389.1, 670.2, 1394.8, 674.8), (1391.9, 779.1, 1394.8, 783.6)],
                "dentro": [(1403.3, 561.4, 1406.1, 565.9), (1400.4, 670.2, 1406.1, 674.8),
                           (1400.4, 779.1, 1403.3, 783.6)],
                "batentes": (561.4, 783.6)},
    "Suíte 2": {"fora": [(1391.9, 1177.2, 1394.8, 1181.8), (1389.1, 1271.6, 1394.8, 1276.1),
                         (1389.1, 1365.9, 1391.9, 1370.4)],
                "dentro": [(1403.3, 1185.0, 1406.1, 1189.5), (1400.4, 1275.4, 1406.1, 1280.0),
                           (1400.4, 1365.9, 1403.3, 1370.4)],
                "batentes": (1185.0, 1370.4)},
    "Suíte Master": {"fora": [(1151.0, 1394.8, 1153.8, 1399.3), (1151.0, 1487.0, 1156.7, 1491.6),
                              (1153.8, 1579.3, 1156.7, 1588.4), (1151.0, 1676.1, 1156.7, 1680.6),
                              (1151.0, 1768.4, 1153.8, 1772.9)],
                     "dentro": [(1165.2, 1394.8, 1168.0, 1399.3), (1162.3, 1497.9, 1168.0, 1502.5),
                                (1162.3, 1601.1, 1165.2, 1605.7)],
                     "batentes": (1394.8, 1605.7)},
    "Suíte 1": {"fora": [(2301.9, 1487.2, 2304.7, 1496.2), (2301.9, 1590.4, 2307.5, 1594.9),
                         (2304.7, 1689.0, 2307.5, 1693.5)],
                "dentro": [(2293.4, 1494.0, 2296.2, 1498.5), (2290.5, 1591.5, 2296.2, 1596.0),
                           (2290.5, 1689.0, 2293.4, 1693.5)],
                "batentes": (1494.0, 1693.5)}}


# O piso entre as folhas (usuário: "e atenção ao piso entre as folhas de vidro e de bronze"). Na Casa B, a faixa entre os
# planos ia na cor média da madeira de cada linha; aqui ela ficava chapada (as réguas do 1º Pavimento correm no comprido
# da faixa, que é estreita) e os encontros das folhas guardavam os nós dos caixilhos antigos. Então, em cada porta, a
# faixa inteira, da face de fora da folha de fora à de dentro da folha de dentro (com `folga_dentro_px` para o quarto, que
# leva os nós), em todo o vão (do começo da primeira folha ao fim da última), recebe um bloco de réguas do próprio quarto,
# limpo, do mesmo tamanho (ali junto, a cortina cobre o piso em muitas linhas). Do lado de fora, `folga_fora_px` px junto
# à face recebem o piso da varanda da mesma linha, um pouco mais longe (`fora_de_px`), no lugar dos fios do caixilho
# antigo. Depois, o vidro fino de dentro e o bronze de fora.
PISO_ENTRE_FOLHAS_TA = {"folga_dentro_px": 3, "folga_fora_px": 3, "fora_de_px": 8, "busca_px": 260, "tol_cor": 28}


def piso_entre_folhas_ta(Q, img, q=None, p=None, jt=None):
    q, p, jt = q or VAOS_SUITES_TA, p or PISO_ENTRE_FOLHAS_TA, jt or JUNCOES_TA
    out = img.copy()
    for nome, (eixo, lado, pares) in q["portas"].items():
        def px(r):
            (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
            return a, b, c, d
        fora = [px(f) for f, _ in pares]
        dentro = [px(d) for _, d in pares]
        # no comprido, das folhas aos batentes (as junções da origem e da extremidade entram no piso limpo, sem os nós
        # dos caixilhos antigos)
        b0, b1 = (Q.p2q(0, y)[1] for y in jt[nome]["batentes"])
        L0 = int(np.floor(min([r[1] for r in fora + dentro] + [b0])))
        L1 = int(np.ceil(max([r[3] for r in fora + dentro] + [b1])))
        if lado > 0:                                              # o quarto à direita, a varanda à esquerda
            t_fora = int(np.floor(min(r[0] for r in fora)))
            z0, z1 = t_fora, int(np.ceil(max(r[2] for r in dentro))) + p["folga_dentro_px"]
        else:
            t_fora = int(np.ceil(max(r[2] for r in fora)))
            z0, z1 = int(np.floor(min(r[0] for r in dentro))) - p["folga_dentro_px"], t_fora
        w = z1 - z0
        # a fonte: um bloco de réguas limpo do próprio quarto, do tamanho da faixa (`w` x o vão), procurado no piso livre ao
        # lado (`busca_px` para dentro e para cima e para baixo): só madeira do piso, a até `tol_cor` da cor mediana dela
        # (fora a cortina, a sombra dela, os tapetes e as camas); o mais limpo e, entre os limpos, o mais perto da porta. Os
        # poucos px dele que não são madeira limpa (com a faixa até os batentes, o bloco é mais comprido e já não acha
        # 100%) são refeitos com a madeira em volta
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
        ruim = (~mad[i:i + H, j:j + w]).astype(np.uint8) * 255          # o pouco que não é madeira limpa, refeito
        if ruim.any():                                                     # com a madeira em volta
            bloco = cv2.inpaint(bloco, ruim, 2, cv2.INPAINT_TELEA)
        best = (x0b + j, float(frac[i, j]))
        out[L0:L1, z0:z1] = bloco
        k, de = p["folga_fora_px"], p["fora_de_px"]
        if lado > 0:
            out[L0:L1, t_fora - k:t_fora] = out[L0:L1, t_fora - k - de:t_fora - de]
        else:
            out[L0:L1, t_fora:t_fora + k] = out[L0:L1, t_fora + de:t_fora + k + de]
        print(f"    {nome}: o piso entre as folhas com um bloco de réguas do quarto ({best[1]:.0%} de madeira limpa)")
    return out


def _plano_ss(Q, rects, k, folga=0.0, margem=6):
    """A máscara de um plano de folhas (as folhas e as junções, unidas), em `k` x a resolução, e a janela dela (px)."""
    caixas = []
    for r in rects:
        (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        caixas.append((a - folga, b - folga, c + folga, d + folga))
    X0 = int(np.floor(min(c[0] for c in caixas))) - margem
    Y0 = int(np.floor(min(c[1] for c in caixas))) - margem
    X1 = int(np.ceil(max(c[2] for c in caixas))) + margem
    Y1 = int(np.ceil(max(c[3] for c in caixas))) + margem
    m = np.zeros(((Y1 - Y0) * k, (X1 - X0) * k), np.uint8)
    for a, b, c, d in caixas:
        cv2.rectangle(m, (int(round((a - X0) * k)), int(round((b - Y0) * k))),
                      (int(round((c - X0) * k)) - 1, int(round((d - Y0) * k)) - 1), 255, -1)
    return m, (X0, Y0, X1, Y1), caixas


def _baixa(m, box):
    X0, Y0, X1, Y1 = box
    return cv2.resize(m.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)


def _erode(m, r):
    return cv2.erode(m, np.ones((2 * r + 1, 2 * r + 1), np.uint8)) if r > 0 else m


def vidros_dentro_ta(Q, img, q=None, j=None):
    """O plano de dentro em vidro fino (o miolo claro e as bordas cinza), como na Casa B: as duas folhas e as junções
    de vidro (`JUNCOES_TA`) numa peça só, com a borda em volta dela toda."""
    q, j = q or VAOS_SUITES_TA, j or JUNCOES_TA
    out, k = img.copy(), q["ss"]
    for nome, (eixo, lado, pares) in q["portas"].items():
        m, box, _ = _plano_ss(Q, [d for _, d in pares] + j[nome]["dentro"], k)
        A = _baixa(m, box)[..., None]
        M = _baixa(_erode(m, int(round(q["larg_borda_px"] * k))), box)[..., None]
        X0, Y0, X1, Y1 = box
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg = reg * (1 - A) + np.float32(q["borda"]) * A
        reg = reg * (1 - M) + np.float32(q["vidro"]) * M
        out[Y0:Y1, X0:X1] = np.clip(reg, 0, 255).astype(np.uint8)
    return out


def bronzes_fora_ta(Q, img, q=None, j=None):
    """O plano de fora em brise de bronze escovado, como `final3840_casac.brises_suites_tc` (o bronze com os fios do
    escovado no comprido, o brilho no meio de cada folha, o contorno escuro e a sombra curta), mas com as folhas e as
    junções de bronze (`JUNCOES_TA`) numa peça só: o contorno corre em volta dela toda, e as junções, em bronze, ficam
    sem o brilho (são as peças entre as folhas, não folhas)."""
    import retoque_1pav_casae as RE
    q, j = q or BRISES_SUITES_TA, j or JUNCOES_TA
    k, f = q["ss"], q["folga_px"]
    rng = np.random.default_rng(q["semente"])
    out = img.copy()
    for nome, folhas in q["folhas_pt"].items():
        m, box, caixas = _plano_ss(Q, folhas + j[nome]["fora"], k, folga=f)
        X0, Y0, X1, Y1 = box
        h, w = Y1 - Y0, X1 - X0
        A = _baixa(m, box)
        s = q["sombra"]
        out = RE.sombra(out, A, box, s["desloc"], s["sigma"], s["forca"])
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        ruido = rng.normal(size=(h, w)).astype(np.float32)              # os fios do escovado, no comprido (y)
        ruido = cv2.GaussianBlur(ruido, (0, 0), sigmaX=0.3, sigmaY=6.0)
        ruido /= max(float(ruido.std()), 1e-6)
        cor = np.float32(q["bronze"]) * (1 + q["escovado"] * ruido)[..., None]
        reg = reg * (1 - A[..., None]) + cor * A[..., None]
        L = np.zeros_like(m)                                             # o brilho no meio de cada folha
        for a, b, c, d in caixas[:len(folhas)]:
            xm = (a + c) / 2
            cv2.line(L, (int(round((xm - X0) * k)), int(round((b - Y0) * k))),
                     (int(round((xm - X0) * k)), int(round((d - Y0) * k))), 255,
                     max(1, int(round(q["larg_brilho_px"] * k))))
        L = _baixa(L, box)[..., None]
        reg = reg * (1 - L) + np.float32(q["brilho"]) * L
        e = max(1, int(round(q["larg_borda_px"] * k)))                   # o contorno, centrado na borda da peça
        B = cv2.dilate(m, np.ones((2 * (e // 2) + 1,) * 2, np.uint8)) & ~_erode(m, e - e // 2)
        B = _baixa(B, box)[..., None]
        reg = reg * (1 - B) + np.float32(q["borda"]) * B
        out[Y0:Y1, X0:X1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    portas das suítes: o plano de fora em bronze escovado e o de dentro em vidro, cada um com as junções "
          f"no próprio material ({', '.join(q['folhas_pt'])})")
    return out


def portas_suites_ta(Q, img):
    img = vidros_dentro_ta(Q, piso_entre_folhas_ta(Q, img))
    return bronzes_fora_ta(Q, img)


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

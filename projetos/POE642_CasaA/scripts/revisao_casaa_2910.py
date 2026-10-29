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
import final3840_casad as D                     # noqa: E402
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


# ----------------------------------------------------------------------------------------------------------------------
# Os itens da revisão de 29/10/26 (mapas `renders/POE642_CasaA_PH_<pavimento>_2910_revisao_mapa.jpg`). OK do usuário:
# "Itens de 1 a 10 ok."; no item 4: "No item 4, preencha com tom Branco sem tracejado." Retoques locais sobre as finais
# (a do Térreo saiu do `final3840_casaa_terreo.py` e recebeu depois os boxes e as bordas; o cache das etapas não está
# mais aqui). Os rótulos que mudam são tirados da imagem pelo próprio desenho deles: o rótulo é desenhado de novo, sozinho,
# com as mesmas opções do `final3840_casaa_terreo.rotulos`, e o alfa dele separa o texto do fundo (`_sem_rotulo`).

FINAL_TERREO = FA.CASA / "renders" / "POE642_CasaA_PH_Terreo_final_rotulos.png"
FINAL_SUBSOLO = FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_final_rotulos.png"


def _rotulos_pav(Q):
    """Os rótulos do PDF e os desvios de cada pavimento, como nas etapas `rotulos` dos motores."""
    import retoque_1pav_casae as R1
    q = FA.A.PAVIMENTOS[Q.chave]
    rot = [r for r in R1.rotulos_pdf(Q.pg) if r[0] in q.get("incluir", ()) or not any(f in r[0] for f in FA.A.FORA)]
    if Q.chave == "Terreo":
        import final3840_casaa_terreo as T
        return rot, [T.AJUSTES_T.get(a[0], a) for a in q["ajustes"]]
    if Q.chave == "1Pavimento":
        import final3840_casaa_1pav as P
        return rot, [P.AJUSTES_1P.get(a[0], a) for a in q["ajustes"]] + [
            a for n, a in P.AJUSTES_1P.items() if n not in [b[0] for b in q["ajustes"]]]
    return rot, q["ajustes"]


def _rotulo(Q, rot, nome, perto_px):
    """O rótulo `nome` do PDF mais perto de `perto_px` (há dois JARDIM)."""
    cands = [r for r in rot if r[0] == nome]
    return min(cands, key=lambda r: np.hypot(*np.subtract(Q.p2q(*r[2]), perto_px)))


def _alfa_rotulo(Q, forma, r, ajustes):
    """O alfa (0..1, no quadro) do rótulo r, desenhado sozinho como na final."""
    import retoque_1pav_casae as R1
    cor = R1.ROTULOS["cor"]
    R1.ROTULOS["cor"] = (255, 255, 255)
    try:
        aj = [(a[0], a[1], a[2], dict(a[3], cor=(255, 255, 255))) if len(a) > 3 and isinstance(a[3], dict) else a
              for a in ajustes]                                    # o alfa sai em branco, qualquer que seja a cor
        o = R1.rotulos_ambientes(np.zeros(forma + (3,), np.uint8), [r], Q.p2q, escala_desvio=FA.A.LARGURA / 2000,
                                 granito=None, ajustes=aj)
    finally:
        R1.ROTULOS["cor"] = cor
    return o[..., 1].astype(np.float32) / 255


def _caixa(a, limiar=0.02):
    ys, xs = np.nonzero(a > limiar)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _sem_rotulo(img, a, cor, cheio=0.85):
    """O fundo sob o rótulo de alfa a e cor `cor`: (img - cor a) / (1 - a); onde o texto é cheio (a > `cheio`), o fundo
    vem do entorno (inpaint)."""
    x0, y0, x1, y1 = _caixa(a)
    x0, y0, x1, y1 = x0 - 4, y0 - 4, x1 + 4, y1 + 4
    reg, al = img[y0:y1, x0:x1].astype(np.float32), a[y0:y1, x0:x1, None]
    B = np.clip((reg - np.float32(cor) * al) / np.maximum(1 - al, 1e-3), 0, 255).astype(np.uint8)
    B = cv2.inpaint(B, ((al[..., 0] > cheio) * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    out = img.copy()
    out[y0:y1, x0:x1] = B
    return out


def _com_rotulo(img, a, cor):
    return np.clip(img * (1 - a[..., None]) + np.float32(cor) * a[..., None], 0, 255).astype(np.uint8)


# 1. O JARDIM (4,79 m²): o tracejado da projeção da cobertura passa entre as duas linhas do rótulo. Ele sai só sob o texto,
# como na Casa B: cada traço (os px claros e neutros, `branco`, numa faixa de `faixa_px` em volta da linha dele) que
# encosta na caixa do texto mais `folga_px` sai inteiro, e o fundo (as folhas da palmeira e a grama) vem do entorno.
# 3. O JARDIM (17,46 m²): o rótulo, em preto sobre a grama, em branco, como o dos outros jardins.
JARDINS_TA = {"jardim_479": {"perto_px": (1586, 1672), "cor": (255, 255, 255), "folga_px": 6, "branco": 205,
                             "faixa_px": (1640, 1700)},
              "jardim_1746": {"perto_px": (2361, 998), "cor": (255, 255, 255)}}


def jardins_ta(Q, img):
    q = JARDINS_TA
    rot, aj = _rotulos_pav(Q)
    forma = img.shape[:2]
    out = img.copy()
    # o JARDIM de 4,79 m²
    j = q["jardim_479"]
    r = _rotulo(Q, rot, "JARDIM", j["perto_px"])
    a = _alfa_rotulo(Q, forma, r, aj)
    B = _sem_rotulo(out, a, j["cor"])
    x0, y0, x1, y1 = _caixa(a)
    f = j["folga_px"]
    ya, yb = j["faixa_px"]
    reg = B[ya:yb].astype(np.int16)
    claro = ((reg.min(axis=2) > j["branco"]) & ((reg.max(axis=2) - reg.min(axis=2)) < 30)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(claro, connectivity=8)
    caixa = np.zeros_like(claro, bool)
    caixa[max(0, y0 - f - ya):y1 + f - ya, x0 - f:x1 + f] = True
    tocam = [i for i in np.unique(lab[caixa & (claro > 0)]) if i > 0 and st[i, 3] <= 4]   # os traços (finos), não o texto
    tira = cv2.dilate(np.isin(lab, tocam).astype(np.uint8), np.ones((3, 3), np.uint8))
    B[ya:yb] = cv2.inpaint(B[ya:yb], tira * 255, 3, cv2.INPAINT_TELEA)
    out = _com_rotulo(B, a, j["cor"])
    print(f"    JARDIM (4,79 m²): {len(tocam)} traços do tracejado sob o texto saem")
    # o JARDIM de 17,46 m²
    j = q["jardim_1746"]
    r = _rotulo(Q, rot, "JARDIM", j["perto_px"])
    a = _alfa_rotulo(Q, forma, r, aj)
    import retoque_1pav_casae as R1
    out = _com_rotulo(_sem_rotulo(out, a, R1.ROTULOS["cor"]), a, j["cor"])
    print("    JARDIM (17,46 m²): o rótulo em branco")
    return out


# 2. A ÁREA DE SERVIÇO DESCOBERTA: o X tracejado do PDF (DOC_LINHAS E PROJEÇÕES, um traço por segmento) atravessava o
# rótulo, embaixo. Como na Casa E: o rótulo no cruzamento do X e o X aberto em volta dele (os traços que entram na caixa do
# texto mais `folga_px` saem inteiros). O traço sai com o piso de `desloc_px` ao lado, na perpendicular dele (a pedra
# portuguesa, sem o borrão de um inpaint); onde o rótulo estava, o fundo volta, com o X por baixo.
SERVICO_TA = {"nome": "ÁREA DE SERVIÇO DESCOBERTA", "camada": "DOC_LINHAS E PROJEÇÕES",
              "janela_pt": (1495.0, 1784.0, 1700.0, 2062.0), "folga_px": 7, "meia_larg_px": 2.2, "escuro": 120,
              "desloc_px": 6}


def _x_servico(Q):
    q = SERVICO_TA
    a0, b0, a1, b1 = q["janela_pt"]
    segs = []
    for d in Q.desenhos:
        r = d["rect"]
        if d.get("layer") != q["camada"] or d["type"] != "s" or r.x0 < a0 or r.x1 > a1 or r.y0 < b0 or r.y1 > b1:
            continue
        segs += [(it[1].x, it[1].y, it[2].x, it[2].y) for it in d["items"] if it[0] == "l"]
    segs = np.float64(segs)
    # as duas diagonais (subindo e descendo) e o cruzamento
    sobe = segs[(segs[:, 3] - segs[:, 1]) * (segs[:, 2] - segs[:, 0]) < 0]
    desce = segs[(segs[:, 3] - segs[:, 1]) * (segs[:, 2] - segs[:, 0]) > 0]
    def reta(s):
        p = np.vstack([s[:, :2], s[:, 2:]])
        return np.polyfit(p[:, 0], p[:, 1], 1)
    (m1, c1), (m2, c2) = reta(sobe), reta(desce)
    xc = (c2 - c1) / (m1 - m2)
    return segs, Q.p2q(xc, m1 * xc + c1)


def servico_ta(Q, img):
    import retoque_1pav_casae as R1
    q = SERVICO_TA
    rot, aj = _rotulos_pav(Q)
    forma = img.shape[:2]
    r = _rotulo(Q, rot, q["nome"], (1813, 1860))
    a = _alfa_rotulo(Q, forma, r, aj)
    out = _sem_rotulo(img, a, R1.ROTULOS["cor"])
    segs, (cx, cy) = _x_servico(Q)
    # o rótulo levado ao cruzamento: o centro da caixa do texto no cruzamento
    x0, y0, x1, y1 = _caixa(a)
    e = FA.A.LARGURA / 2000
    pcx, pcy = Q.p2q(*r[2])
    d = (cx - (x0 + x1) / 2, cy - (y0 + y1) / 2)
    aj2 = [a_ for a_ in aj if a_[0] != q["nome"]] + [(q["nome"], (pcx / e, pcy / e), (d[0] / e, d[1] / e))]
    a2 = _alfa_rotulo(Q, forma, r, aj2)
    x0, y0, x1, y1 = _caixa(a2)
    f = q["folga_px"]
    # os traços que entram na caixa (mais a folga) saem inteiros
    n = 0
    for s in segs:
        (u0, v0), (u1, v1) = Q.p2q(s[0], s[1]), Q.p2q(s[2], s[3])
        bx0, bx1, by0, by1 = min(u0, u1), max(u0, u1), min(v0, v1), max(v0, v1)
        t = np.linspace(0, 1, 40)
        xs, ys = u0 + (u1 - u0) * t, v0 + (v1 - v0) * t
        if not np.any((xs > x0 - f) & (xs < x1 + f) & (ys > y0 - f) & (ys < y1 + f)):
            continue
        m = np.zeros(forma, np.uint8)
        cv2.line(m, (int(round(u0 * 8)), int(round(v0 * 8))), (int(round(u1 * 8)), int(round(v1 * 8))), 255,
                 max(1, int(round(2 * q["meia_larg_px"]))), cv2.LINE_8, shift=3)
        m = m > 0
        lum = out.astype(np.int16).mean(axis=2)
        m &= cv2.dilate(((lum < q["escuro"]) & m).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        nx, ny = -(v1 - v0), (u1 - u0)
        k = q["desloc_px"] / np.hypot(nx, ny)
        dx, dy = int(round(nx * k)), int(round(ny * k))
        src = np.roll(np.roll(out, -dy, axis=0), -dx, axis=1)
        out[m] = src[m]
        n += 1
    out = _com_rotulo(out, a2, R1.ROTULOS["cor"])
    print(f"    ÁREA DE SERVIÇO DESCOBERTA: o rótulo no cruzamento do X ({cx:.0f}, {cy:.0f}) e {n} traços abertos em volta")
    return out


# 4. A faixa entre o hall externo e o jardim, entre as duas paredes (no PDF, o piso com um X tracejado; na final, o
# travertino claro com o X em traços pretos e brancos): em branco, sem o tracejado (usuário: "preencha com tom Branco sem
# tracejado"). O miolo entre as paredes, em pt do PDF, com a borda antisserrilhada. Em volta dele (`anel_px`), os
# restos claros dos traços do X que passavam da borda vão para o cinza da parede (a mediana dela ali).
FAIXA_BRANCA_TA = {"pt": (2296.2, 1072.2, 2500.3, 1083.5), "cor": (255, 255, 255), "ss": 8, "anel_px": 4,
                   "claro_acima": 25}


def faixa_branca_ta(Q, img):
    q = FAIXA_BRANCA_TA
    (a, b), (c, d) = Q.p2q(*q["pt"][:2]), Q.p2q(*q["pt"][2:])
    X0, Y0, X1, Y1 = int(np.floor(a)) - 2, int(np.floor(b)) - 2, int(np.ceil(c)) + 2, int(np.ceil(d)) + 2
    k = q["ss"]
    m = np.zeros(((Y1 - Y0) * k, (X1 - X0) * k), np.uint8)
    cv2.rectangle(m, (int(round((a - X0) * k)), int(round((b - Y0) * k))),
                  (int(round((c - X0) * k)) - 1, int(round((d - Y0) * k)) - 1), 255, -1)
    A_ = cv2.resize(m.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
    out = img.copy()
    e = q["anel_px"]
    anel = out[Y0 - e:Y1 + e, X0 - e:X1 + e]
    dentro = np.pad(A_[..., 0], e) > 0.02                             # o miolo do PDF
    lum = anel.astype(np.int16).mean(axis=2)
    parede = np.median(anel[~dentro & (lum < np.median(lum[~dentro]) + 10)], axis=0)
    claro = ~dentro & (lum > np.median(lum[~dentro]) + q["claro_acima"])
    anel[claro] = parede
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - A_) + np.float32(q["cor"]) * A_, 0, 255).astype(np.uint8)
    print(f"    faixa entre o hall externo e o jardim: em branco, sem o tracejado ({int(claro.sum())} px de restos do X "
          f"na parede)")
    return out


# 5. O elevador e os shafts. O Subsolo já tem a cabine de aço padrão (`final3840_casaa.elevador`, a mesma da Casa B, de
# 26/10); no Térreo e no 1º Pavimento o elevador era o X do PDF sobre o bege ou o branco. Nos três PDFs a caixa do
# elevador e o vão da porta (à esquerda) são os mesmos, em pt: a cabine entra com a configuração do Subsolo
# (`final3840_casaa.ELEVADOR`) e o rótulo ELEVADOR é escrito de novo por cima, como na final. Os X dos shafts (DOC_LINHAS E
# PROJEÇÕES), em cinza no Subsolo e no Térreo, vão para o preto dos tracejados (`final3840_casaa_terreo.preto_branco`):
# o X cinza sai (os px a até `faixa_px` da reta de cada perna, no miolo do shaft, com o fundo do entorno) e os traços do
# PDF entram em preto, na largura das projeções, só no miolo, abertos em volta do rótulo SHAFT do Térreo (os que entram na
# caixa do texto mais `folga_px` não entram), como o X do shaft da Casa B. Os shafts em pt: o da direita do elevador nos
# dois pavimentos, e o de cima, só no Subsolo.
ELEVADOR_TA = {"rotulo": "ELEVADOR",
               "shafts_pt": {"Subsolo": [(2021.2, 1230.9, 2143.1, 1287.5), (2114.8, 1287.6, 2143.1, 1372.7)],
                             "Terreo": [(2114.8, 1287.6, 2143.1, 1372.7)]},
               "camada": "DOC_LINHAS E PROJEÇÕES", "faixa_px": 2.5, "folga_px": 5}


def elevador_ta(Q, img):
    import retoque_1pav_casae as R1
    out = FA.elevador(Q, np.ascontiguousarray(img.copy()))
    rot, aj = _rotulos_pav(Q)
    r = min((r for r in rot if r[0] == ELEVADOR_TA["rotulo"]), key=lambda r: abs(r[2][0] - 2064))
    a = _alfa_rotulo(Q, img.shape[:2], r, aj)
    print(f"    {Q.chave}: a cabine de aço do elevador, com o rótulo de novo por cima")
    return _com_rotulo(out, a, R1.ROTULOS["cor"])


def shafts_ta(Q, img):
    import final3840_casaa_terreo as T
    import retoque_1pav_casae as R1
    q, pj = ELEVADOR_TA, T.PROJ
    out = img.copy()
    rot, aj = _rotulos_pav(Q)
    for a0, b0, a1, b1 in q["shafts_pt"].get(Q.chave, ()):
        segs = []
        for d in Q.desenhos:
            r = d["rect"]
            if d.get("layer") == q["camada"] and d["type"] == "s" and r.x0 >= a0 - 0.5 and r.x1 <= a1 + 0.5 \
                    and r.y0 >= b0 - 0.5 and r.y1 <= b1 + 0.5:
                segs += [(it[1].x, it[1].y, it[2].x, it[2].y) for it in d["items"] if it[0] == "l"]
        (X0, Y0), (X1, Y1) = Q.p2q(a0, b0), Q.p2q(a1, b1)
        X0, Y0, X1, Y1 = int(np.floor(X0)) - 3, int(np.floor(Y0)) - 3, int(np.ceil(X1)) + 3, int(np.ceil(Y1)) + 3
        # o rótulo SHAFT (Térreo), se cai na caixa: sai antes e volta por cima, e a caixa dele abre o X
        rs = [r for r in rot if r[0] == "SHAFT" and X0 <= Q.p2q(*r[2])[0] <= X1 and Y0 <= Q.p2q(*r[2])[1] <= Y1]
        al = _alfa_rotulo(Q, out.shape[:2], rs[0], aj) if rs else None
        if al is not None:
            out = _sem_rotulo(out, al, R1.ROTULOS["cor"])
        reg = out[Y0:Y1, X0:X1]
        # o miolo do shaft (fora as paredes): o claro maior da caixa
        claro = (reg.astype(np.int16).mean(axis=2) > 110).astype(np.uint8)
        n_, lab, st, _ = cv2.connectedComponentsWithStats(claro)
        miolo = (lab == 1 + int(np.argmax(st[1:, 4]))).astype(np.uint8)
        miolo = cv2.erode(miolo, np.ones((3, 3), np.uint8))
        # o X cinza: as duas pernas inteiras, na faixa, só no miolo
        m = np.zeros(reg.shape[:2], np.uint8)
        for x0, y0, x1, y1 in segs:
            (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
            cv2.line(m, (int(round((u0 - X0) * 8)), int(round((v0 - Y0) * 8))),
                     (int(round((u1 - X0) * 8)), int(round((v1 - Y0) * 8))), 255, int(round(2 * q["faixa_px"])),
                     cv2.LINE_8, shift=3)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) * miolo
        out[Y0:Y1, X0:X1] = cv2.inpaint(np.ascontiguousarray(reg), m, 3, cv2.INPAINT_TELEA)
        if al is not None:                                  # os traços que entram na caixa do texto não entram
            tx0, ty0, tx1, ty1 = _caixa(al)
            f = q["folga_px"]
            def fora(sg):
                (u0, v0), (u1, v1) = Q.p2q(sg[0], sg[1]), Q.p2q(sg[2], sg[3])
                t = np.linspace(0, 1, 20)
                xs_, ys_ = u0 + (u1 - u0) * t, v0 + (v1 - v0) * t
                return not np.any((xs_ > tx0 - f) & (xs_ < tx1 + f) & (ys_ > ty0 - f) & (ys_ < ty1 + f))
            segs = [sg for sg in segs if fora(sg)]
        # os traços do PDF em preto, na largura das projeções, só no miolo (as pontas não entram na parede)
        k = pj["ss"]
        h, w = reg.shape[:2]
        t = np.zeros((h * k, w * k), np.uint8)
        for x0, y0, x1, y1 in segs:
            (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
            cv2.line(t, (int((u0 - X0) * k), int((v0 - Y0) * k)), (int((u1 - X0) * k), int((v1 - Y0) * k)), 255,
                     max(1, int(round(pj["larg_px"] * k))), cv2.LINE_AA)
        a = cv2.resize(t.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * miolo
        r_ = out[Y0:Y1, X0:X1].astype(np.float32)
        out[Y0:Y1, X0:X1] = np.clip(r_ * (1 - a[..., None]) + np.float32(pj["preto"]) * a[..., None], 0, 255
                                    ).astype(np.uint8)
        if al is not None:
            out = _com_rotulo(out, al, R1.ROTULOS["cor"])
        print(f"    {Q.chave}: o X do shaft ({a0:.0f}, {b0:.0f}) em preto, {len(segs)} traços"
              + (", aberto em volta do rótulo SHAFT" if al is not None else ""))
    return out


# 6. O Subsolo: as peças do Térreo que o PDF do Subsolo desenha fora dele estavam na hachura. Como na Casa B
# (`subsolo_casab_2910.nevoado_sb`), elas saem da final do Térreo, no nublado do Térreo nas plantas de cima
# (`entorno_esmaecido.NUBLADO`), recortadas pelo desenho delas no PDF do Subsolo (os dois PDFs e os dois quadros têm as
# mesmas coordenadas): as 7 pedras dos pisantes, a borda da piscina (o cinza do PDF), a piscina e o spa (os
# preenchimentos da ARQ_CONTRAPISO) e o deck de madeira (`deck_pt`, em L: no PDF, as réguas entre o tracejado da
# ARQ_CONTRAPISO à esquerda e em cima, a borda da piscina à direita, o spa e a escada do Subsolo embaixo; o mesmo L do deck
# na final do Térreo). Só onde a final do Subsolo é hachura (o branco e os fios cinza, em manchas grandes): o subsolo fica
# como está.
# Do Térreo saem antes os rótulos (PISCINA, SPA, PRAINHA, DECK DE MADEIRA: o alfa de cada um, como em `_sem_rotulo`) e as
# letras D das escadas (as manchas escuras e neutras do tamanho de uma letra, com o entorno).
# O trecho de baixo do deck (pedido de 29/10 na 3ª leva: "faltando parte do deck nevoado, ao subir as escadas, na prancha
# do subsolo"): no PDF, as réguas descem à esquerda da escada até a linha do gramado (1299 pt); a 3ª caixa do `deck_pt`.
NEVOADO_TA = {"caixa_pt": (550.0, 530.0, 1160.0, 1235.0), "camada": "ARQ_CONTRAPISO",
              "cores": [(0.89, 0.89, 0.89), (0.5, 0.87, 1.0)], "tol_cor": 0.02,
              "deck_pt": [(567.0, 703.7, 907.1, 1049.6), (567.0, 1049.6, 748.6, 1230.9), (567.0, 1230.9, 736.7, 1299.0)],
              "hachura": {"lum": 150, "croma": 18, "area_px": 50000}, "ss": 4,
              "letra": {"escuro_max": 120, "neutro_max": 30, "lado_max_px": 30, "folga_px": 2, "raio_px": 3}}


def _nublar_ta(t, W):
    from entorno_esmaecido import NUBLADO as n
    t = cv2.GaussianBlur(t.astype(np.float32), (0, 0), n["desfoque"] * W / 3840)
    cinza = t.mean(axis=2, keepdims=True)
    t = cinza + (t - cinza) * n["saturacao"]
    return 255 - (255 - t) * (1 - n["clarear"])


def nevoado_ta(Q, img, terreo):
    import ajustes_casaa as AJ
    import retoque_1pav_casae as R1
    q = NEVOADO_TA
    a0, b0, a1, b1 = q["caixa_pt"]
    H, W = img.shape[:2]
    k = q["ss"]
    pecas = np.zeros((H * k, W * k), np.uint8)
    n_p = 0
    for d in Q.desenhos:
        r = d["rect"]
        if d.get("layer") != q["camada"] or d.get("fill") is None or r.x0 < a0 or r.y0 < b0 or r.x0 > a1 or r.y0 > b1:
            continue
        if not any(max(abs(u - v) for u, v in zip(d["fill"], c)) <= q["tol_cor"] for c in q["cores"]):
            continue
        for c in AJ.caminhos_pdf(d, lambda x, y: tuple(v * k for v in Q.p2q(x, y))):
            if len(c) >= 3:
                cv2.fillPoly(pecas, [np.int32(np.round(c))], 255)
        n_p += 1
    for da0, db0, da1, db1 in q["deck_pt"]:                           # o deck
        (u0, v0), (u1, v1) = Q.p2q(da0, db0), Q.p2q(da1, db1)
        cv2.rectangle(pecas, (int(round(u0 * k)), int(round(v0 * k))), (int(round(u1 * k)) - 1, int(round(v1 * k)) - 1),
                      255, -1)
    pecas = cv2.resize(pecas, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    # a hachura da final do Subsolo
    h_ = q["hachura"]
    i16 = img.astype(np.int16)
    claro = ((i16.mean(axis=2) > h_["lum"]) & ((i16.max(axis=2) - i16.min(axis=2)) < h_["croma"])).astype(np.uint8)
    claro = cv2.morphologyEx(claro, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n_, lab, st, _ = cv2.connectedComponentsWithStats(claro)
    hach = np.isin(lab, [i for i in range(1, n_) if st[i, 4] >= h_["area_px"]]).astype(np.float32)
    a = pecas * hach
    ys, xs = np.nonzero(a > 0)
    X0, Y0, X1, Y1 = xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5
    # o Térreo sem os rótulos e sem as letras D, nublado
    QT = FA.QuadroA("Terreo")
    rot, aj = _rotulos_pav(QT)
    t = terreo.copy()
    tirados = []
    for r in rot:
        al = _alfa_rotulo(QT, t.shape[:2], r, aj)
        if (al[Y0:Y1, X0:X1] * a[Y0:Y1, X0:X1]).sum() > 0:
            t = _sem_rotulo(t, al, R1.ROTULOS["cor"])
            tirados.append(r[0])
    lt = q["letra"]
    reg = t[Y0:Y1, X0:X1]
    escuro = (reg.max(axis=2) < lt["escuro_max"]) & (reg.max(axis=2).astype(int) - reg.min(axis=2) < lt["neutro_max"])
    n_, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(escuro.astype(np.uint8), np.ones((5, 5), np.uint8)))
    m = np.zeros(escuro.shape, np.uint8)
    for i in range(1, n_):
        if st[i, 2] <= lt["lado_max_px"] and st[i, 3] <= lt["lado_max_px"]:
            m[(lab == i) & escuro] = 255
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * lt["folga_px"] + 1,) * 2))
    m &= ((a[Y0:Y1, X0:X1] > 0) * 255).astype(np.uint8)
    t[Y0:Y1, X0:X1] = cv2.inpaint(reg, m, lt["raio_px"], cv2.INPAINT_TELEA)
    nv = _nublar_ta(t[Y0:Y1, X0:X1], W)
    out = img.copy()
    al_ = a[Y0:Y1, X0:X1, None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(out[Y0:Y1, X0:X1] * (1 - al_) + nv * al_), 0, 255).astype(np.uint8)
    print(f"    Subsolo: {n_p} peças do Térreo e o deck, nevoados ({int((a > 0.5).sum())} px), sem os rótulos "
          f"({', '.join(tirados)}) e sem as letras ({int((m > 0).sum())} px)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 7 a 10. O mobiliário, no padrão das outras casas. As peças são as do PDF, cada uma pela camada e pelo retângulo (pt);
# na Casa A muitas estão em camadas trocadas (as poltronas e o sofá reto da varanda na DOC_TEXTOS, a mesa de jantar na
# ARQ_MARCENARIA e as cadeiras dela na ARQ_LAYOUT HUMANIZAÇÃO).
CAMADAS_MOVEIS_TA = ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO", "DOC_TEXTOS", "ARQ_MARCENARIA")

# 7. As 12 cadeiras das duas mesas redondas da varanda gourmet (ARQ_MOBILIÁRIO, 1,60 m; as cadeiras na ARQ_LAYOUT
# HUMANIZAÇÃO): as de couro do conjunto padrão, como nas Casas B e C (`final3840_casac.jogos_varanda_tc`), as mesas de
# madeira da final ficam. O tampo do render tem uns 4 px a menos de raio que o do PDF (o anel entre os dois era das
# cadeiras antigas): antes, o tampo do render é ampliado em volta do centro até o círculo do PDF (`mesas_varanda_ta`; o
# raio dele, a beira da madeira, medido em `n_raios` direções: onde o amarelo da madeira, b* do Lab, cai abaixo de
# `madeira_b`), com a beira macia.
JOGOS_VARANDA_TA = dict(Cc.JOGOS_VARANDA_TC, mesas_pt=[(1435.9, 1084.0, 1526.7, 1174.7), (1430.6, 1253.9, 1521.3, 1344.6)],
                        n_raios=48, madeira_b=140, beira_px=1.0)


def mesas_varanda_ta(Q, img, q=None):
    q = q or JOGOS_VARANDA_TA
    out = img.astype(np.float32)
    H, W = img.shape[:2]
    b_ = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)[..., 2].astype(np.float32)
    for m in q["mesas_pt"]:
        (x0, y0), (x1, y1) = Q.p2q(m[0], m[1]), Q.p2q(m[2], m[3])
        cx, cy, R = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2
        raios = []
        for ang in np.linspace(0, 2 * np.pi, q["n_raios"], endpoint=False):
            rr = np.arange(R - 15, R + 5, 0.5)
            v = b_[np.round(cy + rr * np.sin(ang)).astype(int), np.round(cx + rr * np.cos(ang)).astype(int)]
            k = np.nonzero(v < q["madeira_b"])[0]
            if len(k):
                raios.append(rr[k[0]])
        r_render = float(np.median(raios))
        e = R / r_render
        M = np.float32([[1 / e, 0, cx * (1 - 1 / e)], [0, 1 / e, cy * (1 - 1 / e)]])
        maior = cv2.warpAffine(out, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        yy, xx = np.mgrid[0:H, 0:W]
        a = np.clip((R - np.hypot(xx - cx, yy - cy)) / q["beira_px"] + 0.5, 0, 1).astype(np.float32)
        out = out * (1 - a[..., None]) + maior * a[..., None]
        print(f"    mesa da varanda em ({cx:.0f}, {cy:.0f}): o tampo do render (raio {r_render:.1f} px) ampliado ao do PDF "
              f"({R:.1f} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _desenho(Q, camada, r, tipos=("f", "fs")):
    return next(d for d in Q.desenhos if d.get("layer") == camada and d["type"] in tipos
                and max(abs(a - b) for a, b in zip(d["rect"], r)) < 0.5)


class _QCamadas:
    """O quadro com as camadas de algumas peças trocadas (`troca`: {(camada, retângulo pt): camada nova}), para as
    rotinas das outras casas, que procuram as peças pela camada delas."""

    def __init__(self, Q, troca):
        self._Q = Q
        def nova(d):
            for (cam, r), c2 in troca.items():
                if d.get("layer") == cam and max(abs(a - b) for a, b in zip(d["rect"], r)) < 0.5:
                    return dict(d, layer=c2)
            return d
        self.desenhos = [nova(d) for d in Q.desenhos]

    def __getattr__(self, k):
        return getattr(self._Q, k)


# 8. As 8 cadeiras da mesa de jantar (o assento de 24 x 28 pt e os dois braços de cada uma, ARQ_LAYOUT HUMANIZAÇÃO; a mesa
# oval na ARQ_MARCENARIA): a cadeira padrão das outras casas (`final3840_casad.jantar_d`: a da mesa de 10 lugares da
# biblioteca, com o quadro de madeira e o assento em linho, de frente para a mesa, 1/3 sob o tampo). Antes, o piso no
# lugar das cadeiras antigas (a caixa de cada uma mais `folga_px`): o travertino da mesma linha, do primeiro trecho livre
# ao lado (os estratos são deitados), longe das peças do PDF (`livre_px`), dos rótulos e dos traços (mais escuros que
# `traco_cinza`), com a passagem macia; esse é o piso que fica (`passos`=0: sem a cópia ao lado do `jantar_d`, que pela
# legenda do PDF trazia o rótulo da sala de jantar, que na final está noutro lugar).
JANTAR_TA = dict(D.JANTAR_TD, mesa_pt=(1717.9, 1123.2, 1888.0, 1191.2), lado_pt=(24.0, 30.0), lado_norm=True,
                 mesa_pdf=True, camada_cadeiras="ARQ_LAYOUT HUMANIZAÇÃO", camada_mesa="ARQ_MARCENARIA",
                 folga_px=6, busca_px=(30, 400), livre_px=4, suave_px=2.0, traco_cinza=190, passos=0)


def _ocupado(Q, livre_px, camadas=CAMADAS_MOVEIS_TA):
    m = Q.preencher(lambda d: d.get("layer") in camadas) > 0.02
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * livre_px + 1,) * 2, np.uint8)) > 0


def _piso_ao_lado(img, caixas, ocupado, busca, suave, eixo="x"):
    """O piso no lugar das caixas (px): a mesma faixa deslocada no `eixo` até o primeiro trecho livre (nada de
    `ocupado`), com a borda macia. Devolve a imagem e quantas caixas saíram."""
    out = img.astype(np.float32)
    H, W = ocupado.shape
    n = 0
    for x0, y0, x1, y1 in caixas:
        d_ = None
        for d in range(busca[0], busca[1]):
            for s_ in (-1, 1):
                dx, dy = (s_ * d, 0) if eixo == "x" else (0, s_ * d)
                if 0 <= x0 + dx and x1 + dx <= W and 0 <= y0 + dy and y1 + dy <= H \
                        and not ocupado[y0 + dy:y1 + dy, x0 + dx:x1 + dx].any():
                    d_ = (dx, dy)
                    break
            if d_:
                break
        if d_ is None:
            print(f"      sem trecho livre para o piso da caixa ({x0}, {y0})")
            continue
        m = np.zeros((H, W), np.float32)
        m[y0:y1, x0:x1] = 1
        m = cv2.GaussianBlur(m, (0, 0), suave)
        fonte = np.roll(np.roll(out, -d_[1], axis=0), -d_[0], axis=1)
        out = out * (1 - m[..., None]) + fonte * m[..., None]
        n += 1
    return np.clip(out, 0, 255).astype(np.uint8), n


def jantar_ta(Q, img, q=None):
    q = q or JANTAR_TA
    mesa = q["mesa_pt"]
    cads = [d for d in Q.desenhos if d.get("layer") == q["camada_cadeiras"] and d["type"] in ("f", "fs")
            and mesa[0] - 35 <= d["rect"].x0 and d["rect"].x1 <= mesa[2] + 35
            and mesa[1] - 35 <= d["rect"].y0 and d["rect"].y1 <= mesa[3] + 35]
    assentos = [d for d in cads if q["lado_pt"][0] <= min(d["rect"].width, d["rect"].height)
                and max(d["rect"].width, d["rect"].height) <= q["lado_pt"][1]]
    # a caixa de cada cadeira (o assento e os braços) mais a folga
    caixas = []
    for a in assentos:
        r = a["rect"]
        grupo = [d["rect"] for d in cads if d["rect"].x0 >= r.x0 - 4 and d["rect"].x1 <= r.x1 + 4
                 and d["rect"].y0 >= r.y0 - 4 and d["rect"].y1 <= r.y1 + 4]
        (x0, y0), (x1, y1) = Q.p2q(min(g.x0 for g in grupo), min(g.y0 for g in grupo)), \
            Q.p2q(max(g.x1 for g in grupo), max(g.y1 for g in grupo))
        f = q["folga_px"]
        caixas.append((int(np.floor(x0)) - f, int(np.floor(y0)) - f, int(np.ceil(x1)) + f, int(np.ceil(y1)) + f))
    oc = _ocupado(Q, q["livre_px"])
    # nem os rótulos nem os traços (a linha cinza da parede, os tracejados) são origem do piso
    traco = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < q["traco_cinza"]
    oc |= cv2.dilate((traco | _rotulos_mascara(Q, img.shape[:2])).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    for c in caixas:                                       # as próprias cadeiras não são origem do piso
        x0, y0, x1, y1 = c
        oc[y0:y1, x0:x1] = True
    piso, n = _piso_ao_lado(img, caixas, oc, q["busca_px"], q["suave_px"])
    Qp = _QCamadas(Q, {**{(q["camada_cadeiras"], tuple(a["rect"])): "ARQ_MOBILIÁRIO" for a in assentos},
                       (q["camada_mesa"], mesa): "ARQ_MOBILIÁRIO"})
    out = D.jantar_d(Qp, img, piso, q=q)
    print(f"    mesa de jantar: {len(assentos)} cadeiras no padrão das outras casas ({n} caixas com o piso ao lado)")
    return out


# 9. As poltronas: o modelo padrão, a poltrona da sala íntima do 1º Pavimento da Casa E (`final3840_casae.
# _modelo_poltrona_1p`), no centro da peça do PDF, no lado `t_pt` (o maior lado da peça, ou o dado: nas giradas a 45°, a
# caixa é a diagonal), com a abertura do assento virada para a `frente` (dx, dy) e a sombra e o contato das da Casa E. O
# lugar da antiga (a peça com `folga_px` e a sombra dela, `sombra_px`, para baixo e à esquerda) é refeito por material: no
# tapete (os preenchimentos de `tapetes`), o tapete; fora dele, o piso; cada parte com a mesma parte deslocada até o
# primeiro trecho todo livre do mesmo material (sem as peças do PDF, `livre_px`, sem os rótulos), primeiro no `eixo` do
# veio do piso, depois no outro e na diagonal. As projeções tracejadas que passam por cima voltam por cima no fim
# (`tracejados_ta`).
POLTRONAS_TA = {
    "Terreo": {"eixo": "x", "pecas": [
        ("varanda, de cima", "DOC_TEXTOS", (1387.3, 610.7, 1437.5, 658.2), (1.0, 0.0), None),
        ("varanda, de baixo", "DOC_TEXTOS", (1387.3, 687.9, 1437.5, 735.4), (1.0, 0.0), None),
        ("varanda, sob a projeção, de cima", "DOC_TEXTOS", (1484.1, 852.9, 1558.2, 927.0), (-0.6, 0.8), 64.0),
        ("varanda, sob a projeção, de baixo", "DOC_TEXTOS", (1484.1, 948.3, 1558.2, 1022.4), (-0.6, -0.8), 64.0),
        ("sala de estar, à direita do tapete", "ARQ_LAYOUT HUMANIZAÇÃO", (1869.1, 641.5, 1920.9, 694.8), (-0.95, 0.3),
         None),
        ("sala de estar, embaixo, à esquerda", "ARQ_LAYOUT HUMANIZAÇÃO", (1749.9, 754.8, 1794.0, 801.5), (0.0, -1.0),
         None),
        ("sala de estar, embaixo, à direita", "ARQ_LAYOUT HUMANIZAÇÃO", (1817.9, 754.8, 1862.0, 801.5), (0.0, -1.0),
         None),
        ("sala de estar, em X, no alto à esquerda", "ARQ_LAYOUT HUMANIZAÇÃO", (1703.7, 859.2, 1773.2, 928.5),
         (0.71, 0.71), 52.0),
        ("sala de estar, em X, no alto à direita", "ARQ_LAYOUT HUMANIZAÇÃO", (1816.1, 858.9, 1885.5, 928.3),
         (-0.71, 0.71), 52.0),
        ("sala de estar, em X, embaixo à direita", "ARQ_LAYOUT HUMANIZAÇÃO", (1815.0, 947.8, 1884.4, 1017.1),
         (-0.71, -0.71), 52.0),
        ("sala de estar, em X, embaixo à esquerda", "ARQ_LAYOUT HUMANIZAÇÃO", (1704.6, 947.6, 1774.0, 1017.0),
         (0.71, -0.71), 52.0),
        ("terraço gourmet", "ARQ_MOBILIÁRIO", (1083.7, 1449.1, 1144.1, 1509.5), (0.0, 1.0), None),
        ("escritório", "ARQ_LAYOUT HUMANIZAÇÃO", (2280.9, 721.9, 2331.8, 775.4), (-0.7, -0.7), None)],
        "tapetes": [("ARQ_LAYOUT HUMANIZAÇÃO", (1415.6, 602.9, 1585.7, 744.6)),
                    ("ARQ_MOBILIÁRIO", (1699.0, 590.2, 1925.7, 816.7))],
        # a antiga do render, à direita do tapete da sala de estar, é maior e mais girada que a peça do PDF
        "folga_px": {"sala de estar, à direita do tapete": 12},
        # junto da parede, com a sombra dela no piso
        "sombra_parede": ("escritório",)},
    "1Pavimento": {"eixo": "x", "pecas": [
        ("suíte 2, no canto da janela", "ARQ_LAYOUT HUMANIZAÇÃO", (1420.4, 1193.2, 1466.2, 1239.0), (0.7, 0.7), None),
        ("suíte master, junto da mesinha", "ARQ_LAYOUT HUMANIZAÇÃO", (1439.3, 1524.5, 1492.6, 1576.0), (-0.6, -0.8),
         None),
        ("sala íntima, embaixo do tapete", "ARQ_LAYOUT HUMANIZAÇÃO", (1837.6, 1331.9, 1888.5, 1385.4), (0.6, -0.8),
         None)],
        "tapetes": [("ARQ_LAYOUT HUMANIZAÇÃO", (1457.4, 1218.6, 1655.8, 1331.9)),
                    ("ARQ_LAYOUT HUMANIZAÇÃO", (1812.1, 1146.1, 1925.5, 1344.5))],
        # as antigas do render das suítes são maiores que as peças do PDF; a da suíte 2 encosta na cortina, que fica
        "folga_px": {"suíte 2, no canto da janela": 13, "suíte master, junto da mesinha": 10},
        "recorte_pt": {"suíte 2, no canto da janela": (1419.0, 1150.0, 1500.0, 1270.0)}},
}
POLTRONAS_PARAM_TA = {"folga_px": 7, "sombra_px": 5, "madeira_b": 8, "fundo_claro": 190, "ficam_px": 1, "livre_px": 5, "busca_px": 260,
                      "tol_lab": (60, 9), "banda_px": (16, 8), "escuro_abs": 90, "escuro_rel": 30, "traco_px": 3, "livre_borda_px": 12,
                      "emenda_px": 4, "esfuma_px": 2}


def _mascara_peca(Q, camada, r):
    return Q.preencher(lambda d: d.get("layer") == camada and D._dentro_pt(d["rect"], r)) > 0.05


def _rotulos_mascara(Q, forma):
    rot, aj = _rotulos_pav(Q)
    m = np.zeros(forma, bool)
    for r in rot:
        m |= _alfa_rotulo(Q, forma, r, aj) > 0.02
    return m


def _tapar_linhas(out, buraco, materiais, proibido, busca, tol, trecho=28, candidatos=8):
    """Cada trecho de linha do `buraco` num material (lista de máscaras; o resto é o piso) vem do trecho da mesma linha
    deslocado até o primeiro lugar todo livre (os estratos do travertino e a trama do tapete são deitados): do mesmo
    material, fora do `proibido` e na cor do anel em volta (Lab, `tol`: a luz e a cor; os estratos mais escuros entram,
    a mesa de centro, que no PDF só tem o contorno, e os tracejados não), em pedaços de até `trecho` px (entre os
    tracejados em X não cabe um trecho comprido). Sem trecho livre na linha, a linha livre mais perto em cima ou
    embaixo; sem nenhum, o px fica nas `falhas` (devolvidas)."""
    H, W = buraco.shape
    lab = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    fonte = out.copy()
    resto = ~np.any(materiais, axis=0) if materiais else np.ones((H, W), bool)
    falhas = np.zeros((H, W), bool)
    for mat in list(materiais) + [resto]:
        n_, lb, st, _ = cv2.connectedComponentsWithStats((buraco & mat).astype(np.uint8))
        for i in range(1, n_):
            x, y, w, h = st[i, :4]
            x0, y0, x1, y1 = max(0, x - busca), max(0, y - busca), min(W, x + w + busca), min(H, y + h + busca)
            comp = lb[y0:y1, x0:x1] == i
            m_ = mat[y0:y1, x0:x1]
            anel = cv2.dilate(comp.astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool) \
                & ~buraco[y0:y1, x0:x1] & m_ & ~proibido[y0:y1, x0:x1]
            if not anel.any():
                falhas[y0:y1, x0:x1] |= comp
                continue
            ref = np.median(lab[y0:y1, x0:x1][anel], axis=0)
            dif = np.abs(lab[y0:y1, x0:x1] - ref)
            # a tolerância cresce com a variação do próprio piso em volta (as réguas do vinílico variam de tom)
            da = dif[anel]
            tl = float(np.clip(1.2 * np.percentile(da[:, 0], 95), 25, tol[0]))
            tc = float(np.clip(1.2 * np.percentile(da[:, 1:].max(axis=1), 95), tol[1], 13))
            ok = m_ & ~buraco[y0:y1, x0:x1] & ~proibido[y0:y1, x0:x1] & (dif[..., 0] < tl) \
                & (dif[..., 1:].max(axis=2) < tc)
            src = out[y0:y1, x0:x1]
            dst = fonte[y0:y1, x0:x1]
            bur_w = buraco[y0:y1, x0:x1]
            for yy in np.unique(np.nonzero(comp)[0]):
                xs = np.nonzero(comp[yy])[0]
                cortes = np.nonzero(np.diff(xs) > 1)[0]
                trechos = [(a + k, min(b, a + k + trecho)) for a, b in zip(np.r_[xs[0], xs[cortes + 1]],
                                                                         np.r_[xs[cortes], xs[-1]] + 1)
                           for k in range(0, b - a, trecho)]
                for a, b in trechos:
                    # os primeiros `candidatos` deslocamentos livres; fica o que emenda melhor com os vizinhos da
                    # linha (o estrato do travertino continua)
                    cands = []
                    for d in range(1, busca):
                        for s_ in (-d, d):
                            if 0 <= a + s_ and b + s_ <= ok.shape[1] and ok[yy, a + s_:b + s_].all():
                                cands.append(s_)
                        if len(cands) >= candidatos:
                            break
                    feito = bool(cands)
                    if cands:
                        viz = [(a - 1, -1)] if a >= 1 and (not bur_w[yy, a - 1] or comp[yy, a - 1]) else []
                        viz += [(b, 0)] if b < ok.shape[1] and not bur_w[yy, b] else []
                        def custo(s_):
                            return sum(np.abs(src[yy, x + s_] - dst[yy, x]).sum() for x, _ in viz
                                       if 0 <= x + s_ < ok.shape[1])
                        s_ = min(cands, key=custo) if viz else cands[0]
                        dst[yy, a:b] = src[yy, a + s_:b + s_]
                    if not feito:
                        for d in range(1, busca):
                            for y2 in (yy - d, yy + d):
                                if 0 <= y2 < ok.shape[0] and ok[y2, a:b].all():
                                    dst[yy, a:b] = src[y2, a:b]
                                    feito = True
                                    break
                            if feito:
                                break
                    if not feito:
                        falhas[y0 + yy, x0 + a:x0 + b] = True
    return fonte, falhas


def _tapete_limpo(out, tapete, livre, banda, sigma=30, tol_l=3.0):
    """O tom limpo do `tapete` do render: a distância d à linha dele (d < 0 dentro), os px limpos do miolo (`livre`, sem
    a sombra das peças: até `tol_l` abaixo da luz mediana) e o tom deles desfocado em `sigma` (normalized convolution)."""
    t8 = tapete.astype(np.uint8)
    d = cv2.distanceTransform(1 - t8, cv2.DIST_L2, 5) - cv2.distanceTransform(t8, cv2.DIST_L2, 5)
    L = out.mean(axis=2)
    miolo = livre & (d < -banda[0])
    limpo = miolo & (L > np.median(L[miolo]) - tol_l)
    wm = limpo.astype(np.float32)
    den = cv2.GaussianBlur(wm, (0, 0), sigma)[..., None]
    campo = cv2.GaussianBlur(out * wm[..., None], (0, 0), sigma) / np.maximum(den, 1e-4)
    campo[den[..., 0] < 1e-3] = np.median(out[limpo], axis=0)
    return d, limpo, campo


def _tapete_por_perfil(out, fonte, buraco, livre, d, campo, banda, janela=80):
    """O tapete sob o `buraco` refeito por um modelo, sem copiar trechos: no miolo (d <= -banda[0]), o tom limpo
    (`campo`); na borda, pela distância d à linha do tapete do PDF, o perfil de cor da borda medido em volta de cada
    parte (a mediana dos px `livre` de cada d, de `banda`[0] px dentro a `banda`[1] px fora: o recuo e o relevo da borda
    do render), levado ao tom limpo dali; por fora, sobre o perfil, o desenho do piso que veio da mesma linha (`fonte`,
    o veio do travertino), crescendo de 0 na linha a 1 em 3 px. Devolve quantas partes."""
    H, W = buraco.shape
    B, O = banda
    alvo = buraco & (d < O)
    nc, lb, st, _ = cv2.connectedComponentsWithStats(alvo.astype(np.uint8))
    bins = np.arange(-B, O + 1)
    for i in range(1, nc):
        x, y, w, h = st[i, :4]
        x0, y0, x1, y1 = max(0, x - janela), max(0, y - janela), min(W, x + w + janela), min(H, y + h + janela)
        comp = lb[y0:y1, x0:x1] == i
        dd = d[y0:y1, x0:x1]
        lv = livre[y0:y1, x0:x1]
        src = out[y0:y1, x0:x1]
        perfil = np.full((len(bins), 3), np.nan, np.float32)
        di = np.round(dd).astype(int)
        for k, b in enumerate(bins):
            sel = lv & (di == b)
            if sel.sum() >= 8:
                perfil[k] = np.median(src[sel], axis=0)
        okp = ~np.isnan(perfil[:, 0])
        okp_real = okp.copy()
        ys, xs = np.nonzero(comp)
        dv = dd[ys, xs]
        cm = campo[y0 + ys, x0 + xs]
        if okp.sum() < 3:
            fonte[y0 + ys, x0 + xs] = np.where((dv > 0)[:, None], fonte[y0 + ys, x0 + xs], cm)
            continue
        for c in range(3):
            perfil[:, c] = np.interp(bins, bins[okp], perfil[okp, c])
        pv = np.stack([np.interp(np.clip(dv, -B, O), bins, perfil[:, c]) for c in range(3)], axis=1)
        # dentro: o perfil levado ao tom limpo dali (que vale inteiro no miolo, d <= -B)
        cor = np.where((dv <= -B)[:, None], cm, pv + (cm - perfil[0]) * np.clip(-dv / B, 0, 1)[:, None])
        # fora: o perfil com o desenho do piso por cima
        f_ = fonte[y0:y1, x0:x1]
        det = (f_ - cv2.GaussianBlur(f_, (0, 0), 3))[ys, xs]
        cor = np.where((dv > 0)[:, None], pv + np.clip(dv / 3, 0, 1)[:, None] * det, cor)
        # por fora, onde a borda não tem amostra em volta (o canto todo sob a antiga), o piso da mesma linha
        sem = (dv > 0) & ~okp_real[np.clip(np.round(dv).astype(int) + B, 0, len(bins) - 1)]
        cor[sem] = f_[ys[sem], xs[sem]]
        fonte[y0 + ys, x0 + xs] = cor
    return nc - 1


def _emenda_macia(out, fonte, buraco, fora, raio, limite=(3.0, 10.0)):
    """Sem degrau na beira do `buraco`: a diferença de tom (só a baixa frequência, `raio` px) entre o que está em volta
    (sem o que é `fora`: os traços escuros e as peças) e o preenchimento junto da beira, levada para dentro, macia (o
    inpaint da diferença, canal a canal); para escurecer, só até `limite`[0] (a sombra das antigas não entra)."""
    anel_f = cv2.dilate(buraco.astype(np.uint8), np.ones((2 * raio + 1,) * 2, np.uint8)).astype(bool) & ~buraco & ~fora
    anel_d = buraco & ~cv2.erode(buraco.astype(np.uint8), np.ones((2 * raio + 1,) * 2, np.uint8)).astype(bool)
    def media(img, m):
        w = m.astype(np.float32)
        return cv2.GaussianBlur(img * w[..., None], (0, 0), raio) / np.maximum(cv2.GaussianBlur(w, (0, 0), raio),
                                                                                1e-4)[..., None], \
            cv2.GaussianBlur(w, (0, 0), raio) > 0.05
    mf, okf = media(out, anel_f)
    md, okd = media(fonte, anel_d)
    beira = anel_d & okf & okd
    dif = np.zeros_like(out)
    dif[beira] = mf[beira] - md[beira]
    sem = (buraco & ~beira).astype(np.uint8)
    dif = np.clip(dif, -limite[0], limite[1])
    res = fonte.copy()
    for c in range(3):
        res[..., c] += np.where(buraco, cv2.inpaint(dif[..., c], sem, 5, cv2.INPAINT_TELEA), 0)
    return res


def tirar_poltronas_ta(Q, img, q=None, p=None):
    """O lugar das poltronas antigas (antes da trama dos tapetes e das poltronas novas, `poltronas_ta`)."""
    q, p = q or POLTRONAS_TA[Q.chave], p or POLTRONAS_PARAM_TA
    H, W = img.shape[:2]
    out = img.astype(np.float32)
    buraco = np.zeros((H, W), bool)
    vertical = np.zeros((H, W), bool)
    s = p["sombra_px"]
    for nome, cam, r, _, _ in q["pecas"]:
        k = 2 * q.get("folga_px", {}).get(nome, p["folga_px"]) + 1
        m = cv2.dilate(_mascara_peca(Q, cam, r).astype(np.uint8), np.ones((k, k), np.uint8))
        m |= cv2.warpAffine(m, np.float32([[1, 0, -s], [0, 1, s]]), (W, H))
        if nome in q.get("recorte_pt", {}):            # só dentro do recorte (o que fica em volta, como a cortina)
            (a0, b0), (a1, b1) = Q.p2q(*q["recorte_pt"][nome][:2]), Q.p2q(*q["recorte_pt"][nome][2:])
            rec = np.zeros_like(m)
            rec[int(np.ceil(b0)):int(b1), int(np.ceil(a0)):int(a1)] = 1
            m &= rec
        buraco |= m.astype(bool)
        if nome in q.get("sombra_parede", ()):
            vertical |= m.astype(bool)
    tapetes = [Q.preencher(lambda d, c=c, r=r: d.get("layer") == c and max(abs(u - v) for u, v in zip(d["rect"], r))
                           < 0.5) > 0.5 for c, r in q["tapetes"]]
    pecas = Q.preencher(lambda d: d.get("layer") in CAMADAS_MOVEIS_TA and not any(
        d.get("layer") == c and max(abs(u - v) for u, v in zip(d["rect"], r)) < 0.5 for c, r in q["tapetes"])) > 0.05
    # as peças que ficam (as mesinhas, o sofá; a mesa de centro, que no PDF só tem o contorno, pela cor de madeira) e
    # os rótulos não entram no buraco
    antigas = np.zeros((H, W), bool)
    for _, cam, r, _, _ in q["pecas"]:
        antigas |= _mascara_peca(Q, cam, r)
    lab_ = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    b_ = lab_[..., 2]
    madeira = cv2.morphologyEx(((b_.astype(np.int16) - cv2.medianBlur(b_, 51)) > p["madeira_b"]).astype(np.uint8),
                               cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
    madeira &= cv2.medianBlur(lab_[..., 0], 51) > p["fundo_claro"]      # só no piso claro (no vinílico, tudo é madeira)
    rotulos = _rotulos_mascara(Q, (H, W))
    kf = 2 * p["ficam_px"] + 1
    ficam = cv2.dilate(((pecas & ~antigas) | rotulos).astype(np.uint8), np.ones((kf, kf), np.uint8)).astype(bool) \
        | cv2.dilate(madeira.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    buraco &= ~ficam
    vertical &= buraco
    # os traços: bem mais escuros que o piso em volta (no travertino claro e no vinílico escuro)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    escuro = (cinza < p["escuro_abs"]) | (cinza.astype(np.int16) - cv2.medianBlur(cinza, 31) < -p["escuro_rel"])
    lb_ = 2 * p["livre_borda_px"] + 1
    livre = ~cv2.dilate((pecas | buraco | escuro).astype(np.uint8), np.ones((lb_, lb_), np.uint8)).astype(bool)
    modelos = [_tapete_limpo(out, t, livre, p["banda_px"]) for t in tapetes]
    lp = 2 * p["livre_px"] + 1
    objetos = cv2.dilate((pecas | buraco | rotulos).astype(np.uint8),
                         np.ones((lp, lp), np.uint8)).astype(bool)
    # a borda de cada tapete também (o miolo do tapete não vem de junto da borda, nem o piso), e a beira dos traços
    tracos = cv2.dilate(escuro.astype(np.uint8), np.ones((2 * p["traco_px"] + 1,) * 2, np.uint8)).astype(bool)
    proibido = objetos | tracos
    kb = 2 * p["banda_px"][1] + 3
    for t in tapetes:
        proibido |= cv2.morphologyEx(t.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((kb, kb), np.uint8)).astype(bool)
    fonte, falhas = _tapar_linhas(out, buraco, tapetes, proibido, p["busca_px"], p["tol_lab"])
    # junto de uma parede, a sombra dela (que corre na vertical) volta: a luz de cada coluna em volta (fora do buraco e
    # das peças) sobre a luz do piso longe dela
    n_, lbv, stv, _ = cv2.connectedComponentsWithStats(vertical.astype(np.uint8))
    for i in range(1, n_):
        x, y, w, h = stv[i, :4]
        y0, y1 = max(0, y - 2 * h), min(H, y + 3 * h)
        m_ = lbv[y0:y1, x:x + w] == i
        L = out[y0:y1, x:x + w].mean(axis=2)
        ok = ~(objetos | buraco)[y0:y1, x:x + w] & (L > 120)
        col = np.array([np.median(L[ok[:, c], c]) if ok[:, c].sum() > 5 else np.nan for c in range(w)])
        col = np.interp(np.arange(w), np.nonzero(~np.isnan(col))[0], col[~np.isnan(col)])
        col = cv2.GaussianBlur(col.reshape(1, -1).astype(np.float32), (0, 0), 2).ravel()
        fator = np.clip(col / np.percentile(col, 80), 0.7, 1.0)
        sub = fonte[y0:y1, x:x + w]
        sub[m_] *= np.broadcast_to(fator, m_.shape)[m_][:, None]
    # o tapete e a borda dele sob as antigas: o tom limpo e o perfil da borda em volta (sem os tracejados e as peças)
    nb = sum(_tapete_por_perfil(out, fonte, buraco, livre, d, campo, p["banda_px"]) for d, _, campo in modelos)
    # o que não achou trecho livre (fora da borda dos tapetes, que o modelo refez): o inpaint do que já foi refeito
    for d, _, _ in modelos:
        falhas &= d >= p["banda_px"][1]
    if falhas.any():
        fonte = cv2.inpaint(np.clip(fonte, 0, 255).astype(np.uint8), falhas.astype(np.uint8), 3,
                            cv2.INPAINT_TELEA).astype(np.float32)
    fonte = _emenda_macia(out, fonte, buraco, tracos | pecas, p["emenda_px"])
    e = p["esfuma_px"]
    al = cv2.GaussianBlur(cv2.dilate(buraco.astype(np.uint8), np.ones((2 * e + 1,) * 2, np.uint8)).astype(np.float32),
                          (0, 0), e / 2)
    al[buraco] = 1
    out = out * (1 - al[..., None]) + fonte * al[..., None]
    print(f"    {Q.chave}: o lugar das {len(q['pecas'])} poltronas antigas refeito ({nb} partes nos tapetes"
          + (f"; {int(falhas.sum())} px sem trecho livre, no inpaint)" if falhas.any() else ")"))
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def poltronas_ta(Q, img, q=None):
    import final3840_casae as E
    import retoque_terreo_casae as T
    q, qe = q or POLTRONAS_TA[Q.chave], E.POLTRONAS_TE
    out = img.astype(np.float32)
    cor, a_m = E._modelo_poltrona_1p(qe)
    fx, fy = qe["modelo"]["frente"]
    for nome, _, r, (dx, dy), t_pt in q["pecas"]:
        (ax, ay), (bx_, by) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        cx, cy = (ax + bx_) / 2, (ay + by) / 2
        t = t_pt * Q.px_m / 56.69 if t_pt else max(bx_ - ax, by - ay)
        ang = np.degrees(np.arctan2(dx, dy) - np.arctan2(fx, fy))
        c2, a2 = E._girar_peca(cor, a_m, t / max(a_m.shape), ang)
        T.pousar_planta(out, c2, a2, float(cx), float(cy), t, qe["sombra"])
        T.pousar_planta(out, c2, a2, float(cx), float(cy), t, qe["sombra_contato"])
    print(f"    {Q.chave}: {len(q['pecas'])} poltronas no modelo da sala íntima da Casa E")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# 10a. Os sofás: estofados, como nas Casas B e D (`revisao_casab_2910.estofados_pdf_tb`: o linho com volume, a trama e os
# traços de dentro do PDF como costuras e vincos, com a sombra no piso), na silhueta de cada peça do PDF.
ESTOFADOS_TA = {
    "Terreo": [dict(RB.ESTOFADOS_SUITES_TB, camada="ARQ_LAYOUT HUMANIZAÇÃO", semente=82, estofados=[
                   ("sofá curvo da varanda", [(1510.0, 578.9, 1613.6, 692.9)]),
                   ("sofá curvo da sala de estar", [(1690.2, 582.2, 1845.2, 724.0)])]),
               dict(RB.ESTOFADOS_SUITES_TB, camada="DOC_TEXTOS", semente=83, estofados=[
                   ("sofá reto da varanda", [(1446.3, 738.5, 1559.7, 764.0)]),
                   ("sofá do terraço gourmet", [(1096.7, 1550.0, 1122.2, 1663.3)])])],
    # o sofá em L da sala íntima (o assento, o encosto e os braços, seis peças) e as duas almofadas, por cima dele
    "1Pavimento": [dict(RB.ESTOFADOS_SUITES_TB, camada="ARQ_LAYOUT HUMANIZAÇÃO", semente=84, estofados=[
        ("sofá em L da sala íntima", [(1897.0, 1176.6, 1928.2, 1318.8), (1839.8, 1145.4, 1928.2, 1176.6),
                                      (1928.2, 1176.6, 1944.7, 1318.8), (1839.8, 1128.9, 1944.7, 1176.6),
                                      (1831.3, 1128.9, 1839.8, 1176.6), (1897.0, 1318.8, 1944.7, 1327.3)]),
        ("almofada de cima do sofá da sala íntima", [(1842.9, 1171.6, 1859.9, 1188.6)]),
        ("almofada de baixo do sofá da sala íntima", [(1884.9, 1298.8, 1901.9, 1315.8)])])]}


def estofados_ta(Q, img):
    for q in ESTOFADOS_TA.get(Q.chave, ()):
        img = RB.estofados_pdf_tb(Q, img, q, Q.chave)
    return img


# 10b. Os tapetes: a trama do tapete da Casa D (`final3840_casad.tapete_trama_d`: o relevo do tapete do bloco
# `conjunto_estar_tapete` da biblioteca na escala, só nos px do tapete, sem mudar o tom médio), em todos os tapetes do PDF.
TAPETES_TA = {"Terreo": dict(D.TAPETE_TRAMA_D, tapetes_pt=[("varanda", (1415.6, 602.9, 1585.7, 744.6)),
                                                           ("sala de estar", (1699.0, 590.2, 1925.7, 816.7))],
                             miolo=("varanda", "sala de estar")),
              # no 1º Pavimento, os das suítes ficam sob as camas: a cor é a da faixa junto à borda
              "1Pavimento": dict(D.TAPETE_TRAMA_D, tapetes_pt=[("suíte 1", (2047.6, 1553.7, 2246.0, 1678.5)),
                                                               ("suíte 2", (1457.4, 1218.6, 1655.8, 1331.9)),
                                                               ("suíte 3", (1433.3, 594.7, 1631.7, 725.1)),
                                                               ("suíte master", (1209.3, 1431.7, 1407.7, 1567.7)),
                                                               ("sala íntima", (1812.1, 1146.1, 1925.5, 1344.5))],
                                 miolo=())}


def tapetes_ta(Q, img):
    q = TAPETES_TA.get(Q.chave)
    return D.tapete_trama_d(Q, img, q=q) if q else img


# As projeções tracejadas passam por cima das peças (`final3840_casaa_terreo.projecoes`): os traços delas que cruzam as
# peças trocadas voltam por cima, em preto ou branco pelo fundo (`preto_branco`), como na final.
def tracejados_ta(Q, img, zonas_pt):
    import final3840_casaa_terreo as T
    q = T.PROJ
    par = FA.paredes_pdf(Q)
    tracos = []
    doc = T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"])
    def total(k):
        return sum(e for k2, e, _ in doc if k2[1] == k[1] and abs(k2[2] - k[2]) <= 2)
    for k, ext, segs in doc:
        if total(k) > q["max_doc_pt"]:
            continue
        xm, ym = Q.p2q(*np.mean([((x0 + x1) / 2, (y0 + y1) / 2) for x0, y0, x1, y1 in segs], axis=0))
        if par[int(ym), int(xm)] > 0.5 or any(a <= xm <= c and b <= ym <= d for a, b, c, d in q["fora_q"]):
            continue
        tracos += [sg for sg in segs if any(a0 <= (sg[0] + sg[2]) / 2 <= a1 and b0 <= (sg[1] + sg[3]) / 2 <= b1
                                            for a0, b0, a1, b1 in zonas_pt)]
    out, _ = T.preto_branco(Q, img, tracos)
    print(f"    {Q.chave}: {len(tracos)} traços das projeções de novo por cima das peças trocadas")
    return out


# A revisão de 29/10 da Casa A (itens 1 a 10, com o 4 em branco sem tracejado; o 11 espera o OK), por pavimento, sobre a
# final aprovada (a do commit das junções das portas): o Térreo primeiro, porque o Subsolo nevoa as peças dele.
def tracejados_zonas_ta(q, folga_pt=12.0):
    return [(r[0] - folga_pt, r[1] - folga_pt, r[2] + folga_pt, r[3] + folga_pt) for _, _, r, _, _ in q["pecas"]]


def revisao_ta(chave, img, terreo=None):
    Q = FA.QuadroA(chave)
    out = img
    if chave == "Terreo":
        out = jardins_ta(Q, out)                                  # 1 e 3
        out = servico_ta(Q, out)                                  # 2
        out = faixa_branca_ta(Q, out)                             # 4
    out = elevador_ta(Q, out)                                     # 5
    if chave in ELEVADOR_TA["shafts_pt"]:
        out = shafts_ta(Q, out)
    if chave == "Subsolo":
        out = nevoado_ta(Q, out, terreo)                          # 6
    if chave in POLTRONAS_TA:                                     # 9 e 10
        out = tirar_poltronas_ta(Q, out)
        out = tapetes_ta(Q, out)
        out = poltronas_ta(Q, out)
        out = estofados_ta(Q, out)
    if chave == "Terreo":
        out = Cc.jogos_varanda_tc(Q, mesas_varanda_ta(Q, out), JOGOS_VARANDA_TA)   # 7
        out = jantar_ta(Q, out)                                   # 8
        out = tracejados_ta(Q, out, tracejados_zonas_ta(POLTRONAS_TA[chave]))
    return out


# Os antes/depois da revisão (retângulos em pt, por pavimento e item).
ANTES_DEPOIS_TA = {
    "Terreo": {"item1_jardim_479": (1262, 1729, 1509, 1899), "item2_servico_descoberta": (1495, 1784, 1700, 2062),
               "item3_jardim_1746": (1998, 1089, 2244, 1260), "item4_faixa_branca": (2270, 1030, 2530, 1125),
               "item5_elevador": (2000, 1200, 2170, 1400), "item7_8_jogos_jantar": (1415, 1070, 1900, 1355),
               "item9_10_varanda_estar": (1370, 575, 1935, 1035), "item9_10_gourmet": (1060, 1430, 1160, 1680),
               "item9_escritorio": (2265, 700, 2345, 790)},
    "Subsolo": {"item5_elevador": (2000, 1200, 2170, 1400), "item6_nevoado": (550, 530, 1160, 1235)},
    "1Pavimento": {"item5_elevador": (2000, 1200, 2170, 1400), "item9_10_sala_intima": (1790, 1100, 1960, 1400),
                   "item9_10_suite2": (1400, 1170, 1670, 1380), "item9_10_suite_master": (1200, 1420, 1520, 1615),
                   "item10_tapetes_suites_1_3": None}}


def antes_depois_ta(chave, antes, depois, max_lado=1800):
    Q = FA.QuadroA(chave)
    for nome, r in ANTES_DEPOIS_TA[chave].items():
        if r is None:                                    # as suítes 1 e 3 lado a lado
            partes = []
            for rr in ((2040, 1545, 2255, 1690), (1425, 585, 1640, 735)):
                (x0, y0), (x1, y1) = Q.p2q(rr[0], rr[1]), Q.p2q(rr[2], rr[3])
                x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
                partes.append(np.vstack([antes[y0:y1, x0:x1], np.full((12, x1 - x0, 3), 255, np.uint8),
                                         depois[y0:y1, x0:x1]]))
            h = max(pp.shape[0] for pp in partes)
            junto = np.hstack([np.pad(partes[0], ((0, h - partes[0].shape[0]), (0, 24), (0, 0)), constant_values=255),
                               np.pad(partes[1], ((0, h - partes[1].shape[0]), (0, 0), (0, 0)), constant_values=255)])
        else:
            (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
            x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
            a, d = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
            lado = (x1 - x0) <= (y1 - y0) * 1.3
            junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), d]) if lado else \
                np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), d])
        k = min(3.0, max_lado / max(junto.shape[:2]))
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
        arq = FA.CASA / "renders" / f"POE642_CasaA_PH_{chave}_2910_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {arq.name}")


FINAIS_TA = {"Terreo": FINAL_TERREO, "Subsolo": FINAL_SUBSOLO, "1Pavimento": FINAL_1PAV}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portas", action="store_true", help="as portas e as junções das suítes do 1º Pavimento")
    ap.add_argument("--revisao", action="store_true", help="os itens 1 a 10 da revisão de 29/10, nos três pavimentos")
    ap.add_argument("--antes", type=Path, default=FINAL_1PAV)
    ap.add_argument("--saida", type=Path, default=FINAL_1PAV)
    ap.add_argument("--pasta_antes", type=Path, default=None,
                    help="--revisao: a pasta das finais de antes (por padrão, as próprias finais, sobrescritas)")
    a = ap.parse_args()
    if a.revisao:
        antes = {k: (a.pasta_antes / v.name if a.pasta_antes else v) for k, v in FINAIS_TA.items()}
        imgs = {k: cv2.imread(str(v)) for k, v in antes.items()}
        terreo = revisao_ta("Terreo", imgs["Terreo"])
        saidas = {"Terreo": terreo, "Subsolo": revisao_ta("Subsolo", imgs["Subsolo"], terreo),
                  "1Pavimento": revisao_ta("1Pavimento", imgs["1Pavimento"])}
        for k, out in saidas.items():
            cv2.imwrite(str(FINAIS_TA[k]), out)
            print(FINAIS_TA[k])
            antes_depois_ta(k, imgs[k], out)
        return
    if not a.portas:
        ap.error("indique o pedido: --portas ou --revisao")
    Q = FA.QuadroA("1Pavimento")
    img = cv2.imread(str(a.antes))
    out = portas_suites_ta(Q, img)
    cv2.imwrite(str(a.saida), out)
    print(a.saida)


if __name__ == "__main__":
    main()

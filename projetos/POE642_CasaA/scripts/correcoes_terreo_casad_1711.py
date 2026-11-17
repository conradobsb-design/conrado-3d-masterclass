"""Térreo da Casa D, as correções de 17/11 vendo o Térreo ("VAMOS VER COMO ESTÁ O TERREO DA CASA D"), na final e direto
nos 12K A e B, cada peça na escala de cada imagem, no afim afinado ali (`correcoes_terreo_casab_1611.Mapa.local`). Antes
deste roteiro, as bancadas de Dekton Danae (`danae_bancadas_1611.py ... D_Terreo`: "SIM, CONFIRA AS BANCADAS DA CASA D").

1. `banho_gourmet` ("CORRIJA ESSES RESIDUOS DE PISO ANTIGO. E CORRIJA O PRETO ANTIGO DAS PAREDES."): as 2 faixas claras
   em pé no banho gourmet (onde o PDF não tem nada: o piso antigo) viram o piso de cada lado, em espelho; os fios pretos
   e cinza-escuros rente às faces das paredes (o preto antigo) ficam no cinza das paredes.
2. `folhas_correr` ("CORRIJA OS LINKS ENTRE AS FOLHAS DE CORRER. ELAS PRECISAM ESTAR CONECTADAS, NÃO FLUTUANDO."): as 4
   folhas de vidro entre a varanda gourmet e o living: as de planos diferentes passam uma pela outra (o trespasse), as
   do mesmo plano se encontram; cada folha esticada com o próprio perfil e a ponta dela levada ao novo fim.
3. `grama_suite3` ("REMOVA ESSES PONTOS TRACEJADOS E CORRIJA A GRAMA"): a faixa de Bege Bahia à direita da parede da
   suíte 3: os pontinhos claros do tracejado e a grama clara junto a ela viram a grama de logo além, em espelho.
4. `ripado_master` ("MELHORE A REPRESENTAÇÃO DO AMADEIRADO EXTERNO EM L, REVESTINDO O QUARTO POR FORA DAS FOLHAS DE
   VIDRO."; "USE O MESMO AMADEIRADO PARA REVESTIR"): o ripado em L da suíte master (as ripas da ARQ_ELEMENTOS FIXOS, à
   esquerda e em cima, por fora das folhas de vidro) no ripado de nogueira do painel da suíte 3
   (`um_pav_casaa_1111.FOLHAS_1P`: as ripas, as juntas, a luz, o contorno e a sombra curta para fora).
5. `cooktop_gourmet` ("REMOVA AS LINHAS TÉCNICAS"): o retângulo claro em volta do cooktop da ilha gourmet (o recorte
   da ARQ_LOUÇAS E METAIS) sai, com o granito em volta (inpaint só nos px claros do traço); o cooktop fica.
6. `mesas_varanda` ("TOM PEDRA TERRACOTA RAJADA E MADEIRA NOGUEIRA"): as 2 mesas de centro da varanda gourmet: a oval
   maior em pedra terracota rajada (o terracota com os veios claros) e a redonda menor em nogueira (o tampo liso da mesa
   de centro de nogueira da biblioteca da Casa A), com a luz de cada uma.
7. `louceiro_despensa` ("MELHORE O ASPECTO DAS PORTAS E REMOVA RESÍDUOS DO PISO ANTERIOR"): as soleiras claras das
   portas do louceiro e da despensa viram o piso da cozinha, em espelho; as folhas de giro (abertas junto à parede da
   esquerda, no retângulo do PDF) de novo na madeira das portas, com o contorno e a sombra curta; os batentes do vão no
   cinza das paredes.
8. `movel_jantar` ("ESSE MÓVEL DA SALA DE JANTAR NO TOM SÓLIDO PADRÃO QUE ESTAMOS ADOTANDO."): o móvel junto à parede
   da sala de jantar (o retângulo da ARQ_MOBILIÁRIO) na cor sólida dos armários, sem os traços técnicos.
9. `porta_hall` ("PORTA NO MESMO TOM FORA A FORA, O TOM MAIS ESCURO, ONDE VEMOS NA MAIOR PARTE DELA"): a folha de correr
   deitada do hall de entrada, de ponta a ponta no perfil escuro dela (o trecho claro da ponta da direita sai).

10. `soleiras_residuos` ("CORRIJA O CONTORNO DAS PORTAS, AINDA COM RESÍDUOS DO PISO ANTERIOR."; "AQUI TAMBÉM TEM
   RESÍDUOS DO PISO ANTERIOR. REMOVA-OS."): as faixas claras do piso antigo nos vãos da área descoberta (a de cima, sobre
   as 2 folhas de vidro, e a da esquerda, junto à folha de correr) e da área de serviço (junto ao gás) viram o piso de
   cada lado (em espelho; onde do outro lado há folha, só do lado livre); as folhas ficam.
11. `carros` ("REMOVA OS RESÍDUOS DO PISO ANTERIOR E MELHORE O CONTORNO DOS CARROS"; "REFAÇA OS CARROS SOBRE O
   PISO"): cada um dos 3 carros da garagem tirado pela silhueta (o branco e o cinza neutros, os furos fechados) e pousado
   de novo sobre o piso refeito: numa faixa em volta dele (`faixa_px`), o piso da garagem tecido de novo (quilting das
   faixas limpas entre os carros, no tom do piso em volta), sem o halo antigo; a borda do carro macia (a silhueta
   encolhida e desfocada) e a sombra curta de contato.
12. `madeira_hall` ("VAMOS MELHORAR O REVESTIMENTO DE MADEIRA. USANDO O PADRÃO QUE ADOTAMOS AO REDOR DAS JANELAS."): as
   4 faixas de madeira dos 2 trechos de parede do hall de entrada (dos dois lados de cada um) no ripado de nogueira das
   janelas (o do painel da suíte 3 e do L da suíte master).

  python3 correcoes_terreo_casad_1711.py final [--saida <png>]
  python3 correcoes_terreo_casad_1711.py doze [--opcao AB] [--saida <jpg com {}>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                   # noqa: E402

FINAL = DF.PLANTAS["D_Terreo"]
DOZE = DF.DOZE_K["D_Terreo"]
RAIZ = AQUI.parents[1]

BANHO_GOURMET = {"faixas": [(1445.5, 371.5, 1450.0, 467.0), (1552.5, 373.5, 1563.0, 428.0)],
                 "caixa": (1376, 358, 1724, 476), "preto_lum": 50, "escuro_lum": 74, "parede": 80}
# as folhas (colunas em px da final, bordas) e as pontas: (folha, ponta, fim antigo, fim novo) — o fim é a borda da
# última linha da folha (embaixo) ou da primeira (em cima)
FOLHAS = {"B": (1803.5, 1807.5), "A": (1806.5, 1809.5)}
TRESPASSES = [("B", "cima", 818.0, 809.0), ("B", "baixo", 941.0, 943.5),
              ("B", "cima", 946.0, 943.5), ("B", "baixo", 1069.0, 1077.0),
              ("A", "baixo", 813.0, 821.0), ("A", "cima", 1074.0, 1066.0)]
GRAMA_S3 = {"faixa": (2531.5, 1493.5, 2535.0, 1760.0), "creme_rb": 26, "creme_lum": 150}
RIPADO_MASTER = [((623.28, 1325.09, 627.46, 1553.77), "x-"), ((627.46, 1325.09, 841.08, 1329.27), "y-")]
# os 4 traços do retângulo técnico (px da final: o retângulo a cobrir e o deslocamento da fonte do granito)
COOKTOP = {"tracos": [((1528.0, 616.4, 1586.0, 618.2), (0.0, -2.6)), ((1582.4, 615.5, 1585.6, 652.0), (3.6, 0.0)),
                      ((1528.4, 615.5, 1531.6, 652.0), (-3.4, 0.0)), ((1528.0, 647.6, 1541.0, 651.0), (0.0, 4.0)),
                      ((1571.5, 647.6, 1586.0, 651.0), (0.0, 4.0)), ((1541.0, 648.6, 1571.5, 651.0), (0.0, 3.5))],
           "caixa": (1515, 600, 1600, 665)}
MESAS = {"caixa": (1528, 1028, 1626, 1096), "grande": (1566.0, 1057.0), "pequena": (1601.5, 1075.0),
         "rb": (26.0, 12.0), "terracota": (78, 106, 166), "veio": (186, 204, 228), "semente": 1717,
         "nogueira": (RAIZ / "POE642_CasaA/biblioteca-objetos/02-terreo/sala-de-estar/"
                      "mesa-centro-redonda-nogueira-adorno.png", (100, 470, 280, 680))}
LOUCEIRO = {"soleiras": [((2099, 484, 2152, 501), "y", "ambos"), ((2099, 552, 2152, 570), "y", "ambos")],
            # a sombra da folha antiga à direita dela (o rótulo DESPENSA começa em x 2110 a partir de y 596: ali, de cima)
            "velhas": [((2106.7, 462.0, 2110.0, 488.0), (4.0, 0.0)), ((2106.7, 445.5, 2110.0, 462.0), (0.0, 16.0)),
                       ((2106.7, 565.6, 2110.0, 596.0), (4.0, 0.0)),
                       ((2106.7, 596.0, 2110.0, 608.5), (0.0, -11.0))],
            "folhas": [(2104.4, 446.2, 2106.7, 488.0), (2104.4, 565.6, 2106.7, 607.4)],
            "batentes": [(2101.4, 488.0, 2105.0, 496.9), (2145.6, 488.0, 2149.0, 496.9),
                         (2101.4, 556.6, 2105.0, 565.6), (2145.6, 556.6, 2149.0, 565.6)],
            "parede": (80, 80, 80)}
# (caixa de busca em px da final, o eixo da espessura da faixa, de que lado vem o piso)
SOLEIRAS = [((2196, 553, 2300, 569), "y", "antes"), ((2178, 497, 2196, 558), "x", "antes"),
            ((2549, 423, 2569, 487), "x", "ambos")]
CARROS = {"caixas": [(2650, 466, 2814, 790), (2816, 466, 2982, 790), (2984, 466, 3150, 790)], "rb_carro": 30,
          "faixa_px": 20.0, "amostras": [(2800, 490, 2830, 760), (2961, 490, 2983, 760)], "p_px": 11, "sobra_px": 4,
          "sombra": 0.34}
MADEIRA_HALL = [((2426.6, 911.6, 2430.9, 978.2), "x-"), ((2440.3, 911.6, 2444.7, 978.6), "x+"),
                ((2426.6, 1129.3, 2430.9, 1201.6), "x-"), ((2440.3, 1129.3, 2444.7, 1201.6), "x+")]
MOVEL_JANTAR = {"móvel do jantar": (2058.1, 801.5, 2093.9, 921.0)}
PORTA_HALL = {"folha": (2317.5, 1096.5, 2462.5, 1100.5), "claro_x": 2430.5, "fonte_x": 2400.0, "ponta_px": 1.0}


def _local(out, mp, caixa):
    return mp.local(out, caixa) if mp.ref is not None else mp


def _caixa(r, folga):
    return (int(r[0]) - folga, int(r[1]) - folga, int(np.ceil(r[2])) + folga, int(np.ceil(r[3])) + folga)


def _lum(px):
    return px.astype(np.float32).mean(axis=-1)


def _neutro(px, tol):
    p = px.astype(np.int16)
    return (p.max(axis=-1) - p.min(axis=-1)) < tol


# ----------------------------------------------------------------------------------------------------------------------
def _espelho_x(out, m, r):
    """O retângulo r (px da final): cada metade recebe, em espelho, as colunas do seu lado."""
    x0, y0, x1, y1 = m.ret(r)
    X0, X1 = int(round(x0)), int(round(x1))
    Y0, Y1 = int(round(y0)), int(round(y1))
    meio = (X0 + X1) / 2
    fonte = out.copy()
    for x in range(X0, X1):
        src = 2 * X0 - 1 - x if x < meio else 2 * X1 - 1 - x
        out[Y0:Y1, x] = fonte[Y0:Y1, src]


def _espelho_y(out, m, r):
    x0, y0, x1, y1 = m.ret(r)
    X0, X1 = int(round(x0)), int(round(x1))
    Y0, Y1 = int(round(y0)), int(round(y1))
    meio = (Y0 + Y1) / 2
    fonte = out.copy()
    for y in range(Y0, Y1):
        src = 2 * Y0 - 1 - y if y < meio else 2 * Y1 - 1 - y
        out[y, X0:X1] = fonte[src, X0:X1]


def _soleira(out, m, caixa, eixo, lado, rb_min=12, lum_min=160):
    """A faixa clara do piso antigo na caixa (px da final) vira o piso de cada lado, em espelho ao longo da espessura
    (eixo "y": a faixa deitada); `lado` "antes" (de cima ou da esquerda), "depois" ou "ambos"."""
    X0, Y0, X1, Y1 = (int(round(v)) for v in m.ret(caixa))
    reg = out[Y0:Y1, X0:X1]
    I = reg.astype(np.int16)
    creme = ((I[..., 2] - I[..., 0]) > rb_min) & (I.mean(-1) > lum_min)
    k = 2 * int(np.ceil(1.0 * m.s)) + 1
    creme = cv2.dilate(creme.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    creme &= ~(_neutro(reg, 10) & (np.abs(_lum(reg) - 80) < 8))          # a parede fica
    if not creme.any():
        return 0
    fonte = out.copy()
    ys, xs = np.nonzero(creme)
    if eixo == "y":
        a, b = Y0 + ys.min(), Y0 + ys.max()
        for y, x in zip(Y0 + ys, X0 + xs):
            usa_antes = lado == "antes" or (lado == "ambos" and y < (a + b) / 2)
            src = 2 * a - 1 - y if usa_antes else 2 * b + 1 - y
            out[y, x] = fonte[src, x]
    else:
        a, b = X0 + xs.min(), X0 + xs.max()
        for y, x in zip(Y0 + ys, X0 + xs):
            usa_antes = lado == "antes" or (lado == "ambos" and x < (a + b) / 2)
            src = 2 * a - 1 - x if usa_antes else 2 * b + 1 - x
            out[y, x] = fonte[y, src]
    return int(creme.sum())


def soleiras_residuos(out, mp, q=SOLEIRAS):
    n = 0
    for caixa, eixo, lado in q:
        m = _local(out, mp, (caixa[0] - 20, caixa[1] - 20, caixa[2] + 20, caixa[3] + 20))
        n += _soleira(out, m, caixa, eixo, lado)
    print(f"    área descoberta e área de serviço: as faixas do piso antigo nos vãos no piso de cada lado ({n} px)")


def carros(out, mp, q=CARROS):
    from scipy import ndimage
    from texturizar_base import quilting
    xs_ = [v for c in q["caixas"] for v in (c[0], c[2])]
    ys_ = [v for c in q["caixas"] for v in (c[1], c[3])]
    m = _local(out, mp, (min(xs_), min(ys_), max(xs_), max(ys_)))
    fontes = []
    for a in q["amostras"]:
        X0, Y0, X1, Y1 = (int(round(v)) for v in m.ret(a))
        fontes.append(out[Y0:Y1, X0:X1].astype(np.float32))
    tom = np.median(np.concatenate([f_.reshape(-1, 3) for f_ in fontes]), axis=0)
    p = max(8, int(round(q["p_px"] * m.s)))
    sobra = max(3, int(round(q["sobra_px"] * m.s)))
    rng = np.random.default_rng(1718)
    for caixa in q["caixas"]:
        X0, Y0, X1, Y1 = (int(round(v)) for v in m.ret(caixa))
        reg = out[Y0:Y1, X0:X1]
        h, w = reg.shape[:2]
        I = reg.astype(np.int16)
        carro = ((I[..., 2] - I[..., 0]) < q["rb_carro"]).astype(np.uint8)
        k = 2 * int(np.ceil(1.5 * m.s)) + 1
        carro = cv2.morphologyEx(carro, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(carro, 8)
        if n < 2:
            continue
        carro = ndimage.binary_fill_holes(lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))))
        # o piso novo numa faixa em volta, no tom do piso do lugar
        D = int(np.ceil(q["faixa_px"] * m.s))
        faixa = cv2.dilate(carro.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * D + 1,) * 2))
        piso = quilting(fontes, h, w, p=p, sobra=sobra, candidatos=300, rng=rng)
        fora = (cv2.dilate(faixa, np.ones((5, 5), np.uint8)) > 0) & ~(faixa > 0)
        if fora.any():
            piso *= (np.median(reg[fora].reshape(-1, 3).astype(np.float32), axis=0) / np.maximum(tom, 1))[None, None]
        a_f = cv2.GaussianBlur(faixa.astype(np.float32), (0, 0), 1.5 * m.s)
        a_f = np.maximum(a_f, cv2.erode(faixa, np.ones((3, 3), np.uint8)).astype(np.float32))
        novo = reg.astype(np.float32) * (1 - a_f[..., None]) + piso * a_f[..., None]
        # a sombra curta de contato e o carro por cima, a borda macia
        e = max(1, int(round(0.8 * m.s)))
        core = cv2.erode(carro.astype(np.uint8), np.ones((2 * e + 1, 2 * e + 1), np.uint8)).astype(np.float32)
        ca = np.clip(cv2.GaussianBlur(core, (0, 0), 0.7 * m.s) * 1.15, 0, 1)
        M = np.float32([[1, 0, -1.2 * m.s], [0, 1, 1.6 * m.s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(carro.astype(np.float32), M, (w, h)), (0, 0), 2.2 * m.s)
        novo *= (1 - q["sombra"] * sb * (1 - ca))[..., None]
        novo = novo * (1 - ca[..., None]) + reg.astype(np.float32) * ca[..., None]
        out[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    print("    garagem: os 3 carros pousados de novo sobre o piso refeito em volta (sem o halo antigo), a borda macia e a "
          "sombra curta")


def madeira_hall(out, mp, q=MADEIRA_HALL):
    import um_pav_casaa_1111 as U
    m = _local(out, mp, (2400, 890, 2470, 1215))
    for i, (r, lado) in enumerate(q):
        _ripado(out, m, r, lado, U.FOLHAS_1P, np.random.default_rng(1720 + i))
    print("    hall: as 4 faixas de madeira das paredes no ripado de nogueira das janelas")


def banho_gourmet(out, mp, q=BANHO_GOURMET):
    m = _local(out, mp, q["caixa"])
    for r in q["faixas"]:
        _espelho_x(out, m, r)
    X0, Y0, X1, Y1 = (int(v) for v in m.ret(q["caixa"]))
    reg = out[Y0:Y1, X0:X1]
    g = _lum(reg)
    neu = _neutro(reg, 16)
    parede = neu & (np.abs(g - q["parede"]) < 6)
    k = 2 * int(np.ceil(3 * m.s)) + 1
    perto = cv2.dilate(parede.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    preto = neu & (g < q["preto_lum"]) & perto
    k2 = 2 * int(np.ceil(1.2 * m.s)) + 1
    ext = (cv2.dilate(preto.astype(np.uint8), np.ones((k2, k2), np.uint8)) > 0) & neu & (g < q["escuro_lum"])
    cor = np.median(reg[parede].reshape(-1, 3), axis=0)
    reg[ext] = cor.astype(np.uint8)
    print(f"    banho gourmet: as 2 faixas do piso antigo no piso de cada lado; {int(ext.sum())} px do preto antigo nas "
          f"faces das paredes no cinza delas")


def _esticar(out, m, cols, ponta, antigo, novo, c_px=2.0):
    X0, X1 = int(round(m.x(cols[0]))), int(round(m.x(cols[1])))
    C = max(1, int(round(c_px * m.s)))
    A, N = int(round(m.y(antigo))), int(round(m.y(novo)))
    if ponta == "baixo":
        cap = out[A - C:A, X0:X1].copy()
        perfil = np.median(out[A - C - int(10 * m.s):A - C - int(2 * m.s), X0:X1], axis=0)
        if N - C > A - C:
            out[A - C:N - C, X0:X1] = perfil.astype(np.uint8)[None]
        out[N - C:N, X0:X1] = cap
    else:
        cap = out[A:A + C, X0:X1].copy()
        perfil = np.median(out[A + C + int(2 * m.s):A + C + int(10 * m.s), X0:X1], axis=0)
        if N + C < A + C:
            out[N + C:A + C, X0:X1] = perfil.astype(np.uint8)[None]
        out[N:N + C, X0:X1] = cap


def folhas_correr(out, mp, q=TRESPASSES, f=FOLHAS):
    m = _local(out, mp, (1780, 680, 1830, 1215))
    for folha, ponta, antigo, novo in sorted(q, key=lambda t: t[0] != "B"):
        _esticar(out, m, f[folha], ponta, antigo, novo)
    print("    living/varanda: as 4 folhas de correr ligadas (o trespasse entre os planos, o encontro no mesmo plano)")


def grama_suite3(out, mp, q=GRAMA_S3):
    r = q["faixa"]
    m = _local(out, mp, _caixa(r, 20))
    x0, y0, x1, y1 = m.ret(r)
    Xa, Xb = int(np.floor(x0)), int(round(x1))
    Y0, Y1 = int(round(y0)), int(round(y1))
    reg = out[Y0:Y1, Xa:Xb]
    I = reg.astype(np.int16)
    creme = ((I[..., 2] - I[..., 0]) > q["creme_rb"]) & (I.mean(-1) > q["creme_lum"])
    for j, x in enumerate(range(Xa, Xb)):
        src = 2 * Xb - 1 - x
        tira = ~creme[:, j]
        out[Y0:Y1, x][tira] = out[Y0:Y1, src][tira]
    print("    suíte 3: os pontinhos do tracejado e a grama clara junto à faixa de Bege Bahia viram grama")


def _ripado(out, m, r, lado, qa, rng):
    s = m.s
    rm = m.ret(r)
    f = int(np.ceil(5 * s))
    X0, Y0 = int(np.floor(rm[0])) - f, int(np.floor(rm[1])) - f
    X1, Y1 = int(np.ceil(rm[2])) + f, int(np.ceil(rm[3])) + f
    w, h = X1 - X0, Y1 - Y0
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    loc = (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)
    A = alfa_ret(loc, (h, w))
    vert = lado in ("x-", "x+")
    dx, dy = {"x-": (-1.0, 0.6), "x+": (1.0, 0.6), "y-": (-0.6, -1.0), "y+": (0.6, 1.0)}[lado]
    sb = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, dx * s], [0, 1, dy * s]]), (w, h)), (0, 0), 0.9 * s)
    reg *= (1 - qa["sombra"] * sb * (1 - A))[..., None]
    ys = (np.arange(h, dtype=np.float32) + 0.5)[:, None] * np.ones((1, w), np.float32)
    xs = (np.arange(w, dtype=np.float32) + 0.5)[None, :] * np.ones((h, 1), np.float32)
    veio = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0),
                            sigmaX=(0.6 if vert else 6.0) * s, sigmaY=(6.0 if vert else 0.6) * s)
    veio /= max(float(veio.std()), 1e-6)
    rel = np.clip((xs - loc[0]) / max(loc[2] - loc[0], 1e-3) if vert else (ys - loc[1]) / max(loc[3] - loc[1], 1e-3),
                  0, 1)
    luz = 1 + qa["luz"] * (rel - 0.5) * (-1 if lado in ("x-", "y-") else 1)
    cor = np.float32(qa["madeira"])[None, None] * (luz * (1 + qa["veio"] * veio))[..., None]
    fase = np.mod((ys - loc[1]) if vert else (xs - loc[0]), qa["ripa_px"] * s)
    jp = qa["junta_px"] * s
    jt = np.clip(1 - np.abs(fase - jp / 2) / (jp / 2 + 0.5), 0, 1) * qa["junta_forca"]
    cor = cor * (1 - jt[..., None]) + np.float32(qa["junta"]) * jt[..., None]
    cp = qa["contorno_px"] * s
    dentro = alfa_ret((loc[0] + cp, loc[1] + cp, loc[2] - cp, loc[3] - cp), (h, w))
    reg = reg * (1 - A[..., None]) + cor * A[..., None]
    borda = np.clip(A - dentro, 0, 1)[..., None]
    reg = reg * (1 - borda) + np.float32(qa["contorno"]) * borda
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def ripado_master(out, mp, q=RIPADO_MASTER):
    import um_pav_casaa_1111 as U
    m = _local(out, mp, (600, 1300, 860, 1570))
    for i, (r, lado) in enumerate(q):
        _ripado(out, m, r, lado, U.FOLHAS_1P, np.random.default_rng(1700 + i))
    print("    suíte master: o ripado de nogueira em L por fora das folhas de vidro, o do painel da suíte 3")


def cooktop_gourmet(out, mp, q=COOKTOP):
    m = _local(out, mp, q["caixa"])
    fonte = out.copy()
    for r, d in q["tracos"]:
        CB.copia(out, fonte, m, r, d)
    print("    gourmet: o retângulo técnico em volta do cooktop sai (o granito de logo ao lado)")


_NOG = {}


def _nogueira(q):
    if "t" not in _NOG:
        p, (x0, y0, x1, y1) = q["nogueira"]
        im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)[y0:y1, x0:x1, :3]
        _NOG["t"] = im.astype(np.float32)
    return _NOG["t"]


def _terracota(h, w, s, q):
    """O terracota rajado: o fundo com a nuvem suave e os veios claros finos e sinuosos (os cruzamentos do zero de dois
    ruídos lisos, um veio principal e outros mais finos), com a força variando ao longo deles."""
    rng = np.random.default_rng(q["semente"])

    def ruido(sig):
        n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sig * s)
        return n / max(float(n.std()), 1e-6)
    n1, na, nb, nf = ruido(8.0), ruido(4.0), ruido(2.2), ruido(5.0)
    veio = 0.85 * np.exp(-(na / 0.06) ** 2) + 0.45 * np.exp(-(nb / 0.045) ** 2)
    veio = np.clip(veio * np.clip(0.55 + 0.45 * nf, 0, 1), 0, 1)
    veio = cv2.GaussianBlur(veio, (0, 0), 0.3 * s)
    base = np.float32(q["terracota"])[None, None] * (1 + 0.07 * n1)[..., None]
    return base * (1 - 0.65 * veio[..., None]) + np.float32(q["veio"])[None, None] * 0.65 * veio[..., None]


def mesas_varanda(out, mp, q=MESAS):
    m = _local(out, mp, q["caixa"])
    X0, Y0, X1, Y1 = (int(v) for v in m.ret(q["caixa"]))
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    h, w = reg.shape[:2]
    rb = reg[..., 2] - reg[..., 0]
    a = np.clip((rb - q["rb"][0]) / q["rb"][1], 0, 1)
    g = reg.mean(-1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cg = (m.x(q["grande"][0]) - X0, m.y(q["grande"][1]) - Y0)
    cp = (m.x(q["pequena"][0]) - X0, m.y(q["pequena"][1]) - Y0)
    dg = np.hypot((xx - cg[0]) / 1.25, yy - cg[1])
    dp = np.hypot(xx - cp[0], yy - cp[1]) * 1.55
    grande = (dg < dp).astype(np.float32)
    mesa = a > 0.5
    luz = g / max(float(np.median(g[mesa])), 1.0)
    T = _terracota(h, w, m.s, q)
    N = _nogueira(q)
    lado = int(np.ceil(36 * m.s))
    Nm = cv2.resize(N, (lado, lado), interpolation=cv2.INTER_AREA)
    tn = np.empty_like(reg)
    tn[:] = Nm.mean(axis=(0, 1))
    py, px = int(cp[1] - lado / 2), int(cp[0] - lado / 2)
    ya, xa = max(py, 0), max(px, 0)
    yb, xb = min(py + lado, h), min(px + lado, w)
    tn[ya:yb, xa:xb] = Nm[ya - py:yb - py, xa - px:xb - px]
    tex = T * grande[..., None] + tn * (1 - grande[..., None])
    novo = tex * np.clip(luz, 0.6, 1.25)[..., None]
    reg = reg * (1 - a[..., None]) + novo * a[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    varanda gourmet: a mesa oval em pedra terracota rajada e a redonda em nogueira")


def louceiro_despensa(out, mp, q=LOUCEIRO):
    m = _local(out, mp, (2085, 430, 2165, 620))
    for r, d in q["velhas"]:
        CB.copia(out, out.copy(), m, r, d)
    for caixa, eixo, lado in q["soleiras"]:
        _soleira(out, m, caixa, eixo, lado)
    for r in q["batentes"]:
        CB.pintar(out, m, [(r, "ret", q["parede"], 0)])
    pq = CB.PORTAS_SERVICO
    for r in q["folhas"]:
        CB.sombra(out, m, r, pq["sombra"], dx=0.9, dy=0.0, sigma=0.6)
        borda = tuple(v * pq["borda"] for v in pq["madeira"])
        CB.pintar(out, m, [(r, "ret", pq["madeira"], 0), (r, "contorno", borda, pq["borda_px"])])
    print("    louceiro e despensa: as soleiras do piso antigo no piso da cozinha, os batentes no cinza das paredes, as "
          "folhas de giro de novo na madeira das portas")


def movel_jantar(out, mp, q=MOVEL_JANTAR):
    for nome, r in q.items():
        m = _local(out, mp, _caixa(r, 25))
        CB.armarios(out, m, {nome: r}, couro=False)


def porta_hall(out, mp, q=PORTA_HALL):
    r = q["folha"]
    m = _local(out, mp, _caixa(r, 20))
    x0, y0, x1, y1 = m.ret(r)
    Y0, Y1 = int(np.floor(y0)), int(np.ceil(y1))
    Xc = int(round(m.x(q["claro_x"])))
    Xf = int(round(m.x(q["fonte_x"])))
    P = max(1, int(round(q["ponta_px"] * m.s)))
    X0, X1 = int(round(x0)), int(round(x1))
    col = out[Y0:Y1, Xf].copy()
    ponta = out[Y0:Y1, X0:X0 + P][:, ::-1].copy()
    out[Y0:Y1, Xc:X1 - P] = col[:, None]
    out[Y0:Y1, X1 - P:X1] = ponta
    print("    hall: a folha de correr deitada no tom escuro de ponta a ponta")


PASSOS = (banho_gourmet, folhas_correr, grama_suite3, ripado_master, cooktop_gourmet, mesas_varanda,
          louceiro_despensa, movel_jantar, porta_hall, soleiras_residuos, carros, madeira_hall)


def aplicar(img, mp, passos=PASSOS):
    out = img.copy()
    for f in passos:
        f(out, mp)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    final = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(final, Mapa()))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        doze = cv2.imread(str(f))
        M = DF.afim_12k(final, doze)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = final
        out = aplicar(doze, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

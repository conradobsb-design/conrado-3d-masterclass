"""As peças da biblioteca do usuário no Subsolo da Casa A (12/11).

Usuário: "FIZ UMA BIBLIOTECA DE ITENS QUE PODEMOS UTILIZAR NA PLANTA DO SUBSOLO DA CASA A. [...] VEJA NA PASTA O QUE
PODEMOS SUBSTITUIR NA PLANTA E GANHAR MAIS REALISMO." A biblioteca (`biblioteca-objetos/`, PNG com transparência, vista
de cima, gerados no Higgsfield; aqui só a pasta `01-subsolo`, o LEIA-ME e o índice) foi comparada com a planta e as
trocas aprovadas pelo usuário:
  "1. SIGO COM A SUA RECOMENDAÇÃO. SEM ALTERAR A COMPOSIÇÃO" (academia: esteira-a, bicicleta-b, banco-supino);
  "2. VASO BRANCO E DEMAIS RECOMENDAÇÕES" (BH. FEM./MASC.: a bacia Carrara branca, a cuba esculpida no granito marrom
     da especificação e o chuveiro quadrado com braço);
  "3. BH SERV. MESMO BATENDO USE OS ITENS DA BIBLIOTECA E SUA RECOMENDAÇÃO PARA O CHUVEIRO QUADRADO";
  "4. OPÇÃO A" (sauna: o banco reto de travertino);
  "5. DEPÓSITO: FICA COMO ESTÁ"; "6. NÃO MEXA NOS PISOS."

Cada peça vai no retângulo do PDF da peça que ela substitui (a composição não muda), girada para o símbolo do PDF:
- **Academia (`ACADEMIA`):** as 2 esteiras, as 2 bicicletas e o supino no retângulo do PDF, todas com o console para
  a esquerda, como no PDF; no supino, a barra
  da biblioteca (1,1 m na escala do banco) é alongada até a do PDF (1,72 m) repetindo uma coluna da barra e do
  travessão do rack de cada lado do banco (`barra`), sem tocar no banco. Por baixo das peças antigas (e da sombra
  delas), o vinílico volta exato: as réguas da final (`REGUAS`, refeitas pelo `vinilico_foto.trocar` sobre a final de
  antes do vinílico, com a mesma semente; diferença zero com a final) vezes a luz do lugar, a luz da final sobre as
  réguas, levada para dentro do buraco pela média normalizada do piso em volta. A sombra curta das peças novas é a de
  `final3840_casaa.APARELHOS`.
- **Banhos (`BANHOS_BIB`):** as bacias no retângulo do vaso do PDF (a parede para a parede; antes, o retângulo no tom
  do piso em volta, `sob_peca`, para a borda da bacia não mostrar o vaso marrom), com a descarga cromada de novo por
  cima; nos BH. FEM./MASC., a cuba esculpida da biblioteca no retângulo da cuba do PDF (fatiada: os cantos e o
  meio, com a torneira, na escala da altura; as faixas lisas esticadas), com o sombreado dela (as bordas chanfradas e a
  sombra por dentro) sobre o granito marrom de antes (`fontes_procedurais.granito_referencia`) e a torneira cromada
  dela; a bancada de travertino bruto fica. No BH. SERV., a bancada no polígono do PDF com o granito da peça da
  biblioteca (tecido das faixas só de granito dela), com a borda de antes, e a cuba branca com a torneira da peça no
  retângulo da cuba do PDF (a cuba de semiencaixe passa da bancada, como no PDF). Os 3 chuveiros: a placa quadrada da
  biblioteca (`chuveiro-quadrado`), o braço e a canopla da `chuveiro-quadrado-parede`, o braço do comprimento do PDF
  até a parede; antes, o braço antigo (mais largo) vira piso, copiado do piso ao lado.
- **Sauna (`SAUNA_BIB`):** o banco reto de travertino da biblioteca no retângulo do banco do PDF (as pontas na escala
  da altura, o meio esticado no veio), no tom do banco de antes (0,90 do piso, regra de 10/11: em cima, mais escuro);
  a sombra de contato fica.
- Os pisos, as paredes, os rótulos e o depósito ficam como estavam.

  python3 biblioteca_subsolo_casaa_1211.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT` (a de antes desta rodada); sem --saida, grava a final do Subsolo
e os antes e depois `renders/POE642_CasaA_PH_Subsolo_1211_<trecho>_antes_depois.jpg`.
"""

import argparse
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
CASA = AQUI.parent
RAIZ_GIT = CASA.parent.parent
FINAL = CASA / "renders" / "POE642_CasaA_PH_Subsolo_final_rotulos.png"
BIB = CASA / "biblioteca-objetos" / "01-subsolo"
ANTES_COMMIT = "028a12f"
# as réguas do vinílico da academia (BGR) com o piso em alfa, na janela que começa em `origem` (px do quadro); refeitas
# pelo `vinilico_foto.trocar` sobre a final do commit `commit` (a de antes do vinílico)
REGUAS = CASA / "renders" / "POE642_CasaA_PH_Subsolo_vinilico_reguas_academia.png"
REGUAS_Q = {"origem": (1345, 1060), "commit": "7723238"}

ACADEMIA = {
    "pecas": [
        {"nome": "esteira 1", "png": "academia/esteira-a.png", "pt": (1270.0, 1343.0, 1360.7, 1382.7)},
        {"nome": "esteira 2", "png": "academia/esteira-a.png", "pt": (1270.0, 1399.7, 1360.7, 1439.4)},
        {"nome": "bicicleta 1", "png": "academia/bicicleta-b.png", "pt": (1298.4, 1493.6, 1346.6, 1513.4),
         },
        {"nome": "bicicleta 2", "png": "academia/bicicleta-b.png", "pt": (1298.4, 1550.3, 1346.6, 1570.1)},
        {"nome": "supino", "png": "academia/banco-supino.png", "pt": (1465.6, 1431.0, 1542.2, 1528.6),
         "barra": (170, 340)},       # as colunas (no PNG de pé) que se repetem: a barra e o travessão do rack
    ],
    "giro": "ccw",                   # o PNG de pé (console em cima) com o console para a esquerda, como no PDF
    "sombra": (0.30, 1.4, 1.6),      # força, distância e sigma (px): a de `final3840_casaa.APARELHOS`
    "busca_px": 30, "liga_px": 12, "desvio": 18, "folga_px": 2, "luz_sigma": 4.0,
}
BANHOS_BIB = {
    "vasos": [
        {"nome": "BH. FEM.", "png": "banho-feminino-academia/bacia-carrara.png", "pt": (1396.1, 1746.1, 1416.1, 1775.2),
         "giro": "180", "descarga": (1402.4, 1773.9, 1409.8, 1775.2)},
        {"nome": "BH. MASC.", "png": "banho-masculino-academia/bacia-carrara.png",
         "pt": (1518.0, 1746.1, 1538.0, 1775.2), "giro": "180", "descarga": (1524.3, 1773.9, 1531.7, 1775.2)},
        {"nome": "BH. SERV.", "png": "banho-de-servico/bacia-monte-carlo-sem-valvula.png",
         "pt": (929.9, 1135.2, 961.0, 1156.5), "giro": "ccw", "descarga": (929.9, 1142.7, 932.3, 1149.0)},
    ],
    # a cuba esculpida, girada 180° (a torneira junto à parede, embaixo): o recorte em volta da bacia (px do PNG
    # girado), as fatias em x (fixa, estica, fixa com a torneira, estica, fixa) e os fatores do granito
    "cuba": {"png": "banho-feminino-academia/cuba-esculpida-travertino.png", "recorte": (86, 80, 481, 395),
             "fatias": (60, 154, 234, 335), "rim": 1.10, "bacia": 0.86, "croma_torneira": 20,
             "torneira": (163, 186, 223, 315)},
    "servico": {"png": "banho-de-servico/cuba-servico-granito.png", "giro": "ccw", "borda": 0.62, "larg": 0.6,
                "faixa_lib": 6},
    "chuveiro": {"placa": "banho-feminino-academia/chuveiro-quadrado.png", "placa_q": (13, 13, 363, 371),
                 "parede": "banho-feminino-academia/chuveiro-quadrado-parede.png", "canopla_q": (119, 12, 186, 75),
                 "braco_q": (138, 100, 166, 101), "giros": {"antessala": "180", "banho feminino": "180",
                                                           "banho de serviço": "ccw"},
                 "limpa_px": 2, "sombra": (0.30, 1.0, 0.9)},
}
SAUNA_BIB = {"png": "sauna/banco-reto-travertino.png", "pontas": 60, "erosao_px": 3}
ANTES_DEPOIS = {"academia": (1330, 1040, 1900, 1530), "banhos_sauna": (1180, 1545, 1900, 1660),
                "bh_serv": (1085, 870, 1230, 1060)}


# ----------------------------------------------------------------------------------------------------------------------
def quieto(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


def ler_png(nome, cortar=True):
    """O PNG da biblioteca em BGRA float32 (0 a 255), recortado ao alfa."""
    P = cv2.imread(str(BIB / nome), cv2.IMREAD_UNCHANGED).astype(np.float32)
    if cortar:
        ys, xs = np.nonzero(P[..., 3] > 0)
        P = P[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return np.ascontiguousarray(P)


def girar(P, giro):
    if giro == "ccw":
        return np.ascontiguousarray(cv2.rotate(P, cv2.ROTATE_90_COUNTERCLOCKWISE))
    if giro == "cw":
        return np.ascontiguousarray(cv2.rotate(P, cv2.ROTATE_90_CLOCKWISE))
    if giro == "180":
        return np.ascontiguousarray(cv2.rotate(P, cv2.ROTATE_180))
    return P


def caixa_px(Q, r):
    (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def dentro(P, c):
    """A caixa (px) de P dentro de c, com a proporção de P, no meio."""
    x0, y0, x1, y1 = c
    s = min((x1 - x0) / P.shape[1], (y1 - y0) / P.shape[0])
    w, h = P.shape[1] * s, P.shape[0] * s
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


def esticar(P, eixo, trechos):
    """Fatia P no `eixo` (1: x, 0: y): `trechos` = [(a, b, novo)], cada fatia [a, b) levada a `novo` px (None: fica)."""
    partes = []
    for a, b, novo in trechos:
        f = P[:, a:b] if eixo == 1 else P[a:b]
        if novo is not None:
            novo = max(1, int(round(novo)))
            f = cv2.resize(f, (novo, f.shape[0]) if eixo == 1 else (f.shape[1], novo), interpolation=cv2.INTER_CUBIC)
            f[..., 3] = np.clip(f[..., 3], 0, 255)
        partes.append(f)
    return np.ascontiguousarray(np.concatenate(partes, axis=eixo))


def renderizar(P, c, H, W, ss=4, pad=6):
    """P (BGRA) no retângulo c (px, float) do quadro, com a cobertura exata: a janela (X0, Y0, X1, Y1), a cor
    pré-multiplicada (h x w x 3) e o alfa (h x w)."""
    x0, y0, x1, y1 = c
    X0, Y0 = max(int(np.floor(x0)) - pad, 0), max(int(np.floor(y0)) - pad, 0)
    X1, Y1 = min(int(np.ceil(x1)) + pad, W), min(int(np.ceil(y1)) + pad, H)
    pm = P.copy()
    pm[..., :3] *= pm[..., 3:4] / 255
    tw, th = max(1, int(round((x1 - x0) * ss))), max(1, int(round((y1 - y0) * ss)))
    r = cv2.resize(pm, (tw, th), interpolation=cv2.INTER_AREA)
    can = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss, 4), np.float32)
    ox, oy = int(round((x0 - X0) * ss)), int(round((y0 - Y0) * ss))
    can[oy:oy + th, ox:ox + tw] = r[:can.shape[0] - oy, :can.shape[1] - ox]
    small = cv2.resize(can, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    return (X0, Y0, X1, Y1), small[..., :3], np.clip(small[..., 3] / 255, 0, 1)


def sombra_alfa(a, dist, sig):
    s = cv2.GaussianBlur(a, (0, 0), sig)
    M = np.float32([[1, 0, -dist], [0, 1, dist]])                     # a luz do alto à direita
    return cv2.warpAffine(s, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)


def compor(out, P, c, sombra=None, nao=None):
    """P no retângulo c do quadro, com a sombra curta (força, distância, sigma) e sem tocar em `nao` (bool H x W)."""
    H, W = out.shape[:2]
    (X0, Y0, X1, Y1), cor, a = renderizar(P, c, H, W)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    if sombra:
        f, d, s = sombra
        reg *= (1 - f * sombra_alfa(a, d, s))[..., None]
    reg = reg * (1 - a[..., None]) + cor
    if nao is not None:
        n = nao[Y0:Y1, X0:X1]
        reg[n] = out[Y0:Y1, X0:X1][n]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# A academia: o vinílico por baixo das peças antigas e as peças novas
def reguas_academia():
    """As réguas do vinílico da academia (BGR float32) e o piso (bool), na janela de `REGUAS_Q["origem"]`."""
    if REGUAS.exists():
        R = cv2.imread(str(REGUAS), cv2.IMREAD_UNCHANGED)
        return R[..., :3].astype(np.float32), R[..., 3] > 127
    import vinilico_foto as V
    import um_pav_casaa_1111 as U
    dado = subprocess.run(["git", "show", f"{REGUAS_Q['commit']}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"],
                          cwd=RAIZ_GIT, capture_output=True, check=True).stdout
    velha = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    Q = quieto(V.quadro, "A", "Subsolo")
    cam = V.camadas_spec("A_Subsolo", Q, velha.shape[:2])
    pegas = []
    orig = U._reguas_amostra

    def espiao(h, w, px_m, q, rng):
        T = orig(h, w, px_m, q, rng)
        pegas.append(T)
        return T
    U._reguas_amostra = espiao
    try:
        _, piso = quieto(V.trocar, Q, velha, "madeira", camadas=cam)
    finally:
        U._reguas_amostra = orig
    T = pegas[0]
    ox, oy = REGUAS_Q["origem"]
    p = piso[oy:oy + T.shape[0], ox:ox + T.shape[1]]
    R = np.dstack([np.clip(np.round(T), 0, 255).astype(np.uint8), (p * 255).astype(np.uint8)])
    cv2.imwrite(str(REGUAS), R)
    print(f"    réguas da academia refeitas sobre a final de {REGUAS_Q['commit']}: {REGUAS.name}")
    return np.round(T).astype(np.float32), p


def rotulos_mascara(Q, forma):
    """Os rótulos da especificação (o alfa deles, com 2 px de folga): não são piso."""
    import vinilico_foto as V
    cam = quieto(V.camadas_spec, "A_Subsolo", Q, forma)
    m = np.zeros(forma, bool)
    for a, _ in cam:
        m |= a > 0.01
    return ndimage.binary_dilation(m, iterations=2)


def nconv(v, m, sig):
    num = cv2.GaussianBlur(v * m[..., None], (0, 0), sig)
    den = cv2.GaussianBlur(m.astype(np.float32), (0, 0), sig)[..., None]
    return num, den


def academia(Q, out):
    q = ACADEMIA
    T, piso = reguas_academia()
    ox, oy = REGUAS_Q["origem"]
    h, w = T.shape[:2]
    reg = out[oy:oy + h, ox:ox + w].astype(np.float32)
    Lr = reg / np.maximum(T, 1)
    caixas = [caixa_px(Q, p["pt"]) for p in q["pecas"]]
    perto = np.zeros((h, w), bool)
    caixa_m = np.zeros((h, w), bool)
    for x0, y0, x1, y1 in caixas:
        b = q["busca_px"]
        perto[max(int(y0) - b - oy, 0):int(y1) + b - oy, max(int(x0) - b - ox, 0):int(x1) + b - ox] = True
        caixa_m[max(int(y0) - 1 - oy, 0):int(np.ceil(y1)) + 1 - oy, max(int(x0) - 1 - ox, 0):int(np.ceil(x1)) + 1 - ox] = True
    # a luz larga do piso longe das peças, e o que foge do piso esperado perto delas: as peças antigas e a sombra
    limpo = piso & ~perto
    num, den = nconv(Lr, limpo, 12.0)
    E = T * num / np.maximum(den, 1e-4)
    rot = rotulos_mascara(Q, out.shape[:2])[oy:oy + h, ox:ox + w]
    velho = perto & ~rot & (np.abs(reg - E).max(axis=2) > q["desvio"])
    n, lab = cv2.connectedComponents(velho.astype(np.uint8), connectivity=8)
    perto_caixa = ndimage.binary_dilation(caixa_m, iterations=q["liga_px"])
    toca = np.unique(lab[perto_caixa & velho])
    velho = np.isin(lab, toca[toca > 0])
    buraco = ndimage.binary_dilation(velho | caixa_m, iterations=q["folga_px"]) & perto & ~rot
    # o vinílico de volta no buraco: as réguas vezes a luz do piso em volta (média normalizada, cada vez mais larga)
    valido = piso & ~buraco
    L = np.zeros_like(Lr)
    falta = buraco.copy()
    for sig in (q["luz_sigma"], 8.0, 16.0, 32.0):
        num, den = nconv(Lr, valido, sig)
        ok = falta & (den[..., 0] > 0.05)
        L[ok] = (num / np.maximum(den, 1e-6))[ok]
        falta &= ~ok
        if not falta.any():
            break
    reg[buraco] = (T * L)[buraco]
    out[oy:oy + h, ox:ox + w] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    academia: {int(buraco.sum())} px de vinílico refeito pelas réguas da final (peças antigas e sombras)")
    for p, c in zip(q["pecas"], caixas):
        P = ler_png(p["png"], cortar=False)
        if "barra" in p:
            # a barra do PDF: o supino de pé tem a barra em cima; repete as colunas da barra e do travessão do rack
            a0, a1 = p["barra"]
            ys, xs = np.nonzero(P[..., 3] > 0)
            larg, alt = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
            alvo = (c[3] - c[1]) / (c[2] - c[0]) * alt               # depois do giro: a barra na altura da caixa
            d = max(0, int(round((alvo - larg) / 2)))
            col = lambda x: np.repeat(P[:, x:x + 1], d, axis=1)
            P = np.concatenate([P[:, :a0], col(a0), P[:, a0:a1], col(a1), P[:, a1:]], axis=1)
        ys, xs = np.nonzero(P[..., 3] > 0)
        P = girar(np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1]), q["giro"])
        cc = dentro(P, c) if p.get("dentro") else c
        out = compor(out, P, cc, sombra=q["sombra"])
        print(f"    academia: {p['nome']} ({Path(p['png']).stem}) em {cc[2] - cc[0]:.1f} x {cc[3] - cc[1]:.1f} px")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Os banhos
def piso_ao_lado(out, m, d):
    """Os px de m recebem o piso deslocado de d = (dx, dy) px (o veio do travertino e do Bege Bahia é deitado)."""
    ys, xs = np.nonzero(m)
    H, W = m.shape
    sy, sx = np.clip(ys + d[1], 0, H - 1), np.clip(xs + d[0], 0, W - 1)
    out[ys, xs] = out[sy, sx]
    return out


def sob_peca(out, c, par, anel=(3, 9)):
    """O retângulo c (o vaso antigo, de outra cor) no tom mediano do piso em volta (o anel de `anel` px, fora das
    paredes), para a borda suave da peça nova não mostrar a cor da antiga."""
    x0, y0, x1, y1 = (int(np.floor(c[0])) - 1, int(np.floor(c[1])) - 1, int(np.ceil(c[2])) + 1, int(np.ceil(c[3])) + 1)
    a, b = anel
    H, W = out.shape[:2]
    m = np.zeros((H, W), bool)
    m[max(y0 - b, 0):y1 + b, max(x0 - b, 0):x1 + b] = True
    m[max(y0 - a, 0):y1 + a, max(x0 - a, 0):x1 + a] = False
    m &= ~ndimage.binary_dilation(par, iterations=1)
    lum = out.astype(np.float32).mean(axis=2)
    ok = m & (lum > np.percentile(lum[m], 30))                    # o piso (sem sombras, bancadas e louças escuras)
    tom = np.median(out[ok].reshape(-1, 3), axis=0)
    caixa = np.zeros((H, W), bool)
    caixa[y0:y1, x0:x1] = True
    caixa &= ~par
    out[caixa] = np.round(tom).astype(np.uint8)
    return out


def chuveiro_peca(q, placa_pt, dist_pt):
    """O chuveiro de pé (parede em cima): a canopla e o braço da peça de parede e a placa quadrada, o braço com o
    comprimento que leva a placa a `dist_pt` da parede (a placa com `placa_pt`)."""
    par = ler_png(q["parede"], cortar=False)
    pl = ler_png(q["placa"], cortar=False)
    x0, y0, x1, y1 = q["placa_q"]
    placa = pl[y0:y1, x0:x1]
    wp = placa.shape[1]
    x0, y0, x1, y1 = q["canopla_q"]
    can = par[y0:y1, x0:x1]
    x0, y0, x1, y1 = q["braco_q"]
    linha = par[y0:y1, x0:x1]
    k = wp / placa_pt                                                # px do PNG por pt
    nb = max(1, int(round(dist_pt * k - can.shape[0])))
    braco = np.repeat(linha, nb, axis=0)
    def centro(f):
        c = np.zeros((f.shape[0], wp, 4), np.float32)
        a = (wp - f.shape[1]) // 2
        c[:, a:a + f.shape[1]] = f
        return c
    return np.ascontiguousarray(np.concatenate([centro(can), centro(braco), placa], axis=0))


def cuba_esculpida(Q, out, c, semente):
    """A cuba esculpida da biblioteca no retângulo da cuba do PDF, no granito marrom: o sombreado da peça (as bordas
    chanfradas e a sombra por dentro) sobre o granito de antes, e a torneira cromada dela."""
    import fontes_procedurais as FP
    q = BANHOS_BIB["cuba"]
    P = girar(ler_png(q["png"], cortar=False), "180")
    x0, y0, x1, y1 = q["recorte"]
    P = P[y0:y1, x0:x1]
    cx = caixa_px(Q, c["cuba"])
    sy = (cx[3] - cx[1]) / P.shape[0]
    alvo = (cx[2] - cx[0]) / sy
    f0, f1, f2, f3 = q["fatias"]
    fixo = f0 + (f2 - f1) + (P.shape[1] - f3)
    sobra = alvo - fixo
    l1, l2 = f1 - f0, f3 - f2
    P2 = esticar(P, 1, [(0, f0, None), (f0, f1, sobra * l1 / (l1 + l2)), (f1, f2, None),
                        (f2, f3, sobra * l2 / (l1 + l2)), (f3, P.shape[1], None)])
    # a torneira: o cromo (pouca cor) na janela dela
    tx0, ty0, tx1, ty1 = q["torneira"]
    Q8 = P2[..., :3]
    croma = Q8.max(axis=2) - Q8.min(axis=2)
    tor = np.zeros(P2.shape[:2], np.float32)
    desl = int(round(sobra * l1 / (l1 + l2))) - l1                 # a fatia esticada da esquerda empurra o meio
    ax0, ax1 = tx0 + desl, tx1 + desl
    jan = (slice(ty0, ty1), slice(ax0, ax1))
    tor[jan] = (croma[jan] < q["croma_torneira"]).astype(np.float32)
    tor = cv2.GaussianBlur(cv2.morphologyEx(tor, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)), (0, 0), 0.8)
    H, W = out.shape[:2]
    (X0, Y0, X1, Y1), cor, a = renderizar(P2, cx, H, W)
    T4 = np.dstack([np.repeat(tor[..., None] * 255, 4, axis=2)[..., :3], tor * 255]).astype(np.float32)
    _, _, a_t = renderizar(T4, cx, H, W)
    cor_l = cor / np.maximum(a[..., None], 1e-4)
    lum = cor_l.mean(axis=2)
    # a borda (fora da bacia do PDF e da torneira) é a referência do sombreado
    ys, xs = np.mgrid[Y0:Y1, X0:X1].astype(np.float32) + 0.5
    b = caixa_px(Q, c["bacia"])
    bacia = ((xs > b[0]) & (xs < b[2]) & (ys > b[1]) & (ys < b[3])).astype(np.float32)
    bacia = cv2.GaussianBlur(bacia, (0, 0), 0.5)
    rim = (a > 0.95) & (bacia < 0.05) & (a_t < 0.05)
    ref = float(np.median(lum[rim]))
    S = np.clip(lum / ref, 0.35, 1.25)
    G = FP.granito_referencia(Y1 - Y0, X1 - X0, Q.px_m, semente=semente).astype(np.float32)
    k = q["rim"] * (1 - bacia) + q["bacia"] * bacia
    novo = G * (k * S)[..., None]
    novo = novo * (1 - a_t[..., None]) + cor_l * a_t[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    reg = reg * (1 - a[..., None]) + novo * a[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


def granito_lib(P, faixa, lado_px, alto_px, k):
    """O granito da peça da biblioteca (girada) tecido em `alto_px` x `lado_px` (px do quadro), na escala k (px do
    quadro por px do PNG): as faixas de cima e de baixo da cuba, só de granito, empilhadas (espelhadas uma sim, uma
    não) e emendadas com 10 px de transição."""
    branco = (P[..., :3].min(axis=2) > 200) & (P[..., 3] > 200)
    ys, xs = np.nonzero(branco)
    y0, y1 = ys.min(), ys.max()
    a, b = faixa, P.shape[1] - faixa
    cima = P[faixa:y0 - 4, a:b, :3]
    baixo = P[y1 + 4:P.shape[0] - faixa, a:b, :3]
    W = int(np.ceil(lado_px / k)) + 2
    Hs = int(np.ceil(alto_px / k)) + 2
    tiras, i = [], 0
    while sum(t.shape[0] for t in tiras) < Hs + 40:
        t = (cima, baixo)[i % 2]
        tiras.append(t if (i // 2) % 2 == 0 else t[::-1])
        i += 1
    tela = tiras[0]
    for t in tiras[1:]:
        e = 10
        mix = np.linspace(0, 1, e, dtype=np.float32)[:, None, None]
        tela = np.concatenate([tela[:-e], tela[-e:] * (1 - mix) + t[:e] * mix, t[e:]], axis=0)
    tela = cv2.resize(tela[:Hs], (W, Hs), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(tela, (max(1, int(round(W * k))), max(1, int(round(Hs * k)))), interpolation=cv2.INTER_AREA)


def servico(Q, out, FA):
    q = BANHOS_BIB["servico"]
    sv = FA.BANHOS["servico"]
    P = girar(ler_png(q["png"]), q["giro"])
    branco = (P[..., :3].min(axis=2) > 200) & (P[..., 3] > 200)
    n, lab, st, _ = cv2.connectedComponentsWithStats(branco.astype(np.uint8), 8)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    cuba = ndimage.binary_fill_holes(lab == i)
    cuba = ndimage.binary_dilation(cuba, iterations=3)
    ys, xs = np.nonzero(cuba)
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    # a torneira: o cromo atrás da cuba (do lado da parede, à esquerda depois do giro)
    croma = P[..., :3].max(axis=2) - P[..., :3].min(axis=2)
    tor = (croma < 22) & (P[..., :3].mean(axis=2) > 70) & ~cuba & (P[..., 3] > 200)
    tor[:, bx0 + (bx1 - bx0) // 3:] = False
    tor[:by0 + (by1 - by0) // 4] = False
    tor[by1 - (by1 - by0) // 4:] = False
    n, lab = cv2.connectedComponents(tor.astype(np.uint8), connectivity=8)
    if n > 1:
        tam = np.bincount(lab.ravel())[1:]
        tor = lab == 1 + int(np.argmax(tam))
    tor = ndimage.binary_dilation(tor, iterations=1)
    ys, xs = np.nonzero(tor)
    tx0 = xs.min()
    alfa = np.maximum(cv2.GaussianBlur(cuba.astype(np.float32), (0, 0), 1.0),
                      cv2.GaussianBlur(tor.astype(np.float32), (0, 0), 0.7))
    Pc = P.copy()
    Pc[..., 3] = alfa * 255 * (P[..., 3] / 255)
    c = caixa_px(Q, sv["cuba"])
    kx, ky = (c[2] - c[0]) / (bx1 - bx0), (c[3] - c[1]) / (by1 - by0)
    x0r = min(tx0, bx0)
    crop = Pc[by0:by1, x0r:bx1]
    alvo = (c[0] - (bx0 - x0r) * kx, c[1], c[2], c[3])
    # a bancada: o polígono do PDF com o granito da peça, a borda de antes, sem sombra nova (a de antes fica)
    d = next(d for d in Q.desenhos if d.get("layer") == "ARQ_BANCADAS" and d["type"] in ("f", "fs")
             and FA._dentro((sv["bancada"][0] - 0.2, sv["bancada"][1] - 0.2, sv["bancada"][2] + 0.2,
                             sv["bancada"][3] + 0.2), tuple(d["rect"]))
             and abs(d["rect"].width - (sv["bancada"][2] - sv["bancada"][0])) < 0.5)
    poli = [(p.x, p.y) for it in d["items"] for p in it[1:] if hasattr(p, "x")]
    k = (kx + ky) / 2
    out = FA.bancada_pedra(Q, out, sv["bancada"], lambda tl: granito_lib(P, q["faixa_lib"], tl.w, tl.h, k)[:tl.h, :tl.w],
                           q["borda"], q["larg"], 0.0, poli=poli)
    out = compor(out, crop, alvo, nao=quieto(FA.paredes_pdf, Q) > 0.3)
    print("    BH. SERV.: bancada no granito da peça da biblioteca (polígono do PDF), cuba branca e torneira da peça")
    return out


def banhos(Q, out, FA):
    q = BANHOS_BIB
    par = quieto(FA.paredes_pdf, Q) > 0.3
    # os braços antigos dos chuveiros viram piso (o braço novo é mais fino)
    qc = q["chuveiro"]
    for ch in FA.BANHOS["chuveiros"]:
        m = np.zeros(out.shape[:2], np.uint8)
        for k in ("braco", "canopla"):
            x0, y0, x1, y1 = caixa_px(Q, ch[k])
            m[int(np.floor(y0)) - qc["limpa_px"]:int(np.ceil(y1)) + qc["limpa_px"],
              int(np.floor(x0)) - qc["limpa_px"]:int(np.ceil(x1)) + qc["limpa_px"]] = 1
        x0, y0, x1, y1 = caixa_px(Q, ch["ducha"])
        m[int(np.floor(y0)):int(np.ceil(y1)), int(np.floor(x0)):int(np.ceil(x1))] = 0
        m = m.astype(bool) & ~ndimage.binary_dilation(par, iterations=1)
        vertical = (ch["braco"][3] - ch["braco"][1]) > (ch["braco"][2] - ch["braco"][0])
        out = piso_ao_lado(out, m, (6, 0) if vertical else (0, -6))
    # as cubas esculpidas (BH. FEM. e BH. MASC.)
    for i, c in enumerate(FA.BANHOS["fem_masc"]):
        out = cuba_esculpida(Q, out, c, 2630 + i)
        print(f"    banho {c['nome']}: cuba esculpida da biblioteca no granito marrom, torneira cromada dela")
    # o banho de serviço: bancada e cuba
    out = servico(Q, out, FA)
    # as bacias, com a descarga de novo
    for v in q["vasos"]:
        P = girar(ler_png(v["png"]), v["giro"])
        out = sob_peca(out, caixa_px(Q, v["pt"]), par)
        out = compor(out, P, caixa_px(Q, v["pt"]), nao=par)
        out = FA.placa_cromada(Q, out, v["descarga"])
        print(f"    {v['nome']}: {Path(v['png']).stem} branca no retângulo do vaso do PDF, com a descarga")
    # os chuveiros
    for ch in FA.BANHOS["chuveiros"]:
        giro = qc["giros"][ch["nome"]]
        d = ch["ducha"]
        if giro == "180":                                          # a parede embaixo
            parede = ch["canopla"][3]
            P = chuveiro_peca(qc, d[2] - d[0], parede - d[3])
            alvo = (d[0], d[1], d[2], parede)
        else:                                                      # a parede à esquerda
            parede = ch["canopla"][0]
            P = chuveiro_peca(qc, d[3] - d[1], d[0] - parede)
            alvo = (parede, d[1], d[2], d[3])
        P = girar(P, giro)
        out = compor(out, P, caixa_px(Q, alvo), sombra=qc["sombra"], nao=par)
        print(f"    chuveiro ({ch['nome']}): a placa quadrada, o braço até a parede e a canopla da biblioteca")
    return out


def sauna(Q, out, antes, FA):
    q = SAUNA_BIB
    c = caixa_px(Q, FA.SAUNA["pt"])
    P = ler_png(q["png"])
    sy = (c[3] - c[1]) / P.shape[0]
    alvo = (c[2] - c[0]) / sy
    p = q["pontas"]
    P = esticar(P, 1, [(0, p, None), (p, P.shape[1] - p, alvo - 2 * p), (P.shape[1] - p, P.shape[1], None)])
    # o tom do banco de antes (0,90 do piso), canal a canal, no miolo
    e = q["erosao_px"]
    x0, y0, x1, y1 = (int(np.ceil(c[0])) + e, int(np.ceil(c[1])) + e, int(np.floor(c[2])) - e, int(np.floor(c[3])) - e)
    tom = np.median(antes[y0:y1, x0:x1].reshape(-1, 3), axis=0)
    m = P[..., 3] > 250
    ganho = tom / np.median(P[..., :3][m], axis=0)
    P[..., :3] = np.clip(P[..., :3] * ganho, 0, 255)
    out = compor(out, P, c)
    print(f"    sauna: banco reto de travertino da biblioteca, no tom do banco de antes (BGR {np.round(tom).astype(int)})")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    import final3840_casaa as FA
    Q = quieto(FA.QuadroA, "Subsolo")
    out = np.ascontiguousarray(antes.copy())
    out = academia(Q, out)
    out = banhos(Q, out, FA)
    out = sauna(Q, out, antes, FA)
    return out


def antes_depois(antes, depois, pasta, max_lado=2200):
    feitos = []
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        lado = (x1 - x0) <= (y1 - y0) * 1.3
        junto = np.hstack([a, np.full((a.shape[0], 8, 3), 255, np.uint8), b]) if lado else \
            np.vstack([a, np.full((8, a.shape[1], 3), 255, np.uint8), b])
        k = min(4.0, max_lado / max(junto.shape[:2]))
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        arq = pasta / f"POE642_CasaA_PH_Subsolo_1211_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        feitos.append(arq)
        print(f"    {arq.name}")
    return feitos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes", type=Path)
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    if a.antes:
        antes = cv2.imread(str(a.antes))
    else:
        dado = subprocess.run(["git", "show", f"{ANTES_COMMIT}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"],
                              cwd=RAIZ_GIT, capture_output=True, check=True).stdout
        antes = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    out = aplicar(antes)
    saida = a.saida or FINAL
    cv2.imwrite(str(saida), out)
    print(f"    {saida}")
    if not a.saida:
        antes_depois(antes, out, FINAL.parent)


if __name__ == "__main__":
    main()

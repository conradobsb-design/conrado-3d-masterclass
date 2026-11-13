"""Os post-its do cliente no Subsolo da Casa C (13/11, quadro "POE 642 - Revisão de Imagens").

Sobre a final com a biblioteca (`biblioteca_subsolo_casac_1311`, commit `ANTES_COMMIT`), como os mesmos pedidos no
Subsolo da Casa B (`pedidos_subsolo_casab_1211`, de onde vêm as portas e o desenho das setas):
- **"Já removeu manchas do bege Bahia como fizemos nas outras plantas?"** (`bege`, a regra de 10/11): as manchas do
  Bege Bahia a 45%, como nos três pavimentos da Casa A.
- **"Colocar um piso com menos manchas cinzas."** (`travertino`, a varanda do Subsolo): as manchas largas do travertino
  saem (a luz e a cor de baixa frequência levadas à mediana do piso, `forca`); o veio fino fica.
- **"Representar um filete entre os dois pisos"** (`filete`, entre o Bege Bahia do pátio e o travertino da varanda): uma
  tira de pedra de 4 cm no encontro dos dois, com os fios das bordas.
- **"Tem um pilar aqui"** (`pilar`, no alto do encontro; o PDF não o desenha): redondo, de 0,30 m, no cinza das paredes,
  como o pilar do Subsolo da Casa B.
- **"Trocar essa representação para uma escala de plantinhas menores"** (`floreira`, a floreira junto à sauna): o
  canteiro refeito com a terra, a forração miúda e plantinhas de ~0,18 m (antes, arbustos de ~0,40 m numa faixa de
  0,27 m).
- **"Colocar a seta em todas as escadas e a descrição."** (`escadas`): o triângulo cheio no 1º degrau, com a ponta para
  onde a escada sobe, o S logo abaixo dele e a descrição em duas linhas, como no Subsolo das Casas A e B: nos degraus
  largos, "SOBE PARA O / JARDIM" no pátio, acima da escada; na escada estreita (degraus 11 a 21), "SOBE PARA O / DECK"
  logo abaixo dela, sobre a hachura limpa em volta do texto.
- **"Melhorar representação das portas de giro. Encostar nas paredes."** (`portas`, `pedidos_subsolo_casab_1211.
  portas_sb`): as 3 portas de giro (sauna, BH academia e depósito) com a folha de madeira clara, o veio no comprido, o
  contorno e a sombra curta, quina com quina na ponta da parede; os marcos saem (a parede vai até a folha) e o vão fica
  com a soleira de travertino; a do depósito, numa parede deitada, feita na imagem transposta.
- **"Fazer as mesmas mudanças que foram apontadas no subsolo da casa A e que cabem para essa casa"**: as que cabem já
  estão (os chuveiros desenhados, as louças sem caixa, os aparelhos da academia no tamanho da Casa A, BH nos rótulos) ou
  entram aqui (a seta com o S e a descrição, as portas quina com quina e as pontas de parede retas nos portais).

Depois, na revisão do 12K (13/11, "ESTOU REVISANDO O SUBSOLO DA CASA C"):
- **"REMOVA O HACHURADO DE FUNDO ... NÃO TERÁ MAIS HACHURADO, FUNDO BRANCO"** (`fundo_branco`, como no Subsolo da Casa
  A em 05/11): fora da pegada (`final3840_casac.pegada_subsolo`) tudo branco, sem a hachura e sem o contorno do lote; na
  borda da pegada a hachura sai pela conta dela (`ajustes_casaa.subsolo_hachurado`).
- **"REMOVA A LINHA PRETA E PRESERVE A DIFERENÇA DE TONS. SÓ REMOVA A LINHA EM DIAGONAL"** (`escada_sem_corte`, a
  escada estreita): a linha de corte do PDF (com o zigue-zague) sai; o trecho depois do corte continua nevoado, com a
  divisa reta (a diagonal entre as pontas da linha), refeito pela mesma conta de `final3840_casac.escada_estreita_s`.
- **"CORRIJA A LOCALIZAÇÃO DO PILAR. ELE FICA NO TRAVERTINO."** (`PILAR`): o pilar todo dentro do travertino, afastado
  do filete e da borda de cima, onde o post-it do cliente o marca (antes, no canto, metade fora do piso).
- **"NO PISO DO TRAVERTINO REMOVER MANCHAS CINZAS, CONFORME ORIENTAÇÃO"** (`travertino`, o post-it "Colocar um piso com
  menos manchas cinzas"): as manchas largas cinzas saem (a baixa frequência à mediana do piso); o veio fino fica.

  python3 pedidos_subsolo_casac_1311.py [--antes <png>] [--saida <png>]
"""

import argparse
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import final3840_casac as C                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402

CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Subsolo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "6ea1bc3"

# (regra de 10/11, "Bege Bahia menos manchado, em todas as plantas de todas as casas"; usuário: "Já removeu manchas do
# bege Bahia como fizemos nas outras plantas?") as manchas da pedra a 45% (`forca`) em todo o Bege Bahia (a chapada
# 232: o pátio, os degraus largos, o caminho e o depósito), pela conta de `terreo_casaa_1011.bege_ta`: o tom do lugar
# (a mediana larga, com as peças tapadas) fica, a luz, as sombras e as arestas dos degraus também; as letras (o escuro)
# e as peças (pouco croma, escuras ou verdes) ficam como estão
BEGE = {"chapada": (232, 232, 232), "forca": 0.35, "mediana_px": 61, "croma_obj": 22, "lum_obj": 120, "area_obj": 30,
        "aresta": 10.0, "aresta_px": 2, "texto": 0.72, "linha": 0.92}
# a varanda do Subsolo (px): o retângulo do travertino, a força e o sigma da baixa frequência que sai
# (revisão do 12K, "NO PISO DO TRAVERTINO REMOVER MANCHAS CINZAS") a força 0,85 e só no piso (`den_min`: a fração de
# piso na média em volta a partir da qual a correção é inteira)
TRAVERTINO = {"px": (637, 321, 1064, 737), "sigma": (28.0, 2.5), "forca": 0.85, "texto": 0.80, "den_min": 0.5}
# o encontro do Bege Bahia com o travertino (px): x, de y0 a y1; a largura (m), a cor da pedra e a dos fios (BGR)
# (13/11, "Esse filete, eu não sei se ele é num tom preto ... deve vir do mármore bege Bahia") o filete em Bege Bahia:
# uma tira de `larg_m` da pedra do pátio logo ao lado, um pouco mais clara (um mini degrau polido), com o fio fino da
# aresta do lado do travertino e a sombrinha curta nele
FILETE = {"x": 636.4, "y0": 320.0, "y1": 737.0, "larg_m": 0.05, "clarear": 1.035, "fonte_dx": -14,
          "fio": (150, 165, 178), "fio_alfa": 0.55, "sombra": 0.10, "ss": 8}
# (13/11, revisão do 12K: "CORRIJA A LOCALIZAÇÃO DO PILAR. ELE FICA NO TRAVERTINO.") o pilar inteiro no travertino, onde
# o post-it o marca: ~0,15 m à direita do filete e ~0,12 m abaixo da borda de cima (antes, (636.4, 329.5), no canto)
PILAR = {"centro_px": (656.0, 336.0), "diam_m": 0.30, "cor": (80, 80, 80), "ss": 8}
# (revisão do 12K) o fundo: fora da pegada, branco puro (a hachura e o contorno do lote saem)
FUNDO = {"fora": 0.001}
# (revisão do 12K) a escada estreita sem a linha de corte: a divisa do trecho nevoado reta, entre as pontas da linha
# (pt); `folga_px`: o anel em volta da linha e da diferença das divisas que é refeito
ESCADA_CORTE = {"divisa": [(657.1, 1155.3), (691.4, 1240.9)], "folga_px": 1, "fundo_px": 6, "ss": 8}
# a floreira junto à sauna (`final3840_casac.FLOREIRA_S`): plantinhas de `d_m`, a cada `passo` (fração da altura)
FLOREIRA = {"d_m": (0.16, 0.20), "passo": 0.056, "forracao_m": (0.09, 0.14), "forracao_passo_m": 0.07, "semente": 1311}
# as escadas: o triângulo (px, a ponta para onde sobe), a letra (centro x, topo y) e a descrição (linhas, centro x, base
# da 1ª linha, a entrelinha e o fundo branco em volta para a hachura)
ESCADAS = [
    {"nome": "degraus largos", "triangulo": [(509.0, 740.5), (519.0, 740.5), (514.0, 749.5)],
     "s_px": (505, 744, 525, 765), "s_fonte": (25, 0), "letra_topo": 751.5,
     "texto": ("SOBE PARA O", "JARDIM"), "centro_x": 514.0, "base_y": 711.0, "fundo": None},
    {"nome": "escada estreita", "triangulo": [(697.0, 1001.0), (697.0, 1012.0), (707.5, 1006.5)],
     "s_px": None, "texto": ("SOBE PARA O", "DECK"), "centro_x": 762.0, "base_y": 1090.0, "fundo": (255, 255, 255)},
]
COR_SETA = (30, 30, 30)
ENTRELINHA = 20
# as portas de giro (`pedidos_subsolo_casab_1211.PORTAS_SB`, px): a parede (as faces), as pontas do PDF, a folha aberta,
# a dobradiça (topo ou base) e o lado para onde abre; a do depósito na imagem transposta (x e y trocados)
PORTAS = {
    "portas": [
        {"nome": "sauna", "parede": (813.5, 822.4), "topo": 750.5, "base": 798.3,
         "folha": (822.4, 792.9, 864.2, 795.3), "dobra": "base", "lado": +1, "soleira": True},
        {"nome": "BH academia", "parede": (888.1, 897.1), "topo": 750.5, "base": 804.2,
         "folha": (897.1, 753.5, 944.8, 755.9), "dobra": "topo", "lado": +1, "soleira": True},
    ],
    "soleira_px": (815, 762, 821, 788),
    "transpostas": [
        {"nome": "depósito", "parede": (737.1, 746.0), "topo": 998.6, "base": 1052.3,
         "folha": (746.0, 1001.5, 793.8, 1003.9), "dobra": "topo", "lado": +1, "soleira": True},
    ],
}
# (13/11, "tem que ter o caixote dessa jardineira ... a borda, tudo direitinho") o caixote da floreira junto à sauna,
# pelo PDF (ARQ_PAISAGISMO): a caixa de fora e a de dentro (px); a borda em concreto claro, com os fios das arestas, a
# sombra da borda na terra (a luz do alto à direita) e a sombra curta da caixa no piso
CAIXOTE = {"fora": (664.2, 737.1, 694.0, 978.9), "dentro": (670.2, 743.0, 688.1, 972.9), "cor": (204, 212, 218),
           "ruido": 0.025, "fio": (150, 158, 166), "fio_alfa": 0.7, "sombra_terra": 0.35, "sombra_piso": 0.16,
           "ss": 8, "semente": 1311}
# (13/11, "As portas não podem estar flutuando ... remove o batente e cola a quina com quina da parede com a porta") a
# ponta da parede vai até a quina da folha: (folha px, dobra, lado, transposta)
QUINAS = [((822.4, 792.9, 864.2, 795.3), "base", +1, False),
          ((897.1, 753.5, 944.8, 755.9), "topo", +1, False),
          ((746.0, 1001.5, 793.8, 1003.9), "topo", +1, True)]
# (revisão do 12K) o antes e depois contra a final de antes desta revisão (a do disco)
REVISAO = {"planta": (330, 220, 1920, 1700), "pilar": (590, 290, 720, 400), "escada": (680, 960, 900, 1120),
           "travertino": (637, 321, 1064, 737)}
ANTES_DEPOIS = {"bege_bahia": (350, 300, 1260, 1700), "varanda_filete_pilar": (600, 300, 1080, 760),
                "caixote": (640, 725, 720, 995), "floreira_escadas": (355, 690, 900, 1120),
                "portas": (780, 725, 1080, 830)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            C.contexto_c()
            _Q["Q"] = F.Quadro("Subsolo")
    return _Q["Q"]


_Q = {}


def _alfa_poligono(pts, X0, Y0, w, h, ss=8):
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((np.float32(pts) - [X0, Y0]) * ss))], 255, cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def _pintar(out, a, X0, Y0, cor):
    h, w = a.shape
    reg = out[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg * (1 - a[..., None]) + np.float32(cor) * a[..., None]), 0,
                                        255).astype(np.uint8)
    return out


# ----------------------------------------------------------------------------------------------------------------------
def fundo_branco(Q, img, q=FUNDO):
    """Sem a hachura: a final do Subsolo é final * p + hachura * (1 - p) (`ajustes_casaa.subsolo_hachurado`, p a pegada);
    a hachura sai pela conta dela (as mesmas diagonais) e no lugar entra o branco; fora da pegada, branco puro."""
    import ajustes_casaa as AJ
    p = C.pegada_subsolo(Q)
    # só o pedaço da planta: a pegada também pega uma faixa fina no pé do lote (y ~1815 a 1838, a linha do lote e o
    # tracejado da calçada da base), que fica branca
    n, lab, st, _ = cv2.connectedComponentsWithStats((p > q["fora"]).astype(np.uint8), connectivity=8)
    p = p * (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    h = AJ.SUBSOLO_R2["hachura"]
    H, W = img.shape[:2]
    s = h["passo_m"] * Q.px_m
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fr = np.mod((xx + yy) / np.sqrt(2), s)
    a = np.clip(h["largura_px"] / 2 + 0.5 - np.minimum(fr, s - fr), 0, 1)[..., None]
    fundo = 255 * (1 - a) + np.float32(h["cor"]) * a
    out = img.astype(np.float32) + (255 - fundo) * (1 - p[..., None])
    out[p <= q["fora"]] = 255
    print(f"    fundo branco: {int((p <= q['fora']).sum())} px fora da pegada (sem a hachura e o contorno do lote)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _escada_estreita(Q, img, corte, ss=8):
    """A conta de `final3840_casac.escada_estreita_s` até antes da linha de corte, com a divisa do trecho nevoado em
    `corte` (pt): o recorte (px), a cobertura da escada e o desenho."""
    sys.path.insert(0, str(C.RAIZ / "_texturas"))
    from texturas import textura
    q, s = C.ESTREITA_S, F.ESCADA_SOMBRA
    ex0, ey0, ex1, ey1 = q["pdf"]
    x0, y0, x1, y1 = F.ret_q(Q, (ex0 - 8, ey0, ex1, ey1))
    x0, y0, x1, y1 = x0, y0 - 1, x1 + 1, y1 + 1
    X, Y = C.grade_pt(Q, x0, y0, x1, y1)
    a = F.ret_aa_q(Q, q["pdf"])[y0:y1, x0:x1]
    h, w = a.shape
    bordas = [ex0] + list(q["bocels"]) + [ex1]
    k = np.searchsorted(bordas, X).astype(np.int32)
    f = C.sombras_degraus(k, len(bordas), s)
    bege = F.fechar(Q.cor([(232, 232, 232)], tol=6), 5)
    tom = np.median(img[bege].reshape(-1, 3), axis=0).astype(np.float32)
    T = textura(F.DEGRAUS_F["pedra"], Q.px_m, h, w, semente=q["semente"]).astype(np.float32)
    novo = T / T.reshape(-1, 3).mean(axis=0) * tom * f[..., None]
    pts = [Q.p2q(x, y) for x, y in corte + [(ex1 + 3, ey1 + 3), (ex1 + 3, ey0 - 3), (corte[0][0], ey0 - 3)]]
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((np.float32(pts) - (x0, y0)) * ss))], 255)
    depois = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    e, nv = q["esmaecer"], q["nevoa"]
    antes_c = novo * (1 - e) + 255 * e
    nevoa = cv2.GaussianBlur(novo, (0, 0), nv["sigma_px"]) * (1 - nv["branco"]) + 255 * nv["branco"]
    desenho = antes_c * (1 - depois[..., None]) + nevoa * depois[..., None]
    return (x0, y0, x1, y1), a, depois, desenho


def escada_sem_corte(Q, img, q=ESCADA_CORTE):
    """A escada estreita sem a linha de corte: onde estava a linha (e onde a divisa reta difere da do zigue-zague), o
    desenho refeito pela conta da escada, com a divisa reta; nas pontas (fora da escada), o fundo de junto."""
    qe = C.ESTREITA_S
    (x0, y0, x1, y1), a, dep_v, des_v = _escada_estreita(Q, img, qe["corte"], q["ss"])
    _, _, dep_n, des_n = _escada_estreita(Q, img, q["divisa"], q["ss"])
    h, w = a.shape
    ss = q["ss"]
    cp = np.float32([Q.p2q(x, y) for x, y in qe["corte"]])
    ml = np.zeros((h * ss, w * ss), np.uint8)
    cv2.polylines(ml, [np.int32(np.round((cp - (x0, y0)) * ss))], False, 255,
                  max(1, int(round(qe["linha"]["larg_px"] * ss))), cv2.LINE_AA)
    al = cv2.resize(ml.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    reg = img[y0:y1, x0:x1].astype(np.float32)
    # a conta bate com a final longe da linha? (o desenho de antes, onde a escada é cheia)
    longe = (a > 0.999) & ~_dil(al > 0.002, 3)
    dif = np.abs(reg - des_v)[longe].mean()
    troca = _dil((al > 0.002) | (np.abs(dep_v - dep_n) > 0.002), q["folga_px"])
    # o fundo de junto, nas pontas da linha fora da escada: o px da mesma coluna, `fundo_px` acima (no alto) ou abaixo
    fundo = reg.copy()
    meio = h // 2
    fp = q["fundo_px"]
    for yy in range(h):
        y2 = max(yy - fp, 0) if yy < meio else min(yy + fp, h - 1)
        fundo[yy] = reg[y2]
    novo = des_n * a[..., None] + fundo * (1 - a[..., None])
    reg[troca] = novo[troca]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    escada estreita: a linha de corte sai ({int(troca.sum())} px refeitos; a divisa do nevoado reta); a conta "
          f"bate com a final longe da linha (diferença média {dif:.2f})")
    return out


def _dil(m, r):
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)) > 0


def bege(Q, img, q=BEGE):
    im = img.astype(np.float32)
    B = cv2.morphologyEx(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2).astype(np.uint8), cv2.MORPH_CLOSE,
                         np.ones((5, 5), np.uint8)) > 0
    B &= ~(BS.quieto(FA.paredes_pdf, Q) > 0.3)
    f = cv2.GaussianBlur(im, (0, 0), 0.7)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    verde = f[..., 1] > f[..., 2] + 4
    cand = B & ((croma < q["croma_obj"]) | (lum < q["lum_obj"]) | verde)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), connectivity=8)
    ok = np.zeros(n, bool)
    ok[1:] = (st[1:, cv2.CC_STAT_AREA] >= q["area_obj"])
    obj = _dil(ok[lab], 1)
    ys, xs = np.nonzero(B)
    y0, y1 = max(ys.min() - 30, 0), min(ys.max() + 31, Q.H)
    x0, x1 = max(xs.min() - 30, 0), min(xs.max() + 31, Q.W)
    piso = (B & ~obj)[y0:y1, x0:x1]
    sub = cv2.inpaint(img[y0:y1, x0:x1].copy(), ((~piso) * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    tom = cv2.GaussianBlur(cv2.medianBlur(sub, q["mediana_px"]).astype(np.float32), (0, 0), 1.5)
    tl = tom.mean(axis=2)
    gx, gy = cv2.Sobel(tl, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(tl, cv2.CV_32F, 0, 1, ksize=3)
    aresta = _dil(np.hypot(gx, gy) / 8 > q["aresta"], q["aresta_px"])
    lumv = im[y0:y1, x0:x1].mean(axis=2)
    texto = _dil(piso & (lumv < q["texto"] * tl), 2)
    # as linhas dos degraus (corridas escuras compridas, deitadas ou em pé) ficam inteiras, como estão
    escuro = (piso & (lumv < q["linha"] * tl)).astype(np.uint8)
    linhas = (cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((1, 21), np.uint8)) |
              cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((21, 1), np.uint8))) > 0
    texto |= _dil(linhas, 2)
    D = im[y0:y1, x0:x1] / np.maximum(tom, 1)
    novo = tom * (1 + q["forca"] * (D - 1))
    m = (piso & ~aresta & ~texto).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 0.8) * (piso & ~texto)
    out = im.copy()
    out[y0:y1, x0:x1] = im[y0:y1, x0:x1] * (1 - m[..., None]) + novo * m[..., None]
    print(f"    Bege Bahia: as manchas a {q['forca'] * 100:.0f}% em {int(piso.sum())} px (o pátio, os degraus, o caminho e "
          "o depósito)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def travertino(out, q=TRAVERTINO):
    """As manchas largas do travertino da varanda saem: a baixa frequência (média normalizada no piso, sem o texto) vai
    à mediana do piso, com `forca`; o veio fino e o texto ficam."""
    x0, y0, x1, y1 = q["px"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    lum = reg.mean(axis=2)
    med = float(np.median(lum))
    piso = lum > q["texto"] * med
    piso = cv2.erode(piso.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    # as manchas são faixas deitadas (o veio do travertino): a média normalizada esticada na horizontal
    sx, sy = q["sigma"]
    m = piso.astype(np.float32)
    num = cv2.GaussianBlur(reg * m[..., None], (0, 0), sigmaX=sx, sigmaY=sy)
    den = cv2.GaussianBlur(m, (0, 0), sigmaX=sx, sigmaY=sy)[..., None]
    L = num / np.maximum(den, 1e-4)
    alvo = np.median(reg[piso], axis=0)
    # (revisão do 12K) só no piso: as paredes e as esquadrias dentro do retângulo ficam (longe do piso, a média
    # normalizada não tem amostra e clareava a parede de cima)
    no_piso = (lum > q["texto"] * med).astype(np.float32) * np.clip(den[..., 0] / q["den_min"], 0, 1)
    reg += q["forca"] * (alvo[None, None] - L) * no_piso[..., None]
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    varanda: as manchas largas do travertino saem (BGR mediano {np.round(alvo).astype(int)}, força "
          f"{q['forca']})")
    return out


def filete(Q, out, q=FILETE):
    w = q["larg_m"] * Q.px_m
    x, y0, y1 = q["x"], q["y0"], q["y1"]
    X0, Y0 = int(np.floor(x - w)) - 3, int(np.floor(y0))
    W, H = int(np.ceil(2 * w)) + 6, int(np.ceil(y1 - y0))
    # a pedra: o Bege Bahia do pátio `fonte_dx` px à esquerda, um pouco mais clara
    pedra = out[Y0:Y0 + H, X0 + q["fonte_dx"]:X0 + q["fonte_dx"] + W].astype(np.float32) * q["clarear"]
    a = _alfa_poligono([(x - w / 2, y0), (x + w / 2, y0), (x + w / 2, y1), (x - w / 2, y1)], X0, Y0, W, H, q["ss"])
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    reg = reg * (1 - a[..., None]) + pedra * a[..., None]
    # a sombrinha do mini degrau no travertino (à direita) e o fio da aresta
    xe = x + w / 2
    sb = _alfa_poligono([(xe, y0), (xe + 1.6, y0), (xe + 1.6, y1), (xe, y1)], X0, Y0, W, H, q["ss"])
    reg *= (1 - q["sombra"] * sb)[..., None]
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    fio = _alfa_poligono([(xe - 0.3, y0), (xe + 0.3, y0), (xe + 0.3, y1), (xe - 0.3, y1)], X0, Y0, W, H, q["ss"])
    out = _pintar(out, fio * q["fio_alfa"], X0, Y0, q["fio"])
    print(f"    o filete de Bege Bahia entre o pátio e o travertino ({w:.1f} px, um mini degrau com o fio da aresta)")
    return out


def pilar(Q, out, q=PILAR):
    ss = q["ss"]
    cx, cy = q["centro_px"]
    r = q["diam_m"] * Q.px_m / 2
    x0, y0 = int(cx - r) - 2, int(cy - r) - 2
    w = h = int(2 * r) + 5
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.circle(m, (int(round((cx - x0) * ss)), int(round((cy - y0) * ss))), int(round(r * ss)), 255, -1, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    out = _pintar(out, a, x0, y0, q["cor"])
    print(f"    o pilar redondo de {q['diam_m']:.2f} m no alto do encontro dos pisos, em ({cx:.0f}, {cy:.0f})")
    return out


def floreira(Q, img, q=FLOREIRA):
    """O canteiro da floreira (`final3840_casac.floreira_s`) com a forração miúda e as plantinhas menores."""
    qs = C.FLOREIRA_S
    fl = Q.cor([C.FLOREIRA_COR], tol=6).astype(np.uint8)
    x0, y0, x1, y1 = qs["caixa"]
    m = np.zeros_like(fl)
    m[y0 - 2:y1 + 2, x0 - 2:x1 + 2] = fl[y0 - 2:y1 + 2, x0 - 2:x1 + 2]
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5) * m
    rng = np.random.default_rng(q["semente"])
    plantas = []
    tipos = ("arbusto_1", "arbusto_2", "arbusto_3")
    n = int(round(1 / q["passo"]))
    for i in range(n):
        v = (i + 0.5) / n + rng.uniform(-0.15, 0.15) * q["passo"]
        u = 0.5 + (0.12 if i % 2 else -0.12) + rng.uniform(-0.05, 0.05)
        plantas.append((tipos[i % 3], float(rng.uniform(*q["d_m"])), (float(u), float(v)), int(rng.integers(0, 4)) * 90))
    cfg = {"terra": C.JARDINS_C["terra"], "terra_ruido": C.JARDINS_C["terra_ruido"],
           "forracao": dict(C.JARDINS_C["forracao"], d_m=q["forracao_m"], passo_m=q["forracao_passo_m"]),
           "plantas": plantas, "transbordo_m": 0.0, "semente": q["semente"]}
    B, AJ = F.B, F.AJ
    with F.em_quadro(Q):
        AJ.base_terreo, base = (lambda forma, c="Terreo": cv2.resize(Q.chapada, (forma[1], forma[0]),
                                                                      interpolation=cv2.INTER_NEAREST)), AJ.base_terreo
        try:
            r = B.mascara_pdf
            B.mascara_pdf = lambda chave, forma, **kw: r("Subsolo", forma, **kw)
            with contextlib.redirect_stdout(io.StringIO()):
                out = B.canteiro(np.ascontiguousarray(img.copy()), a, (x0, y0, x1, y1), cfg, Q.px_m,
                                 "floreira da sauna")
        finally:
            B.mascara_pdf = r
            AJ.base_terreo = base
    # o canteiro só dentro da floreira (ele refazia também o entorno: os degraus, o rótulo da sauna, o S da escada)
    dentro = cv2.dilate((a > 0.01).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    fim = img.copy()
    fim[dentro] = out[dentro]
    print(f"    floreira: {len(plantas)} plantinhas de {q['d_m'][0]:.2f} a {q['d_m'][1]:.2f} m e a forração miúda")
    return fim


def escadas(out, qs=ESCADAS):
    from PIL import ImageFont
    from rodape_entrega import FONTES
    from cliente_subsolo_casaa_0511 import _alfa_texto
    e = FA.ESCADA_A
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), e["corpo_px"] * 4)
    for q in qs:
        # o S de antes sai (o degrau logo ao lado, na mesma linha) e volta logo abaixo da seta
        if q["s_px"] is not None:
            x0, y0, x1, y1 = q["s_px"]
            dx, dy = q["s_fonte"]
            reg = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
            s_ = cv2.dilate((reg < 150).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            ys, xs = np.nonzero(s_)
            out[ys + y0, xs + x0] = out[ys + y0 + dy, xs + x0 + dx]
            pts = np.float32(q["triangulo"])
            cx = float(pts[:, 0].min() + pts[:, 0].max()) / 2
            l_, t_, r_, b_ = fonte.getbbox("S", anchor="ls")
            ox, oy = cx - (l_ + r_) / 8, q["letra_topo"] - t_ / 4
            W, H = int((r_ - l_) / 4) + 12, e["corpo_px"] * 3
            X0, Y0 = int(ox) - 4, int(oy) - e["corpo_px"] * 2
            a = _alfa_texto("S", fonte, e["corpo_px"], ox, oy, (X0, Y0, W, H))
            out = _pintar(out, a, X0, Y0, e["cor_texto"])
        # a seta
        pts = np.float32(q["triangulo"])
        bx0, by0 = np.floor(pts.min(axis=0)).astype(int) - 2
        bx1, by1 = np.ceil(pts.max(axis=0)).astype(int) + 3
        out = _pintar(out, _alfa_poligono(pts, bx0, by0, bx1 - bx0, by1 - by0), bx0, by0, COR_SETA)
        # a descrição
        larg = [fonte.getlength(t) / 4 for t in q["texto"]]
        for i, (linha, lw) in enumerate(zip(q["texto"], larg)):
            tx, ly = q["centro_x"] - lw / 2, q["base_y"] + i * ENTRELINHA
            W, H = int(lw) + 12, e["corpo_px"] * 3
            X0, Y0 = int(tx) - 4, int(ly) - e["corpo_px"] * 2
            a = _alfa_texto(linha, fonte, e["corpo_px"], tx, ly, (X0, Y0, W, H))
            if q["fundo"] is not None:                    # a hachura limpa em volta do texto
                f = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
                f = cv2.GaussianBlur(f, (0, 0), 1.0)
                out = _pintar(out, np.clip(f, 0, 1), X0, Y0, q["fundo"])
            out = _pintar(out, a, X0, Y0, e["cor_texto"])
        print(f"    {q['nome']}: a seta no 1º degrau{', o S logo abaixo dela' if q['s_px'] else ''} e "
              f"\"{' / '.join(q['texto'])}\"")
    return out


def portas(Q, out, q=PORTAS):
    import pedidos_subsolo_casab_1211 as PB
    # a soleira no bege das soleiras de antes da Casa C (a mediana do vão da porta da sauna), não no cinza da Casa B
    x0, y0, x1, y1 = q["soleira_px"]
    sol = tuple(float(v) for v in np.median(out[y0:y1, x0:x1].reshape(-1, 3), axis=0))
    base = dict(PB.PORTAS_SB, tique_px=(0, 0, 0, 0), soleira=sol)
    with contextlib.redirect_stdout(io.StringIO()):
        out = PB.portas_sb(Q, out, q=dict(base, portas=q["portas"]))
        T = np.ascontiguousarray(out.transpose(1, 0, 2))
        T = PB.portas_sb(Q, T, q=dict(base, portas=q["transpostas"]))
    out = np.ascontiguousarray(T.transpose(1, 0, 2))
    nomes = [p["nome"] for p in q["portas"] + q["transpostas"]]
    print(f"    portas: {', '.join(nomes)} com a folha de madeira clara quina com quina na ponta da parede, sem os "
          "marcos, a soleira no vão")
    return out



def caixote(Q, out, q=CAIXOTE):
    ss = q["ss"]
    ox0, oy0, ox1, oy1 = q["fora"]
    ix0, iy0, ix1, iy1 = q["dentro"]
    X0, Y0 = int(np.floor(ox0)) - 4, int(np.floor(oy0)) - 4
    W, H = int(np.ceil(ox1)) + 5 - X0, int(np.ceil(oy1)) + 5 - Y0
    fora = _alfa_poligono([(ox0, oy0), (ox1, oy0), (ox1, oy1), (ox0, oy1)], X0, Y0, W, H, ss)
    dentro = _alfa_poligono([(ix0, iy0), (ix1, iy0), (ix1, iy1), (ix0, iy1)], X0, Y0, W, H, ss)
    borda = np.clip(fora - dentro, 0, 1)
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    # a sombra curta da caixa no piso (para baixo e à esquerda), fora dela
    sp = cv2.GaussianBlur(cv2.warpAffine(fora, np.float32([[1, 0, -1.6], [0, 1, 1.6]]), (W, H)), (0, 0), 1.2)
    reg *= (1 - q["sombra_piso"] * sp * (1 - fora))[..., None]
    # a sombra da borda na terra (junto à borda de cima e à da direita)
    st = cv2.GaussianBlur(cv2.warpAffine(1 - dentro, np.float32([[1, 0, -1.4], [0, 1, 1.4]]), (W, H),
                                         borderValue=1), (0, 0), 1.0)
    reg *= (1 - q["sombra_terra"] * st * dentro)[..., None]
    # a borda: o concreto claro com um grão leve
    rng = np.random.default_rng(q["semente"])
    gr = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.8)
    cor = np.float32(q["cor"])[None, None] * (1 + q["ruido"] * gr / max(float(gr.std()), 1e-6))[..., None]
    reg = reg * (1 - borda[..., None]) + cor * borda[..., None]
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    # os fios das arestas (a de fora e a de dentro)
    for (a0, b0, a1, b1) in (q["fora"], q["dentro"]):
        M = np.zeros((H * ss, W * ss), np.uint8)
        cv2.rectangle(M, (int(round((a0 - X0) * ss)), int(round((b0 - Y0) * ss))),
                      (int(round((a1 - X0) * ss)), int(round((b1 - Y0) * ss))), 255, max(1, int(0.5 * ss)), cv2.LINE_AA)
        fio = cv2.resize(M.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
        out = _pintar(out, fio * q["fio_alfa"], X0, Y0, q["fio"])
    print(f"    floreira: o caixote do PDF ({(ox1 - ox0) / Q.px_m:.2f} x {(oy1 - oy0) / Q.px_m:.2f} m, a borda de "
          f"{(ix0 - ox0) / Q.px_m * 100:.0f} cm) em concreto claro, com as arestas, a sombra na terra e no piso")
    return out


def quinas(out, qs=QUINAS, cor=(80, 80, 80), tol=8, gap_max=10, ss=8):
    """A ponta da parede até a quina da folha (vértice com vértice): onde sobrou soleira ou batente entre a parede e a
    folha, entra a parede (a face do lado da folha até a linha da borda de fora da folha)."""
    feitas = []
    for (fx0, fy0, fx1, fy1), dobra, lado, transp in qs:
        im = out.transpose(1, 0, 2) if transp else out
        I = im.astype(np.int16)
        par = np.abs(I - np.int16(cor)).max(axis=2) <= tol
        yref = int(round(fy0)) - 3 if dobra == "topo" else int(round(fy1)) + 3
        # as faces da parede na linha de referência (a corrida que termina junto à folha)
        xe = fx0 if lado > 0 else fx1
        xs = [x for x in range(int(xe) - 4, int(xe) + 5) if par[yref, x]]
        if not xs:
            continue
        x = xs[len(xs) // 2]
        a_, b_ = x, x
        while par[yref, a_ - 1]:
            a_ -= 1
        while par[yref, b_ + 1]:
            b_ += 1
        wa, wb = a_, b_ + 1
        if dobra == "topo":
            y = int(np.floor(fy0))
            while y > fy0 - gap_max and not par[y, wa:wb].all():
                y -= 1
            r0, r1 = y + 1, fy0
        else:
            y = int(np.ceil(fy1))
            while y < fy1 + gap_max and not par[y, wa:wb].all():
                y += 1
            r0, r1 = fy1, y
        if r1 - r0 <= 0.05:
            continue
        Y0, Y1 = int(np.floor(r0)), int(np.ceil(r1))
        yy = np.arange(Y0, Y1) + 0.5
        cob = np.clip(np.minimum(yy + 0.5, r1) - np.maximum(yy - 0.5, r0), 0, 1)[:, None, None]
        reg = im[Y0:Y1, wa:wb].astype(np.float32)
        im[Y0:Y1, wa:wb] = np.clip(np.round(reg * (1 - cob) + np.float32(cor) * cob), 0, 255).astype(np.uint8)
        feitas.append(f"{r1 - r0:.1f} px")
    # os tiquinhos escuros que sobraram dos marcos em volta das portas (pontos isolados quase pretos) saem
    limpos = 0
    for (fx0, fy0, fx1, fy1), dobra, lado, transp in qs:
        im = out.transpose(1, 0, 2) if transp else out
        X0, Y0 = int(min(fx0, fx1)) - 16, int(fy0) - 56
        X1, Y1 = int(max(fx0, fx1)) + 4, int(fy1) + 56
        sub = np.ascontiguousarray(im[Y0:Y1, X0:X1])
        lum = sub.astype(np.float32).mean(axis=2)
        esc = (lum < 55).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(esc, connectivity=8)
        m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= 6]).astype(np.uint8)
        if m.any():
            m = cv2.dilate(m, np.ones((3, 3), np.uint8))
            novo = cv2.inpaint(sub, m * 255, 2, cv2.INPAINT_TELEA)
            im[Y0:Y1, X0:X1][m > 0] = novo[m > 0]
            limpos += int(n - 1)
    print(f"    portas: a ponta da parede até a quina da folha em {len(feitas)} portas ({', '.join(feitas)}); "
          f"{limpos} tiquinhos dos marcos fora")
    return out

# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    # (revisão do 12K) o fundo branco e a escada estreita sem a linha de corte, antes de tudo (as setas e os textos vêm
    # depois, já no branco)
    out = fundo_branco(Q, out)
    out = escada_sem_corte(Q, out)
    out = bege(Q, out)
    # (13/11, "Era pra mexer no Travertino ou era pra mexer no Bege Bahia?") o travertino tinha voltado como estava;
    # (revisão do 12K, "NO PISO DO TRAVERTINO REMOVER MANCHAS CINZAS, CONFORME ORIENTAÇÃO") as manchas cinzas saem
    out = travertino(out)
    out = filete(Q, out)
    out = pilar(Q, out)
    out = floreira(Q, out)
    out = caixote(Q, out)
    out = portas(Q, out)
    out = quinas(out)
    out = escadas(out)
    return out


def antes_depois(antes, depois, quadros=None, prefixo="postits"):
    quadros = quadros or ANTES_DEPOIS
    for nome, (x0, y0, x1, y1) in quadros.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(4.0, 1000 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaC_PH_Subsolo_1311_{prefixo}_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois ({prefixo}): {', '.join(quadros)}")


def final_de(commit):
    dado = subprocess.run(["git", "show", f"{commit}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"], cwd=RAIZ_GIT,
                          capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes) if a.antes else final_de(ANTES_COMMIT)
    depois = aplicar(antes)
    if a.saida:
        cv2.imwrite(a.saida, depois)
        print(f"    {a.saida}")
        return
    atual = cv2.imread(str(FINAL))
    cv2.imwrite(str(FINAL), depois)
    print(f"    {FINAL.name}")
    antes_depois(antes, depois)
    antes_depois(atual, depois, REVISAO, "revisao12k")


if __name__ == "__main__":
    main()

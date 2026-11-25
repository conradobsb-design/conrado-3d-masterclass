"""Casa A Térreo, 4ª leva de 25/11 (os recortes do 12K B): a escada do jardim, as geladeiras e as máquinas de lavar, as
plantas, o lavabo, o escritório, o armário junto ao lavabo e a soleira do GÁS.

- **Escada** ("vamos refazer a escada. a divisão em diagonal para a parte que ficará transparente e o formato dos
  degraus. melhorar a representação do guarda corpo", com a imagem do PDF): redesenhada na geometria do PDF. 1º lance,
  degraus 1 a 9 (de 2255,9 a 2417,1, passo 17,9), o patamar inteiro (2417,1 a 2488,7, sem degraus) e o 2º lance, 11 a
  19 (de 2417,1 a 2254,1). A parte cheia é a do 1º lance à esquerda da linha de corte do PDF (a diagonal de 2363,1 no
  alto a 2399,2 embaixo, com a quebra em Z no meio, desenhada fina); o resto (o fim do 1º lance, o patamar e o 2º
  lance, tracejados no PDF) fica transparente como antes (o tom dos degraus com o desenho a 0,55 e 0,15 da grama). Os
  degraus: a pedra de hoje (o tom mediano dos degraus cheios) com o veio do travertino novo ao comprido do degrau, um
  pouco diferente em cada pedra, o bocel em linha fina com a sombra curta no degrau de baixo (no 1º lance à esquerda,
  no 2º à direita). Os guarda-corpos do PDF (as duas bordas de cada lance, o U em volta do vão do jardim e o contorno
  do patamar) em vidro: a faixa de 1,2 px clara com o contorno fino escuro, a sombra curta na parte cheia; na parte
  transparente, mais leves. Os rótulos (SOBE PARA O 1º PAVIMENTO, a seta e o S) voltam por cima.

Final, prancha e 12K A e B.

  python3 terreo_casaa_2511d.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vetor_2511 as V               # noqa: E402
import vidros_claros_1911 as VC      # noqa: E402

PLANTA = "A_Terreo"
PX_M = 59.7059
TEX = EP.PROJ / "_texturas/travertino_opcoes_2511"

ESCADA = dict(
    caixa=(2250.0, 908.0, 2494.0, 1088.0),
    sup=(2255.9, 914.6, 2417.1, 986.2), pat=(2417.1, 914.6, 2488.7, 1081.8), inf=(2254.1, 1010.1, 2417.1, 1081.8),
    xs_sup=[2255.9, 2273.8, 2291.7, 2309.6, 2327.5, 2345.4, 2363.4, 2381.3, 2399.2, 2417.1],
    xs_inf=[2254.1, 2273.8, 2291.7, 2309.6, 2327.5, 2345.4, 2363.4, 2381.3, 2399.2, 2417.1],
    quebra=[(2363.1, 914.6), (2379.3, 946.4), (2374.3, 946.4), (2388.2, 954.4), (2383.3, 954.4), (2399.2, 986.2)],
    # os guarda-corpos (ARQ_ELEMENTOS FIXOS): as bordas dos lances, o U do vão e o contorno do patamar
    gc=[(2255.9, 917.0, 2486.4, 918.2), (2485.2, 917.0, 2486.4, 1079.4), (2254.1, 1078.2, 2486.4, 1079.4),
        (2255.9, 982.6, 2420.7, 983.8), (2419.5, 982.6, 2420.7, 1013.7), (2254.1, 1012.5, 2420.7, 1013.7)],
    grama=(2262.0, 895.0, 2480.0, 911.0),          # a grama logo acima (o tom do que está por baixo)
    veu=0.55, grama_peso=0.15, tex_m=1.2, tex_ganho=0.55,
    bocel=dict(larg=0.28, escuro=0.30, sombra=0.11, sombra_px=1.3, luz=0.05),
    # o vidro: claro sobre os degraus cheios, mais escuro sobre a parte transparente
    vidro=(238, 236, 231), vidro_borda=(112, 112, 110), vidro_t=(150, 150, 147), vidro_borda_t=(68, 68, 68),
    borda_larg=0.24, gc_sombra=0.16,
    corte=(78, 78, 78), corte_larg=0.30,
    # o contorno da escada (o claro de antes, 1,5 px fora da linha do PDF, sai: a grama de mais longe por cima) e o
    # contorno novo na linha do PDF
    limpa=[((2256.0, 910.5, 2492.0, 914.6), (0.0, -6.0)), ((2488.7, 912.0, 2492.5, 1084.5), (5.0, 0.0)),
           ((2254.0, 1081.8, 2492.0, 1085.0), (0.0, 5.0))],
    contorno=[((2255.9, 914.6), (2488.7, 914.6)), ((2488.7, 914.6), (2488.7, 1081.8)),
              ((2488.7, 1081.8), (2254.1, 1081.8)), ((2254.1, 1010.1), (2417.1, 1010.1)),
              ((2417.1, 1010.1), (2417.1, 986.2)), ((2417.1, 986.2), (2255.9, 986.2))],
    contorno_cor=(203, 202, 197), contorno_larg=0.7)


def _tex(nome, lado, giro=True):
    T = cv2.imread(str(TEX / nome)).astype(np.float32)
    if giro:
        T = cv2.rotate(T, cv2.ROTATE_90_CLOCKWISE)          # o veio ao comprido do degrau (na vertical da planta)
    T = cv2.resize(T, (lado, lado), interpolation=cv2.INTER_AREA)
    T2 = np.concatenate([T, T[:, ::-1]], 1)
    return np.concatenate([T2, T2[::-1]], 0)


def escada(img, escala, origem, q=ESCADA):
    for r, d in q["limpa"]:
        rx0, ry0, rx1, ry1 = V.janela(img, r, escala, origem, folga=0)
        dx, dy = int(round(d[0] * escala)), int(round(d[1] * escala))
        img[ry0:ry1, rx0:rx1] = img[ry0 + dy:ry1 + dy, rx0 + dx:rx1 + dx]
    jan = V.janela(img, q["caixa"], escala, origem)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, escala, origem)
    a_sup = V.cob([V.ret(*q["sup"])], jan, escala, origem)
    a_pat = V.cob([V.ret(*q["pat"])], jan, escala, origem)
    a_inf = V.cob([V.ret(*q["inf"])], jan, escala, origem)
    pe = np.clip(a_sup + a_pat + a_inf, 0, 1)
    x0s, y0s, _, y1s = q["sup"]
    cheia_pol = [(x0s, y0s)] + q["quebra"] + [(x0s, y1s)]
    a_cheia = V.cob([cheia_pol], jan, escala, origem) * a_sup
    a_trans = np.clip(pe - a_cheia, 0, 1)
    # o tom dos degraus cheios de hoje (sem as letras nem as linhas) e o da grama
    L = reg.mean(2)
    zona = a_cheia > 0.99
    med = np.median(L[zona])
    tom = np.median(reg[zona & (np.abs(L - med) < 12)], axis=0)
    gx0, gy0, gx1, gy1 = V.janela(img, q["grama"], escala, origem, folga=0)
    grama = np.median(img[gy0:gy1, gx0:gx1].reshape(-1, 3).astype(np.float32), axis=0)
    # as letras (rótulos) da parte cheia, para voltar por cima
    faixa = ((ys > q["sup"][1] + 5.0) & (ys < q["sup"][3] - 5.0))[:, None]
    at, cor_t = V.letras(reg, (a_cheia > 0.5) & faixa, escala=escala, ref=med, dif=90.0, piso_dif=35.0)
    # as pedras: o veio do travertino novo, ao comprido, um deslocamento por degrau
    lado = max(16, int(round(q["tex_m"] * PX_M * escala)))
    T2 = _tex("travertino_opcao_2.png", lado)
    Tl = T2.mean(2)
    Tl = Tl / Tl.mean()
    p = T2.shape[0]
    rng = np.random.default_rng(642)
    D = np.empty_like(reg)
    D[:] = tom
    H, W = reg.shape[:2]
    jj = np.arange(X0, X1)
    ii = np.arange(Y0, Y1)
    pedras = []
    for k, (ax, bx) in enumerate(zip(q["xs_sup"][:-1], q["xs_sup"][1:])):
        pedras.append((ax, q["sup"][1], bx, q["sup"][3]))
    for ax, bx in zip(q["xs_inf"][:-1], q["xs_inf"][1:]):
        pedras.append((ax, q["inf"][1], bx, q["inf"][3]))
    pedras.append(q["pat"])
    for k, pr in enumerate(pedras):
        a = V.cob([V.ret(*pr)], jan, escala, origem)
        if not (a > 0).any():
            continue
        dx, dy = rng.integers(0, p, 2)
        f = 1.0 + rng.uniform(-0.015, 0.015)
        tl = Tl[np.mod(ii + dy, p)[:, None], np.mod(jj + dx, p)[None, :]]
        pedra = tom[None, None, :] * (f * (1 + q["tex_ganho"] * (tl - 1)))[..., None]
        D = V.compor(D, a, pedra)
    # o bocel: a linha fina, a sombra no degrau de baixo e a luz na quina
    b = q["bocel"]
    fator = np.ones((H, W), np.float32)
    for xs_l, lim, lado_s in ((q["xs_sup"][1:], q["sup"], -1), (q["xs_inf"][1:], q["inf"], +1)):
        lin = (ys >= lim[1]) & (ys <= lim[3])
        for xl in xs_l:
            d = (xs - xl) * lado_s                  # > 0 do lado do degrau de baixo
            som = np.where(d > 0, np.exp(-d / b["sombra_px"]), 0.0) * b["sombra"]
            luz = np.where((d < 0) & (d > -0.6), b["luz"], 0.0)
            fator[lin] *= (1 - som + luz)[None, :].astype(np.float32)
            a_l = V.cob([V.ret(xl - b["larg"] / 2, lim[1], xl + b["larg"] / 2, lim[3])], jan, escala, origem)
            fator *= (1 - b["escuro"] * a_l)
    D = D * fator[..., None]
    cheio = D
    gp = q["grama_peso"]
    trans = (1 - gp) * ((1 - q["veu"]) * tom + q["veu"] * D) + gp * grama
    out = reg * (1 - pe[..., None]) + cheio * a_cheia[..., None] + trans * a_trans[..., None]
    # o contorno da escada, por fora da linha do PDF
    a_k = np.zeros((H, W), np.float32)
    for p0, p1 in q["contorno"]:
        a_k = np.maximum(a_k, V.cob([V.seg(p0, p1, q["contorno_larg"] * 2)], jan, escala, origem))
    a_k *= (1 - pe)
    out = V.compor(out, a_k, q["contorno_cor"])
    # os guarda-corpos de vidro
    for r in q["gc"]:
        af = V.cob([V.ret(*r)], jan, escala, origem)
        x0, y0, x1, y1 = r
        e = q["borda_larg"]
        dentro = V.cob([V.ret(x0 + e, y0 + e, x1 - e, y1 - e)], jan, escala, origem)
        borda = np.clip(af - dentro, 0, 1)
        w = a_cheia[..., None]
        cor_v = w * np.float32(q["vidro"]) + (1 - w) * np.float32(q["vidro_t"])
        cor_b = w * np.float32(q["vidro_borda"]) + (1 - w) * np.float32(q["vidro_borda_t"])
        sb = cv2.GaussianBlur(af, (0, 0), max(0.6 * escala, 0.5))
        Ms = np.float32([[1, 0, 0.6 * escala], [0, 1, 0.8 * escala]])
        sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - af) * a_cheia
        out *= (1 - q["gc_sombra"] * sb)[..., None]
        out = V.compor(out, dentro, cor_v)
        out = V.compor(out, borda, cor_b)
    # a linha de corte (a diagonal com a quebra em Z)
    qb = q["quebra"]
    a_c = np.zeros((H, W), np.float32)
    for p0, p1 in zip(qb[:-1], qb[1:]):
        a_c = np.maximum(a_c, V.cob([V.seg(p0, p1, q["corte_larg"])], jan, escala, origem))
    out = V.compor(out, a_c * 0.9, q["corte"])
    # os rótulos por cima
    out = V.compor(out, at, cor_t)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# O piso de travertino novo (o mesmo de `travertino_terreo_casaa_2511`, na mesma fase: a textura espelhada em coordenadas
# absolutas da imagem, 1,2 m por quadro), para refazer trechos: a luz é a do piso novo em volta (a razão imagem/textura
# nos px que são o piso novo, alisada), sem as manchas.
import travertino_terreo_casaa_2511 as TV   # noqa: E402

DZ_S = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]["s"]
_TEX = {}


def tex_piso(escala, giro=False):
    lado = int(round(TV.PISO["m"] * PX_M * (DZ_S if escala > 1.5 else 1.0)))
    k = (lado, giro)
    if k not in _TEX:
        if giro:
            _TEX[k] = _tex("travertino_opcao_2.png", lado)
        else:
            _TEX[k] = TV.tex_tile(TV.PISO["textura"], lado)
    return _TEX[k]


def piso_tt(jan, escala, giro=False):
    X0, Y0, X1, Y1 = jan
    return TV.textura_em(tex_piso(escala, giro), np.arange(X0, X1), np.arange(Y0, Y1))


def _bbox(polys):
    xs = [p[0] for pol in polys for p in pol]
    ys = [p[1] for pol in polys for p in pol]
    return min(xs), min(ys), max(xs), max(ys)


def refazer_piso(img, escala, origem, zona, objetos=(), sombra=0.14, letras=False, luz_sig=14.0, tol=0.10,
                 escurecer=1.0, giro=False, ref_luz=None, pena=0.0):
    """O piso novo nos polígonos `zona` (px da final), menos os `objetos` (polígonos), com a sombra curta deles; as
    letras escuras do trecho (os rótulos) voltam por cima. `ref_luz`: polígonos onde medir a luz (padrão: a zona)."""
    x0, y0, x1, y1 = _bbox(list(zona) + list(objetos) + (list(ref_luz) if ref_luz else []))
    jan = V.janela(img, (x0, y0, x1, y1), escala, origem, folga=int(6 * escala) + 2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    az = V.cob(list(zona), jan, escala, origem)
    ao = V.cob(list(objetos), jan, escala, origem) if objetos else np.zeros((H, W), np.float32)
    ar = V.cob(list(ref_luz), jan, escala, origem) if ref_luz else az
    TT = piso_tt(jan, escala, giro)
    Lr = reg.mean(2)
    r = Lr / np.maximum(TT.mean(2), 1.0)
    livre = (ar > 0.99) & (ao < 0.01)
    # a luz do piso novo: o valor mais frequente da razão (as manchas e as peças velhas ficam fora)
    h, e = np.histogram(r[livre], bins=80, range=(0.6, 1.4))
    h = np.convolve(h, np.ones(5) / 5, mode="same")
    med = float(e[np.argmax(h)] + (e[1] - e[0]) / 2)
    ok = livre & (np.abs(r - med) < tol)
    sig = luz_sig * escala
    num = cv2.GaussianBlur(np.where(ok, r, 0).astype(np.float32), (0, 0), sig)
    den = cv2.GaussianBlur(ok.astype(np.float32), (0, 0), sig)
    luz = np.where(den > 1e-3, num / np.maximum(den, 1e-3), med)
    novo = TT * (luz * escurecer)[..., None]
    if objetos and sombra:
        Ms = np.float32([[1, 0, 0.7 * escala], [0, 1, 0.9 * escala]])
        sb = cv2.GaussianBlur(cv2.warpAffine(ao, Ms, (W, H)), (0, 0), max(1.1 * escala, 0.6)) * (1 - ao)
        novo *= (1 - sombra * sb)[..., None]
    if pena:                                        # a transição suave na borda da zona (para dentro)
        d = cv2.distanceTransform((az > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / max(escala, 1e-3)
        az = az * np.clip(d / pena, 0, 1)
    a = az * (1 - ao)
    out = reg * (1 - a[..., None]) + novo * a[..., None]
    if letras:
        z = (az > 0.5) & (ao < 0.5)
        at, cor = V.letras(reg, z, escala=escala, ref=float(np.median(Lr[livre])), dif=80.0, piso_dif=30.0,
                           area_min=0.8)
        out = V.compor(out, at, cor)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Soleiras no bege (pedido do usuário no escritório: "corrija a representação das soleiras para o tom beje"): o Bege
# Bahia da casa, um pouco mais fundo que o travertino, liso com um grão leve, e o contorno fino um tom abaixo.
SOLEIRA = dict(cor=(176, 202, 225), contorno=(138, 156, 176), contorno_larg=0.22, grao=0.025)


def soleira(img, escala, origem, rets, q=SOLEIRA, cantos=()):
    """As soleiras (retângulos, px da final) no bege; `cantos`: retângulos de parede (o cinza 53) por cima."""
    x0, y0, x1, y1 = _bbox([V.ret(*r) for r in rets])
    jan = V.janela(img, (x0, y0, x1, y1), escala, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    rng = np.random.default_rng(int(x0 * 7 + y0))
    ruido = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), max(0.6 * escala, 0.5))
    ruido /= max(float(ruido.std()), 1e-3)
    cor = np.float32(q["cor"])[None, None, :] * (1 + q["grao"] * ruido)[..., None]
    for r in rets:
        a = V.cob([V.ret(*r)], jan, escala, origem)
        e = q["contorno_larg"]
        dentro = V.cob([V.ret(r[0] + e, r[1] + e, r[2] - e, r[3] - e)], jan, escala, origem)
        reg = V.compor(reg, a, cor)
        reg = V.compor(reg, np.clip(a - dentro, 0, 1), q["contorno"])
    for r in cantos:
        reg = V.compor(reg, V.cob([V.ret(*r)], jan, escala, origem), (53, 53, 53))
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def folhas(img, escala, origem, rets):
    """As folhas e caixilhos do PDF no padrão das esquadrias (o perfil cinza claro, o vidro claro, a linha fina)."""
    traco = 0.5 if escala <= 1.5 else min(0.5, EP.TRACO_12K / escala)
    for r in rets:
        img = VC.redesenhar(img, [r], escala, origem, traco, inpaint=False)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# As soleiras no bege (GÁS, área de serviço, janelas do WC e do banho varanda), com as folhas redesenhadas por cima
SOLEIRAS = dict(
    gas=dict(rets=[(1706.6, 1634.1, 1769.3, 1643.0)],
             cantos=[(1706.6, 1634.1, 1708.3, 1636.2), (1767.5, 1634.1, 1769.3, 1636.2)],     # os tocos da parede
             folhas=[(1706.6, 1636.2, 1708.9, 1643.0), (1766.9, 1636.2, 1769.3, 1643.0)]),   # os batentes
    correr=dict(rets=[(1778.2, 1631.1, 1909.6, 1643.0)], cantos=[],
                folhas=[(1780.6, 1637.1, 1846.3, 1640.0), (1841.5, 1640.0, 1907.2, 1643.0)]),
    janelas=dict(rets=[(1550.1, 1630.6, 1606.2, 1643.0), (1618.8, 1630.6, 1674.9, 1643.0)], cantos=[],
                 folhas=[(1549.5, 1636.8, 1606.8, 1639.7), (1618.2, 1636.8, 1675.5, 1639.7)]),
)


def soleiras_servico(img, escala, origem):
    for q in SOLEIRAS.values():
        img = soleira(img, escala, origem, q["rets"], cantos=q["cantos"])
        img = folhas(img, escala, origem, q["folhas"])
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Lavabo: a bancada no tom do piso (levemente escuro), a faixa ao lado da peça de baixo em piso, a soleira da porta, a
# janela alta (a soleira no vão da parede e a folha fina) e o piso sob a janela antiga.
LAVABO = dict(
    bancada=[(2315.6, 410.0, 2345.4, 467.4), (2327.5, 467.4, 2345.4, 514.5)],
    escurecer=0.90, antes="60f949f",                 # a luz (a cuba esculpida) vem da bancada de antes do fiorito
    faixa=(2315.6, 467.4, 2327.5, 514.5), faixa_luz=(2290.0, 468.0, 2314.0, 512.0),
    porta_soleira=(2265.4, 514.5, 2317.7, 523.5),
    porta_folhas=[(2263.0, 514.5, 2265.4, 521.4), (2317.7, 514.5, 2320.1, 521.4), (2264.7, 460.8, 2267.0, 514.5)],
    jan_piso=(2255.9, 353.3, 2345.4, 361.5), jan_luz=(2262.0, 361.5, 2312.0, 368.0),
    jan_soleira=(2267.8, 349.1, 2333.5, 353.3),
    jan_folhas=[(2267.8, 350.2, 2300.9, 351.6), (2300.4, 350.2, 2333.5, 351.6)])
_SH = {}


def _luz_bancada(q=LAVABO):
    """A luz da bancada (a cuba esculpida, as sombras) na final de antes do fiorito: L / mediana da pedra; e a
    torneira (cinza)."""
    if "sh" not in _SH:
        rel = EP.PLANTAS[PLANTA][0]
        im = EP.git_img(rel, q["antes"])
        x0, y0, x1, y1 = _bbox([V.ret(*r) for r in q["bancada"]])
        bx0, by0, bx1, by1 = int(x0) - 2, int(y0) - 2, int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 2
        reg = im[by0:by1, bx0:bx1].astype(np.float32)
        L = reg.mean(2)
        pedra = (reg[..., 2] - reg[..., 0]) > 15
        Lb = cv2.GaussianBlur(L, (0, 0), 0.5)
        sh = np.ones_like(Lb)
        for r in q["bancada"]:                       # cada peça no seu tom (a de baixo não fica mais clara)
            m = np.zeros(L.shape, bool)
            m[int(r[1]) - by0:int(np.ceil(r[3])) - by0, int(r[0]) - bx0:int(np.ceil(r[2])) - bx0] = True
            sh[m] = Lb[m] / max(float(np.median(L[m & pedra])), 1.0)
        metal = ~pedra & (L < 215)
        _SH["sh"] = (sh.astype(np.float32), metal.astype(np.float32), (bx0, by0))
    return _SH["sh"]


def _no_quadro(mapa, b0, jan, escala, origem):
    """Um mapa em px da final (começando em b0) levado à janela da imagem."""
    X0, Y0, X1, Y1 = jan
    M = np.float32([[escala, 0, (b0[0] - origem[0]) * escala - X0 + 0.5 * escala - 0.5],
                    [0, escala, (b0[1] - origem[1]) * escala - Y0 + 0.5 * escala - 0.5]])
    return cv2.warpAffine(mapa, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def lavabo(img, escala, origem, q=LAVABO):
    # o piso: a faixa ao lado da peça de baixo e a sobra da janela antiga
    img = refazer_piso(img, escala, origem, [V.ret(*q["faixa"])], ref_luz=[V.ret(*q["faixa_luz"])])
    img = refazer_piso(img, escala, origem, [V.ret(*q["jan_piso"])], ref_luz=[V.ret(*q["jan_luz"])])
    # a bancada: o travertino do piso (o veio ao comprido), um pouco mais escuro, com a luz da cuba esculpida
    polys = [V.ret(*r) for r in q["bancada"]]
    jan = V.janela(img, _bbox(polys), escala, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    sh, metal, b0 = _luz_bancada(q)
    shq = _no_quadro(sh, b0, jan, escala, origem)
    mq = _no_quadro(metal, b0, jan, escala, origem)
    TT = piso_tt(jan, escala, giro=True)
    a = V.cob(polys, jan, escala, origem) * (1 - np.clip(mq * 1.5, 0, 1))
    pedra = TT * (q["escurecer"] * shq)[..., None]
    out = V.compor(reg, a, pedra)
    e = 0.25
    borda = np.zeros(a.shape, np.float32)
    for r in q["bancada"]:
        ar = V.cob([V.ret(*r)], jan, escala, origem)
        ad = V.cob([V.ret(r[0] + e, r[1] + e, r[2] - e, r[3] - e)], jan, escala, origem)
        borda = np.maximum(borda, ar - ad)
    out = out * (1 - 0.22 * np.clip(borda, 0, 1))[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    # a soleira da porta e a da janela, as folhas
    img = soleira(img, escala, origem, [q["porta_soleira"]])
    img = folhas(img, escala, origem, q["porta_folhas"])
    img = soleira(img, escala, origem, [q["jan_soleira"]])
    img = folhas(img, escala, origem, q["jan_folhas"])
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Escritório: o piso livre refeito (sem as manchas das peças antigas, a faixa velha junto à parede da direita, o fundo
# da porta), as soleiras das janelas de canto e da porta no bege, as folhas e a porta no padrão, a parede de baixo.
def _circulo(cx, cy, r, n=48):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in t]


def _ret_arred(x0, y0, x1, y1, r, embaixo=True, n=6):
    """Retângulo com os cantos de baixo (ou de cima) arredondados."""
    pts = [(x0, y0), (x1, y0)] if embaixo else []
    if embaixo:
        for k in range(n + 1):
            a = np.pi / 2 * k / n
            pts.append((x1 - r + r * np.cos(a), y1 - r + r * np.sin(a)))
        for k in range(n + 1):
            a = np.pi / 2 + np.pi / 2 * k / n
            pts.append((x0 + r + r * np.cos(a), y1 - r + r * np.sin(a)))
    return pts


def _poltrona_pdf():
    """O contorno da poltrona do escritório no PDF (o caminho fechado, com as curvas achatadas)."""
    Q = EP.quadro(PLANTA)
    for d in Q.desenhos:
        if d["type"] != "f" or d["layer"] != "ARQ_LAYOUT HUMANIZAÇÃO":
            continue
        r = d["rect"]
        a = Q.p2q(r.x0, r.y0)
        b = Q.p2q(r.x1, r.y1)
        if abs(min(a[0], b[0]) - 2529.4) < 0.3 and abs(min(a[1], b[1]) - 521.8) < 0.3:
            pts = []
            for it in d["items"]:
                if it[0] == "l":
                    pts += [Q.p2q(it[1].x, it[1].y), Q.p2q(it[2].x, it[2].y)]
                elif it[0] == "c":
                    p0, c1, c2, p1 = it[1], it[2], it[3], it[4]
                    for t in np.linspace(0, 1, 10):
                        x = (1 - t) ** 3 * p0.x + 3 * (1 - t) ** 2 * t * c1.x + 3 * (1 - t) * t * t * c2.x + t ** 3 * p1.x
                        y = (1 - t) ** 3 * p0.y + 3 * (1 - t) ** 2 * t * c1.y + 3 * (1 - t) * t * t * c2.y + t ** 3 * p1.y
                        pts.append(Q.p2q(x, y))
            return pts
    return []


ESCRITORIO = dict(
    zona=[V.ret(2354.4, 353.3, 2590.5, 598.1)],
    armario_l=[(2354.4, 353.3), (2486.6, 353.3), (2486.6, 378.3), (2372.1, 378.3), (2372.1, 522.2), (2354.4, 522.2)],
    cadeira_mesa=[(2462.8, 389.6), (2486.3, 389.6), (2489.3, 396.0), (2491.5, 404.0), (2491.5, 425.5),
                  (2456.2, 425.5), (2456.2, 404.0), (2458.8, 396.0)],
    pecas=[(2414.2, 424.5, 2534.0, 475.4),          # mesa
           (2498.0 - 72.0, 568.2, 2498.7, 598.1)],  # aparador
    cadeiras=[(2429.9, 472.5, 2458.9, 502.1), (2491.0, 472.5, 2520.6, 502.1)],
    poltrona=(2557.0, 551.8, 27.9),
    mesinha=(2523.7, 569.5, 13.4),
    soleiras=[(2495.9, 341.4, 2593.2, 353.3), (2593.2, 341.4, 2605.2, 355.2), (2593.2, 355.2, 2605.2, 429.1),
              (2345.4, 536.1, 2354.4, 588.5)],
    folhas=[(2495.9, 349.7, 2498.0, 352.7), (2498.0, 349.7, 2591.1, 352.7),                 # janela de cima
            (2590.5, 353.4, 2592.9, 359.3), (2590.5, 359.3, 2592.9, 425.0), (2590.5, 425.0, 2592.9, 430.9),
            (2347.5, 533.8, 2354.4, 536.1), (2347.5, 588.5, 2354.4, 590.8),                 # batentes da porta
            (2354.4, 586.8, 2408.1, 589.2)],                                                # a porta (aberta)
    parede=[(2345.4, 590.8, 2354.4, 601.5), (2354.4, 598.1, 2593.2, 601.5)])


def escritorio(img, escala, origem, q=ESCRITORIO):
    obj = [q["armario_l"], q["cadeira_mesa"]] + [V.ret(*r) for r in q["pecas"]]
    obj += [_ret_arred(*r, 7.0) for r in q["cadeiras"]]
    obj.append(_circulo(*q["poltrona"], n=64))
    pol = _poltrona_pdf()
    if pol:
        obj.append(pol)
    obj.append(_circulo(*q["mesinha"]))
    img = refazer_piso(img, escala, origem, q["zona"], objetos=obj, letras=True)
    jan = V.janela(img, _bbox([V.ret(*r) for r in q["parede"]]), escala, origem, folga=1)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    reg = V.compor(reg, V.cob([V.ret(*r) for r in q["parede"]], jan, escala, origem), (53, 53, 53))
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    img = soleira(img, escala, origem, q["soleiras"])
    img = folhas(img, escala, origem, q["folhas"])
    return img


# ----------------------------------------------------------------------------------------------------------------------
# O armário ao lado do lavabo: o contorno nítido no retângulo do PDF (o tom sólido do miolo) e o piso em volta sem as
# manchas.
ARMARIO = dict(ret=(2196.2, 371.2, 2243.9, 610.1),
               zona=[V.ret(2162.0, 371.2, 2196.2, 612.5), V.ret(2196.2, 610.1, 2245.7, 619.5)],
               contorno=0.35, escuro=0.72)


def armario(img, escala, origem, q=ARMARIO):
    img = refazer_piso(img, escala, origem, q["zona"], objetos=[V.ret(*q["ret"])])
    x0, y0, x1, y1 = q["ret"]
    jan = V.janela(img, q["ret"], escala, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    mi = V.cob([V.ret(x0 + 4, y0 + 6, x1 - 4, y1 - 6)], jan, escala, origem) > 0.99
    tom = np.median(reg[mi], axis=0)
    a = V.cob([V.ret(*q["ret"])], jan, escala, origem)
    e = q["contorno"]
    ad = V.cob([V.ret(x0 + e, y0 + e, x1 - e, y1 - e)], jan, escala, origem)
    reg = V.compor(reg, a, tom)
    reg = V.compor(reg, np.clip(a - ad, 0, 1), tom * q["escuro"])
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Peças da biblioteca (PNG com alfa): pousadas no retângulo (px da final), com a sombra curta.
BIB = EP.PROJ / "POE642_CasaA/biblioteca-objetos"
_PNG = {}


def _png(rel, giro=0):
    k = (rel, giro)
    if k not in _PNG:
        P = cv2.imread(str(rel), cv2.IMREAD_UNCHANGED)
        a = P[..., 3]
        ys, xs = np.nonzero(a > 8)
        P = P[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        if giro:
            P = np.rot90(P, giro // 90).copy() if giro in (90, 180, 270) else P
        _PNG[k] = (P[..., :3].astype(np.float32), P[..., 3].astype(np.float32) / 255.0)
    return _PNG[k]


def _gira(rgb, a, graus):
    if not graus:
        return rgb, a
    h, w = a.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), graus, 1.0)
    return (cv2.warpAffine(rgb * a[..., None], M, (w, h), flags=cv2.INTER_LINEAR),
            cv2.warpAffine(a, M, (w, h), flags=cv2.INTER_LINEAR))


def pousar(img, escala, origem, rgb, a, r, sombra=0.25):
    """O PNG (pré-multiplicado ou não) esticado no retângulo r (px da final)."""
    from instalacao_terreo_casad_1711 import _pousar
    x0, y0, x1, y1 = r
    ri = ((x0 - origem[0]) * escala, (y0 - origem[1]) * escala, (x1 - origem[0]) * escala, (y1 - origem[1]) * escala)
    _pousar(img, rgb, a, ri, sombra, escala)
    return img


def contorno(img, escala, origem, r, cor, larg):
    jan = V.janela(img, r, escala, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    a = V.cob([V.ret(*r)], jan, escala, origem)
    ad = V.cob([V.ret(r[0] + larg, r[1] + larg, r[2] - larg, r[3] - larg)], jan, escala, origem)
    reg = V.compor(reg, np.clip(a - ad, 0, 1), cor)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def pintar_rets(img, escala, origem, rets, cor):
    jan = V.janela(img, _bbox([V.ret(*r) for r in rets]), escala, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    reg = V.compor(reg, V.cob([V.ret(*r) for r in rets], jan, escala, origem), cor)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


def copiar(img, escala, origem, r, d):
    """O retângulo r (px da final) recebe a imagem deslocada d (px da final)."""
    X0, Y0, X1, Y1 = V.janela(img, r, escala, origem, folga=0)
    dx, dy = int(round(d[0] * escala)), int(round(d[1] * escala))
    img[Y0:Y1, X0:X1] = img[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx]
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Geladeiras e máquinas de lavar da biblioteca: a geladeira inox G2 (a das cozinhas das Casas B, D e E) nos 4 módulos
# do PDF, a frente para a cozinha, com o contorno fino do corpo; a lavadora de tampa superior nos 2 vãos do PDF, o
# painel contra a parede.
ELETROS = dict(
    geladeiras=[(1769.8, 1392.3, 1817.5, 1442.0), (1820.0, 1392.3, 1867.8, 1442.0),
                (1888.7, 1392.3, 1936.4, 1442.0), (1936.4, 1392.3, 1984.2, 1442.0)],
    lavadoras=[(1829.0, 1454.9, 1870.8, 1496.7), (1876.7, 1454.9, 1918.5, 1496.7)],
    limpa=[((1768.0, 1388.0, 1869.8, 1392.3), (0.0, -4.5)), ((1886.8, 1388.0, 1986.0, 1392.3), (0.0, -4.5)),
           ((1827.0, 1496.7, 1920.5, 1500.8), (0.0, 4.6)), ((1827.0, 1452.6, 1829.0, 1496.7), (-2.4, 0.0)),
           ((1918.5, 1452.6, 1921.0, 1496.7), (2.6, 0.0))],
    vaos=[(1817.5, 1392.3, 1820.0, 1442.0), (1870.8, 1454.9, 1876.7, 1496.7)],
    vao_cor=(70, 72, 76), contorno=(78, 80, 84), contorno_larg=0.35,
    png_gel=BIB / "02-terreo/cozinha/geladeira-inox.png",
    png_lav=EP.PROJ / "POE642_CasaD/biblioteca-objetos/02-terreo/area-de-servico/lavadora-tampa-superior.png")


def eletros(img, escala, origem, q=ELETROS):
    for r, d in q["limpa"]:
        img = copiar(img, escala, origem, r, d)
    img = pintar_rets(img, escala, origem, q["vaos"], q["vao_cor"])
    rgb, a = _png(q["png_gel"], 180)
    for r in q["geladeiras"]:
        img = pousar(img, escala, origem, rgb, a, r, 0.28)
        x0, y0, x1, y1 = r
        img = contorno(img, escala, origem, (x0, y0 + (y1 - y0) * 0.095, x1, y1), q["contorno"], q["contorno_larg"])
    rgb, a = _png(q["png_lav"])
    for r in q["lavadoras"]:
        img = pousar(img, escala, origem, rgb, a, r, 0.28)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Plantas: a palmeira-ráfis da biblioteca no lugar das plantas borradas (2 na varanda, 1 na sala de estar, 1 no jantar),
# cobrindo a mancha antiga; em volta, o piso refeito (os restos claros e a sombra velha), sem tocar no sofá, no vidro e
# nas paredes.
PLANTAS = dict(
    png=BIB / "02-terreo/paisagismo/palmeira-rafis.png",
    pecas=[(1819.5, 381.0, 25.5, 15), (1843.6, 410.6, 15.5, 200), (1905.5, 397.5, 20.0, 110),
           (1905.2, 1079.0, 19.5, 300)],      # (cx, cy, raio, giro)
    anel=4.5, sombra=0.30,
    # os cantos refeitos inteiros (o piso em volta das plantas, sem o sofá, o vidro e as paredes)
    zonas=[[(1789.0, 351.5), (1870.2, 351.5), (1870.2, 446.0), (1807.0, 446.0), (1799.0, 420.0), (1794.0, 400.0),
            (1791.0, 385.0), (1789.0, 372.0)],
           [(1875.6, 372.0), (1940.0, 372.0), (1940.0, 405.0), (1918.0, 412.0), (1905.0, 425.0), (1896.0, 440.0),
            (1875.6, 440.0)]])


def _protege_cor(reg):
    """O que não é piso nem mancha no entorno de uma planta: madeira e tecidos (saturados), o creme claro das almofadas,
    o vidro azulado e o escuro (paredes, pés)."""
    hsv = cv2.cvtColor(np.clip(reg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.int16)
    lab = cv2.cvtColor(np.clip(reg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.int16)
    verde = (hsv[..., 0] >= 28) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 30)
    madeira = (hsv[..., 1] > 70) & ~verde
    claro = lab[..., 0] > 236
    azul = lab[..., 2] < 130
    escuro = lab[..., 0] < 110
    m = (madeira | claro | azul | escuro).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0


def plantas(img, escala, origem, q=PLANTAS):
    for z in q["zonas"]:
        img = refazer_piso(img, escala, origem, [z], luz_sig=12.0, pena=3.0)
    for cx, cy, r, g in q["pecas"]:
        if cy > 1000:                               # a do jantar: só o anel em volta
            zona = [_circulo(cx, cy, r + q["anel"], 64)]
            img = refazer_piso(img, escala, origem, zona, ref_luz=[_circulo(cx, cy, r + q["anel"] + 8, 64)],
                               luz_sig=10.0, pena=3.0)
        rgb, a = _png(q["png"])
        rgb, a = _gira(rgb, a, g)
        img = pousar(img, escala, origem, rgb, a, (cx - r, cy - r, cx + r, cy + r), q["sombra"])
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Bancada da área gourmet num tom só, de fora a fora ("mantenha o mesmo tom para a bancada, fora a fora"): o U do PDF
# em granito marrom desenhado (o tom mediano de hoje, o mosqueado leve e os pontinhos claros e escuros, sorteados em
# coordenadas da final: a mesma pedra na final e nos 12K), sem as emendas e as peças em outro tom; o cooktop, a grelha,
# a cuba e a torneira ficam; o contorno fino. As banquetas ("precisam estar sob a bancada e não sobre"): a bancada e a
# borda dela passam por cima, com a sombra do tampo na banqueta.
GOURMET = dict(
    u=[(1476.7, 1269.9), (1766.3, 1269.9), (1766.3, 1329.6), (1512.5, 1329.6), (1512.5, 1401.2), (1766.3, 1401.2),
       (1766.3, 1443.0), (1476.7, 1443.0)],
    pecas=[(1614.6, 1296.9, 1661.4, 1327.9), (1521.4, 1401.4, 1582.6, 1436.6), (1699.4, 1408.6, 1744.4, 1435.6),
           (1717.8, 1424.4, 1725.0, 1440.2)],
    tom_amostra=(1530.0, 1272.0, 1600.0, 1296.0),
    pontos=0.035, claro=(206, 214, 222), escuro=(38, 44, 52), mosqueado=0.05,
    contorno=(40, 46, 56), contorno_larg=0.28,
    banquetas=(1470.0, 1255.0, 1700.0, 1269.9), sombra_banq=0.32)


def gourmet(img, escala, origem, q=GOURMET):
    jan = V.janela(img, _bbox([q["u"]]), escala, origem, folga=3)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    tx0, ty0, tx1, ty1 = V.janela(img, q["tom_amostra"], escala, origem, folga=0)
    am = img[ty0:ty1, tx0:tx1].reshape(-1, 3).astype(np.float32)
    Lm = am.mean(1)
    tom = np.median(am[np.abs(Lm - np.median(Lm)) < 10], axis=0)
    xs, ys = V.coords(jan, escala, origem)
    # o mosqueado: ruído em coordenadas da final (o mesmo desenho em qualquer escala)
    rng = np.random.default_rng(1911)
    bx0, by0, bx1, by1 = [int(v) for v in _bbox([q["u"]])]
    G = rng.normal(0, 1, (by1 - by0 + 4, bx1 - bx0 + 4)).astype(np.float32)
    G = cv2.GaussianBlur(G, (0, 0), 2.0)
    G /= max(float(G.std()), 1e-3)
    mapa = cv2.resize(G, None, fx=1, fy=1)
    M = np.float32([[1.0 / escala, 0, (X0 + 0.5) / escala + origem[0] - bx0 + 2 - 0.5 / escala],
                    [0, 1.0 / escala, (Y0 + 0.5) / escala + origem[1] - by0 + 2 - 0.5 / escala]])
    mosq = cv2.warpAffine(mapa, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    pedra = tom[None, None, :] * (1 + q["mosqueado"] * mosq)[..., None]
    # os pontinhos (claros e escuros), sorteados na área do U em px da final
    area = (bx1 - bx0) * (by1 - by0)
    n = int(area * q["pontos"])
    px = rng.uniform(bx0, bx1, n)
    py = rng.uniform(by0, by1, n)
    pr = rng.uniform(0.18, 0.45, n)
    pc = rng.random(n) < 0.8
    ss = 4
    can_c = np.zeros((H * ss, W * ss), np.uint8)
    can_e = np.zeros((H * ss, W * ss), np.uint8)
    for x, y, r, c in zip(px, py, pr, pc):
        u = int(round(((x - origem[0]) * escala - X0) * ss))
        v = int(round(((y - origem[1]) * escala - Y0) * ss))
        rr = max(1, int(round(r * escala * ss)))
        if -rr <= u < W * ss + rr and -rr <= v < H * ss + rr:
            cv2.circle(can_c if c else can_e, (u, v), rr, 255, -1, lineType=cv2.LINE_AA)
    ac = cv2.resize(can_c.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    ae = cv2.resize(can_e.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    pedra = V.compor(pedra, ac * 0.85, q["claro"])
    pedra = V.compor(pedra, ae * 0.8, q["escuro"])
    a = V.cob([q["u"]], jan, escala, origem)
    ap = V.cob([V.ret(*r) for r in q["pecas"]], jan, escala, origem)
    banq = reg.copy()
    out = V.compor(reg, a * (1 - ap), pedra)
    # o contorno do U (por dentro)
    u = q["u"]
    ak = np.zeros((H, W), np.float32)
    for p0, p1 in zip(u, u[1:] + u[:1]):
        ak = np.maximum(ak, V.cob([V.seg(p0, p1, q["contorno_larg"] * 2)], jan, escala, origem))
    out = V.compor(out, ak * a * (1 - ap), q["contorno"])
    # as banquetas: a sombra do tampo na parte de fora, junto à borda de cima
    bj = V.janela(img, q["banquetas"], escala, origem, folga=0)
    yb = (np.arange(bj[1], bj[3]) + 0.5) / escala + origem[1]
    d = np.clip(q["banquetas"][3] - yb, 0, None)
    som = q["sombra_banq"] * np.exp(-d / 1.6)
    by_0, by_1 = bj[1] - Y0, bj[3] - Y0
    bx_0, bx_1 = max(bj[0] - X0, 0), min(bj[2] - X0, W)
    if by_0 < 0:
        som = som[-by_0:]
        by_0 = 0
    seg_ = out[by_0:by_1, bx_0:bx_1]
    Lb = seg_.mean(2)
    cadeira = (seg_[..., 2] - seg_[..., 0] > 25) | (Lb < 150)          # a madeira e a palha (não o piso claro)
    f = 1 - som[:seg_.shape[0], None] * cadeira
    out[by_0:by_1, bx_0:bx_1] = seg_ * f[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# Tracejados das projeções (varanda e sala de estar) mais finos ("deixar as linhas mais finas"): os traços cinza de hoje
# afinados pelo meio (a distância à borda), o mesmo desenho e o mesmo passo; o que sai volta ao piso novo.
TRACEJADOS = dict(caixas=[(1505.0, 600.0, 1880.0, 885.0), (1878.0, 600.0, 2160.0, 885.0)],
                  larg=0.55, cor=(118, 118, 118))


def tracejados(img, escala, origem, q=TRACEJADOS):
    for cx in q["caixas"]:
        jan = V.janela(img, cx, escala, origem, folga=0)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1]
        lab = cv2.cvtColor(reg, cv2.COLOR_BGR2LAB).astype(np.int16)
        L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
        cinza = (np.abs(A - 128) < 5) & (np.abs(B - 129) < 7) & (L > 85) & (L < 178)
        n, lb, st, _ = cv2.connectedComponentsWithStats(cinza.astype(np.uint8), 8)
        ok = np.zeros(n, bool)
        e2 = escala * escala
        for i in range(1, n):
            w, h, ar = st[i, 2], st[i, 3], st[i, 4]
            ok[i] = (ar >= 3 * e2) and (ar <= 40 * e2) and (max(w, h) >= 2.5 * escala)
        traco = ok[lb]
        if not traco.any():
            continue
        dist = cv2.distanceTransform(traco.astype(np.uint8), cv2.DIST_L2, 5)
        meia_velha = np.percentile(dist[traco], 95)
        meia_nova = q["larg"] / 2 * escala
        # o alfa novo: o miolo do traço, com a borda suave
        a_novo = np.clip(dist - (meia_velha - meia_nova) + 0.5, 0, 1) * traco
        sai = cv2.dilate(traco.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        # o piso novo por baixo (a luz do piso em volta)
        TT = piso_tt(jan, escala)
        r = reg.astype(np.float32).mean(2) / np.maximum(TT.mean(2), 1)
        livre = ~sai & (L > 185)
        h_, e_ = np.histogram(r[livre], bins=80, range=(0.6, 1.4))
        med = float(e_[np.argmax(np.convolve(h_, np.ones(5) / 5, mode="same"))] + 0.005)
        okp = livre & (np.abs(r - med) < 0.1)
        sig = 6 * escala
        luz = cv2.GaussianBlur(np.where(okp, r, 0).astype(np.float32), (0, 0), sig) / np.maximum(
            cv2.GaussianBlur(okp.astype(np.float32), (0, 0), sig), 1e-3)
        piso = TT * luz[..., None]
        out = reg.astype(np.float32)
        out[sai] = piso[sai]
        out = V.compor(out, a_novo, q["cor"])
        img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# O filete entre o Bege Bahia e o travertino ("mantenha essa linha ... até o final. faz o L também aqui"): a divisa do
# PDF (x 1512,5 de 350,3 a 1207,2; y 1207,2 de 1219,9 a 1512,5; x 1219,9 de 1207,2 a 1643,0) num filete fino e
# contínuo, escurecendo o piso (as sombras ficam), só onde é piso; o filete antigo (parcial) sai antes (cada lado recebe
# o próprio piso de 2,5 px mais longe).
FILETE = dict(linhas=[((1512.5, 350.3), (1512.5, 1207.2)), ((1219.9, 1207.2), (1512.5, 1207.2)),
                      ((1219.9, 1207.2), (1219.9, 1643.0))],
              larg=1.0, forca=0.20, desloca=2.6, faixa=1.8)


def filete(img, escala, origem, q=FILETE):
    for (x0, y0), (x1, y1) in q["linhas"]:
        vert = abs(x1 - x0) < 0.01
        f, dsl = q["faixa"], q["desloca"]
        lados = ([((x0 - f, y0, x0, y1), (-dsl, 0.0)), ((x0, y0, x0 + f, y1), (dsl, 0.0))] if vert else
                 [((x0, y0 - f, x1, y0), (0.0, -dsl)), ((x0, y0, x1, y0 + f), (0.0, dsl))])
        for r, d in lados:
            X0, Y0, X1, Y1 = V.janela(img, r, escala, origem, folga=0)
            dx, dy = int(round(d[0] * escala)), int(round(d[1] * escala))
            dest = img[Y0:Y1, X0:X1]
            src = img[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx]
            ok = (dest.mean(2) > 140) & (src.mean(2) > 140)
            dest[ok] = src[ok]
        box = (min(x0, x1) - 2, min(y0, y1) - 2, max(x0, x1) + 2, max(y0, y1) + 2)
        jan = V.janela(img, box, escala, origem, folga=1)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1].astype(np.float32)
        a = V.cob([V.seg((x0, y0), (x1, y1), q["larg"])], jan, escala, origem)
        piso = (reg.mean(2) > 140).astype(np.float32)
        reg *= (1 - q["forca"] * a * piso)[..., None]
        img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# A escada que desce para o Subsolo ("criou um piso na junta entre a madeira e o degrau. ... melhore a transparência
# para que consigamos ver o piso travertino mais opaco"): os 10 degraus do PDF (de 903,5, colado no deck, a 1082,6,
# passo 17,9) no travertino novo (o veio ao comprido do degrau), a parte depois da diagonal a 80% (o resto, o tom
# liso), o bocel fino com a sombra curta no degrau de baixo, a diagonal fina, o contorno claro na grama; a seta e o D
# voltam por cima.
DESCE = dict(
    caixa=(900.0, 1054.0, 1088.0, 1134.0),
    pe=(903.5, 1057.9, 1082.6, 1129.5),
    xs=[903.5, 921.4, 939.3, 957.2, 975.1, 993.0, 1010.9, 1028.9, 1046.8, 1064.7, 1082.6],
    diagonal=[(920.6, 1057.9), (954.6, 1129.5)],
    veu=0.80, escurecer=0.97,
    bocel=dict(larg=0.26, escuro=0.28, sombra=0.10, sombra_px=1.3, luz=0.05),
    corte=(88, 88, 88), corte_larg=0.28,
    contorno=[((903.5, 1129.5), (1082.6, 1129.5)), ((1082.6, 1057.9), (1082.6, 1129.5))],
    contorno_cor=(203, 202, 197), contorno_larg=0.7,
    junta=((903.5, 1057.9), (903.5, 1129.5)), junta_cor=(96, 92, 88))


def desce(img, escala, origem, q=DESCE):
    jan = V.janela(img, q["caixa"], escala, origem)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, escala, origem)
    pe = V.cob([V.ret(*q["pe"])], jan, escala, origem)
    x0, y0, x1, y1 = q["pe"]
    (dx0, dy0), (dx1, dy1) = q["diagonal"]
    a_cheia = V.cob([[(x0, y0), (dx0, y0), (dx1, y1), (x0, y1)]], jan, escala, origem) * pe
    a_trans = np.clip(pe - a_cheia, 0, 1)
    # as letras (a seta e o D) do 1º degrau
    L = reg.mean(2)
    zona = (a_cheia > 0.5)
    med = float(np.median(L[zona]))
    at, cor_t = V.letras(reg, zona, escala=escala, ref=med, dif=90.0, piso_dif=35.0)
    # os degraus: o travertino novo, o veio ao comprido, um deslocamento por degrau
    TT = piso_tt(jan, escala, giro=True)
    lado = TT.shape[0]
    T2 = tex_piso(escala, giro=True)
    p = T2.shape[0]
    rng = np.random.default_rng(1129)
    D = np.zeros_like(reg)
    jj = np.arange(X0, X1)
    ii = np.arange(Y0, Y1)
    for a_, b_ in zip(q["xs"][:-1], q["xs"][1:]):
        a = V.cob([V.ret(a_, y0, b_, y1)], jan, escala, origem)
        dx, dy = rng.integers(0, p, 2)
        D += T2[np.mod(ii + dy, p)[:, None], np.mod(jj + dx, p)[None, :]] * a[..., None]
    D *= q["escurecer"]
    b = q["bocel"]
    fator = np.ones((H, W), np.float32)
    lin = ((ys >= y0) & (ys <= y1))[:, None]
    for xl in q["xs"][1:-1]:
        d = xs - xl                                  # o degrau de baixo fica à direita (desce para a direita)
        som = np.where(d > 0, np.exp(-d / b["sombra_px"]), 0.0) * b["sombra"]
        luz = np.where((d < 0) & (d > -0.6), b["luz"], 0.0)
        fator *= np.where(lin, (1 - som + luz)[None, :], 1.0).astype(np.float32)
        a_l = V.cob([V.ret(xl - b["larg"] / 2, y0, xl + b["larg"] / 2, y1)], jan, escala, origem)
        fator *= (1 - b["escuro"] * a_l)
    D = D * fator[..., None]
    liso = np.median(D[pe > 0.99], axis=0)
    trans = q["veu"] * D + (1 - q["veu"]) * liso
    out = reg * (1 - pe[..., None]) + D * a_cheia[..., None] + trans * a_trans[..., None]
    # a junta com o deck, a diagonal, o contorno na grama
    out = V.compor(out, V.cob([V.seg(*q["junta"], 0.3)], jan, escala, origem), q["junta_cor"])
    out = V.compor(out, V.cob([V.seg(*q["diagonal"], q["corte_larg"])], jan, escala, origem) * 0.85, q["corte"])
    ak = np.zeros((H, W), np.float32)
    for p0, p1 in q["contorno"]:
        ak = np.maximum(ak, V.cob([V.seg(p0, p1, q["contorno_larg"] * 2)], jan, escala, origem))
    out = V.compor(out, ak * (1 - pe), q["contorno_cor"])
    out = V.compor(out, at, cor_t)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


ITENS = {"escada": ESCADA["caixa"],
         "soleiras_servico": (1540.0, 1625.0, 1915.0, 1650.0),
         "lavabo": (2250.0, 340.0, 2350.0, 530.0),
         "escritorio": (2340.0, 335.0, 2610.0, 610.0),
         "armario": (2155.0, 360.0, 2255.0, 625.0),
         "eletros": (1760.0, 1380.0, 1995.0, 1505.0),
         "plantas": (1785.0, 350.0, 1935.0, 435.0),
         "gourmet": (1470.0, 1255.0, 1772.0, 1447.0),
         "tracejados": (1505.0, 600.0, 2160.0, 885.0),
         "filete": (1215.0, 345.0, 1520.0, 1650.0),
         "desce": (895.0, 1045.0, 1092.0, 1138.0)}
FUNC = {"escada": escada, "soleiras_servico": soleiras_servico, "lavabo": lavabo, "escritorio": escritorio,
        "armario": armario, "eletros": eletros, "plantas": plantas, "gourmet": gourmet, "tracejados": tracejados,
        "filete": filete, "desce": desce}


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in nomes:
            im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            x0, y0, x1, y1 = ITENS[nome]
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

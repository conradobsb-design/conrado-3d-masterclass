"""O DCE e o WC DCE 1 do Térreo da Casa E refeitos (18/11, usuário: "VAMOS CORRIGIR A REPRESENTAÇÃO DESSES AMBIENTES:
1. O ENTORNO DA CAMA PRECISA SER PERFEITO, SEM ERROS, SEM BORRÕES. 2. O CONTORNO DO ARMÁRIO DE CABIDES PRECISA ESTAR
COMPLETO. 3. AS JANELAS BEM DESENHADAS 4. ATRÁS DA PORTA DO WC DCE TEM UM ERRO NA PAREDE QUE PRECISA SER CORRIGIDO. 5. O
PISO DEVE SEGUIR A REFERENCIA DOS BANHOS DA CASA D E REFEITO AQUI. OLHE O ENTORNO DO VASO. OLHE COMO FICOU MAL FEITO.
6. CORRIJA A FOLHA DO BOX E O CHUVEIRO."), na final e direto nos 12K A e B. Tudo pela geometria do PDF.

DCE:
- `cama`: o retângulo da cama do PDF (o quadro bege velho e o borrão em volta) volta ao granito marrom do DCE (um trecho
  limpo dele, espelhado) e a cama de solteiro da biblioteca (`quarto-dce-1/cama-solteiro-e`) entra inteira nele, a
  cabeceira na parede da direita, com a sombra curta;
- `armario`: o contorno do guarda-roupa de cabides fechado nos quatro lados, no tom do friso de cima;
- `janela`: o vão redesenhado (o peitoril, as faces) e as peças de esquadria do PDF: marcos e montantes em grafite, as
  duas folhas de correr em vidro claro com a linha do meio.

WC DCE 1:
- `piso`: o piso inteiro no cinza claro dos banhos da Casa D (o tom do WC DCE de lá, com a nuvem suave e o grão fino),
  de parede a parede, com a sombra curta rente às paredes; a bancada marrom tabaco e a cuba ficam; o rótulo volta por
  cima (o desenho das letras tirado do de antes);
- `parede`: atrás da folha da porta, a parede de baixo refeita lisa (o PDF tem a parede de 2395,8 a 2448,4);
- `box`: a faixa do box no vidro claro com os fios, e as duas folhas de correr do PDF, com os perfis nas pontas;
- `chuveiro`: o quadrado da biblioteca no quadrado do PDF, com o braço cromado até a parede da direita e a canopla;
- `bacia`: a bacia Monte Carlo da biblioteca no retângulo do PDF, a caixa contra a parede da direita;
- `porta`: a folha da porta (aberta junto à parede de baixo) na madeira das portas da Casa D, com o fio e a sombra;
- `janela`: como a do DCE.

  python3 dce_wcdce_terreo_casae_1811.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 dce_wcdce_terreo_casae_1811.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import biblioteca_terreo_casaa_1211 as BT                   # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
import danae_foto as DF                                     # noqa: E402
import janela_pia_casaa_1611 as JP                          # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402
from pedidos_terreo_casaa_2910 import JANELAS_TA            # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
BIB = RAIZ / "POE642_CasaE/biblioteca-objetos/02-terreo"

# px da final (PDF: ARQ_LAYOUT HUMANIZAÇÃO, ARQ_LOUÇAS E METAIS, ARQ_BANCADAS, ARQ_PAREDE)
DCE = {"caixa": (2220, 478, 2400, 645), "piso": (2225.6, 494.9, 2386.9, 629.2),
       "rotulo": (2292.0, 582.0, 2360.0, 618.0),
       "cama": {"png": BIB / "quarto-dce-1/cama-solteiro-e.png", "ret": (2263.9, 494.9, 2386.9, 552.2),
                "limpa": (2257.0, 494.9, 2386.9, 559.0)},
       "granito": (2270.0, 555.0, 2358.0, 587.0),
       "armario": {"ret": (2225.6, 563.6, 2257.0, 629.0), "cor": (115, 161, 198), "px": 0.8}}
JANELAS = {
    "DCE": {"caixa": (2230, 470, 2345, 510), "vao": (2245.6, 485.9, 2329.1, 494.9),
            "folhas": [(2248.5, 491.9, 2288.8, 494.9), (2285.9, 488.9, 2326.2, 491.9)],
            "marcos": [(2245.6, 488.9, 2248.5, 494.9), (2326.2, 488.9, 2329.1, 494.9)],
            "montantes": [(2248.5, 491.9, 2251.5, 494.9), (2285.9, 491.9, 2288.8, 494.9),
                          (2285.9, 488.9, 2288.8, 491.9), (2323.2, 488.9, 2326.2, 491.9)],
            "vidros": [(2251.5, 491.9, 2285.9, 494.9), (2288.8, 488.9, 2323.2, 491.9)]},
    "WC DCE 1": {"caixa": (2390, 470, 2485, 510), "vao": (2404.8, 485.9, 2467.5, 494.9),
                 "folhas": [(2407.2, 485.9, 2438.5, 488.9), (2433.7, 488.9, 2465.1, 491.9),
                            (2429.5, 491.9, 2447.5, 494.9)],
                 "marcos": [(2404.8, 485.9, 2407.2, 494.9), (2465.1, 485.9, 2467.5, 494.9)],
                 "montantes": [(2407.2, 485.9, 2411.9, 488.9), (2433.7, 485.9, 2438.5, 488.9),
                               (2433.7, 488.9, 2438.5, 491.9), (2460.3, 488.9, 2465.1, 491.9)],
                 "vidros": [(2411.9, 485.9, 2433.7, 488.9), (2438.5, 488.9, 2460.3, 491.9),
                            (2429.5, 491.9, 2447.5, 494.9)]}}
ESQ = {"grafite": (58, 60, 64), "fio": (34, 35, 38), "fio_px": 0.35, "vidro": (226, 229, 232),
       "vidro_fio": (120, 123, 128), "vidro_fio_px": 0.3, "meio": (150, 153, 158), "meio_px": 0.3}
WC = {"caixa": (2380, 478, 2492, 645),
      "piso": (2395.8, 494.9, 2476.4, 629.2), "bancada": (2446.2, 590.9, 2476.4, 629.2),
      "rotulo": (2396.5, 583.0, 2446.0, 613.0),
      "tom": (210.8, 214.2, 220.0), "nuvem": (0.007, 2.0), "grao": (0.005, 0.6), "ao": (0.07, 2.0),
      "parede": (2395.8, 629.2, 2448.4, 636.4), "parede_cor": (80, 80, 80),
      "box": {"faixa": (2395.8, 541.1, 2476.4, 544.1), "vidro": (214, 219, 223), "vidro_a": 0.8,
              "fio": (150, 155, 160), "fio_px": 0.3,
              "folhas": [(2395.9, 541.9, 2438.2, 542.5), (2406.8, 542.8, 2449.2, 543.4)],
              "folha_cor": (150, 156, 162), "perfil": (112, 117, 122), "perfil_px": 1.0},
      "chuveiro": {"png": BIB / "banho-gourmet/chuveiro-quadrado.png", "cabeca": (2448.0, 513.7, 2459.8, 525.5),
                   "braco": (2459.0, 518.8, 2476.2, 520.3), "canopla": (2475.2, 517.6, 2476.4, 521.6),
                   "cromo": (206, 208, 211), "brilho": (238, 239, 241), "borda": (118, 121, 126),
                   "sombra": [{"dx": 0.006, "dy": 0.008, "sig": 0.01, "forca": 0.22}]},
      "bacia": {"png": BIB / "banho-dce-1/bacia-monte-carlo-sem-valvula.png", "ret": (2445.8, 559.6, 2476.4, 580.7),
                "sombra": [{"dx": -0.012, "dy": 0.012, "sig": 0.015, "forca": 0.22}]},
      "porta": {"folha": (2393.7, 622.8, 2438.1, 625.2), "madeira": (134, 166, 202), "contorno": (58, 72, 92),
                "contorno_px": 0.45, "sombra": (0.28, -0.8, 1.0, 0.9)}}


def _png(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def _cx(m, x):
    return m.x(x) - 0.5


def _cy(m, y):
    return m.y(y) - 0.5


def _janela(out, m, q, c=ESQ):
    jq = {"vao": q["vao"], "folhas": q["folhas"], "fora": (q["vao"][0], q["vao"][1], q["vao"][0], q["vao"][1]),
          "fora_dx": 0.0}
    out[...] = JP.desenhar(out, m.s, m.t, jq, JANELAS_TA)
    pecas = []
    for r in q["vidros"]:
        x0, y0, x1, y1 = r
        ym = (y0 + y1) / 2
        pecas += [(r, "ret", c["vidro"], 0), (r, "contorno", c["vidro_fio"], c["vidro_fio_px"]),
                  ((x0, ym - c["meio_px"] / 2, x1, ym + c["meio_px"] / 2), "ret", c["meio"], 0)]
    for r in q["marcos"] + q["montantes"]:
        pecas += [(r, "ret", c["grafite"], 0), (r, "contorno", c["fio"], c["fio_px"])]
    CB.pintar(out, m, pecas)


def _tile(patch, h, w):
    """O trecho repetido em espelho até h x w."""
    t = patch
    while t.shape[0] < h:
        t = np.concatenate([t, t[::-1]], axis=0)
    while t.shape[1] < w:
        t = np.concatenate([t, t[:, ::-1]], axis=1)
    return t[:h, :w]


# ----------------------------------------------------------------------------------------------------------------------
def _nc(img, w, sig):
    num = cv2.GaussianBlur(img * (w[..., None] if img.ndim == 3 else w), (0, 0), sig)
    den = cv2.GaussianBlur(w, (0, 0), sig)
    d = np.maximum(den, 1e-4)
    return num / (d[..., None] if img.ndim == 3 else d), den


def piso_dce(out, m, q=DCE):
    """O granito do DCE num tom só: o texto do rótulo sai (inpaint), o tom de fundo (o desfocado só do piso) dá lugar
    ao tom da mediana, o grão fica; junto às paredes e às peças (menos a cama, que é refeita) a sombra curta fica."""
    s = m.s
    X0, Y0, X1, Y1 = m.reti(q["piso"])
    sub = np.ascontiguousarray(out[Y0:Y1, X0:X1])
    forma = sub.shape[:2]

    def ret(r, f=0.0):
        rr = m.ret(r)
        return alfa_ret((rr[0] - X0 - f, rr[1] - Y0 - f, rr[2] - X0 + f, rr[3] - Y0 + f), forma) > 0.5
    # o texto (claro) do rótulo sai
    rot = ret(q["rotulo"])
    L = sub.astype(np.float32).mean(axis=2)
    txt = (rot & (L > np.median(L[rot]) + 18)).astype(np.uint8)
    k = max(1, int(round(1.2 * s)))
    txt = cv2.dilate(txt, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
    sub = cv2.inpaint(sub, txt * 255, max(3, int(round(4 * s))), cv2.INPAINT_TELEA)
    f = sub.astype(np.float32)
    L = f.mean(axis=2)
    rb = f[..., 2] - f[..., 0]
    cama = ret(q["cama"]["limpa"], 7 * s)
    F = (np.abs(L - 110) < 26) & (np.abs(rb - 48) < 16)
    n, lab, st, _ = cv2.connectedComponentsWithStats(F.astype(np.uint8), 4)
    grande = np.zeros(n, bool)
    grande[1:] = st[1:, cv2.CC_STAT_AREA] >= 400 * s * s
    F = grande[lab]
    Fs = (F & ~cama).astype(np.float32)
    tom = np.median(f[Fs > 0].reshape(-1, 3), axis=0)
    fundo, _ = _nc(f, Fs, 5 * s)
    obj = (~F & ~cama).astype(np.uint8)
    d = cv2.distanceTransform(1 - obj, cv2.DIST_L2, 5)
    longe = (Fs * (d > 12 * s)).astype(np.float32)
    placa, cob = _nc(f, longe, 18 * s)
    placa = np.where((cob > 0.02)[..., None], placa, tom[None, None])
    sombra = np.minimum(0.0, fundo - placa)
    w_s = np.clip((10 * s - d) / (6 * s), 0, 1)[..., None]
    novo = tom[None, None] + (f - fundo) + w_s * sombra
    a = F.astype(np.float32)[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(f * (1 - a) + novo * a), 0, 255).astype(np.uint8)
    return tom


def dce(out, m, q=DCE):
    s = m.s
    tom = piso_dce(out, m, q)
    # a cama: o retângulo dela no granito limpo do DCE, depois a cama da biblioteca inteira
    gx0, gy0, gx1, gy1 = m.reti(q["granito"])
    patch = out[gy0:gy1, gx0:gx1].copy()
    rm = m.ret(q["cama"]["limpa"])
    X0, Y0, X1, Y1 = int(np.floor(rm[0])), int(np.floor(rm[1])), int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    # a janela com uma folga em volta: o granito novo leva o tom de baixa frequência do piso em volta (o anel de fora),
    # para não ficar o retângulo de emenda
    g = int(np.ceil(8 * s))
    X0, Y0, X1, Y1 = X0 - g, Y0 - g, X1 + g, Y1 + g
    forma = (Y1 - Y0, X1 - X0)
    loc = (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)
    a = alfa_ret(loc, forma)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    # o anel: o granito de fora (não a parede escura nem o que é claro)
    Lr = reg.mean(axis=2)
    anel = ((1 - alfa_ret((loc[0] - 1, loc[1] - 1, loc[2] + 1, loc[3] + 1), forma)) * (Lr > 85) * (Lr < 140)
            ).astype(np.float32)
    sg = 5 * s
    num = cv2.GaussianBlur(reg * anel[..., None], (0, 0), sg)
    den = cv2.GaussianBlur(anel, (0, 0), sg)[..., None]
    baixa = num / np.maximum(den, 1e-4)
    falta = (den[..., 0] < 0.02)
    baixa[falta] = tom
    tl = _tile(patch, *forma).astype(np.float32)
    novo = baixa + (tl - cv2.GaussianBlur(tl, (0, 0), sg))
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)
    x0, y0, x1, y1 = q["cama"]["ret"]
    P = _png(q["cama"]["png"])
    o = out.astype(np.float32)
    # a cabeceira (em cima no png) na parede da direita: girada 90° no sentido horário
    BT.pousar(o, P, _cx(m, (x0 + x1) / 2), _cy(m, (y0 + y1) / 2), (y1 - y0) * s, (x1 - x0) * s, -90.0,
              BT.SOMBRAS["movel"], DF.PX_M * s)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    # o guarda-roupa de cabides: o contorno fechado
    ar = q["armario"]
    CB.pintar(out, m, [(ar["ret"], "contorno", ar["cor"], ar["px"])])
    print("    DCE: a cama da biblioteca no retângulo do PDF sobre o granito limpo; o contorno do armário fechado")


def wc(out, m, q=WC):
    s = m.s
    rp = m.ret(q["piso"])
    X0, Y0, X1, Y1 = int(np.floor(rp[0])) - 1, int(np.floor(rp[1])) - 1, int(np.ceil(rp[2])) + 1, int(np.ceil(rp[3])) + 1
    forma = (Y1 - Y0, X1 - X0)
    antigo = out[Y0:Y1, X0:X1].astype(np.float32).copy()

    def loc(r):
        rr = m.ret(r)
        return (rr[0] - X0, rr[1] - Y0, rr[2] - X0, rr[3] - Y0)
    # o piso dos banhos da Casa D: o tom, a nuvem suave e o grão fino
    rng = np.random.default_rng(1811)
    fn, sn = q["nuvem"]
    fg, sg = q["grao"]
    nuvem = cv2.GaussianBlur(rng.normal(0, 1, forma).astype(np.float32), (0, 0), sn * s)
    nuvem /= max(float(nuvem.std()), 1e-6)
    grao = cv2.GaussianBlur(rng.normal(0, 1, forma).astype(np.float32), (0, 0), sg * s)
    grao /= max(float(grao.std()), 1e-6)
    piso = np.float32(q["tom"])[None, None] * (1 + fn * nuvem + fg * grao)[..., None]
    # a sombra curta rente às paredes
    lp = loc(q["piso"])
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
    d = np.minimum.reduce([xx - lp[0], lp[2] - xx, yy - lp[1], lp[3] - yy])
    fa, da = q["ao"]
    piso *= (1 - fa * np.exp(-np.maximum(d, 0) / (da * s)))[..., None]
    a = alfa_ret(lp, forma) * (1 - alfa_ret(loc(q["bancada"]), forma))
    reg = antigo * (1 - a[..., None]) + piso * a[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    # a parede de baixo atrás da porta
    CB.pintar(out, m, [(q["parede"], "ret", q["parede_cor"], 0)])
    # o box: a faixa de vidro e as duas folhas de correr
    b = q["box"]
    fx0, fy0, fx1, fy1 = b["faixa"]
    rf = m.ret(b["faixa"])
    a_b = alfa_ret((rf[0] - X0, rf[1] - Y0, rf[2] - X0, rf[3] - Y0), forma)[..., None] * b["vidro_a"]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a_b) + np.float32(b["vidro"]) * a_b), 0, 255).astype(np.uint8)
    pecas = [((fx0, fy0, fx1, fy0 + b["fio_px"]), "ret", b["fio"], 0),
             ((fx0, fy1 - b["fio_px"], fx1, fy1), "ret", b["fio"], 0)]
    for f in b["folhas"]:
        x0, y0, x1, y1 = f
        pecas += [(f, "ret", b["folha_cor"], 0),
                  ((x0, y0 - 0.3, x0 + b["perfil_px"], y1 + 0.3), "ret", b["perfil"], 0),
                  ((x1 - b["perfil_px"], y0 - 0.3, x1, y1 + 0.3), "ret", b["perfil"], 0)]
    CB.pintar(out, m, pecas)
    # o chuveiro: o braço cromado até a parede, a canopla, a cabeça quadrada por cima
    c = q["chuveiro"]
    x0, y0, x1, y1 = c["braco"]
    e = 0.35
    CB.pintar(out, m, [((x0, y0 - e, x1, y1 + e), "ret", c["borda"], 0), ((x0, y0, x1, y1), "ret", c["cromo"], 0),
                       ((x0, y0 + 0.15, x1, y0 + 0.6), "ret", c["brilho"], 0)])
    cx0, cy0, cx1, cy1 = c["canopla"]
    CB.pintar(out, m, [((cx0 - e, cy0 - e, cx1, cy1 + e), "ret", c["borda"], 0),
                       ((cx0, cy0, cx1, cy1), "ret", c["cromo"], 0)])
    hx0, hy0, hx1, hy1 = c["cabeca"]
    o = out.astype(np.float32)
    BT.pousar(o, _png(c["png"]), _cx(m, (hx0 + hx1) / 2), _cy(m, (hy0 + hy1) / 2), (hx1 - hx0) * s, (hy1 - hy0) * s,
              0.0, c["sombra"], DF.PX_M * s)
    # a bacia: a caixa (em cima no png) contra a parede da direita
    bq = q["bacia"]
    x0, y0, x1, y1 = bq["ret"]
    BT.pousar(o, _png(bq["png"]), _cx(m, (x0 + x1) / 2), _cy(m, (y0 + y1) / 2), (y1 - y0) * s, (x1 - x0) * s, -90.0,
              bq["sombra"], DF.PX_M * s)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    # o fio da cabeça do chuveiro (como os quadrados da Casa D)
    CB.pintar(out, m, [(c["cabeca"], "contorno", c["borda"], 0.4)])
    # a folha da porta, na madeira das portas da Casa D
    p = q["porta"]
    fo, sdx, sdy, ssg = p["sombra"]
    rf = m.ret(p["folha"])
    af = alfa_ret((rf[0] - X0, rf[1] - Y0, rf[2] - X0, rf[3] - Y0), forma)
    M = np.float32([[1, 0, sdx * s], [0, 1, sdy * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(af, M, (forma[1], forma[0])), (0, 0), ssg * s) * (1 - af)
    reg = out[Y0:Y1, X0:X1].astype(np.float32) * (1 - fo * sb)[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    CB.pintar(out, m, [(p["folha"], "ret", p["madeira"], 0), (p["folha"], "contorno", p["contorno"], p["contorno_px"])])
    print("    WC DCE 1: o piso dos banhos da Casa D, a parede atrás da porta, o box, o chuveiro quadrado com o braço, a "
          "bacia e a folha da porta")


def rotulos(out, mp, op=None):
    import pedidos_terreo_casae_1611 as P
    import revisao_terreo_casac_1411 as R14
    import escada_painel_casae_1711 as EP
    import json
    rots = {r[0]: r for r in P.ROTULOS}
    cores = {"DCE": P.CLARO, "WC DCE 1": P.ESCURO}
    caixas = {"DCE": DCE["caixa"], "WC DCE 1": WC["caixa"]}
    if op == "B":
        glob = EP._kalam_global()
        kal = {b["nome"]: b for b in json.loads(EP.KALAM.read_text())}
    for nome in ("DCE", "WC DCE 1"):
        m = mp.local(out, caixas[nome]) if mp.ref is not None else mp
        if op == "B":
            b = kal[nome]
            EP._desenha_kalam(out, m, b["linhas"], tuple(b["cor"]), glob)
            continue
        s = m.s
        WX0, WY0 = m.reti((2280.0, 570.0, 2460.0, 625.0))[:2]
        WX1, WY1 = m.reti((2280.0, 570.0, 2460.0, 625.0))[2:]
        jan = out[WY0:WY1, WX0:WX1].astype(np.float32)
        X0 = (WX0 - m.t[0] - 0.5 + 0.5 * s) / s
        Y0 = (WY0 - m.t[1] - 0.5 + 0.5 * s) / s
        R14.desenhar_linhas(jan, P.linhas_rotulo(rots[nome]), cores[nome], s, X0, Y0)
        out[WY0:WY1, WX0:WX1] = np.clip(np.round(jan), 0, 255).astype(np.uint8)
    print("    rótulos do DCE e do WC DCE 1 redesenhados" + (" (Kalam)" if op == "B" else " (Inter)")
          + "; o do WC no meio do piso livre")


def aplicar(img, mp, op=None):
    out = img.copy()
    m = mp.local(out, WC["caixa"]) if mp.ref is not None else mp
    wc(out, m)
    m = mp.local(out, DCE["caixa"]) if mp.ref is not None else mp
    dce(out, m)
    for nome, q in JANELAS.items():
        m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
        _janela(out, m, q)
        print(f"    janela do {nome}: o vão, os marcos e os montantes em grafite, as folhas em vidro")
    rotulos(out, mp, op)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa()))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, op)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

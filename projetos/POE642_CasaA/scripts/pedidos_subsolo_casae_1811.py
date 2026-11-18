r"""Casa E, Subsolo: os padrões de todas as casas, as notas do cliente (Miro, "Revisão das Plantas 2") e o mobiliário
pela biblioteca da Casa E (18/11/26).

O levantamento aprovado (usuário: "DE ACORDO") está em `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_1811_levantamento.jpg`
e `..._1811_mobiliario.jpg`; a análise de 16/11 em `POE642_CasaE/POE642_CasaE_analise_notas_e_padroes_1611.md`. Como no
Subsolo da Casa D (`biblioteca_subsolo_casad_1511`) e no Térreo da Casa E (`pedidos_terreo_casae_1611`), na mesma escala
(59,7 px/m), um passo por item, na ordem de `PASSOS`:

1. `fundo`: o fundo branco, sem a hachura diagonal e sem o tracejado do lote (Subsolo A, nota 2; margem branca, 16/11);
2. `perimetro` (no fim): o contorno da casa no pátio, no cinza das paredes (nota 1: "Demarcar melhor o perímetro da casa");
3. `bege`: o Bege Bahia do Subsolo da Casa A (a amostra tecida, na escala dela), com a luz do lugar, no pátio, no depósito
   e na casa de máquinas de 5,83 m² (notas 2 e A4: "Diminuir a escala da textura");
4. `escada`: pelo PDF (o render a tinha invertida): os degraus 1 a 7 (à esquerda), deste nível, inteiros, no travertino; os
   de depois da diagonal de corte (8 a 17), transparentes no tom da escada (o véu da Casa D), sem o branco; ▶ e S no 1º
   degrau e "SOBE PARA O / TÉRREO" no pátio, à esquerda (G1, nota 6);
5. `piscina`: a água mais sóbria, como no Térreo (nota 4); a profundidade (nota 5; 18/11, usuário, com a linha verde no
   tanque da direita: "A única parte mais rasa da piscina é essa que eu delimitei [...] O restante é tudo fundo"): só a
   faixa de cima do tanque da direita, junto à sauna, rasa e clara; todo o resto fundo, com a sombra do degrau; a borda entre a piscina e a academia na
   pastilha da piscina (nota 3) e as outras bordas em Bege Bahia lisa, um tom abaixo (16/11);
6. `travertino`: sauna, ducha e vestiário no travertino do Térreo (o da Casa D), liso (nota 8);
7. `marrom`: o DCE e a casa de máquinas de 15,07 m² no piso marrom da amostra do cliente (como no Térreo);
8. `wc_dce2`: o piso cinza-claro, a bancada marrom tabaco, a cuba, a bacia, o box e o chuveiro do WC DCE 1 do Térreo;
9. `dce`: a cama de solteiro da biblioteca, o criado-mudo na cor dos armários, o armário de cabides com fundo (nota 7);
10. `academia`, `sauna`, `ducha`, `vestiario`, `elevador`: as peças da biblioteca (a folha do mobiliário);
11. `portas`: as portas de giro no padrão da Casa D, quina a quina (G3);
12. `rotulos`: o padrão (Inter, um corpo, centrados e alinhados); "AMBIENTE" sai.

Uso (de POE642_CasaA/scripts/):
  python3 pedidos_subsolo_casae_1811.py [--ate <passo>] [--de <passo>] [--cache <pasta>] [--saida <png>]
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

import final3840_casae as FE                    # noqa: E402
import pedidos_terreo_casae_1611 as PE          # noqa: E402

CASA = FE.CASA
R = CASA / "renders"
FINAL = R / "POE642_CasaE_PH_Subsolo_v1_final.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "e730bde"
BIB = CASA / "biblioteca-objetos" / "01-subsolo"
BIBT = CASA / "biblioteca-objetos" / "02-terreo"
PAREDE = (80, 80, 80)
u8, dil = PE.u8, PE.dil


def antes_img():
    """A final do Subsolo do commit de base (lida do git: a final em disco é regravada aqui)."""
    rel = FINAL.relative_to(RAIZ_GIT).as_posix()
    dados = subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"], capture_output=True,
                           check=True).stdout
    return cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR)


def quieto(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


def paredes(Q, lim=0.3):
    if "par" not in _CACHE:
        _CACHE["par"] = FE.paredes_pdf(Q)
    return _CACHE["par"] > lim


_CACHE = {}


def ret_mask(forma, r):
    x0, y0, x1, y1 = r
    m = np.zeros(forma, bool)
    m[int(round(y0)):int(round(y1)), int(round(x0)):int(round(x1))] = True
    return m


def png(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


# ----------------------------------------------------------------------------------------------------------------------
# 0. A base: a final sem os rótulos (eles voltam no fim, no padrão de 16/11)
def base(Q, img):
    limpa, _ = FE.sem_rotulos("Subsolo", img, novos=True)
    return limpa


# ----------------------------------------------------------------------------------------------------------------------
# 1. O fundo branco: a pegada é o que a legenda pinta (fechado, sem furos, as manchas grandes), mais o bloco da piscina
# (as bordas dela são brancas na legenda e encostam no lado de fora); fora dela, branco puro.
FUNDO = {"fechar": 7, "abrir": 3, "area_min": 2000, "suave": 0.8, "dentro_px": [(857, 476, 1000, 912)]}


def pegada(Q, q=FUNDO):
    if "pegada" in _CACHE:
        return _CACHE["pegada"]
    nb = (Q.chapada.min(axis=2) < 250).astype(np.uint8)
    nb = cv2.morphologyEx(nb, cv2.MORPH_OPEN, np.ones((q["abrir"], q["abrir"]), np.uint8))
    nb = cv2.morphologyEx(nb, cv2.MORPH_CLOSE, np.ones((q["fechar"], q["fechar"]), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb, connectivity=8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    for r in q["dentro_px"]:
        m |= ret_mask(m.shape, r)
    m = ndimage.binary_fill_holes(m)
    _CACHE["pegada"] = m
    return m


def fundo(Q, img, q=FUNDO):
    m = pegada(Q, q)
    p = cv2.GaussianBlur(m.astype(np.float32), (0, 0), q["suave"])
    p = np.maximum(p, m.astype(np.float32))[..., None]
    o = img.astype(np.float32) * p + 255 * (1 - p)
    print(f"    fundo branco: {int((~m).sum())} px fora da pegada (sem a hachura e o tracejado do lote)")
    return u8(o)


# ----------------------------------------------------------------------------------------------------------------------
# 2. O perímetro da casa no pátio (nota 1), no fim: o contorno da pegada no cinza das paredes, 2 px (como na Casa D).
PERIMETRO = {"larg": 2.0, "cor": PAREDE, "ss": 8}


def perimetro(Q, img, q=PERIMETRO):
    import pedidos_subsolo_casac_1311 as PS
    m = pegada(Q).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    ss = q["ss"]
    ys, xs = np.nonzero(m)
    X0, Y0, X1, Y1 = xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5
    M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    for c in cs:
        pts = (c.reshape(-1, 2).astype(np.float32) + 0.5 - [X0, Y0]) * ss
        cv2.polylines(M, [np.int32(np.round(pts))], True, 255, max(1, int(round(q["larg"] * ss))), cv2.LINE_AA)
    a = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    out = PS._pintar(img.copy(), a, X0, Y0, q["cor"])
    print("    perímetro: o contorno da casa no pátio, no cinza das paredes")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 3. O Bege Bahia (notas 2 e A4; o da Casa D, aprovado: "o bege bahia deve ficar igual ao das outras casas A, B e C"): na
# chapada 232, fora a escada (refeita no passo `escada`) e o WC DCE 2 (vai ao piso dos banhos), a amostra do Subsolo da
# Casa A tecida sem emenda, vezes a luz larga do lugar; o que está sobre o piso (o que foge do tom dele) fica.
BEGE = {"final": FE.RAIZ / "POE642_CasaA" / "renders" / "POE642_CasaA_PH_Subsolo_final_rotulos.png",
        "amostra": (1120, 1110, 1320, 1310), "luz_sigma": 18.0, "tol": 40,
        "fora_px": [(1855, 486, 1952, 640)]}


def bege(Q, img, q=BEGE):
    import materiais_terreo_casac_1311 as MT
    B = np.all(Q.chapada == 232, axis=2)
    for r in q["fora_px"]:
        B &= ~ret_mask(B.shape, r)
    B &= ~paredes(Q)
    I = img.astype(np.float32)
    med = np.median(I[B], axis=0)
    perto = np.abs(I - med).max(axis=2) < q["tol"]
    B &= perto
    # os arcos das portas (o traço da ARQ_PAREDE, engrossado), onde o Bege Bahia está em volta: "essa planta humanizada
    # não recebe o arco" (Casa D, 16/11)
    arcos = np.zeros(B.shape, np.uint8)
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or not any(it[0] == "c" for it in d.get("items", [])):
            continue
        (a0, b0), (a1, b1) = Q.p2q(d["rect"].x0, d["rect"].y0), Q.p2q(d["rect"].x1, d["rect"].y1)
        if not (14 <= abs(a1 - a0) <= 220 and abs(abs(a1 - a0) - abs(b1 - b0)) < 2):
            continue
        for c in Q.caminhos(d):
            cv2.polylines(arcos, [np.int32(np.round(np.asarray(c) * 8))], False, 1, 5, cv2.LINE_8, shift=3)
    perto_bege = cv2.dilate(B.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    B |= (arcos > 0) & perto_bege & perto & ~paredes(Q)
    ys, xs = np.nonzero(B)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    A = cv2.imread(str(q["final"]))
    a0, b0, a1, b1 = q["amostra"]
    T = MT.sem_emenda(A[b0:b1, a0:a1].astype(np.float32), y1 - y0, x1 - x0)
    L = I[y0:y1, x0:x1].mean(axis=2)
    m = B[y0:y1, x0:x1].astype(np.float32)
    s = q["luz_sigma"]
    luz = cv2.GaussianBlur(L * m, (0, 0), s) / np.maximum(cv2.GaussianBlur(m, (0, 0), s), 1e-4)
    luz = np.clip(luz / max(float(np.median(L[m > 0])), 1.0), 0.8, 1.1)
    novo = T * luz[..., None]
    a = cv2.GaussianBlur(m, (0, 0), 0.6)[..., None] * m[..., None]
    o = I.copy()
    o[y0:y1, x0:x1] = o[y0:y1, x0:x1] * (1 - a) + novo * a
    print(f"    Bege Bahia: o pátio, o depósito e a casa de máquinas no Bege Bahia do Subsolo da Casa A "
          f"({B.sum() / Q.px_m ** 2:.1f} m²), com a luz do lugar")
    return u8(o)


# ----------------------------------------------------------------------------------------------------------------------
# 6. O travertino (nota 8: "Essa textura de travertino está diferente das outras casas"): sauna, ducha e vestiário no
# travertino do Térreo da Casa E (o Romano levigado da Casa D, `pedidos_terreo_casae_1611.travertino`), fora a escada.
TRAVERTINO = dict(PE.TRAVERTINO, fora_px=[(1150, 410, 1457, 484)])


def travertino(Q, img, q=TRAVERTINO):
    import final3840_casaa_terreo as T
    ch = T.F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), 5) & ~paredes(Q)
    for r in q["fora_px"]:
        ch &= ~ret_mask(ch.shape, r)
    return PE.trocar_piso(Q, img, ch, PE.textura_travertino(Q, Q.H, Q.W, q), q, "travertino do Térreo (sauna, ducha, "
                          "vestiário)")


# ----------------------------------------------------------------------------------------------------------------------
# 7. O piso marrom (como no Térreo: a amostra do cliente, sem as pintas do granito): o DCE e a casa de máquinas de 15,07 m².
MARROM = dict(PE.MARROM, extra_px=[])


def marrom(Q, img, q=MARROM):
    return PE.marrom(Q, img, q)


# 6b. O travertino num tom só, sem as juntas e sem os pontinhos (como o do Térreo, `travertino_terreo_casae_1711`, 17/11:
# "as manchas cinzas, remova as juntas também"): as áreas da sauna, da ducha e do vestiário; a bancada e os bancos ficam.
TRAV_LIMPO = {"caixa": (1050, 755, 1495, 915), "areas": [(1060, 760, 1492, 912)],
              "fica": [(1060, 832, 1184, 912), (1452, 762, 1490, 844)]}


def travertino_limpo(Q, img, q=TRAV_LIMPO):
    import travertino_terreo_casae_1711 as TV
    from correcoes_terreo_casab_1611 import Mapa
    guarda = (TV.CAIXA, TV.AREAS, TV.FICA, TV.PECAS)
    TV.CAIXA, TV.AREAS, TV.FICA, TV.PECAS = q["caixa"], q["areas"], q["fica"], []
    try:
        return TV.aplicar(img, Mapa())
    finally:
        TV.CAIXA, TV.AREAS, TV.FICA, TV.PECAS = guarda


# ----------------------------------------------------------------------------------------------------------------------
# 4. A escada pelo PDF (ARQ_ESCADAS E RAMPAS): 17 degraus de 17,92 px (0,30 m) de x 1150,9 a 1455,5, entre y 411,3 e
# 482,9; o S do PDF no 1º degrau (à esquerda) e a linha de corte em diagonal de (1258,1; 411,3) a (1294,2; 482,9): à
# esquerda dela, os degraus deste nível (1 a 7), inteiros; à direita, os tracejados (8 a 17), acima do corte. O render a
# tinha invertida (o branco nos degraus de baixo, o S no fim). Agora: todos os degraus no travertino do Térreo, um tom
# abaixo do piso (o fio de cada espelho, a sombra curta do espelho no degrau de baixo, o nariz claro), e os de depois da
# diagonal sob o véu claro da Casa D ("manter divisória da escada em diagonal, sem linha, e dali para cima os degraus em
# transparência"); ▶ e S no 1º degrau; a descrição "SOBE PARA O / TÉRREO" vai com os rótulos.
ESCADA = {"x0": 1150.9, "passo": 17.917, "n": 17, "y0": 411.3, "y1": 482.95,
          "corte": ((1258.1, 411.3), (1294.2, 482.9)), "tom": 0.88, "veu": 0.38, "veu_cor": (236, 236, 236),
          "rampa_px": 1.5, "linha": 0.66, "linha_px": 0.8, "sombra": (0.16, 3.2), "nariz": (1.04, 1.2),
          "borda": 0.80, "borda_px": 0.8, "ss": 4,
          "tri": (1160.4, 427.0), "tri_tam": (13.0, 15.0), "tri_cor": (30, 30, 30), "letra": ("S", (1160.4, 448.0)),
          "texto": ("SOBE PARA O", "TÉRREO"), "texto_px": (1138.0, 447.0)}


def escada(Q, img, q=ESCADA):
    import terreo_casaa_1011 as TA
    import final3840_casaa_terreo as T
    x0, p, n, y0, y1, ss = q["x0"], q["passo"], q["n"], q["y0"], q["y1"], q["ss"]
    xe = x0 + n * p
    X0, Y0, X1, Y1 = int(np.floor(x0)) - 2, int(np.floor(y0)) - 2, int(np.ceil(xe)) + 2, int(np.ceil(y1)) + 1
    h, w = Y1 - Y0, X1 - X0
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    X = X0 + (xx + 0.5) / ss
    Y = Y0 + (yy + 0.5) / ss
    dentro = ((X >= x0) & (X < xe) & (Y >= y0) & (Y < y1)).astype(np.float32)
    u = (X - x0) / p
    k = np.floor(u)
    fr = u - k
    f = np.ones_like(X)
    # a sombra do espelho seguinte no degrau de baixo (a luz do alto à direita), menos no último
    s0, sd = q["sombra"]
    f *= np.where(k < n - 1, 1 - s0 * np.exp(-(1 - fr) * p / sd), 1.0)
    # o nariz claro logo depois de cada espelho
    nf, nd = q["nariz"]
    f *= np.where(k > 0, 1 + (nf - 1) * np.exp(-fr * p / nd), 1.0)
    # o fio de cada espelho (e o do 1º degrau) e as bordas de cima e de baixo
    db = np.minimum(fr, 1 - fr) * p
    f *= np.where(db < q["linha_px"] / 2, q["linha"], 1.0)
    f *= np.where((np.abs(X - x0) < q["linha_px"] / 2) | (np.abs(X - xe) < q["linha_px"] / 2), q["linha"], 1.0)
    f *= np.where(np.abs(Y - y0) < q["borda_px"] / 2, q["borda"], 1.0)
    fs = cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA)
    a = cv2.resize(dentro, (w, h), interpolation=cv2.INTER_AREA)
    T_ = PE.textura_travertino(Q, Q.H, Q.W)[Y0:Y1, X0:X1] * q["tom"]
    novo = T_ * fs[..., None]
    # o véu depois da diagonal de corte
    (cx0, cy0), (cx1, cy1) = q["corte"]
    Xc = cx0 + (Y - cy0) * (cx1 - cx0) / (cy1 - cy0)
    v = np.clip((X - Xc) / q["rampa_px"] + 0.5, 0, 1)
    v = cv2.resize(v, (w, h), interpolation=cv2.INTER_AREA)[..., None] * q["veu"]
    novo = novo * (1 - v) + np.float32(q["veu_cor"]) * v
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    out = img.copy()
    out[Y0:Y1, X0:X1] = u8(reg * (1 - a[..., None]) + novo * a[..., None])
    # ▶ e S no 1º degrau
    o = out.astype(np.float32)
    o = TA.triangulo(o, TA.seta_tri(q["tri"][0], q["tri"][1], (1, 0), *q["tri_tam"]), q["tri_cor"])
    out = u8(o)
    out = T.letra(Q, out, q["letra"][0], centro_q=q["letra"][1])
    print(f"    escada: {n} degraus pelo PDF no travertino ({p / Q.px_m:.2f} m), os de depois da diagonal (8 a 17) sob o "
          f"véu de {q['veu']:.0%}; ▶ e S no 1º degrau (o render a tinha invertida)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 5. A piscina (notas 3, 4 e 5): a água pelo render (o azul; a faixa do meio é água desde 28/10), mais sóbria como a do
# Térreo (`pedidos_terreo_casae_1611.PISCINA`: metade da saturação e a tinta). A profundidade (18/11, usuário, com a linha
# verde no tanque da direita: "A única parte mais rasa da piscina é essa que eu delimitei, tá? O restante é tudo fundo.
# [...] não é bem uma prainha, na verdade é uma parte mais rasa mesmo"): só a faixa de cima do tanque da direita (de
# 781 a 808, junto à sauna; `rasa_ret`) rasa, no tom de antes; todo o resto fundo, mais escuro, com a sombra do degrau no
# lado fundo, junto à rasa. A borda entre a água comprida e o visor da academia na pastilha da piscina (o Barlavento de
# fundo seco da biblioteca, na escala dele); as outras bordas (a de cima e a da esquerda) em Bege Bahia lisa, um tom
# abaixo do pátio (o alto-relevo de 16/11, `pedidos_terreo_casad_1611._bege_levigado`).
PISCINA = dict(PE.PISCINA, funda=0.80, bloco=(855, 474, 1060, 926), azul=25, rasa_ret=(989.0, 781.0, 1053.5, 808.0),
               pastilha=(966.0, 489.0, 984.5, 770.0), barlavento=CASA / "biblioteca-objetos" / "04-materiais" /
               "piscina-e-areas-molhadas" / "barlavento-fundo.png", barlavento_m=4.64, pastilha_tom=0.97,
               bege=[(856.0, 474.0, 1000.0, 489.0), (856.0, 489.0, 870.5, 926.0)])


def piscina(Q, img, q=PISCINA):
    import pedidos_terreo_casad_1611 as PD
    out = img.astype(np.float32)
    bx0, by0, bx1, by1 = q["bloco"]
    reg = out[by0:by1, bx0:bx1]
    ag = (reg[..., 0] > reg[..., 2] + q["azul"])
    ag = cv2.morphologyEx(ag.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
    ag = ndimage.binary_fill_holes(ag)
    ag &= ~paredes(Q)[by0:by1, bx0:bx1]
    yy, xx = np.mgrid[by0:by1, bx0:bx1]
    rx0, ry0, rx1, ry1 = q["rasa_ret"]
    rasa = ag & (xx >= rx0) & (xx < rx1) & (yy >= ry0) & (yy < ry1)
    funda = ag & ~rasa
    wf = cv2.GaussianBlur(funda.astype(np.float32), (0, 0), 1.0)
    lum = reg.mean(axis=2, keepdims=True)
    novo = lum + (reg - lum) * q["sat"]
    novo = novo * np.float32(q["tinta"])
    novo = novo * (q["funda"] * wf + q["rasa"] * (1 - wf))[..., None]
    d = cv2.distanceTransform((~rasa).astype(np.uint8), cv2.DIST_L2, 3)
    f, alc = q["degrau"]
    sombra = np.where(funda, 1 - (1 - f) * np.clip(1 - d / alc, 0, 1), 1.0)
    novo = novo * sombra[..., None]
    a = cv2.GaussianBlur(ag.astype(np.float32), (0, 0), 0.5) * ag
    reg[:] = reg * (1 - a[..., None]) + novo * a[..., None]
    # a borda junto à academia na pastilha
    P = cv2.imread(str(q["barlavento"])).astype(np.float32)
    lado = int(round(q["barlavento_m"] * Q.px_m))
    P = cv2.resize(P, (lado, lado), interpolation=cv2.INTER_AREA) * q["pastilha_tom"]
    x0, y0, x1, y1 = q["pastilha"]
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    m = np.zeros((Y1 - Y0, X1 - X0), np.float32)
    m[:] = 1
    m[:, 0] = X0 + 1 - x0
    m[:, -1] = x1 - (X1 - 1)
    m *= ~ag[Y0 - by0:Y1 - by0, X0 - bx0:X1 - bx0]
    tile = np.tile(P, ((Y1 - Y0) // lado + 2, (X1 - X0) // lado + 2, 1))[(Y0 % lado):(Y0 % lado) + Y1 - Y0,
                                                                         (X0 % lado):(X0 % lado) + X1 - X0]
    out[Y0:Y1, X0:X1] = out[Y0:Y1, X0:X1] * (1 - m[..., None]) + tile * m[..., None]
    # as outras bordas em Bege Bahia lisa
    capa = np.zeros(out.shape[:2], bool)
    for r in q["bege"]:
        capa |= ret_mask(capa.shape, r)
    capa &= ~paredes(Q)
    capa[by0:by1, bx0:bx1] &= ~ag
    # (não sobre o vidro do visor nem o caixilho escuro dele)
    cap_reg = img.astype(np.float32)
    capa &= cap_reg.mean(axis=2) > 150
    ys, xs = np.nonzero(capa)
    Y0, Y1, X0, X1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    Tb = PD._bege_levigado(Y1 - Y0, X1 - X0, PD.BORDA_PISCINA)
    mm = capa[Y0:Y1, X0:X1]
    agr = np.zeros(mm.shape, bool)
    agr_full = np.zeros(out.shape[:2], bool)
    agr_full[by0:by1, bx0:bx1] = ag
    agr = agr_full[Y0:Y1, X0:X1]
    quina = mm & (cv2.dilate(agr.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    Tb = Tb * np.where(quina, q["quina"], 1.0)[..., None]
    sub = out[Y0:Y1, X0:X1]
    sub[mm] = Tb[mm]
    beira = agr & (cv2.dilate(mm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    sub[beira] *= q["beira_agua"]
    print(f"    piscina: a água mais sóbria (saturação a {q['sat']:.0%}); só a faixa de cima do tanque da direita rasa, o "
          f"resto fundo ({q['funda']:.0%}) com a sombra do degrau; a borda junto à academia na pastilha Barlavento; as "
          "outras bordas em Bege Bahia lisa")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# As peças da biblioteca: BT.pousar com o centro no px (o centro contínuo - 0,5), wt x ht antes do giro (anti-horário).
def _pousar(img, P, x0, y0, x1, y1, ang, sombra, Q, troca=False):
    import biblioteca_terreo_casaa_1211 as BT
    wt, ht = (y1 - y0, x1 - x0) if troca else (x1 - x0, y1 - y0)
    o = BT.pousar(img.astype(np.float32), P, (x0 + x1) / 2 - 0.5, (y0 + y1) / 2 - 0.5, wt, ht, ang,
                  BT.SOMBRAS[sombra] if sombra else [], Q.px_m, nao=paredes(Q, 0.5))
    return u8(o)


def piso_linhas(Q, img, rets, ok, busca=700, nome="piso"):
    """Cada retângulo (px) recebe o piso das mesmas linhas, deslocado na horizontal (as réguas do vinílico correm
    deitadas): o menor deslocamento em que o retângulo deslocado cai todo em `ok` (bool, o piso limpo), com a costura
    das bordas (`biblioteca_subsolo_casaa_1211.costura`)."""
    import biblioteca_subsolo_casaa_1211 as BS
    out = img.copy()
    par = paredes(Q, 0.5)
    # junto às paredes (a faixa da sombra delas, que o filtro marca), as mesmas linhas de outro x servem
    livre = ok | cv2.dilate(par.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool)
    for r in rets:
        livre &= ~ret_mask(livre.shape, r)
    for r in rets:
        x0, y0, x1, y1 = (int(round(v)) for v in r)
        achou = None
        for d in sorted(range(-busca, busca + 1), key=abs):
            if abs(d) < (x1 - x0) // 2 or x0 + d < 0 or x1 + d > out.shape[1]:
                continue
            if livre[y0:y1, x0 + d:x1 + d].all():
                achou = d
                break
        if achou is None:
            raise RuntimeError(f"{nome}: sem piso limpo para {r}")
        novo = np.ascontiguousarray(out[y0:y1, x0 + achou:x1 + achou])
        novo = BS.costura(out, novo, x0, y0, x1, y1, par)
        caixa = ~par[y0:y1, x0:x1]
        out[y0:y1, x0:x1][caixa] = novo[caixa]
    return out


# 10. A academia (a folha do mobiliário; como na Casa D: "as 2 esteiras A, as 2 bicicletas B e os 2 supinos nos tamanhos
# da Casa A"): os aparelhos de antes saem (o vinílico das mesmas linhas, de logo ao lado); entram, nos lugares do PDF,
# as 2 esteiras A (1,76 x 0,77 m, o console à esquerda como no PDF), as 2 bicicletas B (0,89 x 0,51 m, o console à
# esquerda), as 2 bolas, a estação de cabos, o suporte de halteres e os 2 supinos (o banco no comprimento do PDF, a
# barra embaixo, alongada como na Casa D). As barras de alongamento ficam (estão no PDF).
ACADEMIA = {"limpa": [(1031, 504, 1132, 556), (1031, 558, 1132, 611), (1025, 620, 1137, 673), (1025, 689, 1137, 741),
                      (1205, 493, 1292, 540), (1360, 578, 1483, 712), (1596, 790, 1709, 882), (1749, 782, 1791, 883),
                      (1903, 646, 1944, 752)],
            "esteiras": [(1082.35, 644.7), (1082.35, 713.5)], "esteira": (46.0, 105.2),
            "bicicletas": [(1081.95, 528.45), (1081.95, 582.75)], "bicicleta": (30.3, 52.9),
            "bolas": [(1228.2, 513.5), (1268.9, 513.5)], "bola_px": 39.0,
            "estacao": (1368.5, 581.9, 1478.6, 705.0),
            "halteres": (1924.0, 699.3), "halteres_ht": 95.6,
            "supinos": [(1653.15, 835.1), (1771.0, 835.1)], "supino_px": (80.6, 102.7), "barra": (170, 340)}


def academia(Q, img, q=ACADEMIA):
    import biblioteca_subsolo_casaa_1211 as BS
    import biblioteca_terreo_casaa_1211 as BT
    # o vinílico da legenda (as linhas finas das réguas fechadas) fora das paredes
    F = np.all(Q.chapada == (79, 120, 168), axis=2).astype(np.uint8)
    F = cv2.morphologyEx(F, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool) & ~paredes(Q, 0.2)
    I = img.astype(np.float32)
    med = cv2.medianBlur(img, 41).astype(np.float32)
    obj = (np.abs(I - med).max(axis=2) > 28) | (I.mean(axis=2) < 95)
    obj = cv2.dilate(obj.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    out = piso_linhas(Q, img, q["limpa"], F & ~obj, nome="academia")
    par = paredes(Q, 0.5)

    def pousa(P, cx, cy, wt, ht, ang, sombra="movel"):
        nonlocal out
        o = BT.pousar(out.astype(np.float32), P, cx - 0.5, cy - 0.5, wt, ht, ang, BT.SOMBRAS[sombra], Q.px_m, nao=par)
        out = u8(o)
    P = png(BIB / "academia/esteira-a.png")
    for cx, cy in q["esteiras"]:
        pousa(P, cx, cy, *q["esteira"], 90.0)
    P = png(BIB / "academia/bicicleta-b.png")
    for cx, cy in q["bicicletas"]:
        pousa(P, cx, cy, *q["bicicleta"], 90.0)
    P = png(BIB / "academia/bola-exercicio-e.png")
    for cx, cy in q["bolas"]:
        pousa(P, cx, cy, q["bola_px"], q["bola_px"], 0.0, "mesa")
    P = png(BIB / "academia/estacao-cabos-e.png")
    x0, y0, x1, y1 = q["estacao"]
    ht = y1 - y0
    pousa(P, (x0 + x1) / 2, (y0 + y1) / 2, ht * P.shape[1] / P.shape[0], ht, 0.0)
    P = png(BIB / "academia/suporte-halteres-e.png")
    ht = q["halteres_ht"]
    pousa(P, *q["halteres"], ht * P.shape[1] / P.shape[0], ht, 0.0)
    # o supino: a barra e o travessão do rack alongados (as colunas `barra` repetidas) até a proporção do PDF
    P = BS.ler_png("academia/banco-supino.png", cortar=False)
    ys, xs = np.nonzero(P[..., 3] > 0)
    P = np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    lb, la = q["supino_px"]
    alt, larg = P.shape[:2]
    d = max(0, int(round((la / lb * alt - larg) / 2)))
    a0, a1 = q["barra"]
    a0, a1 = a0 - xs.min(), a1 - xs.min()

    def col(x):
        return np.repeat(P[:, x:x + 1], d, axis=1)
    P = np.ascontiguousarray(np.concatenate([P[:, :a0], col(a0), P[:, a0:a1], col(a1), P[:, a1:]], axis=1))
    s = lb / P.shape[0]
    for cx, cy in q["supinos"]:
        pousa(P, cx, cy, P.shape[1] * s, P.shape[0] * s, 180.0)
    print("    academia: os aparelhos de antes saem (o vinílico das mesmas linhas); 2 esteiras A, 2 bicicletas B, 2 bolas, a "
          "estação de cabos, o suporte de halteres e 2 supinos da biblioteca")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 10b. A sauna (regra da Casa D: "os bancos da sauna são do mesmo material do piso, com tom em destaque"): o degrau e o
# assento (junto à parede de baixo) do PDF (ARQ_ELEMENTOS FIXOS) no travertino do piso (tecido de um trecho limpo da
# sauna), mais escuros, o assento mais que o degrau, com a face na borda e a sombra curta.
SAUNA = {"degrau": (1063.3, 837.1, 1180.1, 873.2), "assento": (1063.3, 873.2, 1180.1, 909.2),
         "piso_px": (1075, 776, 1165, 826), "tons": {"degrau": 0.86, "assento": 0.78}, "face": 0.80, "sombra": 0.30}


def sauna(Q, img, q=SAUNA):
    import revisao_terreo_casac_1511 as R15
    import biblioteca_terreo_casad_1511 as TD
    par = paredes(Q, 0.5)
    H, W = par.shape
    o = img.astype(np.float32)
    for nome in ("degrau", "assento"):
        x0, y0, x1, y1 = q[nome]
        X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
        a = np.zeros((H, W), np.float32)
        a[Y0:Y1, X0:X1] = 1
        a *= ~par
        o *= (1 - q["sombra"] * R15._sombra(a, W, H))[..., None]
        T_ = TD._tecido(img, q["piso_px"], Y1 - Y0, X1 - X0, 1811 + len(nome)) * q["tons"][nome]
        m = a[Y0:Y1, X0:X1] > 0
        borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        T_[borda] *= q["face"]
        reg = o[Y0:Y1, X0:X1]
        reg[m] = T_[m]
    print("    sauna: o degrau e o assento no travertino do piso, mais escuros (em destaque), com a face e a sombra")
    return u8(o)


# ----------------------------------------------------------------------------------------------------------------------
# 10c. Os chuveiros (o quadrado do PDF): a cabeça quadrada da biblioteca no quadrado do PDF, com o braço cromado até a
# parede e a canopla (como o do WC DCE 1 do Térreo, `dce_wcdce_terreo_casae_1811.wc`); o desenho de antes sai (o piso
# de logo ao lado, `limpa`, `de`).
CROMO = {"cromo": (206, 208, 211), "brilho": (238, 239, 241), "borda": (118, 121, 126),
         "sombra": [{"dx": 0.006, "dy": 0.008, "sig": 0.01, "forca": 0.22}], "png": BIB / "sauna/chuveiro-quadrado.png"}
CHUVEIROS = [
    # (nome, cabeça px, parede ("baixo"|"dir"), coordenada da parede, limpa px, (dx, dy) da fonte do piso)
    ("ducha", (1212.9, 880.9, 1224.8, 892.8), "baixo", 909.8, (1210, 876, 1229, 909.5), (0, -1)),
    ("vestiário", (1456.3, 870.7, 1468.2, 882.6), "dir", 1485.2, (1449, 864, 1485, 890), (0, -1)),
    ("WC DCE 2", (1916.0, 601.6, 1928.0, 613.6), "dir", 1945.0, None, None),     # o piso novo já cobre o de antes
]


def chuveiro(img, Q, cab, lado, parede, q=CROMO):
    import biblioteca_terreo_casaa_1211 as BT
    import correcoes_terreo_casab_1611 as CB
    from correcoes_terreo_casab_1611 import Mapa
    m = Mapa()
    out = img.copy()
    x0, y0, x1, y1 = cab
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    e, w2 = 0.35, 0.75
    if lado == "dir":
        braco, can = (cx, cy - w2, parede, cy + w2), (parede - 1.2, cy - 2.0, parede, cy + 2.0)
        brilho = (cx, cy - w2 + 0.15, parede, cy - w2 + 0.6)
        bb = (cx, cy - w2 - e, parede, cy + w2 + e)
        cb = (can[0] - e, can[1] - e, can[2], can[3] + e)
    else:
        braco, can = (cx - w2, cy, cx + w2, parede), (cx - 2.0, parede - 1.2, cx + 2.0, parede)
        brilho = (cx - w2 + 0.15, cy, cx - w2 + 0.6, parede)
        bb = (cx - w2 - e, cy, cx + w2 + e, parede)
        cb = (can[0] - e, can[1] - e, can[2] + e, can[3])
    CB.pintar(out, m, [(bb, "ret", q["borda"], 0), (braco, "ret", q["cromo"], 0), (brilho, "ret", q["brilho"], 0),
                       (cb, "ret", q["borda"], 0), (can, "ret", q["cromo"], 0)])
    o = out.astype(np.float32)
    BT.pousar(o, png(q["png"]), cx - 0.5, cy - 0.5, x1 - x0, y1 - y0, 0.0, q["sombra"], Q.px_m)
    out = u8(o)
    CB.pintar(out, m, [(cab, "contorno", q["borda"], 0.4)])
    return out


def chuveiros(Q, img, q=CHUVEIROS):
    import biblioteca_subsolo_casab_1311 as BB
    out = img.copy()
    par = paredes(Q, 0.5)
    for nome, cab, lado, parede, limpa, desloc in q:
        if limpa is not None:
            out = BB.piso_desloc(out, limpa, par, *desloc)
        out = chuveiro(out, Q, cab, lado, parede)
    print(f"    chuveiros: {', '.join(c[0] for c in q)} com a cabeça quadrada da biblioteca, o braço cromado e a canopla")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 10d. O vestiário (como na Casa D: "a cuba é esculpida no travertino, mas a bancada é no granito marrom tabaco
# intenso"): a bancada do PDF (ARQ_BANCADAS) no marrom tabaco com a face; a cuba de travertino da biblioteca no lugar da
# cuba do PDF, a torneira na parede da direita; a bacia Carrara no retângulo do PDF, a caixa contra a parede da esquerda.
VESTIARIO = {"bancada": (1457.1, 766.5, 1485.2, 839.7), "face": 0.82,
             "cuba": (1458.6, 787.0, 1484.4, 819.0), "cuba_png": BIB / "vestiario/cuba-travertino-vestiario.png",
             "bacia": (1336.0, 874.5, 1366.6, 895.6), "bacia_limpa": (1333, 870, 1372, 900),
             "bacia_png": BIB / "vestiario/bacia-carrara.png"}


def vestiario(Q, img, q=VESTIARIO):
    import biblioteca_subsolo_casad_1511 as SD
    import biblioteca_terreo_casad_1511 as TD
    import biblioteca_subsolo_casab_1311 as BB
    par = paredes(Q, 0.5)
    x0, y0, x1, y1 = q["bancada"]
    X0, Y0, X1, Y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    m = ret_mask(par.shape, (X0, Y0, X1, Y1)) & ~par
    out = TD._pinta_textura(img, m, SD.tabaco(Y1 - Y0, X1 - X0), q["face"])
    out = _pousar(out, png(q["cuba_png"]), *q["cuba"], -90.0, "baixa", Q, troca=True)
    out = BB.piso_desloc(out, q["bacia_limpa"], par, 1, 0)
    out = _pousar(out, png(q["bacia_png"]), *q["bacia"], 90.0, "baixa", Q, troca=True)
    print("    vestiário: a bancada no marrom tabaco, a cuba de travertino (a torneira na parede); a bacia Carrara")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 10e. O WC DCE 2 (banhos com o mesmo piso, 16/11; como o WC DCE 1 do Térreo, `dce_wcdce_terreo_casae_1811.wc`): o piso
# no cinza claro dos banhos da Casa D (o tom, a nuvem suave e o grão fino), de parede a parede, com a sombra curta rente
# às paredes; a bancada do PDF no marrom tabaco com a cuba compacta (a do WC DCE 1); a bacia Monte Carlo (a caixa contra
# a parede da direita); o box em vidro claro com as duas folhas de correr.
WC2 = {"piso": (1861.4, 491.9, 1945.0, 636.2), "bancada": (1915.1, 491.9, 1945.0, 529.4),
       "cuba": (1918.6, 499.1, 1939.4, 523.0), "cuba_png": "banho-do-motorista/cuba-compacta",
       "bacia": (1914.3, 540.0, 1945.0, 561.0), "bacia_png": BIB / "banho-dce-2/bacia-monte-carlo-sem-valvula.png",
       "tom": (210.8, 214.2, 220.0), "nuvem": (0.007, 2.0), "grao": (0.005, 0.6), "ao": (0.07, 2.0),
       "box": {"faixa": (1861.4, 579.9, 1945.0, 582.9), "vidro": (214, 219, 223), "vidro_a": 0.8,
               "fio": (150, 155, 160), "fio_px": 0.3,
               "folhas": [(1861.5, 580.7, 1907.0, 581.3), (1899.4, 581.5, 1944.9, 582.1)],
               "folha_cor": (150, 156, 162), "perfil": (112, 117, 122), "perfil_px": 1.0}}


def wc_dce2(Q, img, q=WC2):
    import correcoes_terreo_casab_1611 as CB
    import mobiliario_terreo_casac_1311 as MB
    import biblioteca_subsolo_casad_1511 as SD
    import biblioteca_terreo_casad_1511 as TD
    from correcoes_terreo_casab_1611 import Mapa
    from janela_pia_casaa_1611 import alfa_ret
    mp = Mapa()
    par = paredes(Q, 0.5)
    x0, y0, x1, y1 = q["piso"]
    X0, Y0, X1, Y1 = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1, int(np.ceil(x1)) + 1, int(np.ceil(y1)) + 1
    forma = (Y1 - Y0, X1 - X0)
    out = img.copy()
    antigo = out[Y0:Y1, X0:X1].astype(np.float32)
    rng = np.random.default_rng(1811)
    fn, sn = q["nuvem"]
    fg, sg = q["grao"]
    nuvem = cv2.GaussianBlur(rng.normal(0, 1, forma).astype(np.float32), (0, 0), sn)
    nuvem /= max(float(nuvem.std()), 1e-6)
    grao = cv2.GaussianBlur(rng.normal(0, 1, forma).astype(np.float32), (0, 0), sg)
    grao /= max(float(grao.std()), 1e-6)
    piso = np.float32(q["tom"])[None, None] * (1 + fn * nuvem + fg * grao)[..., None]
    # a sombra curta rente às paredes (as do PDF dentro da caixa)
    livre = ~par[Y0:Y1, X0:X1]
    d = cv2.distanceTransform(livre.astype(np.uint8), cv2.DIST_L2, 3)
    fa, da = q["ao"]
    piso *= (1 - fa * np.exp(-np.maximum(d - 0.5, 0) / da))[..., None]
    lp = (x0 - X0, y0 - Y0, x1 - X0, y1 - Y0)
    a = alfa_ret(lp, forma) * livre
    reg = antigo * (1 - a[..., None]) + piso * a[..., None]
    out[Y0:Y1, X0:X1] = u8(reg)
    # a bancada no marrom tabaco e a cuba compacta
    bx0, by0, bx1, by1 = (int(round(v)) for v in q["bancada"])
    m = ret_mask(par.shape, (bx0, by0, bx1, by1)) & ~par
    out = TD._pinta_textura(out, m, SD.tabaco(by1 - by0, bx1 - bx0), 0.82)
    P = MB.ler(q["cuba_png"])
    cx0, cy0, cx1, cy1 = q["cuba"]
    wt, ht = cx1 - cx0, cy1 - cy0
    giro = 90.0 if (wt < ht) != (P.shape[1] < P.shape[0]) else 0.0
    if giro:
        wt, ht = ht, wt
    out = MB.pousar(out, P, (cx0 + cx1) / 2 - 0.5, (cy0 + cy1) / 2 - 0.5, wt, ht, giro, "baixa", par)
    # a bacia: a caixa (em cima no png) contra a parede da direita
    out = _pousar(out, png(q["bacia_png"]), *q["bacia"], -90.0, "baixa", Q, troca=True)
    # o box
    b = q["box"]
    fx0, fy0, fx1, fy1 = b["faixa"]
    a_b = alfa_ret((fx0 - X0, fy0 - Y0, fx1 - X0, fy1 - Y0), forma)[..., None] * b["vidro_a"]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = u8(reg * (1 - a_b) + np.float32(b["vidro"]) * a_b)
    pecas = [((fx0, fy0, fx1, fy0 + b["fio_px"]), "ret", b["fio"], 0),
             ((fx0, fy1 - b["fio_px"], fx1, fy1), "ret", b["fio"], 0)]
    for f in b["folhas"]:
        a0, b0, a1, b1 = f
        pecas += [(f, "ret", b["folha_cor"], 0), ((a0, b0 - 0.3, a0 + b["perfil_px"], b1 + 0.3), "ret", b["perfil"], 0),
                  ((a1 - b["perfil_px"], b0 - 0.3, a1, b1 + 0.3), "ret", b["perfil"], 0)]
    CB.pintar(out, mp, pecas)
    print("    WC DCE 2: o piso cinza dos banhos (o do WC DCE 1), a bancada marrom tabaco com a cuba compacta, a bacia Monte "
          "Carlo e o box em vidro claro")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 10f. O DCE (nota 7: "Colocar um fundo, para o piso não ser o fundo"; como o DCE 1 do Térreo): a cama e o criado de
# antes saem (o piso marrom limpo de logo acima, tecido); a cama de solteiro da biblioteca no retângulo do PDF, a
# cabeceira na parede da direita; o criado-mudo na cor sólida dos armários da E, com o fio e a sombra curta; o
# guarda-roupa de cabides desenhado como o do DCE 1: o fundo em madeira clara, o varão no comprido, os cabides, o fio.
DCE = {"limpa": (1724, 546, 1855, 638), "piso_px": (1660, 500, 1820, 560),
       "cama": (1729.5, 577.8, 1852.5, 635.2), "cama_png": BIB / "quarto-dce-2/cama-solteiro-e.png",
       "criado": (1828.6, 551.0, 1852.5, 574.9), "criado_cor": (129, 160, 189), "criado_fio": (111, 138, 163),
       "armario": (1643.5, 599.3, 1715.1, 635.2), "fundo": (184, 204, 220), "varao": (138, 140, 142),
       "cabide": (150, 152, 154), "contorno": (115, 161, 198), "passo_px": 5.2}


def dce(Q, img, q=DCE):
    import biblioteca_terreo_casad_1511 as TD
    import biblioteca_terreo_casaa_1211 as BT
    import correcoes_terreo_casab_1611 as CB
    from correcoes_terreo_casab_1611 import Mapa
    mp = Mapa()
    par = paredes(Q, 0.5)
    out = img.copy()
    # o lugar da cama e do criado de antes no piso marrom limpo
    x0, y0, x1, y1 = q["limpa"]
    m = ret_mask(par.shape, q["limpa"]) & ~cv2.dilate(par.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    T_ = TD._tecido(out, q["piso_px"], y1 - y0, x1 - x0, 1812)
    big = np.zeros(out.shape, np.float32)
    big[y0:y1, x0:x1] = T_
    o = out.astype(np.float32)
    # a luz larga do lugar (a sombra rente às paredes) volta pelo desfocado do piso de fora
    o[m] = big[m]
    out = u8(o)
    out = _pousar(out, png(q["cama_png"]), *q["cama"], -90.0, "movel", Q, troca=True)
    CB.sombra(out, mp, q["criado"], 0.28, dx=-0.8, dy=0.8, sigma=0.8)
    CB.pintar(out, mp, [(q["criado"], "ret", q["criado_cor"], 0), (q["criado"], "contorno", q["criado_fio"], 0.6)])
    # o guarda-roupa de cabides
    ax0, ay0, ax1, ay1 = q["armario"]
    ym = (ay0 + ay1) / 2
    pecas = [(q["armario"], "ret", q["fundo"], 0), ((ax0 + 1.5, ym - 0.45, ax1 - 1.5, ym + 0.45), "ret", q["varao"], 0)]
    x = ax0 + 4.5
    while x < ax1 - 3.5:
        pecas.append(((x - 0.4, ay0 + 4.0, x + 0.4, ay1 - 4.0), "ret", q["cabide"], 0))
        x += q["passo_px"]
    pecas.append((q["armario"], "contorno", q["contorno"], 0.8))
    CB.sombra(out, mp, q["armario"], 0.22, dx=-0.8, dy=0.8, sigma=0.8)
    CB.pintar(out, mp, pecas)
    print("    DCE: a cama de solteiro da biblioteca (a cabeceira na parede), o criado-mudo na cor dos armários e o "
          "guarda-roupa de cabides com fundo")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 10g. O elevador: a cabine da biblioteca na caixa da cabine do PDF (INS_INSTALAÇÕES HIDRÁULICAS), a porta embaixo.
ELEVADOR = {"cabine": (1960.0, 729.0, 2043.5, 808.9), "png": BIB / "elevador/cabine-elevador-e.png"}


def elevador(Q, img, q=ELEVADOR):
    import biblioteca_terreo_casaa_1211 as BT
    x0, y0, x1, y1 = q["cabine"]
    o = BT.pousar(img.astype(np.float32), png(q["png"]), (x0 + x1) / 2 - 0.5, (y0 + y1) / 2 - 0.5, x1 - x0, y1 - y0,
                  0.0, [], Q.px_m)
    print("    elevador: a cabine da biblioteca na caixa do PDF")
    return u8(o)


# ----------------------------------------------------------------------------------------------------------------------
# 5b. A cascata (18/11, usuário: "Conseguimos representar a cascata?", com a foto de referência: a bica de inox na
# parede de pedra rústica, a lâmina d'água caindo na piscina e a espuma onde ela bate; "Sendo vista de cima para a
# cascata"). O PDF não a desenha: entra na parede de fora da piscina comprida (a da esquerda, a que se vê da academia
# pelo visor), no meio dela, com 2,0 m. Vista de cima: o topo da parede no trecho da cascata em pedra rústica (os
# filetes da foto, em vez do Bege Bahia liso da borda); a bica de inox saindo da face da parede sobre a água, com o fio
# escuro, o brilho e a sombra curta na água; a lâmina caindo logo adiante (riscos claros no comprido); a espuma branca
# onde ela bate, que se desfaz para dentro da piscina, e as ondinhas claras mais adiante.
# Depois (usuário, com o recorte da piscina e a marca verde: "A cascata fica aqui na parte de baixo. Tem o revestimento,
# né, em pedra e tudo, mas o mais importante é a cascata em si [...] é bom fazer do jeito que você fez, você só colocou
# no lugar errado"): o mesmo desenho, na parede de baixo da piscina (`lado` "sul"), no trecho da marca (x 884 a 949,
# ~1,1 m): o revestimento de pedra numa faixa de 7 px (0,12 m) junto à face da parede, a bica saindo dela para cima,
# sobre a água, e a lâmina, a espuma e as ondinhas para dentro da piscina. O desenho é o da parede da esquerda
# (`_cascata_oeste`), feito no recorte girado (a parede de baixo vira a da esquerda) e desvirado; no trecho mais curto a
# espuma sai um pouco mais larga (`miolo_px`, `bolha_lim`), para ler como a de antes.
CASCATA = {"lado": "sul", "x": (884.0, 949.0), "face": 924.6, "pedra_px": 7.0,
           "bica_px": 6.5, "lamina_px": 3.5, "espuma_px": 15.0, "miolo_px": 3.0, "bolha_lim": 0.48,
           "ondas_px": 30.0, "inox": (196, 199, 201), "inox_fio": (98, 102, 106), "inox_brilho": (238, 240, 241),
           "pedra": [(150, 160, 168), (128, 138, 147), (168, 177, 184), (112, 121, 130)], "junta": (82, 88, 94),
           "espuma": (246, 247, 247), "semente": 1811}
# a de antes, na parede da esquerda da piscina comprida (2,0 m): CASCATA_OESTE
CASCATA_OESTE = dict(CASCATA, lado="oeste", y=(575.0, 695.0), parede=(859.5, 870.0), miolo_px=2.2, bolha_lim=0.56)


def cascata(Q, img, q=CASCATA):
    if q["lado"] == "sul":
        x0, x1 = q["x"]
        face = q["face"]
        topo = face - q["pedra_px"]
        alc = q["bica_px"] + q["lamina_px"] + max(q["espuma_px"], q["ondas_px"]) + 6
        Rx0, Rx1 = int(np.floor(x0)) - 6, int(np.ceil(x1)) + 6
        Ry0, Ry1 = int(np.floor(topo - alc)) - 4, int(np.ceil(face)) + 3
        # girado no sentido horário, a parede de baixo fica à esquerda: (x, y) -> (Ry1 - y, x - Rx0)
        rot = cv2.rotate(np.ascontiguousarray(img[Ry0:Ry1, Rx0:Rx1]), cv2.ROTATE_90_CLOCKWISE)
        qr = dict(q, y=(x0 - Rx0, x1 - Rx0), parede=(Ry1 - face, Ry1 - topo))
        rot = _cascata_oeste(rot, qr)
        out = img.copy()
        out[Ry0:Ry1, Rx0:Rx1] = cv2.rotate(rot, cv2.ROTATE_90_COUNTERCLOCKWISE)
        print(f"    cascata: a bica de inox de {(x1 - x0) / Q.px_m:.1f} m na parede de baixo da piscina, a lâmina, a "
              "espuma e as ondinhas para dentro dela; o revestimento de pedra rústica junto à face da parede")
        return out
    out = _cascata_oeste(img, q)
    y0, y1 = q["y"]
    print(f"    cascata: a bica de inox de {(y1 - y0) / Q.px_m:.1f} m na parede de fora da piscina, a lâmina e a espuma; o "
          "topo da parede no trecho em pedra rústica")
    return out


def _cascata_oeste(img, q):
    """A cascata numa parede à esquerda da água (a água para +x), no trecho y = q["y"]; q["parede"]: x da faixa de pedra
    (de fora para a face da água)."""
    y0, y1 = q["y"]
    p0, p1 = q["parede"]
    ss = 4
    X0, X1 = int(np.floor(p0)) - 1, int(np.ceil(p1 + q["bica_px"] + q["ondas_px"])) + 2
    Y0, Y1 = int(np.floor(y0)) - 3, int(np.ceil(y1)) + 4
    h, w = Y1 - Y0, X1 - X0
    rng = np.random.default_rng(q["semente"])
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1].copy()
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    X = X0 + (xx + 0.5) / ss
    Y = Y0 + (yy + 0.5) / ss
    dentro_y = (Y >= y0) & (Y < y1)

    def baixa(a):
        return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)

    # o topo da parede em pedra rústica: em cada fiada (no comprido da parede) uma ou duas pedras na largura, de
    # comprimentos e tons variados, com a junta escura e a aresta de cima clara (o relevo)
    pedra = np.zeros((h * ss, w * ss, 3), np.float32)
    junta = np.zeros((h * ss, w * ss), np.float32)
    aresta = np.zeros((h * ss, w * ss), np.float32)
    yc = y0 - rng.uniform(0, 4)
    while yc < y1:
        comp = rng.uniform(4.0, 13.0)
        cortes = [p0, p1] if rng.random() < 0.45 else [p0, p0 + (p1 - p0) * rng.uniform(0.35, 0.65), p1]
        for xa, xb in zip(cortes[:-1], cortes[1:]):
            cy0 = yc + rng.uniform(-1.5, 1.5) if xa > p0 else yc
            tom = np.float32(q["pedra"][rng.integers(len(q["pedra"]))]) * rng.uniform(0.92, 1.08)
            m = (X >= xa) & (X < xb) & (Y >= cy0) & (Y < yc + comp)
            pedra[m] = tom
            junta[m & ((np.abs(Y - cy0) < 0.4) | (np.abs(X - xa) < 0.35))] = 1
            aresta[m & (Y >= cy0 + 0.4) & (Y < cy0 + 1.1)] = 1
        yc += comp
    grao = cv2.GaussianBlur(rng.normal(0, 1, (h * ss, w * ss)).astype(np.float32), (0, 0), 0.8 * ss)
    pedra *= (1 + 0.07 * grao / max(float(grao.std()), 1e-6) + 0.10 * aresta)[..., None]
    pedra = pedra * (1 - junta[..., None]) + np.float32(q["junta"]) * junta[..., None]
    a_p = baixa(dentro_y & (X >= p0) & (X < p1))[..., None]
    reg = reg * (1 - a_p) + baixa_c(pedra, w, h) * a_p
    # a sombra curta da bica e da lâmina na água
    b0, b1 = p1, p1 + q["bica_px"]
    sb = baixa(dentro_y & (X >= b1) & (X < b1 + 3.0)) * 0.22
    reg *= (1 - sb)[..., None]
    # a espuma onde a lâmina bate: branca junto dela, desfazendo-se para dentro da piscina, em bolhas
    l1 = b1 + q["lamina_px"]
    d = np.clip(X - l1, 0, None)
    bol = cv2.GaussianBlur(rng.random((h * ss, w * ss)).astype(np.float32), (0, 0), 0.9 * ss)
    bol = (bol - bol.min()) / max(float(bol.max() - bol.min()), 1e-6)
    pontas = np.clip((np.minimum(Y - y0, y1 - Y)) / 6.0, 0, 1)
    # o miolo branco junto à lâmina e as bolhas soltas mais adiante
    lim = q.get("bolha_lim", 0.56)
    miolo = np.exp(-d / q.get("miolo_px", 2.2))
    bolhas = (bol > lim) * np.exp(-d / (q["espuma_px"] * 0.55)) * np.clip((bol - lim) / 0.12, 0, 1)
    esp = np.clip(0.95 * miolo + 0.9 * bolhas, 0, 1) * pontas
    esp *= ((X >= l1 - 0.5) & (Y >= y0 - 2) & (Y < y1 + 2))
    # as ondinhas claras mais adiante: pedaços de arco quebrados, não linhas retas
    torce = cv2.GaussianBlur(rng.normal(0, 1, (h * ss, w * ss)).astype(np.float32), (0, 0), 2.5 * ss)
    torce /= max(float(torce.std()), 1e-6)
    onda = 0.5 + 0.5 * np.sin((d / 3.6 + 0.9 * torce) * 2 * np.pi)
    quebra = cv2.GaussianBlur(rng.random((h * ss, w * ss)).astype(np.float32), (0, 0), 1.5 * ss)
    quebra = (quebra - quebra.min()) / max(float(quebra.max() - quebra.min()), 1e-6)
    onda = (np.clip(onda - 0.8, 0, 1) / 0.2 * (quebra > 0.5) * np.exp(-d / q["ondas_px"]) *
            (d > q["espuma_px"] * 0.35) * pontas * 0.22)
    a_e = baixa(np.clip(esp + onda * (Y >= y0) * (Y < y1), 0, 1))[..., None]
    reg = reg * (1 - a_e) + np.float32(q["espuma"]) * a_e
    # a lâmina caindo, vista de cima: riscos claros no comprido, translúcidos
    risco = cv2.GaussianBlur(rng.normal(0, 1, (h * ss, w * ss)).astype(np.float32), (0, 0), sigmaX=0.6 * ss,
                             sigmaY=0.25 * ss)
    risco = np.clip(0.75 + 0.5 * risco / max(float(risco.std()), 1e-6), 0.35, 1)
    a_l = baixa((dentro_y & (X >= b1) & (X < l1)) * risco)[..., None] * 0.85
    reg = reg * (1 - a_l) + np.float32((240, 243, 244)) * a_l
    # a bica de inox: a chapa, o fio escuro em volta, o brilho no comprido
    bica = dentro_y & (X >= b0) & (X < b1)
    fio = bica & ((X >= b1 - 0.45) | (Y < y0 + 0.45) | (Y >= y1 - 0.45))
    brilho = bica & (X >= b0 + 1.5) & (X < b0 + 2.3)
    for m, cor in ((bica, q["inox"]), (fio, q["inox_fio"]), (brilho, q["inox_brilho"])):
        a = baixa(m)[..., None]
        reg = reg * (1 - a) + np.float32(cor) * a
    out[Y0:Y1, X0:X1] = reg
    return u8(out)


def baixa_c(A, w, h):
    return cv2.resize(A, (w, h), interpolation=cv2.INTER_AREA)


# ----------------------------------------------------------------------------------------------------------------------
# 11. As portas de giro (G3: "Melhorar representação das portas de giro. Encostar nas paredes."; o padrão da Casa D,
# `portas_casae_1711`): o PDF do Subsolo desenha as folhas em pedaços (a busca de `pedidos_terreo_casac_1311.portas_pdf`
# não as acha), então cada porta vem do PDF à mão: a folha aberta (o retângulo dos pedaços), os marcos no plano da
# parede (pintados de parede: a ponta dela vai até a face da folha, quina a quina) e a caixa da limpeza (a folha cinza e
# os batentes brancos de antes saem, com o piso de logo adiante, `sentido`). As folhas de madeira na madeira clara das
# portas da Casa D; as da sauna, do vestiário e dos boxes em vidro claro com o fio cinza (como na Casa D).
PORTAS = [
    # (nome, folha, marcos, limpa, sentido, "madeira"|"vidro")
    ("casa de máquinas (5,83 m²)", (1958.4, 491.9, 1960.8, 539.6), [(1954.0, 482.9, 1958.4, 491.9),
                                                                   (2006.2, 482.9, 2010.4, 491.9)],
     (1953.0, 489.0, 1966.0, 545.0), (12.0, 0.0), "bronze"),
    ("WC DCE 2", (1861.4, 496.3, 1909.2, 498.7), [(1852.5, 491.9, 1861.4, 496.3), (1852.5, 544.1, 1861.4, 548.3)],
     None, None, "madeira"),
    ("vestiário", (1336.0, 777.0, 1383.7, 779.4), [(1327.0, 771.0, 1336.0, 777.0), (1327.0, 824.7, 1336.0, 829.0)],
     (1335.0, 770.0, 1389.0, 784.0), (0.0, 12.0), "vidro"),
    ("sauna", (1189.7, 774.0, 1231.5, 776.4), [(1180.7, 768.0, 1189.7, 774.0), (1180.7, 815.8, 1189.7, 820.0)],
     (1188.0, 767.0, 1237.0, 781.0), (0.0, 12.0), "vidro"),
    ("depósito (de cima)", (1774.8, 356.2, 1815.0, 358.6), [(1768.0, 350.0, 1774.8, 356.2)],
     (1774.0, 350.0, 1821.0, 363.0), (0.0, 12.0), "madeira"),
    ("depósito (de baixo)", (1774.8, 434.1, 1815.0, 436.5), [(1768.0, 436.5, 1774.8, 443.0)],
     (1774.0, 429.0, 1821.0, 442.0), (0.0, -12.0), "madeira"),
    ("casa de máquinas (15,07 m²)", (1551.5, 927.7, 1553.9, 975.5), [(1553.9, 909.8, 1558.1, 927.7),
                                                                    (1502.0, 909.8, 1506.1, 927.7)],
     (1545.0, 925.0, 1559.0, 981.0), (-12.0, 0.0), "bronze"),
    ("DCE", (1648.0, 491.9, 1650.3, 539.6), [(1643.5, 482.9, 1648.0, 491.9), (1695.7, 482.9, 1699.9, 491.9)],
     (1644.5, 489.0, 1657.0, 545.0), (12.0, 0.0), "madeira"),
    ("WC do vestiário", (1404.2, 843.2, 1406.6, 884.1), [], (1397.0, 842.0, 1407.0, 888.0), (-10.0, 0.0), "madeira"),
    ("box do vestiário", (1410.5, 843.2, 1412.9, 884.1), [], (1410.0, 842.0, 1419.0, 888.0), (10.0, 0.0), "vidro"),
    ("box da ducha", (1208.7, 838.2, 1209.9, 879.0), [], (1204.0, 835.0, 1215.0, 883.0), (9.0, 0.0), "vidro"),
]
# (18/11, usuário: "Porta da casa de máquinas em tom bronze.") as das duas casas de máquinas no bronze escovado das folhas
# das suítes do 1º Pavimento da Casa E (`final3840_casac.BRISES_SUITES_TC`): a cor, a borda escura, os fios no comprido e
# um brilho fino no meio
BRONZE = {"madeira": (74, 106, 139), "contorno": (44, 66, 90), "veio": 0.07, "brilho": (112, 146, 180),
          "brilho_px": 0.4}
VIDRO = {"vidro": (214, 219, 223), "fio": (150, 155, 160), "fio_px": 0.35, "perfil": (112, 117, 122), "perfil_px": 1.0,
         "sombra": 0.18}


def portas(Q, img, q=PORTAS):
    import correcoes_terreo_casab_1611 as CB
    import portas_casae_1711 as PC
    from correcoes_terreo_casab_1611 import Mapa
    m = Mapa()
    out = img.copy()
    for i, (nome, folha, marcos, limpa, sentido, tipo) in enumerate(q):
        if limpa is not None:
            fx0, fy0, fx1, fy1 = folha
            ao_longo = (30.0, 0.0) if (fx1 - fx0) > (fy1 - fy0) else (0.0, 30.0)
            sentidos = [sentido, (sentido[0] * 1.8, sentido[1] * 1.8), ao_longo, (-ao_longo[0], -ao_longo[1])]
            rm = m.reti(limpa)
            ddx, ddy = int(round(sentido[0])), int(round(sentido[1]))
            F = out[rm[1] + ddy:rm[3] + ddy, rm[0] + ddx:rm[2] + ddx].astype(np.float32)
            LF, cF = F.mean(axis=2), F.max(axis=2) - F.min(axis=2)
            neutro = float(np.median(cF)) < 14
            sel = (LF > 105) if neutro else (cF >= 14)
            amostra = LF[sel] if sel.sum() > 10 else LF.ravel()
            med = float(np.median(amostra))
            q1, q3 = np.percentile(amostra, [25, 75])
            lim = max(5.0, 2.0 * (q3 - q1) / 1.35)
            PC._remendo(out, m, limpa, sentidos, PC._destoa_porta(med, lim, neutro), med, tol=max(6.0, lim),
                        neutro=neutro)
        if marcos:
            CB.pintar(out, m, [(r, "ret", PAREDE, 0) for r in marcos])
        if tipo in ("madeira", "bronze"):
            vert = (folha[3] - folha[1]) > (folha[2] - folha[0])
            if tipo == "madeira":
                PC.folha(out, m, folha, vert, 1811 + i)
            else:
                b = BRONZE
                PC.folha(out, m, folha, vert, 1811 + i, dict(PC.FOLHA, madeira=b["madeira"], contorno=b["contorno"],
                                                               veio=b["veio"]))
                x0, y0, x1, y1 = folha
                bp = b["brilho_px"] / 2
                meio = (((x0 + x1) / 2 - bp, y0 + 0.8, (x0 + x1) / 2 + bp, y1 - 0.8) if vert else
                        (x0 + 0.8, (y0 + y1) / 2 - bp, x1 - 0.8, (y0 + y1) / 2 + bp))
                CB.pintar(out, m, [(meio, "ret", b["brilho"], 0)])
        else:
            v = VIDRO
            CB.sombra(out, m, folha, v["sombra"], dx=-0.8, dy=0.8, sigma=0.8)
            x0, y0, x1, y1 = folha
            vert = (y1 - y0) > (x1 - x0)
            p = v["perfil_px"]
            pontas = [(x0, y0, x1, y0 + p), (x0, y1 - p, x1, y1)] if vert else [(x0, y0, x0 + p, y1), (x1 - p, y0, x1, y1)]
            CB.pintar(out, m, [(folha, "ret", v["vidro"], 0), (folha, "contorno", v["fio"], v["fio_px"])] +
                      [(r, "ret", v["perfil"], 0) for r in pontas])
    # os vãos no plano da parede, no Bege Bahia de logo ao lado (os traços cinza dos batentes de antes saem)
    import biblioteca_subsolo_casab_1311 as BB
    par = paredes(Q, 0.5)
    for r, dx, dy in VAOS:
        out = BB.piso_desloc(out, r, par, dx, dy)
    print(f"    portas: {len(q)} portas de giro pelo PDF, quina a quina com a parede (madeira da Casa D; bronze nas casas de máquinas; "
          f"vidro na sauna, no vestiário e nos boxes); {len(VAOS)} vãos sem os traços dos batentes de antes")
    return out


# os vãos das portas no plano da parede (px) e o lado do Bege Bahia que os refaz (dx, dy)
VAOS = [((1648.6, 483.2, 1695.4, 491.6), 0, -1),          # DCE (o pátio acima)
        ((1959.4, 483.2, 2005.4, 491.8), 0, -1),          # casa de máquinas de 5,83 m² (o depósito acima)
        ((1768.4, 356.6, 1774.6, 436.2), -1, 0)]          # depósito (a circulação à esquerda)


# ----------------------------------------------------------------------------------------------------------------------
# 12. Os rótulos no padrão de todas as casas (16/11; `pedidos_terreo_casae_1611.ROTULOS`: Inter, o nome e a área, um
# corpo só, no meio do piso livre de cada ambiente, as fileiras vizinhas pela mesma base; a cor pelo fundo). "AMBIENTE"
# sai (riscado pelo cliente; o PDF não dá nome à ducha). A CASA DE MÁQUINAS de 5,83 m² em 3 linhas (a sala é estreita).
# A descrição da escada ("SOBE PARA O / TÉRREO") no corpo das descrições do Térreo, à esquerda da escada.
ROTULOS = [
    ("CIRCULAÇÃO", ("CIRCULAÇÃO", "A: 38,37 m²"), (1420.0, 342.0), "normal"),
    ("DEPÓSITO", ("DEPÓSITO", "A: 12,65 m²"), (1912.0, 384.0), "normal"),
    ("DCE", ("DCE", "A: 8,4 m²"), (1752.0, 532.0), "normal"),
    ("WC DCE 2", ("WC DCE 2", "A: 3,36 m²"), (1888.0, 532.0), "wc"),
    ("CASA DE MÁQUINAS (5,83)", ("CASA DE", "MÁQUINAS", "A: 5,83 m²"), (2002.0, 592.0), "normal"),
    ("ELEVADOR", ("ELEVADOR",), (2001.75, 773.0), "normal"),
    ("ACADEMIA", ("ACADEMIA", "A: 85,5 m²"), (1640.0, 703.0), "normal"),
    ("PISCINA", ("PISCINA", "A: 14,76 m²"), (922.0, 530.0), "normal"),
    ("SAUNA", ("SAUNA", "A: 4,62 m²"), (1121.0, 806.0), "normal"),
    ("VESTIÁRIO", ("VESTIÁRIO", "A: 6 m²"), (1396.0, 806.0), "normal"),
    ("CASA DE MÁQUINAS (15,07)", ("CASA DE MÁQUINAS", "A: 15,07 m²"), (1355.0, 990.0), "normal"),
]
DESCRICAO = {"texto": ("SOBE PARA O", "TÉRREO"), "x": 1138.0, "y": 447.0, "alinhar": "direita", "cor": (20, 20, 20)}
SEM_TEXTOS = False


def rotulos(Q, img, q=ROTULOS):
    import revisao_terreo_casac_1411 as R14
    import terreo_casaa_1011 as TA
    if SEM_TEXTOS:
        print("    rótulos e descrição da escada: fora (a final sem textos, entrada da opção B do 12K)")
        return img
    guarda = PE.ROTULOS
    PE.ROTULOS = q
    try:
        d = DESCRICAO
        out = TA.compor(img.astype(np.float32), PE.alfa_escada(d["texto"], d["x"], d["y"], d["alinhar"], img.shape[:2]),
                        d["cor"])
        lum = cv2.GaussianBlur(img.astype(np.float32).mean(axis=2), (0, 0), 3)
        claros = []
        for r in q:
            cor = PE.cor_rotulo(r, img, lum)
            if cor == PE.CLARO:
                claros.append(r[0])
            out = R14.desenhar_linhas(out, PE.linhas_rotulo(r), cor)
    finally:
        PE.ROTULOS = guarda
    print(f"    rótulos: {len(q)} no padrão (Inter, um corpo; o WC DCE 2 no corpo do WC DCE 1), claros sobre o fundo escuro "
          f"({', '.join(claros)}); \"AMBIENTE\" saiu; a descrição \"SOBE PARA O TÉRREO\" à esquerda da escada")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("base", base), ("fundo", fundo), ("bege", bege), ("travertino", travertino),
          ("travertino_limpo", travertino_limpo), ("marrom", marrom), ("escada", escada), ("piscina", piscina),
          ("academia", academia), ("sauna", sauna), ("wc_dce2", wc_dce2), ("chuveiros", chuveiros),
          ("vestiario", vestiario), ("dce", dce), ("elevador", elevador), ("cascata", cascata), ("portas", portas),
          ("perimetro", perimetro), ("rotulos", rotulos)]


def rodar(img, de=None, ate=None, cache=None):
    Q = FE.QuadroE("Subsolo")
    nomes = [n for n, _ in PASSOS]
    i0 = nomes.index(de) if de else 0
    i1 = nomes.index(ate) + 1 if ate else len(nomes)
    out = img
    if de and cache:
        out = cv2.imread(str(Path(cache) / f"{nomes[i0 - 1]}.png"))
    for n, f in PASSOS[i0:i1]:
        print(f"[{n}]")
        out = f(Q, out)
        if cache:
            Path(cache).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(Path(cache) / f"{n}.png"), out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--cache")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = antes_img()
    out = rodar(antes, a.de, a.ate, a.cache)
    cv2.imwrite(a.saida or str(FINAL), out)


if __name__ == "__main__":
    main()

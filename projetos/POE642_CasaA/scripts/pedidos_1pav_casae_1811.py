r"""Casa E, 1º Pavimento: o levantamento de 18/11 (padrões de todas as casas, notas do cliente e mobiliário pela biblioteca
da Casa E), aprovado pelo usuário ("1. Quartzito Aura 2. confirmo": o piso dos banhos fica no quartzito Aura e os
chuveiros vão ao quadrado de parede da biblioteca).

As folhas do levantamento: `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_1811_levantamento.jpg` e
`..._1811_mobiliario.jpg`. Parte da final do 1º Pavimento do commit `ANTES_COMMIT` e faz um passo por item, na ordem de
`PASSOS`, como no Subsolo (`pedidos_subsolo_casae_1811`):

1. `nublado` (itens 1 e 2): o Térreo esmaecido em volta e nos vazios refeito a partir do Térreo aprovado (a final de
   hoje, sem os rótulos, as descrições e as setas), no nublado dos 1º Pavimentos (`entorno_esmaecido.NUBLADO`), com o
   gramado do Térreo esfumaçado (12/11); sem o tracejado do limite do lote e com a margem branca (16/11, Casa D).
2. `escada` (item 3): os degraus cortados no tom da escada (o véu claro das Casas C e D, sem o branco); ▶ e D no
   degrau de cima.
3. `tracejados` e `rouparia` (itens 4 e 5): a rouparia sem o tracejado e sem a soleira (a porta de correr no bronze);
   as claraboias do banho master só com o retângulo cinza fino, sem o X.
4. `elevador` e `chuveiros` (itens 7 e 8): a cabine da biblioteca; os chuveiros dos banhos 1 a 4 e do master no
   quadrado de parede da biblioteca, com o braço cromado.
5. `banhos` (itens 6 e 12): as bancadas de quartzito com a cuba esculpida, as bacias Carrara, a bancada dupla, a
   banheira oval e o misturador do master.
6. `esquadrias` (item 9): os boxes no vidro claro com o fio bronze; as esquadrias e os batentes no bronze contornado.
7. `mobiliario` (item 12): as suítes, a sala íntima (o sofá fica), a copinha e a rouparia pela biblioteca da Casa E.
8. `rotulos` (item 10): os rótulos no padrão (Inter, um corpo, alinhados) e "DESCE PARA O / TÉRREO".

Uso (de POE642_CasaA/scripts/):
  python3 pedidos_1pav_casae_1811.py [--ate <passo>] [--de <passo>] [--cache <pasta>] [--saida <png>]
"""
import argparse
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casae as FE                    # noqa: E402

CASA = FE.CASA
R = CASA / "renders"
FINAL = R / "POE642_CasaE_PH_1Pavimento_v1_final.png"
TERREO = R / "POE642_CasaE_PH_Terreo_v1_final.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "b227fc4"
BIB = CASA / "biblioteca-objetos" / "03-primeiro-pavimento"
PAREDE = (80, 80, 80)


def u8(a):
    return np.clip(np.round(a), 0, 255).astype(np.uint8)


def antes_img():
    """A final do 1º Pavimento do commit de base (lida do git: a final em disco é regravada aqui)."""
    rel = FINAL.relative_to(RAIZ_GIT).as_posix()
    dados = subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"], capture_output=True,
                           check=True).stdout
    return cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR)


def quieto(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


_CACHE = {}


def paredes(Q, lim=0.3):
    if "par" not in _CACHE:
        _CACHE["par"] = FE.paredes_pdf(Q)
    return _CACHE["par"] > lim


# ----------------------------------------------------------------------------------------------------------------------
# 0. A base: a final sem os rótulos (eles voltam no fim, no padrão de 16/11)
def base(Q, img):
    limpa, _ = quieto(FE.sem_rotulos, "1Pavimento", img, novos=True)
    return limpa


# ----------------------------------------------------------------------------------------------------------------------
# 1. O Térreo esmaecido. A fonte: a final do Térreo de hoje, sem os textos (as caixas das linhas do JSON da Kalam, que
# tem todos os rótulos e as descrições das escadas, e as setas de fora da pegada, `SETAS_TERREO`, px) refeitos pelo
# entorno (inpaint), no nublado dos 1º Pavimentos. Fora da pegada do 1º Pavimento, o nublado novo inteiro (o tracejado do
# lote e a faixa de baixo saem: a margem branca do Térreo); nos vazios (escada e hall), o nublado novo vezes o que a
# final põe por cima dele (o X, as bordas, o vidro): a razão entre a final e o fundo dela sem esses traços (a mediana
# larga), só onde ela foge do fundo (`traco_tol`); no resto do vazio, o nublado novo puro.
NUBLADO_E = {"kalam": R / "POE642_CasaE_PH_Terreo_rotulos_kalam.json", "folga_px": (5, 4),
             "setas_px": [(765, 1342, 785, 1386),          # ◀ D da escada do deck
                          (2505, 1396, 2524, 1423),        # a seta da entrada, no hall
                          (2197, 975, 2219, 1017),         # ◀ S da escada interna
                          (1437, 423, 1458, 461)],         # ◀ D da escada do Subsolo
             "mediana_px": 11, "traco_tol": 0.07}


def terreo_sem_textos(q=NUBLADO_E):
    if "terreo" in _CACHE:
        return _CACHE["terreo"]
    t = cv2.imread(str(TERREO))
    m = np.zeros(t.shape[:2], np.uint8)
    fx, fy = q["folga_px"]
    for it in json.loads(Path(q["kalam"]).read_text(encoding="utf-8")):
        for _txt, cx, cy, meia_h, larg in it["linhas"]:
            cv2.rectangle(m, (int(cx - larg / 2 - fx), int(cy - meia_h - fy)), (int(cx + larg / 2 + fx), int(cy + meia_h + fy)),
                          1, -1)
    for x0, y0, x1, y1 in q["setas_px"]:
        cv2.rectangle(m, (x0, y0), (x1, y1), 1, -1)
    t = cv2.inpaint(t, m, 4, cv2.INPAINT_TELEA)
    _CACHE["terreo"] = t
    return t


def nublado(Q, img, q=NUBLADO_E):
    from entorno_esmaecido import pegada
    import opcoes_1pav_casae as O
    W = Q.W
    nub = FE._nublar(terreo_sem_textos(q), W)
    b = cv2.imread(str(O.BASE_CIMA))
    b = cv2.resize(b, (W, round(b.shape[0] * W / b.shape[1])), interpolation=cv2.INTER_AREA)
    peg = pegada(b, O.FORA)
    a = np.maximum(cv2.GaussianBlur(peg.astype(np.float32), (0, 0), 1.0), peg)
    ctx = (1 - a)[..., None]
    vaz = O.mascara_vazios(b) & (a > 0.5)
    f = img.astype(np.float32)
    out = f * (1 - ctx) + nub * ctx
    # nos vazios: o nublado novo vezes os traços da final
    # (a razão na luminância: no fundo verde de antes, a razão por canal tingia de ciano os traços cinza)
    fundo = cv2.medianBlur(img, q["mediana_px"]).astype(np.float32).mean(axis=2)
    raz = (f.mean(axis=2) / np.maximum(fundo, 1))[..., None]
    traco = np.abs(raz[..., 0] - 1) > q["traco_tol"]
    traco = cv2.dilate(traco.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    v = vaz & ~traco
    out[v] = nub[v]
    vt = vaz & traco
    out[vt] = (nub * raz)[vt]
    print(f"    Térreo esmaecido refeito com o Térreo de hoje: {int((ctx[..., 0] > 0.5).sum())} px em volta (sem o "
          f"tracejado do lote) e {int(vaz.sum())} px nos vazios ({int(vt.sum())} px de traços por cima)")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# 3. A escada (nota 5: "Não deixar os degraus cortados branco. Deixar transparente mas na mesma cor da escada. Exemplo
# casa C"; G1 e G2, como no Subsolo A: a seta e a descrição em todas as escadas): os degraus pela mesma rotina de antes
# (`final3840_casae.escada_e`, o sombreamento de descida), mas os de depois do corte só sob o véu claro das Casas C e D
# (38%, sem o desfoque), no tom da escada, sem o branco; ▶ (para onde se desce) e D no degrau de cima, à esquerda; a
# descrição "DESCE PARA O / TÉRREO" vai com os rótulos, à esquerda da escada.
ESCADA = {"nevoa": {"branco": 0.38, "sigma_px": 0.3}, "tri_tam": (13.0, 15.0), "tri_cor": (30, 30, 30),
          "tri_v": 0.30, "letra_v": 0.58}


def escada(Q, img, q=ESCADA):
    import terreo_casaa_1011 as TA
    import final3840_casaa_terreo as T
    e = dict(FE.ESCADA_1PAV_E, nevoa=q["nevoa"], letra=None)
    out = quieto(FE.escada_e, Q, img, e)
    ex0, ey0, ex1, ey1 = e["pdf"]
    cx = (ex0 + e["bocels"][0]) / 2
    (tx, ty) = Q.p2q(cx, ey0 + (ey1 - ey0) * q["tri_v"])
    (lx, ly) = Q.p2q(cx, ey0 + (ey1 - ey0) * q["letra_v"])
    o = TA.triangulo(out.astype(np.float32), TA.seta_tri(tx, ty, (1, 0), *q["tri_tam"]), q["tri_cor"])
    out = T.letra(Q, u8(o), "D", centro_q=(lx, ly))
    print(f"    escada: os degraus de depois do corte sob o véu de {q['nevoa']['branco']:.0%} no tom da escada (sem o "
          f"branco); ▶ e D no degrau de cima ({tx:.0f}, {ty:.0f})")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 4 e 5. Os tracejados (`final3840_casae.tracejados_pb_1p`, no cinza fino de 17/11, `revisao_1pav_casae_1711`): todos
# os grupos saem pela limpeza da rotina (o piso ao lado, no mesmo material); voltam o X dos vazios e do shaft e, nas
# claraboias do banho master (nota 2: "Padronizar para as outras plantas que tiverem claraboia"), só o retângulo, sem o
# X (o padrão da lista CDE). A rouparia não volta (nota 3: "sem o tracejado").
TRACEJADOS = {"sem": ("rouparia",), "so_retangulo": ("banho master: vaso", "banho master: box")}


def tracejados(Q, img, q=TRACEJADOS):
    import revisao_1pav_casae_1711 as RV
    guarda, pb = FE.TRACEJADOS_1P, FE.tracejados_pb_te

    def reto(t):
        return abs(t[2] - t[0]) < 0.3 or abs(t[3] - t[1]) < 0.3

    cfg = q

    def pb_filtrado(Q_, im, q=None, vaos=True, trechos=None):
        if trechos is not None:
            im = RV._faixa_vazios(Q_, im, trechos)
            trechos = [(n, [t for t in tr if n not in cfg["so_retangulo"] or reto(t)]) for n, tr in trechos
                       if n not in cfg["sem"]]
        return pb(Q_, im, q=q, vaos=vaos, trechos=trechos)
    FE.TRACEJADOS_1P = dict(guarda, larg_px=RV.LARG_PX, preto=RV.CINZA, branco=RV.CINZA_ESCURO)
    FE.tracejados_pb_te = pb_filtrado
    try:
        out = quieto(FE.tracejados_pb_1p, Q, img)
    finally:
        FE.TRACEJADOS_1P, FE.tracejados_pb_te = guarda, pb
    print("    tracejados: a rouparia sem o tracejado; as claraboias do banho master só com o retângulo cinza fino, sem o "
          "X; o X dos vazios e do shaft de novo no cinza fino")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 4b. A rouparia (nota 3: "sem o tracejado e sem a soleira"): o piso de madeira dela inteiro de novo (a limpeza do
# tracejado deixava manchas), num trecho limpo da circulação, com as réguas deitadas como as dela, e o vão da porta
# (a soleira do PDF, ARQ_PAREDE) na mesma madeira, sem emenda; a folha da porta de correr (a peça branca do PDF, junto
# ao vão) no bronze das portas das casas de máquinas do Subsolo (`pedidos_subsolo_casae_1811.BRONZE`: a madeira clara
# das portas some sobre o piso de madeira).
ROUPARIA = {"piso": (2083.5, 746.5, 2186.0, 811.3), "vao": (2105.8, 811.3, 2155.9, 820.6),
            "fonte": (1960, 832), "folha": (2115.9, 808.6, 2169.7, 811.0)}


def bronze(out, folha, semente):
    """A folha (px) no bronze escovado das portas das casas de máquinas do Subsolo: a cor, a borda escura, os fios no
    comprido e o brilho fino no meio (em `out`, no lugar)."""
    import correcoes_terreo_casab_1611 as CB
    import pedidos_subsolo_casae_1811 as PS
    import portas_casae_1711 as PC
    b, m = PS.BRONZE, CB.Mapa()
    x0, y0, x1, y1 = folha
    vert = (y1 - y0) > (x1 - x0)
    PC.folha(out, m, folha, vert, semente, dict(PC.FOLHA, madeira=b["madeira"], contorno=b["contorno"], veio=b["veio"]))
    bp = b["brilho_px"] / 2
    meio = (((x0 + x1) / 2 - bp, y0 + 0.8, (x0 + x1) / 2 + bp, y1 - 0.8) if vert else
            (x0 + 0.8, (y0 + y1) / 2 - bp, x1 - 0.8, (y0 + y1) / 2 + bp))
    CB.pintar(out, m, [(meio, "ret", b["brilho"], 0)])


def rouparia(Q, img, q=ROUPARIA):
    import correcoes_terreo_casab_1611 as CB
    out = img.astype(np.float32)
    par = paredes(Q, 0.5)
    H, W = par.shape
    m = np.zeros((H, W), np.float32)
    for x0, y0, x1, y1 in (q["piso"], q["vao"]):
        m = np.maximum(m, CB.alfa_ret((x0, y0, x1, y1), (H, W)))
    m[par] = 0
    X0, Y0 = int(np.floor(q["piso"][0])), int(np.floor(q["piso"][1]))
    X1, Y1 = int(np.ceil(q["piso"][2])), int(np.ceil(q["vao"][3]))
    fx, fy = q["fonte"]
    fonte = img[fy:fy + (Y1 - Y0), fx:fx + (X1 - X0)].astype(np.float32)
    a = m[Y0:Y1, X0:X1, None]
    out[Y0:Y1, X0:X1] = out[Y0:Y1, X0:X1] * (1 - a) + fonte * a
    out = u8(out)
    bronze(out, q["folha"], 1811)
    print("    rouparia: o piso de madeira inteiro de novo e o vão sem a soleira; a folha da porta de correr no bronze")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 7. O elevador: a cabine da biblioteca na caixa da cabine do PDF (INS_INSTALAÇÕES HIDRÁULICAS, a mesma do Subsolo).
ELEVADOR = {"cabine": (1960.0, 729.0, 2043.5, 808.9), "png": BIB / "elevador/cabine-elevador-e.png"}


def elevador(Q, img, q=ELEVADOR):
    import biblioteca_terreo_casaa_1211 as BT
    import pedidos_subsolo_casae_1811 as PS
    x0, y0, x1, y1 = q["cabine"]
    o = BT.pousar(img.astype(np.float32), PS.png(q["png"]), (x0 + x1) / 2 - 0.5, (y0 + y1) / 2 - 0.5, x1 - x0, y1 - y0,
                  0.0, [], Q.px_m)
    print("    elevador: a cabine da biblioteca na caixa do PDF")
    return u8(o)


# ----------------------------------------------------------------------------------------------------------------------
# 8. Os chuveiros (usuário: "2. confirmo": o quadrado de parede da biblioteca, nítido no 12K, como no Subsolo): a cabeça
# quadrada da biblioteca no quadrado do PDF (ARQ_LOUÇAS E METAIS), com o braço cromado até a parede e a canopla
# (`pedidos_subsolo_casae_1811.chuveiro`, aqui com a parede de qualquer lado); o desenho de antes sai (o piso do próprio
# box, `limpa`, deslocado `de`). No banho master, o PDF desenha os 2 de teto no meio do box (o vidro em cima, a
# claraboia embaixo): ficam no lugar do PDF, cada um com o braço até a parede do lado (0,45 e 0,52 m).
CHUVEIROS = [
    # (nome, cabeça px, parede ("cima"|"baixo"|"esq"|"dir"), coordenada da parede, limpa px, amostra limpa do piso px)
    ("banho 2", (2521.8, 583.5, 2533.6, 595.3), "cima", 567.1, (2515, 567, 2540, 602), (2502, 612, 2550, 660)),
    ("banho 1", (2521.8, 950.8, 2533.6, 962.6), "cima", 934.4, (2515, 934, 2540, 969), (2502, 979, 2550, 1027)),
    ("banho 4", (1432.7, 1176.5, 1444.5, 1188.3), "baixo", 1204.7, (1428, 1171, 1449, 1205), (1412, 1124, 1462, 1166)),
    ("banho 3", (1432.7, 1234.4, 1444.6, 1246.3), "cima", 1218.0, (1428, 1218, 1449, 1251), (1412, 1256, 1462, 1290)),
    ("banho master (esquerda)", (1856.2, 761.6, 1868.0, 773.4), "esq", 1835.0, (1848, 753, 1877, 783),
     (1878, 724, 1936, 754)),
    ("banho master (direita)", (1907.2, 761.6, 1919.0, 773.4), "dir", 1945.0, (1899, 753, 1928, 783),
     (1878, 724, 1936, 754)),
]
# o piso do box do master embaixo da claraboia (a limpeza do X deixou riscos claros), sob a linha dela: o do próprio box,
# de logo abaixo do vidro (`dy` px acima), já sem os chuveiros de antes
BOX_MASTER = {"limpa": (1836, 789, 1944, 812), "dy": -54}
CROMO = {"png": BIB / "banho-1/chuveiro-quadrado.png"}


def chuveiro(img, Q, cab, lado, parede, q=CROMO):
    import biblioteca_terreo_casaa_1211 as BT
    import correcoes_terreo_casab_1611 as CB
    import pedidos_subsolo_casae_1811 as PS
    c = PS.CROMO
    m = CB.Mapa()
    out = img.copy()
    x0, y0, x1, y1 = cab
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    e, w2 = 0.35, 0.75
    if lado in ("esq", "dir"):
        a, b = (parede, cx) if lado == "esq" else (cx, parede)
        pc = parede if lado == "dir" else parede + 1.2
        braco = (a, cy - w2, b, cy + w2)
        can = (pc - 1.2, cy - 2.0, pc, cy + 2.0)
        brilho = (a, cy - w2 + 0.15, b, cy - w2 + 0.6)
        bb = (a, cy - w2 - e, b, cy + w2 + e)
        cb = (can[0] - e, can[1] - e, can[2] + e, can[3] + e)
    else:
        a, b = (parede, cy) if lado == "cima" else (cy, parede)
        pc = parede if lado == "baixo" else parede + 1.2
        braco = (cx - w2, a, cx + w2, b)
        can = (cx - 2.0, pc - 1.2, cx + 2.0, pc)
        brilho = (cx - w2 + 0.15, a, cx - w2 + 0.6, b)
        bb = (cx - w2 - e, a, cx + w2 + e, b)
        cb = (can[0] - e, can[1] - e, can[2] + e, can[3] + e)
    CB.pintar(out, m, [(bb, "ret", c["borda"], 0), (braco, "ret", c["cromo"], 0), (brilho, "ret", c["brilho"], 0),
                       (cb, "ret", c["borda"], 0), (can, "ret", c["cromo"], 0)])
    o = out.astype(np.float32)
    BT.pousar(o, PS.png(q["png"]), cx - 0.5, cy - 0.5, x1 - x0, y1 - y0, 0.0, c["sombra"], Q.px_m)
    out = u8(o)
    CB.pintar(out, m, [(cab, "contorno", c["borda"], 0.4)])
    return out


def limpar_piso(Q, out, ret, amostra, nao_luz=None):
    """O piso do retângulo (px) refeito pela amostra limpa do mesmo piso, na luz de em volta
    (`alternativa1_terreo_casad_1611.refazer`); as paredes ficam. `nao_luz` (px): retângulos que não dão a luz (a
    floreira, o vidro)."""
    import alternativa1_terreo_casad_1611 as A1
    import regras_terreo_casab_1311 as RT
    par = paredes(Q, 0.5)
    H, W = par.shape
    m = np.zeros((H, W), bool)
    x0, y0, x1, y1 = ret
    m[int(np.floor(y0)):int(np.ceil(y1)), int(np.floor(x0)):int(np.ceil(x1))] = True
    ficam = RT.dilatar(par, 1)
    for a0, b0, a1, b1 in (nao_luz or []):
        ficam[int(b0):int(b1), int(a0):int(a1)] = True
    # só o próprio ambiente dá a luz: o que fica do outro lado das paredes (a varanda, o Térreo esmaecido) sai
    X0, Y0 = max(int(x0) - 24, 0), max(int(y0) - 24, 0)
    X1, Y1 = min(int(np.ceil(x1)) + 24, W), min(int(np.ceil(y1)) + 24, H)
    livre = ~RT.dilatar(par, 1)[Y0:Y1, X0:X1]
    n, rot = cv2.connectedComponents(livre.astype(np.uint8))
    dentro = m[Y0:Y1, X0:X1] & livre
    if dentro.any():
        rots = np.bincount(rot[dentro], minlength=n)
        rots[0] = 0
        ficam[Y0:Y1, X0:X1] |= ~np.isin(rot, np.nonzero(rots)[0])
    return A1.refazer(out, m & ~par, [(None, amostra)], ficam=ficam)


def chuveiros(Q, img, q=CHUVEIROS):
    out = img.copy()
    for nome, cab, lado, parede, limpa, amostra in q:
        out = limpar_piso(Q, out, limpa, amostra)
    b = BOX_MASTER
    x0, y0, x1, y1 = b["limpa"]
    par = paredes(Q, 0.5)
    sub = out[y0 + b["dy"]:y1 + b["dy"], x0:x1].copy()
    ok = ~par[y0:y1, x0:x1] & ~par[y0 + b["dy"]:y1 + b["dy"], x0:x1]
    out[y0:y1, x0:x1][ok] = sub[ok]
    for nome, cab, lado, parede, limpa, amostra in q:
        out = chuveiro(out, Q, cab, lado, parede)
    print(f"    chuveiros: {', '.join(c[0] for c in q)} com a cabeça quadrada da biblioteca, o braço cromado e a canopla")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 6 e 12 (banhos). As peças da biblioteca (03-primeiro-pavimento) nos retângulos do PDF (ARQ_BANCADAS e ARQ_LOUÇAS E
# METAIS): nos banhos 1 a 4, a bancada de quartzito Aura com a cuba esculpida (nota 6: "as cubas mais marcadas", a borda
# e a sombra curta), a cuba no lugar da do PDF e a bancada esticada dos lados sem esticar a pedra
# (`mobiliario_terreo_casae_1611.esticada`); a bacia Carrara com a caixa contra a parede. No master, a bancada dupla da
# E com as 2 cubas nos lugares do PDF (`bancada_cubas`), a banheira oval da E, o misturador de piso junto à cabeceira e
# a bacia Carrara (a linha da claraboia de novo por cima dela). O piso de em volta, pela amostra limpa do próprio banho.
def ler(rel):
    P = cv2.imread(str(BIB / f"{rel}.png"), cv2.IMREAD_UNCHANGED)
    if P.shape[2] == 3:
        P = np.dstack([P, np.full(P.shape[:2], 255, np.uint8)])
    P = P.astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 8)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def bancada_cubas(P, L, D, cols, centros, ss=4, borda=0.04):
    """A bancada P (BGRA, as torneiras em cima) com L x D px (x ss): as cubas de P (`cols`, frações da largura, que não
    esticam) com os centros em `centros` (frações de L, da esquerda do PNG); a pedra lisa de entre elas repetida em
    espelho no resto, as beiras de P (`borda`) nas pontas."""
    H, W = P.shape[:2]
    Qp = cv2.resize(P, (max(1, round(W * D * ss / H)), round(D * ss)), interpolation=cv2.INTER_AREA)
    W2 = Qp.shape[1]
    b = max(1, round(borda * W2))
    c = [(round(a * W2), round(z * W2)) for a, z in cols]
    liso = Qp[:, c[0][1]:c[1][0]] if len(c) > 1 else Qp[:, b:c[0][0]]
    Lt = round(L * ss)
    rep = np.concatenate([liso, liso[:, ::-1]], axis=1)
    out = np.tile(rep, (1, Lt // rep.shape[1] + 2, 1))[:, :Lt].copy()
    out[:, :b] = Qp[:, :b]
    out[:, Lt - b:] = Qp[:, W2 - b:]
    for (c0, c1), f in zip(c, centros):
        w = c1 - c0
        x0 = int(round(f * Lt - w / 2))
        x0 = min(max(x0, b), Lt - b - w)
        out[:, x0:x0 + w] = Qp[:, c0:c1]
    return np.ascontiguousarray(out)


BANHOS = {
    # bancada px, centro da cuba (x ou y px), frente da bancada, bacia px, frente da bacia, amostra do piso px
    "banho 2": {"bancada": (2360.0, 566.5, 2438.3, 603.3), "cuba": 2418.4, "frente": (0, 1),
                "bacia": (2454.6, 566.5, 2475.6, 597.2), "bacia_frente": (0, 1), "amostra": (2380, 620, 2470, 660),
                "bacia_antes": (2444, 566, 2487, 612)},
    "banho 1": {"bancada": (2360.0, 933.7, 2438.3, 970.5), "cuba": 2418.4, "frente": (0, 1),
                "bacia": (2454.6, 933.7, 2475.6, 964.4), "bacia_frente": (0, 1), "amostra": (2380, 987, 2470, 1027),
                "bacia_antes": (2444, 933, 2487, 979)},
    "banho 4": {"bancada": (1528.4, 1172.4, 1604.7, 1205.4), "cuba": 1547.95, "frente": (0, -1),
                "bacia": (1491.2, 1174.7, 1512.3, 1205.4), "bacia_frente": (0, -1), "amostra": (1480, 1122, 1600, 1162),
                "bacia_antes": (1480, 1160, 1523, 1205)},
    "banho 3": {"bancada": (1528.4, 1217.3, 1604.7, 1250.4), "cuba": 1547.95, "frente": (0, 1),
                "bacia": (1490.9, 1217.3, 1512.0, 1248.0), "bacia_frente": (0, 1), "amostra": (1480, 1262, 1600, 1300),
                "bacia_antes": (1480, 1217, 1523, 1262)},
}
BANCADA_SIMPLES = {"png": "banho-1/bancada-simples-quartzito-aura", "cols": (0.255, 0.71)}
MASTER = {"bancada": (1910.1, 445.0, 1945.0, 593.0), "cubas": (491.25, 552.65), "png": "banho-master/bancada-master-e",
          "cols": ((0.15, 0.415), (0.605, 0.85)), "banheira": (1799.8, 470.8, 1853.3, 554.8),
          "misturador": (1800.0, 458.5, 9.0, 13.0), "bacia": (1774.2, 780.6, 1795.3, 811.3),
          "banheira_antes": (1784, 447, 1868, 601),         # a de antes era maior que a do PDF
          "floreira": (1730, 440, 1784, 610), "vaso_antes": (1749, 766, 1818, 812), "linha": (1745, 778, 1822, 796),
          "amostra": (1770, 615, 1890, 700), "amostra_vaso": (1758, 732, 1814, 764)}


def _limpa(Q, out, ret, folga, amostra):
    x0, y0, x1, y1 = ret
    return limpar_piso(Q, out, (x0 - folga, y0 - folga, x1 + folga, y1 + folga), amostra)


def banhos(Q, img, q=BANHOS, m=MASTER):
    import mobiliario_terreo_casac_1311 as MB
    import mobiliario_terreo_casae_1611 as MBE
    par = paredes(Q, 0.5)
    out = img.copy()
    Pb = ler("banho-1/bacia-carrara")
    Ps = ler(BANCADA_SIMPLES["png"])
    for nome, b in q.items():
        x0, y0, x1, y1 = b["bancada"]
        out = _limpa(Q, out, b["bancada"], 3, b["amostra"])
        out = _limpa(Q, out, b["bacia_antes"], 0, b["amostra"])
        L, D = x1 - x0, y1 - y0
        pos = (b["cuba"] - x0) / L
        if b["frente"] == (0, -1):
            pos = 1 - pos
        P = MBE.esticada(Ps, L, D, BANCADA_SIMPLES["cols"], pos)
        out = MBE.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, L, D, MB.frente(b["frente"]), "baixa", par)
        x0, y0, x1, y1 = b["bacia"]
        out = MBE.pousar(out, Pb, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente(b["bacia_frente"]), "baixa",
                         par)
    # o master
    out = _limpa(Q, out, m["bancada"], 3, m["amostra"])
    out = limpar_piso(Q, out, m["banheira_antes"], m["amostra"], nao_luz=[m["floreira"]])
    mx, my, mw, mh = m["misturador"]
    x0, y0, x1, y1 = m["bancada"]
    L, D = y1 - y0, x1 - x0
    P = bancada_cubas(ler(m["png"]), L, D, m["cols"], [(c - y0) / L for c in m["cubas"]])
    out = MBE.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, L, D, MB.frente((-1, 0)), "baixa", par)
    x0, y0, x1, y1 = m["banheira"]
    out = MBE.pousar(out, ler("banho-master/banheira-oval-master-e"), (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0,
                     MB.frente((1, 0)), "movel", par)
    out = MBE.pousar(out, ler("banho-master/misturador-piso-banheira-render"), mx, my, mw, mh, MB.frente((0, 1)),
                     "baixa", par)
    # a bacia, sob a linha da claraboia (de novo por cima dela)
    out = limpar_piso(Q, out, m["vaso_antes"], m["amostra_vaso"])
    x0, y0, x1, y1 = m["bacia"]
    out = MBE.pousar(out, Pb, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente((0, -1)), "baixa", par)
    out = linha_claraboia(Q, out, m["linha"])
    print(f"    banhos: {', '.join(q)} com a bancada de quartzito e a cuba esculpida da biblioteca e a bacia Carrara; "
          "master com a bancada dupla da E (as 2 cubas no lugar do PDF), a banheira oval, o misturador de piso e a bacia")
    return out


def linha_claraboia(Q, out, caixa):
    """A linha tracejada da claraboia do vaso do master de novo, só dentro da `caixa` (px): sobre a bacia nova."""
    import revisao_1pav_casae_1711 as RV
    trechos = [(n, [t for t in tr if abs(t[3] - t[1]) < 0.3]) for n, tr in FE._tracos_1p(Q)
               if n == "banho master: vaso"]
    q = dict(FE.TRACEJADOS_1P, larg_px=RV.LARG_PX, preto=RV.CINZA, branco=RV.CINZA_ESCURO)
    com = quieto(FE.tracejados_pb_te, Q, out, q=q, trechos=trechos)
    x0, y0, x1, y1 = (int(round(v)) for v in caixa)
    res = out.copy()
    res[y0:y1, x0:x1] = com[y0:y1, x0:x1]
    return res


# ----------------------------------------------------------------------------------------------------------------------
# 9. Os boxes, os batentes e as esquadrias, como no Subsolo de 18/11 (`pedidos_subsolo_casae_1811.ESQUADRIAS` e
# `VIDRO_C`; usuário: "DEVEMOS FAZER UM CONTORNO ESCURO ... RECOMENDO O TOM BRONZE DAS ESQUADRIAS"):
# - os boxes dos banhos 1 a 4 e do master: o vidro do PDF (o tracejado duplo de ARQ_LOUÇAS E METAIS), de parede a
#   parede, no vidro claro com o fio e os perfis das pontas no bronze; os traços do box de antes (2 a 3 linhas cinza
#   em volta) saem, com o piso do próprio banho;
# - as peças brancas do PDF (ARQ_PAREDE): nos grupos das esquadrias (as portas de correr das varandas, as janelas dos
#   banhos e da floreira, as portas do banho master e a da sala íntima), o vão no plano da parede numa cor só (a
#   mediana dele, a soleira de antes, sem os traços cinza), os vidros no vidro claro com a linha do meio e os marcos no
#   bronze, tudo contornado no bronze escuro; as folhas de correr do banho master na madeira das portas; fora deles,
#   os batentes das portas de giro (a peça na espessura da parede e as guarnições) no bronze contornado, com a sombra
#   curta das guarnições. As folhas de giro ficam (já no padrão da Casa D); o guarda-corpo do vazio do hall, o
#   elevador, a rouparia e os nichos dos boxes ficam.
BRANCOS_PDF = {"camada": "ARQ_PAREDE", "area": (1300, 500, 2800, 1700)}
GRUPOS_ESQ = [
    # (nome, caixa px)
    ("porta de correr da suíte master", (1394, 592, 1409, 872)),
    ("porta de correr da suíte 4", (1394, 902, 1409, 1096)),
    ("janela do banho 4", (1394, 1132, 1409, 1194)),
    ("janela do banho 3", (1394, 1231, 1409, 1293)),
    ("porta de correr da suíte 3", (1394, 1326, 1409, 1520)),
    ("janela do banho 2", (2556, 589, 2567, 651)),
    ("janela do banho 1", (2556, 956, 2567, 1018)),
    ("porta de correr da suíte 2", (2478, 693, 2490, 911)),
    ("porta de correr da suíte 1", (2478, 1061, 2490, 1278)),
    ("janela da floreira", (1738, 487, 1749, 529)),
    ("porta do banho master (suíte)", (1732, 600, 1749, 674)),
    ("porta do banho master (closet)", (1944, 598, 1955, 673)),
    # a da sala íntima: o vão dela era quase todo o vidro cinza do render; a soleira no bege das portas das varandas
    ("porta da sala íntima", (1747, 1440, 1833, 1451), "porta de correr da suíte 3"),
]
# as folhas de correr (as peças de 2,4 px do PDF) na madeira das portas
FOLHAS_CORRER = [(1739.3, 610.4, 1741.7, 676.1), (1954.3, 587.6, 1956.7, 623.4), (1954.3, 647.3, 1956.7, 683.1)]
# o guarda-corpo do vazio do hall e o da varanda de baixo (as peças brancas do PDF, índices), fora
FICAM_PDF = {92, 107, 108, 109, 110, 135, 161, 162, 163, 191, 214, 215, 216, 217, 237, 238, 239, 240, 241, 242}
BOXES = [
    # (nome, vidro px, faixa dos traços de antes px ou None, deslocamento da fonte do piso (dx, dy) px)
    # nos banhos 1 e 2 o box de antes tinha mais 2 linhas (as folhas de correr do render, a 14 e a 4 px do vidro do
    # PDF): a faixa delas, abaixo da bacia, com o piso de 30 px à esquerda; nos banhos 3 e 4 e no master o vidro novo
    # cobre o de antes
    ("banho 2", (2492.3, 567.1, 2495.3, 673.4), (2476, 603, 2492, 673), (-30, 0)),
    ("banho 1", (2492.7, 934.3, 2495.7, 1040.6), (2476, 970, 2492, 1040), (-30, 0)),
    ("banho 4", (1469.8, 1116.4, 1472.8, 1204.8), None, None),
    ("banho 3", (1470.0, 1217.9, 1473.0, 1306.3), None, None),
    ("banho master", (1835.1, 715.8, 1938.4, 718.8), None, None),
]


def copiar_piso(out, faixa, desloc, suave=1.5):
    """A `faixa` px com o piso de `desloc` px ao lado, com as bordas suaves (`suave` px)."""
    x0, y0, x1, y1 = faixa
    dx, dy = desloc
    h, w = y1 - y0, x1 - x0
    a = np.ones((h, w), np.float32)
    for k in range(int(np.ceil(suave))):
        f = (k + 1) / (suave + 1)
        a[k, :] = np.minimum(a[k, :], f)
        a[-1 - k, :] = np.minimum(a[-1 - k, :], f)
        a[:, k] = np.minimum(a[:, k], f)
        a[:, -1 - k] = np.minimum(a[:, -1 - k], f)
    out = out.copy()
    reg = out[y0:y1, x0:x1].astype(np.float32)
    src = out[y0 + dy:y1 + dy, x0 + dx:x1 + dx].astype(np.float32)
    out[y0:y1, x0:x1] = u8(reg * (1 - a[..., None]) + src * a[..., None])
    return out


ESQ = {"bronze": (74, 106, 139), "contorno": (44, 66, 90), "contorno_px": 0.55, "vidro": (220, 224, 227),
       "meio": (150, 156, 162), "meio_px": 0.25, "sombra": 0.16}


def _brancos(Q, q=BRANCOS_PDF):
    if "brancos" in _CACHE:
        return _CACHE["brancos"]
    X0, Y0, X1, Y1 = q["area"]
    lst = []
    for i, d in enumerate(Q.desenhos):
        if not str(d.get("layer", "")).startswith(q["camada"]) or d["type"] != "f":
            continue
        f = d.get("fill")
        if not f or tuple(round(v, 2) for v in f) != (1.0, 1.0, 1.0):
            continue
        r = d["rect"]
        (a, b), (c, e) = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        x0, y0, x1, y1 = min(a, c), min(b, e), max(a, c), max(b, e)
        if x1 < X0 or x0 > X1 or y1 < Y0 or y0 > Y1:
            continue
        lst.append((i, (x0, y0, x1, y1)))
    _CACHE["brancos"] = lst
    return lst


def _dentro(r, c):
    return r[0] >= c[0] and r[1] >= c[1] and r[2] <= c[2] and r[3] <= c[3]


def _juntar(rs, tol=0.3):
    """Os retângulos que se tocam, unidos (as metades de 1,5 px de cada vidro)."""
    rs = [list(r) for r in rs]
    mud = True
    while mud:
        mud = False
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                a, b = rs[i], rs[j]
                if a[0] <= b[2] + tol and b[0] <= a[2] + tol and a[1] <= b[3] + tol and b[1] <= a[3] + tol:
                    rs[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    rs.pop(j)
                    mud = True
                    break
            if mud:
                break
    return [tuple(r) for r in rs]


def esquadrias(Q, img, q=ESQ):
    import correcoes_terreo_casab_1611 as CB
    import pedidos_subsolo_casae_1811 as PS
    import portas_casae_1711 as PC
    m = CB.Mapa()
    out = img.copy()
    # os boxes
    for nome, vidro, faixa, desloc in BOXES:
        if faixa is not None:
            out = copiar_piso(out, faixa, desloc)
        v = PS.VIDRO_C
        CB.sombra(out, m, vidro, v["sombra"], dx=-0.8, dy=0.8, sigma=0.8)
        x0, y0, x1, y1 = vidro
        vert = (y1 - y0) > (x1 - x0)
        pp = v["perfil_px"]
        pontas = [(x0, y0, x1, y0 + pp), (x0, y1 - pp, x1, y1)] if vert else [(x0, y0, x0 + pp, y1), (x1 - pp, y0, x1, y1)]
        CB.pintar(out, m, [(vidro, "ret", v["vidro"], 0), (vidro, "contorno", v["fio"], v["fio_px"])] +
                  [(r, "ret", v["perfil"], 0) for r in pontas])
    # as esquadrias, grupo por grupo
    brancos = [(i, r) for i, r in _brancos(Q) if i not in FICAM_PDF]
    usados = set()
    folhas = [r for r in FOLHAS_CORRER]
    n_vid = n_mar = 0
    cores = {}
    for nome, caixa, *soleira_de in GRUPOS_ESQ:
        pecas = [(i, r) for i, r in brancos if _dentro(r, caixa)]
        usados |= {i for i, _ in pecas}
        pecas = [(i, r) for i, r in pecas if not any(_dentro(r, (f[0] - 0.2, f[1] - 0.2, f[2] + 0.2, f[3] + 0.2))
                                                    for f in folhas)]
        vaos = [r for _, r in pecas if min(r[2] - r[0], r[3] - r[1]) >= 8.5 and max(r[2] - r[0], r[3] - r[1]) >= 20]
        vidros = [r for _, r in pecas if r not in vaos and min(r[2] - r[0], r[3] - r[1]) <= 4.6
                  and max(r[2] - r[0], r[3] - r[1]) >= 20]
        marcos = [r for _, r in pecas if r not in vaos and r not in vidros]
        if not vaos:
            rs = [r for _, r in pecas]
            vaos = [(min(r[0] for r in rs), min(r[1] for r in rs), max(r[2] for r in rs), max(r[3] for r in rs))]
        pintar = []
        for x0, y0, x1, y1 in vaos:
            sub = out[int(round(y0)):int(round(y1)), int(round(x0)):int(round(x1))].reshape(-1, 3).astype(np.float32)
            lum = sub.mean(axis=1)
            cor = tuple(float(c) for c in np.median(sub[lum >= np.percentile(lum, 40)], axis=0))
            cor = cores[soleira_de[0]] if soleira_de else cor
            cores.setdefault(nome, cor)
            pintar.append(((x0, y0, x1, y1), "ret", cor, 0))
        for r in _juntar(vidros):
            x0, y0, x1, y1 = r
            vert = (y1 - y0) > (x1 - x0)
            if vert:
                xm = (x0 + x1) / 2
                meio = (xm - q["meio_px"] / 2, y0 + 0.6, xm + q["meio_px"] / 2, y1 - 0.6)
            else:
                ym = (y0 + y1) / 2
                meio = (x0 + 0.6, ym - q["meio_px"] / 2, x1 - 0.6, ym + q["meio_px"] / 2)
            pintar += [(r, "ret", q["vidro"], 0), (meio, "ret", q["meio"], 0), (r, "contorno", q["contorno"], q["contorno_px"])]
            n_vid += 1
        for r in marcos:
            pintar += [(r, "ret", q["bronze"], 0), (r, "contorno", q["contorno"], q["contorno_px"])]
            n_mar += 1
        pintar += [(r, "contorno", q["contorno"], q["contorno_px"]) for r in vaos]
        CB.pintar(out, m, pintar)
    for i, f in enumerate(folhas):
        PC.folha(out, m, f, True, 1900 + i)
    # os batentes das portas de giro: as peças fora dos grupos, no tamanho do batente (a da espessura da parede, ~2,1 x
    # 9 px) e das guarnições (~1,2 x 4,2 px)
    bat = []
    for i, r in brancos:
        if i in usados:
            continue
        a, b = sorted((r[2] - r[0], r[3] - r[1]))
        if (a <= 1.3 and b <= 4.5) or (1.9 <= a <= 2.6 and 8.5 <= b <= 9.6):
            bat.append(r)
    for r in bat:
        a = min(r[2] - r[0], r[3] - r[1])
        if a <= 1.3:
            CB.sombra(out, m, r, q["sombra"], dx=-0.6, dy=0.6, sigma=0.6)
    CB.pintar(out, m, [p for r in bat for p in ((r, "ret", q["bronze"], 0), (r, "contorno", q["contorno"], q["contorno_px"]))])
    print(f"    esquadrias: {len(BOXES)} boxes no vidro claro com o fio bronze; {len(GRUPOS_ESQ)} esquadrias ({n_vid} vidros, "
          f"{n_mar} marcos) e {len(bat)} peças de batente no bronze contornado; {len(folhas)} folhas de correr na madeira")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 12. O mobiliário pela biblioteca da Casa E (a folha 2 do levantamento), nos retângulos do PDF (ARQ_LAYOUT
# HUMANIZAÇÃO): nas suítes, as peças de antes (a cama, o tapete, os criados, o banco, a cadeira da escrivaninha; na
# master, também a poltrona e o pufe) saem com o piso de madeira (`limpa`, a amostra limpa da circulação), e entram o
# tapete, a cama (king na master), os 2 criados, o banco de pé de cama de 17/11 (`revisao_1pav_casae_1711.BANCOS`), a
# cadeira da bancada e, na master, a poltrona e o criado redondo no lugar do pufe. Na master, a cama de antes passava
# 0,7 m do PDF (o banco ia mais para baixo): tudo vai para o lugar do PDF. Na sala íntima, o tapete (por baixo do
# sofá), a mesa de centro redonda, a mesa lateral (por baixo dela, como as do PDF) e a poltrona; o sofá fica: o L da
# biblioteca não cabe no do PDF (a chaise de 0,84 x 2,0 m, a da biblioteca é larga e curta) e o de antes já é o mesmo
# modelo, no lugar do PDF. Na copinha, o tampo da E com a cuba Franke e o armário; na rouparia, a estante aberta e o
# módulo de nichos no L do PDF.
# Depois (usuário: "troque os bancos, que estão em frente as camas por outro modelo da biblioteca"): o banco K3 da
# biblioteca (`bancos-pe-de-cama-propostas/banco-k3`: linho off-white com a moldura de nogueira e os rolos nas pontas,
# que se destaca do tapete bege) no lugar do K4 de couro caramelo; ("as cadeiras de escritório devem estar parcialmente
# sob as mesas") cada cadeira 4 px (0,07 m) mais para dentro da escrivaninha, ~40% dela sob o tampo: o tampo da final de
# antes (`mesa`) volta por cima dela, com a sombra curta da borda; a limpeza da cadeira de antes fica fora do tampo
# (nas suítes 3 e 4 a borda do tampo que a cadeira de antes cobria vem do próprio tampo, `mesa_reparo` (px, dy)).
BANCO_PNG = "banco-k3.png"
MESA_SOMBRA = {"forca": 0.26, "sigma": 1.0, "d": 1.2}
MADEIRA = (1770, 830, 1980, 900)
SUITES = {
    # (`limpa`: a última inclui o resto do rótulo de antes, sob o banco antigo; `cortina`: não dá a luz do piso)
    "suíte master": {"limpa": [(1452, 560, 1684, 846), (1425, 752, 1536, 866)], "cama": ((1504, 567, 1628, 697), "king"),
                     "cortina": (1398, 552, 1426, 900),
                     "tapete": (1461, 612, 1670, 749), "banco": ((1504, 700, 1628, 724), 0),
                     "criados": [(1465, 568, 1501, 604), (1632, 568, 1668, 604)], "frente": (0, 1),
                     "poltrona": ((1459.0, 824.0), 52.0, (1, -1)), "redondo": (1483, 758, 1526, 802)},
    "suíte 2": {"limpa": [(2304, 678, 2469, 849), (2262, 727, 2292, 776)], "cama": ((2352, 683, 2434, 801), "casal"),
                "cortina": (2468, 670, 2492, 860),
                "tapete": (2315, 722, 2468, 842), "banco": ((2352, 806, 2434, 830), 0),
                "criados": [(2319, 683, 2349, 713), (2438, 683, 2467, 713)], "frente": (0, 1),
                "cadeira": ((2248, 733, 2283, 770), (-1, 0)), "mesa": (2226, 683, 2261.7, 823)},
    "suíte 1": {"limpa": [(2304, 1045, 2469, 1216), (2262, 1094, 2292, 1143)], "cama": ((2352, 1050, 2434, 1168), "casal"),
                "cortina": (2468, 1037, 2492, 1227),
                "tapete": (2315, 1086, 2468, 1206), "banco": ((2352, 1173, 2434, 1197), 0),
                "criados": [(2319, 1050, 2349, 1080), (2438, 1050, 2467, 1080)], "frente": (0, 1),
                "cadeira": ((2248, 1100, 2283, 1137), (-1, 0)), "mesa": (2226, 1050, 2261.7, 1190)},
    "suíte 4": {"limpa": [(1425, 887, 1600, 1062), (1671, 936, 1703, 985)], "cama": ((1466, 892, 1548, 1010), "casal"),
                "cortina": (1398, 880, 1426, 1070),
                "tapete": (1427, 934, 1595, 1054), "banco": ((1466, 1015, 1548, 1039), 0),
                "criados": [(1433, 892, 1463, 922), (1552, 892, 1582, 922)], "frente": (0, 1),
                "cadeira": ((1681, 942, 1717, 979), (1, 0)), "mesa": (1703.3, 892, 1739, 1032),
                "mesa_reparo": ((1703, 936, 1711, 986), -44)},
    "suíte 3": {"limpa": [(1425, 1360, 1600, 1536), (1671, 1434, 1703, 1483)], "cama": ((1470, 1413, 1552, 1531), "casal"),
                "cortina": (1398, 1352, 1426, 1545),
                "tapete": (1427, 1368, 1595, 1488), "banco": ((1470, 1384, 1552, 1408), 180),
                "criados": [(1437, 1501, 1466, 1531), (1555, 1501, 1585, 1531)], "frente": (0, -1),
                "cadeira": ((1681, 1440, 1717, 1477), (1, 0)), "mesa": (1703.3, 1390, 1739, 1531),
                "mesa_reparo": ((1703, 1434, 1711, 1484), -44)},
}
SALA_INTIMA = {"tapete": (1876, 1235, 2115, 1384), "sofa": [(1867, 1215, 1917, 1334), (1917, 1215, 2076, 1265)],
               "sofa_folga": 3, "poltrona_antes": (2113, 1228, 2158, 1345), "poltrona": (2084, 1280, 2140, 1333),
               "mesa": (1956, 1299, 2016, 1359), "lateral": (1997, 1314, 2039, 1356),
               # (usuário: "corrija a representação dessa mesa lateral, da sala íntima", a redonda do render junto ao
               # braço do sofá, borrada e com a sombra escura em volta): sai, com o piso de madeira (fora do sofá e do
               # tapete), e entra a mesa redonda de carvalho da biblioteca, a da mesa de centro, no mesmo lugar
               "lateral_sofa_antes": (2077, 1199, 2120, 1235), "lateral_sofa": (2097.5, 1218.5, 33.0)}
COPINHA = {"tampo": (1888.3, 916.2, 2053.4, 951.6), "cuba": (2034.4, 931.2, 30.0, 24.0),
           "armario": (2053.4, 916.2, 2216.7, 951.6)}
ROUPARIA_MOVEIS = {"estante": (2082.3, 715.8, 2216.7, 745.6), "nichos": (2186.8, 745.6, 2216.7, 807.7)}


def repetida(P, L, D, ss=4):
    """P (BGRA) na profundidade D, repetida em espelho até o comprimento L (px, x ss)."""
    H, W = P.shape[:2]
    Qp = cv2.resize(P, (max(1, round(W * D * ss / H)), round(D * ss)), interpolation=cv2.INTER_AREA)
    rep = np.concatenate([Qp, Qp[:, ::-1]], axis=1)
    Lt = round(L * ss)
    return np.ascontiguousarray(np.tile(rep, (1, Lt // rep.shape[1] + 2, 1))[:, :Lt])


def mobiliario(Q, img):
    import mobiliario_terreo_casac_1311 as MB
    import mobiliario_terreo_casae_1611 as MBE
    import revisao_1pav_casae_1711 as RV
    par = paredes(Q, 0.5)
    out = img.copy()

    def pos(o, P, r, frente, sombra, troca=False):
        x0, y0, x1, y1 = r
        w, h = (y1 - y0, x1 - x0) if troca else (x1 - x0, y1 - y0)
        return MBE.pousar(o, P, (x0 + x1) / 2, (y0 + y1) / 2, w, h, MB.frente(frente), sombra, par)
    import correcoes_terreo_casab_1611 as CB
    antes = img.copy()
    bancos = []
    for nome, s in SUITES.items():
        for r in s["limpa"]:
            out = limpar_piso(Q, out, r, MADEIRA, nao_luz=[s["cortina"]])
        pasta = "suite-master" if nome == "suíte master" else "suite-1"
        out = pos(out, ler(f"{pasta}/tapete"), s["tapete"], (0, 1), None)
        r, tipo = s["cama"]
        out = pos(out, ler(f"{pasta}/cama-king-master-e" if tipo == "king" else f"{pasta}/cama-casal-e"), r,
                  s["frente"], "movel")
        Pc = ler(f"{pasta}/criado-lateral-e")
        for r in s["criados"]:
            out = pos(out, Pc, r, s["frente"], "movel")
        bancos.append((nome, *s["banco"]))
        if "cadeira" in s:
            r, fr = s["cadeira"]
            if "mesa_reparo" in s:
                (x0, y0, x1, y1), dy = s["mesa_reparo"]
                antes[y0:y1, x0:x1] = antes[y0 + dy:y1 + dy, x0:x1]
            out = pos(out, ler(f"{pasta}/cadeira-bancada-suite"), r, fr, "movel", troca=fr[0] != 0)
            # o tampo da escrivaninha por cima da cadeira, com a sombra curta da borda nela
            x0, y0, x1, y1 = s["mesa"]
            cy0, cy1 = int(r[1]) - 6, int(np.ceil(r[3])) + 6
            ms = MESA_SOMBRA
            CB.sombra(out, CB.Mapa(), (x0, cy0 + 4, x1, cy1 - 4), ms["forca"], dx=ms["d"] * (1 if fr[0] < 0 else -1),
                      dy=ms["d"] * 0.6, sigma=ms["sigma"])
            a_ = CB.alfa_ret((x0, y0, x1, y1), out.shape[:2])[cy0:cy1, :, None]
            out[cy0:cy1] = u8(out[cy0:cy1] * (1 - a_) + antes[cy0:cy1] * a_)
        if "poltrona" in s:
            (cx, cy), lado, fr = s["poltrona"]
            out = MBE.pousar(out, ler("sala-intima/poltrona-intima-e"), cx, cy, lado, lado, MB.frente(fr), "movel", par)
            out = pos(out, ler(f"{pasta}/criado-redondo"), s["redondo"], (0, 1), "movel")
    out = quieto(RV.bancos, out, dict(RV.BANCOS, png=RV.BANCOS["png"].with_name(BANCO_PNG),
                                      bancos=[(n, tuple(map(float, r)), g) for n, r, g in bancos]))
    # a sala íntima
    s = SALA_INTIMA
    out = limpar_piso(Q, out, s["poltrona_antes"], MADEIRA, nao_luz=[(1860, 1200, 2116, 1392)])
    out = limpar_piso(Q, out, s["lateral_sofa_antes"], MADEIRA, nao_luz=[(1860, 1200, 2077, 1340), (1876, 1235, 2116, 1392)])
    H, W = par.shape
    sofa = np.zeros((H, W), bool)
    f = s["sofa_folga"]
    for x0, y0, x1, y1 in s["sofa"]:
        sofa[y0 - f:y1 + f, x0 - f:x1 + f] = True
    com = pos(out, ler("sala-intima/tapete-intimo-e"), s["tapete"], (0, 1), None)
    out = np.where(sofa[..., None], out, com)
    out = pos(out, ler("sala-intima/mesa-lateral-metal-madeira"), s["lateral"], (0, 1), "mesa")
    out = pos(out, ler("sala-intima/mesa-intima-redonda-e"), s["mesa"], (0, 1), "mesa")
    cx, cy, dm = s["lateral_sofa"]
    out = MBE.pousar(out, ler("sala-intima/mesa-intima-redonda-e"), cx, cy, dm, dm, 0.0, "mesa", par)
    out = pos(out, ler("sala-intima/poltrona-intima-e"), s["poltrona"], (-1, 0), "movel", troca=True)
    # a copinha e a rouparia
    c = COPINHA
    x0, y0, x1, y1 = c["tampo"]
    out = MBE.pousar(out, repetida(ler("copinha/tampo-copinha-e"), x1 - x0, y1 - y0), (x0 + x1) / 2, (y0 + y1) / 2,
                     x1 - x0, y1 - y0, 0.0, None, par)
    cx, cy, cw, chh = c["cuba"]
    out = MBE.pousar(out, ler("copinha/cuba-franke-misturador-unic"), cx, cy, cw, chh, MB.frente((0, -1)), "baixa", par)
    x0, y0, x1, y1 = c["armario"]
    out = MBE.pousar(out, repetida(ler("rouparia/armario-despensa-fechado"), x1 - x0, y1 - y0), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente((0, -1)),
                     None, par)
    r = ROUPARIA_MOVEIS
    x0, y0, x1, y1 = r["estante"]
    out = MBE.pousar(out, repetida(ler("rouparia/modulo-estante-aberta"), x1 - x0, y1 - y0), (x0 + x1) / 2,
                     (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente((0, 1)), None, par)
    x0, y0, x1, y1 = r["nichos"]
    out = MBE.pousar(out, ler("rouparia/bancada-rouparia-e"), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0,
                     MB.frente((0, 1)), None, par)
    print(f"    mobiliário: {', '.join(SUITES)} (tapete, cama, criados, banco K3, cadeira sob o tampo; poltrona e criado "
          "redondo na master); sala íntima (tapete, mesa de centro, mesa lateral redonda, poltrona; o sofá fica); copinha (tampo, cuba "
          "Franke, armário); rouparia (estante e nichos)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 10. Os rótulos no padrão de todas as casas (16/11; `pedidos_terreo_casae_1611.ROTULOS`: Inter, o nome e a área, um
# corpo só, no meio do piso livre de cada ambiente, fora dos móveis novos; a cor pelo fundo): as fileiras vizinhas pela
# mesma base (BANHO 2 e CLOSET 2; BANHO 1 e CLOSET 1; BANHO 4 e CLOSET 4; BANHO 3 e CLOSET 3; CIRCULAÇÃO e COPINHA, no
# corredor, a da copinha diante do tampo) e as colunas pelo mesmo eixo (as suítes 3 e 4, entre o tapete e a
# escrivaninha; os banhos 3 e 4; os closets 3 e 4; os das suítes 1 e 2 e os das varandas da direita). A descrição da
# escada ("DESCE PARA O / TÉRREO", G2) no corpo das descrições do Térreo, à esquerda da escada, ao lado do ▶ D.
ROTULOS = [
    ("SUÍTE MASTER", ("SUÍTE MASTER", "A: 28,89 m²"), (1580.0, 800.0), "normal"),
    ("BANHO MASTER", ("BANHO MASTER", "A: 19,72 m²"), (1830.0, 630.0), "normal"),
    ("CLOSET MASTER", ("CLOSET MASTER", "A: 10,56 m²"), (2087.5, 631.0), "normal"),
    ("ELEVADOR", ("ELEVADOR",), (2001.75, 773.0), "normal"),
    ("ROUPARIA", ("ROUPARIA", "A: 3,6 m²"), (2135.0, 775.0), "normal"),
    ("CLOSET 2", ("CLOSET 2", "A: 3,78 m²"), (2306.0, 633.0), "normal"),
    ("BANHO 2", ("BANHO 2", "A: 5,94 m²"), (2424.0, 633.0), "normal"),
    ("SUÍTE 2", ("SUÍTE 2", "A: 17 m²"), (2393.0, 866.0), "normal"),
    ("VARANDA (suíte 2)", ("VARANDA", "A: 5,2 m²"), (2523.5, 789.0), "normal"),
    ("CLOSET 1", ("CLOSET 1", "A: 3,78 m²"), (2306.0, 1000.0), "normal"),
    ("BANHO 1", ("BANHO 1", "A: 5,94 m²"), (2424.0, 1000.0), "normal"),
    ("SUÍTE 1", ("SUÍTE 1", "A: 17 m²"), (2393.0, 1232.0), "normal"),
    ("VARANDA (suíte 1)", ("VARANDA", "A: 5,2 m²"), (2523.5, 1144.0), "normal"),
    ("CIRCULAÇÃO", ("CIRCULAÇÃO", "A: 19,3 m²"), (1829.0, 863.0), "normal"),
    ("COPINHA", ("COPINHA", "A: 3,85 m²"), (2052.0, 863.0), "normal"),
    ("SUÍTE 4", ("SUÍTE 4", "A: 19,98 m²"), (1636.0, 983.0), "normal"),
    ("BANHO 4", ("BANHO 4", "A: 4,92 m²"), (1538.0, 1138.0), "normal"),
    ("CLOSET 4", ("CLOSET 4", "A: 3,15 m²"), (1653.0, 1138.0), "normal"),
    ("BANHO 3", ("BANHO 3", "A: 4,95 m²"), (1538.0, 1274.0), "normal"),
    ("CLOSET 3", ("CLOSET 3", "A: 3,15 m²"), (1653.0, 1274.0), "normal"),
    ("SUÍTE 3", ("SUÍTE 3", "A: 19,98 m²"), (1636.0, 1434.0), "normal"),
    ("SALA ÍNTIMA", ("SALA ÍNTIMA", "A: 44,94 m²"), (1806.0, 1296.0), "normal"),
    ("VARANDA", ("VARANDA", "A: 65,75 m²"), (1285.0, 1031.0), "normal"),
]
DESCRICAO = {"texto": ("DESCE PARA O", "TÉRREO"), "x": 1860.0, "y": 1000.0, "alinhar": "direita", "cor": (20, 20, 20)}
SEM_TEXTOS = False


def rotulos(Q, img, q=ROTULOS):
    import pedidos_terreo_casae_1611 as PE
    import revisao_terreo_casac_1411 as R14
    import terreo_casaa_1011 as TA
    if SEM_TEXTOS:
        print("    rótulos e descrição da escada: fora (a final sem textos, entrada da opção B do 12K)")
        return img
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
    print(f"    rótulos: {len(q)} no padrão (Inter, um corpo), claros sobre o fundo escuro ({', '.join(claros) or 'nenhum'}); "
          "a descrição \"DESCE PARA O TÉRREO\" à esquerda da escada")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# 12b. As folhagens em 4K (usuário: "vamos melhorar as representações das folhas. preciso que você mantenha os tipos de
# folha, mas gere o 4k delas e reaplique-as na imagem"): cada espécie do render gerada de novo no Higgsfield (Nano
# Banana 2, 4K, vista de cima, com o recorte do render como referência), recortada do fundo branco e guardada na
# biblioteca (03-primeiro-pavimento): a palmeira de folha fina das 2 plantas da varanda principal, a palmeira em roseta
# da varanda da suíte 1, a folhagem larga do jardim da sala íntima e a folhagem da floreira do banho master. A planta
# de antes sai (as folhas: o que foge do piso de em volta, fora dos vasos de terracota) com o piso de em volta, e a nova
# entra no mesmo centro, no mesmo tamanho, com a sombra curta. Na floreira, a folhagem 4K enche o caixote.
FOLHAGENS = [
    # (nome, png da biblioteca, caixa da planta de antes px, centro px, lado da planta px, deslocamento do piso que
    # cobre a de antes (dx, dy) px, diâmetro do vaso px)
    ("varanda principal (em cima)", "varanda-principal/palmeira-folha-fina-4k", (1177, 545, 1285, 650),
     (1229.0, 590.0), 60.0, (0, 125), 64.0),
    ("varanda principal (embaixo)", "varanda-principal/palmeira-folha-fina-4k", (1177, 1446, 1264, 1531),
     (1218.0, 1490.0), 56.0, (0, -170), 60.0),
    ("varanda da suíte 1", "varanda-da-suite-1/palmeira-roseta-4k", (2496, 1220, 2554, 1286),
     (2525.5, 1253.0), 42.0, (0, -78), 46.0),
    ("jardim da sala íntima", "jardim-sala-intima/folhagem-larga-4k", (2116, 1474, 2182, 1549),
     (2148.0, 1511.0), 40.0, (0, -76), 44.0),
]
# (usuário: "ao lado da planta deveria ser o quê em marrom? e a planta precisa estar dentro de um vaso. providencie o
# vaso e entenda se é uma poltrona com uma mesa") o PDF não desenha nada no canto de baixo da varanda principal; os 2
# círculos marrons vêm do render da IA. A biblioteca da E prevê para essa varanda a poltrona externa B e a mesa lateral
# externa (redonda, de madeira marrom): a mesa no círculo menor, a poltrona no maior, virada para a mesa. Cada planta
# vai num vaso de concreto (o da biblioteca, `vaso-folhagem-a`, com a terra no lugar das folhas dele), a planta por cima,
# as folhas passando da borda.
VARANDA_CANTO = {"limpa": [(1182, 1406, 1254, 1468), (1238, 1452, 1312, 1531)], "desloc": (0, -170),
                 "mesa": (1217.0, 1437.0, 36.0), "poltrona": (1275.0, 1492.0, 48.0, (-1, -1))}
# o vaso redondo de concreto (o dos vasos de folhagem da biblioteca): a borda clara, a sombra dela por dentro e a terra
VASO = {"px": 400, "borda": 0.10, "concreto": (178, 186, 190), "aresta": (150, 158, 162), "terra": (56, 72, 92),
        "semente": 1811}


def vaso(q=VASO):
    n = q["px"]
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2) / (n / 2)
    rng = np.random.default_rng(q["semente"])
    ruido = cv2.GaussianBlur(rng.normal(0, 1, (n, n)).astype(np.float32), (0, 0), 3) * 6
    out = np.zeros((n, n, 4), np.float32)
    ri = 1 - 2 * q["borda"]
    t = np.clip((r - ri) / (1 - ri), 0, 1)[..., None]
    borda = np.float32(q["concreto"]) * (1 - 0.25 * t) + np.float32(q["aresta"]) * 0.25 * t
    sombra = np.clip(1 - (ri - r) / 0.12, 0, 1)[..., None] * 0.45
    terra = np.float32(q["terra"]) * (1 - sombra) + ruido[..., None]
    out[..., :3] = np.where((r >= ri)[..., None], borda + ruido[..., None] * 0.5, terra)
    out[..., 3] = np.clip((1 - r) * n / 2, 0, 1) * 255
    return out
# o que não dá a luz do piso (os caixilhos da varanda) e as faixas refeitas com as mesmas linhas mais à direita (o
# guarda-corpo de baixo, que as folhas de antes cruzavam): (caixa px, dx px)
FOLHAGENS_NAO_LUZ = [(1150, 540, 1178, 1560), (1150, 1530, 1320, 1560), (2100, 1545, 2200, 1560),
                     (1192, 1414, 1244, 1458), (1248, 1464, 1300, 1522)]          # e os 2 vasos de terracota
FOLHAGENS_FAIXAS = [((1170, 1531, 1266, 1556), 100)]
FLOREIRA = {"jpg": BIB / "banho-master/floreira-folhagem-4k.jpg", "caixa": (1744, 446, 1778, 528), "borda_px": 2.0,
            "borda": 0.75}


def piso_deslocado(out, m, dx, dy, suave=1.6):
    """Os px de `m` com o piso de (dx, dy) px adiante (o mesmo piso, sem objetos), com a borda suave."""
    a = cv2.GaussianBlur(cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), suave)
    a = np.maximum(a, m)[..., None]
    src = np.roll(out, (-dy, -dx), axis=(0, 1)).astype(np.float32)
    return u8(out * (1 - a) + src * a)


def folhagens(Q, img, q=FOLHAGENS, f=FLOREIRA):
    import alternativa1_terreo_casad_1611 as A1
    import mobiliario_terreo_casae_1611 as MBE
    import regras_terreo_casab_1311 as RT
    import mobiliario_terreo_casac_1311 as MB
    par = paredes(Q, 0.5)
    out = img.copy()
    ficam_base = RT.dilatar(par, 1)
    for a0, b0, a1, b1 in FOLHAGENS_NAO_LUZ:
        ficam_base[b0:b1, a0:a1] = True
    # o canto de baixo da varanda principal: os círculos de antes saem
    v = VARANDA_CANTO
    for x0, y0, x1, y1 in v["limpa"]:
        m = np.zeros(par.shape, bool)
        m[y0:y1, x0:x1] = True
        out = piso_deslocado(out, m & ~ficam_base, *v["desloc"], suave=3.0)
    V = vaso()
    plantas = []
    for nome, rel, (x0, y0, x1, y1), (cx, cy), lado, desloc, dv in q:
        dx, dy = desloc or (0, 0)
        if desloc is None:                     # no jardim de madeira: a amostra da circulação, na luz de em volta
            fundo = np.median(img[y0:y0 + 6, x0 + 20:x1].reshape(-1, 3).astype(np.float32), axis=0)
        else:
            fundo = np.median(img[y0 + dy:y1 + dy, x0 + dx:x1 + dx].reshape(-1, 3).astype(np.float32), axis=0)
        sub = img[y0:y1, x0:x1].astype(np.float32)
        dif = np.abs(sub - fundo).sum(axis=2) > 36
        verde = (sub[..., 1] >= sub[..., 2] - 4) & (sub[..., 1] > sub[..., 0] - 2)
        terracota = (sub[..., 2] - sub[..., 1] > 22) & (sub[..., 2] > 120)
        m = np.zeros(par.shape, bool)
        m[y0:y1, x0:x1] = (dif | verde & (np.abs(sub - fundo).sum(axis=2) > 18)) & ~terracota
        m = RT.dilatar(m, 2)
        m[:y0, :] = m[y1:, :] = False
        m[:, :x0] = m[:, x1:] = False
        if desloc is None:
            out = A1.refazer(out, m & ~par & ~ficam_base, [(None, MADEIRA)], ficam=ficam_base)
        else:
            out = piso_deslocado(out, m & ~par & ~ficam_base, dx, dy, suave=2.5)
        for (a0, b0, a1, b1), dx in FOLHAGENS_FAIXAS:
            if a0 < x1 and a1 > x0 and b0 < y1 + 30 and b1 > y0:
                out[b0:b1, a0:a1] = img[b0:b1, a0 + dx:a1 + dx]
        plantas.append((rel, cx, cy, lado, dv))
    # a mesa e a poltrona do canto, depois os vasos e as plantas por cima
    cx, cy, d = v["mesa"]
    out = MBE.pousar(out, ler("varanda-principal/mesa-lateral-externa"), cx, cy, d, d, 0.0, "mesa", par)
    cx, cy, d, fr = v["poltrona"]
    out = MBE.pousar(out, ler("varanda-principal/poltrona-externa-b"), cx, cy, d, d, MB.frente(fr), "movel", par)
    for rel, cx, cy, lado, dv in plantas:
        out = MBE.pousar(out, V, cx, cy, dv, dv, 0.0, "movel", par)
        out = MBE.pousar(out, ler(rel), cx, cy, lado, lado, 0.0, "baixa", par)
    # a floreira
    x0, y0, x1, y1 = f["caixa"]
    T = cv2.imread(str(f["jpg"]))
    w, h = x1 - x0, y1 - y0
    H, W = T.shape[:2]
    if W / H > w / h:
        nw = int(H * w / h)
        T = T[:, (W - nw) // 2:(W - nw) // 2 + nw]
    else:
        nh = int(W * h / w)
        T = T[(H - nh) // 2:(H - nh) // 2 + nh]
    T = cv2.resize(T, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum.reduce([xx + 0.5, w - xx - 0.5, yy + 0.5, h - yy - 0.5])
    T *= (f["borda"] + (1 - f["borda"]) * np.clip(d / f["borda_px"], 0, 1))[..., None]
    out[y0:y1, x0:x1] = u8(T)
    print(f"    folhagens 4K: {', '.join(n for n, *_ in q)} em vasos de concreto (as plantas de antes no piso de em volta) e "
          "a floreira do banho master; no canto de baixo da varanda principal, a mesa lateral e a poltrona externas")
    return out


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("base", base), ("nublado", nublado), ("escada", escada), ("tracejados", tracejados), ("rouparia", rouparia),
          ("elevador", elevador), ("chuveiros", chuveiros), ("banhos", banhos), ("esquadrias", esquadrias),
          ("mobiliario", mobiliario), ("folhagens", folhagens), ("rotulos", rotulos)]


def rodar(img, de=None, ate=None, cache=None):
    Q = FE.QuadroE("1Pavimento")
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
    out = rodar(antes_img(), a.de, a.ate, a.cache)
    cv2.imwrite(a.saida or str(FINAL), out)
    print(f"-> {a.saida or FINAL}")


if __name__ == "__main__":
    main()

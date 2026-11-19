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
# o quartzito Aura (Higgsfield, 4096 px, a foto da chapa; usuário: "todos os pisos dos banhos são em quartzito aura")
AURA = BIB / "banho-master/quartzito-aura-4k.jpg"
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
# (usuário: "tracejados em tom cinza claro com linhas finas", "clareie todos os tracejados para cinza claro") o traço
# dos tracejados no fundo claro: do cinza 128 de `revisao_1pav_casae_1711.CINZA` (escuro sobre o quartzito Aura) para o
# cinza claro; a espessura fica (0,8 px, `LARG_PX`); no fundo escuro, o cinza claro de `CINZA_ESCURO`, como antes
TRACEJADO_CINZA = (172, 172, 172)


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
    FE.TRACEJADOS_1P = dict(guarda, larg_px=RV.LARG_PX, preto=TRACEJADO_CINZA, branco=RV.CINZA_ESCURO)
    FE.tracejados_pb_te = pb_filtrado
    try:
        out = quieto(FE.tracejados_pb_1p, Q, img)
    finally:
        FE.TRACEJADOS_1P, FE.tracejados_pb_te = guarda, pb
    print("    tracejados: a rouparia sem o tracejado; as claraboias do banho master só com o retângulo cinza claro fino, "
          "sem o X; o X dos vazios e do shaft de novo no cinza claro fino")
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


def bancada_esticada(P, L, D, cols, centros, ss=4):
    """A bancada P (BGRA, as torneiras em cima) com L x D px (x ss): as cubas de P (`cols`, frações da largura) sem
    esticar, com os centros em `centros` (frações de L); a pedra de entre elas e das pontas esticada no comprido (os
    veios seguem, sem o espelho que fazia zigue-zague)."""
    H, W = P.shape[:2]
    Dt, Lt = round(D * ss), round(L * ss)
    k = Dt / H                                   # a escala das cubas (a da altura)
    src = [0]
    dst = [0]
    for (a, z), f in zip(cols, centros):
        w = (z - a) * W * k
        x0 = f * Lt - w / 2
        src += [a * W, z * W]
        dst += [x0, x0 + w]
    src.append(W)
    dst.append(Lt)
    out = np.zeros((Dt, Lt, P.shape[2]), np.float32)
    for i in range(len(src) - 1):
        s0, s1, d0, d1 = src[i], src[i + 1], int(round(dst[i])), int(round(dst[i + 1]))
        if d1 <= d0 or s1 <= s0:
            continue
        pedaco = P[:, int(round(s0)):int(round(s1))]
        out[:, d0:d1] = cv2.resize(pedaco, (d1 - d0, Dt), interpolation=cv2.INTER_AREA)
    return np.ascontiguousarray(out)


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
# (usuário, depois do 12K: "bancada em quartzito aura e cuba esculpida em quartzito aura em 4k, da biblioteca. se não
# tiver, fazer") a da biblioteca (`bancada-dupla-quartzito-aura`) tinha 699 px: a de 4K foi feita no Higgsfield a partir
# dela (`bancada-dupla-quartzito-aura-4k`, 5679 x 2322, as cubas esculpidas na mesma pedra), e no 12K entra direto
MASTER = {"bancada": (1910.1, 445.0, 1945.0, 593.0), "cubas": (491.25, 552.65),
          "png": "banho-master/bancada-dupla-quartzito-aura-4k",
          # (usuário: "a torneira de piso da banheira foi colocada no lugar errado") a banheira no contorno inteiro do PDF
          # (ARQ_LOUÇAS E METAIS, de 454,2 a 554,8: a cabeceira arredondada entra) e o misturador de piso no meio da
          # cabeceira, junto à parede, a bica sobre a borda (antes ficava solto no canto de cima, à esquerda)
          "cols": ((0.08, 0.39), (0.567, 0.88)), "banheira": (1799.8, 454.2, 1853.3, 554.8),
          "misturador": (1826.55, 455.5, 9.0, 13.0), "bacia": (1774.2, 780.6, 1795.3, 811.3),
          "banheira_antes": (1784, 447, 1868, 601),         # a de antes era maior que a do PDF
          "floreira": (1730, 440, 1784, 610), "vaso_antes": (1749, 766, 1818, 812), "linha": (1745, 778, 1822, 796),
          "amostra": (1770, 615, 1890, 700), "amostra_vaso": (1758, 732, 1814, 764),
          # (usuário: "aqui é um armário, cor sólida") o armário do PDF junto à floreira (ARQ_LAYOUT, 1748 a 1776 x 535,5
          # a 593,7 px), com o contorno cinza de antes até o piso de Aura: `armario_liso`, o tom das outras casas
          "armario": (1748.0, 535.0, 1778.0, 594.4)}


# (usuário, depois do 12K: "melhore a representação do piso em volta da porta, no banho master", "em volta da banheira",
# "remova esse contorno indevido em volta da bancada e corrija o piso no alto também") as limpezas pela amostra deixavam
# manchas escuras em volta da banheira, retângulos de outro tom junto à porta e a sobra clara da bancada de antes. O piso
# claro da parte de cima do banho master (da floreira à parede da bancada, até as paredes do vaso e do box) é refeito
# inteiro: a luz larga do piso do render (a final de b227, sem as peças: o que foge da mediana), vezes as nuvens finas da
# pedra (ruído em 3 escalas, de leve), e as peças entram de novo por cima.
# (usuário: "corrigir o piso das regiões do vaso e chuveiro, igual ao resto do banheiro") também o do vaso e o do box,
# com os chuveiros, a bacia e os retângulos das claraboias de novo por cima
PISO_BM = {"caixa": (1742, 447, 1947, 813), "pontos": [(1830, 650), (1785, 745), (1890, 745)],
           # a floreira e o armário do PDF junto à parede de baixo dela (ARQ_LAYOUT, com a diagonal) ficam
           "fora": [(1738, 440, 1782, 533), (1746, 533, 1778, 596)],
           "semente": 1816}


# (usuário: "todos os pisos dos banhos são em quartzito aura"; "nos banheiros não teremos juntas. faça algo mais
# uniforme e sem muita repetição") o piso do banho master (o de cima, o do vaso e o do box) e o dos banhos 1 a 4 (com o
# box e o nicho do chuveiro) em quartzito Aura sem juntas: cada banho um recorte só, contínuo, da foto da chapa
# (`AURA`, lida como 6,4 m de lado: os veios largos e nada se repete dentro do banho; cada banho num trecho e num giro
# dela), os veios suavizados (`contraste`) para um piso mais uniforme; a luz do piso do render (a final de b227, sem
# as peças: o que foge da mediana) só no claro e escuro. Junto às paredes, a mistura com o cinza delas pela cobertura
# do PDF; as folhas das portas ficam; as peças (bancadas, bacias, banheira, chuveiros, retângulos das claraboias)
# entram de novo por cima
PISO_AURA = {"aura_m": 6.4, "contraste": 0.55, "tom": 0.965, "luz": (0.88, 1.06), "luz_sigma": 40.0, "foge": 14}
PISO_BANHOS = {
    # retângulo de dentro (px), nicho do chuveiro (px), semente (o trecho e o giro da chapa)
    "banho 2": {"caixa": (2361, 567, 2557, 674), "nicho": (2515, 561, 2540, 567), "semente": 1821},
    "banho 1": {"caixa": (2361, 934, 2557, 1041), "nicho": (2515, 928, 2540, 934), "semente": 1822},
    "banho 4": {"caixa": (1408, 1116, 1604, 1205), "nicho": (1427, 1205, 1450, 1210), "semente": 1823},
    "banho 3": {"caixa": (1408, 1218, 1604, 1307), "nicho": (1427, 1213, 1450, 1218), "semente": 1824},
}


def chapa_aura(caixa, semente, q=PISO_AURA):
    """Um recorte contínuo da foto da chapa de Aura na `caixa` (px, float32 BGR), sem juntas e sem repetir, os veios
    suavizados; o trecho e o giro (0 ou 180°) pela `semente`."""
    import mobiliario_terreo_casac_1311 as MB
    if "aura" not in _CACHE:
        _CACHE["aura"] = cv2.imread(str(AURA)).astype(np.float32)
    T = _CACHE["aura"]
    x0, y0, x1, y1 = caixa
    k = T.shape[1] / (q["aura_m"] * MB.PX_M)              # px da foto por px da final
    w = min(int(round((x1 - x0) * k)), T.shape[1])
    h = min(int(round((y1 - y0) * k)), T.shape[0])
    rng = np.random.default_rng(semente)
    rx, ry = int(rng.integers(0, T.shape[1] - w + 1)), int(rng.integers(0, T.shape[0] - h + 1))
    pl = T[ry:ry + h, rx:rx + w]
    if rng.random() < 0.5:
        pl = pl[::-1, ::-1]
    pl = cv2.resize(pl, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    m = pl.reshape(-1, 3).mean(axis=0)
    return m + (pl - m) * q["contraste"]


def piso_aura(Q, out, caixas, pontos, semente, fora=(), q=PISO_AURA):
    """O piso de quartzito Aura nos não-parede das `caixas` (px) ligados aos `pontos`, fora os retângulos `fora` e as
    folhas das portas (que ficam)."""
    import correcoes_terreo_casab_1611 as CB
    import regras_terreo_casab_1311 as RT
    par = paredes(Q, 0.5)
    H, W = par.shape
    caixa = np.zeros((H, W), bool)
    for a0, b0, a1, b1 in caixas:
        caixa[b0:b1, a0:a1] = True
    n, lab = cv2.connectedComponents((caixa & ~par).astype(np.uint8))
    m = np.isin(lab, [lab[py, px] for px, py in pontos]) & (lab > 0)
    for a0, b0, a1, b1 in fora:
        m[b0:b1, a0:a1] = False
    # a luz: o piso do render da final aprovada de antes (b227), sem as peças, só o claro e escuro
    ref = antes_img().astype(np.float32)
    med = np.median(ref[m], axis=0)
    fonte = m & (np.abs(ref - med).max(axis=2) < q["foge"])
    sg = q["luz_sigma"]
    num = cv2.GaussianBlur(ref.mean(axis=2) * fonte, (0, 0), sg)
    den = cv2.GaussianBlur(fonte.astype(np.float32), (0, 0), sg)
    L = num / np.maximum(den, 1e-4)
    L = np.clip(L / float(np.median(L[m])), *q["luz"])
    ys, xs = np.nonzero(RT.dilatar(m, 1))
    bx0, by0, bx1, by1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    novo = np.zeros((H, W, 3), np.float32)
    novo[by0:by1, bx0:bx1] = chapa_aura((bx0, by0, bx1, by1), semente)
    novo *= (L * q["tom"])[..., None]
    # junto às paredes: o cinza delas pela cobertura do PDF
    FE.paredes_pdf(Q)
    ap = np.clip(Q._par, 0, 1).astype(np.float32)
    zona = RT.dilatar(m, 1) & (ap < 0.98) & caixa
    fora_m = np.zeros((H, W), bool)
    for a0, b0, a1, b1 in fora:
        fora_m[b0:b1, a0:a1] = True
    zona &= ~fora_m
    novo = np.float32(PAREDE)[None, None] * ap[..., None] + novo * (1 - ap[..., None])
    af = np.zeros((H, W), np.float32)
    for f in folhas_portas(out):
        af = np.maximum(af, CB.alfa_ret(f, (H, W)))
    w = zona.astype(np.float32) * (1 - af)
    o = out.astype(np.float32)
    o = o * (1 - w[..., None]) + novo * w[..., None]
    return u8(o), int(m.sum())


def piso_banho_master(Q, out, q=PISO_BM):
    """O piso do banho master (o de cima, o do vaso e o do box) em quartzito Aura (`piso_aura`)."""
    out, _ = piso_aura(Q, out, [q["caixa"]], q["pontos"], q["semente"], fora=q["fora"])
    return out


def bancada_master_12k(out, mapa, q=MASTER):
    """A bancada 4K do banho master direto no 12K (`out`, uint8, mudado no lugar), sem a sombra (a da final já está)."""
    import biblioteca_terreo_casaa_1211 as BT
    import mobiliario_terreo_casac_1311 as MB
    x0, y0, x1, y1 = q["bancada"]
    m = mapa((int(x0) - 10, int(y0) - 4, int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 10))
    L, D = (y1 - y0) * m.s, (x1 - x0) * m.s
    P = bancada_esticada(ler(q["png"]), L, D, q["cols"], [(c - y0) / (y1 - y0) for c in q["cubas"]])
    cx, cy = m.x((x0 + x1) / 2) - 0.5, m.y((y0 + y1) / 2) - 0.5
    g = int(max(L, D) / 2) + 6
    X0, Y0, X1, Y1 = int(cx) - g, int(cy) - g, int(cx) + g, int(cy) + g
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    o = BT.pousar(reg, P, cx - X0, cy - Y0, L, D, MB.frente((-1, 0)), [], MB.PX_M * m.s)
    out[Y0:Y1, X0:X1] = u8(o)
    print(f"    a bancada 4K de quartzito Aura direto no 12K, a {m.s:.4f}x ({L:.0f} x {D:.0f} px)")
    return out


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
        pb = PISO_BANHOS[nome]
        a0, b0, a1, b1 = pb["caixa"]
        out, _ = piso_aura(Q, out, [pb["caixa"], pb["nicho"]], [((a0 + a1) // 2, (b0 + b1) // 2)], pb["semente"])
        x0, y0, x1, y1 = b["bancada"]
        L, D = x1 - x0, y1 - y0
        pos = (b["cuba"] - x0) / L
        if b["frente"] == (0, -1):
            pos = 1 - pos
        P = MBE.esticada(Ps, L, D, BANCADA_SIMPLES["cols"], pos)
        out = MBE.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, L, D, MB.frente(b["frente"]), "baixa", par)
        x0, y0, x1, y1 = b["bacia"]
        out = MBE.pousar(out, Pb, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente(b["bacia_frente"]), "baixa",
                         par)
    # o master: o piso inteiro refeito (as manchas, os retângulos e o contorno da bancada de antes; o vaso e o box), e
    # os 2 chuveiros dele de novo
    out = piso_banho_master(Q, out)
    out = armario_liso(out, [m["armario"]], par)
    for nome, cab, lado, parede, _, _ in CHUVEIROS:
        out = chuveiro(out, Q, cab, lado, parede)
    mx, my, mw, mh = m["misturador"]
    x0, y0, x1, y1 = m["bancada"]
    L, D = y1 - y0, x1 - x0
    P = bancada_esticada(ler(m["png"]), L, D, m["cols"], [(c - y0) / L for c in m["cubas"]])
    out = MBE.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, L, D, MB.frente((-1, 0)), "baixa", par)
    x0, y0, x1, y1 = m["banheira"]
    out = MBE.pousar(out, ler("banho-master/banheira-oval-master-e"), (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0,
                     MB.frente((1, 0)), "movel", par)
    out = MBE.pousar(out, ler("banho-master/misturador-piso-banheira-render"), mx, my, mw, mh, MB.frente((0, 1)),
                     "baixa", par)
    # a bacia, sob os retângulos das claraboias (de novo por cima)
    x0, y0, x1, y1 = m["bacia"]
    out = MBE.pousar(out, Pb, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente((0, -1)), "baixa", par)
    out = linha_claraboia(Q, out, PISO_BM["caixa"], nomes=("banho master: vaso", "banho master: box"))
    print(f"    banhos: {', '.join(q)} com a bancada de quartzito e a cuba esculpida da biblioteca e a bacia Carrara; "
          "master com a bancada dupla da E (as 2 cubas no lugar do PDF), a banheira oval, o misturador de piso e a bacia")
    return out


def linha_claraboia(Q, out, caixa, nomes=("banho master: vaso",), vaos=True, sob_rotulo=()):
    """Os retângulos tracejados das claraboias do master (`nomes`) de novo, só dentro da `caixa` (px): sobre a bacia e
    o piso novos (só os traços retos, como em `tracejados`: sem o X)."""
    import revisao_1pav_casae_1711 as RV

    def reto(t):
        return abs(t[2] - t[0]) < 0.3 or abs(t[3] - t[1]) < 0.3
    trechos = [(n, [t for t in tr if reto(t)]) for n, tr in FE._tracos_1p(Q) if n in nomes]
    q = dict(FE.TRACEJADOS_1P, larg_px=RV.LARG_PX, preto=TRACEJADO_CINZA, branco=RV.CINZA_ESCURO)
    com = quieto(FE.tracejados_pb_te, Q, out, q=q, vaos=vaos, trechos=trechos)
    for a0, b0, a1, b1 in sob_rotulo:                  # onde o texto do rótulo passa, o traço para
        com[b0:b1, a0:a1] = out[b0:b1, a0:a1]
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
# (usuário, depois do 12K: "tire o contorno do recamier") o K3 sem a moldura de nogueira: o miolo de linho com os rolos
# (o PNG da biblioteca cortado por dentro da moldura), no mesmo retângulo
BANCO = BIB / "suite-master/banco-k3-sem-contorno.png"
MESA_SOMBRA = {"forca": 0.26, "sigma": 1.0, "d": 1.2}
MADEIRA = (1770, 830, 1980, 900)
SUITES = {
    # (`limpa`: a última inclui o resto do rótulo de antes, sob o banco antigo; `cortina`: não dá a luz do piso)
    "suíte master": {"limpa": [(1452, 560, 1684, 846), (1425, 752, 1536, 866)], "cama": ((1504, 567, 1628, 697), "king"),
                     # a faixa escura da sombra velha junto ao criado da direita, o pontinho junto ao rack, o rack
                     "extra": [(1666, 556, 1692, 615), (1494, 861, 1506, 875), (1499, 855, 1637, 884)],
                     "cortina": (1398, 552, 1426, 900),
                     "tapete": (1461, 612, 1670, 749), "banco": ((1504, 700, 1628, 724), 0),
                     "criados": [(1465, 568, 1501, 604), (1632, 568, 1668, 604)], "frente": (0, 1),
                     "poltrona": ((1459.0, 824.0), 52.0, (1, -1)), "redondo": (1483, 758, 1526, 802)},
    "suíte 2": {"limpa": [(2304, 678, 2469, 849), (2262, 727, 2292, 776)], "cama": ((2352, 683, 2434, 801), "casal"),
                "extra": [(2226, 888, 2294, 912), (2326, 894, 2454, 922)],
                "cortina": (2468, 670, 2492, 860),
                "tapete": (2315, 722, 2468, 842), "banco": ((2352, 806, 2434, 830), 0),
                "criados": [(2319, 683, 2349, 713), (2438, 683, 2467, 713)], "frente": (0, 1),
                "cadeira": ((2248, 733, 2283, 770), (-1, 0)), "mesa": (2226, 683, 2261.7, 823)},
    "suíte 1": {"limpa": [(2304, 1045, 2469, 1216), (2262, 1094, 2292, 1143)], "cama": ((2352, 1050, 2434, 1168), "casal"),
                "extra": [(2326, 1261, 2454, 1290)],
                "cortina": (2468, 1037, 2492, 1227),
                "tapete": (2315, 1086, 2468, 1206), "banco": ((2352, 1173, 2434, 1197), 0),
                "criados": [(2319, 1050, 2349, 1080), (2438, 1050, 2467, 1080)], "frente": (0, 1),
                "cadeira": ((2248, 1100, 2283, 1137), (-1, 0)), "mesa": (2226, 1050, 2261.7, 1190)},
    "suíte 4": {"limpa": [(1425, 887, 1600, 1062), (1671, 936, 1703, 985)], "cama": ((1466, 892, 1548, 1010), "casal"),
                "extra": [(1443, 1079, 1570, 1108)],
                "cortina": (1398, 880, 1426, 1070),
                "tapete": (1427, 934, 1595, 1054), "banco": ((1466, 1015, 1548, 1039), 0),
                "criados": [(1433, 892, 1463, 922), (1552, 892, 1582, 922)], "frente": (0, 1),
                "cadeira": ((1681, 942, 1717, 979), (1, 0)), "mesa": (1703.3, 892, 1739, 1032),
                "mesa_reparo": ((1703, 936, 1711, 986), -44)},
    "suíte 3": {"limpa": [(1425, 1360, 1600, 1536), (1671, 1434, 1703, 1483)], "cama": ((1470, 1413, 1552, 1531), "casal"),
                "extra": [(1448, 1314, 1575, 1343)],
                "cortina": (1398, 1352, 1426, 1545),
                "tapete": (1427, 1368, 1595, 1488), "banco": ((1470, 1384, 1552, 1408), 180),
                "criados": [(1437, 1501, 1466, 1531), (1555, 1501, 1585, 1531)], "frente": (0, -1),
                "cadeira": ((1681, 1440, 1717, 1477), (1, 0)), "mesa": (1703.3, 1390, 1739, 1531),
                "mesa_reparo": ((1703, 1434, 1711, 1484), -44)},
}
SALA_INTIMA = {"tapete": (1876, 1235, 2115, 1384),
               # (usuário: "corrija esse contorno do tapete, tanto na vertical quanto na horizontal") a peça da
               # biblioteca tem, em volta, um filete claro esverdeado com um sulco escuro logo dentro e os cantos
               # arredondados, que na planta virava um contorno desenhado: a peça vai cortada `tapete_borda` px (da
               # peça, ~3 px da final) para dentro, a textura até a borda reta e os cantos vivos do retângulo do PDF
               "tapete_borda": 7,
               # (usuário: "ja corrija o contorno do tapete" e "o contorno do sofá com o tapete também") o sofá em L é o
               # do render (do 3D), mas não mais recortado nas caixas do PDF com 3 px de folga: a faixa da folga trazia
               # o tapete velho e a sombra escura do render em volta do estofado (e, ao lado do braço, a mesinha que
               # saiu), e o tapete novo fazia degraus. Agora: `sofa` é o L inteiro do render (com sobra), e nas bordas
               # que dão para o tapete e para o piso refeito (`sofa_bordas`) o recorte segue o próprio estofado (os px
               # mais claros que `sofa_limiar`, a sombra do render fica de fora); o tapete vai inteiro, retângulo do PDF,
               # por baixo, e o sofá ganha a sombra de contato dos outros móveis (`SOMBRAS["movel"]`) só no que é novo
               "sofa": [(1845, 1190, 1924, 1346), (1845, 1190, 2078, 1271)],
               # (a borda de baixo do chaise: no render, sobre o tapete branco antigo, o reflexo claro alonga o
               # estofado 2,5 px em relação ao trecho sobre o piso; a borda vai reta na altura do trecho sobre o piso,
               # o 3º valor: até onde a borda pode ir, px)
               "sofa_bordas": [((2062, 1190, 2078, 1271), "x+"), ((1924, 1256, 2078, 1271), "y+"),
                               ((1908, 1267, 1924, 1346), "x+"), ((1845, 1330, 1924, 1346), "y+", 1339.0)],
               "sofa_limiar": 182, "sofa_mediana": 5,
               # a quina do sofá com o tapete e o piso (embaixo, à esquerda): o piso sob a borda do sofá refeito, sem os
               # pontinhos escuros do contorno do render
               "piso_quina": (1854, 1337, 1876, 1347), "poltrona_antes": (2113, 1228, 2158, 1350), "poltrona": (2084, 1280, 2140, 1333),
               "mesa": (1956, 1299, 2016, 1359), "lateral": (1997, 1314, 2039, 1356),
               # (usuário: "corrija a representação dessa mesa lateral, da sala íntima", a redonda do render junto ao
               # braço do sofá, borrada e com a sombra escura em volta): sai, com o piso de madeira (fora do sofá e do
               # tapete), e entra a mesa redonda de carvalho da biblioteca, a da mesa de centro, no mesmo lugar
               # (usuário: "tem uma mesinha redonda diferente [...] ao lado do sofá. tamanho e posição divergente do 3D")
               # no tamanho e no lugar do PDF (ARQ_LAYOUT, o círculo de 2041,7..2059,7 x 1259,6..1277,5 px: 0,30 m, na
               # frente do sofá, junto ao braço direito, por cima da borda do assento), não mais o do render (0,55 m, ao
               # lado do braço; o lugar dele fica no piso de madeira, `lateral_sofa_antes`)
               "lateral_sofa_antes": (2070, 1199, 2120, 1235), "lateral_sofa": (2050.7, 1268.55, 18.0),
               "nogueira": (52, 82, 122)}
COPINHA = {"tampo": (1888.3, 916.2, 2053.4, 951.6), "cuba": (2034.4, 931.2, 30.0, 24.0),
           "armario": (2053.4, 916.2, 2216.7, 951.6),
           # (usuário: "melhore aspecto da bancada e do armario ao lado dela com tom sólido adotado nas outras casas.
           # remova linhas técnicas da imagem") o tampo no quartzito Aura dos banhos (a foto de 4096 px por 3 m, os veios
           # na diagonal, a aresta da frente um tom abaixo), a cuba Franke de volta; o armário liso no tom dos armários
           # das outras casas (`armario_liso`, sem a divisão das portas nem o fio do meio); a faixa da parede de baixo
           # (os tracinhos claros e escuros do PDF e o fio da base) no cinza 80 antes
           "aura_m": 3.0, "aura_x0": 140, "aresta": 0.9,
           "parede": (1886, 951, 2219, 959),
           # o "m²" de um rótulo antigo no piso diante do armário: o piso das mesmas fiadas, 35 px à direita
           "piso_resto": ((2138, 896, 2162, 911), (35, 0))}
# (usuário: "corrija o erro no canto e adicione a claraboia (vão tracejado)") os nichos até a parede de baixo (entre
# eles e a parede ficava uma faixa clara do desenho de antes); a claraboia: o retângulo tracejado do PDF (o grupo
# "rouparia" de `TRACEJADOS_1P`, sem o X), no cinza claro fino, depois do piso e do armário (`retoques`)
ROUPARIA_MOVEIS = {"estante": (2082.3, 715.8, 2216.7, 745.6), "nichos": (2186.8, 745.6, 2216.7, 811.3)}


def armario_liso(out, rets, par):
    """(usuário, depois do 12K: "usar o modelo de armario que usamos nas outras casas com tom sólido, em vez desses
    caixotes abertos") os retângulos (px) num armário liso só, na cor dos armários das Casas C, D e do Térreo da E
    (`revisao_terreo_casac_1311.COZINHA`: a cor, a face um tom abaixo na borda de fora, a sombra curta)."""
    import correcoes_terreo_casab_1611 as CB
    import revisao_terreo_casac_1311 as RC
    import revisao_terreo_casac_1511 as R15
    c = RC.COZINHA
    H, W = par.shape
    a = np.zeros((H, W), np.float32)
    for r in rets:
        a = np.maximum(a, CB.alfa_ret(r, (H, W)))
    a *= ~par
    m = a > 0.5
    o = out.astype(np.float32)
    o *= (1 - c["sombra"] * R15._sombra(a, W, H))[..., None]
    borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    cor = np.float32(c["cor_armario"])[None, None] * np.where(borda, c["face"], 1.0)[..., None]
    return u8(o * (1 - a[..., None]) + cor * a[..., None])


def tampo_aura(L, D, q=COPINHA, ss=4):
    """O tampo L x D px (x ss, BGRA) recortado da foto do quartzito Aura (`q["aura"]`, `q["aura_m"]` metros de lado), a
    aresta da frente (em cima) um tom abaixo."""
    import mobiliario_terreo_casac_1311 as MB
    T = cv2.imread(str(AURA))
    k = T.shape[1] / (q["aura_m"] * MB.PX_M)          # px da foto por px da final
    w, h = int(round(L * k)), int(round(D * k))
    x0 = q["aura_x0"]
    y0 = (T.shape[0] - h) // 2
    P = cv2.resize(T[y0:y0 + h, x0:x0 + w], (round(L * ss), round(D * ss)), interpolation=cv2.INTER_AREA)
    P = P.astype(np.float32)
    P[:max(1, round(0.6 * ss))] *= q["aresta"]
    return np.dstack([P, np.full(P.shape[:2], 255, np.float32)])


def repetida(P, L, D, ss=4):
    """P (BGRA) na profundidade D, repetida em espelho até o comprimento L (px, x ss)."""
    H, W = P.shape[:2]
    Qp = cv2.resize(P, (max(1, round(W * D * ss / H)), round(D * ss)), interpolation=cv2.INTER_AREA)
    rep = np.concatenate([Qp, Qp[:, ::-1]], axis=1)
    Lt = round(L * ss)
    return np.ascontiguousarray(np.tile(rep, (1, Lt // rep.shape[1] + 2, 1))[:, :Lt])


# (usuário, depois do 12K: "corrija esse erro atrás da poltrona", "melhore a representação do piso nessa região",
# "corrigir essa falha no piso" da suíte 2) a limpeza das suítes pela amostra da circulação (`limpar_piso`) deixava
# blocos de réguas desencontradas, emendas nas bordas das caixas e, junto às cortinas (a caixa da cortina não mudava),
# restos dos móveis de antes (a lasca branca da poltrona antiga, os pingos da borda do tapete antigo). Agora o piso das
# caixas, dos `extra` e da faixa até a cortina (o que não é o tecido dela: o claro sem cor ligado ao corpo da cortina)
# vem de réguas novas no desenho do vinílico da E (`vinilico_novo`: as fiadas na fase das do piso de em volta, na luz
# dele, com sigmas até 128 px para o miolo das caixas).
VINIL_NOVO = {"anel_px": 30, "sigmas": (24, 48, 96, 192), "madeira_croma": 30, "madeira_lum": (120, 215),
              "semente": 1812}


def _fase(prof, larg):
    """A fase (px) das juntas (os mínimos) de um perfil de linhas, pela correlação com o cosseno do passo `larg`."""
    ys = np.arange(len(prof), dtype=np.float32)
    ok = np.isfinite(prof)
    p = np.where(ok, prof, 0)
    melhor = None
    for ph in np.linspace(0, larg, 240, endpoint=False):
        v = float((p * np.cos(2 * np.pi * (ys - ph) / larg) * ok).sum())
        if melhor is None or v < melhor[0]:
            melhor = (v, ph)
    return melhor[1]


def vinilico_novo(Q, out, buraco, q=VINIL_NOVO, luz_dentro=False):
    """Réguas novas do vinílico da E (`retoque_1pav_casae.reguas_vinilico`, o desenho da final) em cada região do
    `buraco`, com as fiadas na fase das do piso de em volta (a junta no mesmo y: as tábuas continuam nas bordas) e na
    luz dele (a média local normalizada do anel de piso em volta, estendida para dentro)."""
    import regras_terreo_casab_1311 as RT
    import retoque_1pav_casae as RP
    px = Q.px_m
    larg = RP.VINILICO["regua_m"] * px
    par = paredes(Q, 0.5)
    o = out.astype(np.float32)
    I16 = out.astype(np.int16)
    lum = I16.mean(axis=2)
    madeira = (((I16.max(axis=2) - I16.min(axis=2)) >= q["madeira_croma"]) & (lum >= q["madeira_lum"][0])
               & (lum <= q["madeira_lum"][1]) & ~RT.dilatar(par, 1))
    n, lab = cv2.connectedComponents(buraco.astype(np.uint8))
    H, W = buraco.shape
    for i in range(1, n):
        b_g = lab == i
        ys, xs = np.nonzero(b_g)
        if luz_dentro and len(ys) < 60:      # um retalho solto (entre os caixilhos), não é o piso do quarto
            continue
        g = q["anel_px"] + 8
        X0, Y0, X1, Y1 = max(xs.min() - g, 0), max(ys.min() - g, 0), min(xs.max() + g + 1, W), min(ys.max() + g + 1, H)
        b = b_g[Y0:Y1, X0:X1]
        reg = o[Y0:Y1, X0:X1]
        anel = RT.dilatar(b, q["anel_px"]) & ~buraco[Y0:Y1, X0:X1] & madeira[Y0:Y1, X0:X1]
        # a fase das juntas no anel (o perfil das linhas, sem a média local)
        Lm = reg.mean(axis=2)
        hp = Lm - cv2.blur(Lm, (1, 9))
        cnt = anel.sum(axis=1)
        prof = np.where(cnt > 3, (hp * anel).sum(axis=1) / np.maximum(cnt, 1), np.nan)
        fase = _fase(prof, larg) + Y0
        # a luz
        Lt = np.zeros_like(reg)
        falta = RT.dilatar(b, 3)
        if luz_dentro:                    # o quarto inteiro: a luz larga do próprio piso dele (sem os móveis de antes)
            mad = b & madeira[Y0:Y1, X0:X1]
            if mad.sum() < 20:
                continue
            med = np.median(reg[mad], axis=0)
            fonte = mad & (np.abs(reg - med).max(axis=2) < 25)
            for sg in (48, 96, 192):
                num = cv2.GaussianBlur(reg * fonte[..., None], (0, 0), sg)
                den = cv2.GaussianBlur(fonte.astype(np.float32), (0, 0), sg)
                ok = falta & (den > 0.02)
                Lt[ok] = (num / np.maximum(den, 1e-6)[..., None])[ok]
                falta &= ~ok
            Lt[falta] = med
            anel = anel & False
        for sg in q["sigmas"]:
            num = cv2.GaussianBlur(reg * anel[..., None], (0, 0), sg)
            den = cv2.GaussianBlur(anel.astype(np.float32), (0, 0), sg)
            ok = falta & (den > 0.02)
            Lt[ok] = (num / np.maximum(den, 1e-6)[..., None])[ok]
            falta &= ~ok
        if falta.any() and anel.any():
            Lt[falta] = reg[anel].mean(axis=0)
        # o anel não pode ter os móveis claros/escuros de madeira: o que foge muito da luz larga dele sai e a luz é
        # refeita (uma passada)
        foge = anel & (np.abs(reg - Lt).max(axis=2) > 28)
        if foge.any():
            anel &= ~foge
            Lt[:] = 0
            falta = RT.dilatar(b, 3)
            for sg in q["sigmas"]:
                num = cv2.GaussianBlur(reg * anel[..., None], (0, 0), sg)
                den = cv2.GaussianBlur(anel.astype(np.float32), (0, 0), sg)
                ok = falta & (den > 0.02)
                Lt[ok] = (num / np.maximum(den, 1e-6)[..., None])[ok]
                falta &= ~ok
            if falta.any():
                Lt[falta] = reg[anel].mean(axis=0) if anel.any() else reg[b].mean(axis=0)
        # o desenho, com a junta na fase
        h, w = (Y1 - Y0) + int(np.ceil(2 * larg)), X1 - X0
        sem = q["semente"] + i
        rr = np.random.default_rng(sem)
        veio = cv2.GaussianBlur(rr.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.30 * px, sigmaY=0.7)
        veio = 1 + 0.035 * veio / max(float(veio.std()), 1e-6)
        D = RP.reguas_vinilico(h, w, px, veio, np.ones((h, w), bool), np.random.default_rng(sem))
        fD = _fase(D.mean(axis=1) - cv2.blur(D.mean(axis=1)[:, None], (1, 9))[:, 0], larg)
        d = int(round((fD - (fase - Y0)) % larg))
        D = D[d:d + (Y1 - Y0)]
        a = np.maximum(cv2.GaussianBlur(b.astype(np.float32), (0, 0), 0.7), b)
        a[~RT.dilatar(b, 2)] = 0
        novo = Lt * D[..., None]
        reg[:] = reg * (1 - a[..., None]) + novo * a[..., None]
    return u8(o)


def cortina_tecido(img, caixa, lado):
    """O tecido da cortina na caixa (px): o claro sem cor (croma < 30) ligado ao lado de fora (`lado` "esq": a coluna
    da esquerda da caixa)."""
    x0, y0, x1, y1 = caixa
    sub = img[y0:y1, x0:x1].astype(np.int16)
    baixo = ((sub.max(axis=2) - sub.min(axis=2)) < 30).astype(np.uint8)
    n, lab = cv2.connectedComponents(baixo, connectivity=4)
    borda = lab[:, :3] if lado == "esq" else lab[:, -3:]
    m = np.isin(lab, np.unique(borda[borda > 0]))
    out = np.zeros(img.shape[:2], bool)
    out[y0:y1, x0:x1] = m
    return out


# (usuário: "o piso tem que ter cntinuidade sem quebras e sem montagens inapropriadas") o piso de cada suíte refeito
# inteiro, de parede a parede (a face de dentro das paredes medida da cama; do lado da janela, até o tecido da cortina),
# numa luz só, a larga do próprio piso do quarto: sem as emendas entre o piso refeito e restos de limpezas antigas (a
# faixa borrada junto ao criado da master). Ficam: as paredes, o tecido das cortinas, as folhas das portas
# (`portas_casae_1711.portas`) e as escrivaninhas (o tampo é refeito em `retoques`).
QUARTOS = {"suíte master": (1406, 566, 1733, 883), "suíte 2": (2225, 683, 2484, 921),
           "suíte 1": (2225, 1050, 2484, 1289), "suíte 4": (1406, 892, 1739, 1106),
           "suíte 3": (1406, 1315, 1739, 1530)}
_FOLHAS = {}


def folhas_portas(img):
    """As folhas das portas de giro do 1º Pavimento (px), como `portas_casae_1711` as acha no PDF."""
    if "f" not in _FOLHAS:
        import portas_casae_1711 as PC
        with contextlib.redirect_stdout(io.StringIO()):
            _FOLHAS["f"] = [p["folha"] for p in PC.portas("1Pavimento", img).values()]
    return _FOLHAS["f"]


def piso_suite(Q, out, nome, s):
    import regras_terreo_casab_1311 as RT
    par = paredes(Q, 0.5)
    H, W = par.shape
    x0, y0, x1, y1 = QUARTOS[nome]
    b = np.zeros((H, W), bool)
    b[y0:y1, x0:x1] = True
    cx0, cy0, cx1, cy1 = s["cortina"]
    lado = "esq" if cx0 < 2000 else "dir"
    caixa = (cx0 + 8, cy0, cx1 + 6, cy1) if lado == "esq" else (cx0 - 6, cy0, cx1 - 8, cy1)
    b &= ~RT.dilatar(cortina_tecido(out, caixa, lado), 1)
    b &= ~RT.dilatar(par, 1)
    for fx0, fy0, fx1, fy1 in folhas_portas(out):
        b[int(fy0) - 2:int(np.ceil(fy1)) + 2, int(fx0) - 2:int(np.ceil(fx1)) + 2] = False
    if "mesa" in s:
        mx0, my0, mx1, my1 = s["mesa"]
        b[int(my0) - 1:int(np.ceil(my1)) + 1, int(mx0) - 1:int(np.ceil(mx1)) + 1] = False
    return vinilico_novo(Q, out, b, luz_dentro=True)


def _mediana(v, k):
    r = k // 2
    pad = np.pad(v, r, mode="edge")
    return np.median(np.stack([pad[i:i + len(v)] for i in range(k)]), axis=0)


def sofa_alfa(img, s=SALA_INTIMA):
    """A pegada (0..1) do sofá em L do render: o L inteiro (`sofa`), recortado nas bordas que dão para o tapete
    (`sofa_bordas`: retângulo e lado, "x+" o sofá à esquerda, "y+" o sofá acima). Em cada linha (ou coluna) da borda, de
    fora para dentro, a sombra do render (mais escura que `sofa_limiar`) sai até o 1º px do estofado, com a fração de
    px da passagem; a mediana ao longo da borda (`sofa_mediana` px) tira o pente da textura do tapete velho, e a borda
    sai reta, com os cantos arredondados do próprio sofá."""
    H, W = img.shape[:2]
    a = np.zeros((H, W), np.float32)
    for x0, y0, x1, y1 in s["sofa"]:
        a[y0:y1, x0:x1] = 1
    lum = img.astype(np.float32).mean(axis=2)
    lim = float(s["sofa_limiar"])
    for (x0, y0, x1, y1), lado, *ate in s["sofa_bordas"]:
        sub = lum[y0:y1, x0:x1]
        if lado == "x+":
            sub = sub.T                                   # cada coluna de `sub`: uma linha da imagem, de dentro p/ fora
        n = sub.shape[0]
        fora = sub < lim
        k = np.argmin(fora[::-1], axis=0)                 # os px escuros seguidos, a partir de fora
        k[fora.all(axis=0)] = n
        j = n - k
        e = j.astype(np.float32)
        ok = (j > 0) & (j < n)
        c = np.nonzero(ok)[0]
        p_in, p_out = sub[j[c] - 1, c], sub[j[c], c]
        e[c] = j[c] - 0.5 + np.clip((p_in - lim) / np.maximum(p_in - p_out, 1e-3), 0, 1)
        e = _mediana(e, s["sofa_mediana"])
        if ate:
            e = np.minimum(e, ate[0] - (x0 if lado == "x+" else y0))
        b = np.clip(e[None, :] - np.arange(n, dtype=np.float32)[:, None], 0, 1)
        a[y0:y1, x0:x1] *= b.T if lado == "x+" else b
    # um px claro solto na sombra (fora do L) não volta
    n, rot, st, _ = cv2.connectedComponentsWithStats((a > 0).astype(np.uint8))
    if n > 2:
        a[rot != 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 0
    return a


def sofa_sobre_tapete(out, img, s, com):
    """O sofá do render (`img`) por cima de `com` (o tapete novo inteiro), recortado em `sofa_alfa`; a sombra de
    contato (a dos móveis da biblioteca) cai só no que é novo: o tapete e o piso refeito junto ao braço."""
    import biblioteca_terreo_casaa_1211 as BT
    import mobiliario_terreo_casac_1311 as MB
    a = sofa_alfa(img, s)
    H, W = a.shape
    novo = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in (s["tapete"], s["lateral_sofa_antes"], s["piso_quina"]):
        novo[int(y0):int(np.ceil(y1)), int(x0):int(np.ceil(x1))] = True
    f = np.ones((H, W), np.float32)
    for sb in BT.SOMBRAS["movel"]:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, sb["sig"] * MB.PX_M))
        M = np.float32([[1, 0, sb["dx"] * MB.PX_M], [0, 1, sb["dy"] * MB.PX_M]])
        f *= 1 - sb["forca"] * cv2.warpAffine(sh, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    c = com.astype(np.float32)
    c[novo] *= f[novo][:, None]
    r = c * (1 - a[..., None]) + img.astype(np.float32) * a[..., None]
    return np.clip(np.round(r), 0, 255).astype(np.uint8)


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
        out = piso_suite(Q, out, nome, s)
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
    out = quieto(RV.bancos, out, dict(RV.BANCOS, png=BANCO,
                                      bancos=[(n, tuple(map(float, r)), g) for n, r, g in bancos]))
    # a sala íntima
    s = SALA_INTIMA
    out = limpar_piso(Q, out, s["poltrona_antes"], MADEIRA, nao_luz=[(1860, 1200, 2116, 1392)])
    out = limpar_piso(Q, out, s["lateral_sofa_antes"], MADEIRA, nao_luz=[(1860, 1200, 2070, 1340), (1876, 1235, 2116, 1392)])
    out = limpar_piso(Q, out, s["piso_quina"], MADEIRA, nao_luz=[(1845, 1190, 1924, 1339), (1876, 1235, 2116, 1392)])
    tapete = ler("sala-intima/tapete-intimo-e")
    m = s["tapete_borda"]
    tapete = np.ascontiguousarray(tapete[m:-m, m:-m])
    tapete[..., 3] = 255
    # pousado 1 px maior e recortado a seco no retângulo: as 4 bordas retas, sem a coluna meio tapete, meio piso
    x0, y0, x1, y1 = s["tapete"]
    com = pos(out, tapete, (x0, y0, x1 + 2, y1 + 2), (0, 1), None)
    seco = np.zeros(out.shape[:2], bool)
    seco[y0:y1 + 1, x0:x1 + 1] = True
    out = sofa_sobre_tapete(out, img, s, np.where(seco[..., None], com, out))
    # (usuário: "represente as mesas redondas corretamente") no PDF, as duas mesas de centro são redondas, encaixadas: a
    # menor (0,7 m) por baixo da maior (1,0 m), à direita; a menor, que saía retangular (`mesa-lateral-metal-madeira`),
    # na mesma mesa redonda da biblioteca, em nogueira
    out = pos(out, MBE.tingir_madeira(ler("sala-intima/mesa-intima-redonda-e"), s["nogueira"]), s["lateral"], (0, 1),
              "mesa")
    out = pos(out, ler("sala-intima/mesa-intima-redonda-e"), s["mesa"], (0, 1), "mesa")
    cx, cy, dm = s["lateral_sofa"]
    out = MBE.pousar(out, ler("sala-intima/mesa-intima-redonda-e"), cx, cy, dm, dm, 0.0, "mesa", par)
    out = pos(out, ler("sala-intima/poltrona-intima-e"), s["poltrona"], (-1, 0), "movel", troca=True)
    # a copinha e a rouparia
    c = COPINHA
    out = out.copy()
    a0, b0, a1, b1 = c["parede"]
    out[b0:b1, a0:a1] = PAREDE
    out = copiar_piso(out, *c["piso_resto"])
    out = armario_liso(out, [c["armario"]], par)
    x0, y0, x1, y1 = c["tampo"]
    out = MBE.pousar(out, tampo_aura(x1 - x0, y1 - y0, c), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, None,
                     par)
    cx, cy, cw, chh = c["cuba"]
    out = MBE.pousar(out, ler("copinha/cuba-franke-misturador-unic"), cx, cy, cw, chh, MB.frente((0, -1)), "baixa", par)
    out = armario_liso(out, [ROUPARIA_MOVEIS["estante"], ROUPARIA_MOVEIS["nichos"]], par)
    print(f"    mobiliário: {', '.join(SUITES)} (tapete, cama, criados, banco K3, cadeira sob o tampo; poltrona e criado "
          "redondo na master); sala íntima (tapete, mesa de centro, mesa lateral redonda, poltrona; o sofá fica); copinha (tampo, cuba "
          "Franke, armário liso no tom das outras casas, sem as linhas técnicas); rouparia (o armário liso em L, no tom das "
          "outras casas)")
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
    ("varanda principal (em cima)", "varanda-principal/palmeira-folha-fina-4k", (1177, 545, 1285, 668),
     (1229.0, 590.0), 60.0, (0, 125), 64.0),
    ("varanda principal (embaixo)", "varanda-principal/palmeira-folha-fina-4k", (1177, 1446, 1264, 1531),
     (1218.0, 1490.0), 56.0, (0, -170), 60.0),
    ("varanda da suíte 1", "varanda-da-suite-1/palmeira-roseta-4k", (2496, 1208, 2554, 1286),
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
# os que não mudam na limpeza: só os caixilhos e o guarda-corpo (as 3 primeiras de `FOLHAGENS_NAO_LUZ`); os vasos de
# terracota saem com o resto (antes ficavam e deixavam um quadrado do piso velho em volta da mesa e da poltrona, com
# folhas). O piso refeito vai ao tom do piso em volta (`regras_terreo_casab_1311.tom_do_entorno`: a média local do anel
# em volta, estendida para dentro), sem os degraus de tom nas bordas das cópias deslocadas: `tom_suave`, por região.
FOLHAGENS_FICAM = FOLHAGENS_NAO_LUZ[:3]
FOLHAGENS_TOM = {"sigma": 22.0, "pena": 2.0, "lum": 22, "quente": 8, "k": 1e-3}


def tom_suave(out, buraco, fonte, q=FOLHAGENS_TOM):
    """Cada região do `buraco` (o piso refeito) no tom local do piso de em volta: D = T - C, T a média local (gaussiana
    larga, normalizada) da `fonte` de cor parecida em volta (a luminância e o quente, R - B, perto dos do buraco: sem
    os caixilhos cinza-azulados), C a do próprio buraco; longe da fonte, T vai à média dela na região (`k`); somado
    com a borda suave."""
    o = out.astype(np.float32)
    s = q["sigma"]
    n, lab, st, _ = cv2.connectedComponentsWithStats(buraco.astype(np.uint8), 8)
    H, W = buraco.shape
    for i in range(1, n):
        x, y, w, h, _ = st[i]
        g = int(3 * s) + 4
        X0, Y0, X1, Y1 = max(x - g, 0), max(y - g, 0), min(x + w + g, W), min(y + h + g, H)
        reg = o[Y0:Y1, X0:X1]
        b = (lab[Y0:Y1, X0:X1] == i)
        lum, quente = reg.mean(axis=2), reg[..., 2] - reg[..., 0]
        f = (fonte[Y0:Y1, X0:X1] & ~buraco[Y0:Y1, X0:X1] & (np.abs(lum - np.median(lum[b])) < q["lum"])
             & (np.abs(quente - np.median(quente[b])) < q["quente"]))
        bf, ff = b.astype(np.float32), f.astype(np.float32)
        k = q["k"]
        Tg = reg[f].mean(axis=0) if f.any() else reg[b].mean(axis=0)
        T = (cv2.GaussianBlur(reg * ff[..., None], (0, 0), s) + k * Tg) / (cv2.GaussianBlur(ff, (0, 0), s) + k)[..., None]
        Cg = reg[b].mean(axis=0)
        C = (cv2.GaussianBlur(reg * bf[..., None], (0, 0), s) + k * Cg) / (cv2.GaussianBlur(bf, (0, 0), s) + k)[..., None]
        wgt = np.maximum(cv2.GaussianBlur(bf, (0, 0), q["pena"]), bf)
        wgt[fonte[Y0:Y1, X0:X1] == 0] *= b[fonte[Y0:Y1, X0:X1] == 0]
        reg += wgt[..., None] * (T - C)
    return u8(o)
FLOREIRA = {"jpg": BIB / "banho-master/floreira-3-costelas-4k.png", "caixa": (1744, 446, 1778, 528), "borda_px": 2.0,
            "borda": 0.75}
# a entrada do Topaz sem as plantas (só os vasos com a terra): as folhas 4K e a floreira entram direto no 12K
# (`folhas_12k`), como a cascata do Subsolo (usuário: "traga a cascata em 4K [...] senão vai sair muito distorcido")
SEM_FOLHAS = False


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
    for a0, b0, a1, b1 in FOLHAGENS_FICAM:
        ficam_base[b0:b1, a0:a1] = True
    feito = np.zeros(par.shape, bool)
    # o canto de baixo da varanda principal: os círculos de antes saem
    v = VARANDA_CANTO
    for x0, y0, x1, y1 in v["limpa"]:
        m = np.zeros(par.shape, bool)
        m[y0:y1, x0:x1] = True
        out = piso_deslocado(out, m & ~ficam_base, *v["desloc"], suave=3.0)
        feito |= m & ~ficam_base
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
            feito |= m & ~par & ~ficam_base
        for (a0, b0, a1, b1), dx in FOLHAGENS_FAIXAS:
            if a0 < x1 and a1 > x0 and b0 < y1 + 30 and b1 > y0:
                out[b0:b1, a0:a1] = img[b0:b1, a0 + dx:a1 + dx]
        plantas.append((rel, cx, cy, lado, dv))
    # o piso refeito no tom do de em volta (com a folga da borda suave das cópias)
    out = tom_suave(out, feito & ~ficam_base, ~RT.dilatar(par, 1) & ~ficam_base)
    # a mesa e a poltrona do canto, depois os vasos e as plantas por cima
    cx, cy, d = v["mesa"]
    out = MBE.pousar(out, ler("varanda-principal/mesa-lateral-externa"), cx, cy, d, d, 0.0, "mesa", par)
    cx, cy, d, fr = v["poltrona"]
    out = MBE.pousar(out, ler("varanda-principal/poltrona-externa-b"), cx, cy, d, d, MB.frente(fr), "movel", par)
    for rel, cx, cy, lado, dv in plantas:
        out = MBE.pousar(out, V, cx, cy, dv, dv, 0.0, "movel", par)
        if not SEM_FOLHAS:
            out = MBE.pousar(out, ler(rel), cx, cy, lado, lado, 0.0, "baixa", par)
    if SEM_FOLHAS:
        print("    (sem as plantas, só os vasos: a entrada do Topaz; as folhas 4K vão direto no 12K)")
    # a floreira
    out[f["caixa"][1]:f["caixa"][3], f["caixa"][0]:f["caixa"][2]] = floreira_peca(f)
    print(f"    folhagens 4K: {', '.join(n for n, *_ in q)} em vasos de concreto (as plantas de antes no piso de em volta) e "
          "a floreira do banho master; no canto de baixo da varanda principal, a mesa lateral e a poltrona externas")
    return out


def floreira_peca(f=FLOREIRA, w=None, h=None):
    """A folhagem 4K da floreira no tamanho da caixa (w x h px; sem eles, o da caixa na final), as bordas escurecidas
    (`borda_px` na escala da final)."""
    x0, y0, x1, y1 = f["caixa"]
    esc = 1.0 if w is None else w / (x1 - x0)
    w, h = (x1 - x0, y1 - y0) if w is None else (w, h)
    T = cv2.imread(str(f["jpg"]))
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
    T *= (f["borda"] + (1 - f["borda"]) * np.clip(d / (f["borda_px"] * esc), 0, 1))[..., None]
    return u8(T)


def folhas_12k(out, mapa, Q=None, q=FOLHAGENS, f=FLOREIRA):
    """As plantas 4K e a floreira direto no 12K (`out`, uint8, mudado no lugar): `mapa(caixa)` dá o `Mapa` da final ao
    12K afinado em volta da caixa (px da final); a planta no centro e no lado da final vezes a escala, com a sombra curta
    na escala do 12K; as paredes (`paredes`) levadas ao 12K não mudam."""
    import biblioteca_terreo_casaa_1211 as BT
    import mobiliario_terreo_casac_1311 as MB
    Q = Q or FE.QuadroE("1Pavimento")
    par = paredes(Q, 0.5).astype(np.uint8)
    for nome, rel, _, (cx, cy), lado, _, dv in q:
        m = mapa((int(cx - dv), int(cy - dv), int(cx + dv), int(cy + dv)))
        folga = int(np.ceil(dv * m.s))
        X0, Y0 = int(m.x(cx)) - folga, int(m.y(cy)) - folga
        X1, Y1 = int(m.x(cx)) + folga, int(m.y(cy)) + folga
        Mp = np.float64([[m.s, 0, m.t[0] + 0.5 - 0.5 * m.s - X0], [0, m.s, m.t[1] + 0.5 - 0.5 * m.s - Y0]])
        nao = cv2.warpAffine(par, Mp, (X1 - X0, Y1 - Y0), flags=cv2.INTER_NEAREST) > 0
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        o = BT.pousar(reg, ler(rel), m.x(cx) - 0.5 - X0, m.y(cy) - 0.5 - Y0, lado * m.s, lado * m.s, 0.0,
                      BT.SOMBRAS["baixa"], MB.PX_M * m.s, nao=nao)
        out[Y0:Y1, X0:X1] = u8(o)
        print(f"    {nome}: a planta 4K direto no 12K, a {m.s:.4f}x ({lado * m.s:.0f} px)")
    x0, y0, x1, y1 = f["caixa"]
    m = mapa((x0 - 14, y0 - 10, x1 + 14, y1 + 10))
    X0, Y0, X1, Y1 = m.reti(f["caixa"])
    out[Y0:Y1, X0:X1] = floreira_peca(f, X1 - X0, Y1 - Y0)
    print(f"    a floreira do banho master: a folhagem 4K direto no 12K ({X1 - X0} x {Y1 - Y0} px)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 13. Os retoques depois do 12K (usuário, 18/11):
# - "corrija esse erro do móvel da suite master e melhore a representação e tom do móvel": os racks de TV das 5 suítes
#   e o da sala íntima
#   (no PDF, ARQ_LAYOUT HUMANIZAÇÃO, 2,0 a 2,2 x 0,40 m) pelo aparador de freijó da biblioteca da E (hall), esticado no
#   comprido (o veio é no comprido), a frente para o quarto; a TV do PDF (5 cm) por cima, em grafite, junto à parede;
# - "corrigir esse traço preto em volta da escrivaninha, remover": o tampo das 4 escrivaninhas refeito liso, na madeira
#   dele (a mediana), com o veio no comprido e a sombra curta, sem o fio escuro da borda; os objetos de cima (o notebook,
#   o monitor, a luminária) voltam como estavam;
# - "na suite 2 [...] trocar a porta pelo modelo que usamos de madeira": a folha aberta do PDF na madeira clara das
#   portas da Casa D (`portas_casae_1711.folha`);
# - "remover esses traços do piso do closet da suite master": a faixa de piso refeita em réguas (`vinilico_novo`) e a
#   sombra curta dos armários contínua nas duas bordas (no lugar dos tracinhos).
RACKS = [("suíte master", (1502.3, 859.1, 1633.6, 883.0), (1524.1, 878.6, 1604.5, 881.6), (0, -1)),
         ("suíte 2", (2330.1, 897.9, 2449.5, 921.8), (2351.9, 917.4, 2432.3, 920.4), (0, -1)),
         ("suíte 1", (2330.1, 1265.1, 2449.5, 1289.0), (2351.9, 1284.6, 2432.3, 1287.6), (0, -1)),
         ("suíte 4", (1446.8, 1083.0, 1566.2, 1106.9), (1468.6, 1102.5, 1549.0, 1105.5), (0, -1)),
         ("suíte 3", (1452.0, 1315.9, 1571.4, 1339.7), (1469.2, 1317.2, 1549.7, 1320.2), (0, 1)),
         ("sala íntima", (1888.5, 1417.4, 2067.6, 1441.2), (1934.9, 1436.9, 2015.4, 1439.9), (0, -1))]
# o piso de baixo do rack de antes que não vem das suítes (o da sala íntima), refeito em réguas antes do novo
RACKS_LIMPA = [(1884, 1412, 2082, 1442)]
RACK = {"png": CASA / "biblioteca-objetos/02-terreo/hall-de-entrada/aparador-freijo.png", "tv": (36, 36, 38),
        "tv_borda": (78, 78, 80), "tv_sombra": 0.35}
ESCRIVANINHAS = [("suíte 2", (2226.0, 683.0, 2261.7, 823.0)), ("suíte 1", (2226.0, 1050.0, 2261.7, 1190.0)),
                 ("suíte 4", (1703.3, 892.0, 1739.0, 1032.0)), ("suíte 3", (1703.3, 1390.0, 1739.0, 1531.0))]
# (usuário: "deixe as 4 escrivaninhas no mesmo tom") o tampo das 4 num tom só, o claro das suítes 3 e 4 (BGR; o das
# suítes 1 e 2 era o mesmo do vinílico, 110/145/186, e o tampo sumia no piso)
ESCRIVANINHA = {"objeto": 30, "objeto_min_px": 5, "margem_px": 3, "veio": 0.035, "sombra": 0.20, "semente": 1813,
                "tom": (139.0, 173.0, 205.0)}
# (usuário: "remova erros sobre a escrivaninha. deixe um teclado Apple em alta definição sobre a escrivaninha", "remova
# residuos sobre a escrivaninha e substitua o teclado pelo teclado Apple") os objetos de antes do tampo (os pontinhos, o
# bloco claro, a bolinha, o monitor borrado com a mancha marrom e o teclado branco) não voltam; no tampo liso, um monitor
# de alumínio visto de cima (o topo da tela, o vidro escuro na frente, o pé) junto à parede e o teclado Apple na frente,
# os dois no eixo da cadeira e em tamanho real (Studio Display 62,3 cm; Magic Keyboard 27,9 cm). As peças foram feitas
# no Higgsfield sobre o preto e recortadas (`suite-4/monitor-apple-studio`, `suite-4/teclado-apple-magic`); no 12K entram
# direto, nítidas (`computadores_12k`)
COMPUTADOR = {"teclado": BIB / "suite-4/teclado-apple-magic.png", "monitor": BIB / "suite-4/monitor-apple-studio.png",
              "teclado_m": 0.279, "monitor_m": 0.623, "monitor_parede_px": 8.0, "teclado_frente_px": 12.0}
PORTA_SUITE2 = {"folha": (2225.6, 905.9, 2279.4, 908.3), "semente": 1814}
# (usuário: "refazer as portas de correr do closet da suite master") as 2 folhas de correr do vão banho master / closet
# master (ARQ_PAREDE) saíam num traço só, de ponta a ponta (o trecho entre elas também): cada folha de novo na madeira das
# portas, separadas; entre elas, o piso do closet
PORTAS_CLOSET = {"folhas": [(1954.3, 587.6, 1956.7, 623.4), (1954.3, 647.3, 1956.7, 683.1)],
                 "entre": (1954, 623, 1960, 648), "semente": 1817}
CLOSET_MASTER = {"faixa": (1956, 599, 2216, 672), "miolo": (1977, 605, 2195, 664), "sombras": {599: 0.82, 600: 0.72, 601: 0.90, 668: 0.92, 669: 0.82,
                                                              670: 0.70, 671: 0.84}}


def escrivaninha(out, r, semente, q=ESCRIVANINHA):
    import correcoes_terreo_casab_1611 as CB
    x0, y0, x1, y1 = r
    X0, Y0, X1, Y1 = int(x0) - 6, int(y0) - 6, int(np.ceil(x1)) + 6, int(np.ceil(y1)) + 6
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    a = CB.alfa_ret((x0 - X0, y0 - Y0, x1 - X0, y1 - Y0), forma)
    m = q["margem_px"]
    dentro = CB.alfa_ret((x0 - X0 + m, y0 - Y0 + m, x1 - X0 - m, y1 - Y0 - m), forma) > 0.99
    med = np.median(reg[dentro], axis=0)
    obj = dentro & (np.abs(reg - med).max(axis=2) > q["objeto"])
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj.astype(np.uint8))
    obj = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= q["objeto_min_px"]])
    obj = cv2.dilate(obj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & dentro
    antes = reg.copy()
    # a sombra curta, fora do tampo
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -0.8], [0, 1, 1.0]]), (forma[1], forma[0])), (0, 0), 1.0)
    reg *= (1 - q["sombra"] * sb * (1 - a))[..., None]
    rng = np.random.default_rng(semente)
    nn = cv2.GaussianBlur(rng.normal(0, 1, forma).astype(np.float32), (0, 0), sigmaX=0.6, sigmaY=6.0)
    nn = 1 + q["veio"] * nn / max(float(nn.std()), 1e-6)
    tampo = np.float32(q.get("tom", med))[None, None] * nn[..., None]
    reg = reg * (1 - a[..., None]) + tampo * a[..., None]
    if q.get("objetos_voltam", False):
        ao = cv2.GaussianBlur(obj.astype(np.float32), (0, 0), 0.6)
        reg = reg * (1 - ao[..., None]) + antes * ao[..., None]
    out[Y0:Y1, X0:X1] = u8(reg)
    return int(obj.sum())


def _computadores(q=COMPUTADOR):
    """Por escrivaninha: (peça, cx, cy, comprimento px, profundidade px, frente) do monitor e do teclado (px da final)."""
    import mobiliario_terreo_casac_1311 as MB
    res = []
    for nome, (x0, y0, x1, y1) in ESCRIVANINHAS:
        (c0, c1, c2, c3), d = SUITES[nome]["cadeira"]
        cy = (c1 + c3) / 2
        fr = (-d[0], -d[1])                     # o monitor e o teclado olham para a cadeira
        if d == (-1, 0):                        # a cadeira à direita: a parede à esquerda
            xm, xt = x0 + q["monitor_parede_px"], x1 - q["teclado_frente_px"]
        else:
            xm, xt = x1 - q["monitor_parede_px"], x0 + q["teclado_frente_px"]
        for peca, x, m in (("monitor", xm, q["monitor_m"]), ("teclado", xt, q["teclado_m"])):
            P = cv2.imread(str(q[peca]), cv2.IMREAD_UNCHANGED).astype(np.float32)
            L = m * MB.PX_M
            res.append((P, x, cy, L, L * P.shape[0] / P.shape[1], fr, peca))
    return res


def computadores(out, par):
    import mobiliario_terreo_casac_1311 as MB
    for P, cx, cy, L, D, fr, peca in _computadores():
        out = MB.pousar(out, P, cx, cy, L, D, MB.frente(fr), "mesa" if peca == "monitor" else "baixa", par)
    return out


def computadores_12k(out, mapa):
    """O monitor e o teclado direto no 12K (`out`, uint8, mudado no lugar), nítidos, sem a sombra (a da final fica)."""
    import biblioteca_terreo_casaa_1211 as BT
    import mobiliario_terreo_casac_1311 as MB
    n = 0
    for P, cx, cy, L, D, fr, peca in _computadores():
        g = int(L / 2) + 4
        m = mapa((int(cx) - g, int(cy) - g, int(cx) + g + 1, int(cy) + g + 1))
        X, Y = m.x(cx) - 0.5, m.y(cy) - 0.5
        G = int(g * m.s) + 4
        X0, Y0 = int(X) - G, int(Y) - G
        reg = out[Y0:Y0 + 2 * G, X0:X0 + 2 * G].astype(np.float32)
        o = BT.pousar(reg, P, X - X0, Y - Y0, L * m.s, D * m.s, MB.frente(fr), [], MB.PX_M * m.s)
        out[Y0:Y0 + 2 * G, X0:X0 + 2 * G] = u8(o)
        n += 1
    print(f"    {n} peças (monitor e teclado Apple) direto no 12K")
    return out


def rack(out, r, tv, frente, par, q=RACK):
    import correcoes_terreo_casab_1611 as CB
    import mobiliario_terreo_casac_1311 as MB
    import mobiliario_terreo_casae_1611 as MBE
    P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
    x0, y0, x1, y1 = r
    out = MBE.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, MB.frente(frente), "mesa", par)
    o = out.astype(np.float32)
    H, W = par.shape
    a = CB.alfa_ret(tv, (H, W))
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -0.6], [0, 1, 0.8]]), (W, H)), (0, 0), 0.8)
    o *= (1 - q["tv_sombra"] * sb * (1 - a))[..., None]
    tx0, ty0, tx1, ty1 = tv
    face = CB.alfa_ret((tx0, ty0, tx1, ty0 + 1.0) if frente == (0, 1) else (tx0, ty1 - 1.0, tx1, ty1), (H, W))
    face = np.minimum(face, a)
    cor = np.float32(q["tv"])[None, None] * (1 - face[..., None]) + np.float32(q["tv_borda"])[None, None] * face[..., None]
    return u8(o * (1 - a[..., None]) + cor * a[..., None])


# (usuário: "corrigir as paredes, colocar o tom certo - suite 2") trechos de parede do render que ficaram quase pretos
# (a parede entre o closet 2 e a escrivaninha da suíte 2, a de cima da suíte 1, fios escuros junto às faces): o px de
# parede do PDF (a cobertura da ARQ_PAREDE) escuro vai ao cinza 80 das paredes (26/10); na borda, a mistura do cinza
# com o de fora pela cobertura do PDF
PAREDES_TOM = {"escuro": 60, "cinza": (80, 80, 80)}
# (usuário: "painel de madeira segue no modelo adotado nas outras casas") a faixa de madeira por fora das folhas de vidro
# das suítes 3, 4 e master, do lado da varanda principal (do render, marrom liso), no ripado de nogueira da Casa D
# (`correcoes_terreo_casad_1711._ripado` com `um_pav_casaa_1111.FOLHAS_1P`, o do L da suíte master da D e das ripas do
# escritório do Térreo da E): o veio ao longo, as juntas das ripas, a luz, o contorno e a sombra curta para a varanda
# ("o painel é ambos os lados da casa") e a faixa da fachada da direita, por fora das varandas das suítes 1 e 2
# (usuário: "nos paineis de madeira no 3D tem diversos marcadores/separadores como folhas que se abrem. preciso que
# adicione nos locais, conforme o 3d") o painel folha por folha, como as folhas amadeiradas da Casa A
# (`um_pav_casaa_1111.folhas_1p`: cada folha com o seu contorno), com o vão escuro entre elas (`PAINEL_FOLHAS`), nos
# `cortes` (px, y): à esquerda, os do PDF (ARQ_PAREDE): os marcos das portas de correr das suítes master, 4 e 3 e os
# montantes entre as folhas de vidro delas (os quadradinhos de 3 x 4,8 px: 3 folhas de 1,5 m na master, de 1 m na 4 e na
# 3) e os marcos das janelas dos banhos 4 e 3; à direita, os marcos das janelas dos banhos 2 e 1 e as pontas das
# varandas das suítes 2 e 1, cujo vão de 4 m (o guarda-corpo, sem montantes no PDF) vai em 4 folhas de 1 m, o módulo das
# suítes 3 e 4
PAINEIS = [{"ret": (1389.6, 535.0, 1395.7, 1533.5), "lado": "x-", "semente": 1818,
            "cortes": [595.8, 687.5, 776.9, 868.6, 906.3, 969.1, 1029.7, 1092.5, 1133.0, 1192.7, 1232.3, 1292.0,
                       1330.2, 1393.1, 1453.6, 1516.5]},
           {"ret": (2565.4, 555.0, 2571.5, 1287.5), "lado": "x-", "semente": 1819,
            "cortes": [590.4, 650.1, 682.9, 742.6, 802.3, 862.0, 921.7, 957.6, 1017.3, 1050.1, 1109.8, 1169.5,
                       1229.2]}]
PAINEL_FOLHAS = {"vao_px": 1.1, "vao": (20, 26, 34)}
# (usuário: "melhore o aspecto de todos os guarda corpo, com uma folha de vidro contínua") os 8 guarda-corpos do PDF
# (ARQ_ELEMENTOS FIXOS, as faixas de 1,2 px): a varanda principal (em cima, à esquerda e embaixo), as varandas das suítes
# 2 e 1 (à direita, até o painel), o L do vazio da escada e o do jardim da sala íntima. A faixa cinza de antes (as duas
# linhas e as bordas, 4 a 8 px) sai: para dentro, o piso de logo ao lado (`dentro_px`); para fora, o piso até a borda da
# laje ou do painel (`ate`, px) ou o que há do lado de fora (`fora_px`). Depois, uma folha de vidro só, de ponta a ponta,
# no desenho dos guarda-corpos da Casa A (`terreo_casaa_1011.vidro_laminas`: o vidro claro, as faces em linha fina, o
# brilho no meio e a sombra curta), antes dos painéis
GUARDA_CORPOS = [
    # (retângulo px, lado de dentro (+1: x/y maiores), `dentro_px`: até a borda escura do piso de dentro, "ate": a borda
    # da laje/do painel ou "fora_px": a faixa de fora; "longo": o trecho ao longo, até os cantos; na ordem: a fonte da
    # limpeza é a imagem já limpa pelos de antes, e os cantos da varanda principal saem limpos)
    {"ret": (1168.2, 533.1, 1169.4, 1534.4), "dentro": +1, "dentro_px": 8.5, "ate": 1163.6, "longo": (528.6, 1541.5)},
    {"ret": (1168.2, 533.1, 1395.7, 534.3), "dentro": +1, "dentro_px": 10.0, "ate": 528.6, "longo": (1163.6, 1389.6),
     "folga": 1},
    {"ret": (1168.2, 1533.2, 1395.7, 1534.4), "dentro": -1, "dentro_px": 5.0, "ate": 1541.5, "longo": (1163.6, 1389.6)},
    {"ret": (2559.4, 682.9, 2560.6, 921.7), "dentro": -1, "dentro_px": 4.0, "ate": 2565.4},
    {"ret": (2559.4, 1050.1, 2560.6, 1288.9), "dentro": -1, "dentro_px": 4.0, "ate": 2565.4},
    {"ret": (1872.6, 1044.2, 1873.8, 1124.0), "dentro": -1, "dentro_px": 5.0, "fora_px": 1.4},
    {"ret": (1872.6, 1122.8, 2216.7, 1124.0), "dentro": +1, "dentro_px": 3.5, "fora_px": 0.0},
    {"ret": (2219.1, 1327.8, 2220.3, 1548.7), "dentro": -1, "dentro_px": 4.0, "fora_px": 2.4},
]
GUARDA_CORPO = {"folga": 3, "foge": 18, "ao_longo": (90, -90, 150, -150, 60, -60), "tom_px": 3, "tom_sigma": 10.0,
                "tom_lim": (0.88, 1.12)}


# (usuário: "limpe esse residuo no canto do armario do closet 1", "limpe essa sujeira no piso do closet 3", "limpe também
# esses borrões no piso do closet 4") o piso dos closets 1, 3 e 4 (a caixa de dentro do L dos armários, até a porta)
# refeito em réguas contínuas (`vinilico_novo`, a luz do próprio piso), fora as paredes, os armários (o claro sem cor)
# e as folhas das portas
CLOSETS_PISO = {"closet 1": (2261, 969, 2351, 1050), "closet 4": (1614, 1106, 1702, 1172),
                "closet 3": (1614, 1244, 1702, 1315), "armario_lum": 185, "armario_sat": 60}


def pisos_closets(Q, out, q=CLOSETS_PISO):
    par = paredes(Q, 0.5)
    H, W = par.shape
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV)
    armario = (out.mean(axis=2) > q["armario_lum"]) & (hsv[..., 1] < q["armario_sat"])
    folhas = np.zeros((H, W), bool)
    for fx0, fy0, fx1, fy1 in folhas_portas(out):
        folhas[int(fy0):int(np.ceil(fy1)), int(fx0):int(np.ceil(fx1))] = True
    for nome in ("closet 1", "closet 4", "closet 3"):
        x0, y0, x1, y1 = q[nome]
        b = np.zeros((H, W), bool)
        b[y0:y1, x0:x1] = True
        out = vinilico_novo(Q, out, b & ~par & ~armario & ~folhas, luz_dentro=True)
    return out


def _faixa(vert, a0, a1, c0, c1):
    return (slice(a0, a1), slice(c0, c1)) if vert else (slice(c0, c1), slice(a0, a1))


def _fonte_piso(out, vert, a0, a1, c0, c1, desl, q):
    """O piso para a faixa (a0:a1 ao longo, c0:c1 de través) a `desl` px de través; onde a fonte foge do piso (um vaso,
    uma peça), o piso das mesmas linhas mais adiante ou mais atrás ao longo (`ao_longo`)."""
    f = out[_faixa(vert, a0, a1, c0 + desl, c1 + desl)].astype(np.float32)
    med = np.median(f.reshape(-1, 3), axis=0)
    ruim = np.abs(f - med).max(axis=2) > q["foge"]
    ruim = cv2.dilate(ruim.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    for k in q["ao_longo"]:
        if not ruim.any():
            break
        b0, b1 = a0 + k, a1 + k
        if b0 < 0 or b1 > (out.shape[0] if vert else out.shape[1]):
            continue
        g = out[_faixa(vert, b0, b1, c0 + desl, c1 + desl)].astype(np.float32)
        bom = np.abs(g - med).max(axis=2) <= q["foge"]
        usa = ruim & bom
        f[usa] = g[usa]
        ruim &= ~usa
    return f


# a claraboia da rouparia: o retângulo inteiro do PDF (a rotina cortava os lados em volta do rótulo do PDF, que não é
# o da final), e o traço só para sob o texto do rótulo da final ("ROUPARIA / A: 3,6 m²", 2108 a 2161 x 767 a 790 px,
# com 3 px de folga)
CLARABOIA_ROUPARIA = {"sob_rotulo": (2105, 764, 2165, 794)}
# (usuário: "representar o vão com tracejado") o vão no meio da parede de cima da suíte master (DOC_LINHAS E PROJEÇÕES:
# o retângulo de 1408,7 a 1445,5 x 537,6 a 555,7 px e o X), que a final não mostrava (a rotina dos tracejados não desenha
# sobre parede): o retângulo e o X tracejados (traços de 15 px e vãos de 6 px, centrados em cada lado, como os do PDF),
# finos, no cinza claro dos tracejados sobre fundo escuro (`revisao_1pav_casae_1711.CINZA_ESCURO`)
VAO_MASTER = {"ret": (1408.7, 537.6, 1445.5, 555.7), "traco_px": 15.0, "vao_px": 6.0, "larg_px": 0.8,
              "cor": (200, 200, 200), "ss": 8}


def vao_tracejado(out, q=VAO_MASTER):
    x0, y0, x1, y1 = q["ret"]
    linhas = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0)),
              ((x0, y0), (x1, y1)), ((x0, y1), (x1, y0))]
    ss = q["ss"]
    X0, Y0 = int(x0) - 3, int(y0) - 3
    W, H = int(np.ceil(x1)) + 4 - X0, int(np.ceil(y1)) + 4 - Y0
    m = np.zeros((H * ss, W * ss), np.uint8)
    d, g = q["traco_px"], q["vao_px"]
    for (a, b), (c, e) in linhas:
        L = float(np.hypot(c - a, e - b))
        ux, uy = (c - a) / L, (e - b) / L
        k0 = int(np.ceil((L / 2 + d / 2) / (d + g))) + 1
        for k in range(-k0, k0 + 1):
            t0, t1 = max(L / 2 + k * (d + g) - d / 2, 0.0), min(L / 2 + k * (d + g) + d / 2, L)
            if t1 - t0 < 1.0:
                continue
            p0 = ((a + ux * t0 - X0) * ss, (b + uy * t0 - Y0) * ss)
            p1 = ((a + ux * t1 - X0) * ss, (b + uy * t1 - Y0) * ss)
            cv2.line(m, tuple(int(round(v)) for v in p0), tuple(int(round(v)) for v in p1), 255,
                     max(1, int(round(q["larg_px"] * ss))), cv2.LINE_AA)
    al = cv2.resize(m.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    out = out.copy()
    out[Y0:Y0 + H, X0:X0 + W] = u8(reg * (1 - al) + np.float32(q["cor"]) * al)
    return out


def guarda_corpos(Q, out, q=GUARDA_CORPO):
    """Os guarda-corpos (`GUARDA_CORPOS`) numa folha de vidro contínua, a faixa de antes limpa."""
    import terreo_casaa_1011 as TA
    o = out.astype(np.float32)
    for g in GUARDA_CORPOS:
        out = u8(o)                                         # a fonte: a imagem já limpa pelos de antes
        x0, y0, x1, y1 = g["ret"]
        vert = (y1 - y0) > (x1 - x0)
        d = g["dentro"]
        lo, hi = (x0, x1) if vert else (y0, y1)             # as faces do vidro, no eixo de través
        l0, l1 = g.get("longo", (y0, y1) if vert else (x0, x1))
        a0, a1 = int(np.floor(l0)), int(np.ceil(l1))
        face_in, face_out = (hi, lo) if d > 0 else (lo, hi)
        # para dentro: de logo antes da face de fora até `dentro_px` depois da de dentro, o piso de dentro
        b_in = face_in + d * g["dentro_px"]
        if "ate" in g:                                      # para fora, o piso até a borda da laje / do painel
            b_out = g["ate"]
        else:
            b_out = face_out - d * g["fora_px"]
        c0, c1 = sorted((b_in, b_out))
        c0, c1 = int(np.floor(c0)), int(np.ceil(c1))
        larg = c1 - c0
        desl = d * (larg + g.get("folga", q["folga"]))
        if "fora_px" in g and g["fora_px"] > 0:
            # o lado de fora (o vazio, o jardim): o que há logo além
            f0, f1 = sorted((face_out, face_out - d * g["fora_px"]))
            f0, f1 = int(np.floor(f0)), int(np.ceil(f1))
            fs = -d * (f1 - f0 + q["folga"])
            if vert:
                o[a0:a1, f0:f1] = out[a0:a1, f0 + fs:f1 + fs]
            else:
                o[f0:f1, a0:a1] = out[f0 + fs:f1 + fs, a0:a1]
            c0, c1 = (max(c0, f1), c1) if d > 0 else (c0, min(c1, f0))
            larg = c1 - c0
            desl = d * (larg + g.get("folga", q["folga"]))
        f = _fonte_piso(out, vert, a0, a1, c0, c1, desl, q)
        # o tom: a borda de dentro da faixa no do piso logo além dela (sem degrau), coluna a coluna ao longo
        k = q["tom_px"]
        if d > 0:
            alem, borda = out[_faixa(vert, a0, a1, c1, c1 + k)], (f[:, -k:] if vert else f[-k:, :])
        else:
            alem, borda = out[_faixa(vert, a0, a1, c0 - k, c0)], (f[:, :k] if vert else f[:k, :])
        eixo = 1 if vert else 0
        ref = np.median(alem.astype(np.float32), axis=eixo)
        src = np.median(borda, axis=eixo)
        sg = q["tom_sigma"]
        ganho = cv2.GaussianBlur(ref[None], (0, 0), sg)[0] / np.maximum(cv2.GaussianBlur(src[None], (0, 0), sg)[0], 1)
        ganho = np.clip(ganho, *q["tom_lim"])
        f = f * (ganho[:, None, :] if vert else ganho[None, :, :])
        o[_faixa(vert, a0, a1, c0, c1)] = f
    rets_pt = []
    for g in GUARDA_CORPOS:
        x0, y0, x1, y1 = g["ret"]
        (a, b), (c, e) = Q.q2p(x0, y0), Q.q2p(x1, y1)
        rets_pt.append((min(a, c), min(b, e), max(a, c), max(b, e)))
    o = TA.vidro_laminas(Q, u8(o), rets_pt, TA.ESCADAS_TA["jardim"]["vidro"])
    return u8(o)


def painel_folhas(out, pv, q=PAINEL_FOLHAS):
    """O painel de ripado `pv` folha por folha (cada uma com o seu contorno), com o vão escuro nos `cortes`."""
    import correcoes_terreo_casab_1611 as CB
    import correcoes_terreo_casad_1711 as CD
    import um_pav_casaa_1111 as U
    x0, y0, x1, y1 = pv["ret"]
    cortes = sorted(c for c in pv.get("cortes", []) if y0 < c < y1)
    lim = [y0] + cortes + [y1]
    rng = np.random.default_rng(pv["semente"])
    v = q["vao_px"] / 2
    for i, (a, b) in enumerate(zip(lim, lim[1:])):
        CD._ripado(out, CB.Mapa(), (x0, a + (v if i else 0), x1, b - (v if i < len(lim) - 2 else 0)), pv["lado"],
                   U.FOLHAS_1P, rng)
    H, W = out.shape[:2]
    al = np.zeros((H, W), np.float32)
    for c in cortes:
        al = np.maximum(al, CB.alfa_ret((x0, c - v, x1, c + v), (H, W)))
    o = out.astype(np.float32)
    out[:] = u8(o * (1 - al[..., None]) + np.float32(q["vao"]) * al[..., None])
    return len(lim) - 1


def paredes_tom(Q, out, q=PAREDES_TOM):
    import regras_terreo_casab_1311 as RT
    FE.paredes_pdf(Q)
    a = np.clip(Q._par, 0, 1).astype(np.float32)
    o = out.astype(np.float32)
    lum = o.mean(axis=2)
    cheio = (a > 0.5) & (lum < q["escuro"])
    borda = RT.dilatar(cheio, 1) & ~cheio & (a > 0.02) & (lum < q["escuro"] + 60)
    fora = ~RT.dilatar(a > 0.02, 1)
    num = cv2.GaussianBlur(o * fora[..., None], (0, 0), 2.0)
    den = cv2.GaussianBlur(fora.astype(np.float32), (0, 0), 2.0)
    cinza = np.float32(q["cinza"])
    viz = np.where((den > 0.05)[..., None], num / np.maximum(den, 1e-4)[..., None], cinza)
    o[cheio] = cinza
    ab = a[borda][:, None]
    o[borda] = cinza * ab + viz[borda] * (1 - ab)
    print(f"    paredes: {int(cheio.sum())} px escuros no cinza 80 ({int(borda.sum())} na borda)")
    return u8(o)


def retoques(Q, img):
    import portas_casae_1711 as PC
    import correcoes_terreo_casab_1611 as CB
    par = paredes(Q, 0.5)
    out = img.copy()
    n_obj = [escrivaninha(out, r, ESCRIVANINHA["semente"] + i) for i, (_, r) in enumerate(ESCRIVANINHAS)]
    out = computadores(out, par)
    b = np.zeros(par.shape, bool)
    for x0, y0, x1, y1 in RACKS_LIMPA:
        b[y0:y1, x0:x1] = True
    out = vinilico_novo(Q, out, b & ~par)
    for nome, r, tv, fr in RACKS:
        out = rack(out, r, tv, fr, par)
    # (usuário: "melhore a representação dessa porta da suite 2") o 4º argumento de `PC.folha` é o da porta deitada no
    # PDF, cuja folha fica em pé: a folha da suíte 2 é deitada na imagem (o veio no comprido dela, sem os salpicos de
    # quando o veio a atravessava); as do closet master, em pé
    PC.folha(out, CB.Mapa(), PORTA_SUITE2["folha"], False, PORTA_SUITE2["semente"])
    pc = PORTAS_CLOSET
    x0, y0, x1, y1 = pc["entre"]
    b = np.zeros(par.shape, bool)
    b[y0:y1, x0:x1] = True
    out = vinilico_novo(Q, out, b & ~par)
    for i, f in enumerate(pc["folhas"]):
        PC.folha(out, CB.Mapa(), f, True, pc["semente"] + i)
    out = paredes_tom(Q, out)
    out = pisos_closets(Q, out)
    out = guarda_corpos(Q, out)
    nf = [painel_folhas(out, pv) for pv in PAINEIS]
    c = CLOSET_MASTER
    x0, y0, x1, y1 = c["faixa"]
    b = np.zeros(par.shape, bool)
    b[y0:y1, x0:x1] = True
    mx0, my0, mx1, my1 = c["miolo"]
    b[my0:my1, mx0:mx1] = False                   # o miolo do piso fica (dá a luz)
    out = vinilico_novo(Q, out, b & ~par)
    o = out.astype(np.float32)
    for y, f in c["sombras"].items():
        o[y, x0:x1] *= f
    out = u8(o)
    out = linha_claraboia(Q, out, ROUPARIA["piso"], nomes=("rouparia",), vaos=False,
                          sob_rotulo=[CLARABOIA_ROUPARIA["sob_rotulo"]])
    out = vao_tracejado(out)
    print(f"    retoques: {len(ESCRIVANINHAS)} escrivaninhas lisas, sem o fio escuro nem os resíduos ({sum(n_obj)} px de objetos "
          "de antes fora), com o monitor e o teclado Apple; "
          f"{len(RACKS)} racks (suítes e sala íntima) no aparador de freijó com a TV do PDF; a porta da suíte 2 e as 2 folhas de "
          f"correr do closet master em madeira; o piso do closet "
          f"master sem os traços; {len(GUARDA_CORPOS)} guarda-corpos numa folha de vidro contínua; os painéis de ripado em "
          f"{' e '.join(map(str, nf))} folhas; a claraboia da rouparia (o retângulo tracejado) e o vão da parede de cima "
          "da suíte master tracejado")
    return out


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("base", base), ("nublado", nublado), ("escada", escada), ("tracejados", tracejados), ("rouparia", rouparia),
          ("elevador", elevador), ("chuveiros", chuveiros), ("banhos", banhos), ("esquadrias", esquadrias),
          ("mobiliario", mobiliario), ("folhagens", folhagens), ("retoques", retoques), ("rotulos", rotulos)]


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
    ap.add_argument("--sem_textos", action="store_true", help="sem os rótulos e a descrição (entrada da opção B do 12K)")
    ap.add_argument("--sem_folhas", action="store_true", help="sem as plantas, só os vasos (entrada do Topaz do 12K)")
    a = ap.parse_args()
    global SEM_TEXTOS, SEM_FOLHAS
    SEM_TEXTOS, SEM_FOLHAS = a.sem_textos, a.sem_folhas
    if (a.sem_textos or a.sem_folhas) and not a.saida:
        ap.error("--sem_textos/--sem_folhas pedem --saida (a final fica como está)")
    out = rodar(antes_img(), a.de, a.ate, a.cache)
    cv2.imwrite(a.saida or str(FINAL), out)
    print(f"-> {a.saida or FINAL}")


if __name__ == "__main__":
    main()

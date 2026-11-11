#!/usr/bin/env python3
"""Casa A, 1º Pavimento: os pedidos do cliente de 11/11/26 (com os recortes em `pedidos_cliente/1Pavimento_1111/`,
transcritos no LEIA.md) e as regras do Térreo que valem para ele, sobre a final aprovada do 1º Pavimento (ab9a071).

Usuário: "já vou deixar as alterações, além das que definimos como regra do 1º pavimento. só inicie depois que eu aprovar
o terreo." Depois: "Térreo aprovado, inicie o 1°".

Os passos (cada um sobre o anterior; `--de`/`--ate` recomeçam ou param num passo, com os passos gravados em `--passos`):
  1. nublado: o Térreo nublado refeito a partir da final aprovada do Térreo (a imagem limpa da entrada da IA do 12K, sem
     rótulos, triângulos, descrições e tracejados), fora da pegada do 1º Pavimento, nos dois vazios e no poço da escada
     em U (com os degraus 1 a 7 do Térreo); o tracejado do lote e o tracejado branco somem com o nublado antigo;
  2. tracejados: saem os tracejados de dentro da pegada que não são de vazio (os contornos da cobertura, o do quarto e
     do banho master, o afastamento de baixo) e as molduras e os X antigos dos vazios;
  3. pergolado: na cor dele (madeira), apagado, sob o 1º Pavimento;
  4. contorno: o contorno da casa em maior destaque;
  5. vazios: os X e as molduras finos e claros (os dois vazios, o vazio junto ao elevador e o shaft de cima); o guarda-
     corpo de vidro do vazio junto à circulação; o shaft de cima fechado em parede (sem a janela);
  ... (os outros pedidos, nos passos seguintes)
"""
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                    # noqa: E402
import final3840_casaa_terreo as T              # noqa: E402
import final3840_casaa_1pav as P1               # noqa: E402
import terreo_casaa_1011 as TA                  # noqa: E402

FINAL = FA.CASA / "renders" / "POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png"
dilatar, compor = TA.dilatar, TA.compor


def quadro():
    with contextlib.redirect_stdout(io.StringIO()):
        Q = FA.QuadroA("1Pavimento")
        P1.inicial(Q)
    return Q


def ret_px(Q, r):
    return TA.ret_q(Q, r)


def ret_alfa(Q, r_px, ss=4, borda=0.0):
    """O retângulo (px do quadro, fracionário) como alfa de 0 a 1 (antisserrilhado)."""
    x0, y0, x1, y1 = r_px
    a = np.zeros((Q.H, Q.W), np.float32)
    X0, Y0, X1, Y1 = int(np.floor(x0)) - 2, int(np.floor(y0)) - 2, int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 2
    m = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    cv2.rectangle(m, (int(round((x0 - X0) * ss)), int(round((y0 - Y0) * ss))),
                  (int(round((x1 - X0) * ss)) - 1, int(round((y1 - Y0) * ss)) - 1), 255, -1)
    a[Y0:Y1, X0:X1] = cv2.resize(m.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    if borda > 0:
        a = cv2.GaussianBlur(a, (0, 0), borda)
    return a


# ----------------------------------------------------------------------------------------------------------------------
# 1. O Térreo nublado (regra do 1º Pavimento, seção 11; cliente, 11/11: "Remover as linhas tracejadas do telhado e a
# linha tracejada branca ... Deixar apenas as que representam 'vazios', claraboias e pergolados"): o Térreo é a imagem
# limpa da final aprovada (`ampliacao_12k_terreo_casaa.preparar`: sem rótulos, sem triângulos e descrições das
# escadas, sem os tracejados finos), nublada como em `rotulos_casaa.nublar` (70% de branco, 80% da saturação, desfoque
# leve). Entra fora da pegada do pavimento (o lote e o tracejado branco antigos somem), nos dois vazios (do PDF, de
# moldura a moldura; a viga entre eles fica) e no poço da escada em U (fora dos degraus do 1º Pavimento; os degraus 1 a
# 7, até a linha de corte, são do Térreo). A linha de corte e o contorno do vão entre os lances voltam por cima.
NUBLADO_1P = {"corte": {"cor": (150, 150, 150), "larg_px": 0.85},
              "vazios_pt": [(1315.4, 805.7, 1655.6, 1060.8), (1666.9, 805.7, 1925.4, 1060.8)],
              "poco_px": (2253.0, 891.0, 2533.0, 1106.0), "borda_px": 0.6,
              "vao": ((132, 138, 147), 0.9)}


def terreo_limpo():
    """A final aprovada do Térreo sem rótulos, triângulos, descrições e tracejados, no quadro (a entrada da IA do 12K
    no lugar dela; fora dela, o branco)."""
    import ampliacao_12k_terreo_casaa as Z
    ent = cv2.imread(str(Z.ENTRADA_IA))
    rc = json.loads(Z.DADOS.read_text())["recortes"]
    t = np.full((2160, 3840, 3), 255, np.uint8)
    h, w = ent.shape[:2]
    t[rc["Yia"]:rc["Yia"] + h, rc["X0"]:rc["X0"] + w] = ent
    return t


def nublar(t):
    from entorno_esmaecido import NUBLADO
    t = cv2.GaussianBlur(t.astype(np.float32), (0, 0), NUBLADO["desfoque"] * t.shape[1] / 3840)
    cinza = t.mean(axis=2, keepdims=True)
    t = cinza + (t - cinza) * NUBLADO["saturacao"]
    return 255 - (255 - t) * (1 - NUBLADO["clarear"])


def degraus_1p(Q):
    """Os degraus do 1º Pavimento na escada em U (os lances e o patamar do PDF, menos o trecho do Térreo)."""
    q = P1.ESCADA_U_1P
    a = np.maximum.reduce([ret_alfa(Q, ret_px(Q, q[k])) for k in ("lanco1", "patamar", "lanco2")])
    return a * (1 - (Q.troca.astype(np.float32) / 255))


def pegada_1p(Q, k=None):
    """A pegada do 1º Pavimento sem os dentes da pegada antiga (as pontas das vigas do pergolado coladas à casa, com o
    trecho tracejado delas sob a laje): abertura de `CONTORNO_1P["abrir_px"]` (25 px: tira os 8 dentes, de 14 a 18 px de
    largura, e as 2 lascas de 1 a 2 px na borda da varanda de 14,6 m², e nada da casa). Vale para o nublado, o pergolado
    e o contorno."""
    k = k or CONTORNO_1P["abrir_px"]
    pg = (Q.pegada > 127).astype(np.uint8)
    return cv2.morphologyEx(pg, cv2.MORPH_OPEN, np.ones((k, k), np.uint8)) > 0


def mascara_terreo(Q, q=None):
    """Onde o Térreo nublado aparece: fora da pegada, nos vazios e no poço da escada (0 a 1)."""
    q = q or NUBLADO_1P
    pg = pegada_1p(Q)
    a = np.maximum(cv2.GaussianBlur(pg.astype(np.float32), (0, 0), 1.0), pg)
    m = 1 - a
    for r in q["vazios_pt"]:
        m = np.maximum(m, ret_alfa(Q, ret_px(Q, r), borda=q["borda_px"]))
    poco = ret_alfa(Q, q["poco_px"], borda=q["borda_px"]) * (1 - degraus_1p(Q))
    return np.clip(np.maximum(m, poco), 0, 1)


def nublado_1p(Q, img, q=None):
    q = q or NUBLADO_1P
    t = nublar(terreo_limpo())
    m = mascara_terreo(Q, q)[..., None]
    out = img.astype(np.float32) * (1 - m) + t * m
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    # a linha de corte do Térreo na escada em U, suavizada (usuário, vendo a final: "pode remover a linha preta, mas
    # preserve a divisão. ou suavize a linha preta": a divisão fica, num cinza médio mais fino, em vez do grafite), e o
    # contorno fino do vão entre os lances, por cima
    guarda = P1.CORTE_U
    P1.CORTE_U = dict(guarda, **q["corte"])
    try:
        out = P1.linha_corte(Q, out)
    finally:
        P1.CORTE_U = guarda
    e = P1.ESCADA_U_1P
    l1, pa, l2 = e["lanco1"], e["patamar"], e["lanco2"]
    cor, larg = q["vao"]
    tl = FA.tela(np.ascontiguousarray(out), Q, (l2[0], l1[1], pa[2], l2[3]), folga=4)
    c = tl.reduzir(tl.linha([(l1[0], l1[3]), (pa[0], l1[3]), (pa[0], l2[1]), (l2[0], l2[1])], larg))
    tl.reg = tl.reg * (1 - c[..., None]) + np.float32(cor) * c[..., None]
    out = tl.gravar()
    print(f"    nublado: o Térreo aprovado (limpo) nublado em {100 * float((m[..., 0] > 0.5).mean()):.1f}% do quadro "
          f"(fora da pegada, nos 2 vazios e no poço da escada em U); a linha de corte e o vão de volta")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 2. Os tracejados que não são de vazio saem de dentro da pegada (cliente: "Remover as linhas tracejadas do telhado";
# no banho master: "Remover as linhas tracejadas."): os contornos da cobertura (ARQ_CONTRAPISO: a de x = 1281,4 pt no
# quarto e no banho master, a de baixo, as duas da varanda de 39 m², a da esquerda das varandas), o afastamento de
# baixo (DOC_LINHAS) e os traços antigos das molduras dos vazios, pela troca com o piso de perto do mesmo material
# (`terreo_casaa_1011.apagar_retas`). Fora da pegada, o nublado novo já não os tem.
TRACEJADOS_1P = dict(TA.TRACEJADOS_TA, min_n=10, banda_px=3, costura_px=4, costura_dif=10,
                     # o afastamento de baixo continua tracejado dentro da janela da saleta (as linhas da janela
                     # são fixas): as linhas y0..y1 da caixa recebem a interpolação das de fora (px do quadro)
                     restos_px=[(2019, 1636, 2135, 1637)],
                     # o trecho de cima do L tracejado da varanda de 6,36 m² (curto demais para virar cadeia)
                     extras_px=[((1521.0, 335.0), (1592.0, 335.0))],
                     # o rótulo VARANDA 6,36 m² encosta na reta de x = 1521 (o rótulo fica fixo): na faixa entre a
                     # borda e a 1ª letra, os px que fogem do piso de logo à esquerda (x0f..x1f) recebem esse piso
                     rotulo_px=[(1517, 455, 1522, 495, 1514, 1516)])


def retas_1p(Q, q=None):
    import pedidos_terreo_casaa_2910 as P
    q = q or TRACEJADOS_1P
    pg = Q.pegada > 127
    retas = []
    for cam in ("ARQ_CONTRAPISO", "DOC_LINHAS E PROJEÇÕES"):
        for k, ext, segs in T.cadeias_tracejadas(Q, [cam], min_n=2, min_ext=20):
            if len(segs) < q["min_n"] and cam == "ARQ_CONTRAPISO":
                continue
            if k[1] not in (0.0, 90.0):
                continue
            x0, y0, x1, y1 = P._linha_inteira(segs)
            p0, p1 = Q.p2q(x0, y0), Q.p2q(x1, y1)
            n = max(2, int(np.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 4))
            dentro = [pg[int(np.clip(p0[1] + (p1[1] - p0[1]) * t, 0, Q.H - 1)),
                         int(np.clip(p0[0] + (p1[0] - p0[0]) * t, 0, Q.W - 1))] for t in np.linspace(0, 1, n)]
            if any(dentro):
                retas.append((p0, p1, q["banda_px"], False))
    retas += [(p0, p1, q["banda_px"], False) for p0, p1 in q.get("extras_px", [])]
    return retas


def tracejados_1p(Q, img, q=None):
    q = q or TRACEJADOS_1P
    retas = retas_1p(Q, q)
    par = FA.paredes_pdf(Q) > 0.05
    rots = TA.rotulos_na_imagem(Q, img)
    rot = np.zeros(img.shape[:2], np.float32)
    for _, al, _, _ in rots:
        rot = np.maximum(rot, al)
    fixo = dilatar(par, 1) | dilatar(rot > 0.02, 1)
    pular = mascara_terreo(Q) > 0.5
    moveis = TA.moveis_pdf(Q, q)
    out, n = TA.apagar_retas(img, retas, fixo, moveis, TA.materiais(Q), pular, q)
    out, nc = costura(img, out, retas, moveis, par, dilatar(rot > 0.02, 3) | pular, q)
    print(f"    tracejados: {len(retas)} retas da cobertura, do afastamento e das molduras antigas dentro da pegada, "
          f"{n} px trocados pelo piso de perto, {nc} px de costura nos objetos e nas bordas das paredes")
    return out


def costura(img, out, retas, moveis, par, excl, q=None):
    """Sobre os objetos (a cama e a banheira da suíte e do banho master) o `apagar_retas` só troca os px do traço, e
    sobra uma costura clara ou escura na faixa da reta; na borda das paredes (que ficam fixas) sobra o pingo do traço.
    Ali (só nas retas verticais: as horizontais correm junto das janelas e dos peitoris, que não podem borrar) a faixa
    de `costura_px` de cada lado da reta recebe a interpolação linear entre as duas colunas (ou linhas) de
    fora dela, onde ainda foge dela mais que `costura_dif`, e só com as duas pontas fora das paredes (a borda delas
    fica nítida); no piso, a troca com o piso de perto já ficou. Por fim, as caixas de `restos_px`."""
    q = q or TRACEJADOS_1P
    H, W = out.shape[:2]
    o = img.astype(np.float32)
    mo = cv2.medianBlur(img, 11).astype(np.float32)
    obj = moveis | ((mo.max(axis=2) - mo.min(axis=2) < q["croma_obj"]) & (mo.mean(axis=2) > q["lum_obj"]))
    alvo = (dilatar(obj, 2) | (dilatar(par, 3) & ~par)) & ~excl
    res = out.astype(np.float32)
    w = q["costura_px"]
    n = 0
    for p0, p1, _, _ in retas:
        vert = abs(p1[0] - p0[0]) < abs(p1[1] - p0[1])
        if not vert and not q.get("costura_horizontais"):
            continue
        if vert:
            c = int(round((p0[0] + p1[0]) / 2))
            a, b = sorted((int(round(p0[1])), int(round(p1[1]))))
            a, b = max(a - q["ponta_px"], 0), min(b + q["ponta_px"], H - 1)
            if c - w - 1 < 0 or c + w + 1 >= W:
                continue
            fx = res[a:b + 1, c - w - 1].copy(), res[a:b + 1, c + w + 1].copy()
            for i, x in enumerate(range(c - w, c + w + 1)):
                t = (i + 1) / (2 * w + 2)
                interp = fx[0] * (1 - t) + fx[1] * t
                troca = alvo[a:b + 1, x] & ~par[a:b + 1, c - w - 1] & ~par[a:b + 1, c + w + 1] & \
                    (np.abs(res[a:b + 1, x] - interp).max(axis=1) > q["costura_dif"])
                res[a:b + 1, x][troca] = interp[troca]
                n += int(troca.sum())
        else:
            r = int(round((p0[1] + p1[1]) / 2))
            a, b = sorted((int(round(p0[0])), int(round(p1[0]))))
            a, b = max(a - q["ponta_px"], 0), min(b + q["ponta_px"], W - 1)
            if r - w - 1 < 0 or r + w + 1 >= H:
                continue
            fy = res[r - w - 1, a:b + 1].copy(), res[r + w + 1, a:b + 1].copy()
            for i, y in enumerate(range(r - w, r + w + 1)):
                t = (i + 1) / (2 * w + 2)
                interp = fy[0] * (1 - t) + fy[1] * t
                troca = alvo[y, a:b + 1] & ~par[r - w - 1, a:b + 1] & ~par[r + w + 1, a:b + 1] & \
                    (np.abs(res[y, a:b + 1] - interp).max(axis=1) > q["costura_dif"])
                res[y, a:b + 1][troca] = interp[troca]
                n += int(troca.sum())
    for x0, y0, x1, y1, f0, f1 in q.get("rotulo_px", []):
        for y in range(y0, y1 + 1):
            piso = res[y, f0:f1 + 1].mean(axis=0)
            fora = np.abs(res[y, x0:x1 + 1] - piso).max(axis=1) > q["costura_dif"]
            res[y, x0:x1 + 1][fora] = piso
            n += int(fora.sum())
    for x0, y0, x1, y1 in q["restos_px"]:
        cima, baixo = res[y0 - 1, x0:x1 + 1].copy(), res[y1 + 1, x0:x1 + 1].copy()
        for y in range(y0, y1 + 1):
            t = (y - y0 + 1) / (y1 - y0 + 2)
            res[y, x0:x1 + 1] = cima * (1 - t) + baixo * t
            n += x1 - x0 + 1
    return np.clip(np.round(res), 0, 255).astype(np.uint8), n


# ----------------------------------------------------------------------------------------------------------------------
# 2b. O Bege Bahia menos manchado (regra de 10/11, "em todas as plantas de todas as casas"; usuário, vendo a final:
# "Reduzir manchas do bege Bahia, da mesma forma que fizemos. Isso é regra para todas as demais plantas."): nas 4
# varandas, no quarto de serviço, na saleta e no B. serviço (o cinza 232 da base chapada, dentro da pegada e fora do
# nublado e das paredes), as manchas a 45% do contraste, pelo mesmo `terreo_casaa_1011.bege_ta` do Térreo; a luz, as
# sombras, o tom, as peças e os rótulos ficam.
BEGE_1P = dict(TA.BEGE_TA)


def bege_1p(Q, img, q=None):
    q = q or BEGE_1P
    zona = TA.T.F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), 5) & pegada_1p(Q)
    zona &= ~(mascara_terreo(Q) > 0.02) & ~(FA.paredes_pdf(Q) > 0.3)
    return TA.bege_ta(Q, img, q, zona=zona)


# ----------------------------------------------------------------------------------------------------------------------
# 3. O pergolado (cliente: "Como essa planta é do 1º pavimento, nós não vemos o pergolado tracejado, vemos ele na cor
# dele. Só que com o tom mais 'apagado' para mostrar que ele está embaixo do 1º pavimento."; usuário, vendo a final:
# "Pergolado esfumaçado, conforme orientação, por estar abaixo do 1° pavimento"): as vigas do PDF (ARQ_PERGOLADO: cada
# viga é o par de traços a 0,2 m), cheias, na madeira (o tom das réguas do deck do Térreo, com um grão largo e leve),
# esfumaçadas: o véu do nublado (`apagado`: a fração de branco) e as bordas desfocadas (`esfumado_px`, o sigma em px),
# com a sombra difusa no Térreo de baixo; cada viga vai até a borda da casa (a ponta tracejada dela sob a laje fica sob
# o nublado: `pegada_1p`); só onde o Térreo aparece (o 1º Pavimento fica por cima).
PERGOLADO_1P = {"madeira": (78, 112, 152), "grao": 0.04, "grao_px": 3.0, "apagado": 0.62, "saturacao": 0.85,
                "esfumado_px": 2.2, "sombra": 0.04, "sombra_px": (2.0, 2.0, 4.0), "ponta_px": 14, "semente": 1111}


def pergolado_vigas(Q):
    """As vigas do pergolado (px do quadro): [(x0, y0, x1, y1, vertical)], pelos pares de traços da ARQ_PERGOLADO."""
    import pedidos_terreo_casaa_2910 as P
    hs, vs = [], []
    for k, _, segs in T.cadeias_tracejadas(Q, ["ARQ_PERGOLADO"]):
        x0, y0, x1, y1 = P._linha_inteira(segs)
        (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
        (hs if k[1] == 0.0 else vs).append((min(u0, u1), min(v0, v1), max(u0, u1), max(v0, v1)))
    vigas = []
    for lista, vert in ((sorted(vs, key=lambda r: r[0]), True), (sorted(hs, key=lambda r: r[1]), False)):
        usadas = set()
        for i, a in enumerate(lista):
            if i in usadas:
                continue
            for j in range(i + 1, len(lista)):
                b = lista[j]
                d = (b[0] - a[0]) if vert else (b[1] - a[1])
                if j not in usadas and 8 <= d <= 16:
                    usadas |= {i, j}
                    if vert:
                        vigas.append((a[0], min(a[1], b[1]), b[0], max(a[3], b[3]), True))
                    else:
                        vigas.append((min(a[0], b[0]), a[1], max(a[2], b[2]), b[1], False))
                    break
    return vigas


def _ate_a_casa(pg, viga, alcance):
    """A viga esticada até a borda da casa (a pegada aberta), quando a ponta dela para a até `alcance` px dela."""
    x0, y0, x1, y1, vert = viga
    H, W = pg.shape
    if vert:
        c = int(np.clip(round((x0 + x1) / 2), 0, W - 1))
        for d in range(1, alcance + 1):
            if pg[int(np.clip(y1 + d, 0, H - 1)), c]:
                y1 += d + 2
                break
        for d in range(1, alcance + 1):
            if pg[int(np.clip(y0 - d, 0, H - 1)), c]:
                y0 -= d + 2
                break
    else:
        c = int(np.clip(round((y0 + y1) / 2), 0, H - 1))
        for d in range(1, alcance + 1):
            if pg[c, int(np.clip(x1 + d, 0, W - 1))]:
                x1 += d + 2
                break
        for d in range(1, alcance + 1):
            if pg[c, int(np.clip(x0 - d, 0, W - 1))]:
                x0 -= d + 2
                break
    return x0, y0, x1, y1, vert


def pergolado_1p(Q, img, q=None):
    q = q or PERGOLADO_1P
    pg = pegada_1p(Q)
    vigas = [_ate_a_casa(pg, v, q["ponta_px"]) for v in pergolado_vigas(Q)]
    H, W = img.shape[:2]
    a = np.zeros((H, W), np.float32)
    for x0, y0, x1, y1, vert in vigas:
        a = np.maximum(a, ret_alfa(Q, (x0, y0, x1, y1)))
    # o grão largo e leve da madeira (o veio fino some no esfumado)
    rng = np.random.default_rng(q["semente"])
    grao = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), q["grao_px"])
    grao /= max(float(grao.std()), 1e-6)
    madeira = np.float32(q["madeira"]) * (1 + q["grao"] * grao[..., None])
    cinza = madeira.mean(axis=2, keepdims=True)
    madeira = cinza + (madeira - cinza) * q["saturacao"]
    madeira = 255 - (255 - madeira) * (1 - q["apagado"])
    vis = mascara_terreo(Q)
    asf = cv2.GaussianBlur(a, (0, 0), q["esfumado_px"])
    f = img.astype(np.float32)
    # a sombra difusa das vigas no Térreo (para baixo e à esquerda, como as outras)
    dx, dy, sg = q["sombra_px"]
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -dx], [0, 1, dy]]), (W, H)), (0, 0), sg)
    f *= (1 - q["sombra"] * sb * (1 - asf) * vis)[..., None]
    al = (asf * vis)[..., None]
    out = f * (1 - al) + madeira * al
    print(f"    pergolado: {len(vigas)} vigas do PDF na madeira, esfumaçadas ({int(q['apagado'] * 100)}% de branco, bordas "
          f"desfocadas a {q['esfumado_px']} px), até a borda da casa, sob o 1º Pavimento")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 4. O contorno da casa em maior destaque (cliente: "Deixa o contorno da casa em maior destaque.", com as setas na borda
# da varanda e no pergolado): a borda de fora da pegada do 1º Pavimento (sem os vazios) em linha cinza-escura firme e,
# do lado de fora, sobre o Térreo nublado, a sombra suave do pavimento (para baixo e à esquerda), que o descola do
# Térreo.
CONTORNO_1P = {"cor": (58, 58, 58), "larg_px": 2.2, "simplifica_px": 1.2, "abrir_px": 25, "sombra": 0.22, "sombra_px": (5.0, 5.0, 5.0)}


def contorno_1p(Q, img, q=None):
    q = q or CONTORNO_1P
    H, W = img.shape[:2]
    # sem os dentes do pegada antiga (as pontas das vigas do pergolado coladas à casa): abertura de `abrir_px`
    pg = pegada_1p(Q, q["abrir_px"]).astype(np.uint8)
    cs, _ = cv2.findContours(pg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cs = [cv2.approxPolyDP(c, q["simplifica_px"], True) for c in cs if cv2.contourArea(c) > 5000]
    ss = 4
    m = np.zeros((H * ss, W * ss), np.uint8)
    for c in cs:
        cv2.polylines(m, [np.int32(np.round((c.astype(np.float32) + 0.5) * ss))], True, 255,
                      max(1, int(round(q["larg_px"] * ss))), cv2.LINE_AA)
    linha = cv2.resize(m.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    dx, dy, sg = q["sombra_px"]
    pf = pg.astype(np.float32)
    sb = cv2.GaussianBlur(cv2.warpAffine(pf, np.float32([[1, 0, -dx], [0, 1, dy]]), (W, H)), (0, 0), sg)
    f = img.astype(np.float32)
    f *= (1 - q["sombra"] * sb * (1 - pf))[..., None]
    out = compor(f, linha, q["cor"])
    print(f"    contorno: a borda de fora do 1º Pavimento ({len(cs)} contorno, {sum(len(c) for c in cs)} vértices) em "
          f"linha de {q['larg_px']} px e a sombra do pavimento sobre o Térreo nublado")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 5. Os vazios (cliente: "Deixar as linhas tracejadas mais finas e mais claras", nos X dos vazios; "Colocar o tracejado
# em 'X' que indica vazio", no vão entre o elevador e o banho 1; "Representar como parede normal sem janela", no shaft
# de cima, junto à circulação): os traços da DOC_LINHAS E PROJEÇÕES dos dois vazios (X e molduras) e o X do vazio junto
# ao elevador (que o desenho de 26/10 deixava de fora), finos e claros como no Térreo (`terreo_casaa_1011.FINOS_TA`),
# fora das paredes; o vazio junto ao elevador e o shaft de cima limpos (o branco de dentro, sem os restos e o X antigo)
# e com o X fino (o shaft, de canto a canto); a janela do shaft vira parede, emendada nas duas laterais. O vazio da
# direita recebe o guarda-corpo de vidro do PDF (ARQ_ELEMENTOS FIXOS) junto à circulação e à sala íntima, no desenho dos
# vidros (regra [22/10]).
VAZIOS_1P = {"caixas_px": [(1505, 600, 2160, 888), (2348, 1110, 2392, 1214)],
             "limpar_px": [(2356, 1118, 2384, 1207), (2258, 356, 2341, 402)],
             "shaft_x_px": (2258, 356, 2341, 402), "branco": (247, 247, 246),
             "janela_px": (2252, 402, 2353, 417), "parede_amostra_px": (2246, 360, 2254, 400),
             "guarda_corpo_pt": [(1811.5, 802.3, 1925.4, 803.5), (1924.3, 802.3, 1925.4, 1064.2),
                                 (1811.5, 1063.1, 1925.4, 1064.2)]}


def vazios_1p(Q, img, q=None):
    q = q or VAZIOS_1P
    out = img.copy()
    # a janela do shaft vira parede (a cor das paredes de perto)
    x0, y0, x1, y1 = q["parede_amostra_px"]
    cor_par = np.median(img[y0:y1, x0:x1].reshape(-1, 3), axis=0)
    x0, y0, x1, y1 = q["janela_px"]
    out[y0:y1, x0:x1] = cor_par.astype(np.uint8)
    # o branco limpo dentro do vazio do elevador e do shaft
    for x0, y0, x1, y1 in q["limpar_px"]:
        out[y0:y1, x0:x1] = np.uint8(q["branco"])
    # os traços: os do PDF nas caixas e o X do shaft (de canto a canto da caixa limpa)
    segs = []
    for _, _, ss in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"], min_n=2, min_ext=20):
        for s in ss:
            u, v = Q.p2q((s[0] + s[2]) / 2, (s[1] + s[3]) / 2)
            if any(a <= u <= c and b <= v <= d for a, b, c, d in q["caixas_px"]):
                segs.append(s)
    x0, y0, x1, y1 = q["shaft_x_px"]
    (a0, b0), (a1, b1) = Q.q2p(x0, y0), Q.q2p(x1, y1)
    tr, va = 5.0, 3.5                                      # pt: o traço e o vão dos tracejados do PDF
    for p, r in (((a0, b0), (a1, b1)), ((a0, b1), (a1, b0))):
        L = np.hypot(r[0] - p[0], r[1] - p[1])
        d = ((r[0] - p[0]) / L, (r[1] - p[1]) / L)
        t = 0.0
        while t < L:
            t1 = min(t + tr, L)
            segs.append((p[0] + d[0] * t, p[1] + d[1] * t, p[0] + d[0] * t1, p[1] + d[1] * t1))
            t = t1 + va
    fq = TA.FINOS_TA
    pq = dict(T.PROJ, larg_px=fq["larg_px"], preto=fq["escuro"], branco=fq["claro"], limiar=fq["limiar"])
    novo, _ = T.preto_branco(Q, out, segs, pq)
    par = FA.paredes_pdf(Q)[..., None]
    novo = np.clip(np.round(novo * (1 - par) + out * par), 0, 255).astype(np.uint8)
    # o guarda-corpo de vidro do vazio junto à circulação
    novo = TA.vidro_laminas(Q, novo, q["guarda_corpo_pt"], TA.ESCADAS_TA["jardim"]["vidro"])
    print(f"    vazios: {len(segs)} traços finos e claros (os X e as molduras dos 2 vazios, o X do vazio junto ao "
          f"elevador e o do shaft); a janela do shaft em parede; o guarda-corpo de vidro do vazio junto à circulação")
    return np.clip(np.round(novo), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 6. As folhas amadeiradas das portas das suítes para as varandas (cliente: "Representar melhor o painel amadeirado que tem
# aqui entre a varanda e o quarto"; "Representar melhor o painel amadeirado, ele acaba sumindo no piso amadeirado";
# usuário, vendo a final: "aqui são duas folhas amadeiradas" (suíte 2), "aqui são quatro folhas amadeiradas. corrija os
# resíduos limpando a imagem" (suíte master), "corrija o amadeirado aqui também" (suíte 1)): o plano de fora das portas
# das suítes, folha por folha como no PDF (`revisao_casaa_2910.BRISES_SUITES_TA` e as folhas da frente dos banhos,
# `pedidos_terreo_casaa_2910.BANHOS_1PAV_TA`), cada uma no seu trilho (os trilhos se alternam) e com o seu contorno, em
# ripado de nogueira (as ripas marcadas, o veio no comprido, a aresta da luz), com as junções do PDF na mesma madeira,
# mais escura, e a sombra curta na varanda. Antes, a faixa do plano de fora é limpa (a faixa contínua de antes, o
# bronze antigo e os restos): do lado da varanda e na frente dos banhos, o Bege Bahia da varanda ao lado; entre os
# trilhos, no vão do quarto, o piso do quarto de logo ao lado. Suítes 3 (2 folhas), 2 (2 + 1 do banho), master (2 + 2 da
# frente do banho master) e 1 (2 + 2 do banho 1).
FOLHAS_1P = {"madeira": (52, 82, 122), "junta": (30, 46, 70), "juncao": 0.80, "ripa_px": 3.6, "junta_px": 0.9,
             "junta_forca": 0.75, "luz": 0.16, "veio": 0.08, "contorno": (34, 40, 48), "contorno_px": 0.6,
             "folga_px": 0.7, "sombra": 0.26, "sombra_px": (-0.9, 1.1, 0.9), "margem_fora_px": 4, "fonte_px": 3,
             "semente": 1116, "suites": ("Suíte 3", "Suíte 2", "Suíte Master", "Suíte 1")}


def _rotulos_mascara(Q, img, folga=2):
    """Os px dos rótulos do PDF achados na imagem (com `folga` px em volta)."""
    rot = np.zeros(img.shape[:2], np.float32)
    for _, al, _, _ in TA.rotulos_na_imagem(Q, img):
        rot = np.maximum(rot, al)
    return dilatar(rot > 0.02, folga)


def _anel(out, U, larg, passo, proibido, janela=None):
    """O anel de `larg` px em volta de U (bool) limpo: cada px recebe o de `passo` px mais para fora, na normal da borda
    de U (o gradiente da distância), ou mais longe se ali for `proibido` ou U. Devolve o número de px trocados."""
    H, W = U.shape
    if janela is None:
        ys, xs = np.nonzero(U)
        janela = (max(xs.min() - larg - passo - 12, 0), max(ys.min() - larg - passo - 12, 0),
                  min(xs.max() + larg + passo + 13, W), min(ys.max() + larg + passo + 13, H))
    X0, Y0, X1, Y1 = janela
    u = U[Y0:Y1, X0:X1]
    dist = cv2.distanceTransform((~u).astype(np.uint8), cv2.DIST_L2, 5)
    gx = cv2.Sobel(dist, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(dist, cv2.CV_32F, 0, 1, ksize=3)
    nrm = np.maximum(np.hypot(gx, gy), 1e-6)
    gx, gy = gx / nrm, gy / nrm
    anel = (dist > 0) & (dist <= larg) & ~proibido[Y0:Y1, X0:X1]
    fonte = out.copy()
    n = 0
    for y, x in zip(*np.nonzero(anel)):
        for k in (passo, passo + 3, passo + 6, passo + 10):
            sx, sy = int(round(x + gx[y, x] * (k + larg - dist[y, x]))), int(round(y + gy[y, x] * (k + larg - dist[y, x])))
            if 0 <= sx < X1 - X0 and 0 <= sy < Y1 - Y0 and not u[sy, sx] and not proibido[Y0 + sy, X0 + sx]:
                out[Y0 + y, X0 + x] = fonte[Y0 + sy, X0 + sx]
                n += 1
                break
    return n


def _cobertura(r, X0, Y0, w, h):
    """O retângulo r (px do quadro, fracionário) como cobertura exata de cada px da janela (0 a 1)."""
    xs = np.arange(X0, X0 + w, dtype=np.float32)
    ys = np.arange(Y0, Y0 + h, dtype=np.float32)
    cx = np.clip(np.minimum(xs + 1, r[2]) - np.maximum(xs, r[0]), 0, 1)
    cy = np.clip(np.minimum(ys + 1, r[3]) - np.maximum(ys, r[1]), 0, 1)
    return cy[:, None] * cx[None, :]


def _pecas_fora(Q, nome):
    """As folhas e as junções do plano de fora de uma suíte (px do quadro), o lado da varanda e as linhas do quarto."""
    import pedidos_terreo_casaa_2910 as P
    import revisao_casaa_2910 as RA

    def px(r):
        (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        return min(a, c), min(b, d), max(a, c), max(b, d)
    folhas = [px(r) for r in RA.BRISES_SUITES_TA["folhas_pt"][nome]]
    juncoes = [px(r) for r in RA.JUNCOES_TA[nome]["fora"]]
    if nome in P.BANHOS_1PAV_TA:
        folhas += [px(r) for r in P.BANHOS_1PAV_TA[nome]["folhas"]]
        juncoes += [px(r) for r in P.BANHOS_1PAV_TA[nome]["juncoes"]]
    lado = RA.VAOS_SUITES_TA["portas"][nome][1]                 # +1: a varanda à esquerda; -1: à direita
    quarto = tuple(Q.p2q(0, y)[1] for y in RA.JUNCOES_TA[nome]["batentes"])
    return folhas, juncoes, lado, quarto


def _limpar_faixa(out, par, folhas, pecas, lado, quarto, q, rot=None):
    """A faixa do plano de fora limpa: o Bege Bahia da varanda ao lado (fora do trilho e em frente aos banhos) e, entre
    os trilhos, no vão do quarto, o piso do quarto das `fonte_px` colunas de logo ao lado, repetidas."""
    m = q["margem_fora_px"]
    if lado > 0:
        t = int(np.floor(min(r[0] for r in folhas)))
        L, R = t - m, int(np.ceil(max(r[2] for r in folhas))) + 1
    else:
        t = int(np.ceil(max(r[2] for r in folhas))) - 1
        L, R = int(np.floor(min(r[0] for r in folhas))) - 1, t + m
    Y0 = int(np.floor(min(r[1] for r in pecas))) - 3
    Y1 = int(np.ceil(max(r[3] for r in pecas))) + 3
    d = R - L + 3
    n = 0
    for y in range(Y0, Y1):
        no_quarto = quarto[0] <= y + 0.5 <= quarto[1]
        for x in range(L, R + 1):
            if par[y, x]:
                continue
            fora_trilho = (x < t) if lado > 0 else (x > t)
            if fora_trilho or not no_quarto:
                src = x - d if lado > 0 else x + d                      # o Bege Bahia da varanda
            else:
                # o piso do quarto, das `fonte_px` colunas livres de logo ao lado (depois do trilho de vidro)
                faixa = range(R + 1, R + 16) if lado > 0 else range(L - 1, L - 16, -1)
                livres = [c for c in faixa if not par[y, c] and (rot is None or not rot[y, c])][:q["fonte_px"]]
                if not livres:
                    continue
                src = livres[(x - t) % len(livres)] if lado > 0 else livres[(t - x) % len(livres)]
            # sem copiar os rótulos (o VARANDA encosta na faixa): a mesma coluna, em outra linha
            for dy in (0, -36, 36, -54, 54, -72, 72):
                ys = y + dy
                if 0 <= ys < out.shape[0] and not par[ys, src] and (rot is None or not rot[ys, src]):
                    out[y, x] = out[ys, src]
                    n += 1
                    break
    return n


def folhas_1p(Q, img, q=None):
    q = q or FOLHAS_1P
    par = FA.paredes_pdf(Q) > 0.3
    out = img.copy()
    rng = np.random.default_rng(q["semente"])
    rot = _rotulos_mascara(Q, img)
    contas = []
    for nome in q["suites"]:
        folhas, juncoes, lado, quarto = _pecas_fora(Q, nome)
        pecas = folhas + juncoes
        nl = _limpar_faixa(out, par, folhas, pecas, lado, quarto, q, rot)
        f = q["folga_px"]
        X0 = int(np.floor(min(r[0] for r in pecas))) - 6
        Y0 = int(np.floor(min(r[1] for r in pecas))) - 6
        X1 = int(np.ceil(max(r[2] for r in pecas))) + 6
        Y1 = int(np.ceil(max(r[3] for r in pecas))) + 6
        w, h = X1 - X0, Y1 - Y0
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        cresce = [(r[0] - f, r[1], r[2] + f, r[3]) if (r[3] - r[1]) > (r[2] - r[0]) else
                  (r[0], r[1] - f, r[2], r[3] + f) for r in pecas]
        A = np.zeros((h, w), np.float32)
        for r in cresce:
            A = np.maximum(A, _cobertura(r, X0, Y0, w, h))
        # a sombra curta das peças na varanda (fora delas)
        dx, dy, sg = q["sombra_px"]
        sb = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h)), (0, 0), sg)
        reg *= (1 - q["sombra"] * sb * (1 - A) * (~par[Y0:Y1, X0:X1]))[..., None]
        ys = (np.arange(h, dtype=np.float32) + Y0 + 0.5)[:, None] * np.ones((1, w), np.float32)
        xs = (np.arange(w, dtype=np.float32) + X0 + 0.5)[None, :] * np.ones((h, 1), np.float32)
        veio = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.6, sigmaY=6.0)
        veio /= max(float(veio.std()), 1e-6)
        nf = len(folhas)
        # as junções primeiro (madeira mais escura), depois as folhas, cada uma com o seu contorno
        for i, r in sorted(enumerate(cresce), key=lambda t: t[0] < nf):
            a = _cobertura(r, X0, Y0, w, h)
            cp = q["contorno_px"]
            dentro = _cobertura((r[0] + cp, r[1] + cp, r[2] - cp, r[3] - cp), X0, Y0, w, h)
            rel = np.clip((xs - r[0]) / max(r[2] - r[0], 1e-3), 0, 1)
            luz = 1 + q["luz"] * (rel - 0.5) * lado
            cor = np.float32(q["madeira"])[None, None] * (luz * (1 + q["veio"] * veio))[..., None]
            if i < nf:
                fase = np.mod(ys - r[1], q["ripa_px"])
                jt = np.clip(1 - np.abs(fase - q["junta_px"] / 2) / (q["junta_px"] / 2 + 0.5), 0, 1) * q["junta_forca"]
                cor = cor * (1 - jt[..., None]) + np.float32(q["junta"]) * jt[..., None]
            else:
                cor *= q["juncao"]
            reg = reg * (1 - a[..., None]) + cor * a[..., None]
            borda = np.clip(a - dentro, 0, 1)[..., None]
            reg = reg * (1 - borda) + np.float32(q["contorno"]) * borda
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        contas.append(f"{nome} ({nf} folhas, {len(juncoes)} junções, {nl} px limpos)")
    print(f"    folhas amadeiradas: o plano de fora das portas das suítes folha por folha, em ripado de nogueira: "
          f"{'; '.join(contas)}")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 6b. Os guarda-corpos de vidro das varandas (usuário, vendo a final: "melhore a representação do guarda corpo aqui"
# (varandas de 7,15 e 6,36 m²); "o guarda corpo vai até o final, encostando na parede" (varanda de 39 m², cujo trecho de
# baixo tinha saído com o tracejado do afastamento)): os guarda-corpos do PDF (ARQ_ELEMENTOS FIXOS, as duas linhas a
# 1,2 px), de ponta a ponta, no desenho de vidro das regras (`terreo_casaa_1011.vidro_laminas`: o vidro claro, as duas
# faces em linha fina, o brilho no meio e a sombra curta). Antes, a borda da varanda é limpa: do vidro até a borda da
# casa (o contorno fica) e `dentro_px` para dentro, o Bege Bahia da varanda de logo ao lado (a faixa rosada e os restos).
# `fora`: o lado de fora de cada trecho (-1: esquerda/cima; +1: direita/baixo).
GUARDA_CORPOS_1P = {"trechos_px": [
    # varanda de 6,36 m²: em cima, à esquerda e embaixo (junto ao vazio)
    ((1517.9, 334.8, 1590.1, 336.0), -1), ((1517.9, 334.8, 1519.1, 604.7), -1), ((1517.9, 603.5, 1590.1, 604.7), +1),
    # varanda de 7,15 m²: em cima (junto ao vazio) e à esquerda
    ((1517.9, 884.1, 1590.1, 885.3), -1), ((1517.9, 884.1, 1519.1, 1207.2), -1),
    # varanda de 14,6 m²: em cima, à esquerda e embaixo
    ((1222.3, 1209.5, 1339.3, 1210.7), -1), ((1222.3, 1209.5, 1223.5, 1640.6), -1), ((1222.3, 1639.4, 1339.3, 1640.6), +1),
    # varanda de 39 m²: embaixo (da parede do B. serviço até o canto), à direita e em cima
    ((2163.3, 1639.4, 2770.0, 1640.6), +1), ((2768.8, 1108.0, 2770.0, 1640.6), +1), ((2557.4, 1108.0, 2770.0, 1109.2), -1)],
    "dentro_px": 3, "busca_px": 9}


def guarda_corpos_1p(Q, img, q=None):
    q = q or GUARDA_CORPOS_1P
    out = img.copy()
    par = FA.paredes_pdf(Q) > 0.3
    pg = pegada_1p(Q)
    rot = _rotulos_mascara(Q, img)
    n = 0
    for (x0, y0, x1, y1), fora in q["trechos_px"]:
        vert = (y1 - y0) > (x1 - x0)
        if vert:
            a0, a1 = int(np.floor(y0)), int(np.ceil(y1))
            c0, c1 = x0, x1
        else:
            a0, a1 = int(np.floor(x0)), int(np.ceil(x1))
            c0, c1 = y0, y1
        for a in range(a0, a1):
            # a borda da casa: de fora do vidro até onde a pegada acaba (o contorno fica)
            face = int(np.floor(c0)) if fora < 0 else int(np.ceil(c1))
            borda = face
            for k in range(1, q["busca_px"] + 1):
                b = face + fora * k
                yy, xx = (a, b) if vert else (b, a)
                if not pg[yy, xx]:
                    break
                borda = b
            ini = int(np.ceil(c1)) + q["dentro_px"] if fora < 0 else int(np.floor(c0)) - q["dentro_px"]
            fim = borda - fora * 2                                  # 2 px antes: o contorno fica inteiro
            passo = abs(ini - fim) + 4
            for b in range(min(ini, fim), max(ini, fim) + 1):
                yy, xx = (a, b) if vert else (b, a)
                if par[yy, xx] or rot[yy, xx]:
                    continue
                # o Bege de logo para dentro; junto a um rótulo, o da mesma faixa umas linhas antes ou depois
                for da, db in ((0, 0), (-30, 0), (30, 0), (-45, 0), (45, 0), (0, 20), (0, 40)):
                    sb = b - fora * (passo + db)
                    sy, sx = (a + da, sb) if vert else (sb, a + da)
                    if 0 <= sy < out.shape[0] and 0 <= sx < out.shape[1] and not par[sy, sx] and not rot[sy, sx] \
                            and pg[sy, sx]:
                        out[yy, xx] = img[sy, sx]
                        n += 1
                        break
    rets_pt = []
    for (x0, y0, x1, y1), _ in q["trechos_px"]:
        (a, b), (c, d) = Q.q2p(x0, y0), Q.q2p(x1, y1)
        rets_pt.append((min(a, c), min(b, d), max(a, c), max(b, d)))
    out = TA.vidro_laminas(Q, out, rets_pt, TA.ESCADAS_TA["jardim"]["vidro"])
    print(f"    guarda-corpos: {len(rets_pt)} trechos de vidro nas varandas de 6,36, 7,15, 14,6 e 39 m² (o de baixo da de "
          f"39 m² até a parede), com a borda limpa ({n} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 7. A bancada junto ao quarto de serviço (cliente: "Cor da bancada é no Dekton Danae"): a bancada do PDF (ARQ_BANCADAS)
# no Dekton Danae do Térreo (`terreo_casaa_1011.danae`), em volta da cuba redonda (que fica), com o contorno fino.
BANCADA_1P = {"bancada_pt": (1695.2, 1449.2, 1768.9, 1483.2), "cuba_pt": (1713.35, 1466.2, 9.9), "semente": 1117,
              "contorno": (140, 146, 150),
              # usuário, vendo a final: "Melhore a representação da Cuba, torneira e ralo da Cuba": a cuba redonda
              # de louça (a aba, a bacia em degradê da borda ao fundo com a sombra por dentro do lado da luz, a sombra
              # curta na bancada), o ralo cromado no fundo e a torneira de mesa cromada atrás (do lado da parede de
              # baixo): a base redonda, a bica até o terço de trás da bacia e a alavanca para a direita (pt).
              "aba_pt": 1.4, "sombra_bacia": 0.16, "ralo_pt": 1.45,
              "torneira": {"recuo_pt": 3.4, "base_pt": 1.9, "bica_larg_pt": 1.8, "bica_ate": 0.28,
                           "alavanca_pt": (1.2, 4.8, 1.3)}}


def _cuba_redonda(Q, out, cx, cy, r, q):
    """A cuba redonda de louça: a aba branca, a bacia da borda ao fundo (BACIA_BORDA -> BACIA_FUNDO), mais escura junto
    à borda do alto à direita (a luz vem de lá e a borda faz sombra por dentro), a sombra curta na bancada e o ralo
    cromado no fundo (o anel, o miolo escuro com a grelha e o brilho)."""
    from retoque_terreo_casab import BACIA_BORDA, BACIA_FUNDO, LOUCA, LOUCA_CONTORNO
    tl = FA.tela(out, Q, (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), folga=4)
    k = FA.PT_PX * 8
    u, v = tl.pt(cx, cy)
    c = (int(round(u)), int(round(v)))
    disco = tl.vazia()
    cv2.circle(disco, c, int(round(r * k)), 255, -1, cv2.LINE_AA)
    FA.sombra_q(tl, disco, forca=0.24, dist=0.9, sigma=1.0)
    tl.pintar(disco, LOUCA)
    rb = r - q["aba_pt"]
    bacia = tl.vazia()
    cv2.circle(bacia, c, int(round(rb * k)), 255, -1, cv2.LINE_AA)
    X, Y = tl.grade()
    t = np.clip(np.hypot(X - cx, Y - cy) / rb, 0, 1)
    lado = np.clip(0.5 + 0.5 * ((X - cx) - (Y - cy)) / (rb * 1.414), 0, 1)          # 1 no alto à direita
    f = np.float32(BACIA_FUNDO)[None, None] * (1 - t[..., None] ** 1.6) + np.float32(BACIA_BORDA)[None, None] * t[..., None] ** 1.6
    f *= (1 - q["sombra_bacia"] * np.clip((t - 0.45) / 0.55, 0, 1) * (0.25 + 0.75 * lado))[..., None]
    tl.pintar_img(bacia, f)
    tl.contorno(disco, 0.4, LOUCA_CONTORNO)
    tl.contorno(bacia, 0.3, (190, 193, 195))
    # o ralo: o anel cromado, o miolo escuro com a grelha em cruz e o brilho do alto à direita
    rr = q["ralo_pt"] * k
    anel = tl.vazia()
    cv2.circle(anel, c, int(round(rr)), 255, -1, cv2.LINE_AA)
    FA.sombra_q(tl, anel, forca=0.15, dist=0.4, sigma=0.4)
    tl.pintar(anel, FA.CROMO["meio"])
    miolo = tl.vazia()
    cv2.circle(miolo, c, int(round(rr * 0.62)), 255, -1, cv2.LINE_AA)
    tl.pintar(miolo, (84, 88, 92))
    grelha = tl.vazia()
    e = int(round(rr * 0.62))
    cv2.line(grelha, (c[0] - e, c[1]), (c[0] + e, c[1]), 255, max(1, int(round(0.22 * k))), cv2.LINE_AA)
    cv2.line(grelha, (c[0], c[1] - e), (c[0], c[1] + e), 255, max(1, int(round(0.22 * k))), cv2.LINE_AA)
    tl.pintar(grelha, FA.CROMO["meio"])
    brilho = tl.vazia()
    cv2.ellipse(brilho, c, (int(round(rr * 0.82)), int(round(rr * 0.82))), 0, -80, -10, 255,
                max(1, int(round(0.25 * k))), cv2.LINE_AA)
    tl.pintar(brilho, FA.CROMO["claro"], 0.9)
    tl.contorno(anel, 0.3, FA.CROMO["contorno"])
    return tl.gravar()


def _torneira_mesa(Q, out, cx, cy, r, q):
    """A torneira de mesa atrás da cuba (do lado da parede, y maior): a base redonda cromada, a bica até o terço de trás
    da bacia (`FA.torneira`, com o brilho e a sombra curta) e a alavanca para a direita."""
    t = q["torneira"]
    by = cy + r + t["recuo_pt"]
    w = t["bica_larg_pt"] / 2
    bica = (cx - w, cy + r * t["bica_ate"], cx + w, by)
    out = FA.torneira(Q, out, bica, (cx, by, t["base_pt"]))
    x0, x1, larg = t["alavanca_pt"]
    return FA.placa_cromada(Q, out, (cx + x0, by - larg / 2, cx + x1, by + larg / 2), raio_pt=0.5)


def bancada_1p(Q, img, q=None):
    q = q or BANCADA_1P
    tl = FA.tela(np.ascontiguousarray(img.copy()), Q, q["bancada_pt"], folga=6)
    m = tl.ret(q["bancada_pt"])
    cx, cy, r = q["cuba_pt"]
    c = np.zeros_like(m)
    u, v = tl.pt(cx, cy)
    cv2.circle(c, (int(round(u)), int(round(v))), int(round(r * FA.PT_PX * 8)), 255, -1)
    m = cv2.bitwise_and(m, cv2.bitwise_not(c))
    tl.pintar_img(m, TA.danae(tl.h, tl.w, q["semente"]))
    tl.contorno(m, 0.35, q["contorno"])
    out = tl.gravar()
    out = _cuba_redonda(Q, out, cx, cy, r, q)
    out = _torneira_mesa(Q, out, cx, cy, r, q)
    print("    bancada: a do quarto de serviço no Dekton Danae, com a cuba redonda de louça (aba, bacia, ralo cromado) e a "
          "torneira de mesa cromada (base, bica e alavanca)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 7b. As cubas dos banhos (usuário, vendo a final: "melhore a representação das cubas esculpidas em marmore travertino
# bruto. e a torneira precisa fica mais bem representada"): nos banhos 1, 2, 3 e master, a bancada do PDF de novo no
# travertino bruto (`final3840_casaa_1pav.banhos`, sem repetir a sombra) e a cuba esculpida nela como a do lavatório do
# Térreo aprovado (`terreo_casaa_1011.cuba_esculpida`: a bacia de cantos redondos, lisa e um tom abaixo, o fundo côncavo,
# a borda fina, o lábio claro e o ralo cromado), com a borda de pedra de `aba_pt` em volta; a torneira de mesa cromada
# maior e mais marcada (a base, a bica, o arejador na ponta e a alavanca de lado), também no B. serviço (cuba branca).
CUBAS_1P = {"banhos": ("master", "banho 1", "banho 2", "banho 3"), "aba_pt": 2.2, "raio_pt": 3.4, "escurecer": 0.84,
            "poros": 0.7,
            "base_pt": 1.95, "bica_pt": 1.9, "alavanca_pt": (4.2, 1.25), "arejador_pt": 0.75}


def _torneira_melhor(Q, out, bica, base, q):
    """A torneira de mesa: a bica (`bica`, pt) alargada para `bica_pt` e a base de raio `base_pt`, com o brilho e a
    sombra curta (`final3840_casaa.torneira`); o arejador na ponta da bica e a alavanca de lado, para a direita da bica
    (de quem está de frente para a cuba)."""
    x0, y0, x1, y1 = bica
    bx, by, _ = base
    vert = (y1 - y0) >= (x1 - x0)
    w = q["bica_pt"] / 2
    if vert:
        cx = (x0 + x1) / 2
        bica = (cx - w, y0, cx + w, y1)
        ponta = (cx, y0) if abs(by - y1) < abs(by - y0) else (cx, y1)
    else:
        cy = (y0 + y1) / 2
        bica = (x0, cy - w, x1, cy + w)
        ponta = (x0, cy) if abs(bx - x1) < abs(bx - x0) else (x1, cy)
    out = FA.torneira(Q, out, bica, (bx, by, q["base_pt"]))
    # o arejador: o disco escuro na ponta da bica
    r = q["arejador_pt"]
    tl = FA.tela(out, Q, (ponta[0] - r - 1, ponta[1] - r - 1, ponta[0] + r + 1, ponta[1] + r + 1), folga=3)
    m = tl.vazia()
    u, v = tl.pt(*ponta)
    cv2.circle(m, (int(round(u)), int(round(v))), int(round(r * FA.PT_PX * 8)), 255, -1, cv2.LINE_AA)
    tl.pintar(m, FA.CROMO["escuro"])
    tl.contorno(m, 0.25, FA.CROMO["contorno"])
    out = tl.gravar()
    # a alavanca, de lado na base (perpendicular à bica)
    L, e = q["alavanca_pt"]
    dx, dy = (ponta[0] - bx, ponta[1] - by)
    n = max(np.hypot(dx, dy), 1e-6)
    px_, py_ = -dy / n, dx / n                                      # a perpendicular
    if px_ + py_ < 0:
        px_, py_ = -px_, -py_
    a = (bx + px_ * 0.6, by + py_ * 0.6)
    b = (bx + px_ * L, by + py_ * L)
    alav = (min(a[0], b[0]) - (e / 2 if abs(px_) < 0.5 else 0), min(a[1], b[1]) - (e / 2 if abs(py_) < 0.5 else 0),
            max(a[0], b[0]) + (e / 2 if abs(px_) < 0.5 else 0), max(a[1], b[1]) + (e / 2 if abs(py_) < 0.5 else 0))
    return FA.placa_cromada(Q, out, alav, raio_pt=0.55)


def cubas_1p(Q, img, q=None):
    q = q or CUBAS_1P
    tb = FA.BANHOS["trav_bancada"]
    out = np.ascontiguousarray(img.copy())

    def travertino(sem):
        return lambda tl: np.float32(tb["tom"]) * FA.travertino_bruto(Q, tl.h, tl.w, sem,
                                                                      **FA.TRAVERTINO["bancada"])[..., None]
    nomes = [k for k, v in P1.BANHOS_1P.items() if isinstance(v, dict)]
    n = 0
    for nome in q["banhos"]:
        b = P1.BANHOS_1P[nome]
        i = nomes.index(nome)
        out = FA.bancada_pedra(Q, out, b["bancada"], travertino(2730 + i), tb["borda"], tb["larg"], 0.0)
        for j, c in enumerate(b["cubas"]):
            a = q["aba_pt"]
            x0, y0, x1, y1 = c["cuba"]
            cc = {"cuba": c["cuba"], "bacia": (x0 + a, y0 + a, x1 - a, y1 - a)}
            out = TA.cuba_esculpida(Q, out, cc, travertino(2740 + 10 * i + j), q["escurecer"], q["raio_pt"],
                                    q["poros"])
            out = _torneira_melhor(Q, out, c["torneira"], c["base"], q)
            n += 1
    for c in P1.BANHOS_1P["B. serviço"]["cubas"]:
        out = _torneira_melhor(Q, out, c["torneira"], c["base"], q)
    print(f"    cubas: {n} cubas esculpidas no travertino bruto (banhos 1, 2, 3 e master) e as torneiras de mesa "
          f"redesenhadas (também a do B. serviço)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 8. O tapete da sala íntima (cliente: "Trocar a cor do tapete. Está camuflando com o piso."; regra [11/11]: tapetes que
# não se confundem com o piso): o tapete do PDF no taupe escolhido para o tapete da varanda do Térreo (opção A), com a
# trama, a luz e a sombra das peças de cima (`terreo_casaa_1011.tapetes_1111`).
TAPETE_1P = dict(TA.TAPETES_1111, opcao="A",
                 tapetes=[("sala íntima", "ARQ_LAYOUT HUMANIZAÇÃO", (1812.1, 1146.1, 1925.5, 1344.5))])


def tapete_1p(Q, img, q=None):
    return TA.tapetes_1111(Q, img, q or TAPETE_1P)



# ----------------------------------------------------------------------------------------------------------------------
# 8b. A sala íntima (usuário, vendo a final: "vamos melhorar esse mobiliário, contorno, sofá, trazendo mais realismo"):
# o sofá em L do PDF redesenhado peça a peça em bouclé creme (o creme da sala do Térreo, `sala_1111`): o encosto alto
# (a faixa de cima e a da direita), as almofadas do encosto com o vinco, as quatro almofadas do assento separadas pela
# costura funda, os dois braços arredondados, cada peça com o volume (a borda mais escura do lado oposto à luz) e a trama
# miúda; três almofadas soltas (terracota e areia) encostadas no encosto; a mesa de centro do render em nogueira (o veio,
# o chanfro) e as três mesinhas redondas (as duas do PDF junto aos braços e a da poltrona) em grafite; a sombra macia de
# todas no tapete e no piso (`final3840_casad.SOMBRA_JOGOS_D`) e o contorno fino. Antes, o tapete sob as peças antigas
# (e as bordas serrilhadas e as sombras borradas delas) é refeito com a trama do próprio tapete (a faixa limpa da
# esquerda, `faixa_tapete_px`, linha a linha: as listras são horizontais) e, fora do tapete, o anel em volta recebe o
# travertino de logo ao lado (`_anel`). A poltrona fica inteira sobre o tapete (usuário: "poltrona deve ficar sobre o
# tapete, na sua integridade"): o tapete desce até 10 px abaixo dela e a poltrona volta inteira (`poltrona_png`).
SALA_INTIMA_1P = {
    # o tapete vai até 10 px abaixo da poltrona (usuário: "poltrona deve ficar sobre o tapete, na sua integridade")
    "tapete_px": (2035.7, 968.6, 2155.1, 1230.5), "amostra_tapete_px": (2040, 1128, 2092, 1160), "debrum": 0.10,
    # a poltrona inteira, recortada da final de partida (ab9a071) antes do passo do tapete, que tingia o alto dela
    "poltrona_png": FA.CASA / "bases" / "POE642_CasaA_1Pavimento_poltrona_sala_intima.png", "poltrona_px": (2064, 1165),
    "folga_px": 8,
    # o sofá (px do PDF): a pegada, os braços, o encosto (a faixa alta e as almofadas, com o vinco) e o assento
    "pegada_px": [(2055.9, 950.4, 2175.3, 1000.7), (2125.0, 1000.7, 2175.3, 1159.4)],
    "bracos_px": [(2055.9, 950.4, 2064.8, 1000.7), (2125.0, 1150.4, 2175.3, 1159.4)],
    "encosto_px": [(2064.8, 950.4, 2175.3, 959.4), (2166.3, 959.4, 2175.3, 1150.4)],
    "almof_encosto_px": [((2064.8, 959.4, 2166.3, 967.8), ("y", 963.5)), ((2157.9, 967.8, 2166.3, 1150.4), ("x", 2162.2))],
    "assento_px": [(2064.8, 967.8, 2124.0, 1000.7), (2124.0, 967.8, 2157.9, 1000.7),
                   (2125.0, 1000.7, 2157.9, 1075.5), (2125.0, 1075.5, 2157.9, 1150.4)],
    "soltas": [((2079.0, 972.5), (24.0, 10.5), -7.0, "terracota"), ((2149.0, 976.0), (23.0, 10.5), -45.0, "areia"),
               ((2151.5, 1131.0), (10.5, 24.0), 6.0, "terracota")],
    "mesa_centro_px": (2056.5, 1044.5, 2093.0, 1117.5),
    "mesinhas_px": [(2077.05, 1004.35, 8.95), (2121.3, 1138.35, 8.95), (2140.5, 1189.0, 13.8)],
    "creme": (200, 214, 226), "base": 0.78, "terracota": (66, 100, 166), "areia": (150, 176, 198),
    "nogueira": (48, 78, 118), "grafite": (74, 76, 79),
    "volume": 0.20, "volume_px": 3.2, "luz": 0.07, "vinco": 0.16, "vinco_px": 0.8, "trama": 0.035,
    "almofada_volume": 0.30, "almofada_px": 2.6, "contorno": (96, 100, 104), "contorno_alfa": 0.55,
    "semente": 1131}


def _volume(m, ss, vol, vol_px, luz):
    """O fator de volume de uma peça estofada (máscara m em ss): a borda arredondada mais escura, mais ainda do lado
    oposto à luz (cima e direita)."""
    dist = cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 5) / ss
    t = np.minimum(1, dist / vol_px)
    gx = cv2.Sobel(dist, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(dist, cv2.CV_32F, 0, 1, ksize=3)
    nn = np.maximum(np.hypot(gx, gy), 1e-6)
    dirl = (gy - gx) / nn / np.sqrt(2)
    return (1 - vol * (1 - t) ** 2) * (1 + luz * dirl * (1 - t))


def _ret_girado(c, tam, ang, raio, X0, Y0, h, w, ss):
    """Um retângulo de cantos arredondados (centro c, tamanho tam, px) girado de `ang` graus, como máscara em ss."""
    M = np.zeros((h * ss, w * ss), np.uint8)
    cx, cy = (c[0] - X0) * ss, (c[1] - Y0) * ss
    a, b = tam[0] * ss / 2 - raio * ss, tam[1] * ss / 2 - raio * ss
    th = np.deg2rad(ang)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    pts = (np.array([[-a, -b], [a, -b], [a, b], [-a, b]]) @ R.T + [cx, cy]).astype(np.int32)
    cv2.fillConvexPoly(M, pts, 255)
    for p in pts:
        cv2.circle(M, tuple(int(v) for v in p), int(round(raio * ss)), 255, -1)
    if raio > 0:
        cv2.polylines(M, [pts], True, 255, int(round(2 * raio * ss)))
    return M.astype(np.float32) / 255


def sala_intima_1p(Q, img, q=None):
    import final3840_casad as D
    import pedidos_terreo_casaa_2910 as P
    q = q or SALA_INTIMA_1P
    out = img.copy()
    H, W = out.shape[:2]
    ss, k = 8, Q.px_m
    rng = np.random.default_rng(q["semente"])
    par = FA.paredes_pdf(Q) > 0.3
    rot = _rotulos_mascara(Q, img)
    # as peças novas (px), como máscara inteira (para limpar) e com a folga
    pecas = np.zeros((H, W), np.uint8)
    for r in q["pegada_px"] + [q["mesa_centro_px"]]:
        cv2.rectangle(pecas, (int(np.floor(r[0])), int(np.floor(r[1]))), (int(np.ceil(r[2])), int(np.ceil(r[3]))), 1, -1)
    for cx, cy, rr in q["mesinhas_px"]:
        cv2.circle(pecas, (int(round(cx)), int(round(cy))), int(np.ceil(rr)), 1, -1)
    pecas = pecas.astype(bool)
    zona = dilatar(pecas, q["folga_px"])
    # 1. o tapete inteiro refeito com a trama de um trecho limpo dele (`amostra_tapete_px`): as listras são horizontais,
    # então cada faixa de linhas vem de linhas da amostra (deslocadas ao acaso) e as colunas da amostra em ladrilhos
    # espelhados; a borda do tapete um pouco mais escura (o debrum); a poltrona fica (os px claros dela na caixa)
    tx0, ty0, tx1, ty1 = q["tapete_px"]
    ax0, ay0, ax1, ay1 = q["amostra_tapete_px"]
    A = img[ay0:ay1, ax0:ax1].astype(np.float32)
    ah, aw = A.shape[:2]
    X0t, Y0t = int(np.floor(tx0)), int(np.floor(ty0))
    wt, ht = int(np.ceil(tx1)) - X0t, int(np.ceil(ty1)) - Y0t
    novo = np.zeros((ht, wt, 3), np.float32)
    for j0 in range(0, ht, ah):
        oy, ox = int(rng.integers(ah)), int(rng.integers(2 * aw))
        for y in range(j0, min(j0 + ah, ht)):
            u = (np.arange(wt) + ox) % (2 * aw)
            novo[y] = A[(y - j0 + oy) % ah, np.where(u < aw, u, 2 * aw - 1 - u)]
    cob = _cobertura((tx0, ty0, tx1, ty1), X0t, Y0t, wt, ht)
    dentro = _cobertura((tx0 + 1.2, ty0 + 1.2, tx1 - 1.2, ty1 - 1.2), X0t, Y0t, wt, ht)
    novo *= (1 - q["debrum"] * np.clip(cob - dentro, 0, 1))[..., None]
    reg = out[Y0t:Y0t + ht, X0t:X0t + wt].astype(np.float32)
    pol = cv2.imread(str(q["poltrona_png"]), cv2.IMREAD_UNCHANGED)
    pa = pol[..., 3].astype(np.float32) / 255
    ppx, ppy = q["poltrona_px"]
    polt_a = np.zeros((H, W), np.float32)
    polt_a[ppy:ppy + pol.shape[0], ppx:ppx + pol.shape[1]] = pa
    polt = polt_a > 0.5
    a_t = cob
    out[Y0t:Y0t + ht, X0t:X0t + wt] = np.clip(np.round(reg * (1 - a_t[..., None]) + novo * a_t[..., None]), 0,
                                               255).astype(np.uint8)
    tap = np.zeros((H, W), bool)
    tap[Y0t:Y0t + ht, X0t:X0t + wt] = cob > 0.02
    ys = np.nonzero(a_t > 0.02)[0]
    # 2. fora do tapete, o anel em volta das peças: o travertino de logo ao lado
    na = _anel(out, pecas, q["folga_px"], 3, par | rot | tap)
    # 3. as máscaras das peças em ss, numa janela só
    X0 = int(np.floor(min(r[0] for r in q["pegada_px"] + [q["mesa_centro_px"]]))) - 24
    Y0 = int(np.floor(min(r[1] for r in q["pegada_px"]))) - 24
    X1 = int(np.ceil(max(r[2] for r in q["pegada_px"]))) + 24
    Y1 = int(np.ceil(max([r[3] for r in q["pegada_px"]] + [c[1] + c[2] for c in q["mesinhas_px"]]
                         + [q["tapete_px"][3]]))) + 24
    w, h = X1 - X0, Y1 - Y0

    def ret(r, raio):
        return P._ret_arred(r, raio, X0, Y0, h, w, ss)

    def red(M):
        return cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA)
    sofa = np.zeros((h * ss, w * ss), np.float32)
    for r in q["pegada_px"]:
        sofa = np.maximum(sofa, ret(r, 2.0))
    mesa = ret(q["mesa_centro_px"], 1.6)
    mesinhas = []
    for cx, cy, rr in q["mesinhas_px"]:
        M = np.zeros((h * ss, w * ss), np.uint8)
        cv2.circle(M, (int(round((cx - X0) * ss)), int(round((cy - Y0) * ss))), int(round(rr * ss)), 255, -1, cv2.LINE_AA)
        mesinhas.append(M.astype(np.float32) / 255)
    # 4. a sombra macia do sofá e da mesa de centro no tapete e no piso
    def sombra(a, onde):
        luz = np.ones((h, w), np.float32)
        for sd in D.SOMBRA_JOGOS_D:
            dm = np.float32([[1, 0, sd["dx_m"] * k], [0, 1, sd["dy_m"] * k]])
            luz *= 1 - cv2.GaussianBlur(cv2.warpAffine(a, dm, (w, h), flags=cv2.INTER_LINEAR), (0, 0),
                                        sd["sig_m"] * k) * sd["forca"]
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg *= (1 - (1 - luz) * (1 - a) * onde)[..., None]
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    livre = (~par[Y0:Y1, X0:X1]).astype(np.float32)
    sombra(np.maximum(red(sofa), red(mesa)), livre)
    sombra(polt_a[Y0:Y1, X0:X1], tap[Y0:Y1, X0:X1].astype(np.float32))
    # a poltrona inteira por cima do tapete
    reg = out[ppy:ppy + pol.shape[0], ppx:ppx + pol.shape[1]].astype(np.float32)
    out[ppy:ppy + pol.shape[0], ppx:ppx + pol.shape[1]] = np.clip(np.round(
        reg * (1 - pa[..., None]) + pol[..., :3].astype(np.float32) * pa[..., None]), 0, 255).astype(np.uint8)
    # 5. o sofá: a base (a costura funda entre as peças), o encosto alto, os braços, as almofadas do encosto e do assento
    creme = np.float32(q["creme"])
    tr = cv2.GaussianBlur(rng.normal(0, 1, sofa.shape).astype(np.float32), (0, 0), 0.4 * ss)
    tr2 = cv2.GaussianBlur(rng.normal(0, 1, sofa.shape).astype(np.float32), (0, 0), 1.6 * ss)
    trama = (1 + q["trama"] * tr / max(float(tr.std()), 1e-6)) * (1 + 0.6 * q["trama"] * tr2 / max(float(tr2.std()), 1e-6))
    out = P._pintar(out, X0, Y0, w, h, ss, sofa, creme[None, None] * (q["base"] * trama)[..., None])
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    px, py = (xx + 0.5) / ss + X0, (yy + 0.5) / ss + Y0
    folga = 0.35

    def peca(r, raio, claro=1.0, vinco=None):
        M = ret((r[0] + folga, r[1] + folga, r[2] - folga, r[3] - folga), raio)
        f = _volume(M > 0.5, ss, q["volume"], q["volume_px"], q["luz"]) * claro * trama
        if vinco:
            eixo, v = vinco
            f *= 1 - q["vinco"] * np.exp(-(((px if eixo == "x" else py) - v) / q["vinco_px"]) ** 2)
        return P._pintar(out, X0, Y0, w, h, ss, M, creme[None, None] * f[..., None])
    for r in q["encosto_px"]:
        out = peca(r, 1.8, 1.03)
    for r, vinco in q["almof_encosto_px"]:
        out = peca(r, 2.0, 0.97, vinco)
    for r in q["assento_px"]:
        out = peca(r, 2.4, 1.0)
    for r in q["bracos_px"]:
        out = peca(r, 2.6, 1.04)
    # as almofadas soltas, com a sombra curta no assento
    for c, tam, ang, cor in q["soltas"]:
        M = _ret_girado(c, tam, ang, 1.9, X0, Y0, h, w, ss)
        a = red(M)
        sh = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -1.0], [0, 1, 1.0]]), (w, h)), (0, 0), 1.0)
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg *= (1 - 0.35 * sh * (1 - a))[..., None]
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        f = _volume(M > 0.5, ss, q["almofada_volume"], q["almofada_px"], q["luz"]) * trama
        out = P._pintar(out, X0, Y0, w, h, ss, M, np.float32(q[cor])[None, None] * f[..., None])
    # 6. a mesa de centro em nogueira e as mesinhas em grafite, com a sombra delas (também no sofá)
    out = P._madeira_peca(Q, out, mesa, X0, Y0, w, h, ss, q["nogueira"], 90.0, int(rng.integers(1 << 30)), sombra=False)
    for M in mesinhas:
        sombra(red(M), livre)
        f = _volume(M > 0.5, ss, 0.10, 1.6, 0.10) * (1 + 0.012 * tr / max(float(tr.std()), 1e-6))
        out = P._pintar(out, X0, Y0, w, h, ss, M, np.float32(q["grafite"])[None, None] * f[..., None])
    # 7. o contorno fino do sofá e das mesas
    tudo = np.maximum.reduce([sofa, mesa] + mesinhas)
    borda = np.clip(tudo - cv2.erode(tudo, np.ones((int(0.6 * ss), int(0.6 * ss)), np.uint8)), 0, 1) * q["contorno_alfa"]
    out = P._pintar(out, X0, Y0, w, h, ss, borda, np.float32(q["contorno"])[None, None] * np.ones_like(borda)[..., None])
    print(f"    sala íntima: o sofá em L em bouclé creme peça a peça (encosto, almofadas, braços, 3 almofadas soltas), a "
          f"mesa de centro em nogueira, 3 mesinhas em grafite, a sombra macia e o contorno fino; o tapete refeito sob as "
          f"peças antigas: inteiro, com a trama dele ({len(ys)} linhas de px) e o piso em volta ({na} px)")
    return out

# ----------------------------------------------------------------------------------------------------------------------
# 9. Os guarda-roupas em L e em U (cliente: "Deixar os cabides se encontrando no 'L' do guarda-roupa. Tirar essa lateral
# como se fossem dois guarda-roupas separados."): cada guarda-roupa dos closets (o 3 e o 2, dos recortes, e, na mesma
# regra, o master em U e o 1) redesenhado como uma peça só, no desenho de `_texturas/elementos.guarda_roupa` (o fundo
# bege que escurece junto às portas, os cabides de través, o cabideiro de metal, a moldura ocre): sem a lateral entre os
# trechos; os cabideiros dos trechos se encontram no meio do canto (em L) e os cabides de cada trecho vão até o canto; as
# portas só nas faces do trecho voltadas para o closet. Os retângulos do PDF (pt), como em
# `ajustes_casaa.GUARDA_ROUPAS_1PAV`: cada trecho sem o canto e os cantos à parte.
CLOSETS_1P = {
    "closet 3": {"trechos": [((1664.1, 613.0, 1698.1, 692.3), "direita"), ((1698.1, 579.0, 1825.6, 613.0), "baixo")],
                 "cantos": [(1664.1, 579.0, 1698.1, 613.0)]},
    "closet 2": {"trechos": [((1598.9, 1072.2, 1729.3, 1106.2), "baixo"), ((1729.3, 1106.2, 1763.3, 1276.3), "esquerda")],
                 "cantos": [(1729.3, 1072.2, 1763.3, 1106.2)]},
    "closet master": {"trechos": [((1539.3, 1483.3, 1652.7, 1517.4), "baixo"), ((1652.7, 1517.4, 1686.7, 1741.2), "esquerda"),
                                  ((1536.5, 1741.2, 1652.7, 1775.2), "cima")],
                      "cantos": [(1652.7, 1483.3, 1686.7, 1517.4), (1652.7, 1741.2, 1686.7, 1775.2)]},
    "closet 1": {"trechos": [((2021.2, 1415.2, 2055.2, 1483.2), "direita"), ((2055.2, 1381.2, 2174.3, 1415.2), "baixo")],
                 "cantos": [(2021.2, 1381.2, 2055.2, 1415.2)]},
    "miolo": (191, 212, 228), "moldura": (88, 148, 196), "semente": 1119, "ss": 8,
    "lateral_cm": 2.0, "fundo_cm": 1.2, "porta_cm": 2.5, "contorno_cm": 0.6, "tubo_cm": 1.0}
CM = 56.69 / 100.0                       # pt por cm (escala 1:50)


def _closet(Q, out, c, q, rng):
    pecas = [r for r, _ in c["trechos"]] + list(c["cantos"])
    caixa = (min(r[0] for r in pecas), min(r[1] for r in pecas), max(r[2] for r in pecas), max(r[3] for r in pecas))
    tl = FA.tela(out, Q, caixa, folga=3)
    S = 8
    ys, xs = np.mgrid[0:tl.h * S, 0:tl.w * S].astype(np.float32)
    (ax, ay), (bx, by) = Q.q2p(tl.x0, tl.y0), Q.q2p(tl.x0 + 1, tl.y0 + 1)
    X, Y = ax + (xs + 0.5) / S * (bx - ax), ay + (ys + 0.5) / S * (by - ay)

    def dentro(r):
        return (X >= r[0]) & (X < r[2]) & (Y >= r[1]) & (Y < r[3])

    def colado(a, b):
        """Se os retângulos a e b têm um lado em comum (ou quase)."""
        t = 0.3
        return ((abs(a[2] - b[0]) < t or abs(b[2] - a[0]) < t) and min(a[3], b[3]) - max(a[1], b[1]) > t) or \
               ((abs(a[3] - b[1]) < t or abs(b[3] - a[1]) < t) and min(a[2], b[2]) - max(a[0], b[0]) > t)
    U = np.zeros(X.shape, bool)
    for r in pecas:
        U |= dentro(r)
    # a profundidade relativa (0 no fundo, 1 nas portas) de cada trecho e, no canto, a menor das dos vizinhos
    def prof(r, lado):
        x0, y0, x1, y1 = r
        return {"baixo": (Y - y0) / (y1 - y0), "cima": (y1 - Y) / (y1 - y0), "direita": (X - x0) / (x1 - x0),
                "esquerda": (x1 - X) / (x1 - x0)}[lado]
    yy = np.zeros(X.shape, np.float32)
    for r, lado in c["trechos"]:
        m = dentro(r)
        yy[m] = np.clip(prof(r, lado), 0, 1)[m]
    for k in c["cantos"]:
        m = dentro(k)
        viz = [prof(r, lado) for r, lado in c["trechos"] if colado(r, k)]
        yy[m] = np.clip(np.minimum.reduce(viz), 0, 1)[m]
    t = (216 - 40 * yy ** 1.4)[..., None] * np.ones((1, 1, 3), np.float32)
    # os cabides: de través em cada trecho, a cada 10 a 14 cm, até o canto
    sig = 0.7 * CM
    for r, lado in c["trechos"]:
        x0, y0, x1, y1 = r
        horiz = lado in ("baixo", "cima")
        a0, a1 = (x0, x1) if horiz else (y0, y1)
        lados_canto = [k for k in c["cantos"] if colado(r, k)]
        ini = a0 + (2 if any((k[2] <= x0 + 0.3) if horiz else (k[3] <= y0 + 0.3) for k in lados_canto) else
                    rng.uniform(5, 9)) * CM
        fim = a1 - (2 if any((k[0] >= x1 - 0.3) if horiz else (k[1] >= y1 - 0.3) for k in lados_canto) else 5) * CM
        dep = (y1 - y0) if horiz else (x1 - x0)
        p = ini
        m = dentro(r)
        while p < fim:
            f0, f1 = rng.uniform(0.12, 0.20), rng.uniform(0.78, 0.88)
            s = Y if not horiz else X
            perfil = np.exp(-0.5 * ((s - p) / sig) ** 2)
            fr = np.clip(prof(r, lado), 0, 1)
            sel = m & (fr >= f0) & (fr <= f1)
            t[sel] -= (rng.uniform(38, 52) * perfil[sel])[..., None]
            p += rng.uniform(10, 14) * CM
    t = t / 216 * np.float32(q["miolo"])
    # o cabideiro: o tubo no meio de cada trecho, até o meio de cada canto colado; a sombra curta e o brilho
    tubo = np.zeros(X.shape, np.float32)
    dist_t = np.full(X.shape, np.inf, np.float32)
    r_t = q["tubo_cm"] * CM
    for r, lado in c["trechos"]:
        x0, y0, x1, y1 = r
        horiz = lado in ("baixo", "cima")
        a0, a1 = (x0 + 2 * CM, x1 - 2 * CM) if horiz else (y0 + 2 * CM, y1 - 2 * CM)
        for k in c["cantos"]:
            if colado(r, k):
                kc = ((k[0] + k[2]) / 2, (k[1] + k[3]) / 2)
                if horiz:
                    a0, a1 = (min(a0, kc[0]), a1) if k[2] <= x0 + 0.3 else (a0, max(a1, kc[0]))
                else:
                    a0, a1 = (min(a0, kc[1]), a1) if k[3] <= y0 + 0.3 else (a0, max(a1, kc[1]))
        if horiz:
            yc = (y0 + y1) / 2
            d = np.where((X >= a0 - r_t) & (X <= a1 + r_t), np.abs(Y - yc), np.inf)
        else:
            xc = (x0 + x1) / 2
            d = np.where((Y >= a0 - r_t) & (Y <= a1 + r_t), np.abs(X - xc), np.inf)
        dist_t = np.minimum(dist_t, d)
    perfil = np.clip(1 - (dist_t / r_t) ** 2, 0, 1)
    sombra = np.exp(-0.5 * ((dist_t - 1.6 * r_t) / (0.8 * r_t)) ** 2) * 0.22 * (dist_t < 3 * r_t)
    t *= (1 - sombra)[..., None]
    metal = (110 + 120 * np.clip(1 - np.abs(dist_t / r_t - 0.3) * 1.4, 0, 1))[..., None] * np.ones((1, 1, 3), np.float32)
    t = np.where((perfil > 0)[..., None], metal, t)
    # a moldura: as laterais e o fundo em ocre, as portas uma faixa de 2,5 cm, e o contorno escuro; nada entre os trechos
    mold = np.float32(q["moldura"])
    for r, lado in [(r, l) for r, l in c["trechos"]] + [(k, None) for k in c["cantos"]]:
        x0, y0, x1, y1 = r
        m = dentro(r)
        outros = [o for o in pecas if o is not r]
        for nome, d, e_fora in (("esq", X - x0, (x0 - 0.5, y0, x0, y1)), ("dir", x1 - X, (x1, y0, x1 + 0.5, y1)),
                                ("cima", Y - y0, (x0, y0 - 0.5, x1, y0)), ("baixo", y1 - Y, (x0, y1, x1, y1 + 0.5))):
            interno = any(colado(e_fora, o) or (o[0] < e_fora[2] and o[2] > e_fora[0] and o[1] < e_fora[3] and
                                                 o[3] > e_fora[1]) for o in outros)
            if interno:
                continue
            porta = lado is not None and {"esquerda": "esq", "direita": "dir", "cima": "cima", "baixo": "baixo"}[lado] == nome
            fundo = lado is None or {"esquerda": "dir", "direita": "esq", "cima": "baixo", "baixo": "cima"}[lado] == nome
            larg = (q["porta_cm"] if porta else (q["fundo_cm"] if fundo else q["lateral_cm"])) * CM
            fx = 1.0 if porta else 0.97
            sel = m & (d < larg)
            t[sel] = mold * fx
            sel = m & (d < q["contorno_cm"] * CM)
            t[sel] = mold * 0.68
    a = tl.reduzir((U * 255).astype(np.uint8))
    cor = cv2.resize(t * U[..., None], (tl.w, tl.h), interpolation=cv2.INTER_AREA) / np.maximum(a, 1e-4)[..., None]
    tl.reg = tl.reg * (1 - a[..., None]) + cor * a[..., None]
    return tl.gravar()


def closets_1p(Q, img, q=None):
    q = q or CLOSETS_1P
    out = np.ascontiguousarray(img.copy())
    rng = np.random.default_rng(q["semente"])
    nomes = [k for k in q if k.startswith("closet")]
    for n in nomes:
        out = _closet(Q, out, q[n], q, rng)
    print(f"    guarda-roupas: {len(nomes)} closets ({', '.join(nomes)}) numa peça só, os cabides se encontrando no "
          f"canto, sem a lateral entre os trechos")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 10. As portas quina a quina (cliente: "Encostar essa porta mais na parede, ela tá solta."; usuário: "revisar todas as
# portas, quina a quina para todas as portas com suas respectivas paredes."; regra [10/11] e [11/11]): todas as folhas de
# abrir do PDF (as peças brancas finas da ARQ_PAREDE presas a um marco) foram conferidas; nas 11 em que a folha parava
# antes da ponta da parede (`_ligar_folha` pede a ponte), a ponta da parede avança até a face de dentro da folha, sem o
# marco, vértice com vértice (`cliente_subsolo_casaa_0511.portais_cs`, como no Térreo). As portas de correr das suítes
# (bronze e vidro) e as do elevador ficam como estão.
PORTAS_1P = {"caixas": {"closet_master": (1676, 1462, 1752, 1482), "closet_2": (1742, 980, 1818, 1000),
                        "suite_master": (1843, 1214, 1919, 1234), "suite_3": (1966, 580, 2041, 600),
                        "suite_2": (1966, 1147, 1986, 1223), "banho_3": (2043, 473, 2119, 492),
                        "quarto_serv_1": (2101, 1317, 2120, 1393), "quarto_serv_2": (2101, 1428, 2120, 1503),
                        "b_servico": (2148, 1554, 2212, 1573), "suite_1": (2162, 1317, 2181, 1393),
                        "closet_1": (2411, 1306, 2486, 1325)},
             "cor_parede": 80, "claros": {"mediana": 5, "acima": 25, "subiu": 20}}


def portas_1p(Q, img, q=None):
    import cliente_subsolo_casaa_0511 as CS
    q = q or PORTAS_1P
    antes = CS.PORTAIS_CS
    CS.PORTAIS_CS = dict(antes, portais=q["caixas"], faixas={}, cor_parede=q["cor_parede"],
                         contorno=(0.0, q["cor_parede"]), piso_min=70)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            out = CS.portais_cs(Q, img.copy())
    finally:
        CS.PORTAIS_CS = antes
    cl = q["claros"]
    for x0, y0, x1, y1 in q["caixas"].values():
        reg = out[y0:y1, x0:x1]
        med = cv2.medianBlur(np.ascontiguousarray(reg), cl["mediana"])
        lr, lm = reg.astype(np.float32).mean(axis=2), med.astype(np.float32).mean(axis=2)
        lv = img[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m = (lr > lm + cl["acima"]) & (lr > lv + cl["subiu"])
        reg[m] = med[m]
    print(f"    portas: {len(q['caixas'])} folhas presas à ponta da parede, quina a quina "
          f"({', '.join(q['caixas'])})")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 11. As escadas (cliente: "Colocar a seta e a descrição em todas as escadas. Representar o guarda-corpo."; na caracol:
# "Colocar a seta na escada e a descrição Desce para 'tal espaço'"; regra [10/11]: o triângulo cheio no degrau de quem
# chega por este pavimento, a ponta no sentido do percurso, e a descrição em duas linhas, no corpo das descrições do
# Térreo): o D das duas sai; a escada em U desce para o hall interno do Térreo (o triângulo no degrau 19, para a
# direita, e "DESCE PARA O / HALL INTERNO" sobre os degraus do lance); a caracol desce para a área de serviço (o
# triângulo no degrau de chegada, junto aos 0°, no sentido horário, e "DESCE PARA A / ÁREA DE SERVIÇO" na saleta). Os
# guarda-corpos de vidro do PDF (ARQ_ELEMENTOS FIXOS) no desenho dos vidros (regra [22/10]): na escada em U, o contorno
# da escada (em cima, na direita e embaixo) e a borda da circulação junto ao poço; na caracol, os três que fecham a
# abertura (o anel do corrimão fica como está).
ESCADAS_1P = {"u": {"letra": ("D", (0, 24)), "tri_px": (2264.0, 1046.0), "dir": (1, 0), "txt_px": (2281.0, 1046.0),
                    "texto": ("DESCE PARA O", "HALL INTERNO"), "alinhar": "esquerda",
                    "guarda_corpo_pt": [(2017.8, 1072.2, 2019.0, 1185.6), (2017.8, 1253.6, 2019.0, 1276.3),
                                        (2021.2, 1097.1, 2240.1, 1098.3), (2238.9, 1097.1, 2240.1, 1251.3),
                                        (2019.5, 1250.2, 2240.1, 1251.3)]},
              "caracol": {"apagar_px": (2001, 1552, 2019, 1570), "ang": 9.85, "raio_pt": 28.0, "tri": (13.0, 15.0),
                          "sentido": -1,
                          "txt_px": (2052.0, 1604.0), "texto": ("DESCE PARA A", "ÁREA DE SERVIÇO"),
                          "alinhar": "esquerda",
                          "guarda_corpo_pt": [(1808.6, 1715.1, 1819.7, 1716.2), (1818.6, 1715.1, 1819.7, 1775.2),
                                              (1759.9, 1647.6, 1761.0, 1718.5)]},
              "cor_texto": (45, 45, 45)}


def escadas_1p(Q, img, q=None):
    q = q or ESCADAS_1P
    out = np.ascontiguousarray(img.copy())
    u, c = q["u"], q["caracol"]
    # o D da escada em U sai (o degrau de baixo dele, no mesmo degrau); o da caracol, por inpaint (o triângulo cobre)
    out = TA.tirar_letra(Q, out, u["letra"][0], Q.p2q(*P1.ESCADA_U_1P["centro"]), u["letra"][1])
    x0, y0, x1, y1 = c["apagar_px"]
    reg = out[y0:y1, x0:x1]
    esc = (reg.astype(np.float32).mean(axis=2) < 110).astype(np.uint8)
    out[y0:y1, x0:x1] = cv2.inpaint(reg, cv2.dilate(esc, np.ones((3, 3), np.uint8)) * 255, 3, cv2.INPAINT_TELEA)
    # os guarda-corpos de vidro
    out = TA.vidro_laminas(Q, out, u["guarda_corpo_pt"] + c["guarda_corpo_pt"], TA.ESCADAS_TA["jardim"]["vidro"])
    # os triângulos e as descrições
    tx, ty = u["tri_px"]
    out = TA.triangulo(out, TA.seta_tri(tx, ty, u["dir"]))
    out = TA._texto_escada(out, u["texto"], *u["txt_px"], u["alinhar"], q["cor_texto"])
    cx, cy = Q.p2q(*P1.CARACOL_1P["centro"])
    ang = np.radians(c["ang"])
    rm = c["raio_pt"] * FA.PT_PX
    tx, ty = cx + rm * np.cos(ang), cy - rm * np.sin(ang)
    sg = c.get("sentido", 1)                              # 1: horário; -1: anti-horário (a descida para a esquerda)
    out = TA.triangulo(out, TA.seta_tri(tx, ty, (sg * np.sin(ang), sg * np.cos(ang)), *c["tri"]))
    out = TA._texto_escada(out, c["texto"], *c["txt_px"], c["alinhar"], q["cor_texto"])
    print("    escadas: o triângulo e a descrição nas duas (DESCE PARA O HALL INTERNO, na em U; DESCE PARA A ÁREA DE "
          "SERVIÇO, na caracol), sem o D; os guarda-corpos de vidro da escada em U e da abertura da caracol")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 12. A floreira do banho master (cliente: "Diminuir o tamanho dessa vegetação"): a folhagem grande, que passava da
# floreira para o banho, sai; o banho volta a ter o travertino (tecido do próprio banho, `piso_refeito`); a floreira (o
# vão do PDF entre a fachada e a divisória de vidro) recebe a forração verde baixa e as 3 plantas do PDF, pequenas
# (copas de 0,40 a 0,48 m, as plantas da biblioteca), cada uma dentro dela; a divisória de vidro de correr do PDF (as 3
# folhas desencontradas da ARQ_PAREDE) volta por cima, no desenho dos vidros.
FLOREIRA_1P = {"banho_px": (1387, 1464, 1410, 1630), "desloc_px": 129, "desloc_box_px": 60, "box_y": 1565, "torneira_px": (1396, 1493, 1407, 1504),
               "restos_px": (1405, 1527, 1424, 1562),
               "canteiro_px": (1346.0, 1464.0, 1387.5, 1628.7), "forracao": (70, 104, 78), "contraste": 0.55,
               "plantas": [("palmeira_1", (1362.5, 1490.0), 0.48), ("arbusto_3", (1362.5, 1562.0), 0.40),
                           ("palmeira_3", (1361.5, 1606.0), 0.44)],
               "vidros_pt": [(1193.8, 1623.2, 1196.7, 1668.6), (1191.0, 1673.1, 1193.8, 1718.5),
                             (1188.2, 1723.0, 1191.0, 1768.4)],
               "semente": 1121}


def floreira_1p(Q, img, q=None):
    import pedidos_terreo_casaa_2910 as P
    sys.path.insert(0, str(TA.RAIZ / "_texturas"))
    import texturas
    q = q or FLOREIRA_1P
    out = img.copy()
    # o banho sem as folhas: a faixa entre a divisória de vidro e a banheira recebe o piso do próprio banho, das mesmas
    # linhas mais à direita (`desloc_px`: o travertino, o vidro do box e o piso do box seguem no lugar), menos a torneira
    # da banheira; as emendas esfumadas
    x0, y0, x1, y1 = q["banho_px"]
    dx = q["desloc_px"]
    zona = np.zeros(img.shape[:2], np.float32)
    zona[y0:y1, x0:x1] = 1
    a0, b0, a1, b1 = q["torneira_px"]
    zona[b0:b1, a0:a1] = 0
    zona = cv2.GaussianBlur(zona, (0, 0), 0.8)
    # acima do vidro do box, o piso de `desloc_px` à direita; do vidro para baixo (o piso do box), o de `desloc_box_px`
    yb = q["box_y"]
    fonte = np.roll(img, -dx, axis=1).astype(np.float32)
    fonte[yb:] = np.roll(img, -q["desloc_box_px"], axis=1)[yb:]
    out = np.clip(np.round(img * (1 - zona[..., None]) + fonte * zona[..., None]), 0, 255).astype(np.uint8)
    # os restos escuros das folhas junto à banheira (manchas pequenas bem mais escuras que o piso)
    a0, b0, a1, b1 = q["restos_px"]
    reg = out[b0:b1, a0:a1]
    lum = reg.astype(np.float32).mean(axis=2)
    esc = ((lum < cv2.medianBlur(reg, 9).astype(np.float32).mean(axis=2) - 25)).astype(np.uint8)
    out[b0:b1, a0:a1] = cv2.inpaint(reg, cv2.dilate(esc, np.ones((3, 3), np.uint8)) * 255, 3, cv2.INPAINT_TELEA)
    # o canteiro: a forração verde baixa (a grama do padrão, escura e de pouco contraste), com a sombra das bordas
    a0, b0, a1, b1 = q["canteiro_px"]
    X0, Y0, X1, Y1 = int(np.floor(a0)), int(np.floor(b0)), int(np.ceil(a1)), int(np.ceil(b1))
    h, w = Y1 - Y0, X1 - X0
    g = texturas.textura("grama_padrao", Q.px_m, h, w, semente=q["semente"]).astype(np.float32)
    g = g.mean(axis=(0, 1)) + (g - g.mean(axis=(0, 1))) * q["contraste"]
    g = g / g.reshape(-1, 3).mean(axis=0) * np.float32(q["forracao"])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    borda = np.minimum.reduce([xx + 0.5, w - xx - 0.5, yy + 0.5, h - yy - 0.5])
    g *= (1 - 0.25 * np.exp(-borda / 2.5))[..., None]
    a = ret_alfa(Q, (a0, b0, a1, b1))[Y0:Y1, X0:X1, None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + g * a), 0, 255).astype(np.uint8)
    # as 3 plantas pequenas
    for nome, (cx, cy), d in q["plantas"]:
        TA._pousar(out, nome, cx, cy, d, Q.px_m)
    # a divisória de vidro por cima
    out = TA.vidro_laminas(Q, out, q["vidros_pt"], TA.ESCADAS_TA["jardim"]["vidro"])
    print(f"    floreira do banho master: a folhagem grande sai (o banho com o travertino de volta); "
          f"a forração verde e {len(q['plantas'])} plantas pequenas dentro do canteiro; a divisória de vidro")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 13. Os bancos em frente às camas (usuário, vendo a suíte 1: "vamos representar esses bancos em frente as camas com mais
# realismo"): os cinco bancos de pé de cama (suítes 3, 2, master e os dois da suíte 1) redesenhados como banco estofado:
# a base de nogueira aparecendo num aro fino, o assento de linho caramelo com volume (a borda arredondada mais escura do
# lado oposto à luz, que vem de cima e da direita como nas outras sombras), o vivo da costura na borda, o vinco entre as
# duas almofadas nos bancos longos, a trama do tecido e a sombra macia no tapete (a mesma dos outros móveis,
# `final3840_casad.SOMBRA_JOGOS_D`). Antes, o anel do banco antigo (a sombra e o contorno borrados) recebe o tapete de
# logo ao lado (`_anel`), menos do lado da cama. As caixas são as do render (a borda de fora de cada banco), não as do
# PDF: na suíte 3 e na master a cama e o banco do render saíram alguns px deslocados do PDF. `cama`: o lado da cama
# (-1: em cima; +1: embaixo).
BANCOS_1P = {"bancos_px": [("Suíte 3", (1691.5, 486.5, 1788.5, 512.5), -1),
                           ("Suíte Master", (1456.5, 1290.5, 1552.5, 1316.5), +1),
                           ("Suíte 2", (1716.5, 1060.5, 1812.5, 1085.5), +1),
                           ("Suíte 1", (2310.5, 1430.5, 2365.5, 1449.5), +1),
                           ("Suíte 1", (2414.5, 1430.5, 2470.5, 1449.5), +1)],
             "madeira": (60, 94, 136), "raio_px": 1.4, "aro_px": 0.95, "assento_raio_px": 2.2,
             "linho": (142, 174, 206), "volume": 0.24, "volume_px": 4.2, "luz": 0.08, "vivo": 0.07,
             "vivo_px": (0.5, 0.4), "vinco": 0.09, "vinco_px": 1.1, "trama": 0.014, "fio": 0.012, "nuvem": 0.018,
             "longo_px": 70, "anel_px": 4, "semente": 1121}


def bancos_1p(Q, img, q=None):
    import final3840_casad as D
    import pedidos_terreo_casaa_2910 as P
    q = q or BANCOS_1P
    out = img.copy()
    H, W = out.shape[:2]
    par = FA.paredes_pdf(Q) > 0.3
    rot = _rotulos_mascara(Q, img)
    ss, k = 8, Q.px_m
    rng = np.random.default_rng(q["semente"])
    nl = 0
    for nome, r, cama in q["bancos_px"]:
        x0, y0, x1, y1 = r
        lado_cama = np.zeros((H, W), bool)
        if cama < 0:
            lado_cama[:int(np.floor(y0)), :] = True
        else:
            lado_cama[int(np.ceil(y1)):, :] = True
        # 1. o anel do banco antigo limpo (o tapete de logo ao lado), menos do lado da cama
        U = np.zeros((H, W), bool)
        U[int(np.floor(y0)):int(np.ceil(y1)), int(np.floor(x0)):int(np.ceil(x1))] = True
        nl += _anel(out, U, q["anel_px"], 3, par | rot | lado_cama)
        f = 16
        X0, Y0, X1, Y1 = int(np.floor(x0)) - f, int(np.floor(y0)) - f, int(np.ceil(x1)) + f, int(np.ceil(y1)) + f
        w, h = X1 - X0, Y1 - Y0
        M = P._ret_arred(r, q["raio_px"], X0, Y0, h, w, ss)
        a = cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA)
        # 2. a sombra macia no tapete (não na cama, mais alta, nem nas paredes)
        luz = np.ones((h, w), np.float32)
        for s in D.SOMBRA_JOGOS_D:
            dm = np.float32([[1, 0, s["dx_m"] * k], [0, 1, s["dy_m"] * k]])
            luz *= 1 - cv2.GaussianBlur(cv2.warpAffine(a, dm, (w, h), flags=cv2.INTER_LINEAR), (0, 0),
                                        s["sig_m"] * k) * s["forca"]
        livre = (~(lado_cama | par)[Y0:Y1, X0:X1]).astype(np.float32)
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg *= (1 - (1 - luz) * (1 - a) * livre)[..., None]
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        # 3. a base de nogueira (o aro em volta do assento)
        out = P._madeira_peca(Q, out, M, X0, Y0, w, h, ss, q["madeira"], 0.0, int(rng.integers(1 << 30)), sombra=False)
        # 4. o assento de linho: uma ou duas almofadas, cada uma com o seu volume
        ar = q["aro_px"]
        ri = (x0 + ar, y0 + ar, x1 - ar, y1 - ar)
        S = P._ret_arred(ri, q["assento_raio_px"], X0, Y0, h, w, ss)
        yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
        px = (xx + 0.5) / ss + X0
        cortes = [ri[0], ri[2]]
        if x1 - x0 > q["longo_px"]:
            cortes = [ri[0], (ri[0] + ri[2]) / 2, ri[2]]
        fator = np.ones(S.shape, np.float32)
        for a_, b_ in zip(cortes[:-1], cortes[1:]):
            m = ((px >= a_) & (px < b_) & (S > 0.5)).astype(np.uint8)
            dist = cv2.distanceTransform(m, cv2.DIST_L2, 5) / ss
            t = np.minimum(1, dist / q["volume_px"])
            gx = cv2.Sobel(dist, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(dist, cv2.CV_32F, 0, 1, ksize=3)
            nn = np.maximum(np.hypot(gx, gy), 1e-6)
            dirl = (gy - gx) / nn / np.sqrt(2)                      # +: a borda virada para a luz (cima e direita)
            vivo = np.exp(-((dist - q["vivo_px"][0]) / q["vivo_px"][1]) ** 2)
            fs = (1 - q["volume"] * (1 - t) ** 2) * (1 + q["luz"] * dirl * (1 - t)) * (1 - q["vivo"] * vivo)
            fator = np.where(m > 0, fs, fator)
        for c in cortes[1:-1]:
            fator *= 1 - q["vinco"] * np.exp(-((px - c) / q["vinco_px"]) ** 2)
        tr = cv2.GaussianBlur(rng.normal(0, 1, S.shape).astype(np.float32), (0, 0), 0.5 * ss)
        fio = cv2.GaussianBlur(rng.normal(0, 1, S.shape).astype(np.float32), (0, 0), sigmaX=2.5 * ss, sigmaY=0.3 * ss)
        nv = cv2.GaussianBlur(rng.normal(0, 1, S.shape).astype(np.float32), (0, 0), 3.0 * ss)
        fator *= (1 + q["trama"] * tr / max(float(tr.std()), 1e-6)) * (1 + q["fio"] * fio / max(float(fio.std()), 1e-6))
        fator *= 1 + q["nuvem"] * nv / max(float(nv.std()), 1e-6)
        out = P._pintar(out, X0, Y0, w, h, ss, S, np.float32(q["linho"])[None, None, :] * fator[..., None])
    print(f"    bancos: {len(q['bancos_px'])} bancos de pé de cama estofados (base de nogueira, assento de linho com "
          f"volume, vivo e vinco, sombra macia), o anel do banco antigo limpo ({nl} px)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 14. Os shafts (usuário: "melhore a representação do x tracejado"; regra: X dos shafts em preto): o fundo de cada shaft
# (o vão entre as paredes na final, `shafts_px`: o de cima é o do render, mais alto que o do PDF) limpo em branco, sem os
# retângulos e os riscos do render, e o X tracejado redesenhado de canto a canto, fino e simétrico (um traço cruza o
# centro, o mesmo passo para os dois lados). As paredes de `paredes_px` (o dente da parede dos shafts da suíte master)
# recebem de novo o cinza das paredes, no desenho do PDF; `manchas_px` (a quina junto ao shaft de cima, com os px pretos
# do render) fica toda no cinza das paredes.
SHAFTS_1P = {"shafts_px": [(2256, 354, 2346, 402), (2355, 1118, 2384, 1207), (1660, 1438, 1712, 1455),
                           (1722, 1435, 1738, 1455)],
             "paredes_px": [(1644, 1424, 1752, 1470)], "manchas_px": [(2346, 401, 2357, 416)], "parede": (80, 80, 80),
             "fundo": (246, 246, 245), "x": (60, 60, 60), "x_px": 0.85, "traco_px": 3.4, "vao_px": 2.2,
             "recuo_px": 1.8}


def shafts_1p(Q, img, q=None):
    q = q or SHAFTS_1P
    out = img.astype(np.float32)
    par = np.clip(FA.paredes_pdf(Q), 0, 1).astype(np.float32)
    for x0, y0, x1, y1 in q["paredes_px"]:
        a = par[y0:y1, x0:x1][..., None]
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + np.float32(q["parede"]) * a
    for x0, y0, x1, y1 in q["manchas_px"]:                         # a quina de parede com os px pretos do render
        out[y0:y1, x0:x1] = np.float32(q["parede"])
    ss = 8
    for x0, y0, x1, y1 in q["shafts_px"]:                           # o vão do shaft na final (as paredes ficam)
        out[y0:y1, x0:x1] = np.float32(q["fundo"])
        r = q["recuo_px"]
        X0, Y0 = x0 - 2, y0 - 2
        w, h = (x1 - x0) + 4, (y1 - y0) + 4
        M = np.zeros((h * ss, w * ss), np.uint8)
        passo = q["traco_px"] + q["vao_px"]
        for (ax, ay), (bx, by) in (((x0 + r, y0 + r), (x1 - r, y1 - r)), ((x1 - r, y0 + r), (x0 + r, y1 - r))):
            cx, cy = (ax + bx) / 2, (ay + by) / 2
            L = np.hypot(bx - ax, by - ay) / 2
            ux, uy = (bx - ax) / (2 * L), (by - ay) / (2 * L)
            # os traços centrados em 0, ±passo, ±2 passo... (um traço cruza o centro), cortados nas pontas
            kmax = int(np.ceil(L / passo)) + 1
            for kk in range(-kmax, kmax + 1):
                t0 = max(kk * passo - q["traco_px"] / 2, -L)
                t1 = min(kk * passo + q["traco_px"] / 2, L)
                if t1 - t0 < 0.4:
                    continue
                p0 = ((cx + ux * t0 - X0) * ss, (cy + uy * t0 - Y0) * ss)
                p1 = ((cx + ux * t1 - X0) * ss, (cy + uy * t1 - Y0) * ss)
                cv2.line(M, tuple(int(round(v)) for v in p0), tuple(int(round(v)) for v in p1), 255,
                         max(1, int(round(q["x_px"] * ss))), cv2.LINE_AA)
        al = cv2.resize(M.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
        al *= _cobertura((x0, y0, x1, y1), X0, Y0, w, h)
        reg = out[Y0:Y0 + h, X0:X0 + w]
        out[Y0:Y0 + h, X0:X0 + w] = reg * (1 - al[..., None]) + np.float32(q["x"]) * al[..., None]
    print(f"    shafts: {len(q['shafts_px'])} shafts com o fundo branco limpo e o X tracejado redesenhado, fino e "
          f"simétrico; as paredes de {len(q['paredes_px'])} trechos de volta ao desenho do PDF")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 15. As mesinhas redondas da suíte master (usuário, no recorte dos shafts e da poltrona: "melhore a representação da
# mesa redonda, da parede e limpe resíduos da imagem"): o par de mesinhas encaixadas do PDF (a de baixo e a de cima,
# que passa por cima dela) em nogueira, com o veio e o chanfro, a de cima um tom mais clara; a sombra macia no piso e a
# de contato da de cima na de baixo; o contorno fino. Antes, o anel em volta (os restos do render) recebe o vinílico de
# logo ao lado (`_anel`), sem tocar a poltrona. (A parede dos shafts: no passo `shafts`.)
MESINHAS_MASTER_1P = {"mesas_px": [(1629.2, 1405.55, 8.95, (44, 72, 110)), (1631.55, 1393.45, 8.95, (56, 88, 130))],
                      "poltrona_px": (1642, 1370, 1702, 1424), "anel_px": 5, "contorno": (34, 46, 62),
                      "contorno_alfa": 0.6, "semente": 1141}


def mesinhas_master_1p(Q, img, q=None):
    import final3840_casad as D
    import pedidos_terreo_casaa_2910 as P
    q = q or MESINHAS_MASTER_1P
    out = img.copy()
    H, W = out.shape[:2]
    par = FA.paredes_pdf(Q) > 0.3
    rot = _rotulos_mascara(Q, img)
    rng = np.random.default_rng(q["semente"])
    U = np.zeros((H, W), np.uint8)
    for cx, cy, r, _ in q["mesas_px"]:
        cv2.circle(U, (int(round(cx)), int(round(cy))), int(np.ceil(r)), 1, -1)
    proib = par | rot
    a0, b0, a1, b1 = q["poltrona_px"]
    proib[b0:b1, a0:a1] = True
    n = _anel(out, U.astype(bool), q["anel_px"], 3, proib)
    ss, k = 8, Q.px_m
    X0 = int(min(c[0] - c[2] for c in q["mesas_px"])) - 20
    Y0 = int(min(c[1] - c[2] for c in q["mesas_px"])) - 20
    X1 = int(max(c[0] + c[2] for c in q["mesas_px"])) + 20
    Y1 = int(max(c[1] + c[2] for c in q["mesas_px"])) + 20
    w, h = X1 - X0, Y1 - Y0
    Ms = []
    for cx, cy, r, _ in q["mesas_px"]:
        M = np.zeros((h * ss, w * ss), np.uint8)
        cv2.circle(M, (int(round((cx - X0) * ss)), int(round((cy - Y0) * ss))), int(round(r * ss)), 255, -1, cv2.LINE_AA)
        Ms.append(M.astype(np.float32) / 255)
    reds = [cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA) for M in Ms]
    a = np.maximum(*reds)
    luz = np.ones((h, w), np.float32)
    for sd in D.SOMBRA_JOGOS_D:
        dm = np.float32([[1, 0, sd["dx_m"] * k], [0, 1, sd["dy_m"] * k]])
        luz *= 1 - cv2.GaussianBlur(cv2.warpAffine(a, dm, (w, h), flags=cv2.INTER_LINEAR), (0, 0), sd["sig_m"] * k) * sd["forca"]
    livre = (~proib[Y0:Y1, X0:X1]).astype(np.float32)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    reg *= (1 - (1 - luz) * (1 - a) * livre)[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    for i, ((cx, cy, r, tom), M) in enumerate(zip(q["mesas_px"], Ms)):
        if i > 0:                                                   # a de cima faz sombra na de baixo
            sh = cv2.GaussianBlur(cv2.warpAffine(reds[i], np.float32([[1, 0, -1.2], [0, 1, 1.2]]), (w, h)), (0, 0), 1.0)
            reg = out[Y0:Y1, X0:X1].astype(np.float32)
            reg *= (1 - 0.40 * sh * (1 - reds[i]) * reds[0])[..., None]
            out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        out = P._madeira_peca(Q, out, M, X0, Y0, w, h, ss, tom, 0.0, int(rng.integers(1 << 30)), sombra=False)
        borda = np.clip(M - cv2.erode(M, np.ones((5, 5), np.uint8)), 0, 1) * q["contorno_alfa"]
        out = P._pintar(out, X0, Y0, w, h, ss, borda, np.float32(q["contorno"])[None, None] * np.ones_like(borda)[..., None])
    print(f"    mesinhas da suíte master: o par encaixado em nogueira (a de cima mais clara, com a sombra na de baixo), a "
          f"sombra macia e o contorno fino; o anel em volta limpo ({n} px)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 16. O contorno dos armários (usuário, no recorte do closet 2: "melhore o contorno de todos os armarios. revise-os e
# corrija-os"): em volta de cada guarda-roupa (os 4 closets, `CLOSETS_1P`, e o armário do quarto de serviço,
# `final3840_casaa_1pav.ARMARIO`), o anel do render (a faixa escura e as manchas da sombra antiga junto às portas) recebe o
# piso de logo ao lado (`_anel`, sem as paredes e os rótulos); depois, a mesma sombra curta e macia em todos, para o lado
# oposto à luz, e o contorno fino e nítido na borda da peça.
ARMARIOS_1P = {"anel_px": 10, "passo_px": 3, "sombra": 0.20, "sombra_px": (-1.2, 1.2, 1.3), "contorno": (48, 70, 98),
               "contorno_alfa": 0.75, "contorno_px": 0.7}


def armarios_1p(Q, img, q=None):
    q = q or ARMARIOS_1P
    out = img.copy()
    H, W = out.shape[:2]
    par = FA.paredes_pdf(Q) > 0.3
    rot = _rotulos_mascara(Q, img, folga=1)

    def px(r):
        (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        return min(a, c), min(b, d), max(a, c), max(b, d)
    grupos = []
    for nome in [k for k in CLOSETS_1P if k.startswith("closet")]:
        c = CLOSETS_1P[nome]
        grupos.append((nome, [px(r) for r, _ in c["trechos"]] + [px(r) for r in c["cantos"]]))
    grupos.append(("armário do quarto de serviço", [px(P1.ARMARIO["armario"])]))
    n = 0
    for nome, rets in grupos:
        U = np.zeros((H, W), bool)
        for r in rets:
            U[int(np.floor(r[1])):int(np.ceil(r[3])), int(np.floor(r[0])):int(np.ceil(r[2]))] = True
        n += _anel(out, U, q["anel_px"], q["passo_px"], par | rot)
        X0 = int(np.floor(min(r[0] for r in rets))) - 10
        Y0 = int(np.floor(min(r[1] for r in rets))) - 10
        X1 = int(np.ceil(max(r[2] for r in rets))) + 10
        Y1 = int(np.ceil(max(r[3] for r in rets))) + 10
        w, h = X1 - X0, Y1 - Y0
        A = np.zeros((h, w), np.float32)
        Din = np.zeros((h, w), np.float32)
        cp = q["contorno_px"]
        for r in rets:
            A = np.maximum(A, _cobertura(r, X0, Y0, w, h))
        Din = cv2.erode(A, np.ones((3, 3), np.uint8)) if cp >= 1 else None
        dx, dy, sg = q["sombra_px"]
        sb = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h)), (0, 0), sg)
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg *= (1 - q["sombra"] * sb * (1 - A) * (~par[Y0:Y1, X0:X1]))[..., None]
        # o contorno: a borda de dentro da peça, `contorno_px` de largura (a cobertura menos a cobertura encolhida)
        dentro = np.zeros((h, w), np.float32)
        for r in rets:
            dentro = np.maximum(dentro, _cobertura((r[0] + cp, r[1] + cp, r[2] - cp, r[3] - cp), X0, Y0, w, h))
        # a borda só onde a peça encontra o piso (não entre os trechos nem junto à parede)
        borda = np.clip(A - dentro, 0, 1)
        fora = cv2.dilate((A < 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & \
            ~cv2.dilate(par[Y0:Y1, X0:X1].astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        borda *= fora * q["contorno_alfa"]
        reg = reg * (1 - borda[..., None]) + np.float32(q["contorno"]) * borda[..., None]
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        _ = Din
    print(f"    armários: {len(grupos)} guarda-roupas ({', '.join(g for g, _ in grupos)}) com o anel do render limpo "
          f"({n} px), a mesma sombra curta e o contorno fino e nítido")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 17. Os retoques de 11/11 à noite (usuário, com recortes): "corrija o vidro/guardacorpo" (a janela de vidro do PDF entre
# a circulação e o vão da escada, que o render fazia com o caixilho grosso e um montante escuro), "corrija o guarda corpo
# aqui também" (o vidro do vazio da direita, com o tracejado da moldura do vazio por cima), "corrija o piso marmore
# travertino bruto aqui" (a circulação, manchada e lavada junto ao vazio) e "melhore o aspecto dessa poltrona junto a
# escrivaninha e a representação do lapt top" (a suíte 1).
# - os vidros: a faixa de cada um (`vidros_px`, com o lado de cada material) limpa, cada px com o de `passo_px` px para
#   o lado dele (o branco do vazio, o travertino), e o vidro de novo no desenho das regras (`terreo_casaa_1011.
#   vidro_laminas`), fino e contínuo, sem o tracejado e sem o caixilho;
#   as fontes da limpeza fogem das diagonais do X do vazio, que voltam desenhadas na faixa (só elas: a borda do vazio
#   é o próprio guarda-corpo);
# - a circulação: o travertino vem do passo dos pisos (`pisos_1111e`, logo antes);
# - a poltrona da escrivaninha: a antiga sai no passo dos pisos (o vinílico novo por cima, `forcar_px`) e entra a
#   cadeira de madeira e linho da biblioteca (a das mesas de trabalho das outras casas, `final3840_casad.
#   _cadeira_bloco`), virada para a escrivaninha, 1/3 sob o tampo, com a sombra curta do tampo sobre ela;
# - o laptop: as manchas pretas saem (o tampo da escrivaninha de logo ao lado, emendado sem costura) e entra um laptop
#   aberto visto de cima:
#   a base de alumínio com o teclado e o trackpad, a dobradiça escura e a tampa inclinada para trás, com a sombra curta.
RETOQUES_1111E = {
    # (x0, y0, x1, y1) da faixa limpa, eixo do vidro (v/h), o lado "menor" (esquerda/cima) e o "maior"
    "faixas_px": [((2243, 611, 2261, 877), "v"), ((2147, 604, 2160, 882), "v"), ((2027, 601, 2160, 611), "h"),
                  ((2027, 876, 2160, 886), "h")],
    "passo_px": 9,
    "vidros_px": [(2249.0, 612.2, 2250.2, 876.7)],                  # a janela de vidro (px, a linha do meio do PDF)
    "vazio_px": (2027, 603, 2157, 880), "cadeira_velha_px": (2453, 1366, 2503, 1398),
    "laptop_velho_px": (2458, 1337, 2501, 1366), "mesa_px": (2363.4, 1332.5, 2512.6, 1368.4),
    "laptop_px": (2467.0, 1344.5, 2488.0, 1358.5), "tampa_px": 4.0,
    "aluminio": (196, 197, 199), "teclado": (74, 74, 78), "semente": 1151}


def retoques_1111e(Q, img, q=None):
    import final3840_casad as D
    import pedidos_terreo_casaa_2910 as P
    q = q or RETOQUES_1111E
    out = img.copy()
    H, W = out.shape[:2]
    par = FA.paredes_pdf(Q) > 0.3
    ss, k = 8, Q.px_m
    vx0, vy0, vx1, vy1 = q["vazio_px"]
    # 1. os vidros: a faixa limpa, cada lado com o material dele, e o vidro de novo
    passo = q["passo_px"]
    fonte = out.copy()
    # as diagonais do X do vazio (as fontes da limpeza fogem delas; voltam desenhadas depois)
    segs = []
    for _, _, ss_ in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"], min_n=2, min_ext=20):
        for s in ss_:
            u, v = Q.p2q((s[0] + s[2]) / 2, (s[1] + s[3]) / 2)
            if vx0 - 4 <= u <= vx1 + 4 and vy0 - 4 <= v <= vy1 + 4 and min(abs(s[2] - s[0]), abs(s[3] - s[1])) > 0.3:
                segs.append(s)
    linha = np.zeros((H, W), np.uint8)
    for s in segs:
        (a_, b_), (c_, d_) = Q.p2q(s[0], s[1]), Q.p2q(s[2], s[3])
        cv2.line(linha, (int(round(a_)), int(round(b_))), (int(round(c_)), int(round(d_))), 1, 5)
    evitar = par | (linha > 0)
    for (x0, y0, x1, y1), eixo in q["faixas_px"]:
        if eixo == "v":
            meio = (x0 + x1) / 2
            for y in range(y0, y1):
                for x in range(x0, x1):
                    if par[y, x]:
                        continue
                    sx = x - passo if x < meio else x + passo
                    while 0 < sx < W - 1 and evitar[y, sx]:
                        sx += -1 if x < meio else 1
                    out[y, x] = fonte[y, sx]
        else:
            meio = (y0 + y1) / 2
            for y in range(y0, y1):
                for x in range(x0, x1):
                    if par[y, x]:
                        continue
                    sy = y - passo if y < meio else y + passo
                    while 0 < sy < H - 1 and evitar[sy, x]:
                        sy += -1 if y < meio else 1
                    out[y, x] = fonte[sy, x]
    # o X tracejado do vazio de volta onde a faixa foi limpa (só as diagonais: a borda é o próprio guarda-corpo)
    faixa = np.zeros((H, W), np.float32)
    for (x0, y0, x1, y1), _ in q["faixas_px"]:
        faixa[y0:y1, x0:x1] = 1.0
    fq = TA.FINOS_TA
    pq = dict(T.PROJ, larg_px=fq["larg_px"], preto=fq["escuro"], branco=fq["claro"], limiar=fq["limiar"])
    xis, _ = T.preto_branco(Q, out, segs, pq)
    faixa = (faixa * (1 - par))[..., None]
    out = np.clip(np.round(xis * faixa + out * (1 - faixa)), 0, 255).astype(np.uint8)
    vidros = list(VAZIOS_1P["guarda_corpo_pt"])
    for x0, y0, x1, y1 in q["vidros_px"]:
        (a_, b_), (c_, d_) = Q.q2p(x0, y0), Q.q2p(x1, y1)
        vidros.append((min(a_, c_), min(b_, d_), max(a_, c_), max(b_, d_)))
    out = np.clip(np.round(TA.vidro_laminas(Q, out, vidros, TA.ESCADAS_TA["jardim"]["vidro"])), 0, 255).astype(np.uint8)
    # 2. o laptop antigo sai: o tampo de logo ao lado, emendado sem costura (Poisson)
    l0, m0, l1, m1 = q["laptop_velho_px"]
    dl = l1 - l0 + 6
    rem = out[m0 - 2:m1 + 2, l0 - dl - 2:l1 - dl + 2].copy()
    msk = np.full(rem.shape[:2], 255, np.uint8)
    msk[:2], msk[-2:], msk[:, :2], msk[:, -2:] = 0, 0, 0, 0
    out = cv2.seamlessClone(rem, out, msk, ((l0 + l1) // 2, (m0 + m1) // 2), cv2.NORMAL_CLONE)
    # 3. a cadeira nova: a de madeira e linho da biblioteca (`final3840_casad._cadeira_bloco`, a das mesas de trabalho
    # das outras casas), virada para a escrivaninha, 1/3 sob o tampo, e a sombra curta do tampo sobre ela
    mx0, my0, mx1, my1 = q["mesa_px"]
    X0, Y0 = int(np.floor(mx0)), int(np.floor(my0))
    mesa_a = np.zeros((H, W), np.float32)
    mesa_a[Y0:int(np.ceil(my1)), X0:int(np.ceil(mx1))] = _cobertura((mx0, my0, mx1, my1), X0, Y0,
                                                                     int(np.ceil(mx1)) - X0, int(np.ceil(my1)) - Y0)
    qc = D.MOVEIS_TD["cadeira"]
    D_px = qc["m"] * k
    ccx = (q["cadeira_velha_px"][0] + q["cadeira_velha_px"][2]) / 2
    ccy = my1 + D_px * (0.5 - qc["sob"])
    cor, a = D._cadeira_bloco(Q, (0, -1), contorno=qc["contorno"])
    outf = out.astype(np.float32)
    D._pousar(outf, cor, a, ccx, ccy, k, cobre=mesa_a)
    s_ = D.F.PECAS["sombra"]
    d_ = s_["dist_m"] * k
    sb = cv2.GaussianBlur(cv2.warpAffine(mesa_a, np.float32([[1, 0, -d_], [0, 1, d_]]), (W, H)), (0, 0),
                          s_["sig_m"] * k) * s_["forca"]
    cad_a = np.zeros((H, W), np.float32)
    h_, w_ = a.shape
    cad_a[int(ccy - h_ / 2):int(ccy - h_ / 2) + h_, int(ccx - w_ / 2):int(ccx - w_ / 2) + w_] = a
    outf *= (1 - sb * np.clip(cad_a, 0, 1) * (1 - mesa_a))[..., None]
    out = np.clip(np.round(outf), 0, 255).astype(np.uint8)
    # 4. o laptop: a sombra curta, a tampa inclinada, a dobradiça, a base com o teclado e o trackpad
    lx0, ly0, lx1, ly1 = q["laptop_px"]
    tp = q["tampa_px"]
    X0, Y0 = int(lx0) - 6, int(ly0 - tp) - 6
    w, h = int(lx1) - X0 + 7, int(ly1) - Y0 + 7
    base = P._ret_arred((lx0, ly0, lx1, ly1), 1.0, X0, Y0, h, w, ss)
    tampa = P._ret_arred((lx0 + 0.3, ly0 - tp, lx1 - 0.3, ly0 + 0.4), 0.8, X0, Y0, h, w, ss)
    tudo = np.maximum(base, tampa)
    a = cv2.resize(tudo, (w, h), interpolation=cv2.INTER_AREA)
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -0.9], [0, 1, 1.0]]), (w, h)), (0, 0), 1.0)
    reg = out[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    reg *= (1 - 0.35 * sb * (1 - a))[..., None]
    out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    py = (yy + 0.5) / ss + Y0
    px_ = (xx + 0.5) / ss + X0
    alu = np.float32(q["aluminio"])
    # a tampa: o alumínio mais escuro, mais ainda junto à dobradiça
    ft = 0.80 + 0.10 * np.clip((ly0 - py) / tp, 0, 1)
    out = P._pintar(out, X0, Y0, w, h, ss, tampa, alu[None, None] * ft[..., None])
    fb = 1.0 - 0.06 * np.clip((py - ly0) / (ly1 - ly0), 0, 1)
    out = P._pintar(out, X0, Y0, w, h, ss, base, alu[None, None] * fb[..., None])
    # o teclado: as teclas escuras numa grade, a moldura do alumínio em volta
    kx0, kx1, ky0, ky1 = lx0 + 1.6, lx1 - 1.6, ly0 + 1.4, ly0 + (ly1 - ly0) * 0.56
    tec = ((px_ > kx0) & (px_ < kx1) & (py > ky0) & (py < ky1)).astype(np.float32)
    gx = np.mod((px_ - kx0) / ((kx1 - kx0) / 13), 1.0)
    gy = np.mod((py - ky0) / ((ky1 - ky0) / 5), 1.0)
    vao = ((gx < 0.16) | (gy < 0.18)).astype(np.float32)
    cor_t = np.float32(q["teclado"])[None, None] * (1 + 0.9 * vao)[..., None]
    out = P._pintar(out, X0, Y0, w, h, ss, tec * base, cor_t)
    # o trackpad, mais claro, no meio da frente
    tcx = (lx0 + lx1) / 2
    tpad = ((np.abs(px_ - tcx) < (lx1 - lx0) * 0.17) & (py > ky1 + 1.0) & (py < ly1 - 1.0)).astype(np.float32)
    out = P._pintar(out, X0, Y0, w, h, ss, tpad * base, (alu * 1.06)[None, None] * np.ones_like(tpad)[..., None])
    # a dobradiça e o contorno fino
    dob = (np.abs(py - ly0) < 0.45).astype(np.float32) * base
    out = P._pintar(out, X0, Y0, w, h, ss, dob, np.float32((52, 52, 56))[None, None] * np.ones_like(dob)[..., None])
    borda = np.clip(tudo - cv2.erode(tudo, np.ones((4, 4), np.uint8)), 0, 1) * 0.6
    out = P._pintar(out, X0, Y0, w, h, ss, borda, np.float32((96, 96, 100))[None, None] * np.ones_like(borda)[..., None])
    print("    retoques de 11/11 (noite): a janela de vidro da circulação e o guarda-corpo do vazio finos e limpos (o X "
          "do vazio redesenhado), a cadeira de madeira e linho da biblioteca e o laptop aberto na escrivaninha da "
          "suíte 1")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 18. Os pisos de vinílico e de travertino bruto (usuário, 11/11 à noite: "melhore o aspecto do piso vinílico e do
# marmore travertino bruto. sem mexer nos demais pisos"; "traga mais realismo, mantendo-os novos e limpos"). Só nas
# áreas desses dois materiais na base chapada (o vinílico das suítes e dos closets; o travertino bruto da circulação,
# da sala íntima e dos banhos), e só no que é piso: fora as peças do PDF (layout, louças, bancadas, elementos fixos e
# escadas, cheias por dentro, com `pdf_folga_px`), as paredes e o que foge do tom do piso do lugar (a luz larga do
# próprio piso, `final3840_casab.luz_robusta`); a sombra dos móveis (o px mais escuro no mesmo matiz, perto das peças)
# fica, como fator. Os rótulos saem antes (`ampliacao_a3_casaa.tirar`) e voltam desenhados por cima no fim.
# - vinílico: réguas de 20 cm, de 1,1 a 1,8 m, em fiadas com as juntas desencontradas, na direção das tábuas do render
#   (`direcao`: "h", as fiadas deitadas, como em todos os ambientes do render, inclusive as faixas estreitas dos vãos
#   das portas; "auto" pega a de mais contraste), cada régua num tom (alternado, sutil) e com o veio da madeira no comprido (o veio largo e os
#   fios finos), a junta fina e escura entre as fiadas, com o bisel claro logo abaixo, e a junta de topo; desenhado em
#   4x e reduzido (juntas nítidas);
# - travertino bruto: a foto da biblioteca (`final3840_casaa.travertino_bruto`, os veios na horizontal e os poros),
#   mais suave e sem manchas, sem rejuntes (como no Térreo);
# - a luz: a do lugar (raio `luz_m`), achatada em `plano` para o tom mediano de cada ambiente (novo e limpo).
PISOS_1111E = {
    "vinilico": {"chapada": (79, 120, 168), "regua_m": 0.20, "comprimento_m": (1.1, 1.8), "tom": 0.035,
                 "matiz": 0.012, "veio": 0.035, "veio_fino": 0.06, "junta": 0.74, "junta_px": 0.55, "bisel": 0.030,
                 "topo": 0.86, "direcao": "h", "semente": 1112,
                 # usuário (11/11, com a foto de um vinílico de carvalho claro): "vamos trazer esse piso vinílico em sua
                 # respectiva escala para os ambientes que possuem piso vinílico. vamos testar e se der certo adotaremos
                 # para todas as outras plantas" -> as réguas da própria foto (`_reguas_amostra`); vendo o teste (20 cm):
                 # "sim, aplique em todas as plantas com vinílico, mas com uma escala mais reduzida" -> 12 cm
                 # (`regua_m` abaixo, o mesmo de `vinilico_foto.VINILICO_FOTO`)
                 "regua_foto_m": 0.12,
                 "amostra": {"arquivo": "_texturas/originais/amostra_vinilico_carvalho_1111.png", "fiada_px": 20.8,
                             "fase_px": 7.0, "apara_px": 1.5, "junta_min": 3.0, "janela_px": 5, "peca_min_px": 18,
                             "sem_repetir": 6,
                             # os vãos das portas (na chapada, preto) com o vinílico do render (entre a folha de correr
                             # e a cortina): a cor do vinílico antigo, até `vao_px` do ambiente, ligados a ele
                             "vao_px": 30, "vao_croma": 0.035, "vao_r": (0.75, 1.25)}},
    "travertino": {"chapada": (202, 217, 220), "forca": 1.1, "veio": 0.012, "faixa": 0.022, "poros": 8,
                   "poro_esc": 0.07, "semente": 1113},
    "camadas_pdf": ("ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_LOUÇAS E METAIS", "ARQ_BANCADAS", "ARQ_ELEMENTOS FIXOS",
                    "ARQ_ESCADAS E RAMPAS"),
    "pdf_folga_px": 1, "desvio": 30, "croma": 0.030, "sombra_min": 0.70, "perto_m": 0.40, "luz_m": 0.9,
    "plano": 0.6, "forcar_px": [(2453, 1370, 2503, 1398)]}


def _reguas_1111e(h, w, px_m, q, rng):
    """O desenho do vinílico (média ~1, BGR), h x w px, em fiadas horizontais: 4x e reduzido."""
    k = 4
    Hk, Wk = h * k, w * k
    larg = q["regua_m"] * px_m * k
    D = np.ones((Hk, Wk, 3), np.float32)
    jl = max(1, int(round(q["junta_px"] * k)))
    y = -rng.uniform(0, larg)
    while y < Hk:
        b0, b1 = int(round(y)), int(round(y + larg))
        x = -rng.uniform(0, q["comprimento_m"][1] * px_m * k)
        while x < Wk:
            comp = rng.uniform(*q["comprimento_m"]) * px_m * k
            a0, a1 = int(round(x)), int(round(x + comp))
            hh, ww = b1 - b0, a1 - a0
            n1 = cv2.GaussianBlur(rng.normal(0, 1, (hh, ww)).astype(np.float32), (0, 0),
                                  sigmaX=0.30 * px_m * k, sigmaY=0.006 * px_m * k)
            n2 = cv2.GaussianBlur(rng.normal(0, 1, (hh, ww)).astype(np.float32), (0, 0),
                                  sigmaX=0.08 * px_m * k, sigmaY=0.0018 * px_m * k)
            n1 /= max(float(n1.std()), 1e-6)
            n2 /= max(float(n2.std()), 1e-6)
            tom = 1 + rng.choice((-1, 1)) * rng.uniform(0.3, 1.0) * q["tom"]
            u = rng.normal(0, 1)
            matiz = np.float32([1 - q["matiz"] * u, 1, 1 + q["matiz"] * u])
            f = tom * (1 + q["veio"] * n1 - q["veio_fino"] * np.maximum(n2, 0))
            pedaco = f[..., None] * matiz[None, None]
            c0, c1 = max(a0, 0), min(a1, Wk)
            r0, r1 = max(b0, 0), min(b1, Hk)
            if c1 > c0 and r1 > r0:
                D[r0:r1, c0:c1] = pedaco[r0 - b0:r1 - b0, c0 - a0:c1 - a0]
                if 0 <= a0 < Wk:                                             # a junta de topo
                    D[r0:r1, a0:min(a0 + jl, Wk)] *= q["topo"]
            x += comp
        if 0 <= b0 < Hk:                                                     # a junta entre as fiadas e o bisel
            D[b0:min(b0 + jl, Hk)] *= q["junta"]
            D[min(b0 + jl, Hk):min(b0 + 2 * jl, Hk)] *= 1 + q["bisel"]
        y += larg
    return cv2.resize(D, (w, h), interpolation=cv2.INTER_AREA)


_PECAS_AMOSTRA = {}


def _pecas_amostra(qa):
    """As réguas inteiras da foto (de junta de topo a junta de topo, em cada fiada), em pé (o comprimento em y), BGR."""
    from scipy.signal import find_peaks
    if qa["arquivo"] in _PECAS_AMOSTRA:
        return _PECAS_AMOSTRA[qa["arquivo"]]
    a = cv2.imread(str(TA.RAIZ / qa["arquivo"])).astype(np.float32)
    Ha, Wa = a.shape[:2]
    w, ph, ap = qa["fiada_px"], qa["fase_px"], qa["apara_px"]
    n = int(round(w))
    pecas = []
    k = 0
    while ph + (k + 1) * w <= Wa:
        c0 = ph + k * w
        xs = np.linspace(c0 + ap, c0 + w - ap, n).astype(np.float32)
        mx = np.repeat(xs[None], Ha, axis=0)
        my = np.repeat(np.arange(Ha, dtype=np.float32)[:, None], n, axis=1)
        fiada = cv2.remap(a, mx, my, cv2.INTER_LINEAR)
        m = fiada.mean(axis=(1, 2))
        j = qa["janela_px"]
        d = np.zeros(Ha, np.float32)
        for y in range(j, Ha - j + 1):
            d[y] = abs(m[y - j:y].mean() - m[y:y + j].mean())
        juntas, _ = find_peaks(d, height=qa["junta_min"], distance=10)
        for y0, y1 in zip(juntas[:-1], juntas[1:]):
            if y1 - y0 >= qa["peca_min_px"]:
                pecas.append(fiada[y0 + 1:y1 - 1])
        k += 1
    _PECAS_AMOSTRA[qa["arquivo"]] = pecas
    return pecas


def _reguas_amostra(h, w, px_m, q, rng):
    """O vinílico da foto (cor da foto, BGR), h x w px, em fiadas horizontais de `regua_m`: cada fiada com réguas
    inteiras da foto, sorteadas (sem repetir as últimas `sem_repetir`, às vezes giradas 180°) e emendadas junta a junta;
    a escala: a largura da régua da foto vira `regua_m`. Em 4x e reduzido."""
    qa = q["amostra"]
    pecas = _pecas_amostra(qa)
    k = 4
    Hk, Wk = h * k, w * k
    larg = q.get("regua_foto_m", q["regua_m"]) * px_m * k
    D = np.zeros((Hk, Wk, 3), np.float32)
    ult = []
    y = -rng.uniform(0, larg)
    while y < Hk:
        b0, b1 = int(round(y)), int(round(y + larg))
        hh = b1 - b0
        x = -rng.uniform(0, 1.2 * px_m * k)
        while x < Wk:
            i = int(rng.integers(len(pecas)))
            while i in ult:
                i = int(rng.integers(len(pecas)))
            ult = (ult + [i])[-qa["sem_repetir"]:]
            P = pecas[i]
            if rng.random() < 0.5:
                P = P[::-1, ::-1]
            comp = int(round(P.shape[0] * hh / P.shape[1]))
            pedaco = cv2.resize(np.ascontiguousarray(P.transpose(1, 0, 2)), (comp, hh), interpolation=cv2.INTER_CUBIC)
            a0 = int(round(x))
            c0, c1 = max(a0, 0), min(a0 + comp, Wk)
            r0, r1 = max(b0, 0), min(b1, Hk)
            if c1 > c0 and r1 > r0:
                D[r0:r1, c0:c1] = pedaco[r0 - b0:r1 - b0, c0 - a0:c1 - a0]
            x = a0 + comp
        y += larg
    return cv2.resize(D, (w, h), interpolation=cv2.INTER_AREA)


def _objetos_pdf(Q, camadas, folga):
    """As peças do PDF (as camadas dadas), cheias por dentro e com `folga` px."""
    from scipy import ndimage as nd
    linhas = np.zeros((Q.H, Q.W), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in camadas:
            for c in Q.caminhos(d):
                if len(c) >= 2:
                    if d["type"] in ("f", "fs") and len(c) >= 3:
                        cv2.fillPoly(linhas, [np.int32(np.round(c))], 1)
                    cv2.polylines(linhas, [np.int32(np.round(c))], False, 1, 2)
    return dilatar(nd.binary_fill_holes(linhas > 0), folga)


def pisos_1111e(Q, img, q=None):
    import final3840_casab as F
    import ampliacao_a3_casaa as AM
    import ampliacao_12k_terreo_casaa as Z
    q = q or PISOS_1111E
    H, W = img.shape[:2]
    k = Q.px_m
    # os rótulos saem (voltam no fim)
    with contextlib.redirect_stdout(io.StringIO()):
        rots = Z.rotulos(Q, img)
    camadas = [(Z.alfa_rotulo(Q, b_, (H, W)), tuple(b_["cor"])) for b_ in rots]
    base = AM.tirar(img, camadas, 0.85)
    I = base.astype(np.float32)
    par = dilatar(FA.paredes_pdf(Q) > 0.3, 1)
    pdf = _objetos_pdf(Q, q["camadas_pdf"], q["pdf_folga_px"])
    forcar = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in q["forcar_px"]:
        forcar[y0:y1, x0:x1] = True
    pdf &= ~forcar
    out = I.copy()
    feitos, rotulo_ok = {}, np.zeros((H, W), bool)
    for nome in ("vinilico", "travertino"):
        qm = q[nome]
        mat = (Q.chapada == qm["chapada"]).all(axis=2)
        mat = cv2.morphologyEx(mat.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
        mat &= ~par
        if nome == "vinilico" and "amostra" in qm:
            qa = qm["amostra"]
            ref = np.median(I[mat & ~pdf], axis=0)
            nI = I / np.maximum(I.sum(axis=2, keepdims=True), 1)
            rv = I.mean(axis=2) / max(float(ref.mean()), 1.0)
            cand = dilatar(mat, qa["vao_px"]) & ~mat & ~par & (Q.chapada == 0).all(axis=2)
            cand &= (np.abs(nI - ref / ref.sum()).max(axis=2) < qa["vao_croma"]) & (rv > qa["vao_r"][0]) & \
                (rv < qa["vao_r"][1])
            ligado = ndimage.binary_propagation(mat, mask=mat | cand)
            mat |= cand & ligado
        L = F.luz_robusta(base, mat & ~pdf, 0.5 * k, desvio=q["desvio"])
        n = I / np.maximum(I.sum(axis=2, keepdims=True), 1)
        nL = L / np.maximum(L.sum(axis=2, keepdims=True), 1)
        err = np.abs(n - nL).max(axis=2)
        r = cv2.GaussianBlur(I.mean(axis=2), (0, 0), 0.8) / np.maximum(L.mean(axis=2), 1)
        dev = np.abs(I - L).max(axis=2)
        piso = mat & ~pdf & (err < q["croma"]) & ((dev < q["desvio"]) | ((r > q["sombra_min"]) & (r < 1.0)))
        piso |= mat & forcar
        if nome == "vinilico" and "amostra" in qm:      # os fiapos do piso antigo (veios claros de 1 px) entram
            nb, labb, stb, _ = cv2.connectedComponentsWithStats((mat & ~pdf & ~piso).astype(np.uint8), 8)
            peq = np.zeros(nb, bool)
            peq[1:] = stb[1:, cv2.CC_STAT_AREA] <= 60
            piso |= peq[labb]
        # cada ambiente (componente) com a sua luz achatada e a direção das tábuas
        nc, lab, st, _ = cv2.connectedComponentsWithStats(mat.astype(np.uint8), 8)
        perto = cv2.GaussianBlur(dilatar(mat & ~piso, int(round(q["perto_m"] * k))).astype(np.float32), (0, 0), 3.0)
        S = np.where(r < 0.985, np.clip(r / 0.985, q["sombra_min"] * 0.8, 1.0), 1.0)
        S = 1 - (1 - S) * perto
        Lg = F.luz_robusta(base, piso, q["luz_m"] * k, desvio=q["desvio"])
        rng = np.random.default_rng(qm["semente"])
        cont = 0
        for i in range(1, nc):
            x, y, w, h, a = st[i]
            if a < 400:
                continue
            m = (lab[y:y + h, x:x + w] == i) & piso[y:y + h, x:x + w]
            if m.sum() < 200:
                continue
            med = np.median(Lg[y:y + h, x:x + w][m], axis=0)
            Lr = Lg[y:y + h, x:x + w] * (1 - q["plano"]) + med[None, None] * q["plano"]
            if nome == "vinilico":
                deitado = qm["direcao"] == "h"
                if qm["direcao"] == "auto":
                    g = cv2.cvtColor(img[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY).astype(np.float32)
                    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
                    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
                    deitado = float((gy[m] ** 2).sum()) >= float((gx[m] ** 2).sum())
                gerar = _reguas_amostra if "amostra" in qm else _reguas_1111e
                if deitado:
                    T = gerar(h, w, k, qm, rng)
                else:
                    T = np.ascontiguousarray(gerar(w, h, k, qm, rng).transpose(1, 0, 2))
            else:
                T = FA.travertino_bruto(Q, h, w, qm["semente"] + i, qm["veio"], qm["faixa"], qm["poros"],
                                        qm["poro_esc"], forca=qm["forca"])[..., None]
            if nome == "vinilico" and "amostra" in qm:      # a cor é a da foto; do lugar, só a luz (relativa)
                novo = T * (Lr.mean(axis=2, keepdims=True) / max(float(med.mean()), 1.0)) * S[y:y + h, x:x + w, None]
            else:
                novo = Lr * T * S[y:y + h, x:x + w, None]
            al = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5) * m
            reg = out[y:y + h, x:x + w]
            reg[:] = reg * (1 - al[..., None]) + novo * al[..., None]
            rotulo_ok[y:y + h, x:x + w] |= m
            cont += 1
        feitos[nome] = (cont, int(piso.sum()))
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    # os rótulos de volta: os que caem nos pisos refeitos, desenhados por cima; os outros, como estavam
    volta = [(a, c) for a, c in camadas if (rotulo_ok & (a > 0.02)).any()]
    fora = np.zeros((H, W), bool)
    for a, c in camadas:
        if not (rotulo_ok & (a > 0.02)).any():
            fora |= dilatar(a > 0.002, 2)
    out = AM.pintar(out, volta)
    out[fora] = img[fora]
    vin = (f"réguas da foto do carvalho claro, {q['vinilico'].get('regua_foto_m', 0.2) * 100:.0f} cm cada, emendadas junta a junta"
           if "amostra" in q["vinilico"]
           else "réguas de 20 cm com juntas finas, bisel e veio")
    print(f"    pisos: vinílico em {feitos['vinilico'][0]} ambientes ({feitos['vinilico'][1]} px), {vin}; travertino bruto em {feitos['travertino'][0]} ambientes "
          f"({feitos['travertino'][1]} px), sem manchas e sem rejuntes; {len(volta)} rótulos redesenhados por cima")
    return out


# 19. Os degraus da escada em U no mesmo travertino dos pisos (usuário, 11/11 à noite: "sim, aplique o mesmo acabamento
# nos degraus da escada em U"): só a parte do 1º Pavimento (os degraus coloridos dos dois lanços e o patamar; os do
# Térreo, enevoados, ficam), só no que é pedra: fora as linhas dos espelhos, a linha de corte, o guarda-corpo, o
# triângulo e o texto (o que foge do tom da pedra, com `folga_px`). Cada degrau (e o patamar) é uma peça: o
# travertino de `pisos_1111e` (os estratos e os poros, sem manchas), com o veio no comprimento da peça e uma semente
# por peça (pela posição), num tom só para a escada inteira (a luz larga da pedra, achatada em `plano`; usuário, vendo
# a 1ª versão, com as peças em tons diferentes).
DEGRAUS_1111E = {"caixa_px": (2250, 888, 2490, 1108), "desvio": 22, "croma": 0.03, "claro_max": 232,
                 "folga_px": 1, "mediana_px": 7, "linha": 14, "escuro": 110, "poro_max": (30, 7), "quente_min": 12,
                 "luz_m": 0.6,
                 "plano": 1.0,
                 "area_min": 80, "lado_min": 5, "semente": 1119}


def degraus_1111e(Q, img, q=None):
    import final3840_casab as F
    q = q or DEGRAUS_1111E
    qt = PISOS_1111E["travertino"]
    out = img.astype(np.float32)
    H, W = img.shape[:2]
    x0, y0, x1, y1 = q["caixa_px"]
    caixa = np.zeros((H, W), bool)
    caixa[y0:y1, x0:x1] = True
    par = dilatar(FA.paredes_pdf(Q) > 0.3, 1)
    mat = caixa & (Q.chapada == qt["chapada"]).all(axis=2) & ~par
    I = out
    lum = I.mean(axis=2)
    pedra = mat & (lum < q["claro_max"])
    L = F.luz_robusta(img, pedra, 0.4 * Q.px_m, desvio=q["desvio"])
    n = I / np.maximum(I.sum(axis=2, keepdims=True), 1)
    nL = L / np.maximum(L.sum(axis=2, keepdims=True), 1)
    # é pedra o que tem o matiz dela (os degraus mais escuros do render entram); as linhas finas (os espelhos, a linha
    # de corte, o texto, o triângulo: mais escuras que a mediana de perto) e os guarda-corpos ficam
    lm = cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), q["mediana_px"]).astype(np.float32)
    finas = (lum < lm - q["linha"]) & caixa
    # os poros do desenho antigo (manchas pequenas, sem comprimento) não são linhas: entram na pedra
    nl, ll, sl, _ = cv2.connectedComponentsWithStats(finas.astype(np.uint8), 8)
    poro = np.zeros(nl, bool)
    poro[1:] = (sl[1:, 4] <= q["poro_max"][0]) & (np.maximum(sl[1:, 2], sl[1:, 3]) <= q["poro_max"][1])
    finas &= ~poro[ll]
    linhas = dilatar(finas | (lum < q["escuro"]), q["folga_px"])
    gc = np.zeros((H, W), np.uint8)
    for r_ in ESCADAS_1P["u"]["guarda_corpo_pt"]:
        (ga, gb), (gc_, gd) = Q.p2q(r_[0], r_[1]), Q.p2q(r_[2], r_[3])
        cv2.rectangle(gc, (int(min(ga, gc_)) - 2, int(min(gb, gd)) - 2), (int(max(ga, gc_)) + 2, int(max(gb, gd)) + 2), 1, -1)
    quente = (I[..., 2] - I[..., 0]) >= q["quente_min"]           # a pedra é quente; o Térreo enevoado, cinza
    ok = pedra & quente & (np.abs(n - nL).max(axis=2) < q["croma"]) & ~linhas & (gc == 0)
    nc, lab, st, _ = cv2.connectedComponentsWithStats(ok.astype(np.uint8), 4)
    # um tom só para a escada: a luz larga da pedra, achatada em `plano` para a mediana
    Lg = F.luz_robusta(img, ok, q["luz_m"] * Q.px_m, desvio=q["desvio"])
    med = np.median(I[ok], axis=0)
    Lg = Lg * (1 - q["plano"]) + med[None, None] * q["plano"]
    pecas = 0
    for i in range(1, nc):
        x, y, w, h, a = st[i]
        if a < q["area_min"] or min(w, h) < q["lado_min"]:
            continue
        m = lab[y:y + h, x:x + w] == i
        Lp = Lg[y:y + h, x:x + w]
        sem = q["semente"] + 7 * int(x) + 13 * int(y)
        if h >= w:
            T = FA.travertino_bruto(Q, w, h, sem, qt["veio"], qt["faixa"], qt["poros"], qt["poro_esc"],
                                    forca=qt["forca"]).T[..., None]
        else:
            T = FA.travertino_bruto(Q, h, w, sem, qt["veio"], qt["faixa"], qt["poros"], qt["poro_esc"],
                                    forca=qt["forca"])[..., None]
        T = T / max(float(T[m].mean()), 1e-3)                 # cada peça na média 1 (a foto varia de um trecho a outro)
        al = (cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5) * m)[..., None]
        reg = out[y:y + h, x:x + w]
        reg[:] = reg * (1 - al) + Lp * T * al
        pecas += 1
    print(f"    degraus da escada em U: {pecas} peças (os degraus coloridos e o patamar) no travertino dos pisos, com o "
          f"veio no comprimento; os enevoados, as linhas, o guarda-corpo, o triângulo e o texto ficam")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 20. Os retoques de 11/11, mais tarde (usuário, com recortes):
# - "a sombra de descida para esquerda não ficou bom. até acho que está ao contrário. corrija" (a caracol): o D do PDF
#   fica no degrau junto aos 0°, onde a descida começa, e ela segue no sentido anti-horário (para a esquerda, para o
#   trecho do Térreo); os cinco degraus do 1º Pavimento passam a escurecer nesse sentido (o junto aos 0°, o mais alto,
#   no tom cheio; o junto aos 93,1°, `tons`[0]), com a sombra curta do espelho do degrau de cima (o do lado dos 0°) no
#   de baixo. A conta é a razão entre o fator novo e o de `final3840_casaa_1pav.caracol` (o tom de cada degrau e a
#   sombra do espelho), em 4x, só no trecho cheio, fora das guardas, do anel, do pilar e do triângulo. O triângulo vira
#   para o mesmo sentido (`ESCADAS_1P["caracol"]["sentido"]`);
# - "revise portas e remova os arcos de movimento delas" e "essa porta precisa ser representada novamente" (a da suíte
#   3, cuja folha tinha sumido no vinílico): as 11 folhas de giro (`folhas_px`, os retângulos brancos da ARQ_PAREDE do
#   PDF, abertas junto à parede) redesenhadas no mesmo desenho: o piso de baixo limpo (o de `desloc_px` px para o lado
#   de fora da parede, numa régua do vinílico), a folha fina em madeira clara com o veio no comprido, o contorno e a
#   sombra curta; sem arco nenhum (os arcos do PDF não entram; no 12K, voltam da final, `pecas`);
# - "melhore a representação dessas portas de vidro e remova os resíduos existentes" (a janela de correr da saleta,
#   junto à caracol): o vão limpo (a soleira em travertino, `saleta`), as faces da parede em linha fina, os batentes em
#   alumínio e as duas folhas de correr do PDF, desencontradas, cada uma no perfil de alumínio com o vidro no desenho
#   das regras (`terreo_casaa_1011.vidro_laminas`);
# - "faltou a representação dessa cadeira de escritório" (a escrivaninha da suíte 3): o semicírculo branco do render
#   sai (o vinílico da mesma fiada, `cadeira_velha_px`) e entra a cadeira de madeira e linho da biblioteca, virada
#   para a mesa (para baixo), 1/3 sob o tampo, com a sombra curta dele (como a da suíte 1).
RETOQUES_1111F = {
    "caracol": {"tons": (0.84, 1.0), "escuro_max": 90, "ss": 4},
    "folhas_px": [(2426.1, 1312.2, 2479.8, 1314.6), (2107.2, 1332.5, 2109.6, 1386.3),
                  (2172.3, 1332.5, 2174.7, 1386.3), (2058.8, 479.3, 2112.6, 481.7), (1972.3, 586.8, 2026.0, 589.2),
                  (1748.4, 986.8, 1802.1, 989.2), (1972.9, 1153.4, 1975.2, 1207.2), (1849.9, 1225.1, 1903.6, 1227.5),
                  (2107.2, 1434.1, 2109.6, 1487.8), (1682.7, 1472.9, 1736.4, 1475.2), (2163.3, 1560.0, 2205.1, 1562.4)],
    "folha": {"madeira": (134, 166, 202), "contorno": (58, 72, 92), "contorno_alfa": 0.95, "veio": 0.05,
              "raio_px": 0.5, "sombra": 0.28, "sombra_px": (-0.8, 1.0, 0.9), "limpa_px": 3, "desloc_px": 12},
    "saleta": {"vao_px": (1912.6, 1629.9, 2136.5, 1644.2), "soleira": (200, 210, 220),
               "faces": (135, 135, 138), "batentes_px": [(1912.6, 1631.1, 1914.9, 1643.0),
                                                        (2134.1, 1631.1, 2136.5, 1643.0)],
               "folhas_px": [((1914.9, 1640.0, 2026.9, 1643.0), (1919.7, 2022.1)),
                             ((2022.1, 1637.1, 2134.1, 1640.0), (2026.9, 2129.3))],
               "aluminio": (178, 181, 186), "aluminio_contorno": (118, 120, 126)},
    "cadeira_s3": {"mesa_px": (1624.3, 562.3, 1781.2, 598.1), "ccx": 1664.8, "frente": (0, 1),
                   "cadeira_velha_px": (1644, 534, 1687, 563), "desloc_px": 46},
    "semente": 1161}


def _cadeira_mesa(Q, out, mesa_px, ccx, frente):
    """A cadeira de madeira e linho da biblioteca (`final3840_casad._cadeira_bloco`) virada para a mesa (`frente`), 1/3
    sob o tampo, e a sombra curta do tampo sobre ela; `out` em float32, mudado no lugar."""
    import final3840_casad as D
    H, W = out.shape[:2]
    k = Q.px_m
    mx0, my0, mx1, my1 = mesa_px
    X0, Y0 = int(np.floor(mx0)), int(np.floor(my0))
    mesa_a = np.zeros((H, W), np.float32)
    mesa_a[Y0:int(np.ceil(my1)), X0:int(np.ceil(mx1))] = _cobertura((mx0, my0, mx1, my1), X0, Y0,
                                                                     int(np.ceil(mx1)) - X0, int(np.ceil(my1)) - Y0)
    qc = D.MOVEIS_TD["cadeira"]
    D_px = qc["m"] * k
    ccy = (my1 + D_px * (0.5 - qc["sob"])) if frente[1] < 0 else (my0 - D_px * (0.5 - qc["sob"]))
    cor, a = D._cadeira_bloco(Q, frente, contorno=qc["contorno"])
    D._pousar(out, cor, a, ccx, ccy, k, cobre=mesa_a)
    s_ = D.F.PECAS["sombra"]
    d_ = s_["dist_m"] * k
    sb = cv2.GaussianBlur(cv2.warpAffine(mesa_a, np.float32([[1, 0, -d_], [0, 1, d_]]), (W, H)), (0, 0),
                          s_["sig_m"] * k) * s_["forca"]
    cad_a = np.zeros((H, W), np.float32)
    h_, w_ = a.shape
    cad_a[int(ccy - h_ / 2):int(ccy - h_ / 2) + h_, int(ccx - w_ / 2):int(ccx - w_ / 2) + w_] = a
    out *= (1 - sb * np.clip(cad_a, 0, 1) * (1 - mesa_a))[..., None]


def _caracol_descida(Q, img, q):
    import final3840_casaa_1pav as P1x
    qc, qt = P1x.CARACOL_1P, T.CARACOL
    ss = q["ss"]
    cx, cy = qc["centro"]
    R = qc["r_anel"] * FA.PT_PX + 4
    pcx, pcy = Q.p2q(cx, cy)
    X0, Y0 = int(pcx - R), int(pcy - R)
    w = h = int(2 * R) + 2
    ys, xs = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    (ax, ay), (bx, by) = Q.q2p(X0, Y0), Q.q2p(X0 + 1, Y0 + 1)
    Xs, Ys = ax + (xs + 0.5) / ss * (bx - ax), ay + (ys + 0.5) / ss * (by - ay)
    r = np.hypot(Xs - cx, Ys - cy)
    th = np.degrees(np.arctan2(-(Ys - cy), Xs - cx)) % 360
    b = np.array(qc["cheio"])
    n = len(b) - 1
    kk = np.clip(np.searchsorted(b, th) - 1, 0, n - 1)
    fs, alc = qt["espelho"]
    t0, t1 = qc["tons"]
    velho = (t0 + (t1 - t0) * kk / (n - 1)) * np.where(
        kk < n - 1, 1 - fs * np.exp(-np.maximum((b[np.minimum(kk + 1, n)] - th) * np.pi / 180 * r * FA.PT_PX, 0) / alc), 1)
    n0, n1 = q["tons"]
    novo = (n1 - (n1 - n0) * kk / (n - 1)) * np.where(
        kk > 0, 1 - fs * np.exp(-np.maximum((th - b[kk]) * np.pi / 180 * r * FA.PT_PX, 0) / alc), 1)
    cheio = ((r >= qc["r_pilar"] + 0.6) & (r <= qc["r_anel"] - 1.0) & (th > b[0] + 0.8) & (th < b[-1] - 0.8))
    razao = np.where(cheio, novo / np.maximum(velho, 1e-3), 1.0)
    rz = cv2.resize(razao.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    reg = img[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    escuro = dilatar(reg.mean(axis=2) < q["escuro_max"], 1)
    viz = ~escuro
    rzv = cv2.GaussianBlur(rz * viz, (0, 0), 2.0) / np.maximum(cv2.GaussianBlur(viz.astype(np.float32), (0, 0), 2.0), 1e-4)
    rz = np.where(escuro, rzv, rz).astype(np.float32)
    out = img.copy()
    out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg * rz[..., None]), 0, 255).astype(np.uint8)
    return out


def retoques_1111f(Q, img, q=None):
    import pedidos_terreo_casaa_2910 as P
    q = q or RETOQUES_1111F
    H, W = img.shape[:2]
    par = FA.paredes_pdf(Q) > 0.3
    # 1. a caracol: a descida para a esquerda
    out = _caracol_descida(Q, img, q["caracol"])
    # 2. as folhas das portas de giro: o piso de baixo limpo e a folha de novo
    qf = q["folha"]
    ss = 8
    rng = np.random.default_rng(q["semente"])
    for x0, y0, x1, y1 in q["folhas_px"]:
        deitada = (x1 - x0) > (y1 - y0)
        e = qf["limpa_px"]
        a0, b0, a1, b1 = int(np.floor(x0)) - e, int(np.floor(y0)) - e, int(np.ceil(x1)) + e, int(np.ceil(y1)) + e
        d = qf["desloc_px"]
        if deitada:
            cima = par[b0 - 4:b0, a0:a1].mean() if b0 >= 4 else 1.0
            baixo = par[b1:b1 + 4, a0:a1].mean()
            dy = -d if cima < baixo else d
            fonte = out[b0 + dy:b1 + dy, a0:a1].copy()
        else:
            esq = par[b0:b1, a0 - 4:a0].mean()
            dir_ = par[b0:b1, a1:a1 + 4].mean()
            dx = -d if esq < dir_ else d
            fonte = out[b0:b1, a0 + dx:a1 + dx].copy()
        reg = out[b0:b1, a0:a1]
        cinza = (reg.max(axis=2).astype(np.int16) - reg.min(axis=2)) < 15
        livre = ~par[b0:b1, a0:a1] & ~(cinza & (reg.max(axis=2) < 110))     # a parede pintada também fica
        reg[livre] = fonte[livre]
        # a folha (em 8x): madeira clara, o veio no comprido, o contorno e a sombra curta
        X0, Y0 = a0 - 3, b0 - 3
        w, h = a1 - a0 + 6, b1 - b0 + 6
        m = P._ret_arred((x0, y0, x1, y1), qf["raio_px"], X0, Y0, h, w, ss)
        al = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA)
        sx, sy, sg = qf["sombra_px"]
        sb = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, sx], [0, 1, sy]]), (w, h)), (0, 0), sg)
        r_ = out[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
        r_ *= (1 - qf["sombra"] * sb * (1 - al))[..., None]
        out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(r_), 0, 255).astype(np.uint8)
        n_ = cv2.GaussianBlur(rng.normal(0, 1, m.shape).astype(np.float32), (0, 0),
                              sigmaX=(6.0 if deitada else 0.6) * ss, sigmaY=(0.6 if deitada else 6.0) * ss)
        n_ = 1 + qf["veio"] * n_ / max(float(n_.std()), 1e-6)
        out = P._pintar(out, X0, Y0, w, h, ss, m, np.float32(qf["madeira"])[None, None] * n_[..., None])
        borda = np.clip(m - cv2.erode(m, np.ones((5, 5), np.uint8)), 0, 1) * qf["contorno_alfa"]
        out = P._pintar(out, X0, Y0, w, h, ss, borda, np.float32(qf["contorno"])[None, None] * np.ones_like(borda)[..., None])
    # 3. as portas de vidro da saleta
    qs = q["saleta"]
    vx0, vy0, vx1, vy1 = qs["vao_px"]
    A0, B0, A1, B1 = int(np.floor(vx0)), int(np.floor(vy0)), int(np.ceil(vx1)), int(np.ceil(vy1)) + 1
    wv, hv = A1 - A0, B1 - B0
    Tx = FA.travertino_bruto(Q, hv, wv, q["semente"] + 7, 0.008, 0.012, 6, 0.05, forca=0.8)
    cob = _cobertura((vx0, vy0, vx1, vy1), A0, B0, wv, hv)[..., None]
    reg = out[B0:B1, A0:A1].astype(np.float32)
    reg = reg * (1 - cob) + np.float32(qs["soleira"])[None, None] * Tx[..., None] * cob
    out[B0:B1, A0:A1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    of = out.astype(np.float32)
    for yy in (vy0, vy1):                                                # as faces da parede, em linha fina
        a = _cobertura((vx0, yy - 0.45, vx1, yy + 0.45), A0, B0 - 1, wv, hv + 2)[..., None]
        of[B0 - 1:B1 + 1, A0:A1] = of[B0 - 1:B1 + 1, A0:A1] * (1 - a) + np.float32(qs["faces"]) * a
    def _ret(rr, cor, contorno):
        rx0, ry0, rx1, ry1 = rr
        X0, Y0 = int(np.floor(rx0)) - 1, int(np.floor(ry0)) - 1
        w, h = int(np.ceil(rx1)) - X0 + 2, int(np.ceil(ry1)) - Y0 + 2
        a = _cobertura(rr, X0, Y0, w, h)[..., None]
        of[Y0:Y0 + h, X0:X0 + w] = of[Y0:Y0 + h, X0:X0 + w] * (1 - a) + np.float32(cor) * a
        dentro = _cobertura((rx0 + 0.5, ry0 + 0.5, rx1 - 0.5, ry1 - 0.5), X0, Y0, w, h)[..., None]
        borda = np.clip(a - dentro, 0, 1) * 0.8
        of[Y0:Y0 + h, X0:X0 + w] = of[Y0:Y0 + h, X0:X0 + w] * (1 - borda) + np.float32(contorno) * borda
    for rr in qs["batentes_px"]:
        _ret(rr, qs["aluminio"], qs["aluminio_contorno"])
    vidros = []
    for (fx0, fy0, fx1, fy1), (gx0, gx1) in qs["folhas_px"]:
        _ret((fx0, fy0, fx1, fy1), qs["aluminio"], qs["aluminio_contorno"])
        (p0x, p0y), (p1x, p1y) = Q.q2p(gx0, fy0 + 0.35), Q.q2p(gx1, fy1 - 0.35)
        vidros.append((min(p0x, p1x), min(p0y, p1y), max(p0x, p1x), max(p0y, p1y)))
    out = np.clip(np.round(of), 0, 255).astype(np.uint8)
    out = np.clip(np.round(TA.vidro_laminas(Q, out, vidros, dict(TA.ESCADAS_TA["jardim"]["vidro"], ponta_px=0.0))),
                  0, 255).astype(np.uint8)
    # 4. a cadeira da escrivaninha da suíte 3
    qc = q["cadeira_s3"]
    c0, d0, c1, d1 = qc["cadeira_velha_px"]
    dl = qc["desloc_px"]
    out[d0:d1, c0:c1] = out[d0:d1, c0 + dl:c1 + dl]
    of = out.astype(np.float32)
    _cadeira_mesa(Q, of, qc["mesa_px"], qc["ccx"], qc["frente"])
    out = np.clip(np.round(of), 0, 255).astype(np.uint8)
    print(f"    retoques de 11/11 (mais tarde): a caracol escurecendo para a esquerda (a descida); {len(q['folhas_px'])} "
          f"folhas de giro redesenhadas, sem arcos (a da suíte 3 de volta); as portas de vidro da saleta (vão limpo, "
          f"batentes, duas folhas de correr); a cadeira da escrivaninha da suíte 3")
    return out


PASSOS = [("nublado", nublado_1p), ("tracejados", tracejados_1p), ("bege", bege_1p), ("pergolado", pergolado_1p),
          ("contorno", contorno_1p), ("vazios", vazios_1p), ("shafts", shafts_1p), ("folhas", folhas_1p),
          ("guarda_corpos", guarda_corpos_1p), ("bancada", bancada_1p), ("cubas", cubas_1p), ("tapete", tapete_1p),
          ("sala_intima", sala_intima_1p), ("closets", closets_1p), ("armarios", armarios_1p), ("bancos", bancos_1p),
          ("mesinhas_master", mesinhas_master_1p), ("portas", portas_1p), ("escadas", escadas_1p),
          ("floreira", floreira_1p), ("pisos_1111e", pisos_1111e), ("retoques_1111e", retoques_1111e),
          ("degraus_1111e", degraus_1111e), ("retoques_1111f", retoques_1111f)]


def correcoes(img, de=None, ate=None, salvar_passos=None):
    Q = quadro()
    nomes = [n for n, _ in PASSOS]
    i0 = nomes.index(de) if de else 0
    out = img
    for nome, f in PASSOS[i0:]:
        print(f"  {nome}", flush=True)
        out = f(Q, out)
        if salvar_passos:
            Path(salvar_passos).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(Path(salvar_passos) / f"passo_{nome}.png"), out)
        if nome == ate:
            break
    return out


# os antes e depois dos 17 pedidos (contra a final de ab9a071), em renders/POE642_CasaA_PH_1Pavimento_1111_<trecho>_
# antes_depois.jpg (px do quadro)
ANTES_DEPOIS_1111_1P = {"1Pavimento": {
    "planta": (1150, 260, 2830, 1720), "contorno_pergolado": (1180, 860, 1620, 1250),
    "varanda_636_painel": (1495, 320, 1640, 620), "varanda_715_painel": (1495, 870, 1640, 1220),
    "varanda_39_painel": (2480, 1180, 2640, 1600), "vazios": (1490, 580, 2180, 910),
    "shaft_parede": (2200, 320, 2420, 560), "elevador_x": (2230, 1090, 2420, 1230), "escada_u": (2230, 880, 2560, 1100),
    "caracol": (1930, 1490, 2170, 1660), "banho_master": (1320, 1440, 1760, 1650), "tapete_sala_intima": (1990, 900, 2230, 1260),
    "bancada_danae": (2150, 1430, 2280, 1600), "closet_3": (1860, 340, 2060, 520), "closet_2": (1780, 880, 2010, 1215),
    "closet_master": (1720, 1300, 1920, 1645), "closet_1": (2240, 1200, 2445, 1340),
    "portas_suite3_banho3": (1950, 460, 2130, 610), "portas_suite_master_closet": (1660, 1200, 1930, 1490),
    "portas_servico_suite1": (2080, 1300, 2200, 1520), "bege_varanda_146": (1200, 1200, 1300, 1650),
    "bege_varanda_39": (2540, 1200, 2800, 1660), "bege_servico_saleta": (1900, 1300, 2200, 1660)}}
# a 2ª leva de 11/11 (contra a final de 216506b): o Bege Bahia menos manchado e o pergolado esfumaçado, em
# renders/..._1111b_<trecho>_antes_depois.jpg
ANTES_DEPOIS_1111B_1P = {"1Pavimento": {
    "pergolado": (1170, 860, 1630, 1260), "bege_varanda_146": (1200, 1200, 1300, 1650),
    "bege_varanda_39": (2540, 1200, 2800, 1660), "bege_varandas_636_715": (1495, 320, 1640, 1220),
    "bege_servico_saleta": (1900, 1300, 2200, 1660)}}

# a 4ª leva de 11/11 (contra a final de e3cb9cf): as folhas amadeiradas das portas das suítes, os guarda-corpos das
# varandas, as cubas e as torneiras, a sala íntima, os bancos das camas, os shafts, as mesinhas e a parede da suíte
# master, o contorno dos armários e a linha de corte da escada, em renders/..._1111d_<trecho>_antes_depois.jpg
ANTES_DEPOIS_1111D_1P = {"1Pavimento": {
    "planta": (1150, 260, 2830, 1720), "folhas_suite3_varanda636": (1495, 320, 1640, 620),
    "folhas_suite2_varanda715": (1495, 870, 1640, 1220), "folhas_master_varanda146": (1200, 1190, 1380, 1660),
    "folhas_suite1_varanda39": (2480, 1090, 2790, 1420), "guarda_corpo_39_baixo": (2140, 1590, 2790, 1665),
    "cubas_master": (1515, 1578, 1685, 1645), "cubas_banho1": (2480, 1220, 2550, 1340),
    "cubas_banho2": (1715, 875, 1820, 940), "cubas_banho3": (2045, 355, 2145, 420),
    "sala_intima": (1990, 900, 2240, 1260), "bancos_suite3": (1660, 450, 1820, 540),
    "bancos_master": (1425, 1260, 1585, 1345), "bancos_suite2": (1690, 1030, 1840, 1110),
    "bancos_suite1": (2280, 1400, 2500, 1470), "shaft_cima": (2230, 330, 2380, 430),
    "shafts_master_mesinhas": (1590, 1370, 1790, 1500), "shaft_elevador": (2330, 1100, 2420, 1220),
    "closet_2": (1780, 880, 2010, 1215), "closet_master": (1720, 1300, 1920, 1645), "closet_3": (1860, 330, 2060, 520),
    "closet_1": (2240, 1190, 2450, 1345), "escada_u": (2230, 880, 2560, 1100)}}

# a 5ª leva de 11/11 (contra a final de 17670fa): a poltrona da sala íntima inteira sobre o tapete, os vidros da
# circulação e do vazio, a escrivaninha da suíte 1 (cadeira e laptop) e os pisos de vinílico e de travertino bruto, em
# renders/..._1111e_<trecho>_antes_depois.jpg
ANTES_DEPOIS_1111E_1P = {"1Pavimento": {
    "planta": (1150, 260, 2830, 1720), "sala_intima_poltrona": (1990, 900, 2240, 1260),
    "circulacao_vidros": (2020, 495, 2275, 900), "escrivaninha_suite1": (2380, 1320, 2540, 1420),
    "vinilico_suite3": (1500, 330, 1760, 520), "vinilico_suite2": (1580, 980, 1820, 1150),
    "vinilico_master": (1380, 1220, 1600, 1340), "vinilico_suite1": (2300, 1380, 2560, 1600),
    "vinilico_closet_master": (1760, 1340, 1900, 1600), "travertino_banho_master": (1440, 1430, 1700, 1590),
    "travertino_banho1": (2470, 1180, 2560, 1330), "travertino_banho2": (1690, 860, 1830, 960),
    "travertino_banho3": (1990, 330, 2120, 440), "travertino_sala_circulacao": (1980, 640, 2260, 1000)}}

# a 6ª leva de 11/11 (contra a final de 279ec5c): os degraus da escada em U no travertino novo, a caracol escurecendo
# para a esquerda, as 11 folhas de giro sem arcos (a da suíte 3 de volta), as portas de vidro da saleta e a cadeira da
# escrivaninha da suíte 3, em renders/..._1111f_<trecho>_antes_depois.jpg
ANTES_DEPOIS_1111F_1P = {"1Pavimento": {
    "planta": (1150, 260, 2830, 1720), "escada_u": (2240, 870, 2500, 1120),
    "caracol_saleta": (1900, 1470, 2150, 1660), "suite3_porta_cadeira": (1580, 480, 2060, 640),
    "porta_banho3": (2030, 440, 2140, 520), "portas_suite2_banho2_master": (1720, 950, 2010, 1260),
    "portas_circulacao": (2040, 1290, 2240, 1600), "porta_banho_suite1": (2380, 1270, 2520, 1350),
    "porta_banho_master": (1650, 1440, 1770, 1510)}}

# o teste do vinílico da foto (11/11, contra a final de 0e5d084), em renders/..._1111g_<trecho>_antes_depois.jpg
ANTES_DEPOIS_1111G_1P = {"1Pavimento": {
    "planta": (1150, 260, 2830, 1720), "suite3_closet3": (1480, 320, 2090, 660),
    "suite2_closet2": (1700, 860, 2010, 1260), "suite_master": (1330, 1190, 1920, 1640),
    "suite1_closet1": (2150, 1200, 2560, 1600), "detalhe_reguas": (1560, 1140, 1760, 1260)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", required=True, help="a final do 1º Pavimento de partida (ab9a071) ou um passo")
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--saida")
    ap.add_argument("--passos")
    ap.add_argument("--antes_depois", action="store_true",
                    help="grava os recortes de ANTES_DEPOIS_1111G_1P em renders/ (antes: a imagem de --antes, ou a de "
                         "--antes_ref)")
    ap.add_argument("--antes_ref", help="a imagem de antes dos recortes (a final instalada), no lugar de --antes")
    a = ap.parse_args()
    antes = cv2.imread(a.antes)
    out = correcoes(antes, a.de, a.ate, a.passos)
    cv2.imwrite(a.saida or str(FINAL), out)
    if a.antes_depois:
        import pedidos_terreo_casaa_2910 as P
        ref = cv2.imread(a.antes_ref) if a.antes_ref else antes
        P.antes_depois_pedidos_ta("1Pavimento", ref, out, caixas=ANTES_DEPOIS_1111G_1P, sufixo="1111g")


if __name__ == "__main__":
    main()

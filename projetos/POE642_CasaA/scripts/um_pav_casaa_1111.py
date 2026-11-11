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
NUBLADO_1P = {"vazios_pt": [(1315.4, 805.7, 1655.6, 1060.8), (1666.9, 805.7, 1925.4, 1060.8)],
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
    # a linha de corte do Térreo na escada em U e o contorno fino do vão entre os lances, por cima
    out = P1.linha_corte(Q, out)
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
# 6. Os painéis amadeirados entre as varandas e os quartos (cliente: "Representar melhor o painel amadeirado que tem
# aqui entre a varanda e o quarto"; "Representar melhor o painel amadeirado, ele acaba sumindo no piso amadeirado"): o
# painel do trilho de fora (a faixa marrom de ~0,1 m na final, junto à varanda de 6,36 m², à de 7,15 m² e à de 39 m²)
# vira um ripado de madeira escura, nogueira, com as ripas marcadas (a junta escura a cada `ripa_px`), a aresta de cima
# iluminada, o contorno escuro dos dois lados e a sombra curta na varanda, num tom bem diferente do piso vinílico.
PAINEIS_1P = {"faixas_px": [(1589.5, 346.0, 1596.5, 594.0), (1594.6, 899.0, 1600.2, 1000.0),
                            (1589.5, 1000.0, 1596.5, 1210.0), (2550.4, 1222.0, 2556.6, 1547.0)],
              "madeira": (52, 82, 122), "junta": (30, 46, 70), "ripa_px": 3.6, "junta_px": 0.9, "luz": 0.16,
              "contorno": (34, 40, 48), "contorno_px": 0.7, "sombra": 0.20, "veio": 0.08, "semente": 1116}


def paineis_1p(Q, img, q=None):
    q = q or PAINEIS_1P
    out = img.astype(np.float32)
    rng = np.random.default_rng(q["semente"])
    ss = 8
    for x0, y0, x1, y1 in q["faixas_px"]:
        X0, Y0, X1, Y1 = int(np.floor(x0)) - 4, int(np.floor(y0)) - 2, int(np.ceil(x1)) + 4, int(np.ceil(y1)) + 2
        h, w = Y1 - Y0, X1 - X0
        ys, xs = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32) / ss
        xs += X0
        ys += Y0
        dentro = (xs >= x0) & (xs < x1) & (ys >= y0) & (ys < y1)
        # as ripas: ao longo da faixa (a faixa é vertical), a junta escura a cada ripa
        fase = np.mod(ys - y0, q["ripa_px"])
        junta = dentro & (fase < q["junta_px"])
        # a luz de cima: a aresta da direita (a luz vem do alto à direita) um pouco mais clara
        rel = np.clip((xs - x0) / max(x1 - x0, 1e-3), 0, 1)
        luz = 1 + q["luz"] * (rel - 0.5)
        veio = cv2.GaussianBlur(rng.normal(0, 1, ys.shape).astype(np.float32), (0, 0), sigmaX=1.0, sigmaY=6.0)
        veio /= max(float(veio.std()), 1e-6)
        cor = np.float32(q["madeira"])[None, None, :] * (luz * (1 + q["veio"] * veio))[..., None]
        cor = np.where(junta[..., None], np.float32(q["junta"]), cor)
        borda = dentro & ((xs - x0 < q["contorno_px"]) | (x1 - xs <= q["contorno_px"]) |
                          (ys - y0 < q["contorno_px"]) | (y1 - ys <= q["contorno_px"]))
        cor = np.where(borda[..., None], np.float32(q["contorno"]), cor)

        def red(a):
            return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
        a = red(dentro)
        c = cv2.resize(cor * dentro[..., None], (w, h), interpolation=cv2.INTER_AREA) / np.maximum(a, 1e-4)[..., None]
        reg = out[Y0:Y1, X0:X1]
        # a sombra curta na varanda (para baixo e à esquerda)
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -1.4], [0, 1, 1.4]]), (w, h)), (0, 0), 1.1)
        reg *= (1 - q["sombra"] * sb * (1 - a))[..., None]
        reg[:] = reg * (1 - a[..., None]) + c * a[..., None]
    print(f"    painéis amadeirados: {len(q['faixas_px'])} trechos em ripado de nogueira (varandas de 6,36, 7,15 e "
          f"39 m²), com as ripas, o contorno e a sombra")
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
# 8. O tapete da sala íntima (cliente: "Trocar a cor do tapete. Está camuflando com o piso."; regra [11/11]: tapetes que
# não se confundem com o piso): o tapete do PDF no taupe escolhido para o tapete da varanda do Térreo (opção A), com a
# trama, a luz e a sombra das peças de cima (`terreo_casaa_1011.tapetes_1111`).
TAPETE_1P = dict(TA.TAPETES_1111, opcao="A",
                 tapetes=[("sala íntima", "ARQ_LAYOUT HUMANIZAÇÃO", (1812.1, 1146.1, 1925.5, 1344.5))])


def tapete_1p(Q, img, q=None):
    return TA.tapetes_1111(Q, img, q or TAPETE_1P)


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
    out = TA.triangulo(out, TA.seta_tri(tx, ty, (np.sin(ang), np.cos(ang)), *c["tri"]))
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


PASSOS = [("nublado", nublado_1p), ("tracejados", tracejados_1p), ("bege", bege_1p), ("pergolado", pergolado_1p),
          ("contorno", contorno_1p), ("vazios", vazios_1p), ("paineis", paineis_1p), ("bancada", bancada_1p),
          ("tapete", tapete_1p), ("closets", closets_1p), ("portas", portas_1p), ("escadas", escadas_1p),
          ("floreira", floreira_1p)]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", required=True, help="a final do 1º Pavimento de partida (ab9a071) ou um passo")
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--saida")
    ap.add_argument("--passos")
    ap.add_argument("--antes_depois", action="store_true",
                    help="grava os recortes de ANTES_DEPOIS_1111_1P em renders/ (antes: a imagem de --antes)")
    a = ap.parse_args()
    antes = cv2.imread(a.antes)
    out = correcoes(antes, a.de, a.ate, a.passos)
    cv2.imwrite(a.saida or str(FINAL), out)
    if a.antes_depois:
        import pedidos_terreo_casaa_2910 as P
        P.antes_depois_pedidos_ta("1Pavimento", antes, out, caixas=ANTES_DEPOIS_1111_1P, sufixo="1111")


if __name__ == "__main__":
    main()

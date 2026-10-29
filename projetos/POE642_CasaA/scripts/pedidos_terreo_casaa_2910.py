r"""Casa A: os pedidos do usuário de 29/10/26 à noite, sobre as finais da revisão de 29/10 (`revisao_casaa_2910`).

Cada pedido veio com um recorte da planta do Térreo; aqui, um passo por pedido, na ordem de `pedidos_terreo_ta`. O
Térreo novo segue para os outros dois pavimentos: no 1º Pavimento, o Térreo nublado em volta e nos vazios troca onde o
Térreo mudou (`nublado_1pav_ta`), e as camas ganham o matelassê; no Subsolo, as peças nevoadas do Térreo são refeitas
(`revisao_casaa_2910.revisao_ta`, a partir da final de antes da revisão). As ferramentas comuns:
- `copiar_textura`: o buraco recebe o mesmo material de outro lugar da final, no deslocamento em que o entorno do buraco
  casa melhor (cv2.matchTemplate com máscara), trecho a trecho;
- `espelhar_faixa`: uma faixa fina recebe o material de fora dela, refletido na borda (sem mancha, com o desenho dele);
- `piso_refeito` (a 2ª leva, seção 13): a zona dos móveis inteira recebe o travertino tecido de novo, emendado ao piso
  de fora pela membrana (sem degrau de tom); por cima, os móveis de novo, com o contorno limpo e a sombra suave.

Uso (sobre as finais da revisão, as do commit 219b22b; o Subsolo parte da final de antes da revisão, a do commit 1ccaaa3;
`--pasta_comparar`, opcional, com as finais da 1ª leva, a do commit 387a97f, para os antes e depois da 2ª leva):
  python3 pedidos_terreo_casaa_2910.py --pasta_antes <finais de 219b22b> --antes_subsolo <png de 1ccaaa3> \
      --pasta_comparar <finais de 387a97f>
"""
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                                    # noqa: E402
import final3840_casaa_terreo as T                              # noqa: E402


# ----------------------------------------------------------------------------------------------------------------------
# Ferramentas
def copiar_textura(out, buraco, valido, busca=260, trecho=28, anel=5, perto=8, candidatos=12, rng_sem=None):
    """Preenche `buraco` (bool) em `out` (BGR, alterado no lugar) trecho a trecho (`trecho` px): cada trecho vem do mesmo
    recorte deslocado, no deslocamento (até `busca` px, a mais de `perto` px) em que o anel de `anel` px em volta do
    trecho (só os px de `valido`) casa melhor; o recorte de origem tem de estar todo em `valido`. Devolve os px que não
    acharam origem (ficam para o inpaint de quem chama)."""
    H, W = out.shape[:2]
    falhou = np.zeros(buraco.shape, bool)
    ys, xs = np.nonzero(buraco)
    if not len(ys):
        return falhou
    ok_u8 = valido.astype(np.uint8)
    feito = np.zeros(buraco.shape, bool)
    by0, bx0 = ys.min(), xs.min()
    for ty in range(by0, ys.max() + 1, trecho):
        for tx in range(bx0, xs.max() + 1, trecho):
            b = buraco[ty:ty + trecho, tx:tx + trecho] & ~feito[ty:ty + trecho, tx:tx + trecho]
            if not b.any():
                continue
            yy, xx = np.nonzero(b)
            y0, x0 = ty + yy.min() - anel, tx + xx.min() - anel
            y1, x1 = ty + yy.max() + 1 + anel, tx + xx.max() + 1 + anel
            if y0 < 0 or x0 < 0 or y1 > H or x1 > W:
                falhou[ty:ty + trecho, tx:tx + trecho] |= b
                continue
            hb = np.zeros((y1 - y0, x1 - x0), bool)
            hb[ty + yy - y0, tx + xx - x0] = True
            ring = cv2.dilate(hb.astype(np.uint8), np.ones((2 * anel + 1,) * 2, np.uint8)).astype(bool) & ~hb \
                & valido[y0:y1, x0:x1] & ~buraco[y0:y1, x0:x1]
            if ring.sum() < 6:
                falhou[ty:ty + trecho, tx:tx + trecho] |= b
                continue
            sy0, sx0 = max(0, y0 - busca), max(0, x0 - busca)
            sy1, sx1 = min(H, y1 + busca), min(W, x1 + busca)
            janela = out[sy0:sy1, sx0:sx1].astype(np.float32)
            tpl = out[y0:y1, x0:x1].astype(np.float32)
            m = np.repeat(ring[..., None], 3, axis=2).astype(np.float32)
            cus = cv2.matchTemplate(janela, tpl, cv2.TM_SQDIFF, mask=m)
            # o recorte de origem: o buraco e o anel todos em `valido`
            need = (hb | ring).astype(np.float32)
            inval = cv2.matchTemplate((1 - ok_u8[sy0:sy1, sx0:sx1]).astype(np.float32), need, cv2.TM_CCORR)
            cus[inval > 0.5] = np.inf
            oy, ox = y0 - sy0, x0 - sx0
            cy0, cy1 = max(0, oy - perto), min(cus.shape[0], oy + perto + 1)
            cx0, cx1 = max(0, ox - perto), min(cus.shape[1], ox + perto + 1)
            cus[cy0:cy1, cx0:cx1] = np.inf
            if not np.isfinite(cus).any():
                falhou[ty:ty + trecho, tx:tx + trecho] |= b
                continue
            k = int(np.argmin(cus))
            py, px = divmod(k, cus.shape[1])
            src = out[sy0 + py:sy0 + py + (y1 - y0), sx0 + px:sx0 + px + (x1 - x0)]
            reg = out[y0:y1, x0:x1]
            reg[hb] = src[hb]
            feito[y0:y1, x0:x1] |= hb
    return falhou & ~feito


def espelhar_faixa(img, faixa, parede, max_px=8):
    """Cada px da `faixa` (fina, encostada na `parede`) recebe o px refletido na borda de fora dela, na direção que sai
    da parede mais perto (dx, dy em -1, 0, 1): o material de fora continua, com o desenho dele, sem mancha."""
    out = img.copy()
    if not faixa.any():
        return out
    H, W = faixa.shape
    _, lab = cv2.distanceTransformWithLabels((~parede).astype(np.uint8), cv2.DIST_L2, 5,
                                             labelType=cv2.DIST_LABEL_PIXEL)
    py, px = np.nonzero(parede)
    wy = np.zeros(lab.max() + 1, np.int32)
    wx = np.zeros(lab.max() + 1, np.int32)
    lp = lab[py, px]
    wy[lp], wx[lp] = py, px
    ys, xs = np.nonzero(faixa)
    qy, qx = wy[lab[ys, xs]], wx[lab[ys, xs]]
    dy, dx = np.sign(ys - qy), np.sign(xs - qx)
    # o primeiro px fora da faixa e da parede, andando para fora
    e = np.full(len(ys), -1, np.int32)
    for k in range(1, max_px + 1):
        yy, xx = np.clip(ys + k * dy, 0, H - 1), np.clip(xs + k * dx, 0, W - 1)
        livre = ~faixa[yy, xx] & ~parede[yy, xx] & (e < 0)
        e[livre] = k
    ok = e > 0
    # o reflexo na borda de fora: o px a e px é o primeiro de fora; o espelho fica a 2e - 1
    sy = np.clip(ys + (2 * e - 1) * dy, 0, H - 1)
    sx = np.clip(xs + (2 * e - 1) * dx, 0, W - 1)
    out[ys[ok], xs[ok]] = img[sy[ok], sx[ok]]
    ruim = np.zeros(faixa.shape, bool)
    ruim[ys[~ok], xs[~ok]] = True
    if ruim.any():
        out = cv2.inpaint(out, (ruim | parede).astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA) * ruim[..., None] \
            + out * ~ruim[..., None]
    return out


def _salientes(img, k=21, lim=38):
    """Os px que fogem do material em volta (objetos pequenos, traços, pontos): longe da mediana local."""
    med = cv2.medianBlur(img, k).astype(np.int16)
    return (np.abs(img.astype(np.int16) - med).max(axis=2) > lim)


def _caixas_de(m, lado, folga=12):
    """As caixas (y0, y1, x0, x1) de `lado` px que cobrem os px de m, com `folga` px de margem."""
    H, W = m.shape
    ys, xs = np.nonzero(m)
    feitas = set()
    for y, x in zip(ys // lado, xs // lado):
        feitas.add((y, x))
    return [(max(0, y * lado - folga), min(H, (y + 1) * lado + folga), max(0, x * lado - folga),
             min(W, (x + 1) * lado + folga)) for y, x in sorted(feitas)]


def segs_q(Q, segs):
    return [(*Q.p2q(a, b), *Q.p2q(c, d)) for a, b, c, d in segs]


def mascara_segs(Q, forma, segs, larg_px, ss=4):
    """Os traços (pt) numa máscara (0..1) de largura `larg_px`."""
    H, W = forma
    xs = [v for s in segs_q(Q, segs) for v in (s[0], s[2])]
    ys = [v for s in segs_q(Q, segs) for v in (s[1], s[3])]
    m = np.zeros(forma, np.float32)
    if not xs:
        return m
    X0, Y0 = max(0, int(min(xs)) - 6), max(0, int(min(ys)) - 6)
    X1, Y1 = min(W, int(max(xs)) + 7), min(H, int(max(ys)) + 7)
    t = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    for u0, v0, u1, v1 in segs_q(Q, segs):
        cv2.line(t, (int((u0 - X0) * ss), int((v0 - Y0) * ss)), (int((u1 - X0) * ss), int((v1 - Y0) * ss)), 255,
                 max(1, int(round(larg_px * ss))), cv2.LINE_AA)
    m[Y0:Y1, X0:X1] = cv2.resize(t.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    return m


def cadeia(Q, camada, ang, off, tol=0.6, min_ext=20):
    """Os traços de uma cadeia tracejada do PDF (`final3840_casaa_terreo.cadeias_tracejadas`): camada, direção (0 ou 90) e
    a distância à origem (o `off` da cadeia, em pt)."""
    out = []
    for (c, a, o), ext, segs in T.cadeias_tracejadas(Q, [camada], min_n=3, min_ext=min_ext):
        if a == ang and abs(o - off) <= tol:
            out += segs
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 1. As paredes (usuário, com os recortes da parede de cima da varanda, da parede de cima do escritório, da janela do
# jardim e de um vão: "corrigir falhas na parede. essas imperfeições não podem aparecer", "corrigir imperfeições na
# parede e na quina", "corrija as imperfeições das paredes"): a parede da final tinha, em muitos trechos, 1 a 4 px a
# mais que o contorno do PDF, em dentes e franjas da cor dela (cinza 80) por cima do piso ou da grama. Em volta de toda
# parede do PDF (`anel_px`), o que tem a cor da parede (até `tol`) e não é parede no PDF recebe o material de fora (a
# faixa é fina: o px de fora refletido na borda dela, `espelhar_faixa`); depois a parede inteira de novo no contorno do PDF, com a borda
# antisserrilhada. Também os px escuros e neutros (mais escuros que a parede, `croma`) do anel: os nós pretos da borda.
# Fora: os muros do lote (`final3840_casaa_terreo.MUROS`) e a faixa branca entre o hall externo e o
# jardim (item 4 da revisão), que encostam na parede de propósito.
PAREDES_LIMPAS = {"anel_px": 4, "tol": 22, "croma": 16,
                  "fora_q": [(2530, 870, 2775, 900)]}


def paredes_limpas(Q, img, q=None):
    q = q or PAREDES_LIMPAS
    qp = T.PAREDES_T
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") is not None and max(d["fill"]) < 0.5
                    and max(d["rect"].width, d["rect"].height) <= qp.get("max_pt", np.inf), ss=4)
    dentro = a > 0.03
    k = 2 * q["anel_px"] + 1
    anel = cv2.dilate(dentro.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & ~dentro
    im = img.astype(np.int16)
    cinza = np.abs(im - np.int16(qp["cor"][0])).max(axis=2) <= q["tol"]
    escuro = (im.max(axis=2) < qp["cor"][0] + q["tol"]) & (im.max(axis=2) - im.min(axis=2) <= q["croma"])
    franja = anel & (cinza | escuro)
    fora = np.zeros(franja.shape, bool)
    for x0, y0, x1, y1 in list(T.MUROS["faixas"]) + q["fora_q"]:
        fora[y0:y1, x0:x1] = True
    franja &= ~fora
    out = espelhar_faixa(img, franja, dentro)
    al = a.copy()
    al[fora] = np.where(dentro[fora], al[fora], 0)
    res = out.astype(np.float32) * (1 - al[..., None]) + np.float32(qp["cor"]) * al[..., None]
    res[fora] = img[fora]
    print(f"    paredes: {int(franja.sum())} px de dentes e franjas fora do contorno do PDF refeitos com o piso ou a "
          f"grama de fora; a parede de novo no contorno do PDF")
    return np.clip(np.round(res), 0, 255).astype(np.uint8)


def rotulos_mascara(Q, forma, folga=2):
    """Os px dos rótulos da final (todos), com `folga` px: os passos que refazem pisos não mexem neles."""
    import revisao_casaa_2910 as R
    m = R._rotulos_mascara(Q, forma)
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * folga + 1,) * 2, np.uint8)).astype(bool)


# ----------------------------------------------------------------------------------------------------------------------
# 2. As janelas (usuário: "corrigir imperfeições na borda da parede e na borda da janela", com a janela de cima do
# escritório; "melhore o aspecto dessa janela", com a janela da pia da cozinha; a janela do jardim de 17,46 m² no recorte
# da parede, com uma pinta escura no vidro): cada uma de novo no desenho do PDF (as peças brancas da ARQ_PAREDE), no
# padrão das janelas que ficaram boas (a da garagem): o vão da parede (`vao`) no cinza claro do peitoril, com a face de
# cada lado num fio escuro, e o vidro (`vidros`, cada folha da janela) mais claro, com o contorno fino; a sombra curta da
# folha no peitoril. A da cozinha tem duas folhas de correr, desencontradas, como no PDF; a da quina da varanda entra
# também (a ponta dela, junto à quina da parede, tinha um nó claro).
JANELAS_TA = {"peitoril": (198, 200, 203), "face": (118, 120, 124), "face_px": 0.55, "vidro": (226, 229, 232),
              "vidro_contorno": (122, 125, 130), "vidro_px": 0.5, "sombra": 0.22, "folga_px": 2,
              "janelas": [
                  {"nome": "do jardim de 17,46 m²", "vao": (2284.8, 1096.6, 2296.2, 1251.9),
                   "vidros": [(2288.8, 1094.9, 2291.7, 1253.6)]},
                  {"nome": "de cima do escritório", "vao": (2249.1, 550.6, 2341.5, 561.9),
                   "vidros": [(2249.1, 558.5, 2341.5, 561.4)]},
                  {"nome": "da direita do escritório", "vao": (2341.5, 563.7, 2352.9, 633.9),
                   "vidros": [(2339.0, 562.0, 2341.3, 633.9)], "sem_vao": True},
                  {"nome": "da quina da varanda", "vao": (1666.9, 567.6, 1729.2, 579.0),
                   "vidros": [(1666.9, 572.1, 1729.2, 575.0)]},
                  {"nome": "da pia da cozinha", "vao": (1922.0, 1474.7, 1933.4, 1670.3),
                   "vidros": [(1927.7, 1477.0, 1930.5, 1574.8), (1930.5, 1570.2, 1933.4, 1668.0)]}]}


def janelas_ta(Q, img, q=None):
    q = q or JANELAS_TA
    out = np.ascontiguousarray(img.copy())
    for j in q["janelas"]:
        caixa = tuple(f(v) for f, v in zip((min, min, max, max), zip(*([j["vao"]] + j["vidros"]))))
        tl = FA.tela(out, Q, caixa, folga=q["folga_px"] + 3)
        if not j.get("sem_vao"):
            mv = tl.ret(j["vao"])
            tl.pintar(mv, q["peitoril"])
            tl.contorno(mv, q["face_px"], q["face"])
        for v in j["vidros"]:
            m = tl.ret(v)
            FA.sombra_q(tl, m, forca=q["sombra"], dist=0.7, sigma=0.7)
            tl.pintar(m, q["vidro"])
            tl.contorno(m, q["vidro_px"], q["vidro_contorno"])
        out = tl.gravar()
        print(f"    janela {j['nome']}: de novo no desenho do PDF ({len(j['vidros'])} folha(s))")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 3. A despensa (usuário: "não há esse movel em L na despensa. remova-o"): no PDF a despensa só tem o piso; o armário em
# L do render (a marcenaria rosada junto à parede da direita e à de baixo, com a sombra) sai e entra um trecho inteiro
# de granito limpo (`despensa_ta`). O rótulo vai para o centro no passo dos rótulos.
DESPENSA_TA = {"miolo_pt": (1825.6, 1678.8, 1922.0, 1775.2), "granito_lum": (40, 135), "granito_rb": 18,
               "pecas_px": [(2104, 1528, 2153, 1600), (2048, 1593, 2153, 1633)], "transicao_px": 4,
               "busca_px": (1450, 1080, 2750, 1645)}


def _granito(im):
    i = im.astype(np.int16)
    lum = i.mean(axis=2)
    return (lum > 58) & (lum < 135) & (i[..., 2] - i[..., 0] > 18)


def _peca_granito(img, gr, livre, h, w, ref_m, ref_s, busca):
    """O trecho h x w de granito limpo (sem juntas, sem manchas de sombra) de cor mais perto da de referência."""
    bx0, by0, bx1, by1 = busca
    melhor = None
    for yy in range(by0, by1 - h, 2):
        for xx in range(bx0, bx1 - w, 2):
            if gr[yy:yy + h, xx:xx + w].mean() < 0.99 or not livre[yy:yy + h, xx:xx + w].all():
                continue
            p = img[yy:yy + h, xx:xx + w].astype(np.float32)
            L = p.mean(axis=2)
            linha = max(np.abs(np.diff(L.mean(axis=0))).max(), np.abs(np.diff(L.mean(axis=1))).max())
            hb, wb = h // 10 * 10, w // 10 * 10
            mancha = np.abs(L[:hb, :wb].reshape(hb // 10, 10, wb // 10, 10).mean(axis=(1, 3)) - L.mean()).max()
            p = p.reshape(-1, 3)
            d = float(np.abs(p.mean(axis=0) - ref_m).sum() + 0.5 * np.abs(p.std(axis=0) - ref_s).sum() + 4 * linha
                      + 3 * mancha)
            if melhor is None or d < melhor[0]:
                melhor = (d, xx, yy)
    return melhor


def despensa_ta(Q, img, q=None):
    """O armário em L e a sombra dele saem: as `pecas_px` (o braço de cima, junto à parede da direita, e o de baixo)
    recebem cada uma um trecho inteiro do mesmo granito, limpo, da cozinha ou da área gourmet (o de cor e pintas mais
    parecidas com as do granito que sobrou na despensa); a transição com o granito da despensa é de `transicao_px` px e
    as paredes não mudam. Roda antes de tirar os rótulos (o DESPENSA, por cima do armário, sai e volta no centro)."""
    q = q or DESPENSA_TA
    out = img.copy()
    gr = _granito(img)
    pa = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") is not None, ss=4)
    rot = rotulos_mascara(Q, img.shape[:2])
    (x0, y0), (x1, y1) = Q.p2q(*q["miolo_pt"][:2]), Q.p2q(*q["miolo_pt"][2:])
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    livre = (pa < 0.01) & ~rot
    livre[Y0 - 20:Y1 + 20, X0 - 20:X1 + 20] = False
    ref = img[Y0:Y1, X0:X1][gr[Y0:Y1, X0:X1] & ~rot[Y0:Y1, X0:X1]].astype(np.float32)
    ref_m, ref_s = ref.mean(axis=0), ref.std(axis=0)
    t = q["transicao_px"]
    for px0, py0, px1, py1 in q["pecas_px"]:
        h, w = py1 - py0, px1 - px0
        _, sx, sy = _peca_granito(img, gr, livre, h, w, ref_m, ref_s, q["busca_px"])
        peca = img[sy:sy + h, sx:sx + w].astype(np.float32)
        # a rampa só nos lados que dão para o granito da despensa (nas paredes, a peça vai até elas)
        al = np.ones((h, w), np.float32)
        yy, xx = np.mgrid[0:h, 0:w]
        for d, fora in ((xx, pa[py0:py1, px0 - 1]), (w - 1 - xx, pa[py0:py1, px1]), (yy, pa[py0 - 1, px0:px1]),
                        (h - 1 - yy, pa[py1, px0:px1])):
            if fora.mean() < 0.5:
                al = np.minimum(al, np.clip((d + 1) / (t + 1), 0, 1))
        al *= 1 - pa[py0:py1, px0:px1]
        reg = out[py0:py1, px0:px1].astype(np.float32)
        out[py0:py1, px0:px1] = np.clip(np.round(reg * (1 - al[..., None]) + peca * al[..., None]), 0, 255
                                        ).astype(np.uint8)
        print(f"    despensa: o armário sai ({w}x{h} px em granito limpo de ({sx}, {sy}))")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 4. A ilha da varanda gourmet (usuário: "essa linha preta ao meio da pedra na ilha da varanda não existe. remova-a."): a
# linha escura atravessada na pedra da ilha (no PDF, uma peça só, sem divisão) recebe o granito de logo acima e de logo
# abaixo, em espelho, linha a linha (`linha_px`: a faixa dela, x0, y0, x1, y1).
ILHA_TA = {"linha_px": (1478, 1284, 1767, 1296), "escuro": 6}


def ilha_ta(Q, img, q=None):
    q = q or ILHA_TA
    x0, y0, x1, y1 = q["linha_px"]
    out = img.copy()
    L = img.astype(np.float32).mean(axis=2)
    # a linha: as linhas de px da faixa bem mais escuras que a mediana do granito de cima e de baixo
    ref = np.median(np.concatenate([L[y0 - 8:y0 - 3, x0:x1], L[y1 + 3:y1 + 8, x0:x1]]))
    perfil = np.median(L[y0:y1, x0:x1], axis=1)
    linhas = [y0 + i for i, v in enumerate(perfil) if v < ref - q["escuro"]]
    if not linhas:
        print("    ilha da varanda: a linha escura não foi achada")
        return out
    a, b = min(linhas) - 1, max(linhas) + 2
    meio = (a + b) / 2
    for y in range(a, b):
        src = 2 * a - y - 1 if y < meio else 2 * b - y - 1
        out[y, x0:x1] = img[src, x0:x1]
    print(f"    ilha da varanda: sem a linha escura no meio da pedra (y {a} a {b - 1})")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 5. A borda da piscina (usuário: "remova o traço da borda da piscina. note que ele só aparece em um trecho e depois não
# tem mais. por isso, remova qualquer traço de borda da piscina"): o fio lilás no Bege Bahia junto à borda de baixo da
# piscina (a aresta de uma peça do PDF que o render desenhou só de x 1098 em diante): a faixa dele (`faixa_px`) recebe o
# Bege Bahia de logo abaixo (`desloc_px`), coluna a coluna; a sombra do pergolado e os tracejados pretos, verticais,
# seguem iguais. Em volta das outras bordas da piscina e do spa não há fio.
PISCINA_TA = {"faixa_px": (1098, 1055, 1352, 1063), "desloc_px": 9}


def piscina_ta(Q, img, q=None):
    q = q or PISCINA_TA
    x0, y0, x1, y1 = q["faixa_px"]
    out = img.copy()
    d = q["desloc_px"]
    out[y0:y1, x0:x1] = img[y0 + d:y1 + d, x0:x1]
    # a emenda de cima e de baixo, macia (1 px de cada lado, meio a meio)
    for y in (y0, y1 - 1):
        out[y, x0:x1] = ((out[y, x0:x1].astype(np.uint16) + img[y, x0:x1]) // 2).astype(np.uint8)
    print(f"    piscina: sem o fio de borda no Bege Bahia ({(x1 - x0) * (y1 - y0)} px, o Bege Bahia de logo abaixo)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 6. Os rótulos (usuário: "corrigir contornos. e rótulos de todos os ambientes centralizados."): no começo dos pedidos,
# os rótulos dos ambientes saem (`rotulos_tirar_ta`: o fundo sob cada um, pela cor dele, como nos itens 1 a 3 da
# revisão), para os passos que refazem pisos e móveis não esbarrarem neles; no fim (`rotulos_centro_ta`), cada um volta
# no centro do piso livre do ambiente dele: o recinto do PDF (`final3840_casab.ambientes_rotulos`, fechado pelas
# paredes, pelos vãos e pelos boxes, com os boxes e a divisória da Casa A), menos os móveis, as louças, as bancadas, os
# carros e os tracejados das projeções (com `folga_px`); entre os px onde a caixa do rótulo cabe inteira no livre, o mais
# perto do centro do ambiente (nos ambientes abertos, `alvo_pdf`, o ponto do texto do PDF; os tapetes, maiores que
# `tapete_m2`, não são obstáculo, e os rótulos que ficam, sim). Nos ambientes abertos, o recinto vaza para o vizinho (a área dele passa de `vazou` vezes a
# do rótulo): ali o rótulo fica onde está, como na Casa B. A cor: o branco sobre o granito e a grama, o cinza dos rótulos no resto. Ficam onde estão os
# rótulos acertados na revisão (os jardins, a área de serviço descoberta) e os das peças (piscina, prainha, spa, deck,
# shaft, elevador e a claraboia).
ROTULOS_CENTRO_TA = {"manter": ("ELEVADOR", "SHAFT", "PROJ. CLARABOIA", "JARDIM", "ÁREA DE SERVIÇO DESCOBERTA",
                                "PISCINA", "PRAINHA", "SPA", "DECK DE MADEIRA"),
                     "obstaculos": ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_LOUÇAS E METAIS", "ARQ_MARCENARIA",
                                    "ARQ_BANCADAS", "ARQ_ELEMENTOS FIXOS", "EST_PILAR", "DOC_TEXTOS",
                                    "ARQ_ESCADAS E RAMPAS"),
                     "folga_px": 3, "obst_px": 2, "escuro_lum": 125, "branco": (250, 250, 250), "vazou": 1.6,
                     "tapete_m2": 3.0, "minimo": 0.45, "alvo_pdf": ("SALA DE ESTAR", "HALL INTERNO", "SALA DE JANTAR", "VARANDA"),
                     "tom_sigma_px": 4.0, "corpos": (1.3, 1.15, 1.0), "aberto_px": 30,
                     # a garagem: a faixa livre acima dos carros, no meio do carro do centro; o quarto do motorista: o
                     # piso livre abaixo da cama
                     "regioes_px": {"GARAGEM": (2165, 1310, 2700, 1640)},
                     "alvos_px": {"GARAGEM": (2432, 1329), "Q. MOTORISTA": (2463, 1266)}}


def rotulos_tirar_ta(Q, img, q=None):
    """Os rótulos dos ambientes saem: o texto (o alfa de cada um, `revisao_casaa_2910._alfa_rotulo`, com 1 px) recebe o
    piso de volta copiado do entorno (`copiar_textura`; a subtração pela cor deixava o texto fantasma, porque a final
    suavizou os rótulos depois de escritos)."""
    import revisao_casaa_2910 as R
    q = q or ROTULOS_CENTRO_TA
    rot, aj = R._rotulos_pav(Q)
    tirados, alfas = [], []
    for r in rot:
        if r[0] in q["manter"]:
            continue
        a = R._alfa_rotulo(Q, img.shape[:2], r, aj)
        if a.max() < 0.3:
            continue
        tirados.append(r)
        alfas.append(a)
    texto = np.zeros(img.shape[:2], bool)
    for a in alfas:
        texto |= a > 0.03
    buraco = cv2.dilate(texto.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    todos = R._rotulos_mascara(Q, img.shape[:2])
    valido = ~cv2.dilate((buraco | todos | _salientes(img)).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    out = img.copy()
    falhou = copiar_textura(out, buraco, valido, busca=150, trecho=14, anel=4, perto=4)
    if falhou.any():
        out = cv2.inpaint(out, (falhou * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    # o tom: o do entorno (média normalizada, sem os traços e os pontos); do trecho copiado, só o desenho fino (sem o
    # remendo mais claro ou mais escuro que o piso em volta)
    s_ = q["tom_sigma_px"]
    V = (~buraco & ~_salientes(img, k=21, lim=14)).astype(np.float32)
    B = buraco.astype(np.float32)
    I0, F = img.astype(np.float32), out.astype(np.float32)
    tom_fora = cv2.GaussianBlur(I0 * V[..., None], (0, 0), s_) / np.maximum(cv2.GaussianBlur(V, (0, 0), s_), 1e-3)[..., None]
    tom_copia = cv2.GaussianBlur(F * B[..., None], (0, 0), s_) / np.maximum(cv2.GaussianBlur(B, (0, 0), s_), 1e-3)[..., None]
    out[buraco] = np.clip(np.round(F + tom_fora - tom_copia), 0, 255).astype(np.uint8)[buraco]
    print(f"    rótulos: {len(tirados)} tirados para os pedidos (o piso copiado do entorno; voltam no centro do "
          f"ambiente no fim)")
    return out, tirados, aj


def rotulos_centro_ta(Q, img, tirados, aj, q=None):
    import final3840_casab as F
    import retoque_1pav_casae as R1
    import revisao_casaa_2910 as R
    import re
    q = q or ROTULOS_CENTRO_TA
    H, W = img.shape[:2]
    e2000 = W / 2000
    esc = FA.A.LARGURA / 2000

    def ajuste(r):
        """O ajuste do rótulo na final (o desvio e as opções), se houver."""
        ax, ay = Q.p2q(*r[2])
        for a_ in aj:
            if a_[0] == r[0] and np.hypot(ax - a_[1][0] * e2000, ay - a_[1][1] * e2000) < 25 * e2000:
                op = a_[3] if len(a_) > 3 else {}
                return a_[2], (op if isinstance(op, dict) else {"corpo": op})
        return (0.0, 0.0), {}

    def alfa(r, desvio, op):
        ax, ay = Q.p2q(*r[2])
        return R._alfa_rotulo(Q, (H, W), r, [(r[0], (ax / e2000, ay / e2000), desvio, op)])

    # o centro atual de cada rótulo (o desenho dele, no corpo da final)
    pontos = []
    for r in tirados:
        c = R._caixa(alfa(r, *ajuste(r)))
        pontos.append(((c[0] + c[2]) / 2, (c[1] + c[3]) / 2))
    guardar = (F.vidros_box, F.duchas_box, Q.preencher)
    preencher = Q.preencher

    def preencher_com_divisoria(filtro, ss=4, fs=True):
        m = preencher(filtro, ss=ss, fs=fs)
        sonda = {"layer": "ARQ_PAREDE", "fill": (0.36, 0.36, 0.36), "type": "f"}
        return np.maximum(m, FA.ret_aa(Q, FA.PAREDES_A["divisoria"])) if filtro(sonda) else m
    try:
        F.vidros_box, F.duchas_box = FA.vidros_box_a, FA.duchas_box_a
        Q.preencher = preencher_com_divisoria
        ambs = [F.ambientes_rotulos(Q, pontos, todas=t) for t in (True, False)]
    finally:
        F.vidros_box, F.duchas_box, Q.preencher = guardar
    grande = q["tapete_m2"] * 56.69 ** 2                 # os tapetes não são obstáculo: o rótulo pode ficar sobre eles
    obst = Q.preencher(lambda d: d.get("layer") in q["obstaculos"] and d["rect"].width * d["rect"].height < grande,
                       ss=2, fs=True) > 0.05
    for r in R._rotulos_pav(Q)[0]:                        # os rótulos que ficam também são obstáculo
        if r[0] in q["manter"]:
            a_ = alfa(r, *ajuste(r))
            if a_.max() > 0.3:
                x0_, y0_, x1_, y1_ = R._caixa(a_)
                obst[y0_:y1_, x0_:x1_] = True
    tr = np.zeros(obst.shape, np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in q["obstaculos"] and d["type"] == "s":
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c))], False, 1, 2)
    for _, _, segs in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"]):
        for u0, v0, u1, v1 in segs_q(Q, segs):
            cv2.line(tr, (int(u0), int(v0)), (int(u1), int(v1)), 1, 3)
    obst |= tr.astype(bool)
    k = 2 * q["obst_px"] + 1
    obst = cv2.dilate(obst.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    novos, out = [], img.copy()
    lum = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    f = q["folga_px"]
    for i, r in enumerate(tirados):
        area = [float(m_.group(1).replace(",", ".")) for t in r[1] for m_ in [re.search(r"A:\s*([\d,]+)", t[0])] if m_]
        # o recinto: das duas repartições (fechada também pelos vidros e caixilhos, ou só pelas paredes), a de área mais
        # perto da do rótulo
        regs = [a_ == i + 1 for a_ in ambs]
        razao = [rg.sum() / Q.px_m ** 2 / area[0] if area else 0 for rg in regs]
        k_ = int(np.argmin([abs(np.log(max(z, 1e-3))) for z in razao]))
        reg = regs[k_]
        vazou = not area or not (q["minimo"] <= razao[k_] <= q["vazou"]) or reg.sum() < 50
        desvio, op = ajuste(r)
        c0 = R._caixa(alfa(r, desvio, op))
        if r[0] in q["regioes_px"]:                    # o ambiente aberto com a região livre dada (a garagem)
            x0_, y0_, x1_, y1_ = q["regioes_px"][r[0]]
            reg = np.zeros_like(reg)
            reg[y0_:y1_, x0_:x1_] = True
        elif vazou:                                    # o recinto vazou (ambiente aberto) ou não fechou: fica perto
            m_ = q["aberto_px"]                        # de onde está
            reg = np.zeros_like(reg)
            reg[max(c0[1] - m_, 0):c0[3] + m_, max(c0[0] - m_, 0):c0[2] + m_] = True
        livre = reg & ~obst
        # o corpo: o padrão (`corpos`[0]) onde cabe no piso livre; senão, o nome em duas linhas no mesmo corpo (quando
        # ele tem duas palavras e a primeira não é abreviada); senão, o compacto
        palavras = r[0].split()
        quebra = len(palavras) == 2 and len(palavras[0]) > 2
        tentativas = [(c_, qb) for c_ in q["corpos"] for qb in ((False, True) if quebra else (False,))]
        for corpo, qb in tentativas:
            op_c = {k2: v for k2, v in op.items() if k2 not in ("cor", "quebra")}
            op_c["corpo"] = corpo
            if qb:
                op_c["quebra"] = palavras
            c = R._caixa(alfa(r, desvio, op_c))
            w, h = c[2] - c[0], c[3] - c[1]
            cabe = cv2.erode(livre.astype(np.uint8), np.ones((h + 2 * f, w + 2 * f), np.uint8)).astype(bool)
            if cabe.any():
                break
        ys, xs = np.nonzero(reg)
        gx, gy = xs.mean(), ys.mean()                  # o centro do ambiente (o recinto inteiro)
        if r[0] in q["alvos_px"]:                      # o centro da faixa livre dada (o quarto do motorista, a garagem)
            gx, gy = q["alvos_px"][r[0]]
        elif r[0] in q["alvo_pdf"]:                    # nos ambientes abertos, o centro é o do texto do PDF
            gx, gy = Q.p2q(*r[2])
        cx0, cy0 = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
        ys2, xs2 = np.nonzero(cabe)
        if len(ys2):
            j = int(np.argmin((xs2 - gx) ** 2 + (ys2 - gy) ** 2))
            tx, ty = float(xs2[j]), float(ys2[j])
        else:                                          # não cabe em nenhum lugar livre: fica onde está
            tx, ty = cx0, cy0
        d_novo = (desvio[0] + (tx - cx0) / esc, desvio[1] + (ty - cy0) / esc)
        a = alfa(r, d_novo, op_c)
        x0, y0, x1, y1 = R._caixa(a)
        fundo = np.median(lum[y0:y1, x0:x1][a[y0:y1, x0:x1] < 0.05])
        cor = q["branco"] if fundo < q["escuro_lum"] else R1.ROTULOS["cor"]
        out = R._com_rotulo(out, a, cor)
        novos.append(f"{r[0]} {corpo:.2f}x{' em 2 linhas' if qb else ''} ({round(pontos[i][0])}, {round(pontos[i][1])})"
                     f"->({round(tx)}, {round(ty)})")
    print("    rótulos no centro do piso livre: " + "; ".join(novos))
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 7. Os tracejados (usuário, com o recorte da entrada da garagem: "corrigir falha no tracejado"; "tem um tracejado que não
# foi representado da laje. são dois tracejados paralelos. note que são dois tracejados mais pontilhados, mais próximos os
# tracejos. veja no pdf."; e, com o recorte da pista: "esse tracejado não existe."):
# - a linha do afastamento do PDF (DOC_LINHAS E PROJEÇÕES, de traço longo, a reta de cima, a da direita, a de baixo e a
#   inclinada da esquerda, `afastamento`) estava só no render, cinza e falhada (a final deixava de fora as retas longas,
#   `final3840_casaa_terreo.PROJ["max_doc_pt"]`): o fio antigo sai (a faixa de `faixa_px` em volta da reta recebe o
#   material de cada lado, espelhado) e a reta entra inteira, do início ao fim, em preto ou branco pelo fundo;
# - a laje: o contorno de fora da projeção da cobertura (ARQ_CONTRAPISO, traço curto) tinha o de dentro, paralelo, a
#   ~34 pt, que não entrou (`laje_dentro`: as retas de cima, da direita, de baixo e da esquerda): entra igual ao de fora;
# - na pista, duas retas da hachura da pedra no PDF (ARQ_CONTRAPISO, x = 2379 e 2384 pt, abaixo de y = 1786 pt) tinham
#   entrado como se fossem a projeção da cobertura (a 2 px dela) e atravessavam a pista até o muro: saem (`nao_existe`).
TRACEJADOS_TA = {"afastamento": [(0.0, 539.0), (0.0, 1787.0), (85.5, -261.0), (90.0, -2965.0)],
                 "laje_dentro": [(0.0, 545.0), (90.0, -2347.0), (0.0, 1781.0), (90.0, -1324.0)],
                 "nao_existe_q": [(2626, 1645, 2646, 1940)], "faixa_px": 7, "salto": 10,
                 "laje_fora_pista": [(0.0, 1815.0)], "pista_x0": 1905,
                 "apagar_q": [(2560, 1620, 3262, 1666), (3236, 320, 3264, 1666)]}


def _segs_doc(Q, ang, off, camada, tol=1.0, min_ext=20):
    out = []
    for (c, a, o), ext, segs in T.cadeias_tracejadas(Q, [camada], min_n=2, min_ext=min_ext):
        if a == ang and abs(o - off) <= tol:
            out += segs
    return out


def _apagar_faixa(img, mascara_linha, faixa_px, salto, caixas, rotulo=None):
    """Os px da faixa (a máscara da linha, mais `faixa_px`), só nas `caixas` (px) onde está o fio antigo, que fogem do
    material em volta recebem o px a `salto` px dali, de um lado ou do outro da linha (o que tem a cor mais perto da dos
    vizinhos ao longo dela): o material segue, sem trazer o do outro lado da borda. Com `rotulo` (o material de cada
    px pelo PDF), o px só vem do mesmo material (a 1, 1,5 ou 2 saltos): na quina com outra borda ela não vira degrau."""
    out = img.copy()
    k = 2 * faixa_px + 1
    faixa = cv2.dilate((mascara_linha > 0.05).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    dentro = np.zeros(faixa.shape, bool)
    for x0, y0, x1, y1 in caixas:
        dentro[y0:y1, x0:x1] = True
    faixa &= dentro
    sal = _salientes(img, k=15, lim=14) & faixa
    sal = cv2.dilate(sal.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & faixa
    H, W = faixa.shape
    im = img.astype(np.float32)
    for y, x in zip(*np.nonzero(sal)):
        horiz = faixa[y, max(0, x - 12):x + 13].sum() > faixa[max(0, y - 12):y + 13, x].sum()
        viz = im[y, max(0, x - 14):x + 15][~sal[y, max(0, x - 14):x + 15]] if horiz else \
            im[max(0, y - 14):y + 15, x][~sal[max(0, y - 14):y + 15, x]]
        ref = np.median(viz, axis=0) if len(viz) else im[y, x]
        passos = (salto,) if rotulo is None else (salto, salto * 3 // 2, 2 * salto)
        cands = [c for p in passos for c in (((y + p, x), (y - p, x)) if horiz else ((y, x + p), (y, x - p)))]
        cands = [(yy, xx) for yy, xx in cands if 0 <= yy < H and 0 <= xx < W and not faixa[yy, xx]
                 and (rotulo is None or rotulo[yy, xx] == rotulo[y, x])]
        if cands:
            yy, xx = min(cands, key=lambda c: float(np.abs(im[c] - ref).sum()))
            out[y, x] = img[yy, xx]
    return out


def tracejados_ta(Q, img, q=None, etapa="tudo"):
    """etapa "apagar": só tira as retas da hachura e o fio antigo; "desenhar": só desenha as retas (entre as duas, a
    borda da pista é refeita, `borda_pista_ta`, sem os traços novos dentro da faixa dela)."""
    import ajustes_casaa as AJ
    q = q or TRACEJADOS_TA
    out = img.copy()
    grupos = [_segs_doc(Q, a, o, "DOC_LINHAS E PROJEÇÕES") for a, o in q["afastamento"]]
    afast = [s for g in grupos for s in g]
    laje = [s for a, o in q["laje_dentro"] for s in _segs_doc(Q, a, o, "ARQ_CONTRAPISO", min_ext=120)]
    if etapa == "desenhar":
        # o contorno de fora da laje junto ao canteiro da pista sai com a borda refeita (`borda_pista_ta`): volta só ali
        fora = [s for a, o in q["laje_fora_pista"] for s in _segs_doc(Q, a, o, "ARQ_CONTRAPISO", min_ext=120)
                if min(Q.p2q(s[0], s[1])[0], Q.p2q(s[2], s[3])[0]) >= q["pista_x0"]]
        antes = out
        out, n_b = T.preto_branco(Q, out, afast + laje)
        out, _ = T.preto_branco(Q, out, fora, dict(T.PROJ, limiar=0))    # na borda grama/pedra, preto como era
        # as paredes e o portão ficam por cima das retas, como no PDF (a laje de dentro e o afastamento correm junto à
        # parede de baixo da garagem e ao portão)
        a = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") is not None, ss=4)[..., None]
        out = np.clip(np.round(out * (1 - a) + antes * a), 0, 255).astype(np.uint8)
        print(f"    tracejados: o afastamento ({len(afast)} traços) inteiro e nítido; o contorno de dentro da laje "
              f"({len(laje)} traços)")
        return out
    # as retas da hachura que não existem
    for x0, y0, x1, y1 in q["nao_existe_q"]:
        reg = out[y0:y1, x0:x1].astype(np.int16)
        L = reg.mean(axis=2)
        col = np.median(L, axis=0)
        escuras = np.nonzero(col < np.median(col) - 10)[0]
        for c in escuras:
            for dc in (4, -4, 6, -6):
                if 0 <= c + dc < reg.shape[1] and (c + dc) not in escuras:
                    out[y0:y1, x0 + c] = out[y0:y1, x0 + c + dc]
                    break
    # o afastamento: o fio antigo sai (na pista, a pedra só da pedra e a grama só da grama) e a reta entra
    m = mascara_segs(Q, out.shape[:2], [_linha_inteira(g) for g in grupos if g], 1.5)
    pista = AJ.acesso_alfa(Q.p2q, out.shape[:2])[0] > 0.5
    out = _apagar_faixa(out, m, q["faixa_px"], q["salto"], q["apagar_q"], rotulo=pista)
    print("    tracejados: sem as retas da hachura da pista e sem o fio antigo do afastamento")
    if etapa == "apagar":
        return out
    return tracejados_ta(Q, out, q, "desenhar")


def _linha_inteira(segs):
    """A reta inteira de um grupo de traços colineares: do primeiro ponto ao último, ao longo dela."""
    x0, y0, x1, y1 = segs[0]
    t = np.arctan2(y1 - y0, x1 - x0)
    u = [(np.cos(t) * x + np.sin(t) * y, (x, y)) for s in segs for x, y in ((s[0], s[1]), (s[2], s[3]))]
    a, b = min(u)[1], max(u)[1]
    return (a[0], a[1], b[0], b[1])


# ----------------------------------------------------------------------------------------------------------------------
# 8. O contorno da pista (usuário, com o recorte da entrada da garagem: "corrigir falha no tracejado e no contorno da
# pista de acesso à garagem. as bordas estão com falhas, do inicio ao fim"): a borda da pedra portuguesa com a grama,
# do portão à garagem, tinha a franja verde-acinzentada da pedra antiga, pontos claros e um degrau onde a linha do
# afastamento cruza. Ela é refeita no contorno do PDF (o preenchimento da pista na ARQ_CONTRAPISO, `ajustes_casaa.
# acesso_alfa`, o contorno com a garagem de fora), numa faixa de `faixa_px` px de cada lado: de dentro, a pedra refletida
# na borda de dentro da faixa; de fora, a grama refletida na de fora (`espelhar_faixa`); a borda com a cobertura exata
# do contorno, e por cima a linha fina do PDF (`ajustes_casaa.ACESSO_BORDA["linha"]`), contínua do início ao fim.
BORDA_PISTA_TA = {"caixa_q": (1900, 1600, 3445, 1945), "faixa_px": 4, "faixa_grama_px": 7, "linha": ((112, 114, 110), 0.55, 0.62)}


def borda_pista_ta(Q, img, q=None):
    import ajustes_casaa as AJ
    q = q or BORDA_PISTA_TA
    H, W = img.shape[:2]
    poly, contornos = AJ.acesso_alfa(Q.p2q, (H, W))
    cx0, cy0, cx1, cy1 = q["caixa_q"]
    cont = [c for c in contornos if len(c) > 50 and c[:, 0].max() > cx0 and c[:, 1].max() > cy0]
    m = np.zeros((H * 4, W * 4), np.uint8)
    for c in cont:
        cv2.fillPoly(m, [np.int32(np.round(c * 4))], 255)
    A = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    caixa = np.zeros((H, W), bool)
    caixa[cy0:cy1, cx0:cx1] = True
    im = img.astype(np.int16)
    grama = (im[..., 1] > im[..., 2] + 2) & (im[..., 1] > im[..., 0])
    dentro = (A > 0.5) & caixa
    k, kg = 2 * q["faixa_px"] + 1, 2 * q["faixa_grama_px"] + 1     # a grama tinha o fio claro a ~4 px da borda
    perto_grama = cv2.dilate(grama.astype(np.uint8), np.ones((kg + 6, kg + 6), np.uint8)).astype(bool)
    borda = (cv2.dilate(dentro.astype(np.uint8), np.ones((kg, kg), np.uint8)).astype(bool) &
             ~cv2.erode(dentro.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)) & caixa & perto_grama
    faixa_in = borda & dentro
    faixa_out = borda & ~dentro
    out = espelhar_faixa(img, faixa_in, faixa_out | ~caixa | ~dentro & ~borda)
    out = espelhar_faixa(out, faixa_out, faixa_in | dentro)
    # a borda antisserrilhada: a pedra (de dentro) e a grama (de fora) misturadas pela cobertura do contorno
    pedra = espelhar_faixa(img, borda, ~dentro & ~borda, max_px=16)    # a pedra estendida sobre a faixa toda
    gr = espelhar_faixa(img, borda, dentro & ~borda, max_px=16)         # a grama estendida sobre a faixa toda
    a = A[..., None]
    mix = pedra.astype(np.float32) * a + gr.astype(np.float32) * (1 - a)
    perto = cv2.dilate(borda.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    res = out.astype(np.float32)
    res[perto] = mix[perto]
    cor, forca, larg = q["linha"]
    kk = 8
    lm = np.zeros((H * kk, W * kk), np.uint8)
    for c in cont:
        cv2.polylines(lm, [np.int32(np.round(c * kk))], True, 255, max(1, round(larg * 1.92 * kk)), cv2.LINE_AA)
    la = cv2.resize(lm, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    la *= forca * perto_grama * caixa
    res = res * (1 - la[..., None]) + np.float32(cor) * la[..., None]
    print(f"    pista: a borda com a grama refeita no contorno do PDF ({int(borda.sum())} px), com a linha fina "
          f"contínua")
    return np.clip(np.round(res), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 9. O box do banho varanda (usuário: "arrume esse box. ele está passando pela parede. deve ficar reto e dentro de sua
# área, conforme o pdf. mantenha a folha contínua."): as duas folhas desencontradas (um degrau no meio) iam até 1,5 px
# dentro da parede da direita. Agora: a faixa da linha do box volta ao piso (`final3840_casaa.limpar_box`) e entra uma
# folha só, reta, na linha do PDF, da face de uma parede à da outra (as faces achadas nas paredes do PDF, na própria
# linha do vidro, menos `recuo_px`: a aresta sombreada da parede do render não fica sob o vidro), com as faces finas e a
# sombra curta do padrão dos boxes.
BOX_VARANDA_TA = {"meio": 1712.8, "recuo_px": 1.2}


def box_varanda_ta(Q, img, q=None):
    q = q or BOX_VARANDA_TA
    qb = FA.BANHOS["box"]
    box = next(b for b in AJ_folhas(Q) if b["hor"] and abs(b["meio"] - q["meio"]) < 1)
    v0, v1 = FA.vao_box(Q, box)
    out = FA.limpar_box(Q, np.ascontiguousarray(img.copy()), box, v0, v1)
    # as faces das paredes na linha do vidro, em px
    pa = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") is not None
                     and max(d["fill"]) < 0.5, ss=8)
    (u0, yc), (u1, _) = Q.p2q(v0, box["meio"]), Q.p2q(v1, box["meio"])
    yi, xm = int(round(yc)), int(round((u0 + u1) / 2))
    linha = pa[yi - 1:yi + 2].max(axis=0)
    a = xm
    while a > 0 and linha[a - 1] < 0.5:
        a -= 1
    b = xm
    while b < len(linha) - 1 and linha[b + 1] < 0.5:
        b += 1
    # a cobertura parcial do px da face (o vidro encosta nela, sem entrar)
    xa, xb = a - (1 - linha[a - 1]) if linha[a - 1] < 1 else a, b + 1 + (1 - linha[b + 1]) if linha[b + 1] < 1 else b + 1
    # nas pontas, o vidro antigo que entrava na aresta da parede: a coluna recebe o que está logo acima da faixa
    for c in list(range(int(xa) - 4, int(xa) + 2)) + list(range(int(xb) - 1, int(xb) + 5)):
        for r in range(yi - 3, yi + 4):
            out[r, c] = out[yi - 6 if r < yi else yi + 6, c]
    xa, xb = xa + q["recuo_px"], xb - q["recuo_px"]
    s0, s1 = Q.q2p(xa, yc)[0], Q.q2p(xb, yc)[0]
    e = qb["larg_px"] / FA.PT_PX / 2
    r = (s0, box["meio"] - e, s1, box["meio"] + e)
    tl = FA.tela(out, Q, r, folga=5)
    m = tl.ret(r)
    FA.sombra_q(tl, m, forca=qb["sombra"], dist=0.9, sigma=0.8)
    tl.pintar(m, qb["vidro"])
    tl.contorno(m, qb["face_px"], qb["face"])
    out = tl.gravar()
    print(f"    banho varanda: o box numa folha só de vidro, reta, de face a face das paredes ({xb - xa:.1f} px)")
    return out


def AJ_folhas(Q):
    import ajustes_casaa as AJ
    return AJ.folhas_box(Q.pg)


# ----------------------------------------------------------------------------------------------------------------------
# A sombra e a pintura das peças (as de `revisao_casab_2910`, com o arredondamento): a sombra macia vai até a borda da
# caixa de desenho, que tem de ter a folga dela inteira (`SOMBRA_FOLGA_PX`: o desvio de 0,10 m e a cauda do desfoque);
# truncada, a cauda escurecia a caixa em 1 nível e a borda dela aparecia no piso como um retângulo.
SOMBRA_FOLGA_PX = 26


def _sombra_piso(img, X0, Y0, a, px_m, sombras=None):
    """A sombra macia e a de contato (`final3840_casad.SOMBRA_JOGOS_D`) do alfa `a` (com o canto em X0, Y0) no piso, fora
    da peça; `a` já com a folga para a sombra."""
    import final3840_casad as D
    luz = np.ones(a.shape, np.float32)
    for s in sombras or D.SOMBRA_JOGOS_D:
        d = np.float32([[1, 0, s["dx_m"] * px_m], [0, 1, s["dy_m"] * px_m]])
        luz *= 1 - cv2.GaussianBlur(cv2.warpAffine(a, d, a.shape[::-1], flags=cv2.INTER_LINEAR), (0, 0),
                                    s["sig_m"] * px_m) * s["forca"]
    h, w = a.shape
    reg = img[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    img[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg * (1 - (1 - luz) * (1 - a))[..., None]), 0, 255).astype(np.uint8)
    return img


def _pintar(img, X0, Y0, w, h, ss, M, cor):
    """A `cor` (BGR, em ss) nos px da máscara `M` (0 a 1, em ss), levadas ao quadro em área (a borda antisserrilhada)."""
    def red(x):
        return cv2.resize(x, (w, h), interpolation=cv2.INTER_AREA)
    a = red(M)
    c = red(cor * M[..., None]) / np.maximum(a, 1e-4)[..., None]
    reg = img[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    img[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg * (1 - a[..., None]) + c * a[..., None]), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 10. As espreguiçadeiras (usuário: "melhorar o aspecto das espreguiçadeiras"): as duas do render (caixas lilás, tortas
# em relação ao PDF, com rabichos e a sombra borrada) saem: a zona delas recebe o Bege Bahia de novo (tecido por quilting
# com o Bege Bahia limpo logo acima, `fonte_px`, no tom do entorno). Entram as do PDF (ARQ_LAYOUT HUMANIZAÇÃO, o
# retângulo girado de 2,00 x 0,60 m e a dobra do encosto): a estrutura em madeira (freijó, `moldura_m`, com o veio ao
# longo da peça, o chanfro e o aro), a almofada em linho off-white por dentro (o volume nas bordas, a textura fina), o
# encosto do lado da dobra mais curto (um tom acima, a luz subindo até a cabeceira) e o vinco da dobra; a sombra macia e
# a de contato no piso, como as dos jogos (`final3840_casad.SOMBRA_JOGOS_D`).
ESPREG_TA = {"pecas_pt": [(1158.9, 728.3, 1274.1, 814.5), (1158.9, 813.4, 1274.1, 899.5)],
             "camada": "ARQ_LAYOUT HUMANIZAÇÃO", "fonte_px": (1335, 350, 1475, 520), "zona_px": 14,
             "desvio_sombra_px": (-6, 6), "p_px": 30, "ss": 8, "semente": 2911,
             "moldura_m": 0.045, "madeira": "freijo", "almofada": (212, 225, 236), "volume_m": 0.07, "volume": 0.13,
             "encosto": (0.96, 1.03), "vinco": 0.22, "vinco_px": 0.7, "linho": 0.007}


def _poligono_pt(d):
    pts = [(p.x, p.y) for it in d["items"] for p in it[1:] if hasattr(p, "x")]
    out = []
    for p in pts:
        if not out or max(abs(p[0] - out[-1][0]), abs(p[1] - out[-1][1])) > 0.05:
            out.append(p)
    if len(out) > 1 and max(abs(out[0][0] - out[-1][0]), abs(out[0][1] - out[-1][1])) < 0.05:
        out.pop()
    return out


def espreguicadeiras_ta(Q, img, q=None):
    import revisao_casab_2910 as RB
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import texturas
    q = q or ESPREG_TA
    ss, k = q["ss"], Q.px_m
    out = img.copy()
    pecas = []
    for r in q["pecas_pt"]:
        d = next(d for d in Q.desenhos if d.get("layer") == q["camada"] and d["type"] == "f"
                 and max(abs(a - b) for a, b in zip(d["rect"], r)) < 0.5)
        canto = np.float32([Q.p2q(*p) for p in _poligono_pt(d)])
        # a dobra: o traço de dentro (as pontas longe dos cantos)
        dobra = None
        for t in Q.desenhos:
            if t.get("layer") != q["camada"] or t["type"] != "s" or not all(
                    r[0] - 0.5 <= v <= r[2] + 0.5 for v in (t["rect"].x0, t["rect"].x1)) or not all(
                    r[1] - 0.5 <= v <= r[3] + 0.5 for v in (t["rect"].y0, t["rect"].y1)):
                continue
            ps = [(p.x, p.y) for it in t["items"] for p in it[1:] if hasattr(p, "x")]
            if all(min(np.hypot(*(np.float32(Q.p2q(*p)) - c)) for c in canto) > 3 for p in ps):
                dobra = np.float32([Q.p2q(*p) for p in ps[:2]])
        pecas.append((canto, dobra))
    # 1. o Bege Bahia de novo na zona das antigas (e da sombra delas)
    X0 = int(min(c[:, 0].min() for c, _ in pecas)) - SOMBRA_FOLGA_PX
    Y0 = int(min(c[:, 1].min() for c, _ in pecas)) - SOMBRA_FOLGA_PX
    X1 = int(max(c[:, 0].max() for c, _ in pecas)) + SOMBRA_FOLGA_PX
    Y1 = int(max(c[:, 1].max() for c, _ in pecas)) + SOMBRA_FOLGA_PX
    w, h = X1 - X0, Y1 - Y0
    zona = np.zeros((h, w), np.uint8)
    dx, dy = q["desvio_sombra_px"]
    for c, _ in pecas:
        cv2.fillPoly(zona, [np.int32(np.round(c - (X0, Y0)))], 1)
        cv2.fillPoly(zona, [np.int32(np.round(c - (X0 - dx, Y0 - dy)))], 1)
    zona = cv2.dilate(zona, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * q["zona_px"] + 1,) * 2))
    # só no Bege Bahia: a água da piscina ao lado (e a borda dela) fica
    rg = img[Y0:Y1, X0:X1].astype(np.int16)
    agua = cv2.dilate(((rg[..., 0] - rg[..., 2]) > 25).astype(np.uint8), np.ones((7, 7), np.uint8))
    zona &= 1 - agua
    fx0, fy0, fx1, fy1 = q["fonte_px"]
    fonte = img[fy0:fy1, fx0:fx1]
    tec = texturas.quilting(texturas.variantes(fonte, False), h, w, p=q["p_px"], sobra=max(3, q["p_px"] // 3),
                            rng=np.random.default_rng(q["semente"]))[:h, :w].astype(np.float32)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    anel = cv2.dilate(zona, np.ones((9, 9), np.uint8)).astype(bool) & ~zona.astype(bool)
    tec *= (np.median(reg[anel], axis=0) / np.maximum(tec.reshape(-1, 3).mean(axis=0), 1))[None, None, :]
    al = cv2.GaussianBlur(zona.astype(np.float32), (0, 0), 1.6)
    al = np.maximum(al, cv2.erode(zona, np.ones((5, 5), np.uint8)).astype(np.float32))
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - al[..., None]) + tec * al[..., None]), 0, 255).astype(np.uint8)
    # 2. as novas, peça a peça
    rng = np.random.default_rng(q["semente"])
    for i, (c, dobra) in enumerate(pecas):
        M = np.zeros((h * ss, w * ss), np.uint8)
        cv2.fillPoly(M, [np.int32(np.round((c - (X0, Y0)) * ss))], 255)
        M = M.astype(np.float32) / 255
        a = cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA)
        out = _sombra_piso(out, X0, Y0, a, k)
        dist = cv2.distanceTransform((M > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / ss / k      # m
        mold = (M > 0.5) & (dist <= q["moldura_m"])
        alm = (M > 0.5) & (dist > q["moldura_m"])
        # o eixo da peça: o lado mais comprido
        lados = [(c[j], c[(j + 1) % len(c)]) for j in range(len(c))]
        p0, p1 = max(lados, key=lambda l: np.hypot(*(l[1] - l[0])))
        eixo = (p1 - p0) / np.hypot(*(p1 - p0))
        ang = np.degrees(np.arctan2(-eixo[1], eixo[0]))
        # a madeira
        veio = RB._veio_tb(np.random.default_rng(q["semente"] + 10 + i), h * ss, w * ss, ang, k, ss)
        Mm = mold.astype(np.float32)
        tom = np.float32(RB.TONS_TB[q["madeira"]])
        cor_m = tom[None, None, :] * (veio * RB._relevo_tb(M, k, ss))[..., None]
        out = _pintar(out, X0, Y0, w, h, ss, Mm, cor_m)
        # a almofada: volume, encosto (do lado da dobra mais perto da ponta), vinco e linho
        Ma = alm.astype(np.float32)
        da = cv2.distanceTransform(alm.astype(np.uint8), cv2.DIST_L2, 5) / ss / k
        fator = 1 - q["volume"] * (1 - np.minimum(1, da / q["volume_m"])) ** 2
        yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
        px, py = xx / ss + X0, yy / ss + Y0
        if dobra is not None:
            m0 = dobra.mean(axis=0)
            centro = c.mean(axis=0)
            s = np.sign(np.dot(m0 - centro, eixo))                      # o encosto: o lado da dobra além do centro
            t = ((px - m0[0]) * eixo[0] + (py - m0[1]) * eixo[1]) * s     # px além da dobra
            ponta = max(float(np.dot(cc - m0, eixo) * s) for cc in c)
            enc = t > 0
            e0, e1 = q["encosto"]
            fator *= np.where(enc, e0 + (e1 - e0) * np.clip(t / max(ponta, 1), 0, 1), 1.0)
            fator *= 1 - q["vinco"] * np.exp(-(t / q["vinco_px"]) ** 2) * np.where(t < 0, 1.0, 0.6)
        lin = cv2.GaussianBlur(rng.normal(0, 1, M.shape).astype(np.float32), (0, 0), 0.8 * ss)
        fator *= 1 + q["linho"] * lin / max(float(lin.std()), 1e-6)
        cor_a = np.float32(q["almofada"])[None, None, :] * fator[..., None]
        out = _pintar(out, X0, Y0, w, h, ss, Ma, cor_a)
    print("    espreguiçadeiras: as 2 do PDF, em madeira com a almofada de linho, o encosto e a dobra, a sombra no "
          "Bege Bahia")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 11. As cadeiras do jantar (usuário: "substituir essas cadeiras pela nossa modelo, integrando suavemente ao piso. as
# cadeiras devem ser com assento marrom"; depois: "corrigir piso, nas beiradas . note que ficou defeituoso." e "essas
# imperfeições no piso precisam sair. no entorno das cadeiras, vemos manchas. o piso precisa ter perfeição e fluidez"):
# o modelo padrão (a cadeira da mesa de 10 lugares da biblioteca, `final3840_casad.jantar_d`, como em
# `revisao_casaa_2910.jantar_ta`) com o assento em couro marrom (`linho`: o tom na luz da foto). Em volta da mesa e das
# cadeiras, até `margem_px` (as sombras e os restos das cadeiras antigas, as manchas cinza e a lilás junto ao tampo), o
# travertino é refeito inteiro (`piso_refeito`); o tampo fica, com a beira na cor dele e a sombra macia no piso.
JANTAR_MARROM_TA = {"linho": {"tom": (52, 80, 118), "gama": 1.0, "sat_madeira": (0.30, 0.15), "absoluto": True},
                    "margem_px": 16, "semente": 2916}


def jantar_marrom_ta(Q, img, q=None):
    import revisao_casaa_2910 as RA
    q = q or JANTAR_MARROM_TA
    qj = dict(RA.JANTAR_TA, linho=q["linho"])
    mesa = qj["mesa_pt"]
    forma = img.shape[:2]
    cads = [d for d in Q.desenhos if d.get("layer") == qj["camada_cadeiras"] and d["type"] in ("f", "fs")
            and mesa[0] - 35 <= d["rect"].x0 and d["rect"].x1 <= mesa[2] + 35
            and mesa[1] - 35 <= d["rect"].y0 and d["rect"].y1 <= mesa[3] + 35]
    assentos = [d for d in cads if qj["lado_pt"][0] <= min(d["rect"].width, d["rect"].height)
                and max(d["rect"].width, d["rect"].height) <= qj["lado_pt"][1]]
    d_m = next(d for d in Q.desenhos if d.get("layer") == qj["camada_mesa"] and d["type"] in ("f", "fs")
               and max(abs(a_ - b_) for a_, b_ in zip(d["rect"], mesa)) < 0.5)
    tampo = Q.preencher(lambda d: d is d_m, ss=4)
    pecas = np.zeros(forma, bool)
    for d in cads:
        r = d["rect"]
        (x0, y0), (x1, y1) = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        pecas[int(y0):int(np.ceil(y1)) + 1, int(x0):int(np.ceil(x1)) + 1] = True
    zona = _dilatar(pecas | (tampo > 0.02), q["margem_px"]) & ~(tampo > 0.98) & ~_paredes_fixas(Q, forma)
    zona &= ~_outros_moveis(Q, forma, [mesa] + [tuple(d["rect"]) for d in cads])
    # o tampo: o miolo da final; a beira (antisserrilhada pelo PDF) na cor do miolo mais perto
    ys, xs = np.nonzero(tampo > 0.001)
    X0, Y0, X1, Y1 = xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3
    a = tampo[Y0:Y1, X0:X1]
    miolo = a > 0.98
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    _, rot = cv2.distanceTransformWithLabels((~miolo).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    yy, xx = np.nonzero(miolo)
    idx = np.zeros(rot.max() + 1, int)
    idx[rot[yy, xx]] = np.arange(len(yy))
    cor = reg.copy()
    cor[~miolo] = reg[yy[idx[rot[~miolo]]], xx[idx[rot[~miolo]]]]
    A, C = np.zeros(forma, np.float32), np.zeros(img.shape, np.float32)
    A[Y0:Y1, X0:X1], C[Y0:Y1, X0:X1] = a, cor
    out = piso_refeito(img, zona, q["semente"])
    out = _colar_peca(Q, out, A, C, sombras=SOMBRA_MESA_TA)
    Qp = RA._QCamadas(Q, {**{(qj["camada_cadeiras"], tuple(a_["rect"])): "ARQ_MOBILIÁRIO" for a_ in assentos},
                          (qj["camada_mesa"], mesa): "ARQ_MOBILIÁRIO"})
    out = D_jantar(Qp, out, out, qj)
    print(f"    mesa de jantar: {len(assentos)} cadeiras no modelo padrão, assento em couro marrom; o travertino em volta "
          f"refeito ({int(zona.sum())} px), o tampo com a sombra macia")
    return out


def D_jantar(Qp, img, piso, q):
    import final3840_casad as D
    return D.jantar_d(Qp, img, piso, q=q)


# ----------------------------------------------------------------------------------------------------------------------
# 12. O estar da varanda (usuário: "precisamos melhorar muito esse ambiente. são duas mesas de centro que precisam ser
# bem evidenciadas as suas partes. é uma sobre posta a outra, com tom e sobretom. corrija os contornos das poltronas e
# adicione uma mesinha redonda de madeira entre elas conforme o pdf. melhore o aspecto do tapete e suas bordas. melhore o
# aspecto do bancos estofado e seu entorno. abaixo dele, o piso está imperfeito."; depois: "essa marca em L, começando
# atrás do banco, precisa sair. o piso travertino bruto precisa ficar perfeito."). O ambiente é refeito do piso para
# cima, com o sofá curvo de novo por cima (`_estofado`):
# - o piso (travertino) na zona dos móveis, até `margem_px` deles (com a sombra antiga do banco, que fazia a marca em L):
#   `piso_refeito`, emendado ao piso de fora sem degrau;
# - o tapete do PDF (ARQ_LAYOUT HUMANIZAÇÃO), reto, no tom do tapete da final, com a trama do tapete da biblioteca
#   (`final3840_casad.TAPETE_TRAMA_D`), a faixa de acabamento da borda (`faixa_m`, um tom abaixo) e a sombra curta da
#   espessura dele no piso;
# - as duas mesas de centro do PDF (ARQ_MOBILIÁRIO), uma sobre a outra, em carvalho: a de baixo no tom médio, a de cima
#   no sobretom mais claro, cada uma com o veio, o chanfro e o aro; a de cima faz sombra na de baixo;
# - as mesinhas redondas do PDF (entre as poltronas e na ponta do sofá) em madeira;
# - as duas poltronas no modelo padrão de contorno limpo (`poltronas_limpas_ta`);
# - o banco estofado do PDF (DOC_TEXTOS): o quadro fino em madeira, o assento em linho com as três partes (os vincos nas
#   costuras do PDF) e as duas almofadas das pontas, um tom acima e mais altas, cada peça com volume e sombra.
VARANDA_TA = {"tapete_pt": (1415.6, 602.9, 1585.7, 744.6), "sofa_pt": (1510.0, 578.9, 1613.6, 692.9),
              "poltronas_pt": [(1387.3, 610.7, 1437.5, 658.2), (1387.3, 687.9, 1437.5, 735.4)],
              "banco_pt": (1446.3, 738.5, 1559.7, 764.0),
              "mesas_pt": [((1481.7, 657.5, 1530.3, 715.7), (100, 134, 172)), ((1465.2, 639.9, 1507.4, 680.4),
                                                                              (134, 168, 202))],
              "mesinha_tom": (92, 124, 160),
              "mesinhas_pt": [(1408.3, 663.8, 1425.3, 680.8), (1492.6, 590.7, 1509.6, 607.7)],
              "janela_px": (1556, 340, 1812, 610), "margem_px": 18,
              "fora_px": [(1785, 340, 1812, 440)],                  # a planta junto da ponta do sofá
              "faixa_m": 0.035, "faixa": 0.06, "borda_sombra": 0.16, "semente": 2912,
              "banco": {"quadro_pt": (1448.2, 739.5, 1557.8, 763.0), "costuras_x_pt": (1484.7, 1521.3),
                        "almofadas_pt": [(1451.3, 741.1, 1467.7, 761.5), (1538.3, 741.1, 1554.6, 761.5)],
                        "linho": (196, 209, 219), "almofada": (150, 172, 196), "madeira": "castanho",
                        "volume_m": 0.06, "volume": 0.16, "vinco": 0.30, "vinco_px": 0.8, "trama": 0.02,
                        "almofada_volume": 0.22}}


def _mascara_ret(Q, camada, r, forma, ss=4):
    return Q.preencher(lambda d, c=camada, r=r: d.get("layer") == c and d["type"] in ("f", "fs")
                       and max(abs(a - b) for a, b in zip(d["rect"], r)) < 0.5, ss=ss)


def _trama(Q, h, w, semente, q=None):
    """O relevo do tapete do bloco da biblioteca (`final3840_casad.TAPETE_TRAMA_D`) em h x w: o fator em volta de 1."""
    import final3840_casad as D
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import texturas
    q = q or D.TAPETE_TRAMA_D
    foto = cv2.imread(str(AQUI.parent.parent / "_blocos" / "recortes" / f"{q['recorte']}.png"))
    x0, y0, x1, y1 = q["trecho"]
    L = foto[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    rel = L / cv2.GaussianBlur(L, (0, 0), q["sigma_px"])
    e = Q.px_m / q["px_m_foto"]
    rel = cv2.resize(rel, None, fx=e, fy=e, interpolation=cv2.INTER_AREA)
    u8 = np.repeat(np.clip((rel - 1) * 510 + 128, 0, 255).astype(np.uint8)[..., None], 3, axis=2)
    tec = texturas.quilting(texturas.variantes(u8, True), h, w, p=q["p_px"], sobra=max(3, q["p_px"] // 3),
                            rng=np.random.default_rng(semente))[:h, :w]
    return 1 + np.clip(q["forca"] * (tec[..., 0].astype(np.float32) - 128) / 510, -q["limite"], q["limite"])


def _madeira_peca(Q, out, M, X0, Y0, w, h, ss, tom, ang, semente, sombra=True):
    """Uma peça de madeira (a máscara `M` em ss, com o canto em X0, Y0): a sombra no que está embaixo, o veio no
    ângulo `ang`, o chanfro e o aro."""
    import revisao_casab_2910 as RB
    k = Q.px_m
    a = cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA)
    if sombra:
        out = _sombra_piso(out, X0, Y0, a, k)
    veio = RB._veio_tb(np.random.default_rng(semente), h * ss, w * ss, ang, k, ss)
    tom = RB.TONS_TB[tom] if isinstance(tom, str) else tom
    cor = np.float32(tom)[None, None, :] * (veio * RB._relevo_tb(M, k, ss))[..., None]
    return _pintar(out, X0, Y0, w, h, ss, M, cor)


def varanda_estar_ta(Q, img, q=None):
    q = q or VARANDA_TA
    forma = img.shape[:2]
    tap = FA.ret_aa(Q, q["tapete_pt"])
    sofa = _mascara_ret(Q, "ARQ_LAYOUT HUMANIZAÇÃO", q["sofa_pt"], forma) > 0.02
    lista = ([("DOC_TEXTOS", r) for r in q["poltronas_pt"] + [q["banco_pt"]]]
             + [("ARQ_MOBILIÁRIO", r) for r, _ in q["mesas_pt"]] + [("ARQ_MOBILIÁRIO", r) for r in q["mesinhas_pt"]])
    pecas = _pecas_pdf(Q, lista, forma) > 0.02
    nomes = ("varanda, de cima", "varanda, de baixo")
    peg = _pegada_poltronas(Q, nomes, forma)
    zona = _dilatar((tap > 0.02) | sofa | pecas | peg, q["margem_px"])
    X0, Y0, X1, Y1 = q["janela_px"]
    jan = np.zeros(forma, bool)
    jan[Y0:Y1, X0:X1] = True
    zona &= jan & ~_paredes_fixas(Q, forma) & ~_plantas(img)
    for fx0, fy0, fx1, fy1 in q["fora_px"]:
        zona[fy0:fy1, fx0:fx1] = False
    zona &= ~_outros_moveis(Q, forma, [q["tapete_pt"], q["sofa_pt"]] + [r for _, r in lista])
    cor_t = _cor_tapete(img, tap, sofa | pecas | peg)
    # 1. o piso e o tapete
    out = piso_refeito(img, zona, q["semente"])
    out = _tapete_novo(Q, out, tap, cor_t, q["semente"] + 1, q)
    # 2. o sofá curvo, as mesas de centro (a de baixo primeiro) e as mesinhas
    out = _estofado(Q, out, "sofá curvo da varanda")
    for i, (r, tom_m) in enumerate(q["mesas_pt"]):
        out = _peca_madeira_pdf(Q, out, "ARQ_MOBILIÁRIO", r, tom_m, -55.0, q["semente"] + 10 + i)
    for i, r in enumerate(q["mesinhas_pt"]):
        out = _peca_madeira_pdf(Q, out, "ARQ_MOBILIÁRIO", r, q["mesinha_tom"], 30.0 + 40 * i, q["semente"] + 20 + i)
    # 3. as poltronas e o banco estofado
    out = poltronas_limpas_ta(Q, out, _pecas_poltronas(nomes))
    out = banco_estofado_ta(Q, out, q["banco_pt"], q["banco"], q["semente"] + 30)
    out = _tracejados_zona(Q, out, zona)
    print(f"    varanda: o estar refeito (o piso, o tapete, o sofá curvo, as 2 mesas de centro sobrepostas, as 2 mesinhas "
          f"de madeira, as 2 poltronas e o banco estofado; {int(zona.sum())} px de piso)")
    return out


def _peca_madeira_pdf(Q, out, camada, r, tom, ang, semente, ss=8, sombra=True):
    d = next(d for d in Q.desenhos if d.get("layer") == camada and d["type"] in ("f", "fs")
             and max(abs(a - b) for a, b in zip(d["rect"], r)) < 0.5)
    (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    f = SOMBRA_FOLGA_PX
    X0, Y0 = int(np.floor(min(x0, x1))) - f, int(np.floor(min(y0, y1))) - f
    X1, Y1 = int(np.ceil(max(x0, x1))) + f, int(np.ceil(max(y0, y1))) + f
    w, h = X1 - X0, Y1 - Y0
    M = np.zeros((h * ss, w * ss), np.uint8)
    for c in Q.caminhos(d):
        if len(c) >= 3:
            cv2.fillPoly(M, [np.int32(np.round((np.float32(c) - (X0, Y0)) * ss))], 255)
    return _madeira_peca(Q, out, M.astype(np.float32) / 255, X0, Y0, w, h, ss, tom, ang, semente, sombra)


def _ret_arred(r_px, raio_px, X0, Y0, h, w, ss):
    M = np.zeros((h * ss, w * ss), np.uint8)
    (a, b), (c, d) = ((r_px[0] - X0) * ss, (r_px[1] - Y0) * ss), ((r_px[2] - X0) * ss, (r_px[3] - Y0) * ss)
    rr = int(round(raio_px * ss))
    a, b, c, d = (int(round(v)) for v in (a, b, c, d))
    cv2.rectangle(M, (a + rr, b), (c - rr, d), 255, -1)
    cv2.rectangle(M, (a, b + rr), (c, d - rr), 255, -1)
    for cx, cy in ((a + rr, b + rr), (c - rr, b + rr), (a + rr, d - rr), (c - rr, d - rr)):
        cv2.circle(M, (cx, cy), rr, 255, -1)
    return M.astype(np.float32) / 255


def banco_estofado_ta(Q, img, r, q, semente):
    ss, k = 8, Q.px_m
    (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    f = SOMBRA_FOLGA_PX
    X0, Y0, X1, Y1 = int(x0) - f, int(y0) - f, int(np.ceil(x1)) + f, int(np.ceil(y1)) + f
    w, h = X1 - X0, Y1 - Y0
    out = img.copy()
    rng = np.random.default_rng(semente)
    externo = _ret_arred((x0, y0, x1, y1), 1.6, X0, Y0, h, w, ss)
    (qa, qb), (qc, qd) = Q.p2q(*q["quadro_pt"][:2]), Q.p2q(*q["quadro_pt"][2:])
    assento = _ret_arred((qa, qb, qc, qd), 1.2, X0, Y0, h, w, ss)
    # a sombra no piso e o quadro de madeira
    out = _madeira_peca(Q, out, externo, X0, Y0, w, h, ss, q["madeira"], 0.0, semente)
    # o assento: linho com volume em cada parte, os vincos nas costuras
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    px = xx / ss + X0
    partes = np.zeros(assento.shape, np.float32)
    cortes = [qa] + [Q.p2q(c, 0)[0] for c in q["costuras_x_pt"]] + [qc]
    for a_, b_ in zip(cortes[:-1], cortes[1:]):
        m = ((px >= a_) & (px < b_)).astype(np.uint8) & (assento > 0.5)
        dist = cv2.distanceTransform(m, cv2.DIST_L2, 5) / ss / k
        partes = np.maximum(partes, np.where(m > 0, np.minimum(1, dist / q["volume_m"]), 0))
    fator = 1 - q["volume"] * (1 - partes) ** 2
    for c in q["costuras_x_pt"]:
        xc = Q.p2q(c, 0)[0]
        fator *= 1 - q["vinco"] * np.exp(-((px - xc) / q["vinco_px"]) ** 2)
    tr = cv2.GaussianBlur(rng.normal(0, 1, assento.shape).astype(np.float32), (0, 0), 0.5 * ss)
    fator *= 1 + q["trama"] * tr / max(float(tr.std()), 1e-6)
    cor = np.float32(q["linho"])[None, None, :] * fator[..., None]
    out = _pintar(out, X0, Y0, w, h, ss, assento, cor)
    # as almofadas das pontas: um tom acima, mais altas (o miolo claro, a borda funda), com a sombra no assento
    for ra in q["almofadas_pt"]:
        (a0, b0), (a1, b1) = Q.p2q(*ra[:2]), Q.p2q(*ra[2:])
        Ma = _ret_arred((a0, b0, a1, b1), 2.4, X0, Y0, h, w, ss)
        aa = cv2.resize(Ma, (w, h), interpolation=cv2.INTER_AREA)
        out = _sombra_piso(out, X0, Y0, aa, k)
        dist = cv2.distanceTransform((Ma > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / ss / k
        t = np.minimum(1, dist / 0.07)
        f = (1 - q["almofada_volume"] * (1 - t) ** 2) * (1 + 0.04 * (t - 0.5))
        tr = cv2.GaussianBlur(rng.normal(0, 1, Ma.shape).astype(np.float32), (0, 0), 0.5 * ss)
        f *= 1 + q["trama"] * tr / max(float(tr.std()), 1e-6)
        out = _pintar(out, X0, Y0, w, h, ss, Ma, np.float32(q["almofada"])[None, None, :] * f[..., None])
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 13. O piso perfeito e fluido em volta dos móveis (pedidos do usuário vendo a entrega: "ainda não ficou bom. note que tem
# imperfeição no piso, ao redor da mesa. o piso precisa ficar perfeito e fluido."; "essas imperfeições no piso precisam
# sair. no entorno das cadeiras, vemos manchas. o piso precisa ter perfeição e fluidez"; "corrigir esses traços no tapete
# e em volta da poltrona. o tapete tem que estar perfeito, tanto no seu interior quanto no contorno"; "corrija as
# poltronas também"; "corrija o sofá, tapete e borda da mesa, sem essa mancha"; "essa marca em L, começando atrás do
# banco, precisa sair. o piso travertino bruto precisa ficar perfeito."; "corrija o entorno dessa mesa lateral a
# poltrona. está borrada. precisamos ver o contorno da mesa, o piso, o efeito suave da sombra.").
# Os remendos de antes (o piso de um trecho ao lado, ou o tom médio do entorno) deixavam bordas: caixas mais claras, a
# marca da zona, o desenho borrado. Agora, em cada ambiente, a zona dos móveis inteira (com as sombras e os restos das
# peças antigas) recebe o travertino tecido de novo (`piso_refeito`) e, por cima, os móveis de novo, cada um com o
# contorno limpo e a sombra suave.
# - `piso_refeito`: o quilting do travertino limpo (`fontes_px`, os espelhos só na horizontal: os estratos ficam
#   deitados), emendado ao piso de fora pela membrana (`_membrana`): a diferença entre o piso real e o tecido, na borda
#   da zona (sem os traços e os pontos, `salto`), suavizada ao longo dela e levada para dentro, harmônica. O tom chega à
#   borda igual ao de fora, sem degrau e sem mancha; dentro, o desenho é o do travertino.
# - `poltronas_limpas_ta`: o modelo padrão (a poltrona da sala íntima da Casa E) com o contorno limpo (`_modelo_limpo`):
#   a silhueta alisada, sem a franja castanha do bouclé da foto (a beira de `beira_px` com a cor do estofado de dentro)
#   e com um fio um pouco mais escuro na beira; o lugar das antigas sai com o piso (`_pegada_poltronas`: a pegada exata
#   delas, com a sombra, desenhando-as de novo num quadro neutro).
# - `_tracejados_zona`: os traços das projeções que passam na zona de novo por cima, em preto ou branco pelo fundo.
PISO_TA = {"fontes_px": [(1526, 358, 1580, 556), (1885, 884, 2155, 924)], "p_px": 24, "salto": 14, "suave_px": 2.0,
           "tom_tol": 28}
# a sombra das mesas de tampo grande (a de jantar, a de centro da sala de estar): mais curta e mais leve que a dos jogos
SOMBRA_MESA_TA = [{"dx_m": -0.05, "dy_m": 0.05, "sig_m": 0.06, "forca": 0.24},
                  {"dx_m": -0.015, "dy_m": 0.015, "sig_m": 0.02, "forca": 0.22}]
POLTRONA_LIMPA_TA = {"beira_px": 3, "liso_px": 1.4, "escurecer": 0.10}


def _membrana(c, dominio, fixo, reg=1e-4):
    """A função harmônica em `dominio` (bool) que vale `c` (h x w x n) nos px de `fixo` vizinhos dele; onde o vizinho não
    é nem domínio nem fixo, a borda é livre."""
    from scipy import sparse
    from scipy.sparse.linalg import splu
    H, W = dominio.shape
    ys, xs = np.nonzero(dominio)
    n = len(ys)
    idx = -np.ones((H, W), np.int64)
    idx[ys, xs] = np.arange(n)
    diag = np.full(n, reg)
    b = np.zeros((n, c.shape[2]))
    linhas, colunas = [], []
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        yy, xx = ys + dy, xs + dx
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        yy, xx = np.clip(yy, 0, H - 1), np.clip(xx, 0, W - 1)
        j = np.where(ok, idx[yy, xx], -1)
        viz = j >= 0
        linhas.append(np.nonzero(viz)[0])
        colunas.append(j[viz])
        diag += viz
        f = ok & ~viz & fixo[yy, xx]
        diag += f
        b[f] += c[yy[f], xx[f]]
    borda = fixo & ~dominio
    b += reg * (c[borda].mean(axis=0) if borda.any() else 0)
    nv = sum(len(v) for v in linhas)
    A = sparse.csc_matrix((np.concatenate([-np.ones(nv), diag]),
                           (np.concatenate(linhas + [np.arange(n)]), np.concatenate(colunas + [np.arange(n)]))),
                          shape=(n, n))
    lu = splu(A)
    out = np.zeros(c.shape, np.float32)
    out[ys, xs] = np.stack([lu.solve(b[:, k]) for k in range(c.shape[2])], axis=1)
    return out


def piso_refeito(img, zona, semente, q=None):
    """O travertino de novo na `zona` (bool, no quadro): o tecido das fontes, emendado ao piso de fora pela membrana."""
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import texturas
    q = q or PISO_TA
    H, W = zona.shape
    ys, xs = np.nonzero(zona)
    y0, y1, x0, x1 = max(ys.min() - 2, 0), min(ys.max() + 3, H), max(xs.min() - 2, 0), min(xs.max() + 3, W)
    h, w = y1 - y0, x1 - x0
    fontes = []
    for a, b, c, d in q["fontes_px"]:
        f_ = img[b:d, a:c]
        fontes += [f_, np.ascontiguousarray(f_[:, ::-1])]
    tec = texturas.quilting(fontes, h, w, p=q["p_px"], sobra=max(3, q["p_px"] // 3),
                            rng=np.random.default_rng(semente))[:h, :w].astype(np.float32)
    I = img[y0:y1, x0:x1].astype(np.float32)
    Z = zona[y0:y1, x0:x1]
    # a borda que vale: o piso de fora (perto do tom das fontes; sem as paredes, as plantas e os móveis), sem os traços e os
    # pontos (os px que fogem do material em volta)
    med = np.median(np.concatenate([f_.reshape(-1, 3) for f_ in fontes]).astype(np.float32), axis=0)
    fixo = ~Z & ~_salientes(img[y0:y1, x0:x1], k=21, lim=q["salto"]) & (np.abs(I - med).max(axis=2) < q["tom_tol"])
    V = fixo.astype(np.float32)
    s = q["suave_px"]
    c = cv2.GaussianBlur((I - tec) * V[..., None], (0, 0), s) / np.maximum(cv2.GaussianBlur(V, (0, 0), s),
                                                                           1e-3)[..., None]
    novo = np.clip(np.round(tec + _membrana(c, Z, fixo)), 0, 255).astype(np.uint8)
    out = img.copy()
    reg = out[y0:y1, x0:x1]
    reg[Z] = novo[Z]
    return out


def _paredes_fixas(Q, forma):
    """O que nunca é piso refeito: as paredes e os pilares do PDF."""
    m = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill") is not None, ss=2) > 0.02
    return cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)


def _plantas(img, perto=4):
    I8 = img.astype(np.int16)
    m = (I8[..., 1] - I8[..., 2] > 6) & (I8[..., 1] > I8[..., 0])
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    return cv2.dilate(m, np.ones((2 * perto + 1,) * 2, np.uint8)).astype(bool)


def _dilatar(m, px):
    return cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1,) * 2)).astype(bool)


_MODELO_LIMPO = {}


def _modelo_limpo(q=None):
    """(cor, alfa) da poltrona padrão com o contorno limpo."""
    import final3840_casae as E
    q = q or POLTRONA_LIMPA_TA
    chave = tuple(sorted(q.items()))
    if chave in _MODELO_LIMPO:
        return _MODELO_LIMPO[chave]
    cor, a = E._modelo_poltrona_1p(E.POLTRONAS_TE)
    p = 4
    a = np.pad(a, p)
    cor = np.pad(cor, ((p, p), (p, p), (0, 0)), mode="edge")
    ms = cv2.GaussianBlur((a > 0.5).astype(np.float32), (0, 0), q["liso_px"]) > 0.5
    n, lab, st, _ = cv2.connectedComponentsWithStats(ms.astype(np.uint8))
    ms = lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    b = q["beira_px"]
    dentro = cv2.erode(ms.astype(np.uint8), np.ones((2 * b + 1,) * 2, np.uint8)).astype(bool)
    _, rot = cv2.distanceTransformWithLabels((~dentro).astype(np.uint8), cv2.DIST_L2, 5,
                                             labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(dentro)
    idx = np.zeros(rot.max() + 1, int)
    idx[rot[ys, xs]] = np.arange(len(ys))
    c2 = cor.copy()
    fora = ~dentro
    c2[fora] = cor[ys[idx[rot[fora]]], xs[idx[rot[fora]]]]
    d = cv2.distanceTransform(ms.astype(np.uint8), cv2.DIST_L2, 5)
    t = np.clip(d / (b + 1.5), 0, 1)[..., None]
    c2 = np.where(dentro[..., None], cor, cv2.GaussianBlur(c2 * (1 - t) + cor * t, (0, 0), 0.8))
    c2 = c2 * (1 - q["escurecer"] * np.exp(-((d - 0.5) / 1.2) ** 2))[..., None]
    al = np.clip(cv2.GaussianBlur(ms.astype(np.float32), (0, 0), 0.55), 0, 1)
    yy, xx = np.nonzero(al > 0.01)
    res = (c2[yy.min():yy.max() + 1, xx.min():xx.max() + 1].astype(np.float32),
           al[yy.min():yy.max() + 1, xx.min():xx.max() + 1].astype(np.float32))
    _MODELO_LIMPO[chave] = res
    return res


def poltronas_limpas_ta(Q, img, pecas):
    """As poltronas (como em `revisao_casaa_2910.poltronas_ta`: nome, camada, retângulo pt, frente, lado pt) no modelo
    limpo, com a sombra e o contato da Casa E."""
    import final3840_casae as E
    import retoque_terreo_casae as RT
    qe = E.POLTRONAS_TE
    out = img.astype(np.float32)
    cor, a_m = _modelo_limpo()
    fx, fy = qe["modelo"]["frente"]
    for nome, _, r, (dx, dy), t_pt in pecas:
        (ax, ay), (bx_, by) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        cx, cy = (ax + bx_) / 2, (ay + by) / 2
        t = t_pt * Q.px_m / 56.69 if t_pt else max(bx_ - ax, by - ay)
        ang = np.degrees(np.arctan2(dx, dy) - np.arctan2(fx, fy))
        c2, a2 = E._girar_peca(cor, a_m, t / max(a_m.shape), ang)
        RT.pousar_planta(out, c2, a2, float(cx), float(cy), t, qe["sombra"])
        RT.pousar_planta(out, c2, a2, float(cx), float(cy), t, qe["sombra_contato"])
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _pecas_poltronas(nomes, trocas=None):
    import revisao_casaa_2910 as RA
    trocas = trocas or {}
    return [(p[0], p[1], p[2]) + trocas.get(p[0], (p[3], p[4])) for p in RA.POLTRONAS_TA["Terreo"]["pecas"]
            if p[0] in nomes]


def _pegada_poltronas(Q, nomes, forma):
    """A pegada das poltronas da final (as da revisão, com a sombra): desenhadas de novo num quadro neutro."""
    import revisao_casaa_2910 as RA
    base = np.full(forma + (3,), 128, np.uint8)
    r = RA.poltronas_ta(Q, base, q=dict(RA.POLTRONAS_TA["Terreo"], pecas=_pecas_poltronas(nomes)))
    return np.abs(r.astype(np.int16) - 128).max(axis=2) > 1


def _pecas_pdf(Q, pecas, forma, ss=4):
    """A máscara (0..1) das peças do PDF (camada, retângulo pt): o preenchimento de cada uma."""
    m = np.zeros(forma, np.float32)
    for camada, r in pecas:
        m = np.maximum(m, _mascara_ret(Q, camada, r, forma, ss=ss))
    return m


def _outros_moveis(Q, forma, fora_pt, folga_px=2):
    """Os móveis do PDF que não são refeitos (os de fora das caixas `fora_pt`), com `folga_px`: ficam como estão."""
    import revisao_casaa_2910 as RA

    def dentro(r):
        return any(a - 1 <= r.x0 and r.x1 <= c + 1 and b - 1 <= r.y0 and r.y1 <= d + 1 for a, b, c, d in fora_pt)
    m = Q.preencher(lambda d: d.get("layer") in RA.CAMADAS_MOVEIS_TA and not dentro(d["rect"])
                    and d["rect"].width * d["rect"].height < 2.5 * 56.69 ** 2, ss=2) > 0.05
    return _dilatar(m, folga_px)


def _tracejados_zona(Q, img, zona):
    """Os traços das projeções (DOC_LINHAS E PROJEÇÕES) que passam na `zona`, de novo por cima, em preto ou branco pelo
    fundo, só dentro dela (fora, os mesmos traços já estão na final)."""
    par = FA.paredes_pdf(Q)
    H, W = zona.shape
    tracos = []
    for _, _, segs in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"]):
        for sg in segs:
            pts = [Q.p2q(sg[0] + (sg[2] - sg[0]) * t, sg[1] + (sg[3] - sg[1]) * t) for t in np.linspace(0, 1, 7)]
            pts = [(int(np.clip(u, 0, W - 1)), int(np.clip(v, 0, H - 1))) for u, v in pts]
            if any(zona[v, u] for u, v in pts) and par[pts[3][1], pts[3][0]] <= 0.5:
                tracos.append(sg)
    if not tracos:
        return img
    novo, _ = T.preto_branco(Q, img, tracos)
    m = cv2.GaussianBlur(_dilatar(zona, 3).astype(np.float32), (0, 0), 1.0)[..., None]
    return np.clip(np.round(img * (1 - m) + novo * m), 0, 255).astype(np.uint8)


def _tapete_novo(Q, img, tap, cor, semente, q, zona=None):
    """O tapete (`tap`, 0..1 no quadro) por cima do piso: o tom `cor`, a trama da biblioteca, a faixa da borda um tom
    abaixo e a sombra curta da espessura dele no piso."""
    ys, xs = np.nonzero(tap > 0.001)
    y0, y1, x0, x1 = ys.min() - 4, ys.max() + 5, xs.min() - 4, xs.max() + 5
    t = tap[y0:y1, x0:x1]
    h, w = t.shape
    trama = _trama(Q, h, w, semente)
    dt = cv2.distanceTransform((t > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    faixa = np.where(dt > 0, np.clip(1 - (dt - q["faixa_m"] * Q.px_m) / 1.0, 0, 1), 0)
    tapete = np.float32(cor)[None, None, :] * (trama * (1 - q["faixa"] * faixa))[..., None]
    sb = cv2.GaussianBlur(cv2.warpAffine(t, np.float32([[1, 0, -1.2], [0, 1, 1.2]]), (w, h)), (0, 0), 1.0)
    piso = img[y0:y1, x0:x1].astype(np.float32) * (1 - q["borda_sombra"] * sb * (1 - t))[..., None]
    novo = piso * (1 - t[..., None]) + tapete * t[..., None]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    return out


def _cor_tapete(img, tap, ocupado):
    """O tom do tapete da final: a mediana do miolo dele, longe das peças."""
    miolo = cv2.erode((tap > 0.99).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~_dilatar(ocupado, 8)
    return np.median(img[miolo].astype(np.float32), axis=0)


def _relatorio(nome, zona):
    print(f"    {nome}: piso refeito em {int(zona.sum())} px")


# 13a. O estar sob a projeção da varanda: as 2 poltronas em X e a mesinha redonda entre elas (no lugar do borrão e do
# caco cinza ao lado).
PROJECAO_TA = {"poltronas": ("varanda, sob a projeção, de cima", "varanda, sob a projeção, de baixo"),
               "mesinha": ("DOC_TEXTOS", (1527.6, 927.7, 1547.4, 947.5)), "mesinha_tom": (100, 134, 172),
               "cacos_px": [(1705, 744, 1736, 760)], "margem_px": 10, "semente": 2918}


def projecao_varanda_ta(Q, img, q=None):
    q = q or PROJECAO_TA
    forma = img.shape[:2]
    pecas = _pecas_poltronas(q["poltronas"])
    peg = _pegada_poltronas(Q, q["poltronas"], forma)
    mes = _pecas_pdf(Q, [q["mesinha"]], forma) > 0.02
    caco = np.zeros(forma, bool)
    for x0, y0, x1, y1 in q["cacos_px"]:
        caco[y0:y1, x0:x1] = True
    zona = _dilatar(peg | _dilatar(mes, 6) | caco, q["margem_px"]) & ~_paredes_fixas(Q, forma)
    zona &= ~_outros_moveis(Q, forma, [p[2] for p in pecas] + [q["mesinha"][1]])
    out = piso_refeito(img, zona, q["semente"])
    out = _peca_madeira_pdf(Q, out, q["mesinha"][0], q["mesinha"][1], q["mesinha_tom"], 136.0, q["semente"] + 1)
    out = poltronas_limpas_ta(Q, out, pecas)
    out = _tracejados_zona(Q, out, zona)
    _relatorio("estar sob a projeção da varanda (2 poltronas e a mesinha de madeira)", zona)
    return out


# 13b. A sala de estar: o tapete redondo do PDF de novo (o miolo com a trama, a faixa da borda e a sombra curta), o
# sofá curvo estofado de novo por cima dele, a mesa de centro no contorno do PDF (o tom da da final, com a borda nítida,
# o chanfro e a sombra macia; a da final, de beira borrada e serrilhada, sai com o piso),
# as 3 mesinhas de madeira (as 2 redondas e a de cantos arredondados na ponta do sofá) e as 3 poltronas limpas (a da
# direita girada como no PDF, de frente para a mesa de centro).
SALA_ESTAR_TA = {"tapete": ("ARQ_MOBILIÁRIO", (1699.0, 590.2, 1925.7, 816.7)), "sofa": "sofá curvo da sala de estar",
                 "mesa_pt": (1783.5, 688.2, 1851.4, 728.0), "mesa_folga_px": 10, "mesa_rb": 18,
                 "mesinhas": [("DOC_TEXTOS", (1842.4, 632.7, 1862.2, 652.6)),
                              ("DOC_TEXTOS", (1796.1, 763.5, 1815.9, 783.3)),
                              ("DOC_TEXTOS", (1732.8, 686.0, 1757.1, 707.8))],
                 "mesinha_tom": (100, 134, 172),
                 "poltronas": ("sala de estar, à direita do tapete", "sala de estar, embaixo, à esquerda",
                               "sala de estar, embaixo, à direita"),
                 "giro": {"sala de estar, à direita do tapete": ((-0.71, 0.71), 47.0)},
                 "margem_px": 14, "semente": 2917, "faixa_m": 0.035, "faixa": 0.06, "borda_sombra": 0.16}


def _peca_da_final(img, caixa, cor_fundo, rb_min):
    """A peça (uma mesa da final, mais rosada que o fundo) na `caixa` px: (alfa, cor) no quadro. A cor da beira é a do
    miolo mais perto (sem o fundo antigo misturado); o alfa, o da silhueta alisada, com a borda nítida."""
    x0, y0, x1, y1 = caixa
    reg = img[y0:y1, x0:x1].astype(np.float32)
    rb = reg[..., 2] - reg[..., 0]
    rb0 = float(cor_fundo[2] - cor_fundo[0])
    m = rb > rb0 + rb_min
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    m = lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    cheio = m.astype(np.uint8).copy()
    cv2.floodFill(cheio, np.zeros((cheio.shape[0] + 2, cheio.shape[1] + 2), np.uint8), (0, 0), 2)
    m = cheio != 2
    miolo = cv2.erode(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    # o contorno nítido: a silhueta alisada a 4 x e levada ao quadro em área (sem a beira borrada do render)
    h, w = m.shape
    m4 = cv2.GaussianBlur(cv2.resize(m.astype(np.float32), (w * 4, h * 4), interpolation=cv2.INTER_LINEAR), (0, 0),
                          3.0) > 0.5
    al = cv2.resize(m4.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    _, rot = cv2.distanceTransformWithLabels((~miolo).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(miolo)
    idx = np.zeros(rot.max() + 1, int)
    idx[rot[ys, xs]] = np.arange(len(ys))
    cor = reg.copy()
    fora = ~miolo
    cor[fora] = reg[ys[idx[rot[fora]]], xs[idx[rot[fora]]]]
    A = np.zeros(img.shape[:2], np.float32)
    C = np.zeros(img.shape, np.float32)
    A[y0:y1, x0:x1], C[y0:y1, x0:x1] = al, cor
    return A, C


def _colar_peca(Q, out, A, C, folga=None, sombras=None):
    """A peça (alfa A, cor C, no quadro) por cima, com a sombra macia no piso."""
    folga = folga or SOMBRA_FOLGA_PX
    ys, xs = np.nonzero(A > 0.001)
    X0, Y0, X1, Y1 = xs.min() - folga, ys.min() - folga, xs.max() + folga + 1, ys.max() + folga + 1
    a = A[Y0:Y1, X0:X1]
    out = _sombra_piso(out, X0, Y0, a, Q.px_m, sombras)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + C[Y0:Y1, X0:X1] * a[..., None]), 0, 255
                                ).astype(np.uint8)
    return out


def _mesa_contorno_pdf(Q, out, camada, r, cor, sombras=None, liso_px=1.2, ss=8):
    """A mesa pelo contorno do PDF (só traços: os pontos deles em volta do centro, pela ordem do ângulo), alisado, no tom
    `cor`, com o chanfro e a sombra macia; a borda nítida, antisserrilhada."""
    import revisao_casab_2910 as RB
    pts = [(p.x, p.y) for d in Q.desenhos if d.get("layer") == camada and d["type"] == "s"
           and r[0] - 0.6 <= d["rect"].x0 and d["rect"].x1 <= r[2] + 0.6
           and r[1] - 0.6 <= d["rect"].y0 and d["rect"].y1 <= r[3] + 0.6
           for it in d["items"] for p in it[1:] if hasattr(p, "x")]
    pts = np.float32(pts)
    c = pts.mean(axis=0)
    poli = np.float32([Q.p2q(*p) for p in pts[np.argsort(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))]])
    f = SOMBRA_FOLGA_PX
    X0, Y0 = int(poli[:, 0].min()) - f, int(poli[:, 1].min()) - f
    X1, Y1 = int(np.ceil(poli[:, 0].max())) + f, int(np.ceil(poli[:, 1].max())) + f
    w, h = X1 - X0, Y1 - Y0
    M = np.zeros((h * ss, w * ss), np.uint8)
    cv2.fillPoly(M, [np.int32(np.round((poli - (X0, Y0)) * ss))], 255)
    M = (cv2.GaussianBlur(M.astype(np.float32) / 255, (0, 0), liso_px * ss) > 0.5).astype(np.float32)
    out = _sombra_piso(out, X0, Y0, cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA), Q.px_m, sombras)
    cor_m = np.float32(cor)[None, None, :] * RB._relevo_tb(M, Q.px_m, ss)[..., None]
    return _pintar(out, X0, Y0, w, h, ss, M, cor_m)


def _estofado(Q, img, nome):
    import revisao_casaa_2910 as RA
    import revisao_casab_2910 as RB
    for q in RA.ESTOFADOS_TA["Terreo"]:
        es = [e for e in q["estofados"] if e[0] == nome]
        if es:
            return RB.estofados_pdf_tb(Q, img, dict(q, estofados=es), "Terreo")
    raise KeyError(nome)


def sala_estar_ta(Q, img, q=None):
    import revisao_casaa_2910 as RA
    q = q or SALA_ESTAR_TA
    forma = img.shape[:2]
    tap = _mascara_ret(Q, q["tapete"][0], q["tapete"][1], forma)
    r_sofa = next(e[1][0] for qq in RA.ESTOFADOS_TA["Terreo"] for e in qq["estofados"] if e[0] == q["sofa"])
    sofa = _mascara_ret(Q, "ARQ_LAYOUT HUMANIZAÇÃO", r_sofa, forma) > 0.02
    mes = _pecas_pdf(Q, q["mesinhas"], forma) > 0.02
    peg = _pegada_poltronas(Q, q["poltronas"], forma)
    pecas = _pecas_poltronas(q["poltronas"], q["giro"])
    (mx0, my0), (mx1, my1) = Q.p2q(*q["mesa_pt"][:2]), Q.p2q(*q["mesa_pt"][2:])
    f = q["mesa_folga_px"]
    caixa_mesa = (int(mx0) - f, int(my0) - f, int(np.ceil(mx1)) + f, int(np.ceil(my1)) + f)
    ocupado = sofa | mes | peg
    ocupado[caixa_mesa[1]:caixa_mesa[3], caixa_mesa[0]:caixa_mesa[2]] = True
    cor_t = _cor_tapete(img, tap, ocupado)
    A, C = _peca_da_final(img, caixa_mesa, cor_t, q["mesa_rb"])
    zona = _dilatar((tap > 0.02) | sofa | mes | peg | (A > 0.01), q["margem_px"])
    zona &= ~_paredes_fixas(Q, forma) & ~_plantas(img)
    zona &= ~_outros_moveis(Q, forma, [q["tapete"][1], r_sofa, q["mesa_pt"]] + [r for _, r in q["mesinhas"]]
                            + [p[2] for p in pecas])
    out = piso_refeito(img, zona, q["semente"])
    out = _tapete_novo(Q, out, tap, cor_t, q["semente"] + 1, q)
    out = _estofado(Q, out, q["sofa"])
    cor_mesa = np.median(C[A > 0.99], axis=0)
    out = _mesa_contorno_pdf(Q, out, "ARQ_LAYOUT HUMANIZAÇÃO", q["mesa_pt"], cor_mesa, SOMBRA_MESA_TA)
    for i, (camada, r) in enumerate(q["mesinhas"]):
        out = _peca_madeira_pdf(Q, out, camada, r, q["mesinha_tom"], 25.0 + 37 * i, 2913 + i)
    out = poltronas_limpas_ta(Q, out, pecas)
    out = _tracejados_zona(Q, out, zona)
    _relatorio("sala de estar (o tapete redondo, o sofá, a mesa de centro, 3 mesinhas e 3 poltronas)", zona)
    return out


# 13c. A sala de estar em X: o piso de todo o estar refeito (com a mancha clara entre as poltronas de baixo), a mesa
# triangular no contorno do PDF (o tom da da final, com a borda nítida) e as 4 poltronas limpas.
ESTAR_X_TA = {"poltronas": ("sala de estar, em X, no alto à esquerda", "sala de estar, em X, no alto à direita",
                            "sala de estar, em X, embaixo à direita", "sala de estar, em X, embaixo à esquerda"),
              "mesa": ("ARQ_MOBILIÁRIO", (1777.1, 914.9, 1819.3, 955.4)), "mesa_folga_px": 8, "mesa_rb": 18,
              "margem_px": 6, "semente": 2919}


def estar_x_ta(Q, img, q=None):
    q = q or ESTAR_X_TA
    forma = img.shape[:2]
    pecas = _pecas_poltronas(q["poltronas"])
    peg = _pegada_poltronas(Q, q["poltronas"], forma)
    rets = [p[2] for p in pecas]
    (x0, y0), (x1, y1) = Q.p2q(min(r[0] for r in rets), min(r[1] for r in rets)), \
        Q.p2q(max(r[2] for r in rets), max(r[3] for r in rets))
    caixa = np.zeros(forma, bool)
    caixa[int(y0):int(np.ceil(y1)), int(x0):int(np.ceil(x1))] = True
    # a mesa triangular da final sai com o piso e volta no contorno do PDF, no tom dela
    (mx0, my0), (mx1, my1) = Q.p2q(*q["mesa"][1][:2]), Q.p2q(*q["mesa"][1][2:])
    f = q["mesa_folga_px"]
    caixa_mesa = (int(mx0) - f, int(my0) - f, int(np.ceil(mx1)) + f, int(np.ceil(my1)) + f)
    fundo = np.median(img[caixa & ~peg].astype(np.float32), axis=0)
    A, C = _peca_da_final(img, caixa_mesa, fundo, q["mesa_rb"])
    zona = (_dilatar(peg, q["margem_px"]) | caixa | _dilatar(A > 0.01, 3)) & ~_paredes_fixas(Q, forma)
    zona &= ~_outros_moveis(Q, forma, rets + [q["mesa"][1]])
    out = piso_refeito(img, zona, q["semente"])
    out = _mesa_contorno_pdf(Q, out, q["mesa"][0], q["mesa"][1], np.median(C[A > 0.99], axis=0), SOMBRA_MESA_TA)
    out = poltronas_limpas_ta(Q, out, pecas)
    out = _tracejados_zona(Q, out, zona)
    _relatorio("sala de estar em X (a mesa triangular e as 4 poltronas)", zona)
    return out


# 13d. O escritório: a mesa lateral do PDF (dois tampos redondos, um sobre o outro, no lugar do borrão) em madeira, no
# tom e no sobretom, com a sombra macia, e a poltrona limpa.
ESCRITORIO_TA = {"poltrona": "escritório",
                 "mesas": [("ARQ_LAYOUT HUMANIZAÇÃO", (2270.2, 753.0, 2287.2, 770.0), (100, 134, 172)),
                           ("ARQ_LAYOUT HUMANIZAÇÃO", (2262.1, 763.3, 2279.1, 780.3), (134, 168, 202))],
                 "margem_px": 10, "semente": 2920}


def escritorio_ta(Q, img, q=None):
    q = q or ESCRITORIO_TA
    forma = img.shape[:2]
    pecas = _pecas_poltronas((q["poltrona"],))
    peg = _pegada_poltronas(Q, (q["poltrona"],), forma)
    mes = _pecas_pdf(Q, [(c, r) for c, r, _ in q["mesas"]], forma) > 0.02
    zona = _dilatar(peg | _dilatar(mes, 5), q["margem_px"]) & ~_paredes_fixas(Q, forma)
    zona &= ~_outros_moveis(Q, forma, [p[2] for p in pecas] + [r for _, r, _ in q["mesas"]])
    out = piso_refeito(img, zona, q["semente"])
    for i, (camada, r, tom) in enumerate(q["mesas"]):
        out = _peca_madeira_pdf(Q, out, camada, r, tom, 20.0 + 50 * i, q["semente"] + 1 + i)
    out = poltronas_limpas_ta(Q, out, pecas)
    out = _tracejados_zona(Q, out, zona)
    _relatorio("escritório (a mesa lateral em dois tampos de madeira e a poltrona)", zona)
    return out


# 13e. A poltrona do terraço gourmet, junto aos brises (usuário: "rotacione 45º para a direita, apontando a poltrona para
# a mesa de centro. conforme o pdf", e depois: "você não fez a rotação da poltrona da varanda que eu te pedi" e "a
# poltrona fica proxima aos brises"): no PDF ela é girada, com o encosto no alto à esquerda e a frente para a mesa de
# centro, embaixo à direita; na final olhava para baixo. A antiga sai com o piso (`piso_refeito`) e a nova entra limpa,
# girada (`frente`), no lado `t_pt` (a caixa do PDF é a diagonal da peça girada).
GOURMET_POLTRONA_TA = {"nome": "terraço gourmet", "frente": (0.71, 0.71), "t_pt": 56.0, "margem_px": 8,
                       "semente": 2922}


def gourmet_poltrona_ta(Q, img, q=None):
    q = q or GOURMET_POLTRONA_TA
    forma = img.shape[:2]
    pecas = _pecas_poltronas((q["nome"],), {q["nome"]: (q["frente"], q["t_pt"])})
    peg = _pegada_poltronas(Q, (q["nome"],), forma)
    zona = _dilatar(peg, q["margem_px"]) & ~_paredes_fixas(Q, forma) & ~_outros_moveis(Q, forma, [pecas[0][2]])
    out = piso_refeito(img, zona, q["semente"])
    out = poltronas_limpas_ta(Q, out, pecas)
    _relatorio("terraço gourmet (a poltrona girada como no PDF, de frente para a mesa de centro)", zona)
    return out


# 13f. O banho do motorista (usuário: "remova as manchas marrom atras da porta e no contorno do vaso sanitario"): o fio
# marrom em volta do vaso (a borda do render) e o granito do quarto que entrava no vão da porta e sob a folha aberta saem
# com o Bege Bahia do próprio banho (`piso_refeito` com as fontes do banho); o vaso volta com o miolo dele, a beira na
# cor do miolo (antisserrilhada pelo PDF) e a sombra de contato leve. A bancada e a folha da porta ficam.
BANHO_MOTORISTA_TA = {"vaso": ("ARQ_LOUÇAS E METAIS", (2071.5, 1381.2, 2092.8, 1412.3)),
                      "bancada": ("ARQ_BANCADAS", (2103.6, 1381.2, 2143.3, 1403.8)),
                      "caixas_px": [(2383, 1251, 2392, 1301), (2338, 1297, 2392, 1303)],
                      "folha_px": (2341, 1293, 2385, 1297), "vaso_px": 4, "miolo_px": 2, "aro": 0.14,
                      "fontes_px": [(2302, 1252, 2378, 1290)], "p_px": 16, "semente": 2923,
                      "sombras": [{"dx_m": -0.02, "dy_m": 0.02, "sig_m": 0.02, "forca": 0.25}]}


def banho_motorista_ta(Q, img, q=None):
    q = q or BANHO_MOTORISTA_TA
    forma = img.shape[:2]
    vaso = _mascara_ret(Q, q["vaso"][0], q["vaso"][1], forma)
    bancada = _dilatar(_mascara_ret(Q, q["bancada"][0], q["bancada"][1], forma) > 0.02, 1)
    miolo = cv2.erode((vaso > 0.99).astype(np.uint8), np.ones((2 * q["miolo_px"] + 1,) * 2, np.uint8)).astype(bool)
    zona = _dilatar(vaso > 0.02, q["vaso_px"]) & ~miolo
    for x0, y0, x1, y1 in q["caixas_px"]:
        zona[y0:y1, x0:x1] = True
    fx0, fy0, fx1, fy1 = q["folha_px"]
    folha = np.zeros(forma, bool)
    folha[fy0:fy1, fx0:fx1] = True
    zona &= ~_paredes_fixas(Q, forma) & ~bancada & ~folha
    # o vaso: o miolo da final, levado à beira
    ys, xs = np.nonzero(vaso > 0.001)
    X0, Y0, X1, Y1 = xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    m_ = miolo[Y0:Y1, X0:X1]
    _, rot = cv2.distanceTransformWithLabels((~m_).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    yy, xx = np.nonzero(m_)
    idx = np.zeros(rot.max() + 1, int)
    idx[rot[yy, xx]] = np.arange(len(yy))
    cor = reg.copy()
    cor[~m_] = reg[yy[idx[rot[~m_]]], xx[idx[rot[~m_]]]]
    # a beira um pouco mais escura (o contorno da louça, sem o fio marrom)
    d_ = cv2.distanceTransform((vaso[Y0:Y1, X0:X1] > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    cor *= (1 - q["aro"] * np.exp(-((d_ - 0.5) / 1.0) ** 2))[..., None]
    A, C = np.zeros(forma, np.float32), np.zeros(img.shape, np.float32)
    A[Y0:Y1, X0:X1], C[Y0:Y1, X0:X1] = vaso[Y0:Y1, X0:X1], cor
    out = piso_refeito(img, zona, q["semente"], dict(PISO_TA, fontes_px=q["fontes_px"], p_px=q["p_px"]))
    out = _colar_peca(Q, out, A, C, sombras=q["sombras"])
    _relatorio("banho do motorista (sem o marrom em volta do vaso, no vão da porta e sob a folha)", zona)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 14. O matelassê nas camas (usuário: "faltou os matelassê das camas. adicione-a em todas"): o mesmo das camas da Casa B
# (`revisao_casab_2910.MATELASSE_TB`: o pesponto em losangos de 12 cm na grade do PDF e o relevo de cada losango, com a
# luz do alto à direita), multiplicado sobre o edredom de cada cama da Casa A (a cama do motorista, no Térreo, e as seis
# do 1º Pavimento, `ajustes_casaa.CAMA_MOTORISTA` e `CAMAS_1PAV`): da dobra do lençol aos pés, dentro do colchão (a
# `borda` das camas); as faixas e almofadas bordô, os travesseiros e a dobra ficam lisos (o bordô é achado pela cor, com
# `folga_px`), e os traços escuros (o tracejado que passa sobre a cama da suíte master) também.
MATELASSE_TA = {"folga_px": 1.5, "bordo_dr": 18, "escuro": 110}


def matelasse_ta(Q, img, q=None):
    import ajustes_casaa as AJ
    import revisao_casab_2910 as RB
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import elementos
    q = q or MATELASSE_TA
    qb = RB.MATELASSE_TB
    camas = AJ.CAMA_MOTORISTA if Q.chave == "Terreo" else AJ.CAMAS_1PAV
    k = qb["ss"]
    out = img.astype(np.float32)
    (ax, ay), (bx, by) = Q.q2p(0, 0), Q.q2p(1000, 1000)
    sx_, sy_ = (bx - ax) / 1000, (by - ay) / 1000
    passo = qb["passo_m"] * 56.69
    feitas = []
    for nome, r, cab, tipo in camas["camas"]:
        p_ = elementos.ROUPA_CAMA[tipo]
        e = camas["borda"]
        (u0, v0), (u1, v1) = Q.p2q(r[0] + e, r[1] + e), Q.p2q(r[2] - e, r[3] - e)
        X0, Y0, X1, Y1 = int(np.floor(u0)) - 1, int(np.floor(v0)) - 1, int(np.ceil(u1)) + 2, int(np.ceil(v1)) + 2
        w, h = X1 - X0, Y1 - Y0
        xs = X0 + (np.arange(w * k)[None, :] + 0.5) / k
        ys = Y0 + (np.arange(h * k)[:, None] + 0.5) / k
        xpt, ypt = ax + xs * sx_, ay + ys * sy_
        dentro = ((xs >= u0) & (xs <= u1) & (ys >= v0) & (ys <= v1)).astype(np.float32)
        X = {"esq": (xs - u0), "dir": (u1 - xs), "baixo": (v1 - ys), "cima": (ys - v0)}[cab] / Q.px_m
        X = np.broadcast_to(X, dentro.shape)
        zona = dentro * (X >= p_["dobra"][1] + qb["folga_m"])
        # o bordô (as faixas, a peseira) e os traços escuros ficam lisos
        reg = img[Y0:Y1, X0:X1].astype(np.int16)
        liso = ((reg[..., 2] - reg[..., 1] > q["bordo_dr"]) & (reg[..., 2] > 70)) | (reg.mean(axis=2) < q["escuro"])
        kf = 2 * int(np.ceil(q["folga_px"])) + 1
        liso = cv2.dilate(liso.astype(np.uint8), np.ones((kf, kf), np.uint8))
        liso = cv2.resize(liso, (w * k, h * k), interpolation=cv2.INTER_NEAREST).astype(bool)
        zona = zona * ~liso
        u, v = (xpt + ypt) / passo, (xpt - ypt) / passo
        lp = qb["largura_pt"]
        pesp = np.maximum(np.exp(-((u - np.round(u)) * passo / lp) ** 2), np.exp(-((v - np.round(v)) * passo / lp) ** 2))
        alt = np.minimum(np.abs(u - np.round(u)), np.abs(v - np.round(v))) * 2
        alt = cv2.GaussianBlur(np.clip(alt, 0, 1).astype(np.float32) ** 0.6, (0, 0), 0.3 * k)
        gy, gx = np.gradient(alt * passo * Q.px_m / 56.69 * k)
        fator = (1 - qb["pesponto"] * pesp) * (1 + qb["acolchoado"] * np.clip(gx * 0.7 - gy * 0.7, -1, 1))
        zona = cv2.GaussianBlur(zona.astype(np.float32), (0, 0), 0.4 * k)
        f = cv2.resize((1 + zona * (fator - 1)).astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
        out[Y0:Y1, X0:X1] *= f[..., None]
        feitas.append(nome)
    print(f"    matelassê no edredom das camas ({'; '.join(feitas)})")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# A sequência
def pedidos_terreo_ta(img):
    """O Térreo com os pedidos; devolve a final nova e o Térreo sem rótulos de antes e de depois (para o nublado do 1º
    Pavimento, que não leva rótulos)."""
    Q = FA.QuadroA("Terreo")
    sem_antes = rotulos_tirar_ta(Q, img)[0]
    out = despensa_ta(Q, img)                      # antes dos rótulos: o DESPENSA estava sobre o armário
    out, tirados, aj = rotulos_tirar_ta(Q, out)
    out = paredes_limpas(Q, out)
    out = janelas_ta(Q, out)
    out = ilha_ta(Q, out)
    out = piscina_ta(Q, out)
    out = tracejados_ta(Q, out, etapa="apagar")
    out = borda_pista_ta(Q, out)
    out = tracejados_ta(Q, out, etapa="desenhar")
    out = box_varanda_ta(Q, out)
    out = espreguicadeiras_ta(Q, out)
    out = jantar_marrom_ta(Q, out)
    out = varanda_estar_ta(Q, out)
    out = projecao_varanda_ta(Q, out)
    out = sala_estar_ta(Q, out)
    out = estar_x_ta(Q, out)
    out = escritorio_ta(Q, out)
    out = gourmet_poltrona_ta(Q, out)
    out = banho_motorista_ta(Q, out)
    out = matelasse_ta(Q, out)
    sem_depois = out.copy()
    out = rotulos_centro_ta(Q, out, tirados, aj)
    return out, sem_antes, sem_depois


# O 1º Pavimento mostra o Térreo nublado fora da pegada e nos vazios (`rotulos_casaa.nublar`). Onde o Térreo mudou (sem
# os rótulos; fora as linhas tracejadas novas da pista, `fora_px`, que o nublado não leva), entra a diferença entre o
# Térreo novo e o antigo, nublados: fora da pegada, somada; nos vazios (onde o branco multiplica o Térreo nublado), pela
# razão novo/antigo.
NUBLADO_1PAV_TA = {"limiar": 4, "folga_px": 5, "fora_px": [(1860, 1560, 3460, 1960)]}


def nublado_1pav_ta(img, t_velho, t_novo, q=None):
    import final3840_casaa_1pav as P1
    import rotulos_casaa as A
    from entorno_esmaecido import NUBLADO
    q = q or NUBLADO_1PAV_TA
    Q = FA.QuadroA("1Pavimento")
    P1.inicial(Q)

    def nublar(t):
        t = cv2.GaussianBlur(t.astype(np.float32), (0, 0), NUBLADO["desfoque"] * t.shape[1] / 3840)
        cinza = t.mean(axis=2, keepdims=True)
        t = cinza + (t - cinza) * NUBLADO["saturacao"]
        return 255 - (255 - t) * (1 - NUBLADO["clarear"])
    mud = np.abs(t_novo.astype(np.int16) - t_velho.astype(np.int16)).max(axis=2) > q["limiar"]
    for x0, y0, x1, y1 in q["fora_px"]:
        mud[y0:y1, x0:x1] = False
    k = 2 * q["folga_px"] + 1
    m = cv2.GaussianBlur(cv2.dilate(mud.astype(np.uint8), np.ones((k, k), np.uint8)).astype(np.float32), (0, 0), 2.0)
    pg = Q.pegada > 127
    a = np.maximum(cv2.GaussianBlur(pg.astype(np.float32), (0, 0), 1.0), pg)
    tv, tn = nublar(t_velho), nublar(t_novo)
    f = img.astype(np.float32)
    out = f + (tn - tv) * ((1 - a) * m)[..., None]
    vaz = (Q.janelas > 127) & (a > 0.5)
    raz = tn / np.maximum(tv, 1)
    mv = (m * vaz)[..., None]
    out = out * (1 - mv) + f * raz * mv
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    n = int((np.abs(out.astype(np.int16) - img.astype(np.int16)).max(axis=2) > 2).sum())
    print(f"    1º Pavimento: o Térreo nublado em volta e nos vazios refeito onde o Térreo mudou ({n} px)")
    _ = A
    return out


# Os antes/depois (caixas em px do quadro).
ANTES_DEPOIS_PEDIDOS_TA = {
    "Terreo": {"pista_borda_tracejados": (1880, 1560, 3450, 1950), "paredes_janelas_despensa": (1880, 1080, 2210, 1660),
               "box_banho_varanda": (1555, 1470, 1725, 1625), "espreguicadeiras_piscina": (1080, 480, 1500, 1090),
               "jantar_cadeiras": (1880, 885, 2175, 1075), "varanda_estar": (1530, 325, 1835, 625),
               "sala_estar_mesinhas_poltrona": (1835, 360, 2205, 650), "estar_x_mesinha": (1610, 625, 1870, 870),
               "ilha_varanda": (1460, 1235, 1790, 1335), "cama_motorista": (2370, 1095, 2475, 1255)},
    "1Pavimento": {"camas_matelasse": (1380, 300, 2520, 1610), "nublado_piscina": (1080, 480, 1500, 1090)},
    "Subsolo": {"nevoado_piscina": (1060, 470, 1520, 1100)}}


# Os da 2ª leva (os pedidos vendo a entrega), contra a final da 1ª (`--pasta_comparar`).
ANTES_DEPOIS_2A_TA = {
    "Terreo": {"estar_projecao_mesinha": (1640, 680, 1840, 840), "jantar_piso": (1880, 885, 2175, 1075),
               "sala_estar_tapete_poltronas": (1850, 360, 2200, 650), "varanda_estar_banco": (1530, 325, 1835, 625),
               "sala_estar_x": (1910, 650, 2125, 845), "escritorio_mesa_lateral": (2440, 470, 2620, 640),
               "terraco_gourmet_poltrona": (1240, 1270, 1400, 1430), "banho_motorista": (2290, 1200, 2400, 1310),
               "rotulos_garagem_motorista": (2080, 1080, 2920, 1720), "rotulos_servico": (1180, 1080, 2120, 1720)},
    "1Pavimento": {"nublado_estar": (1380, 300, 2250, 1110)}}


def antes_depois_pedidos_ta(chave, antes, depois, max_lado=1800, caixas=None, sufixo="2910b"):
    for nome, (x0, y0, x1, y1) in (caixas or ANTES_DEPOIS_PEDIDOS_TA)[chave].items():
        a, d = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        lado = (x1 - x0) <= (y1 - y0) * 1.3
        junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), d]) if lado else \
            np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), d])
        k = min(3.0, max_lado / max(junto.shape[:2]))
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
        arq = FA.CASA / "renders" / f"POE642_CasaA_PH_{chave}_{sufixo}_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {arq.name}")


def main():
    import argparse
    import revisao_casaa_2910 as RA
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta_antes", type=Path, default=None,
                    help="a pasta das finais de antes (por padrão, as próprias finais, sobrescritas)")
    ap.add_argument("--antes_subsolo", type=Path, required=True,
                    help="a final do Subsolo de antes da revisão de 29/10 (a que recebe o nevoado do Térreo novo)")
    ap.add_argument("--pasta_comparar", type=Path, default=None,
                    help="a pasta das finais da 1ª leva (para os antes e depois da 2ª leva, `_2910c_`)")
    a = ap.parse_args()
    finais = RA.FINAIS_TA
    antes = {k: cv2.imread(str(a.pasta_antes / v.name if a.pasta_antes else v)) for k, v in finais.items()}
    terreo, t_velho, t_novo = pedidos_terreo_ta(antes["Terreo"])
    um = nublado_1pav_ta(antes["1Pavimento"], t_velho, t_novo)
    um = matelasse_ta(FA.QuadroA("1Pavimento"), um)
    sub = RA.revisao_ta("Subsolo", cv2.imread(str(a.antes_subsolo)), terreo)
    for k, out in (("Terreo", terreo), ("1Pavimento", um), ("Subsolo", sub)):
        cv2.imwrite(str(finais[k]), out)
        print(finais[k])
        antes_depois_pedidos_ta(k, antes[k], out)
        if a.pasta_comparar and k in ANTES_DEPOIS_2A_TA:
            antes_depois_pedidos_ta(k, cv2.imread(str(a.pasta_comparar / finais[k].name)), out, caixas=ANTES_DEPOIS_2A_TA,
                                    sufixo="2910c")


if __name__ == "__main__":
    main()

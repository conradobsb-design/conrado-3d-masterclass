#!/usr/bin/env python3
"""O tom da piscina de referência em todas as piscinas (usuário, 28/10/26: "APLIQUE O TOM DA PISCINA NO TÉRREO TAMBÉM"
e "APLIQUE ESSE TOM DE PISCINA EM TODAS AS PISCINAS DE TODAS AS CASAS").

O tom é o do Subsolo da Casa E (`final3840_casae.PISCINA_E`, com a vista de cima da sauna do modelo 3D: "NOTE TAMBÉM O
TOM DA PISCINA QUE ADOTAREMOS"): a água turquesa (BGR ~168, 160, 42), as peças de 14,5 cm do Barlavento marcadas como
pastilhas e a rede clara das cáusticas. As piscinas dos Térreos (as das Casas A a D vêm dos renders de 2000 px com o
Barlavento sob a água verde-azulada clara de 15/10; a da Casa E, do retocado dela) trocam só a água, sem rodar de novo os
motores, como as cortinas (`cortinas_franzidas.py`):

- a água é achada pela cor (o miolo azul, `ciano`, em manchas de pelo menos `area_min` px, com os furos fechados) e vai
  até a beira quente (o Bege Bahia, a madeira: o azul abaixo do vermelho em `quente_br`), a até `beira_px` do miolo (a
  faixa clara e quase sem cor que o render deixou junto às bordas, na prainha da Casa D, entra); o que não é água fica
  como está: as bordas, as peças claras e neutras grandes dentro da água (as espreguiçadeiras: o que sobra da abertura
  de `peca_px`), os px de `proteger` (os vidros do Térreo da Casa E, pelo PDF);
- os traços escuros sobre a água (`escuro_rel`: os rótulos, os tracejados de projeção) ficam: cada px deles é separado
  da água antiga (a fração do traço pela luz entre a água de perto e o miolo do traço) e posto sobre a nova, sem halo;
- o desenho da água antiga fica: a luz relativa de cada px (as peças do Barlavento e o rejunte, os degraus da prainha e
  do spa, a sombra curta das bordas) passa ao turquesa com o contraste de `ganho` (o claro das cáusticas antigas, que vira
  rede nova, com `ganho_claro`);
- a sombra curta das beiras na água (`sombra`: força e alcance em px), que com a antiga chega à do Subsolo;
- por cima, a rede de cáusticas do Subsolo (`PISCINA_E["causticas"]`, no claro dele), longe das beiras (`causticas_px`).

Uso (da pasta POE642_CasaA/scripts/), uma planta por vez:
  python3 piscinas_turquesa.py A-Terreo | B-Terreo | C-Terreo | D-Terreo [--antes <png>]
A final é regravada no lugar (`--antes` guarda uma cópia da anterior). O Térreo da Casa E usa a mesma rotina na etapa
"piscina" do motor (`final3840_casae.passos_terreo`).

As bordas retas pelo PDF ("corrija as bordas deixando as perfeitas", na Casa A), sem trocar a água (`bordas_retas`):
  python3 piscinas_turquesa.py A-Terreo --bordas --rede <a final de antes do turquesa>
"""
import argparse
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))

TURQUESA = {"ciano": (22, 22, 100), "area_min": 1500, "beira_px": 8, "quente_br": (-14, -2), "peca_croma": 14,
            "peca_px": 9, "escuro_rel": (-0.40, -0.25), "ganho": 1.5, "ganho_claro": 0.6, "base": (0.45, 1.45),
            "causticas_px": (1.5, 4.0), "sombra": (0.22, 2.2), "px_m": 59.7, "semente": 2850}
FINAIS = {"A-Terreo": RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_rotulos.png",
          "B-Terreo": RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png",
          "C-Terreo": RAIZ / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png",
          "D-Terreo": RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png"}


def causticas(h, w, px_m, semente):
    """A rede clara das cáusticas (0 a 1), a mesma do Subsolo da Casa E (`final3840_casae.agua_e`)."""
    from final3840_casae import PISCINA_E
    q = PISCINA_E
    rng = np.random.default_rng(semente)
    c = np.zeros((h, w), np.float32)
    for esc, f in q["causticas"]:
        n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), esc * px_m * 0.3)
        n /= max(float(n.std()), 1e-6)
        c += f * np.exp(-(n / q["caustica_larg"]) ** 2)
    return np.clip(cv2.GaussianBlur(c, (0, 0), 0.6), 0, 1)


def turquesa(img, px_m=None, semente=None, q=None, proteger=None):
    """A água de `img` (BGR, uint8) no turquesa da referência; devolve (imagem, m² de água por mancha). `proteger`: os
    px que ficam como estão (bool, do tamanho da imagem: os vidros dentro da água, no Térreo da Casa E)."""
    from final3840_casae import PISCINA_E
    q = q or TURQUESA
    px_m = px_m or q["px_m"]
    semente = q["semente"] if semente is None else semente
    a = img.astype(np.float32)
    b, g, r = a[..., 0], a[..., 1], a[..., 2]
    dbr, dgr, bmin = q["ciano"]
    nucleo = (b - r > dbr) & (g - r > dgr) & (b > bmin)
    n, lab, st, _ = cv2.connectedComponentsWithStats(nucleo.astype(np.uint8), 8)
    out = a.copy()
    areas = []
    Y = a.mean(axis=2)
    alc = q["beira_px"]
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < q["area_min"]:
            continue
        x, y, w, h = st[i, :4]
        f = alc + 6
        x0, y0, x1, y1 = max(x - f, 0), max(y - f, 0), min(x + w + f, img.shape[1]), min(y + h + f, img.shape[0])
        nu = lab[y0:y1, x0:x1] == i
        reg_ = a[y0:y1, x0:x1]
        bb, gg, rr = b[y0:y1, x0:x1], g[y0:y1, x0:x1], r[y0:y1, x0:x1]
        yy = Y[y0:y1, x0:x1]
        croma = reg_.max(axis=2) - reg_.min(axis=2)
        # a mancha da água: o miolo azul com os furos fechados, até a beira quente (o Bege Bahia, a madeira), a até
        # `beira_px` dele (a faixa clara e quase sem cor que o render deixou junto às bordas, na prainha da Casa D, entra)
        r0 = ndimage.binary_fill_holes(cv2.morphologyEx(nu.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)))
        k = 2 * alc + 1
        viz = cv2.dilate(r0.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
        q0, q1 = q["quente_br"]
        cand = viz & ((bb - rr) > q0)
        nc, lc = cv2.connectedComponents(cand.astype(np.uint8), connectivity=4)
        regiao = np.isin(lc, np.unique(lc[r0 & cand])) & (lc > 0)
        regiao = ndimage.binary_fill_holes(regiao)
        # a fração de água de cada px: 1 por dentro, caindo na passagem para a beira quente
        agua = np.clip(((bb - rr) - q0) / (q1 - q0), 0, 1) * cv2.dilate(regiao.astype(np.uint8), np.ones((3, 3), np.uint8))
        # as peças claras e neutras grandes dentro da água (as espreguiçadeiras) ficam, com o antialias em volta
        neutro = regiao & ~nu & (croma < q["peca_croma"]) & (yy > 140)
        grandes = cv2.morphologyEx(neutro.astype(np.uint8), cv2.MORPH_OPEN, np.ones((q["peca_px"],) * 2, np.uint8)) > 0
        grandes = cv2.dilate(grandes.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~nu
        agua *= ~grandes
        if proteger is not None:
            agua *= ~proteger[y0:y1, x0:x1]
        ref_y = float(np.median(yy[nu]))
        rel = yy / max(ref_y, 1.0) - 1
        # os traços escuros sobre a água (os rótulos, os tracejados: mais escuros que `escuro_rel[1]`, com o antialias
        # em volta) são separados da água antiga e postos sobre a nova: em cada px, a fração do traço (`at`, pela luz
        # entre a água antiga de perto e o miolo do traço, o mais escuro a 2 px) fica, e o resto vira a água nova
        e0, e1 = q["escuro_rel"]
        escuro = regiao & (rel < e1)
        sobre = cv2.dilate(escuro.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & regiao & (agua > 0.5)
        limpo = nu & ~sobre
        peso = cv2.GaussianBlur(limpo.astype(np.float32), (0, 0), 5)
        y_ant = cv2.GaussianBlur(np.where(limpo, yy, 0).astype(np.float32), (0, 0), 5) / np.maximum(peso, 1e-3)
        y_ant = np.where(peso > 1e-3, y_ant, ref_y)
        tom_traco = cv2.erode(reg_, np.ones((5, 5), np.uint8))          # o miolo do traço mais perto
        at = np.clip((y_ant - yy) / np.maximum(y_ant - tom_traco.mean(axis=2), 1.0), 0, 1) * sobre
        # o desenho da água antiga, relativo: peças, rejunte, degraus e a sombra das bordas (o claro, menos); sob os
        # traços e na faixa clara das beiras, a água lisa
        rel = np.where(rel < 0, q["ganho"] * rel, q["ganho_claro"] * rel)
        base = np.where(sobre | ~nu & (croma < q["peca_croma"]), 1.0, np.clip(1 + rel, *q["base"]))
        # a sombra curta das beiras e a rede das cáusticas, longe delas
        dist = cv2.distanceTransform((agua > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        fs, sa = q["sombra"]
        base *= 1 - fs * np.exp(-np.maximum(dist - 0.5, 0) / sa)
        nova = np.float32(PISCINA_E["tom"]) * base[..., None]
        d0, d1 = q["causticas_px"]
        c = causticas(y1 - y0, x1 - x0, px_m, semente + i) * np.clip((dist - d0) / (d1 - d0), 0, 1)
        nova = nova * (1 - c[..., None]) + np.float32(PISCINA_E["claro"]) * c[..., None]
        nova = np.where(sobre[..., None], tom_traco * at[..., None] + nova * (1 - at[..., None]), nova)
        reg = out[y0:y1, x0:x1]
        reg[:] = reg * (1 - agua[..., None]) + nova * agua[..., None]
        areas.append(round(float(agua.sum()) / px_m ** 2, 1))
    return np.clip(np.round(out), 0, 255).astype(np.uint8), areas


# As bordas retas pelo PDF (usuário, 28/10/26, na piscina do Térreo da Casa A: "corrija as bordas deixando as
# perfeitas"): a água do render passava até 3 px do desenho, com a beira ondulada, pingos ciano fora dela e os cantos
# arredondados; a faixa de pedra clara entre o deck e a piscina e em volta do spa variava de largura, com uma franja
# ciano por dentro. Pelos retângulos do PDF (pt): `agua` (o preenchimento azul da ARQ_CONTRAPISO: a piscina com a
# prainha, que o degrau divide por dentro, e o spa) e `pedra` (as faixas entre as linhas do PDF: entre o deck e a
# piscina, e o anel do spa).
BORDAS = {"A-Terreo": {"agua": [(918.5, 709.3, 1145.3, 1219.6), (748.5, 1049.5, 907.2, 1219.6)],
                       "pedra": [(907.2, 709.3, 918.5, 1230.9), (737.1, 1038.2, 907.2, 1049.5),
                                 (737.1, 1049.5, 748.5, 1230.9), (737.1, 1219.6, 907.2, 1230.9)],
                       "pedra_tom": (194, 208, 223), "pedra_grao": 2.5}}
# `sombra`: a da água do Subsolo da Casa E (`PISCINA_E["sombra"]`), agora a partir da beira nova (a do TURQUESA somava
# com a da água antiga); `causticas_px`: a rede some junto à beira, como no TURQUESA; `fora_px`, o alcance máximo, por
# fora, da água que passava do desenho (até 3 px) e do fio claro que o render deixava junto a ela (medido em cada lado)
BORDA = {"ss": 4, "faixa_px": 7, "fora_px": 7, "fora_dif": 3.0, "sombra": (0.34, 2.2),
         "causticas_px": TURQUESA["causticas_px"], "traco": (120, 45, 30), "semente": 2860}


def rede_turquesa(img_antes, q=None, px_m=None, semente=None):
    """A rede das cáusticas que `turquesa(img_antes)` pôs em cada piscina (0 a 1, antes de sumir junto às beiras), para
    refazer a água junto a uma beira nova com a mesma rede, contínua. Devolve os rótulos das manchas de água (o miolo
    azul, só as que viraram turquesa) e, por rótulo, (x0, y0, x1, y1, rede) na janela da mancha."""
    q = q or TURQUESA
    px_m = px_m or q["px_m"]
    semente = q["semente"] if semente is None else semente
    a = img_antes.astype(np.float32)
    b, g, r = a[..., 0], a[..., 1], a[..., 2]
    dbr, dgr, bmin = q["ciano"]
    nucleo = (b - r > dbr) & (g - r > dgr) & (b > bmin)
    n, lab, st, _ = cv2.connectedComponentsWithStats(nucleo.astype(np.uint8), 8)
    redes = {}
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < q["area_min"]:
            continue
        x, y, w, h = st[i, :4]
        f = q["beira_px"] + 6
        x0, y0 = max(x - f, 0), max(y - f, 0)
        x1, y1 = min(x + w + f, img_antes.shape[1]), min(y + h + f, img_antes.shape[0])
        redes[i] = (x0, y0, x1, y1, causticas(y1 - y0, x1 - x0, px_m, semente + i))
    return lab, redes


def _rede_quadro(img_antes, agua_px, forma, px_m=None, semente=None):
    """A rede de `rede_turquesa` no quadro inteiro, por retângulo de água (a mancha que mais cobre cada um)."""
    lab, redes = rede_turquesa(img_antes, px_m=px_m, semente=semente)
    C = np.zeros(forma[:2], np.float32)
    for a, b, c, d in agua_px:
        i0, i1, j0, j1 = int(b), int(np.ceil(d)), int(a), int(np.ceil(c))
        ids, cont = np.unique(lab[i0:i1, j0:j1], return_counts=True)
        cont = [(k, n) for k, n in zip(ids, cont) if k in redes]
        if not cont:
            continue
        x0, y0, x1, y1, rede = redes[max(cont, key=lambda t: t[1])[0]]
        f = BORDA["faixa_px"] * 2 + 4
        r0, r1 = max(i0 - f, y0), min(i1 + f, y1)
        c0, c1 = max(j0 - f, x0), min(j1 + f, x1)
        C[r0:r1, c0:c1] = rede[r0 - y0:r1 - y0, c0 - x0:c1 - x0]
    return C


def _cobertura(rets, x0, y0, w, h, ss):
    """A fração de cada px coberta pelos retângulos (px do quadro, float), por supersample."""
    m = np.zeros((h * ss, w * ss), np.uint8)
    for a, b, c, d in rets:
        i0, i1 = int(round((b - y0) * ss)), int(round((d - y0) * ss))
        j0, j1 = int(round((a - x0) * ss)), int(round((c - x0) * ss))
        m[max(i0, 0):max(i1, 0), max(j0, 0):max(j1, 0)] = 1
    return cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)


def _corpos(agua):
    """Cada corpo d'água como lista de retângulos (a união deles): um retângulo solto é um corpo só."""
    return [[c] if len(c) == 4 and not isinstance(c[0], (tuple, list)) else list(c) for c in agua]


def _distancias(rets, xs, ys, folga=0.0):
    """As distâncias pelos eixos à borda da união dos retângulos (px do quadro), para os px de centro (xs, ys):
    por dentro, até a borda à esquerda, à direita, em cima e embaixo (dl, dr, du, dd; inf fora); por fora, até a água à
    direita, à esquerda, embaixo e em cima (er, el, ed, eu; inf se não há na linha). `folga`: os retângulos crescem
    tanto no eixo de través (para os cantos por fora)."""
    h, w = xs.shape
    inf = np.float32(np.inf)
    dl, dr, du, dd = (np.full((h, w), inf, np.float32) for _ in range(4))
    er, el, ed, eu = (np.full((h, w), inf, np.float32) for _ in range(4))

    def uniao(iv):
        iv = sorted(iv)
        out = []
        for a, b in iv:
            if out and a <= out[-1][1] + 0.6:
                out[-1][1] = max(out[-1][1], b)
            else:
                out.append([a, b])
        return out
    for i in range(h):
        y = ys[i, 0]
        x = xs[i]
        for a, b in uniao([(r[0], r[2]) for r in rets if r[1] - folga <= y < r[3] + folga]):
            den = (x >= a) & (x < b)
            dl[i] = np.where(den, x - a, dl[i])
            dr[i] = np.where(den, b - x, dr[i])
            er[i] = np.where(x < a, np.minimum(er[i], a - x), er[i])
            el[i] = np.where(x >= b, np.minimum(el[i], x - b), el[i])
    for j in range(w):
        x = xs[0, j]
        y = ys[:, j]
        for a, b in uniao([(r[1], r[3]) for r in rets if r[0] - folga <= x < r[2] + folga]):
            den = (y >= a) & (y < b)
            du[:, j] = np.where(den, y - a, du[:, j])
            dd[:, j] = np.where(den, b - y, dd[:, j])
            ed[:, j] = np.where(y < a, np.minimum(ed[:, j], a - y), ed[:, j])
            eu[:, j] = np.where(y >= b, np.minimum(eu[:, j], y - b), eu[:, j])
    return (dl, dr, du, dd), (er, el, ed, eu)


def bordas_retas(img, agua_px, pedra_px=(), pedra_tom=None, pedra_grao=2.5, rede=None, proteger=None, q=None):
    """As bordas das piscinas retas e nítidas no desenho do PDF (px do quadro). `agua_px`: os corpos d'água, cada um um
    retângulo ou a lista dos retângulos que o formam (a piscina com a prainha, um L). Na faixa de `faixa_px` junto à
    beira, a água é refeita: o fundo, pelo espelho da água de dentro (pelos eixos; nos cantos para dentro, na direção
    da beira mais perto) sem os fios claros; a rede das cáusticas, a mesma da água de dentro (`rede`, do quadro
    inteiro: `_rede_quadro`), contínua até a beira e sumindo junto a ela (`causticas_px`); a sombra curta das beiras
    (`sombra`) a partir da beira exata. Fora da água, o piso de fora é espelhado sobre a água que passava e o fio claro
    antigo, com o alcance medido em cada lado de cada corpo (até `fora_px`). As faixas de `pedra` levam a pedra clara
    lisa (`pedra_tom`, com o grão fino). Ficam como estão os px de `proteger` (bool, do quadro: as paredes e os vidros
    do PDF junto às piscinas) e os traços escuros e neutros por cima (os tracejados de projeção, `traco`)."""
    from scipy import ndimage
    q = q or BORDA
    ss, L, Lf = q["ss"], q["faixa_px"], q["fora_px"]
    corpos = _corpos(agua_px)
    todos = [r for c in corpos for r in c] + list(pedra_px)
    m = 2 * max(L, Lf) + 12
    x0 = max(int(np.floor(min(r[0] for r in todos))) - m, 0)
    y0 = max(int(np.floor(min(r[1] for r in todos))) - m, 0)
    x1 = min(int(np.ceil(max(r[2] for r in todos))) + m, img.shape[1])
    y1 = min(int(np.ceil(max(r[3] for r in todos))) + m, img.shape[0])
    w, h = x1 - x0, y1 - y0
    orig = img[y0:y1, x0:x1].astype(np.float32)
    reg = orig.copy()
    xs = np.broadcast_to(np.arange(w, dtype=np.float32)[None, :] + x0 + 0.5, (h, w)).copy()
    ys = np.broadcast_to(np.arange(h, dtype=np.float32)[:, None] + y0 + 0.5, (h, w)).copy()
    prot = np.zeros((h, w), bool) if proteger is None else proteger[y0:y1, x0:x1].copy()
    a_agua = _cobertura([r for c in corpos for r in c], x0, y0, w, h, ss)
    agua_alguma = a_agua > 0.01
    a_pedra = np.clip(_cobertura(list(pedra_px), x0, y0, w, h, ss) - a_agua, 0, 1) if pedra_px else np.zeros((h, w),
                                                                                                         np.float32)
    ciano = (orig[..., 0] - orig[..., 2] > 22) & (orig[..., 1] - orig[..., 2] > 22)

    def remapear(mx, my):
        return cv2.remap(orig, (mx - x0 - 0.5).astype(np.float32), (my - y0 - 0.5).astype(np.float32),
                         cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def fonte_ruim(mx, my):
        """A fonte cai num px protegido (ou fora da janela)."""
        jx = np.clip(np.round(mx - x0 - 0.5).astype(int), 0, w - 1)
        jy = np.clip(np.round(my - y0 - 0.5).astype(int), 0, h - 1)
        return prot[jy, jx]
    # 1. fora da água (e fora da pedra): o piso de fora espelhado sobre a água que passava e o fio claro antigo, com o
    # alcance medido em cada lado de cada corpo: a última linha, a partir da beira, que ainda difere do piso de mais
    # longe (`fora_dif` na mediana da linha, ou ciano), mais 1 px
    livre = (a_pedra < 0.01) & ~prot & ~agua_alguma
    mx, my = xs.copy(), ys.copy()
    fora = np.zeros((h, w), bool)
    for corpo in corpos:
        # as distâncias pela união de verdade (com os recantos dos cantos para dentro) e pelos retângulos crescidos de
        # través (os cantos por fora: só onde os dois lados que se encontram ali são limpos)
        _, d0 = _distancias(corpo, xs, ys)
        _, d1 = _distancias(corpo, xs, ys, folga=Lf)
        ks = []
        for dist in d0:
            def linha(e, dist=dist):
                return (dist > e) & (dist <= e + 1)
            refs = [orig[linha(e) & livre & ~ciano] for e in range(Lf + 4, Lf + 10)]
            refs = [r for r in refs if len(r)]
            if not refs or sum(len(r) for r in refs) < 20:
                ks.append(0)
                continue
            ref = np.median(np.concatenate(refs), axis=0)
            ult = -1
            for e in range(Lf):
                sel = linha(e) & livre
                if sel.sum() < 10:
                    continue
                if np.abs(np.median(orig[sel], axis=0) - ref).max() > q["fora_dif"] or ciano[sel].mean() > 0.05:
                    ult = e
            ks.append(min(ult + 2, Lf) if ult >= 0 else 0)
        kr, kl, kd, ku = ks                 # o lado esquerdo (água à direita), o direito, o de cima e o de baixo
        er0, el0, ed0, eu0 = d0
        er1, el1, ed1, eu1 = d1
        diag_x = ~np.isfinite(er0) & ~np.isfinite(el0)
        diag_y = ~np.isfinite(ed0) & ~np.isfinite(eu0)
        perto_y = ((ed1 < kd) & (kd > 0)) | ((eu1 < ku) & (ku > 0))
        perto_x = ((er1 < kr) & (kr > 0)) | ((el1 < kl) & (kl > 0))
        for dist0, dist1, k, eixo, sinal, perto in ((er0, er1, kr, "x", -1, perto_y), (el0, el1, kl, "x", 1, perto_y),
                                                    (ed0, ed1, kd, "y", -1, perto_x), (eu0, eu1, ku, "y", 1, perto_x)):
            if k == 0:
                continue
            diag = diag_x if eixo == "x" else diag_y
            dist = np.where(diag & perto, dist1, dist0)
            sel = (dist > 0) & (dist < k) & ~agua_alguma
            if eixo == "x":
                mx = np.where(sel, xs + sinal * 2 * (k - dist), mx)
            else:
                my = np.where(sel, ys + sinal * 2 * (k - dist), my)
            fora |= sel
    ruim = fonte_ruim(mx, my) | (cv2.remap(agua_alguma.astype(np.float32), (mx - x0 - 0.5).astype(np.float32),
                                            (my - y0 - 0.5).astype(np.float32), cv2.INTER_LINEAR) > 0.01)
    fora &= ~ruim
    reg = np.where(fora[..., None], remapear(mx, my), reg)
    # 2. a pedra clara nas faixas do PDF, lisa, com o grão fino
    if pedra_px:
        rng = np.random.default_rng(q["semente"])
        grao = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.8)
        grao *= pedra_grao / max(float(grao.std()), 1e-6)
        pedra = np.float32(pedra_tom)[None, None, :] + grao[..., None]
        reg = reg * (1 - a_pedra[..., None]) + pedra * a_pedra[..., None]
    # 3. a água: na faixa junto à beira, o espelho da água de dentro, com a sombra curta a partir da beira exata
    fs, sa = q["sombra"]
    mx, my = xs.copy(), ys.copy()
    prof = np.full((h, w), np.inf, np.float32)
    mascara = np.zeros((h * ss, w * ss), np.uint8)
    for corpo in corpos:
        cresce = [(r[0] - 1, r[1] - 1, r[2] + 1, r[3] + 1) for r in corpo]
        (dl, dr, du, dd), _ = _distancias(cresce, xs, ys)
        dl, dr, du, dd = dl - 1, dr - 1, du - 1, dd - 1           # a partir da beira de verdade (-1 a 0: o antialias)
        den = np.isfinite(dl)
        perto_x = den & ((dl < L) | (dr < L))
        perto_y = den & ((du < L) | (dd < L))
        mx = np.where(den & (dl < L) & (dl <= dr), xs + 2 * (L - dl), np.where(den & (dr < L), xs - 2 * (L - dr), mx))
        my = np.where(den & (du < L) & (du <= dd), ys + 2 * (L - du), np.where(den & (dd < L), ys - 2 * (L - dd), my))
        for a, b, c, d in corpo:
            i0, i1 = int(round((b - y0) * ss)), int(round((d - y0) * ss))
            j0, j1 = int(round((a - x0) * ss)), int(round((c - x0) * ss))
            mascara[max(i0, 0):max(i1, 0), max(j0, 0):max(j1, 0)] = 1
        # nos cantos para dentro (o encontro do L), a beira mais perto é a ponta: o espelho na direção dela
        edt, ind = ndimage.distance_transform_edt(np.pad(mascara, 1), return_indices=True)
        edt, ind = edt[1:-1, 1:-1], ind[:, 1:-1, 1:-1] - 1
        cy = (np.arange(h) * ss + ss // 2)[:, None]
        cx = (np.arange(w) * ss + ss // 2)[None, :]
        pe = edt[cy, cx] / ss
        canto = den & ~perto_x & ~perto_y & (pe < L) & (pe > 0)
        if canto.any():
            ny = (cy - ind[0][cy, cx]) / np.maximum(edt[cy, cx], 1e-6)
            nx = (cx - ind[1][cy, cx]) / np.maximum(edt[cy, cx], 1e-6)
            mx = np.where(canto, xs + 2 * (L - pe) * nx, mx)
            my = np.where(canto, ys + 2 * (L - pe) * ny, my)
        prof = np.where(den, np.minimum(prof, np.where(np.isfinite(pe) & (pe > 0), pe,
                                                        np.maximum(np.minimum.reduce([dl, dr, du, dd]), 0))), prof)
    agua = remapear(mx, my)
    agua = np.where(fonte_ruim(mx, my)[..., None], orig, agua)
    # o fundo sem a rede clara (a abertura tira os fios claros finos) e a rede voltando de `causticas_px[0]` a `[1]`
    # da beira: a mesma de dentro (`rede`), ou, sem ela, a do espelho
    lisa = cv2.GaussianBlur(cv2.morphologyEx(agua, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), (0, 0), 0.8)
    d0, d1 = q["causticas_px"]
    volta = np.clip((prof - d0) / (d1 - d0), 0, 1)
    if rede is not None:
        from final3840_casae import PISCINA_E
        c = rede[y0:y1, x0:x1] * volta
        agua = lisa * (1 - c[..., None]) + np.float32(PISCINA_E["claro"]) * c[..., None]
    else:
        dif = agua - lisa
        agua = lisa + np.maximum(dif, 0) * volta[..., None] + np.minimum(dif, 0)
    faixa = prof < L
    sombra = np.where(faixa, 1 - fs * np.exp(-np.maximum(prof - 0.5, 0) / sa), 1.0).astype(np.float32)
    agua = np.where(faixa[..., None], agua * sombra[..., None], orig)
    reg = reg * (1 - a_agua[..., None]) + agua * a_agua[..., None]
    # 4. os traços escuros e neutros por cima e os px protegidos ficam, só onde a imagem mudou
    t1, t0, cr = q["traco"]
    lum = orig.max(axis=2)
    croma = orig.max(axis=2) - orig.min(axis=2)
    at = np.clip((t1 - lum) / (t1 - t0), 0, 1) * (croma < cr)
    at = np.maximum(at, prot.astype(np.float32))
    at *= np.abs(reg - orig).max(axis=2) > 0.5
    reg = reg * (1 - at[..., None]) + orig * at[..., None]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


# Os corpos d'água de cada Térreo (pt do PDF: os preenchimentos azuis da ARQ_CONTRAPISO; a piscina com a prainha, que o
# degrau divide por dentro, é um corpo só) e as camadas do PDF que ficam como estão junto a eles (a parede fina ao lado
# da piscina da Casa C; os vidros e as esquadrias)
BORDAS.update({
    # na Casa B, a faixa de 17 pt à esquerda do braço da piscina (contornada no PDF, sem o azul) é água na base da
    # legenda aprovada (a mesma cor do braço) e na final: entra no corpo
    "B-Terreo": {"agua": [[(588.8, 1088.4, 605.8, 1264.2), (605.8, 1088.4, 713.5, 1281.2), (481.1, 1281.2, 900.6, 1518.4)],
                          (730.5, 1088.4, 900.6, 1264.2)]},
    "C-Terreo": {"agua": [[(498.6, 1467.7, 748.0, 1637.8), (496.3, 1637.8, 918.1, 1779.5)],
                          (759.4, 1467.7, 918.1, 1626.5)]},
    # na Casa D, a parede da piscina (a ARQ_PAREDE de 3,1 pt colada na água) virou no render um contorno cinza-azulado
    # borrado em volta da água: não fica protegida, e a água encontra a borda de pedra direto, como nas outras casas
    "D-Terreo": {"agua": [[(750.6, 709.6, 920.1, 1146.2), (920.1, 709.6, 1079.4, 986.5)],
                          (937.1, 1003.5, 1079.4, 1146.2)], "proteger": ()},
    # na Casa E, a beira vem na etapa "piscina" do motor (`final3840_casae.piscina_terreo_e`), com os vidros protegidos
    "E-Terreo": {"agua": [[(509.9, 1108.1, 953.9, 1277.4)], (809.4, 1294.4, 953.9, 1439.0)], "proteger": ()},
})
CAMADAS_PROTEGIDAS = ("ARQ_PAREDE", "ARQ - Parede", "ARQ_ESQUADRIAS", "ARQ_ELEMENTOS FIXOS", "ARQ_VIDROS")


def quadro(planta):
    """O quadro da prancha (o PDF e o p2q) do pavimento da planta ("A-Terreo"...)."""
    casa, chave = planta.split("-")
    if casa == "A":
        import final3840_casaa as FA
        return FA.QuadroA(chave)
    import final3840_casab as F
    if casa == "C":
        import final3840_casac as C
        C.contexto_c()
    elif casa == "D":
        import final3840_casad as D
        D.contexto_d()
    elif casa == "E":
        import final3840_casae as E
        return E.QuadroE(chave)
    return F.Quadro(chave)


def _bordas_px(planta, Q=None):
    """Os corpos e as faixas de pedra de `BORDAS[planta]` em px do quadro da prancha, e os px protegidos do PDF
    (`CAMADAS_PROTEGIDAS`, com 1 px de folga) perto deles."""
    Q = Q or quadro(planta)

    def px(r):
        (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        return (min(a, c), min(b, d), max(a, c), max(b, d))
    b = BORDAS[planta]
    corpos = [[px(r) for r in c] for c in _corpos(b["agua"])]
    pedra = [px(r) for r in b.get("pedra", [])]
    xs = [v for c in corpos for r in c for v in (r[0], r[2])]
    ys = [v for c in corpos for r in c for v in (r[1], r[3])]
    j0, i0, j1, i1 = int(min(xs)) - 40, int(min(ys)) - 40, int(max(xs)) + 40, int(max(ys)) + 40
    prot = np.zeros((Q.H, Q.W), np.uint8)
    for d in Q.pg.get_drawings():
        if d.get("layer") not in b.get("proteger", CAMADAS_PROTEGIDAS):
            continue
        (a, bb), (c, dd) = Q.p2q(d["rect"].x0, d["rect"].y0), Q.p2q(d["rect"].x1, d["rect"].y1)
        if max(a, c) < j0 or min(a, c) > j1 or max(bb, dd) < i0 or min(bb, dd) > i1:
            continue
        for cam in Q.caminhos(d):
            pts = np.int32(np.round(cam))
            if d["type"] in ("f", "fs") and len(pts) >= 3:
                cv2.fillPoly(prot, [pts], 1)
            cv2.polylines(prot, [pts], False, 1, 1)
    prot = cv2.dilate(prot, np.ones((3, 3), np.uint8)).astype(bool)
    return corpos, pedra, b.get("pedra_tom"), b.get("pedra_grao", 2.5), prot


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("planta", choices=sorted(set(FINAIS) | set(BORDAS)))
    ap.add_argument("--antes", type=Path, help="guarda aqui uma cópia da final anterior")
    ap.add_argument("--bordas", action="store_true", help="só as bordas retas pelo PDF (`BORDAS`), sem trocar a água")
    ap.add_argument("--rede", type=Path, help="com --bordas: a final de antes do turquesa, para a rede das cáusticas "
                    "seguir contínua até a beira")
    a = ap.parse_args()
    final = FINAIS[a.planta]
    if a.antes:
        shutil.copyfile(final, a.antes)
    img = cv2.imread(str(final))
    if a.bordas:
        corpos, pedra, tom, grao, prot = _bordas_px(a.planta)
        rede = _rede_quadro(cv2.imread(str(a.rede)), [r for c in corpos for r in c], img.shape) if a.rede else None
        cv2.imwrite(str(final), bordas_retas(img, corpos, pedra, tom, grao, rede=rede, proteger=prot))
        print(f"{a.planta}: as bordas de {len(corpos)} piscinas retas pelo PDF, com {len(pedra)} faixas de pedra clara "
              f"-> {final.relative_to(RAIZ)}")
        return
    novo, areas = turquesa(img)
    cv2.imwrite(str(final), novo)
    print(f"{a.planta}: a água de {len(areas)} piscinas no turquesa da referência ({', '.join(map(str, areas))} m²) "
          f"-> {final.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()

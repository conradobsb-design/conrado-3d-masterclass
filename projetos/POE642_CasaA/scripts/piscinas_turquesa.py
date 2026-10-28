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


def _rede_quadro(img_antes, agua_px, forma):
    """A rede de `rede_turquesa` no quadro inteiro, por retângulo de água (a mancha que mais cobre cada um)."""
    lab, redes = rede_turquesa(img_antes)
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


def bordas_retas(img, agua_px, pedra_px, pedra_tom, pedra_grao=2.5, rede=None, q=None):
    """As bordas das piscinas retas e nítidas nos retângulos do PDF (px do quadro). Na faixa de `faixa_px` junto à beira,
    a água é refeita: o fundo, pelo espelho da água de dentro sem os fios claros (sem a beira antiga); a rede das
    cáusticas, a mesma da água de dentro (`rede`, do quadro inteiro: `_rede_quadro`), contínua até a beira e sumindo
    junto a ela (`causticas_px`); a sombra curta das beiras (`sombra`) a partir da beira exata. Fora da água, a até
    `fora_px`, o piso de fora é espelhado sobre a água que passava; as faixas de `pedra` levam a pedra clara lisa
    (`pedra_tom`, com o grão fino); os traços escuros e neutros por cima (os tracejados de projeção, `traco`: luz
    máxima, luz do miolo e croma) ficam. Devolve a imagem nova."""
    q = q or BORDA
    ss, L, Lf = q["ss"], q["faixa_px"], q["fora_px"]
    todos = list(agua_px) + list(pedra_px)
    x0 = int(np.floor(min(r[0] for r in todos))) - 2 * L - 4
    y0 = int(np.floor(min(r[1] for r in todos))) - 2 * L - 4
    x1 = int(np.ceil(max(r[2] for r in todos))) + 2 * L + 4
    y1 = int(np.ceil(max(r[3] for r in todos))) + 2 * L + 4
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, img.shape[1]), min(y1, img.shape[0])
    w, h = x1 - x0, y1 - y0
    orig = img[y0:y1, x0:x1].astype(np.float32)
    reg = orig.copy()
    xs = np.arange(w, dtype=np.float32)[None, :] + x0 + 0.5
    ys = np.arange(h, dtype=np.float32)[:, None] + y0 + 0.5
    xs, ys = np.broadcast_to(xs, (h, w)), np.broadcast_to(ys, (h, w))
    a_agua = _cobertura(agua_px, x0, y0, w, h, ss)
    a_pedra = np.clip(_cobertura(pedra_px, x0, y0, w, h, ss) - a_agua, 0, 1)
    # 1. fora da água (e fora da pedra): o piso de fora espelhado sobre a água que passava e o fio claro que o render
    # deixava junto a ela; o alcance é medido em cada lado (até `fora_px`): a última linha, a partir da beira, que
    # ainda difere do piso de mais longe (`fora_dif` na média da linha, ou ciano), mais 1 px. Espelhar a faixa toda
    # sem medir dobraria os fios do piso numa linha paralela à beira
    mx, my = xs.copy(), ys.copy()
    fora = np.zeros((h, w), bool)
    livre = a_pedra < 0.01
    ciano = (orig[..., 0] - orig[..., 2] > 22) & (orig[..., 1] - orig[..., 2] > 22)

    def alcance(linha):
        """O alcance do lado: `linha(e)` dá a máscara da linha a `e` px da beira, por fora."""
        ref = [orig[linha(e) & livre] for e in range(Lf + 4, Lf + 10)]
        ref = np.concatenate([r for r in ref if len(r)]) if any(len(r) for r in ref) else None
        if ref is None or len(ref) < 20:
            return 0
        ref = ref.mean(0)
        ult = -1
        for e in range(Lf):
            px = orig[linha(e) & livre]
            if len(px) < 10:
                continue
            if np.abs(px.mean(0) - ref).max() > q["fora_dif"] or ciano[linha(e) & livre].mean() > 0.05:
                ult = e
        return min(ult + 2, Lf) if ult >= 0 else 0
    for a, b, c, d in agua_px:
        dentro_y = (ys > b) & (ys < d)
        dentro_x = (xs > a) & (xs < c)
        lados = (("x", a, -1, lambda e, a=a: dentro_y & (xs < a - e) & (xs > a - e - 1)),
                 ("x", c, 1, lambda e, c=c: dentro_y & (xs > c + e) & (xs < c + e + 1)),
                 ("y", b, -1, lambda e, b=b: dentro_x & (ys < b - e) & (ys > b - e - 1)),
                 ("y", d, 1, lambda e, d=d: dentro_x & (ys > d + e) & (ys < d + e + 1)))
        for eixo, borda, sinal, linha in lados:
            k = alcance(linha)
            if k == 0:
                continue
            if eixo == "x":
                e = (xs - borda) * sinal
                sel = (e > 0) & (e < k) & (ys > b - k) & (ys < d + k)
                mx = np.where(sel, borda + sinal * (2 * k - e), mx)
            else:
                e = (ys - borda) * sinal
                sel = (e > 0) & (e < k) & (xs > a - k) & (xs < c + k)
                my = np.where(sel, borda + sinal * (2 * k - e), my)
            fora |= sel
    piso = cv2.remap(orig, (mx - x0 - 0.5).astype(np.float32), (my - y0 - 0.5).astype(np.float32), cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT)
    reg = np.where(fora[..., None], piso, reg)
    # 2. a pedra clara nas faixas do PDF, lisa, com o grão fino
    rng = np.random.default_rng(q["semente"])
    grao = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.8)
    grao *= pedra_grao / max(float(grao.std()), 1e-6)
    pedra = np.float32(pedra_tom)[None, None, :] + grao[..., None]
    reg = reg * (1 - a_pedra[..., None]) + pedra * a_pedra[..., None]
    # 3. a água: na faixa junto à beira, o espelho da água de dentro, com a sombra curta a partir da beira exata
    fs, sa = q["sombra"]
    mx, my = xs.copy(), ys.copy()
    prof = np.full((h, w), np.inf, np.float32)
    for a, b, c, d in agua_px:
        den = (xs >= a - 1) & (xs <= c + 1) & (ys >= b - 1) & (ys <= d + 1)
        dl, dr, dt, db = xs - a, c - xs, ys - b, d - ys
        mx = np.where(den & (dl < L), a + 2 * L - dl, np.where(den & (dr < L), c - 2 * L + dr, mx))
        my = np.where(den & (dt < L), b + 2 * L - dt, np.where(den & (db < L), d - 2 * L + db, my))
        prof = np.where(den, np.minimum(prof, np.maximum(np.minimum.reduce([dl, dr, dt, db]), 0)), prof)
    agua = cv2.remap(orig, (mx - x0 - 0.5).astype(np.float32), (my - y0 - 0.5).astype(np.float32), cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REFLECT)
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
    # 4. os traços escuros e neutros por cima ficam, só onde a imagem mudou
    t1, t0, cr = q["traco"]
    lum = orig.max(axis=2)
    croma = orig.max(axis=2) - orig.min(axis=2)
    at = np.clip((t1 - lum) / (t1 - t0), 0, 1) * (croma < cr)
    mudou = np.abs(reg - orig).max(axis=2) > 0.5
    at *= mudou
    reg = reg * (1 - at[..., None]) + orig * at[..., None]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


def _bordas_px(planta):
    """Os retângulos de `BORDAS[planta]` em px do quadro da prancha (o p2q do quadro da Casa)."""
    casa, chave = planta.split("-")
    if casa != "A":
        raise SystemExit(f"{planta}: sem os retângulos do PDF em BORDAS")
    import final3840_casaa as FA
    Q = FA.QuadroA({"Terreo": "Terreo"}[chave])

    def px(r):
        (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        return (min(a, c), min(b, d), max(a, c), max(b, d))
    b = BORDAS[planta]
    return [px(r) for r in b["agua"]], [px(r) for r in b["pedra"]], b["pedra_tom"], b["pedra_grao"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("planta", choices=sorted(FINAIS))
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
        agua, pedra, tom, grao = _bordas_px(a.planta)
        rede = _rede_quadro(cv2.imread(str(a.rede)), agua, img.shape) if a.rede else None
        cv2.imwrite(str(final), bordas_retas(img, agua, pedra, tom, grao, rede=rede))
        print(f"{a.planta}: as bordas de {len(agua)} piscinas retas pelo PDF, com {len(pedra)} faixas de pedra clara "
              f"-> {final.relative_to(RAIZ)}")
        return
    novo, areas = turquesa(img)
    cv2.imwrite(str(final), novo)
    print(f"{a.planta}: a água de {len(areas)} piscinas no turquesa da referência ({', '.join(map(str, areas))} m²) "
          f"-> {final.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()

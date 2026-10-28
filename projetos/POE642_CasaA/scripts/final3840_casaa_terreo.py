#!/usr/bin/env python3
"""A final do Térreo da Casa A refeita na resolução da prancha (3840 px, ~59,7 px/m), com a auditoria de 26/10/26.

O usuário aprovou a lista do Térreo (26/10/26: "aplique a lista"; no travertino, "B": fica o de hoje):
- E10: as paredes em cinza 80 (resposta da auditoria); os pilares redondos da varanda já são pretos e ficam;
- E3 e E8: as escadas sem o triângulo e sem linhas, os degraus marcados pelo sombreamento, com a letra do PDF: S na
  escada interna do jardim, S na caracol, D no lance do deck abaixo do spa; os degraus escalonados entre o deck da
  piscina e o deck de madeira (sem letra no PDF) com o D no degrau de cima;
- E4: a seta preta de ~1,5 m no hall externo, apontando para a porta pivotante;
- E2: o armário do quarto do motorista com os cabides, como nos closets da Casa A;
- E5: o box do banho do motorista em vidro contínuo (no granito, a faixa cinza-clara visível das Casas B a D);
- E7: o rótulo do LAVABO mais à esquerda, longe da bancada; o SALA DE ESTAR fora do tapete ("O tapete conta como
  objeto, sim");
- E9: a bancada do lavabo com a borda e a sombra, mais marcada que o piso;
- E11: o granito marrom (cozinha, gourmet, serviço, despensa, motorista e garagem) no granito das Casas B a D.

Pedidos seguintes do usuário (26/10/26): o travertino bruto do Subsolo no piso ("melhorar o aspecto do travertino bruto
no piso do térreo"); os vasos do lavabo e dos banheiros da varanda gourmet em marrom-escuro; no lavatório, a cuba
esculpida em granito marrom e a bancada em travertino bruto mais marcado que o piso; o banho de serviço (o do motorista)
com piso em Bege Bahia e a pia em granito marrom mais escuro; o rótulo do banho do motorista mais abaixo e centralizado;
a ilha em U do gourmet em granito marrom mais escuro que o piso; as projeções tracejadas em preto nos fundos claros e em
branco nos escuros. E depois: a limpeza dos contornos ("faça uma limpeza em contornos. apareceram alguns erros em volta
de pisos, bancadas, sanitários, cubas"): o piso novo até a borda de cada peça, sem o anel do piso antigo; o cooktop do
PDF na ilha em U ("Me parece que você removeu um cooktop"); a ilha e a pia da cozinha em granito marrom mais escuro
("as bancadas em pedra da cozinha também são no granito marrom, levemente escurecido").

A imagem de partida é a final aprovada do Térreo no quadro de 3840 px, sem os rótulos (`rotulos_casaa.final_imagem`).
Cada item é redesenhado ali, pelo PDF (vetor) e pela base chapada da legenda, com as rotinas do `final3840_casaa.py`.

Uso (da pasta POE642_CasaA/scripts/):
  python3 final3840_casaa_terreo.py                  # a final do Térreo com os rótulos
  python3 final3840_casaa_terreo.py --de paredes     # recomeça de uma etapa (as anteriores ficam em cache)
  python3 final3840_casaa_terreo.py --ate granito    # para numa etapa (a final só é gravada quando todas rodam)
  python3 final3840_casaa_terreo.py --de rotulos --antes antes.png   # e os antes e depois de cada item
Saída: `renders/POE642_CasaA_PH_Terreo_final_rotulos.png`, que vai ao `rodape_entrega.py --no-quadro`.
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casaa as FA                     # noqa: E402

F, A, AJ = FA.F, FA.A, FA.AJ
CASA, ETAPAS, PT_PX = FA.CASA, FA.ETAPAS, FA.PT_PX
tela, sombra_q, ret_aa = FA.tela, FA.sombra_q, FA.ret_aa


# ----------------------------------------------------------------------------------------------------------------------
# 1. O granito marrom (E11): o das Casas B a D (`fontes_procedurais.granito_referencia`, na escala da prancha, no tom
# da referência do usuário, RGB ~118, 89, 69), no lugar do granito ampliado de 2000 px (mais largo, borrado e com as
# pintas grandes). Onde: a cor malva da base chapada (cozinha, bar do gourmet, área de serviço, despensa, gás, bloco do
# motorista e garagem), só nos px que a final mostra como piso (os objetos ficam: carros, bancadas, armários, inox, a
# cama; um px a menos em volta deles). A luz da final passa ao granito novo só onde escurece mais que o desenho da
# pedra antiga (`limiar`): as sombras dos carros, das bancadas e das paredes ficam; as nuvens do granito antigo, não.
# O tracejado claro das projeções (R8; a laje superior sobre a área de serviço, DOC_LINHAS E PROJEÇÕES) fica o da final:
# os px junto aos traços do PDF mais claros que a pedra em volta (`proj_claro`) não trocam.
# Os contornos (usuário, 26/10/26: "faça uma limpeza em contornos. apareceram alguns erros em volta de pisos, bancadas,
# sanitários, cubas"): os objetos são as manchas claras ou neutras da final de verdade (`area_obj` px ou mais, px a px,
# sem a folga de antes, que deixava um anel do granito antigo em volta de cada peça), com os furos de dentro; as pintas
# soltas do granito antigo, mesmo juntas, são piso. As caixas a refazer (`refaz`) trocam inteiras, menos as paredes; e
# a faixa de piso em volta das bancadas refeitas em granito (a ilha em U do gourmet, a ilha e a pia da cozinha: `anel_px`,
# menos o lado das banquetas da ilha da cozinha) também, sem o brilho da borda do quartzito antigo.
# O banho do motorista (usuário, 26/10/26: "Banho serviço: piso em mármore bege bahia, pedra pia em marrom granito
# levemente escurecida"; no Térreo, o banho de serviço é o do motorista) recebe o Bege Bahia das Casas B a D no lugar do
# granito, na mesma máscara e com a mesma luz (`bege`); a bancada e a cuba antigas (`refaz`) viram piso, e as peças novas
# vêm na etapa `loucas`.
GRANITO_T = {"chapada": (158, 167, 191), "fechar": 5, "sig_obj": 0.6, "lum_obj": 150, "croma_obj": 16,
             "area_obj": 60, "buraco_max": 600, "sig_luz": 1.4, "sig_base_m": 0.8, "limiar": 0.08, "proj_claro": 18,
             "semente": 2700, "bege": (2021.2, 1381.2, 2143.3, 1466.0),
             "refaz": [(2103.6, 1381.2, 2143.3, 1410.6)], "refaz_px": 6, "bege_semente": 2705, "anel_px": 3}


def nconv2(a, m, sig, onde=None, escalas=(2, 4, 8, 16)):
    """A média normalizada (só os px de m) de uma imagem de um canal; nos px de `onde` sem px de m no raio sig (a borda
    entre dois pisos, junto a uma peça), a de um raio maior (`escalas` vezes sig), em vez de zero."""
    num, den = cv2.GaussianBlur(a * m, (0, 0), sig), cv2.GaussianBlur(m, (0, 0), sig)
    out = num / np.maximum(den, 1e-4)
    if onde is None:
        return out
    falta = (den < 0.05) & onde
    for k in escalas:
        if not falta.any():
            break
        num, den = cv2.GaussianBlur(a * m, (0, 0), sig * k), cv2.GaussianBlur(m, (0, 0), sig * k)
        ok = falta & (den >= 0.05)
        out[ok] = num[ok] / den[ok]
        falta &= ~ok
    return out


def tracejado(Q):
    """Os traços da DOC_LINHAS E PROJEÇÕES no quadro (3 px), em cache."""
    if getattr(Q, "_tracejado", None) is None:
        tr = np.zeros((Q.H, Q.W), np.uint8)
        for d in Q.desenhos:
            if d.get("layer") == "DOC_LINHAS E PROJEÇÕES" and d["type"] == "s":
                for c in Q.caminhos(d):
                    cv2.polylines(tr, [np.int32(np.round(c))], False, 1, 3)
        Q._tracejado = tr > 0
    return Q._tracejado


def caixas(Q, rets, folga_px):
    """Os retângulos (pt) no quadro, com a folga (px)."""
    a = np.zeros((Q.H, Q.W), np.float32)
    for r in rets:
        a = np.maximum(a, ret_aa(Q, r))
    k = 2 * folga_px + 1
    return cv2.dilate((a > 0.02).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)


def refazer(Q, rets, folga_px):
    """As caixas a refazer (pt), com a folga (px), sem as paredes (o escuro grosso da base chapada; os traços finos das
    peças antigas saem junto)."""
    escuro = (Q.chapada.max(axis=2) <= 60).astype(np.uint8)
    parede = cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)
    return caixas(Q, rets, folga_px) & ~parede


def perto_de(m, px):
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * px + 1, 2 * px + 1), np.uint8)).astype(bool)


def traco_chapada(Q, ch):
    """Os px de traço da base chapada junto ao piso ch: as cores fora da paleta e o px entre o piso e uma peça branca (o
    antialias dos traços do PDF, que não é nem piso nem peça e ficava com o px antigo)."""
    if getattr(Q, "_raras", None) is None:
        c = Q.chapada.astype(np.int32)
        k = (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2]
        cores, n = np.unique(k, return_counts=True)
        Q._raras = ~np.isin(k, cores[n >= 5000])
    branco = np.all(Q.chapada == 255, axis=2)
    entre = perto_de(branco, 1) & ~branco & (Q.chapada.max(axis=2) > 60)
    return perto_de(ch, 1) & ~ch & (Q._raras | entre)


def pecas_cheias(Q):
    """As peças cheias da base chapada (os preenchimentos brancos do PDF: bancadas, armários; sem os contornos finos dos
    móveis), que são objeto até a borda."""
    if getattr(Q, "_cheias", None) is None:
        Q._cheias = cv2.morphologyEx(np.all(Q.chapada == 255, axis=2).astype(np.uint8), cv2.MORPH_OPEN,
                                     np.ones((5, 5), np.uint8)).astype(bool)
    return Q._cheias


def manchas(m, area_min, buraco_max):
    """As manchas de m com area_min px ou mais, com os furos de dentro (até buraco_max px)."""
    from scipy import ndimage
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    g = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= area_min])
    furo = ndimage.binary_fill_holes(g) & ~g
    n, lab, st, _ = cv2.connectedComponentsWithStats(furo.astype(np.uint8), 8)
    return g | np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= buraco_max])


def bege_bahia(Q, h, w, semente):
    """O Bege Bahia das Casas B a D (a foto da biblioteca na escala, no tom delas), h x w x 3."""
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from texturas import textura
    T = textura("bege_bahia", Q.px_m, h, w, semente=semente).astype(np.float32)
    return T / T.reshape(-1, 3).mean(axis=0) * np.float32(FA.PISOS_A["Bege Bahia"]["tom"])


def anel_bancadas(Q, px):
    """A faixa da borda das bancadas refeitas em granito (a ilha em U, a ilha e a pia da cozinha): px para fora e 2 px
    para dentro (o px da borda, que a pedra nova cobre só em parte, levava o branco do quartzito antigo), menos o lado
    das banquetas da ilha da cozinha."""
    m = np.zeros((Q.H, Q.W), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round([Q.p2q(x, y) for x, y in ILHA["poli"]]))], 1)
    m = m.astype(bool)
    r = caixas(Q, [COZINHA["pia"]], 0)
    i = caixas(Q, [COZINHA["ilha"]], 0)
    dentro = cv2.erode((m | r | i).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    i = perto_de(i, px)
    i[:int(np.ceil(Q.p2q(0, COZINHA["ilha"][1])[1])), :] = False
    return (perto_de(m | r, px) | i) & ~dentro


def granito(Q, img):
    import fontes_procedurais as FP
    q = GRANITO_T
    im = img.astype(np.float32)
    ch = F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), q["fechar"])
    branco = np.all(Q.chapada == 255, axis=2) & perto_de(ch, 7)
    traco = traco_chapada(Q, ch)
    refaz = (refazer(Q, q["refaz"], q["refaz_px"]) & perto_de(ch, 7)) | (anel_bancadas(Q, q["anel_px"]) & perto_de(ch, 3))
    onde = (ch | branco | refaz | traco) & (FA.paredes_pdf(Q) < 0.5)          # as esquadrias e as portas ficam
    f = cv2.GaussianBlur(im, (0, 0), q["sig_obj"])
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    obj = manchas(onde & ((lum > q["lum_obj"]) | (croma < q["croma_obj"])), q["area_obj"], q["buraco_max"])
    obj |= branco & ~obj & (lum > q["lum_obj"] * 0.8)           # o resto claro dos objetos na base branca
    obj |= pecas_cheias(Q) & ~refaz
    # o tracejado das projeções
    L0 = im.mean(axis=2)
    claro = L0 - cv2.medianBlur(np.clip(L0, 0, 255).astype(np.uint8), 9).astype(np.float32) > q["proj_claro"]
    proj = perto_de(ch & tracejado(Q) & claro, 1)
    m = (onde & ~obj & ~proj) | refaz
    # a luz: o que escurece além do desenho da pedra antiga (sombras), só com os px do granito
    mf = (m & ~refaz).astype(np.float32)
    perto = nconv2(L0, mf, q["sig_luz"], onde=m)
    base = nconv2(L0, mf, q["sig_base_m"] * Q.px_m)
    sh = np.clip(perto / np.maximum(base, 1) + q["limiar"], 0, 1)
    # nas caixas refeitas, a luz do piso em volta (a sombra das paredes e das peças, sem a da peça antiga)
    sh[refaz] = np.clip(nconv2(L0, mf, 2.5, onde=refaz) / np.maximum(base, 1) + q["limiar"], 0, 1)[refaz]
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    T = FP.granito_referencia(y1 - y0 + 16, x1 - x0 + 16, Q.px_m, semente=q["semente"]).astype(np.float32)[8:-8, 8:-8]
    # o banho do motorista em Bege Bahia
    bg = (ret_aa(Q, q["bege"]) > 0.5)[y0:y1, x0:x1]
    T = np.where(bg[..., None], bege_bahia(Q, y1 - y0, x1 - x0, q["bege_semente"]), T)
    novo = im.copy()
    novo[y0:y1, x0:x1] = T * sh[y0:y1, x0:x1, None]
    out = F.pousar(im, novo, m, suave=0.6)
    print(f"    granito das Casas B a D: {m.sum() / Q.px_m ** 2:.1f} m² de piso (os objetos ficam, sem folga: "
          f"{(onde & obj).sum() / Q.px_m ** 2:.1f} m²; o tracejado das projeções: {int(proj.sum())} px); o banho do "
          f"motorista em Bege Bahia ({(bg & m[y0:y1, x0:x1]).sum() / Q.px_m ** 2:.1f} m²)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 1b. O travertino bruto do piso (usuário, 26/10/26: "melhorar o aspecto do travertino bruto no piso do térreo"; antes,
# "B": ficava o de hoje, rosado e quase liso): o do Subsolo aprovado (`final3840_casaa.travertino_bruto`: a foto da
# biblioteca na escala, os veios horizontais e os poros, no creme das Casas B a D), na cor do travertino da base chapada
# (estar, jantar, varanda, halls, escritório, lavabo, lavatório, banho varanda e WC, o lounge do gourmet), só no piso:
# - os móveis são os brancos da base chapada (com 2 px de folga) e o que a final mostra fora do tom do piso: mais claro
#   (`claro`), de outra cor (`croma`) ou muito escuro (traços, pilares, vidros); as sombras (mais escuras, na mesma cor)
#   são piso e passam ao travertino novo como luz, como no granito;
# - o tracejado das projeções (mais escuro que o piso, junto aos traços do PDF) fica o da final;
# - as louças e a bancada que são refeitas na etapa `loucas` (`refaz`) viram piso antes, inteiras (menos as paredes).
# Os contornos (usuário, 26/10/26: "faça uma limpeza em contornos"): antes, os móveis levavam uma folga de 2 a 4 px do
# piso antigo, rosado, em volta. Agora o piso troca até a borda de cada peça, px a px, pelo quanto o px foge do piso
# antigo em volta (`alfa_objetos`): mais claro, de outra cor ou muito escuro é objeto; a sombra (mais escura e mais
# acinzentada, como o render antigo a fazia) é piso e passa ao travertino novo como luz; os px da borda, meio objeto e
# meio piso, misturam os dois. As manchas só um pouco mais claras que o piso, na mesma cor e sem px fortes (a luz do
# render antigo e os restos rosados de peças que saíram, que no travertino novo viravam retângulos rosados), são piso. O miolo das peças cheias da base (bancadas, armários) é sempre objeto; os px de traço da
# base (o antialias entre o piso e a peça, que não era nem um nem outro e ficava com o px antigo) entram na troca.
TRAV_T = {"chapada": (202, 217, 220), "fechar": 3, "area_obj": 40, "sig_luz": 0.8, "sig_base_m": 0.8, "limiar": 0.05,
          "proj_escuro": 0.93, "sig_m": 3.0, "refaz": [(2077.1, 577.4, 2106.3, 597.5), (1293.9, 1734.0, 1323.0, 1754.0),
                                                       (1442.9, 1612.5, 1462.9, 1641.6),
                                                       (1292.7, 1605.1, 1406.1, 1633.4)],
          "refaz_px": 7, "semente": 2704,
          # o quanto o px foge do piso antigo: (onde começa, onde já é objeto)
          "alfa": {"croma": (0.015, 0.035), "claro": (1.03, 1.07), "escuro": (0.62, 0.50), "sig_px": 0.6,
                   "zona_px": 3, "buraco_max": 600,
                   # px forte (croma, claro, escuro); mancha fraca: até 2% de px fortes, 90% abaixo de croma e claro
                   "forte": (0.05, 1.10, 0.55), "fraca": (0.02, 0.02, 1.09)}}


def travertino_t(Q, h, w, semente, borda=8):
    """O travertino bruto do Subsolo aprovado (h x w x 3), no tom dele (gerado com `borda` px a mais em volta: na borda
    da foto, os poros se juntavam numa fila escura)."""
    p = FA.PISOS_A["travertino"]
    D = FA.travertino_bruto(Q, h + 2 * borda, w + 2 * borda, semente, forca=p["forca"], **FA.TRAVERTINO["piso"])
    return np.float32(p["tom"]) * D[borda:borda + h, borda:borda + w, None]


def alfa_objetos(im, L, onde, area_min, z):
    """O quanto cada px de `onde` é objeto (0: o piso antigo, com ou sem sombra; 1: objeto), pela cor dele contra a do
    piso antigo em volta (L): mais claro, de outra cor ou muito escuro. Só junto às manchas de objeto de verdade
    (area_min px ou mais, com os furos de dentro): as pintas e os veios soltos do piso antigo são piso."""
    f = cv2.GaussianBlur(im, (0, 0), z["sig_px"])
    lf = np.maximum(f.mean(axis=2), 1)
    lL = np.maximum(L.mean(axis=2), 1)
    r = lf / lL
    c, cL = f / lf[..., None], L / lL[..., None]
    cd = np.abs(c - cL).max(axis=2)
    # mais escuro que o piso: a sombra do render antigo é também mais acinzentada (o tom do piso indo para o neutro)
    v = cL - 1
    t = np.clip(((c - 1) * v).sum(axis=2) / np.maximum((v * v).sum(axis=2), 1e-6), 0, 1)[..., None]
    cd = np.where(r < 1, np.minimum(cd, np.abs(c - 1 - t * v).max(axis=2)), cd)
    rampa = lambda x, a, b: np.clip((x - a) / (b - a), 0, 1)
    w = np.maximum.reduce([rampa(cd, *z["croma"]), rampa(r, *z["claro"]), rampa(r, *z["escuro"])])
    g = manchas(onde & (w > 0.5), area_min, z["buraco_max"])
    # as manchas só um pouco mais claras que o piso, na mesma cor (a luz do render antigo, os restos rosados de peças
    # antigas), sem px fortes, são piso
    n, lab = cv2.connectedComponents(g.astype(np.uint8), connectivity=8)
    cnt = np.maximum(np.bincount(lab.ravel(), minlength=n), 1)
    fr = lambda x: np.bincount(lab.ravel(), weights=x.ravel().astype(np.float64), minlength=n) / cnt
    f_forte = fr((cd > z["forte"][0]) | (r > z["forte"][1]) | (r < z["forte"][2]))
    fraca = (f_forte <= z["fraca"][0]) & (fr(cd > z["fraca"][1]) <= 0.1) & (fr(r > z["fraca"][2]) <= 0.1)
    fraca[0] = False
    g &= ~fraca[lab]
    a = np.where(onde & perto_de(g, z["zona_px"]), w, 0).astype(np.float32)
    a[g & ((w <= 0.5) | ~perto_de(~g, 2))] = 1                   # os furos e o miolo das peças
    return a


def travertino(Q, img):
    q = TRAV_T
    im = img.astype(np.float32)
    ch = F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), q["fechar"])
    branco = np.all(Q.chapada == 255, axis=2) & perto_de(ch, 7)
    # o traço junto ao granito é dele (a etapa do granito o troca), não do travertino; e a divisa dos dois pisos fica
    gran = perto_de(np.all(Q.chapada == np.uint8(GRANITO_T["chapada"]), axis=2), 2)
    cru = np.all(Q.chapada == np.uint8(q["chapada"]), axis=2)
    refaz = refazer(Q, q["refaz"], q["refaz_px"]) | (anel_bancadas(Q, GRANITO_T["anel_px"]) & perto_de(ch, 3) & ~gran)
    onde = (ch | branco | refaz | traco_chapada(Q, ch)) & (FA.paredes_pdf(Q) < 0.5)   # as esquadrias e as portas ficam
    onde &= ~(gran & ~cru)
    L = F.luz_robusta(im, ch & ~perto_de(branco, 2), 1.0 * Q.px_m)
    lum = im.mean(axis=2)
    a = alfa_objetos(im, L, onde, q["area_obj"], q["alfa"])
    a[perto_de(ch & tracejado(Q) & (lum / np.maximum(L.mean(axis=2), 1) < q["proj_escuro"]), 1)] = 1
    a[pecas_cheias(Q) & ~refaz] = 1
    a[refaz] = 0
    # a luz: as sombras (o que escurece além do desenho da pedra antiga, até a borda dos móveis) e a luz larga
    limpo = onde & (a < 0.5) & ~refaz
    mf = limpo.astype(np.float32)
    perto = nconv2(lum, mf, q["sig_luz"], onde=onde)
    base = nconv2(lum, mf, q["sig_base_m"] * Q.px_m)
    larga = nconv2(lum, mf, q["sig_m"] * Q.px_m)
    k = larga / np.median(larga[limpo])
    sh = np.clip(perto / np.maximum(base, 1) + q["limiar"], 0, 1) * k
    # nas caixas refeitas, a luz do piso em volta (a sombra das paredes e das peças, sem a da peça antiga)
    sh[refaz] = (np.clip(nconv2(lum, mf, 2.5, onde=refaz) / np.maximum(base, 1) + q["limiar"], 0, 1) * k)[refaz]
    m = onde & (a < 1)
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    novo = im.copy()
    novo[y0:y1, x0:x1] = travertino_t(Q, y1 - y0, x1 - x0, q["semente"]) * sh[y0:y1, x0:x1, None]
    a3 = np.where(m, a, 1)[..., None]
    out = im * a3 + novo * (1 - a3)
    print(f"    travertino bruto do Subsolo no piso: {(m & (a < 0.5)).sum() / Q.px_m ** 2:.1f} m², até a borda dos "
          f"móveis (os móveis e o que foge do tom do piso ficam: {(onde & (a >= 0.5)).sum() / Q.px_m ** 2:.1f} m²)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 2. O bloco do motorista:
# - E2: o armário do quarto (o retângulo com a diagonal da DOC_LINHAS E PROJEÇÕES, 0,60 x 1,80 m, junto à parede da
#   direita) aberto, visto de cima, com os cabides e o cabideiro de metal, como os guarda-roupas dos closets da Casa A
#   (`ajustes_casaa.guarda_roupas_1pav`: `_texturas/elementos.guarda_roupa`, os tons da Casa E, bege dentro e ocre na
#   borda), com as portas do lado do quarto e a sombra curta no granito;
# - E5: o box do banho (as duas folhas de correr do PDF, `AJ.folhas_box`) em vidro contínuo e visível; no granito, a faixa
#   cinza-clara da regra de 22/10 ("Tem que estar visível"), com as faces finas. Desde 28/10 (etapa `box_motorista`,
#   `FA.boxes`), as duas folhas fechadas, de parede a parede, sem o trilho tracejado.
MOTORISTA = {"armario": (2250.8, 1287.6, 2284.8, 1389.7), "portas": "esquerda", "sombra": 0.30, "ss": 4,
             "semente": 41, "box_meio": 2060.9}


def motorista(Q, img):
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from elementos import guarda_roupa
    from retoque_1pav_casae import GUARDA_ROUPAS
    q = MOTORISTA
    out = np.ascontiguousarray(img.copy())
    r = q["armario"]
    tl = tela(out, Q, r, folga=6)
    sombra_q(tl, tl.ret(r), forca=q["sombra"], dist=1.4, sigma=1.4)
    out = tl.gravar()
    x0, y0, x1, y1 = r
    (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
    S = q["ss"]
    comp, prof = max(x1 - x0, y1 - y0) / 56.69, min(x1 - x0, y1 - y0) / 56.69
    cor, alfa = guarda_roupa(comp, prof, Q.px_m * S, semente=q["semente"], miolo=GUARDA_ROUPAS["miolo"],
                             moldura=GUARDA_ROUPAS["moldura"], barra=True)
    k = {"baixo": 0, "direita": 1, "cima": 2, "esquerda": 3}[q["portas"]]
    cor, alfa = np.ascontiguousarray(np.rot90(cor, k)), np.ascontiguousarray(np.rot90(alfa, k))
    X0, Y0, X1, Y1 = int(np.floor(u0)), int(np.floor(v0)), int(np.ceil(u1)), int(np.ceil(v1))
    tw, th = int(round((u1 - u0) * S)), int(round((v1 - v0) * S))
    ox, oy = int(round((u0 - X0) * S)), int(round((v0 - Y0) * S))
    grande = np.zeros(((Y1 - Y0) * S, (X1 - X0) * S, 3), np.float32)
    ag = np.zeros(grande.shape[:2], np.float32)
    grande[oy:oy + th, ox:ox + tw] = cv2.resize(cor, (tw, th), interpolation=cv2.INTER_AREA)
    ag[oy:oy + th, ox:ox + tw] = cv2.resize(alfa, (tw, th), interpolation=cv2.INTER_AREA)
    cr = cv2.resize(grande, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    ar = cv2.resize(ag, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - ar) + cr, 0, 255).astype(np.uint8)
    print(f"    quarto do motorista: o armário com os cabides e o cabideiro ({comp:.2f} x {prof:.2f} m), portas à "
          f"{q['portas']}")
    return out


def box_motorista(Q, img):
    """O box do banho do motorista (`FA.boxes`): as duas folhas fechadas, de parede a parede, sem o trilho tracejado
    (pedido de 28/10); no granito, o vidro claro lê como a faixa cinza-clara da regra de 22/10."""
    q = MOTORISTA
    out = FA.boxes(Q, np.ascontiguousarray(img.copy()), so=lambda b: not b["hor"] and abs(b["meio"] - q["box_meio"]) < 1)
    print("    banho do motorista: o box em vidro contínuo, de parede a parede")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 3. E9: a bancada do lavabo (o retângulo da ARQ_BANCADAS, encostado na parede da direita) mais marcada que o piso de
# travertino, no mesmo tom claro dele: a borda fina no tom escurecido da própria pedra e a sombra curta no piso, como as
# bancadas do Subsolo (`bancada_pedra`); a pedra, a cuba e a torneira ficam as da final.
LAVABO = {"bancada": (2077.9, 615.8, 2106.3, 670.2), "borda": 0.70, "larg_px": 0.7, "sombra": 0.36}


def lavabo(Q, img):
    q = LAVABO
    r = q["bancada"]
    tl = tela(np.ascontiguousarray(img.copy()), Q, r, folga=6)
    m = tl.ret(r)
    sombra_q(tl, m, forca=q["sombra"], dist=1.3, sigma=1.3)
    k = max(1, int(round(q["larg_px"] * 8)))
    borda = m & ~cv2.erode(m, np.ones((k, k), np.uint8))
    tl.pintar_img(borda, tl.reg * q["borda"])
    print("    lavabo: a bancada com a borda no tom escurecido da pedra e a sombra curta no piso")
    return tl.gravar()


# ----------------------------------------------------------------------------------------------------------------------
# 3b. As louças e as bancadas (usuário, 26/10/26):
# - "sanitário do lavabo em marrom escuro" e, "nos banheiros da varanda gourmet: sanitários no marrom escuro" (o WC e o
#   banho varanda): os vasos do `retoque_subsolo_casae` no contorno do PDF, em louça marrom-escura;
# - no lavatório: "cuba esculpida no marrom granito, pedra bancada cuba em mármore travertino bruto levemente escurecido
#   para distinguir do piso": a bancada do PDF no travertino bruto mais marcado das bancadas do Subsolo (o tom mais
#   fundo, a borda no tom escurecido da pedra e a sombra curta), a cuba esculpida em granito marrom (a borda polida e a
#   bacia funda, `cuba_granito`) e a torneira cromada;
# - no banho do motorista (o banho de serviço do Térreo): "pedra pia em marrom granito levemente escurecida para
#   distinguir do piso": a bancada do PDF em granito marrom um pouco mais escuro, com a borda e a sombra, a cuba branca
#   de semiencaixe e a torneira; o vaso fica branco.
LOUCAS = {"vaso_escuro": {"louca": (40, 54, 76), "contorno": (18, 24, 32), "tampo": (58, 76, 102)},   # BGR
          "vasos": [("lavabo", (2077.1, 577.4, 2106.3, 597.5), "direita"),
                    ("WC", (1293.9, 1734.0, 1323.0, 1754.0), "esquerda"),
                    ("banho varanda", (1442.9, 1612.5, 1462.9, 1641.6), "cima")],
          "lavatorio": {"bancada": (1292.7, 1605.1, 1406.1, 1633.4), "cuba": (1342.0, 1610.8, 1384.6, 1627.8),
                        "bacia": (1343.4, 1612.2, 1383.2, 1626.4), "torneira": (1339.4, 1618.2, 1347.0, 1620.3),
                        "base": (1338.8, 1619.25, 1.5), "semente": 2706},
          "motorista": {"bancada": (2103.6, 1381.2, 2143.3, 1403.8), "cuba": (2112.1, 1388.0, 2134.7, 1410.6),
                        "torneira": (2122.0, 1389.9, 2124.8, 1397.7), "base": (2123.4, 1389.4, 1.4),
                        "escurecer": 0.86, "borda": 0.62, "larg": 0.6, "sombra": 0.34, "semente": 2707,
                        # o chuveiro (no PDF, só o braço e um disco de 1 pt junto à parede de cima, no meio do box):
                        # a placa cromada das outras, no mesmo eixo (saía com o granito antigo)
                        "chuveiro": {"ducha": (2037.6, 1386.6, 2047.4, 1396.4), "braco": (2041.8, 1381.2, 2043.2, 1391.5),
                                     "canopla": (2040.5, 1381.2, 2044.5, 1382.5)}}}


def loucas(Q, img):
    q = LOUCAS
    out = np.ascontiguousarray(img.copy())
    for nome, caixa, parede in q["vasos"]:
        out = FA.vaso(Q, out, caixa, parede, q["vaso_escuro"])
    print(f"    {len(q['vasos'])} vasos em louça marrom-escura: " + ", ".join(n for n, _, _ in q["vasos"]))
    lv = q["lavatorio"]
    tb = FA.BANHOS["trav_bancada"]
    out = FA.bancada_pedra(Q, out, lv["bancada"], lambda tl: np.float32(tb["tom"]) * FA.travertino_bruto(
        Q, tl.h, tl.w, lv["semente"], **FA.TRAVERTINO["bancada"])[..., None], tb["borda"], tb["larg"], tb["sombra"])
    out = FA.cuba_granito(Q, out, lv, lv["semente"] + 1)
    out = FA.torneira(Q, out, lv["torneira"], lv["base"])
    print("    lavatório: bancada em travertino bruto mais marcado que o piso, cuba esculpida em granito marrom, torneira")
    mt = q["motorista"]
    out = FA.bancada_pedra(Q, out, mt["bancada"], lambda tl: FA._granito(Q, tl, mt["semente"]) * mt["escurecer"],
                           mt["borda"], mt["larg"], mt["sombra"])
    out = FA.cuba_branca(Q, out, mt["cuba"])
    out = FA.torneira(Q, out, mt["torneira"], mt["base"])
    out = FA.chuveiro(Q, out, mt["chuveiro"])
    print("    banho do motorista: bancada em granito marrom um pouco mais escuro, cuba branca, torneira, chuveiro; "
          "vaso branco")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 3c. A ilha em U da varanda gourmet (usuário, 26/10/26: "pedra da ilha em U da varanda gourmet é marrom granito, igual
# ao piso. deixe-a levemente escurecida para distinguir do piso"; era o quartzito Carrara de 21/10): o polígono da
# ARQ_BANCADAS em granito marrom um pouco mais escuro que o piso do gourmet, com a borda no tom escurecido da pedra e a
# sombra curta (E9); a área molhada da perna de baixo (o retângulo do PDF) rebaixada, um tom abaixo, com a borda.
# Depois (usuário, 26/10/26: "Me parece que você removeu um cooktop da bancada da ilha da varanda gourmet"; o PDF tem o
# cooktop de 5 bocas no braço de cima, que a final aprovada não mostrava; e a limpeza dos contornos):
# - o cooktop de inox de 5 bocas da biblioteca, o mesmo da ilha da cozinha, no retângulo do PDF, com os botões embaixo,
#   do lado de quem cozinha (`cooktop`);
# - a cuba de inox redesenhada no PDF (`cuba_inox`: a aba, a bacia com a sombra das bordas de cima e da direita, a
#   válvula) e a torneira cromada, no lugar da recortada da final (que trazia a moldura branca do quartzito antigo);
# - as linhas finas da pedra do PDF no tom da borda: o degrau do balcão das banquetas no braço de cima e as laterais em
#   cascata das pontas (`linhas`).
ILHA = {"poli": [(1281.4, 1596.6), (1281.4, 1432.2), (1556.3, 1432.2), (1556.3, 1488.9), (1315.4, 1488.9),
                 (1315.4, 1556.9), (1556.3, 1556.9), (1556.3, 1596.6)],
        "molhada": (1443.5, 1559.2, 1554.1, 1593.8),
        "cuba": {"cuba": (1492.8, 1564.3, 1534.8, 1589.2), "bacia": (1494.3, 1565.7, 1533.4, 1587.7),
                 "torneira": (1514.5, 1579.3, 1516.2, 1590.4), "base": (1515.35, 1590.6, 1.4)},
        "cooktop": (1409.5, 1458.8, 1459.4, 1487.2),
        "linhas": [((1282.5, 1451.45), (1554.1, 1451.45)), ((1283.05, 1452.1), (1283.05, 1596.6)),
                   ((1555.2, 1432.2), (1555.2, 1488.9))],
        "escurecer": 0.86, "molhada_esc": 0.80, "borda": 0.62, "larg": 0.6, "sombra": 0.34, "linha_px": 0.9,
        "linha": 0.70, "semente": 2708}
INOX = {"aba": (196, 199, 202), "bacia": (176, 180, 184), "sombra": (0.30, 2.0), "contorno": (128, 132, 136),
        "larg": 0.4}
COOKTOP = {"bloco": "cooktop_inox_5_90", "esticar": 1.10, "azul": 18}


def cuba_inox(Q, out, c):
    """A cuba de inox de embutir: a aba fina, a bacia com a sombra das bordas de cima e da direita por dentro (a luz
    vem do alto à direita), a válvula cromada; e a torneira."""
    q = INOX
    tl = tela(out, Q, c["cuba"], folga=4)
    m = tl.ret(c["cuba"], 1.0)
    tl.pintar(m, q["aba"])
    b = tl.ret(c["bacia"], 1.6)
    dist = cv2.distanceTransform(b, cv2.DIST_L2, 5) / 8
    X, Y = tl.grade()
    x0, y0, x1, y1 = c["bacia"]
    lado = np.clip(((X - x0) / (x1 - x0) + (y1 - Y) / (y1 - y0)) / 2, 0, 1)
    f, alc = q["sombra"]
    d_out = cv2.resize(dist.astype(np.float32), (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    prof = 1 - f * np.clip(1 - d_out / alc, 0, 1) * (0.35 + 0.65 * lado)
    tl.pintar_img(b, np.float32(q["bacia"]) * prof[..., None])
    tl.contorno(b, q["larg"], q["contorno"])
    tl.contorno(m, q["larg"], q["contorno"])
    v = tl.vazia()
    cx, cy = tl.pt((x0 + x1) / 2, (y0 + y1) / 2)
    cv2.circle(v, (int(cx), int(cy)), int(1.3 * PT_PX * 8), 255, -1, cv2.LINE_AA)
    tl.pintar(v, FA.CROMO["meio"])
    tl.contorno(v, 0.3, FA.CROMO["contorno"])
    out = tl.gravar()
    return FA.torneira(Q, out, c["torneira"], c["base"])


def cooktop(Q, out, r):
    """O cooktop de inox de 5 bocas da biblioteca (o da ilha da cozinha, `ajustes_casaa.desenhar_ilha`): na altura do
    retângulo do PDF, até `esticar` na largura, centrado, os botões embaixo; o anel azul da chama em inox."""
    q = COOKTOP
    rgba = cv2.imread(str(A.RAIZ / "_blocos" / "recortes" / f"{q['bloco']}.png"), cv2.IMREAD_UNCHANGED)
    cor0 = rgba[..., :3].astype(np.float32)
    azul = np.clip((cor0[..., 0] - cor0[..., 2] - q["azul"]) / 20, 0, 1)[..., None]
    cor0 = cor0 * (1 - azul) + cor0.mean(axis=2, keepdims=True) * azul
    a0 = rgba[..., 3].astype(np.float32) / 255
    (x0, y0), (x1, y1) = Q.p2q(*r[:2]), Q.p2q(*r[2:])
    H = y1 - y0
    W = min(x1 - x0, H * rgba.shape[1] / rgba.shape[0] * q["esticar"])
    cx, cy, k = (x0 + x1) / 2, (y0 + y1) / 2, 8
    Wi, Hi = int(np.ceil(W)) + 2, int(np.ceil(H)) + 2
    fx, fy = np.floor(cx - W / 2) - 1, np.floor(cy - H / 2) - 1
    M = cv2.getAffineTransform(np.float32([(0, 0), (rgba.shape[1], 0), (0, rgba.shape[0])]),
                               np.float32([((cx - W / 2 - fx) * k, (cy - H / 2 - fy) * k),
                                           ((cx + W / 2 - fx) * k, (cy - H / 2 - fy) * k),
                                           ((cx - W / 2 - fx) * k, (cy + H / 2 - fy) * k)]))
    c1 = cv2.resize(cv2.warpAffine(cor0 * a0[..., None], M, (Wi * k, Hi * k), flags=cv2.INTER_AREA), (Wi, Hi),
                    interpolation=cv2.INTER_AREA)
    a1 = cv2.resize(cv2.warpAffine(a0, M, (Wi * k, Hi * k), flags=cv2.INTER_AREA), (Wi, Hi),
                    interpolation=cv2.INTER_AREA)[..., None]
    fx, fy = int(fx), int(fy)
    reg = out[fy:fy + Hi, fx:fx + Wi].astype(np.float32)
    out[fy:fy + Hi, fx:fx + Wi] = np.clip(reg * (1 - a1) + c1, 0, 255).astype(np.uint8)
    return out


def linhas_pedra(Q, out, linhas, larg_px, mult):
    """As linhas finas da pedra do PDF (degraus, laterais em cascata) no tom escurecido da própria pedra."""
    for a, b in linhas:
        tl = tela(out, Q, (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), folga=3)
        m = tl.linha([a, b], larg_px)
        tl.pintar_img(m, tl.reg * mult)
        out = tl.gravar()
    return out


def ilha(Q, img):
    q = ILHA
    xs, ys = [p[0] for p in q["poli"]], [p[1] for p in q["poli"]]
    caixa = (min(xs), min(ys), max(xs), max(ys))
    out = FA.bancada_pedra(Q, np.ascontiguousarray(img.copy()), caixa,
                           lambda tl: FA._granito(Q, tl, q["semente"]) * q["escurecer"], q["borda"], q["larg"],
                           q["sombra"], poli=q["poli"])
    out = FA.bancada_pedra(Q, out, q["molhada"], lambda tl: FA._granito(Q, tl, q["semente"] + 1) * q["molhada_esc"],
                           q["borda"], q["larg"], 0.0)
    out = linhas_pedra(Q, out, q["linhas"], q["linha_px"], q["linha"])
    out = cuba_inox(Q, out, q["cuba"])
    out = cooktop(Q, out, q["cooktop"])
    print("    ilha em U do gourmet: granito marrom um pouco mais escuro que o piso, com a borda e a sombra; a área "
          "molhada rebaixada; o degrau do balcão e as laterais em cascata; a cuba de inox e a torneira; o cooktop de "
          "5 bocas do PDF")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 3d. As bancadas de pedra da cozinha (usuário, 26/10/26: "as bancadas em pedra da cozinha também são no granito marrom,
# levemente escurecido"; eram o quartzito Carrara de 21/10), como a ilha do gourmet:
# - a ilha (1,90 x 1,20 m) em granito um pouco mais escuro que o piso, com a borda e a sombra curta, as laterais em
#   cascata das pontas no tom da borda, e o cooktop de 5 bocas da biblioteca redesenhado por cima (as banquetas, fora do
#   tampo, ficam);
# - a bancada da pia, na parede da direita, no mesmo granito, com a área molhada rebaixada (um tom abaixo) e as duas
#   cubas de inox com as torneiras redesenhadas no PDF.
COZINHA = {"ilha": (1717.9, 1409.5, 1825.6, 1477.5), "cooktop": (1746.8, 1446.4, 1796.7, 1474.7),
           "laterais": [((1720.2, 1409.5), (1720.2, 1477.5)), ((1823.4, 1409.5), (1823.4, 1477.5))],
           "pia": (1888.0, 1395.3, 1922.0, 1670.3), "molhada": (1890.3, 1477.5, 1922.0, 1615.3),
           "cubas": [{"cuba": (1892.0, 1484.9, 1916.9, 1521.2), "bacia": (1893.4, 1486.3, 1915.5, 1519.8),
                      "torneira": (1908.6, 1501.4, 1919.7, 1502.6), "base": (1919.6, 1502.0, 1.3)},
                     {"cuba": (1892.0, 1530.3, 1916.9, 1566.5), "bacia": (1893.4, 1531.7, 1915.5, 1565.1),
                      "torneira": (1908.6, 1546.8, 1919.7, 1548.0), "base": (1919.6, 1547.4, 1.3)}],
           "semente": 2710}


def cozinha(Q, img):
    q, i = COZINHA, ILHA
    pedra = lambda s, k: (lambda tl: FA._granito(Q, tl, s) * k)
    out = FA.bancada_pedra(Q, np.ascontiguousarray(img.copy()), q["ilha"], pedra(q["semente"], i["escurecer"]),
                           i["borda"], i["larg"], i["sombra"])
    out = linhas_pedra(Q, out, q["laterais"], i["linha_px"], i["linha"])
    out = cooktop(Q, out, q["cooktop"])
    out = FA.bancada_pedra(Q, out, q["pia"], pedra(q["semente"] + 1, i["escurecer"]), i["borda"], i["larg"],
                           i["sombra"])
    out = FA.bancada_pedra(Q, out, q["molhada"], pedra(q["semente"] + 2, i["molhada_esc"]), i["borda"], i["larg"], 0.0)
    for c in q["cubas"]:
        out = cuba_inox(Q, out, c)
    print("    cozinha: a ilha e a bancada da pia em granito marrom um pouco mais escuro que o piso, com a borda e a "
          "sombra; as laterais em cascata e o cooktop da ilha; a área molhada rebaixada e as duas cubas de inox")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 4. As paredes (E10; resposta do usuário: cinza 80) nos preenchimentos escuros da ARQ_PAREDE (com os muros do lote),
# com antialias, como no Subsolo (`final3840_casaa.paredes`): antes, o preto das paredes antigas que passa do PDF (a
# franja de 1 a 3 px) é refeito com o que está em volta. Os pilares redondos da varanda e do gourmet (EST - Pilar,
# soltos) já são pretos e ficam; os brises (preenchimentos brancos no PDF) também.
# Os muros do lote: a linha preta da final (em cima, embaixo e à esquerda) fica uns 5 px fora dos muros do PDF (as
# faixas de mais de 300 pt, que saem do contorno do PDF, `max_pt`); ela mesma passa a cinza 80, px a px pelo escuro
# (`muros`: as faixas do quadro em volta do lote), para não dobrar a espessura.
PAREDES_T = dict(FA.PAREDES_A, divisoria=None, encostos=[], max_pt=300)
MUROS = {"faixas": [(262, 140, 3445, 186), (262, 1912, 3445, 1962), (262, 140, 300, 1962), (3398, 140, 3445, 1962)],
         "escuro": (110, 20), "croma": 18}


def paredes(Q, img):
    out = FA.paredes(Q, img, PAREDES_T).astype(np.float32)
    q = MUROS
    lo, hi = q["escuro"][1], q["escuro"][0]
    n = 0
    for x0, y0, x1, y1 in q["faixas"]:
        reg = out[y0:y1, x0:x1]
        lum, croma = reg.max(axis=2), reg.max(axis=2) - reg.min(axis=2)
        w = (np.clip((hi - lum) / (hi - lo), 0, 1) * (croma < q["croma"]))[..., None]
        out[y0:y1, x0:x1] = reg * (1 - w) + np.float32(PAREDES_T["cor"]) * w
        n += int((w > 0.5).sum())
    print(f"    muros do lote: a linha preta da final em cinza {PAREDES_T['cor'][0]} ({n} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 5. As escadas (E3, E8): sem o triângulo (R14) e sem linhas (usuário, 26/10/26, no Subsolo: "não precisa constar
# linhas, mas sim sombras denotando que o sentido é de subida"): os degraus marcados só pelo sombreamento das escadas
# aprovadas (cada degrau um pouco mais claro que o de baixo, `tom`, e a sombra curta de cada espelho no degrau de
# baixo, `espelho`); depois do corte, o trecho esmaecido, como antes. A letra do PDF (S ou D) em Inter SemiBold, cinza
# quase preto, na origem do texto do PDF.
LETRA = {"fonte": "Inter-SemiBold.otf", "corpo_px": 17, "cor": (45, 45, 45)}


def letra(Q, out, texto, origem_pt=None, centro_q=None):
    """A letra do sentido: na origem do texto do PDF (pt) ou centrada num ponto do quadro (px)."""
    from PIL import Image, ImageDraw, ImageFont
    from rodape_entrega import FONTES
    q = LETRA
    fonte = ImageFont.truetype(str(FONTES / q["fonte"]), q["corpo_px"] * 4)
    ox, oy = Q.p2q(*origem_pt) if origem_pt else centro_q
    W = H = q["corpo_px"] * 3
    X0, Y0 = int(ox) - W // 2, int(oy) - H // 2
    t = Image.new("L", (W * 4, H * 4), 0)
    ImageDraw.Draw(t).text(((ox - X0) * 4, (oy - Y0) * 4), texto, font=fonte, fill=255,
                           anchor="ls" if origem_pt else "mm")
    a = np.asarray(t.resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(reg * (1 - a) + np.float32(q["cor"]) * a, 0, 255).astype(np.uint8)
    return out


def sem_triangulo(out, caixa_q, lum=125):
    """O triângulo antigo: os px escuros na caixa dele, refeitos com o que está em volta."""
    x0, y0, x1, y1 = caixa_q
    reg = out[y0:y1, x0:x1]
    tri = cv2.dilate((reg.astype(np.float32).mean(axis=2) < lum).astype(np.uint8), np.ones((5, 5), np.uint8))
    out[y0:y1, x0:x1] = cv2.inpaint(reg, tri, 4, cv2.INPAINT_TELEA)
    return out


# 5a. O lance do deck abaixo do spa (o mesmo do Subsolo, nas mesmas coordenadas do PDF): desce do deck de madeira (à
# esquerda) para o subsolo, o D do PDF no degrau de cima (a origem do PDF fica na borda do deck, metade fora). Os degraus em Bege Bahia, como no Subsolo aprovado (`degraus_bege`),
# com o mesmo sombreamento (o degrau de cima, junto ao deck, o mais claro); como na final aprovada, cheio até a marca de
# corte e esmaecido depois (à direita), sem a sombra no pátio (no Térreo, embaixo é o subsolo).
DECK_T = dict(FA.DEGRAUS_A, corte=((754.4, 1234.5), (787.7, 1299.4)), esmaece="direita", patio=None, semente=2701,
              texto="D", centro=((735.4 + 754.1) / 2, 1265.0), triangulo_q=(900, 1080, 935, 1112))

# 5b. Os degraus escalonados entre o deck de madeira e o deck da piscina (12 a 18 do PDF; o 19 é o deck da piscina):
# os 7 blocos de Bege Bahia da ARQ_CONTRAPISO, do mais baixo (à esquerda, no deck de madeira) ao mais alto (junto ao
# deck da piscina), cada um por cima do de baixo, com a sombra curta dele no degrau de baixo, no deck e na grama, o tom
# de cada degrau um pouco mais claro que o de baixo, sem contorno; o D (o PDF não tem letra: do Térreo, eles descem) no
# degrau de cima.
PISANTES = {"blocos": [(640.8, 666.8, 714.5, 794.4), (674.8, 632.8, 748.5, 771.7), (708.8, 564.8, 782.5, 754.7),
                       (742.8, 576.1, 816.5, 740.5), (776.8, 553.4, 844.8, 726.4), (822.2, 576.1, 867.5, 715.0),
                       (861.9, 544.9, 907.2, 703.7)],
            "tom": (0.88, 1.0), "tom_degrau": 0.02, "forca": 0.85, "sombra": (0.42, 1.8, 1.6), "semente": 2702,
            "texto": "D", "triangulo_q": (800, 520, 835, 555)}

# 5c. A escada interna do jardim (em U, travertino): sobe do hall (o S do PDF no 1º degrau: a origem do PDF cai no vidro
# junto à escada), o 1º
# lance da esquerda para a direita, o patamar à direita e o 2º lance de volta à esquerda. Cheia até a marca de corte do
# 7º degrau, como na final aprovada (a diagonal), e esmaecida depois. Os traços dos degraus e o tracejado do trecho
# esmaecido saem (a mediana de 7 px dentro da escada); o trecho cheio no travertino bruto do piso (26/10/26), com o
# sombreamento inteiro; o esmaecido, o da final, com o sombreamento mais fraco (`esmaecido`).
ESCADA_U = {"piso": 17.0, "lance1": (2021.2, 1094.9, 2174.3, 1162.9), "patamar": (2174.3, 1094.9, 2242.3, 1253.6),
            "lance2": (2019.5, 1185.6, 2174.3, 1253.6), "corte": ((2122.5, 1092.9), (2155.7, 1161.7)),
            "tom": (0.90, 1.0), "espelho": (0.28, 2.4), "esmaecido": 0.40, "mediana": 7, "semente": 2709,
            "texto": "S", "centro": ((2021.2 + 2038.2) / 2, 1128.9), "triangulo_q": (2258, 938, 2282, 960)}


def deck(Q, img):
    q = DECK_T
    out = sem_triangulo(img.copy(), q["triangulo_q"])
    out = FA.degraus_bege(Q, out, q)
    out = letra(Q, out, q["texto"], centro_q=Q.p2q(*q["centro"]))
    print(f"    lance do deck: sem o triângulo e sem linhas; o {q['texto']} no degrau de cima")
    return out


def pisantes(Q, img):
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from texturas import textura
    q = PISANTES
    out = sem_triangulo(np.ascontiguousarray(img.copy()), q["triangulo_q"])
    bl = q["blocos"]
    caixa = (min(b[0] for b in bl), min(b[1] for b in bl), max(b[2] for b in bl), max(b[3] for b in bl))
    tl = tela(out, Q, caixa, folga=8)
    T = textura("bege_bahia", Q.px_m, tl.h, tl.w, semente=q["semente"]).astype(np.float32)
    T = (1 + q["forca"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(FA.PISOS_A["Bege Bahia"]["tom"])
    rng = np.random.default_rng(q["semente"])
    n = len(bl)
    t0, t1 = q["tom"]
    fs, dist, sig = q["sombra"]
    for k, r in enumerate(bl):                               # do mais baixo ao mais alto, cada um por cima
        m = tl.ret(r)
        sombra_q(tl, m, forca=fs, dist=dist, sigma=sig)
        f = (t0 + (t1 - t0) * k / (n - 1)) * (1 + rng.uniform(-q["tom_degrau"], q["tom_degrau"]))
        tl.pintar_img(m, T * f)
    out = tl.gravar()
    x0, y0, x1, y1 = bl[-1]
    out = letra(Q, out, q["texto"], centro_q=Q.p2q((x0 + x1) / 2, (y0 + y1) / 2))
    print(f"    degraus escalonados: {n} blocos em Bege Bahia, sem contorno, cada um com a sombra no de baixo; "
          f"o {q['texto']} no de cima")
    return out


def escada_u(Q, img):
    q = ESCADA_U
    out = sem_triangulo(np.ascontiguousarray(img.copy()), q["triangulo_q"])
    rets = [q["lance1"], q["patamar"], q["lance2"]]
    caixa = (min(r[0] for r in rets), min(r[1] for r in rets), max(r[2] for r in rets), max(r[3] for r in rets))
    tl = tela(out, Q, caixa, folga=4)
    X, Y = tl.grade()
    dentro = np.zeros((tl.h, tl.w), bool)
    for r in rets:
        dentro |= (X >= r[0]) & (X <= r[2]) & (Y >= r[1]) & (Y <= r[3])
    # sem os traços: a mediana dentro da escada (com 2 px de folga, para os contornos)
    dil = cv2.dilate(dentro.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    med = cv2.medianBlur(np.clip(tl.reg, 0, 255).astype(np.uint8), q["mediana"]).astype(np.float32)
    tl.reg = np.where(dil[..., None], med, tl.reg)
    # o sombreamento: no 1º lance, sobe para a direita; no 2º, para a esquerda (o patamar é o degrau entre os dois)
    p, (t0, t1), (fs, alc) = q["piso"], q["tom"], q["espelho"]
    f = np.ones((tl.h, tl.w), np.float32)
    a0, b0, a1, b1 = q["lance1"]
    n1 = int(round((a1 - a0) / p))
    k = np.clip(((X - a0) // p).astype(int), 0, n1 - 1)
    l1 = (X >= a0) & (X <= a1) & (Y >= b0) & (Y <= b1)
    xb = a0 + (k + 1) * p                                       # o espelho do degrau de cima (à direita)
    f1 = (t0 + (t1 - t0) * k / n1) * (1 - fs * np.exp(-np.maximum((xb - X) * PT_PX, 0) / alc))
    f = np.where(l1, f1, f)
    c0, d0, c1, d1 = q["lance2"]
    n2 = int(np.ceil((c1 - c0) / p))
    j = np.clip(((c1 - X) // p).astype(int), 0, n2 - 1)
    l2 = (X >= c0) & (X <= c1) & (Y >= d0) & (Y <= d1)
    xb2 = c1 - (j + 1) * p                                      # o espelho do degrau de cima (à esquerda)
    f2 = (t1 - 0.02) * (1 - fs * np.exp(-np.maximum((xb2 - X) * -PT_PX, 0) / alc) * (j < n2 - 1))
    f = np.where(l2, f2, f)
    pa = (X >= q["patamar"][0]) & (Y >= q["patamar"][1]) & (Y <= q["patamar"][3]) & (X <= q["patamar"][2])
    fp = t1 * np.where((Y >= d0) & (Y <= d1), 1 - fs * np.exp(-np.maximum((X - c1) * PT_PX, 0) / alc), 1.0)
    f = np.where(pa, fp, f)
    (x0, y0), (x1, y1) = q["corte"]
    cheio = l1 & (X < x0 + (x1 - x0) / (y1 - y0) * (Y - y0))
    # o trecho cheio no travertino bruto do piso (`travertino_t`, 26/10/26), cada degrau com o tom um pouco diferente
    rng = np.random.default_rng(q["semente"])
    tons = 1 + rng.uniform(-0.02, 0.02, n1)
    T = travertino_t(Q, tl.h, tl.w, q["semente"]) * tons[k][..., None]
    tl.reg = np.where(cheio[..., None], T, tl.reg)
    e = q["esmaecido"]
    f = np.where(cheio, f, 1 - e * (1 - f))
    tl.reg *= np.where(dentro, f, 1.0)[..., None]
    out = tl.gravar()
    out = letra(Q, out, q["texto"], centro_q=Q.p2q(*q["centro"]))
    print(f"    escada interna: {n1} + {n2} degraus sem linhas, com o sombreamento de subida (cheia até o corte do 7º, "
          f"esmaecida depois); o {q['texto']} no 1º degrau")
    return out


# 5d. A escada caracol da área de serviço (sobe ao 1º Pavimento; S na origem do PDF): os degraus em leque em volta do
# pilar, sem as linhas, no tom claro da final aprovada, do 1º (a 4,2°, à direita do pilar) em sentido anti-horário,
# cada um um pouco mais claro que o de baixo e com a sombra curta do espelho do de cima; cheia até a marca de corte do
# PDF (~150°), como na final aprovada (o arco cheio destacado), e esmaecida depois (um véu claro sobre o granito, com o
# mesmo sombreamento mais fraco, no lugar do tracejado). O pilar no centro em preto (E10) e o corrimão em volta.
CARACOL = {"centro": (1756.42, 1718.8), "r_pilar": 4.0, "r_degrau": 50.6, "r_corrimao": 52.3, "a0": 4.21,
           "passo": 17.78, "corte": 150.0, "tom": (148, 174, 206), "tons": (0.84, 1.0), "espelho": (0.30, 2.2),
           "veu": ((236, 236, 234), 0.40), "esmaecido": 0.45, "corrimao": ((84, 112, 148), 1.3, 0.45),
           "pilar": (24, 24, 24), "textura": 0.45, "semente": 2703, "texto": "S", "origem": (1783.4, 1727.9)}


def caracol(Q, img):
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from texturas import textura
    q = CARACOL
    cx, cy = q["centro"]
    R = q["r_corrimao"] + 1.5
    tl = tela(np.ascontiguousarray(img.copy()), Q, (cx - R, cy - R, cx + R, cy + R), folga=3)
    S = 8
    # a grade em ss (a cobertura exata das bordas dos degraus)
    ys, xs = np.mgrid[0:tl.h * S, 0:tl.w * S].astype(np.float32)
    (ax, ay), (bx, by) = Q.q2p(tl.x0, tl.y0), Q.q2p(tl.x0 + 1, tl.y0 + 1)
    X, Y = ax + (xs + 0.5) / S * (bx - ax), ay + (ys + 0.5) / S * (by - ay)
    r = np.hypot(X - cx, Y - cy)
    th = (np.degrees(np.arctan2(-(Y - cy), X - cx)) - q["a0"]) % 360            # 0 no espelho do 1º degrau
    k = (th // q["passo"]).astype(int)                                             # o degrau (0 = 1º)
    n = int(np.ceil(360 / q["passo"]))
    t0, t1 = q["tons"]
    f = t0 + (t1 - t0) * np.clip(k, 0, n - 1) / (n - 1)
    fs, alc = q["espelho"]
    dist = ((k + 1) * q["passo"] - th) * np.pi / 180 * r * PT_PX                   # px até o espelho do de cima
    f = f * (1 - fs * np.exp(-np.maximum(dist, 0) / alc))
    degrau = (r >= q["r_pilar"]) & (r <= q["r_degrau"])
    cheio = degrau & (th <= q["corte"] - q["a0"])
    def red(m):
        return cv2.resize(m.astype(np.float32), (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    fr = red(f * degrau) / np.maximum(red(degrau), 1e-4)
    a_cheio, a_degrau = red(cheio), red(degrau)
    T = textura("travertino", Q.px_m, tl.h, tl.w, semente=q["semente"]).astype(np.float32)
    T = (1 + q["textura"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(q["tom"])
    # o trecho esmaecido: o véu claro sobre o que está embaixo (o granito), com o sombreamento mais fraco
    cv, fv = q["veu"]
    e = q["esmaecido"]
    esm = (tl.reg * (1 - fv) + np.float32(cv) * fv) * (1 - e * (1 - fr))[..., None]
    a_esm = np.clip(a_degrau - a_cheio, 0, 1)[..., None]
    tl.reg = tl.reg * (1 - a_esm) + esm * a_esm
    tl.reg = tl.reg * (1 - a_cheio[..., None]) + (T * fr[..., None]) * a_cheio[..., None]
    # o corrimão em volta (cheio no trecho cheio, fraco no esmaecido) e o pilar preto
    cor, larg, fraco = q["corrimao"]
    anel = np.abs(r - q["r_corrimao"]) <= larg / PT_PX / 2
    a_anel = red(anel & (th <= q["corte"] - q["a0"])) + fraco * red(anel & (th > q["corte"] - q["a0"]))
    tl.reg = tl.reg * (1 - a_anel[..., None]) + np.float32(cor) * a_anel[..., None]
    a_pilar = red(r < q["r_pilar"])[..., None]
    tl.reg = tl.reg * (1 - a_pilar) + np.float32(q["pilar"]) * a_pilar
    out = tl.gravar()
    out = letra(Q, out, q["texto"], origem_pt=q["origem"])
    print(f"    caracol: {n} degraus em leque sem linhas, com o sombreamento de subida (cheia até o corte, esmaecida "
          f"depois), o pilar preto e o corrimão; o {q['texto']} na origem do PDF")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 5e. As projeções tracejadas (usuário, 26/10/26: "a projeção em tracejado precisa ficar evidente. Em fundos escuros,
# faça a projeção com tom branco; para tons claros, marque-as com tom preto tracejado"): os traços do PDF redesenhados
# nítidos por cima de tudo, cada traço em preto ou branco pelo fundo em volta dele (a luminância mediana de uma faixa
# de `fundo_px`, sem o próprio traço). Quais (as cadeias de traços colineares com vãos, `cadeias_tracejadas`):
# - DOC_LINHAS E PROJEÇÕES: o pavimento superior (os dois X da varanda e do estar), a claraboia do lavabo, a laje
#   superior da área de serviço e o X da área de serviço descoberta; ficam de fora os afastamentos e os limites do lote
#   (retas de mais de `max_doc_pt`, somados os trechos), as que caem dentro das paredes e os X do elevador e do shaft
#   (`fora_q`);
# - ARQ_PERGOLADO: a grade do pergolado sobre a prainha;
# - ARQ_CONTRAPISO: o contorno de fora da cobertura (`cobertura`: as cadeias da final aprovada; o contorno de dentro e
#   os desenhos dos pisos, como a pedra portuguesa, ficam de fora).
PROJ = {"max_doc_pt": 900, "fora_q": [(2250, 1100, 2395, 1215)], "larg_px": 1.5, "fundo_px": 9, "limiar": 120,
        "preto": (30, 30, 30), "branco": (250, 250, 250), "ss": 4,
        "cobertura": [(0.0, 300), (90.0, 1486), (90.0, 2635), (0.0, 1673), (0.0, 1177)]}


def cadeias_tracejadas(Q, camadas, min_n=4, min_ext=40, max_cob=0.9):
    """As linhas tracejadas do PDF: os traços retos colineares (mesma direção, a cada 0,5°, e mesma distância à origem,
    pela direção do próprio traço, a 1 pt; as faixas vizinhas juntas, para a reta longa não se partir no arredondamento)
    em cadeias com vãos (a cobertura do traço no comprimento até `max_cob`)."""
    from collections import defaultdict
    grupos = defaultdict(list)
    for d in Q.desenhos:
        if d["type"] != "s" or d.get("layer") not in camadas:
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            x0, y0, x1, y1 = it[1].x, it[1].y, it[2].x, it[2].y
            if np.hypot(x1 - x0, y1 - y0) < 0.5:
                continue
            g = np.degrees(np.arctan2(y1 - y0, x1 - x0)) % 180
            a = round(g * 2) / 2 % 180
            t = np.radians(g)
            off = -np.sin(t) * (x0 + x1) / 2 + np.cos(t) * (y0 + y1) / 2
            u0, u1 = sorted((np.cos(t) * x0 + np.sin(t) * y0, np.cos(t) * x1 + np.sin(t) * y1))
            grupos[(d.get("layer"), a, int(round(off)))].append((u0, u1, (x0, y0, x1, y1)))
    # as faixas vizinhas (1 pt) da mesma direção numa só
    juntos, feito = {}, set()
    for k in sorted(grupos):
        if k in feito:
            continue
        cam, a, o = k
        v, j = [], o
        while (cam, a, j) in grupos:
            v += grupos[(cam, a, j)]
            feito.add((cam, a, j))
            j += 1
        juntos[(cam, a, (o + j - 1) / 2)] = v
    out = []
    for k, v in juntos.items():
        v.sort()
        med = np.median([b - a for a, b, _ in v])
        g = [v[0]]
        for s_ in v[1:] + [None]:
            if s_ is not None and s_[0] - g[-1][1] <= max(3 * med, 6):
                g.append(s_)
                continue
            ext = g[-1][1] - g[0][0]
            if len(g) >= min_n and ext >= min_ext and sum(b - a for a, b, _ in g) / max(ext, 1e-6) <= max_cob:
                out.append((k, ext, [seg for _, _, seg in g]))
            if s_ is not None:
                g = [s_]
    return out


def projecoes(Q, img):
    q = PROJ
    par = FA.paredes_pdf(Q)
    tracos = []
    doc = cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"])
    def total(k):                                           # a reta inteira: os trechos da mesma direção a até 2 pt
        return sum(e for k2, e, _ in doc if k2[1] == k[1] and abs(k2[2] - k[2]) <= 2)
    for k, ext, segs in doc:
        if total(k) > q["max_doc_pt"]:
            continue
        xm, ym = Q.p2q(*np.mean([((x0 + x1) / 2, (y0 + y1) / 2) for x0, y0, x1, y1 in segs], axis=0))
        if par[int(ym), int(xm)] > 0.5 or any(a <= xm <= c and b <= ym <= d for a, b, c, d in q["fora_q"]):
            continue
        tracos += segs
    tracos += [seg for _, _, segs in cadeias_tracejadas(Q, ["ARQ_PERGOLADO"]) for seg in segs]
    for (cam, a, off), ext, segs in cadeias_tracejadas(Q, ["ARQ_CONTRAPISO"], min_ext=120):
        if a not in (0.0, 90.0):
            continue
        x0, y0, x1, y1 = segs[0]
        pos = Q.p2q(x0, y0)[1] if a == 0.0 else Q.p2q(x0, y0)[0]
        if any(a == ca and abs(pos - cp) < 4 for ca, cp in q["cobertura"]):
            tracos += segs
    out, n_b = preto_branco(Q, img, tracos)
    print(f"    projeções tracejadas: {len(tracos)} traços do PDF, {len(tracos) - n_b} em preto (fundo claro) e "
          f"{n_b} em branco (fundo escuro)")
    return out


def preto_branco(Q, img, tracos, q=None):
    """Os traços do PDF (pt) nítidos por cima de tudo, cada um em preto ou branco pelo fundo em volta dele."""
    q = q or PROJ
    out = img.astype(np.float32)
    lum = img.astype(np.float32).mean(axis=2)
    S, w = q["ss"], q["larg_px"]
    n_b = 0
    for x0, y0, x1, y1 in tracos:
        (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
        bx0, by0 = int(min(u0, u1)) - q["fundo_px"], int(min(v0, v1)) - q["fundo_px"]
        bx1, by1 = int(max(u0, u1)) + q["fundo_px"] + 1, int(max(v0, v1)) + q["fundo_px"] + 1
        bx0, by0, bx1, by1 = max(bx0, 0), max(by0, 0), min(bx1, Q.W), min(by1, Q.H)
        m = np.zeros(((by1 - by0) * S, (bx1 - bx0) * S), np.uint8)
        cv2.line(m, (int((u0 - bx0) * S), int((v0 - by0) * S)), (int((u1 - bx0) * S), int((v1 - by0) * S)), 255,
                 max(1, int(round(w * S))), cv2.LINE_AA)
        a = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)
        fundo = lum[by0:by1, bx0:bx1][a < 0.02]
        claro = np.median(fundo) >= q["limiar"] if fundo.size else True
        cor = np.float32(q["preto"] if claro else q["branco"])
        n_b += not claro
        out[by0:by1, bx0:bx1] = out[by0:by1, bx0:bx1] * (1 - a[..., None]) + cor * a[..., None]
    return np.clip(np.round(out), 0, 255).astype(np.uint8), n_b


# ----------------------------------------------------------------------------------------------------------------------
# 6. E4: a seta da entrada principal: cheia, preta, ~1,5 m, no piso do hall externo (Bege Bahia), apontando para a porta
# pivotante (a entrada vem pelos pisantes do leste), abaixo do rótulo do hall (acima, ficava na linha da folha da porta
# aberta e parecia continuá-la). Medidas em m: o comprimento, a cabeça (comprimento e largura) e a haste; a `ponta` em
# px do quadro.
SETA = {"ponta": (2470, 800), "comp_m": 1.5, "cabeca_m": (0.40, 0.46), "haste_m": 0.14, "cor": (28, 28, 28), "ss": 8}


def seta(Q, img):
    q = SETA
    S, k = q["ss"], Q.px_m
    (px, py) = q["ponta"]
    comp, (hc, hl), hs = q["comp_m"] * k, (q["cabeca_m"][0] * k, q["cabeca_m"][1] * k), q["haste_m"] * k
    x0, y0, x1, y1 = int(px - 4), int(py - hl / 2 - 4), int(px + comp + 4), int(py + hl / 2 + 4)
    m = np.zeros(((y1 - y0) * S, (x1 - x0) * S), np.uint8)
    def P(x, y):
        return ((x - x0) * S, (y - y0) * S)
    pts = [P(px, py), P(px + hc, py - hl / 2), P(px + hc, py - hs / 2), P(px + comp, py - hs / 2),
           P(px + comp, py + hs / 2), P(px + hc, py + hs / 2), P(px + hc, py + hl / 2)]
    cv2.fillPoly(m, [np.int32(np.round(pts))], 255, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)[..., None]
    out = img.copy()
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.float32(q["cor"]) * a, 0, 255).astype(np.uint8)
    print(f"    entrada principal: a seta de {q['comp_m']:.1f} m no hall externo, apontando para a porta pivotante")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 7. Os rótulos, como na final aprovada (`rotulos_casaa.final_rotulos`: o corpo do PDF ampliado, os desvios aprovados,
# branco no granito), com dois desvios novos (E7):
# - LAVABO: no corpo do PDF (1,0), para a área não encostar na bancada (o lavabo tem ~1 m de piso livre);
# - SALA DE ESTAR: fora do tapete ("O tapete conta como objeto, sim"), no piso livre entre a borda do tapete e as
#   poltronas do estar sob a projeção.
AJUSTES_T = {"LAVABO": ("LAVABO", (1192.4, 224.3), (-2.5, 0), 1.0),
             # usuário, 26/10/26: "o escrito do b. motorista pode ficar mais abaixo e centralizado": no meio do piso seco
             # (entre o box e a parede da direita), abaixo do vaso e da cuba
             "B. MOTORISTA": ("B. MOTORISTA", (1211.8, 661.1), (7.3, 1.0), 0.9),
             "SALA DE ESTAR": ("SALA DE ESTAR", (1074.6, 270.8), (-14.6, 61.5))}


def rotulos(Q, img):
    import retoque_1pav_casae as R1
    q = A.PAVIMENTOS["Terreo"]
    rot = [r for r in R1.rotulos_pdf(Q.pg) if r[0] in q.get("incluir", ()) or not any(f in r[0] for f in A.FORA)]
    ajustes = [AJUSTES_T.get(a[0], a) for a in q["ajustes"]]
    out = R1.rotulos_ambientes(img, rot, Q.p2q, escala_desvio=A.LARGURA / 2000,
                               granito=A.granito(img, q.get("granito_lum_max")), ajustes=ajustes,
                               cor_granito=R1.ROTULOS["branco"])
    print(f"    {len(rot)} rótulos, com os desvios aprovados; LAVABO no corpo do PDF e SALA DE ESTAR fora do tapete")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Pedidos de 28/10/26 no Térreo (com a final já no turquesa e nas bordas retas de `piscinas_turquesa.py`):
# - "faltou o box do banho varanda. incluir.": o box de correr do PDF (horizontal, entre o vaso e o chuveiro), de que o
#   render só deixou um traço azul fraco, como os boxes do Subsolo (`final3840_casaa.boxes`): as duas folhas de vidro
#   contínuas, desencontradas, com as faces finas e a sombra curta (desde o pedido seguinte, fechadas, de parede a
#   parede, sem o trilho tracejado);
# - "limpe esses resquicios" e "corrija o contorno do marmore bege bahia, removendo esses resquicios": as pecinhas
#   cinza-rosadas na borda de cima do Bege Bahia junto à grama (a cada coluna, o que não é grama logo acima da linha da
#   borda), refeitas com a borda e a grama de uma coluna limpa ao lado; na placa de pedra da ponta direita do caminho,
#   a faixa rosada para fora do lote (o branco da prancha, como acima dela), o tufo de folhas sobre a borda de cima da
#   placa e o risco claro na grama entre as placas.
BOX_VARANDA = {"meio": 1712.8}
LIMPEZA_2810 = {
    # a borda de cima do Bege Bahia: as colunas (px), a linha da borda (a primeira de pedra), as linhas refeitas acima e
    # abaixo dela, a grama (g - b mínimo), os tracejados brancos da projeção na grama (protegidos) e a transição (px)
    "bege_topo": {"x": (1083, 1512), "linha": 340, "acima": 6, "abaixo": 4, "grama_gb": 30, "branco": 215, "suave": 2},
    # a placa da ponta direita: (x0, y0, x1, y1) de cada remendo e de onde vem (dx, dy)
    "remendos": [((3430, 712, 3442, 867), "linha", 690), ((3430, 867, 3442, 881), "linha", 890),
                 ((3331, 602, 3359, 619), "desloca", (0, 17)), ((3260, 655, 3269, 679), "desloca", (0, 26))],
}


def box_varanda(Q, img):
    out = FA.boxes(Q, np.ascontiguousarray(img.copy()),
                   so=lambda b: b["hor"] and abs(b["meio"] - BOX_VARANDA["meio"]) < 1)
    print("    banho varanda: o box de correr (as duas folhas de vidro contínuas, de parede a parede)")
    return out


def _colar(out, src, x0, y0, x1, y1, suave):
    """Cola src[y0:y1, x0:x1] em out com a transição de `suave` px nas bordas do remendo."""
    h, w = y1 - y0, x1 - x0
    ay = np.clip(np.minimum(np.arange(h) + 1, h - np.arange(h)) / (suave + 1), 0, 1)
    ax = np.clip(np.minimum(np.arange(w) + 1, w - np.arange(w)) / (suave + 1), 0, 1)
    a = (ay[:, None] * ax[None, :])[..., None]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - a) + src.astype(np.float32) * a), 0, 255).astype(np.uint8)


def limpeza_2810(Q, img):
    q = LIMPEZA_2810
    out = np.ascontiguousarray(img.copy())
    t = q["bege_topo"]
    x0, x1 = t["x"]
    L, ac, ab, sv = t["linha"], t["acima"], t["abaixo"], t["suave"]
    a = img.astype(np.int32)
    faixa = a[L - ac:L, x0:x1]
    nao_grama = (faixa[..., 1] - faixa[..., 0] < t["grama_gb"])
    branco = faixa.min(axis=2) > t["branco"]
    longe = a[L - 30:L - ac - 2, x0:x1]
    tracejado = (longe.min(axis=2) > t["branco"]).any(axis=0)
    tracejado = np.convolve(tracejado, np.ones(5), "same") > 0
    ruim = (nao_grama & ~branco).any(axis=0) & ~tracejado
    ruim = (np.convolve(ruim, np.ones(2 * sv + 1), "same") > 0) & ~tracejado
    corridas, i = [], 0
    while i < len(ruim):
        if ruim[i]:
            j = i
            while j < len(ruim) and ruim[j]:
                j += 1
            corridas.append((i, j))
            i = j
        else:
            i += 1
    feitas = 0
    for i, j in corridas:
        n = j - i
        for dx in [-(n + 8), n + 8, -(2 * n + 12), 2 * n + 12]:
            s0, s1 = i + dx, j + dx
            if s0 >= 0 and s1 <= len(ruim) and not ruim[s0:s1].any() and not tracejado[s0:s1].any():
                y0, y1 = L - ac - sv, L + ab + sv
                _colar(out, img[y0:y1, x0 + s0:x0 + s1], x0 + i, y0, x0 + j, y1, sv)
                feitas += 1
                break
    for (r0, r1, r2, r3), modo, de in q["remendos"]:
        if modo == "linha":
            src = np.repeat(img[de:de + 1, r0:r2], r3 - r1, axis=0)
            out[r1:r3, r0:r2] = src
        else:
            dx, dy = de
            _colar(out, img[r1 + dy:r3 + dy, r0 + dx:r2 + dx], r0, r1, r2, r3, 2)
    print(f"    contorno do Bege Bahia junto à grama: {feitas} de {len(corridas)} trechos com resquícios refeitos; a placa "
          f"da ponta direita sem a faixa rosada fora do lote, sem o tufo na borda e sem o risco na grama")
    return out


# A borda de baixo da varanda junto à grama (usuário, 28/10/26: "pode corrigir a borda de baixo da varanda também"):
# entre o pilar preto e a parede do lavatório, uma faixa cinza-rosada de 2 a 4 px com dentes e trechos escuros soltos.
# A beira fica reta na linha do PDF (o fim do piso da varanda, 1786,5 pt): por cima, o travertino espelhado do piso de
# logo acima; por baixo, a grama espelhada da de logo abaixo; na linha, o meio-termo do antialias.
VARANDA_BAIXO = {"x": (1251, 1476), "linha_pt": 1786.5, "faixa": 6}


def varanda_baixo(Q, img):
    q = VARANDA_BAIXO
    out = np.ascontiguousarray(img.copy())
    x0, x1 = q["x"]
    L = Q.p2q(0, q["linha_pt"])[1]
    Li, f = int(np.floor(L)), q["faixa"]
    src = img.astype(np.float32)
    for y in range(Li - f, Li + f + 1):
        if y < Li:
            linha = src[2 * (Li - f) - 1 - y, x0:x1]                   # o piso, espelhado em volta de Li - f
        elif y > Li:
            linha = src[2 * (Li + f) + 1 - y, x0:x1]                   # a grama, espelhada em volta de Li + f
        else:
            a = L - Li                                                  # a fração do px Li que ainda é piso
            linha = src[2 * (Li - f) - 1 - (Li - 1), x0:x1] * a + src[2 * (Li + f) + 1 - (Li + 1), x0:x1] * (1 - a)
        out[y, x0:x1] = np.clip(np.round(linha), 0, 255).astype(np.uint8)
    print(f"    varanda: a borda de baixo junto à grama reta na linha do PDF ({L:.1f} px), de x {x0} a {x1}")
    return out


def passos_terreo(Q, ini):
    return [
        ("granito", lambda im: granito(Q, im)),
        ("travertino", lambda im: travertino(Q, im)),
        ("motorista", lambda im: motorista(Q, im)),
        ("box_motorista", lambda im: box_motorista(Q, im)),
        ("loucas", lambda im: loucas(Q, im)),
        ("ilha", lambda im: ilha(Q, im)),
        ("cozinha", lambda im: cozinha(Q, im)),
        ("lavabo", lambda im: lavabo(Q, im)),
        ("paredes", lambda im: paredes(Q, im)),
        ("deck", lambda im: deck(Q, im)),
        ("pisantes", lambda im: pisantes(Q, im)),
        ("escada_u", lambda im: escada_u(Q, im)),
        ("caracol", lambda im: caracol(Q, im)),
        ("projecoes", lambda im: projecoes(Q, im)),
        ("seta", lambda im: seta(Q, im)),
        ("rotulos", lambda im: rotulos(Q, im)),
        ("box_varanda", lambda im: box_varanda(Q, im)),
        ("limpeza_2810", lambda im: limpeza_2810(Q, im)),
        ("varanda_baixo", lambda im: varanda_baixo(Q, im)),
    ]


# O antes e o depois de cada item (a final aprovada até aqui, com os rótulos, e a nova), recortes no quadro (px)
ANTES_DEPOIS = {"planta": (700, 300, 3420, 1980), "granito": (1450, 1100, 2750, 1700),
                "motorista": (2240, 1080, 2560, 1330), "lavabo": (2230, 320, 2380, 540),
                "degraus_escalonados": (780, 320, 1100, 620), "lance_deck": (880, 1030, 1110, 1150),
                "escada_interna": (2240, 880, 2540, 1110), "caracol": (1700, 1440, 2120, 1660),
                "entrada": (2380, 560, 2700, 900), "sala_estar": (1860, 330, 2260, 720),
                # os pedidos seguintes de 26/10 (o travertino bruto, as louças, as bancadas, a ilha, as projeções)
                "travertino": (1860, 330, 2640, 880), "banhos_varanda": (1440, 1380, 1720, 1700),
                "ilha_gourmet": (1440, 1200, 1860, 1520), "banho_motorista": (2240, 1180, 2420, 1330),
                "projecoes": (1150, 560, 2200, 1250),
                # a limpeza dos contornos, o cooktop da ilha gourmet e as bancadas da cozinha em granito
                "contornos_moveis": (1560, 1000, 1760, 1160), "contornos_estar": (1880, 380, 2120, 560),
                "contornos_banhos": (1470, 1440, 1700, 1620), "contornos_lavabo": (2280, 380, 2370, 530),
                "contornos_hall": (2380, 600, 2520, 760), "ilha_cooktop": (1440, 1240, 1800, 1480),
                "cozinha_bancadas": (1900, 1220, 2180, 1530)}


def antes_depois(antes, depois, max_lado=1800, chaves=None):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        if chaves is not None and nome not in chaves:
            continue
        a, d = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        lado = (x1 - x0) <= (y1 - y0) * 1.3
        junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), d]) if lado else \
            np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), d])
        k = min(3.0, max_lado / max(junto.shape[:2]))
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
        arq = CASA / "renders" / f"POE642_CasaA_PH_Terreo_2610_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {arq.name}")


def final_3840(salvar=True, de=None, ate=None):
    """A final de 3840 px com os rótulos. de: recomeça desta etapa (a anterior vem do cache); ate: para nela."""
    Q = FA.QuadroA("Terreo")
    ini = FA.inicial(Q)
    passos = passos_terreo(Q, ini)
    nomes = [n for n, _ in passos]
    i0 = nomes.index(de) if de else 0
    i1 = nomes.index(ate) + 1 if ate else len(passos)
    img = cv2.imread(str(ETAPAS / f"Terreo_{nomes[i0 - 1]}.png")) if i0 > 0 else ini
    for nome, f in passos[i0:i1]:
        t0 = time.time()
        img = f(img)
        print(f"  [{nome}] {time.time() - t0:.0f} s", flush=True)
        cv2.imwrite(str(ETAPAS / f"Terreo_{nome}.png"), img)
    if salvar and ate is None and i1 == len(passos):
        nome = CASA / "renders" / "POE642_CasaA_PH_Terreo_final_rotulos.png"
        cv2.imwrite(str(nome), img)
        print(f"    {nome} {img.shape[1]}x{img.shape[0]}")
    return Q, img


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--antes", help="a final aprovada antes destes itens (PNG): gera os antes e depois")
    ap.add_argument("--so", help="aplica só estas etapas (separadas por vírgula) sobre a final atual, no lugar (a final "
                    "já tem o turquesa e as bordas da piscina de `piscinas_turquesa.py`, que o motor não refaz)")
    a = ap.parse_args()
    if a.so:
        Q = FA.QuadroA("Terreo")
        nome = CASA / "renders" / "POE642_CasaA_PH_Terreo_final_rotulos.png"
        img = cv2.imread(str(nome))
        etapas = dict(passos_terreo(Q, None))
        for e in a.so.split(","):
            img = etapas[e](img)
        cv2.imwrite(str(nome), img)
        print(f"    {nome}")
        raise SystemExit
    Q, img = final_3840(de=a.de, ate=a.ate)
    if a.antes:
        antes_depois(cv2.imread(a.antes), img)

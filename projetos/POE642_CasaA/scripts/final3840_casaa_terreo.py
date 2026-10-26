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
branco nos escuros.

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
# O banho do motorista (usuário, 26/10/26: "Banho serviço: piso em mármore bege bahia, pedra pia em marrom granito
# levemente escurecida"; no Térreo, o banho de serviço é o do motorista) recebe o Bege Bahia das Casas B a D no lugar do
# granito, na mesma máscara e com a mesma luz (`bege`); a bancada e a cuba antigas (`refaz`) viram piso, e as peças novas
# vêm na etapa `loucas`.
GRANITO_T = {"chapada": (158, 167, 191), "fechar": 5, "sig_obj": 1.6, "lum_obj": 150, "croma_obj": 16,
             "area_pinta": 40, "sig_luz": 1.4, "sig_base_m": 0.8, "limiar": 0.08, "proj_claro": 18,
             "semente": 2700, "bege": (2021.2, 1381.2, 2143.3, 1466.0),
             "refaz": [(2103.6, 1381.2, 2143.3, 1410.6)], "refaz_px": 4, "bege_semente": 2705}


def nconv2(a, m, sig):
    """A média normalizada (só os px de m) de uma imagem de um canal."""
    return cv2.GaussianBlur(a * m, (0, 0), sig) / np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)


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


def bege_bahia(Q, h, w, semente):
    """O Bege Bahia das Casas B a D (a foto da biblioteca na escala, no tom delas), h x w x 3."""
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from texturas import textura
    T = textura("bege_bahia", Q.px_m, h, w, semente=semente).astype(np.float32)
    return T / T.reshape(-1, 3).mean(axis=0) * np.float32(FA.PISOS_A["Bege Bahia"]["tom"])


def granito(Q, img):
    import fontes_procedurais as FP
    q = GRANITO_T
    ch = np.all(Q.chapada == np.uint8(q["chapada"]), axis=2)
    ch = F.fechar(ch, q["fechar"])
    f = cv2.GaussianBlur(img.astype(np.float32), (0, 0), q["sig_obj"])
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    obj = ch & ((lum > q["lum_obj"]) | (croma < q["croma_obj"]))
    # as pintas claras do granito antigo não são objeto
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj.astype(np.uint8), 8)
    obj = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_pinta"]])
    obj = cv2.dilate(obj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    # o tracejado das projeções
    L0 = img.astype(np.float32).mean(axis=2)
    claro = L0 - cv2.medianBlur(np.clip(L0, 0, 255).astype(np.uint8), 9).astype(np.float32) > q["proj_claro"]
    proj = ch & tracejado(Q) & claro
    refaz = caixas(Q, q["refaz"], q["refaz_px"]) & ch
    m = (ch & ~obj & ~cv2.dilate(proj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)) | refaz
    # a luz: o que escurece além do desenho da pedra antiga (sombras), só com os px do granito
    L = img.astype(np.float32).mean(axis=2)
    mf = m.astype(np.float32)
    perto = nconv2(L, mf, q["sig_luz"])
    base = nconv2(L, mf, q["sig_base_m"] * Q.px_m)
    sh = np.clip(perto / np.maximum(base, 1) + q["limiar"], 0, 1)
    sh[refaz] = 1.0
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    T = FP.granito_referencia(y1 - y0, x1 - x0, Q.px_m, semente=q["semente"]).astype(np.float32)
    # o banho do motorista em Bege Bahia
    bg = (ret_aa(Q, q["bege"]) > 0.5)[y0:y1, x0:x1]
    T = np.where(bg[..., None], bege_bahia(Q, y1 - y0, x1 - x0, q["bege_semente"]), T)
    novo = img.astype(np.float32).copy()
    novo[y0:y1, x0:x1] = T * sh[y0:y1, x0:x1, None]
    out = F.pousar(img.astype(np.float32), novo, m, suave=0.6)
    print(f"    granito das Casas B a D: {m.sum() / Q.px_m ** 2:.1f} m² de piso (os objetos ficam: "
          f"{(ch & obj).sum() / Q.px_m ** 2:.1f} m²; o tracejado das projeções: {int(proj.sum())} px); o banho do "
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
# - as louças e a bancada que são refeitas na etapa `loucas` (`refaz`) viram piso antes.
TRAV_T = {"chapada": (202, 217, 220), "fechar": 3, "obj_px": 2, "sig_obj": 1.2, "claro": 0.06, "croma": 0.045,
          "escuro": 0.45, "area_pinta": 40, "sig_luz": 1.0, "sig_base_m": 0.8, "limiar": 0.05, "proj_escuro": 0.93,
          "sig_m": 3.0, "refaz": [(2077.1, 577.4, 2106.3, 597.5), (1293.9, 1734.0, 1323.0, 1754.0),
                                   (1442.9, 1612.5, 1462.9, 1641.6), (1292.7, 1605.1, 1406.1, 1633.4)],
          "refaz_px": 4, "semente": 2704}


def travertino_t(Q, h, w, semente):
    """O travertino bruto do Subsolo aprovado (h x w x 3), no tom dele."""
    p = FA.PISOS_A["travertino"]
    D = FA.travertino_bruto(Q, h, w, semente, forca=p["forca"], **FA.TRAVERTINO["piso"])
    return np.float32(p["tom"]) * D[..., None]


def travertino(Q, img):
    q = TRAV_T
    im = img.astype(np.float32)
    ch = F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), q["fechar"])
    branco = np.all(Q.chapada == 255, axis=2) & cv2.dilate(ch.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
    k = 2 * q["obj_px"] + 1
    obj_ch = cv2.dilate(branco.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    # o tom do piso em volta e o que foge dele
    L = F.luz_robusta(im, ch & ~obj_ch, 1.0 * Q.px_m)
    f = cv2.GaussianBlur(im, (0, 0), q["sig_obj"])
    lf, lL = np.maximum(f.mean(axis=2), 1), np.maximum(L.mean(axis=2), 1)
    r = lf / lL
    cd = np.abs(f / lf[..., None] - L / lL[..., None]).max(axis=2)
    obj = ch & ((r > 1 + q["claro"]) | (cd > q["croma"]) | (r < q["escuro"]))
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj.astype(np.uint8), 8)
    obj = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_pinta"]])
    obj = cv2.dilate(obj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    proj = ch & tracejado(Q) & (im.mean(axis=2) / lL < q["proj_escuro"])
    proj = cv2.dilate(proj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    refaz = caixas(Q, q["refaz"], q["refaz_px"]) & (ch | branco)
    m = (ch & ~obj_ch & ~obj & ~proj) | refaz
    # a luz: as sombras (o que escurece além do desenho da pedra antiga) e a luz larga do lugar
    lum = im.mean(axis=2)
    mf = (m & ~refaz).astype(np.float32)
    perto = nconv2(lum, mf, q["sig_luz"])
    base = nconv2(lum, mf, q["sig_base_m"] * Q.px_m)
    larga = nconv2(lum, mf, q["sig_m"] * Q.px_m)
    sh = np.clip(perto / np.maximum(base, 1) + q["limiar"], 0, 1) * larga / np.median(larga[m])
    sh[refaz] = (larga / np.median(larga[m]))[refaz]
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    novo = im.copy()
    novo[y0:y1, x0:x1] = travertino_t(Q, y1 - y0, x1 - x0, q["semente"]) * sh[y0:y1, x0:x1, None]
    out = F.pousar(im, novo, m, suave=0.6)
    print(f"    travertino bruto do Subsolo no piso: {m.sum() / Q.px_m ** 2:.1f} m² (os móveis e o que foge do tom "
          f"do piso ficam: {((ch | branco) & ~m).sum() / Q.px_m ** 2:.1f} m²)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 2. O bloco do motorista:
# - E2: o armário do quarto (o retângulo com a diagonal da DOC_LINHAS E PROJEÇÕES, 0,60 x 1,80 m, junto à parede da
#   direita) aberto, visto de cima, com os cabides e o cabideiro de metal, como os guarda-roupas dos closets da Casa A
#   (`ajustes_casaa.guarda_roupas_1pav`: `_texturas/elementos.guarda_roupa`, os tons da Casa E, bege dentro e ocre na
#   borda), com as portas do lado do quarto e a sombra curta no granito;
# - E5: o box do banho (as duas folhas de correr do PDF, `AJ.folhas_box`) em vidro contínuo e visível; no granito, a faixa
#   cinza-clara da regra de 22/10 ("Tem que estar visível"), com as faces finas, e o trilho contínuo até a parede.
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
    # o box: as duas folhas e o trilho contínuo, na faixa cinza-clara
    b = FA.BANHOS["box"]
    box = next(x for x in AJ.folhas_box(Q.pg) if not x["hor"] and abs(x["meio"] - q["box_meio"]) < 1)
    meio, lado, e = box["meio"], b["afasta_px"] / PT_PX, b["larg_px"] / PT_PX / 2
    for i, f in enumerate(sorted(box["folhas"], key=lambda f: (f[0] + f[2]) / 2)):
        c = meio + (-lado if i == 0 else lado) / 2
        rr = (c - e, f[1], c + e, f[3])
        tl = tela(out, Q, rr, folga=5)
        m = tl.ret(rr)
        sombra_q(tl, m, forca=b["sombra"], dist=0.9, sigma=0.8)
        tl.pintar(m, b["vidro"])
        tl.contorno(m, b["face_px"], b["face"])
        out = tl.gravar()
    a0, a1 = min(t[0] for t in box["trilho"]), max(t[1] for t in box["trilho"])
    w = b["trilho_px"] / PT_PX / 2
    rr = (meio - w, a0, meio + w, a1)
    tl = tela(out, Q, rr, folga=3)
    tl.pintar(tl.ret(rr), b["vidro"], 0.9)
    out = tl.gravar()
    print("    banho do motorista: o box em vidro contínuo (as duas folhas e o trilho até a parede), cinza-claro no granito")
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
# sombra curta (E9); a área molhada da perna de baixo (o retângulo do PDF) rebaixada, um tom abaixo, com a borda; a cuba
# de inox e a torneira ficam as da final (no lugar do PDF).
ILHA = {"poli": [(1281.4, 1596.6), (1281.4, 1432.2), (1556.3, 1432.2), (1556.3, 1488.9), (1315.4, 1488.9),
                 (1315.4, 1556.9), (1556.3, 1556.9), (1556.3, 1596.6)],
        "molhada": (1443.5, 1559.2, 1554.1, 1593.8), "cuba": (1492.8, 1564.3, 1534.8, 1589.2),
        "torneira": (1514.5, 1579.3, 1516.2, 1591.7), "escurecer": 0.86, "molhada_esc": 0.80, "borda": 0.62,
        "larg": 0.6, "sombra": 0.34, "semente": 2708}


def ilha(Q, img):
    q = ILHA
    antes = img.copy()
    xs, ys = [p[0] for p in q["poli"]], [p[1] for p in q["poli"]]
    caixa = (min(xs), min(ys), max(xs), max(ys))
    out = FA.bancada_pedra(Q, np.ascontiguousarray(img.copy()), caixa,
                           lambda tl: FA._granito(Q, tl, q["semente"]) * q["escurecer"], q["borda"], q["larg"],
                           q["sombra"], poli=q["poli"])
    out = FA.bancada_pedra(Q, out, q["molhada"], lambda tl: FA._granito(Q, tl, q["semente"] + 1) * q["molhada_esc"],
                           q["borda"], q["larg"], 0.0)
    # a cuba de inox e a torneira da final
    a = np.maximum(ret_aa(Q, q["cuba"]), ret_aa(Q, q["torneira"]))[..., None]
    out = np.clip(out.astype(np.float32) * (1 - a) + antes.astype(np.float32) * a, 0, 255).astype(np.uint8)
    print("    ilha em U do gourmet: granito marrom um pouco mais escuro que o piso, com a borda e a sombra; a área "
          "molhada rebaixada; a cuba de inox e a torneira da final")
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
    a cada 0,5 pt) em cadeias com vãos (a cobertura do traço no comprimento até `max_cob`)."""
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
            a = round((np.degrees(np.arctan2(y1 - y0, x1 - x0)) % 180) * 2) / 2 % 180
            t = np.radians(a)
            off = -np.sin(t) * x0 + np.cos(t) * y0
            u0, u1 = sorted((np.cos(t) * x0 + np.sin(t) * y0, np.cos(t) * x1 + np.sin(t) * y1))
            grupos[(d.get("layer"), a, round(off * 2) / 2)].append((u0, u1, (x0, y0, x1, y1)))
    out = []
    for k, v in grupos.items():
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
    print(f"    projeções tracejadas: {len(tracos)} traços do PDF, {len(tracos) - n_b} em preto (fundo claro) e "
          f"{n_b} em branco (fundo escuro)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


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


def passos_terreo(Q, ini):
    return [
        ("granito", lambda im: granito(Q, im)),
        ("travertino", lambda im: travertino(Q, im)),
        ("motorista", lambda im: motorista(Q, im)),
        ("loucas", lambda im: loucas(Q, im)),
        ("ilha", lambda im: ilha(Q, im)),
        ("lavabo", lambda im: lavabo(Q, im)),
        ("paredes", lambda im: paredes(Q, im)),
        ("deck", lambda im: deck(Q, im)),
        ("pisantes", lambda im: pisantes(Q, im)),
        ("escada_u", lambda im: escada_u(Q, im)),
        ("caracol", lambda im: caracol(Q, im)),
        ("projecoes", lambda im: projecoes(Q, im)),
        ("seta", lambda im: seta(Q, im)),
        ("rotulos", lambda im: rotulos(Q, im)),
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
                "projecoes": (1150, 560, 2200, 1250)}


def antes_depois(antes, depois, max_lado=1800):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
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
    a = ap.parse_args()
    Q, img = final_3840(de=a.de, ate=a.ate)
    if a.antes:
        antes_depois(cv2.imread(a.antes), img)

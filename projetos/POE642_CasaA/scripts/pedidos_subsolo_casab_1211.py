#!/usr/bin/env python3
"""Subsolo da Casa B: os pedidos de 12/11 (usuário, com os recortes da prancha), sobre a final instalada.

Pedidos: "Fazer as mesmas mudanças que foram apontadas no subsolo da casa A e que cabem para essa casa"; "Colocar a seta
em todas as escadas e a descrição"; "Demarcar melhor o perímetro da casa" e "Tem um pilar aqui" (o canto de cima, à
esquerda, da garagem); na circulação do BH serviço, "O piso continua nessa demarcação" (até a linha do topo da garagem),
"Melhorar representação da porta. Encostar na parede." e um "?" no objeto redondo do box; "usar o mesmo bloco de bicicleta
usado na casa A"; "remova a hachura do terreno fora do subsolo."; na sauna, "Aqui também tem soleira." e de novo as portas
encostadas na parede; "Representar a cor de armário e prateleira igual o indicado da casa A. Sem textura. Uma cor neutra e
sólida."; "Tirar o nome shaft."; e, por mensagem: "centralizar rótulos"; "reduzir manchas no marmore bege bahia";
"melhorar a representação da madeira do deck, igual fizemos na casa A"; "melhorar a representação do marmore travertino
bruto"; "trocar maquinario da academia pelos da casa A, que ficaram com melhor representação"; "melhorar representação dos
bancos da sauna"; "adicionar ralo na pia do bh. sauna".

Um passo por pedido (`PASSOS`), na ordem; `--de`/`--ate` para refazer um trecho, `--passos <pasta>` para gravar cada
um. Coordenadas em px do quadro de 3840 (o mesmo do PDF, `final3840_casab.Quadro("Subsolo")`).
"""
import argparse
import contextlib
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casab as F                      # noqa: E402
import final3840_casaa as FA                     # noqa: E402

B = F.B
RENDERS = B.CASA_B / "renders"
FINAL = RENDERS / "POE642_CasaB_PH_Subsolo_final_rotulos.png"
PEGADA = RENDERS / "POE642_CasaB_PH_Subsolo_pegada_mascara.png"

# ----------------------------------------------------------------------------------------------------------------------
# 1. Os pisos. Cada um refeito pelo `vinilico_foto.trocar` (o mesmo cuidado do vinílico: só o que é piso, fora as peças do
# PDF, as paredes e o que foge do tom do lugar; a luz larga e as sombras de contato da final; o texto e os riscos escuros
# por cima), com outro desenho no lugar das réguas. Os rótulos de `ROTULOS_SB["apagar_px"]` saem com o piso velho (voltam
# no centro do ambiente, passo `rotulos`).
#  - Bege Bahia (garagem, as duas circulações, o BH serviço): a foto da biblioteca (`bege_bahia`) com as manchas a
#    `bege_forca` do contraste (usuário: "reduzir manchas no marmore bege bahia"; na Casa A, 45%).
#  - Travertino bruto (depósito, sauna, BH sauna): o do 1º Pavimento da Casa A de 11/11 (`um_pav_casaa_1111.PISOS_1111E`,
#    "novo e limpo": os estratos e os poros, sem manchas) (usuário: "melhorar a representação do marmore travertino
#    bruto").
#  - A faixa acima do BH serviço e da circulação (usuário, com a linha desenhada: "O piso continua nessa demarcação"): o
#    Bege da garagem continua à direita, da linha do topo da garagem até as paredes, entre a garagem e o muro que sobe
#    (`faixa_px`); a garagem espelhada na borda dela (`espelho_x`), sem emenda.
PISOS_SB = {"bege": {"cores": [(232, 232, 232)], "forca": 0.45, "semente": 1201},
            "travertino": {"cores": [(202, 217, 220), (201, 217, 220)], "semente": 1202},
            # (12/11, usuário, com o recorte da faixa: "melhorar a representação dos contornos e o piso") a faixa entra
            # no mesmo Bege da garagem, numa peça só (antes, a garagem espelhada em x 1359: a emenda aparecia), da
            # borda de cima da garagem (y 275) até a face da parede da direita (x 1549)
            "faixa_px": (1359, 275, 1549, 330), "fundo_faixa": 200,
            # a circulação do BH serviço (no PDF, branca; na base, sem a cor do Bege): o mesmo piso
            "bege_incluir_px": [(1449, 317, 1511, 386)]}
ROTULOS_SB = {
    # as caixas (px) dos rótulos que saem com o piso (o texto que cai nelas não volta)
    "apagar_px": [(1093, 392, 1168, 430), (1662, 391, 1742, 428), (1024, 638, 1090, 676), (1162, 658, 1238, 692),
                  (1246, 662, 1324, 699), (814, 657, 890, 696), (1394, 368, 1446, 414), (1452, 334, 1510, 364)],
}


def _gerar_bege(forca):
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura

    def gerar(h, w, k, rng, deitado, med):
        T = textura("bege_bahia", k, h, w, semente=int(rng.integers(1, 10 ** 6))).astype(np.float32)
        D = T / T.reshape(-1, 3).mean(axis=0)
        return np.float32(med)[None, None] * (1 + forca * (D - 1))
    return gerar


def _gerar_travertino(Q):
    import um_pav_casaa_1111 as U
    qt = U.PISOS_1111E["travertino"]

    def gerar(h, w, k, rng, deitado, med):
        sem = int(rng.integers(1, 10 ** 6))
        if deitado:
            T = FA.travertino_bruto(Q, h, w, sem, qt["veio"], qt["faixa"], qt["poros"], qt["poro_esc"],
                                    forca=qt["forca"])
        else:
            T = FA.travertino_bruto(Q, w, h, sem, qt["veio"], qt["faixa"], qt["poros"], qt["poro_esc"],
                                    forca=qt["forca"]).T
        return np.float32(med)[None, None] * np.ascontiguousarray(T)[..., None]
    return gerar


def _apagar(Q):
    m = np.zeros((Q.H, Q.W), bool)
    for x0, y0, x1, y1 in ROTULOS_SB["apagar_px"]:
        m[y0:y1, x0:x1] = True
    return m


def pisos_sb(Q, img, q=PISOS_SB):
    import vinilico_foto as V
    apagar = _apagar(Q)
    out = img.copy()
    # a faixa acima do BH serviço e da circulação: o branco e a hachura de antes (o que não é parede) entram no Bege da
    # garagem, preenchidos antes no tom dela (para entrarem como piso), e o Bege novo sai numa peça só com a garagem
    x0, y0, x1, y1 = q["faixa_px"]
    reg = out[y0:y1, x0:x1]
    claro = reg.min(axis=2) >= q["fundo_faixa"]
    cinza = (reg.max(axis=2).astype(np.int16) - reg.min(axis=2)) < 12
    fundo = claro | (cinza & (reg.mean(axis=2) > 150))
    garagem = img[y0 + 5:y1, x0 - 60:x0 - 5].reshape(-1, 3)
    reg[fundo] = np.median(garagem, axis=0).astype(np.uint8)
    with contextlib.redirect_stdout(io.StringIO()):
        inc = np.zeros((Q.H, Q.W), bool)
        inc[y0:y1, x0:x1] = fundo
        for a0, b0, a1, b1 in q["bege_incluir_px"]:
            inc[b0:b1, a0:a1] = True
        out, pb = V.trocar(Q, out, q["bege"]["cores"], q=dict(V.VINILICO_FOTO, semente=q["bege"]["semente"]),
                           gerar=_gerar_bege(q["bege"]["forca"]), apagar=apagar, incluir=inc)
        out, pt = V.trocar(Q, out, q["travertino"]["cores"], q=dict(V.VINILICO_FOTO, semente=q["travertino"]["semente"],
                                                                        direcao="h"),
                           gerar=_gerar_travertino(Q), apagar=apagar)
    print(f"    pisos: Bege Bahia em {int(pb.sum())} px (manchas a {q['bege']['forca']:.0%}), travertino bruto em "
          f"{int(pt.sum())} px (o de 11/11 da Casa A); a faixa acima do BH serviço e da circulação: {int(fundo.sum())} px "
          f"no mesmo Bege da garagem, numa peça só")
    return out


# 2. O deck da ducha (usuário: "melhorar a representação da madeira do deck, igual fizemos na casa A"): o deck do Térreo
# da Casa A de 11/11 (`terreo_casaa_1011.deck_madeira_ta`: réguas de 20 cm no sentido do PDF, peças de 1,6 a 3,4 m, o tom
# de madeira nova, veio, bisel, juntas e topos discretos), nas cores do deck na base da Casa B. O rótulo DUCHA sai antes
# (o escuro dele, pelo entorno) e volta no passo dos rótulos; o chuveiro da ducha (`B.CHUVEIRO_DUCHA`) é redesenhado por
# cima, como no motor.
DECK_SB = {"cores": [(99, 136, 174), (76, 106, 138)], "rotulo_px": (814, 657, 890, 696), "escuro": 110}


def deck_sb(Q, img, q=DECK_SB):
    import terreo_casaa_1011 as TC
    from retoque_subsolo_casae import chuveiro
    x0, y0, x1, y1 = q["rotulo_px"]
    reg = img[y0:y1, x0:x1]
    m = np.zeros(img.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = cv2.dilate((reg.mean(axis=2) < q["escuro"]).astype(np.uint8), np.ones((3, 3), np.uint8)) * 255
    base = cv2.inpaint(img, m, 4, cv2.INPAINT_TELEA)
    guarda = TC.rotulos_na_imagem
    TC.rotulos_na_imagem = lambda *a, **k: []
    try:
        out = TC.deck_madeira_ta(Q, base, q=dict(TC.DECK_TA, cores=q["cores"]))
    finally:
        TC.rotulos_na_imagem = guarda
    c = B.CHUVEIRO_DUCHA
    out = chuveiro(np.ascontiguousarray(out.copy()), Q.p2q, c["ducha"], c["braco"], c["canopla"])
    print("    deck da ducha: o da Casa A (réguas de 20 cm, madeira nova), o chuveiro de novo por cima")
    return out


# 3. O entorno em branco (usuário: "remova a hachura do terreno fora do subsolo."; na Casa A, "Deixar sem hachura. Deixar
# na cor branca. Sem fundo." e "Tirar a representação do deck e da piscina superior. Deixar apenas o subsolo mesmo."): fora
# da pegada do Subsolo (a máscara de R2, `PEGADA`, mais a faixa nova acima do BH serviço), tudo branco: a hachura, a linha
# do lote e as peças do Térreo nevoadas (a pedra grande, os degraus 1-9, o deck e as pedras). As paredes ligadas às da
# casa ficam (o muro que sobe, mais largo que a máscara).
FUNDO_SB = {"parede_max": 100, "croma_max": 12}


def _pegada(Q):
    peg = cv2.resize(cv2.imread(str(PEGADA), cv2.IMREAD_GRAYSCALE), (Q.W, Q.H), interpolation=cv2.INTER_LINEAR) > 127
    x0, y0, x1, y1 = PISOS_SB["faixa_px"]
    peg[y0:y1, x0:x1] = True
    return peg


def fundo_sb(Q, img, q=FUNDO_SB):
    peg = _pegada(Q)
    I = img.astype(np.int16)
    parede = (I.max(axis=2) <= q["parede_max"]) & ((I.max(axis=2) - I.min(axis=2)) <= q["croma_max"])
    parede = ndimage.binary_propagation(parede & peg, mask=parede)
    dentro = peg | parede
    out = img.copy()
    out[~dentro] = 255
    print(f"    entorno em branco: {int((~dentro).sum())} px (hachura, lote e peças do Térreo nevoadas); "
          f"{int((parede & ~peg).sum())} px de parede ligada à casa fora da máscara ficam")
    return out


# 4. O perímetro (usuário: "Demarcar melhor o perímetro da casa"): onde a borda da pegada não é parede (a garagem em
# cima e à esquerda, a faixa nova, a ducha e a escada), um traço no cinza das paredes, `larg_px` para fora do piso.
# E o pilar (usuário, no canto de cima à esquerda da garagem: "Tem um pilar aqui"; o PDF não o desenha): redondo, de
# `diam_m`, no cinza das paredes, onde o usuário o marcou (`centro_px`).
# (12/11, "melhorar a representação dos contornos e o piso", no recorte da faixa acima do BH serviço) o traço de cima
# corre reto e contínuo da garagem até a face da parede da direita (`segmentos_px`; junto a parede o traço não sai,
# e ali ficava um vão de 6 px antes da parede)
PERIMETRO_SB = {"larg_px": 3, "cor": (80, 80, 80), "parede_lum": 110, "segmentos_px": [(1340, 272, 1550, 275)],
                "pilar": {"centro_px": (913.0, 291.0), "diam_m": 0.30, "cor": (80, 80, 80), "ss": 8}}


def perimetro_sb(Q, img, q=PERIMETRO_SB):
    peg = _pegada(Q)
    lum = img.astype(np.float32).mean(axis=2)
    casa = peg & (lum < 250)
    casa = ndimage.binary_fill_holes(casa)
    casa = cv2.morphologyEx(casa.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    k = q["larg_px"]
    faixa = cv2.dilate(casa.astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
    faixa &= ~casa
    I = img.astype(np.int16)
    parede = casa & (lum <= q["parede_lum"]) & ((I.max(axis=2) - I.min(axis=2)) <= 12)
    perto = cv2.dilate(parede.astype(np.uint8), np.ones((2 * k + 7, 2 * k + 7), np.uint8)) > 0
    faixa &= ~perto                                         # junto a parede, nada (ela já marca o perímetro)
    out = img.copy()
    out[faixa] = q["cor"]
    for x0, y0, x1, y1 in q["segmentos_px"]:
        out[y0:y1, x0:x1] = q["cor"]
    # o pilar
    qp = q["pilar"]
    ss = qp["ss"]
    cx, cy = qp["centro_px"]
    r = qp["diam_m"] * Q.px_m / 2
    x0, y0 = int(cx - r) - 2, int(cy - r) - 2
    w = h = int(2 * r) + 5
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.circle(m, (int(round((cx - x0) * ss)), int(round((cy - y0) * ss))), int(round(r * ss)), 255, -1, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[y0:y0 + h, x0:x0 + w].astype(np.float32)
    out[y0:y0 + h, x0:x0 + w] = np.clip(np.round(reg * (1 - a) + np.float32(qp["cor"]) * a), 0, 255).astype(np.uint8)
    print(f"    perímetro: {int(faixa.sum())} px de traço ({k} px) onde a borda não é parede; o pilar redondo de "
          f"{qp['diam_m'] * 100:.0f} cm em ({cx:.0f}, {cy:.0f}) px")
    return out


# 5. As portas de giro (usuário, com os recortes das quatro: "Melhorar representação da porta. Encostar na parede."; na
# porta da sauna, "Aqui também tem soleira."). Nas quatro (BH serviço, depósito, sauna, BH sauna), pelo PDF (ARQ_PAREDE):
#  - o marco que a base deixava nas pontas da parede (o batente no vão e as guarnições de 1,2 x 4,2 px saindo das faces)
#    sai: o piso de cada lado continua (`desloc_px` para longe da parede, na mesma linha);
#  - a ponta da parede do lado da dobradiça avança até a face da folha (`vértice com vértice`, como na Casa A): a quina da
#    folha encontra a quina da parede;
#  - a soleira no vão, entre as pontas (nas portas da sauna, do BH serviço e do BH sauna; a do depósito não tem no PDF):
#    o travertino claro da soleira da saleta do 1º Pavimento da Casa A, com os fios das faces;
#  - a folha (o retângulo do PDF, aberta a 90°) de novo, na madeira clara das folhas do 1º Pavimento da Casa A
#    (`um_pav_casaa_1111.RETOQUES_1111F["folha"]`), com o contorno e a sombra curta; a folha antiga sai antes (o piso
#    logo ao lado, `desloc_px`, para o lado do ambiente).
# Coordenadas: px do quadro (as do PDF levadas pelo `p2q`). `parede` = as faces da parede (x), `topo` = a ponta de cima
# (y), `base` = a de baixo; `folha` = (x0, y0, x1, y1); `dobra` = "topo" ou "base"; `lado` = +1 se a folha vai para a
# direita da parede.
PORTAS_SB = {
    "portas": [
        {"nome": "BH serviço", "parede": (1439.8, 1448.8), "topo": 333.1, "base": 374.9,
         "folha": (1404.0, 336.1, 1439.8, 338.5), "dobra": "topo", "lado": -1, "soleira": True},
        {"nome": "depósito", "parede": (1511.5, 1520.5), "topo": 330.1, "base": 377.9,
         "folha": (1520.5, 333.1, 1562.3, 335.5), "dobra": "topo", "lado": +1, "soleira": False},
        {"nome": "sauna", "parede": (1144.3, 1153.2), "topo": 613.7, "base": 661.5,
         "folha": (1153.2, 656.1, 1195.0, 658.5), "dobra": "base", "lado": +1, "soleira": True},
        {"nome": "BH sauna", "parede": (1233.9, 1245.8), "topo": 610.8, "base": 664.5,
         "folha": (1245.8, 613.7, 1293.6, 616.1), "dobra": "topo", "lado": +1, "soleira": True},
    ],
    # as pontas da parede na imagem não batem com as do PDF (a base deixou de 1 a 6 px de piso entre a parede e o
    # marco: o "Encostar na parede"); elas são achadas na própria imagem (a primeira corrida de `parede_corrida` px
    # da cor da parede, de dentro do vão para fora), e as faces também (a menor das larguras das duas pontas)
    "marco_px": 4.0, "desloc_px": 9, "limpa_folha_px": 5, "parede": (80, 80, 80), "parede_max": 110,
    "parede_tol": 3, "parede_corrida": 3,
    "soleira": (206, 215, 224), "faces": (135, 135, 138), "ss": 8, "semente": 1203,
    # o "?" do usuário (o objeto redondo no box do BH serviço): o tique do PDF na porta de correr do box, que a base virou
    # um botão escuro; sai (o piso do box, `desloc_px` à direita)
    "tique_px": (1474, 390, 1488, 401)}


def _cob(r, X0, Y0, w, h, ss=8):
    m = np.zeros((h * ss, w * ss), np.uint8)
    a, b, c, d = ((r[0] - X0) * ss, (r[1] - Y0) * ss, (r[2] - X0) * ss, (r[3] - Y0) * ss)
    cv2.rectangle(m, (int(round(a)), int(round(b))), (int(round(c)) - 1, int(round(d)) - 1), 255, -1)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def _compor(out, r, cor, X0, Y0, w, h):
    a = _cob(r, X0, Y0, w, h)[..., None]
    reg = out[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    cor = np.float32(cor) if np.ndim(cor) == 1 else cor
    out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg * (1 - a) + cor * a), 0, 255).astype(np.uint8)


def _piso_do_lado(out, ys, xs, dx, dy, livre):
    """Os px (ys, xs) recebem o piso a (dx, dy), só onde `livre`."""
    H, W = out.shape[:2]
    yy, xx = np.clip(ys + dy, 0, H - 1), np.clip(xs + dx, 0, W - 1)
    sel = livre[ys, xs]
    out[ys[sel], xs[sel]] = out[yy[sel], xx[sel]]


def portas_sb(Q, img, q=PORTAS_SB):
    import pedidos_terreo_casaa_2910 as P
    import um_pav_casaa_1111 as U
    out = img.copy()
    H, W = out.shape[:2]
    lum = out.astype(np.float32).mean(axis=2)
    I = out.astype(np.int16)
    parede = (lum <= q["parede_max"]) & ((I.max(axis=2) - I.min(axis=2)) <= 14)
    qf = U.RETOQUES_1111F["folha"]
    rng = np.random.default_rng(q["semente"])
    ss = q["ss"]
    cor80 = np.abs(img.astype(np.int16) - np.int16(q["parede"])).max(axis=2) <= q["parede_tol"]
    nr = q["parede_corrida"]
    for pt in q["portas"]:
        xa, xb = pt["parede"]
        yt, yb = pt["topo"], pt["base"]
        fx0, fy0, fx1, fy1 = pt["folha"]
        d = q["desloc_px"]
        # 0. as pontas e as faces da parede na imagem
        xc = int((xa + xb) / 2)
        y = int(np.floor(yt))
        while not cor80[y - nr + 1:y + 1, xc].all():
            y -= 1
        Ys = y + 1                                                 # a ponta de cima termina em Ys (exclusivo)
        y = int(np.ceil(yb)) - 1
        while not cor80[y:y + nr, xc].all():
            y += 1
        Yi = y                                                     # a de baixo começa em Yi

        def _faces(yy):
            r = cor80[yy]
            a_, b_ = xc, xc
            while r[a_ - 1]:
                a_ -= 1
            while r[b_ + 1]:
                b_ += 1
            return a_, b_ + 1
        xa, xb = min(_faces(Ys - nr), _faces(Yi + nr - 1), key=lambda t: t[1] - t[0])
        if pt["lado"] < 0:
            fx1 = float(xa)                                        # a folha encosta na face da parede
        else:
            fx0 = float(xb)
        # a. o marco e a folha antiga saem (o piso de cada lado, na mesma linha; da folha, ao lado dela)
        m = int(np.ceil(q["marco_px"]))
        X0, X1 = xa - m - 1, xb + m + 1
        Y0, Y1 = Ys, Yi
        livre = ~parede
        for x in range(X0, X1):
            if xa <= x < xb:
                continue                                           # o vão: a soleira ou o piso, depois
            dx = -d if x < xa else d
            ys = np.arange(Y0, Y1)
            _piso_do_lado(out, ys, np.full_like(ys, x), dx, 0, livre)
        e = q["limpa_folha_px"]
        a0, a1 = int(np.floor(min(fx0, fx1))) - 1, int(np.ceil(max(fx0, fx1))) + e
        if pt["lado"] < 0:
            a0, a1 = int(np.floor(fx0)) - e, int(np.ceil(fx1)) + 1
        b0, b1 = int(np.floor(fy0)) - e, int(np.ceil(fy1)) + e
        dy = d if pt["dobra"] == "topo" else -d                    # o ambiente fica abaixo (dobra em cima) ou acima
        yy, xx = np.mgrid[b0:b1, a0:a1]
        _piso_do_lado(out, yy.ravel(), xx.ravel(), 0, dy, ~cor80)    # (o ponto escuro na ponta da folha também)
        # b. o vão: a soleira (ou o piso de um dos lados) entre as pontas, com a ponta da dobradiça até a face da folha
        ytop = fy0 if pt["dobra"] == "topo" else yt
        ybot = fy1 if pt["dobra"] == "base" else yb
        VX0, VX1 = xa - 2, xb + 2
        VY0, VY1 = Ys - 2, Yi + 2
        w, h = VX1 - VX0, VY1 - VY0
        if pt["soleira"]:
            Tx = FA.travertino_bruto(Q, w, h, int(rng.integers(1, 10 ** 6)), 0.008, 0.012, 6, 0.05, forca=0.8).T
            Tx = np.ascontiguousarray(Tx) / float(Tx.mean())        # numa peça tão pequena a média foge de 1
            cor = np.float32(q["soleira"])[None, None] * Tx[..., None]
            _compor(out, (xa, ytop, xb, ybot), cor, VX0, VY0, w, h)
            for xf in (xa, xb):                                   # os fios das faces
                _compor(out, (xf - 0.45, ytop, xf + 0.45, ybot), q["faces"], VX0, VY0, w, h)
        else:
            for x in range(xa, xb):
                ys = np.arange(Ys, Yi)
                xs_ = np.full_like(ys, x)
                out[ys, xs_] = out[ys, xs_ - (x - xa) - d]                     # o piso do lado de fora da folha
        # as pontas da parede: a de cima até `ytop`, a de baixo de `ybot`; a da dobradiça avança até a face da folha
        _compor(out, (xa, Ys - 1.0, xb, ytop), q["parede"], VX0, VY0, w, h)
        _compor(out, (xa, ybot, xb, Yi + 1.0), q["parede"], VX0, VY0, w, h)
        # c. a folha: madeira clara, o veio no comprido, o contorno e a sombra curta (como no 1º Pavimento da Casa A)
        FX0, FY0 = int(np.floor(fx0)) - 3, int(np.floor(fy0)) - 3
        fw, fh = int(np.ceil(fx1)) + 3 - FX0, int(np.ceil(fy1)) + 3 - FY0
        mk = P._ret_arred((fx0, fy0, fx1, fy1), qf["raio_px"], FX0, FY0, fh, fw, ss)
        al = cv2.resize(mk, (fw, fh), interpolation=cv2.INTER_AREA)
        sx, sy, sg = qf["sombra_px"]
        sb = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, sx], [0, 1, sy]]), (fw, fh)), (0, 0), sg)
        r_ = out[FY0:FY0 + fh, FX0:FX0 + fw].astype(np.float32)
        r_ *= (1 - qf["sombra"] * sb * (1 - al))[..., None]
        out[FY0:FY0 + fh, FX0:FX0 + fw] = np.clip(np.round(r_), 0, 255).astype(np.uint8)
        n_ = cv2.GaussianBlur(rng.normal(0, 1, mk.shape).astype(np.float32), (0, 0), sigmaX=6.0 * ss, sigmaY=0.6 * ss)
        n_ = 1 + qf["veio"] * n_ / max(float(n_.std()), 1e-6)
        out = P._pintar(out, FX0, FY0, fw, fh, ss, mk, np.float32(qf["madeira"])[None, None] * n_[..., None])
        borda = np.clip(mk - cv2.erode(mk, np.ones((5, 5), np.uint8)), 0, 1) * qf["contorno_alfa"]
        out = P._pintar(out, FX0, FY0, fw, fh, ss, borda,
                        np.float32(qf["contorno"])[None, None] * np.ones_like(borda)[..., None])
    # o tique do box do BH serviço
    x0, y0, x1, y1 = q["tique_px"]
    out[y0:y1, x0:x1] = out[y0:y1, x0 + 14:x1 + 14]
    print(f"    portas: {len(q['portas'])} folhas de novo (madeira clara, quina com quina com a ponta da parede), os "
          f"marcos fora, soleiras na sauna, no BH serviço e no BH sauna; o tique do box do BH serviço saiu")
    return out


# 6. Os bancos da sauna (usuário: "melhorar representação dos bancos da sauna"; e, do Subsolo da Casa A, a regra de
# 10/11/26: "NA PARTE DE CIMA, SE FOR O MESMO MATERIAL, O TOM FICA MAIS ESCURO"). Os dois níveis do PDF
# (`final3840_casab.SAUNA_F`: o da frente, o espelho entre eles e o de trás, junto à parede) refeitos no travertino bruto
# novo do piso (`um_pav_casaa_1111.PISOS_1111E["travertino"]`, os veios deitados, ao comprido do banco), no tom do piso
# da sauna (a mediana, `piso_px`) vezes o nível: o da frente `frente`, o de trás, mais alto, `tras` (mais escuros que o
# piso, cada um mais que o de baixo), o espelho entre eles `espelho` (na sombra). Antes os bancos eram mais claros que o
# piso, no travertino antigo, com os poros grandes, e a frente do banco da frente era um traço tracejado (o fio do PDF
# partido pela troca do piso). Agora: a sombra de contato no de baixo, junto à frente de cada nível (`contato_piso`,
# `contato_banco`: força e px); o fio fino do pé na frente do banco da frente (`pe`) e o brilho fino da quina do de trás
# (`quina`); o piso logo acima da frente (`refaz_px` linhas, onde estava o tracejado) vem de `desloc_px` acima.
BANCOS_SB = {"frente": 0.93, "espelho": 0.78, "tras": 0.86, "contato_piso": (0.16, 5.0), "contato_banco": (0.13, 4.0),
             "pe": {"cor": (118, 122, 126), "larg_px": 0.9, "forca": 0.5}, "quina": {"larg_px": 0.8, "forca": 0.05},
             "piso_px": (976, 684, 1138, 701), "refaz_px": 3, "desloc_px": 6, "semente": 1204}


def bancos_sb(Q, img, q=BANCOS_SB):
    import um_pav_casaa_1111 as U
    from retoque_terreo_casae import linha_aa
    qt = U.PISOS_1111E["travertino"]
    b = F.SAUNA_F[Q.chave]
    (x0, y0), (x1, y1) = Q.p2q(*b["pt"][:2]), Q.p2q(*b["pt"][2:])
    ye0, ye1 = Q.p2q(0, b["espelho_pt"][0])[1], Q.p2q(0, b["espelho_pt"][1])[1]
    out = img.astype(np.float32)
    a_, b_, c_, d_ = q["piso_px"]
    Pz = out[b_:d_, a_:c_].reshape(-1, 3)
    med = np.median(Pz[Pz.mean(axis=1) > 150], axis=0)
    X0, X1, Y0, Y1 = int(np.floor(x0)), int(np.ceil(x1)), int(np.floor(y0)), int(np.ceil(y1))
    parede = (img.astype(np.float32).mean(axis=2) < 110)
    # o piso logo acima da frente (sem o tracejado)
    r, dz = q["refaz_px"], q["desloc_px"]
    out[Y0 - r:Y0 + 1, X0:X1] = out[Y0 - r - dz:Y0 + 1 - dz, X0:X1]
    # a sombra de contato no piso, junto à frente do banco da frente
    f, L = q["contato_piso"]
    for y in range(Y0 - int(np.ceil(L)), Y0 + 1):
        dd = y0 - (y + 0.5)
        if dd > 0:
            out[y, X0:X1] *= 1 - f * max(0.0, 1 - dd / L)
    # os bancos
    h, w = Y1 - Y0, X1 - X0
    T = FA.travertino_bruto(Q, h, w, q["semente"], qt["veio"], qt["faixa"], qt["poros"], qt["poro_esc"],
                            forca=qt["forca"])
    T = (T / float(T.mean()))[..., None]
    rows = np.arange(Y0, Y1, dtype=np.float32)
    cols = np.arange(X0, X1, dtype=np.float32)

    def cov(v, a, b):
        return np.clip(np.minimum(v + 1, b) - np.maximum(v, a), 0, 1)
    cf, ce, ct = cov(rows, y0, ye0), cov(rows, ye0, ye1), cov(rows, ye1, y1)
    al_y = cf + ce + ct
    tom = (cf * q["frente"] + ce * q["espelho"] + ct * q["tras"]) / np.maximum(al_y, 1e-6)
    fb, Lb = q["contato_banco"]
    dd = ye0 - (rows + 0.5)
    ao = np.where((dd > 0) & (rows + 0.5 < ye0), 1 - fb * np.clip(1 - dd / Lb, 0, 1), 1.0)
    novo = np.float32(med)[None, None] * T * (tom * ao)[:, None, None]
    al = (al_y[:, None] * cov(cols, x0, x1)[None, :])[..., None]
    al = al * ~parede[Y0:Y1, X0:X1, None]
    reg = out[Y0:Y1, X0:X1]
    reg[:] = reg * (1 - al) + novo * al
    # o pé do banco da frente e a quina do de trás
    hh, ww = Y1 - Y0 + 2, X1 - X0
    ln = linha_aa((hh, ww), [(x0 - X0, y0 - Y0), (x1 - X0, y0 - Y0)], q["pe"]["larg_px"])[:h, :, None]
    ln = ln * q["pe"]["forca"] * (al > 0)
    reg[:] = reg * (1 - ln) + np.float32(q["pe"]["cor"]) * ln
    lq = linha_aa((hh, ww), [(x0 - X0, ye1 - Y0 + 1.0), (x1 - X0, ye1 - Y0 + 1.0)], q["quina"]["larg_px"])[:h, :, None]
    reg[:] = reg * (1 + q["quina"]["forca"] * lq * al)
    print(f"    sauna: os bancos no travertino novo, o da frente a {q['frente']} e o de trás a {q['tras']} do tom do piso "
          f"(RGB {tuple(int(c) for c in med[::-1])}), o espelho a {q['espelho']}, com a sombra de contato e o pé")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# 7. O ralo da cuba do BH sauna (usuário: "adicionar ralo na pia do bh. sauna"): como os ralos das pias da cozinha e do
# gourmet do Térreo da Casa A (11/11, `terreo_casaa_1011._ralos`): o disco cromado (`FA.CROMO["meio"]`) com o miolo escuro,
# o anel fino e a sombra curta, com 5 px (~9 cm) de diâmetro, no ponto do ralo do PDF (o pontinho no fundo da cuba, no
# eixo da bica; px: centro e raio).
RALO_SB = {"centro_px": (1340.0, 646.0), "raio_px": 2.6, "miolo": 0.55, "cor_miolo": (78, 82, 86),
           "contorno": (0.45, (70, 74, 78)), "sombra": (0.18, 0.5, 0.5), "ss": 8}


def ralo_sb(Q, img, q=RALO_SB):
    cx, cy = q["centro_px"]
    r, ss = q["raio_px"], q["ss"]
    X0, Y0 = int(np.floor(cx - r)) - 3, int(np.floor(cy - r)) - 3
    w = h = int(np.ceil(2 * r)) + 7
    reg = img[Y0:Y0 + h, X0:X0 + w].astype(np.float32)

    def disco(rr):
        m = np.zeros((h * ss, w * ss), np.uint8)
        cv2.circle(m, (int(round((cx - X0) * ss * 16)), int(round((cy - Y0) * ss * 16))), int(round(rr * ss * 16)),
                   255, -1, cv2.LINE_AA, shift=4)
        return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    m, mi, dentro = disco(r), disco(r * q["miolo"]), disco(r - q["contorno"][0])
    f, dd, sg = q["sombra"]
    sb = cv2.GaussianBlur(cv2.warpAffine(m[..., 0], np.float32([[1, 0, dd], [0, 1, dd]]), (w, h)), (0, 0), sg)[..., None]
    reg *= 1 - f * sb * (1 - m)
    reg = reg * (1 - m) + np.float32(FA.CROMO["meio"]) * m
    anel = np.clip(m - dentro, 0, 1)
    reg = reg * (1 - anel) + np.float32(q["contorno"][1]) * anel
    reg = reg * (1 - mi) + np.float32(q["cor_miolo"]) * mi
    out = img.copy()
    out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    BH sauna: o ralo cromado na cuba ({2 * r:.1f} px, no ponto do ralo do PDF)")
    return out


# 8. A escada da ducha (usuário: "Colocar a seta em todas as escadas e a descrição"; o Subsolo da Casa B tem só esta, a
# de 6 degraus, da ducha para a pedra grande, `ajustes_casab.ESCADAS_S[0]`): como no Subsolo da Casa A
# (`cliente_subsolo_casaa_0511.escada_cs`): o S sai (o degrau das mesmas colunas, `desloc_s` px acima: os degraus correm
# na vertical); a seta, o triângulo cheio no degrau de baixo (o da direita, junto ao deck), com a ponta para onde a
# escada sobe (à esquerda), no escuro da seta da Casa A, do tamanho que cabe no degrau (15 px); a descrição em caixa alta
# na fonte, no corpo e na cor do S, em duas linhas, como na Casa A ("SOBE PARA O / DECK" lá), aqui "SOBE PARA O /
# JARDIM" (no alto da escada, no Térreo, fica a pedra grande junto ao jardim), logo abaixo da escada, no branco (ao
# lado dela fica o deck), com o meio do bloco no meio da escada sem passar da parede do deck (`x_max`).
ESCADA_SB = {"s_px": (746, 634, 761, 652), "desloc_s": -18,
             "triangulo": [(748.5, 637.5), (760.5, 631.0), (760.5, 644.0)], "cor_seta": (30, 30, 30), "ss": 8,
             "texto": ("SOBE PARA O", "JARDIM"), "centro_x": 717.0, "x_max": 752.0, "base_y": 701.0,
             "entrelinha_px": 20}


def escada_sb(Q, img, q=ESCADA_SB):
    from PIL import ImageFont
    from rodape_entrega import FONTES
    from cliente_subsolo_casaa_0511 import _alfa_texto
    e = FA.ESCADA_A
    out = img.copy()
    x0, y0, x1, y1 = q["s_px"]
    reg = img[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    s_ = cv2.dilate((reg < 150).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    ys, xs = np.nonzero(s_)
    out[ys + y0, xs + x0] = img[ys + y0 + q["desloc_s"], xs + x0]
    k = q["ss"]
    pts = np.float32(q["triangulo"])
    bx0, by0 = np.floor(pts.min(axis=0)).astype(int) - 2
    bx1, by1 = np.ceil(pts.max(axis=0)).astype(int) + 3
    m = np.zeros(((by1 - by0) * k, (bx1 - bx0) * k), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((pts - [bx0, by0]) * k))], 255, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)[..., None]
    r_ = out[by0:by1, bx0:bx1].astype(np.float32)
    out[by0:by1, bx0:bx1] = np.clip(np.round(r_ * (1 - a) + np.float32(q["cor_seta"]) * a), 0, 255).astype(np.uint8)
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), e["corpo_px"] * 4)
    larg = [fonte.getlength(t) / 4 for t in q["texto"]]
    cx = min(q["centro_x"], q["x_max"] - max(larg) / 2)
    for i, (linha, lw) in enumerate(zip(q["texto"], larg)):
        tx, ly = cx - lw / 2, q["base_y"] + i * q["entrelinha_px"]
        W, H = int(lw) + 12, e["corpo_px"] * 3
        X0, Y0 = int(tx) - 4, int(ly) - e["corpo_px"] * 2
        a = _alfa_texto(linha, fonte, e["corpo_px"], tx, ly, (X0, Y0, W, H))[..., None]
        r_ = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
        out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(r_ * (1 - a) + np.float32(e["cor_texto"]) * a), 0,
                                            255).astype(np.uint8)
    print(f"    escada: o S saiu; a seta no degrau de baixo e \"{' / '.join(q['texto'])}\" logo abaixo da escada")
    return out


# 9. O armário da academia (usuário: "Representar a cor de armário e prateleira igual o indicado da casa A. Sem textura.
# Uma cor neutra e sólida."): a cor padrão dos armários e prateleiras da Casa A (`cliente_subsolo_casaa_0511.
# PRATELEIRAS_CS`, RGB 208, 178, 156), lisa, no retângulo do armário entre as paredes (`px`, a face da academia à
# esquerda), com o fio da face (`face`: a cor x o fator); a sombra curta no vinílico, junto à face, fica a de antes.
# (O retângulo junto à parede de baixo da academia não é prateleira: no passo dos aparelhos ele sai e entra a bola.)
# E o shaft (usuário: "Tirar o nome shaft."): o nome sai e o vão fica no fundo claro, com o X tracejado de canto a canto
# como os shafts do 1º Pavimento da Casa A (`um_pav_casaa_1111.SHAFTS_1P`: fino, simétrico, um traço cruzando o
# centro; preto, pela regra dos tracejados: "ou brancos ou pretos, a depender do fundo"). Antes o X era cinza claro e
# partido pelo nome.
ARMARIO_SB = {"pecas": [((1687, 531, 1724, 652), ("esq",))], "face": 0.82}
SHAFT_SB = {"px": (1734, 534, 1821, 551)}


def armario_shaft_sb(Q, img):
    import um_pav_casaa_1111 as U
    from cliente_subsolo_casaa_0511 import PRATELEIRAS_CS
    out = img.astype(np.float32)
    cor = np.float32(PRATELEIRAS_CS["cor"])
    for (x0, y0, x1, y1), faces in ARMARIO_SB["pecas"]:
        out[y0:y1, x0:x1] = cor
        for fc in faces:
            sl = {"esq": np.s_[y0:y1, x0], "dir": np.s_[y0:y1, x1 - 1], "topo": np.s_[y0, x0:x1]}[fc]
            out[sl] = cor * ARMARIO_SB["face"]
    q = U.SHAFTS_1P
    x0, y0, x1, y1 = SHAFT_SB["px"]
    out[y0:y1, x0:x1] = np.float32(q["fundo"])
    ss, r = 8, q["recuo_px"]
    X0, Y0 = x0 - 2, y0 - 2
    w, h = (x1 - x0) + 4, (y1 - y0) + 4
    M = np.zeros((h * ss, w * ss), np.uint8)
    passo = q["traco_px"] + q["vao_px"]
    for (ax, ay), (bx, by) in (((x0 + r, y0 + r), (x1 - r, y1 - r)), ((x1 - r, y0 + r), (x0 + r, y1 - r))):
        cx, cy = (ax + bx) / 2, (ay + by) / 2
        L = np.hypot(bx - ax, by - ay) / 2
        ux, uy = (bx - ax) / (2 * L), (by - ay) / (2 * L)
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
    al *= U._cobertura((x0, y0, x1, y1), X0, Y0, w, h)
    reg = out[Y0:Y0 + h, X0:X0 + w]
    out[Y0:Y0 + h, X0:X0 + w] = reg * (1 - al[..., None]) + np.float32(q["x"]) * al[..., None]
    print(f"    academia: o armário na cor padrão da Casa A, liso (RGB {PRATELEIRAS_CS['cor'][::-1]}); o shaft sem o "
          f"nome, com o X tracejado preto de canto a canto")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# 10. Os aparelhos da academia (usuário: "trocar maquinario da academia pelos da casa A, que ficaram com melhor
# representação"): as duas esteiras, as duas bicicletas (com os dois pedais, `cliente_subsolo_casaa_0511.pedais_cs`) e
# o supino da final do Subsolo da Casa A (a mesma escala: 59,7 px/m nas duas), cada um com o meio no meio do aparelho
# da Casa B (o lugar do PDF), o supino espelhado (na Casa B a barra fica à direita do banco). Antes, os aparelhos da
# Casa B saem: nas caixas deles (`limpar_px`, com a sombra; e o rótulo ACADEMIA, escrito de novo no passo dos rótulos)
# o vinílico é refeito (`vinilico_foto.trocar`, a mesma régua e a mesma semente da academia: as réguas continuam as
# mesmas em volta), com as caixas preenchidas antes no tom do piso em volta (para entrarem como piso). Cada aparelho da
# Casa A sai da final dela pelo alfa (`_alfa_aparelho`: o cinza e o preto contra a cor da madeira, com a borda suave),
# sem a sombra de lá; aqui, a sombra curta dos aparelhos (`final3840_casaa.APARELHOS["sombra"]`: força, distância e
# desfoque, para baixo e à esquerda).
ACADEMIA_SB = {"limpar_px": [(1416, 459, 1482, 496), (1416, 525, 1482, 562), (1528, 450, 1638, 504),
                             (1529, 506, 1638, 561), (1426, 600, 1522, 714), (1531, 612, 1592, 640),
                             (1386, 731, 1532, 764)],
               "final_a": "renders/POE642_CasaA_PH_Subsolo_final_rotulos.png",
               # (caixa na final da Casa A, o meio na Casa B, espelhar)
               "pecas": [((1460, 1169, 1564, 1223), (1582.5, 475.0), False),     # esteira de cima
                         ((1460, 1232, 1564, 1285), (1583.5, 533.5), False),     # esteira de baixo
                         ((1474, 1323, 1549, 1364), (1448.5, 475.5), False),     # bicicleta de cima
                         ((1474, 1384, 1550, 1423), (1448.5, 542.0), False),     # bicicleta de baixo
                         ((1670, 1270, 1766, 1372), (1474.5, 656.5), True)],     # supino
               "parede_area": 3000,
               # (12/11, usuário, com o recorte do retângulo junto à parede de baixo: "No lugar dessas linhas,
               # representar uma bola presa na parede. Tirar linhas."): o retângulo (ARQ_LAYOUT HUMANIZAÇÃO, 2,21 x
               # 0,45 m) sai com os aparelhos da Casa B (a última caixa de `limpar_px`, até a linha de cima da face da
               # parede) e entra a bola de pilates (a da academia do Subsolo da Casa E, `final3840_casae.ACADEMIA_E`:
               # 0,68 m, o cinza claro e a esfera com a luz do alto à direita), no lugar do círculo do recorte, encostada
               # na parede, no suporte em U de metal grafite preso na parede (`suporte`: folga, espessura e cor), com a
               # sombra curta dos aparelhos
               "bola": {"centro_px": (1422.0, 743.0), "raio_px": 20.5, "cor": (198, 200, 202),
                        "contorno": ((120, 122, 126), 0.8), "suporte": (1.2, 1.7, (72, 74, 78)), "ss": 8}}


def _bola(img, q):
    """A bola de pilates presa na parede: a esfera (`final3840_casae._sombreado`, modo esfera), o fio do contorno, o
    suporte em U (a metade de baixo de um anel, com os dois braços até a parede) e a sombra curta."""
    cx, cy = q["centro_px"]
    r, ss = q["raio_px"], q["ss"]
    X0, Y0 = int(cx - r) - 8, int(cy - r) - 8
    w = h = int(2 * r) + 17
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32) / ss + 0.5 / ss
    xx += X0
    yy += Y0
    d = np.hypot(xx - cx, yy - cy)

    def reduz(a):
        return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    dx, dy = (xx - cx) / r, (yy - cy) / r
    z = np.sqrt(np.clip(1 - dx ** 2 - dy ** 2, 0, 1))
    L3 = np.float32([0.45, -0.45, 0.77]) / np.linalg.norm([0.45, -0.45, 0.77])
    lam = np.clip(dx * L3[0] + dy * L3[1] + z * L3[2], 0, 1)
    luz = 0.42 + 0.66 * lam + 0.22 * lam ** 30
    m = (d <= r).astype(np.float32)
    a = reduz(m)
    cor = reduz(m[..., None] * np.float32(q["cor"])[None, None] * luz[..., None]) / np.maximum(a, 1e-6)[..., None]
    folga, esp, cs = q["suporte"]
    ra = r + folga
    anel = (np.abs(d - ra) <= esp / 2) & (yy >= cy)
    bracos = (np.abs(np.abs(xx - cx) - ra) <= esp / 2) & (yy >= cy) & (yy <= cy + r + 2)
    sup = reduz(anel | bracos)
    co, fc = q["contorno"]
    borda = reduz((np.abs(d - r) <= 0.45).astype(np.float32)) * fc
    f, dist, sig = FA.APARELHOS["sombra"]
    tudo = np.maximum(a, sup)
    sb = cv2.GaussianBlur(cv2.warpAffine(tudo, np.float32([[1, 0, -dist], [0, 1, dist]]), (w, h)), (0, 0), sig) * f
    out = img.astype(np.float32)
    reg = out[Y0:Y0 + h, X0:X0 + w]
    reg *= (1 - sb * (1 - tudo))[..., None]
    reg[:] = reg * (1 - a[..., None]) + cor * a[..., None]
    reg[:] = reg * (1 - borda[..., None]) + np.float32(co) * borda[..., None]
    reg[:] = reg * (1 - sup[..., None]) + np.float32(cs) * sup[..., None]
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _alfa_aparelho(reg):
    """O alfa de um aparelho (cinza, cromado ou preto) sobre a madeira: 1 no miolo (pouco colorido ou escuro), a borda
    suave pela cor e pelo escuro, só junto ao miolo."""
    r = reg.astype(np.float32)
    mx, lum = r.max(axis=2), r.mean(axis=2)
    c = (mx - r.min(axis=2)) / np.maximum(mx, 1)
    core = (c < 0.10) | (lum < 70)
    n, lab, st, _ = cv2.connectedComponentsWithStats(core.astype(np.uint8), 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= 12
    core = keep[lab]
    a = np.maximum(np.clip((0.20 - c) / 0.10, 0, 1), np.clip((95 - lum) / 25, 0, 1))
    a *= cv2.dilate(core.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    a[core] = 1.0
    return a


def academia_sb(Q, img, q=ACADEMIA_SB):
    import vinilico_foto as V
    H, W = img.shape[:2]
    # a. os aparelhos da Casa B saem (o vinílico refeito nas caixas deles)
    I = img.astype(np.int16)
    par0 = (np.abs(I - 80).max(axis=2) <= 6).astype(np.uint8)
    nn, lb, stt, _ = cv2.connectedComponentsWithStats(par0, 8)
    big = np.zeros(nn, bool)
    big[1:] = stt[1:, cv2.CC_STAT_AREA] > q["parede_area"]
    par = big[lb]
    m = np.zeros((H, W), bool)
    pre = img.copy()
    for x0, y0, x1, y1 in q["limpar_px"]:
        m[y0:y1, x0:x1] = True
    m &= ~par
    for x0, y0, x1, y1 in q["limpar_px"]:
        anel = np.zeros((H, W), bool)
        anel[y0 - 6:y1 + 6, x0 - 6:x1 + 6] = True
        anel[y0:y1, x0:x1] = False
        anel &= ~par
        sel = np.zeros((H, W), bool)
        sel[y0:y1, x0:x1] = True
        pre[sel & m] = np.median(img[anel], axis=0)
    with contextlib.redirect_stdout(io.StringIO()):
        out, _ = V.trocar(Q, pre, [(124, 162, 200)], apagar=m, incluir=m)
    # b. os da Casa A, com a sombra curta
    A = cv2.imread(str(Path(__file__).resolve().parents[1] / q["final_a"]))
    f, dist, sig = FA.APARELHOS["sombra"]
    o = out.astype(np.float32)
    for (ax0, ay0, ax1, ay1), (cx, cy), esp in q["pecas"]:
        reg = A[ay0:ay1, ax0:ax1]
        al = _alfa_aparelho(reg)
        cor = reg.astype(np.float32)
        if esp:
            al, cor = al[:, ::-1], cor[:, ::-1]
        h, w = al.shape
        X0, Y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
        pad = 6
        big_a = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
        big_a[pad:pad + h, pad:pad + w] = al
        sb = cv2.GaussianBlur(cv2.warpAffine(big_a, np.float32([[1, 0, -dist], [0, 1, dist]]),
                                             (w + 2 * pad, h + 2 * pad)), (0, 0), sig) * f * (1 - big_a)
        r_ = o[Y0 - pad:Y0 + h + pad, X0 - pad:X0 + w + pad]
        r_ *= (1 - sb)[..., None]
        r2 = o[Y0:Y0 + h, X0:X0 + w]
        r2[:] = r2 * (1 - al[..., None]) + cor * al[..., None]
    o = _bola(np.clip(np.round(o), 0, 255).astype(np.uint8), q["bola"])
    print(f"    academia: os aparelhos da Casa B e o retângulo junto à parede saem (o vinílico refeito em "
          f"{len(q['limpar_px'])} caixas) e entram os {len(q['pecas'])} da Casa A (2 esteiras, 2 bicicletas, o supino "
          f"espelhado), com a sombra curta, e a bola de pilates presa na parede")
    return o


# 11. Os rótulos (usuário: "centralizar rótulos"; regra: "rótulos centralizados", nenhum sobre objeto): os que saíram
# nos passos anteriores (no piso novo, `ROTULOS_SB["apagar_px"]`, e o da academia) voltam, cada um no meio do piso livre
# do seu ambiente: o recinto pelo PDF (`final3840_casab.ambientes_rotulos`, com os vidros e os batentes), sem os
# objetos (as camadas de obstáculo dos rótulos, os bancos da sauna e os aparelhos novos da academia, com `margem_px`);
# o meio é a média do piso livre; se a caixa do texto ali toca objeto ou sai do recinto, ela anda o mínimo até ficar
# livre. O texto, o corpo e a quebra são os de antes (`Quadro.q["ajustes"]`: BH / SERVIÇO em duas linhas, a circulação
# do BH serviço no corpo 0,8); a cor, preta ou branca pelo fundo (`final3840_casab.cor_do_fundo`). ELEVADOR fica; SHAFT
# saiu (passo 9).
ROTULOS_SB2 = {"desenhar": ("BH SERVIÇO", "CIRCULAÇÃO", "DEPÓSITO", "ACADEMIA", "DUCHA", "SAUNA", "BH SAUNA",
                            "GARAGEM"),
               "margem_px": 5, "raio_px": 60, "corpos": (1.0, 0.85, 0.72),
               # os ambientes abertos (a garagem e o deck da ducha para fora; a circulação da sauna para a garagem):
               # o recinto do PDF vaza, e o piso livre fica nesta caixa (px; por nome e x do ponto do PDF arredondado)
               "recorte_px": {("GARAGEM", 1129): (897, 275, 1358, 596), ("DUCHA", 848): (762, 597, 957, 771),
                              ("CIRCULAÇÃO", 1191): (1154, 598, 1234, 696)}}


def rotulos_sb(Q, img, q=ROTULOS_SB2):
    import retoque_1pav_casae as R1
    rf = F.ROTULOS_F
    rot = F.textos_rotulos(F.B.rotulos_casab(Q.pg, Q.p2q2000) + [r for r in R1.rotulos_pdf(Q.pg) if r[0] == "SHAFT"])
    busca = [Q.p2q(*r[2]) for r in rot]
    amb = F.ambientes_rotulos(Q, busca, todas=True)
    obst = Q.preencher(lambda d: d.get("layer") in rf["obstaculos"], ss=2, fs=True) > 0.05
    tr = np.zeros(obst.shape, np.uint8)
    for d in Q.desenhos:                  # os traços (sem os da ARQ_PAREDE: os arcos das portas, que a final não tem)
        if d.get("layer") in rf["obstaculos"] and d.get("layer") != "ARQ_PAREDE" and d["type"] == "s":
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c))], False, 1, 2)
    obst |= tr.astype(bool)
    b = F.SAUNA_F[Q.chave]
    x0, y0, x1, y1 = F.ret_q(Q, b["pt"])
    obst[y0:y1 + 1, x0:x1 + 1] = True
    A = cv2.imread(str(Path(__file__).resolve().parents[1] / ACADEMIA_SB["final_a"]))
    for (ax0, ay0, ax1, ay1), (cx, cy), _ in ACADEMIA_SB["pecas"]:
        w, h = ax1 - ax0, ay1 - ay0
        X0, Y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
        obst[Y0:Y0 + h, X0:X0 + w] |= _alfa_aparelho(A[ay0:ay1, ax0:ax1]) > 0.2
    k = 2 * q["margem_px"] + 1
    obst = cv2.dilate(obst.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    I_obst = cv2.integral(obst.astype(np.uint8))
    esc = Q.W / 2000
    out = img.copy()

    def soma(I, a, b_, c, d):
        return int(I[d, c] - I[b_, c] - I[d, a] + I[b_, a])
    for i, r1 in enumerate(rot):
        nome = r1[0]
        if nome not in q["desenhar"]:
            continue
        cx, cy = Q.p2q(*r1[2])
        opc = {}
        for n, (axx, ayy), d_, *extra in Q.q["ajustes"]:
            if n == nome and np.hypot(cx - axx * esc, cy - ayy * esc) < 25 * esc:
                opc = dict(extra[0]) if extra and isinstance(extra[0], dict) else ({"corpo": extra[0]} if extra else {})
        reg = amb == i + 1
        rc = q["recorte_px"].get((nome, int(round(cx))))
        if rc is not None:
            caixa = np.zeros_like(reg)
            caixa[rc[1]:rc[3], rc[0]:rc[2]] = True
            reg = caixa & ~(Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill"),
                                        ss=1) > 0.3) if rc else reg
        livre = reg & ~obst
        ry, rx = np.nonzero(livre)
        tx, ty = rx.mean(), ry.mean()
        I_reg = cv2.integral(reg.astype(np.uint8))
        corpo0 = opc.get("corpo", R1.ROTULOS["escala"])
        for fc in q["corpos"]:                 # onde o texto não cabe livre, o corpo cai (como em `F.rotulos`)
            o_ = dict(opc, corpo=corpo0 * fc)
            bx0, by0, bx1, by1 = F._caixa_texto(Q, r1, o_)
            w, h = bx1 - bx0, by1 - by0
            melhor = None
            for rr in range(0, q["raio_px"] + 1):
                anel = [(0, 0)] if rr == 0 else [(int(round(rr * np.cos(t))), int(round(rr * np.sin(t))))
                                                 for t in np.linspace(0, 2 * np.pi, max(8, int(2 * np.pi * rr)),
                                                                      endpoint=False)]
                for ox, oy in anel:
                    a0, b0 = int(round(tx - w / 2 + ox)), int(round(ty - h / 2 + oy))
                    a1, b1 = a0 + int(round(w)), b0 + int(round(h))
                    toca = soma(I_obst, a0, b0, a1, b1)
                    fora = (a1 - a0) * (b1 - b0) - soma(I_reg, a0, b0, a1, b1)
                    custo = 10 ** 6 * fora + 1000 * toca + rr
                    if melhor is None or custo < melhor[0]:
                        melhor = (custo, a0, b0, a1, b1)
                if melhor[0] < 10 ** 3:
                    break
            if melhor[0] < 10 ** 3:
                break
        opc = o_
        _, a0, b0, a1, b1 = melhor
        dx, dy = a0 - (cx + bx0), b0 - (cy + by0)
        o2 = dict(opc, cor=F.cor_do_fundo(out, a0, b0, a1, b1))
        out = R1.rotulos_ambientes(out, [r1], Q.p2q, escala_desvio=esc, granito=None,
                                   ajustes=[(nome, (cx / esc, cy / esc), (dx / esc, dy / esc), o2)], halo=None)
        print(f"      {nome}: o meio do piso livre em ({tx:.0f}, {ty:.0f}) px; a caixa em ({a0}, {b0})-({a1}, {b1}) "
              f"{'livre' if melhor[0] < 1000 else 'tocando'}, corpo {fc}")
    print(f"    rótulos: {len(q['desenhar'])} nomes no meio do piso livre de cada ambiente")
    return out


PASSOS = [("pisos", pisos_sb), ("deck", deck_sb), ("fundo", fundo_sb), ("perimetro", perimetro_sb),
          ("portas", portas_sb), ("bancos", bancos_sb), ("ralo", ralo_sb), ("escada", escada_sb),
          ("armario", armario_shaft_sb), ("academia", academia_sb), ("rotulos", rotulos_sb)]


def correcoes(img, de=None, ate=None, salvar_passos=None):
    Q = F.Quadro("Subsolo")
    nomes = [n for n, _ in PASSOS]
    i0 = nomes.index(de) if de else 0
    i1 = nomes.index(ate) + 1 if ate else len(nomes)
    out = img
    for nome, f in PASSOS[i0:i1]:
        print(f"  [{nome}]", flush=True)
        out = f(Q, out)
        if salvar_passos:
            Path(salvar_passos).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(Path(salvar_passos) / f"passo_{nome}.png"), out)
    return out


# Os antes e depois (contra a final de partida, a de 21fa118): a planta inteira e os trechos, em
# `renders/POE642_CasaB_PH_Subsolo_1211_<trecho>_antes_depois.jpg` da Casa B (px da final: x0, y0, x1, y1).
ANTES_DEPOIS_SB = {"planta": (630, 240, 1960, 820), "portas_bh_servico_deposito": (1380, 310, 1590, 430),
                   "sauna_bh_sauna": (950, 575, 1350, 785), "academia": (1360, 440, 1835, 785),
                   "escada_ducha": (630, 575, 975, 785), "garagem_pilar_perimetro": (880, 255, 1380, 610),
                   "faixa_bh_servico": (1300, 255, 1600, 345), "bola_parede": (1370, 715, 1560, 780)}


def antes_depois_sb(antes, depois, q=ANTES_DEPOIS_SB, max_lado=2400):
    pasta = Path(__file__).resolve().parents[2] / "POE642_CasaB" / "renders"
    for nome, (x0, y0, x1, y1) in q.items():
        a, d = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        lado = (x1 - x0) <= (y1 - y0) * 1.3
        junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), d]) if lado else \
            np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), d])
        k = min(3.0, max_lado / max(junto.shape[:2]))
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
        arq = pasta / f"POE642_CasaB_PH_Subsolo_1211_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {arq.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes", type=Path, default=FINAL, help="a final de partida (padrão: a instalada)")
    ap.add_argument("--saida", type=Path, default=None, help="padrão: grava por cima da final")
    ap.add_argument("--de", default=None)
    ap.add_argument("--ate", default=None)
    ap.add_argument("--passos", type=Path, default=None)
    ap.add_argument("--antes_depois", action="store_true", help="grava os antes e depois (ANTES_DEPOIS_SB)")
    a = ap.parse_args()
    img = cv2.imread(str(a.antes))
    out = correcoes(img, a.de, a.ate, a.passos)
    cv2.imwrite(str(a.saida or FINAL), out)
    print(f"    {a.saida or FINAL}")
    if a.antes_depois:
        antes_depois_sb(img, out)

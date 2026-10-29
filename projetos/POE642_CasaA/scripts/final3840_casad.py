#!/usr/bin/env python3
"""A final da Casa D refeita na resolução da prancha (3840 px, ~59,7 px/m), pelo motor das Casas B e C.

Pedido do usuário (22/10/26), depois dos mapas do pente fino da Casa D (`conferencia_casad.py`): "Casa D" e, às
perguntas dos mapas, "1. Igual ao das outras casas 2. Em Madeira 3. Sim, para os 3 4. Areia 5. Os do render
6. Hachura". Valem os 23 itens do Térreo e os 10 do Subsolo dos mapas, com as respostas:
- o granito no tom e no desenho da referência (o das Casas B e C), também no acesso de veículos;
- os brises de ripas da ARQ_ELEMENTOS FIXOS em madeira;
- os três triângulos da R14: na escada de 16 degraus, no degrau 16 (Térreo, para a esquerda) e no degrau 1 (Subsolo,
  para a direita); e nos blocos em cascata à esquerda da piscina, apontando para a esquerda, para onde descem;
- as bancadas e as ilhas em pedra areia humanizada, com as cubas brancas (como nas Casas B e C);
- as camas e os bancos ao pé delas do render aprovado (como na Casa C);
- no Subsolo, em cor cheia só o Subsolo e o pátio; a faixa verde entra na hachura do Térreo final.
Tudo desenhado na resolução da prancha, guardando as decisões de 15/10 (os itens do retoque da Casa D: a piscina com a
borda alta e o dreno, o acesso de veículos em granito, a cabine do elevador, os cooktops de 5 bocas, os tanques
duplos, o banco capitonê, a mesa redonda com o tapete orgânico).

Auditoria de 26/10 no Subsolo (usuário, 27/10: "ok, aplique a lista. no item 7, siga a recomendação"): as paredes em
cinza 80, a escada sem linhas e sem triângulo (com o S, nevoada depois do corte), os cabides no armário do DCE 1, o box
do WC DCE em vidro contínuo, as bancadas em granito com a borda e a sombra, a cuba esculpida e o vaso marrom no
vestiário, os chuveiros cromados, as portas de vidro da academia como as da Casa C e o rótulo do WC DCE no piso livre
(`passos_subsolo_d`). Depois do OK, a pedido do usuário (27/10): a cuba esculpida do vestiário em Bege Bahia e o vaso
branco.

Auditoria de 26/10 no Térreo (usuário, 27/10: "Aprovo a lista e sigamos no item 9 com a recomendação"): as paredes e os
muros em cinza 80, o travertino em estratos da Casa C, a seta da entrada, a escada e os blocos em cascata sem linhas e sem
triângulo (com o D), os cabides nos armários do DCE, da suíte 3 e ao lado do banho master, os boxes em vidro contínuo,
as bancadas com a borda e a sombra e os materiais do Térreo da Casa C, os chuveiros cromados, os X abrindo embaixo dos
rótulos, o rótulo do WC DCE no piso livre, a roupa de cama no DCE, o banco da varanda gourmet e a prateleira da adega
(`passos_terreo_d`).

A Casa D tem a mesma folha, o mesmo recorte, a mesma escala e as mesmas cores de legenda das Casas B e C: as rotinas do
`final3840_casab.py` e do `final3840_casac.py` servem como estão. `contexto_d()` aponta os módulos para a Casa D e
troca os parâmetros que são da casa (as coordenadas em pt do PDF da Casa D). As imagens de partida são o render
retocado e aprovado do Térreo (2000 px, com o Barlavento) e a final do Subsolo (3840 px), levados ao quadro.

Uso (da pasta POE642_CasaA/scripts/):
  python3 final3840_casad.py Terreo              # a final do Térreo com os rótulos
  python3 final3840_casad.py Terreo --de pecas   # recomeça de uma etapa (as anteriores ficam em cache)
  python3 final3840_casad.py Subsolo             # depois do Térreo (a hachura vem do Térreo final)
Saída: `POE642_CasaD/renders/POE642_CasaD_PH_<Pavimento>_final_rotulos.png`, que vai ao `rodape_entrega.py --no-quadro`.
"""
import os
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casab as F                     # noqa: E402
import final3840_casac as C                     # noqa: E402

B, AJ, A = F.B, F.AJ, F.A
RAIZ = B.RAIZ
CASA_D = RAIZ / "POE642_CasaD"
CONFIG_D = CASA_D / "config_bases.json"
CACHE_D = Path(os.environ.get("POE642_CACHE", tempfile.gettempdir())) / "poe642_casad_etapas"

PAVIMENTOS_D = {
    "Terreo": {"render": "renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v4.png",
               "aprovada": "renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v4.png",
               "pdf": "642 - TÉRREO - CASA D.pdf",
               "sem_tela": "bases/POE642_CasaD_BASE_Terreo_v3_texturas.png",
               "chapada": "bases/POE642_CasaD_BASE_Terreo_v2_16x9.png",
               "ajustes": []},
    "Subsolo": {"render": "renders/POE642_CasaD_PH_Subsolo_v1_final.png",
                "aprovada": "renders/POE642_CasaD_PH_Subsolo_v1_final.png",
                "pdf": "642 - SUBSOLO - CASA D.pdf",
                "sem_tela": "bases/POE642_CasaD_BASE_Subsolo_v3_texturas.png",
                "chapada": "bases/POE642_CasaD_BASE_Subsolo_v2_16x9.png",
                "ajustes": []},
}


# quadro comum de 2000 px -> imagem de partida em 2000 px (SIFT da base 16:9 contra ela): 102 pontos no Térreo (0,59 px);
# no Subsolo, a final de 3840 reduzida a 2000, 64 pontos (0,35 px): já é o quadro, deslocado ~1 px
AFIM_QR_D = {"Terreo": ((1.000038, -0.000459, 0.379265), (0.000381, 0.998504, -3.404415)),
             "Subsolo": ((1.000658, 0.000224, -0.758257), (-0.00012, 1.001479, -1.278286))}


# ----------------------------------------------------------------------------------------------------------------------
# Os parâmetros da Casa D (pt do PDF da Casa D; px do quadro de 3840 onde dito)
# Os pisos: as cores de legenda das Casas B e C. No Térreo da Casa D não há deck nem pedra portuguesa (o acesso de
# veículos é granito, como a garagem: decisão de 15/10); o Bege Bahia cobre a área da piscina, a varanda gourmet, os
# blocos, a escada, os pisantes e os banhos. No Subsolo, Bege Bahia, vinílico e granito.
PISOS_D = {
    "Terreo": [
        ("travertino", [(202, 217, 220), (202, 218, 221)], 5, "travertino", 1.6, 3.0),
        ("vinílico", [(124, 162, 200)], 5, "vinilico", None, 1.0),
        ("granito", [(50, 66, 90)], 5, "granito", None, 1.5),
        ("Bege Bahia", [(232, 232, 232)], 5, "bege", None, 1.5),
        ("grama", [(80, 145, 110)], 3, "grama", None, 3.0),
    ],
    "Subsolo": [
        ("Bege Bahia", [(232, 232, 232)], 5, "bege", None, 1.5),
        ("vinílico", [(124, 162, 200)], 5, "vinilico", None, 1.0),
        ("granito", [(50, 66, 90)], 5, "granito", None, 1.5),
    ],
}
# Os tons (itens 2, 5 e 6 do pente fino; resposta 1, "Igual ao das outras casas"): o render de 15/10 tinha o granito
# escuro (~75, 56, 49) com pontos brancos, o Bege Bahia rosado (~226, 209, 198) e a grama clara (~93, 108, 47). A
# textura da biblioteca vai no tom dos mesmos pisos das finais das Casas B e C (a referência): granito ~116, 87, 68;
# Bege Bahia ~230, 211, 187; grama ~84, 100, 43 (RGB). A luz do lugar fica.
TONS_D = dict(C.TONS_C)
_piso_textura_b = F.piso_textura


def piso_textura_d(Q, img, m, nome, forca, sig_m, semente, **kw):
    if nome == "granito" and Q.chave == "Terreo":
        # a luz do granito sem os carros do render (grafite e azul-marinho, quase no tom do granito, entravam na luz
        # e deixavam manchas escuras em volta dos carros novos): ali, a mediana do granito
        img = img.copy()
        livre = m.copy()
        caixas = [F.ret_q(Q, (r[0] - 15, r[1] - 15, r[2] + 15, r[3] + 15)) for r in CARROS_PT]
        for x0, y0, x1, y1 in caixas:
            livre[y0:y1, x0:x1] = False
        med = np.median(img[livre], axis=0)
        for x0, y0, x1, y1 in caixas:
            img[y0:y1, x0:x1] = med
    novo = _piso_textura_b(Q, img, m, nome, forca, sig_m, semente, **kw)
    alvo = TONS_D.get(nome)
    if alvo is not None and m.any():
        med = np.median(novo[m], axis=0)
        novo = novo * (np.float32(alvo) / np.maximum(med, 1.0))
    return novo


# Os carros (item 7, R12): os 3 do PDF (ARQ_LAYOUT HUMANIZAÇÃO; o da esquerda em duas metades), prata, alinhados (o
# mesmo y) e do mesmo tamanho, 4,70 x 1,85 m. O modelo é o carro do meio do render (na janela em px do render de 2000).
CARROS_PT = [(2414.4, 690.9, 2526.1, 943.2), (2572.5, 687.3, 2684.0, 935.3), (2727.0, 672.6, 2850.6, 960.2)]
# O carro branco do meio do render é o modelo. O granito do render da Casa D é quase neutro (~51, 44, 48): o carro é o
# que foge dele (mais de `foge` num canal), não o px neutro, que pegava o granito e juntava os três carros num só.
CARROS_D = dict(B.CARROS_B, janela=(1468, 236, 1556, 400), foge=45,
                centros_pdf=[(2470.2, 815.0), (2628.3, 815.0), (2788.8, 815.0)],
                # desde 27/10 ("melhorar a representação dos veículos"): o modelo é o carro do meio da final aprovada da
                # Casa C (prata, nítido, na mesma escala), no lugar do carro branco do render de 2000 px da Casa D (vidros
                # com ruído, borda irregular); a silhueta é o que não tem o tom do granito (o carro é neutro)
                fonte=RAIZ / "POE642_CasaC" / "renders" / "POE642_CasaC_PH_Terreo_final_rotulos.png",
                janela_fonte=(2905, 355, 3065, 680), croma_max=20, lum_min=100)
# As camas e os bancos ao pé delas (item 23; resposta 5, "Os do render"): ficam como no render aprovado de 15/10; as
# peças do PDF delas não entram e, depois das peças, o render volta no retângulo, com a sombra curta.
CAMAS_D = {"borda": 1.7, "ss": 4, "semente": 41, "camas": [
    ("suíte master", (639.5, 1560.6, 751.2, 1698.9), "baixo", "casal"),
    ("suíte 1", (1133.3, 1690.4, 1246.6, 1792.5), "dir", "casal"),
    ("suíte 2", (1592.5, 1690.4, 1705.9, 1792.5), "esq", "casal"),
    ("DCE", (2317.0, 727.8, 2373.7, 841.2), "cima", "solteiro")]}
BANCOS_D = [(1109.5, 1696.1, 1132.1, 1786.8), (1707.0, 1696.1, 1729.7, 1786.8)]
# Os cooktops de 5 bocas (decisão de 15/10): os dois deitados; girados 180° (usuário, 27/10/26: "você precisa girar
# 180º os dois cooktops"): 3 bocas em cima e 2 embaixo, os botões do lado de cima, de quem cozinha (as banquetas da ilha
# gourmet ficam embaixo)
COOKTOPS_D = [{"pt": (1332.4, 813.2, 1382.3, 841.6), "giro": 180},
              {"pt": (1719.9, 686.3, 1769.8, 714.7), "giro": 180}]
# As 4 banquetas da ilha gourmet (item 22): no PDF da Casa D são desenhos de traço da ARQ_LOUÇAS E METAIS abaixo da
# ilha; as de linho da biblioteca (0,40 m) no centro de cada uma, viradas para a ilha (para cima), entrando sob o tampo.
# No bloco, a frente do assento fica em cima e o encosto embaixo (`blocos.json`): sem giro (até 27/10, `giro` 180 as
# deixava de costas para a ilha)
# O contorno (usuário, 29/10/26, com o recorte das 4: "melhore o contorno dessas cadeiras também"): o bloco em 4x com a
# beira das cadeiras do escritório (`MOVEIS_TD["cadeira"]["contorno"]`: sem a franja clara do recorte, alfa macio, aro
# fino mais escuro), levado a 1x em área (antes, o bloco direto em 1x, serrilhado); o piso da caixa de cada uma
# (`piso` "bege") no desenho do Bege Bahia, não na etapa dos pisos (que ainda tem as banquetas do render: o aro cinza
# em volta das novas era o resto delas)
BANQUETAS_D = {"caixa_pt": (1280.0, 865.0, 1435.0, 900.0), "camada": "ARQ_LOUÇAS E METAIS", "giro": 0,
               "contorno": True, "piso": "bege"}
# Os guarda-corpos de vidro (item 13): as lâminas brancas de 2 cm da ARQ_ELEMENTOS FIXOS, nenhuma desenhada antes: o L
# da borda do terraço da piscina (junto aos blocos) e as duas do vão da escada de 16 degraus (em cima e à esquerda)
GUARDA_CORPOS_D = [(604.9, 1202.9, 606.0, 1376.3), (361.7, 1375.2, 606.0, 1376.3), (361.7, 1375.2, 362.8, 1701.8),
                   (673.5, 1412.1, 966.0, 1413.2), (673.5, 1412.1, 674.6, 1483.5)]
# Os brises de ripas (item 14; resposta 2, "Em Madeira"): as ripas da ARQ_ELEMENTOS FIXOS (os preenchimentos brancos
# pequenos, com o contorno preto) nestas caixas: a lateral direita da garagem e a faixa abaixo dela, os dois lados da
# porta pivotante do hall, a fachada da suíte master (em cima e à esquerda) e a faixa à direita da escada, a lateral
# da suíte 3. Saíram (pedidos de 27/10) a faixa à direita da escada, sob a porta de vidro do hall ("não existe essa
# linha marrom"), e a faixa da fachada de baixo à esquerda ("esse beiral é todo no bege bahia. remova o vinilico
# daqui"): nas duas, as ripas da ARQ_ELEMENTOS FIXOS estão no PDF, mas por baixo do piso (pintadas antes dele), e não
# aparecem; ali fica o Bege Bahia. Depois, com o OK do usuário ("1. sim, todo em bege bahia. 2. remova."), saíram também
# a faixa da fachada de baixo à direita (essa aparece no PDF; o beiral todo é Bege Bahia, `BEIRAL_BEGE_TD`) e as duas
# peças giradas junto à gourmet (escondidas no PDF, como as primeiras)
BRISES_D = {"caixas_pt": [(2891.1, 652.8, 2911.0, 834.1), (2780.0, 975.6, 2893.0, 995.6),
                          (2175.2, 1083.9, 2208.4, 1163.6), (2175.2, 1290.8, 2208.4, 1375.4),
                          (463.2, 1476.9, 686.4, 1709.6), (2268.2, 1489.3, 2288.1, 1653.6)],
            "lado_max_pt": 20.0, "madeira": 0.92, "tons": (0.86, 1.06), "contorno": (34, 50, 68),
            "contorno_px": 0.5, "sombra": {"dist_m": 0.04, "sig_m": 0.025, "forca": 0.30}, "semente": 91}
# As projeções (item 15), em tracejado, só nestas zonas (pt): sobre os pisos claros, o traço cinza-escuro (os dois X do
# banho master); sobre o granito e as plantas, cinza-claro (os X da garagem e da faixa abaixo dela, o da área descoberta
# e o do jardim do lavabo, e o tracejado da cobertura na faixa de cima da garagem, na ARQ_ELEMENTOS FIXOS). Os
# retângulos com diagonal da DOC_LINHAS (armários até o teto) não entram (seção 7).
PROJECOES_D = [(604.7, 1829.2, 790.8, 1880.5)]
PROJECOES_CLARAS_D = [(1949.2, 748.7, 2120.1, 881.6), (2351.8, 1363.0, 2451.5, 1501.6)]
# a cobertura e os X da garagem e da faixa de grama abaixo dela: desde os pedidos de 27/10 em `projecoes_lajes_td`
COBERTURA_D = []
# Revisão de 28/10/26, item 1 (OK do usuário: "pode aplicar os 7"; a regra de 28/10: "os tracejados são ou brancos ou
# pretos, a depender do fundo"): os dois X do banho master, no quartzito claro, em preto nítido, não mais no cinza-escuro
PROJECOES_TRACO_D = {"pisos": {"cor": (30, 30, 30), "forca": 1.0, "larg": 1.4},
                     "claras": {"cor": (214, 214, 212), "forca": 0.95, "larg": 1.4}}
# As peças do PDF que ficam como no render aprovado: o estar da suíte 3 (no PDF da Casa D, o sofá está na INS_INSTALAÇÕES
# HIDRÁULICAS e a mesa de centro na DOC_LINHAS; só o tapete, da ARQ_LAYOUT, entrava, e cobria os dois)
FORA_PECAS_D = [(2060.0, 1495.0, 2256.0, 1640.0)]
# os dois vasos do hall, junto aos brises, e a planta sobre a bancada gourmet (objetos de 15/10, item 22): as plantas do
# render (no PDF, a da bancada é um contorno de traço)
VASOS_D = [(2117.6, 1089.9, 2186.9, 1153.8), (2117.7, 1299.9, 2187.0, 1363.8)]
# Os vasos do hall (usuário, 27/10/26: "o sombreado das plantas ficou muito carregado. suavize mais."): no render, cada
# planta está sobre a sombra cinza dele, um quadrado entre 110 e 170 de luminância que `C.verde` (o escuro abaixo de 170
# ligado às folhas) levava junto. Só as folhas vêm do render (o verde e o escuro abaixo de `escuro` ligado a ele), com a
# sombra curta das peças mais leve e mais aberta (`sombra`)
PLANTAS_VASO_TD = {"escuro": 95, "sombra": {"dist_m": 0.05, "sig_m": 0.05, "forca": 0.16}}
# a planta sobre a bancada gourmet saiu (usuário, 27/10/26: "remova esse elemento decorativo do gourmet"): o render não
# volta ali, e o desenho dela no PDF (traços da ARQ_LAYOUT HUMANIZAÇÃO) segue fora das peças; fica a pedra da bancada
SEM_PLANTA_TD = [(1276.9, 681.3, 1315.9, 715.5)]
# o quadrado da circulação da ala íntima (usuário, 27/10/26: "esse quadrante pontilhado não existe aqui"): um
# preenchimento branco de 0,8 m da ARQ_LAYOUT HUMANIZAÇÃO pintado no PDF antes do vinílico, que o cobre (não aparece);
# entrava como peça, com o contorno tracejado. Fica fora das peças, com o vinílico em volta
PECAS_OCULTAS_TD = [(1677.0, 1512.0, 1724.2, 1559.0)]
# As cubas que o PDF da Casa D desenha sem o aro (seção 6, todas em louça branca): as duas do banho master (retângulos
# soltos na bancada), a do lavabo (só a torneira no PDF; a bacia no lugar da do render) e a do WC DCE (de parede, só
# contorno). Entram com as outras, pela rotina das cubas das bancadas.
CUBAS_EXTRA_D = {"Terreo": [(656.6, 1717.6, 685.0, 1740.7), (709.6, 1717.6, 738.0, 1740.7),
                            (2332.8, 1382.0, 2349.9, 1414.3), (2150.0, 759.9, 2166.6, 783.2)]}
_cubas_bancada_b = F.cubas_bancada


def cubas_bancada_d(Q):
    return sorted(set(_cubas_bancada_b(Q)) | set(CUBAS_EXTRA_D.get(Q.chave, [])))
NAO_TAPETE_D = []
# As bordas do tapete da suíte master (usuário, 27/10/26: "suavize as bordas do tapete da suíte master"): no PDF (o
# retângulo da ARQ_LOUÇAS E METAIS em `pt`), as franjas são traços juntos nos dois lados, e as peças os pintavam como
# hachura escura (a faixa cinza de 4 px). Na faixa de `faixa_px` em volta da borda, o cinza (croma abaixo de `croma`,
# luz abaixo de `luz`) e o que é tapete ou piso sai para a passagem macia (`suave_px`) do tapete (a `fonte_px` para
# dentro, nas bordas de pé e nas deitadas) ao piso (a mesma distância para fora), com a beira do tapete um pouco mais
# escura (`beira`) e a sombra curta no piso (`sombra`); as peças por cima dele (cabeceira, cama, criados: os
# preenchimentos de mais de `peca_pt`) ficam
TAPETE_SUITE_TD = {"pt": (610.3, 1519.2, 780.3, 1660.9), "faixa_px": 4, "fonte_px": (7, 3), "suave_px": 1.5,
                   "beira": 0.05, "sombra": 0.10, "croma": 30, "luz": 160, "peca_pt": 8.0}


# O trilho da cortina da suíte master fora dela (usuário, 27/10/26: "essa linha não existe no meio da imagem"): o trilho
# da cortina da esquerda vai de parede a parede (`cortinas_b`), mas em cima o canto da suíte é de vidro, e ele subia
# pelo Bege Bahia do deck até a faixa da cobertura; no retângulo (pt) fora da suíte, a imagem de antes das cortinas
TRILHO_FORA_TD = [(480.7, 1364.1, 489.2, 1497.6)]


def sem_trilho_fora_d(Q, img, antes):
    out = img.copy()
    for r in TRILHO_FORA_TD:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        out[y0:y1, x0:x1] = antes[y0:y1, x0:x1]
    print(f"    suíte master: o trilho da cortina para na suíte ({len(TRILHO_FORA_TD)} trecho fora dela sai)")
    return out


def tapete_suave_d(Q, img):
    q = TAPETE_SUITE_TD
    x0p, y0p, x1p, y1p = q["pt"]
    (ax, ay), (bx, by) = Q.p2q(x0p, y0p), Q.p2q(x1p, y1p)
    f = q["faixa_px"]
    X0, Y0 = int(np.floor(ax)) - f - 1, int(np.floor(ay)) - f - 1
    X1, Y1 = int(np.ceil(bx)) + f + 1, int(np.ceil(by)) + f + 1
    src = img.astype(np.float32)
    yy, xx = np.mgrid[Y0:Y1, X0:X1]
    dist = np.stack([xx + 0.5 - ax, bx - xx - 0.5, yy + 0.5 - ay, by - yy - 0.5])   # para dentro de cada lado
    lado = dist.argmin(axis=0)
    d = dist.min(axis=0)
    nx = np.choose(lado, [1, -1, 0, 0])
    ny = np.choose(lado, [0, 0, 1, -1])
    o = np.where(lado < 2, q["fonte_px"][0], q["fonte_px"][1])
    H, W = src.shape[:2]
    dr = np.round(o - d).astype(int)
    fr = np.round(o + d).astype(int)
    rug = src[np.clip(yy + ny * dr, 0, H - 1), np.clip(xx + nx * dr, 0, W - 1)]
    piso = src[np.clip(yy - ny * fr, 0, H - 1), np.clip(xx - nx * fr, 0, W - 1)]
    sv = q["suave_px"]
    a = np.clip(0.5 + d / (2 * sv), 0, 1)[..., None]
    beira = 1 - q["beira"] * np.exp(-np.maximum(d, 0) / sv)[..., None]
    sombra = 1 - q["sombra"] * np.exp(-np.maximum(-d, 0) / sv)[..., None]
    novo = a * rug * beira + (1 - a) * piso * sombra
    reg = src[Y0:Y1, X0:X1]
    cinza = (reg.max(axis=2) - reg.min(axis=2) < q["croma"]) & (reg.mean(axis=2) < q["luz"])
    def por_cima(dd):
        r = dd["rect"]
        return dd.get("layer") in F.CAMADAS_PECAS and dd.get("fill") and min(r.width, r.height) > q["peca_pt"] \
            and not (abs(r.x0 - x0p) < 0.5 and abs(r.y0 - y0p) < 0.5) \
            and r.x1 > x0p - 5 and r.x0 < x1p + 5 and r.y1 > y0p - 5 and r.y0 < y1p + 5
    pecas = Q.preencher(por_cima, fs=False)[Y0:Y1, X0:X1]
    pecas = cv2.dilate((pecas > 0.05).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    alvo = (np.abs(d) <= f) & ~pecas
    n = int((alvo & cinza).sum())
    out = img.copy()
    out[Y0:Y1, X0:X1][alvo] = np.clip(novo[alvo], 0, 255).astype(np.uint8)
    print(f"    suíte master: as bordas do tapete macias ({n} px da franja cinza, {int(alvo.sum())} px na faixa)")
    return out
# As esquadrias: na piscina, na prainha e no spa, as paredes da ARQ_PAREDE são brancas e finas como vidro (a base já as
# tirava, `zonas_excluidas` da config); não são esquadria (como na Casa C)
VIDROS_FORA_D = [(717.4, 679.7, 1104.1, 1172.5)]
# As zonas dos móveis humanizados (seção 8): o estar da varanda gourmet, o living, a sala íntima e o estar da suíte 3
HUMANIZAR_D = [(1228.0, 1117.7, 1538.0, 1336.6), (1674.7, 1208.8, 2021.1, 1482.5), (1292.0, 1537.6, 1510.9, 1820.5),
               (2057.6, 1491.6, 2267.3, 1646.7)]
# Os jardins (item 16): os dois canteiros da floreira da legenda (o do lavabo e o da sala íntima), cada um na sala
# inteira; só plantas verdes da biblioteca, no tamanho real, sem passar das paredes nem dos vidros
JARDINS_D = {
    "terra": (38, 54, 40), "terra_ruido": 0.10,
    "forracao": {"nomes": ["arbusto_1", "arbusto_2", "arbusto_3"], "d_m": (0.40, 0.55), "passo_m": 0.32, "tom": 0.92},
    "canteiros": [
        ("jardim do lavabo", (2583, 1212, 2700, 1325), 21,
         [("costela_de_adao", 0.85, (0.30, 0.30), 0), ("palmeira_3", 0.80, (0.70, 0.68), 90),
          ("planta_folhas_largas", 0.70, (0.72, 0.25), 180), ("arbusto_2", 0.55, (0.25, 0.75), 0)]),
        ("jardim da sala íntima", (1460, 1690, 1796, 1757), 22,
         [("palmeira_3", 0.85, (0.08, 0.50), 0), ("costela_de_adao", 0.80, (0.24, 0.45), 90),
          ("planta_folhas_largas", 0.75, (0.40, 0.55), 180), ("palmeira_2", 0.95, (0.56, 0.48), 0),
          ("costela_de_adao", 0.80, (0.73, 0.52), 270), ("planta_folhas_largas", 0.70, (0.88, 0.45), 90),
          ("arbusto_1", 0.55, (0.96, 0.55), 0)])]}
FLOREIRA_COR = (58, 122, 79)
# A vegetação do gramado (item 1): as plantas da biblioteca no tamanho real, nos lugares das do render, só nos dois
# cantos da esquerda, junto à piscina e junto à suíte 3. O achado das plantas do render (px do render de 2000) pegava
# também a sombra junto ao muro de cima e os X tracejados na grama abaixo da garagem (fileiras de palmeiras que o render
# não tem); essas caixas saem. Junto à suíte 3, só as plantas até 1,8 m, a até ~1,5 m da parede (as árvores de 4 m
# avançavam pelo gramado, como os leques do motor).
VEGETACAO_D = {"fora_render": [(400, 0, 2000, 125), (1370, 380, 2000, 520), (1395, 600, 2000, 1116)],
               "suite3_render": (1290, 600, 2000, 1116), "d_max_m": 1.8}
_plantas_do_gramado = F.plantas_do_gramado


def plantas_do_gramado_d():
    q = VEGETACAO_D
    sx0, sy0, sx1, sy1 = q["suite3_render"]
    out = []
    for x, y, nome, d_m in _plantas_do_gramado():
        if any(a <= x < c and b <= y < e for a, b, c, e in q["fora_render"]):
            continue
        if sx0 <= x < sx1 and sy0 <= y < sy1 and d_m > q["d_max_m"]:
            continue
        out.append((x, y, nome, d_m))
    return out
# A escada de 16 degraus junto à suíte master (item 11, R14; resposta 3): sobe do Subsolo, numerada de 1 a 16 da
# esquerda para a direita (o "D" do PDF junto ao 16). No Térreo é a chegada: os pisos em Bege Bahia (a legenda), em cada
# bocel a linha cinza suave e a sombra de ~10 cm no degrau de baixo (à esquerda); o triângulo no degrau 16, apontando
# para a esquerda (a descida).
ESCADA_T = {"nome": "de 16 degraus, do Subsolo ao terraço", "pdf": (676.9, 1415.5, 966.0, 1483.5),
            "bocels": [695.0 + 18.07 * k for k in range(15)], "corte": None, "baixo": "esquerda", "inicio": "direita"}
# Os blocos em cascata à esquerda da piscina (item 12, como na Casa B): os 10 blocos de pedra do PDF (ARQ_CONTRAPISO,
# os de 4 lados nesta caixa), cada um em Bege Bahia com o bocel e a sombra curta sobre o de baixo e na grama; o
# triângulo da R14 (resposta 3) no terraço, com a ponta junto à borda do bloco mais alto, apontando para a esquerda,
# para onde descem
# (a caixa vai até 640 pt para o triângulo, que fica no terraço, à direita da ponta, caber inteiro)
BLOCOS_D = dict(F.BLOCOS_F, caixa_pt=(300.0, 800.0, 640.0, 1280.0), triangulos_pt=[(604.0, 1108.0, "esquerda")])
# Os rótulos que partem de outro ponto (pt), no lugar do ponto do PDF (R7): a SUÍTE MASTER (a fachada de cima é vidro
# e brise, que não fecham o ambiente, e o rótulo ia para o terraço, fora da suíte; parte do piso livre à direita da
# cama) e a GARAGEM (no PDF, sobre o carro do meio; parte da faixa de cima, entre o acesso e os carros)
ROTULOS_PONTOS_D = {"Terreo": {"SUÍTE MASTER": (845.9, 1548.2), "GARAGEM": (2628.0, 640.0)}}
# A soleira do elevador em inox escovado (Térreo 21, Subsolo 8; seção 4): o vão da parede direita da cabine, entre os
# batentes do PDF (pt)
SOLEIRA_ELEVADOR_D = dict(C.SOLEIRA_ELEVADOR_C, pt={"Terreo": (1246.6, 1424.0, 1255.2, 1463.7),
                                                    "Subsolo": (1246.6, 1425.4, 1255.2, 1462.2)})


def contexto_d():
    """Os módulos das Casas B e C passam a ler a Casa D: as pastas, a config, o PDF, o render e a base chapada, e os
    parâmetros que são da casa."""
    B.CASA_B = CASA_D
    B.CONFIG_B = CONFIG_D
    B.CACHE = CACHE_D
    B.PAVIMENTOS_B = PAVIMENTOS_D
    B.AFIM_QR_B = AFIM_QR_D
    # o gramado do render de 2000 px (o lote e uma amostra de grama sem plantas), para achar as plantas do motor
    B.GRAMA_B = dict(B.GRAMA_B, lote=(191, 75, 1755, 1000), amostra=(1480, 720, 1720, 800))
    F.ETAPAS = CACHE_D / "final3840"
    B.contexto()
    F.PISOS = PISOS_D
    F.piso_textura = piso_textura_d
    F.arcos_porta = C.arcos_porta_c
    F.PECAS = dict(F.PECAS, humanizar=dict(F.PECAS["humanizar"], zonas_pt={"Terreo": HUMANIZAR_D}),
                   marcas=dict(F.PECAS["marcas"], fora_pt={}))
    F.SAUNA_F = {k: v for k, v in F.SAUNA_F.items() if k not in ("Terreo", "Subsolo")}
    F.PAREDES_F = dict(F.PAREDES_F, muros_pt={}, brises=dict(F.PAREDES_F["brises"], caixa_pt={}),
                       guarda_corpo=dict(F.PAREDES_F["guarda_corpo"], pt={"Terreo": GUARDA_CORPOS_D}, labio_pt={}))
    F.ESQUADRIAS_F = {"de_volta_pt": {}, "travertino_pt": {}, "ref_pt": {}}
    F.alfa_canteiros = alfa_canteiros_d
    F.plantas_do_gramado = plantas_do_gramado_d
    F.cubas_bancada = cubas_bancada_d
    F.vasos_sanitarios = vasos_sanitarios_d
    C.jardins_c = jardins_d
    F.ROTULOS_F = dict(F.ROTULOS_F, livres=("JARDIM",), textos={}, pontos=ROTULOS_PONTOS_D)
    F.BLOCOS_F = BLOCOS_D
    F.BANCADAS_F = dict(F.BANCADAS_F, chapas=CHAPAS_D, **CUBAS_CHAPA_D,
                        travertino_bancada=dict(F.BANCADAS_F["travertino_bancada"],
                                                tom=TRAVERTINO_BRUTO_D["tom_bancada"]),
                        cuba_travertino=dict(F.BANCADAS_F["cuba_travertino"], tom=TRAVERTINO_BRUTO_D["tom_cuba"]))
    B.CARROS_B = CARROS_D
    B.CAMAS_B = CAMAS_D
    B.COOKTOPS_B = COOKTOPS_D
    B.SOLEIRAS_B = dict(B.SOLEIRAS_B, sem=[])
    B.VIDROS_B = dict(B.VIDROS_B, fora=VIDROS_FORA_D)
    B.ROTULOS_FORA, B.ROTULOS_NOMES = [("Ref.", None)], []
    # os títulos das folhas são "0. TÉRREO" e "-1. 1º SUBSOLO": o filtro por "TÉRREO" levava junto o DCE TÉRREO e o
    # WC DCE TÉRREO
    A.FORA = tuple(f for f in A.FORA if f not in ("SUBSOLO", "TÉRREO")) + ("1º SUBSOLO", "0. TÉRREO")
    # os pisos que encostam na grama: os das Casas B e C, mais o Bege Bahia e o granito do acesso de veículos
    B.BORDAS = dict(B.BORDAS, pisos=list(B.BORDAS["pisos"]) + [(232, 232, 232), (50, 66, 90)])
    # as rotinas da Casa C que leem os parâmetros dela
    C.CASA_C, C.CACHE_C = CASA_D, CACHE_D
    C.CAMAS_C, C.BANCOS_C = CAMAS_D, BANCOS_D
    C.JARDINS_C, C.FLOREIRA_COR = JARDINS_D, FLOREIRA_COR
    C.SOLEIRA_ELEVADOR_C = SOLEIRA_ELEVADOR_D


# ----------------------------------------------------------------------------------------------------------------------
# A vegetação e os jardins (as rotinas da Casa C com os canteiros da Casa D)
def alfa_canteiros_d(Q):
    return C.alfa_canteiros_c(Q)


_jardins_c = C.jardins_c


def jardins_d(Q, img):
    """Os canteiros pela rotina da Casa C; os dois da Casa D dão para o gramado (o da sala íntima embaixo, o do lavabo
    à direita), e a limpeza das folhas do motor fora do canteiro tomava a grama por folha e a trocava por manchas
    cinza. Fora dos canteiros, a grama e o traço preto da legenda voltam como estavam."""
    out = _jardins_c(Q, img)
    dentro = cv2.dilate((alfa_canteiros_d(Q) > 0.02).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    volta = Q.cor([F.BORDAS_GRAMA, (0, 0, 0)], tol=6) & ~dentro
    out[volta] = img[volta]
    print(f"    jardins: {int(volta.sum())} px de grama e de traço em volta dos canteiros de volta ao que eram")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# As peças da biblioteca
# As banquetas parcialmente sob a bancada da ilha (usuário, 27/10/26: "as banquetas ficam parcialmente sob a bancada
# da ilha"): o desenho de cada banqueta no PDF (0,42 x 0,46 m, da ARQ_LOUÇAS E METAIS, com o centro puxado para um
# lado) passava por vaso sanitário, e a etapa das tampas pintava por cima uma tampa branca que subia sobre a ilha; as da
# caixa das banquetas saem dos vasos. Antes da banqueta da biblioteca, o piso da caixa dela (fora do tampo) volta ao da
# etapa dos pisos (o resto da banqueta do render ia junto)
_vasos_b = F.vasos_sanitarios


def folhas_d(reg):
    """As folhas da planta do render: o verde (BGR: acima do vermelho) e o escuro abaixo de `escuro` ligado a ele, sem
    buracos; a sombra cinza do render em volta fica fora."""
    from scipy import ndimage
    v = reg[..., 1] > reg[..., 2] + 12
    m = cv2.morphologyEx((v | (reg.mean(axis=2) < PLANTAS_VASO_TD["escuro"])).astype(np.uint8), cv2.MORPH_CLOSE,
                         np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    return ndimage.binary_fill_holes(np.isin(lab, np.unique(lab[v & (lab > 0)])))


def plantas_vaso_d(Q, img, ini):
    guarda = F.PECAS["sombra"]
    F.PECAS["sombra"] = PLANTAS_VASO_TD["sombra"]
    try:
        return C.pecas_do_render(Q, img, ini, VASOS_D, folhas_d, "hall: as plantas em vaso")
    finally:
        F.PECAS["sombra"] = guarda


def vasos_sanitarios_d(Q):
    x0, y0, x1, y1 = BANQUETAS_D["caixa_pt"]
    return [(d, lado) for d, lado in _vasos_b(Q) if not (x0 <= d["rect"].x0 and d["rect"].x1 <= x1
                                                         and y0 <= d["rect"].y0 and d["rect"].y1 <= y1)]


def banquetas_d(Q, img):
    """As 4 banquetas de linho (0,40 m) nos desenhos do PDF abaixo da ilha gourmet, viradas para ela, entrando sob o
    tampo. Os centros: os traços da ARQ_LOUÇAS E METAIS na caixa, agrupados em x."""
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q, s = BANQUETAS_D, F.PECAS["sombra"]
    x0, y0, x1, y1 = q["caixa_pt"]
    rs = sorted([d["rect"] for d in Q.desenhos if d.get("layer") == q["camada"] and x0 <= d["rect"].x0
                 and d["rect"].x1 <= x1 and y0 <= d["rect"].y0 and d["rect"].y1 <= y1], key=lambda r: r.x0)
    grupos = []
    for r in rs:
        if grupos and r.x0 <= grupos[-1][2] + 2.0:
            g = grupos[-1]
            grupos[-1] = [min(g[0], r.x0), min(g[1], r.y0), max(g[2], r.x1), max(g[3], r.y1)]
        else:
            grupos.append([r.x0, r.y0, r.x1, r.y1])
    cs = [Q.p2q((g[0] + g[2]) / 2, (g[1] + g[3]) / 2) for g in grupos]
    if q.get("contorno"):
        # a de linho em 4x, sem a franja do recorte e com o aro fino, como as cadeiras do escritório (virada para cima)
        cor, al = _cadeira_bloco(Q, (0, -1), contorno=MOVEIS_TD["cadeira"]["contorno"], m=B.BANQUETAS_B["d_m"])
    else:
        cor, al = blocos.bloco("banqueta_linho", B.BANQUETAS_B["d_m"] * Q.px_m / 0.45)
    for _ in range(q["giro"] // 90):
        cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
    al = np.clip(al, 0, 1).astype(np.float32)
    h, w = al.shape
    d_ = s["dist_m"] * Q.px_m
    out = img.astype(np.float32)
    tampo = Q.preencher(lambda d: d.get("layer") == "ARQ_BANCADAS" and d.get("fill"), fs=False)
    f = int(np.ceil(d_ + 4 * s["sig_m"] * Q.px_m)) + 2
    caixas = [(int(cx - w / 2) - f, int(cy - h / 2) - f) for cx, cy in cs]
    if q.get("piso") == "bege":
        # o piso das caixas (fora do tampo) no desenho do Bege Bahia, na luz do Bege Bahia em volta: a etapa dos pisos
        # ainda tem ali as banquetas do render, que voltavam por baixo das novas como um aro cinza
        buraco = np.zeros(tampo.shape, bool)
        for X0, Y0 in caixas:
            buraco[Y0:Y0 + h + 2 * f, X0:X0 + w + 2 * f] = True
        buraco &= tampo < 0.5
        ys, xs = np.nonzero(buraco)
        bx0, by0, bx1, by1 = xs.min() - 30, ys.min() - 30, xs.max() + 31, ys.max() + 31
        Dd, bege = bege_desenho_d(Q, (bx0, by0, bx1, by1))
        ok = (cv2.erode(bege[by0:by1, bx0:bx1].astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & \
            ~cv2.dilate(buraco[by0:by1, bx0:bx1].astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & \
            (tampo[by0:by1, bx0:bx1] < 0.05)
        luz = _tom_em_escalas(out[by0:by1, bx0:bx1] / Dd, buraco[by0:by1, bx0:bx1], ok,
                              MOVEIS_TD["conjunto_varanda"]["luz_px"])
        pisos = out.copy()
        pisos[by0:by1, bx0:bx1] = luz * Dd
    else:
        pisos = cv2.imread(str(F.ETAPAS / f"{Q.chave}_pisos.png")).astype(np.float32)
    for (cx, cy), (X0, Y0) in zip(cs, caixas):
        Wr, Hr = w + 2 * f, h + 2 * f
        Mt = np.float32([[1, 0, cx - w / 2 - X0], [0, 1, cy - h / 2 - Y0]])
        livre = 1 - tampo[Y0:Y0 + Hr, X0:X0 + Wr]
        a = cv2.warpAffine(al, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        c = cv2.warpAffine(cor.astype(np.float32), Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Wr, Hr)), (0, 0),
                              s["sig_m"] * Q.px_m) * s["forca"] * livre
        a = a * livre
        piso = pisos[Y0:Y0 + Hr, X0:X0 + Wr]
        out[Y0:Y0 + Hr, X0:X0 + Wr] = np.where((livre > 0.5)[..., None], piso, out[Y0:Y0 + Hr, X0:X0 + Wr])
        reg = out[Y0:Y0 + Hr, X0:X0 + Wr]
        reg *= (1 - sb * (1 - a))[..., None]
        out[Y0:Y0 + Hr, X0:X0 + Wr] = reg * (1 - a[..., None]) + c * a[..., None]
    print(f"    ilha gourmet: {len(cs)} banquetas de linho da biblioteca nos desenhos do PDF, parcialmente sob o tampo, "
          f"sobre o piso refeito")
    return np.clip(out, 0, 255).astype(np.uint8)


def biblioteca_d(Q, img):
    out = np.ascontiguousarray(img.copy())
    with F.em_quadro(Q):
        if Q.chave == "Terreo":
            out = B.cooktops_b(out)
            out = banquetas_d(Q, out)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Os móveis humanizados (pedidos de 27/10, vendo a final: "melhorar a representação dos mobiliários. eles ainda estão
# fotocópia do original. preciso de textura e efeito humanizado [...] revise uma a uma"; nas poltronas do living:
# "essas linhas marcantes devem sair e termos algo mais humanizado com textura e revestimento"; no estar junto à mesa de
# jantar: "melhore o aspecto das poltronas e da mesa de centro. as linhas marcam muito"; na sala íntima: "melhore a
# aparencia dessa poltrona. revestimento, textura"; nos quartos: "melhore a aparencia das cadeiras e as coloque
# parcialmente sob as mesas"). As poltronas redondas do living, a da sala íntima e a cadeira da suíte master estão na
# ARQ_LOUÇAS E METAIS do PDF e saíam em louça branca, com o contorno.
# - Os estofados: a silhueta de cada peça do PDF (os preenchimentos dela na caixa, `lado_pt` entre os limites), sem os
#   traços: as almofadas (as regiões entre os traços de dentro) com volume (a altura sobe da borda para o miolo, `raio_m`;
#   a luz do alto à direita, `contraste`, e o vale escuro junto às costuras e à borda, `vale`), a trama do bouclé
#   (`trama`) e, no lugar do contorno, a borda macia no tom da peça escurecido (`borda`). Os de uma peça só em várias
#   partes (a cadeira da suíte 1) vão juntos (`unir`).
# - As mesas de madeira (a de centro e as laterais redondas, no tom quente): a madeira que já têm, levada até a borda no
#   lugar do contorno escuro, com o chanfro claro em cima e à direita e escuro embaixo e à esquerda.
# - As cadeiras parcialmente sob as mesas: a cadeira do render sai (o piso da etapa dos pisos fora da mesa e, onde ela
#   entrava no tampo, o tampo refeito, `_refaz_tampo`) e a de madeira e linho da biblioteca (`cadeira`) entra virada
#   para a mesa, com 1/3 sob o tampo e a sombra curta dele por cima.
# - Os armários até o teto: o tracejado branco que o render deixou na diagonal deles ("tem um risco branco no meio do
#   guarda roupa. precisamos limpar esses resíduos da planta"): ao longo de cada diagonal da DOC_LINHAS (mais de
#   `min_pt`), o ponto mais claro que a mediana em pé e a deitada, ou que os 4 vizinhos, toma a média do par de
#   vizinhos mais parecido (os cabides e as prateleiras ficam).
MOVEIS_TD = {
    "ss": 4,
    "estofados": [("as 4 poltronas do estar junto à mesa de jantar", (1890.0, 930.0, 2075.0, 1120.0), (45, 60), False),
                  ("as 2 poltronas redondas do living", (1785.0, 1210.0, 1910.0, 1268.0), (38, 50), False),
                  ("a poltrona da sala íntima", (1368.0, 1535.0, 1428.0, 1595.0), (45, 56), False, 99.0),
                  # usuário, 27/10/26: "aprimore o revestimento dessa poltrona e seu apoio" (a poltrona girada e o puff)
                  ("a poltrona e o apoio da suíte 2", (1605.0, 1580.0, 1705.0, 1665.0), (35, 60), False),
                  # usuário, 27/10/26: "aplique na poltrona e suporte da suíte master o mesmo revestimento estofado da
                  # poltrona da suíte" (a da suíte 2); no PDF, as costuras dela vêm picadas em segmentos curtos (de
                  # menos de 1 a 4,8 pt): todos contam, para o assento, o encosto e os braços saírem em partes
                  ("a poltrona e o apoio da suíte master", (500.0, 1590.0, 590.0, 1680.0), (35, 60), False, 0.1)],
    # a poltrona da sala íntima (o círculo do PDF, com o desenho miúdo): uma concha em bouclé, o assento (`assento`, do
    # raio) puxado para a frente (para a mesa de centro e o sofá), o encosto e os braços em volta, mais altos
    "conchas": {"a poltrona da sala íntima": {"frente": (-0.28, 0.96), "assento": 0.64, "desvio": 0.20}},
    "cor": {"poltrona": (200, 212, 222), "cadeira": (170, 180, 190)},
    "costura_min_pt": 14.0,
    "estofado": {"raio_m": 0.10, "altura": 3.0, "contraste": 0.8, "luz_min": -0.30, "luz_max": 0.18, "vale": 0.14,
                 "trama": 0.035, "borda": 0.74, "costura_px": 0.9, "silhueta_px": 0.9, "semente": 2711,
                 # os vincos (usuário, 27/10/26: "você tirou as linhas, mas não deixou o contorno delas em formato de
                 # sombra para deixar claro as partes e encosto da poltrona"): cada traço de dentro do PDF (de
                 # `vinco_min_pt` para cima, longe da borda) vira uma sombra macia, com o lado da luz mais claro
                 "vinco": 0.30, "vinco_sig_px": 0.75, "vinco_min_pt": 2.5, "vinco_borda_px": 1.4, "realce": 0.10,
                 "realce_px": 0.9},
    "madeiras": {"zonas_pt": [(1860.0, 930.0, 2075.0, 1120.0), (1785.0, 1210.0, 1910.0, 1268.0)], "lado_pt": (10, 60),
                 "quente": 28, "miolo_px": 2, "chanfro_m": 0.03, "chanfro": 1.6, "aro": 0.22},
    # as cadeiras das mesas de trabalho: (nome, caixa da cadeira do PDF, mesa, para onde olha, refazer o tampo sob a
    # cadeira antiga[, de onde vem o piso: (dx, dy) px]); a nova (a de madeira e linho da biblioteca, `cadeira`) entra
    # com 1/3 sob o tampo. O piso volta da etapa dos pisos; na suíte master, onde ela ainda tem as pontas dos braços da
    # cadeira do render, vem do vinílico livre ao lado (entre o banco da cama e a cadeira), na mesma fileira de réguas
    "cadeiras_mesas": [("suíte master", (846.6, 1618.9, 890.4, 1660.8), (872.5, 1588.4, 906.5, 1700.6), (1, 0), True,
                        (-40, 0)),
                       ("suíte 1", (1132.7, 1594.3, 1167.8, 1627.8), (1104.9, 1577.0, 1246.6, 1605.4), (0, -1), True,
                        (58, 0)),
                       ("escritório", (2156.8, 1740.9, 2190.2, 1776.0), (2122.5, 1701.8, 2167.8, 1815.1), (-1, 0),
                        False, (28, 0)),
                       ("escritório (visita de cima)", (2100.5, 1713.8, 2131.3, 1746.2),
                        (2122.5, 1701.8, 2167.8, 1815.1), (1, 0), False, (-36, 0)),
                       ("escritório (visita de baixo)", (2100.5, 1770.7, 2131.3, 1803.1),
                        (2122.5, 1701.8, 2167.8, 1815.1), (1, 0), False, (-36, 0))],
    # o contorno das cadeiras do escritório (usuário, 29/10/26, com o recorte da mesa da suíte 3/escritório: "melhore o
    # contorno dessas cadeiras do escritório"; depois, com os recortes das da suíte 1 e da suíte master: "faça os retoques
    # a essa cadeira" e "faça retoques nessa cadeira também"): no bloco em 4x, a franja clara do recorte sai (a cor da beira é a do
    # miolo mais perto, `miolo_px4` para dentro; o alfa recua `recuo_px4` e fica macio em `suave_px4`) e a silhueta
    # ganha a beira fina mais escura (`aro_px4`, até `aro_tom` da cor), como o contorno das outras peças; o piso em
    # volta vem das réguas da mesma fileira, ao lado (`fundo` nas cadeiras do escritório e das suítes: na etapa dos pisos
    # o vinílico ali é outro, ou ainda tem a cadeira do render, e ficava o retângulo escuro ou o aro cinza da antiga); a
    # beira do tampo (`borda_mesa`, só na mesa do escritório, a única com o traço cinza; o traço,
    # `desloc_px` além da linha do PDF, como o traço que já está no render) volta por cima das cadeiras, `alem_pt` para
    # cada lado delas (todo o trecho em que o piso foi refeito)
    "cadeira": {"bloco": "banqueta_linho", "largura_bloco_m": 0.45, "m": 0.56, "sob": 1 / 3, "folga_px": 7,
                "contorno": {"nomes": ("escritório", "suíte master", "suíte 1"), "miolo_px4": 2, "recuo_px4": 1, "suave_px4": 0.7,
                             "aro_px4": 3.0, "aro_tom": 0.74,
                             "borda_mesa": {"nomes": ("escritório",), "cor": (100, 110, 122), "larg_px": 1.5,
                                            "desloc_px": (0.7, 0.5), "alem_pt": 13.0}}},
    # os jogos de mesa da varanda gourmet (usuário, 27/10/26: "melhore o aspectos desses jogos de mesa. adicione um
    # freijó às mesas e cadeiras mais realistas e humanizadas"; depois, vendo o conjunto da biblioteca: "USE ESSA MESA E
    # CADEIRAS NA VARANDA, NO LUGAR DAQUELAS"): o conjunto de mesa de madeira com 6 cadeiras de couro
    # (`mesa_redonda_6_couro`, a referência do usuário das mesas da varanda da Casa E, na mesma disposição das cadeiras do
    # PDF) no centro de cada mesa, com o tampo (`tampo_px` no bloco a `px_m_bloco`) no diâmetro da mesa do PDF (1,60 m);
    # o segundo girado 180°, como na Casa E
    "jogos": [{"mesa_pt": (1254.9, 974.6, 1345.6, 1065.3), "giro": 0},
              {"mesa_pt": (1425.0, 974.6, 1515.7, 1065.3), "giro": 180}],
    "conjunto_varanda": {"bloco": "mesa_redonda_6_couro", "px_m_bloco": 400, "tampo_px": 705, "luz_px": 8.0,
                         # o tom mais próximo das outras mobílias (usuário, 27/10/26: "conseguimos deixar o tom desses
                         # mobiliários mais próximo do tom das outras mobílias? não queria que destoasse"): a nogueira
                         # escura do tampo no mel do aparador e da mesa de jantar, o couro escuro das cadeiras no areia
                         # do linho e do bouclé, o vidro fumê do centro num cinza claro; cada parte no seu `tom` (BGR),
                         # na luz da foto (`gama`: o contraste dela). As cadeiras voltaram ao couro da foto (usuário,
                         # 27/10/26, vendo-as no areia: "volta as cadeiras que estavam antes"): `couro` None, sem tom
                         "tons": {"madeira": ((126, 156, 188), 1.0), "couro": None,
                                  "vidro": ((140, 146, 152), 0.8), "sat_vidro": 45, "borda_px": 3.0}},
    "diagonais": {"min_pt": 30.0, "faixa_px": 5.0, "claro": 12, "vizinhos": 10, "mediana_px": 7},
}


def _dentro_pt(r, z, folga=0.5):
    return z[0] - folga <= r.x0 and r.x1 <= z[2] + folga and z[1] - folga <= r.y0 and r.y1 <= z[3] + folga


def _caixa_px(Q, rs, folga=(4, 5)):
    x0 = min(r.x0 for r in rs)
    y0 = min(r.y0 for r in rs)
    x1 = max(r.x1 for r in rs)
    y1 = max(r.y1 for r in rs)
    (a, b), (c, d) = Q.p2q(x0, y0), Q.p2q(x1, y1)
    return int(np.floor(min(a, c))) - folga[0], int(np.floor(min(b, d))) - folga[0], \
        int(np.ceil(max(a, c))) + folga[1], int(np.ceil(max(b, d))) + folga[1]


def _mascara_pdf(Q, ds, X0, Y0, w, h, ss, traco_px=None):
    m = np.zeros((h * ss, w * ss), np.uint8)
    for d in ds:
        for c in Q.caminhos(d):
            p = np.int32(np.round((np.float32(c) - (X0, Y0)) * ss))
            if traco_px is None and len(c) >= 3:
                cv2.fillPoly(m, [p], 255)
            elif traco_px is not None and len(c) >= 2:
                cv2.polylines(m, [p], False, 255, max(1, int(round(traco_px * ss))), cv2.LINE_8)
    return m


def estofado_d(Q, img, fills, tracos, cor, rng, concha=None, vincos=()):
    q, ss = MOVEIS_TD["estofado"], MOVEIS_TD["ss"]
    X0, Y0, X1, Y1 = _caixa_px(Q, [d["rect"] for d in fills])
    w, h = X1 - X0, Y1 - Y0
    M = _mascara_pdf(Q, fills, X0, Y0, w, h, ss)
    Mx = cv2.dilate(M, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(q["silhueta_px"] * ss) + 1,) * 2))
    Cs = _mascara_pdf(Q, tracos, X0, Y0, w, h, ss, traco_px=q["costura_px"]) & M
    if concha:
        ys, xs = np.nonzero(M)
        cx, cy, R = xs.mean(), ys.mean(), (xs.max() - xs.min()) / 2
        fr = np.float32(concha["frente"]) / np.linalg.norm(concha["frente"])
        sc = (int(round(cx + fr[0] * concha["desvio"] * R)), int(round(cy + fr[1] * concha["desvio"] * R)))
        cv2.circle(Cs, sc, int(round(concha["assento"] * R)), 255, max(1, int(round(q["costura_px"] * ss))))
        Cs &= M
    # os vincos: os traços de dentro e a costura da concha, longe da borda (lá fica a borda macia)
    V = (_mascara_pdf(Q, vincos, X0, Y0, w, h, ss, traco_px=q["costura_px"]) > 0) if vincos else np.zeros(M.shape, bool)
    if concha:
        V |= Cs > 0
    V &= cv2.distanceTransform((M > 0).astype(np.uint8), cv2.DIST_L2, 5) > q["vinco_borda_px"] * ss
    n, lab = cv2.connectedComponents(((M > 0) & (Cs == 0)).astype(np.uint8), connectivity=4)
    hgt = np.zeros(M.shape, np.float32)
    R = q["raio_m"] * Q.px_m * ss
    for i in range(1, n):
        mi = (lab == i).astype(np.uint8)
        if mi.sum() < 4 * ss * ss:
            continue
        dist = cv2.distanceTransform(mi, cv2.DIST_L2, 5)
        t = np.clip(dist / max(min(R, dist.max() * 0.9), 1e-3), 0, 1)
        hgt = np.maximum(hgt, (1 - (1 - t) ** 2.2) * (mi > 0))
    hgt = cv2.GaussianBlur(hgt, (0, 0), 1.0 * ss)
    gy, gx = np.gradient(hgt * q["altura"])
    nz = 1.0 / np.sqrt(gx ** 2 + gy ** 2 + 1)
    L = np.float32([0.55, -0.55, 0.63])
    L /= np.linalg.norm(L)
    luz = np.clip(((-gx * L[0] - gy * L[1] + L[2]) * nz - L[2]) * q["contraste"], q["luz_min"], q["luz_max"])
    a = cv2.GaussianBlur(rng.normal(0, 1, M.shape).astype(np.float32), (0, 0), 0.45 * ss)
    b = cv2.GaussianBlur(rng.normal(0, 1, M.shape).astype(np.float32), (0, 0), 1.2 * ss)
    tr = a / max(a.std(), 1e-6) + 0.25 * b / max(b.std(), 1e-6)
    tr /= max(tr.std(), 1e-6)
    f = (1 + luz) * (1 - q["vale"] * (1 - hgt)) * (1 + q["trama"] * tr)
    if V.any():
        sg = q["vinco_sig_px"] * ss
        pico = min(1.0, q["costura_px"] * ss / (np.sqrt(2 * np.pi) * sg))
        d_ = q["realce_px"] * ss

        def vinco(dx, dy):
            v = cv2.warpAffine(V.astype(np.float32), np.float32([[1, 0, dx], [0, 1, dy]]), V.shape[::-1])
            return np.clip(cv2.GaussianBlur(v, (0, 0), sg) / pico, 0, 1)
        escuro = vinco(d_ * 0.4, -d_ * 0.4)                # a sombra do vinco, puxada para o lado oposto à luz
        claro = np.clip(vinco(-d_, d_) - escuro, 0, 1)       # a borda do vinco virada para a luz (alto à direita)
        f *= (1 - q["vinco"] * escuro) * (1 + q["realce"] * claro)
    rgb = np.float32(cor)[None, None, :] * f[..., None]

    def red(x):
        return cv2.resize(x, (w, h), interpolation=cv2.INTER_AREA)
    a_sil = red(Mx.astype(np.float32) / 255)
    a_in = red(M.astype(np.float32) / 255)
    soma = red(rgb * (M > 0)[..., None])
    cor_q = (soma + np.float32(cor) * q["borda"] * (a_sil - a_in)[..., None]) / np.maximum(a_sil, 1e-4)[..., None]
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    img[Y0:Y1, X0:X1] = np.clip(reg * (1 - a_sil[..., None]) + cor_q * a_sil[..., None], 0, 255).astype(np.uint8)
    return img


def madeira_d(Q, img, d_fill):
    q, ss = MOVEIS_TD["madeiras"], MOVEIS_TD["ss"]
    X0, Y0, X1, Y1 = _caixa_px(Q, [d_fill["rect"]])
    w, h = X1 - X0, Y1 - Y0
    M = _mascara_pdf(Q, [d_fill], X0, Y0, w, h, ss)
    Mx = cv2.dilate(M, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ss + 1,) * 2))

    def red(x):
        return cv2.resize(x, (w, h), interpolation=cv2.INTER_AREA)
    a_sil = red(Mx.astype(np.float32) / 255)
    a_in = red(M.astype(np.float32) / 255)
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    # o miolo (a madeira a mais de `miolo_px` da borda); o resto toma o px do miolo mais perto
    miolo = cv2.erode((a_in > 0.99).astype(np.uint8), np.ones((2 * q["miolo_px"] + 1,) * 2, np.uint8))
    if miolo.sum() < 4:
        return img
    _, lab = cv2.distanceTransformWithLabels(1 - miolo, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(miolo)
    idx = np.zeros(lab.max() + 1, np.int64)
    idx[lab[ys, xs]] = np.arange(len(ys))
    near = idx[lab]
    mad = np.where(miolo[..., None] > 0, reg, reg[ys[near], xs[near]])
    dist = cv2.distanceTransform((M > 0).astype(np.uint8), cv2.DIST_L2, 5) / ss
    bv = red(np.clip(dist / (q["chanfro_m"] * Q.px_m), 0, 1))
    gy, gx = np.gradient(cv2.GaussianBlur(bv, (0, 0), 0.6))
    luz = np.clip((gx * -0.7 + gy * 0.7) * q["chanfro"], -0.18, 0.14)
    fat = (1 - luz) * (1 - q["aro"] * np.clip(a_sil - a_in, 0, 1) / np.maximum(a_sil, 1e-3))
    img[Y0:Y1, X0:X1] = np.clip(reg * (1 - a_sil[..., None]) + mad * fat[..., None] * a_sil[..., None], 0,
                                255).astype(np.uint8)
    return img


def diagonais_armarios_d(Q, img):
    q = MOVEIS_TD["diagonais"]
    m = np.zeros((Q.H, Q.W), np.uint8)
    n = 0
    for d in Q.desenhos:
        if d.get("layer") != "DOC_LINHAS E PROJEÇÕES":
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            a, b = it[1], it[2]
            if abs(a.x - b.x) > 5 and abs(a.y - b.y) > 5 and np.hypot(a.x - b.x, a.y - b.y) >= q["min_pt"]:
                pa, pb = Q.p2q(a.x, a.y), Q.p2q(b.x, b.y)
                cv2.line(m, tuple(int(round(v)) for v in pa), tuple(int(round(v)) for v in pb), 255,
                         int(round(2 * q["faixa_px"])))
                n += 1
    # o ponto branco é o px mais claro que a mediana em pé e a deitada (os cabides e as prateleiras são lisos num dos
    # dois sentidos) ou que os 4 vizinhos; ele toma a média do par de vizinhos mais parecido (em pé ou deitado), duas
    # passadas para os pares de pontos; a mediana de 11x11 escurecia os vãos entre os cabides e os cantos
    out = img.copy()
    k = q["mediana_px"]
    total = 0
    nc, _, st, _ = cv2.connectedComponentsWithStats(m)
    for i in range(1, nc):
        x0, y0, w, h = st[i, :4]
        x0, y0 = max(x0 - k, 1), max(y0 - k, 1)
        x1, y1 = min(x0 + w + 2 * k, Q.W - 1), min(y0 + h + 2 * k, Q.H - 1)
        faixa = m[y0:y1, x0:x1] > 0
        for _ in range(2):
            reg = out[y0 - 1:y1 + 1, x0 - 1:x1 + 1].astype(np.float32)
            c = reg[1:-1, 1:-1]
            meds = []
            for eixo in (0, 1):
                pad = np.pad(c, [(k // 2, k // 2) if j == eixo else (0, 0) for j in range(3)], mode="edge")
                meds.append(np.median(np.stack([np.take(pad, range(j, j + c.shape[eixo]), axis=eixo)
                                                for j in range(k)]), axis=0))
            lum = c.mean(axis=2)
            dif = [lum - md.mean(axis=2) for md in meds]
            cima, baixo, esq, dir_ = reg[:-2, 1:-1], reg[2:, 1:-1], reg[1:-1, :-2], reg[1:-1, 2:]
            viz = np.max([v.mean(axis=2) for v in (cima, baixo, esq, dir_)], axis=0)
            claro = faixa & ((np.minimum(*dif) > q["claro"]) | (lum - viz > q["vizinhos"]))
            em_pe = np.abs(cima - baixo).sum(axis=2) <= np.abs(esq - dir_).sum(axis=2)
            novo = np.where(em_pe[..., None], (cima + baixo) / 2, (esq + dir_) / 2)
            sub = out[y0:y1, x0:x1]
            sub[claro] = np.clip(novo[claro], 0, 255).astype(np.uint8)
            total += int(claro.sum())
    print(f"    armários até o teto: {total} px do tracejado branco do render nas {n} diagonais voltam ao fundo")
    return out


def _cadeira_bloco(Q, frente, rng=None, contorno=None, m=None):
    """A cadeira de madeira e linho da biblioteca (`MOVEIS_TD["cadeira"]`) em 4x, girada para olhar em `frente` (no bloco,
    a frente do assento olha para cima e o encosto fica embaixo, `blocos.json`): (cor, alfa) em 1x, com o centro no
    meio. Com `contorno` (`MOVEIS_TD["cadeira"]["contorno"]`), a beira sem a franja do recorte e com o aro fino; `m`, a
    largura (m) no lugar da da cadeira."""
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    from scipy import ndimage
    q = MOVEIS_TD["cadeira"]
    cor, al = blocos.bloco(q["bloco"], 4 * (m or q["m"]) * Q.px_m / q["largura_bloco_m"])
    if contorno:
        k = contorno
        cor, al = cor.astype(np.float32), np.clip(al, 0, 1).astype(np.float32)
        n = 2 * k["miolo_px4"] + 1
        miolo = cv2.erode((al > 0.98).astype(np.uint8), np.ones((n, n), np.uint8)) > 0
        _, (iy, ix) = ndimage.distance_transform_edt(~miolo, return_indices=True)
        cor = np.where(miolo[..., None], cor, cor[iy, ix])
        n = 2 * k["recuo_px4"] + 1
        al = cv2.GaussianBlur(cv2.erode(al, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))), (0, 0),
                              k["suave_px4"])
        d = ndimage.distance_transform_edt(al > 0.5)
        aro = np.clip(1 - d / k["aro_px4"], 0, 1)
        cor = cor * (1 - (1 - k["aro_tom"]) * aro)[..., None]
    ang = float(np.degrees(np.arctan2(-frente[0], -frente[1])))
    h, w = al.shape
    lado = int(np.ceil(max(h, w) * 1.45 / 4)) + 4
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 0.25)
    M[0, 2] += lado / 2 - w / 2
    M[1, 2] += lado / 2 - h / 2
    a = cv2.warpAffine(np.clip(al, 0, 1).astype(np.float32), M, (lado, lado), flags=cv2.INTER_AREA)
    c = cv2.warpAffine(cor.astype(np.float32) * al[..., None], M, (lado, lado), flags=cv2.INTER_AREA)
    return c / np.maximum(a, 1e-4)[..., None], a


def _pousar(out, cor, a, cx, cy, px_m, cobre=None, sombra=True):
    """Pousa (cor, a) com o centro em (cx, cy) px, em subpixel; `cobre` (alfa no quadro) é o que fica por cima (a
    mesa); a sombra curta das peças."""
    s = F.PECAS["sombra"]
    h, w = a.shape
    f = 8
    X0, Y0 = int(np.floor(cx - w / 2)) - f, int(np.floor(cy - h / 2)) - f
    Wr, Hr = w + 2 * f, h + 2 * f
    Mt = np.float32([[1, 0, cx - w / 2 - X0], [0, 1, cy - h / 2 - Y0]])
    aa = cv2.warpAffine(a, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
    cc = cv2.warpAffine(cor, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
    livre = 1 - cobre[Y0:Y0 + Hr, X0:X0 + Wr] if cobre is not None else 1.0
    reg = out[Y0:Y0 + Hr, X0:X0 + Wr]
    if sombra:
        d_ = s["dist_m"] * px_m
        sb = cv2.GaussianBlur(cv2.warpAffine(aa, np.float32([[1, 0, -d_], [0, 1, d_]]), (Wr, Hr)), (0, 0),
                              s["sig_m"] * px_m) * s["forca"] * livre
        reg *= (1 - sb * (1 - aa))[..., None]
    aa = aa * livre
    reg[:] = reg * (1 - aa[..., None]) + cc * aa[..., None]


def _refaz_tampo(out, mesa_px, faixa, vertical):
    """O tampo sob a cadeira antiga (`faixa`: linhas ao longo do comprimento): o tom coluna a coluna de uma ponta à
    outra e o veio fino espelhado do trecho vizinho."""
    X0, Y0, X1, Y1 = mesa_px
    v = out if vertical else out.transpose(1, 0, 2)
    c0, c1, l0, l1 = (X0, X1, Y0, Y1) if vertical else (Y0, Y1, X0, X1)
    r0, r1 = max(faixa[0], l0 + 2), min(faixa[1], l1 - 2)
    if r1 <= r0:
        return
    orig = v[:, c0:c1].copy()
    ini = orig[max(r0 - 2, l0):r0].mean(axis=0) if r0 > l0 + 1 else orig[r1:r1 + 2].mean(axis=0)
    fim = orig[r1:min(r1 + 2, l1)].mean(axis=0) if r1 < l1 - 1 else ini
    L = r1 - r0
    t = ((np.arange(L) + 0.5) / L)[:, None, None]
    det = orig - cv2.GaussianBlur(orig, (1, 0), sigmaX=0.1, sigmaY=4.0)
    idx = np.arange(r0, r1)
    meio = (r0 + r1) / 2
    src = np.where(idx < meio, 2 * r0 - 1 - idx, 2 * r1 - 1 - idx)
    src = np.clip(src, l0 + 1, l1 - 2)
    v[r0:r1, c0:c1] = ini[None] * (1 - t) + fim[None] * t + det[src]


def cadeiras_mesas_d(Q, img, piso, nomes=None, refaz_tampo=True):
    """As cadeiras das mesas de trabalho: a antiga sai (o piso da etapa dos pisos, ou o de `fundo`, fora da mesa; e o
    tampo refeito onde ela o cobria), a nova entra virada para a mesa, com 1/3 sob o tampo, e a sombra do tampo cai
    sobre ela. Com `nomes`, só as cadeiras cujo nome começa por um deles; `refaz_tampo` False deixa o tampo como está
    (numa imagem em que ele já foi refeito)."""
    import final3840_casaa as FA
    q, qc, s = MOVEIS_TD, MOVEIS_TD["cadeira"], F.PECAS["sombra"]
    out = img.astype(np.float32)
    P = piso.astype(np.float32)
    D_px = qc["m"] * Q.px_m
    for nome, cad, mesa, frente, refaz, *fundo in q["cadeiras_mesas"]:
        if nomes and not nome.startswith(tuple(nomes)):
            continue
        mesa_a = FA.ret_aa(Q, mesa)
        mx0, my0, mx1, my1 = F.ret_q(Q, mesa)
        vertical = (my1 - my0) > (mx1 - mx0)
        cx0, cy0, cx1, cy1 = F.ret_q(Q, cad)
        f = qc["folga_px"]
        if refaz and refaz_tampo:
            faixa = (cy0 - 2, cy1 + 2) if vertical else (cx0 - 2, cx1 + 2)
            _refaz_tampo(out, (mx0, my0, mx1, my1), faixa, vertical)
        # o piso de volta onde estava a cadeira antiga (com a sombra dela), fora da mesa, emendado em 1,5 px
        m = np.zeros(mesa_a.shape, np.float32)
        m[cy0 - f:cy1 + f, cx0 - f:cx1 + f] = 1
        m = cv2.GaussianBlur(m, (0, 0), 1.5) * (1 - np.clip(mesa_a * 1.5, 0, 1))
        Pc = P
        if fundo:
            dx, dy = fundo[0]
            Pc = P.copy()
            a0, b0, a1, b1 = cx0 - 2 * f, cy0 - 2 * f, cx1 + 2 * f, cy1 + 2 * f
            Pc[b0:b1, a0:a1] = out[b0 + dy:b1 + dy, a0 + dx:a1 + dx]
        out = out * (1 - m[..., None]) + Pc * m[..., None]
        # a cadeira nova: o centro na linha do da antiga, a frente 1/3 sob o tampo
        ccx, ccy = Q.p2q((cad[0] + cad[2]) / 2, (cad[1] + cad[3]) / 2)
        if frente[0]:
            borda = Q.p2q(mesa[0] if frente[0] > 0 else mesa[2], 0)[0]
            ccx = borda - frente[0] * D_px * (0.5 - qc["sob"])
        else:
            borda = Q.p2q(0, mesa[1] if frente[1] > 0 else mesa[3])[1]
            ccy = borda - frente[1] * D_px * (0.5 - qc["sob"])
        ct = qc.get("contorno")
        cor, a = _cadeira_bloco(Q, frente, contorno=ct if ct and nome.startswith(ct["nomes"]) else None)
        _pousar(out, cor, a, ccx, ccy, Q.px_m, cobre=mesa_a)
        # a sombra curta do tampo só sobre a cadeira (no piso, a mesa do render não tem sombra)
        d_ = s["dist_m"] * Q.px_m
        sb = cv2.GaussianBlur(cv2.warpAffine(mesa_a, np.float32([[1, 0, -d_], [0, 1, d_]]), mesa_a.shape[::-1]),
                              (0, 0), s["sig_m"] * Q.px_m) * s["forca"]
        cad_a = np.zeros_like(mesa_a)
        h, w = a.shape
        cad_a[int(ccy - h / 2):int(ccy - h / 2) + h, int(ccx - w / 2):int(ccx - w / 2) + w] = a
        alvo = np.clip(cad_a, 0, 1) * (1 - mesa_a)
        out *= (1 - sb * alvo)[..., None]
        if ct and nome.startswith(ct["borda_mesa"]["nomes"]):
            # a beira do tampo passa por cima da cadeira (o piso de volta apagava o traço dela ali)
            bm = ct["borda_mesa"]
            ox, oy = (v / 1.0525 for v in bm["desloc_px"])
            if frente[0]:
                xb = (mesa[0] if frente[0] > 0 else mesa[2]) + ox
                seg = (xb, max(cad[1] - bm["alem_pt"], mesa[1]), xb, min(cad[3] + bm["alem_pt"], mesa[3]))
            else:
                yb = (mesa[1] if frente[1] > 0 else mesa[3]) + oy
                seg = (max(cad[0] - bm["alem_pt"], mesa[0]), yb, min(cad[2] + bm["alem_pt"], mesa[2]), yb)
            out = _tracos_d(Q, out, [seg], bm["cor"], bm["larg_px"]).astype(np.float32)
        print(f"    cadeira do {nome}: a de madeira e linho da biblioteca, 1/3 sob o tampo, com a sombra dele")
    return np.clip(out, 0, 255).astype(np.uint8)


def bege_limpo_d(Q, piso, caixa, fora):
    """O Bege Bahia dos pisos refeito na `caixa` (px) onde a etapa dos pisos ainda tem o render (as peças do render
    ficam fora da legenda): o mesmo desenho (`textura("bege_bahia")` com a semente e o retângulo de `F.piso_textura`,
    guardado em `F.ETAPAS`) na luz do piso em volta (o piso dividido pelo desenho, liso, levado para dentro, fora de
    `fora`)."""
    x0, y0, x1, y1 = caixa
    Dd, bege = bege_desenho_d(Q, caixa)
    sub = piso[y0:y1, x0:x1].astype(np.float32)
    ok = (cv2.erode(bege[y0:y1, x0:x1].astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & ~fora[y0:y1, x0:x1]
    sg = MOVEIS_TD["conjunto_varanda"]["luz_px"]
    L = cv2.GaussianBlur(sub / Dd * ok[..., None], (0, 0), sg) / np.maximum(
        cv2.GaussianBlur(ok.astype(np.float32), (0, 0), sg), 1e-4)[..., None]
    return L * Dd


def bege_desenho_d(Q, caixa):
    """O desenho do Bege Bahia na `caixa` (px), em volta de 1 (`textura("bege_bahia")` com a semente e o retângulo de
    `F.piso_textura`, guardado em `F.ETAPAS`), e a máscara do Bege Bahia do PDF."""
    x0, y0, x1, y1 = caixa
    arq = F.ETAPAS / f"{Q.chave}_bege_{x0}_{y0}_{x1}_{y1}.npy"
    bege = Q.cor([(232, 232, 232)], tol=6)
    if arq.exists():
        Dd = np.load(arq)
    else:
        sys.path.insert(0, str(RAIZ / "_texturas"))
        from texturas import textura
        ys, xs = np.nonzero(bege)
        by0, bx0, by1, bx1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
        i = [pz[3] for pz in F.PISOS[Q.chave]].index("bege")
        T = textura("bege_bahia", Q.px_m, by1 - by0, bx1 - bx0, semente=700 + i).astype(np.float32)
        Dd = (T / T.reshape(-1, 3).mean(axis=0))[y0 - by0:y1 - by0, x0 - bx0:x1 - bx0]
        np.save(arq, Dd)
    return Dd, bege


def tons_varanda_d(cor, al, q):
    """O bloco do jogo da varanda nos tons de `q["tons"]`: o tampo (o disco de `tampo_px` no centro do bloco), o vidro
    (no tampo, o cinza: saturação abaixo de `sat_vidro`) e o couro (fora do tampo); a passagem do tampo às cadeiras
    suave em `borda_px`. A parte com o tom None fica na cor da foto."""
    t = q["tons"]
    h, w = al.shape
    yy, xx = np.mgrid[:h, :w]
    tampo = np.clip((q["tampo_px"] / 2 - np.hypot(xx - w / 2, yy - h / 2)) / t["borda_px"] + 0.5, 0, 1)
    c8 = np.clip(cor, 0, 255).astype(np.uint8)
    sat = cv2.GaussianBlur(cv2.cvtColor(c8, cv2.COLOR_BGR2HSV)[..., 1].astype(np.float32), (0, 0), 1.5)
    vid = tampo * np.clip((t["sat_vidro"] + 8 - sat) / 16, 0, 1)
    pesos = {"madeira": tampo - vid, "couro": 1 - tampo, "vidro": vid}
    L = np.maximum(cor.astype(np.float32).mean(axis=2), 1.0)
    ok = al > 0.5
    novo = np.zeros(cor.shape, np.float32)
    for nome, p in pesos.items():
        if t[nome] is None:                         # a parte fica na cor da foto
            novo += p[..., None] * cor.astype(np.float32)
            continue
        tom, gama = t[nome]
        med = np.median(L[ok & (p > 0.9)])
        novo += p[..., None] * np.float32(tom) * ((L / med) ** gama)[..., None]
    return np.clip(novo, 0, 255)


def jogos_mesa_d(Q, img, piso):
    """Os jogos de mesa da varanda gourmet: o jogo do render sai (o piso da etapa dos pisos na caixa da mesa e das
    cadeiras do PDF) e entra o conjunto de mesa de madeira e 6 cadeiras de couro da referência do usuário
    (`mesa_redonda_6_couro`), no centro da mesa do PDF, com o tampo no diâmetro dela, girado `giro`, com a sombra curta."""
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = MOVEIS_TD["conjunto_varanda"]
    out = img.astype(np.float32)
    P = piso.astype(np.float32)
    cor, al = blocos.bloco(q["bloco"], q["px_m_bloco"])
    cor = tons_varanda_d(cor, al, q)
    for jg in MOVEIS_TD["jogos"]:
        mesa = jg["mesa_pt"]
        mcx, mcy = (mesa[0] + mesa[2]) / 2, (mesa[1] + mesa[3]) / 2
        cads = [d["rect"] for d in Q.desenhos if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and d["type"] in ("f", "fs")
                and 28 <= max(d["rect"].width, d["rect"].height) <= 40
                and abs((d["rect"].x0 + d["rect"].x1) / 2 - mcx) < 80 and abs((d["rect"].y0 + d["rect"].y1) / 2 - mcy) < 80]
        # o piso de volta na caixa do jogo inteiro (mesa e cadeiras, com as sombras)
        m = np.zeros(out.shape[:2], np.float32)
        for r in cads + [type(cads[0])(*mesa)] if cads else []:
            a0, b0, a1, b1 = F.ret_q(Q, (r.x0, r.y0, r.x1, r.y1))
            m[b0 - 8:b1 + 9, a0 - 9:a1 + 8] = 1
        m = cv2.GaussianBlur(m, (0, 0), 1.5)
        # embaixo do jogo do render, a etapa dos pisos ainda tem as cadeiras dele: ali o Bege Bahia é refeito
        ys, xs = np.nonzero(m > 0.01)
        cx0, cy0, cx1, cy1 = xs.min() - 30, ys.min() - 30, xs.max() + 31, ys.max() + 31
        Pl = P.copy()
        Pl[cy0:cy1, cx0:cx1] = bege_limpo_d(Q, piso, (cx0, cy0, cx1, cy1), m > 0.01)
        out = out * (1 - m[..., None]) + Pl * m[..., None]
        _pousar(out, *_jogo_q(Q, jg, cor, al, q), Q.px_m)
        print("    jogo de mesa da varanda: a mesa de madeira (1,60 m) e as 6 cadeiras de couro da referência do usuário")
    return np.clip(out, 0, 255).astype(np.uint8)


def _jogo_q(Q, jg, cor, al, q):
    """O conjunto no quadro: (cor, alfa, cx, cy), em 4x com o tampo no diâmetro da mesa do PDF, girado `giro` e reduzido
    ao quadro; (cx, cy) é o centro em px, em subpixel."""
    mesa = jg["mesa_pt"]
    (ax, ay), (bx, by) = Q.p2q(mesa[0], mesa[1]), Q.p2q(mesa[2], mesa[3])
    sc = 4 * (bx - ax) / q["tampo_px"]
    c = cv2.resize(cor.astype(np.float32) * al[..., None], None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    a = cv2.resize(al.astype(np.float32), None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    if jg["giro"]:
        c, a = cv2.rotate(c, cv2.ROTATE_180), cv2.rotate(a, cv2.ROTATE_180)
    h4, w4 = a.shape
    h1, w1 = int(np.ceil(h4 / 4)), int(np.ceil(w4 / 4))
    c = cv2.resize(np.pad(c, ((0, h1 * 4 - h4), (0, w1 * 4 - w4), (0, 0))), (w1, h1), interpolation=cv2.INTER_AREA)
    a = cv2.resize(np.pad(a, ((0, h1 * 4 - h4), (0, w1 * 4 - w4))), (w1, h1), interpolation=cv2.INTER_AREA)
    c = c / np.maximum(a, 1e-4)[..., None]
    return c, a, (ax + bx) / 2 + (w1 - w4 / 4) / 2, (ay + by) / 2 + (h1 - h4 / 4) / 2


# A sombra dos jogos da varanda (usuário, 28/10/26, com o recorte das duas mesas: "traga um sombreamento das cadeiras e
# mesas que integre ao piso"): a sombra curta das peças (3,5 cm, 30%) mal aparecia no Bege Bahia. Como o sofá da
# varanda da Casa E ("sombra leve"): uma sombra macia projetada para baixo e à esquerda (a luz do render vem do alto, à
# direita) e uma de contato, junto à base, que assenta as peças no piso. Cada uma é o alfa do conjunto deslocado
# (`dx_m`, `dy_m`), desfocado (`sig_m`) e na `forca`; as duas se somam (1 − Π(1 − s)) e escurecem só o piso, fora das
# peças.
SOMBRA_JOGOS_D = [{"dx_m": -0.10, "dy_m": 0.10, "sig_m": 0.09, "forca": 0.42},
                  {"dx_m": -0.02, "dy_m": 0.02, "sig_m": 0.03, "forca": 0.35}]


def sombra_jogos_d(Q, img):
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = MOVEIS_TD["conjunto_varanda"]
    cor, al = blocos.bloco(q["bloco"], q["px_m_bloco"])
    out = img.astype(np.float32)
    for jg in MOVEIS_TD["jogos"]:
        _, a, cx, cy = _jogo_q(Q, jg, cor, al, q)
        h, w = a.shape
        f = int(np.ceil(max(abs(s["dx_m"]) + 3 * s["sig_m"] for s in SOMBRA_JOGOS_D) * Q.px_m)) + 4
        X0, Y0 = int(np.floor(cx - w / 2)) - f, int(np.floor(cy - h / 2)) - f
        Wr, Hr = w + 2 * f, h + 2 * f
        aa = cv2.warpAffine(a, np.float32([[1, 0, cx - w / 2 - X0], [0, 1, cy - h / 2 - Y0]]), (Wr, Hr),
                            flags=cv2.INTER_LINEAR)
        luz = np.ones((Hr, Wr), np.float32)
        for s in SOMBRA_JOGOS_D:
            d = np.float32([[1, 0, s["dx_m"] * Q.px_m], [0, 1, s["dy_m"] * Q.px_m]])
            sb = cv2.GaussianBlur(cv2.warpAffine(aa, d, (Wr, Hr), flags=cv2.INTER_LINEAR), (0, 0),
                                  s["sig_m"] * Q.px_m) * s["forca"]
            luz *= 1 - sb
        reg = out[Y0:Y0 + Hr, X0:X0 + Wr]
        reg *= (1 - (1 - luz) * (1 - aa))[..., None]
    print(f"    jogos da varanda: a sombra macia e a de contato no piso ({len(MOVEIS_TD['jogos'])} jogos)")
    return np.clip(out, 0, 255).astype(np.uint8)


# A mesa de jantar do living (usuário, 27/10/26: "melhore o aspecto das cadeiras, sem repetir o modelo das demais da
# planta"): as 10 cadeiras do PDF (ARQ_MOBILIÁRIO, de `lado_pt`, junto à mesa, com 1/3 sob o tampo) saem, com o piso da
# etapa dos pisos, e entra a cadeira estofada em linho com o quadro de madeira da mesa de 10 lugares da biblioteca
# (`mesa_jantar_10`, a segunda de cima: a cadeira até onde começa o tampo, `recorte` em px do bloco a `px_m_bloco`), na
# largura da cadeira do PDF, de frente para a mesa, com a borda do recorte `sob_px` sob o tampo; a mesa fica por cima. As
# outras cadeiras da planta são a de madeira e linho (`banqueta_linho`, mesas de trabalho e banquetas) e as de couro dos
# jogos da varanda (`mesa_redonda_6_couro`)
JANTAR_TD = {"mesa_pt": (1697.4, 956.1, 1765.4, 1126.3), "lado_pt": (26.0, 32.0), "bloco": "mesa_jantar_10",
             "px_m_bloco": 400, "recorte": (496, 6, 727, 150), "sob_px": 2.0, "folga_px": 7,
             # o linho da foto, cinza-esverdeado e na sombra da mesa, no bege quente (`tom`, BGR, na luz `gama`); a
             # madeira (saturação acima de `sat_madeira`) fica
             "linho": {"tom": (176, 196, 214), "gama": 0.75, "sat_madeira": (0.30, 0.15)}}


def jantar_d(Q, img, piso, q=None):
    """`q`: a configuração (a da Casa D por padrão). Com `linho["absoluto"]`, o assento fica no `tom` (BGR) na luz da
    foto (a luz de cada px sobre a mediana do assento, na potência `gama`), não só na cor do `tom`."""
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    import final3840_casaa as FA
    q, s = q or JANTAR_TD, F.PECAS["sombra"]
    mesa = q["mesa_pt"]
    cads = [d["rect"] for d in Q.desenhos if d.get("layer") == "ARQ_MOBILIÁRIO" and d["type"] in ("f", "fs")
            and q["lado_pt"][0] <= min(d["rect"].width, d["rect"].height)
            and max(d["rect"].width, d["rect"].height) <= q["lado_pt"][1]
            and mesa[0] - 35 <= d["rect"].x0 and d["rect"].x1 <= mesa[2] + 35
            and mesa[1] - 35 <= d["rect"].y0 and d["rect"].y1 <= mesa[3] + 35]
    out = img.astype(np.float32)
    P = piso.astype(np.float32)
    mesa_a = FA.ret_aa(Q, mesa)
    if q.get("mesa_pdf"):                   # a forma do tampo do PDF (a oval), não a caixa dele
        d_m = next(d for d in Q.desenhos if d.get("layer") == "ARQ_MOBILIÁRIO" and d["type"] in ("f", "fs")
                   and max(abs(a_ - b_) for a_, b_ in zip(d["rect"], mesa)) < 0.5)
        X0_, Y0_, X1_, Y1_ = F.ret_q(Q, mesa)
        mm = _mascara_pdf(Q, [d_m], X0_, Y0_, X1_ - X0_, Y1_ - Y0_, 4).astype(np.float32) / 255
        mesa_a = np.zeros_like(mesa_a)
        mesa_a[Y0_:Y1_, X0_:X1_] = cv2.resize(mm, (X1_ - X0_, Y1_ - Y0_), interpolation=cv2.INTER_AREA)
    f = q["folga_px"]
    m = np.zeros(mesa_a.shape, np.float32)
    # a etapa dos pisos ainda tem as cadeiras do render embaixo das do PDF: o piso de cada caixa vem do travertino ao
    # lado, nas mesmas linhas (os estratos são deitados), do primeiro deslocamento cuja origem é toda travertino na
    # legenda do PDF
    trav = cv2.erode(Q.cor(next(pz[1] for pz in F.PISOS[Q.chave] if pz[3] == "travertino"), tol=6).astype(np.uint8),
                     np.ones((5, 5), np.uint8)) > 0
    Pl = P.copy()
    for r in cads:
        a0, b0, a1, b1 = F.ret_q(Q, (r.x0, r.y0, r.x1, r.y1))
        x0_, y0_, x1_, y1_ = a0 - f - 3, b0 - f - 3, a1 + f + 3, b1 + f + 3
        m[b0 - f:b1 + f, a0 - f:a1 + f] = 1
        passo = x1_ - x0_ + 2
        fora = -1 if (r.x0 + r.x1) / 2 < (mesa[0] + mesa[2]) / 2 else 1
        for dx in [j * fora * passo for i in range(1, q.get("passos", 2) + 1) for j in (i, -i)]:
            if 0 <= x0_ + dx and x1_ + dx <= Q.W and trav[y0_:y1_, x0_ + dx:x1_ + dx].all():
                Pl[y0_:y1_, x0_:x1_] = P[y0_:y1_, x0_ + dx:x1_ + dx]
                break
    m = cv2.GaussianBlur(m, (0, 0), 1.5) * (1 - np.clip(mesa_a * 1.5, 0, 1))
    out = out * (1 - m[..., None]) + Pl * m[..., None]
    k = 4 * Q.px_m
    cor, al = blocos.bloco(q["bloco"], k)
    e = k / q["px_m_bloco"]
    x0, y0, x1, y1 = (int(round(v * e)) for v in q["recorte"])
    c0 = np.clip(cor[y0:y1, x0:x1].astype(np.float32), 0, 255)
    ql = q["linho"]
    sat = cv2.cvtColor(c0.astype(np.uint8), cv2.COLOR_BGR2HSV)[..., 1:2].astype(np.float32) / 255
    madeira = np.clip((sat - ql["sat_madeira"][0]) / ql["sat_madeira"][1], 0, 1)
    if ql.get("absoluto"):
        Lc = c0.mean(axis=2, keepdims=True)
        ok = (al[y0:y1, x0:x1] > 0.5) & (madeira[..., 0] < 0.5)
        linho = np.float32(ql["tom"]) * (Lc / max(float(np.median(Lc[..., 0][ok])), 1.0)) ** ql["gama"]
    else:
        linho = 255 * (c0.mean(axis=2, keepdims=True) / 255) ** ql["gama"] * np.float32(ql["tom"]) / np.mean(ql["tom"])
    # o halo claro do recorte da foto (o fundo que ficou na borda) sai: o alfa 1 px menor no quadro
    a0_ = cv2.erode(al[y0:y1, x0:x1].astype(np.float32), np.ones((5, 5), np.uint8))
    c0 = (linho * (1 - madeira) + c0 * madeira) * a0_[..., None]
    (mx0, my0), (mx1, my1) = Q.p2q(mesa[0], mesa[1]), Q.p2q(mesa[2], mesa[3])
    d_ = s["dist_m"] * Q.px_m
    for r in cads:
        (ax, ay), (bx, by) = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        lado = "esq" if cx < mesa[0] else "dir" if cx > mesa[2] else "cima" if cy < mesa[1] else "baixo"
        if q.get("lado_norm"):              # a mesa oval: as cabeceiras ficam dentro da caixa dela
            u, v = (cx - (mesa[0] + mesa[2]) / 2) / (mesa[2] - mesa[0]), (cy - (mesa[1] + mesa[3]) / 2) / (mesa[3] - mesa[1])
            lado = ("esq" if u < 0 else "dir") if abs(u) > abs(v) else ("cima" if v < 0 else "baixo")
        larg = (by - ay) if lado in ("esq", "dir") else (bx - ax)       # a largura da cadeira ao longo da borda
        sc = 4 * larg / c0.shape[1]
        c = cv2.resize(c0, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
        a = cv2.resize(a0_, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
        # no recorte (a cadeira de cima da mesa da foto), a frente (a borda do tampo) fica embaixo e o encosto curvo em
        # cima: a de cima fica como está e as outras giram para a frente olhar a mesa (usuário, 28/10/26: "AS CADEIRAS
        # DA MESA ESTÃO INVERTIDAS?": o giro estava trocado, com o encosto virado para a mesa)
        giro = {"cima": None, "baixo": cv2.ROTATE_180, "esq": cv2.ROTATE_90_COUNTERCLOCKWISE,
                "dir": cv2.ROTATE_90_CLOCKWISE}[lado]
        if giro is not None:
            c, a = cv2.rotate(c, giro), cv2.rotate(a, giro)
        h4, w4 = a.shape
        h1, w1 = int(np.ceil(h4 / 4)), int(np.ceil(w4 / 4))
        c = cv2.resize(np.pad(c, ((0, h1 * 4 - h4), (0, w1 * 4 - w4), (0, 0))), (w1, h1), interpolation=cv2.INTER_AREA)
        a = cv2.resize(np.pad(a, ((0, h1 * 4 - h4), (0, w1 * 4 - w4))), (w1, h1), interpolation=cv2.INTER_AREA)
        c = c / np.maximum(a, 1e-4)[..., None]
        h, w = h4 / 4, w4 / 4
        sob = q["sob_px"]
        px, py = {"baixo": ((ax + bx) / 2, my1 - sob + h / 2), "cima": ((ax + bx) / 2, my0 + sob - h / 2),
                  "esq": (mx0 + sob - w / 2, (ay + by) / 2), "dir": (mx1 - sob + w / 2, (ay + by) / 2)}[lado]
        _pousar(out, c, a, px + (w1 - w) / 2, py + (h1 - h) / 2, Q.px_m, cobre=mesa_a)
    # a sombra curta do tampo sobre as cadeiras
    sb = cv2.GaussianBlur(cv2.warpAffine(mesa_a, np.float32([[1, 0, -d_], [0, 1, d_]]), mesa_a.shape[::-1]), (0, 0),
                          s["sig_m"] * Q.px_m) * s["forca"]
    alvo = np.clip(m * 2, 0, 1) * (1 - mesa_a)
    out *= (1 - sb * alvo)[..., None]
    print(f"    mesa de jantar do living: {len(cads)} cadeiras estofadas em linho com o quadro de madeira (a da mesa de 10 "
          f"lugares da biblioteca), de frente para a mesa, 1/3 sob o tampo")
    return np.clip(out, 0, 255).astype(np.uint8)


def moveis_td(Q, img):
    q = MOVEIS_TD
    out = img.copy()
    rng = np.random.default_rng(q["estofado"]["semente"])
    pecas = [d for d in Q.desenhos if d.get("layer") in F.CAMADAS_PECAS]
    # as mesas de madeira primeiro (a cor quente que já têm), depois os estofados
    mq = q["madeiras"]
    n_mad = 0
    madeiras = set()
    for d in pecas:
        r = d["rect"]
        if d["type"] in ("f", "fs") and any(_dentro_pt(r, z) for z in mq["zonas_pt"]) \
                and mq["lado_pt"][0] <= max(r.width, r.height) <= mq["lado_pt"][1]:
            x0, y0, x1, y1 = F.ret_q(Q, (r.x0, r.y0, r.x1, r.y1))
            c = np.median(out[y0 + 2:y1 - 2, x0 + 2:x1 - 2].reshape(-1, 3), axis=0) if (y1 - y0 > 6 and x1 - x0 > 6) \
                else None
            if c is not None and c[2] - c[0] > mq["quente"]:
                out = madeira_d(Q, out, d)
                madeiras.add(id(d))
                n_mad += 1
    # as peças de madeira ficam de fora dos estofados (a mesa de centro redonda do estar tem o lado das poltronas); a
    # madeira é o tom quente (R - B acima de `quente`: as mesas de 32 a 63, as poltronas de 18 a 22)
    n_est = 0
    for nome, z, (lmin, lmax), unir, *cmin in q["estofados"]:
        fills = [d for d in pecas if d["type"] in ("f", "fs") and _dentro_pt(d["rect"], z) and id(d) not in madeiras
                 and lmin <= max(d["rect"].width, d["rect"].height) <= lmax]
        grupos = [fills] if unir else [[d] for d in fills]
        cor = q["cor"]["cadeira" if "cadeira" in nome else "poltrona"]
        for g in grupos:
            rs = [d["rect"] for d in g]
            caixa = (min(r.x0 for r in rs), min(r.y0 for r in rs), max(r.x1 for r in rs), max(r.y1 for r in rs))
            tr = [d for d in pecas if d["type"] == "s" and _dentro_pt(d["rect"], caixa)
                  and max(d["rect"].width, d["rect"].height) >= (cmin[0] if cmin else q["costura_min_pt"])]
            vs = [d for d in pecas if d["type"] == "s" and _dentro_pt(d["rect"], caixa)
                  and max(d["rect"].width, d["rect"].height) >= max([q["estofado"]["vinco_min_pt"], *cmin])]
            out = estofado_d(Q, out, g, tr, cor, rng, concha=q.get("conchas", {}).get(nome), vincos=vs)
            n_est += 1
    print(f"    móveis: {n_est} estofados com volume e bouclé, sem os traços; {n_mad} mesas de madeira sem o contorno")
    out = almofadas_d(Q, out)
    piso = cv2.imread(str(F.ETAPAS / f"{Q.chave}_pisos.png"))
    out = cadeiras_mesas_d(Q, out, piso)
    out = jantar_d(Q, out, piso)
    out = sombra_jogos_d(Q, jogos_mesa_d(Q, out, piso))
    out = tapete_trama_d(Q, poltronas_modelo_e_d(Q, out))
    out = diagonais_armarios_d(Q, out)
    return floreiras_td(Q, out)


# As poltronas no modelo da sala íntima da Casa E (usuário, 28/10/26, com o recorte das duas poltronas embaixo do tapete
# do estar da varanda gourmet e o da poltrona da sala íntima do 1º Pavimento da Casa E: "preciso que as poltronas
# estejam no modelo da poltrona da casa e, da sala intima da casa E."; depois, com o das duas à esquerda do tapete do
# estar do living, junto à mesinha de madeira: "altere essas duas também para o modelo sugerido da poltrona da sala
# intima da casa E."): as 4 poltronas (no PDF, as peças da ARQ_LAYOUT HUMANIZAÇÃO em `pecas`, pt) saem e entra a
# concha de estofado creme recortada da final do 1º Pavimento da Casa E (`final3840_casae._modelo_poltrona_1p`), no
# centro e no maior lado da peça do PDF, com a abertura do assento virada para `frente` (para a mesa de centro na
# varanda, para o tapete no living), com a sombra e o contato das poltronas do Térreo da Casa E
# (`POLTRONAS_TE["sombra"]`, `["sombra_contato"]`).
# O buraco (a peça do PDF com `folga_px` e a sombra antiga para baixo e à esquerda, `sombra_px`; fora dele, a madeira da
# mesinha do living, R − B acima de `madeira_rb` na caixa `madeira_pt`) é refeito com o que estava em volta: o tapete (dentro do retângulo do
# PDF, `tapetes`, aquém da borda) e o piso de fora (o Bege Bahia na varanda, o travertino no living), cada um do seu, em
# ladrilhos de grão com o tom do anel (`final3840_casae._material_por_ladrilhos`); a borda escura de 1 px do tapete
# (`borda`: a linha "y" de baixo do tapete da varanda, a "x" da esquerda do do living) volta nos px dela, com a cor dos
# trechos limpos da mesma borda. Só os px livres (o material dentro de `tol_lum` da mediana dele e longe dos objetos)
# servem de fonte (o Bege Bahia é manchado: a tolerância é larga, e só as paredes e as peças ficam de fora; o tapete é
# liso: a tolerância é curta, sem a sombra da mesinha). No living,
# o travertino de fora do tapete vem da mesma linha, `fora_desloc` ao lado (os estratos são deitados).
# O entorno (usuário, 29/10/26, com o recorte das duas da varanda: "retoque o entorno das poltronas"): o tom do tapete no
# buraco vem só do tapete livre em desfoques crescentes (`_tom_em_escalas`; no miolo do buraco, longe do tapete livre, o
# ladrilho caía no px original, e a antiga ficava, com o contorno cinza saindo por baixo da nova); o Bege Bahia de fora,
# com `bege`, é o desenho do piso (`bege_desenho_d`, a mesma semente da biblioteca) na luz do Bege Bahia em volta, também
# em desfoques crescentes (no alto do buraco, junto ao tapete, o Bege Bahia livre fica longe).
POLTRONAS_E_D = {"pecas": [((1328.3, 1308.6, 1374.2, 1351.4), (0, -1)), ((1396.3, 1308.6, 1442.3, 1351.4), (0, -1)),
                           ((1687.7, 1268.4, 1735.5, 1311.4), (1, 0)), ((1687.7, 1353.4, 1735.5, 1396.5), (1, 0))],
                 "tapetes": [{"pt": (1272.6, 1154.9, 1499.3, 1324.9), "borda": ("y", 1324.9), "bege": True},
                             {"pt": (1713.6, 1235.1, 1997.1, 1433.5), "borda": ("x", 1713.6), "fora_desloc": (-40, 0)}],
                 "folga_px": 5, "sombra_px": 3, "madeira_rb": 25, "madeira_pt": [(1690.0, 1312.0, 1740.0, 1352.0)],
                 "tol_lum": {"tapete": 12, "piso": 45}, "esfuma_px": 2}


def _tom_em_escalas(out, buraco, livre, s0):
    """`out` com o `buraco` no tom do material `livre` em volta: a média só do livre, no desfoque de `s0` e, onde ele
    não alcança, nos de 2, 4, 8... vezes."""
    res = out.copy()
    ys, xs = np.nonzero(buraco)
    m_ = 160
    y0, y1 = max(ys.min() - m_, 0), min(ys.max() + m_ + 1, out.shape[0])
    x0, x1 = max(xs.min() - m_, 0), min(xs.max() + m_ + 1, out.shape[1])
    sub, falta = out[y0:y1, x0:x1], buraco[y0:y1, x0:x1].copy()
    lv = livre[y0:y1, x0:x1].astype(np.float32)
    r = res[y0:y1, x0:x1]
    s = float(s0)
    while falta.any() and s <= 64:
        p = cv2.GaussianBlur(lv, (0, 0), s)
        m = cv2.GaussianBlur(sub * lv[..., None], (0, 0), s)
        ok = falta & (p > 1e-3)
        r[ok] = m[ok] / p[ok][:, None]
        falta &= ~ok
        s *= 2
    return res


def poltronas_modelo_e_d(Q, img):
    import final3840_casae as E
    import retoque_terreo_casae as T
    q = POLTRONAS_E_D
    qe = E.POLTRONAS_TE
    H, W = img.shape[:2]
    out = img.astype(np.float32)
    L = out.mean(axis=2)
    # a madeira da mesinha do living (R − B acima de `madeira_rb`, só na caixa dela: o Bege Bahia também é quente)
    madeira = np.zeros((H, W), bool)
    for r in q["madeira_pt"]:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        madeira[y0:y1, x0:x1] = (out[y0:y1, x0:x1, 2] - out[y0:y1, x0:x1, 0]) > q["madeira_rb"]
    # os buracos: a peça do PDF com folga e a sombra antiga
    buraco = np.zeros((H, W), bool)
    k = 2 * q["folga_px"] + 1
    for r, _ in q["pecas"]:
        a = Q.preencher(lambda d, r=r: d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and _dentro_pt(d["rect"], r))
        m = cv2.dilate((a > 0.05).astype(np.uint8), np.ones((k, k), np.uint8))
        s = q["sombra_px"]
        m |= cv2.warpAffine(m, np.float32([[1, 0, -s], [0, 1, s]]), (W, H))
        buraco |= m.astype(bool)
    buraco &= ~cv2.dilate(madeira.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    proibido = cv2.dilate(buraco.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) | \
        cv2.dilate(madeira.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    fonte = out.copy()
    feito = np.zeros((H, W), bool)
    for tp in q["tapetes"]:
        x0, y0, x1, y1 = F.ret_q(Q, tp["pt"])
        eixo, v = tp["borda"]
        lx = int(round(Q.p2q(v, 0)[0])) if eixo == "x" else None
        ly = int(round(Q.p2q(0, v)[1])) if eixo == "y" else None
        zona = np.zeros((H, W), bool)
        zona[y0 - 60:y1 + 60, x0 - 60:x1 + 60] = True
        alvo = buraco & zona
        if not alvo.any():
            continue
        dentro = np.zeros((H, W), bool)
        dentro[y0:y1, x0:x1] = True
        linha = np.zeros((H, W), bool)
        if eixo == "y":
            linha[ly, x0:x1] = True
            dentro[ly:, :] = False
        else:
            linha[y0:y1, lx] = True
            dentro[:, :lx + 1] = False
        fora = ~dentro & ~linha
        for nome, mat in (("tapete", dentro), ("piso", fora)):
            parte = alvo & mat
            if not parte.any():
                continue
            if nome == "piso" and "fora_desloc" in tp:
                # o travertino em estratos deitados: a mesma linha, do lado (sem o grão em ladrilhos, que quebrava o veio)
                ox, oy = tp["fora_desloc"]
                ys, xs = np.nonzero(parte)
                fonte[ys, xs] = out[ys + oy, xs + ox]
                print(f"      poltronas no modelo da Casa E: {nome}, {int(parte.sum())} px da mesma linha, {ox} px ao lado")
                continue
            if nome == "piso" and tp.get("bege"):
                # o desenho do Bege Bahia (a semente da biblioteca) na luz do Bege Bahia em volta, longe do tapete
                ys, xs = np.nonzero(parte)
                cx0, cy0, cx1, cy1 = xs.min() - 30, ys.min() - 30, xs.max() + 31, ys.max() + 31
                fora_l = cv2.dilate((buraco | dentro | linha).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
                Dd, bege = bege_desenho_d(Q, (cx0, cy0, cx1, cy1))
                ok_l = (cv2.erode(bege[cy0:cy1, cx0:cx1].astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & \
                    ~fora_l[cy0:cy1, cx0:cx1]
                luz = _tom_em_escalas(out[cy0:cy1, cx0:cx1] / Dd, parte[cy0:cy1, cx0:cx1], ok_l,
                                      MOVEIS_TD["conjunto_varanda"]["luz_px"])
                fonte[ys, xs] = (luz * Dd)[ys - cy0, xs - cx0]
                print(f"      poltronas no modelo da Casa E: {nome}, {int(parte.sum())} px no desenho do Bege Bahia")
                continue
            limpo = mat & ~proibido & zona
            med = np.median(L[limpo])
            livre = limpo & (np.abs(L - med) < q["tol_lum"][nome])
            base = _tom_em_escalas(out, parte, livre, qe["tom_px"])
            novo = E._material_por_ladrilhos(base, parte, livre, qe, 50.0)
            fonte[parte] = novo[parte]
            print(f"      poltronas no modelo da Casa E: {nome}, {int(parte.sum())} px em ladrilhos ({int(livre.sum())} livres)")
        lin = alvo & linha
        ok = linha & ~proibido
        if lin.any() and ok.any():
            ys, xs = np.nonzero(ok)
            cores = out[ys, xs]
            yl, xl = np.nonzero(lin)
            fonte[yl, xl] = cores[np.arange(len(yl)) % len(cores)]
        feito |= alvo
    e = q["esfuma_px"]
    al = cv2.GaussianBlur(cv2.dilate(feito.astype(np.uint8), np.ones((2 * e + 1,) * 2, np.uint8)).astype(np.float32),
                          (0, 0), e / 2)
    al[feito] = 1
    out = out * (1 - al[..., None]) + fonte * al[..., None]
    # a concha da sala íntima da Casa E, no centro e no tamanho da peça, virada para a `frente`
    cor, a_m = E._modelo_poltrona_1p(qe)
    fx, fy = qe["modelo"]["frente"]
    for r, (dx, dy) in q["pecas"]:
        (ax, ay), (bx, by) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        cx, cy, t = (ax + bx) / 2, (ay + by) / 2, max(bx - ax, by - ay)
        ang = np.degrees(np.arctan2(dx, dy) - np.arctan2(fx, fy))
        c2, a2 = E._girar_peca(cor, a_m, t / max(a_m.shape), ang)
        T.pousar_planta(out, c2, a2, float(cx), float(cy), t, qe["sombra"])
        T.pousar_planta(out, c2, a2, float(cx), float(cy), t, qe["sombra_contato"])
    print(f"    {len(q['pecas'])} poltronas no modelo da sala íntima da Casa E (varanda gourmet e living)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# A trama do tapete do estar da varanda gourmet (usuário, 29/10/26, com o recorte do tapete: "traga textura para o
# tapete"): o relevo do tapete do bloco `conjunto_estar_tapete` da biblioteca (a lã mesclada em carreiras deitadas), só o
# relevo (o tom do trecho `trecho` dividido pelo desfoque de `sigma_px`: a luz da foto sai), na escala real (a foto tem
# `px_m_foto`), tecido sem repetição (o image quilting da biblioteca de texturas, retalhos de `p_px` e os espelhos, sem
# giros: as carreiras ficam deitadas, no comprido do tapete), com `forca` e limitado a ±`limite`, multiplicado só no
# tapete: dentro do retângulo do PDF (`tapetes_pt`) recuado `recuo_px` (a borda escura e a franja ficam), nos px da cor
# do tapete (croma a até `croma_tol` da mediana, luz até `claro_tol` acima dela: as sombras das peças entram, as peças
# não). O tom médio do tapete não muda. Depois (usuário, 29/10/26: "adicione textura ao tapete", com o recorte do estar do
# living, e "adicione textura aos tapetes das suites"): o do living e os das 4 suítes (o orgânico da master, os das camas
# da suíte 1 e da 2, o do estar da suíte 3/escritório); fora o da varanda, a cor do tapete é a mediana da faixa junto à
# borda (`anel_px` para dentro do recuo), porque a cama cobre o miolo.
TAPETE_TRAMA_D = {"tapetes_pt": [("varanda", (1272.6, 1154.9, 1499.3, 1324.9)),
                                  ("living", (1713.6, 1235.1, 1997.1, 1433.5)),
                                  ("suíte master", (610.3, 1519.2, 780.3, 1660.9)),
                                  ("suíte 1", (1094.8, 1672.6, 1208.2, 1814.3)),
                                  ("suíte 2", (1630.9, 1671.3, 1744.3, 1813.0)),
                                  ("suíte 3/escritório", (2069.4, 1523.3, 2239.5, 1636.7))],
                  "anel_px": 10, "recorte": "conjunto_estar_tapete",
                  "trecho": (4, 8, 138, 48), "px_m_foto": 317 / 3.1, "sigma_px": 4.0, "forca": 1.4, "limite": 0.06,
                  "p_px": 10, "semente": 29, "recuo_px": 3, "croma_tol": 6, "claro_tol": 8, "miolo": ("varanda",)}


def tapete_trama_d(Q, img, nomes=None, q=None):
    """`q`: a configuração (a da Casa D por padrão); `miolo`: os tapetes cuja cor é a mediana de todo o miolo (nos
    outros, a da faixa junto à borda)."""
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import texturas
    q = q or TAPETE_TRAMA_D
    foto = cv2.imread(str(RAIZ / "_blocos" / "recortes" / f"{q['recorte']}.png"))
    x0, y0, x1, y1 = q["trecho"]
    L = foto[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    rel = L / cv2.GaussianBlur(L, (0, 0), q["sigma_px"])
    e = Q.px_m / q["px_m_foto"]
    rel = cv2.resize(rel, None, fx=e, fy=e, interpolation=cv2.INTER_AREA)
    u8 = np.repeat(np.clip((rel - 1) * 510 + 128, 0, 255).astype(np.uint8)[..., None], 3, axis=2)
    out = img.astype(np.float32)
    for i, (nome, r) in enumerate(q["tapetes_pt"]):
        if nomes and nome not in nomes:
            continue
        X0, Y0, X1, Y1 = F.ret_q(Q, r)
        h, w = Y1 - Y0, X1 - X0
        tec = texturas.quilting(texturas.variantes(u8, True), h, w, p=q["p_px"], sobra=max(3, q["p_px"] // 3),
                                rng=np.random.default_rng(q["semente"] + i))[:h, :w]
        t = np.clip(q["forca"] * (tec[..., 0].astype(np.float32) - 128) / 510, -q["limite"], q["limite"])
        sub = out[Y0:Y1, X0:X1]
        Ls = sub.mean(axis=2)
        cr = sub - Ls[..., None]
        k = q["recuo_px"]
        ref = np.zeros((h, w), bool)
        ref[k:-k, k:-k] = True
        if nome not in q["miolo"]:
            n_ = k + q["anel_px"]
            ref[n_:-n_, n_:-n_] = False
        cm = np.median(cr[ref], axis=0)
        lm = np.median(Ls[ref])
        tap = (np.abs(cr - cm).max(axis=2) < q["croma_tol"]) & (Ls < lm + q["claro_tol"])
        # as peças: onde o que não é tapete se adensa (o bouclé tem pontos da cor do tapete)
        obj = cv2.GaussianBlur((~tap).astype(np.float32), (0, 0), 2) > 0.35
        obj = cv2.dilate(obj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        m = np.zeros((h, w), np.float32)
        m[k:-k, k:-k] = 1
        m *= ~obj
        m = cv2.GaussianBlur(m, (0, 0), 0.7) * m
        out[Y0:Y1, X0:X1] = sub * (1 + t * m)[..., None]
        print(f"    tapete {nome}: a trama do tapete do bloco {q['recorte']} na escala ({int(m.sum())} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# As almofadas do sofá do estar do living (usuário, 27/10/26, com o sofá anterior de volta: "deixe ao menos as almofadas
# em um tom sólido, sem linhas"; depois: "nas almofadas deixe evidente os contornos para que saibamos que existem uma na
# frente da outra", "pode ser até tom sobre tom para cada uma das almofadas. sendo uma mais escura atrás e outra mais
# clara na frente" e "traga um revestimento com textura pra dar efeito almofada de lã"): as 3 do PDF, cada uma em duas
# peças (a de trás, acima de `corte_pt`, e a da frente, em roundrects da ARQ_MOBILIÁRIO, em `caixa_pt`), cada peça
# preenchida por dentro dos contornos fechados dela (os traços abertos, como a linha do assento, saem na abertura de
# `abre_px`; os vincos de dentro somem), tom sobre tom (o tecido claro do sofá em volta, acima de `tecido_min`, a `tom`:
# a de trás mais escura, a da frente mais clara), com o contorno fino (`contorno`, da cor de cada uma) e a sombra curta e
# macia; a da frente por cima da de trás. O revestimento (`la`): o tricô da almofada cinza do `sofa_reto_boucle` da
# biblioteca (o recorte girado `giro` graus, para as carreiras ficarem deitadas, no comprido das almofadas), só o
# relevo dele (a luz da foto sai no desfoque de `sigma_px`), na escala real (a foto tem `px_m_foto`), tecido sem
# repetição (o image quilting da biblioteca de texturas), e o volume de almofada (`volume`: o miolo mais claro, as bordas mais fundas, até `raio_m` da borda)
ALMOFADAS_TD = {"caixa_pt": (1780.0, 1430.0, 1921.0, 1452.5), "corte_pt": (1442.0, 1440.5), "traco_px": 0.8,
                "abre_px": 1.5, "tom": {"tras": 0.84, "frente": 0.97}, "tecido_min": 170, "ss": 4,
                "contorno": {"px": 0.7, "tom": 0.72},
                "sombra": {"desloc_px": (-0.8, 0.8), "sigma_px": 1.0, "forca": 0.16},
                "la": {"recorte": "sofa_reto_boucle", "centro": (112, 102), "giro": 45, "lado_px": 20,
                       "px_m_foto": 126.25, "sigma_px": 3.0, "forca": 1.6, "semente": 64},
                "volume": {"forca": 0.10, "raio_m": 0.06}}


def _textura_la(Q, h, w, px_m):
    """O relevo do tricô (`ALMOFADAS_TD["la"]`) em volta de 1, em `px_m`, tecido em h x w pelo image quilting da
    biblioteca de texturas (retalhos da amostra e dos espelhos dela, sem os giros: as carreiras ficam deitadas)."""
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import texturas
    q = ALMOFADAS_TD["la"]
    im = cv2.imread(str(RAIZ / "_blocos" / "recortes" / f"{q['recorte']}.png"))
    gi = cv2.warpAffine(im, cv2.getRotationMatrix2D(q["centro"], q["giro"], 1.0), im.shape[1::-1],
                        flags=cv2.INTER_LINEAR)
    (cx, cy), r = q["centro"], q["lado_px"]
    L = gi[cy - r:cy + r, cx - r:cx + r].astype(np.float32).mean(axis=2)
    rel = L / np.maximum(cv2.GaussianBlur(L, (0, 0), q["sigma_px"]), 1)
    rel = 1 + q["forca"] * (rel - rel.mean())
    e = px_m / q["px_m_foto"]
    rel = cv2.resize(rel, None, fx=e, fy=e, interpolation=cv2.INTER_CUBIC)
    u8 = np.repeat(np.clip((rel - 1) * 255 + 128, 0, 255).astype(np.uint8)[..., None], 3, axis=2)
    p_ = int(min(40, rel.shape[0] // 3))
    tec = texturas.quilting(texturas.variantes(u8, True), h, w, p=p_, sobra=max(3, p_ // 4),
                            rng=np.random.default_rng(q["semente"]))[:h, :w]
    return 1 + (tec[..., 0].astype(np.float32) - 128) / 255


def almofadas_d(Q, img):
    from scipy import ndimage
    q, ss = ALMOFADAS_TD, ALMOFADAS_TD["ss"]
    tr = [d for d in Q.desenhos if d["type"] == "s" and d.get("layer") in F.CAMADAS_PECAS
          and _dentro_pt(d["rect"], q["caixa_pt"])]
    X0, Y0, X1, Y1 = _caixa_px(Q, [d["rect"] for d in tr])
    w, h = X1 - X0, Y1 - Y0
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(round(q["abre_px"] * ss)) + 1,) * 2)
    kc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(round(q["contorno"]["px"] * ss)) + 1,) * 2)
    la = _textura_la(Q, h * ss, w * ss, Q.px_m * ss)
    R = q["volume"]["raio_m"] * Q.px_m * ss

    def peca(ds):
        cheio = ndimage.binary_fill_holes(_mascara_pdf(Q, ds, X0, Y0, w, h, ss, traco_px=q["traco_px"]) > 0)
        cheio = cv2.morphologyEx(cheio.astype(np.uint8), cv2.MORPH_OPEN, k)
        borda = cheio - cv2.erode(cheio, kc)
        t = np.clip(cv2.distanceTransform(cheio, cv2.DIST_L2, 5) / R, 0, 1)
        relevo = la * (1 + q["volume"]["forca"] * (t - 0.5)) * cheio
        a, b = [cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA) for m in (cheio, borda)]
        rel = cv2.resize(relevo, (w, h), interpolation=cv2.INTER_AREA) / np.maximum(a, 1e-4)
        return a, b, rel
    tras = peca([d for d in tr if d["rect"].y1 <= q["corte_pt"][0]])
    frente = peca([d for d in tr if d["rect"].y0 >= q["corte_pt"][1]])
    out = img.copy()
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    uniao = np.maximum(tras[0], frente[0])
    anel = (cv2.dilate((uniao > 0.05).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0) & (uniao <= 0.05)
    tecido = np.median(reg[anel & (reg.mean(axis=2) > q["tecido_min"])], axis=0)
    s_ = q["sombra"]
    for (a, b, rel), t in ((tras, q["tom"]["tras"]), (frente, q["tom"]["frente"])):  # a de trás primeiro; a da frente
        cor = tecido * t                                                             # por cima
        sh = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, s_["desloc_px"][0]], [0, 1, s_["desloc_px"][1]]]),
                                             (w, h)), (0, 0), s_["sigma_px"]) * (1 - a) * s_["forca"]
        reg *= (1 - sh)[..., None]
        reg = reg * (1 - a[..., None]) + cor * rel[..., None] * a[..., None]
        reg = reg * (1 - b[..., None]) + cor * q["contorno"]["tom"] * b[..., None]
    out[Y0:Y1, X0:X1] = np.clip(reg, 0, 255).astype(np.uint8)
    n, _ = cv2.connectedComponents((uniao > 0.5).astype(np.uint8))
    print(f"    sofá do living: {n - 1} almofadas de lã (o tricô da biblioteca), tom sobre tom (a de trás mais escura, "
          f"a da frente mais clara), com o contorno fino")
    return out


def carros_d(Q, img, M):
    """Os 3 carros da R12 (prata, 4,70 x 1,85 m, alinhados), como `final3840_casab.carros`. O modelo (desde 27/10) é o
    carro do meio da final aprovada da Casa C: a silhueta é o que foge do tom do granito (neutro e claro, com os vidros
    de dentro), levada à medida da R12 em cada centro do PDF, com a borda limpa e a sombra curta."""
    from scipy import ndimage
    q = CARROS_D
    r = dict(AJ.CARROS_A["r12"], centros_pdf=q["centros_pdf"])
    fonte = cv2.imread(str(q["fonte"]))
    wx0, wy0, wx1, wy1 = q["janela_fonte"]
    reg = fonte[wy0:wy1, wx0:wx1].astype(np.float32)
    carro = (reg[..., 2] - reg[..., 0] < q["croma_max"]) & (reg.mean(axis=2) > q["lum_min"])
    m = cv2.morphologyEx(carro.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    sil = ndimage.binary_fill_holes(lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    sil = cv2.erode(sil.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    ys, xs = np.nonzero(sil)
    y0, y1 = ys.min(), ys.max() + 1
    comp = y1 - y0
    f0, f1 = r["faixa_largura"]
    larguras = sil[int(y0 + f0 * comp):int(y0 + f1 * comp)].sum(axis=1)
    larg = float(np.median(larguras[larguras > 0]))
    sx, sy = r["largura_m"] * Q.px_m / larg, r["comprimento_m"] * Q.px_m / comp
    cx, cy = float(xs.mean()), (y0 + y1) / 2
    alfa0 = cv2.GaussianBlur(sil.astype(np.float32), (0, 0), 0.6)
    out = img.astype(np.float32)
    for px_, py_ in r["centros_pdf"]:
        tx, ty = Q.p2q(px_, py_)
        Mw = np.float32([[sx, 0, tx - sx * cx], [0, sy, ty - sy * cy]])
        a = cv2.warpAffine(alfa0, Mw, (Q.W, Q.H), flags=cv2.INTER_LINEAR)
        c = cv2.warpAffine(reg, Mw, (Q.W, Q.H), flags=cv2.INTER_CUBIC)
        d_ = 0.08 * Q.px_m
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Q.W, Q.H)), (0, 0),
                              0.06 * Q.px_m) * (1 - a) * 0.38
        out *= (1 - sb)[..., None]
        out = out * (1 - a[..., None]) + c * a[..., None]
    print(f"    garagem (R12): {len(r['centros_pdf'])} carros prata de {r['comprimento_m']:.2f} x {r['largura_m']:.2f} m "
          f"(o modelo: o carro da final aprovada da Casa C, escala {sx:.2f} x {sy:.2f}), alinhados, com a sombra curta")
    return np.clip(out, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# Os brises de ripas em madeira (item 14, resposta 2)
def brises_pdf_d(Q):
    q = BRISES_D
    ds = []
    for d in Q.desenhos:
        r = d["rect"]
        if d.get("layer") == "ARQ_ELEMENTOS FIXOS" and d["type"] in ("f", "fs") and d.get("fill") \
                and min(d["fill"]) > 0.9 and max(r.width, r.height) < q["lado_max_pt"] \
                and any(c[0] <= r.x0 and r.x1 <= c[2] and c[1] <= r.y0 and r.y1 <= c[3] for c in q["caixas_pt"]):
            ds.append(d)
    return ds


def brises_madeira(Q, img):
    """Cada ripa do PDF (o preenchimento branco da ARQ_ELEMENTOS FIXOS, em 8x) na madeira da biblioteca, com o veio no
    sentido do comprimento dela, um tom levemente diferente por ripa, o contorno fino marrom-escuro e a sombra curta
    (para baixo e à esquerda). Entre as ripas fica o que está embaixo."""
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    q, ss = BRISES_D, 8
    s = q["sombra"]
    ds = brises_pdf_d(Q)
    rng = np.random.default_rng(q["semente"])
    out = img.astype(np.float32)
    for k, cx in enumerate(q["caixas_pt"]):
        dk = [d for d in ds if cx[0] <= d["rect"].x0 and d["rect"].x1 <= cx[2] and cx[1] <= d["rect"].y0
              and d["rect"].y1 <= cx[3]]
        if not dk:
            continue
        X0, Y0, X1, Y1 = F.ret_q(Q, cx)
        X0, Y0, X1, Y1 = X0 - 4, Y0 - 4, X1 + 5, Y1 + 5
        w, h = X1 - X0, Y1 - Y0
        tex = textura("madeira", Q.px_m, h, w, semente=q["semente"] + k).astype(np.float32) * q["madeira"]
        tex_v = cv2.rotate(textura("madeira", Q.px_m, w, h, semente=q["semente"] + 50 + k).astype(np.float32),
                           cv2.ROTATE_90_CLOCKWISE) * q["madeira"]

        def reduzir(x):
            return cv2.resize(x.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
        tudo = np.zeros((h * ss, w * ss), np.uint8)
        cor = np.zeros((h, w, 3), np.float32)
        acum = np.zeros((h, w), np.float32)
        for d in dk:
            m = np.zeros((h * ss, w * ss), np.uint8)
            polys = [np.round((c - (X0, Y0)) * ss).astype(np.int32) for c in Q.caminhos(d) if len(c) >= 3]
            cv2.fillPoly(m, polys, 255)
            tudo |= m
            a = reduzir(m / 255.0)
            r = d["rect"]
            em_pe = r.height > r.width
            t = (tex_v if em_pe else tex) * rng.uniform(*q["tons"])
            cor += t * a[..., None]
            acum += a
        a = np.clip(acum, 0, 1)
        cor = cor / np.maximum(acum, 1e-3)[..., None]
        mf = tudo.astype(np.float32) / 255
        d_ = s["dist_m"] * Q.px_m * ss
        sb = reduzir(cv2.GaussianBlur(cv2.warpAffine(mf, np.float32([[1, 0, -d_], [0, 1, d_]]), (w * ss, h * ss)),
                                      (0, 0), s["sig_m"] * Q.px_m * ss)) * s["forca"]
        reg = out[Y0:Y1, X0:X1]
        reg *= (1 - sb * (1 - a))[..., None]
        reg[:] = reg * (1 - a[..., None]) + cor * a[..., None]
        lt = max(1, int(round(q["contorno_px"] * ss)))
        anel = tudo & ~cv2.erode(tudo, np.ones((lt, lt), np.uint8))
        al = np.clip(reduzir(anel / 255.0) * 1.3, 0, 1)
        reg[:] = reg * (1 - al[..., None]) + np.float32(q["contorno"]) * al[..., None]
    print(f"    brises: {len(ds)} ripas do PDF em madeira, com o veio no comprimento, o contorno fino e a sombra curta")
    return np.clip(out, 0, 255).astype(np.uint8)


def paredes_d(Q, img):
    return brises_madeira(Q, F.paredes(Q, img))


# O revestimento de ripas em L da suíte master (usuário, 27/10/26: "esse revestimento em marrom em L e em volta das
# portas de vidro é contínuo. de uma parede a outra"): as ripas saem inteiras na etapa das paredes, mas a limpeza das
# esquadrias (o piso de junto do vidro espelhado) as apagava diante das portas de vidro, em cima e embaixo à esquerda.
# Nas caixas de `BRISES_DE_VOLTA_TD` (as de `BRISES_D`), as ripas do PDF voltam da imagem de antes das esquadrias
BRISES_DE_VOLTA_TD = [(463.2, 1476.9, 686.4, 1709.6)]
# A soleira entre a cozinha e a área de serviço (usuário, 27/10/26: "a soleira que divide a cozinha da área de serviço
# precisa ser melhor representada. ela é mais larga do que foi apresentado aqui"): o vão da parede no PDF (pt), na
# espessura inteira dela, entre as duas faces; a etapa das soleiras não o achava, e ficava um fio do render
SOLEIRAS_EXTRA_TD = [(1952.5, 699.8, 1961.0, 753.1)]


# A bancada da pia da cozinha (usuário, 27/10/26: "entre a cuba e a jardineira tem uma faixa branca que não deveria
# estar ali. o contorno da pia é em marrom granito igual a pia da direita. acima da pia esquerda tem esse item em branco
# que não existe"): a limpeza das esquadrias espelha a vizinhança da janela e trazia o branco da cuba da esquerda para a
# faixa entre a janela (579,2 pt) e a cuba (586 pt). O granito com a torneira volta da imagem de antes das esquadrias; as
# `espelho_px` linhas de cima (lá, o resto da janela antiga do render) recebem as de baixo, em espelho
BANCADAS_DE_VOLTA_TD = [{"pt": (1687.0, 579.2, 1733.6, 585.9), "espelho_px": 2}]


def pos_vidros_d(Q, img, antes):
    import final3840_casaa as FA
    out = img.copy()
    caixas = BRISES_DE_VOLTA_TD
    ripas = [d for d in brises_pdf_d(Q) if any(c[0] <= d["rect"].x0 and d["rect"].x1 <= c[2] and c[1] <= d["rect"].y0
                                                and d["rect"].y1 <= c[3] for c in caixas)]
    ids = {id(d) for d in ripas}
    m = Q.preencher(lambda d: id(d) in ids, fs=True) > 0.02
    n = int((m & (np.abs(out.astype(np.int16) - antes.astype(np.int16)).max(axis=2) > 0)).sum())
    out[m] = antes[m]
    for r in SOLEIRAS_EXTRA_TD:
        out = FA.soleira_bege(Q, out, r)
    for b in BANCADAS_DE_VOLTA_TD:
        (u0, v0), (u1, v1) = Q.p2q(*b["pt"][:2]), Q.p2q(*b["pt"][2:])
        x0, x1, y0, y1, k = int(np.floor(u0)), int(np.ceil(u1)), int(np.ceil(v0)), int(np.floor(v1)), b["espelho_px"]
        out[y0 + k:y1, x0:x1] = antes[y0 + k:y1, x0:x1]
        out[y0:y0 + k, x0:x1] = antes[y0 + k:y0 + 2 * k, x0:x1][::-1]
    print(f"    suíte master: as ripas em L de volta diante das portas de vidro ({len(ripas)} ripas, {n} px); "
          f"{len(SOLEIRAS_EXTRA_TD)} soleira de Bege Bahia no vão inteiro (cozinha e área de serviço)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# A auditoria de 26/10 no Térreo (mapa `renders/POE642_CasaD_PH_Terreo_auditoria_2610_v2.jpg`; usuário, 27/10/26: "Aprovo
# a lista e sigamos no item 9 com a recomendação"), com as rotinas do Térreo aprovado da Casa C:
# 1. as paredes e os muros do lote em cinza 80 (E10) e, depois das esquadrias, a parede de volta onde a limpeza delas a
#    cortou (`pos_esquadrias_d`). Sem a limpeza dos vãos escuros da Casa C (`C.janelas_s`): aqui ela só pegava as faixas
#    brancas da ARQ_PAREDE dentro das ilhas (em granito escuro, uma linha branca de ponta a ponta) e na borda do jardim da
#    sala íntima. Os trilhos das cortinas param nas paredes do PDF (`F.cortinas(paredes_pdf=True)`, como na Casa B):
#    sem o preto, o da janela da suíte master descia pelo closet até o muro;
# 2. o travertino em estratos do Térreo da Casa C (`C.travertino_estratos`) no living/jantar, no hall e no lavabo, e o
#    mesmo desenho nas bancadas e cubas de travertino (`C.travertino_bruto_tc`, como na Casa C);
# 3. a seta da entrada principal (E4), no piso do hall de entrada, apontando para a porta pivotante (`SETA_TD`);
# 4. a escada de 16 degraus sem as linhas e sem o triângulo (E3, E8): os degraus em Bege Bahia com o sombreamento de
#    descida (o 16, junto ao terraço, o mais claro; `C.sombras_degraus`) e o D do PDF no degrau 16;
# 5. os blocos em cascata sem o bocel e sem o triângulo, com a sombra curta de cada bloco sobre o de baixo
#    (`F.degraus_blocos`, como na Casa B) e o D no meio do bloco de cima (o último pintado do PDF, junto ao deck; no lugar
#    do triângulo ele ficava na borda, metade no deck);
# 6. os guarda-roupas com cabides (E2; `elementos.guarda_roupa`, como os closets das Casas B e C): o armário do DCE, o da
#    suíte 3/escritório e o módulo ao lado do banho master (os retângulos com a diagonal da DOC_LINHAS);
# 7. os boxes de correr dos banhos 1, 2 e 3 e do WC DCE em vidro contínuo, com as faces finas e a sombra curta, desde
#    28/10 fechados, de parede a parede, sem o trilho tracejado (`final3840_casaa.boxes`); as folhas do PDF, pareadas por box (`AJ.folhas_box` juntava as dos três banhos, que estão
#    na mesma linha); antes, a faixa tracejada da base sai, refeita com o piso logo acima;
# 8-9. as bancadas com a borda e a sombra curta (E9) e os materiais do Térreo aprovado da Casa C (pergunta 9,
#    recomendação aceita): o lavabo com a bancada e a cuba esculpida em granito marrom e o vaso marrom; o banho master e
#    os banhos 1, 2 e 3 com a bancada e a cuba esculpida em travertino bruto e o vaso branco; o banho gourmet com a
#    bancada em granito marrom escurecido e a cuba branca (o WC DCE tem só a cuba, de parede: branca); a ilha e as
#    bancadas da cozinha e da gourmet em granito marrom no tom do piso, escurecido (86%), como nas Casas B e C.
#    Depois, vendo a final (usuário, 27/10/26: "Banho gourmet: sanitário marrom, bancada da pia e Cuba esculpida no
#    mármore travertino bruto"): o banho gourmet como os banhos, com a bancada e a cuba esculpida em travertino bruto, e
#    o vaso marrom, como o do lavabo;
# 10. os chuveiros na placa cromada com os furinhos, o braço até a parede e a canopla (`final3840_casaa.chuveiro`): banho
#    master (2), banhos 1, 2 e 3, WC DCE, banho gourmet e a ducha do deck; as placas e os braços do PDF ficam fora das peças;
# 11. os X tracejados (GARAGEM, ÁREA DESCOBERTA, JARDIM do lavabo) abrem embaixo dos rótulos (E7), como na Casa C:
#    os rótulos saem duas vezes, a segunda sobre o fundo sem o tracejado embaixo dos textos (`rotulos_terreo_d`);
# 12. o rótulo do WC DCE TÉRREO parte do piso livre entre a cuba, o vaso e a porta (E7); os arcos das portas do PDF,
#    que a final não desenha (R3), saem dos obstáculos dos rótulos, como no Subsolo (`rotulos_sub_d`): o do WC DCE
#    fechava o piso livre e devolvia o rótulo para dentro do box (desde 27/10, a pedido, ele vai para o box, como no
#    PDF, com o corpo menor: `ROTULOS_TD["fixos"]`);
# 13. a cama do DCE com a roupa de cama da biblioteca, como no DCE 1 do Subsolo (`cama_dce_d`);
# 14. o banco do estar da varanda gourmet (o retângulo de cantos redondos da DOC_LINHAS E PROJEÇÕES, 0,60 x 1,80 m), em
#    madeira, sem encosto, como o da varanda da Casa E: a madeira da mesa da suíte 3/escritório (o veio no comprido; a
#    textura do piso de madeira trazia as juntas das réguas e o banco saía xadrez), um pouco mais escura, em 4 ripas;
# 15. a prateleira de vinhos da adega na parede do fundo (a da direita), como na Casa C (`C.adega_c`).
# Depois, vendo a final (usuário, 27/10/26: "Lavabo: bancada e Cuba esculpida no mármore travertino bruto, sanitário
# marrom"; "Banhos suítes: piso quartzo aura, bancada e pia esculpida no quartzo aura e sanitário branco"): o lavabo com a
# bancada e a cuba esculpida em travertino bruto (o vaso já era marrom); o banho master e os banhos 1, 2 e 3 com o piso,
# a bancada e a cuba esculpida no quartzito Aura da biblioteca (a chapa do quadro de referências de 19/10, no tom entre o
# branco e o cinza dos banhos do 1º Pavimento da Casa E; `QUARTZITO_TD`, `CHAPAS_D`), o vaso branco como já era.
MATERIAIS_TD = {"granito": [],
                "travertino": [(2320.0, 1370.0, 2362.0, 1492.0),                # o lavabo (pedido de 27/10)
                               (1360.0, 640.0, 1500.0, 673.0)],                 # o banho gourmet (pedido de 27/10)
                "quartzito": [(628.0, 1705.0, 766.0, 1750.0), (910.0, 1694.0, 954.0, 1770.0),
                              (1885.0, 1694.0, 1971.0, 1770.0)],                # banho master, banhos 1, 2 e 3
                "granito_escuro": [(1200.0, 675.0, 1430.0, 727.0), (1255.0, 804.0, 1458.0, 881.0),
                                   (1598.0, 575.0, 1818.0, 620.0),
                                   (1660.0, 680.0, 1806.0, 750.0),                # gourmet e cozinha, bancada e ilha
                                   (2050.0, 565.0, 2220.0, 625.0)],               # área de serviço, a dos tanques
                # (usuário, 27/10/26, na bancada dos tanques: "altere o tom da bancada para o marrom granito")
                "cubas_brancas": [(2150.0, 759.9, 2166.6, 783.2)],                                  # a do WC DCE
                # o pontilhado do granito que o PDF desenha na bancada do banho gourmet (466 pontos da ARQ_BANCADAS):
                # o contorno do PDF o redesenhava, e no travertino eram poros escuros densos; sai
                "sem_pontilhado": [(1360.0, 640.0, 1500.0, 673.0)]}
VASOS_TD = [((2216.1, 1454.1, 2245.2, 1474.1), "marrom"),                                           # o do lavabo
            ((1272.3, 640.8, 1292.3, 669.9), "marrom")]                                # o do banho gourmet (27/10)
# os chuveiros: a placa (ducha) e o braço do PDF; a canopla, na ponta do braço junto à parede
CHUVEIROS_TD = [("banho master, à esquerda", (630.7, 1849.0, 641.9, 1860.2), (615.1, 1853.9, 637.5, 1855.3)),
                ("banho master, à direita", (686.9, 1849.2, 698.1, 1860.4), (691.3, 1854.1, 713.7, 1855.5)),
                ("banho 1", (931.2, 1845.8, 942.4, 1857.0), (915.6, 1850.7, 938.0, 1852.1)),
                ("banho 2", (1896.7, 1845.8, 1907.9, 1857.0), (1901.2, 1850.7, 1923.5, 1852.1)),
                ("banho 3", (1948.9, 1846.1, 1960.1, 1857.3), (1933.3, 1851.0, 1955.6, 1852.4)),
                ("WC DCE", (2202.8, 836.7, 2214.0, 847.9), (2207.3, 841.6, 2229.6, 843.1)),
                ("banho gourmet", (1219.3, 642.5, 1230.5, 653.7), (1224.2, 647.0, 1225.6, 669.3)),
                ("ducha do deck", (1159.7, 659.3, 1170.9, 670.5), (1164.2, 664.2, 1186.5, 665.7))]
# os boxes de correr: as duas folhas do PDF de cada um, o meio e o trilho no vão (pt)
BOXES_TD = [{"nome": "banho 1", "hor": True, "meio": 1821.6, "trilho": [(980.9, 1016.5)],
             "folhas": [(915.6, 1820.9, 968.0, 1821.4), (928.5, 1821.7, 980.9, 1822.3)]},
            {"nome": "banho 2", "hor": True, "meio": 1821.9, "trilho": [(1822.6, 1858.3)],
             "folhas": [(1858.3, 1821.2, 1910.7, 1821.7), (1871.1, 1822.0, 1923.5, 1822.6)]},
            {"nome": "banho 3", "hor": True, "meio": 1821.6, "trilho": [(1998.5, 2034.1)],
             "folhas": [(1933.3, 1820.9, 1985.6, 1821.4), (1946.1, 1821.7, 1998.5, 1822.3)]},
            {"nome": "WC DCE", "hor": True, "meio": 818.1, "trilho": [(2145.2, 2174.5)],
             "folhas": [(2174.5, 817.4, 2218.9, 817.9), (2185.8, 818.2, 2230.2, 818.8)]}]
BOX_FAIXA_TD = {"meia_pt": 2.4, "sobe_px": 7}
GUARDA_ROUPAS_TD = {"ss": 4, "semente": 61, "pecas": [("DCE", (2238.8, 834.4, 2295.5, 868.4), "cima"),
                                                      ("suíte 3/escritório", (1932.6, 1577.0, 1966.6, 1690.4), "direita"),
                                                      ("ao lado do banho master", (872.5, 1710.3, 906.5, 1880.3), "esquerda"),
                                                      # usuário, 27/10/26: "armário à esquerda com cabides." (o do outro
                                                      # lado do corredor, aberto para ele)
                                                      ("à esquerda do corredor do banho master",
                                                       (787.4, 1806.6, 821.5, 1880.3), "direita")]}
BANCO_VARANDA_TD = {"pt": (1263.0, 1196.9, 1297.0, 1298.9), "raio_pt": 5.7, "ripas": 4, "madeira": 0.80,
                    "fonte_pt": (2125.0, 1705.0, 2166.0, 1811.0),       # o tampo da mesa da suíte 3/escritório
                    "junta": (70, 92, 118), "larg_junta": 0.35, "forca_junta": 0.45, "contorno": (60, 72, 88),
                    "larg_contorno": 0.45, "sombra": {"dist_m": 0.05, "sig_m": 0.035, "forca": 0.32}, "ss": 4}
ADEGA_TD = dict(C.ADEGA_C, pt=(2241.6, 987.4, 2258.6, 1083.8), modulos=2)
ESCADA_DESCIDA_TD = {"d_pt": (957.0, 1449.5),                # o meio do degrau 16 (o D do PDF, na ponta do degrau)
                     "d_blocos_pt": (588.7, 1108.0)}          # o meio do bloco de cima da cascata (574,2 a 603,2 pt)
SETA_TD = {"ponta": (2462, 1068)}
ROTULOS_TD = {"pontos": {}, "folga_px": 4,
              # o WC DCE dentro do box, como no PDF, com o corpo menor (usuário, 27/10/26: "o rótulo aqui está sobre a
              # porta. preciso que coloque dentro do box como está no pdf, com fonte mais reduzida"); antes, a busca
              # partia de (2195, 790) pt, no piso seco, e o rótulo caía junto da porta
              "fixos": {"WC DCE TÉRREO": {"corpo": 0.62, "quebra": ["WC DCE", "TÉRREO"]},
                        # a adega (usuário, 27/10/26, com a adega em U: "centralize o rótulo"): no meio do piso livre,
                        # entre o vidro (2121 pt) e a prateleira do fundo, e entre as prateleiras de cima e de baixo
                        "ADEGA": {"pt": (2181.3, 1035.6)},
                        # a despensa (usuário, 27/10/26: "corrija a posição do rótulo, de forma que não fique sobre o
                        # armário. centralize no piso"): entre a folha da porta aberta (1879 pt) e o armário em L
                        # (1934,1 pt), e entre a parede de cima (763,5 pt) e o armário de baixo (847,3 pt)
                        "DESPENSA": {"pt": (1906.5, 805.4)}},
              # em branco (usuário, 27/10/26, no DCE TÉRREO: "rótulo em branco"), qualquer que seja o fundo
              "brancos": ("DCE TÉRREO",)}
# o piso dos banhos das suítes em quartzito Aura (pedido de 27/10): o Bege Bahia da legenda (a mancha de cada banho, a
# partir do rótulo do PDF) com a luz larga do render e o desenho da chapa, no tom dela
QUARTZITO_TD = {"banhos": ("BANHO MASTER", "BANHO 1", "BANHO 2", "BANHO 3"), "chapa": "quartzito_aura",
                "tom": (211, 215, 221), "contraste": 1.0, "sig_m": 1.5, "semente": 731, "busca_px": 24}
# as chapas da biblioteca nas bancadas e cubas (`F.bancadas`, `F.cuba_esculpida`): o quartzito Aura dos banhos das
# suítes (a bancada no tom do piso, marcada pela borda E9; a cuba um pouco mais clara, polida) e o Bege Bahia da cuba do
# vestiário do Subsolo (pedido de 27/10: "Vestiário: mármore bege Bahia no piso e Cuba esculpida, bancada da pia no
# granito marrom, sanitário branco")
CHAPAS_D = {"quartzito": {"chapa": "quartzito_aura", "tom": (211, 215, 221), "contraste": 0.8}}
# O travertino bruto das bancadas e das cubas esculpidas (lavabo e banho gourmet; usuário, 27/10/26: "Melhore o aspecto
# do travertino bruto"): o desenho em estratos da Casa C (`C.travertino_estratos`) saía calmo demais e num tom rosado,
# quase de madeira clara. Agora no creme da foto da biblioteca (`_texturas/originais/travertino.webp`, RGB ~228, 221,
# 204), um pouco mais escuro na bancada que na cuba; os veios mais marcados e no comprido da peça (na bancada em pé do
# lavabo, na vertical); os poros abertos (o "bruto") mais numerosos e mais escuros. Só na Casa D.
TRAVERTINO_BRUTO_D = {"base": 1.0, "amp": 1.5, "finas": 1.0, "poros": 1.6, "poro_esc": 1.85,
                      "tom_bancada": (186, 204, 216), "tom_cuba": (200, 217, 228)}                      # BGR
CUBAS_CHAPA_D = {
    "cuba_quartzito": dict(F.BANCADAS_F["cuba_travertino"], chapa="quartzito_aura", contraste=0.6,
                           tom=(218, 222, 227), contorno=(150, 156, 164), contorno_bacia=(162, 168, 176)),
    "cuba_bege": dict(F.BANCADAS_F["cuba_travertino"], chapa="bege_bahia", contraste=0.6, tom=(194, 216, 234),
                      contorno=(140, 160, 182), contorno_bacia=(152, 172, 192))}


def travertino_bruto_d(Q, h, w, semente, veio, faixa, poros, poro_esc, forca=1.6):
    """No lugar de `final3840_casaa.travertino_bruto` (as bancadas e as cubas): o desenho de `TRAVERTINO_BRUTO_D`, sem o
    tom, com o veio no comprido da peça."""
    q = TRAVERTINO_BRUTO_D
    em_pe = h > w
    hh, ww = (w, h) if em_pe else (h, w)
    D = C.travertino_estratos(Q, hh, ww, semente, base=forca * q["base"], poros=poros * q["poros"],
                              poro_esc=poro_esc * q["poro_esc"], amp=q["amp"], finas=q["finas"], quente=False)
    return np.ascontiguousarray(D.T) if em_pe else D


def quartzito_banhos_d(Q, img, antes):
    """O piso dos banhos das suítes em quartzito Aura: na mancha de Bege Bahia de cada banho (a que tem o rótulo do PDF;
    a mesma máscara dos pisos, sem as paredes), a luz larga do render (`antes`, a entrada dos pisos) com o desenho da
    chapa, no tom dela."""
    q = QUARTZITO_TD
    arcos, _ = F.arcos_porta(Q)
    preto = Q.cor([(17, 17, 17), (0, 0, 0)], tol=20) & ~arcos
    bege = F.fechar(Q.cor([(232, 232, 232)], tol=6), 5) & ~preto
    _, lab = cv2.connectedComponents(bege.astype(np.uint8), connectivity=4)
    m = np.zeros_like(bege)
    r = q["busca_px"]
    for nome, _, (px, py), _ in B.rotulos_casab(Q.pg, Q.p2q2000):
        if nome in q["banhos"]:
            cx, cy = (int(round(v)) for v in Q.p2q(px, py))
            jan = lab[cy - r:cy + r, cx - r:cx + r]
            ids, n = np.unique(jan[jan > 0], return_counts=True)
            m |= lab == ids[np.argmax(n)]
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    L = F.luz_robusta(antes, m, q["sig_m"] * Q.px_m)
    L = L / np.median(L[m], axis=0)
    D = F._chapa_luz(Q, q, y1 - y0, x1 - x0, q["semente"])
    novo = img.astype(np.float32).copy()
    novo[y0:y1, x0:x1] = L[y0:y1, x0:x1] * np.float32(q["tom"]) * D[..., None]
    print(f"    banhos das suítes: o piso em quartzito Aura ({int(m.sum())} px, {len(q['banhos'])} banhos)")
    return np.clip(F.pousar(img.astype(np.float32), novo, m, suave=0.5), 0, 255).astype(np.uint8)


# O tracejado sob a ilha gourmet (usuário, 27/10/26: "tem tracejados embaixo da ilha. precisamos removê-los"): na borda
# de baixo do granito do gourmet, da esquerda da ilha até a parede do living, o render tem um tracejado cinza (não há
# linha no PDF ali); a etapa dos pisos o guarda (a borda fica fora da legenda). Na faixa (`pt`; a 1ª linha, a última
# do granito): a 2ª linha vai para o granito de cima onde o px está mais perto dele que do Bege Bahia de baixo
# (`ref_px` abaixo); as outras, ao Bege Bahia de baixo onde estão mais escuras que ele (`escuro`)
TRACEJADO_ILHA_TD = {"pt": (1208.3, 875.95, 1579.8, 881.6), "ref_px": 5, "escuro": 15}


def sem_tracejado_ilha_d(Q, img):
    q = TRACEJADO_ILHA_TD
    x0, y0, x1, y1 = F.ret_q(Q, q["pt"])
    out = img.copy()
    g = out[y0, x0:x1].astype(np.int16)
    b = out[y0 + q["ref_px"], x0:x1].astype(np.int16)
    p = out[y0 + 1, x0:x1].astype(np.int16)
    gr = np.abs(p - g).sum(axis=1) < np.abs(p - b).sum(axis=1)
    out[y0 + 1, x0:x1][gr] = out[y0, x0:x1][gr]
    n = int(gr.sum())
    for y in range(y0 + 2, y1):
        p = out[y, x0:x1].astype(np.int16)
        esc = p.mean(axis=1) < b.mean(axis=1) - q["escuro"]
        out[y, x0:x1][esc] = out[y0 + q["ref_px"], x0:x1][esc]
        n += int(esc.sum())
    print(f"    gourmet: o tracejado do render sob a ilha sai ({n} px da borda ao granito e ao Bege Bahia)")
    return out


def piso_estratos_d(Q, img, m, nome, forca, sig_m, semente, **kw):
    if nome == "travertino" and kw.get("bruto") == "estratos":
        return C.piso_textura_c(Q, img, m, nome, forca, sig_m, semente, **kw)
    return piso_textura_d(Q, img, m, nome, forca, sig_m, semente, **kw)


def _dentro_td(r, zonas):
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    return any(z[0] <= cx <= z[2] and z[1] <= cy <= z[3] for z in zonas)


def bancadas_terreo_d(Q, img):
    """As bancadas com a borda e a sombra (E9) e os materiais pedidos, peça a peça; as cubas esculpidas (travertino no
    lavabo e no banho gourmet, quartzito Aura nos banhos das suítes) no lugar da louça; a branca (WC DCE), de parede,
    por cima da pedra."""
    import final3840_casaa as FA
    mt = MATERIAIS_TD
    brancas = [tuple(round(v, 1) for v in r) for r in mt["cubas_brancas"]]
    cubas = [c for c in cubas_bancada_d(Q) if tuple(round(v, 1) for v in c) not in brancas]
    gs = {k: [(Q.p2q(*z[:2]), Q.p2q(*z[2:])) for z in mt[k]]
          for k in ("granito", "travertino", "granito_escuro", "quartzito")}

    def pedra(Q_, comp):
        ys, xs = np.nonzero(comp)
        cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
        for k in ("granito", "granito_escuro", "travertino", "quartzito"):
            if any(a[0] <= cx <= b[0] and a[1] <= cy <= b[1] for a, b in gs[k]):
                return k
        return None

    def cuba(Q_, out, r):
        return F.cuba_esculpida(Q_, out, r, next((k for k in ("granito", "quartzito") if _dentro_td(r, mt[k])),
                                                 "travertino"))
    guarda = F.cubas_bancada
    F.cubas_bancada = lambda Q_: cubas
    todos = Q.desenhos
    Q._desenhos = [d for d in todos if not (d.get("layer") == "ARQ_BANCADAS" and d["type"] == "s"
                                            and d["rect"].width < 0.6 and d["rect"].height < 0.6
                                            and _dentro_td(tuple(d["rect"]), mt["sem_pontilhado"]))]
    try:
        out = C.bancadas_c(Q, img, borda=F.BANCADAS_F["borda_e9"], pedra=pedra, cuba=cuba)
    finally:
        F.cubas_bancada = guarda
        Q._desenhos = todos
    out = np.ascontiguousarray(np.clip(out, 0, 255).astype(np.uint8))
    for r in mt["cubas_brancas"]:
        out = FA.cuba_branca(Q, out, r)
    print(f"    bancadas: lavabo e banho gourmet em travertino bruto com a cuba esculpida em travertino; banho master e "
          f"banhos 1, 2 e 3 em quartzito Aura com a cuba esculpida em quartzito; gourmet e cozinha em granito marrom "
          f"escurecido; {len(mt['cubas_brancas'])} cuba branca (WC DCE)")
    return out


def chuveiros_td():
    """Os chuveiros como `final3840_casaa.chuveiro` os pede: a placa, o braço e a canopla na ponta do braço que fica
    longe da placa (a da parede)."""
    out = []
    for nome, ducha, braco in CHUVEIROS_TD:
        cx, cy = (ducha[0] + ducha[2]) / 2, (ducha[1] + ducha[3]) / 2
        x0, y0, x1, y1 = braco
        if x1 - x0 >= y1 - y0:
            xw = x0 if abs(cx - x0) > abs(cx - x1) else x1
            canopla = (min(xw, xw + (1.3 if xw == x0 else -1.3)), y0 - 0.7, max(xw, xw + (1.3 if xw == x0 else -1.3)),
                       y1 + 0.7)
        else:
            yw = y0 if abs(cy - y0) > abs(cy - y1) else y1
            canopla = (x0 - 0.7, min(yw, yw + (1.3 if yw == y0 else -1.3)), x1 + 0.7,
                       max(yw, yw + (1.3 if yw == y0 else -1.3)))
        out.append({"nome": nome, "ducha": ducha, "braco": braco, "canopla": canopla})
    return out


def chuveiros_terreo_d(Q, img):
    import final3840_casaa as FA
    out = np.ascontiguousarray(img.copy())
    for c in chuveiros_td():
        out = FA.chuveiro(Q, out, c)
    print(f"    {len(CHUVEIROS_TD)} chuveiros na placa cromada com os furinhos, o braço até a parede e a canopla")
    return out


# O box do banho gourmet (usuário, 27/10/26: "marca com um tom claro esse box do banho gourmet"): no PDF, o vidro fixo
# entre o chuveiro e o vaso (as duas linhas tracejadas da ARQ_LOUÇAS E METAIS, 1252,3 a 1255,1 pt, de parede a parede),
# que `F.boxes_granito` não achava; no render, um traço cinza-escuro. O traço sai (o granito de `desvio_px` ao lado) e
# entra o vidro claro, com as faces finas
# Depois, o fechamento (usuário, 27/10/26: "faz o fechamento do box"): desde a parede de cima (579,8 pt; antes começava
# em 603,3 pt e ficava um vão de uns 0,4 m)
BOX_GOURMET_TD = {"pt": (1252.3, 579.8, 1255.1, 669.4), "cor": (222, 226, 228), "face": (150, 154, 158),
                  "face_forca": 0.55, "limpa_px": 3, "desvio_px": 9}


def box_gourmet_d(Q, img):
    import final3840_casaa as FA
    q = BOX_GOURMET_TD
    out = img.copy()
    x0, y0, x1, y1 = F.ret_q(Q, q["pt"])
    a0, a1 = x0 - q["limpa_px"], x1 + q["limpa_px"]
    out[y0:y1, a0:a1] = out[y0:y1, a0 + q["desvio_px"]:a1 + q["desvio_px"]]
    o = out.astype(np.float32)
    a = FA.ret_aa(Q, q["pt"])[..., None]
    o = o * (1 - a) + np.float32(q["cor"]) * a
    e = 0.45 / FA.PT_PX
    for f in ((q["pt"][0], q["pt"][1], q["pt"][0] + e, q["pt"][3]), (q["pt"][2] - e, q["pt"][1], q["pt"][2], q["pt"][3])):
        af = FA.ret_aa(Q, f)[..., None] * q["face_forca"]
        o = o * (1 - af) + np.float32(q["face"]) * af
    print("    banho gourmet: o box de vidro em tom claro, no lugar do traço cinza-escuro do render")
    return np.clip(o, 0, 255).astype(np.uint8)


# 28/10 (usuário, no WC DCE: "corrija a existência de uma segunda porta, atrás da principal. remova essa porta que está
# atrás"): a limpeza das esquadrias (`F.esquadrias_terreo`) leva ao piso a folha antiga do render espelhando o que está
# em volta, e logo abaixo da folha aberta da porta do WC DCE fica o vidro do box: o espelho punha uma cópia dele, uma
# segunda folha, a 5 px da porta. Entre a face de baixo da folha do PDF (`folha_pt`) e a linha do box (`box_pt`), o piso
# volta ao de antes das esquadrias; a primeira linha logo abaixo da folha, que antes ainda era a folha antiga do render,
# vem da seguinte. Depois ("remova esse tracejado na ponta da porta"): as colunas das duas pontas da folha entram
# também; ficavam em claro e escuro alternados, como um tracejado. Na da ponta junto à parede (`parede`), o piso da
# coluna ao lado, como a face da parede abaixo do box (a de antes das esquadrias tinha um traço escuro de 2 px).
ENTRE_PORTA_BOX_TD = [{"x_pt": (2190.6, 2229.6), "folha_pt": 810.3, "box_pt": 818.1, "parede": "direita"}]


def entre_porta_box_td(Q, img, antes):
    out = img.copy()
    for q in ENTRE_PORTA_BOX_TD:
        (x0, y0), (x1, y1) = Q.p2q(q["x_pt"][0], q["folha_pt"]), Q.p2q(q["x_pt"][1], q["box_pt"])
        a, b = int(np.floor(x0)), int(np.ceil(x1))                  # com as colunas das duas pontas da folha
        r0, r1 = int(np.ceil(y0)), int(np.floor(y1 - 1.5))           # da folha até antes da face do vidro do box
        out[r0 + 1:r1, a:b] = antes[r0 + 1:r1, a:b]
        out[r0, a:b] = antes[r0 + 1, a:b]
        if q["parede"] == "direita":
            out[r0:r1, b - 1] = out[r0:r1, b - 2]
        else:
            out[r0:r1, a] = out[r0:r1, a + 1]
    print(f"    WC DCE: sem a cópia do vidro do box entre a folha da porta e o box ({len(ENTRE_PORTA_BOX_TD)} faixa)")
    return out


# 28/10 (usuário, com o recorte da porta da circulação para a sala íntima: "tem uma segunda porta colada na parede em
# tom cinza que precisa ser removida"): no vão dessa porta, o render deixou a folha fechada (uma faixa clara de ponta a
# ponta) e a etapa das soleiras desenhou por cima a soleira de Bege Bahia com as faces cinza (o vão é branco no PDF),
# que se lê como uma segunda folha, fechada, junto à aberta. Os dois lados são vinílico: o vão, entre os batentes
# (`vao_pt`), recebe o vinílico dos dois lados, cada metade espelhada do seu lado e as duas fundidas no meio (as réguas
# são deitadas); nas linhas da folha aberta (`folha_y_pt`, com folga), só o lado de lá, para a folha não entrar no vão.
# A folha e os batentes ficam. A soleira saía 1,2 px à esquerda do vão do PDF (vem do vão branco da base de 2000 px),
# com a face da esquerda em 1438 e 1439: o vão cresce 2 px para a esquerda (`alarga_px`), para a face sair junto.
VAO_SEM_SOLEIRA_TD = [{"vao_pt": (1246.6, 1509.2, 1255.2, 1561.4), "folha_y_pt": (1559.8, 1562.1), "lado": "direita",
                       "folga_px": 2, "alarga_px": (2, 0)}]
# Revisão de 28/10/26, item 6 (OK do usuário): no Subsolo, a porta do WC DCE para o DCE 1, o mesmo caso, entre dois
# granitos. Ali a soleira ia de ponta a ponta do vão (sem os batentes) e a face da direita era um traço escuro (a coluna
# 930): o vão inteiro do PDF recebe o granito dos dois lados (1 px mais largo à direita) e os batentes do PDF voltam
# (`batentes`, como os das portas de vidro: claros com o contorno fino). Nas linhas da folha aberta do WC DCE, à
# esquerda e em cima, só o granito do DCE 1; e, na final, o rótulo do WC DCE encosta no vão pela esquerda: o vão todo
# vem só do lado do DCE 1 (`so_lado`).
VAO_SEM_SOLEIRA_SD = [{"vao_pt": (753.4, 1235.5, 761.9, 1275.1), "folha_y_pt": (1237.6, 1239.9), "lado": "direita",
                       "folga_px": 2, "alarga_px": (0, 1), "so_lado": True,
                       "batentes": [(753.4, 1235.5, 759.9, 1238.3), (759.9, 1235.5, 761.9, 1236.9),
                                    (753.4, 1272.3, 759.9, 1275.1), (759.9, 1273.7, 761.9, 1275.1)]}]


def vao_sem_soleira_td(Q, img):
    import final3840_casaa as FA
    out = img.astype(np.float32)
    vaos = VAO_SEM_SOLEIRA_TD if Q.chave == "Terreo" else VAO_SEM_SOLEIRA_SD
    for q in vaos:
        x0, y0, x1, y1 = F.ret_q(Q, q["vao_pt"])
        x0, x1 = x0 - q["alarga_px"][0], x1 + q["alarga_px"][1]
        w = x1 - x0
        esq = out[y0:y1, x0 - w:x0][:, ::-1]                      # o lado esquerdo, espelhado na face do vão
        dir_ = out[y0:y1, x1:x1 + w][:, ::-1]                     # o lado direito, espelhado na outra face
        p = ((np.arange(w, dtype=np.float32) + 0.5) / w)[None, :, None]
        if q["lado"] == "esquerda":
            p = 1 - p
            esq, dir_ = dir_, esq
        novo = esq * (1 - p) + dir_ * p
        f0 = int(np.floor(Q.p2q(0, q["folha_y_pt"][0])[1])) - q["folga_px"]
        f1 = int(np.ceil(Q.p2q(0, q["folha_y_pt"][1])[1])) + q["folga_px"]
        lin = np.arange(y0, y1)
        na_folha = (lin >= f0) & (lin < f1)
        novo[na_folha] = dir_[na_folha]
        if q.get("so_lado"):
            novo = dir_
        a = FA.ret_aa(Q, q["vao_pt"])[y0:y1].max(axis=1)[:, None, None]          # só a cobertura das linhas
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + novo * a
    out = np.clip(out, 0, 255).astype(np.uint8)
    batentes = [b for q in vaos for b in q.get("batentes", [])]
    if batentes:
        pv = FA.PORTAS_VIDRO
        FA.PORTAS_VIDRO = dict(pv, portas=[{"nome": "batentes do vão sem soleira", "batentes": batentes, "folhas": [],
                                            "montante_pt": 0.6}])
        try:
            out = FA.portas_vidro(Q, out)
        finally:
            FA.PORTAS_VIDRO = pv
    print(f"    vão sem soleira: o piso dos dois lados no vão ({len(vaos)} porta)")
    return out


# Revisão de 28/10/26, itens 4 e 5 (OK do usuário): na suíte master e na porta da sala íntima para a circulação da suíte
# 2, um traço escuro de 1 px ao longo da folha aberta, entre ela e a parede (um resto da folha antiga do render que a
# limpeza das esquadrias deixava, uma "segunda folha"). Nas faixas `rets` (pt), o piso volta ao de antes das esquadrias
# (a etapa das soleiras, onde o vinílico já estava limpo).
RESTOS_FOLHA_TD = {"rets": [(891.0, 1502.7, 944.0, 1505.4), (1559.5, 1560.6, 1612.0, 1563.3)]}


def restos_folha_td(Q, img, antes):
    out = img.copy()
    for r in RESTOS_FOLHA_TD["rets"]:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        out[y0:y1, x0:x1] = antes[y0:y1, x0:x1]
    print(f"    sem o traço escuro junto à folha aberta ({len(RESTOS_FOLHA_TD['rets'])} portas)")
    return out


# Revisão de 28/10/26, itens 2 e 3 (OK do usuário), no hall, na porta ao lado da adega:
# - a folha é de vidro no PDF (o contorno de 2268,6 a 2270,9 pt com a linha do meio), aberta junto à parede da adega, e
#   saía num fio pontilhado cinza-azulado; agora como as portas de vidro do living (`final3840_casaa.portas_vidro`: o
#   caixilho de alumínio, o vidro no meio, os montantes e a sombra curta), depois de o fio sair (`limpa_pt`: o
#   travertino do lado, espelhado);
# - as duas linhas tracejadas da laje (1081,0 e 1092,3 pt) começam no PDF junto à folha (2267,1 pt) e atravessam o hall;
#   na final, só a partir da grama (2366,3 pt). Os traços do próprio PDF (ARQ_PAREDE) até a borda da grama (`ate_x_pt`)
#   entram em preto nítido (fundo claro, a regra de 28/10), por baixo da folha; o branco na grama fica como estava.
HALL_PORTA_TD = {"limpa_pt": (2267.1, 987.4, 2272.6, 1082.9),
                 "porta": {"nome": "de vidro do hall, junto à adega", "batentes": [],
                           "folhas": [((2268.6, 987.4, 2270.9, 1082.9), "y")], "montante_pt": 0.6},
                 "linhas_y_pt": (1081.0, 1092.3), "de_x_pt": 2267.0, "ate_x_pt": 2366.3,
                 "cor": (30, 30, 30), "larg_px": 1.5, "ss": 8}


def _tracos_d(Q, img, segs, cor, larg_px, ss=8):
    """Os traços (pt) por cima, nítidos e com antialias, numa cor só."""
    out = img.astype(np.float32)
    for x0, y0, x1, y1 in segs:
        (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
        bx0, by0 = int(min(u0, u1)) - 3, int(min(v0, v1)) - 3
        bx1, by1 = int(max(u0, u1)) + 4, int(max(v0, v1)) + 4
        m = np.zeros(((by1 - by0) * ss, (bx1 - bx0) * ss), np.uint8)
        cv2.line(m, (int(round((u0 - bx0) * ss)), int(round((v0 - by0) * ss))),
                 (int(round((u1 - bx0) * ss)), int(round((v1 - by0) * ss))), 255,
                 max(1, int(round(larg_px * ss))), cv2.LINE_AA)
        a = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)[..., None]
        out[by0:by1, bx0:bx1] = out[by0:by1, bx0:bx1] * (1 - a) + np.float32(cor) * a
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def hall_porta_td(Q, img):
    import final3840_casaa as FA
    q = HALL_PORTA_TD
    out = img.copy()
    x0, y0, x1, y1 = F.ret_q(Q, q["limpa_pt"])
    x0 += 1                                                   # a face da parede da adega fica
    w = x1 - x0
    out[y0:y1, x0:x1] = out[y0:y1, x1:x1 + w][:, ::-1]           # o travertino de junto, espelhado (estratos deitados)
    segs = []
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            a, b = it[1], it[2]
            if abs(a.y - b.y) < 0.05 and any(abs(a.y - y) < 0.05 for y in q["linhas_y_pt"]) and \
                    q["de_x_pt"] <= min(a.x, b.x) and max(a.x, b.x) <= q["ate_x_pt"] and abs(a.x - b.x) < 8:
                segs.append((a.x, a.y, b.x, b.y))
    out = _tracos_d(Q, out, segs, q["cor"], q["larg_px"], q["ss"])
    pv = FA.PORTAS_VIDRO
    FA.PORTAS_VIDRO = dict(pv, portas=[q["porta"]])
    try:
        out = FA.portas_vidro(Q, out)
    finally:
        FA.PORTAS_VIDRO = pv
    print(f"    hall: a folha de vidro da porta junto à adega e {len(segs)} traços da laje em preto no travertino")
    return out


def boxes_terreo_d(Q, img):
    """O box do banho gourmet (no granito) na faixa cinza-clara, como estava (`F.boxes_granito`); os de correr dos
    banhos 1, 2 e 3 e do WC DCE em vidro contínuo (`final3840_casaa.boxes`), com as folhas pareadas por box. Antes, a
    faixa tracejada da base, ao longo de cada box, recebe o piso logo acima."""
    import final3840_casaa as FA
    out = box_gourmet_d(Q, F.boxes_granito(Q, img)).copy()
    q = BOX_FAIXA_TD
    for b in BOXES_TD:
        xs = [f[0] for f in b["folhas"]] + [f[2] for f in b["folhas"]] + [t for tr in b["trilho"] for t in tr]
        x0, y0, x1, y1 = F.ret_q(Q, (min(xs), b["meio"] - q["meia_pt"], max(xs), b["meio"] + q["meia_pt"]))
        d = q["sobe_px"]
        out[y0:y1, x0:x1] = out[y0 - d:y1 - d, x0:x1]
    folhas = AJ.folhas_box
    AJ.folhas_box = lambda pg: [dict(b) for b in BOXES_TD]
    try:
        return FA.boxes(Q, np.ascontiguousarray(out))
    finally:
        AJ.folhas_box = folhas


def biblioteca_terreo_d(Q, img):
    """As peças da biblioteca (cooktops, banquetas) e as da auditoria de 26/10: os guarda-roupas com cabides, o banco
    da varanda gourmet e a prateleira de vinhos da adega."""
    out = biblioteca_d(Q, img)
    guarda = B.GUARDA_ROUPAS_B
    B.GUARDA_ROUPAS_B = GUARDA_ROUPAS_TD
    try:
        with F.em_quadro(Q):
            out = B.guarda_roupas_terreo(out)
    finally:
        B.GUARDA_ROUPAS_B = guarda
    out = banco_varanda_d(Q, out)
    ga = C.ADEGA_C
    C.ADEGA_C = ADEGA_TD
    try:
        out = C.adega_c(Q, out)
    finally:
        C.ADEGA_C = ga
    return out


# A adega em U (usuário, 27/10/26: "faz a adega em u"): além da prateleira do fundo (`ADEGA_TD`, a parede da direita),
# as das paredes de cima e de baixo, do mesmo fundo (0,30 m), da prateleira do fundo até perto das folhas de vidro da
# esquerda (`lados`: (onde fica a parede, retângulo pt)); a mesma rotina da Casa C (`C.adega_c`, que põe o gargalo na
# parede da direita), na imagem girada para a parede de cada uma ficar à direita
ADEGA_U_TD = {"lados": [("cima", (2130.0, 987.4, 2241.6, 1004.4)), ("baixo", (2130.0, 1066.8, 2241.6, 1083.8))],
              "modulos": 2}


class _QGirado:
    """O quadro visto na imagem girada (`cima`: 90° no sentido horário; `baixo`: no anti-horário), para as rotinas que
    só pedem `p2q` e `px_m`."""

    def __init__(self, Q, lado, H, W):
        self.Q, self.lado, self.H, self.W, self.px_m = Q, lado, H, W, Q.px_m

    def p2q(self, x, y):
        u, v = self.Q.p2q(x, y)
        return ((self.H - 1) - v, u) if self.lado == "cima" else (v, (self.W - 1) - u)


def adega_u_d(Q, img):
    q = ADEGA_U_TD
    out = img
    ga = C.ADEGA_C
    try:
        for lado, (x0, y0, x1, y1) in q["lados"]:
            H, W = out.shape[:2]
            if lado == "cima":                                      # a parede de cima fica à direita
                gir, pt = np.ascontiguousarray(np.rot90(out, -1)), (x0, y1, x1, y0)
            else:                                                   # a de baixo
                gir, pt = np.ascontiguousarray(np.rot90(out, 1)), (x1, y0, x0, y1)
            C.ADEGA_C = dict(ADEGA_TD, pt=pt, modulos=q["modulos"])
            gir = C.adega_c(_QGirado(Q, lado, H, W), gir)
            out = np.ascontiguousarray(np.rot90(gir, 1 if lado == "cima" else -1))
    finally:
        C.ADEGA_C = ga
    print("    adega: em U, com as prateleiras das paredes de cima e de baixo")
    return out


def banco_varanda_d(Q, img):
    """O banco do estar da varanda gourmet, sem encosto, em madeira (como o da varanda da Casa E): o retângulo de
    cantos redondos do PDF, as ripas no comprido (com o veio da mesa da suíte 3/escritório, já na imagem), as juntas,
    o contorno fino e a sombra curta."""
    q, k = BANCO_VARANDA_TD, BANCO_VARANDA_TD["ss"]
    (u0, v0), (u1, v1) = Q.p2q(*q["pt"][:2]), Q.p2q(*q["pt"][2:])
    X0, Y0, X1, Y1 = int(u0) - 6, int(v0) - 6, int(np.ceil(u1)) + 7, int(np.ceil(v1)) + 7
    w, h = X1 - X0, Y1 - Y0
    rr = q["raio_pt"] * (u1 - u0) / (q["pt"][2] - q["pt"][0])
    m = np.zeros((h * k, w * k), np.uint8)
    a_, b_, c_, d_ = (u0 - X0) * k, (v0 - Y0) * k, (u1 - X0) * k, (v1 - Y0) * k
    r_ = rr * k
    cv2.rectangle(m, (int(a_ + r_), int(b_)), (int(c_ - r_), int(d_)), 255, -1)
    cv2.rectangle(m, (int(a_), int(b_ + r_)), (int(c_), int(d_ - r_)), 255, -1)
    for cx, cy in ((a_ + r_, b_ + r_), (c_ - r_, b_ + r_), (a_ + r_, d_ - r_), (c_ - r_, d_ - r_)):
        cv2.circle(m, (int(cx), int(cy)), int(r_), 255, -1, cv2.LINE_AA)
    mf = m.astype(np.float32) / 255

    def reduzir(x):
        return cv2.resize(x.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    a = reduzir(mf)
    s = q["sombra"]
    dd = s["dist_m"] * Q.px_m * k
    sb = reduzir(cv2.GaussianBlur(cv2.warpAffine(mf, np.float32([[1, 0, -dd], [0, 1, dd]]), (w * k, h * k)), (0, 0),
                                  s["sig_m"] * Q.px_m * k)) * s["forca"]
    fx0, fy0, fx1, fy1 = F.ret_q(Q, q["fonte_pt"])
    tex = cv2.resize(img[fy0:fy1, fx0:fx1].astype(np.float32), (w, h), interpolation=cv2.INTER_AREA) * q["madeira"]
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    reg *= (1 - sb * (1 - a))[..., None]
    reg[:] = reg * (1 - a[..., None]) + tex[:h, :w] * a[..., None]
    from retoque_terreo_casae import linha_aa
    n = q["ripas"]
    for i in range(1, n):
        x = (u0 - X0) + i * (u1 - u0) / n
        al = linha_aa((h, w), [(x, v0 - Y0 + 0.5), (x, v1 - Y0 - 0.5)], q["larg_junta"])[..., None] * \
            q["forca_junta"] * a[..., None]
        reg[:] = reg * (1 - al) + np.float32(q["junta"]) * al
    anel = m & ~cv2.erode(m, np.ones((max(1, int(round(q["larg_contorno"] * k))),) * 2, np.uint8))
    al = np.clip(reduzir(anel / 255.0) * 1.3, 0, 1)[..., None]
    reg[:] = reg * (1 - al) + np.float32(q["contorno"]) * al
    print(f"    varanda gourmet: o banco de madeira sem encosto ({(u1 - u0) / Q.px_m:.2f} x {(v1 - v0) / Q.px_m:.2f} m), "
          f"em {n} ripas, com a sombra curta")
    return np.clip(out, 0, 255).astype(np.uint8)


def escadas_terreo_d(Q, img):
    """A escada de 16 degraus sem as linhas e sem o triângulo, com o sombreamento de descida e o D do PDF no degrau 16;
    os blocos em cascata sem o bocel, com a sombra de cada um sobre o de baixo e o D no lugar do triângulo."""
    s = F.ESCADA_SOMBRA
    ex0, ey0, ex1, ey1 = ESCADA_T["pdf"]
    x0, y0, x1, y1 = F.ret_q(Q, (ex0 - 8, ey0, ex1, ey1))
    X, Y = C.grade_pt(Q, x0, y0, x1, y1)
    bordas = [ex0] + list(ESCADA_T["bocels"]) + [ex1]
    k = np.searchsorted(bordas, X).astype(np.int32)
    n = len(bordas)
    f = C.sombras_degraus(k, n, s)
    bege = F.fechar(Q.cor([(232, 232, 232)], tol=6), 5)[y0:y1, x0:x1] & (Y >= ey0) & (Y <= ey1) & (X <= ex1)
    out = img.copy()
    reg = out[y0:y1, x0:x1].astype(np.float32)
    reg = np.where(bege[..., None], reg * f[..., None], reg)
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    out = F.letra(Q, out, "D", Q.p2q(*ESCADA_DESCIDA_TD["d_pt"]))
    print("    escada de 16 degraus: sem linhas e sem triângulo, com o sombreamento de descida; o D no degrau 16")
    bf = F.BLOCOS_F
    F.BLOCOS_F = dict(bf, triangulos_pt=[])                   # o D vai no meio do bloco de cima, não na borda
    try:
        out = F.degraus_blocos(Q, out, linhas=False, letra_="D")
    finally:
        F.BLOCOS_F = bf
    print("    o D no meio do bloco de cima da cascata")
    return F.letra(Q, out, "D", Q.p2q(*ESCADA_DESCIDA_TD["d_blocos_pt"]))


def projecoes_terreo_d(Q, img, so_pisos=False):
    """As projeções do PDF em tracejado (item 15 de 22/10), como desde 25/10 (antes na etapa das escadas). `so_pisos`:
    só as dos pisos claros (os dois X do banho master), para refazê-las sobre a final."""
    out = np.ascontiguousarray(img.copy())
    with F.em_quadro(Q):
        pa = AJ.PROJECOES_A
        n = 0
        grupos = ((PROJECOES_D, PROJECOES_TRACO_D["pisos"], "DOC_LINHAS E PROJEÇÕES"),
                  (PROJECOES_CLARAS_D, PROJECOES_TRACO_D["claras"], "DOC_LINHAS E PROJEÇÕES"),
                  (COBERTURA_D, PROJECOES_TRACO_D["claras"], "ARQ_ELEMENTOS FIXOS"))
        try:
            for zonas, t, camada in grupos[:1] if so_pisos else grupos:
                AJ.PROJECOES_A = dict(pa, larg_px=pa["larg_px"] * Q.W / 2000 * t["larg"], cor=t["cor"],
                                      forca=t["forca"])
                out, k = B.linhas_pdf(out, "Terreo", zonas, camada)
                n += k
        finally:
            AJ.PROJECOES_A = pa
    print(f"    projeções do PDF em tracejado ({n} traços): os X do banho master, da área descoberta e do jardim do "
          f"lavabo")
    return out


# As projeções da laje sobre a garagem e a faixa de grama abaixo dela (pedidos de 27/10: na garagem, "melhorar a
# representação dessas projeções em branco"; no gramado, "faltou a representação correta dessas projeções"), como no
# PDF: os 9 vãos da laje com o X tracejado nas diagonais; no gramado, o contorno de cada vão (a EST_LAJE, que no PDF só
# aparece sobre o branco) e a borda da laje à esquerda em traço fino contínuo, e as duas linhas tracejadas de baixo (a
# partir da grama); na garagem, as duas linhas tracejadas de cima (o tracejado escuro do render sai antes), a de baixo
# e as bordas da direita (até o brise) e da esquerda (abaixo do gás). O tracejado regular de `C._tracejado` (começa e
# termina num traço inteiro), mais curto e fino que o de antes, em branco quente; nada sobre as paredes. A linha de cima
# (559,4 pt) vai até onde o PDF a desenha (usuário, 27/10/26: "esse pontilhado branco se estende até depois do banho
# gourmet"): os 209 traços da ARQ_PAREDE de 1147,3 a 2298,8 pt, por cima da grama e das floreiras; antes, desde a
# ponta da floreira (2214 pt). A limpeza do escuro do render fica no granito
PROJ_LAJES_TD = {
    "vaos_x": [(2420.1, 2459.9), (2471.2, 2510.9), (2522.2, 2561.9), (2573.3, 2612.9), (2624.3, 2664.0),
               (2675.3, 2715.0), (2726.3, 2766.0), (2777.4, 2817.0), (2828.4, 2868.1)],
    "garagem": {"y": (570.7, 661.4), "contorno": False,
                "tracejadas": [((1147.3, 559.4), (2910.6, 559.4)), ((2383.3, 570.7), (2899.3, 570.7)),
                               # o fechamento na ponta esquerda (usuário, 27/10/26: "faltou o fechamento da projeção em
                               # tracejado branco"): as duas linhas de pé da ARQ_PAREDE e a de dentro até a parede
                               # depois (usuário, 27/10/26: "dentro da área do bege bahia não tem tracejado. ele
                               # termina logo acima, no encontro com o piso bege bahia"): no PDF, o piso do deck cobre
                               # o resto das linhas de pé; a de fora vai só até a borda dele e a de dentro sai
                               ((1147.3, 559.4), (1147.3, 570.7)), ((1158.6, 570.7), (1195.6, 570.7)),
                               ((2383.3, 662.0), (2899.3, 662.0)), ((2899.3, 570.7), (2899.3, 662.0)),
                               ((2910.6, 559.4), (2910.6, 662.0)), ((2383.3, 627.4), (2383.3, 662.0))],
                "finas": [], "limpar": [((2214.0, 2910.6), 559.4), ((2383.3, 2899.3), 570.7)]},
    "grama": {"y": (995.9, 1081.0), "contorno": True,
              "tracejadas": [((2366.3, 1081.0), (2899.3, 1081.0)), ((2366.3, 1092.3), (2910.6, 1092.3))],
              "finas": [((2383.3, 987.4), (2383.3, 1081.0))], "limpar": []},
    # a laje da lateral direita da sala íntima, junto ao brise (usuário, 27/10/26: "vamos melhorar a representação da
    # projeção tracejada em branco. tem a laje aqui em cinza claro"): a faixa de laje (o cinza claro, da parede à borda
    # de 2284,3 pt) fica; o retângulo tracejado da ARQ_PAREDE além dela (2284,3 a 2295,6 pt, de 1497,7 a 1894,5),
    # que o render desenhava em preto sobre a grama, sai (`limpar_v`: (y0, y1), x) e entra em branco; sem os X dos vãos
    "lateral": {"vaos": False, "contorno": False,
                "tracejadas": [((2284.3, 1497.7), (2284.3, 1894.5)), ((2295.6, 1497.7), (2295.6, 1894.5)),
                               ((2284.3, 1497.7), (2295.6, 1497.7)), ((2284.3, 1894.5), (2295.6, 1894.5))],
                "finas": [], "limpar": [], "limpar_v": [((1497.7, 1894.5), 2284.3), ((1497.7, 1894.5), 2295.6)]},
    "traco_m": 0.10, "vao_m": 0.05, "larg_px": 1.1, "fino_px": 0.7, "cor": (228, 233, 236), "forca": 0.92,
    "fino_forca": 0.75, "parede_tol": 10, "limpeza": {"meia_px": 2, "desvio_px": 6, "escuro": 14}, "ss": 4}


ZONAS_LAJE_TD = ("garagem", "grama", "lateral")
def projecoes_lajes_td(Q, img):
    from scipy import ndimage
    q = PROJ_LAJES_TD
    out = img.copy()
    parede = np.abs(out.astype(np.int16) - 80).max(axis=2) <= q["parede_tol"]
    parede = cv2.dilate(parede.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    # o tracejado escuro do render ao longo das linhas de cima da garagem: cada px da faixa mais escuro que o granito
    # logo acima e logo abaixo (a mediana ao longo da linha) volta a ser o granito de `desvio_px` acima
    lq = q["limpeza"]
    h, d = lq["meia_px"], lq["desvio_px"]
    n_limpo = 0
    for nome in ZONAS_LAJE_TD:
        for (xa, xb), y in q[nome]["limpar"]:
            (x0, yq), (x1, _) = Q.p2q(xa, y), Q.p2q(xb, y)
            x0, x1, yi = int(np.floor(x0)), int(np.ceil(x1)), int(round(yq))
            faixa = out[yi - h:yi + h + 1, x0:x1]
            viz = np.concatenate([out[yi - d - h:yi - d + h + 1, x0:x1], out[yi + d - h:yi + d + h + 1, x0:x1]])
            ref = ndimage.median_filter(np.median(viz.mean(axis=2), axis=0), size=15)
            esc = faixa.mean(axis=2) < ref[None, :] - lq["escuro"]
            esc = cv2.dilate(esc.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & \
                ~parede[yi - h:yi + h + 1, x0:x1]
            faixa[esc] = out[yi - d - h:yi - d + h + 1, x0:x1][esc]
            n_limpo += int(esc.sum())
        # as linhas de pé: o mesmo, de lado (o escuro volta ao que está `desvio_px` à direita, a grama)
        for (ya, yb), x in q[nome].get("limpar_v", []):
            (xq, y0), (_, y1) = Q.p2q(x, ya), Q.p2q(x, yb)
            y0, y1, xi = int(np.floor(y0)), int(np.ceil(y1)), int(round(xq))
            faixa = out[y0:y1, xi - h:xi + h + 1]
            viz = np.concatenate([out[y0:y1, xi - d - h:xi - d + h + 1], out[y0:y1, xi + d - h:xi + d + h + 1]], axis=1)
            ref = ndimage.median_filter(np.median(viz.mean(axis=2), axis=1), size=15)
            esc = faixa.mean(axis=2) < ref[:, None] - lq["escuro"]
            esc = cv2.dilate(esc.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & \
                ~parede[y0:y1, xi - h:xi + h + 1]
            faixa[esc] = out[y0:y1, xi + d - h:xi + d + h + 1][esc]
            n_limpo += int(esc.sum())
    ss = q["ss"]
    tr, va = q["traco_m"] * Q.px_m, q["vao_m"] * Q.px_m
    linhas_tr, linhas_fi = [], []
    for nome in ZONAS_LAJE_TD:
        z = q[nome]
        y0, y1 = z.get("y", (0, 0))
        for xa, xb in (q["vaos_x"] if z.get("vaos", True) else []):
            linhas_tr += [((xa, y0), (xb, y1)), ((xb, y0), (xa, y1))]
            if z["contorno"]:
                linhas_fi += [((xa, y0), (xb, y0)), ((xa, y0), (xa, y1)), ((xb, y0), (xb, y1))]
        linhas_tr += z["tracejadas"]
        linhas_fi += z["finas"]
    pts = np.array([Q.p2q(*p) for ln in linhas_tr + linhas_fi for p in ln])
    X0, Y0 = (np.floor(pts.min(axis=0)) - 6).astype(int)
    X1, Y1 = (np.ceil(pts.max(axis=0)) + 7).astype(int)
    m_tr = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    m_fi = np.zeros_like(m_tr)
    for a, b in linhas_tr:
        C._tracejado(m_tr, np.subtract(Q.p2q(*a), (X0, Y0)), np.subtract(Q.p2q(*b), (X0, Y0)), tr, va, q["larg_px"], ss)
    for a, b in linhas_fi:
        pa, pb = (tuple(int(round(v * ss)) for v in np.subtract(Q.p2q(*p), (X0, Y0))) for p in (a, b))
        cv2.line(m_fi, pa, pb, 255, max(1, int(round(q["fino_px"] * ss))), cv2.LINE_AA)

    def reduzir(m):
        return cv2.resize(m.astype(np.float32) / 255.0, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    a = np.maximum(reduzir(m_tr) * q["forca"], reduzir(m_fi) * q["fino_forca"])
    a[parede[Y0:Y1, X0:X1]] = 0
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    cor = np.float32(q["cor"])
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - a[..., None]) + cor * a[..., None], 0, 255).astype(np.uint8)
    print(f"    projeções da laje: {n_limpo} px do tracejado escuro do render saem; os X dos 9 vãos na garagem e no "
          f"gramado, o contorno fino dos vãos no gramado e {sum(len(q[k]['tracejadas']) for k in ZONAS_LAJE_TD)} "
          f"linhas tracejadas da laje (garagem, gramado e a lateral da sala íntima), em branco")
    return out


# As portas de vidro (pedidos de 27/10): entre o living e a varanda ("corrija a representação dessas portas de vidro") e
# entre a cozinha e o living ("representar a soleira e a porta de correr adequadamente"), como as portas de vidro da
# Casa A (`final3840_casaa.portas_vidro`): a soleira de Bege Bahia no vão do PDF (R13), os batentes em branco e cada
# folha no plano dela no PDF, com o caixilho de alumínio, o vidro e a sombra curta. No living, as 4 folhas em dois
# planos (as das pontas por fora); na cozinha, a folha de correr por fora do vão, junto à parede (no PDF, sem batentes:
# a parede encosta na soleira)
PORTAS_VIDRO_TD = [
    {"nome": "do living para a varanda", "soleira": (1589.1, 876.9, 1597.6, 1367.3),
     "batentes": [(1589.1, 876.9, 1597.6, 879.1), (1589.1, 1365.0, 1597.6, 1367.3)],
     "folhas": [((1595.3, 882.0, 1597.6, 997.8), "y"), ((1593.0, 1003.4, 1595.3, 1119.2), "y"),
                ((1593.0, 1124.9, 1595.3, 1240.7), "y"), ((1595.3, 1246.4, 1597.6, 1362.2), "y")],
     "montante_pt": 0.6},
    {"nome": "de correr da cozinha para o living", "soleira": (1757.2, 868.4, 1861.6, 876.9), "batentes": [],
     "folhas": [((1744.2, 865.8, 1851.9, 868.1), "x")], "montante_pt": 0.6},
    # a de correr da suíte 2 para o beiral (usuário, 27/10/26: "abaixo da porta de vidro à direita tem uma linha preta
    # que não deveria existir, remova-a. são três folhas que se movem para esquerda. folhas únicas, sem estarem
    # duplicadas"): as três folhas do PDF, cada uma no plano dela (de 1880,3 a 1887,1 pt, a da direita por dentro),
    # uma folha só cada (o render as desenhava em dois traços ou num bloco cinza); a soleira sem as faces (`faces`), até
    # 1 px abaixo do vão, e sem a face do beiral embaixo (`BEIRAL_SEM_FACE_TD`): o Bege Bahia passa direto ao beiral
    {"nome": "de correr da suíte 2", "soleira": (1602.6, 1880.3, 1801.1, 1889.8), "faces": False,
     "batentes": [(1602.6, 1880.3, 1604.9, 1888.8), (1798.8, 1880.3, 1801.1, 1888.8)],
     "folhas": [((1604.9, 1884.9, 1669.5, 1887.1), "x"), ((1669.5, 1882.6, 1734.2, 1884.9), "x"),
                ((1734.2, 1880.3, 1798.8, 1882.6), "x")], "montante_pt": 0.6},
]


# As floreiras dos dois caixotes junto à fachada de cima (usuário, 27/10/26: "nesses "caixotes" externos temos
# floreiras. adicione o verde para termos as floreiras"): no PDF, cada caixote é o retângulo da parede de 0,12 m e o
# miolo de 2,6 x 0,19 m; o miolo recebe a floreira do lavabo da Casa C (`C.floreira_lavabo_t`: o fundo de casca e
# seixos e as plantas de folha larga da biblioteca, cortadas no miolo), com as plantas ao longo dele
FLOREIRAS_TD = {"miolos_pt": [(1658.6, 559.7, 1806.9, 570.7), (2058.0, 559.7, 2206.3, 570.7)], "n": 18,
                "plantas": ("planta_folhas_largas", "dieffenbachia", "planta_folhas_largas"), "d_m": (0.30, 0.38),
                "borda": (96, 104, 110), "borda_pt": 0.5, "seixos_m2": 0, "semente": 2710}


def floreiras_td(Q, img):
    q = FLOREIRAS_TD
    guarda = C.FLOREIRA_LAVABO_T
    rng = np.random.default_rng(q["semente"])
    out = img
    try:
        for k, pt in enumerate(q["miolos_pt"]):
            plantas = [(q["plantas"][(i + k) % len(q["plantas"])], float(rng.uniform(*q["d_m"])),
                        ((i + 0.5) / q["n"] + float(rng.uniform(-0.02, 0.02)), float(rng.uniform(0.40, 0.60))),
                        int(rng.integers(0, 360))) for i in range(q["n"])]
            C.FLOREIRA_LAVABO_T = dict(guarda, pt=pt, borda=q["borda"], borda_pt=q["borda_pt"], seixos_m2=q["seixos_m2"],
                                       semente=q["semente"] + k, plantas=plantas)
            out = C.floreira_lavabo_t(Q, out)
    finally:
        C.FLOREIRA_LAVABO_T = guarda
    print(f"    floreiras: os {len(q['miolos_pt'])} caixotes da fachada de cima com {q['n']} plantas cada")
    return out


# Os restos escuros do render junto às portas novas (pt): a ponta da folha antiga da porta da cozinha, sobre o granito à
# direita da folha nova, e os puxadores antigos nas emendas das folhas do living, sobre o piso do living, junto à face
# da soleira; os px mais escuros que o piso do retângulo (a mediana menos `escuro`) voltam ao piso `desvio_px` acima
RESTOS_PORTAS_TD = {"rets": [(1851.9, 863.0, 1857.0, 868.4), (1598.3, 994.6, 1604.0, 1005.0),
                             (1598.3, 1116.3, 1604.0, 1125.8), (1598.3, 1237.9, 1604.0, 1248.4)],
                    "escuro": 25, "desvio_px": 6}
# Os nichos das janelas da fachada de baixo à esquerda (pt; o vão do PDF entre o caixilho e a face de fora da parede,
# branco no PDF): com o brise escondido fora (pedido de 27/10, "esse beiral é todo no bege bahia"), ali aparecia o
# desenho antigo da janela do render; o nicho recebe o Bege Bahia do beiral logo abaixo, como os das outras janelas
NICHOS_BEIRAL_TD = [(822.6, 1883.6, 869.2, 1888.8), (939.8, 1883.6, 992.1, 1888.8),
                    (1846.5, 1883.6, 1898.8, 1888.8), (1956.9, 1883.6, 2009.2, 1888.8)]
# O beiral de baixo à direita todo em Bege Bahia (usuário, 27/10/26: "1. sim, todo em bege bahia"): a faixa sob as
# portas de vidro da suíte 2 e sob os banhos 2 e 3 (no render, um cinza de concreto; sob os banhos, o brise que saiu),
# da parede do jardim à ponta da fachada, entre a face de fora das paredes e a grama, recebe o Bege Bahia do beiral da
# esquerda (as mesmas linhas, do trecho mais comprido só de Bege Bahia em `fonte_px`, em espelho alternado)
# O recolhimento das folhas da porta de vidro do living (usuário, 27/10/26: "a parte de baixo onde se recolhe todas as
# portas de vidro deve ficar igual ao espaço de cima. o branco do espaço vazio sai para o tom acinzentado igual da parte
# de cima"): o vão da parede de baixo (branco no PDF) recebe o de cima, espelhado (a ponta junto da porta na porta)
RECOLHE_TD = {"fonte_pt": (1589.1, 739.3, 1597.6, 876.9), "alvo_pt": (1589.1, 1367.3, 1597.6, 1489.2)}
# O recolhimento das folhas da porta de vidro da sala íntima (usuário, 27/10/26: "esse vão para entrada das portas de
# vidro para a esquerda não pode ser branco. faça como fizemos para as portas de vidro do living"): o vão deitado na
# parede de cima do elevador (branco no PDF) recebe o mesmo vão de cima do living, girado (a ponta junto da porta, à
# direita, na porta); `alvo_pt` já só o vão, entre as faces das paredes
RECOLHE_ELEV_TD = {"alvo_pt": (1137.0, 1382.1, 1254.0, 1389.5)}
# Depois, de fora a fora (usuário, 27/10/26, vendo a borda do jardim da sala íntima em cinza e a ponta da direita em
# concreto: "vamos manter o beiral no mesmo tom claro e uniforme de fora a fora"): da laje sob o jardim (a EST_LAJE de
# 1252,3 pt, que passa sob as pontas das paredes dele) até a borda da laje da lateral (2284,3 pt); sob o jardim, as
# `grama_px` linhas logo abaixo do beiral (o fio cinza e preto da borda do jardim no render) recebem a grama de baixo
BEIRAL_BEGE_TD = {"x_pt": (1252.3, 2284.3), "y_pt": (1888.8, 1898.0), "fonte_px": (880, 1700),
                  "grama_x_pt": (1252.3, 1596.0), "grama_px": 3}
# O beiral sobe formando o L (usuário, 27/10/26: "o beiral também sobe formando o L. segue o bege no lugar desse cinza
# claro com falhas. remova o cinza e substitua por bege. não altere paredes e nem o tracejado"; depois: "é somente esse
# trecho até o brise marrom"): a faixa entre a face da parede do escritório (2275,6 pt) e o tracejado da laje
# (2284,3 pt), do pé do brise (1645,5 pt) até o beiral, recebe o beiral de junto do canto, de pé (o trecho de mesmo
# comprimento à esquerda da faixa, sem a linha da face); a face do beiral sai sob a faixa, para o L ficar contínuo. A
# coluna da face da parede e a do tracejado ficam. Vai na etapa das projeções, depois delas: antes, a limpeza do
# tracejado da lateral (`limpar_v`, que compara com a faixa vizinha) mudava com o claro e mexia no tracejado.
# Depois, em frente ao brise (usuário, 27/10/26: "corrija só um trecho fino do beiral que ficou com vestígios antigos em
# cinza. esse beiral passa em frente ao brise marrom, mas em uma faixa estreita"): de `brise` (a face de fora das lâminas
# do PDF, 2280,2 pt, e o canto da laje, 1497,7 pt) até o pé do brise, só a faixa estreita entre as lâminas e o
# tracejado, a continuação de pé do mesmo beiral
BEIRAL_L_TD = {"x_pt": (2275.6, 2284.3), "y_pt": (1645.5, 1888.8), "brise": {"x_pt": 2280.2, "y_pt": 1497.7}}
# os vãos de porta da fachada de baixo onde a linha da face do beiral (a de cima da tira) não passa: x0, x1 (pt)
BEIRAL_SEM_FACE_TD = [(1602.6, 1801.1)]


# O pisante junto ao hall de entrada (usuário, 27/10/26: "tem um traço branco no contorno de baixo do bloco de pedra no
# acesso a casa. formando um dente que não existe. corrija, deixando-o reto"): no PDF, a borda de baixo do bloco (a
# EST_LAJE de 2371,4 a 2590,8 pt) é reta em 1347,2 pt; na imagem, o Bege Bahia da parte da esquerda descia 2 px além dela
# (o traço claro) e o da direita parava nela, com a borda. Nas colunas em que o claro passa da borda, as `linhas` da borda
# vêm das da direita, em espelho
PISANTE_RETO_TD = {"x_pt": (2371.4, 2590.8), "y_pt": 1347.2, "linhas": 2, "claro": 100}


def pisante_reto_td(Q, img):
    q = PISANTE_RETO_TD
    (u0, v), (u1, _) = Q.p2q(q["x_pt"][0], q["y_pt"]), Q.p2q(q["x_pt"][1], q["y_pt"])
    x0, x1, y0 = int(np.ceil(u0)), int(np.floor(u1)), int(np.floor(v))
    y1 = y0 + q["linhas"]
    out = img.copy()
    passa = img[y1 - 1, x0:x1].astype(np.float32).mean(axis=1) > q["claro"]
    certo = np.nonzero(~passa)[0]
    n = 0
    if len(certo):
        ref = img[y0:y1, x0 + certo].copy()
        for i in np.nonzero(passa)[0]:
            j = int(np.argmin(np.abs(certo - i)))
            k = (j + (certo[j] - i)) % (2 * len(certo))                # o espelho a partir da coluna certa mais perto
            out[y0:y1, x0 + i] = ref[:, k if k < len(certo) else 2 * len(certo) - 1 - k]
            n += 1
    print(f"    pisante do hall: o contorno de baixo reto ({n} colunas)")
    return out


def beiral_l_td(Q, img):
    q = BEIRAL_L_TD
    (u0, v0), (u1, v1) = Q.p2q(q["x_pt"][0], q["y_pt"][0]), Q.p2q(q["x_pt"][1], q["y_pt"][1])
    x0, x1, y0 = int(np.ceil(u0)) + 1, int(np.floor(u1)), int(np.ceil(v0))
    face = int(np.floor(v1)) + 1                                    # a linha da face do beiral (a de cima dele)
    y1 = face + 1
    (ub, vb) = Q.p2q(q["brise"]["x_pt"], q["brise"]["y_pt"])
    xb, yb = int(np.ceil(ub)), int(np.ceil(vb))
    de_pe = img[face + 1:face + 1 + x1 - x0, x0 - (y1 - yb):x0].transpose(1, 0, 2)    # de yb (em cima) a y1
    out = img.copy()
    out[y0:y1, x0:x1] = de_pe[y0 - yb:]
    out[yb:y0, xb:x1] = de_pe[:y0 - yb, xb - x0:]
    print(f"    beiral: sobe no L entre a parede do escritório e o tracejado ({x1 - x0} x {y1 - y0} px) e segue, "
          f"estreito, em frente ao brise ({x1 - xb} x {y0 - yb} px)")
    return out


def portas_vidro_td(Q, img):
    import final3840_casaa as FA
    pv = FA.PORTAS_VIDRO
    FA.PORTAS_VIDRO = dict(pv, portas=PORTAS_VIDRO_TD)
    try:
        out = FA.portas_vidro(Q, img)
    finally:
        FA.PORTAS_VIDRO = pv
    q = RESTOS_PORTAS_TD
    n = 0
    for r in q["rets"]:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        reg = out[y0:y1, x0:x1]
        lum = reg.astype(np.int16).mean(axis=2)
        esc = lum < np.median(lum) - q["escuro"]
        reg[esc] = out[y0 - q["desvio_px"]:y1 - q["desvio_px"], x0:x1][esc]
        n += int(esc.sum())
    rq = RECOLHE_TD
    sx0, sy0, sx1, sy1 = F.ret_q(Q, rq["fonte_pt"])
    tx0, ty0, tx1, ty1 = F.ret_q(Q, rq["alvo_pt"])
    tx0, tx1 = tx0 + 1, tx1 - 1                     # só o vão, entre as faces das paredes
    fonte = out[sy0:sy1, tx0:tx1][::-1].copy()
    fonte = np.concatenate([fonte] * (1 + (ty1 - ty0) // len(fonte)), axis=0)[:ty1 - ty0]
    out[ty0:ty1, tx0:tx1] = fonte
    ex0, ey0, ex1, ey1 = F.ret_q(Q, RECOLHE_ELEV_TD["alvo_pt"])
    fonte = out[sy1 - (ex1 - ex0):sy1, tx0:tx1].transpose(1, 0, 2)
    out[ey0:ey1, ex0:ex1] = cv2.resize(fonte, (ex1 - ex0, ey1 - ey0), interpolation=cv2.INTER_AREA)
    bq = BEIRAL_BEGE_TD
    (bx0, by0), (bx1, by1) = Q.p2q(bq["x_pt"][0], bq["y_pt"][0]), Q.p2q(bq["x_pt"][1], bq["y_pt"][1])
    bx0, bx1, by0, by1 = int(np.floor(bx0)), int(np.ceil(bx1)), int(np.floor(by0)) + 1, int(np.ceil(by1))
    fonte = out[by0:by1, bq["fonte_px"][0]:bq["fonte_px"][1]].astype(np.int16)
    # da fonte, o trecho contínuo mais comprido de colunas de Bege Bahia (quente e claro em todas as linhas)
    bom = ((fonte[1:, :, 2] - fonte[1:, :, 0] > 12) & (fonte[1:].mean(axis=2) > 150)).mean(axis=0) >= 0.85
    melhor, ini = (0, 0), None
    for i, b in enumerate(list(bom) + [False]):
        if b and ini is None:
            ini = i
        elif not b and ini is not None:
            melhor = max(melhor, (i - ini, ini))
            ini = None
    fonte = fonte[:, melhor[1]:melhor[1] + melhor[0]].astype(np.uint8)
    tira = np.concatenate([fonte, fonte[:, ::-1]] * (1 + (bx1 - bx0) // max(2 * fonte.shape[1], 1)), axis=1)[:, :bx1 - bx0]
    alvo = out[by0:by1, bx0:bx1]
    livre = np.ones(alvo.shape[:2], bool)
    alvo[livre] = tira[livre]
    for xa, xb in BEIRAL_SEM_FACE_TD:
        (ua, _), (ub, _) = Q.p2q(xa, 0), Q.p2q(xb, 0)
        ua, ub = int(np.ceil(ua)), int(np.floor(ub))
        out[by0, ua:ub] = out[by0 + 1, ua:ub]
    (gx0, _), (gx1, _) = Q.p2q(bq["grama_x_pt"][0], 0), Q.p2q(bq["grama_x_pt"][1], 0)
    gx0, gx1, g = int(np.floor(gx0)), int(np.ceil(gx1)), bq["grama_px"]
    out[by1:by1 + g, gx0:gx1] = out[by1 + g:by1 + 2 * g, gx0:gx1]
    for r in NICHOS_BEIRAL_TD:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        h = y1 - y0
        out[y0:y1, x0:x1] = out[y1 + 1:y1 + 1 + h, x0:x1]
    print(f"    {n} px escuros das folhas antigas (cozinha e living) voltam ao piso; o beiral de baixo de fora a fora "
          f"({int(livre.sum())} px) e {len(NICHOS_BEIRAL_TD)} nichos de janela da fachada de baixo no Bege Bahia")
    return out


def seta_terreo_d(Q, img):
    import final3840_casaa_terreo as FT
    guarda = FT.SETA
    FT.SETA = dict(guarda, ponta=SETA_TD["ponta"])
    try:
        return FT.seta(Q, img)
    finally:
        FT.SETA = guarda


def rotulos_terreo_d(Q, img):
    """Os rótulos (E7) sem tracejado embaixo, como na Casa C (`C.rotulos_t`): os rótulos saem uma vez, e o que as
    projeções e a seta mudaram (a etapa das escadas, do cache) volta embaixo de cada texto, com folga; então os rótulos
    saem de novo, nos mesmos lugares, sobre o fundo sem o tracejado. O WC DCE TÉRREO fica no ponto do PDF, dentro do box (`ROTULOS_TD["fixos"]`), e os arcos
    das portas saem dos obstáculos (como em `rotulos_sub_d`); os guarda-roupas novos, o banco e a prateleira da adega
    entram como obstáculo."""
    rot = B.rotulos_casab(Q.pg, Q.p2q2000)
    rf = F.ROTULOS_F
    obst = [r for _, r, _ in GUARDA_ROUPAS_TD["pecas"]] + [BANCO_VARANDA_TD["pt"], ADEGA_TD["pt"]] + \
        [r for _, r in ADEGA_U_TD["lados"]]
    pontos = dict(rf["pontos"].get(Q.chave, {}), **ROTULOS_TD["pontos"])
    F.ROTULOS_F = dict(rf, pontos=dict(rf["pontos"], **{Q.chave: pontos}),
                       obstaculos_pt=dict(rf.get("obstaculos_pt", {}), **{Q.chave: obst}),
                       fixos=dict(rf.get("fixos", {}), **{Q.chave: ROTULOS_TD["fixos"]}),
                       brancos=dict(rf.get("brancos", {}), **{Q.chave: ROTULOS_TD["brancos"]}))
    todos = Q.desenhos
    Q._desenhos = [d for d in todos if not (d.get("layer") == "ARQ_PAREDE" and C.arco_porta(d))]
    try:
        def uma(im):
            return F.rotulos(Q, im, rot, Q.q["ajustes"], granito=A.granito(im, Q.q.get("granito_lum_max", 125)))
        antes = cv2.imread(str(F.ETAPAS / f"{Q.chave}_escadas.png"))
        out1 = uma(img)
        texto = np.abs(out1.astype(np.int16) - img.astype(np.int16)).max(axis=2) > 10
        perto = cv2.dilate(texto.astype(np.uint8), np.ones((2 * ROTULOS_TD["folga_px"] + 1,) * 2, np.uint8)) > 0
        proj = np.abs(img.astype(np.int16) - antes.astype(np.int16)).max(axis=2) > 0
        sob = perto & proj
        base = img.copy()
        base[sob] = antes[sob]
        print(f"    rótulos: {int(sob.sum())} px de tracejado embaixo dos textos voltam ao fundo; os rótulos de novo")
        return uma(base)
    finally:
        F.ROTULOS_F = rf
        Q._desenhos = todos


# ----------------------------------------------------------------------------------------------------------------------
# A final inteira
def passos_terreo_d(Q, ini, M):
    chave = "Terreo"
    cooktops = [(c["pt"][0] - 2, c["pt"][1] - 2, c["pt"][2] + 2, c["pt"][3] + 2) for c in COOKTOPS_D]
    camas = [c[1] for c in CAMAS_D["camas"]]
    chuv = [(min(c["ducha"][0], c["braco"][0]) - 1, min(c["ducha"][1], c["braco"][1]) - 1,
             max(c["ducha"][2], c["braco"][2]) + 1, max(c["ducha"][3], c["braco"][3]) + 1) for c in chuveiros_td()]
    fora = CARROS_PT + cooktops + FORA_PECAS_D + VASOS_D + SEM_PLANTA_TD + PECAS_OCULTAS_TD + camas + BANCOS_D + \
        [BANQUETAS_D["caixa_pt"]] + chuv
    # sob os carros, a legenda tem o contorno deles (traços): ali tudo é granito, para o piso não guardar o desenho
    for r in CARROS_PT:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        Q.chapada[y0:y1, x0:x1] = (50, 66, 90)
    F.piso_textura = piso_estratos_d
    F.VASOS_COR = dict(F.VASOS_COR, Terreo=VASOS_TD)
    cinza = F.PAREDES_F["cinza"]
    return [
        ("pisos", lambda im: sem_tracejado_ilha_d(Q, quartzito_banhos_d(
            Q, F.pisos(Q, im, incluir={"granito": CARROS_PT}, bruto={"travertino": "estratos"}), im))),
        ("bordas", lambda im: B.bordas_grama(im, chave)),
        ("vegetacao", lambda im: C.vegetacao_c(Q, im, M)),
        ("bancadas", lambda im: bancadas_terreo_d(Q, im)),
        ("pecas", lambda im: tapete_suave_d(Q, C.pecas_c(Q, im, ini, fora, camas + NAO_TAPETE_D))),
        ("tampas", lambda im: cama_dce_d(Q, plantas_vaso_d(Q, C.camas_render(Q, F.tampas_vasos(Q, C.restos_piso(
            Q, im, ini, FORA_PECAS_D)), ini), ini))),
        ("vasos", lambda im: F.vasos_cor(Q, im)),
        ("biblioteca", lambda im: biblioteca_terreo_d(Q, im)),
        ("moveis", lambda im: moveis_td(Q, im)),
        ("carros", lambda im: carros_d(Q, im, M)),
        ("chuveiros", lambda im: chuveiros_terreo_d(Q, im)),
        ("boxes", lambda im: boxes_terreo_d(Q, im)),
        ("paredes", lambda im: brises_madeira(Q, F.paredes(Q, im, cor=cinza))),
        ("soleiras", lambda im: vao_sem_soleira_td(Q, C.soleira_elevador(Q, F.soleiras(Q, im)))),
        # a entrada das esquadrias vai em cópia: `F.esquadrias_terreo` escreve nela, e o `antes` de `pos_esquadrias_d`
        # tem de ser a etapa das soleiras (os recortes atrás das folhas abertas não voltavam)
        # a adega em U depois das esquadrias: a limpeza delas espelhava a ponta da prateleira junto do vidro
        ("esquadrias", lambda im: adega_u_d(Q, pos_vidros_d(Q, portas_vidro_td(Q, restos_folha_td(Q, entre_porta_box_td(
            Q, pos_esquadrias_d(Q, F.esquadrias_terreo(Q, im.copy(), parede=cinza), im), im), im)), im))),
        ("cortinas", lambda im: sem_trilho_fora_d(Q, F.cortinas(Q, im, paredes_pdf=True), im)),
        ("escadas", lambda im: escadas_terreo_d(Q, im)),
        ("projecoes", lambda im: hall_porta_td(Q, pisante_reto_td(Q, beiral_l_td(Q, projecoes_lajes_td(
            Q, projecoes_terreo_d(Q, im)))))),
        ("seta", lambda im: seta_terreo_d(Q, im)),
        ("rotulos", lambda im: rotulos_terreo_d(Q, im)),
    ]


def final_3840_d(chave, salvar=True, de=None, ate=None):
    """A final de 3840 px com os rótulos. de: recomeça desta etapa (a anterior vem do cache); ate: para nela."""
    import time
    contexto_d()
    Q = F.Quadro(chave)
    ini = C.quadro_inicial_c(Q)
    M = F.afim_render(Q, CASA_D / Q.q["render"], CASA_D / Q.q["aprovada"])
    if chave == "Subsolo":
        passos = passos_subsolo_d(Q, ini)
    else:
        import final3840_casaa as FA
        passos = passos_terreo_d(Q, ini, M)
        FA.travertino_bruto = travertino_bruto_d        # o travertino bruto das bancadas e cubas (pedido de 27/10)
    nomes = [n for n, _ in passos]
    i0 = nomes.index(de) if de else 0
    i1 = nomes.index(ate) + 1 if ate else len(passos)
    F.ETAPAS.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(F.ETAPAS / f"{chave}_{nomes[i0 - 1]}.png")) if i0 > 0 else ini
    for nome, f in passos[i0:i1]:
        t0 = time.time()
        img = f(img)
        print(f"  [{nome}] {time.time() - t0:.0f} s", flush=True)
        cv2.imwrite(str(F.ETAPAS / f"{chave}_{nome}.png"), img)
    if salvar and i1 == len(passos):
        nome = CASA_D / "renders" / f"POE642_CasaD_PH_{chave}_final_rotulos.png"
        cv2.imwrite(str(nome), img)
        print(f"    {nome} {img.shape[1]}x{img.shape[0]}")
    return Q, img


# ----------------------------------------------------------------------------------------------------------------------
# O Subsolo
# A escada de 16 degraus no Subsolo (item 5, R14; resposta 3): a mesma, subindo do pátio (degrau 1, à esquerda) para o
# terraço; cheia até a marca de corte do PDF do Subsolo (o zigue-zague no degrau 7). Desde a auditoria de 26/10, sem os
# bocéis e sem o triângulo, nevoada depois do corte, com o S (`ESCADA_SUB_D`, abaixo)
ESCADA_S = dict(ESCADA_T, nome="de 16 degraus, do pátio ao terraço", inicio="esquerda", viva="esquerda",
                apos="esmaecida",
                corte=[(785.0, 1415.5), (801.4, 1445.7), (809.9, 1445.7), (796.9, 1453.2), (805.4, 1453.2),
                       (821.5, 1483.5)])
# Os aparelhos da academia (esteiras, bicicletas e supinos) ficam os da final aprovada de 15/10: pelo PDF saíam
# silhuetas cinza chapadas, sem a lona da esteira nem as barras dos supinos (no tamanho do PDF, já conferido). Uma
# caixa por grupo (as bicicletas, as esteiras e os supinos): numa caixa só, a sauna e o vestiário entravam junto e o
# Bege Bahia quase neutro da final antiga voltava por cima do novo
FORA_PECAS_S = [(672.1, 1636.5, 743.3, 1721.9), (957.0, 1622.2, 1075.6, 1726.7), (1203.8, 1598.5, 1298.8, 1864.3)]
# A cama do DCE 1 fica a da final aprovada (resposta 5, "Os do render"). A bancada do vestiário com a cuba, que vinha
# da final aprovada (item 37 de 15/10), é refeita pelo PDF desde a auditoria de 26/10 (`banhos_sub_d`).
CAMAS_S = {"borda": 1.7, "ss": 4, "semente": 41, "camas": [("DCE 1", (846.0, 1203.9, 902.7, 1317.3), "baixo",
                                                             "solteiro")]}
# Depois (usuário, 27/10/26: "melhore o aspecto da roupa de cama para dar mais clareza de se trata de uma cama"): a cama do
# render era um retângulo branco com o travesseiro; no colchão (o retângulo do PDF menos a borda, que fica a moldura de
# madeira do render) entra a roupa de cama da biblioteca do tipo "motorista", a da cama de solteiro do Térreo da Casa A
# aprovada em 21/10 ("está tudo muito brancão"): o lençol branco com a dobra, o travesseiro, o edredom em linho claro e a
# peseira bordô nos pés, com o pesponto; a cabeceira embaixo, contra a parede da janela
# No Térreo (auditoria de 26/10, item 13), a mesma roupa de cama na cama do DCE, com a cabeceira em cima
CAMA_DCE_S = {"camas": {"Subsolo": [("DCE 1", CAMAS_S["camas"][0][1], "baixo", "motorista")],
                        "Terreo": [("DCE", (2317.0, 727.8, 2373.7, 841.2), "cima", "motorista")]},
              "borda": 1.7, "ss": 4, "semente": 31}


# Revisão de 28/10/26, item 7 (OK do usuário): a parede tracejada dupla do PDF em volta do pátio (ARQ_PAREDE, fora da
# pegada: as duas linhas à esquerda, as duas embaixo, que seguem até o canto da academia, e a de fora no alto, a ~1 m do
# piso) sumia sob a hachura do terreno (R2), e só ficava o traço de dentro no alto, onde ele coincide com a borda do
# pátio. Os traços do próprio PDF entram por cima da hachura, em preto (fundo claro), nítidos; os que tocam a pegada
# (dilatada `folga_px`) ficam de fora (as paredes e o contorno do pátio).
PAREDE_PATIO_SD = {"caixa_q": (440, 1150, 1500, 1800), "folga_px": 2, "cor": (30, 30, 30), "larg_px": 1.2}


def parede_patio_sd(Q, img, peg):
    q = PAREDE_PATIO_SD
    k = 2 * q["folga_px"] + 1
    dentro = cv2.dilate((peg > 0.5).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    cx0, cy0, cx1, cy1 = q["caixa_q"]
    segs = []
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            (u0, v0), (u1, v1) = Q.p2q(it[1].x, it[1].y), Q.p2q(it[2].x, it[2].y)
            if not all(cx0 <= u <= cx1 and cy0 <= v <= cy1 for u, v in ((u0, v0), (u1, v1))):
                continue
            if dentro[int(v0), int(u0)] or dentro[int(v1), int(u1)]:
                continue
            segs.append((it[1].x, it[1].y, it[2].x, it[2].y))
    out = _tracos_d(Q, img, segs, q["cor"], q["larg_px"])
    print(f"    pátio: a parede tracejada dupla do PDF, {len(segs)} traços em preto sobre a hachura")
    return out


def pegada_subsolo(Q):
    """O que fica em cor cheia no Subsolo (R2; resposta 6, "Hachura"): o Subsolo e o pátio, o que a legenda pinta (os
    ambientes, o pátio e a escada, com as paredes), fechado e sem furos. A faixa verde de 15/10 fica de fora (entra na
    hachura do Térreo final). 0 a 1, no quadro."""
    from scipy import ndimage
    nb = (Q.chapada.min(axis=2) < 250).astype(np.uint8)
    # sem os traços finos (o tracejado do contorno da laje, que fechava a faixa verde junto com o pátio e a deixava
    # dentro da pegada); as paredes e os pisos, largos, ficam
    nb = cv2.morphologyEx(nb, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    nb = cv2.morphologyEx(nb, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb, 8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 2000])
    m = ndimage.binary_fill_holes(m)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6)
    return np.maximum(a, m * 1.0)


# A auditoria de 26/10 no Subsolo (mapa `renders/POE642_CasaD_PH_Subsolo_auditoria_2610_v2.jpg`; usuário, 27/10/26: "ok,
# aplique a lista. no item 7, siga a recomendação"), com as rotinas do Subsolo aprovado da Casa C:
# 1. as paredes em cinza 80 (E10; não há pilares), com os vãos das janelas que ficavam escuros no claro (`C.janelas_s`;
#    os batentes do elevador, a partir de 1240 pt, ficam);
# 2-3. a escada de 16 degraus sem os traços dos bocéis e sem o triângulo (E3, E8): os degraus em Bege Bahia com o
#    sombreamento de subida (o 1, junto ao pátio, o mais escuro), o corte do PDF (no degrau 7) e os degraus 8 a 16,
#    depois dele, nevoados, como a escada estreita da Casa C (`C.escada_estreita_s`, aqui sem esmaecer o trecho de antes
#    do corte, que é cheio desde 15/10); o S do PDF centrado no degrau 1 (a origem do texto cai no pátio);
# 4. o armário do DCE 1 (o retângulo da DOC_LINHAS, junto à parede de cima) com os cabides (E2), o guarda-roupa aberto
#    dos closets das Casas A e B (`elementos.guarda_roupa`), com as portas para o quarto;
# 5. o box de correr do WC DCE em vidro contínuo, com as faces finas e a sombra curta, desde 28/10 fechado, de parede a
#    parede, sem o trilho tracejado (E5, `final3840_casaa.boxes`); antes, a faixa cinza tracejada da base e do render sai, refeita com o granito logo acima;
# 6-7. as bancadas com a borda no tom escurecido da pedra e a sombra curta (E9) e os materiais da recomendação: o WC DCE
#    como o BH serviço das Casas B e C (bancada em granito marrom no tom do piso, levemente escurecido, a cuba de
#    semiencaixe e o vaso brancos, a torneira cromada); o vestiário como o BH academia da Casa C (bancada em granito
#    marrom, a cuba esculpida em granito marrom na bacia do PDF, a torneira cromada na prateleira de trás, o vaso marrom).
#    Depois (usuário, 27/10/26: "Vestiário: mármore bege Bahia no piso e Cuba esculpida, bancada da pia no granito
#    marrom, sanitário branco"): a cuba esculpida em Bege Bahia (`CUBAS_CHAPA_D`) e o vaso branco; o piso já era Bege
#    Bahia e a bancada, granito marrom. No PDF do Subsolo as bancadas são só traços (a ARQ_BANCADAS sem preenchimento): entram pelos retângulos (pt);
# 8. os chuveiros do WC DCE, da ducha da sauna e do vestiário na placa cromada com os furinhos, o braço até a parede e a
#    canopla (`final3840_casaa.chuveiro`); as placas e os braços do PDF ficam fora das peças;
# 9. as portas de correr do pátio para a academia como as da Casa C (`C.portas_academia_s`): a soleira de Bege Bahia na
#    faixa toda da parede, as 4 folhas nos planos do PDF com os montantes e os batentes;
# 10. o rótulo do WC DCE no meio do piso livre, entre a cuba, o vaso e a parede (E7). O arco da porta do PDF, que não
#    aparece (R3), ocupava esse piso no mapa de obstáculos dos rótulos e o mandava para o lado do chuveiro: os arcos das
#    portas (`C.arco_porta`) saem dos obstáculos dos rótulos do Subsolo.
# Com as paredes em cinza, o nicho do chuveiro do vestiário (o retângulo da ARQ_BANCADAS dentro da parede da direita,
# que a parede preta escondia) saía branco: entra na pedra clara das soleiras, com as faces finas, como prateleira.
# Depois, vendo a final (usuário, 27/10/26: "remova a linha técnica em diagonal. deixe apenas uma sombra no lugar."): sem
# a linha de corte do PDF e sem o zigue-zague da quebra; a divisa com o trecho nevoado é a diagonal reta do PDF (do 1º
# ao último ponto do corte) e, no lugar da linha, só uma sombra suave sobre os degraus de antes dela
ESCADA_SUB_D = {"pdf": ESCADA_S["pdf"], "bocels": ESCADA_T["bocels"],
                "corte": [ESCADA_S["corte"][0], ESCADA_S["corte"][-1]], "esmaecer": 0.0, "nevoa": {"branco": 0.72, "sigma_px": 1.2}, "linha": None,
                "sombra_corte": {"forca": 0.30, "alc_px": 4.0}, "letra": 0.0, "semente": 763}
ARMARIO_DCE_S = {"pt": (761.9, 1183.0, 830.0, 1214.2), "lado": "baixo", "ss": 4, "semente": 57}
BOX_WC_DCE_S = {"faixa": (686.0, 1224.8, 752.9, 1229.2), "sobe_px": 7}
BANHOS_SUB_D = {
    "wc_dce": {"bancada": (686.0, 1232.2, 705.3, 1276.6), "cuba": (687.3, 1243.1, 709.9, 1265.7),
               "torneira": (689.6, 1253.3, 699.0, 1255.4), "base": (690.4, 1254.35, 1.4), "semente": 2710},
    "vestiario": {"bancada": (924.6, 1801.6, 955.0, 1874.7), "cuba": (931.9, 1817.0, 951.8, 1856.2),
                  "torneira": (928.6, 1835.6, 936.0, 1837.7), "base": (928.6, 1836.65, 1.4), "semente": 2711},
    "borda": 0.62, "larg_px": 0.6, "sombra": 0.34}
# os vasos tingidos: nenhum (o do WC do vestiário era marrom; pedido de 27/10, "sanitário branco"); o do WC DCE é branco
VASOS_SUB_D = []
CHUVEIROS_SUB_D = [
    {"nome": "WC DCE", "ducha": (701.6, 1201.2, 712.8, 1212.4), "braco": (686.0, 1206.1, 708.3, 1207.6),
     "canopla": (686.0, 1205.4, 687.3, 1208.3)},
    {"nome": "ducha da sauna", "ducha": (810.9, 1847.2, 822.1, 1858.5), "braco": (815.7, 1851.7, 817.2, 1874.1),
     "canopla": (815.0, 1872.8, 817.9, 1874.1)},
    {"nome": "vestiário", "ducha": (1067.3, 1839.5, 1078.5, 1850.7), "braco": (1071.8, 1844.4, 1094.1, 1845.8),
     "canopla": (1092.8, 1843.7, 1094.1, 1846.5)}]
PORTA_ACADEMIA_SUB_D = {"nome": "do pátio para a academia", "soleira": (600.0, 1500.4, 608.5, 1738.5),
                        "batentes": [(600.0, 1500.4, 608.5, 1501.5), (600.0, 1737.4, 608.5, 1738.5)],
                        "folhas": [((600.0, 1501.5, 602.3, 1560.5), "y"), ((602.3, 1560.5, 604.6, 1619.4), "y"),
                                   ((602.3, 1619.4, 604.6, 1678.4), "y"), ((600.0, 1678.4, 602.3, 1737.4), "y")],
                        "montante_pt": 5.7, "pontas_pt": [(596.0, 1738.5, 612.0, 1751.0), (596.0, 1489.0, 612.0, 1500.4)]}
JANELAS_SUB_D = dict(C.JANELAS_S, x_max_pt=1240.0)
ROTULOS_SUB_D = {"pontos": {"WC DCE": (731.5, 1268.0)}}
NICHO_VESTIARIO_S = (1094.7, 1833.9, 1099.8, 1855.4)
# Depois, vendo a final (usuário, 27/10/26: "corrija as portas e seus contornos, além da parede na parte de baixo"; "corrija
# os erros nas paredes"; "corrija esse erro na parede. complete a parte que ficou faltando no batente da porta do banho";
# "limpe o risco atrás da porta e os riscos em frente a janela no piso"): a faixa de limpeza das esquadrias
# (`B.esquadrias_final`) refaz o que está em volta das folhas e das janelas espelhando a vizinhança, e no Subsolo trazia o
# que não é piso: o cinza da parede numa faixa acima da folha da porta da escada para o depósito, o Bege Bahia da soleira
# num bloco acima da folha de baixo da porta dupla do depósito (e o granito no lugar da parede logo abaixo dela), o traço
# do box acima da folha da porta do WC DCE, os pedaços do Bege Bahia de fora no piso diante da janela do WC DCE, a cama
# esticada diante da janela do DCE 1, a faixa de granito mais clara ao lado da folha da porta do DCE 1 e os recortes de
# Bege Bahia na parede do vestiário, acima da folha e do batente da porta. Depois das esquadrias:
# - a parede do PDF (e o traço da face, 1 px para fora) volta à etapa anterior (as soleiras) onde lá era o cinza ou o
#   traço, neutros, e as esquadrias puseram cor (como as paredes recortadas atrás das portas do Térreo da Casa C,
#   `C.pos_esquadrias_t`): o batente da porta do vestiário fica inteiro, encostado na parede;
# - nas `faixa_px` de cada lado de cada folha e do caixilho das janelas, fora da peça nova e da parede, o piso volta à
#   etapa anterior; onde lá estava a folha antiga (o traço claro e a sombra arroxeada do render, que fogem do piso em
#   volta), entra o piso da etapa anterior um pouco mais longe da folha (`desloca_px`), do mesmo lado.
POS_ESQUADRIAS_SUB_D = {
    # fora: o box de correr entre o vaso e o chuveiro do vestiário, com uma folha em cada face da parede do PDF; ali as
    # esquadrias abrem o vão entre as folhas (o piso passa), como na final aprovada
    "paredes": {"croma_min": 12, "cinza_tol": 14, "neutro": 10, "fora": [(1020.4, 1806.1, 1059.5, 1816.3)]},
    "faixa_px": 8, "cobre": 0.2, "anel_px": 5, "desloca_px": (8, 11, 14, 17), "velho": {"gb": 9, "lum": 45},
    "pecas": [("porta dupla do depósito, folha de cima", (912.2, 1329.2, 950.3, 1331.4)),
              ("porta dupla do depósito, folha de baixo", (912.2, 1403.1, 950.3, 1405.4)),
              ("porta da escada para o depósito", (974.5, 1477.8, 1009.9, 1480.1)),
              ("porta do WC DCE", (718.0, 1237.6, 753.4, 1239.9)),
              ("porta do DCE 1", (766.9, 1283.7, 769.2, 1319.1)),
              ("porta do vestiário", (930.3, 1753.4, 964.3, 1755.7)),
              ("porta da sauna", (803.2, 1802.3, 805.5, 1843.6)),
              # as janelas: o caixilho fino das esquadrias (1 pt além do retângulo do PDF); do lado de dentro, o piso vai
              # até ele
              ("janela do WC DCE", (702.3, 1320.3, 734.0, 1325.5)),
              # no DCE 1, a cama e o criado-mudo encostam na janela: do lado de dentro, a faixa volta inteira à etapa
              # anterior (lá, a cabeceira e o traço da parede; mais longe da janela seria a cama de novo)
              ("janela do DCE 1", (828.1, 1320.3, 882.6, 1325.5), {"so_antes": -1})]}
# No Térreo (auditoria de 26/10, item 1), a mesma limpeza: a parede do PDF de volta onde as esquadrias a cortaram
POS_ESQUADRIAS_D = {"Subsolo": POS_ESQUADRIAS_SUB_D,
                    "Terreo": dict(POS_ESQUADRIAS_SUB_D, paredes=dict(POS_ESQUADRIAS_SUB_D["paredes"], fora=[], claro=40,
                                                                      fino_px=6, longo_px=12), pecas=[])}


def escada_sub_d(Q, img):
    guarda = C.ESTREITA_S
    C.ESTREITA_S = ESCADA_SUB_D
    try:
        return C.escada_estreita_s(Q, img)
    finally:
        C.ESTREITA_S = guarda


def armario_dce_d(Q, img):
    """O guarda-roupa aberto, com os cabides e o cabideiro (R11, E2), no retângulo do PDF, como os closets da Casa B
    (`ajustes_casab.guarda_roupas_terreo`), no quadro do Subsolo."""
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from elementos import guarda_roupa
    from retoque_1pav_casae import GUARDA_ROUPAS
    q = ARMARIO_DCE_S
    S = q["ss"]
    x0, y0, x1, y1 = q["pt"]
    (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
    comp, prof = max(x1 - x0, y1 - y0) / 56.69, min(x1 - x0, y1 - y0) / 56.69
    cor, alfa = guarda_roupa(comp, prof, Q.px_m * S, semente=q["semente"], miolo=GUARDA_ROUPAS["miolo"],
                             moldura=GUARDA_ROUPAS["moldura"], barra=True)
    k = {"baixo": 0, "direita": 1, "cima": 2, "esquerda": 3}[q["lado"]]
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
    out = img.astype(np.float32)
    out[Y0:Y1, X0:X1] = out[Y0:Y1, X0:X1] * (1 - ar) + cr
    print(f"    DCE 1: o armário com os cabides e o cabideiro ({comp:.2f} x {prof:.2f} m), as portas para o quarto")
    return np.clip(out, 0, 255).astype(np.uint8)


def cama_dce_d(Q, img):
    """A roupa de cama da biblioteca (`elementos.roupa_de_cama`) no colchão de cada cama de CAMA_DCE_S, no quadro, como
    `ajustes_casab.camas_b` (as camas em pé na planta, com a cabeceira em cima ou embaixo)."""
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import elementos
    q = CAMA_DCE_S
    k = q["ss"]
    out = img.copy()
    camas = q["camas"][Q.chave]
    for i, (nome, r, cab, tipo) in enumerate(camas):
        e = q["borda"]
        (u0, v0), (u1, v1) = Q.p2q(r[0] + e, r[1] + e), Q.p2q(r[2] - e, r[3] - e)
        cor, al = elementos.roupa_de_cama((v1 - v0) / Q.px_m, (u1 - u0) / Q.px_m, Q.px_m * k, tipo,
                                          semente=q["semente"] + i)
        if cab == "cima":
            cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE)[:, ::-1], cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)[:, ::-1]
        else:
            cor, al = cv2.rotate(cor, cv2.ROTATE_90_COUNTERCLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_COUNTERCLOCKWISE)
        X0, Y0 = int(np.floor(u0)) - 1, int(np.floor(v0)) - 1
        X1, Y1 = int(np.ceil(u1)) + 2, int(np.ceil(v1)) + 2
        tw, th = int(round((u1 - u0) * k)), int(round((v1 - v0) * k))
        cor = cv2.resize(np.ascontiguousarray(cor * al[..., None]), (tw, th), interpolation=cv2.INTER_AREA)
        al = cv2.resize(np.ascontiguousarray(al), (tw, th), interpolation=cv2.INTER_AREA)
        g = np.zeros(((Y1 - Y0) * k, (X1 - X0) * k, 3), np.float32)
        ga = np.zeros(g.shape[:2], np.float32)
        ox, oy = int(round((u0 - X0) * k)), int(round((v0 - Y0) * k))
        g[oy:oy + th, ox:ox + tw] = cor
        ga[oy:oy + th, ox:ox + tw] = al
        pre = cv2.resize(g, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        a_ = cv2.resize(ga, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a_[..., None]) + pre), 0, 255).astype(np.uint8)
    print("    camas: a roupa de cama da biblioteca (" + "; ".join(f"{n}, {t}" for n, _, _, t in camas) +
          "), com a cabeceira contra a parede")
    return out


def banhos_sub_d(Q, img):
    import final3840_casaa as FA
    q = BANHOS_SUB_D
    out = np.ascontiguousarray(img.copy())
    ge = F.BANCADAS_F["granito_escuro"]
    med = np.median(img[Q.cor([ge["cor_piso"]], tol=6)].reshape(-1, 3), axis=0).astype(np.float32)

    def granito(tl, s, tom=None):
        G = FA._granito(Q, tl, s)
        return G if tom is None else G / G.reshape(-1, 3).mean(axis=0) * tom
    w, v = q["wc_dce"], q["vestiario"]
    # o WC DCE: a bancada no granito do piso, levemente escurecido; a cuba de semiencaixe branca, a torneira
    out = FA.bancada_pedra(Q, out, w["bancada"], lambda tl: granito(tl, w["semente"], med * ge["escurecer"]),
                           q["borda"], q["larg_px"], q["sombra"])
    out = FA.cuba_branca(Q, out, w["cuba"])
    out = FA.torneira(Q, out, w["torneira"], w["base"])
    # o vestiário: a bancada em granito marrom (o piso é Bege Bahia), a cuba esculpida na bacia do PDF em Bege Bahia
    # (pedido de 27/10; antes, em granito), a torneira na prateleira de trás, junto à parede
    out = FA.bancada_pedra(Q, out, v["bancada"], lambda tl: granito(tl, v["semente"]), q["borda"], q["larg_px"],
                           q["sombra"])
    out = np.ascontiguousarray(np.clip(F.cuba_esculpida(Q, out, v["cuba"], "bege"), 0, 255).astype(np.uint8))
    out = FA.torneira(Q, out, v["torneira"], v["base"])
    for c in CHUVEIROS_SUB_D:
        out = FA.chuveiro(Q, out, c)
    print(f"    WC DCE: bancada em granito marrom levemente escurecido, cuba e vaso brancos, torneira; vestiário: bancada "
          f"em granito marrom, cuba esculpida em Bege Bahia, torneira; {len(CHUVEIROS_SUB_D)} chuveiros na placa "
          f"cromada com o braço")
    return out


def box_wc_dce_d(Q, img):
    import final3840_casaa as FA
    q = BOX_WC_DCE_S
    x0, y0, x1, y1 = F.ret_q(Q, q["faixa"])
    out = img.copy()
    d = q["sobe_px"]
    out[y0:y1, x0:x1] = img[y0 - d:y1 - d, x0:x1]
    return FA.boxes(Q, np.ascontiguousarray(out))


def nicho_d(Q, img):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    from retoque_terreo_casae import BEGE
    x0, y0, x1, y1 = F.ret_q(Q, NICHO_VESTIARIO_S)
    q = F.SOLEIRAS_F
    T = textura("bege_bahia", Q.px_m, y1 - y0, x1 - x0, semente=q["semente"] + 60).astype(np.float32)
    T = np.clip((1 + q["forca"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(BEGE["tom"]), 0, 255)
    out = img.copy()
    out[y0:y1, x0:x1] = T.astype(np.uint8)
    cv2.rectangle(out, (x0, y0), (x1 - 1, y1 - 1), tuple(int(c) for c in q["linha"]), 1)
    return out


def rotulos_sub_d(Q, img):
    todos = Q.desenhos
    Q._desenhos = [d for d in todos if not (d.get("layer") == "ARQ_PAREDE" and C.arco_porta(d))]
    try:
        return F.rotulos(Q, img, B.rotulos_casab(Q.pg, Q.p2q2000), Q.q["ajustes"],
                         granito=A.granito(img, Q.q.get("granito_lum_max", 125)))
    finally:
        Q._desenhos = todos


def portas_academia_sub_d(Q, img):
    guarda = C.PORTA_ACADEMIA_S
    C.PORTA_ACADEMIA_S = PORTA_ACADEMIA_SUB_D
    try:
        return C.portas_academia_s(Q, img)
    finally:
        C.PORTA_ACADEMIA_S = guarda


def _faixas_folha(out, A, a, ret, q, so_antes=0):
    """Os dois lados (-1, antes; 1, depois) da peça horizontal `ret` (px, fracionário): a faixa de `faixa_px` fora da peça
    (as linhas que ela cobre em até `cobre`) e da parede volta a A (a etapa anterior); onde A tinha a peça antiga (foge do
    piso do anel logo depois da faixa; se lá é parede, do anel do outro lado), o piso de A mais longe; no lado `so_antes`,
    a faixa toda volta a A."""
    f, an = q["faixa_px"], q["anel_px"]
    u0, v0, u1, v1 = ret
    c0, c1 = int(np.floor(u0)) - 1, int(np.ceil(u1)) + 1
    topo, base = int(np.floor(v0 - 1 + q["cobre"])) + 1, int(np.ceil(v1 - q["cobre"]))
    lados = {-1: ((topo - f, topo), (topo - f - an, topo - f)), 1: ((base, base + f), (base + f, base + f + an))}
    refs = {}
    for lado, (_, (g0, g1)) in lados.items():
        ref = A[g0:g1, c0:c1][a[g0:g1, c0:c1] <= 0.02]
        if len(ref) >= 10:
            refs[lado] = (np.median(ref[:, 1] - ref[:, 0]), np.median(ref.mean(axis=1)))
    n = 0
    for lado, ((r0, r1), _) in lados.items():
        if not refs:
            break
        gb, lum = refs.get(lado, refs.get(-lado))

        def velho(B):
            return ((B[..., 1] - B[..., 0]) < gb - q["velho"]["gb"]) | (np.abs(B.mean(axis=2) - lum) > q["velho"]["lum"])
        livre = a[r0:r1, c0:c1] <= 0.02
        novo = A[r0:r1, c0:c1].copy()
        falta = (velho(novo) & livre) if so_antes != lado else np.zeros_like(livre)
        for s in q["desloca_px"]:
            if not falta.any():
                break
            fonte = A[r0 + lado * s:r1 + lado * s, c0:c1]
            ok = falta & ~velho(fonte) & (a[r0 + lado * s:r1 + lado * s, c0:c1] <= 0.02)
            novo[ok] = fonte[ok]
            falta &= ~ok
        m = livre & ~falta
        out[r0:r1, c0:c1][m] = novo[m].astype(np.uint8)
        n += int(m.sum())
    return n


def pos_esquadrias_d(Q, img, antes):
    q = POS_ESQUADRIAS_D[Q.chave]
    out = img.copy()
    A = antes.astype(np.int32)
    a = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "ARQ_ELEMENTOS FIXOS") and d.get("fill") is not None
                    and max(d["fill"]) < 0.5, ss=4)
    # as faixas em volta das folhas e das janelas (as verticais, na imagem transposta)
    n_fx = 0
    for _, r, *op in q["pecas"]:
        (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        if r[2] - r[0] >= r[3] - r[1]:
            o, B, m, ret = out, A, a, (x0, y0, x1, y1)
        else:
            o, B, m, ret = out.transpose(1, 0, 2), A.transpose(1, 0, 2), a.T, (y0, x0, y1, x1)
        n_fx += _faixas_folha(o, B, m, ret, q, **(op[0] if op else {}))
    # a parede do PDF (e o traço da face, 1 px para fora) de volta onde lá era o cinza (ou o traço, mais escuro) e as
    # esquadrias puseram cor
    pq = q["paredes"]
    parede = cv2.dilate((a >= 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    era = (C._croma(antes) <= pq["neutro"]) & (A.mean(axis=2) <= np.mean(F.PAREDES_F["cinza"]) + pq["cinza_tol"])
    volta = parede & era & (C._croma(out) >= pq["croma_min"])
    for r in pq["fora"]:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        volta[y0:y1, x0:x1] = False
    # os recortes atrás das folhas abertas (usuário, 27/10/26, nos banhos 2 e 3: "corrija as paredes que estão atrás
    # das portas. existe um recorte na imagem que precisa ser preenchido com a parede"): a limpeza das esquadrias leva
    # o piso de junto da folha sobre 2 a 5 px da parede atrás dela; no quartzito dos banhos, neutro, o critério da cor
    # não pegava. Onde a ARQ_PAREDE é parede, lá era o cinza e agora há um claro (`claro`), em faixas finas e compridas
    # (`fino_px`, `longo_px`: os recortes, não os batentes das portas e do elevador), a parede volta
    if "claro" in pq:
        ap = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") is not None
                         and max(d["fill"]) < 0.5, ss=4)
        claro = (ap >= 0.5) & era & (out.astype(np.int32).mean(axis=2) - A.mean(axis=2) > pq["claro"])
        n, lab, st, _ = cv2.connectedComponentsWithStats(claro.astype(np.uint8))
        rec = np.isin(lab, [i for i in range(1, n) if min(st[i, 2], st[i, 3]) <= pq["fino_px"]
                            and max(st[i, 2], st[i, 3]) >= pq["longo_px"]])
        volta |= rec
        print(f"    recortes atrás das folhas: {int(rec.sum())} px de parede de volta")
    out[volta] = antes[volta]
    print(f"    depois das esquadrias: {n_fx} px de piso de volta em volta de {len(q['pecas'])} folhas e janelas; "
          f"{int(volta.sum())} px de parede de volta")
    return out


def passos_subsolo_d(Q, ini):
    chave = "Subsolo"
    peg = pegada_subsolo(Q)
    dentro = peg > 0.5
    AJ.SUBSOLO_R2 = dict(AJ.SUBSOLO_R2, terreo=CASA_D / "renders" / "POE642_CasaD_PH_Terreo_final_rotulos.png")
    C.CAMAS_C, C.BANCOS_C = CAMAS_S, []
    F.VASOS_COR = dict(F.VASOS_COR, Subsolo=VASOS_SUB_D)
    F.ROTULOS_F = dict(F.ROTULOS_F, pontos=dict(F.ROTULOS_F["pontos"], Subsolo=ROTULOS_SUB_D["pontos"]))
    cinza = F.PAREDES_F["cinza"]
    camas = [c[1] for c in CAMAS_S["camas"]]
    b = BANHOS_SUB_D
    fora = FORA_PECAS_S + camas + [b["wc_dce"]["bancada"], b["wc_dce"]["cuba"], b["vestiario"]["bancada"],
                                   BOX_WC_DCE_S["faixa"]] + \
        [(min(c["ducha"][0], c["braco"][0]) - 1, min(c["ducha"][1], c["braco"][1]) - 1,
          max(c["ducha"][2], c["braco"][2]) + 1, max(c["ducha"][3], c["braco"][3]) + 1) for c in CHUVEIROS_SUB_D]
    return [
        ("pisos", lambda im: F.pisos(Q, im, dentro=dentro)),
        ("bancadas", lambda im: C.bancadas_c(Q, im)),            # o peitoril cinza do WC DCE (a única peça cheia)
        ("pecas", lambda im: F.pecas_pdf(Q, im, ini, fora=fora, camas=camas)),
        ("aparelhos", lambda im: C.pecas_do_render(Q, im, ini, FORA_PECAS_S, C.neutro, "academia: os aparelhos")),
        ("tampas", lambda im: cama_dce_d(Q, C.camas_render(Q, F.tampas_vasos(Q, im), ini))),
        ("vasos", lambda im: F.vasos_cor(Q, im)),
        ("armario", lambda im: armario_dce_d(Q, im)),
        ("banhos", lambda im: box_wc_dce_d(Q, banhos_sub_d(Q, im))),
        ("paredes", lambda im: F.paredes(Q, im, cor=cinza)),
        ("soleiras", lambda im: vao_sem_soleira_td(Q, nicho_d(Q, C.soleira_elevador(Q, F.soleiras(Q, im))))),
        ("esquadrias", lambda im: pos_esquadrias_d(Q, portas_academia_sub_d(Q, C.janelas_s(
            Q, B.esquadrias_final(im, chave, Q.pg, Q.p2q, Q.px_m, parede=cinza), JANELAS_SUB_D)), im)),
        ("escadas", lambda im: escada_sub_d(Q, im)),
        ("hachura", lambda im: parede_patio_sd(Q, AJ.subsolo_hachurado(im, peg, Q.px_m), peg)),
        ("rotulos", lambda im: rotulos_sub_d(Q, im)),
    ]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(PAVIMENTOS_D))
    ap.add_argument("--de", default=None, help="recomeça desta etapa (pisos, bordas, vegetacao, bancadas, pecas, ...)")
    ap.add_argument("--ate", default=None, help="para nesta etapa")
    a = ap.parse_args()
    final_3840_d(a.pavimento, de=a.de, ate=a.ate)

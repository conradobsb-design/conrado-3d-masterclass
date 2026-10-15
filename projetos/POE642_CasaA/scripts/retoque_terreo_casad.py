#!/usr/bin/env python3
"""Retoque sem IA do render do Térreo da Casa D (prompt v1). A imagem final é o render.

Os itens são corrigidos um a um, na ordem pedida pelo usuário.

1. Porta pivotante principal (entre o hall de entrada e o estar): o motor cortou a folha no
   alinhamento da parede; no PDF ela vai de ponta a ponta, passando para o lado do hall até o arco
   pequeno. A folha é estendida com o próprio trecho dela (mesmas linhas) até o fim do PDF, onde o
   arco pequeno do render já começa. Mesmo caso da Casa C.
2. Chuveiros do banho master: o motor ligou os dois chuveiros numa barra de parede a parede. No PDF
   (ARQ_LOUÇAS E METAIS) são duas duchas quadradas de ~19 cm, cada uma num braço que sai da parede
   lateral (a da esquerda e a da direita). A barra sai, com o texto ilegível que o motor pôs junto à
   parede de baixo (as linhas viram o piso limpo de cima, em espelho, que já tem a sombra da parede
   da direita), e entram as duchas na placa aprovada da Casa A
   reduzida, com sombra curta, o braço cromado da parede até o centro da ducha e a canopla na parede.
3. Armários até o teto (no PDF, os retângulos com diagonal da layer DOC_LINHAS E PROJEÇÕES): 16
   retângulos (closet do master, suítes 1 e 2, circulação, cozinha, serviço, DCE e gourmet). O
   motor os fez como móveis de meia altura, com sombra projetada no piso. A sombra sai: em cada face
   livre que dá para piso, o escurecimento é medido (mediana ao longo da face, por canal, até o
   patamar do piso), ajustado por um modelo suave (o tom de cada régua do vinílico fica) e refinado
   ponto a ponto ao longo da face (penumbra nas pontas); onde duas sombras se encontram (cantos
   internos) vale a mais escura, sem somar; a borda da face repete a linha seguinte já limpa. O
   tampo fica no tom areia dos armários da Casa C, com o veio do próprio armário do render (pedido
   do usuário: só o tom muda; o sombreado de caixa das bordas sai); onde o motor fez caixa lisa,
   quartzo ou caixa branca, o veio vem do armário da direita da suíte 2. Contorno fino nas faces
   livres. Embaixo dos dois armários junto a uma bancada (canto de cima da cozinha e o vizinho ao
   gás), a sombra é funda e emenda na da bancada: o piso é refeito em granito tecido dos trechos
   limpos, com a borda da sombra da bancada em diagonal (luz de cima à direita) e, na cozinha, a
   sombra da parede da direita continuando.
4. Área molhada da bancada da pia da cozinha: o retângulo da layer ARQ_BANCADAS em volta das cubas
   é demarcado em traço cinza fino, como na Casa C, nos lados livres (esquerda e embaixo; em cima é
   a parede e à direita, o armário do canto).
5. Eletrodomésticos da cozinha: os dois volumes ao lado do armário do canto (no PDF, sem diagonal)
   ficam em inox; a caixa do render fica (sombreado, borda das portas, divisória e sombra) e só o tom
   muda, para aço escovado levemente frio, com riscos verticais sutis. O do canto é armário (areia).
6. Porta de correr do abrigo de gás: o motor fez uma soleira cinza larga no vão de cima. As linhas
   dela viram o piso do abrigo (as de baixo, em espelho) e entra a porta do PDF (ARQ_PAREDE): duas
   folhas em planos diferentes na espessura da parede (a da esquerda por fora, a da direita por
   dentro), com montantes e batentes, em 8x, e a sombra curta da folha de dentro.
7. Carros: o motor fez os três em prata; cada um ganha um tom (pedido do usuário): grafite, branco
   perolado e azul-marinho. Na silhueta de cada carro (o que não é o granito quente do piso, mais a
   borda misturada), uma curva de tom leva a luminância do prata à da tinta, mantendo a ordem do
   render (vidros mais escuros que a lataria, reflexos); a cor entra só nos tons médios e claros e
   as lanternas ficam.
8. Erros 1 e 2 da lista (lote): no PDF o lado esquerdo do lote é só a linha tracejada; o motor fez
   um muro preto. A grama vai até a linha (as colunas do muro vêm das de logo à direita) e fora do
   lote volta a ser a base (fundo branco e linha tracejada). As plantas dos cantos de cima e de baixo
   à esquerda, que passavam da linha e dos muros, terminam no lote; os trechos de muro cobertos pelas
   folhas são refeitos com o perfil de uma coluna limpa do próprio muro.
9. Erro 3 da lista (faixa com X à direita do hall): no PDF é gramado com os retângulos com X da
   projeção da laje e as duas linhas tracejadas embaixo; o motor fez um canteiro de plantas. A faixa
   vira grama tecida (image quilting) do gramado limpo à direita da garagem, com a sombra do muro de
   cima e do muro da direita; as linhas do PDF (levado ao render, sem as curvas de nível, que a base
   esconde) entram em cinza claro, engrossadas para o traço fino do render. O muro de cima (e a grade
   à direita), onde as pontas das folhas passavam, vira a mediana de cada linha; a folha que caía no
   travertino do hall sai por inpainting.
10. Erro 4 da lista (ponta do acesso de veículos): o motor fez o trecho junto ao limite direito em
   piso cinza; é o mesmo granito da garagem (pedido do usuário). Granito tecido (image quilting) do
   acesso limpo, com o perfil de luz de cada linha (a sombra do muro de cima) do granito logo à
   esquerda, por canal.
11. Erro 5 da lista (projeção sobre a entrada da garagem): os retângulos com X (DOC_LINHAS E
   PROJEÇÕES) e o contorno tracejado (os traços curtos das layers de parede e de elementos fixos),
   levados ao render, em cinza e traço fino, como os arcos sobre o granito, só sobre o granito.
12. Erro 6 da lista (portas sobre o granito sem arco): como na Casa C, os arcos das portas (curvas da
   layer ARQ_PAREDE) que caem sobre o granito são redesenhados em cinza e traço fino, só onde o piso é
   granito: banho gourmet, louceiro, despensa, serviço para a garagem e a porta dupla da área
   descoberta.
13. Erro 7 da lista (área descoberta): o motor pôs um vaso sanitário junto à parede da direita e não
   fez o X tracejado do PDF. O vaso sai (granito tecido, na luz do entorno: `apagar`) e o X da layer
   DOC_LINHAS E PROJEÇÕES entra em cinza e traço fino, só sobre o granito da base chapada.
14. Erro 8 da lista (tanques): o motor fez uma cuba só; no PDF são dois tanques. A cuba do motor sai
   (bancada tecida dos trechos limpos, na luz dos dois lados) e entram os dois tanques aprovados da
   Casa B (os mesmos da Casa C), girados para a torneira ficar do lado da parede, na mesma escala.
15. Erro 9 da lista (DCE): o motor fez uma marcenaria em L no lugar da cama de solteiro e do
   criado-mudo do PDF. A sombra alta que ela jogava no piso sai (campo de luz suave do piso dividido
   pelo nível do piso aceso de cada linha; o arco da porta fica); o L vira vinílico tecido do próprio
   quarto e entram a cama de solteiro e o criado-mudo do quarto externo da Casa C (do render dela), a
   cama girada para a cabeceira ficar na parede de cima, nas caixas do PDF, com sombra curta.
16. Erros 10 e 11 da lista (cooktops): no PDF os dois têm 5 bocas, 2 em cima (nos cantos) e 3
   embaixo; a ilha da cozinha ficou sem cooktop e o da gourmet saiu com 4 bocas nos cantos e uma no
   meio. Os dois viram o cooktop da gourmet da Casa C já corrigido (2 em cima e 3 embaixo), levado à
   caixa do PDF; o da gourmet do motor sai antes (quartzo tecido da própria bancada, na luz dela).
17. Erro 12 da lista (bancada da pia da gourmet): o motor a fez em madeira (em dois tons); é quartzo,
   como as outras bancadas. Quartzo tecido da bancada do cooktop, na cor dela, com o perfil de luz por
   linha do trecho limpo (sombra da parede e borda da frente) e, junto à geladeira, a luz 2D da
   própria bancada (a sombra dela); a cuba fica.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_terreo_casad.py RENDER.webp --saida PASTA --nome NOME
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))
from retoque_terreo_casac import CHUVEIRO_TETO, CROMO, CROMO_CLARO, CROMO_ESCURO, SS  # noqa: E402
from retoque_terreo_casac import COZINHA as COZINHA_C  # noqa: E402
from retoque_terreo_casac import ARCOS_GRANITO  # noqa: E402
from texturizar_base import quilting  # noqa: E402

BASE = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - TÉRREO - CASA D.pdf"
CONFIG = RAIZ / "POE642_CasaD/config_bases.json"

# porta pivotante principal: linhas da folha, trecho da folha copiado e a parte que faltou (até o
# fim da folha no PDF, onde o arco pequeno do render começa)
PIVOTANTE = {"linhas": (567, 571), "fonte_x": 1240, "de": 1267, "ate": 1282}
# chuveiros do banho master: a barra do motor (com os registros, a sombra e o texto ilegível que o
# motor escreveu junto à parede de baixo), refeita com as linhas limpas de cima (em espelho); duchas,
# braços e canoplas do PDF (ARQ_LOUÇAS E METAIS, em px do render)
CHUVEIROS_BHM = {
    "barra": (403, 882, 458, 902),
    "emenda": 0,
    "duchas": [
        {"nome": "esquerda", "ducha": (411.9, 886.1, 418.0, 892.3), "braco": (403.0, 415.0, 889.2),
         "canopla": (403.0, 888.2, 404.0, 890.2)},
        {"nome": "direita", "ducha": (442.7, 886.2, 448.8, 892.4), "braco": (445.7, 457.7, 889.3),
         "canopla": (456.7, 888.3, 457.7, 890.3)},
    ],
    "larg_braco": 0.8,
    "sombra": {"desloc": (-1.0, 1.0), "sigma": 0.8, "forca": 0.3},
}

# armários até o teto: no PDF, os retângulos com uma diagonal (layer DOC_LINHAS E PROJEÇÕES, traço
# 0,57). Retângulo de cada um em px do render (a diagonal levada pela cadeia da base).
ARMARIOS = [
    ("closet do master, braço de cima", (267.8, 810.1, 351.8, 828.7)),
    ("closet do master, braço da esquerda", (267.7, 828.7, 286.4, 903.3)),
    ("closet do master, braço de baixo", (286.4, 884.7, 395.2, 903.3)),
    ("circulação, à direita do banho master", (497.8, 862.9, 516.6, 903.3)),
    ("à esquerda do banho 1", (544.5, 810.1, 563.3, 903.3)),
    ("suíte 1, braço em pé", (568.0, 737.0, 586.6, 799.2)),
    ("suíte 1, braço deitado", (586.7, 737.0, 624.0, 755.7)),
    ("suíte 2, braço deitado", (1065.6, 737.0, 1121.7, 755.6)),
    ("suíte 2, braço em pé", (1103.0, 755.6, 1121.6, 799.2)),
    ("suíte 2, à direita", (1126.2, 737.0, 1145.0, 799.2)),
    ("cozinha, canto de baixo", (945.3, 319.5, 970.2, 344.4)),
    ("cozinha, canto de cima", (1062.7, 189.9, 1089.7, 210.1)),          # o motor fez quartzo
    ("serviço, junto ao WC DCE", (1198.5, 266.0, 1238.9, 286.2)),
    ("serviço, vizinho ao gás", (1280.9, 189.9, 1330.8, 211.6)),
    ("DCE, embaixo", (1294.8, 329.8, 1325.9, 348.4)),
    ("gourmet", (787.7, 224.1, 808.2, 239.6)),                          # o motor fez caixa branca
]
ARMARIO = {
    # areia: o tom do painel laqueado da Casa C (o dos armários da cozinha de lá, aprovado). O veio
    # é o do próprio armário do render (pedido do usuário): só o tom muda
    "fonte_areia": (RAIZ / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_retocado.png", COZINHA_C["fonte_areia"]),
    # veio: a luminância do armário sobre ela mesma desfocada; o limite tira o sombreado de caixa
    # que o motor fez nas bordas (lia como móvel baixo) e deixa o veio, que é sutil
    "sigma_veio": 3.0, "veio_lim": (0.92, 1.08),
    # px a mais embaixo, onde o render ainda tem a borda clara (da bancada ou da caixa do motor)
    "ajuste": {"cozinha, canto de cima": (0, 0, 0, 1), "serviço, vizinho ao gás": (0, 0, 0, 1)},
    # onde o motor não fez armário de madeira (caixa lisa com sombreado de móvel baixo, quartzo ou
    # caixa branca), o veio vem de outro armário do render (o da direita da suíte 2, alto: o veio
    # é vertical, como em todos os armários do render, e só se repete na largura, em espelho)
    "veio_emprestado": (1128, 740, 1143, 797),
    "sem_veio": ["cozinha, canto de baixo", "cozinha, canto de cima", "serviço, junto ao WC DCE",
                 "serviço, vizinho ao gás", "gourmet"],
    # faces junto a uma bancada: a sombra embaixo do armário é funda e emenda na da bancada; o
    # granito granulado não aguenta ser clareado tanto. O piso é refeito (ver PISO_SOB_ARMARIO)
    "manter_piso": [("cozinha, canto de cima", "baixo"), ("serviço, vizinho ao gás", "baixo")],
    "contorno": COZINHA_C["contorno"],
    # sombra que o motor projetou no piso: faixa medida a partir de cada face livre (até D px); a
    # referência é o patamar do piso logo depois da sombra
    "faixa": 22, "limiar": 0.97, "alem": 6, "suave": 2,
}

# piso refeito embaixo dos armários que encostam numa bancada: faixa de H linhas abaixo do armário,
# em granito tecido (image quilting) dos trechos limpos; a borda da sombra da bancada fica em
# diagonal (a luz vem de cima à direita), com penumbra curta; a sombra da parede da direita (medida
# logo abaixo da faixa, coluna a coluna) continua; trechos protegidos (a folha da porta) ficam
PISO_SOB_ARMARIO = {
    "fontes": [(1240, 240, 1290, 262), (1000, 300, 1060, 318)],
    # (armário, linhas, sombra da parede ao lado continua, trechos protegidos)
    "faixas": [("cozinha, canto de cima", 20, True, []),
               ("serviço, vizinho ao gás", 26, False, [(1303, 219, 1331, 222), (1329, 215, 1336, 220)])],
    "penumbra": 3.0, "emenda": 6, "medida": 16,
}

# área molhada da bancada da pia da cozinha (PDF, ARQ_BANCADAS): traço cinza fino, como na Casa C,
# nos lados livres (a esquerda e embaixo; em cima é a parede e à direita, o armário do canto)
AREA_MOLHADA = {
    "pontos": [(975.7, 190.5), (975.7, 209.5), (1062.1, 209.5)],
    "traco": COZINHA_C["traco"], "larg_traco": COZINHA_C["larg_traco"], "forca_traco": COZINHA_C["forca_traco"],
}

# eletrodomésticos da cozinha (os dois volumes do PDF, ao lado do armário do canto): em inox. A caixa
# do render fica (sombreado, borda das portas, divisória e sombra); só o tom muda, com escovado sutil
INOX = {
    "janela": (971, 317, 1024, 346),
    "cor": (186, 184, 181),                     # BGR: aço escovado, levemente frio
    "lum": (70.0, 150.0),                       # luminância: granito (0) .. caixa (1), nas bordas
    "escovado": 0.025, "semente": 642,
}

# porta de correr do abrigo de gás (PDF, ARQ_PAREDE, em px do render): duas folhas em planos
# diferentes na espessura da parede de cima (a da esquerda por fora, a da direita por dentro), com
# os montantes nas pontas e os batentes. O motor fez uma soleira cinza larga: as linhas dela viram o
# piso do abrigo (as de baixo, em espelho), com a sombra curta das folhas
PORTA_GAS = {
    "soleira": (1335, 185, 1370, 193),
    "folhas": [(1336.7, 185.2, 1352.5, 186.5), (1352.5, 186.5, 1368.4, 187.7)],
    "montantes": [(1336.7, 1338.2), (1351.0, 1352.5), (1352.5, 1354.1), (1366.9, 1368.4)],
    "batentes": [(1335.4, 185.2, 1336.7, 186.8), (1368.4, 185.2, 1369.7, 186.8)],
    "janela": (1332, 182, 1373, 196),
    "folha": (196, 199, 202), "montante": (150, 154, 158), "contorno": (85, 92, 98), "larg_contorno": 0.3,
    "sombra": (0.80, 0.90, 0.96),                # linhas logo abaixo da folha de dentro
}

# carros da garagem: o motor fez os três em prata. Cada um ganha um tom (pedido do usuário). Na
# silhueta do carro (o que não é o granito quente do piso), uma curva de tom leva a luminância do
# prata à da tinta, mantendo a ordem do render (vidros mais escuros que a lataria, reflexos); a cor
# entra só nos tons médios e claros (o vidro escuro fica neutro)
CARROS = {
    # (nome, caixa, curva: ("escurecer", base, faixa, expoente) ou ("clarear", ini, fim, força), cor BGR)
    "carros": [("esquerda", (1388, 246, 1458, 398), ("escurecer", 26.0, 74.0, 1.6), (1.02, 1.0, 0.98)),   # grafite
               ("meio", (1475, 243, 1542, 391), ("clarear", 130.0, 195.0, 0.55), (0.99, 1.0, 1.01)),     # branco perolado
               ("direita", (1557, 236, 1633, 407), ("escurecer", 18.0, 52.0, 1.4), (1.34, 0.96, 0.74))],  # azul-marinho
    "quente": 16, "lum_min": 90.0, "claro": 125.0, "fecho": 9, "reflexo": 0.6, "cor_lum": (70.0, 140.0),
    "lanterna": (40, 120),                      # R - B e R mínimos: lanternas e faróis âmbar ficam
}
# lote (erros 1 e 2): no PDF o lado esquerdo do lote é só a linha tracejada; o motor fez um muro
# preto (x 188-195). A grama vai até a linha (as colunas vêm das de logo à direita) e fora do lote
# volta a ser a base (fundo branco e linha tracejada). As plantas dos cantos de cima e de baixo à
# esquerda, que passavam da linha e dos muros, terminam no lote: os muros cobertos pelas folhas são
# refeitos com o perfil de uma coluna limpa do próprio muro
LOTE = {
    "x_grama": 190, "faixa_muro": (190, 196), "desloc": 8,
    "muro_cima": (66, 75), "coluna_cima": 480,
    "muro_baixo": (1000, 1007), "coluna_baixo": 560,
    "x_cantos": 470, "y": (0, 1050),
}

# faixa com X à direita do hall (erro 3): no PDF é gramado, com os retângulos com X (projeção da
# laje, linhas finas) e as duas linhas tracejadas embaixo; o motor fez um canteiro de plantas. A
# faixa vira grama tecida (image quilting) do gramado limpo à direita da garagem, com a sombra do
# muro de cima e do muro da direita, e as linhas do PDF (levado ao render) entram em cinza claro
FAIXA_X = {
    "ret": (1364, 415, 1648, 487),
    # muro de cima (e a grade à direita) com as pontas das folhas: cada linha vira a mediana dela
    "muro": [((1364, 1597), (409, 415)), ((1597, 1648), (409, 415))],
    # folha sobre o travertino do hall, à esquerda: os px verdes (G > R) e o contorno escuro dela
    # (abaixo do arco da porta, que fica) saem por inpainting
    "hall": (1350, 430, 1364, 476), "contorno_folha": (1356, 445, 1364, 472), "escuro": 175,
    "fonte_grama": [(1680, 300, 1750, 470)],
    # sombra: (onde começa, até onde, força) a partir do muro de cima (por trecho de x) e da direita
    "sombra_cima": [((1364, 1597), 12, 0.45), ((1597, 1648), 8, 0.25)],
    "sombra_dir": (1648, 9, 0.40),
    "linhas": {"larg": 4, "cor": (205, 210, 205), "forca": 0.5,
               "excluir": ["ARQ_CONTRAPISO", "ARQ_ELEMENTOS FIXOS"]},
}

# ponta do acesso de veículos (erro 4): o motor fez o trecho junto ao limite direito em cinza; no
# PDF (e a pedido do usuário) é o mesmo granito da garagem. Granito tecido (image quilting) do
# acesso limpo, com o perfil de luz de cada linha (a sombra do muro de cima) do granito logo à
# esquerda, por canal
ACESSO = {
    "ret": (1656, 89, 1757, 235),
    "fonte": [(1440, 96, 1640, 180)],
    "perfil_x": (1600, 1650),
}
# projeção sobre a entrada da garagem (erro 5): os retângulos com X e o contorno tracejado da layer
# DOC_LINHAS E PROJEÇÕES, levados ao render, em cinza e traço fino (como os arcos sobre o granito),
# só sobre o granito
PROJECAO_GARAGEM = {
    "janela": (1338, 175, 1668, 238),
    # os X (DOC_LINHAS) e o contorno tracejado (os traços curtos das layers de parede e elementos fixos)
    "linhas": {"larg": 3.6, "cor": (160, 161, 160), "forca": 0.7, "layers": ["DOC_LINHAS E PROJEÇÕES"],
               "curtos": {"ARQ_PAREDE": 4.5, "ARQ_ELEMENTOS FIXOS": 4.5}},
    "granito_lum": (35.0, 115.0),
}

# área descoberta (erro 7): o motor pôs um vaso sanitário (com a sombra) junto à parede da direita e
# não fez o X tracejado do PDF. O vaso sai (granito tecido, na luz do entorno) e o X entra em cinza
# e traço fino, só sobre o granito
AREA_DESCOBERTA = {
    "vaso": (1211, 293, 1240, 317),
    "fonte_granito": [(1160, 322, 1200, 346), (1440, 96, 1640, 180)],
    "janela_x": (1150, 288, 1250, 350),
}

# tanques (erro 8): o motor fez uma cuba só; no PDF são dois tanques. A cuba do motor sai (bancada
# tecida dos trechos limpos, na luz do entorno) e entram os dois tanques aprovados da Casa B (os
# mesmos usados na Casa C), girados para a torneira ficar do lado da parede (em cima), na mesma escala
TANQUES = {
    "cuba_motor": (1216, 190, 1241, 210),
    "fonte_bancada": [(1195, 191, 1214, 208), (1243, 191, 1262, 208)],
    "fonte_tanques": (RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Terreo_v4_retocado.png", (1147, 763, 1165, 804)),
    "em": (1197, 191),
}

# quarto de serviço (DCE, erro 9): o motor fez uma marcenaria em L no lugar da cama de solteiro e do
# criado-mudo. A sombra alta que a marcenaria jogava no piso sai (campo de luz suave do piso,
# dividido pelo nível do piso aceso de cada linha); o L vira piso (vinílico tecido do próprio quarto)
# e entram a cama de solteiro e o criado-mudo usados no quarto externo da Casa C (do render dela),
# a cama girada para a cabeceira ficar na parede de cima, nas caixas do PDF, com sombra curta
DCE = {
    "piso": (1294, 268, 1338, 330),           # piso do quarto com a sombra da marcenaria
    "piso_aceso_x": (1297, 1307),             # colunas do piso aceso (referência de cada linha)
    "sombra_x0": 1310,                        # a correção vale daqui para a direita
    "L": [(1326, 330, 1369, 348), (1337, 268, 1369, 330)],     # marcenaria do motor -> piso
    "fonte_piso": [(1296, 297, 1322, 329)],
    "cama": (1338, 271, 1369, 334),
    "criado": (1323, 272, 1334, 285),
    "fonte": RAIZ / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_render.webp",
    "fonte_cama": (753, 189, 825, 222), "cortar_cobertor": (796, 807),
    "fonte_criado": (733, 178, 747, 195),
    "sombra": (0.84, 0.93),                   # 2 px à esquerda e embaixo de cada peça
}

# cooktops (erros 10 e 11): no PDF os dois têm 5 bocas, 2 em cima (nos cantos) e 3 embaixo. A ilha
# da cozinha ficou sem cooktop e o da gourmet saiu com 4 bocas nos cantos e uma no meio. Os dois
# viram o cooktop da gourmet da Casa C já corrigido (exatamente 2 em cima e 3 embaixo), levado à
# caixa do PDF; o da gourmet do motor sai antes (quartzo tecido da própria bancada)
COOKTOPS_D = {
    "fonte": (RAIZ / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_retocado.png", (718, 565, 747, 583)),
    "gourmet_motor": (795, 317, 828, 338),
    "fonte_quartzo": [(762, 320, 792, 348), (832, 320, 862, 348)],
    "caixas": [("ilha da cozinha", (1010, 249, 1038, 264)), ("gourmet", (798, 318, 825, 334))],
}

# bancada da pia da gourmet (erro 12): o motor a fez em madeira; é quartzo, como as outras bancadas.
# Quartzo tecido da bancada da gourmet (a do cooktop), na cor dela, com a luz da própria bancada do
# render (a sombra da parede, a da geladeira e a borda da frente: a luminância suavizada sobre a do
# trecho limpo); a cuba fica
BANCADA_GOURMET = {
    "ret": (727, 245, 852, 270),
    "cuba": (801, 248, 823, 268),
    "fonte_quartzo": [(762, 320, 792, 348), (832, 320, 862, 348)],
    "ref": (735, 252, 790, 266),
    # o motor fez a madeira em dois tons (dois blocos): a luz é o perfil por linha do bloco da
    # esquerda; só junto à geladeira (a partir de x 822, com transição até 832) vale a luz 2D do
    # bloco da direita (a sombra da geladeira)
    "ref_dir": (824, 258, 836, 266), "geladeira": (822, 832),
}


def alinhar_base(render):
    """Base 16:9 reduzida e levada ao render por SIFT + afim; também a base chapada (v2)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), render.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    return (cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255)),
            cv2.warpAffine(chapada, A, render.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255)),
            A)


def pdf_cadeia(A, forma_render):
    """Página do PDF e a conversão PDF -> render pela mesma cadeia da base (recorte, largura da
    base, tela 16:9, redução ao tamanho do render e o afim A)."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Terreo"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sx, sy = forma_render[1] / wt, forma_render[0] / ht

    def p2r(x, y):
        bx, by = ((x - clip.x0) * zoom + (wt - wb) // 2) * sx, ((y - clip.y0) * zoom + (ht - hb) // 2) * sy
        return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]

    return pg, p2r


def pdf_no_render(janela, A, forma_render):
    """Trecho do PDF rasterizado e levado ao render pela mesma cadeia da base, em SS vezes a
    resolução (cinza, 255 = papel)."""
    cfg = json.loads(CONFIG.read_text())
    doc = pymupdf.open(PDF)
    pg = doc[cfg["pavimentos"]["Terreo"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sx, sy = forma_render[1] / wt, forma_render[0] / ht

    def p2r(x, y):
        bx, by = ((x - clip.x0) * zoom + (wt - wb) // 2) * sx, ((y - clip.y0) * zoom + (ht - hb) // 2) * sy
        return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]

    Ai = np.linalg.inv(np.vstack([A, [0, 0, 1]]))

    def r2p(x, y):
        bx, by, _ = Ai @ [x, y, 1]
        return (bx / sx - (wt - wb) // 2) / zoom + clip.x0, (by / sy - (ht - hb) // 2) / zoom + clip.y0

    x0, y0, x1, y1 = janela
    a, b = r2p(x0 - 2, y0 - 2), r2p(x1 + 2, y1 + 2)
    ret = pymupdf.Rect(a[0], a[1], b[0], b[1])
    zp = 60
    pix = pg.get_pixmap(clip=ret, matrix=pymupdf.Matrix(zp, zp), alpha=False, colorspace=pymupdf.csGRAY)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    src = [(0, 0), (pix.width, 0), (0, pix.height)]
    dst = [((p2r(ret.x0 + u / zp, ret.y0 + v / zp)[0] - x0) * SS, (p2r(ret.x0 + u / zp, ret.y0 + v / zp)[1] - y0) * SS)
           for u, v in src]
    M = cv2.getAffineTransform(np.float32(src), np.float32(dst))
    return cv2.warpAffine(np.ascontiguousarray(img), M, ((x1 - x0) * SS, (y1 - y0) * SS), flags=cv2.INTER_AREA,
                          borderValue=255)


def grama(out, fontes, alto, largo):
    """Grama tecida (image quilting) de trechos limpos do gramado do render."""
    f = []
    for x0, y0, x1, y1 in fontes:
        g = out[y0:y1, x0:x1].astype(np.float32)
        f += [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    return quilting(f, alto, largo, p=16, sobra=5, candidatos=600)[:alto, :largo]


def linhas_pdf(out, A, janela, q, mascara=None):
    """Traços do PDF (vetor, por layer) na janela, levados ao render pela cadeia da base e
    desenhados em SS vezes a resolução, no traço fino do render, em cor clara. O MuPDF não desliga
    as layers deste PDF no raster, então os traços vêm de get_drawings: q["layers"] (só essas) ou
    q["excluir"] (todas menos essas), e q["curtos"] (layer: comprimento máximo em px), só os traços
    curtos de tracejado dessas layers; as curvas de nível (ocultas na base) nunca entram."""
    x0, y0, x1, y1 = janela
    h, w = y1 - y0, x1 - x0
    pg, p2r = pdf_cadeia(A, out.shape)
    ocultas = set(json.loads(CONFIG.read_text())["pavimentos"]["Terreo"]["layers_ocultas"])
    m = np.zeros((h * SS, w * SS), np.uint8)
    larg = max(1, int(round(q["larg"])))

    def pt(v):
        x, y = p2r(v.x, v.y)
        return [int(round((x - x0) * SS)), int(round((y - y0) * SS))]

    for d in pg.get_drawings():
        layer = d.get("layer") or ""
        if layer in ocultas or d.get("color") is None:
            continue
        curto = q.get("curtos", {}).get(layer)
        if "layers" in q and layer not in q["layers"] and curto is None:
            continue
        if layer in q.get("excluir", ()):
            continue
        (rx0, ry0), (rx1, ry1) = p2r(d["rect"].x0, d["rect"].y0), p2r(d["rect"].x1, d["rect"].y1)
        if rx1 < x0 - 1 or rx0 > x1 + 1 or ry1 < y0 - 1 or ry0 > y1 + 1:
            continue
        for it in d["items"]:
            if curto is not None and (it[0] != "l" or np.hypot(*np.subtract(p2r(it[1].x, it[1].y),
                                                                            p2r(it[2].x, it[2].y))) > curto):
                continue                                   # dessas layers, só os traços de tracejado
            if it[0] == "l":
                cv2.line(m, pt(it[1]), pt(it[2]), 255, larg, cv2.LINE_AA)
            elif it[0] == "c":
                tt = np.linspace(0, 1, 24)[:, None]
                c = [np.array(pt(v), np.float32) for v in it[1:5]]
                curva = (1 - tt) ** 3 * c[0] + 3 * (1 - tt) ** 2 * tt * c[1] + 3 * (1 - tt) * tt ** 2 * c[2] + tt ** 3 * c[3]
                cv2.polylines(m, [np.round(curva).astype(np.int32)], False, 255, larg, cv2.LINE_AA)
            elif it[0] == "re":
                r = it[1]
                cv2.polylines(m, [np.array([pt(r.tl), pt(r.tr), pt(r.br), pt(r.bl)], np.int32)], True, 255, larg,
                              cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * q["forca"]
    if mascara is not None:
        a *= mascara
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + np.array(q["cor"], np.float32) * a[..., None],
                                0, 255).astype(np.uint8)
    return out


def textura(out, fontes, alto, largo, p=16):
    """Textura tecida (image quilting) de trechos limpos do render, normalizada (média 1 por canal)."""
    f = []
    for x0, y0, x1, y1 in fontes:
        g = out[y0:y1, x0:x1].astype(np.float32)
        g = g / g.reshape(-1, 3).mean(axis=0)
        f += [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    return quilting(f, alto, largo, p=p, sobra=max(3, p // 3), candidatos=600)[:alto, :largo]


def apagar(out, ret, mascara, fontes, sigma=5.0, borda=1.0):
    """Tira um objeto: os px da máscara viram a textura das fontes na luz do entorno (o campo de
    luz, por canal, é interpolado dos px de fora da máscara por convolução normalizada)."""
    x0, y0, x1, y1 = ret
    h, w = y1 - y0, x1 - x0
    m = cv2.GaussianBlur(mascara.astype(np.float32), (0, 0), borda) if borda else mascara.astype(np.float32)
    m = np.maximum(m, mascara.astype(np.float32))
    reg = out[y0:y1, x0:x1].astype(np.float32)
    fora = (1 - mascara.astype(np.float32))[..., None]
    num = cv2.GaussianBlur(reg * fora, (0, 0), sigma)
    den = cv2.GaussianBlur(np.repeat(fora, 3, axis=2), (0, 0), sigma)
    luz = num / np.maximum(den, 1e-3)
    tex = textura(out, fontes, h, w)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - m[..., None]) + tex * luz * m[..., None], 0, 255).astype(np.uint8)
    return out


def pivotante(out):
    q = PIVOTANTE
    y0, y1 = q["linhas"]
    de, ate, fx = q["de"], q["ate"], q["fonte_x"]
    out[y0:y1, de:ate] = out[y0:y1, fx:fx + ate - de]
    print(f"    porta pivotante: folha estendida até o fim do PDF (x {ate})")
    return out


def chuveiros_bhm(out):
    q = CHUVEIROS_BHM
    x0, y0, x1, y1 = q["barra"]
    n = y1 - y0
    out[y0:y1, x0:x1] = out[y0 - n:y0, x0:x1][::-1]          # piso limpo de cima, em espelho
    e = q["emenda"]
    for k in range(e):                                        # emenda suave embaixo
        t = (k + 1) / (e + 1)
        y = y1 - e + k
        out[y, x0:x1] = np.clip(out[y, x0:x1] * (1 - t) + out[y1 + k, x0:x1] * t, 0, 255).astype(np.uint8)

    wx0, wy0, wx1, wy1 = x0, y0, x1, y1
    h, w = wy1 - wy0, wx1 - wx0

    def px(v, o=0.0):
        return int(round((v - o) * SS))

    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def pintar(mascara, cor):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    s = q["sombra"]
    for d in q["duchas"]:
        dx0, dy0, dx1, dy1 = d["ducha"]
        ducha = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(ducha, (px(dx0, wx0), px(dy0, wy0)), (px(dx1, wx0), px(dy1, wy0)), 255, -1)
        M = np.float32([[1, 0, s["desloc"][0] * SS], [0, 1, s["desloc"][1] * SS]])
        sombra = cv2.GaussianBlur(cv2.warpAffine(ducha.astype(np.float32), M, (w * SS, h * SS)), (0, 0),
                                  s["sigma"] * SS) / 255
        reg *= (1 - s["forca"] * cv2.resize(sombra, (w, h), interpolation=cv2.INTER_AREA))[..., None]

        placa = cv2.resize(img[hy0:hy1, hx0:hx1], (px(dx1 - dx0), px(dy1 - dy0)), interpolation=cv2.INTER_CUBIC)
        cor = np.zeros((h * SS, w * SS, 3), np.uint8)
        cor[px(dy0, wy0):px(dy0, wy0) + placa.shape[0], px(dx0, wx0):px(dx0, wx0) + placa.shape[1]] = placa
        a = cv2.resize(ducha.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        c = cv2.resize(cor.astype(np.float32) * (ducha[..., None] / 255), (w, h), interpolation=cv2.INTER_AREA)
        c = c / np.maximum(a, 1e-6)
        reg = reg * (1 - a) + c * a

        bx0, bx1, by = d["braco"]                             # braço por cima da ducha, até o centro
        braco = np.zeros_like(ducha)
        cv2.line(braco, (px(bx0, wx0), px(by, wy0)), (px(bx1, wx0), px(by, wy0)), 255, px(q["larg_braco"]))
        brilho = np.zeros_like(ducha)
        cv2.line(brilho, (px(bx0, wx0), px(by - 0.1, wy0)), (px(bx1, wx0), px(by - 0.1, wy0)), 255, max(1, px(0.3)))
        pintar(braco, CROMO_ESCURO)
        pintar(brilho, CROMO_CLARO)
        cx0, cy0, cx1, cy1 = d["canopla"]
        canopla = np.zeros_like(ducha)
        cv2.rectangle(canopla, (px(cx0, wx0), px(cy0, wy0)), (px(cx1, wx0), px(cy1, wy0)), 255, -1)
        pintar(canopla, CROMO)
        print(f"    banho master, chuveiro da {d['nome']}: ducha, braço da parede e canopla do PDF")
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    return out


def eh_parede(px):
    return (px.max(axis=-1) <= 45) & ((px.max(axis=-1).astype(int) - px.min(axis=-1)) <= 8)


def parede_grossa(chapada):
    """Paredes da base chapada sem os traços finos (bordas e diagonais dos armários, linhas do PDF)."""
    return cv2.morphologyEx(eh_parede(chapada).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0


def modelo_sombra(r):
    """Sombra suave e crescente em d (1 = sem sombra), ajustada à razão medida r(d), d >= 1:
    s(d) = 1 - A * max(0, 1 - (d - 1) / L) ** p. O tom de cada régua do piso não entra no modelo
    e fica na imagem."""
    d = np.arange(1, len(r), dtype=np.float32)
    A = np.arange(0.0, 0.81, 0.01)[:, None, None, None]
    L = np.arange(1.0, len(r) + 0.1, 0.5)[None, :, None, None]
    P = np.array([0.6, 0.8, 1.0, 1.3, 1.7, 2.2, 3.0])[None, None, :, None]
    s = 1 - A * np.clip(1 - (d - 1) / L, 0, 1) ** P
    e = ((s - r[1:]) ** 2).sum(axis=-1)
    i = np.unravel_index(np.argmin(e), e.shape)
    return np.concatenate([[1.0], s[i]])


def armarios(out, chapada):
    """Armários até o teto: tampo em areia, sem sombra no piso; contorno nas faces livres."""
    q = ARMARIO
    img = cv2.imread(str(q["fonte_areia"][0]))
    fx0, fy0, fx1, fy1 = q["fonte_areia"][1]
    t = img[fy0:fy1, fx0:fx1]
    retangulos = [tuple(int(round(v)) + d for v, d in zip(r, q["ajuste"].get(nome, (0, 0, 0, 0))))
                  for nome, r in ARMARIOS]
    ocupado = np.zeros(out.shape[:2], bool)
    for x0, y0, x1, y1 in retangulos:
        ocupado[y0:y1, x0:x1] = True
    grossa = parede_grossa(chapada)
    branco = chapada.min(axis=-1) >= 245
    piso = ~branco & ~grossa & ~ocupado                    # o que pode ter a sombra do motor
    D = q["faixa"]
    lados = {"esquerda": (slice(None), 0), "direita": (slice(None), -1), "cima": (0, slice(None)),
             "baixo": (-1, slice(None))}
    # sombra de todas as faces, medida no render antes do retoque; onde duas se sobrepõem (cantos
    # internos) vale a mais escura, sem somar (sombra sobre sombra não escurece mais)
    S = np.ones(out.shape, np.float32)
    orig = out.copy()
    relatorio, bordas = [], []
    for (nome, _), (x0, y0, x1, y1) in zip(ARMARIOS, retangulos):
        faces = {"cima": (y0 - 1, (x0, x1), "y", -1), "baixo": (y1, (x0, x1), "y", 1),
                 "esquerda": (x0 - 1, (y0, y1), "x", -1), "direita": (x1, (y0, y1), "x", 1)}
        livres, sombras = [], []
        for lado, (c0, (a, b), eixo, passo) in faces.items():
            fora = [c0 + passo * k for k in range(0, 3)]
            g = grossa[fora, a:b] if eixo == "y" else grossa[a:b, fora]
            oc = ocupado[c0, a:b] if eixo == "y" else ocupado[a:b, c0]
            if g.mean() > 0.5 or oc.mean() > 0.5:
                continue
            livres.append(lado)
            pi = piso[fora, a:b] if eixo == "y" else piso[a:b, fora]
            if pi.mean() < 0.5 or (nome, lado) in q["manter_piso"]:
                continue

            def mascara(k, a, b):
                """Piso na linha k da faixa; nas 2 primeiras (a borda, que a base marca com traço
                ou com o branco do armário) vale o piso da linha 2."""
                c, c2 = c0 + passo * k, c0 + passo * 2
                if eixo == "y":
                    m = piso[c, a:b] if k >= 2 else piso[c2, a:b] & ~grossa[c, a:b] & ~ocupado[c, a:b]
                else:
                    m = piso[a:b, c] if k >= 2 else piso[a:b, c2] & ~grossa[a:b, c] & ~ocupado[a:b, c]
                return c, m

            # perfil por canal: mediana ao longo da face (sem 2 px nas pontas), só no piso
            a2, b2 = a + 2, b - 2
            perfil = np.full((D, 3), np.nan, np.float32)
            for k in range(D):
                c, m = mascara(k, a2, b2)
                v = orig[c, a2:b2] if eixo == "y" else orig[a2:b2, c]
                if m.sum() >= 3:
                    perfil[k] = np.median(v[m].astype(np.float32), axis=0)
            lum = perfil.mean(axis=1)
            if np.isnan(lum[:4]).any():
                continue
            # patamar: onde o piso para de clarear (cresce menos de 2% nas 3 linhas seguintes)
            dp = next((d for d in range(2, D - 3) if np.nanmax(lum[d + 1:d + 4]) - lum[d] < 0.02 * lum[d]), D - 3)
            ref = np.nanmedian(perfil[dp:dp + 4], axis=0)
            r = perfil[:dp] / ref
            if np.nanmin(r[1:].mean(axis=1)) >= q["limiar"] and abs(r[0].mean() - 1) < 1 - q["limiar"]:
                continue
            s = np.ones((D, 3), np.float32)
            for ch in range(3):
                s[:dp, ch] = modelo_sombra(np.nan_to_num(r[:, ch], nan=1.0))
                s[0, ch] = r[0, ch]                       # borda: a razão medida (traço do motor)
            # sombra local, ponto a ponto ao longo da face (inclusive um pouco além das pontas, na
            # penumbra): a razão entre o perfil local e o mediano, normalizada pelo patamar (o tom
            # da régua), suavizada ao longo da face
            e0, e1 = max(a - q["alem"], 0), b + q["alem"]
            n = e1 - e0
            loc = np.full((dp + 4, n, 3), np.nan, np.float32)
            msk = np.zeros((dp + 4, n), bool)
            for k in range(dp + 4):
                c, m = mascara(k, e0, e1)
                v = orig[c, e0:e1] if eixo == "y" else orig[e0:e1, c]
                loc[k][m] = v[m]
                msk[k] = m
            med = np.concatenate([perfil[:dp], np.repeat(ref[None], 4, axis=0)])
            Q = loc / med[:, None, :]
            Q = Q / np.nanmedian(Q[dp:], axis=0, keepdims=True)
            Qs = np.ones_like(Q)
            h2 = q["suave"]
            for k in range(dp):                           # mediana móvel: guarda a borda da penumbra
                for i in range(n):
                    j = Q[k, max(i - h2, 0):i + h2 + 1]
                    j = j[np.isfinite(j).all(axis=1)]
                    if len(j):
                        Qs[k, i] = np.median(j, axis=0)
            dentro = np.zeros(n, bool)
            dentro[a - e0:b - e0] = True
            for k in range(1, dp):
                c, m = mascara(k, e0, e1)
                sl = np.clip(s[k][None] * Qs[k], 0.25, 1.0)
                alvo = S[c, e0:e1] if eixo == "y" else S[e0:e1, c]
                alvo[m] = np.minimum(alvo[m], sl[m])
            # borda da face (o traço escuro ou claro do motor): repete a linha seguinte, já sem sombra
            c, m = mascara(0, a, b)
            bordas.append((eixo, c, c + passo, a, b, m))
            sombras.append(f"{lado} ({1 - s[1:].mean(axis=1).min():.0%}, {dp} px)")
        relatorio.append((nome, livres, sombras))
    out[:] = np.clip(out.astype(np.float32) / S, 0, 255).astype(np.uint8)
    for eixo, c, c1, a, b, m in bordas:
        if eixo == "y":
            out[c, a:b][m] = out[c1, a:b][m]
        else:
            out[a:b, c][m] = out[a:b, c1][m]

    areia = t.reshape(-1, 3).astype(np.float32).mean(axis=0)
    Y = orig.astype(np.float32).mean(axis=2)

    def veio(x0, y0, x1, y1):
        """Veio do armário do render: a luminância sobre a dela mesma desfocada (sem o degradê)."""
        y = Y[y0:y1, x0:x1]
        base = cv2.GaussianBlur(y, (0, 0), q["sigma_veio"], borderType=cv2.BORDER_REFLECT)
        return np.clip(y / np.maximum(base, 1), *q["veio_lim"])

    for (nome, livres, sombras), (x0, y0, x1, y1) in zip(relatorio, retangulos):
        h, w = y1 - y0, x1 - x0
        if nome in q["sem_veio"]:
            vx0, vy0, vx1, vy1 = q["veio_emprestado"]
            v = veio(vx0, vy0, vx1, vy1)
            v = np.concatenate([v, v[::-1]] * (h // (2 * v.shape[0]) + 1), axis=0)[:h]
            v = np.concatenate([v, v[:, ::-1]] * (w // (2 * v.shape[1]) + 1), axis=1)[:, :w]
        else:
            v = veio(x0, y0, x1, y1)
        reg = areia[None, None] * v[..., None]
        borda = np.zeros((h, w), bool)
        for lado in livres:
            borda[lados[lado]] = True
        reg[borda] *= q["contorno"]
        m = ~grossa[y0:y1, x0:x1]
        alvo = out[y0:y1, x0:x1]
        alvo[m] = np.clip(reg[m], 0, 255).astype(np.uint8)
        print(f"    {nome}: {w}x{h} px em areia ({'veio emprestado' if nome in q['sem_veio'] else 'veio do render'}); "
              f"contorno: {', '.join(livres) or '-'}; sombra tirada: {', '.join(sombras) or '-'}")
    return out


def piso_sob_armario(out, chapada):
    q = PISO_SOB_ARMARIO
    grossa = parede_grossa(chapada)
    fontes = []
    for x0, y0, x1, y1 in q["fontes"]:
        f = out[y0:y1, x0:x1].astype(np.float32)
        fontes += [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    ref = np.mean([f.reshape(-1, 3).mean(axis=0) for f in fontes], axis=0)
    rects = dict((nome, r) for nome, r in ARMARIOS)
    for nome, H, parede, protegidos in q["faixas"]:
        ax0, _, ax1, ay1 = rects[nome]
        ajuste = ARMARIO["ajuste"].get(nome, (0, 0, 0, 0))
        cx0, cx1, cy1 = int(round(ax0)) + ajuste[0], int(round(ax1)) + ajuste[2], int(round(ay1)) + ajuste[3]
        x0, x1, y0, y1 = cx0 - H, cx1, cy1, cy1 + H
        tex = quilting(fontes, y1 - y0, x1 - x0, p=12, sobra=4, candidatos=500)[:y1 - y0, :x1 - x0]
        # sombra da parede (e só ela): fator por coluna medido logo abaixo da faixa
        baixo = out[y1:y1 + q["medida"], x0:x1].astype(np.float32).mean(axis=0)
        if parede:
            f = np.clip(baixo / ref, 0, 1)
            f = np.stack([np.convolve(f[:, c], np.ones(5) / 5, "same") for c in range(3)], axis=1)
            f[:2], f[-2:] = f[2], f[-3]
            tex = tex * f[None]
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        a = np.clip((xx - cx0 + (yy - cy1)) / q["penumbra"] + 0.5, 0, 1)     # borda diagonal
        a *= np.clip((y1 - 0.5 - yy) / q["emenda"], 0, 1)                    # emenda embaixo
        a[grossa[y0:y1, x0:x1]] = 0
        for px0, py0, px1, py1 in protegidos:
            a[max(py0 - y0, 0):max(py1 - y0, 0), max(px0 - x0, 0):max(px1 - x0, 0)] = 0
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + tex * a[..., None], 0, 255).astype(np.uint8)
        print(f"    {nome}: piso refeito embaixo ({x1 - x0}x{H} px), sem a sombra do armário")
    return out


def area_molhada(out):
    q = AREA_MOLHADA
    xs, ys = [x for x, _ in q["pontos"]], [y for _, y in q["pontos"]]
    jx0, jy0, jx1, jy1 = int(min(xs)) - 2, int(min(ys)) - 1, int(max(xs)) + 3, int(max(ys)) + 3
    h, w = jy1 - jy0, jx1 - jx0
    f = np.zeros((h * SS, w * SS), np.uint8)
    pts = np.array([[int(round((x - jx0) * SS)), int(round((y - jy0) * SS))] for x, y in q["pontos"]], np.int32)
    cv2.polylines(f, [pts], False, 255, max(1, int(round(q["larg_traco"] * SS))))
    a = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None] * q["forca_traco"]
    reg = out[jy0:jy1, jx0:jx1].astype(np.float32)
    out[jy0:jy1, jx0:jx1] = np.clip(reg * (1 - a) + np.array(q["traco"], np.float32) * a, 0, 255).astype(np.uint8)
    print("    área molhada da bancada da pia demarcada (lados livres: esquerda e embaixo)")
    return out


def inox(out):
    q = INOX
    x0, y0, x1, y1 = q["janela"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    Y = reg.mean(axis=2)
    a = np.clip((Y - q["lum"][0]) / (q["lum"][1] - q["lum"][0]), 0, 1)[..., None]
    ref = np.median(Y[a[..., 0] >= 1])
    rng = np.random.default_rng(q["semente"])
    riscos = cv2.GaussianBlur(rng.normal(0, 1, (1, x1 - x0)).astype(np.float32), (0, 0), 0.7)
    riscos = 1 + q["escovado"] * riscos / max(float(riscos.std()), 1e-6)
    aco = np.array(q["cor"], np.float32)[None, None] * (Y / ref)[..., None] * riscos[..., None]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + aco * a, 0, 255).astype(np.uint8)
    print("    eletrodomésticos da cozinha em inox (o armário do canto fica em areia)")
    return out


def porta_gas(out):
    q = PORTA_GAS
    x0, y0, x1, y1 = q["soleira"]
    n = y1 - y0
    out[y0:y1, x0:x1] = out[y1:y1 + n, x0:x1][::-1]       # piso do abrigo, em espelho
    yb = int(np.ceil(q["folhas"][1][3]))
    for k, f in enumerate(q["sombra"]):
        out[yb + k, x0:x1] = np.clip(out[yb + k, x0:x1] * f, 0, 255).astype(np.uint8)

    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0

    def px(v, o):
        return int(round((v - o) * SS))

    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def pintar(mascara, cor):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    lc = max(1, px(q["larg_contorno"], 0))
    for fx0, fy0, fx1, fy1 in q["folhas"]:
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(m, (px(fx0, wx0), px(fy0, wy0)), (px(fx1, wx0), px(fy1, wy0)), 255, -1)
        pintar(m, q["folha"])
    for mx0, mx1 in q["montantes"]:
        fy0, fy1 = next((f[1], f[3]) for f in q["folhas"] if f[0] - 0.01 <= mx0 and mx1 <= f[2] + 0.01)
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(m, (px(mx0, wx0), px(fy0, wy0)), (px(mx1, wx0), px(fy1, wy0)), 255, -1)
        pintar(m, q["montante"])
    m = np.zeros((h * SS, w * SS), np.uint8)
    for fx0, fy0, fx1, fy1 in q["folhas"] + q["batentes"]:
        cv2.rectangle(m, (px(fx0, wx0), px(fy0, wy0)), (px(fx1, wx0), px(fy1, wy0)), 255, lc)
    pintar(m, q["contorno"])
    m = np.zeros((h * SS, w * SS), np.uint8)
    for bx0, by0, bx1, by1 in q["batentes"]:
        cv2.rectangle(m, (px(bx0, wx0), px(by0, wy0)), (px(bx1, wx0), px(by1, wy0)), 255, -1)
    pintar(m, q["contorno"])
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    abrigo de gás: soleira do motor fora; porta de correr do PDF (duas folhas em dois planos)")
    return out


def carros(out):
    q = CARROS
    for nome, (x0, y0, x1, y1), curva, cor in q["carros"]:
        reg = out[y0:y1, x0:x1].astype(np.float32)
        Y = reg.mean(axis=2)
        frio = np.abs(reg[..., 2] - reg[..., 0]) < q["quente"]          # o granito é quente (R > B)
        sil = ((frio & (Y > q["lum_min"])) | (Y > q["claro"])).astype(np.uint8)   # o granito nunca é tão claro
        sil = cv2.morphologyEx(sil, cv2.MORPH_CLOSE, np.ones((q["fecho"], q["fecho"]), np.uint8))
        cont, _ = cv2.findContours(sil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        sil = np.zeros_like(sil)
        cv2.drawContours(sil, [max(cont, key=cv2.contourArea)], -1, 1, -1)
        sil = cv2.dilate(sil, np.ones((3, 3), np.uint8))         # a borda misturada com o piso também
        lanterna = (reg[..., 2] - reg[..., 0] > q["lanterna"][0]) & (reg[..., 2] > q["lanterna"][1])
        a = cv2.GaussianBlur((sil * ~lanterna).astype(np.float32), (0, 0), 0.6)[..., None]
        topo = np.percentile(Y[sil > 0], 97)
        if curva[0] == "escurecer":
            _, base, faixa, ex = curva
            Yn = base + faixa * np.clip(Y / topo, 0, 1) ** ex
            Yn += q["reflexo"] * np.clip(Y - topo, 0, None)
        else:
            _, ini_, fim_, forca = curva
            s = np.clip((Y - ini_) / (fim_ - ini_), 0, 1)
            Yn = Y + forca * s * s * (3 - 2 * s) * (250 - Y)
        lo, hi = q["cor_lum"]
        sc = np.clip((Y - lo) / (hi - lo), 0, 1)[..., None]
        unid = np.array(cor, np.float32)[None, None]
        novo = Yn[..., None] * (1 + sc * (unid - 1))
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + novo * a, 0, 255).astype(np.uint8)
        print(f"    carro da {nome}: curva {curva[0]}, cor {cor}")
    return out


def lote(out, base):
    q = LOTE
    (c0, c1), (b0, b1) = q["muro_cima"], q["muro_baixo"]
    xg, xc = q["x_grama"], q["x_cantos"]
    f0, f1 = q["faixa_muro"]
    d = q["desloc"]
    out[c1:b0, f0:f1] = out[c1:b0, f0 + d:f1 + d]                 # muro preto -> grama de logo à direita
    out[c0:c1, xg - 2:xc] = out[c0:c1, q["coluna_cima"]][:, None]   # muro de cima sem as folhas
    out[b0:b1, xg - 2:xc] = out[b0:b1, q["coluna_baixo"]][:, None]  # muro de baixo sem as folhas
    y0, y1 = q["y"]
    fora = np.zeros(out.shape[:2], bool)
    fora[y0:y1, :xg] = True
    fora[y0:c0, :xc] = True
    fora[b1:y1, :xc] = True
    out[fora] = base[fora]
    print(f"    muro da esquerda fora (grama até a linha tracejada); fora do lote: base ({int(fora.sum())} px)")
    return out


def faixa_x(out, A):
    q = FAIXA_X
    for (a, b), (c, d) in q["muro"]:
        out[c:d, a:b] = np.median(out[c:d, a:b], axis=1).astype(np.uint8)[:, None]
    hx0, hy0, hx1, hy1 = q["hall"]
    reg = out[hy0 - 4:hy1 + 4, hx0 - 4:hx1]
    verde = (reg[..., 1].astype(int) - reg[..., 2] > 8).astype(np.uint8)
    verde[:4], verde[-4:], verde[:, :4] = 0, 0, 0
    cx0, cy0, cx1, cy1 = q["contorno_folha"]
    sub = reg[cy0 - hy0 + 4:cy1 - hy0 + 4, cx0 - hx0 + 4:cx1 - hx0 + 4]
    verde[cy0 - hy0 + 4:cy1 - hy0 + 4, cx0 - hx0 + 4:cx1 - hx0 + 4] |= (sub.mean(axis=2) < q["escuro"]).astype(np.uint8)
    verde = cv2.dilate(verde, np.ones((3, 3), np.uint8))
    out[hy0 - 4:hy1 + 4, hx0 - 4:hx1] = cv2.inpaint(np.ascontiguousarray(reg), verde, 3, cv2.INPAINT_TELEA)
    x0, y0, x1, y1 = q["ret"]
    h, w = y1 - y0, x1 - x0
    g = grama(out, q["fonte_grama"], h, w)
    f = np.ones((h, w), np.float32)
    for (a, b), n, forca in q["sombra_cima"]:
        for d in range(n):
            f[d, a - x0:b - x0] = np.minimum(f[d, a - x0:b - x0], 1 - forca * (1 - d / n) ** 1.5)
    xd, n, forca = q["sombra_dir"]
    for d in range(n):
        f[:, xd - x0 - 1 - d] = np.minimum(f[:, xd - x0 - 1 - d], 1 - forca * (1 - d / n) ** 1.5)
    out[y0:y1, x0:x1] = np.clip(g * f[..., None], 0, 255).astype(np.uint8)
    out = linhas_pdf(out, A, q["ret"], q["linhas"])
    print(f"    faixa com X: canteiro do motor vira grama ({w}x{h} px) com as linhas do PDF")
    return out


def acesso(out):
    q = ACESSO
    x0, y0, x1, y1 = q["ret"]
    h, w = y1 - y0, x1 - x0
    f = []
    for a, b, c, d in q["fonte"]:
        g = out[b:d, a:c].astype(np.float32)
        f += [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    tex = quilting(f, h, w, p=16, sobra=5, candidatos=600)[:h, :w]
    tex = tex / tex.reshape(-1, 3).mean(axis=0)
    px0, px1 = q["perfil_x"]
    perfil = out[y0:y1, px0:px1].astype(np.float32).mean(axis=1)
    perfil = np.stack([np.convolve(np.pad(perfil[:, c], 2, mode="edge"), np.ones(5) / 5, "valid") for c in range(3)],
                      axis=1)
    out[y0:y1, x0:x1] = np.clip(tex * perfil[:, None, :], 0, 255).astype(np.uint8)
    print(f"    ponta do acesso: {w}x{h} px de granito no lugar do cinza")
    return out


def projecao_granito(out, janela):
    """Máscara (0/1) do granito do render na janela: escuro e quente (sem parede preta, sem madeira)."""
    x0, y0, x1, y1 = janela
    reg = out[y0:y1, x0:x1].astype(np.float32)
    Y = reg.mean(axis=2)
    lo, hi = PROJECAO_GARAGEM["granito_lum"]
    return ((Y > lo) & (Y < hi) & (reg[..., 2] > reg[..., 0])).astype(np.float32)


def projecao_garagem(out, A):
    q = PROJECAO_GARAGEM
    gran = projecao_granito(out, q["janela"])
    out = linhas_pdf(out, A, q["janela"], q["linhas"], mascara=gran)
    print("    projeção tracejada com X sobre a entrada da garagem")
    return out


def arcos_no_granito(out, A, chapada):
    """Como na Casa C: os arcos das portas (curvas da layer ARQ_PAREDE) que caem sobre o granito
    são redesenhados em cinza e traço fino (pedido do usuário na Casa C), só onde o piso é granito."""
    q = ARCOS_GRANITO
    gran = (np.abs(chapada.astype(np.int32) - np.array(q["granito"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    gran = cv2.morphologyEx(gran, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))   # fecha os traços finos
    pg, p2r = pdf_cadeia(A, out.shape)
    n = 0
    for d in pg.get_drawings():
        if d.get("layer") != "ARQ_PAREDE" or not any(it[0] == "c" for it in d["items"]):
            continue
        r = d["rect"]
        (x0, y0), (x1, y1) = p2r(r.x0, r.y0), p2r(r.x1, r.y1)
        x0, y0, x1, y1 = int(x0) - 2, int(y0) - 2, int(np.ceil(x1)) + 3, int(np.ceil(y1)) + 3
        if max(x1 - x0, y1 - y0) < q["min_px"] or x0 < 0 or y0 < 0 or x1 > out.shape[1] or y1 > out.shape[0]:
            continue
        g = gran[y0:y1, x0:x1]
        if g.mean() < q["fracao"]:
            continue
        h, w = y1 - y0, x1 - x0
        f = np.zeros((h * SS, w * SS), np.uint8)
        for it in d["items"]:
            if it[0] != "c":
                continue
            pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
            tt = np.linspace(0, 1, 60)[:, None]
            curva = (1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1] + 3 * (1 - tt) * tt ** 2 * pp[2] + tt ** 3 * pp[3]
            pts = np.round((curva - [x0, y0]) * SS).astype(np.int32)
            cv2.polylines(f, [pts], False, 255, max(1, int(round(q["larg"] * SS))), cv2.LINE_AA)
        a = (cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * g)[..., None]
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.array(q["cor"], np.float32) * a, 0, 255).astype(np.uint8)
        n += 1
        print(f"      arco em ({(x0 + x1) / 2:.0f}, {(y0 + y1) / 2:.0f})")
    print(f"    {n} arcos de porta sobre o granito em cinza")
    return out


def granito_chapada(chapada, janela):
    """Máscara (0/1) do granito pela base chapada (cor exata), fechada nos traços finos; vale também
    onde o render pôs sombra funda no granito."""
    x0, y0, x1, y1 = janela
    q = ARCOS_GRANITO
    g = (np.abs(chapada.astype(np.int32) - np.array(q["granito"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    g = cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return g[y0:y1, x0:x1].astype(np.float32)


def area_descoberta(out, A, chapada):
    q = AREA_DESCOBERTA
    x0, y0, x1, y1 = q["vaso"]
    pad = 10
    ret = (x0 - pad, y0 - pad, x1, y1 + pad)
    m = np.zeros((ret[3] - ret[1], ret[2] - ret[0]), bool)
    m[pad:pad + y1 - y0, pad:pad + x1 - x0] = True
    out = apagar(out, ret, m, q["fonte_granito"], sigma=4.0)
    gran = granito_chapada(chapada, q["janela_x"])
    out = linhas_pdf(out, A, q["janela_x"], PROJECAO_GARAGEM["linhas"] | {"curtos": {}}, mascara=gran)
    print("    área descoberta: vaso inventado fora; X tracejado do PDF")
    return out


def tanques(out):
    q = TANQUES
    x0, y0, x1, y1 = q["cuba_motor"]
    pad = 14                                            # luz da bancada dos dois lados
    ret = (x0 - pad, y0, x1 + pad, y1)
    m = np.zeros((y1 - y0, x1 - x0 + 2 * pad), bool)
    m[:, pad:pad + x1 - x0] = True
    out = apagar(out, ret, m, q["fonte_bancada"], sigma=9.0, borda=0)
    img = cv2.imread(str(q["fonte_tanques"][0]))
    a, b, c, d = q["fonte_tanques"][1]
    s = cv2.rotate(img[b:d, a:c], cv2.ROTATE_90_COUNTERCLOCKWISE)        # torneira (à direita) para cima
    tx, ty = q["em"]
    claro = s.mean(axis=2) >= 90                        # sem os px da parede da Casa B nas pontas
    alvo = out[ty:ty + s.shape[0], tx:tx + s.shape[1]]
    alvo[claro] = s[claro]
    print(f"    tanques: cuba do motor fora; os dois tanques da Casa B ({s.shape[1]}x{s.shape[0]} px) em ({tx}, {ty})")
    return out


def dce(out, chapada):
    q = DCE
    x0, y0, x1, y1 = q["piso"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    Y = reg.mean(axis=2)
    piso = ~parede_grossa(chapada)[y0:y1, x0:x1] & (Y > 25)
    w = piso.astype(np.float32)
    campo = cv2.GaussianBlur(Y * w, (0, 0), sigmaX=1.5, sigmaY=5) / np.maximum(cv2.GaussianBlur(w, (0, 0), sigmaX=1.5, sigmaY=5), 1e-3)
    a, b = q["piso_aceso_x"]
    aceso = np.median(Y[:, a - x0:b - x0], axis=1)
    aceso = cv2.GaussianBlur(aceso[:, None], (1, 0), sigmaX=0.1, sigmaY=4).ravel()
    f = np.clip(campo / aceso[:, None], 0.2, 1.0)
    f[:, :q["sombra_x0"] - x0] = 1.0
    reg[piso] /= f[piso][:, None]
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)

    ref = np.median(out[300:328, 1300:1336].reshape(-1, 3).astype(np.float32), axis=0)   # piso já corrigido
    for lx0, ly0, lx1, ly1 in q["L"]:
        tex = textura(out, q["fonte_piso"], ly1 - ly0, lx1 - lx0, p=12)
        alvo = out[ly0:ly1, lx0:lx1]
        m = ~parede_grossa(chapada)[ly0:ly1, lx0:lx1]
        alvo[m] = np.clip(tex * ref, 0, 255).astype(np.uint8)[m]

    img = cv2.imread(str(q["fonte"]))
    fx0, fy0, fx1, fy1 = q["fonte_cama"]
    c0, c1 = q["cortar_cobertor"]
    cama = np.concatenate([img[fy0:fy1, fx0:c0], img[fy0:fy1, c1:fx1]], axis=1)
    cama = cv2.rotate(cama, cv2.ROTATE_90_CLOCKWISE)                 # cabeceira (à esquerda) em cima
    for (bx0, by0, bx1, by1), peca in ((q["cama"], cama), (q["criado"], None)):
        if peca is None:
            sx0, sy0, sx1, sy1 = q["fonte_criado"]
            peca = img[sy0:sy1, sx0:sx1]
        out[by0:by1, bx0:bx1] = cv2.resize(peca, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)
        for k, s in enumerate(q["sombra"]):                         # sombra curta: esquerda e embaixo
            out[by0 + 2:by1 + 1, bx0 - 1 - k] = np.clip(out[by0 + 2:by1 + 1, bx0 - 1 - k] * s, 0, 255).astype(np.uint8)
            if by1 + k < 348:
                out[by1 + k, bx0 - 1:bx1 - 1] = np.clip(out[by1 + k, bx0 - 1:bx1 - 1] * s, 0, 255).astype(np.uint8)
    print("    DCE: marcenaria do motor vira piso; cama de solteiro e criado-mudo do PDF")
    return out


def cooktops(out):
    q = COOKTOPS_D
    x0, y0, x1, y1 = q["gourmet_motor"]
    pad = 10
    ret = (x0 - pad, y0, x1 + pad, y1 + pad)          # em cima já é a borda da bancada: a luz vem só dela
    m = np.zeros((ret[3] - ret[1], ret[2] - ret[0]), bool)
    m[:y1 - y0, pad:pad + x1 - x0] = True
    out = apagar(out, ret, m, q["fonte_quartzo"], sigma=6.0, borda=0)
    img = cv2.imread(str(q["fonte"][0]))
    a, b, c, d = q["fonte"][1]
    s = img[b:d, a:c]
    for nome, (cx0, cy0, cx1, cy1) in q["caixas"]:
        out[cy0:cy1, cx0:cx1] = cv2.resize(s, (cx1 - cx0, cy1 - cy0), interpolation=cv2.INTER_AREA)
        print(f"    cooktop da {nome}: 5 bocas (2 em cima, 3 embaixo) em {cx1 - cx0}x{cy1 - cy0} px")
    return out


def bancada_gourmet(out):
    q = BANCADA_GOURMET
    x0, y0, x1, y1 = q["ret"]
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    Y = reg.mean(axis=2)
    rx0, ry0, rx1, ry1 = q["ref"]
    ref = np.median(out[ry0:ry1, rx0:rx1].astype(np.float32).mean(axis=2))
    perfil = np.median(Y[:, rx0 - x0:rx1 - x0], axis=1) / ref
    dx0, dy0, dx1, dy1 = q["ref_dir"]
    luz2 = cv2.GaussianBlur(Y, (0, 0), 1.2) / np.median(out[dy0:dy1, dx0:dx1].astype(np.float32).mean(axis=2))
    g0, g1 = q["geladeira"]
    tr = np.clip((np.arange(x0, x1) - g0) / (g1 - g0), 0, 1)[None, :]
    luz = perfil[:, None] * (1 - tr) + luz2 * tr
    cor = np.median(np.concatenate([out[b:d, a:c].reshape(-1, 3) for a, b, c, d in q["fonte_quartzo"]]).astype(np.float32),
                    axis=0)
    tex = textura(out, q["fonte_quartzo"], h, w)
    novo = tex * cor * luz[..., None]
    cx0, cy0, cx1, cy1 = q["cuba"]
    m = np.ones((h, w), bool)
    sub = reg[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    m[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] = (sub[..., 2] - sub[..., 0]) > 28     # na caixa da cuba, só a madeira
    reg[m] = novo[m]
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    bancada da pia da gourmet em quartzo (a cuba fica)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] porta pivotante principal")
    out = pivotante(out)
    print("[2] chuveiros do banho master")
    out = chuveiros_bhm(out)
    print("[3] armários até o teto")
    _, chapada, _ = alinhar_base(orig)
    out = armarios(out, chapada)
    out = piso_sob_armario(out, chapada)
    print("[4] área molhada da bancada da pia")
    out = area_molhada(out)
    print("[5] eletrodomésticos em inox")
    out = inox(out)
    print("[6] porta de correr do abrigo de gás")
    out = porta_gas(out)
    print("[7] carros em tons diferentes")
    out = carros(out)

    print("[8] erros 1 e 2: muro inventado à esquerda e plantas fora do lote")
    base, _, _ = alinhar_base(orig)
    out = lote(out, base)
    print("[9] erro 3: faixa com X à direita do hall")
    _, _, A = alinhar_base(orig)
    out = faixa_x(out, A)
    print("[10] erro 4: ponta do acesso de veículos em granito")
    out = acesso(out)
    print("[11] erro 5: projeção com X sobre a entrada da garagem")
    out = projecao_garagem(out, A)
    print("[12] erro 6: arcos das portas sobre o granito")
    out = arcos_no_granito(out, A, chapada)
    print("[13] erro 7: vaso inventado e X da área descoberta")
    out = area_descoberta(out, A, chapada)
    print("[14] erro 8: dois tanques")
    out = tanques(out)
    print("[15] erro 9: cama e criado-mudo do DCE")
    out = dce(out, chapada)
    print("[16] erros 10 e 11: cooktops da ilha e da gourmet")
    out = cooktops(out)
    print("[17] erro 12: bancada da pia da gourmet em quartzo")
    out = bancada_gourmet(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

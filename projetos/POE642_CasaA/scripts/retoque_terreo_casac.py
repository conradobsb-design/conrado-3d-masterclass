#!/usr/bin/env python3
"""Retoque sem IA do render do Térreo da Casa C (prompt v3). A imagem final é o render.

Os erros são corrigidos um a um, na ordem combinada com o usuário.

1. Chuveiros de teto: o motor deixou os boxes vazios (e, na ducha entre os lavabos, um ralo redondo). Cada um recebe a placa quadrada aprovada
   na Casa A (banho 3 do 1º Pavimento, 11 x 11 px, a mesma escala), no centro do símbolo do PDF
   (quadrado de 20 cm da layer ARQ_LOUÇAS E METAIS, levado ao render pela base alinhada).
2. Plantas fora do lote: o motor deixou palmeiras passando da linha tracejada em todo o lado
   esquerdo e do muro nos cantos de cima e de baixo à esquerda. Fora do lote volta a ser o que a
   base tem (fundo branco e linha tracejada); os dois trechos de muro cobertos pelas folhas são
   refeitos com o próprio muro do render, um pouco à direita. A vegetação termina no lote.
3. Jardins de inverno: as plantas passavam dos vidros, sobre o piso, a caixa do elevador e os
   próprios vidros. Ficam só dentro das floreiras (geometria medida no render). Os vidros e a
   parede de baixo do elevador são refeitos com o perfil de um trecho limpo do mesmo elemento; as
   faixas de piso com folha ou sombra são trocadas pelo piso limpo logo ao lado, com emenda suave.
   As portas de correr de vidro (folhas em dois planos dos lados, embaixo e em cima do jardim 2)
   vêm da base alinhada, que coincide com o render nos montantes; entre as folhas, piso do lado de
   fora e floreira do lado de dentro.
4. Cozinha: o motor fez as bancadas e a ilha no granito do piso, com uma cuba só. Bancadas e ilha
   ficam no quartzo claro da bancada gourmet do próprio render (image quilting), com o cooktop e as
   banquetas como estão; os dois armários altos (retângulo com diagonal no PDF: o de baixo à
   esquerda e o junto à geladeira) viram o tampo do armário em marcenaria areia, tecida do painel
   do quarto, com contorno nas faces livres e sem a diagonal, como os armários das Casas A e B;
   entre a geladeira e o armário volta o vão de piso do PDF; as duas
   cubas do PDF são desenhadas como as do lavatório gourmet da Casa B, com a torneira do lado da
   parede. A área molhada da bancada das cubas (retângulo da layer ARQ_BANCADAS) é demarcada com
   um traço cinza fino nos lados livres (esquerda, direita e embaixo).
5. Quarto externo: o motor trocou a cama de solteiro do PDF por dois eletrodomésticos e o
   criado-mudo por uma caixa branca. A cama vem de uma das camas de solteiro do próprio render
   (quarto 2), virada para a cabeceira ficar na parede da direita como no PDF, encurtada no
   cobertor e ajustada à largura do PDF; o criado-mudo vem do criado-mudo da suíte. O piso que
   ficou à mostra (a sombra do eletrodoméstico) vem do piso limpo ao lado, e cada peça ganha a
   sombra curta que as camas do render têm.
6. Tanques da área de serviço: a bancada tinha saído no granito do piso, com os tanques escuros.
   A bancada fica no mesmo quartzo da cozinha e os dois tanques são os aprovados da Casa B (louça
   branca, torneira do lado da parede), na mesma escala, nas posições da base alinhada.
7. Estar: o motor pôs duas poltronas a mais acima do tapete (no PDF só há as duas da esquerda).
   Elas saem com a sombra. O piso volta continuando os veios verticais de cima, em espelho; a
   borda de cima do tapete vem do trecho limpo da mesma borda à direita; o tapete logo abaixo vem
   das linhas limpas de baixo, nas mesmas colunas. Emenda suave dos lados.
8. Estar, conforme o PDF: o aparador comprido que o motor inventou abaixo do sofá sai (vira
   piso); a mesa de centro, que o motor fez numa peça só, vira as duas do PDF, uma sobre a outra
   (a emenda é refeita com a borda de baixo, a sombra e a borda de cima da própria mesa); as
   mesas laterais quadradas viram as orgânicas do PDF (duas, a menor atrás), com a forma tirada
   do PDF levado ao render, no tampo de madeira da mesa de centro, com contorno e sombra curta.
   O piso que volta é tecido (image quilting) do travertino limpo do próprio estar; o trecho da
   cortina junto à janela, que ficava sob a ponta do aparador, fica como no render.
9. Gourmet: o motor pôs cinco banquetas embaixo da bancada do cooktop (no PDF não há nenhuma).
   Elas saem com a sombra. O piso volta continuando os veios verticais de baixo, em espelho, e a
   sombra da bancada (3 linhas abaixo da borda) é refeita com o perfil medido nos trechos limpos
   da mesma borda, dos dois lados. Emenda suave dos lados.
10. Cooktops: o motor fez os dois com 6 bocas; no PDF os dois têm 5. Na gourmet sai a boca do
   meio de cima (fica o tampo do próprio cooktop). O da ilha da cozinha é o mesmo desenho girado
   (3 bocas na coluna da esquerda, 2 na da direita): vira o cooktop da gourmet já corrigido,
   girado 90° e levado à caixa do da ilha.
11. Box do BH master 2: o motor deixou o vão da esquerda sem a porta de giro. Ela volta como no
   PDF (layer ARQ_BANCADAS, levada ao render pela mesma cadeia da base): a folha de vidro aberta
   junto à parede de cima e o arco do giro até o batente de baixo, no traço das portas do render.
   O arco passa por baixo do chuveiro de teto (que fica por cima). O vão ao lado do chuveiro
   (retângulo com dois X tracejados na layer DOC_LINHAS E PROJEÇÕES, algo acima do plano de corte)
   fica tracejado sobre o piso, como no PDF: os X vêm do próprio PDF levado ao render e o lado
   livre (o da esquerda, os outros são parede) ganha um contorno tracejado no mesmo traço.
12. Escada estreita abaixo do box: no PDF são 10 degraus (do 11 ao 20, subindo para a direita);
   o motor fez 6. As 5 arestas internas do motor saem (as colunas viram o piso limpo do degrau ao
   lado) e entram 9, repartidas por igual entre a primeira e a última aresta do render, com o
   perfil de sombra das arestas do próprio render, um pouco mais estreito para o degrau menor.
13. Elevador: o motor fez a caixa no travertino do hall. A caixa fica branca e a cabine, no tom
   da cabine do Subsolo da Casa B aprovado (pedido do usuário): é a própria cabine de lá (sem a
   soleira), girada para a porta ficar à esquerda e levada à cabine do PDF (quase a mesma escala).
14. Chuveiro externo (no pisante junto ao muro de baixo): o motor fez uma cruz escura, que ainda
   atravessava o muro. A cruz sai (a barra deitada vira a pedra de cima do mesmo pisante; a em pé
   vira as colunas limpas ao lado, que já têm a pedra, a borda, a grama e o muro). Entra o
   chuveiro do PDF (ARQ_LOUÇAS E METAIS): a ducha quadrada de ~19 cm, na placa aprovada da Casa A
   reduzida, o braço cromado até o muro e a canopla.
15. Degraus largos (descem para o pátio, para cima na imagem): a seta da base sai (as colunas
   viram as limpas ao lado) e a sombra de cada aresta, que o motor pôs do lado de baixo (lia como
   subida), passa para o lado de cima, com o perfil da mesma escada no Subsolo da Casa C aprovado:
   tira-se o perfil do motor (medido em cada aresta) e aplica-se o do Subsolo. As duas arestas em
   L também: a sombra fica do lado de fora (à esquerda, o nível mais baixo).
16. Aparador do hall de entrada: o motor o fez comprido até a ponta da parede. No PDF ele termina
   antes e ao lado fica uma mesa redonda. O aparador é encurtado (a ponta da direita, com a borda e
   a sombra, vem para o fim do PDF), o resto volta a ser travertino (veios de baixo, em espelho) e
   entra a mesa redonda do PDF, no tampo de madeira do próprio aparador, com contorno e sombra.
17. Lavabo ao lado da adega: o motor fez duas cubas; no PDF a de cima é só bancada. O miolo da
   de cima vira a bancada lisa do trecho de baixo (mesmas colunas, com a borda da direita); a borda
   de cima da bancada e a cuba de baixo ficam. Adega: o móvel comprido de madeira junto à parede
   da direita não existe no PDF e vira o piso da adega (as colunas limpas, em espelho). O móvel do
   topo do lavabo (malva no PDF, que o motor pintou no granito do piso) vira marcenaria areia,
   como os armários da cozinha, com o contorno na face livre (embaixo).
18. Escritório: no vão da parede de cima é uma janela, não a porta de correr que o motor fez. A
   folha de correr sai (a borda de baixo da parede e o piso de madeira vêm do trecho da mesma
   parede à esquerda) e o vão recebe a janela das próprias janelas da parede da esquerda do
   escritório, girada (o lado de fora para cima), com dois panos e o montante no meio.
19. Cadeiras das escrivaninhas: o PDF tem cadeira na escrivaninha do Quarto 1, do quarto das duas
   camas e da suíte do canto; o motor fez as escrivaninhas sem elas. Entra a cadeira do próprio
   render (a de visitante do escritório, recortada por máscara sobre o piso), um pouco maior como a
   do PDF, girada para a escrivaninha e centrada no símbolo do PDF. A cadeira entra por cor; a
   sombra entra só como escurecimento (sem levar o tom do piso do escritório para o tapete). A
   frente da cadeira fica por baixo da escrivaninha (pedido do usuário): onde é tampo, fica o
   tampo; na faixa da sombra da escrivaninha, a cadeira recebe a mesma sombra.
20. BH master 1: o motor fez duas cubas soltas com a torneira na lateral (do lado da parede). No
   PDF é uma cuba esculpida longa: duas bacias com a torneira nas pontas (em cima e embaixo) e um
   trecho liso no meio. As cubas do motor saem (a bancada lisa entre elas é repetida em espelho)
   e entram as duas bacias do PDF, em louça branca, no desenho das cubas da cozinha; entre elas
   fica a pedra da bancada (pedido do usuário: o meio não é branco). No BH
   master 2 a cuba está certa, mas a torneira saiu na lateral; no PDF ela fica no meio da borda de
   cima: a cuba é redesenhada no mesmo lugar, com a torneira em cima.
21. Porta pivotante principal: o motor cortou a folha na soleira; no PDF ela vai de ponta a ponta,
   passando para o lado de fora até o arco. A folha é estendida com o próprio trecho dela (mesmas
   linhas) até o fim do PDF, e a ponta recebe o arremate da ponta de dentro, em espelho.
22. Arcos das portas sobre o granito: no granito marrom o arco escuro do motor não aparece. Os arcos
   das portas (curvas da layer ARQ_PAREDE) que caem sobre o granito são redesenhados em cinza claro,
   com a geometria do PDF levada ao render, só onde o piso é granito (cor exata da base chapada).
23. Bancos ao pé das camas: o PDF tem banco ao pé da cama da suíte master, do Quarto 1, do Quarto 3
   e das duas camas de solteiro do Quarto 2; o motor não fez os bancos e esticou as camas dos
   Quartos 1, 2 e 3 por cima deles. Essas camas voltam ao comprimento do PDF (a ponta da cama, com
   a borda e a sombra, vem para o pé do PDF; o vão vira o tapete ou o piso ao lado) e entram os
   bancos do Térreo da Casa B aprovado (pedido do usuário): o de duas almofadas nas camas de casal
   e o liso nas de solteiro, levados ao retângulo do PDF, com a sombra deles.
24. Vaso do lavabo masculino: o motor fez um vaso cinza, fora do padrão dos outros. Ele sai (o piso
   vem do trecho limpo à esquerda, nas mesmas linhas) e entra o vaso suspenso branco do lavabo ao
   lado da adega, espelhado (a parede fica à direita) e levado ao retângulo do PDF.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_terreo_casac.py RENDER.webp --saida PASTA --nome NOME
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
from retoque_terreo_casab import cuba  # noqa: E402
from texturizar_base import quilting  # noqa: E402

BASE = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Terreo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Terreo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Terreo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - TÉRREO - CASA C.pdf"
CONFIG = RAIZ / "POE642_CasaC/config_bases.json"
VIDRO = (211, 214, 214)                                  # BGR de #D6D6D3
# lote no render: linha tracejada da esquerda e muros de cima e de baixo
LOTE = {"x_esq": 155, "muro_cima": (24, 32), "muro_baixo": (952, 958)}
# trecho com folhas por cima dos muros (x) e coluna limpa de onde o muro é copiado
MURO_COBERTO = {"x": (150, 262), "coluna_limpa": 300}
# jardins de inverno no render: interiores (onde as plantas ficam), vidros e parede do elevador.
# Cada vidro/parede: faixa [x0, x1) x [y0, y1) e o perfil limpo (linha ou coluna) que a refaz.
JARDINS = {
    "interiores": [(924, 482, 1055, 615), (984, 424, 1057, 475)],      # onde as plantas ficam
    "faixas": [
        {"nome": "vidro esquerdo", "ret": (918, 482, 924, 615), "perfil": ("linha", 560)},
        {"nome": "vidro direito", "ret": (1055, 482, 1061, 615), "perfil": ("linha", 600)},
        {"nome": "vidro de baixo", "ret": (924, 616, 1055, 621), "perfil": ("coluna", 1040)},
        {"nome": "vidro de cima do jardim 2", "ret": (984, 419, 1057, 424), "perfil": ("coluna", 1040, 616)},
        {"nome": "parede de baixo do elevador", "ret": (918, 475, 984, 482), "perfil": ("coluna", 930)},
    ],
    # faixas de piso com folha ou sombra de folha: trocadas inteiras pelo piso limpo ao lado
    # (veios verticais: de lado à esquerda, de baixo para a faixa de baixo), com emenda suave
    "pisos": [
        ("à esquerda do jardim", (895, 478, 918, 626), (-22, 0)),
        ("abaixo do jardim", (916, 621, 1063, 635), (0, 14)),
        ("interior do elevador, embaixo", (936, 455, 978, 475), (0, -20)),
    ],
    "emenda": 3,
    # portas de vidro: faixa, deslocamento para dentro (floreira), eixo e limite da floreira
    # (do lado de dentro do limite é floreira; do lado de fora, piso)
    "portas": [
        ("esquerda", (914, 482, 927, 618), (13, 0), "x", 924),
        ("direita", (1048, 482, 1063, 618), (-15, 0), "x", 1054),
        ("embaixo", (919, 609, 1060, 624), (0, -15), "y", 614),
        ("em cima do jardim 2", (984, 416, 1057, 428), (0, 12), "y", 424),
    ],
}
# cozinha (geometria medida no render, conferida com o PDF levado ao render)
COZINHA = {
    # bancada de cima (das cubas), bancada da esquerda, ilha e bancada de baixo à direita
    "quartzo": [(1131, 131, 1283, 150), (1131, 150, 1147, 238), (1176, 188, 1213, 286),
                (1265, 281, 1283, 340)],
    "cooktop": (1192, 207, 1212, 239),          # fica, com o contorno escuro em volta
    # armários altos (o de baixo à esquerda e o junto à geladeira) e as faces livres (as que não
    # encostam em parede), onde vai o contorno
    "armarios": [((1131, 238, 1147, 323), ("cima", "direita")),
                 ((1265, 257, 1283, 281), ("cima", "esquerda", "baixo"))],
    # vão de piso entre a geladeira e o armário (no render era bancada): piso de 22 px à esquerda,
    # com a sombra junto ao armário igual à da bancada (fator por linha, até o armário), só da
    # coluna da sombra lateral da bancada para a direita
    "vao": ((1258, 251, 1283, 257), -22, (0.70, 0.59, 0.51), 1262),
    "cubas": [(1177, 135, 1197, 149), (1202, 135, 1222, 149)],
    # quartzo limpo da bancada gourmet (os dois lados do cooktop e o braço da esquerda)
    "fonte_quartzo": [(646, 566, 714, 596), (752, 566, 812, 596), (647, 507, 666, 560)],
    "fonte_areia": (690, 281, 744, 290),         # painel laqueado do quarto (liso)
    "contorno": 0.75,                            # face livre do armário (1 px)
    # área molhada da bancada das cubas (PDF, ARQ_BANCADAS): lados livres em traço cinza fino
    "area_molhada": (1146.75, 130.4, 1255.23, 148.17), "traco": (120, 128, 138), "larg_traco": 0.6,
    "forca_traco": 0.7,
}
# quarto externo (geometria da base chapada alinhada; paredes conferidas no render)
QUARTO_EXTERNO = {
    "cama": (1589, 389, 1650, 419),              # até a parede da direita e a de baixo
    "fonte_cama": (753, 189, 825, 222),          # cama de solteiro de cima do quarto 2 (cabeceira à esquerda)
    "cortar_cobertor": (796, 807),               # colunas do cobertor liso tiradas da fonte
    "criado": (1636, 369, 1650, 386),
    "fonte_criado": (733, 178, 747, 195),        # criado-mudo da suíte
    # piso: a sombra do eletrodoméstico à esquerda da cama e a borda de cima da caixa branca
    "pisos": [((1584, 386, 1590, 419), (-12, 0)), ((1636, 368, 1650, 369), (0, -3))],
    "sombra_cima": 0.91,                         # como em cima das camas do quarto 2
    "sombra_pe": 0.93,                           # no pé da cama (a ponta das camas do quarto 2)
}
# área de serviço: bancada dos tanques (até a parede da direita e a janela de baixo) e os dois
# tanques do Térreo aprovado da Casa B (contorno de fora e torneira, sem a coluna da parede),
# colados a partir do canto de cima à esquerda, na base alinhada (a torneira chega a 1 px da
# parede, como no PDF)
SERVICO = {
    "bancada": (1384, 177, 1406, 253),
    "fonte_tanques": (RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Terreo_v4_retocado.png", (1147, 763, 1165, 804)),
    "tanques_em": (1387, 182),
}
# estar: as duas poltronas a mais (com a sombra), a borda de cima do tapete e as fontes limpas
POLTRONAS = {
    "ret": (922, 669, 1005, 707),
    "piso_ate": 695,                    # acima: piso em espelho a partir da linha 669
    "borda_ate": 699,                   # 695-698: borda do tapete, do trecho limpo à direita
    "fonte_borda_x": (1008, 1050),
    "tapete_dy": 10,                    # 699-706: tapete das linhas de baixo, mesmas colunas
    "emenda": 3,
}
# estar, conforme o PDF (geometria do PDF levado ao render pela mesma cadeia da base)
ESTAR = {
    # aparador abaixo do sofá (não existe no PDF) e mesas laterais quadradas do motor, com a
    # sombra: viram piso. Emenda suave (esq, cima, dir, baixo) só onde encosta em piso limpo
    "piso": [((898, 834, 1042, 851), (2, 0, 2, 0)),
             ((889, 800, 911, 828), (2, 2, 0, 2)),
             ((1026, 800, 1049, 828), (0, 2, 2, 2))],
    "fonte_piso": [(880, 640, 1060, 668), (1050, 798, 1088, 846)],   # travertino limpo do estar
    # trecho da cortina (ondas sobre a janela) que o piso do aparador cobriu: volta o do render
    "cortina": (1005, 848, 1042, 851),
    # mesa de centro: no PDF são duas, com os contornos nas linhas 726-744 e 747-766; o render
    # fez uma só na mesma área. Linhas da emenda: destino <- origem (borda de baixo, sombra, sombra
    # clara e borda de cima da própria mesa)
    "mesa": {"x": (930, 1002), "linhas": {744: 766, 745: 767, 746: 768, 747: 726}},
    # mesas laterais orgânicas: janela e sementes (a menor, atrás, primeiro)
    "laterais": [((885, 788, 916, 828), [(906, 800), (902, 813)]),
                 ((1022, 786, 1052, 826), [(1040, 798), (1037, 811)])],
    "madeira": (945, 735, 990, 762),             # tampo da mesa de centro (veio vertical)
    "contorno": (80, 99, 118),                   # BGR do contorno da mesa de centro
    "sombra": {"desloc": (-2, 2), "sigma": 1.2, "forca": 0.45},
}
SS = 8
# gourmet: banquetas (com a sombra) abaixo da borda da bancada (linha 598, que fica); piso em
# espelho a partir da linha de baixo; sombra da bancada medida nos trechos limpos da borda
BANQUETAS = {
    "ret": (666, 599, 786, 617),
    "sombra_linhas": (599, 603),
    "colunas_limpas": [(648, 664), (788, 806)],
    "piso_ref": (606, 613),          # linhas de piso limpo nas colunas limpas (referência do tom)
    "emenda": 3,
}
# cooktops: caixa com o contorno (exclusivo à direita e embaixo) e a boca que sobra na gourmet
COOKTOPS = {
    "gourmet": (718, 565, 747, 583),
    "boca_a_mais": (727, 566, 736, 573),        # a do meio de cima, entre os divisores
    "ilha": (1192, 207, 1212, 239),
}
# porta de giro do box do BH master 2 (PDF, layer ARQ_BANCADAS, em px do render): folha aberta
# junto à parede de cima, arco com centro na dobradiça; o chuveiro de teto fica por cima do arco
PORTA_BOX = {
    "folha": (420.6, 469.2, 442.3, 471.0),
    "centro": (420.6, 469.4), "raio": 21.7,
    "janela": (416, 464, 448, 496),
    "chuveiro": (437, 479, 448, 490),
    "vidro": (211, 214, 214), "contorno": (85, 92, 98),
    "arco": (110, 126, 144), "larg_arco": 0.8, "larg_contorno": 0.35,
    # vão (projeção) ao lado do chuveiro: retângulo do PDF, lado livre à esquerda e o tracejado
    "vao": (452.3, 469.4, 462.4, 500.1), "janela_vao": (448, 466, 466, 503),
    "traco": 2.0, "espaco": 1.2, "larg_traco": 0.5,
}
# escada estreita (degraus 11 a 20 do PDF): linhas dos degraus (com a sombra da parede em cima e a
# aresta de baixo), bordas das arestas (x onde volta o claro), perfil da sombra à esquerda da aresta
ESCADA = {
    "x": (358, 456), "y": (506, 554),
    "bordas_velhas": [379, 394, 409, 425, 440],
    "borda_ini": 363.5, "borda_fim": 454.0, "degraus": 10,
    "perfil": ([-0.7, 0.0, 0.7, 1.4, 2.1, 2.8], [0.97, 0.52, 0.77, 0.85, 0.95, 1.0]),
    "limpar": (5, 6),                            # colunas [borda-5, borda+1) <- as 6 px à direita
}
# elevador: interior da caixa (entre as paredes; a borda antisserrilhada da parede fica), a
# cabine do PDF (px inteiros) e a cabine do Subsolo da Casa B (na resolução da base, sem a soleira
# da porta, que lá fica embaixo)
ELEVADOR = {
    "interior": (925, 426, 978, 475),
    "cabine": (926, 428, 968, 472),
    "branco": (255, 255, 255),
    "fonte": (RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final.png", (3116, 1011, 3276, 1162)),
}
# chuveiro externo: a cruz do motor (barra deitada e em pé, com a borda antisserrilhada), as
# fontes limpas, e a geometria do PDF (ducha, braço e canopla, em px do render)
CHUVEIRO_EXT = {
    "barra_deitada": ((608, 941, 628, 945), -14),          # <- linhas de cima, mesmas colunas
    "barra_em_pe": ((616, 934, 621, 961), -6),             # <- colunas à esquerda, mesmas linhas
    "ducha": (615.03, 937.25, 621.17, 943.39),
    "braco": (618.1, 941.0, 952.0), "larg_braco": 0.8,
    "canopla": (617.0, 951.4, 619.2, 952.5),
    "janela": (612, 934, 625, 955),
    "sombra": {"desloc": (-1.0, 1.0), "sigma": 0.8, "forca": 0.3},
}
# degraus largos: seta da base (com o deslocamento das colunas limpas), faixa das arestas retas,
# colunas de medida (sem a seta e sem os L), arestas que viram em L e o fim dos L; perfis da mesma
# escada no Subsolo da Casa C aprovado (fator sobre o piso liso, d = linha - aresta e coluna - aresta)
DEGRAUS_LARGOS = {
    "seta": ((289, 366, 301, 531), -12),
    "x": (190, 331), "y": (366, 520),
    "medida_x": (262, 318),
    "L": [{"y": 490, "x": 231}, {"y": 506, "x": 246}],
    "fim_L": 566,
    "perfil": {"d": list(range(-10, 7)),
               "f": [1.0, 1.0, 0.99, 0.99, 0.98, 0.96, 0.92, 0.87, 0.80, 0.71, 0.61, 0.99, 1.0, 1.0, 1.0, 1.0, 1.0]},
    "perfil_L": {"d": list(range(-7, 2)), "f": [1.0, 0.99, 0.95, 0.91, 0.84, 0.76, 0.64, 0.61, 1.0]},
}
# aparador do hall: linhas do aparador (com a borda da parede e a sombra), colunas da ponta da
# direita levadas ao fim do PDF, trecho que vira piso e a mesa redonda do PDF (centro, raio)
APARADOR = {
    "linhas": (621, 639),
    "ponta": ((1281, 1287), 1264),           # colunas da ponta -> a partir desta coluna
    "piso": (1270, 622, 1289, 640),          # veios de baixo, em espelho
    "mesa": ((1279.0, 630.5), 8.0),
    "madeira": (1215, 624, 1260, 632),
    "contorno": (80, 99, 118),
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.4},
}
# lavabo ao lado da adega: miolo da cuba a mais (linhas, colunas) e o trecho liso da bancada de
# baixo; adega: o móvel (com a sombra e as bordas antisserrilhadas) e as colunas de piso limpo
LAVABO_ADEGA = {
    "cuba_a_mais": (1233, 532, 1251, 559),
    "bancada_lisa": (595, 613),
    "movel": (1205, 480, 1227, 616),
    "piso_adega": (1190, 1205),
    "movel_lavabo": ((1233, 482, 1284, 500), ("baixo",)),     # entre as paredes, até a borda de baixo
}
# escritório: faixa da folha de correr sob a parede de cima (<- mesma faixa mais à esquerda), vão
# da janela na espessura da parede e a fonte: um pano limpo e o montante da janela da parede da
# esquerda (colunas da espessura da parede, de fora para dentro)
JANELA_ESCRITORIO = {
    "faixa_folha": ((1396, 481, 1459, 486), -50),
    "vao": (1413, 475, 1459, 481),
    "pano": (517, 545), "montante": (546, 549), "colunas": (1333, 1339),
}
# cadeiras das escrivaninhas: a cadeira de visitante do escritório (de frente para a direita), o
# centro dela, a escala para o tamanho da cadeira do PDF e, para cada escrivaninha, o centro do
# símbolo do PDF e o giro (0: de frente para a direita; "horario": de frente para baixo)
CADEIRAS = {
    "fonte": (1368, 543, 1391, 567), "centro_fonte": (1384.0, 554.0), "escala": 1.2,
    "piso_ref": (1366, 538, 1377, 545),
    # escrivaninha: eixo, onde começa o tampo e a faixa da sombra dela no piso (antes do tampo)
    "lugares": [("Quarto 1", (1106.3, 313.8), None, ("x", 1111, 1106)),
                ("quarto das duas camas", (706.7, 274.5), "horario", ("y", 279, 276)),
                ("suíte do canto", (621.5, 338.6), None, ("x", 626, 621))],
}
# BH master 1: trecho da bancada com as cubas do motor (<- linhas lisas entre elas, em espelho) e
# as bacias da cuba do PDF: a de cima (torneira em cima) e a de baixo (embaixo); o meio é bancada
CUBA_BHM1 = {
    "bancada": (392, 221, 408, 286), "lisa": (247, 260),
    "bacia_cima": (393, 225, 407, 244), "bacia_baixo": (393, 261, 407, 280),
    # BH master 2: trecho da cuba do motor (<- bancada lisa de baixo, em espelho) e a cuba do PDF
    "bhm2_bancada": (337, 455, 354, 478), "bhm2_lisa": (479, 494), "bhm2_cuba": (338, 457, 352, 475),
}
# porta pivotante principal: linhas da folha, trecho da folha copiado, onde começa a parte que
# faltou, fim no PDF e a ponta de dentro (arremate)
PIVOTANTE = {"linhas": (670, 674), "fonte_x": 1370, "de": 1406, "ate": 1434, "ponta": (1340, 1342)}
# arcos das portas sobre o granito: cor do granito na base chapada (BGR de #5A4232), parte mínima
# do arco sobre o granito, cor e largura do traço
ARCOS_GRANITO = {"granito": (50, 66, 90), "tol": 12, "fracao": 0.3, "min_px": 8,
                 "cor": (160, 161, 160), "larg": 0.45}   # cinza e fino: aparece no granito, discreto
# bancos ao pé das camas. Camas a encurtar: linhas, faixa da ponta (com borda e sombra),
# deslocamento até o pé do PDF e de que lado vem o preenchimento do vão (tapete ou piso)
BANCOS = {
    # (no Quarto 3 o tapete termina logo à esquerda: o vão repete só as colunas de tapete)
    "encurtar": [("Quarto 1", (205, 276), (1043, 1057), 6, None),
                 ("Quarto 3", (194, 257), (668, 679), 9, (664, 668)),
                 ("Quarto 2, cama de cima", (186, 229), (815, 829), -10, None),
                 ("Quarto 2, cama de baixo", (240, 283), (815, 829), -10, None)],
    # bancos do Térreo da Casa B: recorte (com a sombra), corpo do banco e o tom do tapete em volta
    "fonte": RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Terreo_v4_retocado.png",
    "modelos": {"casal": ((1078, 194, 1104, 257), (1083, 196, 1102, 253), 212.0),
                "solteiro": ((1239, 181, 1256, 214), (1243, 182, 1254, 210), 205.0)},
    # retângulo do banco no PDF (px do render) e o giro (anti-horário: a sombra continua embaixo)
    "lugares": [("suíte master", "casal", (499.8, 367.8, 549.6, 380.2), True),
                ("Quarto 1", "casal", (1044.4, 212.4, 1056.9, 262.1), False),
                ("Quarto 3", "casal", (671.8, 197.5, 684.3, 247.2), False),
                ("Quarto 2, cama de cima", "solteiro", (815.5, 191.0, 824.9, 219.0), False),
                ("Quarto 2, cama de baixo", "solteiro", (815.5, 245.4, 824.9, 273.3), False)],
}
# vaso do lavabo masculino: o vaso cinza do motor (com a sombra), o piso limpo à esquerda e o vaso
# padrão (recorte, corpo e tom do piso em volta) do lavabo ao lado da adega; retângulo do PDF
VASO_MASC = {
    "apagar": (664, 826, 687, 843), "piso_dx": -23,
    "fonte": (1233, 507, 1253, 523), "corpo": (1233.0, 508.5, 1251.5, 521.0), "piso": 215.0,
    "destino": (670.6, 828.6, 686.3, 839.9),
}
CROMO_ESCURO = (130, 134, 138)
CROMO = (196, 199, 202)
CROMO_CLARO = (238, 240, 242)
CHUVEIRO_TETO = (RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final2.png", (1160, 214, 1171, 225))
CHUVEIROS = {
    "BH master 1": (411.2, 187.9),
    "BH 3": (630.5, 149.8),
    "BH 2": (868.4, 149.8),
    "BH 1": (1016.1, 149.8),
    "BH master 2": (442.3, 484.6),
    "ducha entre os lavabos": (716.06, 834.2),      # o motor pôs um ralo redondo; a placa o cobre
}


def chuveiros_teto(out):
    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    cab = img[hy0:hy1, hx0:hx1]
    for nome, (cx, cy) in CHUVEIROS.items():
        px, py = round(cx - (hx1 - hx0 - 1) / 2), round(cy - (hy1 - hy0 - 1) / 2)
        out[py:py + cab.shape[0], px:px + cab.shape[1]] = cab
        print(f"    {nome}: chuveiro de teto em ({cx}, {cy})")
    return out


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
    """Página do PDF e as conversões PDF -> render e render -> PDF pela mesma cadeia da base
    (recorte, largura da base, tela 16:9, redução ao tamanho do render e o afim A)."""
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
    """Trecho do PDF rasterizado e levado ao render pela mesma cadeia da base (recorte, largura
    da base, tela 16:9, redução ao tamanho do render e o afim A), em SS vezes a resolução."""
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

    Ai = np.linalg.inv(np.vstack([A, [0, 0, 1]]))

    def r2p(x, y):
        bx, by, _ = Ai @ [x, y, 1]
        return (bx / sx - (wt - wb) // 2) / zoom + clip.x0, (by / sy - (ht - hb) // 2) / zoom + clip.y0

    x0, y0, x1, y1 = janela
    a, b = r2p(x0 - 2, y0 - 2), r2p(x1 + 2, y1 + 2)
    ret = pymupdf.Rect(a[0], a[1], b[0], b[1])
    zp = 60
    pix = pg.get_pixmap(clip=ret, matrix=pymupdf.Matrix(zp, zp), alpha=False)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)[..., ::-1]
    src = [(0, 0), (pix.width, 0), (0, pix.height)]
    dst = [((p2r(ret.x0 + u / zp, ret.y0 + v / zp)[0] - x0) * SS, (p2r(ret.x0 + u / zp, ret.y0 + v / zp)[1] - y0) * SS)
           for u, v in src]
    M = cv2.getAffineTransform(np.float32(src), np.float32(dst))
    return cv2.warpAffine(np.ascontiguousarray(img), M, ((x1 - x0) * SS, (y1 - y0) * SS), flags=cv2.INTER_AREA,
                          borderValue=(255, 255, 255))


def fora_do_lote(out, base):
    H, W = out.shape[:2]
    x0 = LOTE["x_esq"]
    (c0, c1), (b0, b1) = LOTE["muro_cima"], LOTE["muro_baixo"]
    fora = np.zeros((H, W), bool)
    fora[:, :x0] = True                                   # à esquerda da linha tracejada
    fora[:c0, :MURO_COBERTO["x"][1]] = True               # acima do muro de cima, no canto
    fora[b1:, :MURO_COBERTO["x"][1]] = True               # abaixo do muro de baixo, no canto
    mudou = fora & (np.abs(out.astype(int) - base.astype(int)).max(axis=2) > 40)
    out[fora] = base[fora]
    # muros: as folhas passavam por cima; o muro volta, copiado da coluna limpa do próprio render
    mx0, mx1 = MURO_COBERTO["x"]
    xl = MURO_COBERTO["coluna_limpa"]
    for y0, y1 in ((c0, c1), (b0, b1)):
        out[y0:y1, max(mx0, x0):mx1] = out[y0:y1, xl:xl + 1]
    print(f"    {int(mudou.sum())} px de folhas fora do lote; muros refeitos em x {max(mx0, x0)}-{mx1}")
    return out


def jardins_de_inverno(out):
    j = JARDINS
    a = out.astype(np.int32)
    n_faixas = 0
    for f in j["faixas"]:                                   # vidros e parede: perfil limpo repetido
        x0, y0, x1, y1 = f["ret"]
        tipo, pos = f["perfil"][0], f["perfil"][1]
        if tipo == "linha":
            out[y0:y1, x0:x1] = a[pos, x0:x1][None].astype(np.uint8)
        else:
            ini = f["perfil"][2] if len(f["perfil"]) > 2 else y0
            out[y0:y1, x0:x1] = a[ini:ini + (y1 - y0), pos][:, None].astype(np.uint8)
        n_faixas += (y1 - y0) * (x1 - x0)
    e = j["emenda"]
    n = 0
    for nome, (x0, y0, x1, y1), (dx, dy) in j["pisos"]:
        fonte = out[y0 + dy:y1 + dy, x0 + dx:x1 + dx].astype(np.float32)
        alvo = out[y0:y1, x0:x1].astype(np.float32)
        h, w = y1 - y0, x1 - x0
        # emenda suave só no lado que encosta no piso que fica (longe dos jardins)
        al = np.ones((h, w), np.float32)
        if dx < 0:
            al[:, :e] = (np.arange(e) + 1)[None] / (e + 1)
        elif dx > 0:
            al[:, -e:] = (np.arange(e)[::-1] + 1)[None] / (e + 1)
        elif dy > 0:
            al[-e:, :] = (np.arange(e)[::-1] + 1)[:, None] / (e + 1)
        out[y0:y1, x0:x1] = np.clip(alvo * (1 - al[..., None]) + fonte * al[..., None], 0, 255).astype(np.uint8)
        n += h * w
    print(f"    {n_faixas} px de vidro e parede refeitos; {n} px de piso refeitos (folhas e sombras)")
    return out


def portas_de_vidro(out, base, chapada):
    """Folhas de vidro da base sobre as faixas dos jardins; o resto da faixa é piso ou floreira."""
    a = out.copy()
    c = chapada.astype(np.int32)
    # vidro e montantes: a cor exata do vidro da legenda e o preto (contorno e montantes) da base chapada
    cinza = np.abs(c - np.array(VIDRO)).max(axis=2) <= 8
    preto = c.max(axis=2) < 60
    vidro = cinza | preto
    n = 0
    for nome, (x0, y0, x1, y1), (dx, dy), eixo, lim in JARDINS["portas"]:
        for y in range(y0, y1):
            for x in range(x0, x1):
                if vidro[y, x]:
                    out[y, x] = base[y, x]
                    n += 1
                    continue
                pos = x if eixo == "x" else y
                passo = dx if eixo == "x" else dy
                dentro = (pos >= lim) if passo > 0 else (pos <= lim)
                out[y, x] = a[y + dy, x + dx] if dentro else a[y - dy, x - dx]
    print(f"    portas de vidro da base: {n} px")
    return out


def quartzo(out, alto, largo):
    """Quartzo claro tecido (image quilting) dos trechos limpos da bancada gourmet do render."""
    fontes = []
    for x0, y0, x1, y1 in COZINHA["fonte_quartzo"]:
        t = out[y0:y1, x0:x1].astype(np.float32)
        fontes += [np.ascontiguousarray(v) for v in (t, t[:, ::-1], t[::-1, :], t[::-1, ::-1])]
    return quilting(fontes, alto, largo, p=16, sobra=4, candidatos=600)


def cozinha(out):
    c = COZINHA
    bx0, by0 = min(r[0] for r in c["quartzo"]), min(r[1] for r in c["quartzo"])
    bx1, by1 = max(r[2] for r in c["quartzo"]), max(r[3] for r in c["quartzo"])
    tex = quartzo(out, by1 - by0, bx1 - bx0)
    m = np.zeros((by1 - by0, bx1 - bx0), bool)
    for x0, y0, x1, y1 in c["quartzo"]:
        m[y0 - by0:y1 - by0, x0 - bx0:x1 - bx0] = True
    cx0, cy0, cx1, cy1 = c["cooktop"]
    m[cy0 - by0:cy1 - by0, cx0 - bx0:cx1 - bx0] = False
    reg = out[by0:by1, bx0:bx1]
    reg[m] = np.clip(tex[m], 0, 255).astype(np.uint8)
    print(f"    quartzo: {int(m.sum())} px de bancada e ilha")

    (x0, y0, x1, y1), dx, sombra, xs = c["vao"]
    out[y0:y1, x0:x1] = out[y0:y1, x0 + dx:x1 + dx]
    for i, f in enumerate(sombra):
        y = y1 - len(sombra) + i
        out[y, xs:x1] = np.clip(out[y, xs:x1].astype(np.float32) * f, 0, 255).astype(np.uint8)
    print(f"    vão de piso entre a geladeira e o armário: {(x1 - x0) * (y1 - y0)} px")

    fx0, fy0, fx1, fy1 = c["fonte_areia"]
    t = out[fy0:fy1, fx0:fx1]
    lado = {"esquerda": (slice(None), 0), "direita": (slice(None), -1), "cima": (0, slice(None)),
            "baixo": (-1, slice(None))}
    for (x0, y0, x1, y1), faces in c["armarios"]:
        h, w = y1 - y0, x1 - x0
        lin = np.concatenate([t, t[::-1]] * (h // (2 * t.shape[0]) + 1), axis=0)[:h]
        reg = np.concatenate([lin, lin[:, ::-1]] * (w // (2 * t.shape[1]) + 1), axis=1)[:, :w].astype(np.float32)
        borda = np.zeros((h, w), bool)
        for face in faces:
            borda[lado[face]] = True
        reg[borda] *= c["contorno"]
        out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    armário alto {w}x{h} px, contorno em {', '.join(faces)}")

    for x0, y0, x1, y1 in c["cubas"]:                      # torneira do lado da parede (em cima)
        reg = np.ascontiguousarray(out[y0:y1, x0:x1][::-1])
        reg = cuba(reg, (0, 0, x1 - x0, y1 - y0))
        out[y0:y1, x0:x1] = reg[::-1]
    print(f"    {len(c['cubas'])} cubas")

    ax0, ay0, ax1, ay1 = c["area_molhada"]
    jx0, jy0, jx1, jy1 = int(ax0) - 2, int(ay0) - 1, int(ax1) + 3, int(ay1) + 3
    h, w = jy1 - jy0, jx1 - jx0
    f = np.zeros((h * SS, w * SS), np.uint8)
    pts = [(ax0, ay0), (ax0, ay1), (ax1, ay1), (ax1, ay0)]
    pts = np.array([[int(round((x - jx0) * SS)), int(round((y - jy0) * SS))] for x, y in pts], np.int32)
    cv2.polylines(f, [pts], False, 255, max(1, int(round(c["larg_traco"] * SS))))
    a = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None] * c["forca_traco"]
    reg = out[jy0:jy1, jx0:jx1].astype(np.float32)
    out[jy0:jy1, jx0:jx1] = np.clip(reg * (1 - a) + np.array(c["traco"], np.float32) * a, 0, 255).astype(np.uint8)
    print("    área molhada da bancada das cubas demarcada")
    return out


def quarto_externo(out):
    q = QUARTO_EXTERNO
    a = out.copy()
    for (x0, y0, x1, y1), (dx, dy) in q["pisos"]:
        out[y0:y1, x0:x1] = a[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    fx0, fy0, fx1, fy1 = q["fonte_cama"]
    c0, c1 = q["cortar_cobertor"]
    cama = np.concatenate([a[fy0:fy1, fx0:c0], a[fy0:fy1, c1:fx1]], axis=1)[:, ::-1]   # cabeceira à direita
    x0, y0, x1, y1 = q["cama"]
    out[y0:y1, x0:x1] = cv2.resize(cama, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    out[y0 - 1, x0:x1] = np.clip(out[y0 - 1, x0:x1] * q["sombra_cima"], 0, 255).astype(np.uint8)
    out[y0:y1, x0 - 1] = np.clip(out[y0:y1, x0 - 1] * q["sombra_pe"], 0, 255).astype(np.uint8)
    print(f"    cama de solteiro: {fx1 - fx0 - (c1 - c0)}x{fy1 - fy0} px da fonte em {x1 - x0}x{y1 - y0} px")
    fx0, fy0, fx1, fy1 = q["fonte_criado"]
    x0, y0, x1, y1 = q["criado"]
    out[y0:y1, x0:x1] = cv2.resize(a[fy0:fy1, fx0:fx1], (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    print(f"    criado-mudo: {x1 - x0}x{y1 - y0} px")
    return out


def tanques(out):
    x0, y0, x1, y1 = SERVICO["bancada"]
    out[y0:y1, x0:x1] = np.clip(quartzo(out, y1 - y0, x1 - x0), 0, 255).astype(np.uint8)
    arq, (fx0, fy0, fx1, fy1) = SERVICO["fonte_tanques"]
    px, py = SERVICO["tanques_em"]
    out[py:py + fy1 - fy0, px:px + fx1 - fx0] = cv2.imread(str(arq))[fy0:fy1, fx0:fx1]
    print(f"    bancada: {(x1 - x0) * (y1 - y0)} px no quartzo; tanques da Casa B em ({px}, {py})")
    return out


def poltronas_estar(out):
    q = POLTRONAS
    x0, y0, x1, y1 = q["ret"]
    a = out.astype(np.float32)
    novo = a[y0:y1, x0:x1].copy()
    yp, yb, w = q["piso_ate"], q["borda_ate"], x1 - x0
    novo[:yp - y0] = a[y0 - 1:y0 - 1 - (yp - y0):-1, x0:x1]          # veios de cima, em espelho
    fx0, fx1 = q["fonte_borda_x"]
    t = a[yp:yb, fx0:fx1]
    novo[yp - y0:yb - y0] = np.concatenate([t, t[:, ::-1]] * (w // (2 * t.shape[1]) + 1), axis=1)[:, :w]
    dy = q["tapete_dy"]
    novo[yb - y0:] = a[yb + dy:y1 + dy, x0:x1]
    e = q["emenda"]
    al = np.ones(w, np.float32)
    al[:e] = (np.arange(e) + 1) / (e + 1)
    al[-e:] = (np.arange(e)[::-1] + 1) / (e + 1)
    reg = a[y0:y1, x0:x1]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - al[None, :, None]) + novo * al[None, :, None], 0, 255).astype(np.uint8)
    print(f"    duas poltronas a mais: {w}x{y1 - y0} px refeitos (piso e borda do tapete)")
    return out


def piso_tecido(out, ret, emenda, fontes, semente):
    """Travertino tecido (veios verticais: só espelhos, sem girar), no tom do piso limpo em volta."""
    x0, y0, x1, y1 = ret
    h, w = y1 - y0, x1 - x0
    tex = quilting(fontes, h, w, p=16, sobra=4, candidatos=800, rng=np.random.default_rng(semente))
    dentro = np.zeros(out.shape[:2], np.uint8)
    dentro[y0:y1, x0:x1] = 1
    anel = (cv2.dilate(dentro, np.ones((9, 9), np.uint8)) > 0) & (dentro == 0)
    px = out[anel].astype(np.float32)
    px = px[px.mean(axis=1) > 195]                         # só piso e tapete (sem parede e sombra)
    tex += np.median(px, axis=0) - np.median(tex.reshape(-1, 3), axis=0)
    al = np.ones((h, w), np.float32)
    e, c, d, b = emenda
    for k in range(e):
        al[:, k] = np.minimum(al[:, k], (k + 1) / (e + 1))
    for k in range(d):
        al[:, w - 1 - k] = np.minimum(al[:, w - 1 - k], (k + 1) / (d + 1))
    for k in range(c):
        al[k, :] = np.minimum(al[k, :], (k + 1) / (c + 1))
    for k in range(b):
        al[h - 1 - k, :] = np.minimum(al[h - 1 - k, :], (k + 1) / (b + 1))
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - al[..., None]) + tex * al[..., None], 0, 255).astype(np.uint8)


def estar(out, A):
    e = ESTAR
    a = out.copy()
    mx0, my0, mx1, my1 = e["madeira"]
    t = a[my0:my1, mx0:mx1].astype(np.float32)

    fontes = []
    for x0, y0, x1, y1 in e["fonte_piso"]:
        f = a[y0:y1, x0:x1].astype(np.float32)
        fontes += [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    for k, (ret, emenda) in enumerate(e["piso"]):
        piso_tecido(out, ret, emenda, fontes, 642 + k)
    cx0, cy0, cx1, cy1 = e["cortina"]
    out[cy0:cy1, cx0:cx1] = a[cy0:cy1, cx0:cx1]
    print(f"    aparador e mesas laterais quadradas: {len(e['piso'])} trechos de piso tecido; cortina mantida")

    x0, x1 = e["mesa"]["x"]
    for destino, origem in e["mesa"]["linhas"].items():
        out[destino, x0:x1] = a[origem, x0:x1]
    print("    mesa de centro em duas peças, como no PDF")

    s = e["sombra"]
    for (wx0, wy0, wx1, wy1), sementes in e["laterais"]:
        h, w = wy1 - wy0, wx1 - wx0
        pdf = pdf_no_render((wx0, wy0, wx1, wy1), A, out.shape)
        branco = (cv2.cvtColor(pdf, cv2.COLOR_BGR2GRAY) > 235).astype(np.uint8)
        lin = np.concatenate([t, t[::-1]] * (h // (2 * t.shape[0]) + 1), axis=0)[:h]
        madeira = np.concatenate([lin, lin[:, ::-1]] * (w // (2 * t.shape[1]) + 1), axis=1)[:, :w]
        reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
        for sx, sy in sementes:
            f = branco.copy()
            cv2.floodFill(f, np.zeros((f.shape[0] + 2, f.shape[1] + 2), np.uint8), ((sx - wx0) * SS, (sy - wy0) * SS), 2)
            forma = cv2.dilate((f == 2).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
            M = np.float32([[1, 0, s["desloc"][0] * SS], [0, 1, s["desloc"][1] * SS]])
            sombra = cv2.GaussianBlur(cv2.warpAffine(forma, M, (w * SS, h * SS)), (0, 0), s["sigma"] * SS)
            reg *= (1 - s["forca"] * cv2.resize(sombra, (w, h), interpolation=cv2.INTER_AREA))[..., None]
            borda = forma - cv2.erode(forma, np.ones((7, 7), np.uint8))           # contorno de ~0,8 px
            a_tampo = cv2.resize(forma, (w, h), interpolation=cv2.INTER_AREA)[..., None]
            a_borda = cv2.resize(borda, (w, h), interpolation=cv2.INTER_AREA)[..., None]
            reg = reg * (1 - a_tampo) + madeira * a_tampo
            reg = reg * (1 - a_borda) + np.array(e["contorno"], np.float32) * a_borda
        out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    mesas laterais orgânicas do PDF: {len(e['laterais'])} pares")
    return out


def banquetas(out):
    q = BANQUETAS
    x0, y0, x1, y1 = q["ret"]
    a = out.astype(np.float32)
    h, w = y1 - y0, x1 - x0
    novo = a[y1 + h - 1:y1 - 1:-1, x0:x1].copy()                  # veios de baixo, em espelho
    s0, s1 = q["sombra_linhas"]
    r0, r1 = q["piso_ref"]
    limpas = np.concatenate([a[:, c0:c1] for c0, c1 in q["colunas_limpas"]], axis=1)
    piso = limpas[r0:r1].reshape(-1, 3).mean(axis=0)
    for y in range(s0, s1):
        novo[y - y0] *= limpas[y].mean(axis=0) / piso                # fator por canal
    e = q["emenda"]
    al = np.ones(w, np.float32)
    al[:e] = (np.arange(e) + 1) / (e + 1)
    al[-e:] = (np.arange(e)[::-1] + 1) / (e + 1)
    reg = a[y0:y1, x0:x1]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - al[None, :, None]) + novo * al[None, :, None], 0, 255).astype(np.uint8)
    print(f"    cinco banquetas a mais: {w}x{h} px refeitos (piso e sombra da bancada)")
    return out


def cooktops(out):
    c = COOKTOPS
    x0, y0, x1, y1 = c["gourmet"]
    dentro = out[y0 + 1:y1 - 1, x0 + 1:x1 - 1].reshape(-1, 3).astype(np.float32)
    tampo = np.median(dentro[dentro.mean(axis=1) > 195], axis=0)       # tampo claro entre as grelhas
    bx0, by0, bx1, by1 = c["boca_a_mais"]
    ruido = np.random.default_rng(5).normal(0, 1.5, (by1 - by0, bx1 - bx0, 1))
    out[by0:by1, bx0:bx1] = np.clip(tampo + ruido, 0, 255).astype(np.uint8)
    girado = cv2.rotate(out[y0:y1, x0:x1], cv2.ROTATE_90_CLOCKWISE)    # fila de cima vira a coluna da direita
    ix0, iy0, ix1, iy1 = c["ilha"]
    out[iy0:iy1, ix0:ix1] = cv2.resize(girado, (ix1 - ix0, iy1 - iy0), interpolation=cv2.INTER_CUBIC)
    print("    cooktops com 5 bocas, como no PDF (gourmet e ilha)")
    return out


def porta_box(out, A):
    q = PORTA_BOX
    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0

    def px(v, o):
        return int(round((v - o) * SS))

    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    arco = np.zeros((h * SS, w * SS), np.uint8)
    cx, cy = q["centro"]
    cv2.ellipse(arco, (px(cx, wx0), px(cy, wy0)), (px(q["raio"], 0), px(q["raio"], 0)), 0, 0, 90, 255,
                max(1, px(q["larg_arco"], 0)), cv2.LINE_AA)
    a = cv2.resize(arco.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    c0, c1, c2, c3 = q["chuveiro"]
    a[c1 - wy0:c3 - wy0, c0 - wx0:c2 - wx0] = 0                     # o chuveiro de teto fica por cima
    reg = reg * (1 - a[..., None]) + np.array(q["arco"], np.float32) * a[..., None]

    fx0, fy0, fx1, fy1 = q["folha"]
    folha = np.zeros((h * SS, w * SS), np.uint8)
    cv2.rectangle(folha, (px(fx0, wx0), px(fy0, wy0)), (px(fx1, wx0), px(fy1, wy0)), 255, -1)
    k = max(1, px(q["larg_contorno"], 0))
    miolo = cv2.erode(folha, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
    a_f = cv2.resize(folha.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    a_m = cv2.resize(miolo.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    reg = reg * (1 - a_f) + np.array(q["contorno"], np.float32) * a_f
    reg = reg * (1 - a_m) + np.array(q["vidro"], np.float32) * a_m
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    porta de giro do box do BH master 2: folha aberta e arco")

    # vão ao lado do chuveiro: os X tracejados do PDF e o contorno tracejado do lado livre
    jx0, jy0, jx1, jy1 = q["janela_vao"]
    h, w = jy1 - jy0, jx1 - jx0
    cinza = cv2.cvtColor(pdf_no_render((jx0, jy0, jx1, jy1), A, out.shape), cv2.COLOR_BGR2GRAY).astype(np.float32)
    vx0, vy0, vx1, vy1 = q["vao"]
    dentro = np.zeros((h * SS, w * SS), np.float32)
    dentro[px(vy0, jy0) + 3:px(vy1, jy0) - 3, px(vx0, jx0) + 3:px(vx1, jx0) - 3] = 1
    k = max(1, px(q["larg_traco"], 0))                                   # diagonais na largura do traço
    tracos = cv2.dilate(((cinza < 160) & (dentro > 0)).astype(np.uint8), np.ones((k, k), np.uint8)).astype(np.float32)
    y = vy0
    while y < vy1:
        cv2.line(tracos, (px(vx0, jx0), px(y, jy0)), (px(vx0, jx0), px(min(y + q["traco"], vy1), jy0)), 1.0,
                 max(1, px(q["larg_traco"], 0)))
        y += q["traco"] + q["espaco"]
    a = np.clip(cv2.resize(tracos, (w, h), interpolation=cv2.INTER_AREA), 0, 1)[..., None]
    reg = out[jy0:jy1, jx0:jx1].astype(np.float32)
    out[jy0:jy1, jx0:jx1] = np.clip(reg * (1 - a) + np.array(q["arco"], np.float32) * a, 0, 255).astype(np.uint8)
    print("    vão ao lado do chuveiro: tracejado sobre o piso, como no PDF")
    return out


def escada(out):
    e = ESCADA
    y0, y1 = e["y"]
    a = out.copy()
    antes, desloc = e["limpar"]
    for b in e["bordas_velhas"]:
        out[y0:y1, b - antes:b + 1] = a[y0:y1, b - antes + desloc:b + 1 + desloc]
    x0, x1 = e["x"]
    n = e["degraus"]
    passo = (e["borda_fim"] - e["borda_ini"]) / n
    bordas = [e["borda_ini"] + k * passo for k in range(1, n)]
    xs = np.arange(x0, x1)[:, None] + (np.arange(SS) + 0.5)[None, :] / SS
    fator = np.ones(xs.shape)
    d_ref, f_ref = e["perfil"]
    for b in bordas:
        fator *= np.interp(b - xs, d_ref, f_ref, left=1.0, right=1.0)
    rel = fator.mean(axis=1)
    reg = out[y0:y1, x0:x1].astype(np.float32) * rel[None, :, None].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    escada estreita: {n} degraus (arestas a cada {passo:.2f} px)")
    return out


def elevador(out):
    q = ELEVADOR
    x0, y0, x1, y1 = q["interior"]
    out[y0:y1, x0:x1] = q["branco"]
    arq, (fx0, fy0, fx1, fy1) = q["fonte"]
    cabine = cv2.rotate(cv2.imread(str(arq))[fy0:fy1, fx0:fx1], cv2.ROTATE_90_CLOCKWISE)   # porta à esquerda
    cx0, cy0, cx1, cy1 = q["cabine"]
    out[cy0:cy1, cx0:cx1] = cv2.resize(cabine, (cx1 - cx0, cy1 - cy0), interpolation=cv2.INTER_AREA)
    print(f"    elevador: caixa branca e a cabine do Subsolo da Casa B ({cx1 - cx0}x{cy1 - cy0} px)")
    return out


def chuveiro_externo(out):
    q = CHUVEIRO_EXT
    for (x0, y0, x1, y1), d in (q["barra_deitada"],):
        out[y0:y1, x0:x1] = out[y0 + d:y1 + d, x0:x1]
    (x0, y0, x1, y1), d = q["barra_em_pe"]
    out[y0:y1, x0:x1] = out[y0:y1, x0 + d:x1 + d]

    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0

    def px(v, o=0.0):
        return int(round((v - o) * SS))

    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def pintar(mascara, cor):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    dx0, dy0, dx1, dy1 = q["ducha"]
    ducha = np.zeros((h * SS, w * SS), np.uint8)
    cv2.rectangle(ducha, (px(dx0, wx0), px(dy0, wy0)), (px(dx1, wx0), px(dy1, wy0)), 255, -1)
    s = q["sombra"]
    M = np.float32([[1, 0, s["desloc"][0] * SS], [0, 1, s["desloc"][1] * SS]])
    sombra = cv2.GaussianBlur(cv2.warpAffine(ducha.astype(np.float32), M, (w * SS, h * SS)), (0, 0), s["sigma"] * SS) / 255
    reg *= (1 - s["forca"] * cv2.resize(sombra, (w, h), interpolation=cv2.INTER_AREA))[..., None]

    bx, by0, by1 = q["braco"]
    braco = np.zeros_like(ducha)
    cv2.line(braco, (px(bx, wx0), px(by0, wy0)), (px(bx, wx0), px(by1, wy0)), 255, px(q["larg_braco"]))
    brilho = np.zeros_like(ducha)
    cv2.line(brilho, (px(bx, wx0), px(by0, wy0)), (px(bx, wx0), px(by1, wy0)), 255, max(1, px(0.3)))
    pintar(braco, CROMO_ESCURO)
    pintar(brilho, CROMO_CLARO)
    cx0, cy0, cx1, cy1 = q["canopla"]
    canopla = np.zeros_like(ducha)
    cv2.rectangle(canopla, (px(cx0, wx0), px(cy0, wy0)), (px(cx1, wx0), px(cy1, wy0)), 255, -1)
    pintar(canopla, CROMO)

    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    placa = cv2.resize(img[hy0:hy1, hx0:hx1], (px(dx1 - dx0), px(dy1 - dy0)), interpolation=cv2.INTER_CUBIC)
    cor = np.zeros((h * SS, w * SS, 3), np.uint8)
    cor[px(dy0, wy0):px(dy0, wy0) + placa.shape[0], px(dx0, wx0):px(dx0, wx0) + placa.shape[1]] = placa
    a = cv2.resize(ducha.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    c = cv2.resize(cor.astype(np.float32) * (ducha[..., None] / 255), (w, h), interpolation=cv2.INTER_AREA)
    c = c / np.maximum(a, 1e-6)
    reg = reg * (1 - a) + c * a
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    chuveiro externo: cruz do motor fora; ducha, braço e canopla do PDF")
    return out


def degraus_largos(out):
    q = DEGRAUS_LARGOS
    (sx0, sy0, sx1, sy1), d = q["seta"]
    out[sy0:sy1, sx0:sx1] = out[sy0:sy1, sx0 + d:sx1 + d]
    L = out.astype(np.float32).mean(axis=2)
    K = np.ones(L.shape, np.float32)
    mx0, mx1 = q["medida_x"]
    y0, y1 = q["y"]
    m = np.median(L[y0:y1, mx0:mx1], axis=1)
    arestas = [y0 + i for i in range(1, len(m) - 1) if m[i] < 170 and m[i] <= m[i - 1] and m[i] <= m[i + 1]]
    ds, fs = q["perfil"]["d"], np.array(q["perfil"]["f"], np.float32)
    for c in arestas:
        liso = np.median(L[c - 7:c - 3, mx0:mx1])
        motor = np.clip([np.median(L[c + k, mx0:mx1]) / liso for k in ds], 0.3, 1.1)
        xi = q["x"][0]
        for dl in q["L"]:
            if abs(c - dl["y"]) <= 2:
                xi = dl["x"]
        K[c + ds[0]:c + ds[-1] + 1, xi:q["x"][1]] *= (fs / motor)[:, None]
    dv, fv = q["perfil_L"]["d"], np.array(q["perfil_L"]["f"], np.float32)
    for dl in q["L"]:
        xc, ya, yb = dl["x"], dl["y"] - 1, q["fim_L"]
        liso = np.median(L[ya + 8:yb - 4, xc - 12:xc - 8])
        motor = np.clip([np.median(L[ya + 8:yb - 4, xc + k]) / liso for k in dv], 0.3, 1.1)
        K[ya:yb, xc + dv[0]:xc + dv[-1] + 1] *= (fv / motor)[None, :]
    out[:] = np.clip(out.astype(np.float32) * K[..., None], 0, 255).astype(np.uint8)
    print(f"    degraus largos: seta fora; {len(arestas)} arestas e {len(q['L'])} L com a sombra para o pátio")
    return out


def aparador_hall(out):
    q = APARADOR
    y0, y1 = q["linhas"]
    (p0, p1), destino = q["ponta"]
    a = out.copy()
    out[y0:y1, destino:destino + p1 - p0] = a[y0:y1, p0:p1]
    x0, fy0, x1, fy1 = q["piso"]
    h = fy1 - fy0
    out[fy0:fy1, x0:x1] = a[fy1 + h - 1:fy1 - 1:-1, x0:x1]
    (cx, cy), raio = q["mesa"]
    s = q["sombra"]
    wx0, wy0 = int(cx - raio - 4), int(cy - raio - 4)
    wx1, wy1 = int(cx + raio + 5), int(cy + raio + 5)
    w, hh = wx1 - wx0, wy1 - wy0
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    forma = np.zeros((hh * SS, w * SS), np.uint8)
    cv2.circle(forma, (int(round((cx - wx0) * SS)), int(round((cy - wy0) * SS))), int(round(raio * SS)), 255, -1)
    forma = forma.astype(np.float32)
    M = np.float32([[1, 0, s["desloc"][0] * SS], [0, 1, s["desloc"][1] * SS]])
    sombra = cv2.GaussianBlur(cv2.warpAffine(forma, M, (w * SS, hh * SS)), (0, 0), s["sigma"] * SS) / 255
    reg *= (1 - s["forca"] * cv2.resize(sombra, (w, hh), interpolation=cv2.INTER_AREA))[..., None]
    mx0, my0, mx1, my1 = q["madeira"]
    t = a[my0:my1, mx0:mx1].astype(np.float32)
    lin = np.concatenate([t, t[::-1]] * (hh // (2 * t.shape[0]) + 1), axis=0)[:hh]
    madeira = np.concatenate([lin, lin[:, ::-1]] * (w // (2 * t.shape[1]) + 1), axis=1)[:, :w]
    borda = forma - cv2.erode(forma, np.ones((7, 7), np.uint8))
    a_t = cv2.resize(forma / 255, (w, hh), interpolation=cv2.INTER_AREA)[..., None]
    a_b = cv2.resize(borda / 255, (w, hh), interpolation=cv2.INTER_AREA)[..., None]
    reg = reg * (1 - a_t) + madeira * a_t
    reg = reg * (1 - a_b) + np.array(q["contorno"], np.float32) * a_b
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    aparador do hall no comprimento do PDF e a mesa redonda ao lado")
    return out


def lavabo_adega(out):
    q = LAVABO_ADEGA
    a = out.copy()
    x0, y0, x1, y1 = q["cuba_a_mais"]
    r0, r1 = q["bancada_lisa"]
    t = a[r0:r1, x0:x1]
    out[y0:y1, x0:x1] = np.concatenate([t, t[::-1]] * ((y1 - y0) // (2 * t.shape[0]) + 1), axis=0)[:y1 - y0]
    x0, y0, x1, y1 = q["movel"]
    c0, c1 = q["piso_adega"]
    t = a[y0:y1, c0:c1]
    out[y0:y1, x0:x1] = np.concatenate([t, t[:, ::-1]] * ((x1 - x0) // (2 * t.shape[1]) + 1), axis=1)[:, :x1 - x0]
    (x0, y0, x1, y1), faces = q["movel_lavabo"]
    fx0, fy0, fx1, fy1 = COZINHA["fonte_areia"]
    t = a[fy0:fy1, fx0:fx1]
    h, w = y1 - y0, x1 - x0
    lin = np.concatenate([t, t[::-1]] * (h // (2 * t.shape[0]) + 1), axis=0)[:h]
    reg = np.concatenate([lin, lin[:, ::-1]] * (w // (2 * t.shape[1]) + 1), axis=1)[:, :w].astype(np.float32)
    lado = {"esquerda": (slice(None), 0), "direita": (slice(None), -1), "cima": (0, slice(None)),
            "baixo": (-1, slice(None))}
    for face in faces:
        reg[lado[face]] *= COZINHA["contorno"]
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    lavabo: a cuba a mais vira bancada e o móvel do topo vira marcenaria; adega: o móvel sai")
    return out


def janela_escritorio(out):
    q = JANELA_ESCRITORIO
    a = out.copy()
    (x0, y0, x1, y1), d = q["faixa_folha"]
    out[y0:y1, x0:x1] = a[y0:y1, x0 + d:x1 + d]
    c0, c1 = q["colunas"]
    pano = cv2.rotate(a[q["pano"][0]:q["pano"][1], c0:c1], cv2.ROTATE_90_CLOCKWISE)[::-1]
    montante = cv2.rotate(a[q["montante"][0]:q["montante"][1], c0:c1], cv2.ROTATE_90_CLOCKWISE)[::-1]
    vx0, vy0, vx1, vy1 = q["vao"]
    w = vx1 - vx0
    esq = (w - montante.shape[1]) // 2
    dir_ = w - montante.shape[1] - esq
    janela = np.concatenate([pano[:, :esq], montante, pano[:, ::-1][:, :dir_]], axis=1)
    out[vy0:vy1, vx0:vx1] = cv2.resize(janela, (w, vy1 - vy0), interpolation=cv2.INTER_AREA)
    print("    escritório: janela no vão de cima, no lugar da porta de correr")
    return out


def cadeiras(out):
    q = CADEIRAS
    a = out.copy()
    fx0, fy0, fx1, fy1 = q["fonte"]
    sprite = a[fy0:fy1, fx0:fx1].astype(np.float32)
    rx0, ry0, rx1, ry1 = q["piso_ref"]
    piso = np.median(a[ry0:ry1, rx0:rx1].reshape(-1, 3).astype(np.float32), axis=0)
    lum, lum_piso = sprite.mean(axis=2), float(piso.mean())
    alfa = np.clip((lum - lum_piso - 10) / 20, 0, 1)                   # a cadeira (clara)
    sombra = np.clip((lum_piso - lum - 6) / 14, 0, 1) * (1 - lum / lum_piso)   # escurecimento
    sombra[:, -2:][lum[:, -2:] < 120] = 0                               # borda da mesa de origem
    alfa = np.dstack([alfa, sombra])
    cx, cy = q["centro_fonte"][0] - fx0, q["centro_fonte"][1] - fy0
    e = q["escala"]
    for nome, (tx, ty), giro, (eixo, tampo, faixa) in q["lugares"]:
        sp, al, ccx, ccy = sprite, alfa, cx, cy
        if giro == "horario":                                      # de frente para baixo
            sp, al = cv2.rotate(sp, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
            ccx, ccy = sprite.shape[0] - 1 - cy, cx
        h, w = sp.shape[:2]
        x0, y0 = int(np.floor(tx - ccx * e)) - 1, int(np.floor(ty - ccy * e)) - 1
        W, H = int(np.ceil(w * e)) + 3, int(np.ceil(h * e)) + 3
        M = np.float32([[e, 0, tx - ccx * e - x0], [0, e, ty - ccy * e - y0]])
        spw = cv2.warpAffine(sp, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        alw = cv2.warpAffine(al, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
        orig = a[y0:y0 + H, x0:x0 + W].astype(np.float32)
        pos = (np.arange(W) + x0)[None, :] if eixo == "x" else (np.arange(H) + y0)[:, None]
        alw[np.broadcast_to(pos >= tampo, alw.shape[:2])] = 0          # o tampo fica por cima
        a_c, a_s = alw[..., :1], alw[..., 1:]
        reg = orig * (1 - a_s)
        reg = reg * (1 - a_c) + spw * a_c
        # na faixa da sombra da escrivaninha, a cadeira recebe a mesma sombra (razão sobre o piso)
        lum = orig.mean(axis=2)
        if eixo == "x":
            piso_f = np.median(lum[:, faixa - 6 - x0:faixa - 1 - x0])
            for k in range(faixa, tampo):
                razao = min(1.0, float(np.median(lum[:, k - x0])) / piso_f)
                reg[:, k - x0] = orig[:, k - x0] * (1 - a_c[:, k - x0]) + reg[:, k - x0] * razao * a_c[:, k - x0]
        else:
            piso_f = np.median(lum[faixa - 6 - y0:faixa - 1 - y0, :])
            for k in range(faixa, tampo):
                razao = min(1.0, float(np.median(lum[k - y0, :])) / piso_f)
                reg[k - y0] = orig[k - y0] * (1 - a_c[k - y0]) + reg[k - y0] * razao * a_c[k - y0]
        out[y0:y0 + H, x0:x0 + W] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    cadeira da escrivaninha ({nome}) em ({tx}, {ty})")
    return out


def cuba_bhm1(out):
    q = CUBA_BHM1
    x0, y0, x1, y1 = q["bancada"]
    r0, r1 = q["lisa"]
    t = out[r0:r1, x0:x1].copy()
    out[y0:y1, x0:x1] = np.concatenate([t, t[::-1]] * ((y1 - y0) // (2 * t.shape[0]) + 1), axis=0)[:y1 - y0]
    cx0, cy0, cx1, cy1 = q["bacia_cima"]                       # torneira em cima: desenho virado
    reg = np.ascontiguousarray(out[cy0:cy1, cx0:cx1][::-1])
    out[cy0:cy1, cx0:cx1] = cuba(reg, (0, 0, cx1 - cx0, cy1 - cy0))[::-1]
    out = cuba(out, q["bacia_baixo"])                          # torneira embaixo
    print("    BH master 1: cuba esculpida do PDF, com as torneiras nas pontas")
    x0, y0, x1, y1 = q["bhm2_bancada"]
    r0, r1 = q["bhm2_lisa"]
    t = out[r0:r1, x0:x1].copy()
    out[y0:y1, x0:x1] = np.concatenate([t, t[::-1]] * ((y1 - y0) // (2 * t.shape[0]) + 1), axis=0)[:y1 - y0]
    cx0, cy0, cx1, cy1 = q["bhm2_cuba"]
    reg = np.ascontiguousarray(out[cy0:cy1, cx0:cx1][::-1])
    out[cy0:cy1, cx0:cx1] = cuba(reg, (0, 0, cx1 - cx0, cy1 - cy0))[::-1]
    print("    BH master 2: cuba com a torneira em cima, como no PDF")
    return out


def pivotante(out):
    q = PIVOTANTE
    y0, y1 = q["linhas"]
    de, ate, fx = q["de"], q["ate"], q["fonte_x"]
    out[y0:y1, de:ate] = out[y0:y1, fx:fx + ate - de]
    p0, p1 = q["ponta"]
    out[y0:y1, ate - (p1 - p0):ate] = out[y0:y1, p0:p1][:, ::-1]
    print(f"    porta pivotante: folha estendida até o fim do PDF (x {ate})")
    return out


def arcos_no_granito(out, A, chapada):
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
            p = np.array([p2r(pt.x, pt.y) for pt in it[1:5]])
            t = np.linspace(0, 1, 60)[:, None]
            curva = ((1 - t) ** 3 * p[0] + 3 * (1 - t) ** 2 * t * p[1] + 3 * (1 - t) * t ** 2 * p[2] + t ** 3 * p[3])
            pts = np.round((curva - [x0, y0]) * SS).astype(np.int32)
            cv2.polylines(f, [pts], False, 255, max(1, int(round(q["larg"] * SS))), cv2.LINE_AA)
        a = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * g
        a = a[..., None]
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.array(q["cor"], np.float32) * a, 0, 255).astype(np.uint8)
        n += 1
    print(f"    {n} arcos de porta sobre o granito em cinza")
    return out


def bancos_camas(out):
    q = BANCOS
    a = out.copy()
    for nome, (y0, y1), (s0, s1), d, tapete in q["encurtar"]:
        out[y0:y1, s0 + d:s1 + d] = a[y0:y1, s0:s1]                   # a ponta vem para o pé do PDF
        if tapete:                                                      # vão: só as colunas de tapete
            t0, t1 = tapete
            for k in range(abs(d)):
                out[y0:y1, s0 + k] = a[y0:y1, t1 - 1 - (k % (t1 - t0))]
        elif d > 0:                                                     # pé à esquerda: vão à esquerda
            for k in range(d):
                out[y0:y1, s0 + k] = a[y0:y1, s0 - 1 - k]
        else:                                                           # pé à direita: vão à direita
            for k in range(-d):
                out[y0:y1, s1 - 1 - k] = a[y0:y1, s1 + k]
        print(f"    {nome}: cama no comprimento do PDF ({d:+d} px)")
    fonte = cv2.imread(str(q["fonte"])).astype(np.float32)
    for nome, modelo, (dx0, dy0, dx1, dy1), girar in q["lugares"]:
        (cx0, cy0, cx1, cy1), (bx0, by0, bx1, by1), piso = q["modelos"][modelo]
        spr = fonte[cy0:cy1, cx0:cx1].copy()
        bx0, by0, bx1, by1 = bx0 - cx0, by0 - cy0, bx1 - cx0, by1 - cy0
        corpo = np.zeros(spr.shape[:2], np.float32)
        corpo[by0:by1, bx0:bx1] = 1
        fator = np.where(corpo > 0, 1.0, np.clip(spr.mean(axis=2) / piso, 0, 1)).astype(np.float32)
        if girar:
            W = spr.shape[1]
            spr, corpo, fator = (cv2.rotate(m, cv2.ROTATE_90_COUNTERCLOCKWISE) for m in (spr, corpo, fator))
            bx0, by0, bx1, by1 = by0, W - bx1, by1, W - bx0
        sx, sy = (dx1 - dx0) / (bx1 - bx0), (dy1 - dy0) / (by1 - by0)
        jx0, jy0 = int(np.floor(dx0 - bx0 * sx)) - 1, int(np.floor(dy0 - by0 * sy)) - 1
        jw = int(np.ceil(spr.shape[1] * sx)) + 3
        jh = int(np.ceil(spr.shape[0] * sy)) + 3
        M = np.float32([[sx, 0, dx0 - bx0 * sx - jx0], [0, sy, dy0 - by0 * sy - jy0]])
        spr_w = cv2.warpAffine(spr, M, (jw, jh), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
        al = cv2.warpAffine(corpo, M, (jw, jh), flags=cv2.INTER_LINEAR, borderValue=0)[..., None]
        fa = cv2.warpAffine(fator, M, (jw, jh), flags=cv2.INTER_LINEAR, borderValue=1)[..., None]
        reg = out[jy0:jy0 + jh, jx0:jx0 + jw].astype(np.float32) * fa
        out[jy0:jy0 + jh, jx0:jx0 + jw] = np.clip(reg * (1 - al) + spr_w * al, 0, 255).astype(np.uint8)
        print(f"    banco ({modelo}) ao pé da cama: {nome}")
    return out


def vaso_masc(out):
    q = VASO_MASC
    a = out.copy()
    x0, y0, x1, y1 = q["apagar"]
    d = q["piso_dx"]
    out[y0:y1, x0:x1] = a[y0:y1, x0 + d:x1 + d]
    fx0, fy0, fx1, fy1 = q["fonte"]
    spr = a[fy0:fy1, fx0:fx1].astype(np.float32)[:, ::-1]                # espelhado: parede à direita
    alfa = np.clip((np.abs(spr.mean(axis=2) - q["piso"]) - 6) / 14, 0, 1)
    w = fx1 - fx0
    bx0, by0, bx1, by1 = q["corpo"]
    bx0, bx1 = w - (bx1 - fx0), w - (bx0 - fx0)
    by0, by1 = by0 - fy0, by1 - fy0
    dx0, dy0, dx1, dy1 = q["destino"]
    sx, sy = (dx1 - dx0) / (bx1 - bx0), (dy1 - dy0) / (by1 - by0)
    jx0, jy0 = int(np.floor(dx0 - bx0 * sx)) - 1, int(np.floor(dy0 - by0 * sy)) - 1
    jw, jh = int(np.ceil(w * sx)) + 3, int(np.ceil(spr.shape[0] * sy)) + 3
    M = np.float32([[sx, 0, dx0 - bx0 * sx - jx0], [0, sy, dy0 - by0 * sy - jy0]])
    spr_w = cv2.warpAffine(spr, M, (jw, jh), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
    al = cv2.warpAffine(alfa, M, (jw, jh), flags=cv2.INTER_LINEAR, borderValue=0)[..., None]
    reg = out[jy0:jy0 + jh, jx0:jx0 + jw].astype(np.float32)
    out[jy0:jy0 + jh, jx0:jx0 + jw] = np.clip(reg * (1 - al) + spr_w * al, 0, 255).astype(np.uint8)
    print("    lavabo masculino: vaso suspenso branco, como os outros")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] chuveiros de teto")
    out = chuveiros_teto(out)
    print("[2] plantas fora do lote")
    base, chapada, A = alinhar_base(orig)
    out = fora_do_lote(out, base)
    print("[3] jardins de inverno")
    out = jardins_de_inverno(out)
    out = portas_de_vidro(out, base, chapada)
    print("[4] cozinha")
    out = cozinha(out)
    print("[5] quarto externo")
    out = quarto_externo(out)
    print("[6] tanques da área de serviço")
    out = tanques(out)
    print("[7] poltronas a mais no estar")
    out = poltronas_estar(out)
    print("[8] estar conforme o PDF")
    out = estar(out, A)
    print("[9] banquetas a mais na gourmet")
    out = banquetas(out)
    print("[10] cooktops")
    out = cooktops(out)
    print("[11] porta do box do BH master 2")
    out = porta_box(out, A)
    print("[12] degraus da escada estreita")
    out = escada(out)
    print("[13] elevador")
    out = elevador(out)
    print("[14] chuveiro externo")
    out = chuveiro_externo(out)
    print("[15] degraus largos")
    out = degraus_largos(out)
    print("[16] aparador do hall")
    out = aparador_hall(out)
    print("[17] lavabo e adega")
    out = lavabo_adega(out)
    print("[18] janela do escritório")
    out = janela_escritorio(out)
    print("[19] cadeiras das escrivaninhas")
    out = cadeiras(out)
    print("[20] cuba do BH master 1")
    out = cuba_bhm1(out)
    print("[21] porta pivotante principal")
    out = pivotante(out)
    print("[22] arcos das portas sobre o granito")
    out = arcos_no_granito(out, A, chapada)
    print("[23] bancos ao pé das camas")
    out = bancos_camas(out)
    print("[24] vaso do lavabo masculino")
    out = vaso_masc(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[25] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

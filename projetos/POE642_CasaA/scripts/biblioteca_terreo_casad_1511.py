"""A proposta de 15/11 no Térreo da Casa D: a biblioteca e as notas do cliente (Revisão das Plantas 2).

Usuário: "cadeiras terracota, lavabo granito marrom, pode aplicar", sobre a proposta
(`POE642_CasaD/renders/POE642_CasaD_PH_Terreo_1511_proposta_{1,2,3}.jpg`, `proposta_biblioteca_casad_1511.py`). As peças
e as funções são as das Casas A, B e C (`mobiliario_terreo_casac_1311`, `biblioteca_terreo_casac_1311`,
`regras_terreo_casab_1311`), nos desenhos do PDF da Casa D (os índices de `F.Quadro("Terreo")` depois de
`final3840_casad.contexto_d()`; px da final de 3840):
- **Suítes** (`CAMAS`, `CRIADOS`, `BANCOS`, `POLTRONAS`, `CADEIRAS`): a king A na suíte master (a cabeceira embaixo) e a
  casal A nas suítes 1 e 2 (a cabeceira à direita e à esquerda), com a manta de tricô caída e o travesseiro extra, cada
  quarto num tom leve (como na Casa C); os criados da Casa A com o abajur (redondos na master, como no PDF); o banco B1
  de veludo ao pé de cada cama; a poltrona e o pufe da master, a poltrona A e o pufe na suíte 2, a frente para o pufe; a
  cadeira de escritório nas escrivaninhas da master e da suíte 1, 1/3 sob o tampo.
- **Banhos** (`PECAS`, `DUPLA`, `CHUVEIROS`): a bancada dupla esculpida no banho master (as cubas nas do PDF), a cuba
  esculpida de travertino nos banhos 1, 2 e 3, as bacias Carrara brancas, os chuveiros desenhados em planta.

  python3 biblioteca_terreo_casad_1511.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final e os antes e depois
`POE642_CasaD/renders/POE642_CasaD_PH_Terreo_1511_<trecho>_antes_depois.jpg`.
"""

import argparse
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import final3840_casad as D                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402
import biblioteca_subsolo_casab_1311 as BB       # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import regras_terreo_casab_1311 as RT            # noqa: E402
import mobiliario_terreo_casac_1311 as MB        # noqa: E402
import camas_casac_1311 as CM                    # noqa: E402
import manta_caida_casac_1311 as MC              # noqa: E402

CASA_D = AQUI.parents[1] / "POE642_CasaD"
R = CASA_D / "renders"
FINAL = R / "POE642_CasaD_PH_Terreo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "b606ec6"
PX_M = B1.PX_M

# (15/11, usuário: "use tom terracota, bege e areia nos quartos") um tom por quarto, na manta de tricô caída, no
# travesseiro extra e no veludo do banco de pé de cama: terracota na suíte master, bege na suíte 1, areia na suíte 2; a
# roupa de cama clara (off-white e branco). RGB da manta (na escala de `camas_casac_1311.TONS`, a luz do tricô por cima)
# e BGR do veludo (como `revisao_terreo_casac_1311.SOBRIOS`, que vale a mediana vista de cima)
QUARTOS = {"terracota": {"manta": (196, 136, 108), "veludo": (78, 108, 168)},
           "bege": {"manta": (224, 210, 188), "veludo": (172, 198, 214)},
           "areia": {"manta": (212, 190, 156), "veludo": (140, 178, 200)}}
# as camas: (nome, caixa px (a do PDF), giro (0: cabeceira em cima; 180: embaixo; 90: à esquerda; -90: à direita), tipo,
# roupa, o tom do quarto, o lado da manta)
CAMAS = [("suíte master", (800.6, 1405.1, 918.2, 1550.8), 180.0, "king", "off-white", "terracota", "esq"),
         ("suíte 1", (1320.7, 1541.8, 1440.1, 1649.3), -90.0, "casal", "off-white", "bege", "esq"),
         ("suíte 2", (1805.5, 1541.8, 1924.9, 1649.3), 90.0, "casal", "branco", "areia", "dir")]
# os bancos de pé de cama (B1) nos retângulos do PDF, no veludo do tom do quarto
# (16/11, usuário, na suíte master: "aqui não é recamier, mas armário com cor sólida") o 97352 sai dos bancos e vai para
# os armários lisos (`ARMARIOS`)
BANCOS = [(104083, "bege"), (104160, "areia")]
# os criados: (índice, forma, giro, diâmetro do abajur)
CRIADOS = [(97046, "redondo", 0.0, 19.0), (97058, "redondo", 0.0, 19.0), (104078, "ret", -90.0, 17.0),
           (104073, "ret", -90.0, 17.0), (104155, "ret", 90.0, 17.0), (104150, "ret", 90.0, 17.0)]
POLTRONAS = [("suíte master", "suite-master/poltrona", 97070, "suite-master/pufe", 97236),
             ("suíte 2", "sala-intima/poltrona-a", 94151, "suite-master/pufe", 104165)]
# as cadeiras de escritório: (nome, índices da cadeira, a borda da mesa (px), o lado da mesa, a mesa (px))
CADEIRAS = [("suíte master", (97526,), 1046.0, "dir", (1046, 1434, 1082, 1553)),
            ("suíte 1", (93564, 93565), 1452.3, "cima", (1291, 1422, 1440, 1453))]

# os banhos: ("B1", png, cx, cy, larg, alt, giro (a parede: 0 em cima, 180 embaixo, 90 à esquerda, -90 à direita),
# sombra, extra); ("cuba", c): o miolo da cuba a c px da ponta direita do PNG
PECAS = {
    "banho 1": [("B1", "banho-1/cuba-esculpida-travertino", 1108.8, 1586.1, 70.6, 36.0, 90.0, "baixa", ("cuba", 35.3)),
                ("B1", "banho-1/bacia-carrara", 1106.15, 1651.75, 21.1, 30.7, 90.0, "baixa", None)],
    "banho 2": [("B1", "banho-2/cuba-esculpida-travertino", 2135.6, 1586.1, 70.6, 36.0, -90.0, "baixa", ("cuba", 35.3)),
                ("B1", "banho-2/bacia-carrara", 2138.3, 1649.85, 21.1, 30.7, -90.0, "baixa", None)],
    "banho 3": [("B1", "banho-3/cuba-esculpida-travertino", 2180.6, 1586.1, 70.6, 36.0, 90.0, "baixa", ("cuba", 35.3)),
                ("B1", "banho-3/bacia-carrara", 2177.9, 1649.35, 21.1, 30.7, 90.0, "baixa", None)],
    "banho master": [("B1", "banho-master/bacia-carrara", 916.65, 1726.55, 21.1, 30.7, 180.0, "baixa", None)],
}
# a bancada dupla do banho master: a bancada do PDF (px, a parede em cima) e o miolo das 2 cubas ao longo dela
DUPLA = {"png": "banho-master/bancada-dupla-esculpida-render-v2", "c": (793.7, 1563.3, 929.6, 1598.4), "giro": 0.0,
         "cubas": (833.55, 889.45), "colunas": {"canto": 30, "cuba1": (60, 335), "cuba2": (452, 725)}}
# os chuveiros de parede do PDF (a placa de 11,8 px e o braço até a parede): o desenho em planta da biblioteca, nítido
# (`chuveiro-quadrado-parede-planta`, como nos banhos da Casa B); a parede (x da face, o lado) e o piso de onde vem
CH_Q = "banho-1/chuveiro-quadrado-parede-planta"
CHUVEIROS = [{"nome": f"banho {n}", "placa_px": p, "png": CH_Q, "parede": w, "piso": (0, -1)}
             for n, p, w in (("master (box)", (791.4, 1708.8, 803.2, 1720.6), (774.3, "esq")),
                             ("master (meio)", (850.5, 1709.0, 862.3, 1720.8), (879.4, "dir")),
                             ("1", (1107.9, 1705.5, 1119.7, 1717.3), (1090.8, "esq")),
                             ("2", (2124.7, 1705.5, 2136.5, 1717.3), (2153.6, "dir")),
                             ("3", (2179.7, 1705.8, 2191.5, 1717.6), (2162.6, "esq")))]
# as claraboias do banho master (px: o retângulo de fora): o X sai, fica o retângulo tracejado, cinza e fino
# (`pedidos_terreo_casac_1311.claraboias`; Miro: "Representar as claraboias apenas com as linhas de fora, sem o X")
CLARABOIAS = [{"nome": "box do banho master", "ret": (774.3, 1702.8, 879.4, 1726.5), "antes": "preto"},
              {"nome": "bacia do banho master", "ret": (886.6, 1702.8, 947.5, 1726.5), "antes": "preto"}]
# (Miro: "Representar os armários e prateleiras sem textura. Com cor sólida e neutra como algumas casas acima", "Não é
# pedra, é armário", "Padronizar a cor de representação do guarda-roupa", "Continuar o guarda-roupa até o final") os
# armários e guarda-roupas (os retângulos da DOC_LINHAS E PROJEÇÕES) na cor dos armários das outras casas
# (`revisao_terreo_casac_1311.COZINHA`: o miolo liso, a face um tom abaixo no contorno e a sombra curta), sem as
# prateleiras e o veio; o L da suíte 1 vai inteiro até a parede de baixo (a ponta clara some)
ARMARIOS = {"closet master": 104098, "closet master 2 (banho)": 104114, "closet master 2 (banho 1)": 104109,
            "closet da suíte 1": 104124, "closet da suíte 2": 104132, "suíte 3": 104140, "sala íntima": 134,
            "suíte 2 (bancada)": 104093, "sala íntima, junto ao elevador": 104145, "suíte 2 (banho 2)": 104182,
            "louceiro": 104282, "despensa": 104290, "cozinha (pia)": 104246, "cozinha (geladeira)": 104241,
            "área de serviço (tanques)": 104277, "área de serviço": 104272, "DCE": 104231,
            # (16/11, usuário: "corrija esse armario do escritorio para o tom sólido") o da parede da direita do escritório
            "escritório (suíte 3)": 104221,
            # (16/11, usuário: "esse armario ao lado vaso na cor sólida de armário definido já. sem textura!") o do banho
            # gourmet, junto à bacia (DOC_LINHAS E PROJEÇÕES)
            "banho gourmet (junto à bacia)": 104298,
            # (16/11, usuário, ao pé da cama da master: "aqui não é recamier, mas armário com cor sólida")
            "suíte master (ao pé da cama)": 97352,
            # (16/11, usuário, no DCE: "o armario de baixo com cabide e o criado mudo na cor sólida") o criado-mudo junto
            # à cabeceira; o armário de baixo (DCE) vai aberto, com os cabides (`CABIDES`)
            "DCE (criado-mudo)": 104226}
# (16/11, usuário: "os armários do closet são representados com os cabides, igual as das casas A, B e C. isso vale
# para a casa E também. Os outros armários é que são representado com cor sólida definida na casa A.") os armários dos
# closets saem da cor lisa e vão abertos, com os cabides e o cabideiro (R11, `final3840_casae.armario_cabides`, o
# guarda-roupa da biblioteca de elementos); os em L e em U em trechos (pt do PDF), cada um com as portas para o miolo
# do closet; os outros armários seguem na cor lisa
ARMARIOS_CLOSET = ("closet master", "closet master 2 (banho)", "closet master 2 (banho 1)", "closet da suíte 1",
                   "closet da suíte 2", "DCE")
CABIDES = [("closet master 2 (esquerda)", (787.4, 1806.6, 821.5, 1880.3), "direita"),
           ("closet master 2 (direita)", (872.5, 1710.3, 906.5, 1880.3), "esquerda"),
           ("DCE (armário de baixo)", (2238.8, 834.3, 2295.5, 868.3), "cima")]
# (16/11, usuário: "faça o U no armário de forma contínua, sem barreiras"; "faz o L do armário sem barreiras, de forma
# contínua"; "igual ao que fizemos nas outras casas. revise para ver se tem algum assim e corrija") os armários em U e em L
# dos closets numa peça só, como na Casa B (`pedidos_terreo_casab_1211.closets_tb`, o desenho do 1º Pavimento da Casa A,
# `um_pav_casaa_1111._closet`): cada trecho sem o canto, os cantos à parte, os cabides até o canto, o cabideiro se
# encontrando no meio do canto, a moldura só por fora (pt). Os dois trechos do closet master 2 não se tocam: ficam
CLOSETS_CONTINUOS = {
    "closet master": {"trechos": [((367.9, 1744.3, 401.9, 1846.3), "direita"), ((401.9, 1710.3, 521.0, 1744.3), "baixo"),
                                  ((401.9, 1846.3, 600.3, 1880.3), "cima")],
                      "cantos": [(367.9, 1710.3, 401.9, 1744.3), (367.9, 1846.3, 401.9, 1880.3)]},
    "closet da suíte 1": {"trechos": [((915.0, 1611.1, 949.0, 1690.4), "direita"), ((949.0, 1577.0, 1017.0, 1611.1), "baixo")],
                          "cantos": [(915.0, 1577.0, 949.0, 1611.1)]},
    "closet da suíte 2": {"trechos": [((1890.1, 1611.1, 1924.1, 1690.4), "esquerda"),
                                      ((1822.1, 1577.0, 1890.1, 1611.1), "baixo")],
                          "cantos": [(1890.1, 1577.0, 1924.1, 1611.1)]},
    "semente": 1616}
# (Miro: "Nome e área do ambiente e metragem", nos closets) o nome e a área (m², das faces das paredes e dos armários
# do PDF) no corpo dos rótulos dos banhos (a Inter Regular dos rótulos, `retoque_1pav_casae.ROTULOS`, com o corpo medido
# no BANHO 1 da final: 46 px de largura; 15,5 px entre as bases), no miolo livre de cada closet
CLOSETS = {"corpo": (10.7, 10.7), "entrelinha": 15.5, "cor": (20, 20, 20),
           "rotulos": [("CLOSET", (514.6, 1562.7, 759.4, 1741.9), (655.0, 1648.0)),
                       ("CLOSET", (956.5, 1562.0, 1081.8, 1741.9), (1019.2, 1640.0)),
                       ("CLOSET", (1090.8, 1422.4, 1198.3, 1541.8), (1162.5, 1496.0)),
                       ("CLOSET", (2046.1, 1422.4, 2153.6, 1541.8), (2082.0, 1496.0))]}
# a suíte 3/escritório: na mesa do PDF (px), a cadeira de escritório do lado da janela e as de visita do outro lado, 1/3
# por baixo do tampo; (nome, png, a caixa da cadeira de antes (px), o lado da mesa, a borda da mesa, a largura (px))
MESA_S3 = (2362.5, 1553.8, 2410.3, 1673.2)
CADEIRAS_S3 = [("escritório", "escritorio/cadeira-escritorio", (2409, 1595, 2434, 1632), "esq", 2410.3, 34.0),
               ("visita (de cima)", "escritorio/cadeira-visitante", (2340, 1565, 2366, 1602), "dir", 2362.5, 30.0),
               ("visita (de baixo)", "escritorio/cadeira-visitante", (2340, 1625, 2366, 1662), "dir", 2362.5, 30.0)]
# (Miro: "Colocar cortina", suíte 3, a janela junto ao jardim) a cortina C4 no vão da janela (o vidro à direita; x da
# face de dentro e o trecho em y, px)
CORTINA_S3 = ("v", "direita", 2504.0, 1352.0, 1493.0)
# (Miro: "Melhorar a representação do painel (destacar mais em relação ao piso)") o painel de ripas de madeira de fora da
# janela da suíte 3 (px): a madeira um tom abaixo (`tom`) e o fio escuro em volta
PAINEL_S3 = {"ret": (2515, 1340, 2529, 1498), "tom": 0.72, "fio": (40, 52, 66)}
# (Miro: "A porta está 'entrando' na parede e camuflando com a cor do piso"; Subsolo: "Melhorar representação das portas
# de giro. Encostar nas paredes") as portas de giro como nas Casas B e C (`pedidos_terreo_casac_1311.portas`): quina com
# quina na ponta da parede, a folha de madeira, a soleira no bege da soleira do banho master (`soleira_px`)
PORTAS = {"soleira_px": (758, 1620, 764, 1655)}
# a sala íntima com o conjunto da Casa A (a regra das casas, como a sala TV da Casa C): o tapete, o sofá em L A no L do
# PDF, a poltrona A, a mesa lateral; a mesa de centro redonda de antes volta por cima; o vinílico refeito por baixo
SALA_INTIMA = {"tapete": 66515, "sofa": (126044, 125978), "poltrona": 125683, "mesas_laterais": (125976,),
               "mesas_centro": (125212,)}
# (Miro: "Não tem soleira", a passagem da suíte 2 para o closet) a soleira sai: o vinílico (px)
SEM_SOLEIRA = [(2037, 1481, 2047, 1538)]
# (usuário: "cadeiras terracota") o tecido das 10 cadeiras do jantar (o encosto e o assento greige, saturação >= `sat_min`
# e luz abaixo de `lum_max`, fora o tampo) em terracota (BGR), com a luz de cada px (a razão à mediana, ** `gama`); a
# madeira clara e a sombra no piso ficam
JANTAR = {"zona": (1893, 750, 2012, 968), "mesa": (1912, 765, 1991, 952), "sat_min": 38, "lum": (60, 172),
          "terracota": (66, 98, 164), "gama": 0.9}
# (Miro: "Usar a mesma representação de planta da casa A") os 2 vasos do hall: a folhagem A da sala íntima da Casa A
# (centro e diâmetro, px), a planta de antes sai (o travertino logo à esquerda, `BB.piso_desloc`)
VASOS_HALL = {"png": "sala-intima/vaso-folhagem-a", "vasos": [((2366, 912, 2426, 972), (2397.0, 943.0), 52.0, 0.0),
                                                              ((2370, 1143, 2426, 1195), (2398.0, 1169.0), 52.0, 140.0)]}
# (Miro: "Centralizar a seta com a abertura da porta, usando este modelo de seta") a seta comprida sai (o travertino logo
# abaixo) e entra o triângulo do modelo (o da Casa C), no meio do vão entre as duas paredes do hall (x da parede, o vão
# em y), a ponta para dentro (para a esquerda); comprimento e largura (px)
SETA_HALL = {"caixa": (2462, 1051, 2556, 1085), "x": 2436.0, "vao_y": (980.0, 1130.0), "comp": 18.0, "larg": 21.0,
             "cor": (20, 20, 20), "ss": 8}
# (Miro: "Representar um painel aqui", entre a escada do deck e o elevador) o vão do vidro de correr da circulação vira
# um painel de madeira (o retângulo da parede no PDF, px): a madeira escura dos brises, as ripas e o fio
PAINEL_ESCADA = {"ret": (1145.0, 1330.0, 1314.7, 1341.8), "madeira": (70, 98, 132), "ripa_px": 3.0, "ripa": 0.82,
                 "fio": (40, 52, 66), "ss": 8}
# (15/11, usuário: "remova o percentual definido de manchas do mármore bege bahia, como fizemos nas casas A, B e C") o
# Bege Bahia (a chapada 232: o deck, as escadas e os pisantes) com as manchas a 35% (`pedidos_subsolo_casac_1311.bege`,
# a regra de 10/11); os banhos das suítes e o WC DCE, que dividem a chapada 232 mas são o quartzito Aura, ficam de fora
# (os px da chapada 232 dentro destas caixas, px)
BEGE_FORA = [(770, 1550, 952, 1746), (1088, 1528, 1202, 1746), (2044, 1532, 2158, 1746), (2160, 1532, 2275, 1746),
             (2384, 525, 2481, 680)]
# (15/11, usuário: "vamos usar o tom sóbrio de grama que usamos nas casas A, B e C") o verde externo (o gramado, as
# árvores e os arbustos) refeito com o gramado da Casa B, como no Térreo da Casa C (`paisagismo_terreo_casac_1311`), e
# só 3 oliveiras (Miro: "No terreno não precisa representar muitas árvores"): (centro px, diâmetro px)
OLIVEIRAS = [((520, 300), 230), ((3120, 1520), 260), ((470, 1840), 170)]
# a gourmet, a cozinha e a área de serviço (os retângulos e os polígonos do PDF, ARQ_BANCADAS; px):
# - (Miro: "Geral: Não precisa representar os armários inferiores ou superiores com essa linha acima da bancada") a
#   bancada da pia gourmet de ponta a ponta no granito (a amostra limpa do piso, tecida), sem as divisões dos módulos e a
#   projeção do armário de cima, com a face um tom abaixo;
# - (Miro: "Representar a churrasqueira", a nota no módulo da esquerda) a grelha da Casa A no módulo da esquerda;
# - a cuba Franke com misturador na cuba do PDF; o cooktop de 4 bocas no lugar do de 5 (o granito correndo ao longo da
#   ilha, `RT.balcao`); as banquetas B nos 4 círculos do PDF, 40% do assento sob o tampo (o tampo volta por cima);
# - (Miro: "Aqui tem que representar dois painéis pivotantes") no lado do deck, dois painéis pivotantes fechados de
#   madeira clara, de ponta a ponta do vão;
# - (Miro: "Cor da ilha é no Dekton Danae", "Cor da bancada no dekton danae") a ilha e a bancada da pia da cozinha e a
#   bancada dos tanques no Dekton Danae (`terreo_casaa_1011.danae`), as cubas Franke (2 na cozinha, os 2 tanques) e o
#   cooktop de 4 bocas; a geladeira inox G2 nos 2 vãos do PDF (a frente para a cozinha)
GOURMET = {"pia": 68320, "granito_px": (1405, 530, 1470, 600), "face": 0.86, "semente": 1511,
           "churrasqueira": ((1395.3, 476.0, 1465.8, 523.5), 56.0),
           "cuba": (1558.95, 502.95, 38.2, 26.3),
           "cooktop_velho": (1530.4, 618.0, 1582.9, 647.8), "cooktop": (1556.65, 632.9, 31.0, 29.0),
           "ilha": (1454.5, 612.8, 1658.0, 685.0), "banquetas": (1493.4, 1535.15, 1576.95, 1618.75), "banqueta_d": 25.0,
           "banquetas_velhas": (1476, 685, 1636, 707), "deck_px": (1500, 735, 1600, 768),
           "paineis": {"x": (1390.5, 1396.5), "y": (558.0, 702.0), "folga": 1.5, "madeira": (150, 186, 214),
                       "fio": (70, 92, 118)}}
COZINHA = {"ilha": 68310, "pia": 52828, "tanques": 52187, "semente": 1512,
           "cubas": [("cozinha/pia", 1925.6, 391.85, 38.2, 26.3), ("cozinha/pia", 1965.6, 391.85, 38.2, 26.3),
                     ("serviço/tanque", 2317.05, 393.45, 37.9, 31.9), ("serviço/tanque", 2357.55, 393.45, 37.9, 31.9)],
           "cooktop": (1964.85, 499.25, 31.0, 29.0),
           "geladeiras": [(1864.8, 619.3, 1912.6, 667.1), (1912.6, 619.3, 1960.3, 667.1)]}
# (Miro: "Bancada na pedra marrom tabaco", "Cor do piso desse banheiro segue padrão dos outros dessa casa", WC DCE
# térreo) a bancada (px, menos a cuba) no granito marrom tabaco (o da gourmet); o piso no quartzito Aura dos banhos das
# suítes (a amostra limpa do banho 2, tecida), fora as peças (o que foge da mediana do piso, `obj`) e as paredes
WC_DCE = {"bancada": (2386.5, 526.8, 2410.0, 621.6), "cuba": (2392.0, 561.0, 2410.0, 587.5), "caixa": (2386, 526, 2477, 677),
          "quartzito_px": (2062, 1588, 2110, 1626), "obj": 30, "semente": 1513}
# (Miro: "Piso do gás também é no marrom tabaco") o piso do abrigo do gás (o miolo entre as paredes, a partir de
# `semente`), fora o rótulo, no granito marrom tabaco
GAS = {"caixa": (2552, 352, 2634, 428), "semente": (2575, 410), "miolo_img": ((366, 413), (2563, 2629))}
# (Miro: "Fazer uma linha contínua aqui pra linha tracejada não ficar voando", a divisa da área descoberta) o lado da
# direita do retângulo do X, contínuo, no tom do tracejado (px)
AREA_DESCOBERTA = {"linha": ((2347.0, 566.0), (2347.0, 676.5)), "cor": (226, 228, 230), "larg": 1.1, "ss": 8,
                   # o X do vazio, refeito tracejado depois do piso marrom novo (o tecido da amostra o cobria)
                   "x": [((2193.0, 566.0), (2347.0, 676.5)), ((2347.0, 566.0), (2193.0, 676.5))],
                   "traco": {"larg_px": 1.1, "traco_px": 7.0, "vao_px": 4.5}}
# (Subsolo, Miro: "Lembrar de usar para o piso marrom tabaco a referência colocada lá em cima para dar destaque para as
# bancadas e o marrom do piso ficar mais sóbrio"; as Casas A e B: "mais uniforme ... mais sóbrio") o granito do piso na
# amostra do cliente, como no Térreo da Casa B (`pedidos_terreo_casab_1211.marrom_tb`); as bancadas de granito ficam no
# tom escuro de antes (em destaque)
# (Miro: "Remover as linhas tracejadas do telhado ... Deixar apenas as que representam 'vazios', claraboias e
# pergolados"; "Tirar o X dos vãos do pergolado. Representar apenas a estrutura dele em si. Representar com uma cor
# cinza. Fazer os quadrados no pergolado de cima igual o debaixo ... Com linhas tracejadas") os tracejados claros da
# garagem de cima saem (o granito tecido de um trecho limpo entre os carros; o rótulo fica) e os dois escuros do telhado
# no hall (o travertino logo abaixo); o de baixo, sobre a grama, sai com o gramado novo. Os dois pergolados ficam só com
# os módulos da EST_LAJE do PDF (9 de 41,8 px a cada 53,7 px), retângulos tracejados em cinza fino
# (16/11, usuário: "Você verificou todas as portas ... não tem nenhuma porta flutuando?") a soleira da porta da área
# de serviço para o gás (`portas`) fica: a busca dos traços claros do telhado à esquerda a tomava por tracejado e a cobria
# de granito até y 472 (sobrava só o pé dela, solto no vão); `soleiras`: as caixas que a busca não toca (px)
PERGOLADOS = {"limpa": (2637, 330, 3212, 470), "esquerda": (2540, 338, 2648, 472), "gas": (2558, 354, 2627, 427), "soleiras": [(2551, 420, 2566, 488)], "rotulo": (2846, 417, 2942, 454), "lum": 128, "croma": 45,
              "granito_px": (2792, 520, 2834, 700),
              # (16/11) o trecho do hall começa depois da face da parede da adega (de x 2447, a cópia dos 5 px de
              # cima descia a parede de baixo da adega e as garrafas: um degrau de 5 px na parede)
              "hall": (2516, 896, 2618, 916), "hall_lum": 110, "hall_dy": 5,
              "x0": 2676.0, "passo": 53.7, "larg": 41.8, "n": 9, "ys": [(362.6, 458.1), (810.4, 900.0)],
              "traco": {"cor": (165, 165, 165), "larg_px": 1.0, "traco_px": 6.0, "vao_px": 4.0, "ss": 8}}
# a cama do DCE do Térreo (a caixa do PDF, a cabeceira em cima): a solteiro A com a peseira, na roupa branca e a peseira
# em areia (os tons dos quartos)
DCE = {"caixa": (2567.4, 528.0, 2627.1, 647.4), "giro": 0.0, "roupa": "branco", "tom": "areia"}
# (usuário: "lavabo granito marrom") a bancada e a cuba do lavabo em granito marrom tabaco, como no lavabo da Casa C de
# 15/11 (`revisao_terreo_casac_1511.lavabo_bancada`): as 2 peças da ARQ_BANCADAS (px; a de cima com a cuba)
LAVABO = {"pecas": [(2578.8, 1213.4, 2606.2, 1257.7), (2578.8, 1257.7, 2606.2, 1326.9)], "cuba": 0}
# (Miro: "Representar a janela", o jardim do lavabo) a janela do PDF entre o lavabo e o jardim (o vão da ARQ_PAREDE,
# px): o desenho da janela da suíte 3 da final de antes (a moldura clara e os vidros), no vão
JANELA_LAVABO = {"vao": (2607, 1210, 2617, 1330), "fonte": (2505, 1354, 2516, 1491)}
# (Miro: "Trocar essa representação do jardim de inverno e melhorar a linha tracejada"; proposta: "Jardim do lavabo como
# o de 4,79 m² da Casa A") os 2 jardins internos como na Casa C (`pedidos_terreo_casac_1311.jardins`): a grama no tom do
# gramado novo do lote, a sombra de contato junto às paredes, poucas plantas menores; no do lavabo, o X fino e claro
JARDINS = {
    "jardins": {
        "lavabo": {"caixa_px": (2617, 1211, 2700, 1330), "x_doc": True, "rotulo_px": (2634, 1238, 2692, 1264),
                   "plantas": [("arbusto_3", (2636, 1228), 0.40), ("palmeira_3", (2682, 1312), 0.60)]},
        "entre as suítes": {"caixa_px": (1458, 1691, 1787, 1751), "rotulo_px": (1600, 1696, 1678, 1730),
                            "plantas": [("palmeira_3", (1488, 1722), 0.70), ("arbusto_3", (1712, 1733), 0.45),
                                        ("arbusto_3", (1764, 1708), 0.40)]}},
    "contato": (0.20, 3.0), "semente": 1511, "gramado_px": (3000, 1250, 3080, 1300), "branco": (250, 250, 250),
    "floreira": {"px": (0, 0, 1, 1), "n": 1, "d_m": 0.01, "terra": (34, 44, 56), "terra_ruido": 0.18,
                 "verde": (60, 102, 88)}}
# (Miro: "Representar banco com estofamento") o banco de madeira à esquerda do estar da varanda (a caixa da DOC_LINHAS,
# px) vira o banco estofado dos brises da Casa A, a frente para o estar
BANCO_VARANDA = {"caixa": (1457.4, 1022.0, 1493.2, 1129.5), "png": "lounge-dos-brises/banco-brises"}
# (Miro: "Colocar a seta em todas as escadas e a descrição") como no Térreo da Casa C (`pedidos_terreo_casac_1311.escadas`):
# o triângulo cheio no 1º degrau de quem desce, a ponta para onde desce, e a descrição em duas linhas; a letra D do PDF
# fica. A escada larga do deck desce para o jardim (como a do deck da Casa C); a estreita, junto à suíte master, para o
# Subsolo (cai na escada do Subsolo)
ESCADAS = [
    {"nome": "escada larga do deck", "triangulo": [(713.5, 928.5), (724.5, 923.0), (724.5, 934.0)], "s_px": None,
     "texto": ("DESCE PARA O", "JARDIM"), "centro_x": 815.0, "base_y": 968.0, "fundo": None},
    {"nome": "escada estreita", "triangulo": [(1128.5, 1267.0), (1139.5, 1261.5), (1139.5, 1272.5)], "s_px": None,
     # (16/11, usuário: "coloque a descrição ao lado direito da seta triangular") à direita da seta, no meio da altura dela
     "texto": ("DESCE PARA O", "SUBSOLO"), "centro_x": 1218.0, "base_y": 1263.0, "fundo": None}]
# (Miro: "Demarcar melhor o perímetro da casa", a borda do deck) o fio da borda do Bege Bahia junto ao gramado (o px do
# Bege Bahia que toca a grama, um tom abaixo, e o px da grama junto a ele, menos)
PERIMETRO = {"bege": 0.62, "grama": 0.80, "area_min": 5000}
# (Miro: "Tirar o contorno dos mobiliários") o fio escuro e neutro em volta dos tapetes e das mesas retangulares (os
# retângulos do PDF, px): cada px dele, até `faixa` da borda, recebe o px de `passo` para o lado de onde está (dentro: a
# peça; fora: o piso)
CONTORNOS = {"rets": [(1467.4, 977.8, 1706.2, 1156.9), (1931.9, 1062.3, 2230.5, 1271.3), (1914.8, 768.5, 1986.4, 947.7),
                      (2058.1, 801.5, 2093.9, 921.0), (2306.7, 1365.8, 2485.8, 1485.3), (2362.5, 1553.8, 2410.3, 1673.2),
                      (1844.8, 1521.7, 1964.2, 1671.0)],
             "faixa": 2.2, "passo": 4, "escuro": 22, "croma": 34}
# o rótulo do SPA saía "A: 6,29 m" (sem o ²): o ² da Inter Regular logo depois do m (centro x, base, corpo, px)
SPA_M2 = {"cx": 1218.8, "base": 899.0, "corpo": 10.5, "cor": (40, 45, 45)}
# os rótulos reescritos (Inter Regular dos rótulos, `retoque_1pav_casae.ROTULOS`): GARAGEM (o piso marrom novo e a
# limpeza do pergolado o cobriam; em branco sobre o granito, a largura do GARAGEM de antes, 59 px) e DCE TÉRREO (na
# final de antes, em branco sobre a madeira e com as letras cortadas; no padrão dos outros quartos: escuro, o corpo dos
# rótulos dos banhos, no miolo livre entre a parede e a cama). (texto, centro x, base, corpo, cor); `apaga`: a caixa
# do rótulo de antes (o vinílico refeito por baixo, px)
ROTULOS_NOVOS = {"garagem": {"linhas": [("GARAGEM", 2893.5, 432.5), ("A: 62,95 m²", 2893.5, 448.0)], "largura": 59.0,
                             "cor": (236, 236, 236)},
                 "dce": {"linhas": [("DCE TÉRREO", 2525.0, 588.0), ("A: 6 m²", 2525.0, 603.5)], "corpo": 10.7,
                         "cor": (20, 20, 20), "apaga": (2490, 574, 2567, 607)},
                 # o LOUCEIRO e a DESPENSA: as prateleiras em U (lisas, na cor dos armários) cobriam o fim do texto;
                 # no meio do livre entre elas (centro do bloco, px), no corpo que cabe (`largura` da linha mais larga)
                 "armarios": {"itens": [(("LOUCEIRO", "A: 2,73 m²"), (2134.5, 442.0), (2096, 398, 2166, 446)),
                                        (("DESPENSA", "A: 2,59 m²"), (2134.5, 614.5), (2094, 586, 2166, 634))],
                              "largura": 50.0, "cor": (236, 236, 236), "entrelinha": 1.42, "altura": 0.73}}
ANTES_DEPOIS = {"planta": (440, 120, 3420, 1980), "suite_master": (500, 1321, 1100, 1757),
                "suites_1_2": (1079, 1393, 1990, 1757), "suite_3": (1740, 1200, 2560, 1757),
                "deck_piscina": (440, 330, 1420, 1360), "varanda_living": (1370, 690, 2640, 1340),
                "gourmet_cozinha_servico": (1370, 340, 2660, 720), "garagem": (2560, 300, 3260, 930),
                "lavabo_hall": (2330, 860, 2740, 1360)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            D.contexto_d()
            _Q["Q"] = F.Quadro("Terreo")
    return _Q["Q"]


_Q = {}


# ----------------------------------------------------------------------------------------------------------------------
def camas(out, par, q=CAMAS):
    for nome, (x0, y0, x1, y1), giro, tipo, roupa, tom, lado in q:
        enf = f"{tom} (Casa D)"
        r, g, b = QUARTOS[tom]["manta"]
        CM.TONS[enf] = (b, g, r)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        comp, larg = (y1 - y0, x1 - x0) if giro in (0.0, 180.0) else (x1 - x0, y1 - y0)
        with contextlib.redirect_stdout(io.StringIO()):
            P0 = CM.cama(tipo, roupa, enf, "nada")
            P, p = MC.manta_caida(P0, enf, lado)
        H0, W0 = P0.shape[:2]
        wt, ht = larg * (W0 + 2 * p) / W0, comp * (H0 + 2 * p) / H0
        out = MB.pousar(out, P, cx, cy, wt, ht, giro, None, par)
        al = RT._alfa_peca(P, cx, cy, wt, ht, giro, par.shape)
        out = _resto_fora(out, (x0, y0, x1, y1), al, par)
        print(f"    {nome}: a cama {tipo} A, roupa {roupa}, a manta de tricô caída e o travesseiro extra em {tom}")
    return out


def _resto_fora(out, c, al, par, folga=2):
    """O desenho de antes que sobra na caixa `c` (px) fora da peça nova (alfa `al` < 0,5; a cama da biblioteca tem os
    cantos arredondados e a borda macia): cada px recebe o seu reflexo do lado de fora da borda mais perto da caixa."""
    x0, y0, x1, y1 = c
    X0, Y0, X1, Y1 = int(np.floor(x0)) - folga, int(np.floor(y0)) - folga, int(np.ceil(x1)) + folga, int(np.ceil(y1)) + folga
    resto = np.zeros(par.shape, bool)
    resto[Y0:Y1, X0:X1] = True
    resto &= (al < 0.5) & ~par
    fonte = out.copy()
    H, W = par.shape
    for y, x in zip(*np.nonzero(resto)):
        d = [(x - X0, "x0"), (X1 - 1 - x, "x1"), (y - Y0, "y0"), (Y1 - 1 - y, "y1")]
        k, lado = min(d)
        if lado == "x0":
            xs, ys = X0 - 1 - k, y
        elif lado == "x1":
            xs, ys = X1 + k, y
        elif lado == "y0":
            xs, ys = x, Y0 - 1 - k
        else:
            xs, ys = x, Y1 + k
        if 0 <= xs < W and 0 <= ys < H and not par[ys, xs]:
            out[y, x] = fonte[ys, xs]
    return out


def bancos(Q, out, par, q=BANCOS):
    import revisao_terreo_casac_1311 as RC
    for i, tom in q:
        P, cx, cy, L, Dp, giro = RC._banco_png(RT.caixa_pdf(Q, i), "casal")
        out = MB.pousar(out, RC.veludo(P, QUARTOS[tom]["veludo"]), cx, cy, L, Dp, giro, "movel", par)
    print(f"    bancos de pé de cama: o B1 nos {len(q)} retângulos do PDF, no veludo do tom de cada quarto "
          f"({', '.join(t for _, t in q)})")
    return out


def cadeiras(Q, out, par, q=CADEIRAS, qc=MB.CADEIRA_ESC):
    """Como `mobiliario_terreo_casac_1311.cadeiras_escritorio`, com o lado "cima" (a mesa em cima da cadeira)."""
    for nome, ids, borda, lado, mesa_px in q:
        _, m = MB.contorno(Q, list(ids))
        ys, xs = np.nonzero(m)
        X0, Y0, X1, Y1 = xs.min() - 3, ys.min() - 3, xs.max() + 4, ys.max() + 4
        buraco = np.zeros(par.shape, bool)
        buraco[Y0:Y1, X0:X1] = True
        mx0, my0, mx1, my1 = mesa_px
        mesa = np.zeros(par.shape, bool)
        mesa[my0:my1, mx0:mx1] = True
        buraco &= ~mesa & ~par
        out = MB.piso_vinilico(Q, out, buraco)
        fonte = out.copy()
        P = MB.ler(qc["png"])
        wt = qc["larg"]
        ht = wt * P.shape[0] / P.shape[1]
        f = qc["sob"]
        if lado == "dir":
            cx, cy, g = borda - ht / 2 + f * ht, (ys.min() + ys.max()) / 2, 90.0
        elif lado == "esq":
            cx, cy, g = borda + ht / 2 - f * ht, (ys.min() + ys.max()) / 2, -90.0
        elif lado == "cima":
            cx, cy, g = (xs.min() + xs.max()) / 2, borda + ht / 2 - f * ht, 180.0
        else:
            cx, cy, g = (xs.min() + xs.max()) / 2, borda - ht / 2 + f * ht, 0.0
        out = MB.pousar(out, P, cx, cy, wt, ht, g, "movel", par)
        ca = RT._alfa_peca(P, cx, cy, wt, ht, g, par.shape)
        a = mesa.astype(np.float32)
        Ya, Yb, Xa, Xb = my0 - 6, my1 + 6, mx0 - 6, mx1 + 6
        out[Ya:Yb, Xa:Xb] = RT.mesa_sobre(out[Ya:Yb, Xa:Xb], fonte[Ya:Yb, Xa:Xb], a[Ya:Yb, Xa:Xb], ca[Ya:Yb, Xa:Xb])
        print(f"    {nome}: a cadeira de escritório, 1/3 por baixo da escrivaninha")
    return out


def bancada_dupla(out, par, q=DUPLA):
    """A bancada dupla na parede de cima: o comprimento em x (como `biblioteca_terreo_casac_1311.dupla_png`, que é na
    parede da esquerda)."""
    P = B1.ler_png(q["png"])
    x0, y0, x1, y1 = q["c"]
    L, Dp = x1 - x0, y1 - y0
    s = Dp / P.shape[0]
    k = q["colunas"]["canto"]
    a1, b1 = q["colunas"]["cuba1"]
    a2, b2 = q["colunas"]["cuba2"]
    c1, c2 = q["cubas"][0] - x0, q["cubas"][1] - x0
    w = P.shape[1]
    esq = (c1 - (b1 - a1) * s / 2) / s - k
    meio = (c2 - c1 - ((b1 - a1) + (b2 - a2)) * s / 2) / s
    dir_ = (L - c2 - (b2 - a2) * s / 2) / s - k
    P = BS.esticar(P, 1, [(0, k, None), (k, a1, esq), (a1, b1, None), (b1, a2, meio), (a2, b2, None),
                          (b2, w - k, dir_), (w - k, w, None)])
    o = BT.pousar(out.astype(np.float32), P, (x0 + x1) / 2, (y0 + y1) / 2, L, Dp, q["giro"], BT.SOMBRAS["baixa"], PX_M,
                  nao=par)
    print(f"    banho master: a bancada dupla esculpida em {L:.1f} x {Dp:.1f} px, as cubas nas do PDF")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def pecas(out, par, q=PECAS):
    n = 0
    for amb, ps in q.items():
        for p in ps:
            out = RT.pousar_bib(out, RT.item_bib(*p), par)
            n += 1
    print(f"    banhos: {n} peças da biblioteca ({', '.join(q)})")
    return out


def chuveiros(out, par, q=CHUVEIROS):
    import biblioteca_terreo_casac_1311 as BC
    return BC.chuveiros(out, par, [], q)


def claraboias(Q, out, q=CLARABOIAS):
    import pedidos_terreo_casac_1311 as PT
    return PT.claraboias(Q, out, q)


def armarios(Q, out, par, q=ARMARIOS, closets=ARMARIOS_CLOSET, cabides=CABIDES, continuos=CLOSETS_CONTINUOS):
    import revisao_terreo_casac_1311 as RC
    import final3840_casae as FE
    q = {k: v for k, v in q.items() if k not in closets}
    import revisao_terreo_casac_1511 as R15
    c = RC.COZINHA
    o = out.astype(np.float32)
    H, W = par.shape
    n = 0
    for nome, i in q.items():
        a, m = RT.mascara_pdf(Q, [i])
        a = a.astype(np.float32) * ~par
        m = m & ~par
        o *= (1 - c["sombra"] * R15._sombra(a, W, H))[..., None]
        borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        cor = np.float32(c["cor_armario"])[None, None] * np.where(borda, c["face"], 1.0)[..., None]
        o = o * (1 - a[..., None]) + cor * a[..., None]
        n += int(m.sum())
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    with contextlib.redirect_stdout(io.StringIO()):
        for k, (nome, r, lado) in enumerate(cabides):
            out = FE.armario_cabides(Q, out, r, lado, semente=57 + k, nome=nome)
    import um_pav_casaa_1111 as U
    rng = np.random.default_rng(continuos["semente"])
    nomes = [k for k in continuos if k != "semente"]
    for nome in nomes:
        out = U._closet(Q, out, continuos[nome], dict(U.CLOSETS_1P), rng)
    print(f"    armários: {len(q)} na cor dos armários, lisos ({n} px): {', '.join(q)}; os {len(closets)} dos closets "
          f"abertos, com os cabides ({', '.join(nomes)} numa peça só, em U e em L, sem a divisão no canto; o master 2 em "
          f"{len(cabides)} trechos)")
    return out


def spa_m2(out, q=SPA_M2):
    import revisao_terreo_casac_1411 as R14
    from rodape_entrega import FONTES
    out = R14.desenhar_linhas(out, [("²", str(FONTES / "Inter-Regular.otf"), q["corpo"], q["cx"], q["base"])], q["cor"])
    print("    piscina: o ² do rótulo do SPA")
    return out


def rotulos_novos(Q, out, par, q=ROTULOS_NOVOS):
    import revisao_terreo_casac_1411 as R14
    from PIL import ImageFont
    from rodape_entrega import FONTES
    fonte = str(FONTES / "Inter-Regular.otf")
    g = q["garagem"]
    corpo = 400 * g["largura"] / ImageFont.truetype(fonte, 400).getlength(g["linhas"][0][0])
    out = R14.desenhar_linhas(out, [(t, fonte, corpo, cx, b) for t, cx, b in g["linhas"]], g["cor"])
    d = q["dce"]
    x0, y0, x1, y1 = d["apaga"]
    reg = out[y0:y1, x0:x1].astype(np.int16)
    claro = (reg.min(axis=2) > 150) & ((reg.max(axis=2) - reg.min(axis=2)) < 45)
    bur = np.zeros(par.shape, bool)
    bur[y0:y1, x0:x1] = cv2.dilate(claro.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    out = MB.piso_vinilico(Q, out, bur & ~par)
    out = R14.desenhar_linhas(out, [(t, fonte, d["corpo"], cx, b) for t, cx, b in d["linhas"]], d["cor"])
    a = q["armarios"]
    f400 = ImageFont.truetype(fonte, 400)
    corpo_a = min(400 * a["largura"] / (f400.getbbox(t[0])[2] - f400.getbbox(t[0])[0]) for t, _, _ in a["itens"])
    for linhas, (cx, cy), (x0, y0, x1, y1) in a["itens"]:
        reg = np.ascontiguousarray(out[y0:y1, x0:x1])
        I = reg.astype(np.int16)
        claro = (((I.min(axis=2) > 140) & ((I.max(axis=2) - I.min(axis=2)) < 50)).astype(np.uint8)
                 & (~par[y0:y1, x0:x1]).astype(np.uint8))
        out[y0:y1, x0:x1] = cv2.inpaint(reg, cv2.dilate(claro, np.ones((3, 3), np.uint8)) * 255, 3, cv2.INPAINT_TELEA)
        e = a["entrelinha"] * corpo_a
        b0 = cy - ((len(linhas) - 1) * e - a["altura"] * corpo_a) / 2
        out = R14.desenhar_linhas(out, [(t, fonte, corpo_a, cx, b0 + i * e) for i, t in enumerate(linhas)], a["cor"])
    print(f"    rótulos: GARAGEM reescrito ({corpo:.1f} px de corpo); DCE TÉRREO no padrão dos quartos; LOUCEIRO e "
          f"DESPENSA no meio do livre das prateleiras ({corpo_a:.1f} px)")
    return out


def rotulos_closets(out, q=CLOSETS):
    import revisao_terreo_casac_1411 as R14
    from rodape_entrega import FONTES
    linhas = []
    for nome, (x0, y0, x1, y1), (cx, base) in q["rotulos"]:
        area = (x1 - x0) * (y1 - y0) / PX_M ** 2
        txt = f"A: {area:.2f} m²".replace(".", ",")
        linhas += [(nome, str(FONTES / "Inter-Regular.otf"), q["corpo"][0], cx, base),
                   (txt, str(FONTES / "Inter-Regular.otf"), q["corpo"][1], cx, base + q["entrelinha"])]
        print(f"    {nome}: {txt}")
    return R14.desenhar_linhas(out, linhas, q["cor"])


def cadeiras_s3(Q, out, par, q=CADEIRAS_S3, mesa_px=MESA_S3):
    mx0, my0, mx1, my1 = mesa_px
    mesa = np.zeros(par.shape, bool)
    mesa[int(round(my0)):int(round(my1)), int(round(mx0)):int(round(mx1))] = True
    for nome, png, (x0, y0, x1, y1), lado, borda, wt in q:
        buraco = np.zeros(par.shape, bool)
        buraco[y0 - 2:y1 + 3, x0 - 2:x1 + 3] = True
        buraco &= ~mesa & ~par
        out = MB.piso_vinilico(Q, out, buraco)
        fonte = out.copy()
        P = MB.ler(png)
        ht = wt * P.shape[0] / P.shape[1]
        f = 1 / 3
        cy = (y0 + y1) / 2
        if lado == "dir":
            cx, g = borda - ht / 2 + f * ht, 90.0
        else:
            cx, g = borda + ht / 2 - f * ht, -90.0
        out = MB.pousar(out, P, cx, cy, wt, ht, g, "movel", par)
        ca = RT._alfa_peca(P, cx, cy, wt, ht, g, par.shape)
        a = mesa.astype(np.float32)
        Ya, Yb, Xa, Xb = int(my0) - 6, int(my1) + 6, int(mx0) - 6, int(mx1) + 6
        out[Ya:Yb, Xa:Xb] = RT.mesa_sobre(out[Ya:Yb, Xa:Xb], fonte[Ya:Yb, Xa:Xb], a[Ya:Yb, Xa:Xb], ca[Ya:Yb, Xa:Xb])
    print(f"    suíte 3: a cadeira de escritório e as 2 de visita na mesa, 1/3 por baixo do tampo")
    return out


def cortina_s3(out, q=CORTINA_S3):
    import regras_terreo_casab_1311 as RTB
    import biblioteca_terreo_casaa_1211 as BT_
    o, v, ex, t0, t1 = q
    P, cx, cy, wt, ht = RTB.cortina_desenho({"o": o, "v": v, "ex": ex, "t0": t0, "t1": t1}, dict(RTB.CORTINAS_TB))
    o_ = BT_.pousar(out.astype(np.float32), P, cx, cy, wt, ht, 0.0, BT_.SOMBRAS["movel"], PX_M)
    print("    suíte 3: a cortina C4 na janela junto ao jardim")
    return np.clip(np.round(o_), 0, 255).astype(np.uint8)


def painel_s3(out, q=PAINEL_S3):
    x0, y0, x1, y1 = q["ret"]
    reg = out[y0:y1, x0:x1].astype(np.int16)
    madeira = (reg[..., 2] - reg[..., 0] > 18) & (reg.mean(axis=2) > 60)
    madeira = cv2.morphologyEx(madeira.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
    o = reg.astype(np.float32)
    o[madeira] *= q["tom"]
    borda = madeira & ~cv2.erode(madeira.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    o[borda] = np.float32(q["fio"])
    out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    suíte 3: o painel de ripas um tom abaixo, com o fio ({int(madeira.sum())} px)")
    return out


def portas(Q, out, q=PORTAS):
    import pedidos_terreo_casac_1311 as PT
    return PT.portas(Q, out, dict(PT.PORTAS, soleira_px=q["soleira_px"], pular=()))


def sala_intima(Q, out, antes, par, q=SALA_INTIMA):
    _, tap = MB.contorno(Q, [q["tapete"]])
    _, sofa = MB.contorno(Q, list(q["sofa"]))
    _, pol = MB.contorno(Q, [q["poltrona"]])
    _, ml = MB.contorno(Q, list(q["mesas_laterais"]))
    velho = RT.dilatar(sofa | pol | ml | tap, 8) & ~par
    out = MB.piso_vinilico(Q, out, velho)
    x0, y0, x1, y1 = RT.caixa_pdf(Q, q["tapete"])
    out = MB.pousar(out, MB.ler("sala-intima/tapete"), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, "tapete", par)
    Ps = MB.ler("sala-intima/sofa-l-a")
    melhor = None
    for esp, P in ((False, Ps), (True, np.ascontiguousarray(Ps[:, ::-1]))):
        _, _, (iou, g, _, _) = MB.encaixar(Q, P, sofa, giros=(0, 90, 180, 270))
        if melhor is None or iou > melhor[0]:
            melhor = (iou, g, esp, P)
    iou, g, esp, P = melhor
    ys, xs = np.nonzero(sofa)
    bw, bh = float(xs.max() + 1 - xs.min()), float(ys.max() + 1 - ys.min())
    cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
    wt, ht = (bw, bh) if round(g) % 180 == 0 else (bh, bw)
    out = MB.pousar(out, P, cx, cy, wt, ht, g, "movel", par)
    out = MB.recorte(Q, out, antes, list(q["mesas_centro"]))
    for i in q["mesas_laterais"]:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        D_ = ((x1 - x0) + (y1 - y0)) / 2
        out = MB.pousar(out, MB.ler("sala-intima/mesa-lateral"), (x0 + x1) / 2, (y0 + y1) / 2, D_, D_, 0.0, "baixa", par)
    Pp = MB.ler("sala-intima/poltrona-a")
    cx, cy, (iou2, g2, wt2, ht2) = MB.encaixar(Q, Pp, pol)
    out = MB.pousar(out, Pp, cx, cy, wt2, ht2, g2, "movel", par)
    print(f"    sala íntima: o tapete, o sofá em L A ({'espelhado, ' if esp else ''}giro {g:.0f}°, {iou * 100:.0f}% sobre o "
          f"L do PDF), a poltrona A (giro {g2:.0f}°), a mesa lateral; a mesa de centro de antes por cima")
    return out


def sem_soleira(Q, out, par, q=SEM_SOLEIRA):
    for c in q:
        # (16/11) o vão branco da ARQ_PAREDE conta como parede no `par`, e o `piso_desloc` só troca o que não é
        # parede: a soleira ficava. O miolo do vão sai do `par` (as pontas das paredes, fora dele, ficam)
        p_ = par.copy()
        p_[c[1] + 1:c[3] - 1, c[0]:c[2]] = False
        out = BB.piso_desloc(out, c, p_, -1, 0)
    print("    suíte 2: a soleira da passagem do closet sai")
    return out


def jantar(out, q=JANTAR):
    x0, y0, x1, y1 = q["zona"]
    mx0, my0, mx1, my1 = q["mesa"]
    reg = out[y0:y1, x0:x1]
    hsv = cv2.cvtColor(reg, cv2.COLOR_BGR2HSV).astype(np.int16)
    Y = reg.astype(np.float32) @ np.float32([0.114, 0.587, 0.299])
    m = (hsv[..., 1] >= q["sat_min"]) & (Y > q["lum"][0]) & (Y < q["lum"][1])
    m[my0 - y0:my1 - y0, mx0 - x0:mx1 - x0] = False
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) > 0
    r = (Y / max(float(np.median(Y[m])), 1.0)) ** q["gama"]
    o = reg.astype(np.float32)
    novo = np.float32(q["terracota"])[None, None] * r[..., None]
    o[m] = novo[m]
    borda = (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~m & (Y < q["lum"][1] + 15)
    borda[my0 - y0:my1 - y0, mx0 - x0:mx1 - x0] = False
    o[borda] = o[borda] * 0.5 + novo[borda] * 0.5
    out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    jantar: o encosto e o assento das cadeiras em terracota ({int(m.sum())} px)")
    return out


def vasos_hall(out, par, q=VASOS_HALL):
    P = MB.ler(q["png"])
    for (x0, y0, x1, y1), (cx, cy), D_, giro in q["vasos"]:
        out = BB.piso_desloc(out, (x0, y0, x1, y1), par, -1, 0)
        out = MB.pousar(out, P, cx, cy, D_, D_, giro, "movel", par)
    print("    hall: os 2 vasos com a folhagem A da Casa A")
    return out


def _poligono(out, pts, cor, ss=8):
    pts = np.float32(pts)
    X0, Y0 = int(np.floor(pts[:, 0].min())) - 2, int(np.floor(pts[:, 1].min())) - 2
    X1, Y1 = int(np.ceil(pts[:, 0].max())) + 3, int(np.ceil(pts[:, 1].max())) + 3
    M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    cv2.fillPoly(M, [np.int32(np.round((pts - [X0, Y0]) * ss))], 255, cv2.LINE_AA)
    a = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + np.float32(cor) * a), 0, 255).astype(np.uint8)
    return out


def seta_hall(out, par, q=SETA_HALL):
    out = BB.piso_desloc(out, q["caixa"], par, 0, 1)
    cy = sum(q["vao_y"]) / 2
    x, c, l_ = q["x"], q["comp"], q["larg"]
    out = _poligono(out, [(x - c / 2, cy), (x + c / 2, cy - l_ / 2), (x + c / 2, cy + l_ / 2)], q["cor"], q["ss"])
    print(f"    hall: a seta comprida sai; o triângulo no meio do vão da porta (y {cy:.0f}), para dentro")
    return out


def painel_escada(out, q=PAINEL_ESCADA):
    x0, y0, x1, y1 = q["ret"]
    ss = q["ss"]
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    W, H = (X1 - X0) * ss, (Y1 - Y0) * ss
    M = np.zeros((H, W), np.float32)
    cv2.rectangle(M, (int((x0 - X0) * ss), int((y0 - Y0) * ss)), (int((x1 - X0) * ss) - 1, int((y1 - Y0) * ss) - 1), 1, -1)
    a = cv2.resize(M, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
    xx = np.arange(X0, X1) + 0.5
    luz = np.where(((xx - x0) % q["ripa_px"]) < 0.8, q["ripa"], 1.0)[None, :, None]
    cor = np.float32(q["madeira"])[None, None] * luz * np.ones((Y1 - Y0, 1, 1), np.float32)
    borda = np.zeros((Y1 - Y0, X1 - X0), bool)
    borda[[0, -1], :] = True
    borda[:, [0, -1]] = True
    cor[borda] = np.float32(q["fio"])
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + cor * a), 0, 255).astype(np.uint8)
    print("    circulação: o vão do vidro entre a escada e o elevador vira um painel de madeira ripada")
    return out


def bege(Q, out, fora=BEGE_FORA):
    import pedidos_subsolo_casac_1311 as PS
    guarda = Q.chapada
    ch = guarda.copy()
    for x0, y0, x1, y1 in fora:
        reg = ch[y0:y1, x0:x1]
        reg[np.all(reg == 232, axis=2)] = (0, 0, 1)
    Q.chapada = ch
    try:
        return PS.bege(Q, out)
    finally:
        Q.chapada = guarda


def gramado(out, q=OLIVEIRAS):
    import paisagismo_terreo_casac_1311 as PC
    guarda = PC.OLIVEIRAS
    PC.OLIVEIRAS = q
    try:
        return PC.aplicar(out)
    finally:
        PC.OLIVEIRAS = guarda


def _tecido(out, fonte, h, w, semente):
    import terreo_casaa_1011 as TC
    x0, y0, x1, y1 = fonte
    return TC.tecido(TC.variantes(out[y0:y1, x0:x1].astype(np.float32)), h, w, 16, 5, semente)


def _pinta_textura(out, m, T_, face=None):
    """A máscara `m` (bool, imagem inteira) com a textura `T_` (do tamanho da caixa de `m`), a borda um tom abaixo."""
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    big = np.zeros(out.shape, np.float32)
    big[y0:y1, x0:x1] = T_[:y1 - y0, :x1 - x0]
    o = out.astype(np.float32)
    o[m] = big[m]
    if face:
        b = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        o[b] = big[b] * face
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def _bib(out, par, png, cx, cy, wt, ht, giro, sombra="baixa"):
    return RT.pousar_bib(out, RT.item_bib("BT", png, cx, cy, wt, ht, giro, sombra, None), par)


def gourmet(Q, out, par, q=GOURMET):
    # a bancada da pia sem os armários: o granito tecido, a face um tom abaixo; a cuba Franke por cima
    _, m = RT.mascara_pdf(Q, [q["pia"]])
    m &= ~par
    ys, xs = np.nonzero(m)
    T_ = _tecido(out, q["granito_px"], ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min(), q["semente"])
    out = _pinta_textura(out, m, T_, q["face"])
    (x0, y0, x1, y1), wt = q["churrasqueira"]
    P = MB.ler("area-gourmet/grelha-churrasqueira")
    out = MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, wt, wt * P.shape[0] / P.shape[1], 0.0, "baixa", par)
    cx, cy, wt, ht = q["cuba"]
    out = _bib(out, par, "area-gourmet/cuba-franke-misturador-unic", cx, cy, wt, ht, 0.0)
    # o cooktop de 4 bocas
    out = RT.balcao(out, par, [(q["cooktop_velho"], "x", 2, 4.0)])
    cx, cy, wt, ht = q["cooktop"]
    out = _bib(out, par, "cozinha/cooktop-quatro-bocas", cx, cy, wt, ht, 0.0)
    # as banquetas B: as de antes saem (o deck logo abaixo), as novas 40% sob o tampo, o tampo por cima
    # (16/11, usuário: "remova esse tracejado, tanto em cima das banquetas, quanto embaixo delas") o deck de uma amostra
    # limpa logo abaixo, no lugar do piso copiado de 25 px abaixo (que trazia o tracejado e um tom mais escuro)
    import pedidos_terreo_casad_1611b as PD2
    out = PD2.piso_amostra(out, q["banquetas_velhas"], par, q["deck_px"])
    fonte = out.copy()
    P = MB.ler("area-gourmet/banqueta-b")
    d_ = q["banqueta_d"]
    ht = d_ * P.shape[0] / P.shape[1]
    ix0, iy0, ix1, iy1 = q["ilha"]
    cy = iy1 + 0.1 * ht
    for cx in q["banquetas"]:
        out = MB.pousar(out, P, cx, cy, d_, ht, 180.0, "movel", par)
    # (16/11, usuário: "a parte das banquetas que sobrepõe a bancada deve sair. a ideia é que as banquetas estejam abaixo
    # da bancada") o tampo da ilha inteiro volta por cima (antes, só os 3 px da beira)
    Y0, Y1 = int(np.floor(iy0)), int(np.ceil(iy1))
    X0, X1 = int(ix0), int(np.ceil(ix1))
    t = np.clip(iy1 - (np.arange(Y0, Y1) + 0.0), 0, 1)[:, None, None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(fonte[Y0:Y1, X0:X1] * t + out[Y0:Y1, X0:X1] * (1 - t)), 0, 255).astype(np.uint8)
    # (16/11, usuário: "não é assim os paines pivotantes. representar igual ao da casa A, em forma de brises") os dois
    # painéis pivotantes como os brises da Casa A (`pedidos_terreo_casad_1611b.brises`)
    import pedidos_terreo_casad_1611b as PD2
    out = PD2.brises(out, par)
    print("    gourmet: a bancada da pia sem os armários, a churrasqueira no módulo da esquerda, a cuba Franke, o cooktop "
          "de 4 bocas, 4 banquetas B 40% sob o tampo e os 2 painéis pivotantes no lado do deck, em brises")
    return out


def cozinha(Q, out, par, q=COZINHA):
    import terreo_casaa_1011 as TC
    H, W = par.shape
    for k, i in enumerate((q["ilha"], q["pia"], q["tanques"])):
        _, m = RT.mascara_pdf(Q, [i])
        if i != q["ilha"]:                          # na ilha, a faixa do meio (ARQ_PAREDE no PDF) também é tampo
            m &= ~par
        ys, xs = np.nonzero(m)
        T_ = TC.danae(ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min(), q["semente"] + k)
        out = _pinta_textura(out, m, T_, TC.DANAE["borda"])
    for nome, cx, cy, wt, ht in q["cubas"]:
        out = _bib(out, par, "area-de-servico/cuba-franke-inox-link", cx, cy, wt, ht, 0.0)
    cx, cy, wt, ht = q["cooktop"]
    out = _bib(out, par, "cozinha/cooktop-quatro-bocas", cx, cy, wt, ht, 0.0)
    P = MB.ler("cozinha/geladeira-inox")
    for x0, y0, x1, y1 in q["geladeiras"]:
        out = BB.piso_desloc(out, (x0, y0, x1, y1), par, 0, -1)
    for x0, y0, x1, y1 in q["geladeiras"]:
        ht = y1 - y0 - 1
        wt = min(x1 - x0 - 2, ht * P.shape[1] / P.shape[0])
        out = MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, wt, ht, 180.0, "movel", par)
    print("    cozinha e serviço: a ilha, a bancada da pia e a dos tanques em Dekton Danae; as cubas e os tanques Franke; "
          "o cooktop de 4 bocas; as 2 geladeiras inox G2")
    return out


def wc_dce(out, par, q=WC_DCE, g=GOURMET):
    x0, y0, x1, y1 = q["bancada"]
    m = np.zeros(par.shape, bool)
    m[int(round(y0)):int(round(y1)), int(round(x0)):int(round(x1))] = True
    c0, d0, c1, d1 = q["cuba"]
    m[int(d0) - 1:int(np.ceil(d1)) + 1, int(c0) - 1:int(np.ceil(c1)) + 1] = False
    m &= ~par
    ys, xs = np.nonzero(m)
    T_ = _tecido(out, g["granito_px"], ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min(), q["semente"])
    out = _pinta_textura(out, m, T_, 0.86)
    # o piso: o bege que sobra na caixa, fora a bancada, as peças e as paredes
    X0, Y0, X1, Y1 = q["caixa"]
    reg = out[Y0:Y1, X0:X1].astype(np.int16)
    livre = ~par[Y0:Y1, X0:X1] & ~m[Y0:Y1, X0:X1]
    med = np.median(reg[livre], axis=0)
    obj = np.abs(reg - med).max(axis=2) > q["obj"]
    obj = cv2.dilate(obj.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    piso = livre & ~obj
    T_ = _tecido(out, q["quartzito_px"], Y1 - Y0, X1 - X0, q["semente"] + 1)
    o = out[Y0:Y1, X0:X1].astype(np.float32)
    o[piso] = T_[piso]
    out[Y0:Y1, X0:X1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    WC DCE: a bancada no granito marrom tabaco; o piso no quartzito Aura dos outros banhos ({int(piso.sum())} px)")
    return out


def gas(out, par, q=GAS, g=GOURMET):
    X0, Y0, X1, Y1 = q["caixa"]
    livre = (~par[Y0:Y1, X0:X1]).astype(np.uint8)
    n, lab = cv2.connectedComponents(livre, connectivity=4)
    sx, sy = q["semente"]
    m0 = lab == lab[sy - Y0, sx - X0]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    L = reg.mean(axis=2)
    fundo = float(np.median(L[m0]))
    # (16/11, usuário: "corrija o piso dentro desse espaço") o piso até a face das paredes da imagem (as do render estão
    # 3 a 4 px para a direita e para baixo das do PDF: o filete claro embaixo e à direita era piso de antes)
    ym, xm = q["miolo_img"]
    ext = np.zeros_like(m0)
    ext[ym[0] - Y0:ym[1] - Y0, xm[0] - X0:xm[1] - X0] = True
    ext &= np.abs(reg - 80).max(axis=2) > 3
    m0 = m0 | ext
    # o rótulo: a tinta de antes (escuro sobre o claro) vira o branco dos rótulos sobre o granito; escuro em relação à
    # luz do entorno (a mediana de 15 px) e longe da beira (a sombra escura da direita e de baixo do render virava um
    # véu branco com a mediana da caixa inteira)
    Lbg = cv2.medianBlur(np.clip(L, 0, 255).astype(np.uint8), 15).astype(np.float32)
    nucleo = cv2.erode(m0.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    a = np.clip((Lbg - L - 12) / max(fundo - 40.0, 1.0), 0, 1)[..., None] * nucleo[..., None]
    T_ = _tecido(out, g["granito_px"], Y1 - Y0, X1 - X0, 1514)
    novo = T_ * (1 - a) + np.float32((236, 236, 236)) * a
    reg[m0] = novo[m0]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    gás: o piso no granito marrom tabaco, o rótulo em branco ({int(m0.sum())} px)")
    return out


def marrom(Q, out):
    import pedidos_terreo_casab_1211 as PB
    return PB.marrom_tb(Q, out)                     # (o tecido da amostra vai para $CACHE_TB, se dado)


def area_descoberta(out, q=AREA_DESCOBERTA):
    import pedidos_terreo_casac_1311 as PT
    import pedidos_subsolo_casac_1311 as PS
    t = dict(q["traco"])
    ss = q["ss"]
    X0, Y0, X1, Y1 = 2186, 559, 2354, 684
    M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    for p0, p1 in q["x"]:
        PT._tracejado(M, p0, p1, X0, Y0, t, ss)
    out = PS._pintar(out, cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA),
                     X0, Y0, q["cor"])
    (ax, ay), (bx, by) = q["linha"]
    X0, Y0, X1, Y1 = int(min(ax, bx)) - 3, int(min(ay, by)) - 3, int(max(ax, bx)) + 4, int(max(ay, by)) + 4
    M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    cv2.line(M, (int((ax - X0) * ss), int((ay - Y0) * ss)), (int((bx - X0) * ss), int((by - Y0) * ss)), 255,
             max(1, int(round(q["larg"] * ss))), cv2.LINE_AA)
    a = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + np.float32(q["cor"]) * a), 0, 255).astype(np.uint8)
    print("    área descoberta: a linha contínua no lado da direita do tracejado")
    return out


def pergolados(out, par, q=PERGOLADOS):
    import pedidos_terreo_casac_1311 as PT
    import pedidos_subsolo_casac_1311 as PS
    # a faixa do pergolado de cima: o granito tecido de ponta a ponta (os traços fracos do tracejado antigo saíam só em
    # parte pela cor), fora as paredes; o rótulo de volta por cima, pelo alfa do branco sobre o granito
    x0, y0, x1, y1 = q["limpa"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    T_ = _tecido(out, q["granito_px"], y1 - y0, x1 - x0, 1515)
    livre = np.ones((y1 - y0, x1 - x0), bool)        # o tracejado do telhado está na ARQ_PAREDE: a faixa não tem parede
    hh, ww = livre.shape
    dist = np.minimum.outer(np.minimum(np.arange(hh) + 0.5, hh - np.arange(hh) - 0.5),
                            np.minimum(np.arange(ww) + 0.5, ww - np.arange(ww) - 0.5))
    a_ = np.clip(dist / 10.0, 0, 1)[..., None]
    # o tom e a luz larga do granito do lugar (a amostra entre os carros é um pouco mais clara e lisa)
    T_ += cv2.GaussianBlur(cv2.medianBlur(np.clip(reg, 0, 255).astype(np.uint8), 9).astype(np.float32), (0, 0), 12) - \
        cv2.GaussianBlur(T_, (0, 0), 12)
    novo = reg * (1 - a_) + T_ * a_
    out[y0:y1, x0:x1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    m = livre
    # à esquerda, junto ao abrigo do gás: os traços claros do tracejado do telhado (fora o miolo do gás, com o rótulo)
    gx0, gy0, gx1, gy1 = q["esquerda"]
    I = out[gy0:gy1, gx0:gx1].astype(np.int16)
    tr = (I.mean(axis=2) > q["lum"]) & ((I.max(axis=2) - I.min(axis=2)) < q["croma"])
    a0, b0, a1, b1 = q["gas"]
    tr[b0 - gy0:b1 - gy0, a0 - gx0:a1 - gx0] = False
    for s0, t0, s1, t1 in q.get("soleiras", ()):                  # as soleiras das portas ficam
        tr[max(t0 - gy0, 0):max(t1 - gy0, 0), max(s0 - gx0, 0):max(s1 - gx0, 0)] = False
    tr = cv2.dilate(tr.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    tr &= ~(np.abs(I - 80).max(axis=2) <= 6)                       # a parede cinza fica
    T2 = _tecido(out, q["granito_px"], gy1 - gy0, gx1 - gx0, 1516)
    T2 += np.median(out[gy0:gy1, gx0:gx1][~tr].reshape(-1, 3).astype(np.float32), axis=0) - \
        np.median(T2.reshape(-1, 3), axis=0)
    o = out[gy0:gy1, gx0:gx1].astype(np.float32)
    o[tr] = T2[tr]
    out[gy0:gy1, gx0:gx1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    # os tracejados escuros do telhado no hall (no PDF, na ARQ_PAREDE: a máscara das paredes não serve aqui)
    hx0, hy0, hx1, hy1 = q["hall"]
    reg_h = out[hy0:hy1, hx0:hx1].astype(np.int16)
    esc = (reg_h.mean(axis=2) < q["hall_lum"]) & ~(np.abs(reg_h - 80).max(axis=2) <= 6)   # a parede cinza fica
    esc = cv2.dilate(esc.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    fonte = out.copy()
    for y, x in zip(*np.nonzero(esc)):
        out[hy0 + y, hx0 + x] = fonte[hy0 + y - q["hall_dy"], hx0 + x]
    # os módulos, tracejados em cinza
    t = q["traco"]
    ss = t["ss"]
    X0, X1 = int(q["x0"]) - 4, int(q["x0"] + (q["n"] - 1) * q["passo"] + q["larg"]) + 5
    for ya, yb in q["ys"]:
        Y0, Y1 = int(ya) - 4, int(yb) + 5
        M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
        for k in range(q["n"]):
            a0 = q["x0"] + k * q["passo"]
            a1 = a0 + q["larg"]
            for p0, p1 in (((a0, ya), (a1, ya)), ((a1, ya), (a1, yb)), ((a1, yb), (a0, yb)), ((a0, yb), (a0, ya))):
                PT._tracejado(M, p0, p1, X0, Y0, t, ss)
        al = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        r0, s0, r1, s1 = q["rotulo"]                  # o rótulo da garagem (reescrito no fim) sem tracejado por baixo
        al[max(0, s0 - Y0):max(0, s1 - Y0), max(0, r0 - X0):max(0, r1 - X0)] = 0
        out = PS._pintar(out, al, X0, Y0, t["cor"])
    print(f"    garagem: os tracejados do telhado e os X dos pergolados saem ({int(m.sum())} px); os 2 pergolados com os "
          f"{q['n']} módulos do PDF, tracejados em cinza")
    return out


def cama_dce(out, par, q=DCE):
    x0, y0, x1, y1 = q["caixa"]
    enf = f"{q['tom']} (Casa D)"
    r, g, b = QUARTOS[q["tom"]]["manta"]
    CM.TONS[enf] = (b, g, r)
    with contextlib.redirect_stdout(io.StringIO()):
        P = CM.cama("solteiro", q["roupa"], enf, "peseira")
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = MB.pousar(out, P, cx, cy, x1 - x0, y1 - y0, q["giro"], "movel", par)
    out = _resto_fora(out, (x0, y0, x1, y1), RT._alfa_peca(P, cx, cy, x1 - x0, y1 - y0, q["giro"], par.shape), par)
    print(f"    DCE do Térreo: a cama de solteiro A com a peseira em {q['tom']}")
    return out


def lavabo(out, antes, q=LAVABO, qj=JANELA_LAVABO):
    import revisao_terreo_casac_1511 as R15
    with contextlib.redirect_stdout(io.StringIO()):
        out = R15.lavabo_bancada(out, dict(R15.LAVABO, pecas=q["pecas"], cuba=q["cuba"]))
    x0, y0, x1, y1 = qj["vao"]
    a0, b0, a1, b1 = qj["fonte"]
    F_ = antes[b0:b1, a0:a1]
    out[y0:y1, x0:x1] = cv2.resize(F_, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    print("    lavabo: a bancada e a cuba em granito marrom tabaco; a janela do jardim desenhada no vão do PDF")
    return out


def jardins(Q, out, q=JARDINS):
    import pedidos_terreo_casac_1311 as PT
    canto = out[0:8, 0:8].copy()                    # a floreira de `PT.jardins` (só na Casa C): 1 px no canto, de volta
    with contextlib.redirect_stdout(io.StringIO()) as log:
        out = PT.jardins(Q, out, q)
    print("\n".join(l for l in log.getvalue().splitlines() if "floreira" not in l))
    out[0:8, 0:8] = canto
    return out


def banco_varanda(out, par, q=BANCO_VARANDA):
    x0, y0, x1, y1 = q["caixa"]
    P = MB.ler(q["png"])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    g = MB.frente((1, 0))
    out = MB.pousar(out, P, cx, cy, y1 - y0, x1 - x0, g, "movel", par)
    out = _resto_fora(out, (x0, y0, x1, y1), RT._alfa_peca(P, cx, cy, y1 - y0, x1 - x0, g, par.shape), par)
    print(f"    varanda: o banco estofado dos brises no lugar do banco de madeira (giro {g:.0f}°)")
    return out


def escadas(out, q=ESCADAS):
    import pedidos_terreo_casac_1311 as PT
    return PT.escadas(out, q)


def perimetro(Q, out, q=PERIMETRO, fora=BEGE_FORA):
    B = np.all(Q.chapada == 232, axis=2)
    for x0, y0, x1, y1 in fora:
        B[y0:y1, x0:x1] = False
    I = out.astype(np.int16)
    grama = (I[..., 1] - I[..., 0] > 12) & (I[..., 2] - I[..., 1] < 15) & (I.mean(axis=2) < 150)
    # só o gramado (as manchas grandes): o antisserrilhado dos rótulos e as juntas dos degraus também caíam na cor
    n_, lab_, st_, _ = cv2.connectedComponentsWithStats(grama.astype(np.uint8), connectivity=8)
    grama = np.isin(lab_, [i for i in range(1, n_) if st_[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    k = np.ones((3, 3), np.uint8)
    borda_b = B & (cv2.dilate(grama.astype(np.uint8), k) > 0) & ~grama
    borda_g = grama & (cv2.dilate(borda_b.astype(np.uint8), k) > 0)
    o = out.astype(np.float32)
    o[borda_b] *= q["bege"]
    o[borda_g] *= q["grama"]
    print(f"    deck: o fio do perímetro junto ao gramado ({int(borda_b.sum())} px)")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def contornos(out, q=CONTORNOS):
    fonte = out.copy()
    H, W = out.shape[:2]
    n = 0
    for x0, y0, x1, y1 in q["rets"]:
        e = int(np.ceil(q["faixa"])) + q["passo"] + 2
        X0, Y0, X1, Y1 = int(x0) - e, int(y0) - e, int(np.ceil(x1)) + e, int(np.ceil(y1)) + e
        yy, xx = np.mgrid[Y0:Y1, X0:X1] + 0.5
        dl, dr, dt, db = xx - x0, x1 - xx, yy - y0, y1 - yy
        dentro = (dl > 0) & (dr > 0) & (dt > 0) & (db > 0)
        dist = np.where(dentro, np.minimum(np.minimum(dl, dr), np.minimum(dt, db)),
                        np.maximum(np.maximum(-dl, -dr), np.maximum(-dt, -db)))
        faixa = np.abs(dist) <= q["faixa"]
        reg = fonte[Y0:Y1, X0:X1].astype(np.int16)
        lum = reg.mean(axis=2)
        croma = reg.max(axis=2) - reg.min(axis=2)
        viz = cv2.blur(lum.astype(np.float32), (9, 9))
        fio = faixa & (lum < viz - q["escuro"]) & (croma < q["croma"])
        # o lado mais perto (para onde o px anda): dentro, para o miolo; fora, para longe
        lado = np.argmin(np.stack([np.abs(dl), np.abs(dr), np.abs(dt), np.abs(db)]), axis=0)
        sx = np.choose(lado, [1, -1, 0, 0])
        sy = np.choose(lado, [0, 0, 1, -1])
        sinal = np.where(dentro, 1, -1)
        p = q["passo"]
        for v, u in zip(*np.nonzero(fio)):
            ty, tx = Y0 + v + sinal[v, u] * sy[v, u] * p, X0 + u + sinal[v, u] * sx[v, u] * p
            if 0 <= ty < H and 0 <= tx < W:
                out[Y0 + v, X0 + u] = fonte[ty, tx]
                n += 1
    print(f"    contornos: o fio escuro em volta de {len(q['rets'])} tapetes e mesas sai ({n} px)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    # (16/11, usuário: "Alternativa 1") as peças da biblioteca da Casa D (`alternativa1_terreo_casad_1611`) no lugar
    # das das Casas A a C
    import alternativa1_terreo_casad_1611 as A1
    Q = quadro()
    out = antes.copy()
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    MB.CRIADOS, MB.POLTRONAS = CRIADOS, POLTRONAS
    out = bege(Q, out)
    out = claraboias(Q, out)
    out = chuveiros(out, par)
    out = A1.bancada_dupla(out, par)
    out = A1.pecas(out, par)
    import pedidos_terreo_casad_1611b as PD2
    out = PD2.tapete_master(Q, out, par)
    out = A1.camas(out, par)
    out = PD2.contorno_cama(out, par)
    out = A1.bancos(Q, out, par)
    out = A1.criados(Q, out, par)
    out = A1.poltronas(Q, out, par)
    out = A1.cadeiras(Q, out, par)
    out = armarios(Q, out, par)
    out = A1.sala_intima(Q, out, antes, par)
    import pedidos_terreo_casad_1611 as PD
    out = PD.bancada_intima(out, par)
    out = A1.escritorio(out, par)
    out = A1.cadeiras_s3(Q, out, par)
    # (16/11, usuário: "Para as escrivaninhas dos quartos, use o tom de madeira nogueira")
    out = A1.escrivaninhas(out, par)
    # (16/11, usuário: a mesa, o piso entre o vidro e o painel e o painel de madeira da suíte 3) no lugar de `painel_s3`
    out = PD2.suite3(Q, out, par)
    out = portas(Q, out)
    out = sem_soleira(Q, out, par)
    out = A1.jantar(Q, out, par)
    out = A1.estar(Q, out, par)
    out = A1.varanda(Q, out, par)
    out = vasos_hall(out, par)
    out = seta_hall(out, par)
    out = painel_escada(out)
    out = A1.gourmet(Q, out, par)
    out = cozinha(Q, out, par)
    out = wc_dce(out, par)
    out = marrom(Q, out)
    out = PD2.geladeiras(Q, out, par)
    out = PD2.geladeira_gourmet(out, par)
    out = gas(out, par)
    out = area_descoberta(out)
    out = A1.cama_dce(out, par)
    # (16/11, usuário, no DCE: "corrigir o contorno da cama, sem falhas!")
    out = PD2.contorno_cama(out, par, dict(PD2.CONTORNO_CAMA, camas=("DCE",)))
    out = lavabo(out, antes)
    out = banco_varanda(out, par)
    out = contornos(out)
    out = gramado(out)
    out = perimetro(Q, out)
    out = escadas(out)
    out = jardins(Q, out)
    out = pergolados(out, par)
    out = rotulos_closets(out)
    out = spa_m2(out)
    out = rotulos_novos(Q, out, par)
    # (16/11, usuário: o padrão das cortinas das Casas A, B e C, bem visíveis; os rótulos centralizados, alinhados e
    # padronizados) as cortinas C4 em todos os trechos (a da suíte 3 inclusive) e os rótulos no padrão das casas
    import cortinas_padrao_casad_1611 as CP
    import rotulos_padrao_casad_1611 as RP
    out = PD2.pedras(Q, out, par)
    out = PD2.floreiras(out, par)
    out = PD2.aparador(Q, out)
    out = PD.borda_piscina(out)
    out = PD.arandelas(Q, out, par)
    out = CP.aplicar(Q, out, par)
    # (16/11, usuário: "Esse último WC-DCE do térreo tá bem desconfigurado") o banho refeito entre o apagar e o escrever
    out = RP.aplicar(out, lambda o: A1.wc_dce(o, par))
    # (16/11, usuário: "Confira o contorno das portas [...] a parede atrás da porta [...] nenhuma mancha de arco [...]
    # onde tiver soleira tem que colocar") as faces das paredes atrás das folhas, as manchas junto às portas e as
    # soleiras das portas de correr (`portas_revisao_casad_1611`)
    import portas_revisao_casad_1611 as PR
    out = PR.aplicar(out)
    out = PD2.paredes_banhos(out)
    out = PD2.porta_hall(out)
    out = PD2.vidros(out)
    out = PD2.tracejado_ilha(out)
    out = PD2.margem(out)
    return out


def antes_depois(antes, depois, pasta=R):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(5.0, 1500 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        lado = a.shape[1] <= a.shape[0] * 1.6
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b]) if lado else \
            np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS" if lado else "ANTES (em cima) | DEPOIS (embaixo)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        cv2.imwrite(str(Path(pasta) / f"POE642_CasaD_PH_Terreo_1511_{nome}_antes_depois.jpg"), np.vstack([topo, junto]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def final_de(commit):
    dado = subprocess.run(["git", "show", f"{commit}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"], cwd=RAIZ_GIT,
                          capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes) if a.antes else final_de(ANTES_COMMIT)
    depois = aplicar(antes)
    if a.saida:
        cv2.imwrite(a.saida, depois)
        print(f"    {a.saida}")
        antes_depois(antes, depois, Path(a.saida).parent)
        return
    cv2.imwrite(str(FINAL), depois)
    antes_depois(antes, depois)


if __name__ == "__main__":
    main()

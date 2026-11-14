"""A revisão do 12K do Térreo da Casa C (13/11, "ESTOU REVISANDO O TÉRREO DA CASA C").

Sobre a final de `ANTES_COMMIT` (a do 12K de 13/11: o estar E1 e o paisagismo das oliveiras):
- **"FALTOU O BOX DO CHUVEIRO"** (`box_ducha`): o chuveiro entre os lavabos (a área do ralo, aberta para o lavabo
  feminino) tem no PDF o vidro do box (ARQ_LOUÇAS E METAIS, a linha dupla tracejada de 1227,1 a 1229,9 pt, da parede do
  corredor até o peitoril de baixo); entra contínuo, de parede a parede, com as faces finas e a sombra curta
  (`final3840_casab.boxes_vidro`, como os outros boxes da Casa C).
- **"CORRIJA O CONTORNO DAS CUBAS. TEM MANCHAS BRANCAS"** (`bancadas_cubas`): as faixas da bancada acima e abaixo das
  cubas esculpidas dos lavabos masculino e feminino estavam num granito pontilhado de branco, com fios brancos onde
  encostam na cuba e na parede; viram o travertino bruto no tom da cuba (como o lavatório da Casa B, "IGUAL DA CUBA
  ESCULPIDA"), com o fio da borda nos lados livres (não no da parede).
- **"VAMOS VARIAR OS TONS DOS BANCOS EM FRENTE AS CAMAS. MANTEM O DA SUITE MASTER COMO ESTÁ"** (`bancos`): o B1 dos
  quartos (veludo capitonê, moldura de freijó) em três veludos (`TONS`); só o veludo muda de cor (a luz, o capitonê e os
  botões ficam); a moldura, a sombra e a suíte master ficam. A troca é exata: a final menos o banco de antes mais o novo,
  pelos mesmos `banco_b1` e `pousar` do `mobiliario_terreo_casac_1311`.
- **"FICOU FALTANDO A DELIMITAÇÃO DAS CLARABOIAS CONFORME ORIENTAÇÃO"** (`claraboias`; a orientação do cliente:
  "Representar as claraboias apenas com as linhas de fora, sem o X no meio ... Usar um tom cinza e as linhas mais
  fininhas"): o tracejado cinza fino das 5 claraboias (`pedidos_terreo_casac_1311.CLARABOIAS` e `TRACO`) tinha sumido
  sob os materiais da Casa B (o piso refeito por cima); volta igual, depois de limpar os restos do tracejado preto
  antigo junto às paredes (no BH master 1).
- **"MELHORAR A REPRESENTAÇÃO DO APARADOR E DAS PLANTAS"** (o post-it: "Representação da planta está errada";
  `aparador_planta`): o aparador do hall (junto à parede do lavabo, PDF 88368) era uma caixa de madeira com os arcos do
  PDF por cima e a planta (o sol do PDF, 85121) um disco bege serrilhado; entram o aparador de freijó gerado no
  Higgsfield (`gpt_image_2`, 2K, vista de cima, com o vaso de galhos secos, os livros de linho e a tigela de travertino;
  `biblioteca-objetos/02-terreo/hall/aparador-freijo-objetos.png`), na proporção do PDF tirando madeira lisa entre os
  objetos (sem esticar), e o vaso de folhagem da biblioteca (`sala-intima/vaso-folhagem-a`) no círculo da planta; o
  travertino do hall refeito por baixo.
- **"MANTENHA O MESMO MATERIAL PARA PORTA DE FORA A FORA"** (`porta_hall`): a folha da porta pivotante do hall (aberta,
  y 1294 a 1298) tinha o miolo escuro até a parede e claro dali até a ponta; agora a folha inteira como a parte de dentro.
- **"REMOVA A SETA QUE ESTÁ NA IMAGEM E SUBSTITUA PELA A INDICADA"** (o post-it: "Centralizar a seta com a abertura da
  porta, usando este modelo de seta"; `seta_entrada`): a seta de 1,5 m do hall sai (o travertino refeito) e entra o
  triângulo cheio das escadas (18 x 21 px, como o da Casa B), com a ponta para dentro da casa, no centro do vão
  (y 1245,8 a 1424,9 px), a 16 px da soleira, do lado de fora.
- **"REPRESENTAR UM FILETE ENTRE OS DOIS PISOS."** (`filete_garagem`, entre a pedra portuguesa do acesso e o piso
  marrom da garagem): como o filete do Subsolo da Casa C, uma tira de Bege Bahia de 5 cm (a amostra da calçada da
  entrada) no encontro (y 344), de parede a parede, com o fio fino das duas arestas e a sombrinha curta no piso da
  garagem; e os pontinhos claros soltos no piso marrom da garagem (em volta dos carros) saem.
- **"ADICIONAR DUAS MÁQUINAS DE LAVAR ROUPAS NESSE VÃO."** (o post-it: "Colocar duas máquinas de lavar roupa";
  `maquinas`): no vão da área de serviço entre a parede de cima e a bancada dos tanques, encostadas na parede da
  direita, as duas máquinas de 0,60 m da Casa B (`pedidos_terreo_casab_1211._maquina`: o tampo branco arredondado, o
  painel junto à parede, o botão e a sombra curta).
- **"TROCAR O MATERIAL DA BANCADA PARA GRANITO MARROM TABACO"** (o post-it: "Cor da bancada é marrom tabaco";
  `bancada_servico`): a bancada dos tanques da área de serviço (era o travertino claro) no marrom tabaco da Casa B (a
  pedra da ilha gourmet da Casa B, tecida: `pedidos_terreo_casab_1211._tabaco`), com o contorno fino um tom abaixo nos
  lados livres; as cubas de inox e as torneiras ficam.
- **"CRIE O AMBIENTE"** (o post-it no quarto de serviço: "Colocar uma cama e um guarda-roupa aqui. E o nome do ambiente
  mais pra cima."; `quarto_servico`): a cama de solteiro do quarto externo (`camas_casac_1311.cama`, 2,0 x 1,0 m, roupa
  branca, peseira cinza-clara) deitada junto à parede de baixo, a cabeceira na parede da esquerda; o guarda-roupa de
  0,57 m na parede da esquerda, da parede de cima até 11 cm da cama, no desenho dos guarda-roupas da Casa C (o creme
  mais escuro do lado aberto, o varão no meio, os cabides, o fio de madeira e a sombra curta); o rótulo (a mesma letra,
  levada pelo alfa contra o piso) no meio da área livre, entre o guarda-roupa e a parede, abaixo da porta.
- **"CORRIJA O ERRO DA CUBA"** (o BH serviço; `bh_servico`): a bancada do PDF saía no piso, só com um contorno cinza
  solto, e a cuba com uma tira branca subindo pelo canto; como no BH serviço da Casa B
  (`pedidos_terreo_casab_1211.cozinha_tb`, item 4): a bancada em marrom tabaco com o contorno e a sombra curta, a cuba
  de semiencaixe em louça branca da Casa A (`final3840_casaa.cuba_branca`) no retângulo do PDF (o piso de logo ao lado
  por baixo da parte que passa da bancada e da cuba antiga) e a torneira cromada saindo da parede.
- **"CORRIJA ESSAS PORTAS PARA FICAREM BEM REPRESENTADAS"** (a área de serviço descoberta; `portas_descoberta`): as duas
  portas de giro das paredes da esquerda e da direita tinham ficado com a folha do render (uma barra escura de
  esquadria, solta), porque no PDF a folha é desenhada em 4 pedaços e a busca das portas (`pedidos_terreo_casac_1311.
  portas_pdf`) não a achava; agora como as outras portas de giro da Casa C (`pedidos_subsolo_casab_1211.portas_sb`): a
  folha de madeira clara no retângulo do PDF, quina com quina na ponta da parede, sem os marcos, a soleira no vão.
- **"CORRIJA A COZINHA. BANCADAS EM DEKTON DANAE. ESTÁ FALTANDO ARMÁRIOS. REPRESENTAR OS ARMÁRIOS NA COR DEFINIDA,
  INCLUSIVE O ARMÁRIO DO LOUCEIRO"**, "BANCADA EM L DA COZINHA DEKTON DANAE", "COR DA ILHA DA COZINHA EM DEKTON
  DANAE", "ESTÁ FALTANDO ESSE ARMÁRIO NA COZINHA" (os post-its: "Cor da bancada é no Dekton Danae", "Representar
  armário e prateleiras na mesma cor", "Seguir essa cor"; `cozinha`): a bancada em L da pia (PDF 38671 e o trecho das
  cubas, 38920), a ilha
  (53847) e a bancada da direita, abaixo do armário (38868), no Dekton Danae (`terreo_casaa_1011.danae`, a face um tom
  abaixo); as cubas, as torneiras e o cooktop ficam por cima. Os dois armários altos do PDF (o da parede da esquerda,
  88831, e o da direita, 88836, os retângulos com a diagonal), que tinham sumido sob o granito do piso no mobiliário
  (c4cd7ce), e as prateleiras em U do louceiro 1 (88919) na cor dos armários de antes (a madeira clara, RGB 189, 160,
  129, "seguir essa cor"), lisa, sem textura, com a face um tom abaixo; a sombra curta das peças no piso.
- **"O PISO ACIMA DA CORTINA ... É VINÍLICO"** (`faixa_vinilico`): nas portas de correr da Varanda 1 (quarto 1) e da
  Varanda (quartos 2 e 3), o vão entre os perfis, acima da cortina, saía num marrom escuro e acinzentado; agora é o
  vinílico do quarto (as réguas de logo abaixo da cortina, espelhadas para cima, coluna a coluna: o mesmo tom e as
  mesmas réguas); os perfis da porta (cinza e escuros) ficam.
- **"REVISE TODOS OS ARMÁRIOS E REMOVA DIVISÓRIAS. ELES FORMAM O L CONTÍNUO ... JÁ FIZEMOS ISSO NAS CASAS A E B"**
  (`closets`): os guarda-roupas em L e em U do PDF (os polígonos da DOC_LINHAS: o closet do quarto 1, o do vizinho, o
  do quarto 3 e os closets master 1, em U, e 2) como uma peça só, no desenho do 1º Pavimento da Casa A e do Térreo da
  Casa B (`um_pav_casaa_1111._closet`: o fundo bege que escurece junto às portas, os cabides de través até o canto, o
  cabideiro se encontrando no meio do canto, a moldura ocre só por fora, nada entre os trechos).
- **"NO QUARTO 1, TEMOS UM ARMÁRIO NA ENTRADA DO QUARTO COM FUNDO DO ARMÁRIO DO CLOSET ... PRECISA SER REPRESENTADO"**
  (`armario_entrada`): o armário raso do PDF (88482, 0,30 m) de costas para o closet, com as portas para a entrada: o
  miolo bege no tom dos guarda-roupas, a moldura ocre e a faixa das portas, sem cabides.
- **"CORRIJA NO QUARTO 1 E 2 OS TAPETES. CORRIJA NO QUARTO 1, O DEFEITO DA MESA LATERAL E O CONTORNO DA CAMA. REVISE
  TODAS AS CAMAS DE TODOS OS QUARTOS"** (`quartos`): no mobiliário (`mobiliario_terreo_casac_1311.poltronas` e
  `cadeiras_escritorio`) o piso refeito em volta da poltrona, do pufe e das cadeiras entrou no tapete (o degrau na borda
  de baixo dos tapetes do quarto 1 e do quarto 3) e ficou num tom mais claro que o vinílico novo; agora o tapete volta
  inteiro no retângulo do PDF (a lã dele, no tom dele) e o piso em volta das peças é o vinílico do quarto no tom do
  entorno, com a sombra curta das peças de novo. A mesa lateral de vidro do quarto 1 (um anel quebrado) vira a mesinha
  redonda de madeira da biblioteca, com a sombra curta. Em todas as camas, o contorno claro da cama de antes (as faixas
  claras e cinzas entre a cama nova e o tapete ou o piso) sai: o tapete ou o piso de logo ao lado, copiado para dentro, e
  a sombra curta da cama.
- **"REMOVA ESSE TRACEJADO EM VOLTA DA PLANTA"** (`tracejado_lote`): o retângulo tracejado do lote (x 296 a 3583, y 5 a
  2050, que encostava na borda do gramado à esquerda) sai: fora do lote, branco puro.

  python3 revisao_terreo_casac_1311.py [--antes <png>] [--saida <png>]
"""

import argparse
import contextlib
import io
import subprocess
import sys
import types
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import final3840_casac as C                      # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import mobiliario_terreo_casac_1311 as MB        # noqa: E402

PX_M = B1.PX_M
Q_PX_PT = 59.70590031258779 / 56.69                 # px do quadro por pt do PDF
R = AQUI.parents[1] / "POE642_CasaC" / "renders"
FINAL = R / "POE642_CasaC_PH_Terreo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "48a23e8"

# o vidro do box (pt): x0, y0, x1, y1, deitado
BOX_DUCHA = [(1227.08, 1722.84, 1229.91, 1785.03, False)]
# as faixas da bancada (pt) e o lado da parede; o bloco da cuba (pt, para o tom); o travertino (`final3840_casaa.
# travertino_bruto`, os parâmetros do lavatório da Casa B) e o fio da borda
BANCADAS = [{"nome": "lavabo masc.", "parede": "esq", "cuba": (1025.8, 1675.8, 1045.7, 1727.9),
             "faixas": [(1017.3, 1649.1, 1040.0, 1675.8), (1017.3, 1727.9, 1040.0, 1785.2)]},
            {"nome": "lavabo fem.", "parede": "dir", "cuba": (1315.0, 1675.8, 1334.8, 1727.9),
             "faixas": [(1320.6, 1649.1, 1343.3, 1675.8), (1320.6, 1727.9, 1343.3, 1785.2)]}]
TRAV = {"veio": 0.010, "faixa": 0.016, "poros": 6, "poro_esc": 0.05, "forca": 0.8, "semente": 1311, "fio": 0.82,
        "ss": 8, "tom_pct": 70}
# os bancos dos quartos (índice do retângulo do PDF, tamanho) e o veludo novo (BGR, a mediana vista de cima); o
# veludo do PNG: o matiz do bordô (OpenCV, >= 150 ou < 8) e saturado; `gama`: o contraste da luz do veludo
# (a 1ª tentativa, mais clara e com gama 0,75, saiu rosa-chiclete; estes são os da variante B, fechados, de veludo)
TONS = [("quarto 3", 88634, "casal", "rosé antigo", (76, 70, 112)),
        ("quarto 2, de cima", 88609, "solteiro", "azul petróleo", (72, 62, 28)),
        ("quarto 2, de baixo", 88614, "solteiro", "azul petróleo", (72, 62, 28)),
        ("quarto 1", 88517, "casal", "verde musgo", (42, 76, 70))]
VELUDO = {"matiz": (150, 8), "sat_min": 60, "gama": 0.5}
# as claraboias: a faixa em volta do retângulo (px) onde ficam os restos do tracejado antigo; o escuro (fração da
# mediana do piso) e o cinza da parede (tolerância)
CLARA = {"faixa_px": 2.5, "escuro": 0.6, "face": 0.85, "parede": (80, 16), "passo_px": 3, "busca_px": 8,
         "protege_px": 3}
# o aparador e a planta (px): o retângulo do aparador e o círculo da planta do PDF, a área refeita, a amostra do
# travertino do hall, o PNG do aparador (a madeira lisa entre os objetos sai em `lisos_min_px`) e o vaso
APARADOR = {"ret": (2313.9, 1199.8, 2433.3, 1223.7), "planta": (2436.9, 1198.5, 2472.8, 1234.3),
            "refaz": (2306, 1198, 2481, 1244), "fonte": (2306, 1248, 2480, 1288),
            "png": "02-terreo/hall/aparador-freijo-objetos.png", "lisos_min_px": 300, "costura_px": 24,
            "vaso": "03-primeiro-pavimento/sala-intima/vaso-folhagem-a.png", "vaso_px": 40.0}
# a folha da porta pivotante: as linhas (y) e o trecho (x) refeito com a mediana da parte de dentro (x da amostra)
PORTA = {"linhas": (1294, 1299), "refaz_x": (2699, 2752), "amostra_x": (2580, 2690)}
# a seta: a caixa da seta de antes (px) e o escuro dela; a amostra do travertino; o triângulo (o vão, a face de fora da
# soleira, o recuo, comprimento e largura)
SETA = {"caixa": (2590, 1362, 2696, 1410), "lum": 120, "fonte": (2560, 1412, 2690, 1442), "vao_y": (1245.8, 1424.9),
        "soleira_x": 2712.2, "recuo_px": 16.0, "comp": 18.0, "larg": 21.0}
# o filete (px): o encontro (y), as pontas (x, as faces das paredes), a largura (m), a amostra do Bege Bahia, o fio e a
# sombrinha; os pontinhos claros: a caixa do piso da garagem acima do quarto externo, o claro acima da mediana local, a
# área máxima e a folga em volta dos carros
FILETE_G = {"y": 344.0, "x": (2714.0, 3268.0), "larg_m": 0.05, "fonte": (2760, 1250, 2840, 1320),
            "fio": (150, 165, 178), "fio_alfa": 0.55, "fio_px": 0.6, "sombra": 0.10, "sombra_px": 1.6, "ss": 8,
            "pontos": (2716, 348, 3266, 670), "claro": 35, "area_max": 30, "carro_px": 4, "texto_min": 225}
# as máquinas de lavar (px): x0, y0, x1, y1 de cada (a parede da direita em x 2700; o vão de y 260 à bancada em 343)
MAQUINAS = [(2663.5, 262.0, 2698.5, 299.0), (2663.5, 303.0, 2698.5, 340.0)]
# a bancada dos tanques (px; a parede à direita em x 2700): o retângulo, as cubas (o inox, pouco croma, em peças
# grandes) e a sombra delas, a amostra do marrom tabaco na final da Casa B e o contorno
BANCADA_SERV = {"ret": (2655.4, 343.2, 2700.0, 495.6), "inox_croma": 16, "cuba_area": 100, "cuba_sombra": 0.35,
                "final_b": AQUI.parents[1] / "POE642_CasaB" / "renders" / "POE642_CasaB_PH_Terreo_final_rotulos.png",
                "fonte": (1418, 1325, 1546, 1381), "semente": 1313, "contorno": (30, 40, 54), "contorno_alfa": 0.5,
                "ss": 8}
# o quarto de serviço (px): o vão (x0, y0, x1, y1), a cama (o retângulo do PDF da do quarto externo, para o tamanho), o
# guarda-roupa (fundo e folga até a cama), o rótulo de antes (caixa) e o centro novo, a amostra do piso
QUARTO_S = {"vao": (2474.5, 501.0, 2615.5, 662.5), "cama_pdf": 84669, "cama": ("solteiro", "branco", "cinza-claro"),
            "giro": 90.0, "arm_fundo_m": 0.57, "arm_folga_m": 0.11, "arm_cor": ((189, 209, 225), (158, 175, 188)),
            "varao": (150, 156, 160), "cabide_px": 7.3, "cabide": 0.86, "fio": (75, 128, 170), "sombra": 0.18,
            "rotulo": (2500, 612, 2602, 646), "rotulo_centro": (2562.0, 574.0), "piso": (2480, 512, 2550, 560),
            "semente": 1314, "ss": 8}
# o BH serviço (px): a bancada e a cuba do PDF, a cuba antiga (a caixa, para o piso por baixo), a torneira (deitada,
# a base na parede) e de onde vem o piso (dx)
BH_SERV = {"bancada_px": (2676.4, 501.2, 2700.3, 554.9), "cuba_px": (2669.3, 514.7, 2693.1, 538.5),
           "antiga_px": (2666, 503, 2696, 543), "torneira_px": (2686.5, 525.1, 2699.5, 528.1), "base": "fim",
           "piso_amostra": (2622, 518, 2660, 560), "contorno": (30, 40, 54), "semente": 1315}
# as duas portas de giro da área de serviço descoberta (px, pelo PDF: a parede, o vão com os marcos, a folha)
PORTAS_DESC = [{"nome": "A. serviço descoberta, esquerda", "parede": (2463.2, 2473.4), "topo": 110.1, "base": 163.9,
                "folha": (2473.4, 113.1, 2521.1, 115.5), "dobra": "topo", "lado": 1, "soleira": True},
               {"nome": "A. serviço descoberta, direita", "parede": (2706.2, 2716.4), "topo": 110.1, "base": 163.9,
                "folha": (2658.5, 113.1, 2706.2, 115.5), "dobra": "topo", "lado": -1, "soleira": True}]
# a cozinha: as peças do PDF (índices) em Danae e na cor dos armários (BGR); o que fica por cima (o inox, o cooktop:
# pouco croma, compacto); a face e a sombra
COZINHA = {"danae": [(38671, 38920), (53847,), (38868,)], "armarios": [(88831,), (88836,), (88919,)], "cor_armario": (129, 160, 189),
           "face": 0.86, "fica_croma": 18, "fica_area": 8, "fica_max_px": 60, "sombra": 0.22, "semente": 1316}
# o vão das portas de correr das varandas (px): a faixa, e onde medir o tom do vinílico do quarto (logo abaixo da
# cortina); o marrom da faixa (R - B, lum máx.) e o vinílico do quarto
FAIXAS_VIN = [{"faixa": (1255, 316, 1440, 341), "tom": (1262, 346, 1400, 366)},
              {"faixa": (1440, 316, 1623, 341), "tom": (1450, 349, 1615, 369)},
              {"faixa": (2000, 318, 2166, 341), "tom": (2000, 346, 2170, 354)}]
VIN = {"marrom_rb": 25, "marrom_lum": 168, "croma": 28, "tom_rb": 50, "tom_lum": (100, 178)}
# os guarda-roupas (pt, dos polígonos do PDF): cada trecho sem o canto, com o lado das portas, e os cantos à parte
CLOSETS_TC = {
    "quarto 1": {"trechos": [((1601.3, 640.0, 1635.3, 733.5), "direita"), ((1635.3, 733.5, 1706.2, 767.6), "cima")],
                 "cantos": [(1601.3, 733.5, 1635.3, 767.6)]},
    "vizinho do quarto 1": {"trechos": [((1558.8, 640.0, 1592.8, 733.5), "esquerda"),
                                        ((1487.9, 733.5, 1558.8, 767.6), "cima")],
                            "cantos": [(1558.8, 733.5, 1592.8, 767.6)]},
    "quarto 3": {"trechos": [((898.3, 640.0, 932.3, 733.5), "direita"), ((932.3, 733.5, 1003.2, 767.6), "cima")],
                 "cantos": [(898.3, 733.5, 932.3, 767.6)]},
    "closet master 1": {"trechos": [((736.7, 538.0, 855.8, 572.0), "baixo"), ((855.8, 572.0, 889.8, 733.5), "esquerda"),
                                    ((736.7, 733.5, 855.8, 767.6), "cima")],
                        "cantos": [(855.8, 538.0, 889.8, 572.0), (855.8, 733.5, 889.8, 767.6)]},
    "closet master 2": {"trechos": [((901.1, 1019.8, 935.1, 1110.6), "esquerda"), ((731.0, 1110.6, 901.1, 1144.6), "cima")],
                        "cantos": [(901.1, 1110.6, 935.1, 1144.6)]},
    "semente": 1317}
# o armário da entrada do quarto 1 (px, PDF 88482): o retângulo e o lado das portas
ARMARIO_ENT = {"px": (1813.6, 569.9, 1924.1, 587.8), "lado": "baixo", "ss": 8}
# os quartos: os tapetes (PDF) com a amostra limpa da lã (px), as peças em volta deles e a amostra do vinílico do quarto
QUARTOS = {"tapetes": [{"pdf": 53797, "amostra": (1983, 530, 2003, 562)},
                       {"pdf": 53802, "amostra": (1277, 486, 1297, 512)}],
           "piso": {"q1": (1835, 600, 1905, 650), "q3": (1225, 515, 1275, 540)},
           "poltronas": ["quarto 1"], "cadeiras": ["quarto 1", "quarto 3"],
           "mesa_lateral": {"pdf": 88573, "png": "suite-3/criado-redondo", "d": 18.0, "quarto": "q1"},
           "anel_px": 4, "salto_px": 3, "salto_max_px": 14, "viz_px": 6, "texto_lum": 90, "madeira_rb": 40, "madeira_lum": 178}
LOTE = {"abre_px": 5, "nb": 245, "corpo": 0.8}
ANTES_DEPOIS = {"lavabos": (1080, 1480, 1640, 1700), "quartos": (300, 260, 2300, 760),
                "claraboias": (700, 230, 1100, 990), "hall": (2280, 1170, 2790, 1460), "garagem": (2690, 300, 3290, 700),
                "area_servico": (2540, 230, 2760, 520), "quarto_servico": (2440, 480, 2720, 690), "bh_servico": (2610, 488, 2712, 600), "area_descoberta": (2440, 40, 2740, 260), "cozinha": (2150, 240, 2480, 720), "varandas": (1240, 240, 2180, 380), "closets": (880, 320, 1960, 980), "quarto_1": (1960, 340, 2180, 680), "quarto_3": (1180, 340, 1460, 600),
                "inteira": (0, 0, 3840, 2160)}


def quadro():
    with contextlib.redirect_stdout(io.StringIO()):
        C.contexto_c()
        return F.Quadro("Terreo")


def _q(Q, r):
    a, b = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    return min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])


def _cob(a0, a1, n, o, ss):
    """A cobertura (0 a 1) de cada px [o, o + n) pelo intervalo [a0, a1]."""
    xs = np.arange(n * ss) / ss + o + 0.5 / ss
    return cv2.resize(((xs >= a0) & (xs < a1)).astype(np.float32)[None], (n, 1), interpolation=cv2.INTER_AREA)[0]


def box_ducha(Q, img):
    vb = F.vidros_box
    F.vidros_box = lambda Q_: list(BOX_DUCHA)
    try:
        return F.boxes_vidro(Q, img)
    finally:
        F.vidros_box = vb


def bancadas_cubas(Q, img, q=TRAV):
    out = img.astype(np.float32)
    for b in BANCADAS:
        cx0, cy0, cx1, cy1 = _q(Q, b["cuba"])
        bloco = img[int(cy0) + 2:int(cy1) - 1, int(cx0) + 2:int(cx1) - 1].reshape(-1, 3).astype(np.float32)
        lum = bloco.mean(axis=1)
        tom = np.median(bloco[lum >= np.percentile(lum, q["tom_pct"])], axis=0)   # a borda clara da cuba, sem a bacia
        for k, f in enumerate(b["faixas"]):
            x0, y0, x1, y1 = _q(Q, f)
            X0, Y0 = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1
            w, h = int(np.ceil(x1)) + 2 - X0, int(np.ceil(y1)) + 2 - Y0
            a = np.outer(_cob(y0, y1, h, Y0, q["ss"]), _cob(x0, x1, w, X0, q["ss"]))
            Qk = types.SimpleNamespace(px_m=Q.px_m)
            with contextlib.redirect_stdout(io.StringIO()):
                D = FA.travertino_bruto(Qk, h, w, q["semente"] + 7 * k + (0 if b["parede"] == "esq" else 50),
                                        q["veio"], q["faixa"], q["poros"], q["poro_esc"], forca=q["forca"])
            T = np.float32(tom)[None, None] * (D / float(np.mean(D)))[..., None]
            # o fio da borda: os lados livres (não o da parede)
            xi0, xi1 = (x0, x1 - 1.0) if b["parede"] == "dir" else (x0 + 1.0, x1)
            dentro = np.outer(_cob(y0 + 1.0, y1 - 1.0, h, Y0, q["ss"]), _cob(xi0, xi1, w, X0, q["ss"]))
            fio = np.clip(a - dentro, 0, 1)
            T = T * (1 - (1 - q["fio"]) * fio[..., None])
            reg = out[Y0:Y0 + h, X0:X0 + w]
            reg[:] = reg * (1 - a[..., None]) + T * a[..., None]
        print(f"    {b['nome']}: as 2 faixas da bancada no travertino da cuba (BGR {np.round(tom).astype(int)}), sem os "
              f"pontos e os fios brancos")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def veludo(P, alvo, q=VELUDO):
    """O PNG do B1 com o veludo no tom `alvo` (BGR): a luz do veludo (Y / mediana) ** gama vezes o alvo."""
    rgb = P[..., :3]
    hsv = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    h, s = hsv[..., 0], hsv[..., 1]
    m = ((h >= q["matiz"][0]) | (h < q["matiz"][1])) & (s > q["sat_min"]) & (P[..., 3] > 0)
    Y = rgb @ np.float32([0.114, 0.587, 0.299])
    r = (Y / max(float(np.median(Y[m])), 1.0)) ** q["gama"]
    novo = np.float32(alvo)[None, None] * r[..., None]
    w = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6)[..., None]
    Q2 = P.copy()
    Q2[..., :3] = np.clip(rgb * (1 - w) + novo * w, 0, 255)
    return Q2


def _banco_png(c, tam, P=None):
    """O PNG do B1 do jeito do `banco_b1`: os módulos do capitonê para a proporção do PDF; (P, cx, cy, L, D, giro)."""
    x0, y0, x1, y1 = c
    w, h = x1 - x0, y1 - y0
    L, D = max(w, h), min(w, h)
    png, per = MB.BANCOS_B1[tam]
    P = B1.ler_png(png) if P is None else P
    Hp, Wp = P.shape[:2]
    n = int(round((L / D * Hp - Wp) / per))
    c_ = Wp // 2
    if n != 0:
        P = np.concatenate([P[:, :c_], P[:, c_ - n * per:]], axis=1)
    return np.ascontiguousarray(P), (x0 + x1) / 2, (y0 + y1) / 2, L, D, (0.0 if w >= h else 90.0)


def _camada(P, cx, cy, L, D, giro, H, W):
    """O banco pousado sem sombra num fundo preto: a cor vezes a cobertura (a final é fundo * (1 - a) + isso)."""
    z = np.zeros((H, W, 3), np.float32)
    return BT.pousar(z, P, cx, cy, L, D, giro, [], PX_M, nao=None)


def bancos(Q, img):
    out = img.astype(np.float32)
    H, W = img.shape[:2]
    for nome, idx, tam, cor, alvo in TONS:
        c = MB.RT.caixa_pdf(Q, idx)
        P, cx, cy, L, D, giro = _banco_png(c, tam)
        P2 = veludo(P, alvo)
        x0, y0, x1, y1 = int(c[0]) - 6, int(c[1]) - 6, int(np.ceil(c[2])) + 7, int(np.ceil(c[3])) + 7
        velho = _camada(P, cx, cy, L, D, giro, H, W)[y0:y1, x0:x1]
        novo = _camada(P2, cx, cy, L, D, giro, H, W)[y0:y1, x0:x1]
        out[y0:y1, x0:x1] += novo - velho
        print(f"    {nome}: o banco B1 em veludo {cor}")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def claraboias(img, q=CLARA):
    import pedidos_terreo_casac_1311 as PT
    out = img.copy()
    tr = PT.TRACO
    for cl in PT.CLARABOIAS:
        x0, y0, x1, y1 = cl["ret"]
        X0, Y0, X1, Y1 = int(x0) - 12, int(y0) - 12, int(np.ceil(x1)) + 13, int(np.ceil(y1)) + 13
        reg = out[Y0:Y1, X0:X1]
        I = reg.astype(np.int16)
        lum, croma = I.mean(axis=2), I.max(axis=2) - I.min(axis=2)
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32) + 0.5
        f = q["faixa_px"]
        na_x = (yy >= y0 - f) & (yy <= y1 + f)
        na_y = (xx >= x0 - f) & (xx <= x1 + f)
        faixa = ((np.minimum(np.abs(xx - x0), np.abs(xx - x1)) <= f) & na_x) | \
                ((np.minimum(np.abs(yy - y0), np.abs(yy - y1)) <= f) & na_y)
        parede = np.abs(I - q["parede"][0]).max(axis=2) <= q["parede"][1]
        dentro = (xx > x0 + f) & (xx < x1 - f) & (yy > y0 + f) & (yy < y1 - f)
        piso = float(np.median(lum[dentro & ~parede & (lum > 100)])) if (dentro & ~parede & (lum > 100)).any() else 200.0
        esc = (lum < q["escuro"] * piso) & ~parede & (croma < 20)
        # onde a borda da claraboia é a face de uma parede (o box do BH master 2, o BH master 1): a franja entre a parede
        # e o piso (os pontinhos do tracejado antigo) também é resto: do lado de fora, parede; do lado de dentro, o
        # escuro até `face` da mediana do piso
        for lado, fora_, perto in (("x0", xx < x0, np.abs(xx - x0) <= f), ("x1", xx > x1, np.abs(xx - x1) <= f),
                                   ("y0", yy < y0, np.abs(yy - y0) <= f), ("y1", yy > y1, np.abs(yy - y1) <= f)):
            perto &= na_x if lado[0] == "x" else na_y
            alem = (np.abs(xx - (x0 - 3.5 if lado == "x0" else x1 + 3.5)) <= 1.0) & na_x if lado[0] == "x" else \
                (np.abs(yy - (y0 - 3.5 if lado == "y0" else y1 + 3.5)) <= 1.0) & na_y
            if alem.any() and parede[alem].mean() > 0.6:
                esc |= perto & ~fora_ & ~parede & (lum < q["face"] * piso) & (croma < 20)
                esc |= perto & fora_ & ~parede & (croma < 20) & (lum < piso * 0.9)
        # os restos: o escuro da faixa, menos o que está junto (`protege_px`) das peças que saem dela (o vidro do box, a
        # bacia): pelos componentes inteiros não dá, a franja escura junto à parede liga tudo ao vidro
        k = 2 * q["protege_px"] + 1
        prot = cv2.dilate((esc & ~faixa).astype(np.uint8), np.ones((k, k), np.uint8)) > 0
        resto = esc & faixa & ~prot
        junto = cv2.dilate(parede.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        cinza = np.median(reg[parede], axis=0) if parede.any() else np.float32(q["parede"][0])
        na_par = resto & junto & ((lum < 70) | ~((xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)))
        n_par = int(na_par.sum())
        reg[na_par] = np.round(cinza).astype(np.uint8)        # na parede (fora do retângulo ou bem escuro): o cinza dela
        resto &= ~na_par
        # no piso: o px de dentro da claraboia, `passo_px` para o meio, que não é resto nem parede
        cy_, cx_ = (y0 + y1) / 2 - Y0, (x0 + x1) / 2 - X0
        for v, u in zip(*np.nonzero(resto)):
            dy, dx = np.sign(cy_ - v), np.sign(cx_ - u)
            d = min(abs(yy[v, u] - y0), abs(yy[v, u] - y1)) < min(abs(xx[v, u] - x0), abs(xx[v, u] - x1))
            sy, sx = (dy, 0) if d else (0, dx)
            for k in range(q["passo_px"], q["busca_px"] + 1):
                vv, uu = int(v + sy * k), int(u + sx * k)
                if 0 <= vv < reg.shape[0] and 0 <= uu < reg.shape[1] and not resto[vv, uu] and not parede[vv, uu]:
                    reg[v, u] = reg[vv, uu]
                    break
        # o retângulo de fora, tracejado, cinza e fino (o mesmo do `pedidos_terreo_casac_1311.claraboias`)
        ss = tr["ss"]
        M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
        for p0, p1 in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            PT._tracejado(M, p0, p1, X0, Y0, tr, ss)
        a = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        out = PT.PS._pintar(out, a, X0, Y0, tr["cor"])
        print(f"    claraboia ({cl['nome']}): o retângulo de fora tracejado em cinza {tr['cor'][0]}, {tr['larg_px']} px; "
              f"{int(resto.sum()) + n_par} px de restos do tracejado antigo fora")
    return out


def _bib(nome):
    return cv2.imread(str(AQUI.parent / "biblioteca-objetos" / nome), cv2.IMREAD_UNCHANGED).astype(np.float32)


def aparador_png(L, D, q=APARADOR):
    """O aparador na proporção L x D: tira a madeira lisa (as colunas só de madeira) do meio dos trechos lisos entre os
    objetos, por igual, com uma costura suave; as pontas ficam."""
    P = _bib(q["png"])
    h, w = P.shape[:2]
    alvo = int(round(L / D * h))
    tirar = w - alvo
    if tirar <= 0:
        return P
    hsv = cv2.cvtColor(np.clip(P[..., :3], 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    lisa = (((hsv[..., 0] >= 5) & (hsv[..., 0] <= 25) & (hsv[..., 1] > 60)).mean(axis=0) > 0.97)
    runs, s0 = [], None
    for i, v in enumerate(lisa):
        if v and s0 is None:
            s0 = i
        if not v and s0 is not None:
            runs.append((s0, i))
            s0 = None
    meio = [r for r in runs if r[0] > 0 and r[1] < w and r[1] - r[0] >= q["lisos_min_px"]]
    cada = [tirar // len(meio) + (1 if k < tirar % len(meio) else 0) for k in range(len(meio))]
    cs = q["costura_px"]
    out, x = [], 0
    for (a, b), n in zip(meio, cada):
        c = (a + b) // 2
        c0, c1 = c - n // 2, c - n // 2 + n             # [c0, c1) sai
        esq = P[:, x:c0]
        dir_ = P[:, c1:c1 + cs]
        t = np.linspace(0, 1, cs, dtype=np.float32)[None, :, None]
        junta = esq[:, -cs:] * (1 - t) + dir_ * t
        out += [esq[:, :-cs], junta]
        x = c1 + cs
    out.append(P[:, x:])
    return np.ascontiguousarray(np.concatenate(out, axis=1))


def aparador_planta(Q, img, q=APARADOR):
    import paisagismo_terreo_casab_1311 as PJ
    out = img.copy()
    x0, y0, x1, y1 = q["refaz"]
    I = out.astype(np.int16)
    parede = (np.abs(I - 80).max(axis=2) <= 16)
    m = np.zeros(out.shape[:2], bool)
    m[y0:y1, x0:x1] = True
    m &= ~parede
    fx0, fy0, fx1, fy1 = q["fonte"]
    out = PJ.preencher(out, m, img[fy0:fy1, fx0:fx1].copy(), anel_px=6, nao=parede, sig=8.0)
    ax0, ay0, ax1, ay1 = q["ret"]
    L, D = ax1 - ax0, ay1 - ay0
    P = aparador_png(L, D)
    o = BT.pousar(out.astype(np.float32), P, (ax0 + ax1) / 2, (ay0 + ay1) / 2, L, D, 0.0, BT.SOMBRAS["movel"], PX_M)
    V = _bib(q["vaso"])
    ys, xs = np.nonzero(V[..., 3] > 0)
    V = np.ascontiguousarray(V[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    k = q["vaso_px"] / max(V.shape[:2])
    px0, py0, px1, py1 = q["planta"]
    o = BT.pousar(o, V, (px0 + px1) / 2, (py0 + py1) / 2, V.shape[1] * k, V.shape[0] * k, 0.0, BT.SOMBRAS["movel"],
                  PX_M)
    print(f"    hall: o aparador de freijó com os objetos ({L:.0f} x {D:.0f} px, {P.shape[1]} px do PNG) e o vaso de "
          f"folhagem ({q['vaso_px']:.0f} px) no lugar da caixa e do disco serrilhado")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def porta_hall(img, q=PORTA):
    out = img.copy()
    y0, y1 = q["linhas"]
    a0, a1 = q["amostra_x"]
    x0, x1 = q["refaz_x"]
    perfil = np.median(img[y0:y1, a0:a1].astype(np.float32), axis=1)
    out[y0:y1, x0:x1] = np.round(perfil[:, None, :]).astype(np.uint8)
    print(f"    porta do hall: a folha de x {x0} a {x1} como a parte de dentro (o miolo escuro de fora a fora)")
    return out


def seta_entrada(Q, img, q=SETA):
    import paisagismo_terreo_casab_1311 as PJ
    import terreo_casaa_1011 as TC
    x0, y0, x1, y1 = q["caixa"]
    zona = np.zeros(img.shape[:2], bool)
    zona[y0:y1, x0:x1] = img[y0:y1, x0:x1].astype(np.float32).mean(axis=2) < q["lum"]
    zona = cv2.dilate(zona.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    fx0, fy0, fx1, fy1 = q["fonte"]
    out = PJ.preencher(img, zona, img[fy0:fy1, fx0:fx1].copy(), anel_px=6, sig=8.0)
    cy = sum(q["vao_y"]) / 2
    cx = q["soleira_x"] + q["recuo_px"] + q["comp"] / 2
    out = TC.triangulo(out.astype(np.float32), TC.seta_tri(cx, cy, (-1, 0), q["comp"], q["larg"]))
    print(f"    entrada: sem a seta de 1,5 m ({int(zona.sum())} px de travertino refeito); o triângulo no centro do vão "
          f"(x {cx:.0f}, y {cy:.0f}), com a ponta para dentro")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def filete_garagem(Q, img, q=FILETE_G):
    import materiais_terreo_casac_1311 as MT
    out = img.astype(np.float32)
    # os pontinhos claros no piso marrom (antes do filete)
    px0, py0, px1, py1 = q["pontos"]
    sub = img[py0:py1, px0:px1]
    lum = sub.astype(np.float32).mean(axis=2)
    med = cv2.medianBlur(sub, 9).astype(np.float32).mean(axis=2)
    claro = (lum > med + q["claro"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(claro, connectivity=8)
    grande = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > q["area_max"]])
    carro = cv2.dilate(grande.astype(np.uint8), np.ones((2 * q["carro_px"] + 1,) * 2, np.uint8)) > 0
    # o texto do rótulo (GARAGEM, a área) é branco puro: fica
    texto = cv2.dilate((sub.min(axis=2) > q["texto_min"]).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    carro |= texto
    pontos = (claro > 0) & ~carro
    pontos = cv2.dilate(pontos.astype(np.uint8), np.ones((3, 3), np.uint8))
    pontos[carro] = 0
    novo = cv2.inpaint(np.ascontiguousarray(sub), pontos * 255, 3, cv2.INPAINT_TELEA)
    out[py0:py1, px0:px1][pontos > 0] = novo[pontos > 0]
    # o filete
    w_ = q["larg_m"] * Q.px_m
    ya, yb = q["y"] - w_ / 2, q["y"] + w_ / 2
    x0, x1 = q["x"]
    X0, Y0 = int(np.floor(x0)) - 1, int(np.floor(ya)) - 3
    W, H = int(np.ceil(x1)) + 2 - X0, int(np.ceil(yb)) + 5 - Y0
    ss = q["ss"]
    cx = _cob(x0, x1, W, X0, ss)
    a = np.outer(_cob(ya, yb, H, Y0, ss), cx)
    fx0, fy0, fx1, fy1 = q["fonte"]
    T = MT.sem_emenda(img[fy0:fy1, fx0:fx1].astype(np.float32), H, W)
    reg = out[Y0:Y0 + H, X0:X0 + W]
    sb = np.outer(_cob(yb, yb + q["sombra_px"], H, Y0, ss), cx)
    reg *= (1 - q["sombra"] * sb)[..., None]
    reg[:] = reg * (1 - a[..., None]) + T * a[..., None]
    f = q["fio_px"] / 2
    fio = np.outer(_cob(ya - f, ya + f, H, Y0, ss) + _cob(yb - f, yb + f, H, Y0, ss), cx)
    fio = np.clip(fio, 0, 1) * q["fio_alfa"]
    reg[:] = reg * (1 - fio[..., None]) + np.float32(q["fio"]) * fio[..., None]
    print(f"    garagem: {int(pontos.sum())} px de pontinhos claros fora; o filete de Bege Bahia ({w_:.1f} px) entre a "
          f"pedra portuguesa e o piso, de x {x0:.0f} a {x1:.0f}, com os fios e a sombrinha")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def maquinas(img, qs=MAQUINAS):
    import pedidos_terreo_casab_1211 as PB2
    out = img.astype(np.float32)
    for r in qs:
        out = PB2._maquina(out, r)
    print(f"    área de serviço: {len(qs)} máquinas de lavar no vão acima dos tanques, encostadas na parede")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def bancada_servico(img, q=BANCADA_SERV):
    from scipy import ndimage
    import pedidos_terreo_casab_1211 as PB2
    x0, y0, x1, y1 = q["ret"]
    X0, Y0 = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1
    W, H = int(np.ceil(x1)) + 1 - X0, int(np.ceil(y1)) + 2 - Y0
    reg = img[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    I = reg.astype(np.int16)
    lum = I.mean(axis=2)
    ss = q["ss"]
    cob = np.outer(_cob(y0, y1, H, Y0, ss), _cob(x0, x1, W, X0, ss))
    dentro = cob > 0.99
    # as cubas: o inox (pouco croma), em peças grandes, com os furos; a sombra bege em volta delas é pedra (sai)
    croma = I.max(axis=2) - I.min(axis=2)
    inox = dentro & (croma < q["inox_croma"])
    n, lab, st, _ = cv2.connectedComponentsWithStats(inox.astype(np.uint8), connectivity=8)
    cuba = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["cuba_area"]])
    cuba = ndimage.binary_fill_holes(cuba)
    a = cob * (1 - cv2.GaussianBlur(cuba.astype(np.float32), (0, 0), 0.5))
    imgB = cv2.imread(str(q["final_b"]))
    with contextlib.redirect_stdout(io.StringIO()):
        T = PB2._tabaco(imgB, q["fonte"], H, W, q["semente"]).astype(np.float32)
    # a sombra curta das cubas no granito (a luz do alto à direita)
    sb = cv2.GaussianBlur(cv2.warpAffine(cuba.astype(np.float32), np.float32([[1, 0, -1.0], [0, 1, 1.2]]), (W, H)),
                          (0, 0), 1.0) * (1 - cuba)
    T = T * (1 - q["cuba_sombra"] * sb)[..., None]
    reg = reg * (1 - a[..., None]) + T * a[..., None]
    # o contorno: a borda de 1 px nos lados livres (esquerda, cima, baixo), não na parede
    miolo = np.outer(_cob(y0 + 1.0, y1 - 1.0, H, Y0, ss), _cob(x0 + 1.0, x1, W, X0, ss))
    fio = np.clip(cob - miolo, 0, 1) * q["contorno_alfa"]
    reg = reg * (1 - fio[..., None]) + np.float32(q["contorno"]) * fio[..., None]
    out = img.copy()
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    área de serviço: a bancada dos tanques em granito marrom tabaco ({int((a > 0.5).sum())} px), as cubas de "
          f"inox ficam")
    return out


def _guarda_roupa(out, r, q, rng):
    """O guarda-roupa visto de cima (deitado em pé: o comprimento em y, a parede à esquerda), como os da Casa C."""
    x0, y0, x1, y1 = r
    ss = q["ss"]
    X0, Y0 = int(np.floor(x0)) - 3, int(np.floor(y0)) - 1
    W, H = int(np.ceil(x1)) + 5 - X0, int(np.ceil(y1)) + 5 - Y0
    a = np.outer(_cob(y0, y1, H, Y0, ss), _cob(x0, x1, W, X0, ss))
    t = np.clip((np.arange(W, dtype=np.float32) + X0 + 0.5 - x0) / (x1 - x0), 0, 1)
    c0, c1 = np.float32(q["arm_cor"][0]), np.float32(q["arm_cor"][1])
    cor = (c0[None, :] * (1 - t[:, None]) + c1[None, :] * t[:, None])[None].repeat(H, axis=0)
    # os cabides (traços deitados, de comprimentos um pouco diferentes) e o varão no meio, em supersample
    M = np.zeros((H * ss, W * ss), np.uint8)
    xm = (x0 + x1) / 2
    yy = y0 + q["cabide_px"] * 0.8
    while yy < y1 - 2:
        meia = (x1 - x0) * rng.uniform(0.30, 0.37)
        cv2.line(M, (int((xm - meia - X0) * ss), int((yy - Y0) * ss)), (int((xm + meia - X0) * ss), int((yy - Y0) * ss)),
                 255, max(1, int(0.8 * ss)), cv2.LINE_AA)
        yy += q["cabide_px"]
    cab = cv2.resize(M.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    V = np.zeros((H * ss, W * ss), np.uint8)
    cv2.line(V, (int((xm - X0) * ss), int((y0 + 2 - Y0) * ss)), (int((xm - X0) * ss), int((y1 - 2 - Y0) * ss)), 255,
             max(1, int(1.3 * ss)), cv2.LINE_AA)
    var = cv2.resize(V.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    cor = cor * (1 - (1 - q["cabide"]) * cab[..., None])
    cor = cor * (1 - var[..., None]) + np.float32(q["varao"]) * var[..., None]
    # o fio de madeira no lado aberto e na ponta de baixo
    miolo = np.outer(_cob(y0, y1 - 1.2, H, Y0, ss), _cob(x0, x1 - 1.2, W, X0, ss))
    fio = np.clip(a - miolo, 0, 1)
    cor = cor * (1 - fio[..., None]) + np.float32(q["fio"]) * fio[..., None]
    reg = out[Y0:Y0 + H, X0:X0 + W]
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, 1.2], [0, 1, 1.4]]), (W, H)), (0, 0), 1.2)
    reg *= (1 - q["sombra"] * sb * (1 - a))[..., None]
    reg[:] = reg * (1 - a[..., None]) + cor * a[..., None]
    return out


def quarto_servico(Q, img, q=QUARTO_S):
    import paisagismo_terreo_casab_1311 as PJ
    import camas_casac_1311 as CM
    out = img.copy()
    # o rótulo de antes: o alfa do branco contra o piso
    rx0, ry0, rx1, ry1 = q["rotulo"]
    sub = img[ry0:ry1, rx0:rx1].astype(np.float32)
    lum = sub.mean(axis=2)
    piso = float(np.median(lum[lum < 160]))
    alfa = np.clip((lum - piso - 6) / (245 - piso - 6), 0, 1)
    cor_txt = np.median(sub[alfa > 0.9], axis=0) if (alfa > 0.9).any() else np.float32((245, 245, 245))
    m = np.zeros(img.shape[:2], bool)
    m[ry0:ry1, rx0:rx1] = cv2.dilate((alfa > 0.04).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    fx0, fy0, fx1, fy1 = q["piso"]
    out = PJ.preencher(out, m, img[fy0:fy1, fx0:fx1].copy(), anel_px=5, sig=6.0)
    # a cama
    vx0, vy0, vx1, vy1 = q["vao"]
    c = MB.RT.caixa_pdf(Q, q["cama_pdf"])
    comp, larg = max(c[2] - c[0], c[3] - c[1]), min(c[2] - c[0], c[3] - c[1])
    with contextlib.redirect_stdout(io.StringIO()):
        P = CM.cama(q["cama"][0], q["cama"][1], q["cama"][2], "peseira")
    cx, cy = vx0 + comp / 2, vy1 - larg / 2
    o = BT.pousar(out.astype(np.float32), P, cx, cy, larg, comp, q["giro"], BT.SOMBRAS["movel"], PX_M)
    # o guarda-roupa
    fundo = q["arm_fundo_m"] * Q.px_m
    gy1 = vy1 - larg - q["arm_folga_m"] * Q.px_m
    o = _guarda_roupa(o, (vx0, vy0, vx0 + fundo, gy1), q, np.random.default_rng(q["semente"]))
    # o rótulo no lugar novo
    h, w = alfa.shape
    ncx, ncy = q["rotulo_centro"]
    nx0, ny0 = int(round(ncx - w / 2)), int(round(ncy - h / 2))
    reg = o[ny0:ny0 + h, nx0:nx0 + w]
    reg[:] = reg * (1 - alfa[..., None]) + np.float32(cor_txt) * alfa[..., None]
    print(f"    quarto de serviço: a cama de solteiro ({comp:.0f} x {larg:.0f} px) junto à parede de baixo, o guarda-roupa "
          f"({fundo:.0f} x {gy1 - vy0:.0f} px) na parede da esquerda; o rótulo subiu para ({ncx:.0f}, {ncy:.0f})")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def bh_servico(Q, img, q=BH_SERV):
    import pedidos_terreo_casab_1211 as PB2
    FAa = FA
    H, W = img.shape[:2]
    par = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                      and max(d["fill"]) < 0.6, ss=2) > 0.3
    o8 = img.copy()
    bx0, by0, bx1, by1 = q["bancada_px"]
    # o piso por baixo da cuba antiga e da parte da cuba nova que passa da bancada
    fora = np.zeros((H, W), bool)
    a0, b0, a1, b1 = q["antiga_px"]
    fora[b0:b1, a0:a1] = True
    fora |= PB2._ret_px_bool(H, W, q["cuba_px"])
    fora[int(np.floor(by0)):int(np.ceil(by1)), int(np.floor(bx0)) + 1:int(np.ceil(bx1))] = False
    fora &= ~par
    import paisagismo_terreo_casab_1311 as PJ
    banc = np.zeros((H, W), bool)
    banc[int(np.floor(by0)) - 1:int(np.ceil(by1)) + 2, int(np.floor(bx0)):int(np.ceil(bx1)) + 1] = True
    fx0, fy0, fx1, fy1 = q["piso_amostra"]
    # a folha clara da porta, a louça e o cinza das paredes (a beira delas) não dão o tom
    Ii = img.astype(np.int16)
    claro = (Ii.mean(axis=2) > 150) | ((Ii.max(axis=2) - Ii.min(axis=2)) < 25)
    o8 = PJ.preencher(o8, cv2.dilate(fora.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0,
                      img[fy0:fy1, fx0:fx1].copy(), anel_px=5, nao=par | banc | claro, sig=5.0)
    # a bancada: o marrom tabaco (a pedra da ilha gourmet da Casa B), o contorno e a sombra
    imgB = cv2.imread(str(BANCADA_SERV["final_b"]))
    antes_par = o8[par].copy()
    rb = PB2._pt(Q, q["bancada_px"])
    tl = FAa.tela(o8, Q, rb, folga=4)
    mb = tl.ret(rb, 0.2)
    FAa.sombra_q(tl, mb, forca=0.24, dist=0.9, sigma=0.9)
    with contextlib.redirect_stdout(io.StringIO()):
        T_ = PB2._tabaco(imgB, PB2.BANCADAS_TB["fonte_tabaco_px"], tl.h, tl.w, q["semente"])
    tl.pintar(mb, T_)
    tl.contorno(mb, 0.5, q["contorno"])
    o8 = tl.gravar()
    o8[par] = antes_par
    # a cuba de louça branca e a torneira cromada (a base na parede, a bica sobre a bacia)
    o8 = FAa.cuba_branca(Q, o8, PB2._pt(Q, q["cuba_px"]))
    t0, t1, t2, t3 = PB2._pt(Q, q["torneira_px"])
    tl = FAa.tela(o8, Q, (t0, t1, t2, t3), folga=4)
    ym = (t1 + t3) / 2
    bica = (t0, ym - 0.55, t2, ym + 0.55)
    base, ponta = ((t2, ym), (t0, ym)) if q["base"] == "fim" else ((t0, ym), (t2, ym))
    mb_ = tl.ret(bica, 0.5)
    FAa.sombra_q(tl, mb_, forca=0.30, dist=0.8, sigma=0.7)
    tl.pintar(mb_, FAa.CROMO["meio"])
    tl.contorno(mb_, 0.3, FAa.CROMO["contorno"])
    for (cx, cy), rr, cor in ((base, 1.5, FAa.CROMO["meio"]), (ponta, 0.8, FAa.CROMO["escuro"])):
        v = tl.vazia()
        px_, py_ = tl.pt(cx, cy)
        cv2.circle(v, (int(px_), int(py_)), int(rr * PB2.FA.PT_PX * 8), 255, -1, cv2.LINE_AA)
        tl.pintar(v, cor)
        tl.contorno(v, 0.3, FAa.CROMO["contorno"])
    o8 = tl.gravar()
    print("    BH serviço: a bancada em marrom tabaco com o contorno e a sombra, a cuba de louça branca no retângulo do PDF "
          "(sem a tira branca da antiga) e a torneira cromada")
    return o8


def portas_descoberta(Q, img, ps=PORTAS_DESC):
    import pedidos_terreo_casac_1311 as PT
    import pedidos_subsolo_casab_1211 as PB
    x0, y0, x1, y1 = PT.PORTAS["soleira_px"]
    sol = tuple(float(v) for v in np.median(img[y0:y1, x0:x1].reshape(-1, 3), axis=0))
    base = dict(PB.PORTAS_SB, tique_px=(0, 0, 0, 0), soleira=sol)
    with contextlib.redirect_stdout(io.StringIO()):
        out = PB.portas_sb(Q, img.copy(), q=dict(base, portas=list(ps)))
    print(f"    área de serviço descoberta: as {len(ps)} portas de giro com a folha de madeira clara, quina com quina na "
          f"ponta da parede, e a soleira no vão")
    return out


def cozinha(Q, img, q=COZINHA):
    import terreo_casaa_1011 as TC
    H, W = img.shape[:2]
    out = img.astype(np.float32)
    I = img.astype(np.int16)
    croma = I.max(axis=2) - I.min(axis=2)

    def fica(m):
        """O que está por cima da peça (as cubas, as torneiras, o cooktop): pouco croma, compacto (não as linhas
        compridas das bordas)."""
        c = (m & (croma < q["fica_croma"])).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(c, connectivity=8)
        ok = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["fica_area"]
              and max(st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]) <= q["fica_max_px"]]
        return cv2.dilate(np.isin(lab, ok).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0

    def sombra(m):
        a = m.astype(np.float32)
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -1.0], [0, 1, 1.3]]), (W, H)), (0, 0), 1.1)
        return sb * (1 - a)

    def peca(ids, cor):
        nonlocal out
        a, m = MB.RT.mascara_pdf(Q, list(ids))
        # as linhas cinzas da borda antiga, logo fora da peça (as compridas, de pouco croma): o piso de volta
        anel = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~m
        c = (anel & (croma < q["fica_croma"])).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(c, connectivity=8)
        lin = np.isin(lab, [i for i in range(1, n) if max(st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]) >
                            q["fica_max_px"]])
        if lin.any():
            ys, xs = np.nonzero(lin)
            y0, y1, x0, x1 = max(ys.min() - 6, 0), ys.max() + 7, max(xs.min() - 6, 0), xs.max() + 7
            sub = np.clip(np.round(out[y0:y1, x0:x1]), 0, 255).astype(np.uint8)
            mk = cv2.dilate(lin[y0:y1, x0:x1].astype(np.uint8), np.ones((3, 3), np.uint8)) & ~m[y0:y1, x0:x1]
            novo = cv2.inpaint(sub, mk.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA).astype(np.float32)
            out[y0:y1, x0:x1][mk > 0] = novo[mk > 0]
        out *= (1 - q["sombra"] * sombra(m))[..., None]
        f = fica(m)
        borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        cor = cor * np.where(borda, q["face"], 1.0)[..., None]
        al = a[..., None] * (~f)[..., None]
        out = out * (1 - al) + cor * al
        return int(m.sum()), int(f.sum())
    danae = TC.danae(H, W, q["semente"]).astype(np.float32)
    n_d = [peca(i, danae) for i in q["danae"]]
    cor_a = np.broadcast_to(np.float32(q["cor_armario"]), (H, W, 3))
    n_a = [peca(i, cor_a) for i in q["armarios"]]
    print(f"    cozinha: a bancada em L, a ilha e a bancada da direita em Dekton Danae ({sum(n for n, _ in n_d)} px; "
          f"{sum(f for _, f in n_d)} px de cubas, torneiras e cooktop por cima); os 2 armários altos e as prateleiras do "
          f"louceiro 1 na cor dos armários, lisa ({sum(n for n, _ in n_a)} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def faixa_vinilico(img, fs=FAIXAS_VIN, q=VIN):
    """O vão de cada porta no piso do quarto: as linhas do vinílico de logo abaixo da cortina, espelhadas para cima
    (as mesmas réguas e o mesmo tom, coluna a coluna); onde a coluna não tem vinílico, a mais perto que tem."""
    out = img.copy()
    I = img.astype(np.int16)
    L = I.mean(axis=2)
    croma = I.max(axis=2) - I.min(axis=2)
    n = 0
    for f in fs:
        x0, y0, x1, y1 = f["faixa"]
        tx0, ty0, tx1, ty1 = f["tom"]
        T_ = I[ty0:ty1, x0:x1]
        Lt = T_.mean(axis=2)
        vin = ((T_[..., 2] - T_[..., 0]) > q["tom_rb"]) & (Lt > q["tom_lum"][0]) & (Lt < q["tom_lum"][1])
        cols = np.arange(x0, x1)
        dentro = (cols >= tx0) & (cols < tx1)
        boas = np.nonzero((vin.mean(axis=0) > 0.9) & dentro)[0]
        src_x = boas[np.abs(np.arange(x1 - x0)[:, None] - boas[None, :]).argmin(axis=1)] + x0
        h_s = ty1 - ty0
        Ib = I[y0:y1, x0:x1]
        m = ((Ib[..., 2] - Ib[..., 0]) > q["marrom_rb"]) & (L[y0:y1, x0:x1] < q["marrom_lum"]) & \
            (croma[y0:y1, x0:x1] > q["croma"])
        for k, y in enumerate(range(y1 - 1, y0 - 1, -1)):
            j = k % (2 * h_s)
            sy = ty0 + (j if j < h_s else 2 * h_s - 1 - j)
            row = img[sy, src_x]
            mm = m[y - y0]
            out[y, x0:x1][mm] = row[mm]
        n += int(m.sum())
    print(f"    varandas: o vão das portas de correr acima da cortina no vinílico do quarto, as réguas de logo abaixo da "
          f"cortina espelhadas ({n} px)")
    return out


def closets(Q, img, q=CLOSETS_TC):
    import um_pav_casaa_1111 as U
    out = np.ascontiguousarray(img.copy())
    rng = np.random.default_rng(q["semente"])
    qa = dict(U.CLOSETS_1P)
    nomes = [k for k in q if k != "semente"]
    for n in nomes:
        out = U._closet(Q, out, q[n], qa, rng)
    print(f"    guarda-roupas: {', '.join(nomes)} numa peça só, sem a divisão no canto, os cabides se encontrando")
    return out


def armario_entrada(img, q=ARMARIO_ENT):
    """O armário raso: o miolo bege (o dos guarda-roupas, `um_pav_casaa_1111.CLOSETS_1P`) que escurece junto às portas,
    a moldura ocre (as laterais, o fundo e a faixa das portas) e o contorno escuro."""
    import um_pav_casaa_1111 as U
    qa = U.CLOSETS_1P
    x0, y0, x1, y1 = q["px"]
    ss = q["ss"]
    cmp = U.CM * Q_PX_PT
    X0, Y0 = int(np.floor(x0)) - 2, int(np.floor(y0)) - 2
    W, H = int(np.ceil(x1)) + 3 - X0, int(np.ceil(y1)) + 3 - Y0
    a = np.outer(_cob(y0, y1, H, Y0, ss), _cob(x0, x1, W, X0, ss))
    yy = (np.arange(H, dtype=np.float32) + Y0 + 0.5 - y0) / (y1 - y0)
    fr = np.clip(yy if q["lado"] == "baixo" else 1 - yy, 0, 1)
    t = (216 - 40 * fr ** 1.4)[:, None, None] * np.ones((1, W, 3), np.float32) / 216 * np.float32(qa["miolo"])
    mold = np.float32(qa["moldura"])

    def faixa(a0, a1, b0, b1):
        return np.outer(_cob(b0, b1, H, Y0, ss), _cob(a0, a1, W, X0, ss))
    lat, fun, por, con = (qa[k] * cmp for k in ("lateral_cm", "fundo_cm", "porta_cm", "contorno_cm"))
    porta_y = (y1 - por, y1) if q["lado"] == "baixo" else (y0, y0 + por)
    fundo_y = (y0, y0 + fun) if q["lado"] == "baixo" else (y1 - fun, y1)
    m = np.clip(faixa(x0, x0 + lat, y0, y1) + faixa(x1 - lat, x1, y0, y1) + faixa(x0, x1, *porta_y) +
                faixa(x0, x1, *fundo_y), 0, 1)
    t = t * (1 - m[..., None]) + mold * m[..., None]
    c = np.clip(a - np.outer(_cob(y0 + con, y1 - con, H, Y0, ss), _cob(x0 + con, x1 - con, W, X0, ss)), 0, 1)
    t = t * (1 - c[..., None]) + mold * 0.68 * c[..., None]
    out = img.astype(np.float32)
    reg = out[Y0:Y0 + H, X0:X0 + W]
    reg[:] = reg * (1 - a[..., None]) + t * a[..., None]
    print(f"    quarto 1: o armário raso da entrada ({x1 - x0:.0f} x {y1 - y0:.0f} px), as portas para a entrada")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _alfa(P, cx, cy, wt, ht, g, forma):
    return MB.RT._alfa_peca(P, cx, cy, wt, ht, g, forma)


def _cama_pose(Q, item):
    """A cama como em `mobiliario_terreo_casac_1311.camas`: (P, cx, cy, wt, ht, giro)."""
    import camas_casac_1311 as CM
    import manta_caida_casac_1311 as MC
    nome, i, giro, tipo, roupa, enf, modo, lado, bancos_ = item
    x0, y0, x1, y1 = MB.RT.caixa_pdf(Q, i)
    comp, larg = (y1 - y0, x1 - x0) if giro in (0.0, 180.0) else (x1 - x0, y1 - y0)
    with contextlib.redirect_stdout(io.StringIO()):
        if modo == "manta":
            P0 = CM.cama(tipo, roupa, enf, "nada")
            P, p = MC.manta_caida(P0, enf, lado)
        else:
            P0 = CM.cama(tipo, roupa, enf, "peseira")
            P, p = P0, 0
    H0, W0 = P0.shape[:2]
    return P, (x0 + x1) / 2, (y0 + y1) / 2, larg * (W0 + 2 * p) / W0, comp * (H0 + 2 * p) / H0, giro, (x0, y0, x1, y1)


def _poltrona_pose(Q, nome):
    for n, png, ip, png_pufe, ipufe in MB.POLTRONAS:
        if n != nome:
            continue
        _, mp = MB.contorno(Q, [ip])
        _, mf = MB.contorno(Q, [ipufe])
        ys, xs = np.nonzero(mp)
        pc = np.array([xs.mean(), ys.mean()])
        ys2, xs2 = np.nonzero(mf)
        fc = np.array([xs2.mean(), ys2.mean()])
        g = MB.frente(fc - pc)
        (_, _), (w, h), _ = cv2.minAreaRect(np.column_stack([xs, ys]).astype(np.float32))
        lado = 0.92 * min(w, h)
        P = MB.ler(png)
        (_, _), (w2, h2), _ = cv2.minAreaRect(np.column_stack([xs2, ys2]).astype(np.float32))
        Pf = MB.ler(png_pufe)
        buraco = MB.RT.dilatar(mp, 8) | MB.RT.dilatar(mf, 8)
        return [(P, pc[0], pc[1], lado * P.shape[1] / P.shape[0], lado, g),
                (Pf, fc[0], fc[1], max(w2, h2), min(w2, h2), g)], buraco


def _cadeira_pose(Q, nome):
    q = MB.CADEIRA_ESC
    for n, ids, borda, lado, mesa_px in MB.CADEIRAS:
        if n != nome:
            continue
        _, m = MB.contorno(Q, list(ids))
        ys, xs = np.nonzero(m)
        X0, Y0, X1, Y1 = xs.min() - 3, ys.min() - 3, xs.max() + 4, ys.max() + 4
        buraco = np.zeros(m.shape, bool)
        buraco[Y0:Y1, X0:X1] = True
        mx0, my0, mx1, my1 = mesa_px
        buraco[my0:my1, mx0:mx1] = False
        P = MB.ler(q["png"])
        wt = q["larg"]
        ht = wt * P.shape[0] / P.shape[1]
        f = q["sob"]
        if lado == "dir":
            cx, cy, g = borda - ht / 2 + f * ht, (ys.min() + ys.max()) / 2, 90.0
        elif lado == "esq":
            cx, cy, g = borda + ht / 2 - f * ht, (ys.min() + ys.max()) / 2, -90.0
        else:
            cx, cy, g = (xs.min() + xs.max()) / 2, borda - ht / 2 + f * ht, 0.0
        mesa = np.zeros(m.shape, bool)
        mesa[my0:my1, mx0:mx1] = True
        return (P, cx, cy, wt, ht, g), buraco, mesa


def _sombra_em(out, alfa, onde):
    """A sombra curta das peças (`BT.SOMBRAS["movel"]`, alfa somado) só nos px `onde`."""
    o = out.astype(np.float32)
    f = np.ones(alfa.shape, np.float32)
    for sb in BT.SOMBRAS["movel"]:
        sh = cv2.GaussianBlur(alfa, (0, 0), max(0.3, sb["sig"] * PX_M))
        Ms = np.float32([[1, 0, sb["dx"] * PX_M], [0, 1, sb["dy"] * PX_M]])
        sh = cv2.warpAffine(sh, Ms, (alfa.shape[1], alfa.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        f *= 1 - sb["forca"] * sh * (1 - alfa)
    o[onde] *= f[onde][..., None]
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def quartos(Q, img, q=QUARTOS):
    import paisagismo_terreo_casab_1311 as PJ
    import materiais_terreo_casac_1311 as MT
    H, W = img.shape[:2]
    forma = (H, W)
    out = img.copy()
    par = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                      and max(d["fill"]) < 0.6, ss=2) > 0.3
    # as peças que ficam (alfa) e os buracos de piso do mobiliário
    pecas, buracos, mesas = [], np.zeros(forma, bool), np.zeros(forma, bool)
    for n in q["poltronas"]:
        ps, bur = _poltrona_pose(Q, n)
        pecas += ps
        buracos |= bur
    for n in q["cadeiras"]:
        pz, bur, mesa = _cadeira_pose(Q, n)
        pecas.append(pz)
        buracos |= bur
        mesas |= mesa
    obj = np.zeros(forma, np.float32)
    for P, cx, cy, wt, ht, g in pecas:
        obj = np.maximum(obj, _alfa(P, cx, cy, wt, ht, g, forma))
    camas = [_cama_pose(Q, it) for it in MB.CAMAS]
    a_cama = np.zeros(forma, np.float32)
    for P, cx, cy, wt, ht, g, _ in camas:
        a_cama = np.maximum(a_cama, _alfa(P, cx, cy, wt, ht, g, forma))
    a_banco = np.zeros(forma, np.float32)
    bancos_ = [(MB.RT.caixa_pdf(Q, b), "solteiro" if it[3] == "solteiro" else "casal") for it in MB.CAMAS for b in it[8]]
    bancos_.append((MB.RT.caixa_pdf(Q, MB.BANCO_MASTER["pdf"]), "casal"))
    for c, tam in bancos_:
        P, cx, cy, L, D, g = _banco_png(c, tam)
        a_banco = np.maximum(a_banco, _alfa(P, cx, cy, L, D, g, forma))
    criados = np.zeros(forma, bool)
    for i, *_ in MB.CRIADOS:
        x0, y0, x1, y1 = MB.RT.caixa_pdf(Q, i)
        criados[int(y0) - 3:int(np.ceil(y1)) + 4, int(x0) - 3:int(np.ceil(x1)) + 4] = True
    mx = q["mesa_lateral"]
    lx0, ly0, lx1, ly1 = MB.RT.caixa_pdf(Q, mx["pdf"])
    lcx, lcy = (lx0 + lx1) / 2, (ly0 + ly1) / 2
    yy, xx = np.mgrid[0:H, 0:W]
    lateral = (xx - lcx) ** 2 + (yy - lcy) ** 2 <= (mx["d"] / 2 + 4) ** 2
    buracos |= lateral
    fixo = (obj > 0.02) | (a_cama > 0.02) | (a_banco > 0.02) | par | criados | mesas
    I = img.astype(np.int16)
    madeira = ((I[..., 2] - I[..., 0]) > q["madeira_rb"]) & (I.mean(axis=2) < q["madeira_lum"])
    # 1. os tapetes: a lã de volta onde o piso entrou (o retângulo do PDF, menos as peças)
    rug_all = np.zeros(forma, bool)
    n_t = 0
    for t in q["tapetes"]:
        x0, y0, x1, y1 = MB.RT.caixa_pdf(Q, t["pdf"])
        X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
        cov = np.zeros(forma, np.float32)
        cov[Y0:Y1, X0:X1] = np.outer(_cob(y0, y1, Y1 - Y0, Y0, 8), _cob(x0, x1, X1 - X0, X0, 8))
        rug_all |= cov > 0.5
        m = (cov > 0.01) & (buracos | madeira) & ~fixo
        ax0, ay0, ax1, ay1 = t["amostra"]
        T = MT.sem_emenda(img[ay0:ay1, ax0:ax1].astype(np.float32), Y1 - Y0, X1 - X0)
        big = np.zeros((H, W, 3), np.float32)
        big[Y0:Y1, X0:X1] = T
        o = out.astype(np.float32)
        o[m] = o[m] * (1 - cov[m][..., None]) + big[m] * cov[m][..., None]
        out = np.clip(np.round(o), 0, 255).astype(np.uint8)
        n_t += int(m.sum())
    # 2. o piso em volta das peças (o buraco do mobiliário fora do tapete): o vinílico do quarto no tom do entorno
    piso_m = buracos & ~rug_all & ~fixo
    for k, (fx0, fy0, fx1, fy1) in q["piso"].items():
        reg = np.zeros(forma, bool)
        reg[fy0 - 260:fy1 + 260, fx0 - 260:fx1 + 260] = True
        m = piso_m & reg
        if m.any():
            out = PJ.preencher(out, m, img[fy0:fy1, fx0:fx1].copy(), anel_px=6, nao=fixo | rug_all | buracos, sig=8.0)
            piso_m &= ~m
    out = _sombra_em(out, obj, buracos & ~fixo)
    # 3. a mesa lateral
    Pm = MB.ler(mx["png"])
    o = BT.pousar(out.astype(np.float32), Pm, lcx, lcy, mx["d"], mx["d"], 0.0, BT.SOMBRAS["movel"], PX_M)
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    # 4. o contorno das camas: o anel (o retângulo do PDF mais `anel_px`) fora da cama nova, do lado de fora para dentro
    e, sl = q["anel_px"], q["salto_px"]
    # os rótulos (as letras escuras e sem cor) não são fonte nem são refeitos
    Io = out.astype(np.int16)
    texto = (Io.mean(axis=2) < q["texto_lum"]) & ((Io.max(axis=2) - Io.min(axis=2)) < 30)
    base_ok = ~(fixo | (a_cama > 0.01))
    n_a = 0
    for P, cx, cy, wt, ht, g, (x0, y0, x1, y1) in camas:
        X0, Y0, X1, Y1 = int(np.floor(x0)) - e, int(np.floor(y0)) - e, int(np.ceil(x1)) + e, int(np.ceil(y1)) + e
        anel = np.zeros(forma, bool)
        anel[Y0:Y1, X0:X1] = True
        anel &= (a_cama < 0.02) & ~fixo
        # as letras dos rótulos perto da cama (o escuro fora do retângulo + 3 px; o contorno escuro antigo fica dentro)
        perto = np.zeros(forma, bool)
        perto[Y0 + e - 3:Y1 - e + 3, X0 + e - 3:X1 - e + 3] = True
        letras = cv2.dilate((texto & ~perto).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        fonte_ok = base_ok & ~letras
        anel &= ~letras
        ys, xs = np.nonzero(anel)
        resto = []
        for y, x in zip(ys, xs):
            d = {(0, -1): y - Y0, (0, 1): Y1 - 1 - y, (-1, 0): x - X0, (1, 0): X1 - 1 - x}
            for (dx, dy), dist in sorted(d.items(), key=lambda kv: kv[1]):
                k = dist + sl
                if k > q["salto_max_px"]:
                    resto.append((y, x))
                    break
                sy, sx = y + dy * k, x + dx * k
                if 0 <= sy < H and 0 <= sx < W and fonte_ok[sy, sx]:
                    out[y, x] = out[sy, sx]
                    break
            else:
                resto.append((y, x))
        # os px sem fonte perto (junto aos criados e à parede): a mediana do piso livre em volta (o anel fora)
        r_ = q["viz_px"]
        livre = fonte_ok & ~anel
        for y, x in resto:
            a0, a1, b0, b1 = max(y - r_, 0), y + r_ + 1, max(x - r_, 0), x + r_ + 1
            v = livre[a0:a1, b0:b1]
            if v.any():
                out[y, x] = np.median(out[a0:a1, b0:b1][v], axis=0)
        n_a += len(ys)
        a1 = _alfa(P, cx, cy, wt, ht, g, forma)
        out = _sombra_em(out, a1, anel)
    print(f"    quartos: os tapetes do quarto 1 e do quarto 3 inteiros ({n_t} px de lã de volta), o piso em volta da "
          f"poltrona, do pufe e das cadeiras no vinílico do quarto, a mesa lateral de madeira no quarto 1; o contorno "
          f"claro de {len(camas)} camas fora ({n_a} px), com a sombra curta")
    return out


def tracejado_lote(img, q=LOTE):
    from scipy import ndimage
    nb = (img.min(axis=2) < q["nb"]).astype(np.uint8)
    k = q["abre_px"]
    ab = cv2.morphologyEx(nb, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(ab, connectivity=8)
    lote = ndimage.binary_fill_holes(lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    lote = cv2.dilate(lote.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    out = img.copy()
    fora = ~lote & (nb > 0)
    out[~lote] = 255
    # o muro de baixo passava da borda direita do lote até a quina do tracejado: para na borda, como o de cima (e como
    # na Casa B); a borda é a coluna mais à direita do lote acima dele
    H = img.shape[0]
    cols = np.nonzero((out[:int(H * q["corpo"])].min(axis=2) < q["nb"]).any(axis=0))[0]
    borda = int(cols.max()) + 1
    n_muro = int((out[:, borda + 1:].min(axis=2) < q["nb"]).sum())
    out[:, borda + 1:] = 255
    print(f"    o tracejado do lote: {int(fora.sum())} px fora do lote em branco; o muro de baixo para na borda (x {borda}, "
          f"{n_muro} px)")
    return out


def aplicar(antes):
    Q = quadro()
    out = box_ducha(Q, antes)
    out = bancadas_cubas(Q, out)
    out = bancos(Q, out)
    out = claraboias(out)
    out = aparador_planta(Q, out)
    out = porta_hall(out)
    out = seta_entrada(Q, out)
    out = filete_garagem(Q, out)
    out = maquinas(out)
    out = bancada_servico(out)
    out = quarto_servico(Q, out)
    out = bh_servico(Q, out)
    out = portas_descoberta(Q, out)
    out = cozinha(Q, out)
    out = faixa_vinilico(out)
    out = closets(Q, out)
    out = armario_entrada(out)
    out = quartos(Q, out)
    out = tracejado_lote(out)
    return out


def final_de(commit):
    dado = subprocess.run(["git", "show", f"{commit}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"], cwd=RAIZ_GIT,
                          capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(2.5, 1800 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        j = np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b])
        t = np.full((44, j.shape[1], 3), 255, np.uint8)
        cv2.putText(t, "ANTES (em cima) | DEPOIS (embaixo)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2,
                    cv2.LINE_AA)
        cv2.imwrite(str(R / f"POE642_CasaC_PH_Terreo_1311_revisao12k_{nome}_antes_depois.jpg"), np.vstack([t, j]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes) if a.antes else final_de(ANTES_COMMIT)
    depois = aplicar(antes)
    cv2.imwrite(a.saida or str(FINAL), depois)
    print(f"    {a.saida or FINAL.name}")
    if not a.saida:
        antes_depois(antes, depois)


if __name__ == "__main__":
    main()

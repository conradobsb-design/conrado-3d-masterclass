"""As alterações da Casa A no Térreo da Casa B (13/11).

Usuário, vendo o Térreo da Casa B ao lado da lista do que a Casa A recebeu depois de 12/11: "VAMOS REVISAR OS
MOBILIÁRIOS DO TÉRREO DA CASA B E REALIZAR AS ALTERAÇÕES FEITAS NA CASA A LISTADAS ACIMA". Sobre a final de 4574dc9 (o
Térreo de 12/11), as regras aprovadas na Casa A (o mobiliário vai pela proposta, à parte):
- **Letras (`LETRAS_TB`, `letras`):** o D logo abaixo da seta das 3 escadas (DESCE PARA O SUBSOLO, PARA O DECK e PARA O
  JARDIM), como no Térreo da Casa A (`pedidos_terreo_casaa_1211c.letras`, `letras_escadas_casaa_1211.um_pav`): no corpo
  e na cor das descrições, centrado sob o triângulo, a `folga_px` dele; uma anotação "txt" a mais nos dados do 12K
  (`POE642_CasaB_PH_Terreo_12K_dados.json`), que o `montar12k` desenha (A na Inter, B na Kalam).
- **Shafts (`SHAFTS_TB`, `shafts`):** os 2 vãos (junto à sala íntima e junto à cozinha) no claro e o X de canto a canto
  em cinza fino, tracejado (`regras_1211_casaa.desenhar_x`, a regra de 12/11), com a borda de parede em volta limpa
  (`limpar_aro`); no 12K, desenhados na escala dele (`regras_1211_casaa.shafts_12k`).
- **Chuveiros (`CHUVEIROS_TB`, `chuveiros`):** os desenhos em planta (`chuveiros_planta_casaa_1211`, como no 1º
  Pavimento da Casa A e no Subsolo da Casa B): os 2 de teto do banho master no quadrado do PDF; os de parede (banhos 1,
  2 e 3, os 2 BH gourmet e a ducha do deck) com a placa quadrada e o braço até a face da parede; os do BH serviço e do
  BH motorista, redondos de parede (o banho de serviço da Casa A). Os de antes (a placa, o braço, a canopla e a sombra)
  viram o piso do lado (`biblioteca_subsolo_casab_1311.piso_desloc`, com a costura); a sombra `chuveiro`.
- **Paredes retas (`PAREDES_TB`, `paredes`):** `biblioteca_subsolo_casaa_1211.paredes_retas` no cinza 80 das paredes da
  Casa B, com as proteções do Térreo da Casa A (`regras_1211_casaa`: os objetos do PDF, as folhas e esquadrias da
  ARQ_PAREDE fora do cinza das paredes, só o branco ligado à borda é o lado de fora) e o elevador.
- **Tapetes das suítes (`TAPETES_TB`, `tapetes`; "NÃO VOU QUERER TROCAR AS CAMAS QUE EU JÁ COLOQUEI, MAS QUERO O RETOQUE
  EM VOLTA DO CONTORNO E NOS TAPETES"):** o tapete do PDF de cada suíte refeito inteiro com o da biblioteca no tom do de
  hoje; as camas de 12/11 (e os bancos, o sofá e os criados) por cima pelo contorno do PDF, com a sombra curta dos
  móveis: o halo da IA em volta das camas sai.
- **Peças do Higgsfield (`GELADEIRAS_TB`, `RECAMIERS_TB`, `BANCO_CLOSET_TB`, `CORTINAS_TB`, `pecas_higgsfield`; "G2, R7,
  B1, C4", e o recamier depois trocado pelo R11, na medida do original):** a geladeira inox nos 3 retângulos da cozinha,
  a frente para a ilha; o banco estofado capitonê no closet master; os 2 recamiers de veludo na suíte master (o de
  antes achado na imagem, o piso por baixo em espelho dentro da madeira ao lado, as mesinhas de volta por cima); a
  cortina de linho em ondas nos trilhos do PDF (os trechos que se sobrepõem unidos), o trilho grafite do lado do vidro.
- **Jardim de inverno (`JARDIM_TB`, `jardim_inverno`):** "NÃO HÁ A NECESSIDADE DE TANTOS X, FAÇA APENAS UM DE UMA DIAGONAL
  A OUTRA": os tracejados de antes saem e entra um X só, de canto a canto, interrompido em volta do rótulo; "AS FOLHAS DE
  BAIXO PRECISAM ESTAR EM CONTATO UMA COM A OUTRA": as 3 folhas de baixo encostadas.
- **Rótulos em grade (`ROTULOS_GRADE_TB`, `rotulos_grade`):** SUÍTE 1 e 2 numa linha, CIRCULAÇÃO e SUÍTE 3 noutra, SUÍTE 1
  e CIRCULAÇÃO numa coluna, SUÍTE 2 e 3 noutra; o de antes sai pela conta do alfa, o novo entra pelo mesmo desenho, e os
  dados do 12K levam os desvios novos.
- **Esquadrias pretas (`ESQUADRIAS_TB`, `esquadrias`; vendo a prévia: "FAÇA APENAS O CONTORNO DA ESQUADRIA EM
  PRETO"):** o contorno dos boxes, das portas de vidro e dos caixilhos das janelas em preto, fino, o vidro claro (a regra de 12/11 da Casa A, "As esquadrias dos box, portas de
  vidro e janelas são pretas"): os traços do PDF (os da ARQ_PAREDE e, nas louças, os vidros dos boxes: longos e finos)
  desenhados em preto onde a final mostra o vidro ou o alumínio neutro; a parede, a madeira das portas de giro, o bronze
  dos brises e os chuveiros não mudam. A primeira tentativa (o traço neutro da ARQ_PAREDE escurecido pela cor) ficou
  irregular: os boxes não pegavam e as linhas escureciam pela metade.
- **Mobiliário (`MOBILIARIO_TB`, `ABAJURES_TB`, `BALCAO_TB`, `CADEIRAS_TB`, `mobiliario`; as 15 respostas, "A BANCADA
  DO BH. MOTORISTA É MARROM TABACO", "FALTOU A CADEIRA DE ESCRITORIO NAS ESCRIVANINHAS"):** as peças da Casa A no
  retângulo do PDF: criados com abajur, a bancada dupla esculpida e as bacias Carrara do banho master, a cuba esculpida
  e a bacia dos banhos 1 a 3, o lavabo, as bacias marrons e as cubas esculpidas do BH gourmet, só a louça da cuba e a
  bacia Monte Carlo nos BH serviço e motorista, cooktops de 4 bocas (o resto do de 5 vira bancada, `balcao`), as cubas
  e os tanques Franke, a grelha; e a cadeira de escritório nas 3 escrivaninhas, 1/3 por baixo da mesa (`cadeiras`).
- **Mobiliário, 2ª etapa (`SALA_INTIMA_TB`, `JANTAR_TB`, `ESPREG_TB`, `BANQUETAS_TB`; "PODE FAZER A 2ª ETAPA"):** a sala
  íntima com o conjunto da Casa A (tapete, sofá em L A, mesas laterais, poltrona A; a mesa de centro e a quadrada
  ficam), as 10 cadeiras oliva no jantar (a mesa por cima), as espreguiçadeiras A na prainha e as banquetas B na
  bancada gourmet; o piso por baixo das peças de antes refeito por `piso_saltando`.
- **Rótulos em dobro (corrigido):** o `rotulos_grade` parte dos desvios dos dados do `ANTES_COMMIT` (os do disco já vêm
  movidos de uma rodada anterior).
No 12K (`ampliacao_12k_terreo_casaa.montar12k` com `PAV` "Terreo_CasaB", chamado pelo `ampliacao_12k_terreo_casab`):
`pecas_12k` traz o que mudou na final (`REG_MASC`) da final ampliada sobre a saída do Topaz e, por cima, os chuveiros
nítidos na escala do 12K e o contorno das esquadrias redesenhado nela (`esquadrias_12k`, onde a final aceitou o perfil:
o canal 2 de `REG_MASC`); os shafts e as letras vão pelo `montar12k`.

  python3 regras_terreo_casab_1311.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final, os dados do 12K, o registro e os
antes e depois `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_<trecho>_antes_depois.jpg`.
"""

import argparse
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import biblioteca_subsolo_casab_1311 as BB       # noqa: E402
import regras_1211_casaa as RG                   # noqa: E402
import revisao_terreo_casab_1311 as RV           # noqa: E402
import paisagismo_terreo_casab_1311 as PJ        # noqa: E402

CASA_B = AQUI.parents[1] / "POE642_CasaB"
R = CASA_B / "renders"
FINAL = R / "POE642_CasaB_PH_Terreo_final_rotulos.png"
DADOS = R / "POE642_CasaB_PH_Terreo_12K_dados.json"
REG_JSON = R / "POE642_CasaB_PH_Terreo_12K_regras.json"
REG_MASC = R / "POE642_CasaB_PH_Terreo_12K_regras_zona.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "7ecb326"
PX_M = B1.PX_M

# as letras: a escada (o meio do triângulo dela nos dados do 12K, px) e a letra
LETRAS_TB = {"escadas": [((680.6, 643.6), "D"), ((1080.3, 833.0), "D"), ((608.0, 917.6), "D")], "folga_px": 2.5}
# os vãos dos shafts na final (px, x1/y1 exclusivos): o branco dentro das paredes
SHAFTS_TB = [(1564, 742, 1592, 771), (1563, 1252, 1591, 1278)]
# os chuveiros: a placa (o quadrado do PDF, px), o desenho, a face da parede (px) e o lado do braço (None: de teto), e o
# lado de onde vem o piso que cobre o de antes (dx, dy)
CH_Q, CH_R = "banho-1/chuveiro-quadrado-parede-planta", "banho-de-servico/chuveiro-redondo-parede-planta"
CH_T = "banho-master/chuveiro-quadrado-planta"
CHUVEIROS_TB = [
    {"nome": "banho master (esquerda)", "placa_px": (1278.7, 391.4, 1290.5, 403.2), "png": CH_T, "parede": None,
     "piso": (-1, 0)},
    {"nome": "banho master (direita)", "placa_px": (1505.6, 391.4, 1517.4, 403.2), "png": CH_T, "parede": None,
     "piso": (1, 0)},
    {"nome": "banho 1", "placa_px": (1903.6, 373.5, 1915.4, 385.3), "png": CH_Q, "parede": (1932, "dir"), "piso": (0, 1)},
    {"nome": "banho 2", "placa_px": (2675.0, 373.5, 2686.8, 385.3), "png": CH_Q, "parede": (2658, "esq"), "piso": (0, 1)},
    {"nome": "banho 3", "placa_px": (2768.4, 859.2, 2780.2, 871.0), "png": CH_Q, "parede": (842, "cima"), "piso": (-1, 0)},
    {"nome": "BH gourmet (esquerda)", "placa_px": (1125.6, 1630.4, 1137.4, 1642.2), "png": CH_Q, "parede": (1109, "esq"),
     "piso": (0, -1)},
    {"nome": "BH gourmet (direita)", "placa_px": (1509.5, 1630.4, 1521.3, 1642.2), "png": CH_Q, "parede": (1538, "dir"),
     "piso": (0, -1)},
    # no deck, o piso de cada linha (as tábuas são deitadas) vem das duas laterais da mesma linha, em degradê (copiado
    # de um lado só, o trecho aparecia como uma faixa de outro tom)
    {"nome": "ducha do deck", "placa_px": (854.6, 741.4, 866.4, 753.2), "png": CH_Q, "parede": (776, "baixo"),
     "piso": "linhas"},
    {"nome": "BH serviço", "placa_px": (1848.0, 1633.3, 1859.8, 1645.1), "png": CH_R, "parede": (1831, "esq"),
     "piso": (0, 1)},
    {"nome": "BH motorista", "placa_px": (2822.2, 1547.7, 2834.0, 1559.5), "png": CH_R, "parede": (1576, "baixo"),
     "piso": (-1, 0)},
]
LIMPA_PX = 3                 # em volta da placa e do braço de antes (a sombra deles)
PAREDES_TB = dict(BS.PAREDES_RETAS, fora_fundo=True)
ELEVADOR_TB = (1720, 515, 1825, 665)          # a caixa do elevador (px), fora das paredes retas
# (usuário, vendo a prévia: "FAÇA APENAS O CONTORNO DA ESQUADRIA EM PRETO") o traço fino (`traco_px`): só o contorno de
# cada folha, caixilho e vidro de box em preto, o vidro claro por dentro (com 1,1 px, os dois lados das folhas finas
# viravam uma barra preta)
ESQUADRIAS_TB = {"perfil": (34, 34, 36), "traco_px": 0.5, "ss": 8, "forca": 1.6, "croma_max": 16, "lum_min": 120,
                 "box_larg_px": 1.5, "box_comp_px": 40, "box_raio_px": 80, "chuveiro_folga_px": 3, "boxes_pretos": False}
_ESQ = {}                 # onde a final aceita o perfil (bool, px da final), para o 12K
# os tapetes das suítes (usuário: "NÃO VOU QUERER TROCAR AS CAMAS QUE EU JÁ COLOQUEI, MAS QUERO O RETOQUE EM VOLTA DO
# CONTORNO E NOS TAPETES"): o tapete do PDF (o índice do desenho) refeito inteiro com o da biblioteca no tom do de hoje
# (`png`), como nas suítes do 1º Pavimento da Casa A; as camas de 12/11, os bancos, o sofá e os criados por cima, pelo
# contorno do PDF de cada peça (`CAMADAS_TAP` e `extra`), com a sombra curta dos móveis (`biblioteca_terreo_casaa.
# SOMBRAS["movel"]`): o halo da IA em volta das camas sai. Na suíte master, a dobra do edredom do PDF passa da cama da
# IA (`fora_px`): ali entra o tapete.
TAPETES_TB = {"master": {"tapete": 35, "png": "suite-master/tapete", "extra": [63289],
                         "fora_px": [(1036, 702, 1048, 727), (1163, 702, 1169, 727)]},
              "suíte 1": {"tapete": 71886, "png": "sala-intima/tapete", "extra": []},
              "suíte 2": {"tapete": 71788, "png": "sala-intima/tapete", "extra": []},
              "suíte 3": {"tapete": 71904, "png": "sala-intima/tapete", "extra": []}}
CAMADAS_TAP = ("ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_LOUÇAS E METAIS", "ARQ_MOBILIÁRIO")
# as peças geradas no Higgsfield e escolhidas pelo usuário ("G2, R7, B1, C4"; `pecas_higgsfield_1311.py` as recorta na
# biblioteca): a geladeira inox nos 3 retângulos da cozinha (o PDF), a frente (os puxadores) para a ilha, à esquerda;
# os 2 recamiers de veludo na suíte master (o retângulo do PDF; a cabeceira curva em cima, o encosto do lado de fora,
# espelhados), o piso de antes refeito por baixo dos antigos com as réguas do vinílico (`reguas`) e as mesinhas de
# encaixe de volta por cima; o banco estofado capitonê no retângulo do banco do closet master; a cortina de linho em
# ondas nos 10 trechos do PDF (`ajustes_casab.trechos_cortina_b`), o trilho grafite do lado do vidro, de parede a parede
# (como o trilho de antes), sobre o piso refeito em espelho (as tábuas continuam).
BIB_TODA = AQUI.parent / "biblioteca-objetos"
GELADEIRAS_TB = {"png": "02-terreo/cozinha/geladeira-inox.png", "pdf": [63242, 63248, 63236]}
# os recamiers de antes passam do retângulo do PDF (o encosto e o braço): o de antes é o branco pouco colorido do bouclé
# (`velho_croma`, `velho_lum`) até `busca_px` do retângulo, ligado a ele, mais `folga_px` (a sombra); o piso por baixo,
# em cada linha (as tábuas são deitadas), em espelho a partir das duas beiradas do buraco
# (usuário: "CUIDADO COM A PROPORÇÃO DO RECAMIER E MESA LATERAL"; "PODEMOS USAR OUTRO MODELO DE RECAMIER QUE TENHA AS
# MESMAS DIMENSÕES DO ORIGINAL?"; "R11") o recamier gerado na medida do original (0,70 x 1,50 m, 2,16:1 contra os 2,14:1
# do PDF): entra no retângulo do PDF sem deformar; as mesinhas, no tamanho do PDF (`encurtar`, que tirava gomos do meio
# de um PNG mais comprido, fica para outros casos)
RECAMIERS_TB = {"png": "03-primeiro-pavimento/suite-master/recamier-veludo-champanhe.png", "encurtar": None,
                "pdf": [(63598, "esq"), (63651, "dir")], "mesas": [78368, 78353], "folga_px": 8, "busca_px": 14,
                "velho_croma": 45, "velho_lum": 105,
                # (13/11, revisão do 12K: "CORRIJA O PISO NESSA ÁREA DA SUÍTE") o espelho por linha deixava fantasmas (as
                # barras claras em cima, o risco entre os recamiers): o piso da área toda (fora as mesinhas e a poltrona
                # de couro) é refeito com as réguas do vinílico (`piso_reguas`)
                "zona_px": [(1024, 391, 1203, 452), (1024, 452, 1168, 500)], "tom_px": (1030, 505, 1200, 540)}
BANCO_CLOSET_TB = {"png": "03-primeiro-pavimento/closet-master/banco-estofado-capitone.png",
                   "px": (1340.0, 624.0, 1451.0, 670.0)}
CORTINAS_TB = {"png": "02-terreo/cortinas/cortina-linho-onda.png", "prof_px": 9.0, "vidro_px": 4.5,
               "limpa": (4.0, 5.5), "dentro_px": 3, "parede": 95, "seguidos": 3, "busca_px": 360, "junta_px": 16}
# o jardim de inverno (usuário: "NÃO HÁ A NECESSIDADE DE TANTOS X, FAÇA APENAS UM DE UMA DIAGONAL A OUTRA" e "AS FOLHAS
# DE BAIXO PRECISAM ESTAR EM CONTATO UMA COM A OUTRA"): os tracejados de antes saem (o branco pouco colorido sobre o
# gramado, fora o rótulo; o gramado refeito por inpaint) e entra um X só, de canto a canto do miolo (`miolo_px`), no
# tracejado branco de antes, interrompido em volta do rótulo (`rotulo_px`, com `folga_px`); as 3 folhas de vidro de
# baixo encostam uma na outra (os vãos `vaos_px` com o perfil da folha, o fio preto da junta no meio)
JARDIM_TB = {"miolo_px": (2041, 735, 2238, 935), "rotulo_px": (2078, 811, 2194, 841), "folga_px": 4,
             "tracejado_lum": 140, "tracejado_croma": 50, "cor": (232, 234, 230), "traco_px": 6.0, "vao_px": 3.5,
             "larg_px": 1.3, "recuo_px": 2.0, "ss": 8,
             "folhas_y": (934, 943), "vaos_px": [(2102, 2110), (2170, 2178)], "perfil_x": 2070}
# os rótulos das suítes (usuário: "ALINHE A SUITE 1 E 2 NA HORIZONTAL. E ALINHE A CIRCULAÇÃO E SUITE 3 NA HORIZONTAL.
# ALINE A SUITE 1 E CIRCULAÇÃO NA VERTICAL. ALINHE SUITE 2 E 3 NA VERTICAL"): o meio de cada um (px) numa grade: a
# linha das suítes 1 e 2 em y 560; a da circulação e da suíte 3 em y 695 (a circulação é estreita: a suíte 3 sobe);
# a coluna da suíte 1 e da circulação em x 2135; a das suítes 2 e 3 em x 2416 (a da suíte 3: mais à direita, ela
# cairia no tapete da cama). O rótulo de antes sai pela conta do alfa e o novo entra pelo mesmo desenho; o 12K lê os
# desvios novos nos dados.
ROTULOS_GRADE_TB = {"SUÍTE 1": (2135.0, 560.0), "SUÍTE 2": (2416.0, 560.0), "CIRCULAÇÃO": (2135.0, 695.0),
                    "SUÍTE 3": (2416.0, 695.0)}
_ZONA_FORA = {}           # os px que o 12K não traz da final (o texto dos rótulos novos, que o 12K desenha nítido)
# O mobiliário decidido (13/11, as 15 respostas, uma a uma; "A BANCADA DO BH. MOTORISTA É MARROM TABACO"; "FALTOU A
# CADEIRA DE ESCRITORIO NAS ESCRIVANINHAS"): as peças da Casa A no retângulo do PDF de cada uma, com as convenções de
# lá (`biblioteca_terreo_casaa_1211`, `biblioteca_1pav_casaa_1211`): o giro pela parede (0: a parede em cima, a
# torneira ou a caixa acoplada para ela; 180: embaixo; 90: à esquerda; -90: à direita), as medidas da Casa A onde o
# PNG não é o retângulo do PDF (a bacia Carrara 21,1 x 30,7; a Monte Carlo 22,5 x 32,7; as cubas Franke com a
# torneira além do retângulo, do lado da parede). (leitor, png, cx, cy, larg, alt, giro, sombra, extra); leitor: BT
# (02-terreo) ou B1 (03-primeiro-pavimento); alt None: na proporção do PNG.
MOBILIARIO_TB = {
    # os criados da Casa A no tom da madeira das bancadas, com o abajur visto de cima (o PDF manda: retangulares na
    # master, na suíte 2 e na 3; redondos na suíte 1)
    "criados": [("B1", "suite-master/criado-retangular-vista-superior", 1022.45, 743.8, 39.3, 25.8, 180.0, "movel",
                 "tom_bancada"),
                ("B1", "suite-master/criado-retangular-vista-superior", 1188.55, 743.8, 39.3, 25.8, 180.0, "movel",
                 "tom_bancada"),
                ("B1", "suite-3/criado-redondo", 1962.4, 519.2, 32.7, 32.7, 90.0, "movel", None),
                ("B1", "suite-3/criado-redondo", 1963.2, 363.45, 32.7, 32.7, 90.0, "movel", None),
                ("B1", "suite-1/criado-retangular-vista-superior", 2520.45, 440.9, 47.8, 29.9, -90.0, "movel",
                 "tom_bancada"),
                ("B1", "suite-1/criado-retangular-vista-superior", 2604.2, 815.85, 41.8, 29.9, 180.0, "movel",
                 "tom_bancada")],
    # banho master: a bancada dupla esculpida (as 2 cubas caem nas do PDF) e as bacias Carrara brancas
    "banho_master": [("B1", "banho-master/bancada-dupla-esculpida-render-v2", 1398.05, 346.55, 131.3, 35.9, 0.0,
                      "baixa", None),
                     ("B1", "banho-master/bacia-carrara", 1261.15, 474.95, 21.1, 30.7, 90.0, "baixa", None),
                     ("B1", "banho-master/bacia-carrara", 1534.95, 474.95, 21.1, 30.7, -90.0, "baixa", None)],
    # banhos 1, 2 e 3: a cuba esculpida de travertino na bancada inteira (a cuba no lugar da do PDF: ("cuba", c); no
    # `biblioteca_1pav_casaa_1211.cuba_na_bancada`, c conta da ponta direita do PNG: girado -90, a de baixo; 180, a da
    # esquerda) e a bacia Carrara branca
    "banhos": [("B1", "banho-1/cuba-esculpida-travertino", 1848.85, 495.85, 65.7, 35.9, 90.0, "baixa", ("cuba", 32.9)),
               ("B1", "banho-1/bacia-carrara", 1846.25, 436.1, 21.1, 30.7, 90.0, "baixa", None),
               ("B1", "banho-2/cuba-esculpida-travertino", 2741.5, 540.55, 143.3, 35.8, -90.0, "baixa",
                ("cuba", 58.2)),
               ("B1", "banho-2/bacia-carrara", 2744.1, 439.05, 21.1, 30.7, -90.0, "baixa", None),
               ("B1", "banho-3/cuba-esculpida-travertino", 2607.15, 913.8, 143.3, 35.8, 180.0, "baixa",
                ("cuba", 58.2)),
               ("B1", "banho-3/bacia-carrara", 2708.65, 916.35, 21.1, 30.7, 180.0, "baixa", None)],
    # lavabo: a cuba esculpida de poros na bancada e a bacia no marrom dos vasos (como o lavabo da Casa A)
    "lavabo": [("BT", "lavabo/cuba-esculpida-poros-render", 2267.6, 824.7, 57.0, 31.4, 90.0, "baixa", "lavabo"),
               ("BT", "lavabo/bacia-carrara", 2267.25, 767.45, 21.1, 30.7, 90.0, "baixa", "marrom")],
    # BH gourmet: as bacias marrons e, no lavatório, a cuba esculpida de travertino em cada bloco do PDF (mais estreita
    # que o PNG: os lados viram um aro fino e a cuba estreita um pouco, `cuba_estreita`)
    "bh_gourmet": [("BT", "lavabo/bacia-carrara", 1138.35, 1553.05, 21.1, 30.7, 0.0, "baixa", "marrom"),
                   ("BT", "lavabo/bacia-carrara", 1514.45, 1553.05, 21.1, 30.7, 0.0, "baixa", "marrom"),
                   ("B1", "banho-1/cuba-esculpida-travertino", 1294.15, 1625.3, 30.1, 32.0, 180.0, "baixa",
                    ("estreita", 0.164, 0.845, 0.06)),
                   ("B1", "banho-1/cuba-esculpida-travertino", 1354.85, 1625.3, 30.1, 32.0, 180.0, "baixa",
                    ("estreita", 0.164, 0.845, 0.06))],
    # BH serviço e BH motorista: só a louça da cuba (a bancada marrom tabaco fica) e a bacia Monte Carlo
    "bh_servico": [("B1", "banho-de-servico/cuba-servico-granito", 1850.05, 1531.8, 23.8, None, 90.0, None, "louca"),
                   ("BT", "banho-do-motorista/bacia-monte-carlo-sem-valvula", 1847.35, 1588.5, 22.5, 32.7, 90.0,
                    "baixa", None)],
    "bh_motorista": [("BT", "banho-do-motorista/cuba-compacta", 2935.6, 1557.4, 24.0, None, 180.0, None, "louca"),
                     ("BT", "banho-do-motorista/bacia-monte-carlo-sem-valvula", 2878.85, 1560.15, 22.5, 32.7, 180.0,
                      "baixa", None)],
    # cozinha: o cooktop de 4 bocas no meio do de 5 (o resto vira bancada, `BALCAO_TB`) e as cubas Franke da pia
    "cozinha": [("BT", "cozinha/cooktop-quatro-bocas", 1693.65, 1499.05, 31.0, 29.0, 90.0, None, None),
                ("BT", "area-de-servico/cuba-franke-inox-link", 1672.7, 1650.85, 38.2, 30.3, 180.0, None, None),
                ("BT", "area-de-servico/cuba-franke-inox-link", 1720.5, 1650.85, 38.2, 30.3, 180.0, None, None)],
    # gourmet: o cooktop de 4 bocas, a cuba Franke com misturador e a grelha da Casa A no meio da churrasqueira do PDF
    "gourmet": [("BT", "cozinha/cooktop-quatro-bocas", 1383.6, 1363.3, 31.0, 29.0, 0.0, None, None),
                ("BT", "area-gourmet/cuba-franke-misturador-unic", 1383.7, 1509.1, 43.0, 27.0, 180.0, None, None),
                ("BT", "area-gourmet/grelha-churrasqueira", 1501.95, 1508.0, 62.0, 32.0, 0.0, None, None)],
    # área de serviço: os tanques Franke (a torneira na parede da direita)
    "tanques": [("BT", "area-de-servico/cuba-franke-inox-link", 2219.1, 1492.95, 37.9, 35.4, -90.0, None, None),
                ("BT", "area-de-servico/cuba-franke-inox-link", 2219.1, 1532.45, 37.9, 35.4, -90.0, None, None)]}
# os abajures (centro e diâmetro, px), um em cada criado: 19 nos de ~0,70 m, 17 nos menores (como na Casa A)
ABAJURES_TB = [(1022.45, 743.8, 19.0), (1188.55, 743.8, 19.0), (1962.4, 519.2, 17.0), (1963.2, 363.45, 17.0),
               (2520.45, 440.9, 17.0), (2604.2, 815.85, 19.0)]
# os cooktops de 5 bocas que saem: o retângulo do PDF (com a `folga` do rebaixo claro em volta) vira bancada, cada
# metade com o granito logo do lado (ao longo da bancada: `eixo`), a emenda do meio e a borda em rampa de `rampa` px:
# (c, eixo, folga, rampa)
BALCAO_TB = [((1678.7, 1472.8, 1708.6, 1525.3), "y", 2, 3), ((1357.3, 1348.4, 1409.9, 1378.2), "x", 5, 3)]
# as cadeiras de escritório (a da Casa A, 34 px de largura) nas 3 escrivaninhas: ~1/3 da cadeira por baixo da mesa, o
# encosto para fora; a de antes sai (o piso refeito em espelho, `piso_espelho`) e a mesa volta por cima, com a sombra
# curta dela na cadeira. lado: onde a cadeira fica em relação à mesa
CADEIRAS_TB = {"png": "escritorio/cadeira-escritorio", "larg": 34.0, "sob": 1 / 3, "folga_px": 3,
               "itens": [{"nome": "suíte 1", "cadeira": 62273, "mesa": 71876, "lado": "cima"},
                         {"nome": "suíte 2", "cadeira": 62240, "mesa": 71855, "lado": "dir"},
                         {"nome": "suíte master", "cadeira": 63443, "mesa": 71925, "lado": "esq"}]}
# A 2ª etapa do mobiliário ("PODE FAZER A 2ª ETAPA"), a que refaz o piso por baixo das peças de antes:
# - a sala íntima com o conjunto da Casa A (`SALA_INTIMA_TB`): o tapete, o sofá em L A (o "anti_t" da Casa A: o corpo
#   comprido à direita, contra a parede, e a ponta em cima; 89% de sobreposição com o L do PDF), as mesas laterais
#   redondas nos 2 círculos do PDF e a poltrona A no símbolo do PDF (o encosto, a faixa fina do PDF, para o elevador; a
#   frente para a sala: 225°; 50 x 52 px). O PDF tem uma poltrona só (a proposta dizia 2); a mesa de centro redonda fica
#   (de volta por cima, pelo contorno do PDF). Depois ("PÕE UM BANCO ESTOFADO, COMO SE FOSSE UM PUFF NA FRENTE DA
#   POLTRONA"): o retângulo girado do PDF na frente da poltrona (0,62 x 0,43 m, o lado comprido de través à frente
#   dela: o pufe dela), que o render tinha feito de mesa de madeira, vira o pufe estofado da Casa A
#   (`suite-master/pufe`, 45°); a mesa de madeira sai, com o piso refeito. E ("TROQUE O TOM DA MESA DE CENTRO PARA UM
#   TOM QUENTE"): a mesa de centro no tom da madeira das bancadas (o dos criados), com o veio dela;
# - o jantar: só as 10 cadeiras oliva da Casa A (30 px) no lugar das bordô, no centro do retângulo de cada uma no PDF,
#   viradas para a mesa; a mesa e o aparador ficam (a mesa de volta por cima, com a sombra curta nas cadeiras);
# - a prainha: as 2 espreguiçadeiras A no retângulo do PDF, a cabeceira à direita (a parte menor do PDF);
# - a bancada gourmet: as 5 banquetas B da Casa A (25 px) no lugar das 5 de hoje (o PDF desenha 4, desiguais; a planta
#   tem 5 desde 12/11 e a proposta foi com 5), ~40% do assento por baixo da bancada (a borda em y 1319,3): o que passa
#   da borda não é desenhado (`corte_y`).
SALA_INTIMA_TB = {"tapete": 70337, "sofa": (77730, 77731, 77732, 77733, 77734, 77735), "mesa_centro": 77823, "pufe": 71935,
                  "pufe_png": "suite-master/pufe", "pufe_px": (36.8, 25.5), "pufe_giro": 45.0,
                  "mesa_centro_tom": B1.TOM_BANCADA,
                  "mesas_laterais": [77800, 77858], "poltrona": 62306, "poltrona_px": (50.0, 52.0), "poltrona_giro": 225.0,
                  "folga_px": 10, "folga_pufe_px": 10}
JANTAR_TB = {"mesa": 63685, "larg": 30.0, "folga_px": 7,
             "cadeiras": [(62447, 0.0), (62496, 0.0), (62545, 0.0), (62594, 0.0), (31098, 180.0), (31147, 180.0),
                          (31196, 180.0), (31245, 180.0), (62643, 90.0), (31294, -90.0)]}
# (13/11, "Gostei da E4") na prainha, dentro d'água, a espreguiçadeira de resina gerada no Higgsfield (E4: polietileno
# areia/greige, o encosto em placa reta; recortada em `02-terreo/deck-piscina/espreguicadeira-resina.png`, o encosto em
# cima como a A) no lugar da A de madeira: no comprimento do retângulo do PDF, a largura pela proporção do PNG (sem
# deformar), no meio dele, o encosto à direita
# (13/11, "Adicione os colchonetes ... e esse encosto de cabeça"; "os colchonetes não são de resina, é sobre a
# espreguiçadeira de material de resina") sobre a resina, o colchonete creme e o encosto de cabeça em rolo da
# espreguiçadeira A, com a costura na dobra do encosto e a sombra curta (`espreguicadeira-resina-colchonete.png`)
ESPREG_TB = {"png": "deck-piscina/espreguicadeira-resina-colchonete", "pdf": [62435, 62441], "giro": -90.0,
             "sem_deformar": True,
             "sombra": "baixa"}
BANQUETAS_TB = {"png": "area-gourmet/banqueta-b", "larg": 25.0, "borda_y": 1319.3,
                "xs": [1321.5, 1370.0, 1420.0, 1470.0, 1519.0], "velhas_px": (17, 1295)}
ANTES_DEPOIS = {"letras_escadas":(590, 600, 1180, 960), "shafts": (1540, 720, 1615, 1300),
                "tapetes_master": (995, 560, 1220, 790), "tapetes_suites": (1930, 330, 2650, 860),
                "esquadrias_banho_master": (1230, 300, 1560, 420), "esquadrias_jardim_inverno": (1880, 770, 2240, 960),
                "esquadrias_servico": (1540, 1440, 2260, 1700), "geladeiras": (1740, 1395, 1845, 1565),
                "recamiers_suite_master": (995, 380, 1225, 525), "banco_closet": (1320, 600, 1470, 690),
                "cortinas_fachada": (1550, 325, 2560, 375), "cortinas_master": (955, 380, 1000, 775),
                "jardim_inverno": (2025, 725, 2250, 955), "rotulos_suites": (2060, 520, 2520, 790),
                "chuveiros_banhos": (1250, 340, 2810, 900), "chuveiros_servico": (1095, 1520, 2880, 1680),
                "mob_banho_master": (1225, 315, 1565, 500), "mob_banho_1": (1815, 410, 1885, 540),
                "mob_banho_2": (2710, 415, 2775, 620), "mob_banho_3": (2525, 885, 2730, 945),
                "mob_lavabo": (2240, 745, 2295, 865), "mob_bh_gourmet": (1115, 1525, 1535, 1650),
                "mob_bh_servico": (1820, 1505, 1880, 1610), "mob_bh_motorista": (2855, 1530, 2960, 1585),
                "mob_cozinha": (1640, 1455, 1750, 1680), "mob_gourmet": (1340, 1335, 1545, 1535),
                "mob_tanques": (2190, 1465, 2245, 1560), "mob_criados_master": (990, 715, 1220, 770),
                "mob_criados_suites": (1935, 335, 2640, 845), "mob_escrivaninha_master": (1145, 375, 1245, 520),
                "mob_escrivaninha_s1": (2020, 535, 2180, 620), "mob_escrivaninha_s2": (2240, 350, 2315, 525),
                "mob_sala_intima": (1630, 345, 1830, 630), "mob_jantar": (1715, 1075, 1985, 1215),
                "mob_prainha": (915, 1135, 1060, 1285), "mob_banquetas": (1290, 1285, 1560, 1345)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            _Q["Q"] = F.Quadro("Terreo")
    return _Q["Q"]


_Q = {}


# ----------------------------------------------------------------------------------------------------------------------
def letras(img, q=LETRAS_TB, gravar=True):
    """O D sob a seta de cada escada (como `letras_escadas_casaa_1211.um_pav`), na final e nos dados do 12K."""
    import ampliacao_12k_terreo_casaa as Z
    import terreo_casaa_1011 as TA
    forma = img.shape[:2]
    d = json.loads(DADOS.read_text())
    d["anotacoes"] = [a for a in d["anotacoes"] if not (a[0] == "txt" and a[1][0] in (["S"], ["D"]))]
    tris = [np.float32(a[1]) for a in d["anotacoes"] if a[0] == "tri"]
    txts = [a for a in d["anotacoes"] if a[0] == "txt"]
    out = img.astype(np.float32)
    feitos = []
    for (cx, cy), L in q["escadas"]:
        t = min(tris, key=lambda p: float(np.hypot(*(p.mean(axis=0) - (cx, cy)))))
        cor = min(txts, key=lambda a: float(np.hypot(a[1][1] - cx, a[1][2] - cy)))[2]
        x = float(t[:, 0].min() + t[:, 0].max()) / 2
        topo = float(t[:, 1].max()) + q["folga_px"]
        dados = [[L], x, topo + 6.0, "centro"]
        a = Z.alfa_anotacao("txt", dados, forma)
        ys, xs = np.nonzero(a > 0.3)
        dados[2] += topo - ys.min()
        dados[1] += x - (xs.min() + xs.max()) / 2
        a = Z.alfa_anotacao("txt", dados, forma)
        out = TA.compor(out, a, tuple(cor))
        ys, xs = np.nonzero(a > 0.3)
        feitos.append(f"{L} em x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")
        d["anotacoes"].append(["txt", dados, list(cor)])
    print(f"    letras: {'; '.join(feitos)}")
    if gravar:
        DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def shafts(img, vaos=SHAFTS_TB):
    for v in vaos:
        img = RG.desenhar_x(img, v)
        img, n = RG.limpar_aro(img, v)
    print(f"    shafts: {len(vaos)} vãos no claro e o X em cinza fino")
    return img


def shafts_12k(final, out, s, ox, oy):
    for v in SHAFTS_TB:
        out = RG.desenhar_x(out, v, s, ox, oy)
        out, _ = RG.limpar_aro(out, v, s, ox, oy)
    return out


def chuveiro_desenho(ch):
    """(P, cx, cy, larg, alt, giro) do chuveiro na final (px)."""
    x0, y0, x1, y1 = ch["placa_px"]
    pc = ((x0 + x1) / 2, (y0 + y1) / 2)
    placa = ((x1 - x0) + (y1 - y0)) / 2
    if ch["parede"] is None:
        P = B1.ler_png(ch["png"])
        return P, pc[0], pc[1], placa, placa, 0.0
    return BB.chuveiro_pos(ch["png"], pc, ch["parede"], placa)


def piso_linhas(out, r):
    """O retângulo r (px) com o piso de cada linha das duas laterais dela (a mesma largura logo à esquerda e logo à
    direita), em degradê da esquerda para a direita."""
    x0, y0, x1, y1 = int(np.floor(r[0])), int(np.floor(r[1])), int(np.ceil(r[2])), int(np.ceil(r[3]))
    w = x1 - x0
    esq = out[y0:y1, x0 - w - 1:x0 - 1].astype(np.float32)
    dir_ = out[y0:y1, x1 + 1:x1 + w + 1].astype(np.float32)
    t = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    out[y0:y1, x0:x1] = np.clip(np.round(esq * (1 - t) + dir_ * t), 0, 255).astype(np.uint8)
    return out


def chuveiros(out, par, reg):
    for ch in CHUVEIROS_TB:
        x0, y0, x1, y1 = ch["placa_px"]
        a = [x0 - LIMPA_PX, y0 - LIMPA_PX, x1 + LIMPA_PX, y1 + LIMPA_PX]
        if ch["parede"] is not None:                    # o trecho de antes vai da placa até a face da parede
            face, lado = ch["parede"]
            if lado == "esq":
                a[0] = face
            elif lado == "dir":
                a[2] = face
            elif lado == "cima":
                a[1] = face
            else:
                a[3] = face
        if ch["piso"] == "linhas":
            out = piso_linhas(out, a)
        else:
            out = BB.piso_desloc(out, tuple(a), par, ch["piso"][0], ch["piso"][1], folga=0)
        P, cx, cy, wt, ht, ang = chuveiro_desenho(ch)
        o = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, ang, B1.SOMBRAS["chuveiro"], PX_M, nao=par)
        out = np.clip(np.round(o), 0, 255).astype(np.uint8)
        reg["pecas"].append({"tipo": "chuveiro_tb", "nome": ch["nome"]})
    print(f"    chuveiros: {len(CHUVEIROS_TB)} desenhados em planta (2 de teto, 6 quadrados e 2 redondos de parede)")
    return out


def paredes(Q, out, antes):
    q = PAREDES_TB
    protegido = ndimage.binary_dilation((out != antes).any(axis=2), iterations=2)
    im = out.astype(np.int16)
    cinza = (np.abs(im - q["cor"]).max(axis=2) <= q["tol"]) & ((im.max(axis=2) - im.min(axis=2)) <= q["croma"])
    folhas = (BS.quieto(FA.paredes_pdf, Q) > 0.3) & ~cinza
    protegido |= ndimage.binary_dilation(folhas, iterations=1) | RG.objetos_pdf(Q)
    x0, y0, x1, y1 = ELEVADOR_TB
    protegido[y0:y1, x0:x1] = True
    return BS.paredes_retas(Q, out, protegido, FA, q)


def _caixa(Q, d):
    pts = np.concatenate([np.asarray(c) for c in Q.caminhos(d)])
    return pts.min(0), pts.max(0)


def tapete(Q, out, q):
    """O tapete do PDF refeito com o da biblioteca no tom do de hoje; as peças sobre ele de volta, pelo contorno do PDF,
    com a sombra curta."""
    dt = Q.desenhos[q["tapete"]]
    (x0, y0), (x1, y1) = _caixa(Q, dt)
    objs = set()
    for i, d in enumerate(Q.desenhos):
        if i == q["tapete"] or d.get("type") != "f" or (d.get("layer") not in CAMADAS_TAP and i not in q["extra"]):
            continue
        if not Q.caminhos(d):
            continue
        (a0, b0), (a1, b1) = _caixa(Q, d)
        if a1 < x0 or a0 > x1 or b1 < y0 or b0 > y1 or (a1 - a0) < 3 or (b1 - b0) < 3:
            continue
        objs.add(id(d))
    alfa = Q.preencher(lambda d: id(d) in objs, ss=4, fs=True).astype(np.float32)
    rug = Q.preencher(lambda d: d is dt, ss=4, fs=True).astype(np.float32)
    X0, Y0, X1, Y1 = int(np.floor(x0)) - 6, int(np.floor(y0)) - 6, int(np.ceil(x1)) + 6, int(np.ceil(y1)) + 6
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    al = np.clip(alfa[Y0:Y1, X0:X1], 0, 1)
    for a0, b0, a1, b1 in q.get("fora_px", ()):
        al[b0 - Y0:b1 - Y0, a0 - X0:a1 - X0] = 0
    ru = np.clip(rug[Y0:Y1, X0:X1], 0, 1)
    livre = (ru > 0.99) & ~ndimage.binary_dilation(al > 0.01, iterations=8)
    tom = np.median(reg[livre], axis=0)
    P = B1.ler_png(q["png"])
    m = P[..., 3] > 250
    P[..., :3] = np.clip(P[..., :3] * (np.float32(tom) / np.median(P[..., :3][m], axis=0)), 0, 255)
    w, h = x1 - x0, y1 - y0
    if (P.shape[1] > P.shape[0]) != (w > h):
        P = np.ascontiguousarray(np.rot90(P))
    novo = BT.pousar(reg.copy(), P, (x0 + x1) / 2 - X0, (y0 + y1) / 2 - Y0, w, h, 0.0, BT.SOMBRAS["tapete"], PX_M)
    for sb in BT.SOMBRAS["movel"]:
        sh = cv2.GaussianBlur(al, (0, 0), max(0.3, sb["sig"] * PX_M))
        Ms = np.float32([[1, 0, sb["dx"] * PX_M], [0, 1, sb["dy"] * PX_M]])
        sh = cv2.warpAffine(sh, Ms, (sh.shape[1], sh.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        novo *= (1 - sb["forca"] * sh * (1 - al))[..., None]
    res = novo * (1 - al[..., None]) + reg * al[..., None]
    dentro = np.clip(cv2.dilate(ru, np.ones((3, 3), np.uint8)), 0, 1)[..., None]
    res = reg * (1 - dentro) + res * dentro
    out[Y0:Y1, X0:X1] = np.clip(np.round(res), 0, 255).astype(np.uint8)
    return out, tom


def tapetes(Q, out, q=TAPETES_TB):
    feitos = []
    for nome, t in q.items():
        out, tom = tapete(Q, out, t)
        feitos.append(f"{nome} (BGR {np.round(tom).astype(int)})")
    print(f"    tapetes refeitos inteiros, as camas por cima pelo contorno do PDF: {'; '.join(feitos)}")
    return out


def _tracos_esquadrias(Q, q=ESQUADRIAS_TB):
    """Os traços das esquadrias do PDF: os da ARQ_PAREDE e, nas louças, só os vidros dos boxes (longos e finos)."""
    for d in Q.desenhos:
        if d.get("layer") not in ("ARQ_PAREDE", "ARQ_LOUÇAS E METAIS") or d.get("type") != "s":
            continue
        cs = Q.caminhos(d)
        if not cs:
            continue
        pts = np.concatenate([np.asarray(c) for c in cs])
        w, h = pts.max(0) - pts.min(0)
        if d.get("layer") == "ARQ_LOUÇAS E METAIS":
            # (14/11, "ESSE É O ESTILO DE BOX DE CHUVEIRO ... PARA TODOS OS BANHEIROS. NADA DE ESQUADRIA PRETA") os
            # vidros dos boxes ficam no vidro claro com o fio cinza, sem o contorno preto
            if not q["boxes_pretos"]:
                continue
            if not (min(w, h) <= q["box_larg_px"] and max(w, h) >= q["box_comp_px"]):
                continue
            # só os vidros dos boxes: perto de um chuveiro (os traços longos das camas e dos recamiers, na mesma camada,
            # ficavam pretos)
            cx, cy = (pts.min(0) + pts.max(0)) / 2
            if not any(np.hypot(cx - (c["placa_px"][0] + c["placa_px"][2]) / 2, cy - (c["placa_px"][1] + c["placa_px"][3]) / 2)
                       <= q["box_raio_px"] for c in CHUVEIROS_TB):
                continue
        yield cs


def esquadrias(Q, out, q=ESQUADRIAS_TB):
    """O contorno das esquadrias do PDF em preto, só onde a final mostra o vidro ou o alumínio neutro (fora a parede e a
    borda dela; a madeira das portas de giro e o bronze dos brises, coloridos, ficam); fora os chuveiros desenhados."""
    H, W = out.shape[:2]
    ss = q["ss"]
    M = np.zeros((H * ss, W * ss), np.uint8)
    for cs in _tracos_esquadrias(Q, q):
        for c in cs:
            cv2.polylines(M, [np.int32(np.round(np.asarray(c) * ss))], False, 255,
                          max(1, int(round(q["traco_px"] * ss))), cv2.LINE_AA)
    al = cv2.resize(M.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    del M
    im = out.astype(np.int16)
    croma = im.max(axis=2) - im.min(axis=2)
    parede = (np.abs(im - 80).max(axis=2) <= 22) & (croma <= 12)
    neutro = (croma <= q["croma_max"]) & (im.mean(axis=2) >= q["lum_min"])
    ok = ndimage.binary_dilation(neutro & ~ndimage.binary_dilation(parede, iterations=1), iterations=1) & ~parede
    for ch in CHUVEIROS_TB:
        x0, y0, x1, y1 = [int(round(v)) for v in ch["placa_px"]]
        e = q["chuveiro_folga_px"]
        if ch["parede"] is not None:
            face, lado = ch["parede"]
            x0, x1 = (face, x1) if lado == "esq" else (x0, face) if lado == "dir" else (x0, x1)
            y0, y1 = (face, y1) if lado == "cima" else (y0, face) if lado == "baixo" else (y0, y1)
        ok[min(y0, y1) - e:max(y0, y1) + e, min(x0, x1) - e:max(x0, x1) + e] = False
    _ESQ["ok"] = ok
    al = np.clip(al * q["forca"], 0, 1) * ok
    novo = out.astype(np.float32) * (1 - al[..., None]) + np.float32(q["perfil"]) * al[..., None]
    print(f"    esquadrias: o contorno preto em {int((al > 0.3).sum())} px (os boxes, as portas de vidro e as janelas)")
    return np.clip(np.round(novo), 0, 255).astype(np.uint8)


def esquadrias_12k(out, s, X0, Ya3, ok, q=ESQUADRIAS_TB):
    """O mesmo contorno no 12K, desenhado na escala dele (nítido), onde a final aceitou o perfil (`ok`, ampliado)."""
    H, W = out.shape[:2]
    M = np.zeros((H, W), np.uint8)
    esp = max(1, int(round(q["traco_px"] * s)))
    for cs in _tracos_esquadrias(quadro(), q):
        for c in cs:
            pts = (np.asarray(c, np.float64) - [X0, Ya3]) * s * 4
            cv2.polylines(M, [np.int32(np.round(pts))], False, 255, esp, cv2.LINE_AA, shift=2)
    ok8 = ok.astype(np.uint8) * 255
    for y in range(0, H, 1024):
        y1 = min(H, y + 1024)
        Fq = np.array([[s, 0, -s * X0], [0, s, -s * Ya3 - y]], np.float64)
        okb = cv2.warpAffine(ok8, Fq, (W, y1 - y), flags=cv2.INTER_NEAREST, borderValue=0) > 127
        a = np.clip(M[y:y1].astype(np.float32) / 255 * q["forca"], 0, 1) * okb
        reg = out[y:y1].astype(np.float32)
        out[y:y1] = np.clip(np.round(reg * (1 - a[..., None]) + np.float32(q["perfil"]) * a[..., None]), 0, 255
                            ).astype(np.uint8)
    print("    esquadrias no 12K: o contorno preto nítido")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# As peças do Higgsfield
def ler_peca(rel):
    P = cv2.imread(str(BIB_TODA / rel), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def peca_desenho(it):
    """(P, cx, cy, larg, alt) de uma peça do registro, na final (px)."""
    if it["tipo"] == "cortina":
        return cortina_desenho(it)
    P = ler_peca(it["png"])
    if it.get("encurtar"):                               # as colunas [a, b) do PNG saem (os gomos do meio)
        a_, b_ = it["encurtar"]
        P = np.ascontiguousarray(np.concatenate([P[:, :a_], P[:, b_:]], axis=1))
    if it.get("rot"):
        P = np.ascontiguousarray(np.rot90(P, it["rot"]))
    if it.get("espelho"):
        P = np.ascontiguousarray(P[:, ::-1])
    x0, y0, x1, y1 = it["c"]
    return P, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0


def caixa_pdf(Q, i):
    (x0, y0), (x1, y1) = _caixa(Q, Q.desenhos[i])
    return float(x0), float(y0), float(x1), float(y1)


def reguas(Q, img, ponto):
    """As réguas do vinílico (BGR float32) do ambiente que tem `ponto` e o canto delas: as do `vinilico_foto.trocar`
    (a mesma conta, só para pegar as réguas)."""
    import um_pav_casaa_1111 as U
    import vinilico_foto as V
    pegas = []
    orig = U._reguas_amostra

    def espiao(h, w, px_m, qv, rng):
        T = orig(h, w, px_m, qv, rng)
        f = sys._getframe(1).f_locals
        pegas.append((T if f["deitado"] else np.ascontiguousarray(T.transpose(1, 0, 2)), f["x"], f["y"]))
        return T
    U._reguas_amostra = espiao
    try:
        BS.quieto(V.trocar, Q, img, [(124, 162, 200)])
    finally:
        U._reguas_amostra = orig
    for T, x, y in pegas:
        if x <= ponto[0] < x + T.shape[1] and y <= ponto[1] < y + T.shape[0]:
            return T, x, y
    raise RuntimeError("as réguas não foram achadas")


def piso_reguas(Q, out, buraco, sigmas=(4, 8, 16)):
    """O vinílico de volta no `buraco` (bool): as réguas vezes a luz do piso em volta (média normalizada)."""
    ys, xs = np.nonzero(buraco)
    T, ox, oy = reguas(Q, out, (int(xs.mean()), int(ys.mean())))
    h, w = T.shape[:2]
    reg = out[oy:oy + h, ox:ox + w].astype(np.float32)
    b = buraco[oy:oy + h, ox:ox + w]
    Lr = reg / np.maximum(T, 1)
    num, den = BS.nconv(Lr, ~b, 12.0)
    E = T * num / np.maximum(den, 1e-4)
    valido = ~b & (np.abs(reg - E).max(axis=2) <= 18)
    L = np.zeros_like(Lr)
    falta = b.copy()
    for sg in sigmas:
        num, den = BS.nconv(Lr, valido, sg)
        ok = falta & (den[..., 0] > 0.05)
        L[ok] = (num / np.maximum(den, 1e-6))[ok]
        falta &= ~ok
    reg[b] = (T * L)[b]
    out[oy:oy + h, ox:ox + w] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


def piso_espelho(out, buraco, larg_max=16, croma_min=40, nao_fonte=None):
    """Cada trecho do `buraco` em cada linha com o piso de madeira da mesma linha, refletido em vaivém dentro da faixa de
    piso logo ao lado (até `larg_max` px de madeira contígua: a cor da madeira, `croma_min`): a metade da esquerda vem
    da esquerda, a da direita, da direita; as tábuas deitadas continuam, sem emenda na beirada, e o reflexo não alcança
    a janela, a cortina ou os móveis em volta (`nao_fonte`: os px que não servem de fonte, como a escrivaninha, que
    também é madeira)."""
    res = out.copy()
    im = out.astype(np.int16)
    madeira = ((im.max(axis=2) - im.min(axis=2)) >= croma_min) & ~buraco
    if nao_fonte is not None:
        madeira &= ~nao_fonte
    W = out.shape[1]
    for y in np.unique(np.nonzero(buraco)[0]):
        xs = np.nonzero(buraco[y])[0]
        quebras = np.nonzero(np.diff(xs) > 1)[0]
        for a, b in zip(np.r_[xs[0], xs[quebras + 1]], np.r_[xs[quebras], xs[-1]] + 1):
            we = 0
            while we < larg_max and a - 1 - we >= 0 and madeira[y, a - 1 - we]:
                we += 1
            wd = 0
            while wd < larg_max and b + wd < W and madeira[y, b + wd]:
                wd += 1
            meio = (a + b) / 2 if we and wd else (b if we else a)
            for x in range(a, b):
                if x < meio and we:
                    k = (x - a) % (2 * we)
                    fx = a - 1 - (k if k < we else 2 * we - 1 - k)
                elif wd:
                    k = (b - 1 - x) % (2 * wd)
                    fx = b + (k if k < wd else 2 * wd - 1 - k)
                else:
                    continue
                res[y, x] = out[y, fx]
    return res


def pousar_peca(out, it, sombras, par):
    P, cx, cy, wt, ht = peca_desenho(it)
    o = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, 0.0, sombras, PX_M, nao=par)
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def recorte_de_volta(Q, out, antes, ids, reg_pecas, sombra=True):
    """As peças `ids` do PDF de volta da imagem `antes`, pelo contorno do PDF (com a sombra curta delas)."""
    alvo = {id(Q.desenhos[i]) for i in ids}
    al = np.clip(Q.preencher(lambda d: id(d) in alvo, ss=4, fs=True).astype(np.float32), 0, 1)
    ys, xs = np.nonzero(al > 0.01)
    x0, y0, x1, y1 = xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7
    a = al[y0:y1, x0:x1]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    if sombra:
        for sb in BT.SOMBRAS["mesa"]:
            sh = cv2.GaussianBlur(a, (0, 0), max(0.3, sb["sig"] * PX_M))
            Ms = np.float32([[1, 0, sb["dx"] * PX_M], [0, 1, sb["dy"] * PX_M]])
            sh = cv2.warpAffine(sh, Ms, (sh.shape[1], sh.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
            reg *= (1 - sb["forca"] * sh * (1 - a))[..., None]
    reg = reg * (1 - a[..., None]) + antes[y0:y1, x0:x1].astype(np.float32) * a[..., None]
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    reg_pecas.append({"tipo": "recorte", "c": [int(x0), int(y0), int(x1), int(y1)]})
    cv2.imwrite(str(R / f"POE642_CasaB_PH_Terreo_12K_regras_recorte_{x0}_{y0}.png"),
                np.dstack([out[y0:y1, x0:x1], np.clip(np.round(a * 255), 0, 255).astype(np.uint8)]))
    return out


def trilhos(img, q=CORTINAS_TB):
    """Os 10 trechos de cortina do PDF com o trilho de parede a parede: (o, vidro, ex, t0, t1), como o motor de antes
    (`ajustes_casab.cortinas_b`: a linha logo dentro do ambiente até o 1º px da parede)."""
    import ajustes_casab as AB
    Q = quadro()
    with contextlib.redirect_stdout(io.StringIO()):
        with F.em_quadro(Q):
            trechos = AB.trechos_cortina_b(Q.chave)
    par = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") and max(d["fill"]) < 0.6, ss=2) > 0.3
    res = []
    for o, vidro, ex, e0, e1 in trechos:
        im = img if o == "v" else img.transpose(1, 0, 2)
        pq = par if o == "v" else par.T
        v = vidro if o == "v" else {"cima": "esquerda", "baixo": "direita"}[vidro]
        dentro = int(round(ex)) + (q["dentro_px"] if v == "esquerda" else -q["dentro_px"])
        escuro = im[:, dentro].astype(np.float32).mean(axis=1) < q["parede"]

        def ate(y, passo):
            n = 0
            for yy in range(int(round(y)), int(round(y)) + passo * q["busca_px"], passo):
                if pq[yy, dentro]:
                    return yy - passo * 0.5
                n = n + 1 if escuro[yy] else 0
                if n >= q["seguidos"]:
                    return yy - passo * (q["seguidos"] - 1) - passo * 0.5
            return y
        res.append([o, v, float(ex), ate((e0 + e1) / 2, -1), ate((e0 + e1) / 2, 1)])
    def sem_parede(o, v, ex, a_, b_):
        # (13/11) um vão curto entre dois trechos sem parede no meio (os restos escuros da cortina de antes paravam a
        # busca e partiam a cortina da suíte 2): unidos
        pq = par if o == "v" else par.T
        dentro = int(round(ex)) + (q["dentro_px"] if v == "esquerda" else -q["dentro_px"])
        return not pq[int(np.floor(a_)):int(np.ceil(b_)) + 1, dentro].any()
    unidos = []
    for o, v, ex, t0, t1 in sorted(res, key=lambda t: (t[0], t[1], round(t[2]), t[3])):
        if unidos and unidos[-1][:2] == [o, v] and abs(unidos[-1][2] - ex) < 3 \
                and (t0 < unidos[-1][4] - 2 or (t0 - unidos[-1][4] <= q["junta_px"]
                                                and sem_parede(o, v, ex, unidos[-1][4], t0))) \
                and t1 > unidos[-1][3] + 2:
            unidos[-1][3], unidos[-1][4] = min(unidos[-1][3], t0), max(unidos[-1][4], t1)
        else:
            unidos.append([o, v, ex, t0, t1])
    return [tuple(u) for u in unidos]


def cortina_desenho(it, q=CORTINAS_TB):
    """A cortina de um trecho: o PNG (o trilho em cima) repetido no comprimento, na profundidade `prof_px`, girado com o
    trilho do lado do vidro; (P, cx, cy, larg, alt) na final."""
    P = ler_peca(q["png"])
    o, v, ex, t0, t1 = it["o"], it["v"], it["ex"], it["t0"], it["t1"]
    comp, prof = t1 - t0, q["prof_px"]
    k = prof / P.shape[0]
    larg_png = comp / k
    rep = int(np.ceil(larg_png / P.shape[1]))
    T = np.concatenate([P] * rep, axis=1)[:, :int(round(larg_png))] if rep > 1 else P[:, :int(round(larg_png))]
    T = np.ascontiguousarray(T)
    # na vertical (o, "v"): o trilho (em cima no PNG) vai para o lado do vidro
    c0 = ex - q["vidro_px"] if v == "esquerda" else ex + q["vidro_px"] - prof
    if o == "v":
        T = np.ascontiguousarray(np.rot90(T, 1 if v == "esquerda" else -1))
        return T, c0 + prof / 2, (t0 + t1) / 2, prof, comp
    # na horizontal (a imagem transposta: "esquerda" = o vidro em cima)
    if v == "direita":
        T = np.ascontiguousarray(T[::-1])
    return T, (t0 + t1) / 2, c0 + prof / 2, comp, prof


def cortinas(out, par, reg, q=CORTINAS_TB):
    feitos = 0
    for o, v, ex, t0, t1 in trilhos(out, q):
        # o pano e o trilho de antes saem: o piso logo do lado de dentro, em espelho (as tábuas continuam)
        a0 = ex - q["limpa"][0] if v == "esquerda" else ex - q["limpa"][1]
        a1 = ex + q["limpa"][1] if v == "esquerda" else ex + q["limpa"][0]
        im = out if o == "v" else out.transpose(1, 0, 2)
        A0, A1 = int(np.floor(a0)), int(np.ceil(a1))
        T0, T1 = int(np.floor(t0)), int(np.ceil(t1))
        n = A1 - A0
        if v == "esquerda":                       # o vidro à esquerda: o piso vem da direita, espelhado
            fonte = im[T0:T1, A1:A1 + n][:, ::-1].copy()
        else:
            fonte = im[T0:T1, A0 - n:A0][:, ::-1].copy()
        im[T0:T1, A0:A1] = fonte
        it = {"tipo": "cortina", "o": o, "v": v, "ex": ex, "t0": t0, "t1": t1}
        P, cx, cy, wt, ht = cortina_desenho(it, q)
        o_ = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, 0.0, BT.SOMBRAS["movel"][1:], PX_M)
        out = np.clip(np.round(o_), 0, 255).astype(np.uint8)
        reg["pecas"].append(it)
        feitos += 1
    print(f"    cortinas: {feitos} trilhos (os trechos do PDF que se sobrepõem unidos) com a cortina de linho em ondas "
          "(o trilho grafite do lado do vidro)")
    return out


def pecas_higgsfield(Q, out, antes, par, reg):
    # a geladeira: a frente (embaixo no PNG) para a esquerda
    for i in GELADEIRAS_TB["pdf"]:
        it = {"tipo": "png", "png": GELADEIRAS_TB["png"], "rot": -1, "c": list(caixa_pdf(Q, i)), "sombra": "movel"}
        out = pousar_peca(out, it, BT.SOMBRAS["movel"], par)
        reg["pecas"].append(it)
    print(f"    geladeiras: {len(GELADEIRAS_TB['pdf'])} em inox, a frente para a ilha")
    # o banco do closet master
    it = {"tipo": "png", "png": BANCO_CLOSET_TB["png"], "c": list(BANCO_CLOSET_TB["px"]), "sombra": "movel"}
    out = pousar_peca(out, it, BT.SOMBRAS["movel"], par)
    reg["pecas"].append(it)
    print("    closet master: o banco estofado capitonê")
    # os recamiers: o piso por baixo dos antigos (fora as mesinhas), os novos e as mesinhas de volta por cima
    q = RECAMIERS_TB
    alvo = {id(Q.desenhos[i]) for i, _ in q["pdf"]}
    pdf = Q.preencher(lambda d: id(d) in alvo, ss=2, fs=True) > 0.05
    alvo_m = {id(Q.desenhos[i]) for i in q["mesas"]}
    mesas = Q.preencher(lambda d: id(d) in alvo_m, ss=2, fs=True) > 0.05
    im = out.astype(np.int16)
    branco = ((im.max(axis=2) - im.min(axis=2)) < q["velho_croma"]) & (im.mean(axis=2) > q["velho_lum"])
    perto = cv2.dilate(pdf.astype(np.uint8), np.ones((2 * q["busca_px"] + 1,) * 2, np.uint8)) > 0
    n, lab = cv2.connectedComponents((branco & perto).astype(np.uint8), connectivity=8)
    toca = np.unique(lab[pdf & branco])
    velho = np.isin(lab, toca[toca > 0]) | pdf
    k = 2 * q["folga_px"] + 1
    buraco = (cv2.dilate(velho.astype(np.uint8), np.ones((k, k), np.uint8)) > 0) & ~par & ~mesas
    for x0, y0, x1, y1 in q["zona_px"]:
        buraco[y0:y1, x0:x1] = True
    buraco &= ~par & ~mesas
    out = piso_reguas(Q, out, buraco, sigmas=(4, 8, 16, 32, 64, 128))
    # a luz das réguas novas no tom do piso logo abaixo (o armário claro da direita clareava a estimativa)
    x0_, y0_, x1_, y1_ = q["tom_px"]
    alvo = np.median(out[y0_:y1_, x0_:x1_].reshape(-1, 3).astype(np.float32), axis=0)
    o = out.astype(np.float32)
    bf = buraco.astype(np.float32)
    num = cv2.GaussianBlur(o * bf[..., None], (0, 0), 25)
    den = cv2.GaussianBlur(bf, (0, 0), 25)[..., None]
    loc = num / np.maximum(den, 1e-4)
    o[buraco] = (o * alvo[None, None] / np.maximum(loc, 1))[buraco]
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    for i, lado in q["pdf"]:
        # o PNG: a cabeceira à esquerda e o encosto em cima; girado, a cabeceira em cima e o encosto à direita
        it = {"tipo": "png", "png": q["png"], "encurtar": list(q["encurtar"]) if q["encurtar"] else None, "rot": -1,
              "espelho": lado == "esq",
              "c": list(caixa_pdf(Q, i)), "sombra": "movel"}
        out = pousar_peca(out, it, BT.SOMBRAS["movel"], par)
        reg["pecas"].append(it)
    out = recorte_de_volta(Q, out, antes, q["mesas"], reg["pecas"])
    print("    suíte master: os 2 recamiers de veludo (espelhados), as mesinhas de encaixe de volta por cima")
    out = cortinas(out, par, reg)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# O mobiliário decidido
def cuba_estreita(P, alvo, miolo, aro):
    """A cuba esculpida mais estreita que o PNG (`alvo` = larg / alt, menor que a do PNG): os lados lisos viram um aro de
    `aro` da largura nova e o miolo (a cuba e a torneira, `miolo`: as frações da largura do PNG) estreita o que falta."""
    h, w = P.shape[:2]
    W = alvo * h
    a, b = int(round(w * miolo[0])), int(round(w * miolo[1]))
    la = max(1, int(round(aro * W)))
    lm = max(1, int(round(W - 2 * la)))
    partes = [cv2.resize(P[:, :a], (la, h), interpolation=cv2.INTER_AREA),
              cv2.resize(P[:, a:b], (lm, h), interpolation=cv2.INTER_AREA),
              cv2.resize(P[:, b:], (la, h), interpolation=cv2.INTER_AREA)]
    return np.ascontiguousarray(np.concatenate(partes, axis=1))


def preparar_bib(it):
    """(P, larg, alt) de uma peça da biblioteca do registro ({"leitor", "png", "larg", "alt", "extra"})."""
    leitor = {"BT": BT, "B1": B1}[it["leitor"]]
    extra = it.get("extra")
    extra = tuple(extra) if isinstance(extra, list) else extra
    wt, ht = it["larg"], it["alt"]
    estreita = isinstance(extra, tuple) and extra[0] == "estreita"
    if estreita or (extra == "louca" and leitor is B1):
        P = leitor.ler_png(it["png"])
        P = cuba_estreita(P, wt / ht, extra[1:3], extra[3]) if estreita else BT.so_louca(P)
        if ht is None:
            ht = wt * P.shape[0] / P.shape[1]
        return P, float(wt), float(ht)
    P, wt, ht = leitor.preparar(it["png"], wt, ht, extra)
    if it.get("corte_y") is not None and it.get("giro", 0.0) == 0.0:
        # a banqueta por baixo da bancada: as linhas do PNG além da borda (y >= corte_y) não aparecem (também no 12K)
        P = P.copy()
        H = P.shape[0]
        f = (it["corte_y"] - (it["cy"] - ht / 2)) / ht * H
        r = np.arange(H, dtype=np.float32) + 0.5
        P[..., 3] *= np.clip(f - r + 0.5, 0, 1)[:, None]
    return P, wt, ht


def pousar_bib(out, it, par):
    P, wt, ht = preparar_bib(it)
    o = BT.pousar(out.astype(np.float32), P, it["cx"], it["cy"], wt, ht, it["giro"], BT.SOMBRAS[it["sombra"]], PX_M,
                  nao=par)
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def item_bib(leitor, png, cx, cy, wt, ht, ang, sombra, extra):
    return {"tipo": "bib", "leitor": leitor, "png": png, "cx": cx, "cy": cy, "larg": wt, "alt": ht, "giro": ang,
            "sombra": sombra, "extra": list(extra) if isinstance(extra, tuple) else extra}


def balcao(out, par, q=BALCAO_TB):
    """Cada metade do cooktop de 5 bocas que sai com o granito logo do lado, deslocado ao longo da bancada (as linhas
    dela continuam), a emenda do meio e a borda em rampa; sem costura de tom (com os pontos do granito, ela manchava)."""
    for c, eixo, folga, rampa in q:
        X0, Y0 = int(np.floor(c[0])) - folga, int(np.floor(c[1])) - folga
        X1, Y1 = int(np.ceil(c[2])) + folga, int(np.ceil(c[3])) + folga
        if eixo == "x":
            meio = (X0 + X1) / 2
            d = int(np.ceil(meio + rampa - X0)) + 2
            A, B = out[Y0:Y1, X0 - d:X1 - d], out[Y0:Y1, X0 + d:X1 + d]
            t_ = np.clip((np.arange(X0, X1) + 0.5 - (meio - rampa)) / (2 * rampa), 0, 1)[None, :, None]
        else:
            meio = (Y0 + Y1) / 2
            d = int(np.ceil(meio + rampa - Y0)) + 2
            A, B = out[Y0 - d:Y1 - d, X0:X1], out[Y0 + d:Y1 + d, X0:X1]
            t_ = np.clip((np.arange(Y0, Y1) + 0.5 - (meio - rampa)) / (2 * rampa), 0, 1)[:, None, None]
        F = A.astype(np.float32) * (1 - t_) + B.astype(np.float32) * t_
        h, w = Y1 - Y0, X1 - X0
        dist = np.minimum.outer(np.minimum(np.arange(h) + 0.5, h - np.arange(h) - 0.5),
                                np.minimum(np.arange(w) + 0.5, w - np.arange(w) - 0.5))
        m = np.clip(dist / 2.0, 0, 1)[..., None] * ~par[Y0:Y1, X0:X1, None]
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - m) + F * m), 0, 255).astype(np.uint8)
    return out


def _alfa_peca(P, cx, cy, wt, ht, ang, forma):
    Pb = P.copy()
    Pb[..., :3] = 255
    return BT.pousar(np.zeros(forma + (3,), np.float32), Pb, cx, cy, wt, ht, ang, [], PX_M)[..., 0] / 255


def mesa_sobre(out, fonte, a, ca, s=1.0):
    """A mesa (alfa `a`) de `fonte` por cima, com a sombra curta dela (`BT.SOMBRAS["mesa"]`) só na cadeira (alfa `ca`)."""
    o = out.astype(np.float32)
    for sb in BT.SOMBRAS["mesa"]:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, sb["sig"] * PX_M * s))
        Ms = np.float32([[1, 0, sb["dx"] * PX_M * s], [0, 1, sb["dy"] * PX_M * s]])
        sh = cv2.warpAffine(sh, Ms, (sh.shape[1], sh.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        o *= (1 - sb["forca"] * sh * (1 - a) * ca)[..., None]
    o = o * (1 - a[..., None]) + fonte.astype(np.float32) * a[..., None]
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def cadeiras(Q, out, par, reg, q=CADEIRAS_TB):
    feitas = []
    for c in q["itens"]:
        it = item_bib("BT", q["png"], 0.0, 0.0, q["larg"], None, 0.0, "movel", None)
        P, wt, ht = preparar_bib(it)
        x0, y0, x1, y1 = caixa_pdf(Q, c["cadeira"])
        mx0, my0, mx1, my1 = caixa_pdf(Q, c["mesa"])
        d, f = ht, q["sob"]
        if c["lado"] == "cima":
            cx, cy, ang = (x0 + x1) / 2, my0 + d * f - d / 2, 0.0
        elif c["lado"] == "dir":
            cx, cy, ang = mx1 - d * f + d / 2, (y0 + y1) / 2, -90.0
        else:
            cx, cy, ang = mx0 + d * f - d / 2, (y0 + y1) / 2, 90.0
        it.update(cx=float(cx), cy=float(cy), alt=float(ht), giro=ang)
        alvo = id(Q.desenhos[c["mesa"]])
        a = np.clip(Q.preencher(lambda dd: id(dd) == alvo, ss=4, fs=True), 0, 1)
        mesa = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        # a cadeira de antes: o retângulo do PDF dela, com a folga da sombra, fora a mesa e as paredes
        fo = q["folga_px"]
        buraco = np.zeros(par.shape, bool)
        buraco[int(np.floor(y0)) - fo:int(np.ceil(y1)) + fo, int(np.floor(x0)) - fo:int(np.ceil(x1)) + fo] = True
        buraco &= ~mesa & ~par
        out = piso_espelho(out, buraco, nao_fonte=mesa)
        fonte = out.copy()
        out = pousar_bib(out, it, par)
        reg["pecas"].append(it)
        ca = _alfa_peca(P, cx, cy, wt, ht, ang, par.shape)
        # a mesa de volta por cima, no trecho em que a cadeira (e a sombra dela) a alcança
        mud = np.abs(out.astype(np.int16) - fonte.astype(np.int16)).max(axis=2) > 0
        ys, xs = np.nonzero(mud)
        X0, Y0, X1, Y1 = xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5
        out[Y0:Y1, X0:X1] = mesa_sobre(out[Y0:Y1, X0:X1], fonte[Y0:Y1, X0:X1], a[Y0:Y1, X0:X1], ca[Y0:Y1, X0:X1])
        cv2.imwrite(str(R / f"POE642_CasaB_PH_Terreo_12K_regras_mesa_{X0}_{Y0}.png"),
                    np.dstack([np.round(a[Y0:Y1, X0:X1] * 255), np.round(ca[Y0:Y1, X0:X1] * 255),
                               np.zeros((Y1 - Y0, X1 - X0))]).astype(np.uint8))
        reg["topo"].append({"tipo": "mesa_topo", "c": [int(X0), int(Y0), int(X1), int(Y1)]})
        feitas.append(c["nome"])
    print(f"    cadeiras de escritório: {', '.join(feitas)} (1/3 por baixo da escrivaninha, a de antes saiu)")
    return out


def mascara_pdf(Q, ids, limiar=0.05):
    alvo = {id(Q.desenhos[i]) for i in ids}
    a = np.clip(Q.preencher(lambda d: id(d) in alvo, ss=4, fs=True), 0, 1)
    return a, a > limiar


def dilatar(m, r):
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)) > 0


def piso_saltando(out, buraco, fonte, larg=16, alcance=60, eixo="x", ancorar=False):
    """Como o `piso_espelho`, linha a linha (ou coluna a coluna, `eixo` "y"), mas a fonte (`fonte`, bool) não precisa
    estar colada: em cada lado, os `larg` px de fonte mais perto, pulando o que não é fonte (uma mesa, um pufe) até
    `alcance` px; a metade de cada lado vem do seu lado, em vaivém. `ancorar`: o vaivém conta das bordas do buraco
    inteiro, não das de cada trecho (num buraco de beira inclinada, as emendas das tábuas copiadas saíam em degrau,
    acompanhando a beira; ancoradas, ficam em pé, como as das tábuas)."""
    if eixo == "y":
        res = piso_saltando(np.ascontiguousarray(out.transpose(1, 0, 2)), buraco.T, fonte.T, larg, alcance, "x",
                            ancorar)
        return np.ascontiguousarray(res.transpose(1, 0, 2))
    res = out.copy()
    fonte = fonte & ~buraco
    W = out.shape[1]
    cols = np.nonzero(buraco.any(axis=0))[0]
    XA, XB = int(cols.min()), int(cols.max()) + 1
    for y in np.unique(np.nonzero(buraco)[0]):
        xs = np.nonzero(buraco[y])[0]
        quebras = np.nonzero(np.diff(xs) > 1)[0]
        for a, b in zip(np.r_[xs[0], xs[quebras + 1]], np.r_[xs[quebras], xs[-1]] + 1):
            E = [x for x in range(a - 1, max(a - 1 - alcance, -1), -1) if fonte[y, x]][:larg]
            D = [x for x in range(b, min(b + alcance, W)) if fonte[y, x]][:larg]
            # um lado com 1 ou 2 px de fonte (a beira escura junto a uma parede) não serve: vem tudo do outro
            E, D = (E if len(E) >= 4 else []), (D if len(D) >= 4 else [])
            meio = (a + b) / 2 if E and D else (b if E else a)
            ia, ib = (XA, XB) if ancorar else (a, b)
            for x in range(a, b):
                if x < meio and E:
                    k = (x - ia) % (2 * len(E))
                    fx = E[k if k < len(E) else 2 * len(E) - 1 - k]
                elif D:
                    k = (ib - 1 - x) % (2 * len(D))
                    fx = D[k if k < len(D) else 2 * len(D) - 1 - k]
                else:
                    continue
                res[y, x] = out[y, fx]
    return res


def tom_do_entorno(antes, feito, buraco, fonte, sigma=10.0, anel_px=12):
    """O piso refeito (`feito`, no `buraco`) no tom do piso em volta: a média local do anel de fonte em volta do buraco
    (em `antes`), estendida para dentro, menos a média local do que entrou; as tábuas e os veios ficam, só a luz muda
    (a fonte de longe, perto da janela, é mais clara)."""
    anel = dilatar(buraco, anel_px) & ~buraco & fonte
    ref = antes.astype(np.float32)
    o = feito.astype(np.float32)
    num, den = BS.nconv(ref, anel.astype(np.float32), sigma)
    T = num / np.maximum(den, 1e-6)
    num2, den2 = BS.nconv(o, buraco.astype(np.float32), sigma)
    C = num2 / np.maximum(den2, 1e-6)
    o[buraco] += (T - C)[buraco]
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def mesa_por_cima(out, fonte, a, ca, reg):
    """A mesa (alfa `a`) de `fonte` de volta por cima do que mudou em volta dela (as cadeiras e a sombra delas), com a
    sombra curta dela nas cadeiras (alfa `ca`); no 12K, a da saída do Topaz (`topo_12k`)."""
    mud = np.abs(out.astype(np.int16) - fonte.astype(np.int16)).max(axis=2) > 0
    ys, xs = np.nonzero(mud)
    X0, Y0, X1, Y1 = xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5
    out[Y0:Y1, X0:X1] = mesa_sobre(out[Y0:Y1, X0:X1], fonte[Y0:Y1, X0:X1], a[Y0:Y1, X0:X1], ca[Y0:Y1, X0:X1])
    cv2.imwrite(str(R / f"POE642_CasaB_PH_Terreo_12K_regras_mesa_{X0}_{Y0}.png"),
                np.dstack([np.round(a[Y0:Y1, X0:X1] * 255), np.round(ca[Y0:Y1, X0:X1] * 255),
                           np.zeros((Y1 - Y0, X1 - X0))]).astype(np.uint8))
    reg["topo"].append({"tipo": "mesa_topo", "c": [int(X0), int(Y0), int(X1), int(Y1)]})
    return out


def sala_intima(Q, out, par, reg, q=SALA_INTIMA_TB):
    antes = out.copy()
    forma = par.shape
    _, pol = mascara_pdf(Q, [q["poltrona"]])
    _, redondo = mascara_pdf(Q, [q["mesas_laterais"][1]])
    _, quad = mascara_pdf(Q, [q["pufe"]])
    _, tap = mascara_pdf(Q, [q["tapete"]])
    # o piso por baixo da poltrona, do pufe redondo e da mesa quadrada de antes: as tábuas deitadas, linha a linha
    # (a folga leva junto a sombra delas, para baixo e para a esquerda)
    buraco = (dilatar(pol, q["folga_px"]) | dilatar(redondo, q["folga_pufe_px"]) | dilatar(quad, q["folga_pufe_px"])) \
        & ~par
    im = out.astype(np.int16)
    madeira = (im.max(axis=2) - im.min(axis=2)) >= 40
    fonte = madeira & ~dilatar(tap, 2) & ~dilatar(par, 3)        # (3: a beira escura junto às paredes não serve)
    out = tom_do_entorno(antes, piso_saltando(out, buraco, fonte, alcance=70, ancorar=True), buraco, fonte)
    pecas = []
    x0, y0, x1, y1 = caixa_pdf(Q, q["tapete"])
    pecas.append(("B1", "sala-intima/tapete", (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, 90.0, "tapete", None))
    xs0, ys0, xs1, ys1 = [f(v) for f, v in zip((min, min, max, max),
                                                zip(*[caixa_pdf(Q, i) for i in q["sofa"]]))]
    pecas.append(("B1", "sala-intima/sofa-l-a", (xs0 + xs1) / 2, (ys0 + ys1) / 2, xs1 - xs0, ys1 - ys0, 0.0, "movel",
                  "anti_t"))
    for p in pecas:
        it = item_bib(*p)
        out = pousar_bib(out, it, par)
        reg["pecas"].append(it)
    # ("TROQUE O TOM DA MESA DE CENTRO PARA UM TOM QUENTE") a mesa de centro no tom quente da madeira das bancadas (o
    # dos criados, `B1.TOM_BANCADA`): cada px vezes o tom novo sobre a mediana do tampo de antes (o veio e a borda
    # escura ficam, no tom novo)
    _, mc = mascara_pdf(Q, [q["mesa_centro"]])
    tampo = cv2.erode(mc.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    med = np.median(antes[tampo].reshape(-1, 3).astype(np.float32), axis=0)
    fonte_mc = antes.astype(np.float32)
    fonte_mc[dilatar(mc, 1)] *= np.float32(q["mesa_centro_tom"]) / np.maximum(med, 1)
    fonte_mc = np.clip(np.round(fonte_mc), 0, 255).astype(np.uint8)
    out = recorte_de_volta(Q, out, fonte_mc, [q["mesa_centro"]], reg["pecas"])
    for i in q["mesas_laterais"]:
        x0, y0, x1, y1 = caixa_pdf(Q, i)
        D = ((x1 - x0) + (y1 - y0)) / 2
        it = item_bib("B1", "sala-intima/mesa-lateral", (x0 + x1) / 2, (y0 + y1) / 2, D, D, 0.0, "baixa", None)
        out = pousar_bib(out, it, par)
        reg["pecas"].append(it)
    ys, xs = np.nonzero(pol)
    w, h = q["poltrona_px"]
    it = item_bib("B1", "sala-intima/poltrona-a", float(xs.mean()), float(ys.mean()), w, h, q["poltrona_giro"], "movel",
                  None)
    out = pousar_bib(out, it, par)
    reg["pecas"].append(it)
    ys, xs = np.nonzero(quad)
    w, h = q["pufe_px"]
    it = item_bib("B1", q["pufe_png"], float(xs.mean()), float(ys.mean()), w, h, q["pufe_giro"], "movel", None)
    out = pousar_bib(out, it, par)
    reg["pecas"].append(it)
    print("    sala íntima: o tapete, o sofá em L A, as 2 mesas laterais, a poltrona A e o pufe estofado na frente dela "
          "(a mesa de centro fica)")
    return out


def jantar(Q, out, par, reg, q=JANTAR_TB):
    a, mesa = mascara_pdf(Q, [q["mesa"]])
    buraco = np.zeros(par.shape, bool)
    for i, _ in q["cadeiras"]:
        x0, y0, x1, y1 = caixa_pdf(Q, i)
        f = q["folga_px"]
        buraco[int(np.floor(y0)) - f:int(np.ceil(y1)) + f, int(np.floor(x0)) - f:int(np.ceil(x1)) + f] = True
    buraco &= ~dilatar(mesa, 1) & ~par
    im = out.astype(np.int16)
    claro = (im.mean(axis=2) > 150) & ((im.max(axis=2) - im.min(axis=2)) < 45)
    fonte = claro & ~dilatar(mesa, 2) & ~par
    # o travertino tem os veios em pé: em cima e embaixo, coluna a coluna; nas pontas, linha a linha
    lados = np.zeros(par.shape, bool)
    for i, g in q["cadeiras"]:
        if g in (90.0, -90.0):
            x0, y0, x1, y1 = caixa_pdf(Q, i)
            lados[int(y0) - 8:int(y1) + 9, int(x0) - 8:int(x1) + 9] = True
    out = piso_saltando(out, buraco & ~lados, fonte, alcance=30, eixo="y")
    out = piso_saltando(out, buraco & lados, fonte, alcance=30, eixo="x")
    fonte_mesa = out.copy()
    ca = np.zeros(par.shape, np.float32)
    for i, g in q["cadeiras"]:
        x0, y0, x1, y1 = caixa_pdf(Q, i)
        it = item_bib("BT", "sala-de-jantar/cadeira-jantar-oliva-render", (x0 + x1) / 2, (y0 + y1) / 2, q["larg"], None,
                      g, "movel", None)
        P, wt, ht = preparar_bib(it)
        it["alt"] = float(ht)
        out = pousar_bib(out, it, par)
        reg["pecas"].append(it)
        ca = np.maximum(ca, _alfa_peca(P, it["cx"], it["cy"], wt, ht, g, par.shape))
    out = mesa_por_cima(out, fonte_mesa, a, ca, reg)
    print(f"    jantar: as {len(q['cadeiras'])} cadeiras oliva da Casa A no lugar das bordô (a mesa de volta por cima)")
    return out


def _passo_grade(img, x0, y0, x1, y1, lmin=5, lmax=20):
    """O passo (px, fracionário) da grade dos azulejos na vertical: o pico da autocorrelação da luz das linhas."""
    g = img[y0:y1, x0:x1].astype(np.float32).mean(axis=2).mean(axis=1)
    g = g - np.convolve(g, np.ones(7) / 7, mode="same")
    g = g[3:-3]
    ac = np.array([np.dot(g[:-k], g[k:]) / (len(g) - k) for k in range(lmin, min(lmax, len(g) - 4) + 1)])
    i = int(np.argmax(ac))
    if 0 < i < len(ac) - 1:                              # o pico com a parábola nos vizinhos
        d = 0.5 * (ac[i - 1] - ac[i + 1]) / (ac[i - 1] - 2 * ac[i] + ac[i + 1])
    else:
        d = 0.0
    return lmin + i + d


def espreguicadeiras_prainha(Q, out, par, reg, q=ESPREG_TB):
    for i in q["pdf"]:
        x0, y0, x1, y1 = caixa_pdf(Q, i)
        larg = y1 - y0
        if q.get("sem_deformar"):                         # o comprimento do PDF; a largura pela proporção do PNG
            P = BT.ler_png(q["png"])
            larg = (x1 - x0) * P.shape[1] / P.shape[0]
            # a peça é mais estreita que o retângulo do PDF: a água volta por baixo dele (o que sobra nas bordas),
            # cada linha copiada da água logo acima (metade de cima) ou logo abaixo (de baixo) no passo da grade dos
            # azulejos (`passo`, pela autocorrelação na vertical), as juntas contínuas
            X0, Y0, X1, Y1 = int(np.floor(x0)) - 2, int(np.floor(y0)) - 2, int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 2
            p = _passo_grade(out, X0, Y0 - 34, X1, Y0 - 4)
            novo = out.copy()
            meio = (Y0 + Y1) / 2
            for y in range(Y0, Y1):
                if y < meio:
                    src = y - int(np.ceil((y - Y0 + 1) / p)) * p
                else:
                    src = y + int(np.ceil((Y1 - y) / p)) * p
                novo[y, X0:X1] = out[int(round(src)), X0:X1]
            m = np.zeros(out.shape[:2], bool)
            m[Y0:Y1, X0:X1] = True
            m &= ~par
            out[m] = novo[m]
        it = item_bib("BT", q["png"], (x0 + x1) / 2, (y0 + y1) / 2, larg, x1 - x0, q["giro"],
                      q.get("sombra"), None)
        out = pousar_bib(out, it, par)
        reg["pecas"].append(it)
    print(f"    prainha: as 2 espreguiçadeiras ({Path(q['png']).stem}), o encosto à direita")
    return out


def banquetas(out, par, reg, q=BANQUETAS_TB):
    meia, ytopo = q["velhas_px"]
    yb = int(np.floor(q["borda_y"]))
    buraco = np.zeros(par.shape, bool)
    for x in q["xs"]:
        buraco[ytopo:yb, int(x - meia):int(x + meia) + 1] = True
    buraco &= ~par
    im = out.astype(np.int16)
    fonte = (im.mean(axis=2) > 150) & ~par
    out = piso_saltando(out, buraco, fonte, alcance=30)
    for x in q["xs"]:
        it = item_bib("BT", q["png"], x, q["borda_y"] - 2.0, q["larg"], None, 0.0, "movel", None)
        it["corte_y"] = q["borda_y"]
        P, wt, ht = preparar_bib(it)
        it["alt"] = float(ht)
        out = pousar_bib(out, it, par)
        reg["pecas"].append(it)
    print(f"    gourmet: as {len(q['xs'])} banquetas B da Casa A, ~40% por baixo da bancada")
    return out


def mobiliario(Q, out, par, reg, q=MOBILIARIO_TB):
    antes = out.copy()
    out = balcao(out, par)
    n = 0
    for amb, pecas in q.items():
        for p in pecas:
            it = item_bib(*p)
            out = pousar_bib(out, it, par)
            reg["pecas"].append(it)
            n += 1
    for cx, cy, D in ABAJURES_TB:
        out = B1.abajur(out, cx, cy, D)
        reg["topo"].append({"tipo": "abajur", "cx": cx, "cy": cy, "d": D})
    out = cadeiras(Q, out, par, reg)
    # a 2ª etapa
    out = sala_intima(Q, out, par, reg)
    out = jantar(Q, out, par, reg)
    out = espreguicadeiras_prainha(Q, out, par, reg)
    out = banquetas(out, par, reg)
    if "ok" in _ESQ:                 # no 12K, o contorno das esquadrias não passa por cima das peças novas
        mud = np.abs(out.astype(np.int16) - antes.astype(np.int16)).max(axis=2) > 2
        _ESQ["ok"] &= ~mud
    print(f"    mobiliário: {n} peças da Casa A ({', '.join(q)}), {len(ABAJURES_TB)} abajures; os cooktops de 5 bocas "
          "viraram bancada")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# O jardim de inverno e os rótulos das suítes
def x_jardim(img, s=1.0, ox=0.0, oy=0.0, q=JARDIM_TB):
    """O X tracejado de canto a canto do miolo do jardim, interrompido em volta do rótulo, na escala `s`."""
    x0, y0, x1, y1 = [float(v) for v in q["miolo_px"]]
    r = q["recuo_px"]
    a0, b0, a1, b1 = (x0 + r - ox) * s, (y0 + r - oy) * s, (x1 - r - ox) * s, (y1 - r - oy) * s
    A0, B0, A1, B1 = int(np.floor(a0)) - 2, int(np.floor(b0)) - 2, int(np.ceil(a1)) + 2, int(np.ceil(b1)) + 2
    ss = q["ss"]
    M = np.zeros(((B1 - B0) * ss, (A1 - A0) * ss), np.uint8)
    rx0, ry0, rx1, ry1 = q["rotulo_px"]
    f = q["folga_px"]
    traco, passo = q["traco_px"] * s, (q["traco_px"] + q["vao_px"]) * s
    for (ax, ay), (bx, by) in (((a0, b0), (a1, b1)), ((a1, b0), (a0, b1))):
        L = np.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        t = 0.0
        while t < L:
            t1 = min(t + traco, L)
            mx, my = ax + ux * (t + t1) / 2, ay + uy * (t + t1) / 2
            fx, fy = mx / s + ox, my / s + oy                 # o meio do traço, em px da final
            if not (rx0 - f <= fx <= rx1 + f and ry0 - f <= fy <= ry1 + f):
                p0 = ((ax + ux * t - A0) * ss, (ay + uy * t - B0) * ss)
                p1 = ((ax + ux * t1 - A0) * ss, (ay + uy * t1 - B0) * ss)
                cv2.line(M, tuple(int(round(v)) for v in p0), tuple(int(round(v)) for v in p1), 255,
                         max(1, int(round(q["larg_px"] * s * ss))), cv2.LINE_AA)
            t += passo
    al = cv2.resize(M.astype(np.float32) / 255, (A1 - A0, B1 - B0), interpolation=cv2.INTER_AREA)[..., None]
    reg = img[B0:B1, A0:A1].astype(np.float32)
    img[B0:B1, A0:A1] = np.clip(np.round(reg * (1 - al) + np.float32(q["cor"]) * al), 0, 255).astype(np.uint8)
    return img


def _alfa_rotulo_nome(nome, forma):
    import ampliacao_12k_terreo_casab as ZB
    with contextlib.redirect_stdout(io.StringIO()):
        Qr = ZB.quadro()
        ZB._usar_rotulos_b(Qr)
    b = next(r for r in json.loads(DADOS.read_text())["rotulos"] if r["nome"] == nome)
    return ZB.Z.alfa_rotulo(Qr, b, forma)


def jardim_inverno(out, q=JARDIM_TB):
    x0, y0, x1, y1 = q["miolo_px"]
    reg = out[y0:y1, x0:x1].astype(np.int16)
    trac = ((reg.max(axis=2) - reg.min(axis=2)) < q["tracejado_croma"]) & (reg.mean(axis=2) > q["tracejado_lum"])
    texto = _alfa_rotulo_nome("JARDIM DE INVERNO", out.shape[:2]) > 0.02
    texto = cv2.dilate(texto.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    trac &= ~texto[y0:y1, x0:x1]
    trac[q["folhas_y"][0] - y0:, :] = False              # as folhas de baixo ficam
    m = cv2.dilate(trac.astype(np.uint8), np.ones((3, 3), np.uint8))
    M = np.zeros(out.shape[:2], np.uint8)
    M[y0:y1, x0:x1] = m
    X0, Y0, X1, Y1 = x0 - 6, y0 - 6, x1 + 6, y1 + 6
    sub = cv2.inpaint(np.ascontiguousarray(out[Y0:Y1, X0:X1]), M[Y0:Y1, X0:X1] * 255, 3, cv2.INPAINT_TELEA)
    out[Y0:Y1, X0:X1][M[Y0:Y1, X0:X1] > 0] = sub[M[Y0:Y1, X0:X1] > 0]
    out = x_jardim(out, q=q)
    _ZONA_FORA["jardim"] = cv2.dilate((_alfa_rotulo_nome("JARDIM DE INVERNO", out.shape[:2]) > 0.03).astype(np.uint8),
                                      np.ones((3, 3), np.uint8)) > 0
    # as folhas de baixo: o perfil de uma folha (a coluna do meio dela) nos vãos, e o fio preto da junta
    fy0, fy1 = q["folhas_y"]
    col = out[fy0:fy1, q["perfil_x"]].copy()
    for a, b in q["vaos_px"]:
        out[fy0:fy1, a:b] = col[:, None]
        meio = (a + b) // 2
        lin = out[fy0:fy1, meio].astype(np.int16)
        borda = lin.mean(axis=1) < 200                 # só na altura do vidro e do perfil (o gramado em volta fica)
        out[fy0:fy1, meio][borda] = ESQUADRIAS_TB["perfil"]
        if "ok" in _ESQ:                                # o 12K traz as folhas da final (o contorno do PDF tinha os vãos)
            _ESQ["ok"][fy0 - 2:fy1 + 2, a - 8:b + 8] = False
    print(f"    jardim de inverno: um X só, de canto a canto ({int(m.sum())} px do tracejado de antes refeitos), e as 3 "
          "folhas de baixo encostadas")
    return out


def rotulos_grade(out, q=ROTULOS_GRADE_TB, gravar=True):
    import ampliacao_12k_terreo_casab as ZB
    import ampliacao_a3_casaa as AM
    import terreo_casaa_1011 as TA
    Z = ZB.Z
    with contextlib.redirect_stdout(io.StringIO()):
        Qr = ZB.quadro()
        ZB._usar_rotulos_b(Qr)
    forma = out.shape[:2]
    d = json.loads(DADOS.read_text())
    # (13/11) o desvio de partida é o dos dados do `ANTES_COMMIT` (o da final de partida): os do disco já vêm movidos
    # de uma rodada anterior, e o rótulo antigo, procurado no lugar novo, ficava na final (os 4 saíram em dobro)
    rel = DADOS.relative_to(RAIZ_GIT)
    base = json.loads(subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"],
                                     capture_output=True, check=True).stdout)
    base = {(b["nome"], tuple(np.round(b["pdf"], 3))): b["desvio"] for b in base["rotulos"] if b["nome"] in q}
    novos = []
    for b in d["rotulos"]:
        if b["nome"] not in q:
            continue
        b["desvio"] = list(base[(b["nome"], tuple(np.round(b["pdf"], 3)))])
        a = Z.alfa_rotulo(Qr, b, forma)
        out = np.ascontiguousarray(AM.tirar(out, [(a, tuple(b["cor"]))], 0.85))
        ys, xs = np.nonzero(a > 0.3)
        cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
        alvo = q[b["nome"]]
        b["desvio"] = [b["desvio"][0] + alvo[0] - cx, b["desvio"][1] + alvo[1] - cy]
        novos.append(b)
    fora = np.zeros(forma, bool)
    o = out.astype(np.float32)
    feitos = []
    for b in novos:
        a = Z.alfa_rotulo(Qr, b, forma)
        o = TA.compor(o, a, tuple(b["cor"]))
        fora |= cv2.dilate((a > 0.03).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ys, xs = np.nonzero(a > 0.3)
        feitos.append(f"{b['nome']} ({(xs.min() + xs.max()) / 2:.1f}, {(ys.min() + ys.max()) / 2:.1f})")
    _ZONA_FORA["rotulos"] = fora
    print(f"    rótulos em grade: {'; '.join(feitos)}")
    if gravar:
        DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
        rj = R / "POE642_CasaB_PH_Terreo_rotulos_1211.json"
        if rj.exists():
            lista = json.loads(rj.read_text())
            por_nome = {(b["nome"], tuple(np.round(b["pdf"], 3))): b for b in novos}
            for b in lista:
                k = (b["nome"], tuple(np.round(b["pdf"], 3)))
                if k in por_nome:
                    b["desvio"] = por_nome[k]["desvio"]
            rj.write_text(json.dumps(lista, ensure_ascii=False) + "\n")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes, gravar_dados=True):
    Q = quadro()
    out = antes.copy()
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    reg = {"pecas": [], "topo": []}
    out = letras(out, gravar=gravar_dados)
    out = shafts(out)
    out = chuveiros(out, par, reg)
    out = paredes(Q, out, antes)
    out = tapetes(Q, out)
    out = esquadrias(Q, out)
    out = pecas_higgsfield(Q, out, antes, par, reg)
    out = mobiliario(Q, out, par, reg)
    out = RV.aplicar(sys.modules[__name__], Q, out, par, reg)       # a revisão do 12K (13/11)
    out = PJ.aplicar(out, reg)                                      # o paisagismo (13/11: oliveiras, outras plantas)
    out = jardim_inverno(out)
    out = rotulos_grade(out, gravar=gravar_dados)
    return out, reg, par


def peca_12k(it):
    if it["tipo"].startswith("rv_"):                # a revisão do 12K (`revisao_terreo_casab_1311`)
        return RV.peca_12k(it)
    if it["tipo"] == "chuveiro_tb":
        ch = next(c for c in CHUVEIROS_TB if c["nome"] == it["nome"])
        P, cx, cy, wt, ht, ang = chuveiro_desenho(ch)
        return P, cx, cy, wt, ht, ang, []
    if it["tipo"] in ("png", "cortina"):
        P, cx, cy, wt, ht = peca_desenho(it)
        return P, cx, cy, wt, ht, 0.0, []
    if it["tipo"] == "bib":                          # o mobiliário da Casa A
        P, wt, ht = preparar_bib(it)
        return P, it["cx"], it["cy"], wt, ht, it["giro"], []
    if it["tipo"] == "recorte":                      # as mesinhas da suíte master, da final, por cima dos recamiers
        x0, y0, x1, y1 = it["c"]
        P = cv2.imread(str(R / f"POE642_CasaB_PH_Terreo_12K_regras_recorte_{x0}_{y0}.png"),
                       cv2.IMREAD_UNCHANGED).astype(np.float32)
        return P, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, []
    return None


def pecas_12k(final, out, s, X0, Ya3):
    """No 12K do Térreo da Casa B (`ampliacao_12k_terreo_casaa.montar12k`, antes dos tracejados e dos textos)."""
    base = out.copy()                                  # a saída do Topaz: as escrivaninhas nítidas, por cima das cadeiras
    out = BB.pecas_12k(final, out, s, X0, Ya3, reg_json=REG_JSON, reg_masc=REG_MASC, peca=peca_12k)
    out = topo_12k(out, base, s, X0, Ya3)
    out = RV.copias_12k(out, base, s, X0, Ya3, REG_JSON)  # a cama da suíte 3: a da suíte 1 da saída do Topaz, girada
    out = PJ.pecas_12k(out, base, s, X0, Ya3, REG_JSON)    # o paisagismo: o chão da saída do Topaz, as plantas nítidas
    if REG_MASC.exists():
        ok = cv2.imread(str(REG_MASC))[..., 2] > 127
        if ok.any():
            out = esquadrias_12k(out, s, X0, Ya3, ok)
    out = x_jardim(out, s, X0, Ya3)                    # o X do jardim de inverno, nítido na escala do 12K
    return out


def topo_12k(out, base, s, X0, Ya3):
    """Os abajures (desenhados na escala do 12K) e as escrivaninhas por cima das cadeiras novas: a da saída do Topaz,
    pelo alfa do PDF ampliado, com a sombra curta na cadeira."""
    if not REG_JSON.exists():
        return out
    H, W = out.shape[:2]
    for it in json.loads(REG_JSON.read_text()).get("topo", []):
        if it["tipo"] == "abajur":
            out = B1.abajur(out, it["cx"], it["cy"], it["d"], s, X0, Ya3)
            continue
        x0, y0, x1, y1 = it["c"]
        m = cv2.imread(str(R / f"POE642_CasaB_PH_Terreo_12K_regras_mesa_{x0}_{y0}.png")).astype(np.float32) / 255
        U0, V0 = max(int(np.floor((x0 - X0) * s)), 0), max(int(np.floor((y0 - Ya3) * s)), 0)
        U1, V1 = min(int(np.ceil((x1 - X0) * s)), W), min(int(np.ceil((y1 - Ya3) * s)), H)
        Mw = np.array([[1 / s, 0, U0 / s + X0 - x0], [0, 1 / s, V0 / s + Ya3 - y0]], np.float64)
        al = cv2.warpAffine(m, Mw, (U1 - U0, V1 - V0), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                            borderValue=0)
        out[V0:V1, U0:U1] = mesa_sobre(out[V0:V1, U0:U1], base[V0:V1, U0:U1], np.clip(al[..., 0], 0, 1),
                                       np.clip(al[..., 1], 0, 1), s)
    return out


def salvar_registro(antes, depois, reg, par):
    zona = cv2.dilate((np.abs(antes.astype(np.int16) - depois.astype(np.int16)).max(axis=2) > 2).astype(np.uint8),
                      np.ones((5, 5), np.uint8)).astype(bool)
    for m_ in _ZONA_FORA.values():                       # o texto dos rótulos novos: o 12K o desenha nítido
        zona &= ~m_
    m = np.zeros(antes.shape, np.uint8)
    m[..., 0] = zona * 255
    m[..., 1] = par * 255
    if "ok" in _ESQ:
        m[..., 2] = _ESQ["ok"] * 255                 # onde o contorno das esquadrias entra (para o 12K)
    cv2.imwrite(str(REG_MASC), m)
    REG_JSON.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n")
    print(f"    {REG_JSON.name}: {len(reg['pecas'])} peças; zona {int(zona.sum())} px")


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(4.0, 1600 / max(a.shape[1], 1), 900 / max(a.shape[0], 1))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        junto = np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b]) if a.shape[1] > a.shape[0] * 1.6 \
            else np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS" if junto.shape[1] > 2 * a.shape[1] else "ANTES (em cima) | DEPOIS (embaixo)",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaB_PH_Terreo_1311_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes", type=Path)
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    if a.antes:
        antes = cv2.imread(str(a.antes))
    else:
        rel = FINAL.relative_to(RAIZ_GIT)
        dado = subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"], capture_output=True,
                              check=True).stdout
        antes = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    depois, reg, par = aplicar(antes, gravar_dados=not a.saida)
    cv2.imwrite(str(a.saida or FINAL), depois)
    print(f"    {a.saida or FINAL}")
    if not a.saida:
        salvar_registro(antes, depois, reg, par)
        antes_depois(antes, depois)


if __name__ == "__main__":
    main()

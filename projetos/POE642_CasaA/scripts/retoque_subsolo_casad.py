#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Subsolo da Casa D (POE 642).

O render (Nano Banana Pro, 2000 x 1116) saiu fiel no layout, mas aproximou a planta (~2,73 x a
base reduzida a 2000 px). Os retoques são feitos no quadro do render, como no Térreo; no fim, a
imagem vai para o quadro comum das bases (a mesma folha e o mesmo enquadramento do Térreo), para
a planta do Subsolo cair exatamente sob a do Térreo.

Itens (o mapa está em POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_v1_erros.jpg):
1. Depósito: a faixa areia que o motor pôs junto à parede da esquerda (um armário que não existe no
   PDF) vira o granito do piso.
2. Depósito: as juntas de placas gigantes (~1,9 m) e as quatro manchas claras do granito saem; o piso
   fica contínuo, como no DCE 1 e no WC DCE (pedido do usuário).
3. WC DCE: o piso da área do chuveiro (acima da divisória) saiu mais claro e acinzentado; volta ao tom
   do granito do resto do banheiro (ganho por canal, a textura do render fica).
4. WC DCE: o símbolo do CAD (quadrado, braço e o toco na parede) vira o chuveiro do Térreo: ducha
   quadrada (a placa aprovada da Casa A), braço cromado até a parede da esquerda e canopla, na
   geometria do PDF.
5. DCE 1: o armário até o teto (o da linha diagonal) saiu quase branco; vira a madeira areia dos
   armários até o teto do Térreo, com o veio no comprido, sem a diagonal e sem sombra. A mancha
   clara do piso junto ao criado-mudo sai, como as do depósito.
6. Sauna: o braço do banco em L que o motor subiu junto ao vidro sai; ali volta o piso de Bege Bahia.
7. Sauna: o banco, que o motor fez em madeira, fica no mármore Bege Bahia (pedido do usuário), o
   mesmo do piso, com o veio: os dois níveis do PDF (degrau da frente e assento junto à parede, layer
   ARQ_ELEMENTOS FIXOS) se leem pela sombra curta de cada borda no nível de baixo e por um brilho
   leve na quina, sem linhas escuras.
8. Ducha da antessala: o símbolo do CAD (quadrado, braço e a cruz branca sobre a parede) vira o
   chuveiro, com o braço saindo da parede de baixo; a parede volta ao preto.
9. Box do vestiário: o mesmo, com o braço saindo da parede da direita; o toco da cruz que passou
   para o vinílico da academia sai.
10. Vestiário: a cuba da bancada saiu só com o contorno cinza; vira uma cuba branca de verdade (aba,
    bacia com a borda mais escura indo ao fundo claro, válvula cromada), com a torneira cromada
    saindo da faixa junto à parede, na geometria do PDF (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS).
11. Esteiras: os letreiros que o motor escreveu nas lonas saem (sem texto na planta); fica a lona.
13. Arcos das portas sobre o granito (pedido do usuário): como no Térreo, ficam em cinza e traço
    fino; aqui o arco preto do render (~1,5 px) sai antes (granito tecido) e o cinza vem do PDF.
14. Escada (pedido do usuário): só sombreamento que denota a descida, sem linhas nem tracejados. O
    Bege Bahia é refeito sem a linha de caminhamento, o círculo, a marca de corte, o tracejado e as
    linhas dos degraus; os pisos (16, de 27,1 px, do PDF) escurecem para baixo (a escada sobe da
    esquerda, do pátio, para a direita) e cada espelho joga uma sombra curta no piso de baixo, à
    esquerda dele: os degraus se leem só pelo tom.
16. Sanitários (pedido do usuário: mais bem representados): os vasos do WC DCE e do WC do vestiário,
    chapados e com o contorno do CAD no render, são desenhados em 8 x no contorno exato do PDF, com
    o tampo fechado (pedido do usuário): louça com volume (bordas um pouco mais escuras), contorno
    fino e sombra curta no piso; o tampo cobre a bacia da linha da dobradiça do PDF à frente, recuado
    da borda, com volume, contorno e sombra leve sobre a louça.
17. Portas de vidro de acesso à academia (pedido do usuário: mais finas): as quatro folhas de correr
    (dois trilhos), que o render fez como cápsulas cinza de ~10 px, são refeitas na espessura do PDF
    (3,4 px): vidro claro com a linha central fina, montantes de alumínio nas pontas e contorno fino;
    o vão (a faixa branca entre as folhas e o vinílico) vira soleira de Bege Bahia, como o pátio.
18. Vidro da sauna e janela alta da academia (pedido do usuário: finos como as portas): as barras
    grossas do render saem; o vidro fixo é refeito na espessura do PDF (vidro claro, linha central,
    caixilhos de alumínio nas pontas e contorno fino), o peitoril e a soleira em Bege Bahia, os
    retornos da parede em preto e as faces da parede em traço fino e claro, como no PDF; na janela, a
    faixa de vinílico que a barra cobria volta.
19. Entrada do elevador (pedido do usuário): as duas folhas da porta, recolhidas no poço, que o render
    fez como cápsulas cinza de ~8 px, ficam finas, na espessura do PDF (4,2 px), em inox com contorno
    fino; a soleira, branca chapada, vira a de entrada de elevador: inox escovado no sentido da porta,
    com os dois frisos-guia, entre os batentes de alumínio.
20. Área verde (pedido do usuário): a faixa entre o pátio e a parede tracejada de fora (à esquerda, e
    a faixa estreita embaixo, até o tracejado de dentro) é jardim, como a lateral do lote no Térreo:
    no quadro comum, a faixa da esquerda recebe o jardim vizinho do Térreo retocado na mesma altura
    (grama em cima, as touceiras de samambaias e palmeiras embaixo) e a de baixo, grama tecida da
    grama limpa do Térreo; só o fundo branco muda (pátio, prédio e peças brancas ficam).
21. Janelas do WC DCE e do DCE 1 (pedido do usuário: vidros finos): as cápsulas grossas do render,
    que passavam 3 px do vão para dentro do cômodo e para a circulação, saem (granito em cima, Bege
    Bahia embaixo) e as janelas entram no desenho fino dos outros vidros (`vidros_fixos`).
22. Portas de giro (pedido do usuário: mais finas e elegantes): as folhas, que o render fez como
    barras de 10 a 12 px com contorno preto, e os arcos saem (piso tecido do próprio cômodo, sem tocar
    nas paredes da base chapada) e entram do PDF: a folha na espessura do PDF (3,4 px), em branco
    suave com contorno fino, e o arco em traço fino (no granito, o cinza dos arcos; no Bege Bahia, um
    cinza mais escuro no lugar do preto).
12. Pátio: a parede tracejada dupla de fora (à esquerda, embaixo e no alto), que o motor apagou ou
    cortou, volta: os traços do PDF (ARQ_PAREDE, fora da planta) desenhados no quadro comum.

Escala (pedido do usuário): a imagem final sai no quadro comum das bases (3840 x 2160, a folha 16:9
inteira, o mesmo das pranchas), com a planta exatamente sob a do Térreo; fora da planta, o fundo é
branco puro. Saídas: _retocado (quadro do render) e _final (quadro comum).

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/retoque_subsolo_casad.py POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_v1_render.webp \
      --saida POE642_CasaD/renders --nome POE642_CasaD_PH_Subsolo_v1_retocado
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))

from retoque_terreo_casac import CHUVEIRO_TETO, CROMO, CROMO_CLARO, CROMO_ESCURO, SS  # noqa: E402
from retoque_terreo_casab import LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO  # noqa: E402
from retoque_terreo_casad import interpolar, textura  # noqa: E402
from texturizar_base import quilting  # noqa: E402

BASE = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Subsolo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Subsolo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Subsolo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - SUBSOLO - CASA D.pdf"
CONFIG = RAIZ / "POE642_CasaD/config_bases.json"


def alinhar_base(render):
    """Base 16:9 reduzida ao tamanho do render e levada a ele por SIFT + afim (como no Térreo)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return A


def pdf_cadeia(A, forma_render):
    """Página do PDF e a conversão PDF -> render pela mesma cadeia da base (recorte, largura da base,
    tela 16:9, redução ao tamanho do render e o afim A)."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Subsolo"]["pagina"]]
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


# trechos limpos do granito do depósito, entre as juntas do motor (px do render)
GRANITO = [(1110, 60, 1176, 220), (1192, 60, 1326, 220), (1192, 240, 1326, 380)]

FAIXA_DEPOSITO = {
    "ret": (1046, 42, 1132, 257),          # janela: a faixa e um trecho do granito à direita
    "faixa": (1049, 44, 1104, 256),        # a faixa areia, até a sombra da borda direita
    "lum_min": 45,                         # a parede (escura) não entra na luz nem muda
}

JUNTAS_DEPOSITO = {
    "ret": (1046, 42, 1398, 498),          # o depósito inteiro (até a parede da academia)
    "faixas": [(1180, 44, 1185, 497), (1332, 44, 1337, 497),        # juntas verticais (x 1182 e 1334)
               (1100, 226, 1396, 231), (1143, 387, 1373, 392)],     # horizontais (y 228 e 389)
    "manchas": [(1112, 252, 9, 8), (1092, 305, 9, 10), (1130, 305, 9, 9), (1204, 422, 9, 10)],
    "lum": (45, 200),                      # só o granito e as juntas mudam; a parede e os arcos ficam
    "folha": (1141, 479, 1199, 488),       # a folha da porta no fim da escada (com o contorno) não muda
}

BOX_WC = {
    "box": (711, 45, 809, 104),            # piso do box do WC DCE, acima da divisória cinza
    "ref": (712, 114, 808, 245),           # o granito do resto do banheiro
    "lum": (50, 130),                      # só o piso entra na conta (sem louças nem paredes)
}

# chuveiros na geometria do PDF (px do render), com a placa aprovada da Casa A, como no Térreo;
# a escala do render é ~2,73 x a do Térreo, então sombra e brilho crescem na mesma proporção
SOMBRA_CHUVEIRO = {"desloc": (-2.7, 2.7), "sigma": 2.2, "forca": 0.3}
CHUVEIRO_WC = {
    "nome": "WC DCE",
    "lum_max": 130,                                       # a luz vem só do granito, sem o branco do símbolo
                                                          # (nos pisos de Bege Bahia, 235: o piso tem ~215)
    "apagar": [(711, 67, 754, 92)],                       # o quadrado, o braço e o toco junto à parede
    "fontes": [(714, 48, 730, 66), (756, 48, 806, 100), (714, 93, 750, 103)],
    "parede": (699, 72, 711, 87),                         # o toco branco que entrou na parede
    "ducha": (733.4, 70.8, 750.2, 87.5),
    "braco": (709.6, 78.1, 741.8, 80.2),                  # do centro da ducha à face da parede
    "canopla": (709.6, 76.4, 711.4, 81.9),
    "janela": (698, 62, 760, 98),
}

# armário até o teto do DCE 1: a madeira areia dos armários do Térreo retocado (aprovado), ampliada
# na razão entre as escalas dos dois renders, que é o mesmo aspecto que ela tem na prancha
TERREO_RETOCADO = RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png"
ARMARIO_DCE = {
    "ret": (824, 45, 925, 90),             # o miolo; os contornos escuros da direita e de baixo ficam
    # (trecho do Térreo, giro em graus): o da direita da suíte 2 (veio em pé, girado) e o do DCE
    "fontes": [((1128, 740, 1143, 797), 90), ((1297, 332, 1324, 346), 0)],
    "escala": 2.73,
    "mancha": (921, 192, 9, 8),            # mancha clara no granito, acima do criado-mudo
    "janela_mancha": (906, 178, 945, 204),
    "fontes_piso": [(840, 110, 900, 180), (840, 200, 880, 240)],
}

# sauna (px do render, da geometria do PDF): o miolo é refeito inteiro em Bege Bahia tecido do pátio
# (o mesmo tom do piso da sauna no render), na luz do piso que já era Bege Bahia
SAUNA = {
    "miolo": (597, 889, 846, 1073),        # entre o caixilho do vidro, as paredes e a linha da porta
    "fontes": [(330, 430, 450, 620), (450, 430, 560, 620), (330, 640, 450, 830), (450, 640, 560, 830)],
    "luz": (675, 895, 840, 965),           # o piso limpo que já era Bege Bahia
    "banco": (609.1, 973.3, 846.9, 1073.6),
    "degrau_ate": 1023.5,                  # o degrau da frente vai até aqui; daí para baixo, o assento
    "tons": (0.97, 1.0),                   # degrau e assento: o mesmo mármore, o degrau só um pouco abaixo
    "sombra": 0.18, "alcance": 4.0,        # sombra de cada borda no nível de baixo (força, decaimento px)
    "brilho": 0.05, "quina": 1.5,          # brilho leve na quina do nível de cima (força, largura px)
}

CHUVEIRO_DUCHA = {
    "nome": "ducha da antessala",
    "lum_min": 150,                                       # a luz só do Bege Bahia, sem a borda da parede
    "apagar": [(894, 1030, 918, 1073), (884, 1063, 928, 1073)],   # quadrado, braço e a cruz acima da parede
    "fontes": [(863, 1032, 890, 1070), (918, 1032, 945, 1070), (965, 990, 1045, 1065)],
    "parede": (884, 1073, 928, 1088),                     # a cruz branca pintada sobre a parede de baixo
    "ducha": (897.3, 1032.9, 914.1, 1049.6),
    "braco": (904.6, 1041.2, 906.7, 1073.0),
    "canopla": (902.9, 1071.3, 908.4, 1073.2),
    "janela": (888, 1026, 924, 1080),
}
CHUVEIRO_BOX = {
    "nome": "box do vestiário",
    "lum_min": 150,                                       # a luz só do Bege Bahia, sem a borda da parede
    "apagar": [(1278, 1009, 1322, 1048)],
    "fontes": [(1276, 992, 1318, 1010), (1240, 1048, 1318, 1072)],
    "parede": (1322, 1006, 1336, 1052),                   # a cruz (e o nicho) sobre a parede da direita
    "alem": [(1336, 1023, 1343, 1036)],                   # o toco da cruz no vinílico da academia
    "fontes_alem": [(1345, 985, 1440, 1065)],
    "ducha": (1281.7, 1021.5, 1298.5, 1038.2),
    "braco": (1290.1, 1028.8, 1322.0, 1030.9),
    "canopla": (1320.3, 1027.1, 1322.3, 1032.5),
    "janela": (1272, 1014, 1330, 1046),
}

CUBA_VEST = {
    "bacia": (1080.5, 989.6, 1106.8, 1044.6),   # a cuba retangular; à esquerda, a faixa da torneira
    "raio": 3.5, "aba": 2.6, "fundo": 5.0,       # canto, largura da aba e da borda da bacia até o fundo
    "valvula": (1093.65, 1017.1, 2.0),
    # torneira: sobre a bancada clara o cromado some (como no lavatório do Térreo): contorno escuro e
    # sombra curta (dx, dy, sigma, força)
    "base": ((1076.0, 1017.65), 2.6), "bica": (1076.0, 1089.5, 1017.65), "larg_bica": 2.6,
    "escuro": (92, 96, 100), "sombra": (1.6, 1.6, 2.0, 0.35),
    "janela": (1062, 982, 1114, 1052),
}

LETREIROS = {
    # (janela, caixa das letras): as letras são os px claros (> 100) da caixa, com 2 px de folga
    "lonas": [((1138, 780, 1183, 822), (1142, 788, 1153, 813)), ((1223, 777, 1268, 820), (1227, 785, 1238, 810))],
    "fontes": [(1150, 812, 1175, 836), (1238, 812, 1262, 836)],
    "lum": (60, 100),                      # a luz vem só da lona (sem os trilhos nem as letras)
}

QUADRO = {"largura": 3840, "altura": 2160, "ss": 2}
TRACEJADO = {
    "largura": 1.1, "cor": (62, 64, 66),   # o traço do tracejado que o motor manteve, na escala final
    # fora da planta (vis de 1800 px): à esquerda do pátio, abaixo dele e a faixa de cima do pátio
    "fora": lambda x, y: x < 160 or y > 944 or (639 < y < 649.5 and x < 275),
}

# arcos das portas sobre o granito: o cinza do Térreo (Casa C), num traço na escala deste render
ARCOS = {"granito": (50, 66, 90), "tol": 12, "fracao": 0.3, "min_px": 15,
         "cor": (160, 161, 160), "larg": 1.1, "faixa": 2.5, "escuro": 70}

ESCADA = {
    "ret": (690, 390, 1130, 490),          # do pátio (a sombra do 1º espelho) à porta do depósito
    "refazer_de": 693,                     # daí para a direita o Bege Bahia é refeito (some o círculo)
    "x0": 696.4, "passo": 27.1, "pisos": 16,
    "escurece": 0.12,                      # o piso de baixo fica 12% mais escuro que o de cima
    "sombra": 0.2, "alcance": 5.0,         # sombra do espelho no piso de baixo: força e decaimento (px)
}

# vasos: o polígono preenchido do PDF (ARQ_LOUÇAS E METAIS) pela caixa em px do render; a parede é
# o lado do tanque; as cores são as louças aprovadas da Casa B
VASOS = [
    {"nome": "WC DCE", "caixa": (709.1, 197.6, 752.8, 227.4), "parede": "esquerda"},
    {"nome": "WC do vestiário", "caixa": (1279.2, 918.9, 1322.8, 948.7), "parede": "direita"},
]
VASO = {"dobradica": 5.7,                 # da parede até a linha da dobradiça (o PDF quebra ali o contorno)
        "recuo": 1.2,                      # o tampo recuado da borda da louça
        "cor_tampo": (250, 250, 249),
        "sombra": (1.6, 1.6, 2.2, 0.28),   # sombra no piso: dx, dy, sigma, força
        "sombra_tampo": (0.5, 0.6, 0.8, 0.18),
        "volume": (0.88, 5.0),             # louça: tom na borda e alcance (px) do sombreado de volume
        "volume_tampo": (0.9, 6.0)}
# (parafusos e dobradiças ficam de fora: com 1 a 2 px viravam manchas sem forma)

# portas de correr de vidro entre o pátio e a academia (px do render, do PDF, layer ARQ_PAREDE)
PORTAS_VIDRO = {
    "vao": (577, 517, 596, 869),           # do pátio (com a ponta arredondada da cápsula) ao vinílico
    "luz": (556, 525, 578, 860),           # o pátio logo ao lado: tom da soleira
    # folhas: (trilho x0, x1), (y0, y1), montantes (y de cada ponta) e a linha central do vidro
    "folhas": [((581.2, 584.6), (517.9, 605.7), (526.4, 597.3), 582.9),
               ((584.6, 588.0), (605.7, 693.6), (614.2, 685.1), 586.3),
               ((584.6, 588.0), (693.6, 781.4), (702.0, 772.9), 586.3),
               ((581.2, 584.6), (781.4, 869.2), (789.8, 860.7), 582.9)],
    "batentes": [(581.2, 516.3, 593.9, 517.9), (581.2, 869.2, 593.9, 870.9)],
    "vidro": (222, 218, 210), "aluminio": (150, 153, 156), "linha": (150, 152, 155),
    "contorno": (70, 72, 74), "larg_contorno": 0.5, "larg_linha": 0.45,
}

# vidros fixos (px do render, do PDF, layer ARQ_PAREDE): vidro, linha central, caixilhos, retornos de
# parede, faces da parede e o que volta a ser piso (Bege Bahia; na janela, também o vinílico)
VIDROS_FIXOS = [
    {"nome": "janela alta da academia", "janela": (600, 490, 698, 524),
     "bege": (604.9, 491.5, 694.2, 516.4), "luz": (612, 470, 690, 489),
     "vinil": (606, 517, 693, 522), "fontes_vinil": [(615, 530, 690, 560)],
     "paredes": [(604.9, 499.5, 607.5, 505.4), (604.9, 509.7, 607.5, 516.4),
                 (691.6, 499.6, 694.2, 505.5), (691.6, 509.7, 694.2, 516.4)],
     "caixilhos": [(604.9, 505.4, 608.7, 509.7), (690.3, 505.5, 694.2, 509.7)],
     "vidro": (608.7, 505.4, 690.3, 509.7), "centro": ((608.7, 507.6), (690.3, 507.6)),
     "faces": [((607.5, 499.5), (691.6, 499.5)), ((607.5, 516.4), (691.6, 516.4))]},
    {"nome": "vidro da sauna", "janela": (574, 884, 599, 1078),
     "bege": (576.0, 887.9, 597.0, 1073.6), "luz": (556, 900, 575, 1060),
     "paredes": [(587.1, 887.9, 593.9, 890.4), (587.1, 1071.1, 593.9, 1073.6)],
     "caixilhos": [(582.9, 887.9, 587.1, 890.9), (582.9, 1070.7, 587.1, 1073.6)],
     "vidro": (582.9, 890.9, 587.1, 1070.7), "centro": ((585.0, 890.9), (585.0, 1070.7)),
     "faces": [((581.2, 887.9), (581.2, 1073.6)), ((593.9, 890.4), (593.9, 1071.1))]},
]
# janelas da parede de baixo do bloco do DCE: o que a cápsula do render cobriu fora do vão volta antes
# (granito no cômodo, Bege Bahia na circulação; a luz vem só do próprio piso)
BEGE = [(330, 430, 450, 620), (450, 430, 560, 620), (330, 640, 450, 830), (450, 640, 560, 830)]
for _nome, (_x0, _x1), (_jx0, _jx1), _paredes, _caix, _vidro, _yc, _faces in [
        ("janela do WC DCE", (732.7, 783.7), (726, 790),
         [(732.7, 252.2, 735.3, 259.0), (781.1, 252.2, 783.7, 259.0)],
         [(732.7, 248.0, 735.7, 252.2), (780.7, 248.0, 783.7, 252.2)], (734.4, 250.1, 782.0, 254.3), 252.2,
         [((732.7, 246.3), (783.7, 246.3)), ((735.3, 259.0), (781.1, 259.0))]),
        ("janela do DCE 1", (921.4, 1006.4), (914, 1014),
         [(921.4, 252.3, 924.0, 259.0), (1003.9, 252.3, 1006.4, 259.0)],
         [(921.4, 248.0, 924.4, 252.3), (1003.4, 248.1, 1006.4, 252.3)], (923.1, 250.1, 1004.7, 254.4), 252.3,
         [((921.4, 246.4), (1006.4, 246.4)), ((924.0, 259.0), (1003.9, 259.0))])]:
    VIDROS_FIXOS.append({
        "nome": _nome, "janela": (_jx0, 238, _jx1, 268),
        "restaurar": [((_jx0, 230, _jx1, 247), (int(_x0), 242, int(round(_x1)), 247), "granito", (45, 110)),
                      ((_jx0, 258, _jx1, 274), (int(_x0), 258, int(round(_x1)), 263), "bege", (150, 240))],
        "bege": (_x0, 246.3, _x1, 259.0), "luz": (_jx0 + 10, 264, _jx1 - 10, 272),
        "paredes": _paredes, "caixilhos": _caix, "vidro": _vidro,
        "centro": ((_vidro[0], _yc), (_vidro[2], _yc)), "faces": _faces})
FACE = {"cor": (120, 122, 124), "larg": 0.45}

# portas de giro (px do render, do PDF, layer ARQ_PAREDE): folha (retângulo) e o arco; o piso do cômodo
PORTAS_GIRO = [
    ("WC DCE", (758.1, 125.0, 811.1, 128.4), "granito"),
    ("DCE 1", (831.3, 193.6, 834.7, 246.3), "granito"),
    ("depósito, folha de cima", (1053.3, 261.4, 1102.0, 264.8), "granito"),
    ("depósito, folha de baixo", (1053.3, 371.5, 1102.0, 374.9), "granito"),
    ("depósito, fim da escada", (1142.6, 482.8, 1195.6, 486.2), "granito"),
    ("sauna", (855.3, 890.1, 914.8, 893.5), "bege"),
    ("ducha", (885.8, 965.9, 889.2, 1027.4), "bege"),
    ("vestiário", (1076.3, 893.2, 1127.3, 896.6), "bege"),
    ("WC do vestiário", (1213.1, 971.7, 1268.3, 975.1), "bege"),
    ("box do vestiário", (1213.1, 983.5, 1268.3, 986.9), "bege"),
]
PORTA = {"folha": (238, 238, 236), "contorno": (88, 90, 92), "larg_contorno": 0.5,
         "margem": (5, 4),                 # o que sai em volta da folha do PDF: na espessura e no comprimento
         "faixa_arco": 2.5,                # e em volta do arco do PDF
         "arco": {"granito": ((160, 161, 160), 1.1), "bege": ((110, 112, 115), 0.9)},
         "lum": {"granito": (45, 110), "bege": (150, 240)},
         "escuro": {"granito": 70, "bege": 150}}

ELEVADOR_ENTRADA = {
    "janela": (1536, 364, 1566, 499),
    "capsulas": [(1541, 367, 1550, 406), (1541, 456, 1550, 497)],   # o que sai (vira o cinza do poço)
    "poco": (1538, 410, 1545, 455),        # o cinza do poço, entre as folhas
    "folhas": [(1545.9, 373.2, 1550.1, 402.7), (1545.9, 461.8, 1550.1, 491.4)],
    "soleira": (1550.6, 404.8, 1563.3, 459.7),
    "batentes": [(1550.6, 402.7, 1563.3, 404.8), (1550.6, 459.7, 1563.3, 461.8)],
    "frisos": (1554.0, 1559.6), "larg_friso": 0.8,
    "inox": (190, 192, 195), "inox_folha": (200, 202, 205), "friso": (112, 115, 118), "brilho": (222, 224, 226),
}

AREA_VERDE = {
    "ret_vis": (132.2, 648.0, 644.5, 949.3),   # dentro do tracejado de dentro (vis de 1800 px)
    "esquerda_ate_vis": 166.0,                 # a faixa da esquerda (até o pátio, com folga)
    "desloc": -66,                             # px do quadro: o jardim do Térreo logo à esquerda
    "grama": [(370, 1160, 490, 1500)],         # grama limpa do Térreo no quadro de 3840
    "branco": 235,                             # só o fundo claro vira jardim
}


def apagar_largo(out, ret, mascara, fontes, sigma=4.0, borda=0.8, lum_min=None, lum_max=None, escuros=False):
    """Como o apagar do Térreo, para áreas largas: a luz do entorno (por canal) vem da convolução
    normalizada em várias escalas (interpolar), que cobre o miolo da máscara; com lum_min, a parede
    (escura) não entra na luz e não muda (com escuros=True, os traços escuros dentro da máscara, como o
    contorno de um símbolo, também mudam); com lum_max, peças claras (folhas de porta) não entram na luz."""
    x0, y0, x1, y1 = ret
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    claro = reg.mean(axis=2) > lum_min if lum_min is not None else np.ones((h, w), bool)
    m = cv2.GaussianBlur(mascara.astype(np.float32), (0, 0), borda) if borda else mascara.astype(np.float32)
    m = np.maximum(m, mascara.astype(np.float32))
    if not escuros:
        m *= claro
    amostra = ~mascara & claro
    if lum_max is not None:
        amostra &= reg.mean(axis=2) < lum_max
    luz = interpolar(reg, amostra, sigma)
    tex = textura(out, fontes, h, w)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - m[..., None]) + tex * luz * m[..., None], 0, 255).astype(np.uint8)
    return out


def faixa_deposito(out):
    q = FAIXA_DEPOSITO
    x0, y0, x1, y1 = q["ret"]
    fx0, fy0, fx1, fy1 = q["faixa"]
    m = np.zeros((y1 - y0, x1 - x0), bool)
    m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = True
    out = apagar_largo(out, q["ret"], m, GRANITO, sigma=4.0, borda=0.8, lum_min=q["lum_min"])
    print("    faixa areia do depósito fora; granito no lugar")
    return out


def juntas_deposito(out):
    q = JUNTAS_DEPOSITO
    x0, y0, x1, y1 = q["ret"]
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for fx0, fy0, fx1, fy1 in q["faixas"]:
        m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = 1
    for mx, my, mw, mh in q["manchas"]:
        cv2.ellipse(m, (mx + mw // 2 - x0, my + mh // 2 - y0), (mw // 2 + 3, mh // 2 + 3), 0, 0, 360, 1, -1)
    lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    m = m.astype(bool) & (lum > q["lum"][0]) & (lum < q["lum"][1])
    fx0, fy0, fx1, fy1 = q["folha"]
    m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = False
    out = apagar_largo(out, q["ret"], m, GRANITO, sigma=2.0, borda=0.6, lum_min=q["lum"][0], lum_max=110)
    print(f"    juntas e manchas do depósito fora: {int(m.sum())} px")
    return out


def piso_box_wc(out):
    q = BOX_WC
    reg = out.astype(np.float32)

    def mediana(r):
        x0, y0, x1, y1 = r
        p = reg[y0:y1, x0:x1].reshape(-1, 3)
        lum = p.mean(axis=1)
        return np.median(p[(lum > q["lum"][0]) & (lum < q["lum"][1])], axis=0)

    ganho = mediana(q["ref"]) / mediana(q["box"])
    x0, y0, x1, y1 = q["box"]
    b = reg[y0:y1, x0:x1]
    piso = (b.mean(axis=2) > 45)[..., None]
    out[y0:y1, x0:x1] = np.clip(np.where(piso, b * ganho, b), 0, 255).astype(np.uint8)
    print(f"    piso do box do WC DCE no tom do granito (ganho BGR {np.round(ganho, 3)})")
    return out


def desenhar_chuveiro(out, d, sombra=SOMBRA_CHUVEIRO):
    """Chuveiro visto de cima, como o do WC DCE do Térreo: sombra curta, ducha quadrada (a placa da
    Casa A), braço cromado (horizontal ou vertical, um retângulo do PDF) do centro da ducha à face da
    parede, com o brilho no eixo, e a canopla na parede."""
    wx0, wy0, wx1, wy1 = d["janela"]
    h, w = wy1 - wy0, wx1 - wx0
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def ret_ss(r):
        return (int(round((r[0] - wx0) * SS)), int(round((r[1] - wy0) * SS)),
                int(round((r[2] - wx0) * SS)), int(round((r[3] - wy0) * SS)))

    def pintar(mascara, cor):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    dx0, dy0, dx1, dy1 = ret_ss(d["ducha"])
    ducha = np.zeros((h * SS, w * SS), np.uint8)
    cv2.rectangle(ducha, (dx0, dy0), (dx1, dy1), 255, -1)
    M = np.float32([[1, 0, sombra["desloc"][0] * SS], [0, 1, sombra["desloc"][1] * SS]])
    sb = cv2.GaussianBlur(cv2.warpAffine(ducha.astype(np.float32), M, (w * SS, h * SS)), (0, 0), sombra["sigma"] * SS) / 255
    reg *= (1 - sombra["forca"] * cv2.resize(sb, (w, h), interpolation=cv2.INTER_AREA))[..., None]
    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    placa = cv2.resize(img[hy0:hy1, hx0:hx1], (dx1 - dx0, dy1 - dy0), interpolation=cv2.INTER_CUBIC)
    cor = np.zeros((h * SS, w * SS, 3), np.uint8)
    cor[dy0:dy1, dx0:dx1] = placa
    a = cv2.resize(ducha.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    c = cv2.resize(cor.astype(np.float32) * (ducha[..., None] / 255), (w, h), interpolation=cv2.INTER_AREA) / np.maximum(a, 1e-6)
    reg = reg * (1 - a) + c * a
    bx0, by0, bx1, by1 = ret_ss(d["braco"])
    braco = np.zeros_like(ducha)
    cv2.rectangle(braco, (bx0, by0), (bx1, by1), 255, -1)
    brilho = np.zeros_like(ducha)
    if bx1 - bx0 >= by1 - by0:                       # braço horizontal: brilho ao longo de x
        yc = (by0 + by1) // 2 - SS // 4
        cv2.line(brilho, (bx0, yc), (bx1, yc), 255, max(1, SS // 2))
    else:
        xc = (bx0 + bx1) // 2 - SS // 4
        cv2.line(brilho, (xc, by0), (xc, by1), 255, max(1, SS // 2))
    pintar(braco, CROMO_ESCURO)
    pintar(brilho, CROMO_CLARO)
    cx0, cy0, cx1, cy1 = ret_ss(d["canopla"])
    canopla = np.zeros_like(ducha)
    cv2.rectangle(canopla, (cx0, cy0), (cx1, cy1), 255, -1)
    pintar(canopla, CROMO)
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    return out


def trocar_chuveiro(out, q):
    """O símbolo do CAD sai (piso tecido do próprio ambiente, na luz do entorno), a parede volta ao
    preto onde o símbolo entrou nela, e entra o chuveiro desenhado."""
    pad = 8                                          # margem de piso em volta: a luz vem dela
    for x0, y0, x1, y1 in q["apagar"]:
        m = np.zeros((y1 - y0 + 2 * pad, x1 - x0 + 2 * pad), bool)
        m[pad:-pad, pad:-pad] = True
        out = apagar_largo(out, (x0 - pad, y0 - pad, x1 + pad, y1 + pad), m, q["fontes"], sigma=2.0, borda=0.0,
                           lum_min=q.get("lum_min", 45), lum_max=q.get("lum_max", 235), escuros=True)
    if q.get("parede"):
        # a parede volta ao preto onde o símbolo entrou nela, no preto do miolo da própria parede em
        # volta (praticamente 0, desvio < 1): o retalho inteiro, sem fantasma do contorno da cruz
        x0, y0, x1, y1 = q["parede"]
        e = 12
        viz = out[y0 - e:y1 + e, x0 - e:x1 + e].reshape(-1, 3)
        dentro = np.zeros((y1 - y0 + 2 * e, x1 - x0 + 2 * e), bool)
        dentro[e:-e, e:-e] = True
        miolo = viz[(viz.astype(np.float32).mean(axis=1) <= 5) & ~dentro.ravel()]
        out[y0:y1, x0:x1] = np.median(miolo, axis=0).astype(np.uint8)
    for x0, y0, x1, y1 in q.get("alem", []):
        m = np.zeros((y1 - y0 + 2 * pad, x1 - x0 + 2 * pad), bool)
        m[pad:-pad, pad:-pad] = True
        out = apagar_largo(out, (x0 - pad, y0 - pad, x1 + pad, y1 + pad), m, q["fontes_alem"], sigma=2.0,
                           borda=0.0, lum_min=45, lum_max=200, escuros=True)
    out = desenhar_chuveiro(out, q)
    print(f"    {q['nome']}: símbolo do CAD fora; ducha, braço e canopla do PDF")
    return out


def armario_dce(out):
    q = ARMARIO_DCE
    img = cv2.imread(str(TERREO_RETOCADO))
    fontes = []
    for (x0, y0, x1, y1), giro in q["fontes"]:
        t = img[y0:y1, x0:x1]
        if giro:
            t = np.rot90(t)
        t = cv2.resize(t, None, fx=q["escala"], fy=q["escala"], interpolation=cv2.INTER_CUBIC).astype(np.float32)
        fontes += [np.ascontiguousarray(v) for v in (t, t[:, ::-1], t[::-1, :], t[::-1, ::-1])]
    x0, y0, x1, y1 = q["ret"]
    tex = quilting(fontes, y1 - y0, x1 - x0, p=24, sobra=8, candidatos=600)[:y1 - y0, :x1 - x0]
    out[y0:y1, x0:x1] = np.clip(tex, 0, 255).astype(np.uint8)
    jx0, jy0, jx1, jy1 = q["janela_mancha"]
    mx, my, mw, mh = q["mancha"]
    m = np.zeros((jy1 - jy0, jx1 - jx0), np.uint8)
    cv2.ellipse(m, (mx + mw // 2 - jx0, my + mh // 2 - jy0), (mw // 2 + 3, mh // 2 + 3), 0, 0, 360, 1, -1)
    out = apagar_largo(out, q["janela_mancha"], m.astype(bool), q["fontes_piso"], sigma=2.0, borda=0.6,
                       lum_min=45, lum_max=110)
    print("    armário até o teto do DCE 1 em madeira areia, sem a diagonal; mancha do piso fora")
    return out


def sauna(out):
    q = SAUNA
    x0, y0, x1, y1 = q["miolo"]
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    # luz chapada: a mediana do piso limpo (a sombra que o motor pôs junto ao L não entra)
    lx0, ly0, lx1, ly1 = q["luz"]
    p = reg[ly0 - y0:ly1 - y0, lx0 - x0:lx1 - x0].reshape(-1, 3)
    luz = np.median(p[p.mean(axis=1) > 170], axis=0)[None, None, :]
    novo = textura(out, q["fontes"], h, w, p=24) * luz
    # fator em 8 x (bordas sem serrilhado): tom de cada nível, sombra de cada borda no nível de baixo
    # (o degrau no piso, o assento no degrau, as pontas da esquerda no piso) e brilho na quina de cima
    bx0, by0, bx1, by1 = q["banco"]
    ym = q["degrau_ate"]
    yy, xx = np.mgrid[0:h * SS, 0:w * SS]
    yy = y0 + (yy + 0.5) / SS
    xx = x0 + (xx + 0.5) / SS
    no_banco = xx >= bx0
    degrau = no_banco & (yy >= by0) & (yy < ym)
    assento = no_banco & (yy >= ym)
    fator = np.ones(yy.shape, np.float32)
    fator[degrau] = q["tons"][0]
    fator[assento] = q["tons"][1]

    def sombra(d):
        return 1 - q["sombra"] * np.exp(-np.maximum(d, 0) / q["alcance"])

    piso = ~(degrau | assento)
    s_piso = np.minimum(np.where(no_banco & (yy < by0), sombra(by0 - yy), 1.0),
                        np.where((xx < bx0) & (yy >= by0 - 2), sombra(bx0 - xx), 1.0))
    fator[piso] *= s_piso[piso]
    fator[degrau] *= sombra(ym - yy)[degrau]
    quina = ((degrau & (yy - by0 < q["quina"])) | (assento & (yy - ym < q["quina"]))
             | ((degrau | assento) & (xx - bx0 < q["quina"])))
    fator[quina] *= 1 + q["brilho"]
    fator = cv2.resize(fator, (w, h), interpolation=cv2.INTER_AREA)
    out[y0:y1, x0:x1] = np.clip(novo * fator[..., None], 0, 255).astype(np.uint8)
    print("    sauna: braço do L fora; banco no mármore Bege Bahia, níveis pela sombra e pela quina")
    return out


def cuba_vestiario(out):
    q = CUBA_VEST
    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def px(v, o=0.0):
        return int(round((v - o) * SS))

    def pintar(mascara, cor, forca=1.0):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None] * forca
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    def ret_arred(b, raio):
        m = np.zeros((h * SS, w * SS), np.uint8)
        bx0, by0, bx1, by1 = px(b[0], wx0), px(b[1], wy0), px(b[2], wx0), px(b[3], wy0)
        rr = min(px(raio), (bx1 - bx0) // 2, (by1 - by0) // 2)
        cv2.rectangle(m, (bx0 + rr, by0), (bx1 - rr, by1), 255, -1)
        cv2.rectangle(m, (bx0, by0 + rr), (bx1, by1 - rr), 255, -1)
        for cx, cy in ((bx0 + rr, by0 + rr), (bx1 - rr, by0 + rr), (bx0 + rr, by1 - rr), (bx1 - rr, by1 - rr)):
            cv2.circle(m, (cx, cy), rr, 255, -1)
        return m

    def circulo(cx, cy, r):
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.circle(m, (px(cx, wx0), px(cy, wy0)), max(1, px(r)), 255, -1)
        return m

    bx0, by0, bx1, by1 = q["bacia"]
    pintar(ret_arred(q["bacia"], q["raio"]), LOUCA_CONTORNO)
    pintar(ret_arred((bx0 + 0.9, by0 + 0.9, bx1 - 0.9, by1 - 0.9), q["raio"] - 0.9), LOUCA)
    passos = 8
    for i in range(passos):                       # bacia: a borda mais escura indo ao fundo claro
        k = i / (passos - 1)
        cor = tuple(BACIA_BORDA[c] * (1 - k) + BACIA_FUNDO[c] * k for c in range(3))
        ins = q["aba"] + k * q["fundo"]
        pintar(ret_arred((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(1.0, q["raio"] - k * 2)), cor)
    vx, vy, vr = q["valvula"]
    pintar(circulo(vx, vy, vr), CROMO_ESCURO)
    pintar(circulo(vx, vy, vr * 0.7), CROMO_CLARO)
    tx0, tx1, ty = q["bica"]
    (ox, oy), r = q["base"]
    sdx, sdy, ssig, sforca = q["sombra"]
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.line(m, (px(tx0 + sdx, wx0), px(ty + sdy, wy0)), (px(tx1 + sdx, wx0), px(ty + sdy, wy0)), 255, px(q["larg_bica"]))
    cv2.circle(m, (px(ox + sdx, wx0), px(oy + sdy, wy0)), px(r), 255, -1)
    sb = cv2.resize(cv2.GaussianBlur(m.astype(np.float32), (0, 0), ssig * SS) / 255, (w, h), interpolation=cv2.INTER_AREA)
    reg *= (1 - sforca * sb)[..., None]
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.line(m, (px(tx0, wx0), px(ty, wy0)), (px(tx1, wx0), px(ty, wy0)), 255, px(q["larg_bica"]))
    pintar(m, q["escuro"])
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.line(m, (px(tx0, wx0), px(ty, wy0)), (px(tx1 - 0.6, wx0), px(ty, wy0)), 255, px(q["larg_bica"] - 1.0))
    pintar(m, CROMO)
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.line(m, (px(tx0, wx0), px(ty - 0.4, wy0)), (px(tx1 - 0.8, wx0), px(ty - 0.4, wy0)), 255, max(1, px(0.5)))
    pintar(m, CROMO_CLARO)
    pintar(circulo(ox, oy, r), q["escuro"])
    pintar(circulo(ox, oy, r - 0.6), CROMO)
    pintar(circulo(ox - 0.4, oy - 0.4, r * 0.45), CROMO_CLARO)
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    vestiário: cuba branca com válvula e torneira cromada, na geometria do PDF")
    return out


def letreiros(out):
    q = LETREIROS
    total = 0
    for janela, caixa in q["lonas"]:
        x0, y0, x1, y1 = janela
        cx0, cy0, cx1, cy1 = caixa
        lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        m[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] = (lum[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] > q["lum"][1])
        m = cv2.dilate(m, np.ones((5, 5), np.uint8)).astype(bool)
        m[:cy0 - y0] = False
        m[cy1 - y0:] = False
        m[:, :cx0 - x0] = False
        m[:, cx1 - x0:] = False
        total += int(m.sum())
        out = apagar_largo(out, janela, m, q["fontes"], sigma=2.0, borda=0.6, lum_min=q["lum"][0],
                           lum_max=q["lum"][1], escuros=True)
    print(f"    letreiros das esteiras fora: {total} px")
    return out


def arcos_granito(out, A):
    """Arcos das portas (curvas da ARQ_PAREDE) sobre o granito: o arco preto do render sai (px escuros
    numa faixa em volta da curva do PDF, só no granito da base chapada) e entra o arco cinza fino."""
    q = ARCOS
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    gran = (np.abs(chapada.astype(np.int32) - np.array(q["granito"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    gran = cv2.morphologyEx(gran, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))   # fecha os traços finos
    pg, p2r = pdf_cadeia(A, out.shape)
    n = 0
    for d in pg.get_drawings():
        if d.get("layer") != "ARQ_PAREDE" or not any(it[0] == "c" for it in d["items"]):
            continue
        r = d["rect"]
        (x0, y0), (x1, y1) = p2r(r.x0, r.y0), p2r(r.x1, r.y1)
        x0, y0, x1, y1 = int(x0) - 6, int(y0) - 6, int(np.ceil(x1)) + 7, int(np.ceil(y1)) + 7
        if max(x1 - x0, y1 - y0) < q["min_px"] or x0 < 0 or y0 < 0 or x1 > out.shape[1] or y1 > out.shape[0]:
            continue
        g = gran[y0:y1, x0:x1].astype(bool)
        if g.mean() < q["fracao"]:
            continue
        h, w = y1 - y0, x1 - x0
        curvas = []
        for it in d["items"]:
            if it[0] == "c":
                pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
                tt = np.linspace(0, 1, 80)[:, None]
                curvas.append((1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1] + 3 * (1 - tt) * tt ** 2 * pp[2]
                              + tt ** 3 * pp[3])

        def traco(larg):
            f = np.zeros((h * SS, w * SS), np.uint8)
            for c in curvas:
                cv2.polylines(f, [np.round((c - [x0, y0]) * SS).astype(np.int32)], False, 255,
                              max(1, int(round(larg * SS))), cv2.LINE_AA)
            return cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

        lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m = (traco(2 * q["faixa"]) > 0.05) & g & (lum < q["escuro"])
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & g
        out = apagar_largo(out, (x0, y0, x1, y1), m, GRANITO, sigma=2.0, borda=0.0, lum_min=45, lum_max=130,
                           escuros=True)
        a = (traco(q["larg"]) * g)[..., None]
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.array(q["cor"], np.float32) * a, 0, 255).astype(np.uint8)
        n += 1
    print(f"    {n} arcos de porta sobre o granito em cinza fino")
    return out


def escada(out):
    q = ESCADA
    x0, y0, x1, y1 = q["ret"]
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    luz = interpolar(reg, reg.mean(axis=2) > 195, 6.0)          # sem as linhas (mais escuras)
    novo = reg.copy()
    r0 = q["refazer_de"] - x0
    novo[:, r0:] = (textura(out, SAUNA["fontes"], h, w, p=24) * luz)[:, r0:]
    # fator por coluna, com 8 amostras por px (bordas dos degraus sem serrilhado e sem linha)
    xs = x0 + (np.arange(w * SS) + 0.5) / SS
    k = np.clip(np.floor((xs - q["x0"]) / q["passo"]), -1, q["pisos"] - 1)
    base = np.where(k < 0, 1.0, 1 - q["escurece"] * (q["pisos"] - 1 - k) / (q["pisos"] - 1))
    d = q["x0"] + (k + 1) * q["passo"] - xs                   # distância ao espelho logo à direita
    sombra = np.where(k < q["pisos"] - 1, 1 - q["sombra"] * np.exp(-d / q["alcance"]), 1.0)
    fator = (base * sombra).reshape(w, SS).mean(axis=1)
    out[y0:y1, x0:x1] = np.clip(novo * fator[None, :, None], 0, 255).astype(np.uint8)
    print("    escada: sem linhas; degraus pelo tom, escurecendo para baixo, com a sombra de cada espelho")
    return out


def vasos(out, A):
    pg, p2r = pdf_cadeia(A, out.shape)
    q = VASO
    for v in VASOS:
        cx0, cy0, cx1, cy1 = v["caixa"]
        corpo = None
        for d in pg.get_drawings():
            if d.get("layer") != "ARQ_LOUÇAS E METAIS" or d["type"] != "f":
                continue
            (a0, b0), (a1, b1) = p2r(d["rect"].x0, d["rect"].y0), p2r(d["rect"].x1, d["rect"].y1)
            if max(abs(a0 - cx0), abs(b0 - cy0), abs(a1 - cx1), abs(b1 - cy1)) < 1.0:
                corpo = d
                break
        wx0, wy0, wx1, wy1 = int(cx0) - 6, int(cy0) - 6, int(np.ceil(cx1)) + 7, int(np.ceil(cy1)) + 7
        h, w = wy1 - wy0, wx1 - wx0
        pts = []
        for it in corpo["items"]:
            for p in it[1:]:
                if hasattr(p, "x"):
                    x, y = p2r(p.x, p.y)
                    pts.append([round((x - wx0) * SS), round((y - wy0) * SS)])
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.fillPoly(m, [cv2.convexHull(np.int32(pts))], 255)
        reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

        def reduzir(mm):
            return cv2.resize(mm.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)

        def pintar(mm, cor):
            nonlocal reg
            a = reduzir(mm / 255.0 if mm.dtype == np.uint8 else mm)[..., None]
            reg = reg * (1 - a) + np.asarray(cor, np.float32) * a

        sdx, sdy, ssig, sforca = q["sombra"]
        sh = cv2.warpAffine(m.astype(np.float32) / 255, np.float32([[1, 0, sdx * SS], [0, 1, sdy * SS]]), (w * SS, h * SS))
        reg *= (1 - sforca * reduzir(cv2.GaussianBlur(sh, (0, 0), ssig * SS)) * (1 - reduzir(m / 255.0)))[..., None]
        # corpo: louça com volume (distância à borda) e contorno fino
        dist = cv2.distanceTransform(m, cv2.DIST_L2, 5) / SS
        borda, alcance = q["volume"]
        tom = borda + (1 - borda) * np.clip(dist / alcance, 0, 1)
        corpo_cor = np.asarray(LOUCA, np.float32)[None, None, :] * tom[..., None]
        a = (m / 255.0)[..., None]
        cor_ss = corpo_cor * a
        pintar(m, (0, 0, 0))                          # zera onde entra o corpo
        reg += cv2.resize(cor_ss, (w, h), interpolation=cv2.INTER_AREA)
        anel = m & ~cv2.erode(m, np.ones((int(0.7 * SS), int(0.7 * SS)), np.uint8))
        pintar(anel, LOUCA_CONTORNO)
        # tampo fechado: o corpo recuado, da linha da dobradiça à frente, com volume e contorno
        tampo = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * q["recuo"] * SS) + 1,) * 2))
        xs = wx0 + (np.arange(w * SS) + 0.5) / SS
        xd = cx0 + q["dobradica"] if v["parede"] == "esquerda" else cx1 - q["dobradica"]
        if v["parede"] == "esquerda":
            tampo[:, xs < xd] = 0
        else:
            tampo[:, xs > xd] = 0
        tampo = cv2.morphologyEx(tampo, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3 * SS,) * 2))
        tdx, tdy, tsig, tforca = q["sombra_tampo"]
        st = cv2.warpAffine(tampo.astype(np.float32) / 255, np.float32([[1, 0, tdx * SS], [0, 1, tdy * SS]]), (w * SS, h * SS))
        reg *= (1 - tforca * reduzir(cv2.GaussianBlur(st, (0, 0), tsig * SS)) * (1 - reduzir(tampo / 255.0)))[..., None]
        dt = cv2.distanceTransform(tampo, cv2.DIST_L2, 5) / SS
        borda, alcance = q["volume_tampo"]
        tom = borda + (1 - borda) * np.clip(dt / alcance, 0, 1)
        cor_t = np.asarray(q["cor_tampo"], np.float32)[None, None, :] * tom[..., None] * (tampo / 255.0)[..., None]
        reg = reg * (1 - reduzir(tampo / 255.0)[..., None]) + cv2.resize(cor_t, (w, h), interpolation=cv2.INTER_AREA)
        pintar(tampo & ~cv2.erode(tampo, np.ones((int(0.6 * SS), int(0.6 * SS)), np.uint8)), LOUCA_CONTORNO)
        out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    vaso do {v['nome']}: louça com volume e tampo fechado")
    return out


def portas_vidro(out):
    q = PORTAS_VIDRO
    x0, y0, x1, y1 = q["vao"]
    h, w = y1 - y0, x1 - x0
    lx0, ly0, lx1, ly1 = q["luz"]
    p = out[ly0:ly1, lx0:lx1].reshape(-1, 3).astype(np.float32)
    luz = np.median(p[p.mean(axis=1) > 170], axis=0)[None, None, :]
    reg = textura(out, SAUNA["fontes"], h, w, p=12) * luz          # soleira de Bege Bahia

    def ret(r):
        return (round((r[0] - x0) * SS), round((r[1] - y0) * SS)), (round((r[2] - x0) * SS), round((r[3] - y0) * SS))

    def pintar(mm, cor):
        nonlocal reg
        a = cv2.resize(mm.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.asarray(cor, np.float32) * a

    for (tx0, tx1), (fy0, fy1), (gy0, gy1), xc in q["folhas"]:
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(m, *ret((tx0, fy0, tx1, fy1)), 255, -1)
        pintar(m, q["aluminio"])
        m = np.zeros_like(m)
        cv2.rectangle(m, *ret((tx0, gy0, tx1, gy1)), 255, -1)
        pintar(m, q["vidro"])
        m = np.zeros_like(m)
        cv2.line(m, (round((xc - x0) * SS), round((gy0 - y0) * SS)), (round((xc - x0) * SS), round((gy1 - y0) * SS)),
                 255, max(1, round(q["larg_linha"] * SS)))
        pintar(m, q["linha"])
        m = np.zeros_like(m)
        cv2.rectangle(m, *ret((tx0, fy0, tx1, fy1)), 255, max(1, round(q["larg_contorno"] * SS)))
        for gy in (gy0, gy1):
            cv2.line(m, (round((tx0 - x0) * SS), round((gy - y0) * SS)), (round((tx1 - x0) * SS), round((gy - y0) * SS)),
                     255, max(1, round(q["larg_contorno"] * SS)))
        pintar(m, q["contorno"])
    for b in q["batentes"]:
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(m, *ret(b), 255, -1)
        pintar(m, q["aluminio"])
        m = np.zeros_like(m)
        cv2.rectangle(m, *ret(b), 255, max(1, round(q["larg_contorno"] * SS)))
        pintar(m, q["contorno"])
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    portas de vidro da academia: folhas na espessura do PDF, soleira de Bege Bahia")
    return out


def vidros_fixos(out):
    pv = PORTAS_VIDRO
    for q in VIDROS_FIXOS:
        for (wx0, wy0, wx1, wy1), (mx0, my0, mx1, my1), piso, (lo, hi) in q.get("restaurar", []):
            m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
            m[my0 - wy0:my1 - wy0, mx0 - wx0:mx1 - wx0] = True
            m[:, :] &= True
            out = apagar_largo(out, (wx0, wy0, wx1, wy1), m, GRANITO if piso == "granito" else BEGE, sigma=2.0,
                               borda=0.0, lum_min=lo, lum_max=hi, escuros=True)
        if q.get("vinil"):
            vx0, vy0, vx1, vy1 = q["vinil"]
            m = np.zeros((vy1 - vy0 + 16, vx1 - vx0 + 16), bool)
            m[8:-8, 8:-8] = True
            out = apagar_largo(out, (vx0 - 8, vy0 - 8, vx1 + 8, vy1 + 8), m, q["fontes_vinil"], sigma=2.0, borda=0.0,
                               lum_min=80, lum_max=200, escuros=True)
        x0, y0, x1, y1 = q["janela"]
        h, w = y1 - y0, x1 - x0
        lx0, ly0, lx1, ly1 = q["luz"]
        p = out[ly0:ly1, lx0:lx1].reshape(-1, 3).astype(np.float32)
        luz = np.median(p[p.mean(axis=1) > 170], axis=0)
        viz = out[y0:y1, x0:x1].reshape(-1, 3)
        preto = np.median(viz[viz.astype(np.float32).mean(axis=1) <= 5], axis=0)
        reg = out[y0:y1, x0:x1].astype(np.float32)
        bege = textura(out, SAUNA["fontes"], h, w, p=12) * luz[None, None, :]

        def ss(v, o):
            return round((v - o) * SS)

        def mret(r, esp=-1):
            m = np.zeros((h * SS, w * SS), np.uint8)
            cv2.rectangle(m, (ss(r[0], x0), ss(r[1], y0)), (ss(r[2], x0), ss(r[3], y0)), 255, esp)
            return m

        def mlin(a, b, larg):
            m = np.zeros((h * SS, w * SS), np.uint8)
            cv2.line(m, (ss(a[0], x0), ss(a[1], y0)), (ss(b[0], x0), ss(b[1], y0)), 255, max(1, round(larg * SS)))
            return m

        def red(m):
            return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]

        def pintar(m, cor):
            nonlocal reg
            a = red(m)
            reg = reg * (1 - a) + np.asarray(cor, np.float32) * a

        a = red(mret(q["bege"]))
        reg = reg * (1 - a) + bege * a                               # peitoril / soleira e o piso em volta
        for r in q["paredes"]:
            pintar(mret(r), preto)
        for a_, b_ in q["faces"]:
            pintar(mlin(a_, b_, FACE["larg"]), FACE["cor"])
        for r in q["caixilhos"]:
            pintar(mret(r), pv["aluminio"])
        pintar(mret(q["vidro"]), pv["vidro"])
        pintar(mlin(*q["centro"], pv["larg_linha"]), pv["linha"])
        borda = max(1, round(pv["larg_contorno"] * SS))
        for r in q["caixilhos"] + [q["vidro"]]:
            pintar(mret(r, borda), pv["contorno"])
        out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    {q['nome']}: vidro fino na espessura do PDF")
    return out


def elevador_entrada(out):
    q = ELEVADOR_ENTRADA
    pv = PORTAS_VIDRO
    x0, y0, x1, y1 = q["janela"]
    h, w = y1 - y0, x1 - x0
    px0, py0, px1, py1 = q["poco"]
    poco = np.median(out[py0:py1, px0:px1].reshape(-1, 3), axis=0)
    for cx0, cy0, cx1, cy1 in q["capsulas"]:
        out[cy0:cy1, cx0:cx1] = poco
    reg = out[y0:y1, x0:x1].astype(np.float32)

    def mret(r, esp=-1):
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(m, (round((r[0] - x0) * SS), round((r[1] - y0) * SS)),
                      (round((r[2] - x0) * SS), round((r[3] - y0) * SS)), 255, esp)
        return m

    def red(m):
        return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]

    def pintar(m, cor):
        nonlocal reg
        a = red(m)
        reg = reg * (1 - a) + np.asarray(cor, np.float32) * a

    borda = max(1, round(pv["larg_contorno"] * SS))
    for r in q["folhas"]:
        pintar(mret(r), q["inox_folha"])
        pintar(mret(r, borda), pv["contorno"])
    # soleira: inox escovado no sentido da porta (ao longo de y), com os dois frisos-guia
    sx0, sy0, sx1, sy1 = q["soleira"]
    rng = np.random.default_rng(642)
    esc = rng.normal(0, 1, (h * SS, w * SS)).astype(np.float32)
    esc = cv2.GaussianBlur(esc, (0, 0), sigmaX=0.6 * SS, sigmaY=6 * SS)
    esc = esc / (esc.std() + 1e-6) * 4.0
    cor = np.asarray(q["inox"], np.float32)[None, None, :] + esc[..., None]
    a = red(mret(q["soleira"]))
    reg = reg * (1 - a) + cv2.resize(cor, (w, h), interpolation=cv2.INTER_AREA) * a
    for fx in q["frisos"]:
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.line(m, (round((fx - x0) * SS), round((sy0 - y0) * SS)), (round((fx - x0) * SS), round((sy1 - y0) * SS)),
                 255, max(1, round(q["larg_friso"] * SS)))
        pintar(m, q["friso"])
        m = np.zeros_like(m)
        cv2.line(m, (round((fx + 0.8 - x0) * SS), round((sy0 - y0) * SS)), (round((fx + 0.8 - x0) * SS), round((sy1 - y0) * SS)),
                 255, max(1, round(0.4 * SS)))
        pintar(m, q["brilho"])
    pintar(mret(q["soleira"], borda), pv["contorno"])
    for r in q["batentes"]:
        pintar(mret(r), pv["aluminio"])
        pintar(mret(r, borda), pv["contorno"])
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print("    elevador: folhas finas em inox; soleira de inox escovado com frisos, entre batentes de alumínio")
    return out


def portas_giro(out, A):
    q = PORTA
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    # só as paredes grossas: a base também tem em preto os contornos finos das folhas e dos arcos
    preto = (chapada.max(axis=2) < 60).astype(np.uint8)
    parede = cv2.morphologyEx(preto, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    parede = cv2.dilate(parede, np.ones((3, 3), np.uint8)).astype(bool)
    # e só onde o render também tem parede grossa (no vão do vestiário a base é preta onde o render
    # tem a borda da folha antiga)
    escuro = (out.astype(np.float32).mean(axis=2) < 45).astype(np.uint8)
    parede &= cv2.dilate(cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)),
                         np.ones((3, 3), np.uint8)).astype(bool)
    pg, p2r = pdf_cadeia(A, out.shape)
    arcos = []
    for d in pg.get_drawings():
        if d.get("layer") == "ARQ_PAREDE" and any(it[0] == "c" for it in d["items"]):
            (a0, b0), (a1, b1) = p2r(d["rect"].x0, d["rect"].y0), p2r(d["rect"].x1, d["rect"].y1)
            if max(a1 - a0, b1 - b0) > 15:
                curvas = []
                for it in d["items"]:
                    if it[0] == "c":
                        pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
                        tt = np.linspace(0, 1, 80)[:, None]
                        curvas.append((1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1]
                                      + 3 * (1 - tt) * tt ** 2 * pp[2] + tt ** 3 * pp[3])
                arcos.append(((a0, b0, a1, b1), curvas))
    for nome, (fx0, fy0, fx1, fy1), piso in PORTAS_GIRO:
        # o arco da porta: o que toca a folha
        arco = min(arcos, key=lambda a: min(abs(a[0][0] - fx0) + abs(a[0][1] - fy0), abs(a[0][2] - fx1) + abs(a[0][3] - fy1),
                                            abs(a[0][0] - fx0) + abs(a[0][3] - fy1), abs(a[0][2] - fx1) + abs(a[0][1] - fy0)))
        ax0, ay0, ax1, ay1 = arco[0]
        x0, y0 = int(min(fx0, ax0)) - 10, int(min(fy0, ay0)) - 10
        x1, y1 = int(np.ceil(max(fx1, ax1))) + 11, int(np.ceil(max(fy1, ay1))) + 11
        h, w = y1 - y0, x1 - x0
        horizontal = (fx1 - fx0) > (fy1 - fy0)
        me, mc = q["margem"]
        ex, ey = (mc, me) if horizontal else (me, mc)
        m = np.zeros((h, w), bool)
        m[max(0, int(fy0 - ey) - y0):int(np.ceil(fy1 + ey)) - y0, max(0, int(fx0 - ex) - x0):int(np.ceil(fx1 + ex)) - x0] = True

        def traco(curvas, larg):
            f = np.zeros((h * SS, w * SS), np.uint8)
            for c in curvas:
                cv2.polylines(f, [np.round((c - [x0, y0]) * SS).astype(np.int32)], False, 255,
                              max(1, int(round(larg * SS))), cv2.LINE_AA)
            return cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

        lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m |= (traco(arco[1], 2 * q["faixa_arco"]) > 0.05) & (lum < q["escuro"][piso])
        m &= ~parede[y0:y1, x0:x1]
        lo, hi = q["lum"][piso]
        out = apagar_largo(out, (x0, y0, x1, y1), m, GRANITO if piso == "granito" else BEGE, sigma=2.0, borda=0.0,
                           lum_min=lo, lum_max=hi, escuros=True)
        reg = out[y0:y1, x0:x1].astype(np.float32)

        def pintar(a, cor):
            nonlocal reg
            reg = reg * (1 - a[..., None]) + np.asarray(cor, np.float32) * a[..., None]

        cor_arco, larg_arco = q["arco"][piso]
        pintar(traco(arco[1], larg_arco) * ~parede[y0:y1, x0:x1], cor_arco)
        f = np.zeros((h * SS, w * SS), np.uint8)
        p0 = (round((fx0 - x0) * SS), round((fy0 - y0) * SS))
        p1 = (round((fx1 - x0) * SS), round((fy1 - y0) * SS))
        cv2.rectangle(f, p0, p1, 255, -1)
        pintar(cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA), q["folha"])
        f = np.zeros_like(f)
        cv2.rectangle(f, p0, p1, 255, max(1, round(q["larg_contorno"] * SS)))
        pintar(cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA), q["contorno"])
        out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    {len(PORTAS_GIRO)} portas de giro: folha fina do PDF e arco em traço fino")
    return out


def no_quadro(out, A):
    """O render retocado vai para o quadro comum (a base 16:9 na largura das pranchas) pelo inverso da
    cadeia base -> render (a base reduzida ao tamanho do render, não uniforme, e o afim A), com 2 x
    de superamostragem; fora da planta (a mancha da base chapada, com folga), o fundo fica branco."""
    q = QUADRO
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sxr, syr = out.shape[1] / wt, out.shape[0] / ht
    WF, HF, s = q["largura"], q["altura"], q["ss"]
    sxf, syf = WF * s / wt, HF * s / ht
    D = np.float64([[sxr / sxf, 0, 0], [0, syr / syf, 0], [0, 0, 1]])
    M = (np.vstack([A, [0, 0, 1]]) @ D)[:2]                    # quadro (2 x) -> render
    grande = cv2.warpAffine(out, M, (WF * s, HF * s), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP,
                            borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    final = cv2.resize(grande, (WF, HF), interpolation=cv2.INTER_AREA)
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), (WF, HF), interpolation=cv2.INTER_NEAREST)
    nb = (chapada.min(axis=2) < 245).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb)
    planta = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 5000])
    # os objetos brancos na base (cama, criado-mudo, armário, elevador, aparelhos, louças) são buracos
    # dentro da planta: entram nela, senão viravam fundo branco
    planta = ndimage.binary_fill_holes(planta)
    planta = cv2.dilate(planta.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    final[~planta] = 255
    print(f"    quadro comum {WF} x {HF}: planta da base com folga de 3 px; fundo branco fora dela")
    return final


def area_verde(final):
    from PIL import Image
    from rodape_entrega import no_quadro_comum
    q = AREA_VERDE
    cfg = json.loads(CONFIG.read_text())
    ent = cfg["entrega"]
    base_t = RAIZ / "POE642_CasaD" / ent["pasta_bases"] / ent["pavimentos"]["Terreo"]["base"]
    HF, WF = final.shape[:2]
    terreo = no_quadro_comum(Image.open(str(TERREO_RETOCADO)).convert("RGB"), base_t, "Terreo", WF)
    terreo = cv2.cvtColor(np.asarray(terreo), cv2.COLOR_RGB2BGR)
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    kv = wb / cfg["largura_visualizacao"]

    def quadro(xv, yv):
        return (((wt - wb) // 2 + xv * kv) * WF / wt, ((ht - hb) // 2 + yv * kv) * HF / ht)

    (x0, y0), (x1, y1) = quadro(*q["ret_vis"][:2]), quadro(*q["ret_vis"][2:])
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    xe = int(round(quadro(q["esquerda_ate_vis"], 0)[0]))
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), (WF, HF), interpolation=cv2.INTER_NEAREST)
    nb = (chapada.min(axis=2) < 245).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb)
    planta = ndimage.binary_fill_holes(np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 5000]))
    reg = final[y0:y1, x0:x1]
    m = ~planta[y0:y1, x0:x1] & (reg.min(axis=2) >= q["branco"])
    jardim = np.zeros_like(reg, dtype=np.float32)
    d = q["desloc"]
    jardim[:, :xe - x0] = terreo[y0:y1, x0 + d:xe + d]
    fontes = []
    for gx0, gy0, gx1, gy1 in q["grama"]:
        g = terreo[gy0:gy1, gx0:gx1].astype(np.float32)
        fontes += [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    resto = x1 - xe
    jardim[:, xe - x0:] = quilting(fontes, y1 - y0, resto, p=24, sobra=8, candidatos=500)[:y1 - y0, :resto]
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6)
    a = np.maximum(a, m)[..., None]
    final[y0:y1, x0:x1] = np.clip(reg * (1 - a) + jardim * a, 0, 255).astype(np.uint8)
    print(f"    área verde: {int(m.sum())} px (jardim do Térreo na faixa da esquerda, grama tecida embaixo)")
    return final


def tracejado(final):
    """Traços do tracejado de fora (ARQ_PAREDE) do PDF, direto no quadro comum (sem o afim do render)."""
    q = TRACEJADO
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Subsolo"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    HF, WF = final.shape[:2]
    kv = clip.width / cfg["largura_visualizacao"]

    def vis(p):
        return (p.x - clip.x0) / kv, (p.y - clip.y0) / kv

    def quadro(p):
        return [int(round(((p.x - clip.x0) * zoom + (wt - wb) // 2) * WF / wt * SS)),
                int(round(((p.y - clip.y0) * zoom + (ht - hb) // 2) * HF / ht * SS))]

    m = np.zeros((HF * SS, WF * SS), np.uint8)
    n = 0
    for d in pg.get_drawings():
        if d.get("layer") != "ARQ_PAREDE" or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] == "l" and q["fora"](*vis(it[1])) and q["fora"](*vis(it[2])):
                cv2.line(m, quadro(it[1]), quadro(it[2]), 255, max(1, int(round(q["largura"] * SS))), cv2.LINE_AA)
                n += 1
    a = cv2.resize(m.astype(np.float32) / 255, (WF, HF), interpolation=cv2.INTER_AREA)[..., None]
    final[:] = np.clip(final * (1 - a) + np.array(q["cor"], np.float32) * a, 0, 255).astype(np.uint8)
    print(f"    tracejado de fora do pátio: {n} traços do PDF")
    return final


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] depósito: faixa areia inventada")
    out = faixa_deposito(out)
    print("[2] depósito: juntas gigantes e manchas claras")
    out = juntas_deposito(out)
    print("[3] WC DCE: piso do box no tom do granito")
    out = piso_box_wc(out)
    print("[4] WC DCE: chuveiro")
    out = trocar_chuveiro(out, CHUVEIRO_WC)
    print("[5] DCE 1: armário até o teto")
    out = armario_dce(out)
    print("[6, 7] sauna: braço do banco em L e banco em Bege Bahia")
    out = sauna(out)
    print("[8] ducha da antessala: chuveiro")
    out = trocar_chuveiro(out, CHUVEIRO_DUCHA)
    print("[9] box do vestiário: chuveiro")
    out = trocar_chuveiro(out, CHUVEIRO_BOX)
    print("[10] vestiário: cuba da bancada")
    out = cuba_vestiario(out)
    print("[11] esteiras: letreiros nas lonas")
    out = letreiros(out)
    print("[13] arcos das portas sobre o granito")
    out = arcos_granito(out, alinhar_base(orig))
    print("[22] portas de giro mais finas")
    out = portas_giro(out, alinhar_base(orig))
    print("[14] escada: sombreamento de descida, sem linhas")
    out = escada(out)
    print("[16] sanitários")
    out = vasos(out, alinhar_base(orig))
    print("[17] portas de vidro de acesso à academia")
    out = portas_vidro(out)
    print("[18] vidro da sauna e janela alta da academia")
    out = vidros_fixos(out)
    print("[19] entrada do elevador")
    out = elevador_entrada(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")

    print("[escala] quadro comum das bases, com a planta sob a do Térreo")
    final = no_quadro(out, alinhar_base(orig))
    print("[20] área verde entre o pátio e a parede tracejada")
    final = area_verde(final)
    print("[12] pátio: tracejado de fora")
    final = tracejado(final)
    nome_final = args.nome.replace("_retocado", "") + "_final"
    cv2.imwrite(str(args.saida / f"{nome_final}.png"), final)
    print(f"[fim] {args.saida / (nome_final + '.png')}")


if __name__ == "__main__":
    main()

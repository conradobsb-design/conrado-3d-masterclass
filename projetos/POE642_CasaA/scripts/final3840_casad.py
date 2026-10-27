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
(`passos_subsolo_d`).

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
                centros_pdf=[(2470.2, 815.0), (2628.3, 815.0), (2788.8, 815.0)])
# As camas e os bancos ao pé delas (item 23; resposta 5, "Os do render"): ficam como no render aprovado de 15/10; as
# peças do PDF delas não entram e, depois das peças, o render volta no retângulo, com a sombra curta.
CAMAS_D = {"borda": 1.7, "ss": 4, "semente": 41, "camas": [
    ("suíte master", (639.5, 1560.6, 751.2, 1698.9), "baixo", "casal"),
    ("suíte 1", (1133.3, 1690.4, 1246.6, 1792.5), "dir", "casal"),
    ("suíte 2", (1592.5, 1690.4, 1705.9, 1792.5), "esq", "casal"),
    ("DCE", (2317.0, 727.8, 2373.7, 841.2), "cima", "solteiro")]}
BANCOS_D = [(1109.5, 1696.1, 1132.1, 1786.8), (1707.0, 1696.1, 1729.7, 1786.8)]
# Os cooktops de 5 bocas (decisão de 15/10): os dois deitados, 2 bocas em cima e 3 embaixo
COOKTOPS_D = [{"pt": (1332.4, 813.2, 1382.3, 841.6), "giro": 0},
              {"pt": (1719.9, 686.3, 1769.8, 714.7), "giro": 0}]
# As 4 banquetas da ilha gourmet (item 22): no PDF da Casa D são desenhos de traço da ARQ_LOUÇAS E METAIS abaixo da
# ilha; as de linho da biblioteca (0,40 m) no centro de cada uma, viradas para a ilha (para cima), entrando sob o tampo
BANQUETAS_D = {"caixa_pt": (1280.0, 865.0, 1435.0, 900.0), "camada": "ARQ_LOUÇAS E METAIS", "giro": 180}
# Os guarda-corpos de vidro (item 13): as lâminas brancas de 2 cm da ARQ_ELEMENTOS FIXOS, nenhuma desenhada antes: o L
# da borda do terraço da piscina (junto aos blocos) e as duas do vão da escada de 16 degraus (em cima e à esquerda)
GUARDA_CORPOS_D = [(604.9, 1202.9, 606.0, 1376.3), (361.7, 1375.2, 606.0, 1376.3), (361.7, 1375.2, 362.8, 1701.8),
                   (673.5, 1412.1, 966.0, 1413.2), (673.5, 1412.1, 674.6, 1483.5)]
# Os brises de ripas (item 14; resposta 2, "Em Madeira"): as ripas da ARQ_ELEMENTOS FIXOS (os preenchimentos brancos
# pequenos, com o contorno preto) nestas caixas: a lateral direita da garagem e a faixa abaixo dela, os dois lados da
# porta pivotante do hall, a fachada da suíte master (em cima e à esquerda) e a faixa à direita da escada, a lateral
# da suíte 3, as duas faixas da fachada de baixo e as duas peças giradas junto à gourmet
BRISES_D = {"caixas_pt": [(2891.1, 652.8, 2911.0, 834.1), (2780.0, 975.6, 2893.0, 995.6),
                          (2175.2, 1083.9, 2208.4, 1163.6), (2175.2, 1290.8, 2208.4, 1375.4),
                          (463.2, 1476.9, 686.4, 1709.6), (957.9, 1476.9, 1135.5, 1496.9),
                          (2268.2, 1489.3, 2288.1, 1653.6), (775.6, 1881.4, 1045.3, 1901.4),
                          (1793.5, 1881.4, 2063.1, 1901.4), (1141.2, 760.1, 1201.0, 879.7)],
            "lado_max_pt": 20.0, "madeira": 0.92, "tons": (0.86, 1.06), "contorno": (34, 50, 68),
            "contorno_px": 0.5, "sombra": {"dist_m": 0.04, "sig_m": 0.025, "forca": 0.30}, "semente": 91}
# As projeções (item 15), em tracejado, só nestas zonas (pt): sobre os pisos claros, o traço cinza-escuro (os dois X do
# banho master); sobre o granito e as plantas, cinza-claro (os X da garagem e da faixa abaixo dela, o da área descoberta
# e o do jardim do lavabo, e o tracejado da cobertura na faixa de cima da garagem, na ARQ_ELEMENTOS FIXOS). Os
# retângulos com diagonal da DOC_LINHAS (armários até o teto) não entram (seção 7).
PROJECOES_D = [(604.7, 1829.2, 790.8, 1880.5)]
PROJECOES_CLARAS_D = [(2371.7, 549.3, 2922.4, 672.7), (2409.7, 981.3, 2879.7, 1090.5), (1949.2, 748.7, 2120.1, 881.6),
                      (2351.8, 1363.0, 2451.5, 1501.6)]
COBERTURA_D = [(2371.7, 615.8, 2912.9, 672.7)]
PROJECOES_TRACO_D = {"pisos": {"cor": (92, 92, 94), "forca": 0.9, "larg": 1.4},
                     "claras": {"cor": (214, 214, 212), "forca": 0.95, "larg": 1.4}}
# As peças do PDF que ficam como no render aprovado: o estar da suíte 3 (no PDF da Casa D, o sofá está na INS_INSTALAÇÕES
# HIDRÁULICAS e a mesa de centro na DOC_LINHAS; só o tapete, da ARQ_LAYOUT, entrava, e cobria os dois)
FORA_PECAS_D = [(2060.0, 1495.0, 2256.0, 1640.0)]
# os dois vasos do hall, junto aos brises, e a planta sobre a bancada gourmet (objetos de 15/10, item 22): as plantas do
# render (no PDF, a da bancada é um contorno de traço)
VASOS_D = [(2117.6, 1089.9, 2186.9, 1153.8), (2117.7, 1299.9, 2187.0, 1363.8), (1276.9, 681.3, 1315.9, 715.5)]
# As cubas que o PDF da Casa D desenha sem o aro (seção 6, todas em louça branca): as duas do banho master (retângulos
# soltos na bancada), a do lavabo (só a torneira no PDF; a bacia no lugar da do render) e a do WC DCE (de parede, só
# contorno). Entram com as outras, pela rotina das cubas das bancadas.
CUBAS_EXTRA_D = {"Terreo": [(656.6, 1717.6, 685.0, 1740.7), (709.6, 1717.6, 738.0, 1740.7),
                            (2332.8, 1382.0, 2349.9, 1414.3), (2150.0, 759.9, 2166.6, 783.2)]}
_cubas_bancada_b = F.cubas_bancada


def cubas_bancada_d(Q):
    return sorted(set(_cubas_bancada_b(Q)) | set(CUBAS_EXTRA_D.get(Q.chave, [])))
NAO_TAPETE_D = []
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
    C.jardins_c = jardins_d
    F.ROTULOS_F = dict(F.ROTULOS_F, livres=("JARDIM",), textos={}, pontos=ROTULOS_PONTOS_D)
    F.BLOCOS_F = BLOCOS_D
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
    cor, al = blocos.bloco("banqueta_linho", B.BANQUETAS_B["d_m"] * Q.px_m / 0.45)
    for _ in range(q["giro"] // 90):
        cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
    al = np.clip(al, 0, 1).astype(np.float32)
    h, w = al.shape
    d_ = s["dist_m"] * Q.px_m
    out = img.astype(np.float32)
    tampo = Q.preencher(lambda d: d.get("layer") == "ARQ_BANCADAS" and d.get("fill"), fs=False)
    for cx, cy in cs:
        f = int(np.ceil(d_ + 4 * s["sig_m"] * Q.px_m)) + 2
        X0, Y0 = int(cx - w / 2) - f, int(cy - h / 2) - f
        Wr, Hr = w + 2 * f, h + 2 * f
        Mt = np.float32([[1, 0, cx - w / 2 - X0], [0, 1, cy - h / 2 - Y0]])
        livre = 1 - tampo[Y0:Y0 + Hr, X0:X0 + Wr]
        a = cv2.warpAffine(al, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        c = cv2.warpAffine(cor.astype(np.float32), Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Wr, Hr)), (0, 0),
                              s["sig_m"] * Q.px_m) * s["forca"] * livre
        a = a * livre
        reg = out[Y0:Y0 + Hr, X0:X0 + Wr]
        reg *= (1 - sb * (1 - a))[..., None]
        out[Y0:Y0 + Hr, X0:X0 + Wr] = reg * (1 - a[..., None]) + c * a[..., None]
    print(f"    ilha gourmet: {len(cs)} banquetas de linho da biblioteca nos desenhos do PDF, entrando sob o tampo")
    return np.clip(out, 0, 255).astype(np.uint8)


def biblioteca_d(Q, img):
    out = np.ascontiguousarray(img.copy())
    with F.em_quadro(Q):
        if Q.chave == "Terreo":
            out = B.cooktops_b(out)
            out = banquetas_d(Q, out)
    return out


def carros_d(Q, img, M):
    """Os 3 carros da R12 (prata, 4,70 x 1,85 m, alinhados), como `final3840_casab.carros`, com a silhueta do modelo
    achada pelo que foge do granito em volta (a borda da janela)."""
    from scipy import ndimage
    q = CARROS_D
    r = dict(AJ.CARROS_A["r12"], centros_pdf=q["centros_pdf"])
    ap = cv2.imread(str(CASA_D / Q.q["aprovada"]))
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = ap[wy0:wy1, wx0:wx1].astype(np.float32)
    borda = np.concatenate([reg[:, :6].reshape(-1, 3), reg[:, -6:].reshape(-1, 3)])
    car = np.abs(reg - np.median(borda, axis=0)).max(axis=2) > q["foge"]
    m = cv2.morphologyEx(car.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    sil = ndimage.binary_fill_holes(lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    sil = cv2.erode(sil.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    qa = AJ.CARROS_A
    Y = reg.mean(axis=2)
    lanterna = (reg[..., 2] - reg[..., 0] > qa["lanterna"][0]) & (reg[..., 2] > qa["lanterna"][1]) & \
        (reg[..., 2] - reg[..., 1] > qa["lanterna"][0])
    pq, alvo = r["quantis"]
    Yn = np.interp(Y, np.percentile(Y[sil & ~lanterna], pq), alvo)
    prata = np.where((sil & ~lanterna)[..., None], Yn[..., None] * np.float32(r["tom"]), reg)
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
        c = cv2.warpAffine(prata, Mw, (Q.W, Q.H), flags=cv2.INTER_CUBIC)
        c = cv2.addWeighted(c, 1.5, cv2.GaussianBlur(c, (0, 0), 1.2), -0.5, 0)
        d_ = 0.08 * Q.px_m
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Q.W, Q.H)), (0, 0),
                              0.06 * Q.px_m) * (1 - a) * 0.38
        out *= (1 - sb)[..., None]
        out = out * (1 - a[..., None]) + c * a[..., None]
    print(f"    garagem (R12): {len(r['centros_pdf'])} carros prata de {r['comprimento_m']:.2f} x {r['largura_m']:.2f} m "
          f"(o modelo: o carro branco do render), alinhados, com a borda limpa e a sombra curta")
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
# 7. os boxes de correr dos banhos 1, 2 e 3 e do WC DCE em vidro contínuo, com as faces finas, a sombra curta e o trilho
#    (`final3840_casaa.boxes`); as folhas do PDF, pareadas por box (`AJ.folhas_box` juntava as dos três banhos, que estão
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
#    fechava o piso livre e devolvia o rótulo para dentro do box;
# 13. a cama do DCE com a roupa de cama da biblioteca, como no DCE 1 do Subsolo (`cama_dce_d`);
# 14. o banco do estar da varanda gourmet (o retângulo de cantos redondos da DOC_LINHAS E PROJEÇÕES, 0,60 x 1,80 m), em
#    madeira, sem encosto, como o da varanda da Casa E: a madeira da mesa da suíte 3/escritório (o veio no comprido; a
#    textura do piso de madeira trazia as juntas das réguas e o banco saía xadrez), um pouco mais escura, em 4 ripas;
# 15. a prateleira de vinhos da adega na parede do fundo (a da direita), como na Casa C (`C.adega_c`).
MATERIAIS_TD = {"granito": [(2320.0, 1370.0, 2362.0, 1492.0)],                                        # o lavabo
                "travertino": [(628.0, 1705.0, 766.0, 1750.0), (910.0, 1694.0, 954.0, 1770.0),
                               (1885.0, 1694.0, 1971.0, 1770.0),                # banho master, banhos 1, 2 e 3
                               (1360.0, 640.0, 1500.0, 673.0)],                 # o banho gourmet (pedido de 27/10)
                "granito_escuro": [(1200.0, 675.0, 1430.0, 727.0), (1255.0, 804.0, 1458.0, 881.0),
                                   (1598.0, 575.0, 1818.0, 620.0),
                                   (1660.0, 680.0, 1806.0, 750.0)],               # gourmet e cozinha, bancada e ilha
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
                                                      ("ao lado do banho master", (872.5, 1710.3, 906.5, 1880.3), "esquerda")]}
BANCO_VARANDA_TD = {"pt": (1263.0, 1196.9, 1297.0, 1298.9), "raio_pt": 5.7, "ripas": 4, "madeira": 0.80,
                    "fonte_pt": (2125.0, 1705.0, 2166.0, 1811.0),       # o tampo da mesa da suíte 3/escritório
                    "junta": (70, 92, 118), "larg_junta": 0.35, "forca_junta": 0.45, "contorno": (60, 72, 88),
                    "larg_contorno": 0.45, "sombra": {"dist_m": 0.05, "sig_m": 0.035, "forca": 0.32}, "ss": 4}
ADEGA_TD = dict(C.ADEGA_C, pt=(2241.6, 987.4, 2258.6, 1083.8), modulos=2)
ESCADA_DESCIDA_TD = {"d_pt": (957.0, 1449.5),                # o meio do degrau 16 (o D do PDF, na ponta do degrau)
                     "d_blocos_pt": (588.7, 1108.0)}          # o meio do bloco de cima da cascata (574,2 a 603,2 pt)
SETA_TD = {"ponta": (2462, 1068)}
ROTULOS_TD = {"pontos": {"WC DCE TÉRREO": (2195.0, 790.0)}, "folga_px": 4}


def piso_estratos_d(Q, img, m, nome, forca, sig_m, semente, **kw):
    if nome == "travertino" and kw.get("bruto") == "estratos":
        return C.piso_textura_c(Q, img, m, nome, forca, sig_m, semente, **kw)
    return piso_textura_d(Q, img, m, nome, forca, sig_m, semente, **kw)


def _dentro_td(r, zonas):
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    return any(z[0] <= cx <= z[2] and z[1] <= cy <= z[3] for z in zonas)


def bancadas_terreo_d(Q, img):
    """As bancadas com a borda e a sombra (E9) e os materiais do Térreo aprovado da Casa C, peça a peça; as cubas
    esculpidas (granito no lavabo, travertino nos banhos e no banho gourmet) no lugar da louça; a branca (WC DCE), de
    parede, por cima da pedra."""
    import final3840_casaa as FA
    mt = MATERIAIS_TD
    brancas = [tuple(round(v, 1) for v in r) for r in mt["cubas_brancas"]]
    cubas = [c for c in cubas_bancada_d(Q) if tuple(round(v, 1) for v in c) not in brancas]
    gs = {k: [(Q.p2q(*z[:2]), Q.p2q(*z[2:])) for z in mt[k]] for k in ("granito", "travertino", "granito_escuro")}

    def pedra(Q_, comp):
        ys, xs = np.nonzero(comp)
        cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
        for k in ("granito", "granito_escuro", "travertino"):
            if any(a[0] <= cx <= b[0] and a[1] <= cy <= b[1] for a, b in gs[k]):
                return k
        return None

    def cuba(Q_, out, r):
        return F.cuba_esculpida(Q_, out, r, "granito" if _dentro_td(r, mt["granito"]) else "travertino")
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
    print(f"    bancadas: lavabo em granito marrom com a cuba esculpida em granito; banho master, banhos 1, 2 e 3 e "
          f"banho gourmet em travertino bruto com a cuba esculpida em travertino; gourmet e cozinha em granito marrom "
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


def boxes_terreo_d(Q, img):
    """O box do banho gourmet (no granito) na faixa cinza-clara, como estava (`F.boxes_granito`); os de correr dos
    banhos 1, 2 e 3 e do WC DCE em vidro contínuo (`final3840_casaa.boxes`), com as folhas pareadas por box. Antes, a
    faixa tracejada da base, ao longo de cada box, recebe o piso logo acima."""
    import final3840_casaa as FA
    out = F.boxes_granito(Q, img).copy()
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
        return C.adega_c(Q, out)
    finally:
        C.ADEGA_C = ga


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


def projecoes_terreo_d(Q, img):
    """As projeções do PDF em tracejado (item 15 de 22/10), como desde 25/10 (antes na etapa das escadas)."""
    out = np.ascontiguousarray(img.copy())
    with F.em_quadro(Q):
        pa = AJ.PROJECOES_A
        n = 0
        try:
            for zonas, t, camada in ((PROJECOES_D, PROJECOES_TRACO_D["pisos"], "DOC_LINHAS E PROJEÇÕES"),
                                     (PROJECOES_CLARAS_D, PROJECOES_TRACO_D["claras"], "DOC_LINHAS E PROJEÇÕES"),
                                     (COBERTURA_D, PROJECOES_TRACO_D["claras"], "ARQ_ELEMENTOS FIXOS")):
                AJ.PROJECOES_A = dict(pa, larg_px=pa["larg_px"] * Q.W / 2000 * t["larg"], cor=t["cor"],
                                      forca=t["forca"])
                out, k = B.linhas_pdf(out, "Terreo", zonas, camada)
                n += k
        finally:
            AJ.PROJECOES_A = pa
    print(f"    projeções do PDF em tracejado ({n} traços): os X do banho master, da garagem, da área descoberta e do "
          f"jardim do lavabo, e a cobertura da garagem")
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
    saem de novo, nos mesmos lugares, sobre o fundo sem o tracejado. O WC DCE TÉRREO parte do piso livre, e os arcos
    das portas saem dos obstáculos (como em `rotulos_sub_d`); os guarda-roupas novos, o banco e a prateleira da adega
    entram como obstáculo."""
    rot = B.rotulos_casab(Q.pg, Q.p2q2000)
    rf = F.ROTULOS_F
    obst = [r for _, r, _ in GUARDA_ROUPAS_TD["pecas"]] + [BANCO_VARANDA_TD["pt"], ADEGA_TD["pt"]]
    pontos = dict(rf["pontos"].get(Q.chave, {}), **ROTULOS_TD["pontos"])
    F.ROTULOS_F = dict(rf, pontos=dict(rf["pontos"], **{Q.chave: pontos}),
                       obstaculos_pt=dict(rf.get("obstaculos_pt", {}), **{Q.chave: obst}))
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
    fora = CARROS_PT + cooktops + FORA_PECAS_D + VASOS_D + camas + BANCOS_D + [BANQUETAS_D["caixa_pt"]] + chuv
    # sob os carros, a legenda tem o contorno deles (traços): ali tudo é granito, para o piso não guardar o desenho
    for r in CARROS_PT:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        Q.chapada[y0:y1, x0:x1] = (50, 66, 90)
    F.piso_textura = piso_estratos_d
    F.VASOS_COR = dict(F.VASOS_COR, Terreo=VASOS_TD)
    cinza = F.PAREDES_F["cinza"]
    return [
        ("pisos", lambda im: F.pisos(Q, im, incluir={"granito": CARROS_PT}, bruto={"travertino": "estratos"})),
        ("bordas", lambda im: B.bordas_grama(im, chave)),
        ("vegetacao", lambda im: C.vegetacao_c(Q, im, M)),
        ("bancadas", lambda im: bancadas_terreo_d(Q, im)),
        ("pecas", lambda im: C.pecas_c(Q, im, ini, fora, camas + NAO_TAPETE_D)),
        ("tampas", lambda im: cama_dce_d(Q, C.pecas_do_render(Q, C.camas_render(Q, F.tampas_vasos(Q, C.restos_piso(
            Q, im, ini, FORA_PECAS_D)), ini), ini, VASOS_D, C.verde, "hall e gourmet: as plantas em vaso"))),
        ("vasos", lambda im: F.vasos_cor(Q, im)),
        ("biblioteca", lambda im: biblioteca_terreo_d(Q, im)),
        ("carros", lambda im: carros_d(Q, im, M)),
        ("chuveiros", lambda im: chuveiros_terreo_d(Q, im)),
        ("boxes", lambda im: boxes_terreo_d(Q, im)),
        ("paredes", lambda im: brises_madeira(Q, F.paredes(Q, im, cor=cinza))),
        ("soleiras", lambda im: C.soleira_elevador(Q, F.soleiras(Q, im))),
        ("esquadrias", lambda im: pos_esquadrias_d(Q, F.esquadrias_terreo(Q, im, parede=cinza), im)),
        ("cortinas", lambda im: F.cortinas(Q, im, paredes_pdf=True)),
        ("escadas", lambda im: escadas_terreo_d(Q, im)),
        ("projecoes", lambda im: projecoes_terreo_d(Q, im)),
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
        FA.travertino_bruto = C.travertino_bruto_tc     # o travertino em estratos nas bancadas e cubas (como na Casa C)
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
# 5. o box de correr do WC DCE em vidro contínuo, com as faces finas, a sombra curta e o trilho (E5, `final3840_casaa.
#    boxes`); antes, a faixa cinza tracejada da base e do render sai, refeita com o granito logo acima;
# 6-7. as bancadas com a borda no tom escurecido da pedra e a sombra curta (E9) e os materiais da recomendação: o WC DCE
#    como o BH serviço das Casas B e C (bancada em granito marrom no tom do piso, levemente escurecido, a cuba de
#    semiencaixe e o vaso brancos, a torneira cromada); o vestiário como o BH academia da Casa C (bancada em granito
#    marrom, a cuba esculpida em granito marrom na bacia do PDF, a torneira cromada na prateleira de trás, o vaso marrom).
#    No PDF do Subsolo as bancadas são só traços (a ARQ_BANCADAS sem preenchimento): entram pelos retângulos (pt);
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
VASOS_SUB_D = [((1065.6, 1770.6, 1094.7, 1790.6), "marrom")]          # o do WC do vestiário; o do WC DCE fica branco
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
                    "Terreo": dict(POS_ESQUADRIAS_SUB_D, paredes=dict(POS_ESQUADRIAS_SUB_D["paredes"], fora=[]), pecas=[])}


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
    # o vestiário: a bancada em granito marrom (o piso é Bege Bahia), a cuba esculpida em granito na bacia do PDF, a
    # torneira na prateleira de trás, junto à parede
    out = FA.bancada_pedra(Q, out, v["bancada"], lambda tl: granito(tl, v["semente"]), q["borda"], q["larg_px"],
                           q["sombra"])
    out = np.ascontiguousarray(np.clip(F.cuba_granito(Q, out, v["cuba"]), 0, 255).astype(np.uint8))
    out = FA.torneira(Q, out, v["torneira"], v["base"])
    for c in CHUVEIROS_SUB_D:
        out = FA.chuveiro(Q, out, c)
    print(f"    WC DCE: bancada em granito marrom levemente escurecido, cuba e vaso brancos, torneira; vestiário: bancada e "
          f"cuba esculpida em granito marrom, torneira; {len(CHUVEIROS_SUB_D)} chuveiros na placa cromada com o braço")
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
        ("soleiras", lambda im: nicho_d(Q, C.soleira_elevador(Q, F.soleiras(Q, im)))),
        ("esquadrias", lambda im: pos_esquadrias_d(Q, portas_academia_sub_d(Q, C.janelas_s(
            Q, B.esquadrias_final(im, chave, Q.pg, Q.p2q, Q.px_m, parede=cinza), JANELAS_SUB_D)), im)),
        ("escadas", lambda im: escada_sub_d(Q, im)),
        ("hachura", lambda im: AJ.subsolo_hachurado(im, peg, Q.px_m)),
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

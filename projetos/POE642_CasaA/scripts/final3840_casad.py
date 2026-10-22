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


def piso_textura_d(Q, img, m, nome, forca, sig_m, semente):
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
    novo = _piso_textura_b(Q, img, m, nome, forca, sig_m, semente)
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
BLOCOS_D = dict(F.BLOCOS_F, caixa_pt=(300.0, 800.0, 610.0, 1280.0), triangulos_pt=[(604.0, 1108.0, "esquerda")])
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
    F.ROTULOS_F = dict(F.ROTULOS_F, livres=("JARDIM",), textos={}, pontos={})
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
# As escadas (R14) e as projeções
def escadas_d(Q, img):
    from retoque_terreo_casae import escada_linhas
    out = np.ascontiguousarray(img.copy())
    if Q.chave == "Terreo":
        out = escada_linhas(out, None, ESCADA_T, p2r=Q.p2q)
        out = F.degraus_blocos(Q, out)
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
        print(f"    projeções do PDF em tracejado ({n} traços): os X do banho master, da garagem, da área descoberta e "
              f"do jardim do lavabo, e a cobertura da garagem")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# A final inteira
def passos_terreo_d(Q, ini, M):
    chave = "Terreo"
    cooktops = [(c["pt"][0] - 2, c["pt"][1] - 2, c["pt"][2] + 2, c["pt"][3] + 2) for c in COOKTOPS_D]
    camas = [c[1] for c in CAMAS_D["camas"]]
    fora = CARROS_PT + cooktops + FORA_PECAS_D + VASOS_D + camas + BANCOS_D + [BANQUETAS_D["caixa_pt"]]
    # sob os carros, a legenda tem o contorno deles (traços): ali tudo é granito, para o piso não guardar o desenho
    for r in CARROS_PT:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        Q.chapada[y0:y1, x0:x1] = (50, 66, 90)
    return [
        ("pisos", lambda im: F.pisos(Q, im, incluir={"granito": CARROS_PT})),
        ("bordas", lambda im: B.bordas_grama(im, chave)),
        ("vegetacao", lambda im: C.vegetacao_c(Q, im, M)),
        ("bancadas", lambda im: C.bancadas_c(Q, im)),
        ("pecas", lambda im: C.pecas_c(Q, im, ini, fora, camas + NAO_TAPETE_D)),
        ("tampas", lambda im: C.pecas_do_render(Q, C.camas_render(Q, F.tampas_vasos(Q, C.restos_piso(
            Q, im, ini, FORA_PECAS_D)), ini), ini, VASOS_D, C.verde, "hall e gourmet: as plantas em vaso")),
        ("biblioteca", lambda im: biblioteca_d(Q, im)),
        ("carros", lambda im: carros_d(Q, im, M)),
        ("boxes", lambda im: F.boxes_granito(Q, im)),
        ("paredes", lambda im: paredes_d(Q, im)),
        ("soleiras", lambda im: C.soleira_elevador(Q, F.soleiras(Q, im))),
        ("esquadrias", lambda im: F.esquadrias_terreo(Q, im)),
        ("cortinas", lambda im: F.cortinas(Q, im)),
        ("escadas", lambda im: escadas_d(Q, im)),
        ("rotulos", lambda im: F.rotulos(Q, im, B.rotulos_casab(Q.pg, Q.p2q2000), Q.q["ajustes"],
                                         granito=A.granito(im, Q.q.get("granito_lum_max", 125)))),
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
        passos = passos_terreo_d(Q, ini, M)
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
# terraço; cheia até a marca de corte do PDF do Subsolo (o zigue-zague no degrau 7) e esmaecida depois, com os bocéis e
# as sombras; o triângulo no degrau 1, apontando para a direita (a subida)
ESCADA_S = dict(ESCADA_T, nome="de 16 degraus, do pátio ao terraço", inicio="esquerda", viva="esquerda",
                apos="esmaecida",
                corte=[(785.0, 1415.5), (801.4, 1445.7), (809.9, 1445.7), (796.9, 1453.2), (805.4, 1453.2),
                       (821.5, 1483.5)])
# Os aparelhos da academia (esteiras, bicicletas e supinos) ficam os da final aprovada de 15/10: pelo PDF saíam
# silhuetas cinza chapadas, sem a lona da esteira nem as barras dos supinos (no tamanho do PDF, já conferido). Uma
# caixa por grupo (as bicicletas, as esteiras e os supinos): numa caixa só, a sauna e o vestiário entravam junto e o
# Bege Bahia quase neutro da final antiga voltava por cima do novo
FORA_PECAS_S = [(672.1, 1636.5, 743.3, 1721.9), (957.0, 1622.2, 1075.6, 1726.7), (1203.8, 1598.5, 1298.8, 1864.3)]
# A cama do DCE 1 fica a da final aprovada (resposta 5, "Os do render")
# A bancada do vestiário com a cuba: no PDF do Subsolo são só traços (a ARQ_BANCADAS sem preenchimento e a cuba sem
# louça), e saíam o contorno e o piso por dentro; ficam as da final aprovada (a cuba em louça branca na pedra, item 37
# de 15/10)
CUBA_VESTIARIO_S = [(924.0, 1816.5, 952.5, 1857.0)]
CAMAS_S = {"borda": 1.7, "ss": 4, "semente": 41, "camas": [("DCE 1", (846.0, 1203.9, 902.7, 1317.3), "baixo",
                                                             "solteiro")]}


def pegada_subsolo(Q):
    """O que fica em cor cheia no Subsolo (R2; resposta 6, "Hachura"): o Subsolo e o pátio, o que a legenda pinta (os
    ambientes, o pátio e a escada, com as paredes), fechado e sem furos. A faixa verde de 15/10 fica de fora (entra na
    hachura do Térreo final). 0 a 1, no quadro."""
    from scipy import ndimage
    nb = (Q.chapada.min(axis=2) < 250).astype(np.uint8)
    nb = cv2.morphologyEx(nb, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb, 8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 2000])
    m = ndimage.binary_fill_holes(m)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6)
    return np.maximum(a, m * 1.0)


def escadas_s(Q, img):
    from retoque_terreo_casae import escada_linhas
    return escada_linhas(np.ascontiguousarray(img.copy()), None, ESCADA_S, p2r=Q.p2q)


def passos_subsolo_d(Q, ini):
    chave = "Subsolo"
    peg = pegada_subsolo(Q)
    dentro = peg > 0.5
    AJ.SUBSOLO_R2 = dict(AJ.SUBSOLO_R2, terreo=CASA_D / "renders" / "POE642_CasaD_PH_Terreo_final_rotulos.png")
    C.CAMAS_C, C.BANCOS_C = CAMAS_S, []
    camas = [c[1] for c in CAMAS_S["camas"]]
    return [
        ("pisos", lambda im: F.pisos(Q, im, dentro=dentro)),
        ("bancadas", lambda im: C.bancadas_c(Q, im)),
        ("pecas", lambda im: F.pecas_pdf(Q, im, ini, fora=FORA_PECAS_S + CUBA_VESTIARIO_S + camas, camas=camas)),
        ("aparelhos", lambda im: C.pecas_do_render(
            Q, C.pecas_do_render(Q, im, ini, FORA_PECAS_S, C.neutro, "academia: os aparelhos"), ini, CUBA_VESTIARIO_S,
            lambda reg: np.ones(reg.shape[:2], bool), "vestiário: a bancada com a cuba branca")),
        ("tampas", lambda im: C.camas_render(Q, F.tampas_vasos(Q, im), ini)),
        ("paredes", lambda im: F.paredes(Q, im)),
        ("soleiras", lambda im: C.soleira_elevador(Q, F.soleiras(Q, im))),
        ("esquadrias", lambda im: B.esquadrias_final(im, chave, Q.pg, Q.p2q, Q.px_m)),
        ("escadas", lambda im: escadas_s(Q, im)),
        ("hachura", lambda im: AJ.subsolo_hachurado(im, peg, Q.px_m)),
        ("rotulos", lambda im: F.rotulos(Q, im, B.rotulos_casab(Q.pg, Q.p2q2000), Q.q["ajustes"],
                                         granito=A.granito(im, Q.q.get("granito_lum_max", 125)))),
    ]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(PAVIMENTOS_D))
    ap.add_argument("--de", default=None, help="recomeça desta etapa (pisos, bordas, vegetacao, bancadas, pecas, ...)")
    ap.add_argument("--ate", default=None, help="para nesta etapa")
    a = ap.parse_args()
    final_3840_d(a.pavimento, de=a.de, ate=a.ate)

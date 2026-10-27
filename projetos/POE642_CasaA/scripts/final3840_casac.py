#!/usr/bin/env python3
"""A final da Casa C refeita na resolução da prancha (3840 px, ~59,7 px/m), pelo motor da Casa B.

Pedido do usuário (22/10/26), depois dos mapas do pente fino da Casa C (`conferencia_casac.py`): "Casa C" e, às
perguntas dos mapas, "1. BANCO EM BRONZE FOSCO; 2. OK; 3. DE ACORDO; 4. PEDRA AREIA; 5. EM 3840 PX". Valem os 23 itens
do Térreo e os 13 do Subsolo dos mapas, com as respostas:
- o L junto ao deck fica banco em bronze fosco (como o da Casa B);
- no Subsolo, em cor cheia o Subsolo, o pátio, os degraus largos e o caminho; o resto do lote na hachura do Térreo final;
- os triângulos da R14: no Térreo, na escada estreita junto ao deck (apontando para a esquerda) e no degrau 10 dos
  largos (apontando para cima); no Subsolo, no degrau 1 dos largos (para baixo) e no 11 da estreita (para a direita);
- as bancadas e as ilhas em pedra areia humanizada, com as cubas brancas (como na Casa B);
- tudo desenhado na resolução da prancha, guardando as decisões de 14/10 (os itens 1 a 25 do retoque da Casa C).
Depois, vendo a final: "PODE MANTER O JOGO DE CAMA QUE ESTAVA ANTES." e "MANTENHA OS BANCOS QUE ESTAVAM EM FRENTE AS
CAMAS TAMBÉM": as camas e os bancos ao pé delas são os do render aprovado (`camas_render`), sem a roupa de cama
da biblioteca.

A Casa C tem a mesma folha, o mesmo recorte, a mesma escala e as mesmas cores de legenda da Casa B: as rotinas do
`final3840_casab.py` (e as dos ajustes que ele chama, `ajustes_casab.py`) servem como estão. `contexto_c()` aponta os
dois módulos para a Casa C (pastas, config, PDF, render, base chapada) e troca os parâmetros que são da casa (as
coordenadas em pt do PDF da Casa C: camas, guarda-roupas, cooktops, inox, elevador, carros, jardins, guarda-corpos,
escadas, projeções, rótulos). A imagem de partida é o render retocado e aprovado de 14/10 (2000 px), levado ao quadro.

Auditoria de 26/10 no Subsolo (usuário: "ok, aplique a lista"): as paredes em cinza 80, o travertino bruto, as escadas
com o S e o sombreamento (a estreita com a linha de corte e nevoada depois dela), o box de correr, os materiais do BH
academia, os rótulos, os chuveiros cromados e a cabine do elevador em aço (`passos_subsolo_c`).

Uso (da pasta POE642_CasaA/scripts/):
  python3 final3840_casac.py Terreo              # a final do Térreo com os rótulos
  python3 final3840_casac.py Terreo --de pecas   # recomeça de uma etapa (as anteriores ficam em cache)
  python3 final3840_casac.py Subsolo             # depois do Térreo (a hachura vem do Térreo final)
Saída: `POE642_CasaC/renders/POE642_CasaC_PH_<Pavimento>_final_rotulos.png`, que vai ao `rodape_entrega.py --no-quadro`.
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

B, AJ, A = F.B, F.AJ, F.A
RAIZ = B.RAIZ
CASA_C = RAIZ / "POE642_CasaC"
CONFIG_C = CASA_C / "config_bases.json"
CACHE_C = Path(os.environ.get("POE642_CACHE", tempfile.gettempdir())) / "poe642_casac_etapas"

PAVIMENTOS_C = {
    "Terreo": {"render": "renders/POE642_CasaC_PH_Terreo_v3_retocado_barlavento.png",
               "aprovada": "renders/POE642_CasaC_PH_Terreo_v3_retocado_barlavento.png",
               "pdf": "642 - TÉRREO - CASA C.pdf",
               "sem_tela": "bases/POE642_CasaC_BASE_Terreo_v3_texturas.png",
               "chapada": "bases/POE642_CasaC_BASE_Terreo_v2_16x9.png",
               "ajustes": []},
    "Subsolo": {"render": "renders/POE642_CasaC_PH_Subsolo_v3_retocado.png",
                "aprovada": "renders/POE642_CasaC_PH_Subsolo_v3_retocado.png",
                "pdf": "642 - SUBSOLO - CASA C.pdf",
                "sem_tela": "bases/POE642_CasaC_BASE_Subsolo_v3_texturas.png",
                "chapada": "bases/POE642_CasaC_BASE_Subsolo_v2_16x9.png",
                "ajustes": []},
}


# quadro comum de 2000 px -> render de 2000 (SIFT da base 16:9 contra o render): 232 pontos no Térreo (0,57 px), 43 no
# Subsolo (0,53 px)
AFIM_QR_C = {"Terreo": ((1.000123, -0.000059, 0.025942), (-0.000118, 0.998966, -2.757008)),
             "Subsolo": ((1.000793, 0.000492, -0.366251), (0.002727, 0.999693, -4.532169))}


# ----------------------------------------------------------------------------------------------------------------------
# Os parâmetros da Casa C (pt do PDF da Casa C; px do quadro de 3840 onde dito)
# Os pisos: as mesmas cores de legenda da Casa B, mais o Bege Bahia, que no Térreo da Casa C cobre o pátio, os degraus
# largos, o caminho, a escada estreita, os pisantes e os banhos 1, 2, 3 e master 2.
PISOS_C = {
    "Terreo": [
        ("travertino", [(202, 217, 220), (202, 218, 221)], 5, "travertino", 1.6, 3.0),
        ("vinílico", [(124, 162, 200)], 5, "vinilico", None, 1.0),
        ("granito", [(50, 66, 90)], 5, "granito", None, 1.5),
        ("Bege Bahia", [(232, 232, 232)], 5, "bege", None, 1.5),
        ("deck", [(99, 136, 174), (76, 106, 138)], 5, "deck", None, None),
        ("pedra portuguesa", [(85, 138, 185)], 3, "pedra", None, 1.5),
        ("grama", [(80, 145, 110)], 3, "grama", None, 3.0),
    ],
    "Subsolo": [
        ("travertino", [(202, 217, 220), (201, 217, 220)], 5, "travertino", 1.6, 3.0),
        ("Bege Bahia", [(232, 232, 232)], 5, "bege", None, 1.5),
        ("vinílico", [(124, 162, 200)], 5, "vinilico", None, 1.0),
    ],
}
# Os tons das escalas (itens 3, 6 e 7 do pente fino): o render de 14/10 tinha o granito escuro (~82, 61, 55), o Bege
# Bahia rosado (~229, 212, 198) e a grama clara (~105, 121, 64). A textura da biblioteca vai no tom dos mesmos pisos da
# final da Casa B (a referência): granito ~116, 87, 68; Bege Bahia ~230, 211, 187; grama ~84, 100, 43 (RGB). A luz do
# lugar fica (a mediana do piso é levada ao tom; as variações de luz e sombra ficam).
TONS_C = {"granito": (68, 87, 116), "bege": (187, 211, 230), "grama": (43, 100, 84)}       # BGR
_piso_textura_b = F.piso_textura


def piso_textura_c(Q, img, m, nome, forca, sig_m, semente, **kw):
    if nome == "travertino" and kw.get("bruto") == "estratos":
        # o travertino bruto em estratos (pedidos de 26/10, `travertino_estratos`), na luz do próprio piso
        ys, xs = np.nonzero(m)
        y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
        L = F.luz_robusta(img, m, sig_m * Q.px_m)
        novo = img.astype(np.float32).copy()
        novo[y0:y1, x0:x1] = L[y0:y1, x0:x1] * travertino_estratos(Q, y1 - y0, x1 - x0, semente)
        return novo
    novo = _piso_textura_b(Q, img, m, nome, forca, sig_m, semente, **kw)
    alvo = TONS_C.get(nome)
    if alvo is not None and m.any():
        med = np.median(novo[m], axis=0)
        novo = novo * (np.float32(alvo) / np.maximum(med, 1.0))
    return novo


# Os carros (R12): os 3 do PDF (ARQ_LAYOUT HUMANIZAÇÃO), prata, alinhados (o mesmo y), do tamanho de 4,70 x 1,85 m. O
# modelo é o carro prata do render (o do meio, na janela em px do render de 2000).
CARROS_PT = [(2481.0, 589.0, 2599.0, 851.0), (2639.0, 589.0, 2757.0, 851.0), (2821.0, 589.0, 2939.0, 851.0)]
# o granito do render (~82, 61, 55) é quase neutro: o carro é o px com R - B abaixo de 15 (na Casa B, 35)
CARROS_C = dict(B.CARROS_B, janela=(1395, 180, 1712, 352), modelo=1, neutro=15,
                centros_pdf=[(2540.1, 722.0), (2698.0, 722.0), (2880.2, 722.0)])
# As camas: o retângulo da cama no PDF e o lado da cabeceira. Usuário (22/10/26): "PODE MANTER O JOGO DE CAMA QUE
# ESTAVA ANTES": as camas ficam como no render aprovado de 14/10 (sem a roupa de cama da biblioteca); as peças do PDF
# delas não entram e, depois das peças (o tapete por baixo), o render volta no retângulo da cama, com a sombra curta.
CAMAS_C = {"borda": 1.7, "ss": 4, "semente": 41, "camas": [
    ("suíte master", (776.8, 776.1, 894.7, 900.2), "cima", "casal"),
    ("quarto 3", (1127.9, 586.7, 1241.3, 688.8), "dir", "casal"),
    ("quarto 2, de cima", (1249.8, 577.6, 1363.2, 634.3), "esq", "solteiro"),
    ("quarto 2, de baixo", (1249.8, 674.0, 1363.2, 730.7), "esq", "solteiro"),
    ("quarto 1", (1808.8, 606.0, 1932.9, 723.9), "dir", "casal"),
    ("quarto externo", (2774.8, 940.5, 2888.2, 997.2), "dir", "solteiro")]}
# Os bancos ao pé das camas (14/10, item 24), também como no render (usuário, 22/10/26: "MANTENHA OS BANCOS QUE ESTAVAM
# EM FRENTE AS CAMAS TAMBÉM"): suíte master, quarto 3, os dois do quarto 2 e quarto 1
BANCOS_C = [(790.4, 903.1, 881.1, 925.7), (1104.1, 592.4, 1126.8, 683.1), (1366.0, 580.5, 1383.0, 631.5),
            (1366.0, 679.7, 1383.0, 730.7), (1783.3, 619.6, 1805.9, 710.3)]
# Os guarda-roupas com cabides (R11): no PDF da Casa C são faixas brancas (sem preenchimento) com a diagonal da
# DOC_LINHAS; os trechos (pt), achados na base chapada, e o lado das portas
GUARDA_ROUPAS_C = {"ss": 4, "semente": 51, "pecas": [
    ("closet master 1, em cima", (737.6, 538.9, 889.5, 573.0), "baixo"),
    ("closet master 1, à direita", (856.3, 573.0, 889.5, 734.5), "esquerda"),
    ("closet master 1, embaixo", (737.6, 734.5, 889.5, 768.6), "cima"),
    ("quarto 3, em pé", (899.0, 641.4, 932.3, 734.5), "direita"),
    ("quarto 3, embaixo", (899.0, 734.5, 1003.5, 768.6), "cima"),
    ("quarto 2, em pé", (1559.9, 641.4, 1593.1, 734.5), "esquerda"),
    ("quarto 2, embaixo", (1488.7, 734.5, 1593.1, 768.6), "cima"),
    ("quarto 1, em pé", (1600.7, 641.4, 1634.9, 734.5), "direita"),
    ("quarto 1, embaixo", (1600.7, 734.5, 1706.1, 768.6), "cima"),
    ("closet master 2, à direita", (901.9, 1021.2, 935.1, 1112.3), "esquerda"),
    ("closet master 2, embaixo", (731.9, 1112.3, 935.1, 1145.6), "cima"),
    # auditoria de 26/10, item 11 (E2): o armário cortado do quarto externo (DOC_LINHAS E PROJEÇÕES, só com a diagonal)
    ("quarto externo", (2698.3, 943.3, 2729.5, 997.2), "direita")]}
# Os cooktops de 5 bocas (14/10, item 10): o da gourmet deitado (2 em cima, 3 embaixo); o da ilha da cozinha em pé, com
# 3 bocas na coluna da esquerda e 2 na da direita
# Pedidos de 26/10: os dois girados 180º ("gire o cooktop da varanda em 180º"; na ilha: "o cooktop precisa ser girado
# em 180º para ficar corretamente"), o da varanda gourmet de 0 para 180 e o da ilha de 90 para 270
COOKTOPS_C = [{"pt": (1188.3, 1264.3, 1238.2, 1292.6), "giro": 180},
              {"pt": (2057.7, 615.1, 2086.0, 664.9), "giro": 270}]
# As 4 banquetas da ilha da cozinha: os círculos (0,40 m) da ARQ_LAYOUT HUMANIZAÇÃO à esquerda da ilha, viradas para ela
BANQUETAS_C = {"caixa_pt": (2000.0, 590.0, 2035.0, 760.0), "giro": 270}
# O chuveiro externo do pisante (14/10, item 14): a ducha, o braço até o muro e a canopla do PDF
CHUVEIRO_C = {"ducha": (1000.4, 1942.0, 1011.6, 1953.2), "braco": (1005.3, 1946.5, 1006.7, 1968.8),
              "canopla": (1004.3, 1968.8, 1007.7, 1969.4)}
# Os guarda-corpos de vidro (item 13): as lâminas brancas de 2 cm da ARQ_ELEMENTOS FIXOS, nenhuma desenhada antes: o L da
# varanda master (7,2 m em cima e 9,7 m à esquerda, sobre o pátio), a borda de cima da varanda dos quartos e a da varanda 1
GUARDA_CORPOS_C = [(483.9, 460.8, 889.8, 462.0), (483.9, 460.8, 485.0, 1011.3), (1068.4, 460.8, 1422.7, 462.0),
                   (1771.4, 460.8, 1932.9, 462.0)]
# As projeções (item 15), em tracejado, só nestas zonas (pt): a claraboia da varanda master, as dos closets master 1 e
# 2, o X do box do BH master 2 (14/10, item 11), os X dos dois jardins de inverno e o da área de serviço descoberta. As
# diagonais dos armários e guarda-roupas não entram (seção 7), nem a divisa do lote, que já está.
# Bem visíveis (item 15): sobre os pisos claros, o traço cinza-escuro e um pouco mais largo que o da Casa A; sobre as
# plantas dos jardins e o granito da área descoberta, cinza-claro.
PROJECOES_C = [(562.9, 454.4, 790.8, 511.3), (771.8, 601.5, 814.5, 687.0), (790.8, 1043.0, 876.3, 1085.8),
               (695.9, 1085.8, 729.1, 1142.7),
               # auditoria de 26/10, item 14 (R8): a claraboia sobre o chuveiro e o vaso do BH master 1
               (590.0, 536.0, 730.0, 566.0)]
PROJECOES_JARDINS_C = [(1555.1, 990.8, 1811.5, 1365.9), (2215.0, 283.4, 2452.4, 459.1)]
PROJECOES_TRACO_C = {"pisos": {"cor": (92, 92, 94), "forca": 0.9, "larg": 1.4},
                     "jardins": {"cor": (214, 214, 212), "forca": 0.95, "larg": 1.4}}
# As peças do PDF que não entram (a decisão de 14/10, item 9: as banquetas sob o braço de baixo da bancada gourmet
# saem; no PDF são 7, quase todas sob o tampo) e as que, grandes e simples, não são tapete (o aparador comprido da
# circulação, 8,5 x 0,7 m)
FORA_PECAS_C = [(1070.0, 1312.0, 1342.0, 1345.0), (1880.0, 1495.0, 2130.0, 1746.0), (1490.0, 1490.0, 1880.0, 1760.0),
                (1120.0, 885.0, 1370.0, 1098.0)]
# os dois vasos junto ao sofá curvo do estar: as plantas do render (a da biblioteca saía com manchas claras em volta)
VASOS_C = [(2055.0, 1672.0, 2156.0, 1780.0)]
FORA_PECAS_C.extend(VASOS_C)
NAO_TAPETE_C = [(1455.4, 863.9, 1937.3, 903.6)]
# As esquadrias: no deck, no banco em L, na prainha, no spa e na piscina, as paredes estruturais da ARQ_PAREDE são
# brancas e finas como vidro (a base já as tirava, `zonas_excluidas` da config); não são esquadria. A zona cobre também
# as bordas de fora da piscina e o vidro da borda infinita: juntos, eles formavam uma esquadria do tamanho da piscina,
# e o redesenho clareava os degraus da prainha e as bordas. O vidro da borda infinita fica o do render (fino, cinza).
VIDROS_FORA_C = [(478.0, 1230.0, 938.0, 1800.0)]
# Os dois conjuntos do estar e o da sala TV ficam como no render aprovado (14/10, itens 7 e 8; acima, em
# `FORA_PECAS_C`): no PDF, o tapete orgânico da direita do estar é um desenho de 210 traços que as peças pintavam por
# cima do sofá curvo, e as poltronas e os sofás são só contorno (o tapete os cobria, e o sofá saía sem as almofadas).
# O tapete da sala TV (item 20) fica o do render, que já se distingue do travertino novo.
# As zonas dos móveis humanizados (seção 8, 22/10): o estar, a sala TV e as varandas
HUMANIZAR_C = [(1480.0, 1480.0, 2135.0, 1760.0), (1120.0, 880.0, 1365.0, 1095.0)]
# Os jardins (item 16): os três canteiros da floreira da legenda (o jardim de inverno 1, o 2 e o jardim 1), cada um na
# sala inteira; só plantas verdes da biblioteca, no tamanho real
JARDINS_C = {
    "terra": (38, 54, 40), "terra_ruido": 0.10,
    "forracao": {"nomes": ["arbusto_1", "arbusto_2", "arbusto_3"], "d_m": (0.40, 0.55), "passo_m": 0.32, "tom": 0.92},
    "canteiros": [
        ("jardim de inverno", (1775, 934, 2024, 1190), 21,
         [("costela_de_adao", 0.95, (0.22, 0.22), 0), ("planta_folhas_largas", 0.90, (0.76, 0.20), 90),
          ("palmeira_2", 1.30, (0.50, 0.50), 0), ("planta_folhas_largas", 0.85, (0.22, 0.78), 180),
          ("costela_de_adao", 0.90, (0.78, 0.80), 270), ("palmeira_3", 0.80, (0.50, 0.86), 0),
          ("arbusto_2", 0.75, (0.86, 0.50), 90), ("arbusto_1", 0.75, (0.14, 0.50), 0)]),
        ("jardim de inverno 2", (1892, 824, 2024, 918), 22,
         [("costela_de_adao", 0.80, (0.28, 0.45), 0), ("palmeira_3", 0.75, (0.72, 0.50), 90),
          ("arbusto_2", 0.55, (0.50, 0.30), 0)]),
        ("jardim 1", (1124, 839, 1230, 978), 23,
         [("palmeira_2", 1.10, (0.50, 0.50), 0), ("costela_de_adao", 0.75, (0.30, 0.22), 90),
          ("planta_folhas_largas", 0.70, (0.70, 0.80), 180), ("arbusto_1", 0.55, (0.25, 0.82), 0)])]}
FLOREIRA_COR = (58, 122, 79)
# Os degraus largos (item 12, R14): no PDF (ARQ_CONTRAPISO), numerados de 1 (junto ao pátio) a 10 (o patamar do
# caminho); no Térreo descem do caminho para o pátio (para cima na planta): cada bocel com a linha cinza suave e a
# sombra de ~10 cm no degrau de baixo (em cima dele); os dois em L, com a sombra à esquerda. (x0, y0, x1, y1, lado da
# sombra), em pt; e o triângulo no topo, no degrau junto ao patamar, apontando para cima.
DEGRAUS_LARGOS_T = {
    "bocels": [(226.5, y, 509.9, y, "cima") for y in (926.9, 955.5, 984.1, 1012.8, 1041.4, 1070.0, 1098.6)]
    + [(300.2, 1127.3, 509.9, 1127.3, "cima"), (328.5, 1155.9, 509.9, 1155.9, "cima"),
       (300.2, 1127.3, 300.2, 1269.3, "esquerda"), (328.5, 1155.9, 328.5, 1269.3, "esquerda")],
    "triangulos": [(419.2, 1135.5, "cima")]}
# A escada estreita (11 a 21): desce do deck para o caminho ("D" do PDF junto ao 21); o pé à esquerda, o triângulo no
# topo, junto ao deck, apontando para a esquerda
ESCADA_ESTREITA_T = {"nome": "estreita, do deck para o caminho", "pdf": (538.3, 1155.9, 708.4, 1240.9),
                     "bocels": [555.3 + 17.0 * k for k in range(9)], "corte": None, "baixo": "esquerda",
                     "inicio": "direita"}


def contexto_c():
    """Os módulos da Casa B passam a ler a Casa C: as pastas, a config, o PDF, o render e a base chapada, e os
    parâmetros que são da casa."""
    B.CASA_B = CASA_C
    B.CONFIG_B = CONFIG_C
    B.CACHE = CACHE_C
    B.PAVIMENTOS_B = PAVIMENTOS_C
    B.AFIM_QR_B = AFIM_QR_C
    # o gramado do render de 2000 px (o lote e uma amostra de grama sem plantas), para achar as plantas do motor
    B.GRAMA_B = dict(B.GRAMA_B, lote=(152, 26, 1830, 956), amostra=(1354, 778, 1562, 830))
    F.ETAPAS = CACHE_C / "final3840"
    B.contexto()
    F.PISOS = PISOS_C
    # as duas mesas de centro do estar estão na DOC_TEXTOS do PDF da Casa C (o resto da camada é desenho de peças)
    F.CAMADAS_PECAS = tuple(dict.fromkeys(F.CAMADAS_PECAS + ("DOC_TEXTOS",)))
    F.piso_textura = piso_textura_c
    F.arcos_porta = arcos_porta_c
    F.PECAS = dict(F.PECAS, humanizar=dict(F.PECAS["humanizar"], zonas_pt={"Terreo": HUMANIZAR_C}),
                   marcas=dict(F.PECAS["marcas"], fora_pt={}))
    F.SAUNA_F = {k: v for k, v in F.SAUNA_F.items() if k not in ("Terreo", "Subsolo")}
    F.PAREDES_F = dict(F.PAREDES_F, muros_pt={}, brises=dict(F.PAREDES_F["brises"], caixa_pt={}),
                       guarda_corpo=dict(F.PAREDES_F["guarda_corpo"], pt={"Terreo": GUARDA_CORPOS_C}, labio_pt={}))
    F.ESQUADRIAS_F = {"de_volta_pt": {}, "travertino_pt": {}, "ref_pt": {}}
    F.alfa_canteiros = alfa_canteiros_c
    F.CHUVEIRO_DECK = CHUVEIRO_C
    F.ROTULOS_F = dict(F.ROTULOS_F, livres=("JARDIM DE INVERNO", "JARDIM DE INVERNO 2", "JARDIM 1"), textos={},
                       pontos={})
    B.CARROS_B = CARROS_C
    B.CAMAS_B = CAMAS_C
    B.GUARDA_ROUPAS_B = GUARDA_ROUPAS_C
    B.COOKTOPS_B = COOKTOPS_C
    B.SOLEIRAS_B = dict(B.SOLEIRAS_B, sem=[])
    B.VIDROS_B = dict(B.VIDROS_B, fora=VIDROS_FORA_C)
    B.ROTULOS_FORA, B.ROTULOS_NOMES = [], []
    # o título da folha do Subsolo é "-1. 1º SUBSOLO": o filtro por "SUBSOLO" levava junto a VARANDA SUBSOLO
    A.FORA = tuple(f for f in A.FORA if f != "SUBSOLO") + ("1º SUBSOLO",)
    B.BORDAS = dict(B.BORDAS, pisos=list(B.BORDAS["pisos"]) + [(232, 232, 232)])
    F.VASOS_COR = dict(F.VASOS_COR, **VASOS_COR_C)


# ----------------------------------------------------------------------------------------------------------------------
# A imagem de partida: o render aprovado de 14/10 (2000 px), levado ao quadro da prancha pelo afim da base
def quadro_inicial_c(Q):
    from PIL import Image
    q = Q.q
    rd = CASA_C / q["render"]
    cache = CACHE_C / f"{Q.chave}_quadro_inicial.png"
    if cache.exists() and cache.stat().st_mtime > rd.stat().st_mtime:
        return cv2.imread(str(cache))
    r = Image.open(rd).convert("RGB")
    img = A.no_quadro_fixo(r, r, Q.base, Q.chave)
    CACHE_C.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(cache), img)
    return img


def tapetes_por_baixo(Q, camas):
    """Os tapetes do PDF (os preenchimentos grandes e simples, que não são cama) vão para o começo da ordem de pintura:
    no PDF da Casa C, o tapete da sala TV e o do estar vêm depois do sofá, das mesas e das poltronas, e as peças os
    pintavam por cima delas (o sofá e as mesas sumiam sob o tapete)."""
    q = F.PECAS
    n = 0
    for d in Q.desenhos:
        r = d["rect"]
        if d.get("layer") in F.CAMADAS_PECAS and d["type"] in ("f", "fs") and len(d["items"]) <= 5 \
                and r.width * r.height / 56.69 ** 2 >= q["tapete_m2"] \
                and not any(abs(r.x0 - c[0]) < 3 and abs(r.y0 - c[1]) < 3 for c in camas):
            d["seqno"] = -1
            n += 1
    print(f"    {n} tapetes do PDF por baixo das peças")


def pecas_c(Q, img, amostra, fora, camas):
    tapetes_por_baixo(Q, camas)
    return F.pecas_pdf(Q, img, amostra, fora=fora, camas=camas)


# ----------------------------------------------------------------------------------------------------------------------
# A vegetação e os jardins
def floreiras(Q):
    """Os canteiros da floreira da legenda: [(nome, alfa 0 a 1, caixa em px, semente, plantas)]."""
    fl = (Q.cor([FLOREIRA_COR], tol=6)).astype(np.uint8)
    fl = cv2.morphologyEx(fl, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    out = []
    for nome, (x0, y0, x1, y1), sem, plantas in JARDINS_C["canteiros"]:
        m = np.zeros_like(fl)
        m[y0 - 2:y1 + 2, x0 - 2:x1 + 2] = fl[y0 - 2:y1 + 2, x0 - 2:x1 + 2]
        a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5) * m
        out.append((nome, a, (x0, y0, x1, y1), sem, plantas))
    return out


def alfa_canteiros_c(Q):
    return np.max([a for _, a, *_ in floreiras(Q)], axis=0)


def sprite_limpo(cor, a, sig=1.2):
    """A planta da biblioteca sem a franja clara do recorte (pedidos de 26/10, nos jardins de inverno: "corrigir os
    erros dos contornos"): a borda do alfa mais justa e, na borda, a cor das folhas de dentro (não a do fundo branco da
    foto)."""
    a = np.clip((a - 0.25) / 0.75, 0, 1).astype(np.float32)
    dentro = (a > 0.92).astype(np.float32)
    num = cv2.GaussianBlur(cor * dentro[..., None], (0, 0), sig)
    den = cv2.GaussianBlur(dentro, (0, 0), sig)[..., None]
    viz = num / np.maximum(den, 1e-4)
    borda = ((a < 0.92) & (den[..., 0] > 0.02))[..., None]
    return np.where(borda, viz, cor).astype(np.float32), a


def jardins_c(Q, img):
    q = JARDINS_C
    out = np.ascontiguousarray(img.copy())
    sprite = B.planta_sprite

    def sprite_c(nome, d_m, px_m):
        cor, a, d_px = sprite(nome, d_m, px_m)
        return (*sprite_limpo(cor, a), d_px)
    B.planta_sprite = sprite_c
    try:
        return _jardins_c(Q, out)
    finally:
        B.planta_sprite = sprite


def _jardins_c(Q, out):
    q = JARDINS_C
    comum = {"terra": q["terra"], "terra_ruido": q["terra_ruido"], "forracao": q["forracao"]}
    feitos = np.zeros(out.shape[:2], np.float32)
    with F.em_quadro(Q):
        for nome, a, caixa, sem, plantas in floreiras(Q):
            antes = out
            out = B.canteiro(out, a, caixa, dict(comum, plantas=plantas, transbordo_m=0.0, semente=sem), Q.px_m, nome)
            # a limpeza das folhas fora deste canteiro (`B.canteiro`, passo 1) refazia as do jardim vizinho já pintado,
            # numa faixa escura e borrada (o alto do jardim de inverno, junto ao jardim de inverno 2; auditoria de
            # 26/10, item 16): o que já foi pintado volta
            k = feitos[..., None]
            out = np.clip(out * (1 - k) + antes.astype(np.float32) * k, 0, 255).astype(np.uint8)
            feitos = np.maximum(feitos, a)
    print("    jardins: os dois jardins de inverno e o jardim 1 na sala inteira, só plantas verdes da biblioteca")
    return out


def vegetacao_c(Q, img, M):
    import json as _json
    from retoque_terreo_casae import sprite_referencia, pousar_planta
    out = img.astype(np.float32)
    sombra = _json.loads((RAIZ / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    verde = Q.cor([F.BORDAS_GRAMA], tol=10)
    fundo = out.copy()
    cache = {}
    plantas = F.plantas_do_gramado()
    for x, y, nome, d_m in plantas:
        X, Y = M @ np.array([x, y, 1.0])
        if nome not in cache:
            cache[nome] = sprite_referencia(nome, Q.px_m)
        cor, a_, dm = cache[nome]
        esc = d_m / dm
        interp = cv2.INTER_AREA if esc < 1 else cv2.INTER_CUBIC
        cor_e = cv2.resize(cor, None, fx=esc, fy=esc, interpolation=interp)
        a_e = np.clip(cv2.resize(a_, None, fx=esc, fy=esc, interpolation=interp), 0, 1)
        cor_e = np.clip(cv2.addWeighted(cor_e, 1.6, cv2.GaussianBlur(cor_e, (0, 0), 1.4), -0.6, 0), 0, 255)
        pousar_planta(fundo, cor_e, a_e, X, Y, d_m * Q.px_m, sombra)
    al = cv2.GaussianBlur(verde.astype(np.float32), (0, 0), 0.6)[..., None]
    out = out * (1 - al) + fundo * al
    print(f"    vegetação do gramado: {len(plantas)} plantas da biblioteca, nos lugares das do render, no tamanho real")
    return jardins_c(Q, np.clip(out, 0, 255).astype(np.uint8))


def arco_porta(d, lado=(15.0, 75.0)):
    """O arco de uma porta (R3: não aparece): um traço só de curvas, num quadrado de 15 a 75 pt."""
    r, its = d["rect"], d["items"]
    return d["type"] == "s" and its and all(it[0] == "c" for it in its) and lado[0] < max(r.width, r.height) < lado[1] \
        and abs(r.width - r.height) < 4 and abs((d.get("width") or 0) - 0.57) < 0.05


# Os arcos das portas na base chapada (R3, item 11), que entram no piso em volta (`F.pisos`): os da Casa B (ARQ_PAREDE,
# de 20 a 70 pt) e mais o da pivotante do hall (121,9 pt), o da folha pequena da sala de almoço (17 pt) e os das portas
# dos boxes dos BH master 1 e 2, que o PDF da Casa C desenha na ARQ_BANCADAS (ficavam em pontinhos no travertino)
ARCOS_C = {"camadas": ("ARQ_PAREDE", "ARQ_BANCADAS"), "lado_pt": (15.0, 130.0)}


def arcos_porta_c(Q):
    q = ARCOS_C
    m = np.zeros((Q.H, Q.W), np.uint8)
    n = 0
    for d in Q.desenhos:
        if d.get("layer") in q["camadas"] and arco_porta(d, q["lado_pt"]):
            for c in Q.caminhos(d):
                cv2.polylines(m, [np.int32(np.round(c))], False, 1, F.ARCOS_F["largura_px"])
            n += 1
    return m.astype(bool), n


def bancadas_c(Q, img, **kw):
    """As bancadas (pedra areia e cubas brancas) sem o arco das portas de giro dos boxes, que o PDF desenha na
    ARQ_BANCADAS (R3; antes, 14/10, o do BH master 2 tinha voltado). kw: a borda, a pedra e a cuba de `F.bancadas`."""
    todos = Q.desenhos
    Q._desenhos = [d for d in todos if not (d.get("layer") == "ARQ_BANCADAS" and arco_porta(d))]
    try:
        return F.bancadas(Q, img, **kw)
    finally:
        Q._desenhos = todos


# ----------------------------------------------------------------------------------------------------------------------
# As peças da biblioteca
def banquetas_c(Q, img):
    """As 4 banquetas de linho (0,40 m) nos círculos do PDF à esquerda da ilha, viradas para ela, entrando sob o tampo."""
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q, s = BANQUETAS_C, F.PECAS["sombra"]
    x0, y0, x1, y1 = q["caixa_pt"]
    cs = [Q.p2q((d["rect"].x0 + d["rect"].x1) / 2, (d["rect"].y0 + d["rect"].y1) / 2) for d in Q.desenhos
          if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and d["type"] in ("f", "fs") and x0 <= d["rect"].x0
          and d["rect"].x1 <= x1 and y0 <= d["rect"].y0 and d["rect"].y1 <= y1]
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
    print(f"    ilha da cozinha: {len(cs)} banquetas de linho da biblioteca nos círculos do PDF, entrando sob o tampo")
    return np.clip(out, 0, 255).astype(np.uint8)


def camas_render(Q, img, ini):
    """As camas e os bancos ao pé delas do render aprovado (pedidos do usuário), no retângulo do PDF, por cima do
    tapete, com a sombra curta das peças (para baixo e à esquerda)."""
    s = F.PECAS["sombra"]
    out = img.astype(np.float32)
    a = np.max([F.ret_aa_q(Q, r) for r in [c[1] for c in CAMAS_C["camas"]] + BANCOS_C], axis=0)
    d_ = s["dist_m"] * Q.px_m
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Q.W, Q.H)), (0, 0),
                          s["sig_m"] * Q.px_m) * s["forca"]
    out *= (1 - sb * (1 - a))[..., None]
    out = out * (1 - a[..., None]) + ini.astype(np.float32) * a[..., None]
    print(f"    camas: as {len(CAMAS_C['camas'])} do render aprovado de 14/10, com o jogo de cama de antes, e os "
          f"{len(BANCOS_C)} bancos ao pé delas")
    return np.clip(out, 0, 255).astype(np.uint8)


def pecas_do_render(Q, img, ini, rects, peca, texto):
    """As peças do render aprovado nos retângulos `rects` (pt): os px de `peca` (a máscara do que, no render, é peça
    e não piso), sobre o piso da final, com a sombra curta das peças. Nelas, a legenda pinta o piso por dentro do
    contorno do PDF, e os pisos as cortavam."""
    s = F.PECAS["sombra"]
    out = img.astype(np.float32)
    a = np.zeros((Q.H, Q.W), np.float32)
    for r in rects:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        m = peca(ini[y0:y1, x0:x1].astype(np.int16)).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
        m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 40])
        a[y0:y1, x0:x1] = np.maximum(a[y0:y1, x0:x1], cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5))
    d_ = s["dist_m"] * Q.px_m
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Q.W, Q.H)), (0, 0),
                          s["sig_m"] * Q.px_m) * s["forca"]
    out *= (1 - sb * (1 - a))[..., None]
    out = out * (1 - a[..., None]) + ini.astype(np.float32) * a[..., None]
    print(f"    {texto} do render aprovado ({int((a > 0.5).sum())} px), com a sombra curta")
    return np.clip(out, 0, 255).astype(np.uint8)


def restos_piso(Q, img, ini, rects, area_max=400):
    """Nas zonas que ficam como no render (`rects`, pt: o estar e a sala TV), o piso novo entrava em pedacinhos
    soltos entre as linhas dos estofados (a legenda tem o travertino ali), em pintas amareladas sobre o sofá. O que
    mudou em relação ao render em manchas de até `area_max` px volta a ser o render; o piso grande em volta fica."""
    out = img.copy()
    n_px = 0
    # só dentro das peças do PDF e junto delas (2 px): com o travertino bruto (auditoria de 26/10), o piso aberto muda em
    # toda parte, e as manchinhas soltas do piso novo voltavam ao travertino liso do render em volta do tapete
    pecas = cv2.dilate((Q.preencher(lambda d: d.get("layer") in F.CAMADAS_PECAS and d.get("fill"), ss=2) > 0.3)
                       .astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    for r in rects:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        mud = (np.abs(img[y0:y1, x0:x1].astype(np.int16) - ini[y0:y1, x0:x1].astype(np.int16)).max(axis=2) > 12)
        n, lab, st, _ = cv2.connectedComponentsWithStats(mud.astype(np.uint8), 8)
        m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= area_max])
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~np.isin(
            lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > area_max]) & pecas[y0:y1, x0:x1]
        out[y0:y1, x0:x1][m] = ini[y0:y1, x0:x1][m]
        n_px += int(m.sum())
    print(f"    estar e sala TV: {n_px} px de piso solto entre as linhas dos estofados voltam ao render")
    return out


def neutro(reg):
    """O cinza, o preto e o cromado (o vinílico e o travertino são quentes)."""
    return (reg.max(axis=2) - reg.min(axis=2)) < 28


def verde(reg):
    """As folhas: o verde (BGR: acima do vermelho) e o escuro em volta dele (as folhas na sombra), sem buracos; as
    manchas escuras sem verde (os traços do sofá) ficam fora."""
    from scipy import ndimage
    v = reg[..., 1] > reg[..., 2] + 12
    m = cv2.morphologyEx((v | (reg.mean(axis=2) < 170)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    com_verde = np.unique(lab[v & (lab > 0)])
    return ndimage.binary_fill_holes(np.isin(lab, com_verde))


# A soleira do elevador em inox escovado (Térreo 22, Subsolo 11; seção 4 das regras): o vão da parede esquerda da
# cabine, entre os batentes do PDF (pt). Não é vão branco do PDF (a etapa das soleiras não o pega): no Térreo ficava o
# travertino e, no Subsolo, a soleira bege do render.
SOLEIRA_ELEVADOR_C = {"pt": {"Terreo": (1553.7, 1035.3, 1562.2, 1072.1), "Subsolo": (1553.7, 1034.9, 1565.0, 1071.8)},
                      "inox": (198, 199, 200), "escovado": 6.0, "brilho": 10.0, "linha": (128, 130, 132),
                      "linha_px": 0.6, "semente": 61}


def soleira_elevador(Q, img):
    q = SOLEIRA_ELEVADOR_C
    r = q["pt"][Q.chave]
    x0, y0, x1, y1 = F.ret_q(Q, r)
    x0, y0, x1, y1 = x0 - 2, y0 - 2, x1 + 2, y1 + 2
    a = F.ret_aa_q(Q, r)[y0:y1, x0:x1]
    h, w = a.shape
    (u0, v0), (u1, v1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    em_pe = (v1 - v0) >= (u1 - u0)
    rng = np.random.default_rng(q["semente"])
    n = w if em_pe else h
    fio = cv2.GaussianBlur(rng.normal(0, 1, (1, n)).astype(np.float32), (0, 0), 0.7).ravel() * q["escovado"]
    fio = fio[None, :] if em_pe else fio[:, None]
    t = np.linspace(-1, 1, h if em_pe else w, dtype=np.float32)
    luz = (-t * q["brilho"] / 2)[:, None] if em_pe else (-t * q["brilho"] / 2)[None, :]
    inox = np.float32(q["inox"])[None, None, :] + (fio + luz)[..., None]
    # as faces da parede, em linha cinza fina, nos lados compridos
    e = q["linha_px"] / np.hypot(*(np.array(Q.p2q(1, 0)) - np.array(Q.p2q(0, 0))))
    fl = np.maximum(F.ret_aa_q(Q, (r[0], r[1], r[0] + e, r[3]) if em_pe else (r[0], r[1], r[2], r[1] + e)),
                    F.ret_aa_q(Q, (r[2] - e, r[1], r[2], r[3]) if em_pe else (r[0], r[3] - e, r[2], r[3])))[y0:y1, x0:x1]
    out = img.astype(np.float32)
    reg = out[y0:y1, x0:x1]
    reg = reg * (1 - a[..., None]) + inox * a[..., None]
    out[y0:y1, x0:x1] = reg * (1 - fl[..., None]) + np.float32(q["linha"]) * fl[..., None]
    print("    soleira do elevador em inox escovado, entre os batentes do PDF")
    return np.clip(out, 0, 255).astype(np.uint8)


# Os vidros dos jardins de inverno (usuário, 27/10/26, vendo a final: "corrija esses riscos brancos dentro da área verde,
# no contorno interno, logo depois das portas de vidro."): a faixa do vidro na base é mais larga que o vidro fino que as
# esquadrias desenham, e a parte de dentro dela ficava com manchinhas claras do travertino; embaixo do jardim de inverno,
# a base tem ainda uma soleira estreita (branco e travertino) entre as plantas e o vidro, que saía como um risco claro.
# Linha a linha, em cada lado do jardim (sem os cantos, `cantos_px`), da borda das plantas para fora até a primeira linha
# comprida do vidro desenhado (`longo_px`; sem vidro a até `busca_px`, a linha fica como está): o claro entre as plantas
# e o vidro (e nos `borda_px` px da borda das plantas) vira a vegetação de dentro do próprio jardim, copiada a `fontes`
# px para dentro; onde há a soleira (2 px ou mais da base que não são planta, vidro nem traço), a borda das plantas, com a
# sombra dela, é deslocada até o vidro (os últimos `desloca_px` px, com a emenda em transição), como nos outros lados. O que ficar sem fonte vai por inpaint curto. O vidro e
# o lado de fora não mudam.
JARDINS_VIDROS_TC = {"jardim": [(58, 122, 79)], "vidro": [(211, 214, 214)], "area_min_px": 2000, "busca_px": 10,
                     "claro": 120, "longo_px": 25, "borda_px": 3, "desloca_px": 14, "transicao_px": 6, "cantos_px": 4,
                     "fontes": (16, 22, 28, 34, 40)}


def jardins_vidros_t(Q, img):
    q = JARDINS_VIDROS_TC
    G = Q.cor(q["jardim"], tol=6)
    vidro = Q.cor(q["vidro"], tol=6)
    traco = Q.cor([(0, 0, 0)], tol=20)
    lum = img.astype(np.float32).mean(axis=2)
    claro = lum > q["claro"]
    cv_ = (claro & (vidro | traco)).astype(np.uint8)
    k_ = q["longo_px"]
    longo = (cv2.morphologyEx(cv_, cv2.MORPH_OPEN, np.ones((1, k_), np.uint8)) |
             cv2.morphologyEx(cv_, cv2.MORPH_OPEN, np.ones((k_, 1), np.uint8))) > 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(G.astype(np.uint8), 8)
    out = img.copy()
    sobra = np.zeros(G.shape, np.uint8)
    trocados, jardins = 0, 0
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < q["area_min_px"]:
            continue
        g = lab == i
        x, y, w, h, _ = st[i]
        mexeu = False
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            vertical = ox != 0
            c0 = q["cantos_px"]
            for t in (range(y + c0, y + h - c0) if vertical else range(x + c0, x + w - c0)):
                ls = np.nonzero(g[t, x:x + w] if vertical else g[y:y + h, t])[0]
                if not len(ls):
                    continue
                e = (x if vertical else y) + (ls.min() if (ox if vertical else oy) < 0 else ls.max())
                p0 = (e, t) if vertical else (t, e)
                fim = next((k for k in range(1, q["busca_px"] + 1) if longo[p0[1] + oy * k, p0[0] + ox * k]), None)
                if fim is None:
                    continue
                fora = [(p0[0] + ox * k, p0[1] + oy * k) for k in range(1, fim)]
                soleira = sum(1 for px, py in fora if not (g[py, px] or vidro[py, px] or traco[py, px]))
                if soleira >= 2:
                    # a soleira entre as plantas e o vidro: a borda das plantas (com a sombra dela) vai até o vidro,
                    # com a emenda, lá dentro das plantas, em transição (`transicao_px`)
                    vao = len(fora)
                    k0 = 1 - q["desloca_px"]
                    for k in range(k0, fim):
                        px, py = p0[0] + ox * k, p0[1] + oy * k
                        a_ = min(1.0, (k - k0 + 1) / q["transicao_px"])
                        novo = img[py - oy * vao, px - ox * vao].astype(np.float32)
                        out[py, px] = np.clip(a_ * novo + (1 - a_) * img[py, px], 0, 255).astype(np.uint8)
                        trocados += 1
                    mexeu = True
                    continue
                for k in range(1 - q["borda_px"], fim):
                    px, py = p0[0] + ox * k, p0[1] + oy * k
                    if not (claro[py, px] or k > 0):
                        continue
                    for s in q["fontes"]:
                        sx, sy = px - ox * s, py - oy * s
                        if g[sy, sx] and not claro[sy, sx]:
                            out[py, px] = img[sy, sx]
                            trocados += 1
                            mexeu = True
                            break
                    else:
                        sobra[py, px] = 255
        jardins += mexeu
    if sobra.any():
        out = cv2.inpaint(out, sobra, 2, cv2.INPAINT_TELEA)
    print(f"    jardins de inverno: {trocados} px entre as plantas e o vidro com a vegetação de dentro, em {jardins} "
          f"jardins ({int((sobra > 0).sum())} por inpaint)")
    return out


# As portas de vidro dos jardins de inverno (usuário, 27/10/26, vendo a final: "melhore o aspecto das portas de vidro dos
# jardins de inverno"): eram os traços finos e falhados das esquadrias. Ficam como as do escritório e da adega
# (`final3840_casaa.portas_vidro`): cada folha de correr do PDF (as faixas brancas da ARQ_PAREDE, com os montantes de
# 4,5 pt nas pontas) em alumínio, com o vidro no meio, o contorno e a sombra curta, e os batentes. Antes, o fundo da faixa
# do vidro é refeito: a metade de fora com o travertino de fora, a de dentro com as plantas do jardim (cada uma copiada
# logo ao lado, `fundo_px` além da faixa), para não voltar o risco claro entre as plantas e as folhas. Laterais do
# JARDIM DE INVERNO: 2 folhas cada; embaixo: 3; no alto do JARDIM DE INVERNO 2: 2. `jardim` é o lado das plantas.
# O vidro fixo do JARDIM 1 (usuário, 27/10/26: "aplique o mesmo desenho no vidro fixo também"): no PDF, o painel branco
# de 4,3 pt (o vidro de 2,9 pt e o caixilho) entre os dois arremates cinza da parede, com os quadrados brancos do
# caixilho nas pontas; entra como uma folha (sem correr) com os montantes nas pontas e os dois quadrados como batentes.
# A faixa do fundo fica entre os arremates cinza (que são parede) e é refletida nas bordas (`espelho`): a 13 px, a cópia
# de fora pegava a ponta da costela-de-adão do vaso ao lado, e a reflexão não deixa emenda na borda.
PORTAS_JARDINS_TC = {"fundo_px": 3, "portas": [
    {"nome": "do jardim de inverno, à esquerda", "faixa": (1553.7, 1110.6, 1562.2, 1357.2), "jardim": "dir",
     "batentes": [(1553.7, 1110.6, 1562.2, 1112.8), (1553.7, 1354.9, 1562.2, 1357.2)],
     "folhas": [((1559.3, 1112.8, 1562.2, 1236.1), "y"), ((1556.5, 1231.6, 1559.3, 1354.9), "y")], "montante_pt": 4.5},
    {"nome": "do jardim de inverno, à direita", "faixa": (1802.5, 1110.6, 1811.0, 1357.2), "jardim": "esq",
     "batentes": [(1802.5, 1110.6, 1811.0, 1112.8), (1802.5, 1354.9, 1811.0, 1357.2)],
     "folhas": [((1802.5, 1112.8, 1805.4, 1236.1), "y"), ((1805.4, 1231.6, 1808.2, 1354.9), "y")], "montante_pt": 4.5},
    {"nome": "do jardim de inverno, embaixo", "faixa": (1562.2, 1357.2, 1802.5, 1365.7), "jardim": "cima",
     "batentes": [(1562.2, 1357.2, 1564.4, 1365.7), (1800.3, 1357.2, 1802.5, 1365.7)],
     "folhas": [((1718.6, 1357.2, 1800.3, 1360.0), "x"), ((1641.5, 1360.0, 1723.2, 1362.8), "x"),
                ((1564.4, 1362.8, 1646.1, 1365.7), "x")], "montante_pt": 4.6},
    {"nome": "do jardim de inverno 2, em cima", "faixa": (1672.7, 997.2, 1802.5, 1005.7), "jardim": "baixo",
     "batentes": [(1672.7, 997.2, 1675.0, 1005.7), (1800.3, 997.2, 1802.5, 1005.7)],
     "folhas": [((1675.0, 1002.8, 1739.9, 1005.7), "x"), ((1735.4, 1000.0, 1800.3, 1002.8), "x")], "montante_pt": 4.5},
    {"nome": "do jardim 1 (vidro fixo)", "faixa": (1048.5, 1021.5, 1057.0, 1091.8), "jardim": "esq",
     "batentes": [(1053.1, 1019.8, 1055.9, 1021.5), (1053.1, 1091.8, 1055.9, 1093.5)],
     "folhas": [((1051.6, 1021.5, 1055.9, 1091.8), "y")], "montante_pt": 2.9, "espelho": True}]}


def portas_jardins_t(Q, img):
    import final3840_casaa as FA
    q = PORTAS_JARDINS_TC
    out = img.copy()
    for p in q["portas"]:
        x0, y0, x1, y1 = F.ret_q(Q, p["faixa"])
        v = out if p["jardim"] in ("dir", "esq") else out.transpose(1, 0, 2)
        c0, c1, l0, l1 = (x0, x1, y0, y1) if p["jardim"] in ("dir", "esq") else (y0, y1, x0, x1)
        fonte = v.copy()
        meio = (c0 + c1) // 2
        larg = c1 - c0
        jardim_depois = p["jardim"] in ("dir", "baixo")
        # a metade de fora com o piso de fora, a de dentro com as plantas, copiadas logo além da faixa
        for c in range(c0, c1):
            if p.get("espelho"):
                src = 2 * c1 - 1 - c if c >= meio else 2 * c0 - 1 - c
            else:
                de_dentro = (c >= meio) == jardim_depois
                d = larg + q["fundo_px"]
                src = c + d if (de_dentro == jardim_depois) else c - d
            v[l0:l1, c] = fonte[l0:l1, src]
    guarda = FA.PORTAS_VIDRO
    so_fundo = ("faixa", "jardim", "espelho")
    FA.PORTAS_VIDRO = dict(FA.PORTAS_VIDRO, portas=[{k: v_ for k, v_ in p.items() if k not in so_fundo}
                                                     for p in q["portas"]])
    try:
        out = FA.portas_vidro(Q, out)
    finally:
        FA.PORTAS_VIDRO = guarda
    return out


# O banco em L do deck (usuário, 27/10/26, vendo a final: "banco bronze fosco, sem falhas."): no PDF, o banco é o
# assento (a madeira escura da legenda, a cor do `F.BANCO_DECK`) e, do lado do deck, a frente dele, uma faixa branca
# fina da ARQ_PAREDE com o traço preto. O `F.deck_detalhes` pintava de bronze só o assento; a frente ficava a madeira do
# render, com o reflexo claro sob o braço de cima, o degrau na ponta de cima, a peça clara na de baixo e o quadrado
# escuro no canto de dentro. A moldura da frente, das pontas e do canto entra no banco (os px cinza da base, brancos, de
# traço ou do antialias, a até `frente_px` do assento; a faixa de trás, a até `tras_px` da pedra e da grama, fica como
# está) e o L inteiro sai em bronze fosco, escovado, com o contorno e a sombra curta, como o da Casa B.
BANCO_DECK_TC = {"frente_px": 7, "tras_px": 8, "tras": [(232, 232, 232), (80, 145, 110)], "tras_min_px": 500,
                 "assento_min_px": 2000}


def deck_detalhes_c(Q, img):
    q, qb = BANCO_DECK_TC, F.BANCO_DECK
    assento = F.fechar(Q.cor([qb["cor_base"]], tol=6), 3)
    # só o assento do banco (as manchas grandes da cor; pedacinhos da mesma cor em outras peças não ganham moldura)
    n, lab, st, _ = cv2.connectedComponentsWithStats(assento.astype(np.uint8), 8)
    assento = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["assento_min_px"]])
    tras = Q.cor(q["tras"], tol=6)
    # só as manchas grandes (a pedra, a grama): o antialias claro de um traço dentro do banco não conta
    n, lab, st, _ = cv2.connectedComponentsWithStats(tras.astype(np.uint8), 8)
    tras = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["tras_min_px"]])
    ch = Q.chapada.astype(np.int16)
    cinza = (np.abs(ch[..., 0] - ch[..., 1]) < 6) & (np.abs(ch[..., 1] - ch[..., 2]) < 6)
    moldura = cinza & ~tras

    def perto(m, d):
        return cv2.dilate(m.astype(np.uint8), np.ones((2 * d + 1, 2 * d + 1), np.uint8)) > 0
    frente = moldura & perto(assento, q["frente_px"]) & ~perto(tras, q["tras_px"]) & ~assento
    guarda = Q.chapada.copy()
    try:
        Q.chapada[frente] = qb["cor_base"]
        out = F.deck_detalhes(Q, img)
    finally:
        Q.chapada[...] = guarda
    print(f"    banco do deck: a moldura da frente e das pontas do PDF ({int(frente.sum())} px) junto com o assento, o L "
          f"inteiro em bronze fosco")
    return out


# As cadeiras das mesas de trabalho (usuário, 27/10/26, vendo a final: "As cadeiras precisam ficar parcialmente abaixo
# da mesa de escritório."): no PDF, a cadeira entra cerca de 1/3 sob o tampo (11 de 35 pt), mas a mesa é uma faixa da
# DOC_LINHAS E PROJEÇÕES, pintada antes da cadeira, que saía inteira por cima. A mesa volta por cima da parte da cadeira
# que fica sob o tampo, como as banquetas sob a pedra (seção 8): o tampo, na largura toda e com 1 px da borda do lado da
# cadeira, é refeito ali com o tom de cada coluna passando de uma ponta à outra e o veio fino de um trecho livre da
# própria mesa, adiante no comprimento (longe das pontas), sem o que atravessa a mesa (uma junta, um risco); assim não
# entra costura nem faixa de tom nova. A caixa da cadeira vai com folga (`folga_px`: a sombra dela cai para baixo e à
# esquerda). A sombra curta do tampo cai sobre a cadeira (só na silhueta dela no PDF) onde a luz (do alto, à direita) a
# manda, como a das peças (`F.PECAS["sombra"]`). Pares (pt) do PDF: cadeira e mesa.
CADEIRAS_MESAS_TC = {"pares": [("quarto 1", (1882.2, 786.8, 1915.6, 822.0), (1904.6, 730.7, 1932.9, 855.4)),
                               ("quarto 3", (1150.0, 716.8, 1185.2, 750.3), (1127.9, 739.2, 1241.3, 767.6)),
                               ("suíte master", (997.8, 832.2, 1031.2, 867.3), (1020.2, 776.1, 1048.5, 917.8))],
                     "folga_px": {"esq": 7, "cima": 5, "dir": 5, "baixo": 7}, "borda_px": 1, "pontas_px": 3,
                     "emenda_px": 2, "veio_sig_px": 4.0}


def cadeiras_mesas_t(Q, img):
    q, s = CADEIRAS_MESAS_TC, F.PECAS["sombra"]
    f, e, n = q["folga_px"], q["borda_px"], q["emenda_px"]
    out = img.astype(np.float32)
    H, W = out.shape[:2]
    for nome, cad, mesa in q["pares"]:
        (cx0, cy0), (cx1, cy1) = Q.p2q(cad[0], cad[1]), Q.p2q(cad[2], cad[3])
        (mx0, my0), (mx1, my1) = Q.p2q(mesa[0], mesa[1]), Q.p2q(mesa[2], mesa[3])
        X0, X1, Y0, Y1 = int(round(mx0)), int(round(mx1)), int(round(my0)), int(round(my1))
        a0, a1 = int(np.floor(cx0)) - f["esq"], int(np.ceil(cx1)) + f["dir"]
        b0, b1 = int(np.floor(cy0)) - f["cima"], int(np.ceil(cy1)) + f["baixo"]
        vertical = (Y1 - Y0) > (X1 - X0)
        # trabalha sempre com a mesa em pé (o comprimento nas linhas): a horizontal vai transposta
        v = out if vertical else out.transpose(1, 0, 2)
        if vertical:
            c0, c1, l0, l1, k0, k1, antes = X0, X1, Y0, Y1, b0, b1, (cx0 + cx1) / 2 < (X0 + X1) / 2
        else:
            c0, c1, l0, l1, k0, k1, antes = Y0, Y1, X0, X1, a0, a1, (cy0 + cy1) / 2 < (Y0 + Y1) / 2
        rc0, rc1 = (c0 - e, c1) if antes else (c0, c1 + e)          # a largura toda, com a borda do lado da cadeira
        r0, r1 = max(l0, k0), min(l1, k1)
        L = r1 - r0
        lo, hi = l0 + q["pontas_px"], l1 - q["pontas_px"]
        orig = v.copy()

        def veio_de(dl):
            # o detalhe fino do trecho, sem o que atravessa a mesa de lado a lado (uma junta, um risco): a média de cada
            # linha sai
            c = np.ascontiguousarray(orig[r0 + dl:r1 + dl, rc0:rc1])
            d = c - cv2.GaussianBlur(c, (1, 0), sigmaX=0.1, sigmaY=q["veio_sig_px"])
            return d - d.mean(axis=1, keepdims=True)

        # o trecho do veio: o livre, adiante no comprimento (o mais perto que não toca a cadeira nem as pontas)
        desl = next((sg * d for d in range(L, l1 - l0) for sg in (-1, 1) if lo <= r0 + sg * d and r1 + sg * d <= hi),
                    None)
        if desl is None:
            print(f"    cadeira do {nome}: a mesa não tem trecho livre para refazer o tampo; fica como está")
            continue
        # o tom: coluna a coluna, de uma ponta à outra (média de `emenda_px` linhas em cada ponta), como se a mesa
        # passasse por baixo da cadeira; o veio: só o detalhe fino do trecho copiado (sem as faixas de tom dele)
        ini = orig[r0 - n:r0, rc0:rc1].mean(axis=0)
        fim = orig[r1:r1 + n, rc0:rc1].mean(axis=0)
        t = ((np.arange(L) + 0.5) / L)[:, None, None]
        veio = veio_de(desl)
        v[r0:r1, rc0:rc1] = ini[None] * (1 - t) + fim[None] * t + veio
        # a sombra curta do tampo, fora da mesa, só na caixa da cadeira
        m = np.zeros((H, W), np.float32)
        m[Y0:Y1, X0:X1] = 1
        d_ = s["dist_m"] * Q.px_m
        sb = cv2.GaussianBlur(cv2.warpAffine(m, np.float32([[1, 0, -d_], [0, 1, d_]]), (W, H)), (0, 0),
                              s["sig_m"] * Q.px_m) * s["forca"]
        # só sobre a cadeira (a silhueta dela no PDF, 1 px mais larga): o piso junto à mesa já tem a sombra do tampo
        sil = Q.preencher(lambda d, r=cad: d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and d["rect"].x0 >= r[0] - 0.5
                          and d["rect"].y0 >= r[1] - 0.5 and d["rect"].x1 <= r[2] + 0.5 and d["rect"].y1 <= r[3] + 0.5)
        sil = cv2.dilate(sil, np.ones((3, 3), np.uint8))
        sb *= sil * (1 - m)
        out *= (1 - sb)[..., None]
        print(f"    cadeira do {nome}: a mesa por cima da parte sob o tampo ({L} px de comprimento, o veio de "
              f"{abs(desl)} px adiante, no tom das pontas)")
    return np.clip(out, 0, 255).astype(np.uint8)


# A adega (usuário, 27/10/26, vendo a final: "adicione a prateleira de vinhos como fizemos na outra casa, ao fundo da
# adega. não sobreponha o rotulo nessa prateleira"; "as garrafas em escala"). No PDF da Casa C a adega (1,26 x 4,30 m,
# as folhas de vidro na parede da esquerda) não tem nada dentro: a prateleira entra na parede do fundo, a da direita, de
# ponta a ponta, como a da Casa B (`ajustes_casab.adega_b`): marcenaria areia com o veio no comprido, o contorno fino,
# os módulos em traço fino e as garrafas deitadas, o gargalo junto à parede e a base para o piso. As garrafas na escala
# real (m): 0,075 de diâmetro, o corpo de 0,21 e o gargalo de 0,08 (0,03 de diâmetro), a cada 0,09; a da Casa B, no
# quadro de 3840 px, ficou com a metade disso. A prateleira tem 0,30 m de fundo (o comprimento da garrafa), e o piso
# livre, 0,96 m, onde o rótulo (0,90 m) cabe sem encostar nela; ela entra como obstáculo dos rótulos (`rotulos_t`).
ADEGA_C = {"pt": (2100.2, 1110.6, 2117.2, 1354.3), "modulos": 6, "madeira": (160, 186, 206), "contorno": (110, 118, 124),
           "larg_px": 0.4, "garrafa_m": {"diam": 0.075, "corpo": 0.21, "ombro": 0.015, "gargalo": 0.08,
                                         "diam_gargalo": 0.03, "passo": 0.09, "folga": 0.03, "da_parede": 0.005},
           "vidros": [(26, 40, 28), (20, 32, 48), (30, 24, 46), (24, 34, 26), (22, 30, 40)], "brilho": 0.45,
           "sombra": {"desloc_px": (-0.6, 0.7), "sigma_px": 0.6, "forca": 0.35}, "ss": 8, "semente": 3}


def adega_c(Q, img):
    from retoque_terreo_casae import linha_aa
    q, g = ADEGA_C, ADEGA_C["garrafa_m"]
    X0, Y0 = Q.p2q(q["pt"][0], q["pt"][1])
    X1, Y1 = Q.p2q(q["pt"][2], q["pt"][3])
    wx0, wy0, wx1, wy1 = int(X0) - 6, int(Y0) - 6, int(np.ceil(X1)) + 6, int(np.ceil(Y1)) + 6
    h, w = wy1 - wy0, wx1 - wx0
    r = (X0 - wx0, Y0 - wy0, X1 - wx0, Y1 - wy0)
    out = img.astype(np.float32)
    reg = out[wy0:wy1, wx0:wx1]
    al = B.ret_aa((h, w), r)
    # a marcenaria: o tom areia com o veio no comprido (aqui, na vertical)
    rng = np.random.default_rng(q["semente"])
    ve = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.6, sigmaY=9)
    mad = np.float32(q["madeira"])[None, None] * (1 + 0.06 * ve / max(ve.std(), 1e-6))[..., None]
    reg *= (1 - B.sombra_de(al, Q.px_m, forca=0.25))[..., None]
    reg = reg * (1 - al[..., None]) + mad * al[..., None]
    c = B.contorno_aa((h, w), r, q["larg_px"])[..., None]
    reg = reg * (1 - c) + np.float32(q["contorno"]) * c
    mods = np.linspace(r[1], r[3], q["modulos"] + 1)
    for yd in mods[1:-1]:
        c = linha_aa((h, w), [(r[0], yd), (r[2], yd)], q["larg_px"])[..., None]
        reg = reg * (1 - c) + np.float32(q["contorno"]) * c
    # as garrafas: deitadas, o gargalo junto à parede (à direita), a base para o piso
    k, m_, s_ = q["ss"], Q.px_m, q["sombra"]
    ponta = r[2] - g["da_parede"] * m_
    gl, om, cp = g["gargalo"] * m_, g["ombro"] * m_, g["corpo"] * m_
    n = 0
    for a, b in zip(mods[:-1], mods[1:]):
        ys = np.arange(a + (g["folga"] + g["diam"] / 2) * m_, b - (g["folga"] + g["diam"] / 2) * m_ + 1e-6,
                       g["passo"] * m_)
        ys += ((b - a) - (g["folga"] * 2 + g["diam"]) * m_ - (ys[-1] - ys[0])) / 2 if len(ys) else 0
        for y in ys:
            cor = np.float32(q["vidros"][int(rng.integers(len(q["vidros"])))])
            mk = np.zeros((h * k, w * k), np.uint8)

            def traco(xa, xb, larg, y=y, mk=mk):
                cv2.line(mk, (int(round(xa * k)), int(round(y * k))), (int(round(xb * k)), int(round(y * k))), 255,
                         max(1, int(round(larg * k))), cv2.LINE_AA)
            dg, dc = g["diam_gargalo"] * m_, g["diam"] * m_
            traco(ponta - dg / 2, ponta - gl, dg)
            traco(ponta - gl, ponta - gl - om, (dg + dc) / 2)
            traco(ponta - gl - om - dc / 2, ponta - gl - om - cp + dc / 2, dc)       # as pontas do traço são redondas
            a_ = cv2.resize(mk.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * al
            sh = cv2.GaussianBlur(cv2.warpAffine(a_, np.float32([[1, 0, s_["desloc_px"][0]], [0, 1, s_["desloc_px"][1]]]),
                                                 (w, h)), (0, 0), s_["sigma_px"]) * (1 - a_)
            reg *= (1 - s_["forca"] * sh)[..., None]
            reg = reg * (1 - a_[..., None]) + cor * a_[..., None]
            # o brilho no comprido do corpo, do lado da luz (em cima)
            bm = np.zeros((h * k, w * k), np.uint8)
            yb = y - dc * 0.22
            cv2.line(bm, (int(round((ponta - gl - om - 0.4) * k)), int(round(yb * k))),
                     (int(round((ponta - gl - om - cp + 0.6) * k)), int(round(yb * k))), 255,
                     max(1, int(round(0.45 * k))), cv2.LINE_AA)
            ab = cv2.resize(bm.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None] * \
                q["brilho"] * a_[..., None]
            reg = reg * (1 - ab) + (cor * 0.4 + 255 * 0.6) * ab
            n += 1
    out[wy0:wy1, wx0:wx1] = reg
    print(f"    adega: prateleira de vinhos na parede do fundo ({(X1 - X0) / m_:.2f} x {(Y1 - Y0) / m_:.2f} m), "
          f"{q['modulos']} módulos e {n} garrafas na escala")
    return np.clip(out, 0, 255).astype(np.uint8)


def biblioteca_c(Q, img):
    out = np.ascontiguousarray(img.copy())
    with F.em_quadro(Q):
        if Q.chave == "Terreo":
            out = B.guarda_roupas_terreo(out)
            out = B.cooktops_b(out)
            out = banquetas_c(Q, out)
    if Q.chave == "Terreo":
        out = adega_c(Q, out)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# As escadas (R14) e as projeções
def degraus_linhas(Q, img, q):
    """Os bocéis (pt; cada um com o lado do degrau de baixo): a linha cinza suave e a sombra de ~10 cm no degrau de
    baixo, sem traço preto, e os triângulos (24 x 26 cm), como `retoque_terreo_casae.escada_linhas`."""
    from retoque_terreo_casae import ESCADA_LINHAS
    t = ESCADA_LINHAS
    forca, alcance = t["sombra"]
    k = 4
    xs = [v for b in q["bocels"] for v in (b[0], b[2])] + [x for x, _, _ in q["triangulos"]]
    ys = [v for b in q["bocels"] for v in (b[1], b[3])] + [y for _, y, _ in q["triangulos"]]
    X0, Y0, X1, Y1 = F.ret_q(Q, (min(xs) - 25, min(ys) - 25, max(xs) + 25, max(ys) + 25))
    w, h = X1 - X0, Y1 - Y0

    def P(x, y):
        u, v = Q.p2q(x, y)
        return (u - X0) * k, (v - Y0) * k

    def faixa(a0, b0, a1, b1):
        m = np.zeros((h * k, w * k), np.uint8)
        (u0, v0), (u1, v1) = P(a0, b0), P(a1, b1)
        cv2.rectangle(m, (int(round(min(u0, u1))), int(round(min(v0, v1)))),
                      (int(round(max(u0, u1))) - 1, int(round(max(v0, v1))) - 1), 255, -1)
        return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    fator = np.ones((h, w), np.float32)
    for x0, y0, x1, y1, lado in q["bocels"]:
        hor = abs(y1 - y0) < abs(x1 - x0)
        e = t["bocel_pt"] / 2
        fator *= 1 - (1 - t["bocel"]) * (faixa(x0, y0 - e, x1, y1 + e) if hor else faixa(x0 - e, y0, x1 + e, y1))
        sinal = {"cima": -1, "baixo": 1, "esquerda": -1, "direita": 1}[lado]
        for f in np.linspace(0, 1, 9)[:-1]:
            fa, fb = sinal * alcance * f, sinal * alcance * (f + 1 / 8)
            a, b = min(fa, fb), max(fa, fb)
            fx = faixa(x0, y0 + a, x1, y1 + b) if hor else faixa(x0 + a, y0, x1 + b, y1)
            fator *= 1 - forca * (1 - f - 1 / 16) ** 1.6 * fx
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    reg *= fator[..., None]
    tri = t["triangulo"]
    for xp, yp, sentido in q["triangulos"]:
        dx, dy = {"esquerda": (-1, 0), "direita": (1, 0), "cima": (0, -1), "baixo": (0, 1)}[sentido]
        xa, ya = xp - dx * tri["altura_pt"], yp - dy * tri["altura_pt"]
        bb = tri["base_pt"] / 2
        pts = [(xp, yp), (xa - dy * bb, ya - dx * bb), (xa + dy * bb, ya + dx * bb)]
        m = np.zeros((h * k, w * k), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round([P(x, y) for x, y in pts]))], 255)
        a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg[:] = reg * (1 - a) + np.float32(tri["cor"]) * a
    print(f"    degraus largos: {len(q['bocels'])} bocéis do PDF com a linha suave e a sombra curta; "
          f"{len(q['triangulos'])} triângulo(s) da R14")
    return np.clip(out, 0, 255).astype(np.uint8)


def escadas_c(Q, img):
    from retoque_terreo_casae import escada_linhas
    out = np.ascontiguousarray(img.copy())
    if Q.chave == "Terreo":
        out = degraus_linhas(Q, out, DEGRAUS_LARGOS_T)
        out = escada_linhas(out, None, ESCADA_ESTREITA_T, p2r=Q.p2q)
        with F.em_quadro(Q):
            pa = AJ.PROJECOES_A
            n = 0
            try:
                for zonas, t in ((PROJECOES_C, PROJECOES_TRACO_C["pisos"]),
                                 (PROJECOES_JARDINS_C, PROJECOES_TRACO_C["jardins"])):
                    AJ.PROJECOES_A = dict(pa, larg_px=pa["larg_px"] * Q.W / 2000 * t["larg"], cor=t["cor"],
                                          forca=t["forca"])
                    out, k = B.linhas_pdf(out, "Terreo", zonas, "DOC_LINHAS E PROJEÇÕES")
                    n += k
            finally:
                AJ.PROJECOES_A = pa
        print(f"    projeções do PDF em tracejado ({n} traços): claraboias, os X dos jardins e da área descoberta")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# A final inteira
# ----------------------------------------------------------------------------------------------------------------------
# O Térreo, auditoria de 26/10 (mapa `POE642_CasaC_PH_Terreo_auditoria_2610_v2.jpg`; aprovada pelo usuário: "Aplique a
# lista. No item 8, siga a recomendação.")
# (Os materiais dos lavabos, do BH serviço e do BH externo mudaram com os pedidos de 26/10: `MATERIAIS_TC`.)
# Item 8, os materiais, no padrão do Térreo aprovado da Casa B: as cubas esculpidas e as bancadas dos banhos em travertino
# bruto (BH 1, 2 e 3, BH master 1 e 2, lavabo); as cubas dos lavabos masc. e fem. (os da varanda gourmet) em granito
# marrom, na bancada de travertino bruto; os vasos do lavabo e dos lavabos masc. e fem. marrons (`VASOS_COR_C`); a ilha e
# as bancadas da cozinha e a bancada do gourmet em granito marrom no tom do piso, escurecido (`granito_pt`); as do BH
# serviço e do BH externo (no granito) na pedra areia, com as louças brancas.
# As cubas do PDF (ARQ_BANCADAS): a peça esculpida do BH master 1 tem duas bacias (a de cima e a de baixo, cada uma com a
# torneira) e a prateleira no meio; `F.cubas_bancada` pegava também dois retângulos que juntam bacia e prateleira (a
# prateleira saía como uma terceira cuba).
BANHOS_TC = {"cubas_fora": [(596.5, 643.6, 619.6, 707.2), (596.5, 677.4, 619.6, 707.2), (596.5, 707.2, 619.6, 741.2)],
             "cubas_mais": [(596.5, 643.6, 619.6, 676.2), (596.5, 708.4, 619.6, 741.2)],
             "granito_pt": [(1940.0, 450.0, 2218.0, 860.0), (1045.0, 1105.0, 1430.0, 1330.0)], "folga_pt": 2.0}
# Item 9: os chuveiros de teto do PDF (as placas de 20 cm da ARQ_LOUÇAS E METAIS) na placa cromada com os furinhos
# (`final3840_casaa.chuveiro`); os do BH serviço, do BH externo e do deck com o braço até a parede e a canopla do PDF
CHUVEIROS_T = [(623.4, 569.2, 634.6, 580.4), (680.1, 1110.6, 691.3, 1121.8), (1023.1, 499.8, 1034.3, 511.0),
               (1456.8, 499.8, 1468.0, 511.0), (1726.1, 499.8, 1737.3, 511.0), (1179.0, 1748.4, 1190.2, 1759.6),
               {"ducha": (2415.7, 824.3, 2426.9, 835.5), "braco": (2420.2, 829.2, 2442.5, 830.6),
                "canopla": (2441.4, 828.3, 2442.5, 831.5)},
               {"ducha": (2659.5, 964.6, 2670.7, 975.8), "braco": (2664.0, 969.5, 2686.3, 970.9),
                "canopla": (2685.2, 968.6, 2686.3, 971.8)},
               CHUVEIRO_C]
# Item 6, os boxes: os de correr dos BH 1, 2 e 3 e da ducha entre os lavabos são os pares de folhas do PDF
# (`AJ.folhas_box`, como no Subsolo e na Casa A); os dos BH master 1 e 2 são o vidro fixo (o preenchimento cinza de 3 cm
# da ARQ_BANCADAS) e a porta de vidro (a faixa branca no vão), que entram como um vidro contínuo (`F.boxes_vidro`), com a
# divisória de vidro entre o chuveiro e o vaso do BH master 1; os do granito (BH serviço e BH externo) na faixa
# cinza-clara (`F.boxes_granito`), como na Casa B. A mesma lista vale para os rótulos: o lado do chuveiro sai dos
# ambientes (o rótulo BH SERVIÇO, que caía dentro do box, vai para o piso seco; item 12).
VIDROS_TC = [(592.1, 615.6, 665.7, 617.3, True), (665.7, 538.0, 667.4, 617.3, False), (667.4, 615.6, 728.2, 617.3, True),
             (646.0, 1088.4, 648.3, 1144.4, False),
             (2372.4, 799.1, 2443.2, 800.5, True), (2633.3, 943.3, 2636.1, 986.0, False)]
BOX_GRANITO_MEIO_PT = 799.8                    # o box de correr do BH serviço, que `AJ.folhas_box` acha, fica no granito
# Item 10: a cabine do elevador em aço, como no Subsolo (`ELEVADOR_S`); no Térreo, a soleira e o poço do PDF do Térreo
# (a face de dentro da parede da esquerda em 1562,2 pt)
ELEVADOR_T = {"soleira": SOLEIRA_ELEVADOR_C["pt"]["Terreo"], "anel": (1562.2, 1009.3, 1648.6, 1097.5)}
# Itens 4 e 5, as escadas sem linhas e sem triângulo, com o sombreamento (cada degrau mais claro que o de baixo, a sombra
# curta de cada espelho) e o D: no Térreo as duas descem do deck e do caminho. Os degraus largos (1 a 10; o PDF não marca
# o sentido) com o D no degrau de cima, junto ao patamar 10, no lugar do triângulo; a escada estreita (11 a 21) com o D
# do PDF no degrau de cima, junto ao deck. Os degraus pelos bocéis do PDF, como no Subsolo (`LARGOS_S`, `ESTREITA_S`).
ESCADAS_TC = {"largos_d_pt": (419.2, 1141.6), "estreita_d_pt": (699.9, 1198.4)}
# Item 3 (E4): a seta da entrada principal, como a da Casa A (`final3840_casaa_terreo.seta`, preta, de 1,5 m), no piso do
# HALL DE ENTRADA, abaixo do rótulo, apontando para dentro, a partir da porta pivotante do PDF (a parede da direita, em
# x ~2705 px, com o vão de y ~1298 a ~1425 px)
SETA_TC = {"ponta": (2598, 1386)}


def cubas_terreo_c(Q):
    """As cubas do Térreo: as da ARQ_BANCADAS (`F.cubas_bancada`, guardada em `_cubas_bancada_f`), sem os retângulos
    que juntam bacia e prateleira no BH master 1, e com as duas bacias dele (`BANHOS_TC`)."""
    q = BANHOS_TC
    fora = {tuple(round(v, 1) for v in r) for r in q["cubas_fora"]}
    return sorted([c for c in _cubas_bancada_f(Q) if tuple(round(v, 1) for v in c) not in fora] + q["cubas_mais"])


_cubas_bancada_f = F.cubas_bancada


def _dentro(cx, cy, rs):
    return any(r[0] <= cx <= r[2] and r[1] <= cy <= r[3] for r in rs)


def cuba_terreo_c(Q, out, r):
    """A cuba esculpida: em granito marrom a do lavabo (pedidos de 26/10); as outras em travertino bruto (as dos lavabos
    masc. e fem., que eram de granito, passam ao travertino bruto, pedido de 26/10)."""
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    return F.cuba_esculpida(Q, out, r, "granito" if _dentro(cx, cy, [MATERIAIS_TC["lavabo_pt"]]) else "travertino")


def pedra_terreo_c(Q):
    """A pedra de cada peça de bancada (pedidos de 26/10): granito marrom no lavabo e nos lavabos masc. e fem.; granito
    marrom escurecido no BH serviço e no BH externo (sobre o piso de granito) e na cozinha e no gourmet (`granito_pt`);
    travertino bruto nos outros banhos com cuba (BH 1, 2 e 3, BH master 1 e 2); a pedra areia nas demais (área de
    serviço)."""
    f = BANHOS_TC["folga_pt"]
    mt = MATERIAIS_TC
    zonas = [mt["lavabo_pt"]] + mt["lavabos_mf_pt"]
    cubas = F.cubas_bancada(Q)
    gran = [r for r in cubas if _dentro((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, zonas)]
    rs_g = [F.ret_q(Q, (r[0] - f, r[1] - f, r[2] + f, r[3] + f)) for r in gran]
    rs = [F.ret_q(Q, (r[0] - f, r[1] - f, r[2] + f, r[3] + f)) for r in cubas if r not in gran]
    gs = [(Q.p2q(*g[:2]), Q.p2q(*g[2:])) for g in BANHOS_TC["granito_pt"] + mt["granito_escuro_pt"]]

    def p(Q_, comp):
        if any(comp[y0:y1, x0:x1].any() for x0, y0, x1, y1 in rs_g):       # a peça da cuba do lavabo ou dos masc./fem.
            return "granito"
        ys, xs = np.nonzero(comp)
        cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
        if any(a[0] <= cx <= b[0] and a[1] <= cy <= b[1] for a, b in gs):
            return "granito_escuro"
        if any(comp[y0:y1, x0:x1].any() for x0, y0, x1, y1 in rs):
            return "travertino"
        return None
    return p


def bancadas_t(Q, img):
    guarda = F.cubas_bancada
    F.cubas_bancada = cubas_terreo_c
    try:
        return bancadas_c(Q, img, borda=F.BANCADAS_F["borda_e9"], pedra=pedra_terreo_c(Q), cuba=cuba_terreo_c)
    finally:
        F.cubas_bancada = guarda


def chuveiros_t(Q, img):
    import final3840_casaa as FA
    out = np.ascontiguousarray(img.copy())
    for c in CHUVEIROS_T:
        if not isinstance(c, dict):
            cx, cy = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
            meio = (cx - 0.3, cy - 0.3, cx + 0.3, cy + 0.3)
            c = {"ducha": c, "braco": meio, "canopla": meio}
        out = FA.chuveiro(Q, out, c)
    print(f"    {len(CHUVEIROS_T)} chuveiros na placa cromada com os furinhos (3 com o braço e a canopla do PDF)")
    return out


def vidros_box_t(Q):
    """Os vidros de box do Térreo para os rótulos: os que fecham o chuveiro de parede a parede (os dos BH master 1 e 2
    e o do BH serviço). Os de correr dos BH 1, 2 e 3 e o do BH externo param antes da parede (o trilho e o revestimento
    ficam entre eles e ela): o lado do chuveiro vazava para o banho inteiro, que saía dos ambientes, e os rótulos BH 1,
    BH 2, BH 3, BH EXTERNO e QUARTO EXTERNO iam para fora."""
    return [v for v in VIDROS_TC if not (v[0] > 2600 and not v[4])]


def boxes_t(Q, img):
    import final3840_casaa as FA
    folhas = AJ.folhas_box
    vb = F.vidros_box
    AJ.folhas_box = lambda pg: [b for b in folhas(pg) if not (b["hor"] and abs(b["meio"] - BOX_GRANITO_MEIO_PT) < 1)]
    F.vidros_box = lambda Q_: list(VIDROS_TC)
    try:
        out = FA.boxes(Q, np.ascontiguousarray(img.copy()))
        return F.boxes_vidro(Q, F.boxes_granito(Q, out))
    finally:
        AJ.folhas_box, F.vidros_box = folhas, vb


def elevador_t(Q, img):
    import final3840_casaa as FA
    guarda = FA.ELEVADOR
    FA.ELEVADOR = dict(FA.ELEVADOR, **dict(ELEVADOR_S, **ELEVADOR_T))
    out = img.astype(np.float32)
    a = FA.ret_aa(Q, POCO_ELEVADOR_T)[..., None]                    # o poço limpo, branco (pedidos de 26/10)
    out = np.clip(out * (1 - a) + 255.0 * a, 0, 255).astype(np.uint8)
    try:
        return FA.elevador(Q, np.ascontiguousarray(out))
    finally:
        FA.ELEVADOR = guarda


def degraus_largos_t(Q, img):
    """Os degraus largos no Térreo: o tom de cada degrau pelos bocéis do PDF (`LARGOS_S`, `sombras_degraus`) sobre o
    Bege Bahia, sem as linhas e sem o triângulo, com o D no degrau de cima."""
    q, s = LARGOS_S, F.ESCADA_SOMBRA
    cx0, cy0, cx1, cy1 = q["caixa_pt"]
    x0, y0, x1, y1 = F.ret_q(Q, (cx0, cy0 - 12, cx1, cy1))
    X, Y = grade_pt(Q, x0, y0, x1, y1)
    k = sum((Y > b).astype(np.int32) for b in q["retos"]) + sum(((X > lx) & (Y > ly)).astype(np.int32)
                                                               for lx, ly in q["em_l"])
    n = len(q["retos"]) + len(q["em_l"])
    f = sombras_degraus(k, n, s)
    bege = F.fechar(Q.cor([(232, 232, 232)], tol=6), 5)[y0:y1, x0:x1] & (X >= cx0) & (X <= cx1)
    out = img.copy()
    reg = out[y0:y1, x0:x1].astype(np.float32)
    reg = np.where(bege[..., None], reg * f[..., None], reg)
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    out = F.letra(Q, out, "D", Q.p2q(*ESCADAS_TC["largos_d_pt"]))
    print(f"    degraus largos: {n - 1} degraus sem linhas e sem triângulo, com o sombreamento; o D no degrau de cima")
    return out


def escada_estreita_t(Q, img):
    """A escada estreita no Térreo: o tom de cada degrau pelos bocéis do PDF (`ESTREITA_S`) sobre o Bege Bahia, sem as
    linhas e sem o triângulo, com a sombra do 1º espelho no caminho e o D do PDF no degrau de cima."""
    q, s = ESTREITA_S, F.ESCADA_SOMBRA
    ex0, ey0, ex1, ey1 = q["pdf"]
    x0, y0, x1, y1 = F.ret_q(Q, (ex0 - 8, ey0, ex1, ey1))
    X, Y = grade_pt(Q, x0, y0, x1, y1)
    bordas = [ex0] + list(q["bocels"]) + [ex1]
    k = np.searchsorted(bordas, X).astype(np.int32)
    n = len(bordas)
    f = sombras_degraus(k, n, s)
    bege = F.fechar(Q.cor([(232, 232, 232)], tol=6), 5)[y0:y1, x0:x1] & (Y >= ey0) & (Y <= ey1) & (X <= ex1)
    out = img.copy()
    reg = out[y0:y1, x0:x1].astype(np.float32)
    reg = np.where(bege[..., None], reg * f[..., None], reg)
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    out = F.letra(Q, out, "D", Q.p2q(*ESCADAS_TC["estreita_d_pt"]))
    print(f"    escada estreita: {n - 1} degraus sem linhas e sem triângulo, com o sombreamento; o D no degrau de cima")
    return out


def projecoes_t(Q, img):
    """As projeções do PDF (R8) em tracejado, como em 22/10 (`escadas_c`): os X dos jardins de inverno e da área
    descoberta; as claraboias, desenhadas (`claraboias_t`, pedidos de 26/10)."""
    out = np.ascontiguousarray(img.copy())
    with F.em_quadro(Q):
        pa = AJ.PROJECOES_A
        n = 0
        try:
            for zonas, t in ((PROJECOES_JARDINS_C, PROJECOES_TRACO_C["jardins"]),):
                AJ.PROJECOES_A = dict(pa, larg_px=pa["larg_px"] * Q.W / 2000 * t["larg"], cor=t["cor"],
                                      forca=t["forca"])
                out, k = B.linhas_pdf(out, "Terreo", zonas, "DOC_LINHAS E PROJEÇÕES")
                n += k
        finally:
            AJ.PROJECOES_A = pa
    print(f"    projeções do PDF em tracejado ({n} traços): os X dos jardins e da área descoberta")
    return claraboias_t(Q, out)


def seta_t(Q, img):
    import final3840_casaa_terreo as FT
    guarda = FT.SETA
    FT.SETA = dict(guarda, ponta=SETA_TC["ponta"])
    try:
        return FT.seta(Q, img)
    finally:
        FT.SETA = guarda


def rotulos_t(Q, img):
    """Os rótulos (E7) com os boxes do Térreo (`vidros_box_t`; o lado do chuveiro fora dos ambientes) e, item 13, sem
    tracejado embaixo: os rótulos saem uma vez, e o que as projeções mudaram (a etapa anterior às projeções, do cache)
    volta embaixo de cada texto, com folga; então os rótulos saem de novo, nos mesmos lugares (o lugar depende só do
    PDF), sobre o fundo sem o tracejado, como o X do shaft da Casa B."""
    import retoque_1pav_casae as R1
    rot = B.rotulos_casab(Q.pg, Q.p2q2000)
    esc = Q.W / 2000
    quebras = [(r[0], (Q.p2q(*r[2])[0] / esc, Q.p2q(*r[2])[1] / esc), (0.0, 0.0), {"quebra": ROTULOS_TC["quebras"][r[0]]})
               for r in rot if r[0] in ROTULOS_TC["quebras"]]
    corpos = [(r[0], (Q.p2q(*r[2])[0] / esc, Q.p2q(*r[2])[1] / esc), (0.0, 0.0),
               {"corpo": R1.ROTULOS["escala"] * ROTULOS_TC["corpos"][r[0]]}) for r in rot if r[0] in ROTULOS_TC["corpos"]]
    ajustes = list(Q.q["ajustes"]) + quebras + corpos
    vb = F.vidros_box
    F.vidros_box = vidros_box_t
    fonte = R1.ROTULOS.get("fonte_nome")
    R1.ROTULOS["fonte_nome"] = ROTULOS_TC["fonte_nome"]
    rf = F.ROTULOS_F
    obst = [r for _, r, _ in GUARDA_ROUPAS_C["pecas"]] + list(CLARABOIAS_T["rets"]) + [ADEGA_C["pt"]]
    pontos = dict(rf["pontos"].get(Q.chave, {}), **{n: p for n, p in ROTULOS_TC["pontos"].items() if p})
    F.ROTULOS_F = dict(rf, pontos=dict(rf["pontos"], **{Q.chave: pontos}),
                       obstaculos_pt=dict(rf.get("obstaculos_pt", {}), **{Q.chave: obst}))
    try:
        def uma(im):
            return F.rotulos(Q, im, rot, ajustes, granito=A.granito(im, Q.q.get("granito_lum_max", 125)))
        antes = cv2.imread(str(F.ETAPAS / f"{Q.chave}_escadas.png"))
        out1 = uma(img)
        texto = np.abs(out1.astype(np.int16) - img.astype(np.int16)).max(axis=2) > 10
        perto = cv2.dilate(texto.astype(np.uint8), np.ones((2 * ROTULOS_TC["folga_px"] + 1,) * 2, np.uint8)) > 0
        proj = np.abs(img.astype(np.int16) - antes.astype(np.int16)).max(axis=2) > 0
        sob = perto & proj
        base = img.copy()
        base[sob] = antes[sob]
        print(f"    rótulos: {int(sob.sum())} px de tracejado embaixo dos textos voltam ao fundo; os rótulos de novo")
        return uma(base)
    finally:
        F.vidros_box = vb
        F.ROTULOS_F = rf
        if fonte is None:
            R1.ROTULOS.pop("fonte_nome", None)
        else:
            R1.ROTULOS["fonte_nome"] = fonte


ROTULOS_TC = {"folga_px": 4,
              # pedidos de 26/10 ("melhorar a representação dos rótulos de toda a planta"): o nome em Inter SemiBold e a
              # área em Regular (a hierarquia do nome; o texto segue preto ou branco, sem halo nem sombra, a regra de
              # 22/10); o JARDIM DE INVERNO 2, que passava das paredes do jardim, em duas linhas
              "fonte_nome": "SemiBold", "quebras": {"JARDIM DE INVERNO 2": ["JARDIM DE", "INVERNO 2"],
                                                    "CLOSET MASTER 1": ["CLOSET", "MASTER 1"]},
              # 27/10, vendo a final: "corrija esse rótulo para que não fique sobre o guarda roupas" (CLOSET MASTER 1).
              # Os guarda-roupas da Casa C são faixas da DOC_LINHAS E PROJEÇÕES, fora das camadas de obstáculo dos
              # rótulos, e as claraboias também: entram como obstáculo (`obstaculos_pt` do `final3840_casab.rotulos`).
              # O piso livre do closet master 1, entre a parede e o guarda-roupa, tem 2,1 m (124 px) e o nome numa linha
              # 116 px: vai em duas linhas, como o JARDIM DE INVERNO 2, no meio do piso livre entre a claraboia e os
              # guarda-roupas
              # "corrija o rótulo da garagem para que não fique muito próximo do carro": no PDF, o GARAGEM está sobre
              # o carro do meio, e o lugar livre mais perto encostava no retrovisor dele (4 px); a busca parte do meio
              # do vão entre o carro do meio e o da direita (a 0,2 m de cada um)
              "pontos": {"GARAGEM": (2788.1, 695.2), "CLOSET MASTER 1": (794.6, 707.4), "ADEGA": (2070.4, 1242.7)},
              # a prateleira de vinhos da adega (27/10, `ADEGA_C`): ao lado dela, o piso livre tem 0,96 m e a área do
              # rótulo, 0,90 m; no corpo cheio, o "A:" encostava na porta de vidro. O usuário escolheu o rótulo menor:
              # 85% do corpo (a mesma fração da `F.ROTULOS_F["corpos"]`), no meio do piso livre (o ponto acima, entre a
              # porta e a prateleira, na altura do PDF)
              "corpos": {"ADEGA": 0.85}}


# ----------------------------------------------------------------------------------------------------------------------
# O Térreo, pedidos de 26/10 vendo a final da auditoria (usuário, um a um: "melhorar o aspecto das cortinas"; "melhorar o
# aspecto do marmore travertino bruto"; "melhorar a representação da claraboia"; "melhorar a representação dos rótulos
# de toda a planta"; "lavabo: pedra da bancada e cuba esculpida em marrom granito. na parte de cima temos uma floreira";
# lavabos masc. e fem.: "pedra das pias em marrom granito. cubas em marmore travertino bruto"; "banho serviço: pedra da
# pia em marrom granito e cuba branca"; "banho externo: pedra da pia em marrom granito e cuba branca"; os portões da área
# descoberta: "atras das portas tem uma soleira. remova-as"; "remova soleira clara de uma das portas"; "tem uma soleira
# atras da porta do quarto serviço. remova-a"; "remova essa 'soleira' da janela da cozinha"; a ilha: "essas duas linhas
# claras não existem na bancada. e o cooktop precisa ser girado em 180º"; "melhorar a representação dos chuveiros de teto
# dos banhos"; "gire o cooktop da varanda em 180º"; "remover sujeiras e riscos do escritório"; o elevador e os jardins de
# inverno: "remover as sujeiras, limpar as sujeiras e corrigir os erros dos contornos"; "corrija as paredes atrás das
# portas. alguma sombra ou efeito recortou as paredes"; "corrija as portas da adega").
#
# O travertino bruto em estratos: o travertino de verdade, serrado no veio, tem faixas finas e compridas (umas mais
# claras, outras mais amareladas), as linhas finas de alguns encontros e os poros alongados no sentido das faixas; o
# desenho de antes (a foto da biblioteca com dois ruídos borrados) saía manchado. Duas famílias de faixas (largas, de 5
# a 25 cm, e finas, de 0,8 a 4 cm), levemente onduladas, cada uma com a força variando ao longo do comprimento; uma em
# cada quatro com a linha fina no encontro; os poros de 2 a 7 cm, deitados; as faixas escuras puxam para o amarelo. A
# foto da biblioteca fica por baixo, calma, para o grão. O mesmo desenho nas bancadas, nas cubas esculpidas e no piso
# (`travertino_bruto_tc` troca o da Casa A só durante o Térreo).
TRAVERTINO_TC = {"base": 1.1, "estratos": [((0.05, 0.25), 0.028), ((0.008, 0.04), 0.022)], "veio": 0.06,
                 "veio_frac": 0.25, "poros": 6, "poro_esc": 0.12, "poro_m": (0.015, 0.06),
                 "quente": (1.35, 1.05, 0.80)}                                 # BGR


def _estratos(rng, h, w, px_m, larg_m, amp, n_extra=300):
    """As faixas horizontais: o desvio de cada px (amp x o nível da faixa x a força ao longo dela), a distância ao
    encontro de cima (px), o índice da faixa e a força."""
    Y = np.mgrid[0:h, 0:w][0].astype(np.float32)
    ond = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=1.5 * px_m, sigmaY=0.5 * px_m)
    yw = Y + ond / max(float(ond.std()), 1e-6) * 0.04 * px_m
    n = int(h / (larg_m[0] * px_m)) + n_extra
    larg = rng.uniform(*larg_m, n) * px_m
    bordas = np.cumsum(larg) - n_extra / 2 * np.mean(larg)
    nivel = rng.normal(0, 1, n).astype(np.float32)
    k = np.clip(np.searchsorted(bordas, yw), 0, n - 1)
    env = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.9 * px_m, sigmaY=0.06 * px_m)
    env = np.clip(0.5 + env / max(float(env.std()), 1e-6) * 0.5, 0, 1)
    fr = np.abs(yw - bordas[np.clip(k - 1, 0, n - 1)])
    return amp * nivel[k] * env, fr, k, env


def travertino_estratos(Q, h, w, semente, base=None, poros=None, poro_esc=None, amp=1.0, finas=1.0, quente=True):
    """O desenho do travertino bruto em estratos (média ~1), h x w px: (h, w, 3) com o tom quente das faixas, ou
    (h, w) sem ele (quente=False). finas: a força das faixas finas e das linhas (numa peça estreita, as faixas finas
    fortes liam como réguas de madeira)."""
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    q = TRAVERTINO_TC
    px_m = Q.px_m
    rng = np.random.default_rng(semente)
    T = textura("travertino", px_m, h, w, semente=semente).astype(np.float32)
    det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * px_m), 1)
    D = 1 + (q["base"] if base is None else base) * (det.mean(axis=2) - 1)
    delta = np.zeros((h, w), np.float32)
    for i, (larg_m, a) in enumerate(q["estratos"]):
        s, fr, k, env = _estratos(rng, h, w, px_m, larg_m, a * amp * (finas if i else 1.0))
        delta += s
    tem = rng.uniform(0, 1, 100000) < q["veio_frac"]
    delta -= q["veio"] * amp * finas * np.clip(1 - fr / 0.7, 0, 1) * tem[np.clip(k, 0, 99999)] * env
    n = int((q["poros"] if poros is None else poros) * h * w / px_m ** 2)
    P = np.zeros((h * 4, w * 4), np.float32)
    for x, y, c, e in zip(rng.uniform(0, w * 4, n), rng.uniform(0, h * 4, n),
                          rng.uniform(*q["poro_m"], n) * px_m * 4, rng.uniform(0.6, 1.0, n)):
        cv2.ellipse(P, (int(x), int(y)), (max(2, int(c / 2)), 1), 0, 0, 360, float(e), -1, cv2.LINE_AA)
    P = np.clip(cv2.resize(P, (w, h), interpolation=cv2.INTER_AREA) * 3, 0, 1)
    pe = q["poro_esc"] if poro_esc is None else poro_esc
    if not quente:
        return (D * (1 + delta) * (1 - pe * P)).astype(np.float32)
    Dc = D[..., None] * (1 + delta[..., None] * np.float32(q["quente"]))
    return (Dc * (1 - pe * P)[..., None]).astype(np.float32)


def travertino_bruto_tc(Q, h, w, semente, veio, faixa, poros, poro_esc, forca=1.6):
    """No lugar de `final3840_casaa.travertino_bruto` durante o Térreo: o desenho em estratos, sem o tom (as bancadas, as
    cubas e as faixas o multiplicam pelo delas), mais calmo que o do piso (as peças são estreitas: as faixas largas
    ficam, as finas e as linhas quase somem)."""
    return travertino_estratos(Q, h, w, semente, base=forca * 0.6, poros=poros * 0.7, poro_esc=poro_esc,
                               amp=min(1.0, faixa / 0.02) * 0.9, finas=0.3, quente=False)


# As claraboias (R8): as cinco do PDF (DOC_LINHAS E PROJEÇÕES, o retângulo com o X), a da varanda master, as dos closets
# master 1 e 2, a do box do BH master 2 e a do chuveiro e do vaso do BH master 1. Antes, o tracejado do PDF ia como está
# (traços de comprimentos diferentes, o X partido, a moldura aberta embaixo no closet master 1) e a da varanda ficava
# em branco (o preenchimento branco do PDF). Agora: o piso por baixo (o travertino da varanda, `incluir` nos pisos); a
# luz de cima, um clarão suave no retângulo; a moldura e o X em tracejado regular, com um traço inteiro em cada canto e
# no cruzamento do X (o tracejado é repartido para caber exato em cada lado e em cada diagonal).
CLARABOIAS_T = {"rets": [(578.1, 468.9, 782.1, 506.2), (782.1, 616.0, 809.7, 679.9), (797.8, 1050.6, 866.2, 1079.2),
                         (703.8, 1087.9, 722.5, 1144.6), (592.1, 538.0, 728.2, 563.6)],
                "luz": 0.13, "luz_cor": (252, 252, 250), "luz_sig_px": 1.4,
                "cor": (78, 78, 80), "larg_px": 1.35, "forca": 0.88, "traco_m": 0.15, "vao_m": 0.085, "ss": 4}


def _tracejado(m, p0, p1, traco, vao, larg, ss):
    """Traços de p0 a p1 (px), com o tracejado repartido para começar e terminar num traço inteiro e, com n ímpar, um
    traço no meio."""
    p0, p1 = np.float64(p0), np.float64(p1)
    L = float(np.hypot(*(p1 - p0)))
    n = max(1, int(round((L + vao) / (traco + vao))))
    if n % 2 == 0:
        n += 1
    u = L / (n * traco + (n - 1) * vao) if n > 1 else 1.0
    t, g = traco * u, vao * u
    d = (p1 - p0) / max(L, 1e-6)
    for i in range(n):
        a = p0 + d * i * (t + g)
        b = a + d * (t if n > 1 else L)
        cv2.line(m, tuple(int(round(v * ss)) for v in a), tuple(int(round(v * ss)) for v in b), 255,
                 max(1, int(round(larg * ss))), cv2.LINE_AA)


def claraboias_t(Q, img):
    q = CLARABOIAS_T
    out = img.astype(np.float32)
    ss = q["ss"]
    for r in q["rets"]:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        X0, Y0, X1, Y1 = x0 - 6, y0 - 6, x1 + 6, y1 + 6
        (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        a, b, c, d = a - X0, b - Y0, c - X0, d - Y0
        reg = out[Y0:Y1, X0:X1]
        luz = np.zeros(reg.shape[:2], np.float32)
        cv2.rectangle(luz, (int(round(a)), int(round(b))), (int(round(c)) - 1, int(round(d)) - 1), 1.0, -1)
        luz = cv2.GaussianBlur(luz, (0, 0), q["luz_sig_px"])[..., None] * q["luz"]
        reg[:] = reg + (np.float32(q["luz_cor"]) - reg) * luz
        m = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
        tr, va = q["traco_m"] * Q.px_m, q["vao_m"] * Q.px_m
        for p0, p1 in (((a, b), (c, b)), ((c, b), (c, d)), ((c, d), (a, d)), ((a, d), (a, b)),
                       ((a, b), (c, d)), ((c, b), (a, d))):
            _tracejado(m, p0, p1, tr, va, q["larg_px"], ss)
        al = cv2.resize(m.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
        al *= q["forca"]
        reg[:] = reg * (1 - al) + np.float32(q["cor"]) * al
    print(f"    claraboias: {len(q['rets'])} com o piso por baixo, a luz de cima e a moldura e o X em tracejado regular")
    return np.clip(out, 0, 255).astype(np.uint8)


# Os materiais pedidos: o lavabo com a bancada e a cuba esculpida em granito marrom; os lavabos masc. e fem. com a
# bancada em granito marrom e as cubas esculpidas em travertino bruto; o BH serviço e o BH externo com a bancada em
# granito marrom e as louças brancas (no piso de granito, o granito da bancada escurecido, como as da cozinha, para
# destacar do piso: E9). As peças de bancada (pt) de cada um.
MATERIAIS_TC = {"lavabo_pt": (2120.0, 1140.0, 2232.0, 1312.0),
                "lavabos_mf_pt": [(990.0, 1650.0, 1080.0, 1760.0), (1290.0, 1650.0, 1370.0, 1760.0)],
                "granito_escuro_pt": [(2418.0, 700.0, 2446.0, 756.0), (2546.0, 881.0, 2573.0, 946.0)]}


# A floreira do lavabo (o preenchimento da ARQ_CONTRAPISO no alto do lavabo, entre as paredes e a bancada; a referência
# do usuário: folhas largas verde-escuras sobre seixos e casca de pinus): o fundo de casca e seixos claros, as plantas
# de folha larga da biblioteca, cortadas na caixa, e a borda fina da floreira na pedra da bancada.
FLOREIRA_LAVABO_T = {"pt": (2125.7, 1110.6, 2219.2, 1144.4), "borda_pt": 1.1, "semente": 4211,
                     "casca": (38, 52, 70), "seixo": (178, 186, 192), "seixos_m2": 220, "seixo_m": (0.012, 0.03),
                     "borda": (60, 74, 96), "sombra": 0.35, "folha": (0.50, 0.62, 0.48), "folha_sat": 0.75,
                     "plantas": [("planta_folhas_largas", 0.62, (0.12, 0.50), 20), ("costela_de_adao", 0.58, (0.36, 0.45), 200),
                                 ("dieffenbachia", 0.55, (0.60, 0.55), 110), ("planta_folhas_largas", 0.60, (0.86, 0.48), 300)]}


def floreira_lavabo_t(Q, img):
    q = FLOREIRA_LAVABO_T
    out = img.astype(np.float32)
    x0, y0, x1, y1 = q["pt"]
    e = q["borda_pt"]
    X0, Y0, X1, Y1 = F.ret_q(Q, q["pt"])
    X0, Y0, X1, Y1 = X0 - 2, Y0 - 2, X1 + 2, Y1 + 2
    h, w = Y1 - Y0, X1 - X0
    rng = np.random.default_rng(q["semente"])
    import final3840_casaa as FA
    caixa = FA.ret_aa(Q, q["pt"])[Y0:Y1, X0:X1]
    miolo = FA.ret_aa(Q, (x0 + e, y0 + e, x1 - e, y1 - e))[Y0:Y1, X0:X1]
    # o fundo: a casca de pinus (manchas escuras alongadas) e os seixos claros
    n = rng.normal(0, 1, (h, w)).astype(np.float32)
    fundo = np.float32(q["casca"]) * (1 + 0.22 * cv2.GaussianBlur(n, (0, 0), 0.8)[..., None])
    sx = np.zeros((h * 4, w * 4), np.float32)
    k = int(q["seixos_m2"] * h * w / Q.px_m ** 2)
    for cx, cy, r_, ang in zip(rng.uniform(0, w * 4, k), rng.uniform(0, h * 4, k),
                               rng.uniform(*q["seixo_m"], k) * Q.px_m * 2, rng.uniform(0, 180, k)):
        cv2.ellipse(sx, (int(cx), int(cy)), (max(2, int(r_)), max(2, int(r_ * 0.7))), float(ang), 0, 360, 1.0, -1,
                    cv2.LINE_AA)
    sx = cv2.resize(sx, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    luz_s = 1 + 0.10 * cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.6)[..., None]
    fundo = fundo * (1 - sx) + np.float32(q["seixo"]) * luz_s * sx
    reg = out[Y0:Y1, X0:X1]
    a = caixa[..., None]
    reg[:] = reg * (1 - a) + np.float32(q["borda"]) * a                   # a borda: a pedra da bancada, escura
    m = miolo[..., None]
    reg[:] = reg * (1 - m) + fundo * m
    # as plantas, cortadas no miolo, com a sombra curta (as folhas por cima umas das outras: "over" pré-multiplicado)
    pre = np.zeros((h, w, 3), np.float32)
    folhas = np.zeros((h, w), np.float32)
    for nome, d_m, (fx, fy), giro in q["plantas"]:
        cor, al = sprite_limpo(*B.planta_sprite(nome, d_m, Q.px_m)[:2])
        M = cv2.getRotationMatrix2D((al.shape[1] / 2, al.shape[0] / 2), giro, 1.0)
        cor = cv2.warpAffine(cor, M, (al.shape[1], al.shape[0]))
        al = cv2.warpAffine(al, M, (al.shape[1], al.shape[0]))
        px_, py_ = Q.p2q(x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy)
        ox, oy = int(round(px_ - X0 - al.shape[1] / 2)), int(round(py_ - Y0 - al.shape[0] / 2))
        a0, b0 = max(0, ox), max(0, oy)
        a1, b1 = min(w, ox + al.shape[1]), min(h, oy + al.shape[0])
        if a1 <= a0 or b1 <= b0:
            continue
        s_al = al[b0 - oy:b1 - oy, a0 - ox:a1 - ox][..., None]
        s_cor = cor[b0 - oy:b1 - oy, a0 - ox:a1 - ox]
        # o verde-escuro e fosco da referência (as plantas da biblioteca são claras e com brilho branco)
        cinza_f = s_cor.mean(axis=2, keepdims=True)
        s_cor = (cinza_f + (s_cor - cinza_f) * q["folha_sat"]) * np.float32(q["folha"])
        pre[b0:b1, a0:a1] = s_cor * s_al + pre[b0:b1, a0:a1] * (1 - s_al)
        folhas[b0:b1, a0:a1] = s_al[..., 0] + folhas[b0:b1, a0:a1] * (1 - s_al[..., 0])
    pre *= miolo[..., None]
    folhas *= miolo
    sombra = cv2.GaussianBlur(np.roll(np.roll(folhas, 2, axis=0), -2, axis=1), (0, 0), 1.6) * q["sombra"] * miolo
    reg[:] = reg * (1 - sombra[..., None])
    reg[:] = reg * (1 - folhas[..., None]) + pre
    print(f"    lavabo: a floreira com a casca e os seixos, {len(q['plantas'])} plantas de folha larga e a borda fina")
    return np.clip(out, 0, 255).astype(np.uint8)


# Os chuveiros de teto (a placa quadrada de 20 cm do PDF): a placa cromada nítida, com o chanfro claro em cima e à
# direita (a luz do alto à direita) e escuro embaixo e à esquerda, a face acetinada levemente rebaixada, os bicos em dois
# anéis e no centro, o contorno fino e a sombra curta. Antes, a placa saía cinza e borrada, com uma grade de pontos.
CHUVEIRO_TETO_T = {"raio_pt": 1.5, "chanfro_pt": 1.0, "face": (206, 209, 212), "claro": (246, 247, 248),
                   "escuro": (128, 132, 137), "bico": (104, 108, 113), "bico_pt": 0.30,
                   "aneis": [(3.3, 12), (1.8, 6)], "contorno": (78, 82, 87), "sombra": 0.32}


def chuveiro_teto(Q, out, r):
    import final3840_casaa as FA
    q = CHUVEIRO_TETO_T
    tl = FA.tela(out, Q, r, folga=5)
    x0, y0, x1, y1 = r
    d = tl.ret(r, q["raio_pt"])
    FA.sombra_q(tl, d, forca=q["sombra"], dist=1.1, sigma=1.0)
    X, Y = tl.grade()
    # o chanfro: claro em cima e à direita, escuro embaixo e à esquerda
    t = np.clip(((X - x0) / (x1 - x0) + (y1 - Y) / (y1 - y0)) / 2, 0, 1)[..., None]
    cor = np.float32(q["escuro"]) * (1 - t) + np.float32(q["claro"]) * t
    tl.pintar_img(d, cor)
    c = q["chanfro_pt"]
    face = tl.ret((x0 + c, y0 + c, x1 - c, y1 - c), max(0.4, q["raio_pt"] - c))
    v = np.clip((Y - y0) / (y1 - y0), 0, 1)[..., None]
    tl.pintar_img(face, np.float32(q["face"]) * (1.03 - 0.06 * v))
    bicos = tl.vazia()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pts = [(cx, cy)] + [(cx + rr * np.cos(2 * np.pi * i / n), cy + rr * np.sin(2 * np.pi * i / n))
                        for rr, n in q["aneis"] for i in range(n)]
    for px_, py_ in pts:
        a, b = tl.pt(px_, py_)
        cv2.circle(bicos, (int(round(a)), int(round(b))), max(1, int(round(q["bico_pt"] * FA.PT_PX * 8))), 255, -1,
                   cv2.LINE_AA)
    tl.pintar(bicos, q["bico"], 0.85)
    tl.contorno(face, 0.25, (172, 176, 180))
    tl.contorno(d, 0.4, q["contorno"])
    return tl.gravar()


def chuveiros_tc(Q, img):
    """Os chuveiros: os do braço até a parede com o braço e a canopla de `final3840_casaa.chuveiro`; a placa de todos
    na `chuveiro_teto`."""
    import final3840_casaa as FA
    out = np.ascontiguousarray(img.copy())
    for c in CHUVEIROS_T:
        if isinstance(c, dict):
            out = FA.chuveiro(Q, out, c)
            out = chuveiro_teto(Q, out, c["ducha"])
        else:
            out = chuveiro_teto(Q, out, c)
    print(f"    {len(CHUVEIROS_T)} chuveiros na placa cromada nova (chanfro, face acetinada, bicos em anéis); 3 com o braço")
    return out


# O poço do elevador: entre a cabine e a parede da direita sobravam restos do render (uma mancha preta e branca); o poço
# todo (a face de dentro das paredes do PDF) fica branco, como no Subsolo aprovado, e a cabine vem por cima.
POCO_ELEVADOR_T = (1562.2, 1008.5, 1661.4, 1099.2)


# As soleiras e os vãos (pedidos de 26/10): a soleira atrás da porta do quarto de serviço (o vão vertical do BH serviço)
# sai (`B.SOLEIRAS_B["sem"]`) e o granito do piso atravessa o vão. Os vãos onde o piso passa: o da porta de correr entre a
# área descoberta e a área de serviço (granito); o da porta de correr do escritório (o vinílico dele) e o da adega
# (travertino); a claraboia da varanda master (travertino); e as faixas dos vidros dos jardins de inverno (o travertino
# de fora; o jardim termina no vidro).
# 27/10, vendo a final ("aplique a correção na soleira."; "a soleira é da área de serviço."): a porta de correr entre a
# cozinha e a área de serviço tinha no vão, entre os batentes, a faixa clara do render (bege rosado, não do
# `F.soleiras`: o vão não é um dos `B.vaos_brancos`). A mesma correção do quarto de serviço: o granito dos dois lados
# atravessa o vão (o vão de dentro, sem os batentes) e a folha fica como está.
SEM_SOLEIRA_TC = [(2365.0, 707.5, 2373.5, 750.6)]
VAO_COZINHA_SERVICO_T = (2219.2, 511.5, 2227.7, 576.7)
VAOS_TC = {"granito": [(2365.0, 707.5, 2373.5, 750.6), (2264.6, 458.6, 2406.3, 470.8), VAO_COZINHA_SERVICO_T],
           "vinílico": [(2309.9, 1110.6, 2320.0, 1354.3)],
           "travertino": [(578.1, 468.9, 782.1, 506.2), (2036.3, 1110.6, 2046.3, 1354.3),
                          (1553.7, 1110.6, 1562.2, 1365.7), (1802.5, 1110.6, 1811.0, 1365.7),
                          (1553.7, 1357.2, 1811.0, 1365.7), (1672.7, 997.2, 1802.5, 1005.7)]}


# Depois das esquadrias:
# - as paredes recortadas atrás das portas: a limpeza da faixa das folhas trocava pela cor do piso o trecho de parede
#   junto à folha aberta (3 a 4 px ao longo de 1 m nos BH 1, 2 e 3; as pontas das paredes junto aos batentes); onde o PDF
#   tem parede e a etapa anterior tinha o cinza dela, o cinza volta (o batente claro, neutro, fica);
# - os portões da área descoberta: a faixa clara entre o trilho e a folha volta ao granito da etapa anterior;
# - a ilha da cozinha: as duas linhas claras (os preenchimentos brancos da ARQ_PAREDE ao longo da ilha, que as esquadrias
#   desenhavam como vidro) saem;
# - a porta de correr da área descoberta e os vidros dos jardins de inverno: o que não é folha nem batente do PDF na
#   faixa volta ao piso dos pisos (o granito; o travertino de fora dos jardins), sem a faixa clara e sem as plantas e a
#   terra que passavam do vidro; e o vão da porta de correr entre a cozinha e a área de serviço (27/10; o trecho junto
#   à folha, em `vao_cozinha`);
# - a janela da cozinha: a faixa clara sob a folha da direita vira a bancada de granito (o trecho logo abaixo, copiado);
# - as portas de correr do escritório e da adega: o vão volta ao piso e as 4 folhas são refeitas nos planos do PDF
#   (`final3840_casaa.portas_vidro`, como a da academia no Subsolo), sem a soleira e sem os riscos.
POS_ESQUADRIAS_TC = {
    "portoes": [(2228.0, 326.4, 2272.5, 333.4), (2404.0, 326.4, 2448.6, 333.4)], "poste_lum": 90,
    "ilha": (2044.0, 573.5, 2055.0, 751.8),
    "faixas_piso": [(2264.6, 461.5, 2406.3, 470.8), (1553.7, 1110.6, 1562.2, 1365.7), (1802.5, 1110.6, 1811.0, 1365.7),
                    (1553.7, 1357.2, 1811.0, 1365.7), (1672.7, 997.2, 1802.5, 1005.7), VAO_COZINHA_SERVICO_T],
    "janela": {"pt": (2101.0, 461.5, 2166.0, 470.6), "desce_px": 13, "fonte_x_pt": (2113.0, 2161.5)},
    # o vão da porta de correr da cozinha para a área de serviço (27/10): junto à folha, onde a base tem o traço do
    # contrapiso e o cinza da folha (não o branco do vão), os pisos guardavam a faixa clara do render; ali (a chapada
    # abaixo de `branco`) entra o granito da cozinha, `desloca_px` ao lado
    "vao_cozinha": {"pt": VAO_COZINHA_SERVICO_T, "branco": 230, "desloca_px": -12},
    "claro": 150, "croma": 40,
    "paredes": {"croma_min": 16, "cinza_tol": 14},
    "portas": [{"nome": "do escritório", "vao": (2309.9, 1110.6, 2320.0, 1354.3),
                "batentes": [(2309.9, 1110.6, 2318.4, 1112.8), (2309.9, 1352.1, 2318.4, 1354.3)],
                "folhas": [((2309.9, 1112.8, 2312.8, 1174.9), "y"), ((2312.8, 1170.4, 2315.6, 1232.4), "y"),
                           ((2312.8, 1232.4, 2315.6, 1294.5), "y"), ((2309.9, 1290.0, 2312.8, 1352.1), "y")],
                "montante_pt": 4.5},
               {"nome": "da adega", "vao": (2036.3, 1110.6, 2046.3, 1354.3),
                "batentes": [(2037.8, 1110.6, 2046.3, 1112.8), (2037.8, 1352.1, 2046.3, 1354.3)],
                "folhas": [((2037.8, 1112.8, 2040.6, 1174.9), "y"), ((2040.6, 1170.4, 2043.5, 1232.4), "y"),
                           ((2040.6, 1232.4, 2043.5, 1294.5), "y"), ((2037.8, 1290.0, 2040.6, 1352.1), "y")],
                "montante_pt": 4.5}]}


def _croma(img):
    i = img.astype(np.int32)
    return i.max(axis=2) - i.min(axis=2)


def _folhas_pdf(Q, r, folga_px=0.6):
    """Os preenchimentos da ARQ_PAREDE (folhas, batentes, montantes, paredes) dentro de r (pt), no quadro (bool)."""
    x0, y0, x1, y1 = r
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") is not None
                    and d["rect"].x0 >= x0 - 0.5 and d["rect"].x1 <= x1 + 0.5
                    and d["rect"].y0 >= y0 - 0.5 and d["rect"].y1 <= y1 + 0.5, ss=4)
    return cv2.dilate((a > 0.15).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0 if folga_px else a > 0.15


def soleiras_t(Q, img):
    guarda = B.SOLEIRAS_B
    B.SOLEIRAS_B = dict(guarda, sem=list(guarda.get("sem", [])) + SEM_SOLEIRA_TC)
    try:
        return F.soleiras(Q, img)
    finally:
        B.SOLEIRAS_B = guarda


def pos_esquadrias_t(Q, img, antes):
    import final3840_casaa as FA
    q = POS_ESQUADRIAS_TC
    out = img.copy()
    pisos = cv2.imread(str(F.ETAPAS / f"{Q.chave}_pisos.png"))
    # as paredes recortadas atrás das portas
    pq = q["paredes"]
    a = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "ARQ_ELEMENTOS FIXOS") and d.get("fill") is not None
                    and max(d["fill"]) < 0.5, ss=4)
    era = (np.abs(antes.astype(np.int32) - np.int32(F.PAREDES_F["cinza"])).max(axis=2) <= pq["cinza_tol"])
    volta = (a >= 0.5) & era & (_croma(out) >= pq["croma_min"])
    volta = cv2.dilate(volta.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (a > 0.02) & \
        (_croma(out) >= pq["croma_min"])
    out[volta] = antes[volta]
    n_par = int(volta.sum())
    # os portões: o vão entre o trilho e a folha (a faixa clara e o contorno dela) volta à etapa anterior; os postes
    # escuros das guias ficam
    n_port = 0
    for r in q["portoes"]:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        m = out[y0:y1, x0:x1].astype(np.int32).mean(axis=2) > q["poste_lum"]
        out[y0:y1, x0:x1][m] = antes[y0:y1, x0:x1][m]
        n_port += int(m.sum())
    # a ilha: as duas linhas claras saem
    x0, y0, x1, y1 = F.ret_q(Q, q["ilha"])
    mud = np.abs(out[y0:y1, x0:x1].astype(np.int32) - antes[y0:y1, x0:x1].astype(np.int32)).max(axis=2) > 0
    out[y0:y1, x0:x1][mud] = antes[y0:y1, x0:x1][mud]
    n_ilha = int(mud.sum())
    # as faixas onde o piso passa (a porta de correr da área descoberta, os vidros dos jardins de inverno)
    n_faixa = 0
    for r in q["faixas_piso"]:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        folha = _folhas_pdf(Q, r)[y0:y1, x0:x1]
        m = ~folha
        out[y0:y1, x0:x1][m] = pisos[y0:y1, x0:x1][m]
        n_faixa += int(m.sum())
    v = q["vao_cozinha"]
    x0, y0, x1, y1 = F.ret_q(Q, v["pt"])
    m = Q.chapada[y0:y1, x0:x1].astype(np.int32).mean(axis=2) < v["branco"]
    out[y0:y1, x0:x1][m] = out[y0:y1, x0 + v["desloca_px"]:x1 + v["desloca_px"]][m]
    n_faixa += int(m.sum())
    # a janela da cozinha: a faixa clara sob a folha da direita vira a bancada logo abaixo
    j = q["janela"]
    x0, y0, x1, y1 = F.ret_q(Q, j["pt"])
    folha = _folhas_pdf(Q, (j["pt"][0], 458.0, j["pt"][2], j["pt"][3]), folga_px=0)[y0:y1, x0:x1]
    reg = out[y0:y1, x0:x1]
    m = (reg.astype(np.int32).mean(axis=2) > q["claro"] - 30) & ~folha
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~folha
    d = j["desce_px"] + (y1 - y0)
    fx0, _, fx1, _ = F.ret_q(Q, (j["fonte_x_pt"][0], 470.0, j["fonte_x_pt"][1], 471.0))
    cols = fx0 + np.arange(x1 - x0) % (fx1 - fx0)                  # o trecho livre da bancada, repetido na largura
    fonte = out[y0 + d:y1 + d][:, cols]
    reg[m] = fonte[m]
    n_jan = int(m.sum())
    # as portas de correr do escritório e da adega
    for p in q["portas"]:
        x0, y0, x1, y1 = F.ret_q(Q, p["vao"])
        out[y0:y1, x0:x1] = pisos[y0:y1, x0:x1]
    guarda = FA.PORTAS_VIDRO
    FA.PORTAS_VIDRO = dict(FA.PORTAS_VIDRO, portas=[{k: v for k, v in p.items() if k != "vao"} for p in q["portas"]])
    try:
        out = FA.portas_vidro(Q, out)
    finally:
        FA.PORTAS_VIDRO = guarda
    print(f"    depois das esquadrias: {n_par} px de parede de volta atrás das portas; {n_port} px de soleira clara fora "
          f"dos portões; {n_ilha} px das linhas da ilha; {n_faixa} px de piso na porta de correr e nos vidros dos jardins; "
          f"{n_jan} px da janela da cozinha; as portas do escritório e da adega refeitas")
    return out


# As cortinas (pedido: "melhorar o aspecto das cortinas"): o pano fechado era uma linha fina em zigue-zague (a onda do
# tecido sem corpo). Agora o pano tem o corpo do tecido franzido: o lado do vidro quase reto, o do ambiente em ondas
# (a festa da prega), as pregas em luz e sombra (a crista clara, o vale escuro), a dobra da frente um pouco mais escura
# e a sombra curta no piso. O trilho segue o mesmo, de parede a parede.
CORTINA_TC = {"passo_m": 0.15, "prof_pano_m": 0.075, "festa_m": 0.018}


def pano_cortina(comp_m, px_m, cor=None, passo_m=None, prof_pano=None, festa=None, **_):
    """O pano franzido, que desde 27/10 está na biblioteca (`blocos.pano_franzido`) e vale para todas as casas."""
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = CORTINA_TC
    return blocos.pano_franzido(comp_m, px_m, cor=blocos.LINHO if cor is None else cor,
                                passo_m=q["passo_m"] if passo_m is None else passo_m,
                                prof_pano=q["prof_pano_m"] if prof_pano is None else prof_pano,
                                festa=q["festa_m"] if festa is None else festa)


# As cortinas do estar (usuário, 27/10/26, sobre a final: "e essas cortinas? corrija-as."): no PDF da Casa C, as do
# estar, junto aos vidros do canto do hall e da fachada de baixo, estão na ARQ_MOBILIÁRIO (as outras, na ARQ_LOUÇAS E
# METAIS, que é onde `B.onda_cortina_b` procura) e ficavam as bolinhas do render. Entram as ondas da ARQ_MOBILIÁRIO, nos
# mesmos critérios (traço de 0,85 pt, curvas de 4 a 8 pt), em trechos de pelo menos `min_pt`; o lado do vidro é o do
# traço comprido da ARQ_PAREDE paralelo mais perto (até `vidro_pt`), que no estar fica embaixo ou à direita.
CORTINAS_MOB_TC = {"camada": "ARQ_MOBILIÁRIO", "min_pt": 30.0, "vidro_pt": 14.0, "parede_min_pt": 40.0}


def trechos_cortina_tc(chave, orig):
    import pymupdf
    q, qb = CORTINAS_MOB_TC, B.CORTINAS_B
    trechos = orig(chave)
    pg, p2r = AJ.pdf_pavimento(chave)
    seg, par = [], []
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") == q["camada"] and d["type"] == "s" and abs((d.get("width") or 0) - qb["traco"]) < 0.05 \
                and any(it[0] == "c" for it in d["items"]) and qb["onda"][0] < max(r.width, r.height) < qb["onda"][1] \
                and min(r.width, r.height) < qb["onda"][2]:
            seg.append((r.height > r.width, pymupdf.Rect(r)))
        elif d.get("layer") == "ARQ_PAREDE" and max(r.width, r.height) >= q["parede_min_pt"] and min(r.width, r.height) < 1:
            par.append(pymupdf.Rect(r))
    grupos = []
    for v, r in seg:
        perto = [g for g in grupos if g[0] == v and g[1].intersects(pymupdf.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1))]
        z = pymupdf.Rect(r)
        for g in perto:
            z |= g[1]
            grupos.remove(g)
        grupos.append((v, z))
    n = 0
    for v, r in grupos:
        if max(r.width, r.height) < q["min_pt"]:
            continue
        if v:
            eixo = (r.x0 + r.x1) / 2
            ds = [(p.x0 - eixo) for p in par if p.width < 1 and p.y0 < r.y1 and p.y1 > r.y0
                  and abs(p.x0 - eixo) < q["vidro_pt"]]
            lado = "direita" if ds and min(ds, key=abs) > 0 else "esquerda"
            (ex, e0), (_, e1) = p2r(eixo, r.y0), p2r(eixo, r.y1)
            trechos.append(("v", lado, ex, e0, e1))
        else:
            eixo = (r.y0 + r.y1) / 2
            ds = [(p.y0 - eixo) for p in par if p.height < 1 and p.x0 < r.x1 and p.x1 > r.x0
                  and abs(p.y0 - eixo) < q["vidro_pt"]]
            lado = "baixo" if ds and min(ds, key=abs) > 0 else "cima"
            (e0, ey), (e1, _) = p2r(r.x0, eixo), p2r(r.x1, eixo)
            trechos.append(("h", lado, ey, e0, e1))
        n += 1
    print(f"    cortinas da ARQ_MOBILIÁRIO (o estar): {n} trechos")
    return sorted(trechos, key=lambda t: (t[0], t[2], t[3]))


def cortinas_t(Q, img):
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    orig = blocos.cortina

    def cortina(comp_m, px_m, aberta=False, com_pano=True, com_trilho=True, **kw):
        if com_pano and not com_trilho and not aberta:
            return pano_cortina(comp_m, px_m, **kw)
        return orig(comp_m, px_m, aberta=aberta, com_pano=com_pano, com_trilho=com_trilho, **kw)
    blocos.cortina = cortina
    tr = B.trechos_cortina_b
    B.trechos_cortina_b = lambda chave: trechos_cortina_tc(chave, tr)
    try:
        return F.cortinas(Q, img, paredes_pdf=True)
    finally:
        blocos.cortina = orig
        B.trechos_cortina_b = tr


def passos_terreo_c(Q, ini, M):
    chave = "Terreo"
    cooktops = [(c["pt"][0] - 2, c["pt"][1] - 2, c["pt"][2] + 2, c["pt"][3] + 2) for c in COOKTOPS_C]
    ch = CHUVEIRO_C
    camas = [c[1] for c in CAMAS_C["camas"]]
    fora = CARROS_PT + cooktops + FORA_PECAS_C + camas + BANCOS_C + [BANQUETAS_C["caixa_pt"],
                                   (ch["ducha"][0] - 3, ch["ducha"][1] - 3, ch["canopla"][2] + 3, ch["canopla"][3] + 3)]
    # sob os carros, a legenda tem o contorno deles (traços): ali tudo é granito, para o piso não guardar o desenho
    for r in CARROS_PT:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        Q.chapada[y0:y1, x0:x1] = (50, 66, 90)
    cinza = F.PAREDES_F["cinza"]
    # Auditoria de 26/10 (aprovada: "Aplique a lista. No item 8, siga a recomendação."): o travertino bruto no piso (2);
    # as bancadas com a borda e a sombra e os materiais do padrão da Casa B (7, 8); os vasos marrons (8); os chuveiros
    # cromados (9); os boxes em vidro contínuo (6); a cabine em aço (10); paredes em cinza 80 (1); o trilho das cortinas
    # parando nas paredes do PDF (15); as escadas sem linhas, com o D (4, 5); a claraboia do BH master 1 (14); a seta (3);
    # os rótulos sem tracejado embaixo e o BH SERVIÇO fora do box (12, 13). O armário do quarto externo com os cabides
    # (11, `GUARDA_ROUPAS_C`) e o jardim de inverno sem a faixa escura (16, `jardins_c`).
    # Pedidos de 26/10 vendo a final: o travertino em estratos (pisos, bancadas e cubas); os vãos onde o piso passa e a
    # claraboia da varanda com o piso (`VAOS_TC`); a floreira do lavabo e os materiais dos lavabos e dos BH serviço e
    # externo; os cooktops girados; os chuveiros de teto novos; o poço do elevador limpo; sem a soleira atrás da porta do
    # quarto de serviço; depois das esquadrias, as paredes atrás das portas, os portões, a ilha, a porta de correr, a
    # janela da cozinha, os vidros dos jardins e as portas do escritório e da adega (`pos_esquadrias_t`); as cortinas com
    # o pano novo; as claraboias desenhadas; os rótulos com o nome em SemiBold
    return [
        ("pisos", lambda im: F.pisos(Q, im, incluir=dict(VAOS_TC, granito=CARROS_PT + VAOS_TC["granito"]),
                                     bruto={"travertino": "estratos"})),
        ("bordas", lambda im: B.bordas_grama(im, chave)),
        ("vegetacao", lambda im: vegetacao_c(Q, im, M)),
        ("bancadas", lambda im: floreira_lavabo_t(Q, bancadas_t(Q, im))),
        ("pecas", lambda im: pecas_c(Q, im, ini, fora, camas + NAO_TAPETE_C)),
        ("tampas", lambda im: pecas_do_render(Q, camas_render(Q, F.tampas_vasos(Q, restos_piso(Q, im, ini, FORA_PECAS_C[1:4])),
                                                             ini), ini, VASOS_C, verde,
                                              "estar: os dois vasos junto ao sofá curvo")),
        ("vasos", lambda im: F.vasos_cor(Q, im)),
        ("biblioteca", lambda im: biblioteca_c(Q, im)),
        ("cadeiras", lambda im: cadeiras_mesas_t(Q, im)),
        ("carros", lambda im: F.carros(Q, im, M)),
        ("deck", lambda im: deck_detalhes_c(Q, im)),
        ("chuveiros", lambda im: chuveiros_tc(Q, im)),
        ("boxes", lambda im: boxes_t(Q, im)),
        ("elevador", lambda im: elevador_t(Q, im)),
        ("paredes", lambda im: F.paredes(Q, im, cor=cinza)),
        ("soleiras", lambda im: soleira_elevador(Q, soleiras_t(Q, im))),
        ("esquadrias", lambda im: portas_jardins_t(Q, jardins_vidros_t(Q, pos_esquadrias_t(
            Q, janelas_s(Q, F.esquadrias_terreo(Q, im, parede=cinza), JANELAS_T), im)))),
        ("cortinas", lambda im: cortinas_t(Q, im)),
        ("escadas", lambda im: escada_estreita_t(Q, degraus_largos_t(Q, im))),
        ("projecoes", lambda im: projecoes_t(Q, im)),
        ("seta", lambda im: seta_t(Q, im)),
        ("rotulos", lambda im: rotulos_t(Q, im)),
    ]


def final_3840_c(chave, salvar=True, de=None, ate=None):
    """A final de 3840 px com os rótulos. de: recomeça desta etapa (a anterior vem do cache); ate: para nela."""
    import time
    contexto_c()
    Q = F.Quadro(chave)
    ini = quadro_inicial_c(Q)
    M = F.afim_render(Q, CASA_C / Q.q["render"], CASA_C / Q.q["aprovada"])
    import final3840_casaa as FA
    if chave == "Subsolo":
        passos = passos_subsolo_c(Q, ini)
    else:
        passos = passos_terreo_c(Q, ini, M)
        FA.travertino_bruto = travertino_bruto_tc       # o travertino em estratos nas bancadas e cubas (pedidos de 26/10)
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
        nome = CASA_C / "renders" / f"POE642_CasaC_PH_{chave}_final_rotulos.png"
        cv2.imwrite(str(nome), img)
        print(f"    {nome} {img.shape[1]}x{img.shape[0]}")
    return Q, img


# ----------------------------------------------------------------------------------------------------------------------
# O Subsolo
# Os bancos da sauna em travertino (14/10): na legenda, o degrau da frente em L (#CAC6AE) e o assento junto à parede de
# baixo (#C1BDA1); o travertino da biblioteca no tom do piso da sauna, 0,91 e 0,867 dele, com as arestas em linha fina
SAUNA_C = {"pt": (549.6, 990.8, 651.7, 1138.9), "pecas": [((174, 198, 202), 0.91), ((161, 189, 193), 0.867)],
           "piso_px": (824, 760, 975, 880), "linha": (108, 121, 123), "larg_px": 0.7, "forca": 0.8, "semente": 733}
# Os aparelhos da academia (esteiras, bicicletas e supinos) ficam os do render aprovado: pelo PDF saíam silhuetas
# cinza chapadas, sem a lona da esteira nem as barras dos supinos (no tamanho do PDF, já conferido)
FORA_PECAS_S = [(961.7, 511.3, 1360.5, 796.2)]
# A floreira junto à sauna (item 5): só as plantas da biblioteca, dentro dela
FLOREIRA_S = {"caixa": (672, 745, 688, 973), "semente": 31,
              "plantas": [("arbusto_1", 0.42, (0.5, 0.08), 0), ("arbusto_2", 0.40, (0.5, 0.25), 90),
                          ("arbusto_3", 0.42, (0.5, 0.42), 180), ("arbusto_1", 0.40, (0.5, 0.58), 270),
                          ("arbusto_2", 0.42, (0.5, 0.75), 0), ("arbusto_3", 0.40, (0.5, 0.92), 90)]}


def pegada_subsolo(Q):
    """O que fica em cor cheia no Subsolo (R2, resposta do usuário "OK"): o que a legenda pinta (os ambientes do
    Subsolo, o pátio, os degraus largos e o caminho, com as paredes), fechado e sem furos, mais a escada estreita
    esmaecida. 0 a 1, no quadro."""
    from scipy import ndimage
    nb = (Q.chapada.min(axis=2) < 250).astype(np.uint8)
    nb = cv2.morphologyEx(nb, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb, 8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 2000])
    m = ndimage.binary_fill_holes(m)
    x0, y0, x1, y1 = F.ret_q(Q, ESCADA_ESTREITA_T["pdf"])
    m[y0 - 1:y1 + 2, x0 - 1:x1 + 2] = True
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6)
    return np.maximum(a, m * 1.0)


def bancos_sauna_c(Q, img, bruto=None):
    """bruto: o desenho do travertino bruto da Casa A (`final3840_casaa.TRAVERTINO[bruto]`), não a foto lisa."""
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    q = SAUNA_C
    out = img.astype(np.float32)
    px0, py0, px1, py1 = q["piso_px"]
    trav = Q.cor([(202, 217, 220)], tol=4)[py0:py1, px0:px1]
    piso = np.median(out[py0:py1, px0:px1][trav], axis=0)
    x0, y0, x1, y1 = F.ret_q(Q, q["pt"])
    x0, y0, x1, y1 = x0 - 3, y0 - 3, x1 + 3, y1 + 3
    if bruto:
        import final3840_casaa as FA
        D = FA.travertino_bruto(Q, y1 - y0, x1 - x0, q["semente"], forca=F.SAUNA_F["veio"], **FA.TRAVERTINO[bruto])
    else:
        T = textura("travertino", Q.px_m, y1 - y0, x1 - x0, semente=q["semente"]).astype(np.float32)
        det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * Q.px_m), 1)
        D = 1 + 1.6 * (det - 1)
    reg = out[y0:y1, x0:x1]
    tudo = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for cor, f in q["pecas"]:
        m = Q.cor([cor], tol=4)[y0:y1, x0:x1].astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5)[..., None]
        reg[:] = reg * (1 - a) + piso * f * D[..., None] * a
        tudo |= m
        borda = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((2, 2), np.uint8)).astype(np.float32)
        al = np.clip(cv2.GaussianBlur(borda, (0, 0), 0.4) * q["larg_px"] * 1.4, 0, 1)[..., None] * q["forca"]
        reg[:] = reg * (1 - al) + np.float32(q["linha"]) * al
    print("    sauna: o banco em L e o assento em travertino " + ("bruto (veios e poros)" if bruto else "da biblioteca")
          + ", no tom do piso (0,91 e 0,867), arestas finas")
    return np.clip(out, 0, 255).astype(np.uint8)


def floreira_s(Q, img):
    q = FLOREIRA_S
    fl = Q.cor([FLOREIRA_COR], tol=6).astype(np.uint8)
    x0, y0, x1, y1 = q["caixa"]
    m = np.zeros_like(fl)
    m[y0 - 2:y1 + 2, x0 - 2:x1 + 2] = fl[y0 - 2:y1 + 2, x0 - 2:x1 + 2]
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5) * m
    cfg = {"terra": JARDINS_C["terra"], "terra_ruido": JARDINS_C["terra_ruido"],
           "forracao": dict(JARDINS_C["forracao"], d_m=(0.30, 0.40), passo_m=0.22), "plantas": q["plantas"],
           "transbordo_m": 0.0, "semente": q["semente"]}
    with F.em_quadro(Q):
        AJ.base_terreo, base = (lambda forma, c="Terreo": cv2.resize(Q.chapada, (forma[1], forma[0]),
                                                                      interpolation=cv2.INTER_NEAREST)), AJ.base_terreo
        try:
            r = B.mascara_pdf
            B.mascara_pdf = lambda chave, forma, **kw: r("Subsolo", forma, **kw)
            out = B.canteiro(np.ascontiguousarray(img.copy()), a, (x0, y0, x1, y1), cfg, Q.px_m, "floreira da sauna")
        finally:
            B.mascara_pdf = r
            AJ.base_terreo = base
    return out


# ----------------------------------------------------------------------------------------------------------------------
# A auditoria de 26/10 no Subsolo (mapa `renders/POE642_CasaC_PH_Subsolo_auditoria_2610_v2.jpg`; usuário: "ok, aplique a
# lista", com as recomendações das duas perguntas): as paredes em cinza 80 (E10); o travertino bruto do Subsolo aprovado
# da Casa B no piso e nos bancos da sauna (E11); as escadas sem linhas e sem triângulo, com o S e o sombreamento (E3,
# E8); a escada estreita com a linha de corte do PDF e nevoada depois dela, como a escada em U da Casa A; o box de correr
# do BH academia em vidro contínuo com o trilho (E5); a bancada com a borda e a sombra (E9) e os materiais do BH sauna da
# Casa B (bancada em granito marrom, cuba esculpida em travertino bruto, vaso marrom); os rótulos SAUNA e BH ACADEMIA
# longe do banco, do box e das paredes (E7); os chuveiros de teto na placa cromada com os furinhos; a cabine do
# elevador em aço, como nas Casas A e B.
# O vaso do BH academia (o retângulo da louça no PDF, pt) e a cor; no Térreo, nenhum (os da Casa B não valem aqui)
VASOS_COR_C = {"Subsolo": [((781.3, 1094.9, 810.4, 1114.9), "marrom")],
               # Térreo (auditoria de 26/10, item 8, o padrão da Casa B): o lavabo e os lavabos masc. e fem.
               "Terreo": [((2125.7, 1162.9, 2154.8, 1182.9), "marrom"), ((1101.6, 1744.0, 1130.7, 1764.0), "marrom"),
                          ((1262.4, 1756.1, 1282.5, 1785.2), "marrom")]}
# A torneira cromada da cuba do BH academia (usuário, 26/10/26: "faltou a torneira metalica da cuba"; o PDF não a
# desenha): na prateleira de trás, entre o aro da cuba e a parede da direita, no meio da cuba, com a bica sobre a bacia,
# como as dos banhos da Casa A (`final3840_casaa.torneira`: a base redonda e o bico, em pt)
TORNEIRA_S = {"bico": (801.4, 996.5, 808.7, 998.6), "base": (808.7, 997.55, 1.4)}
# Os chuveiros de teto do PDF (ARQ_LOUÇAS E METAIS, as placas de 20 cm): o da ducha e o do BH academia
CHUVEIROS_S = [(685.8, 1026.9, 697.0, 1038.1), (685.8, 1102.1, 697.0, 1113.3)]
# Os rótulos (E7): a folga maior em volta do texto (o BH ACADEMIA encostava na linha do box e na parede); o SAUNA parte do
# meio do piso livre (o banco, ARQ_CONTRAPISO, não é obstáculo dos rótulos, e o texto encostava nele)
ROTULOS_S = {"folga_px": 4, "pontos": {"SAUNA": (586.2, 1010.0)}}
# Os degraus largos (pátio para o caminho), sem os bocéis e sem o triângulo: cada px leva o número do degrau pelos bocéis
# do PDF (os 7 retos e os 2 em L: o lado de lá do L é o que fica à direita e abaixo do canto); 0 é o pátio, 1 o degrau
# junto a ele (onde estava o triângulo) e o último, o patamar do caminho. O S no lugar do triângulo (o PDF não marca o
# sentido aqui; vale o do triângulo de 22/10: sobe do pátio para o caminho).
LARGOS_S = {"caixa_pt": (226.5, 926.9, 509.9, 1269.3), "s_pt": (368.2, 941.2),
            "retos": (926.9, 955.5, 984.1, 1012.8, 1041.4, 1070.0, 1098.6), "em_l": ((300.2, 1127.3), (328.5, 1155.9))}
# A escada estreita (11 a 21), do caminho para o deck: os degraus em Bege Bahia com o sombreamento de subida (o 11, à
# esquerda, o mais escuro), esmaecida como desde 14/10; a linha de corte do PDF (ARQ_ESCADAS E RAMPAS, a diagonal com a
# quebra) em cinza escuro fino, como na escada em U do 1º Pavimento da Casa A, e o trecho depois dela (19 a 21) nevoado;
# o S do PDF no degrau 11 (a origem do texto cai fora da escada), esmaecido como ela. Saem os restos do render (o anel e o
# traço laranja no 18, a diagonal fraca no 11, o pontinho no 19) e o triângulo.
ESTREITA_S = {"pdf": (538.3, 1155.9, 708.4, 1240.9), "bocels": [555.3 + 17.0 * k for k in range(9)],
              "corte": [(657.1, 1155.3), (672.8, 1194.5), (681.3, 1194.5), (667.4, 1202.4), (675.9, 1202.4),
                        (691.4, 1240.9)],
              "esmaecer": 0.40, "nevoa": {"branco": 0.72, "sigma_px": 1.2}, "linha": {"cor": (64, 64, 64), "larg_px": 1.2},
              "letra": 0.35, "semente": 762}
# A cabine do elevador em aço (a rotina da Casa A, `final3840_casaa.elevador`), no desenho do PDF da Casa C
# (INS_INSTALAÇÕES HIDRÁULICAS): as paredes e o piso da cabine, a porta telescópica à esquerda, o poço entre as paredes
# do PDF e a soleira em inox. O poço da Casa C é largo à direita da cabine (17 pt): o anel cinza fica estreito em volta
# dela (~4,5 pt, como na Casa A) e o resto do poço fica branco, como os shafts
ELEVADOR_S = {"externo": (1568.2, 1013.8, 1644.1, 1093.0), "interno": (1572.7, 1018.3, 1639.5, 1088.5),
              "vao": (1568.2, 1036.4, 1572.7, 1070.4),
              "folhas": [(1569.3, 1019.5, 1571.0, 1036.4), (1569.3, 1033.6, 1571.0, 1050.6),
                         (1569.3, 1056.2, 1571.0, 1073.2), (1569.3, 1070.4, 1571.0, 1087.4)],
              "soleira": SOLEIRA_ELEVADOR_C["pt"]["Subsolo"], "anel": (1565.0, 1009.3, 1648.6, 1097.5)}


def grade_pt(Q, x0, y0, x1, y1):
    """Os pt do PDF do centro de cada px do recorte [y0:y1, x0:x1] do quadro (o p2q é afim)."""
    (a, b), (c, d), (e, f) = Q.p2q(0, 0), Q.p2q(100, 0), Q.p2q(0, 100)
    M = np.linalg.inv(np.array([[(c - a) / 100, (e - a) / 100], [(d - b) / 100, (f - b) / 100]]))
    U, V = np.meshgrid(np.arange(x0, x1) + 0.5 - a, np.arange(y0, y1) + 0.5 - b)
    return M[0, 0] * U + M[0, 1] * V, M[1, 0] * U + M[1, 1] * V


def sombras_degraus(k, n, s):
    """O fator de cada px pelo número do degrau k (0 o piso de baixo, 1 a n-1 os degraus, n o de cima): cada degrau um
    pouco mais claro que o de baixo, a sombra curta do espelho do de cima e a do 1º espelho no piso de baixo
    (`F.ESCADA_SOMBRA`, como `F.escada_sombreada`)."""
    rng = np.random.default_rng(s["semente"])
    tons = 1 + rng.uniform(-s["tom_degrau"], s["tom_degrau"], n + 1)
    t0, t1 = s["tom"]
    f = np.where((k >= 1) & (k < n), (t0 + (t1 - t0) * (k - 1) / max(n - 1, 1)) * tons[k], 1.0).astype(np.float32)
    for i in range(0, n):
        m = k == i
        if not m.any():
            continue
        d = cv2.distanceTransform((k <= i).astype(np.uint8), cv2.DIST_L2, 5)        # até o degrau de cima
        fs, alc = s["piso"] if i == 0 else s["espelho"]
        f = np.where(m, f * (1 - fs * np.exp(-np.maximum(d - 0.5, 0) / alc)), f)
    return f


def degraus_largos_s(Q, img):
    q, s = LARGOS_S, F.ESCADA_SOMBRA
    cx0, cy0, cx1, cy1 = q["caixa_pt"]
    x0, y0, x1, y1 = F.ret_q(Q, (cx0, cy0 - 12, cx1, cy1))
    X, Y = grade_pt(Q, x0, y0, x1, y1)
    k = sum((Y > b).astype(np.int32) for b in q["retos"]) + sum(((X > lx) & (Y > ly)).astype(np.int32)
                                                               for lx, ly in q["em_l"])
    n = len(q["retos"]) + len(q["em_l"])
    f = sombras_degraus(k, n, s)
    # o Bege Bahia da legenda, com as linhas finas da base fechadas (a projeção do PDF que corta o pátio e os degraus)
    bege = F.fechar(Q.cor([(232, 232, 232)], tol=6), 5)[y0:y1, x0:x1] & (X >= cx0) & (X <= cx1)
    out = img.copy()
    reg = out[y0:y1, x0:x1].astype(np.float32)
    reg = np.where(bege[..., None], reg * f[..., None], reg)
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    out = F.letra(Q, out, "S", Q.p2q(*q["s_pt"]))
    print(f"    degraus largos: {n - 1} degraus sem linhas e sem triângulo, com o sombreamento de subida (do pátio para "
          f"o caminho); o S no degrau 1")
    return out


def escada_estreita_s(Q, img, ss=8):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    q, s = ESTREITA_S, F.ESCADA_SOMBRA
    ex0, ey0, ex1, ey1 = q["pdf"]
    x0, y0, x1, y1 = F.ret_q(Q, (ex0 - 8, ey0, ex1, ey1))
    x0, y0, x1, y1 = x0, y0 - 1, x1 + 1, y1 + 1
    X, Y = grade_pt(Q, x0, y0, x1, y1)
    a = F.ret_aa_q(Q, q["pdf"])[y0:y1, x0:x1][..., None]
    h, w = a.shape[:2]
    # os degraus pelos bocéis (0 = o caminho, à esquerda; 1 = o degrau 11), o tom do Bege Bahia da planta
    bordas = [ex0] + list(q["bocels"]) + [ex1]
    k = np.searchsorted(bordas, X).astype(np.int32)
    n = len(bordas)
    f = sombras_degraus(k, n, s)
    bege = F.fechar(Q.cor([(232, 232, 232)], tol=6), 5)
    tom = np.median(img[bege].reshape(-1, 3), axis=0).astype(np.float32)
    T = textura(F.DEGRAUS_F["pedra"], Q.px_m, h, w, semente=q["semente"]).astype(np.float32)
    novo = T / T.reshape(-1, 3).mean(axis=0) * tom * f[..., None]
    # o trecho depois da linha de corte (0 a 1), pelo polígono da linha e da borda direita da escada
    pts = [Q.p2q(x, y) for x, y in q["corte"] + [(ex1 + 3, ey1 + 3), (ex1 + 3, ey0 - 3), (q["corte"][0][0], ey0 - 3)]]
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((np.float32(pts) - (x0, y0)) * ss))], 255)
    depois = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    e, nv = q["esmaecer"], q["nevoa"]
    antes_c = novo * (1 - e) + 255 * e
    nevoa = cv2.GaussianBlur(novo, (0, 0), nv["sigma_px"]) * (1 - nv["branco"]) + 255 * nv["branco"]
    novo = antes_c * (1 - depois) + nevoa * depois
    out = img.astype(np.float32)
    reg = out[y0:y1, x0:x1]
    # a sombra do 1º espelho no caminho (esmaecida como a escada), fora da escada
    ch = bege[y0:y1, x0:x1][..., None] & (k == 0)[..., None]
    reg[:] = np.where(ch, reg * (1 - (1 - f[..., None]) * (1 - e)), reg)
    reg[:] = reg * (1 - a) + novo * a
    out = np.clip(out, 0, 255).astype(np.uint8)
    # a linha de corte do PDF, por cima, e o S do PDF no degrau 11, esmaecido como a escada
    lc = q["linha"]
    cp = np.float32([Q.p2q(x, y) for x, y in q["corte"]])
    ml = np.zeros((h * ss, w * ss), np.uint8)
    cv2.polylines(ml, [np.int32(np.round((cp - (x0, y0)) * ss))], False, 255, max(1, int(round(lc["larg_px"] * ss))),
                  cv2.LINE_AA)
    al = cv2.resize(ml.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - al) + np.float32(lc["cor"]) * al, 0, 255).astype(np.uint8)
    cor = F.LETRA_F["cor"]
    F.LETRA_F["cor"] = tuple(int(round(c + (255 - c) * q["letra"])) for c in cor)
    try:
        out = F.letra(Q, out, "S", Q.p2q((bordas[0] + bordas[1]) / 2, (ey0 + ey1) / 2))
    finally:
        F.LETRA_F["cor"] = cor
    print(f"    escada estreita: {n - 1} degraus em Bege Bahia, sem linhas e sem triângulo, com o sombreamento de subida, "
          f"esmaecida; a linha de corte do PDF e o trecho depois dela nevoado; o S no degrau 11")
    return out


def torneira_s(Q, img):
    import final3840_casaa as FA
    out = FA.torneira(Q, np.ascontiguousarray(img.copy()), TORNEIRA_S["bico"], TORNEIRA_S["base"])
    print("    BH academia: a torneira cromada na prateleira de trás da cuba")
    return out


def chuveiros_s(Q, img):
    """Os chuveiros de teto na placa cromada com os furinhos (`final3840_casaa.chuveiro`, sem o braço)."""
    import final3840_casaa as FA
    out = np.ascontiguousarray(img.copy())
    for r in CHUVEIROS_S:
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        meio = (cx - 0.3, cy - 0.3, cx + 0.3, cy + 0.3)
        out = FA.chuveiro(Q, out, {"ducha": r, "braco": meio, "canopla": meio})
    print(f"    {len(CHUVEIROS_S)} chuveiros de teto: a placa cromada com os furinhos")
    return out


def boxes_s(Q, img):
    """O box de correr do BH academia: as duas folhas do PDF em vidro contínuo e o trilho no vão (`final3840_casaa.boxes`,
    como os boxes da Casa A)."""
    import final3840_casaa as FA
    return FA.boxes(Q, np.ascontiguousarray(img.copy()))


# A limpeza (usuário, 26/10/26, vendo a final: "limpeza necessária, vários micro imagens em erro" e, nas portas de vidro
# da academia, "alguns retoques no piso e nas portas de vidro"): o que a base chapada não pinta como piso ficava com os
# px do render de 14/10. Logo depois dos pisos:
# - as linhas finas da base entre os pisos (a emenda do pátio com a varanda, os bocéis tracejados junto à floreira) são
#   refeitas pelos pisos em volta (`cv2.inpaint`);
# - os brancos do PDF (a borda da floreira, o vão do vidro da sauna, os vãos das janelas e das portas, as louças e as
#   bancadas, que as etapas seguintes redesenham) saem num claro só, sem os restos do render (as folhas fora da floreira,
#   a mancha branca no canto do vidro);
# - a faixa das portas de correr da academia fica fora (`portas_academia_s`, depois das esquadrias).
LIMPEZA_S = {"fino_px": 6, "perto_px": 4, "area_max": 6000,
             "porta_academia": (889.2, 540.8, 900.6, 926.3),
             # a floreira com a borda (a mureta branca do PDF em volta do canteiro) e o vão do vidro da sauna: tudo o que
             # não é o canteiro nem parede vira a pedra clara (a mureta e o peitoril do vidro), sem os restos do render
             "floreira_pt": (508.0, 926.3, 549.6, 1158.0), "vidro_pt": 542.6,
             "fora": [ESTREITA_S["pdf"], (1565.0, 1008.5, 1661.4, 1099.2)]}


def limpeza_s(Q, img, dentro):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    from retoque_terreo_casae import BEGE
    q = LIMPEZA_S
    out = img.copy()
    ch = Q.chapada
    pisos = Q.cor([c for _, cs, *_ in PISOS_C["Subsolo"] for c in cs], tol=6)
    preto = ch.max(axis=2) < 60
    branco = ch.min(axis=2) >= 250
    outros = Q.cor([FLOREIRA_COR] + [c for c, _ in SAUNA_C["pecas"]], tol=6)
    fora = np.zeros_like(dentro)
    for r in q["fora"] + [q["porta_academia"]] + FORA_PECAS_S:          # e os aparelhos da academia, do render
        x0, y0, x1, y1 = F.ret_q(Q, r)
        fora[y0 - 2:y1 + 2, x0 - 2:x1 + 2] = True
    # 1. as linhas finas da base entre os pisos
    resto = (dentro & ~pisos & ~preto & ~branco & ~outros & ~fora).astype(np.uint8)
    k = q["fino_px"]
    fino = resto & (1 - cv2.morphologyEx(resto, cv2.MORPH_OPEN, np.ones((k, k), np.uint8)))
    perto = cv2.dilate(pisos.astype(np.uint8), np.ones((2 * q["perto_px"] + 1,) * 2, np.uint8))
    # e os traços pretos finos do PDF (a borda do vão do vidro da sauna, os lados da mureta): as paredes são grossas e
    # as etapas seguintes redesenham as finas, as peças e os vidros por cima; ali ficavam os vidros e as folhas do render
    fino_preto = preto & ~cv2.morphologyEx(preto.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
    linhas = ((fino | (fino_preto & dentro & ~fora)) & perto).astype(np.uint8) * 255
    out = cv2.inpaint(out, linhas, 2, cv2.INPAINT_TELEA)
    # a pedra clara: o Bege Bahia nítido das soleiras (`F.soleiras`), no quadro inteiro, para pousar em qualquer máscara
    T = textura("bege_bahia", Q.px_m, Q.H, Q.W, semente=F.SOLEIRAS_F["semente"] + 50).astype(np.float32)
    T = np.clip((1 + F.SOLEIRAS_F["forca"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(BEGE["tom"]), 0, 255)
    # 2. os brancos do PDF na pedra clara (os pequenos: não os ambientes inteiros nem o poço do elevador); as placas dos
    # chuveiros (as etapas seguintes as desenham no tamanho do PDF) ficam no piso em volta
    chuv = np.zeros_like(dentro)
    for r in CHUVEIROS_S:
        x0, y0, x1, y1 = F.ret_q(Q, (r[0] - 2, r[1] - 2, r[2] + 2, r[3] + 2))
        chuv[y0:y1, x0:x1] = True
    n, lab, st, _ = cv2.connectedComponentsWithStats((branco & dentro & ~fora & ~chuv).astype(np.uint8), 8)
    claros = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= q["area_max"]])
    x0, y0, x1, y1 = F.ret_q(Q, q["floreira_pt"])
    zona = np.zeros_like(dentro)
    zona[y0:y1, x0:x1] = True
    claros |= zona & ~outros & (~preto | fino_preto) & ~pisos
    out[claros] = T[claros].astype(np.uint8)
    out = cv2.inpaint(out, (chuv & dentro & (branco | ~pisos)).astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    print(f"    limpeza: {int((linhas > 0).sum())} px de linhas finas da base refeitos pelos pisos em volta; "
          f"{int(claros.sum())} px dos brancos do PDF e da borda da floreira na pedra clara")
    return out


JANELAS_S = {"lum_max": 90, "escuro_min": 0.15, "cor": (232, 234, 236), "recuo_pt": 0.3, "x_max_pt": 1550.0}
# No Térreo (auditoria de 26/10, com as paredes em cinza 80): a janela do chuveiro do BH master 2 (84% escura); os outros
# vãos têm o caixilho e o vidro das esquadrias (até 47% de traço escuro), que ficam
JANELAS_T = dict(JANELAS_S, escuro_min=0.6, x_max_pt=1e9)


# As portas de correr da academia (usuário, 26/10/26: "alguns retoques no piso e nas portas de vidro"): na faixa da
# parede, o PDF desenha as 4 folhas em escada (ARQ_PAREDE, brancas) e as pontas da soleira; a final tinha o travertino e
# a madeira em degraus e uma faixa bege do render, e a limpeza das esquadrias espelhava os pisos para dentro da faixa.
# Depois das esquadrias, a porta é refeita pela rotina das portas de vidro da Casa A (`final3840_casaa.portas_vidro`): a
# soleira de Bege Bahia nítido na faixa toda, com as faces da parede em cinza fino; os batentes nas pontas; as 4 folhas
# nos planos do PDF, o caixilho claro com o vidro no meio, os montantes e a sombra curta.
PORTA_ACADEMIA_S = {"nome": "da academia", "soleira": (889.2, 540.8, 900.6, 926.3),
                    "batentes": [(889.2, 540.8, 900.6, 543.1), (889.2, 924.0, 900.6, 926.3)],
                    "folhas": [((897.7, 543.1, 900.6, 641.7), "y"), ((894.9, 637.2, 897.7, 735.8), "y"),
                               ((892.0, 731.3, 894.9, 829.9), "y"), ((889.2, 825.4, 892.0, 924.0), "y")],
                    "montante_pt": 4.5, "pontas_pt": [(884.0, 926.3, 906.0, 940.0), (884.0, 528.0, 906.0, 540.8)]}


def portas_academia_s(Q, img):
    import final3840_casaa as FA
    guarda = FA.PORTAS_VIDRO
    FA.PORTAS_VIDRO = dict(FA.PORTAS_VIDRO, portas=[PORTA_ACADEMIA_S])
    try:
        out = FA.portas_vidro(Q, img)
    finally:
        FA.PORTAS_VIDRO = guarda
    # nas pontas da porta, as esquadrias desenhavam um batente listrado por cima da parede (no pé, junto ao depósito):
    # a parede do PDF volta ali, só nessas janelas
    par = F.paredes(Q, out.copy(), cor=F.PAREDES_F["cinza"])
    for r in PORTA_ACADEMIA_S["pontas_pt"]:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        out[y0:y1, x0:x1] = par[y0:y1, x0:x1]
    # e os tiquinhos cinza dos montantes antigos das esquadrias que sobravam na madeira, junto à faixa: a madeira em volta
    s_ = PORTA_ACADEMIA_S["soleira"]
    x0, y0, x1, y1 = F.ret_q(Q, (s_[2] + 0.6, s_[1] + 3, s_[2] + 3.0, s_[3] - 3))
    reg = out[y0:y1, x0:x1].astype(np.int32)
    cinza = np.zeros(out.shape[:2], np.uint8)
    cinza[y0:y1, x0:x1] = (((reg[..., 2] - reg[..., 0]) < 45) & (reg.mean(axis=2) < 150)).astype(np.uint8) * 255
    return cv2.inpaint(out, cinza, 2, cv2.INPAINT_TELEA)


def sem_verde_s(Q, img):
    """Depois das esquadrias: a limpeza da faixa do vidro da sauna espelha o lado do canteiro para dentro do vão e
    trazia as folhas da borda dele (pontinhos verdes junto ao vidro). A mureta da floreira e o peitoril até o vidro (o
    que não é canteiro nem parede grossa, até `vidro_pt`) voltam inteiros à pedra clara; e, no resto da zona, o px
    esverdeado fora do canteiro vai à pedra em volta (a mediana dos px claros e quentes da zona)."""
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    from retoque_terreo_casae import BEGE
    x0, y0, x1, y1 = F.ret_q(Q, LIMPEZA_S["floreira_pt"])
    out = img.copy()
    xm = F.ret_q(Q, (LIMPEZA_S["vidro_pt"], 0, LIMPEZA_S["vidro_pt"], 0))[0]
    preto = Q.chapada.max(axis=2) < 60
    grosso = cv2.morphologyEx(preto.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
    mureta = ~Q.cor([FLOREIRA_COR], tol=6) & ~grosso
    mureta[:, :x0] = False
    mureta[:, xm:] = False
    mureta[:y0] = False
    mureta[y1:] = False
    T = textura("bege_bahia", Q.px_m, y1 - y0, xm - x0, semente=F.SOLEIRAS_F["semente"] + 51).astype(np.float32)
    T = np.clip((1 + F.SOLEIRAS_F["forca"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(BEGE["tom"]), 0, 255)
    reg = out[y0:y1, x0:xm]
    m = mureta[y0:y1, x0:xm]
    reg[m] = T[m].astype(np.uint8)
    reg = out[y0:y1, x0:x1].astype(np.int32)
    canteiro = Q.cor([FLOREIRA_COR], tol=6)[y0:y1, x0:x1]
    b, g, r = reg[..., 0], reg[..., 1], reg[..., 2]
    verde = (g >= r - 2) & (g > b + 15) & ~canteiro
    pedra = (r > g) & (g > b) & (r > 170) & ~canteiro
    if verde.any() and pedra.any():
        reg[verde] = np.median(reg[pedra], axis=0).astype(np.int32)
        out[y0:y1, x0:x1] = reg.astype(np.uint8)
    print(f"    floreira: {int(verde.sum())} px esverdeados fora do canteiro na pedra clara")
    return out


def janelas_s(Q, img, q=None):
    """Os vãos das janelas (os preenchimentos brancos da ARQ_PAREDE) que ficaram escuros: com as paredes pretas não se
    viam; no cinza 80, a janela da ducha do BH academia (na parede de baixo) saía como uma barra preta. O vão fica
    claro, como nas janelas da Casa B, com o vidro fino das esquadrias. q: os parâmetros (`JANELAS_S`, `JANELAS_T`)."""
    q = q or JANELAS_S
    out = img.copy()
    n = 0
    for d in Q.desenhos:
        r = d["rect"]
        if d.get("layer") != "ARQ_PAREDE" or not d.get("fill") or min(d["fill"]) < 0.9 or r.width * r.height < 20 \
                or r.x0 > q["x_max_pt"]:                               # não os batentes do elevador
            continue
        e = q["recuo_pt"]
        x0, y0, x1, y1 = F.ret_q(Q, (r.x0 + e, r.y0 + e, r.x1 - e, r.y1 - e))
        reg = out[y0:y1, x0:x1]
        lum = reg.astype(np.float32).mean(axis=2)
        m = lum < q["lum_max"]
        if m.mean() >= q["escuro_min"]:
            reg[m] = q["cor"]
            n += 1
    print(f"    janelas: {n} vão(s) escuro(s) no claro")
    return out


def elevador_s(Q, img):
    import final3840_casaa as FA
    guarda = FA.ELEVADOR
    FA.ELEVADOR = dict(FA.ELEVADOR, **ELEVADOR_S)
    try:
        return FA.elevador(Q, np.ascontiguousarray(img.copy()))
    finally:
        FA.ELEVADOR = guarda


def passos_subsolo_c(Q, ini):
    chave = "Subsolo"
    peg = pegada_subsolo(Q)
    dentro = peg > 0.5
    AJ.SUBSOLO_R2 = dict(AJ.SUBSOLO_R2, terreo=CASA_C / "renders" / "POE642_CasaC_PH_Terreo_final_rotulos.png")
    F.SAUNA_F = dict(F.SAUNA_F, Subsolo={"pt": SAUNA_C["pt"]})
    F.ROTULOS_F = dict(F.ROTULOS_F, folga_px=ROTULOS_S["folga_px"], pontos={"Subsolo": ROTULOS_S["pontos"]})
    cinza = F.PAREDES_F["cinza"]
    fora_box = [(727.5, 1076.5, 731.5, 1139.0)]               # os traços do box de correr (vão em `boxes_s`)
    fora_chuveiros = [(r[0] - 1, r[1] - 1, r[2] + 1, r[3] + 1) for r in CHUVEIROS_S]
    return [
        ("pisos", lambda im: limpeza_s(Q, F.pisos(Q, im, dentro=dentro, bruto={"travertino": "piso"}), dentro)),
        ("floreira", lambda im: floreira_s(Q, im)),
        ("bancadas", lambda im: torneira_s(Q, bancadas_c(Q, im, borda=F.BANCADAS_F["borda_e9"], pedra="granito",
                                                      cuba=F.cuba_granito))),
        ("sauna", lambda im: bancos_sauna_c(Q, im, bruto="bancada")),
        ("pecas", lambda im: F.pecas_pdf(Q, im, ini, fora=FORA_PECAS_S + fora_box + fora_chuveiros)),
        ("aparelhos", lambda im: pecas_do_render(Q, im, ini, FORA_PECAS_S, neutro, "academia: os aparelhos")),
        ("tampas", lambda im: F.tampas_vasos(Q, im)),
        ("vasos", lambda im: F.vasos_cor(Q, im)),
        ("chuveiros", lambda im: chuveiros_s(Q, im)),
        ("boxes", lambda im: boxes_s(Q, im)),
        ("elevador", lambda im: elevador_s(Q, im)),
        ("paredes", lambda im: F.paredes(Q, im, cor=cinza)),
        ("soleiras", lambda im: soleira_elevador(Q, F.soleiras(Q, im))),
        ("esquadrias", lambda im: portas_academia_s(Q, sem_verde_s(Q, janelas_s(
            Q, B.esquadrias_final(im, chave, Q.pg, Q.p2q, Q.px_m, parede=cinza))))),
        ("escadas", lambda im: escada_estreita_s(Q, degraus_largos_s(Q, im))),
        ("hachura", lambda im: AJ.subsolo_hachurado(im, peg, Q.px_m)),
        ("rotulos", lambda im: F.rotulos(Q, im, B.rotulos_casab(Q.pg, Q.p2q2000), Q.q["ajustes"],
                                         granito=A.granito(im, Q.q.get("granito_lum_max", 125)))),
    ]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(PAVIMENTOS_C))
    ap.add_argument("--de", default=None, help="recomeça desta etapa (pisos, bordas, vegetacao, bancadas, pecas, ...)")
    ap.add_argument("--ate", default=None, help="para nesta etapa")
    a = ap.parse_args()
    final_3840_c(a.pavimento, de=a.de, ate=a.ate)

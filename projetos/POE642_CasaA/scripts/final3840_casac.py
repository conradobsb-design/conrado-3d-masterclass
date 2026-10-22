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


def piso_textura_c(Q, img, m, nome, forca, sig_m, semente):
    novo = _piso_textura_b(Q, img, m, nome, forca, sig_m, semente)
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
    ("closet master 2, embaixo", (731.9, 1112.3, 935.1, 1145.6), "cima")]}
# Os cooktops de 5 bocas (14/10, item 10): o da gourmet deitado (2 em cima, 3 embaixo); o da ilha da cozinha em pé, com
# 3 bocas na coluna da esquerda e 2 na da direita
COOKTOPS_C = [{"pt": (1188.3, 1264.3, 1238.2, 1292.6), "giro": 0},
              {"pt": (2057.7, 615.1, 2086.0, 664.9), "giro": 90}]
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
               (695.9, 1085.8, 729.1, 1142.7)]
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


def jardins_c(Q, img):
    q = JARDINS_C
    out = np.ascontiguousarray(img.copy())
    comum = {"terra": q["terra"], "terra_ruido": q["terra_ruido"], "forracao": q["forracao"]}
    with F.em_quadro(Q):
        for nome, a, caixa, sem, plantas in floreiras(Q):
            out = B.canteiro(out, a, caixa, dict(comum, plantas=plantas, transbordo_m=0.0, semente=sem), Q.px_m, nome)
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


def bancadas_c(Q, img):
    """As bancadas (pedra areia e cubas brancas) sem o arco das portas de giro dos boxes, que o PDF desenha na
    ARQ_BANCADAS (R3; antes, 14/10, o do BH master 2 tinha voltado)."""
    todos = Q.desenhos
    Q._desenhos = [d for d in todos if not (d.get("layer") == "ARQ_BANCADAS" and arco_porta(d))]
    try:
        return F.bancadas(Q, img)
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
    for r in rects:
        x0, y0, x1, y1 = F.ret_q(Q, r)
        mud = (np.abs(img[y0:y1, x0:x1].astype(np.int16) - ini[y0:y1, x0:x1].astype(np.int16)).max(axis=2) > 12)
        n, lab, st, _ = cv2.connectedComponentsWithStats(mud.astype(np.uint8), 8)
        m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= area_max])
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~np.isin(
            lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > area_max])
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


def biblioteca_c(Q, img):
    out = np.ascontiguousarray(img.copy())
    with F.em_quadro(Q):
        if Q.chave == "Terreo":
            out = B.guarda_roupas_terreo(out)
            out = B.cooktops_b(out)
            out = banquetas_c(Q, out)
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
    return [
        ("pisos", lambda im: F.pisos(Q, im, incluir={"granito": CARROS_PT})),
        ("bordas", lambda im: B.bordas_grama(im, chave)),
        ("vegetacao", lambda im: vegetacao_c(Q, im, M)),
        ("bancadas", lambda im: bancadas_c(Q, im)),
        ("pecas", lambda im: pecas_c(Q, im, ini, fora, camas + NAO_TAPETE_C)),
        ("tampas", lambda im: pecas_do_render(Q, camas_render(Q, F.tampas_vasos(Q, restos_piso(Q, im, ini, FORA_PECAS_C[1:4])),
                                                             ini), ini, VASOS_C, verde,
                                              "estar: os dois vasos junto ao sofá curvo")),
        ("biblioteca", lambda im: biblioteca_c(Q, im)),
        ("carros", lambda im: F.carros(Q, im, M)),
        ("deck", lambda im: F.deck_detalhes(Q, im)),
        ("boxes", lambda im: F.boxes_granito(Q, im)),
        ("paredes", lambda im: F.paredes(Q, im)),
        ("soleiras", lambda im: soleira_elevador(Q, F.soleiras(Q, im))),
        ("esquadrias", lambda im: F.esquadrias_terreo(Q, im)),
        ("cortinas", lambda im: F.cortinas(Q, im)),
        ("escadas", lambda im: escadas_c(Q, im)),
        ("rotulos", lambda im: F.rotulos(Q, im, B.rotulos_casab(Q.pg, Q.p2q2000), Q.q["ajustes"],
                                         granito=A.granito(im, Q.q.get("granito_lum_max", 125)))),
    ]


def final_3840_c(chave, salvar=True, de=None, ate=None):
    """A final de 3840 px com os rótulos. de: recomeça desta etapa (a anterior vem do cache); ate: para nela."""
    import time
    contexto_c()
    Q = F.Quadro(chave)
    ini = quadro_inicial_c(Q)
    M = F.afim_render(Q, CASA_C / Q.q["render"], CASA_C / Q.q["aprovada"])
    if chave == "Subsolo":
        passos = passos_subsolo_c(Q, ini)
    else:
        passos = passos_terreo_c(Q, ini, M)
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
# Os degraus largos no Subsolo (item 6): a mesma escada (os bocéis tracejados do PDF do Subsolo, nas mesmas posições),
# subindo do pátio (degrau 1) para o caminho: a sombra no degrau de baixo (em cima de cada bocel; os dois em L, à
# esquerda) e o triângulo no degrau 1, junto ao pátio, apontando para o caminho (para baixo na planta).
DEGRAUS_LARGOS_S = {"bocels": DEGRAUS_LARGOS_T["bocels"], "triangulos": [(368.2, 947.3, "baixo")]}
# A escada estreita (11 a 21) fica esmaecida (14/10); o "S" do PDF do Subsolo está no degrau 11: o triângulo ali,
# apontando para a direita (sobe para o deck), esmaecido como ela
TRIANGULO_ESTREITA_S = {"pt": (549.3, 1198.4, "direita"), "esmaecer": 0.5}
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


def bancos_sauna_c(Q, img):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    q = SAUNA_C
    out = img.astype(np.float32)
    px0, py0, px1, py1 = q["piso_px"]
    trav = Q.cor([(202, 217, 220)], tol=4)[py0:py1, px0:px1]
    piso = np.median(out[py0:py1, px0:px1][trav], axis=0)
    x0, y0, x1, y1 = F.ret_q(Q, q["pt"])
    x0, y0, x1, y1 = x0 - 3, y0 - 3, x1 + 3, y1 + 3
    T = textura("travertino", Q.px_m, y1 - y0, x1 - x0, semente=q["semente"]).astype(np.float32)
    det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * Q.px_m), 1)
    reg = out[y0:y1, x0:x1]
    tudo = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for cor, f in q["pecas"]:
        m = Q.cor([cor], tol=4)[y0:y1, x0:x1].astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5)[..., None]
        reg[:] = reg * (1 - a) + piso * f * (1 + 1.6 * (det - 1)) * a
        tudo |= m
        borda = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((2, 2), np.uint8)).astype(np.float32)
        al = np.clip(cv2.GaussianBlur(borda, (0, 0), 0.4) * q["larg_px"] * 1.4, 0, 1)[..., None] * q["forca"]
        reg[:] = reg * (1 - al) + np.float32(q["linha"]) * al
    print("    sauna: o banco em L e o assento em travertino da biblioteca, no tom do piso (0,91 e 0,867), arestas finas")
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


def escadas_s(Q, img):
    out = degraus_linhas(Q, img, DEGRAUS_LARGOS_S)
    from retoque_terreo_casae import ESCADA_LINHAS
    t = ESCADA_LINHAS["triangulo"]
    q = TRIANGULO_ESTREITA_S
    xp, yp, sentido = q["pt"]
    dx, dy = {"esquerda": (-1, 0), "direita": (1, 0), "cima": (0, -1), "baixo": (0, 1)}[sentido]
    xa, ya = xp - dx * t["altura_pt"], yp - dy * t["altura_pt"]
    bb = t["base_pt"] / 2
    pts = [(xp, yp), (xa - dy * bb, ya - dx * bb), (xa + dy * bb, ya + dx * bb)]
    k = 8
    X0, Y0, X1, Y1 = F.ret_q(Q, (xp - 20, yp - 20, xp + 20, yp + 20))
    w, h = X1 - X0, Y1 - Y0
    mm = np.zeros((h * k, w * k), np.uint8)
    cv2.fillPoly(mm, [np.int32(np.round([((np.array(Q.p2q(x, y)) - (X0, Y0)) * k) for x, y in pts]))], 255)
    a = cv2.resize(mm.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    cor = 255 - (255 - np.float32(t["cor"])) * q["esmaecer"]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - a) + cor * a, 0, 255).astype(np.uint8)
    print("    escada estreita (esmaecida): o triângulo da R14 no degrau 11, apontando para a direita")
    return out


def passos_subsolo_c(Q, ini):
    chave = "Subsolo"
    peg = pegada_subsolo(Q)
    dentro = peg > 0.5
    AJ.SUBSOLO_R2 = dict(AJ.SUBSOLO_R2, terreo=CASA_C / "renders" / "POE642_CasaC_PH_Terreo_final_rotulos.png")
    F.SAUNA_F = dict(F.SAUNA_F, Subsolo={"pt": SAUNA_C["pt"]})
    return [
        ("pisos", lambda im: F.pisos(Q, im, dentro=dentro)),
        ("floreira", lambda im: floreira_s(Q, im)),
        ("bancadas", lambda im: bancadas_c(Q, im)),
        ("sauna", lambda im: bancos_sauna_c(Q, im)),
        ("pecas", lambda im: F.pecas_pdf(Q, im, ini, fora=FORA_PECAS_S)),
        ("aparelhos", lambda im: pecas_do_render(Q, im, ini, FORA_PECAS_S, neutro, "academia: os aparelhos")),
        ("tampas", lambda im: F.tampas_vasos(Q, im)),
        ("paredes", lambda im: F.paredes(Q, im)),
        ("soleiras", lambda im: soleira_elevador(Q, F.soleiras(Q, im))),
        ("esquadrias", lambda im: B.esquadrias_final(im, chave, Q.pg, Q.p2q, Q.px_m)),
        ("escadas", lambda im: escadas_s(Q, im)),
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

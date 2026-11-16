"""A proposta de 15/11 no Subsolo da Casa D: a biblioteca e as notas do cliente (Revisão das Plantas 2).

Usuário: "cadeiras terracota, lavabo granito marrom, pode aplicar", sobre a proposta
(`POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_1511_proposta_1.jpg`, `proposta_biblioteca_casad_1511.py`). Como no Térreo
(`biblioteca_terreo_casad_1511`), as peças e as funções são as das Casas A, B e C, nos desenhos do PDF da Casa D (px da
final de 3840):
- **Como no Subsolo da Casa A** (Miro: "Fazer as mesmas mudanças que foram apontadas no subsolo da casa A"): o fundo
  branco, sem a hachura e o contorno do lote (`fundo_branco`); o perímetro da casa marcado no pátio (`perimetro`; "Demarcar
  melhor o perímetro da casa"); o Bege Bahia com as manchas a 35%, como nas Casas A, B e C (`bege`; "Diminuir a escala
  da textura"; usuário: "o bege bahia deve ficar igual ao das outras casas A, B e C"); as portas de giro quina com quina
  (`portas`; "Melhorar representação das portas de giro. Encostar nas paredes").
- **Escada** ("Não deixar os degraus cortados branco. Deixar transparente mas na mesma cor da escada. Exemplo casa C";
  "Colocar a seta em todas as escadas e a descrição"): os degraus continuam onde era branco, num véu leve; o triângulo
  no 1º degrau e "SOBE PARA O / TÉRREO".
- **Academia** ("usar o mesmo bloco de bicicleta usado na casa A", "Tirar o contorno dos blocos", "Isso aqui não
  existe"): as 2 esteiras A, as 2 bicicletas B e os 2 supinos nos tamanhos da Casa A, o vinílico refeito por baixo; a
  peça com a barra na parede do WC do vestiário sai (a parede continua).
- **Sauna e vestiário** ("Os bancos da sauna é no mesmo material do piso ... em destaque"; "A cuba ... é esculpida no
  travertino"; "Colocar soleira aqui"): os bancos no travertino do piso, em dois tons; a cuba esculpida de travertino; a
  bacia Carrara; os chuveiros desenhados; a soleira no vão entre a academia e a antessala.
- **DCE 1 e WC DCE** ("Deixar o tamanho das letras padronizadas"; o piso marrom tabaco "mais sóbrio", com as bancadas
  em destaque): a cama de solteiro A com a peseira (areia), a cuba no granito, a bacia Monte Carlo, o chuveiro redondo,
  o granito do piso na amostra do cliente (`pedidos_terreo_casab_1211.marrom_tb`) e os dois rótulos no mesmo corpo.

  python3 biblioteca_subsolo_casad_1511.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final e os antes e depois
`POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_1511_<trecho>_antes_depois.jpg` (com --saida, na pasta da saída).
"""

import argparse
import contextlib
import io
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
import final3840_casad as D                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402
import biblioteca_subsolo_casab_1311 as BB       # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import regras_terreo_casab_1311 as RT            # noqa: E402
import mobiliario_terreo_casac_1311 as MB        # noqa: E402
import biblioteca_terreo_casad_1511 as TD        # noqa: E402

CASA_D = AQUI.parents[1] / "POE642_CasaD"
R = CASA_D / "renders"
FINAL = R / "POE642_CasaD_PH_Subsolo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "b606ec6"
PX_M = B1.PX_M
PAREDE = (80, 80, 80)

# o fundo: a pegada (o que a legenda pinta, fechado e sem furos, as manchas de `area_min` px); fora dela, branco puro
FUNDO = {"fechar": 7, "abrir": 3, "area_min": 2000, "suave": 0.8}
# o perímetro: o contorno da pegada, no cinza das paredes (px de largura)
PERIMETRO = {"larg": 2.0, "cor": PAREDE, "ss": 8}
# o Bege Bahia (`pedidos_subsolo_casac_1311.bege`, a chapada 232): fora a sauna, a antessala e o vestiário (o
# travertino deles fica) e a escada (refeita em `escada`)
# (16/11, usuário: "o piso e bancos da sauna/vestiário e circulação (onde tem bege bahia) também devem ter as manchas
# reduzidas no bege bahia") só a escada fica de fora (refeita em `escada`)
BEGE_FORA = [(836, 1236, 1152, 1336)]
# (16/11, usuário: "melhore a representação do bege bahia no piso") o pátio no Bege Bahia do Subsolo da Casa A (a
# amostra, px, tecida sem emenda; o granulado fino dele), com a luz larga do lugar (as sombras junto às paredes)
BEGE_A = {"final": AQUI.parents[1] / "POE642_CasaA" / "renders" / "POE642_CasaA_PH_Subsolo_final_rotulos.png",
          "amostra": (1120, 1110, 1320, 1310), "luz_sigma": 18.0, "tol": 40,
          # os rótulos de antes sobre o Bege Bahia (SAUNA, VESTIÁRIO; px): saem com o piso novo (reescritos centrados)
          "rotulos": [(805, 1624, 868, 1655), (1133, 1630, 1199, 1663),
                      # (16/11, "evitar que tenha alguma mancha ao redor da porta") o tracejado do render junto ao
                      # vão da porta dupla do depósito (não está no PDF)
                      (1070, 1160, 1079, 1243)],
          # (16/11, usuário: "Não pode ter nenhuma mancha de arco da porta [...] Essa planta humanizada não recebe o
          # arco") os arcos das portas (ARQ_PAREDE) no Bege Bahia: o traço do arco no PDF não é a chapada 232, e o
          # arco do render ficava (a sauna, o vestiário e os dois boxes do WC do vestiário); o caminho do arco, com
          # `arco_px` de cada lado, entra no piso novo
          "arco_px": 2}
# a escada: a caixa dos degraus (entre as paredes, px); o branco do corte (`branco`: a luz mínima e o croma máximo); o
# trecho dos degraus inteiros (x) de onde vem o período dos espelhos; (16/11, usuário: "manter divisória da escada em
# diagonal, sem linha, e dali para cima os degraus em transparência") o véu dos degraus depois da diagonal, que entra
# numa rampa de `rampa_px` (a divisa sem o fio escuro do corte)
ESCADA = {"caixa": (839, 1251, 1147, 1324), "branco": (215, 22), "fonte_x": (859, 955), "veu": 0.38, "rampa_px": 2.0}
# a seta e a descrição (`pedidos_terreo_casac_1311.escadas`): o triângulo no 1º degrau, a ponta para onde sobe; o S do
# PDF fica logo abaixo; a descrição no pátio, à esquerda da escada
SETA = [{"nome": "escada", "triangulo": [(843.5, 1262.0), (843.5, 1273.0), (854.0, 1267.5)], "s_px": None,
         "texto": ("SOBE PARA O", "TÉRREO"), "centro_x": 760.0, "base_y": 1270.0, "fundo": None}]
# as portas de giro: a soleira no bege da soleira da porta do DCE 1 (px)
# ("porta em (1681, 995)", a do vestiário: a busca das pontas da parede errava e riscava uma linha de ponta a ponta da
# sauna; fica como está)
PORTAS = {"soleira_px": (935, 1151, 968, 1157), "pular": ("porta em (1681, 995)",)}
# a soleira no vão entre a academia e a antessala da sauna e do vestiário (px), no bege das soleiras, com o fio
# (16/11, usuário: "aqui não tem soleira, somente o vinílico") o vão entre a academia e a antessala no vinílico da
# academia (o de logo acima, `vao`, px)
SOLEIRA = {"vao": (955, 1594, 1092, 1606), "cor": (181, 208, 228), "fio": 0.86, "ss": 8,
           # (16/11, usuário: "faltaram as soleiras: para a sauna e para o vestiário") os vãos das portas nas paredes da
           # sauna e do vestiário (os retângulos brancos da ARQ_PAREDE, na espessura da parede da imagem, px)
           "portas": [(945.0, 1605.0, 955.5, 1655.0), (1092.0, 1606.5, 1101.5, 1655.5)]}
# (16/11, usuário: "corrija as portas conforme 3d"; "As folhas de vidro precisam seguir o estilo das que usamos no
# subsolo da casa A") as portas de correr entre o pátio e a academia (o vão da ARQ_PAREDE, px): o vinílico da academia
# até a face de fora do vão e as folhas como as do pátio da Casa A (`final3840_casaa.PORTAS_VIDRO["portas"][0]` com o
# perfil de `biblioteca_subsolo_casaa_1211.ESQUADRIAS`, na mesma escala: 59,7 px/m nas duas): 4 folhas em 2 trilhos, as
# das pontas no de fora (o do pátio) e as do meio no de dentro, as de cada lado sobrepostas no montante; cada folha com
# o vidro claro, o perfil escuro em volta e o traço dos montantes perto das pontas; os batentes nas duas pontas do vão
PORTA_ACADEMIA = {"vao": (759.1, 1341.7, 768.0, 1592.5), "x": 759.1, "folha_px": 3.0, "batente_px": 2.4,
                  "montante_px": 4.74, "montante_fio_px": 0.63, "perfil_px": 0.9,
                  "perfil": (34, 34, 36), "vidro": (228, 226, 220), "sombra": 0.18, "ss": 8,
                  # a nitidez das folhas da final da Casa A (o perfil em ~100-120 e o vidro em ~150-180 lá, não o preto
                  # e o branco puros do desenho): o trecho das folhas desfocado de leve
                  "suave": 0.5}
# a peça com a barra na parede de cima do WC do vestiário ("Isso aqui não existe"): a parede continua (px); embaixo, o
# piso de `dy` abaixo
NAO_EXISTE = {"parede": (1201, 1598, 1281, 1606), "piso": (1201, 1606, 1281, 1612), "dy": 7}
# (16/11, usuário: "Você verificou todas as portas para saber se está quina a quina com a parede, não tem nenhuma porta
# flutuando não, né?") a folha de vidro da porta do vestiário (a do desenho de antes) ficava solta: 2 px abaixo da
# parede e 3 px à direita da soleira (a da sauna encosta nas duas). O trecho da folha (com as marcas logo abaixo, px)
# sobe `dy` e vai `dx` à esquerda, encostando na parede e na ponta da soleira; onde ela estava, o Bege Bahia de
# `piso_dy` px abaixo
FOLHA_VESTIARIO = {"folha": (1106, 1608, 1147, 1614), "dx": -3, "dy": -2, "limpa": (1103, 1606, 1148, 1614),
                   "piso_dy": 9}
# a academia: os aparelhos de antes (caixas px, com folga) e os novos, nos tamanhos da Casa A
# (`biblioteca_subsolo_casaa_1211.ACADEMIA`): as esteiras 1,76 x 0,77 m, de pé (o console em cima, como no PDF); as
# bicicletas 1,45 vezes o símbolo do PDF, o console para a esquerda; os supinos com o banco de 1,60 m no x e a barra de
# 2,04 m (as colunas da barra e do rack repetidas), a barra à esquerda
ACADEMIA = {"limpa": [(849, 1488, 898, 1522), (849, 1536, 898, 1570), (1139, 1471, 1194, 1580), (1199, 1471, 1254, 1580),
                      (1398, 1447, 1492, 1562), (1398, 1607, 1492, 1724)], "limpa_lado": (1, 1, -1, -1, -1, -1),
            "esteiras": [(1166.4, 1525.2), (1226.1, 1525.2)], "esteira": (46.0, 105.2),
            "bicicletas": [(873.55, 1505.05), (873.55, 1552.85)], "bicicleta": (30.3, 52.9),
            "supinos": [(1439.2, 1504.95), (1439.2, 1665.75)], "supino_m": (1.60, 2.04), "barra": (170, 340)}
# a sauna: o degrau e o assento (junto à parede de baixo) do PDF (px), no travertino do piso (a amostra), o assento
# mais escuro
SAUNA = {"degrau": (778.7, 1664.9, 945.7, 1700.4), "assento": (778.7, 1700.4, 945.7, 1735.9),
         # (16/11, usuário: "os bancos da sauna são do mesmo material do piso, com tom em destaque") o travertino do piso
         # (a amostra do vestiário, tecida), mais escuro (o assento, junto à parede, mais que o degrau), com a face na
         # borda e a sombra curta no piso
         "piso_px": (1140, 1688, 1192, 1734), "tons": {"degrau": 0.86, "assento": 0.78}, "face": 0.80,
         "sombra": 0.30}
# o vestiário: a bancada do PDF (px, a parede à esquerda) com a cuba esculpida de travertino; a bacia Carrara (a parede
# à direita); os chuveiros de parede (a placa, a parede)
VESTIARIO = {"bancada": (1100.9, 1675.2, 1129.5, 1716.4), "bacia": (1249.4, 1626.3, 1280.1, 1647.4),
                          # (16/11, usuário: "a cuba é esculpida no travertino, mas a bancada é no granito marrom tabaco intenso") a
             # bancada inteira do render (de parede a parede, px) no granito marrom tabaco (o da ilha gourmet da Casa B,
             # `revisao_terreo_casac_1311.BANCADA_SERV`), com a face; a cuba esculpida de travertino no retângulo do PDF
             "bancada_toda": (1101, 1659, 1131, 1736), "face": 0.82,
             "bacia_limpa": (1246, 1623, 1283, 1651),
             # (16/11, usuário: "entre as portas do vestiário é parede, no tom de parede, não de piso") a faixa clara
             # entre as duas folhas de correr do box (px): no cinza das paredes
             "entre_portas": (1201, 1665, 1243, 1672)}
CH_Q, CH_R = "banho-1/chuveiro-quadrado-parede-planta", "banho-de-servico/chuveiro-redondo-parede-planta"
CHUVEIROS = [{"nome": "antessala", "placa_px": (981.1, 1707.0, 992.9, 1718.8), "png": CH_Q, "parede": (1735.2, "baixo"),
              "piso": (0, -1)},
             {"nome": "vestiário", "placa_px": (1251.2, 1698.8, 1263.0, 1710.6), "png": CH_Q, "parede": (1279.4, "dir"),
              "piso": (-1, 0)},
             {"nome": "WC DCE", "placa_px": (866.1, 1026.6, 877.9, 1038.4), "png": CH_R, "parede": (849.6, "esq"),
              "piso": (1, 0)}]
# o WC DCE: a cuba no granito (o meio da cuba do PDF, a parede à esquerda), a bacia Monte Carlo (a parede à esquerda);
# as de antes saem (o piso de cima e o da direita)
# (16/11, usuário: "a bancada do WC DCE é granito marrom tabaco intenso, diferente do piso"; "corrija a representação
# da bancada da pia, a soleira da porta, o erro atrás da porta do WC e o contorno do chuveiro") a bancada do PDF (px)
# no granito marrom tabaco intenso, com a face; a cuba branca da biblioteca (só a louça e a torneira do PNG, sem o
# granito dele) por cima; os restos da cuba de antes (o branco, `cuba_restos`) saem; a porta: a soleira no vão entre os
# batentes (px), os batentes no cinza da parede, e os restos escuros atrás da folha aberta (`atras`) saem
WC_DCE = {"bancada": (850.2, 1060.4, 869.9, 1105.0), "cuba_restos": (866, 1064, 884, 1102),
          "cuba": (862.5, 1082.6, 34.7, 24.6),
          "bacia_limpa": (847, 1114, 882, 1140), "bacia": (864.3, 1126.85, 21.1, 30.6),
          "porta": {"soleira": (920.6, 1065.7, 929.6, 1101.5), "batentes": [(920.6, 1058.0, 929.6, 1065.7),
                                                                          (920.6, 1101.5, 929.6, 1108.0)],
                    "atras": (874, 1056, 921, 1065), "tol": 22,
                    # a faixa escura que sobrava atrás da folha (a sombra da folha de antes): as linhas de logo abaixo
                    "faixa": (874, 1059, 921, 1062), "faixa_dy": 3}}
# (16/11, usuário: "a cama ficou com a cabeceira para cima, mas deve ficar para baixo")
# (16/11, usuário: "corrija criado mudo e contorno da cama") o criado de antes (a caixa do PDF, px) sai e entra o da
# Casa A no tom da madeira das bancadas, com o abajur, como nas suítes do Térreo (`mobiliario_terreo_casac_1311.criados`)
DCE = {"caixa": (1018.1, 1029.5, 1077.9, 1148.9), "giro": 180.0, "roupa": "branco", "tom": "areia",
       "criado": (994.9, 1123.5, 1015.8, 1147.4), "abajur": 14.0,
       # o lugar da cama e do criado de antes refeito no granito do piso antes da cama nova (o contorno da cama de antes
       # ficava nas bordas): a amostra limpa do piso do DCE 1 (px), no tom do piso em volta
       "piso_px": (940, 1040, 1010, 1068), "folga": 3}
# (16/11, usuário: "centralize os rótulos") cada rótulo no meio do espaço livre do ambiente (centro x, y do bloco,
# px): a ACADEMIA no eixo da sala, acima das esteiras; a SAUNA acima dos bancos; o VESTIÁRIO entre a bancada e os
# boxes; o ELEVADOR na cabine; o DCE 1 entre a parede e a cama; o WC DCE entre a bancada e a porta; o DEPÓSITO no meio.
# O corpo: o da 1ª linha de antes (a largura da tinta, px) ou `corpo`; DCE 1 e WC DCE no mesmo corpo (o WC DCE
# só cabe nele). `apaga`: a caixa do rótulo de antes (px) e como sai: "dx"/"-dx" (o piso da direita/da esquerda),
# "claro" (o texto branco sobre o granito, inpaint) ou None (o piso novo já o tirou: o Bege Bahia, a cabine do
# elevador)
ROTULOS = {"entrelinha": 1.42, "altura": 0.73, "escuro": (20, 20, 20), "claro": (236, 236, 236), "itens": [
    {"linhas": ("ACADEMIA", "A: 72,23 m²"), "centro": (1198.5, 1406.0), "largura": 56.0, "cor": "escuro",
     "apaga": ((1016, 1439, 1081, 1469), "dx")},
    {"linhas": ("SAUNA", "A: 6,55 m²"), "centro": (865.0, 1636.0), "largura": 37.0, "cor": "escuro", "apaga": None},
    # (16/11, usuário: "alinhe esses dois rótulos") o VESTIÁRIO na fileira da SAUNA (o mesmo y)
    # (16/11, conferência do 12K) o ponto que sobrava da ponta do "A" de antes, à esquerda do "A" novo: o piso da esquerda
    {"linhas": ("VESTIÁRIO", "A: 6,41 m²"), "centro": (1164.5, 1636.0), "largura": 56.0, "cor": "escuro",
     "apaga": ((1136, 1633, 1142, 1641), "-dx")},
    {"linhas": ("ELEVADOR",), "centro": (1397.75, 1282.1), "largura": 56.0, "cor": "escuro", "apaga": None},
    {"linhas": ("DCE 1", "A: 6 m²"), "centro": (976.5, 1092.0), "corpo": 8.4, "cor": "claro",
     "apaga": ((956, 1070, 1006, 1104), "claro")},
    {"linhas": ("WC DCE", "A: 2,88 m²"), "centro": (897.5, 1090.0), "corpo": 8.4, "cor": "claro",
     "apaga": ((877, 1078, 920, 1110), "claro")},
    {"linhas": ("DEPÓSITO/CASA DE", "MÁQUINAS", "A: 20,02 m²"), "centro": (1217.5, 1160.0), "largura": 103.0,
     "cor": "claro", "apaga": ((1158, 1124, 1277, 1175), "claro")}]}
# (16/11, usuário: "melhore a representação do elevador igual das outras casas") a cabine de aço das Casas A a C
# (`final3840_casaa.elevador`, pt do PDF da Casa D): a cabine (INS_INSTALAÇÕES HIDRÁULICAS), a porta na parede da
# direita (o vão do PDF), as folhas telescópicas, a soleira em inox no vão da parede, os corrimãos nas outras três; o
# anel do poço estreito em volta da cabine e o resto do poço em branco, como na Casa C
ELEVADOR = {"poco": (1153.1, 1398.5, 1246.6, 1489.2),
            "externo": (1168.5, 1404.2, 1244.4, 1483.4), "interno": (1173.0, 1408.7, 1239.9, 1478.9),
            "vao": (1239.9, 1424.0, 1244.4, 1463.6),
            "folhas": [(1241.5, 1409.9, 1243.2, 1424.0), (1241.5, 1421.1, 1243.2, 1435.2),
                       (1241.5, 1452.4, 1243.2, 1466.5), (1241.5, 1463.6, 1243.2, 1477.7)],
            "soleira": (1244.4, 1422.5, 1255.2, 1465.1), "anel": (1164.0, 1399.7, 1246.6, 1487.9),
            "corrimaos": ("cima", "esquerda", "baixo")}
ANTES_DEPOIS = {"planta": (536, 960, 1580, 1790), "academia": (830, 1430, 1520, 1600),
                "sauna_vestiario": (755, 1585, 1300, 1752), "dce": (835, 990, 1100, 1165),
                "escada_patio": (536, 960, 1160, 1350)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            D.contexto_d()
            _Q["Q"] = F.Quadro("Subsolo")
    return _Q["Q"]


_Q = {}


# ----------------------------------------------------------------------------------------------------------------------
def pegada(Q, q=FUNDO):
    nb = (Q.chapada.min(axis=2) < 250).astype(np.uint8)
    # os tracejados de fora (a projeção do Térreo e o contorno do lote: traços de 1 px) saem antes de fechar; com eles,
    # o vão até a casa fechava e entrava na pegada (a hachura ficava ali)
    nb = cv2.morphologyEx(nb, cv2.MORPH_OPEN, np.ones((q["abrir"], q["abrir"]), np.uint8))
    nb = cv2.morphologyEx(nb, cv2.MORPH_CLOSE, np.ones((q["fechar"], q["fechar"]), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb, connectivity=8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    return ndimage.binary_fill_holes(m)


def fundo_branco(Q, out, q=FUNDO):
    m = pegada(Q, q)
    p = cv2.GaussianBlur(m.astype(np.float32), (0, 0), q["suave"])
    p = np.maximum(p, m.astype(np.float32))[..., None]
    o = out.astype(np.float32) * p + 255 * (1 - p)
    print(f"    fundo branco: {int((~m).sum())} px fora da pegada (sem a hachura e o contorno do lote)")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def perimetro(Q, out, q=PERIMETRO):
    import pedidos_subsolo_casac_1311 as PS
    m = pegada(Q).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    ss = q["ss"]
    ys, xs = np.nonzero(m)
    X0, Y0, X1, Y1 = xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5
    M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    for c in cs:
        pts = (c.reshape(-1, 2).astype(np.float32) + 0.5 - [X0, Y0]) * ss
        cv2.polylines(M, [np.int32(np.round(pts))], True, 255, max(1, int(round(q["larg"] * ss))), cv2.LINE_AA)
    a = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    out = PS._pintar(out, a, X0, Y0, q["cor"])
    print("    perímetro: o contorno da casa no pátio, no cinza das paredes")
    return out


def bege(Q, out, fora=BEGE_FORA, q=BEGE_A):
    import materiais_terreo_casac_1311 as MT
    B = np.all(Q.chapada == 232, axis=2)
    for x0, y0, x1, y1 in fora:
        B[y0:y1, x0:x1] = False
    B &= ~(BS.quieto(FA.paredes_pdf, Q) > 0.3)
    I = out.astype(np.float32)
    med = np.median(I[B], axis=0)
    perto = np.abs(I - med).max(axis=2) < q["tol"]                # só o piso (fora o que está sobre ele)
    for x0, y0, x1, y1 in q["rotulos"]:
        perto[y0:y1, x0:x1] = True
    B &= perto
    # os arcos das portas (o caminho do PDF, engrossado) onde o Bege Bahia está em volta
    arcos = np.zeros(B.shape, np.uint8)
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or not any(it[0] == "c" for it in d.get("items", [])):
            continue
        (a0, b0), (a1, b1) = Q.p2q(d["rect"].x0, d["rect"].y0), Q.p2q(d["rect"].x1, d["rect"].y1)
        w_, h_ = abs(a1 - a0), abs(b1 - b0)
        if not (14 <= w_ <= 220 and abs(w_ - h_) < 2):
            continue
        for c in Q.caminhos(d):
            cv2.polylines(arcos, [np.int32(np.round(np.asarray(c) * 8))], False, 1, 1 + 2 * q["arco_px"],
                          cv2.LINE_8, shift=3)
    perto_bege = cv2.dilate(B.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    # (só o que é perto do piso: as peças sobre ele, o chuveiro, a bacia, ficam)
    B |= (arcos > 0) & perto_bege & perto & ~(BS.quieto(FA.paredes_pdf, Q) > 0.3)
    ys, xs = np.nonzero(B)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    A = cv2.imread(str(q["final"]))
    a0, b0, a1, b1 = q["amostra"]
    T = MT.sem_emenda(A[b0:b1, a0:a1].astype(np.float32), y1 - y0, x1 - x0)
    # a luz larga do lugar (a média do piso em volta / a mediana), vezes o Bege Bahia da Casa A
    L = I[y0:y1, x0:x1].mean(axis=2)
    m = B[y0:y1, x0:x1].astype(np.float32)
    s = q["luz_sigma"]
    luz = cv2.GaussianBlur(L * m, (0, 0), s) / np.maximum(cv2.GaussianBlur(m, (0, 0), s), 1e-4)
    luz = np.clip(luz / max(float(np.median(L[m > 0])), 1.0), 0.8, 1.1)
    novo = T * luz[..., None]
    a = cv2.GaussianBlur(m, (0, 0), 0.6)[..., None] * m[..., None]
    o = out.astype(np.float32)
    o[y0:y1, x0:x1] = o[y0:y1, x0:x1] * (1 - a) + novo * a
    print(f"    Bege Bahia: o pátio, a sauna, o vestiário e a circulação no Bege Bahia do Subsolo da Casa A "
          f"({int(B.sum())} px), com a luz do lugar")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def escada(out, q=ESCADA):
    x0, y0, x1, y1 = q["caixa"]
    reg = out[y0:y1, x0:x1].astype(np.int16)
    lum, croma = reg.min(axis=2), reg.max(axis=2) - reg.min(axis=2)
    branco = (lum > q["branco"][0]) & (croma < q["branco"][1])
    branco = cv2.morphologyEx(branco.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
    # cada linha do corte para a direita, de 5 px antes do branco (o fio e a sombra da diagonal) até o fim da caixa,
    # fora a parede
    parede = (np.abs(reg - 80).max(axis=2) <= 12)
    for v in range(branco.shape[0]):
        us = np.nonzero(branco[v])[0]
        if len(us):
            branco[v, max(0, us.min() - 5):] = True
    branco &= ~parede
    # o período dos espelhos: a autocorrelação da luz das colunas dos degraus inteiros
    f0, f1 = q["fonte_x"]
    col = reg[:, f0 - x0:f1 - x0].mean(axis=(0, 2))
    col = col - col.mean()
    ac = np.correlate(col, col, "full")[len(col) - 1:]
    per = int(np.argmax(ac[8:40]) + 8)
    o = reg.astype(np.float32)
    inicio = np.full(branco.shape[0], 10 ** 6, np.float32)
    for v in range(branco.shape[0]):
        us = np.nonzero(branco[v])[0]
        if len(us):
            inicio[v] = us.min()
    # a fonte: só os degraus inteiros, à esquerda do ponto mais à esquerda do corte (junto ao corte, a sombra da
    # diagonal se repetiria em listras)
    corte = int(np.nonzero(branco.any(axis=0))[0].min()) - 3
    for v, u in zip(*np.nonzero(branco)):
        k = u
        while k >= corte:
            k -= per
        if k >= 0:
            w = q["veu"] * float(np.clip((u - inicio[v] + 0.5) / q["rampa_px"], 0, 1))
            o[v, u] = reg[v, k] * (1 - w) + 255 * w
    out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    escada: os degraus continuam no corte branco ({int(branco.sum())} px, espelhos a cada {per} px), com um "
          f"véu de {q['veu']:.0%}")
    return out


def seta(out, q=SETA):
    import pedidos_terreo_casac_1311 as PT
    return PT.escadas(out, q)


def portas(Q, out, q=PORTAS):
    import pedidos_terreo_casac_1311 as PT
    return PT.portas(Q, out, dict(PT.PORTAS, soleira_px=q["soleira_px"], pular=q["pular"]))


def porta_academia(out, par, q=PORTA_ACADEMIA):
    out = BB.piso_desloc(out, q["vao"], par, 1, 0)
    vx0, vy0, vx1, vy1 = q["vao"]
    bt, w, mo = q["batente_px"], q["folha_px"], q["montante_px"]
    y0, y1 = vy0 + bt, vy1 - bt
    L = (y1 - y0 + 2 * mo) / 4                       # a folha: o vão em 4, com a sobreposição dos montantes
    x0 = q["x"]
    fora, dentro = (x0, x0 + w), (x0 + w, x0 + 2 * w)
    folhas = [(fora, y0, y0 + L), (dentro, y0 + L - mo, y0 + 2 * L - mo), (dentro, y1 - 2 * L + mo, y1 - L + mo),
              (fora, y1 - L, y1)]

    def ret(a0, b0, a1, b1, cor, forca=1.0):
        nonlocal out
        if forca >= 1.0:
            out = TD._poligono(out, [(a0, b0), (a1, b0), (a1, b1), (a0, b1)], cor, q["ss"])
        else:                                        # a sombra: o piso escurecido
            reg = out.copy()
            out = TD._poligono(out, [(a0, b0), (a1, b0), (a1, b1), (a0, b1)], (0, 0, 0), q["ss"])
            out = np.clip(reg.astype(np.float32) * (1 - forca) + out.astype(np.float32) * forca, 0,
                          255).astype(np.uint8)
    # a sombra curta das folhas (a luz do alto à direita), como a da Casa A
    ret(x0 - 0.9, y0 + 0.9, x0 + 2 * w - 0.9, y1 + 0.9, None, q["sombra"])
    for b0, b1 in ((vy0, y0), (y1, vy1)):                          # os batentes, no perfil
        ret(vx0, b0, vx1, b1, q["perfil"])
    p, f = q["perfil_px"], q["montante_fio_px"]
    for (a0, a1), b0, b1 in folhas:
        ret(a0, b0, a1, b1, q["perfil"])
        ret(a0 + p, b0 + p, a1 - p, b1 - p, q["vidro"])
        for yy in (b0 + mo, b1 - mo):                              # os montantes
            ret(a0, yy - f / 2, a1, yy + f / 2, q["perfil"])
    X0, X1 = int(np.floor(x0)) - 2, int(np.ceil(x0 + 2 * w)) + 2
    Y0, Y1 = int(np.floor(y0)) - 1, int(np.ceil(y1)) + 1
    trecho = out[Y0 - 3:Y1 + 3, X0 - 3:X1 + 3].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(cv2.GaussianBlur(trecho, (0, 0), q["suave"])[3:-3, 3:-3]), 0,
                                255).astype(np.uint8)
    print(f"    academia: as portas de correr do pátio como as do pátio do Subsolo A (4 folhas de {L / PX_M:.2f} m em 2 "
          "trilhos, o vidro claro com o perfil escuro e os montantes; os batentes nas pontas)")
    return out


def folha_vestiario(out, q=FOLHA_VESTIARIO):
    src = out.copy()
    x0, y0, x1, y1 = q["limpa"]
    d = q["piso_dy"]
    out[y0:y1, x0:x1] = src[y0 + d:y1 + d, x0:x1]
    x0, y0, x1, y1 = q["folha"]
    dx, dy = q["dx"], q["dy"]
    out[y0 + dy:y1 + dy, x0 + dx:x1 + dx] = src[y0:y1, x0:x1]
    print(f"    vestiário: a folha de vidro encostada na parede e na ponta da soleira ({-dy} px acima, {-dx} px à "
          "esquerda; a da sauna já encostava)")
    return out


def soleira(out, par, q=SOLEIRA):
    out = BB.piso_desloc(out, q["vao"], par, 0, -1)
    for x0, y0, x1, y1 in q["portas"]:
        out = TD._poligono(out, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], tuple(v * q["fio"] for v in q["cor"]),
                           q["ss"])
        out = TD._poligono(out, [(x0 + 0.8, y0 + 0.8), (x1 - 0.8, y0 + 0.8), (x1 - 0.8, y1 - 0.8),
                                 (x0 + 0.8, y1 - 0.8)], q["cor"], q["ss"])
    print("    soleiras: nas portas da sauna e do vestiário; o vão entre a academia e a antessala no vinílico")
    return out


def nao_existe(out, q=NAO_EXISTE):
    x0, y0, x1, y1 = q["parede"]
    out[y0:y1, x0:x1] = PAREDE
    a0, b0, a1, b1 = q["piso"]
    out[b0:b1, a0:a1] = out[b0 + q["dy"]:b1 + q["dy"], a0:a1]
    print("    vestiário: a peça com a barra na parede do WC sai; a parede continua")
    return out


def academia(Q, out, par, q=ACADEMIA):
    # os aparelhos de antes: o vinílico do lado (as réguas deitadas seguem na mesma linha); num buraco grande, a luz do
    # `piso_vinilico` não chegava ao miolo e ele ficava preto
    for c, lado in zip(q["limpa"], q["limpa_lado"]):
        out = BB.piso_desloc(out, c, par, lado, 0)
    P = BS.ler_png("academia/esteira-a.png")
    wt, ht = q["esteira"]
    for cx, cy in q["esteiras"]:
        out = MB.pousar(out, P, cx, cy, wt, ht, 0.0, "movel", par)
    P = BS.ler_png("academia/bicicleta-b.png")
    wt, ht = q["bicicleta"]
    for cx, cy in q["bicicletas"]:
        out = MB.pousar(out, P, cx, cy, wt, ht, 90.0, "movel", par)
    # o supino: a barra e o travessão do rack alongados (as colunas `barra` repetidas) até a proporção da Casa A
    P = BS.ler_png("academia/banco-supino.png", cortar=False)
    ys, xs = np.nonzero(P[..., 3] > 0)
    P = np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    lb, la = q["supino_m"]
    alt, larg = P.shape[:2]
    d = max(0, int(round((la / lb * alt - larg) / 2)))
    a0, a1 = q["barra"]
    a0, a1 = a0 - xs.min(), a1 - xs.min()

    def col(x):
        return np.repeat(P[:, x:x + 1], d, axis=1)
    P = np.ascontiguousarray(np.concatenate([P[:, :a0], col(a0), P[:, a0:a1], col(a1), P[:, a1:]], axis=1))
    s = lb * PX_M / P.shape[0]
    for cx, cy in q["supinos"]:
        out = MB.pousar(out, P, cx, cy, P.shape[1] * s, P.shape[0] * s, 90.0, "movel", par)
    print("    academia: os aparelhos de antes saem (o vinílico refeito); 2 esteiras A, 2 bicicletas B e 2 supinos nos "
          f"tamanhos da Casa A (o supino {lb:.2f} x {P.shape[1] * s / PX_M:.2f} m)")
    return out


def sauna(out, par, q=SAUNA):
    import revisao_terreo_casac_1511 as R15
    H, W = par.shape
    a0, b0, a1, b1 = q["piso_px"]
    o = out.astype(np.float32)
    for nome in ("degrau", "assento"):
        x0, y0, x1, y1 = q[nome]
        X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
        a = np.zeros((H, W), np.float32)
        a[Y0:Y1, X0:X1] = 1
        a *= ~par
        o *= (1 - q["sombra"] * R15._sombra(a, W, H))[..., None]
        T_ = TD._tecido(out, (a0, b0, a1, b1), Y1 - Y0, X1 - X0, 1518 + len(nome)) * q["tons"][nome]
        m = a[Y0:Y1, X0:X1] > 0
        borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        T_[borda] *= q["face"]
        reg = o[Y0:Y1, X0:X1]
        reg[m] = T_[m]
    print("    sauna: o degrau e o assento no travertino do piso, mais escuros (em destaque), com a face e a sombra")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def vestiario(out, par, q=VESTIARIO):
    X0, Y0, X1, Y1 = q["bancada_toda"]
    m = np.zeros(par.shape, bool)
    m[Y0:Y1, X0:X1] = True
    m &= ~par
    out = TD._pinta_textura(out, m, tabaco(Y1 - Y0, X1 - X0), q["face"])
    x0, y0, x1, y1 = q["bancada"]
    P = BS.ler_png("banho-feminino-academia/cuba-esculpida-travertino.png")
    out = MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, 90.0, "baixa", par)
    out = BB.piso_desloc(out, q["bacia_limpa"], par, -1, 0)
    x0, y0, x1, y1 = q["bacia"]
    out = MB.pousar(out, B1.ler_png("banho-master/bacia-carrara"), (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0,
                    -90.0, "baixa", par)
    x0, y0, x1, y1 = q["entre_portas"]
    reg = out[y0:y1, x0:x1]
    reg[reg.astype(np.int16).mean(axis=2) > 175] = PAREDE
    print("    vestiário: a bancada no granito marrom tabaco, a cuba esculpida de travertino; a bacia Carrara; a parede "
          "entre as folhas do box")
    return out


def chuveiros(out, par, q=CHUVEIROS):
    import biblioteca_terreo_casac_1311 as BC
    return BC.chuveiros(out, par, [], q)


def tabaco(h, w, semente=None):
    """O granito marrom tabaco intenso (o da ilha gourmet da Casa B, como na bancada do lavabo da Casa C), h x w."""
    import revisao_terreo_casac_1311 as RC
    import pedidos_terreo_casab_1211 as PB2
    qs = RC.BANCADA_SERV
    with contextlib.redirect_stdout(io.StringIO()):
        return PB2._tabaco(cv2.imread(str(qs["final_b"])), qs["fonte"], h, w,
                           qs["semente"] if semente is None else semente).astype(np.float32)


def _cuba_branca():
    """A louça e a torneira da cuba da biblioteca (`cuba-servico-granito`), sem o granito em volta."""
    P = BS.ler_png("banho-de-servico/cuba-servico-granito.png")
    I = P[..., :3]
    lum, croma = I.mean(axis=2), I.max(axis=2) - I.min(axis=2)
    m = (P[..., 3] > 128) & (lum > 150) & (croma < 40)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 0.01 * m.size])
    m = ndimage.binary_fill_holes(m)
    Q2 = P.copy()
    Q2[..., 3] = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0) * 255 * m
    ys, xs = np.nonzero(m)
    return np.ascontiguousarray(Q2[ys.min():ys.max() + 1, xs.min():xs.max() + 1]), (P.shape[1], P.shape[0]), \
        (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def wc_dce(out, par, q=WC_DCE):
    # os restos brancos da cuba de antes
    x0, y0, x1, y1 = q["cuba_restos"]
    reg = np.ascontiguousarray(out[y0:y1, x0:x1])
    I = reg.astype(np.int16)
    claro = ((I.min(axis=2) > 140) & ((I.max(axis=2) - I.min(axis=2)) < 45)).astype(np.uint8)
    claro = cv2.dilate(claro, np.ones((3, 3), np.uint8)) & (~par[y0:y1, x0:x1]).astype(np.uint8)
    out[y0:y1, x0:x1] = cv2.inpaint(reg, claro * 255, 3, cv2.INPAINT_TELEA)
    # a bancada no granito marrom tabaco intenso e a cuba branca por cima
    x0, y0, x1, y1 = q["bancada"]
    X0, Y0, X1, Y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    m = np.zeros(par.shape, bool)
    m[Y0:Y1, X0:X1] = True
    m &= ~par
    out = TD._pinta_textura(out, m, tabaco(Y1 - Y0, X1 - X0), 0.82)
    P, (W0, H0), (a0, b0, a1, b1) = _cuba_branca()
    cx, cy, wt, ht = q["cuba"]
    s_ = wt / W0                                          # a escala do PNG inteiro (wt no comprido, girado 90°)
    pw, ph = (a1 - a0) * s_, (b1 - b0) * s_
    dx, dy = ((a0 + a1) / 2 - W0 / 2) * s_, ((b0 + b1) / 2 - H0 / 2) * s_
    # girado 90° (anti-horário): o (dx, dy) do PNG vai para (dy, -dx) na tela
    out = MB.pousar(out, P, cx + dy, cy - dx, pw, ph, 90.0, "baixa", par)
    out = BB.piso_desloc(out, q["bacia_limpa"], par, 1, 0)
    cx, cy, wt, ht = q["bacia"]
    out = MB.pousar(out, MB.ler("banho-do-motorista/bacia-monte-carlo-sem-valvula"), cx, cy, wt, ht, 90.0, "baixa",
                    par)
    print("    WC DCE: a bancada no granito marrom tabaco intenso com a cuba branca; a bacia Monte Carlo")
    return out


def wc_porta(out, q=WC_DCE):
    p = q["porta"]
    for x0, y0, x1, y1 in p["batentes"]:
        out[int(round(y0)):int(round(y1)), int(round(x0)):int(round(x1))] = PAREDE
    x0, y0, x1, y1 = p["soleira"]
    c = SOLEIRA["cor"]
    out = TD._poligono(out, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], tuple(v * SOLEIRA["fio"] for v in c))
    out = TD._poligono(out, [(x0 + 0.8, y0 + 0.8), (x1 - 0.8, y0 + 0.8), (x1 - 0.8, y1 - 0.8), (x0 + 0.8, y1 - 0.8)], c)
    # atrás da folha aberta: o que foge do piso (os restos da folha e dos batentes de antes) sai
    x0, y0, x1, y1 = p["atras"]
    reg = np.ascontiguousarray(out[y0:y1, x0:x1])
    I = reg.astype(np.float32)
    med = np.median(I.reshape(-1, 3), axis=0)
    resto = (np.abs(I - med).max(axis=2) > p["tol"]).astype(np.uint8)
    out[y0:y1, x0:x1] = cv2.inpaint(reg, cv2.dilate(resto, np.ones((3, 3), np.uint8)) * 255, 3, cv2.INPAINT_TELEA)
    x0, y0, x1, y1 = p["faixa"]
    out[y0:y1, x0:x1] = out[y0 + p["faixa_dy"]:y1 + p["faixa_dy"], x0:x1]
    print("    WC DCE: a soleira no vão da porta, os batentes na parede, os restos atrás da folha fora")
    return out


def elevador(Q, out, q=ELEVADOR):
    import final3840_casaa as FA
    x0, y0, x1, y1 = BS.caixa_px(Q, q["poco"])
    out = out.copy()
    out[int(np.ceil(y0)):int(np.floor(y1)), int(np.ceil(x0)):int(np.floor(x1))] = 255
    guarda = FA.ELEVADOR
    FA.ELEVADOR = dict(FA.ELEVADOR, **{k: v for k, v in q.items() if k != "poco"})
    try:
        return FA.elevador(Q, np.ascontiguousarray(out))
    finally:
        FA.ELEVADOR = guarda


def cama_dce(out, par, q=DCE):
    f = q["folga"]
    m = np.zeros(par.shape, bool)
    for x0, y0, x1, y1 in (q["caixa"], q["criado"]):
        m[int(y0) - f:int(np.ceil(y1)) + f, int(x0) - f:int(np.ceil(x1)) + f] = True
    m &= ~TD.RT.dilatar(par, 1)
    ys, xs = np.nonzero(m)
    Y0, Y1, X0, X1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    a0, b0, a1, b1 = q["piso_px"]
    T_ = TD._tecido(out, q["piso_px"], Y1 - Y0, X1 - X0, 1519)
    big = np.zeros(out.shape, np.float32)
    big[Y0:Y1, X0:X1] = T_
    o = out.astype(np.float32)
    o[m] = big[m]
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    out = TD.cama_dce(out, par, q)
    x0, y0, x1, y1 = q["criado"]
    with contextlib.redirect_stdout(io.StringIO()):
        P, _, _ = B1.preparar("suite-master/criado-retangular-vista-superior", 1, 1, "tom_bancada")
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = MB.pousar(out, P, cx, cy, x1 - x0, y1 - y0, 180.0, "movel", par)
    out = B1.abajur(out, cx, cy, q["abajur"])
    print("    DCE 1: o criado da Casa A com o abajur")
    return out


def marrom(Q, out):
    import pedidos_terreo_casab_1211 as PB
    return PB.marrom_tb(Q, out)


def rotulos(out, par, q=ROTULOS):
    import revisao_terreo_casac_1411 as R14
    from PIL import ImageFont
    from rodape_entrega import FONTES
    fonte = str(FONTES / "Inter-Regular.otf")
    f400 = ImageFont.truetype(fonte, 400)
    feitos = []
    for it in q["itens"]:
        if it["apaga"]:
            (x0, y0, x1, y1), modo = it["apaga"]
            if modo in ("dx", "-dx"):
                out = BB.piso_desloc(out, (x0, y0, x1, y1), par, 1 if modo == "dx" else -1, 0)
            else:
                reg = np.ascontiguousarray(out[y0:y1, x0:x1])
                I = reg.astype(np.int16)
                # o branco do texto e os pontos escuros do halo dele (o que foge da mediana do granito)
                med = np.median(I.reshape(-1, 3), axis=0)
                claro = (((I.min(axis=2) > 140) & ((I.max(axis=2) - I.min(axis=2)) < 50)) |
                         (np.abs(I - med).max(axis=2) > 28)).astype(np.uint8) & (~par[y0:y1, x0:x1]).astype(np.uint8)
                out[y0:y1, x0:x1] = cv2.inpaint(reg, cv2.dilate(claro, np.ones((3, 3), np.uint8)) * 255, 3,
                                                cv2.INPAINT_TELEA)
        if "corpo" in it:
            corpo = it["corpo"]
        else:
            l_, _, r_, _ = f400.getbbox(it["linhas"][0])
            corpo = 400 * it["largura"] / (r_ - l_)
        n = len(it["linhas"])
        e = q["entrelinha"] * corpo
        cx, cy = it["centro"]
        b0 = cy - ((n - 1) * e - q["altura"] * corpo) / 2
        out = R14.desenhar_linhas(out, [(t, fonte, corpo, cx, b0 + i * e) for i, t in enumerate(it["linhas"])],
                                  q[it["cor"]])
        feitos.append(f"{it['linhas'][0]} ({corpo:.1f} px)")
    print(f"    rótulos centrados: {', '.join(feitos)}")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    out = fundo_branco(Q, out)
    out = bege(Q, out)
    out = escada(out)
    out = nao_existe(out)
    # o granito do piso antes das peças (as peças novas por cima dele; antes, o piso novo cobria a bancada do WC DCE e
    # deixava o quadrado do chuveiro de antes em volta do novo)
    out = marrom(Q, out)
    out = academia(Q, out, par)
    out = sauna(out, par)
    out = vestiario(out, par)
    out = chuveiros(out, par)
    out = wc_dce(out, par)
    out = cama_dce(out, par)
    out = portas(Q, out)
    out = wc_porta(out)
    out = soleira(out, par)
    out = folha_vestiario(out)
    out = porta_academia(out, par)
    out = elevador(Q, out)
    out = perimetro(Q, out)
    out = seta(out)
    out = rotulos(out, par)
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
        cv2.imwrite(str(Path(pasta) / f"POE642_CasaD_PH_Subsolo_1511_{nome}_antes_depois.jpg"),
                    np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
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

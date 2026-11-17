"""Térreo da Casa B, as correções de 16/11 e 17/11 vendo o 12K (depois das bancadas de Danae, `danae_bancadas_1611.py
B_Terreo`), na final e direto nos 12K A e B, cada peça desenhada na escala de cada imagem:

1. `porta_cozinha` ("APROVEITA E CORRIJA ESSA FALHA NA PORTA DE CORRER DA COZINHA"): a folha de correr da passagem da
   gourmet para a cozinha e os 2 batentes do vão, de novo pelo PDF (o de cima na ponta do toco de parede: "ELE É NA
   PAREDE, NÃO AO LADO"), no padrão das esquadrias da Casa B (o branco com o
   contorno preto fino, `regras_terreo_casab_1311.ESQUADRIAS_TB`); antes, o piso em volta da folha (no 12K, a folha
   virou um tubo de contorno grosso, com um nó na ponta de cima, um ponto claro ao lado e uma mancha laranja embaixo).
2. `cubas_lavatorio` ("CORRIJA A LATERAL DA CUBA DO LAVATÓRIO"): nas 2 cubas esculpidas do lavatório gourmet, o lado
   direito do trecho que passa da bancada era uma coluna clara e neutra (no 12K, uma fresta); ele recebe o lado esquerdo
   em espelho (o fio escuro e o piso de fora), cuba a cuba.
3. `armarios` ("CORRIJA O TOM DOS ARMARIOS DO TERREO DA CASA B, PARA O TOM QUE DEFINIMOS DESDE A CASA A. REMOVENDO
   VEIOS E DEIXANDO A COR SÓLIDA"): os 7 armários de madeira com veio (o aparador do living, o do alto da suíte 3, os
   da suíte master e da sala íntima, os 2 de costas entre as suítes 1 e 2 e o de baixo da suíte 1), nos retângulos do
   PDF, na cor sólida dos armários (`revisao_terreo_casac_1311.COZINHA`: o miolo liso, a face um tom abaixo, a sombra
   curta); o que é cadeira por cima (o couro) fica. Os de closet seguem com os cabides; o louceiro e a despensa já são
   lisos (num tom rosado) e ficam.
4. `portas_servico` ("CORRIJA ESSAS FALHAS AO REDOR DAS PORTAS"): as folhas de giro do BH serviço e do quarto de serviço,
   abertas junto à parede de cima: o traço escuro tracejado que corria embaixo de cada uma (o resto da folha antiga)
   sai, a folha é desenhada de novo na madeira dela, com o contorno fino e a sombra curta; os pontinhos claros do piso
   do quarto junto ao vão saem.
5. `maquinas` ("CORRIJA PISO NO CONTORNO DAS MÁQUINAS DE LAVAR. CORRIJA A ESCALA DAS MÁQUINAS PARA CABER ACIMA DA
   BANCADA"; "NÃO ENCUBRA AS MAQUINAS"): o piso atrás das máquinas (um retângulo mais escuro) vem de um trecho limpo do
   piso da área de serviço, no tom do piso em volta; as 2 máquinas, tiradas da própria imagem, voltam no tamanho do PDF
   (0,60 m), centradas na largura da bancada dos tanques e acima dela, visíveis, com a sombra curta.
6. `cuba_bh_servico` ("SUBSTITUA PELA CUBA DA BIBLIOTECA"): a cuba do BH serviço pela cuba de serviço da biblioteca
   (`POE642_CasaA/biblioteca-objetos/01-subsolo/banho-de-servico/cuba-servico-granito.png`: só a louça e a torneira,
   tiradas do granito da foto), com a torneira para a parede, como no PDF; a cuba antiga sai (o granito da bancada e o
   piso de logo ao lado).

7. `louceiro_despensa` ("SIM, PASSE O LOUCEIRO E A DESPENSA PARA O TOM PADRÃO"): os armários em L do louceiro e da
   despensa (os polígonos da ARQ_LAYOUT HUMANIZAÇÃO), do rosado na cor sólida dos armários, como os outros (o que
   foge do rosado por cima fica).
8. `porta_adega` ("CORRIJA ESSE RESIDUO DE PISO ANTIGO ABAIXO DA PORTA"): a folha de giro da área de serviço, aberta
   junto à parede de baixo da adega, como as do serviço (o traço velho tracejado embaixo sai, a folha de novo).
9. `gourmet_altura` ("SE NÃO TEM FALHA, SÓ DÊ A IDEIA DE QUE A BANCADA ESTÁ MAIS ALTA DO QUE O PISO"): na frente da
   bancada de trás da gourmet (a da cuba e da grelha), o fio escuro da quina, um brilho de 1 px na beira do tampo e a
   sombra curta no piso à frente.
10. `lavabo_bancada` ("CORRIJA A BANCADA NO TOM DA CUBA"): no lavabo, a peça de bancada abaixo da cuba esculpida (mais
   clara, com pontinhos e riscos) no tom da cuba: a luz suave dela, sem os pontinhos e riscos, no tom mediano da
   pedra da cuba (a regra da Casa A), com o grão fino dessa pedra.

11. `pia_sala_intima` ("PRECISAMOS MELHORAR A REPRESENTAÇÃO DESSA BANCADA E PIA, SEM LINHA TÉCNICA. AQUI É PLANTA
   HUMANIZADAS"): a bancada estreita do bar da sala íntima sem o retângulo de linha técnica (a pedra limpa do alto
   dela, em espelho, de ponta a ponta) e a cuba redonda chapada pela cuba redonda da biblioteca
   (`03-primeiro-pavimento/banho-master/cuba-entrada.png`, só a louça e a torneira), no círculo do PDF, a torneira para
   a parede.
12. `banco_deck` ("REMOVA ESSE TRAÇO BRANCO NA PARTE DE BAIXO DO BANCO"): a linha clara sob o banco do pé do deck (a
   linha 1710, x 615 a 897) vira a grama de logo abaixo.

13. `armario_quarto_servico` ("ESSE ARMARIO DO QUARTO DE SERVIÇO NÃO É COM CABIDES?", e depois "NÃO É DE CABIDES
   MESMO"): o armário do quarto de serviço (o retângulo da ARQ_LAYOUT HUMANIZAÇÃO, 0,90 x 0,50 m, junto à parede da
   esquerda), que era um bloco cinza, liso na cor sólida dos armários, como os outros (`armarios`).

14. `margem_lote` ("REMOVA ESSES TRAÇOS FORA DA PLANTA"; "PRECISA REMOVER ESSA SOBRA AQUI DE MURO"): fora do lote (das
   pontas do muro de cima, medidas na própria imagem), tudo no fundo branco: as 2 marcas de canto em L à esquerda, os
   fantasmas claros do tracejado antigo e as 2 linhas que o muro de baixo puxava além da ponta; a ponta do muro de baixo
   com a mesma passagem para o branco da do de cima; nas bordas do gramado, a coluna clara da esquerda e a coluna verde
   clara (e o entalhe branco junto ao muro) da direita viram grama.
15. `grama_muro` ("CORRIJA ESSE TRAÇO VERDE, RESÍDUO DA ANTIGA GRAMA, RENTE AO MURO DO TERRENO"): a faixa verde clara
   de 4 px (na final) logo acima do muro de baixo, de ponta a ponta, vira a grama de logo acima dela.
16. `portoes_descoberta` ("TEMOS UMA LINHA TÉCNICA AQUI. O QUE ELA É?", "TEMOS PORTÕES AQUI", "PRECISAMOS
   REPRESENTÁ-LOS"): os 2 portões de correr da área de serviço descoberta (ARQ_ELEMENTOS FIXOS: em cada lado, 2 folhas
   desencontradas, da parede da casa ao muro, e os batentes nas pontas), que estavam em linha técnica (a folha de cima
   em traço claro, a de baixo fundida à faixa cinza da borda do piso), no padrão da Casa B para os portões de correr da
   área descoberta (em alumínio, com o contorno fino, a linha do meio de cada folha e a sombra curta). Antes, a faixa
   cinza de 2 a 3 px em volta do piso (o contorno fino do contrapiso no PDF, engrossado no render) sai: o piso vai até a
   face de fora de cada portão e até a borda de baixo do PDF e encontra a grama direto, como a pedra da garagem. No 12K
   o desenho vai no afim afinado ali (`Mapa.local`: a final ampliada casada com o 12K, 1 a 2 px além do afim geral).

  python3 correcoes_terreo_casab_1611.py final [--saida <png>]
  python3 correcoes_terreo_casab_1611.py doze [--opcao AB] [--saida <jpg com {}>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                          # noqa: E402
from janela_pia_casaa_1611 import alfa_contorno, alfa_ret, compor   # noqa: E402

FINAL = DF.PLANTAS["B_Terreo"]
DOZE = DF.DOZE_K["B_Terreo"]
RAIZ = AQUI.parents[1]

PRETO = (34, 34, 36)                              # o contorno das esquadrias da Casa B (ESQUADRIAS_TB["perfil"])
BRANCO = (236, 236, 234)
PORTA_COZINHA = {"folha": (1550.6, 1449.7, 1553.0, 1524.3),
                 # (17/11, usuário: "ESSE BATENTE FICOU FORA DA PAREDE. ELE É NA PAREDE, NÃO AO LADO") o de cima na
                 # ponta do toco de parede (na largura dele na final, x 1548,75 a 1562,3), não à esquerda dele como no
                 # PDF; o de baixo na ponta da parede de baixo
                 "batentes": [(1548.75, 1400.4, 1562.3, 1401.9), (1538.4, 1473.5, 1551.2, 1475.0)],
                 # o toco reto até o batente (a quina de baixo à esquerda dele tinha um dente marrom), na cor da parede
                 "parede": [(1548.75, 1393.6, 1552.5, 1400.4)], "parede_amostra": (1553.0, 1384.0, 1560.0, 1392.0),
                 # (o retângulo, o deslocamento da fonte do piso)
                 "limpa": [((1550.5, 1444.0, 1559.0, 1530.0), (9.0, 0.0)),
                           ((1538.0, 1442.0, 1550.5, 1473.3), (21.0, 0.0)),
                           # onde ficava o batente de cima (e a tirinha de parede à esquerda do toco) e o borrão claro
                           # sob ele no 12K: o piso de logo abaixo
                           ((1536.0, 1398.6, 1550.2, 1408.0), (0.0, 10.0)),
                           ((1550.2, 1402.0, 1564.0, 1408.0), (0.0, 9.0))]}
# as cubas: (coluna da borda esquerda, coluna da borda direita) do trecho que passa da bancada, as linhas
CUBAS_LAV = {"cubas": [(1278, 1310), (1339, 1370)], "linhas": (1608, 1618), "faixa": 3}
ARMARIOS = {"aparador do living": (1790.7, 1246.8, 1909.5, 1275.5),
            "suíte 3 (alto)": (2442.2, 621.2, 2597.5, 651.1),
            "suíte master": (1204.0, 388.3, 1233.8, 510.6),
            "sala íntima": (1562.3, 349.5, 1592.1, 510.7),
            "suíte 1 (parede da direita)": (2210.1, 362.2, 2239.9, 517.5),
            "suíte 2 (parede da esquerda)": (2248.9, 362.2, 2281.1, 517.5),
            "suíte 1 (embaixo)": (2031.0, 582.4, 2171.3, 612.2)}
PORTAS_SERVICO = {"folhas": {"BH serviço": (1866.8, 1506.4, 1902.6, 1508.8),
                             "quarto de serviço": (2001.1, 1506.4, 2042.9, 1508.8)},
                  "limpa": [((1864.8, 1500.6, 1902.5, 1514.5), (0.0, 15.0)),
                            ((1999.1, 1500.6, 2042.8, 1514.5), (0.0, 15.0)),
                            ((1911.6, 1508.0, 1917.0, 1541.0), (7.0, 0.0))],
                  "madeira": (128, 160, 196), "borda": 0.62, "borda_px": 0.4, "sombra": 0.28}
MAQUINAS = {"area": (2199.0, 1370.0, 2241.7, 1461.6), "fonte": (2104.0, 1372.0, 2183.0, 1428.0),
            "ref": (2187.0, 1380.0, 2198.0, 1450.0), "suave_px": 3.0,
            "novas": [(2201.1, 1376.2, 2236.9, 1412.0), (2201.1, 1417.7, 2236.9, 1453.6)], "sombra": 0.25}
CUBA_BHS = {"png": RAIZ / "POE642_CasaA/biblioteca-objetos/01-subsolo/banho-de-servico/cuba-servico-granito.png",
            "cuba": (1838.2, 1519.9, 1861.9, 1543.7), "apaga": (1835.0, 1516.0, 1866.0, 1548.0),
            "bancada_x1": 1856.0, "dy_granito": 16.0, "dx_piso": 12.0, "sombra": 0.25}


LOUCEIRO_DESPENSA = {"louceiro": [(1830.9, 1490.0), (1830.9, 1370.5), (1860.8, 1370.5), (1860.8, 1466.1),
                                  (1933.9, 1466.1), (1933.9, 1490.0)],
                     "despensa": [(1939.9, 1490.0), (1939.9, 1466.1), (2019.0, 1466.1), (2019.0, 1370.5),
                                  (2042.9, 1370.5), (2042.9, 1490.0)],
                     "outro": 40.0}
PORTA_ADEGA = dict(PORTAS_SERVICO, folhas={"área de serviço (junto à adega)": (2126.5, 1297.4, 2180.2, 1299.8)},
                   limpa=[((2124.5, 1290.6, 2180.1, 1306.5), (0.0, 16.0))])
GOURMET_ALTURA = {"frente": (1296.5, 1486.0, 1538.4), "sombra_px": 4.5, "sombra": 0.30, "fio_px": 0.6, "fio": 0.62,
                  "brilho_px": 1.2, "brilho": 1.07}
LAVABO_BANCADA = {"peca": (2251.9, 853.7, 2270.4, 898.8), "ref": (2253.8, 799.0, 2258.6, 818.0), "borda_px": 1.0}

PIA_SALA_INTIMA = {"interior": (1563.5, 586.5, 1594.5, 727.5), "fonte": (1563.5, 588.0, 1594.5, 652.0),
                   "cuba": (1567.8, 662.5, 1588.1, 682.8),
                   "png": RAIZ / "POE642_CasaA/biblioteca-objetos/03-primeiro-pavimento/banho-master/cuba-entrada.png",
                   "sat_max": 18, "lum_min": 110, "sombra": 0.25}
BANCO_DECK = {"traco": (615.0, 1709.6, 897.0, 1711.0), "dy": 3.0}
ARMARIO_QS = {"ret": (1911.5, 1552.5, 1941.6, 1606.2)}
# a margem: as referências (px da final) para achar, na própria imagem, as pontas dos muros e as bordas do gramado
LOTE = {"muro_cima": (80, 110), "muro_baixo": (1878, 1900), "meio_x": (400, 3400), "linha_muro_cima": 100,
        "linha_muro_baixo": 1883,
        "grama": (108, 1876), "amostra_grama": (300, 900), "amostra_esq": (1100, 1700), "borda_esq_px": 4, "borda_dir_px": 5}
GRAMA_MURO = {"x": (298, 3513), "busca": (1870, 1884), "faixa_px": 4.5}
# os portões (ARQ_ELEMENTOS FIXOS, px da final); "piso": o contrapiso da área descoberta (ARQ_CONTRAPISO)
PORTOES_AD = {
    "piso": (1822.0, 1678.05, 2138.4, 1848.2),
    "borda_baixo": ((1816.0, 1843.0, 2138.4, 1853.5), (0.0, -7.0), (0.0, 7.0)),
    "lados": {
        "esquerdo": {"faixa": (1816.0, 1679.84, 1830.0, 1876.29), "d_piso": (10.0, 0.0), "d_fora": (-8.0, 0.0),
                     "batentes": [(1821.99, 1678.05, 1826.76, 1679.84), (1821.99, 1876.29, 1826.76, 1878.08)],
                     "folhas": [(1824.37, 1679.84, 1826.76, 1746.72), (1821.99, 1746.72, 1824.37, 1876.29)]},
        "direito": {"faixa": (2126.0, 1679.2, 2138.4, 1876.29), "d_piso": (-10.0, 0.0), "d_fora": (-10.0, 0.0),
                    "batentes": [(2132.34, 1679.2, 2137.12, 1680.99), (2132.34, 1876.29, 2137.12, 1878.08)],
                    "folhas": [(2134.73, 1680.99, 2137.12, 1746.72), (2132.34, 1746.72, 2134.73, 1876.29)]}},
    "caixa_local": (1790, 1655, 2170, 1860),
    # `ajustes_casab.PORTOES_B` (a regra da Casa B: "portões de correr da área descoberta em alumínio")
    "aluminio": (196, 198, 200), "contorno": (104, 106, 110), "contorno_px": 0.45,
    "meio": (150, 152, 156), "meio_px": 0.3, "sombra": 0.30}


class Mapa:
    """A final levada à imagem: u' = s (u - 1/2) + t + 1/2 (px de borda; s = 1, t = 0: a própria final)."""

    def __init__(self, s=1.0, t=(0.0, 0.0)):
        self.s, self.t = s, t

    def x(self, u):
        return self.s * (u - 0.5) + self.t[0] + 0.5

    def y(self, v):
        return self.s * (v - 0.5) + self.t[1] + 0.5

    def ret(self, r):
        return (self.x(r[0]), self.y(r[1]), self.x(r[2]), self.y(r[3]))

    def reti(self, r):
        return tuple(int(round(v)) for v in self.ret(r))

    ref = None                                    # a final (só no 12K), para o afinamento local

    def local(self, img, caixa, raio=12):
        """O afim afinado na caixa (px da final): a final ampliada (s) casada com a imagem, com o subpixel; sem `ref`
        (a própria final), o mesmo."""
        if self.ref is None:
            return self
        x0, y0, x1, y1 = caixa
        tpl = cv2.resize(self.ref[y0:y1, x0:x1], None, fx=self.s, fy=self.s,
                         interpolation=cv2.INTER_CUBIC).astype(np.float32)
        ex, ey = self.x(x0), self.y(y0)
        X0, Y0 = int(np.floor(ex)) - raio, int(np.floor(ey)) - raio
        reg = img[Y0:Y0 + tpl.shape[0] + 2 * raio + 1, X0:X0 + tpl.shape[1] + 2 * raio + 1].astype(np.float32)
        r = cv2.matchTemplate(reg, tpl, cv2.TM_CCOEFF_NORMED)
        _, _, _, (bx, by) = cv2.minMaxLoc(r)

        def sub(c, a, b):
            d = a + b - 2 * c
            return 0.0 if d == 0 else 0.5 * (a - b) / d
        sx = sub(r[by, bx], r[by, bx - 1], r[by, bx + 1]) if 0 < bx < r.shape[1] - 1 else 0.0
        sy = sub(r[by, bx], r[by - 1, bx], r[by + 1, bx]) if 0 < by < r.shape[0] - 1 else 0.0
        dx, dy = X0 + bx + sx - ex, Y0 + by + sy - ey
        print(f"      afim local em {caixa}: {dx:+.2f}, {dy:+.2f} px")
        return Mapa(self.s, (self.t[0] + dx, self.t[1] + dy))


def copia(out, fonte, mp, r, d):
    """O retângulo r (px da final) recebe a fonte deslocada d (px da final), na escala da imagem."""
    x0, y0, x1, y1 = mp.reti(r)
    dx, dy = int(round(d[0] * mp.s)), int(round(d[1] * mp.s))
    out[y0:y1, x0:x1] = fonte[y0 + dy:y1 + dy, x0 + dx:x1 + dx]


def pintar(out, mp, pecas, folga=6):
    """Pinta [(ret px da final, 'ret'|'contorno', cor, largura px da final)] por cobertura exata, numa caixa só."""
    rs = [mp.ret(p[0]) for p in pecas]
    f = int(np.ceil(folga * mp.s))
    X0, Y0 = int(min(r[0] for r in rs)) - f, int(min(r[1] for r in rs)) - f
    X1, Y1 = int(max(r[2] for r in rs)) + f, int(max(r[3] for r in rs)) + f
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    for (r, tipo, cor, larg), rm in zip(pecas, rs):
        loc = (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)
        a = alfa_ret(loc, forma) if tipo == "ret" else alfa_contorno(loc, larg * mp.s, forma)
        reg = compor(reg, a, cor)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def sombra(out, mp, r, forca, dx=0.8, dy=1.0, sigma=0.9, fora=True):
    """A sombra curta do retângulo r (px da final) no que está em volta."""
    rm = mp.ret(r)
    f = int(np.ceil(6 * mp.s))
    X0, Y0, X1, Y1 = int(rm[0]) - f, int(rm[1]) - f, int(rm[2]) + f, int(rm[3]) + f
    forma = (Y1 - Y0, X1 - X0)
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    M = np.float32([[1, 0, dx * mp.s], [0, 1, dy * mp.s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), sigma * mp.s)
    if fora:
        sb *= (1 - a)
    reg = out[Y0:Y1, X0:X1].astype(np.float32) * (1 - forca * sb)[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def porta_cozinha(out, mp, q=PORTA_COZINHA):
    fonte = out.copy()
    for r, d in q["limpa"]:
        copia(out, fonte, mp, r, d)
    x0, y0, x1, y1 = mp.reti(q["parede_amostra"])
    cor = tuple(float(v) for v in np.median(fonte[y0:y1, x0:x1].reshape(-1, 3), axis=0))
    pecas = [(r, "ret", cor, 0) for r in q["parede"]]
    for r in [q["folha"]] + q["batentes"]:
        pecas += [(r, "ret", BRANCO, 0), (r, "contorno", PRETO, 0.5)]
    pintar(out, mp, pecas)
    print("    porta de correr da cozinha: a folha e os 2 batentes do PDF, no branco com o contorno preto fino")


def cubas_lavatorio(out, mp, q=CUBAS_LAV):
    y0, y1 = q["linhas"]
    for esq, dir_ in q["cubas"]:
        eixo = (esq + dir_ + 1) / 2                       # o meio do trecho (px de borda)
        u0, u1 = esq - (q["faixa"] - 1), esq + 1          # as colunas do lado esquerdo (o fio e o piso de fora)
        U0, U1 = int(round(mp.x(u0))), int(round(mp.x(u1)))
        V0, V1 = int(round(mp.y(y0))), int(round(mp.y(y1)))
        A = mp.x(eixo)
        D0 = int(round(2 * A - U1))
        out[V0:V1, D0:D0 + (U1 - U0)] = out[V0:V1, U0:U1][:, ::-1]
    print(f"    lavatório gourmet: o lado direito das {len(q['cubas'])} cubas com o fio do lado esquerdo, em espelho")


def armarios(out, mp, q=ARMARIOS, couro=True):
    import revisao_terreo_casac_1311 as RC
    c = RC.COZINHA
    for nome, r in q.items():
        rm = mp.ret(r)
        f = int(np.ceil(6 * mp.s))
        X0, Y0, X1, Y1 = int(rm[0]) - f, int(rm[1]) - f, int(rm[2]) + f, int(rm[3]) + f
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        forma = reg.shape[:2]
        loc = (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)
        a = alfa_ret(loc, forma)
        e = mp.s
        miolo = alfa_ret((loc[0] + e, loc[1] + e, loc[2] - e, loc[3] - e), forma)
        # o couro das cadeiras por cima fica
        im = reg
        if couro:
            pele = ((im[..., 2] - im[..., 0]) > 85) & (im[..., 2] > 110)
            pele = cv2.dilate(pele.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
            a = a * ~pele
            miolo = miolo * ~pele
        M = np.float32([[1, 0, -1.0 * mp.s], [0, 1, 1.3 * mp.s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), 1.1 * mp.s) * (1 - a)
        reg = reg * (1 - c["sombra"] * sb)[..., None]
        cor = np.float32(c["cor_armario"])
        reg = compor(reg, a - miolo, cor * c["face"])
        reg = compor(reg, miolo, cor)
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    armários na cor sólida das casas (sem o veio): {', '.join(q)}")


def portas_servico(out, mp, q=PORTAS_SERVICO):
    fonte = out.copy()
    for r, d in q["limpa"]:
        copia(out, fonte, mp, r, d)
    for nome, r in q["folhas"].items():
        sombra(out, mp, r, q["sombra"], dx=0.0, dy=0.9, sigma=0.6)
        borda = tuple(v * q["borda"] for v in q["madeira"])
        pintar(out, mp, [(r, "ret", q["madeira"], 0), (r, "contorno", borda, q["borda_px"])])
    print(f"    portas de giro do serviço: o traço velho sob as folhas e os pontinhos do piso saem; as folhas de novo "
          f"({', '.join(q['folhas'])})")


def _piso_tecido(fonte, mp, r_fonte, h, w):
    """Um trecho h x w de piso a partir do retângulo limpo `r_fonte` (px da final): a fonte e o espelho dela, em pé e
    deitada, até cobrir."""
    x0, y0, x1, y1 = mp.reti(r_fonte)
    P = fonte[y0:y1, x0:x1].astype(np.float32)
    lin = np.concatenate([P, P[::-1]], axis=0)
    while lin.shape[0] < h:
        lin = np.concatenate([lin, lin], axis=0)
    col = np.concatenate([lin, lin[:, ::-1]], axis=1)
    while col.shape[1] < w:
        col = np.concatenate([col, col], axis=1)
    return col[:h, :w]


def maquinas(out, mp, q=MAQUINAS):
    fonte = out.copy()
    X0, Y0, X1, Y1 = mp.reti(q["area"])
    reg = fonte[Y0:Y1, X0:X1].astype(np.float32)
    # as máquinas de hoje: o branco esmaltado e o aro cinza (neutros e claros), em componentes grandes
    lum = reg.mean(axis=2)
    sat = reg.max(axis=2) - reg.min(axis=2)
    m = (lum > 150) & (sat < 35)
    m = ndimage.binary_fill_holes(cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)))
    lab, n = ndimage.label(m)
    sprites = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        mm = lab[sl] == i + 1
        if mm.sum() < 300 * mp.s * mp.s:
            continue
        sprites.append((sl[0].start, reg[sl].copy(), mm.astype(np.float32)))
    sprites.sort(key=lambda t: t[0])
    if len(sprites) != len(q["novas"]):
        raise SystemExit(f"máquinas: achei {len(sprites)}, esperava {len(q['novas'])}")
    # o piso: um trecho limpo da área de serviço, no tom do piso logo à esquerda, com a emenda macia
    h, w = Y1 - Y0, X1 - X0
    T = _piso_tecido(fonte, mp, q["fonte"], h, w)
    # a luz linha a linha da faixa de piso logo à esquerda (suavizada), para não ficar emenda
    rx0, _, rx1, _ = mp.reti(q["ref"])
    ref = cv2.GaussianBlur(fonte[Y0:Y1, rx0:rx1].astype(np.float32).mean(axis=1, keepdims=True), (0, 0), 6 * mp.s)
    tm = cv2.GaussianBlur(T.mean(axis=1, keepdims=True), (0, 0), 6 * mp.s)
    T += (ref - tm)
    rampa = np.clip(np.arange(w, dtype=np.float32) / max(q["suave_px"] * mp.s, 1.0), 0, 1)[None, :, None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - rampa) + T * rampa), 0, 255).astype(np.uint8)
    # as máquinas no tamanho do PDF, acima da bancada
    for (_, S, mm), r in zip(sprites, q["novas"]):
        sombra(out, mp, r, q["sombra"])
        rm = mp.ret(r)
        bx0, by0 = int(np.floor(rm[0])), int(np.floor(rm[1]))
        bw, bh = int(round(rm[2] - rm[0])), int(round(rm[3] - rm[1]))
        Sz = cv2.resize(S, (bw, bh), interpolation=cv2.INTER_AREA)
        az = cv2.resize(cv2.GaussianBlur(mm, (0, 0), 0.6), (bw, bh), interpolation=cv2.INTER_AREA)[..., None]
        dst = out[by0:by0 + bh, bx0:bx0 + bw].astype(np.float32)
        out[by0:by0 + bh, bx0:bx0 + bw] = np.clip(np.round(dst * (1 - az) + Sz * az), 0, 255).astype(np.uint8)
    print("    máquinas de lavar: o piso de trás sem o retângulo escuro; as 2 no tamanho do PDF (0,60 m), acima da "
          "bancada dos tanques, visíveis")


_CUBA = {}


def _cuba_bib(q=CUBA_BHS):
    """A louça e a torneira da cuba de serviço da biblioteca (sem o granito da foto), giradas com a torneira para a
    esquerda: (rgb, alfa, a caixa da louça dentro da imagem)."""
    if "P" not in _CUBA:
        P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
        rgb, al = P[..., :3], P[..., 3] / 255
        lum = rgb.mean(axis=2)
        sat = rgb.max(axis=2) - rgb.min(axis=2)
        m = (lum > 140) & (sat < 40) & (al > 0.5)
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = ndimage.binary_fill_holes(m)
        lab, n = ndimage.label(m)
        tam = ndimage.sum(m, lab, range(1, n + 1))
        louca = lab == (int(np.argmax(tam)) + 1)
        ys, xs = np.nonzero(louca)
        lx0, ly0, lx1, ly1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        # a torneira: os componentes claros e neutros logo acima da louça, dentro da largura dela
        tor = np.zeros(m.shape, bool)
        alto = 0.45 * (ly1 - ly0)
        for i, sl in enumerate(ndimage.find_objects(lab)):
            if i + 1 == int(np.argmax(tam)) + 1:
                continue
            if sl[1].start >= lx0 and sl[1].stop <= lx1 and sl[0].stop >= ly0 - alto and sl[0].start < ly0:
                tor[sl] |= lab[sl] == i + 1
        mm = (louca | tor).astype(np.float32)
        ys, xs = np.nonzero(mm)
        X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        rgb, mm = rgb[Y0:Y1, X0:X1], mm[Y0:Y1, X0:X1]
        caixa = (lx0 - X0, ly0 - Y0, lx1 - X0, ly1 - Y0)
        # girada 90° no sentido anti-horário: a torneira (em cima) vai para a esquerda
        rgb, mm = np.rot90(rgb).copy(), np.rot90(mm).copy()
        h0 = Y1 - Y0
        caixa = (caixa[1], (X1 - X0) - caixa[2], caixa[3], (X1 - X0) - caixa[0])
        _CUBA["P"] = (rgb, mm, caixa, h0)
    return _CUBA["P"]


def cuba_bh_servico(out, mp, q=CUBA_BHS):
    fonte = out.copy()
    ax0, ay0, ax1, ay1 = q["apaga"]
    bx = q["bancada_x1"]
    meio = (ay0 + ay1) / 2
    # a cuba antiga sai: o granito da bancada (de cima e de baixo) e o piso de logo ao lado
    copia(out, fonte, mp, (ax0, ay0, bx, meio), (0.0, -q["dy_granito"]))
    copia(out, fonte, mp, (ax0, meio, bx, ay1), (0.0, q["dy_granito"]))
    copia(out, fonte, mp, (bx, ay0, ax1, ay1), (q["dx_piso"], 0.0))
    # a cuba da biblioteca: a louça no retângulo do PDF (o lado comprido), a torneira para a parede
    rgb, mm, (lx0, ly0, lx1, ly1), _ = _cuba_bib(q)
    cx0, cy0, cx1, cy1 = mp.ret(q["cuba"])
    k = (cy1 - cy0) / (ly1 - ly0)                       # a louça na altura do retângulo do PDF
    W, H = int(round(rgb.shape[1] * k)), int(round(rgb.shape[0] * k))
    # a louça encostada à direita do retângulo do PDF, no meio dele na altura
    X0 = int(round(cx1 - lx1 * k))
    Y0 = int(round((cy0 + cy1) / 2 - (ly0 + ly1) / 2 * k))
    S = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_AREA)
    a = cv2.resize(mm, (W, H), interpolation=cv2.INTER_AREA)
    # a sombra curta da louça
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, 0.8 * mp.s], [0, 1, 1.0 * mp.s]]), (W, H)), (0, 0),
                          0.9 * mp.s) * (1 - a)
    dst = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    dst = dst * (1 - q["sombra"] * sb)[..., None]
    dst = dst * (1 - a[..., None]) + S * a[..., None]
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(dst), 0, 255).astype(np.uint8)
    print("    BH serviço: a cuba de serviço da biblioteca (a louça e a torneira), a torneira para a parede")


def _alfa_poli(pts, forma, encolhe=0.0, ss=8):
    """A cobertura do polígono (px da imagem) e a do miolo (o polígono encolhido `encolhe` px)."""
    hi = np.zeros((forma[0] * ss, forma[1] * ss), np.uint8)
    cv2.fillPoly(hi, [np.int32(np.round(np.float64(pts) * ss))], 255)
    a = cv2.resize(hi.astype(np.float32) / 255, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
    k = int(round(encolhe * ss))
    if k > 0:
        hi = cv2.erode(hi, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
    m = cv2.resize(hi.astype(np.float32) / 255, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)
    return a, m


def louceiro_despensa(out, mp, q=LOUCEIRO_DESPENSA):
    import revisao_terreo_casac_1311 as RC
    c = RC.COZINHA
    for nome in ("louceiro", "despensa"):
        pts = [(mp.x(x), mp.y(y)) for x, y in q[nome]]
        f = int(np.ceil(6 * mp.s))
        X0, Y0 = int(min(p[0] for p in pts)) - f, int(min(p[1] for p in pts)) - f
        X1, Y1 = int(max(p[0] for p in pts)) + f, int(max(p[1] for p in pts)) + f
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        forma = reg.shape[:2]
        a, miolo = _alfa_poli([(x - X0, y - Y0) for x, y in pts], forma, encolhe=mp.s)
        # o que foge do rosado por cima (as folhas, os textos) fica
        rosa = np.median(reg[miolo > 0.99], axis=0)
        outro = np.linalg.norm(reg - rosa, axis=2) > q["outro"]
        outro = cv2.dilate(outro.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        a, miolo = a * ~outro, miolo * ~outro
        M = np.float32([[1, 0, -1.0 * mp.s], [0, 1, 1.3 * mp.s]])
        sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), 1.1 * mp.s) * (1 - a)
        reg = reg * (1 - c["sombra"] * sb)[..., None]
        cor = np.float32(c["cor_armario"])
        reg = compor(reg, a - miolo, cor * c["face"])
        reg = compor(reg, miolo, cor)
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    louceiro e despensa: os armários em L do rosado na cor sólida dos armários")


def porta_adega(out, mp, q=PORTA_ADEGA):
    portas_servico(out, mp, q)


def gourmet_altura(out, mp, q=GOURMET_ALTURA):
    x0, yf, x1 = q["frente"]
    L = q["sombra_px"]
    X0, X1 = int(np.floor(mp.x(x0))), int(np.ceil(mp.x(x1)))
    Y0, Y1 = int(np.floor(mp.y(yf - L))) - 1, int(np.ceil(mp.y(yf + q["brilho_px"]))) + 2
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    cx = alfa_ret((mp.x(x0) - X0, 0, mp.x(x1) - X0, forma[0]), forma)
    # a sombra no piso à frente: mais forte junto à quina
    v = np.arange(forma[0], dtype=np.float32) + 0.5 + Y0
    d = np.clip((mp.y(yf) - v) / (L * mp.s), 0, 1)
    w = np.where(v < mp.y(yf), (1 - d) ** 2, 0.0)[:, None] * cx
    reg = reg * (1 - q["sombra"] * w)[..., None]
    # o brilho na beira do tampo e o fio escuro da quina
    br = alfa_ret((mp.x(x0) - X0, mp.y(yf) - Y0, mp.x(x1) - X0, mp.y(yf + q["brilho_px"]) - Y0), forma)
    reg = reg * (1 + (q["brilho"] - 1) * br)[..., None]
    e = q["fio_px"] / 2
    fi = alfa_ret((mp.x(x0) - X0, mp.y(yf - e) - Y0, mp.x(x1) - X0, mp.y(yf + e) - Y0), forma)
    reg = reg * (1 - (1 - q["fio"]) * fi)[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    gourmet: a bancada de trás mais alta que o piso (o fio da quina, o brilho do tampo, a sombra no piso)")


def lavabo_bancada(out, mp, q=LAVABO_BANCADA):
    """A peça no tom da cuba: a luz suave dela (a mediana e o desfoque só por dentro, sem os pontinhos e riscos) levada ao
    tom mediano da pedra da cuba (`ref`, a faixa ao lado da cuba, sem a torneira), com o grão fino dessa faixa; o
    contorno da peça fica."""
    b = q["borda_px"]
    x0, y0, x1, y1 = q["peca"]
    rm = mp.ret((x0 + b, y0 + b, x1 - b, y1 - b))
    X0, Y0, X1, Y1 = int(np.floor(rm[0])) - 2, int(np.floor(rm[1])) - 2, int(np.ceil(rm[2])) + 2, int(np.ceil(rm[3])) + 2
    sub = out[Y0:Y1, X0:X1].copy()
    reg = sub.astype(np.float32)
    forma = reg.shape[:2]
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    dentro = (a > 0.5).astype(np.float32)
    k = max(5, int(round(5 * mp.s)) | 1)
    med = cv2.medianBlur(sub, k).astype(np.float32)
    sg = 3.0 * mp.s
    luz = cv2.GaussianBlur(med * dentro[..., None], (0, 0), sg) / np.maximum(cv2.GaussianBlur(dentro, (0, 0), sg), 1e-3)[..., None]
    rx0, ry0, rx1, ry1 = mp.reti(q["ref"])
    F = out[ry0:ry1, rx0:rx1].astype(np.float32)
    ref = np.median(F.reshape(-1, 3), axis=0)
    luz *= ref / np.maximum(np.median(luz[dentro > 0], axis=0), 1)
    grao = F - cv2.GaussianBlur(F, (0, 0), 1.5 * mp.s)
    while grao.shape[0] < forma[0]:
        grao = np.concatenate([grao, grao[::-1]], axis=0)
    while grao.shape[1] < forma[1]:
        grao = np.concatenate([grao, grao[:, ::-1]], axis=1)
    T = luz + 0.8 * grao[:forma[0], :forma[1]]
    reg = reg * (1 - a[..., None]) + T * a[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    lavabo: a bancada abaixo da cuba no tom da cuba, sem os pontinhos e riscos")


def _cuba_redonda(q=PIA_SALA_INTIMA):
    """A louça e a torneira da cuba redonda da biblioteca (sem a pedra da foto), giradas com a torneira para a esquerda:
    (rgb, alfa, a caixa da louça)."""
    if "R" not in _CUBA:
        P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
        rgb, al = P[..., :3], P[..., 3] / 255
        lum = rgb.mean(axis=2)
        sat = rgb.max(axis=2) - rgb.min(axis=2)
        m = (lum > q["lum_min"]) & (sat < q["sat_max"]) & (al > 0.5)
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = ndimage.binary_fill_holes(m)
        lab, n = ndimage.label(m)
        tam = ndimage.sum(m, lab, range(1, n + 1))
        i_l = int(np.argmax(tam)) + 1
        louca = lab == i_l
        ys, xs = np.nonzero(louca)
        lx0, ly0, lx1, ly1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        mm = louca.copy()
        alto = 0.45 * (ly1 - ly0)
        for i, sl in enumerate(ndimage.find_objects(lab)):
            if i + 1 == i_l:
                continue
            if sl[1].start >= lx0 and sl[1].stop <= lx1 and sl[0].stop >= ly0 - alto and sl[0].start < ly0 + 0.2 * (ly1 - ly0):
                mm[sl] |= lab[sl] == i + 1
        mm = mm.astype(np.float32)
        ys, xs = np.nonzero(mm)
        X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        rgb, mm = rgb[Y0:Y1, X0:X1], mm[Y0:Y1, X0:X1]
        caixa = (lx0 - X0, ly0 - Y0, lx1 - X0, ly1 - Y0)
        rgb, mm = np.rot90(rgb).copy(), np.rot90(mm).copy()
        W0 = X1 - X0
        caixa = (caixa[1], W0 - caixa[2], caixa[3], W0 - caixa[0])
        _CUBA["R"] = (rgb, mm, caixa)
    return _CUBA["R"]


def pia_sala_intima(out, mp, q=PIA_SALA_INTIMA):
    fonte = out.copy()
    # a bancada limpa: a pedra do alto dela (sem a linha técnica), em espelho, de ponta a ponta
    X0, Y0, X1, Y1 = mp.reti(q["interior"])
    fx0, fy0, fx1, fy1 = mp.reti(q["fonte"])
    F = fonte[fy0:fy1, fx0:fx1].astype(np.float32)
    lin = F
    while lin.shape[0] < Y1 - Y0:
        lin = np.concatenate([lin, lin[::-1]], axis=0)
    T = cv2.resize(lin[:Y1 - Y0], (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA) if lin.shape[1] != X1 - X0 \
        else lin[:Y1 - Y0]
    out[Y0:Y1, X0:X1] = np.clip(np.round(T), 0, 255).astype(np.uint8)
    # a cuba redonda da biblioteca no círculo do PDF, a torneira para a parede (à esquerda)
    rgb, mm, (lx0, ly0, lx1, ly1) = _cuba_redonda(q)
    cx0, cy0, cx1, cy1 = mp.ret(q["cuba"])
    k = ((cx1 - cx0) + (cy1 - cy0)) / ((lx1 - lx0) + (ly1 - ly0))
    W, H = int(round(rgb.shape[1] * k)), int(round(rgb.shape[0] * k))
    BX = int(round((cx0 + cx1) / 2 - (lx0 + lx1) / 2 * k))
    BY = int(round((cy0 + cy1) / 2 - (ly0 + ly1) / 2 * k))
    S = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_AREA)
    a = cv2.resize(mm, (W, H), interpolation=cv2.INTER_AREA)
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, 0.8 * mp.s], [0, 1, 1.0 * mp.s]]), (W, H)), (0, 0),
                          0.9 * mp.s) * (1 - a)
    dst = out[BY:BY + H, BX:BX + W].astype(np.float32)
    dst = dst * (1 - q["sombra"] * sb)[..., None]
    dst = dst * (1 - a[..., None]) + S * a[..., None]
    out[BY:BY + H, BX:BX + W] = np.clip(np.round(dst), 0, 255).astype(np.uint8)
    print("    sala íntima: a bancada do bar sem a linha técnica e a cuba redonda da biblioteca (louça e torneira)")


def banco_deck(out, mp, q=BANCO_DECK):
    fonte = out.copy()
    copia(out, fonte, mp, q["traco"], (0.0, q["dy"]))
    print("    deck: o traço claro sob o banco vira grama")


def armario_quarto_servico(out, mp, q=ARMARIO_QS):
    armarios(out, mp, {"quarto de serviço": q["ret"]}, couro=False)


def _grama(px):
    p = px.astype(np.int16)
    return (p.mean(-1) < 125) & (p[..., 1] - p[..., 0] > 25)


def _dentro(px):
    """O que é do lote (grama, pedra, piso): não o fundo nem o muro escuro."""
    p = px.astype(np.int16)
    return (p.mean(-1) < 200) & (np.abs(p[..., 1] - p[..., 0]) + np.abs(p[..., 1] - p[..., 2]) > 14)


def _cinza(out, y, xs):
    p = out[y, xs].astype(np.int16)
    return ((np.abs(p[:, 1] - p[:, 0]) < 12) & (np.abs(p[:, 1] - p[:, 2]) < 12)).mean()


def margem_lote(out, mp, q=LOTE):
    g = out.astype(np.int16).mean(axis=2)
    xs = slice(int(mp.x(q["meio_x"][0])), int(mp.x(q["meio_x"][1])))
    # o muro de cima: do miolo para cima até o fundo e para baixo até a grama
    ya, yb = int(mp.y(q["muro_cima"][0])), int(mp.y(q["muro_cima"][1]))
    meio_c = ya + int(np.argmin(g[ya:yb, xs].mean(1)))
    yt = meio_c
    while g[yt - 1, xs].mean() < 252:
        yt -= 1
    gy0 = meio_c
    while _cinza(out, gy0, xs) > 0.5:
        gy0 += 1
    # o de baixo: do miolo para baixo até o fundo (com a sombra mole dele) e para cima até a grama
    ya, yb = int(mp.y(q["muro_baixo"][0])), int(mp.y(q["muro_baixo"][1]))
    meio_b = ya + int(np.argmin(g[ya:yb, xs].mean(1)))
    yf = meio_b
    while g[yf + 1, xs].mean() < 250:
        yf += 1
    gy1 = meio_b
    while _cinza(out, gy1 - 1, xs) > 0.5:
        gy1 -= 1
    # as pontas: as do muro de cima; a do de baixo, a dele mesmo (as 2 linhas que passam dela saem)
    linha = g[int(mp.y(q["linha_muro_cima"]))]
    xl = int(np.argmax(linha < 200))
    xr = len(linha) - 1 - int(np.argmax(linha[::-1] < 230))
    lb = g[int(mp.y(q["linha_muro_baixo"])), :xr + 1]
    xb = len(lb) - 1 - int(np.argmax(lb[::-1] < 200))
    fora = np.ones(g.shape, bool)
    fora[yt:yf + 1, xl:xr + 1] = False
    fora[gy1:yf + 1, xb + 1:] = True
    fundo = np.median(out[fora].reshape(-1, 3), axis=0).round().astype(np.uint8)
    out[fora] = fundo
    # as bordas do gramado (entre os muros): a 1ª e a última coluna no tom da grama de dentro
    def tom(cols):
        return out[ae, cols].astype(np.int16).mean(0)
    ae = slice(int(mp.y(q["amostra_esq"][0])), int(mp.y(q["amostra_esq"][1])))
    k = int(np.ceil(q["borda_esq_px"] * mp.s)) + 2
    ref = tom(slice(xl + 3 * k, xl + 6 * k)).mean(0)
    cols = tom(slice(xl, xl + k))
    lc = xl + int(np.argmax(np.abs(cols - ref).max(1) < 8))
    for i, x in enumerate(range(lc - 1, xl - 1, -1)):          # em espelho (sem emenda) a partir de lc
        ok = _dentro(out[gy0:gy1, lc + i])
        out[gy0:gy1, x][ok] = out[gy0:gy1, lc + i][ok]
    ae = slice(int(mp.y(q["amostra_grama"][0])), int(mp.y(q["amostra_grama"][1])))
    k = int(np.ceil(q["borda_dir_px"] * mp.s))
    w0 = xr - 6 * k - 10
    cols = tom(slice(w0, xr + 1))
    ultima = len(cols) - 1 - int(np.argmax(cols[::-1].mean(1) < 125))
    ref = cols[ultima - 5 * k:ultima - 2 * k].mean(0)
    xg = ultima
    while xg - 1 > ultima - k and np.abs(cols[xg - 1] - ref).max() > 6:
        xg -= 1
    xg_, ult_ = w0 + xg, w0 + ultima
    for i, x in enumerate(range(xg_, ult_ + 1)):              # em espelho a partir de xg_
        ok = _dentro(out[gy0:gy1, xg_ - 1 - i])
        out[gy0:gy1, x][ok] = out[gy0:gy1, xg_ - 1 - i][ok]
    out[gy0:gy1, ult_ + 1:xr + 1] = fundo
    print(f"    margem: fora do lote (x {xl} a {xr}, y {yt} a {yf}; o muro de baixo até x {xb}) no fundo "
          f"{tuple(int(v) for v in fundo)}; as bordas do gramado (y {gy0} a {gy1 - 1}): à esquerda x {xl} a {lc - 1}, "
          f"à direita x {xg_} a {ult_}, em grama")


def grama_muro(out, mp, q=GRAMA_MURO):
    x0, x1 = int(np.floor(mp.x(q["x"][0]))), int(np.ceil(mp.x(q["x"][1])))
    ya, yb = int(mp.y(q["busca"][0])), int(np.ceil(mp.y(q["busca"][1])))
    reg = out[ya:yb, x0:x1].astype(np.int16)
    cinza = (np.abs(reg[..., 1] - reg[..., 0]) < 10) & (np.abs(reg[..., 1] - reg[..., 2]) < 10) & (reg.mean(-1) < 110)
    topo = np.argmax(cinza, axis=0)
    ok = cinza.any(axis=0)
    # o muro é reto: o topo por blocos de colunas (a mediana), interpolado
    bl = max(64, int(64 * mp.s))
    cx, ty = [], []
    for i in range(0, x1 - x0, bl):
        m = ok[i:i + bl]
        if m.sum() > bl // 4:
            cx.append(i + bl / 2)
            ty.append(np.median(topo[i:i + bl][m]))
    mt = ya + np.round(np.interp(np.arange(x1 - x0), cx, ty)).astype(int)
    h = int(np.ceil(q["faixa_px"] * mp.s))
    n = 0
    for j, x in enumerate(range(x0, x1)):
        y1 = mt[j]
        if not _grama(out[y1 - h - 1, x]):
            continue
        # em espelho (sem emenda) a grama de logo acima
        out[y1 - h:y1, x] = out[y1 - h - 1:y1 - 2 * h - 1:-1, x]
        n += 1
    print(f"    muro de baixo: a faixa verde clara de {h} px acima dele (o topo em y {int(np.median(mt))}, {n} colunas) "
          f"vira a grama de logo acima, em espelho")


def _refaz(out, mp, faixa, piso, d_piso, d_fora):
    """A faixa (px da final) refeita: o que é do piso (cobertura exata) vem da imagem deslocada d_piso, o resto (a grama)
    de d_fora (px da final)."""
    fonte = out.copy()
    r = mp.ret(faixa)
    X0, Y0 = int(np.floor(r[0])) - 1, int(np.floor(r[1])) - 1
    X1, Y1 = int(np.ceil(r[2])) + 1, int(np.ceil(r[3])) + 1
    forma = (Y1 - Y0, X1 - X0)

    def desl(d):
        dx, dy = int(round(d[0] * mp.s)), int(round(d[1] * mp.s))
        return fonte[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)

    def loc(q):
        return (q[0] - X0, q[1] - Y0, q[2] - X0, q[3] - Y0)
    ap = alfa_ret(loc(mp.ret(piso)), forma)[..., None]
    novo = desl(d_piso) * ap + desl(d_fora) * (1 - ap)
    a = alfa_ret(loc(r), forma)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32) * (1 - a) + novo * a
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def portoes_descoberta(out, mp, q=PORTOES_AD):
    m = mp.local(out, q["caixa_local"])
    faixa, d_piso, d_fora = q["borda_baixo"]
    _refaz(out, m, faixa, q["piso"], d_piso, d_fora)
    for nome, lado in q["lados"].items():
        _refaz(out, m, lado["faixa"], q["piso"], lado["d_piso"], lado["d_fora"])
        pecas = lado["batentes"] + lado["folhas"]
        for r in pecas:
            sombra(out, m, r, q["sombra"], dx=-0.6, dy=0.8, sigma=0.6)
        desenho = [(r, "ret", q["aluminio"], 0) for r in pecas]
        for r in lado["folhas"]:
            xm = (r[0] + r[2]) / 2
            desenho.append(((xm - q["meio_px"] / 2, r[1], xm + q["meio_px"] / 2, r[3]), "ret", q["meio"], 0))
        desenho += [(r, "contorno", q["contorno"], q["contorno_px"]) for r in pecas]
        pintar(out, m, desenho)
    print("    área descoberta: a faixa cinza em volta do piso sai (o piso até a face de fora dos portões e a borda de "
          "baixo do PDF); os 2 portões de correr (2 folhas e 2 batentes cada) em alumínio, com o contorno, a linha do "
          "meio e a sombra curta")


PASSOS = (porta_cozinha, cubas_lavatorio, armarios, portas_servico, maquinas, cuba_bh_servico,
          louceiro_despensa, porta_adega, gourmet_altura, lavabo_bancada, pia_sala_intima, banco_deck,
          armario_quarto_servico, margem_lote, grama_muro, portoes_descoberta)
NOVOS_1711D = (margem_lote, grama_muro, portoes_descoberta)
NOVOS_1711C = (pia_sala_intima, banco_deck, armario_quarto_servico)
NOVOS_1711 = (louceiro_despensa, porta_adega, gourmet_altura, lavabo_bancada)


def aplicar(img, mp, passos=PASSOS):
    out = img.copy()
    for f in passos:
        f(out, mp)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    final = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(final, Mapa()))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        doze = cv2.imread(str(f))
        M = DF.afim_12k(final, doze)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = final
        out = aplicar(doze, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

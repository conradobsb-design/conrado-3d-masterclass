#!/usr/bin/env python3
"""Pente fino pelas regras das plantas da Casa D (POE 642), como os das Casas B e C (`conferencia_casab.py`,
`conferencia_casac.py`).

Pedido do usuário (22/10/26): "Casa D" (a ordem da seção 17 das regras: Casa E, Casa A, Casa B, Casa D, Casa D;
a última).
Cada prancha de entrega atual (`POE642_CasaD/entrega/POE642_CasaD_PH_<Pavimento>_entrega.png`) foi conferida
trecho a trecho contra o PDF do cliente (`_pdfs_cliente/642 - <PAVIMENTO> - CASA D.pdf`) e o `POE642_REGRAS.md`,
com as escalas medidas primeiro (seção 2, "ATENÇÃO ÀS ESCALAS"). O PDF vai ao quadro da prancha pela mesma cadeia
das bases (`opcoes_1pav_casae.quadro_pdf`, com a config da Casa D): 59,7 px/m, as paredes do PDF caem sobre as da
prancha. Os itens ficam em `PENTE_FINO` (pontos em px da prancha de 3840) e o script desenha o mapa numerado de
cada pavimento, com a legenda embaixo: `POE642_CasaD/renders/POE642_CasaD_PH_<Pavimento>_pente_fino_mapa.jpg`; com
`--escalas`, a folha das escalas (`POE642_CasaD/renders/POE642_CasaD_PH_escalas_conferencia.jpg`).

Uso (da pasta POE642_CasaA/scripts/):
  python3 conferencia_casac.py            # os dois mapas
  python3 conferencia_casac.py Terreo
  python3 conferencia_casac.py --escalas  # a folha das escalas
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from conferencia_casaa import VERMELHO, fonte, quebrar

AQUI = Path(__file__).resolve().parent
CASA_D = AQUI.parent.parent / "POE642_CasaD"
PX_M = 59.7   # px/m da prancha (o PDF a 1:50 no quadro da prancha, pelo alinhamento das paredes)
# folha das escalas: (título, pavimento, canto do trecho de 1,5 x 1,5 m na prancha, sem móveis, material da biblioteca)
ESCALA_PISOS = [
    ("Travertino · living", "Terreo", (2250, 980), "travertino"),
    ("Vinílico · circulação das suítes", "Terreo", (1225, 1345), "vinilico"),
    ("Granito marrom · acesso da garagem", "Terreo", (2700, 240), "granito_marrom"),
    ("Granito marrom · cozinha", "Terreo", (1990, 520), "granito_marrom"),
    ("Bege Bahia · varanda gourmet", "Terreo", (1180, 1100), "bege_bahia"),
    ("Bege Bahia · pisante", "Terreo", (2650, 960), "bege_bahia"),
    ("Grama", "Terreo", (2900, 1600), "grama"),
    ("Granito marrom · depósito (Subsolo)", "Subsolo", (1150, 1050), "granito_marrom"),
    ("Vinílico · academia", "Subsolo", (1100, 1430), "vinilico"),
    ("Bege Bahia · pátio do Subsolo", "Subsolo", (600, 1400), "bege_bahia"),
]
# vegetação: (título, recorte na prancha do Térreo)
ESCALA_VEGETACAO = [
    ("Canto de cima, à esquerda", (345, 130, 790, 560)),
    ("Canto de baixo, à esquerda", (345, 1500, 800, 1940)),
    ("Junto à suíte 3 / escritório, à direita", (2500, 1300, 2780, 1790)),
    ("Jardim da sala íntima", (1440, 1660, 1820, 1840)),
]
# recorte de cada mapa (px da prancha de 3840), em volta da planta
RECORTE = {"Subsolo": (440, 950, 1600, 1800), "Terreo": (330, 100, 3470, 1980)}

# (número, texto, pontos em px da prancha de 3840); número None: nota sem marca no mapa (os conformes).
# Usuário (21/10/26), depois do primeiro mapa: "ATENÇÃO ÀS ESCALAS". As escalas vêm primeiro: cada textura
# medida na prancha (régua de 1 m = 59,7 px) ao lado da da biblioteca na mesma escala (`texturas.textura`), a
# vegetação medida folha a folha e os móveis, louças e carros sobrepostos ao contorno do PDF.
# Na Casa D as escalas e a regra de 22/10 "tudo desenhado na resolução da prancha" valem desde o começo: a proposta
# é refazer as duas finais em 3840 px como as das Casas B e C (`final3840_casab.py`, `final3840_casac.py`), guardando
# as decisões de 15/10 (os 44 itens do retoque do Térreo e os 23 do Subsolo).
PENTE_FINO = {
    "Subsolo": [
        (1, "Só o Subsolo, com o resto do terreno hachurado (R2): o lote do Térreo final em diagonais finas a 45°, "
            "cinza-claro, como nas Casas A, B, C e E; hoje o resto do lote está em branco. Proposta: em cor cheia o "
            "Subsolo e o pátio (o contorno da EST_LAJE no PDF). A confirmar: a área verde entre o pátio e a parede "
            "tracejada (pedido de 15/10) fica verde, com as plantas da biblioteca no tamanho real, ou entra na hachura",
         [(560, 1650), (1500, 1060)]),
        (2, "Escala do Bege Bahia (R1, seção 18): placa de 0,60 m com as nuvens de 10 a 20 cm e o tom quente da "
            "referência (~230, 211, 186). Hoje: liso e rosado (~227, 209, 202), com riscos brancos do motor. No pátio, na "
            "circulação, na escada, na sauna, na ducha e no vestiário", [(620, 1400), (900, 1210)]),
        (3, "Escala do vinílico (R4): réguas de ~20 cm, deitadas como no PDF. Hoje: réguas largas e lisas, com veio de "
            "madeira (~166, 128, 104). Na academia", [(1200, 1400)]),
        (4, "Granito marrom (seção 3): o mesmo do Térreo, na escala e no tom decididos (item 2 do Térreo). Hoje: liso e "
            "rosado (~90, 62, 61), num tom diferente do Térreo (~75, 56, 49). DCE 1, WC DCE e depósito",
         [(1200, 1080), (950, 1060)]),
        (5, "Escada (R14 e seção 5): os 16 degraus do PDF em Bege Bahia, cheios do 1 ao 7 (a marca de corte do PDF) e "
            "esmaecidos depois, com os bocéis tracejados; a linha cinza suave em cada bocel e a sombra de ~10 cm; o "
            "triângulo no degrau 1, junto ao pátio, apontando para a direita (o \"S\" do PDF: sobe). Hoje: só o "
            "sombreamento de descida de 15/10, sem linhas nem triângulo (substituído pelas regras de 19/10)",
         [(870, 1290), (1100, 1290)]),
        (6, "Portas sem arcos (R3): os 10 arcos do PDF (WC DCE, DCE 1, as duas folhas do depósito, a do fim da escada, "
            "sauna, ducha, vestiário, WC e box do vestiário), hoje em cinza no granito e no Bege Bahia. Ficam as folhas, "
            "finas e brancas, e os batentes; o piso segue limpo onde estava o arco", [(1110, 1190), (1000, 1615), (1240, 1630)]),
        (7, "Rótulos (seção 12, novos na Casa D): os 6 ambientes do PDF com nome e área (DCE 1, WC DCE, depósito/casa "
            "de máquinas, academia, vestiário e sauna), mais o elevador, em Inter no corpo do PDF × 1,3; brancos no "
            "granito (R6), pretos nos pisos claros, sem sombra e dentro do ambiente, fora dos objetos (R7)",
         [(1215, 1150), (1046, 1454), (833, 1639)]),
        (8, "Soleiras (R13): conferir porta a porta com o PDF, na resolução da prancha; onde o vão fica em branco, "
            "soleira em Bege Bahia, com as faces da parede em cinza fino; onde o piso atravessa, sem soleira. A do "
            "elevador em inox escovado (seção 4; hoje já é)", [(970, 1150), (1385, 1320)]),
        (9, "Paredes pretas no contorno do PDF (seção 2, 21/10): bordas retas e cantos nítidos, sem falhas dentro nem "
            "sobras para fora", [(1550, 1500)]),
        (10, "Tudo na resolução da prancha (seção 2, 22/10): a final do Subsolo refeita em 3840 px, como as das Casas B "
             "e C: pisos da biblioteca, aparelhos, louças e banco da sauna nítidos no contorno do PDF, sem os borrões do "
             "render ampliado, guardando as decisões de 15/10 (os 23 itens do retoque)", [(1350, 1450)]),
        (None, "Conferido na escala e conforme: o quadro (59,7 px/m; o elevador cai sobre o do Térreo); esteiras, "
               "bicicletas e supinos no tamanho do PDF; banco da sauna em Bege Bahia, em dois níveis (decisão de 15/10); "
               "chuveiros de braço no WC DCE, na ducha e no vestiário; bacias com a tampa e a cuba branca do vestiário; "
               "vidros finos da academia e da sauna; soleira do elevador em inox; sem pilares (o PDF da Casa D não tem "
               "a EST_PILAR); curvas de nível ocultas", []),
    ],
    "Terreo": [
        (1, "Escala da vegetação (seção 10, R1): a do motor está grande demais, com leques de palmeira de ~2 m, e "
            "avança ~2,5 m pelo gramado junto à suíte 3 / escritório. Entram as plantas da biblioteca no tamanho real, "
            "com a sombra, só dentro do lote e fora dos pisos, nos dois cantos da esquerda, junto à piscina e junto à "
            "suíte 3", [(520, 260), (470, 1820), (2640, 1460)]),
        (2, "Granito marrom (seção 3): hoje escuro (~75, 56, 49), quase liso e com pontos brancos; no Subsolo, outro "
            "tom (~90, 62, 61). A confirmar: o desenho e o tom da referência das outras casas (~118, 89, 69, nuvens "
            "suaves e lascas de agregado) ou o Marrom Tabaco escolhido em 15/10 (~90, 66, 50) com o mesmo desenho. "
            "Cozinha, gourmet, banho gourmet, louceiro, despensa, serviço, área descoberta, garagem e acesso de veículos",
         [(1990, 560), (2950, 260)]),
        (3, "Escala do travertino (R1, seção 3): o da biblioteca, placa de 1,20 m, veios horizontais de 5 a 20 cm, sem "
            "riscos nem emendas (Casa B, 22/10). Hoje: estrias verticais contínuas de vários metros. Living/jantar, hall, "
            "adega e lavabo", [(2250, 1000), (2520, 1100)]),
        (4, "Escala do vinílico (R4): réguas de ~20 cm, claras, em tons alternados, deitadas como desenha o PDF. Hoje: "
            "réguas largas e lisas, com veio de madeira (~169, 135, 109). Suítes, sala íntima, circulações, closet e DCE",
         [(1250, 1360), (1700, 1400), (2400, 1450)]),
        (5, "Escala do Bege Bahia (R1, seção 18): placa de 0,60 m com as nuvens de 10 a 20 cm e o tom quente da "
            "referência (~230, 211, 186). Hoje: liso e rosado (~226, 209, 198), com riscos brancos do motor. Deck da "
            "piscina, varanda gourmet, pisantes, blocos da esquerda, escada e banhos", [(800, 720), (1350, 1000), (2700, 1060)]),
        (6, "Grama da referência (R4): a do motor é clara e de grão miúdo (~93, 108, 47); a da referência é ~71, 84, 42, "
            "com manchas suaves de 0,5 a 1 m", [(2950, 1600)]),
        (7, "Carros (R12): os 3 do PDF em prata, alinhados e do mesmo tamanho, 4,70 × 1,85 m (281 × 110 px). Hoje: "
            "grafite, branco e azul-marinho (as cores diferentes de 15/10, substituídas pela R12), de ~4,3 a 5,1 m",
         [(2730, 620), (2890, 620), (3060, 620)]),
        (8, "Tudo na resolução da prancha (seção 2, 22/10): a final do Térreo refeita em 3840 px, como as das Casas B e C "
            "(`final3840_casad.py`): pisos da biblioteca, móveis, louças, bancadas e plantas nítidos no contorno do PDF, "
            "sem os borrões do render ampliado, guardando as decisões de 15/10 (os 44 itens do retoque: a piscina com a "
            "borda alta e o dreno, o acesso de veículos em granito, a cabine do elevador, os cooktops de 5 bocas, os "
            "tanques duplos, o banco capitonê, a mesa redonda com o tapete orgânico)", [(2100, 1500), (1800, 900)]),
        (9, "Rótulos (seção 12, novos na Casa D): os 33 ambientes do PDF com nome e área, mais o elevador, em Inter no "
            "corpo do PDF × 1,3; brancos no granito (R6) e nos jardins, pretos nos pisos claros, sem sombra e dentro do "
            "ambiente. Nenhum sobre objeto (R7): no PDF, GARAGEM cai sobre o carro do meio; vai para o piso livre mais "
            "perto", [(2891, 604), (2096, 1017), (863, 1383)]),
        (10, "Portas sem arcos (R3): os 22 arcos do PDF, inclusive os cinza do granito (15/10, item 12), a pivotante do "
             "hall e a porta dupla da área descoberta. Ficam as folhas, finas e brancas, e os batentes",
         [(2380, 1030), (2240, 640), (1110, 1370)]),
        (11, "Escada de 16 degraus junto à suíte master (R14 e seção 5): é a que sobe do Subsolo (\"1\" a \"16\" da "
             "esquerda para a direita), e no Térreo é a chegada. Degraus em Bege Bahia, a linha cinza suave em cada "
             "bocel e a sombra de ~10 cm; o triângulo no topo, no degrau 16 (à direita), apontando para a esquerda "
             "(descida). Hoje: listras sem sombra nem triângulo", [(990, 1270), (1260, 1270)]),
        (12, "Blocos em cascata à esquerda da piscina (seção 5, como na Casa B): cada bloco do PDF em Bege Bahia, com o "
             "contorno fino de bocel e a sombra curta (para baixo e à esquerda) no de baixo e na grama. A confirmar: o "
             "triângulo da R14 no início, apontando para onde descem (para a esquerda)", [(640, 900), (720, 1040)]),
        (13, "Guarda-corpos de vidro (seção 9), da ARQ_ELEMENTOS FIXOS, hoje nenhum aparece: em volta do vão da escada "
             "(a borda de cima, 6,2 m, e a ponta da esquerda) e na borda do terraço da piscina junto aos blocos (o L da "
             "esquerda). Vidro claro com as duas faces em linha fina, a sombra curta e as quinas fechadas",
         [(1000, 1252), (760, 1120)]),
        (14, "Brises de ripas (R9, seção 9), da ARQ_ELEMENTOS FIXOS: dos dois lados da porta pivotante do hall, na "
             "lateral direita da garagem, na lateral da suíte 3 / escritório e nas duas faixas da fachada de baixo, com o "
             "tracejado da projeção da cobertura ao lado. Hoje: paredes pretas no hall, uma linha cinza na garagem e nada "
             "na fachada. A confirmar a cor: madeira (como no Térreo da Casa E) ou grafite (como na Casa B)",
         [(2440, 930), (2440, 1170), (3170, 620), (2525, 1400), (1085, 1755)]),
        (15, "Projeções (R8) em tracejado bem visível: os dois X do banho master (o box e o vaso; hoje não aparecem), o "
             "X do jardim do lavabo (hoje coberto pela palmeira), os X da garagem, da faixa abaixo dela e da área "
             "descoberta (hoje finos e apagados). Os armários e painéis da DOC_LINHAS conferidos um a um: até o teto em "
             "marcenaria areia, sem a diagonal (seção 7)", [(850, 1715), (2660, 1260), (2900, 420)]),
        (16, "Jardins (seção 10): o da sala íntima (5,5 m²) e o do lavabo só verdes, com as plantas da biblioteca no "
             "tamanho real, sem passar das paredes nem dos vidros; hoje palmeiras grandes saindo do canteiro",
         [(1630, 1713), (2660, 1250)]),
        (17, "Cortinas (seção 8): os 12 panos do PDF em linho off-white (suíte master: 2 em cima e 2 na lateral; sala "
             "íntima, 2; suítes 1, 2 e 3, 2 em cada), com o trilho de parede a parede. Hoje: nenhuma",
         [(645, 1450), (1510, 1680), (1250, 1740), (2400, 1740)]),
        (18, "Portas, vidros e janelas finos (seções 4 e 18): os caixilhos do render ampliado redesenhados na espessura "
             "do PDF: vidro claro com as duas faces em linha fina, caixilho de alumínio, peitoril em pedra",
         [(1830, 960), (1500, 1330)]),
        (19, "Louças (seção 6, 22/10): todas as bacias com a tampa (conferir uma a uma: banho master, banhos 1, 2 e 3, "
             "lavabo, banho gourmet e WC DCE) e as cubas em louça branca, também as duas da cozinha e as do serviço "
             "(hoje em inox) e a da gourmet", [(1900, 400), (2140, 1650), (2500, 1255)]),
        (20, "Paredes pretas no contorno do PDF (seção 2, 21/10): bordas retas e cantos nítidos, sem falhas dentro nem "
             "sobras para fora, em todas as paredes", [(1800, 1330)]),
        (21, "Soleiras (R13): conferir porta a porta com o PDF, na resolução da prancha; onde o vão fica em branco, "
             "soleira em Bege Bahia, com as faces da parede em cinza fino; onde o piso atravessa, sem soleira. A do "
             "elevador em inox escovado (seção 4)", [(1385, 1330), (2380, 690)]),
        (22, "Regras de 22/10 das Casas B e C que valem aqui: as 4 banquetas da ilha gourmet parcialmente sob o tampo e "
             "o box do banho gourmet (piso em granito) em cinza claro, visível. A confirmar para a Casa D (pedidos das "
             "Casas B e C): bancadas e ilhas em pedra areia humanizada (hoje o quartzo claro de 15/10)",
         [(1560, 705), (1450, 420), (1900, 580)]),
        (23, "A confirmar (como na Casa C, \"PODE MANTER O JOGO DE CAMA QUE ESTAVA ANTES\"): as camas e os bancos ao pé "
             "delas ficam os do render aprovado de 15/10, ou entram a roupa de cama da biblioteca", [(860, 1480), (1340, 1520)]),
        (None, "Conferido na escala e conforme: o quadro (59,7 px/m; as paredes do PDF caem sobre as da prancha e o "
               "elevador sobre o do Subsolo); piscina, prainha e spa em Barlavento, com a borda alta e o dreno de 15/10; "
               "acesso de veículos em granito, como a garagem (15/10); cooktops de 5 bocas; tanques duplos; máquinas e "
               "eletrodomésticos em inox; elevador com a cabine; sem pilares (o PDF da Casa D não tem a EST_PILAR); "
               "lote tracejado e curvas de nível ocultas", []),
    ],
}


def mapa(chave, saida):
    img = Image.open(CASA_D / "entrega" / f"POE642_CasaD_PH_{chave}_entrega.png").convert("RGB")
    itens = PENTE_FINO[chave]
    x0, y0, x1, y1 = RECORTE[chave]
    img = img.crop((x0, y0, x1, y1))
    d = ImageDraw.Draw(img)
    fn = fonte("SemiBold", 34)
    for n, _, pontos in itens:
        for x, y in pontos:
            cx, cy = x - x0, y - y0
            d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), outline=VERMELHO, width=5)
            d.text((cx + 30, cy - 34), str(n), font=fn, fill=VERMELHO, stroke_width=3, stroke_fill=(255, 255, 255))
    # legenda
    W = img.width
    fl = fonte("Regular", 30)
    blocos = [quebrar(f"{n}. {t}" if n else t, fl, W - 80, d) for n, t, _ in itens]
    alt = 40 + sum(44 * len(b) + 14 for b in blocos)
    leg = Image.new("RGB", (W, alt), (255, 255, 255))
    dl = ImageDraw.Draw(leg)
    y = 30
    for b in blocos:
        for li in b:
            dl.text((40, y), li, font=fl, fill=(30, 30, 30))
            y += 44
        y += 14
    final = Image.new("RGB", (W, img.height + alt), (255, 255, 255))
    final.paste(img, (0, 0))
    final.paste(leg, (0, img.height))
    nome = saida / f"POE642_CasaD_PH_{chave}_pente_fino_mapa.jpg"
    final.save(nome, quality=88)
    print(f"    {nome} ({sum(1 for n, _, _ in itens if n)} itens)")


def prancha(chave):
    return cv2.imread(str(CASA_D / "entrega" / f"POE642_CasaD_PH_{chave}_entrega.png"))


def regua(img, x, y, k):
    """Régua de 1 m (0,5 m preto e 0,5 m branco) na imagem ampliada k vezes."""
    m = int(round(PX_M * k))
    cv2.rectangle(img, (x, y), (x + m // 2, y + 12), (0, 0, 0), -1)
    cv2.rectangle(img, (x + m // 2, y), (x + m, y + 12), (255, 255, 255), -1)
    cv2.rectangle(img, (x, y), (x + m, y + 12), (0, 0, 0), 2)


def escalas(saida):
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import texturas as TX
    k, L = 6, int(round(1.5 * PX_M))   # trechos de 1,5 x 1,5 m, ampliados 6 vezes
    pr = {ch: prancha(ch) for ch in ("Terreo", "Subsolo")}
    ft, fs = fonte("SemiBold", 34), fonte("Regular", 28)
    blocos = []
    for titulo, ch, (x, y), mat in ESCALA_PISOS:
        a = pr[ch][y:y + L, x:x + L]
        b = np.clip(TX.textura(mat, PX_M, L, L), 0, 255).astype(np.uint8)
        par = [cv2.resize(t, None, fx=k, fy=k, interpolation=cv2.INTER_NEAREST) for t in (a, b)]
        for t in par:
            regua(t, 14, 14, k)
        im = Image.new("RGB", (2 * L * k + 30, L * k + 90), (255, 255, 255))
        for i, t in enumerate(par):
            im.paste(Image.fromarray(t[..., ::-1]), (i * (L * k + 30), 90))
        d = ImageDraw.Draw(im)
        d.text((0, 6), titulo, font=ft, fill=(30, 30, 30))
        d.text((0, 48), "prancha atual  ·  biblioteca na mesma escala (1,5 × 1,5 m)", font=fs, fill=(90, 90, 90))
        blocos.append(im)
    W = blocos[0].width
    for titulo, (x0, y0, x1, y1) in ESCALA_VEGETACAO:
        a = pr["Terreo"][y0:y1, x0:x1].copy()
        kv = W / a.shape[1]
        a = cv2.resize(a, None, fx=kv, fy=kv, interpolation=cv2.INTER_CUBIC)
        regua(a, 14, 14, kv)
        im = Image.new("RGB", (W, a.shape[0] + 60), (255, 255, 255))
        im.paste(Image.fromarray(a[..., ::-1]), (0, 60))
        ImageDraw.Draw(im).text((0, 8), f"Vegetação · {titulo} (régua de 1 m)", font=ft, fill=(30, 30, 30))
        blocos.append(im)
    # duas colunas: os pisos à esquerda, a vegetação à direita
    esq, dir_ = blocos[:len(ESCALA_PISOS)], blocos[len(ESCALA_PISOS):]
    alt = max(sum(b.height + 40 for b in esq), sum(b.height + 40 for b in dir_))
    folha = Image.new("RGB", (2 * W + 120, alt + 40), (255, 255, 255))
    for col, lista in enumerate((esq, dir_)):
        y = 40
        for b in lista:
            folha.paste(b, (40 + col * (W + 40), y))
            y += b.height + 40
    nome = saida / "POE642_CasaD_PH_escalas_conferencia.jpg"
    folha.save(nome, quality=85)
    print(f"    {nome}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimentos", nargs="*", default=None)
    ap.add_argument("--saida", type=Path, default=CASA_D / "renders")
    ap.add_argument("--escalas", action="store_true", help="a folha de conferência das escalas")
    args = ap.parse_args()
    if args.escalas:
        print("[escalas] folha de conferência")
        escalas(args.saida)
        return
    for ch in args.pavimentos or list(PENTE_FINO):
        print(f"[{ch}] mapa do pente fino")
        mapa(ch, args.saida)


if __name__ == "__main__":
    main()

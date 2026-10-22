#!/usr/bin/env python3
"""Pente fino pelas regras das plantas da Casa C (POE 642), como o da Casa B (`conferencia_casab.py`).

Pedido do usuário (22/10/26): "Casa C" (a ordem da seção 17 das regras: Casa E, Casa A, Casa B, Casa C, Casa D).
Cada prancha de entrega atual (`POE642_CasaC/entrega/POE642_CasaC_PH_<Pavimento>_entrega.png`) foi conferida
trecho a trecho contra o PDF do cliente (`_pdfs_cliente/642 - <PAVIMENTO> - CASA C.pdf`) e o `POE642_REGRAS.md`,
com as escalas medidas primeiro (seção 2, "ATENÇÃO ÀS ESCALAS"). O PDF vai ao quadro da prancha pela mesma cadeia
das bases (`opcoes_1pav_casae.quadro_pdf`, com a config da Casa C): 59,7 px/m, as paredes do PDF caem sobre as da
prancha. Os itens ficam em `PENTE_FINO` (pontos em px da prancha de 3840) e o script desenha o mapa numerado de
cada pavimento, com a legenda embaixo: `POE642_CasaC/renders/POE642_CasaC_PH_<Pavimento>_pente_fino_mapa.jpg`; com
`--escalas`, a folha das escalas (`POE642_CasaC/renders/POE642_CasaC_PH_escalas_conferencia.jpg`).

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
CASA_C = AQUI.parent.parent / "POE642_CasaC"
PX_M = 59.7   # px/m da prancha (o PDF a 1:50 no quadro da prancha, pelo alinhamento das paredes)
# folha das escalas: (título, pavimento, canto do trecho de 1,5 x 1,5 m na prancha, sem móveis, material da biblioteca)
ESCALA_PISOS = [
    ("Travertino · varanda gourmet", "Terreo", (1380, 1200), "travertino"),
    ("Vinílico · suíte master", "Terreo", (810, 700), "vinilico"),
    ("Granito marrom · área de serviço", "Terreo", (2480, 260), "granito_marrom"),
    ("Pedra portuguesa · acesso de carros", "Terreo", (2805, 100), "pedra_portuguesa"),
    ("Bege Bahia · pátio do Térreo", "Terreo", (490, 450), "bege_bahia"),
    ("Bege Bahia · pisante", "Terreo", (3132, 1215), "bege_bahia"),
    ("Grama", "Terreo", (2805, 1500), "grama"),
    ("Deck", "Terreo", (800, 1150), "madeira"),
    ("Bege Bahia · pátio do Subsolo", "Subsolo", (420, 400), "bege_bahia"),
    ("Travertino · varanda do Subsolo", "Subsolo", (700, 400), "travertino"),
    ("Vinílico · academia", "Subsolo", (1280, 630), "vinilico"),
    ("Bege Bahia · depósito", "Subsolo", (1110, 770), "bege_bahia"),
]
# vegetação: (título, recorte na prancha do Térreo)
ESCALA_VEGETACAO = [
    ("Canto de cima, à esquerda", (295, 50, 655, 320)),
    ("Faixa da esquerda, junto à piscina", (295, 1100, 475, 1820)),
    ("Junto à garagem, à direita", (3270, 330, 3510, 950)),
    ("Jardim de inverno", (1770, 810, 2030, 1190)),
]
# recorte de cada mapa (px da prancha de 3840), em volta da planta
RECORTE = {"Subsolo": (250, 180, 1900, 1700), "Terreo": (250, 30, 3560, 1880)}

# (número, texto, pontos em px da prancha de 3840); número None: nota sem marca no mapa (os conformes).
# Usuário (21/10/26), depois do primeiro mapa: "ATENÇÃO ÀS ESCALAS". As escalas vêm primeiro: cada textura
# medida na prancha (régua de 1 m = 59,7 px) ao lado da da biblioteca na mesma escala (`texturas.textura`), a
# vegetação medida folha a folha e os móveis, louças e carros sobrepostos ao contorno do PDF.
# Na Casa C as escalas e a regra de 22/10 "tudo desenhado na resolução da prancha" valem desde o começo: a proposta
# é refazer as duas finais em 3840 px como a da Casa B (`final3840_casab.py`), guardando as decisões de 14/10.
PENTE_FINO = {
    "Subsolo": [
        (1, "Só o Subsolo, com o resto do terreno hachurado (R2): o lote do Térreo final em diagonais finas a 45°, "
            "cinza-claro, como nas Casas A, B e E; hoje o resto do lote está em branco, sem o contorno. A confirmar o "
            "que fica em cor cheia. Pelo PDF do Subsolo, o cinza cheio é o pátio, a faixa dos degraus largos e o "
            "caminho (o Bege Bahia de 14/10), com os bocéis tracejados. Proposta: em cor cheia o Subsolo, o pátio, os "
            "degraus largos e o caminho, como hoje; deck, piscina, casa, jardins e garagem do Térreo na hachura",
         [(1300, 1250), (1650, 1450)]),
        (2, "Escala do Bege Bahia (R1, seção 18): placa de 0,60 m com as nuvens de 10 a 20 cm e o tom quente da "
            "referência (~230, 211, 186). Hoje: liso e rosado (~228, 213, 203), com riscos brancos do motor. No pátio, "
            "nos degraus largos, no caminho e no depósito", [(420, 450), (1110, 850), (520, 1400)]),
        (3, "Escala do travertino (R1, seção 3): o da biblioteca, placa de 1,20 m, veios horizontais de 5 a 20 cm (o "
            "aprovado na Casa B). Hoje: estrias verticais contínuas de vários metros. Na varanda do Subsolo, na sauna, "
            "na ducha e no BH academia", [(760, 380)]),
        (4, "Escala do vinílico (R4): réguas de ~20 cm, no sentido do PDF (deitadas na academia). Hoje: desfocado, com "
            "veio de madeira e sem réguas (~171, 134, 106)", [(1300, 650)]),
        (5, "Floreira junto à sauna (seção 10, 22/10): faixa de ~0,5 m do lado de fora da parede esquerda da sauna. "
            "Hoje as folhas passam por cima dos degraus largos. Plantas da biblioteca no tamanho real, só verdes, "
            "dentro da floreira", [(650, 860)]),
        (6, "Escadas (R14 e seção 5): degraus largos em Bege Bahia, com a linha cinza suave nos bocéis e a sombra de "
            "~10 cm, sem traço preto. No PDF do Subsolo o \"S\" está no degrau 11 (a escada estreita sobe do caminho "
            "para o deck). Proposta: nos largos, o triângulo (24 × 26 cm) no degrau 1, junto ao pátio, apontando para o "
            "caminho (para baixo na planta); a estreita (11 a 21) segue esmaecida (14/10), com o triângulo no 11 "
            "apontando para a direita. A confirmar", [(450, 760), (780, 1020)]),
        (7, "Portas sem arcos (R3): as 3 portas de giro do PDF (circulação da sauna, BH academia e depósito). Ficam as "
            "folhas, finas e brancas, na espessura do PDF, e os batentes; o piso segue limpo onde estava o arco",
         [(830, 770), (930, 760), (1020, 760)]),
        (8, "Portas, vidros e janelas finos (seções 4 e 18): a parede de vidro entre a varanda e a academia e a porta "
            "de vidro da sauna, com as duas faces em linha fina e o vidro claro", [(1065, 550), (720, 742)]),
        (9, "Rótulos (seção 12, novos na Casa C): os 5 ambientes do PDF com nome e área (varanda subsolo, academia, "
            "depósito, sauna e BH academia), mais o elevador, em Inter no corpo do PDF × 1,3, pretos nos pisos claros, "
            "sem sombra, dentro do ambiente e fora dos objetos (R7)", [(900, 520), (1341, 491)]),
        (10, "Louças (seção 6, 22/10): a bacia do BH academia com a tampa e a cuba em louça branca", [(962, 915)]),
        (11, "Soleiras (R13): conferir porta a porta com o PDF, na resolução da prancha; onde o vão fica em branco, "
             "soleira em Bege Bahia, com as faces da parede em cinza fino; onde o piso atravessa, sem soleira. A do "
             "elevador em inox escovado (seção 4)", [(1795, 865)]),
        (12, "Paredes pretas no contorno do PDF (seção 2, 21/10): bordas retas e cantos nítidos, sem falhas dentro nem "
             "sobras para fora", [(1250, 925)]),
        (13, "Tudo na resolução da prancha (seção 2, 22/10): a final do Subsolo refeita em 3840 px, como a da Casa B: "
             "pisos da biblioteca, aparelhos, louças e banco da sauna nítidos no contorno do PDF, sem os borrões do "
             "render ampliado", [(1250, 400)]),
        (None, "Conferido na escala e conforme: o quadro (59,7 px/m, o elevador cai sobre o do Térreo); esteiras, "
               "bicicletas e supinos no tamanho do PDF; banco da sauna em travertino, em L e em dois níveis (14/10); "
               "chuveiros de teto da ducha e do box (14/10); elevador com a cabine; sem pilares (o PDF da Casa C não "
               "tem a EST_PILAR); curvas de nível ocultas", []),
    ],
    "Terreo": [
        (1, "Escala da vegetação (seção 10, R1): a do motor está grande demais, com leques de palmeira de ~2 m e folhas "
            "de costela-de-adão de ~1 m. Entram as plantas da biblioteca no tamanho real, com a sombra, só dentro do "
            "lote e fora dos pisos, nos quatro cantos, na faixa junto à piscina e em volta do bloco externo da garagem",
         [(420, 200), (380, 1500), (3380, 560), (2950, 920)]),
        (2, "Escala da pedra portuguesa (R1, seção 3): pedras de 6 a 8 cm, em leque, no tom da foto (bege, cinza e "
            "rosado). Hoje: pedras arredondadas regulares de ~10 a 12 cm, em caramelo (~181, 144, 108), no acesso de "
            "carros", [(3050, 150)]),
        (3, "Escala e desenho do granito marrom (seção 3): nuvens suaves e lascas de agregado, no tom da referência "
            "(~118, 89, 69). Hoje: quase liso e escuro (~82, 61, 55). Cozinha, louceiro, serviço, área descoberta, "
            "quarto e BH de serviço, o bloco externo e a garagem", [(2300, 560), (3150, 700)]),
        (4, "Escala do travertino (R1, seção 3): o da biblioteca, placa de 1,20 m, veios horizontais de 5 a 20 cm, sem "
            "riscos nem emendas (Casa B, 22/10). Hoje: estrias verticais contínuas de vários metros. Áreas sociais, "
            "circulações, hall, varandas, lavabos e BH master 1", [(1700, 1150), (2550, 1400)]),
        (5, "Escala do vinílico (R4): réguas de ~20 cm, claras, em tons alternados, como desenha o PDF. Hoje: liso, com "
            "veio de madeira e sem réguas (~171, 134, 106). Suíte master, quartos, closets e escritório",
         [(1000, 780), (1460, 450), (2690, 1050)]),
        (6, "Escala do Bege Bahia (R1, seção 18): placa de 0,60 m com as nuvens de 10 a 20 cm e o tom quente da "
            "referência (~230, 211, 186). Hoje: liso e rosado (~229, 212, 198), com riscos brancos. Pátio, degraus "
            "largos, caminho, escada estreita, pisantes e os banhos (BH 1, 2, 3 e master 2)",
         [(490, 450), (3132, 1260), (560, 1500)]),
        (7, "Grama e madeira da referência (R4): a grama do motor tem grão miúdo e verde claro (~105, 121, 64); a da "
            "referência é ~71, 84, 42, com manchas suaves de 0,5 a 1 m. As réguas do deck estão na escala, mas o tom é "
            "avermelhado (~165, 115, 84; a madeira da referência é ~191, 160, 133): a troca do tom, como na Casa B",
         [(2600, 1600), (900, 1200)]),
        (8, "Carros (R12): os 3 do PDF em prata, alinhados e do mesmo tamanho, 4,70 × 1,85 m (281 × 110 px). Hoje: "
            "~4,47 × 1,91 m, em branco, prata e grafite", [(2980, 470)]),
        (9, "Tudo na resolução da prancha (seção 2, 22/10): a final do Térreo refeita em 3840 px, como a da Casa B "
            "(`final3840_casac.py`): pisos da biblioteca, móveis, louças, bancadas e plantas nítidos no contorno do "
            "PDF, sem os borrões do render ampliado, guardando as decisões de 14/10 (itens 1 a 25 do retoque: "
            "chuveiros de teto, cooktops de 5 bocas, bancos ao pé das camas, cadeiras das escrivaninhas, elevador)",
         [(2150, 1060), (1950, 1420)]),
        (10, "Rótulos (seção 12, novos na Casa C): os 46 ambientes do PDF com nome e área, mais o elevador, em Inter no "
             "corpo do PDF × 1,3; brancos no granito (R6) e nos jardins, pretos nos pisos claros, sem sombra e dentro "
             "do ambiente. Nenhum sobre objeto (R7): no PDF, SUÍTE MASTER, QUARTO 1 e QUARTO 3 caem sobre a cama e "
             "GOURMET sobre a bancada; vão para o piso livre mais perto", [(1007, 664), (1363, 425), (1427, 1025)]),
        (11, "Portas sem arcos (R3): as 25 portas de giro do PDF, inclusive os 8 arcos cinza do granito (14/10, item "
             "23) e os portões duplos da área descoberta. Ficam as folhas, finas e brancas, e os batentes; a "
             "pivotante do hall com a folha até a ponta do PDF (14/10, item 22), sem os arcos",
         [(840, 530), (1240, 820), (2615, 525), (2700, 1300), (1300, 1510)]),
        (12, "Escadas com linhas e triângulo (R14): no Térreo as duas descem (\"D\" do PDF junto ao degrau 21). A "
             "estreita desce do deck para o caminho (triângulo no topo, junto ao deck, apontando para a esquerda) e os "
             "degraus largos seguem descendo do caminho para o pátio (triângulo no 10, apontando para cima). Bocéis com "
             "a linha cinza suave e a sombra de ~10 cm, sem traço preto, em Bege Bahia. Hoje: traços e a sombra do "
             "motor", [(790, 1040), (500, 850)]),
        (13, "Guarda-corpos de vidro (seção 9, 22/10), da ARQ_ELEMENTOS FIXOS, hoje nenhum aparece: o L da varanda "
             "master (7,2 m em cima e 9,7 m à esquerda, sobre o pátio), a borda de cima da varanda dos quartos (6,3 m) "
             "e a da varanda 1 (2,9 m). Vidro claro com as duas faces em linha fina, a sombra curta, as quinas "
             "fechadas e os fechamentos até a parede", [(636, 520), (850, 247), (1440, 247), (2090, 247)]),
        (14, "O L junto ao deck: no PDF é uma floreira em L (ARQ_PAISAGISMO, mureta de ~10 cm), que segue em faixa ao "
             "lado da piscina; hoje é o banco de bronze da Casa B, posto por analogia em 14/10 (\"confirmar com o "
             "usuário\"). A confirmar: floreira com plantas, só verdes, ou banco em bronze fosco", [(700, 1180)]),
        (15, "Projeções (R8) em tracejado bem visível: a claraboia da varanda master, as dos closets master 1 (hoje X "
             "em traço contínuo) e master 2 (hoje não aparece), os X dos jardins de inverno 1 e 2 (cobertos pelas "
             "plantas) e o X da área de serviço descoberta (hoje apagado). Os armários e painéis da DOC_LINHAS "
             "conferidos um a um: até o teto em marcenaria areia, sem a diagonal (seção 7)",
         [(800, 270), (930, 460), (990, 880), (2588, 170)]),
        (16, "Jardins (seção 10, 22/10): jardim de inverno 1, jardim de inverno 2 e jardim 1 só verdes, com o canteiro "
             "na sala inteira, sem passar dos vidros nem das paredes (hoje a palmeira do jardim 1 passa da parede), as "
             "plantas da biblioteca no tamanho real (hoje leques de ~2 m) e o X da projeção por cima (item 15)",
         [(1900, 1040), (1960, 861), (1180, 900)]),
        (17, "Cortinas (seção 8): as 7 do PDF (2 nas portas da varanda da suíte master, 3 nos quartos 2 e 3 e 2 no "
             "quarto 1) em linho off-white, com o trilho de parede a parede e um pano só por janela. Hoje: só "
             "pontinhos escuros", [(796, 700), (1500, 345), (2040, 342)]),
        (18, "Portas, vidros e janelas finos (seções 4 e 18): hoje caixilhos largos em tubo cinza nas portas de correr "
             "das varandas dos quartos e da suíte master e nas janelas da cozinha e da área descoberta. Vidro claro "
             "com as duas faces em linha fina, caixilho de alumínio, peitoril em pedra", [(1250, 322), (2590, 250)]),
        (19, "Louças (seção 6, 22/10): todas as bacias com a tampa (conferir uma a uma: BH master 1 e 2, BH 1, 2 e 3, "
             "lavabos masculino, feminino e da adega, BH de serviço e BH externo) e as cubas em louça branca, também "
             "as da cozinha e da gourmet", [(1297, 1610), (1466, 1610), (2680, 580)]),
        (20, "Tapete da sala TV: o do PDF (branco, sob o sofá e a poltrona) hoje quase não se distingue do travertino; "
             "entra no contorno do PDF, em linho claro, com a borda nítida", [(1430, 835)]),
        (21, "Paredes pretas no contorno do PDF (seção 2, 21/10): bordas retas e cantos nítidos, sem falhas dentro nem "
             "sobras para fora, em todas as paredes", [(1645, 1050)]),
        (22, "Soleiras (R13): conferir porta a porta com o PDF, na resolução da prancha; onde o vão fica em branco, "
             "soleira em Bege Bahia, com as faces da parede em cinza fino; onde o piso atravessa, sem soleira. A do "
             "elevador em inox escovado (seção 4)", [(1900, 330), (2430, 1200)]),
        (23, "Regras de 22/10 da Casa B que valem aqui: banquetas da ilha da cozinha parcialmente sob o tampo e o box "
             "dos banhos de piso em granito em cinza claro, onde houver. A confirmar para a Casa C (pedidos só da Casa "
             "B): bancadas e ilhas em pedra areia humanizada (hoje o quartzo claro de 14/10)",
         [(2300, 450), (1380, 1110), (2890, 790)]),
        (None, "Conferido na escala e conforme: o quadro (59,7 px/m; as paredes do PDF caem sobre as da prancha e o "
               "elevador sobre o do Subsolo); piscina em Barlavento com o spa e a prainha; cooktops de 5 bocas; "
               "chuveiros de teto; elevador com a cabine; sem pilares (o PDF da Casa C não tem a EST_PILAR); lote "
               "tracejado e curvas de nível ocultas", []),
    ],
}


def mapa(chave, saida):
    img = Image.open(CASA_C / "entrega" / f"POE642_CasaC_PH_{chave}_entrega.png").convert("RGB")
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
    nome = saida / f"POE642_CasaC_PH_{chave}_pente_fino_mapa.jpg"
    final.save(nome, quality=88)
    print(f"    {nome} ({sum(1 for n, _, _ in itens if n)} itens)")


def prancha(chave):
    return cv2.imread(str(CASA_C / "entrega" / f"POE642_CasaC_PH_{chave}_entrega.png"))


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
    nome = saida / "POE642_CasaC_PH_escalas_conferencia.jpg"
    folha.save(nome, quality=85)
    print(f"    {nome}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimentos", nargs="*", default=None)
    ap.add_argument("--saida", type=Path, default=CASA_C / "renders")
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

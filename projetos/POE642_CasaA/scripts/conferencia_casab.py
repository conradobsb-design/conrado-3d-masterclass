#!/usr/bin/env python3
"""Pente fino pelas regras das plantas da Casa B (POE 642), como o da Casa A (`conferencia_casaa.py --pente-fino`).

Pedido do usuário (21/10/26): "SEGUIMOS PARA A CASA B" (a ordem da seção 17 das regras: Casa E, Casa A, Casa B, Casa C,
Casa D). Cada prancha de entrega atual (`POE642_CasaB/entrega/POE642_CasaB_PH_<Pavimento>_entrega.png`) foi conferida
trecho a trecho contra o PDF do cliente (`_pdfs_cliente/642 - <PAVIMENTO> - CASA B.pdf`) e o `POE642_REGRAS.md`. O PDF
foi levado ao quadro da prancha por alinhamento das paredes (ECC afim; prancha ≈ PDF a 1,2 px/pt × 0,878 + (126,5; −238)).
Os itens ficam em `PENTE_FINO` (pontos em px da prancha de 3840) e o script desenha o mapa numerado de cada pavimento,
com a legenda embaixo: `POE642_CasaB/renders/POE642_CasaB_PH_<Pavimento>_pente_fino_mapa.jpg`.

Depois do primeiro mapa, o usuário pediu "ATENÇÃO ÀS ESCALAS": com `--escalas`, a folha de conferência das escalas
(`POE642_CasaB/renders/POE642_CasaB_PH_escalas_conferencia.jpg`): cada piso da prancha ao lado do da biblioteca
(`_texturas/texturas.textura`) na mesma escala (1,5 × 1,5 m a 59,7 px/m, ampliados 6 vezes), e a vegetação com uma régua de 1 m.

Uso (da pasta POE642_CasaA/scripts/):
  python3 conferencia_casab.py            # os dois mapas
  python3 conferencia_casab.py Terreo
  python3 conferencia_casab.py --escalas  # a folha das escalas
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from conferencia_casaa import VERMELHO, fonte, quebrar

AQUI = Path(__file__).resolve().parent
CASA_B = AQUI.parent.parent / "POE642_CasaB"
PX_M = 59.7   # px/m da prancha (o PDF a 1:50 no quadro da prancha, pelo alinhamento das paredes)
# folha das escalas: (título, pavimento, canto do trecho de 1,5 x 1,5 m na prancha, sem móveis, material da biblioteca)
ESCALA_PISOS = [
    ("Pedra portuguesa · acesso", "Terreo", (2900, 1740), "pedra_portuguesa"),
    ("Granito marrom · área descoberta", "Terreo", (1900, 1700), "granito_marrom"),
    ("Travertino · living", "Terreo", (1610, 1000), "travertino"),
    ("Vinílico · sala íntima", "Terreo", (1620, 630), "vinilico"),
    ("Grama", "Terreo", (2880, 660), "grama"),
    ("Deck · varanda", "Terreo", (700, 1400), "madeira"),
    ("Bege Bahia · garagem do Subsolo", "Subsolo", (1000, 330), "bege_bahia"),
    ("Travertino · depósito do Subsolo", "Subsolo", (1564, 330), "travertino"),
]
# vegetação: (título, recorte na prancha do Térreo)
ESCALA_VEGETACAO = [
    ("Canto de cima, à esquerda", (220, 40, 900, 640)),
    ("Frente da área de serviço", (1380, 1640, 1900, 1980)),
    ("Jardim de inverno", (1980, 700, 2300, 960)),
]
# recorte de cada mapa (px da prancha de 3840), em volta da planta
RECORTE = {"Subsolo": (250, 180, 1900, 1180), "Terreo": (200, 0, 3640, 2060)}

# (número, texto, pontos em px da prancha de 3840); número None: nota sem marca no mapa (os conformes).
# Usuário (21/10/26), depois do primeiro mapa: "ATENÇÃO ÀS ESCALAS". As escalas vêm primeiro: cada textura
# medida na prancha (régua de 1 m = 59,7 px) ao lado da da biblioteca na mesma escala (`texturas.textura`), a
# vegetação medida folha a folha e os móveis, louças e carros sobrepostos ao contorno do PDF.
PENTE_FINO = {
    "Subsolo": [
        (1, "Só o Subsolo, com o resto do terreno hachurado (R2): saem os esmaecidos do Térreo e o lote fica em diagonais "
            "finas a 45°, em cinza-claro, como nas Casas A e E. A confirmar o que fica em cor cheia. Pelo PDF, as duas "
            "escadas sobem do nível da ducha (\"S\" no Subsolo, \"D\" no Térreo) e o deck em L ao lado da ducha continua "
            "no mesmo nível, sem degrau; a pedra grande e as pedras da esquerda ficam no alto da escada de 6 degraus. "
            "Proposta: em cor cheia a ducha, o deck em L e o início das duas escadas; a pedra grande e as pedras, que "
            "estão no nível do Térreo, vão para a hachura (hoje a pedra grande está em cor cheia, decisão de 14/10)",
         [(350, 740), (530, 740), (674, 990)]),
        (2, "Escala do Bege Bahia (R1, seção 18): placa de 0,60 m com as nuvens de 10 a 20 cm visíveis e o tom quente da "
            "referência (~230, 211, 186). Hoje: liso e rosado (~228, 214, 205), sem nuvens, com riscos brancos do motor na "
            "garagem. Na garagem, nas duas circulações e no BH serviço", [(1120, 420), (1200, 700)]),
        (3, "Escala do travertino (R1, seção 3): placa de 1,20 m, veios horizontais de 5 a 20 cm (o aprovado da casa). "
            "Hoje: estrias verticais contínuas de vários metros. No depósito, na sauna e no banco, no BH sauna e na pedra "
            "grande", [(1680, 400), (1050, 660)]),
        (4, "Academia: o piso (réguas de ~20 cm) e os aparelhos estão na escala do PDF, mas em volta das bicicletas e do "
            "supino ficaram retângulos de piso em outro tom, sobras da colagem dos objetos do render; o piso fica contínuo",
         [(1447, 476), (1447, 543), (1474, 656)]),
        (5, "Escada de 6 degraus (R14 e seção 18): sobe da ducha para a pedra grande (o \"S\" do PDF; usuário: \"desce da "
            "pedra grande para a ducha\"). Bocéis com a linha cinza suave e a sombra curta, sem traço preto; o triângulo "
            "(24 × 26 cm) no 1º degrau, junto à ducha, apontando para a esquerda; depois do corte, esmaecida e tracejada. "
            "Hoje: traços finos e a seta", [(714, 644)]),
        (6, "Escada de 9 degraus (R14): sobe do deck em L para a varanda; o triângulo no 1º degrau, à esquerda, apontando "
            "para a direita; cheia até o corte e esmaecida depois. Hoje: esmaecida inteira, com a seta (depende do item 1)",
         [(994, 834)]),
        (7, "Portas sem arcos (R3): as 4 portas de giro do PDF (BH serviço, depósito, circulação da sauna e BH sauna). "
            "Ficam as folhas, finas e brancas, na espessura do PDF, e os batentes",
         [(1424, 350), (1530, 344), (1180, 644), (1262, 636)]),
        (8, "Portas, vidros e janelas finos (seções 4 e 18): a parede de vidro entre a garagem e a academia (hoje caixilho "
            "branco largo, com montante), os vidros da sauna em folha contínua e o vidro do box do BH serviço",
         [(1366, 520), (964, 680), (1470, 394)]),
        (9, "Rótulos (seção 12, novos na Casa B): os 9 ambientes do PDF com nome e área (garagem, as duas circulações, BH "
            "serviço, depósito, academia, sauna, BH sauna e ducha), mais o elevador, em Inter no corpo do PDF × 1,3. Nenhum "
            "sobre objeto (R7): o \"BH SERVIÇO\" do PDF cai sobre a bacia e vai para o piso livre. O shaft só se pedido",
         [(1600, 600), (1100, 500)]),
        (10, "Soleiras (R13): conferir porta a porta com o PDF; onde o vão fica em branco, soleira em Bege Bahia na escala, "
             "com as faces da parede em cinza fino; onde o piso atravessa, sem soleira", [(1490, 300), (1300, 610)]),
        (11, "Paredes pretas no contorno do PDF (seção 2, 21/10): bordas retas e cantos nítidos, sem falhas dentro nem "
             "sobras para fora, em todas as paredes", [(1600, 770)]),
        (12, "Pilares (R8): os dois pilares redondos da EST_PILAR estão no PDF do Subsolo, mas caem no terreno, sob o bloco "
             "do motorista do Térreo. Proposta: não desenhar no Subsolo (ficam no Térreo, item 11). A confirmar", []),
        (None, "Conferido na escala e conforme: o quadro (59,7 px/m, o elevador cai sobre o do Térreo), as réguas da ducha "
               "(~18 cm), esteiras, bicicletas e supino no tamanho do PDF, elevador com a cabine, shaft com o X, armário "
               "ao lado do elevador sem diagonal, banco da sauna em dois níveis, louças e chuveiros, garagem sem carros "
               "(o PDF não tem)", []),
    ],
    "Terreo": [
        (1, "Escala da vegetação (seção 10, R1): a do motor está de 1,5 a 3 vezes o tamanho real. Costela-de-adão com "
            "folhas de ~1,5 m (a real chega a ~0,9 m), samambaias com frondes de ~2,6 m, estrelícias com a flor de ~1,2 m; "
            "no jardim de inverno, leques de palmeira de ~2,2 m. Entram as plantas da biblioteca no tamanho real, com a "
            "sombra, só dentro do lote e fora dos pisos (hoje passam do muro e do lote nos quatro cantos e na frente da "
            "área de serviço)", [(400, 220), (3300, 280), (400, 1760), (1600, 1800), (3360, 1400), (2136, 800)]),
        (2, "Escala da pedra portuguesa (R1, seção 3): pedras de 6 a 8 cm, em leque, no tom da foto (bege, cinza e rosado). "
            "Hoje: uma trama regular de quadrinhos de ~15 cm, em caramelo, na garagem e no acesso", [(3000, 1760)]),
        (3, "Escala e desenho do granito marrom (seção 3): nuvens suaves e lascas de agregado de vários tamanhos, no tom da "
            "referência (~118, 89, 69). Hoje: quase liso, com estrias verticais e sem grão, bem mais escuro (~90, 60, 58). "
            "Cozinha, serviço, área descoberta e o bloco do motorista", [(1600, 1380), (1920, 1800)]),
        (4, "Escala do travertino (R1, seção 3): placa de 1,20 m, veios horizontais de 5 a 20 cm. Hoje: estrias verticais "
            "contínuas de vários metros. Living, varanda, hall, banhos e pisantes", [(1700, 1120), (3100, 1060)]),
        (5, "Escala do vinílico (R4): réguas de ~20 cm, claras, em tons alternados, como desenha o PDF. Hoje: liso, com "
            "veio de madeira e sem réguas, nas suítes, no closet master, na sala íntima e na circulação",
         [(1200, 600), (2100, 560), (2100, 725)]),
        (6, "Grama e madeira da referência (R4): a grama do motor tem grão miúdo e verde mais claro (~89, 111, 43); a da "
            "referência é ~71, 84, 42, com manchas suaves de 0,5 a 1 m. As réguas do deck já estão na escala (~19 cm), mas "
            "o tom é avermelhado (~170, 114, 86; a madeira da referência é ~191, 160, 133): a confirmar a troca do tom "
            "(também na ducha do Subsolo)", [(3000, 840), (860, 1560)]),
        (7, "Carros (R12): os 3 do PDF em prata, alinhados e do mesmo tamanho, 4,70 × 1,85 m (282 × 110 px). Hoje: o bloco "
            "do PDF, de ~4,4 × 1,8 m, em branco, prata e grafite", [(2520, 1520)]),
        (8, "Rótulos (seção 12, novos na Casa B): os 37 ambientes do PDF com nome e área, mais o elevador, em Inter no corpo "
            "do PDF × 1,3; brancos no granito (R6: cozinha, louceiro, despensa, serviço, quarto e BH de serviço, área "
            "descoberta e o bloco do motorista). Nenhum sobre objeto (R7): no PDF, SUÍTE 3 cai sobre a cama, PRAINHA sobre "
            "a espreguiçadeira e LAVABO sobre a bancada. A confirmar: o \"SUÍTE 2 · 15,71 m²\" solto na faixa de travertino "
            "atrás da suíte master (proposta: não entra) e o banho da suíte master, que no PDF se chama \"SUÍTE MASTER · "
            "13,7 m²\"", [(2540, 750), (980, 1200), (1700, 1400)]),
        (9, "Portas sem arcos (R3): as ~25 portas de giro do PDF; ficam as folhas, finas e brancas, na espessura do PDF, e "
            "os batentes. A pivotante do hall com a folha até a ponta do PDF (seção 4)",
         [(1520, 560), (2460, 1100), (1160, 1580), (2280, 1320)]),
        (10, "Escadas com linhas e triângulo (R14): no Térreo as duas descem (\"D\" do PDF). A de 6 degraus desce da pedra "
             "grande para a ducha (triângulo de 24 × 26 cm no topo, junto à pedra, apontando para a direita); a de 9 "
             "degraus desce da varanda para o deck em L (triângulo no topo, junto à varanda, apontando para a esquerda). "
             "Bocéis com a linha cinza suave e a sombra de ~10 cm, sem traço preto. Hoje: traços e setas",
         [(714, 644), (994, 810)]),
        (11, "Pilares (R8): os 2 pilares redondos da EST_PILAR, no bloco do motorista (paredes do depósito e do banho), em "
             "preto como as paredes, no diâmetro do PDF. Hoje não aparecem", [(2816, 1380), (2816, 1500)]),
        (12, "Projeções (R8): o X tracejado do jardim de inverno (4 painéis, DOC_LINHAS E PROJEÇÕES) bem visível por cima "
             "das plantas (hoje coberto); sai o X tracejado que o motor desenhou no hall interno, em volta do pufe, que "
             "não está no PDF", [(2136, 1065)]),
        (13, "Portões em zigue-zague da ARQ_ELEMENTOS FIXOS: entre o jardim do hall e a garagem e entre a área de serviço "
             "descoberta e a garagem. Hoje somem sob as plantas e o piso; entram finos, como no PDF (seção 4, porta "
             "camarão). A confirmar se são portões ou brises, e a cor", [(2460, 1284), (2170, 1676)]),
        (14, "Armários até o teto (seção 7): closet master e os armários das suítes 1, 2 e 3 em marcenaria areia com veio, "
             "sem a diagonal da DOC_LINHAS, que hoje aparece", [(1400, 660), (2000, 630), (2600, 440), (2430, 840)]),
        (15, "Eletrodomésticos em inox (seção 7): na cozinha, os quadrados sem diagonal à direita da ilha (hoje "
             "marcenaria bege) e o refrigerador (\"Ref.\") do gourmet (hoje bege)", [(1780, 1460), (1160, 1510)]),
        (16, "Cooktops (seção 7): o da bancada gourmet e o da ilha da cozinha com as 5 bocas do PDF (bloco "
             "cooktop_inox_5_90, de 0,88 × 0,50 m, como nas Casas A e E). Hoje: 6 bocas no gourmet e bocas embaralhadas "
             "na ilha", [(1380, 1364), (1690, 1480)]),
        (17, "Adega (seção 7): a prateleira de vinhos do PDF, na parede de baixo, e não armário (hoje um banco bege)",
         [(2130, 1222)]),
        (18, "Sala íntima: a bancada clara do PDF (ARQ_BANCADAS), com a cuba e a torneira, junto ao shaft; o motor fez um "
             "móvel de madeira com um enfeite", [(1580, 656)]),
        (19, "Elevador: a porta em inox com a soleira em inox escovado (seção 4); proposta: a cabine do Subsolo, como nas "
             "Casas C, D e E. Hoje: caixa branca vazia", [(1773, 603)]),
        (20, "Portas, vidros e janelas finos (seções 4 e 18): hoje caixilhos largos, brancos ou em tubo cinza (janelas da "
             "suíte master, das suítes e dos banhos, adega, jardim do hall, porta de correr da cozinha)",
         [(960, 560), (2000, 320), (2430, 1194)]),
        (21, "Cortinas (seção 8): as linhas onduladas do PDF (suíte master, sala íntima, suítes 1, 2 e 3) em linho "
             "off-white, com o trilho de parede a parede (bloco cortina). Hoje: só manchas marrons do motor",
         [(970, 500), (1740, 340), (2640, 740)]),
        (22, "Paredes pretas no contorno do PDF (seção 2, 21/10): bordas retas e cantos nítidos, sem falhas dentro nem "
             "sobras para fora, em todas as paredes", [(2340, 960)]),
        (23, "Soleiras (R13): conferir porta a porta com o PDF; onde o vão fica em branco, soleira em Bege Bahia na escala, "
             "com as faces da parede em cinza fino; onde o piso atravessa, sem soleira", [(2280, 700), (1820, 1660)]),
        (24, "Pedidos de 21/10 na Casa A, a confirmar para a Casa B: roupa de cama da biblioteca nas camas (suítes, quarto "
             "de serviço e motorista), quartzito Carrara nas bancadas e na ilha, boxes com as folhas contínuas e "
             "banquetas de linho na bancada gourmet", [(1100, 680), (1680, 1640), (1380, 430)]),
        (25, "A peça branca comprida abaixo do lavatório gourmet, do lado de fora (na ARQ_PAREDE, 50 cm de fundo): "
             "pendente desde a entrega. A confirmar o que é (floreira, banco ou peitoril)", [(1320, 1662)]),
        (None, "Conferido na escala e conforme: o quadro (59,7 px/m; o elevador cai sobre o do Subsolo); camas, bancos, "
               "criados, sofás, poltronas, mesas e cadeiras, bacias, cubas, tanques e espreguiçadeiras no contorno do PDF "
               "(sobreposto à prancha); réguas do deck (~19 cm); piscina em Barlavento com o spa e a prainha; pufe do hall; "
               "banco em L de bronze no deck; pisantes; shafts com o X", []),
    ],
}


def mapa(chave, saida):
    img = Image.open(CASA_B / "entrega" / f"POE642_CasaB_PH_{chave}_entrega.png").convert("RGB")
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
    nome = saida / f"POE642_CasaB_PH_{chave}_pente_fino_mapa.jpg"
    final.save(nome, quality=88)
    print(f"    {nome} ({sum(1 for n, _, _ in itens if n)} itens)")


def prancha(chave):
    return cv2.imread(str(CASA_B / "entrega" / f"POE642_CasaB_PH_{chave}_entrega.png"))


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
    nome = saida / "POE642_CasaB_PH_escalas_conferencia.jpg"
    folha.save(nome, quality=85)
    print(f"    {nome}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimentos", nargs="*", default=None)
    ap.add_argument("--saida", type=Path, default=CASA_B / "renders")
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

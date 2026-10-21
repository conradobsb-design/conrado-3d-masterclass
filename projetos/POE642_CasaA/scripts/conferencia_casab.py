#!/usr/bin/env python3
"""Pente fino pelas regras das plantas da Casa B (POE 642), como o da Casa A (`conferencia_casaa.py --pente-fino`).

Pedido do usuário (21/10/26): "SEGUIMOS PARA A CASA B" (a ordem da seção 17 das regras: Casa E, Casa A, Casa B, Casa C,
Casa D). Cada prancha de entrega atual (`POE642_CasaB/entrega/POE642_CasaB_PH_<Pavimento>_entrega.png`) foi conferida
trecho a trecho contra o PDF do cliente (`_pdfs_cliente/642 - <PAVIMENTO> - CASA B.pdf`) e o `POE642_REGRAS.md`. O PDF
foi levado ao quadro da prancha por alinhamento das paredes (ECC afim; prancha ≈ PDF a 1,2 px/pt × 0,878 + (126,5; −238)).
Os itens ficam em `PENTE_FINO` (pontos em px da prancha de 3840) e o script desenha o mapa numerado de cada pavimento,
com a legenda embaixo: `POE642_CasaB/renders/POE642_CasaB_PH_<Pavimento>_pente_fino_mapa.jpg`.

Uso (da pasta POE642_CasaA/scripts/):
  python3 conferencia_casab.py            # os dois mapas
  python3 conferencia_casab.py Terreo
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from conferencia_casaa import VERMELHO, fonte, quebrar

AQUI = Path(__file__).resolve().parent
CASA_B = AQUI.parent.parent / "POE642_CasaB"
# recorte de cada mapa (px da prancha de 3840), em volta da planta
RECORTE = {"Subsolo": (250, 180, 1900, 1180), "Terreo": (200, 0, 3640, 2060)}

# (número, texto, pontos em px da prancha de 3840)
PENTE_FINO = {
    "Subsolo": [
        (1, "Só o Subsolo, com o resto do terreno hachurado (R2): saem os esmaecidos do Térreo e o lote fica em diagonais "
            "finas a 45°, em cinza-claro, como nas Casas A e E. A confirmar o que fica em cor cheia. Pelo PDF, as duas "
            "escadas sobem do nível da ducha (\"S\" no Subsolo, \"D\" no Térreo) e o deck em L ao lado da ducha continua "
            "no mesmo nível, sem degrau; a pedra grande e as pedras da esquerda ficam no alto da escada de 6 degraus. "
            "Proposta: em cor cheia a ducha, o deck em L e o início das duas escadas; a pedra grande e as pedras, que "
            "estão no nível do Térreo, vão para a hachura (hoje a pedra grande está em cor cheia, decisão de 14/10)",
         [(350, 740), (530, 740), (674, 990)]),
        (2, "Escada de 6 degraus (R14 e seção 18): sobe da ducha para a pedra grande (o \"S\" do PDF; usuário: \"desce da "
            "pedra grande para a ducha\"). Bocéis com a linha cinza suave e a sombra curta, sem traço preto; o triângulo "
            "no 1º degrau, junto à ducha, apontando para a esquerda; depois do corte, esmaecida e tracejada. Hoje: "
            "traços finos e a seta", [(714, 644)]),
        (3, "Escada de 9 degraus (R14): sobe do deck em L para a varanda; o triângulo no 1º degrau, à esquerda, apontando "
            "para a direita; cheia até o corte e esmaecida depois. Hoje: esmaecida inteira, com a seta (depende do item 1)",
         [(994, 834)]),
        (4, "Portas sem arcos (R3): as 4 portas de giro do PDF (BH serviço, depósito, circulação da sauna e BH sauna). "
            "Ficam as folhas, finas e brancas, e os batentes", [(1424, 350), (1530, 344), (1180, 644), (1262, 636)]),
        (5, "Portas, vidros e janelas finos (seções 4 e 18): a parede de vidro entre a garagem e a academia (hoje caixilho "
            "branco largo, com montante), os vidros da sauna em folha contínua e o vidro do box do BH serviço",
         [(1366, 520), (964, 680), (1470, 394)]),
        (6, "Bege Bahia como a referência (seção 18), com as nuvens visíveis e o tom quente: na garagem, nas duas "
            "circulações e no BH serviço. Hoje está rosado e, na garagem, com riscos brancos do motor",
         [(1120, 420), (1200, 700)]),
        (7, "Travertino na escala, com o veio na horizontal (seções 3 e 18; o aprovado da casa): depósito, sauna e banco, "
            "BH sauna e pedra grande. Hoje o veio corre na vertical. A madeira da ducha segue a do deck do Térreo "
            "(item 19 do Térreo)", [(1680, 400), (1050, 660)]),
        (8, "Rótulos (seção 12, novos na Casa B): os 9 ambientes do PDF com nome e área (garagem, as duas circulações, BH "
            "serviço, depósito, academia, sauna, BH sauna e ducha), mais o elevador. Nenhum sobre objeto (R7): o \"BH "
            "SERVIÇO\" do PDF cai sobre a bacia e vai para o piso livre. O shaft só se pedido (como na Casa A)",
         [(1600, 600), (1100, 500)]),
        (9, "Soleiras (R13): conferir porta a porta com o PDF; onde o vão fica em branco, soleira em Bege Bahia com as faces "
            "da parede em cinza fino; onde o piso atravessa, sem soleira", [(1490, 300), (1300, 610)]),
        (10, "Paredes pretas no contorno do PDF (seção 2, 21/10): bordas retas e cantos nítidos, sem falhas dentro nem "
             "sobras para fora, em todas as paredes", [(1600, 770)]),
        (11, "Pilares (R8): os dois pilares redondos da EST_PILAR estão no PDF do Subsolo, mas caem no terreno, sob o bloco "
             "do motorista do Térreo. Proposta: não desenhar no Subsolo (ficam no Térreo, item 5). A confirmar", []),
    ],
    "Terreo": [
        (1, "Rótulos (seção 12, novos na Casa B): os 37 ambientes do PDF com nome e área, mais o elevador; brancos no "
            "granito (R6: cozinha, louceiro, despensa, serviço, quarto e BH de serviço, área descoberta e o bloco do "
            "motorista). Nenhum sobre objeto (R7): no PDF, SUÍTE 3 cai sobre a cama, PRAINHA sobre a espreguiçadeira e "
            "LAVABO sobre a bancada. A confirmar: o \"SUÍTE 2 · 15,71 m²\" solto na faixa de travertino atrás da suíte "
            "master (proposta: não entra) e o banho da suíte master, que no PDF se chama \"SUÍTE MASTER · 13,7 m²\"",
         [(2540, 750), (980, 1200), (1700, 1400)]),
        (2, "Portas sem arcos (R3): as ~25 portas de giro do PDF; ficam as folhas, finas e brancas, e os batentes. A "
            "pivotante do hall com a folha até a ponta do PDF (seção 4)", [(1520, 560), (2460, 1100), (1160, 1580),
                                                                           (2280, 1320)]),
        (3, "Escadas com linhas e triângulo (R14): no Térreo as duas descem (\"D\" do PDF). A de 6 degraus desce da pedra "
            "grande para a ducha (triângulo no topo, junto à pedra, apontando para a direita); a de 9 degraus desce da "
            "varanda para o deck em L (triângulo no topo, junto à varanda, apontando para a esquerda). Bocéis com a linha "
            "cinza suave e a sombra curta, sem traço preto. Hoje: traços e setas", [(714, 644), (994, 810)]),
        (4, "Carros (R12): os 3 do PDF em prata, alinhados e do mesmo tamanho (4,70 × 1,85 m). Hoje: branco, prata e "
            "grafite", [(2520, 1520)]),
        (5, "Pilares (R8): os 2 pilares redondos da EST_PILAR, no bloco do motorista (paredes do depósito e do banho), em "
            "preto como as paredes. Hoje não aparecem", [(2816, 1380), (2816, 1500)]),
        (6, "Projeções (R8): o X tracejado do jardim de inverno (4 painéis, DOC_LINHAS E PROJEÇÕES) bem visível por cima "
            "das plantas (hoje coberto); sai o X tracejado que o motor desenhou no hall interno, em volta do pufe, que "
            "não está no PDF", [(2136, 830), (2136, 1065)]),
        (7, "Portões em zigue-zague da ARQ_ELEMENTOS FIXOS: entre o jardim do hall e a garagem e entre a área de serviço "
            "descoberta e a garagem. Hoje somem sob as plantas e o piso; entram finos, como no PDF (seção 4, porta "
            "camarão). A confirmar se são portões ou brises, e a cor", [(2460, 1284), (2170, 1676)]),
        (8, "Armários até o teto (seção 7): closet master e os armários das suítes 1, 2 e 3 em marcenaria areia com veio, "
            "sem a diagonal da DOC_LINHAS, que hoje aparece", [(1400, 660), (2000, 630), (2600, 440), (2430, 840)]),
        (9, "Eletrodomésticos em inox (seção 7): na cozinha, os quadrados sem diagonal à direita da ilha (hoje "
            "marcenaria bege) e o refrigerador (\"Ref.\") do gourmet (hoje bege)", [(1780, 1460), (1160, 1510)]),
        (10, "Cooktops (seção 7): o da bancada gourmet e o da ilha da cozinha com as 5 bocas do PDF (bloco cooktop_inox_5_90, "
             "como nas Casas A e E). Hoje: 6 bocas no gourmet e bocas embaralhadas na ilha", [(1380, 1364), (1690, 1480)]),
        (11, "Adega (seção 7): a prateleira de vinhos do PDF, na parede de baixo, e não armário (hoje um banco bege)",
         [(2130, 1222)]),
        (12, "Sala íntima: a bancada clara do PDF (ARQ_BANCADAS), com a cuba e a torneira, junto ao shaft; o motor fez um "
             "móvel de madeira com um enfeite", [(1580, 656)]),
        (13, "Elevador: a porta em inox com a soleira em inox escovado (seção 4); proposta: a cabine do Subsolo, como nas "
             "Casas C, D e E. Hoje: caixa branca vazia", [(1773, 603)]),
        (14, "Portas, vidros e janelas finos (seções 4 e 18): hoje caixilhos largos, brancos ou em tubo cinza (janelas da "
             "suíte master, das suítes e dos banhos, adega, jardim do hall, porta de correr da cozinha)",
         [(960, 560), (2000, 320), (2430, 1194)]),
        (15, "Cortinas (seção 8): as linhas onduladas do PDF (suíte master, sala íntima, suítes 1, 2 e 3) em linho "
             "off-white, com o trilho de parede a parede (bloco cortina). Hoje: só manchas marrons do motor",
         [(970, 500), (1740, 340), (2640, 740)]),
        (16, "Granito marrom no desenho e no tom da referência (seção 3): hoje RGB ~90, 60, 58, bem mais escuro que a "
             "referência (~118, 89, 69); cozinha, serviço, área descoberta e o bloco do motorista",
         [(1600, 1380), (1920, 1800)]),
        (17, "Pedra portuguesa em leque, no tom da foto (seção 3, 20/10: bege, cinza e rosado): hoje caramelo em trama, na "
             "garagem e no acesso", [(3000, 1760)]),
        (18, "Travertino na escala, com o veio na horizontal (seção 3): living, varanda, hall, banhos e pisantes; hoje o "
             "veio corre na vertical", [(1700, 1120), (3100, 1060)]),
        (19, "Grama e madeira da referência (R4): as réguas do deck já estão na escala (~19 cm), mas o tom é avermelhado "
             "(RGB ~170, 114, 86; a madeira da referência é ~191, 160, 133); a grama do motor é mais clara e saturada que "
             "a da referência. A confirmar a troca do tom do deck (também na ducha do Subsolo)",
         [(3000, 840), (860, 1560)]),
        (20, "Vegetação (seção 10): da biblioteca, no tamanho real e com a sombra, só dentro do lote e fora dos pisos. As "
             "touceiras do motor nos quatro cantos e na frente da área de serviço passam do muro e do lote",
         [(400, 220), (3300, 280), (400, 1760), (1600, 1800), (3360, 1400)]),
        (21, "Paredes pretas no contorno do PDF (seção 2, 21/10): bordas retas e cantos nítidos, sem falhas dentro nem "
             "sobras para fora, em todas as paredes", [(2340, 960)]),
        (22, "Soleiras (R13): conferir porta a porta com o PDF; onde o vão fica em branco, soleira em Bege Bahia com as "
             "faces da parede em cinza fino; onde o piso atravessa, sem soleira", [(2280, 700), (1820, 1660)]),
        (23, "Pedidos de 21/10 na Casa A, a confirmar para a Casa B: roupa de cama da biblioteca nas camas (suítes, quarto "
             "de serviço e motorista), quartzito Carrara nas bancadas e na ilha, boxes com as folhas contínuas e "
             "banquetas de linho na bancada gourmet", [(1100, 680), (1680, 1640), (1380, 430)]),
        (24, "A peça branca comprida abaixo do lavatório gourmet, do lado de fora (na ARQ_PAREDE, 50 cm de fundo): "
             "pendente desde a entrega. A confirmar o que é (floreira, banco ou peitoril)", [(1320, 1662)]),
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
    blocos = [quebrar(f"{n}. {t}", fl, W - 80, d) for n, t, _ in itens]
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
    print(f"    {nome} ({len(itens)} itens)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimentos", nargs="*", default=None)
    ap.add_argument("--saida", type=Path, default=CASA_B / "renders")
    args = ap.parse_args()
    for ch in args.pavimentos or list(PENTE_FINO):
        print(f"[{ch}] mapa do pente fino")
        mapa(ch, args.saida)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Conferência item a item das plantas da Casa A (POE 642) contra o PDF do cliente, como na Casa E.

Pedido do usuário (19/10/26): "vamos fazer a conferência de item a item do render da casa A, conforme fizemos
com a casa E. Pegar o PDF da casa A e rever item a item com o render." Cada pavimento foi comparado lado a lado
com o PDF (`_pdfs_cliente/642 - <PAVIMENTO> - CASA A.pdf`), os dois no quadro comum. As divergências ficam em
`ITENS` (pontos em px de uma prévia de 2000 px do quadro comum) e o script desenha o mapa numerado de cada
pavimento, com a legenda embaixo: `renders/POE642_CasaA_PH_<Pavimento>_conferencia.jpg`.

Uso (da pasta POE642_CasaA/scripts/):
  python3 conferencia_casaa.py            # os três mapas
  python3 conferencia_casaa.py Terreo
  python3 conferencia_casaa.py --pente-fino   # mapas do pente fino pelas regras (21/10/26), sobre a prancha atual
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import rotulos_casaa as A
from rodape_entrega import FONTES, no_quadro_comum

LARGURA = 3840
VERMELHO = (205, 40, 40)
# recorte de cada mapa (px de 2000 do quadro comum), em volta da planta
RECORTE = {"Terreo": (360, 150, 1450, 1015), "1Pavimento": (620, 150, 1450, 880), "Subsolo": (540, 440, 1260, 875)}

# (número, texto, pontos em px de 2000 do quadro comum)
ITENS = {
    "Terreo": [
        (1, "Pilares redondos da varanda e o pilar junto ao gourmet em marrom; no PDF são os pilares estruturais "
            "(no padrão da Casa E, pretos como as paredes)", [(809, 301), (809, 473), (657, 650), (642, 847)]),
        (2, "Sala de estar: falta a poltrona da direita e os dois vasos de plantas junto ao sofá; o sofá curvo "
            "do PDF acompanha o tapete pela esquerda, o render o pôs ao longo do alto", [(1104, 243), (1027, 226)]),
        (3, "Estar sob a projeção do pavimento superior: no PDF são 4 poltronas em X com a mesa triangular no "
            "centro; o render fez uma mesa retangular com 6 cadeiras", [(1051, 390)]),
        (4, "Sala de jantar: a mesa do PDF é oval (pontas arredondadas); a do render é retangular chanfrada",
         [(1055, 510)]),
        (5, "Lavabo: falta o vaso sanitário (no alto, à direita) e o X tracejado da claraboia; no lugar, uma peça "
            "estranha com um arco", [(1205, 195)]),
        (6, "Escritório: no PDF a mesa tem uma cadeira em cima (de escritório) e duas embaixo; o render pôs "
            "duas em cima", [(1287, 215)]),
        (7, "Banho da varanda: uma bacia sanitária no lugar do chuveiro (o PDF tem a ducha e a divisória do box)",
         [(868, 828)]),
        (8, "Jardim (4,79 m²): sem plantas; o PDF tem três touceiras", [(825, 873)]),
        (9, "Área de serviço: a escada caracol saiu só como um traço fino sobre o granito (o PDF tem os degraus "
            "em leque e o corrimão)", [(1029, 818)]),
        (10, "Área de serviço: a porta da direita, no alto, está sem o arco", [(1050, 775)]),
        (11, "Quarto do motorista: a cama virou um bloco lilás, sem lençol nem travesseiro", [(1260, 612)]),
        (12, "Banho do motorista: o chuveiro e a divisória do box viraram um bloco lilás", [(1186, 655)]),
    ],
    "1Pavimento": [
        (1, "Suíte 3: os criados-mudos do PDF são redondos; os do render são quadrados", [(864, 188), (950, 188)]),
        (2, "Suíte 3: falta o banco ao pé da cama", [(907, 254)]),
        (3, "Suíte 2: falta o banco ao pé da cama", [(919, 558)]),
        (4, "Suíte master: falta o banco ao pé da cama", [(784, 681)]),
        (5, "Suíte 1: falta o banco ao pé das camas", [(1272, 749)]),
        (6, "Quarto de serviço: faltam a cama de solteiro e o criado-mudo (no lugar, uma faixa de madeira com "
            "dois quadrados claros)", [(1013, 730)]),
        (7, "Banho master: a banheira do PDF é oval; a do render é retangular de cantos arredondados", [(760, 781)]),
    ],
    "Subsolo": [
        (1, "Banho de serviço: faltam o chuveiro (na parede da esquerda) e a divisória de vidro do box",
         [(590, 480)]),
        # usuário (19/10/26): o banco é horizontal; a faixa vertical à esquerda é o piso da piscina, a passagem
        # da sauna para a piscina ("não é em L")
        (2, "Sauna: o banco horizontal do PDF, ao longo da parede de baixo, virou piso na v6, por decisão anterior "
            "(a faixa vertical à esquerda é a passagem da sauna para a piscina e fica como piso)", [(670, 840)]),
        # apontado pelo usuário (19/10/26), depois da conferência
        (3, "Escada que desce do deck para a circulação: depois da linha de corte do PDF (a diagonal), os degraus "
            "devem ter a cor e a textura do Subsolo, visíveis; antes dela (três degraus, vindo de cima), "
            "esmaecidos", [(525, 566)]),
    ],
}


# pente fino pelas regras (POE642_REGRAS.md, 21/10/26; pedido do usuário: "siga com a Casa A"), sobre a prancha atual
# (a final com os rótulos), como o da Casa E: mapa em renders/POE642_CasaA_PH_<Pavimento>_pente_fino_mapa.jpg
RECORTE_PF = {"Subsolo": (330, 130, 1290, 900), "Terreo": (130, 55, 1820, 1025), "1Pavimento": (560, 120, 1480, 900)}
PENTE_FINO = {
    "Subsolo": [
        (1, "Só o Subsolo, com o resto do terreno hachurado (R2): o deck, a piscina, o spa, a escada larga e as "
            "espreguiçadeiras são do Térreo (hoje esmaecidos) e saem; o terreno do lote fica em diagonais finas a 45°, "
            "em cinza-claro, como na Casa E", [(440, 300), (600, 330), (520, 500)]),
        (2, "Gramado abaixo da escada do deck (pedido de 19/10, item 13): a proposta é que fique, porque foi pedido no "
            "nível da circulação, com a grama da referência na escala (R4). A confirmar", [(470, 720)]),
        (3, "Escada do deck, 11 degraus (R14 e seção 18): sobe da circulação (o \"S\" do PDF) para o deck. Bocéis com a "
            "linha cinza suave e a sombra curta; o triângulo no 1º degrau, junto à circulação, apontando para a "
            "esquerda; do corte em diante (degraus 9 a 11), esmaecida e tracejada. Hoje: sem linhas e sem triângulo",
         [(517, 570)]),
        (4, "Portas sem arcos (R3): as 5 portas de giro do PDF (banho de serviço, depósito, antessala da sauna, "
            "banhos feminino e masculino). Ficam as folhas, finas e brancas, e os batentes",
         [(609, 529), (715, 520), (733, 804), (794, 803), (956, 803)]),
        (5, "Portas, vidros e janelas finos (seções 4 e 18): entre a circulação interna e a externa, a porta de vidro de "
            "correr do PDF (duas folhas desencontradas) no lugar do traço preto grosso; a janela entre o depósito e a "
            "academia em vidro fino e claro; os vidros da sauna em folha contínua, sem montantes; a folha da porta do "
            "depósito fina e branca", [(660, 543), (722, 546), (622, 805)]),
        (6, "Bege Bahia como a referência (seção 18): a circulação externa, a circulação interna e o depósito estão "
            "rosados, com veios grandes, fora de escala. Entram o desenho e o tom da foto (RGB 230, 211, 186), na "
            "escala, com a luz do lugar, como na Casa E", [(600, 700), (684, 522), (900, 520)]),
        (7, "Travertino na escala (R1 e seção 18): no hall, os veios do motor estão na vertical, com riscos escuros; na "
            "sauna, na antessala e nos banhos, em faixas largas. Entra o travertino aprovado do Térreo da Casa A (veio "
            "horizontal, sem rejuntes), na mesma escala, com a luz do lugar", [(1130, 590), (690, 830), (812, 832),
                                                                               (935, 832)]),
        (8, "Shafts e projeções (R8): os dois shafts estão cheios, marrom e cinza, com o X contínuo; ficam brancos, com o "
            "X tracejado em cinza médio. Faltam três retângulos da camada DOC_LINHAS E PROJEÇÕES: ao longo das paredes "
            "de cima e da direita do depósito (0,5 e 0,7 m de fundo) e junto à parede de baixo da academia "
            "(3,5 × 0,4 m); entram em traço cinza fino, como no PDF. A confirmar o que são (prateleiras?)",
         [(1208, 563), (1234, 606), (826, 465), (963, 500), (876, 775)]),
        (9, "Soleiras (R13): conferir porta a porta com o PDF (banho de serviço, depósito, sauna, banhos, academia e "
            "hall). Onde o vão fica em branco, soleira em Bege Bahia com as faces da parede em cinza fino; onde o piso "
            "atravessa, sem soleira", [(622, 530), (785, 790), (948, 790)]),
        (10, "Rótulos (seção 12): o \"²\" encosta no \"m\" nos 9 rótulos; passa à regra de 20/10, logo depois do "
             "\"m\". Nenhum rótulo fica sobre objeto (conforme)", [(656, 507), (834, 660)]),
    ],
    "Terreo": [
        (1, "Escadas com linhas e triângulo (R14 e seção 18), nas quatro: a interna em U (do 1º degrau à esquerda do "
            "lanço de cima, para a direita; cheia até o corte, esmaecida e tracejada depois), a caracol da área de "
            "serviço (sobe da direita, anti-horário; degraus 1 a 7 cheios), a larga do deck ao pátio da piscina "
            "(degraus 12 a 19, hoje blocos de Bege Bahia sem linhas) e a do deck para o Subsolo (1 a 11: no Térreo, "
            "desce; o triângulo no topo, junto ao deck). Bocéis em linha cinza suave com a sombra curta. O sentido "
            "da larga, a confirmar (proposta: sobe do deck)", [(1234, 518), (1030, 813), (480, 245), (517, 570)]),
        (2, "Rótulos (R6 e seção 12): no granito marrom (cozinha, área gourmet, área de serviço, despensa, garagem e "
            "bloco do motorista) os rótulos estão em cinza; passam a branco. O \"²\" vai logo depois do \"m\" em todos",
         [(1040, 706), (953, 805), (1255, 772), (866, 703)]),
        (3, "Carros (R12): hoje branco, grafite e azul-marinho, desalinhados (pedido de 19/10, substituído pela regra). "
            "Passam a prata, alinhados e do mesmo tamanho (4,70 × 1,85 m), como na Casa E",
         [(1179, 779), (1268, 764), (1353, 773)]),
        (4, "Projeções em tracejado bem visível, por cima (R8 e R9): as da cobertura (a de baixo, junto aos brises, "
            "some sobre o Bege Bahia; a vertical da garagem e a de cima não aparecem), a do pergolado e a da laje "
            "superior na área de serviço, como no PDF", [(636, 871), (1372, 835), (774, 160), (981, 774)]),
        (5, "Portas, vidros e janelas finos (seções 4 e 18): o vidro entre a varanda e as salas e o do hall saíram como "
            "um tubo cinza grosso com nós (montantes); entram finos, claros, em folha contínua, com os perfis finos "
            "(como o item 8 do pente fino do Térreo da Casa E)", [(976, 330), (976, 440), (1274, 395)]),
        (6, "Armários até o teto (seção 7): na cozinha, na área de serviço e no quarto do motorista estão em lilás, com "
            "a diagonal do PDF desenhada; passam à marcenaria areia com veio, sem a diagonal",
         [(1048, 590), (1051, 740), (898, 817), (1310, 610)]),
        (7, "Grama na escala da referência (R1 e R4), no tom do render, como no Térreo da Casa E",
         [(300, 520), (1600, 860), (1500, 130)]),
        (8, "Deck de madeira (R4): réguas de ~20 cm, num marrom avermelhado; passa à madeira da referência, em réguas "
            "de ~15 cm", [(416, 380)]),
        (9, "Bege Bahia como a referência (seção 18): o entorno da piscina, o pátio de cima, o hall externo e os "
            "pisantes (hoje o das varandas do 1º Pavimento, claro e rosado); entram o desenho e o tom da foto, na escala",
         [(700, 200), (1335, 430), (1560, 380)]),
        (10, "Granito marrom (seção 3): hoje quase preto (RGB ~89, 65, 59); passa ao desenho e ao tom da referência "
             "do usuário (RGB ~118, 89, 69), como na Casa E", [(1000, 660), (960, 830), (1300, 728)]),
        (11, "Pedra portuguesa (seção 3): no acesso de veículos e na área de serviço descoberta está caramelo, em pedras "
             "grandes; passa ao leque com juntas claras, no tom da foto (bege, cinza e rosado), em pedras de 6 a 8 cm",
         [(926, 940), (1600, 940)]),
        (12, "Vegetação (seção 10): a do motor tem folhas de 1 a 1,3 m, fora de escala, e passa do lote nos cantos; "
             "troca pelas plantas da biblioteca, no tamanho real, só dentro do lote e fora dos pisos (como a opção A "
             "do Térreo da Casa E)", [(220, 130), (1700, 140), (230, 930), (1720, 700)]),
        (13, "Sala de jantar (item 4 da conferência de 19/10): a mesa do PDF é oval, com 8 cadeiras (corrigido em "
             "21/10: dizia 10); a do render é retangular chanfrada, com as mesmas 8", [(1050, 506)]),
        (14, "Escritório (item 6 da conferência de 19/10): no PDF, a cadeira de escritório em cima da mesa e as duas "
             "de visita embaixo; o render pôs duas em cima e duas embaixo", [(1289, 233)]),
        (15, "Banho da varanda (item 7 da conferência de 19/10): no PDF, o vaso em cima e o chuveiro com o box embaixo; "
             "o render pôs uma bacia no lugar do chuveiro", [(850, 825)]),
        (16, "Soleiras (R13): conferir porta a porta com o PDF; onde o vão fica em branco, soleira em Bege Bahia com as "
             "faces da parede em cinza fino; onde o piso atravessa, sem soleira", [(1130, 620), (900, 760)]),
    ],
    "1Pavimento": [
        (1, "Entorno (seção 11): o Térreo nublado em volta (70% de branco, 80% da saturação, desfoque leve), com a final "
            "do Térreo depois do pente fino, e o 1º Pavimento por cima, integralmente. Hoje o entorno é o do motor, "
            "quase apagado", [(650, 330), (1400, 320), (700, 880)]),
        (2, "Portas sem arcos (R3): os 11 arcos do PDF saem; ficam as folhas, finas e brancas, e os batentes",
         [(1278, 671), (1085, 708), (1145, 708), (1086, 237), (1041, 293), (925, 501), (1015, 615), (977, 652),
          (1085, 761), (890, 781), (1138, 803)]),
        (3, "Escadas (R14 e seção 5): a em U desce daqui (o \"D\" do PDF, 20 degraus): bocéis com a linha suave e a "
            "sombra curta, e o triângulo no topo (degrau 20), apontando para a descida; na caracol da saleta, só o "
            "trecho do pavimento cheio, com o triângulo", [(1215, 518), (1030, 808)]),
        (4, "Guarda-roupas com cabides (R11): nos closets 3, 2, 1 e master, o motor fez armários de madeira com riscos; "
            "entram os guarda-roupas da biblioteca, abertos, nos retângulos com diagonal do PDF, com as portas do "
            "lado do closet. A cor, a confirmar (proposta: como na Casa E, bege dentro, ocre na borda e o cabideiro "
            "de metal)", [(1014, 223), (971, 486), (932, 751), (1209, 656)]),
        (5, "Armários até o teto (seção 7): na circulação, na sala íntima e no quarto de serviço (os retângulos com "
            "diagonal do PDF), em marcenaria areia com veio, sem a diagonal", [(1114, 268), (1044, 557), (1121, 734)]),
        (6, "Bancos ao pé das camas (itens 2 a 5 da conferência de 19/10; seção 8): nas suítes 3, 2, master e 1, em "
            "estofado bege com textura, como na Casa E", [(907, 285), (919, 558), (784, 681), (1272, 749)]),
        (7, "Suíte 3 (item 1 da conferência): os criados-mudos do PDF são redondos; os do render, quadrados",
         [(864, 188), (950, 188)]),
        (8, "Quarto de serviço (item 6 da conferência): no lugar da faixa com dois quadrados claros, a cama de solteiro "
            "e o criado-mudo do PDF", [(1013, 730)]),
        (9, "Banho master (item 7 da conferência): a banheira do PDF é oval; a do render, retangular de cantos "
            "arredondados", [(760, 781)]),
        (10, "Cortinas (seção 8): nas janelas das quatro suítes, o motor fez fileiras de pontinhos; entram a cortina de "
             "linho da biblioteca e o trilho de parede a parede, como no 1º Pavimento da Casa E",
         [(842, 250), (835, 590), (712, 720), (1318, 760)]),
        (11, "Vinílico na escala (R4): nas suítes e nos closets, réguas da referência (~20 cm, claras, em tons "
             "alternados), na luz do lugar; hoje marrom médio", [(845, 300), (1230, 800), (880, 650)]),
        (12, "Bege Bahia das quatro varandas como a referência (seção 18): o desenho e o tom da foto, na escala, com os "
             "vasos e as plantas por cima", [(655, 736), (797, 539), (796, 242), (1388, 714)]),
        (13, "Projeções em tracejado bem visível (R8 e R9): as da cobertura (em cima e embaixo) e a do pergolado, como "
             "no PDF", [(900, 172), (1000, 856), (640, 470)]),
        (14, "Portas, vidros e janelas finos (seções 4 e 18): as portas de vidro de correr das suítes para as varandas "
             "saíram em caixilho grosso, com segmentos; entram as folhas finas do PDF, em dois planos",
         [(842, 195), (1328, 690), (700, 650)]),
        (15, "Soleiras (R13): conferir porta a porta com o PDF; onde o vão fica em branco, soleira em Bege Bahia com as "
             "faces da parede em cinza fino; onde o piso atravessa, sem soleira", [(1060, 690), (950, 520)]),
        (16, "Rótulos (seção 12): o \"²\" encosta no \"m\" nos 22 rótulos; passa à regra de 20/10. Nenhum fica sobre "
             "objeto (conforme)", [(1070, 546), (823, 690)]),
    ],
}


def fonte(peso, tam):
    return ImageFont.truetype(str(FONTES / f"Inter-{peso}.otf"), tam)


def quebrar(texto, f, largura, d):
    linhas, atual = [], ""
    for p in texto.split():
        t = f"{atual} {p}".strip()
        if d.textlength(t, font=f) > largura and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    return linhas + [atual]


def mapa(chave, saida, pente_fino=False):
    import json
    cfg = json.loads(A.CONFIG.read_text())
    q = A.PAVIMENTOS[chave]
    base = (A.CONFIG.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][chave]["base"]).resolve()
    if pente_fino:
        # o pente fino mostra a prancha atual: a final com os rótulos, já no quadro comum
        nome_final = Path(q["render"]).stem.split("_final")[0] + "_final_rotulos.png"
        img = Image.open(A.CASA / "renders" / nome_final).convert("RGB")
        itens, recorte = PENTE_FINO[chave], RECORTE_PF[chave]
    else:
        # o mapa mostra a imagem aprovada, antes dos ajustes
        img = no_quadro_comum(Image.open(A.CASA / q.get("aprovada", q["render"])).convert("RGB"), base, chave, LARGURA)
        itens, recorte = ITENS[chave], RECORTE[chave]
    k = LARGURA / 2000
    x0, y0, x1, y1 = recorte
    img = img.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k)))
    d = ImageDraw.Draw(img)
    fn = fonte("SemiBold", 34)
    for n, _, pontos in itens:
        for x, y in pontos:
            cx, cy = (x - x0) * k, (y - y0) * k
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
    nome = saida / f"POE642_CasaA_PH_{chave}_{'pente_fino_mapa' if pente_fino else 'conferencia'}.jpg"
    final.save(nome, quality=88)
    print(f"    {nome} ({len(itens)} itens)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimentos", nargs="*", default=None)
    ap.add_argument("--saida", type=Path, default=A.CASA / "renders")
    ap.add_argument("--pente-fino", action="store_true", help="mapa do pente fino pelas regras, sobre a prancha atual")
    args = ap.parse_args()
    for ch in args.pavimentos or list(PENTE_FINO if args.pente_fino else ITENS):
        print(f"[{ch}] mapa {'do pente fino' if args.pente_fino else 'da conferência'}")
        mapa(ch, args.saida, args.pente_fino)


if __name__ == "__main__":
    main()

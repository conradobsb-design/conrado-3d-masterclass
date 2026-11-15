"""A proposta da Casa D (15/11): a troca pela biblioteca e as notas do cliente da "Revisão das Plantas 2", ambiente por
ambiente, só para o OK (nada é aplicado aqui).

Usuário: "aprovado. vamos para a casa D"; "pode seguir com a casa D." Como nas Casas B e C (regra 0 do
`POE642_REGRAS_CONSOLIDADAS_CDE.md`: proposta antes, instalação depois): para cada ambiente, a planta de hoje (a final
aprovada em 29/10), as peças da biblioteca recomendadas (as escolhas das Casas A, B e C), o que muda e as notas do
cliente que caem ali (o texto do post-it, do quadro "POE 642 - Revisão de Imagens", coluna "REVISÃO DAS PLANTAS 2").

  python3 proposta_biblioteca_casad_1511.py
Saída: `POE642_CasaD/renders/POE642_CasaD_PH_{Terreo,Subsolo}_1511_proposta_<n>.jpg`.
"""
import textwrap
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
BIB = AQUI.parent / "biblioteca-objetos"
CASA_D = AQUI.parents[1] / "POE642_CasaD"
CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_D / "renders"
FONTES = AQUI.parent / "entrega" / "assets" / "fontes"
F_T = ImageFont.truetype(str(FONTES / "Inter-SemiBold.otf"), 38)
F_S = ImageFont.truetype(str(FONTES / "Inter-SemiBold.otf"), 24)
F_B = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 23)
F_P = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 21)
F_C = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 17)
W = 2600
TINTA, SUAVE, LINHA = (34, 38, 42), (105, 108, 112), (210, 206, 198)
POSTIT, ROSA = (252, 238, 150), (246, 170, 222)
FINAL = {"Terreo": R / "POE642_CasaD_PH_Terreo_final_rotulos.png", "Subsolo": R / "POE642_CasaD_PH_Subsolo_final_rotulos.png"}

# cada ambiente: título, recortes da final (x0, y0, x1, y1), peças da biblioteca (png, legenda), o que muda, notas
TERREO = [
 ("Suíte master, banho master e closet", [(500, 1321, 1207, 1757)],
  [("03-primeiro-pavimento/suite-master/cama-king-a", "cama king A"),
   ("03-primeiro-pavimento/suite-master/criado-retangular-vista-superior", "criado com abajur"),
   ("03-primeiro-pavimento/bancos-pe-de-cama/b1-veludo-bordo-casal", "banco B1 (veludo)"),
   ("03-primeiro-pavimento/suite-master/poltrona", "poltrona"), ("03-primeiro-pavimento/suite-master/pufe", "pufe"),
   ("03-primeiro-pavimento/suite-master/tapete", "tapete inteiro"),
   ("02-terreo/cortinas/cortina-linho-onda", "cortina C4"),
   ("03-primeiro-pavimento/banho-master/bancada-dupla-esculpida-render-v2", "bancada dupla esculpida"),
   ("03-primeiro-pavimento/banho-master/bacia-carrara", "bacia Carrara"),
   ("03-primeiro-pavimento/banho-master/chuveiro-quadrado-planta", "chuveiro em planta")],
  ["Cama king A da Casa C: manta de tricô caída nos pés (tom leve), travesseiro extra; criados da Casa A com abajur.",
   "Banco de pé de cama B1 em veludo (cada quarto num tom), a poltrona e o pufe da master em tons sóbrios.",
   "Cortina C4 nos trilhos do PDF; tapete da biblioteca inteiro, sem remendo.",
   "Banho master: bancada dupla esculpida no comprimento do PDF, bacias Carrara brancas, chuveiros desenhados, box em vidro claro, as claraboias só com o contorno.",
   "Closet: o guarda-roupa contínuo até o fim, na cor padrão dos armários, e o rótulo com nome e área."],
  ["Continuar o guarda-roupa até o final", "Nome e área do ambiente e metragem (closet da master)",
   "Representar as claraboias apenas com as linhas de fora, sem o X no meio [...] tom cinza e linhas fininhas."]),
 ("Suítes 1 e 2 e banhos 1 e 2", [(1079, 1393, 1450, 1757), (1793, 1393, 2193, 1757)],
  [("03-primeiro-pavimento/suite-2/cama-casal-a", "cama casal A"),
   ("03-primeiro-pavimento/suite-2/criado-redondo", "criado redondo"),
   ("03-primeiro-pavimento/bancos-pe-de-cama/b1-veludo-bordo-casal", "banco B1"),
   ("02-terreo/escritorio/cadeira-escritorio", "cadeira de escritório"),
   ("02-terreo/cortinas/cortina-linho-onda", "cortina C4"),
   ("03-primeiro-pavimento/banho-1/cuba-esculpida-travertino", "cuba esculpida"),
   ("03-primeiro-pavimento/banho-master/bacia-carrara", "bacia Carrara"),
   ("03-primeiro-pavimento/banho-master/chuveiro-quadrado-planta", "chuveiro em planta")],
  ["Camas casal A com a manta de tricô (como na Casa C), criados, bancos B1 em tons diferentes.",
   "Escrivaninha da suíte 1 com a cadeira de escritório, 1/3 sob o tampo.",
   "Banhos: cuba esculpida de travertino na bancada do PDF, bacia Carrara, chuveiro desenhado, box claro.",
   "Closets: os guarda-roupas em L contínuos, numa cor só, com o rótulo de cada closet."],
  ["Nome e área do ambiente e metragem (closets das suítes 1 e 2)", "Continuar o guarda-roupa até o final (suíte 1)",
   "Não tem soleira (passagem do closet da suíte 2)", "Padronizar a cor de representação do guarda-roupa"]),
 ("Suíte 3/escritório e banho 3", [(2036, 1336, 2536, 1757)],
  [("02-terreo/escritorio/mesa-a", "mesa"), ("02-terreo/escritorio/cadeira-escritorio", "cadeira de escritório"),
   ("02-terreo/escritorio/cadeira-visitante", "cadeira de visita"),
   ("03-primeiro-pavimento/sala-intima/sofa-l-a", "sofá (estar da suíte)"),
   ("02-terreo/cortinas/cortina-linho-onda", "cortina C4"),
   ("03-primeiro-pavimento/banho-1/cuba-esculpida-travertino", "cuba esculpida")],
  ["Mesa do escritório com a cadeira de escritório e as de visita; o estar da suíte com o sofá da biblioteca.",
   "Cortina C4 na janela junto ao jardim; o painel de ripas destacado do piso (madeira mais escura e o fio).",
   "Porta na quina da parede, em madeira que destaque do vinílico (a folha não some no piso).",
   "Banho 3 como os banhos 1 e 2."],
  ["Colocar cortina", "Melhorar a representação do painel (destacar mais em relação ao piso)",
   "A porta está \"entrando\" na parede e camuflando com a cor do piso", "Padronizar a cor de representação do guarda-roupa"]),
 ("Sala íntima, circulações e elevador", [(1300, 1200, 1800, 1720)],
  [("03-primeiro-pavimento/sala-intima/sofa-l-a", "sofá em L A"), ("03-primeiro-pavimento/sala-intima/tapete", "tapete"),
   ("03-primeiro-pavimento/sala-intima/mesa-lateral", "mesas laterais"),
   ("03-primeiro-pavimento/sala-intima/poltrona-a", "poltrona A"),
   ("03-primeiro-pavimento/closet-master/modulo-armario-canto", "armário na cor padrão")],
  ["Sala íntima com o conjunto da Casa A (regra das casas): sofá em L A, tapete, mesas laterais redondas e poltrona A, na pegada do PDF.",
   "Os armários da circulação, da sala íntima e ao lado do elevador sem textura, na cor padrão (RGB 208, 178, 156); o bloco ao lado do elevador vira armário (não pedra).",
   "Sem a linha dos armários sobre a bancada; um painel de madeira entre a escada e o elevador, no retângulo marcado."],
  ["Não é pedra, é armário", "Representar os armários e prateleiras sem textura. Com cor sólida e neutra como algumas casas acima.",
   "Geral: Não precisa representar os armários inferiores ou superiores com essa linha acima da bancada.",
   "Representar um painel aqui (entre a escada e o elevador)"]),
 ("Living, jantar, adega e hall", [(1800, 686, 2636, 1336)],
  [("03-primeiro-pavimento/sala-intima/vaso-folhagem-a", "vaso (planta da Casa A)"),
   ("02-terreo/sala-de-jantar/cadeira-jantar-oliva-render", "cadeira oliva (Casa A), opção")],
  ["O estar e o jantar ficam como aprovados em 29/10 (sem trocar o desenho); só sai o contorno dos móveis (nota geral).",
   "Os dois vasos do hall com a planta da Casa A; a seta da entrada no centro da porta, no modelo da Casa A.",
   "A escolher: as cadeiras do jantar ficam como estão, ou viram as oliva da Casa A, ou as azul-marinho da Casa C."],
  ["Usar a mesma representação de planta da casa A (vasos do hall)",
   "Centralizar a seta com a abertura da porta, usando este modelo de seta.",
   "Trocar essa representação do jardim de inverno e melhorar a linha tracejada. (jardim junto ao lavabo)"]),
 ("Varanda gourmet", [(1379, 693, 1800, 1200)],
  [("02-terreo/lounge-dos-brises/banco-brises", "banco estofado"),
   ("02-terreo/varanda/sofa-curvo-externo", "sofá curvo"), ("02-terreo/varanda/mesa-centro-seixo", "mesa seixo"),
   ("02-terreo/varanda/mesa-redonda", "mesa redonda"), ("02-terreo/varanda/cadeira-mesa-redonda", "cadeira")],
  ["O banco de madeira à esquerda do estar vira banco estofado (o banco dos brises da Casa A, almofada em linho).",
   "O resto da varanda como está (sofá curvo, mesas redondas), sem o contorno dos móveis."],
  ["Representar banco com estofamento"]),
 ("Gourmet e banho gourmet", [(1379, 357, 1800, 686)],
  [("02-terreo/cozinha/cooktop-quatro-bocas", "cooktop 4 bocas"),
   ("02-terreo/area-gourmet/cuba-franke-misturador-unic", "cuba Franke"),
   ("02-terreo/area-gourmet/grelha-churrasqueira", "churrasqueira"),
   ("02-terreo/area-gourmet/banqueta-b", "banqueta B"),
   ("02-terreo/lavabo/cuba-esculpida-poros-render", "cuba esculpida"),
   ("02-terreo/lavabo/bacia-carrara", "bacia (marrom)")],
  ["Churrasqueira com a grelha da Casa A no módulo do PDF; sem as linhas dos armários da bancada de trás.",
   "Cooktop de 4 bocas na ilha, cuba Franke com misturador; banquetas B com 40% do assento sob o tampo.",
   "Dois painéis pivotantes de madeira clara, fechados, no lado do deck (o retângulo marcado).",
   "Banho gourmet: cuba esculpida e bacia marrom; chuveiro desenhado; box claro."],
  ["Representar a churrasqueira", "Aqui tem que representar dois painéis pivotantes",
   "Geral: Não precisa representar os armários inferiores ou superiores com essa linha acima da bancada."]),
 ("Cozinha, louceiro e despensa", [(1800, 357, 2193, 686)],
  [("02-terreo/cozinha/cooktop-quatro-bocas", "cooktop 4 bocas"),
   ("02-terreo/cozinha/cuba-franke-dupla-vista-superior", "cubas Franke"),
   ("02-terreo/cozinha/geladeira-inox", "geladeira G2")],
  ["Ilha e bancada da pia em Dekton Danae; cooktop de 4 bocas e cubas Franke; geladeira inox G2 no vão do PDF.",
   "Louceiro e despensa: prateleiras e armários lisos, na cor padrão, sem textura.",
   "As floreiras das janelas da cozinha e do serviço num verde diferente do gramado."],
  ["Cor da ilha é no Dekton Danae", "Cor da bancada no dekton danae",
   "Representar os armários e prateleiras sem textura. Com cor sólida e neutra como algumas casas acima.",
   "Deixar o tom da vegetação dos jardins nas janelas diferente do terreno"]),
 ("Área de serviço, DCE térreo, área descoberta e gás", [(2186, 357, 2643, 686)],
  [("02-terreo/area-de-servico/cuba-franke-inox-link", "tanques Franke"),
   ("02-terreo/quarto-do-motorista/cama-solteiro-a", "cama solteiro A"),
   ("02-terreo/banho-do-motorista/cuba-compacta", "cuba"),
   ("02-terreo/banho-do-motorista/bacia-monte-carlo-sem-valvula", "bacia Monte Carlo")],
  ["Tanques Franke na bancada em Dekton Danae; armários do serviço lisos, na cor padrão.",
   "DCE: cama de solteiro A com a peseira; WC DCE com a bancada em marrom tabaco e o piso como os dos outros banhos da casa.",
   "Área descoberta: uma linha contínua na divisa, para o tracejado não ficar solto; o gás no granito marrom tabaco."],
  ["Bancada na pedra marrom tabaco (WC DCE)", "Cor do piso desse banheiro segue padrão dos outros dessa casa.",
   "Fazer uma linha contínua aqui pra linha tracejada não ficar voando.", "Piso do gás também é no marrom tabaco"]),
 ("Piscina, prainha, spa e deck", [(457, 357, 1379, 1200)],
  [],
  ["Água num azul mais sóbrio (o tom de referência das outras casas) e a diferença de fundo entre a piscina, a prainha e o spa mais marcada.",
   "O contorno da casa mais forte na borda do deck; a seta e a descrição nas escadas (DESCE PARA O JARDIM, para o Subsolo)."],
  ["Deixar o tom de azul para a piscina mais sóbrio. Ver exemplo.", "Mostrar melhor a diferença de profundidade",
   "Demarcar melhor o perímetro da casa", "Colocar a seta em todas as escadas e a descrição"]),
 ("Garagem, acesso e pergolados", [(2636, 357, 3150, 807)],
  [],
  ["Sai o tracejado do telhado; ficam só os vazios, as claraboias e os pergolados.",
   "Pergolados sem o X: só a estrutura, em cinza, tracejada; o de cima com os quadrados iguais aos do de baixo. Os carros ficam."],
  ["Remover as linhas tracejadas do telhado. [...] Deixar apenas as que representam 'vazios', claraboias e pergolados.",
   "Tirar o X dos vãos do pergolado. Representar apenas a estrutura dele em si. Representar com uma cor cinza. Fazer os quadrados no pergolado de cima igual o debaixo, essa é a estrutura dele. Com linhas tracejadas."]),
 ("Lavabo, jardins e paisagismo", [(2350, 1200, 2714, 1336), (1340, 1690, 1820, 1780)],
  [("02-terreo/lavabo/cuba-esculpida-poros-render", "cuba esculpida"), ("02-terreo/lavabo/bacia-carrara", "bacia"),
   ("02-terreo/paisagismo/oliveira", "oliveira"), ("02-terreo/paisagismo/moreia", "moreia"),
   ("02-terreo/paisagismo/filodendro-xanadu", "filodendro")],
  ["Lavabo: a cuba esculpida e a bacia como no lavabo da Casa C (bancada e cuba em granito marrom, a última decisão), a janela do jardim desenhada.",
   "Jardim do lavabo como o de 4,79 m² da Casa A (grama sóbria, poucas plantas menores, X fino).",
   "Gramado da Casa A: 80% grama, poucas árvores (como as 3 oliveiras da Casa C) e arbustos baixos."],
  ["Representar a janela (jardim do lavabo)", "OBS GERAL: No terreno não precisa representar muitas árvores [...] Representar arbustos que são menores."]),
]
SUBSOLO = [
 ("Academia", [(755, 1325, 1555, 1600)],
  [("01-subsolo/academia/esteira-a", "esteira A"), ("01-subsolo/academia/bicicleta-b", "bicicleta (da Casa A)"),
   ("01-subsolo/academia/banco-supino", "supino")],
  ["Os aparelhos da biblioteca nos tamanhos da Casa A (como no Subsolo da Casa B): 2 esteiras, 2 bicicletas e os 2 supinos, sem o contorno dos blocos, o vinílico refeito por baixo.",
   "A peça clara com a barra na parede de cima do vestiário sai (o cliente: não existe)."],
  ["usar o mesmo bloco de bicicleta usado na casa A", "Tirar o contorno dos blocos. (4 notas)", "Isso aqui não existe"]),
 ("Sauna e vestiário", [(755, 1595, 1290, 1750)],
  [("01-subsolo/sauna/banco-reto-travertino", "banco de travertino"),
   ("01-subsolo/banho-feminino-academia/cuba-esculpida-travertino", "cuba esculpida"),
   ("01-subsolo/banho-feminino-academia/bacia-carrara", "bacia Carrara"),
   ("01-subsolo/banho-feminino-academia/chuveiro-quadrado-parede", "chuveiro")],
  ["Sauna: os bancos no travertino do piso, em dois tons (em cima mais escuro), com a sombra, como na Casa B.",
   "Vestiário: a cuba esculpida no travertino (não a peça de sobrepor), a bacia Carrara e o chuveiro desenhado.",
   "Soleiras nas portas da sauna e do vestiário; portas quina a quina."],
  ["Os bancos da sauna é no mesmo material do piso. Lembrar de deixar ele em destaque em relação ao piso.",
   "A cuba não é assim. Está parecendo uma peça de sobrepor. Ela é esculpida no travertino.", "Colocar soleira aqui"]),
 ("DCE 1 e WC DCE", [(840, 995, 1090, 1160)],
  [("02-terreo/quarto-do-motorista/cama-solteiro-a", "cama solteiro A"),
   ("01-subsolo/banho-de-servico/cuba-servico-granito", "cuba no granito"),
   ("02-terreo/banho-do-motorista/bacia-monte-carlo-sem-valvula", "bacia Monte Carlo"),
   ("01-subsolo/banho-de-servico/chuveiro-redondo-parede", "chuveiro redondo")],
  ["Cama de solteiro A com a peseira; WC com a cuba no granito, a bacia Monte Carlo e o chuveiro redondo desenhado.",
   "O piso marrom tabaco na referência mais sóbria (as bancadas em destaque); os rótulos DCE 1 e WC DCE no mesmo corpo."],
  ["Deixar o tamanho das letras padronizadas.",
   "Lembrar de usar para o piso marrom tabaco a referência colocada lá em cima para dar destaque para as bancadas e o marrom do piso ficar mais sóbrio."]),
 ("Escada, depósito, pátio e entorno", [(650, 990, 1340, 1340)],
  [("01-subsolo/deposito/armario-despensa-fechado", "armário do depósito")],
  ["Como no Subsolo da Casa A: sem a hachura, fundo branco; seta e descrição na escada (SOBE PARA O TÉRREO); portas de giro quina a quina.",
   "A escada sem os degraus cortados em branco: transparente, na cor da escada (como na Casa C).",
   "O contorno da casa mais forte no pátio; o Bege Bahia com a textura na escala menor."],
  ["Não deixar os degraus cortados branco. Deixar transparente mas na mesma cor da escada. Exemplo casa C",
   "Demarcar melhor o perímetro da casa", "Diminuir a escala da textura",
   "Colocar a seta em todas as escadas e a descrição", "Melhorar representação das portas de giro. Encostar nas paredes."]),
]


def peca(rel, lado=150):
    im = cv2.imread(str(BIB / f"{rel}.png"), cv2.IMREAD_UNCHANGED)
    if im.ndim == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGRA)
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    ys, xs = np.nonzero(im[..., 3] > 8)
    if len(xs):
        im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = (lado - 10) / max(im.shape[:2])
    im = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    fundo = np.full((lado, lado, 3), 241, np.float32)
    h, w = im.shape[:2]
    y0, x0 = (lado - h) // 2, (lado - w) // 2
    a = im[..., 3:4].astype(np.float32) / 255
    fundo[y0:y0 + h, x0:x0 + w] = fundo[y0:y0 + h, x0:x0 + w] * (1 - a) + im[..., :3].astype(np.float32) * a
    return Image.fromarray(cv2.cvtColor(np.clip(fundo, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))


def linhas(texto, fonte, larg):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    out, cur = [], ""
    for p in texto.split():
        t = (cur + " " + p).strip()
        if d.textlength(t, font=fonte) <= larg:
            cur = t
        else:
            out.append(cur)
            cur = p
    if cur:
        out.append(cur)
    return out


def secao(final, n, titulo, recortes, pecas, muda, notas):
    # à esquerda, os recortes da planta de hoje (até 1150 x 760)
    ims = []
    for x0, y0, x1, y1 in recortes:
        c = final[y0:y1, x0:x1]
        ims.append(c)
    alt_max = 760 if len(ims) == 1 else 520
    esq = []
    for c in ims:
        k = min(1150 / c.shape[1], alt_max / c.shape[0], 2.2)
        esq.append(Image.fromarray(cv2.cvtColor(cv2.resize(c, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)))
    h_esq = sum(i.height for i in esq) + 14 * (len(esq) - 1) + 34
    # à direita: as peças (6 por linha), o que muda, as notas
    xr, lr = 1230, W - 1230 - 40
    blocos = []
    y = 0
    if pecas:
        y += 34
        y += ((len(pecas) + 5) // 6) * 196
    y += 40
    txt_muda = [linhas("• " + m, F_B, lr) for m in muda]
    y += sum(len(t) * 31 + 8 for t in txt_muda)
    y += 46
    txt_notas = [linhas("“" + t + "”", F_P, lr - 28) for t in notas]
    y += sum(len(t) * 28 + 26 for t in txt_notas)
    H = max(h_esq, y) + 110
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 64], fill=(244, 243, 239))
    d.text((40, 12), f"{n}. {titulo}", font=F_T, fill=TINTA)
    yy = 90
    d.text((40, yy - 4), "Hoje (a final aprovada em 29/10)", font=F_S, fill=SUAVE)
    yy += 30
    for im in esq:
        img.paste(im, (40, yy))
        d.rectangle([40, yy, 40 + im.width, yy + im.height], outline=LINHA, width=2)
        yy += im.height + 14
    y = 90
    if pecas:
        d.text((xr, y - 4), "Peças da biblioteca recomendadas", font=F_S, fill=SUAVE)
        y += 30
        for i, (rel, leg) in enumerate(pecas):
            cx, cy = xr + (i % 6) * 222, y + (i // 6) * 196
            img.paste(peca(rel), (cx, cy))
            d.rectangle([cx, cy, cx + 150, cy + 150], outline=LINHA, width=1)
            for j, l in enumerate(linhas(leg, F_C, 210)[:2]):
                d.text((cx, cy + 154 + j * 19), l, font=F_C, fill=TINTA)
        y += ((len(pecas) + 5) // 6) * 196 + 6
    d.text((xr, y), "O que muda", font=F_S, fill=SUAVE)
    y += 36
    for t in txt_muda:
        for l in t:
            d.text((xr, y), l, font=F_B, fill=TINTA)
            y += 31
        y += 8
    y += 10
    d.text((xr, y), "Notas do cliente (Revisão das Plantas 2)", font=F_S, fill=SUAVE)
    y += 36
    for t in txt_notas:
        h = len(t) * 28 + 14
        d.rectangle([xr, y, xr + lr, y + h], fill=POSTIT)
        for j, l in enumerate(t):
            d.text((xr + 14, y + 7 + j * 28), l, font=F_P, fill=TINTA)
        y += h + 12
    return img


def folhas(pav, lista, por_folha):
    final = cv2.imread(str(FINAL[pav]))
    secs = [secao(final, i + 1, *s) for i, s in enumerate(lista)]
    saidas = []
    for k in range(0, len(secs), por_folha):
        grupo = secs[k:k + por_folha]
        cab = Image.new("RGB", (W, 120), (255, 255, 255))
        dc = ImageDraw.Draw(cab)
        nome = "Térreo" if pav == "Terreo" else "Subsolo"
        dc.text((40, 26), f"Casa D · {nome} · proposta de 15/11 (biblioteca e notas do cliente), para o OK", font=F_T, fill=TINTA)
        dc.text((40, 76), "Nada aplicado ainda. Notas gerais: seta e descrição em todas as escadas; tirar o contorno dos mobiliários; as mudanças do Subsolo da Casa A que cabem.",
                font=F_P, fill=SUAVE)
        H = cab.height + sum(s.height + 24 for s in grupo)
        out = Image.new("RGB", (W, H), (255, 255, 255))
        out.paste(cab, (0, 0))
        y = cab.height
        for s in grupo:
            out.paste(s, (0, y))
            y += s.height + 24
        f = R / f"POE642_CasaD_PH_{pav}_1511_proposta_{k // por_folha + 1}.jpg"
        out.save(f, quality=86)
        saidas.append(f)
        print(f.name, out.size)
    return saidas


if __name__ == "__main__":
    folhas("Terreo", TERREO, 4)
    folhas("Subsolo", SUBSOLO, 4)

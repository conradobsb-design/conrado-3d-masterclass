#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Térreo da Casa E (POE 642).

O render (Nano Banana Pro, 2000 x 1116) manteve a escala da base: a base 16:9 reduzida ao tamanho do
render cai nele quase pela identidade (escala 0,9998 x 1,0066, deslocamento de 0,3 e -2,8 px). Os
retoques são feitos no quadro do render, como nas outras casas.

Itens (o mapa está em POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_erros.jpg):
1. Lote: a vegetação que o motor passou para fora do lote (à esquerda, embaixo e no alto à
   direita) sai, e as linhas tracejadas do lote, que ele apagou, voltam: fora do lote fica a base
   alinhada (o branco, a linha tracejada da esquerda, a da direita e o retângulo tracejado embaixo).
   Os muros de cima e de baixo, onde as folhas passavam por cima, voltam ao preto (cada linha do
   muro vira a mediana dela num trecho limpo).
2. Faixa à direita dos pisantes: a faixa em Bege Bahia que o motor inventou entre o gramado e a
   linha tracejada da direita (fora do gramado, branca no PDF) volta ao branco da base, no mesmo
   passo do item 1.
3. Jardim interno: as plantas, que o motor espalhou para fora da floreira (por cima da escada e no
   travertino em volta, com a sombra delas), ficam só no retângulo da floreira do PDF; fora dele
   voltam a escada (os degraus tracejados, da mesma coluna logo acima, e a linha diagonal, que segue
   até a floreira) e o travertino (da mesma coluna, mais abaixo: os veios correm na vertical), e a
   borda da floreira entra em traço fino.
4. Tapete do estar da varanda: o motor fez um tapete redondo; no PDF ele é orgânico (polígono branco
   da layer ARQ_MOBILIÁRIO), com um recorte em volta da ponta esquerda do sofá. O tapete toma a forma
   do PDF: o que sai vira travertino (as mesmas colunas da faixa limpa acima do tapete, pois os veios
   correm na vertical, na luz do travertino em volta e com a sombra dos móveis), o que entra vira
   tapete tecido do próprio tapete; sofá, poltronas, mesas e aparador ficam; borda fina por fora.
5. Varanda: as quatro barras a 45° à esquerda das poltronas (ARQ_ELEMENTOS FIXOS), que o motor
   apagou, voltam na geometria do PDF (cada uma, o retângulo girado da mancha do PDF), no cinza em que
   aparecem na base, com volume leve, contorno fino e sombra curta no piso.
6. Elevador: o motor fez a caixa num piso de pedra clara com um contorno de cabine solto no meio.
   Como nas Casas C e D: caixa branca e a cabine do Subsolo da Casa B aprovado (porta embaixo, como
   no PDF), ocupando a caixa inteira, com 1 a 2 px de folga; as folhas da porta e a soleira ficam.
7. CPD: o vaso sanitário que o motor pôs junto à parede da direita (no PDF o CPD não tem louça) sai,
   com a sombra; ali volta o granito tecido do próprio CPD, na luz do piso em volta.
8. Área de serviço: as duas máquinas do PDF (dois quadrados da ARQ_LAYOUT HUMANIZAÇÃO ao lado do
   tanque duplo), que o motor juntou num bloco de madeira, voltam como as máquinas em inox do Térreo
   da Casa D aprovado (cada uma, a metade do par de lá, no quadrado do PDF), com sombra curta; o resto
   do bloco vira o granito tecido do piso.
9. Área de serviço descoberta: o X tracejado do PDF (layer DOC_LINHAS E PROJEÇÕES: as duas
   diagonais e a linha de baixo), que o motor apagou, volta como a projeção sobre a garagem e a área
   descoberta da Casa D: cinza e traço fino, só sobre o granito.
10. DCE: o motor fez a cama como uma laje de pedra, o criado-mudo como um armário alto e o armário
    até o teto (o da diagonal) como uma pia. As três peças do render saem (granito tecido do próprio
    quarto; paredes, janela e porta ficam) e entram as do DCE do Térreo aprovado da Casa D, nos
    retângulos do PDF: a cama de solteiro (girada, cabeceira na parede da direita, como o travesseiro
    do PDF) e o criado-mudo, com sombra curta, e o armário até o teto em areia com veio, sem sombra de
    móvel baixo e com contorno fino.
11. WC DCE 1: o motor pôs um segundo vaso no alto, onde o PDF tem o chuveiro. O vaso sai (Bege Bahia
    tecido do próprio WC, na luz do piso em volta; a linha do box fica) e entra o chuveiro do PDF como
    o do WC DCE da Casa D (ducha quadrada com a placa da Casa A, braço cromado até a parede da direita
    e canopla, com sombra curta).
12. Arcos das portas sobre o granito (pedido do usuário): como nas Casas C e D, em cinza e traço fino.
    O motor quase não os fez (só o do DCE, apagado e escuro); o arco escuro que houver sai (granito
    tecido, só no granito da base chapada) e entra o arco cinza fino das curvas do PDF (ARQ_PAREDE).
13. Pontos claros do granito (pedido do usuário: muitos, espalhados; tirar alguns): os pontinhos
    claros de 2 a 16 px que o motor salpicou no Marrom Tabaco saem onde se destacam (30 ou mais acima
    do granito em volta); ficam os mais fracos e o grão fino. Cada um vira o granito de um trecho
    vizinho sem ponto, colado com borda suave.
14. Pilar à direita do lavabo (pedido do usuário): o retângulo cinza da ARQ_ELEMENTOS FIXOS, que o
    motor fez como uma peça cinza-taupe com folhas por cima, é um pilar: fica no preto das paredes,
    na geometria do PDF (alto, cobre as folhas).
15. Lavabo (pedido do usuário): cuba esculpida, com a torneira vindo do lado esquerdo. A cuba branca e
    a torneira preta que o motor pôs no meio da bancada saem (quartzo tecido da própria bancada, na luz
    dela); na metade esquerda da bancada do PDF entra a cuba esculpida no próprio quartzo: o fundo
    inclinado escurece para trás, onde fica a fenda do ralo, as bordas de cima e da direita fazem uma
    sombra curta para dentro, e um traço fino marca a borda. A torneira do PDF sai da parede da
    esquerda: canopla e bica cromadas, com brilho e sombra curta.
16. Escritório (pedido do usuário): atrás do sofá é um arranjo de flores (o círculo do PDF, ARQ_LAYOUT
    HUMANIZAÇÃO); o motor fez uma bola verde. Entra o arranjo com a estrelítzia do próprio jardim do
    render (folhas em leque e as flores laranja, as mesmas do paisagismo), reduzida ao círculo do
    PDF, com borda suave e sombra curta.
17. Louceiro (pedido do usuário): veios aparentes de marcenaria. O motor deixou a madeira lisa; o veio
    vem do tampo da mesa de jantar do próprio render (veio no comprido), girado para correr no
    comprimento do louceiro e realçado, como no mobiliário do DCE da Casa D; o tom e as bordas ficam.
18. Escada interna (pedido do usuário): só sombreamento que denota a subida, da direita para a
    esquerda, sem linhas. O travertino da escada é refeito sem os tracejados dos degraus, a linha de
    corte e a diagonal (as mesmas colunas do travertino limpo abaixo da floreira, veios verticais); os
    19 pisos do PDF (9,33 px) clareiam para cima (a escada sobe da direita para a esquerda: o de baixo,
    à direita, é o mais escuro) e cada espelho joga uma sombra curta no piso de baixo, à direita dele,
    inclusive o primeiro, no piso da sala.
19. Jardim de inverno (pedido do usuário): as plantas saem levemente da floreira, sem exagero: nunca
    por cima da escada (a borda de cima fica), um pouco para os lados (até ~3 px) e um pouco mais para
    baixo (até ~6 px), com a borda das folhas irregular; as folhas voltam do render original, por
    cima do traço da floreira, com uma sombra curta desenhada no travertino. Entram poucas flores tropicais coloridas (as estrelítzias
    do jardim do render, laranja, e as mesmas em vermelho, rosa e amarelo), espalhadas.
20. Estar da varanda (pedido do usuário): ali não tem tapete. O tapete retangular que o motor pôs sob
    o sofá, as poltronas, a mesa de centro e o banco sai: vira o Bege Bahia tecido da própria varanda,
    na luz do piso em volta; os móveis (os polígonos brancos do PDF, com folga) ficam, e cada um ganha
    de volta a sombra curta no piso.
21. Escada externa do alto (pedido do usuário): sem linhas, com sombreamento que dá a percepção de
    descida da direita para a esquerda. Como a interna (item 18), com o lado de baixo à esquerda: o
    travertino refeito sem as linhas, os 17 pisos do PDF escurecendo para a esquerda e a sombra curta de
    cada espelho no piso de baixo, à esquerda dele, inclusive o último, no deck.
22. Vaso do banho gourmet (pedido do usuário: com tampo): o motor deixou o símbolo do CAD (caixa com
    parafusos e a bacia pontilhada). Ele sai (granito tecido) e o vaso é desenhado em 8 x no polígono
    do PDF, como os do Subsolo da Casa D, na escala deste render: louça com volume, contorno fino,
    sombra curta no piso e o tampo fechado, da linha da dobradiça (junto à caixa, na parede de cima)
    à frente, recuado da borda, com volume, contorno e sombra leve.
23. Banho gourmet (pedido do usuário): faltava a bancada da pia e a torneira. A bancada do PDF
    (ARQ_BANCADAS, encostada na parede de baixo) é em granito marrom, como o piso: entra pelo contorno
    cinza fino (o dos arcos sobre o granito), com o tampo um pouco mais claro (polido) e sombra curta no
    piso; no painel do meio, a cuba esculpida no próprio granito (como a do lavabo, com a fenda escura)
    e, saindo do painel da esquerda, a torneira cromada do PDF (base redonda e bica até a cuba).
24. Porta do hall externo (pedido do usuário): faltavam a extensão e o arco. A porta do PDF tem duas
    folhas: a grande (que o render fez, com o arco para baixo) e a pequena, à direita, que abre para
    cima; a folha pequena entra na espessura do PDF, no desenho da grande (traço escuro em cima, traço
    médio embaixo, miolo claro), com o encontro das duas marcado, e o arco dela no traço fino dos arcos.
25. Brises da janela do escritório (pedido do usuário: em tons de madeira, do lado de fora): os 8
    retângulos da ARQ_ELEMENTOS FIXOS junto à janela, que o motor apagou na grama, entram como réguas
    de madeira (o veio da mesa de jantar do render, no comprido de cada régua), cada uma num tom um
    pouco diferente, com contorno fino e sombra curta na grama.
26. Carros (pedido do usuário: não precisam estar 100% alinhados): cada carro é recortado (a silhueta
    do render), o granito volta no lugar dele e da sombra (tecido do próprio granito, na luz em volta)
    e o carro volta com um deslocamento e um giro leves, diferentes para cada um, com a sombra curta
    desenhada de novo.
27. Adega (pedido do usuário): prateleira de vinhos em U, não um armário em U. No polígono do PDF
    (ARQ_LAYOUT HUMANIZAÇÃO), a madeira lisa do motor ganha o veio (o da mesa de jantar, no comprido de
    cada braço) e as garrafas deitadas em fileiras, com o gargalo para a parede de cada braço: vidro
    verde-escuro, âmbar e vinho alternados, com o brilho no comprido e sombra curta na madeira.
28. Área de serviço (pedido do usuário): a faixa junto à parede de baixo é em parte armário e em parte
    bancada para roupas; o motor fez tudo em madeira lisa. No PDF, à esquerda, o armário (ARQ_LAYOUT
    HUMANIZAÇÃO) fica em marcenaria areia com o veio (como o louceiro); à direita, a bancada
    (ARQ_BANCADAS) vira o quartzo do tanque (tecido dos trechos limpos da bancada dele, no tom dela),
    com a luz do próprio trecho; contorno fino nas duas peças e entre elas.
29. Cozinha, fileira junto à parede de baixo (pedido do usuário): ao centro, dois eletrodomésticos (ou
    a geladeira) em inox; nas laterais, armários. Os dois quadrados do centro (ARQ_LAYOUT HUMANIZAÇÃO)
    recebem os eletrodomésticos em inox da cozinha aprovada da Casa D (cada um, uma metade do par de
    lá); os dois trechos dos lados viram armários em marcenaria areia com o veio do louceiro (sem
    sombra de móvel baixo); contorno fino em todas as peças.
30. Spa (pedido do usuário): mais um degrau na parte de dentro, formando um quadrado. No PDF o spa tem
    dois contornos internos (o degrau, em volta, e o fundo); o render só tinha o do fundo. Entra o
    contorno de fora do degrau (ARQ_PAREDE, 4,3 px para fora do fundo), como na Casa D: com o perfil de
    luz das arestas do próprio render (medido na aresta do fundo, lado a lado: sombra larga em cima e
    à direita, traço fino à esquerda e embaixo), um pouco mais suave.
31. Piscina, lado esquerdo (pedido do usuário): são duas folhas de vidro. As duas faixas brancas que
    o motor fez ficam como as folhas do PDF (ARQ_PAREDE, 2,8 px cada, com o vão de água entre elas),
    no desenho dos vidros finos da Casa D: vidro claro com a linha central fina e o contorno fino.
32. Paisagismo logo abaixo das escadas (pedido do usuário): o bolsão de grama entre as pedras, os
    degraus e o banco de bronze ganha um canteiro, como os da Casa D: um trecho das costelas-de-adão do
    próprio render (o canto do lote), espelhado, com o contorno orgânico onde o trecho corta a touceira,
    só sobre a grama (as pedras e o banco ficam), emendando nas plantas que já existem embaixo.
33. Garagem, lateral direita (pedido do usuário): faltavam os brises. Os 8 retângulos da ARQ_ELEMENTOS
    FIXOS sobre o granito, acima do trecho de parede, entram no mesmo desenho dos brises do escritório
    (réguas de madeira em tons variados, contorno fino e sombra curta).
34. Banco do estar da varanda (pedido do usuário): banco de madeira sem encosto. O encosto de madeira
    que o motor pôs embaixo do banco sai (Bege Bahia tecido da varanda, com a sombra dele); o banco, no
    retângulo do PDF, vira um tampo de madeira (a da mesa de jantar do render, com o veio no comprido)
    em ripas, com juntas finas, contorno fino e sombra curta, sem as almofadas.
35. Piscinas (pedido do usuário, com a legenda do cliente): revestimento Barlavento (Portobello, a pedra
    hijau, peças de 14,5 x 14,5 cm, tom Caribbean). A água turquesa saturada do motor, com a rede de
    reflexos brancos marcada, vira a pedra das peças (gerada por código: tons verde-acinzentados e
    azulados alternados, grão fino, juntas finas) sob uma água verde-azulada clara, com a luz chapada
    (sem as manchas escuras de sombra, que davam aspecto de sujo: pedido do usuário), só uma sombra
    curta e leve junto às bordas e o degrau da prainha marcado de leve. Efeitos da água (pedido do
    usuário: sem eles parecia vazia): a grade das peças ondulada pela refração, a rede de cáusticas
    do próprio render mais suave (só clareia) e um brilho difuso na diagonal. Na piscina, na prainha e
    no spa (a mancha da água na base chapada); o degrau do spa é desenhado depois (item 30).
36. Nomes e áreas dos ambientes, na imagem final (`salvar_final`).

Regras de 19 e 20/10 (POE642_REGRAS.md), um item por vez, depois do retocado aprovado (itens 1 a 35). A
imagem final passa a ser alinhada no aprovado: um item novo não muda o afim, e o resto fica igual, px a px.
37. Box do banho gourmet (R5: "representar o boxe no banho gourmet, pois não está representado"): no PDF
    é de correr, com duas folhas (a fixa, junto à parede de baixo, e a de correr, por dentro); o vão fica
    em cima. O traço escuro do motor, de parede a parede, sai; as folhas entram como no box da
    referência: linha clara de vidro, sem montantes, borda cinza do lado do chuveiro e sombra suave.
38. Portas sem os arcos (R3: "Não mostrar arco da porta"). No granito, os arcos eram o cinza fino do item
    12 (e o da folha pequena do hall, item 24), desenhados pelo próprio script: deixam de ser desenhados; o
    arco escuro do motor (DCE) segue saindo. No travertino e no Bege Bahia, os arcos do motor saem pelo
    `arcos.remover_arcos`, só nos arcos fora do granito, com o tracejado do PDF que os cruza protegido.
39. Escadas com linhas e o triângulo de orientação (R14), como no Subsolo: o sombreamento dos itens 18 e 21
    sai (fica o travertino limpo) e entram, na geometria do PDF, o bocel em linha suave e a sombra curta no
    degrau de baixo; na interna (sobe da direita para a esquerda), depois do corte, a escada esmaecida e
    tracejada; o triângulo no início de cada uma, apontando para o percurso. A externa do alto desce da
    esquerda para a direita (usuário: "pode inverter"; fica sobre a do Subsolo, que sobe da direita para a
    esquerda), contra o "D" do PDF; o triângulo dela fica à esquerda.
40. Rótulos (R6 e R7): no granito Marrom Tabaco, em branco (antes, cinza 150); nenhum sobre objeto (conferidos os
    29; o do louceiro fica sobre a marcenaria, que é o próprio ambiente, sem piso livre).
41. Carros (R12): alinhados, do mesmo tamanho e da mesma cor. Com `R12_CARROS`, o item 26 apaga os três
    carros como antes e põe, no centro de cada carro do PDF, o carro prata do render (o do meio) levado a
    4,70 x 1,85 m (carroceria, sem os retrovisores), sem giro, com a sombra curta.
42. Grama (R1, R4): o grão de carpete do motor vira o desenho da grama da referência, na escala, com a luz larga
    do lugar e as sombras das plantas, no tom verde do render (escolha do usuário, opção B). Plantas e pisos ficam.
43. Bege Bahia (R1): como no Subsolo, os pontinhos escuros do motor saem e o desenho da biblioteca entra, na escala,
    no tom da foto de referência, com a luz do lugar (varanda, deck, blocos, pisantes e WC DCE 1).
44. Projeções da cobertura (R8, R9; esquema aprovado pelo usuário, com os pilares da varanda dentro do L):
    tracejado cinza fino no L da laje baixa do espaço gourmet + varanda, na laje da garagem (com a linha do PDF e a
    lateral junto aos brises) e na faixa de cima, as bordas das 7 notas "PROJ. COBERTURA" do PDF; menos nas paredes
    pretas.
45. Soleiras e vidros conferidos com o PDF (R13): sem mudança.
46. Cortinas de linho (pente fino de 20/10, item 1), com o bloco da biblioteca (`_blocos/blocos.py`): o trilho de
    parede a parede, do lado do vidro, e o pano por dentro (usuário: "trilhos da cortina tem que ser de fora a fora.
    somente a cortina pode estar a meia distancia, totalmente recolhida ou totalmente fechada"). Escritório: os tracinhos
    brancos do motor saem e os dois panos ficam nos trechos do PDF (a meia distância). Living, vidro da varanda (pedido do
    usuário, "Representar a cortina"; o PDF não traz): o trilho por dentro das quatro folhas escalonadas, da parede até a
    fachada de baixo, e o pano fechado no vão todo.
    Living, fachada de baixo (item 2 do pente fino: "corrija as cortinas aqui também"): o zigue-zague cinza e os tracinhos
    do motor saem; o trilho vai do trilho do vidro da varanda (fecha o L no canto) até a parede da direita, logo acima
    das quatro folhas escalonadas, e os dois panos ficam nos trechos do PDF (ARQ_MOBILIÁRIO), a meia distância.

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/retoque_terreo_casae.py POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_render.webp \
      --saida POE642_CasaE/renders --nome POE642_CasaE_PH_Terreo_v1_retocado
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))

from retoque_terreo_casad import desenhar_chuveiro, interpolar, textura  # noqa: E402
from retoque_subsolo_casad import apagar_largo  # noqa: E402
from retoque_terreo_casac import CROMO, CROMO_CLARO, CROMO_ESCURO  # noqa: E402
from retoque_terreo_casab import LOUCA, LOUCA_CONTORNO  # noqa: E402
from fontes_procedurais import barlavento  # noqa: E402

SS = 8                             # superamostragem dos traços desenhados
BASE = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - TÉRREO - CASA E.pdf"
CONFIG = RAIZ / "POE642_CasaE/config_bases.json"
# o retocado aprovado (itens 1 a 35, 15/10/26): a imagem final é alinhada nele, e os itens das regras novas,
# inclusive os que mudam itens antigos (R3, item 12), não mexem no afim
APROVADO = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado_aprovado.png"


def alinhar_base(render):
    """Base 16:9 reduzida ao tamanho do render e levada a ele por SIFT + afim (como nas outras casas)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    al = cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    return A, al


def pdf_cadeia(A, forma_render):
    """Página do PDF e as conversões PDF -> render e render -> PDF pela mesma cadeia da base (recorte,
    largura da base, tela 16:9, redução ao tamanho do render e o afim A)."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Terreo"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sx, sy = forma_render[1] / wt, forma_render[0] / ht
    Ai = np.linalg.inv(np.vstack([A, [0, 0, 1]]))

    def p2r(x, y):
        bx, by = ((x - clip.x0) * zoom + (wt - wb) // 2) * sx, ((y - clip.y0) * zoom + (ht - hb) // 2) * sy
        return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]

    def r2p(x, y):
        bx, by, _ = Ai @ [x, y, 1]
        return (bx / sx - (wt - wb) // 2) / zoom + clip.x0, (by / sy - (ht - hb) // 2) / zoom + clip.y0

    return pg, p2r, r2p


def caixa_render(d, p2r):
    """Caixa (x0, y0, x1, y1) de um desenho do PDF no quadro do render."""
    (x0, y0), (x1, y1) = p2r(d["rect"].x0, d["rect"].y0), p2r(d["rect"].x1, d["rect"].y1)
    return x0, y0, x1, y1


def mascara_pdf(janela, A, forma_render, filtro):
    """Máscara (0..1, no quadro do render) dos desenhos do PDF escolhidos por filtro(d), preenchidos,
    levados ao render pela mesma cadeia da base. Os desenhos são refeitos numa página nova (o MuPDF
    não desliga as layers deste PDF no raster) e rasterizados em alta resolução."""
    pg, p2r, r2p = pdf_cadeia(A, forma_render)
    nova = pymupdf.open()
    pn = nova.new_page(width=pg.rect.width, height=pg.rect.height)
    sh = pn.new_shape()
    for d in pg.get_drawings():
        if not filtro(d):
            continue
        for it in d["items"]:
            if it[0] == "l":
                sh.draw_line(it[1], it[2])
            elif it[0] == "c":
                sh.draw_bezier(it[1], it[2], it[3], it[4])
            elif it[0] == "re":
                sh.draw_rect(it[1])
            elif it[0] == "qu":
                sh.draw_quad(it[1])
        sh.finish(fill=(0, 0, 0), color=None, closePath=d.get("closePath", True), even_odd=d.get("even_odd", False))
    sh.commit()
    x0, y0, x1, y1 = janela
    a, b = r2p(x0 - 2, y0 - 2), r2p(x1 + 2, y1 + 2)
    ret = pymupdf.Rect(a[0], a[1], b[0], b[1])
    zp = 60
    pix = pn.get_pixmap(clip=ret, matrix=pymupdf.Matrix(zp, zp), alpha=False, colorspace=pymupdf.csGRAY)
    img = 255 - np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    src = [(0, 0), (pix.width, 0), (0, pix.height)]
    dst = [(p2r(ret.x0 + u / zp, ret.y0 + v / zp)[0] - x0, p2r(ret.x0 + u / zp, ret.y0 + v / zp)[1] - y0) for u, v in src]
    M = cv2.getAffineTransform(np.float32(src), np.float32(dst))
    return cv2.warpAffine(np.ascontiguousarray(img).astype(np.float32) / 255, M, (x1 - x0, y1 - y0),
                          flags=cv2.INTER_AREA, borderValue=0)


# lote no quadro do render: o gramado vai de x = 141 a 1798; o muro de cima ocupa as linhas 0 a 5
# (de 142 a 1798) e o de baixo as linhas 932 a 937 (de 141 a 1851, até a linha tracejada da direita).
# Fora: x < 141, x >= 1799 acima do muro de baixo (a faixa entre o gramado e a linha tracejada da
# direita, onde o motor pôs o Bege Bahia), e tudo abaixo do muro de baixo
LOTE = {
    "x_esq": 141, "x_dir": 1799, "x_muro_baixo": 1852,
    "muro_cima": (0, 6), "muro_baixo": (932, 938),
    # trecho limpo (sem folhas) de onde sai a mediana de cada linha do muro
    "limpo_cima": (450, 1450), "limpo_baixo": (450, 1300),
}


def lote(out, base):
    q = LOTE
    xe, xd, xb = q["x_esq"], q["x_dir"], q["x_muro_baixo"]
    (c0, c1), (b0, b1) = q["muro_cima"], q["muro_baixo"]
    a, b = q["limpo_cima"]
    out[c0:c1, xe:xd] = np.median(out[c0:c1, a:b], axis=1).astype(np.uint8)[:, None]
    a, b = q["limpo_baixo"]
    out[b0:b1, xe:xb] = np.median(out[b0:b1, a:b], axis=1).astype(np.uint8)[:, None]
    fora = np.zeros(out.shape[:2], bool)
    fora[:, :xe] = True
    fora[:b0, xd:] = True
    fora[b0:b1, xb:] = True
    fora[b1:, :] = True
    out[fora] = base[fora]
    print(f"    muros de cima e de baixo sem as folhas; fora do lote: base ({int(fora.sum())} px)")
    return out


# jardim interno (item 3): a floreira do PDF no quadro do render (a borda escura da terra no render
# cai nela), a escada logo acima (degraus tracejados verticais de 497 a 542, com a linha horizontal
# em 523, e a diagonal de (1079, 498) a (1094, 527), que no PDF vai até a floreira)
JARDIM = {
    "floreira": (977, 543, 1155, 582), "janela": (950, 490, 1185, 615),
    # a fonte da escada fica abaixo da sombra do louceiro (497 a 499) e acima da linha horizontal;
    # deslocamentos (dy, dx): primeiro só na vertical (o tracejado repete a cada ~6,5 px), depois
    # também de dois degraus (~18,6 px) para os lados, onde a diagonal ocupa a fonte
    "escada": (977, 497, 1155, 543), "fonte_escada": (500, 523),
    "desloc_escada": [(dy, 0) for dy in (13, 26, 20, 7, 14, 19)] + [(dy, dx) for dy in (13, 7, 20) for dx in (-19, 19, -28, 28)],
    "desloc_trav": (64, 80, 96, 112),
    "diagonal": ((1079, 498), (1094, 527)), "diag_fim_y": 543, "cor_diag": (128, 142, 158),
    # plantas: verdes ou escuras; sombra: mais escura que o travertino limpo da mesma coluna (veios
    # verticais), perto das plantas e fora da escada
    "verde": 2, "escuro": 110, "ref_trav": (620, 680), "sombra": 7, "alcance_sombra": 12,
    "borda": {"cor": (78, 80, 80), "larg": 0.9, "forca": 0.85},
}


def linha_aa(forma, pts, larg, fechada=False):
    """Máscara (0 a 1) de uma polilinha, desenhada em SS x e reduzida."""
    h, w = forma
    m = np.zeros((h * SS, w * SS), np.uint8)
    p = np.int32(np.round(np.float64(pts) * SS))
    cv2.polylines(m, [p], fechada, 255, max(1, int(round(larg * SS))), cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def jardim_interno(out):
    q = JARDIM
    fx0, fy0, fx1, fy1 = q["floreira"]
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = out[wy0:wy1, wx0:wx1].astype(int)
    lum = reg.mean(axis=2)
    planta = (reg[..., 1] > reg[..., 2] + q["verde"]) | (lum < q["escuro"])
    dentro = np.zeros(lum.shape, bool)
    dentro[fy0 - wy0:fy1 - wy0, fx0 - wx0:fx1 - wx0] = True
    sx0, sy0, sx1, sy1 = q["escada"]
    escada = np.zeros(lum.shape, bool)
    escada[sy0 - wy0:sy1 - wy0, sx0 - wx0:sx1 - wx0] = True
    # a mancha das plantas (ligada à floreira) e a sombra delas no travertino, em volta
    n, lab = cv2.connectedComponents(planta.astype(np.uint8))
    ligada = np.isin(lab, np.unique(lab[dentro & planta])) & (lab > 0)
    r0, r1 = q["ref_trav"]
    ref = np.median(out[r0:r1, wx0:wx1].astype(np.float32).mean(axis=2), axis=0)[None, :]
    k = 2 * q["alcance_sombra"] + 1
    perto = cv2.dilate(ligada.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    m = cv2.dilate(ligada.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    m |= perto & (lum < ref - q["sombra"]) & ~escada
    m |= perto & planta                                  # pontas soltas de folha
    # na escada, o halo claro em volta das folhas também sai (a fonte é a própria escada, limpa)
    m |= escada & (cv2.dilate(ligada.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
    m &= ~dentro
    f0, f1 = q["fonte_escada"]
    m[:f1 + 1 - wy0] &= ~escada[:f1 + 1 - wy0]          # as plantas não sobem acima da linha horizontal
    # escada: a mesma coluna, alguns degraus de tracejado acima (sem a diagonal e sem as plantas);
    # travertino: a mesma coluna, mais abaixo, onde não há planta nem sombra
    (dx0, dy0), (dx1, dy1) = q["diagonal"]
    incl = (dx1 - dx0) / (dy1 - dy0)
    ys, xs = np.mgrid[wy0:wy1, wx0:wx1]
    na_diag = np.abs(xs - (dx0 + (ys - dy0) * incl)) < 5
    orig = out.copy()
    n_esc = n_trav = 0
    for y, x in zip(*np.nonzero(m)):
        Y, X = y + wy0, x + wx0
        if escada[y, x]:
            for dy, dx in q["desloc_escada"]:
                fy, fx = Y - dy, X + dx
                if f0 <= fy < f1 and sx0 <= fx < sx1 and not na_diag[fy - wy0, fx - wx0] and not m[fy - wy0, fx - wx0]:
                    out[Y, X] = orig[fy, fx]
                    n_esc += 1
                    break
        else:
            for d in q["desloc_trav"]:
                fy = Y + d
                if fy >= wy1 or not m[fy - wy0, x]:
                    out[Y, X] = orig[fy, X]
                    n_trav += 1
                    break
    # a diagonal segue da linha horizontal até a floreira
    a = linha_aa(out.shape[:2], [(dx0 + (f1 + 0.5 - dy0) * incl, f1 + 0.5),
                                 (dx0 + (q["diag_fim_y"] - dy0) * incl, q["diag_fim_y"])], 1.0)[..., None] * 0.8
    out[:] = np.clip(out * (1 - a) + np.float32(q["cor_diag"]) * a, 0, 255).astype(np.uint8)
    # borda da floreira
    b = q["borda"]
    a = linha_aa(out.shape[:2], [(fx0 + 0.5, fy0 + 0.5), (fx1 - 0.5, fy0 + 0.5), (fx1 - 0.5, fy1 - 0.5),
                                 (fx0 + 0.5, fy1 - 0.5)], b["larg"], fechada=True)[..., None] * b["forca"]
    out[:] = np.clip(out * (1 - a) + np.float32(b["cor"]) * a, 0, 255).astype(np.uint8)
    print(f"    plantas fora da floreira: {n_esc} px de escada e {n_trav} px de travertino refeitos; diagonal e borda")
    return out


# tapete do estar da varanda (item 4): o redondo do render é uma elipse; o do PDF, o polígono branco
# da ARQ_MOBILIÁRIO com esta caixa no quadro do render
TAPETE = {
    "janela": (826, 652, 986, 806),
    "pdf": (839.7, 668.0, 965.6, 796.9),
    "velho": ((904.5, 732.0), (60.5, 65.0)),
    "fonte_tapete": [(915, 677, 937, 695), (930, 738, 950, 748), (940, 700, 952, 725)],
    "fonte_travertino": (622, 664),          # linhas limpas acima do tapete (as mesmas colunas)
    # móveis: os polígonos brancos do PDF em volta (sofá, poltronas, mesas, aparador, mesinhas e
    # vasos), com 2 px de folga, e os traços escuros do render junto deles
    "camadas_moveis": ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO", "DOC_TEXTOS"), "escuro": 150,
    "borda": 0.95,
}


def tapete(out, A):
    q = TAPETE
    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    novo = mascara_pdf(q["janela"], A, out.shape, lambda d: d.get("fill") == (1.0, 1.0, 1.0) and
                       d.get("layer") == "ARQ_MOBILIÁRIO" and
                       max(abs(u - v) for u, v in zip(caixa_render(d, p2r), q["pdf"])) <= 1.5)
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    Y = cv2.GaussianBlur(reg.mean(axis=2), (0, 0), 0.8)
    yy, xx = np.mgrid[wy0:wy1, wx0:wx1].astype(np.float32) + 0.5
    (cx, cy), (ax, ay) = q["velho"]
    velho = ((xx - cx) / ax) ** 2 + ((yy - cy) / ay) ** 2 <= 1.0
    def movel(d):
        c = caixa_render(d, p2r)
        return (d.get("fill") == (1.0, 1.0, 1.0) and d.get("layer") in q["camadas_moveis"] and
                max(abs(u - v) for u, v in zip(c, q["pdf"])) > 1.5 and
                c[2] > wx0 and c[0] < wx1 and c[3] > wy0 and c[1] < wy1)

    pecas = cv2.dilate((mascara_pdf(q["janela"], A, out.shape, movel) > 0.3).astype(np.uint8), np.ones((5, 5), np.uint8))
    pecas = (pecas > 0) | (cv2.dilate(pecas, np.ones((5, 5), np.uint8)) > 0) & (Y < q["escuro"])
    sai = velho & (novo < 0.5) & ~pecas
    entra = ~velho & (novo > 0.0) & ~pecas
    # travertino: as mesmas colunas da faixa limpa acima, repetida em espelho na vertical, na luz do
    # travertino em volta; a sombra dos móveis no tapete passa para o travertino (só escurece)
    f0, f1 = q["fonte_travertino"]
    faixa = out[f0:f1, wx0:wx1].astype(np.float32)
    n = f1 - f0
    idx = np.arange(h) % (2 * n)
    trav = faixa[np.where(idx < n, idx, 2 * n - 1 - idx)]
    limpo = ~velho & ~pecas & (novo < 0.01) & (Y > 195)
    luz = interpolar(cv2.GaussianBlur(Y, (0, 0), 1.0) / np.maximum(cv2.GaussianBlur(trav.mean(axis=2), (0, 0), 1.0), 1),
                     limpo, 2.0)
    tap_med = np.median(Y[velho & ~pecas & (novo > 0.5)])
    sombra = np.clip(cv2.GaussianBlur(Y, (0, 0), 1.5) / tap_med, 0.7, 1.0)
    trav = trav * (luz * sombra)[..., None]
    cor = np.median(np.concatenate([out[b:d, a:c].reshape(-1, 3) for a, b, c, d in q["fonte_tapete"]]).astype(np.float32), axis=0)
    tap = textura(out, q["fonte_tapete"], h, w, p=8) * cor
    a_sai = (np.clip(1 - novo, 0, 1) * (cv2.dilate(sai.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) * ~pecas)[..., None]
    reg = reg * (1 - a_sai) + trav * a_sai
    a_ent = (novo * entra)[..., None]
    reg = reg * (1 - a_ent) + tap * a_ent
    borda = np.clip(cv2.dilate(novo, np.ones((3, 3), np.uint8)) - novo, 0, 1) * ~pecas
    reg *= (1 - (1 - q["borda"]) * borda)[..., None]
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    tapete no contorno orgânico do PDF ({int(sai.sum())} px saem, {int(entra.sum())} px entram)")
    return out


# barras a 45° da varanda (item 5): os quadradinhos brancos da ARQ_ELEMENTOS FIXOS nesta janela
BARRAS = {
    "janela": (618, 643, 658, 770),
    "cor": (148, 150, 153), "volume": 0.06,        # cinza da base; mais claro na face de cima
    "contorno": (70, 72, 74), "larg_contorno": 0.5, "traco_pdf": 0.6,
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35},
}


def poligono_aa(forma, pts):
    """Máscara (0 a 1) de um polígono preenchido, desenhado em SS x e reduzido."""
    h, w = forma
    m = np.zeros((h * SS, w * SS), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round(np.float64(pts) * SS))], 255, cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def barras(out, A):
    q = BARRAS
    wx0, wy0, wx1, wy1 = q["janela"]
    pg, p2r, _ = pdf_cadeia(A, out.shape)

    def dentro(d):
        x0, y0, x1, y1 = caixa_render(d, p2r)
        return wx0 < x0 and x1 < wx1 and wy0 < y0 and y1 < wy1

    m = mascara_pdf(q["janela"], A, out.shape, lambda d: d.get("layer") == "ARQ_ELEMENTOS FIXOS" and
                    d["type"] == "f" and d.get("fill") == (1.0, 1.0, 1.0) and dentro(d))
    n, lab = cv2.connectedComponents((m > 0.5).astype(np.uint8))
    forma = out.shape[:2]
    s = q["sombra"]
    # cada barra: o retângulo girado da mancha; a largura vem da área (o retângulo dos centros dos px
    # fica fino demais), mais o traço do contorno do PDF (0,57 pt), e é a mediana das quatro
    rets = []
    for i in range(1, n):
        ys, xs = np.nonzero(lab == i)
        (cx, cy), (a, b), ang = cv2.minAreaRect(np.float32(np.c_[xs + wx0 + 0.5, ys + wy0 + 0.5]))
        comp = max(a, b) + 1
        rets.append(((cx, cy), comp, float(m[lab == i].sum()) / comp + q["traco_pdf"], ang, a >= b))
    larg = float(np.median([r[2] for r in rets]))
    for i, ((cx, cy), comp, _, ang, deitado) in enumerate(rets, 1):
        a, b = (comp, larg) if deitado else (larg, comp)
        cantos = cv2.boxPoints(((cx, cy), (a, b), ang))
        # sombra curta no piso (só escurece)
        sombra = cv2.GaussianBlur(poligono_aa(forma, cantos + np.float32(s["desloc"])), (0, 0), s["sigma"])
        out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
        # a barra: cinza com a face de cima um pouco mais clara (gradiente na largura)
        al = poligono_aa(forma, cantos)
        yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
        u = np.float32([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
        lado = u if a < b else np.float32([-u[1], u[0]])      # direção da largura
        t = np.clip(((xx - cx) * lado[0] + (yy - cy) * lado[1]) / max(min(a, b) / 2, 0.5), -1, 1)
        t *= -np.sign(lado[1] + 1e-6)                           # +1 na face de cima
        cor = np.float32(q["cor"])[None, None, :] * (1 + q["volume"] * t)[..., None]
        out[:] = np.clip(out * (1 - al[..., None]) + cor * al[..., None], 0, 255).astype(np.uint8)
        c = linha_aa(forma, cantos, q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - c) + np.float32(q["contorno"]) * c, 0, 255).astype(np.uint8)
        print(f"    barra {i}: centro ({cx:.1f}, {cy:.1f}), {max(a, b):.1f} x {min(a, b):.1f} px, {ang:.0f}°")
    return out


# elevador (item 6): o vão da caixa entre as paredes (no quadro do render) e a cabine do Subsolo da
# Casa B aprovado, a mesma das Casas C e D; lá a porta já fica embaixo, como aqui (sem girar)
ELEVADOR = {
    "interior": (1018, 370, 1067, 415),
    "cabine": (1020, 372, 1066, 414),          # ocupa a caixa, com 1-2 px de folga (como na Casa D)
    "branco": (255, 255, 255),
    "fonte": (RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final.png", (3116, 1011, 3276, 1162)),
}


def elevador(out):
    q = ELEVADOR
    x0, y0, x1, y1 = q["interior"]
    out[y0:y1, x0:x1] = q["branco"]
    arq, (fx0, fy0, fx1, fy1) = q["fonte"]
    cabine = cv2.imread(str(arq))[fy0:fy1, fx0:fx1]
    cx0, cy0, cx1, cy1 = q["cabine"]
    out[cy0:cy1, cx0:cx1] = cv2.resize(cabine, (cx1 - cx0, cy1 - cy0), interpolation=cv2.INTER_AREA)
    print(f"    elevador: caixa branca e a cabine do Subsolo da Casa B ({cx1 - cx0}x{cy1 - cy0} px)")
    return out


# vaso inventado no CPD (item 7): a caixa do vaso e da sombra dele (a parede da direita começa em
# x = 1290) e trechos limpos do granito do CPD (à direita da folha da porta, que fica em x ~1245)
VASO_CPD = {
    "janela": (1240, 368, 1290, 418), "vaso": (1259, 391, 1290, 414),
    "fontes": [(1249, 372, 1286, 390), (1249, 391, 1258, 417)],
}


def vaso_cpd(out):
    q = VASO_CPD
    wx0, wy0, wx1, wy1 = q["janela"]
    vx0, vy0, vx1, vy1 = q["vaso"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    m[vy0 - wy0:vy1 - wy0, vx0 - wx0:vx1 - wx0] = True
    out = apagar_largo(out, q["janela"], m, q["fontes"], sigma=3.0, lum_min=40, escuros=True)
    print(f"    vaso do CPD: {int(m.sum())} px de granito tecido")
    return out


# máquinas da área de serviço (item 8): o bloco de madeira do render, os dois quadrados do PDF e as
# máquinas em inox do Térreo retocado da Casa D (o par fica em x 1143-1190, y 191-216; a divisória
# em 1166)
MAQUINAS = {
    "bloco": (1078, 289, 1128, 317), "janela": (1010, 289, 1150, 345),
    "fontes_granito": [(1032, 318, 1115, 334), (1130, 300, 1148, 340)],
    "quadrados": [(1079.8, 291.6, 1101.5, 313.4), (1103.3, 291.6, 1125.0, 313.4)],
    "fonte": (RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png",
              [(1143, 191, 1166, 216), (1167, 191, 1190, 216)]),
    "contorno": (70, 70, 72), "larg_contorno": 0.4,
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35},
}


def maquinas(out):
    q = MAQUINAS
    wx0, wy0, wx1, wy1 = q["janela"]
    bx0, by0, bx1, by1 = q["bloco"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    m[by0 - wy0:by1 - wy0, bx0 - wx0:bx1 - wx0] = True
    # a parede de cima (preta) fica
    m &= out[wy0:wy1, wx0:wx1].mean(axis=2) > 35
    out = apagar_largo(out, q["janela"], m, q["fontes_granito"], sigma=3.0, lum_min=40, escuros=False)
    arq, fontes = q["fonte"]
    casad = cv2.imread(str(arq))
    forma = out.shape[:2]
    s = q["sombra"]
    for (x0, y0, x1, y1), (fx0, fy0, fx1, fy1) in zip(q["quadrados"], fontes):
        cantos = np.float32([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        sombra = cv2.GaussianBlur(poligono_aa(forma, cantos + np.float32(s["desloc"])), (0, 0), s["sigma"])
        out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
        # a máquina de lá, levada ao quadrado do PDF (subpixel, por afim)
        maq = casad[fy0:fy1, fx0:fx1].astype(np.float32)
        M = cv2.getAffineTransform(np.float32([(0, 0), (fx1 - fx0, 0), (0, fy1 - fy0)]),
                                   np.float32([(x0, y0), (x1, y0), (x0, y1)]))
        img = cv2.warpAffine(maq, M, forma[::-1], flags=cv2.INTER_AREA)
        al = poligono_aa(forma, cantos)[..., None]
        out[:] = np.clip(out * (1 - al) + img * al, 0, 255).astype(np.uint8)
        c = linha_aa(forma, cantos, q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - c) + np.float32(q["contorno"]) * c, 0, 255).astype(np.uint8)
    print("    área de serviço: bloco de madeira em granito tecido e as duas máquinas em inox da Casa D")
    return out


# X tracejado da área de serviço descoberta (item 9): os traços da DOC_LINHAS E PROJEÇÕES na janela,
# no estilo da projeção da garagem da Casa D (cinza claro, traço fino, só sobre o granito)
X_DESCOBERTA = {
    "janela": (1012, 216, 1160, 284), "layer": "DOC_LINHAS E PROJEÇÕES",
    "cor": (160, 161, 160), "larg": 0.45, "forca": 0.7,
    "granito_lum": (35.0, 115.0),
}


def x_descoberta(out, A):
    q = X_DESCOBERTA
    x0, y0, x1, y1 = q["janela"]
    h, w = y1 - y0, x1 - x0
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    pts = []
    for d in pg.get_drawings():
        if d.get("layer") != q["layer"] or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] == "l":
                a, b = p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)
                if all(x0 <= u <= x1 and y0 <= v <= y1 for u, v in (a, b)):
                    pts.append((a, b))
    m = np.zeros((h * SS, w * SS), np.uint8)
    for a, b in pts:
        cv2.line(m, [int(round((a[0] - x0) * SS)), int(round((a[1] - y0) * SS))],
                 [int(round((b[0] - x0) * SS)), int(round((b[1] - y0) * SS))], 255,
                 max(1, int(round(q["larg"] * SS))), cv2.LINE_AA)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    Y = reg.mean(axis=2)
    lo, hi = q["granito_lum"]
    gran = ((Y > lo) & (Y < hi) & (reg[..., 2] > reg[..., 0])).astype(np.float32)
    a = (cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * gran * q["forca"])[..., None]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.float32(q["cor"]) * a, 0, 255).astype(np.uint8)
    print(f"    área de serviço descoberta: X tracejado do PDF ({len(pts)} traços)")
    return out


# DCE (item 10): o que o motor fez (laje, armário alto e pia) sai, e entram as peças do DCE do Térreo
# retocado da Casa D (aprovado) nos retângulos do PDF (ARQ_LAYOUT HUMANIZAÇÃO); a cama e o
# criado-mudo de lá estão em pé (cabeceira em cima): giradas no sentido horário, a cabeceira fica à
# direita, onde o PDF tem o travesseiro
DCE = {
    "janela": (1150, 250, 1250, 332),
    "limpar": [(1177, 255, 1245, 299), (1156, 288, 1179, 327)],
    "fontes_granito": [(1214, 299, 1240, 325)],
    "fonte": RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png",
    # (nome, recorte na Casa D, giro, retângulo do PDF no render, sombra de móvel baixo)
    "pecas": [("cama", (1338, 271, 1369, 334), cv2.ROTATE_90_CLOCKWISE, (1179.1, 254.6, 1243.2, 284.4), True),
              ("criado-mudo", (1323, 272, 1334, 285), cv2.ROTATE_90_CLOCKWISE, (1229.9, 285.4, 1242.4, 296.3), True),
              ("armário até o teto", (1295, 330, 1326, 349), cv2.ROTATE_90_COUNTERCLOCKWISE,
               (1159.2, 290.3, 1176.3, 324.5), False)],
    "contorno": (70, 72, 74), "larg_contorno": 0.4,
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35},
}


def colar(out, img, ret):
    """Leva img ao retângulo ret (x0, y0, x1, y1, em px do render, subpixel) por afim, com a borda
    antisserrilhada."""
    x0, y0, x1, y1 = ret
    h, w = img.shape[:2]
    M = cv2.getAffineTransform(np.float32([(0, 0), (w, 0), (0, h)]), np.float32([(x0, y0), (x1, y0), (x0, y1)]))
    forma = out.shape[:2]
    im = cv2.warpAffine(img.astype(np.float32), M, forma[::-1], flags=cv2.INTER_AREA)
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])[..., None]
    out[:] = np.clip(out * (1 - al) + im * al, 0, 255).astype(np.uint8)
    return out


def sombra_curta(out, ret, s):
    x0, y0, x1, y1 = ret
    cantos = np.float32([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]) + np.float32(s["desloc"])
    sombra = cv2.GaussianBlur(poligono_aa(out.shape[:2], cantos), (0, 0), s["sigma"])
    out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
    return out


def dce(out):
    q = DCE
    wx0, wy0, wx1, wy1 = q["janela"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    for x0, y0, x1, y1 in q["limpar"]:
        m[y0 - wy0:y1 - wy0, x0 - wx0:x1 - wx0] = True
    out = apagar_largo(out, q["janela"], m, q["fontes_granito"], sigma=3.0, lum_min=40, escuros=False)
    casad = cv2.imread(str(q["fonte"]))
    for nome, (fx0, fy0, fx1, fy1), giro, ret, sombra in q["pecas"]:
        if sombra:
            out = sombra_curta(out, ret, q["sombra"])
        out = colar(out, cv2.rotate(casad[fy0:fy1, fx0:fx1], giro), ret)
        x0, y0, x1, y1 = ret
        c = linha_aa(out.shape[:2], [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - c) + np.float32(q["contorno"]) * c, 0, 255).astype(np.uint8)
        print(f"    DCE, {nome}: a da Casa D em ({x0:.1f}, {y0:.1f}) - ({x1:.1f}, {y1:.1f})")
    return out


# WC DCE 1 (item 11): o vaso que o motor pôs onde o PDF tem o chuveiro (a parede da direita começa em
# x = 1289; a linha do box, que fica, nas linhas 280-281) e o chuveiro do PDF (ARQ_LOUÇAS E METAIS),
# no mesmo desenho do WC DCE da Casa D (a mesma geometria, quase)
WC_DCE = {
    "janela": (1248, 254, 1292, 286), "vaso": (1263, 257, 1289, 280),
    "fontes": [(1251, 258, 1264, 279), (1251, 283, 1270, 299)],
    # a luz vem só do piso limpo (~200-212): sem a linha do box nem a borda da parede, que escureciam
    "lum_min": 192,
    "chuveiro": {"nome": "WC DCE 1", "ducha": (1275.0, 264.4, 1281.2, 270.5), "braco": (1278.1, 1289.7, 267.5),
                 "canopla": (1288.9, 266.5, 1290.1, 268.5)},
    "sombra": {"desloc": (-1.0, 1.0), "sigma": 0.8, "forca": 0.3},
}


def wc_dce(out):
    q = WC_DCE
    wx0, wy0, wx1, wy1 = q["janela"]
    vx0, vy0, vx1, vy1 = q["vaso"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    m[vy0 - wy0:vy1 - wy0, vx0 - wx0:vx1 - wx0] = True
    out = apagar_largo(out, q["janela"], m, q["fontes"], sigma=3.0, lum_min=q["lum_min"], lum_max=235, escuros=True)
    out = desenhar_chuveiro(out, q["janela"], q["chuveiro"], sombra=q["sombra"])
    print("    WC DCE 1: vaso inventado fora; chuveiro do PDF (ducha, braço e canopla)")
    return out


# arcos das portas sobre o granito (item 12, pedido do usuário): o padrão das Casas C e D (cinza
# (160, 161, 160) e traço de 0,45 px na escala do Térreo), só onde a base chapada é granito. Com a R3 (item 38,
# "Não mostrar arco da porta"), o arco cinza deixa de ser desenhado ("desenhar"); o arco escuro do motor segue saindo
ARCOS = {"granito": (50, 66, 90), "tol": 12, "fracao": 0.3, "min_px": 8, "desenhar": False,
         "cor": (160, 161, 160), "larg": 0.45, "faixa": 1.5, "escuro": 55,
         "fontes_granito": [(700, 160, 900, 200), (1300, 160, 1450, 200)]}


def granito_render(forma, A):
    """Máscara (0/1) do granito da base chapada no quadro do render, com os traços finos fechados."""
    q = ARCOS
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), forma[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, forma[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    gran = (np.abs(chapada.astype(np.int32) - np.array(q["granito"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    return cv2.morphologyEx(gran, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))   # fecha os traços finos


def arcos_granito(out, A):
    """Arcos das portas (curvas da ARQ_PAREDE) sobre o granito: o arco escuro do render sai (px
    escuros numa faixa em volta da curva do PDF, só no granito da base chapada) e, sem a R3, entra o cinza fino."""
    q = ARCOS
    gran = granito_render(out.shape[:2], A)
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    n = 0
    for d in pg.get_drawings():
        if d.get("layer") != "ARQ_PAREDE" or not any(it[0] == "c" for it in d["items"]):
            continue
        x0, y0, x1, y1 = caixa_render(d, p2r)
        x0, y0, x1, y1 = int(x0) - 4, int(y0) - 4, int(np.ceil(x1)) + 5, int(np.ceil(y1)) + 5
        if max(x1 - x0, y1 - y0) < q["min_px"] or x0 < 0 or y0 < 0 or x1 > out.shape[1] or y1 > out.shape[0]:
            continue
        g = gran[y0:y1, x0:x1].astype(bool)
        if g.mean() < q["fracao"]:
            continue
        h, w = y1 - y0, x1 - x0
        curvas = []
        for it in d["items"]:
            if it[0] == "c":
                pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
                tt = np.linspace(0, 1, 80)[:, None]
                curvas.append((1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1] + 3 * (1 - tt) * tt ** 2 * pp[2]
                              + tt ** 3 * pp[3])

        def traco(larg):
            f = np.zeros((h * SS, w * SS), np.uint8)
            for c in curvas:
                cv2.polylines(f, [np.round((c - [x0, y0]) * SS).astype(np.int32)], False, 255,
                              max(1, int(round(larg * SS))), cv2.LINE_AA)
            return cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

        lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m = (traco(2 * q["faixa"]) > 0.05) & g & (lum < q["escuro"])
        if m.any():
            m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & g
            out = apagar_largo(out, (x0, y0, x1, y1), m, q["fontes_granito"], sigma=2.0, borda=0.0,
                               lum_min=45, lum_max=130, escuros=True)
        n += 1
        if not q["desenhar"]:
            continue
        a = (traco(q["larg"]) * g)[..., None]
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + np.array(q["cor"], np.float32) * a, 0, 255).astype(np.uint8)
    print(f"    {n} arcos de porta sobre o granito: o escuro do motor fora" +
          ("; o cinza fino desenhado" if q["desenhar"] else "; sem o arco (R3)"))
    return out


# pontos claros do granito (item 13, pedido do usuário): pontinhos compactos (2 a 16 px, caixa de
# até 5 x 5) mais claros que o granito em volta (mediana de 11 px), no render original e onde o
# retoque não mexeu (assim os traços desenhados, arcos e X, nunca entram); saem os de contraste >= 30
PONTOS = {"limiar": 18, "sai": 30, "area": (2, 16), "caixa": 5, "mediana": 11, "margem": 2,
          "desloc": [(7, 0), (-7, 0), (0, 7), (0, -7), (7, 7), (-7, -7), (7, -7), (-7, 7), (12, 0), (-12, 0),
                     (0, 12), (0, -12)]}


def pontos_granito(out, orig, A):
    q = PONTOS
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    gran = (np.abs(chapada.astype(np.int32) - np.array(ARCOS["granito"])).max(axis=2) <= ARCOS["tol"]).astype(np.uint8)
    gran = cv2.morphologyEx(gran, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    igual = (np.abs(out.astype(np.int16) - orig.astype(np.int16)).max(axis=2) == 0).astype(np.uint8)
    ok = (cv2.erode(gran, np.ones((7, 7), np.uint8)) > 0) & (cv2.erode(igual, np.ones((7, 7), np.uint8)) > 0)
    Y = orig.astype(np.float32).mean(axis=2)
    d = Y - cv2.medianBlur(orig, q["mediana"]).astype(np.float32).mean(axis=2)
    claro = (d > q["limiar"]) & ok
    n, lab, st, _ = cv2.connectedComponentsWithStats(claro.astype(np.uint8), connectivity=8)
    a0, a1 = q["area"]
    todos = np.zeros(claro.shape, bool)
    sair = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if not (a0 <= area <= a1 and w <= q["caixa"] and h <= q["caixa"]):
            continue
        todos |= lab == i
        if d[lab == i].max() >= q["sai"]:
            sair.append((x, y, w, h, i))
    proibido = cv2.dilate(todos.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    H, W = Y.shape
    feitos = 0
    e = q["margem"]
    for x, y, w, h, i in sair:
        x0, y0, x1, y1 = x - e, y - e, x + w + e, y + h + e
        ponto = (lab[y0:y1, x0:x1] == i).astype(np.float32)
        al = np.maximum(cv2.GaussianBlur(cv2.dilate(ponto, np.ones((3, 3), np.uint8)), (0, 0), 0.7), ponto)[..., None]
        for dx, dy in q["desloc"]:
            sx0, sy0, sx1, sy1 = x0 + dx, y0 + dy, x1 + dx, y1 + dy
            if sx0 < 0 or sy0 < 0 or sx1 > W or sy1 > H:
                continue
            if not ok[sy0:sy1, sx0:sx1].all() or proibido[sy0:sy1, sx0:sx1].any():
                continue
            reg = out[y0:y1, x0:x1].astype(np.float32)
            fonte = out[sy0:sy1, sx0:sx1].astype(np.float32)
            out[y0:y1, x0:x1] = np.clip(reg * (1 - al) + fonte * al, 0, 255).astype(np.uint8)
            feitos += 1
            break
    print(f"    granito: {feitos} de {len(sair)} pontos claros fortes fora (os mais fracos ficam)")
    return out


# pilar à direita do lavabo (item 14, pedido do usuário): o retângulo cinza da ARQ_ELEMENTOS FIXOS
# no quadro do render; o preto é o da parede do lavabo logo à esquerda
PILAR = {"ret": (1296.0, 667.6, 1373.8, 687.8), "parede": (1291, 660, 1295, 683)}


def pilar(out):
    q = PILAR
    a, b, c, d = q["parede"]
    viz = out[b:d, a:c].reshape(-1, 3)
    preto = np.median(viz[viz.astype(np.float32).mean(axis=1) < 40], axis=0).astype(np.float32)
    x0, y0, x1, y1 = q["ret"]
    al = poligono_aa(out.shape[:2], [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])[..., None]
    out[:] = np.clip(out * (1 - al) + preto * al, 0, 255).astype(np.uint8)
    print(f"    pilar: ({x0}, {y0}) - ({x1}, {y1}) no preto das paredes {preto.astype(int).tolist()}")
    return out


# lavabo (item 15, pedido do usuário): a bancada do render vai de x 1199 a 1251 e de y 667 a 682 (a
# parede da esquerda termina em 1196 e a de baixo começa em 683); a cuba e a torneira do motor ficam
# em x 1218-1239. A cuba esculpida ocupa a metade esquerda do PDF (até 1226,4) com ~2 px de borda,
# e a torneira do PDF (ARQ_LOUÇAS E METAIS) sai da parede da esquerda, na altura do meio da cuba
LAVABO = {
    # a cuba e a torneira do motor saem: as mesmas linhas de quartzo limpo da própria bancada (a luz de
    # cada linha fica), à esquerda e à direita em espelho
    "bancada": (1199, 667, 1252, 683),
    "copias": [((1218, 1227), (1205, 1214), False), ((1227, 1239), (1240, 1252), True)],
    "cuba": (1201.0, 668.8, 1224.6, 680.6),
    "inclinacao": 0.12,                       # o fundo escurece até 12% junto à fenda (atrás)
    "sombra_borda": (0.16, 1.4),               # força e largura da sombra das bordas de cima e da direita
    "luz_borda": 0.04,
    "fenda": {"cor": (92, 94, 98), "larg": 0.8, "recuo": 1.3},
    "contorno": (150, 150, 150), "larg_contorno": 0.4, "forca_contorno": 0.6,
    "torneira": {"canopla": (1198.4, 672.6, 1200.3, 676.8), "bica": (1199.5, 1207.5), "larg": 1.2},
    "sombra": {"desloc": (-1.0, 1.0), "sigma": 0.8, "forca": 0.3},
}


def cuba_esculpida(out, ret, q):
    """Cuba esculpida na própria pedra da bancada, com a parede embaixo: o fundo inclinado escurece
    para trás, onde fica a fenda do ralo; as bordas de cima e da direita fazem sombra curta para
    dentro, as outras pegam um pouco de luz; traço fino na borda."""
    forma = out.shape[:2]
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
    x0, y0, x1, y1 = ret
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    f = 1 - q["inclinacao"] * np.clip((yy - y0) / (y1 - y0), 0, 1)
    s, w = q["sombra_borda"]
    f *= 1 - s * np.exp(-np.clip(yy - y0, 0, None) / w) - s * np.exp(-np.clip(x1 - xx, 0, None) / w)
    f *= 1 + q["luz_borda"] * (np.exp(-np.clip(xx - x0, 0, None) / w) + np.exp(-np.clip(y1 - yy, 0, None) / w))
    f = 1 + (f - 1) * al
    out[:] = np.clip(out * f[..., None], 0, 255).astype(np.uint8)
    fd = q["fenda"]
    a = linha_aa(forma, [(x0 + 1.5, y1 - fd["recuo"]), (x1 - 1.5, y1 - fd["recuo"])], fd["larg"])[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(fd["cor"]) * a, 0, 255).astype(np.uint8)
    a = linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], q["larg_contorno"], fechada=True)[..., None] * q["forca_contorno"]
    out[:] = np.clip(out * (1 - a) + np.float32(q["contorno"]) * a, 0, 255).astype(np.uint8)
    return out


def lavabo(out):
    q = LAVABO
    bx0, by0, bx1, by1 = q["bancada"]
    for (a0, a1), (f0, f1), espelho in q["copias"]:
        fonte = out[by0:by1, f0:f1]
        out[by0:by1, a0:a1] = fonte[:, ::-1] if espelho else fonte
    out = cuba_esculpida(out, q["cuba"], q)
    x0, y0, x1, y1 = q["cuba"]
    forma = out.shape[:2]
    # torneira: canopla na parede da esquerda e a bica cromada até o meio da cuba
    tq = q["torneira"]
    yc = (y0 + y1) / 2
    bica = [(tq["bica"][0], yc), (tq["bica"][1], yc)]
    sb = q["sombra"]
    sombra = cv2.GaussianBlur(linha_aa(forma, [(u + sb["desloc"][0], v + sb["desloc"][1]) for u, v in bica], tq["larg"]),
                              (0, 0), sb["sigma"])
    out[:] = np.clip(out * (1 - sb["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
    for pts, larg, cor in ((bica, tq["larg"], CROMO_ESCURO),
                           ([(tq["bica"][0], yc - 0.15), (tq["bica"][1] - 0.3, yc - 0.15)], 0.35, CROMO_CLARO)):
        a = linha_aa(forma, pts, larg)[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(cor) * a, 0, 255).astype(np.uint8)
    cx0, cy0, cx1, cy1 = tq["canopla"]
    a = poligono_aa(forma, [(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)])[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(CROMO) * a, 0, 255).astype(np.uint8)
    print("    lavabo: cuba do motor fora; cuba esculpida no quartzo e torneira saindo da parede da esquerda")
    return out


# arranjo de flores do escritório (item 16): o círculo do PDF e a estrelítzia do jardim do próprio
# render (centro da touceira com duas flores laranja), no quadro do render
ARRANJO = {"centro": (1275.95, 606.2), "raio": 7.2, "fonte": ((1582, 899), 17),
           "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35}}


def arranjo(out, orig):
    q = ARRANJO
    (cx, cy), r = q["centro"], q["raio"]
    (fx, fy), fr = q["fonte"]
    fonte = orig[fy - fr:fy + fr, fx - fr:fx + fr]
    forma = out.shape[:2]
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
    disco = np.clip(r + 0.5 - np.hypot(xx - cx, yy - cy), 0, 1)
    s = q["sombra"]
    sombra = cv2.GaussianBlur(np.clip(r + 0.5 - np.hypot(xx - cx - s["desloc"][0], yy - cy - s["desloc"][1]), 0, 1),
                              (0, 0), s["sigma"])
    # a bola verde do motor sai junto: a sombra e o arranjo cobrem o círculo dela
    out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
    out = colar_disco(out, fonte, (cx, cy), r, disco)
    print(f"    escritório: arranjo de flores (estrelítzia do jardim) no círculo do PDF, raio {r} px")
    return out


def colar_disco(out, img, centro, r, alfa):
    """Leva img (quadrada) ao quadrado de lado 2r em volta do centro, por afim, com a máscara alfa."""
    cx, cy = centro
    h, w = img.shape[:2]
    M = cv2.getAffineTransform(np.float32([(0, 0), (w, 0), (0, h)]),
                               np.float32([(cx - r, cy - r), (cx + r, cy - r), (cx - r, cy + r)]))
    im = cv2.warpAffine(img.astype(np.float32), M, out.shape[1::-1], flags=cv2.INTER_AREA)
    a = alfa[..., None]
    out[:] = np.clip(out * (1 - a) + im * a, 0, 255).astype(np.uint8)
    return out


# veio do louceiro (item 17): a madeira lisa do louceiro no quadro do render e o tampo da mesa de
# jantar (veio vertical, sem cadeiras), como os veios do DCE da Casa D
VEIO_LOUCEIRO = {"peca": (984, 471, 1147, 490), "fonte": (885, 505, 914, 589),
                 "realce": 2.2, "sigma": 3.0, "lim": (0.85, 1.15), "borda": 1}


def veio_louceiro(out, orig):
    q = VEIO_LOUCEIRO
    a, b, c, d = q["fonte"]
    Y = orig[b:d, a:c].astype(np.float32).mean(axis=2)
    v = Y / np.maximum(cv2.GaussianBlur(Y, (0, 0), q["sigma"], borderType=cv2.BORDER_REFLECT), 1)
    v = np.clip(1 + q["realce"] * (v - 1), *q["lim"])
    g = cv2.rotate(v, cv2.ROTATE_90_CLOCKWISE)                       # veio no comprimento (em x)
    x0, y0, x1, y1 = q["peca"]
    h, w = y1 - y0, x1 - x0
    g = np.concatenate([g, g[::-1]] * (h // (2 * g.shape[0]) + 1), axis=0)[:h]
    g = np.concatenate([g, g[:, ::-1]] * (w // (2 * g.shape[1]) + 1), axis=1)[:, :w]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    base = cv2.GaussianBlur(reg, (0, 0), 1.2)
    e = q["borda"]
    novo = reg.copy()
    novo[e:-e, e:-e] = (base * g[..., None])[e:-e, e:-e]
    out[y0:y1, x0:x1] = np.clip(novo, 0, 255).astype(np.uint8)
    print(f"    louceiro: veio da mesa de jantar, realce {q['realce']}")
    return out


# escadas (itens 18 e 21, pedidos do usuário): os degraus do PDF (ARQ_ESCADAS E RAMPAS) no quadro do
# render, só com sombreamento, sem linhas. "baixo" diz de que lado fica o piso mais baixo: o degrau
# desse lado é o mais escuro e cada espelho joga sombra curta no piso de baixo, do lado de "baixo";
# a sombra do último espelho cai no piso vizinho até "fim_sombra". O travertino vem de "fonte" (a 1ª
# linha e a 1ª coluna de um trecho limpo, com os veios verticais)
ESCADAS = [
    {"nome": "interna (sobe da direita para a esquerda)", "x": (976.4, 1154.6), "n": 19, "linhas": (497, 543),
     "fonte": (600, 976), "baixo": "direita", "fim_sombra": 1163},
    {"nome": "externa (desce da direita para a esquerda)", "x": (599.6, 758.1), "n": 17, "linhas": (212, 248),
     "fonte": (612, 990), "baixo": "esquerda", "fim_sombra": 591},
]
# com a R14 (item 39), o sombreamento dos itens 18 e 21 sai: fica só o travertino limpo, e as linhas vêm depois
R14_ESCADAS = True
ESCADA = {"escurece": 0.10, "sombra": (0.18, 2.0)}   # o mais baixo 10% mais escuro; força e decaimento


def escada(out, q):
    xa, xb = q["x"]
    y0, y1 = q["linhas"]
    xi0, xi1 = int(np.floor(xa)), int(np.ceil(xb))
    f0, c0 = q["fonte"]
    out[y0:y1, xi0:xi1] = out[f0:f0 + (y1 - y0), c0:c0 + (xi1 - xi0)]
    if R14_ESCADAS:
        print(f"    escada {q['nome']}: travertino limpo, sem linhas (as da R14 vêm no item 39)")
        return out
    passo = (xb - xa) / q["n"]
    forca, dec = ESCADA["sombra"]
    direita = q["baixo"] == "direita"
    c0, c1 = (xi0, q["fim_sombra"]) if direita else (q["fim_sombra"], xi1)
    xs = np.arange(c0, c1, dtype=np.float32)
    sub = xs[:, None] + (np.arange(8, dtype=np.float32)[None, :] + 0.5) / 8          # 8 amostras por px
    k = np.clip(np.floor((sub - xa) / passo), 0, q["n"] - 1)       # índice do degrau, da esquerda
    baixeza = k / (q["n"] - 1) if direita else 1 - k / (q["n"] - 1)
    na_escada = (sub >= xa) & (sub < xb)
    f = np.where(na_escada, 1 - ESCADA["escurece"] * baixeza, 1.0)
    if direita:      # espelho à esquerda de cada degrau de baixo: sombra para a direita
        borda = xa + np.clip(np.floor((sub - xa) / passo), 0, q["n"]) * passo
        dist, tem = sub - borda, (sub > xa + passo) | (sub >= xb)
    else:            # espelho à direita de cada degrau de baixo: sombra para a esquerda
        borda = xa + np.clip(np.ceil((sub - xa) / passo), 0, q["n"]) * passo
        dist, tem = borda - sub, (sub < xb - passo) | (sub < xa)
    f *= np.where(tem, 1 - forca * np.exp(-dist / dec), 1.0)
    f = f.mean(axis=1)
    out[y0:y1, c0:c1] = np.clip(out[y0:y1, c0:c1] * f[None, :, None], 0, 255).astype(np.uint8)
    print(f"    escada {q['nome']}: {q['n']} pisos de {passo:.2f} px, sem linhas")
    return out


# jardim de inverno (item 19, pedido do usuário): quanto as folhas podem sair da floreira (px, com
# uma borda irregular entre o mínimo e o máximo) e as flores (o centro da estrelítzia no render, o
# raio do recorte, onde entra na floreira e o tom: o laranja do render ou girado para outra cor)
JARDIM_FORA = {
    "lados": (1.5, 3.5), "baixo": (3.0, 6.5), "semente": 642,
    "flores": {"fonte": [((1671, 540), 9), ((1773, 605), 9), ((1582, 905), 9), ((1440, 722), 8)],
               "pos": [((1002, 557), 0, None), ((1046, 571), 1, "vermelho"), ((1089, 554), 2, None),
                       ((1121, 572), 3, "rosa"), ((1143, 556), 0, "amarelo")],
               "giro_matiz": {"vermelho": -9, "rosa": -20, "amarelo": 9}, "escala": 0.85},
}


def jardim_flores(out, orig):
    q = JARDIM_FORA
    j = JARDIM
    fx0, fy0, fx1, fy1 = j["floreira"]
    wx0, wy0, wx1, wy1 = j["janela"]
    reg = orig[wy0:wy1, wx0:wx1].astype(np.float32)
    lum = reg.mean(axis=2)
    ri = reg.astype(int)
    planta = (ri[..., 1] > ri[..., 2] + j["verde"]) | (lum < j["escuro"])
    dentro = np.zeros(lum.shape, bool)
    dentro[fy0 - wy0:fy1 - wy0, fx0 - wx0:fx1 - wx0] = True
    n, lab = cv2.connectedComponents(planta.astype(np.uint8))
    ligada = np.isin(lab, np.unique(lab[dentro & planta])) & (lab > 0)
    # quanto pode sair: borda irregular (ruído suave) entre o mínimo e o máximo de cada lado
    rng = np.random.default_rng(q["semente"])
    h, w = lum.shape
    ys, xs = np.mgrid[wy0:wy1, wx0:wx1].astype(np.float32) + 0.5

    def ruido(n_, a, b):
        v = cv2.GaussianBlur(rng.normal(0, 1, (1, n_)).astype(np.float32), (0, 0), 4.0)[0]
        v = (v - v.min()) / max(float(np.ptp(v)), 1e-6)
        return a + (b - a) * v

    baixo = ruido(w, *q["baixo"])[None, :]
    esq = ruido(h, *q["lados"])[:, None]
    dir_ = ruido(h, *q["lados"])[:, None]
    # folga de cada px até o limite (o menor dos três lados); as pontas somem num degradê de 2 px, em
    # vez de um corte seco (que lia como papel rasgado)
    folga = np.minimum(np.minimum(fy1 + baixo - ys, xs - (fx0 - esq)), fx1 + dir_ - xs)
    pode = (ys >= fy0 + 1.5) & (folga > 0)
    miolo = (ys > fy0 + 1.5) & (ys < fy1 - 1.5) & (xs > fx0 + 1.5) & (xs < fx1 - 1.5)
    faixa = pode & ~miolo
    suave = np.clip(folga / 2.0, 0, 1)
    # só as folhas voltam (a sombra antiga do render, larga, borrava a borda); a sombra é desenhada:
    # curta, embaixo e à esquerda das folhas que saem, só no travertino
    fora = faixa & ligada & ~(dentro & ~faixa)            # só px de folha (sem o halo claro do render)
    a = fora.astype(np.float32)
    a = np.maximum(cv2.GaussianBlur(a, (0, 0), 0.5), a) * faixa * suave
    cur = out[wy0:wy1, wx0:wx1].astype(np.float32)
    tudo = np.maximum(dentro.astype(np.float32), a)
    M = np.float32([[1, 0, -1.5], [0, 1, 1.5]])
    sb = cv2.GaussianBlur(cv2.warpAffine(tudo, M, (w, h)), (0, 0), 1.0) * (1 - tudo) * (ys > fy0 + 2)
    cur *= (1 - 0.35 * sb)[..., None]
    a = a[..., None]
    out[wy0:wy1, wx0:wx1] = np.clip(cur * (1 - a) + reg * a, 0, 255).astype(np.uint8)
    # flores: o laranja da estrelítzia (pétalas e bico), recortado com borda suave e girado de matiz
    fq = q["flores"]
    forma = out.shape[:2]
    for (px, py), i, cor in fq["pos"]:
        (sx, sy), sr = fq["fonte"][i]
        rec = orig[sy - sr:sy + sr + 1, sx - sr:sx + sr + 1]
        hsv = cv2.cvtColor(rec, cv2.COLOR_BGR2HSV).astype(np.float32)
        b_, g_, r_ = [rec[..., c].astype(np.float32) for c in range(3)]
        flor = np.clip((r_ - g_ - 35) / 30, 0, 1) * np.clip((r_ - 120) / 40, 0, 1)
        flor = cv2.GaussianBlur(flor, (0, 0), 0.5)
        if cor:
            hsv[..., 0] = (hsv[..., 0] + fq["giro_matiz"][cor]) % 180
            if cor == "rosa":
                hsv[..., 1] *= 0.8
        img = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        s = fq["escala"]
        lado = rec.shape[0]
        M = cv2.getAffineTransform(np.float32([(0, 0), (lado, 0), (0, lado)]),
                                   np.float32([(px - lado * s / 2, py - lado * s / 2), (px + lado * s / 2, py - lado * s / 2),
                                               (px - lado * s / 2, py + lado * s / 2)]))
        im = cv2.warpAffine(img, M, forma[::-1], flags=cv2.INTER_AREA)
        al = cv2.warpAffine(flor, M, forma[::-1], flags=cv2.INTER_AREA)[..., None]
        out[:] = np.clip(out * (1 - al) + im * al, 0, 255).astype(np.uint8)
    print(f"    jardim de inverno: folhas um pouco para fora (sem a escada) e {len(fq['pos'])} flores tropicais")
    return out


# sem tapete no estar da varanda (item 20): o retângulo do tapete do motor, a janela dos móveis em
# volta e trechos limpos de Bege Bahia da varanda (acima do sofá e abaixo do banco)
SEM_TAPETE = {
    "tapete": (666, 653, 810, 769), "janela": (655, 630, 820, 790),
    "fontes": [(700, 778, 786, 812), (530, 700, 600, 760)],
    "camadas": ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO"),
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.3},
}


def sem_tapete(out, A):
    q = SEM_TAPETE
    wx0, wy0, wx1, wy1 = q["janela"]
    pg, p2r, _ = pdf_cadeia(A, out.shape)

    def movel(d):
        c = caixa_render(d, p2r)
        return (d.get("fill") == (1.0, 1.0, 1.0) and d.get("layer") in q["camadas"] and
                c[2] > wx0 and c[0] < wx1 and c[3] > wy0 and c[1] < wy1 and (c[2] - c[0]) < 80)

    moveis = mascara_pdf(q["janela"], A, out.shape, movel)
    # os móveis do PDF com 1 px de folga, mais o contorno escuro do render até 2 px (o tapete, mais
    # claro, não entra: senão ficava um halo dele em volta das peças)
    mv = (moveis > 0.3).astype(np.uint8)
    lum = out[wy0:wy1, wx0:wx1].astype(np.float32).mean(axis=2)
    pecas = (cv2.dilate(mv, np.ones((3, 3), np.uint8)) > 0) | ((cv2.dilate(mv, np.ones((5, 5), np.uint8)) > 0) & (lum < 195))
    tx0, ty0, tx1, ty1 = q["tapete"]
    m = np.zeros(pecas.shape, bool)
    m[ty0 - wy0:ty1 - wy0, tx0 - wx0:tx1 - wx0] = True
    m &= ~pecas
    out = apagar_largo(out, q["janela"], m, q["fontes"], sigma=6.0, borda=0.6, lum_min=185, lum_max=228, escuros=True)
    # sombra curta dos móveis no piso refeito (só onde era tapete)
    s = q["sombra"]
    h, w = pecas.shape
    M = np.float32([[1, 0, s["desloc"][0]], [0, 1, s["desloc"][1]]])
    a = np.clip(moveis, 0, 1)
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (w, h)), (0, 0), s["sigma"]) * (1 - a) * m
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    out[wy0:wy1, wx0:wx1] = np.clip(reg * (1 - s["forca"] * sb)[..., None], 0, 255).astype(np.uint8)
    print(f"    estar da varanda: tapete do motor fora ({int(m.sum())} px de Bege Bahia), sombra curta dos móveis")
    return out


# vaso com tampo (item 22): a caixa do polígono do PDF no quadro do render e o lado da parede (onde
# fica a caixa acoplada); os números são os do Subsolo da Casa D divididos pela razão das escalas
# (~2,7: aquele render aproximou a planta)
VASOS = [{"nome": "banho gourmet", "caixa": (607.5, 256.1, 618.5, 272.1), "parede": "cima"}]
VASO = {"dobradica": 4.0, "recuo": 0.5, "cor_tampo": (250, 250, 249),
        "sombra": (0.7, 0.7, 0.9, 0.3), "sombra_tampo": (0.25, 0.3, 0.4, 0.18),
        "volume": (0.88, 2.0), "volume_tampo": (0.9, 2.4), "contorno": 0.45, "contorno_tampo": 0.35,
        "limpar": 2, "fontes_granito": [(700, 160, 900, 200)]}


def vasos(out, A):
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    q = VASO
    for v in VASOS:
        cx0, cy0, cx1, cy1 = v["caixa"]
        corpo = next(d for d in pg.get_drawings() if d.get("layer") == "ARQ_LOUÇAS E METAIS" and d["type"] == "f"
                     and max(abs(a - b) for a, b in zip(caixa_render(d, p2r), v["caixa"])) < 1.0)
        wx0, wy0, wx1, wy1 = int(cx0) - 6, int(cy0) - 6, int(np.ceil(cx1)) + 7, int(np.ceil(cy1)) + 7
        h, w = wy1 - wy0, wx1 - wx0
        # o símbolo do motor sai: os px claros na caixa (com folga) viram granito tecido
        e = q["limpar"]
        reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
        caixa = np.zeros((h, w), bool)
        caixa[int(cy0) - wy0 - e:int(np.ceil(cy1)) - wy0 + e, int(cx0) - wx0 - e:int(np.ceil(cx1)) - wx0 + e] = True
        claro = caixa & (cv2.dilate((reg.mean(axis=2) > 110).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
        out = apagar_largo(out, (wx0, wy0, wx1, wy1), claro, q["fontes_granito"], sigma=2.0, borda=0.0,
                           lum_min=40, lum_max=110, escuros=True)
        pts = []
        for it in corpo["items"]:
            for pt in it[1:]:
                if hasattr(pt, "x"):
                    x, y = p2r(pt.x, pt.y)
                    pts.append([round((x - wx0) * SS), round((y - wy0) * SS)])
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.fillPoly(m, [cv2.convexHull(np.int32(pts))], 255)
        reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

        def reduzir(mm):
            return cv2.resize(mm.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)

        def pintar(mm, cor):
            nonlocal reg
            a = reduzir(mm / 255.0 if mm.dtype == np.uint8 else mm)[..., None]
            reg = reg * (1 - a) + np.asarray(cor, np.float32) * a

        def anel(mm, larg):
            k = max(1, int(round(larg * SS)))
            return mm & ~cv2.erode(mm, np.ones((k, k), np.uint8))

        sdx, sdy, ssig, sforca = q["sombra"]
        sh = cv2.warpAffine(m.astype(np.float32) / 255, np.float32([[1, 0, sdx * SS], [0, 1, sdy * SS]]), (w * SS, h * SS))
        reg *= (1 - sforca * reduzir(cv2.GaussianBlur(sh, (0, 0), ssig * SS)) * (1 - reduzir(m / 255.0)))[..., None]
        dist = cv2.distanceTransform(m, cv2.DIST_L2, 5) / SS
        borda, alcance = q["volume"]
        tom = borda + (1 - borda) * np.clip(dist / alcance, 0, 1)
        cor_ss = np.asarray(LOUCA, np.float32)[None, None, :] * tom[..., None] * (m / 255.0)[..., None]
        pintar(m, (0, 0, 0))
        reg += cv2.resize(cor_ss, (w, h), interpolation=cv2.INTER_AREA)
        pintar(anel(m, q["contorno"]), LOUCA_CONTORNO)
        # tampo fechado: o corpo recuado, da linha da dobradiça à frente
        tampo = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * q["recuo"] * SS) + 1,) * 2))
        ys = wy0 + (np.arange(h * SS) + 0.5) / SS
        xs = wx0 + (np.arange(w * SS) + 0.5) / SS
        lado = v["parede"]
        if lado == "cima":
            tampo[ys < cy0 + q["dobradica"], :] = 0
        elif lado == "baixo":
            tampo[ys > cy1 - q["dobradica"], :] = 0
        elif lado == "esquerda":
            tampo[:, xs < cx0 + q["dobradica"]] = 0
        else:
            tampo[:, xs > cx1 - q["dobradica"]] = 0
        tampo = cv2.morphologyEx(tampo, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (SS + 1,) * 2))
        tdx, tdy, tsig, tforca = q["sombra_tampo"]
        st = cv2.warpAffine(tampo.astype(np.float32) / 255, np.float32([[1, 0, tdx * SS], [0, 1, tdy * SS]]), (w * SS, h * SS))
        reg *= (1 - tforca * reduzir(cv2.GaussianBlur(st, (0, 0), tsig * SS)) * (1 - reduzir(tampo / 255.0)))[..., None]
        dt = cv2.distanceTransform(tampo, cv2.DIST_L2, 5) / SS
        borda, alcance = q["volume_tampo"]
        tom = borda + (1 - borda) * np.clip(dt / alcance, 0, 1)
        cor_t = np.asarray(q["cor_tampo"], np.float32)[None, None, :] * tom[..., None] * (tampo / 255.0)[..., None]
        reg = reg * (1 - reduzir(tampo / 255.0)[..., None]) + cv2.resize(cor_t, (w, h), interpolation=cv2.INTER_AREA)
        pintar(anel(tampo, q["contorno_tampo"]), LOUCA_CONTORNO)
        out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    vaso do {v['nome']}: símbolo do CAD fora; louça com volume e tampo fechado")
    return out


# bancada do banho gourmet (item 23): a bancada, a cuba (o painel do meio) e a torneira do PDF no
# quadro do render; no granito, o contorno é o cinza fino dos arcos e a fenda do ralo é escura
BANCADA_GOURMET = {
    "bancada": (704.5, 289.4, 753.5, 302.7), "cuba": (715.3, 290.9, 729.4, 301.4),
    "tampo": 1.07, "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.3},
    "inclinacao": 0.14, "sombra_borda": (0.2, 1.4), "luz_borda": 0.05,
    "fenda": {"cor": (22, 22, 24), "larg": 0.8, "recuo": 1.3},
    "contorno": (160, 161, 160), "larg_contorno": 0.45, "forca_contorno": 0.8,
    "torneira": {"base": (712.4, 296.3, 1.0), "bica": (712.4, 717.0), "larg": 1.0},
}


def bancada_gourmet(out):
    q = BANCADA_GOURMET
    forma = out.shape[:2]
    x0, y0, x1, y1 = q["bancada"]
    cantos = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    s = q["sombra"]
    sombra = cv2.GaussianBlur(poligono_aa(forma, np.float32(cantos) + np.float32(s["desloc"])), (0, 0), s["sigma"])
    al = poligono_aa(forma, cantos)
    out[:] = np.clip(out * (1 - s["forca"] * sombra * (1 - al))[..., None], 0, 255).astype(np.uint8)
    out[:] = np.clip(out * (1 + (q["tampo"] - 1) * al)[..., None], 0, 255).astype(np.uint8)
    out = cuba_esculpida(out, q["cuba"], q)
    a = linha_aa(forma, cantos, q["larg_contorno"], fechada=True)[..., None] * q["forca_contorno"]
    out[:] = np.clip(out * (1 - a) + np.float32(q["contorno"]) * a, 0, 255).astype(np.uint8)
    tq = q["torneira"]
    bx, by, br = tq["base"]
    bica = [(tq["bica"][0], by), (tq["bica"][1], by)]
    sb = cv2.GaussianBlur(linha_aa(forma, [(u - 1.0, v + 1.0) for u, v in bica], tq["larg"]), (0, 0), 0.8)
    out[:] = np.clip(out * (1 - 0.35 * sb)[..., None], 0, 255).astype(np.uint8)
    for pts, larg, cor in ((bica, tq["larg"], CROMO_ESCURO),
                           ([(bica[0][0], by - 0.15), (bica[1][0] - 0.3, by - 0.15)], 0.35, CROMO_CLARO)):
        a = linha_aa(forma, pts, larg)[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(cor) * a, 0, 255).astype(np.uint8)
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
    a = np.clip(br + 0.5 - np.hypot(xx - bx, yy - by), 0, 1)[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(CROMO) * a, 0, 255).astype(np.uint8)
    print("    banho gourmet: bancada em granito (contorno cinza), cuba esculpida e torneira")
    return out


# porta do hall externo (item 24): a folha pequena e o arco dela (ARQ_PAREDE), no desenho da folha
# grande do render (os tons medidos nela); com a R3 (item 38), sem o arco ("desenhar_arco")
PORTA_HALL = {"folha": (1290.6, 709.4, 1312.4, 710.9), "arco": (1290.6, 688.4, 1312.4, 710.2), "desenhar_arco": False,
              "miolo": (206, 212, 220), "traco_cima": (70, 78, 88), "traco_baixo": (110, 116, 124),
              "larg": 0.6, "cor_arco": (104, 108, 114), "larg_arco": 0.55}


def porta_hall(out, A):
    q = PORTA_HALL
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    forma = out.shape[:2]
    x0, y0, x1, y1 = q["folha"]
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])[..., None]
    out[:] = np.clip(out * (1 - al) + np.float32(q["miolo"]) * al, 0, 255).astype(np.uint8)
    for pts, cor in (([(x0, y0), (x1, y0)], q["traco_cima"]), ([(x0, y1), (x1, y1)], q["traco_baixo"]),
                     ([(x1, y0), (x1, y1)], q["traco_cima"]), ([(x0, y0), (x0, y1)], q["traco_cima"])):
        a = linha_aa(forma, pts, q["larg"])[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(cor) * a, 0, 255).astype(np.uint8)
    arco = next(d for d in pg.get_drawings() if d.get("layer") == "ARQ_PAREDE" and d["type"] == "s"
                and any(it[0] == "c" for it in d["items"])
                and max(abs(a - b) for a, b in zip(caixa_render(d, p2r), q["arco"])) < 1.0)
    for it in (arco["items"] if q["desenhar_arco"] else []):
        if it[0] != "c":
            continue
        pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
        tt = np.linspace(0, 1, 60)[:, None]
        curva = (1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1] + 3 * (1 - tt) * tt ** 2 * pp[2] + tt ** 3 * pp[3]
        a = linha_aa(forma, curva, q["larg_arco"])[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(q["cor_arco"]) * a, 0, 255).astype(np.uint8)
    print("    hall externo: folha pequena da porta e o arco dela, do PDF")
    return out


# brises do escritório (item 25): a coluna dos retângulos da ARQ_ELEMENTOS FIXOS fora da janela e a
# madeira da mesa de jantar do render (veio vertical; nas réguas, deitado)
BRISES = {"janela": (1292, 500, 1308, 600), "fonte": (885, 505, 914, 589),
          "tons": (0.8, 1.0), "semente": 7, "contorno": (38, 52, 70), "larg_contorno": 0.4,   # BGR, marrom escuro
          "sombra": {"desloc": (-1.2, 1.2), "sigma": 0.8, "forca": 0.4}, "nome": "escritório"}
# brises da lateral direita da garagem (item 33, pedido do usuário): os 8 do PDF sobre o granito, acima
# do trecho de parede, no mesmo desenho dos do escritório
BRISES_GARAGEM = dict(BRISES, janela=(1565, 240, 1580, 328), semente=13, nome="garagem")


def brises(out, orig, A, q=BRISES):
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    wx0, wy0, wx1, wy1 = q["janela"]
    rets = sorted({tuple(round(v, 2) for v in caixa_render(d, p2r)) for d in pg.get_drawings()
                   if d.get("layer") == "ARQ_ELEMENTOS FIXOS" and d["type"] == "f"
                   and wx0 <= caixa_render(d, p2r)[0] and caixa_render(d, p2r)[2] <= wx1
                   and wy0 <= caixa_render(d, p2r)[1] and caixa_render(d, p2r)[3] <= wy1}, key=lambda r: r[1])
    a, b, c, d = q["fonte"]
    madeira = cv2.rotate(orig[b:d, a:c], cv2.ROTATE_90_CLOCKWISE)        # veio deitado
    rng = np.random.default_rng(q["semente"])
    forma = out.shape[:2]
    s = q["sombra"]
    for i, (x0, y0, x1, y1) in enumerate(rets):
        cantos = np.float32([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        sombra = cv2.GaussianBlur(poligono_aa(forma, cantos + np.float32(s["desloc"])), (0, 0), s["sigma"])
        out[:] = np.clip(out * (1 - s["forca"] * sombra)[..., None], 0, 255).astype(np.uint8)
        # um trecho diferente da madeira para cada régua, no tamanho dela (8 x mais px que a régua)
        hh, ww = int(np.ceil((y1 - y0) * 3)), int(np.ceil((x1 - x0) * 3))
        oy = int(rng.integers(0, madeira.shape[0] - hh))
        ox = int(rng.integers(0, madeira.shape[1] - ww))
        peca = madeira[oy:oy + hh, ox:ox + ww].astype(np.float32) * rng.uniform(*q["tons"])
        out = colar(out, np.clip(peca, 0, 255).astype(np.uint8), (x0, y0, x1, y1))
        a_ = linha_aa(forma, cantos, q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a_) + np.float32(q["contorno"]) * a_, 0, 255).astype(np.uint8)
    print(f"    {q['nome']}: {len(rets)} brises de madeira do PDF")
    return out


# carros (item 26): a janela da garagem, o granito limpo e, para cada carro (da esquerda para a
# direita), o deslocamento (dx, dy) e o giro (graus) — leves, só para quebrar o alinhamento
CARROS = {"janela": (1300, 250, 1580, 450), "fontes_granito": [(1300, 160, 1450, 200), (700, 160, 900, 200)],
          "movimento": [(-1.0, 6.0, -2.5), (1.0, -4.0, 1.5), (-2.0, 2.0, -1.0)],
          "sombra": {"desloc": (-2.0, 2.0), "sigma": 1.5, "forca": 0.4},
          # R12 (item 41, 19/10/26): "todos os carros de todas as plantas devem estar alinhados, serem do mesmo
          # tamanho e da mesma cor" (prata, 4,70 x 1,85 m). O modelo é o carro prata do render (o do meio), levado
          # a 4,70 m de comprimento e 1,85 m de carroceria (sem os retrovisores), sem giro, no centro de cada carro
          # do PDF (ARQ_LAYOUT HUMANIZAÇÃO, as duas metades de cada um): os três na mesma linha, paralelos.
          "r12": {"modelo": 1, "comprimento_m": 4.70, "largura_m": 1.85, "faixa_largura": (0.35, 0.85),
                  "centros_pdf": [(2355.8, 863.2), (2503.3, 863.2), (2647.3, 863.2)]}}
R12_CARROS = True


def carros(out, A):
    q = CARROS
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = out[wy0:wy1, wx0:wx1].astype(np.int32)
    g = reg.mean(axis=2)
    neutro = np.abs(reg[..., 2] - reg[..., 0]) < 12
    m = ((g > 120) | (neutro & (g > 60))).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    ids = sorted([i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 1500], key=lambda i: cen[i, 0])
    silhuetas = [ndimage.binary_fill_holes(lab == i) for i in ids]
    antes = out.copy()
    tudo = np.zeros(g.shape, bool)
    for s_ in silhuetas:
        tudo |= s_
    sai = cv2.dilate(tudo.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    out = apagar_largo(out, q["janela"], sai, q["fontes_granito"], sigma=4.0, borda=0.8, lum_min=40, lum_max=110,
                       escuros=True)
    h, w = g.shape
    s = q["sombra"]
    if R12_CARROS:
        return carros_r12(out, A, antes, silhuetas[q["r12"]["modelo"]])
    for sil, (dx, dy, ang) in zip(silhuetas, q["movimento"]):
        ys, xs = np.nonzero(sil)
        c = (float(xs.mean()), float(ys.mean()))
        M = cv2.getRotationMatrix2D(c, ang, 1.0)
        M[:, 2] += (dx, dy)
        alfa = cv2.GaussianBlur(sil.astype(np.float32), (0, 0), 0.5)
        alfa = cv2.warpAffine(alfa, M, (w, h), flags=cv2.INTER_LINEAR)
        img = cv2.warpAffine(antes[wy0:wy1, wx0:wx1].astype(np.float32), M, (w, h), flags=cv2.INTER_LINEAR)
        S = np.float32([[1, 0, s["desloc"][0]], [0, 1, s["desloc"][1]]])
        sb = cv2.GaussianBlur(cv2.warpAffine(alfa, S, (w, h)), (0, 0), s["sigma"]) * (1 - alfa)
        r = out[wy0:wy1, wx0:wx1].astype(np.float32) * (1 - s["forca"] * sb)[..., None]
        a = np.clip(alfa, 0, 1)[..., None]
        out[wy0:wy1, wx0:wx1] = np.clip(r * (1 - a) + img * a, 0, 255).astype(np.uint8)
    print(f"    garagem: {len(silhuetas)} carros com deslocamento e giro leves")
    return out


def carros_r12(out, A, antes, sil):
    """Os carros da R12: o modelo (silhueta do render) na escala de 4,70 x 1,85 m, no centro de cada carro do PDF."""
    q, r = CARROS, CARROS["r12"]
    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0
    _, p2r, _ = pdf_cadeia(A, out.shape)
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                   # 1 m na escala 1:50 = 56,69 pt
    px_m = np.hypot(c - a, d - b)
    ys, xs = np.nonzero(sil)
    y0, y1 = ys.min(), ys.max() + 1
    comp = y1 - y0
    f0, f1 = r["faixa_largura"]
    larguras = sil[int(y0 + f0 * comp):int(y0 + f1 * comp)].sum(axis=1)
    larg = float(np.median(larguras[larguras > 0]))             # a carroceria, sem os retrovisores
    sx, sy = r["largura_m"] * px_m / larg, r["comprimento_m"] * px_m / comp
    cx, cy = float(xs.mean()), (y0 + y1) / 2
    s = q["sombra"]
    alfa0 = cv2.GaussianBlur(sil.astype(np.float32), (0, 0), 0.5)
    img0 = antes[wy0:wy1, wx0:wx1].astype(np.float32)
    for px, py in r["centros_pdf"]:
        tx, ty = p2r(px, py)
        M = np.float32([[sx, 0, tx - wx0 - sx * cx], [0, sy, ty - wy0 - sy * cy]])
        alfa = cv2.warpAffine(alfa0, M, (w, h), flags=cv2.INTER_LINEAR)
        img = cv2.warpAffine(img0, M, (w, h), flags=cv2.INTER_CUBIC)
        S = np.float32([[1, 0, s["desloc"][0]], [0, 1, s["desloc"][1]]])
        sb = cv2.GaussianBlur(cv2.warpAffine(alfa, S, (w, h)), (0, 0), s["sigma"]) * (1 - alfa)
        reg = out[wy0:wy1, wx0:wx1].astype(np.float32) * (1 - s["forca"] * sb)[..., None]
        al = np.clip(alfa, 0, 1)[..., None]
        out[wy0:wy1, wx0:wx1] = np.clip(reg * (1 - al) + img * al, 0, 255).astype(np.uint8)
    print(f"    garagem (R12): {len(r['centros_pdf'])} carros prata iguais, de {r['comprimento_m']:.2f} x "
          f"{r['largura_m']:.2f} m ({comp * sy:.0f} x {larg * sx:.0f} px; modelo de {comp} x {larg:.0f} px), "
          f"alinhados nos centros do PDF")
    return out


# adega (item 27): o U do PDF no quadro do render (de fora, e o vão de dentro) e as garrafas: passo,
# comprimento do corpo e do gargalo, larguras (px) e as cores do vidro (BGR)
ADEGA = {"fora": (1084.6, 388.1, 1154.6, 422.1), "dentro": (1097.0, 400.6, 1142.1, 422.1),
         "fonte_veio": (885, 505, 914, 589), "realce": 1.8,
         "passo": 2.6, "corpo": 6.6, "gargalo": 2.6, "larg": 1.9, "larg_gargalo": 0.8, "folga": 1.0,
         "vidros": [(26, 40, 28), (20, 32, 48), (30, 24, 46), (24, 34, 26), (22, 30, 40)], "brilho": 0.45,
         "sombra": {"desloc": (-0.5, 0.6), "sigma": 0.5, "forca": 0.35}, "semente": 3}


def adega(out, orig):
    q = ADEGA
    forma = out.shape[:2]
    fx0, fy0, fx1, fy1 = q["fora"]
    dx0, dy0, dx1, dy1 = q["dentro"]
    wx0, wy0, wx1, wy1 = int(fx0) - 2, int(fy0) - 2, int(np.ceil(fx1)) + 3, int(np.ceil(fy1)) + 3
    h, w = wy1 - wy0, wx1 - wx0
    U = poligono_aa(forma, [(fx0, fy0), (fx1, fy0), (fx1, fy1), (dx1, fy1), (dx1, dy0), (dx0, dy0), (dx0, fy1),
                            (fx0, fy1)])[wy0:wy1, wx0:wx1]
    # veio: no comprido de cada braço (deitado em cima, em pé nos lados)
    a, b, c, d = q["fonte_veio"]
    Y = orig[b:d, a:c].astype(np.float32).mean(axis=2)
    v = np.clip(1 + q["realce"] * (Y / np.maximum(cv2.GaussianBlur(Y, (0, 0), 3.0), 1) - 1), 0.85, 1.15)

    def ladrilho(g, hh, ww):
        g = np.concatenate([g, g[::-1]] * (hh // (2 * g.shape[0]) + 1), axis=0)[:hh]
        return np.concatenate([g, g[:, ::-1]] * (ww // (2 * g.shape[1]) + 1), axis=1)[:, :ww]

    veio_pe = ladrilho(v, h, w)
    veio_deitado = ladrilho(cv2.rotate(v, cv2.ROTATE_90_CLOCKWISE), h, w)
    yy = wy0 + np.arange(h)[:, None] + 0.5 + np.zeros((1, w))
    g = np.where(yy < dy0, veio_deitado, veio_pe)
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    base = cv2.GaussianBlur(reg, (0, 0), 1.2)
    reg = reg * (1 - U[..., None]) + base * g[..., None] * U[..., None]
    # garrafas: (início no gargalo, junto à parede) -> (fundo, para o vão), em 8 x
    garrafas = []
    p_, cp, gl, f = q["passo"], q["corpo"], q["gargalo"], q["folga"]
    x = fx0 + f + p_ / 2
    while x < fx1 - f:                                    # braço de cima: parede em cima
        garrafas.append(((x, fy0 + 0.3), (0, 1)))
        x += p_
    y = dy0 + f + p_ / 2
    while y < fy1 - f:                                    # braços dos lados: parede do lado de fora
        garrafas.append(((fx0 + 0.3, y), (1, 0)))
        if y < q["fora"][3] - 1.4 - f:
            garrafas.append(((fx1 - 0.3, y), (-1, 0)))
        y += p_
    rng = np.random.default_rng(q["semente"])
    s = q["sombra"]
    for (px, py), (ux, uy) in garrafas:
        cor = np.float32(q["vidros"][int(rng.integers(len(q["vidros"])))])
        nx, ny = -uy, ux
        pts_g = [(px, py), (px + ux * gl, py + uy * gl)]
        pts_c = [(px + ux * (gl + 0.6), py + uy * (gl + 0.6)), (px + ux * (gl + cp), py + uy * (gl + cp))]
        m = np.zeros((h * SS, w * SS), np.uint8)
        for pts, larg in ((pts_g, q["larg_gargalo"]), (pts_c, q["larg"])):
            pp = np.int32(np.round((np.float32(pts) - [wx0, wy0]) * SS))
            cv2.line(m, tuple(pp[0]), tuple(pp[1]), 255, max(1, int(round(larg * SS))), cv2.LINE_AA)
        # ombro: liga gargalo e corpo
        pp = np.int32(np.round((np.float32([pts_g[1], pts_c[0]]) - [wx0, wy0]) * SS))
        cv2.line(m, tuple(pp[0]), tuple(pp[1]), 255, max(1, int(round((q["larg"] + q["larg_gargalo"]) / 2 * SS))), cv2.LINE_AA)
        al = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * U
        sh = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, s["desloc"][0]], [0, 1, s["desloc"][1]]]), (w, h)),
                              (0, 0), s["sigma"]) * (1 - al)
        reg *= (1 - s["forca"] * sh)[..., None]
        reg = reg * (1 - al[..., None]) + cor * al[..., None]
        # brilho no comprido, deslocado para o lado da luz (em cima/direita)
        bm = np.zeros((h * SS, w * SS), np.uint8)
        off = 0.35 * (nx if nx != 0 else 0), 0.35 * (ny if ny != 0 else 0)
        pb = np.int32(np.round((np.float32(pts_c) + [abs(off[0]), -abs(off[1])] - [wx0, wy0]) * SS))
        cv2.line(bm, tuple(pb[0]), tuple(pb[1]), 255, max(1, int(round(0.3 * SS))), cv2.LINE_AA)
        ab = cv2.resize(bm.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None] * q["brilho"] * U[..., None]
        reg = reg * (1 - ab) + (cor * 0.4 + 255 * 0.6) * ab
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    adega: prateleira em U com veio e {len(garrafas)} garrafas deitadas")
    return out


# armário e bancada da área de serviço (item 28): as duas peças do PDF no quadro do render e o quartzo
# limpo da bancada do tanque (nas pontas, fora das cubas)
SERVICO = {"armario": (1084.6, 364.8, 1109.4, 383.5), "bancada": (1109.4, 364.8, 1154.6, 383.5),
           "fontes_quartzo": [(1018, 292, 1027, 313), (1069, 292, 1076, 313)],
           "contorno": (120, 116, 112), "larg_contorno": 0.4}


def servico_bancada(out, orig):
    q = SERVICO
    forma = out.shape[:2]
    # armário: o veio da mesa de jantar, deitado, sobre o tom desfocado da peça
    x0, y0, x1, y1 = q["armario"]
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    a, b, c, d = VEIO_LOUCEIRO["fonte"]
    Y = orig[b:d, a:c].astype(np.float32).mean(axis=2)
    v = np.clip(1 + VEIO_LOUCEIRO["realce"] * (Y / np.maximum(cv2.GaussianBlur(Y, (0, 0), 3.0), 1) - 1), 0.85, 1.15)
    v = cv2.rotate(v, cv2.ROTATE_90_CLOCKWISE)
    h, w = Y1 - Y0, X1 - X0
    v = np.concatenate([v, v[::-1]] * (h // (2 * v.shape[0]) + 1), axis=0)[:h, :w]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])[Y0:Y1, X0:X1, None]
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - al) + cv2.GaussianBlur(reg, (0, 0), 1.2) * v[..., None] * al, 0, 255).astype(np.uint8)
    # bancada: quartzo do tanque, com a luz (por coluna e linha) do próprio trecho de madeira
    x0, y0, x1, y1 = q["bancada"]
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    h, w = Y1 - Y0, X1 - X0
    cor = np.median(np.concatenate([out[b_:d_, a_:c_].reshape(-1, 3) for a_, b_, c_, d_ in q["fontes_quartzo"]]).astype(np.float32), axis=0)
    tex = textura(out, q["fontes_quartzo"], h, w, p=8) * cor
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    lum = reg.mean(axis=2)
    luz = cv2.GaussianBlur(lum, (0, 0), 3.0) / max(float(np.median(lum)), 1)
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])[Y0:Y1, X0:X1, None]
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - al) + tex * np.clip(luz, 0.85, 1.05)[..., None] * al, 0, 255).astype(np.uint8)
    for x0, y0, x1, y1 in (q["armario"], q["bancada"]):
        a_ = linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a_) + np.float32(q["contorno"]) * a_, 0, 255).astype(np.uint8)
    print("    área de serviço: armário com veio e bancada de roupas em quartzo")
    return out


# fileira de baixo da cozinha (item 29): os eletrodomésticos (os quadrados do PDF) e as metades do par
# em inox da cozinha retocada da Casa D; os armários (os trechos dos lados) e o louceiro como fonte
COZINHA = {"inox": [(879.5, 392.8, 904.4, 417.6), (906.3, 392.8, 931.2, 417.6)],
           "fonte_inox": (RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png",
                          [(972, 319, 996, 345), (998, 319, 1022, 345)]),
           "armarios": [(829.7, 394.3, 876.3, 419.2), (932.3, 394.3, 975.1, 419.2)],
           "fonte_armario": (990, 473, 1140, 489),
           "contorno": (70, 72, 74), "larg_contorno": 0.4,
           "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.3}}


def cozinha(out):
    q = COZINHA
    forma = out.shape[:2]
    a, b, c, d = q["fonte_armario"]
    madeira = out[b:d, a:c].copy()
    for i, (x0, y0, x1, y1) in enumerate(q["armarios"]):
        ww = int(round((x1 - x0) * 1.0))
        o_ = 0 if i == 0 else madeira.shape[1] - ww
        out = colar(out, madeira[:, o_:o_ + ww], (x0, y0, x1, y1))
    arq, fontes = q["fonte_inox"]
    casad = cv2.imread(str(arq))
    s = q["sombra"]
    for (x0, y0, x1, y1), (fx0, fy0, fx1, fy1) in zip(q["inox"], fontes):
        out = sombra_curta(out, (x0, y0, x1, y1), s)
        out = colar(out, casad[fy0:fy1, fx0:fx1], (x0, y0, x1, y1))
    for x0, y0, x1, y1 in q["armarios"] + q["inox"]:
        a_ = linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a_) + np.float32(q["contorno"]) * a_, 0, 255).astype(np.uint8)
    print("    cozinha: eletrodomésticos em inox ao centro e armários nas laterais")
    return out


# degrau interno do spa (item 30): o contorno de fora do degrau (PDF) e o perfil das arestas do fundo
# medido no render (fator por px a partir da aresta, para dentro), por lado
SPA = {"fora": (521.8, 593.6, 578.6, 650.5),
       "perfis": {"cima": [0.65, 0.77, 0.80, 0.82, 0.86, 0.92], "baixo": [0.90, 0.95],
                  "esquerda": [0.84, 0.91], "direita": [0.61, 0.70, 0.75, 0.82, 0.86, 0.90]},
       "forca": 0.8}


def degrau_spa(out):
    q = SPA
    x0, y0, x1, y1 = q["fora"]
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32) + 0.5
    k = q["forca"]
    F = np.ones(yy.shape, np.float32)
    for lado, dist in (("cima", yy - y0), ("baixo", y1 - yy), ("esquerda", xx - x0), ("direita", x1 - xx)):
        perfil = np.float32(q["perfis"][lado] + [1.0])
        f = np.interp(dist, np.arange(len(perfil), dtype=np.float32) + 0.5, perfil, left=1.0, right=1.0)
        f = np.where(dist >= 0, f, 1.0)
        F = np.minimum(F, 1 - k * (1 - f))
    dentro = (xx > x0) & (xx < x1) & (yy > y0) & (yy < y1)
    F = np.where(dentro, F, 1.0)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(reg * F[..., None], 0, 255).astype(np.uint8)
    print("    spa: o contorno de fora do degrau interno, com o perfil das arestas do render")
    return out


# vidros da piscina (item 31): as duas folhas do PDF no quadro do render e as cores dos vidros finos
# do Subsolo da Casa D (vidro, linha central, contorno)
VIDROS_PISCINA = {"folhas": [(342.4, 480.1, 345.2, 572.9), (359.5, 480.1, 362.3, 572.9)],
                  "vidro": (222, 218, 210), "linha": (150, 152, 155), "larg_linha": 0.45,
                  "contorno": (70, 72, 74), "larg_contorno": 0.5, "alfa_vidro": 0.85}


def vidros_piscina(out):
    q = VIDROS_PISCINA
    forma = out.shape[:2]
    for x0, y0, x1, y1 in q["folhas"]:
        cantos = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        a = poligono_aa(forma, cantos)[..., None] * q["alfa_vidro"]
        out[:] = np.clip(out * (1 - a) + np.float32(q["vidro"]) * a, 0, 255).astype(np.uint8)
        xc = (x0 + x1) / 2
        a = linha_aa(forma, [(xc, y0), (xc, y1)], q["larg_linha"])[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(q["linha"]) * a, 0, 255).astype(np.uint8)
        a = linha_aa(forma, cantos, q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(q["contorno"]) * a, 0, 255).astype(np.uint8)
    print(f"    piscina: {len(q['folhas'])} folhas de vidro do PDF no lado esquerdo")
    return out


# box do banho gourmet (item 37, R5: "representar o boxe no banho gourmet, pois não está representado"):
# no PDF o box é de correr, com duas folhas de vidro (ARQ_LOUÇAS E METAIS): a fixa, junto à parede de baixo,
# e a de correr, por dentro, sobrepostas no meio; o vão fica em cima. O motor fez só um traço escuro de
# parede a parede, que sai (a coluna vira a do granito 2 px à direita, com a mesma textura). As folhas
# entram no desenho do box da referência (_texturas/elementos.py): linha clara de vidro, fina, sem
# montantes nem pontos, com a borda cinza do lado do chuveiro e a sombra suave no piso do box. Na escala
# do render (0,55 px/pt) o vidro de 1 cm teria 0,3 px: cada folha vai com 0,8 px, no eixo dela.
BOX_GOURMET = {"folhas": [(1104.4, 736.9, 1105.0, 784.1), (1105.3, 725.0, 1105.8, 772.3)],   # pt do PDF
               "traco": (673, 254, 303), "fonte_dx": 2,      # px: coluna e linhas do traço do motor
               "vidro": (226, 229, 230), "larg": 0.8, "borda": (150, 153, 155), "larg_borda": 0.3,
               "sombra": {"dx": -1.2, "sigma": 1.0, "forca": 0.22}}


def box_gourmet(out, A):
    q = BOX_GOURMET
    forma = out.shape[:2]
    x, y0, y1 = q["traco"]
    out[y0:y1, x] = out[y0:y1, x + q["fonte_dx"]]
    _, p2r, _ = pdf_cadeia(A, forma)
    for fx0, fy0, fx1, fy1 in q["folhas"]:
        (a, b), (c, d) = p2r(fx0, fy0), p2r(fx1, fy1)
        xc = (a + c) / 2
        s = q["sombra"]
        sm = cv2.GaussianBlur(linha_aa(forma, [(xc + s["dx"], b), (xc + s["dx"], d)], q["larg"]), (0, 0), s["sigma"])
        out[:] = np.clip(out * (1 - s["forca"] * sm)[..., None], 0, 255).astype(np.uint8)
        al = linha_aa(forma, [(xc, b), (xc, d)], q["larg"])[..., None]
        out[:] = np.clip(out * (1 - al) + np.float32(q["vidro"]) * al, 0, 255).astype(np.uint8)
        xb = xc - q["larg"] / 2
        al = linha_aa(forma, [(xb, b), (xb, d)], q["larg_borda"])[..., None]
        out[:] = np.clip(out * (1 - al) + np.float32(q["borda"]) * al, 0, 255).astype(np.uint8)
    print(f"    banho gourmet: traço do motor apagado; box de correr com {len(q['folhas'])} folhas do PDF")
    return out


# portas sem os arcos (item 38, R3: "Não mostrar arco da porta"). No granito, os arcos eram desenhados pelo próprio
# script (o cinza fino do item 12 e o da folha pequena do hall, item 24): deixam de ser desenhados (ARCOS["desenhar"],
# PORTA_HALL["desenhar_arco"]). No travertino ficam os que o motor fez: saem pelo arcos.remover_arcos (o do Subsolo e
# da Casa A), só nos arcos fora do granito, com as linhas tracejadas do PDF que cruzam o arco protegidas (o X do hall).
# O arco da folha pequena do hall (item 24) era só nosso: fica de fora. Faixa de ±2 px (os arcos aqui são finos).
SEM_ARCOS = {"camada": "ARQ_PAREDE", "fracao_granito": 0.3, "tracejado": "DOC_LINHAS E PROJEÇÕES", "larg_prot": 2,
             "tol": 2.0}


def sem_arcos(out, A):
    from arcos import remover_arcos
    q = SEM_ARCOS
    pg, p2r, _ = pdf_cadeia(A, out.shape)
    gran = granito_render(out.shape[:2], A).astype(bool)

    def fora_do_granito(d):
        c = caixa_render(d, p2r)
        if max(abs(u - v) for u, v in zip(c, PORTA_HALL["arco"])) < 1.0:
            return False
        x0, y0, x1, y1 = (int(round(v)) for v in c)
        g = gran[max(0, y0):y1 + 1, max(0, x0):x1 + 1]
        return g.size > 0 and g.mean() < q["fracao_granito"]
    prot = np.zeros(out.shape[:2], np.uint8)
    for d in pg.get_drawings():
        if d.get("layer") == q["tracejado"]:
            for it in d["items"]:
                if it[0] == "l":
                    a, b = p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)
                    cv2.line(prot, (int(round(a[0])), int(round(a[1]))), (int(round(b[0])), int(round(b[1]))), 1,
                             q["larg_prot"])
    return remover_arcos(out, pg, p2r, camadas=(q["camada"],), tol=q["tol"], so_folha=True, filtro=fora_do_granito,
                         proteger=prot.astype(bool))


# escadas com linhas e o triângulo de orientação (item 39, R14), como no Subsolo da mesma casa e na referência
# (_texturas/elementos.py): em cada bocel uma linha suave (20% mais escura) e, logo depois, a sombra curta no degrau de
# baixo; depois do corte, a escada esmaecida, com os bocéis e o contorno tracejados (a projeção); o triângulo cheio no
# início do percurso, apontando para ele. Geometria do PDF (ARQ_ESCADAS E RAMPAS, pt): a caixa, os bocéis de dentro e
# o corte. Sentidos (usuário): a interna sobe da direita para a esquerda (o "S" do PDF à direita; corte depois do 7º
# degrau, o resto tracejado, como no PDF); a externa do alto desce da esquerda para a direita (usuário, 20/10/26: "pode
# inverter"; ela fica sobre a do Subsolo, que sobe da direita para a esquerda: o mesmo lance, contra o "D" do PDF).
ESCADA_LINHAS = {"bocel": 0.80, "bocel_pt": 0.55, "sombra": (0.16, 5.67), "esmaecer": 0.8,
                 "tracejado": (160, 160, 164), "tracejado_px": 0.5, "traco_pt": 5.7, "vao_pt": 2.8,
                 "triangulo": {"base_pt": 13.6, "altura_pt": 14.7, "recuo_pt": 5.67, "cor": (88, 88, 92)},
                 "escadas": [
                     {"nome": "interna, sobe da direita para a esquerda", "pdf": (1659.2, 1138.5, 1984.0, 1221.4),
                      "bocels": [1677.9 + 17.0 * k for k in range(18)], "baixo": "direita", "inicio": "direita",
                      "corte": [(1840.5, 1138.5), (1859.3, 1176.2), (1863.1, 1183.8), (1882.2, 1222.0)]},
                     {"nome": "externa do alto, desce da esquerda para a direita", "pdf": (972.0, 617.0, 1262.9, 685.0),
                      "bocels": [989.0, 1006.1, 1023.1, 1040.1, 1057.1, 1074.1, 1091.1, 1108.1, 1125.1, 1142.1,
                                 1159.1, 1176.1, 1193.1, 1210.1, 1227.2, 1244.2],
                      "baixo": "direita", "inicio": "esquerda", "corte": None}]}


def escada_linhas(out, A, e):
    q = ESCADA_LINHAS
    _, p2r, _ = pdf_cadeia(A, out.shape)
    ex0, ey0, ex1, ey1 = e["pdf"]
    (a, b), (c, d) = p2r(ex0 - 4, ey0 - 4), p2r(ex1 + 4, ey1 + 4)
    x0, y0, x1, y1 = int(np.floor(a)), int(np.floor(b)), int(np.ceil(c)) + 1, int(np.ceil(d)) + 1
    h, w = y1 - y0, x1 - x0

    def P(x, y):
        u, v = p2r(x, y)
        return (u - x0) * SS, (v - y0) * SS

    def poli(pts):
        m = np.zeros((h * SS, w * SS), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round([P(x, y) for x, y in pts]))], 255)
        return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

    def faixa(fx0, fx1):
        return poli([(fx0, ey0), (fx1, ey0), (fx1, ey1), (fx0, ey1)])
    reg = out[y0:y1, x0:x1].astype(np.float32)
    esc = faixa(ex0, ex1)
    viva = esc if e["corte"] is None else poli(e["corte"] + [(ex1, ey1), (ex1, ey0)])
    bocels = [ex0] + list(e["bocels"]) + [ex1]
    # o lado de baixo de cada bocel (a sombra): à direita se o pé da escada está à direita; nada além do pé
    sinal = 1 if e["baixo"] == "direita" else -1
    pe = ex1 if e["baixo"] == "direita" else ex0
    fator = np.ones((h, w), np.float32)
    forca, alcance = q["sombra"]
    for xb in bocels:
        fator *= 1 - (1 - q["bocel"]) * faixa(xb - q["bocel_pt"] / 2, xb + q["bocel_pt"] / 2)
        if xb == pe:
            continue
        for f in np.linspace(0, 1, 9)[:-1]:
            fa, fb = xb + sinal * alcance * f, xb + sinal * alcance * (f + 1 / 8)
            fator *= 1 - forca * (1 - f - 1 / 16) ** 1.6 * faixa(min(fa, fb), max(fa, fb))
    reg *= (1 - (1 - fator) * viva)[..., None]
    if e["corte"] is not None:
        apos = np.clip(esc - viva, 0, 1)[..., None]
        reg = reg * (1 - apos) + (255 - (255 - reg) * q["esmaecer"]) * apos
        m = np.zeros((h * SS, w * SS), np.uint8)
        lw = max(1, int(round(q["tracejado_px"] * SS)))

        def tracejar(pa, pb):
            comp = np.hypot(pb[0] - pa[0], pb[1] - pa[1])
            t = 0.0
            while t < comp:
                t1 = min(comp, t + q["traco_pt"])
                u = P(pa[0] + (pb[0] - pa[0]) * t / comp, pa[1] + (pb[1] - pa[1]) * t / comp)
                v = P(pa[0] + (pb[0] - pa[0]) * t1 / comp, pa[1] + (pb[1] - pa[1]) * t1 / comp)
                cv2.line(m, (int(round(u[0])), int(round(u[1]))), (int(round(v[0])), int(round(v[1]))), 255, lw,
                         cv2.LINE_AA)
                t = t1 + q["vao_pt"]
        for xb in bocels:
            tracejar((xb, ey0), (xb, ey1))
        tracejar((ex0, ey0), (ex1, ey0))
        tracejar((ex0, ey1), (ex1, ey1))
        tr = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * apos[..., 0]
        reg = reg * (1 - tr[..., None]) + np.float32(q["tracejado"]) * tr[..., None]
    # o triângulo no início do percurso, apontando para o outro lado
    t = q["triangulo"]
    yc = (ey0 + ey1) / 2
    if e["inicio"] == "direita":
        xb, xp = ex1 - t["recuo_pt"], ex1 - t["recuo_pt"] - t["altura_pt"]
    else:
        xb, xp = ex0 + t["recuo_pt"], ex0 + t["recuo_pt"] + t["altura_pt"]
    tri = poli([(xp, yc), (xb, yc - t["base_pt"] / 2), (xb, yc + t["base_pt"] / 2)])
    reg = reg * (1 - tri[..., None]) + np.float32(t["cor"]) * tri[..., None]
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    escada {e['nome']}: {len(bocels) - 1} pisos com os bocéis em linha suave e a sombra curta" +
          ("" if e["corte"] is None else "; depois do corte, esmaecida e tracejada") + "; triângulo no início")
    return out


# grama na escala da referência (item 42, R1 e R4: "representar a escala da madeira conforme modelo referência
# apresentado, bem com o da grama, garantindo textura"). A grama do motor tem grão fino de carpete (o detalhe fino com o
# triplo do da referência) e manchas fora de escala; ela passa ao desenho da grama da biblioteca (_texturas, a da
# planta de referência), na escala do render, com a luz larga do lugar e as sombras das plantas. Tom (usuário,
# 20/10/26, entre as opções A, tom da referência, e B: "OPÇÃO B"): o verde do próprio render. Plantas, pisos e o branco
# de fora do lote ficam (texturas_escala.mascara_grama).
# A cor da grama (cromaticidade) é medida num trecho limpo do gramado ("amostra", px: x0, y0, x1, y1), à esquerda: a
# mediana do gramado inteiro puxa para a das palmeiras e as folhas claras viravam grama.
GRAMA = {"cor_chapada": (0x50, 0x91, 0x6E), "tol": 10, "px_por_m": None, "cor": None, "semente": 5,
         "amostra": (150, 380, 330, 500)}


def grama_referencia(out, A):
    from texturas_escala import mascara_grama, trocar_grama
    q = GRAMA
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    gramado = np.abs(chapada.astype(np.int32) - np.array(q["cor_chapada"])).max(axis=2) <= q["tol"]
    _, p2r, _ = pdf_cadeia(A, out.shape)
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                   # 1 m na escala 1:50 = 56,69 pt
    px_m = q["px_por_m"] or float(np.hypot(c - a, d - b))
    x0, y0, x1, y1 = q["amostra"]
    am = cv2.GaussianBlur(out.astype(np.float32), (0, 0), 1.5)[y0:y1, x0:x1].reshape(-1, 3)
    soma = am.sum(axis=1) + 1
    croma = (float(np.median(am[:, 0] / soma)), float(np.median(am[:, 2] / soma)))
    grama, planta = mascara_grama(out, gramado, croma=croma)
    out, n = trocar_grama(out, grama, px_m, cor=q["cor"], semente=q["semente"])
    print(f"    grama da referência a {px_m:.2f} px/m em {n} px (plantas fora: {int(planta.sum())} px)")
    return out


# Bege Bahia como a referência (item 43, R1; usuário, 20/10/26, no Subsolo: "A REPRESENTAÇÃO DO MARMORE BEGE BAHIA
# CONFORME A REFERENCIA DEFINIDA ESTÁ ADEQUADA?"). No Térreo ele estava rosado e claro (RGB 232, 217, 203; a foto, 230,
# 211, 186), em placas grandes com veios brancos soltos e pontinhos escuros do motor. Como no Subsolo da mesma casa: os
# pontinhos escuros pequenos (até 4 px, 14 abaixo da luz em volta) viram a luz do lugar; depois, o desenho da
# biblioteca entra inteiro, na escala, no tom da foto, com a luz do lugar (as sombras dos móveis ficam). Varanda, deck,
# blocos e degraus da esquerda, pisantes e WC DCE 1 (o #E8E8E8 da base chapada). O travertino fica: é o travertino
# aprovado da casa (o do Subsolo vem dele).
BEGE = {"cor_chapada": (232, 232, 232), "tol": 6, "forca": 1.0, "semente": 1, "sig_m": 0.25, "tom": (186, 211, 230),
        "suavizar": 0.4, "pontos": {"limiar": 14, "area": 10, "lado": 4, "sig": 4.0}}


def bege_referencia(out, A):
    from texturas_escala import retexturizar, nconv
    q = BEGE
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    bege = np.abs(chapada.astype(np.int32) - np.array(q["cor_chapada"])).max(axis=2) <= q["tol"]
    _, p2r, _ = pdf_cadeia(A, out.shape)
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    pq = q["pontos"]
    im = out.astype(np.float32)
    m = cv2.erode(bege.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    L = nconv(im, m.astype(np.float32), pq["sig"])
    n, lab, st, _ = cv2.connectedComponentsWithStats((m & ((L - im).max(axis=2) > pq["limiar"])).astype(np.uint8), 8)
    pontos = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= pq["area"]
                           and max(st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]) <= pq["lado"]])
    pontos = cv2.dilate(pontos.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & m
    out[pontos] = np.clip(L[pontos], 0, 255).astype(np.uint8)
    out, npx = retexturizar(out, bege, "bege_bahia", px_m, forca=q["forca"], semente=q["semente"], sig_m=q["sig_m"],
                            cor=q["tom"], suavizar=q["suavizar"])
    print(f"    Bege Bahia: {int(pontos.sum())} px de pontinhos escuros fora; {npx} px no desenho da biblioteca, "
          f"a {px_m:.2f} px/m, no tom da foto")
    return out


# projeções da cobertura (item 44, R8 e R9; usuário, 20/10/26: "quero que você desenhe um tracejado cinza fino sobre
# essas bordas (pode usar a varanda do primeiro pavimento como referência), inclusive junto aos brises da garagem, para
# marcar a projeção. na garagem tem uma linha no PDF. na varanda, existem os escritos da 'PROJ. COBERTURA' fazendo o
# contorno, passando do espaço gourmet banho do espaço gourmet. essa projeção faz um L"; com duas fotos: a fachada
# posterior, "o L fica na varanda + espaço gourmet", e a frontal, com a garagem). As 7 notas "PROJ. COBERTURA" do PDF
# do Térreo marcam bordas de três coberturas (esquema em renders/POE642_CasaE_PH_Terreo_projecoes_esquema.jpg):
# - o L, a laje baixa do espaço gourmet + varanda (fachada posterior): a borda de cima e a esquerda do gourmet (ARQ_
#   ELEMENTOS FIXOS, do PDF do Térreo), a do topo da piscina até a varanda, a esquerda da varanda e a de baixo, até a
#   fachada da sala (o contorno da varanda do 1º Pavimento, no mesmo quadro, com o dente de 10 cm da suíte 3); os
#   pilares da varanda ficam por dentro (o quarto pilar do PDF, em x = 1421, é o de dentro da sala);
# - a laje da garagem (fachada frontal): a linha do PDF em cima da garagem, a lateral direita junto aos brises e a
#   borda de baixo, voltada para o acesso de veículos;
# - a faixa de cima: a borda de cima da circulação até a garagem.
# Tracejado cinza fino por cima de tudo, menos nas paredes pretas (onde o traço some).
PROJECOES = {"ativo": True,
             "linhas": {"L: laje do espaço gourmet + varanda": [(1372.9, 518.6), (697.6, 518.6), (697.6, 1090.3),
                                                                 (983.4, 1090.3), (983.4, 1694.1), (1204.5, 1694.1),
                                                                 (1204.5, 1688.5), (1380.0, 1688.5)],
                        "laje da garagem": [(1992.5, 687.8), (2763.5, 687.8), (2763.5, 1090.3), (2207.9, 1090.3)],
                        "faixa de cima": [(1372.9, 516.3), (2763.5, 516.3), (2763.5, 687.8)]},
             "traco_pt": 8.5, "vao_pt": 4.25, "larg_px": 0.55, "cor": (150, 151, 150), "forca": 0.85, "parede": 45}


def projecoes(out, A):
    q = PROJECOES
    if not q["ativo"]:
        print("    projeções da cobertura: aguardando a confirmação do esquema (PROJECOES['ativo'])")
        return out
    _, p2r, _ = pdf_cadeia(A, out.shape)
    h, w = out.shape[:2]
    m = np.zeros((h * SS, w * SS), np.uint8)
    lw = max(1, int(round(q["larg_px"] * SS)))
    n = 0
    for pts in q["linhas"].values():
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            comp = np.hypot(bx - ax, by - ay)
            t = 0.0
            while t < comp:
                t1 = min(comp, t + q["traco_pt"])
                u = p2r(ax + (bx - ax) * t / comp, ay + (by - ay) * t / comp)
                v = p2r(ax + (bx - ax) * t1 / comp, ay + (by - ay) * t1 / comp)
                cv2.line(m, (int(round(u[0] * SS)), int(round(u[1] * SS))), (int(round(v[0] * SS)), int(round(v[1] * SS))),
                         255, lw, cv2.LINE_AA)
                n += 1
                t = t1 + q["vao_pt"]
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * q["forca"]
    a *= (out.astype(np.float32).mean(axis=2) >= q["parede"])          # nas paredes pretas o traço some
    out[:] = np.clip(out * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None], 0, 255).astype(np.uint8)
    print(f"    projeções da cobertura: {len(q['linhas'])} linhas, {n} traços")
    return out


# cortinas (item 46; pente fino de 20/10, itens 1 e 2), com a cortina de linho da biblioteca (`_blocos/blocos.py`,
# aprovada em 20/10): o trilho de parede a parede (usuário: "trilhos da cortina tem que ser de fora a fora. somente a
# cortina pode estar a meia distancia, totalmente recolhida ou totalmente fechada"), do lado do vidro, e o pano por dentro.
# - Escritório: no PDF (ARQ_LOUÇAS E METAIS) a cortina é a linha ondulada junto à janela da direita, em dois trechos (a
#   meia distância); o motor fez só tracinhos brancos ali. A faixa dos tracinhos volta ao travertino (as mesmas colunas,
#   do vão entre os dois trechos, espelhado) e os panos entram nos trechos do PDF, com o eixo do tecido na linha do PDF.
# - Living, vidro da esquerda (para a varanda): o PDF não traz cortina; o usuário marcou o vidro inteiro ("Representar a
#   cortina"). Quatro folhas de correr escalonadas (a de baixo chega a x = 1385,9 pt): o trilho logo por dentro delas,
#   da parede de cima até o trilho da fachada de baixo, e o pano fechado no vão todo.
# - Living, fachada de baixo (item 2: "corrija as cortinas aqui também"): no PDF (ARQ_MOBILIÁRIO) dois trechos de linha
#   ondulada (a meia distância); o motor fez um zigue-zague cinza no primeiro e tracinhos no segundo, que saem (as
#   linhas logo acima, espelhadas: o veio do travertino corre na vertical). As quatro folhas de baixo são escalonadas (a
#   da direita sobe até y = 1694,1 pt): o trilho fica logo acima delas (y = 1693,3 pt), do trilho do vidro da varanda
#   até a parede da direita, e o eixo do tecido 1 pt acima da linha do PDF.
# Em cada conjunto, `trilho` é (eixo do tecido, início, fim), em pt: com o vidro à direita ou à esquerda, o eixo é um x e
# o início e o fim são y; com o vidro embaixo ou em cima, o contrário. `panos`: (início, fim) de cada pano.
CORTINAS = {"conjuntos": [
    {"nome": "escritório", "vidro": "direita", "trilho": (2225.0, 1098.8, 1354.0),
     "panos": [(1099.4, 1201.0), (1257.5, 1347.8)]},
    {"nome": "living, vidro da varanda", "vidro": "esquerda", "trilho": (1393.7, 1090.3, 1693.3),
     "panos": [(1091.5, 1685.5)]},
    {"nome": "living, fachada de baixo", "vidro": "baixo", "trilho": (1689.6, 1390.0, 1870.1),
     "panos": [(1397.0, 1560.3), (1702.8, 1869.5)]}],
    "limpar": {"faixa": (1284, 1290), "fonte": (534, 556), "linhas": [(475, 533), (557, 615)], "parede": 60},
    "limpar_faixas": [(828, 925, 798, 802), (1000, 1092, 798, 801)],   # px: x0, x1, y0, y1 (fachada de baixo)
    "px_por_m": 31.09}


def pousar_cortina(out, cor, a, eixo, inicio, k, vidro="direita"):
    """Põe a cortina (horizontal, trilho em cima) com o trilho do lado do vidro: o eixo do tecido em `eixo` (um x, com o
    vidro à direita ou à esquerda; um y, com ele embaixo ou em cima), a partir de `inicio` (px do render, com fração; a
    peça vem a k vezes a escala do render e é reduzida aqui)."""
    if vidro in ("direita", "esquerda"):
        giro = cv2.ROTATE_90_CLOCKWISE if vidro == "direita" else cv2.ROTATE_90_COUNTERCLOCKWISE
        cor, a = cv2.rotate(cor, giro), cv2.rotate(a, giro)
        x_esq, y_cima = eixo * k - a.shape[1] / 2, inicio * k     # o eixo do tecido fica no meio da peça (0,085 m)
    else:
        if vidro == "baixo":
            cor, a = cv2.flip(cor, 0), cv2.flip(a, 0)
        x_esq, y_cima = inicio * k, eixo * k - a.shape[0] / 2
    h, w = a.shape
    X0, Y0 = int(np.floor(x_esq / k)) - 1, int(np.floor(y_cima / k)) - 1
    W, H = w // k + 4, h // k + 4
    dx, dy = int(round(x_esq - X0 * k)), int(round(y_cima - Y0 * k))
    pre = np.zeros((H * k, W * k, 3), np.float32)
    al = np.zeros((H * k, W * k), np.float32)
    pre[dy:dy + h, dx:dx + w] = cor * a[..., None]
    al[dy:dy + h, dx:dx + w] = a
    pre = cv2.resize(pre, (W, H), interpolation=cv2.INTER_AREA)
    al = cv2.resize(al, (W, H), interpolation=cv2.INTER_AREA)
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(pre + reg * (1 - al[..., None]), 0, 255).astype(np.uint8)


def cortinas(out, A):
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = CORTINAS
    _, p2r, _ = pdf_cadeia(A, out.shape)
    lp = q["limpar"]                                              # os tracinhos do motor no escritório
    xa, xb = lp["faixa"]
    ya, yb = lp["fonte"]
    fonte = out[ya:yb, xa:xb].copy()
    tira = np.concatenate([fonte, fonte[::-1]] * 4)
    for r0, r1 in lp["linhas"]:                                   # a parede preta em volta fica
        piso = out[r0:r1, xa:xb].astype(np.float32).mean(axis=2) > lp["parede"]
        out[r0:r1, xa:xb][piso] = tira[:r1 - r0][piso]
    for x0, x1, y0, y1 in q["limpar_faixas"]:                     # zigue-zague e tracinhos da fachada de baixo
        acima = out[y0 - 2:y0, x0:x1].copy()
        espelho = np.concatenate([acima[::-1], acima] * ((y1 - y0) // 4 + 1))
        out[y0:y1, x0:x1] = espelho[:y1 - y0]
    k, px_m = 8, q["px_por_m"]

    def r(eixo, t, vertical):                                    # pt -> px: (eixo, posição ao longo do trilho)
        x, y = p2r(eixo, t) if vertical else p2r(t, eixo)
        return (x, y) if vertical else (y, x)

    for c in q["conjuntos"]:
        vertical = c["vidro"] in ("direita", "esquerda")
        ep, tp0, tp1 = c["trilho"]
        (e, t0), (_, t1) = r(ep, tp0, vertical), r(ep, tp1, vertical)
        cor, a = blocos.cortina((t1 - t0) / px_m, px_m * k, com_pano=False)
        pousar_cortina(out, cor, a, e, t0, k, c["vidro"])
        for pp0, pp1 in c["panos"]:
            (e, t0), (_, t1) = r(ep, pp0, vertical), r(ep, pp1, vertical)
            cor, a = blocos.cortina((t1 - t0) / px_m, px_m * k, com_trilho=False)
            pousar_cortina(out, cor, a, e, t0, k, c["vidro"])
        print(f"    {c['nome']}: trilho de parede a parede e {len(c['panos'])} pano(s) de linho")
    return out


# paisagismo abaixo das escadas (item 32): a grama de referência e os canteiros (fonte; espelhar;
# canto de cima à esquerda no destino; lados em que o trecho corta a touceira), como na Casa D
PAISAGISMO = {
    "grama_ref": (420, 868, 480, 922),
    "canteiros": [((142, 668, 237, 745), True, (300, 786), ("cima", "direita", "esquerda"))],   # sem a pedra (x >= 240)
    "limiar": 2.2, "sigma_densidade": 4.0, "densidade": 0.3,
    "onda": (6.0, 8.0), "suave": 4.0, "semente": 11,
}


def paisagismo(out):
    q = PAISAGISMO
    fonte = out.copy()
    lab = cv2.cvtColor(fonte, cv2.COLOR_BGR2LAB).astype(np.float32)
    gx0, gy0, gx1, gy1 = q["grama_ref"]
    g = lab[gy0:gy1, gx0:gx1].reshape(-1, 3)
    mu, sd = g.mean(axis=0), np.maximum(g.std(axis=0), 1)
    z = np.sqrt((((cv2.GaussianBlur(lab, (0, 0), 1.0) - mu) / sd) ** 2).sum(axis=2))
    grama = cv2.GaussianBlur((z < 3.5).astype(np.float32), (0, 0), 0.6)
    rng = np.random.default_rng(q["semente"])
    for (x0, y0, x1, y1), espelhar, (dx, dy), cortes in q["canteiros"]:
        spr = fonte[y0:y1, x0:x1].astype(np.float32)
        dens = cv2.GaussianBlur((z[y0:y1, x0:x1] > q["limiar"]).astype(np.float32), (0, 0), q["sigma_densidade"])
        m = (dens > q["densidade"]).astype(np.uint8)
        cont, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        m = np.zeros_like(m)
        cv2.drawContours(m, cont, -1, 1, -1)
        a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)
        if espelhar:
            spr, a = spr[:, ::-1], a[:, ::-1]
        h, w = a.shape
        amp, esc = q["onda"]
        for lado in cortes:
            n = w if lado in ("cima", "baixo") else h
            onda = cv2.GaussianBlur(rng.normal(0, 1, (1, n + 40)).astype(np.float32), (0, 0), esc)[0, 20:20 + n]
            onda = amp * (1 + onda / max(float(np.abs(onda).max()), 1e-6))
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            dist = {"cima": yy, "baixo": h - 1 - yy, "esquerda": xx, "direita": w - 1 - xx}[lado]
            off = onda[None, :] if lado in ("cima", "baixo") else onda[:, None]
            a = a * np.clip((dist - off) / q["suave"], 0, 1)
        a = a * grama[dy:dy + h, dx:dx + w]
        reg = out[dy:dy + h, dx:dx + w].astype(np.float32)
        out[dy:dy + h, dx:dx + w] = np.clip(reg * (1 - a[..., None]) + spr * a[..., None], 0, 255).astype(np.uint8)
        print(f"    canteiro em ({dx}, {dy}), {w}x{h} px, da touceira em ({x0}, {y0})")
    return out


# banco de madeira sem encosto (item 34): o retângulo do PDF, o encosto do motor (com a sombra) e o
# Bege Bahia limpo da varanda
BANCO_VARANDA = {"banco": (708.0, 746.4, 776.4, 765.0), "encosto": (700, 764, 782, 779),
                 "janela": (690, 755, 795, 790), "fontes": [(700, 778, 786, 812), (530, 700, 600, 760)],
                 "fonte_madeira": (885, 505, 914, 589), "ripas": 4, "junta": (70, 92, 118), "larg_junta": 0.35,
                 "forca_junta": 0.45, "contorno": (60, 72, 88), "larg_contorno": 0.45,
                 "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.35}}


def banco_varanda(out, orig):
    q = BANCO_VARANDA
    wx0, wy0, wx1, wy1 = q["janela"]
    bx0, by0, bx1, by1 = q["banco"]
    ex0, ey0, ex1, ey1 = q["encosto"]
    m = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    m[ey0 - wy0:ey1 - wy0, ex0 - wx0:ex1 - wx0] = True
    m[:int(np.ceil(by1)) - wy0, int(bx0) - wx0:int(np.ceil(bx1)) - wx0] = False      # o banco fica
    out = apagar_largo(out, q["janela"], m, q["fontes"], sigma=4.0, borda=0.6, lum_min=185, lum_max=228,
                       escuros=True)
    out = sombra_curta(out, q["banco"], q["sombra"])
    a, b, c, d = q["fonte_madeira"]
    madeira = cv2.rotate(orig[b:d, a:c], cv2.ROTATE_90_CLOCKWISE)          # veio no comprido (em x)
    hh, ww = int(np.ceil(by1 - by0)), int(np.ceil(bx1 - bx0))
    out = colar(out, madeira[:hh, :ww], q["banco"])
    forma = out.shape[:2]
    n = q["ripas"]
    for k in range(1, n):
        y = by0 + k * (by1 - by0) / n
        a_ = linha_aa(forma, [(bx0, y), (bx1, y)], q["larg_junta"])[..., None] * q["forca_junta"]
        out[:] = np.clip(out * (1 - a_) + np.float32(q["junta"]) * a_, 0, 255).astype(np.uint8)
    a_ = linha_aa(forma, [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], q["larg_contorno"], fechada=True)[..., None]
    out[:] = np.clip(out * (1 - a_) + np.float32(q["contorno"]) * a_, 0, 255).astype(np.uint8)
    print(f"    estar da varanda: banco de madeira em {n} ripas, sem encosto")
    return out


# Barlavento nas piscinas (item 35): a água na base chapada (#DFF6FE), a janela das piscinas, a cor da
# água sobre a pedra (BGR) e quanto do reflexo do motor fica
PISCINAS = {"janela": (330, 460, 625, 685), "agua_base": (254, 246, 223), "tol": 10, "area_min": 200,
            "cor": (214, 222, 172), "semente": 642,
            # luz chapada (sem as manchas escuras do motor, pedido do usuário); só uma sombra curta e
            # leve junto às bordas, para ler a profundidade
            "borda": (0.12, 1.6),
            # degrau entre a piscina e a prainha (ARQ_CONTRAPISO, x = 510,4): a mesma sombra curta do
            # lado fundo (à esquerda) e um fio de luz na quina
            "degraus": [(510.4, 480.1, 572.9)], "quina": 0.05,
            # efeitos da água (pedido do usuário: sem eles parecia vazia): a grade das peças ondulada
            # pela refração (deslocamento suave, em px), a rede de cáusticas do próprio render, mais
            # suave (só clareia) e um brilho difuso na diagonal da superfície
            "ondas": (1.0, 5.0), "causticas": 1.2, "suave_causticas": 0.6, "brilho": 0.04}


def piscinas(out, A):
    q = PISCINAS
    wx0, wy0, wx1, wy1 = q["janela"]
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), out.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    chapada = cv2.warpAffine(chapada, A, out.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))
    ch = chapada[wy0:wy1, wx0:wx1].astype(np.int32)
    agua = (np.abs(ch - np.array(q["agua_base"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(agua)
    agua = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    ciano = (reg[..., 0] - reg[..., 2] > 20) & (reg[..., 1] - reg[..., 2] > 20)
    perto = cv2.dilate(agua.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    m = agua | (perto & ciano)                       # as linhas finas do PDF dentro da água entram
    Y = reg.mean(axis=2)
    w = m.astype(np.float32)

    def media(s):
        return cv2.GaussianBlur(Y * w, (0, 0), s) / np.maximum(cv2.GaussianBlur(w, (0, 0), s), 1e-3)

    forca, dec = q["borda"]
    dist = cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 3)
    luz = 1 - forca * np.exp(-np.maximum(dist - 0.5, 0) / dec)
    yy, xx = np.mgrid[wy0:wy1, wx0:wx1].astype(np.float32) + 0.5
    for xd, ya, yb in q["degraus"]:
        faixa = (yy >= ya) & (yy <= yb)
        d = xd - xx
        luz *= np.where(faixa & (d > 0), 1 - forca * np.exp(-d / dec), 1.0)
        luz *= np.where(faixa & (d <= 0) & (d > -1.0), 1 + q["quina"], 1.0)
    h, wd = Y.shape
    pedra = barlavento(h + 8, wd + 8, semente=q["semente"]) * np.float32(q["cor"])
    # refração: a grade vista através da água ondula (deslocamento suave e pequeno)
    rng = np.random.default_rng(q["semente"])
    amp, sig = q["ondas"]
    dx, dy = (cv2.GaussianBlur(rng.normal(0, 1, (h, wd)).astype(np.float32), (0, 0), sig) for _ in range(2))
    dx, dy = dx * amp / max(float(dx.std()), 1e-6), dy * amp / max(float(dy.std()), 1e-6)
    gy, gx = np.mgrid[0:h, 0:wd].astype(np.float32)
    pedra = cv2.remap(pedra, gx + 4 + dx, gy + 4 + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # cáusticas: a rede de luz do render (só o que é mais claro que a média local), suavizada
    caust = cv2.GaussianBlur(np.clip(Y - media(4.0), 0, None), (0, 0), q["suave_causticas"]) * q["causticas"]
    # brilho difuso: mais claro no canto de cima à esquerda, caindo na diagonal
    diag = ((gx / max(wd - 1, 1)) + (gy / max(h - 1, 1))) / 2
    brilho = 1 + q["brilho"] * (1 - diag)
    novo = pedra * (luz * brilho)[..., None] + caust[..., None] * np.float32([1.0, 1.0, 0.92])
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5)
    a = np.maximum(a, m)[..., None]
    out[wy0:wy1, wx0:wx1] = np.clip(reg * (1 - a) + novo * a, 0, 255).astype(np.uint8)
    print(f"    piscinas: Barlavento Caribbean em {int(m.sum())} px de água")
    return out


# 36. Nomes e áreas dos ambientes (pedido do usuário, 16/10/26: "vamos voltar no térreo da Casa E e adicionar
# os rótulos com área. seguindo o padrão que determinamos"). A regra do 1º Pavimento e do Subsolo
# (`retoque_1pav_casae.rotulos_ambientes`): cada linha do rótulo do PDF entra igual (o nome e "A: 16,63 m²"),
# na posição do PDF, no corpo do PDF 30% maior, em Inter Regular preta; no granito marrom, cinza (150); os
# que caem sobre móvel vão ao piso livre mais próximo. São escritos na imagem final (3840 px): o retocado
# levado ao quadro comum, como na prancha. O retocado de 2000 px fica sem rótulos (é o contexto do 1º
# Pavimento na opção P&B). Ficam fora as notas "PROJ. COBERTURA" (projeção da cobertura, não são ambientes)
# e o título da folha ("0. TÉRREO").
ROTULOS = {"fora": ("PROJ.", "TÉRREO"),
           # (nome, centro do rótulo do PDF no quadro final em px de 2000, desvio em px de 2000[, opções]);
           # os que caem sobre móvel ou peça vão ao piso livre mais próximo
           "ajustes": [("GARAGEM", (1420.5, 323.9), (0, 123)),          # sobre o carro do meio: abaixo dos carros
                       ("VARANDA", (715.5, 609.3), (0, 18)),           # nas cadeiras da mesa: abaixo delas
                       ("DCE", (1202.4, 293.6), (0, 3)),               # encostado na cama: um pouco abaixo
                       ("ÁREA DE SERVIÇO", (1094.2, 324.9), (0, 2)),   # encostado nas máquinas
                       ("COZINHA", (915.6, 372.8), (0, 2)),            # encostado nos bancos da ilha
                       ("CIRCULAÇÃO", (1170.6, 601.3), (-3, 0)),       # encostado na parede do escritório
                       # o "1" caía no chuveiro e o 1,3x não cabe no piso livre do box: corpo do PDF, à esquerda
                       ("WC DCE 1", (1261.6, 271.3), (-2, 0), 1.0),
                       # o lavabo é uma faixa estreita entre o banco e a parede: o nome em duas linhas, no meio dela
                       ("LAVABO GOURMET", (552.4, 291.3), (-5.5, 0), {"quebra": ["LAVABO", "GOURMET"]}),
                       # o jardim interno é todo planta: no verde escuro o preto e o cinza somem; fica em branco
                       ("JARDIM", (1059.5, 562.8), (0, 0), {"cor": (250, 250, 250)})]}
FINAL = {"largura": 3840}


def final_rotulos(out, referencia=None):
    from PIL import Image
    import retoque_1pav_casae as R1
    from opcoes_1pav_casae import quadro_pdf
    from rodape_entrega import no_quadro_comum
    q = ROTULOS
    W = FINAL["largura"]
    ref = None if referencia is None else Image.fromarray(cv2.cvtColor(referencia, cv2.COLOR_BGR2RGB))
    final = cv2.cvtColor(np.asarray(no_quadro_comum(Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)), BASE,
                                                    "Terreo", W, referencia=ref)), cv2.COLOR_RGB2BGR)
    H = final.shape[0]
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Terreo"]["pagina"]]
    at, lt = cv2.imread(str(BASE), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg, cfg, lt, at, wb, hb, W)
    rot = [r for r in R1.rotulos_pdf(pg) if not any(f in r[0] for f in q["fora"])]
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), (W, H), interpolation=cv2.INTER_NEAREST)
    granito = np.abs(chapada.astype(int) - np.array(ARCOS["granito"])).max(axis=2) <= 6
    print(f"    {len(rot)} rótulos: " + ", ".join(r[0] for r in rot))
    # R6 (19/10/26): "Apresentar os rótulos em branco quando for piso marrom granito"
    return R1.rotulos_ambientes(final, rot, p2q, escala_desvio=W / 2000, granito=granito, ajustes=q["ajustes"],
                                cor_granito=R1.ROTULOS["branco"])


def salvar_final(out, saida, nome, referencia=None):
    print("[36] imagem final no quadro comum, com os nomes e áreas dos ambientes")
    final = final_rotulos(out, referencia)
    saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(saida / f"{nome}.png"), final)
    cv2.imwrite(str(saida / f"{nome}_preview.jpg"),
                cv2.resize(final, (2000, round(2000 * final.shape[0] / final.shape[1])), interpolation=cv2.INTER_AREA),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {saida / (nome + '.png')} {final.shape[1]}x{final.shape[0]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    ap.add_argument("--so-final", action="store_true",
                    help="o render dado já é o retocado: só a imagem final com os rótulos (gravada em --nome)")
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    if args.so_final:
        salvar_final(orig, args.saida, args.nome)
        return
    out = orig.copy()
    A, base = alinhar_base(orig)
    print("[1, 2] lote: vegetação fora do lote, linhas tracejadas e faixa à direita dos pisantes")
    out = lote(out, base)
    print("[3] jardim interno: plantas só na floreira")
    out = jardim_interno(out)
    print("[4] tapete do estar da varanda no contorno orgânico do PDF")
    out = tapete(out, A)
    print("[20] estar da varanda: sem tapete")
    out = sem_tapete(out, A)
    print("[5] varanda: as quatro barras a 45° do PDF")
    out = barras(out, A)
    print("[6] elevador: cabine ocupando a caixa")
    out = elevador(out)
    print("[7] CPD: vaso inventado")
    out = vaso_cpd(out)
    print("[8] área de serviço: as duas máquinas")
    out = maquinas(out)
    print("[9] área de serviço descoberta: X tracejado")
    out = x_descoberta(out, A)
    print("[10] DCE: cama, criado-mudo e armário até o teto")
    out = dce(out)
    print("[11] WC DCE 1: vaso a mais no lugar do chuveiro")
    out = wc_dce(out)
    print("[12] arcos das portas sobre o granito")
    out = arcos_granito(out, A)
    print("[13] pontos claros do granito")
    out = pontos_granito(out, orig, A)
    print("[14] pilar à direita do lavabo")
    out = pilar(out)
    print("[15] lavabo: cuba esculpida, torneira da esquerda")
    out = lavabo(out)
    print("[16] escritório: arranjo de flores")
    out = arranjo(out, orig)
    print("[17] louceiro: veio de marcenaria")
    out = veio_louceiro(out, orig)
    print("[18, 21] escadas: só sombreamento, sem linhas")
    for q in ESCADAS:
        out = escada(out, q)
    print("[22] vaso do banho gourmet com tampo")
    out = vasos(out, A)
    print("[23] banho gourmet: bancada da pia e torneira")
    out = bancada_gourmet(out)
    print("[24] porta do hall externo: extensão e arco")
    out = porta_hall(out, A)
    print("[25] brises de madeira na janela do escritório")
    out = brises(out, orig, A)
    print("[26] carros levemente desalinhados")
    out = carros(out, A)
    print("[27] adega: prateleira de vinhos em U")
    out = adega(out, orig)
    print("[28] área de serviço: armário e bancada para roupas")
    out = servico_bancada(out, orig)
    print("[29] cozinha: inox ao centro, armários nas laterais")
    out = cozinha(out)
    print("[35] piscinas: revestimento Barlavento")
    out = piscinas(out, A)
    print("[30] spa: degrau interno")
    out = degrau_spa(out)
    print("[31] piscina: duas folhas de vidro")
    out = vidros_piscina(out)
    print("[32] paisagismo abaixo das escadas")
    out = paisagismo(out)
    print("[33] brises da lateral direita da garagem")
    out = brises(out, orig, A, BRISES_GARAGEM)
    print("[34] estar da varanda: banco de madeira sem encosto")
    out = banco_varanda(out, orig)
    print("[19] jardim de inverno: um pouco para fora, com flores")
    out = jardim_flores(out, orig)
    # o alinhamento da imagem final é medido no retocado aprovado (itens 1 a 35, APROVADO): os itens das regras
    # novas (19 e 20/10) não mudam o afim, e o resto da imagem final fica igual, px a px
    aprovado = cv2.imread(str(APROVADO))
    print("[37] banho gourmet: box de vidro de correr (R5)")
    out = box_gourmet(out, A)
    print("[38] portas sem os arcos (R3): no granito, o item 12 já não os desenha; no travertino, os do motor saem")
    out = sem_arcos(out, A)
    print("[39] escadas com linhas e o triângulo de orientação (R14)")
    for e in ESCADA_LINHAS["escadas"]:
        out = escada_linhas(out, A, e)
    print("[42] grama na escala da referência (R1, R4), no tom do render")
    out = grama_referencia(out, A)
    print("[43] Bege Bahia como a referência (R1)")
    out = bege_referencia(out, A)
    print("[44] projeções da cobertura em tracejado cinza fino (R8, R9)")
    out = projecoes(out, A)
    print("[46] cortinas de linho: escritório e living (pente fino, itens 1 e 2)")
    out = cortinas(out, A)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")
    salvar_final(out, args.saida, args.nome.replace("_retocado", "_final"), referencia=aprovado)


if __name__ == "__main__":
    main()

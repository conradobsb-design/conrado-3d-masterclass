#!/usr/bin/env python3
"""Ajustes, sem IA, das imagens aprovadas da Casa A (POE 642) depois da conferência com o PDF da Casa A.

A conferência (`conferencia_casaa.py`, mapas `renders/POE642_CasaA_PH_<Pavimento>_conferencia.jpg`) listou as
divergências entre as imagens aprovadas e os PDFs do cliente da Casa A. Cada item corrigido entra aqui, um por
vez, no quadro da imagem aprovada (2000 px). A saída é `renders/<imagem aprovada>_ajustes.png`, que é a que vai
aos nomes e áreas (`rotulos_casaa.py`), às pranchas e ao PDF.

Itens:
  Subsolo 1. Banho de serviço (pedido do usuário, 19/10/26): o chuveiro e as duas folhas de vidro do box, do PDF,
     como os aprovados da Casa E.
  Subsolo 2. Sauna (pedido do usuário, 19/10/26: "Eu quero que você traga esse banco de volta"). O banco do PDF
     é horizontal, ao longo da parede de baixo, de parede a parede; a faixa vertical à esquerda, no tom do piso
     da piscina, é a passagem da sauna para a piscina e fica como piso ("o banco não é em L"). Na v6 o banco
     tinha virado piso: sobrou só uma faixa um pouco mais clara, sem a borda. Ele volta como o banco aprovado
     da sauna da Casa E: o travertino da própria faixa, a borda marcada por uma linha fina, uma sombra discreta
     no piso, que é mais baixo, e um brilho leve na quina do banco.
  Subsolo 3. Escada que desce do deck (pedido do usuário, 19/10/26): depois da linha de corte do PDF (a
     diagonal, que não é desenhada), os degraus no travertino do Subsolo, visíveis; antes dela, esmaecidos.
  Subsolo 4. Portas de vidro da academia (pedido do usuário, 19/10/26): para a circulação e para o hall, as
     folhas de vidro do PDF, claras e finas como o vidro da sauna, no lugar do traço preto do motor.
  Subsolo 5. Janelas (pedido do usuário, 19/10/26): a do banho de serviço e a da circulação para o depósito, na
     geometria do PDF (peitoril, faces da parede, vidro, caixilhos e retornos), no lugar da peça cinza do motor.
  Subsolo 6. Circulação (pedido do usuário, 19/10/26): sai o traço preto ao longo da borda esquerda, que o PDF
     não tem.
  Subsolo 7. Depósito e circulação interna (pedido do usuário, 19/10/26): o piso sem as juntas das placas, contínuo,
     com a textura do próprio render, na luz dele.
  Subsolo 8. Banhos feminino e masculino (pedido do usuário, 19/10/26): as cubas no tamanho do PDF (calhas quase da
     largura da bancada), como as cubas aprovadas da Casa E.
  Subsolo 9. Boxes dos chuveiros (pedido do usuário, 19/10/26): na ducha ao lado da sauna e no banho feminino, as
     folhas de vidro de correr do PDF, como as do box do banho de serviço.
  Subsolo 10. Divisória entre os banhos feminino e masculino (pedido do usuário, 19/10/26): não é parede; entra como
     no PDF (camada das bancadas), peça clara no tom das bancadas, com as peças finas em cinza.
  Subsolo 11. Bege Bahia (pedido do usuário, 19/10/26): a área de circulação (era travertino), o depósito e a
     circulação interna no Bege Bahia aprovado (o do 1º Pavimento, que foi ao Térreo), com a sombra do render; a
     escada do deck tira dele a textura do degrau.
  Subsolo 12. Banho de serviço (pedido do usuário, 19/10/26): a bancada da pia e a cuba, nas medidas do PDF, no
     padrão das cubas aprovadas.
  Subsolo 13. Escada do deck (pedido do usuário, 19/10/26): abaixo dela, entre o deck e a circulação, o gramado do
     Térreo, no lugar do branco (pente fino 2, 21/10/26: o do Térreo com os ajustes, na grama da referência).
  Térreo 1. Pilares (pedido do usuário, 19/10/26): os três redondos da varanda e o quadrado junto ao gourmet,
     em marrom no render, no preto das paredes e na geometria do PDF, como o pilar do Térreo da Casa E.
  Térreo 2. Sala de estar (pedido do usuário, 19/10/26): o sofá curvo do PDF acompanhando o tapete pela esquerda,
     com as almofadas, a poltrona da direita e a mesinha na ponta do sofá (clones do render).
  Térreo, rejuntes (pedido do usuário, 19/10/26): o travertino do piso interno contínuo, sem as juntas nem os
     degraus de tom das placas, com a textura e a luz do próprio render.
  Térreo 8. Jardim de 4,79 m² (pedido do usuário, 19/10/26): verde, com o gramado do Térreo e as três touceiras do
     PDF (clones da palmeira em estrela do jardim lateral do render).
  Térreo, tanques (pedido do usuário, 19/10/26): na área de serviço, a bancada com os dois tanques de louça e as
     torneiras de parede, nas medidas do PDF.
  Térreo, gás (pedidos do usuário, 19/10/26): o piso em granito marrom e a porta de duas folhas com os arcos.
  Térreo, porta do jardim (pedido do usuário, 19/10/26): a folha e o arco da porta do jardim para a área descoberta.
  Térreo, portões (pedido do usuário, 19/10/26): os portões de correr dos dois lados da área descoberta, do PDF.
  Térreo 9. Escada caracol (pedido do usuário, 19/10/26): os degraus 1 a 7, até o corte, cheios, em madeira, com o
     corrimão; o resto esmaecido.
  Térreo, portas no granito (pedidos do usuário, 19/10/26): as quatro portas de giro sobre o granito com a folha do
     PDF e o arco em cinza fino, como de regra.
  Térreo, eletrodomésticos (pedido do usuário, 19/10/26): os quadrados do PDF da cozinha, do gourmet e da área de
     serviço com o inox aprovado da Casa D.
  Térreo, bancada gourmet (pedido do usuário, 19/10/26): a área molhada e a divisória do PDF em traço fino, a cuba em
     inox e a torneira gourmet, no lugar das duas caixas do motor.
  Térreo, bancada da cozinha (pedido do usuário, 19/10/26): em quartzo com o desenho de pedra, com a área molhada, as
     duas cubas em inox e as torneiras do PDF.
  Térreo 3. Estar sob a projeção (pedido do usuário, 19/10/26): no lugar da mesa de jantar do motor, as 4 poltronas em
     X e a mesa triangular do PDF, com o X tracejado por cima.
  Térreo 5. Lavabo (pedido do usuário, 19/10/26): bancada de quartzo com a cuba esculpida e a torneira, o vaso
     suspenso e o tracejado da claraboia, nas medidas do PDF.
  Térreo, porta pivotante (pedido do usuário, 19/10/26): a folha até a ponta do PDF, no hall externo, e o arco
     pequeno do lado de lá.
  Térreo, escada interna (pedido do usuário, 19/10/26): os degraus 1 a 7 cheios até a linha de corte, com o
     sombreamento de subida, sem linhas; do 8º em diante esmaecida; o jardim em volta no gramado aprovado.
  Térreo 11 e 12. Motorista (pedido do usuário, 19/10/26): a cama de solteiro, a bancada com a cuba de apoio e a
     torneira, as folhas de vidro do box e o chuveiro, no lugar dos blocos lilás do motor.
  Térreo, carros (pedido do usuário, 19/10/26): cada carro numa cor (branco perolado, grafite, azul-marinho, a
     paleta da Casa D) e os três levemente desalinhados, como na Casa E.
  Térreo, sem arcos (decisão do usuário, 19/10/26, com as plantas de referência dos elementos: "remover os arcos,
     escadas com linhas"): os arcos de todas as portas saem (os do motor e os desenhados nos itens acima); as folhas
     ficam. Na porta camarão da varanda, sai também o cinza que o motor pôs entre cada folha e o arco.

Pente fino pelas regras (POE642_REGRAS.md; mapas do conferencia_casaa.py --pente-fino; usuário, 21/10/26: "confirmado,
pode seguir pela ordem proposta"):
  Térreo 1. Escadas com linhas e triângulo (R14, seção 5): a interna em U e a caracol com a linha suave nos bocéis dos
     degraus cheios, os esmaecidos tracejados, sem a linha de corte e com o triângulo no degrau 1; a do deck para o
     Subsolo sem os traços escuros do motor, viva até o corte e esmaecida depois, com o triângulo de descida no topo; a
     larga, do deck ao pátio, com o bocel de cada bloco e o triângulo no degrau 12.
  Térreo 4. Projeções (R8, R9): a da cobertura (o L da laje, na ARQ_CONTRAPISO) e a da laje superior (na área de
     serviço) em tracejado cinza fino, por cima de tudo menos das paredes, como na Casa E.
  Térreo 5. Vidros finos (seções 4 e 18): entre a varanda e as salas, as quatro portas de correr do PDF, em dois planos,
     no lugar do tubo cinza com montantes; no vão da pivotante do hall, o tubo sai e o piso continua.
  Térreo 3. Carros (R12): prata, alinhados e iguais, de 4,70 x 1,85 m, no lugar das três cores e do desalinhamento
     de 19/10; o modelo é o carro branco do render, levado ao prata do carro da Casa E.
  Térreo 6. Armários até o teto (seção 7): os quatro do PDF (cozinha, área de serviço, motorista) na marcenaria
     areia com veio dos armários da Casa D, sem a diagonal e sem a sombra de móvel baixo no granito, com o contorno
     fino nas faces livres; o braço da bancada dos tanques, que também estava lilás, em quartzo.
  Térreo 7. Grama na escala da referência (R1, R4), no tom do render, como o item 42 do Térreo da Casa E: o gramado é
     o branco da base dentro do lote; as plantas e os tracejados do motor (afastamento, cobertura) ficam; o jardim
     interno da escada também.
  Térreo 8. Deck na madeira da referência (R4): régua a régua, das réguas da foto (~20 cm, a escala do render já
     batia), no tom dela, com a luz e as sombras do lugar.
  Térreo 9. Bege Bahia como a referência (o desenho e o tom da foto, na escala), como o item 43 da Casa E: entorno
     da piscina, pátio, hall externo, pisantes e degraus das escadas externas.
  Térreo 10. Granito marrom no desenho e no tom da referência do usuário, pela rotina do granito do Térreo da Casa
     E (pontos claros e a grade de manchas fora); os rótulos sobre ele seguem brancos (limite de luz do Térreo, 125).
  Térreo 11. Pedra portuguesa em leque, no tom da foto (o item 47 da Casa E), onde ainda é o caramelo do motor, com as
     linhas da DOC_LINHAS do PDF por cima; redesenhada na final de 3840 px pelo rotulos_casaa.py (pedra_final).
  Térreo 12. Vegetação da biblioteca no tamanho real, só dentro do lote (a opção A do item 53 da Casa E): as folhas
     do motor que passavam do lote e sobre os pisos saem (o material da base ao lado, o branco de fora, o perfil do
     muro), a grama do item 7 entra sob as manchas e as plantas da referência, com a copa dentro do verde.
  Térreo 13. Mesa de jantar oval (item 4 da conferência de 19/10): o tampo no contorno do PDF (3,00 x 1,20 m), com a
     madeira do render; as 8 cadeiras do render ficam; a sombra curta acompanha o contorno novo.
  Térreo 14. Escritório (item 6 da conferência de 19/10): as duas cadeiras do motor em cima da mesa saem e entra a
     cadeira de escritório do PDF, em grafite, com o assento sob o tampo; as duas de visita, embaixo, ficam.
  Térreo 15. Banho da varanda (item 7 da conferência de 19/10): a bacia e a faixa pontilhada do motor saem; entram o
     chuveiro de parede e as duas folhas de vidro do box do PDF, como no banho de serviço do Subsolo.
  Térreo 16. Soleiras (R13): nos quatro vãos brancos do PDF (escritório, lavabo, gás e jardim), Bege Bahia na escala
     com as faces da parede em cinza fino; nas outras nove portas o piso atravessa o vão, e nada muda.
  Subsolo, pente fino 1 (R2): só o Subsolo (os pisos e as paredes do PDF, a escada do deck e o gramado); o Térreo em
     volta sai, e a pegada vai para uma máscara; na final, o rotulos_casaa.py hachura o lote do Térreo final fora dela.
  Subsolo, pente fino 2: o gramado abaixo da escada do deck na grama da referência (do Térreo com os ajustes).
  Subsolo, pente fino 3 (R14): a escada do deck com a linha suave e a sombra curta nos bocéis, o trecho depois do corte
     esmaecido e tracejado e o triângulo no 1º degrau, apontando para a subida.
  Subsolo, pente fino 4 (R3): os 5 arcos de porta saem (o traço do arco do PDF, por inpaint); as folhas ficam.
  Subsolo, pente fino 5: a porta de correr da circulação em duas folhas de vidro desencontradas (sem o traço preto),
     as 5 folhas de giro brancas e finas (R3), a janela entre o depósito e a academia em vidro claro e o vidro de
     cima da sauna em folha contínua, sem o montante (seção 18).
  Subsolo, pente fino 6: o Bege Bahia da circulação externa, da interna e do depósito no desenho da biblioteca, na
     escala, e no tom da foto (RGB 230, 211, 186), com a luz do lugar, pela rotina do item 9 do Térreo.
  Subsolo, pente fino 7: o travertino aprovado do Térreo (veio horizontal, sem rejuntes), na escala, no hall, na
     sauna com a antessala e nos banhos, com a luz do lugar; os objetos ficam, e os boxes e o banco são redesenhados.
  Subsolo, pente fino 8 (R8): os dois shafts brancos, com o X tracejado do PDF em cinza médio, e os três retângulos
     da DOC_LINHAS E PROJEÇÕES (depósito e academia) em traço cinza fino.
  Subsolo, pente fino 9 (R13): soleiras de Bege Bahia nos dois vãos brancos do PDF (academia para o hall, com as
     folhas de vidro por cima, e elevador); nas outras portas o piso atravessa o vão.
  1º Pavimento (pente fino pelas regras, 21/10/26): a imagem aprovada é a v7_final2, com o afim do quadro AFIM_QR
     medido como o dos outros (107 pontos, 0,4 px); o item 16 (o "²" dos rótulos) é só o ciclo.
  1º Pavimento, pente fino 1 (seção 11): a pegada do pavimento (pelo render: o que tem cor cheia, fechado e sem furos)
     vai à máscara, e fora dela, branco; na final, o Térreo final sem rótulos entra nublado em volta (rotulos_casaa).
  1º Pavimento, pente fino 2 (R3): os 11 arcos do PDF saem como os do Subsolo, sem puxar a parede, as linhas retas
     nem o piso mais claro ao lado; uma segunda passada tira o arco do render fora do lugar do PDF (e o toco que chega
     à ponta da folha), com as folhas, os batentes e a borda das bancadas intactos. O Subsolo sai igual px a px.
  1º Pavimento, pente fino 3 (R14 e seção 5): a escada em U (desce daqui, inteira) no travertino da escada do Térreo,
     com a linha suave e a sombra curta em cada bocel e o triângulo no degrau 19, para a descida; na caracol da saleta,
     o trecho cheio com os bocéis suaves e o triângulo no degrau do "D" (sentido horário), o resto em branco com os
     bocéis tracejados, sem a linha de percurso e sem o corte.
  1º Pavimento, pente fino 4 (R11): guarda-roupas abertos com cabides nos closets 3, 2, master e 1, nos retângulos com
     diagonal da DOC_LINHAS, como na Casa E (bege dentro, ocre na borda, cabideiro de metal), portas do lado do closet.
  1º Pavimento, pente fino 5 (seção 7): os armários até o teto da circulação e do quarto de serviço (os outros dois
     retângulos com diagonal da DOC_LINHAS) em marcenaria areia com o veio, sem a diagonal e sem a sombra de móvel
     baixo, pela rotina do Térreo (armarios_ate_o_teto; o Térreo sai igual px a px).
  1º Pavimento, pente fino 6 (seção 8): os bancos do PDF ao pé das camas (suítes 3, 2 e master; os dois banquinhos das
     camas de solteiro da suíte 1), estofados em bege como os da Casa E, no pé da cama do render; os rótulos das suítes
     3 e 2, que caíam sobre eles, vão ao piso livre (rotulos_casaa).
  1º Pavimento, pente fino 7: os criados-mudos da suíte 3 redondos, de 60 cm, como no PDF (os do motor eram quadrados):
     o quadrado e a sombra saem (o vinílico da mesma linha, ao lado) e entram os círculos na madeira do quadrado.
  1º Pavimento, pente fino 8: no quarto de serviço, a faixa com dois quadrados do motor sai e entram a cama de solteiro
     e o criado-mudo do PDF, os da suíte 1 (mesmas medidas no PDF) espelhados na vertical, com a sombra curta.
  1º Pavimento, pente fino 9: no banho master, a banheira retangular do motor sai (o piso limpo do banho, tecido, na luz
     de cada linha) e entram a banheira oval da biblioteca de blocos, no retângulo da elipse do PDF, e a torneira de piso
     do PDF na ponta da esquerda (base redonda e bica em cromo), as duas com a sombra curta.
  1º Pavimento, pente fino 10: nas quatro suítes, os tracinhos escuros do motor no lugar das cortinas saem e entram a
     cortina de linho da biblioteca (`_blocos/blocos.cortina`) em cada trecho de linha ondulada do PDF e o trilho de
     parede a parede, do lado do vidro, como no 1º Pavimento da Casa E.
  1º Pavimento, pente fino 11 (R4): vinílico na escala, como no 1º Pavimento da Casa E (réguas de 20 cm, 1,2 a 1,8 m,
     em tons alternados, com o veio do render, e o escurecido mais claro), nas áreas de vinílico da base chapada, só no
     que é piso; as folhas das portas do PDF ficam. Roda logo depois dos itens 2 e 3, antes dos móveis.
  1º Pavimento, pente fino 12 (seção 18): o Bege Bahia das quatro varandas (suítes 3, 2, master e 1) no desenho e no
     tom da referência, com a rotina do Térreo (item 9, `bege_na_referencia`), para os dois pavimentos ficarem iguais.
  1º Pavimento, pente fino 13 (R8, R9): as projeções da cobertura (os dois contornos da ARQ_CONTRAPISO) e do pergolado
     (a grade da ARQ_PERGOLADO) em tracejado, no traço das projeções do Térreo; como caem quase todas fora da pegada,
     sobre o Térreo nublado, entram na final (`projecoes_1pav_final`, chamada por `rotulos_casaa.final_imagem`).
  1º Pavimento, pente fino 14 (seções 4 e 18): nas fachadas das suítes, o "tubo" branco do motor sai e entram as portas
     de vidro de correr do PDF, finas, em dois planos, como os vidros do Térreo (item 5); antes das cortinas (item 10),
     como na Casa E, e depois do Bege Bahia das varandas (item 12, que agora roda logo depois do vinílico).
  1º Pavimento, pente fino 15 (R13): soleiras porta a porta; só a porta de correr da saleta para o quarto de serviço
     tem o vão branco no PDF: Bege Bahia na escala, com as faces da parede em cinza fino e a folha fina por cima.

Uso (da pasta POE642_CasaA/scripts/):
  python3 ajustes_casaa.py Subsolo     # -> ../renders/POE642_CasaA_PH_Subsolo_final_ajustes.png (+ _camada.png)
  python3 ajustes_casaa.py 1Pavimento  # -> ../renders/POE642_CasaA_PH_1Pavimento_v7_final2_ajustes.png (+ _camada.png)
  python3 ajustes_casaa.py Terreo      # -> ../renders/POE642_CasaA_PH_Terreo_final_bege_barlavento_ajustes.png
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
CASA = AQUI.parent
APROVADAS = {"Subsolo": CASA / "renders/POE642_CasaA_PH_Subsolo_final.png",
             "Terreo": CASA / "renders/POE642_CasaA_PH_Terreo_final_bege_barlavento.png",
             "1Pavimento": CASA / "renders/POE642_CasaA_PH_1Pavimento_v7_final2.png"}

# Subsolo 2: o banco da sauna, em px da imagem aprovada (2000 x 1116). As faces de dentro das paredes da
# esquerda, da direita e de baixo foram medidas na imagem (625,0; 717,5; 845,3); a borda do banco é a linha do
# PDF (830,3 no quadro comum), levada à imagem pelo afim da base (-3,6 px em y), e coincide com o fim da
# sombra que a v6 já tinha junto à porta.
# Os números da sauna da Casa E (sombra 0,14 em 1 px, linha 0,22 em 0,35 px) quase não aparecem aqui: esta
# imagem tem 2000 px e é ampliada para 3840 na prancha. A borda fica um pouco mais marcada e o tampo do banco 3%
# mais claro, para ler como uma peça mais alta que o piso, ainda discreto.
BANCO_SAUNA = {"ret": (625.0, 826.7, 717.5, 845.3),
               "sombra": (0.18, 1.6),        # no piso, acima da borda: força e alcance (px)
               "brilho": (0.05, 0.45),       # na quina do banco: força e largura (px)
               "linha": ((70, 78, 86), 0.35, 0.6),   # cor, força e largura (px)
               "clarear": 1.03}              # tampo do banco


# o Bege Bahia aprovado da Casa A: o mármore das varandas do 1º Pavimento (os mesmos trechos que foram ao Térreo,
# `retoque_bege_bahia_terreo.FONTES_1PAV`), tecido por image quilting
BEGE_1PAV = CASA / "renders/POE642_CasaA_PH_1Pavimento_v7_final2.png"
SS_E = 8                                   # supersampling dos desenhos do estar sob a projeção


def textura_bege(alto, largo, semente=642):
    from retoque_bege_bahia_terreo import quilting, FONTES_1PAV
    p1 = cv2.imread(str(BEGE_1PAV)).astype(np.float32)
    fontes = []
    for x0, y0, x1, y1 in FONTES_1PAV:
        f = p1[y0:y1, x0:x1]
        fontes += [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    return quilting(fontes, alto, largo, p=36, sobra=10, rng=np.random.default_rng(semente))


def cobertura_linhas(y0, y1, ya, yb, n=16):
    """Fração de cada linha de pixel (ya..yb-1) coberta pela faixa [y0, y1) em y."""
    ys = np.arange(ya, yb)[:, None] - 0.5 + (np.arange(n)[None, :] + 0.5) / n
    return ((ys >= y0) & (ys < y1)).mean(axis=1)


def cobertura_colunas(x0, x1, xa, xb):
    xs = np.arange(xa, xb).astype(np.float64)
    return np.clip(np.minimum(xs + 0.5, x1) - np.maximum(xs - 0.5, x0), 0, 1)


def banco_sauna(out):
    q = BANCO_SAUNA
    x0, yb, x1, y1 = q["ret"]
    xa, xb = int(np.floor(x0)), int(np.ceil(x1))
    forca, alcance = q["sombra"]
    ya, yz = int(np.floor(yb - alcance - 1)), int(np.ceil(yb + 2))
    # o tampo do banco, um pouco mais claro que o piso
    yt = int(np.ceil(yb))
    tampo = out[yt:int(np.ceil(y1)), xa:xb].astype(np.float32)
    cxt = cobertura_colunas(x0, x1, xa, xb)[None, :, None]
    out[yt:int(np.ceil(y1)), xa:xb] = np.clip(np.round(tampo * (1 + (q["clarear"] - 1) * cxt)), 0, 255).astype(np.uint8)
    reg = out[ya:yz, xa:xb].astype(np.float32)
    cx = cobertura_colunas(x0, x1, xa, xb)[None, :, None]
    # sombra no piso, acima da borda, mais forte junto a ela (seis faixas, como na Casa E)
    for k in range(6):
        c = cobertura_linhas(yb - alcance * (k + 1) / 6, yb, ya, yz)[:, None, None]
        reg *= 1 - forca / 6 * c * cx
    # brilho leve na quina do banco
    fb, lb = q["brilho"]
    c = cobertura_linhas(yb, yb + lb, ya, yz)[:, None, None] * cx
    reg = reg * (1 - fb * c) + 255 * fb * c
    # a linha fina da borda
    cor, fl, lg = q["linha"]
    c = cobertura_linhas(yb - lg / 2, yb + lg / 2, ya, yz)[:, None, None] * cx
    reg = reg * (1 - fl * c) + np.asarray(cor, np.float32) * fl * c
    out[ya:yz, xa:xb] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    banco da sauna: borda em y {yb} px, de x {x0} a {x1} (linha, sombra no piso e brilho na quina)")
    return out


# Subsolo 3. Escada que desce do deck para a circulação em frente à academia (pedido do usuário, 19/10/26): "tem
# uma linha diagonal discriminando até onde tem o esmaecimento [...] até o terceiro degrau de uma pessoa que está
# vindo de cima para baixo é esmaecido. Do terceiro degrau, depois dessa linha diagonal, já tem que ter a cor do
# subsolo, a cor do degrau, a cor da textura do degrau, de forma visível. [...] essa linha em diagonal não precisa
# estar desenhada". A diagonal é a linha de corte da escada no PDF da Casa A (ARQ_ESCADAS E RAMPAS); antes dela,
# vindo do deck, os degraus ficam como estão (esmaecidos, com o deck). Depois dela, os degraus são refeitos com a
# textura do travertino da circulação, na cor creme da escada (a da legenda), nos espelhos do PDF (a v6 tinha um
# degrau a menos no fim), sem linhas e
# com o sombreamento de descida aprovado nas Casas D e E: cada degrau um pouco mais escuro que o de cima e a
# sombra curta de cada espelho no degrau de baixo, à direita dele (a escada desce da esquerda para a direita).
# Medidas do PDF no quadro comum (2000 px), levadas à imagem pelo afim da base (x' = 0,99911 x - 0,000617 y +
# 1,542; y' = 0,000113 x + 0,99973 y - 3,617): diagonal de (479,9; 551,0) a (498,7; 588,6), espelhos em x 489,2
# a 563,9 (o último é a borda com a circulação). Topo e base: as bordas que a imagem já tem (y 548 e 585,5).
ESCADA = {"diagonal": ((480.67, 547.29), (499.44, 584.88)),
          "espelhos": [480.66, 489.96, 499.25, 508.64, 517.93, 527.22, 536.61, 545.90, 555.19, 564.58],
          "faixa_y": (548.6, 585.2),
          # a textura do degrau: o Bege Bahia da circulação (item 11; antes, o travertino que o motor tinha feito
          # nela), num trecho do tamanho deste (largura x altura, px)
          "fonte": (110, 170),
          # a cor do degrau: o creme da legenda desta escada (#D8CDB4, `retangulos` do Subsolo na config), no tom
          # em que o travertino da base (#DCD9CA) saiu nesta imagem (ganho por canal 1,017; 1,001; 1,044, BGR)
          "cor": (183, 205, 226),
          "escurecer": 0.06,                 # do degrau de cima ao de baixo
          # força e alcance (px), à direita de cada espelho; R14 (pente fino 3, 21/10/26): a sombra passa à linha suave e
          # à sombra curta da `escada_linhas` (escada_deck_subsolo), como a mesma escada no Térreo
          "sombra": (0.0, 2.5)}


def escada(out):
    q = ESCADA
    (dx0, dy0), (dx1, dy1) = q["diagonal"]
    esp = np.asarray(q["espelhos"])
    ya0, ya1 = q["faixa_y"]
    forca, alc = q["sombra"]
    xa, xb = int(np.floor(esp[0])) - 1, int(np.ceil(esp[-1] + alc)) + 1
    ya, yb = int(np.floor(ya0)), int(np.ceil(ya1))
    h, w = yb - ya, xb - xa
    ss = 8
    sub = (np.arange(ss) + 0.5) / ss - 0.5
    X = (np.arange(xa, xb)[:, None] + sub[None, :]).reshape(-1)          # subamostras em x
    Y = (np.arange(ya, yb)[:, None] + sub[None, :]).reshape(-1)
    XX, YY = np.meshgrid(X, Y)
    dentro = (YY >= ya0) & (YY < ya1) & (XX < esp[-1])
    xd = dx0 + (YY - dy0) * (dx1 - dx0) / (dy1 - dy0)
    dentro &= XX > xd                                                    # depois da linha de corte
    k = np.searchsorted(esp, XX) - 1                                     # degrau: entre os espelhos k e k+1
    dentro &= k >= 0
    n = len(esp) - 1
    tom = 1 - q["escurecer"] * np.clip(k, 0, n - 1) / (n - 1)
    d = XX - esp[np.clip(k, 0, n - 1)]
    fator = tom * (1 - forca * np.clip(1 - d / alc, 0, 1))
    # a circulação, logo depois do último espelho, também recebe a sombra curta dele (fica com a textura dela)
    circ = (YY >= ya0) & (YY < ya1) & (XX >= esp[-1]) & (XX < esp[-1] + alc)
    fcirc = 1 - forca * np.clip(1 - (XX - esp[-1]) / alc, 0, 1)

    def por_pixel(m):
        return m.reshape(h, ss, w, ss).mean(axis=(1, 3))

    reg = out[ya:yb, xa:xb].astype(np.float32)
    novo = reg * (1 - por_pixel(dentro))[..., None]
    src = textura_bege(q["fonte"][1], q["fonte"][0], semente=643)
    src *= np.asarray(q["cor"], np.float32) / src.reshape(-1, 3).mean(axis=0)
    for j in range(n):
        m = dentro & (k == j)
        c = por_pixel(m)
        if c.max() == 0:
            continue
        f = por_pixel(np.where(m, fator, 0)) / np.maximum(c, 1e-6)
        # um trecho diferente do travertino para cada degrau, para não repetir
        sx, sy = (7 + 23 * j) % (src.shape[1] - w), (11 + 37 * j) % (src.shape[0] - h)
        tex = src[sy:sy + h, sx:sx + w]
        novo += (c * f)[..., None] * tex
    c = por_pixel(circ)
    f = por_pixel(np.where(circ, fcirc, 1))
    novo = novo * (1 - c)[..., None] + (reg * f[..., None]) * c[..., None]
    out[ya:yb, xa:xb] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    print(f"    escada: degraus depois da linha de corte no creme da escada, com a textura do travertino ({int(por_pixel(dentro).sum())} px), "
          f"sem linhas, com o sombreamento de descida")
    return out


# Subsolo 1. Banho de serviço (pedido do usuário, 19/10/26: "siga com o chuveiro do banho de serviço"): faltavam o
# chuveiro e o vidro do box. No PDF da Casa A (ARQ_LOUÇAS E METAIS), o chuveiro sai da parede da esquerda (canopla,
# braço e ducha) e o box é fechado por duas folhas de vidro de correr, sobrepostas, da parede da esquerda até 982,3
# pt; o resto, até a parede da direita, é a passagem. Entram como os aprovados da Casa E (`chuveiro` e `vidro_box`
# do `retoque_subsolo_casae.py`): a ducha quadrada de 20 cm (11,2 pt), centrada na ducha do PDF, o braço cromado
# até a parede e a canopla; e cada folha de vidro fina, com as bordas finas. Pontos do PDF (pt), levados à imagem
# pelo quadro comum e pelo afim da base.
CHUVEIRO_SERV = {"ducha": (933.2, 1086.4, 944.4, 1097.6),    # centro (938,8; 1092,0): a ducha do PDF
                 "braco": (930.5, 1091.3, 938.8, 1092.8),
                 "canopla": (929.9, 1090.4, 930.5, 1093.6),
                 "vidros": [(929.9, 1121.8, 971.6, 1123.2), (940.6, 1123.2, 982.3, 1124.6)]}
# quadro comum (2000 px) -> imagem aprovada de cada pavimento (SIFT entre a base e a imagem, no quadro comum)
AFIM_QR = {"Subsolo": ((0.99911, -0.000617, 1.542), (0.000113, 0.99973, -3.617)),     # o do banco e da escada
           "Terreo": ((1.01177, -0.000681, 0.608099), (-0.000652, 1.009677, -7.747429)),  # 45 pontos, 0,6 px
           "1Pavimento": ((1.010503, 0.001585, -0.902751), (0.000002, 1.007922, -7.520426))}  # 107 pontos, 0,4 px


def pdf_pavimento(chave):
    """A página do PDF da Casa A do pavimento e a função pt do PDF -> px da imagem aprovada."""
    import json
    import pymupdf
    import rotulos_casaa as A
    from opcoes_1pav_casae import quadro_pdf
    cfg = json.loads(A.CONFIG.read_text())
    q = A.PAVIMENTOS[chave]
    base = (A.CONFIG.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][chave]["base"]).resolve()
    pg = pymupdf.open(A.RAIZ / "_pdfs_cliente" / q["pdf"])[cfg["pavimentos"][chave]["pagina"]]
    at, lt = cv2.imread(str(base), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(A.CASA / q["sem_tela"]), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg, cfg, lt, at, wb, hb, 2000)
    (a, b, c), (d, e, f) = AFIM_QR[chave]

    def p2r(x, y):
        qx, qy = p2q(x, y)
        return a * qx + b * qy + c, d * qx + e * qy + f
    return pg, p2r


def chuveiro_servico(out):
    from retoque_subsolo_casae import chuveiro, vidro_box
    q = CHUVEIRO_SERV
    _, p2r = pdf_pavimento("Subsolo")
    for r in q["vidros"]:
        out = vidro_box(out, p2r, r)
    out = chuveiro(out, p2r, q["ducha"], q["braco"], q["canopla"])
    (x0, y0), (x1, y1) = p2r(*q["ducha"][:2]), p2r(*q["ducha"][2:])
    print(f"    banho de serviço: chuveiro na parede da esquerda (ducha em x {x0:.1f}-{x1:.1f}, y {y0:.1f}-{y1:.1f} px) "
          f"e as duas folhas de vidro do box")
    return out


# Subsolo 4. Portas de vidro da academia (pedido do usuário, 19/10/26: "portas de vidro não pretas da sauna da casa
# A"): nos dois lados da academia, para a circulação e para o hall, o motor fez as portas de correr como um traço
# preto com dentes. No PDF da Casa A (ARQ_PAREDE) são folhas de vidro de 2,83 pt (~1,6 px), duas a duas
# desencontradas: quatro do lado da circulação (as do meio mais para dentro da academia) e duas do lado do hall,
# com o batente fino em cima e embaixo. O traço preto sai (em cada linha de pixel, o piso de cada lado continua
# em espelho: o travertino da circulação, a madeira da academia, a soleira e o travertino do hall), e as folhas
# entram como o vidro da sauna: claras, com a borda fina, e a linha do meio do PDF (as duas metades da folha).
PORTAS_ACADEMIA = {
    "lados": [
        # faixa a limpar (px da imagem: x0, x1, linhas y0..y1), folhas e batentes (pt do PDF)
        {"nome": "da circulação", "faixa": (690, 705, 548, 779),
         "folhas": [(1145.32, 1233.19, 1148.15, 1340.62), (1148.15, 1336.09, 1150.99, 1443.52),
                    (1148.15, 1443.52, 1150.99, 1550.95), (1145.32, 1546.42, 1148.15, 1653.85)],
         "batentes": [(1145.32, 1230.92, 1156.66, 1233.19), (1145.32, 1653.85, 1156.66, 1656.12)]},
        {"nome": "do hall", "faixa": (972, 985, 548, 624),
         "folhas": [(1662.64, 1233.19, 1664.91, 1301.79), (1660.37, 1301.79, 1662.64, 1370.39)],
         "batentes": [(1660.37, 1230.92, 1666.89, 1233.19), (1655.55, 1230.92, 1660.37, 1232.34),
                      (1660.37, 1370.39, 1666.89, 1372.65), (1655.55, 1371.24, 1660.37, 1372.65)]}],
    # o traço do motor: o trecho abaixo desta luminância em volta do px mais escuro de cada linha (no fim do lado
    # da circulação ele é cinza, ~65 a 100), mais 1 px de cada lado, a borda dele
    "escuro": 120,
    # o vidro: claro, com a borda fina e escura (como a da sauna, que se lê) e a linha do meio mais clara
    "vidro": (226, 228, 228), "borda": ((70, 72, 74), 0.35), "meio": ((168, 171, 173), 0.25),
    "aluminio": (150, 153, 156)}


def tirar_traco(out, faixa, escuro):
    """Apaga o traço escuro de cada linha da faixa: os px de cada lado do meio dele recebem, em espelho, o piso
    do seu lado."""
    x0, x1, y0, y1 = faixa
    n = 0
    for y in range(y0, y1 + 1):
        lum = out[y, x0:x1].astype(np.float32).mean(axis=1)
        i = int(np.argmin(lum))
        if lum[i] >= escuro:
            continue
        a, b = i, i                          # o trecho escuro em volta do px mais escuro da linha
        while a > 0 and lum[a - 1] < escuro:
            a -= 1
        while b < len(lum) - 1 and lum[b + 1] < escuro:
            b += 1
        a, b = max(a - 1, 0), min(b + 1, x1 - x0 - 1)
        meio = (a + b) / 2
        for i in range(a, b + 1):
            if i <= meio:
                out[y, x0 + i] = out[y, x0 + a - 1 - (i - a)]
            else:
                out[y, x0 + i] = out[y, x0 + b + 1 + (b - i)]
            n += 1
    return n


def portas_academia(out):
    from retoque_subsolo_casae import Tela
    q = PORTAS_ACADEMIA
    _, p2r = pdf_pavimento("Subsolo")
    for lado in q["lados"]:
        n = tirar_traco(out, lado["faixa"], q["escuro"])
        caixa = [f(v) for f, v in zip((min, min, max, max), zip(*(lado["folhas"] + lado["batentes"])))]
        tl = Tela(out, p2r, caixa)
        for b in lado["batentes"]:
            m = tl.ret(b)
            tl.pintar(m, q["aluminio"])
            tl.contorno(m, *q["borda"][::-1])
        for f in lado["folhas"]:
            m = tl.ret(f)
            tl.pintar(m, q["vidro"])
            xm = (f[0] + f[2]) / 2
            tl.pintar(m & tl.ret((xm - 0.25, f[1], xm + 0.25, f[3])), q["meio"][0])
            tl.contorno(m, q["borda"][1], q["borda"][0])
        out = tl.gravar()
        print(f"    lado {lado['nome']}: traço preto apagado ({n} px, o piso de cada lado), "
              f"{len(lado['folhas'])} folhas de vidro e {len(lado['batentes'])} batentes do PDF")
    return out


# Subsolo 5. Janelas (pedido do usuário, 19/10/26: "melhore o aspecto das janelas"): a do banho de serviço (para a
# circulação) e a da circulação para o depósito. O motor fez cada uma como uma peça cinza de cantos arredondados,
# com a borda grossa e borrada, um pouco para fora da parede. No PDF da Casa A (ARQ_PAREDE) é o vão na parede com o
# vidro fino no meio, os caixilhos nas pontas, os retornos da parede e as faces da parede passando pelo vão (o
# peitoril). Entram nessa geometria: o peitoril claro (o quartzo das bancadas), as duas faces em linha fina, o
# vidro como o das portas da academia, os caixilhos em alumínio e os retornos no preto das paredes; acima e
# abaixo do vão, a parede preta. Fora do vão, a borda escura da peça do motor volta ao piso do lado.
JANELAS = [
    {"nome": "do banho de serviço",
     "vao": (1009.25, 1066.51, 1017.76, 1111.87),
     "paredes": [(1009.25, 1060.0, 1017.76, 1066.51), (1009.25, 1111.87, 1017.76, 1118.0),
                 (1013.22, 1066.51, 1017.76, 1068.21), (1013.22, 1110.17, 1017.76, 1111.87)],
     "faces": [(1009.25, 1066.51, 1111.87), (1017.76, 1068.21, 1110.17)],
     "caixilhos": [(1010.39, 1066.51, 1013.22, 1068.5), (1010.39, 1109.88, 1013.22, 1111.87)],
     "vidro": (1010.39, 1068.5, 1014.64, 1109.88)},
    {"nome": "da circulação para o depósito",
     "vao": (1145.32, 1077.85, 1156.66, 1134.54),
     "paredes": [(1145.32, 1071.0, 1156.66, 1077.85), (1145.32, 1134.54, 1156.66, 1141.0),
                 (1145.32, 1077.85, 1149.85, 1079.55), (1152.69, 1077.85, 1156.66, 1079.55),
                 (1145.32, 1132.84, 1149.85, 1134.54), (1152.69, 1132.84, 1156.66, 1134.54)],
     "faces": [(1145.32, 1079.55, 1132.84), (1156.66, 1079.55, 1132.84)],
     "caixilhos": [(1149.85, 1077.85, 1152.69, 1079.83), (1149.85, 1132.56, 1152.69, 1134.54)],
     "vidro": (1148.44, 1079.83, 1152.69, 1132.56)}]
JANELA = {"peitoril": (225, 232, 236),     # BGR de #ECE8E1, o quartzo das bancadas
          "face": ((90, 92, 94), 0.35),    # cor e largura (px) das faces da parede no vão
          "fora": (1.6, 25)}               # faixa fora do vão (px) e quanto mais escura que o piso vira piso


def limpar_fora(out, x0, x1, y0, y1, faixa, limiar):
    """Nos px logo fora do vão (de cada lado), o que é bem mais escuro que o piso logo adiante vira esse piso."""
    for y in range(int(np.floor(y0)), int(np.ceil(y1))):
        for lado, borda in ((-1, x0), (1, x1)):
            xs = [int(np.floor(borda - faixa)) + i for i in range(int(np.ceil(faixa)) + 1)] if lado < 0 else \
                 [int(np.floor(borda)) + i for i in range(int(np.ceil(faixa)) + 1)]
            xs = [x for x in xs if (x + 0.5 < borda if lado < 0 else x + 0.5 > borda)]
            ref = out[y, xs[0] - 3:xs[0] - 1] if lado < 0 else out[y, xs[-1] + 2:xs[-1] + 4]
            piso = ref.astype(np.float32).mean(axis=0)
            for x in xs:
                if out[y, x].astype(np.float32).mean() < piso.mean() - limiar:
                    out[y, x] = np.clip(np.round(piso), 0, 255).astype(np.uint8)


def janelas(out):
    from retoque_subsolo_casae import Tela
    q, pa = JANELA, PORTAS_ACADEMIA
    _, p2r = pdf_pavimento("Subsolo")
    k = 0.5483                               # px por pt nesta imagem
    for j in JANELAS:
        (x0, y0), (x1, y1) = p2r(*j["vao"][:2]), p2r(*j["vao"][2:])
        limpar_fora(out, x0, x1, y0, y1, *q["fora"])
        caixa = [f(v) for f, v in zip((min, min, max, max), zip(*(j["paredes"] + [j["vao"]])))]
        tl = Tela(out, p2r, caixa)
        viz = tl.reg.reshape(-1, 3)
        preto = np.median(viz[viz.mean(axis=1) < 40], axis=0)
        tl.pintar(tl.ret(j["vao"]), q["peitoril"])
        for r in j["paredes"]:
            tl.pintar(tl.ret(r), preto)
        cor, larg = q["face"]
        for x, fy0, fy1 in j["faces"]:
            tl.pintar(tl.ret((x - larg / k / 2, fy0, x + larg / k / 2, fy1)), cor)
        for r in j["caixilhos"]:
            m = tl.ret(r)
            tl.pintar(m, pa["aluminio"])
            tl.contorno(m, pa["borda"][1], pa["borda"][0])
        v = j["vidro"]
        m = tl.ret(v)
        tl.pintar(m, pa["vidro"])
        xm = (v[0] + v[2]) / 2
        tl.pintar(m & tl.ret((xm - 0.25, v[1], xm + 0.25, v[3])), pa["meio"][0])
        tl.contorno(m, pa["borda"][1], pa["borda"][0])
        out = tl.gravar()
        print(f"    janela {j['nome']}: vão x {x0:.1f}-{x1:.1f}, y {y0:.1f}-{y1:.1f} px; peitoril, faces, vidro, "
              f"caixilhos e retornos do PDF")
    return out


# Subsolo 6. Traço preto no fim da circulação (pedido do usuário, 19/10/26: "Esse traço preto no fim da área de
# circulação não existe"): ao longo da borda esquerda da circulação, ~5 px para dentro do travertino, o motor fez
# um traço preto vertical, da escada do deck até a parede de baixo. No PDF da Casa A a circulação só termina (a
# borda do piso, sem linha). O traço sai como o das portas da academia: em cada linha, o travertino de cada lado
# continua em espelho.
TRACO_CIRCULACAO = {"faixa": (566, 584, 585, 845), "escuro": 140}   # px da imagem: x0, x1, linhas y0..y1 (846: a parede)


def traco_circulacao(out):
    n = tirar_traco(out, TRACO_CIRCULACAO["faixa"], TRACO_CIRCULACAO["escuro"])
    print(f"    traço preto da borda da circulação apagado ({n} px, o travertino de cada lado)")
    return out


# Subsolo 7. Juntas do depósito e da circulação interna (pedido do usuário, 19/10/26: "As marcações de juntas não
# existem na área de depósito e nem na circulação interna (entre banho de serviço e depósito)"). O piso desses dois
# ambientes (Bege Bahia na legenda) saiu como placas de ~44 x 22 px, cada uma num tom, com a junta marcada (linhas
# em x 661, 749, 793, 837, 880 e 925 e em y 478, 496 e 522). O piso volta contínuo, com a textura do próprio
# render: tecida (image quilting, como o Bege Bahia aprovado do Térreo) de miolos de placas, cada miolo normalizado
# pelo seu tom, e posta na luz do render (o tom médio do piso em volta, suavizado o bastante para as placas
# sumirem e a sombra junto às paredes ficar). Ficam como estão as paredes, a porta do depósito com o arco e a peça
# junto à parede de baixo.
JUNTAS = {
    # ambientes (px da imagem: x0, y0, x1, y1), por dentro das paredes e das janelas
    "areas": [(702, 455, 974, 541), (626, 455, 695, 538)],
    # miolos de placas, longe das juntas, das paredes, da porta e da sombra da parede da direita
    "fontes": [(753, 458, 790, 476), (797, 458, 834, 476), (841, 458, 877, 476), (884, 458, 921, 476),
               (753, 499, 790, 520), (797, 499, 834, 520), (841, 499, 877, 520), (884, 499, 921, 520),
               (797, 525, 834, 539), (841, 525, 877, 539)],
    "proteger": [(699, 524, 746, 545)],      # a peça junto à parede de baixo do depósito (com a sua sombra)
    "piso_min": 100,                         # abaixo disso é parede ou peça
    "linha": 18,                             # traço fino mais escuro que o piso em volta (o arco da porta)
    "luz_sigma": (14, 8),                    # suavização da luz (x, y): mais que uma placa, menos que a sala
    "p": 12}


def juntas(out):
    from retoque_bege_bahia_terreo import quilting
    q = JUNTAS
    fontes = []
    for x0, y0, x1, y1 in q["fontes"]:
        g = out[y0:y1, x0:x1].astype(np.float32)
        g = g / g.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    for k, (x0, y0, x1, y1) in enumerate(q["areas"]):
        reg = out[y0:y1, x0:x1].astype(np.float32)
        lum = reg.mean(axis=2)
        piso = lum >= q["piso_min"]
        piso &= lum - cv2.GaussianBlur(lum, (0, 0), 2) > -q["linha"]          # o arco e outros traços finos
        for a, b, c, d in q["proteger"]:
            piso[max(b - y0, 0):max(d - y0, 0), max(a - x0, 0):max(c - x0, 0)] = False
        piso = cv2.erode(piso.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        m = piso.astype(np.float32)
        sx, sy = q["luz_sigma"]
        luz = cv2.GaussianBlur(reg * m[..., None], (0, 0), sigmaX=sx, sigmaY=sy) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sigmaX=sx, sigmaY=sy), 1e-3)[..., None]
        tex = quilting(fontes, y1 - y0, x1 - x0, p=q["p"], sobra=max(3, q["p"] // 3), candidatos=600,
                       rng=np.random.default_rng(642 + k))
        a = cv2.GaussianBlur(m, (0, 0), 0.5) * m
        novo = reg * (1 - a[..., None]) + tex * luz * a[..., None]
        out[y0:y1, x0:x1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
        print(f"    {'depósito' if k == 0 else 'circulação interna'}: piso contínuo, sem juntas ({int(piso.sum())} px)")
    return out


# Subsolo 8. Cubas dos banhos feminino e masculino (pedido do usuário, 19/10/26: "as cubas dos banhos femininos e
# masculinos são maiores"). O motor fez em cada bancada uma cuba branca pequena (~16 x 10 px). No PDF da Casa A
# (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS) a cuba é uma calha de ~32 x 15 px, quase da largura da bancada e de toda
# a profundidade, com uma faixa plana junto à parede do fundo, onde fica a torneira. Entra nessa geometria, como
# as cubas aprovadas da Casa E (`retoque_subsolo_casae.bancada_cuba`): a louça branca com o contorno fino, a
# bacia escurecendo da borda ao fundo, a válvula no meio e a torneira cromada saindo da parede, com a sombra
# curta. A bancada do render fica.
CUBAS_BANHOS = [
    {"nome": "feminino", "cuba": (1307.18, 1748.53, 1366.14, 1775.17), "bacia": (1308.31, 1749.66, 1365.0, 1768.37),
     "torneira": (1335.61, 1762.87, 1337.71, 1772.25)},
    {"nome": "masculino", "cuba": (1573.35, 1748.53, 1639.68, 1775.17), "bacia": (1574.48, 1749.66, 1638.55, 1768.37),
     "torneira": (1606.32, 1762.87, 1608.41, 1772.25)}]


def cubas_banhos(out):
    from retoque_subsolo_casae import (Tela, SOMBRA, LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO, CROMO,
                                       CROMO_CLARO, CROMO_ESCURO, SS)
    _, p2r = pdf_pavimento("Subsolo")
    for q in CUBAS_BANHOS:
        tl = Tela(out, p2r, q["cuba"])
        x0, y0, x1, y1 = q["cuba"]
        tl.pintar(tl.ret(q["cuba"], 1.0), LOUCA_CONTORNO)
        tl.pintar(tl.ret((x0 + 0.8, y0 + 0.8, x1 - 0.8, y1 - 0.8), 0.8), LOUCA)
        bx0, by0, bx1, by1 = q["bacia"]
        for i in range(6):                   # a bacia, da borda ao fundo
            k = i / 5
            cor = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
            ins = 0.6 + k * 3.0
            tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.6, 1.6 - k)), cor)
        vx, vy = tl.pt((bx0 + bx1) / 2, (by0 + by1) / 2)
        v = tl.vazia()
        cv2.circle(v, (int(vx), int(vy)), int(1.1 * SS), 255, -1)
        tl.pintar(v, CROMO_ESCURO)
        tx0, ty0, tx1, ty1 = q["torneira"]   # vem da parede do fundo (embaixo)
        m = tl.ret(q["torneira"], 0.8)
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, CROMO_ESCURO)
        tl.pintar(tl.ret((tx0 + 0.3, ty0 + 0.4, (tx0 + tx1) / 2, ty1 - 0.4), 0.4), CROMO_CLARO)
        base = tl.vazia()
        cx, cy = tl.pt((tx0 + tx1) / 2, ty1)
        cv2.circle(base, (int(cx), int(cy)), int(1.0 * SS), 255, -1)
        tl.pintar(base, CROMO)
        out = tl.gravar()
        (a, b), (c, d) = p2r(x0, y0), p2r(x1, y1)
        print(f"    cuba do banho {q['nome']}: x {a:.1f}-{c:.1f}, y {b:.1f}-{d:.1f} px, com a torneira da parede do fundo")
    return out


# Subsolo 9. Boxes dos chuveiros (pedido do usuário, 19/10/26: "faltando a representação dos boxes dos chuveiros, em
# vidro"): a ducha ao lado da sauna e o chuveiro do banho feminino. No PDF da Casa A (ARQ_LOUÇAS E METAIS) cada box
# é de correr: o trilho tracejado de parede a parede e duas folhas de vidro desencontradas; onde não há folha é a
# entrada do box (na ducha, à direita; no banho feminino, embaixo). O render não tem o vidro: na ducha, nada; no
# banho feminino, um traço escuro de cima a baixo, que sai (o travertino de cada lado continua). As folhas entram
# como as do box do banho de serviço (`vidro_box`, aprovado): cada uma na metade do trilho do PDF (1,4 pt), fina,
# clara e com a borda fina.
BOXES = [
    {"nome": "ducha ao lado da sauna",
     "folhas": [(1196.34, 1719.9, 1240.85, 1721.32), (1207.67, 1721.32, 1252.12, 1722.73)]},
    {"nome": "chuveiro do banho feminino", "traco": (846, 862, 786, 844),   # px da imagem: x0, x1, linhas y0..y1
     "folhas": [(1434.45, 1664.62, 1435.87, 1721.88), (1433.03, 1678.5, 1434.45, 1735.7)]}]


def boxes(out):
    from retoque_subsolo_casae import vidro_box
    _, p2r = pdf_pavimento("Subsolo")
    for q in BOXES:
        n = tirar_traco(out, q["traco"], 130) if "traco" in q else 0
        for f in q["folhas"]:
            out = vidro_box(out, p2r, f)
        print(f"    box da {q['nome']}: {len(q['folhas'])} folhas de vidro do PDF" +
              (f"; traço escuro do render apagado ({n} px)" if n else ""))
    return out


# Subsolo 10. Divisória entre os banhos feminino e masculino (pedido do usuário, 19/10/26: "essa divisória não é
# parede. é outra coisa!"). O motor a fez como parede preta (~3 px). No PDF da Casa A ela não está na camada das
# paredes: está na das bancadas (ARQ_BANCADAS), com o miolo branco (na ARQ_PAREDE o trecho é branco, vão) e as
# peças finas em cinza por dentro, em degrau, como as placas de pedra das bancadas, com ~19 cm no total. Entra na
# geometria do PDF como peça clara, no tom das bancadas do render, com a borda fina e as peças finas do PDF em
# cinza; o registro pequeno do lado do banho feminino (ARQ_LOUÇAS E METAIS), cromado. O preto do motor sai antes
# (o piso de cada lado continua); em cima e embaixo ficam as paredes.
DIVISORIA = {"caixa": (1490.01, 1664.62, 1500.78, 1775.17),
             "traco": (882, 894, 786, 845),          # px da imagem: x0, x1, linhas y0..y1 (o preto do motor)
             # as peças finas (pt do PDF): as cinzas da ARQ_BANCADAS e a placa da direita (as linhas de 0,85 pt)
             "pecas": [(1490.01, 1664.62, 1493.98, 1665.76), (1491.71, 1665.76, 1492.85, 1692.97),
                       (1490.01, 1692.97, 1496.81, 1694.1), (1495.68, 1694.1, 1496.81, 1775.17),
                       (1490.01, 1774.04, 1495.68, 1775.17), (1494.05, 1664.62, 1495.18, 1692.97)],
             "registro": (1490.79, 1675.11, 1491.71, 1682.49),
             "pedra": (192, 209, 222),               # BGR da bancada do banho feminino no render
             "peca": (138, 141, 143), "borda": ((120, 122, 124), 0.3)}


def divisoria(out):
    from retoque_subsolo_casae import Tela, CROMO
    q = DIVISORIA
    n = tirar_traco(out, q["traco"], 120)
    _, p2r = pdf_pavimento("Subsolo")
    tl = Tela(out, p2r, q["caixa"])
    m = tl.ret(q["caixa"])
    tl.pintar(m, q["pedra"])
    for r in q["pecas"]:
        tl.pintar(tl.ret(r), q["peca"])
    tl.contorno(m, q["borda"][1], q["borda"][0])
    tl.pintar(tl.ret(q["registro"]), CROMO)
    out = tl.gravar()
    (a, b), (c, d) = p2r(*q["caixa"][:2]), p2r(*q["caixa"][2:])
    print(f"    divisória: preto do motor apagado ({n} px); peça clara do PDF em x {a:.1f}-{c:.1f}, y {b:.1f}-{d:.1f} px")
    return out


# Subsolo 11. Bege Bahia (pedido do usuário, 19/10/26: "esse piso da circulação é marmore bege bahia. Inclusive melhore
# a representação do bege bahia no depósito e na área de circulação"). A circulação ao longo da academia (do pé da
# escada do deck até a parede de baixo, a "área de circulação") tinha saído em travertino, e o depósito e a
# circulação interna num bege fosco, sem cara de mármore. Os três passam ao Bege Bahia aprovado da Casa A: o mármore
# das varandas do 1º Pavimento, que já foi ao Térreo (`textura_bege`), na cor dele, com a sombra suave do render
# (como no Térreo: a textura nova escurece onde o piso do render era mais escuro que o piso em volta, até 14%). A
# escada que desce do deck (item 3) passa a tirar a textura do degrau do mesmo Bege Bahia, no creme dela.
BEGE = {
    "areas": [
        # nome, caixa (px da imagem), semente; a faixa vai até as folhas de vidro da academia (o x de cada linha)
        ("área de circulação", (565, 543, 697, 846), 651),
        ("depósito", (695, 455, 974, 541), 652),          # com a soleira da porta, na parede da circulação interna
        ("circulação interna", (626, 455, 695, 538), 653)],
    "fora": [(619, 779, 700, 846),           # a sauna, com o vidro dela
             (694, 455, 702, 495),           # a janela da circulação para o depósito (item 5)
             (700, 529, 734, 546)],          # a folha da porta do depósito e a peça junto à parede de baixo
    "piso": (100, 245),                      # luminância do piso (fora: paredes, peças escuras e o branco do papel)
    # o arco da porta do depósito: o traço fino volta por cima do Bege Bahia, como escurecimento relativo (a razão
    # entre cada px e a mediana do piso em volta, na imagem de antes deste item)
    "arcos": [(700, 494, 737, 530)],
    "sombra": (0.86, 6)}                     # escurecimento máximo e suavização da luz (px)


def bege_mascaras(out):
    """As três áreas do Bege Bahia: nome, caixa (px), semente e a máscara do piso na caixa (lida de `out` na hora)."""
    q = BEGE
    folhas = [f for lado in PORTAS_ACADEMIA["lados"] if "circulação" in lado["nome"] for f in lado["folhas"]]
    _, p2r = pdf_pavimento("Subsolo")
    lim = [(p2r(f[0], f[1])[1], p2r(f[2], f[3])[1], p2r(f[0], f[1])[0]) for f in folhas]   # y0, y1, x da folha
    for nome, (x0, y0, x1, y1), semente in q["areas"]:
        lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m = (lum >= q["piso"][0]) & (lum <= q["piso"][1])
        ys, xs = np.mgrid[y0:y1, x0:x1]
        for a, b, c, d in q["fora"]:
            m &= ~((xs >= a) & (xs < c) & (ys >= b) & (ys < d))
        if nome == "área de circulação":
            xmax = np.full(y1 - y0, 694.9)
            for fy0, fy1, fx in lim:
                k = (np.arange(y0, y1) + 0.5 >= fy0) & (np.arange(y0, y1) + 0.5 < fy1)
                xmax[k] = fx
            m &= xs + 0.5 <= xmax[:, None]
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
        yield nome, (x0, y0, x1, y1), semente, m


def bege_bahia(out):
    q = BEGE
    for nome, (x0, y0, x1, y1), semente, m in bege_mascaras(out):
        reg = out[y0:y1, x0:x1].astype(np.float32)
        lum = reg.mean(axis=2)
        ys, xs = np.mgrid[y0:y1, x0:x1]
        mf = m.astype(np.float32)
        lum_m = cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), 7).astype(np.float32)
        sig = q["sombra"][1]
        viz = cv2.GaussianBlur(lum_m * mf, (0, 0), sig) / np.maximum(cv2.GaussianBlur(mf, (0, 0), sig), 1e-3)
        sombra = np.clip(viz / float(np.median(lum[m])), q["sombra"][0], 1.0)[..., None]
        tex = textura_bege(y1 - y0, x1 - x0, semente) * sombra
        for a, b, c, d in q["arcos"]:
            k = (xs >= a) & (xs < c) & (ys >= b) & (ys < d)
            if k.any():
                razao = np.clip(lum / np.maximum(cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), 7), 1), 0.4, 1.0)
                tex[k] *= np.where(razao < 0.97, razao, 1.0)[k][:, None]
        a = (cv2.GaussianBlur(mf, (0, 0), 0.5) * mf)[..., None]
        out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - a) + tex * a), 0, 255).astype(np.uint8)
        print(f"    {nome}: Bege Bahia do 1º Pavimento ({int(m.sum())} px), com a sombra suave do render")
    return out


# Subsolo 12. Bancada e cuba do banho de serviço (pedido do usuário, 19/10/26: "faltou a bancada da pia, com a cuba;
# ambos em suas respectivas dimensões"). O motor fez só um quadrado claro junto à parede da esquerda. No PDF da Casa
# A a bancada (ARQ_BANCADAS) tem 22,7 x 51,0 pt (~12 x 28 px), da parede da esquerda, com um recorte onde entra a
# cuba (ARQ_LOUÇAS E METAIS): quadrada, de cantos arredondados, 22,6 pt (~12 px), avançando além da bancada, com a
# bacia à direita e a torneira monocomando no lado da parede, a bica para a direita. Entram nessas medidas, no padrão
# das cubas aprovadas (item 8 e Casa E): a bancada no tom das bancadas do render, com a borda fina e a sombra curta;
# a cuba de louça com o contorno fino, a bacia escurecendo da borda ao fundo e a válvula; a torneira cromada.
BANCADA_SERV = {"bancada": (929.88, 1168.56, 952.56, 1219.58),
                "cuba": (936.73, 1182.77, 959.32, 1205.37),
                "bacia": (942.88, 1185.0, 957.1, 1203.14),
                "torneira": (938.6, 1192.65, 948.38, 1195.49),
                # o quadrado claro do motor passava ~1,5 px da bancada do PDF, para a direita: volta ao piso
                "limpar": (589, 593, 512, 542)}       # px da imagem: x0, x1, linhas y0..y1


def bancada_servico(out):
    from retoque_subsolo_casae import (Tela, SOMBRA, LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO, CROMO,
                                       CROMO_CLARO, CROMO_ESCURO, SS)
    q = BANCADA_SERV
    x0, x1, y0, y1 = q["limpar"]
    for y in range(y0, y1 + 1):              # o que sobra do quadrado do motor: o piso logo à direita
        piso = out[y, x1 + 1:x1 + 4].astype(np.float32).mean(axis=0)
        for x in range(x0, x1 + 1):
            if out[y, x].astype(np.float32).mean() > piso.mean() + 20:
                out[y, x] = np.round(piso).astype(np.uint8)
    _, p2r = pdf_pavimento("Subsolo")
    caixa = (q["bancada"][0], q["bancada"][1], q["cuba"][2], q["bancada"][3])
    tl = Tela(out, p2r, caixa)
    b = tl.ret(q["bancada"])
    tl.sombra(b, **SOMBRA)
    tl.pintar(b, DIVISORIA["pedra"])
    tl.contorno(b, 0.35, (150, 153, 155))
    c = tl.ret(q["cuba"], 2.0)
    tl.sombra(c, **SOMBRA)
    tl.pintar(c, LOUCA_CONTORNO)
    cx0, cy0, cx1, cy1 = q["cuba"]
    tl.pintar(tl.ret((cx0 + 0.8, cy0 + 0.8, cx1 - 0.8, cy1 - 0.8), 1.6), LOUCA)
    bx0, by0, bx1, by1 = q["bacia"]
    for i in range(6):                       # a bacia, da borda ao fundo
        k = i / 5
        cor = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
        ins = 0.4 + k * 2.6
        tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.6, 1.8 - k)), cor)
    vx, vy = tl.pt((bx0 + bx1) / 2 + 1.5, (by0 + by1) / 2)
    v = tl.vazia()
    cv2.circle(v, (int(vx), int(vy)), int(1.1 * SS), 255, -1)
    tl.pintar(v, CROMO_ESCURO)
    tx0, ty0, tx1, ty1 = q["torneira"]       # monocomando no lado da parede, a bica para a direita
    m = tl.ret(q["torneira"], 0.8)
    tl.sombra(m, **SOMBRA)
    tl.pintar(m, CROMO_ESCURO)
    tl.pintar(tl.ret((tx0 + 0.4, ty0 + 0.4, tx1 - 0.4, (ty0 + ty1) / 2), 0.4), CROMO_CLARO)
    base = tl.vazia()
    cx, cy = tl.pt(tx0 + 1.2, (ty0 + ty1) / 2)
    cv2.circle(base, (int(cx), int(cy)), int(1.0 * SS), 255, -1)
    tl.pintar(base, CROMO)
    out = tl.gravar()
    (a, b_), (c_, d) = p2r(*q["bancada"][:2]), p2r(*q["bancada"][2:])
    (e, f), (g, h) = p2r(*q["cuba"][:2]), p2r(*q["cuba"][2:])
    print(f"    banho de serviço: bancada x {a:.1f}-{c_:.1f}, y {b_:.1f}-{d:.1f} px; cuba x {e:.1f}-{g:.1f}, y {f:.1f}-{h:.1f} px")
    return out


# Subsolo 13. Gramado junto à escada do deck (pedido do usuário, 19/10/26: "ao termino dos degraus no sentido do subsolo,
# ou seja, a escada desce, no último degrau, após ele, há um gramado, que separa o último degrau da área de circulação
# do subsolo", com o recorte da prancha do Térreo). Abaixo da escada que desce do deck, entre a borda do deck
# esmaecido e a circulação, a prancha do Subsolo estava em branco; no Térreo ali é o gramado. Entra o gramado do
# próprio Térreo aprovado, no mesmo lugar (as duas imagens vão ao quadro comum, e o afim de uma à outra passa por ele),
# na cor dele, só onde o Subsolo está em branco: da escada até a parede de baixo do Subsolo, da borda esquerda do
# deck esmaecido até a circulação. A borda com o branco é suave (a parte branca de cada px).
# Pente fino pelas regras (21/10/26), Subsolo, item 2 (confirmado: o gramado fica): a fonte passa do Térreo aprovado
# (a grama de carpete do motor) ao Térreo com os ajustes do pente fino, onde ali é a grama da referência na escala
# (item 7 do Térreo; sem plantas nesse trecho). O Subsolo passa a depender dos ajustes do Térreo.
GRAMADO_ESCADA = {"caixa": (376, 584, 575, 849),    # px da imagem do Subsolo: x0, y0, x1, y1
                  "branco": (230, 250),             # rampa da borda: mínimo do px de 230 (nada) a 250 (tudo)
                  "fonte": CASA / "renders/POE642_CasaA_PH_Terreo_final_bege_barlavento_ajustes.png"}


def gramado_escada(out):
    q = GRAMADO_ESCADA
    m = lambda k: np.vstack([np.float64(AFIM_QR[k]), [0, 0, 1]])
    s2t = m("Terreo") @ np.linalg.inv(m("Subsolo"))          # px do Subsolo -> px do Térreo
    terreo = cv2.imread(str(q["fonte"]))
    x0, y0, x1, y1 = q["caixa"]
    gx, gy = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
    mx = (s2t[0, 0] * gx + s2t[0, 1] * gy + s2t[0, 2]).astype(np.float32)
    my = (s2t[1, 0] * gx + s2t[1, 1] * gy + s2t[1, 2]).astype(np.float32)
    grama = cv2.remap(terreo, mx, my, cv2.INTER_LINEAR).astype(np.float32)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    lo, hi = q["branco"]
    a = np.clip((reg.min(axis=2) - lo) / (hi - lo), 0, 1)
    verde = (grama[..., 1] > grama[..., 2] + 8) & (grama[..., 1] > grama[..., 0] + 8)
    # a grama da referência (pente fino 2) tem folhas claras que não passam no verde: a mancha inteira, fechada
    from scipy import ndimage
    verde = ndimage.binary_fill_holes(cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)))
    a *= cv2.GaussianBlur(verde.astype(np.float32), (0, 0), 0.7)
    out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - a[..., None]) + grama * a[..., None]), 0, 255).astype(np.uint8)
    # na emenda com a circulação sobrava o px claro da borda dela (contra o branco): vira a média dos dois lados
    for y in range(y0, y1):
        xs = np.nonzero(a[y - y0] > 0.5)[0]
        if len(xs):
            xl = x0 + xs.max()
            if xl + 2 < out.shape[1] and out[y, xl + 1].mean() > out[y, xl + 2].mean() + 12:
                out[y, xl + 1] = ((out[y, xl].astype(np.float32) + out[y, xl + 2]) / 2).astype(np.uint8)
    print(f"    gramado do Térreo abaixo da escada: {int((a > 0.5).sum())} px (x {x0}-{x1}, y {y0}-{y1})")
    return out


# Térreo 1. Pilares (pedido do usuário, 19/10/26: "siga com os pilares do térreo"): os três pilares redondos da
# varanda e o quadrado junto ao gourmet, que o motor fez em marrom, são os pilares estruturais do PDF da Casa A
# (camada EST - Pilar) e ficam no preto das paredes, como o pilar do Térreo da Casa E (`retoque_terreo_casae.pilar`),
# na geometria do PDF (o contorno preenchido de cada pilar, levado à imagem), com a borda antisserrilhada. O
# marrom do motor sai um pouco maior que o PDF (raio ~7,3 px contra 6,3 px, ~1 px a mais no quadrado): o anel de
# marrom que sobra fora do contorno do PDF volta ao piso de cada pixel (tira-se só a parte marrom da mistura).
PILARES = {"camada": "EST - Pilar",
           "parede": (770, 740, 900, 870),   # paredes do banho da varanda e do WC (px da imagem): o preto
           "janela": 14,                     # meia janela em volta de cada pilar (px)
           "fundo": (3, 8),                  # anel de fundo: distância ao contorno do PDF (px)
           "sigma": 2.5,                     # suavização do fundo de cada lugar (px)
           "anel": 2.5,                      # até onde, fora do contorno do PDF, o marrom do motor vai (px)
           "w_min": 0.15,                    # abaixo disso é o veio do piso, não o marrom
           "residuo": 30}                    # só é marrom o que está na mistura marrom-fundo


def pilares(out):
    from retoque_terreo_casae import poligono_aa
    q = PILARES
    a, b, c, d = q["parede"]
    viz = out[b:d, a:c].reshape(-1, 3)
    preto = np.median(viz[viz.astype(np.float32).mean(axis=1) < 40], axis=0).astype(np.float32)
    pg, p2r = pdf_pavimento("Terreo")
    n = 0
    for dr in pg.get_drawings():
        if dr.get("layer") != q["camada"] or dr["type"] != "f":
            continue                         # o círculo só traçado é o eixo da escada caracol
        pts = [p2r(it[1].x, it[1].y) for it in dr["items"]]
        al = poligono_aa(out.shape[:2], pts)
        ys, xs = np.nonzero(al)
        cx, cy = int(np.average(xs, weights=al[ys, xs])), int(np.average(ys, weights=al[ys, xs]))
        k = q["janela"]
        sl = np.s_[cy - k:cy + k + 1, cx - k:cx + k + 1]
        reg, alr = out[sl].astype(np.float32), al[sl]
        # o marrom do motor e o fundo em volta: cada pixel do anel é fundo + w (marrom - fundo). O fundo é o de
        # cada lugar (média suave dos pixels de fora, sem os pretos), porque em volta do pilar do gourmet há piso,
        # grama e a folha da porta; um fundo único clareava a borda de cima
        marrom = np.median(reg[alr > 0.99], axis=0)
        dist = cv2.distanceTransform((alr < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        fm = ((dist > q["fundo"][0]) & (dist < q["fundo"][1]) & (reg.mean(axis=2) > 60)).astype(np.float32)
        fundo = (cv2.GaussianBlur(reg * fm[..., None], (0, 0), q["sigma"])
                 / np.maximum(cv2.GaussianBlur(fm, (0, 0), q["sigma"]), 1e-4)[..., None])
        v = marrom - fundo
        w = np.clip(((reg - fundo) * v).sum(axis=2) / np.maximum((v * v).sum(axis=2), 1), 0, 1)
        w[np.linalg.norm(reg - (fundo + w[..., None] * v), axis=2) >= q["residuo"]] = 0
        w[(dist > q["anel"]) | (w < q["w_min"]) | (reg[..., 1] > reg[..., 2])] = 0   # longe, veio ou grama (verde)
        reg -= w[..., None] * v              # o marrom sai, fica o piso
        reg = reg * (1 - alr[..., None]) + preto * alr[..., None]
        out[sl] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        x0, y0 = np.min(pts, axis=0)
        x1, y1 = np.max(pts, axis=0)
        forma = "redondo" if len(pts) > 4 else "quadrado"
        print(f"    pilar {forma}: ({x0:.1f}, {y0:.1f}) - ({x1:.1f}, {y1:.1f}) px; marrom {marrom.astype(int).tolist()} "
              f"-> preto; anel fora do PDF: {float((w * (1 - alr)).sum()):.0f} px de marrom de volta ao piso")
        n += 1
    print(f"    {n} pilares no preto das paredes {preto.astype(int).tolist()}")
    return out



# Térreo 2. Sala de estar (pedido do usuário, 19/10/26: "siga com o item 2 do térreo"). No PDF da Casa A (camada ARQ_LAYOUT
# HUMANIZAÇÃO) o sofá curvo acompanha o tapete redondo pela esquerda, das 12h às 7h, com o encosto na borda do tapete
# (um pouco para fora dela) e o assento em C; sobre o assento, duas almofadas e duas almofadas redondas com pregas (os
# círculos com raios, que a conferência leu como vasos); na ponta de cima do sofá, uma mesinha redonda; à direita, a
# poltrona voltada para a mesa de centro. O motor pôs o sofá ao longo do alto do tapete, até a direita, sem a mesinha
# e sem a poltrona. Sem IA:
# 1. o sofá do motor sai: o tapete volta, copiado em volta do centro dele, no mesmo raio (a borda do tapete fica
#    contínua), de um setor livre à direita, em espelho;
# 2. o sofá do PDF entra no estilo do do render (o tecido creme, o rolo do encosto mais claro, a face do encosto que
#    escurece no vinco com o assento, a borda da frente arredondada e a sombra suave no tapete, da luz do alto à
#    direita, como a da mesa de centro); as divisões do encosto do PDF viram costura fina;
# 3. as almofadas do PDF, com volume e sombra curta; as redondas com as pregas e o botão;
# 4. a poltrona da direita é a poltrona de baixo à direita do render, girada para o contorno do PDF (o ângulo que
#    melhor cobre o contorno, com o encosto para a borda do tapete); a mesinha é a mesinha redonda entre as poltronas
#    de baixo; o pufe/mesinha do render junto ao sofá (o contorno grosso do PDF ali) volta por cima. Cada clone com a
#    sombra nova, na mesma luz.
SALA = {"caixa": (995, 180, 1145, 330),                  # janela de trabalho (px da imagem)
        "tapete": ((1073.27, 255.73), 62.91),           # centro e raio (o círculo da ARQ_MOBILIÁRIO)
        # o sofá do motor (px da imagem), com folga para a sombra dele
        "sofa_velho": [(1026.7, 213.3), (1038.3, 205.0), (1055.0, 200.0), (1073.3, 198.0), (1093.3, 198.7),
                       (1108.3, 203.3), (1118.0, 209.7), (1122.0, 218.3), (1119.3, 227.0), (1112.0, 232.3),
                       (1100.0, 234.0), (1086.7, 231.7), (1075.0, 229.7), (1063.3, 230.0), (1050.0, 231.7),
                       (1040.0, 233.7), (1032.7, 236.0), (1028.7, 240.7), (1028.7, 255.0), (1024.3, 260.3),
                       (1015.3, 261.7), (1007.0, 259.3), (1004.0, 252.0), (1004.3, 240.0), (1008.0, 231.0),
                       (1015.3, 224.3), (1021.7, 218.3)],
        "setor_livre": (-40.0, 15.0),                    # graus, anti-horário a partir do leste
        "pufe": ((1036.7, 251.7), 7.2),
        # pontos dentro de cada parte do sofá (px da imagem); a face do encosto é a região de 20 a 40 mil px (8x)
        "encosto": [(1052.5, 194.5), (1025.9, 211.2), (1009.7, 238.7)],
        "assento": [(1072.3, 213.5), (1030.1, 241.6)],
        "almofadas": [[(1052.8, 202.8), (1054.8, 207.0)], [(1022.2, 244.0), (1017.7, 242.4)]],
        "redondas": [((1044.1, 213.4), 4.7), ((1032.55, 223.05), 4.9)],
        "cores": {"assento": (206, 212, 232), "encosto": (213, 219, 237), "face": (204, 210, 229),
                  "almofada": (211, 217, 237)},       # BGR, do sofá e das almofadas do render
        "sombra": [(-1.4, 1.4, 2.0, 0.30), (0, 0, 0.9, 0.14)],   # dx, dy, sigma (px), força: no tapete
        "poltrona": {"fonte": (1815, 752, 1865, 805), "destino": (1865, 638, 1925, 698),   # pt do PDF
                     "angulo": 226.5, "desvio": (-3.09, 1.95)},
        "mesinha": {"fonte": ((1069.7, 294.5), 6.1), "destino": (1095.5, 222.05)}}


def caminhos_pdf(d, p2r, passos=16):
    """Polilinhas (px da imagem) de um desenho do PDF, uma por subcaminho; as curvas são amostradas."""
    out, atual, ult = [], [], None
    for it in d["items"]:
        if it[0] not in ("l", "c"):
            continue
        a, b = it[1], it[-1]
        if ult is None or abs(a.x - ult.x) + abs(a.y - ult.y) > 0.05:
            if atual:
                out.append(atual)
            atual = [p2r(a.x, a.y)]
        if it[0] == "l":
            atual.append(p2r(b.x, b.y))
        else:
            c1, c2 = it[2], it[3]
            for t in np.linspace(0, 1, passos)[1:]:
                x = (1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * c1.x + 3 * (1 - t) * t ** 2 * c2.x + t ** 3 * b.x
                y = (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * c1.y + 3 * (1 - t) * t ** 2 * c2.y + t ** 3 * b.y
                atual.append(p2r(x, y))
        ult = b
    if atual:
        out.append(atual)
    return [np.float64(c) for c in out]


def sala_estar(out):
    q = SALA
    pg, p2r = pdf_pavimento("Terreo")
    SS = 8
    X0, Y0, X1, Y1 = q["caixa"]
    W, H = (X1 - X0) * SS, (Y1 - Y0) * SS
    (CX, CY), R = q["tapete"]
    fonte = out[Y0:Y1, X0:X1].astype(np.float32)
    reg = fonte.copy()
    org = out.astype(np.float32)

    def ss(c):
        return np.int32(np.round((np.asarray(c, np.float64) - [X0, Y0]) * SS))

    def red(m):
        return cv2.resize(m.astype(np.float32) / (255 if m.dtype == np.uint8 else 1), (X1 - X0, Y1 - Y0),
                          interpolation=cv2.INTER_AREA)

    def dist(m):
        return cv2.distanceTransform((m > 0).astype(np.uint8), cv2.DIST_L2, 5) / SS

    def lisa(t):
        return t * t * (3 - 2 * t)

    def pintar(cor, tom, m):
        nonlocal reg
        a = red(m)[..., None]
        c = cv2.resize(np.float32(cor)[None, None] * tom[..., None] * (m[..., None] / 255.0), (X1 - X0, Y1 - Y0),
                       interpolation=cv2.INTER_AREA)
        reg = reg * (1 - a) + c

    def sombra(m, dx, dy, sig, forca):
        nonlocal reg
        sh = cv2.warpAffine(m.astype(np.float32) / 255, np.float32([[1, 0, dx * SS], [0, 1, dy * SS]]), (W, H))
        reg *= (1 - forca * red(cv2.GaussianBlur(sh, (0, 0), sig * SS) * (1 - m / 255.0)))[..., None]

    # 1. o sofá do motor sai: o tapete, copiado em volta do centro, do setor livre (em espelho)
    mv = np.zeros((Y1 - Y0, X1 - X0), np.uint8)
    cv2.fillPoly(mv, [np.int32(np.round(np.float64(q["sofa_velho"]) - [X0, Y0]))], 1)
    mv = cv2.dilate(mv, np.ones((3, 3), np.uint8)).astype(bool)
    ys, xs = np.mgrid[Y0:Y1, X0:X1] + 0.5
    rr, th = np.hypot(xs - CX, ys - CY), np.degrees(np.arctan2(CY - ys, xs - CX))
    (pcx, pcy), pr = q["pufe"]
    buraco = mv & (np.hypot(xs - pcx, ys - pcy) > pr + 1.3) & (rr <= R + 1.0)
    A0, A1 = q["setor_livre"]
    larg = A1 - A0
    t = np.mod(th - A0, 2 * larg)
    ts = np.radians(A0 + np.where(t < larg, t, 2 * larg - t))
    copia = cv2.remap(fonte, (CX + rr * np.cos(ts) - X0 - 0.5).astype(np.float32),
                      (CY - rr * np.sin(ts) - Y0 - 0.5).astype(np.float32), cv2.INTER_LINEAR)
    a = cv2.GaussianBlur(buraco.astype(np.float32), (0, 0), 0.6)[..., None] * (rr <= R + 1.0)[..., None]
    reg = reg * (1 - a) + copia * a

    # 2. o sofá do PDF: contorno, linhas (barreiras entre as partes) e as partes
    ds = [d for d in pg.get_drawings() if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO"
          and d["rect"].x0 >= 1685 and d["rect"].x1 <= 1850 and d["rect"].y0 >= 578 and d["rect"].y1 <= 730]
    contorno = next(d for d in ds if d["type"] == "f" and d["rect"].width > 100)
    sofa = np.zeros((H, W), np.uint8)
    cv2.fillPoly(sofa, [ss(np.vstack(caminhos_pdf(contorno, p2r, 24)))], 255)
    bar = np.zeros((H, W), np.uint8)
    cost = np.zeros((H, W), np.uint8)
    for d in ds:
        r_ = d["rect"]
        if d["type"] != "s" or r_.x0 < 1690 or (r_.x0 > 1780 and r_.y0 > 680):    # sem a planta e a mesa de centro
            continue
        for c in caminhos_pdf(d, p2r, 24):
            cv2.polylines(bar, [ss(c)], False, 255, 3)
            if 4 < max(r_.width, r_.height) < 9 and r_.x0 > 1700 and r_.y0 < 650:     # as divisões do encosto
                cv2.polylines(cost, [ss(c)], False, 255, 3)
    _, lab = cv2.connectedComponents(((sofa > 0) & (bar == 0)).astype(np.uint8), connectivity=4)

    def regiao(pts=(), ks=()):
        ks = list(ks)
        for x, y in pts:
            j, i = int((y - Y0) * SS), int((x - X0) * SS)
            v = lab[j - 6:j + 7, i - 6:i + 7].ravel()
            ks.append(np.bincount(v[v > 0]).argmax())
        return cv2.dilate(np.isin(lab, ks).astype(np.uint8) * 255, np.ones((5, 5), np.uint8)) & sofa

    areas = np.bincount(lab.ravel())
    encosto = regiao(q["encosto"])
    face = regiao(ks=[k for k in range(1, len(areas)) if 20000 < areas[k] < 40000])
    assento = regiao(q["assento"])
    alm = [regiao(p) for p in q["almofadas"]]
    circ = np.zeros((H, W), np.uint8)
    for c, r_ in q["redondas"]:
        cv2.circle(circ, tuple(ss(c)), int(r_ * SS), 255, -1)
    cor = q["cores"]
    for par in q["sombra"]:
        sombra(sofa, *par)
    base = assento | alm[0] | alm[1] | (circ & sofa)
    pintar(cor["assento"], 0.80 + 0.20 * lisa(np.clip(dist(sofa) / 5.0, 0, 1)), base)          # a frente arredondada
    d_ass = cv2.distanceTransform((assento == 0).astype(np.uint8), cv2.DIST_L2, 5) / SS
    pintar(cor["face"], 0.78 + 0.22 * lisa(np.clip(d_ass / 2.0, 0, 1)), face)                 # escurece no vinco
    pintar(cor["encosto"], 0.80 + 0.20 * lisa(np.clip(dist(encosto) / 1.8, 0, 1)), encosto)   # o rolo
    d_face = cv2.distanceTransform((face == 0).astype(np.uint8), cv2.DIST_L2, 5) / SS
    reg *= (1 - 0.22 * red(np.clip(1 - d_face / 1.4, 0, 1) * (assento > 0)))[..., None]       # o vinco no assento
    reg *= (1 - 0.18 * red(cost & encosto))[..., None]                                           # as costuras

    # 3. as almofadas
    for m in alm:
        m = cv2.erode(m, np.ones((3, 3), np.uint8))
        sombra(m, -0.6, 0.6, 0.8, 0.22)
        pintar(cor["almofada"], 0.86 + 0.14 * lisa(np.clip(dist(m) / 2.4, 0, 1)), m)
    for (cx, cy), r_ in q["redondas"]:
        m = np.zeros((H, W), np.uint8)
        cv2.circle(m, tuple(ss((cx, cy))), int(r_ * SS), 255, -1)
        sombra(m, -0.6, 0.6, 0.8, 0.22)
        pintar(cor["almofada"], 0.86 + 0.14 * lisa(np.clip(dist(m) / 2.6, 0, 1)), m)
        pregas = np.zeros((H, W), np.uint8)
        for k in range(8):
            ang = np.radians(22.5 + 45 * k)
            cv2.line(pregas, tuple(ss((cx, cy))), tuple(ss((cx + 0.92 * r_ * np.cos(ang), cy + 0.92 * r_ * np.sin(ang)))),
                     255, 2)
        reg *= (1 - 0.12 * red(pregas & m))[..., None]
        botao = np.zeros((H, W), np.uint8)
        cv2.circle(botao, tuple(ss((cx, cy))), int(0.55 * SS), 255, -1)
        reg *= (1 - 0.25 * red(botao))[..., None]

    # 4. os clones do render, cada um com a sombra nova
    gx, gy = np.meshgrid(np.arange(W) / SS + X0 + 0.5 / SS, np.arange(H) / SS + Y0 + 0.5 / SS)
    gx1, gy1 = np.meshgrid(np.arange(X1 - X0) + X0 + 0.5, np.arange(Y1 - Y0) + Y0 + 0.5)

    def clonar(dentro, c_src, c_dst, ang, par):
        nonlocal reg
        ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
        ux, uy = gx - c_dst[0], gy - c_dst[1]
        m = dentro(c_src[0] + ca * ux + sa * uy, c_src[1] - sa * ux + ca * uy).astype(np.uint8) * 255
        sombra(m, *par)
        ux, uy = gx1 - c_dst[0], gy1 - c_dst[1]
        cor_ = cv2.remap(org, (c_src[0] + ca * ux + sa * uy - 0.5).astype(np.float32),
                         (c_src[1] - sa * ux + ca * uy - 0.5).astype(np.float32), cv2.INTER_CUBIC)
        a = red(m)[..., None]
        reg = reg * (1 - a) + cor_ * a

    def poli(caixa):
        d = next(d for d in pg.get_drawings() if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and d["type"] == "f"
                 and d["rect"].x0 >= caixa[0] and d["rect"].x1 <= caixa[2] and d["rect"].y0 >= caixa[1]
                 and d["rect"].y1 <= caixa[3])
        return np.vstack(caminhos_pdf(d, p2r, 16))
    qp = q["poltrona"]
    pf, pdst = poli(qp["fonte"]), poli(qp["destino"])
    mpf = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mpf, [ss(pf)], 255)
    mpf = cv2.dilate(mpf, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * 0.9 * SS) + 1,) * 2))

    def na_poltrona(sx, sy):
        return mpf[np.clip(((sy - Y0) * SS).astype(int), 0, H - 1), np.clip(((sx - X0) * SS).astype(int), 0, W - 1)] > 0

    def no_circulo(c, r_):
        return lambda sx, sy: np.hypot(sx - c[0], sy - c[1]) <= r_
    clonar(na_poltrona, pf.mean(axis=0), pdst.mean(axis=0) + qp["desvio"], qp["angulo"], (-1.2, 1.2, 1.6, 0.28))
    (mc, mr), mdst = q["mesinha"]["fonte"], q["mesinha"]["destino"]
    clonar(no_circulo(mc, mr), mc, mdst, 0.0, (-0.8, 0.8, 1.0, 0.28))
    clonar(no_circulo((pcx, pcy), pr), (pcx, pcy), (pcx, pcy), 0.0, (-0.8, 0.8, 1.0, 0.25))
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    sala de estar: sofá do motor fora ({int(buraco.sum())} px de tapete de volta); sofá curvo do PDF pela "
          f"esquerda do tapete, com 2 almofadas e 2 redondas; poltrona da direita (girada {qp['angulo']}°) e mesinha")
    return out




# Térreo 8. Jardim de 4,79 m² (pedido do usuário, 19/10/26: "aqui é um jardim verde com plantas"; item 8 da
# conferência). O motor fez o jardim como piso claro, vazio. No PDF da Casa A ele tem a forração (as setinhas da
# hachura de grama) até a faixa de piso junto à porta da direita, e três touceiras. Entra o gramado do próprio Térreo
# (um trecho do gramado ao lado, do tamanho do canteiro), com a sombra curta das paredes em volta (a luz vem do alto à
# direita, como no resto da prancha), e as três touceiras, nas posições e no tamanho do PDF: clones da palmeira em
# estrela do jardim lateral do render (já sobre a grama, com a sua sombra), recortada do gramado pela cor, cada uma
# girada e espelhada para não repetir, com uma sombra curta a mais no canteiro.
JARDIM = {"canteiro": (783.0, 856.0, 890.0, 897.8),       # px da imagem: do PDF (a faixa à direita fica piso)
          "fonte_grama": (600, 885),                      # canto do trecho do gramado ao lado (px)
          "grama_ref": (600, 885, 720, 935),              # gramado limpo: a cor de referência para recortar a planta
          "parede_sombra": (0.22, 2.2),                   # força e alcance da sombra das paredes (px)
          # touceiras: centro (px), raio no PDF (px), planta-fonte (centro, raio) e giro (graus) / espelho
          "touceiras": [((805.6, 877.4), 14.5, ((1500.0, 485.0), 26.0), 15, False),
                        ((835.5, 876.7), 14.5, ((1500.0, 485.0), 26.0), 130, True),
                        ((866.7, 876.7), 14.5, ((1500.0, 485.0), 26.0), 250, False)],
          "sombra": (-1.2, 1.2, 1.2, 0.30)}


def jardim(out):
    q = JARDIM
    x0, y0, x1, y1 = q["canteiro"]
    xa, ya, xb, yb = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    reg = out[ya:yb, xa:xb].astype(np.float32)
    fx, fy = q["fonte_grama"]
    grama = out[fy:fy + yb - ya, fx:fx + xb - xa].astype(np.float32)
    a = (cobertura_colunas(x0, x1, xa, xb)[None, :] * cobertura_linhas(y0, y1, ya, yb)[:, None])[..., None]
    # sombra das paredes: mais forte junto à de cima e à da direita (a luz vem do alto à direita)
    forca, alc = q["parede_sombra"]
    ys = np.arange(ya, yb)[:, None] + 0.5
    xs = np.arange(xa, xb)[None, :] + 0.5
    som = np.maximum(np.clip(1 - (ys - y0) / alc, 0, 1), np.clip(1 - (x1 - xs) / alc, 0, 1) * 0.6)
    som = np.maximum(som, np.clip(1 - (xs - x0) / alc, 0, 1) * 0.5)
    som = np.maximum(som, np.clip(1 - (y1 - ys) / alc, 0, 1) * 0.5)
    grama *= (1 - forca * som)[..., None]
    out[ya:yb, xa:xb] = np.clip(np.round(reg * (1 - a) + grama * a), 0, 255).astype(np.uint8)
    # a planta-fonte: o que não é gramado (distância de cor ao gramado limpo, em Lab), com a borda suave
    fonte = cv2.imread(str(APROVADAS["Terreo"]))
    lab = cv2.cvtColor(fonte, cv2.COLOR_BGR2LAB).astype(np.float32)
    gx0, gy0, gx1, gy1 = q["grama_ref"]
    gref = lab[gy0:gy1, gx0:gx1].reshape(-1, 3)
    mu, sd = gref.mean(axis=0), np.maximum(gref.std(axis=0), 1)
    z = np.sqrt((((cv2.GaussianBlur(lab, (0, 0), 1.0) - mu) / sd) ** 2).sum(axis=2))
    planta = cv2.GaussianBlur((cv2.GaussianBlur((z > 2.2).astype(np.float32), (0, 0), 1.5) > 0.4).astype(np.float32),
                              (0, 0), 0.6)
    fonte = fonte.astype(np.float32)
    for (cx_, cy_), raio, ((sx, sy), sr), giro, espelho in q["touceiras"]:
        k = raio / sr
        t = np.radians(giro)
        R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]) * k
        if espelho:
            R = R @ np.diag([-1, 1])
        Ri = np.linalg.inv(R)                               # destino -> fonte: p_fonte = s + Ri (p - c)
        ja, jb = int(cx_ - raio - 4), int(cx_ + raio + 5)
        ia, ib = int(cy_ - raio - 4), int(cy_ + raio + 5)
        t0 = np.array([sx, sy]) - Ri @ np.array([cx_, cy_]) + Ri @ np.array([ja, ia])
        M = np.hstack([Ri, t0[:, None]]).astype(np.float32)
        cor = cv2.warpAffine(fonte, M, (jb - ja, ib - ia), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP)
        m = cv2.warpAffine(planta, M, (jb - ja, ib - ia), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        yy, xx = np.mgrid[ia:ib, ja:jb] + 0.5
        m *= np.clip((raio + 1.0 - np.hypot(xx - cx_, yy - cy_)) / 2.0, 0, 1)   # só a planta-fonte, sem vizinhas
        sdx, sdy, ssig, sf = q["sombra"]
        sh = cv2.warpAffine(m, np.float32([[1, 0, sdx], [0, 1, sdy]]), (jb - ja, ib - ia))
        sh = cv2.GaussianBlur(sh, (0, 0), ssig) * (1 - m)
        jan = out[ia:ib, ja:jb].astype(np.float32) * (1 - sf * sh)[..., None]
        jan = jan * (1 - m[..., None]) + cor * m[..., None]
        out[ia:ib, ja:jb] = np.clip(np.round(jan), 0, 255).astype(np.uint8)
    print(f"    jardim: gramado do Térreo em x {x0}-{x1}, y {y0}-{y1} px, com a sombra das paredes; "
          f"{len(q['touceiras'])} touceiras do PDF (a palmeira em estrela do jardim lateral)")
    return out


# Térreo, tanques (pedido do usuário, 19/10/26: "aqui são dois tanques de água com torneiras, na área de serviço"). O
# motor fez duas peças lilás com um símbolo estranho. No PDF da Casa A (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS) é a bancada
# junto à parede de cima, com dois tanques de louça lado a lado: cada um com o esfregador (a faixa de cima, com a borda
# de baixo arredondada) e a bacia funda, e a torneira de parede no meio, a bica descendo até o esfregador. Entram
# nessas medidas, no padrão das cubas aprovadas: a bancada no quartzo claro das bancadas, com a borda fina e a sombra
# curta; cada tanque de louça branca com o contorno fino, as nervuras do esfregador, a bacia escurecendo da borda ao
# fundo e a válvula; a torneira cromada, da parede.
TANQUES = {"bancada": [(1530.83, 1605.1, 1610.77, 1642.51), (1610.77, 1605.1, 1613.03, 1644.78)],
           "tanques": [{"caixa": (1532.7, 1610.37, 1568.64, 1640.64), "esfregador": (1533.66, 1611.33, 1567.68, 1622.67),
                        "bacia": (1533.66, 1618.13, 1567.68, 1639.68), "torneira": (1549.99, 1605.1, 1551.35, 1618.36)},
                       {"caixa": (1572.39, 1610.37, 1608.33, 1640.64), "esfregador": (1573.35, 1611.33, 1607.37, 1622.67),
                        "bacia": (1573.35, 1618.13, 1607.37, 1639.68), "torneira": (1589.67, 1605.1, 1591.04, 1618.36)}],
           "nervuras": 5}


def tanques(out):
    from retoque_subsolo_casae import (Tela, SOMBRA, LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO, CROMO,
                                       CROMO_CLARO, CROMO_ESCURO, QUARTZO, SS)
    q = TANQUES
    _, p2r = pdf_pavimento("Terreo")
    caixa = (q["bancada"][0][0], q["bancada"][0][1], q["bancada"][1][2], q["bancada"][1][3])
    tl = Tela(out, p2r, caixa)
    for b in q["bancada"]:
        m = tl.ret(b)
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, QUARTZO)
        tl.contorno(m, 0.35, (150, 153, 155))
    for t in q["tanques"]:
        x0, y0, x1, y1 = t["caixa"]
        c = tl.ret(t["caixa"], 3.0)
        tl.sombra(c, dx=-0.4, dy=0.4, sigma=0.5, forca=0.2)
        tl.pintar(c, LOUCA_CONTORNO)
        tl.pintar(tl.ret((x0 + 0.8, y0 + 0.8, x1 - 0.8, y1 - 0.8), 2.6), LOUCA)
        bx0, by0, bx1, by1 = t["bacia"]
        for i in range(6):                   # a bacia, da borda ao fundo
            k = i / 5
            cor = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
            ins = 0.5 + k * 3.2
            tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.8, 2.6 - k)), cor)
        ex0, ey0, ex1, ey1 = t["esfregador"]  # o esfregador: plano, um pouco acima da bacia, com as nervuras
        e = tl.ret(t["esfregador"], 2.6)
        tl.sombra(e, dx=0, dy=0.5, sigma=0.4, forca=0.25)
        tl.pintar(e, LOUCA)
        tl.contorno(e, 0.3, LOUCA_CONTORNO)
        n = q["nervuras"]
        for k in range(1, n + 1):
            xk = ex0 + 3 + (ex1 - ex0 - 6) * k / (n + 1)
            tl.pintar(tl.ret((xk - 0.3, ey0 + 2.5, xk + 0.3, ey1 - 2.0)), BACIA_BORDA, 0.8)
        vx, vy = tl.pt((bx0 + bx1) / 2, (by0 + by1) / 2 + 3)
        v = tl.vazia()
        cv2.circle(v, (int(vx), int(vy)), int(1.1 * SS), 255, -1)
        tl.pintar(v, CROMO_ESCURO)
        tx0, ty0, tx1, ty1 = t["torneira"]  # da parede de cima, descendo até o esfregador
        m = tl.ret(t["torneira"], 0.6)
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, CROMO_ESCURO)
        tl.pintar(tl.ret((tx0 + 0.25, ty0, (tx0 + tx1) / 2, ty1 - 0.4), 0.3), CROMO_CLARO)
        base = tl.vazia()
        cx, cy = tl.pt((tx0 + tx1) / 2, ty0 + 1.0)
        cv2.circle(base, (int(cx), int(cy)), int(1.0 * SS), 255, -1)
        tl.pintar(base, CROMO)
    out = tl.gravar()
    (a, b), (c, d) = p2r(*caixa[:2]), p2r(*caixa[2:])
    print(f"    área de serviço: bancada x {a:.1f}-{c:.1f}, y {b:.1f}-{d:.1f} px, com os dois tanques e as torneiras do PDF")
    return out


# Térreo, gás (pedidos do usuário, 19/10/26: "piso da área do Gás é marrom granito" e "faltando a representação da
# porta do gás e seu arco"). O motor fez o piso do gás em lilás e a porta como uma faixa cinza, sem folhas nem arcos.
# No PDF da Casa A o gás tem porta de duas folhas, que abrem para a área de serviço descoberta. Entram: o granito
# marrom da área de serviço (um trecho limpo dela, no tom dela), do fundo do gás até a face de fora da parede; e as
# duas folhas abertas, nas medidas do PDF, com os arcos finos (como as portas aprovadas, `desenhar_porta`), mais
# escuros que os do granito, para lerem sobre a pedra portuguesa.
GAS = {"piso": (899.3, 836.9, 932.4, 855.7),          # px da imagem: dentro das paredes do PDF, até a face de fora
       "fonte_granito": (940, 826),                   # canto de um trecho limpo do granito da área de serviço (px)
       "portas": [((1501.24, 1789.35, 1503.5, 1811.85), (1501.24, 1786.51, 1529.41, 1814.69)),
                  ((1555.32, 1789.35, 1557.59, 1811.85), (1529.41, 1786.51, 1557.59, 1814.69))],
       "arco_pedra": ((92, 94, 96), 0.5)}             # cor e largura do arco sobre a pedra portuguesa


def porta_pdf(out, pg, p2r, folha, arco, cor_arco, larg):
    """Folha (retângulo do PDF, em pt) e arco (bbox da curva do PDF) de uma porta, como as aprovadas
    (`retoque_subsolo_casae.desenhar_porta`), com a cor e a largura do arco dadas."""
    import retoque_subsolo_casae as RS
    RS.PORTA["arco"]["_ajuste"] = (cor_arco, larg)
    return RS.desenhar_porta(out, pg, p2r, folha, arco, "_ajuste")


def gas(out):
    q = GAS
    x0, y0, x1, y1 = q["piso"]
    xa, ya, xb, yb = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    fx, fy = q["fonte_granito"]
    gran = out[fy:fy + yb - ya, fx:fx + xb - xa].astype(np.float32)
    a = (cobertura_colunas(x0, x1, xa, xb)[None, :] * cobertura_linhas(y0, y1, ya, yb)[:, None])[..., None]
    reg = out[ya:yb, xa:xb].astype(np.float32)
    out[ya:yb, xa:xb] = np.clip(np.round(reg * (1 - a) + gran * a), 0, 255).astype(np.uint8)
    pg, p2r = pdf_pavimento("Terreo")
    for folha, arco in q["portas"]:
        out = porta_pdf(out, pg, p2r, folha, arco, *q["arco_pedra"])
    print(f"    gás: piso de granito em x {x0}-{x1}, y {y0}-{y1} px; porta de duas folhas com os arcos do PDF")
    return out


# Térreo, porta do jardim (pedido do usuário, 19/10/26: "faltando também as duas portas da área de jardim e seus
# arcos"). No PDF da Casa A o jardim de 4,79 m² abre para a área de serviço descoberta por uma porta de uma folha, no
# vão da parede da direita, que abre para fora; a folha aberta fica junto à parede de baixo (as duas folhas vizinhas
# são as do gás, já feitas). O render tinha só o vão. Entra a folha aberta e o arco, como a porta do gás.
PORTA_JARDIM = {"folha": (1502.48, 1854.26, 1542.17, 1856.53), "arco": (1499.65, 1811.17, 1545.0, 1856.53)}


def porta_jardim(out):
    pg, p2r = pdf_pavimento("Terreo")
    out = porta_pdf(out, pg, p2r, PORTA_JARDIM["folha"], PORTA_JARDIM["arco"], *GAS["arco_pedra"])
    print("    jardim: porta de uma folha para a área descoberta, com o arco do PDF")
    return out


# Térreo, portões (pedido do usuário, 19/10/26: "representar os portões, de ambos os lados, da área descoberta"). No
# PDF da Casa A (ARQ_PAREDE) cada lado da área de serviço descoberta tem um portão de correr de duas folhas
# desencontradas, com os batentes nas pontas: à esquerda, para o gramado; à direita, para o acesso de pedestres. O
# render tinha só uma faixa clara com uma borda escura. A faixa sai (em cada linha, o piso de cada lado continua em
# espelho: a grama e a pedra portuguesa) e entram as folhas nas medidas do PDF, em metal (o alumínio das portas de
# vidro do Subsolo), com a borda fina escura e a linha do meio de cada folha.
PORTOES = {
    "lados": [
        {"nome": "esquerdo", "faixa": (891, 899, 903, 1005),     # px da imagem: x0, x1, linhas y0..y1
         "folhas": [(1493.98, 1873.82, 1496.81, 1967.36), (1491.14, 1962.83, 1493.98, 2056.37)],
         "batentes": [(1491.14, 1871.55, 1499.65, 1873.82), (1491.14, 2056.37, 1499.65, 2058.64)]},
        {"nome": "direito", "faixa": (1006, 1012, 857, 1005),
         "folhas": [(1695.24, 1788.78, 1698.07, 1924.84), (1698.07, 1920.31, 1700.91, 2056.37)],
         "batentes": [(1692.41, 1786.51, 1700.91, 1788.78), (1692.41, 2056.37, 1700.91, 2058.64)]}],
    "metal": (150, 153, 156), "borda": ((70, 72, 74), 0.35), "meio": ((112, 115, 118), 0.3)}


def refazer_faixa(out, faixa):
    """Uma faixa vertical (x0..x1, linhas y0..y1) some: cada metade recebe, em espelho, o que está do seu lado."""
    x0, x1, y0, y1 = faixa
    meio = (x0 + x1) / 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            out[y, x] = out[y, x0 - 1 - (x - x0)] if x <= meio else out[y, x1 + 1 + (x1 - x)]


def portoes(out):
    from retoque_subsolo_casae import Tela
    q = PORTOES
    _, p2r = pdf_pavimento("Terreo")
    for lado in q["lados"]:
        refazer_faixa(out, lado["faixa"])
        caixa = [f(v) for f, v in zip((min, min, max, max), zip(*(lado["folhas"] + lado["batentes"])))]
        tl = Tela(out, p2r, caixa)
        for r in lado["folhas"] + lado["batentes"]:
            m = tl.ret(r)
            tl.sombra(m, dx=-0.5, dy=0.5, sigma=0.5, forca=0.25)
        for r in lado["batentes"]:
            m = tl.ret(r)
            tl.pintar(m, q["metal"])
            tl.contorno(m, q["borda"][1], q["borda"][0])
        for f in lado["folhas"]:
            m = tl.ret(f)
            tl.pintar(m, q["metal"])
            xm = (f[0] + f[2]) / 2
            tl.pintar(m & tl.ret((xm - 0.3, f[1], xm + 0.3, f[3])), q["meio"][0])
            tl.contorno(m, q["borda"][1], q["borda"][0])
        out = tl.gravar()
        print(f"    portão {lado['nome']}: faixa do motor refeita; {len(lado['folhas'])} folhas e "
              f"{len(lado['batentes'])} batentes do PDF")
    return out


# Térreo 9. Escada caracol da área de serviço (pedido do usuário, 19/10/26: "vamos melhorar a representação dessa
# escada caracol. somente uma parte será representada, sendo a outra esmaecida. note onde o arco está em destaque, a
# qual é a área que fica bem destacada, ao contrário da área tracejada"; item 9 da conferência). O motor fez só um
# círculo com doze raios escuros sobre o granito. No PDF da Casa A (ARQ_ESCADAS E RAMPAS e ARQ_ELEMENTOS FIXOS) a
# escada sobe da direita (o "S"), no sentido anti-horário: os degraus 1 a 7, até a linha de corte, são cheios, com o
# corrimão de madeira cheio por fora; o resto (8 em diante, acima do corte) é tracejado. Entra assim:
# - o círculo do motor sai: o granito em volta, tecido de trechos limpos dele (image quilting), na luz do lugar;
# - degraus 1 a 7 (de 0° a 131,4°, os raios do PDF): pisos de madeira clara (a da mesa do render, com o veio no
#   sentido do raio), do pilar central à borda, com o sombreamento de subida das escadas aprovadas (cada degrau um
#   pouco mais claro que o de baixo e a sombra curta de cada espelho no degrau de baixo), sem linhas; o corrimão de
#   madeira por fora, cheio; a sombra curta da escada no granito;
# - degraus 8 em diante: os mesmos pisos, esmaecidos (misturados ao granito), com os espelhos em traço claro;
# - o pilar central, em metal.
# R14 e seção 5 das regras (pente fino de 21/10/26, item 1 do Térreo): em cada bocel, uma linha cinza suave e a
# sombra curta no degrau de baixo; depois do corte, os bocéis tracejados (a projeção); a linha de corte não é desenhada;
# o triângulo de orientação no início (24 x 26 cm, cinza-escuro, a 10 cm). Os números das escadas aprovadas da Casa E
# (retoque_terreo_casae.ESCADA_LINHAS), em pt do PDF.
R14 = {"bocel": 0.80, "bocel_pt": 0.55, "sombra": (0.16, 5.67), "tracejado": (160, 160, 164), "tracejado_px": 0.5,
       "traco_pt": 5.7, "vao_pt": 2.8, "triangulo": {"base_pt": 13.6, "altura_pt": 14.7, "recuo_pt": 5.67,
                                                      "cor": (88, 88, 92)}}


def r14_tracejado(forma, pts, k_pt, larg_px, ss=8):
    """Máscara (0 a 1, no quadro `forma`) de uma polilinha tracejada no passo da R14 (traço e vão em pt; k_pt: px por
    pt), desenhada em ss x e reduzida."""
    q = R14
    h, w = forma
    m = np.zeros((h * ss, w * ss), np.uint8)
    lw = max(1, int(round(larg_px * ss)))
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        comp = np.hypot(xb - xa, yb - ya)
        t = 0.0
        while t < comp:
            t1 = min(comp, t + q["traco_pt"] * k_pt)
            u = (xa + (xb - xa) * t / comp, ya + (yb - ya) * t / comp)
            v = (xa + (xb - xa) * t1 / comp, ya + (yb - ya) * t1 / comp)
            cv2.line(m, (int(round(u[0] * ss)), int(round(u[1] * ss))), (int(round(v[0] * ss)), int(round(v[1] * ss))),
                     255, lw, cv2.LINE_AA)
            t = t1 + q["vao_pt"] * k_pt
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def r14_poligono(forma, pts, ss=8):
    h, w = forma
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round(np.float64(pts) * ss))], 255, cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def r14_linha(forma, pts, larg_px, ss=8):
    h, w = forma
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.polylines(m, [np.int32(np.round(np.float64(pts) * ss))], False, 255, max(1, int(round(larg_px * ss))),
                  cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def r14_triangulo(forma, base, direcao, k_pt, escala=1.0):
    """O triângulo de orientação: a base centrada em `base` (px), a ponta na `direcao` (vetor unitário)."""
    t = R14["triangulo"]
    bx, by = base
    dx, dy = direcao
    alt, meia = t["altura_pt"] * k_pt * escala, t["base_pt"] * k_pt * escala / 2
    pts = [(bx + dx * alt, by + dy * alt), (bx - dy * meia, by + dx * meia), (bx + dy * meia, by - dx * meia)]
    return r14_poligono(forma, pts)


CARACOL = {"centro": (1756.4, 1718.5), "r_corrimao": (50.5, 53.4), "r_piso": 50.5, "r_pilar": 4.0,   # pt do PDF
           "angulos": [0.0, 18.0, 36.4, 55.2, 74.2, 93.3, 112.5, 131.4],      # os raios cheios do PDF (graus)
           "fontes_granito": [(960, 786, 1010, 846)],    # trecho limpo do granito, à esquerda da escada (px)
           "madeira": (1053, 337, 1073, 360),                                 # trecho limpo da mesa (px)
           "tom": (0.86, 1.0), "espelho": (0.35, 2.2),     # degrau 1 a 7; sombra do espelho: força e alcance (px)
           "esmaecer": 0.22, "espelho_esm": ((170, 170, 170), 0.25),
           "corrimao": ((52, 92, 138), (30, 50, 70)), "pilar": (88, 90, 92),
           "sombra": (-1.0, 1.0, 1.2, 0.35),
           # R14 (21/10/26): linha suave nos espelhos dos degraus cheios, os espelhos esmaecidos tracejados e o
           # triângulo no degrau 1, apontando para a subida (anti-horário). No degrau de 18° o triângulo da regra não
           # cabe: entra a 70%, a 38 pt do centro
           "r14": {"triangulo_r_pt": 38.0, "triangulo_escala": 0.7, "tracejado_forca": 0.55}}


def caracol(out):
    from retoque_bege_bahia_terreo import quilting
    q = CARACOL
    _, p2r = pdf_pavimento("Terreo")
    cx, cy = p2r(*q["centro"])
    k = p2r(q["centro"][0] + 100, q["centro"][1])[0] - cx
    k /= 100                                               # px por pt
    Rc0, Rc1 = q["r_corrimao"][0] * k, q["r_corrimao"][1] * k
    Rp, rn = q["r_piso"] * k, q["r_pilar"] * k
    SS = 8
    x0, y0 = int(cx - Rc1 - 6), int(cy - Rc1 - 6)
    x1, y1 = int(cx + Rc1 + 7), int(cy + Rc1 + 7)
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    # 1. o granito: tecido de trechos limpos, na luz do lugar (a média do anel em volta do disco)
    fontes = []
    for a, b, c, d in q["fontes_granito"]:
        g = out[b:d, a:c].astype(np.float32)
        g = g / g.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    tex = quilting(fontes, h, w, p=16, sobra=5, candidatos=500, rng=np.random.default_rng(6420))
    yy, xx = np.mgrid[y0:y1, x0:x1] + 0.5
    rr = np.hypot(xx - cx, yy - cy)
    th = np.degrees(np.arctan2(cy - yy, xx - cx)) % 360
    lum = reg.mean(axis=2)
    anel = (rr > Rc1 + 1.5) & (rr < Rc1 + 6) & (lum > 35) & (lum < 120)   # só o granito (sem a parede e a porta)
    luz = np.median(reg[anel], axis=0)
    disco = np.clip(Rc1 + 1.5 - rr, 0, 1)[..., None]
    reg = reg * (1 - disco) + tex * luz * disco
    granito = reg.copy()

    # coberturas em SS x
    def em_ss(f):
        ys, xs = np.mgrid[y0 * SS:y1 * SS, x0 * SS:x1 * SS]
        return f((xs + 0.5) / SS, (ys + 0.5) / SS)
    R_ss = em_ss(lambda X, Y: np.hypot(X - cx, Y - cy))
    T_ss = em_ss(lambda X, Y: np.degrees(np.arctan2(cy - Y, X - cx)) % 360)

    def red(m):
        return cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    ang = q["angulos"]
    passo = (ang[-1] - ang[0]) / (len(ang) - 1)
    bordas = ang + [ang[-1] + passo * i for i in range(1, 40) if ang[-1] + passo * i < 360] + [360.0]
    a0, b0, a1, b1 = q["madeira"]
    mad = cv2.imread(str(APROVADAS["Terreo"]))[b0:b1, a0:a1].astype(np.float32)
    # piso de cada degrau: a madeira no sistema (raio, ângulo), veio no sentido do raio
    u = np.clip((rr - rn) / (Rp - rn), 0, 1) * (mad.shape[0] - 1)
    piso = np.zeros_like(reg)
    for i in range(len(bordas) - 1):
        t0, t1 = bordas[i], bordas[i + 1]
        dentro = (th >= t0) & (th < t1)
        v = ((th - t0) / (t1 - t0) * (mad.shape[1] - 1) + 7 * i) % (mad.shape[1] - 1)
        cor = cv2.remap(mad, v.astype(np.float32), u.astype(np.float32), cv2.INTER_LINEAR)
        piso[dentro] = cor[dentro]
    na_escada = red((R_ss > rn) & (R_ss <= Rp))
    nvis = len(ang) - 1
    vis_ss = (T_ss >= ang[0]) & (T_ss < ang[-1])
    vis = red(vis_ss & (R_ss <= Rc1)) 
    # 2. a parte esmaecida (acima do corte): o piso misturado ao granito, os espelhos em traço claro
    e = q["esmaecer"]
    a_esm = (na_escada * (1 - red(vis_ss)))[..., None] * e
    reg = reg * (1 - a_esm) + piso * a_esm
    if "r14" in q:
        # R14: os espelhos acima do corte tracejados (a projeção), no cinza e no traço das escadas da Casa E
        tr = np.zeros((h, w), np.float32)
        for t in bordas[nvis:-1]:
            ca, sa = np.cos(np.radians(t)), -np.sin(np.radians(t))
            tr = np.maximum(tr, r14_tracejado((h, w), [(cx - x0 + ca * rn, cy - y0 + sa * rn),
                                                       (cx - x0 + ca * Rp, cy - y0 + sa * Rp)], k, R14["tracejado_px"]))
        tr *= q["r14"]["tracejado_forca"]                     # no granito escuro, o cinza claro inteiro marcava demais
        reg = reg * (1 - tr[..., None]) + np.float32(R14["tracejado"]) * tr[..., None]
    else:
        cor_e, larg_e = q["espelho_esm"]
        for t in bordas[nvis:-1]:
            lin = (np.abs(((T_ss - t + 180) % 360) - 180) * np.pi / 180 * R_ss < larg_e / 2) & (R_ss > rn) & (R_ss <= Rp)
            al = red(lin)[..., None] * 0.45
            reg = reg * (1 - al) + np.float32(cor_e) * al
    # 3. a parte cheia: a sombra curta da escada no granito, os pisos com o sombreamento de subida, o corrimão
    sdx, sdy, ssig, sf = q["sombra"]
    m = red(vis_ss & (R_ss <= Rc1))
    sh = cv2.GaussianBlur(cv2.warpAffine(m, np.float32([[1, 0, sdx], [0, 1, sdy]]), (w, h)), (0, 0), ssig) * (1 - m)
    reg *= (1 - sf * sh)[..., None]
    tmin, tmax = q["tom"]
    forca, alc = q["espelho"]
    fator = np.ones((h * SS, w * SS), np.float32)
    for i in range(nvis):
        t0, t1 = ang[i], ang[i + 1]
        dentro = (T_ss >= t0) & (T_ss < t1)
        tom = tmin + (tmax - tmin) * i / (nvis - 1)
        dist = (t1 - T_ss) * np.pi / 180 * R_ss          # distância (px) ao espelho do degrau de cima
        f = tom * (1 - forca * np.clip(1 - dist / alc, 0, 1)) if i < nvis - 1 else np.full_like(dist, tom)
        fator = np.where(dentro, f, fator)
    a_vis = (red(vis_ss & (R_ss > rn) & (R_ss <= Rp)))[..., None]
    reg = reg * (1 - a_vis) + piso * red(np.where(vis_ss, fator, 1))[..., None] * a_vis
    if "r14" in q:
        # R14: a linha suave em cada bocel dos degraus cheios (o espelho do degrau de baixo e o início, no 0°)
        lb = np.zeros((h, w), np.float32)
        for t in ang[:-1]:
            ca, sa = np.cos(np.radians(t)), -np.sin(np.radians(t))
            lb = np.maximum(lb, r14_linha((h, w), [(cx - x0 + ca * rn, cy - y0 + sa * rn),
                                                   (cx - x0 + ca * Rp, cy - y0 + sa * Rp)], R14["bocel_pt"] * k))
        reg *= (1 - (1 - R14["bocel"]) * lb)[..., None]
        # o triângulo no degrau 1, apontando para a subida (anti-horário: o sentido de theta crescente)
        tm = np.radians((ang[0] + ang[1]) / 2)
        rt = q["r14"]["triangulo_r_pt"] * k
        esc = q["r14"]["triangulo_escala"]
        alt = R14["triangulo"]["altura_pt"] * k * esc
        dirc = (-np.sin(tm), -np.cos(tm))
        t0 = np.radians(ang[0]) + (np.radians(ang[1] - ang[0]) * rt - alt) / 2 / rt     # centrado no degrau
        base = (cx - x0 + np.cos(t0) * rt, cy - y0 - np.sin(t0) * rt)
        tri = r14_triangulo((h, w), base, dirc, k, esc)
        reg = reg * (1 - tri[..., None]) + np.float32(R14["triangulo"]["cor"]) * tri[..., None]
    corr = vis_ss & (R_ss > Rc0) & (R_ss <= Rc1)
    reg = reg * (1 - red(corr)[..., None]) + np.float32(q["corrimao"][0]) * red(corr)[..., None]
    borda = vis_ss & (np.abs(R_ss - Rc1) < 0.25)
    reg = reg * (1 - red(borda)[..., None]) + np.float32(q["corrimao"][1]) * red(borda)[..., None]
    # 4. o pilar central, em metal, com um brilho
    pil = R_ss <= rn
    reg = reg * (1 - red(pil)[..., None]) + np.float32(q["pilar"]) * red(pil)[..., None]
    bri = np.hypot(em_ss(lambda X, Y: X - cx + rn * 0.3), em_ss(lambda X, Y: Y - cy + rn * 0.3)) <= rn * 0.35
    reg = reg * (1 - 0.5 * red(bri)[..., None]) + 200 * 0.5 * red(bri)[..., None]
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    caracol: centro ({cx:.1f}, {cy:.1f}) px, raio {Rc1:.1f} px; degraus 1 a {nvis} cheios "
          f"({ang[0]}° a {ang[-1]}°), {len(bordas) - 1 - nvis} esmaecidos")
    return out


# Térreo, portas no granito (pedidos do usuário, 19/10/26: "melhorar a representação dos arcos e portas. lembrando que
# os arcos das portas no marrom granito são em cinza, com traço fino" e, no banho do motorista, "o arco da porta de
# entrada [...] está imperceptível, devendo ser em cinza, como de regra"). As quatro portas de giro sobre o granito (a
# da cozinha para a área de serviço, a da despensa, a do banho e a do quarto do motorista): o motor fez as folhas
# grossas e um pouco fora do lugar, e os arcos não se viam. A folha do motor sai (os px claros na faixa dela viram o
# granito logo ao lado, do lado de fora da faixa) e entram a folha e o arco do PDF, como as portas aprovadas, o arco
# no cinza fino da regra (160, 161, 160; 0,45 px), o das Casas C, D e E.
PORTAS_GRANITO = {"portas": [  # (nome, folha, arco), em pt do PDF
    ("cozinha para a área de serviço", (1766.11, 1613.6, 1817.13, 1615.87), (1766.11, 1613.6, 1817.13, 1664.62)),
    ("despensa", (1832.72, 1678.8, 1834.99, 1718.48), (1832.72, 1678.8, 1872.41, 1718.48)),
    ("banho do motorista", (2103.43, 1455.43, 2143.11, 1457.69), (2103.43, 1418.01, 2143.11, 1457.69)),
    ("quarto do motorista", (2274.08, 1415.17, 2276.34, 1466.2), (2225.32, 1415.17, 2276.34, 1466.2))],
    "arco": ((160, 161, 160), 0.45), "claro": 30, "faixa": 3}


def portas_granito(out):
    q = PORTAS_GRANITO
    pg, p2r = pdf_pavimento("Terreo")
    for nome, folha, arco in q["portas"]:
        (a, b), (c, d) = p2r(*folha[:2]), p2r(*folha[2:])
        horiz = (c - a) > (d - b)
        f = q["faixa"]
        x0, y0 = int(np.floor(a)) - (1 if horiz else f), int(np.floor(b)) - (f if horiz else 1)
        x1, y1 = int(np.ceil(c)) + (1 if horiz else f), int(np.ceil(d)) + (f if horiz else 1)
        reg = out[y0:y1, x0:x1].astype(np.float32)
        lum = reg.mean(axis=2)
        gran = np.median(lum[lum < np.percentile(lum, 50)])
        claro = lum > gran + q["claro"]
        claro = cv2.dilate(claro.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        ys, xs = np.nonzero(claro)
        n = 0
        for y, x in zip(ys + y0, xs + x0):
            cands = [(y, x + f + 2), (y, x - f - 2)] if not horiz else [(y + f + 2, x), (y - f - 2, x)]
            melhor = min(cands, key=lambda t: abs(out[t].astype(np.float32).mean() - gran))
            out[y, x] = out[melhor]
            n += 1
        out = porta_pdf(out, pg, p2r, folha, arco, *q["arco"])
        print(f"    porta {nome}: folha do motor fora ({n} px); folha e arco do PDF, arco em cinza fino")
    return out


# Térreo, eletrodomésticos (pedido do usuário, 19/10/26: "eletrodomésticos em inox", na fileira de baixo da cozinha
# e do gourmet). O motor fez os volumes no lilás dos armários. No PDF (ARQ_LAYOUT HUMANIZAÇÃO), os quadrados sem
# diagonal são eletrodomésticos: dois no fim da bancada do gourmet, dois na cozinha e as duas máquinas da área de
# serviço. Cada um recebe o inox aprovado da Casa D, levado ao quadrado do PDF, com a sombra curta e o contorno fino,
# como na cozinha e nas máquinas da Casa E: na cozinha e no gourmet, as metades do par da cozinha da Casa D; na área
# de serviço, as máquinas de lá. O volume do motor passa até 2 px do quadrado do PDF (para fora): o inox cobre os
# dois, para não sobrar uma moldura lilás.
INOX = {"quadrados": [  # (onde, quadrado em pt, qual fonte)
    ("gourmet", (1559.67, 1548.4, 1605.02, 1593.76), 0), ("gourmet", (1607.37, 1548.4, 1652.72, 1593.76), 1),
    ("cozinha", (1672.56, 1548.4, 1717.92, 1593.76), 0), ("cozinha", (1717.92, 1548.4, 1763.27, 1593.76), 1),
    ("área de serviço", (1615.87, 1607.93, 1655.55, 1647.61), 2), ("área de serviço", (1661.22, 1607.93, 1700.91, 1647.61), 3)],
    "fonte": (CASA.parent / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png",
              [(972, 319, 996, 345), (998, 319, 1022, 345),        # o par da cozinha
               (1143, 191, 1166, 216), (1167, 191, 1190, 216)]),   # as máquinas da área de serviço
    "contorno": (70, 72, 74), "larg_contorno": 0.4,
    "sombra": {"desloc": (-1.5, 1.5), "sigma": 1.0, "forca": 0.3},
    "claro": 150.0, "alcance": 2.5}           # o volume do motor: px claros (lilás) junto ao quadrado, até 2,5 px


def bloco_render(Y, r, claro, alcance):
    """Bordas (subpixel) do volume claro do render em volta do retângulo r do PDF (px): em cada lado, da borda do
    PDF para fora, enquanto o px é claro (passando por cima de um px mais escuro entre dois claros: o brilho da quina
    do volume), até o alcance; o px de transição entra pela fração. Nunca menor que o PDF."""
    x0, y0, x1, y1 = r
    ph = Y[int(y0 + (y1 - y0) * 0.3):int(y1 - (y1 - y0) * 0.3), :].mean(axis=0)
    pv = Y[:, int(x0 + (x1 - x0) * 0.3):int(x1 - (x1 - x0) * 0.3)].mean(axis=1)

    def lado(p, borda, passo):
        i = int(np.floor(borda + 0.5)) - (1 if passo > 0 else 0)
        def cabe(k):
            return abs(i + k * passo + 0.5 - borda) <= alcance

        while cabe(1) and (p[i + passo] >= claro or (cabe(2) and p[i + 2 * passo] >= claro)):
            i += passo
        if not cabe(1):
            return borda
        v, fora, luz = p[i + passo], p[i + 2 * passo], p[i]
        c = float(np.clip((v - fora) / (luz - fora), 0, 1)) if luz > fora < v else 0.0
        return min(i - c, borda) if passo < 0 else max(i + 1 + c, borda)

    return lado(ph, x0, -1), lado(pv, y0, -1), lado(ph, x1, 1), lado(pv, y1, 1)


def inox(out):
    from retoque_terreo_casae import colar, sombra_curta, linha_aa
    q = INOX
    _, p2r = pdf_pavimento("Terreo")
    arq, fontes = q["fonte"]
    casad = cv2.imread(str(arq))
    forma = out.shape[:2]
    feitos = {}
    Y = out.astype(np.float32).mean(axis=2)
    for onde, quad, f in q["quadrados"]:
        (x0, y0), (x1, y1) = p2r(*quad[:2]), p2r(*quad[2:])
        x0, y0, x1, y1 = bloco_render(Y, (x0, y0, x1, y1), q["claro"], q["alcance"])
        out = sombra_curta(out, (x0, y0, x1, y1), q["sombra"])
        fx0, fy0, fx1, fy1 = fontes[f]
        out = colar(out, casad[fy0:fy1, fx0:fx1], (x0, y0, x1, y1))
        a = linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], q["larg_contorno"], fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(q["contorno"]) * a, 0, 255).astype(np.uint8)
        feitos[onde] = feitos.get(onde, 0) + 1
    print("    eletrodomésticos em inox: " + ", ".join(f"{n} no {k}" if k != "área de serviço" else f"{n} na {k}"
                                                     for k, n in feitos.items()))
    return out


# Térreo, bancada gourmet (pedido do usuário, 19/10/26: "melhore a representação da área molhada e divisoria da
# bancada"). O motor fez, no braço de baixo da bancada, duas caixas: uma com um "texto" ilegível e outra com a cuba.
# No PDF (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS): a área molhada é o retângulo em volta da cuba, a 2,3 pt da borda da
# bancada e da ponta, até a parede; a divisória é a linha que corta a área molhada de lado a lado, interrompida pela
# cuba; a cuba é retangular, de aba fina; a torneira gourmet tem a base e a alavanca junto à parede e a mola até a
# bica, sobre a cuba. As duas caixas saem (a bancada logo à esquerda, coluna a coluna, na mesma luz) e entram: a área
# molhada e a divisória em traço cinza fino (o da área molhada das Casas C e D), com a área 3% mais escura que a
# bancada para se ler como uma zona; a cuba em inox (aba, bacia da borda ao fundo, contorno) e a torneira cromada,
# com a sombra curta.
GOURMET = {
    "limpar": (866, 923, 729, 750), "desloc": 60, "esfumar": 3,   # px: x0, x1, y0, y1; de onde vem a bancada
    "area_molhada": (1443.52, 1559.17, 1554.07, 1596.59),         # pt; o lado de baixo é a parede
    "divisoria": 1576.75,
    "cuba": (1492.85, 1564.28, 1534.8, 1589.22), "bacia": (1493.98, 1565.41, 1533.66, 1588.09),
    "bica": ((1513.75, 1580.3), 3.1), "mola": (1514.52, 1579.35, 1516.23, 1591.69),
    "base": ((1515.35, 1591.9), 1.4), "alavanca": (1510.9, 1590.6, 1513.75, 1593.1),
    "traco": ((140, 142, 144), 0.4, 0.7),                         # cor, largura (px), força
    "tom_area": 0.97,                                              # a área molhada, um pouco mais escura que a bancada
    "aba": (222, 221, 218), "contorno": (120, 124, 128), "bacia_cor": ((166, 165, 162), (202, 201, 198))}


def gourmet(out):
    from retoque_subsolo_casae import Tela, SOMBRA, CROMO, CROMO_CLARO, CROMO_ESCURO, SS
    q = GOURMET
    x0, x1, y0, y1 = q["limpar"]
    d, e = q["desloc"], q["esfumar"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    fonte = out[y0:y1, x0 - d:x1 - d].astype(np.float32)
    w = x1 - x0
    a = np.clip(np.minimum(np.arange(w) + 1, w - np.arange(w)) / e, 0, 1)[None, :, None]
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + fonte * a, 0, 255).astype(np.uint8)

    _, p2r = pdf_pavimento("Terreo")
    ax0, ay0, ax1, ay1 = q["area_molhada"]
    tl = Tela(out, p2r, (ax0 - 3, ay0 - 3, ax1 + 3, ay1))
    cor, larg, forca = q["traco"]

    def linha(p0, p1):
        m = tl.vazia()
        a_, b_ = tl.pt(*p0), tl.pt(*p1)
        cv2.line(m, (int(round(a_[0])), int(round(a_[1]))), (int(round(b_[0])), int(round(b_[1]))), 255,
                 max(1, int(round(larg * SS))))
        return m

    area = tl.ret(q["area_molhada"])
    tl.reg *= (1 - (1 - q["tom_area"]) * tl.reduzir(area))[..., None]
    cx0, cy0, cx1, cy1 = q["cuba"]
    for p0, p1 in [((ax0, ay1), (ax0, ay0)), ((ax0, ay0), (ax1, ay0)), ((ax1, ay0), (ax1, ay1)),
                   ((ax0, q["divisoria"]), (cx0, q["divisoria"])), ((cx1, q["divisoria"]), (ax1, q["divisoria"]))]:
        tl.pintar(linha(p0, p1), cor, forca)

    c = tl.ret(q["cuba"], 1.0)
    tl.sombra(c, **SOMBRA)
    tl.pintar(c, q["aba"])
    bx0, by0, bx1, by1 = q["bacia"]
    borda, fundo = q["bacia_cor"]
    for i in range(6):                       # a bacia, da borda ao fundo
        k = i / 5
        tom = tuple(borda[j] * (1 - k) + fundo[j] * k for j in range(3))
        ins = k * 3.6
        tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.6, 1.4 - k)), tom)
    tl.contorno(c, 0.3, q["contorno"])

    mx0, my0, mx1, my1 = q["mola"]           # a mola, da base à bica
    m = tl.ret(q["mola"], 0.8)
    tl.sombra(m, **SOMBRA)
    tl.pintar(m, CROMO_ESCURO)
    tl.pintar(tl.ret((mx0 + 0.2, my0, (mx0 + mx1) / 2, my1), 0.3), CROMO_CLARO, 0.7)
    for (px_, py_), r, tom in [(q["base"][0], q["base"][1], CROMO), (q["bica"][0], q["bica"][1], CROMO)]:
        disco = tl.vazia()
        u, v = tl.pt(px_, py_)
        cv2.circle(disco, (int(round(u)), int(round(v))), int(round(r * 0.5483 * SS)), 255, -1)
        tl.sombra(disco, **SOMBRA)
        tl.pintar(disco, tom)
        tl.contorno(disco, 0.25, CROMO_ESCURO)
    (u, v), r = tl.pt(*q["bica"][0]), q["bica"][1]
    face = tl.vazia()                        # a face da bica, com o arejador
    cv2.circle(face, (int(round(u)), int(round(v))), int(round(r * 0.6 * 0.5483 * SS)), 255, -1)
    tl.pintar(face, CROMO_ESCURO)
    lv = tl.ret(q["alavanca"], 0.5)
    tl.sombra(lv, **SOMBRA)
    tl.pintar(lv, CROMO)
    tl.contorno(lv, 0.25, CROMO_ESCURO)
    out = tl.gravar()
    print("    bancada gourmet: caixas do motor fora; área molhada e divisória em traço fino, cuba em inox e torneira")
    return out


# Térreo, bancada da cozinha (pedido do usuário, 19/10/26: "melhore as representações das pias e bancada, com a área
# molhada bem representada. além disso, preciso de aspecto de bancada de pedra na cozinha"). O motor fez a bancada da
# parede da direita no lilás dos armários, chapada, com duas cubas borradas. No prompt, todas as bancadas são de
# quartzo claro, com pontilhado fino. No PDF (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS): a bancada vai da parede de cima à de
# baixo; a área molhada é o retângulo em volta das duas cubas, até a parede; as cubas são retangulares, de aba fina; em
# cada uma, a válvula e a torneira de bica reta, com a base e a alavanca junto à parede.
# Entram: a bancada em pedra, o quartzo do próprio render (o da ilha e da bancada gourmet) com o desenho do Bege Bahia
# aprovado (manchas em nuvem e pontinhos) só na luz, para se ler como pedra clara; a área molhada como na
# bancada gourmet (traço cinza fino e 3% mais escura); as cubas em inox e as torneiras cromadas, com a sombra curta.
COZINHA_PIAS = {
    "bancada": (1888.0, 1395.33, 1922.01, 1670.29),               # pt, da parede de cima à de baixo
    "quartzo": (216, 219, 233), "contraste": 1.8, "semente": 645,  # BGR do quartzo da ilha no render
    "area_molhada": (1890.26, 1477.54, 1922.01, 1615.3),           # o lado da direita é a parede
    "cubas": [((1891.96, 1484.91, 1916.91, 1521.19), (1893.1, 1486.04, 1915.78, 1520.06)),
              ((1891.96, 1530.26, 1916.91, 1566.54), (1893.1, 1531.39, 1915.78, 1565.41))],
    "valvula": 3.1, "valvulas": [(1908.0, 1502.9), (1908.0, 1548.26)],
    "bicas": [(1908.59, 1501.43, 1919.74, 1502.61), (1908.59, 1546.79, 1919.74, 1547.96)],
    "bases": [(1917.63, 1500.49, 1920.69, 1503.55), (1917.63, 1545.85, 1920.69, 1548.91)],
    "alavancas": [(1918.3, 1504.1, 1920.0, 1505.6), (1918.3, 1549.4, 1920.0, 1551.0)]}


def cozinha_pias(out):
    from retoque_subsolo_casae import Tela, SOMBRA, CROMO, CROMO_CLARO, CROMO_ESCURO, SS
    q, g = COZINHA_PIAS, GOURMET
    _, p2r = pdf_pavimento("Terreo")
    tl = Tela(out, p2r, q["bancada"])
    b = tl.ret(q["bancada"])
    tl.sombra(b, **SOMBRA)
    tex = textura_bege(tl.h, tl.w, q["semente"])
    lum = tex.mean(axis=2)
    rel = 1 + q["contraste"] * (lum / lum.mean() - 1)
    pedra = np.float32(q["quartzo"])[None, None] * rel[..., None]
    a = tl.reduzir(b)[..., None]
    tl.reg = tl.reg * (1 - a) + pedra * a
    tl.contorno(b, 0.35, (150, 153, 155))

    ax0, ay0, ax1, ay1 = q["area_molhada"]
    area = tl.ret(q["area_molhada"])
    tl.reg *= (1 - (1 - g["tom_area"]) * tl.reduzir(area))[..., None]
    cor, larg, forca = g["traco"]
    for p0, p1 in [((ax1, ay0), (ax0, ay0)), ((ax0, ay0), (ax0, ay1)), ((ax0, ay1), (ax1, ay1))]:
        m = tl.vazia()
        u0, u1 = tl.pt(*p0), tl.pt(*p1)
        cv2.line(m, (int(round(u0[0])), int(round(u0[1]))), (int(round(u1[0])), int(round(u1[1]))), 255,
                 max(1, int(round(larg * SS))))
        tl.pintar(m, cor, forca)

    borda, fundo = g["bacia_cor"]
    for aba, bacia in q["cubas"]:
        c = tl.ret(aba, 1.4)
        tl.sombra(c, **SOMBRA)
        tl.pintar(c, g["aba"])
        bx0, by0, bx1, by1 = bacia
        for i in range(6):                   # a bacia, da borda ao fundo
            k = i / 5
            tom = tuple(borda[j] * (1 - k) + fundo[j] * k for j in range(3))
            ins = k * 3.6
            tl.pintar(tl.ret((bx0 + ins, by0 + ins, bx1 - ins, by1 - ins), max(0.6, 1.2 - k)), tom)
        tl.contorno(c, 0.3, g["contorno"])
    for vx, vy in q["valvulas"]:
        u, v = tl.pt(vx, vy)
        for r, tom in [(q["valvula"], CROMO), (q["valvula"] * 0.65, CROMO_ESCURO)]:
            m = tl.vazia()
            cv2.circle(m, (int(round(u)), int(round(v))), int(round(r * 0.5483 * SS)), 255, -1)
            tl.pintar(m, tom)
    for bica, base, alav in zip(q["bicas"], q["bases"], q["alavancas"]):
        m = tl.ret(bica, 0.6)
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, CROMO_ESCURO)
        tx0, ty0, tx1, ty1 = bica
        tl.pintar(tl.ret((tx0 + 0.3, ty0 + 0.2, tx1 - 0.3, (ty0 + ty1) / 2), 0.3), CROMO_CLARO)
        for peca, tom in [(base, CROMO), (alav, CROMO_ESCURO)]:
            m = tl.ret(peca, 0.4)
            tl.sombra(m, **SOMBRA)
            tl.pintar(m, tom)
            tl.contorno(m, 0.25, CROMO_ESCURO)
    out = tl.gravar()
    print("    bancada da cozinha: quartzo com o desenho de pedra, área molhada, duas cubas em inox e torneiras")
    return out


# Térreo 3. Estar sob a projeção do pavimento superior (pedido do usuário, 19/10/26: "melhorar a representação dessa
# área. não é mesa de jantar. área de estar."). O motor pôs uma mesa retangular com 6 cadeiras. No PDF (ARQ_LAYOUT
# HUMANIZAÇÃO e ARQ_MOBILIÁRIO) são 4 poltronas em X, voltadas para uma mesa triangular de cantos arredondados no
# centro, sob o X tracejado da projeção (DOC_LINHAS E PROJEÇÕES). Sem IA:
# 1. a mesa e as cadeiras do motor saem, com as sombras: o travertino volta, tecido (image quilting) de um trecho
#    limpo dele ao lado, na luz do lugar (a do piso em volta);
# 2. as poltronas são as do PDF (poltronas de encosto curvo, que abraça o assento até os braços), no estilo do sofá
#    aprovado da sala: o contorno do PDF cheio, dividido pelas linhas dele em assento e encosto com os braços (cada
#    parte com o volume arredondado e o vinco nas linhas), nas cores do sofá, com a sombra na mesma luz (as poltronas
#    do render têm outro desenho);
# 3. a mesa triangular, no contorno do PDF, no carvalho da mesa do motor (o veio no comprido), com o contorno fino e
#    a sombra curta;
# 4. o X tracejado volta por cima, como o render o desenha: os traços do PDF, no passo e na fase dos traços do render
#    em volta, na cor e na largura deles.
ESTAR_PROJ = {
    "apagar": (1026, 332, 1107, 443),                         # px: a mesa e as cadeiras do motor, com as sombras
    "janela": (996, 312, 1132, 458),                          # px: o quadrado da projeção
    "fonte_piso": (1137, 330, 1177, 450),                     # px: travertino limpo, à direita do quadrado
    "poltronas": [(1703.75, 859.16, 1773.19, 928.52), (1816.11, 858.86, 1885.46, 928.31),
                  (1814.96, 947.8, 1884.4, 1017.15), (1704.62, 947.57, 1773.97, 1017.02)],   # pt (contornos do PDF)
    "mesa": (1777.07, 914.87, 1819.33, 955.39),               # pt
    "fonte_madeira": (1053, 338, 1083, 361),                  # px da imagem aprovada: o tampo da mesa do motor
    "sombra_poltrona": [(-1.4, 1.4, 2.0, 0.30), (0, 0, 0.9, 0.14)], "sombra_mesa": (-1.0, 1.0, 1.2, 0.28),
    "vinco": 0.18,                                            # as linhas do PDF, no tecido
    "contorno_mesa": ((70, 96, 128), 0.35),
    "traco": {"cor": (112, 116, 120), "larg": 1.25, "forca": 0.62}}


def estar_projecao(out):
    from retoque_bege_bahia_terreo import quilting
    q = ESTAR_PROJ
    pg, p2r = pdf_pavimento("Terreo")
    orig = cv2.imread(str(APROVADAS["Terreo"]))
    X0, Y0, X1, Y1 = q["janela"]
    H, W = (Y1 - Y0) * SS_E, (X1 - X0) * SS_E
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    h, w = reg.shape[:2]

    def ss(pts):
        return np.int32(np.round((np.asarray(pts) - (X0, Y0)) * SS_E))

    def red(m):
        return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)

    def poli(caixa, camada):
        d = next(d for d in pg.get_drawings() if d.get("layer") == camada and d["type"] == "f"
                 and d["rect"].x0 >= caixa[0] - 0.5 and d["rect"].x1 <= caixa[2] + 0.5
                 and d["rect"].y0 >= caixa[1] - 0.5 and d["rect"].y1 <= caixa[3] + 0.5)
        return np.vstack(caminhos_pdf(d, p2r, 16))

    # os traços do X, do PDF (cada traço é uma linha da DOC_LINHAS E PROJEÇÕES)
    tracos = []
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") == "DOC_LINHAS E PROJEÇÕES" and r.width > 5 and r.height > 5 and \
                abs(r.width - r.height) < 0.2 and r.width < 11:
            (a, b), (c, e) = p2r(r.x0, r.y0), p2r(r.x1, r.y1)
            if X0 <= a and c <= X1 and Y0 <= b and e <= Y1:
                it = d["items"][0]
                tracos.append((np.float64(p2r(it[1].x, it[1].y)), np.float64(p2r(it[2].x, it[2].y))))
    Yo = out.astype(np.float32).mean(axis=2)
    ax0, ay0, ax1, ay1 = q["apagar"]

    # 4 (medida antes de apagar): a fase dos traços do render em cada diagonal, fora da área apagada
    def perfil_escuro(pts):
        return np.float32([float(cv2.getRectSubPix(Yo, (1, 1), (float(x), float(y)))[0, 0]) for x, y in pts])

    fases = {}
    for sentido in (1, -1):
        seg = [t for t in tracos if np.sign((t[1][0] - t[0][0]) * (t[1][1] - t[0][1])) == sentido]
        u = seg[0][1] - seg[0][0]
        u = u / np.hypot(*u)
        if u[1] < 0:
            u = -u
        melhor = (-1e9, 0.0)
        for desl in np.arange(-5.5, 5.51, 0.25):
            sc = 0.0
            for a, b in seg:
                a2, b2 = a + desl * u, b + desl * u
                fora = lambda p: not (ax0 - 2 <= p[0] <= ax1 + 2 and ay0 - 2 <= p[1] <= ay1 + 2)
                if not (fora(a2) and fora(b2)):
                    continue
                dentro = [a2 + (b2 - a2) * k for k in np.linspace(0.15, 0.85, 7)]
                vao = [b2 + u * k for k in (0.9, 1.5, 2.1)]
                sc += perfil_escuro(vao).mean() - perfil_escuro(dentro).mean()
            melhor = max(melhor, (sc, desl))
        fases[sentido] = (melhor[1], u)
        print(f"    traços da diagonal {'\\' if sentido > 0 else '/'}: fase do render {melhor[1]:+.2f} px ao longo dela")

    # 1. a mesa e as cadeiras do motor saem: o travertino tecido, na luz do lugar
    med = cv2.medianBlur(out, 7).astype(np.float32)
    apaga = np.zeros(out.shape[:2], bool)
    apaga[ay0:ay1, ax0:ax1] = True
    riscos = np.zeros(out.shape[:2], np.uint8)
    for a, b in tracos:
        cv2.line(riscos, tuple(np.int32(np.round(a))), tuple(np.int32(np.round(b))), 255, 3)
    riscos = cv2.dilate(riscos, np.ones((7, 7), np.uint8)) > 0
    piso = np.zeros_like(apaga)
    piso[Y0:Y1, X0:X1] = True
    piso &= ~cv2.dilate(apaga.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~riscos & (Yo > 185)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    peso = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 10)
    campo = np.where((peso > 0.05)[..., None], nconv(med, piso.astype(np.float32), 10),
                     nconv(med, piso.astype(np.float32), 30))   # no meio da área apagada, a luz de mais longe
    fx0, fy0, fx1, fy1 = q["fonte_piso"]
    campo_f = nconv(med, np.ones(out.shape[:2], np.float32), 10)[fy0:fy1, fx0:fx1]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32) / campo_f
    f = f / f.reshape(-1, 3).mean(axis=0)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    tex = quilting(fontes, ay1 - ay0, ax1 - ax0, p=24, sobra=8, candidatos=400, rng=np.random.default_rng(646))
    novo = out.astype(np.float32)
    novo[ay0:ay1, ax0:ax1] = tex[:ay1 - ay0, :ax1 - ax0] * campo[ay0:ay1, ax0:ax1]
    a = np.zeros(out.shape[:2], np.float32)
    a[ay0:ay1, ax0:ax1] = 1
    a = cv2.GaussianBlur(a, (0, 0), 1.2) * apaga + apaga * 0
    a = np.maximum(a, cv2.erode(apaga.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32))
    novo = out.astype(np.float32) * (1 - a[..., None]) + novo * a[..., None]
    reg = novo[Y0:Y1, X0:X1].copy()

    gx, gy = np.meshgrid(np.arange(W) / SS_E + X0 + 0.5 / SS_E, np.arange(H) / SS_E + Y0 + 0.5 / SS_E)
    gx1, gy1 = np.meshgrid(np.arange(w) + X0 + 0.5, np.arange(h) + Y0 + 0.5)

    def sombra(m, dx, dy, sig, forca):
        nonlocal reg
        sm = cv2.warpAffine(m.astype(np.float32) / 255, np.float32([[1, 0, dx * SS_E], [0, 1, dy * SS_E]]), (W, H))
        sm = cv2.resize(cv2.GaussianBlur(sm, (0, 0), sig * SS_E), (w, h), interpolation=cv2.INTER_AREA)
        reg *= (1 - forca * sm * (1 - red(m)))[..., None]

    # 2. as poltronas do PDF, no estilo do sofá aprovado
    cores = SALA["cores"]

    def lisa(t):
        return t * t * (3 - 2 * t)

    def pintar(cor, tom, m):
        nonlocal reg
        c = cv2.resize(np.float32(cor)[None, None] * tom[..., None] * (m[..., None] / 255.0), (w, h),
                       interpolation=cv2.INTER_AREA)
        a = red(m)
        reg = reg * (1 - a[..., None]) + c

    for k, caixa in enumerate(q["poltronas"]):
        ds = [d for d in pg.get_drawings() if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO"
              and d["rect"].x0 >= caixa[0] - 0.5 and d["rect"].x1 <= caixa[2] + 0.5
              and d["rect"].y0 >= caixa[1] - 0.5 and d["rect"].y1 <= caixa[3] + 0.5]
        corpo = np.zeros((H, W), np.uint8)
        for d in ds:
            if d["type"] == "f":
                for c in caminhos_pdf(d, p2r, 16):
                    cv2.fillPoly(corpo, [ss(c)], 255)
        linhas = np.zeros((H, W), np.uint8)
        for d in ds:
            if d["type"] == "s":
                for c in caminhos_pdf(d, p2r, 16):
                    cv2.polylines(linhas, [ss(c)], False, 255, 2)
        linhas &= corpo
        for par in q["sombra_poltrona"]:
            sombra(corpo, *par)
        n, lab, st, _ = cv2.connectedComponentsWithStats(((corpo > 0) & (linhas == 0)).astype(np.uint8), connectivity=4)
        assento = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        partes = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 4 * SS_E * SS_E]
        perto = cv2.dilate(np.isin(lab, partes).astype(np.uint8), np.ones((5, 5), np.uint8))
        resto = (corpo > 0) & ~np.isin(lab, partes) & (perto == 0)     # sobras finas: vão com o encosto
        for i in partes:
            m = ((lab == i) | (cv2.dilate((lab == i).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & (linhas > 0))
            m = (m & (corpo > 0)).astype(np.uint8) * 255
            dist = cv2.distanceTransform(m, cv2.DIST_L2, 5) / SS_E
            if i == assento:
                pintar(cores["assento"], 0.80 + 0.20 * lisa(np.clip(dist / 3.0, 0, 1)), m)
            else:
                pintar(cores["encosto"], 0.80 + 0.20 * lisa(np.clip(dist / 1.8, 0, 1)), m)
        if resto.any():
            m = resto.astype(np.uint8) * 255
            pintar(cores["encosto"], np.full((H, W), 0.85, np.float32), m)
        reg *= (1 - q["vinco"] * red(linhas))[..., None]
        print(f"    poltrona {k + 1}: contorno do PDF, {len(partes)} partes (assento {st[assento, cv2.CC_STAT_AREA] / SS_E ** 2:.0f} px)")

    # 3. a mesa triangular em carvalho
    pm = poli(q["mesa"], "ARQ_MOBILIÁRIO")
    mm = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mm, [ss(pm)], 255)
    sombra(mm, *q["sombra_mesa"])
    a0, b0, a1, b1 = q["fonte_madeira"]
    mx0, my0 = pm.min(axis=0)
    mx1, my1 = pm.max(axis=0)
    M = cv2.getAffineTransform(np.float32([(0, 0), (a1 - a0, 0), (0, b1 - b0)]),
                               np.float32([(mx0 - X0 - 1, my0 - Y0 - 1), (mx1 - X0 + 1, my0 - Y0 - 1), (mx0 - X0 - 1, my1 - Y0 + 1)]))
    madeira = cv2.warpAffine(orig[b0:b1, a0:a1].astype(np.float32), M, (w, h), flags=cv2.INTER_AREA,
                             borderMode=cv2.BORDER_REFLECT)
    al = red(mm)[..., None]
    reg = reg * (1 - al) + madeira * al
    cor, larg = q["contorno_mesa"]
    borda = mm & ~cv2.erode(mm, np.ones((max(1, int(round(larg * SS_E))),) * 2, np.uint8))
    al = red(borda)[..., None]
    reg = reg * (1 - al) + np.float32(cor) * al

    # 4. o X tracejado por cima, na fase do render
    t = q["traco"]
    risco = np.zeros((H, W), np.uint8)
    for a, b in tracos:
        sentido = np.sign((b[0] - a[0]) * (b[1] - a[1]))
        desl, u = fases[sentido]
        a2, b2 = a + desl * u, b + desl * u
        meio = (a2 + b2) / 2
        if not (ax0 - 6 <= meio[0] <= ax1 + 6 and ay0 - 6 <= meio[1] <= ay1 + 6):
            continue
        cv2.line(risco, tuple(ss(a2)), tuple(ss(b2)), 255, max(1, int(round(t["larg"] * SS_E))))
    al = red(risco)[..., None] * t["forca"]
    # só dentro da área refeita (fora dela, os traços do render ficam)
    dentro = cv2.GaussianBlur(apaga[Y0:Y1, X0:X1].astype(np.float32), (0, 0), 0.8)[..., None]
    reg = reg * (1 - al * dentro) + np.float32(t["cor"]) * al * dentro
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    estar sob a projeção: mesa e 6 cadeiras do motor fora; 4 poltronas em X e a mesa triangular do PDF")
    return out


# Térreo 5. Lavabo (pedido do usuário, 19/10/26: "melhorar cuba e sua posição e tamanho. representar a bancada da
# cuba. representar o sanitário. representar e gerar o rótulo da claraboia"). O motor pôs no alto uma peça estranha
# com um arco e um bloco claro (onde ficam a projeção da claraboia e o vaso) e, à direita, uma cuba branca solta,
# menor que a bancada e longe da parede. No PDF (ARQ_BANCADAS, ARQ_LOUÇAS E METAIS e DOC_LINHAS E PROJEÇÕES): a
# bancada vai da parede da direita até 1,6 m de fundo, com a cuba esculpida (a bacia, com a fenda do ralo junto à
# parede, e um friso atrás) e a torneira saindo da parede; o vaso suspenso na parede da direita, no alto; a projeção
# da claraboia é o retângulo tracejado com o X, no alto do lavabo, com a nota "PROJ. CLARABOIA" logo abaixo. Entram:
# 1. o piso do lavabo de volta onde estavam as peças do motor (travertino tecido do próprio lavabo, na luz dele);
# 2. a bancada em quartzo (como a da cozinha), com a cuba esculpida no próprio quartzo, como a do lavabo aprovado da
#    Casa E: o fundo escurece para a fenda, junto à parede; as bordas de cima e da direita fazem sombra curta para
#    dentro; traço fino na borda; e a torneira cromada saindo da parede;
# 3. o vaso suspenso no contorno do PDF, como os aprovados (louça com volume e o tampo fechado);
# 4. o tracejado da claraboia, como o do estar sob a projeção; o rótulo vem em `rotulos_casaa.py`.
LAVABO_A = {
    "limpar": [(1189, 179, 1236, 198), (1210, 201, 1236, 240)],     # px: as peças do motor, com as sombras
    "fonte_piso": (1191, 199, 1209, 236),                           # px: piso limpo do lavabo, à esquerda
    "sala": (2021.22, 561.94, 2106.26, 715.01),                     # pt: o lavabo, por dentro das paredes
    "bancada": (2077.92, 615.8, 2106.26, 670.23), "cuba": (2079.05, 616.94, 2099.46, 669.09),
    "fenda": 2100.03,                                               # pt: x da fenda do ralo (o friso do PDF)
    "torneira": (2096.65, 644.89, 2104.59, 646.81), "canopla": (2104.59, 643.9, 2106.26, 647.8),
    "vaso": (2077.15, 577.45, 2106.26, 597.46),
    "inclinacao": 0.12, "sombra_borda": (0.16, 1.4), "luz_borda": 0.04,
    "cor_fenda": (92, 94, 98), "contorno_cuba": ((150, 150, 150), 0.4, 0.6)}


def lavabo_a(out):
    from retoque_bege_bahia_terreo import quilting
    from retoque_subsolo_casae import Tela, SOMBRA, CROMO, CROMO_CLARO, CROMO_ESCURO, vaso, SS
    from retoque_terreo_casae import poligono_aa, linha_aa
    q, qc = LAVABO_A, COZINHA_PIAS
    pg, p2r = pdf_pavimento("Terreo")
    (sx0, sy0), (sx1, sy1) = p2r(*q["sala"][:2]), p2r(*q["sala"][2:])

    # 1. o piso de volta
    apaga = np.zeros(out.shape[:2], bool)
    for x0, y0, x1, y1 in q["limpar"]:
        apaga[y0:y1, x0:x1] = True
    sala = np.zeros_like(apaga)
    sala[int(np.ceil(sy0)) + 1:int(sy1) - 1, int(np.ceil(sx0)) + 1:int(sx1) - 1] = True
    Yo = out.astype(np.float32).mean(axis=2)
    piso = sala & ~cv2.dilate(apaga.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & \
        (Yo > cv2.medianBlur(out, 9).astype(np.float32).mean(axis=2) - 12)
    med = cv2.medianBlur(out, 5).astype(np.float32)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    peso = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 6)
    campo = np.where((peso > 0.05)[..., None], nconv(med, piso.astype(np.float32), 6),
                     nconv(med, piso.astype(np.float32), 15))
    fx0, fy0, fx1, fy1 = q["fonte_piso"]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32) / nconv(med, piso.astype(np.float32), 6)[fy0:fy1, fx0:fx1]
    f = f / f.reshape(-1, 3).mean(axis=0)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    ys, xs = np.nonzero(apaga)
    by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    tex = quilting(fontes, by1 - by0, bx1 - bx0, p=14, sobra=5, candidatos=300, rng=np.random.default_rng(647))
    novo = out.astype(np.float32)
    novo[by0:by1, bx0:bx1] = tex[:by1 - by0, :bx1 - bx0] * campo[by0:by1, bx0:bx1]
    a = (cv2.GaussianBlur(apaga.astype(np.float32), (0, 0), 0.8) * apaga)[..., None]
    out[:] = np.clip(out * (1 - a) + novo * a, 0, 255).astype(np.uint8)

    # 2. a bancada em quartzo, a cuba esculpida e a torneira
    tl = Tela(out, p2r, q["bancada"])
    b = tl.ret(q["bancada"])
    tl.sombra(b, **SOMBRA)
    tex = textura_bege(tl.h, tl.w, 648)
    lum = tex.mean(axis=2)
    pedra = np.float32(qc["quartzo"])[None, None] * (1 + qc["contraste"] * (lum / lum.mean() - 1))[..., None]
    a = tl.reduzir(b)[..., None]
    tl.reg = tl.reg * (1 - a) + pedra * a
    tl.contorno(b, 0.35, (150, 153, 155))
    out = tl.gravar()
    forma = out.shape[:2]
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]].astype(np.float32) + 0.5
    (x0, y0), (x1, y1) = p2r(*q["cuba"][:2]), p2r(*q["cuba"][2:])
    al = poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    fa = 1 - q["inclinacao"] * np.clip((xx - x0) / (x1 - x0), 0, 1)       # o fundo desce para a parede
    s_, w_ = q["sombra_borda"]
    fa *= 1 - s_ * np.exp(-np.clip(yy - y0, 0, None) / w_) - s_ * np.exp(-np.clip(x1 - xx, 0, None) / w_)
    fa *= 1 + q["luz_borda"] * (np.exp(-np.clip(xx - x0, 0, None) / w_) + np.exp(-np.clip(y1 - yy, 0, None) / w_))
    fa = 1 + (fa - 1) * al
    out[:] = np.clip(out * fa[..., None], 0, 255).astype(np.uint8)
    xf = p2r(q["fenda"], q["cuba"][1])[0]
    a = linha_aa(forma, [(xf, y0 + 1.5), (xf, y1 - 1.5)], 0.8)[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(q["cor_fenda"]) * a, 0, 255).astype(np.uint8)
    cor, larg, forca = q["contorno_cuba"]
    a = linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], larg, fechada=True)[..., None] * forca
    out[:] = np.clip(out * (1 - a) + np.float32(cor) * a, 0, 255).astype(np.uint8)
    (tx0, ty0), (tx1, ty1) = p2r(*q["torneira"][:2]), p2r(*q["torneira"][2:])
    yc, lt = (ty0 + ty1) / 2, ty1 - ty0
    bica = [(tx1, yc), (tx0, yc)]
    sb = cv2.GaussianBlur(linha_aa(forma, [(u - 1.0, v + 1.0) for u, v in bica], lt), (0, 0), 0.8)
    out[:] = np.clip(out * (1 - 0.3 * sb)[..., None], 0, 255).astype(np.uint8)
    for pts, lg, c in ((bica, lt, CROMO_ESCURO), ([(tx1 - 0.3, yc - 0.15), (tx0, yc - 0.15)], 0.35, CROMO_CLARO)):
        a = linha_aa(forma, pts, lg)[..., None]
        out[:] = np.clip(out * (1 - a) + np.float32(c) * a, 0, 255).astype(np.uint8)
    (cx0, cy0), (cx1, cy1) = p2r(*q["canopla"][:2]), p2r(*q["canopla"][2:])
    a = poligono_aa(forma, [(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)])[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(CROMO) * a, 0, 255).astype(np.uint8)

    # 3. o vaso suspenso
    out = vaso(out, pg, p2r, q["vaso"], "direita")

    # 4. o tracejado da claraboia (por cima do vaso, como no PDF)
    t = ESTAR_PROJ["traco"]
    ax0, ay0, ax1, ay1 = q["sala"]
    risco = np.zeros(forma, np.float32)
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") == "DOC_LINHAS E PROJEÇÕES" and r.x0 >= ax0 - 0.1 and r.x1 <= ax1 + 0.1 and \
                r.y0 >= ay0 - 0.1 and r.y1 <= ay1 + 0.1 and max(r.width, r.height) > 3:
            it = d["items"][0]
            risco = np.maximum(risco, linha_aa(forma, [p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)], t["larg"]))
    risco *= sala
    a = (risco * t["forca"])[..., None]
    out[:] = np.clip(out * (1 - a) + np.float32(t["cor"]) * a, 0, 255).astype(np.uint8)
    print("    lavabo: peças do motor fora; bancada de quartzo com cuba esculpida e torneira; vaso suspenso; "
          "tracejado da claraboia")
    return out


# Térreo, porta pivotante (pedido do usuário, 19/10/26: "melhorar a representação da porta pivotante, mostrando-a até
# o hall externo com seus respectivos arcos"). O motor parou a folha no batente entre os dois halls e só fez o arco
# grande, no hall interno. No PDF (ARQ_PAREDE) a folha passa do pivô e entra 0,65 m no hall externo, e esse trecho
# tem o arco pequeno, do lado de lá. A folha e o arco grande do render ficam (estão no lugar do PDF); entram, no
# mesmo desenho deles: o resto da folha até a ponta do PDF (as três linhas da folha do render: contorno, miolo claro,
# contorno, com o contorno na ponta) e o arco pequeno, do fim da folha ao batente de cima, centrado no pivô, no
# cinza e na largura do arco grande.
PIVOTANTE = {"pivo": (2201.22, 877.44), "ponta": (2238.08, 877.44), "topo": (2201.22, 840.59),   # pt
             "folha_render": (1240, 1280, 351, 354),     # px: x0, x1, linhas da folha do render (contorno, miolo, contorno)
             "inicio": 1288.5,                            # px: onde a folha do render para (no batente)
             "arco": ((118, 121, 124), 1.0, 0.75)}        # cor, largura (px) e força: o arco grande do render


def pivotante(out):
    from retoque_terreo_casae import linha_aa
    q = PIVOTANTE
    _, p2r = pdf_pavimento("Terreo")
    (px, py), (ex, _), (_, ty) = p2r(*q["pivo"]), p2r(*q["ponta"]), p2r(*q["topo"])
    x0, x1, y0, y1 = q["folha_render"]
    linhas = np.median(out[y0:y1, x0:x1].astype(np.float32), axis=1)        # BGR de cada linha da folha
    forma = out.shape[:2]
    # o resto da folha: as três linhas, com a cobertura de subpixel na ponta, e o contorno da ponta
    xi = q["inicio"]
    for k, y in enumerate(range(y0, y1)):
        a = linha_aa(forma, [(xi, y + 0.5), (ex, y + 0.5)], 1.0)
        a[y, :] = np.clip(a[y, :], 0, 1)
        a[:y, :] = 0
        a[y + 1:, :] = 0
        out[:] = np.clip(out * (1 - a[..., None]) + linhas[k] * a[..., None], 0, 255).astype(np.uint8)
    a = linha_aa(forma, [(ex - 0.5, y0), (ex - 0.5, y1)], 1.0)[..., None]
    out[:] = np.clip(out * (1 - a) + linhas[0] * a, 0, 255).astype(np.uint8)
    # o arco pequeno, do fim da folha ao batente de cima
    r = ex - px
    cor, larg, forca = q["arco"]
    pts = [(px + r * np.cos(t), py - r * np.sin(t)) for t in np.linspace(0, np.pi / 2 * (py - ty) / r, 60)]
    a = linha_aa(forma, pts, larg)[..., None] * forca
    out[:] = np.clip(out * (1 - a) + np.float32(cor) * a, 0, 255).astype(np.uint8)
    print(f"    porta pivotante: folha até a ponta do PDF (x {xi:.1f} a {ex:.1f} px) e o arco pequeno no hall externo "
          f"(raio {r:.1f} px)")
    return out


# Térreo, escada interna e o jardim em volta (pedido do usuário, 19/10/26: "vamos melhorar a representação da escada.
# não há uma barreira de subida. precisamos representar a parte colorida até o 7 degrau, onde tem a linha em diagonal.
# sendo esmaecida a partir desse degrau, pois já está na região do 1º pavimento. e a área verde ao redor precisa ter
# um aspecto melhor"). O motor fez a escada em U inteira cheia, com as linhas dos degraus e um retângulo de traço
# por cima (a "barreira"), e o jardim num verde chapado. No PDF (ARQ_ESCADAS E RAMPAS) a escada sobe do degrau 1, à
# esquerda do lanço de cima, para a direita; a linha de corte (o traço em diagonal com o X) passa no 7º degrau; do 8º
# em diante (o resto do lanço de cima, o patamar e o lanço de baixo) é tracejado, acima do corte. O jardim (17,46 m²)
# inclui a área da escada: ela sobe de dentro dele. Sem IA, como a escada caracol:
# 1. o jardim inteiro (com a área da escada) vira o gramado aprovado (o da grama ao lado do jardim de 4,79 m², tecido
#    por image quilting, no tom dele), com a sombra curta das paredes;
# 2. os degraus 1 a 7, até a linha de corte, cheios: o travertino do piso interno (tecido de um trecho limpo), com o
#    sombreamento de subida das escadas aprovadas, sem linhas: cada degrau um pouco mais claro que o de baixo (de 0,86
#    a 1) e a sombra curta de cada espelho no degrau de baixo; e a sombra curta da escada no gramado;
# 3. do 8º degrau em diante, os mesmos pisos esmaecidos sobre o gramado (30%), com os espelhos e o contorno em traço
#    claro;
# 4. a linha de corte do PDF (o traço com o X), fina.
ESCADA_INT = {
    "caixa": (1180, 455, 1335, 575),                          # px: o jardim com a escada (até o vidro da direita)
    "lanco1": (2021.22, 1094.86, 2174.3, 1162.89), "lanco2": (2021.22, 1185.57, 2174.3, 1253.6),
    "patamar": (2174.3, 1094.86, 2242.33, 1253.6),            # pt
    "espelhos": [2038.23, 2055.24, 2072.25, 2089.26, 2106.26, 2123.27, 2140.28, 2157.29],   # pt: entre os degraus
    "cheios": 7,                                              # degraus cheios: até o corte, no 7º
    "corte_caixa": (2118, 1090, 2162, 1166),                  # pt: onde ficam os traços da linha de corte
    "fonte_grama": (600, 885, 720, 935),                      # px da imagem aprovada: o gramado limpo
    "fonte_piso": (1137, 330, 1177, 450),                     # px: travertino limpo
    "piso": (186, 198, 217),                                  # BGR: o travertino dos degraus do render
    "tom": (0.86, 1.0), "espelho": (0.35, 2.2), "esmaecer": 0.30, "espelho_esm": ((170, 170, 170), 0.35),
    "parede": (0.22, 2.5), "sombra": (-1.0, 1.0, 1.2, 0.35), "corte": ((90, 92, 94), 0.5),
    # R14 (21/10/26): a linha suave em cada bocel dos degraus cheios, os bocéis esmaecidos tracejados, sem a linha de
    # corte (seção 5: "a linha de corte não é desenhada") e o triângulo no degrau 1 (o "S" do PDF), apontando para a
    # direita, a subida
    "r14": True}


def escada_interna(out):
    from retoque_bege_bahia_terreo import quilting
    from retoque_terreo_casae import poligono_aa, linha_aa
    q = ESCADA_INT
    pg, p2r = pdf_pavimento("Terreo")
    X0, Y0, X1, Y1 = q["caixa"]
    forma = out.shape[:2]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    h, w = reg.shape[:2]

    def ret_px(r):
        (a, b), (c, d) = p2r(*r[:2]), p2r(*r[2:])
        return a - X0, b - Y0, c - X0, d - Y0

    def poli(pts):
        return poligono_aa(forma, [(x, y) for x, y in pts])[Y0:Y1, X0:X1]

    def ret_aa(r):
        a, b, c, d = ret_px(r)
        return poli([(a + X0, b + Y0), (c + X0, b + Y0), (c + X0, d + Y0), (a + X0, d + Y0)])

    escada = np.maximum.reduce([ret_aa(q[k]) for k in ("lanco1", "lanco2", "patamar")])
    verde = (reg[..., 1] - reg[..., 2] > 6) & (reg[..., 1] - reg[..., 0] > 6)
    jardim = cv2.morphologyEx((verde | (escada > 0.01)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    jardim = jardim.astype(bool) & (reg.mean(axis=2) > 25)     # as paredes ficam

    # 1. o gramado aprovado
    ap = cv2.imread(str(APROVADAS["Terreo"])).astype(np.float32)
    fx0, fy0, fx1, fy1 = q["fonte_grama"]
    g = ap[fy0:fy1, fx0:fx1]
    cor_grama = np.median(g.reshape(-1, 3), axis=0)
    g = g / g.reshape(-1, 3).mean(axis=0)
    fontes = [np.ascontiguousarray(v) for v in (g, g[:, ::-1], g[::-1, :], g[::-1, ::-1])]
    tex = quilting(fontes, h, w, p=30, sobra=10, candidatos=400, rng=np.random.default_rng(649))[:h, :w]
    grama = tex * cor_grama
    parede = (~jardim) & (reg.mean(axis=2) < 70)
    dist = cv2.distanceTransform((~parede).astype(np.uint8), cv2.DIST_L2, 5)
    forca, alc = q["parede"]
    grama *= (1 - forca * np.clip(1 - dist / alc, 0, 1))[..., None]
    aj = cv2.GaussianBlur(jardim.astype(np.float32), (0, 0), 0.6) * jardim
    reg = reg * (1 - aj[..., None]) + grama * aj[..., None]

    # o travertino dos degraus
    fx0, fy0, fx1, fy1 = q["fonte_piso"]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32)
    f = f / cv2.GaussianBlur(f, (0, 0), 8)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    piso = quilting(fontes, h, w, p=24, sobra=8, candidatos=300, rng=np.random.default_rng(650))[:h, :w] * np.float32(q["piso"])

    # a parte cheia: do degrau 1 até a linha de corte
    corte = []
    for d in pg.get_drawings():
        r = d["rect"]
        cx0, cy0, cx1, cy1 = q["corte_caixa"]
        if d.get("layer") == "ARQ_ESCADAS E RAMPAS" and d["type"] == "s" and r.x0 >= cx0 and r.x1 <= cx1 and \
                r.y0 >= cy0 and r.y1 <= cy1 and r.width > 1 and r.height > 1:
            it = d["items"][0]
            corte.append([p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)])
    longos = sorted([c for c in corte if np.hypot(c[1][0] - c[0][0], c[1][1] - c[0][1]) > 8],
                    key=lambda c: min(c[0][1], c[1][1]))
    a1, c1 = longos[0], longos[-1]                            # o primeiro e o último trecho da diagonal
    a1 = sorted(a1, key=lambda p: p[1])
    c1 = sorted(c1, key=lambda p: p[1])
    l0, t0, _, b0 = ret_px(q["lanco1"])
    cheio = poli([(l0 + X0, t0 + Y0), (a1[0][0], t0 + Y0), a1[1], c1[0], (c1[1][0], b0 + Y0), (l0 + X0, b0 + Y0)])
    cheio = np.minimum(cheio, escada)
    esm = np.clip(escada - cheio, 0, 1)

    # 2. os degraus cheios, com o sombreamento de subida e a sombra curta no gramado
    xs = np.arange(w)[None, :] + 0.5
    bordas = [p2r(x, q["lanco1"][1])[0] - X0 for x in [q["lanco1"][0]] + q["espelhos"][:q["cheios"]]]
    tom0, tom1 = q["tom"]
    fator = np.ones((h, w), np.float32)
    n = q["cheios"]
    for k in range(n):
        xa = bordas[k]
        xb = bordas[k + 1] if k + 1 < len(bordas) else w
        dentro = (xs >= xa) & (xs < xb)
        fator = np.where(dentro, tom0 + (tom1 - tom0) * k / (n - 1), fator)
        if k + 1 < len(bordas):                               # a sombra do espelho de cima neste degrau
            sf, sl = q["espelho"]
            fator = np.where(dentro, fator * (1 - sf * np.exp(-np.clip(xb - xs, 0, None) / sl)), fator)
    dx, dy, sig, frc = q["sombra"]
    som = cv2.GaussianBlur(cv2.warpAffine(cheio, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h)), (0, 0), sig)
    reg *= (1 - frc * som * (1 - cheio))[..., None]
    reg = reg * (1 - cheio[..., None]) + piso * fator[..., None] * cheio[..., None]
    if q.get("r14"):
        kpt = p2r(q["lanco1"][0] + 100, q["lanco1"][1])[0] - p2r(*q["lanco1"][:2])[0]
        kpt /= 100                                            # px por pt
        _, ly0, _, ly1 = q["lanco1"]
        lb = np.zeros((h, w), np.float32)
        for x in [q["lanco1"][0]] + q["espelhos"][:n - 1]:
            (ax, ay), (bx, by) = p2r(x, ly0), p2r(x, ly1)
            lb = np.maximum(lb, r14_linha((h, w), [(ax - X0, ay - Y0), (bx - X0, by - Y0)], R14["bocel_pt"] * kpt))
        reg *= (1 - (1 - R14["bocel"]) * lb * cheio)[..., None]
        bx, by = p2r(q["lanco1"][0] + R14["triangulo"]["recuo_pt"], (ly0 + ly1) / 2)
        tri = r14_triangulo((h, w), (bx - X0, by - Y0), (1.0, 0.0), kpt)
        reg = reg * (1 - tri[..., None]) + np.float32(R14["triangulo"]["cor"]) * tri[..., None]

    # 3. do 8º em diante, esmaecido sobre o gramado, com os espelhos e o contorno claros
    k_ = q["esmaecer"]
    reg = reg * (1 - k_ * esm[..., None]) + piso * k_ * esm[..., None]
    if q.get("r14"):
        # R14: os bocéis e o contorno do trecho esmaecido tracejados (a projeção); a linha de corte não é desenhada
        def local(x, y):
            u, v = p2r(x, y)
            return u - X0, v - Y0
        traco = np.zeros((h, w), np.float32)
        for lanco in ("lanco1", "lanco2"):
            _, y0, _, y1 = q[lanco]
            for x in q["espelhos"] + [q["lanco1"][2]]:
                traco = np.maximum(traco, r14_tracejado((h, w), [local(x, y0), local(x, y1)], kpt, R14["tracejado_px"]))
        for k in ("lanco1", "lanco2", "patamar"):
            x0, y0, x1, y1 = q[k]
            traco = np.maximum(traco, r14_tracejado((h, w), [local(x0, y0), local(x1, y0), local(x1, y1),
                                                             local(x0, y1), local(x0, y0)], kpt, R14["tracejado_px"]))
        traco *= esm > 0.5
        reg = reg * (1 - traco[..., None]) + np.float32(R14["tracejado"]) * traco[..., None]
    else:
        cor, frc = q["espelho_esm"]
        traco = np.zeros(forma, np.float32)
        for lanco in ("lanco1", "lanco2"):
            _, y0, _, y1 = q[lanco]
            for x in q["espelhos"] + [q["lanco1"][2]]:
                traco = np.maximum(traco, linha_aa(forma, [p2r(x, y0), p2r(x, y1)], 0.5))
        for k in ("lanco1", "lanco2", "patamar"):
            x0, y0, x1, y1 = q[k]
            traco = np.maximum(traco, linha_aa(forma, [p2r(x0, y0), p2r(x1, y0), p2r(x1, y1), p2r(x0, y1)], 0.5,
                                               fechada=True))
        traco = traco[Y0:Y1, X0:X1] * (esm > 0.5)
        reg = reg * (1 - frc * traco[..., None]) + np.float32(cor) * frc * traco[..., None]

        # 4. a linha de corte
        cor, larg = q["corte"]
        lc = np.zeros(forma, np.float32)
        for c in corte:
            lc = np.maximum(lc, linha_aa(forma, c, larg))
        lc = lc[Y0:Y1, X0:X1][..., None]
        reg = reg * (1 - lc) + np.float32(cor) * lc
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    escada interna: degraus 1 a {n} cheios até o corte, o resto esmaecido ({k_:.0%}) sobre o gramado "
          f"aprovado; sem a barreira do motor")
    return out


# Térreo 11 e 12. Quarto e banho do motorista (pedido do usuário, 19/10/26: "representar a cama no quarto do
# motorista. representar a cuba e bancada da pia corretamente no banho do motorista. representar o box e o chuveiro
# adequadamente. o rótulo do quarto do motorista está no local errado"; o arco da porta do banho já foi, nas portas no
# granito). O motor fez a cama e o box como blocos lilás e a pia como uma cuba solta, sem bancada. No PDF
# (ARQ_LAYOUT HUMANIZAÇÃO, ARQ_BANCADAS e ARQ_LOUÇAS E METAIS):
# - a cama de solteiro encostada na parede de cima, com o travesseiro e o edredom com a ponta dobrada;
# - no banho, a bancada na parede de cima e na da direita, com a cuba quadrada de apoio (passa da frente da
#   bancada) e a torneira saindo da parede de cima;
# - o box ocupa a ponta da esquerda, até as duas folhas de vidro de correr, com o chuveiro de braço na parede de cima.
# Sem IA: os blocos do motor viram o granito (tecido de um trecho limpo do quarto, na luz do lugar) e entram, na
# geometria do PDF: a cama (lençol e edredom brancos com volume, a ponta dobrada mostrando o avesso, o travesseiro, a
# sombra curta); a bancada de quartzo com a cuba de louça, a válvula e a torneira cromada; as folhas de vidro do box
# e o chuveiro, como os aprovados. O rótulo do quarto vai para o lado da cama, como no PDF (`rotulos_casaa.py`).
MOTORISTA = {
    "limpar": [(1188, 631, 1211, 678), (1233, 630, 1257, 649), (1259, 576, 1293, 642)],   # px: box, pia, cama
    "fonte_granito": (1292, 585, 1316, 640),
    "cama": (2152.75, 1288.75, 2203.78, 1396.46), "travesseiro": (2156.15, 1292.15, 2200.37, 1315.96),
    "edredom": (2154.45, 1313.69, 2202.08, 1394.76), "dobra": (2191.87, 1313.69, 2202.08, 1323.9),
    "cores_cama": {"base": (196, 202, 210), "edredom": (228, 232, 237), "travesseiro": (238, 241, 244),
                   "avesso": (206, 212, 219), "contorno": (150, 154, 158)},
    "bancada": (2103.57, 1381.16, 2143.25, 1403.83), "cuba": (2112.11, 1388.0, 2134.7, 1410.6),
    "torneira": (2121.99, 1389.87, 2124.83, 1399.65), "valvula": ((2123.4, 1404.0), 1.3),
    "folhas": [(2060.2, 1421.69, 2060.77, 1466.14), (2061.05, 1410.42, 2061.62, 1454.87)],
    "chuveiro": {"ducha": (2039.2, 1388.2, 2042.9, 1391.9), "braco": (2040.5, 1381.8, 2041.7, 1389.2),
                 "canopla": (2039.6, 1381.2, 2042.5, 1381.8)}}


def motorista(out):
    from retoque_bege_bahia_terreo import quilting
    from retoque_subsolo_casae import (Tela, SOMBRA, LOUCA, LOUCA_CONTORNO, BACIA_BORDA, BACIA_FUNDO, CROMO,
                                       CROMO_CLARO, CROMO_ESCURO, QUARTZO, SS, vidro_box, chuveiro)
    q = MOTORISTA
    _, p2r = pdf_pavimento("Terreo")

    # os blocos do motor viram o granito
    apaga = np.zeros(out.shape[:2], bool)
    for x0, y0, x1, y1 in q["limpar"]:
        apaga[y0:y1, x0:x1] = True
    Yo = out.astype(np.float32).mean(axis=2)
    piso = ~cv2.dilate(apaga.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (Yo > 25) & (Yo < 110)
    med = cv2.medianBlur(out, 5).astype(np.float32)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    peso = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 6)
    campo = np.where((peso > 0.05)[..., None], nconv(med, piso.astype(np.float32), 6), nconv(med, piso.astype(np.float32), 18))
    fx0, fy0, fx1, fy1 = q["fonte_granito"]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32) / campo[fy0:fy1, fx0:fx1]
    f = f / f.reshape(-1, 3).mean(axis=0)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    novo = out.astype(np.float32)
    for k, (x0, y0, x1, y1) in enumerate(q["limpar"]):
        tex = quilting(fontes, y1 - y0, x1 - x0, p=16, sobra=5, candidatos=300, rng=np.random.default_rng(651 + k))
        novo[y0:y1, x0:x1] = tex[:y1 - y0, :x1 - x0] * campo[y0:y1, x0:x1]
    a = (cv2.GaussianBlur(apaga.astype(np.float32), (0, 0), 0.7) * apaga)[..., None]
    a *= (Yo > 25)[..., None]                                   # as paredes ficam
    out[:] = np.clip(out * (1 - a) + novo * a, 0, 255).astype(np.uint8)

    # a cama
    c = q["cores_cama"]
    tl = Tela(out, p2r, q["cama"])
    base = tl.ret(q["cama"], 0.8)
    tl.sombra(base, dx=-1.2, dy=1.2, sigma=1.4, forca=0.32)
    tl.pintar(base, c["base"])
    ed = tl.ret(q["edredom"], 1.2)
    dx0, dy0, dx1, dy1 = q["dobra"]
    tri = tl.vazia()                                            # a ponta dobrada (o avesso do edredom)
    pts = np.int32([tl.pt(dx0, dy0), tl.pt(dx1, dy1), tl.pt(dx1, dy0)])
    cv2.fillPoly(tri, [pts], 255)
    ed_sem = ed & ~tri
    dist = cv2.distanceTransform(ed_sem, cv2.DIST_L2, 5) / SS
    tom = 0.88 + 0.12 * np.clip(dist / 3.0, 0, 1)
    a_ = tl.reduzir(ed_sem)[..., None]
    cor = cv2.resize(np.float32(c["edredom"])[None, None] * tom[..., None] * (ed_sem[..., None] / 255.0), (tl.w, tl.h),
                     interpolation=cv2.INTER_AREA)
    tl.reg = tl.reg * (1 - a_) + cor
    tl.pintar(tri & ed, c["avesso"])
    dobra = tl.vazia()
    cv2.line(dobra, tuple(pts[0]), tuple(pts[1]), 255, max(1, int(0.5 * SS)))
    tl.sombra(dobra, dx=-0.4, dy=0.4, sigma=0.4, forca=0.25)
    tl.pintar(dobra & ed, c["contorno"], 0.6)
    tv = tl.ret(q["travesseiro"], 1.6)
    tl.sombra(tv, dx=-0.5, dy=0.5, sigma=0.6, forca=0.22)
    dist = cv2.distanceTransform(tv, cv2.DIST_L2, 5) / SS
    tom = 0.86 + 0.14 * np.clip(dist / 2.2, 0, 1)
    a_ = tl.reduzir(tv)[..., None]
    cor = cv2.resize(np.float32(c["travesseiro"])[None, None] * tom[..., None] * (tv[..., None] / 255.0), (tl.w, tl.h),
                     interpolation=cv2.INTER_AREA)
    tl.reg = tl.reg * (1 - a_) + cor
    tl.contorno(base, 0.3, c["contorno"])
    out = tl.gravar()

    # a bancada, a cuba de apoio e a torneira da parede de cima
    tl = Tela(out, p2r, (q["bancada"][0], q["bancada"][1], q["bancada"][2], q["cuba"][3]))
    b = tl.ret(q["bancada"])
    tl.sombra(b, **SOMBRA)
    tl.pintar(b, QUARTZO)
    tl.contorno(b, 0.35, (150, 153, 155))
    cb = tl.ret(q["cuba"], 2.4)
    tl.sombra(cb, **SOMBRA)
    tl.pintar(cb, LOUCA_CONTORNO)
    x0, y0, x1, y1 = q["cuba"]
    tl.pintar(tl.ret((x0 + 0.8, y0 + 0.8, x1 - 0.8, y1 - 0.8), 2.0), LOUCA)
    for i in range(6):                       # a bacia, da borda ao fundo
        k = i / 5
        tom = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
        ins = 2.0 + k * 3.0
        tl.pintar(tl.ret((x0 + ins, y0 + ins, x1 - ins, y1 - ins), max(0.6, 1.8 - k)), tom)
    (vx, vy), vr = q["valvula"]
    u, v = tl.pt(vx, vy)
    m = tl.vazia()
    cv2.circle(m, (int(u), int(v)), int(vr * 0.5483 * SS), 255, -1)
    tl.pintar(m, CROMO_ESCURO)
    tx0, ty0, tx1, ty1 = q["torneira"]
    m = tl.ret(q["torneira"], 0.6)
    tl.sombra(m, **SOMBRA)
    tl.pintar(m, CROMO_ESCURO)
    tl.pintar(tl.ret((tx0 + 0.3, ty0, (tx0 + tx1) / 2, ty1 - 0.4), 0.3), CROMO_CLARO)
    m = tl.vazia()
    u, v = tl.pt((tx0 + tx1) / 2, ty0 + 0.9)
    cv2.circle(m, (int(u), int(v)), int(1.0 * SS), 255, -1)
    tl.pintar(m, CROMO)
    out = tl.gravar()

    # o box: as duas folhas de vidro de correr e o chuveiro
    for folha in q["folhas"]:
        out = vidro_box(out, p2r, folha)
    ch = q["chuveiro"]
    out = chuveiro(out, p2r, ch["ducha"], ch["braco"], ch["canopla"])
    print("    motorista: blocos do motor em granito; cama com travesseiro e a ponta dobrada; bancada com a cuba de "
          "apoio e a torneira; box com as folhas de vidro e o chuveiro")
    return out


# Térreo, carros (pedido do usuário, 19/10/26: "mude as cores, deixe cada carro com uma única cor e deixe os carros
# desalinhados"). O motor fez o da esquerda branco e os outros dois no mesmo lilás, alinhados. Como nas Casas D e E
# (aprovadas): cada carro numa cor só, a da paleta da Casa D (branco perolado, grafite, azul-marinho), por uma curva
# de tom na luminância do próprio carro (a ordem do render fica: vidros mais escuros que a lataria, reflexos), com a
# cor só nos tons médios e claros (o vidro escuro fica neutro); e cada um com um deslocamento e um giro leves, para
# quebrar o alinhamento: o carro sai com a sombra dele (o granito volta, tecido por image quilting de trechos limpos
# do granito, na luz do lugar) e entra no lugar novo, com a sombra curta.
CARROS_A = {
    "janela": (1150, 680, 1420, 853),                         # px: a garagem (sem a pedra portuguesa de baixo)
    "fontes_granito": [(1292, 585, 1316, 640), (1234, 712, 1248, 842)],   # px: o quarto do motorista e o meio do vão
    # (nome, curva: ("escurecer", base, faixa, expoente) ou ("clarear", ini, fim, força), cor BGR, (dx, dy, giro))
    "carros": [("esquerda", ("clarear", 150.0, 215.0, 0.35), (0.99, 1.0, 1.01), (-1.0, 5.0, -2.0)),     # branco perolado
               ("meio", ("escurecer", 26.0, 74.0, 1.6), (1.02, 1.0, 0.98), (1.5, -4.0, 1.5)),           # grafite
               ("direita", ("escurecer", 18.0, 52.0, 1.4), (1.34, 0.96, 0.74), (-1.5, 3.0, -1.0))],     # azul-marinho
    "lum_carro": 95.0, "fecho": 9, "reflexo": 0.6, "cor_lum": (70.0, 140.0),
    "lanterna": (70, 140),                                    # R - B (e R - G) e R mínimos: só luz vermelha ou âmbar
    "folga": 31, "x_max": 1410,                               # o que sai: o carro e a sombra dele (até o jardim)
    "sombra": {"desloc": (-2.0, 2.0), "sigma": 1.5, "forca": 0.4},
    # R12 (pente fino de 21/10/26, item 3 do Térreo; regra de 19/10: "todos os carros de todas as plantas devem estar
    # alinhados, serem do mesmo tamanho e da mesma cor", prata, 4,70 x 1,85 m, igual nas cinco casas). Substitui as cores
    # e o desalinhamento acima. O modelo é o carro da esquerda do render (o branco), levado ao prata da Casa E pela
    # luminância (os quantis do carro prata do Térreo da Casa E, retocado) e ao tom dela (cinza um pouco frio), sem as
    # lanternas; na escala de 4,70 m de comprimento e 1,85 m de carroceria (sem os retrovisores), sem giro, no centro
    # de cada carro do PDF (ARQ_LAYOUT HUMANIZAÇÃO), os três na mesma linha (a média dos três centros em y).
    "r12": {"modelo": 0, "comprimento_m": 4.70, "largura_m": 1.85, "faixa_largura": (0.35, 0.85),
            "centros_pdf": [(2028.6, 1637.3), (2186.7, 1637.3), (2347.2, 1637.3)],
            "quantis": ((5, 25, 50, 75, 95), (63.0, 101.0, 163.0, 189.0, 214.0)), "tom": (0.988, 0.994, 1.018)}}


def carros_a(out):
    from scipy import ndimage
    from retoque_bege_bahia_terreo import quilting
    q = CARROS_A
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    Y = reg.mean(axis=2)
    m = cv2.morphologyEx((Y > q["lum_carro"]).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((q["fecho"],) * 2, np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    ids = sorted([i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 1500], key=lambda i: cen[i, 0])
    silhuetas = [ndimage.binary_fill_holes(lab == i) for i in ids]
    assert len(silhuetas) == len(q["carros"]), f"{len(silhuetas)} carros achados"
    # 1. cada carro numa cor só
    pintado = reg.copy()
    for sil, (nome, curva, cor, _) in zip(silhuetas, q["carros"]):
        lanterna = (reg[..., 2] - reg[..., 0] > q["lanterna"][0]) & (reg[..., 2] > q["lanterna"][1]) & \
            (reg[..., 2] - reg[..., 1] > q["lanterna"][0])
        topo = np.percentile(Y[sil], 97)
        if curva[0] == "escurecer":
            _, base, faixa, ex = curva
            Yn = base + faixa * np.clip(Y / topo, 0, 1) ** ex + q["reflexo"] * np.clip(Y - topo, 0, None)
        else:
            _, ini_, fim_, forca = curva
            t = np.clip((Y - ini_) / (fim_ - ini_), 0, 1)
            Yn = Y + forca * t * t * (3 - 2 * t) * (250 - Y)
        lo, hi = q["cor_lum"]
        sc = np.clip((Y - lo) / (hi - lo), 0, 1)[..., None]
        novo = Yn[..., None] * (1 + sc * (np.float32(cor)[None, None] - 1))
        a = (sil & ~lanterna)[..., None]
        pintado = np.where(a, novo, pintado)
        print(f"    carro da {nome}: curva {curva[0]}, cor {cor}")
    # 2. os carros saem: o granito tecido dos vãos, na luz do lugar
    tudo = np.zeros(Y.shape, bool)
    for s_ in silhuetas:
        tudo |= s_
    sai = cv2.dilate(tudo.astype(np.uint8), np.ones((q["folga"],) * 2, np.uint8)) > 0
    sai[:, q["x_max"] - wx0:] = False
    apaga = np.zeros(out.shape[:2], bool)
    apaga[wy0:wy1, wx0:wx1] = sai
    Yo = out.astype(np.float32).mean(axis=2)
    janela = np.zeros_like(apaga)
    janela[wy0:wy1, wx0:wx1] = True
    piso = janela & ~cv2.dilate(apaga.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (Yo > 25) & (Yo < 110)
    med = cv2.medianBlur(out, 5).astype(np.float32)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    peso = cv2.GaussianBlur(piso.astype(np.float32), (0, 0), 10)
    campo = np.where((peso > 0.05)[..., None], nconv(med, piso.astype(np.float32), 10),
                     nconv(med, piso.astype(np.float32), 30))
    fontes = []
    for fx0, fy0, fx1, fy1 in q["fontes_granito"]:
        f = out[fy0:fy1, fx0:fx1].astype(np.float32) / cv2.GaussianBlur(med[fy0:fy1, fx0:fx1], (0, 0), 6)
        f = f / f.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    tex = quilting(fontes, wy1 - wy0, wx1 - wx0, p=14, sobra=5, candidatos=400, rng=np.random.default_rng(652))
    novo_g = out.astype(np.float32)
    novo_g[wy0:wy1, wx0:wx1] = tex[:wy1 - wy0, :wx1 - wx0] * campo[wy0:wy1, wx0:wx1]
    a = (cv2.GaussianBlur(apaga.astype(np.float32), (0, 0), 1.0) * apaga)[..., None]
    out[:] = np.clip(out * (1 - a) + novo_g * a, 0, 255).astype(np.uint8)
    if "r12" in q:
        return carros_r12_a(out, reg, silhuetas[q["r12"]["modelo"]])
    # 3. e entram no lugar novo, com o giro leve e a sombra curta
    h, w = Y.shape
    s = q["sombra"]
    for sil, (nome, _, _, (dx, dy, ang)) in zip(silhuetas, q["carros"]):
        ys, xs = np.nonzero(sil)
        c = (float(xs.mean()), float(ys.mean()))
        M = cv2.getRotationMatrix2D(c, ang, 1.0)
        M[:, 2] += (dx, dy)
        alfa = cv2.warpAffine(cv2.GaussianBlur(sil.astype(np.float32), (0, 0), 0.5), M, (w, h), flags=cv2.INTER_LINEAR)
        img = cv2.warpAffine(pintado, M, (w, h), flags=cv2.INTER_LINEAR)
        S = np.float32([[1, 0, s["desloc"][0]], [0, 1, s["desloc"][1]]])
        sb = cv2.GaussianBlur(cv2.warpAffine(alfa, S, (w, h)), (0, 0), s["sigma"]) * (1 - alfa)
        r = out[wy0:wy1, wx0:wx1].astype(np.float32) * (1 - s["forca"] * sb)[..., None]
        a = np.clip(alfa, 0, 1)[..., None]
        out[wy0:wy1, wx0:wx1] = np.clip(r * (1 - a) + img * a, 0, 255).astype(np.uint8)
    print(f"    garagem: {len(silhuetas)} carros, cada um numa cor, com deslocamento e giro leves")
    return out


def carros_r12_a(out, orig, sil):
    """Os carros da R12: o modelo (o carro branco do render, levado ao prata) na escala de 4,70 x 1,85 m, no centro
    de cada carro do PDF, alinhados. orig: a janela da garagem antes de tudo (BGR, float); sil: a silhueta do modelo."""
    q, r = CARROS_A, CARROS_A["r12"]
    wx0, wy0, wx1, wy1 = q["janela"]
    h, w = wy1 - wy0, wx1 - wx0
    _, p2r = pdf_pavimento("Terreo")
    px_m = p2r(56.69, 0)[0] - p2r(0, 0)[0]                     # 1 m na escala 1:50 = 56,69 pt
    # o prata: a luminância do modelo levada aos quantis do carro prata da Casa E, no tom dele; as lanternas ficam
    Y = orig.mean(axis=2)
    lanterna = (orig[..., 2] - orig[..., 0] > q["lanterna"][0]) & (orig[..., 2] > q["lanterna"][1]) & \
        (orig[..., 2] - orig[..., 1] > q["lanterna"][0])
    pq, alvo = r["quantis"]
    fonte = np.percentile(Y[sil & ~lanterna], pq)
    Yn = np.interp(Y, fonte, alvo)
    prata = np.where((sil & ~lanterna)[..., None], Yn[..., None] * np.float32(r["tom"]), orig)
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
    for px, py in r["centros_pdf"]:
        tx, ty = p2r(px, py)
        M = np.float32([[sx, 0, tx - wx0 - sx * cx], [0, sy, ty - wy0 - sy * cy]])
        alfa = cv2.warpAffine(alfa0, M, (w, h), flags=cv2.INTER_LINEAR)
        img = cv2.warpAffine(prata, M, (w, h), flags=cv2.INTER_CUBIC)
        S = np.float32([[1, 0, s["desloc"][0]], [0, 1, s["desloc"][1]]])
        sb = cv2.GaussianBlur(cv2.warpAffine(alfa, S, (w, h)), (0, 0), s["sigma"]) * (1 - alfa)
        reg = out[wy0:wy1, wx0:wx1].astype(np.float32) * (1 - s["forca"] * sb)[..., None]
        al = np.clip(alfa, 0, 1)[..., None]
        out[wy0:wy1, wx0:wx1] = np.clip(reg * (1 - al) + img * al, 0, 255).astype(np.uint8)
    print(f"    garagem (R12): {len(r['centros_pdf'])} carros prata iguais, de {r['comprimento_m']:.2f} x "
          f"{r['largura_m']:.2f} m ({comp * sy:.0f} x {larg * sx:.0f} px; modelo de {comp} x {larg:.0f} px), "
          f"alinhados nos centros do PDF")
    return out


# Térreo, sem arcos (decisão do usuário, 19/10/26, com as plantas de referência dos elementos, que não desenham o
# arco das portas: "remover os arcos, escadas com linhas"). Todos os arcos de porta do PDF da Casa A (as curvas da
# ARQ_PAREDE: 16 portas de giro, a pivotante com o arco grande e o pequeno, e as 12 da porta camarão da varanda)
# saem da imagem, os do motor e os que os itens acima desenharam no lugar do PDF; as folhas e os batentes ficam.
# - Portas de giro (o arco é um quarto de círculo): o círculo pelas pontas e pelo meio do arco, levado à imagem. Na
#   faixa de ±3 px em volta dele, onde o traço passa (o que difere do piso de dentro e de fora da faixa, na mesma
#   direção), a faixa inteira vira a textura do mesmo piso logo depois dela, na mesma direção (de quatro afastamentos,
#   o mais parecido com o piso em volta), com a borda suave: não fica fantasma do traço nem do halo claro dele. Onde
#   nenhum afastamento serve (o traço passa junto a um móvel), inpaint. Ficam de fora a folha e o batente (as retas
#   do centro às pontas do arco) e o que é preto.
# - Porta camarão (os arcos rasos, de 0,5 m): o motor pintou de cinza o setor entre cada folha e o arco. O setor
#   inteiro, menos as folhas pretas, vira travertino tecido de trechos limpos da varanda, normalizado, vezes o campo de
#   luz do piso em volta (convolução normalizada). Ficam as folhas em zigue-zague, as sombras delas e o trilho.
SEM_ARCOS = {"camada": "ARQ_PAREDE", "tol": 3.0, "limiar": 7, "inpaint": 18, "raso": 1.6,
             "camarao_fontes": [(705, 632, 765, 700), (690, 778, 760, 806)]}     # x0, y0, x1, y1 (px)


def sem_arcos(out):
    from arcos import remover_arcos
    q = SEM_ARCOS
    pg, p2r = pdf_pavimento("Terreo")
    return remover_arcos(out, pg, p2r, camadas=(q["camada"],), tol=q["tol"], limiar=q["limiar"],
                         inpaint=q["inpaint"], raso=q["raso"], camarao_fontes=q["camarao_fontes"])


# Térreo, rejuntes (pedido do usuário, 19/10/26: "Precisamos remover os rejuntes"; escopo escolhido por ele: o piso
# interno do Térreo). O travertino da varanda, das salas, do hall interno, da área gourmet e dos cômodos saiu em
# placas grandes, com a junta marcada (linhas finas verticais e horizontais) e cada placa num tom. O piso volta
# contínuo, com a textura do próprio render e na luz dele:
# - onde: o travertino da legenda (#DCD9CA na base v6, levada à imagem pelo afim do Térreo), sem a escada interna;
#   dentro dele, só o que é piso pela cor (claro e quente como o travertino). Ficam os móveis, os tapetes, as
#   paredes, os traços desenhados (os do PDF: tracejados de projeção, arcos e folhas de porta, escadas; e o que for
#   muito mais escuro que o piso em volta) e um anel de 3 px em volta de tudo isso;
# - a textura: miolos de 32 px do próprio piso sem junta vertical (os veios horizontais do travertino ficam, são a
#   textura), sem os pontinhos escuros, cada um dividido pela luz do lugar, tecidos por image quilting;
# - a luz: o tom do piso em volta, suavizado (sigma 12 px) o bastante para os degraus de tom entre placas sumirem;
#   as sombras dos móveis ficam (o que é 2 a 7% ou mais mais escuro que a luz do lugar);
# - no anel em volta dos móveis e dos traços, o piso original fica, no tom do piso refeito ao lado; o que sobrou de
#   junta vertical ali vira a média dos dois lados.
REJUNTES = {"legenda": (0xCA, 0xD9, 0xDC), "tol": 8,      # travertino na base (BGR)
            "fora": [(1185, 462, 1335, 556)],             # a escada interna (px da imagem: x0, y0, x1, y1)
            "piso": {"L": (140, 214), "quente": (22, 44), "sat": (20, 46)},
            "camadas_desenho": ("DOC_LINHAS E PROJEÇÕES", "ARQ_PAREDE", "ARQ_ESCADAS E RAMPAS", "ARQ_PERGOLADO"),
            "traco": 35,                                  # traço desenhado: mais escuro que a mediana 9 px por isto
            "anel": 7, "janela": 32, "luz": 12}


def rejuntes(out):
    import json
    from retoque_bege_bahia_terreo import quilting
    q = REJUNTES
    import rotulos_casaa as A
    cfg = json.loads(A.CONFIG.read_text())
    base = cv2.imread(str((A.CONFIG.parent / cfg["entrega"]["pasta_bases"] /
                           cfg["entrega"]["pavimentos"]["Terreo"]["base"]).resolve()))
    b2 = cv2.resize(base, (2000, round(base.shape[0] * 2000 / base.shape[1])), interpolation=cv2.INTER_NEAREST)
    trav = (np.abs(b2.astype(int) - q["legenda"]).max(axis=2) <= q["tol"]).astype(np.uint8)
    T = cv2.warpAffine(trav, np.float32(AFIM_QR["Terreo"]), (out.shape[1], out.shape[0]), flags=cv2.INTER_NEAREST)
    for x0, y0, x1, y1 in q["fora"]:
        T[y0:y1, x0:x1] = 0
    T = cv2.erode(T, np.ones((3, 3), np.uint8)).astype(bool)
    rf = out.astype(np.float32)
    L = cv2.GaussianBlur(rf.mean(axis=2), (0, 0), 0.5)
    sat, quente = rf.max(axis=2) - rf.min(axis=2), rf[..., 2] - rf[..., 0]
    pp = q["piso"]
    piso = T & (rf.mean(axis=2) >= pp["L"][0]) & (rf.mean(axis=2) <= pp["L"][1]) & (quente >= pp["quente"][0]) & \
        (quente <= pp["quente"][1]) & (sat >= pp["sat"][0]) & (sat <= pp["sat"][1])
    # os traços desenhados ficam: os do PDF (tracejados de projeção, arcos e folhas de porta, escadas, pergolado),
    # rasterizados e levados à imagem, com 2 px de folga; e o que for muito mais escuro que o piso em volta (as
    # juntas do motor chegam a -25; os traços, a -40 ou mais)
    import pymupdf
    pg, p2r = pdf_pavimento("Terreo")
    doc = pg.parent
    for u in doc.layer_ui_configs():
        doc.set_layer_ui_config(u["number"], action=0 if u["text"] in q["camadas_desenho"] else 2)
    Z = 4
    pix = doc[pg.number].get_pixmap(matrix=pymupdf.Matrix(Z, Z), alpha=False)
    des = (np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).min(axis=2) < 200).astype(np.uint8)
    src = np.float32([[100, 100], [1500, 100], [100, 1500]])
    M = np.vstack([cv2.getAffineTransform(src, np.float32([p2r(*pt) for pt in src])), [0, 0, 1]]) @ np.diag([1 / Z, 1 / Z, 1])
    des = cv2.warpAffine(des * 255, M[:2], (out.shape[1], out.shape[0]), flags=cv2.INTER_AREA) > 20
    forte = (L - cv2.medianBlur(out, 9).astype(np.float32).mean(axis=2)) < -q["traco"]
    piso &= ~cv2.dilate((des | forte).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    piso = cv2.morphologyEx(piso.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (q["anel"], q["anel"]))
    nucleo = piso & ~cv2.dilate((T & ~piso).astype(np.uint8), k).astype(bool)

    def nconv(img, m, sig):
        return cv2.GaussianBlur(img * m[..., None], (0, 0), sig) / \
            np.maximum(cv2.GaussianBlur(m, (0, 0), sig), 1e-4)[..., None]
    med5 = cv2.medianBlur(out, 5).astype(np.float32)
    campo = nconv(med5, nucleo.astype(np.float32), q["luz"])
    d = np.clip(1 - nconv(med5, piso.astype(np.float32), 1.5).mean(axis=2) / np.maximum(campo.mean(axis=2), 1), 0, 1)
    t = np.clip((d - 0.02) / 0.05, 0, 1)
    fator = 1 - d * t * t * (3 - 2 * t)                    # as sombras dos móveis

    dv = L - 0.5 * (np.roll(L, 2, axis=1) + np.roll(L, -2, axis=1))
    J = q["janela"]
    ys, xs = np.nonzero(nucleo)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    cob = cv2.blur(nucleo.astype(np.float32), (J, J), anchor=(0, 0), borderType=cv2.BORDER_CONSTANT)
    usados, fontes = [], []
    for yy in range(y0, y1 - J, 6):
        for xx in range(x0, x1 - J, 6):
            if cob[yy, xx] >= 0.98 and (dv[yy:yy + J, xx:xx + J] < -1.2).mean(axis=0).max() < 0.5 and \
                    all(abs(yy - a) >= 24 or abs(xx - b) >= 24 for a, b in usados):
                usados.append((yy, xx))
    for yy, xx in usados:
        g = rf[yy:yy + J, xx:xx + J].copy()
        md = med5[yy:yy + J, xx:xx + J]
        pinta = (md.mean(axis=2) - g.mean(axis=2)) > 7
        g[pinta] = md[pinta]
        g = g / campo[yy:yy + J, xx:xx + J]
        g = g / g.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(g), np.ascontiguousarray(g[:, ::-1])]
    tex = quilting(fontes, y1 - y0, x1 - x0, p=30, sobra=9, candidatos=500, rng=np.random.default_rng(642))
    novo = rf.copy()
    novo[y0:y1, x0:x1] = tex * campo[y0:y1, x0:x1] * fator[y0:y1, x0:x1, None]
    a = (cv2.GaussianBlur(nucleo.astype(np.float32), (0, 0), 0.7) * nucleo)[..., None]
    res = rf * (1 - a) + novo * a
    # no anel em volta dos móveis e dos traços, o piso original fica, mas no tom novo: a razão entre o piso refeito e
    # o original ali perto (as placas tinham tons diferentes; sem isso a borda do anel marca um degrau)
    wn = nucleo.astype(np.float32)
    den = cv2.GaussianBlur(wn, (0, 0), 4)
    razao = cv2.GaussianBlur(res * wn[..., None], (0, 0), 4) / np.maximum(cv2.GaussianBlur(rf * wn[..., None], (0, 0), 4), 1)
    razao = np.where(den[..., None] > 0.05, razao, 1.0)
    anel = (piso & ~nucleo).astype(np.float32)[..., None] * (1 - a)
    res = res * (1 - anel) + res * razao * anel
    # o que sobrou de junta vertical no anel em volta dos móveis: a média dos dois lados (2 px)
    Lo = res.mean(axis=2)
    c = ((Lo - 0.5 * (np.roll(Lo, 2, axis=1) + np.roll(Lo, -2, axis=1)) < -1.2) & piso).astype(np.float32)
    fv = cv2.filter2D(c, -1, np.ones((20, 1), np.float32) / 20) >= 0.7
    fv = cv2.dilate(fv.astype(np.uint8), np.ones((10, 1), np.uint8)).astype(bool) & (c > 0) & T
    fv = cv2.dilate(fv.astype(np.uint8), np.ones((1, 2), np.uint8)).astype(bool) & piso
    yv, xv = np.nonzero(fv)
    res[yv, xv] = 0.5 * (res[yv, np.clip(xv - 2, 0, None)] + res[yv, np.clip(xv + 2, None, out.shape[1] - 1)])
    out[:] = np.clip(np.round(res), 0, 255).astype(np.uint8)
    print(f"    rejuntes: travertino {int(T.sum())} px, piso {int(piso.sum())} px, refeito {int(nucleo.sum())} px "
          f"({len(usados)} miolos de {J} px); resto de junta vertical no anel: {len(yv)} px")
    return out


# Pente fino pelas regras (21/10/26), Subsolo, item 1: só o Subsolo, com o resto do terreno hachurado (R2, seção 11). A
# imagem do Subsolo trazia, esmaecidos, o deck, a piscina, o spa, a escada larga e as espreguiçadeiras do Térreo (o PDF
# do Subsolo os desenha em cinza). Fica só o Subsolo, a pegada: os pisos e as paredes dele no PDF (as peças cheias da
# ARQ_CONTRAPISO e da ARQ_PAREDE dentro da caixa do Subsolo; as do Térreo ficam à esquerda e acima dela), com a
# circulação externa; a escada do deck (ARQ_ESCADAS E RAMPAS); e o gramado abaixo dela (item 13 de 19/10; confirmado em
# 21/10: o gramado fica). O resto vira branco; na faixa de 2 px em volta da pegada, só o preto das paredes fica (o
# traço do render passa um pouco do PDF). A pegada vai para `SUBSOLO_R2["mascara"]`; na final, o rotulos_casaa.py a leva
# ao quadro pelo mesmo afim da imagem e chama `subsolo_hachurado`: o lote do Térreo final (o que não é branco nele, no
# mesmo quadro, fechado e sem furos) em diagonais finas a 45° (/), cinza 198, a cada 0,40 m, com traço de 1,3 px e o
# contorno do lote em cinza fino (165), como no Subsolo da Casa E (`retoque_subsolo_casae.contexto_hachura`).
SUBSOLO_R2 = {"caixa_pt": (900.0, 1040.0, 2400.0, 1800.0), "camadas": ("ARQ_CONTRAPISO", "ARQ_PAREDE"),
              "escada": "ARQ_ESCADAS E RAMPAS", "ss": 4, "fechar": 5, "anel": 2, "parede": 100,
              "mascara": CASA / "renders/POE642_CasaA_PH_Subsolo_pegada_mascara.png",
              "terreo": CASA / "renders/POE642_CasaA_PH_Terreo_final_rotulos.png",
              "hachura": {"passo_m": 0.40, "largura_px": 1.3, "cor": (198, 198, 198), "contorno_px": 1.6,
                          "cor_contorno": (165, 165, 165)}}


def so_subsolo(out):
    from scipy import ndimage
    q = SUBSOLO_R2
    pg, p2r = pdf_pavimento("Subsolo")
    H, W = out.shape[:2]
    k = q["ss"]
    m = np.zeros((H * k, W * k), np.uint8)
    cx0, cy0, cx1, cy1 = q["caixa_pt"]
    n = 0
    ex, ey = [], []
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") == q["escada"]:
            ex += [r.x0, r.x1]
            ey += [r.y0, r.y1]
        elif (d.get("layer") in q["camadas"] and d["type"] in ("f", "fs") and cx0 <= r.x0 and r.x1 <= cx1
              and cy0 <= r.y0 and r.y1 <= cy1):
            for c in caminhos_pdf(d, p2r):
                cv2.fillPoly(m, [np.int32(np.round(c * k))], 255)
            n += 1
    # a escada do deck: a caixa das linhas dela
    (ax, ay), (bx, by) = p2r(min(ex), min(ey)), p2r(max(ex), max(ey))
    cv2.rectangle(m, (int(round(ax * k)), int(round(ay * k))), (int(round(bx * k)), int(round(by * k))), 255, -1)
    peg = cv2.resize(m.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    # o gramado abaixo da escada (item 13): o verde da caixa dele
    gx0, gy0, gx1, gy1 = GRAMADO_ESCADA["caixa"]
    reg = out[gy0:gy1, gx0:gx1].astype(np.int32)
    verde = (reg[..., 1] > reg[..., 2] + 8) & (reg[..., 1] > reg[..., 0] + 8)
    verde = ndimage.binary_fill_holes(cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)))
    peg[gy0:gy1, gx0:gx1] = np.maximum(peg[gy0:gy1, gx0:gx1], verde)
    # as costuras entre o gramado, a escada e a circulação (o px de borda do render, de 1 a 2 px) ficam na pegada
    f = q["fechar"]
    peg = np.maximum(peg, cv2.morphologyEx((peg > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((f, f), np.uint8)))
    # em volta da pegada, o preto das paredes do render fica
    a = q["anel"]
    perto = cv2.dilate((peg > 0.5).astype(np.uint8), np.ones((2 * a + 1, 2 * a + 1), np.uint8)).astype(bool)
    parede = perto & (out.astype(np.float32).mean(axis=2) < q["parede"])
    peg = np.maximum(peg, parede)
    img = out.astype(np.float32) * peg[..., None] + 255 * (1 - peg[..., None])
    cv2.imwrite(str(q["mascara"]), np.round(peg * 255).astype(np.uint8))
    fora = (peg < 0.5) & (out.min(axis=2) < 245)
    print(f"    só o Subsolo (R2): {n} peças do PDF na pegada, mais a escada do deck e o gramado ({int(verde.sum())} px); "
          f"{int(fora.sum())} px do Térreo em volta viram branco; pegada em {q['mascara'].name}")
    return np.clip(np.round(img), 0, 255).astype(np.uint8)


def subsolo_hachurado(final, pegada, px_m):
    """Na final do Subsolo (no quadro comum): fora da pegada (0 a 1, no quadro), o lote do Térreo final hachurado."""
    from scipy import ndimage
    q = SUBSOLO_R2
    h = q["hachura"]
    H, W = final.shape[:2]
    t = cv2.imread(str(q["terreo"]))
    if t.shape[:2] != (H, W):
        t = cv2.resize(t, (W, H), interpolation=cv2.INTER_AREA)
    nb = cv2.morphologyEx((t.min(axis=2) < 235).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb, connectivity=8)
    lote = ndimage.binary_fill_holes(lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    s = h["passo_m"] * px_m
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fr = np.mod((xx + yy) / np.sqrt(2), s)
    dist = np.minimum(fr, s - fr)
    a = np.clip(h["largura_px"] / 2 + 0.5 - dist, 0, 1) * lote
    fundo = np.full((H, W, 3), 255, np.float32)
    fundo = fundo * (1 - a[..., None]) + np.float32(h["cor"]) * a[..., None]
    borda = lote & ~cv2.erode(lote.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    k = max(1, int(round(h["contorno_px"])))
    borda = cv2.dilate(borda.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & lote
    fundo[borda] = h["cor_contorno"]
    p = np.clip(pegada, 0, 1)[..., None]
    out = final.astype(np.float32) * p + fundo * (1 - p)
    print(f"    terreno hachurado (R2): lote do Térreo final em {100 * lote.mean():.1f}% do quadro, diagonais a cada {s:.1f} px")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), Subsolo, item 4: portas sem arcos (R3). Os 5 arcos de porta do PDF do Subsolo (as
# curvas da ARQ_PAREDE: depósito, banho de serviço, sauna e banhos feminino e masculino) saem; as folhas e os batentes
# ficam. Aqui os arcos do render são traços de 1 px; a rotina do Térreo (arcos.remover_arcos, que refaz uma faixa de
# ±3 px com a textura do piso ao lado) quebrava a grade da pastilha do banho de serviço e deixava uma mancha na sauna.
# Sai só o traço: o arco do PDF numa faixa de 4 px, refeito por inpaint de raio curto (a grade da pastilha e o
# travertino continuam por cima dele).
SEM_ARCOS_SUB = {"camada": "ARQ_PAREDE", "largura_px": 4.0, "raio": 2, "ss": 8, "limiar": 40}


def sem_arcos_subsolo(out):
    return sem_arcos_pdf(out, "Subsolo")


def inpaint_sem_parede(out, m, raio, parede):
    """Inpaint que não puxa o preto da parede: os pixels de `parede` na vizinhança da máscara entram como desconhecidos
    (não servem de fonte) e voltam como estavam; o que é da máscara fora da parede se refaz só com o piso."""
    viz = cv2.dilate(m.astype(np.uint8), np.ones((2 * raio + 5, 2 * raio + 5), np.uint8)) > 0
    r = cv2.inpaint(out, ((m > 0) | (parede & viz)).astype(np.uint8), raio, cv2.INPAINT_TELEA)
    sel = (m > 0) & ~parede
    out = out.copy()
    out[sel] = r[sel]
    return out


def sem_arcos_pdf(out, chave, busca=None):
    """Os arcos de porta do PDF (as curvas da ARQ_PAREDE) saem: o traço numa faixa de 4 px, refeito por inpaint. Com
    `busca`, o inpaint não puxa a parede, as linhas retas do desenho nem o piso mais claro ao lado
    (`inpaint_sem_parede`), e uma segunda passada numa faixa mais larga refaz o que ainda é mais escuro que o piso em
    volta (o arco do render fora do lugar do PDF), longe das paredes e dos batentes do PDF; junto às folhas (os brancos
    compridos da ARQ_PAREDE), tudo menos a linha da folha (o escuro em fio no sentido dela): sai o toco do arco que
    chega à ponta."""
    q = SEM_ARCOS_SUB
    pg, p2r = pdf_pavimento(chave)
    H, W = out.shape[:2]
    k = q["ss"]
    m = np.zeros((H * k, W * k), np.uint8)
    arcos = []
    for d in pg.get_drawings():
        if d.get("layer") == q["camada"] and d["type"] == "s" and any(it[0] == "c" for it in d["items"]):
            cs = caminhos_pdf(d, p2r, 24)
            for c in cs:
                cv2.polylines(m, [np.int32(np.round(c * k))], False, 255, int(q["largura_px"] * k), cv2.LINE_AA)
            arcos.append(cs)
    n = len(arcos)
    traco = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA) > q["limiar"]
    if busca is None:
        out = cv2.inpaint(out, traco.astype(np.uint8), q["raio"], cv2.INPAINT_TELEA)
        print(f"    portas sem arcos: {n} arcos do PDF fora ({int(traco.sum())} px, inpaint de raio {q['raio']})")
        return out
    # o que fica e não serve de fonte: a parede (com folga), as linhas retas do desenho (o escuro em fio de n_f px ou
    # mais, em pé ou deitado: a borda da bancada, as folhas, os trilhos) que o arco cruza ou toca, e, na faixa de cada
    # arco, o outro piso mais claro (o arco no vinílico da suíte junto ao piso claro da circulação)
    L = out.astype(np.float32).mean(axis=2)
    kp, n_f, t = 2 * busca["folga_parede"] + 1, busca["fio"], busca["outro_piso"]
    parede = cv2.dilate((L < busca["parede"]).astype(np.uint8), np.ones((kp, kp), np.uint8)) > 0
    med = cv2.medianBlur(np.clip(L, 0, 255).astype(np.uint8), 9).astype(np.float32)
    escuro = (L < med - busca["escuro"]).astype(np.uint8)
    fios = (cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((1, n_f), np.uint8)) |
            cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((n_f, 1), np.uint8))) > 0
    faixa, piso = np.zeros((H, W), bool), np.zeros((H, W), np.float32)
    for cs in arcos:                        # o piso de cada arco: a mediana da faixa dele, fora do traço e das linhas
        f = np.zeros((H, W), np.uint8)
        for c in cs:
            cv2.polylines(f, [np.int32(np.round(c))], False, 255, busca["faixa"])
        f = f > 0
        livre = f & ~traco & ~parede & ~fios
        piso[f] = np.median(L[livre if livre.any() else f])
        faixa |= f
    fixo = parede | fios | (faixa & (L > piso + t))
    out = inpaint_sem_parede(out, traco, q["raio"], fixo)
    print(f"    portas sem arcos: {n} arcos do PDF fora ({int((traco & ~fixo).sum())} px, inpaint de raio {q['raio']}, "
          f"sem puxar a parede, as linhas retas de {n_f} px ou mais nem o outro piso)")
    batentes = np.zeros((H * k, W * k), np.uint8)
    folhas = {0: np.zeros((H * k, W * k), np.uint8), 1: np.zeros((H * k, W * k), np.uint8)}   # 0: em pé; 1: deitadas
    for d in pg.get_drawings():
        if d.get("layer") == q["camada"] and d["type"] == "f" and d.get("fill") and min(d["fill"]) > 0.9:
            for c in caminhos_pdf(d, p2r):
                w, h = np.ptp(c[:, 0]), np.ptp(c[:, 1])
                folha = max(w, h) >= max(busca["folha_comprida"] * min(w, h), busca["folha_min"])
                alvo = folhas[int(w > h)] if folha else batentes
                cv2.fillPoly(alvo, [np.int32(np.round(c * k))], 255)
    perto = lambda z, f: cv2.dilate((cv2.resize(z, (W, H), interpolation=cv2.INTER_AREA) > 0).astype(np.uint8),
                                    np.ones((2 * f + 1, 2 * f + 1), np.uint8)) > 0
    L = out.astype(np.float32).mean(axis=2)
    med = cv2.medianBlur(np.clip(L, 0, 255).astype(np.uint8), 9).astype(np.float32)
    escuro = L < med - busca["escuro"]
    n_l = busca["linha_folha"]
    linha = np.zeros((H, W), bool)          # a linha da folha: o escuro em fio de n_l px ou mais, no sentido da folha
    for deitada, z in folhas.items():
        fio = np.ones((1, n_l) if deitada else (n_l, 1), np.uint8)
        linha |= cv2.morphologyEx((escuro & perto(z, busca["folga_folha"])).astype(np.uint8), cv2.MORPH_OPEN, fio) > 0
    resto = faixa & escuro & ~perto(batentes, busca["folga_batente"]) & ~linha & ~fixo
    resto = (cv2.dilate(resto.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~linha
    out = inpaint_sem_parede(out, resto, q["raio"], fixo)
    print(f"    segunda passada: {int((resto & ~fixo).sum())} px do arco do render fora do lugar do PDF (faixa de "
          f"{busca['faixa']} px; junto às folhas, fica só a linha delas)")
    return out


# Pente fino pelas regras (21/10/26), Subsolo, item 3: a escada do deck (R14, seção 5). No PDF do Subsolo ela sobe da
# circulação (o "S"), da direita para a esquerda, até o deck; o corte é a diagonal da ARQ_ESCADAS E RAMPAS (de 754,1;
# 1230,9 a 788,2; 1299,0 pt), e o trecho depois dele (os degraus 9 a 11, junto ao deck) é a projeção, tracejada. Os
# degraus do Subsolo (item 3 de 19/10, no creme da escada com a textura do Bege Bahia) perdem a sombra de espelho, que
# lia como linha, e ganham a linha suave em cada bocel com a sombra curta (`retoque_terreo_casae.escada_linhas`, a mesma
# rotina e os mesmos bocéis da escada no Térreo); depois do corte, o creme esmaecido e liso (as linhas antigas saem),
# com os bocéis e o contorno tracejados por cima; o triângulo no 1º degrau, junto à circulação, apontando para a
# esquerda (a subida).
ESCADA_DECK_SUB = {"nome": "do deck, no Subsolo: sobe da circulação, da direita para a esquerda",
                   "pdf": (737.1, 1230.9, 907.2, 1299.0), "bocels": [754.1 + 17.0 * k for k in range(9)],
                   "baixo": "direita", "inicio": "direita", "corte": [(754.1, 1230.9), (788.2, 1299.0)],
                   "viva": "direita", "apos": "tracejada", "esmaecer": 1.0, "esmaecido": 0.45}


def escada_deck_subsolo(out):
    from retoque_terreo_casae import escada_linhas
    e = ESCADA_DECK_SUB
    _, p2r = pdf_pavimento("Subsolo")
    ex0, ey0, ex1, ey1 = e["pdf"]
    (c0, c1) = e["corte"]
    apos = r14_poligono(out.shape[:2], [p2r(*c0), p2r(*c1), p2r(ex0, ey1), p2r(ex0, ey0)])[..., None]
    cor = 255 - (255 - np.float32(ESCADA["cor"])) * e["esmaecido"]
    img = out.astype(np.float32) * (1 - apos) + cor * apos
    return escada_linhas(np.clip(np.round(img), 0, 255).astype(np.uint8), None, e, p2r=p2r)


# Pente fino pelas regras (21/10/26), Subsolo, item 5: portas, vidros e janelas finos (seções 4 e 18).
# - Circulação interna para a externa: o motor fez a porta de correr como um traço preto grosso, com um degrau no meio.
#   No PDF (ARQ_PAREDE) são duas folhas de vidro de 2,83 pt desencontradas (a da esquerda mais para fora), com as pontas
#   brancas. O traço sai com a sombra dele (numa faixa de 6 px, a metade de cima recebe o Bege Bahia de cima em espelho
#   e a de baixo, o de baixo) e entram as folhas no vidro das portas da academia: claras, com a linha do meio e as pontas
#   em alumínio; a borda, de 0,25 px de cada lado (na madeira da academia basta 1/8), para a folha ler no Bege Bahia.
# - Folhas das portas de giro (R3: brancas, finas, com contorno fino): a do depósito era um bloco cinza de ~5 px logo
#   abaixo da folha do PDF (sai: o piso de cima, em espelho); as do banho de serviço, da sauna e dos banhos feminino e
#   masculino eram um traço escuro de 1 a 3 px (sai: cada lado do traço recebe o piso do seu lado, em espelho; no banho
#   de serviço, a parede está 2 px abaixo, e o traço recebe só o piso de baixo). Entram as folhas do PDF (2,27 pt, com
#   as pontas), brancas, com o contorno de 0,25 px de cada lado, pelo mesmo motivo.
# - Janela entre o depósito e a academia: o vão no meio da parede (de 1156,66 a 1224,69 pt) estava cinza-escuro; entra
#   o vidro claro, com a borda fina e a linha do meio. A parede em volta fica preta.
# - Vidros da sauna (folha contínua, seção 18): o de cima tinha um montante (duas marcas escuras a um terço) e os dois
#   trechos em tons diferentes; em cada linha do vidro entra a mediana do trecho. O da esquerda já é contínuo.
VIDROS_SUB = {
    "correr": {"faixa": (626, 694, 537, 540, 543),   # px: colunas x0..x1 e linhas y0..ym..y1 (exclusivos); paredes fora
               "borda": 0.6,
               "folhas": [(1018.89, 1217.88, 1082.67, 1220.72), (1080.40, 1215.05, 1144.18, 1217.88)],
               "pontas": [(1017.76, 1217.88, 1018.89, 1220.72), (1082.67, 1217.88, 1083.81, 1220.72),
                          (1079.27, 1215.05, 1080.40, 1217.88), (1144.18, 1215.05, 1145.32, 1217.88)]},
    "giro": {"contorno": 0.6,
             # porta, folha do PDF (pt), faixa do traço do motor (px, como em espelhar_faixa: ao longo do traço, de a0
             # a a1, e através dele, de b0 a bm do lado de antes e de bm a b1 do de depois; exclusivos) e se o traço é
             # em pé (a faixa vai na transposta); o depósito tem o bloco (px: x0, y0, x1, y1), que recebe o piso de cima
             "folhas": [("do banho de serviço", (969.57, 1208.81, 1009.25, 1211.08), (590, 620, 537, 537, 539), False),
                        ("do depósito", (1156.66, 1197.33, 1207.68, 1199.60), (701, 735, 529, 535, 535), False),
                        ("da sauna", (1196.34, 1710.54, 1236.03, 1712.81), (723, 743, 811, 812, 813), False),
                        ("do banho feminino", (1301.22, 1664.62, 1303.49, 1715.65), (786, 813, 779, 781, 782), True),
                        ("do banho masculino", (1644.78, 1664.62, 1647.05, 1715.65), (786, 813, 968, 970, 971), True)]},
    "janela": (1156.66, 1213.91, 1224.69, 1219.58),
    "sauna": (626, 782, 692, 786),                # px: x0, y0, x1, y1 (exclusivos) do vidro de cima, entre os caixilhos
    "montante": (652, 660)}                       # px: colunas das duas marcas, fora da mediana


def vidro_fino(tl, r, borda=None):
    """Folha de vidro do PDF como as portas da academia: clara, com a linha do meio no comprido e a borda fina."""
    pa = PORTAS_ACADEMIA
    m = tl.ret(r)
    tl.pintar(m, pa["vidro"])
    if r[2] - r[0] > r[3] - r[1]:
        ym = (r[1] + r[3]) / 2
        tl.pintar(m & tl.ret((r[0], ym - 0.25, r[2], ym + 0.25)), pa["meio"][0])
    else:
        xm = (r[0] + r[2]) / 2
        tl.pintar(m & tl.ret((xm - 0.25, r[1], xm + 0.25, r[3])), pa["meio"][0])
    tl.contorno(m, borda or pa["borda"][1], pa["borda"][0])


def espelhar_faixa(out, a0, a1, b0, bm, b1):
    """Apaga um traço horizontal: nas colunas a0..a1, as linhas b0..bm recebem o piso de cima em espelho e as
    linhas bm..b1, o de baixo (exclusivos). Na transposta, um traço em pé."""
    out[b0:bm, a0:a1] = out[2 * b0 - bm:b0, a0:a1][::-1]
    out[bm:b1, a0:a1] = out[b1:2 * b1 - bm, a0:a1][::-1]
    return (a1 - a0) * (b1 - b0)


def vidros_subsolo(out):
    from retoque_subsolo_casae import Tela, PORTA
    q, pa = VIDROS_SUB, PORTAS_ACADEMIA
    _, p2r = pdf_pavimento("Subsolo")
    c = q["correr"]
    n = espelhar_faixa(out, *c["faixa"])
    tl = Tela(out, p2r, [f(v) for f, v in zip((min, min, max, max), zip(*(c["folhas"] + c["pontas"])))])
    for r in c["pontas"]:
        m = tl.ret(r)
        tl.pintar(m, pa["aluminio"])
        tl.contorno(m, pa["borda"][1], pa["borda"][0])
    for r in c["folhas"]:
        vidro_fino(tl, r, c["borda"])
    out = tl.gravar()
    print(f"    porta de correr da circulação: traço preto apagado ({n} px, o Bege Bahia de cada "
          f"lado), 2 folhas de vidro desencontradas e 4 pontas do PDF")
    g = q["giro"]
    for nome, f, faixa, em_pe in g["folhas"]:
        n = espelhar_faixa(out.transpose(1, 0, 2) if em_pe else out, *faixa)
        tl = Tela(out, p2r, f)
        m = tl.ret(f)
        tl.pintar(m, PORTA["folha"])
        tl.contorno(m, g["contorno"], PORTA["contorno"])
        out = tl.gravar()
        print(f"    porta {nome}: {'bloco cinza' if 'depósito' in nome else 'traço escuro'} fora ({n} px) e a folha do "
              f"PDF, branca e fina")
    tl = Tela(out, p2r, q["janela"])
    vidro_fino(tl, q["janela"])
    out = tl.gravar()
    print("    janela entre o depósito e a academia: o vão do PDF em vidro claro")
    x0, y0, x1, y1 = q["sauna"]
    a, b = q["montante"]
    trecho = np.concatenate([out[y0:y1, x0:a], out[y0:y1, b:x1]], axis=1).astype(np.float32)
    out[y0:y1, x0:x1] = np.round(np.median(trecho, axis=1))[:, None].astype(np.uint8)
    print(f"    vidro de cima da sauna: folha contínua, sem o montante (x {x0} a {x1 - 1}, y {y0} a {y1 - 1} px)")
    return out


# Pente fino pelas regras (21/10/26), Subsolo, item 6: Bege Bahia como a referência (seção 18). A circulação externa, a
# interna e o depósito estavam no Bege Bahia do 1º Pavimento (item 11 de 19/10), rosados, com veios grandes, fora de
# escala. Entram o desenho da biblioteca (`_texturas`, na escala do render) e o tom da foto (RGB 230, 211, 186), com a
# luz do lugar, pela rotina do item 9 do Térreo (bege_na_referencia: as constantes de retoque_terreo_casae.BEGE, as do
# Subsolo da Casa E; os pontinhos escuros do motor saem antes, e o anel em volta do que foge da luz vai ao piso novo
# depois; sem isso, os pontinhos ficavam no rosado antigo, cinza no tom novo). A máscara é a do item 11
# (bege_mascaras), sem o verde do gramado junto à borda da circulação externa (com 1 px de folga). A borda de 1 a 2 px
# da máscara, que retexturizar não troca (junto às paredes, ao vidro da sauna e ao gramado), vai ao piso novo de perto,
# só onde é claramente piso (as quinas meio parede ficam). Roda antes do item 5: as folhas e a porta de correr entram
# por cima, e os trechos espelhados dele já vêm do piso novo.
BEGE_SUB = {"verde": (4, 12), "folga_verde": 3,    # G acima de R e de B (como em bege_referencia_a); dilatação (px)
            "borda": {"claro": 170, "sig": 1.5, "peso": 0.15}}   # piso claro; raio e peso mínimo do piso novo perto


def bege_subsolo(out):
    q = BEGE_SUB
    m = np.zeros(out.shape[:2], bool)
    for _, (x0, y0, x1, y1), _, mm in bege_mascaras(out):
        m[y0:y1, x0:x1] |= mm
    im = out.astype(np.int32)
    verde = (im[..., 1] > im[..., 2] + q["verde"][0]) & (im[..., 1] > im[..., 0] + q["verde"][1])
    k = q["folga_verde"]
    m &= ~cv2.dilate(verde.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    _, p2r = pdf_pavimento("Subsolo")
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                  # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d - b))
    from texturas_escala import nconv
    antes = out
    out, npt, npx, nanel = bege_na_referencia(out, m, px_m)
    b = q["borda"]
    novo = (out != antes).any(axis=2) & m
    resto = m & ~novo & (antes.astype(np.float32).mean(axis=2) >= b["claro"])
    resto &= cv2.GaussianBlur(novo.astype(np.float32), (0, 0), b["sig"]) >= b["peso"]
    out[resto] = np.clip(nconv(out.astype(np.float32), novo.astype(np.float32), b["sig"])[resto], 0, 255).astype(np.uint8)
    print(f"    Bege Bahia da circulação externa, da interna e do depósito: {npt} px de pontinhos escuros fora; {npx} px "
          f"no desenho da biblioteca, a {px_m:.2f} px/m, no tom da foto; {nanel} px do anel em volta dos objetos e "
          f"{int(resto.sum())} px da borda")
    return out


# Pente fino pelas regras (21/10/26), Subsolo, item 7: travertino na escala (R1 e seção 18). No hall, os veios do motor
# estavam na vertical, com riscos escuros; na sauna, na antessala e nos banhos, em faixas largas. Entra o travertino
# aprovado do Térreo da Casa A (veio horizontal, sem rejuntes), na mesma escala (os dois pavimentos estão no mesmo
# quadro: 31,1 e 31,5 px/m), como o Subsolo da Casa E (retoque_subsolo_casae.texturas_na_escala): trechos limpos do
# Térreo com os ajustes (a circulação junto ao jardim e a passagem abaixo do escritório), tecidos por image quilting
# com os espelhos que mantêm o veio na horizontal, e o desenho inteiro deles entra (força 1,4) sobre a luz do lugar
# (raio de 1 m, que tira o desenho antigo). A máscara é o travertino da base de entrega do Subsolo (#DCD9CA), nas
# manchas do hall, da sauna com a antessala e dos dois banhos (o pátio, da mesma cor na base, é Bege Bahia desde o
# item 11 de 19/10), sem as portas de vidro entre a academia e o hall. Os traços finos da base (os arcos e as folhas
# das portas do PDF, 1 a 2 px) são fechados (3 x 3), e entra a faixa da sauna junto ao vidro da esquerda, que na base
# ficou na cor do pátio (#E4E4E4); no render, a sauna é toda travertino.
# Os objetos saem da máscara pelo PDF, e não pela luz: com o critério de retexturizar (fugir da luz do lugar), os
# riscos escuros do motor também ficavam, e o piso saía em retalhos. Saem: os traços e as peças da ARQ_LOUÇAS E METAIS
# e da ARQ_BANCADAS (cubas, vasos, chuveiros, ralos), com o que eles fecham; a divisória dos banhos (item 10); o branco
# das louças do render que toca as louças do PDF (a borda de cima dos vasos passa 1 a 2 px do PDF; os pontos claros do
# tampo do banco ficam fora); tudo com 1 px de folga. A borda de 1 a 2 px que fica no desenho antigo (junto às paredes
# e aos objetos) vai ao piso novo de perto, como no item 6. Os vidros dos boxes (item 9) e a borda do banco da sauna
# (item 2) não ficam protegidos: guardavam, na faixa deles, a sombra antiga junto às paredes, que lia como um risco
# escuro. O piso troca por baixo, e os dois são redesenhados por cima, com as mesmas rotinas (vidro_box e
# banco_sauna). Roda antes do item 5 (as folhas das portas entram por cima).
TRAV_SUB = {"cor_base": (0xCA, 0xD9, 0xDC), "tol": 6, "x_min": 620, "area_min": 1000,
            "fora": [(972, 545, 982, 628)],                       # px: as portas de vidro da academia para o hall
            "fechar": 3, "incluir": [(625, 786, 645, 827)],       # px: a faixa da sauna junto ao vidro da esquerda
            "fonte": CASA / "renders/POE642_CasaA_PH_Terreo_final_bege_barlavento_ajustes.png",
            "trechos": [(1142, 318, 1174, 488), (1188, 358, 1288, 430)],   # px do Térreo com os ajustes
            "forca": 1.4, "sig_m": 1.0, "p": 24, "sobra": 8, "candidatos": 400, "semente": 654,
            "camadas": ["ARQ_LOUÇAS E METAIS", "ARQ_BANCADAS"], "fechado_max": 600,   # px: o que os traços fecham
            # pt: os vidros dos boxes na ARQ_LOUÇAS E METAIS (da ducha, com o tracejado que segue até a parede, e do
            # banho feminino), redesenhados depois
            "redesenhados": [(1190.0, 1717.0, 1275.0, 1725.0), (1430.0, 1660.0, 1439.0, 1740.0)],
            "branco": 228, "branco_min": 40, "folga": 1, "borda": {"sig": 1.5, "peso": 0.15}}


def travertino_subsolo(out):
    from retoque_bege_bahia_terreo import quilting
    from texturas_escala import retexturizar
    q = TRAV_SUB
    bb = base_terreo(out.shape[:2], "Subsolo").astype(np.int32)
    trav = (np.abs(bb - np.array(q["cor_base"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(trav, 8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]
                      and st[i, cv2.CC_STAT_LEFT] >= q["x_min"]])
    k = q["fechar"]
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)).astype(bool)
    for x0, y0, x1, y1 in q["incluir"]:
        m[y0:y1, x0:x1] = True
    for x0, y0, x1, y1 in q["fora"]:
        m[y0:y1, x0:x1] = False
    pg, p2r = pdf_pavimento("Subsolo")
    ss = 4
    obj = np.zeros((out.shape[0] * ss, out.shape[1] * ss), np.uint8)
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") in q["camadas"] and not any(r.x0 >= a and r.y0 >= b and r.x1 <= c and r.y1 <= e
                                                      for a, b, c, e in q["redesenhados"]):
            for c in caminhos_pdf(d, p2r):
                pts = np.int32(np.round(c * ss))
                if d["type"] == "f":
                    cv2.fillPoly(obj, [pts], 255)
                else:
                    cv2.polylines(obj, [pts], False, 255, ss)
    r = DIVISORIA["caixa"]
    (x0, y0), (x1, y1) = p2r(r[0], r[1]), p2r(r[2], r[3])
    cv2.rectangle(obj, (int(x0 * ss), int(y0 * ss)), (int(np.ceil(x1 * ss)), int(np.ceil(y1 * ss))), 255, -1)
    obj = cv2.resize(obj, out.shape[1::-1], interpolation=cv2.INTER_AREA) > 0
    louca = obj.copy()
    n, lab, st, _ = cv2.connectedComponentsWithStats((~obj).astype(np.uint8), 4)   # o que os traços fecham
    obj |= np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= q["fechado_max"]])
    n, lab, st, _ = cv2.connectedComponentsWithStats((out.astype(np.float32).mean(axis=2) >= q["branco"]).astype(np.uint8))
    perto = cv2.dilate(louca.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    obj |= np.isin(lab, [i for i in np.unique(lab[perto]) if i and st[i, cv2.CC_STAT_AREA] >= q["branco_min"]])
    k = 2 * q["folga"] + 1
    obj = cv2.dilate(obj.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    m &= ~obj
    terreo = cv2.imread(str(q["fonte"])).astype(np.float32)
    fontes = [terreo[y0:y1, x0:x1] for x0, y0, x1, y1 in q["trechos"]]
    fontes += [f[:, ::-1] for f in fontes] + [f[::-1] for f in fontes]     # espelhos: o veio fica na horizontal

    def do_terreo(h, w):
        return quilting(fontes, h, w, p=q["p"], sobra=q["sobra"], candidatos=q["candidatos"],
                        rng=np.random.default_rng(q["semente"]))[:h, :w]
    from texturas_escala import nconv
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    antes = out
    out, npx = retexturizar(out, m, "travertino", px_m, forca=q["forca"], sig_m=q["sig_m"], pronta=do_terreo,
                            fugir=False)
    b = q["borda"]
    novo = (out != antes).any(axis=2) & m
    resto = m & ~novo & (cv2.GaussianBlur(novo.astype(np.float32), (0, 0), b["sig"]) >= b["peso"])
    out[resto] = np.clip(nconv(out.astype(np.float32), novo.astype(np.float32), b["sig"])[resto], 0, 255).astype(np.uint8)
    print(f"    travertino do hall, da sauna com a antessala e dos banhos: {npx} px no travertino do Térreo, "
          f"a {px_m:.2f} px/m, e {int(resto.sum())} px da borda; os objetos ficam; por cima, de novo:")
    from retoque_subsolo_casae import vidro_box
    for f in [f for b in BOXES for f in b["folhas"]]:
        out = vidro_box(out, p2r, f)
    print(f"    os {sum(len(b['folhas']) for b in BOXES)} vidros dos boxes (item 9)")
    return banco_sauna(out)


# Pente fino pelas regras (21/10/26), Subsolo, item 8: shafts e projeções (R8), da DOC_LINHAS E PROJEÇÕES do PDF, como
# as projeções do 1º Pavimento da Casa E (retoque_1pav_casae.projecoes_1pav).
# - Os dois shafts junto ao elevador (o de cima, largo, e o da direita, estreito): o motor os encheu, de marrom e de
#   cinza, com o X contínuo. O vão fica branco (o que não é parede preta, no retângulo de dentro do PDF arredondado
#   para dentro: a borda escura do render junto à parede também clareia, e a parede não ganha dente branco), e o X
#   entra tracejado, nos traços do próprio PDF, em cinza médio, só no branco. O elevador fica como está.
# - Os três retângulos que o motor não desenhou (usuário, 21/10/26: confirmado, "em traço cinza fino, como no PDF"):
#   junto às paredes de cima e da direita do depósito (0,5 e 0,7 m de fundo) e junto à parede de baixo da academia
#   (3,5 x 0,4 m). Traço contínuo, como no PDF: cinza médio no Bege Bahia do depósito e cinza claro na madeira da
#   academia (o cinza médio sumia nela, como na rouparia da Casa E). Nas paredes pretas, o traço some.
PROJECOES_SUB = {"camada": "DOC_LINHAS E PROJEÇÕES", "branco": 250, "escuro": 30,
                 "vaos": [(2021.2, 1230.9, 2143.1, 1276.3), (2114.8, 1287.6, 2143.1, 1372.7)],   # pt: os dois shafts
                 # caixa (pt), cor e se o traço fica só no vão branco
                 "grupos": [((2020.5, 1230.0, 2144.0, 1277.0), (147, 147, 147), True),     # shaft de cima
                            ((2114.0, 1287.0, 2144.0, 1373.5), (147, 147, 147), True),     # shaft da direita
                            ((1156.0, 1060.0, 1656.5, 1220.5), (150, 150, 150), False),    # depósito: cima e direita
                            ((1377.0, 1627.0, 1577.0, 1651.0), (226, 226, 226), False)],   # academia: embaixo
                 "largura": 0.6, "forca": 0.85, "parede": 40}


def projecoes_subsolo(out):
    import pymupdf
    q = PROJECOES_SUB
    pg, p2r = pdf_pavimento("Subsolo")
    im = out.astype(np.float32)
    branco = np.zeros(out.shape[:2], bool)
    for v in q["vaos"]:
        (a, b), (c, d) = p2r(*v[:2]), p2r(*v[2:])
        x0, y0, x1, y1 = int(np.ceil(a)), int(np.ceil(b)), int(np.floor(c)), int(np.floor(d))
        branco[y0:y1, x0:x1] = im[y0:y1, x0:x1].mean(axis=2) > q["escuro"]
    im[branco] = q["branco"]
    tracos = [dd for dd in pg.get_drawings() if dd.get("layer") == q["camada"]]
    n = 0
    for caixa, cor, no_vao in q["grupos"]:
        cx = pymupdf.Rect(*caixa)
        segs = [(p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)) for dd in tracos if dd["rect"] in cx
                for it in dd["items"] if it[0] == "l"]
        pts = np.array([pt for sg in segs for pt in sg])
        X0, Y0 = np.floor(pts.min(axis=0)).astype(int) - 3
        X1, Y1 = np.ceil(pts.max(axis=0)).astype(int) + 4
        h, w = Y1 - Y0, X1 - X0
        f = np.zeros((h * SS_E, w * SS_E), np.uint8)
        for (ax, ay), (bx, by) in segs:
            cv2.line(f, (int(round((ax - X0) * SS_E)), int(round((ay - Y0) * SS_E))),
                     (int(round((bx - X0) * SS_E)), int(round((by - Y0) * SS_E))), 255,
                     max(1, int(round(q["largura"] * SS_E))), cv2.LINE_AA)
        al = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * q["forca"]
        reg = im[Y0:Y1, X0:X1]
        al *= branco[Y0:Y1, X0:X1] if no_vao else reg.mean(axis=2) >= q["parede"]
        im[Y0:Y1, X0:X1] = reg * (1 - al[..., None]) + np.float32(cor) * al[..., None]
        n += len(segs)
    print(f"    projeções: os vãos dos dois shafts em branco ({int(branco.sum())} px) e {n} traços do PDF em {len(q['grupos'])} grupos "
          f"(o X tracejado dos shafts e os retângulos do depósito e da academia)")
    return np.clip(im, 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), Subsolo, item 9: soleiras (R13), porta a porta no PDF (o vão na espessura da
# parede: branco, entre os batentes, é soleira; com o piso de um dos lados atravessando, não). Sem soleira, como já
# estavam: o banho de serviço (o Barlavento entra no vão), o depósito e a porta de correr da circulação (o piso da
# circulação), a sauna (o travertino), os banhos feminino e masculino (a madeira da academia e o travertino se encontram
# no vão) e a academia para a circulação (o piso da circulação até a madeira). Com soleira (o vão branco no PDF):
# - academia para o hall: o vão inteiro (de 1655,55 a 1666,89 pt), com as duas folhas de vidro de correr por cima; o
#   render tinha uma faixa clara lisa entre a madeira e as folhas. As folhas e os batentes (item 4 de 19/10) ficam;
# - elevador: o vão entre o hall e a cabine (de 2012,72 a 2021,22 pt); o render tinha o travertino antigo.
# Desenho das soleiras do Térreo (item 16, desenhar_soleiras): Bege Bahia na escala, no tom da referência, com as faces
# da parede em cinza fino.
SOLEIRAS_SUB = {"pdf": [(1655.55, 1232.34, 1666.89, 1371.24),     # academia para o hall
                        (2012.72, 1311.71, 2021.22, 1348.56)],    # elevador
                "fora": [f for lado in PORTAS_ACADEMIA["lados"] if lado["nome"] == "do hall"
                         for f in lado["folhas"] + lado["batentes"]],
                "forca": 0.5, "linha": (150, 152, 154), "linha_px": 0.4, "ss": 8, "semente": 7}


def soleiras_subsolo(out):
    out = desenhar_soleiras(out, "Subsolo", SOLEIRAS_SUB)
    print("    2 soleiras de Bege Bahia nos vãos brancos do PDF (academia para o hall, com as folhas de vidro por cima, e "
          "elevador), com as faces da parede em cinza fino; nas outras 8 portas o piso atravessa o vão")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 1: o Térreo nublado em volta (seção 11: 70% de branco, 80% da
# saturação, desfoque leve, com a final do Térreo depois do pente fino; o 1º Pavimento por cima, integralmente). Hoje o
# entorno é o do motor, quase apagado. A pegada do pavimento sai do próprio render aprovado, como em
# `entorno_esmaecido.pegada`: o que tem cor cheia (algum canal abaixo de 215; o contexto do motor, o deck, a piscina e os
# pisantes, está quase branco), em manchas grandes, fechado (9 x 9) e com os furos preenchidos (os vazios com o X, a
# escada), aberto (5 x 5). O PDF do 1º Pavimento não serve: traz o Térreo nas mesmas camadas. Fora da pegada, branco
# no ajuste; a máscara vai a `renders/POE642_CasaA_PH_1Pavimento_pegada_mascara.png`, e na final (`rotulos_casaa.py`,
# chave `nublado`) o Térreo final, sem rótulos, entra nublado fora dela. Roda por último.
PEGADA_1PAV = {"claro": 215, "mancha_min": 5000, "fechar": 9, "abrir": 5,
               "mascara": CASA / "renders/POE642_CasaA_PH_1Pavimento_pegada_mascara.png"}


def so_1pavimento(out):
    from scipy import ndimage
    q = PEGADA_1PAV
    ap = cv2.imread(str(APROVADAS["1Pavimento"]))
    nb = (ap.min(axis=2) < q["claro"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb, connectivity=8)
    grandes = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > q["mancha_min"]]).astype(np.uint8)
    peg = ndimage.binary_fill_holes(cv2.morphologyEx(grandes, cv2.MORPH_CLOSE, np.ones((q["fechar"],) * 2, np.uint8)))
    peg = cv2.morphologyEx(peg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((q["abrir"],) * 2, np.uint8)) > 0
    cv2.imwrite(str(q["mascara"]), (peg * 255).astype(np.uint8))
    fora = ~peg & (out.min(axis=2) < 255)
    out[~peg] = 255
    print(f"    pegada do 1º Pavimento: {100 * peg.mean():.1f}% da imagem; {int(fora.sum())} px do contexto do motor "
          f"viram branco (o Térreo nublado entra na final); máscara em {q['mascara'].name}")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 2: portas sem arcos (R3). Os 11 arcos do PDF (as curvas da
# ARQ_PAREDE) estão no render como traços escuros de 1 px; saem como os do Subsolo (item 4, sem_arcos_pdf: o traço numa
# faixa de 4 px, refeito por inpaint de raio 2, com o vinílico e o Bege Bahia continuando por cima), com três cuidados:
# - o inpaint não puxa a parede (o preto do batente virava mancha no banho 3), as linhas retas do desenho que o arco
#   cruza ou toca (o escuro em fio de 15 px ou mais: a borda da bancada do banho 2, as folhas) nem, na faixa de cada
#   arco, o piso 30 mais claro que o dele (a circulação clara entrava como um dente no vinílico da suíte);
# - alguns arcos do render passam 2 a 3 px para dentro do arco do PDF (o do banho 3 ficava como um arco claro): uma
#   segunda passada, numa faixa de 9 px, refaz o que ainda é mais escuro que o piso em volta (8 abaixo da mediana de
#   9 px), a mais de 2 px dos batentes do PDF e de 1 px das paredes;
# - junto às folhas do PDF (os brancos de 12 px ou mais, 3 vezes mais compridos que largos), a até 4 px (as folhas do
#   render também passam até 3 px do PDF), fica só a linha da folha (o escuro em fio de 7 px no sentido dela); sai o
#   toco do arco que chega à ponta (2 a 3 px de largura, em pé numa folha deitada).
# As folhas, já finas e com o contorno, e os batentes ficam.
SEM_ARCOS_1PAV = {"faixa": 9, "escuro": 8, "parede": 60, "folga_folha": 4, "folga_batente": 2, "folga_parede": 1,
                  "folha_comprida": 3, "folha_min": 12, "linha_folha": 7, "fio": 15,
                  "outro_piso": 30}


def sem_arcos_1pav(out):
    return sem_arcos_pdf(out, "1Pavimento", SEM_ARCOS_1PAV)


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 3: a escada em U (R14 e seção 5). No PDF do 1º Pavimento ela
# desce daqui (o "D", junto ao degrau 20, que é o piso da circulação), inteira e sem linha de corte: o lance de baixo
# desce da esquerda para a direita (degraus 19 a 11), o patamar (10) e o lance de cima volta da direita para a
# esquerda (9 a 1) até o Térreo. O motor fez os bocéis, a linha de percurso com a volta no patamar e as pontas de seta
# em traço cinza-escuro. Entra o que o Térreo tem na mesma escada (ESCADA_INT): o travertino dos degraus, tecido do
# trecho limpo do hall do Térreo aprovado, na cor dos degraus; em cada bocel, a linha suave e a sombra curta no degrau
# de baixo (R14, o mesmo das escadas do Térreo); o bocel do degrau 11 faz sombra no patamar, e o degrau 1 do lance de
# cima, junto ao guarda-corpo, fica sem linha. O triângulo no degrau 19 (o topo), apontando para a descida (para a
# direita). O contorno da escada e o vão entre os lances ficam; a ponta de seta e o "D" do motor, junto ao
# guarda-corpo, saem.
ESCADA_U_1PAV = {"lanco1": (2021.22, 1094.86, 2174.3, 1162.89), "lanco2": (2019.52, 1185.57, 2174.3, 1253.6),
                 "patamar": (2174.3, 1094.86, 2242.33, 1253.6),                  # pt
                 "bocels": [2038.23, 2055.24, 2072.25, 2089.26, 2106.26, 2123.27, 2140.28, 2157.29, 2174.3],
                 "marcas": [(2021.22, 1128.87), (2019.52, 1219.58)],             # pt: a seta e o "D" do percurso
                 "marca_r_px": 3.5, "marca_escuro": 20, "fio_px": 15,
                 "contorno": ((132, 138, 147), 0.9)}     # BGR e largura (px): o cinza do contorno do render, limpo


def escada_u_1pav(out):
    from retoque_bege_bahia_terreo import quilting
    q, qt = ESCADA_U_1PAV, ESCADA_INT
    _, p2r = pdf_pavimento("1Pavimento")
    (a, b), (c, d) = p2r(q["lanco2"][0] - 6, q["lanco1"][1] - 6), p2r(q["patamar"][2] + 6, q["lanco2"][3] + 6)
    X0, Y0, X1, Y1 = int(a), int(b), int(c) + 1, int(d) + 1
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    h, w = reg.shape[:2]
    kpt = (p2r(q["lanco1"][0] + 100, q["lanco1"][1])[0] - p2r(*q["lanco1"][:2])[0]) / 100      # px por pt

    def local(x, y):
        u, v = p2r(x, y)
        return u - X0, v - Y0

    def ret(x0, y0, x1, y1):
        return r14_poligono((h, w), [local(x0, y0), local(x1, y0), local(x1, y1), local(x0, y1)])
    escada = np.maximum.reduce([ret(*q[k]) for k in ("lanco1", "lanco2", "patamar")])
    # o travertino da escada do Térreo: o mesmo trecho, o mesmo tecido e a mesma cor
    fx0, fy0, fx1, fy1 = qt["fonte_piso"]
    f = cv2.imread(str(APROVADAS["Terreo"]))[fy0:fy1, fx0:fx1].astype(np.float32)
    f = f / cv2.GaussianBlur(f, (0, 0), 8)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    piso = quilting(fontes, h, w, p=24, sobra=8, candidatos=300, rng=np.random.default_rng(651))[:h, :w]
    piso = piso * np.float32(qt["piso"])
    # cada bocel: a linha suave e a sombra curta no degrau de baixo (+1: à direita; -1: à esquerda)
    fator = np.ones((h, w), np.float32)
    forca, alcance = R14["sombra"]
    _, a1, _, b1 = q["lanco1"]
    x2, a2, _, b2 = q["lanco2"]
    for xs, ya, yb, sinal in (([x2] + q["bocels"], a2, b2, 1), (q["bocels"], a1, b1, -1)):
        for xb in xs:
            meia = R14["bocel_pt"] / 2
            fator *= 1 - (1 - R14["bocel"]) * ret(xb - meia, ya, xb + meia, yb)
            for t in np.linspace(0, 1, 9)[:-1]:
                fa, fb = xb + sinal * alcance * t, xb + sinal * alcance * (t + 1 / 8)
                fator *= 1 - forca * (1 - t - 1 / 16) ** 1.6 * ret(min(fa, fb), ya, max(fa, fb), yb)
    # a ponta de seta e o "D" do motor que sobram fora da escada, junto ao guarda-corpo, saem antes; o guarda-corpo (o
    # escuro em fio vertical) fica e não serve de fonte (a ponta de seta está sobre ele)
    L = reg.mean(axis=2)
    med = cv2.medianBlur(np.clip(L, 0, 255).astype(np.uint8), 9).astype(np.float32)
    escuro = L < med - q["marca_escuro"]
    guarda = cv2.morphologyEx(escuro.astype(np.uint8), cv2.MORPH_OPEN, np.ones((q["fio_px"], 1), np.uint8)) > 0
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    perto = np.zeros((h, w), bool)
    for x, y in q["marcas"]:
        u, v = local(x, y)
        perto |= np.hypot(xx - u, yy - v) <= q["marca_r_px"]
    marca = perto & (escada < 0.99) & escuro & ~guarda
    reg = inpaint_sem_parede(reg.astype(np.uint8), marca, 2, guarda).astype(np.float32)
    reg = reg * (1 - escada[..., None]) + piso * fator[..., None] * escada[..., None]
    # o contorno da escada e do vão entre os lances, limpo, no cinza do contorno do render
    x1, _, x3, _ = q["patamar"][0], 0, q["patamar"][2], 0
    cor, larg = q["contorno"]
    cont = np.zeros((h, w), np.float32)
    for pts in ([(q["lanco1"][0], a1), (x3, a1), (x3, b2), (x2, b2)],
                [(q["lanco1"][0], b1), (x1, b1), (x1, a2), (x2, a2)]):
        cont = np.maximum(cont, r14_linha((h, w), [local(*p) for p in pts], larg))
    reg = reg * (1 - cont[..., None]) + np.float32(cor) * cont[..., None]
    # o triângulo no degrau 19, a 10 cm do início, apontando para a descida
    base = local(x2 + R14["triangulo"]["recuo_pt"], (a2 + b2) / 2)
    tri = r14_triangulo((h, w), base, (1.0, 0.0), kpt)
    reg = reg * (1 - tri[..., None]) + np.float32(R14["triangulo"]["cor"]) * tri[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    escada em U: travertino do Térreo, {len(q['bocels']) * 2} bocéis com a linha suave e a sombra curta; "
          f"triângulo no degrau 19, para a descida; {int(marca.sum())} px da seta e do \"D\" do motor fora")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 3: a caracol da saleta (R14 e seção 5: "na caracol, só o
# trecho do pavimento fica cheio"). No PDF do 1º Pavimento, o "D" e a seta ficam no degrau junto ao 0° (à direita do
# pilar), apontando para baixo: desce no sentido horário. O render já tem o trecho cheio (o quarto de 0,6° a 93,1°, em
# madeira, cinco degraus) e o resto branco, com os raios do motor (cheios até 130°, tracejados depois), a linha de
# percurso e o símbolo do corte. Entra:
# - no trecho cheio: os riscos escuros do motor saem (a madeira por cima, por inpaint) e, em cada bocel (os raios do
#   PDF a 19,1°, 37,6°, 56,1° e 74,6°), a linha suave e a sombra curta no degrau de baixo (o do sentido horário), com
#   os números da escada em U (R14: 0,16 em 10 cm); o triângulo no degrau do "D", a 70% e a 38 pt do centro, como na
#   caracol do Térreo (o da regra não cabe no degrau de 18,5°), apontando para a descida;
# - no resto: o branco limpo (sem a linha de percurso e sem o corte: "a linha de corte não é desenhada") e os bocéis
#   tracejados (a projeção), nos raios do PDF, no cinza e no traço da R14.
# As guardas (a 0° e a 93,1°), o anel do corrimão, o pilar e o contorno do trecho cheio ficam.
CARACOL_1PAV = {"centro": (1756.4, 1718.5), "r_pilar": 4.0, "r_cheio": 55.5, "r_vazio": 51.3,      # pt
                "cheio": [0.6, 19.1, 37.6, 56.1, 74.6, 93.1],             # graus: as bordas dos degraus cheios
                "tracejados": [111.6, 129.7, 147.6, 164.9, 182.6, 200.4, 218.4, 236.0, 253.5, 270.9, 288.4, 305.9,
                               323.4, 341.4],                                # graus: os bocéis do resto, do PDF
                "guarda_px": 1.8, "escuro": 8, "branco": (250, 250, 250),
                "triangulo_r_pt": 38.0, "triangulo_escala": 0.7}


def caracol_1pav(out):
    q = CARACOL_1PAV
    _, p2r = pdf_pavimento("1Pavimento")
    cx, cy = p2r(*q["centro"])
    k = (p2r(q["centro"][0] + 100, q["centro"][1])[0] - cx) / 100                 # px por pt
    rn, Rc, Rv = q["r_pilar"] * k, q["r_cheio"] * k, q["r_vazio"] * k
    X0, Y0 = int(cx - Rc - 4), int(cy - Rc - 4)
    X1, Y1 = int(cx + Rc + 5), int(cy + Rc + 5)
    reg = out[Y0:Y1, X0:X1].copy()
    h, w = reg.shape[:2]
    ox, oy = cx - X0, cy - Y0
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    rr = np.hypot(xx - ox, yy - oy)
    th = np.degrees(np.arctan2(oy - yy, xx - ox)) % 360
    t0, t1 = q["cheio"][0], q["cheio"][-1]

    guardas = np.zeros((h, w), bool)                      # as duas semirretas (0° e 93,1°), fora do pilar
    for t in (0.0, t1):
        c, s = np.cos(np.radians(t)), np.sin(np.radians(t))
        guardas |= (np.abs((xx - ox) * s + (yy - oy) * c) < q["guarda_px"]) & ((xx - ox) * c - (yy - oy) * s > 0)
    guardas &= rr > rn
    # 1. o trecho cheio: os riscos escuros saem, a madeira por cima
    cheio = (th > t0) & (th < t1) & (rr > rn + 1) & (rr < Rc - 1) & ~guardas
    L = reg.astype(np.float32).mean(axis=2)
    med = cv2.medianBlur(np.clip(L, 0, 255).astype(np.uint8), 9).astype(np.float32)
    madeira = np.median(L[cheio & (L > np.percentile(L[cheio], 50))])
    riscos = cheio & (L < madeira - q["escuro"])
    reg = inpaint_sem_parede(reg, riscos, 2, guardas)
    # 2. o resto: o branco limpo, com os bocéis tracejados
    vazio = ~((th >= t0 - 1) & (th <= t1 + 1)) & (rr > rn + 1.5) & (rr < Rv) & ~guardas
    reg[vazio] = q["branco"]
    tr = np.zeros((h, w), np.float32)
    for t in q["tracejados"]:
        c, s = np.cos(np.radians(t)), -np.sin(np.radians(t))
        tr = np.maximum(tr, r14_tracejado((h, w), [(ox + c * (rn + 1), oy + s * (rn + 1)), (ox + c * Rv, oy + s * Rv)],
                                          k, R14["tracejado_px"]))
    tr *= vazio
    reg = reg.astype(np.float32)
    reg = reg * (1 - tr[..., None]) + np.float32(R14["tracejado"]) * tr[..., None]
    # 3. os bocéis do trecho cheio: a linha suave e a sombra curta no degrau de baixo (sentido horário)
    forca, alc = R14["sombra"]
    alc *= k
    fator = np.ones((h, w), np.float32)
    lb = np.zeros((h, w), np.float32)
    for t in q["cheio"][1:-1]:
        c, s = np.cos(np.radians(t)), -np.sin(np.radians(t))
        lb = np.maximum(lb, r14_linha((h, w), [(ox + c * rn, oy + s * rn), (ox + c * Rc, oy + s * Rc)],
                                      R14["bocel_pt"] * k))
        dist = (t - th) * np.pi / 180 * rr                  # px até o bocel, do lado horário
        fator *= np.where((dist >= 0) & (th > t0), 1 - forca * np.clip(1 - dist / alc, 0, 1) ** 1.6, 1)
    fator *= 1 - (1 - R14["bocel"]) * lb
    no_cheio = ((th > t0) & (th < t1) & (rr > rn) & (rr < Rc) & ~guardas).astype(np.float32)
    reg *= (1 - (1 - fator) * no_cheio)[..., None]
    # 4. o triângulo no degrau do "D", apontando para a descida (sentido horário: theta decrescente)
    a, b = q["cheio"][0], q["cheio"][1]
    rt, esc = q["triangulo_r_pt"] * k, q["triangulo_escala"]
    alt = R14["triangulo"]["altura_pt"] * k * esc
    tb = np.radians(b) - (np.radians(b - a) * rt - alt) / 2 / rt                     # a base, centrada no degrau
    tm = np.radians((a + b) / 2)
    tri = r14_triangulo((h, w), (ox + np.cos(tb) * rt, oy - np.sin(tb) * rt), (np.sin(tm), np.cos(tm)), k, esc)
    reg = reg * (1 - tri[..., None]) + np.float32(R14["triangulo"]["cor"]) * tri[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    caracol da saleta: {int(riscos.sum())} px de riscos fora do trecho cheio ({len(q['cheio']) - 1} degraus, "
          f"{len(q['cheio']) - 2} bocéis com a linha suave e a sombra curta); o resto em branco com "
          f"{len(q['tracejados'])} bocéis tracejados; triângulo no degrau do \"D\", para a descida")
    return out


def escadas_1pav(out):
    return caracol_1pav(escada_u_1pav(out))


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 4: guarda-roupas com cabides (R11) nos closets 3, 2, 1 e
# master. O motor fez armários de madeira com riscos. No PDF, cada guarda-roupa é um retângulo com a diagonal da
# DOC_LINHAS E PROJEÇÕES (os em L e o em U do closet master são dois e três trechos, o canto num deles). Cada trecho
# recebe o `_texturas/elementos.guarda_roupa` como no 1º Pavimento da Casa E (retoque_1pav_casae.guarda_roupas, item 5
# de 20/10): visto de cima, aberto, no tamanho do PDF, desenhado em 4x, com as portas do lado do closet; os tons da Casa
# E (usuário, 21/10: confirmado), bege dentro e ocre na borda, e o cabideiro de metal de lateral a lateral. Os
# retângulos com diagonal da circulação e do quarto de serviço são armários até o teto (item 5) e ficam fora.
GUARDA_ROUPAS_1PAV = {"pecas": [((1664.1, 579.0, 1698.1, 692.3), "direita"), ((1698.1, 579.0, 1825.6, 613.0), "baixo"),
                                # closet 3; closet 2
                                ((1598.9, 1072.2, 1729.3, 1106.2), "baixo"), ((1729.3, 1072.2, 1763.3, 1276.3), "esquerda"),
                                # closet master
                                ((1539.3, 1483.3, 1686.7, 1517.4), "baixo"), ((1652.7, 1517.4, 1686.7, 1775.2), "esquerda"),
                                ((1536.5, 1741.2, 1652.7, 1775.2), "cima"),
                                # closet 1
                                ((2021.2, 1381.2, 2055.2, 1483.2), "direita"), ((2055.2, 1381.2, 2174.3, 1415.2), "baixo")],
                      "ss": 4, "semente": 31}


def guarda_roupas_1pav(out):
    import sys
    sys.path.insert(0, str(CASA.parent / "_texturas"))
    from elementos import guarda_roupa
    from retoque_1pav_casae import GUARDA_ROUPAS
    q = GUARDA_ROUPAS_1PAV
    _, p2r = pdf_pavimento("1Pavimento")
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                  # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d - b))
    S = q["ss"]
    im = out.astype(np.float32)
    for i, ((x0, y0, x1, y1), lado) in enumerate(q["pecas"]):
        (u0, v0), (u1, v1) = p2r(x0, y0), p2r(x1, y1)
        comp, prof = max(x1 - x0, y1 - y0) / 56.69, min(x1 - x0, y1 - y0) / 56.69
        cor, alfa = guarda_roupa(comp, prof, px_m * S, semente=q["semente"] + i, miolo=GUARDA_ROUPAS["miolo"],
                                 moldura=GUARDA_ROUPAS["moldura"], barra=True)
        k = {"baixo": 0, "direita": 1, "cima": 2, "esquerda": 3}[lado]
        cor, alfa = np.ascontiguousarray(np.rot90(cor, k)), np.ascontiguousarray(np.rot90(alfa, k))
        X0, Y0, X1, Y1 = int(np.floor(u0)), int(np.floor(v0)), int(np.ceil(u1)), int(np.ceil(v1))
        tw, th = int(round((u1 - u0) * S)), int(round((v1 - v0) * S))
        ox, oy = int(round((u0 - X0) * S)), int(round((v0 - Y0) * S))
        grande = np.zeros(((Y1 - Y0) * S, (X1 - X0) * S, 3), np.float32)
        ag = np.zeros(grande.shape[:2], np.float32)
        grande[oy:oy + th, ox:ox + tw] = cv2.resize(cor, (tw, th), interpolation=cv2.INTER_AREA)
        ag[oy:oy + th, ox:ox + tw] = cv2.resize(alfa, (tw, th), interpolation=cv2.INTER_AREA)
        cr = cv2.resize(grande, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        ar = cv2.resize(ag, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
        im[Y0:Y1, X0:X1] = im[Y0:Y1, X0:X1] * (1 - ar) + cr
    print(f"    {len(q['pecas'])} trechos de guarda-roupa com cabides nos closets 3, 2, master e 1 (bege dentro, ocre "
          f"na borda, cabideiro de metal)")
    return np.clip(im, 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 5: armários até o teto (seção 7: "marcenaria areia com veio,
# sem a diagonal e sem sombra de móvel baixo"). No PDF do 1º Pavimento, os retângulos com diagonal da DOC_LINHAS E
# PROJEÇÕES que não são guarda-roupa são dois: o da circulação, sob o banho 3 (de parede a parede, até o guarda-corpo da
# escada), e o do quarto de serviço, junto à parede do banho de serviço. O motor fez o da circulação em bege liso, com
# a sombra de móvel baixo no vinílico, e o do quarto de serviço em madeira, com a diagonal. Entram como os do Térreo
# (item 6, armarios_ate_o_teto): a marcenaria areia aprovada com o veio no comprido, no retângulo do PDF, menos as
# paredes; a sombra do motor sai do piso nas faces livres; contorno fino nelas. Na sala íntima o PDF não tem retângulo
# com diagonal: o painel de madeira é o da TV (o retângulo branco do PDF, com a TV) e fica.
ARMARIOS_1PAV = {"pecas": [("circulação, sob o banho 3", (1811.5, 700.8, 2012.7, 729.2), ["baixo", "direita"]),
                           ("quarto de serviço", (1890.8, 1491.7, 1924.8, 1639.1), ["esquerda"])],
                 "pisos": [((1811.5, 700.8, 2012.7, 729.2), "baixo", (0, 0)),
                           ((1890.8, 1491.7, 1924.8, 1639.1), "esquerda", (0, 0))],
                 # a fonte, o contorno e os limites da sombra: os do Térreo (ARMARIOS_A)
                 "fonte": ("POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v4.png",
                           (1128, 740, 1143, 797)),
                 "contorno": (70, 72, 74), "larg_contorno": 0.4, "faixa": 14, "parede": 35, "traco": (0.45, 1.12)}


def armarios_1pav(out):
    return armarios_ate_o_teto(out, "1Pavimento", ARMARIOS_1PAV)


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 6: bancos ao pé das camas (itens 2 a 5 da conferência de
# 19/10; seção 8). O PDF (ARQ_LAYOUT HUMANIZAÇÃO) tem um banco no pé de cada cama de casal (suítes 3 e 2 e master; na 3
# o pé é embaixo, nas outras em cima) e um banquinho no pé de cada cama de solteiro da suíte 1; o motor não desenhou
# nenhum. Entram como os bancos do 1º Pavimento da Casa E (retoque_1pav_casae.bancos_camas, item 12): cada banco no pé
# da cama do render (a primeira queda de luz depois do edredom, na coluna do meio), a 1 px dela, na largura e na altura
# do PDF; estofado bege, com a almofada da Casa E (o assento do meio do sofá do render dela, normalizado, uma almofada a
# cada 1,7 vez a altura do banco), a trama fina, o contorno bege escuro e a sombra curta do banco do Térreo.
BANCOS_1PAV = {"bancos": [  # (banco, cama, o banco abaixo da cama?), em pt do PDF
    ("suíte 3", (1487.7, 678.7, 1578.5, 701.4), (1474.1, 551.7, 1592.1, 675.9), True),
    ("suíte 2", (1510.4, 1233.2, 1601.1, 1255.9), (1499.1, 1257.0, 1612.5, 1370.4), False),
    ("suíte master", (1263.8, 1457.1, 1354.5, 1479.8), (1250.2, 1482.6, 1368.1, 1606.8), False),
    ("suíte 1, cama da esquerda", (2073.9, 1584.1, 2125.0, 1601.1), (2071.1, 1604.0, 2127.8, 1717.3), False),
    ("suíte 1, cama da direita", (2173.2, 1584.1, 2224.2, 1601.1), (2170.3, 1604.0, 2227.0, 1717.3), False)],
    "almofada": ("POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_render.png", (1001, 633, 1034, 654))}


def bancos_1pav(out):
    from retoque_1pav_casae import BANCOS, sombra
    from retoque_terreo_casae import BANCO_VARANDA, colar, linha_aa, SS
    q, qe, bv = BANCOS_1PAV, BANCOS, BANCO_VARANDA
    _, p2r = pdf_pavimento("1Pavimento")
    arq, (fx0, fy0, fx1, fy1) = q["almofada"]
    almofada = cv2.imread(str(CASA.parent / arq))[fy0:fy1, fx0:fx1].astype(np.float32)
    almofada = 1 + qe["relevo"] * (almofada / almofada.reshape(-1, 3).mean(axis=0) - 1)
    L = out.astype(np.float32).mean(axis=2)
    forma = out.shape[:2]
    rng = np.random.default_rng(qe["semente"])
    for nome, B, cama, abaixo in q["bancos"]:
        (bx0, by0), (bx1, by1) = p2r(*B[:2]), p2r(*B[2:])
        alt = by1 - by0
        xc = int(round((bx0 + bx1) / 2))
        col = L[:, xc - 3:xc + 4].mean(axis=1)
        # pé da cama no render: a primeira queda depois do edredom (abaixo de 88% dele), no mínimo local logo depois
        passo = 1 if abaixo else -1
        ya = int(round(p2r(cama[0], cama[3] if abaixo else cama[1])[1])) - 4 * passo
        edredom = col[ya]
        y = ya
        while abs(y - ya) < qe["busca"] and col[y] > 0.88 * edredom:
            y += passo
        janela = [y + k * passo for k in range(4)]
        pe = janela[int(np.argmin([col[v] for v in janela]))]
        if abaixo:
            by0 = pe + qe["folga"]
            by1 = by0 + alt
        else:
            by1 = pe - qe["folga"] + 1
            by0 = by1 - alt
        ret = (bx0, by0, bx1, by1)
        x0, y0 = int(np.floor(bx0)) - 4, int(np.floor(by0)) - 4
        x1, y1 = int(np.ceil(bx1)) + 4, int(np.ceil(by1)) + 4
        m = np.zeros(((y1 - y0) * SS, (x1 - x0) * SS), np.uint8)
        cv2.rectangle(m, (int(round((bx0 - x0) * SS)), int(round((by0 - y0) * SS))),
                      (int(round((bx1 - x0) * SS)) - 1, int(round((by1 - y0) * SS)) - 1), 255, -1)
        mm = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        s = bv["sombra"]
        out = sombra(out, mm, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
        hh, ww = int(np.ceil(alt)) * SS, int(np.ceil(bx1 - bx0)) * SS
        secoes = max(1, int(round((bx1 - bx0) / (qe["proporcao"] * alt))))
        cortes = np.linspace(0, ww, secoes + 1).astype(int)
        peca = np.concatenate([cv2.resize(almofada, (int(b_ - a_), hh), interpolation=cv2.INTER_CUBIC)
                               for a_, b_ in zip(cortes[:-1], cortes[1:])], axis=1)
        amp, sig = qe["trama"]
        trama = cv2.GaussianBlur(rng.normal(0, 1, (hh, ww)).astype(np.float32), (0, 0), sig * SS)
        trama = 1 + amp * trama / max(trama.std(), 1e-6)
        peca = np.clip(peca * trama[..., None] * np.float32(qe["bege"]), 0, 255)
        peca = cv2.resize(peca, (ww // SS, hh // SS), interpolation=cv2.INTER_AREA)
        out = colar(out, peca, ret)
        a_ = linha_aa(forma, [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], qe["larg_contorno"],
                      fechada=True)[..., None]
        out[:] = np.clip(out * (1 - a_) + np.float32(qe["contorno"]) * a_, 0, 255).astype(np.uint8)
        print(f"    banco da {nome}: ({bx0:.1f}, {by0:.1f}) a ({bx1:.1f}, {by1:.1f}) px, {secoes} almofada(s); "
              f"pé da cama do render em {pe}")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 7: os criados-mudos da suíte 3 (item 1 da conferência de
# 19/10). No PDF são redondos, de 60 cm (os círculos brancos da ARQ_LAYOUT HUMANIZAÇÃO, junto à parede, dos dois lados
# da cama); o motor os fez quadrados, de ~45 cm, em madeira clara, com a sombra forte à esquerda e embaixo. O quadrado
# e a sombra saem (o vinílico por inpaint, sem puxar a parede preta nem a cama) e entram os círculos do PDF, na
# madeira do próprio quadrado (o miolo dele, ampliado), com o contorno na mesma madeira mais escura e a sombra curta
# do banco do Térreo (BANCO_VARANDA), a dos bancos do item 6.
CRIADOS_1PAV = {"pecas": [  # (círculo do PDF em pt, caixa a apagar em px, miolo do quadrado em px, piso limpo em px)
    ((1437.1, 553.3, 1471.1, 587.3), (861, 173, 884, 194), (867, 175, 879, 186), (855, 862)),
    ((1595.8, 553.3, 1629.8, 587.3), (951, 173, 972, 194), (955, 175, 967, 186), (971, 979))],
    "parede": 60, "contorno": (0.72, 0.45)}                       # contorno: fator da madeira e largura (px)


def criados_1pav(out):
    from retoque_1pav_casae import sombra
    from retoque_terreo_casae import BANCO_VARANDA, SS
    q = CRIADOS_1PAV
    _, p2r = pdf_pavimento("1Pavimento")
    s = BANCO_VARANDA["sombra"]
    for (cx0, cy0, cx1, cy1), (ax0, ay0, ax1, ay1), (mx0, my0, mx1, my1), (fx0, fx1) in q["pecas"]:
        madeira = out[my0:my1, mx0:mx1].astype(np.float32)
        # 1. o quadrado e a sombra saem: cada linha recebe o vinílico limpo da mesma linha, ao lado (as réguas correm
        # na horizontal), espelhado até cobrir; a parede (o preto de cima) fica
        fonte = out[ay0:ay1, fx0:fx1]
        fonte = np.concatenate([fonte, fonte[:, ::-1]] * ((ax1 - ax0) // (2 * fonte.shape[1]) + 1), axis=1)
        piso = fonte[:, :ax1 - ax0]
        reg = out[ay0:ay1, ax0:ax1]
        parede = reg.astype(np.float32).mean(axis=2) < q["parede"]
        reg[~parede] = piso[~parede]
        # 2. o criado-mudo redondo do PDF, com a sombra curta, a madeira do quadrado e o contorno
        (u0, v0), (u1, v1) = p2r(cx0, cy0), p2r(cx1, cy1)
        xc, yc, r = (u0 + u1) / 2, (v0 + v1) / 2, (u1 - u0) / 2
        x0, y0, x1, y1 = int(np.floor(u0)) - 4, int(np.floor(v0)) - 4, int(np.ceil(u1)) + 4, int(np.ceil(v1)) + 4
        m = np.zeros(((y1 - y0) * SS, (x1 - x0) * SS), np.uint8)
        cv2.circle(m, (int(round((xc - x0) * SS)), int(round((yc - y0) * SS))), int(round(r * SS)), 255, -1)
        disco = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        out = sombra(out, disco, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
        lado = int(round(2 * r))
        tex = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
        ox, oy = int(round(xc - r)) - x0, int(round(yc - r)) - y0
        tex[oy:oy + lado, ox:ox + lado] = cv2.resize(madeira, (lado, lado), interpolation=cv2.INTER_CUBIC)
        reg = out[y0:y1, x0:x1].astype(np.float32)
        reg = reg * (1 - disco[..., None]) + tex * disco[..., None]
        f, larg = q["contorno"]
        m = np.zeros_like(m)
        cv2.circle(m, (int(round((xc - x0) * SS)), int(round((yc - y0) * SS))), int(round((r - larg / 2) * SS)), 255,
                   max(1, int(round(larg * SS))))
        anel = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - anel) + madeira.reshape(-1, 3).mean(axis=0) * f * anel
        out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        print(f"    criado-mudo redondo em ({xc:.1f}, {yc:.1f}) px, {2 * r:.1f} px de diâmetro (60 cm); o quadrado do "
              f"motor e a sombra dele fora")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 8: o quarto de serviço (item 6 da conferência de 19/10). No
# PDF (ARQ_LAYOUT HUMANIZAÇÃO), a cama de solteiro junto à parede da esquerda, com a cabeceira em cima, e o criado-mudo
# à direita dela, junto à parede de cima; o motor fez ali uma faixa clara com dois quadrados brancos e um risco no piso,
# abaixo de onde vai o criado-mudo. A faixa e o risco saem (cada linha recebe o vinílico limpo da mesma linha, à
# direita, espelhado) e entram a cama e o criado-mudo da suíte 1, que no
# PDF têm as mesmas medidas (cama de 56,7 x 113,4 pt; criado-mudo de 31,2 x 22,7 pt): a cama da direita e o criado-mudo
# do meio, da imagem aprovada, espelhados na vertical (lá a cabeceira é embaixo; a dobra do edredom fica à direita,
# como no PDF), no retângulo do PDF, com a sombra curta dos bancos (BANCO_VARANDA).
QUARTO_SERV_1PAV = {"faixas": [((1006, 692, 1029, 773), (1030, 1048)),   # px: a faixa do motor e o piso limpo à direita
                               ((1044, 698, 1048, 723), (1048, 1056))],  # o risco do motor abaixo do criado-mudo
                    "pecas": [("cama de solteiro", (1696.4, 1492.8, 1753.1, 1606.2), (2170.3, 1604.0, 2227.0, 1717.3)),
                              ("criado-mudo", (1757.6, 1494.5, 1788.8, 1517.2), (2133.5, 1693.5, 2164.7, 1716.2))],
                    "parede": 60}


def quarto_servico_1pav(out):
    from retoque_1pav_casae import sombra
    from retoque_terreo_casae import BANCO_VARANDA
    q = QUARTO_SERV_1PAV
    _, p2r = pdf_pavimento("1Pavimento")
    s = BANCO_VARANDA["sombra"]
    # 1. a faixa e o risco do motor saem: o vinílico limpo da mesma linha, à direita, espelhado até cobrir; a parede
    # fica
    for (ax0, ay0, ax1, ay1), (fx0, fx1) in q["faixas"]:
        fonte = out[ay0:ay1, fx0:fx1]
        fonte = np.concatenate([fonte[:, ::-1], fonte] * ((ax1 - ax0) // (2 * fonte.shape[1]) + 1), axis=1)
        piso = fonte[:, -(ax1 - ax0):]                       # o pedaço que encosta no piso de origem
        reg = out[ay0:ay1, ax0:ax1]
        parede = reg.astype(np.float32).mean(axis=2) < q["parede"]
        reg[~parede] = piso[~parede]
    # 2. a cama e o criado-mudo da suíte 1, da imagem aprovada, espelhados na vertical, no retângulo do PDF
    aprovada = cv2.imread(str(APROVADAS["1Pavimento"]))
    for nome, dst, src in q["pecas"]:
        (du0, dv0), (du1, dv1) = p2r(*dst[:2]), p2r(*dst[2:])
        (su0, sv0), (su1, sv1) = p2r(*src[:2]), p2r(*src[2:])
        x0, y0, x1, y1 = int(np.floor(du0)) - 4, int(np.floor(dv0)) - 4, int(np.ceil(du1)) + 4, int(np.ceil(dv1)) + 4
        h, w = y1 - y0, x1 - x0
        # do local (x, y) ao da fonte: x + (su0 - du0); de cabeça para baixo, sv0 + (dv1 - y)
        M = np.float32([[1, 0, x0 + su0 - du0], [0, -1, sv0 + dv1 - y0 - 1]])
        peca = cv2.warpAffine(aprovada, M, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                              borderMode=cv2.BORDER_REFLECT).astype(np.float32)
        alfa = r14_poligono((h, w), [(du0 - x0, dv0 - y0), (du1 - x0, dv0 - y0), (du1 - x0, dv1 - y0),
                                     (du0 - x0, dv1 - y0)])
        out = sombra(out, alfa, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - alfa[..., None]) + peca * alfa[..., None]), 0,
                                    255).astype(np.uint8)
        print(f"    {nome}: ({du0:.1f}, {dv0:.1f}) a ({du1:.1f}, {dv1:.1f}) px, a da suíte 1 espelhada na vertical")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 9: a banheira do banho master (item 7 da conferência de 19/10;
# seção 6: "banheira: com a torneira de piso, quando o PDF tem"). No PDF, a banheira é oval (95,5 x 50,7 pt, 1,68 x
# 0,89 m) e tem a torneira de piso na ponta da esquerda (a base redonda junto à borda e a bica entrando na banheira);
# o motor a fez retangular de cantos arredondados, sem a torneira. A banheira do motor e a sombra dela saem (o piso
# tecido de um trecho limpo do próprio banho, à direita, na luz do lugar) e entram a banheira oval da biblioteca de
# blocos (`_blocos/blocos.py`, "banheira_oval", a do banho master da Casa E) no retângulo da elipse do PDF e a torneira
# de piso no cromo dos chuveiros aprovados, como a da Casa E (retoque_1pav_casae.torneira_banheira), as duas com a
# sombra curta dos bancos.
BANHEIRA_1PAV = {"oval": (1217.0, 1625.1, 1312.5, 1675.8),                   # pt: a elipse do PDF
                 "apagar": (739, 764, 800, 799),                              # px: a banheira do motor e a sombra
                 "fonte_piso": (801, 765, 829, 812),                          # px: piso limpo do banho, à direita
                 "torneira": {"base": (1210.2, 1650.4), "raio_pt": 3.5, "bica": (1226.6, 1650.4), "larg_bica_pt": 1.47},
                 "faixa_luz": 6, "sigma_luz": 3.0,                             # a luz, linha a linha
                 "corpo": (29 / 134, 41 / 134), "cols_torneira": (86 / 231, 143 / 231),  # no recorte da biblioteca
                 "verde": 8, "feather": 0.8}


def banheira_1pav(out):
    import sys
    from retoque_bege_bahia_terreo import quilting
    from retoque_1pav_casae import sombra
    from retoque_terreo_casae import BANCO_VARANDA, SS
    from retoque_terreo_casac import CROMO, CROMO_CLARO, CROMO_ESCURO
    sys.path.insert(0, str(CASA.parent / "_blocos"))
    from blocos import bloco
    q = BANHEIRA_1PAV
    _, p2r = pdf_pavimento("1Pavimento")
    s = BANCO_VARANDA["sombra"]
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    k = px_m / 56.69                                                          # px por pt
    # 1. a banheira do motor e a sombra saem: o piso limpo do banho, tecido, linha a linha na luz do trecho limpo ao
    # lado (o piso clareia de cima para baixo); a planta da floreira fica e a borda da caixa se funde com o piso
    ax0, ay0, ax1, ay1 = q["apagar"]
    fx0, fy0, fx1, fy1 = q["fonte_piso"]
    f = out[fy0:fy1, fx0:fx1].astype(np.float32)
    fontes = [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    h, w = ay1 - ay0, ax1 - ax0
    piso = quilting(fontes, h, w, p=12, sobra=4, candidatos=300, rng=np.random.default_rng(653))[:h, :w]
    luz = cv2.GaussianBlur(out[ay0:ay1, fx0:fx0 + q["faixa_luz"]].astype(np.float32).mean(axis=1)[:, None, :],
                           (0, 0), sigmaX=0.1, sigmaY=q["sigma_luz"])[:, 0, :]
    lp = cv2.GaussianBlur(piso.mean(axis=1)[:, None, :], (0, 0), sigmaX=0.1, sigmaY=q["sigma_luz"])[:, 0, :]
    piso = piso / lp[:, None, :] * luz[:, None, :]
    reg = out[ay0:ay1, ax0:ax1].astype(np.float32)
    verde = (reg[..., 1] - reg[..., 2] > q["verde"]) & (reg[..., 1] - reg[..., 0] > q["verde"])
    m = (~cv2.dilate(verde.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)).astype(np.float32)
    al = cv2.GaussianBlur(np.pad(m, 3), (0, 0), q["feather"])[3:-3, 3:-3] * m
    out[ay0:ay1, ax0:ax1] = np.clip(np.round(reg * (1 - al[..., None]) + piso * al[..., None]), 0, 255).astype(np.uint8)
    # 2. a banheira oval da biblioteca, só o corpo (a torneira de bancada do recorte e o ladrão saem: a borda é refeita
    # na horizontal entre as colunas de fora e o contorno de cima espelha o de baixo), no retângulo da elipse do PDF
    (u0, v0), (u1, v1) = p2r(*q["oval"][:2]), p2r(*q["oval"][2:])
    cor, alfa = bloco("banheira_oval", px_m * SS)
    H, W = alfa.shape
    (r0, rl), (c0, c1) = q["corpo"], q["cols_torneira"]
    r0, rl, c0, c1 = int(round(r0 * H)), int(round(rl * H)), int(round(c0 * W)), int(round(c1 * W))
    for r in range(r0, rl):
        tt = np.linspace(0, 1, c1 - c0 + 1)[1:-1, None]
        cor[r, c0 + 1:c1] = cor[r, c0] * (1 - tt) + cor[r, c1] * tt
    cor, alfa = cor[r0:], alfa[r0:]
    alfa = np.minimum(alfa, alfa[::-1])
    tw, th = int(round((u1 - u0) * SS)), int(round((v1 - v0) * SS))
    cor = cv2.resize(cor * alfa[..., None], (tw, th), interpolation=cv2.INTER_AREA)
    alfa = cv2.resize(alfa, (tw, th), interpolation=cv2.INTER_AREA)
    x0, y0, x1, y1 = int(np.floor(u0)) - 4, int(np.floor(v0)) - 4, int(np.ceil(u1)) + 4, int(np.ceil(v1)) + 4
    grande = np.zeros(((y1 - y0) * SS, (x1 - x0) * SS, 3), np.float32)
    ag = np.zeros(grande.shape[:2], np.float32)
    ox, oy = int(round((u0 - x0) * SS)), int(round((v0 - y0) * SS))
    grande[oy:oy + th, ox:ox + tw] = cor
    ag[oy:oy + th, ox:ox + tw] = alfa
    pre = cv2.resize(grande, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    a_ = cv2.resize(ag, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    out = sombra(out, a_, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - a_[..., None]) + pre), 0, 255).astype(np.uint8)
    # 3. a torneira de piso: a base redonda e a bica, no cromo dos chuveiros aprovados
    t = q["torneira"]
    bx, by = p2r(*t["base"])
    px_, py_ = p2r(*t["bica"])
    r = t["raio_pt"] * k
    x0, y0, x1, y1 = int(bx - r) - 4, int(by - r) - 4, int(px_) + 5, int(by + r) + 5
    hh, ww = y1 - y0, x1 - x0
    cor = np.zeros((hh * SS, ww * SS, 3), np.float32)
    al = np.zeros((hh * SS, ww * SS), np.float32)

    def pt(x, y):
        return int(round((x - x0) * SS)), int(round((y - y0) * SS))

    def pinta(desenho, c):
        mm = np.zeros(al.shape, np.uint8)
        desenho(mm)
        cor[mm > 0] = c
        al[mm > 0] = 1
    lb = t["larg_bica_pt"] * k
    pinta(lambda mm: cv2.line(mm, pt(bx, by), pt(px_, py_), 255, max(1, int(round(lb * SS)))), CROMO_ESCURO)
    pinta(lambda mm: cv2.line(mm, pt(bx, by), pt(px_, py_), 255, max(1, int(round(0.6 * lb * SS)))), CROMO)
    pinta(lambda mm: cv2.line(mm, pt(bx, by - 0.15 * lb), pt(px_ - 0.3, py_ - 0.15 * lb), 255,
                              max(1, int(round(0.22 * lb * SS)))), CROMO_CLARO)
    pinta(lambda mm: cv2.circle(mm, pt(bx, by), int(round(r * SS)), 255, -1), CROMO_ESCURO)
    pinta(lambda mm: cv2.circle(mm, pt(bx, by), int(round(0.82 * r * SS)), 255, -1), CROMO)
    pinta(lambda mm: cv2.circle(mm, pt(bx - 0.3 * r, by - 0.3 * r), int(round(0.35 * r * SS)), 255, -1), CROMO_CLARO)
    a_ = cv2.resize(al, (ww, hh), interpolation=cv2.INTER_AREA)
    c_ = cv2.resize(cor * al[..., None], (ww, hh), interpolation=cv2.INTER_AREA)
    out = sombra(out, a_, (x0, y0, x1, y1), s["desloc"], s["sigma"], s["forca"])
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - a_[..., None]) + c_), 0, 255).astype(np.uint8)
    print(f"    banheira oval da biblioteca em ({u0:.1f}, {v0:.1f}) a ({u1:.1f}, {v1:.1f}) px (a do motor fora); "
          f"torneira de piso em ({bx:.1f}, {by:.1f}) px, com a bica até ({px_:.1f}, {py_:.1f})")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 10: cortinas de linho nas quatro suítes (seção 8: "em linho
# off-white, traço fino. O bloco é o de `_blocos/blocos.py` (`cortina`)"; [20/10] "trilhos da cortina tem que ser de
# fora a fora"). No PDF, cada suíte tem dois trechos de linha ondulada (ARQ_LOUÇAS E METAIS, 0,85 pt) junto às portas de
# vidro; o motor os fez como uma coluna de tracinhos escuros no vinílico. Como no 1º Pavimento da Casa E
# (`retoque_1pav_casae.cortinas_linho`):
# - os tracinhos saem (`limpar`): numa faixa de 9 px no eixo de cada trecho, do começo ao fim dele (com folga), cada linha
#   recebe o vinílico das duas beiradas da faixa, ligado em linha reta (as réguas correm na horizontal), só onde o piso
#   está mais escuro que isso; a beirada fora do tom do vinílico do trecho (a mediana da faixa; a poltrona da suíte 2,
#   o caixilho da suíte 1, o vidro do item 14) dá lugar à outra, e sem beirada no tom a linha fica; a parede e o
#   caixilho (a 7 px do eixo) ficam;
# - o pano da biblioteca em cada trecho do PDF (eixo do tecido no eixo da linha, na mesma extensão: a meia distância) e,
#   em cada suíte, o trilho de parede a parede, do lado do vidro (à esquerda nas suítes 3, 2 e master; à direita na 1).
#   O fim do trilho é a parede preta numa coluna "dentro" px para dentro do quarto; os trilhos do mesmo lado que se
#   sobrepõem viram um só.
CORTINAS_1PAV = {"limpar": {"meia": 4, "linhas": (-5, 8), "escuro": 20, "parede": 40, "difere": 25},
                 "vidro_direita_pt": 2000, "parede": 55, "seguidos": 3, "busca_m": 6.0, "dentro": 3, "ss": 8}


def trechos_cortina_1pav():
    """Os trechos de cortina do PDF: (lado do vidro, eixo x, y de cima, y de baixo), em px da imagem."""
    from retoque_1pav_casae import trechos_cortina
    q = CORTINAS_1PAV
    pg, p2r = pdf_pavimento("1Pavimento")
    trechos = []
    for pts in trechos_cortina(pg):
        xe = float(np.median(pts[:, 0]))                     # o eixo do tecido (as ondas são verticais nas fachadas)
        (ex, ey0), (_, ey1) = p2r(xe, float(pts[:, 1].min())), p2r(xe, float(pts[:, 1].max()))
        trechos.append(("direita" if xe > q["vidro_direita_pt"] else "esquerda", ex, ey0, ey1))
    return trechos


def tracinhos_cortina(out, trechos):
    """Os tracinhos escuros do motor no lugar das cortinas saem (o passo 1 do item 10; o item 14 o chama antes de
    espelhar o piso para as portas de vidro). Devolve os px limpos."""
    q = CORTINAS_1PAV
    lp = q["limpar"]
    limpos = 0
    for _, ex, ey0, ey1 in trechos:
        cc = int(round(ex))
        c0, c1 = cc - lp["meia"], cc + lp["meia"] + 1
        r0, r1 = int(np.floor(ey0)) + lp["linhas"][0], int(np.ceil(ey1)) + lp["linhas"][1]
        reg = out[r0:r1, c0:c1].astype(np.float32)
        esq = np.median(out[r0:r1, c0 - 2:c0].astype(np.float32), axis=1)
        dir_ = np.median(out[r0:r1, c1:c1 + 2].astype(np.float32), axis=1)
        le, ld = esq.mean(axis=1), dir_.mean(axis=1)
        ref = float(np.median(reg.mean(axis=2)))       # o tom do vinílico no trecho: a mediana da faixa (os tracinhos
                                                       # são poucos; as beiradas podem ser o vidro e a poltrona)
        ok_e, ok_d = np.abs(le - ref) < lp["difere"], np.abs(ld - ref) < lp["difere"]
        esq, dir_ = (np.where(ok_e[:, None], esq, dir_),                       # uma beirada fora do piso (móvel,
                     np.where(ok_d[:, None], dir_, esq))                       # caixilho): vale a outra
        tt = ((np.arange(c1 - c0) + 0.5) / (c1 - c0))[None, :, None]
        liso = esq[:, None, :] * (1 - tt) + dir_[:, None, :] * tt
        L = reg.mean(axis=2)
        m = (L < liso.mean(axis=2) - lp["escuro"]) & (L > lp["parede"]) & (ok_e | ok_d)[:, None]
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        m &= ~cv2.dilate((L <= lp["parede"]).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        al = (cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5) * m)[..., None]
        out[r0:r1, c0:c1] = np.clip(np.round(reg * (1 - al) + liso * al), 0, 255).astype(np.uint8)
        limpos += int(m.sum())
    return limpos


def cortinas_1pav(out):
    import sys
    from retoque_terreo_casae import pousar_cortina
    sys.path.insert(0, str(CASA.parent / "_blocos"))
    import blocos
    q = CORTINAS_1PAV
    pg, p2r = pdf_pavimento("1Pavimento")
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    trechos = trechos_cortina_1pav()
    # 1. os tracinhos do motor saem (com o item 14 antes, já saíram: aqui não sobra nada)
    limpos = tracinhos_cortina(out, trechos)
    # 2. os panos nos trechos do PDF e os trilhos de parede a parede
    k = q["ss"]
    busca = int(q["busca_m"] * px_m)
    trilhos = []
    for vidro, ex, ey0, ey1 in trechos:
        # a coluna da busca, um pouco para dentro do quarto (no eixo, colado ao vidro, o caixilho pararia a busca)
        dentro = int(round(ex)) + (q["dentro"] if vidro == "esquerda" else -q["dentro"])
        escuro = out[:, dentro].astype(np.float32).mean(axis=1) < q["parede"]

        def ate_parede(y, passo):
            n = 0
            for yy in range(int(round(y)), int(round(y)) + passo * busca, passo):
                n = n + 1 if escuro[yy] else 0
                if n >= q["seguidos"]:
                    return yy - passo * (q["seguidos"] - 1) - passo * 0.5
            return y
        trilhos.append([vidro, ex, ate_parede((ey0 + ey1) / 2, -1), ate_parede((ey0 + ey1) / 2, +1)])
    unidos = []
    for v, ex, t0, t1 in sorted(trilhos, key=lambda t: (t[0], t[2])):
        if unidos and unidos[-1][0] == v and t0 < unidos[-1][3] - 2:
            unidos[-1][2], unidos[-1][3] = min(unidos[-1][2], t0), max(unidos[-1][3], t1)
        else:
            unidos.append([v, ex, t0, t1])
    for v, ex, t0, t1 in unidos:
        cor, al = blocos.cortina((t1 - t0) / px_m, px_m * k, com_pano=False)
        pousar_cortina(out, cor, al, ex, t0, k, v)
    for v, ex, ey0, ey1 in trechos:
        cor, al = blocos.cortina((ey1 - ey0) / px_m, px_m * k, com_trilho=False)
        pousar_cortina(out, cor, al, ex, ey0, k, v)
    print(f"    {limpos} px de tracinhos do motor fora; {len(trechos)} panos de linho nos trechos do PDF e "
          f"{len(unidos)} trilhos de parede a parede: " + ", ".join(f"{v} x {ex:.0f}, y {t0:.0f} a {t1:.0f}"
                                                                     for v, ex, t0, t1 in unidos))
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 14: as portas de vidro de correr das suítes para as varandas,
# finas, em dois planos (seções 4 e 18). No PDF (ARQ_PAREDE), cada fachada tem dois planos de folhas de correr (cada folha
# em duas lâminas de 1,4 pt lado a lado, com as peças de 2,8 x 4,5 pt nas pontas): o de fora, junto à varanda, e o de
# dentro, a ~3 px; na master, o plano de fora segue pela frente do banho master. O motor fez em cada fachada um "tubo"
# branco de ~8 px com contorno cinza. Como os vidros do Térreo (item 5, `vidros_finos`): o tubo sai (`esquadria_limpar`
# da Casa E, folha a folha: cada coluna da faixa recebe o piso do seu lado, em espelho; o escuro da parede não serve de
# fonte) e as peças do PDF entram finas (`esquadria_desenhar`: o vidro claro e o contorno fino). A limpeza vai do plano
# de fora para o de dentro (`vidro`: o lado da varanda), para o espelho do plano de fora não levar o tubo: entre os
# planos fica o Bege Bahia da varanda; e, antes dela, os tracinhos das cortinas saem (`tracinhos_cortina`, o passo 1
# do item 10), para o espelho do plano de dentro não os copiar. Na suíte 1 os dois planos são zonas separadas: a
# janela do banho 1 (no alinhamento do plano de dentro, mais acima) não entra. As janelas dos banhos 1 e 2 e a da
# escada ficam como estão. Roda depois do Bege Bahia das varandas (item 12) e antes das cortinas (item 10), como na
# Casa E (as fachadas antes das cortinas de linho).
VIDROS_1PAV = {"zonas": [((1389.1, 561.4, 1406.1, 783.6), "esquerda"),        # suíte 3
                         ((1389.1, 1177.2, 1406.1, 1370.4), "esquerda"),       # suíte 2
                         ((1151.0, 1394.8, 1168.0, 1772.9), "esquerda"),       # suíte master e banho master
                         ((2301.9, 1289.9, 2307.5, 1693.5), "direita"),        # suíte 1, plano de fora (em L)
                         ((2290.5, 1491.6, 2296.2, 1693.5), "direita")]}       # suíte 1, plano de dentro


def vidros_1pav(out):
    import sys
    import retoque_terreo_casae as T
    sys.path.insert(0, str(CASA.parent / "_texturas"))
    from texturas import textura
    pg, p2r = pdf_pavimento("1Pavimento")
    px_m = p2r(56.69, 0)[0] - p2r(0, 0)[0]
    limpos = tracinhos_cortina(out, trechos_cortina_1pav())
    par = [d for d in pg.get_drawings() if d.get("layer") == "ARQ_PAREDE"]
    img = out.astype(np.float32)
    n = 0
    for z, vidro in VIDROS_1PAV["zonas"]:
        folhas = [d["rect"] for d in par
                  if d["type"] == "f" and d["fill"] and min(d["fill"]) >= 0.9 and min(d["rect"].width, d["rect"].height)
                  <= 3.2 and z[0] - 0.5 <= d["rect"].x0 and d["rect"].x1 <= z[2] + 0.5 and z[1] - 0.5 <= d["rect"].y0
                  and d["rect"].y1 <= z[3] + 0.5]
        for r in sorted(folhas, key=lambda r: r.x0 if vidro == "esquerda" else -r.x1):   # de fora para dentro
            T.esquadria_limpar(img, r, p2r)
        n += len(folhas)
    for z, _ in VIDROS_1PAV["zonas"]:
        T.esquadria_desenhar(img, z, par, p2r, px_m, textura)
    print(f"    vidros das suítes: {limpos} px de tracinhos das cortinas fora antes; {n} peças do PDF limpas (de fora "
          f"para dentro) e redesenhadas finas em {len(VIDROS_1PAV['zonas'])} zonas")
    return np.clip(img, 0, 255).astype(np.uint8)

# Pente fino pelas regras (21/10/26), 1º Pavimento, item 15: soleiras (R13: a soleira é o vão da porta na espessura da
# parede deixado em branco no PDF, entre os batentes; onde o piso de um dos lados atravessa o vão, não há). Conferidas
# porta a porta, numa folha de recortes do PDF, da base e do render, e pela cor do próprio PDF no meio de cada vão:
# - sem soleira: as 11 portas de giro (os arcos do item 2: o travertino da circulação, o vinílico das suítes ou o cinza
#   do quarto de serviço e da saleta atravessam o vão) e o elevador (no 1º Pavimento, o travertino do hall vai até a
#   cabine; no Subsolo, não). Nada a mudar;
# - com soleira (o vão branco da ARQ_PAREDE, com a folha de correr dentro): a porta de correr da saleta para o quarto
#   de serviço. O motor fez uma caixa clara ocupando o vão;
# - os vãos brancos do banho 3 (na parede de fora, para o Térreo) e do banho de serviço (na parede da varanda) são
#   janelas de correr (0,76 e 0,56 m), não portas: ficam como o motor as fez, como as dos banhos 1 e 2;
# - a seção 4 pede soleira em inox escovado na porta do elevador, mas no PDF do 1º Pavimento o travertino do hall
#   atravessa o vão (R13: só onde o PDF tem): fica sem.
# Desenho das soleiras do Térreo e do Subsolo (`desenhar_soleiras`): o vão exato do PDF em Bege Bahia na escala, no tom
# da referência, com as faces da parede em cinza fino. Por cima, a folha de correr no retângulo do PDF (`fora`), fina:
# clara (`folha`), com o contorno no cinza das faces (a do motor, deixada como estava, tinha um ponto preto na ponta).
SOLEIRAS_1PAV = {"pdf": [(1751.9, 1639.1, 1808.6, 1647.6)],    # saleta para o quarto de serviço
                 "fora": [(1753.1, 1641.7, 1807.5, 1644.5)],   # a folha de correr
                 "folha": (236, 237, 238),
                 "forca": 0.5, "linha": (150, 152, 154), "linha_px": 0.4, "ss": 8, "semente": 7}


def soleiras_1pav(out):
    q = SOLEIRAS_1PAV
    out = desenhar_soleiras(out, "1Pavimento", q)
    _, p2r = pdf_pavimento("1Pavimento")
    k = q["ss"]
    for r in q["fora"]:                                       # a folha de correr, fina, por cima da soleira
        (x0, y0), (x1, y1) = p2r(r[0], r[1]), p2r(r[2], r[3])
        X0, Y0, X1, Y1 = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1, int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 2
        h, w = Y1 - Y0, X1 - X0
        u0, v0, u1, v1 = [int(round(c * k)) for c in (x0 - X0, y0 - Y0, x1 - X0, y1 - Y0)]
        m = np.zeros((h * k, w * k), np.uint8)
        m[v0:v1, u0:u1] = 255
        e = max(1, int(round(q["linha_px"] * k)))
        f = np.zeros_like(m)
        cv2.rectangle(f, (u0, v0), (u1 - 1, v1 - 1), 255, e)
        al = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        fl = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg = reg * (1 - al) + np.float32(q["folha"]) * al
        reg = reg * (1 - fl) + np.float32(q["linha"]) * fl
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    1 soleira de Bege Bahia no vão branco do PDF (saleta), com a folha de correr fina por cima; nas 11 portas "
          "de giro e no elevador o piso atravessa o vão; os vãos brancos dos banhos 3 e de serviço são janelas")
    return out

# Pente fino pelas regras (21/10/26), 1º Pavimento, item 11: vinílico na escala (R4: "Vinílico: réguas de ~20 cm,
# claras, em tons alternados"). O motor fez réguas de ~40 cm. Como no 1º Pavimento da Casa E
# (`retoque_1pav_casae.vinilico_escala`, item 11 de lá, com os mesmos números, `VINILICO`): nas áreas de vinílico da base
# chapada da entrega (o mesmo laranja da legenda, levado à imagem pelo quadro comum, `base_terreo`), só no que é piso no
# render (os objetos no tom da madeira saem por fugir da luz do piso; a sombra fica como piso), as réguas de 20 cm,
# 1,2 a 1,8 m, em fiadas com as juntas desencontradas, cada uma num tom, com o veio do próprio vinílico do render, na
# luz do lugar; e o vinílico escurecido sobe 70% do caminho até a luz mediana. Roda logo depois das portas e das
# escadas (itens 2 e 3), antes dos móveis dos itens 4 a 10, como na Casa E, onde vinha antes dos outros passos. As folhas
# das portas (os brancos compridos da ARQ_PAREDE, como no item 2; o motor as fez em traço duplo fino, no tom da madeira)
# ficam fora do piso, com `folga_folha` px.
VINILICO_1PAV = {"folga_folha": 2}


def vinilico_1pav(out):
    from retoque_1pav_casae import VINILICO, reguas_vinilico
    q = VINILICO
    chapada = base_terreo(out.shape[:2], "1Pavimento")
    vin = (np.abs(chapada.astype(np.int32) - np.array(q["cor_chapada"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    vin = cv2.morphologyEx(vin, cv2.MORPH_CLOSE, np.ones((q["fechar"], 1), np.uint8)) > 0
    pg, p2r = pdf_pavimento("1Pavimento")
    H, W = out.shape[:2]
    sa, bf = SEM_ARCOS_SUB, SEM_ARCOS_1PAV
    k = sa["ss"]
    fl = np.zeros((H * k, W * k), np.uint8)
    for d in pg.get_drawings():
        if d.get("layer") == sa["camada"] and d["type"] == "f" and d.get("fill") and min(d["fill"]) > 0.9:
            for c in caminhos_pdf(d, p2r):
                w, h = np.ptp(c[:, 0]), np.ptp(c[:, 1])
                if max(w, h) >= max(bf["folha_comprida"] * min(w, h), bf["folha_min"]):
                    cv2.fillPoly(fl, [np.int32(np.round(c * k))], 255)
    f = 2 * VINILICO_1PAV["folga_folha"] + 1
    folhas = cv2.dilate((cv2.resize(fl, (W, H), interpolation=cv2.INTER_AREA) > 0).astype(np.uint8),
                        np.ones((f, f), np.uint8)) > 0
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    im = out.astype(np.float32)
    lum, croma = im.mean(axis=2), im[..., 2] - im[..., 0]
    piso = vin & (croma >= q["croma_min"]) & (lum >= q["lum"][0]) & (lum <= q["lum"][1]) & ~folhas
    sx, sy = q["sig_ao_longo_m"] * px_m, q["sig_atravessando_m"] * px_m

    def luz(m):
        mf = m.astype(np.float32)
        return (cv2.GaussianBlur(im * mf[..., None], (0, 0), sigmaX=sx, sigmaY=sy)
                / np.maximum(cv2.GaussianBlur(mf, (0, 0), sigmaX=sx, sigmaY=sy), 1e-4)[..., None])
    L0 = luz(piso)
    razao = im / np.maximum(L0, 1)
    fora = ((im - L0).max(axis=2) > q["claro"]) | (((L0 - im).max(axis=2) > q["escuro"])
                                                  & (razao.max(axis=2) - razao.min(axis=2) > q["matiz"]))
    n, lab, st, _ = cv2.connectedComponentsWithStats((fora & piso).astype(np.uint8), connectivity=8)
    fora = (st[:, cv2.CC_STAT_AREA] >= q["objeto_min"])[lab] & (lab > 0)
    piso &= ~cv2.dilate(fora.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    piso = cv2.morphologyEx(piso.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    mf = piso.astype(np.float32)
    L = luz(piso)
    vs, vy = q["veio_sig"]                                                   # o veio: o detalhe fino ao longo das réguas
    veio = lum / np.maximum(cv2.GaussianBlur(lum, (0, 0), sigmaX=vs, sigmaY=vy), 1)
    limpo = cv2.erode(piso.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    ys, xs = np.nonzero(piso)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    D = reguas_vinilico(y1 - y0, x1 - x0, px_m, veio, limpo, np.random.default_rng(q["semente"]))
    novo = im.copy()
    novo[y0:y1, x0:x1] = L[y0:y1, x0:x1] * D[..., None]
    al = (cv2.GaussianBlur(mf, (0, 0), 0.7) * piso)[..., None]
    novo = im * (1 - al) + novo * al
    sg = q["clarear_sig_m"] * px_m                                           # o escurecido sobe parte do caminho
    Lg = cv2.GaussianBlur(lum * mf, (0, 0), sg) / np.maximum(cv2.GaussianBlur(mf, (0, 0), sg), 1e-4)
    ref = float(np.median(Lg[piso]))
    g = 1 + q["clarear"] * np.maximum(0, ref - Lg) / np.maximum(Lg, 1)
    av = cv2.GaussianBlur(vin.astype(np.float32), (0, 0), 1.0)
    novo *= (1 + (g - 1) * av)[..., None]
    out = np.clip(novo, 0, 255).astype(np.uint8)
    print(f"    vinílico: {int(piso.sum())} px em réguas de {100 * q['regua_m']:.0f} cm, a {px_m:.2f} px/m (fora "
          f"{int((folhas & vin).sum())} px das folhas das portas); o escurecido sobe {100 * q['clarear']:.0f}% do "
          f"caminho até a luz mediana ({ref:.0f}), até +{100 * (g[vin].max() - 1):.0f}%")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 12: o Bege Bahia das quatro varandas como a referência (seção
# 18; R1: a foto de referência, nublada, quente, com o contraste dela). O motor fez as varandas das suítes 3, 2, master e
# 1 num bege claro e rosado com veios grandes de mármore (RGB ~227, 210, 200). Como o Térreo da Casa A (item 9,
# `bege_na_referencia`, com os números do item 43 do Térreo da Casa E, `retoque_terreo_casae.BEGE`), para as duas
# ficarem iguais: os pontinhos escuros pequenos do motor viram a luz do lugar; o desenho da biblioteca entra inteiro, na
# escala, no tom da foto (RGB 230, 211, 186), com a luz do lugar; o que foge da luz (os caixilhos, a linha do
# guarda-corpo) fica, e o anel em volta vai ao piso novo de perto. As áreas são as manchas do #E8E8E8 da base chapada que
# contêm os pontos `sementes` (px), uma por varanda: o hall da caracol, o quarto e o banho de serviço têm a mesma cor na
# base e não são varanda. A mancha é fechada em 5 x 5 onde o render é piso claro, como no Térreo.
BEGE_VARANDAS_1PAV = {"cor_base": (232, 232, 232), "tol": 6, "fechar": 5, "claro": 150,
                      "sementes": [(817, 240), (820, 540), (675, 740), (1400, 700)]}   # suítes 3, 2, master e 1


def bege_varandas_1pav(out):
    q = BEGE_VARANDAS_1PAV
    _, p2r = pdf_pavimento("1Pavimento")
    b2 = base_terreo(out.shape[:2], "1Pavimento").astype(np.int32)
    m = (np.abs(b2 - np.array(q["cor_base"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    ids = sorted({int(lab[y, x]) for x, y in q["sementes"]} - {0})
    bege = np.isin(lab, ids)
    im = out.astype(np.float32)
    claro = (im.mean(axis=2) >= q["claro"]) & ~((im[..., 1] > im[..., 2] + 4) & (im[..., 1] > im[..., 0] + 12))
    k = np.ones((q["fechar"], q["fechar"]), np.uint8)
    bege |= cv2.morphologyEx(bege.astype(np.uint8), cv2.MORPH_CLOSE, k).astype(bool) & claro
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                  # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d - b))
    out, npt, npx, nanel = bege_na_referencia(out, bege, px_m)
    print(f"    Bege Bahia das {len(ids)} varandas: {npt} px de pontinhos escuros fora; {npx} px no desenho da "
          f"biblioteca, a {px_m:.2f} px/m, no tom da foto; {nanel} px do anel em volta dos objetos")
    return out


# Pente fino pelas regras (21/10/26), 1º Pavimento, item 13: as projeções da cobertura e do pergolado em tracejado bem
# visível, por cima (R8, R9). No PDF do 1º Pavimento, as duas estão em tracejado (traços de 5,67 pt): a da cobertura na
# ARQ_CONTRAPISO, em preto (notas "PROJ. COBERTURA"), em dois contornos fechados, o de fora (o L do Térreo: 1290 a 2381
# pt em x e 511 a 1815 pt em y, com o braço de baixo até 1038 pt a partir de 1344 pt) e o de dentro, 34 pt para dentro
# (o beiral), e dois trechos curtos entre eles, à direita; a do pergolado na ARQ_PERGOLADO (notas "PROJ. PERGOLADO"), a
# grade de vigas de 20 cm à esquerda da suíte 2. O motor não as desenhou, e quase tudo cai fora da pegada do
# pavimento, sobre o Térreo nublado: por isso entram na final (`rotulos_casaa.final_imagem`, depois do nublado e do
# tracejado do lote), no quadro de 3840 px. As linhas saem do próprio PDF: os traços curtos de cada camada, juntados
# por reta (a mesma coordenada, em pé ou deitados) enquanto o vão entre eles for curto, só as retas com `min_tracos`
# traços ou mais (os soltos são de outros desenhos). Desenho no traço das projeções do Térreo (item 4, `PROJECOES_A`:
# 8,5 pt de traço, 4,25 de vão, 0,55 px na escala do ajuste, cinza 150, força 0,85), menos nas paredes pretas.
PROJECOES_1PAV = {"camadas": [("ARQ_CONTRAPISO", (0.0, 0.0, 0.0)), ("ARQ_PERGOLADO", None)],
                  "traco_max_pt": 12.0, "junta_pt": 6.0, "min_tracos": 5}


def retas_tracejadas(pg, camada, cor, traco_max, junta, min_tracos):
    """As retas (pt) que os traços curtos de uma camada do PDF formam: em pé ou deitados, na mesma coordenada, juntados
    enquanto o vão for de até `junta` pt; só as com `min_tracos` traços ou mais."""
    grupos = {}
    for d in pg.get_drawings():
        if d.get("layer") != camada or d["type"] != "s" or (cor is not None and d.get("color") != cor):
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            (ax, ay), (bx, by) = (it[1].x, it[1].y), (it[2].x, it[2].y)
            if np.hypot(bx - ax, by - ay) > traco_max:
                continue
            if abs(ay - by) < 0.05:
                grupos.setdefault(("h", round(ay, 1)), []).append((min(ax, bx), max(ax, bx)))
            elif abs(ax - bx) < 0.05:
                grupos.setdefault(("v", round(ax, 1)), []).append((min(ay, by), max(ay, by)))
    retas = []
    for (sentido, c), ts in grupos.items():
        ts.sort()
        corrida = [list(ts[0]), 1]
        for t0, t1 in ts[1:] + [(np.inf, np.inf)]:
            if t0 - corrida[0][1] <= junta:
                corrida[0][1] = max(corrida[0][1], t1)
                corrida[1] += 1
                continue
            if corrida[1] >= min_tracos:
                (u0, u1) = corrida[0]
                retas.append([(u0, c), (u1, c)] if sentido == "h" else [(c, u0), (c, u1)])
            corrida = [[t0, t1], 1]
    return retas


def tracejar(forma, retas, p2x, traco_pt, vao_pt, larg_px, ss=8):
    """Máscara (0 a 1, no quadro `forma`) das retas em pt, refeitas em tracejado de `traco_pt` e `vao_pt`; p2x leva
    pt ao quadro."""
    h, w = forma
    m = np.zeros((h * ss, w * ss), np.uint8)
    lw = max(1, int(round(larg_px * ss)))
    n = 0
    for (ax, ay), (bx, by) in retas:
        comp = np.hypot(bx - ax, by - ay)
        t = 0.0
        while t < comp:
            t1 = min(comp, t + traco_pt)
            u = p2x(ax + (bx - ax) * t / comp, ay + (by - ay) * t / comp)
            v = p2x(ax + (bx - ax) * t1 / comp, ay + (by - ay) * t1 / comp)
            cv2.line(m, (int(round(u[0] * ss)), int(round(u[1] * ss))), (int(round(v[0] * ss)), int(round(v[1] * ss))),
                     255, lw, cv2.LINE_AA)
            n += 1
            t = t1 + vao_pt
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA), n


def projecoes_1pav_final(final, pg, p2q, escala):
    """Na final do 1º Pavimento (quadro de 3840 px; `escala`: px do quadro por px do ajuste): a cobertura e o pergolado
    em tracejado, por cima do Térreo nublado e do pavimento, menos nas paredes pretas."""
    q, e = PROJECOES_1PAV, PROJECOES_A
    retas, nomes = [], []
    for camada, cor in q["camadas"]:
        r = retas_tracejadas(pg, camada, cor, q["traco_max_pt"], q["junta_pt"], q["min_tracos"])
        retas += r
        nomes.append(f"{len(r)} da {camada}")
    a, n = tracejar(final.shape[:2], retas, p2q, e["traco_pt"], e["vao_pt"], e["larg_px"] * escala)
    a *= e["forca"] * (final.astype(np.float32).mean(axis=2) >= e["parede"])     # nas paredes pretas o traço some
    print(f"    projeções da cobertura e do pergolado: {len(retas)} retas do PDF ({', '.join(nomes)}), {n} traços")
    return np.clip(final * (1 - a[..., None]) + np.float32(e["cor"]) * a[..., None], 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), Térreo, item 1: as escadas com linhas e o triângulo (R14 e seção 5). A interna em
# U e a caracol ganharam a R14 nas suas funções (ESCADA_INT["r14"], CARACOL["r14"]); aqui ficam as duas externas.
# - Do deck para o Subsolo (degraus 1 a 11, sob o spa): no PDF do Térreo, o "D" à esquerda, junto ao deck; os bocéis a
#   cada 17 pt, de 737,1 a 907,2 pt, e a escada de 1230,9 a 1299,0 pt. O motor desenhou os bocéis e uma linha no meio em
#   traço escuro, que saem (mediana na horizontal e na vertical, só dentro da escada). Entram os bocéis em linha suave
#   com a sombra curta (retoque_terreo_casae.escada_linhas, a da escada externa do Térreo da Casa E): viva do deck até o
#   corte do PDF do Subsolo (a diagonal no 9º degrau, prolongada até a borda de cima) e, depois dele, já no Subsolo,
#   esmaecida, sem tracejado (0,65: com o 0,45 da Casa E, no Bege Bahia, ficava uma mancha branca); o triângulo no
#   topo, junto ao deck, apontando para a descida.
# - A larga, do deck ao pátio da piscina (degraus 12 a 19): sete blocos desencontrados do ARQ_CONTRAPISO, cada um por
#   cima do anterior, e o pátio. Sobe do deck (usuário, 21/10/26: confirmado). O bocel de cada degrau é o L (a borda da
#   esquerda e a de baixo) do bloco de cima, na parte que fica sobre o de baixo; nele, a linha suave e a sombra curta no
#   degrau de baixo. O triângulo no degrau 12, no meio da faixa à mostra, apontando para a direita (o próximo degrau).
ESCADA_DECK = {"nome": "do deck para o Subsolo, desce da esquerda para a direita",
               "pdf": (737.1, 1230.9, 907.2, 1299.0), "bocels": [754.1 + 17.0 * k for k in range(9)],
               "baixo": "direita", "inicio": "esquerda", "corte": [(754.1, 1230.9), (788.2, 1299.0)],
               "viva": "esquerda", "apos": "esmaecida", "esmaecer": 0.65, "mediana": (7, 5)}
ESCADA_LARGA = {"blocos": [(640.8, 666.8, 714.5, 794.4), (674.8, 632.8, 748.5, 771.7), (708.8, 564.8, 782.5, 754.7),
                           (742.8, 576.1, 816.5, 740.5), (776.8, 553.4, 844.8, 726.4), (822.2, 576.1, 867.5, 715.0),
                           (861.9, 544.9, 907.2, 703.7)],
                "patio": (907.2, 544.9, 960.0, 703.7)}      # o pátio (degrau 19), à direita do último bloco


def escadas_externas_r14(out):
    from retoque_terreo_casae import escada_linhas
    _, p2r = pdf_pavimento("Terreo")
    kpt = (p2r(1000, 1000)[0] - p2r(900, 1000)[0]) / 100       # px por pt

    # 1. do deck para o Subsolo: os traços escuros do motor saem e entram os bocéis da R14
    e = ESCADA_DECK
    ex0, ey0, ex1, ey1 = e["pdf"]
    (a, b), (c, d) = p2r(ex0, ey0), p2r(ex1, ey1)
    x0, y0, x1, y1 = int(np.floor(a)), int(np.floor(b)), int(np.ceil(c)), int(np.ceil(d))
    mx, my = e["mediana"]
    reg = out[y0 - my:y1 + my, x0 - mx:x1 + mx]
    lim = np.empty_like(reg)
    for ch in range(3):                                         # mediana em x (os bocéis), depois em y (a linha do meio)
        c_ = reg[..., ch].astype(np.float32)
        hx = np.stack([np.roll(c_, k, axis=1) for k in range(-(mx // 2), mx // 2 + 1)]).astype(np.float32)
        c_ = np.median(hx, axis=0)
        hy = np.stack([np.roll(c_, k, axis=0) for k in range(-(my // 2), my // 2 + 1)])
        lim[..., ch] = np.clip(np.median(hy, axis=0), 0, 255).astype(np.uint8)
    out[y0:y1, x0:x1] = lim[my:my + (y1 - y0), mx:mx + (x1 - x0)]
    out = escada_linhas(out, None, e, p2r=p2r)

    # 2. a larga: os bocéis dos blocos (o L do bloco de cima sobre o de baixo) e o triângulo no degrau 12
    q = R14
    blocos = ESCADA_LARGA["blocos"] + [ESCADA_LARGA["patio"]]
    pts = [p2r(x, y) for bl in blocos for x, y in ((bl[0], bl[1]), (bl[2], bl[3]))]
    X0, Y0 = int(min(p[0] for p in pts)) - 8, int(min(p[1] for p in pts)) - 8
    X1, Y1 = int(max(p[0] for p in pts)) + 8, int(max(p[1] for p in pts)) + 8
    forma = (Y1 - Y0, X1 - X0)

    def loc(x, y):
        u, v = p2r(x, y)
        return u - X0, v - Y0

    def ret(bl):
        bx0, by0, bx1, by1 = bl
        return r14_poligono(forma, [loc(bx0, by0), loc(bx1, by0), loc(bx1, by1), loc(bx0, by1)])
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forca, alcance = q["sombra"]
    fator = np.ones(forma, np.float32)
    mascaras = [ret(bl) for bl in blocos]
    for i in range(1, len(blocos)):
        cima, baixo = blocos[i], blocos[i - 1]
        # a parte do degrau de baixo que fica à mostra (sem os blocos de cima)
        visivel = mascaras[i - 1].copy()
        for m in mascaras[i:]:
            visivel *= 1 - m
        ya, yb = max(cima[1], baixo[1]), min(cima[3], baixo[3])
        lin = [loc(cima[0], ya), loc(cima[0], yb)]
        if baixo[1] < cima[3] < baixo[3]:
            lin.append(loc(min(cima[2], baixo[2]), cima[3]))
            lin = [lin[0], loc(cima[0], cima[3]), lin[2]]
        lb = r14_linha(forma, lin, q["bocel_pt"] * kpt)
        fator *= 1 - (1 - q["bocel"]) * lb
        # a sombra curta no degrau de baixo, junto ao L (para a esquerda e para baixo)
        dist = cv2.distanceTransform((mascaras[i] < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        som = forca * np.clip(1 - dist / (alcance * kpt), 0, 1) ** 1.6
        fator *= 1 - som * visivel
    reg *= fator[..., None]
    a0, b0, a1_, b1 = blocos[0]
    tri = r14_triangulo(forma, loc(a0 + q["triangulo"]["recuo_pt"], (b0 + b1) / 2), (1.0, 0.0), kpt)
    reg = reg * (1 - tri[..., None]) + np.float32(q["triangulo"]["cor"]) * tri[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    escada larga: {len(blocos) - 1} bocéis em linha suave com a sombra curta; triângulo no degrau 12")
    return out


# Pente fino pelas regras (21/10/26), Térreo, item 6: armários até o teto (seção 7: "marcenaria areia com veio, sem a
# diagonal e sem sombra de móvel baixo"). No PDF da Casa A são os quatro retângulos com diagonal da DOC_LINHAS E
# PROJEÇÕES: na cozinha, junto à parede de cima e ao lado dos eletrodomésticos; na área de serviço; no quarto do
# motorista. O motor os fez em lilás, com a diagonal desenhada, e jogou no granito a sombra de móvel baixo (6 a 8 px:
# embaixo do da cozinha, à esquerda e embaixo do do motorista; à direita do dos eletrodomésticos, um traço preto).
# Entram como os armários até o teto aprovados da Casa D (que são o tom areia do painel da Casa C com o veio do próprio
# render): o trecho liso de um deles, com o veio no comprido de cada peça (espelhado até cobrir), sem a diagonal, no
# retângulo do PDF, menos as paredes pretas do render (a da esquerda do armário da cozinha está 3,5 px mais grossa
# que no PDF e fica); contorno fino nas faces livres, como os armários da cozinha da Casa E (linha de 0,4 px na face
# do PDF; a borda escurecida da Casa D, que lá era sobre o vinílico, no granito escuro virava uma faixa intermediária
# e a borda parecia borrada). A sombra sai do granito como na
# Casa D: em cada face com piso, o perfil (por canal, mediana ao longo da face) contra o patamar logo depois dela; as
# linhas que não são sombra (o traço preto do motor ou a sobra lilás de meio px além do PDF) repetem a linha seguinte,
# já sem sombra. Na área de serviço, o braço da bancada dos tanques acima do armário (ARQ_BANCADAS: a peça branca de
# 1499,6 a 1530,8 pt) também estava lilás, como um armário: entra no quartzo da bancada, como a dos tanques.
ARMARIOS_A = {"pecas": [("cozinha, junto à parede de cima", (1666.9, 1287.6, 1922.0, 1321.6), ["baixo"]),
                        ("cozinha, ao lado dos eletrodomésticos", (1766.1, 1556.9, 1825.6, 1596.6),
                         ["cima", "direita", "esquerda"]),
                        ("área de serviço", (1499.6, 1690.1, 1530.8, 1744.0), ["cima", "direita"]),
                        ("quarto do motorista", (2250.8, 1287.6, 2284.8, 1389.7), ["esquerda", "baixo"])],
              # faces com piso: (retângulo em pt, lado, px a mais em cada ponta ao longo da face, com a sombra
              # sumindo: a do motorista desce além do canto de baixo e entra à esquerda dele)
              "pisos": [((1666.9, 1287.6, 1922.0, 1321.6), "baixo", (0, 0)),
                        ((1766.1, 1556.9, 1825.6, 1596.6), "cima", (0, 0)),
                        ((1766.1, 1556.9, 1825.6, 1596.6), "direita", (0, 0)),
                        ((1499.6, 1690.1, 1530.8, 1744.0), "direita", (0, 0)),
                        ((1499.6, 1642.5, 1530.8, 1690.1), "direita", (0, 0)),     # o braço, abaixo dos tanques
                        ((2250.8, 1287.6, 2284.8, 1389.7), "esquerda", (0, 5)),
                        ((2250.8, 1287.6, 2284.8, 1389.7), "baixo", (5, 0))],
              "bancada": (1499.6, 1605.1, 1530.8, 1690.1),
              "fonte": ("POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v4.png", (1128, 740, 1143, 797)),
              "contorno": (70, 72, 74), "larg_contorno": 0.4, "faixa": 14, "parede": 35, "traco": (0.45, 1.12)}


def armarios_teto(out):
    return armarios_ate_o_teto(out, "Terreo", ARMARIOS_A)


def armarios_ate_o_teto(out, chave, q):
    """Os armários até o teto de `q` (ARMARIOS_A, do Térreo; ARMARIOS_1PAV): a sombra de móvel baixo do motor sai do
    piso, face a face; a marcenaria areia com o veio entra no retângulo do PDF, com o contorno nas faces livres; e, se
    houver `bancada`, o braço da bancada dos tanques no quartzo."""
    from retoque_subsolo_casae import Tela, SOMBRA, QUARTZO
    import retoque_terreo_casae as T
    _, p2r = pdf_pavimento(chave)
    forma = out.shape[:2]
    orig = out.astype(np.float32)
    Y = orig.mean(axis=2)
    # parede: o preto grosso do render (a abertura tira os traços de 1 px do motor)
    parede = cv2.morphologyEx((Y < q["parede"]).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0

    def px(r):
        (a, b), (c, d) = p2r(r[0], r[1]), p2r(r[2], r[3])
        return float(a), float(b), float(c), float(d)

    ocupado = np.zeros(forma, bool)
    for r in [p[1] for p in q["pecas"]] + ([q["bancada"]] if "bancada" in q else []):
        x0, y0, x1, y1 = px(r)                              # só os px inteiros da peça: o da face é piso
        ocupado[int(np.ceil(y0)):int(np.floor(y1)), int(np.ceil(x0)):int(np.floor(x1))] = True

    # 1. a sombra do motor no granito, face a face
    D = q["faixa"]
    S = np.ones(orig.shape, np.float32)
    copias = []
    for r, lado, (e0, e1) in q["pisos"]:
        x0, y0, x1, y1 = px(r)
        # borda (coordenada da face), passo para fora e o trecho ao longo da face (a, b)
        if lado in ("cima", "baixo"):
            borda, passo, a, b = (y0, -1, x0, x1) if lado == "cima" else (y1, 1, x0, x1)
        else:
            borda, passo, a, b = (x0, -1, y0, y1) if lado == "esquerda" else (x1, 1, y0, y1)
        k0 = int(np.floor(borda))                          # a linha (ou coluna) que contém a face
        if passo == -1 and borda == k0:
            k0 -= 1
        ia, ib = int(np.floor(a)), int(np.ceil(b))
        ea, eb = ia - e0, ib + e1

        def linha(k, i0, i1):
            c = k0 + passo * k
            if lado in ("cima", "baixo"):
                return (c, slice(i0, i1))
            return (slice(i0, i1), c)

        perfil = np.full((D, 3), np.nan, np.float32)
        for k in range(D):
            ix = linha(k, ia + 2, ib - 2)
            ok = ~parede[ix] & ~ocupado[ix]
            if ok.sum() >= 3:
                perfil[k] = np.median(orig[ix][ok], axis=0)
        lum = perfil.mean(axis=1)
        # patamar: onde o piso para de clarear (cresce menos de 2% nas 3 linhas seguintes)
        dp = next((d for d in range(2, D - 3) if np.nanmax(lum[d + 1:d + 4]) - lum[d] < 0.02 * lum[d]), D - 3)
        ref = np.nanmedian(perfil[dp:dp + 3], axis=0)
        razao = perfil / ref
        valida = [k >= 1 and q["traco"][0] <= razao[k].mean() <= q["traco"][1] for k in range(D)]
        peso = np.ones(eb - ea, np.float32)                # a sombra some nas pontas estendidas
        if e0:
            peso[:e0] = (np.arange(e0) + 1) / (e0 + 1)
        if e1:
            peso[-e1:] = (np.arange(e1, 0, -1)) / (e1 + 1)
        for k in range(1, dp):
            if not valida[k]:
                continue
            s = np.minimum(razao[k], 1.0)
            f = 1 - (1 - s[None]) * peso[:, None]
            ix = linha(k, ea, eb)
            ok = ~parede[ix] & ~ocupado[ix]
            alvo = S[ix]
            alvo[ok] = np.minimum(alvo[ok], f[ok])
            S[ix] = alvo
        # linhas que não são sombra (a da face, o traço preto, a sobra lilás): a primeira válida, já sem sombra
        kv = next(k for k in range(1, D) if valida[k])
        copias += [(linha(k, ea, eb), linha(kv, ea, eb)) for k in range(kv)]
        print(f"    {lado} de {x0:.0f},{y0:.0f}: sombra de {dp} px (até {1 - np.nanmin(razao[1:dp].mean(axis=1)):.0%}), "
              f"{kv} linha(s) de borda repetida(s)")
    img = orig / S
    for alvo, fonte in copias:
        ok = ~parede[alvo] & ~ocupado[alvo]
        v = img[alvo]
        v[ok] = img[fonte][ok]
        img[alvo] = v

    # 2. o braço da bancada dos tanques, no quartzo
    if "bancada" in q:
        out = np.clip(np.round(img), 0, 255).astype(np.uint8)
        tl = Tela(out, p2r, q["bancada"])
        m = tl.ret(q["bancada"])
        tl.sombra(m, **SOMBRA)
        tl.pintar(m, QUARTZO)
        tl.contorno(m, 0.35, (150, 153, 155))
        img = tl.gravar().astype(np.float32)

    # 3. a marcenaria areia com o veio, no retângulo do PDF, menos as paredes; contorno nas faces livres
    arq, (fx0, fy0, fx1, fy1) = q["fonte"]
    madeira = cv2.imread(str(CASA.parent / arq))[fy0:fy1, fx0:fx1].astype(np.float32)     # veio vertical
    for nome, r, livres in q["pecas"]:
        x0, y0, x1, y1 = px(r)
        X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
        h, w = Y1 - Y0, X1 - X0
        t = cv2.rotate(madeira, cv2.ROTATE_90_CLOCKWISE) if w > h else madeira            # veio no comprido
        t = np.concatenate([t, t[::-1]] * (h // (2 * t.shape[0]) + 1), axis=0)[:h]
        t = np.concatenate([t, t[:, ::-1]] * (w // (2 * t.shape[1]) + 1), axis=1)[:, :w]
        cantos = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        alfa = T.poligono_aa(forma, cantos)[Y0:Y1, X0:X1] * ~parede[Y0:Y1, X0:X1]
        reg = img[Y0:Y1, X0:X1]
        img[Y0:Y1, X0:X1] = reg * (1 - alfa[..., None]) + t * alfa[..., None]
        faces = {"cima": [(x0, y0), (x1, y0)], "baixo": [(x0, y1), (x1, y1)],
                 "esquerda": [(x0, y0), (x0, y1)], "direita": [(x1, y0), (x1, y1)]}
        for lado in livres:
            a_ = T.linha_aa(forma, faces[lado], q["larg_contorno"])[..., None]
            img = img * (1 - a_) + np.float32(q["contorno"]) * a_
        print(f"    {nome}: {w}x{h} px em marcenaria areia, veio {'deitado' if w > h else 'em pé'}; "
              f"contorno: {', '.join(livres)}")
    return np.clip(np.round(img), 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), Térreo, item 7: grama na escala da referência (R1 e R4), no tom do render, como o
# item 42 do Térreo da Casa E (a opção B, escolhida lá: o desenho da grama da biblioteca, na escala, no verde do próprio
# render, com a luz larga do lugar e as sombras das plantas; texturas_escala.mascara_grama e trocar_grama). A grama do
# motor tem grão fino de carpete e manchas fora de escala.
# - Gramado: a base da Casa A tem o lote em branco (o gramado é do motor). Vale o branco da base (levada à imagem pelo
#   quadro comum), dentro do lote (do muro de cima ao de baixo; da linha preta da esquerda até onde o verde acaba, à
#   direita), em manchas grandes e verdes no render (os brancos dos móveis, dos carros e da floreira do lavabo ficam
#   de fora). O jardim interno da escada fica: a escada esmaecida está desenhada sobre a grama dele.
# - Plantas: as da Casa A são verde-sálvia, de cor perto da da grama; o que as separa é o desenho das folhas (energia
#   de 1 a 3 px em torno de 5, contra 1,7 na grama): mascara_grama com est_lim 4 e a faixa de luz da grama mais clara
#   (35 a 125). Junto às bordas do gramado (onde mascara_grama não procura planta, por causa da mistura de cor com o
#   piso) as folhas que encostam numa planta também ficam.
# - Os tracejados do motor sobre a grama ficam (o afastamento obrigatório, em traço escuro, fora até 21 px da linha do
#   PDF; e trechos da projeção da cobertura, 2 px fora da do item 4): linhas retas, finas e longas, achadas no próprio
#   render (na média de 41 px ao longo da linha, 5 abaixo da vizinhança, em trechos de 80 px ou mais e até 3 de
#   largura), a mais de 8 px da borda do gramado (junto às bordas, a sombra dos pisos e dos muros dava linhas falsas)
#   e longe das plantas; cada linha segue mais 40 px nas pontas (a média de 41 px não as alcança), na grama; os px do
#   traço voltam depois da troca. Só os escuros: as projeções do item 4 (cinza claro) são
#   desenhadas depois, por cima, e as linhas claras achadas na grama do motor eram do grão dela. Ficam seis: o
#   afastamento em x 257 e 1711 e em y 854 (dois trechos), e a cobertura em x 1388 e y 147 (contraste de 16 a 22,
#   contra 6 a 9 das falsas).
GRAMA_A = {"lote": (150, 77, 1807, 1007), "branco": 250, "mancha": 10000, "verde_min": 0.5,
           "amostra": (650, 85, 1050, 150), "est_lim": 4, "lum": (35, 125), "verde_max": 130, "borda": 6, "perto": 13,
           "traco": {"media": 41, "limiar": 5, "comprimento": 80, "largura": 3, "borda": 8, "pontas": 40}, "semente": 5}


def base_terreo(forma, chave="Terreo"):
    """A base do pavimento (a chapada da entrega), levada à imagem aprovada pelo quadro comum."""
    import json
    import rotulos_casaa as A
    cfg = json.loads(A.CONFIG.read_text())
    base = cv2.imread(str((A.CONFIG.parent / cfg["entrega"]["pasta_bases"] /
                           cfg["entrega"]["pavimentos"][chave]["base"]).resolve()))
    b2 = cv2.resize(base, (2000, round(base.shape[0] * 2000 / base.shape[1])), interpolation=cv2.INTER_NEAREST)
    return cv2.warpAffine(b2, np.float32(AFIM_QR[chave]), (forma[1], forma[0]), flags=cv2.INTER_NEAREST,
                          borderValue=(255, 255, 255))


def gramado_plantas(out):
    """O gramado (o branco da base dentro do lote, em manchas grandes e verdes), a grama e as plantas dele (item 7)."""
    from texturas_escala import mascara_grama
    q = GRAMA_A
    forma = out.shape[:2]
    b2 = base_terreo(forma)
    im = out.astype(np.float32)
    b, g, r = im[..., 0], im[..., 1], im[..., 2]
    verde = (g > r + 4) & (g > b + 12) & (im.mean(axis=2) < q["verde_max"])
    branco = cv2.morphologyEx((b2.min(axis=2) >= q["branco"]).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    x0, y0, x1, y1 = q["lote"]
    lote = np.zeros(forma, np.uint8)
    lote[y0:y1, x0:x1] = 1
    n, lab, st, _ = cv2.connectedComponentsWithStats(branco & lote, 4)
    gramado = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["mancha"]
                            and verde[lab == i].mean() >= q["verde_min"]])
    a0, b0, a1, b1 = q["amostra"]
    am = cv2.GaussianBlur(im, (0, 0), 1.5)[b0:b1, a0:a1].reshape(-1, 3)
    soma = am.sum(axis=1) + 1
    croma = (float(np.median(am[:, 0] / soma)), float(np.median(am[:, 2] / soma)))
    grama, planta = mascara_grama(out, gramado, croma=croma, est_lim=q["est_lim"], lum=q["lum"],
                                  verde_max=q["verde_max"])
    # junto às bordas do gramado: as folhas que encostam numa planta
    Y = im.mean(axis=2)
    est = cv2.GaussianBlur(np.abs(cv2.GaussianBlur(Y, (0, 0), 1.0) - cv2.GaussianBlur(Y, (0, 0), 3.0)), (0, 0), 1.5)
    dist = cv2.distanceTransform(gramado.astype(np.uint8), cv2.DIST_L2, 5)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (q["perto"], q["perto"]))
    perto = cv2.dilate(planta.astype(np.uint8), k).astype(bool)
    folhas = gramado & (dist <= q["borda"]) & perto & ((est >= q["est_lim"]) | (Y >= 120))
    planta |= folhas
    grama &= ~planta
    return gramado, grama, planta, folhas, dist, Y


def grama_escala(out):
    from texturas_escala import trocar_grama
    q = GRAMA_A
    _, p2r = pdf_pavimento("Terreo")
    forma = out.shape[:2]
    gramado, grama, planta, folhas, dist, Y = gramado_plantas(out)
    # os tracejados do motor: linhas finas, longas e escuras, achadas no render
    t = q["traco"]
    livre = gramado & (dist > t["borda"]) & ~cv2.dilate(planta.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
    D = Y - cv2.GaussianBlur(Y, (0, 0), 2.0)
    w = livre.astype(np.float32)
    traco = np.zeros(forma, bool)
    Dm = np.where(livre, -D, 0)
    for kk, eixo in (((1, t["media"]), 1), ((t["media"], 1), 0)):
        Dd = cv2.blur(Dm, kk) / np.maximum(cv2.blur(w, kk), 1e-3)
        C = Dd - 0.5 * (np.roll(Dd, 2, eixo) + np.roll(Dd, -2, eixo))
        n, lab, st, _ = cv2.connectedComponentsWithStats(((C > t["limiar"]) & livre).astype(np.uint8), 8)
        for i in range(1, n):
            comp, larg = (st[i, 3], st[i, 2]) if eixo == 1 else (st[i, 2], st[i, 3])
            if comp >= t["comprimento"] and larg <= t["largura"]:
                x, y, ww, hh = st[i, :4]
                e = t["pontas"]
                y0_, y1_, x0_, x1_ = (max(y - e, 0), y + hh + e, x, x + ww) if eixo == 1 else (y, y + hh, max(x - e, 0), x + ww + e)
                faixa = np.zeros(forma, bool)
                faixa[y0_:y1_, x0_:x1_] = True
                traco |= faixa & gramado & ~planta & (-D > t["limiar"])
                print(f"    tracejado do motor: x {x}, y {y}, {ww} x {hh} px")
    (a, b_), (c, d) = p2r(0, 0), p2r(56.69, 0)                  # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d - b_))
    orig = out.copy()
    out, npx = trocar_grama(out, grama, px_m, cor=None, semente=q["semente"])
    out[traco] = orig[traco]
    print(f"    grama da referência a {px_m:.2f} px/m em {npx} px; plantas fora: {int(planta.sum())} px "
          f"({int(folhas.sum())} junto às bordas); tracejados do motor que ficam: {int(traco.sum())} px")
    return out


# Pente fino pelas regras (21/10/26), Térreo, item 12: vegetação (seção 10; R1, R4). As folhagens do motor estão fora
# de escala (folhas de 1 a 1,3 m) e passam do lote nos quatro cantos (sobre o muro e no branco de fora) e da pedra do
# acesso. Como a opção A do Térreo da Casa E (item 53 de lá: retoque_terreo_casae.VEGETACAO, sprite_referencia e
# pousar_planta), nas manchas de planta do gramado (as do item 7, achadas na imagem aprovada), só as de vegetação de
# verdade: as cinco grandes, dos quatro cantos e do jardim lateral (as pequenas, de até 600 px, são sombra de parede
# e de degrau, e ficam):
# - folhas fora do verde: as verdes ligadas às manchas por px verdes (uma parede, um caixilho ou a água cortam a
#   ligação; a rotina de restos da Casa E pegava a borda do spa, o caixilho do escritório e um vaso dentro da sala).
#   Sobre os pisos, elas e a sombra delas (3 px em volta) e, a até 1,3 m das manchas, os fragmentos de folha e as
#   sombras soltas (na pedra, o que não é o caramelo do motor; no Bege Bahia, o cinza ou o verde, fora os traços finos
#   da base no mesmo cinza, como o contorno dos carros, e a sombra junto às paredes da casa; as linhas da DOC_LINHAS
#   ficam) viram o mesmo material da base copiado de 12 a 24 px ao lado, como na Casa E (na pedra, o caramelo, que o item 11 troca; o inpaint misturava a grama e deixava uma faixa
#   suja na curva da pedra; os px de cor rara da base, como a borda da curva, ganham o material mais próximo); fora do
#   lote, o branco de fora; sobre o muro (as linhas pretas de cima, de baixo e da esquerda,
#   de 145 a 1807,6 px), o perfil da própria linha num trecho limpo;
# - grama: a do item 7 sob as manchas, com o mesmo desenho (a mesma textura, no mesmo recorte e semente: sem emenda) e
#   a luz larga da grama em volta;
# - plantas: as árvores, arbustos e palmeiras da planta de referência (_texturas/vegetacao), no tamanho real, o maior
#   que cabe primeiro, com a copa dentro do verde: nada sai do lote nem dos pisos.
# A floreira do lavabo (JARDIM, 4,79 m²) e o jardim interno da escada não são do gramado e ficam.
VEG_A = {"mancha_min": 5000, "perto": 121, "muro": {"cima": ((66, 82), (700, 1000)), "baixo": ((1002, 1018), (700, 1100)),
                                                  "esquerda": ((139, 155), (430, 560))},
         "muro_x": (144, 1808), "muro_y": (71, 1013), "linha_lum": 232, "desvio": 15, "branco": 250, "sombra": 7,
         "escuro": 60, "alcance": 81, "pedra_base": (85, 138, 185), "bege_base": (232, 232, 232), "bege_quente": 25,
         "bege_abrir": 5, "preto": 40, "junto_parede": 13}


def copiar_material(img, alvo, base, evitar, desl=(12, 24)):
    """Os px de `alvo` recebem o mesmo material da base copiado de 12 a 24 px ao lado (como restos_fora_do_verde da
    Casa E), de px que não estão em `evitar`; o que sobra, a mediana do material com inpaint."""
    H, W = alvo.shape
    ch = base.astype(np.int32)
    chave = ch[..., 0] * 65536 + ch[..., 1] * 256 + ch[..., 2]
    # os px a refazer com cor rara na base (os traços e o antialias das bordas) ganham o material mais próximo; o branco
    # da base (gramado e fora do lote) não é piso. As fontes ficam com a cor da base delas
    ks, ns = np.unique(chave, return_counts=True)
    maior = np.isin(chave, ks[ns >= 500]) & (chave != 255 * 65536 + 255 * 256 + 255)
    _, lbl = cv2.distanceTransformWithLabels((~maior).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    chave_alvo = np.where(maior, chave, chave[maior][lbl - 1])
    a, b = desl
    passos = [(-a, 0), (0, -a), (0, a), (a, 0), (-b, 0), (0, -b), (0, b), (b, 0), (-a, -a), (-a, a), (a, -a), (a, a)]
    # fonte só de piso de verdade: nem o branco de fora do lote (a base passa 1 a 2 px do render na borda) nem o preto
    real = (img.min(axis=2) < 240) & (img.mean(axis=2) > 60)
    for c in np.unique(chave_alvo[alvo]):
        m = alvo & (chave_alvo == c)
        sao = (chave == c) & ~alvo & ~evitar & real
        if not sao.any():
            continue
        falta = m.copy()
        for dy, dx in passos:
            ys, xs = np.nonzero(falta)
            sy, sx = np.clip(ys + dy, 0, H - 1), np.clip(xs + dx, 0, W - 1)
            v = sao[sy, sx]
            img[ys[v], xs[v]] = img[sy[v], sx[v]]
            falta[ys[v], xs[v]] = False
        if falta.any():
            fundo = img.copy()
            fundo[~sao & ~(m & ~falta)] = np.median(img[sao], axis=0)
            img[falta] = cv2.inpaint(np.clip(fundo, 0, 255).astype(np.uint8), falta.astype(np.uint8), 3,
                                     cv2.INPAINT_TELEA)[falta]
    return img


def vegetacao_a(out):
    import json
    import sys
    from retoque_terreo_casae import VEGETACAO, sprite_referencia, pousar_planta
    from texturas_escala import nconv
    sys.path.insert(0, str(CASA.parent / "_texturas"))
    from texturas import textura, CONFIG as CFG_TEX
    q, ve = VEG_A, VEGETACAO
    _, p2r = pdf_pavimento("Terreo")
    forma = out.shape[:2]
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                  # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d - b))
    aprovada = cv2.imread(str(APROVADAS["Terreo"]))
    gramado, grama0, planta, _, _, _ = gramado_plantas(aprovada)
    verde = gramado.copy()
    n, lab, st, _ = cv2.connectedComponentsWithStats((planta & verde).astype(np.uint8), 8)
    planta = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["mancha_min"]])
    img = out.astype(np.float32)
    # o muro (as linhas pretas do lote) e o retângulo dele
    mx0, mx1 = q["muro_x"]
    my0, my1 = q["muro_y"]
    dentro = np.zeros(forma, bool)
    dentro[my0:my1, mx0:mx1] = True
    ap = aprovada.astype(np.float32)
    linha = np.zeros(forma, bool)
    alvo = np.full(img.shape, 255, np.float32)
    for lado, ((t0, t1), (s0, s1)) in q["muro"].items():
        if lado == "esquerda":
            perfil = np.median(ap[s0:s1, t0:t1], axis=0)               # (colunas, 3)
            for j, col in enumerate(range(t0, t1)):
                if perfil[j].mean() < q["linha_lum"]:
                    linha[my0:my1, col] = True
                    alvo[my0:my1, col] = np.minimum(alvo[my0:my1, col], perfil[j])
        else:
            perfil = np.median(ap[t0:t1, s0:s1], axis=1)               # (linhas, 3)
            for j, row in enumerate(range(t0, t1)):
                if perfil[j].mean() < q["linha_lum"]:
                    linha[row, mx0:mx1] = True
                    alvo[row, mx0:mx1] = np.minimum(alvo[row, mx0:mx1], perfil[j])
    linha &= ~verde
    # as folhas fora do verde: verdes e ligadas às manchas por px verdes
    bb, gg, rr = img[..., 0], img[..., 1], img[..., 2]
    cor_folha = (gg > rr + 4) & (gg > bb + 12)
    semente = cv2.dilate(planta.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    n, lab = cv2.connectedComponents((cor_folha & (~verde | semente)).astype(np.uint8), connectivity=8)
    folha = np.isin(lab, np.unique(lab[semente & (lab > 0)])) & ~verde
    perto = cv2.dilate(planta.astype(np.uint8), np.ones((q["perto"], q["perto"]), np.uint8)).astype(bool)
    k = q["sombra"]
    em_volta = cv2.dilate(folha.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    piso = em_volta & dentro & ~linha & ~verde & (img.mean(axis=2) > q["escuro"])
    b2 = base_terreo(forma)
    k = q["alcance"]
    alcance = cv2.dilate(planta.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & dentro & ~linha & ~verde
    lum = img.mean(axis=2)
    caramelo = (rr > gg + 18) & (gg > bb + 12) & (lum > 95)
    pg_, _ = pdf_pavimento("Terreo")
    tracos = np.zeros(forma, np.uint8)                             # as linhas da DOC_LINHAS ficam
    for d_ in pg_.get_drawings():
        if d_.get("layer") == PEDRA_A["linhas"]["camada"] and d_["type"] == "s":
            for it in d_["items"]:
                if it[0] == "l":
                    (ax, ay), (bx_, by_) = p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)
                    cv2.line(tracos, (int(round(ax)), int(round(ay))), (int(round(bx_)), int(round(by_))), 1, 1)
    tracos = cv2.dilate(tracos, np.ones((5, 5), np.uint8)).astype(bool)
    pedra_b = cv2.dilate((np.abs(b2.astype(np.int32) - np.array(q["pedra_base"])).max(axis=2) <= 6).astype(np.uint8),
                         np.ones((5, 5), np.uint8)).astype(bool)
    na_pedra = alcance & pedra_b & ~caramelo & ~tracos
    # o Bege Bahia é o piso, não os traços finos da base no mesmo cinza (o contorno dos carros): a abertura os tira
    bege_b = cv2.morphologyEx((np.abs(b2.astype(np.int32) - np.array(q["bege_base"])).max(axis=2) <= 6).astype(np.uint8),
                              cv2.MORPH_OPEN, np.ones((q["bege_abrir"],) * 2, np.uint8)).astype(bool)
    # a sombra das paredes da casa no Bege Bahia (a faixa junto à parede, embaixo dos pisantes) é da parede, e fica
    parede = cv2.morphologyEx((img.max(axis=2) < q["preto"]).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    parede = parede.astype(bool) & ~cv2.dilate(linha.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    k = q["junto_parede"]
    junto = cv2.dilate(parede.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    no_bege = alcance & bege_b & ~tracos & ~junto & (cor_folha | (rr - bb < q["bege_quente"]))
    piso |= na_pedra | no_bege
    img = copiar_material(img, piso, b2, piso | verde | cor_folha)
    muro = linha & perto & (np.abs(img - alvo).max(axis=2) > q["desvio"])
    fora = ~dentro & ~linha & perto & (img.min(axis=2) < q["branco"])
    img[muro] = alvo[muro]
    img[fora] = 255
    # grama nova sob as manchas: o desenho do item 7 (a mesma textura, recorte e semente), na luz da grama em volta
    ys, xs = np.nonzero(grama0)
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    T = cv2.GaussianBlur(textura("grama", px_m, by1 - by0, bx1 - bx0, semente=GRAMA_A["semente"]).astype(np.float32),
                         (0, 0), 0.6)
    refazer = cv2.dilate(planta.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & verde
    Lg = nconv(img, (verde & ~refazer).astype(np.float32), 1.5 * px_m)
    novo = img.copy()
    novo[by0:by1, bx0:bx1] = Lg[by0:by1, bx0:bx1] * (T / T.reshape(-1, 3).mean(axis=0))
    al = (cv2.GaussianBlur(refazer.astype(np.float32), (0, 0), 0.8) * verde)[..., None]
    img = img * (1 - al) + novo * al
    # as plantas, mancha por mancha: o maior que cabe primeiro, com a copa dentro do verde
    sombra = json.loads(CFG_TEX.read_text())["vegetacao"]["sombra"]
    dv = cv2.distanceTransform(verde.astype(np.uint8), cv2.DIST_L2, 5)
    rng = np.random.default_rng(ve["semente"])
    n, lab = cv2.connectedComponents(planta.astype(np.uint8))
    postas = []
    for i in range(1, n):
        m = lab == i
        ocup = np.zeros(forma, np.uint8)
        for nome, dm, chance in ve["catalogo"]:
            r = dm * px_m / 2
            cand = np.argwhere(m & (dv >= ve["folga_copa"] * r))
            rng.shuffle(cand)
            for y, x in cand:
                if ocup[y, x] or rng.random() > chance:
                    continue
                if any(np.hypot(x - px, y - py) < ve["afastar"] * (r + pr) for px, py, pr, _ in postas):
                    continue
                postas.append((x, y, r, nome))
                cv2.circle(ocup, (int(x), int(y)), int(r * 0.8), 1, -1)
    fundo = img.copy()
    cache = {}
    for x, y, r, nome in sorted(postas, key=lambda t: t[2]):            # as menores por baixo
        if nome not in cache:
            cache[nome] = sprite_referencia(nome, px_m)
        cor, a_, dm = cache[nome]
        esc = 2 * r / (dm * px_m) * float(rng.uniform(*ve["escala"]))
        cor_e = cv2.resize(cor, None, fx=esc, fy=esc, interpolation=cv2.INTER_LINEAR)
        a_e = cv2.resize(a_, None, fx=esc, fy=esc, interpolation=cv2.INTER_LINEAR)
        pousar_planta(fundo, cor_e, a_e, x, y, dm * px_m * esc, sombra)
    al = cv2.GaussianBlur(verde.astype(np.float32), (0, 0), 0.7)[..., None]
    img = img * (1 - al) + fundo * al
    tipos = {}
    for *_, nome in postas:
        tipos[nome] = tipos.get(nome, 0) + 1
    print(f"    folhas sobre os pisos: {int(piso.sum())} px; fora do lote: {int(fora.sum())} px; muro refeito: "
          f"{int(muro.sum())} px; grama refeita: {int(refazer.sum())} px; {len(postas)} plantas da referência em "
          f"{n - 1} manchas ({', '.join(f'{k} {v}' for k, v in sorted(tipos.items()))})")
    return np.clip(img, 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), Térreo, item 8: deck de madeira (R4: "representar a escala da madeira conforme
# modelo referência"). O motor fez as réguas num marrom avermelhado (RGB ~170, 124, 93), com as juntas fundas; a madeira
# passa à da referência (_texturas/madeira.jpg: o deck da piscina da planta de referência, RGB ~188, 157, 130, réguas
# contínuas, de juntas finas). A escala já batia: medidas por FFT, as réguas da referência têm ~20 cm (5,12 px a 26
# px/m; os "~15 cm" da nota da biblioteca e das regras estavam errados) e as do render, ~19 cm. O deck é a mancha da
# madeira da base (#AE8863, com o traço das réguas, #8C6A4A). Régua a régua, deitadas como no PDF, em 4x: cada régua do
# deck é uma régua inteira da foto (de uma junta à seguinte), sorteada, com deslocamento e espelho ao acaso, na largura
# da referência; sem quilting (as emendas dos retalhos liam como faixas atravessando as réguas). A luz larga do lugar
# e as sombras (dos degraus, da borda da piscina) ficam, como na grama (item 7).
DECK_A = {"cores": [(99, 136, 174), (74, 106, 140)], "tol": 6, "fonte": "_texturas/madeira.jpg", "fonte_px_m": 26,
          "regua_px": 5.12, "ss": 4, "sig_luz_m": 1.5, "sig_sombra_m": 0.25, "sombra_limiar": 0.93, "semente": 8}


def deck_referencia(out):
    from texturas_escala import nconv
    q = DECK_A
    _, p2r = pdf_pavimento("Terreo")
    forma = out.shape[:2]
    b2 = base_terreo(forma).astype(np.int32)
    m = np.zeros(forma, np.uint8)
    for c in q["cores"]:
        m |= (np.abs(b2 - np.array(c)).max(axis=2) <= q["tol"]).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 4)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    deck = lab == i
    x0, y0, w, h = (int(v) for v in st[i, :4])
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                  # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d - b))
    # a foto da referência na escala, em 4x, com as réguas deitadas; as juntas são os mínimos de luz, um por régua
    K = q["ss"]
    f = px_m / q["fonte_px_m"] * K
    ref = cv2.imread(str(CASA.parent / q["fonte"])).astype(np.float32)
    R = cv2.rotate(cv2.resize(ref, (round(ref.shape[1] * f), round(ref.shape[0] * f)), interpolation=cv2.INTER_CUBIC),
                   cv2.ROTATE_90_COUNTERCLOCKWISE)
    lin = R.mean(axis=(1, 2))
    P = q["regua_px"] * f
    juntas = [int(np.argmin(lin[:int(P) + 1]))]
    while juntas[-1] + 2 * P < len(lin):
        a_, b_ = int(round(juntas[-1] + P - P / 3)), int(round(juntas[-1] + P + P / 3))
        juntas.append(a_ + int(np.argmin(lin[a_:b_ + 1])))
    juntas = [j for j in juntas if j + P + 1 <= len(lin)]          # só réguas inteiras
    rng = np.random.default_rng(q["semente"])
    H, W = h * K, w * K
    T = np.zeros((H, W, 3), np.float32)
    y = -rng.uniform(0, P)
    while y < H:
        b0, b1 = int(round(y)), int(round(y + P))
        tira = R[juntas[rng.integers(len(juntas))]:][:b1 - b0]
        if rng.random() < 0.5:
            tira = tira[:, ::-1]
        off = int(rng.integers(0, R.shape[1] - W + 1))
        tira = tira[:, off:off + W]
        s0, s1 = max(0, -b0), min(b1, H) - b0
        if s1 > s0:
            T[b0 + s0:b0 + s1] = tira[s0:s1]
        y += P
    T = cv2.resize(T, (w, h), interpolation=cv2.INTER_AREA)
    # a luz larga do lugar (só a do deck) e as sombras, no tom da referência
    im = out.astype(np.float32)
    mf = deck.astype(np.float32)
    Lg = nconv(im, mf, q["sig_luz_m"] * px_m)
    Lc = nconv(im, mf, q["sig_sombra_m"] * px_m)
    sombra = np.minimum(1.0, ((Lc.mean(axis=2) + 1) / (Lg.mean(axis=2) + 1)) / q["sombra_limiar"])
    luz = Lg / Lg[deck].mean(axis=0)
    novo = im.copy()
    novo[y0:y0 + h, x0:x0 + w] = (luz * sombra[..., None])[y0:y0 + h, x0:x0 + w] * T
    alfa = (cv2.GaussianBlur(mf, (0, 0), 0.7) * mf)[..., None]
    print(f"    deck: {int(deck.sum())} px na madeira da referência, {len(juntas)} réguas da foto, a {px_m:.2f} px/m "
          f"(régua de {q['regua_px'] / q['fonte_px_m'] * 100:.0f} cm)")
    return np.clip(im * (1 - alfa) + novo * alfa, 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), Térreo, item 9: Bege Bahia como a referência (seção 18; R1; a regra de 20/10 do
# Subsolo: a foto de referência, nublada, quente, com o contraste dela). O entorno da piscina, o pátio de cima, a faixa
# junto aos brises, o hall externo, os pisantes e os degraus das escadas externas (o #E8E8E8 da base) estavam no Bege
# Bahia das varandas do 1º Pavimento, claro e rosado (RGB ~225, 209, 198). Como o item 43 do Térreo da Casa E, com os
# números de lá (retoque_terreo_casae.BEGE): os pontinhos escuros pequenos do motor viram a luz do lugar; depois, o
# desenho da biblioteca entra inteiro, na escala, no tom da foto (RGB 230, 211, 186), com a luz do lugar (as sombras
# dos móveis ficam; o que foge dela, móveis, portas e traços, fica como está). A mancha é a do #E8E8E8 da base, sem os
# riscos finos (os contornos dos carros na garagem), fechada em 5 x 5 onde o render é piso claro (as linhas da base, como
# o arco e a folha da pivotante no hall externo, a recortavam, e o arco ficava no tom antigo; a grama entre os pisantes
# não entra). O anel de 2 px que retexturizar deixa no tom antigo em volta do que foge da luz (a folha da pivotante,
# as espreguiçadeiras, os traços) vira o piso novo de perto (média só do piso novo, sem a cor do objeto). Antes das
# escadas externas (item 1), que desenham os bocéis por cima, e dos vidros (item 5), que levam o piso de cada lado para
# o vão do hall.
BEGE_A = {"cor_base": (232, 232, 232), "tol": 6, "mancha_min": 500, "fechar": 5, "claro": 150}


def bege_referencia_a(out):
    q = BEGE_A
    _, p2r = pdf_pavimento("Terreo")
    forma = out.shape[:2]
    b2 = base_terreo(forma).astype(np.int32)
    m = (np.abs(b2 - np.array(q["cor_base"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    bege = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["mancha_min"]])
    im = out.astype(np.float32)
    claro = (im.mean(axis=2) >= q["claro"]) & ~((im[..., 1] > im[..., 2] + 4) & (im[..., 1] > im[..., 0] + 12))
    k = np.ones((q["fechar"], q["fechar"]), np.uint8)
    bege |= cv2.morphologyEx(bege.astype(np.uint8), cv2.MORPH_CLOSE, k).astype(bool) & claro
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                  # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d - b))
    out, npt, npx, nanel = bege_na_referencia(out, bege, px_m)
    print(f"    Bege Bahia: {npt} px de pontinhos escuros fora; {npx} px no desenho da biblioteca, "
          f"a {px_m:.2f} px/m, no tom da foto; {nanel} px do anel em volta dos objetos")
    return out


def bege_na_referencia(out, bege, px_m):
    """O Bege Bahia da máscara no desenho da biblioteca e no tom da foto (retoque_terreo_casae.BEGE), com a luz do
    lugar: antes, os pontinhos escuros do motor viram a luz em volta; depois, o anel que retexturizar deixa em volta do
    que foge da luz vai ao piso novo de perto. Devolve a imagem e os px de pontinhos, de piso novo e de anel."""
    from retoque_terreo_casae import BEGE as e
    from texturas_escala import retexturizar, nconv
    im = out.astype(np.float32)
    pq = e["pontos"]
    mm = cv2.erode(bege.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    L = nconv(im, mm.astype(np.float32), pq["sig"])
    n, lab, st, _ = cv2.connectedComponentsWithStats((mm & ((L - im).max(axis=2) > pq["limiar"])).astype(np.uint8), 8)
    pontos = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= pq["area"]
                           and max(st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]) <= pq["lado"]])
    pontos = cv2.dilate(pontos.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & mm
    out = out.copy()
    out[pontos] = np.clip(L[pontos], 0, 255).astype(np.uint8)
    # o piso que retexturizar troca e o anel que ele deixa em volta do que foge da luz (os mesmos critérios dele)
    i2 = out.astype(np.float32)
    m2 = cv2.erode(bege.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    L2 = nconv(i2, m2.astype(np.float32), e["sig_m"] * px_m)
    foge = ((L2 - i2).max(axis=2) > 12) | ((i2 - L2).max(axis=2) > 30)
    folga = cv2.dilate(foge.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    anel = m2 & folga & ~foge
    out, npx = retexturizar(out, bege, "bege_bahia", px_m, forca=e["forca"], semente=e["semente"], sig_m=e["sig_m"],
                            cor=e["tom"], suavizar=e["suavizar"])
    novo = (m2 & ~folga).astype(np.float32)
    perto = nconv(out.astype(np.float32), novo, 1.5)
    anel &= cv2.GaussianBlur(novo, (0, 0), 1.5) >= 0.15          # só com piso novo bastante em volta
    out[anel] = np.clip(perto[anel], 0, 255).astype(np.uint8)
    return out, int(pontos.sum()), npx, int(anel.sum())


# Pente fino pelas regras (21/10/26), Térreo, item 10: granito marrom (seção 3: "desenho e tom da referência do usuário",
# base RGB ~118, 89, 69). O do render estava quase preto (RGB ~85, 62, 57), com a grade de manchas que o motor repete e
# pontos claros. Como o granito do Térreo da Casa E (retoque_terreo_casae.granito_tom, com as constantes de lá,
# GRANITO_TOM), na mancha do granito da base (#BFA79E, com os traços finos fechados e os buracos de até 20 mil px
# preenchidos: os carros do PDF são buracos maiores que os carros da R12, e o anel entre os dois ficava no tom antigo,
# escuro, em volta do terceiro carro; os carros e os móveis ficam de fora pelo peso de granito):
# 1. pontos claros pequenos do motor saem (a mediana de 13 px), longe dos traços do PDF (DOC_LINHAS E PROJEÇÕES), dos
#    cinza neutros e do que não é granito;
# 2. a grade de manchas de média escala (~3 cm a ~1 m) sai, longe de objetos e paredes (as sombras ficam);
# 3. o desenho e o tom da referência (fontes_procedurais.granito_referencia), com a luz do lugar
#    (texturas_escala.trocar_granito); os traços do PDF e os cinza neutros ficam, com a troca de tom na fração de granito
#    que têm. O peso de granito (cor e luz perto da mediana) deixa de fora os objetos: armários, inox, bancadas, carros,
#    portas, a caracol.
GRANITO_A = {"cor_base": (158, 167, 191), "tol": 6, "buraco_max": 20000}


def granito_referencia_a(out):
    from retoque_terreo_casae import GRANITO_TOM
    from texturas_escala import nconv, trocar_granito
    q = GRANITO_TOM
    pg, p2r = pdf_pavimento("Terreo")
    forma = out.shape[:2]
    b2 = base_terreo(forma).astype(np.int32)
    g = (np.abs(b2 - np.array(GRANITO_A["cor_base"])).max(axis=2) <= GRANITO_A["tol"]).astype(np.uint8)
    g = cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)   # fecha os traços finos
    n, lb, st, _ = cv2.connectedComponentsWithStats((~g).astype(np.uint8), 4)
    borda = np.unique(np.concatenate([lb[0], lb[-1], lb[:, 0], lb[:, -1]]))
    g |= np.isin(lb, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= GRANITO_A["buraco_max"] and i not in borda])
    lab = cv2.cvtColor(out, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0]
    med = np.median(lab[g], axis=0)
    dc = np.hypot(lab[..., 1] - med[1], lab[..., 2] - med[2])
    c0, c1 = q["croma"]
    l0, l1 = q["luz"]
    w = (np.clip((c1 - dc) / (c1 - c0), 0, 1) * np.clip((L - l0 * med[0]) / (0.08 * med[0]), 0, 1)
         * np.clip((l1 * med[0] - L) / (0.10 * med[0]), 0, 1) * g)
    # 1. pontos claros
    pq = q["pontos"]
    Lm = cv2.cvtColor(cv2.medianBlur(out, pq["mediana"]), cv2.COLOR_BGR2LAB)[..., 0].astype(np.float32)
    neutro = (np.hypot(lab[..., 1] - 128, lab[..., 2] - 128) < pq["neutro"]) & (L > 50)
    k = 2 * pq["folga"] + 1
    linhas = np.zeros(forma, np.uint8)                            # os traços do PDF
    for d in pg.get_drawings():
        if d.get("layer") != pq["camada"] or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] == "l":
                (ax, ay), (bx, by) = p2r(it[1].x, it[1].y), p2r(it[2].x, it[2].y)
                cv2.line(linhas, (int(round(ax)), int(round(ay))), (int(round(bx)), int(round(by))), 1, 1)
    protegido = cv2.dilate((neutro | (w < 0.05) & ~((L - Lm) > pq["limiar"]) | linhas.astype(bool)).astype(np.uint8),
                           np.ones((k, k), np.uint8)).astype(bool) | ~g
    claro = ((L - Lm) > pq["limiar"]) & g
    n, lb, st, _ = cv2.connectedComponentsWithStats(claro.astype(np.uint8), 8)
    tocam = np.unique(lb[protegido & claro])
    ok = np.zeros(n, bool)
    ok[1:] = (st[1:, 4] <= pq["area"]) & (st[1:, 2] <= pq["lado"]) & (st[1:, 3] <= pq["lado"])
    ok[tocam] = False
    pontos = ok[lb]
    al = np.maximum(cv2.GaussianBlur(cv2.dilate(pontos.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32),
                                     (0, 0), 0.7), pontos)[..., None] * g[..., None]
    fonte = cv2.medianBlur(out, pq["fonte"]).astype(np.float32)
    im = out.astype(np.float32) * (1 - al) + fonte * al
    # 2. manchas de média escala (a grade que o motor repete no granito)
    mq = q["manchas"]
    croma0 = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    puro = (g & (L > l0 * med[0]) & (L < l1 * med[0]) & (croma0 > 5)).astype(np.uint8)
    dist = cv2.distanceTransform(cv2.erode(puro, np.ones((3, 3), np.uint8)), cv2.DIST_L2, 3)
    a0, a1 = mq["longe"]
    longe = np.clip((dist - a0) / (a1 - a0), 0, 1) * puro
    pf = puro.astype(np.float32)
    curto = nconv(im, pf, mq["sig_curto"]).mean(axis=2)
    largo = nconv(im, pf, mq["sig_largo"]).mean(axis=2)
    im = im * (1 + (mq["forca"] * longe * (largo / np.maximum(curto, 1) - 1)))[..., None]
    # 3. o desenho e o tom da referência do usuário, com a luz do lugar
    linhas_d = cv2.dilate(linhas, np.ones((3, 3), np.uint8)).astype(bool)
    (a, b), (c, d_) = p2r(0, 0), p2r(56.69, 0)                 # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d_ - b))
    res, npx = trocar_granito(np.clip(im, 0, 255).astype(np.uint8), w, px_m, protegido=neutro | linhas_d)
    print(f"    granito: {int(ok.sum())} pontos claros fora ({int(pontos.sum())} px); {npx} px no granito da "
          f"referência, a {px_m:.2f} px/m (antes, mediana RGB {tuple(int(v) for v in np.median(out[g], axis=0)[::-1])})")
    return res


# Pente fino pelas regras (21/10/26), Térreo, item 11: pedra portuguesa (seção 3: "pedras de 6 a 8 cm", no desenho e
# no tom da foto de referência, escolha do usuário de 20/10: "opção 1, tom da foto"). O motor fez pedras caramelo de 12 a
# 15 cm no acesso de veículos e na área de serviço descoberta. Como o item 47 do Térreo da Casa E (com as constantes de
# lá, retoque_terreo_casae.PEDRA, e texturas_escala.trocar_pedra_portuguesa, fonte "leque"): as pedras de 7 cm
# assentadas em leque, com as juntas claras e as cores sorteadas das pedras da foto, sobre a luz relativa e as sombras
# do lugar; a franja da borda (caramelo misturado com a grama) recebe a troca de tom na fração de caramelo que tem.
# Área: a pedra da base (#B98A55, com folga), só onde o px ainda é o caramelo do motor: as plantas, os portões, as
# folhas do gás e a projeção da cobertura ficam. Por isso este é o último item do Térreo, depois das projeções. Os
# traços que o motor fez sobre o caramelo (o X tracejado da área descoberta e o afastamento) saíam com ele; entram as
# linhas da DOC_LINHAS E PROJEÇÕES do PDF por cima da pedra nova, em cinza-escuro fino, tracejadas como no PDF. A
# máscara vai para `PEDRA_A["mascara"]`: na final de 3840 px o rotulos_casaa.py a leva pelo mesmo afim da imagem e as
# pedras e as linhas são desenhadas de novo (pedra_final), para se lerem (no ajuste de 2000 px as pedras têm ~2 px).
PEDRA_A = {"cor_base": (85, 138, 185), "tol": 6, "folga": 3, "granito_base": (158, 167, 191),
           "mascara": CASA / "renders/POE642_CasaA_PH_Terreo_pedra_mascara.png",
           "linhas": {"camada": "DOC_LINHAS E PROJEÇÕES", "cor": (88, 88, 90), "larg_px": 0.5, "forca": 0.8}}


def linhas_sobre_pedra(img, mascara, p2x, escala):
    """As linhas da DOC_LINHAS E PROJEÇÕES do PDF (p2x: pt -> px da imagem) por cima da pedra (só na máscara, com 2 px
    de folga), em cinza-escuro fino; `escala`: px da imagem por px do ajuste de 2000."""
    q = PEDRA_A["linhas"]
    pg, _ = pdf_pavimento("Terreo")
    h, w = img.shape[:2]
    k = 8
    tela = np.zeros((h * k, w * k), np.uint8)
    lw = max(1, int(round(q["larg_px"] * escala * k)))
    for d in pg.get_drawings():
        if d.get("layer") != q["camada"] or d["type"] != "s":
            continue
        for it in d["items"]:
            if it[0] == "l":
                a, b = p2x(it[1].x, it[1].y), p2x(it[2].x, it[2].y)
                cv2.line(tela, (int(round(a[0] * k)), int(round(a[1] * k))), (int(round(b[0] * k)), int(round(b[1] * k))),
                         255, lw, cv2.LINE_AA)
    al = cv2.resize(tela.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    folga = max(3, int(round(2 * escala)) * 2 + 1)
    al *= cv2.dilate(mascara.astype(np.uint8), np.ones((folga, folga), np.uint8)) * q["forca"]
    out = img.astype(np.float32) * (1 - al[..., None]) + np.float32(q["cor"]) * al[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


def trocar_pedra_a(img, m, px_m, franja):
    """A pedra da foto, em leque, na máscara m (as constantes do item 47 da Casa E); com `franja`, a borda que mistura o
    caramelo do motor com a grama ou a parede recebe a troca de tom na fração de caramelo que tem (r - g)."""
    from retoque_terreo_casae import PEDRA
    from texturas_escala import trocar_pedra_portuguesa
    q = PEDRA
    antes = img.astype(np.float32)
    caramelo = np.median(antes[m], axis=0)
    img, n = trocar_pedra_portuguesa(img, m, px_m, pedra_cm=q["pedra_cm"], semente=q["semente"], junta=q["junta"],
                                     contraste=q["contraste"], fonte=q["fonte"])
    f = 0
    if franja:
        pedra = np.median(img[m].astype(np.float32), axis=0)
        borda = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~m
        rg = antes[..., 2] - antes[..., 1]
        frac = np.clip((rg + 23) / (caramelo[2] - caramelo[1] + 23), 0, 1) * borda
        img = np.clip(img.astype(np.float32) + frac[..., None] * (pedra - caramelo), 0, 255).astype(np.uint8)
        f = int((frac > 0.05).sum())
    print(f"    pedra portuguesa ({q['fonte']}): {n} px, pedras de {q['pedra_cm']:.0f} cm a {px_m:.2f} px/m; "
          f"franja da borda: {f} px")
    return img


def pedra_leque(out):
    q = PEDRA_A
    _, p2r = pdf_pavimento("Terreo")
    forma = out.shape[:2]
    b2 = base_terreo(forma).astype(np.int32)
    cm = np.abs(b2 - np.array(q["cor_base"])).max(axis=2) <= q["tol"]
    granito = np.abs(b2 - np.array(q["granito_base"])).max(axis=2) <= q["tol"]
    im = out.astype(np.int32)
    b, g, r = im[..., 0], im[..., 1], im[..., 2]
    caramelo = (r > g + 18) & (g > b + 12) & (im.mean(axis=2) > 95)
    planta = cv2.dilate(((g >= r - 8) | (im.mean(axis=2) < 90)).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    k = 2 * q["folga"] + 1
    m = cv2.dilate(cm.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & ~planta & ~granito & caramelo
    cv2.imwrite(str(q["mascara"]), m.astype(np.uint8) * 255)
    (a, b_), (c, d) = p2r(0, 0), p2r(56.69, 0)                 # 1 m na escala 1:50 = 56,69 pt
    out = trocar_pedra_a(out, m, float(np.hypot(c - a, d - b_)), franja=True)
    return linhas_sobre_pedra(out, m, p2r, 1.0)


def pedra_final(final, mascara, px_m, p2q, escala):
    """Na final de 3840 px (rotulos_casaa): as pedras e as linhas desenhadas de novo na máscara do ajuste levada ao
    quadro (p2q: pt -> px do quadro; escala: px do quadro por px do ajuste)."""
    return linhas_sobre_pedra(trocar_pedra_a(final, mascara, px_m, franja=False), mascara, p2q, escala)


# Pente fino pelas regras (21/10/26), Térreo, item 5: vidros finos (seções 4 e 18). O motor fez dois "tubos" cinza grossos
# com nós escuros (montantes):
# - entre a varanda e as salas: no PDF (ARQ_PAREDE) são quatro portas de vidro de correr, cada uma com duas folhas de
#   1,4 pt lado a lado (dois planos), de 585,8 a 1269,5 pt. O tubo sai (esquadria_limpar da Casa E: cada coluna da faixa
#   recebe o piso do seu lado, em espelho) e as folhas entram como o item 8 do pente fino do Térreo da Casa E
#   (esquadria_desenhar: o vidro claro e o contorno fino do PDF);
# - entre o hall interno e o externo: entre os dois batentes o PDF não tem vidro (é o vão da porta pivotante, com a folha
#   aberta): o tubo sai e o piso de cada lado continua; os batentes ficam.
VIDROS_A = {"desenhar": [(1655.6, 585.8, 1661.2, 1269.5)],      # pt: as quatro portas de correr da varanda
            "so_limpar": [(2198.4, 839.7, 2211.7, 1026.8)]}      # pt: o vão da pivotante, entre os batentes


def vidros_finos(out):
    import sys
    import retoque_terreo_casae as T
    sys.path.insert(0, str(CASA.parent / "_texturas"))
    from texturas import textura
    pg, p2r = pdf_pavimento("Terreo")
    px_m = p2r(56.69, 0)[0] - p2r(0, 0)[0]
    D = pg.get_drawings()
    par = [d for d in D if d.get("layer") == "ARQ_PAREDE"]
    img = out.astype(np.float32)
    n = 0
    for z in VIDROS_A["desenhar"] + VIDROS_A["so_limpar"]:
        for d in par:
            r = d["rect"]
            if d["type"] == "f" and d["fill"] and min(d["fill"]) >= 0.9 and min(r.width, r.height) <= 3.2 and \
                    z[0] - 0.5 <= r.x0 and r.x1 <= z[2] + 0.5 and z[1] - 0.5 <= r.y0 and r.y1 <= z[3] + 0.5:
                T.esquadria_limpar(img, r, p2r)
                n += 1
    for z in VIDROS_A["so_limpar"]:
        T.esquadria_limpar(img, pymupdf_rect(z), p2r)
    for z in VIDROS_A["desenhar"]:
        T.esquadria_desenhar(img, z, par, p2r, px_m, textura)
    print(f"    vidros finos: {n} folhas do PDF limpas e redesenhadas (varanda); o vão do hall sem o tubo do motor")
    return np.clip(img, 0, 255).astype(np.uint8)


def pymupdf_rect(z):
    import pymupdf
    return pymupdf.Rect(*z)


# Pente fino pelas regras (21/10/26), Térreo, item 13: sala de jantar (item 4 da conferência de 19/10). O tampo do PDF
# (ARQ_MARCENARIA, peça branca de 1717,9 a 1888,0 x 1123,2 a 1191,2 pt) é oval, de pontas em semicírculo, com 3,00 x
# 1,20 m; o do motor é retangular chanfrado e menor (2,86 x 1,08 m). As 8 cadeiras do render (3 de cada lado e uma em
# cada cabeceira) já estão onde o PDF as põe e ficam (o mapa do pente fino dizia 10; o PDF tem 8). O tampo é refeito
# no contorno do PDF, em 8x: a madeira do próprio render, estendida linha a linha em espelho (o veio corre no
# comprido), por cima da frente das cadeiras, como no PDF. O piso que o tampo velho cobria e o novo não cobre vem do
# entorno (inpaint), e a sombra curta da mesa no piso (a do motor: deslocada -3, +2 px, desfoque de 3 px, força 0,5)
# passa do contorno velho ao novo pela razão entre as duas; as cadeiras do PDF ficam como estão.
MESA_A = {"camada": "ARQ_MARCENARIA", "caixa": (1717.9, 1123.2, 1888.0, 1191.2), "cadeiras": (1690, 1095, 1915, 1222),
          "folga": 14, "nucleo": 7, "anel": (15, 31), "sombra": {"dx": -3, "dy": 2, "desfoque": 3.0, "forca": 0.5}}


def mesa_oval(out):
    q = MESA_A
    pg, p2r = pdf_pavimento("Terreo")
    forma = out.shape[:2]
    D = pg.get_drawings()
    x0, y0, x1, y1 = q["caixa"]
    tampo = next(d for d in D if d.get("layer") == q["camada"] and d["type"] == "f"
                 and max(abs(d["rect"].x0 - x0), abs(d["rect"].y0 - y0), abs(d["rect"].x1 - x1),
                         abs(d["rect"].y1 - y1)) < 1)
    al = r14_poligono(forma, np.vstack(caminhos_pdf(tampo, p2r)))
    c0, c1, c2, c3 = q["cadeiras"]
    cad = np.zeros(forma, np.float32)
    for d in D:
        r = d["rect"]
        if (d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and d["type"] == "f" and d.get("fill") and min(d["fill"]) > 0.9
                and c0 <= r.x0 and r.x1 <= c2 and c1 <= r.y0 and r.y1 <= c3):
            cad = np.maximum(cad, r14_poligono(forma, np.vstack(caminhos_pdf(d, p2r))))
    cad = cv2.dilate((cad > 0.05).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    img = out.astype(np.float32)
    ys, xs = np.nonzero(al > 0)
    g = q["folga"]
    by0, by1, bx0, bx1 = ys.min() - g, ys.max() + g + 1, xs.min() - g, xs.max() + g + 1
    # o tampo do motor: a madeira (R - B bem acima do piso), ligada ao centro
    rb = img[..., 2] - img[..., 0]
    k = q["nucleo"]
    nucleo = cv2.erode((al > 0.99).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    um = (al > 0).astype(np.uint8)
    a_, b_ = q["anel"]
    anel = (cv2.dilate(um, np.ones((b_, b_), np.uint8)) & ~cv2.dilate(um, np.ones((a_, a_), np.uint8))).astype(bool)
    anel &= ~cad
    madeira, piso = np.median(rb[nucleo]), np.median(rb[anel])
    ao = np.clip((rb - piso) / (madeira - piso), 0, 1)
    n, lab = cv2.connectedComponents((ao > 0.3).astype(np.uint8))
    cy, cx = np.argwhere(nucleo).mean(axis=0).astype(int)
    perto = cv2.dilate((lab == lab[cy, cx]).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    ao = np.where(perto, ao, 0).astype(np.float32)
    # a madeira nova: cada linha da madeira do motor estendida em espelho até a caixa; as linhas de fora, em espelho
    cheio = cv2.erode((ao > 0.97).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    T = np.zeros((by1 - by0, bx1 - bx0, 3), np.float32)
    boas = []
    for y in range(by0, by1):
        xs_ = np.nonzero(cheio[y, bx0:bx1])[0]
        if len(xs_) < 10:
            continue
        lin = img[y, bx0 + xs_.min():bx0 + xs_.max() + 1]
        esq, dir_ = xs_.min(), bx1 - bx0 - 1 - xs_.max()
        while esq > 0 or dir_ > 0:                                     # o espelho pode precisar de mais de uma volta
            e, d_ = min(esq, len(lin) - 1), min(dir_, len(lin) - 1)
            lin = np.pad(lin, ((e, d_), (0, 0)), mode="reflect")
            esq, dir_ = esq - e, dir_ - d_
        T[y - by0] = lin
        boas.append(y - by0)
    t0, t1 = min(boas), max(boas)
    for y in range(t0, t1 + 1):                                        # um veio claro pode ficar fora do núcleo
        if y not in boas:
            T[y] = T[min(boas, key=lambda b: abs(b - y))]
    for y in range(t0):
        T[y] = T[min(t1, 2 * t0 - y)]
    for y in range(t1 + 1, len(T)):
        T[y] = T[max(t0, 2 * t1 - y)]
    # o piso sem o tampo velho, e a sombra do contorno velho trocada pela do novo
    buraco = cv2.dilate((ao > 0.02).astype(np.uint8), np.ones((3, 3), np.uint8))
    piso_img = cv2.inpaint(np.clip(img, 0, 255).astype(np.uint8), buraco, 3, cv2.INPAINT_TELEA).astype(np.float32)
    s = q["sombra"]

    def sombra(m):
        return 1 - s["forca"] * cv2.GaussianBlur(np.roll(m, (s["dy"], s["dx"]), axis=(0, 1)), (0, 0), s["desfoque"])
    razao = (sombra(al) / sombra(ao))[..., None]
    fundo = np.where(buraco[..., None] > 0, piso_img, img) * razao
    fundo = np.where(cad[..., None], img, fundo)
    novo = img.copy()
    novo[by0:by1, bx0:bx1] = fundo[by0:by1, bx0:bx1]
    A = al[by0:by1, bx0:bx1, None]
    novo[by0:by1, bx0:bx1] = T * A + novo[by0:by1, bx0:bx1] * (1 - A)
    print(f"    mesa de jantar oval do PDF: {(x1 - x0) / 56.69:.2f} x {(y1 - y0) / 56.69:.2f} m (a do motor, "
          f"{int((ao > 0.5).sum())} px; a nova, {int((al > 0.5).sum())} px); 8 cadeiras do render")
    return np.clip(novo, 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), Térreo, item 14: escritório (item 6 da conferência de 19/10). No PDF (ARQ_LAYOUT
# HUMANIZAÇÃO), a mesa tem a cadeira de escritório em cima, no centro, com o assento metido sob o tampo, e as duas de
# visita embaixo; o motor pôs duas cadeiras iguais em cima e duas embaixo. As de baixo ficam. As duas de cima saem com
# as sombras: o piso volta linha a linha (o travertino corre em faixas horizontais), entre o piso logo à esquerda e
# logo à direita da mesma linha, com o grão de um trecho limpo do escritório. A cadeira de escritório entra no contorno
# do PDF, peça a peça (o assento, a faixa do encosto e os dois braços), em grafite, com o volume e o vinco das
# poltronas do estar sob a projeção e a sombra curta delas; o tampo da mesa fica por cima. O pino atrás do encosto e
# as alavancas dos lados, de 1 a 2 px nesta escala, saem (liam como as alças de uma panela).
ESCRITORIO_A = {"apagar": (1271, 201, 1332, 215), "lado": 8, "grao": (1255, 262, 1316, 276),   # px
                "mesa": (2171.5, 630.0, 2284.8, 675.3),                                          # pt
                "assento": [(2210.6, 607.6, 2228.2, 641.0), (2228.2, 607.6, 2245.7, 641.0)],
                "encosto": [(2215.6, 611.3, 2228.2, 617.2), (2228.2, 611.3, 2240.7, 617.2)],
                "bracos": [(2212.3, 618.1, 2216.9, 635.0), (2239.4, 618.1, 2244.0, 635.0)],
                "recorte": (2212.3, 611.3, 2244.0, 641.0),       # pt: o assento sem o pino do encosto e as alavancas
                "cores": {"assento": (104, 107, 112), "encosto": (78, 80, 85), "bracos": (58, 60, 64)},
                "volume": (0.72, 2.0), "vinco": (52, 54, 58, 0.3), "folga": 6,
                "sombra": [(-1.4, 1.4, 2.0, 0.30), (0, 0, 0.9, 0.14)]}


def escritorio_cadeira(out):
    q = ESCRITORIO_A
    pg, p2r = pdf_pavimento("Terreo")
    D = pg.get_drawings()
    img = out.astype(np.float32)
    # 1. as duas cadeiras do motor saem: cada linha entre o piso dos dois lados, com o grão de um trecho limpo
    x0, y0, x1, y1 = q["apagar"]
    k = q["lado"]
    esq = img[y0:y1, x0 - k:x0].mean(axis=1)
    dir_ = img[y0:y1, x1:x1 + k].mean(axis=1)
    t = ((np.arange(x0, x1) - (x0 - k / 2)) / (x1 + k / 2 - (x0 - k / 2)))[None, :, None]
    base = esq[:, None] * (1 - t) + dir_[:, None] * t
    gx0, gy0, gx1, gy1 = q["grao"]
    g = img[gy0:gy1, gx0:gx1]
    grao = g - cv2.GaussianBlur(g, (0, 0), 3)
    img[y0:y1, x0:x1] = base + grao[:y1 - y0, :x1 - x0]
    forma = out.shape[:2]
    mx0, my0, mx1, my1 = q["mesa"]
    mesa = r14_poligono(forma, [p2r(mx0, my0), p2r(mx1, my0), p2r(mx1, my1), p2r(mx0, my1)])
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - mesa[y0:y1, x0:x1, None]) + \
        out[y0:y1, x0:x1].astype(np.float32) * mesa[y0:y1, x0:x1, None]
    # 2. a cadeira de escritório do PDF, peça a peça, em 8x
    def peca(caixa):
        return next(d for d in D if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and d["type"] == "f"
                    and max(abs(d["rect"].x0 - caixa[0]), abs(d["rect"].y0 - caixa[1]), abs(d["rect"].x1 - caixa[2]),
                            abs(d["rect"].y1 - caixa[3])) < 0.3)
    partes = {n: [np.vstack(caminhos_pdf(peca(c), p2r)) for c in q[n]] for n in ("assento", "encosto", "bracos")}
    rx0, ry0, rx1, ry1 = q["recorte"]
    (ax, ay), (bx, by) = p2r(rx0, ry0), p2r(rx1, ry1)
    todos = np.vstack([c for v in partes.values() for c in v])
    f = q["folga"]
    X0, Y0 = (np.floor(todos.min(axis=0)) - f).astype(int)
    X1, Y1 = (np.ceil(todos.max(axis=0)) + f).astype(int)
    w, h, SS = X1 - X0, Y1 - Y0, SS_E

    def tela(polis, recortar=False):
        m = np.zeros((h * SS, w * SS), np.uint8)
        for c in polis:
            cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * SS))], 255, cv2.LINE_AA)
        if recortar:
            r = np.zeros_like(m)
            cv2.rectangle(r, tuple(np.int32(np.round((np.float64((ax, ay)) - (X0, Y0)) * SS))),
                          tuple(np.int32(np.round((np.float64((bx, by)) - (X0, Y0)) * SS))), 255, -1)
            m &= r
        return m

    def red(m):
        return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    livre = 1 - mesa[Y0:Y1, X0:X1]                                      # o tampo fica por cima
    reg = img[Y0:Y1, X0:X1]
    corpo = tela(partes["assento"], True) | tela(partes["encosto"] + partes["bracos"])
    for dx, dy, sig, forca in q["sombra"]:
        sm = cv2.warpAffine(corpo.astype(np.float32) / 255, np.float32([[1, 0, dx * SS], [0, 1, dy * SS]]),
                            (w * SS, h * SS))
        sm = cv2.resize(cv2.GaussianBlur(sm, (0, 0), sig * SS), (w, h), interpolation=cv2.INTER_AREA)
        reg *= (1 - forca * sm * (1 - red(corpo)) * livre)[..., None]
    v0, raio = q["volume"]
    *cor_v, larg = q["vinco"]
    for nome in ("assento", "encosto", "bracos"):
        for m in ([tela(partes[nome], nome == "assento")] if nome != "bracos" else [tela([c]) for c in partes[nome]]):
            dist = cv2.distanceTransform(m, cv2.DIST_L2, 5) / SS
            u = np.clip(dist / raio, 0, 1)
            tom = v0 + (1 - v0) * u * u * (3 - 2 * u)
            cor = cv2.resize(np.float32(q["cores"][nome])[None, None] * tom[..., None] * (m[..., None] / 255.0),
                             (w, h), interpolation=cv2.INTER_AREA)
            a = red(m) * livre
            reg = reg * (1 - a[..., None]) + cor * livre[..., None]
            kk = max(1, int(round(larg * SS)))
            borda = red(m & ~cv2.erode(m, np.ones((kk, kk), np.uint8))) * livre
            reg = reg * (1 - borda[..., None]) + np.float32(cor_v) * borda[..., None]
    img[Y0:Y1, X0:X1] = reg
    print(f"    escritório: as duas cadeiras do motor em cima da mesa saem; a cadeira de escritório do PDF entra "
          f"(x {todos[:, 0].min():.1f} a {todos[:, 0].max():.1f}, y {todos[:, 1].min():.1f} a {todos[:, 1].max():.1f} px)")
    return np.clip(np.round(img), 0, 255).astype(np.uint8)


# Pente fino pelas regras (21/10/26), Térreo, item 15: banho da varanda (item 7 da conferência de 19/10; seção 6). No
# PDF (ARQ_LOUÇAS E METAIS), o vaso fica em cima (o render já o tem) e, embaixo, o box: duas folhas de vidro de correr
# desencontradas, da parede da esquerda até 0,87 m, com o trilho tracejado; e o chuveiro de parede, na parede da
# direita (a ducha quadrada de 20 cm, o braço e a canopla). O motor pôs uma bacia branca arredondada no lugar do
# chuveiro e fez o trilho como uma faixa pontilhada, sem o vidro. Como o banho de serviço do Subsolo (item 1 de 19/10):
# - a faixa pontilhada sai: cada coluna entre o piso logo acima e logo abaixo dela, com o grão do piso abaixo;
# - a bacia sai, com a sombra: cada linha recebe o piso da mesma linha mais à esquerda (da esquerda para a direita,
#   o já refeito serve de fonte), no tom de cada coluna (a sombra junto à parede da direita fica);
# - entram as duas folhas do box (vidro_box, 1,3 pt cada, empilhadas como no Subsolo) e o chuveiro (chuveiro: a placa
#   da Casa A, o braço cromado do centro da ducha à parede e a canopla).
BANHO_VARANDA = {"faixa": (853, 812, 894, 818), "bacia": (873, 823, 894, 839), "desl": 17, "limpas": (4, 3),   # px
                 "ducha": (1463.7, 1737.3, 1474.9, 1748.5), "braco": (1469.3, 1742.2, 1490.5, 1743.6),
                 "canopla": (1490.5, 1741.2, 1491.1, 1744.6),
                 "vidros": [(1415.8, 1711.6, 1454.9, 1712.9), (1426.0, 1712.9, 1465.1, 1714.2)]}


def banho_varanda(out):
    from retoque_subsolo_casae import chuveiro, vidro_box
    q = BANHO_VARANDA
    _, p2r = pdf_pavimento("Terreo")
    img = out.astype(np.float32)
    # a faixa pontilhada: cada coluna entre a linha de cima e a de baixo, com o grão das linhas logo abaixo
    x0, y0, x1, y1 = q["faixa"]
    t = ((np.arange(y0, y1) - (y0 - 1)) / (y1 - (y0 - 1)))[:, None, None]
    base = img[y0 - 1][None, x0:x1] * (1 - t) + img[y1][None, x0:x1] * t
    g = img[y1 + 1:y1 + 1 + (y1 - y0), x0:x1]
    img[y0:y1, x0:x1] = base + (g - cv2.GaussianBlur(g, (0, 0), 2))
    # a bacia e a sombra dela: o piso da mesma linha à esquerda, no tom de cada coluna (medido nas linhas limpas)
    x0, y0, x1, y1 = q["bacia"]
    d = q["desl"]
    a, b = q["limpas"]
    limpas = np.r_[y0 - a:y0, y1:y1 + b]
    for x in range(x0, x1):
        tom = img[limpas, x].mean(axis=0) / np.maximum(img[limpas, x - d].mean(axis=0), 1)
        img[y0:y1, x] = img[y0:y1, x - d] * tom
    out = np.clip(np.round(img), 0, 255).astype(np.uint8)
    for r in q["vidros"]:
        out = vidro_box(out, p2r, r)
    out = chuveiro(out, p2r, q["ducha"], q["braco"], q["canopla"])
    (x0, y0), (x1, y1) = p2r(*q["ducha"][:2]), p2r(*q["ducha"][2:])
    print(f"    banho da varanda: a bacia e a faixa pontilhada do motor saem; o chuveiro na parede da direita (ducha em x "
          f"{x0:.1f}-{x1:.1f}, y {y0:.1f}-{y1:.1f} px) e as duas folhas de vidro do box")
    return out


# Pente fino pelas regras (21/10/26), Térreo, item 16: soleiras (R13: "representar onde o PDF tem, e não acrescentar
# onde não tem"). No PDF, a soleira é o vão da porta na espessura da parede deixado em branco, entre os batentes; onde o
# piso de um dos lados atravessa o vão, não há soleira. As 13 portas de giro do PDF (os arcos da ARQ_PAREDE, fora a
# porta camarão), conferidas uma a uma:
# - com soleira no PDF (4): o escritório e o lavabo (o vão branco da ARQ_PAREDE; no render o travertino atravessa),
#   o gás, porta de duas folhas (o vão branco; no render, o granito do item do gás de 19/10 vinha até a face de fora,
#   com a última linha do trecho copiado escura) e o jardim, para a área descoberta (o vão sem parede, branco; no
#   render, uma faixa clara e outra branca);
# - sem soleira (9): as portas da área de serviço, da despensa, do motorista, da garagem, a do banho da varanda, a do
#   WC, a pivotante do hall e as duas do outro lado da garagem, onde o piso de um dos lados atravessa o vão (no render,
#   também). Nada a mudar.
# Os quatro vãos ficam como as soleiras do Térreo da Casa E (item 52 de lá): o vão exato do PDF em Bege Bahia na
# escala (o desenho da biblioteca, no tom do item 9), com as duas faces da parede (os lados compridos) em traço cinza
# fino.
SOLEIRAS_A = {"pdf": [(2106.3, 733.3, 2114.8, 787.5),     # escritório
                      (2028.0, 715.0, 2082.2, 723.5),     # lavabo
                      (1499.6, 1778.0, 1559.2, 1786.5),   # gás (duas folhas)
                      (1491.1, 1811.2, 1499.6, 1856.5)],  # jardim, para a área descoberta
              "forca": 0.5, "linha": (150, 152, 154), "linha_px": 0.4, "ss": 8, "semente": 7}


def soleiras_a(out):
    out = desenhar_soleiras(out, "Terreo", SOLEIRAS_A)
    print(f"    {len(SOLEIRAS_A['pdf'])} soleiras de Bege Bahia nos vãos brancos do PDF (escritório, lavabo, gás e jardim), "
          f"com as faces da parede em cinza fino; nas outras 9 portas o piso atravessa o vão")
    return out


def desenhar_soleiras(out, chave, q):
    """Soleiras de Bege Bahia na escala, no tom do Bege Bahia da referência, nos vãos q["pdf"] (pt) do pavimento, com
    as faces da parede (os lados compridos) em cinza fino; o que estiver em q["fora"] (pt: folhas de vidro e batentes
    por cima do vão) fica."""
    import sys
    sys.path.insert(0, str(CASA.parent / "_texturas"))
    from texturas import textura
    from retoque_terreo_casae import BEGE
    _, p2r = pdf_pavimento(chave)
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                  # 1 m na escala 1:50 = 56,69 pt
    px_m = float(np.hypot(c - a, d - b))
    k = q["ss"]
    for r in q["pdf"]:
        (x0, y0), (x1, y1) = p2r(r[0], r[1]), p2r(r[2], r[3])
        X0, Y0, X1, Y1 = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1, int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 2
        h, w = Y1 - Y0, X1 - X0
        m = np.zeros((h * k, w * k), np.uint8)
        u0, v0, u1, v1 = (int(round((x0 - X0) * k)), int(round((y0 - Y0) * k)), int(round((x1 - X0) * k)),
                          int(round((y1 - Y0) * k)))
        m[v0:v1, u0:u1] = 255
        for fr in q.get("fora", []):
            (fa, fb), (fc, fd) = p2r(fr[0], fr[1]), p2r(fr[2], fr[3])
            m[int(round((fb - Y0) * k)):int(round((fd - Y0) * k)),
              int(round((fa - X0) * k)):int(round((fc - X0) * k))] = 0
        f = np.zeros_like(m)
        e = max(1, int(round(q["linha_px"] * k)))
        if (x1 - x0) >= (y1 - y0):                                # faces da parede: os lados compridos
            f[v0:v0 + e, u0:u1] = 255
            f[v1 - e:v1, u0:u1] = 255
        else:
            f[v0:v1, u0:u0 + e] = 255
            f[v0:v1, u1 - e:u1] = 255
        al = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        fl = cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        T = textura("bege_bahia", px_m, h, w, semente=q["semente"]).astype(np.float32)
        T = (1 + q["forca"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(BEGE["tom"])
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg = reg * (1 - al) + T * al
        reg = reg * (1 - fl) + np.float32(q["linha"]) * fl
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


# Pente fino pelas regras (21/10/26), Térreo, item 4: as projeções em tracejado bem visível, por cima (R8, R9). No PDF da
# Casa A, a da cobertura está na ARQ_CONTRAPISO, em tracejado (as notas "PROJ. COBERTURA"): o L da laje, de 1290 a 2381
# pt em x e de 511 a 1815 pt em y, com o braço de baixo indo até 1038 pt (a partir de 1344 pt), e a linha de 1290 pt
# descendo até 1860 pt. A da laje superior ("PROJ. DA LAJE SUPERIOR", na área de serviço, em volta da caracol) está na
# DOC_LINHAS E PROJEÇÕES. O motor só tinha trechos sobre a grama; no piso, no granito e na pedra não aparecia. Entram no
# traço das projeções do Térreo da Casa E (8,5 pt de traço, 4,25 de vão, 0,55 px, cinza 150, força 0,85), por cima de
# tudo, menos das paredes pretas. As do pavimento superior (os X da varanda), do pergolado e da claraboia já estão no
# render e ficam.
PROJECOES_A = {"linhas": {"cobertura, esquerda": [(1290.0, 511.0), (1290.0, 1860.0)],
                          "cobertura, em cima": [(1290.0, 511.0), (2381.0, 511.0)],
                          "cobertura, direita": [(2381.0, 511.0), (2381.0, 1815.0)],
                          "cobertura, embaixo": [(2381.0, 1815.0), (1038.0, 1815.0), (1038.0, 1344.0), (1290.0, 1344.0)],
                          "laje superior": [(1695.0, 1775.0), (1695.0, 1648.0), (1758.0, 1648.0), (1758.0, 1718.0),
                                            (1817.0, 1718.0)]},
               "traco_pt": 8.5, "vao_pt": 4.25, "larg_px": 0.55, "cor": (150, 151, 150), "forca": 0.85, "parede": 45}


def projecoes_a(out):
    q = PROJECOES_A
    _, p2r = pdf_pavimento("Terreo")
    h, w = out.shape[:2]
    SS_ = 8
    m = np.zeros((h * SS_, w * SS_), np.uint8)
    lw = max(1, int(round(q["larg_px"] * SS_)))
    n = 0
    for pts in q["linhas"].values():
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            comp = np.hypot(bx - ax, by - ay)
            t = 0.0
            while t < comp:
                t1 = min(comp, t + q["traco_pt"])
                u = p2r(ax + (bx - ax) * t / comp, ay + (by - ay) * t / comp)
                v = p2r(ax + (bx - ax) * t1 / comp, ay + (by - ay) * t1 / comp)
                cv2.line(m, (int(round(u[0] * SS_)), int(round(u[1] * SS_))),
                         (int(round(v[0] * SS_)), int(round(v[1] * SS_))), 255, lw, cv2.LINE_AA)
                n += 1
                t = t1 + q["vao_pt"]
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * q["forca"]
    a *= (out.astype(np.float32).mean(axis=2) >= q["parede"])          # nas paredes pretas o traço some
    out[:] = np.clip(out * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None], 0, 255).astype(np.uint8)
    print(f"    projeções: {len(q['linhas'])} linhas (cobertura e laje superior), {n} traços")
    return out


# A ordem da lista é a de execução: o piso do depósito sem juntas (7) e o Bege Bahia (11) vêm antes da escada (3),
# para a sombra do último espelho cair no Bege Bahia, e antes dos itens que apagam traços em espelho (4 e 6), para
# o piso de cada lado já ser o Bege Bahia.
ITENS = {"Subsolo": [("1", "banho de serviço: o chuveiro e o vidro do box", chuveiro_servico),
                     ("2", "sauna: o banco horizontal de volta", banco_sauna),
                     ("7", "depósito e circulação interna: piso contínuo, sem juntas", juntas),
                     ("11", "Bege Bahia na área de circulação, no depósito e na circulação interna", bege_bahia),
                     ("3", "escada: depois da linha de corte, os degraus na cor e textura do Subsolo", escada),
                     ("4", "portas de vidro da academia: folhas de vidro claras, não pretas", portas_academia),
                     ("5", "janelas: vão, peitoril, vidro e caixilhos do PDF, no lugar da peça cinza", janelas),
                     ("6", "circulação: sem o traço preto na borda", traco_circulacao),
                     ("8", "banhos feminino e masculino: as cubas grandes do PDF", cubas_banhos),
                     ("9", "boxes de vidro: ducha ao lado da sauna e banho feminino", boxes),
                     ("10", "divisória entre os banhos: peça clara do PDF, não parede", divisoria),
                     ("12", "banho de serviço: bancada e cuba nas medidas do PDF", bancada_servico),
                     ("13", "gramado depois do último degrau da escada do deck", gramado_escada),
                     ("pf4", "pente fino 4 (R3): portas sem os arcos (as folhas ficam)", sem_arcos_subsolo),
                     ("pf3", "pente fino 3 (R14): escada do deck com a linha nos bocéis, o trecho depois do corte "
                      "tracejado e o triângulo", escada_deck_subsolo),
                     ("pf6", "pente fino 6: Bege Bahia da referência, na escala e no tom da foto", bege_subsolo),
                     ("pf7", "pente fino 7: travertino do Térreo no hall, na sauna, na antessala e nos banhos",
                      travertino_subsolo),
                     ("pf5", "pente fino 5: porta de correr da circulação, folhas das portas de giro, janela do "
                      "depósito e vidro da sauna, finos", vidros_subsolo),
                     ("pf8", "pente fino 8 (R8): shafts brancos com o X tracejado e os retângulos da DOC_LINHAS",
                      projecoes_subsolo),
                     ("pf9", "pente fino 9 (R13): soleiras nos dois vãos brancos do PDF (academia-hall e elevador)",
                      soleiras_subsolo),
                     ("pf1", "pente fino 1 (R2): só o Subsolo; o Térreo em volta sai (o terreno é hachurado na final)",
                      so_subsolo)],
         "Terreo": [("1", "pilares da varanda e do gourmet em preto, como as paredes", pilares),
                    ("2", "sala de estar: o sofá curvo do PDF, a poltrona da direita e a mesinha", sala_estar),
                    ("rejuntes", "piso interno sem os rejuntes: o travertino contínuo", rejuntes),
                    ("8", "jardim de 4,79 m²: verde, com as três touceiras do PDF", jardim),
                    ("tanques", "área de serviço: a bancada com os dois tanques e as torneiras", tanques),
                    ("gas", "gás: piso de granito e a porta de duas folhas com os arcos", gas),
                    ("porta_jardim", "jardim: a porta para a área descoberta, com o arco", porta_jardim),
                    ("portoes", "área descoberta: os portões de correr dos dois lados", portoes),
                    ("9", "escada caracol: degraus 1 a 7 cheios, o resto esmaecido", caracol),
                    ("portas_granito", "portas no granito: folhas do PDF e arcos em cinza fino", portas_granito),
                    ("inox", "eletrodomésticos em inox (cozinha, gourmet e área de serviço)", inox),
                    ("gourmet", "bancada gourmet: área molhada, divisória, cuba e torneira", gourmet),
                    ("cozinha_pias", "bancada da cozinha em pedra: área molhada, cubas e torneiras", cozinha_pias),
                    ("3", "estar sob a projeção: 4 poltronas em X e a mesa triangular, não mesa de jantar", estar_projecao),
                    ("5", "lavabo: bancada com a cuba esculpida, vaso suspenso e a claraboia", lavabo_a),
                    ("pivotante", "porta pivotante: a folha até o hall externo e o arco pequeno", pivotante),
                    ("escada_interna", "escada interna: cheia até o corte, esmaecida depois; o jardim em volta", escada_interna),
                    ("11-12", "motorista: a cama, a bancada com a cuba, o box e o chuveiro", motorista),
                    ("carros", "garagem: os carros prata, alinhados e iguais (R12, pente fino 3; antes, uma cor por "
                     "carro e desalinhados)", carros_a),
                    ("sem_arcos", "portas sem os arcos (as folhas ficam); porta camarão sem o cinza", sem_arcos),
                    ("pf9", "pente fino 9: Bege Bahia como a referência (desenho e tom da foto, na escala)",
                     bege_referencia_a),
                    ("pf1", "pente fino 1 (R14): escadas do deck e larga com linhas e triângulo", escadas_externas_r14),
                    ("pf6", "pente fino 6: armários até o teto em marcenaria areia com veio, sem a diagonal e sem a "
                     "sombra de móvel baixo; o braço da bancada dos tanques em quartzo", armarios_teto),
                    ("pf7", "pente fino 7 (R1, R4): grama na escala da referência, no tom do render", grama_escala),
                    ("pf12", "pente fino 12: vegetação da biblioteca no tamanho real, só dentro do lote", vegetacao_a),
                    ("pf8", "pente fino 8 (R4): deck na madeira da referência, régua a régua", deck_referencia),
                    ("pf10", "pente fino 10: granito marrom no desenho e no tom da referência do usuário",
                     granito_referencia_a),
                    ("pf5", "pente fino 5: vidros finos (varanda e salas; o vão do hall sem o tubo)", vidros_finos),
                    ("pf13", "pente fino 13: mesa de jantar oval, no contorno do PDF", mesa_oval),
                    ("pf14", "pente fino 14: escritório com a cadeira de escritório do PDF em cima", escritorio_cadeira),
                    ("pf15", "pente fino 15: banho da varanda com o chuveiro e o box do PDF, sem a bacia", banho_varanda),
                    ("pf16", "pente fino 16 (R13): soleiras nos quatro vãos brancos do PDF", soleiras_a),
                    # as projeções por cima de tudo (a pedra, depois, só troca o caramelo do motor)
                    ("pf4", "pente fino 4 (R8, R9): projeções da cobertura e da laje superior em tracejado", projecoes_a),
                    ("pf11", "pente fino 11: pedra portuguesa em leque, no tom da foto (redesenhada na final)",
                     pedra_leque)],
         # 1º Pavimento: o pente fino pelas regras (21/10/26); o item 16 (o "²" dos rótulos) foi só o ciclo
         "1Pavimento": [("pf2", "pente fino 2 (R3): portas sem os arcos (as folhas ficam)", sem_arcos_1pav),
                        ("pf3", "pente fino 3 (R14 e seção 5): a escada em U e a caracol da saleta com a linha suave "
                         "nos bocéis e o triângulo da descida", escadas_1pav),
                        ("pf11", "pente fino 11 (R4): vinílico na escala, réguas de 20 cm em tons alternados, como na "
                         "Casa E (antes dos móveis dos itens 4 a 10)", vinilico_1pav),
                        ("pf12", "pente fino 12 (seção 18): Bege Bahia das quatro varandas como a referência, como o do "
                         "Térreo", bege_varandas_1pav),
                        ("pf4", "pente fino 4 (R11): guarda-roupas com cabides nos closets 3, 2, master e 1 (bege dentro, "
                         "ocre na borda, cabideiro)", guarda_roupas_1pav),
                        ("pf5", "pente fino 5 (seção 7): armários até o teto da circulação e do quarto de serviço em "
                         "marcenaria areia, sem a diagonal e sem a sombra de móvel baixo", armarios_1pav),
                        ("pf6", "pente fino 6 (seção 8): bancos estofados em bege ao pé das camas das suítes 3, 2, master "
                         "e 1, como na Casa E", bancos_1pav),
                        ("pf7", "pente fino 7: criados-mudos redondos da suíte 3, como no PDF (os do motor eram quadrados)",
                         criados_1pav),
                        ("pf8", "pente fino 8: quarto de serviço com a cama de solteiro e o criado-mudo do PDF, no lugar da "
                         "faixa com dois quadrados", quarto_servico_1pav),
                        ("pf9", "pente fino 9: banheira oval do banho master com a torneira de piso, como no PDF",
                         banheira_1pav),
                        ("pf14", "pente fino 14 (seções 4 e 18): portas de vidro de correr das suítes para as varandas, "
                         "finas, em dois planos, como no PDF (antes das cortinas, como na Casa E)", vidros_1pav),
                        ("pf10", "pente fino 10: cortinas de linho da biblioteca nas quatro suítes, com o trilho de parede "
                         "a parede", cortinas_1pav),
                        ("pf15", "pente fino 15 (R13): soleira no vão branco do PDF (porta de correr da saleta)",
                         soleiras_1pav),
                        ("pf1", "pente fino 1 (seção 11): só o 1º Pavimento; o Térreo nublado entra em volta na final",
                         so_1pavimento)]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(ITENS))
    ap.add_argument("--saida", type=Path, default=CASA / "renders")
    args = ap.parse_args()
    orig = cv2.imread(str(APROVADAS[args.pavimento]))
    out = orig.copy()
    for n, desc, f in ITENS[args.pavimento]:
        print(f"[{args.pavimento} {n}] {desc}")
        out = f(out)
    nome = args.saida / f"{APROVADAS[args.pavimento].stem}_ajustes.png"
    cv2.imwrite(str(nome), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(nome.with_name(nome.stem + "_camada.png")), np.dstack([out, alfa]))
    print(f"[fim] {nome}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

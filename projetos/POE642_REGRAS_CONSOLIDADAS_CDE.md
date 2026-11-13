# POE 642 · Regras consolidadas para as Casas C, D e E

Lista única das regras usadas no Subsolo, no Térreo e no 1º Pavimento da Casa A e no Subsolo e no Térreo da Casa B
(10 a 13/11/26), para conferir item a item nas Casas C, D e E. Entre colchetes, onde a regra nasceu. O detalhe e as
falas do usuário de cada uma estão no `POE642_REGRAS.md` (seções 4 a 13) e no `POE642_CasaA/scripts/README.md`.

## 0. Como trabalhar

- [ ] **Proposta antes, instalação depois.** A troca de mobiliário de cada pavimento vai como proposta: a planta de hoje
  ao lado das peças da biblioteca, com a recomendada marcada. Nada entra antes do OK. [A e B, todos os pavimentos]
- [ ] **Decisões pendentes, uma a uma.** Quando sobram escolhas, elas são perguntadas uma a uma, com as opções. [B Térreo]
- [ ] **Inconformidade se apresenta antes de alterar.** O que for diferente entre a proposta, o PDF e a planta vai ao
  usuário antes; só o pedido direto entra direto. Ex.: o PDF com 1 poltrona onde a proposta dizia 2; 4 banquetas no
  PDF e 5 na planta. [B Térreo]
- [ ] **Partir das escolhas da Casa A** para o mesmo ambiente: a mesma peça da biblioteca, o mesmo acabamento, o mesmo
  tamanho. [B Subsolo e Térreo]
- [ ] **Realismo sem mudar a composição nem as dimensões do PDF.** A peça segue o desenho do PDF dela (encostos,
  módulos, lado de sentar), não só o contorno. [B Térreo]
- [ ] **Peça que falta na biblioteca é gerada no Higgsfield.**
  - Vista de cima, ortográfica, fundo branco liso, na medida do PDF.
  - 4 variantes para escolher; gasta créditos, então só com o OK.
  - A escolhida é recortada do fundo e entra na pasta da biblioteca.
  - Conferir a proporção ("CUIDADO COM A PROPORÇÃO DO RECAMIER").
  - Material coerente com o uso: nada de madeira dentro d'água. [A 1º Pav, B Térreo]
- [ ] **Antes e depois de cada trecho mexido.** Depois de cada rodada, refazer final, 12K A e B, prancha, PDF da casa
  e book. O 12K vai por .zip (mais de 8000 px). [todas]
- [ ] **O script parte sempre da final e dos dados do commit de base (`ANTES_COMMIT`)**, nunca do que a rodada anterior
  gravou no disco. Na Casa B, a 2ª rodada leu os desvios já movidos e os rótulos saíram em dobro. [B Térreo]

## 1. Paredes, portas e esquadrias

- [ ] **Paredes retas.**
  - A parede é o cinza dela até a face, sem dentes, entalhes nem linhas soltas encostadas.
  - A aresta é contínua.
  - Ficam: as esquadrias, o elevador, tudo o que o PDF desenha e não é parede (folhas, louças, móveis, bancadas,
    geladeiras, grelha) e o branco de dentro (vazios, vidros, shafts).
  - [A três pavimentos; B Subsolo e Térreo]
- [ ] **Portas quina a quina, sem batentes.** A folha encosta vértice com vértice na ponta da parede, e onde ficava o
  batente entra parede. Nenhuma porta "flutuante": conferir todas, inclusive as de correr. [A e B]
- [ ] **Ponta de parede reta nos portais** sem folha desenhada, sem risco do marco. Depois de refazer um piso, as
  folhas voltam por cima. [A]
- [ ] **Esquadrias pretas, só o contorno.**
  - Boxes, portas de vidro e caixilhos de janela levam o contorno fino em preto (~0,5 px), com o vidro claro por dentro.
  - Não mudam: a madeira das portas de giro, o bronze dos brises e os chuveiros.
  - No 12K, o contorno é redesenhado na escala dele, nunca por cima das peças novas.
  - "FAÇA APENAS O CONTORNO DA ESQUADRIA EM PRETO". [A; B Térreo]
- [ ] **Folha do box reta**, de parede a parede, no eixo do PDF. [A Térreo]
- [ ] **Janela de correr com as folhas se encontrando** nos montantes, sobre a soleira. [A 1º Pav]
- [ ] **Soleira em todo vão de janela**, inclusive em cada lado da janela de canto: nunca o cinza da parede nem o
  gramado no vão. [A Térreo e 1º Pav]
- [ ] **Guarda-corpo de vidro limpo**, até o fim, encostando na parede, sem barra cinza nem pontinhos. [A]
- [ ] **Guarda-corpo nas varandas** ("Representar guarda-corpo das varandas"): a lâmina de vidro legível (3 px, as faces
  em cinza escuro, o brilho e a sombra curta), de parede a parede, em toda borda de varanda para o jardim. [C Térreo]
- [ ] **Soleira de entrada como a da Casa C.** [A Térreo]

## 2. Escadas

- [ ] **Triângulo, descrição e letra.**
  - Triângulo cheio no degrau de quem chega, com a descrição em duas linhas ("SOBE PARA O / DECK").
  - A letra **S** ou **D** centrada logo abaixo da seta, no corpo e na cor das descrições.
  - Na opção B (Kalam), a letra também na Kalam.
  - [A três pavimentos; B Subsolo e Térreo]
- [ ] **Descrição da escada acima dela**, no piso livre. [A Térreo]
- [ ] **Caracol:** a parte do pavimento de cima mais clara; o tom acompanha a descida. [A]

## 3. Vazios, shafts e tracejados

- [ ] **Shafts.**
  - Vão limpo, em branco.
  - O X tracejado de canto a canto, em cinza médio (128), ~0,8 px, antisserrilhado.
  - A borda de parede em volta limpa.
  - No 12K, o X é redesenhado na escala dele.
  - [A três pavimentos; B Térreo]
- [ ] **Jardim de inverno:** um X só, de uma diagonal à outra, interrompido em volta do rótulo; as folhas de vidro
  encostadas umas nas outras. [B Térreo]
- [ ] **Claraboia só com as linhas de fora** (cliente, Casa C: "Representar as claraboias apenas com as linhas de fora,
  sem o X no meio para ficar mais discreto. Usar um tom cinza e as linhas mais fininhas. Padronizar para as outras
  plantas que tiverem claraboia."): o retângulo do PDF tracejado, em cinza médio (128), ~0,8 px; sem X, sem o
  tracejado grosso preto ou branco, e o piso contínuo por dentro (sem o véu claro). [C Térreo; na Casa A, o lavabo
  tinha ficado só com o tracejado horizontal, a pedido do usuário: a confirmar]
- [ ] **Escadas e pisos externos (post-its do cliente no Subsolo):** o filete de pedra entre dois pisos que se
  encontram e o pilar onde o cliente marca (redondo, 0,30 m, no cinza das paredes). [B e C Subsolo]
- [ ] **Tracejado só nos vazios.** Saem o telhado, os afastamentos e as projeções. O pergolado fica fino e numa cor só
  (preto) no Térreo, e esfumaçado no 1º Pavimento. [A; B Térreo]

## 4. Banhos e louças

- [ ] **Chuveiros desenhados em planta**, nunca a foto do cromado.
  - Inox médio, chanfro, contorno fino, crivo marcado e sombra curta.
  - De parede: placa quadrada e braço até a face da parede.
  - De teto: no quadrado do PDF.
  - Nos BH de serviço e motorista: redondos de parede.
  - O chuveiro antigo vira o piso do lado; no deck, as réguas linha a linha, sem remendo.
  - [A; B Subsolo e Térreo]
- [ ] **Bacias**, no retângulo do PDF, com a caixa acoplada para a parede.
  - Carrara branca nos banhos das suítes.
  - Carrara no marrom dos vasos do Térreo no lavabo e no BH gourmet: o desenho da louça visível, nunca um bloco chapado.
  - Monte Carlo nos BH de serviço e motorista.
  - Medidas: Carrara 21,1 × 30,7 px; Monte Carlo 22,5 × 32,7 px.
  - [A; B]
- [ ] **Cubas.**
  - Banhos: a cuba esculpida de travertino na bancada inteira, com a cuba no lugar da cuba do PDF.
  - Banho master: a bancada dupla esculpida.
  - Lavabo: a cuba esculpida de poros.
  - Lavatório com blocos estreitos: a cuba esculpida estreitada (os lados viram um aro fino).
  - BH de serviço e motorista: só a louça da cuba; a bancada marrom tabaco fica ("A BANCADA DO BH. MOTORISTA É MARROM
    TABACO").
  - [A; B Térreo]
- [ ] **Bancada no tom da cuba esculpida.** [A Térreo, lavabo]
- [ ] **Louça trocada sem caixa em volta.** Por baixo entra o piso do lado, com o veio e o tom casado. Nenhum ponto
  solto nem mancha clara na louça; no 12K, o contorno liso. [A]
- [ ] **Ralo visível em cada cuba.** [A Térreo]
- [ ] **Banho se escreve BH.** nos rótulos. [A]

## 5. Cozinha, gourmet e serviço

- [ ] **Cooktop de 4 bocas da Casa A** (31 × 29 px) no meio do cooktop do PDF; o resto do de 5 bocas vira bancada. O
  granito é copiado ao longo da bancada, com a emenda e a borda em rampa, sem mancha de tom. [A Térreo; B Térreo]
- [ ] **Cubas e tanques Franke.**
  - Pia: as cubas Franke inox, com a torneira do lado da parede.
  - Gourmet: a cuba com misturador.
  - Área de serviço: os tanques Franke inox.
  - [A Térreo; B Térreo]
- [ ] **Grelha da churrasqueira da Casa A** (62 × 32 px) no meio da churrasqueira do PDF, com 4–5 px de folga, dentro
  da bancada; nunca por cima da parede. [A Térreo; B Térreo]
- [ ] **Banquetas B com ~40% do assento por baixo da bancada**, o encosto para fora. A parte sob o tampo não aparece,
  nem no 12K ("AS BANQUETAS FICAM PARCIALMENTE POR DEBAIXO DA BANCADA"). [A Térreo; B Térreo]
- [ ] **Geladeira inox** (a G2, gerada no Higgsfield), com a frente para a ilha. [B Térreo]
- [ ] **Bancadas:** em Dekton Danae na ilha, na pia e nos tanques da Casa A; as de marrom tabaco seguem mais escuras
  que o piso. [A]
- [ ] **Armários e prateleiras no tom padrão** RGB 208, 178, 156, em todas as casas. [A]
- [ ] **Sem os armários inferiores e superiores** (cliente, Casa C: "Geral: Não precisa representar os armários
  inferiores ou superiores."): o tampo das bancadas liso, sem as divisões dos módulos; ficam as bordas, as cubas, o
  cooktop e a churrasqueira. [C Térreo]
- [ ] **Geladeiras alinhadas** entre si e encostadas na parede, na mesma peça (G2). [C Térreo]
- [ ] **Painéis pivotantes** onde o cliente marca: painéis de madeira clara fechados na linha do vão, com o ponto do
  pivô (o desenho das folhas das portas). [C Térreo, gourmet]

## 6. Quartos, suítes e closets

- [ ] **Camas:** no comprimento do PDF. Na Casa B, as aprovadas (cabeceira de linho cinza, colcha matelassê, veludo
  bordô) ficam como estão. [A; B]
- [ ] **Tapete inteiro, nunca remendado.**
  - O tapete do PDF é refeito inteiro, no tom do de hoje.
  - Camas, bancos, sofá e criados voltam por cima pelo contorno do PDF, com a sombra curta.
  - O halo da IA em volta das camas sai.
  - [A 1º Pav; B Térreo]
- [ ] **Criados da Casa A.**
  - No tom da madeira das bancadas (nunca somem no piso), na forma do PDF (redondo ou retangular).
  - Com o abajur visto de cima: diâmetro 19 px nos de ~0,70 m, 17 nos menores.
  - [A 1º Pav; B Térreo]
- [ ] **Banco ao pé da cama** onde o PDF tem: o banco estofado da biblioteca, gerado no Higgsfield. [A 1º Pav]
- [ ] **Cadeira de escritório nas escrivaninhas** ("FALTOU A CADEIRA DE ESCRITORIO NAS ESCRIVANINHAS").
  - A da Casa A (34 px), com ~1/3 por baixo da mesa e o encosto para fora.
  - A cadeira antiga sai e o piso é refeito.
  - A mesa volta por cima, com a sombra curta na cadeira; no 12K, a mesa vem da saída do Topaz.
  - [B Térreo]
- [ ] **Recamier e chaises** na medida do PDF ("CUIDADO COM A PROPORÇÃO"); as mesinhas de encaixe de volta por cima.
  [B Térreo]
- [ ] **Closet:** banco estofado representado como banco estofado (o capitonê). [B Térreo]
- [ ] **Sem contorno nos mobiliários** ("Tirar o contorno dos mobiliários"): sem o traço do PDF sobre as peças (os
  estofados e as mesas da Casa B; os módulos dos armários da Casa C, o traço laranja vira o creme do armário). [B e C
  Térreo]
- [ ] **Cortinas de linho em ondas** (a C4) nos trilhos do PDF, de parede a parede; os painéis da mesma janela unidos
  num trilho só; o trilho grafite do lado do vidro. Onde a parede segue na mesma linha da janela, a cortina passa
  0,15 m além do vão de cada lado, do lado de dentro ("Pode deixar a cortina ultrapassar um pouco as laterais da
  janela."); num canto, para no vão. [B e C Térreo]

## 7. Salas e jantar

- [ ] **Sala íntima com o conjunto da Casa A.**
  - Tapete, sofá em L A (a peça girada e espelhada para o L do PDF, contando os traços finos do encosto), mesas laterais
    redondas nos círculos do PDF e poltrona A.
  - A mesa de centro do PDF fica, **em tom quente** ("TROQUE O TOM DA MESA DE CENTRO PARA UM TOM QUENTE": o caramelo
    da madeira das bancadas).
  - [A 1º Pav; B Térreo]
- [ ] **Pufe na frente da poltrona.** O retângulo do PDF na frente dela é um banco estofado tipo pufe, nunca mesa de
  madeira ("PÕE UM BANCO ESTOFADO, COMO SE FOSSE UM PUFF NA FRENTE DA POLTRONA"). [B Térreo]
- [ ] **Poltrona virada como no PDF:** o encosto do lado da faixa fina, a frente para a sala; conferir a frente do PNG
  (na biblioteca, sempre para baixo). [A; B]
- [ ] **Peça da biblioteca no tamanho e no giro de maior sobreposição com o PDF**, sem passar dele. A pegada da antiga
  volta ao piso. [A Térreo; B Térreo]
- [ ] **Nada pousado sobre outra peça:** mesas laterais e criados ao redor, nunca por cima. [A 1º Pav]
- [ ] **Jantar:** as cadeiras oliva da Casa A (30 px) no centro de cada cadeira do PDF, viradas para a mesa; a mesa por
  cima, com a sombra curta. [A Térreo; B Térreo]
- [ ] **Estar com IA (Casa B):** o mobiliário realista preservado nas silhuetas do PDF; opções A/B para escolher, e
  mistura peça a peça. [B Térreo]

## 8. Academia, sauna e área externa

- [ ] **Aparelhos da academia da biblioteca nos tamanhos da Casa A**, no meio e no sentido do símbolo do PDF:
  - esteiras 1,76 × 0,77 m;
  - bicicletas 1,23 × 0,51 m;
  - supino 1,60 × 2,04 m;
  - o que o usuário manda ficar fica (a bola);
  - o vinílico da academia é o da biblioteca.
  - [A Subsolo; B Subsolo]
- [ ] **Sauna:** bancos retos de travertino; BH da sauna com a cuba esculpida e a bacia Carrara. [B Subsolo]
- [ ] **Espreguiçadeiras.**
  - No deck: de madeira.
  - Na prainha, dentro d'água: **nunca madeira**, e sim resina/polietileno ou concreto: a de resina E4 da biblioteca
    (`02-terreo/deck-piscina/espreguicadeira-resina.png`, escolhida na Casa B), no comprimento do PDF, sem deformar,
    com o colchonete creme e o encosto de cabeça em rolo da A por cima (`espreguicadeira-resina-colchonete.png`).
  - No retângulo do PDF, com a cabeceira na parte menor do PDF.
  - [A; B Térreo]
- [ ] **Jardins internos e de inverno como o de 4,79 m² da Casa A** ("Trocar essa representação do jardim de
  inverno"): a grama no tom do gramado do lote, poucas plantas menores, os rótulos brancos, o X fino e claro; as
  floreiras com a terra e arbustos iguais. Pisantes completos onde o cliente marca ("Representar demarcação com piso").
  [B e C Térreo]
- [ ] **Gramado da Casa A em todos os Térreos:** 80% grama, poucas árvores nos cantos, arbustos baixos, até o muro.
  Jardins internos como o de 4,79 m² da Casa A. [A; B]
- [ ] **Floreira dentro do retângulo do PDF:** as plantas não passam vidro nem janela. [A 1º Pav]

## 9. Pisos refeitos (por baixo das peças trocadas)

- [ ] **Onde há gerador** (vinílico de réguas, travertino), a pegada volta pelo gerador, com as réguas contínuas. [A]
- [ ] **Sem gerador:**
  - O piso da mesma linha (ou coluna, no travertino de veio em pé), espelhado da fonte ao lado, pulando o que não é piso.
  - As emendas das tábuas em pé, ancoradas nas bordas do buraco, nunca em degrau.
  - Depois, no tom do piso em volta.
  - A beira escura junto à parede não serve de fonte.
  - [B Térreo]
- [ ] **Bege Bahia menos manchado** em todo piso, degrau, pisante, soleira e borda de Bege Bahia: as manchas da pedra
  a 45% do contraste; a luz, as sombras, o tom, as arestas e as linhas dos degraus ficam ("Já removeu manchas do bege
  Bahia como fizemos nas outras plantas?"). [A três pavimentos, 10 e 11/11; C Subsolo, 13/11]
- [ ] **O Bege Bahia na medida do Subsolo da Casa A:** o contraste das manchas no pátio igual ao da Casa A (a mediana de
  61 px e as manchas a 35% no Subsolo da Casa C), também nos degraus de pedra. O post-it "menos manchas cinzas" era do
  Bege Bahia, não do travertino (o travertino fica). [C Subsolo]
- [ ] **Floreira com caixote:** a caixa do PDF com a borda (10 cm, concreto claro), as arestas em fio, a sombra da borda
  na terra e a da caixa no piso; as plantas dentro. [C Subsolo]
- [ ] **Filete entre pisos em pedra** (Bege Bahia, um mini degrau com o fio da aresta), nunca um traço escuro. [C
  Subsolo]
- [ ] **Nunca um quadrado de outro tom** em volta da peça nova. A folga da área refeita leva junto a sombra da peça
  antiga. [A; B]

## 10. Rótulos

- [ ] **No centro do piso livre do ambiente**, fora das peças e do box. [A]
- [ ] **Alinhados em grade.** A mesma fileira com o meio na mesma linha, a mesma coluna no mesmo eixo, e os pares que o
  usuário indica valem sobre a regra geral. O que não cabe fica no seu espaço, e se diz qual. [B Subsolo e Térreo]
- [ ] **Dentro do espaço que nomeia, sem encostar** (~4 px de folga); onde não cabe, o corpo cai (0,9). Área com
  vírgula. [A Térreo]
- [ ] **Garagem** no vão entre dois carros, com folga. [A Térreo]
- [ ] **Duas letras:** A (Inter) e B (Kalam), nos mesmos lugares; o rodapé na fonte atual. [todas]
- [ ] **O rótulo movido sai inteiro do lugar antigo** (pela conta do alfa) e entra uma vez só no novo. No 12K, os
  rótulos são redesenhados nítidos pelos dados. [B Térreo]

## 11. Entregas

- [ ] **Cada planta fechada sai em:** final 3840, prancha, PDF da casa, book e dois JPGs em 12K (12288 × 8689),
  opção A e opção B. [todas]
- [ ] **4K do Nano Banana Pro:** realismo nos materiais, sem iluminação natural, com proporção e desenho travados. Da
  IA ficam só os pisos e a grama. [todas]
- [ ] **Trocas de peça no 12K sem IA nova:** a zona que mudou vem da final ampliada; as peças de PNG entram nítidas
  por cima. [A; B]

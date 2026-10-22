# POE 642 · Casa A · Térreo — prompt v32 (só a imagem base)
_13/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaA_BASE_Terreo_v6_16x9.png`, a base gerada do PDF do cliente, com o pergolado visível e o jardim da escada em verde. Sem imagem de referência.

**Da v31 para a v32 — jardim da escada pintado de verde na base:**
- **Base v6:** o jardim de 17,46 m² em volta da escada principal sai verde chapado #6E9150, com o pontilhado de jardim em verde-escuro. Ficam verdes:
  - a faixa acima do lance de cima;
  - a faixa à direita do patamar;
  - a faixa abaixo do lance de baixo;
  - o vão entre os dois lances.
- **O que não muda na base:** os degraus, o patamar, o friso branco e marrom em volta da escada, as paredes e os dois vidros. O resto da base é idêntico à v5, conferido pixel a pixel.
- **Prompt:** o jardim da escada passa a ser descrito pelo verde. Primeiro vem onde fica o hall da escada, depois como a escada faz o U, e por fim que todo verde chapado vira jardim tropical baixo, sem cobrir os degraus.

**Da v30 para a v31 — só a imagem base, sem referência:**
- **Texto:** tudo que vinha da imagem 2 agora está escrito no prompt.
  - A primeira parte descreve o visual: pedra creme quente, travertino claro, granito marrom-escuro, acesso de veículos em pedra portuguesa caramelo, gramado verde com touceiras tropicais e móveis em creme e carvalho.
  - Os jardins e os móveis continuam com a descrição completa, sem "como na imagem 2".
- **Imagem 1:** toda menção virou "a planta".
- **Conteúdo:** pisos, escadas, jardim da escada, pergolado, marcenaria, bancadas, paredes, vidros e o Avoid são os mesmos da v30.
- **Quando usar:** quando o render com referência copiar demais a imagem 2, ou para testar o motor só com a base. Sem referência, o visual pode variar mais de uma rodada para outra.

**Da v29 para a v30 — jardim em volta da escada principal:**
- **No PDF**, a escada principal em U fica dentro de um jardim de 17,46 m², entre as duas paredes de vidro. O jardim envolve a escada em quatro partes:
  - a faixa entre a parede de cima e o lance de cima;
  - a faixa mais larga à direita, entre o patamar e o vidro da direita;
  - a faixa entre o lance de baixo e a parede de baixo;
  - o vão estreito entre os dois lances.
- **No último render**, só o vão entre os lances saiu verde. As três faixas externas saíram em travertino, como se fossem piso.
- **No prompt**, o jardim da escada passa a listar as quatro partes como um único jardim verde contínuo. Só os lances e o patamar ficam em travertino.
- Entraram também:
  - no item do travertino, "escada principal (só lances e patamar)";
  - o jardim da escada na lista do que segue o texto mesmo quando a imagem 2 mostra outra coisa;
  - no Avoid, piso nas faixas de jardim em volta da escada.
- Base sem alteração: continua a v5.

**Da v28 para a v29 — pergolado na base:**
- **Base v5:** o tracejado do pergolado já estava na v4, mas quase invisível. No PDF ele vem em traço de 0,21 pt cinza, que na base de 6000 px vira menos de meio pixel. Agora ele sai cinza-escuro #4D4D4D, com 3 px e tracejado preservado. Cada viga são duas linhas tracejadas, e há também o contorno externo.
- **Resto da base:** idêntico à v4, conferido pixel a pixel. Só a região do pergolado mudou.
- **Prompt:** o pergolado ganhou um item próprio. Ele aparece só como projeção tracejada sobre o Bege Bahia e sobre parte da prainha, sem viga sólida, ripas, cobertura ou sombra.

**Da v27 para a v28 — sentido das escadas junto ao deck de madeira:**
- **Lance reto abaixo do spa:** desce do deck de madeira para o subsolo. Começa no deck, à esquerda, e desce para a direita, passando sob a borda do deck da piscina. Não liga o deck da piscina ao deck de madeira.
- **Degraus escalonados no canto de cima à esquerda do deck:** são eles que ligam o deck da piscina, descendo, ao deck de madeira.
- **Numeração do PDF do cliente:** degraus 1 a 11 no lance abaixo do spa (o 1 no subsolo, o 11 no deck de madeira) e 12 a 19 nos escalonados (o 19 no deck da piscina). O deck de madeira é um patamar intermediário entre o subsolo e o deck da piscina.
- **Seta do lance abaixo do spa:** saiu do texto. No desenho, ela segue a convenção do Archicad e aponta para o deck, ou seja, para cima. A seta de descida entra na pós-produção.
- **Imagem 2:** nas escadas, como no deck da piscina, na marcenaria e nas bancadas, o texto manda quando a imagem 2 mostrar diferente.

**Da v26 para a v27 — base nova, gerada do PDF do cliente (`bases/POE642_CasaA_BASE_Terreo_v4_16x9.png`):**
- **Todas as paredes em preto puro,** inclusive a de cima do estar, que na base antiga estava cinza e saía como vidro.
- **Cada material numa cor exata da legenda:**
  - travertino #DCD9CA, incluindo o lounge do gourmet;
  - granito #BFA79F: cozinha, bar do gourmet, área de serviço, despensa, bloco do motorista e garagem;
  - Bege Bahia #E8E8E8;
  - piscina #DFF6FE.
- **Deck de madeira** em marrom com hachura (#AE8863). No PDF ele era branco, cor que o prompt lê como jardim.
- **Acesso de veículos e corredor de serviço** em caramelo #B98A55 com padrão de hexágonos. No PDF eles usavam o mesmo cinza do deck da piscina.
- **As duas escadas que descem** (degraus escalonados junto ao deck e lance abaixo do spa) em Bege Bahia, sem faixa branca no deck.
- **Brises** como lâminas de alumínio escuro #2B2B2B. Antes saíam como faixas de vidro.
- O prompt foi ajustado a essa base: o acesso de veículos aparece caramelo com hexágonos, as escadas descem e os brises são lâminas escuras.

**Da v25 para a v26:** correções marcadas no render.
- **Paredes (vermelho):** a borda de cima do estar e o trecho curto junto ao lavabo saem como parede preta. Regra nova: na base, faixa **cinza-médio** com contorno preto também é parede e sai preta; só a faixa fina **cinza-claro** é vidro.
- **Granito Marrom Tabaco (azul):** todos estes pisos são sempre marrom-escuros, nunca pedra clara:
  - a cozinha com a ilha;
  - a faixa do bar do gourmet;
  - a área de serviço com a escada caracol;
  - o bloco do banho do motorista junto ao elevador;
  - a garagem inteira, sob os três carros.
- **Travertino (amarelo):** o lounge do gourmet junto aos brises (poltronas e banco comprido) é Travertino Romano. A v25 dizia "Bege Bahia em volta dos brises", e isso saiu do texto.

**Da v24 para a v25:** sobre o render aprovado da v24, mudam três pontos.
- **Deck da piscina em Bege Bahia:** no render ele ficou cinza-claro liso. Agora o prompt lista cada trecho do deck e manda que ele seja a mesma pedra creme das placas de pedestres. Os trechos são: acima da piscina, à direita com as espreguiçadeiras, abaixo até a varanda gourmet, em volta dos brises e as duas escadas junto ao deck de madeira.
- **Marcenaria em tom areia #CBB89E** e **bancadas em quartzo claro #ECE8E1:** os dois blocos novos determinam que nenhuma das duas fica na cor ou na textura do piso.
- **Imagem 2:** pode ser o render aprovado. Nos três pontos acima, quando a imagem 2 mostrar diferente, o texto manda.
- Para corrigir só a imagem aprovada, sem gerar de novo, use o arquivo `POE642_CasaA_PH_Terreo_v25_ajuste.md`.
- A bancada do lavabo, que era de travertino com cuba esculpida, também entra em quartzo. Me diga se quer manter o travertino só ali.

**Da v23 para a v24:** a v23 acertou a fidelidade, mas saiu vazia. A v24 mantém a estrutura de edição da v23 e devolve a riqueza:
- **Pisos:** voltam com textura fotográfica detalhada (veios, cristais, grão, juntas e brilho), com uma regra explícita: nenhum piso fica em cor chapada ou em quadrados lisos.
- **Bege Bahia e pedra portuguesa:** na v23 os dois saíram cinza, porque o motor manteve a cor da legenda. Agora o prompt diz que o cinza vira pedra bege-creme e caramelo, e que nada fica cinza.
- **Jardins:** na v23 ficaram todos brancos. Agora toda área branca não pavimentada dentro do lote vira paisagismo: grama, canteiros, arbustos, gramíneas e algumas árvores e palmeiras vistas de cima. O prompt diz onde fica cada jardim e determina que a vegetação nunca cobre a casa, a piscina, os decks nem os pisos. O contorno do lote se mantém.
- **Móveis:** continuam exatamente como representados na base, agora com materiais reais dentro das formas (linho, bouclé, carvalho, nogueira, tampos de mármore, metal preto).
- **Referência de estilo:** o render escolhido entra como 2ª imagem. O prompt diz que ele vale só pelo visual e que, onde as duas imagens diferirem, vale a base. Esse é o padrão oficial do Google de "imagem 1 = estrutura, imagem 2 = estilo".
- **Paisagismo como na referência:** gramado cobrindo toda área não pavimentada, touceiras densas de plantas tropicais nos cantos do lote e em faixas nas laterais da casa (junto à garagem, ao quarto do motorista e ao canto do escritório), e gramado aberto no resto, sem copas grandes de árvore no meio.
- **Móveis como na referência:** estofados creme e off-white, carvalho claro, cadeiras brancas no jantar e tapete redondo creme onde houver tapete desenhado.
- **Mantidos:** paredes, vidros, janelas e gradis nítidos, a parede de cima do estar e os itens do Miro.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta a editar. Ela define a geometria e o layout, e deve ser seguida exatamente.

Transforme a planta numa planta humanizada de apresentação, rica e fotorrealista, para uma residência de alto padrão. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala;
- mesmo contorno do lote;
- cada parede, janela, porta, escada, pilar, linha, móvel, carro e a piscina exatamente onde estão, com o mesmo tamanho e a mesma forma.

Muda o acabamento: pisos, água, jardins e materiais dos móveis ficam reais, sofisticados e cheios de vida. O visual geral é o de uma planta de apresentação de arquitetura bem acabada, numa paleta quente e calma: pedra creme quente, travertino claro, granito marrom-escuro, acesso em pedra portuguesa caramelo, gramado verde vivo com touceiras de plantas tropicais e o desenho limpo dos móveis em creme e carvalho.

**PISOS — materiais reais fotografados, cada um exatamente dentro do seu contorno**

Todo piso se lê como pedra ou madeira real fotografada de cima: veios, cristais ou grão visíveis, juntas reais, variação natural entre placas e o brilho suave do acabamento. Nenhum piso fica em cor chapada ou em quadrados lisos.
- **Áreas bege-acinzentadas #DCD9CA** (estar, jantar, varanda, halls, escada principal — só os lances e o patamar —, gourmet, lavabo, banho da varanda) **e o lounge do gourmet junto aos brises** (poltronas e banco comprido, entre a linha dos brises e o bar do gourmet): Travertino Romano levigado #D9CBB3.
  - marfim-bege quente, veios horizontais suaves em mel e taupe claro, poros pequenos estucados, leves mudanças de tom;
  - placas de ~60 × 120 cm em grade reta, juntas finas de 2 mm;
  - brilho acetinado.
- **Áreas malva #BFA79F:** granito Marrom Tabaco polido #4A3426. Inclui:
  - a cozinha com a ilha;
  - a faixa do bar do gourmet;
  - a área de serviço com a escada caracol;
  - a despensa;
  - o quarto e o bloco do banho do motorista junto ao elevador;
  - a garagem inteira, sob os três carros.

  Esses pisos são sempre marrom-escuros, nunca pedra clara.
  - marrom-tabaco profundo, com grão denso e graúdo de cristais pretos, âmbar-escuros e creme;
  - placas de ~60 × 60 cm, juntas escuras finas;
  - brilho de polido com reflexos suaves.
- **Áreas cinza-claro #E8E8E8** e as bordas da piscina e do spa: mármore Bege Bahia #D8CDB4.
  - pedra bege-creme quente, com manchas suaves em nuvem, pontinhos e pequenos fósseis;
  - fosco antiderrapante, placas de ~60 × 60 cm, juntas de 3 mm;
  - cobre o deck da piscina inteiro: a faixa acima da piscina, o lado direito com as espreguiçadeiras e a faixa abaixo dela até a varanda gourmet. O lounge junto aos brises não entra: ele é de travertino;
  - cobre também o hall externo, as placas de pedestres à direita (com grama nas juntas) e as duas escadas junto ao deck de madeira;
  - os degraus escalonados no canto de cima à esquerda do deck ligam o deck da piscina, descendo, ao deck de madeira;
  - o lance reto curto abaixo do spa é outra escada: desce do deck de madeira para o subsolo. O degrau de cima encosta no deck de madeira, à esquerda, e o lance desce para a direita até terminar sob a linha fina da borda do deck da piscina. Ele não liga o deck da piscina ao deck de madeira;
  - o deck da piscina tem que se ler como a mesma pedra creme das placas de pedestres, com as juntas visíveis sob a grade tracejada do pergolado;
  - nada fica cinza nem branco liso.
- **Área marrom hachurada #AE8863** em volta do spa: deck de madeira natural #9A6B47.
  - réguas de ~14 cm seguindo exatamente a hachura;
  - veio reto aparente, emendas desencontradas, frestas escuras finas, leve variação de tom entre réguas.
- **Áreas caramelo #B98A55 com padrão fino de hexágonos** (acesso de veículos, acesso à garagem e corredor de serviço descoberto entre os dois gradis): pedra portuguesa caramelo.
  - o padrão de hexágonos vira um mosaico quente de caramelo e mel, com pedrinhas irregulares cortadas à mão e juntas de areia;
  - nada fica cinza.
- **Piscina e spa azul-claro #DFF6FE:** água turquesa clara, límpida e luminosa #7CC8D4 sobre revestimento claro Barlavento, com ondulações sutis. A prainha fica mais rasa e mais clara, com borda nítida.

**JARDINS — paisagismo exuberante dentro do lote**

Dentro do lote, até os muros de divisa, toda área branca não pavimentada vira jardim paisagístico:
- gramado natural #6E9150, verde vivo e uniforme, com textura real de grama, cobrindo toda área não pavimentada;
- touceiras densas de plantas tropicais vistas de cima (palmeiras, costela-de-adão, filodendros, estrelícias, samambaias) nos cantos do lote;
- faixas de plantio nas laterais da casa: junto à garagem e ao quarto do motorista, e em volta do canto do escritório;
- a jardineira do jardim de inverno cheia de plantas tropicais;
- o jardim da escada principal, que na planta já vem pintado de **verde chapado #6E9150**:
  - **onde fica:** o hall da escada é o retângulo à direita da sala de jantar, fechado por paredes pretas em cima e embaixo e por vidros à esquerda e à direita;
  - **a escada:** é um U deitado, aberto para a esquerda, em travertino. O lance de cima vai da esquerda para a direita, o patamar fica na ponta direita e o lance de baixo volta para a esquerda;
  - **o jardim:** o verde envolve a escada em cima, à direita do patamar e embaixo, e preenche o vão estreito entre os dois lances;
  - **o que vira:** todo verde chapado vira forração tropical baixa e densa, com folhagens pequenas, samambaias e filodendros vistos de cima, exatamente dentro do contorno, sem cobrir degraus nem patamar;
  - **o que fica:** o friso fino branco e marrom em volta da escada continua nítido. Só os lances e o patamar ficam em travertino;
- no resto, gramado aberto, sem copas grandes de árvore no meio do gramado.

A vegetação fica dentro do lote e nunca cobre a casa, a piscina, os decks, os caminhos ou o acesso de veículos. O contorno do lote se mantém, e fora do lote fica papel branco limpo.

**MÓVEIS**

Ficam exatamente como estão representados na base:
- o mesmo desenho refinado, com cada contorno, almofada e detalhe;
- mesma posição, tamanho e orientação;
- sem simplificar, trocar ou reestilizar.

Dentro das formas que já existem, ganham materiais reais de alto padrão numa paleta calma: estofados creme e off-white em linho e bouclé, mesas de carvalho claro, cadeiras brancas no jantar, detalhes em metal preto e tapete redondo creme onde houver tapete desenhado.

**MARCENARIA E BANCADAS — distintas do piso**
- **Marcenaria:** toda a marcenaria embutida fica em tom areia quente e fosco #CBB89E, laqueado liso, bem distinto do piso em volta. Isso inclui os armários da cozinha, o painel alto do estar, as estantes, as bases do bar e da churrasqueira do gourmet e os armários da área de serviço.
- **Bancadas:** todos os tampos ficam em quartzo claro polido #ECE8E1, com pontilhado fino e sutil, mais claros que os pisos. Isso inclui a ilha e as bancadas da cozinha, o bar e a churrasqueira do gourmet e as bancadas da área de serviço e dos banheiros.
- Marcenaria e bancadas nunca pegam a cor ou a textura do piso onde estão.

**PAREDES, VIDROS, JANELAS, GRADIS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, bordas retas e nítidas, espessura como desenhada; alvenaria fechada, sem TV.
  - Toda faixa de parede da planta vira preto sólido, seja preta ou **cinza-médio #5B5B5B com contorno preto**. Só as faixas finas **cinza-claro #D6D6D3** são vidro.
  - A borda de cima do estar é uma parede preta contínua, com uma janela curta no canto superior esquerdo. O trecho curto de parede no alto, entre o estar e o lavabo, também é parede preta.
- **Paredes de vidro e janelas:** cada uma exatamente onde a base mostra, como linha fina de vidro cinza-claro #D6D6D3 entre duas linhas finas de caixilho preto, nítida e contínua.
- **Gradis do corredor de serviço:** barras finas de metal preto entre pequenos postes quadrados; linha escura pontilhada fina e nítida, vazada.
- **Pergolado sobre o deck da piscina:** aparece só como projeção. A grade tracejada cinza-escura, com cada viga em duas linhas tracejadas e o contorno externo, fica exatamente como desenhada, nítida, sobre o Bege Bahia e sobre parte da prainha. Sem vigas sólidas, ripas, cobertura ou sombra.
- **Continuam como desenhados:** os arcos das portas, a fileira de lâminas escuras #2B2B2B dos brises com seus arcos finos, na borda esquerda do lounge do gourmet (lâminas finas de alumínio escuro, não vidro), os X tracejados dos vazios e os muros cinza-escuros.
- **Pilares:** os pontos rosa e o quadrado rosa viram pilares pretos sólidos.
- **Linhas removidas:** as linhas finas e longas tracejadas de recuo e as curvas de nível.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara, uniforme, com cor de luz do dia natural e sem sombra projetada de nenhum tipo. Os materiais se leem por textura, cor e brilho. Cores vivas e naturais, sem texto.

**Evitar:**
- redesenhar, mover, acrescentar ou remover parede, janela, porta ou móvel;
- mudar a forma do lote;
- vegetação em cima da casa, da piscina, dos decks ou dos pisos;
- cinza sobrando nas áreas de Bege Bahia ou no acesso de veículos;
- piso em cor chapada ou em quadrados lisos;
- marcenaria ou bancada na cor ou textura do piso;
- piso claro na cozinha, no bar do gourmet, na área de serviço, no banho do motorista ou na garagem;
- Bege Bahia no lounge do gourmet junto aos brises;
- parede cinza ou em linha fina no alto do estar;
- pavimento cinza ou branco liso em volta da piscina;
- o lance abaixo do spa emendado no deck da piscina, como se ligasse o deck da piscina ao deck de madeira;
- linhas de vidro, janelas ou gradis borrados ou interrompidos;
- pergolado em vigas sólidas ou ripas, ou sumindo;
- piso, travertino ou verde chapado no jardim da escada principal;
- móveis simplificados ou reestilizados;
- azul fora da piscina e do spa;
- sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the floor plan to edit. It defines the geometry and layout, and you follow it exactly.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) for a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, the same lot outline, and every wall, window, door, stair, column, line, furniture piece, car and the pool exactly where they are, at the same size and shape. What changes is the finish: floors, water, gardens and furniture materials become real, high-end and full of life. The overall look is a polished architectural presentation plan in a warm, calm palette: warm cream stone, light travertine, dark brown granite, a caramel cobblestone driveway, a vivid green lawn with clusters of tropical plants, and clean cream-and-oak furniture.

FLOORS — real photographed materials, each exactly inside its own outline
Every floor reads as real stone or wood photographed from above: visible veining, crystals or grain, real slab joints, natural variation from slab to slab, and the soft sheen of its finish. No floor stays a flat colour or a pattern of plain squares.
- Greige #DCD9CA areas (living, dining, veranda, halls, the main stair — its flights and landing only —, gourmet, powder room, veranda bathroom) and the gourmet lounge beside the brise blades (the area with the armchairs and the long bench, between the brise line and the gourmet bar): honed Travertino Romano #D9CBB3 — warm ivory-beige with soft horizontal veining in honey and light taupe, tiny filled pores and gentle tone shifts; slabs about 60 × 120 cm in a straight grid, fine 2 mm joints; satin sheen.
- Mauve #BFA79F areas: polished Marrom Tabaco granite #4A3426 — the kitchen with the island, the strip of the gourmet bar, the laundry and service area with the spiral service stair, the pantry, the driver's room and the driver's bathroom block next to the elevator, and the whole garage floor under the three cars. Deep tobacco brown with a dense, coarse grain of black, dark-amber and cream crystals; slabs about 60 × 60 cm, fine dark joints; glossy polished sheen with soft reflections. These floors are always deep brown, never light stone.
- Light grey #E8E8E8 areas and the pool and spa copings: Bege Bahia marble #D8CDB4 — warm cream-beige stone with soft cloudy tones, fine speckles and small fossil marks; matte non-slip; slabs about 60 × 60 cm with 3 mm joints. This covers the whole pool deck — the paving above the pool, on its right where the two sun loungers stand, and below it down to the gourmet veranda (the gourmet lounge beside the brise blades is travertine, not Bege Bahia) — plus the external hall, the stepping slabs on the right (lawn in their joints) and both stairs beside the wooden deck. The staggered steps at the top-left corner of the wooden deck lead down from the pool deck to the wooden deck. The short straight flight below the spa is a separate stair that goes down from the wooden deck to the basement: its top step meets the wooden deck on its left, and it descends toward the right, ending under the thin edge line of the pool deck; it does not connect the pool deck to the wooden deck. The pool deck reads as the same cream-beige stone as the stepping slabs, with visible slab joints under the dashed pergola grid. Nothing stays grey or plain white.
- Brown hatched #AE8863 area around the spa: natural hardwood deck #9A6B47 — boards about 14 cm wide running exactly along the hatching, visible straight grain, staggered joints, thin dark gaps, slight tone variation between boards.
- Caramel #B98A55 areas with a fine hexagon pattern (driveway, garage access and the uncovered service passage between the two railings): caramel Portuguese cobblestone (pedra portuguesa) — the hexagon pattern becomes a warm caramel-and-honey mosaic of small irregular hand-cut stones with sand joints; never grey.
- Pale blue #DFF6FE pool and spa: clear, bright light-turquoise water #7CC8D4 over light Barlavento tiles, with subtle surface ripples; the wet deck (prainha) shallower and lighter, with a crisp edge.

GARDENS — lush landscaping inside the lot
Inside the lot, up to the boundary walls, every unpaved white area becomes a landscaped garden: a lush, evenly green natural lawn #6E9150 with real grass texture covers every unpaved area; dense clusters of tropical plants seen from above (palms, monstera, philodendron, bird-of-paradise, ferns) fill the lot corners and run as planting strips along the sides of the house — beside the garage and the driver's room, and around the home-office corner; the winter-garden planter is full of tropical plants; the flat green #6E9150 areas in the stair hall are the indoor garden of the main stair. The stair hall is the rectangle just right of the dining room, closed by black walls at the top and bottom and by glass walls on the left and right. Inside it, the travertine stair is a U lying on its side and open to the left: the upper flight runs from left to right, the landing fills the right end, and the lower flight runs back to the left. The green wraps around it — above the upper flight, to the right of the landing and below the lower flight — and fills the narrow slot between the two flights. Every flat green area becomes lush, low, dense tropical groundcover (small leaves, ferns and philodendrons seen from above), exactly inside its outline and never over the treads or the landing; the thin white-and-brown edge line around the stair stays crisp, and only the flights and the landing are travertine; elsewhere the lawn stays open, with no large tree canopies over it. Vegetation stays inside the lot and never covers the house, the pool, the decks, the paths or the driveway; the lot outline keeps its shape; outside the lot stays clean white paper.

FURNITURE
Kept exactly as represented in the plan — the same refined drawings with every outline, cushion and detail, the same position, size and orientation; not simplified, replaced or restyled. Inside the existing shapes, give them real high-end materials in a calm palette: cream and off-white linen and bouclé upholstery, light natural oak tables, white dining chairs, black metal details, and a round cream rug where a rug is drawn.

JOINERY AND COUNTERTOPS — distinct from the floors
- Joinery: all built-in joinery — kitchen cabinets, the tall cabinetry panel in the living room, shelving, the bases of the gourmet bar and barbecue counter, and the laundry cabinets — in a matte warm sand tone #CBB89E, smooth lacquered finish, clearly distinct from the floor around it.
- Countertops: all countertops — the kitchen island and counters, the gourmet bar and barbecue counter, and the laundry and bathroom counters — in light polished quartz #ECE8E1 with a fine, subtle speckle, clearly lighter than the floors.
- Joinery and countertops never take the colour or texture of the floor they stand on.

WALLS, GLASS, WINDOWS, RAILINGS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; closed masonry with no TV. Every wall band in the plan — solid black, or medium grey #5B5B5B outlined in black — renders as solid black; only the thin pale-grey #D6D6D3 strips are glass. The top edge of the living room is a continuous black wall with one short window in its top-left corner, and the short wall piece at the top between the living room and the powder room is solid black wall too.
- Glass walls and windows: every one exactly where the plan shows it, as a thin pale-grey glass line #D6D6D3 between two thin black aluminium frame lines — crisp and continuous.
- Service-passage railings (gradil): slim black metal bars between small square posts, read as a crisp thin dark dotted line, see-through.
- Pergola over the pool deck: shown only as its projection — the dark grey dashed grid (each beam drawn as a pair of dashed lines, plus the dashed outer frame) stays exactly as drawn, crisp and dashed, over the Bege Bahia paving and part of the wet deck; no solid beams, slats, roof or shadows.
- Door arcs, the row of dark #2B2B2B brise blades with their thin swing arcs on the left edge of the gourmet lounge (slim dark aluminium blades, not glass), the dashed void X's and the dark grey boundary walls stay as drawn. Pink column dots and the pink square become solid black columns. The long thin dashed setback lines and the faint terrain contours are removed.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours; no text.

Avoid: redrawing, moving, adding or removing any wall, window, door or furniture piece; changing the lot shape; vegetation over the house, the pool, the decks or the paving; any grey left on the Bege Bahia areas or the driveway; flat colour fills or plain-square floors; joinery or countertops in the floor colour or texture; light floors in the kitchen, gourmet bar strip, laundry, driver's bathroom or garage; Bege Bahia in the gourmet lounge beside the brises; a grey or thin-line wall at the top of the living room; grey or plain white paving around the pool; the flight below the spa merging into the pool deck; blurred or broken glass lines, windows or railings; a pergola drawn as solid beams or slats, or missing; floor, travertine or flat colour on the green stair garden; simplified or restyled furniture; blue outside the pool and spa; shadows; perspective; text.
```

# POE 642 · Casa E · Térreo — prompt v1 (só a imagem base)
_15/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png`.
- **Origem:** foi gerada do PDF do cliente (`642 - TÉRREO - CASA E.pdf`), na mesma folha e no mesmo enquadramento das Casas A, B, C e D.
- **Texturas:** a base já traz a prévia dos pisos, do gramado, da floreira, da água, da pedra portuguesa, do bronze e do louceiro. Granito, travertino, Bege Bahia, grama, água e floreira vêm dos renders aprovados das outras casas; a pedra portuguesa caramelo e o bronze fosco foram gerados por código (`fontes_procedurais.py`). O prompt manda manter cada material e só torná-lo fotorrealista.

**Pisos e áreas externas (definidos por você em 15/10/26):**
- **Granito Marrom Tabaco:** todo o rosa do PDF.
  - cozinha, área de serviço e área de serviço descoberta, DCE, despensa, adega e CPD;
  - área gourmet, circulação gourmet, BH gourmet e lavabo gourmet;
  - garagem, com os 3 carros do PDF, e a faixa de circulação ao longo do muro de cima.
- **Travertino:** todo o oliva do PDF: living, jantar, circulações internas, escritório, lavabo e hall de entrada.
- **Bege Bahia:**
  - o cinza do PDF: varanda, deck em volta da piscina, os degraus largos à esquerda e a faixa à direita do hall;
  - os pisantes embaixo à direita;
  - o WC DCE 1 (um cinza um pouco diferente no PDF).
- **Pedra portuguesa caramelo:** o acesso de veículos curvo à direita, sem os hexágonos do PDF.
- **Pilares:** os quatro, em preto, como as paredes.
- **Jardim interno:** o retângulo abaixo da escada interna.
- **Louceiro:** a faixa acima da escada interna, armário até o teto em marcenaria areia (com a diagonal do PDF).
- **Bancos em bronze fosco:** o L embaixo à esquerda e o retângulo estreito entre a piscina e os degraus.
- **Entorno:** grama com paisagismo dentro do lote.

**Base:**
- **Piscina:** sem as faixas de vidro que o gerador criava em volta da água (a lição das Casas C e D).
- **Escadas:** as duas ficam no tom do PDF, que na prévia de texturas lê como travertino.

**Lições das Casas A a D aplicadas:**
- escala existente em destaque, com a posição medida na base;
- ambientes descritos por posição;
- "nada é acrescentado";
- luz chapada, sem sombra;
- armário até o teto (linha diagonal) chapado, sem sombra de móvel baixo;
- vegetação só no gramado e na floreira, nunca sobre a casa, a piscina, o deck, os pisantes ou o acesso;
- carros só na garagem;
- louças, cubas e cooktops exatamente como desenhados.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta do térreo a editar. Ela define a geometria, o layout e os materiais, e deve ser seguida exatamente.

**Antes de tudo: mantenha a escala existente.** A planta sai exatamente do mesmo tamanho e no mesmo lugar da imagem de entrada, sem aproximar, recortar nem centralizar.

Transforme a planta numa planta humanizada de apresentação do **térreo** de uma residência de alto padrão, rica e fotorrealista. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala, com o mesmo contorno do lote;
- cada parede, pilar, vidro, porta, escada, linha, móvel, louça, carro e a piscina exatamente onde estão, com o mesmo tamanho e a mesma forma;
- nada é acrescentado: nenhum ambiente, parede, porta, escada, móvel, carro ou objeto novo.

Os pisos, o gramado, a floreira, a água, a pedra portuguesa, os bancos de bronze e o louceiro já aparecem na planta com o material final. Cada um mantém o material, a cor e a direção das réguas e dos veios, e só ganha acabamento fotorrealista, com juntas reais e brilho sutil.

**ESCALA E ENQUADRAMENTO:** mantenha a escala existente.
- A planta fica exatamente na mesma posição e com o mesmo tamanho na imagem, com a mesma margem branca em volta.
- **Posição na imagem:** o lote vai de ~7% a ~90% da largura e do muro de cima (no topo da imagem) ao muro de baixo (~83,5% da altura).
  - Abaixo do muro de baixo e à direita da linha tracejada da direita, a imagem é branca.
  - A imagem final tem o mesmo formato 16:9 da entrada.
- Não aproxime, não recorte, não centralize, não amplie, não reduza e não gire nada.
- Mantêm a escala desenhada:
  - a espessura das paredes;
  - o tamanho de cada ambiente, móvel, louça e carro;
  - a largura das réguas e das placas de piso.

**O LOTE E O FUNDO**
- **Lote:** vai do muro preto de cima ao muro preto de baixo, entre as linhas tracejadas da esquerda e da direita.
- **Fora do lote:** abaixo do muro de baixo e à direita da linha tracejada da direita, o fundo fica branco puro e chapado #FFFFFF.

**OS AMBIENTES, ONDE FICA CADA UM**

**Faixa de cima (em granito marrom):** a circulação larga ao longo do muro de cima, do bloco gourmet até a garagem.
- **Escada externa:** os 18 degraus no alto, à esquerda, junto ao bloco do gourmet, que descem, como desenhados.

**Bloco gourmet, no alto à esquerda (em granito marrom):**
- **Lavabo gourmet e BH gourmet:** as duas salas pequenas lado a lado, com as bacias e as cubas como desenhadas.
- **Bancada:** a bancada branca comprida com a cuba, logo abaixo dos dois banheiros.
- **Área gourmet:** abaixo da bancada, com a ilha branca com cooktop e as sete banquetas embaixo, já sobre o deck.

**Bloco da casa, no alto ao centro e à direita (em granito marrom), da esquerda para a direita:**
1. **Cozinha:** a sala grande com a ilha central com cooktop e quatro banquetas, as bancadas com as cubas no alto e os eletrodomésticos embaixo.
2. **Área de serviço descoberta:** no alto, com o X tracejado; o abrigo de gás no canto de cima à esquerda.
3. **Área de serviço:** abaixo dela, com os dois tanques e as máquinas.
4. **DCE (com a cama) e WC DCE 1 (em Bege Bahia):** à direita da área de serviço.
5. **Elevador, adega, despensa e CPD:** a fileira de salas pequenas logo acima do living.
6. **Garagem:** à direita, com os três carros desenhados.

**Área social, ao centro (em travertino):**
- **Living e jantar:** o salão grande.
  - a mesa de jantar comprida à esquerda;
  - o estar embaixo à esquerda, com o sofá curvo sobre o tapete orgânico;
  - a mesa redonda com quatro poltronas embaixo, ao centro;
  - as plantas em vaso desenhadas, como plantas reais do tamanho desenhado.
- **Escada interna:** no meio do salão, exatamente como desenhada, com a linha de corte e os degraus tracejados.
- **Louceiro:** a faixa logo acima da escada, armário até o teto (com a linha diagonal) em marcenaria areia.
- **Jardim interno:** o retângulo verde logo abaixo da escada. É uma floreira.
- **Escritório:** à direita, com a mesa e as duas cadeiras, o sofá curvo e a mesinha redonda.
- **Lavabo:** abaixo do escritório.
- **Hall de entrada:** embaixo à direita, com o X tracejado, a porta grande e a planta em vaso.

**Área externa à esquerda (em Bege Bahia):**
- **Varanda:** entre o gourmet e o living, com as duas mesas redondas com cadeiras, o sofá, as duas poltronas, a mesa de centro e a espreguiçadeira, como desenhados.
- **Pilares:** os quatro círculos pretos na varanda e junto ao living.
- **Piscina, prainha e spa:** a piscina comprida à esquerda, a prainha à direita dela e o spa quadrado embaixo, com as bordas de Bege Bahia.
- **Deck:** o piso em volta da piscina.
- **Degraus largos:** os blocos à esquerda da piscina, como desenhados.
- **Bancos de bronze fosco:** o retângulo estreito entre a piscina e os degraus, e o L embaixo à esquerda.

**Acesso de veículos (pedra portuguesa caramelo):** a faixa curva larga à direita, que sai da frente da garagem e desce até a borda direita do lote.

**Pisantes:** as placas de Bege Bahia sobre o gramado, embaixo à direita, em fileira até a borda direita do lote.

**PISOS — cada ambiente tem um único piso, exatamente dentro das suas paredes**
- **Travertino Romano levigado:** living, jantar, circulações internas, escritório, lavabo e hall de entrada.
  - marfim-bege quente com veios paralelos na mesma direção e poros pequenos;
  - fosco.
- **Mármore Bege Bahia fosco:** varanda, deck, bordas da piscina, degraus largos, faixa à direita do hall, pisantes e WC DCE 1.
  - creme-bege claro e uniforme, quase liso;
  - só um pontilhado fino e leve e alguns veios finos e claros;
  - sem manchas, nuvens ou pontos escuros;
  - antiderrapante na área externa.
- **Granito Marrom Tabaco polido:** cozinha, serviço, DCE, despensa, adega, CPD, gourmet, BH e lavabo gourmet, garagem e a faixa de cima.
  - marrom-tabaco profundo, com grão denso de cristais pretos, âmbar-escuros e creme;
  - placas de ~60 × 60 cm, juntas finas escuras, brilho polido suave;
  - sempre marrom-escuro, nunca pedra clara.
- **Pedra portuguesa caramelo:** o acesso de veículos.
  - mosaico de pedrinhas irregulares de ~5 cm, em tons de caramelo, ocre e creme, com juntas finas de areia;
  - sem hexágonos, sem desenho e sem cinza.
- **Água:** piscina, prainha e spa.
  - água clara turquesa-claro sobre pastilha clara, com ondulação sutil;
  - a prainha, mais rasa e mais clara.

**JARDINS — paisagismo dentro do lote**
- **Gramado:** todo o verde da planta é um gramado natural, verde vivo e uniforme, com textura real de grama.
- **Vegetação:** touceiras densas de plantas tropicais vistas de cima (palmeiras, costela-de-adão, filodendros, estrelícias, samambaias) nos cantos do lote e em faixas ao longo dos muros.
- **Jardim interno:** plantas tropicais exuberantes vistas de cima sobre terra escura, exatamente dentro das bordas.
- **Limites:** fora do jardim interno, a vegetação fica dentro do lote e nunca cobre a casa, a piscina, o deck, a varanda, os pisantes nem o acesso de veículos. O gramado entre os pisantes fica baixo e aberto.

**CARROS:** os três carros da garagem, exatamente nos contornos desenhados, vistos de cima, em cores neutras (branco, prata e grafite), com vidros escuros. Nenhum carro fora da garagem.

**MÓVEIS:** exatamente como desenhados, com cada contorno, almofada e detalhe, na mesma posição, tamanho e orientação. Dentro das formas existentes, materiais de alto padrão em paleta calma:
- estofados em linho e bouclé creme e off-white;
- mesas de carvalho claro;
- cadeiras de jantar brancas;
- detalhes em metal preto;
- tapetes onde há tapete desenhado.

**MARCENARIA, BANCOS E BANCADAS**
- **Louceiro:** armário até o teto em marcenaria areia fosca #CBB89E, laca lisa, chapado, sem a sombra de um móvel baixo.
- **Bancos de bronze fosco:** metal marrom-dourado escuro, escovado fino e fosco, sem brilho espelhado, com bordas nítidas.
- **Bancadas:** cozinha, gourmet, serviço e banheiros em quartzo claro polido #ECE8E1, com pontilhado fino.
- **Louças:** brancas, com metais em preto ou cromado. Bacias, cubas e cooktops exatamente como desenhados.

**PAREDES, PILARES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas e a espessura desenhada. Os dois muros do lote também ficam pretos. Nenhuma parede nova.
- **Pilares:** os quatro, redondos, em preto sólido #111111.
- **Vidros:** linha fina cinza-claro #D6D6D3 entre caixilhos pretos finos, exatamente onde a planta mostra.
- **Portas:** só as desenhadas, com arco e folha, e nenhuma porta nova.
- **Linhas tracejadas:** os X da área de serviço descoberta e do hall de entrada ficam como desenhados, finos e tracejados.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara, uniforme, com cor de luz do dia natural e sem sombra projetada. Cores vivas e naturais, sem texto.

**Evitar:**
- **Escala:** aproximar, recortar, centralizar, ampliar, reduzir ou girar a planta, ou mudar o tamanho de paredes, ambientes, móveis, carros, réguas ou placas.
- **Ambientes:** ambientes, paredes, portas, móveis, carros ou objetos novos.
- **Fundo:** cor, textura ou vegetação fora do lote.
- **Pisos:**
  - pisos em cor chapada, ou trocados de material ou de direção;
  - pedra clara na cozinha, no serviço, no gourmet, na garagem ou na faixa de cima;
  - hexágonos, piso cinza ou concreto no acesso de veículos; pedra portuguesa fora dele;
  - Bege Bahia manchado.
- **Pilares:** cor, anel ou sombra em volta.
- **Bancos:** madeira, concreto ou pedra nos bancos de bronze.
- **Louceiro:** sombra de móvel baixo.
- **Vegetação:** sobre a casa (fora do jardim interno), a piscina, o deck, a varanda, os pisantes ou o acesso de veículos; árvores grandes cobrindo o gramado.
- **Água:** azul fora da piscina, da prainha e do spa.
- **Piscina:** bordas duplas, faixas cinza, molduras ou contornos grossos em volta da água.
- **Geral:** móveis simplificados ou trocados, sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the ground-floor plan to edit. It defines the geometry, the layout and the materials, and you follow it exactly.

FIRST OF ALL, KEEP THE EXISTING SCALE: the plan comes out at exactly the same size and in exactly the same place as in the input image — no zooming in, no cropping, no re-centring.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) of the ground floor of a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, the same lot outline, and every wall, column, glass line, door, stair, line, furniture piece, sanitary fixture, car and the pool exactly where they are, at the same size and shape. Nothing is added: no new room, wall, door, stair, furniture, car or object. The floors, the lawn, the planter, the water, the Portuguese stone paving, the bronze benches and the china cabinet already show their final materials in the plan: keep each one's material, colour and plank or vein direction exactly as it is, and only refine it into a photorealistic surface with real joints and a subtle sheen.

SCALE AND FRAMING
Keep the existing scale. The plan stays exactly where it is in the image and at exactly the same size, with the same white margin around it: do not zoom in, crop, re-centre, enlarge, shrink or rotate anything. The lot runs from about 7% to 90% of the image width, and from the top boundary wall (at the very top of the image) to the bottom boundary wall (about 83.5% of the height); below the bottom wall and to the right of the right dashed line the image is white. The output keeps the same 16:9 frame as the input. Wall thickness, the size of every room, furniture piece, fixture and car, and the width of the floor planks and slabs all stay at the drawn scale.

THE LOT AND THE BACKGROUND
The lot runs from the black boundary wall at the top to the black boundary wall at the bottom, between the dashed lines on the left and right. Outside the lot — below the bottom wall and to the right of the right dashed line — the background is pure flat white #FFFFFF.

THE ROOMS AND WHERE THEY ARE
- Top strip, in brown granite: the wide circulation along the top wall, from the gourmet block to the garage. The outdoor stair at the top left, next to the gourmet block, has 18 steps going down, exactly as drawn.
- Gourmet block, top left, in brown granite: the gourmet powder room and the gourmet bathroom, the two small rooms side by side, with their toilets and basins as drawn; the long white counter with the sink just below them; and the gourmet area below the counter, with the white island with a cooktop and the seven stools below it, already on the deck.
- House block, top centre and right, in brown granite, left to right: (1) the kitchen, the large room with a central island with a cooktop and four stools, the counters with the sinks at the top and the appliances at the bottom; (2) the open service yard at the top, with its dashed X, and the gas room in its top-left corner; (3) the laundry below it, with the two laundry tubs and the machines; (4) the maid's room with the bed and the maid's bathroom (in Bege Bahia) to the right of the laundry; (5) the elevator, the wine room, the pantry and the server room, the row of small rooms just above the living room; (6) the garage on the right, with the three drawn cars.
- Social area, in the centre, in travertine: the large living and dining room — the long dining table on the left, the lounge at the bottom left with the curved sofa on the organic rug, the round table with four armchairs at the bottom centre, and the drawn potted plants as real plants at the drawn size; the indoor stair in the middle of the room, exactly as drawn, with its cut line and dashed steps; the china cabinet, the strip just above the stair, a full-height cabinet (marked with the diagonal line) in sand joinery; the indoor garden, the green rectangle just below the stair, which is a planter; the study on the right, with the desk and two chairs, the curved sofa and the small round table; the powder room below the study; and the entrance hall at the bottom right, with its dashed X, the large door and the potted plant.
- Outdoor area on the left, in Bege Bahia: the veranda between the gourmet area and the living room, with the two round tables with chairs, the sofa, the two armchairs, the coffee table and the lounger, as drawn; the four black columns on the veranda and next to the living room; the pool — the long pool on the left, the wet deck to its right and the square spa below, with Bege Bahia copings; the deck around the pool; the wide steps, the blocks to the left of the pool, as drawn; and the matte bronze benches — the narrow rectangle between the pool and the steps, and the L at the bottom left.
- Driveway, in caramel Portuguese stone: the wide curved strip on the right, running from the front of the garage down to the right edge of the lot.
- Stepping slabs: the Bege Bahia slabs on the lawn at the bottom right, in a row to the right edge of the lot.

FLOORS — each room has exactly one floor, exactly inside its walls
- Honed Travertino Romano: the living and dining room, the inner corridors, the study, the powder room and the entrance hall. Warm ivory-beige with parallel veining in one direction and small natural pores; matte.
- Matte Bege Bahia marble: the veranda, the deck, the pool copings, the wide steps, the strip to the right of the hall, the stepping slabs and the maid's bathroom. A light, uniform cream-beige stone, almost plain: only a fine, faint speckle and a few thin light veins; no stains, clouds or dark spots; non-slip outdoors.
- Polished Marrom Tabaco granite: the kitchen, the service rooms, the maid's room, the pantry, the wine room, the server room, the gourmet area, the gourmet bathroom and powder room, the garage and the top strip. Deep tobacco brown with a dense, coarse grain of black, dark-amber and cream crystals; slabs about 60 × 60 cm, fine dark joints; glossy polished sheen with soft reflections. These floors are always deep brown, never light stone.
- Caramel Portuguese stone: the driveway. A mosaic of small irregular stones of about 5 cm in caramel, ochre and cream tones, with fine sand joints; no hexagons, no pattern and no grey.
- Water: the pool, the wet deck and the spa — clear, bright light-turquoise water over light tiles, with subtle ripples; the wet deck shallower and lighter.

GARDENS — landscaping inside the lot
Every green area of the plan is a natural lawn, vivid and evenly green, with real grass texture. Dense clusters of tropical plants seen from above (palms, monstera, philodendron, bird-of-paradise, ferns) fill the lot corners and run as planting strips along the boundary walls. The indoor garden is a planter full of lush tropical plants seen from above on dark soil, exactly inside its edges. Apart from the indoor garden, vegetation stays inside the lot and never covers the house, the pool, the deck, the veranda, the stepping slabs or the driveway; the grass between the stepping slabs stays short and open.

CARS
The three cars in the garage, exactly inside their drawn outlines, seen from above, in neutral colours (white, silver and graphite), with dark glass. No car outside the garage.

FURNITURE
Kept exactly as drawn — every outline, cushion and detail, the same position, size and orientation; not simplified, replaced or restyled. Inside the existing shapes, give them real high-end materials in a calm palette: cream and off-white linen and bouclé upholstery, light natural oak tables, white dining chairs, black metal details, and rugs where rugs are drawn.

JOINERY, BENCHES AND COUNTERTOPS
- China cabinet: full-height cabinet in a matte warm sand tone #CBB89E, smooth lacquer, flat, with no low-furniture shadow.
- Matte bronze benches: dark golden-brown metal, finely brushed and matte, with no mirror shine, and crisp edges.
- Countertops: the kitchen, the gourmet area, the laundry and the bathrooms in light polished quartz #ECE8E1 with a fine, subtle speckle.
- White sanitary ware with black or chrome fittings; toilets, basins and cooktops exactly as drawn.

WALLS, COLUMNS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; the two boundary walls of the lot are black too; no new walls.
- Columns: the four round columns in solid black #111111.
- Glass: thin pale-grey glass line #D6D6D3 between thin black frame lines, exactly where the plan shows it.
- Doors: only the drawn doors, with their arcs and leaves; no new doors.
- Dashed lines: the X marks over the open service yard and the entrance hall stay as drawn, thin and dashed.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours; no text.

Avoid: zooming in, cropping, re-centring, enlarging, shrinking or rotating the plan, or changing the size of walls, rooms, furniture, cars, planks or slabs; new rooms, walls, doors, furniture, cars or objects; colour, texture or vegetation outside the lot; flat-colour floors, or floors changed in material or direction; light stone in the kitchen, the service rooms, the gourmet area, the garage or the top strip; hexagons, grey paving or concrete on the driveway, or Portuguese stone anywhere else; blotchy Bege Bahia; colour, rings or shadows around the columns; wood, concrete or stone on the bronze benches; a low-furniture shadow on the china cabinet; vegetation over the house (outside the indoor garden), the pool, the deck, the veranda, the stepping slabs or the driveway; large tree canopies over the lawn; blue outside the pool, the wet deck and the spa; double edges, grey bands, frames or thick outlines around the water; simplified or restyled furniture; shadows; perspective; text.
```

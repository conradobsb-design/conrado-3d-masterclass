# POE 642 · Casa B · Térreo — prompt v4 (só a imagem base)
_14/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaB_BASE_Terreo_v3_texturas_16x9.png`.
- **Origem:** foi gerada do PDF do cliente (`642 - TÉRREO - CASA B.pdf`), na mesma folha e no mesmo enquadramento do Subsolo da Casa B. As duas plantas caem uma sobre a outra.
- **Texturas:** a base já traz a prévia dos pisos, do gramado, da floreira e da água, com as texturas aprovadas nos renders da Casa A. O prompt manda manter cada material e só torná-lo fotorrealista.

**Da v3 para a v4 — borda infinita:**
- **Onde fica:** no lado esquerdo do braço de cima da piscina, junto ao deck em L. No PDF, a borda cinza contorna a piscina toda, menos ali, onde há uma faixa branca de 30 cm entre a linha do deck e a da água.
- **O que muda:** essa faixa deixa de ser borda de travertino e vira a calha da borda infinita.
- **Base:** a faixa sai como água, um tom mais escuro que a piscina, e a linha da água fica como o lábio da borda. O resto é igual à da v3.
- **Prompt:** a água transborda por uma borda fina para a calha, sem pedra de borda desse lado.

**Da v2 para a v3 — granito marrom nas áreas delimitadas em malva:**
- **O que muda:** as áreas que o PDF delimita em malva passam a ser de granito Marrom Tabaco polido, como na Casa A.
  - cozinha;
  - faixa da bancada gourmet, na varanda;
  - louceiro e despensa;
  - área de serviço, quarto e BH de serviço;
  - área de serviço descoberta;
  - bloco do motorista.
- **Base:** essas áreas saem em marrom #5A4232, com a textura do granito da cozinha da Casa A. O resto é igual à da v2.
- **No Subsolo, nada muda:** lá o malva continua Bege Bahia, como você definiu.

**Da v1 para a v2 — suas respostas:**
- **Banco em L:** a peça branca que contorna o lado esquerdo e o de baixo do deck grande é um banco em tom bronze. Na base, ele já sai bronze #7A5A3C, com a borda dupla desenhada.
- **Jardim de inverno:** é um jardim com floreira. Na base, o piso dele sai como floreira, com a textura das touceiras tropicais do Térreo da Casa A. O X tracejado da abertura acima fica.
- **Base:** a v3_texturas foi gerada de novo com essas duas mudanças. O resto é igual à da v1.

**Pisos e áreas externas (definidos por você):**
- **Vinílico da Casa A:** área íntima.
  - suítes;
  - sala íntima;
  - closet master;
  - circulação íntima.
- **Granito Marrom Tabaco, como na Casa A:** todas as áreas delimitadas em malva no PDF.
  - cozinha e a faixa da bancada gourmet;
  - louceiro e despensa;
  - área de serviço, quarto e BH de serviço;
  - área de serviço descoberta;
  - bloco do motorista.
- **Pedra portuguesa caramelo, igual à da Casa A:** garagem e acesso de carros, sem os hexágonos do PDF.
- **Deck de madeira:** os três decks listrados.
  - o de cima, à esquerda da piscina;
  - o da ducha, ao lado da escada;
  - o grande de baixo.
- **Mármore travertino:** todo o resto.
  - áreas sociais, halls, banhos e lavabo;
  - varanda gourmet;
  - faixa externa em volta da casa;
  - borda das piscinas, menos o trecho da borda infinita;
  - escadas;
  - pedra grande, pedras escalonadas e pedras de acesso.
- **Garagem:** com os 3 carros do PDF.
- **Entorno:** grama e paisagismo dentro do lote, entre os dois muros.
- **Jardim de inverno:** floreira com plantas tropicais.
- **Banco em L do deck grande:** em tom bronze.

**Lições da Casa A e do Subsolo aplicadas:**
- ambientes descritos por posição;
- escala existente mantida, sem aproximar nem recortar;
- "nada é acrescentado";
- luz chapada, sem sombra;
- vegetação só no gramado, nunca sobre a casa, a piscina, os decks, as pedras ou o acesso de carros.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta do térreo a editar. Ela define a geometria, o layout e os materiais, e deve ser seguida exatamente.

Transforme a planta numa planta humanizada de apresentação do **térreo** de uma residência de alto padrão, rica e fotorrealista. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala, com o mesmo contorno do lote;
- cada parede, vidro, porta, escada, linha, móvel, louça, carro e a piscina exatamente onde estão, com o mesmo tamanho e a mesma forma;
- nada é acrescentado: nenhum ambiente, parede, porta, escada, móvel, carro ou objeto novo.

Os pisos, o gramado, a floreira e a água já aparecem na planta com o material final. Cada um mantém o material, a cor e a direção das réguas e dos veios, e só ganha acabamento fotorrealista, com juntas reais e brilho sutil.

**ESCALA E ENQUADRAMENTO:** mantenha a escala existente.
- A planta fica exatamente na mesma posição e com o mesmo tamanho na imagem, com a mesma margem branca em volta.
- Não aproxime, não recorte, não centralize, não amplie, não reduza e não gire nada.
- Mantêm a escala desenhada:
  - a espessura das paredes;
  - o tamanho de cada ambiente, móvel, louça e carro;
  - a largura das réguas e das placas de piso.

**O LOTE E O FUNDO**
- **Lote:** vai do muro preto de cima ao muro preto de baixo, entre as linhas tracejadas da esquerda e da direita.
- **Fora do lote:** acima do muro de cima e abaixo do muro de baixo, o fundo fica branco puro e chapado #FFFFFF.

**OS AMBIENTES, ONDE FICA CADA UM**

**Ala íntima, a faixa de cima, da esquerda para a direita:**
1. **Suíte master:** a sala grande do canto de cima à esquerda, com o canto de escritório (duas mesas) no alto e a cama de casal embaixo.
2. **Banho master:** acima do closet. Tem a bancada dupla no meio, junto à parede de cima, e um compartimento de cada lado, cada um com bacia e chuveiro.
3. **Closet master:** abaixo do banho master, com a ilha no meio e os armários dos lados.
4. **Sala íntima:** no alto, ao centro, com sofá, mesa redonda e poltronas.
5. **Elevador e shaft:** logo abaixo da sala íntima.
6. **Banho 1:** à direita da sala íntima.
7. **Suíte 1:** cama de casal e mesa de trabalho.
8. **Suíte 2:** duas camas de solteiro e mesa de trabalho.
9. **Banho 2:** no canto de cima à direita.

**Abaixo da faixa de cima:**
- **Circulação íntima:** o corredor horizontal sob as suítes 1 e 2.
- **Suíte 3:** à direita, abaixo da suíte 2, com o banho 3 logo abaixo dela.

**Faixa do meio, da esquerda para a direita:**
1. **Varanda gourmet:** à esquerda do living.
   - no alto, o lounge com sofás e poltronas sobre um tapete cinza;
   - abaixo, duas mesas redondas;
   - embaixo, a bancada gourmet com cooktop e cuba, sobre a faixa de granito marrom.
2. **Living e jantar:** ao centro. No alto fica o sofá em U em volta da mesa de centro; embaixo, a mesa de jantar comprida.
3. **Jardim de inverno:** à direita do sofá do living. É uma floreira com plantas tropicais, entre as paredes e o vidro, com o X tracejado da abertura acima.
4. **Lavabo:** à direita do jardim de inverno.
5. **Hall interno:** à direita do jantar, com a mesa redonda e a porta principal de giro.
6. **Hall externo:** à direita do hall interno, ligado às pedras de acesso.
- **Adega:** a salinha logo abaixo do hall interno.
- **Jardim de 4,62 m²:** o retângulo verde abaixo do hall, à esquerda da entrada da garagem.

**Área da piscina, à esquerda:**
- **Piscina:** em L.
- **Spa:** o quadrado no alto, à direita da piscina.
- **Prainha:** embaixo, à direita, com duas espreguiçadeiras na água rasa.
- **Borda:** de travertino, em volta das três, menos no lado esquerdo do braço de cima da piscina.
- **Borda infinita:** no lado esquerdo do braço de cima da piscina, junto ao deck em L. A água transborda por uma borda fina e nítida para uma calha estreita, sem pedra de borda desse lado.
- **Decks de madeira:** o deck em L acima e à esquerda da piscina, o deck da ducha à direita da escada de cima e o deck grande embaixo da piscina.
- **Banco em L:** contorna o lado esquerdo e o de baixo do deck grande, em tom bronze.

**As escadas:**
- **Escada de cima, à esquerda (6 degraus):** desce da pedra grande, à esquerda, para o deck da ducha, à direita. A seta aponta só para a direita.
- **Escada acima do spa (9 degraus):** desce da varanda gourmet, à direita, para o deck da piscina, à esquerda.
- **Pedra grande e pedras escalonadas:** à esquerda, descem em degraus soltos sobre o gramado, com grama entre as pedras.
- **Espaço branco abaixo da escada de cima:** fica branco.

**Faixa de baixo, da esquerda para a direita:**
1. **Banhos gourmet e lavatório gourmet:** embaixo da varanda.
2. **Cozinha:** com a ilha central e as bancadas.
3. **Louceiro e despensa:** as duas salinhas à direita da cozinha.
4. **Quarto de serviço e BH de serviço:** abaixo do louceiro e da despensa.
5. **Área de serviço:** à direita deles, com os tanques.
6. **Área de serviço descoberta:** o pátio aberto embaixo do quarto de serviço, em granito marrom.

**Garagem e acesso:**
- **Garagem:** à direita da cozinha, com os três carros desenhados.
- **Acesso de carros:** o piso caramelo desce pela direita e corre ao longo de toda a faixa de baixo até a borda direita do lote.
- **Bloco do motorista:** à direita da garagem, de cima para baixo: depósito, quarto do motorista e BH do motorista.

**Pedras de acesso:** as nove placas de travertino à direita do hall, sobre o gramado, até a borda direita do lote.

**PISOS — cada ambiente tem um único piso, exatamente dentro das suas paredes**
- **Travertino Romano levigado:** áreas sociais, varanda gourmet, halls, banhos, lavabo, faixa externa, borda das piscinas, escadas e pedras.
  - marfim-bege quente com veios paralelos na mesma direção e poros pequenos;
  - fosco e antiderrapante nas áreas externas.
- **Granito Marrom Tabaco polido:** cozinha, faixa da bancada gourmet, louceiro, despensa, serviço, área descoberta e bloco do motorista.
  - marrom-tabaco profundo, com grão denso de cristais pretos, âmbar-escuros e creme;
  - placas de ~60 × 60 cm, juntas finas escuras, brilho polido suave;
  - sempre marrom-escuro, nunca pedra clara.
- **Vinílico, padrão madeira:** suítes, sala íntima, closet master e circulação íntima.
  - marrom médio quente, nunca laranja;
  - réguas longas, veio discreto, fosco.
- **Deck de madeira:** os três decks.
  - réguas estreitas na direção desenhada, madeira tropical marrom-avermelhada, com frestas finas.
- **Pedra portuguesa caramelo:** garagem e acesso de carros.
  - mosaico de pedrinhas irregulares em caramelo e mel, com rejunte de areia;
  - nunca cinza e sem hexágonos.
- **Água:** piscina, spa e prainha.
  - água clara turquesa-claro sobre pastilha clara, com ondulação sutil;
  - a prainha, mais rasa e mais clara;
  - na borda infinita, a água passa por um lábio fino e cai na calha estreita, um tom mais escuro.

**JARDINS — paisagismo dentro do lote**
- **Gramado:** todo o verde da planta é um gramado natural, verde vivo e uniforme, com textura real de grama.
- **Vegetação:** touceiras densas de plantas tropicais vistas de cima (palmeiras, costela-de-adão, filodendros, estrelícias, samambaias) nos cantos do lote e em faixas ao longo dos muros e das laterais da casa.
- **Jardim de 4,62 m²:** forração tropical baixa, dentro do contorno verde.
- **Floreira do jardim de inverno:** plantas tropicais exuberantes vistas de cima (costela-de-adão, filodendros, palmeirinhas, samambaias), sobre terra escura, exatamente dentro das paredes e do vidro. O X tracejado da abertura continua visível, fino, por cima.
- **Limites:** fora da floreira e do jardim de 4,62 m², a vegetação fica dentro do lote e nunca cobre a casa, a piscina, os decks, as pedras, as escadas, o acesso de carros nem a área de serviço descoberta. O gramado entre as pedras escalonadas e entre as pedras de acesso fica baixo e aberto.

**CARROS:** os três carros da garagem, exatamente nos contornos desenhados, vistos de cima, em cores neutras (branco, prata e grafite), com vidros escuros. Nenhum carro fora da garagem.

**MÓVEIS:** exatamente como desenhados, com cada contorno, almofada e detalhe, na mesma posição, tamanho e orientação. Dentro das formas existentes, materiais de alto padrão em paleta calma:
- estofados em linho e bouclé creme e off-white;
- mesas de carvalho claro;
- cadeiras de jantar brancas;
- detalhes em metal preto;
- tapetes onde há tapete desenhado;
- o banco em L do deck grande em tom bronze #7A5A3C, acetinado, com a borda desenhada.

**MARCENARIA E BANCADAS — diferentes do piso**
- **Marcenaria:** armários, closets, painéis e bases das bancadas em tom areia fosco #CBB89E, laca lisa.
- **Bancadas:** cozinha, bancada gourmet, serviço e banheiros em quartzo claro polido #ECE8E1, com pontilhado fino.
- **Louças:** brancas, com metais em preto ou cromado. Chuveiros, bacias e cubas exatamente como desenhados, sem chuveiro novo.

**PAREDES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas e a espessura desenhada. Os dois muros do lote também ficam pretos. Nenhuma parede nova.
- **Vidros:** linha fina cinza-claro #D6D6D3 entre caixilhos pretos finos, exatamente onde a planta mostra.
- **Portas:** só as desenhadas, com arco e folha, e nenhuma porta nova.
- **Linhas tracejadas:** as projeções tracejadas junto ao hall e à entrada da garagem e o X do jardim de inverno ficam como desenhados, finos e tracejados.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara, uniforme, com cor de luz do dia natural e sem sombra projetada. Cores vivas e naturais, sem texto.

**Evitar:**
- **Escala:** aproximar, recortar, centralizar, ampliar, reduzir ou girar a planta, ou mudar o tamanho de paredes, ambientes, móveis, carros, réguas ou placas.
- **Ambientes:** ambientes, paredes, portas, móveis, carros ou objetos novos.
- **Fundo:** cor, textura ou vegetação fora do lote.
- **Pisos:**
  - pisos em cor chapada, ou trocados de material ou de direção;
  - madeira laranja;
  - pedra clara na cozinha, na faixa da bancada gourmet, no serviço, na área descoberta ou no bloco do motorista;
  - acesso de carros cinza ou com hexágonos.
- **Vegetação:** sobre a casa (fora da floreira do jardim de inverno), a piscina, os decks, as pedras, as escadas ou o acesso de carros; árvores grandes cobrindo o gramado.
- **Banco em L:** branco, de madeira ou de pedra.
- **Água:** azul fora da piscina, do spa, da prainha e da calha da borda infinita; borda de pedra no lado da borda infinita.
- **Escadas:** seta apontando para os dois lados.
- **Geral:** móveis simplificados ou trocados, sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the ground-floor plan to edit. It defines the geometry, the layout and the materials, and you follow it exactly.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) of the ground floor of a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, the same lot outline, and every wall, glass line, door, stair, line, furniture piece, sanitary fixture, car and the pool exactly where they are, at the same size and shape. Nothing is added: no new room, wall, door, stair, furniture, car or object. The floors, the lawn, the planter and the water already show their final materials in the plan: keep each one's material, colour and plank or vein direction exactly as it is, and only refine it into a photorealistic surface with real joints and a subtle sheen.

SCALE AND FRAMING
Keep the existing scale. The plan stays exactly where it is in the image and at exactly the same size, with the same white margin around it: do not zoom in, crop, re-centre, enlarge, shrink or rotate anything. Wall thickness, the size of every room, furniture piece, fixture and car, and the width of the floor planks and slabs all stay at the drawn scale.

THE LOT AND THE BACKGROUND
The lot runs from the black boundary wall at the top to the black boundary wall at the bottom, between the dashed lines on the left and right. Outside the lot — above the top wall and below the bottom wall — the background is pure flat white #FFFFFF.

THE ROOMS AND WHERE THEY ARE
- Bedroom wing, the top band, left to right: (1) the master suite — the large room at the top-left corner, with a home-office corner (two desks) at its top and the double bed below; (2) the master bathroom, above the closet — a double vanity in the middle against the top wall and one compartment on each side, each with a toilet and a shower; (3) the master closet, below the master bathroom, with an island in the middle and cabinets on both sides; (4) the family lounge at the top centre, with a sofa, a round table and armchairs; (5) the elevator and the shaft, just below the family lounge; (6) bathroom 1, to the right of the family lounge; (7) suite 1, with a double bed and a desk; (8) suite 2, with two single beds and a desk; (9) bathroom 2, at the top-right corner. Below the top band: the bedroom corridor, running horizontally under suites 1 and 2, and suite 3 on the right, below suite 2, with bathroom 3 just below it.
- Middle band, left to right: (1) the gourmet veranda, to the left of the living room — a lounge with sofas and armchairs on a grey rug at the top, two round dining tables below, and the gourmet counter with a cooktop and a sink at the bottom, on a strip of brown granite; (2) the living and dining room in the centre — a U-shaped sofa around a coffee table at the top and the long dining table below; (3) the winter garden, to the right of the living-room sofa — a planter (floreira) with tropical plants between its walls and its glass, with the dashed X of the skylight opening above it; (4) the powder room, to the right of the winter garden; (5) the inner hall, to the right of the dining table, with a round table and the main pivot door; (6) the outer entrance hall, to the right of the inner hall, leading to the stepping slabs. The wine room is the small room just below the inner hall. The 4.62 m² garden is the green rectangle below the hall, to the left of the garage entrance.
- Pool area, on the left: the L-shaped pool; the spa, the square at the top-right of the pool; the wet deck (prainha) at the bottom-right, with two sun loungers in the shallow water; a travertine coping around all three, except on the left side of the pool's upper arm, against the L-shaped deck, which is an infinity edge: the water spills over a thin, crisp lip into a narrow catch channel, with no stone coping on that side. Wooden decks: the L-shaped deck above and to the left of the pool, the outdoor-shower deck to the right of the upper stair, and the large deck below the pool. An L-shaped bench in a bronze tone runs along the left and bottom edges of the large deck.
- Bottom band, left to right: (1) the two pool bathrooms and the pool washbasin, below the veranda; (2) the kitchen, with its central island and counters; (3) the china room and the pantry, the two small rooms to the right of the kitchen; (4) the maid's room and the service bathroom, below the china room and the pantry; (5) the laundry, to their right, with the laundry tubs; (6) the open service yard below the maid's room, in brown granite.
- Garage and access: the garage, to the right of the kitchen, with the three drawn cars; the caramel driveway comes down on the right and runs along the whole bottom band to the right edge of the lot. The driver's block, to the right of the garage, top to bottom: storage room, driver's room and driver's bathroom.
- Stepping slabs: the nine travertine slabs to the right of the entrance hall, on the lawn, running to the right edge of the lot.

THE STAIRS
- The upper stair on the left (6 steps) goes down from the large stone slab on its left to the outdoor-shower deck on its right; its arrow points only to the right. The white space below it stays white.
- The stair above the spa (9 steps) goes down from the gourmet veranda on its right to the pool deck on its left.
- The large stone slab and the staggered stone slabs on the far left step down as separate travertine slabs on the lawn, with grass between them.

FLOORS — each room has exactly one floor, exactly inside its walls
- Honed Travertino Romano: the living and dining room, the gourmet veranda, the halls, the bathrooms, the powder room, the outdoor strip around the house, the pool coping, the stairs and all stone slabs. Warm ivory-beige with parallel veining in one direction and small natural pores; matte and non-slip outdoors.
- Polished Marrom Tabaco granite: the kitchen, the strip under the gourmet counter, the china room, the pantry, the service rooms, the open service yard and the driver's block. Deep tobacco brown with a dense, coarse grain of black, dark-amber and cream crystals; slabs about 60 × 60 cm, fine dark joints; glossy polished sheen with soft reflections. These floors are always deep brown, never light stone.
- Wood-look vinyl: the suites, the family lounge, the master closet and the bedroom corridor. A warm medium brown, never orange; long planks, subtle grain, matte.
- Wooden decks: narrow boards of reddish-brown tropical wood running as drawn, with thin gaps.
- Caramel Portuguese cobblestone (pedra portuguesa): the garage and the driveway. A warm caramel-and-honey mosaic of small irregular hand-cut stones with sand joints; never grey, no hexagon pattern.
- Water: the pool, the spa and the wet deck — clear, bright light-turquoise water over light tiles, with subtle ripples; the wet deck shallower and lighter; at the infinity edge the water flows over a thin lip into the narrow catch channel, one tone darker.

GARDENS — landscaping inside the lot
Every green area of the plan is a natural lawn, vivid and evenly green, with real grass texture. Dense clusters of tropical plants seen from above (palms, monstera, philodendron, bird-of-paradise, ferns) fill the lot corners and run as planting strips along the boundary walls and the sides of the house. The 4.62 m² garden is low tropical ground cover inside its green outline. The winter-garden planter is full of lush tropical plants seen from above (monstera, philodendron, small palms, ferns) on dark soil, exactly inside its walls and glass, with the thin dashed X of the skylight still visible over it. Apart from the planter and the 4.62 m² garden, vegetation stays inside the lot and never covers the house, the pool, the decks, the stone slabs, the stairs, the driveway or the open service yard; the grass between the staggered slabs and between the stepping slabs stays short and open.

CARS
The three cars in the garage, exactly inside their drawn outlines, seen from above, in neutral colours (white, silver and graphite), with dark glass. No car outside the garage.

FURNITURE
Kept exactly as drawn — every outline, cushion and detail, the same position, size and orientation; not simplified, replaced or restyled. Inside the existing shapes, give them real high-end materials in a calm palette: cream and off-white linen and bouclé upholstery, light natural oak tables, white dining chairs, black metal details, rugs where rugs are drawn, and the L-shaped bench on the large deck in a satin bronze tone #7A5A3C with its drawn edge.

JOINERY, COUNTERTOPS AND FIXTURES — distinct from the floors
- Joinery: cabinets, closets, panels and counter bases in a matte warm sand tone #CBB89E, smooth lacquer.
- Countertops: the kitchen, the gourmet counter, the laundry and the bathrooms in light polished quartz #ECE8E1 with a fine, subtle speckle.
- White sanitary ware with black or chrome fittings; showers, toilets and basins exactly as drawn, with no new shower.

WALLS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; the two boundary walls of the lot are black too; no new walls.
- Glass: thin pale-grey glass line #D6D6D3 between thin black frame lines, exactly where the plan shows it.
- Doors: only the drawn doors, with their arcs and leaves; no new doors.
- Dashed lines: the dashed projections by the hall and the garage entrance and the dashed X of the winter garden stay as drawn, thin and dashed.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours; no text.

Avoid: zooming in, cropping, re-centring, enlarging, shrinking or rotating the plan, or changing the size of walls, rooms, furniture, cars, planks or slabs; new rooms, walls, doors, furniture, cars or objects; colour, texture or vegetation outside the lot; flat-colour floors, or floors changed in material or direction; orange wood; light stone in the kitchen, the gourmet-counter strip, the service rooms, the open service yard or the driver's block; a grey or hexagon-patterned driveway; vegetation over the house (outside the winter-garden planter), the pool, the decks, the stone slabs, the stairs or the driveway; a white, wooden or stone L-shaped bench; large tree canopies over the lawn; blue outside the pool, the spa, the wet deck and the infinity-edge channel; stone coping on the infinity edge; a double-headed arrow on the stairs; simplified or restyled furniture; shadows; perspective; text.
```

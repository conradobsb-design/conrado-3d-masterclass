# POE 642 · Casa C · Térreo — prompt v2 (só a imagem base)
_14/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaC_BASE_Terreo_v3_texturas_16x9.png`.
- **Origem:** foi gerada do PDF do cliente (`642 - TÉRREO - CASA C.pdf`), na mesma folha e no mesmo enquadramento do Subsolo da Casa C. As duas plantas caem uma sobre a outra.
- **Texturas:** a base já traz a prévia dos pisos, do gramado, das floreiras e da água, com as texturas aprovadas nos renders das Casas A e B. O prompt manda manter cada material e só torná-lo fotorrealista.

**Da v1 para a v2 — piscina sem bordas a mais:**
- **O que estava errado na base:** as paredes estruturais da piscina, da prainha, do spa, dos degraus e do deck vêm do PDF na layer de parede, com preenchimento branco. No PDF elas ficam escondidas sob a água e o travertino, mas o gerador as transformou em faixas de vidro cinza com contorno preto em volta de tudo.
- **Base (v2 e v3 geradas de novo):** essas paredes saíram da detecção de vidro. Na piscina ficam só três elementos.
  - a borda de travertino em volta da prainha, do spa e da piscina;
  - os dois degraus: as duas linhas finas na parte de baixo da prainha, junto à piscina;
  - o vidro da borda infinita: a linha dupla fina no lado esquerdo da piscina comprida.
- **Deck:** as duas faixas cinza em L entre o banco e o deck também eram falsas; agora o deck vai até o banco.
- **Prompt:** a piscina passa a ser descrita com esses três elementos, e o "Evitar" proíbe bordas duplas, faixas e molduras em volta da água.

**Pisos e áreas externas (definidos por você em 14/10/26):**
- **Travertino:** todo o oliva do PDF.
  - áreas sociais, circulações e halls;
  - varandas, varanda master e varanda gourmet;
  - BH master 1 e lavabos;
  - borda das piscinas.
- **Vinílico da Casa A:** o laranja do PDF.
  - suíte master;
  - quartos 1, 2 e 3;
  - closets master 1 e 2;
  - escritório.
- **Granito Marrom Tabaco, como nas Casas A e B:** o malva do PDF, menos a garagem.
  - cozinha e louceiro;
  - área de serviço, quarto e BH de serviço;
  - área de serviço descoberta;
  - quarto e BH externos;
  - faixa da bancada gourmet.
- **Pedra portuguesa caramelo, sem os hexágonos:** garagem, com os 3 carros do PDF, e acesso de carros.
- **Bege Bahia:**
  - banhos BH 1, BH 2, BH 3 e BH master 2;
  - área externa: pátio, degraus largos e caminho à esquerda;
  - escada estreita ao lado do deck;
  - pisantes.
- **Deck de madeira:** a faixa listrada entre a escada e a piscina.
- **Entorno:** grama e paisagismo dentro do lote.
- **Floreiras:** jardim 1 e os dois jardins de inverno.
- **Banco em L junto ao deck:** em tom bronze, como o da Casa B.

**Degraus largos:** no PDF, eles são numerados de 1, junto ao pátio, a 10, junto ao caminho, e seguem na escada estreita, de 11 a 21, até o deck. Descem para cima, rumo ao pátio, como no Subsolo. A base traz a linha de caminhamento com a seta para cima.

**Lições das Casas A e B aplicadas:**
- escala existente em destaque, com a posição medida na base;
- ambientes descritos por posição;
- "nada é acrescentado";
- luz chapada, sem sombra;
- vegetação só no gramado e nas floreiras, nunca sobre a casa, a piscina, o deck, os pisantes ou o acesso de carros;
- degraus largos sem sombra abaixo das bordas.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta do térreo a editar. Ela define a geometria, o layout e os materiais, e deve ser seguida exatamente.

**Antes de tudo: mantenha a escala existente.** A planta sai exatamente do mesmo tamanho e no mesmo lugar da imagem de entrada, sem aproximar, recortar nem centralizar.

Transforme a planta numa planta humanizada de apresentação do **térreo** de uma residência de alto padrão, rica e fotorrealista. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala, com o mesmo contorno do lote;
- cada parede, vidro, porta, escada, linha, móvel, louça, carro e a piscina exatamente onde estão, com o mesmo tamanho e a mesma forma;
- nada é acrescentado: nenhum ambiente, parede, porta, escada, móvel, carro ou objeto novo.

Os pisos, o gramado, as floreiras e a água já aparecem na planta com o material final. Cada um mantém o material, a cor e a direção das réguas e dos veios, e só ganha acabamento fotorrealista, com juntas reais e brilho sutil.

**ESCALA E ENQUADRAMENTO:** mantenha a escala existente.
- A planta fica exatamente na mesma posição e com o mesmo tamanho na imagem, com a mesma margem branca em volta.
- **Posição na imagem:** o lote vai de ~8% a ~91% da largura e do muro de cima (~2,5% da altura) ao muro de baixo (~85% da altura).
  - Abaixo do muro de baixo, a imagem é branca.
  - A imagem final tem o mesmo formato 16:9 da entrada.
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
1. **Varanda master:** a faixa de travertino que desce pela esquerda da suíte master, do alto até o BH master 2.
2. **BH master 1:** no canto de cima à esquerda da casa.
3. **Closet master 1:** à direita do BH master 1.
4. **Suíte master:** abaixo deles, com a cama de casal, as poltronas à esquerda e a mesa à direita.
5. **BH master 2 e closet master 2:** abaixo da suíte master, o BH à esquerda e o closet à direita.
6. **BH 3, quarto 3, quarto 2 e BH 2:** na faixa de cima, ao centro.
   - o quarto 3 tem cama de casal;
   - o quarto 2, duas camas de solteiro.
7. **BH 1 e quarto 1:** à direita, com cama de casal, poltronas e mesa.
8. **Varandas:** as faixas de travertino acima dos quartos.

**Logo abaixo da faixa de cima:**
- **Sala TV:** abaixo dos quartos 3 e 2, com o sofá em L sobre o tapete.
- **Jardim 1:** o quadrado verde à esquerda da sala TV, ao lado do closet master 2. É uma floreira.
- **Circulação:** o corredor horizontal largo abaixo do quarto 1, até a cozinha.

**Serviço e garagem, à direita:**
- **Cozinha:** no alto, à direita dos quartos, com a ilha central (cooktop e banquetas) e as bancadas.
- **Louceiro 1:** a salinha abaixo, à esquerda da cozinha.
- **Área de serviço:** à direita da cozinha, com os tanques.
- **Área de serviço descoberta:** o pátio aberto acima da área de serviço, junto ao muro de cima, com o X tracejado.
- **Quarto de serviço e BH de serviço:** abaixo da área de serviço.
- **Garagem:** à direita do serviço, com os três carros desenhados. O piso caramelo desce em faixa pela esquerda até a porta da casa.
- **Quarto externo e BH externo:** abaixo dos carros, dentro da garagem.
- **Acesso de carros:** o piso caramelo acima da garagem, no canto de cima à direita do lote.

**Faixa do meio, da esquerda para a direita:**
1. **Gourmet:** abaixo da sala TV, com a bancada comprida sobre a faixa de granito marrom e o cooktop na bancada de baixo.
2. **Elevador:** a caixa ao centro, abaixo da circulação.
3. **Jardim de inverno 2:** o quadradinho verde à direita do elevador. É uma floreira.
4. **Jardim de inverno:** o quadrado verde grande abaixo do elevador. É uma floreira com plantas tropicais.
5. **Jantar:** à direita dos jardins de inverno, com a mesa comprida.
6. **Louceiro 2, adega e lavabo:** à direita do jantar.
7. **Sala de almoço:** no alto, à direita, abaixo do quarto de serviço, com a mesa redonda.
8. **Escritório:** à direita do lavabo, com a mesa e duas cadeiras, em vinílico.

**Faixa de baixo:**
- **Varanda gourmet:** à esquerda, com duas mesas redondas.
- **Lavabo masculino e lavabo feminino:** embaixo da varanda gourmet.
- **Estar:** o salão grande ao centro, com os sofás e as poltronas em volta da mesa de centro e o sofá curvo com a mesa redonda e as plantas à direita.
- **Hall de entrada:** à direita do estar, com a porta de giro.

**Área da piscina, à esquerda:**
- **Deck de madeira:** a faixa listrada acima da piscina.
- **Banco em L:** contorna o lado de cima e o lado esquerdo do deck, em tom bronze, com a borda branca fina desenhada.
- **Prainha:** o retângulo de água no alto, à esquerda.
- **Spa:** o quadrado à direita da prainha, com o quadrado fino desenhado no meio.
- **Piscina:** o retângulo comprido embaixo.
- **Só três elementos em volta e dentro da água:**
  - **Borda de travertino:** em volta da prainha, do spa e da piscina, menos no lado esquerdo da piscina comprida.
  - **Degraus:** as duas linhas finas na parte de baixo da prainha, junto à piscina, são dois degraus submersos, como desenhados.
  - **Borda infinita:** o lado esquerdo da piscina comprida é um vidro fino, a linha dupla desenhada. A água vai até o vidro, sem borda de pedra desse lado.
- **Nada mais:** nenhuma outra borda, faixa, moldura ou linha dupla em volta da água.

**ÁREA EXTERNA À ESQUERDA, EM BEGE BAHIA**
- **Pátio:** o retângulo grande no alto, à esquerda da varanda master.
- **Degraus largos:** a faixa abaixo do pátio, com as bordas dos degraus visíveis.
  - as 2 bordas de baixo viram em L, como desenhadas;
  - descem para cima: do caminho, embaixo, até o pátio, que é o nível mais baixo;
  - a linha de caminhamento fica como desenhada, com a seta apontando só para cima, rumo ao pátio;
  - cada borda é uma linha nítida, sem sombra abaixo dela. Se houver leitura de profundidade, ela fica logo acima de cada borda, do lado do pátio.
- **Caminho:** a faixa comprida que desce à esquerda da piscina.
- **Escada estreita (degraus 11 a 21):** entre o BH master 2 e o deck.
  - desce do deck, à direita, para os degraus largos, à esquerda;
  - fica como desenhada.

**Pisantes:** as placas de Bege Bahia sobre o gramado, em duas fileiras ao longo do muro de baixo e à direita do hall de entrada, até a borda direita do lote.

**PISOS — cada ambiente tem um único piso, exatamente dentro das suas paredes**
- **Travertino Romano levigado:** áreas sociais, circulações, halls, varandas, BH master 1, lavabos e a borda das piscinas.
  - marfim-bege quente com veios paralelos na mesma direção e poros pequenos;
  - fosco e antiderrapante nas áreas externas.
- **Mármore Bege Bahia fosco:** BH 1, BH 2, BH 3, BH master 2, pátio, degraus largos, caminho, escada estreita e pisantes.
  - creme-bege claro e uniforme, quase liso;
  - só um pontilhado fino e leve e alguns veios finos e claros;
  - sem manchas, nuvens ou pontos escuros;
  - antiderrapante na área externa.
- **Granito Marrom Tabaco polido:** cozinha, louceiro, serviço, área descoberta, quarto e BH externos e a faixa da bancada gourmet.
  - marrom-tabaco profundo, com grão denso de cristais pretos, âmbar-escuros e creme;
  - placas de ~60 × 60 cm, juntas finas escuras, brilho polido suave;
  - sempre marrom-escuro, nunca pedra clara.
- **Vinílico, padrão madeira:** suíte master, quartos, closets e escritório.
  - marrom médio quente, nunca laranja;
  - réguas longas na direção desenhada, veio discreto, fosco.
- **Deck de madeira:** réguas estreitas na direção desenhada, madeira tropical marrom-avermelhada, com frestas finas.
- **Pedra portuguesa caramelo:** garagem e acesso de carros.
  - mosaico de pedrinhas irregulares em caramelo e mel, com rejunte de areia;
  - nunca cinza e sem hexágonos.
- **Água:** piscina, spa e prainha.
  - água clara turquesa-claro sobre pastilha clara, com ondulação sutil;
  - a prainha, mais rasa e mais clara.

**JARDINS — paisagismo dentro do lote**
- **Gramado:** todo o verde da planta é um gramado natural, verde vivo e uniforme, com textura real de grama.
- **Vegetação:** touceiras densas de plantas tropicais vistas de cima (palmeiras, costela-de-adão, filodendros, estrelícias, samambaias) nos cantos do lote e em faixas ao longo dos muros e das laterais da casa.
- **Floreiras:** jardim 1 e os dois jardins de inverno.
  - plantas tropicais exuberantes vistas de cima (costela-de-adão, filodendros, palmeirinhas, samambaias) sobre terra escura;
  - exatamente dentro das paredes e dos vidros.
- **Limites:** fora das floreiras, a vegetação fica dentro do lote e nunca cobre a casa, a piscina, o deck, os pisantes, o pátio, os degraus, o caminho nem o acesso de carros. O gramado entre os pisantes fica baixo e aberto.

**CARROS:** os três carros da garagem, exatamente nos contornos desenhados, vistos de cima, em cores neutras (branco, prata e grafite), com vidros escuros. Nenhum carro fora da garagem.

**MÓVEIS:** exatamente como desenhados, com cada contorno, almofada e detalhe, na mesma posição, tamanho e orientação. Dentro das formas existentes, materiais de alto padrão em paleta calma:
- estofados em linho e bouclé creme e off-white;
- mesas de carvalho claro;
- cadeiras de jantar brancas;
- detalhes em metal preto;
- tapetes onde há tapete desenhado;
- o banco em L junto ao deck em tom bronze #7A5A3C, acetinado, com a borda desenhada.

**MARCENARIA E BANCADAS — diferentes do piso**
- **Marcenaria:** armários, closets, painéis e bases das bancadas em tom areia fosco #CBB89E, laca lisa.
- **Bancadas:** cozinha, gourmet, serviço e banheiros em quartzo claro polido #ECE8E1, com pontilhado fino.
- **Louças:** brancas, com metais em preto ou cromado. Chuveiros, bacias e cubas exatamente como desenhados, sem chuveiro novo.

**PAREDES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas e a espessura desenhada. Os dois muros do lote também ficam pretos. Nenhuma parede nova.
- **Vidros:** linha fina cinza-claro #D6D6D3 entre caixilhos pretos finos, exatamente onde a planta mostra.
- **Portas:** só as desenhadas, com arco e folha, e nenhuma porta nova.
- **Linhas tracejadas:** as projeções tracejadas, como o retângulo com X no alto da varanda master e o X da área de serviço descoberta, ficam como desenhadas, finas e tracejadas.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara, uniforme, com cor de luz do dia natural e sem sombra projetada. Cores vivas e naturais, sem texto.

**Evitar:**
- **Escala:** aproximar, recortar, centralizar, ampliar, reduzir ou girar a planta, ou mudar o tamanho de paredes, ambientes, móveis, carros, réguas ou placas.
- **Ambientes:** ambientes, paredes, portas, móveis, carros ou objetos novos.
- **Fundo:** cor, textura ou vegetação fora do lote.
- **Pisos:**
  - pisos em cor chapada, ou trocados de material ou de direção;
  - madeira laranja;
  - pedra clara na cozinha, no serviço, na área descoberta, no quarto ou BH externos ou na faixa da bancada gourmet;
  - garagem ou acesso de carros cinza ou com hexágonos;
  - Bege Bahia manchado.
- **Vegetação:** sobre a casa (fora das floreiras), a piscina, o deck, os pisantes, o pátio, os degraus, o caminho ou o acesso de carros; árvores grandes cobrindo o gramado.
- **Banco em L:** branco, de madeira ou de pedra.
- **Água:** azul fora da piscina, do spa e da prainha.
- **Piscina:** bordas duplas, faixas cinza, molduras ou contornos grossos em volta da água; borda de pedra no lado do vidro da borda infinita; degraus a mais.
- **Degraus largos:** leitura de descida para baixo, sombra abaixo das bordas ou seta apontando para baixo ou para os dois lados.
- **Geral:** móveis simplificados ou trocados, sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the ground-floor plan to edit. It defines the geometry, the layout and the materials, and you follow it exactly.

FIRST OF ALL, KEEP THE EXISTING SCALE: the plan comes out at exactly the same size and in exactly the same place as in the input image — no zooming in, no cropping, no re-centring.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) of the ground floor of a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, the same lot outline, and every wall, glass line, door, stair, line, furniture piece, sanitary fixture, car and the pool exactly where they are, at the same size and shape. Nothing is added: no new room, wall, door, stair, furniture, car or object. The floors, the lawn, the planters and the water already show their final materials in the plan: keep each one's material, colour and plank or vein direction exactly as it is, and only refine it into a photorealistic surface with real joints and a subtle sheen.

SCALE AND FRAMING
Keep the existing scale. The plan stays exactly where it is in the image and at exactly the same size, with the same white margin around it: do not zoom in, crop, re-centre, enlarge, shrink or rotate anything. The lot runs from about 8% to 91% of the image width, and from the top boundary wall (about 2.5% of the height) to the bottom boundary wall (about 85% of the height); below the bottom wall the image is white. The output keeps the same 16:9 frame as the input. Wall thickness, the size of every room, furniture piece, fixture and car, and the width of the floor planks and slabs all stay at the drawn scale.

THE LOT AND THE BACKGROUND
The lot runs from the black boundary wall at the top to the black boundary wall at the bottom, between the dashed lines on the left and right. Outside the lot — above the top wall and below the bottom wall — the background is pure flat white #FFFFFF.

THE ROOMS AND WHERE THEY ARE
- Bedroom wing, the top band, left to right: (1) the master veranda, the travertine strip running down the left side of the master suite; (2) master bathroom 1, at the top-left corner of the house; (3) master closet 1, to its right; (4) the master suite below them, with the double bed, armchairs on the left and a desk on the right; (5) master bathroom 2 and master closet 2 below the master suite, the bathroom on the left and the closet on the right; (6) bathroom 3, bedroom 3 (double bed), bedroom 2 (two single beds) and bathroom 2 across the top centre; (7) bathroom 1 and bedroom 1 on the right, with a double bed, armchairs and a desk; (8) the verandas, the travertine strips above the bedrooms.
- Just below the top band: the TV room below bedrooms 3 and 2, with an L-shaped sofa on a rug; garden 1, the small green square to the left of the TV room, next to master closet 2, which is a planter; and the wide horizontal corridor below bedroom 1, running to the kitchen.
- Service and garage, on the right: the kitchen at the top, to the right of the bedrooms, with a central island (cooktop and stools) and counters; china room 1, the small room below-left of the kitchen; the laundry to the right of the kitchen, with the laundry tubs; the open service yard above the laundry, against the top wall, with its dashed X; the maid's room and the service bathroom below the laundry; the garage to the right of the service area, with the three drawn cars, its caramel floor running down in a strip on its left to the house door; the outdoor room and its bathroom below the cars, inside the garage; and the caramel driveway above the garage, at the top-right corner of the lot.
- Middle band, left to right: (1) the gourmet kitchen below the TV room, with the long counter on a strip of brown granite and the cooktop on the lower counter; (2) the elevator, the box in the centre below the corridor; (3) winter garden 2, the small green square to the right of the elevator, a planter; (4) the winter garden, the large green square below the elevator, a planter with tropical plants; (5) the dining room to the right of the winter gardens, with the long table; (6) china room 2, the wine room and the powder room to the right of the dining room; (7) the breakfast room at the top right, below the maid's room, with a round table; (8) the study, to the right of the powder room, with a desk and two chairs, in vinyl.
- Bottom band: the gourmet veranda on the left, with two round tables; the men's and women's powder rooms below the gourmet veranda; the large living room in the centre, with sofas and armchairs around a coffee table and, on the right, a curved sofa with a round table and plants; and the entrance hall to the right of the living room, with the pivot door.
- Pool area, on the left: the striped wooden deck above the pools; an L-shaped bench in a bronze tone along the top and left sides of the deck, with its thin white drawn edge; the wet deck (prainha), the water rectangle at the top-left; the spa, the square to its right, with its thin inner square as drawn; and the long pool at the bottom. Around and inside the water there are only three elements: (1) a travertine coping around the wet deck, the spa and the pool, except on the left side of the long pool; (2) two submerged steps, the two thin lines across the bottom of the wet deck next to the pool, as drawn; (3) the infinity edge: the left side of the long pool is a thin glass edge, the drawn thin double line, with the water reaching the glass and no stone coping on that side. There is no other edge, band, frame or double line around the water.

OUTDOOR AREA ON THE LEFT, IN BEGE BAHIA
The large patio at the top-left, to the left of the master veranda; the band of wide steps below it, with their step edges visible and the bottom two edges turning in an L as drawn; and the long path running down to the left of the pool. The wide steps descend upward, from the path at the bottom to the patio, which is the lowest level: the walking line stays as drawn, with its arrow pointing only up toward the patio. Each step edge is a crisp line with no shading below it; if any depth cue is shown, it sits just above each edge, on the patio side. The narrow stair (steps 11 to 21) between master bathroom 2 and the deck goes down from the deck on its right to the wide steps on its left, and stays as drawn.

STEPPING SLABS
The Bege Bahia slabs on the lawn, in two rows along the bottom wall and to the right of the entrance hall, running to the right edge of the lot.

FLOORS — each room has exactly one floor, exactly inside its walls
- Honed Travertino Romano: the social areas, corridors, halls, verandas, master bathroom 1, the powder rooms and the pool coping. Warm ivory-beige with parallel veining in one direction and small natural pores; matte and non-slip outdoors.
- Matte Bege Bahia marble: bathrooms 1, 2 and 3, master bathroom 2, the patio, the wide steps, the path, the narrow stair and the stepping slabs. A light, uniform cream-beige stone, almost plain: only a fine, faint speckle and a few thin light veins; no stains, clouds or dark spots; non-slip outdoors.
- Polished Marrom Tabaco granite: the kitchen, the china room, the service rooms, the open service yard, the outdoor room and its bathroom, and the strip under the gourmet counter. Deep tobacco brown with a dense, coarse grain of black, dark-amber and cream crystals; slabs about 60 × 60 cm, fine dark joints; glossy polished sheen with soft reflections. These floors are always deep brown, never light stone.
- Wood-look vinyl: the master suite, the bedrooms, the closets and the study. A warm medium brown, never orange; long planks in the drawn direction, subtle grain, matte.
- Wooden deck: narrow boards of reddish-brown tropical wood running as drawn, with thin gaps.
- Caramel Portuguese cobblestone (pedra portuguesa): the garage and the driveway. A warm caramel-and-honey mosaic of small irregular hand-cut stones with sand joints; never grey, no hexagon pattern.
- Water: the pool, the spa and the wet deck — clear, bright light-turquoise water over light tiles, with subtle ripples; the wet deck shallower and lighter.

GARDENS — landscaping inside the lot
Every green area of the plan is a natural lawn, vivid and evenly green, with real grass texture. Dense clusters of tropical plants seen from above (palms, monstera, philodendron, bird-of-paradise, ferns) fill the lot corners and run as planting strips along the boundary walls and the sides of the house. Garden 1 and the two winter gardens are planters full of lush tropical plants seen from above (monstera, philodendron, small palms, ferns) on dark soil, exactly inside their walls and glass. Apart from the planters, vegetation stays inside the lot and never covers the house, the pool, the deck, the stepping slabs, the patio, the steps, the path or the driveway; the grass between the stepping slabs stays short and open.

CARS
The three cars in the garage, exactly inside their drawn outlines, seen from above, in neutral colours (white, silver and graphite), with dark glass. No car outside the garage.

FURNITURE
Kept exactly as drawn — every outline, cushion and detail, the same position, size and orientation; not simplified, replaced or restyled. Inside the existing shapes, give them real high-end materials in a calm palette: cream and off-white linen and bouclé upholstery, light natural oak tables, white dining chairs, black metal details, rugs where rugs are drawn, and the L-shaped bench by the deck in a satin bronze tone #7A5A3C with its drawn edge.

JOINERY, COUNTERTOPS AND FIXTURES — distinct from the floors
- Joinery: cabinets, closets, panels and counter bases in a matte warm sand tone #CBB89E, smooth lacquer.
- Countertops: the kitchen, the gourmet kitchen, the laundry and the bathrooms in light polished quartz #ECE8E1 with a fine, subtle speckle.
- White sanitary ware with black or chrome fittings; showers, toilets and basins exactly as drawn, with no new shower.

WALLS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; the two boundary walls of the lot are black too; no new walls.
- Glass: thin pale-grey glass line #D6D6D3 between thin black frame lines, exactly where the plan shows it.
- Doors: only the drawn doors, with their arcs and leaves; no new doors.
- Dashed lines: the dashed projections, such as the rectangle with an X at the top of the master veranda and the X over the open service yard, stay as drawn, thin and dashed.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours; no text.

Avoid: zooming in, cropping, re-centring, enlarging, shrinking or rotating the plan, or changing the size of walls, rooms, furniture, cars, planks or slabs; new rooms, walls, doors, furniture, cars or objects; colour, texture or vegetation outside the lot; flat-colour floors, or floors changed in material or direction; orange wood; light stone in the kitchen, the service rooms, the open service yard, the outdoor room or the gourmet-counter strip; a grey or hexagon-patterned garage or driveway; blotchy Bege Bahia; vegetation over the house (outside the planters), the pool, the deck, the stepping slabs, the patio, the steps, the path or the driveway; a white, wooden or stone L-shaped bench; large tree canopies over the lawn; blue outside the pool, the spa and the wet deck; double edges, grey bands, frames or thick outlines around the water, stone coping on the glass infinity edge, or extra steps; wide steps that read as descending downward, shading below their edges, or an arrow pointing down or both ways on them; simplified or restyled furniture; shadows; perspective; text.
```

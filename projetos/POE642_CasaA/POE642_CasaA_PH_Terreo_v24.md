# POE 642 · Casa A · Térreo — prompt v24
_13/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagens de entrada (duas, nesta ordem):**
1. `POE642_CasaA_BASE_Terreo_v3_vidros_neutros_16x9.png`: a base colorida com paredes pretas e vidros neutros, na tela 16:9. É ela que define a geometria.
2. O render de referência que você escolheu (gramado com touceiras tropicais nos cantos, Bege Bahia creme, granito marrom-escuro, pedra portuguesa caramelo). Use o arquivo original, não um print. Ele entra só como referência de estilo.

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

Há duas imagens de entrada:
- **imagem 1 (a planta a editar):** define a geometria e o layout, e deve ser seguida exatamente;
- **imagem 2 (referência de estilo da mesma casa):** copie o visual dela, mas não a geometria. O visual é a pedra creme quente, o travertino claro, o granito marrom-escuro, o acesso em pedra portuguesa caramelo, o gramado verde com touceiras de plantas tropicais e o desenho limpo dos móveis em creme e carvalho.

Onde as duas diferirem, vale a imagem 1.

Transforme a imagem 1 numa planta humanizada de apresentação, rica e fotorrealista, para uma residência de alto padrão. Isto é uma edição da imagem 1, não um desenho novo:
- mesmo enquadramento e mesma escala;
- mesmo contorno do lote;
- cada parede, janela, porta, escada, pilar, linha, móvel, carro e a piscina exatamente onde estão, com o mesmo tamanho e a mesma forma.

Muda o acabamento: pisos, água, jardins e materiais dos móveis ficam reais, sofisticados e cheios de vida.

**PISOS — materiais reais fotografados, cada um exatamente dentro do seu contorno**

Todo piso se lê como pedra ou madeira real fotografada de cima: veios, cristais ou grão visíveis, juntas reais, variação natural entre placas e o brilho suave do acabamento. Nenhum piso fica em cor chapada ou em quadrados lisos.
- **Áreas bege-acinzentadas #DCD9CA** (estar, jantar, varanda, halls, escada principal, gourmet, lavabo, banho da varanda): Travertino Romano levigado #D9CBB3.
  - marfim-bege quente, veios horizontais suaves em mel e taupe claro, poros pequenos estucados, leves mudanças de tom;
  - placas de ~60 × 120 cm em grade reta, juntas finas de 2 mm;
  - brilho acetinado.
- **Áreas malva #BFA79F** (cozinha, área de serviço, despensa, escada de serviço, quarto e banho do motorista, garagem): granito Marrom Tabaco polido #4A3426.
  - marrom-tabaco profundo, com grão denso e graúdo de cristais pretos, âmbar-escuros e creme;
  - placas de ~60 × 60 cm, juntas escuras finas;
  - brilho de polido com reflexos suaves.
- **Áreas cinza-claro #E8E8E8** (deck da piscina, hall externo, placas de pedestres, escada abaixo do deck do spa) e as bordas da piscina e do spa: mármore Bege Bahia #D8CDB4.
  - o cinza da legenda vira pedra bege-creme quente, com manchas suaves em nuvem, pontinhos e pequenos fósseis;
  - fosco antiderrapante, placas de ~60 × 60 cm, juntas de 3 mm;
  - grama nas juntas entre as placas de pedestres;
  - nada fica cinza.
- **Área marrom hachurada #AE8863** em volta do spa: deck de madeira natural #9A6B47.
  - réguas de ~14 cm seguindo exatamente a hachura;
  - veio reto aparente, emendas desencontradas, frestas escuras finas, leve variação de tom entre réguas.
- **Hachura de pontinhos cinza** (acesso de veículos, acesso à garagem e corredor de serviço descoberto entre os dois gradis): pedra portuguesa caramelo #B98A55.
  - os pontinhos cinza viram um mosaico quente de caramelo e mel, com pedrinhas irregulares cortadas à mão e juntas de areia;
  - nada fica cinza.
- **Piscina e spa azul-claro #DFF6FE:** água turquesa clara, límpida e luminosa #7CC8D4 sobre revestimento claro Barlavento, com ondulações sutis. A prainha fica mais rasa e mais clara, com borda nítida.

**JARDINS — paisagismo exuberante dentro do lote**

Dentro do lote, até os muros de divisa, toda área branca não pavimentada vira jardim paisagístico, como na imagem 2:
- gramado natural #6E9150, verde vivo e uniforme, com textura real de grama, cobrindo toda área não pavimentada;
- touceiras densas de plantas tropicais vistas de cima (palmeiras, costela-de-adão, filodendros, estrelícias, samambaias) nos cantos do lote;
- faixas de plantio nas laterais da casa: junto à garagem e ao quarto do motorista, e em volta do canto do escritório;
- a jardineira do jardim de inverno e o jardim sob a escada principal cheios de plantas tropicais;
- no resto, gramado aberto, sem copas grandes de árvore no meio do gramado.

A vegetação fica dentro do lote e nunca cobre a casa, a piscina, os decks, os caminhos ou o acesso de veículos. O contorno do lote se mantém, e fora do lote fica papel branco limpo.

**MÓVEIS**

Ficam exatamente como estão representados na base:
- o mesmo desenho refinado, com cada contorno, almofada e detalhe;
- mesma posição, tamanho e orientação;
- sem simplificar, trocar ou reestilizar.

Dentro das formas que já existem, ganham materiais reais de alto padrão numa paleta calma, como na imagem 2: estofados creme e off-white em linho e bouclé, mesas de carvalho claro, cadeiras brancas no jantar, detalhes em metal preto e tapete redondo creme onde houver tapete desenhado.

**PAREDES, VIDROS, JANELAS, GRADIS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, bordas retas e nítidas, espessura como desenhada; alvenaria fechada, sem TV. A borda de cima do estar é uma parede preta contínua, com uma janela curta no canto superior esquerdo.
- **Paredes de vidro e janelas:** cada uma exatamente onde a base mostra, como linha fina de vidro cinza-claro #D6D6D3 entre duas linhas finas de caixilho preto, nítida e contínua.
- **Gradis do corredor de serviço:** barras finas de metal preto entre pequenos postes quadrados; linha escura pontilhada fina e nítida, vazada.
- **Continuam como desenhados:** os arcos das portas, o zigue-zague dos brises (como lâminas finas de alumínio escuro), os X tracejados dos vazios, a grade tracejada do pergolado e os muros cinza-escuros.
- **Pilares:** os pontos rosa e o quadrado rosa viram pilares pretos sólidos.
- **Linhas removidas:** as linhas finas e longas tracejadas de recuo e as curvas de nível.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara, uniforme, com cor de luz do dia natural e sem sombra projetada de nenhum tipo. Os materiais se leem por textura, cor e brilho. Cores vivas e naturais, sem texto.

**Evitar:**
- redesenhar, mover, acrescentar ou remover parede, janela, porta ou móvel;
- mudar a forma do lote;
- vegetação em cima da casa, da piscina, dos decks ou dos pisos;
- cinza sobrando nas áreas de Bege Bahia ou no acesso de veículos;
- piso em cor chapada ou em quadrados lisos;
- linhas de vidro, janelas ou gradis borrados ou interrompidos;
- móveis simplificados ou reestilizados;
- azul fora da piscina e do spa;
- sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
Two input images. Image 1 is the floor plan to edit: it defines the geometry and layout, and you follow it exactly. Image 2 is a style reference of the same house: copy its look — the warm cream stone, the light travertine, the dark brown granite, the caramel cobblestone driveway, the green lawn with clusters of tropical plants, the clean cream-and-oak furniture rendering — but not its geometry. Where the two differ, image 1 wins.

Edit image 1 into a rich, photorealistic humanized presentation plan (planta humanizada) for a luxury residence. This is an edit of image 1, not a new drawing: keep the same framing and scale, the same lot outline, and every wall, window, door, stair, column, line, furniture piece, car and the pool exactly where they are, at the same size and shape. What changes is the finish: floors, water, gardens and furniture materials become real, high-end and full of life.

FLOORS — real photographed materials, each exactly inside its own outline
Every floor reads as real stone or wood photographed from above: visible veining, crystals or grain, real slab joints, natural variation from slab to slab, and the soft sheen of its finish. No floor stays a flat colour or a pattern of plain squares.
- Greige #DCD9CA areas (living, dining, veranda, halls, main stair, gourmet, powder room, veranda bathroom): honed Travertino Romano #D9CBB3 — warm ivory-beige with soft horizontal veining in honey and light taupe, tiny filled pores and gentle tone shifts; slabs about 60 × 120 cm in a straight grid, fine 2 mm joints; satin sheen.
- Mauve #BFA79F areas (kitchen, laundry, pantry, service stair, driver's room and bath, garage): polished Marrom Tabaco granite #4A3426 — deep tobacco brown with a dense, coarse grain of black, dark-amber and cream crystals; slabs about 60 × 60 cm, fine dark joints; glossy polished sheen with soft reflections.
- Light grey #E8E8E8 areas (pool deck, external hall, stepping slabs, steps below the spa deck) and the pool and spa copings: Bege Bahia marble #D8CDB4 — the grey legend fill becomes warm cream-beige stone with soft cloudy tones, fine speckles and small fossil marks; matte non-slip; slabs about 60 × 60 cm with 3 mm joints; lawn in the joints between the stepping slabs. Nothing stays grey.
- Brown hatched #AE8863 area around the spa: natural hardwood deck #9A6B47 — boards about 14 cm wide running exactly along the hatching, visible straight grain, staggered joints, thin dark gaps, slight tone variation between boards.
- Grey dotted hatch (driveway, garage access and the uncovered service passage between the two railings): caramel Portuguese cobblestone (pedra portuguesa) #B98A55 — the grey dots become a warm caramel-and-honey mosaic of small irregular hand-cut stones with sand joints. Nothing stays grey.
- Pale blue #DFF6FE pool and spa: clear, bright light-turquoise water #7CC8D4 over light Barlavento tiles, with subtle surface ripples; the wet deck (prainha) shallower and lighter, with a crisp edge.

GARDENS — lush landscaping inside the lot
Inside the lot, up to the boundary walls, every unpaved white area becomes a landscaped garden, as in image 2: a lush, evenly green natural lawn #6E9150 with real grass texture covers every unpaved area; dense clusters of tropical plants seen from above (palms, monstera, philodendron, bird-of-paradise, ferns) fill the lot corners and run as planting strips along the sides of the house — beside the garage and the driver's room, and around the home-office corner; the winter-garden planter and the garden under the main stair are full of tropical plants; elsewhere the lawn stays open, with no large tree canopies over it. Vegetation stays inside the lot and never covers the house, the pool, the decks, the paths or the driveway; the lot outline keeps its shape; outside the lot stays clean white paper.

FURNITURE
Kept exactly as represented in the input — the same refined drawings with every outline, cushion and detail, the same position, size and orientation; not simplified, replaced or restyled. Inside the existing shapes, give them real high-end materials in a calm palette, as in image 2: cream and off-white linen and bouclé upholstery, light natural oak tables, white dining chairs, black metal details, and a round cream rug where a rug is drawn.

WALLS, GLASS, WINDOWS, RAILINGS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; closed masonry with no TV. The top edge of the living room is a continuous black wall with one short window in its top-left corner.
- Glass walls and windows: every one exactly where the input shows it, as a thin pale-grey glass line #D6D6D3 between two thin black aluminium frame lines — crisp and continuous.
- Service-passage railings (gradil): slim black metal bars between small square posts, read as a crisp thin dark dotted line, see-through.
- Door arcs, the zig-zag brise line (as dark slim aluminium blades), the dashed void X's, the dashed pergola grid and the dark grey boundary walls stay as drawn. Pink column dots and the pink square become solid black columns. The long thin dashed setback lines and the faint terrain contours are removed.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours; no text.

Avoid: redrawing, moving, adding or removing any wall, window, door or furniture piece; changing the lot shape; vegetation over the house, the pool, the decks or the paving; any grey left on the Bege Bahia areas or the driveway; flat colour fills or plain-square floors; blurred or broken glass lines, windows or railings; simplified or restyled furniture; blue outside the pool and spa; shadows; perspective; text.
```

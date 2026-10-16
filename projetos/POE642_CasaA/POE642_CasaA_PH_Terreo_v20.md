# POE 642 · Casa A · Térreo — prompt v20
_13/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG) e GPT, com uma única imagem de entrada._

**Imagem de entrada:** `POE642_CasaA_BASE_Terreo_v3_vidros_neutros_16x9.png`
Enquanto o `gerar_bases.py` não rodar no PDF original, monte essa imagem no Photoshop a partir da v3 atual: *Imagem › Tamanho da tela* → 6905 × 3884 px, âncora central, extensão branca.

**Da v19 para a v20:**
- A entrada passa a ser lida pela legenda de cores da planta. Cada cor chapada é um material: Travertino #DCD9CA, granito marrom #BFA79F, madeira #AE8863, Bege Bahia #E8E8E8 e revestimento da piscina #DFF6FE. O Quartzito Aura não entra no Térreo.
- Piscina e spa com revestimento Barlavento azul-claro, no lugar da pedra Hitam. A água fica turquesa clara #7CC8D4. Essa cor da água é uma estimativa minha; ajusto se você tiver uma foto do Barlavento.
- Os dois "lavabos" ganharam nomes distintos: o **lavabo** ao lado do escritório (no EN, *powder room*) e o **lavatório junto ao gourmet** (no EN, *washbasin room by the gourmet area*).
- Elevador e shaft, logo abaixo da escada principal, descritos como caixas fechadas.
- Paredes e vidros: sem mudança, vale a base.

**Da v18 para a v19:** as bordas da piscina (incluindo a prainha) e do spa passam a ser em mármore Bege Bahia #D8CDB4, fosco antiderrapante. Isso entrou nos materiais, na conferência final e no "Avoid". O resto é igual à v18.

**Da v17 para a v18 (só o formato mudou; nenhum elemento foi tirado):**
- O verbo "transform" saiu, porque os guias de edição o leem como "mude tudo". Agora a tarefa é "aplicar materiais sobre esta planta exata".
- O que era proibição virou descrição do estado desejado, conforme a recomendação do Google. As negações caíram de 55 para 9, quase todas no bloco "Avoid" do fim.
- O texto ficou em blocos curtos e rotulados e encolheu de ~1.980 para ~1.650 palavras, com as mesmas cores, materiais e ambientes.
- O enquadramento é da base 16:9 com margem branca.
- O item 14 do Miro (alvenaria vedada, sem TV) agora aparece por escrito.

---

## Versão de validação (PT, só para leitura)

**1 · TAREFA**
Aplicar materiais fotorrealistas sobre esta planta exata do térreo. A imagem de entrada é o desenho final: todas as linhas ficam onde estão e mudam só as superfícies (pisos, água, grama, acabamento dos móveis). Saída: planta de apresentação vista de cima, ortográfica, para residência de alto padrão. Mesmo enquadramento, mesma escala e mesma posição de cada pixel da entrada, centralizada em papel branco que preenche o quadro 16:9.

**2 · COMO LER A ENTRADA**
- Faixas pretas sólidas: paredes de alvenaria, totalmente fechadas.
- Faixas finas cinza-claro com contorno preto: vidro (janelas, paredes de vidro, painéis de correr, divisórias de vidro).
- Arcos pretos finos de quarto de círculo com a linha da folha: portas de giro opacas.
- Cores chapadas = legenda de materiais do piso. Cada área recebe o material da sua cor:
  - bege-acinzentado #DCD9CA: mármore Travertino;
  - malva #BFA79F: granito marrom (Marrom Tabaco);
  - marrom #AE8863, com hachura horizontal fina, à esquerda da piscina e em volta do spa: deck de madeira do spa;
  - cinza-claro #E8E8E8: mármore Bege Bahia (por exemplo, o deck em volta da piscina, onde estão as duas espreguiçadeiras, e as placas de pedestres à direita);
  - azul-claro #DFF6FE: piscina e spa (revestimento Barlavento).
- Hachura de pontinhos cinza: acesso de veículos. Retângulos cinza grandes e separados, à direita: placas do acesso de pedestres até a casa.
- Pontos rosa e o quadrado rosa: pilares.
- Quadrados com X tracejado sobre a varanda: projeção dos vazios de pé-direito duplo.
- Grade de quadrados finos sobre o deck da piscina, entre a piscina/prainha e a varanda gourmet: projeção do pergolado.
- Linha em zigue-zague na borda esquerda da varanda gourmet: fileira de brises rotativos.
- Áreas brancas não construídas dentro do lote: jardim. Linhas escuras grossas nas bordas de cima e de baixo: muros de divisa.
- Símbolos brancos de móveis: o layout de mobiliário.

**3 · MANTER EXATAMENTE**
- Contorno, paredes e espessuras, vãos, portas, janelas, escadas, piscina, móveis (posição, tamanho e orientação), carros e limites do lote ficam exatamente como desenhados.
- Toda parede preta continua poché preto sólido #111111, de bordas nítidas: alvenaria 100% vedada, sem TV e sem nada fixado nela.
- Toda faixa de vidro continua uma linha fina cinza-claro #D6D6D3 entre bordas finas pretas de caixilho, mais clara e mais fina que as paredes.
- Pilares em preto sólido: os pontos viram pilares redondos e o quadrado, pilar quadrado.
- A planta contém só o que está desenhado: cada ambiente, parede, porta, janela e móvel aparece uma vez, no lugar que o desenho indica.
- A prancha não tem letreiro de nenhum tipo (nomes de ambientes, números, cotas, logos, marca d'água).
- Somem as linhas finas e longas tracejadas de recuo e as curvas de nível cinza-claro. Ficam o X tracejado dos vazios e a grade tracejada do pergolado.

**4 · MATERIAIS**
- **Estar, jantar, varanda, hall interno, escada principal, espaço gourmet, lavabo, banho da varanda (toda área bege-acinzentada #DCD9CA):** Travertino Romano #D9CBB3, levigado (rugosidade 0,45), veios horizontais suaves, placas grandes com juntas finas.
- **Cozinha, área de serviço, despensa, escada de serviço, quarto e banho do motorista, garagem (toda área malva #BFA79F):** granito Marrom Tabaco, marrom-tabaco profundo #4A3426 com cristais pretos e âmbar-escuros, polido (rugosidade 0,2). Uma pedra claramente marrom.
- **Hall externo e placas do acesso de pedestres à direita:** mármore Bege Bahia #D8CDB4, bege-creme quente com pontinhos claros e pequenas marcas de fóssil, fosco antiderrapante (rugosidade 0,6), com grama nas juntas entre as placas.
- **Deck da piscina** (piso cinza-claro com as espreguiçadeiras): Bege Bahia #D8CDB4, fosco antiderrapante, placas grandes com juntas finas.
- **Escada abaixo do deck do spa** (o lance curto na borda de baixo do deck do spa, descendo para a grama): Bege Bahia #D8CDB4, fosco antiderrapante, a mesma pedra do deck da piscina.
- **Deck do spa** (a hachura horizontal em volta do spa): madeira natural #9A6B47, fosca, réguas longas na horizontal seguindo exatamente a hachura, frestas finas.
- **Acesso de veículos, acesso em nível à garagem e corredor de serviço descoberto:** pedra portuguesa caramelo #B98A55, pedras pequenas e irregulares, juntas aparentes. O corredor de serviço é o retângulo comprido abaixo da lavanderia, entre os dois gradis pretos, da porta da lavanderia até o muro de baixo, logo à esquerda do acesso de veículos (tem um X tracejado na entrada). Ele leva a mesma pedra portuguesa caramelo do acesso de veículos, contínua com ela.
- **Piscina e spa:** revestimento Barlavento azul-claro #DFF6FE, de modo que a água fica turquesa clara, límpida e luminosa #7CC8D4, com o revestimento claro aparecendo através dela.
- **Bordas da piscina e do spa:** mármore Bege Bahia #D8CDB4, fosco antiderrapante. É uma faixa de borda nítida e contínua, bege-creme, contornando todo o perímetro da piscina (incluindo a prainha) e do spa, entre a água e os decks em volta. Uma junta fina a separa do deck.
- **Jardim:** grama natural #6E9150 com canteiros e arbustos tropicais.
- **Muros de divisa:** cinza-escuro sólido #3A3A3A.
- **Móveis:** linho off-white #EDE8DF, carvalho natural #A8865E, metal preto. Carros como desenhados, realistas, vistos de cima.

**5 · PAREDES E VIDROS, AMBIENTE POR AMBIENTE**
- **Lounge da varanda** (ambiente no alto à esquerda: duas poltronas, sofá curvo e sofá de três lugares): lado de cima é uma parede sólida contínua; lado esquerdo aberto para o deck da piscina; lado de baixo aberto para a varanda coberta.
- **Coluna da varanda coberta** (lounge, poltronas e mesas de jantar da varanda): toda a borda esquerda é aberta. O travertino encontra direto o deck de Bege Bahia, sem caixilho e sem linha.
- **Fachada principal do estar e jantar:** uma parede de vidro longa e contínua, de painéis de correr com caixilhos pretos finos. Desce na vertical da parede de cima até a cozinha, entre a coluna da varanda coberta (à esquerda) e o estar/jantar interno (à direita).
- **Borda de cima do estar:** uma janela curta no canto junto ao lounge da varanda, depois parede sólida até o lavabo. Um painel alto de marcenaria branca ao longo do lado direito do estar.
- **Lavabo** (entre o estar e o escritório):
  - paredes sólidas;
  - uma janela na parede de cima;
  - porta de giro simples no canto inferior esquerdo;
  - claraboia em retângulo tracejado fino;
  - bancada de Travertino Romano com cuba esculpida na mesma pedra.
- **Escritório:**
  - parede de cima sólida na parte esquerda e janela na parte direita;
  - canto superior direito envidraçado: a parede direita é vidro do canto até cerca de um terço do comprimento, depois sólida;
  - cortina de linho claro ao longo desse vidro;
  - parede de baixo sólida;
  - porta de giro no canto inferior esquerdo, vinda do hall;
  - estante branca em L ao longo da parede esquerda.
- **Entrada principal:** porta pivotante grande e opaca entre o hall interno e o hall externo.
- **Escada principal:** paredes sólidas em cima e embaixo; paredes de vidro de piso a teto no lado esquerdo (voltado para o jantar) e no lado direito (voltado para o jardim).
- **Elevador e shaft** (as caixinhas logo abaixo da escada principal): caixas fechadas por paredes, como desenhadas.
- **Cozinha:** paredes sólidas em cima e embaixo. Na parede esquerda, uma abertura envidraçada no meio, voltada para o jantar/gourmet. Na parede direita, uma porta de giro e depois um painel de vidro comprido ao lado das cubas.
- **Fachada de baixo (serviço):** janelas pequenas nas paredes de baixo do banho da varanda, do lavatório junto ao gourmet e da lavanderia, exatamente onde aparecem as faixas cinza finas. O resto dessa fachada é parede sólida.
- **Garagem:** lado direito em parede sólida com uma única janela no meio; frente aberta para o acesso de veículos.
- **Gradis do corredor de serviço:** as duas linhas duplas finas com postes pequenos, do pátio de serviço descoberto até o muro de baixo, são gradis de metal preto vazados. Têm barras verticais finas entre postes quadrados pequenos e, vistos de cima, aparecem como uma linha escura pontilhada fina.
- **Varanda gourmet:** a borda esquerda é a fileira de brises verticais rotativos de alumínio preto ao longo do zigue-zague, bem visíveis como lâminas escuras e finas.

**6 · ELEMENTOS ESPECÍFICOS**
- Brises rotativos na varanda gourmet, como no bloco 5.
- **Áreas verdes:**
  - o jardim de inverno (a faixa estreita de jardineira abaixo do lavatório junto ao gourmet) cheio de plantas tropicais exuberantes;
  - todo o jardim em volta da casa verde: grama à esquerda do deck e do gourmet, jardim sob a escada principal, jardim ao lado do quarto do motorista e grama no lado direito do lote.
- **Vazios de pé-direito duplo sobre a varanda:** contorno tracejado fino e X tracejado sobre o travertino, com o piso continuando por baixo.
- **Prainha:** a parte de baixo do retângulo da piscina, separada por uma linha fina, é um degrau raso. Água mais clara e rasa, com borda nítida e bem visível para a parte funda, seguindo exatamente o retângulo da entrada.
- **Pergolado:** a grade entre a piscina/prainha e a varanda gourmet aparece só como linhas tracejadas finas em quadrados sobre o deck de Bege Bahia, exatamente como a grade da entrada. É uma linha de projeção plana, com o deck todo visível por baixo.
- **Acesso à garagem:** a pedra portuguesa caramelo segue em nível até dentro da garagem, sem rampa.

**7 · LUZ, CÂMERA, COR**
- **Luz:** chapada, uniforme e sem sombras, de apresentação; toda superfície iluminada por igual. Sem direção de sol, sem sombra projetada ou de contato, sem oclusão ambiente, sem vinheta. Os materiais se leem só por textura e cor.
- **Câmera:** vista de cima ortográfica estrita a 90°, enquadramento idêntico ao da entrada, sem inclinação e sem profundidade de campo.
- **Cor:** branco neutro-quente ~5000 K, saturação natural, papel branco limpo fora do lote.
  - Travertino e Bege Bahia ficam bege quente.
  - Marrom Tabaco fica marrom profundo.
  - A pedra portuguesa fica caramelo.
  - O deck do spa fica madeira natural.
  - A grama fica verde natural.
  - O vidro fica cinza-claro neutro.
  - A água da piscina e do spa, turquesa clara, é a única superfície azul da imagem.

**8 · CONFERÊNCIA FINAL**
- Preto = parede fechada; faixa cinza fina = vidro.
- Paredes e vidros como no bloco 5; pilares pretos; materiais como no bloco 4.
- Corredor de serviço em pedra portuguesa caramelo; escada abaixo do deck do spa em Bege Bahia.
- Deck da piscina em pedra e deck do spa em madeira.
- Bordas da piscina e do spa em Bege Bahia; revestimento da piscina e do spa claro (Barlavento).
- Pergolado e vazios só em tracejado; jardins verdes.
- Sem sombras, sem letreiro, mesmo enquadramento no papel branco 16:9.

**Evitar:**
- azul ou ciano fora da água da piscina e do spa;
- qualquer letreiro;
- sombras e perspectiva;
- paredes, portas, janelas ou móveis acrescentados, movidos ou removidos;
- parede virando vidro ou vidro virando parede;
- gradis virando parede ou vidro;
- vigas sólidas no pergolado;
- hall externo ou placas escuros;
- granito de serviço com cara de preto;
- acesso de veículos ou corredor de serviço cinza ou em pedra clara;
- deck da piscina ou escada abaixo do spa em madeira;
- deck do spa em pedra;
- borda da piscina ou do spa escura, cinza ou de madeira;
- revestimento da piscina ou do spa escuro ou preto.

---

## Prompt para o motor (EN, colar inteiro)

```
1 · TASK
Render photorealistic materials onto this exact ground-floor plan. The input image is the final drawing: every line stays where it is and only the surfaces change — floors, water, lawn, furniture finishes. Output: a strict top-down orthographic presentation plan for a luxury residence, with the same framing, the same scale and the same pixel position as the input, centred on clean white paper that fills the 16:9 frame.

2 · HOW TO READ THE INPUT
- Solid black bands: masonry walls, fully closed.
- Thin pale-grey strips outlined in black: glass (windows, glass walls, sliding panels, glass partitions).
- Thin black quarter-circle arcs with a leaf line: opaque swing doors.
- Flat colour fills are the floor-material legend of the drawing; every floor area takes the material of its colour:
  - greige #DCD9CA: Travertino Romano marble;
  - mauve #BFA79F: Marrom Tabaco brown granite;
  - brown #AE8863 with fine horizontal hatching, left of the pool and wrapping around the spa: the spa wooden deck;
  - light grey #E8E8E8: Bege Bahia marble — for example the paving around the pool where the two sun loungers stand (the pool deck) and the stepping slabs on the right;
  - pale sky blue #DFF6FE: pool and spa (Barlavento lining).
- Small grey dotted hatch: vehicle driveway. Large separate grey rectangles on the right: pedestrian stepping slabs leading to the house.
- Pink dots and the pink square: structural columns.
- Dashed X squares over the veranda: projection of the double-height voids above.
- Grid of thin squares over the pool deck, between the pool/wet deck and the gourmet veranda: projection of the pergola above.
- Zig-zag line on the left edge of the gourmet veranda: a row of rotating brise blades.
- White unbuilt areas inside the lot: garden. Thick dark lines at the top and bottom edges: boundary walls.
- White furniture symbols: the furniture layout.

3 · KEEP EXACTLY
Outline, walls and their thickness, openings, doors, windows, stairs, pool, furniture (position, size, orientation), cars and lot boundaries stay exactly as drawn. Every black wall stays solid black #111111 poché with crisp edges: 100% closed masonry, with no TV and nothing mounted on it. Every glass strip stays a thin pale-grey line #D6D6D3 between thin black aluminium frame edges, lighter and thinner than the walls. Columns become solid black: round columns for the dots, a square column for the square. The plan contains only what is drawn: every room, wall, door, window and piece of furniture appears once, where the drawing places it. The sheet is unlabelled, with no lettering of any kind (room names, numbers, dimensions, logos, watermark). The long thin dashed setback lines and the faint grey terrain contours disappear; the dashed void X's and the dashed pergola grid stay.

4 · MATERIALS
- Living, dining, veranda, internal hall, main stair, gourmet space, powder room, veranda bathroom (every greige #DCD9CA area): Travertino Romano marble #D9CBB3, honed (roughness 0.45), soft horizontal veining, large-format slabs with fine joints.
- Kitchen, laundry, pantry, service stair, driver's room and bath, garage (every mauve #BFA79F area): Marrom Tabaco granite, deep tobacco-brown base #4A3426 with black and dark-amber crystals, polished (roughness 0.2) — a clearly brown stone.
- External entrance hall and the pedestrian stepping slabs on the right: Bege Bahia marble #D8CDB4, warm cream-beige with fine light speckles and small natural fossil marks, matte non-slip (roughness 0.6); lawn in the joints between the stepping slabs.
- Pool deck (the light-grey paving with the sun loungers): Bege Bahia marble #D8CDB4, matte non-slip, large slabs with fine joints.
- Steps below the spa deck (the short flight at the bottom edge of the spa deck, leading down to the lawn): Bege Bahia marble #D8CDB4, matte non-slip, the same stone as the pool deck.
- Spa deck (the horizontal hatching around the spa): natural hardwood decking #9A6B47, matte, long boards running horizontally exactly along the hatching lines, thin gaps.
- Vehicle driveway, the level access to the garage and the uncovered service passage: caramel Portuguese cobblestone mosaic (pedra portuguesa) #B98A55, small irregular stones, visible joints. The service passage is the long rectangle below the laundry, between the two black railings, running from the laundry door down to the bottom boundary wall just left of the driveway (it carries a dashed X in the input); it is paved in the same caramel cobblestone as the driveway, continuous with it.
- Pool and spa: Barlavento pool lining in pale sky blue #DFF6FE, so the water reads clear, bright light turquoise #7CC8D4, with the light lining showing through it.
- Pool and spa edges: Bege Bahia marble #D8CDB4 coping, matte non-slip — a crisp, continuous cream-beige coping band running around the full outline of the pool (including the wet deck) and of the spa, between the water and the surrounding decks, with a fine joint line separating it from the deck.
- Garden: natural lawn #6E9150 with planting beds and tropical shrubs.
- Boundary walls: solid dark grey #3A3A3A.
- Furniture: off-white linen #EDE8DF, natural oak #A8865E, black metal. Cars as drawn, realistic, seen from above.

5 · WALLS AND GLASS, ZONE BY ZONE
- Veranda lounge (top-left room with two armchairs, a curved sofa and a three-seat sofa): its top side is one continuous solid wall; its left side opens to the pool deck; its bottom side opens to the covered veranda.
- Covered veranda column (veranda lounge, veranda armchairs, veranda dining tables): its whole left edge is open — the travertine floor meets the Bege Bahia pool deck directly, with no frame and no line.
- Main façade of the living and dining room: one long continuous glass wall of sliding panels with thin black frames, running vertically from the top wall down to the kitchen, between the covered veranda column on the left and the indoor living and dining room on the right.
- Top edge of the living room: one short window in the corner next to the veranda lounge, then solid wall up to the powder room. A tall white built-in cabinetry panel runs along the right side of the living room.
- Powder room (lavabo, between the living room and the home office): solid walls; one window in its top wall; a single swing door at its lower left; the skylight shown as a thin dashed rectangle; a Travertino Romano vanity with a sculpted basin carved in the same stone.
- Home office: top wall solid on the left part and a window on the right part; a glazed top-right corner — the right wall is glass from the corner down to about one third of its length, then solid wall; a light linen curtain along that glass; bottom wall solid; a swing door at the lower left from the hall; white L-shaped built-in shelving along the left wall.
- Main entrance: a large opaque pivoting door between the internal hall and the external hall.
- Main stair: solid walls at top and bottom; full-height glass walls on its left side (facing the dining room) and on its right side (facing the garden).
- Elevator and shaft (the small closed boxes just below the main stair): closed solid boxes with walls all round, as drawn.
- Kitchen: solid walls on top and bottom; its left wall has one glazed opening in the middle towards the dining/gourmet area; its right wall has a swing door and then a long glass panel alongside the sinks.
- Bottom (service) façade: small windows in the bottom walls of the veranda bathroom, the washbasin room by the gourmet area and the laundry, exactly where the thin grey strips appear; the rest of that façade is solid wall.
- Garage: right side is a solid wall with one single window in the middle; the front opens to the driveway.
- Service passage railings: the two thin double lines with small posts running from the uncovered service yard down to the bottom boundary wall are see-through black metal railings (gradil) — slim vertical bars between small square posts, read from above as a thin dark dotted line.
- Gourmet veranda: its left edge is the row of vertical rotating black aluminium brise blades along the zig-zag line, clearly visible as dark slim blades.

6 · SPECIFIC ELEMENTS
- Rotating brises on the gourmet veranda, as in section 5.
- Green areas: the winter garden (the narrow planter strip below the washbasin room by the gourmet area) is full of lush tropical plants; every garden around the building is green — lawn left of the deck and gourmet area, garden under the main stair, garden beside the driver's room, lawn on the right side of the lot.
- Double-height voids above the veranda: a thin dashed outline and a dashed diagonal X drawn over the travertine floor, the floor continuing underneath.
- Wet deck (prainha): the lower section of the pool rectangle, separated by a thin line, is a shallow ledge with lighter shallow water and a crisp, clearly visible edge to the deep pool, following exactly the rectangle in the input.
- Pergola: the grid between the pool/wet deck and the gourmet veranda appears only as thin dashed square lines over the Bege Bahia pool deck, exactly as the grid in the input — a flat projection line, with the deck fully visible underneath.
- Garage access: the caramel cobblestone continues level all the way into the garage, with no ramp.

7 · LIGHT, CAMERA, COLOUR
Flat, even, shadowless presentation lighting: every surface uniformly lit, with no sun direction, cast shadows, contact shadows, ambient occlusion or vignetting; materials read by texture and colour alone. Strict orthographic top view at 90°, framing identical to the input, no tilt, no depth of field. Neutral-warm white balance around 5000 K, natural saturation, clean white paper outside the lot. Travertine and Bege Bahia stay warm beige, Marrom Tabaco stays deep brown, the cobblestone stays caramel, the spa deck stays natural wood, the lawn stays natural green, the glass stays neutral pale grey. The pool and spa water, clear light turquoise, are the only blue surfaces in the whole image.

8 · FINAL CHECK
Black = closed wall, thin grey strip = glass; walls and glass zone by zone as section 5; columns black; materials as section 4; service passage in caramel cobblestone; steps below the spa deck in Bege Bahia; pool deck in stone and spa deck in wood; pool and spa edges in Bege Bahia coping; light Barlavento pool and spa lining; pergola and voids as dashed lines only; gardens green; shadowless; unlabelled; same framing on the white 16:9 sheet.
Avoid: any blue or cyan outside the pool and spa water; lettering of any kind; shadows; perspective or 3D tilt; walls, doors, windows or furniture added, moved or removed; a wall turned into glass or glass turned into a wall; railings turned into walls or glass; solid pergola beams; a dark external hall or dark stepping slabs; service granite that reads as black; a grey or light-stone driveway or service passage; a wooden pool deck or wooden steps below the spa deck; a stone spa deck; a dark, grey or wooden edge around the pool or spa; a dark or black pool or spa lining.
```

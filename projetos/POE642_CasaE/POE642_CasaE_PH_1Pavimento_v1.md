# POE 642 · Casa E · 1º Pavimento — prompt v1 (só a imagem base)
_16/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png`.
- **Origem:** foi gerada do PDF do cliente (`642 - 1º PAVIMENTO - CASA E.pdf`), na mesma folha e no mesmo enquadramento do Térreo.
- **Texturas:** a base já traz a prévia dos pisos e da marcenaria.
  - O vinílico, o Bege Bahia e o travertino vêm dos renders aprovados da Casa A; a marcenaria areia, do Térreo retocado da Casa D.
  - O quartzito Aura foi gerado por código (`fontes_procedurais.quartzito_aura`), na cor da legenda do cliente.
  - O prompt manda manter cada material e só torná-lo fotorrealista.

**Pisos (definidos por você em 16/10/26):**
- **Vinílico (Durafloor City Petra, o mesmo da área íntima do 1º Pavimento da Casa A):** todo o laranja do PDF — suítes, closets, closet master, rouparia, sala íntima e circulação.
- **Quartzito Aura:** os cinco banhos (master e suítes 1 a 4).
- **Bege Bahia:** as três varandas (a grande à esquerda e as duas varandinhas à direita) e a bancada da copinha.

**Padrões das outras casas:**
- **Armários:** os brancos com diagonal do PDF, em marcenaria areia, até o teto.
- **Escada:** travertino, como a escada interna do Térreo.
- **Vazios:** em cinza-escuro, com o X tracejado claro, como na Casa A.
  - o de baixo da escada, sobre o jardim interno do Térreo;
  - o do pé-direito duplo do hall de entrada.

**Lições das Casas A a E aplicadas:**
- escala existente em destaque, com a posição medida na base;
- ambientes descritos por posição;
- "nada é acrescentado";
- luz chapada, sem sombra;
- armário até o teto (linha diagonal) chapado, sem sombra de móvel baixo;
- vazios como abertura escura, nunca piso;
- elevador e shaft fechados;
- louças, cubas e chuveiros exatamente como desenhados.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta do 1º pavimento a editar. Ela define a geometria, o layout e os materiais, e deve ser seguida exatamente.

**Antes de tudo: mantenha a escala existente.** A planta sai exatamente do mesmo tamanho e no mesmo lugar da imagem de entrada, sem aproximar, recortar nem centralizar.

Transforme a planta numa planta humanizada de apresentação do **1º pavimento** de uma residência de alto padrão, rica e fotorrealista. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala;
- cada parede, vidro, porta, escada, linha, móvel, louça e armário exatamente onde estão, com o mesmo tamanho e a mesma forma;
- nada é acrescentado: nenhum ambiente, parede, porta, escada, móvel ou objeto novo.

Os pisos e os armários já aparecem na planta com o material final. Cada um mantém o material, a cor e a direção das réguas e dos veios, e só ganha acabamento fotorrealista, com juntas reais e brilho sutil.

**ESCALA E ENQUADRAMENTO:** mantenha a escala existente.
- A planta fica exatamente na mesma posição e com o mesmo tamanho na imagem, com o mesmo fundo branco em volta.
- **Posição na imagem:** a casa vai de ~30% a ~69% da largura e de ~20% a ~74% da altura.
  - As linhas tracejadas finas do lote ficam a ~7% e a ~92,5% da largura e a ~95% da altura, como desenhadas.
  - A imagem final tem o mesmo formato 16:9 da entrada.
- Não aproxime, não recorte, não centralize, não amplie, não reduza e não gire nada.
- Mantêm a escala desenhada:
  - a espessura das paredes;
  - o tamanho de cada ambiente, móvel, louça e armário;
  - a largura das réguas e das placas de piso.

**O FUNDO:** fora da casa e das varandas, o fundo fica branco puro e chapado #FFFFFF, inclusive a área branca abaixo da sala íntima. Sem grama, vegetação, piso ou sombra. As linhas tracejadas do lote ficam finas, como desenhadas.

**OS AMBIENTES, ONDE FICA CADA UM**

**Varanda grande (Bege Bahia):** a faixa larga ao longo de todo o lado esquerdo da casa, de borda a borda.

**Coluna da esquerda (vinílico), de cima para baixo:**
1. **Suíte master:** no alto à esquerda. Cama de casal com dois criados redondos, poltrona com mesinha e o móvel baixo junto à parede de baixo.
2. **Suíte (à esquerda, no meio):** cama de casal e a escrivaninha branca com cadeira junto à parede da direita.
3. **Dois banhos (quartzito Aura):** lado a lado na vertical, abaixo dessa suíte, cada um com bacia, cuba na bancada e chuveiro como desenhados.
4. **Dois closets:** à direita desses banhos, com os armários areia.
5. **Suíte de baixo à esquerda:** cama de casal e a escrivaninha com cadeira.

**Bloco de cima, no centro (da esquerda para a direita):**
- **Banho master (quartzito Aura):** a sala alta acima da casa. Banheira oval solta no alto, bancada com as cubas na parede da direita, a floreira com plantas ao longo da parede da esquerda, o box com os dois chuveiros de teto (os quadradinhos) embaixo e a bacia na salinha de baixo à esquerda.
- **Closet master:** à direita do banho master. Armários areia na parede de cima e na de baixo, com o piso vinílico entre eles.
- **Elevador, shaft e rouparia:** a fileira abaixo do closet master.
  - o elevador é a caixa branca fechada;
  - o shaft é a faixa estreita com o ziguezague;
  - a rouparia tem piso vinílico, as prateleiras areia à direita e o quadrado tracejado, que fica fino como desenhado.

**Centro:**
- **Circulação (vinílico):** o hall largo que liga as suítes, a sala íntima e a escada.
- **Copinha:** a faixa logo acima da escada, com a bancada de Bege Bahia e a cuba redonda branca, e o armário areia à direita.
- **Escada (travertino):** o lance reto no meio, com os degraus, a linha de caminhamento e a seta, exatamente como desenhados.
- **Vazio da escada:** o retângulo cinza-escuro logo abaixo dela, com o X tracejado claro. É uma abertura de pé-direito duplo sobre o jardim do térreo, não um piso.
- **Sala íntima (vinílico):** embaixo, no centro. Sofá em L, poltrona e duas mesinhas redondas sobre o tapete, o móvel baixo na parede de baixo e, à direita dela, a planta em vaso no canto de baixo da circulação, junto ao vazio do hall.

**Coluna da direita (vinílico), de cima para baixo:**
1. **Suíte de cima à direita:** closet com armários areia em L no canto de cima à esquerda, escrivaninha com cadeira à esquerda e cama de casal no centro. O banho (quartzito Aura) fica no alto à direita, e a varandinha de Bege Bahia, ao longo do lado direito.
2. **Suíte de baixo à direita:** igual à de cima, com o closet em L, a escrivaninha, a cama, o banho no alto à direita e a varandinha à direita.

**Vazio do hall de entrada:** embaixo à direita, o quadrado cinza-escuro com o X tracejado claro e o arco da porta. É o pé-direito duplo do hall do térreo, não um piso.

**PISOS — cada ambiente tem um único piso, exatamente dentro das suas paredes**
- **Vinílico Durafloor City Petra:** suítes, closets, closet master, rouparia, sala íntima e circulação.
  - madeira natural marrom-média e quente, nunca laranja;
  - réguas de ~20 cm na direção das linhas desenhadas, com veio visível e juntas desencontradas;
  - acabamento fosco acetinado.
- **Quartzito Aura:** os cinco banhos.
  - pêssego-claro quente #EAD4BF, quase liso;
  - nuvens suaves e veios finos e claros;
  - placas grandes de ~90 cm com juntas finas;
  - levigado, fosco;
  - nunca rosa forte, laranja ou com manchas.
- **Mármore Bege Bahia fosco:** as três varandas, de borda a borda.
  - creme-bege claro e uniforme, quase liso;
  - só um pontilhado fino e leve e alguns veios finos e claros;
  - sem manchas, nuvens ou pontos escuros.
- **Travertino Romano levigado:** a escada.
  - marfim-bege quente, com veios paralelos e poros pequenos;
  - fosco.

**VAZIOS:** os dois retângulos cinza-escuros (abaixo da escada e o do hall de entrada) são aberturas de pé-direito duplo.
- cinza-carvão chapado #4A4A4A: uma abertura escura, não um piso;
- o X tracejado claro e os guarda-corpos ficam como desenhados.

**MÓVEIS:** exatamente como desenhados, com cada contorno, almofada e detalhe, na mesma posição, tamanho e orientação. Dentro das formas existentes, materiais de alto padrão em paleta calma:
- roupa de cama e estofados em linho e bouclé creme e off-white;
- mesinhas e escrivaninhas de carvalho claro;
- detalhes em metal preto;
- tapete só onde há tapete desenhado.

**MARCENARIA, BANCADAS E LOUÇAS**
- **Armários:** os closets, o closet master, a rouparia e o armário da copinha, até o teto.
  - marcenaria areia fosca #CBB89E, laca lisa;
  - chapados, sem a sombra de um móvel baixo e sem a diagonal desenhada por cima.
- **Bancada da copinha:** mármore Bege Bahia, com a cuba redonda branca.
- **Bancadas dos banhos:** quartzo claro polido #ECE8E1, com pontilhado fino.
- **Louças:** brancas, com metais em preto ou cromado.
  - a banheira oval, as bacias e as cubas exatamente como desenhadas;
  - os dois chuveiros de teto do banho master como placas quadradas;
  - os chuveiros dos outros banhos exatamente onde estão desenhados.

**PAREDES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas e a espessura desenhada. Nenhuma parede nova.
- **Vidros:** linha fina cinza-claro #D6D6D3 entre caixilhos pretos finos, exatamente onde a planta mostra (janelas e portas de vidro das varandas, boxes).
- **Portas:** só as desenhadas, com arco e folha, e nenhuma porta nova.
- **Elevador e shaft:** caixas fechadas, que não são vazios.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara, uniforme, com cor de luz do dia natural e sem sombra projetada. Cores vivas e naturais, sem texto.

**Evitar:**
- **Escala:** aproximar, recortar, centralizar, ampliar, reduzir ou girar a planta, ou mudar o tamanho de paredes, ambientes, móveis, réguas ou placas.
- **Ambientes:** ambientes, paredes, portas, móveis ou objetos novos.
- **Fundo:** cor, textura, grama, vegetação ou sombra fora da casa e das varandas; a área branca abaixo da sala íntima com piso.
- **Pisos:**
  - pisos em cor chapada, ou trocados de material ou de direção;
  - madeira laranja;
  - quartzito rosa forte, laranja ou manchado;
  - Bege Bahia manchado;
  - madeira ou pedra nas varandas que não seja o Bege Bahia.
- **Vazios:** com piso, jardim ou cor clara; elevador ou shaft como vazio escuro.
- **Armários:** na cor do piso, com a diagonal desenhada por cima ou com sombra de móvel baixo.
- **Banhos:** chuveiros de parede, braços ou duchas redondas no banho master; chuveiros a mais; metal ou registro em janela.
- **Geral:** móveis simplificados ou trocados, sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the first-floor plan to edit. It defines the geometry, the layout and the materials, and you follow it exactly.

FIRST OF ALL, KEEP THE EXISTING SCALE: the plan comes out at exactly the same size and in exactly the same place as in the input image — no zooming in, no cropping, no re-centring.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) of the first floor of a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, and every wall, glass line, door, stair, line, furniture piece, sanitary fixture and cabinet exactly where they are, at the same size and shape. Nothing is added: no new room, wall, door, stair, furniture or object. The floors and the cabinets already show their final materials in the plan: keep each one's material, colour and plank or vein direction exactly as it is, and only refine it into a photorealistic surface with real joints and a subtle sheen.

SCALE AND FRAMING
Keep the existing scale. The plan stays exactly where it is in the image and at exactly the same size, with the same white background around it: do not zoom in, crop, re-centre, enlarge, shrink or rotate anything. The house runs from about 30% to 69% of the image width and from about 20% to 74% of the height; the thin dashed lot lines stay at about 7% and 92.5% of the width and at about 95% of the height, as drawn. The output keeps the same 16:9 frame as the input. Wall thickness, the size of every room, furniture piece, fixture and cabinet, and the width of the floor planks and slabs all stay at the drawn scale.

THE BACKGROUND
Outside the house and its balconies the background is pure flat white #FFFFFF, including the white area below the family lounge: no grass, no vegetation, no paving and no shadows. The dashed lot lines stay thin, as drawn.

THE ROOMS AND WHERE THEY ARE
- The large balcony, in Bege Bahia: the wide strip along the whole left side of the house, edge to edge.
- Left column, in vinyl wood, top to bottom: (1) the master suite at the top left — double bed with two round bedside tables, an armchair with a small table, and the low unit by its bottom wall; (2) the middle-left suite — double bed and the white desk with a chair by its right wall; (3) two bathrooms in Aura quartzite, stacked below that suite, each with its toilet, the basin in its counter and the shower as drawn; (4) two closets to the right of those bathrooms, with sand wardrobes; (5) the bottom-left suite — double bed and the desk with a chair.
- Top block in the centre, left to right: the master bathroom in Aura quartzite, the tall room projecting above the house — the freestanding oval bathtub at the top, the counter with the basins along the right wall, the planter with plants along the left wall, the shower at the bottom with the two ceiling rain showers (the small squares), and the toilet in the small room at the bottom left; the master closet to its right, with sand wardrobes along the top wall and the bottom wall and the vinyl floor between them; and, in the row below the master closet, the elevator (the closed white box), the shaft (the narrow strip with the zigzag) and the linen room, with a vinyl floor, the sand shelves on its right and the dashed square kept thin as drawn.
- Centre: the wide circulation hall in vinyl wood, linking the suites, the family lounge and the stair; the kitchenette, the strip just above the stair, with a Bege Bahia counter and the round white basin, and the sand cabinet to its right; the travertine stair in the middle, a single straight flight with its treads, walking line and arrow exactly as drawn; the stair void, the dark grey rectangle just below the stair with the light dashed X — a double-height opening over the ground-floor garden, not a floor; and the family lounge at the bottom centre, in vinyl wood — the L-shaped sofa, the armchair and the two small round tables on the rug, the low unit on the bottom wall and, to its right, the potted plant in the bottom corner of the circulation, next to the entrance-hall void.
- Right column, in vinyl wood, top to bottom: the top-right suite — the closet with L-shaped sand wardrobes in its top-left corner, the desk with a chair on the left and the double bed in the centre, its Aura quartzite bathroom at the top right and its narrow Bege Bahia balcony along the right side; and the bottom-right suite, the same — L-shaped closet, desk, bed, bathroom at the top right and the narrow balcony on the right.
- The entrance-hall void at the bottom right: the dark grey square with the light dashed X and the door arc — the double-height space of the ground-floor entrance hall, not a floor.

FLOORS — each room has exactly one floor, exactly inside its walls
- Durafloor City Petra vinyl wood: the suites, the closets, the master closet, the linen room, the family lounge and the circulation hall. A warm, medium-brown natural wood, never orange; planks about 20 cm wide along the drawn lines, visible grain, staggered joints, matte-satin finish.
- Aura quartzite: the five bathrooms. A warm, light peach stone #EAD4BF, almost plain, with soft clouding and fine light veins; large slabs of about 90 cm with fine joints; honed and matte; never strong pink, orange or blotchy.
- Matte Bege Bahia marble: the three balconies, edge to edge. A light, uniform cream-beige stone, almost plain: only a fine, faint speckle and a few thin light veins; no stains, clouds or dark spots.
- Honed Travertino Romano: the stair. Warm ivory-beige with parallel veining and small natural pores; matte.

VOIDS
The two dark grey rectangles — below the stair and at the entrance hall — are double-height voids. Render them as flat dark charcoal #4A4A4A — a dark opening, not a floor — with the light dashed X and the guardrails kept as drawn.

FURNITURE
Kept exactly as drawn — every outline, cushion and detail, the same position, size and orientation; not simplified, replaced or restyled. Inside the existing shapes, give them real high-end materials in a calm palette: cream and off-white linen and bouclé bedding and upholstery, light natural oak bedside tables and desks, black metal details, and a rug only where a rug is drawn.

JOINERY, COUNTERTOPS AND FIXTURES
- Cabinets: the closets, the master closet, the linen room and the kitchenette cabinet are full-height cabinets in a matte warm sand tone #CBB89E, smooth lacquer, flat, with no low-furniture shadow and no diagonal drawn on them.
- Kitchenette counter: Bege Bahia marble with the round white basin.
- Bathroom counters: light polished quartz #ECE8E1 with a fine, subtle speckle.
- White sanitary ware with black or chrome fittings: the oval bathtub, the toilets and the basins exactly as drawn; the two ceiling rain showers of the master bathroom as flat square plates; the showers of the other bathrooms exactly where they are drawn.

WALLS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; no new walls.
- Glass: thin pale-grey glass line #D6D6D3 between thin black frame lines, exactly where the plan shows it — the windows and glass doors to the balconies and the shower screens.
- Doors: only the drawn doors, with their arcs and leaves; no new doors.
- The elevator and the shaft are closed boxes, not voids.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours; no text.

Avoid: zooming in, cropping, re-centring, enlarging, shrinking or rotating the plan, or changing the size of walls, rooms, furniture, planks or slabs; new rooms, walls, doors, furniture or objects; colour, texture, grass, vegetation or shadows outside the house and its balconies, or a floor in the white area below the family lounge; flat-colour floors, or floors changed in material or direction; orange wood; strong pink, orange or blotchy quartzite; blotchy Bege Bahia; any balcony material other than Bege Bahia; floor, garden or light colour in the voids; the elevator or shaft as a dark void; cabinets in the floor colour, with the diagonal drawn on them or with a low-furniture shadow; wall showers, shower arms or round heads in the master bathroom; extra showers; a valve, shower or fitting on a window; simplified or restyled furniture; shadows; perspective; text.
```

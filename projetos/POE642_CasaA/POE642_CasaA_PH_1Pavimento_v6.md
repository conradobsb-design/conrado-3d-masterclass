# POE 642 · Casa A · 1º Pavimento — prompt v6 (só a imagem base)
_14/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaA_BASE_1Pavimento_v2_16x9.png`. A base foi gerada do PDF do cliente (`642-_1__PAVIMENTO_CASA_A_1.pdf`), na mesma prancha do Térreo e do Subsolo, e não tem imagem de referência.

**Da v5 para a v6:**
- **Bege Bahia:** no render da v5, as varandas e o bloco de serviço saíram muito manchados. O texto agora pede uma pedra creme-bege clara e uniforme, quase lisa, só com um pontilhado fino e leve, sem nuvens nem manchas.
- **Escada caracol:** no render da v5, a pintura saiu invertida. O motor coloriu os 3/4 do piso de baixo e deixou branco o quarto que chega a este piso.
  - **Prompt:** agora diz que só um quarto tem cor, o de cima à direita, entre 12h e 3h. Os outros três quartos, a metade esquerda inteira e o quarto de baixo à direita, ficam brancos. A área branca em volta do círculo, que no PDF é a abertura da escada, também fica branca.
  - **Base v2:** os 3/4 do piso de baixo clareiam 80%, em vez de 55%, para lerem como branco. O resto da base é igual à v1.
- **Chuveiros:** cada banho tem agora o chuveiro descrito com o tipo, de teto ou de parede, e com a parede certa, conforme o PDF e as suas indicações.
  - **Banho 3, da suíte de cima:** um chuveiro de teto, no centro da área de banho.
  - **Banho 2, da suíte do meio:** um chuveiro de parede, com o braço saindo da parede de cima.
  - **Banho 1, da suíte de baixo à direita:** um chuveiro de parede na **parede de cima**, abaixo da janelinha alta. No render da v5, ele foi parar na parede direita, que é uma janela de vidro.
  - **Banho master, embaixo à esquerda:** dois chuveiros de teto, lado a lado. No render da v5, eles saíram como chuveiros de parede, com braço.
  - **Banho de serviço:** um chuveiro de parede pequeno, na parede direita. A marca na parede esquerda é uma janelinha, e no render da v5 ela virou um segundo chuveiro.

**Mantidos da v5:**
- **Pisos:**
  - travertino: circulação, sala íntima, os quatro banhos e a escada em U;
  - madeira Durafloor City Petra #A8784F, nunca laranja: suítes e closets;
  - Bege Bahia: as quatro varandas e o bloco de serviço.
- **Vazios:** cinza-escuro #4A4A4A, com o X tracejado claro.
- **Elevador e shaft:** fechados.
- **Quarto de serviço:** com a cama.
- **Armários:** areia.
- **Entorno do Térreo:** esmaecido.
- **Fundo:** branco.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta do 1º pavimento a editar. Ela define a geometria e o layout, e deve ser seguida exatamente.

Transforme a planta numa planta humanizada de apresentação do **1º pavimento**, rica e fotorrealista, para uma residência de alto padrão. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala;
- cada parede, vidro, porta, escada, linha, móvel, armário e louça exatamente onde está, com o mesmo tamanho e a mesma forma;
- nada é acrescentado: nenhum ambiente, parede, porta, escada ou objeto novo.

Muda o acabamento: pisos, móveis e marcenaria ficam reais e sofisticados, numa paleta quente e calma, com o mesmo acabamento do Térreo.

**FUNDO:** todo o fundo é branco puro e chapado #FFFFFF, sem textura, sem tom e sem cor de terreno.

**OS AMBIENTES, ONDE FICA CADA UM** (a piscina esmaecida fica à esquerda)

**Faixa de cima, da esquerda para a direita:**
1. **Varanda da suíte 3:** faixa estreita.
2. **Suíte 3:** cama de casal, duas mesas laterais redondas e uma bancada.
3. **Closet 3.**
4. **Banho 3:** bancada, bacia e área de banho com chuveiro de teto.

Depois do banho 3 há uma caixinha com paredes, que fica como desenhada.

**No meio:**
- **Vazios de pé-direito duplo:** dois, lado a lado, com guarda-corpo de vidro entre eles.
- **Circulação:** desce pela direita dos vazios, a partir do banho 3. Tem uma rouparia areia ao longo da parede de cima e guarda-corpo de vidro do lado dos vazios.
- **Sala íntima:** abaixo da circulação, com sofá em L, poltrona, planta e um painel areia na parede esquerda.
- **Hall da escada:** à direita da sala íntima.
  - A escada em U é de travertino: dois lances paralelos com patamar à direita, subindo da direita para a esquerda.
  - Em volta da escada e no vão entre os lances há vazios cinza-escuros, abertos para o jardim do Térreo.
  - Do lado direito do hall há uma janela de vidro.

**Faixa da suíte 2, da esquerda para a direita:**
1. **Varanda da suíte 2:** faixa estreita.
2. **Banho 2:** em cima.
3. **Closet 2:** à direita, com armários areia.
4. **Suíte 2:** embaixo, com cama de casal e mesa redonda.

**Abaixo do hall da escada:**
- **Elevador e shaft:** caixas fechadas com X tracejado, que não são vazios.
- **Banho 1:** à direita deles.

**Faixa de baixo, da esquerda para a direita:**
1. **Varanda da suíte master:** faixa na lateral esquerda.
2. **Suíte master:** cama de casal e poltronas.
3. **Banho master:** abaixo da suíte master.
   - banheira de imersão solta, bancada dupla, bacia e área de banho com dois chuveiros de teto;
   - jardineira com plantas na lateral esquerda.
4. **Closet master:** à direita, com armários areia em L.
5. **Bloco de serviço:**
   - quarto de serviço com a cama de solteiro;
   - saleta com a escada caracol, embaixo;
   - banho de serviço, à direita.
6. **Suíte 1:** cama, bancada e o closet 1 em cima à esquerda.
7. **Varanda da suíte 1:** larga, à direita.

**AS ESCADAS**
- **Escada em U:** em travertino, com a cor cheia, exatamente como desenhada, com a borda de cada degrau visível.
- **Escada caracol, na saleta abaixo do quarto de serviço:** só **um quarto** do círculo tem cor.
  - **O quarto com cor:** o de cima à direita, entre 12h e 3h, pintado em **creme #D8CDB4** com as linhas dos degraus escuras. É o trecho que chega a este piso e sai com degraus de Bege Bahia, com a cor cheia e a borda de cada degrau visível.
  - **Os outros três quartos:** a metade esquerda inteira e o quarto de baixo à direita, de 3h até 12h no sentido horário. São do piso de baixo e ficam **brancos**, como na planta, só com as linhas cinza-claras dos degraus, sem cor, pedra ou textura.
  - **A área branca em volta do círculo, dentro da saleta:** é a abertura da escada e também fica branca.

**VAZIOS:** os dois quadrados grandes e as faixas em volta da escada em U são vazios de pé-direito duplo.
- Ficam em **cinza-escuro chapado #4A4A4A**, como um vão escuro, não como piso.
- Os dois quadrados grandes mantêm o X tracejado claro.
- Os guarda-corpos de vidro ficam nítidos.

**COR CHEIA E ENTORNO ESMAECIDO**
- **Cor cheia:** todo o 1º pavimento, dentro das paredes pretas, mais as varandas, os vazios e o hall da escada.
- **Esmaecido:** o entorno do Térreo, que na planta já aparece claro. São a piscina e o ofurô, o deck de madeira, os degraus escalonados, o deck da piscina, a grade tracejada do pergolado, as placas de pedestres à direita e os contornos tracejados.
  - Fica exatamente como desenhado, como fantasma claro, dessaturado e de baixo contraste, mais ou menos 50% mais claro.
  - Leva só uma leve sugestão do material, sem textura forte, sem vegetação e sem sombra.
  - Fica sobre o fundo branco.

**PISOS — cada ambiente tem um único piso, exatamente dentro das suas paredes**

Todo piso se lê como material real fotografado de cima, com juntas reais. Nenhum piso fica em cor chapada.
- **Travertino Romano levigado, acetinado** (bege-acinzentado #DCD9CA na planta): circulação, sala íntima, banho master, banho 1, banho 2, banho 3 e a escada em U.
  - marfim-bege quente com **veios paralelos na mesma direção** (faixas mel e taupe claro) e poros pequenos;
  - placas de ~60 × 120 cm, juntas de 2 mm.
- **Madeira Durafloor City Petra** (marrom #A8784F com linhas de régua na planta): suíte master, suítes 1, 2 e 3, e os closets.
  - madeira natural marrom médio quente, **nunca laranja**;
  - réguas de ~20 cm na direção das linhas desenhadas;
  - veio aparente, emendas desencontradas, fosco-acetinado.
- **Mármore Bege Bahia fosco** (cinza-claro #E8E8E8 na planta): as quatro varandas, o quarto de serviço, a saleta e o banho de serviço.
  - creme-bege claro e **uniforme**, quase liso e bem calmo;
  - só um pontilhado fino, leve e de baixo contraste, e uma variação de tom quase imperceptível de uma placa para outra;
  - **sem nuvens, manchas, borrões, pontos escuros nem veios**;
  - placas quadradas de ~60 × 60 cm, juntas finas de 3 mm.
- **O quarto da escada caracol** (creme #D8CDB4 na planta): degraus do mesmo Bege Bahia uniforme.

**MÓVEIS, MARCENARIA E BANHOS**
- **Móveis:** ficam exatamente como desenhados, com o mesmo desenho refinado, posição, tamanho e orientação.
  - estofados e roupa de cama creme e off-white, em linho e bouclé;
  - mesas e criados em carvalho claro, detalhes em metal preto;
  - o quarto de serviço mantém a sua cama de solteiro.
- **Marcenaria:** armários dos closets, rouparia da circulação e painel da sala íntima. Na planta são as áreas areia #CBB89E com uma diagonal.
  - laca fosca tom areia #CBB89E, lisa;
  - a diagonal é só a convenção do desenho e não aparece como risco.
- **Bancadas dos banhos:** quartzo claro polido #ECE8E1, com cubas brancas, louças brancas e metais em preto ou cromado. Banheira solta branca no banho master.
- **Jardineira do banho master:** cheia de folhagens tropicais baixas, dentro do contorno.
- **Cortinas:** as linhas onduladas ao longo das janelas das suítes são cortinas leves de linho off-white, finas e rentes ao vidro.

**CHUVEIROS — cada um exatamente onde a planta desenha**

Visto de cima, o chuveiro de teto é uma placa quadrada rente ao teto, sem braço. O chuveiro de parede é um braço curto que sai da parede, com a ducha na ponta.
- **Banho 3 (suíte 3, faixa de cima):** a área de banho é a parte direita do banho, atrás do box de vidro.
  - um chuveiro **de teto** quadrado, no centro da área de banho, longe das paredes;
  - o misturador fica na parede direita, abaixo da janela.
- **Banho 2 (suíte 2, no meio à esquerda):** a área de banho é a parte esquerda do banho, atrás do box de vidro.
  - um chuveiro **de parede**: o braço sai da **parede de cima**, com a ducha quadrada na ponta, no meio da área de banho;
  - o misturador fica na parede esquerda, embaixo.
- **Banho 1 (suíte 1, à direita do elevador e do shaft):** a área de banho é a parte de cima do banho, acima do box de vidro.
  - um chuveiro **de parede** na **parede de cima**: o braço desce da parede de cima, abaixo da janelinha alta, no meio dela, com a ducha quadrada na ponta;
  - o misturador fica na parede de cima, perto do canto direito;
  - a parede direita é uma janela de vidro: sem chuveiro e sem metal nela.
- **Banho master (embaixo à esquerda):** a área de banho é a parte de baixo à esquerda do banho, abaixo do box de vidro.
  - **dois** chuveiros **de teto** quadrados, lado a lado, rentes ao teto e sem braço;
  - os dois misturadores ficam na parede de baixo, um abaixo de cada chuveiro.
- **Banho de serviço:** a área de banho é a parte de cima do banho, acima do box de vidro.
  - um chuveiro **de parede** pequeno e redondo na **parede direita**, com braço curto;
  - a marca na parede esquerda é uma janelinha, não um chuveiro.

Não há nenhum outro chuveiro.

**PAREDES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas e a espessura desenhada. Nenhuma parede nova.
- **Vidros:** linha fina de vidro cinza-claro #D6D6D3 entre dois caixilhos pretos, exatamente onde a planta mostra:
  - as janelas e portas de vidro das suítes para as varandas;
  - os guarda-corpos dos vazios;
  - a janela do hall da escada;
  - os boxes.
- **Portas e elevador:** as portas são as desenhadas, com arco e folha, e não entra porta nova. Elevador e shaft são caixas fechadas com X tracejado.
- **Ficam como desenhados:** a caixinha depois do banho 3 e o elemento comprido e fino à direita do hall da escada.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara, uniforme, com cor de luz do dia natural e sem sombra projetada. Cores vivas e naturais no 1º pavimento, sem texto.

**Evitar:**
- **No fundo:** qualquer tom, textura, cor de terreno ou linha.
- **Ambientes:** ambientes, paredes, portas ou objetos novos.
- **Vazios:**
  - vazios com piso, jardim ou cor clara;
  - elevador ou shaft como vazio escuro.
- **Escada caracol:**
  - cor nos três quartos do piso de baixo ou na área branca em volta;
  - o quarto de cima à direita branco ou sem cor.
- **Escada em U:** fora do travertino.
- **Pisos:**
  - madeira laranja;
  - Bege Bahia manchado, nublado ou com pontos escuros;
  - varandas ou bloco de serviço em travertino;
  - Bege Bahia nos banhos.
- **Marcenaria:** armários na cor do piso, ou diagonal riscada nos armários.
- **Quarto de serviço:** sem a cama.
- **Chuveiros:**
  - chuveiro de teto nos banhos 1, 2 e de serviço;
  - chuveiro de parede ou braço de chuveiro no banho master ou no banho 3;
  - chuveiro na parede direita do banho 1;
  - chuveiro em cima de janela;
  - chuveiros a mais.
- **Entorno esmaecido:** cor cheia, textura forte ou vegetação.
- **Geral:** sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the first-floor plan to edit. It defines the geometry and layout, and you follow it exactly.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) of the first floor of a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, and every wall, glass line, door, stair, line, piece of furniture, cabinet and sanitary fixture exactly where it is, at the same size and shape. Nothing is added: no new room, wall, door, stair or object. What changes is the finish: floors, furniture and joinery become real and high-end, in a warm, calm palette that matches the ground-floor plan.

BACKGROUND
The whole background is pure flat white #FFFFFF, with no texture, tint or ground colour.

THE ROOMS AND WHERE THEY ARE (the faded pool is on the left)
- Top band, left to right: the narrow balcony of suite 3; suite 3 (double bed, two round side tables, a desk); closet 3; bathroom 3 (vanity, toilet, shower area with a ceiling rain shower). Beyond bathroom 3, a small walled box stays as drawn.
- Middle: the two double-height voids side by side, with a glass guardrail between them; the circulation corridor runs down on the right of the voids from bathroom 3, with a sand linen cabinet along its top wall and a glass guardrail on the void side, and opens into the family lounge below it (L-shaped sofa, armchair, plant, a sand panel on its left wall). To the right of the lounge is the stair hall: the travertine U-shaped stair — two parallel flights with the landing on the right, rising from right to left — with dark grey voids around it and in the gap between the flights, open to the ground-floor garden below, and a glass window on the right side of the hall.
- Suite 2 band, left to right: the narrow balcony of suite 2; bathroom 2 at the top; closet 2 on the right with sand wardrobes; suite 2 below (double bed, round table).
- Below the stair hall: the elevator and the shaft — closed boxes with dashed X's, not voids — and bathroom 1 to their right.
- Bottom band, left to right: the balcony of the master suite along the left side; the master suite (double bed, armchairs); the master bathroom below it (freestanding bathtub, double vanity, toilet, a shower area with two ceiling rain showers, and a planter with plants along its left side); the master closet on the right with L-shaped sand wardrobes; the service block — the service bedroom with its single bed, the small hall below it with the spiral stair, and the service bathroom on the right; suite 1 (bed, desk, with closet 1 at its top-left); and the wide balcony of suite 1 on the right.

THE STAIRS
- U-shaped stair: travertine, in full colour, exactly as drawn, with every step edge visible.
- Spiral stair in the small service hall below the service bedroom: only ONE quarter of the circle is coloured. The coloured quarter is the top-right one, between 12 o'clock and 3 o'clock, drawn in solid cream #D8CDB4 with dark step lines: it is the part that reaches this floor — render it as Bege Bahia steps in full colour, with every step edge visible. The other three quarters — the whole left half and the bottom-right quarter, from 3 o'clock clockwise round to 12 o'clock — belong to the floor below: they stay white, exactly as in the plan, with only their faint light-grey step lines, and no colour, stone or texture. The white area around the circle inside the small hall is the stair opening and also stays white.

VOIDS
The two large squares and the strips around the U-shaped stair are double-height voids. Render them as flat dark charcoal #4A4A4A — a dark opening, not a floor — with the light dashed X kept in the two large squares, and the glass guardrails crisp.

FULL COLOUR AND FADED CONTEXT
Rendered in full colour: the whole first floor inside the black walls, with its balconies, voids and stair hall. Everything else — the ground floor around it, already drawn pale in the plan: the pool and the ofurô, the wooden deck, the staggered steps, the pool deck paving, the dashed pergola grid, the stepping slabs on the right and the dashed outlines — is a faded context: exactly as drawn, a light, desaturated, low-contrast ghost about 50% lighter, with only a faint hint of its materials, no strong texture, no vegetation and no shadows, on the white background.

FLOORS — each room has exactly one floor, exactly inside its walls
Every floor reads as a real material photographed from above, with real joints. No floor stays a flat colour.
- Honed Travertino Romano, satin (greige #DCD9CA in the plan): the circulation, the family lounge, the master bathroom, bathrooms 1, 2 and 3, and the U-shaped stair. Warm ivory-beige with parallel veining all running in one direction (honey and light-taupe bands) and small natural pores; slabs about 60 × 120 cm, 2 mm joints.
- Durafloor City Petra wood (brown #A8784F with plank lines in the plan): the master suite, suites 1, 2 and 3 and all closets. A warm, medium-brown natural wood, never orange; planks about 20 cm wide along the drawn lines, visible grain, staggered joints, matte-satin finish.
- Matte Bege Bahia marble (light grey #E8E8E8 in the plan): the four balconies, the service bedroom, the small service hall and the service bathroom. A light, uniform cream-beige stone, almost plain and very calm: only a fine, faint, low-contrast speckle and a barely visible change of tone from slab to slab; no clouds, patches, stains, blotches, dark spots or veins. Square slabs about 60 × 60 cm with thin 3 mm joints.
- The coloured quarter of the spiral stair (cream #D8CDB4 in the plan): steps in the same uniform Bege Bahia.

FURNITURE, JOINERY AND BATHROOMS
- Furniture: kept exactly as drawn — the same refined drawings, position, size and orientation — with cream and off-white linen and bouclé upholstery and bedding, light natural oak tables and bedside tables, and black metal details. The service bedroom keeps its single bed.
- Joinery: the closet wardrobes, the linen cabinet in the circulation and the panel in the family lounge (the sand #CBB89E areas with a single diagonal line in the plan) are matte sand lacquer #CBB89E, smooth; the diagonal is only a drawing convention and is not drawn on them.
- Bathrooms: vanity countertops in light polished quartz #ECE8E1 with white basins, white sanitary ware and black or chrome fittings; a white freestanding bathtub in the master bathroom.
- The planter in the master bathroom is full of low tropical foliage, inside its outline.
- The wavy lines along the bedroom windows are curtains: light off-white linen curtains, thin and close to the glass.

SHOWERS — each one exactly where the plan draws it
Seen from above, a ceiling shower is a flat square plate flush with the ceiling, with no arm; a wall shower is a short arm coming out of a wall with the shower head at its end.
- Bathroom 3 (suite 3, top band): the shower area is the right part of the bathroom, behind the glass screen. One square CEILING rain shower at the centre of the shower area, away from the walls; its mixer on the right wall, below the window.
- Bathroom 2 (suite 2, middle left): the shower area is the left part of the bathroom, behind the glass screen. One WALL shower: its arm comes out of the TOP wall, with the square head at its end, in the middle of the shower area; its mixer on the left wall, low down.
- Bathroom 1 (suite 1, to the right of the elevator and shaft): the shower area is the top part of the bathroom, above the glass screen. One WALL shower on the TOP wall: its arm comes down from the middle of the top wall, under the small high window, with the square head at its end; its mixer on the top wall, near the top-right corner. The right wall of this shower is a glass window, with no shower or fitting on it.
- Master bathroom (bottom left): the shower area is the bottom-left part of the bathroom, below the glass screen. TWO square CEILING rain showers side by side, flush with the ceiling and with no arms; their two mixers on the bottom wall, one below each.
- Service bathroom: the shower area is the top part of the bathroom, above the glass screen. One small round WALL shower on the RIGHT wall, on a short arm. The mark on its left wall is a small window, not a shower.
There are no other showers.

WALLS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; no new walls.
- Glass: thin pale-grey glass line #D6D6D3 between two thin black aluminium frame lines, exactly where the plan shows it — the bedroom windows and glass doors to the balconies, the void guardrails, the stair-hall window and the shower screens.
- Doors: only the drawn doors, with their arcs and leaves. The elevator and shaft stay closed boxes with dashed X's. The small walled box beyond bathroom 3 and the long thin element to the right of the stair hall stay as drawn.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours on the first floor; no text.

Avoid: any tint, texture, ground colour or lines in the background; new rooms, walls, doors or objects; floor, garden or light colour in the voids; the elevator or shaft as a dark void; colour on the three lower-floor quarters of the spiral stair or on the white area around it; a white or uncoloured top-right quarter of the spiral stair; the U-shaped stair in any material other than travertine; orange wood; blotchy, stained or cloudy Bege Bahia with dark spots; travertine on the balconies or the service block; Bege Bahia in the bathrooms; cabinets in the floor colour or with the diagonal drawn on them; a missing bed in the service bedroom; ceiling showers in bathroom 1, bathroom 2 or the service bathroom; wall showers or shower arms in the master bathroom or bathroom 3; a shower on the right wall of bathroom 1; a shower on a window; extra showers; full colour, strong texture or vegetation on the faded context; shadows; perspective; text.
```

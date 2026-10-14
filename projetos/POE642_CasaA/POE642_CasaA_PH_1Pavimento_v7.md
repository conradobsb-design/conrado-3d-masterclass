# POE 642 · Casa A · 1º Pavimento — prompt v7 (só a imagem base)
_14/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaA_BASE_1Pavimento_v3_16x9.png`. A base foi gerada do PDF do cliente (`642-_1__PAVIMENTO_CASA_A_1.pdf`), na mesma prancha do Térreo e do Subsolo, e não tem imagem de referência.

**Da v6 para a v7:** o render da v6 chegou perto, mas errou a escada caracol, os chuveiros, as varandas e o piso da saleta e do quarto de serviço. Desta vez, a maior parte da correção vai na base (v3), e o prompt acompanha.
- **Saleta e quarto de serviço:** no render da v6, os dois ficaram brancos, sem piso, e a cama de solteiro sumiu.
  - **Causa:** a v6 mandava a "área branca em volta do círculo" ficar branca, e o motor estendeu isso ao bloco inteiro.
  - **Base v3:** a área branca da saleta em volta da caracol virou piso, no mesmo cinza-claro do Bege Bahia. Agora só o círculo fica branco.
  - **Prompt:** o quarto de serviço, a saleta e o banho de serviço têm piso de Bege Bahia, e o quarto mantém a cama.
- **Escada caracol:** no render da v6, o motor coloriu o quarto de cima à **esquerda**, e não o de cima à direita.
  - **Base v3:** o quarto creme continua em cima à direita. Como agora tem piso em volta e o resto do círculo é branco, ele se destaca mais.
  - **Prompt:** manda colorir só a cunha creme já desenhada e diz exatamente onde ela fica. É o quarto entre a linha que sobe do centro e a linha que vai do centro para a direita.
- **Chuveiros:** nas janelinhas dos banhos, a linha de eixo que atravessa a parede saía como barra de vidro e formava um "+". O motor desenhava ali um registro ou um chuveiro de parede. Foi assim que o banho 3 ganhou chuveiro na parede direita e o banho de serviço ganhou um segundo chuveiro.
  - **Base v3:** os 10 "+" saíram. As janelinhas ficaram como janelas simples.
  - **Base v3:** os três chuveiros de teto viraram placas quadradas cinza-aço de 30 cm, com borda escura, no mesmo centro do símbolo do PDF: um no banho 3 e dois no banho master. Antes eram quadradinhos brancos de 20 cm, que o motor desenhava redondos e com braço.
  - **Prompt:** as placas cinza são chuveiros de teto, e nenhuma janela leva metal.
- **Varandas:** na varanda da suíte 1, as duas linhas tracejadas do Térreo dividiam a varanda. No render da v6, só uma faixa estreita virou pedra e o resto ficou cinza. A faixa ainda subiu ao lado do hall da escada, onde não há varanda.
  - **Base v3:** as linhas tracejadas saíram de dentro da varanda.
  - **Prompt:** as quatro varandas são de Bege Bahia, de borda a borda, e acima da varanda da suíte 1 não há varanda.

**Mantidos da v6:**
- **Pisos:**
  - travertino: circulação, sala íntima, os quatro banhos e a escada em U;
  - madeira Durafloor City Petra #A8784F, nunca laranja: suítes e closets;
  - Bege Bahia uniforme: as quatro varandas e o bloco de serviço.
- **Vazios:** cinza-escuro #4A4A4A, com o X tracejado claro.
- **Elevador e shaft:** fechados.
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
- **Escada caracol, na saleta abaixo do quarto de serviço:** um círculo, e só a **cunha creme #D8CDB4 já desenhada na planta** ganha cor. Nada mais, nada menos, nada em outro lugar.
  - **Onde fica a cunha:** é o quarto de cima à direita, entre a linha que sobe do centro do círculo e a linha que vai do centro para a direita, entre 12h e 3h.
  - **Como sai:** é o trecho que chega a este piso. Sai com degraus de Bege Bahia, com a cor cheia e a borda de cada degrau visível.
  - **Os outros três quartos:** a metade esquerda inteira, incluindo o quarto de cima à esquerda, e o quarto de baixo à direita. São do piso de baixo e ficam como **um disco branco**, só com as linhas cinza-claras dos degraus, sem cor, pedra ou textura.
  - **Em volta do círculo:** o piso da saleta é de Bege Bahia.

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

Todo piso se lê como material real fotografado de cima, com juntas reais. Nenhum piso fica em cor chapada, branco ou cinza.
- **Travertino Romano levigado, acetinado** (bege-acinzentado #DCD9CA na planta): circulação, sala íntima, banho master, banho 1, banho 2, banho 3 e a escada em U.
  - marfim-bege quente com **veios paralelos na mesma direção** (faixas mel e taupe claro) e poros pequenos;
  - placas de ~60 × 120 cm, juntas de 2 mm.
- **Madeira Durafloor City Petra** (marrom #A8784F com linhas de régua na planta): suíte master, suítes 1, 2 e 3, e os closets.
  - madeira natural marrom médio quente, **nunca laranja**;
  - réguas de ~20 cm na direção das linhas desenhadas;
  - veio aparente, emendas desencontradas, fosco-acetinado.
- **Mármore Bege Bahia fosco** (cinza-claro #E8E8E8 na planta): todas as áreas cinza-claras viram esta pedra.
  - creme-bege claro e **uniforme**, quase liso e bem calmo;
  - só um pontilhado fino, leve e de baixo contraste, e uma variação de tom quase imperceptível de uma placa para outra;
  - **sem nuvens, manchas, borrões, pontos escuros nem veios**;
  - placas quadradas de ~60 × 60 cm, juntas finas de 3 mm.
- **O quarto da escada caracol** (creme #D8CDB4 na planta): degraus do mesmo Bege Bahia uniforme.

**VARANDAS E BLOCO DE SERVIÇO — inteiros em Bege Bahia**
- **As quatro varandas:** pavimentadas por inteiro em Bege Bahia, de borda a borda, dentro do contorno. Nenhum pedaço fica cinza ou branco.
  - a varanda estreita da suíte 3;
  - a varanda estreita da suíte 2;
  - a varanda da suíte master, na lateral esquerda;
  - a varanda larga da suíte 1, que é o retângulo cinza-claro inteiro à direita da suíte 1 e do banho 1, da borda de cima à borda de baixo.
- **Acima da varanda da suíte 1:** ao lado da janela do hall da escada não há varanda. As linhas tracejadas claras ali são do Térreo e ficam esmaecidas sobre o fundo branco.
- **Bloco de serviço:** o quarto de serviço, a saleta da caracol e o banho de serviço têm o mesmo piso de Bege Bahia, por inteiro.
  - Nenhuma parte fica branca ou cinza.
  - O banho de serviço não é de madeira nem de travertino.
  - O quarto de serviço mantém a sua cama de solteiro.

**MÓVEIS, MARCENARIA E BANHOS**
- **Móveis:** ficam exatamente como desenhados, com o mesmo desenho refinado, posição, tamanho e orientação.
  - estofados e roupa de cama creme e off-white, em linho e bouclé;
  - mesas e criados em carvalho claro, detalhes em metal preto.
- **Marcenaria:** armários dos closets, rouparia da circulação e painel da sala íntima. Na planta são as áreas areia #CBB89E com uma diagonal.
  - laca fosca tom areia #CBB89E, lisa;
  - a diagonal é só a convenção do desenho e não aparece como risco.
- **Bancadas dos banhos:** quartzo claro polido #ECE8E1, com cubas brancas, louças brancas e metais em preto ou cromado. Banheira solta branca no banho master.
- **Jardineira do banho master:** cheia de folhagens tropicais baixas, dentro do contorno.
- **Cortinas:** as linhas onduladas ao longo das janelas das suítes são cortinas leves de linho off-white, finas e rentes ao vidro.

**CHUVEIROS — cada um exatamente onde a planta desenha**
- **Chuveiros de teto:** as **placas quadradas cinza com borda escura** são chuveiros de teto. Há três: uma no banho 3 e duas no banho master.
  - viram placas quadradas de aço escovado, rentes ao teto e sem braço;
  - mantêm o tamanho e a posição desenhados.
- **Chuveiros de parede:** o braço curto sai da parede, com a ducha na ponta.
- **Janelinhas dos banhos:** as caixinhas estreitas nas paredes são janelas simples. Não levam registro, chuveiro nem metal.

Por banho:
- **Banho 3 (suíte 3, faixa de cima):** a área de banho é a parte direita do banho, atrás do box de vidro.
  - um chuveiro **de teto**, a placa cinza no centro da área de banho, longe das paredes;
  - o misturador pequeno fica embaixo, na parede direita;
  - a parede direita tem uma janela simples, sem chuveiro.
- **Banho 2 (suíte 2, no meio à esquerda):** a área de banho é a parte esquerda do banho, atrás do box de vidro.
  - um chuveiro **de parede**: o braço sai da **parede de cima**, com a ducha quadrada na ponta, no meio da área de banho;
  - o misturador fica na parede esquerda, embaixo.
- **Banho 1 (suíte 1, à direita do elevador e do shaft):** a área de banho é a parte de cima do banho, acima do box de vidro.
  - um chuveiro **de parede** na **parede de cima**: o braço desce do meio da parede de cima, abaixo da janelinha, com a ducha quadrada na ponta;
  - o misturador fica na parede de cima, perto do canto direito;
  - a parede direita é uma janela de vidro, sem chuveiro e sem metal.
- **Banho master (embaixo à esquerda):** a área de banho é a parte de baixo à esquerda do banho, abaixo do box de vidro.
  - **dois** chuveiros **de teto**, as duas placas cinza lado a lado, rentes ao teto e sem braço;
  - os dois misturadores pequenos ficam na parede de baixo, um abaixo de cada placa.
- **Banho de serviço:** a área de banho é a parte de cima do banho, acima do box de vidro.
  - um chuveiro **de parede** pequeno e redondo na **parede direita**, com braço curto;
  - a parede esquerda tem uma janelinha simples, sem chuveiro.

Não há nenhum outro chuveiro.

**PAREDES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas e a espessura desenhada. Nenhuma parede nova.
- **Vidros:** linha fina de vidro cinza-claro #D6D6D3 entre dois caixilhos pretos, exatamente onde a planta mostra:
  - as janelas e portas de vidro das suítes para as varandas;
  - os guarda-corpos dos vazios;
  - a janela do hall da escada;
  - as janelinhas dos banhos;
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
  - cor em qualquer lugar do círculo fora da cunha creme de cima à direita;
  - cor no quarto de cima à esquerda;
  - a cunha creme branca ou sem cor.
- **Escada em U:** fora do travertino.
- **Pisos:**
  - madeira laranja;
  - Bege Bahia manchado, nublado ou com pontos escuros;
  - varandas ou bloco de serviço em travertino ou madeira;
  - Bege Bahia nos banhos que não sejam o de serviço.
- **Bloco de serviço e saleta:** piso branco ou cinza; quarto de serviço sem a cama.
- **Varandas:**
  - varanda parcial, partida em faixas ou com partes cinza;
  - varanda acima da varanda da suíte 1, ao lado do hall da escada.
- **Marcenaria:** armários na cor do piso, ou diagonal riscada nos armários.
- **Chuveiros:**
  - chuveiro de teto nos banhos 1, 2 e de serviço;
  - chuveiro de parede, braço de chuveiro ou ducha redonda no banho master ou no banho 3;
  - chuveiro na parede direita do banho 1 ou do banho 3;
  - registro, chuveiro ou metal em cima de uma janela;
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
- Spiral stair in the small service hall below the service bedroom: a circle in which ONLY the cream #D8CDB4 wedge already drawn in the plan is coloured — nothing more, nothing less, nothing elsewhere. That wedge is the top-right quarter of the circle, between the line rising from the centre straight up and the line running from the centre straight to the right (between 12 and 3 o'clock). It is the part that reaches this floor: render it as Bege Bahia steps in full colour, with every step edge visible. The other three quarters — the whole left half, including the top-left quarter, and the bottom-right quarter — belong to the floor below: they stay a plain white disc with only faint light-grey step lines, with no colour, stone or texture. Around the circle, the hall floor is Bege Bahia.

VOIDS
The two large squares and the strips around the U-shaped stair are double-height voids. Render them as flat dark charcoal #4A4A4A — a dark opening, not a floor — with the light dashed X kept in the two large squares, and the glass guardrails crisp.

FULL COLOUR AND FADED CONTEXT
Rendered in full colour: the whole first floor inside the black walls, with its balconies, voids and stair hall. Everything else — the ground floor around it, already drawn pale in the plan: the pool and the ofurô, the wooden deck, the staggered steps, the pool deck paving, the dashed pergola grid, the stepping slabs on the right and the dashed outlines — is a faded context: exactly as drawn, a light, desaturated, low-contrast ghost about 50% lighter, with only a faint hint of its materials, no strong texture, no vegetation and no shadows, on the white background.

FLOORS — each room has exactly one floor, exactly inside its walls
Every floor reads as a real material photographed from above, with real joints. No floor stays a flat colour, white or grey.
- Honed Travertino Romano, satin (greige #DCD9CA in the plan): the circulation, the family lounge, the master bathroom, bathrooms 1, 2 and 3, and the U-shaped stair. Warm ivory-beige with parallel veining all running in one direction (honey and light-taupe bands) and small natural pores; slabs about 60 × 120 cm, 2 mm joints.
- Durafloor City Petra wood (brown #A8784F with plank lines in the plan): the master suite, suites 1, 2 and 3 and all closets. A warm, medium-brown natural wood, never orange; planks about 20 cm wide along the drawn lines, visible grain, staggered joints, matte-satin finish.
- Matte Bege Bahia marble: every light grey #E8E8E8 area in the plan. A light, uniform cream-beige stone, almost plain and very calm: only a fine, faint, low-contrast speckle and a barely visible change of tone from slab to slab; no clouds, patches, stains, blotches, dark spots or veins. Square slabs about 60 × 60 cm with thin 3 mm joints.
- The coloured wedge of the spiral stair (cream #D8CDB4 in the plan): steps in the same uniform Bege Bahia.

BALCONIES AND SERVICE BLOCK — fully Bege Bahia
- The four balconies are paved entirely in Bege Bahia, edge to edge inside their outlines, with no part left grey or white: the narrow balcony of suite 3, the narrow balcony of suite 2, the balcony of the master suite along the left side, and the wide balcony of suite 1 — the whole light grey rectangle to the right of suite 1 and bathroom 1, from its top edge to its bottom edge.
- Above the suite-1 balcony, beside the stair-hall window, there is no balcony: the faint dashed lines there belong to the ground floor and stay faded on the white background.
- The service bedroom, the small spiral-stair hall and the service bathroom all have the same Bege Bahia floor, completely: no part stays white or grey, and the service bathroom is not wood or travertine. The service bedroom keeps its single bed.

FURNITURE, JOINERY AND BATHROOMS
- Furniture: kept exactly as drawn — the same refined drawings, position, size and orientation — with cream and off-white linen and bouclé upholstery and bedding, light natural oak tables and bedside tables, and black metal details.
- Joinery: the closet wardrobes, the linen cabinet in the circulation and the panel in the family lounge (the sand #CBB89E areas with a single diagonal line in the plan) are matte sand lacquer #CBB89E, smooth; the diagonal is only a drawing convention and is not drawn on them.
- Bathrooms: vanity countertops in light polished quartz #ECE8E1 with white basins, white sanitary ware and black or chrome fittings; a white freestanding bathtub in the master bathroom.
- The planter in the master bathroom is full of low tropical foliage, inside its outline.
- The wavy lines along the bedroom windows are curtains: light off-white linen curtains, thin and close to the glass.

SHOWERS — each one exactly where the plan draws it
The grey square plates with a dark rim are ceiling rain showers — there are three: one in bathroom 3 and two in the master bathroom. Render them as square brushed-steel plates flush with the ceiling, with no arm, at the drawn size and position. A wall shower is a short arm coming out of a wall with the shower head at its end. The small narrow boxes in the bathroom walls are plain windows: no valve, shower or fitting on them.
- Bathroom 3 (suite 3, top band): the shower area is the right part of the bathroom, behind the glass screen. One CEILING rain shower — the grey plate at the centre of the shower area, away from the walls; its small mixer low on the right wall. The right wall has a plain window, with no shower.
- Bathroom 2 (suite 2, middle left): the shower area is the left part of the bathroom, behind the glass screen. One WALL shower: its arm comes out of the TOP wall, with the square head at its end, in the middle of the shower area; its mixer on the left wall, low down.
- Bathroom 1 (suite 1, to the right of the elevator and shaft): the shower area is the top part of the bathroom, above the glass screen. One WALL shower on the TOP wall: its arm comes down from the middle of the top wall, under the small window, with the square head at its end; its mixer on the top wall, near the top-right corner. The right wall of this shower is a glass window, with no shower or fitting on it.
- Master bathroom (bottom left): the shower area is the bottom-left part of the bathroom, below the glass screen. TWO CEILING rain showers — the two grey plates side by side, flush with the ceiling and with no arms; their two small mixers on the bottom wall, one below each.
- Service bathroom: the shower area is the top part of the bathroom, above the glass screen. One small round WALL shower on the RIGHT wall, on a short arm. The left wall has a small plain window, with no shower.
There are no other showers.

WALLS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; no new walls.
- Glass: thin pale-grey glass line #D6D6D3 between two thin black aluminium frame lines, exactly where the plan shows it — the bedroom windows and glass doors to the balconies, the void guardrails, the stair-hall window, the small bathroom windows and the shower screens.
- Doors: only the drawn doors, with their arcs and leaves. The elevator and shaft stay closed boxes with dashed X's. The small walled box beyond bathroom 3 and the long thin element to the right of the stair hall stay as drawn.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours on the first floor; no text.

Avoid: any tint, texture, ground colour or lines in the background; new rooms, walls, doors or objects; floor, garden or light colour in the voids; the elevator or shaft as a dark void; colour anywhere in the spiral-stair circle outside the cream top-right wedge; a coloured top-left quarter; a white or uncoloured cream wedge; the U-shaped stair in any material other than travertine; orange wood; blotchy, stained or cloudy Bege Bahia with dark spots; travertine or wood on the balconies or in the service block; a white or grey floor in the service bedroom, the spiral-stair hall or the service bathroom; a missing bed in the service bedroom; a partial balcony, a balcony split into strips or with grey parts; a balcony above the suite-1 balcony beside the stair hall; cabinets in the floor colour or with the diagonal drawn on them; ceiling showers in bathroom 1, bathroom 2 or the service bathroom; wall showers, shower arms or round heads in the master bathroom or bathroom 3; a shower on the right wall of bathroom 1 or bathroom 3; a valve, shower or fitting on a window; extra showers; full colour, strong texture or vegetation on the faded context; shadows; perspective; text.
```

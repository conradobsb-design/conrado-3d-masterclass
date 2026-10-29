# POE 642 · Casa A · Subsolo — prompt v6 (só a imagem base)
_14/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaA_BASE_Subsolo_v4_16x9.png`. A base foi gerada do PDF do cliente (`642-_SUBSOLO_CASA_A_1.pdf`) e não tem imagem de referência.

**Da v5 para a v6:** o render da v5 ficou fiel, mas teve três problemas.
- **A escada destacada era a errada.** O motor deu cor cheia aos degraus escalonados do Térreo, que descem do deck da piscina para o deck de madeira, e apagou a escada certa.
  - **Base v4:** a escada que desce para o pátio da academia sai num creme mais forte, #D8CDB4. Ela foi pintada pela geometria exata do PDF, com os degraus marcados.
  - **Prompt:** diz qual é essa escada, logo abaixo do ofurô e descendo para o pátio da academia, e que os degraus escalonados ficam esmaecidos como o deck.
- **O fundo saiu tingido.** O motor pintou de bege-acinzentado tudo o que ficava acima da linha do lote.
  - **Base v4:** sem as curvas de nível e sem a linha do lote (layer `ARQ_TERRENO PLANEJADO`).
  - **Prompt:** pede fundo inteiro branco puro #FFFFFF, sem tom, textura nem cor de terreno.
- **Banco da sauna:** agora em mármore travertino, não madeira.
- **Reforço:** no render, o depósito saiu dividido e a circulação ganhou uma porta em cima. O texto agora diz quantas aberturas cada um tem.
  - **Circulação:** duas aberturas, a porta para o depósito e a de vidro para o pátio.
  - **Depósito:** uma porta só, sem divisória.

**Versões anteriores:**
- **v4 para v5:** base v3 sem as projeções no depósito e na academia, mapa dos ambientes, escada única, 5 portas e pisos ambiente por ambiente.
- **v3 para v4:** piscina e ofurô esmaecidos.
- **v2 para v3:** prompt reescrito com a base nova e os materiais definidos.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta do subsolo a editar. Ela define a geometria e o layout, e deve ser seguida exatamente.

Transforme a planta numa planta humanizada de apresentação do **subsolo**, rica e fotorrealista, para uma residência de alto padrão. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala;
- cada parede, vidro, porta, escada, linha, equipamento e louça exatamente onde está, com o mesmo tamanho e a mesma forma;
- nada é acrescentado: nenhum ambiente, parede, divisória, porta, escada ou objeto novo.

Muda o acabamento: os pisos e os equipamentos ficam reais e sofisticados, numa paleta quente e calma.

**FUNDO:** todo o fundo é branco puro e chapado #FFFFFF, em volta da planta e dentro e fora da moldura tracejada. Não tem textura de papel nem tom cinza, bege ou creme, nem linhas ou cor de terreno.

**OS AMBIENTES, ONDE FICA CADA UM** (o alto da imagem é o lado da piscina)

**Fileira de cima, da esquerda para a direita:**
1. **Banho de serviço:** pequeno, com bacia, cuba e chuveiro. As pastilhas cinza-água ficam só dentro dele.
2. **Circulação:** sala pequena e quadrada, com exatamente duas aberturas:
   - a porta à direita, para o depósito;
   - a porta de correr de vidro embaixo, para o pátio.

   Não tem porta em cima. O piso é Bege Bahia.
3. **Depósito:** uma sala única, comprida e vazia, até a ponta direita da fileira.
   - Tem uma única porta, a que vem da circulação.
   - Sem parede, divisória, porta, banco, prateleira ou sauna dentro.

**No meio:**
- **Academia:** a sala grande e quadrada de piso de madeira.
  - À esquerda, uma parede inteira de vidro voltada para o pátio.
  - À direita, o vidro para o hall do elevador.
  - Sem porta própria e sem porta para o depósito.

**Ala da direita:**
- **Hall do elevador:** um retângulo comprido que sai da academia para a direita.
- No fim do hall ficam o elevador e os dois shafts, caixas com X tracejado.

**Fileira de baixo, da esquerda para a direita:**
1. **Sauna:** com frente de vidro em L e **um único banco reto de mármore travertino** ao longo da parede de baixo.
2. **Ducha:** a salinha ao lado da sauna, com a sua porta.
3. **Banho feminino.**
4. **Banho masculino.**

Cada banho tem a sua porta, bancada e bacia. Entre os dois fica a área de chuveiro, com boxes de vidro.

**À esquerda:**
- **Pátio de acesso à academia:** a faixa comprida entre a parede de vidro da academia e o muro simples da esquerda, da circulação até a sauna.

**A ESCADA EM DESTAQUE**
- **Qual é:** é a escada que **desce para a academia**. Na planta, é o lance reto pintado em **creme #D8CDB4**, logo abaixo do quadrado esmaecido do ofurô, no canto de cima à esquerda do pátio.
- **Como é:** são 11 degraus num lance único e horizontal. A escada desce do deck de madeira esmaecido, à esquerda, até o pátio da academia, à direita.
- **Como sai no render:** degraus de Bege Bahia com a cor cheia, nítidos, com a borda de cada degrau visível.
- **O que fica esmaecido:** os **degraus escalonados** no alto à esquerda da folha, ao lado da piscina, que sobem do deck de madeira para o deck da piscina. Eles são do Térreo e ficam como o deck de madeira: claros, sem destaque e sem travertino.
- **Não existe outra escada.**

**As portas:** existem só as 5 portas desenhadas com arco:
- banho de serviço;
- circulação para o depósito;
- ducha;
- banho feminino;
- banho masculino.

**COR CHEIA E ENTORNO ESMAECIDO**
- **Cor cheia:** os ambientes do subsolo dentro das paredes pretas, o pátio e a escada creme que desce para a academia.
- **Esmaecido:** todo o resto, que na planta já aparece claro. São a piscina e o ofurô, o deck de madeira do Térreo, os degraus escalonados, o deck da piscina e os contornos tracejados.
  - Fica exatamente como desenhado, como um fantasma claro, dessaturado e de baixo contraste, mais ou menos 50% mais claro.
  - Leva só uma leve sugestão do material (madeira clara, pedra creme clara, azul-água bem claro na piscina e no ofurô), sem textura forte, sem vegetação e sem sombra.
  - Fica sobre o fundo branco puro.

**PISOS — cada ambiente tem um único piso, exatamente dentro das suas paredes**

Todo piso se lê como material real fotografado de cima, com juntas reais e variação natural. Nenhum piso fica em cor chapada ou em quadrados lisos.
- **Travertino Romano levigado, acetinado** (bege-acinzentado #DCD9CA na planta): hall do elevador, sauna, ducha, banho feminino e banho masculino.
  - marfim-bege quente com **veios paralelos bem marcados, todos na mesma direção** (faixas mel e taupe claro), e poros pequenos;
  - placas de ~60 × 120 cm, juntas de 2 mm.
- **Travertino Romano fosco antiderrapante, externo** (mesmo #DCD9CA): o pátio.
  - o mesmo travertino em faixas, com poros, fosco;
  - placas de ~60 × 120 cm;
  - **não** é Bege Bahia nem pedra nublada.
- **Mármore Bege Bahia fosco:** a circulação e o depósito (cinza-claro #E8E8E8 na planta) e a escada (creme #D8CDB4 na planta).
  - creme-bege **uniforme**, com manchas suaves em nuvem e pontinhos de fósseis, **sem veios lineares**;
  - placas quadradas de ~60 × 60 cm, juntas de 3 mm.
- **Revestimento Barlavento** (cinza-esverdeado #B7CFC9 na planta): só o banho de serviço.
  - pastilhas ou placas pequenas cinza-água claras, foscas;
  - piso seco, não água.
- **Madeira natural** (marrom com linhas de régua na planta): só a academia.
  - réguas de ~20 cm na direção das linhas desenhadas;
  - veio aparente, emendas desencontradas, fosco-acetinado.

**ACADEMIA, SAUNA E BANHOS**
- **Academia:** só os equipamentos desenhados, na mesma posição, tamanho e orientação, em preto, grafite e metal escovado:
  - duas esteiras;
  - duas bicicletas ergométricas;
  - um banco de supino com barra.

  Nada mais: sem plantas, suportes, halteres, espelhos, TV ou bancos.
- **Sauna:** um único banco reto de **mármore Travertino Romano**, em bloco liso e claro, ao longo da parede de baixo. O piso também é de travertino, e não há madeira na sauna.
- **Banhos:** bancadas em quartzo claro polido #ECE8E1 com cubas brancas, louças brancas e metais em preto ou cromado, exatamente onde estão.

**PAREDES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas e a espessura desenhada. Nenhuma parede nova.
- **Vidros:** linha fina de vidro cinza-claro #D6D6D3 entre dois caixilhos pretos, exatamente onde a planta mostra:
  - a parede de vidro da academia para o pátio;
  - o vidro entre a academia e o hall;
  - a porta de correr da circulação;
  - a frente em L da sauna;
  - os boxes.
- **Portas e elevador:** só as 5 portas desenhadas. O elevador e os shafts são caixas com X tracejado.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara e uniforme, com cor de luz do dia natural e sem sombra projetada de nenhum tipo. Cores vivas e naturais no subsolo, sem texto.

**Evitar:**
- **No fundo:** qualquer tom, textura, cor de terreno ou linha.
- **Escadas:**
  - destaque, cor ou travertino nos degraus escalonados ao lado da piscina;
  - a escada que desce para a academia esmaecida ou sumindo;
  - uma segunda escada.
- **Ambientes e portas:**
  - ambientes, paredes, divisórias ou portas novos;
  - divisória no depósito;
  - porta em cima da circulação;
  - porta entre a academia e o depósito.
- **Objetos:**
  - pastilhas fora do banho de serviço;
  - banco de madeira na sauna;
  - plantas ou equipamentos extras na academia.
- **Pisos:**
  - pátio em Bege Bahia;
  - circulação ou depósito em travertino.
- **Entorno esmaecido:**
  - cor cheia, textura forte ou vegetação;
  - piscina ou ofurô com água realista.
- **Geral:** sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the basement floor plan to edit. It defines the geometry and layout, and you follow it exactly.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) of the basement of a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, and every wall, glass line, door, stair, line, piece of equipment and sanitary fixture exactly where it is, at the same size and shape. Nothing is added: no new room, wall, partition, door, stair or object. What changes is the finish: floors and equipment become real and high-end, in a warm, calm palette.

BACKGROUND
The whole background is pure flat white #FFFFFF — all around the plan, inside and outside the thin dashed sheet frame — with no paper texture, no grey, beige or cream tint, no terrain lines and no ground colour.

THE ROOMS AND WHERE THEY ARE (top of the image = pool side)
- Top row, left to right: (1) the small service bathroom with toilet, basin and shower — the aqua tiles stay only inside it; (2) the circulation, a small square room with exactly two openings: the door on its right into the storage room and the sliding glass door on its bottom side to the patio — no door on its top side; its floor is Bege Bahia; (3) the storage room — one single, long, empty room running to the right end of the row, with exactly one door (from the circulation) and no wall, partition, door, bench, shelf or sauna inside it.
- Middle: the gym, the large square wood-floored room. Its left side is a full-height glass wall facing the patio; its right side has a glass panel to the elevator hall. It has no doors of its own and no door to the storage room.
- Right wing: the elevator hall, a long rectangle running right from the gym, ending at the elevator and two shafts (boxes with dashed X's).
- Bottom row, left to right: (1) the sauna, with an L-shaped glass front and one single straight bench in Travertino Romano marble along its bottom wall; (2) the small shower room beside it, with its door; (3) the female bathroom; (4) the male bathroom — each bathroom with its door, vanity and toilet, with the shower area and its glass screens between them.
- Left: the patio that gives access to the gym — the long strip between the gym's glass wall and the plain wall on the far left, from the circulation down to the sauna.
- Doors: only the five drawn door arcs — service bathroom, circulation to storage room, shower room, female bathroom, male bathroom.

THE STAIR IN FULL COLOUR
The highlighted stair is the one that goes down to the gym: the straight flight of 11 steps drawn in solid cream #D8CDB4, directly below the faded ofurô square, at the top-left corner of the patio. It is one straight horizontal run that descends from the faded wooden deck on its left down to the patio of the gym on its right. Render it as Bege Bahia steps in full colour, crisp, with every step edge visible. The staggered steps at the top-left of the sheet, beside the pool, climbing from the wooden deck to the pool deck, belong to the ground floor: they stay faded exactly like the wooden deck — pale, not highlighted and not travertine. There is no other stair.

FULL COLOUR AND FADED CONTEXT
Rendered in full colour: the basement rooms inside the black walls, the patio and the cream stair down to the gym. Everything else — already drawn pale in the plan — is a faded context: the pool and the ofurô (hot tub), the ground-floor wooden deck, the staggered steps, the pool deck paving and the dashed outlines. Keep it exactly as drawn, as a light, desaturated, low-contrast ghost about 50% lighter than the basement, with only a faint hint of its materials (pale wood, pale cream stone, a very light aqua tint in the pool and the ofurô), no strong texture, no vegetation and no shadows, on the pure white background.

FLOORS — each room has exactly one floor, exactly inside its walls
Every floor reads as a real material photographed from above, with real joints and natural variation. No floor stays a flat colour or a pattern of plain squares.
- Honed Travertino Romano, satin (greige #DCD9CA in the plan): the elevator hall, the sauna, the shower room, the female bathroom and the male bathroom. Warm ivory-beige with clearly visible parallel veining all running in one direction (honey and light-taupe bands) and small natural pores; rectangular slabs about 60 × 120 cm, 2 mm joints.
- Matte non-slip outdoor Travertino Romano (the same #DCD9CA): the patio. The same banded travertine with pores, matte; slabs about 60 × 120 cm. It is not Bege Bahia and not a cloudy stone.
- Matte Bege Bahia marble: the circulation and the storage room (light grey #E8E8E8 in the plan) and the stair (cream #D8CDB4 in the plan). An even cream-beige with soft cloudy patches and tiny fossil speckles, with no linear veins; square slabs about 60 × 60 cm, 3 mm joints.
- Barlavento tile (grey-green #B7CFC9 in the plan): the service bathroom only. Small light aqua-grey tiles, matte; a dry floor, not water.
- Natural wood (brown with plank lines in the plan): the gym only. Warm wood planks about 20 cm wide, running along the drawn lines, visible grain, staggered joints, matte-satin finish.

GYM, SAUNA AND BATHROOMS
- Gym: only the drawn equipment — two treadmills, two exercise bikes and one weight bench with its barbell — same position, size and orientation, in black, graphite and brushed metal. Nothing else: no plants, racks, dumbbells, mirrors, TV or benches.
- Sauna: one single straight bench in Travertino Romano marble — a smooth, light travertine block — along its bottom wall; travertine floor; no wood in the sauna.
- Bathrooms: vanity countertops in light polished quartz #ECE8E1 with white basins; white sanitary ware and black or chrome fittings, exactly where they are.

WALLS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; no new walls.
- Glass: thin pale-grey glass line #D6D6D3 between two thin black aluminium frame lines, exactly where the plan shows it — the gym's glass wall to the patio, the glass between the gym and the hall, the circulation's sliding glass door, the sauna's L-shaped front and the shower screens.
- Doors: only the five drawn doors, with their arcs and leaves. The elevator and shafts stay as boxes with dashed X's.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours in the basement; no text.

Avoid: any tint, texture, ground colour or lines in the background; highlighting, colouring or travertine on the staggered steps beside the pool; a faded or missing stair down to the gym; a second stair; new rooms, walls, partitions or doors; a partition in the storage room; a door on the top side of the circulation; a door between the gym and the storage room; aqua tiles outside the service bathroom; a wooden sauna bench; plants or extra equipment in the gym; Bege Bahia on the patio; travertine in the circulation or the storage room; full colour, strong texture or vegetation on the faded context; a pool or ofurô with realistic water; shadows; perspective; text.
```

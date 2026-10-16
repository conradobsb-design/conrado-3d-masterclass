# POE 642 · Casa A · Subsolo — prompt v5 (só a imagem base)
_13/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaA_BASE_Subsolo_v3_16x9.png`. A base foi gerada do PDF do cliente (`642-_SUBSOLO_CASA_A_1.pdf`) e não tem imagem de referência.

**Da v4 para a v5 — o que o render da v4 inventou e o que muda:**
- **Escada nova:** além da escada que existe, o motor desenhou um segundo lance descendo pela lateral esquerda do pátio, com parede.
  - O prompt passa a dizer que existe **uma única escada**: o lance reto curto no canto de cima à esquerda do pátio.
  - A lateral esquerda do pátio é só um muro, sem nada encostado.
- **Ambientes novos:** a parte direita do depósito virou uma sauna com bancos de madeira, com parede nova e porta nova para a academia. Também apareceram uma moldura de madeira dentro do depósito e um banco com barra junto à parede de baixo da academia.
  - **Causa:** projeções do CAD (layer `DOC_LINHAS E PROJEÇÕES`) desenhadas como retângulos finos dentro do depósito e junto à parede da academia.
  - **Na base v3:** essas projeções saem. Os X do elevador e dos shafts, que estão na mesma layer, ficam.
  - **No prompt:** entra um mapa dos ambientes, com cada um no seu lugar e as 5 portas que existem. O depósito é uma sala única e vazia, e nada de ambiente, parede ou porta novos.
- **Objetos novos na academia:** vasos de planta, suporte de halteres e um painel na parede. O prompt agora limita a academia aos equipamentos desenhados.
- **Pisos:** o pátio saiu com cara de Bege Bahia, nublado, em vez de travertino. Agora cada piso é descrito ambiente por ambiente, e a diferença entre os dois mármores fica explícita:
  - travertino tem veios paralelos em faixas e poros;
  - Bege Bahia é nublado e uniforme, sem veios lineares.
- **Mantidos:** os materiais, a escada e o pátio com a cor cheia, e o resto esmaecido, inclusive a piscina e o ofurô.

**Da v3 para a v4:** piscina e ofurô esmaecidos (base v2).

**Da v2 para a v3:** prompt reescrito do zero, com a base nova e os materiais definidos agora.
- **Travertino:** hall, sauna, banhos feminino e masculino, e o pátio, em travertino fosco.
- **Bege Bahia:** circulação, depósito e escada.
- **Barlavento:** banho de serviço.
- **Madeira:** academia.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta do subsolo a editar. Ela define a geometria e o layout, e deve ser seguida exatamente.

Transforme a planta numa planta humanizada de apresentação do **subsolo**, rica e fotorrealista, para uma residência de alto padrão. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala;
- cada parede, vidro, porta, escada, linha, equipamento e louça exatamente onde está, com o mesmo tamanho e a mesma forma;
- nada é acrescentado: nenhum ambiente, parede, divisória, porta, escada ou objeto novo.

Muda o acabamento: os pisos e os equipamentos ficam reais e sofisticados, numa paleta quente e calma, com o mesmo acabamento da planta do Térreo.

**OS AMBIENTES, ONDE FICA CADA UM** (o alto da imagem é o lado da piscina)

**Fileira de cima, da esquerda para a direita:**
1. **Banho de serviço:** pequeno, com bacia, cuba e chuveiro.
2. **Circulação:** sala pequena e quadrada.
   - Embaixo, uma porta de correr de vidro para o pátio.
   - À direita, a porta para o depósito.
3. **Depósito:** uma sala única, comprida, retangular e vazia, até a ponta direita da fileira.
   - Não tem divisória, banco, prateleira nem sauna.
   - Não tem porta para a academia.

**No meio:**
- **Academia:** a sala grande e quadrada de piso de madeira.
  - O lado esquerdo é uma parede inteira de vidro, voltada para o pátio.
  - O lado direito tem um vidro para o hall do elevador.
  - Não tem porta própria e não tem porta para o depósito.

**Ala da direita:**
- **Hall do elevador:** um retângulo comprido que sai da academia para a direita.
- No fim do hall ficam o elevador e os dois shafts, caixas com X tracejado.

**Fileira de baixo, da esquerda para a direita:**
1. **Sauna:** com frente de vidro em L e um único banco reto de madeira ao longo da parede de baixo.
2. **Ducha:** a salinha ao lado da sauna, com a sua porta.
3. **Banho feminino.**
4. **Banho masculino.**

Cada banho tem a sua porta, bancada e bacia. Entre os dois fica a área de chuveiro, com boxes de vidro.

**À esquerda:**
- **Pátio de acesso à academia:** a faixa comprida e aberta entre a parede de vidro da academia e o muro simples na extrema esquerda, da circulação até a sauna.

**A única escada:**
- É o lance reto curto no canto de cima à esquerda do pátio, desenhado na horizontal entre o deck de madeira esmaecido e o pátio.
- São cerca de 11 degraus de Bege Bahia num lance único e reto, descendo do deck, à esquerda, para o pátio, à direita.
- **O que não existe:** a escada não faz curva e não há outra escada. O muro da esquerda do pátio não tem nada encostado: nem degraus, nem escada, nem jardineira.

**As portas:** existem só as 5 portas desenhadas com arco:
- banho de serviço;
- circulação para o depósito;
- ducha;
- banho feminino;
- banho masculino.

**COR CHEIA E ENTORNO ESMAECIDO**
- **Cor cheia:** os ambientes do subsolo dentro das paredes pretas, o pátio e a escada.
- **Esmaecido:** todo o resto, que na planta já aparece claro. São a piscina e o ofurô, o deck de madeira do Térreo, os degraus escalonados, o deck da piscina, os contornos tracejados e as linhas do terreno.
  - Fica exatamente como desenhado, como um fantasma claro, dessaturado e de baixo contraste, mais ou menos 50% mais claro.
  - Leva só uma leve sugestão do material (madeira clara, pedra creme clara, azul-água bem claro na piscina e no ofurô), sem textura forte, sem vegetação e sem sombra.
  - Fora do desenho, papel branco limpo.

**PISOS — cada ambiente tem um único piso, exatamente dentro das suas paredes**

Todo piso se lê como material real fotografado de cima, com juntas reais e variação natural. Nenhum piso fica em cor chapada ou em quadrados lisos.
- **Travertino Romano levigado, acetinado** (bege-acinzentado #DCD9CA na planta): hall do elevador, sauna, ducha, banho feminino e banho masculino.
  - marfim-bege quente com **veios paralelos bem marcados, todos na mesma direção** (faixas mel e taupe claro), e poros naturais pequenos;
  - placas retangulares de ~60 × 120 cm, juntas de 2 mm.
- **Travertino Romano fosco antiderrapante, externo** (mesmo #DCD9CA): o pátio.
  - o mesmo travertino em faixas, com poros, fosco;
  - placas de ~60 × 120 cm;
  - **não** é Bege Bahia nem pedra nublada.
- **Mármore Bege Bahia fosco** (cinza-claro #E8E8E8 na planta): circulação, depósito e a escada.
  - creme-bege **uniforme**, com manchas suaves em nuvem e pontinhos de fósseis, **sem veios lineares**;
  - placas quadradas de ~60 × 60 cm, juntas de 3 mm;
  - bem diferente do travertino em faixas.
- **Revestimento Barlavento** (cinza-esverdeado #B7CFC9 na planta): só o banho de serviço.
  - pastilhas ou placas pequenas cinza-água claras, foscas;
  - piso seco, não água.
- **Madeira natural** (marrom com linhas de régua na planta): só a academia.
  - réguas de madeira quente com ~20 cm, na direção das linhas desenhadas;
  - veio aparente, emendas desencontradas, fosco-acetinado.

**ACADEMIA, SAUNA E BANHOS**
- **Academia:** só os equipamentos desenhados, na mesma posição, tamanho e orientação, em preto, grafite e metal escovado:
  - duas esteiras;
  - duas bicicletas ergométricas (os dois aparelhos pequenos);
  - um banco de supino com barra.
  
  Nada mais: sem plantas, suportes, halteres, espelhos, TV ou bancos.
- **Sauna:** um único banco reto de madeira natural clara ao longo da parede de baixo. O piso é de travertino.
- **Banhos:** bancadas em quartzo claro polido #ECE8E1 com cubas brancas, louças brancas e metais em preto ou cromado, exatamente onde estão.

**PAREDES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas e a espessura desenhada. Nenhuma parede nova.
- **Vidros:** linha fina de vidro cinza-claro #D6D6D3 entre dois caixilhos pretos, exatamente onde a planta mostra:
  - a parede de vidro da academia para o pátio;
  - o vidro entre a academia e o hall;
  - a porta de correr da circulação para o pátio;
  - a frente em L da sauna;
  - os boxes.
- **Portas e elevador:** só as 5 portas desenhadas, com arco e folha. O elevador e os shafts são caixas com X tracejado.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara e uniforme, com cor de luz do dia natural e sem sombra projetada de nenhum tipo. Cores vivas e naturais no subsolo, sem texto.

**Evitar:**
- uma segunda escada;
- degraus ao longo do pátio;
- ambientes, paredes, divisórias ou portas novos;
- sauna, bancos ou molduras de madeira no depósito;
- porta entre a academia e o depósito;
- plantas, vasos ou equipamentos extras na academia;
- pátio em Bege Bahia ou pedra nublada;
- circulação ou depósito em travertino;
- cor cheia, textura forte ou vegetação no entorno esmaecido;
- piscina ou ofurô com cor cheia ou água realista;
- água em qualquer outro lugar;
- piso em cor chapada;
- linhas de vidro borradas;
- sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the basement floor plan to edit. It defines the geometry and layout, and you follow it exactly.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) of the basement of a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, and every wall, glass line, door, stair, line, piece of equipment and sanitary fixture exactly where it is, at the same size and shape. Nothing is added: no new room, wall, partition, door, stair or object. What changes is the finish: floors and equipment become real and high-end, in a warm, calm palette that matches the ground-floor plan.

THE ROOMS AND WHERE THEY ARE (top of the image = pool side)
- Top row, left to right: (1) the small service bathroom with toilet, basin and shower; (2) the circulation, a small square room with a sliding glass door to the patio on its bottom side and a door on its right into (3) the storage room — one single, long, empty rectangular room that runs to the right end of the row, with no partitions, no benches, no shelves, no sauna and no door to the gym.
- Middle: the gym, the large square wood-floored room. Its left side is a full-height glass wall facing the patio; its right side has a glass panel to the elevator hall. It has no doors of its own and no door to the storage room.
- Right wing: the elevator hall, a long rectangle running right from the gym, ending at the elevator and two shafts (boxes with dashed X's).
- Bottom row, left to right: (1) the sauna, with an L-shaped glass front and one straight wooden bench along its bottom wall; (2) the small shower room beside it, with its door; (3) the female bathroom; (4) the male bathroom — each bathroom with its door, vanity and toilet, with the shower area and its glass screens between them.
- Left: the patio that gives access to the gym — the long open strip between the gym's glass wall and the plain retaining wall on the far left, from the circulation down to the sauna.
- The only stair: the short straight flight at the top-left corner of the patio, drawn horizontally between the faded wooden deck and the patio — about 11 Bege Bahia steps in one straight run, descending from the deck on the left to the patio on the right. It does not turn and there is no other stair; the patio's left wall has nothing along it — no steps, no stair, no planter.
- Doors: only the five drawn door arcs — service bathroom, circulation to storage room, shower room, female bathroom, male bathroom.

FULL COLOUR AND FADED CONTEXT
Rendered in full colour: the basement rooms inside the black walls, the patio and the stair. Everything else — already drawn pale in the plan — is a faded context: the pool and the ofurô (hot tub), the ground-floor wooden deck, the staggered steps, the pool deck paving, the dashed outlines and the terrain lines. Keep it exactly as drawn, as a light, desaturated, low-contrast ghost about 50% lighter than the basement, with only a faint hint of its materials (pale wood, pale cream stone, a very light aqua tint in the pool and the ofurô), no strong texture, no vegetation and no shadows. Outside the drawing stays clean white paper.

FLOORS — each room has exactly one floor, exactly inside its walls
Every floor reads as a real material photographed from above, with real joints and natural variation. No floor stays a flat colour or a pattern of plain squares.
- Honed Travertino Romano, satin (greige #DCD9CA in the plan): the elevator hall, the sauna, the shower room, the female bathroom and the male bathroom. Warm ivory-beige with clearly visible parallel veining all running in one direction (honey and light-taupe bands) and small natural pores; rectangular slabs about 60 × 120 cm, 2 mm joints.
- Matte non-slip outdoor Travertino Romano (the same #DCD9CA): the patio. The same banded travertine with pores, matte; slabs about 60 × 120 cm. It is not Bege Bahia and not a cloudy stone.
- Matte Bege Bahia marble (light grey #E8E8E8 in the plan): the circulation, the storage room and the stair. An even cream-beige with soft cloudy patches and tiny fossil speckles, with no linear veins; square slabs about 60 × 60 cm, 3 mm joints — clearly different from the banded travertine.
- Barlavento tile (grey-green #B7CFC9 in the plan): the service bathroom only. Small light aqua-grey tiles, matte; a dry floor, not water.
- Natural wood (brown with plank lines in the plan): the gym only. Warm wood planks about 20 cm wide, running along the drawn lines, visible grain, staggered joints, matte-satin finish.

GYM, SAUNA AND BATHROOMS
- Gym: only the drawn equipment — two treadmills, two exercise bikes (the two small machines) and one weight bench with its barbell — same position, size and orientation, in black, graphite and brushed metal. Nothing else: no plants, racks, dumbbells, mirrors, TV or benches.
- Sauna: one single straight bench in light natural wood along its bottom wall; travertine floor.
- Bathrooms: vanity countertops in light polished quartz #ECE8E1 with white basins; white sanitary ware and black or chrome fittings, exactly where they are.

WALLS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges and the drawn thickness; no new walls.
- Glass: thin pale-grey glass line #D6D6D3 between two thin black aluminium frame lines, exactly where the plan shows it — the gym's glass wall to the patio, the glass between the gym and the hall, the circulation's sliding glass door, the sauna's L-shaped front and the shower screens.
- Doors: only the five drawn doors, with their arcs and leaves. The elevator and shafts stay as boxes with dashed X's.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours in the basement; no text.

Avoid: a second stair; steps along the patio; new rooms, walls, partitions or doors; a sauna, benches or wooden frames in the storage room; a door between the gym and the storage room; plants, pots or extra equipment in the gym; Bege Bahia or cloudy stone on the patio; travertine in the circulation or the storage room; full colour, strong texture or vegetation on the faded context; a pool or ofurô in full colour or with realistic water; water anywhere else; flat colour fills; blurred glass lines; shadows; perspective; text.
```

# POE 642 · Casa C · Subsolo — prompt v3 (só a imagem base)
_14/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada (só uma):** `bases/POE642_CasaC_BASE_Subsolo_v3_texturas_16x9.png`.
- **Origem:** foi gerada do PDF do cliente (`642-SUBSOLO_CASA C.pdf`), na mesma folha e no mesmo enquadramento das Casas A e B.
- **Texturas:** a base já traz a prévia dos pisos e da floreira, com as texturas aprovadas nas Casas A e B. O prompt manda manter cada material e só torná-lo fotorrealista.

**Da v2 para a v3 — manter a escala, em destaque:**
- **Logo na abertura:** a primeira instrução do prompt passa a ser manter a escala existente, antes de qualquer outra.
- **Posição medida na base:** o item "ESCALA E ENQUADRAMENTO" ganhou a posição da planta na imagem.
  - a planta ocupa de ~9,5% a ~49% da largura e de ~11% a ~77% da altura;
  - a metade direita da imagem é branca e continua vazia.
- **No Evitar:** entrou "ocupar ou preencher a metade direita vazia".
- **Base:** sem alteração.

**Da v1 para a v2 — sentido de descida dos degraus largos:**
- **O que deu errado:** no render da v1, cada degrau largo saiu com a sombra logo abaixo da borda, o que lê como descida para baixo. A descida é para cima, do caminho para o pátio.
- **Base:** ganhou uma linha de caminhamento nos degraus largos, com o círculo na entrada do caminho e a seta apontando para cima, rumo ao pátio. O resto é igual à da v1.
- **Prompt:** os degraus largos descem para o pátio; a seta aponta só para cima; nenhuma sombra abaixo das bordas. Se houver leitura de profundidade, ela fica do lado de cima de cada borda, do lado do pátio, que é o nível mais baixo.
- **Escada curta numerada:** não muda.

**Pisos e áreas (definidos por você):**
- **Vinílico da Casa A:** academia.
- **Mármore travertino:** varanda do subsolo, sauna, ducha e BH da academia. O banco da sauna fica em travertino, em dois tons mais escuros, como na Casa B.
- **Mármore Bege Bahia:**
  - depósito;
  - área externa: pátio à esquerda da varanda, faixa de degraus largos e caminho comprido que desce.
- **Floreira:** a faixa estreita do lado de fora da parede esquerda da sauna.
- **BH da academia:** a peça branca comprida da parede da direita é uma bancada com cuba.
- **Chuveiros:** os dois quadradinhos (na ducha, em frente à sauna, e no box do BH) são os chuveiros de teto.
- **Esmaecida:** só a escada numerada (degraus 11 a 21), abaixo da sauna. Todo o resto tem a cor cheia.

**Lições das Casas A e B aplicadas:**
- ambientes descritos por posição;
- chuveiros com tipo e lugar;
- escala existente mantida;
- "nada é acrescentado";
- luz chapada, sem sombra.

---

## Versão de validação (PT, só para leitura)

Há uma única imagem de entrada: a planta do subsolo a editar. Ela define a geometria, o layout e os materiais, e deve ser seguida exatamente.

**Antes de tudo: mantenha a escala existente.** A planta sai exatamente do mesmo tamanho e no mesmo lugar da imagem de entrada, sem aproximar, recortar nem centralizar.

Transforme a planta numa planta humanizada de apresentação do **subsolo** de uma residência de alto padrão, rica e fotorrealista. Isto é uma edição da planta, não um desenho novo:
- mesmo enquadramento e mesma escala;
- cada parede, vidro, porta, escada, linha, aparelho, bancada e louça exatamente onde está, com o mesmo tamanho e a mesma forma;
- nada é acrescentado: nenhum ambiente, parede, porta, escada, móvel ou objeto novo.

Os pisos e a floreira já aparecem na planta com o material final. Cada um mantém o material, a cor e a direção das réguas e dos veios, e só ganha acabamento fotorrealista, com juntas reais e brilho sutil.

**ESCALA E ENQUADRAMENTO:** mantenha a escala existente.
- A planta fica exatamente na mesma posição e com o mesmo tamanho na imagem, com a mesma margem branca em volta, mesmo que ocupe só uma parte do quadro.
- **Posição na imagem:** a planta ocupa só a parte da esquerda, de ~9,5% a ~49% da largura e de ~11% a ~77% da altura.
  - A metade direita da imagem é branca e continua vazia.
  - A imagem final tem o mesmo formato 16:9 da entrada.
- Não aproxime, não recorte, não centralize, não amplie, não reduza e não gire nada.
- Mantêm a escala desenhada:
  - a espessura das paredes;
  - o tamanho de cada ambiente, aparelho, bancada e louça;
  - a largura das réguas e das placas de piso.

**FUNDO:** todo o fundo é branco puro e chapado #FFFFFF, sem textura, sem tom e sem cor de terreno.

**OS AMBIENTES, ONDE FICA CADA UM**

**Academia:** a sala grande à direita, em L, com piso vinílico.
- **Aparelhos:** exatamente como desenhados. São dois aparelhos compridos no alto à esquerda, dois pequenos logo abaixo deles e duas estações de musculação com barra à direita.
- **Parede da esquerda:** a parede de vidro voltada para a varanda.

**Elevador:** a caixa fechada no canto de baixo à direita, fora da academia, com a porta para a academia.

**Varanda do subsolo:** a área grande à esquerda da academia, em travertino. Ela se abre para o pátio à esquerda, sem parede.

**Depósito:** a sala vazia abaixo da varanda, à esquerda da parte de baixo da academia, em Bege Bahia.

**Bloco de baixo, à esquerda do depósito, da esquerda para a direita:**
1. **Sauna:**
   - vidro no canto de cima à esquerda, voltado para a varanda;
   - banco de travertino em L, em dois níveis: o degrau da frente em L e o assento junto à parede de baixo, um tom mais escuro.
2. **Ducha:** a passagem estreita entre a sauna e o BH, que desce da varanda. O quadradinho no meio dela é um chuveiro de teto.
3. **BH da academia:**
   - porta no alto;
   - bancada branca comprida com cuba na parede da direita;
   - bacia no canto de baixo à direita;
   - box à esquerda, embaixo, atrás de um vidro, com o chuveiro de teto no quadradinho.

**Floreira:** a faixa estreita do lado de fora da parede esquerda da sauna, entre a sauna e os degraus largos.
- plantas tropicais vistas de cima sobre terra escura;
- exatamente dentro das bordas desenhadas, sem sair delas.

**ÁREA EXTERNA, À ESQUERDA, EM BEGE BAHIA**
- **Pátio:** a área grande à esquerda da varanda.
- **Degraus largos:** a faixa abaixo do pátio, com as bordas dos degraus tracejadas visíveis.
  - descem para cima: do caminho, embaixo, até o pátio, que é o nível mais baixo;
  - a linha de caminhamento fica como desenhada, com a seta apontando só para cima, rumo ao pátio;
  - cada borda é uma linha nítida, sem sombra abaixo dela. Se houver leitura de profundidade, ela fica logo acima de cada borda, do lado do pátio.
- **Caminho:** a faixa comprida que desce até embaixo.

**ESCADA NUMERADA, ESMAECIDA:** a escada abaixo da sauna (degraus 11 a 21).
- fica exatamente como desenhada, como fantasma claro, dessaturado e de baixo contraste;
- leva só uma leve sugestão do material, sem sombra;
- a seta de caminhamento fica como desenhada.

**CHUVEIROS — cada um exatamente onde a planta desenha**
- **Ducha, em frente à sauna:** chuveiro **de teto**, uma ducha quadrada cromada no lugar do quadradinho.
- **Box do BH:** chuveiro **de teto**, uma ducha quadrada cromada no lugar do quadradinho.

Não há chuveiro de parede nem outro chuveiro.

**PISOS — cada ambiente tem um único piso, exatamente dentro das suas paredes**
- **Vinílico, padrão madeira:** academia.
  - marrom médio quente, nunca laranja, como o piso das suítes da Casa A;
  - réguas longas na direção desenhada, veio discreto, fosco.
- **Travertino Romano levigado:** varanda, sauna e banco, ducha e BH da academia.
  - marfim-bege quente com veios paralelos na mesma direção e poros pequenos;
  - fosco e antiderrapante na ducha e no box.
- **Mármore Bege Bahia fosco:** depósito, pátio, degraus largos e caminho.
  - creme-bege claro e uniforme, quase liso;
  - só um pontilhado fino e leve e alguns veios finos e claros;
  - sem manchas, nuvens ou pontos escuros;
  - antiderrapante na área externa.

**LOUÇAS, BANCADAS E APARELHOS**
- **Louças:** brancas, com metais em preto ou cromado.
- **Bancada do BH:** quartzo claro polido #ECE8E1 com cuba branca e torneira cromada.
- **Aparelhos da academia:** exatamente como desenhados, em preto fosco e cinza-grafite, com detalhes cromados.

**PAREDES, VIDROS, PORTAS — nítidos e exatamente como desenhados**
- **Paredes:** poché preto sólido #111111, com bordas retas. Nenhuma parede nova.
- **Vidros:** linha fina cinza-claro #D6D6D3 entre caixilhos pretos finos, exatamente onde a planta mostra:
  - a parede de vidro entre a varanda e a academia;
  - o vidro da sauna;
  - o vidro do box do BH.
- **Portas:** só as desenhadas, com arco e folha, e nenhuma porta nova.

**LUZ E VISTA:** vista de cima ortográfica estrita. Luz clara, uniforme, com cor de luz do dia natural e sem sombra projetada. Cores vivas e naturais, sem texto.

**Evitar:**
- **Fundo:** qualquer tom, textura, cor de terreno ou linha.
- **Escala:** aproximar, recortar, centralizar, ampliar, reduzir ou girar a planta, ou mudar o tamanho de paredes, ambientes, aparelhos, bancadas, réguas ou placas; ocupar ou preencher a metade direita vazia.
- **Ambientes:** ambientes, paredes, portas, móveis ou objetos novos.
- **Pisos:**
  - pisos em cor chapada, ou trocados de material ou de direção;
  - madeira laranja;
  - Bege Bahia manchado;
  - travertino no depósito ou na área externa;
  - Bege Bahia na varanda, na sauna ou no BH.
- **Chuveiros:** chuveiro de parede ou chuveiros a mais.
- **Floreira:** plantas fora das bordas da floreira, ou vegetação em outro lugar.
- **Escada numerada:** cor cheia ou textura forte.
- **Degraus largos:** leitura de descida para baixo, sombra abaixo das bordas ou seta apontando para baixo ou para os dois lados.
- **Geral:** sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
One input image: the basement floor plan to edit. It defines the geometry, the layout and the materials, and you follow it exactly.

FIRST OF ALL, KEEP THE EXISTING SCALE: the plan comes out at exactly the same size and in exactly the same place as in the input image — no zooming in, no cropping, no re-centring.

Edit this plan into a rich, photorealistic humanized presentation plan (planta humanizada) of the basement of a luxury residence. This is an edit of the plan, not a new drawing: keep the same framing and scale, and every wall, glass line, door, stair, line, piece of equipment, countertop and sanitary fixture exactly where it is, at the same size and shape. Nothing is added: no new room, wall, door, stair, furniture or object. The floors and the planter already show their final materials in the plan: keep each one's material, colour and plank or vein direction exactly as it is, and only refine it into a photorealistic surface with real joints and a subtle sheen.

SCALE AND FRAMING
Keep the existing scale. The plan stays exactly where it is in the image and at exactly the same size, with the same white margin around it, even though it fills only part of the frame: do not zoom in, crop, re-centre, enlarge, shrink or rotate anything. The plan occupies only the left part of the image — from about 9.5% to 49% of the width and from about 11% to 77% of the height — and the right half of the image is white and stays empty. The output keeps the same 16:9 frame as the input. Wall thickness, the size of every room, piece of equipment, countertop and fixture, and the width of the floor planks and slabs all stay at the drawn scale.

BACKGROUND
The whole background is pure flat white #FFFFFF, with no texture, tint or ground colour.

THE ROOMS AND WHERE THEY ARE
- Gym: the large L-shaped room on the right, with a vinyl floor. The equipment stays exactly as drawn: two long machines at the top-left, two small ones just below them, and two weight stations with a barbell on the right. Its left side is the glass wall facing the veranda.
- Elevator: the closed box at the bottom-right corner, outside the gym, with its door into the gym.
- Basement veranda: the large travertine area to the left of the gym. It opens to the patio on its left, with no wall.
- Storage room: the empty room below the veranda, to the left of the lower part of the gym, in Bege Bahia.
- Bottom block, to the left of the storage room, left to right: (1) the sauna — glass at its top-left corner facing the veranda, and an L-shaped two-level travertine bench: the L-shaped front step and the seat along the bottom wall, one tone darker; (2) the shower passage (ducha) — the narrow passage between the sauna and the bathroom, coming down from the veranda; the small square in the middle of it is a ceiling shower; (3) the gym bathroom — door at the top, a long white vanity with a basin along its right wall, the toilet at its bottom-right corner, and a shower box at its bottom-left behind a glass screen, with a ceiling shower at the small square.
- Planter: the narrow strip outside the left wall of the sauna, between the sauna and the wide steps — tropical plants seen from above on dark soil, exactly inside its drawn edges.

OUTDOOR AREA ON THE LEFT, IN BEGE BAHIA
The large patio to the left of the veranda, the band of wide steps below it (with their dashed step edges visible) and the long path running down to the bottom. The wide steps descend upward, from the path at the bottom to the patio, which is the lowest level: the walking line stays as drawn, with its arrow pointing only up toward the patio. Each step edge is a crisp line with no shading below it; if any depth cue is shown, it sits just above each edge, on the patio side.

THE NUMBERED STAIR, FADED
The stair below the sauna (steps 11 to 21) stays exactly as drawn, as a light, desaturated, low-contrast ghost with only a faint hint of its material and no shadows; its walking-line arrow stays as drawn.

SHOWERS — each one exactly where the plan draws it
- Shower passage in front of the sauna: one CEILING shower, a square chrome rain head at the small square.
- Bathroom shower box: one CEILING shower, a square chrome rain head at the small square.
There is no wall shower and no other shower.

FLOORS — each room has exactly one floor, exactly inside its walls
- Wood-look vinyl: the gym. A warm medium brown, never orange, like the bedroom floors of the companion house; long planks in the drawn direction, subtle grain, matte.
- Honed Travertino Romano: the veranda, the sauna and its bench, the shower passage and the gym bathroom. Warm ivory-beige with parallel veining in one direction and small natural pores; matte and non-slip in the showers.
- Matte Bege Bahia marble: the storage room, the patio, the wide steps and the path. A light, uniform cream-beige stone, almost plain: only a fine, faint speckle and a few thin light veins; no stains, clouds or dark spots; non-slip outdoors.

FIXTURES, COUNTERTOPS AND EQUIPMENT
- White sanitary ware with black or chrome fittings; the bathroom vanity in light polished quartz #ECE8E1 with a white basin and a chrome faucet.
- Gym equipment exactly as drawn, in matte black and graphite grey with chrome details.

WALLS, GLASS, DOORS — crisp and exactly as drawn
- Walls: solid black #111111 poché with crisp straight edges; no new walls.
- Glass: thin pale-grey glass line #D6D6D3 between thin black frame lines, exactly where the plan shows it — the glass wall between the veranda and the gym, the sauna glass and the bathroom shower screen.
- Doors: only the drawn doors, with their arcs and leaves; no new doors.

LIGHT AND VIEW
Strict top-down orthographic view. Bright, even light in a natural daylight colour, with no cast shadows of any kind; materials read by texture, colour and sheen. Vivid but natural colours; no text.

Avoid: any tint, texture, ground colour or lines in the background; zooming in, cropping, re-centring, enlarging, shrinking or rotating the plan, or changing the size of walls, rooms, equipment, countertops, planks or slabs; filling or using the empty right half of the image; new rooms, walls, doors, furniture or objects; flat-colour floors, or floors changed in material or direction; orange wood; blotchy Bege Bahia; travertine in the storage room or the outdoor area; Bege Bahia in the veranda, the sauna or the bathroom; wall showers or extra showers; plants outside the planter edges or vegetation anywhere else; full colour or strong texture on the numbered stair; wide steps that read as descending downward, shading below their edges, or an arrow pointing down or both ways on them; shadows; perspective; text.
```

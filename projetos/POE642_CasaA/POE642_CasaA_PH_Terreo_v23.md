# POE 642 · Casa A · Térreo — prompt v23
_13/10/2026. Motor: Higgsfield Nano Banana Pro (image-to-image, 16:9, 2K, PNG), com uma única imagem de entrada._

**Imagem de entrada:** `POE642_CasaA_BASE_Terreo_v3_vidros_neutros_16x9.png`, a base colorida com paredes pretas e vidros neutros, na tela 16:9.

**Da v22 para a v23 — mudança de estratégia:**
- Nos renders da v21/v22, o motor redesenhou a planta. Num deles o layout inteiro mudou. Nos outros, entrou mata tropical em volta e mudaram a forma do lote, da piscina, do spa e do deck. O prompt longo (13 mil caracteres) descrevia a casa inteira, e o motor desenhava de novo a partir dessa descrição.
- A v23 é um prompt de **edição** curto, com ~630 palavras e 3.900 caracteres, contra 13 mil na v22. Ele mantém a imagem como está e troca **só** as cores chapadas por pisos reais, cada um dentro do seu contorno. É o modelo oficial do Google para edição: "change only X, keep everything else exactly the same".
- Saíram as descrições de parede ambiente por ambiente. Numa edição, as paredes vêm da própria base, e descrevê-las fazia o motor reinterpretá-las. Ficou só a regra da parede de cima do estar.
- Saíram "arbustos tropicais" e "plantas exuberantes", que puxavam a mata. O jardim agora é grama e vegetação baixa, só dentro dos contornos.
- Ficaram os pisos realistas da v21 em forma curta: veios, grão, placas e juntas.
- Os **móveis ficam exatamente como estão representados na base**: mesmo desenho refinado, com contornos, almofadas e detalhes, sem simplificar, trocar ou reestilizar. Só pode entrar um acabamento sutil dentro das formas que já existem.
- **Paredes, vidros, janelas e gradis** ganharam descrição de representação nítida: parede preta de bordas retas, vidro como linha fina entre dois caixilhos pretos contínua em todo o comprimento, gradil como linha pontilhada escura fina.
- Ficaram os itens do Miro:
  - brises;
  - áreas verdes, com o jardim de inverno;
  - vazios tracejados;
  - prainha;
  - alvenaria vedada, sem TV;
  - pergolado tracejado.

---

## Versão de validação (PT, só para leitura)

Transforme esta planta arquitetônica numa planta humanizada de apresentação. Isto é uma edição da imagem de entrada, não um desenho novo. A imagem fica exatamente como está:
- mesmo enquadramento e mesma escala;
- mesmo contorno do lote;
- cada parede, janela, porta, escada, pilar, linha, símbolo de móvel, carro e a piscina exatamente onde estão, com o mesmo tamanho e a mesma forma.

Mudam só as cores chapadas, que viram pisos reais, cada um exatamente dentro do seu contorno:
- **Áreas bege-acinzentadas #DCD9CA** (estar, jantar, varanda, halls, escada principal, gourmet, lavabo, banho da varanda): Travertino Romano levigado #D9CBB3.
  - marfim-bege quente, veios horizontais suaves em mel e taupe, poros pequenos estucados;
  - placas de ~60 × 120 cm com juntas finas de 2 mm, brilho acetinado.
- **Áreas malva #BFA79F** (cozinha, área de serviço, despensa, escada de serviço, quarto e banho do motorista, garagem): granito Marrom Tabaco polido #4A3426.
  - marrom-tabaco profundo, com grão cristalino graúdo de pontos pretos, âmbar-escuros e creme;
  - placas de ~60 × 60 cm, brilho de polido.
- **Áreas cinza-claro #E8E8E8** (deck da piscina, hall externo, placas de pedestres, escada abaixo do deck do spa) e as bordas da piscina e do spa: mármore Bege Bahia fosco #D8CDB4.
  - bege-creme quente, com manchas suaves em nuvem, pontinhos e pequenos fósseis;
  - placas de ~60 × 60 cm, antiderrapante.
- **Área marrom hachurada #AE8863** em volta do spa: deck de madeira natural #9A6B47.
  - réguas de ~14 cm seguindo exatamente a hachura;
  - veio reto, emendas desencontradas, frestas escuras finas.
- **Piscina e spa azul-claro #DFF6FE:** água turquesa clara e límpida #7CC8D4 sobre revestimento claro Barlavento. A prainha fica mais rasa e mais clara, com borda nítida.
- **Hachura de pontinhos cinza** (acesso de veículos, acesso à garagem e corredor de serviço descoberto entre os dois gradis): pedra portuguesa caramelo #B98A55, pedrinhas irregulares com juntas de areia.
- **Áreas brancas de jardim dentro do lote**, incluindo a jardineira estreita do jardim de inverno: grama natural #6E9150 e vegetação baixa, só dentro dos contornos.
- **Pontos rosa e o quadrado rosa:** pilares pretos sólidos.
- **Linhas finas e longas tracejadas de recuo e curvas de nível cinza-claro:** são removidas.

Os pisos têm variação natural entre placas, sem padrão repetido, e juntas nítidas alinhadas às paredes.

Todo o resto fica exatamente como desenhado, nítido e bem legível:
- **Paredes:** poché preto sólido #111111, bordas retas e nítidas, espessura exatamente como desenhada; alvenaria fechada, sem TV e sem nada fixado. A borda de cima do estar é uma parede preta contínua, com uma janela curta no canto superior esquerdo.
- **Paredes de vidro e janelas:** cada uma exatamente onde a base mostra, como uma linha fina de vidro cinza-claro #D6D6D3 entre duas linhas finas de caixilho preto de alumínio. Nítidas, contínuas em todo o comprimento, mais claras e mais finas que as paredes.
- **Gradis do corredor de serviço:** barras finas de metal preto entre pequenos postes quadrados, lidos como uma linha escura pontilhada fina e nítida, vazada.
- **Continuam exatamente como desenhados:** portas (arcos e folhas), o zigue-zague dos brises (como lâminas escuras finas), os X tracejados dos vazios, a grade tracejada do pergolado e os muros cinza-escuros.
- **Móveis:** ficam exatamente como estão representados na base, no mesmo desenho refinado:
  - cada contorno, almofada, costura e detalhe;
  - mesma posição, tamanho e orientação;
  - sem simplificar, trocar ou reestilizar;
  - só um acabamento real sutil (linho, carvalho, metal preto) dentro das formas que já existem.

**Luz e vista:** luz chapada e uniforme, sem sombra de nenhum tipo; vista de cima ortográfica estrita; papel branco limpo fora do lote; sem texto.

**Evitar:**
- redesenhar, mover, acrescentar ou remover qualquer coisa;
- mudar a forma do lote;
- árvores, arbustos ou vegetação novos fora dos contornos de jardim;
- qualquer parede ou vidro alterado;
- linhas de vidro, janelas ou gradis borrados, interrompidos ou sumidos;
- móveis simplificados, trocados ou reestilizados;
- azul fora da piscina e do spa;
- revestimento da piscina escuro;
- sobrar cor chapada;
- sombras, perspectiva e texto.

---

## Prompt para o motor (EN, colar inteiro)

```
Edit this architectural floor plan into a humanized presentation plan. This is an edit of the input image, not a new drawing. Keep the image exactly as it is: the same framing and scale, the same lot outline, and every wall, window, door, stair, column, line, furniture symbol, car and the pool exactly where they are, at the same size and shape. Change only the flat colour fills into realistic floor materials, each one staying exactly inside its own outline:

- Greige #DCD9CA areas (living, dining, veranda, halls, main stair, gourmet, powder room, veranda bathroom): honed Travertino Romano #D9CBB3 — warm ivory-beige, soft horizontal honey-taupe veining, tiny filled pores, slabs about 60 × 120 cm with fine 2 mm joints, satin sheen.
- Mauve #BFA79F areas (kitchen, laundry, pantry, service stair, driver's room and bath, garage): polished Marrom Tabaco granite #4A3426 — deep tobacco brown with a coarse crystalline grain of black, dark-amber and cream specks, slabs about 60 × 60 cm, polished sheen.
- Light grey #E8E8E8 areas (pool deck, external hall, stepping slabs, steps below the spa deck) and the pool and spa copings: matte Bege Bahia marble #D8CDB4 — warm cream-beige with soft cloudy tones, fine speckles and small fossil marks, slabs about 60 × 60 cm, non-slip.
- Brown hatched #AE8863 area around the spa: natural hardwood deck #9A6B47 — boards about 14 cm wide running exactly along the hatching, straight grain, staggered joints, thin dark gaps.
- Pale blue #DFF6FE pool and spa: clear light-turquoise water #7CC8D4 over light Barlavento tiles; the wet deck (prainha) shallower and lighter, with a crisp edge.
- Grey dotted hatch (driveway, garage access and the uncovered service passage between the two railings): caramel Portuguese cobblestone (pedra portuguesa) #B98A55 — small irregular stones with sand joints.
- White garden areas inside the lot, including the narrow winter-garden planter: natural lawn #6E9150 and low planting, only inside their outlines.
- Pink column dots and the pink square: solid black columns.
- The long thin dashed setback lines and the faint grey terrain contours are removed.

Floors show natural variation between slabs, no repeated pattern, and crisp joints aligned with the walls.

Everything else stays exactly as drawn, crisp and clearly readable:
- Walls: solid black #111111 poché with crisp straight edges and exactly the drawn thickness; closed masonry with no TV and nothing mounted on them. The top edge of the living room is a continuous black wall with one short window in its top-left corner.
- Glass walls and windows: every one exactly where the input shows it, as a thin pale-grey glass line #D6D6D3 between two thin black aluminium frame lines — crisp, continuous along its full length, lighter and thinner than the walls.
- Service-passage railings (gradil): slim black metal bars between small square posts, read as a crisp thin dark dotted line, see-through.
- Doors (arcs and leaves), the zig-zag brise line (as dark slim blades), the dashed void X's, the dashed pergola grid and the dark grey boundary walls stay exactly as drawn.
- Furniture: kept exactly as represented in the input — the same refined drawings with every outline, cushion, seam and detail, the same position, size and orientation; not simplified, replaced or restyled; only a subtle real material finish (linen, oak, black metal) inside the existing shapes.

Flat, even lighting with no shadows of any kind; strict top-down orthographic view; clean white paper outside the lot; no text.

Avoid: redrawing, moving, adding or removing anything; changing the lot shape; new trees, shrubs or vegetation outside the garden outlines; any wall or glass changed; blurred, broken or missing glass lines, windows or railings; simplified, replaced or restyled furniture; blue outside the pool and spa; a dark pool lining; flat colour fills left over; shadows; perspective; text.
```

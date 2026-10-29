# POE 642 · CASA A — HANDOFF PARA CLAUDE CODE
_Resumo da conversa em 13/10/2026. Estúdio: Conrado 3D Studio. Arquitetura: Denise Zuba (Projetos D. Zuba)._

## 1. Objetivo
Gerar as **plantas humanizadas** da Casa A em três pavimentos: Subsolo, Térreo e 1º Pavimento.
- **Motor principal:** Higgsfield Nano Banana Pro, image-to-image, saída 16:9 · 2K · PNG.
- **Teste atual:** o Térreo no GPT ("GPT Astra"), com uma única imagem de entrada.
- **Foco atual:** TÉRREO. O 1º pavimento fica para depois.

## 2. Preferências fixas do Conrado (seguir sempre)
1. Depois de qualquer alteração, **reescrever e entregar o prompt COMPLETO**, nunca só o trecho alterado.
2. O prompt de **validação vai em português**, só para leitura. O que vai para o motor é **sempre em inglês**.
3. **Não chamar** o feedback do cliente de "correções" dentro do prompt. Os elementos são descritos no contexto, porque cada geração é nova.
4. Planta humanizada usa **iluminação chapada, SEM sombras**.
5. Os materiais são **os definidos pelo cliente** (planilha de materiais), e as observações do Miro precisam constar no prompt.
6. As bases saem dos **PDFs** enviados. Ele não manda PNG.

## 3. Fontes
- **Miro:** board "POE 642 – Revisão de Imagens", https://miro.com/app/board/uXjVJkj7NUw=/
  - Contém as Considerações gerais e o Feedback item a item da Casa A: itens 1–9 do Subsolo, 10–19 do Térreo e 20–25 do 1º Pavimento.
  - O conector do Miro deu acesso negado. A leitura foi feita pelo Chrome do usuário, só com zoom e arraste: sem cliques, sem edições, sem JavaScript.
- **Drive, especificações:** pasta `1NNi_gHWYJs-KvOJSBBP_GZTEpqeGvXrG`. Tem a planilha "ESPECIFICAÇÕES DE MATERIAIS CASA A", as "ESPECIFICAÇÕES GERAIS" e o caderno.
- **Drive, PDFs de arquitetura:** pasta `10UABd77xZ9V2R3G85xkOdnvg1kCgrsMj`. Tem a situação/locação 642-ARQ-EX-002 e as plantas de piso 642-ARQ-EX-021.
- **Norte:** cerca de 30° no sentido horário a partir do topo (NE). Entra na **pós-produção**, não no prompt.

## 4. Arquivos
Os arquivos estão no PC em `C:\Users\55619\Documents\Claude\Projects\RENDER IA\POE 642\Casa A\`.

| Arquivo | O que é |
|---|---|
| `POE642_CasaA_BASE_Terreo.png` / `_1Pavimento.png` / `_Subsolo.png` | Bases sem texto, geradas do PDF (6001×3884) |
| `POE642_CasaA_BASE_Terreo_v2_vidros.png` | Térreo com vidros em azul. **Abandonada**, porque o azul vazava para o render |
| **`POE642_CasaA_BASE_Terreo_v3_vidros_neutros.png`** | **BASE ATUAL do Térreo**: paredes pretas e vidros em cinza #D6D6D3 com contorno preto de 2 px |
| `POE642_CasaA_REF_Terreo_AlaSocial*.png` | Recortes da ala social. **Não usar mais**: agora vai só a imagem completa |
| `POE642_CasaA_PH_Terreo.md` | Prompt do Térreo, **v17** (atual) |
| `POE642_CasaA_PH_1Pavimento.md` | Prompt do 1º Pav, v4, já no formato "specific elements" |
| `POE642_CasaA_PH_Subsolo.md` | Prompt do Subsolo, v2, **ainda no formato antigo** "CLIENT CORRECTIONS C1–C9" |

## 5. Pipeline técnico das bases (PyMuPDF)
1. **Remoção de texto:** anotações de redação em todos os textos, depois `apply_redactions`.
2. **Recorte:** `Rect(W*0.035, H*0.095, W*0.975, H*0.955)`, renderizado com 6000 px de largura.
3. **Parede × vidro, a partir da layer `ARQ_PAREDE`:**
   - o preenchimento cinza 0.357 vira preto #111111;
   - formas finas com preenchimento branco e traços retos longos são vidro;
   - as folhas de porta junto a arcos ficam de fora;
   - traços que caem sobre parede ficam de fora (teste pelo ponto médio).
4. **Zonas excluídas da detecção de vidro** (coordenadas numa visualização de 1800 px de largura):
   - muros: y<100 ou y>1030;
   - bancada gourmet (655,680,822,782);
   - ilha da cozinha (900,678,978,702);
   - folha da porta principal (1092,362,1192,378);
   - gradis do corredor de serviço (772,885,792,1040) e (888,885,906,1040).
5. **Cor final do vidro:** cinza neutro #D6D6D3 com contorno preto, feito com `scipy.ndimage.binary_dilation` (2 px). Nunca usar azul.

## 6. Decisões de material — TÉRREO
| Área | Material |
|---|---|
| Estar, jantar, varanda, hall interno, escada principal, gourmet, lavabo, banho da varanda | Travertino Romano #D9CBB3, levigado |
| Cozinha, serviço, despensa, escada de serviço, quarto e banho do motorista, garagem | Granito **Marrom Tabaco** #4A3426, polido. Marrom, não preto |
| Hall externo, placas do acesso de pedestres, **deck da piscina**, **escada abaixo do deck do spa** | Mármore **Bege Bahia** #D8CDB4, fosco antiderrapante |
| Acesso de veículos, acesso à garagem (em nível, sem rampa), **corredor de serviço descoberto entre os gradis** | Pedra portuguesa **caramelo** #B98A55 |
| Deck do spa | Madeira #9A6B47, réguas horizontais |
| Piscina e spa | Pedra Hitam, água #2F5D5A |
| Jardim / muros | Grama #6E9150 / cinza-escuro #3A3A3A |

**Feedback do Miro incorporado:**
- **10:** brises rotativos na varanda gourmet.
- **11:** áreas verdes, incluindo o jardim de inverno.
- **12:** projeção dos vazios em tracejado.
- **13:** deck molhado (prainha) com a delimitação correta.
- **14:** alvenaria preta 100% vedada, sem TV.
- **Pergolado:** grade tracejada sobre o deck da piscina.

## 7. Decisões — 1º PAVIMENTO (prompt v4 no arquivo)
- Quartos e closets em Durafloor City Petra #A8784F, madeira média quente, nunca laranja.
- Circulação, sala íntima e banhos em Travertino Romano.
- Bloco de serviço em **granito cinza-claro #C9C7C2**.
- Quarto de serviço **vazio**, conforme o item 22 do Miro.
- Chuveiro de teto **só** no banho master e no banho da suíte 3.
- Elevador e shaft **fechados**, não são vazios.
- Vazios de pé-direito duplo em cinza-escuro #4A4A4A com X tracejado.
- Escada sobe da direita para a esquerda.
- Pergolado só tracejado. Entorno esmaecido, cerca de 40% mais claro.
- O item 21 (pilares) foi desconsiderado.

## 8. Decisões — SUBSOLO (prompt v2 no arquivo)
- Academia em Durafloor #A8784F.
- Sauna com piso em travertino e um único banco reto de madeira.
- Pátio em travertino fosco.
- Entorno esmaecido.

## 9. Pendências
- [ ] Rodar o Térreo v17 no GPT e no Higgsfield e avaliar o resultado.
- [ ] Gerar as bases com vidro neutro e paredes codificadas para o **1º Pavimento** e o **Subsolo**, com o mesmo pipeline da seção 5.
- [ ] Converter o Subsolo para o formato sem "correções", descrevendo os elementos no contexto.
- [ ] Perguntas em aberto para o Conrado:
  - o depósito e o banho de serviço do subsolo ficam em granito preto ou cinza-claro?
  - o acabamento do Marrom Tabaco é polido mesmo? (hoje está assumido);
  - qual a espécie de madeira do deck do spa?
- [ ] Pós-produção: inserir o norte e a seta de subida das escadas.

## 10. Restrições de ambiente que já apareceram
- O upload direto para o Higgsfield é bloqueado pelo proxy, tanto no container quanto no PC. O usuário sobe as imagens manualmente.

---

## 11. PROMPT ATUAL — TÉRREO v17 (EN, para o motor)
**Imagem única de entrada:** `POE642_CasaA_BASE_Terreo_v3_vidros_neutros.png`
_A versão em português, para validação, está em `POE642_CasaA_PH_Terreo.md`._

```
BLOCK 0 — HOW TO READ THE INPUTS
One input image is provided: the complete ground-floor plan drawn in flat CAD colours. It is a strict geometric template, not a style reference, and it defines the full output framing. Transform THIS image into the rendered plan — same drawing, same position of every line.
Wall versus glass in the image:
- SOLID BLACK bands = masonry walls, fully closed.
- THIN PALE-GREY STRIPS OUTLINED IN BLACK = GLASS (windows, glass walls, sliding glass panels, glass partitions). Keep them exactly like that in the output: a thin neutral pale-grey line #D6D6D3 between two thin black aluminium frame edges. Glass in plan is NEUTRAL GREY — never blue, never cyan, never teal, never tinted.
- Thin black quarter-circle arcs with a thin leaf line = swing doors (opaque doors, not glass).
Reading the rest of the drawing:
- Flat khaki fill = social floor area. Flat mauve fill = service floor area. Light-blue fill = pool and spa water (the ONLY blue in the base).
- Fine horizontal hatching on the left of the pool, wrapping around the spa = the spa wooden deck. Plain light-grey paved area around the pool (where the two sun loungers stand) = the pool deck.
- Small grey hatched dots pattern = vehicle driveway. Large separate grey rectangles on the right = the pedestrian access stepping slabs leading to the house.
- Pink dots and the pink square = structural columns.
- Diagonal dashed X squares over the veranda = projection of the double-height voids above.
- The grid of thin squares over the pool deck, between the pool/wet deck and the gourmet veranda = projection of the PERGOLA above.
- The zig-zag line on the left edge of the gourmet veranda = a row of rotating brise blades.
- White unbuilt areas inside the lot = garden. Thick dark lines at top and bottom edges = boundary walls.
- The white furniture symbols are the furniture layout: keep every piece in its exact position, size and orientation.

BLOCK 1 — ROLE
You are an architectural visualization artist producing a photorealistic humanized floor plan (top-down orthographic, 90° plan view) for a luxury residence presentation. Output must look like a premium real-estate marketing plan, not a 3D perspective.

BLOCK 2 — GEOMETRY (ABSOLUTE)
- Preserve 100% of the base: outline, wall positions and thickness, openings, doors, windows, stairs, pool, furniture layout, lot boundaries. Same framing, same scale, no crop, no rotation, no perspective.
- Every black wall is rendered as SOLID BLACK #111111 poché, crisp edges, uniform, 100% closed masonry.
- Every glass strip stays neutral glass: a thin pale-grey line #D6D6D3 between thin black frame edges, clearly lighter and thinner than the walls, with no blue colour at all.
- Structural columns: every pink dot is a solid black round column; the pink square is a solid black square column.
- Nothing is added: no extra room, wall, door, window, furniture or object; no wall becomes glass and no glass becomes wall.
- NO TEXT anywhere: no room names, no labels, no numbers, no dimensions, no logos, no watermark.
- The long thin dashed setback lines and the faint grey terrain contour lines are not part of the render; only the dashed X projections over the veranda and the dashed pergola grid over the pool deck remain.

BLOCK 3 — MATERIALS (PBR, plan view)
- Living, dining, veranda, internal hall, main stair, gourmet space, lavatory, veranda bathroom: Travertino Romano marble #D9CBB3, honed, roughness 0.45, soft horizontal vein streaks, large-format slabs with fine joints.
- Kitchen, laundry, pantry, service stair, driver's room and bath, garage: Marrom Tabaco granite — deep tobacco-brown base #4A3426 with black and dark amber crystals, polished, roughness 0.2. Brown, not black.
- External entrance hall and the pedestrian access stepping slabs on the right: Bege Bahia marble #D8CDB4 — warm cream-beige stone with fine light speckles and small natural fossil marks, matte non-slip finish, roughness 0.6; lawn in the joints between the stepping slabs.
- Vehicle driveway, every access path to the garage and the uncovered service passage: Portuguese cobblestone mosaic (pedra portuguesa) in caramel tone #B98A55, small irregular stones, visible joints. The uncovered service passage is the long rectangle below the laundry, between the two black railings, running from the laundry door down to the bottom boundary wall, just left of the driveway (it carries a dashed X in the base). It is paved in exactly the same caramel cobblestone as the driveway, continuous with it — never light stone, never Bege Bahia, never grey.
- Pool interior: Hitam black stone, so the water reads deep teal-green #2F5D5A, clear. Spa same finish.
- Pool deck (plain light-grey paved area around the pool, with the sun loungers): Bege Bahia marble #D8CDB4, matte non-slip, large slabs with fine joints — stone, not wood.
- Steps below the spa deck (the short flight of steps at the bottom edge of the spa deck, leading down to the lawn): Bege Bahia marble #D8CDB4, matte non-slip — the same stone as the pool deck, not wood.
- Spa deck (fine horizontal hatching around the spa): natural hardwood decking #9A6B47, matte, long boards running horizontally exactly as the hatching lines, thin gaps — wood, not stone.
- Garden: natural lawn #6E9150 with planting beds and tropical shrubs.
- Boundary walls: solid dark grey #3A3A3A.
- Glass: neutral clear glass seen from above = thin pale-grey line #D6D6D3 with thin black aluminium frames. Absolutely no blue or cyan tint.
- Furniture: neutral premium palette (off-white linen #EDE8DF, natural oak #A8865E, black metal). Cars as drawn, realistic, seen from above.

BLOCK 4 — WALLS AND GLASS, ZONE BY ZONE (exactly as the base shows)
- Veranda lounge (top-left room with two armchairs, curved sofa and three-seat sofa): top side is one continuous solid black wall with no opening; left side has no wall and opens to the pool deck; bottom side is open to the covered veranda.
- Covered veranda column (veranda lounge, veranda armchairs, veranda dining tables): its whole left edge towards the pool deck is completely OPEN — no glass, no frame, no line, just the travertine floor meeting the Bege Bahia pool deck.
- Main glass façade of the living and dining room: one long continuous glass wall (sliding glass panels, thin black frames) running vertically from the top wall down to the kitchen. It separates the covered veranda column on the left (veranda lounge, veranda armchairs, veranda dining tables) from the indoor living and dining room on the right.
- Top edge of the living room: one short window in the corner next to the veranda lounge, then solid black wall up to the lavatory. A tall white built-in cabinetry panel runs along the right side of the living room.
- Lavatory: solid black walls; one window in its top wall; single swing door at its lower-left; skylight projection drawn as a thin dashed rectangle; Travertino Romano vanity with a sculpted stone basin carved in the same stone.
- Home office: top wall is solid black on the left part and a window on the right part; the top-right corner is glazed — the right wall is glass from the corner down to about one third of its length, then solid black wall; a light linen curtain runs along that glass; bottom wall solid black; swing door at the lower-left from the hall; white L-shaped built-in shelving along the left wall.
- Main entrance: a large pivoting entrance door between the internal hall and the external hall — an opaque door, not glass.
- Main stair: enclosed by solid black walls at top and bottom; its left side (facing the dining room) and its right side (facing the garden) are full-height glass walls.
- Kitchen: solid black walls on top and bottom; its left wall has one glazed opening in the middle towards the dining/gourmet area; its right wall has a swing door and then a long glass panel alongside the sinks.
- Bottom (service) façade: small windows on the bottom walls of the veranda bathroom, the lavatory and the laundry, exactly where the thin grey glass strips appear; everything else on that façade is solid black wall.
- Garage: right side is a solid black wall with one single window in the middle; the front opens to the driveway.
- Service passage fences: the two thin double lines with small posts that run from the uncovered service yard down to the bottom boundary wall (the two long sides of the cobblestone service passage) are black metal railings (gradil) — slim black vertical bars between small square posts, see-through, seen from above as a thin dark dotted line. Not glass, not masonry.
- Gourmet veranda: left edge is the row of vertical rotating black aluminium brise blades along the zig-zag line, clearly visible as dark slim blades; no glass there.

BLOCK 5 — OTHER SPECIFIC ELEMENTS
- Green areas: the winter garden (the narrow planter strip below the lavatory) is filled with lush tropical plants; every garden around the building is green — lawn left of the deck and gourmet area, garden under the main stair, garden beside the driver's room, lawn on the right side of the lot.
- Void projections: the double-height voids above the veranda are shown only as thin dashed lines (outline plus dashed diagonal X) over the travertine floor — never as solid lines, shading or a different floor.
- Pergola over the pool deck: the grid of squares between the pool/wet deck and the gourmet veranda is the projection of a pergola above, shown only as thin dashed square lines over the Bege Bahia pool deck, exactly as the grid in the base — no solid beams, slats, roof or shading.
- Wet deck (prainha): the lower section of the pool rectangle, separated by a thin line, is a shallow ledge. Its outline follows exactly the rectangle drawn in the base, with lighter shallow water and a crisp, clearly visible edge to the deep pool.
- Garage access: caramel Portuguese cobblestone all the way to the garage; the access is level, with no ramp.

BLOCK 6 — LIGHTING
Flat, even, shadowless illumination, like a clean presentation plan. NO cast shadows, NO drop shadows, NO contact shadows, NO ambient occlusion, NO sun direction, NO vignetting. Every surface lit uniformly; materials read by texture and colour only.

BLOCK 7 — CAMERA
Strict orthographic top view, 90°, identical to the framing of the input image. No tilt, no perspective, no depth of field.

BLOCK 8 — COLORIMETRY
Neutral-warm white balance ~5000K. Clean white sheet background outside the lot. Natural saturation; travertine and Bege Bahia stay warm beige, spa deck stays natural wood, Marrom Tabaco granite stays deep brown, cobblestone stays caramel, lawn stays natural green, glass stays neutral pale grey. The ONLY blue-green tones allowed in the whole image are the pool and spa water; everything else is free of blue.

BLOCK 9 — CHECKLIST
☐ thick black = solid wall, thin grey strip = glass  ☐ glass neutral grey, no blue anywhere except pool/spa water  ☐ walls and glass zone by zone as BLOCK 4  ☐ columns in black  ☐ no text  ☐ materials as listed  ☐ service passage in caramel cobblestone  ☐ steps below spa deck in Bege Bahia  ☐ gardens around the house  ☐ pergola as dashed grid  ☐ no shadows  ☐ framing 16:9

INVALIDATION
Reject if: any blue or cyan colour remains outside the pool and spa water (on glass lines, frames, walls or floors); any wall becomes glass or any glass becomes wall; the service-passage railings become walls or glass; any text or label appears; any shadow appears; any wall, door or window is moved, added or removed; the pool deck becomes wood; the spa deck becomes stone; a solid pergola appears; the external hall or access slabs are dark; the service-area granite turns black; the driveway or the service passage is grey, black or light stone; the steps below the spa deck are wood; perspective or 3D tilt appears; furniture is added.
```

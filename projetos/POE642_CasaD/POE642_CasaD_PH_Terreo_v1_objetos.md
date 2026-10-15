# POE 642 · Casa D · Térreo — objetos pessoais e decorativos (Higgsfield)

> **Descartado (15/10/26):** o usuário testou e o resultado não ficou a contento; os objetos não entram na entrega.

**Motor:** Nano Banana Pro, 2K, 16:9.
**Imagem de entrada (única):** `renders/POE642_CasaD_PH_Terreo_v1_retocado.png` (o render retocado atual).
**Mapa dos lugares:** `renders/POE642_CasaD_PH_Terreo_v1_objetos_alvos.jpg` (só para conferência; não entra no motor).

Os renders aprovados das Casas A, B e C não têm objetos sobre os móveis (as mesas estão vazias), então não há de onde tirar livros, óculos ou arranjos. O motor gera os objetos sobre a imagem atual; depois, sem IA, a imagem dele é alinhada ao retocado e **só os objetos dos 10 lugares abaixo** são trazidos (cada um recortado na caixa do móvel). O resto da imagem do motor é descartado, então qualquer outra mudança que ele fizer não entra.

## Validação (PT)

Sobre a imagem, sem mudar mais nada: acrescentar objetos pequenos do dia a dia, vistos de cima, em 10 móveis (não em todos):

1. **Estar, a maior das duas mesas de centro redondas:** dois livros de arte empilhados e uma tigela de cerâmica pequena.
2. **Estar, mesa lateral redonda à direita do sofá:** óculos de leitura dobrados e uma xícara com pires.
3. **Sala íntima (entre as suítes 1 e 2), mesa de centro redonda:** bandeja redonda com uma vela e um vasinho de flores secas.
4. **Sala íntima, mesa lateral junto à poltrona:** um livro aberto.
5. **Suíte master, criado-mudo da esquerda:** dois livros empilhados e óculos.
6. **Suíte 1, criado-mudo de cima:** pequeno arranjo de flores num vaso de vidro.
7. **Suíte 2, criado-mudo de baixo:** um livro e um celular.
8. **Suíte 1, escrivaninha:** notebook fechado e uma caneca.
9. **Escritório, escrivaninha:** caderno aberto com caneta e um porta-lápis.
10. **Aparador acima da mesa redonda do estar:** escultura pequena de cerâmica, dois livros empilhados e um vaso alto com galhos.

Regras: tudo pequeno e na escala dos móveis (cada objeto cabe dentro do tampo, com folga); cores neutras e quentes, sem cor forte; luz chapada e uniforme como a da imagem, sem sombra nova além do contato suave dos móveis; sem texto, sem rótulo, sem número; mesmo enquadramento, escala e resolução; nada mais muda (pisos, paredes, móveis, plantas, carros e piscina iguais).

## Prompt (EN, para o motor)

```
Edit this top-down architectural floor plan render. Keep the image exactly as it is: same framing, same scale, same 16:9 aspect ratio, same resolution, same floors, walls, furniture, rugs, plants, cars and pool. Do not move, resize, recolor or redraw anything that is already there.

Only add a few small everyday personal objects, seen strictly from directly above (orthographic top view), resting on top of these 10 pieces of furniture, and nowhere else:

1. Living room, the larger of the two round wooden coffee tables in the center: two stacked art books and a small ceramic bowl.
2. Living room, the small round side table to the right of the white sofa: folded reading glasses and a coffee cup on a saucer.
3. Family room between the two bedroom suites at the bottom, the round wooden coffee table: a round tray with one candle and a tiny vase of dried flowers.
4. Same family room, the small round side table next to the armchair: one open book.
5. Master suite (bottom left), the left bedside table: two stacked books and reading glasses.
6. Suite 1 (bottom center), the upper bedside table: a small flower arrangement in a clear glass vase.
7. Suite 2 (bottom right of the family room), the lower bedside table: one book and a smartphone.
8. Suite 1, the wooden desk against the top wall: a closed laptop and a mug.
9. Home office (bottom right), the wooden desk with chairs: an open notebook with a pen and a small pencil cup.
10. The long wooden sideboard against the top wall above the round dining table with four armchairs: a small ceramic sculpture, two stacked books and a tall vase with branches.

Rules: every object is tiny and true to the scale of the furniture, fully inside the tabletop with a margin. Neutral, warm, muted colors (cream, sand, terracotta, light wood, matte black accents). Flat, even, shadowless lighting matching the image; only the same very soft contact shadow already used on the furniture. Top-down view only, no perspective, no tilted objects. No text, no labels, no numbers, no logos. Leave every other table, bedside table and surface empty.
```

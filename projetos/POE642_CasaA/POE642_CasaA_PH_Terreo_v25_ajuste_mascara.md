# POE 642 · Casa A · Térreo — ajuste v25 com máscara (render aprovado)
_13/10/2026._

**Por que o ajuste sem máscara não funcionou:** o Nano Banana Pro não aceita máscara no Higgsfield (no catálogo, só imagens de referência). Toda edição redesenha a imagem inteira, então outros pisos mudam junto. Para alterar só três pontos de uma imagem aprovada, a edição tem que ficar presa a uma máscara. Fora dela, nenhum pixel muda.

## Onde fazer
1. **Photoshop, com Preenchimento generativo (recomendado):**
   1. abra o render aprovado;
   2. selecione só a área a mudar;
   3. use *Preenchimento generativo* com o prompt da área. O Firefly altera apenas a seleção.

   Faça uma área por vez, com seleções separadas.
   - Para marcenaria e bancadas, que são só mudança de cor, dá para fazer **sem IA**: selecione e aplique *Camada de preenchimento de cor* no modo *Cor* ou *Multiplicação*, nas cores abaixo. Fica exato.
2. **Higgsfield, com Nano Banana 2 em modo inpaint:**
   1. envie o render aprovado como imagem;
   2. envie uma máscara branca sobre a área a mudar, preta no resto;
   3. ative o inpaint e use o prompt da área.

   Uma área por rodada.

## Áreas e prompts (EN, um por área)

**1. Deck da piscina e escadas** (selecione o piso cinza/branco em volta da piscina, a faixa junto aos brises e as duas escadas ao lado do deck de madeira, sem as espreguiçadeiras)
- PT: piso de mármore Bege Bahia visto de cima, bege-creme quente com manchas em nuvem, pontinhos e pequenos fósseis, fosco, placas de ~60 × 60 cm com juntas finas, igual às placas de pedestres; luz chapada sem sombras.

```
Bege Bahia marble paving seen from directly above: warm cream-beige stone #D8CDB4 with soft cloudy tones, fine light speckles and small natural fossil marks, matte, slabs about 60 x 60 cm with fine straight joints, the same stone as the stepping slabs of the plan. Flat, even, shadowless light; strict top-down view; no text.
```

**2. Marcenaria** (selecione armários da cozinha, painel alto do estar, estantes, bases do bar e da churrasqueira, armários da área de serviço)
- PT: os mesmos armários e marcenaria, mesmas formas e posições, em laca fosca tom areia quente #CBB89E, vistos de cima, luz chapada.
- Sem IA: preenchimento de cor **#CBB89E** no modo *Cor*.

```
The same built-in cabinets and joinery seen from directly above, exactly the same shapes, edges and positions, finished in matte warm sand lacquer #CBB89E, smooth and clearly distinct from the floor. Flat, even, shadowless light; strict top-down view; no text.
```

**3. Bancadas** (selecione os tampos: ilha e bancadas da cozinha, bar e churrasqueira do gourmet, bancadas da área de serviço e dos banheiros, sem cubas e cooktops)
- PT: os mesmos tampos, mesmas formas, em quartzo claro polido #ECE8E1 com pontilhado fino e sutil, vistos de cima; cubas e cooktops mantidos.
- Sem IA: preenchimento de cor **#ECE8E1** no modo *Cor* ou *Normal* com 90% de opacidade.

```
The same countertops seen from directly above, exactly the same shapes and edges, with the sinks and cooktops kept as they are, in light polished quartz #ECE8E1 with a fine, subtle speckle, clearly lighter than the floor. Flat, even, shadowless light; strict top-down view; no text.
```

> Para confirmar: com "todas as bancadas em quartzo", a do **lavabo**, que era de travertino com cuba esculpida, também muda. Se quiser manter o travertino só ali, deixe o lavabo fora da seleção.

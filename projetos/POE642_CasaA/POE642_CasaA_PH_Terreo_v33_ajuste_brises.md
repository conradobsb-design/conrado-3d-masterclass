# POE 642 · Casa A · Térreo — ajuste v33: brises da varanda gourmet
_13/10/2026. Edição sobre o render aprovado da v33._

**O que sai:** à esquerda da fileira de brises, na faixa de Bege Bahia entre o gramado e o lounge do gourmet, sobraram duas coisas:
- faixas cinza diagonais e esfumadas, uma por lâmina, que parecem sombras ou cópias fantasmas das lâminas;
- manchas cinza arredondadas nos pivôs das lâminas.

**O que fica:**
- as 7 lâminas pretas, com a mesma posição, ângulo, comprimento e espessura;
- a linha fina em que as lâminas giram;
- todo o resto da imagem.

## Onde fazer (em ordem de segurança)
1. **Photoshop, sem IA (mais rápido e exato):** use a *Ferramenta Remover* ou o *Preenchimento sensível ao conteúdo* sobre as faixas e manchas cinza, sem passar nas lâminas pretas. O Bege Bahia em volta se repete sozinho.
2. **Photoshop, com Preenchimento generativo:**
   - selecione só as faixas e manchas cinza à esquerda da linha dos brises, sem as lâminas pretas;
   - use o **prompt 1**. Só a seleção muda.
3. **Higgsfield, com Nano Banana 2 em inpaint:**
   - envie o render aprovado;
   - envie uma máscara branca sobre as faixas e manchas cinza e preta no resto;
   - use o **prompt 1**.
4. **Nano Banana Pro, sem máscara (prompt 2):** dá para usar, mas o motor redesenha a imagem inteira. Pode mexer em outros pisos, como já aconteceu na v25. Confira a imagem inteira antes de aprovar.

---

## Prompt 1 — com máscara (Photoshop Preenchimento generativo ou Nano Banana 2 inpaint)

**PT (validação):** piso de mármore Bege Bahia visto de cima, continuando sem emenda o piso em volta: pedra bege-creme quente com manchas suaves em nuvem e pontinhos finos, fosca, com juntas retas e finas. Luz chapada e uniforme, sem sombras; vista de cima; sem objetos e sem texto.

```
Bege Bahia marble paving seen from directly above, continuing seamlessly the surrounding paving: warm cream-beige stone with soft cloudy tones and fine speckles, matte, with fine straight slab joints. Flat, even, shadowless light; strict top-down view; no objects, no shadows, no text.
```

## Prompt 2 — sem máscara (Nano Banana Pro, 2K, 16:9, uma imagem: o render aprovado)

**PT (validação):** edite esta imagem e mude só a faixa de piso Bege Bahia à esquerda da fileira de brises, na borda esquerda do lounge do gourmet.
- **Remova:** as faixas cinza diagonais e esfumadas ao lado de cada lâmina, que parecem sombras ou cópias fantasmas, e as manchas cinza nos pivôs.
- **No lugar delas:** continue o mesmo mármore Bege Bahia creme, com as juntas das placas.
- **Mantenha as lâminas:** as 7 lâminas pretas exatamente como estão (posição, ângulo, comprimento e espessura), com a linha fina em que giram.
- **Mantenha o resto:** todo o restante da imagem fica exatamente igual, incluindo enquadramento, escala, paredes, vidros, pisos, móveis, jardins, cores e texturas.
- Sem sombras e sem texto.

```
Edit this image. Change only the strip of Bege Bahia paving just left of the row of seven black brise blades on the left edge of the gourmet lounge: remove the soft grey diagonal streaks beside each blade (shadow-like ghost copies of the blades) and the grey blobs around the blade pivots, and continue the same warm cream-beige Bege Bahia marble slabs, with their fine joints, in their place. Keep the seven black brise blades exactly as they are — same position, angle, length and thickness — together with the thin straight line they pivot on. Keep everything else in the image exactly the same: framing, scale, every wall, glass line, floor, furniture piece, garden, colour and texture. No shadows, no text.
```

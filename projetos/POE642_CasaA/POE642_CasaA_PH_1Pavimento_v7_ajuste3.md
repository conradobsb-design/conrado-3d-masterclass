# POE 642 · Casa A · 1º Pavimento — ajuste 3 sobre o render da v7 (duas imagens)
_14/10/2026. Refaz o `v7_ajuste2`, que ficou grosseiro. Motor: Nano Banana Pro, 2K, 16:9._

**Imagens de entrada, nesta ordem:**
1. **Imagem 1, a editar:** o render do `v7_ajuste`, o que já estava sem a suíte inventada. Use o arquivo original e **não** o resultado do ajuste 2, para não acumular perda de qualidade.
2. **Imagem 2, só referência de posição:** `bases/POE642_CasaA_BASE_1Pavimento_v3_16x9.png`.

**Do ajuste 2 para o ajuste 3:**
- **Chuveiros de teto:** o texto pedia placas de aço com grade de furos, e o motor tende a desenhar isso como peça grande, pesada e brilhante. Agora o pedido é de um desenho fino e discreto, no mesmo traço refinado das bacias e cubas da imagem 1.
  - quadrado pequeno, de ~30 cm, menor que a bacia;
  - contorno fino prata-claro, face cinza bem clara e poucos furinhos minúsculos;
  - sem borda grossa, volume, brilho nem sombra.
- **Resto da imagem:** o prompt manda manter a nitidez e o detalhe da imagem 1 e não suavizar nem redesenhar nada fora dos chuveiros.
- **Imagem 2:** o prompt repete que dela vêm só a posição e o tamanho das placas, nunca o estilo.

**Se ainda sair grosseiro:** são só três peças pequenas. No Photoshop, o resultado é mais limpo:
- apague as placas e as duchas erradas com a *Ferramenta Remover*;
- desenhe um quadrado de ~30 cm em cada posição da base, com contorno fino cinza-prata (#B8B8B8, 1 px) e face cinza-clara (#E6E6E6), e acrescente uma grade de pontinhos se quiser.

## Versão de validação (PT, só para leitura)

**Duas imagens:**
- **Imagem 1:** a planta humanizada pronta, que é a imagem a editar.
- **Imagem 2:** a planta técnica do mesmo pavimento. Serve **só** para mostrar onde ficam os chuveiros de teto e qual é o tamanho deles. Não copie dela cores, pisos, linhas nem estilo.

Edite a imagem 1 e mantenha tudo exatamente igual, com a mesma nitidez e o mesmo detalhe fino: enquadramento, escala, cada parede, vidro, porta, escada, móvel, louça, piso, cor e textura. Não suavize, não engrosse e não redesenhe nada fora dos chuveiros de teto do banho 3 e do banho master.

Na imagem 2, os chuveiros de teto são as placas quadradas cinza com borda escura. Há três: uma no banho 3 e duas no banho master. Na imagem 1, cada uma vira um desenho fino e discreto, no mesmo traço refinado das bacias e cubas da imagem 1:
- um quadrado pequeno, de ~30 cm, menor que a bacia;
- contorno fino prata-claro e face cinza bem clara, com poucos furinhos minúsculos;
- sem borda grossa, sem volume, sem brilho e sem sombra;
- sem braço e sem ligação com a parede.

1. **Banho master:** é o banho embaixo à esquerda.
   - remova qualquer placa ou ducha que esteja fora do lugar, como em cima da banheira ou no meio do piso. A banheira fica inteira à vista, e o piso fica de travertino liso;
   - remova a ducha redonda com braço da área de banho, embaixo à esquerda;
   - coloque **duas** placas finas exatamente onde estão as duas placas cinza da imagem 2: dentro da área de banho, embaixo à esquerda, abaixo do box de vidro, lado a lado;
   - os dois misturadores pequenos na parede de baixo ficam.
2. **Banho 3:** é o banho da ponta direita da faixa de cima.
   - remova qualquer placa fora do lugar, como a da frente da bacia, perto da porta. O piso ali fica de travertino liso;
   - remova a ducha redonda com braço da área de banho, à direita;
   - coloque **uma** placa fina exatamente onde está a placa cinza da imagem 2: no centro da área de banho, à direita do box de vidro, longe das paredes.
3. **Os outros chuveiros** ficam exatamente como estão na imagem 1: os de parede dos banhos 1, 2 e de serviço.

Vista de cima, sem objetos novos e sem texto.

## Prompt para o motor (EN, colar inteiro)

```
Two input images. Image 1 is the finished humanized floor plan — the image to edit. Image 2 is the technical base plan of the same floor, used ONLY as a reference for where the ceiling showers are and how big they are; do not copy its flat colours, floors, lines or style.

Edit image 1. Keep everything exactly the same, with the same sharpness and fine detail — the framing, the scale and every wall, glass line, door, stair, piece of furniture, fixture, floor material, colour and texture. Do not soften, coarsen, thicken or redraw anything outside the ceiling showers of bathroom 3 and the master bathroom.

In image 2, the ceiling showers are the grey square plates with a dark rim — three in total: one in bathroom 3 and two in the master bathroom. In image 1, draw each one as a delicate, discreet top-view symbol in the same refined drawing style as the toilets and basins of image 1: a small square about 30 cm wide, smaller than a toilet, with a thin light-silver outline, a very pale grey face and a few tiny nozzle dots; no thick border, no bulky 3D metal, no glare, no shadow, no arm and no connection to any wall.

1. Master bathroom (bottom left): remove any shower plate or head that is out of place — over the bathtub or in the middle of the floor — so the bathtub is fully visible and the floor there is plain travertine. Remove the round shower head and its arm in the shower area at the bottom left. Place TWO of these delicate ceiling shower squares exactly where the two grey plates are in image 2: inside the shower area at the bottom left, below the glass screen, side by side. Keep the two small mixers on the bottom wall.

2. Bathroom 3 (the bathroom at the right end of the top band): remove any shower plate that is out of place — in front of the toilet near the door — so the floor there is plain travertine. Remove the round shower head and its arm in the shower area on the right. Place ONE delicate ceiling shower square exactly where the grey plate is in image 2: at the centre of the shower area, to the right of the glass screen, away from the walls.

3. All other showers stay exactly as they are in image 1: the wall showers in bathroom 1, bathroom 2 and the service bathroom.

Strict top-down view; no new objects; no text.
```

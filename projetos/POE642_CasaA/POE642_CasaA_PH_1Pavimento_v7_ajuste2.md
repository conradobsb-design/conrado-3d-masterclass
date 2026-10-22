# POE 642 · Casa A · 1º Pavimento — ajuste 2 sobre o render da v7 (duas imagens)
_14/10/2026. Edição sobre o render que saiu do `v7_ajuste`, já sem a suíte inventada. Motor: Nano Banana Pro, 2K, 16:9._

**Imagens de entrada, nesta ordem:**
1. **Imagem 1, a editar:** o render do `v7_ajuste`, em arquivo original.
2. **Imagem 2, só referência de posição:** `bases/POE642_CasaA_BASE_1Pavimento_v3_16x9.png`. Nela, os chuveiros de teto são as placas quadradas cinza com borda escura: uma no banho 3 e duas no banho master.

**O que está errado no render (e só isto muda):**
- **Banho master:**
  - as duas placas saíram enormes, com uns 60 cm, e no lugar errado: uma em cima da banheira e outra no meio do piso;
  - na área de banho, embaixo à esquerda, ficou uma ducha redonda.
- **Banho 3:**
  - a placa saiu enorme e na parte esquerda, na frente da bacia e perto da porta;
  - na área de banho, à direita, ficou a ducha redonda com braço saindo da parede de cima.
- **Chuveiros de parede:** os dos banhos 1, 2 e de serviço já estão certos e ficam como estão.

**Por que duas imagens:** só com texto, o motor erra a posição dos chuveiros de teto. Com a base junto, ele copia a posição e o tamanho das placas cinza. O prompt diz que a imagem 2 serve só para isso, para o motor não trazer as cores chapadas da base.

**Atenção:** o Nano Banana Pro não aceita máscara e redesenha a imagem inteira. Confira a imagem toda antes de aprovar.
- **Se outra coisa mudar, faça no Photoshop:**
  - apague as placas grandes e as duchas redondas com a *Ferramenta Remover*;
  - selecione um quadrado pequeno no lugar de cada placa cinza da base e use o *Preenchimento generativo* com "square ceiling rain shower plate, top view, brushed steel".

## Versão de validação (PT, só para leitura)

**Duas imagens:**
- **Imagem 1:** a planta humanizada pronta, que é a imagem a editar.
- **Imagem 2:** a planta técnica do mesmo pavimento. Serve **só** para mostrar onde ficam os chuveiros de teto e qual é o tamanho deles. Não copie dela cores, pisos, linhas nem estilo.

Edite a imagem 1 e mantenha tudo exatamente igual: enquadramento, escala, cada parede, vidro, porta, escada, móvel, louça, piso, cor e textura. Só os chuveiros de teto do banho 3 e do banho master mudam.

Na imagem 2, os chuveiros de teto são as **placas quadradas cinza com borda escura**. Há três: uma no banho 3 e duas no banho master. Visto de cima, o chuveiro de teto é uma placa quadrada pequena de aço escovado, rente ao teto, com uma grade fina de furinhos, sem braço e sem ligação com a parede. O tamanho é o da placa na imagem 2, de ~30 cm, mais ou menos a largura do assento de uma bacia.

1. **Banho master:** é o banho embaixo à esquerda.
   - remova as duas placas grandes com furinhos: a que está em cima da banheira e a do meio do piso. A banheira fica inteira à vista, e o piso fica de travertino liso ali;
   - remova a ducha redonda e o braço da área de banho, embaixo à esquerda;
   - coloque **duas** placas pequenas exatamente onde estão as duas placas cinza da imagem 2: dentro da área de banho, embaixo à esquerda, abaixo do box de vidro, lado a lado, uma na metade esquerda e outra na metade direita;
   - os dois misturadores pequenos na parede de baixo ficam.
2. **Banho 3:** é o banho da ponta direita da faixa de cima.
   - remova a placa grande com furinhos da parte esquerda do banho, na frente da bacia e perto da porta. O piso ali fica de travertino liso;
   - remova a ducha redonda e o braço que saem da parede de cima na área de banho, à direita;
   - coloque **uma** placa pequena exatamente onde está a placa cinza da imagem 2: no centro da área de banho, à direita do box de vidro, longe das paredes.
3. **Os outros chuveiros** ficam exatamente como estão na imagem 1: os de parede dos banhos 1, 2 e de serviço.

Vista de cima, sem objetos novos e sem texto.

## Prompt para o motor (EN, colar inteiro)

```
Two input images. Image 1 is the finished humanized floor plan — the image to edit. Image 2 is the technical base plan of the same floor, used ONLY as a reference for where the ceiling showers are and how big they are; do not copy its flat colours, floors, lines or style.

Edit image 1. Keep everything exactly the same — the framing, the scale and every wall, glass line, door, stair, piece of furniture, fixture, floor material, colour and texture — except for the ceiling showers of bathroom 3 and the master bathroom.

In image 2, the ceiling showers are the grey square plates with a dark rim — there are three: one in bathroom 3 and two in the master bathroom. Seen from above, a ceiling rain shower is a small square brushed-steel plate flush with the ceiling, with a fine grid of nozzle dots, no arm and no connection to any wall. Its size is the size of the grey plate in image 2 — about 30 cm, roughly the width of a toilet seat.

1. Master bathroom (bottom left): remove the two large dotted square plates — the one over the bathtub and the one in the middle of the floor — so the bathtub is fully visible and the floor there is plain travertine. Remove the round shower head and its arm in the shower area at the bottom left. Place TWO small ceiling shower plates exactly where the two grey plates are in image 2: inside the shower area at the bottom left, below the glass screen, side by side — one in its left half and one in its right half. Keep the two small mixers on the bottom wall.

2. Bathroom 3 (the bathroom at the right end of the top band): remove the large dotted square plate in the left part of the bathroom, in front of the toilet near the door, so the floor there is plain travertine. Remove the round shower head and the arm coming from the top wall in the shower area on the right. Place ONE small ceiling shower plate exactly where the grey plate is in image 2: at the centre of the shower area, to the right of the glass screen, away from the walls.

3. All other showers stay exactly as they are in image 1: the wall showers in bathroom 1, bathroom 2 and the service bathroom.

Strict top-down view; no new objects; no text.
```

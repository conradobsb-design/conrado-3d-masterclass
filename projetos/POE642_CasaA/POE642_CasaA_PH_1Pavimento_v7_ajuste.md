# POE 642 · Casa A · 1º Pavimento — ajuste sobre o render da v7
_14/10/2026. Edição sobre o render da v7, que ficou bem próximo. Motor: Nano Banana Pro, 2K, 16:9. Uma única imagem: o render, em arquivo original._

**O que muda (e só isto):**
1. **Suíte inventada:** o motor criou uma suíte na área à direita da circulação, acima do hall da escada. Ela tem quarto, cama, bancada, armário, closet e banho, e uma faixa de piso em cima. Nada disso existe.
   - **Por que aconteceu:** na base, essa área fica fora da casa. Ela fica entre a parede direita da circulação e a parede de cima do hall da escada, e o motor leu isso como um cômodo.
   - **Como fica:** fundo branco, como a área branca à direita do hall da escada.
   - **Fica como está:**
     - a parede direita da circulação, com as janelas de vidro;
     - a caixinha com X no canto de cima, depois do banho 3;
     - o hall da escada embaixo.
2. **Chuveiros de teto:** no banho 3 e no banho master, saíram duchas redondas presas à parede por um braço. Elas viram placas quadradas de teto, de aço escovado, com furinhos em grade, sem braço e sem ligação com a parede.
   - **Banho 3:** uma placa no centro da área de banho, longe das paredes.
   - **Banho master:** duas placas lado a lado, no centro da área de banho, com os misturadores na parede de baixo.
   - **Ficam como estão:** os chuveiros de parede dos banhos 1, 2 e de serviço, que já estão certos.

**Atenção:** o Nano Banana Pro não aceita máscara e redesenha a imagem inteira. Confira a imagem toda antes de aprovar.
- **Se outra coisa mudar, faça no Photoshop:**
  - **Suíte:** selecione o retângulo da suíte inventada e use *Editar › Preencher › Branco*. Como ali é fundo branco, o resultado é exato.
  - **Chuveiros:** selecione só a ducha redonda e o braço e use o *Preenchimento generativo* com "square ceiling rain shower plate, top view, brushed steel".

## Versão de validação (PT, só para leitura)

Edite esta imagem e mantenha tudo exatamente igual: enquadramento, escala e cada parede, vidro, porta, escada, móvel, louça, piso, cor e textura. Só duas coisas mudam.

1. **Área à direita da circulação, acima do hall da escada:** fica no alto da planta, à direita. É limitada à esquerda pela parede direita da circulação e embaixo pela parede de cima do hall da escada.
   - Ali foi desenhado um bloco que não existe: um quarto com cama, bancada e armário, um closet, um banho com bacia e duas cubas, e uma faixa de piso em cima.
   - Apague esse bloco por inteiro, com paredes, pisos, móveis, portas e louças, e deixe ali o fundo branco puro, igual à área branca à direita do hall da escada.
   - Mantenha exatamente como estão:
     - a parede direita da circulação, com as janelas de vidro;
     - a caixinha com X no canto de cima, depois do banho 3;
     - o hall da escada embaixo.
2. **Chuveiros de teto:** visto de cima, o chuveiro de teto é uma placa quadrada rente ao teto, sem braço e sem ligação com nenhuma parede.
   - **Banho 3:** é o banho da ponta direita da faixa de cima, e a área de banho é a parte direita dele, atrás do box de vidro.
     - remova a ducha redonda e o braço que saem da parede de cima;
     - no **centro da área de banho**, longe das paredes, coloque **uma** placa quadrada de aço escovado, de ~30 cm, com uma grade fina de furinhos.
   - **Banho master:** é o banho embaixo à esquerda, e a área de banho é a parte de baixo à esquerda dele, abaixo do box de vidro.
     - remova as duchas redondas e os braços;
     - coloque **duas** placas quadradas iguais de aço escovado, de ~30 cm, com grade fina de furinhos, lado a lado no centro da área de banho, uma na metade esquerda e outra na metade direita;
     - mantenha os dois misturadores pequenos na parede de baixo.
   - **Os outros chuveiros** ficam exatamente como estão: o de parede do banho 1, o do banho 2 e o do banho de serviço.

Vista de cima, sem objetos novos e sem texto.

## Prompt para o motor (EN, colar inteiro)

```
Edit this image. Keep everything exactly the same — the framing, the scale and every wall, glass line, door, stair, piece of furniture, fixture, floor material, colour and texture — except for these two changes:

1. Top-right area of the plan, to the right of the circulation corridor and above the stair hall — bounded on its left by the corridor's right wall and at the bottom by the top wall of the stair hall: a block was drawn there that does not exist — a bedroom with a bed, desk and wardrobe, a closet, a bathroom with a toilet and two basins, and a strip of paving above them. Erase that whole block completely — its walls, floors, furniture, doors and fixtures — and leave pure white background there, the same as the white area to the right of the stair hall. Keep exactly as they are: the corridor's right wall with its glass windows, the small box with the X at the top of that area beyond bathroom 3, and the stair hall below.

2. Ceiling showers. Seen from above, a ceiling rain shower is a flat square plate flush with the ceiling, with no arm and no connection to any wall.
- Bathroom 3 — the bathroom at the right end of the top band; its shower area is its right part, behind the glass screen: remove the round shower head and the arm coming from the top wall, and at the centre of the shower area, away from the walls, place ONE square brushed-steel ceiling rain shower plate, about 30 cm, with a fine grid of nozzle dots.
- Master bathroom — the bathroom at the bottom left; its shower area is its bottom-left part, below the glass screen: remove the round shower heads and arms, and place TWO identical square brushed-steel ceiling rain shower plates, about 30 cm, with a fine grid of nozzle dots, side by side at the centre of the shower area — one in its left half and one in its right half; keep the two small mixers on the bottom wall.
- All other showers stay exactly as they are: the wall showers in bathroom 1, bathroom 2 and the service bathroom.

Strict top-down view; no new objects; no text.
```

# POE 642 · Regras de representação (todas as casas)

_Consolidado em 19/10/26, antes de começar as execuções. Este arquivo vale mais que o histórico (`POE642_HANDOFF_SESSAO_LOCAL.md`): quando uma regra daqui contradiz uma decisão antiga, vale a daqui. As regras novas de 19/10 estão marcadas com **[19/10]**, e as que elas substituem estão na seção 15._

Pedido do usuário (19/10/26): "vamos consolidar todas as regras, antes de começar as execuções." Junto vieram 13 regras novas. Elas estão abaixo, cada uma no seu tema, com o número da lista do usuário (R1 a R13).

---

## 1. Fluxo de trabalho

- **Retoque local, sem IA.** Ajustes sobre um render aprovado são feitos com os scripts de retoque. Não se roda o motor de novo, porque ele não aceita máscara e redesenha tudo.
- **Um item por vez**, na ordem que o usuário escolher. Cada item entrega:
  - antes/depois;
  - camada só com os px alterados;
  - imagem final, prancha e PDF refeitos;
  - registro no handoff e no README;
  - commit.
- **Antes de retocar:** mapa numerado de erros, com a lista confirmada pelo usuário. A conferência é item a item contra o PDF.
- **Conferência:** na prancha, só a região do item pode mudar (diff).
- **O que não foi pedido fica como está** até o usuário pedir.
- **Sem IA para objetos decorativos:** o teste no Higgsfield foi rejeitado. Upscaler de IA só com autorização, porque gasta créditos.
- **Prompts (quando houver render novo):**
  - sempre completos, em PT (validação) + EN (motor);
  - cada versão é um `.md` novo;
  - nunca falar em "correções";
  - motor: Nano Banana Pro, i2i, 2K, 16:9, com uma única imagem de entrada (a base).
- **Bases e materiais:** sempre dos PDFs do cliente (`gerar_bases.py`) e com os materiais do cliente.

## 2. Escala e enquadramento

- **[19/10] R1. Textura sempre na escala real.** O PDF é 1:50:
  - planta de 2000 px: 31,45 px/m;
  - prancha de 3840 px: 60 px/m.
  - Cada textura da biblioteca (`_texturas/`) tem a largura real que cobre e é aplicada por `textura(nome, px_por_m, …)`, sem repetição visível.
- **Mesmo quadro em todos os pavimentos:** mesma escala e mesma posição. O elevador de um pavimento cai sobre o do outro. Nunca aproximar, recortar ou centralizar a planta. A final sai em 3840 × 2160.
- **Luz:** chapada, clara e uniforme. Todo objeto inserido leva uma sombra curta, com a luz do alto à direita (sombra para baixo e à esquerda). Sombras longas e duras de parede saem.

- **[21/10] Paredes pretas no contorno do PDF** (usuário: "revise todas as paredes e deixe-as em perfeito estado"): as paredes e os pilares são os preenchimentos da ARQ_PAREDE, em preto, com bordas retas e cantos nítidos, sem falhas dentro nem sobras para fora.

## 3. Materiais e texturas (biblioteca `_texturas/`)

- **Pedras: simular pedra, não porcelanato.**
  - Bege Bahia (placa de 0,60 m): "uniforme, quase liso, sem manchas"; o padrão é o Bege Bahia das varandas do 1º Pavimento da Casa A.
  - Travertino (1,20 m, veio horizontal).
  - Quartzito Aura (chapa de 3,00 × 1,95 m).
  - Pedra portuguesa (pedras de 6 a 8 cm), só no acesso de veículos. **[20/10]** No desenho e no tom da foto de referência (`_texturas/originais/pedra_portuguesa.webp`): assentada em leque, com juntas claras de areia, em bege, cinza e rosado (usuário: "opção 1, tom da foto"; substitui o caramelo). Na escala da planta é desenhada por código (`texturas_escala.pedra_portuguesa_leque`), porque a foto ampliada perde o leque.
  - Granito marrom (mais liso e menos escuro que a foto, sem excesso de pontos claros). **[20/10]** Sem os pontos brancos grandes do motor ("opção B, sem pontos os grandes brancos") e sem a grade de manchas repetida. **Desenho e tom da referência do usuário** ("use essa referencia de granito marrom"): base marrom quente (RGB ~118, 89, 69) com nuvens suaves e lascas de agregado de vários tamanhos, em tons de marrom, creme, cinza e quase preto (`fontes_procedurais.granito_referencia`; a foto veio só na conversa, e o desenho foi reproduzido por código).
- **[19/10] R4. Madeira e grama na escala da referência**, com textura: `referencia_planta.webp`, medida em 26 px/m.
  - Madeira de deck: réguas de ~15 cm. **[21/10] Medida de novo (FFT da foto): ~20 cm** (5,12 px a 26 px/m; os ~15 cm vinham de uma conta errada). Vale a régua da referência, como diz a R4.
  - Vinílico: réguas de ~20 cm, claras, em tons alternados.
  - Grama: verde médio com manchas suaves de 0,5 a 1 m.
  - A madeira nunca é laranja.
- **Pisos contínuos:** sem rejuntes nem juntas marcadas.
- **Legenda de cores das bases (entre casas):**

  | Cor da base | Material |
  |---|---|
  | oliva | travertino |
  | laranja | vinílico |
  | malva/terracota | granito marrom (exceção: Subsolo da Casa B, onde é Bege Bahia) |
  | cinza-claro | Bege Bahia (banhos, varandas, área externa, pisantes) |
  | listrado | deck de madeira |

- **Bancadas:** em quartzo claro com desenho de pedra (gourmet e cozinha), nunca madeira.
  - **[21/10] Casa A: ilhas e bancadas em quartzito Carrara** (usuário: "use o quartzito Carrara nas ilhas e bancadas"): branco levemente acinzentado com veios cinza esfumados, na escala, em todas as peças da ARQ_BANCADAS (gourmet, cozinha, lavabo, lavatório, banhos), com cubas, torneiras, inox e cooktops por cima.
- **Bancos de sauna:** na pedra do próprio piso, com linha fina e sombra discreta entre os níveis.

## 4. Portas, janelas, vidros e soleiras

- **[19/10] R3. Nunca mostrar o arco da porta.**
  - Porta de giro: só a folha (branca, fina, na espessura do PDF, com contorno fino) e o batente.
  - Porta camarão: só as folhas em zigue-zague, sem o setor pintado.
- **Porta de correr** (referência de 19/10): caixilho em faixa branca de 5 cm com contorno cinza, folhas em duas linhas sobrepostas e batentes em quadradinhos brancos. Portas de vidro de correr em dois planos, como no PDF.
- **Pivotante:** a folha até a ponta do PDF, passando para o outro hall.
- **Vidros e janelas finos e elegantes:**
  - vidro claro (nunca preto nem azul) com linha central fina;
  - caixilho de alumínio;
  - peitoril em pedra;
  - retornos da parede em preto.
- **Guarda-corpo de vidro fino** nos vazios.
- **[19/10] R13. Soleiras:** representar onde o PDF tem, e não acrescentar onde não tem. As soleiras já desenhadas precisam ser conferidas contra o PDF (seção 16).
  - **Como ler no PDF:** a soleira é o vão da porta na espessura da parede deixado em branco, entre os batentes. Onde o piso de um dos lados atravessa o vão, não há soleira.
  - **Como desenhar:** Bege Bahia na escala, com as duas faces da parede em traço cinza fino (Casa E, Subsolo).
- **Portões de correr** da área descoberta em alumínio. A porta do elevador em inox, com soleira em inox escovado.

## 5. Escadas

- **[19/10] Escadas com linhas.**
  - Em cada bocel, uma linha cinza suave e uma sombra de ~10 cm no degrau de baixo.
  - Nenhum traço preto.
  - Número de degraus igual ao PDF.
- **[19/10] R14. Triângulo de orientação no início da escada,** indicando o sentido, ora subida ora descida, conforme o pavimento. Usuário: "precisamos do triangulo como símbolo de orientação no inicio de escadas, indicando o sentido ora subida ora descida, a depender da situação".
  - Cheio, cinza-escuro, de 24 × 26 cm, no meio da largura e a 10 cm do início.
  - A ponta segue o sentido do percurso de quem chega por aquele pavimento.
  - Subida: no 1º degrau, apontando para cima. Descida: no topo, apontando para baixo.
  - Substitui a seta. Fica sem texto.
- **Escada que passa de pavimento:** cheia até a linha de corte do PDF e esmaecida depois, com os bocéis pontilhados (a projeção) e o corrimão fino. A linha de corte não é desenhada. Na caracol, só o trecho do pavimento fica cheio.
- Função: `_texturas/elementos.py` → `escada(..., triangulo="sobe" | "desce")`.

## 6. Banhos

- **Box em vidro fino:**
  - folha contínua, como no PDF;
  - piso contínuo;
  - o vidro como linha fina clara com sombra cinza ao lado;
  - no box de correr, duas folhas finas desencontradas.
- **[19/10] R10.** Folha contínua também no 1º Pavimento da Casa E, onde o box está incompleto.
- **[21/10] Boxes de correr com as folhas contínuas** (usuário: "boxes dos chuveiros com folhas contínuas"): as duas folhas do PDF inteiras, de parede a parede como no PDF, sem falhas nem trechos escuros, com a sombra fina ao lado; no vão de passagem, o trilho em tracejado cinza fino até a parede, como no PDF.
- **Chuveiro:** cada banho com o tipo e a parede do PDF.
  - Teto: placa quadrada de ~30 cm, ou disco cinza a ~35 cm da parede.
  - Parede: ducha quadrada de ~20 cm com braço cromado e canopla.
- **Vaso sanitário:** branco, com volume, contorno fino, sombra curta e tampo fechado (suspenso, quando o PDF indica).
- **Cuba e torneira:** na posição, no tamanho e do lado do PDF.
- **Área molhada da bancada:** demarcada em traço cinza fino.
- **Banheira:** com a torneira de piso, quando o PDF tem.

## 7. Cozinha, serviço e marcenaria

- **Eletrodomésticos e máquinas em inox.** Leitura do PDF:
  - quadrado sem diagonal = eletrodoméstico;
  - quadrado com diagonal = armário até o teto.
- **Cooktop:** com as bocas do PDF. **Tanques:** louça branca com torneira.
- **Armário até o teto:** marcenaria areia com veio, sem a diagonal e sem sombra de móvel baixo. Louceiro com veio aparente.
- **[19/10] R11. Guarda-roupa com cabides** (referência de 19/10):
  - visto de cima, aberto;
  - moldura branca fina com contorno cinza;
  - miolo cinza-claro, mais escuro junto às portas;
  - cabides em traços cinza a cada ~12 cm, com pequenas diferenças, como roupas.
  - Função: `elementos.py` → `guarda_roupa`.
- **Adega:** prateleira de vinhos, não armário.

## 8. Quartos e mobiliário

- **Nada inventado:** só o que o PDF tem ("Nothing is added"). Sai o que o motor inventa.
- **Camas:** no comprimento do PDF.
- **Banco no pé da cama:** estofado bege, com textura de estofado.
- **Roupa de cama, como mais uma opção (ainda não aplicar):**
  - Referência: `_texturas/originais/referencia_elementos_superior.png` e linha 5 da `cartela_elementos.jpg`.
  - Cama de casal:
    - lençol e edredom brancos;
    - manta bordô atravessada na metade dos pés;
    - travesseiros bordô na frente dos cinza-claros;
    - criados redondos de madeira com abajur branco.
  - Cama de solteiro: faixa bordô atravessada sobre o edredom branco.
- **Tapetes:** só onde o PDF tem, no contorno do PDF. Área de estar não vira jantar. Arranjos e vasos só onde o PDF indica.
- **Cortinas:** em linho off-white, traço fino. O bloco é o de `_blocos/blocos.py` (`cortina`), aprovado em 20/10.
  - **[20/10] Trilho de fora a fora:** sempre de parede a parede. Só o pano muda: a meia distância (como no PDF), todo recolhido ou todo fechado. Usuário: "trilhos da cortina tem que ser de fora a fora. somente a cortina pode estar a meia distancia, totalmente recolhida ou totalmente fechada".

## 9. Estrutura, projeções e brises

- **[19/10] R8. Destacar os pilares e as projeções.**
  - Pilares em preto, como as paredes, na geometria do PDF (EST - Pilar).
  - Projeções (DOC_LINHAS E PROJEÇÕES, cobertura, claraboia, shaft com X, áreas descobertas) em tracejado bem visível.
  - Exemplo do usuário: na Casa A faltaram as projeções dos brises.
- **[19/10] R9. Brises com as projeções de cobertura:** junto dos brises, o tracejado da projeção da cobertura (beiral ou laje), na posição do PDF e por cima. Escolha do usuário em 19/10: "tracejado da cobertura".
- **Brises:** na cor pedida para cada fachada:
  - Casa E: madeira no Térreo, bronze no 1º Pavimento;
  - Casa E 1º Pavimento, fachada das suítes em três camadas: cortina, porta de vidro de correr e brise na face externa.
- **Vazios (pé-direito duplo):** brancos, com o X em cinza médio.

## 10. Área externa

- **Vegetação:** só dentro do lote e fora dos pisos, decks e piscina.
  - Árvores, arbustos e palmeiras da biblioteca (`_texturas/vegetacao/`), no tamanho real, com a sombra.
  - Canteiros com touceiras.
  - Jardim de inverno com as plantas saindo levemente da floreira.
- **Grama:** a da referência, na escala (R4).
- **Piscinas:**
  - revestimento Barlavento (Portobello, 14,5 cm, Caribbean), luz chapada, só a sombra curta das bordas;
  - sem bordas ou vidros inventados;
  - degraus, prainha e spa como no PDF;
  - a borda em pedra conforme a casa.
- **[19/10] R12. Carros:** em todas as plantas, alinhados, do mesmo tamanho e na mesma cor, **prata**. O tamanho é um carro de 4,70 × 1,85 m, igual nas cinco casas (cor e tamanho aceitos pelo usuário em 19/10). A quantidade segue o PDF.
  - **[20/10] Casa E Térreo:** os três carros passam ao modelo da foto do usuário, um SUV visto de cima ("para os três carros, adote esse modelo"), os três em **bronze**, como na foto ("Bronze"). Continuam alinhados e do mesmo tamanho. Só na Casa E ("só para a Casa E"): as Casas A a D seguem com os carros prata. A foto chegou só como imagem na conversa e aguarda o arquivo para entrar na biblioteca.
  - **[21/10] Cancelado:** "Mantenha os carros. Não vamos alterar mais." A Casa E fica com os carros prata, alinhados e iguais (R12), como estão.
- **Lote:** linhas tracejadas do lote nas posições do PDF; nada do motor fora do lote; fundo branco fora do terreno; curvas de nível ocultas.

## 11. Pavimentos

- **[19/10] R2. Subsolo:** mostrar só o subsolo, com o restante do terreno hachurado.
  - Sai o contexto do Térreo (esmaecido ou em linhas) em volta do subsolo.
  - **Hachura:** linhas diagonais finas a 45°, em cinza-claro, sobre o branco, dentro do lote (escolha do usuário em 19/10).
  - **Como é feito:** a cada 0,40 m, traço de 1,3 px, cinza 198, com o contorno do lote em cinza fino. O lote é o do Térreo aprovado no mesmo quadro. Referência: Casa E, `retoque_subsolo_casae.contexto_hachura`.
- **1º Pavimento:** o Térreo "nublado" em volta (padrão, referência de 19/10).
  - `entorno_esmaecido.py --nublado`: 70% de branco, 80% da saturação, desfoque leve.
  - O Térreo usado é o aprovado, sem passar pelo motor.
  - O 1º Pavimento entra por cima, integralmente.
- **Térreo:** a planta inteira em cor cheia, com o entorno do lote.

## 12. Rótulos (nome e área do ambiente)

- **Texto:** o texto e a quebra do PDF ("SUÍTE 1 / A: 17 m²"), na posição do PDF.
- **Fonte:** Inter Regular, no corpo do PDF × 1,3 (ambiente estreito: 0,8 a 1,0×).
- **[20/10] "m²":** o "2" sobrescrito fica logo depois do "m", com a mesma folga pequena em todos os rótulos (7% do corpo), na altura do PDF. Antes ele ficava na posição do PDF e, com a Inter, encostava no "m" ou se afastava, conforme a largura dos números.
- **Cor:** preta sobre os pisos.
  - **[19/10] R6.** Branca sobre o granito marrom.
  - Branca também sobre verde escuro (jardins).
- **[19/10] R7. Proibido rótulo sobre objeto** (banheira, cama, móvel, bancada, louça). O rótulo vai para o piso livre mais próximo. Exemplo do usuário: o "BANHO MASTER" sobre a banheira na Casa E.
- **Notas que não entram:** projeções de cobertura, floreira, muros e título da folha. Entram, quando pedido, o shaft e a claraboia.
- **Resolução:** os rótulos são escritos na final em 3840 px.
- **Todas as casas têm rótulos** (escolha do usuário em 19/10): as Casas B, C e D passam a ter nome e área, com as mesmas regras de A e E.

## 13. Pranchas e PDF

- **Prancha:** 3840 × 2600, no mesmo quadro.
- **Rodapé no padrão do carimbo:**
  - Inter;
  - norte da Casa A;
  - endereço "ML 10 – Conjunto 02, Lotes 17, Unidade X";
  - assinatura New Air / Render 3D / Projetos com IA / Conrado Cortez;
  - marca Paulo Octávio.
- **Quadro de áreas:** as do cliente; sem dado, "NÃO INFORMADO", sem total.
- **PDF:** A3 de largura, na ordem Subsolo, Térreo, 1º Pavimento. Opções para o cliente com sufixo; depois da escolha, regerar sem sufixo.

## 14. Casos específicos já pedidos (por casa)

- **[19/10] R5. Casa E · Térreo:** representar o box no banho gourmet (hoje não tem).
- **[19/10] R10. Casa E · 1º Pavimento:** completar o box, com folha contínua.
- **[19/10] R7. Casa E · 1º Pavimento:** o rótulo do banho master sai de cima da banheira.
- **[19/10] R8. Casa A:** faltam as projeções dos brises.

## 15. Regras substituídas (não usar mais)

| Antes | Agora |
|---|---|
| Arco das portas em cinza fino (160, 161, 160) sobre o granito, por toda parte | **Sem arco** (R3) |
| Escadas só com sombreamento, sem linhas | **Com linha suave no bocel** |
| Escada sem seta nem símbolo de sentido | **Triângulo de orientação no início** (R14) |
| Rótulo cinza (150) sobre o granito | **Branco** (R6) |
| Carros cada um numa cor, levemente desalinhados (Casas A, D e E) | **Alinhados, mesmo tamanho, mesma cor** (R12) |
| Subsolo com o Térreo em volta (esmaecido na Casa B; linhas do PDF do Térreo na Casa E; deck esmaecido na Casa A) | **Só o subsolo, terreno hachurado** (R2) |
| 1º Pavimento da Casa E em opções P&B e linhas | **Nublado** como padrão (os arquivos das opções ficam no histórico) |
| Madeira e grama do motor, fora de escala | **Texturas da referência, na escala** (R1, R4) |

## 16. O que muda nas entregas atuais (inventário, ainda sem executar)

O "x" marca o que cada regra exige em cada prancha já entregue.

| Prancha | Arcos (R3) | Escadas com linha e triângulo (R14) | Rótulos (R6, R7) | Carros (R12) | Subsolo hachurado (R2) | Texturas na escala (R1, R4) | Projeções e brises (R8, R9) | Soleiras (R13) | Outros |
|---|---|---|---|---|---|---|---|---|---|
| A · Subsolo | x | x | x | – | x | x | x | conferir | |
| A · Térreo | feito | x | x | x | – | x | x (brises) | conferir | itens 4, 6, 7 e 10 da conferência |
| A · 1º Pav | x | x | x | – | – | x | x | conferir | o Térreo nublado em volta (hoje é o do motor); guarda-roupas com cabides (R11); itens 1 a 7 da conferência |
| B · Subsolo | x | x | x (novos) | – | x | x | x | conferir | |
| B · Térreo | x | x | x (novos) | x | – | x | x | conferir | |
| C · Subsolo | x | x | x (novos) | – | x | x | x | conferir | |
| C · Térreo | x | x | x (novos) | x | – | x | x | conferir | |
| D · Subsolo | x | x | x (novos) | – | x | x | x | conferir | |
| D · Térreo | x | x | x (novos) | x | – | x | x | conferir | |
| E · Subsolo | x | x | x | – | x | x | x | conferir | |
| E · Térreo | x | x | x | x | – | x | x | conferir | box do banho gourmet (R5) |
| E · 1º Pav | x | x | x (banheira) | – | – | x | x | conferir | box com folha contínua (R10); guarda-roupas com cabides (R11); nublado vira a opção única |

"Novos": as Casas B, C e D ainda não têm nomes e áreas e passam a ter.

## 17. Decisões de 19/10 e ordem de execução

**Respondido pelo usuário em 19/10:**
- carros em prata, de 4,70 × 1,85 m;
- brises com o tracejado da projeção da cobertura;
- hachura do Subsolo em diagonais finas a 45°, cinza-claro;
- rótulos em todas as casas;
- triângulo de orientação no início das escadas.

**Em aberto:** a roupa de cama fica como opção, até o usuário decidir onde usar.

**Ordem de execução (usuário, 19/10):** Casa E, Casa A, Casa B, Casa C, Casa D.
- Dentro de cada casa, um item por vez, com antes/depois, prancha e PDF refeitos a cada item.

## 18. Ajustes de 20/10/26 (Casa E, Subsolo), valem para as outras casas

- **Bege Bahia:** segue a foto de referência na escala: desenho em nuvens visível, no contraste dela, e tom quente (RGB ~230, 211, 186). Substitui o "uniforme, quase liso, sem manchas".
- **Travertino:** quando a foto da biblioteca perde os veios na escala do render, usa-se o travertino aprovado da própria casa (o do Térreo), na mesma escala, com os veios visíveis.
- **Escadas:** o sentido (de onde sobe) é o que o usuário define, mesmo quando o PDF indica outro. O triângulo fica no 1º degrau de quem sobe, apontando para a subida. A parte viva fica desse lado; a parte esmaecida e tracejada, depois do corte.
- **Vidros em folha contínua:** sem montantes nem marcas no meio; só a folha com os perfis finos dos dois lados (os pontos escuros davam a impressão de várias folhas).

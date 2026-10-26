# POE 642 · Regras de representação (todas as casas)

_Consolidado em 19/10/26, antes de começar as execuções. Este arquivo vale mais que o histórico (`POE642_HANDOFF_SESSAO_LOCAL.md`): quando uma regra daqui contradiz uma decisão antiga, vale a daqui. As regras novas de 19/10 estão marcadas com **[19/10]**, e as que elas substituem estão na seção 15._

**[26/10] Especificações novas para todas as casas na seção 19.** Elas mudam o símbolo das escadas (S/D no lugar do triângulo da R14), a cor das paredes (cinza 80, resposta do usuário) e a dos pilares (preto). A aplicação vai planta por planta, com o OK do usuário em cada uma ("Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."; "vou aprovar planta por planta"). A primeira foi o Subsolo da Casa A (seção 19, "Aplicação").

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

- **[21/10] Atenção às escalas** (usuário, no pente fino da Casa B: "ATENÇÃO ÀS ESCALAS"). Em todo pente fino, as escalas são medidas primeiro e vêm no topo da lista:
  - o quadro: os px/m da prancha pelo PDF (~60 px/m em 3840 px) e o elevador de um pavimento sobre o do outro;
  - cada piso da prancha ao lado do da biblioteca na mesma escala (`texturas.textura`), com uma régua de 1 m;
  - a vegetação folha a folha, com a régua (costela-de-adão até ~0,9 m, por exemplo);
  - móveis, louças e carros sobre o contorno do PDF; os carros em 4,70 × 1,85 m (R12).

- **[22/10] Tudo desenhado na resolução da prancha** (usuário, na Casa B: "TEM MUITOS BORRÕES NA IMAGEM. MOBÍLIAS DESGASTADAS E MAL DESENHADAS. PRECISO QUE REVISE ITEM A ITEM E DEIXE A IMAGEM COM OS CONTORNOS PERFEITOS"): nada é desenhado em 2000 px e ampliado para 3840, porque a ampliação borra. Pisos, grama, árvores, móveis, louças, bancadas, peças da biblioteca, paredes, esquadrias, escadas e rótulos são redesenhados direto no quadro da prancha (~60 px/m), pelo PDF (que é vetor) e pela base chapada da legenda. As texturas são sempre reduzidas da amostra (nunca ampliadas) e não levam desfoque. Na Casa B: `final3840_casab.py`; na Casa C (usuário: "EM 3840 PX"), `final3840_casac.py`, o mesmo motor com os parâmetros da casa.

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
- **Pisos contínuos:** sem rejuntes nem juntas marcadas. **[21/10]** Nem pedaços delas: nenhum traço vertical (ou horizontal) que denotava junta, nem junto aos tracejados e aos móveis (usuário: "deixe a imagem limpa, sem esses traços que não representam nada").
- **[26/10] Contornos limpos na troca do piso** (usuário, no Térreo da Casa A: "faça uma limpeza em contornos. apareceram alguns erros em volta de pisos, bancadas, sanitários, cubas, etc."): o piso novo vai até a borda de cada peça, sem a folga que deixava um anel do piso antigo em volta dos móveis, das louças e das bancadas; a sombra das peças passa ao piso novo como luz; o px da borda (meio peça, meio piso) mistura os dois; nada do piso antigo fica solto (manchas rosadas, retângulos de peças que saíram, a moldura branca de pedra antiga em volta de uma cuba ou de uma bancada refeita, pontos escuros na divisa entre dois pisos). Esquadrias, portas e as peças cheias do PDF ficam inteiras.
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
  - **[26/10] Casa A, Térreo: gourmet e cozinha em granito marrom levemente escurecido** (usuário: "pedra da ilha em U da vanrada gourmet é marrom granito, igual ao piso. deixe-a levemente escurecida para distinguir do piso" e "as bancadas em pedra da cozinha também são no granito marrom, levemente escurecido"): a ilha em U do gourmet, a ilha e a bancada da pia da cozinha no granito do piso um pouco mais escuro, com a borda e a sombra curta; a área molhada rebaixada um tom abaixo; cubas de inox, torneiras e cooktops por cima. Substitui o Carrara nessas peças.
  - **[22/10] Casa B: pedra tom areia, humanizada** (usuário: "troque o cinza das bancadas pelo tom areia" e "preciso que as pedras estejam humanizadas"; antes, no mesmo dia, "esse Carrara não está bom. Vamos utilizar uma pedra fina e tom sóbrio" tinha levado a um quartzo cinza de grão miúdo, que saiu):
    - a foto do Bege Bahia da biblioteca (`_texturas/bege_bahia.jpg`, a placa real com as nuvens de 10 a 20 cm), na escala da prancha, com as nuvens um pouco mais calmas (80% do contraste) e levada ao tom areia (RGB ~233, 217, 198);
    - em toda peça da ARQ_BANCADAS: as brancas, as bege (a cuba esculpida e o banco da sauna do Subsolo) e os frisos escuros;
    - borda com volume leve (3 cm), o contorno fino do PDF em cinza quente e nada de desfoque (a pedra não borra);
    - por cima: cubas brancas (seção 6), torneiras, cooktops e banquetas.
- **Bancos de sauna:** na pedra do próprio piso, com linha fina e sombra discreta entre os níveis.
  - **[22/10] Casa B: em travertino** (usuário: "as pedras da sauna, em forma de bancos, são em travertine"): os dois níveis (o retângulo bege da ARQ_CONTRAPISO, 2,95 × 1,00 m) no travertino da biblioteca, no tom e na força de veio do piso da sauna; o nível de trás, junto à parede, um pouco mais claro; o espelho entre os níveis e a frente do banco em linha fina; sombra discreta no nível da frente, junto ao espelho. Não entram na pedra das bancadas.

## 4. Portas, janelas, vidros e soleiras

- **[19/10] R3. Nunca mostrar o arco da porta.**
  - Porta de giro: só a folha (branca, fina, na espessura do PDF, com contorno fino) e o batente.
  - [22/10] Nem resto do arco: onde ele estava, o piso segue limpo, sem pintas (usuário, na porta da suíte 3 da Casa B: "tem um erro nessa porta"). E a limpeza em volta da folha não copia o móvel vizinho para junto dela (lá, uma lasca do guarda-roupa sob a folha aberta).
  - [22/10] Todos os arcos do PDF, de qualquer tamanho e em qualquer camada: na Casa C, o da pivotante do hall tem 2,1 m de raio, e os das portas dos boxes dos banhos master estão na ARQ_BANCADAS.
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
  - **[22/10] Na resolução da prancha e nas faces das paredes** (usuário, na Casa B: "corrigir as soleiras"): a soleira é desenhada na final de 3840 px (nunca ampliada de 2000 px, que borrava), da ponta de uma parede à da outra e na espessura exata da parede do PDF (o desenho vetorial, a 8 x), nítida, com o Bege Bahia da biblioteca no tom da referência; as faces da parede em traço cinza fino; batentes e folhas por cima.
- **Portões de correr** da área descoberta em alumínio. A porta do elevador em inox, com soleira em inox escovado.

## 5. Escadas

- **[19/10] Escadas com linhas.**
  - Em cada bocel, uma linha cinza suave e uma sombra de ~10 cm no degrau de baixo.
  - Nenhum traço preto.
  - Número de degraus igual ao PDF.
- **[26/10] O triângulo da R14 dá lugar ao S/D** (seção 19), planta por planta com o OK do usuário: a letra S ou D do PDF em Inter SemiBold de ~17 px, cinza quase preto (45), na origem do texto do PDF. Aplicado no Subsolo da Casa A.
- **[26/10] Escadas humanizadas, sem linhas** (usuário, no Subsolo da Casa A: "a escada e seus degraus ainda estão representados de forma técnica, sem humanização. não precisa constar linhas, mas sim sombras denotando que o sentido é de subida"): os degraus na pedra deles (lá, Bege Bahia), sem os traços do PDF (nem degraus, nem contorno, nem linha de percurso, nem marca de corte, nem tracejado), marcados só pelo sombreamento das escadas aprovadas: cada degrau um pouco mais claro que o de baixo (de 0,84 a 1) e a sombra curta de cada espelho no degrau de baixo (e a do 1º degrau no piso). Depois do corte, o trecho esmaecido, como antes. Substitui os traços em cinza 85 que a primeira versão da E8 tinha posto.
- **[26/10] A descida para o pavimento de baixo, nas plantas de cima** (usuário, no 1º Pavimento da Casa A: "na descida da escada U é preciso saber onde ela fica nevoada, já no terreo. representando aquela linha em diagonal e enovoar a parte que pertence ao terreo"): a linha de corte do pavimento de baixo (a diagonal com a quebra em zigue-zague, do PDF dele) desenhada fina, em cinza escuro, de lado a lado do lance; os degraus até ela, que são do pavimento de baixo, entram nublados (o pavimento de baixo nublado, recortado pela mesma linha); depois dela, os degraus do pavimento, cheios, com o sombreamento.
- **[19/10] R14. Triângulo de orientação no início da escada,** indicando o sentido, ora subida ora descida, conforme o pavimento. Usuário: "precisamos do triangulo como símbolo de orientação no inicio de escadas, indicando o sentido ora subida ora descida, a depender da situação".
  - Cheio, cinza-escuro, de 24 × 26 cm, no meio da largura e a 10 cm do início.
  - A ponta segue o sentido do percurso de quem chega por aquele pavimento.
  - Subida: no 1º degrau, apontando para cima. Descida: no topo, apontando para baixo.
  - Substitui a seta. Fica sem texto.
- **[22/10] Casa B: degraus em Bege Bahia** (usuário: "e os degraus em pedra bege Bahia na lateral esquerda da imagem???"): as escadas externas da esquerda (a de 6 degraus, da pedra grande para a ducha, nos dois pavimentos, e a de 9, da varanda para o deck em L, no Térreo) nos degraus exatos do PDF (ARQ_ESCADAS E RAMPAS), na foto do Bege Bahia da biblioteca, no tom e no contraste dela, com as linhas e o triângulo por cima. Sem filtro de mediana sobre a pedra (borrava).
  - **[22/10] Degraus em blocos** (usuário, apontando a área à esquerda do deck: "aqui são degraus"): a pedra grande e as 6 lajes em volta dela são blocos de pedra sobrepostos em cascata no PDF (ARQ_CONTRAPISO), não um piso liso. Cada bloco é uma peça de Bege Bahia, como os degraus das escadas, e tem o próprio contorno em linha fina de bocel. O bloco que o PDF desenha por cima deixa a sombra curta (para baixo e à esquerda) no de baixo e na grama. O contorno de cada bloco é o do PDF, mesmo onde a legenda pintava outro material (o canto do deck sob a pedra grande). Onde os blocos descem como degrau, leva o triângulo da R14 no início, apontando para onde desce ("adicione o triângulo descendo nesse degrau").
- **Escada que passa de pavimento:** cheia até a linha de corte do PDF e esmaecida depois, com os bocéis pontilhados (a projeção) e o corrimão fino. A linha de corte não é desenhada. Na caracol, só o trecho do pavimento fica cheio.
- Função: `_texturas/elementos.py` → `escada(..., triangulo="sobe" | "desce")`.

## 6. Banhos

- **Box em vidro fino:**
  - folha contínua, como no PDF;
  - piso contínuo;
  - o vidro como linha fina clara com sombra cinza ao lado;
  - no box de correr, duas folhas finas desencontradas.
- **[19/10] R10.** Folha contínua também no 1º Pavimento da Casa E, onde o box está incompleto.
- **[22/10] Box no granito em cinza claro** (usuário, na Casa B: "preciso que os boxes dos banhos onde tem piso marrom granito em cinza claro. Tem que estar visível"): nos banhos de piso em granito marrom (BH serviço e BH motorista), o vidro do box é uma faixa cinza-clara contínua, de parede a parede, bem visível; nos pisos claros, o vidro fica como está. No PDF, o box é o grupo de 7 ou mais traços paralelos da ARQ_LOUÇAS E METAIS, de 0,75 m ou mais.
- **[21/10] Boxes de correr com as folhas contínuas** (usuário: "boxes dos chuveiros com folhas contínuas"): as duas folhas do PDF inteiras, de parede a parede como no PDF, sem falhas nem trechos escuros, com a sombra fina ao lado; no vão de passagem, o trilho em tracejado cinza fino até a parede, como no PDF.
- **Chuveiro:** cada banho com o tipo e a parede do PDF.
  - Teto: placa quadrada de ~30 cm, ou disco cinza a ~35 cm da parede.
  - Parede: ducha quadrada de ~20 cm com braço cromado e canopla.
- **Vaso sanitário:** branco, com volume, contorno fino, sombra curta e tampo fechado (suspenso, quando o PDF indica).
  - **[26/10] Casa A · Subsolo, banhos feminino e masculino:** vasos marrons ("Sanitarios em marrom, não branco") e cubas em granito marrom ("Cubas dos banhos de serviço em marrom granito"), com a bancada em travertino bruto. O banho de serviço segue com o vaso branco e a cuba branca na bancada de granito marrom.
  - **[26/10] Casa A · 1º Pavimento, banhos 1, 2, 3 e master** (usuário: "No banho 1 e 2 e 3 e master, a(s) cuba(s) é(são) em mármore travertino bruto e o sanitário branco."): a bancada em travertino bruto mais marcado que o piso (E9), a cuba esculpida no mesmo travertino bruto (a borda um pouco mais clara, a bacia mais funda com a sombra por dentro, o contorno no tom escurecido da pedra) e o vaso branco. **B. serviço** ("No banho serviço a cuba é branca, com bancada da pia em marrom granito e sanitário branco."): como o banho de serviço do Subsolo, a bancada em granito marrom no polígono do PDF, a cuba branca de semiencaixe e o vaso branco.
  - **[26/10] Casa B · Subsolo** (usuário: "banho sauna: sanitário marrom, cuba esculpida em mármore travertino bruto e e pedra da bancada da cuba em granito marrom; banho serviço: cuba branca, pedra da pia em marrom granito, sanitário branco."): **BH sauna**, as prateleiras de pedra em volta da cuba em granito marrom (o das Casas B a D), com a borda e a sombra curta (E9), a cuba esculpida em travertino bruto, clara (seção 19, Casa B · Subsolo) e o vaso marrom (a louça dos vasos marrons da Casa A, com a tampa e o volume); **BH serviço**, a bancada da pia em granito marrom, a cuba branca e o vaso branco.
  - **[26/10] Casa B · Térreo** (usuário: "lavabo: cuba esculpida e pedra da bancada da pia em marmore travertino bruto. Sanitário em marrom; banhos varanda gourmet: cubas esculpidas em marrom granito, pedra da bancada da pia em marmore travertino bruto, sanitários em marrom; banho 1, 2 e 3 e banho master - cuba e pedra da pia em marmore travertino bruto, sanitario branco"): as bancadas dos banhos, do lavabo e do lavatório gourmet em travertino bruto, mais marcado que o piso (com a borda e a sombra do E9); as cubas esculpidas em travertino bruto claro (como a do BH sauna do Subsolo aprovado), menos as duas do lavatório gourmet, esculpidas em granito marrom; os vasos do lavabo e dos dois BH gourmet marrons, os dos banhos 1, 2, 3 e master brancos.
  - **[22/10] Todos com a tampa** (usuário, na Casa B: "todos os sanitários precisam ter a sua respectiva tampa"): sem exceção, também onde o PDF desenha o vaso aberto (a abertura e o ralo à mostra). A tampa vai da linha da dobradiça, logo à frente dos parafusos, até a frente, recuada do contorno do vaso (fica o aro fino em volta), em louça branca com volume suave, o traço fino das louças e a sombra curta sobre o aro. Os vasos que já trazem a tampa no PDF levam a mesma, para ficarem iguais.
- **Cuba e torneira:** na posição, no tamanho e do lado do PDF.
  - **[22/10] Cubas em branco** (usuário, na Casa B: "melhore as representações de cubas, pias, tanques" e "cubas em branco"): todas as cubas em louça branca, também as da cozinha, do gourmet e do bar (antes em inox), e os tanques. A bacia tem cantos arredondados, recuada do aro, com a sombra interna do lado da luz (em cima e à direita); o aro duplo do PDF vira um contorno fino só; sombra curta na pedra. Torneiras, válvulas e ralos em metal.
  - **Como ler a cuba no PDF:** na ARQ_LOUÇAS E METAIS, os preenchimentos pequenos (as duas bordas encaixadas); na ARQ_BANCADAS, o retângulo com o aro fino (tiras de até 3,5 cm) encostado nos quatro lados. A peça de pedra entre duas cubas não tem aro em todos os lados e fica em pedra.
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
- **[22/10] Móveis pelo desenho do PDF** (Casa B, "MOBÍLIAS DESGASTADAS E MAL DESENHADAS"): cada peça das camadas ARQ_MOBILIÁRIO, ARQ_LAYOUT HUMANIZAÇÃO, ARQ_LOUÇAS E METAIS e ARQ - Marcenaria é redesenhada no contorno exato do PDF, na ordem de pintura dele (o que está por cima cobre o de baixo), com a cor do material tirada do render, volume suave junto à borda, veio na madeira, trama leve no tecido, o traço fino do PDF e a sombra curta. As peças da biblioteca (camas, guarda-roupas, cooktops, banquetas, cortinas, inox, adega, carros, plantas em vaso) vão por cima, no lugar do PDF.
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
- **[22/10] Móveis humanizados sem perder as características** (usuário, na Casa B, no estar da varanda gourmet: "vamos humanizar esses mobiliários, sem que eles percam as características"): a forma, a cor e o lugar de cada peça são os do PDF. Os estofados ganham volume de almofada e trama de tecido, o traço técnico fica leve e a madeira, com o veio.
- **[22/10] Cama da suíte com o cobre-leito e o banco** (usuário: "vamos representar melhor essa cama e seu cobre-leito. Está faltando o banco que está acima da cama"): a cama segue a silhueta do PDF, com o cobre-leito (matelassê, dobrado em rolo junto aos travesseiros e caindo dos lados como no PDF), os travesseiros, as almofadas e a peseira. Toda peça do PDF entra, mesmo em camada trocada (o banco estava na DOC_TEXTOS).
- **[22/10] Desenho sobre a mesa** (usuário: "preciso do desenho sobre a mesa"): o desenho do tampo do PDF (anel, painéis, peça de centro) aparece por cima da mesa, em linha fina nítida, nunca apagado como hachura.
- **[22/10] Sem marcações técnicas nos tampos** (usuário: "remova essas marcações técnicas sobre o tampo da mesa"): os cantos tracejados e as marcas de CAD sobre mesas e aparadores (no PDF da Casa B, os traços em laranja da ARQ_MOBILIÁRIO e as elipses no meio da mesa de jantar) não entram; o tampo fica liso, só com a madeira. O desenho do tampo que é do móvel (como o da mesa redonda do hall) fica.
- **[22/10] Linhas dos móveis junto às esquadrias** (usuário, no sofá junto às portas de correr do jardim de inverno: "a linha da direita não existe"): a limpeza dos vidros não pode copiar a borda de um móvel vizinho nem esticar as linhas dele até a porta; o móvel termina onde o PDF termina, e entre ele e a porta fica o piso.
- **[22/10] Banquetas sob o tampo** (usuário, na Casa B: "as banquetas devem aparecer parcialmente, atrás da bancada"): nas ilhas e bancadas com banquetas, a pedra cobre a parte da banqueta que fica sob o tampo (aparecem o encosto e a frente do assento); a sombra da banqueta não cai sobre a pedra.
- **Tapetes:** só onde o PDF tem, no contorno do PDF. Área de estar não vira jantar. Arranjos e vasos só onde o PDF indica.
- **Cortinas:** em linho off-white, traço fino. O bloco é o de `_blocos/blocos.py` (`cortina`), aprovado em 20/10.
  - **[20/10] Trilho de fora a fora:** sempre de parede a parede. Só o pano muda: a meia distância (como no PDF), todo recolhido ou todo fechado. Usuário: "trilhos da cortina tem que ser de fora a fora. somente a cortina pode estar a meia distancia, totalmente recolhida ou totalmente fechada".
  - **[22/10] Um pano só por janela** (usuário, na Casa B: "corrija a cortina que está duplicada"): a cortina entra depois das esquadrias. A limpeza das esquadrias espelha o piso de junto do vidro e copiava a cortina desenhada antes dela. Antes do espelho, as ondinhas do PDF que marcam o pano saem do piso, para não voltarem em segunda fileira.

## 9. Estrutura, projeções e brises

- **[19/10] R8. Destacar os pilares e as projeções.**
  - Pilares em preto, como as paredes, na geometria do PDF (EST - Pilar).
  - **[22/10] Pilares redondos em cinza** (usuário, na Casa B: "existem dois pilares representados por bolas. Precisamos deixar em cinza para destacá-los"): cinza médio (RGB ~130, 128, 128) com o contorno escuro fino. Os retangulares seguem pretos.
  - Projeções (DOC_LINHAS E PROJEÇÕES, cobertura, claraboia, shaft com X, áreas descobertas) em tracejado bem visível.
  - **[26/10] Tracejado preto ou branco pelo fundo** (usuário, no Térreo da Casa A: "a projeção em tracejado precisa ficar evidente. Em fundos escuros, faça a projeção com tom branco; para tons claros, marque-as com tom preto tracejado"): os traços do próprio PDF, redesenhados nítidos (~1,5 px) por cima de tudo, cada traço em preto (RGB ~30) nos fundos claros ou em branco nos escuros (granito, grama), pela luminância do fundo em volta dele. Os afastamentos e os limites do lote não são projeção e ficam como estão.
  - **[26/10] Nas paredes, o tracejado some** (como no 1º Pavimento aprovado em 21/10): a projeção que corre junto a uma parede ou janela não é desenhada por cima dela. No Térreo da Casa B, a linha da cobertura do PDF que corre sobre o vidro da porta de correr do living sai; e o X do shaft abre embaixo do rótulo SHAFT, para o texto ficar legível.
  - Exemplo do usuário: na Casa A faltaram as projeções dos brises.
  - **[22/10] Procurar a cobertura também fora da DOC_LINHAS** (usuário, na Casa B: "e onde estão as projeções de cobertura?"): no PDF da Casa B, a cobertura da entrada (a pérgola entre o jardim do hall e a garagem) é um tracejado da ARQ_PAREDE (traços de 5,7 pt). Ela entra na final, nos traços do próprio PDF, em cinza escuro e fino.
- **[19/10] R9. Brises com as projeções de cobertura:** junto dos brises, o tracejado da projeção da cobertura (beiral ou laje), na posição do PDF e por cima. Escolha do usuário em 19/10: "tracejado da cobertura".
- **Brises:** na cor pedida para cada fachada:
  - Casa E: madeira no Térreo, bronze no 1º Pavimento;
  - Casa E 1º Pavimento, fachada das suítes em três camadas: cortina, porta de vidro de correr e brise na face externa.
- **Vazios (pé-direito duplo):** brancos, com o X em cinza médio.
- **[22/10] Guarda-corpo de vidro** (usuário, na Casa B: "faltou a representação do guarda-corpo em L da varanda em vidro"): todo guarda-corpo do PDF aparece, como os vidros das esquadrias (vidro claro, as duas faces em linha fina), com a sombra curta. Todas as lâminas, inclusive os fechamentos até a parede ("está faltando o fechamento desse guarda corpo no lado direito"), e as quinas fechadas, sem falha no vidro nem no piso junto a ele ("tem uma falha logo perto da dobra, na quina").
- **[22/10] Muro na sequência da porta de correr** (usuário: "na sequência das portas de correr, existe muro (em preto)"): o trecho fino que segue a porta de correr até o muro de divisa é muro, em preto.

## 10. Área externa

- **Vegetação:** só dentro do lote e fora dos pisos, decks e piscina.
  - Árvores, arbustos e palmeiras da biblioteca (`_texturas/vegetacao/`), no tamanho real, com a sombra.
  - Canteiros com touceiras.
  - Jardim de inverno com as plantas saindo levemente da floreira.
  - **[22/10] Jardins: só verde e travertino na borda** (usuário, na Casa B: "temos vidro em cima e embaixo e portas de vidro na lateral esquerda. Note que o piso em travertino está presente nas bordas. Sem cores quentes, apenas verde"; e "vamos melhorar as bordas do travertino [...] na parte de baixo do jardim, precisamos do travertino e os brises bem desenhados"): o canteiro não passa por cima de vidro, porta ou piso. No jardim de inverno não há moldura de travertino (usuário, 22/10: "não há essa moldura de travertino. É somente na lateral esquerda [...] temos as duas folhas de vidro de correr e depois travertino, já próximo ao braço do sofá e rente ao tapete"): o canteiro é a sala inteira, do vidro de cima (rente ao vinílico) ao vidro de baixo e da parede às folhas de correr; o travertino fica só do lado de fora das portas. No jardim do hall, o canteiro vai até a linha do travertino, com a borda limpa, e a faixa sob os brises é travertino. Só plantas verdes, sem flores nem folhagem creme, e o chão do canteiro verde-escuro, sem terra marrom à mostra. Os brises vão nítidos, em grafite, com a sombra curta.
- **Grama:** a da referência, na escala (R4).
- **[22/10] Casa B: banco em L do deck em bronze fosco** (usuário: "o banco em L do deck é em bronze fosco"): cor chapada de bronze (RGB ~104, 84, 62), escovado bem leve no sentido de cada braço, a quina do lado da luz um pouco mais clara e a do outro lado um pouco mais escura, contorno fino e sombra curta no deck. Não é madeira.
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
  - **[22/10] Preto ou branco pelo fundo, sem sombra** (usuário, na Casa B: "rótulos não podem ter sombra. Use a cor preta ou branca, a depender do fundo"): o texto é preto ou branco, o que contrastar mais com o fundo da caixa do rótulo (a luminância relativa, pela conta do WCAG: preto nos pisos claros, branco no granito, nos pisos escuros e nos jardins). Nada de halo, sombra ou caixa.
- **[19/10] R7. Proibido rótulo sobre objeto** (banheira, cama, móvel, bancada, louça). O rótulo vai para o piso livre mais próximo. Exemplo do usuário: o "BANHO MASTER" sobre a banheira na Casa E.
  - **[22/10] Como posicionar** (usuário, na Casa B: "melhore os rótulos e não os sobreponha os objetos" e "os rótulos devem estar dentro de seus respectivos ambientes"): a caixa exata do texto procura, em anéis de até 3 m em volta do ponto do PDF, o lugar livre mais perto, sem tocar móvel, tapete, louça, bancada, parede, esquadria, escada nem outro rótulo, e sempre dentro do seu ambiente. Onde não cabe, quebra em duas linhas e depois desce o corpo (0,85, 0,72, 0,62); o corpo cheio vale mais que a distância.
  - **[22/10] Nunca dentro do box** (usuário, na Casa B: "o rótulo do banho gourmet está sobre o chuveiro [...] não precisa ficar dentro do box"): o vidro do box divide o banho, e o lado do chuveiro (o da ducha do PDF) fica fora do ambiente do rótulo; o ponto do PDF que cai dentro do box passa ao piso seco mais perto do mesmo banho.
  - **[22/10] Nome abreviado quando pedido:** "BH. GOURMET" no lugar de "BANHO GOURMET" (Casa B), no centro do nome do PDF.
  - **O ambiente do rótulo:** as paredes do PDF (os preenchimentos escuros) com os vãos entre trechos de parede alinhados fechados até 2 m (as portas e as passagens sem porta, como a da circulação do Subsolo para a garagem); vidros, folhas de porta e boxes não dividem o ambiente. A região livre que tem mais de um ponto do PDF (as áreas abertas: living, hall, varanda) é repartida entre eles pela distância andando por dentro.
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
- **[22/10] Casa B · Térreo:** o rótulo da prainha fica abaixo das duas espreguiçadeiras (usuário: "o rótulo da prainha pode ficar abaixo das duas espreguiçadeiras").
- **[22/10] Casa C** (respostas do usuário aos mapas do pente fino: "1. BANCO EM BRONZE FOSCO; 2. OK; 3. DE ACORDO; 4. PEDRA AREIA; 5. EM 3840 PX"):
  - **Térreo:** o L junto ao deck é banco em bronze fosco, como o da Casa B (no PDF, a ARQ_PAISAGISMO desenha uma floreira).
  - **Subsolo (R2):** em cor cheia o Subsolo, o pátio, os degraus largos e o caminho (o cinza cheio do PDF do Subsolo); o resto do lote do Térreo final na hachura.
  - **Escadas (R14):** no Térreo, a estreita desce do deck (triângulo junto ao deck, apontando para a esquerda) e os degraus largos descem do caminho para o pátio (triângulo no degrau 10, apontando para cima); no Subsolo, os largos com o triângulo no degrau 1 (para baixo) e a estreita esmaecida com o triângulo no 11 (para a direita).
  - **Bancadas e ilhas** em pedra areia humanizada, com as cubas brancas, como na Casa B.
  - **Camas e bancos do render aprovado** (usuário: "PODE MANTER O JOGO DE CAMA QUE ESTAVA ANTES." e "MANTENHA OS BANCOS QUE ESTAVAM EM FRENTE AS CAMAS TAMBÉM"): na Casa C, as camas com a roupa de cama e os bancos ao pé delas ficam como no render aprovado de 14/10, sem a roupa de cama da biblioteca.
- **[22/10] Casa D** (respostas do usuário aos mapas do pente fino: "1. Igual ao das outras casas 2. Em Madeira 3. Sim, para os 3 4. Areia 5. Os do render 6. Hachura"):
  - **Granito igual ao das outras casas:** o tom e o desenho do granito de referência (o das Casas B e C, RGB ~118, 89, 69), não o Marrom Tabaco escuro da entrega de 14/10; vale também para o acesso de veículos.
  - **Brises em madeira** (os ripados do hall, da garagem, da suíte 3 e das fachadas de baixo), com o veio no sentido da ripa, o traço fino e a sombra curta.
  - **Escadas com o triângulo (R14), as três:** no Térreo, a de 16 degraus com o triângulo no degrau 16 (à direita), apontando para a esquerda; no Subsolo, cheia até o corte (degrau 7) e esmaecida depois, com o triângulo no degrau 1, apontando para a direita; os blocos em cascata à esquerda da piscina, com o triângulo apontando para a esquerda, para onde descem.
  - **Bancadas e ilhas** em pedra areia humanizada, com as cubas brancas, como nas Casas B e C.
  - **Camas e bancos do render aprovado**, como na Casa C.
  - **Subsolo (R2):** em cor cheia só o Subsolo e o pátio (o contorno da laje do Subsolo, EST_LAJE); a faixa verde entra na hachura com o resto do lote do Térreo final.
  - **[25/10] Na final em 3840 px** (`final3840_casad.py`): a vegetação do gramado só onde o render tinha plantas (os cantos da esquerda, junto à piscina e junto à suíte 3, sem árvores avançando no gramado); as cubas que o PDF desenha sem o aro (banho master, lavabo, WC DCE) também em louça branca; o estar da suíte 3 fica o do render (no PDF, o sofá e a mesa estão em camadas trocadas).

## 15. Regras substituídas (não usar mais)

| Antes | Agora |
|---|---|
| Arco das portas em cinza fino (160, 161, 160) sobre o granito, por toda parte | **Sem arco** (R3) |
| Escadas só com sombreamento, sem linhas | **Com linha suave no bocel** |
| Escada sem seta nem símbolo de sentido | **Triângulo de orientação no início** (R14) |
| Rótulo cinza (150) sobre o granito | **Branco** (R6) |
| Casa B: bancadas em pedra fina cinza de tom sóbrio (antes, Carrara) | **Pedra tom areia, humanizada** (Bege Bahia da biblioteca) |
| Cubas da cozinha, do gourmet e do bar em inox | **Todas as cubas em louça branca** |
| Pilares redondos em preto | **Em cinza, com o contorno fino** (os retangulares seguem pretos) |
| Rótulo com halo suave do tom do fundo | **Sem halo nem sombra; preto ou branco pelo fundo** |
| Casa B: bancos da sauna no material do render | **Travertino** (os dois níveis) |
| Casa B: degraus das escadas externas em travertino | **Bege Bahia** |
| Casa B: banco em L do deck em réguas de madeira | **Bronze fosco** |
| Box de vidro em cinza escuro sobre o granito | **Cinza claro, visível** |
| Paredes pretas | **Cinza 80** (E10, 26/10), planta por planta |
| Triângulo de orientação nas escadas (R14) | **S/D do PDF** (E3, 26/10), planta por planta |
| Escadas com as linhas dos degraus (bocel de 19/10; traços do PDF em cinza 85 na primeira versão da E8) | **Sem linhas: degraus na pedra, com o sombreamento de subida ou descida** (26/10) |
| Casa A · Subsolo: divisória entre os banhos feminino e masculino como divisória clara (item 94 de 19/10) | **Parede em cinza 80** (26/10) |
| Casa A · Subsolo: banho de serviço em Barlavento | **Bege Bahia** (26/10) |
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
  - **[22/10] Casa B:** o travertino é o da biblioteca (`_texturas/travertino.jpg`, tecido sem repetição), aplicado na final de 3840 px (59,7 px/m), onde os veios aparecem. Não pode haver riscos, emendas nem juntas: os traços verticais e as manchas do motor saem junto com o piso antigo (usuário: "melhore o aspecto do travertino. Remova os riscos").
- **Escadas:** o sentido (de onde sobe) é o que o usuário define, mesmo quando o PDF indica outro. O triângulo fica no 1º degrau de quem sobe, apontando para a subida. A parte viva fica desse lado; a parte esmaecida e tracejada, depois do corte.
- **Vidros em folha contínua:** sem montantes nem marcas no meio; só a folha com os perfis finos dos dois lados (os pontos escuros davam a impressão de várias folhas).

## 19. Especificações de 26/10/26 (todas as casas)

Pedido do usuário (26/10/26): "Especificações para todas as casas, valide cada uma delas em todas as plantas de todas as casas". Ele pediu também: "Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."

As 11 especificações, na ordem do usuário (E1 a E11 nos mapas da auditoria):

| | Especificação (palavras do usuário) | Como fica na planta |
|---|---|---|
| E1 | "Verificar e validar a posição das soleiras." | Porta a porta contra o PDF, como a R13. |
| E2 | "Representar os armários cortados com os cabides." | Todo armário cortado em planta (closets, quartos, DCE) com os cabides, como a R11. |
| E3 | "Colocar o sentido nas escadas (S / D), em vez de triângulo." | A letra S ou D do PDF, em Inter SemiBold, cinza quase preto, na origem do texto do PDF. Substitui o triângulo da R14. O sentido é o dos triângulos atuais, que já seguem as decisões do usuário (seção 18). Sem a linha de percurso do PDF (usuário, 26/10: "não precisa constar linhas"). |
| E4 | "Marcar com uma setinha a entrada principal da casa." | Seta cheia, preta, de ~1,5 m, sobre o piso de fora, apontando para a porta principal. Só no Térreo. |
| E5 | "Representar os boxes." | Box em vidro contínuo e visível (R10), nunca só o tracejado do caimento. |
| E6 | "Retirar a representação dos raios nas portas." | Sem arco (R3). |
| E7 | "O nome do ambiente não deve ficar sobre os objetos; optar sempre por uma das cores, branco ou preto, para criar contraste." | R6 e R7. Também fora da área do chuveiro e sem encostar na linha do box nem na bancada. |
| E8 | "Representar a escada de forma mais demarcada." | Os degraus demarcados pelo sombreamento (cada degrau um pouco mais claro que o de baixo e a sombra curta de cada espelho), sem linhas (usuário, 26/10: "não precisa constar linhas, mas sim sombras denotando que o sentido é de subida"; a proposta inicial eram as linhas do PDF em cinza 85). |
| E9 | "Se a bancada e o piso forem da mesma cor, deixar a bancada mais marcada do que o piso." | Borda fina no tom escurecido da própria pedra e uma sombra curta. |
| E10 | "Representar as paredes em planta com uma tonalidade de um cinza escuro e os pilares no preto para melhor contraste." | **Paredes em cinza 80 (RGB 80, 80, 80; resposta do usuário: "Qual cinza para as paredes: 50, 70 ou 90? Resposta: 80")** e pilares pretos, inclusive os redondos (substitui o pilar redondo cinza de 22/10). |
| E11 | "Se atentar à escala das texturas de piso." | As mesmas texturas e escalas em todas as casas. |

**Auditoria de 26/10** (`POE642_CasaA/scripts/auditoria_2610.py`, que só aponta e não altera nenhuma imagem): os mapas numerados de cada planta estão em `POE642_Casa?/renders/POE642_Casa?_PH_<pav>_auditoria_2610.jpg`; a prévia do estilo proposto e a comparação das escalas, em `_auditoria_2610/`.
- **Conformes em todas as plantas:** E1 (todas as portas conferidas com o PDF), E6 (nenhum raio de porta visível).
- **Inconformes em todas as plantas:** E10 (paredes pretas, RGB 2 a 17), E3 e E8 (todas as escadas com o triângulo).
- **E4:** nenhuma das 5 entradas principais tem seta.
- **E2, E5, E7, E9:** os itens de cada planta estão nos mapas.
- **E11:** as madeiras e o granito das Casas A e E (que vieram de renders de 2000 px) são mais largos e mais borrados que os das Casas B, C e D (réguas de ~10 a 12 cm, com as emendas). A proposta é levar A e E às texturas e escalas de B, C e D, já aprovadas.
- **Fora das 11:** linha tracejada vertical que não existe no PDF atravessando a suíte master e o banho master do 1º Pavimento da Casa A.
- **Respostas do usuário:** paredes em cinza 80; "O tapete conta como objeto, sim" (o rótulo não fica sobre o tapete: A Térreo, sala de estar; A 1º Pav, sala íntima); "vou aprovar planta por planta".

**Aplicação (planta por planta):**
- **Casa A · Subsolo (26/10, `POE642_CasaA/scripts/final3840_casaa.py`, final refeita em 3840 px; aprovada pelo usuário: "OK, subsolo da casa A aprovado"):** os pedidos do usuário para esta planta e a auditoria:
  - travertino bruto no hall, na sauna com a antessala e nos banhos feminino e masculino, na escala das Casas B a D, no creme delas, com os veios horizontais e os poros (E11);
  - Bege Bahia no pátio, na circulação, no depósito e no banho de serviço (que era Barlavento: "Já o banho serviço tem piso em mármore bege bahia");
  - a madeira da academia nas réguas das Casas B a D (E11);
  - o banco da sauna em travertino bruto, mais marcado, com a quina boleada e a sombra de contato;
  - a cabine do elevador em aço, como nas Casas B a D, com a soleira em inox (no lugar do travertino);
  - os chuveiros (placa cromada com os furinhos, braço e canopla) e os boxes (as duas folhas contínuas do PDF, mais visíveis, e o trilho no vão);
  - os armários do depósito em freijó (usuário: "para o armário do deposito use a madeira feijó" e "sem linhas e marcações"): os dois retângulos da DOC_LINHAS, até o teto, uma peça contínua com o veio reto do freijó, sem módulos, sem linha da frente e sem contorno, só com a sombra curta;
  - as portas de vidro de correr da academia (pergunta do usuário: "estão bem representadas?"; não estavam), redesenhadas pelo PDF na resolução da prancha: do pátio, 4 folhas em 2 planos com os montantes e os batentes; do hall, 2 folhas desencontradas sobre a soleira de Bege Bahia nítida; e o vidro fixo em L da sauna (usuário: "corrija essa falha ao final da esquadria"), com o caixilho e as linhas do PDF até a parede, sem riscos em volta (usuário: "remova os riscos do contorno do vidro que não fazem parte": o vão da parede sob o vidro vai sem as faces em cinza); a porta de giro da sauna, que faltava (usuário: "faltou a representação da porta da sauna"): a folha aberta para a antessala, como no PDF, no estilo do vidro fixo da sauna, com os batentes brancos e sem o arco (R3);
  - banhos feminino e masculino: bancada em travertino bruto, mais marcada que o piso (E9); cubas em granito marrom; vasos marrons; a divisória entre os dois vira parede em cinza 80 (substitui o item 94 de 19/10);
  - banho de serviço: bancada em granito marrom, cuba branca, louças e metais nítidos pelo PDF; o vaso fica branco (não foi pedido em marrom);
  - paredes em cinza 80 (E10); a escada com o S (E3), os degraus em Bege Bahia (usuário: "os degraus da escada que sobem são em mármore bege bahia"; eram creme chapado), sem linhas e com o sombreamento de subida (usuário: "não precisa constar linhas, mas sim sombras denotando que o sentido é de subida"), esmaecidos depois do corte; o rótulo do banho de serviço fora do box (E7).
- **Casa A · Térreo (26/10, `POE642_CasaA/scripts/final3840_casaa_terreo.py`, final refeita em 3840 px; aprovada pelo usuário: "terreo aprovado"):** a lista apresentada ao usuário e aprovada ("aplique a lista"); no travertino, "B" (fica o de hoje, rosado e quase liso):
  - paredes em cinza 80 (E10), com os muros do lote (a linha preta da final, em cima, embaixo e à esquerda, também em cinza 80); os pilares soltos já eram pretos e ficam; os brises ficam como estão;
  - escadas sem triângulo e sem linhas (E3, E8), os degraus marcados só pelo sombreamento, com a letra do PDF: S na escada interna do jardim e na caracol, D no lance do deck abaixo do spa; os degraus escalonados entre o deck da piscina e o deck de madeira (sem letra no PDF) com o D no degrau de cima. Onde a origem do texto do PDF cai fora do degrau (no vidro junto à escada interna, na borda do deck), a letra fica centrada no 1º degrau (o de cima, no lance do deck). Os escalonados: blocos de Bege Bahia sem contorno, cada um com a sombra curta no de baixo. A caracol: os degraus em leque em volta do pilar (preto, E10), cheia até a marca de corte e esmaecida depois (um véu claro sobre o granito no lugar do tracejado), com o corrimão;
  - a seta da entrada principal (E4): cheia, preta, de 1,5 m, no Bege Bahia do hall externo, apontando para a porta pivotante, abaixo do rótulo;
  - o armário do quarto do motorista com os cabides e o cabideiro, como os closets da Casa A (E2); o box do banho do motorista em vidro contínuo, a faixa cinza-clara no granito, com o trilho até a parede (E5);
  - a bancada do lavabo com a borda no tom escurecido da pedra e a sombra curta (E9);
  - os rótulos: LAVABO no corpo do PDF, sem encostar na bancada; SALA DE ESTAR fora do tapete, no piso livre entre ele e as poltronas do estar sob a projeção (E7);
  - o granito marrom (cozinha, gourmet, serviço, despensa, gás, motorista e garagem) no granito das Casas B a D (E11), só no piso: os objetos ficam, e ficam também as sombras e o tracejado das projeções.
  - **Pedidos seguintes do usuário (26/10):**
    - "melhorar o aspecto do travertino bruto no piso do térreo": o travertino bruto do Subsolo aprovado (os veios horizontais e os poros, no creme das Casas B a D) em todo o piso de travertino da base (estar, jantar, varanda, halls, escritório, lavabo, lavatório, banho varanda, WC, lounge do gourmet) e no trecho cheio da escada interna; só no piso: os móveis, as sombras e o tracejado ficam (substitui o "B" de antes);
    - "sanitário do lavabo em marrom escuro" e, nos banheiros da varanda gourmet, "sanitários no marrom escuro": os vasos do lavabo, do WC e do banho varanda em louça marrom-escura;
    - no lavatório da varanda gourmet: "cuba esculpida no marrom granito, pedra bancada cuba em mármore travertino bruto levemente escurecido para distinguir do piso" (a bancada no travertino mais marcado das bancadas do Subsolo, com a borda e a sombra);
    - "Banho serviço: piso em mármore bege bahia, pedra pia em marrom granito levemente escurecida para distinguir do piso": no Térreo não há banho com esse nome; o banho de serviço é o do motorista: piso em Bege Bahia, bancada em granito marrom um pouco mais escuro (com a borda e a sombra), cuba branca, chuveiro em placa cromada; o vaso fica branco;
    - "o escrito do b. motorista pode ficar mais abaixo e centralizado": no meio do piso seco, abaixo do vaso e da cuba;
    - "pedra da ilha em U da vanrada gourmet é marrom granito, igual ao piso. deixe-a levemente escurecida para distinguir do piso": a ilha em U (era quartzito Carrara) em granito marrom um pouco mais escuro que o piso, com a borda e a sombra, a área molhada rebaixada um tom abaixo e a cuba de inox da final;
    - as projeções tracejadas em preto ou branco pelo fundo (R8, acima): os dois X do pavimento superior, a claraboia do lavabo, a laje superior e o X da área de serviço descoberta, a grade do pergolado e o contorno de fora da cobertura.
  - **Depois (26/10):**
    - "faça uma limpeza em contornos. apareceram alguns erros em volta de pisos, bancadas, sanitários, cubas, etc. faça uma auditoria e corrija.": a troca do travertino e do granito refeita até a borda das peças (seção 3, contornos limpos). Corrigidos: o anel rosado em volta de cadeiras, sofás, tapete, louças e bancadas; o fantasma do vaso antigo no banho varanda; a faixa clara na borda da bancada do lavatório e na do lavabo; os pontos de piso dentro da bancada do lavabo; a moldura branca da cuba de inox da ilha; a linha clara na borda de dentro da ilha em U; a faixa no meio da janela do WC; os pontos escuros na divisa do hall interno com o externo; os retângulos rosados soltos no piso (jantar, estar, halls); os primeiros traços das diagonais do X da varanda, que ficavam rosados (o tracejado agora sai inteiro);
    - "Me parece que você removeu um cooktop da bancada da ilha da varanda gourmet.": o PDF tem um cooktop de 5 bocas no braço de cima da ilha em U, que a final aprovada não mostrava; entra o cooktop de inox da biblioteca (o mesmo da ilha da cozinha), com os botões do lado de quem cozinha, mais o degrau do balcão das banquetas e as laterais em cascata do PDF em linha fina;
    - "as bancadas em pedra da cozinha também são no granito marrom, levemente escurecido.": a ilha e a bancada da pia da cozinha (seção 3); a bancada em L da área de serviço, com os tanques, fica em Carrara (perguntado, o usuário respondeu "mantem").
- **Casa A · 1º Pavimento (26/10, `POE642_CasaA/scripts/final3840_casaa_1pav.py`, final refeita em 3840 px; aprovada pelo usuário: "1º pavimento da casa A aprovado"):** a lista apresentada ao usuário e aprovada, com as respostas dele ("A. Sim." e "B. mantem") e os pedidos seguintes:
  - paredes em cinza 80 (E10), também as paredes compridas da suíte master, do banho master e da sala íntima;
  - escada em U sem triângulo e sem linhas (E3, E8): os degraus 8 a 19 no travertino bruto do piso, com o sombreamento de subida, e o D no degrau 19; os degraus 1 a 7, do Térreo, nublados até a linha de corte do Térreo, desenhada (seção 5, descida); a caracol da saleta com os cinco degraus do 1º Pavimento no travertino da caracol do Térreo, sombreados, o D do PDF e o resto do círculo com o Térreo nublado;
  - o armário do quarto de serviço com os cabides (E2); os boxes em vidro contínuo com o trilho (E5); os chuveiros pelo PDF;
  - banhos 1, 2, 3 e master: bancada em travertino bruto mais marcado (E9), cubas em travertino bruto e vasos brancos; B. serviço: bancada em granito marrom, cuba branca e vaso branco (seção 6);
  - pisos na escala (E11), até a borda das peças (seção 3): travertino bruto na circulação, na sala íntima e nos banhos; o vinílico nas réguas das Casas B a D; o Bege Bahia no quarto de serviço, na saleta e no B. serviço (as varandas ficam);
  - as projeções em preto ou branco pelo fundo (R8): a cobertura, o pergolado e os X dos vazios; a linha tracejada da suíte master e do banho master, tida como espúria, é o contorno de dentro da cobertura no PDF (ARQ_CONTRAPISO): fica, como projeção (perguntado, o usuário respondeu "mantem");
  - o Térreo nublado refeito a partir do Térreo novo (sem as letras das escadas, as projeções, a seta e os rótulos);
  - os rótulos BANHO 3 e B. SERVIÇO longe da linha do box, SALA ÍNTIMA fora do tapete, acima do sofá (E7).
- **Casa B · Subsolo (26/10, `POE642_CasaA/scripts/final3840_casab.py`, final em 3840 px; aprovada pelo usuário: "subsolo da casa B aprovado"):** a lista apresentada e aprovada ("ok, aplique a lista") e o pedido dos banhos:
  - paredes em cinza 80 (E10), também o muro que sobe na hachura acima do depósito; as portas e janelas com os batentes em cinza 80 (a limpeza das esquadrias passa a ler a parede cinza);
  - escada da ducha sem triângulo e sem linhas (E3, E8): os 5 degraus em Bege Bahia com o sombreamento de subida, a sombra do 1º degrau no deck e o S no 1º degrau;
  - os boxes do BH sauna e do BH serviço em vidro contínuo, com as faces finas e a sombra curta (E5);
  - as bancadas mais marcadas que o piso, com a borda no tom escurecido da pedra e a sombra curta (E9);
  - o rótulo CIRCULAÇÃO (2,23 m²) no meio do corredor, sem encostar nas paredes (E7); o rótulo SHAFT do PDF;
  - banhos (seção 6): BH sauna com as prateleiras em granito marrom, a cuba esculpida em travertino bruto e o vaso marrom; BH serviço com a bancada em granito marrom, a cuba branca e o vaso branco;
  - "melhore o aspecto do marmore travertino bruto": o piso de travertino (sauna, BH sauna com a ducha, depósito) e os bancos da sauna no travertino bruto aprovado na Casa A (a foto da biblioteca na escala, com os veios horizontais longos e os poros pequenos), na luz e no creme de antes; os bancos no desenho mais marcado das bancadas, mantidos os dois níveis, a linha fina e a sombra discreta;
  - "melhore a representação da cuba esculpida com o marmore travertino, mais claro": a cuba do BH sauna é uma peça só de travertino claro (um pouco mais clara que o piso, com o desenho calmo do travertino bruto, poucos poros), do contorno de fora do aro do PDF: a borda larga com a quina clara do lado da luz e a escura do outro, a bacia de cantos bem arredondados e funda (a parede de cima e da direita na sombra, a de baixo e da esquerda na luz), o contorno fino no tom da pedra, a válvula cromada e a sombra curta na bancada; o granito não passa mais por baixo dela (antes, as tiras do aro saíam em granito com a borda escura, um contorno marrom em volta da cuba);
  - depois da aprovação: "corrija o local da ducha externa da planta do subsolo, conforme está na planta do térreo": o chuveiro do deck da ducha segue o do PDF do Térreo (antes, na parede da sauna, à direita) e, com o recorte do Térreo ("a ducha fica mais no canto"), no canto do deck, como lá: a ducha a 28,5 pt (~50 cm) da parede da sauna, como no Térreo da borda do deck, e o braço até a parede de baixo. Regra: quando um pavimento não traz a peça e outro traz, vale a posição do PDF que a traz, medida a partir do canto do ambiente (não a coordenada solta, se os ambientes diferem).
- **Casa B · Térreo (26/10, `POE642_CasaA/scripts/final3840_casab.py`, final em 3840 px; aguarda o OK do usuário):** a lista apresentada e aprovada ("ok, aplique a lista. pilares em preto") e os banhos pela descrição do usuário (seção 6):
  - paredes em cinza 80, também os muros do lote (E10); os dois pilares redondos da garagem e do quarto do motorista em preto (a resposta do usuário substitui o cinza de 22/10);
  - a seta da entrada principal no piso do HALL, apontando para a porta pivotante do HALL INTERNO, abaixo do rótulo (E4);
  - as escadas sem triângulo e sem linhas (E3, E8): a de 6 e a de 9 degraus com o sombreamento e o D do PDF no degrau de cima; a pedra grande e as lajes em cascata sem o bocel, marcadas pela sombra curta de cada uma, com o D no lugar do triângulo de 22/10;
  - as bancadas com a borda e a sombra (E9): as dos banhos, do lavabo e do lavatório gourmet em travertino bruto; as da cozinha, do gourmet e do serviço na pedra areia;
  - os boxes em vidro contínuo com as faces e a sombra curta (E5); os do granito (BH serviço e BH motorista) na faixa cinza-clara de 22/10;
  - as projeções em preto ou branco pelo fundo (R8): os X do jardim de inverno e dos três shafts, a pérgola da entrada e a linha da cobertura junto ao living e à sala íntima;
  - o rótulo SHAFT do PDF junto ao elevador;
  - a linha que não existe no PDF, da janela da suíte 3 atravessando o banho 3, saiu (era o trilho da cortina da suíte 3, que passava pela parede fina do banho; agora o trilho para na primeira parede do PDF);
  - o piso de travertino no travertino bruto do Subsolo aprovado (E11), também nas faixas dos jardins e das esquadrias.

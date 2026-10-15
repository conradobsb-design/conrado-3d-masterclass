# gerar_bases.py — bases das plantas humanizadas (POE 642 · Casa A)

Reescrita do pipeline da seção 5 do handoff (`../POE642_CasaA_HANDOFF_ClaudeCode.md`). O script original não foi guardado.

## Instalação (Windows ou Mac)

```
pip install pymupdf numpy scipy pillow
```

## Uso

```
# diagnóstico: quais layers e preenchimentos o PDF tem (rode isto primeiro em todo PDF novo)
python gerar_bases.py Terreo "C:\...\planta_terreo.pdf" --listar-layers

# base sem texto + base v3 (paredes pretas, vidro cinza neutro) + versão 16:9 + prévia de conferência
python gerar_bases.py Terreo     "C:\...\planta_terreo.pdf"  --saida "C:\...\POE 642\Casa A" --debug
python gerar_bases.py 1Pavimento "C:\...\planta_1pav.pdf"    --saida "C:\...\POE 642\Casa A" --debug
python gerar_bases.py Subsolo    "C:\...\planta_subsolo.pdf" --saida "C:\...\POE 642\Casa A" --debug

# PDF com várias plantas: escolha a página (0 = primeira)
python gerar_bases.py Subsolo planta.pdf --pagina 2
```

## O que cada saída é

| Arquivo | Conteúdo |
|---|---|
| `POE642_CasaA_BASE_<Pav>.png` | Passos 1–2: sem texto, recortada, 6000 px, cores do PDF |
| `POE642_CasaA_BASE_<Pav>_v3_vidros_neutros.png` | Passos 1–5: paredes #111111, vidro #D6D6D3 com contorno preto de 2 px |
| `POE642_CasaA_BASE_<Pav>_v3_vidros_neutros_16x9.png` | A mesma v3 centralizada numa tela branca 16:9 (a saída do motor é 16:9; a base é ~1,545:1) |
| `POE642_CasaA_BASE_<Pav>_debug.png` | Prévia de 1800 px: ○ vermelho = vidro aceito, ○ laranja = folha de porta, ○ azul = traço sobre parede, ○ roxo = zona/muro excluído |

## Ajustes em `config_bases.json`

- `layer_parede` / `cinza_parede`: a layer `ARQ_PAREDE` com preenchimento cinza 0.357. Se um PDF novo usar outros nomes, o `--listar-layers` mostra quais são.
- `cinza_parede_qualquer_layer` (padrão `true`): converte para preto o cinza 0.357 de parede **em qualquer layer**, não só na `ARQ_PAREDE`. Na base do Térreo, a parede de cima do estar e a parede ao lado da marcenaria ficaram em cinza #5B5B5B com contorno preto, e o motor lia essas paredes como faixa de vidro. A detecção de vidro continua só na `ARQ_PAREDE`.
- `zonas_excluidas`: retângulos `[x0, y0, x1, y1]` medidos **na prévia de 1800 px** (a mesma escala do `_debug.png`). Quando a prévia mostrar um falso vidro (bancada, ilha, guarda-corpo, gradil), anote a zona aqui. O Térreo já tem as zonas do handoff, e o Subsolo tem duas folhas de porta.
- `eixo_janela_max_pt` (por pavimento, opcional): descarta o traço curto, de até esse comprimento em pt, que atravessa uma janelinha pelo lado curto da caixa. É o eixo do bloco de janela do CAD. Como vidro, ele virava um "+" na parede, e o motor desenhava ali um registro ou um chuveiro. No 1º Pavimento vale 20 e tira 10 eixos; a prévia `--debug` marca esses descartes em verde.
- `faixas_y_excluidas`: os muros (y < 100 ou y > 1030 na prévia).
- Uma zona também pode ser `{"bbox": [...], "pintar": "#2B2B2B"}`: o que estiver nela sai da detecção de vidro e é pintado nessa cor. No Térreo, as lâminas dos brises viram alumínio escuro em vez de faixas de vidro.
- `reforcar_linhas` (por pavimento): redesenha os traços de uma layer mais grossos e escuros, com ponta reta para o tracejado manter os vãos. No Térreo, o pergolado (`ARQ_PERGOLADO`) vem do PDF em 0,21 pt cinza, que na base de 6000 px vira menos de meio pixel. Por isso ele sai em #4D4D4D com 3 px. O 1º Pavimento já tem a mesma regra; se a layer não existir no PDF, o script mostra 0 traços.
- `legenda` (por pavimento): passo 6, que deixa cada material numa cor única da legenda do prompt. Só pixels da cor de origem mudam, então linhas, móveis e símbolos ficam intactos.
  - `trocas_cor`: troca global de cor. No Térreo, o cáqui #BAB596 vira travertino #DCD9CA e o cinza #E4E4E4 vira Bege Bahia #E8E8E8.
  - `poligonos`: recolore preenchimentos do PDF por layer, cor e região. No Térreo, o acesso de veículos e o corredor de serviço, que usavam o mesmo cinza do deck, viram caramelo #B98A55.
  - `poligonos` com `"modo": "neutros"`: para área sem preenchimento colorido. Dentro do polígono, o branco vira `para` e os símbolos cinza viram `cor_linha`; cores com matiz, como degraus e madeira, ficam. `proteger_layers` lista as layers cujo desenho não muda (paredes, vidros, bordas, degraus). No Térreo, o jardim em volta da escada principal fica verde #6E9150, com o pontilhado de jardim em #557A3D.
  - `retangulos`: pinta um retângulo exato por inteiro e redesenha por cima só as linhas de uma layer (`linhas_layer`, `cor_linha`). No Subsolo, a escada que desce para o pátio da academia sai em creme #D8CDB4 com as linhas de `ARQ_ESCADAS E RAMPAS`. A hachura não servia ali, porque as linhas do deck invadem os últimos degraus.
  - `retangulos` com `"so_cores": ["#hex", …]`: dentro do retângulo, só essas cores viram `para`; com `cor_linha`, as linhas cinza também mudam. Na Casa B, a ducha sai de deck de madeira (#E4E4E4 → #AE8863, réguas em #8A6A4C).
  - `retangulos` com `"so_branco": true`: dentro do retângulo, só o branco vira `para` e as linhas cinza viram `cor_linha`; paredes pretas e cores ficam. No 1º Pavimento, os vazios de pé-direito duplo saem em #4A4A4A com o X claro, e as faixas em volta da escada em U em #4A4A4A. Na base v3, a abertura branca da saleta em volta da caracol vira Bege Bahia (#E8E8E8), e a varanda da suíte 1 perde as linhas tracejadas do Térreo (`cor_linha` igual a `para`). Sem `so_branco`, o retângulo é pintado por inteiro: assim saem as placas de 30 cm dos três chuveiros de teto, cinza-aço com borda escura.
  - `setores`: um quarto de círculo numa cor (`centro_vis`, `raio_vis`, `quadrante` = sup_dir, sup_esq, inf_dir ou inf_esq). No 1º Pavimento, o trecho da escada caracol que chega ao piso sai em creme #D8CDB4. O resto do círculo esmaece com `esmaecer.clarear_circulos`, que aceita um `clarear` próprio por círculo. Na base v2, os 3/4 da caracol que são do piso de baixo clareiam 80%, para lerem como branco.
  - `hachuras`: pinta áreas sem preenchimento que só têm hachura sobre branco. No Térreo, o deck de madeira fica marrom #AE8863, com as linhas em marrom escuro, e a escada abaixo do spa fica Bege Bahia (`"linhas": "verticais"`).
- `esmaecer` (por pavimento): passo 7. Clareia tudo fora dos retângulos `manter_bbox_vis`; `clarear` vai de 0 (nada) a 1 (branco). No Subsolo, ficam com a cor cheia os três blocos do subsolo, o pátio de acesso à academia e a escada que desce do deck. A piscina, o ofurô, o deck de madeira, os degraus escalonados, o deck da piscina e o terreno clareiam 55%.
- `ocultar_layers_zonas` (por pavimento): desliga uma layer só dentro de retângulos da prévia de 1800 px. O script renderiza a página de novo sem a layer e copia só essas zonas. No Subsolo, as projeções (`DOC_LINHAS E PROJEÇÕES`) dentro do depósito e junto à parede de baixo da academia viraram sauna e banco no render, então saem. Os X do elevador e dos shafts, que estão na mesma layer, ficam.
- `layers_ocultas`: layers a desligar antes do render, para o pavimento inteiro (global ou por pavimento). No Subsolo, `ARQ_TERRENO PLANEJADO` sai porque o motor tingia o lote de bege. Sem ela, o fundo fica todo branco. Use quando o texto do CAD vier **vetorizado** (fonte SHX desenhada em linhas): a redação só remove texto real. Ex.: no executivo 005 do Drive, `dz-cota dz-s16 dz-s18 dz-s20 "dz-legenda estrutura" dz-22` apagam cotas e nomes de ambientes. Também dá para passar na hora com `--ocultar`.
- `vidro`: espessura máxima e comprimento mínimo (em pt do PDF) das formas e traços que contam como vidro, tolerâncias da detecção de porta e largura mínima do vidro em pixels.

## Retoque sem IA: `retoque_chuveiros_1pav.py`

Corrige só os chuveiros de teto do render do `v7_ajuste` do 1º Pavimento. O motor errou a posição deles em todas as tentativas por prompt.

1. **Alinhamento:** alinha o render da v7, onde a banheira e o piso estão inteiros, ao render a corrigir. Depois alinha a base v3 ao render da v7. Os dois alinhamentos são feitos por SIFT e transformação afim, com erro mediano de 0,4 px.
2. **Placas grandes:** troca as placas grandes fora do lugar pelo mesmo trecho do render da v7.
3. **Duchas:** apaga as duchas redondas com braço por inpaint.
4. **Placas finas:** desenha placas de 30 cm, com contorno prata fino e furinhos, nas posições das placas cinza da base.

A saída tem dois arquivos:
- **`_final.png`:** o render corrigido.
- **`_final_camada.png`:** transparente fora das alterações, para usar como camada no Photoshop.

Os retângulos de correção estão em px de um render com 2000 px de largura. O script reescala esses valores para o tamanho do arquivo, então também roda com o PNG original em resolução cheia. Precisa de `opencv-python-headless`.

```bash
python retoque_chuveiros_1pav.py ../renders/POE642_CasaA_PH_1Pavimento_v7_ajuste.webp ../renders/POE642_CasaA_PH_1Pavimento_v7.webp ../bases/POE642_CasaA_BASE_1Pavimento_v3_16x9.png --saida ../renders
```

## Retoque a partir da base: `retoque_base_1pav.py`

Roda sobre o `_final.png` e usa a base v3 alinhada ao render, por SIFT e transformação afim, com erro mediano de 0,4 px. Corrige três pontos:

1. **Escada em U:** apaga as linhas do render por inpaint, mantendo a textura de travertino, e desenha as linhas da base: 9 degraus por lance, linha de descida em U, círculo de partida e seta.
2. **Saleta da caracol:** a abertura em L em volta da escada é vão e fica branca, com o desenho do PDF tirado da `bases/POE642_CasaA_BASE_1Pavimento_semtexto.png`. Esse desenho tem os degraus que descem (contínuos no quarto de cima à esquerda e tracejados embaixo), o arco central, as marcas e as linhas duplas que dividem o vão do piso. O quarto creme e o piso em volta ficam do render.
   - Na bancada da entrada da suíte master entra a cuba redonda com a torneira saindo da parede de baixo, medida na mesma base.
   - Os vãos de pé-direito duplo deixam o cinza-escuro e ficam brancos, com o X tracejado e o contorno do PDF. São os dois quadrados grandes, as faixas em volta da escada em U e o vão entre os lances.
3. **Entorno:** tudo fora dos retângulos `esmaecer.manter_bbox_vis` passa a ser a base esmaecida. Isso inclui as pedras de acesso ao hall externo, o pergolado tracejado, a piscina, o ofurô, o deck e os contornos.

A base é reduzida com média (`INTER_AREA`) antes da afim. O `warpAffine` não faz média, e as linhas finas da base sumiriam aos pedaços.

```bash
python retoque_base_1pav.py ../renders/POE642_CasaA_PH_1Pavimento_v7_final.png ../bases/POE642_CasaA_BASE_1Pavimento_v3_16x9.png --saida ../renders
```

## Retoque do Subsolo: `retoque_subsolo.py`

Aplica direto no render aprovado da v6 o ajuste que estava pendente:
1. **Sauna:** o bloco claro no canto, junto ao vidro, vira piso de travertino, copiado das mesmas linhas logo à direita. Fica só o banco horizontal.
2. **Tom:** a imagem fica mais clara e com menos sombra. É uma curva de meios-tons no L do Lab; o preto e o branco não mudam.
3. **Fundo:** o quase-branco vira branco puro.

## Pranchas de entrega: `rodape_entrega.py`

Gera o rodapé de cada pavimento, em 3840 × 440 px, e monta as pranchas: render em cima e rodapé embaixo, na mesma largura.

Os dados de cada casa ficam na chave `entrega` da config dela: pavimentos (título, linha destacada no quadro de áreas e base 16:9), áreas, dados do projeto, pastas e o PDF. Sem `--config`, vale a da Casa A (`config_bases.json` desta pasta). O `pdf_entrega.py` lê a mesma chave. A largura das pranchas vem de `largura_prancha` (Casa A: 2000 px, porque os renders chegaram comprimidos; Casa B: 3840 px, a largura do rodapé).

As três pranchas têm o mesmo tamanho e a planta no mesmo pixel, para que, vistas em sequência, uma fique exatamente dentro da outra:
- **Base comum:** as três bases saem do mesmo enquadramento da folha do cliente. A piscina, por exemplo, cai no mesmo pixel nas três.
- **Alinhamento:** cada render é alinhado à base do seu pavimento, por SIFT e transformação afim, e levado ao quadro 16:9 dessa base.

```bash
python rodape_entrega.py --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_bege.png --render 1Pavimento=../renders/POE642_CasaA_PH_1Pavimento_v7_final2.png --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final.png
python pdf_entrega.py

# Casa B
python rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --render Subsolo=../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final.png
python pdf_entrega.py --config ../../POE642_CasaB/config_bases.json      # pranchas da entrega.pdf.ordem
python rodape_entrega.py --config ../../POE642_CasaC/config_bases.json --render Subsolo=../../POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_v3_retocado.png --render Terreo=../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_retocado.png
python pdf_entrega.py --config ../../POE642_CasaC/config_bases.json      # Subsolo e Térreo
```

## Prévia de texturas: `texturizar_base.py`

Troca as cores chapadas da legenda pelas texturas aprovadas nos renders da Casa A, para o motor ver na base o aspecto de cada piso.

Cada material está na chave `texturas` do pavimento, com:
- as cores da legenda que ele substitui;
- os trechos de origem, em px de um render de 2000 px;
- opcionalmente, um `bbox_vis` para limitar a área e um `escurecer`. No banco da sauna, por exemplo, o tom fica um pouco mais escuro para continuar se lendo como banco.

Só mudam os pixels da cor da legenda, e só dentro das áreas com cor cheia (`esmaecer.manter_bbox_vis`). Linhas, paredes, vidros, portas, móveis e o entorno esmaecido ficam como estão. A textura é tecida por image quilting na escala do render e depois ampliada para a base.

```bash
python texturizar_base.py Subsolo ../../POE642_CasaB/bases/POE642_CasaB_BASE_Subsolo_v2.png --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/bases --nome POE642_CasaB_BASE_Subsolo_v3_texturas
```

Nos `retangulos` com `linhas_layer`, `sem_linhas_bbox_vis` lista as áreas cujos traços não voltam. Na Casa B, isso tira a ponta de seta e o círculo que contradiziam o sentido da descida.

## Elementos do render na base: `elementos_do_render.py`

Faz da base em alta resolução (6905 px) a imagem final. Do render, que sai em 2K com a casa pequena no quadro, vêm só os objetos fotorrealistas, colocados nas posições da base, que segue o layout do PDF.

1. Alinha o render à base, por SIFT e transformação afim.
2. Apaga da base os desenhos em traço que serão trocados, refazendo o piso por image quilting a partir de um trecho limpo do mesmo piso.
3. Recorta cada objeto do render e o cola no retângulo da base, girando ou espelhando quando preciso. O recorte usa uma máscara por cor: neutro sobre madeira para os aparelhos, claro sobre pedra (limiar de Otsu) para as louças.
4. Copia trechos do render, como a cabine do elevador, só onde a base é branca.

Onde o render não tem elemento para trocar, fica o que a base tem. A config está na chave `elementos_do_render` do pavimento.

```bash
python elementos_do_render.py Subsolo ../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_v2_render.webp ../../POE642_CasaB/bases/POE642_CasaB_BASE_Subsolo_v3_texturas_16x9.png --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/renders --nome POE642_CasaB_PH_Subsolo_elementos
```

## Retoque do Térreo da Casa B: `retoque_terreo_casab.py`

No Térreo da Casa B, a imagem final é o próprio render, retocado sem IA:
- o transbordo de água que o motor inventou à esquerda da piscina e dos decks vira gramado;
- o vão abaixo da escada de cima vira área verde;
- o símbolo de planta do hall vira uma touceira do próprio render;
- a bancada do lavatório gourmet fica no quartzo das bancadas da cozinha, e as cubas viram louça branca com torneira cromada.

```bash
python retoque_terreo_casab.py ../../POE642_CasaB/renders/POE642_CasaB_PH_Terreo_v4_render.webp --saida ../../POE642_CasaB/renders --nome POE642_CasaB_PH_Terreo_v4_retocado
```

## Retoques do Subsolo da Casa C: `retoque_subsolo_casac.py` e `retoque_subsolo_casac_v3.py`

No Subsolo da Casa C, a imagem final também é o próprio render, retocado sem IA.

**`retoque_subsolo_casac.py`** (render do prompt v1):
- tira a marca vermelha do usuário;
- vira a sombra dos degraus largos para o lado do pátio, porque eles descem para cima.

**`retoque_subsolo_casac_v3.py`** (render do prompt v3):
- **Bege Bahia:** pátio, degraus largos, caminho e depósito voltam ao Bege Bahia aprovado.
  - A textura é das varandas do 1º Pavimento da Casa A, tecida por quilting na escala do render.
  - As áreas vêm da base chapada (cor #E8E8E8), alinhada ao render por SIFT.
  - As pintinhas e os veios do mármore do render saem.
  - Os contornos, a porta do depósito e as plantas da floreira ficam.
- **Vaso do lavabo masculino:** o vaso cinza do motor vira piso e entra o vaso suspenso branco do lavabo ao lado da adega, espelhado, no retângulo do PDF.
- **Bancos ao pé das camas:** as camas que o motor esticou voltam ao comprimento do PDF (a ponta com borda e sombra é deslocada; o vão vira tapete ou piso) e entram os bancos do Térreo da Casa B, levados ao retângulo do PDF; a sombra deles entra como fator sobre o piso.
- **Arcos das portas sobre o granito:** as curvas da layer ARQ_PAREDE que caem no granito são redesenhadas em cinza claro, traço fino (Bézier do PDF levada ao render por `pdf_cadeia`), mascaradas pela cor exata do granito na base chapada.
- **Porta pivotante principal:** a folha é estendida com o próprio trecho dela até o fim do PDF, do lado de fora, com o arremate da ponta.
- **Cubas dos BH master 1 e 2:** no 1, as duas bacias do PDF (torneiras nas pontas) no lugar das duas cubas do motor, com a pedra da bancada entre elas; no 2, a cuba redesenhada com a torneira em cima. As bacias usam a `cuba` do `retoque_terreo_casab.py`.
- **Janela do escritório:** a folha de correr do motor sai e o vão recebe a janela das janelas da parede esquerda do escritório, girada, com dois panos e montante.
- **Cadeiras das escrivaninhas:** a cadeira de visitante do escritório (cor por máscara, sombra só como escurecimento), girada e centrada no símbolo do PDF, com a frente por baixo da escrivaninha.
- **Área molhada da cozinha:** retângulo do PDF em traço cinza fino nos lados livres.
- **Lavabo e adega:** a cuba a mais vira a bancada lisa do trecho de baixo (mesmas colunas, em espelho); o móvel inventado na adega vira o piso das colunas limpas da adega, em espelho; o móvel do topo do lavabo (malva no PDF) vira marcenaria areia, como os armários da cozinha.
- **Aparador do hall:** encurtado ao comprimento do PDF (a ponta com borda e sombra é levada ao fim) e a mesa redonda do PDF ao lado, no tampo de madeira do aparador, com contorno e sombra curta.
- **Degraus largos:** cada aresta é redesenhada com o perfil do render espelhado (sombra do lado do pátio, filete de luz do outro). Como no PDF, são 9 arestas: a de cima entra com o perfil médio das outras, e as 2 de baixo viram em L junto ao começo do caminho.
- **Banco da sauna:** o banco em U de madeira do render vira o banco da base, em travertino em L e em dois níveis, nos tons do banco aprovado da Casa B.
  - O travertino é o do piso da sauna no render, com os veios verticais continuados em espelho.
  - As arestas são finas, sem sombra.
- **Porta do elevador:** a porta de abrir que o motor pôs no acesso ao elevador vira o vinílico da academia ao lado; o vão e a soleira ficam.
- **Chuveiros de teto:** a ducha e o box do BH recebem a placa quadrada aprovada na Casa A, no centro do quadradinho da base, depois de apagar o que o motor desenhou.

```bash
python retoque_subsolo_casac_v3.py ../../POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_v3_render.webp --saida ../../POE642_CasaC/renders --nome POE642_CasaC_PH_Subsolo_v3_retocado
```

## Retoque do Térreo da Casa C: `retoque_terreo_casac.py`

A imagem final do Térreo da Casa C é o render, retocado sem IA, erro por erro.
- **Chuveiros de teto:** a placa aprovada da Casa A no centro de cada símbolo de chuveiro do PDF (5 boxes e a ducha entre os lavabos, onde a placa cobre o ralo redondo do motor).
- **Plantas fora do lote:** fora da linha tracejada e dos muros volta a ser a base (fundo branco); os muros cobertos por folhas são refeitos com o muro do próprio render.
- **Jardins de inverno:** as plantas ficam só dentro das floreiras; a parede do elevador é refeita com o perfil de um trecho limpo; o piso em volta vem do piso limpo ao lado, com emenda suave. As portas de correr de vidro vêm da base alinhada (o vidro e o preto marcados pela base chapada v2).
- **Cozinha:** bancadas e ilha no quartzo da bancada gourmet do próprio render (image quilting, `texturizar_base.quilting`), com o cooktop e as banquetas como estão; armários altos (retângulo com diagonal no PDF) em marcenaria areia, com contorno nas faces livres; vão de piso entre a geladeira e o armário; as duas cubas com a `cuba` do `retoque_terreo_casab.py`, viradas para a torneira ficar do lado da parede.
- **Quarto externo:** a cama de solteiro vem de uma cama do quarto 2 do próprio render (virada, encurtada no cobertor e ajustada à largura do PDF) e o criado-mudo vem do da suíte, cada um com a sombra curta das camas do render.
- **Tanques da área de serviço:** a bancada no mesmo quartzo da cozinha e os dois tanques copiados do Térreo aprovado da Casa B (mesma escala), nas posições da base alinhada.
- **Estar conforme o PDF:** o aparador inventado vira travertino tecido (image quilting só com espelhos, para os veios seguirem verticais, no tom do piso em volta); a mesa de centro vira as duas do PDF; as mesas laterais orgânicas têm a forma do próprio PDF, rasterizado e levado ao render por `pdf_no_render` (recorte, largura da base, tela 16:9, redução e o afim da base), no tampo da mesa de centro, com contorno e sombra curta.
- **Vaso do lavabo masculino:** o vaso cinza do motor vira piso e entra o vaso suspenso branco do lavabo ao lado da adega, espelhado, no retângulo do PDF.
- **Bancos ao pé das camas:** as camas que o motor esticou voltam ao comprimento do PDF (a ponta com borda e sombra é deslocada; o vão vira tapete ou piso) e entram os bancos do Térreo da Casa B, levados ao retângulo do PDF; a sombra deles entra como fator sobre o piso.
- **Arcos das portas sobre o granito:** as curvas da layer ARQ_PAREDE que caem no granito são redesenhadas em cinza claro, traço fino (Bézier do PDF levada ao render por `pdf_cadeia`), mascaradas pela cor exata do granito na base chapada.
- **Porta pivotante principal:** a folha é estendida com o próprio trecho dela até o fim do PDF, do lado de fora, com o arremate da ponta.
- **Cubas dos BH master 1 e 2:** no 1, as duas bacias do PDF (torneiras nas pontas) no lugar das duas cubas do motor, com a pedra da bancada entre elas; no 2, a cuba redesenhada com a torneira em cima. As bacias usam a `cuba` do `retoque_terreo_casab.py`.
- **Janela do escritório:** a folha de correr do motor sai e o vão recebe a janela das janelas da parede esquerda do escritório, girada, com dois panos e montante.
- **Cadeiras das escrivaninhas:** a cadeira de visitante do escritório (cor por máscara, sombra só como escurecimento), girada e centrada no símbolo do PDF, com a frente por baixo da escrivaninha.
- **Área molhada da cozinha:** retângulo do PDF em traço cinza fino nos lados livres.
- **Lavabo e adega:** a cuba a mais vira a bancada lisa do trecho de baixo (mesmas colunas, em espelho); o móvel inventado na adega vira o piso das colunas limpas da adega, em espelho; o móvel do topo do lavabo (malva no PDF) vira marcenaria areia, como os armários da cozinha.
- **Aparador do hall:** encurtado ao comprimento do PDF (a ponta com borda e sombra é levada ao fim) e a mesa redonda do PDF ao lado, no tampo de madeira do aparador, com contorno e sombra curta.
- **Degraus largos:** a seta da base sai e a sombra das arestas passa para o lado do pátio: em cada aresta tira-se o perfil do motor (medido) e aplica-se o da mesma escada no Subsolo aprovado (fator multiplicativo), inclusive nas arestas em L.
- **Chuveiro externo:** a cruz do motor sai (pedra, borda, grama e muro refeitos com os trechos limpos ao lado) e entra o chuveiro do PDF: ducha quadrada (placa da Casa A reduzida), braço cromado e canopla, com sombra curta.
- **Elevador:** caixa branca e a cabine do Subsolo da Casa B (sem a soleira), girada para a porta ficar à esquerda e levada à cabine do PDF.
- **Escada estreita:** 10 degraus como no PDF; as arestas do motor viram o piso do degrau ao lado e as novas recebem o perfil de sombra medido nas arestas do render (fator multiplicativo em 8x).
- **Porta do box do BH master 2:** folha de vidro aberta e arco do giro desenhados em 8x com a geometria do PDF, no traço das portas do render. O vão ao lado do chuveiro (projeção com dois X) fica tracejado sobre o piso: os X vêm do PDF levado ao render e o lado livre ganha contorno tracejado.
- **Cooktops:** 5 bocas como no PDF: na gourmet sai a boca do meio de cima; o da ilha vira o da gourmet corrigido, girado 90°.
- **Banquetas a mais na gourmet:** saem com a sombra; piso com os veios de baixo em espelho e a sombra da bancada refeita com o fator por linha medido nos trechos limpos da borda.
- **Poltronas a mais no estar:** saem com a sombra; piso com os veios de cima em espelho, borda do tapete do trecho limpo ao lado e tapete das linhas de baixo, com emenda suave.

```bash
python retoque_terreo_casac.py ../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_render.webp --saida ../../POE642_CasaC/renders --nome POE642_CasaC_PH_Terreo_v3_retocado
```

## Retoque do Térreo da Casa D: `retoque_terreo_casad.py`

Mesmo método da Casa C (render retocado sem IA, item por item, na ordem pedida pelo usuário); usa `CHUVEIRO_TETO`, os cromados e `SS` do `retoque_terreo_casac.py`.
- **Porta pivotante principal:** a folha é estendida com o próprio trecho dela até o fim do PDF, do lado do hall, onde o arco pequeno do render começa.
- **Chuveiros do banho master:** a barra do motor (e o texto ilegível junto à parede) vira o piso limpo de cima, em espelho; entram as duas duchas do PDF, na placa da Casa A reduzida, com sombra curta, braço cromado da parede lateral até o centro da ducha e canopla.
- **Armários até o teto:** retângulos com diagonal do PDF. A sombra projetada no piso sai como fator multiplicativo por canal: perfil mediano ao longo de cada face livre até o patamar do piso, modelo suave `modelo_sombra` (preserva o tom das réguas do vinílico), refinamento local ao longo da face (mediana móvel) e combinação pelo mínimo nos cantos. O tampo fica no tom areia da Casa C com o veio do próprio armário (luminância sobre ela mesma desfocada, limitada para tirar o sombreado de caixa); caixas lisas recebem o veio de outro armário. `piso_sob_armario` refaz o granito (quilting) embaixo dos armários junto a bancada.
- **Área molhada da pia da cozinha:** retângulo do PDF (ARQ_BANCADAS) em traço cinza fino nos lados livres, como na Casa C.
- **Inox:** os dois eletrodomésticos da cozinha mudam só de tom (cor de aço vezes a luminância relativa do render, com riscos verticais sutis); a borda com o granito é mesclada pela luminância.
- **Porta do abrigo de gás:** a soleira do motor vira o piso do abrigo (espelho) e as duas folhas de correr do PDF são desenhadas em 8x (folha, montantes, contorno e batentes), com sombra curta.
- **Carros:** curva de tom por carro na silhueta (não-granito: frio ou claro, fechada e preenchida, com a borda), escurecendo ou clareando a luminância do prata; a cor entra só nos tons médios e claros; lanternas (R bem maior que B) ficam.
- **Lote (erros 1 e 2):** o muro inventado vira grama (colunas de logo à direita); fora do lote, a base alinhada; os muros cobertos por folhas, com o perfil de uma coluna limpa.
- **Faixa com X (erro 3):** grama por quilting (`grama`), sombra dos muros por fator, e as linhas do PDF por `linhas_pdf` (`pdf_no_render` da Casa D, que desliga as layers ocultas da base; máscara de linhas engrossada e reduzida, em cor clara).

```bash
python retoque_terreo_casad.py ../../POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_render.webp --saida ../../POE642_CasaD/renders --nome POE642_CasaD_PH_Terreo_v1_retocado
```

## Acabamentos finais: `acabamentos_finais.py`

Roda depois do `elementos_do_render.py`. Onde o render não trouxe objeto, ficam na imagem símbolos técnicos do PDF. Este script os troca por objetos vistos de cima, sem IA, nas posições exatas do PDF:

- **`clonar`:** apaga um símbolo com o mesmo piso de um trecho limpo ao lado (carimbo com o tom médio ajustado).
- **`clonar` com `fonte_vis`:** copia um trecho escolhido, repetido em espelho (ex.: o tampo da bancada para o rebaixo); com `so_onde_alvo_branco`, só o branco muda.
- **`preencher_colunas`:** refaz um piso de veios verticais em volta de uma louça, coluna a coluna, ligando o tom de cima ao de baixo; a louça fica (`preservar_branco`).
- **`parede`:** refaz um trecho de parede repetindo uma linha limpa da mesma parede.
- **`arestas_banco`:** troca a linha dupla entre dois degraus por uma aresta de 1 px, no traço da aresta da frente.
- **`pintar`:** completa uma bancada branca com a cor da bancada.
- **`cubas`:** desenha cuba branca com torneira e válvula cromadas.
- **`armarios`:** troca o retângulo branco com diagonal tracejada (armário no PDF) pelo tampo do armário, na cor da marcenaria dos closets da Casa A, com contorno na face livre.
- **`chuveiros`:** desenha chuveiro de parede (canopla, braço e ducha redonda de 20 cm) e registro, cromados.

Os desenhos são feitos em 8x e reduzidos. Saem o PNG final, a prévia em JPG e um PNG transparente só com as alterações (`_camada.png`), para usar como camada no Photoshop. A config está na chave `acabamentos` do pavimento.

```bash
python acabamentos_finais.py Subsolo ../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_elementos.png --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/renders --nome POE642_CasaB_PH_Subsolo_final
```

## Casa B

O mesmo `gerar_bases.py` gera as bases da Casa B, com a config `projetos/POE642_CasaB/config_bases.json`. O nome dos arquivos de saída vem da chave `prefixo` da config (`POE642_CasaB`).

```bash
python gerar_bases.py Subsolo "642 - SUBSOLO - CASA B.pdf" --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/bases
python gerar_bases.py Terreo "642 - TÉRREO - CASA B.pdf" --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/bases
```

Recursos da legenda usados no Térreo da Casa B:
- **`poligonos` com `cor_linha`:** as linhas cinza dentro do polígono também mudam (ex.: réguas do deck em #8A6A4C). Com `cor_linha` igual a `para`, elas somem no material (ex.: os hexágonos do acesso de carros, que viram pedra portuguesa).
- **`setas`:** desenha uma linha de caminhamento com círculo no início e seta no fim (pontos em vis). Na Casa C, marca que os degraus largos descem para o pátio.
- **`gramados`:** dentro do retângulo do lote, o branco que chega até a borda vira grama, com o halo claro das linhas. O branco fechado dentro da casa (móveis, vazios) fica.
- **`fechados_apos_gramado`:** depois do gramado, o branco que sobrou dentro de um retângulo vira `para` (ex.: na Casa D, os pisantes desenhados só com o contorno viram Bege Bahia, e os triângulos fechados pelos X da projeção viram grama).
- **`retangulos` com `proteger_layers` e `apagar_linhas_layer`:** para piso branco sem polígono no PDF (os banhos da Casa D, brancos com hachura). O miolo branco das peças das layers protegidas (louças, bancadas, móveis) não muda, e os traços da hachura da layer indicada viram o material.
- **`texturizar_base.py` sem `esmaecer`:** a planta inteira recebe textura. Use `tolerancia` 4: com 12, o vidro #D6D6D3 entra no travertino #DCD9CA.

## Limitações conhecidas

- Os PDFs da Casa A que estão no Drive (001 Layout, 004, 005, 006, 021) **não têm** a layer `ARQ_PAREDE` nem o cinza 0.357. O PDF que gerou as bases atuais foi enviado direto na conversa e precisa ser trazido para cá. Sem ele, o script gera só a base sem texto e avisa que a v3 não foi gerada.
- As zonas do Térreo foram medidas sobre aquela base original (6001×3884). Se o PDF novo tiver outro enquadramento, confira no `_debug.png` antes de usar a v3.

## Teste

Validado num PDF sintético com layer `ARQ_PAREDE`: paredes, vidro fino branco, divisória de vidro em traço, traço sobre parede, folha de porta com arco, vidro na faixa do muro e texto. Resultado esperado e obtido: 1 vidro-forma, 1 vidro-traço, 1 descarte de cada tipo (parede, porta, muros), texto removido sem apagar a linha que estava sob ele, nenhum pixel azulado e rotação de 180° idêntica.

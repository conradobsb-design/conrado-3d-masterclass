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
# Casa A, desde os nomes e áreas (18/10/26): as imagens com rótulos já estão no quadro comum, em 3840 px
# (o Subsolo, desde 26/10/26, sai do final3840_casaa.py: não rodar rotulos_casaa.py Subsolo, que voltaria à versão antiga)
python rodape_entrega.py --no-quadro --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png \
    --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_rotulos.png --render 1Pavimento=../renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png
python pdf_entrega.py

# Casa B
python rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --render Subsolo=../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final.png
python pdf_entrega.py --config ../../POE642_CasaB/config_bases.json      # pranchas da entrega.pdf.ordem
python rodape_entrega.py --config ../../POE642_CasaC/config_bases.json --render Subsolo=../../POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_v3_retocado.png --render Terreo=../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_retocado.png
python pdf_entrega.py --config ../../POE642_CasaC/config_bases.json      # Subsolo e Térreo
# Térreo com o Barlavento nas piscinas (15/10/26): --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_bege_barlavento.png
# (e, nas Casas B, C e D, o ..._retocado_barlavento.png do Térreo)
```

**Versões de uma prancha (opções para o cliente):** `rodape_entrega.py --sufixo _x` grava `..._PH_{pavimento}_entrega_x.png`, sem tocar na prancha padrão; `--no-quadro` aceita um render que já está no quadro comum, na largura da prancha (como as montagens do `opcoes_1pav_casae.py`), e o usa como está, sem realinhar nem reamostrar (se o tamanho não bater, para com erro). No `pdf_entrega.py`, `--prancha PAVIMENTO=ARQUIVO` troca a prancha de um pavimento, e `--nome` e `--titulo` dão outro arquivo e outro título ao PDF. Casa E, 1º Pavimento em duas opções (16/10/26) e, depois, a terceira, nublado (19/10/26); o Subsolo e o Térreo (imagens finais já no quadro comum, com os rótulos) entram com `--no-quadro`:

```bash
C=../../POE642_CasaE
python rodape_entrega.py --config $C/config_bases.json --no-quadro --render Subsolo=$C/renders/POE642_CasaE_PH_Subsolo_v1_final.png
python rodape_entrega.py --config $C/config_bases.json --no-quadro --render Terreo=$C/renders/POE642_CasaE_PH_Terreo_v1_final.png
# (Térreo refeito em 20/10/26 com o pente fino inteiro, itens 44 a 63 do handoff; os carros ficam os prata da R12, decisão de 21/10/26;
#  em seguida, as três montagens do 1º Pavimento, com `python opcoes_1pav_casae.py`, as pranchas e os três PDFs abaixo)
python rodape_entrega.py --config $C/config_bases.json --no-quadro --sufixo _pb --render 1Pavimento=$C/renders/POE642_CasaE_PH_1Pavimento_v1_final_pb.png
python rodape_entrega.py --config $C/config_bases.json --no-quadro --sufixo _linhas --render 1Pavimento=$C/renders/POE642_CasaE_PH_1Pavimento_v1_final_linhas.png
python pdf_entrega.py --config $C/config_bases.json --prancha 1Pavimento=$C/entrega/POE642_CasaE_PH_1Pavimento_entrega_pb.png \
    --nome POE642_CasaE_Plantas_Humanizadas_opcao_PB.pdf --titulo "Casa E – Plantas Humanizadas (Subsolo, Térreo e 1º Pavimento) · opção P&B"
python pdf_entrega.py --config $C/config_bases.json --prancha 1Pavimento=$C/entrega/POE642_CasaE_PH_1Pavimento_entrega_linhas.png \
    --nome POE642_CasaE_Plantas_Humanizadas_opcao_Linhas.pdf --titulo "Casa E – Plantas Humanizadas (Subsolo, Térreo e 1º Pavimento) · opção linhas"
# opção nublado (19/10/26, referência do usuário; padrão dos 1º Pavimentos: entorno_esmaecido.py --nublado)
python opcoes_1pav_casae.py --opcao nublado
python rodape_entrega.py --config $C/config_bases.json --no-quadro --sufixo _nublado --render 1Pavimento=$C/renders/POE642_CasaE_PH_1Pavimento_v1_final_nublado.png
python pdf_entrega.py --config $C/config_bases.json --prancha 1Pavimento=$C/entrega/POE642_CasaE_PH_1Pavimento_entrega_nublado.png \
    --nome POE642_CasaE_Plantas_Humanizadas_opcao_Nublado.pdf --titulo "Casa E – Plantas Humanizadas (Subsolo, Térreo e 1º Pavimento) · opção nublado"
# desde 21/10/26, fim do pente fino: o nublado é a opção única (seção 16 das regras); as opções acima ficam no histórico
python opcoes_1pav_casae.py      # -> renders/POE642_CasaE_PH_1Pavimento_v1_final.png, sem sufixo
python rodape_entrega.py --config $C/config_bases.json --no-quadro --render 1Pavimento=$C/renders/POE642_CasaE_PH_1Pavimento_v1_final.png
python pdf_entrega.py --config $C/config_bases.json      # -> entrega/POE642_CasaE_Plantas_Humanizadas.pdf
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
- **Faixa com X (erro 3):** grama por quilting (`grama`), sombra dos muros por fator, e as linhas do PDF por `linhas_pdf`: os traços vêm de `get_drawings` por layer (o MuPDF não desliga as layers deste PDF no raster), sem as curvas de nível, desenhados em 8x e reduzidos, em cor clara.
- **Acesso e projeção da garagem (erros 4 e 5):** o cinza vira granito por quilting, normalizado e multiplicado pelo perfil por linha do granito ao lado; a projeção vem de `linhas_pdf` (X da DOC_LINHAS e só os traços curtos de tracejado das layers de parede), mascarada pelo granito do render.
- **Arcos sobre o granito (erro 6):** `arcos_no_granito` da Casa C, com a cadeia da Casa D.
- **Área descoberta (erro 7):** `apagar` (textura tecida normalizada vezes o campo de luz interpolado do entorno por convolução normalizada) tira o vaso; o X vem de `linhas_pdf`, mascarado pelo granito da base chapada (`granito_chapada`), que vale também na sombra funda.
- **Tanques (erro 8):** `apagar` tira a cuba do motor; o recorte dos tanques da Casa B é girado 90° e colado sem os px escuros (a parede de lá).
- **DCE (erro 9):** sombra da marcenaria tirada pelo campo de luz (blur anisotrópico, normalizado) sobre o nível do piso aceso por linha; piso por `textura`; cama (cobertor encurtado, girada) e criado-mudo do render da Casa C, com sombra curta à esquerda e embaixo.
- **Cooktops (erros 10 e 11):** o cooktop corrigido da Casa C, reduzido à caixa do PDF; o da gourmet do motor sai por `apagar` com a luz só da bancada.
- **Bancada da gourmet (erro 12):** quartzo por `textura` na cor da bancada do cooktop, vezes o perfil de luz por linha (e a luz 2D junto à geladeira); na caixa da cuba, só os px de madeira mudam.
- **Adega e lavabo (erros 13 e 14):** adega em travertino por `textura` com a sombra da parede de cima; no lavabo, bancada por `textura` com contorno e sombra, cuba da Casa B (`cuba`, virada para a torneira ficar em cima), o vidro do render deslocado para depois da bancada e o vaso da Casa C por `colar_vaso`.
- **Banco capitonê (erro 15):** as poltronas saem por interpolação vertical coluna a coluna (veios verticais); o banco é desenhado em 8x (corpo, vincos em losango, botões, borda) com a sombra deslocada e desfocada.
- **Segunda imagem:** `alinhar_fonte2` (SIFT + afim) leva a segunda imagem ao render; `armarios_fonte2` cola os armários dos quartos dela; `mesa_redonda` cola o conjunto da mesa (círculo do tapete e diferenças perto das poltronas, com o tom ajustado), tira a planta (`interpolar` em várias escalas, com o veio) e desenha as mesinhas.
- **Plantas sobre as mesas (erro 17):** tampos da segunda imagem (disco ou retângulo, tom ajustado pela mediana da madeira) e, na mesa de jantar, interpolação vertical coluna a coluna sob a planta e a sombra dela.
- **Piscina (erros 18 e 19):** água da segunda imagem onde qualquer das duas tem água (B - R > 30), fechada e com emenda gaussiana; a borda é a do render.
- **Escada da suíte master (erro 20):** `colar_retangulo` (retângulo da segunda imagem, tom ajustado num anel em volta, emenda gaussiana, paredes protegidas).
- **Bancos ao pé das camas (erro 21):** `bancos_camas` da Casa C (o vão de tapete do lado do pé), com os bancos da Casa B.
- **Cadeiras do escritório (erro 22):** cada cadeira a mais vira as mesmas linhas de piso limpo ao lado (réguas horizontais), colunas repetidas em espelho.
- **Elevador (erro 23):** a cabine da Casa B girada (porta à direita), ocupando a caixa inteira com 1 a 2 px de folga.
- **Degrau da prainha:** as mesmas linhas 36 px à esquerda (3 placas), vezes o fator por coluna da sombra da borda medido acima.
- **Louceiro, despensa e banho gourmet:** `sem_prateleiras` (granito por `textura` com a sombra das paredes por distância, folha da porta protegida) e `banho_gourmet` (divisória do box em 8x, chuveiro como em `chuveiros_bhm`).
- **Bancada da gourmet:** `area_molhada` aceita os pontos; `gourmet_pia` desenha o vaso em 8x e cola a folhagem do vaso do hall (só os px verdes, pré-multiplicados) com sombra curta.
- **Tapete orgânico:** `tapete_organico` (máscara do polígono do PDF por `mascara_pdf`; o que sai do círculo vira travertino de veios verticais na luz interpolada; poltronas e mesinhas protegidas).
- **Inox:** `inox` trata uma lista de caixas (cozinha e área de serviço).
- **Bancada da sala íntima:** `minibar` (quartzo por `textura` com o perfil de luz por coluna; cuba, torneira e frigobar desenhados em 8x; área molhada por `area_molhada`).
- **Chuveiros dos banhos 2 e 3:** `desenhar_chuveiro` (ducha, braço, canopla e sombra, como em `chuveiros_bhm`); `apagar` ganhou `lum_min` para a parede não escurecer a luz.
- **Armários em L:** `armarios_L` (polígono do PDF por `mascara_pdf`, areia com o veio emprestado, contorno nas faces livres).
- **Veios do DCE:** `veios_dce` (luminância da fonte sobre ela mesma desfocada, realçada, girada no comprimento da peça, vezes o tom desfocado da peça).
- **Pisantes:** `pisantes` (quilting do deck limpo, no tom da pedra e com a luz desfocada dela).
- **Torneiras da cozinha:** `torneiras_cozinha` (canopla, alavanca, bica e válvula em 8x).
- **Degrau do spa:** `degrau_spa` (fator por lado medido na aresta do fundo, aplicado ao contorno de fora).
- **Paisagismo:** `paisagismo` (trecho da touceira espelhado, máscara pela densidade da folhagem, contorno ondulado nos lados cortados, só sobre a grama).
- **Torneira lateral e chuveiro do WC DCE:** `lavatorio_gourmet` (base, bica, sombra e contorno da cuba em 8x) e `chuveiro_dce` (`apagar` + `desenhar_chuveiro`).

```bash
python retoque_terreo_casad.py ../../POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_render.webp --saida ../../POE642_CasaD/renders --nome POE642_CasaD_PH_Terreo_v1_retocado
```

## Retoque do Subsolo da Casa D: `retoque_subsolo_casad.py`

O render do Subsolo manteve o layout, mas aproximou a planta (~2,73 x a base reduzida a 2000 px). Os retoques são feitos no quadro do render, com as ferramentas do Térreo (`interpolar`, `textura`, `quilting`, a placa do chuveiro e os cromados), e a geometria vem do PDF pela cadeia da base (`pdf_cadeia`, com o afim do SIFT).
- **`apagar_largo`:** o `apagar` do Térreo para áreas largas: a luz do entorno vem de `interpolar` (várias escalas); `lum_min`/`lum_max` escolhem as amostras de luz (sem parede nem peças claras), e `escuros=True` troca também os traços escuros da máscara (contorno de símbolo).
- **Depósito (erros 1 e 2):** a faixa areia inventada e as juntas gigantes e manchas claras viram o granito tecido do próprio piso; a folha da porta e os arcos ficam.
- **WC DCE (erros 3 e 4):** `piso_box_wc` (ganho por canal até o tom do granito do resto do banheiro) e `trocar_chuveiro`.
- **`trocar_chuveiro` (erros 4, 8 e 9):** o símbolo do CAD sai (piso tecido do ambiente, com margem de piso para a luz), a parede volta ao preto do próprio miolo onde a cruz entrou nela, o toco que passou para outro piso sai, e `desenhar_chuveiro` desenha a ducha (placa da Casa A), o braço (horizontal ou vertical, retângulo do PDF) e a canopla, com sombra e brilho na escala do render.
- **Armário do DCE 1 (erro 5):** `armario_dce` tece (quilting) a madeira areia dos armários até o teto do Térreo retocado, ampliada na razão entre as escalas dos renders, com o veio no comprido.
- **Sauna (erros 6 e 7):** `sauna` refaz o miolo em Bege Bahia tecido do pátio, na luz do piso; o banco do PDF fica em dois tons (0,93 e 0,88) com as linhas de ARQ_ELEMENTOS FIXOS.
- **Cuba do vestiário (erro 10):** `cuba_vestiario` (aba, bacia em degradê, válvula e torneira com contorno escuro e sombra curta, em 8x).
- **Esteiras (erro 11):** `letreiros` tira o texto das lonas.
- **Pedidos depois do retoque (13 a 17):** `arcos_granito` (o arco preto sai e entra o cinza fino do PDF, só no granito da base chapada); `escada` (Bege Bahia refeito sem linhas, pisos do PDF escurecendo para baixo e sombra curta de cada espelho no piso de baixo); `sauna` com o banco no mesmo mármore do piso, níveis pela sombra e pela quina, luz chapada; `vasos` (polígono do PDF em 8 x: louça com volume, contorno, sombra e tampo fechado); `portas_vidro` (folhas de correr na espessura do PDF, com vidro, linha central, montantes e soleira).
- **18 a 20:** `vidros_fixos` (janela alta e vidro da sauna no desenho das portas de vidro); `elevador_entrada` (folhas da porta finas em inox, soleira de inox escovado com frisos-guia entre batentes de alumínio); `area_verde` (no quadro comum: jardim do Térreo retocado, alinhado pela rotina das pranchas, na faixa entre o pátio e o tracejado, e grama tecida na faixa de baixo; só o fundo branco fora da planta).
- **21 e 22:** `vidros_fixos` também nas janelas do WC DCE e do DCE 1 (com `restaurar`, o piso que a cápsula cobria); `portas_giro` (folha e arco do PDF, em 8 x; o que sai é tecido do piso do cômodo, protegendo só as paredes grossas na base e no render).
- **Escala e tracejado (erro 12):** `no_quadro` leva o retocado ao quadro comum das bases (3840 x 2160, inverso da cadeia, 2 x de superamostragem) e deixa branco o que fica fora da mancha da planta; `tracejado` desenha ali os traços da parede tracejada de fora (ARQ_PAREDE) direto do PDF, inclusive o trecho de baixo que o render cortou. Saídas: `_retocado` (quadro do render) e `_final` (quadro comum, com a planta sob a do Térreo).

```bash
python retoque_subsolo_casad.py ../../POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_v1_render.webp --saida ../../POE642_CasaD/renders --nome POE642_CasaD_PH_Subsolo_v1_retocado
```

## Retoque do Térreo da Casa E: `retoque_terreo_casae.py`

O render do Térreo da Casa E manteve a escala da base (o afim do SIFT é quase a identidade). Os retoques são feitos no quadro do render, um item por vez.
- **Lote (itens 1 e 2):** `lote` deixa a base alinhada fora do lote (à esquerda do gramado, entre o gramado e a linha tracejada da direita e abaixo do muro de baixo): saem a vegetação que passava para fora e a faixa de Bege Bahia inventada à direita dos pisantes, e voltam as linhas tracejadas. Os muros de cima e de baixo viram, linha a linha, a mediana de um trecho limpo (sem as folhas por cima).
- **Jardim interno (item 3):** `jardim_interno` acha a mancha das plantas ligada à floreira e a sombra delas (mais escura que o travertino limpo da mesma coluna) e refaz o que fica fora do retângulo do PDF: na escada, cópia da mesma coluna alguns tracejados acima (sem a diagonal; se preciso, dois degraus para o lado); no travertino, da mesma coluna mais abaixo (veios verticais). A diagonal da escada segue até a floreira e a borda da floreira entra em traço fino (`linha_aa`, desenhada em 8 x).
- **Tapete (item 4):** `tapete` troca a elipse do render pelo polígono do PDF (`mascara_pdf`, como na Casa D): o que sai vira travertino das mesmas colunas (faixa limpa acima, em espelho), na luz do travertino em volta e com a sombra dos móveis; o que entra vira tapete tecido. Os móveis são os polígonos brancos do PDF em volta (`caixa_render` acha cada um pela caixa), com folga.
- **Barras da varanda (item 5):** `barras` junta os quadradinhos brancos da ARQ_ELEMENTOS FIXOS em manchas, tira de cada uma o retângulo girado (largura pela área) e desenha em 8 x (`poligono_aa`, `linha_aa`): sombra curta, cinza da base com volume leve e contorno fino.
- **Elevador (item 6):** `elevador`, como nas Casas C e D: caixa branca e a cabine do Subsolo da Casa B, sem girar (porta embaixo), ocupando a caixa.
- **CPD (item 7):** `vaso_cpd` tira o vaso inventado com o `apagar_largo` do Subsolo da Casa D (granito tecido do próprio CPD, na luz do piso em volta).
- **Máquinas (item 8):** `maquinas` apaga o bloco de madeira (granito tecido) e leva cada metade do par de máquinas em inox do Térreo retocado da Casa D ao quadrado do PDF (afim subpixel), com sombra curta e contorno fino.
- **X da área descoberta (item 9):** `x_descoberta` desenha em 8 x os traços da DOC_LINHAS E PROJEÇÕES na janela, em cinza e traço fino, só onde o render é granito (escuro e quente).
- **DCE (item 10):** `dce` tira as peças do motor (`apagar_largo`, granito do quarto) e cola, por afim subpixel (`colar`), a cama, o criado-mudo e o armário do DCE do Térreo retocado da Casa D nos retângulos do PDF (cama e criado-mudo com `sombra_curta`).
- **WC DCE 1 (item 11):** `wc_dce` tira o vaso a mais (`apagar_largo`, luz só do piso limpo) e desenha o chuveiro do PDF com o `desenhar_chuveiro` do Térreo da Casa D.
- **Arcos no granito (item 12):** `arcos_granito`, o do Subsolo da Casa D na escala do Térreo: o arco escuro sai (granito tecido) e entra a curva do PDF em cinza fino, só onde a base chapada é granito.
- **Pontos do granito (item 13):** `pontos_granito` acha os pontinhos claros compactos no render original (contra a mediana de 11 px) e troca os fortes por um trecho vizinho de granito sem ponto.
- **Pilar (item 14):** `pilar` pinta o retângulo do PDF no preto da parede vizinha (borda antisserrilhada).
- **Lavabo (item 15):** `lavabo` limpa a bancada com as próprias linhas de quartzo e desenha a cuba esculpida (sombreamento do fundo inclinado, fenda, borda) e a torneira cromada saindo da parede da esquerda.
- **Arranjo do escritório (item 16):** `arranjo` cola (`colar_disco`) o centro de uma estrelítzia do jardim do render no círculo do PDF, com sombra curta.
- **Louceiro (item 17):** `veio_louceiro`, o `veios_dce` da Casa D: o veio (luminância sobre ela desfocada) do tampo da mesa de jantar, girado, realçado e repetido em espelho, sobre o tom desfocado da peça.
- **Escadas (itens 18 e 21):** `escada` (uma entrada em `ESCADAS` por escada, com o lado mais baixo) refaz o travertino da escada (mesmas colunas, sem linhas) e aplica, com 8 amostras por px, o tom de cada piso do PDF (mais escuro embaixo) e a sombra curta de cada espelho no piso de baixo.
- **Jardim de inverno (item 19):** `jardim_flores` devolve as folhas do render original numa faixa irregular fora da floreira (lados e baixo; nunca em cima), com degradê nas pontas e sombra curta, e cola as flores (recorte laranja das estrelítzias, com o matiz girado para outras cores).
- **Sem tapete na varanda (item 20):** `sem_tapete` apaga o retângulo do tapete (`apagar_largo`, Bege Bahia) fora dos móveis do PDF e devolve a sombra curta deles.
- **Vaso com tampo (item 22):** `vasos`, o do Subsolo da Casa D com a parede em qualquer lado e os números na escala deste render; antes, o símbolo do motor vira granito tecido.
- **Bancada do banho gourmet (item 23):** `bancada_gourmet` desenha a bancada do PDF no granito (contorno cinza fino, tampo um pouco mais claro, sombra curta), a cuba esculpida (`cuba_esculpida`, comum com o lavabo) e a torneira cromada.
- **Porta do hall externo (item 24):** `porta_hall` desenha a folha pequena (retângulo do PDF, nos tons da folha grande do render) e o arco dela (a curva da ARQ_PAREDE).
- **Brises (itens 25 e 33):** `brises` (um conjunto por janela do PDF: `BRISES` no escritório, `BRISES_GARAGEM` na lateral da garagem) cola um trecho da madeira da mesa de jantar em cada retângulo do PDF (`colar`), num tom sorteado, com contorno e sombra curta.
- **Carros (item 26):** `carros` recorta cada silhueta, refaz o granito embaixo (`apagar_largo`) e recoloca o carro com o afim de `CARROS["movimento"]` e uma sombra curta nova.
- **Adega (item 27):** `adega` dá veio ao U do PDF e desenha em 8 x as garrafas deitadas (gargalo, ombro e corpo), em fileiras por braço, com brilho e sombra curta.
- **Área de serviço (item 28):** `servico_bancada` dá veio ao armário do PDF e troca a bancada pelo quartzo tecido do tanque, com contorno fino.
- **Cozinha (item 29):** `cozinha` cola as metades do inox da Casa D nos quadrados do PDF e a madeira do louceiro nos armários dos lados (`colar`), com contorno fino.
- **Spa (item 30):** `degrau_spa`, o da Casa D com subpixel: o contorno de fora do degrau escurece por lado com o perfil das arestas do fundo.
- **Vidros da piscina (item 31):** `vidros_piscina` desenha as duas folhas do PDF como os vidros finos da Casa D (vidro, linha central, contorno).
- **Paisagismo (item 32):** `paisagismo`, o da Casa D: um trecho de touceira do render, recortado pela densidade da folhagem, com borda ondulada nos lados cortados, só sobre a grama.
- **Banco da varanda (item 34):** `banco_varanda` apaga o encosto do motor (`apagar_largo`, Bege Bahia) e cola a madeira da mesa de jantar no retângulo do PDF, em ripas, com contorno e sombra curta.
- **Barlavento nas piscinas (item 35):** `piscinas` troca a água (mancha da base chapada) pela pedra do `fontes_procedurais.barlavento` (peças de 14,5 cm, ondulada por `remap` com deslocamento suave), com a cor da água, luz chapada (sombra curta só nas bordas e no degrau da prainha), as cáusticas do render suavizadas e um brilho difuso.

- **Nomes e áreas (item 36):** `final_rotulos` leva o retocado ao quadro comum (3840 px, como na prancha) e escreve os rótulos do PDF pela regra do 1º Pavimento (`retoque_1pav_casae.rotulos_ambientes`). Os desvios ficam em `ROTULOS["ajustes"]`; as opções são `corpo` (1.0 é o do PDF), `quebra` (o nome em mais linhas, para ambiente estreito) e `cor` (no jardim interno, branco). O script inteiro grava também `_final.png`; com `--so-final`, o render dado já é o retocado e só a imagem final é gerada (em `--nome`). O retocado fica sem rótulos (é o contexto do 1º Pavimento na opção P&B).
- **Regras novas (19 e 20/10), depois do aprovado:** o `main` guarda o retocado dos itens 1 a 35 (`aprovado`) e só então aplica os itens das regras; `salvar_final(..., referencia=aprovado)` mede o alinhamento ao quadro comum no aprovado (`no_quadro_comum(..., referencia=)`), e o resto da imagem final fica igual, px a px. Por isso a imagem final sai do script inteiro; o `--so-final` sobre um retocado com itens novos realinharia a imagem toda.
- **Box do banho gourmet (item 37, R5):** `box_gourmet` apaga o traço escuro do motor (a coluna vira a do granito 2 px à direita) e desenha as duas folhas do PDF (`BOX_GOURMET["folhas"]`, pt) no eixo de cada uma, com 0,8 px: sombra suave à esquerda, a linha clara do vidro e a borda cinza fina do lado do chuveiro.
- **Sem arcos (item 38, R3):** `ARCOS["desenhar"]` e `PORTA_HALL["desenhar_arco"]` (falsos) tiram o arco cinza que os itens 12 e 24 desenhavam no granito e no hall; `sem_arcos` passa o `arcos.remover_arcos` só nos arcos fora do granito (`filtro`; o da folha pequena do hall fica de fora, pois não há arco do motor ali), com faixa de ±2 px e as linhas da DOC_LINHAS E PROJEÇÕES protegidas (`proteger`), para o X do hall seguir inteiro. `remover_arcos` ganhou os dois parâmetros (`filtro`, `proteger`); sem eles, faz o mesmo de antes. O alinhamento da imagem final vem do arquivo `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado_aprovado.png` (o aprovado de 15/10), porque a R3 muda itens antigos.
- **Escadas com linhas (item 39, R14):** com `R14_ESCADAS`, a rotina `escada` dos itens 18 e 21 só deixa o travertino limpo; `escada_linhas` desenha cada escada de `ESCADA_LINHAS["escadas"]` (caixa, bocéis de dentro e corte em pt do PDF; `baixo`, o lado do pé, define para onde vai a sombra; `inicio`, o lado do triângulo), com os parâmetros do `escada_r14` do Subsolo. Opções por escada (20/10/26, escada que desce): `viva` ("esquerda" ou "direita", o lado vivo do corte), `apos` ("tracejada", a projeção acima do corte, ou "esmaecida", o trecho abaixo dele, com os bocéis e as sombras) e `esmaecer` (a externa do alto usa 0,45, com o corte do PDF do Subsolo).
- **Carros (item 41, R12):** com `R12_CARROS`, `carros` apaga os três carros (como no item 26) e chama `carros_r12`: o modelo é a silhueta do carro prata (o do meio, `CARROS["r12"]["modelo"]`); a escala vem de 4,70 m no comprimento e 1,85 m na carroceria (a mediana das larguras de 35% a 85% do comprimento, sem os retrovisores), em px/m medidos pela cadeia do PDF; cada cópia vai ao centro de um carro do PDF (`centros_pdf`, pt), sem giro, com a sombra curta do item 26. Serve de modelo para as outras casas.
- **Grama (item 42, R1, R4):** `grama_referencia` lê o gramado da base chapada (#6E9150), mede a cor da grama num trecho limpo (`GRAMA["amostra"]`), separa as plantas com `texturas_escala.mascara_grama` e troca a grama com `texturas_escala.trocar_grama` (luz larga, sombras das plantas, desenho da biblioteca na escala); `GRAMA["cor"]` None mantém o tom do render (escolha do usuário); um BGR leva ao tom dado.
- **Bege Bahia (item 43, R1):** `bege_referencia` lê o #E8E8E8 da base chapada, troca os pontinhos escuros pequenos pela luz do lugar e passa o `texturas_escala.retexturizar` com os parâmetros do Bege Bahia do Subsolo (`BEGE`: força 1, raio 0,25 m, tom da foto, suavização 0,4 px).
- **Projeções da cobertura (item 44, R8, R9):** `projecoes` desenha, em pt do PDF levados pela cadeia do Térreo, as polilinhas de `PROJECOES["linhas"]` (o L da laje do gourmet + varanda, a laje da garagem e a faixa de cima) em tracejado cinza fino (traço e vão em pt), em 8 x, por cima de tudo, menos nas paredes pretas; `"ativo"` liga e desliga o item.
- **Cortinas (item 46, pente fino, item 1):** `cortinas` põe a cortina de linho de `_blocos/blocos.py` em cada conjunto de `CORTINAS["conjuntos"]`. O trilho vai de parede a parede (`com_pano=False`), e os panos ficam nos trechos dados (`com_trilho=False`), em pt do PDF levados pela cadeia do Térreo. `pousar_cortina` gira a peça com o trilho do lado do vidro ("direita" ou "esquerda") e a pousa em 8 x. Com o vidro embaixo ou em cima, a peça fica na horizontal (`trilho` = y do eixo, x inicial e final). Antes, os traços do motor saem: no escritório, a faixa volta ao travertino (`CORTINAS["limpar"]`); na fachada de baixo do living, as linhas logo acima entram espelhadas (`CORTINAS["limpar_faixas"]`).

```bash
python retoque_terreo_casae.py ../../POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_render.webp --saida ../../POE642_CasaE/renders --nome POE642_CasaE_PH_Terreo_v1_retocado
python retoque_terreo_casae.py ../../POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado.png --so-final \
    --saida ../../POE642_CasaE/renders --nome POE642_CasaE_PH_Terreo_v1_final
```

## Barlavento nas piscinas das Casas A a D: `piscinas_barlavento.py`

O mesmo revestimento da Casa E (item 35 do `retoque_terreo_casae.py`) num render já retocado: a água vira a pedra do `fontes_procedurais.barlavento` sob a água verde-azulada clara, com luz chapada (sombra curta só junto às bordas), a grade ondulada pela refração, as cáusticas do render suavizadas e um brilho difuso.

- **Água:** pela cor do render (B − R > 7, G − R > −5, B > 95), em manchas de 300 px ou mais, com os reflexos e as linhas finas dentro dela. Espreguiçadeiras e tracejados de projeção ficam por cima.
- **Degraus:** as linhas do projeto dentro da água, da base chapada (`--chapada`) alinhada ao render pela base com texturas (`--base`). As máscaras são feitas na resolução da base e reduzidas por área. A fronteira entre os dois tons de água da base (fundo e prainha) também conta como degrau.

```bash
# da pasta projetos/
python3 POE642_CasaA/scripts/piscinas_barlavento.py POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_retocado.png \
    POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_retocado_barlavento.png \
    --base POE642_CasaC/bases/POE642_CasaC_BASE_Terreo_v3_texturas_16x9.png --chapada POE642_CasaC/bases/POE642_CasaC_BASE_Terreo_v2_16x9.png
python3 POE642_CasaA/scripts/piscinas_barlavento.py POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_bege.png \
    POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_bege_barlavento.png \
    --base POE642_CasaA/bases/POE642_CasaA_BASE_Terreo_v6_16x9.png --chapada POE642_CasaA/bases/POE642_CasaA_BASE_Terreo_v6_16x9.png
```

As pranchas do Térreo e os PDFs das quatro casas foram refeitos com essas imagens (`rodape_entrega.py --render Terreo=..._barlavento.png` e `pdf_entrega.py`).

## Casa D: dreno em linha e degraus em níveis: `piscina_dreno_casad.py`

Refaz a água da piscina e do spa da Casa D a partir do render retocado (pedido do usuário depois do Barlavento v1):
- **Borda e dreno** (render de referência do usuário): a água vai até o contorno do projeto, com a sombra curta da borda. Em volta do conjunto piscina + spa, uma capa de pedra da largura da faixa entre os dois (`capa`), e na borda de fora dela o dreno em duas linhas finas paralelas (`dreno`: afastamento e largura de cada uma), só no contorno de fora do conjunto, com cantos em esquadro (distância de tabuleiro).
- **Borda alta:** a capa fica acima da água. A sombra dela na água é a máscara do que não é água varrida na direção do sol (`sol`, `sombra`: força, comprimento e penumbra), limpa e uniforme; mais a linha do desnível junto à água (`desnivel`) e a quina da capa iluminada (`nariz`).
- **Degraus em níveis:** as áreas da água vêm da base chapada alinhada (componentes entre as linhas do projeto). Cada uma tem uma profundidade (`D["areas"]`), e a cor da água muda com ela por absorção (`absorcao`, BGR por m; o tom aprovado vale no fundo, `prof_ref`). O degrau é a troca de tom, com uma luz fina na quina de cima (`quina`) e uma sombra curta ao pé (`pe`).
- A pedra, a refração, as cáusticas e o brilho são as funções do `piscinas_barlavento.py` (`pedra_ondulada`, `causticas`, `brilho_diagonal`).

```bash
# da pasta projetos/
python3 POE642_CasaA/scripts/piscina_dreno_casad.py      # -> POE642_CasaD/renders/..._Terreo_v1_retocado_barlavento_v4.png
```

## Pavimento de baixo esmaecido em volta: `entorno_esmaecido.py`

Para um pavimento superior cujo PDF não traz o térreo (Casa E · 1º Pavimento): leva o render aprovado do pavimento de baixo ao quadro 16:9 comum (o `no_quadro_comum` das pranchas), clareia (`--clarear`, padrão 0,75) e tira saturação (`--saturacao`, padrão 0,4: fica 40% da saturação), e põe por cima a pegada do pavimento de cima em cor cheia (o que não é branco, fechado e com os furos preenchidos). `--fora` devolve ao contexto uma área branca de fora presa na pegada (px de uma prévia de 2000 px). As linhas tracejadas do lote continuam por cima. Com `--base-cima`, a primeira imagem é o render do pavimento de cima: ele vai ao quadro da base dele e entra por cima integralmente, na pegada tirada da base; `--largura` define a saída (3840 para a prancha) e `--recorte` salva também a camada do térreo esmaecido com a área do pavimento de cima transparente.

```bash
python3 entorno_esmaecido.py ../../POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png \
    ../../POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado.png \
    ../../POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png \
    ../../POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v4_entorno_16x9.png --fora 912 752 1096 816
```

## Retoque do 1º Pavimento da Casa E: `retoque_1pav_casae.py`

Retoques sem IA no render v1 (fundo branco), no quadro do render; as posições vêm da prévia de 1800 px (as coordenadas da `config_bases.json` e do PDF), levadas ao render pela base alinhada (`vis2r`). O Térreo esmaecido entra depois, pelo `entorno_esmaecido.py`.
- **Banho master, floreira (item 1):** trecho do jardim interno do Térreo aprovado, girado, no retângulo das plantas do PDF, com contorno fino e sombra curta.
- **Banho master, chuveiros (item 2):** a ducha de parede e o registro saem (`apagar_largo`, quartzito do próprio banho) e entram as placas de teto da Casa A (`placa_teto`).
- **Bacias das suítes da esquerda (item 3):** sem retoque; o PDF desenha duas bacias suspensas costas com costas, como o render.
- **Copinha (item 4):** `bancada_copinha` troca a areia da bancada (retângulo da ARQ_BANCADAS, pela cadeia do PDF) pelo Bege Bahia tecido da varanda do próprio render, somando a diferença de cor na luz da bancada (perfil por linha; as bordas com a parede e a linha da frente pela luminância); `cuba_redonda` desenha a cuba da Casa A no círculo do PDF, com a torneira no cromo das cubas do Térreo.
- **Vazios (item 5):** `vazios` deixa os dois vazios brancos (250, como os da Casa A; pedido do usuário): o cinza do render perto do retângulo e, nos lados com guarda-corpo, a faixa até o vidro do PDF. Por cima, cada traço do X tracejado do PDF (DOC_LINHAS E PROJEÇÕES) em cinza médio (147), e o guarda-corpo de vidro (retângulos de 2 cm da ARQ_ELEMENTOS FIXOS) numa faixa fina de 1,6 px no vidro fino aprovado (vidro e contorno).
- **Arcos das portas (item 6):** `arcos_portas` desenha as curvas da ARQ_PAREDE do PDF (como o `arcos_granito` do Térreo, sem apagar nada: o motor não pôs arco nenhum) e a folha da porta pivotante do hall sobre o vazio; `pintar_traco` usa o cinza fino (160, 161, 160), sem mexer nas paredes.
- **Cortinas (item 7):** `cortinas` junta os arcos da ARQ_LOUÇAS E METAIS em traço de 0,85 (as ondas do PDF) em trechos e desenha cada trecho pela cadeia do PDF, em 8x, no linho off-white (210, 221, 230 BGR), traço de 0,85 px, com a sombra curta (`sombra`). Os vasos das varandas (item 8) ficam, a pedido do usuário.
- **Shaft (item 9):** `shaft` desenha os traços da DOC_LINHAS E PROJEÇÕES dentro da caixa do shaft no PDF (retângulo e X tracejado) em cinza (147), finos, só sobre a parede.
- **Fachadas das suítes (item 10):** `fachadas` refaz a faixa da parede de cada fachada pelo PDF: os intervalos com desenho da ARQ_PAREDE na faixa (onde não há, como nos banhos da direita, nada muda), parede (cinza no PDF) em preto, vão como soleira no Bege Bahia tecido da varanda; as folhas de correr (pares de meias-folhas de 1,42 e os montantes das pontas) no vidro aprovado, com brilho no meio e contorno fino, e as janelas dos banhos. Antes, o sombreado do caixilho no piso de dentro some (ganho por linha até a luz do piso a 5–10 px, só nas linhas de vão). Os brises (colunas de lâminas da ARQ_ELEMENTOS FIXOS; lâminas de 0,9 px, sem desenhar uma a uma para não dar moiré) entram como faixa de bronze com bordas escuras, brilho no meio e sombra curta.
- **Cubas no lugar do PDF (item 11):** `cubas_banhos` leva a cuba do próprio render (com a torneira) ao centro do recorte da ARQ_BANCADAS do PDF, com subpixel e borda suave (banhos das suítes da direita: para a direita; os dois banhos da esquerda, costas com costas: para a esquerda); o lugar antigo recebe o trecho limpo do tampo ao lado, nas mesmas linhas, espelhado, na luz interpolada entre as colunas vizinhas.
- **Bancos em frente às camas (item 12):** `bancos_camas` acha no PDF os retângulos de banco (altura 22,7, largura de cama) encostados numa cama; o pé da cama do render é a primeira queda abaixo de 88% do edredom na coluna do meio (a borda do tapete, mais escura, fica mais adiante); o banco entra a 1 px dele, na largura e altura do PDF, estofado em bege: almofadas lado a lado (uma a cada 1,7 vez a altura) com o tecido, o volume e as costuras da almofada do meio do assento do sofá da sala íntima do render (normalizada, relevo 1,8), uma trama fina (ruído suave de 4%), contorno bege escuro e a sombra curta do `BANCO_VARANDA` do Térreo.
- **Torneira de piso da banheira (item 13):** `torneira_banheira` ajusta uma elipse ao branco da banheira do render (maior que a do PDF), leva a base da torneira do PDF (ARQ_LOUÇAS E METAIS) à mesma posição relativa ao contorno, e desenha em 8x a base redonda, a bica em diagonal e a alavanca no cromo das cubas, com a sombra curta das placas de teto.
- **Nomes e áreas dos ambientes (item 14):** `rotulos_pdf` lê no PDF cada nome de ambiente e as linhas logo abaixo ("A: 17 m" e o "2" sobrescrito), com o texto, o corpo e a origem de cada linha; `rotulos_ambientes` escreve cada linha igual ao PDF, na posição do PDF (só os que caem sobre móvel vão ao piso livre mais próximo, em `ROTULOS["ajustes"]`, autorizado pelo usuário), no corpo do PDF (8 pt e 5,3 pt) levado à escala da imagem e 30% maior (`ROTULOS["escala"]`, com as linhas afastando na mesma escala, em volta do centro do bloco), em Inter Regular, desenhada em 4x e reduzida, em preto; no granito marrom (máscara `granito`), em cinza. O script salva também `_sem_rotulos.png`, que vai à montagem; lá os rótulos são escritos de novo na resolução da prancha.

- **Pente fino de 20/10/26:**
  - item 1, R3: `ARCOS["sem_arco"]`, os arcos não entram mais e fica a folha da pivotante; a floreira usa o Térreo aprovado de 15/10 (`TERREO_FLOREIRA`);
  - item 2, escada (R14): `escada_r14` copia o travertino limpo do Térreo aprovado (abaixo do jardim) para a caixa da escada do PDF e chama o `escada_linhas` do Térreo com a cadeia deste PDF (`p2r`): 19 pisos, triângulo no topo apontando a descida, esmaecida (0,45) depois do corte do Térreo;
  - item 3, boxes: `boxes_continuos` apaga o traço do motor numa faixa em volta do eixo do vidro do PDF (cada px que foge da média dos dois lados vira essa média) e desenha o vidro do box do banho gourmet do Térreo, de parede a parede, com a borda e a sombra do lado do chuveiro (`BOXES`);
  - item 10, cortinas: `cortinas_linho` troca as ondas do item 7 pela cortina de linho da biblioteca (`blocos.cortina` + `pousar_cortina` do Térreo): o pano em cada trecho ondulado do PDF e, por quarto, o trilho de parede a parede (a parede procurada numa coluna 3 px para dentro do quarto; trilhos sobrepostos viram um);
  - itens 9 e 7, portas, janelas e vidros finos: `esquadrias_1pav` faz nas zonas de `ESQUADRIAS_1P` o item 8 do pente fino do Térreo (os brancos finos da ARQ_PAREDE limpos e redesenhados pelo `esquadria_desenhar` de lá). A limpeza é a do Térreo com quatro ajustes (`esquadria_limpar_1p`): a parede é o escuro grosso que não é verde; ela fica fora do retângulo do PDF; do lado dela vem o piso mais perto do outro lado; e faixa e fonte podem mudar por zona (o brise das E23, o X do vazio do hall, o vão da P13). As folhas saem em branco suave com contorno fino, como as portas do Subsolo da Casa E;
  - item 11, vinílico na escala (R4): `vinilico_escala` troca as réguas de ~40 cm do motor por réguas de 20 cm (`reguas_vinilico`: fiadas de 1,2 a 1,8 m, juntas desencontradas, tom por régua e o veio do próprio vinílico do render, em 4x), na luz do piso medida mais larga atravessando as réguas, só no piso (fora tapetes e objetos que fogem da luz do piso). Depois, onde a luz larga fica abaixo da mediana, ela sobe 70% do caminho (pedido de 21/10: "clareia um pouquinho o vinílico onde está escurecido");
- item 12, Bege Bahia das quatro varandas como a referência (seção 18: "segue a foto de referência na escala: desenho em nuvens visível, no contraste dela, e tom quente"): `BEGE_VARANDAS_1PAV` e `bege_varandas_1pav`, com a rotina do item 9 do Térreo (`bege_na_referencia`, os números do item 43 do Térreo da Casa E), para os dois pavimentos ficarem iguais (média BGR ~186, 210, 229 nas varandas e no Bege do Térreo). O motor fez as varandas num bege claro e rosado com veios grandes de mármore. As áreas são as manchas do #E8E8E8 da base chapada que contêm os pontos `sementes`, uma por varanda (o hall da caracol, o quarto e o banho de serviço têm a mesma cor na base e não são varanda), fechadas em 5 x 5 onde o render é piso claro. Os caixilhos e a linha do guarda-corpo ficam (fogem da luz).
- item 13, projeções da cobertura e do pergolado em tracejado (R8, R9): `PROJECOES_1PAV` e `projecoes_1pav_final`, chamada por `rotulos_casaa.final_imagem` (chave `projecoes` do 1º Pavimento), depois do Térreo nublado e do tracejado do lote, no quadro de 3840 px: as linhas caem quase todas fora da pegada do pavimento, e o ajuste é branco ali. No PDF, as duas estão em tracejado de 5,67 pt: a cobertura na ARQ_CONTRAPISO, em preto (notas "PROJ. COBERTURA"), em dois contornos fechados (o de fora é o L do Térreo, com a linha de 1290 pt parando em 1344 pt; o de dentro, 34 pt para dentro) e dois trechos curtos entre eles, à direita; o pergolado na ARQ_PERGOLADO ("PROJ. PERGOLADO"), a grade de vigas de 20 cm à esquerda da suíte 2. As retas saem do PDF (`retas_tracejadas`: os traços curtos de cada camada juntados por coordenada enquanto o vão for de até 6 pt, só as retas com 5 traços ou mais) e são refeitas em tracejado (`tracejar`) no traço do item 4 do Térreo (`PROJECOES_A`: 8,5 pt de traço, 4,25 de vão, 0,55 px na escala do ajuste, cinza 150, força 0,85), menos nas paredes pretas. A imagem com ajustes não muda.
- item 14, portas de vidro de correr finas, em dois planos (seções 4 e 18): `VIDROS_1PAV` e `vidros_1pav`, como os vidros do Térreo (item 5, `vidros_finos`). No PDF (ARQ_PAREDE), cada fachada de suíte tem dois planos de folhas de correr (cada folha em duas lâminas de 1,4 pt, com as peças de 2,8 x 4,5 pt nas pontas): o de fora, junto à varanda, e o de dentro, ~3 px para dentro; na master, o plano de fora segue pela frente do banho master. O motor fez em cada fachada um "tubo" branco de ~8 px. O tubo sai (`esquadria_limpar` da Casa E, peça a peça, do plano de fora para o de dentro, para o espelho não levar o tubo; entre os planos fica o Bege Bahia da varanda) e as peças do PDF entram finas (`esquadria_desenhar`). Antes, os tracinhos das cortinas saem (`tracinhos_cortina`), para o espelho do plano de dentro não os copiar. Na suíte 1 os dois planos são zonas separadas, para a janela do banho 1 ficar de fora; as janelas dos banhos 1 e 2 e a da escada ficam como estão. Ordem na lista `ITENS`: o Bege Bahia das varandas (pf12) passa para logo depois do vinílico (o espelho leva o Bege novo; o resultado dele é o mesmo, px a px), e o pf14 roda antes das cortinas (pf10), como na Casa E.
- item 14, complemento (usuário, 21/10/26: "pode fazer as janelas finas também"): `JANELAS_1PAV` e `janelas_1pav` (pf14b, logo depois das portas). As janelas que tinham ficado como o motor fez, em "tubo" claro, passam pela mesma rotina (seção 4: vidro claro com a linha central, caixilho de alumínio, peitoril em pedra, retornos da parede em preto). Cada zona é o vão branco da ARQ_PAREDE da janela: banhos 3 (para fora), 2, 1 e de serviço, a janela da escada e o vidro da fachada de baixo (saleta e quarto de serviço, duas folhas em dois planos); no banho 2, também o vidro do plano de fora da fachada, que passa pela frente dele. As peças brancas finas saem de fora para dentro (`esquadria_limpar`) e o vão é redesenhado (`esquadria_desenhar`). As duas linhas no alto, à direita, estão dentro de um vazio e não são janela: ficam.
- item 15, soleiras (R13): `SOLEIRAS_1PAV` e `soleiras_1pav`, com `desenhar_soleiras` (a do Térreo e do Subsolo). Conferidas porta a porta numa folha de recortes (PDF, base chapada e render) e pela cor do próprio PDF no meio de cada vão. Sem soleira: as 11 portas de giro (o travertino da circulação, o vinílico das suítes ou o cinza do quarto de serviço e da saleta atravessam o vão) e o elevador (no 1º Pavimento o travertino do hall vai até a cabine; a seção 4 pede soleira de inox no elevador, mas a R13 manda representar só onde o PDF tem). Com soleira: a porta de correr da saleta para o quarto de serviço (o vão branco da ARQ_PAREDE, com a folha dentro); o motor fez uma caixa clara ocupando o vão. O vão vai a Bege Bahia na escala, no tom da referência, com as faces da parede em cinza fino, e a folha de correr entra fina por cima, no retângulo do PDF (clara, `folha`, com o contorno no cinza das faces; a do motor tinha um ponto preto na ponta). Os vãos brancos dos banhos 3 e de serviço são janelas de correr (0,76 e 0,56 m, na parede de fora e na da varanda), não portas: ficam.
- item 16, o "²" dos 22 rótulos: conferido, sem mudança. A regra de 20/10 (o "2" sobrescrito logo depois do "m", item 2 do Térreo) está na rotina compartilhada dos rótulos (`retoque_1pav_casae.rotulos_ambientes`), que roda em todo ciclo: os 22 rótulos do 1º Pavimento (o elevador sem área) já saem com o "m²" certo na prancha.
- o Térreo nublado por dentro (pedidos do usuário de 21/10/26: "precisamos mostrar a parte do Térreo enovoada"; na escada em U, "uma pequena parte dessa escada deve estar enovoada, pois pertence ao Térreo, bem como a parte branca que se refere à parte verde"; e a caracol "não pode ter o branco (...) a escada deve estar aparentando uma escada", com os degraus dentro do círculo): `TERREO_1PAV`, cujas máscaras o `so_1pavimento` grava (`renders/..._terreo_janelas_mascara.png` e `..._terreo_troca_mascara.png`) e o `rotulos_casaa` leva ao quadro pelo mesmo afim da pegada (`no_quadro_fixo(..., extras=)`, chave `terreo` do 1º Pavimento). No `nublar`: nas janelas (caixas dos dois vazios, do poço da escada em U e da abertura da caracol), o que é cinza neutro claro multiplica o Térreo nublado (`JANELA`: o branco vira o nublado; o X tracejado, os contornos, o anel e os bocéis ficam por cima, mais escuros, sem halo; o que tem cor, como os degraus, fica); na troca (os degraus 1 a 7 até a diagonal do corte do Térreo, o polígono do trecho cheio de lá), o Térreo nublado entra inteiro. Nos vazios aparecem as salas do Térreo; no poço, o jardim; na caracol, a caracol do Térreo. A caracol (`caracol_1pav`, item 3) mudou: o trecho cheio para no anel (`r_anel` 52 pt, o raio dos degraus no PDF; a madeira do motor ia até ~58 pt, por fora do anel); por fora do anel, no quarto cheio, entra o travertino da chegada (o piso logo depois, no mesmo raio, em espelho); o resto do círculo e a abertura ficam brancos (o nublado na final), sem os bocéis tracejados, com os 14 bocéis do PDF em traço contínuo suave (`bocel_terreo`); o anel é refeito inteiro.
- os cobre-leitos (pedido do usuário de 21/10/26: "precisamos humanizar os cobre-leitos. As camas estão ainda com o desenho técnico do PDF. Precisamos melhorar a representação. Adote das referências da biblioteca"): `CAMAS_1PAV` e `camas_1pav` (chave `cl`, logo depois do item 8, que desenha a cama do quarto de serviço). Nas seis camas (casal nas suítes 3, 2 e master; solteiro nas duas da suíte 1 e no quarto de serviço), o retângulo branco com o contorno dos travesseiros e a dobra em triângulo dá lugar à roupa de cama da referência da biblioteca (linha 5 da cartela de elementos, guardada como opção em 19/10): `elementos.roupa_de_cama`, desenhada em 4 x e reduzida por área, com o lençol e o edredom brancos (bordas caindo, rugas leves), dois travesseiros cinza-claros junto à cabeceira e dois bordô na frente (um e um no solteiro), com volume e sombra curta, a dobra do lençol com a sombra da borda e a manta bordô atravessada na metade dos pés (no solteiro, a faixa), com as dobras. A cabeceira fica do lado dos travesseiros do PDF (em cima na suíte 3 e no quarto de serviço; embaixo nas outras). O colchão é o retângulo do PDF menos a borda da cama (1,7 pt); nos lados e nos pés, a borda vem da moldura do próprio render (`borda_da_cama`: a linha mais escura a até 4 px da do PDF, ou 7 px se não aparece, e dela para dentro o primeiro claro, a 80% do caminho até o colchão), porque o render desloca as camas 1 a 2 px (na suíte 3, os pés estão 5 px além, com a moldura dupla); na cabeceira, contra a parede, fica a do PDF. A cartela de elementos ganhou, na linha 5, a nossa roupa de cama ao lado da referência. Depois (usuário, 21/10/26: "aplique a mesma roupa de cama"), a cama de solteiro do quarto do motorista, no Térreo: `CAMA_MOTORISTA` e `cama_motorista` (chave `cl` do Térreo, logo depois dos itens 11 e 12, que desenham a cama), pela mesma `pousar_camas` (a rotina das camas do 1º Pavimento, agora com o pavimento e a config por parâmetro), com a cabeceira em cima, contra a parede, e sem a busca da moldura: ali a cama foi desenhada por nós no retângulo do PDF (`MOTORISTA["cama"]`), e o colchão é esse retângulo menos a mesma borda de 1,7 pt.
- o quartzito Carrara nas ilhas e bancadas (pedido do usuário de 21/10/26: "use o quartzito Carrara nas ilhas e bancadas"), nos três pavimentos: `CARRARA_BANCADAS` e `carrara_bancadas(out, pavimento)` (chave `carrara`: no Térreo, depois das soleiras e antes das projeções; no Subsolo e no 1º Pavimento, antes do `so_...`), com a pedra de `fontes_procedurais.quartzito_carrara` (por código, como o granito da referência: não há foto do Carrara na biblioteca). As peças são os preenchimentos brancos da ARQ_BANCADAS do PDF (os cinza ficam de fora), menos as estreitas (lado menor abaixo de 0,30 m: os peitoris das janelas, na mesma camada): 7 no Térreo (a ilha gourmet em U, a ilha e a bancada da cozinha, o lavatório, a bancada dos tanques, o lavabo e o banho do motorista), 6 no 1º Pavimento (os banhos e a bancada com a cuba redonda na circulação, junto ao quarto de serviço) e 3 no Subsolo (os banhos feminino, masculino e de serviço). Em cada peça, a pedra antiga dá lugar ao Carrara, com os veios ao longo do lado maior e a luz do lugar (a luz desfocada da pedra antiga, 2,5 px: as sombras curtas, a sombra junto às paredes, a cuba esculpida do lavabo). É pedra o que está perto do tom dela, em Lab (o claro-escuro pesa menos que a cor, e o mais escuro, dos traços, mais que o mais claro); o tom é o claro-escuro mais frequente da peça abaixo do branco da louça (238), porque nas bancadas pequenas a cuba chega quase à borda e puxava a mediana. Ficam por cima o inox, o cooktop, as linhas da área molhada e a louça: nas peças da ARQ_LOUÇAS E METAIS (com o que os traços fecham) o teste é estrito, para a pedra em volta das cubas do render (2 a 3 px fora das do PDF) virar Carrara; e o miolo das cubas (o que os traços fecham, longe da borda ou sobre uma louça do PDF, mais claro que a pedra) fica. O Carrara é um tom abaixo do branco da louça, para as cubas brancas se destacarem. No PDF, a ilha gourmet do Térreo tem um cooktop de 5 bocas que o render não desenhou: ali fica o Carrara, como o resto da ilha.
- a ilha da cozinha do Térreo (pedido do usuário de 21/10/26: "troque as banquetas, melhore a representação da ilha e troque o cooktop"): `ILHA_COZINHA`, em duas etapas em volta do Carrara. Antes (`ilha_cozinha_limpar`, chave `ilha_limpar`): a faixa das três banquetas do motor (manchas brancas) volta ao granito, copiado do piso 17 px acima, com a borda suave, só fora do tampo; e o cooktop do motor (contorno rosado, 4 bocas) volta à pedra da ilha (a mediana do tampo), até a borda dele, para o Carrara texturizar. Depois (`ilha_cozinha_pecas`, chave `ilha_pecas`, pela `desenhar_ilha`): o contorno fino do tampo (cinza 126, 0,5 px) e a face de dentro das duas laterais em cascata do PDF (as faixas de 4 cm das pontas da ilha na ARQ_BANCADAS, em cinza mais claro); o cooktop do PDF (ARQ_LOUÇAS E METAIS: 5 bocas, 49,9 x 28,3 pt, 0,88 x 0,50 m) com o bloco "cooktop_inox_5_90" da biblioteca, o mesmo da Casa E, na altura do PDF, até 10% de alongamento, centrado, com os botões embaixo (do lado de quem cozinha; as banquetas ficam em cima) e o anel azul da chama em inox; e as três banquetas do PDF (ARQ_LAYOUT HUMANIZAÇÃO: círculos de 22,6 pt, 0,40 m, metade sob o tampo) com o bloco "banqueta_linho" (madeira clara e linho cru, a referência do usuário da ilha gourmet da Casa E), no tamanho e no centro delas, girado de 180° (a frente do assento sob o tampo), com a sombra curta da biblioteca, só fora do tampo. Na final de 3840 px, `rotulos_casaa.final_imagem` chama `ilha_cozinha_final`, que redesenha o contorno, o cooktop e as banquetas nítidos (sem as sombras, que vêm do ajuste ampliado).
- os boxes dos chuveiros com as folhas contínuas (pedido do usuário de 21/10/26: "boxes dos chuveiros com folhas contínuas"), nos três pavimentos: `BOXES_CONTINUOS`, `folhas_box`, `limpar_linha` e `boxes_continuos(out, pavimento)` (chave `boxes`, logo depois do Carrara; no Térreo, depois da ilha). No PDF (ARQ_LOUÇAS E METAIS), os 10 boxes da casa (3 no Subsolo: banho de serviço, ducha e banho feminino; 2 no Térreo: banho da varanda e motorista; 5 no 1º Pavimento: banhos 1, 2, 3, master e de serviço) são de correr: duas folhas desencontradas, cada uma um par de traços de 0,21 pt a ~0,55 pt um do outro (`folhas_box` acha os pares de 30 pt ou mais e junta as duas folhas mais próximas de cada box), e o trilho em tracejado no vão, na linha do meio, até a parede (os traços curtos de 0,2 a 10 pt a até 1,6 pt da linha, além das folhas). No 1º Pavimento o vidro era o do motor: quase sumindo nos banhos 1 e de serviço; no master, com falhas, um trecho escuro no meio e uma linha cheia com degrau no vão; 2 a 3 px fora do PDF. No Subsolo e no Térreo, o nosso, de antes, sem o trilho, com restos de um vidro mais antigo (na ducha, uma faixa clara 4 a 6 px acima). O traço antigo volta ao piso, nas folhas e no vão, cada trecho por si (`limpar_linha`): a faixa do PDF e as linhas de px perto dela (até 4 px entre uma e outra, até 7 px da linha do meio) que destoam do piso a 2 px dos dois lados, no mesmo sentido, em 60% do comprimento ou mais (a borda de um vaso junto ao box, mais curta, não conta), com o antialias; cada px que foge mais de 6 níveis da reta entre o piso dos dois lados vira essa reta, menos nas paredes (as manchas escuras de 40 px ou mais: o trecho escuro do master, pequeno, sai), onde os dois lados não são o mesmo piso (a planta junto ao box do master) e nas louças do PDF (com 2 px de folga). Entram as duas folhas inteiras, com o vidro aprovado (`vidro_box`) e a sombra cinza fina ao lado (embaixo nas horizontais, à esquerda nas verticais), e o trilho em tracejado cinza fino (cinza 150, 0,6 pt) nos traços do PDF, juntados.
- as paredes pretas revistas (pedido do usuário de 21/10/26, com um trecho do jardim do Térreo ao lado da garagem: "melhorar o acabamento das paredes em preto. revise todas as paredes e deixe-as em perfeito estado"), nos três pavimentos: `PAREDES_PDF` e `paredes_perfeitas(out, pavimento)` (chave `paredes`, logo depois dos boxes: no Térreo, antes das projeções e da pedra portuguesa; no Subsolo e no 1º Pavimento, antes do `so_...`). As paredes do PDF são os preenchimentos cinza da ARQ_PAREDE (paredes e pilares; janelas e portas são vãos), desenhados em 4 x e reduzidos. O motor tinha falhas dentro delas (no Térreo, 1.527 px: a grama aparecendo em três trechos da parede da direita da garagem; 1.074 px no 1º Pavimento; 320 no Subsolo), pontas tortas e sobras para fora (o preto, abaixo de 60, a até 4 px da parede, onde ela cobre menos de 15%). As sobras voltam ao que está em volta (cv2.inpaint, com a parede também na máscara, para não puxar o preto) e as paredes são repintadas no preto delas (6, 6, 6), no contorno exato. No Térreo, a pedra portuguesa do acesso (pente fino 11), desenhada depois, muda um pouco de assentamento, porque o muro do lote ao lado dela mudou.
- as bordas do acesso de veículos (pedido do usuário de 21/10/26: "melhorar o acabamento das bordas desse acesso"): `ACESSO_BORDA`, `acesso_alfa` e `pedra_final` (na final de 3840 px, chamada pelo `rotulos_casaa`). A pedra em leque era redesenhada na máscara do ajuste ampliada, binária: a borda saía em degraus de ~2 px, com as pedras cortadas secas e uma franja clara da pedra do ajuste sobre a grama. Agora, onde o acesso encosta na grama, a borda é o contorno do acesso no PDF (os preenchimentos da ARQ_CONTRAPISO no tom 0,89, com a curva; só os que encostam na máscara do ajuste, porque o tom também é de outros pisos), desenhado em 4 x e reduzido, numa faixa de 2 px do ajuste; do lado de fora, o que ainda era pedra volta à grama (cv2.inpaint), e o limite ganha a linha cinza fina do PDF (118, 120, 116; 0,5 px do ajuste; força 0,45). Junto ao muro do lote, ao granito da garagem e por dentro (as plantas), fica a máscara do ajuste, como antes (o contorno do PDF para ~1 px antes do muro). O assentamento do leque muda um pouco, porque a máscara da pedra mudou.
- os traços verticais das juntas antigas (pedido do usuário de 21/10/26, com a varanda: "remover traços na vertical que anteriormente denotavam juntas. Deixe a imagem limpa"): `JUNTAS_VERTICAIS` e `juntas_verticais` (chave `juntas` do Térreo, depois das paredes, antes das projeções, que redesenham o tracejado por cima). O item dos rejuntes (19/10) deixou o piso original num anel de 7 px em volta dos traços desenhados e dos móveis, e ali ficaram pedaços das juntas verticais do motor: tracinhos de 1 a 2 px cruzando os tracejados das projeções, junto aos móveis e às portas de vidro. No travertino da legenda (o dos rejuntes, fechado 5 x 5 para não ter buracos nos traços, sem a escada interna), é junta o px de piso (pela cor dos rejuntes) mais escuro ou mais claro que os dois vizinhos a 2 ou 3 px na horizontal em 3 níveis ou mais, os dois também piso (numa borda de móvel, o px fica entre os dois), numa coluna de 6 px ou mais, medida atravessando as linhas do PDF (que cortam os tracinhos em dois) e fora delas (todos os traços do PDF, com 1 px de folga: o vidro das portas de correr, os tracejados, as folhas). A junta, fechada na vertical (as pontas na folga do traço do PDF) e com o antialias, vira, linha a linha, a reta entre o piso logo à esquerda e logo à direita (se um lado não é piso, o outro; se nenhum, fica): os veios do travertino correm na horizontal e continuam. 3.282 px no Térreo.
- o quarto do motorista (pedido do usuário de 21/10/26: "escreva o rótulo maior e na parte de baixo, onde tem um espaço maior. Melhore o aspecto da cama, pois está tudo muito brancão. E melhore o local da pezeira e seu aspecto"): a cama passa ao tipo "motorista" da roupa de cama (`_texturas/elementos.ROUPA_CAMA`, via `CAMA_MOTORISTA`): o lençol e a dobra continuam brancos, o edredom, depois da dobra, em linho claro (BGR 212, 221, 228), e a peseira bordô vai para os pés da cama (de 79% a 95% do comprimento), com as dobras e o pesponto claro junto às duas bordas (a 2,5 cm delas). O rótulo "Q. MOTORISTA" sai do lado da cama (corpo 0,8) e vai para o piso livre abaixo dela, entre a cama e a parede de baixo, centrado no quarto, no corpo 1,2 (`rotulos_casaa`, ajustes do Térreo), em branco no granito.
  - item 4, banhos 3 e 4: `banhos34_limpar` tira os discos, os registros e a cápsula do vaso (a luz do piso em volta, com a chapa do quartzito logo ao lado), depois do quartzito; `banhos34_pecas` desenha os dois nichos do PDF na parede e as peças com as funções do Subsolo da Casa E: `chuveiro` (ducha quadrada, braço e canopla) e `vaso` (tampo fechado; a dobradiça agora também em cima ou embaixo);
  - item 5, guarda-roupas (R11): `guarda_roupas` põe o `elementos.guarda_roupa` (aberto, com cabides) em cada trecho reto dos armários dos closets (os retângulos das diagonais da ARQ_LAYOUT HUMANIZAÇÃO), com as portas do lado do vinílico; a rouparia fica em marcenaria. Desde 21/10, em bege dentro e ocre na borda, com o cabideiro de metal (`miolo`, `moldura` e `barra` do `guarda_roupa`);
  - item 6, projeções (R8): `projecoes_1pav` desenha os traços da DOC_LINHAS E PROJEÇÕES do shaft entre o elevador e a rouparia (com o vão em branco, como os vazios), da rouparia (em cinza claro, sobre a madeira) e do fundo do banho master, por cima de tudo menos das paredes;
  - item 8, soleiras (R13): `soleiras_1pav` faz, nos sete vãos brancos do PDF (banhos 1 a 4, P11 e P13 do banho master, rouparia), a soleira do Térreo (Bege Bahia na escala, faces da parede em cinza fino); nas suítes o vinílico atravessa e não há soleira;
  - item 12, Bege Bahia das varandas: `varandas_bege` põe o desenho da biblioteca no tom da foto (seção 18), na luz do lugar, só no piso das três varandas (os vasos, as plantas e as peças de fachada ficam; a sombra deles é piso), logo no começo, para a copinha e as soleiras das fachadas saírem no mesmo Bege Bahia;
  - item 13, floreira só no verde: `floreira` tira as flores (o quente do recorte do Térreo aprovado) com `cv2.inpaint` antes de pousar;
  - item 14, aparador da sala íntima: `aparador_sem_planta` tira a plantinha que não está no PDF; cada linha do tampo, no retângulo `APARADOR["planta"]`, é a interpolação entre o px limpo de cada lado;
  - item 16, quartzito dos banhos: `quartzito_referencia`. Nas áreas de quartzito da base chapada, a parte pêssego de cada px vai ao tom da foto do quadro de 19/10. A fração vem do R − B contra o do piso, então sombras acompanham e as bordas de louças e vidros não ganham halo. Depois, `retexturizar` aplica a chapa da biblioteca na escala, só na luz (sem a faixa bege da foto), no piso limpo.

```bash
python3 retoque_1pav_casae.py ../../POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_render.png \
    --saida ../../POE642_CasaE/renders --nome POE642_CasaE_PH_1Pavimento_v1_retocado
```

## Opções de montagem do 1º Pavimento da Casa E: `opcoes_1pav_casae.py`

Duas opções em 3840 px para o cliente (pedido do usuário: "em preto e branco e só com as linhas do PDF"). Nas duas, o render retocado sem rótulos vai ao quadro 16:9 comum e entra por cima integralmente na pegada da base v3 (`entorno_esmaecido.sobrepor`), e os nomes e áreas são reescritos na resolução final (`retoque_1pav_casae.rotulos_ambientes`, com o PDF do 1º Pavimento levado ao quadro por `quadro_pdf`).
- **`_final_pb`:** o entorno é o render aprovado do Térreo, 75% mais claro e sem saturação (`entorno_esmaecido.contexto_render`).
- **`_final_linhas`:** o entorno é o PDF do Térreo só em linhas (`contexto_linhas`): a página desenhada pelo `Raster` do `gerar_bases.py` com as camadas ARQ_CONTRAPISO (cores e hachuras de piso), ARQ_TERRENO PLANEJADO, DOC_TEXTOS e ARQ_ZONA desligadas, sem os textos que sobram (título, escala, números da escada), na tela 16:9 e em cinza (`LINHAS["forca"]`: 70% do traço). O Térreo e o 1º Pavimento têm a mesma página e o mesmo recorte, então o PDF do Térreo cai direto no quadro comum.

`FORA` tem duas áreas brancas de fora presas na pegada: a de baixo da sala íntima e a faixa abaixo da parede de baixo da suíte 3, fechada pela linha fina do PDF. Nessa faixa o render tinha uma barra cinza, e na opção linhas devia haver só linhas. Ela começa abaixo da parede, para não pegar a escrivaninha da suíte, que é branca na base.

Desde 20/10/26 (pente fino do 1º Pavimento, item 1, sem os arcos):
- **Alinhamento fixo:** o afim do 1º Pavimento ao quadro comum é medido em `CIMA_APROVADO` (`renders/POE642_CasaE_PH_1Pavimento_v1_retocado_aprovado.png`, a versão entregue até 20/10, sem rótulos) e aplicado ao retocado atual (`no_quadro_comum(..., referencia=...)`, como o Térreo). Sem isso, cada retoque refazia o SIFT e a pegada inteira saía reamostrada.
- **`SETOR_PORTA`:** o setor branco da porta pequena à direita do vazio do hall, do lado de fora, entra em `FORA`. Os px do traço do arco (da base e do render) recebem o entorno depois da montagem. A base não muda, porque sem o arco o caixilho deixava de ser área fechada e saía da pegada.
- **Vazios nevoados (`nevoar_vazios`, item 15):** o branco dos dois vazios mostra o Térreo de baixo, no entorno da opção, multiplicado pelo tom do render. Assim o X, o vidro e a folha da pivotante ficam por cima. Os vazios são o cinza 74 da base v3 (`VAZIOS`).

O `entorno_esmaecido.py` foi dividido em `contexto_render` (o entorno a partir de um render) e `sobrepor` (pegada, sobreposição integral, tracejado do lote), com o `compor` de antes por cima dos dois.

```bash
python3 opcoes_1pav_casae.py      # -> POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_final.png (+ _preview.jpg), o nublado
python3 opcoes_1pav_casae.py --opcao pb --opcao linhas   # as opções antigas: ..._v1_final_{pb,linhas}.png
```

As opções viraram pranchas e PDFs de entrega com `rodape_entrega.py --no-quadro --sufixo _pb` / `_linhas` / `_nublado` e `pdf_entrega.py --prancha`. Desde 21/10/26 (fim do pente fino, seção 16 das regras), o nublado é a opção única: sem `--opcao`, sai só ele, sem sufixo, e vira a prancha `..._1Pavimento_entrega.png` e o PDF único `POE642_CasaE_Plantas_Humanizadas.pdf` (comandos em "Pranchas de entrega"). Os arquivos das opções ficam no histórico do git.

## Retoque do Subsolo da Casa E: `retoque_subsolo_casae.py`

Retoques locais, sem IA, no render v1 do Subsolo da Casa E, no quadro do render (que manteve a escala da base). Cada item tem o seu número no mapa `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_erros.jpg` (gerado com `--mapa`) e no handoff.
- **Pisos refeitos:** onde o motor trocou o material ou o manchou, o piso da base chapada vira a textura aprovada da base v3 (a mesma prévia que o motor recebeu), alinhada ao render, normalizada e multiplicada pela cor do material no próprio render (`trocar_piso`). Folhas e soleiras de porta da base dentro da área são preenchidas pelo piso em volta (`buracos`).
- **Portas:** `desenhar_porta` desenha a folha (retângulo do PDF) e o arco (a curva do PDF) em traço fino, em 8 x.
- **`--ate N`:** roda só os itens até N (para gravar e conferir um item por vez).
- **Imagem final (`_final.png`, 3840 × 2160):** a planta retocada no quadro comum. Fora dela, o terreno do lote fica hachurado em diagonais a 45°, em cinza-claro (`contexto_hachura`, regra R2 de 19/10/26). O lote é o do Térreo final no mesmo quadro (`lote_do_terreo`; refeito em 21/10/26, depois do pente fino do Térreo). Antes, o fundo tinha as linhas do PDF do Térreo. A escada e o travertino tiram trechos do Térreo aprovado de 15/10 (`TERREO_APROVADO`), fixo, para o Subsolo não mudar quando o Térreo muda. Nela são escritos os nomes e as áreas pela regra do 1º Pavimento (`retoque_1pav_casae.rotulos_ambientes`; no granito, cinza). Os desvios e o corpo de cada rótulo ficam em `ROTULOS["ajustes"]` (nome, centro em px de 2000, desvio e, se preciso, as opções: o corpo, 1.0 sendo o do PDF, ou um dicionário com `corpo`, `quebra` e `cor`). Os nomes em duas linhas no PDF entram como um rótulo só (`rotulos_pdf`). O retocado de 2000 px fica sem rótulos.
- **Item 19 (`piscina_cliente`, pedido do cliente):**
  - a piscina sem a divisória;
  - o visor de baixo e o vidro da sauna sem a base de Bege Bahia, com a água até o vidro;
  - as esquadrias com perfis em grafite e montantes.
- **Rótulos que o PDF não tem:** entram por `ROTULOS["extras"]` (nome, centro em pt do PDF, corpo); o "AMBIENTE" da antessala é o primeiro.
- **Alinhamento da imagem final:** é medido no retocado dos itens 1 a 16 (`rodape_entrega.no_quadro_comum(..., referencia=)`). Assim, um item novo não mexe no resto da imagem.

```bash
python3 retoque_subsolo_casae.py ../../POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_render.webp \
    --mapa ../../POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_erros.jpg      # só o mapa dos erros
python3 retoque_subsolo_casae.py ../../POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_render.webp \
    --saida ../../POE642_CasaE/renders --nome POE642_CasaE_PH_Subsolo_v1_retocado
```

## Portas sem arcos: `arcos.py`

`remover_arcos(out, pg, p2r, camadas=..., so_folha=False)` tira da imagem os arcos de porta do PDF: as curvas das camadas dadas, um quarto de círculo por arco. As folhas e os batentes ficam. Segue a regra R3 de `POE642_REGRAS.md`.
- **Portas de giro:** a faixa do arco vira a textura do mesmo piso logo depois dela, na mesma direção, com a borda suave; quando isso não dá, inpaint.
- **Porta camarão** (arcos rasos): o setor volta a ser o piso tecido (`camarao_fontes`).
- **`so_folha=True`:** só protege a reta de uma ponta se houver folha nela (porta dupla).
- **Onde é usado:** Térreo da Casa A (`ajustes_casaa.sem_arcos`) e Subsolo da Casa E (item 22 do `retoque_subsolo_casae.py`).

## Texturas na escala: `texturas_escala.py`

`retexturizar(out, mascara, nome, px_por_m, forca=0.6)` troca o desenho do piso na máscara pelo da biblioteca `_texturas`, na escala do render. A luz e a cor do lugar ficam (média local do piso, sem traços nem objetos), e os riscos claros do motor viram piso. Segue a regra R1 de `POE642_REGRAS.md`. Usado no Subsolo da Casa E (item 24 do `retoque_subsolo_casae.py`: Bege Bahia e travertino).

## Biblioteca de blocos e cortina: `_blocos/blocos.py`

`python3 blocos.py` (de `projetos/_blocos/`) recorta os blocos de `blocos.json` das folhas em `originais/` (PNG com transparência em `recortes/`), desenha a cortina e faz `cartela_blocos.jpg`.
- `bloco(id, px_por_m)`: cor e alfa do bloco na medida real, para pousar no render.
- `cortina(comp_m, px_por_m, aberta=False)`: a cortina de linho vista de cima, na horizontal (o trilho do lado do vidro, o tecido em ondas, a sombra para dentro).
- Ainda não usada em nenhum retoque (aguarda a aprovação da cartela).

## Pedra portuguesa na escala: `texturas_escala.trocar_pedra_portuguesa`

`trocar_pedra_portuguesa(out, mascara, px_por_m, fonte="foto" | "leque" | "procedural")` troca a pedra portuguesa do motor pela da regra (6 a 8 cm), sobre a luz e as sombras do lugar, como em `trocar_grama`:
- `fonte="leque"` (Casa E, escolha do usuário em 20/10: "opção 1, tom da foto"): `pedra_portuguesa_leque` desenha as pedras de 7 cm assentadas em leque, como na foto de referência (`_texturas/pedra_portuguesa.jpg`). As escamas têm 1,2 m de raio, em fiadas desencontradas, e as pedras seguem arcos concêntricos. Os contornos são levemente irregulares, as juntas, claras de areia, e as cores são sorteadas das pedras da própria foto. A luz do lugar entra só como relativa; o tom é o da foto.
- `fonte="foto"`: a foto vista de cima, espelhada em blocos. Testada e descartada: com 7 cm em ~4 px, o leque some e fica um caleidoscópio. A foto tecida da biblioteca vira cara de granito.
- `fonte="procedural"`: as pedras caramelo soltas de `fontes_procedurais.pedra_portuguesa` (a da base v3), agora com a escala e a junta como parâmetros.

No Térreo da Casa E (item 47) entra no retocado e de novo na final de 3840 px, onde as pedras têm ~4 px. A área do retocado é o caramelo da base chapada, só onde o px ainda é caramelo e sem as plantas. Na final vale só a base, porque o retocado já chega com a pedra nova. No retocado, a franja da borda recebe a troca de tom na fração de caramelo que tem.

## "m²" dos rótulos: `retoque_1pav_casae.rotulos_ambientes`

O "2" sobrescrito do "A: ... m²" fica logo depois do fim do "A: ... m", medido na Inter (`textlength`), com a folga `ROTULOS["folga_m2"]` (7% do corpo da linha), na altura do PDF. Antes ele ficava na posição do PDF e, como a Inter tem outras larguras, encostava no "m" ou se afastava dele. A rotina é a mesma de todos os pavimentos e casas: os que ainda não foram refeitos passam a sair assim quando rodarem de novo.

## Granito menos escuro e sem pontos: `retoque_terreo_casae.granito_tom`

Age só no granito da base chapada, nos px de granito: perto do marrom no croma e de 40% a 150% da luminosidade mediana. Carros, inox, móveis, paredes, rótulos e traços ficam, e as sombras acompanham o tom.
1. **Pontos:** os claros do motor, mais de 10 níveis acima da mediana de 7 px em volta, em manchas de até 40 px e 8 × 8 px, viram a mediana em volta, com a borda suave. Ficam protegidos os px a 2 px de cinza neutro (folhas de porta), das linhas do PDF da DOC_LINHAS E PROJEÇÕES (o X tracejado, desenhado como máscara) e de fora do granito.
2. **Grade de manchas:** a variação de média escala que o motor repete (razão entre a média de 30 px e a de 1 px do granito) sai, longe de objetos e paredes (de 5 a 12 px ela some aos poucos, para as sombras ficarem); o grão fino fica (`GRANITO_TOM["manchas"]`).
3. **Referência:** `texturas_escala.trocar_granito` põe o granito marrom da referência do usuário (`fontes_procedurais.granito_referencia`): base marrom com nuvens e lascas de agregado de 2 a 55 mm em tons de marrom, creme, cinza e quase preto, na escala do render. Usa a luz do lugar (média de 2,5 px nos px de granito, relativa à mediana), para as sombras ficarem. Os traços do PDF e os cinza neutros ficam, com a troca de tom na fração de granito que têm. Substitui o ganho de cor da opção B (`GRANITO_TOM["alvo"]` deixou de ser usado).

Roda antes das projeções, para não tocar o tracejado delas. A máscara da pedra portuguesa (item 47) exclui o granito da base: mais claro, ele passava pelo teste de caramelo na borda do acesso.

## Soleiras do Térreo da Casa E: `retoque_terreo_casae.soleiras`

`SOLEIRAS["pdf"]` traz os 12 vãos de porta do PDF com soleira: o retângulo branco da ARQ_PAREDE na espessura da parede, junto de cada arco. Foram achados pelo arco de cada porta de giro, pegando o branco encostado nele com o comprimento do raio. Cada um é refeito igual, em 8 x:
- o vão exato, em Bege Bahia da biblioteca, na escala e no tom `BEGE["tom"]` (força 0,5 do desenho);
- as duas faces da parede (os lados compridos), em traço cinza fino de 0,4 px.

É a mesma regra do Subsolo (`retoque_subsolo_casae.soleiras`). Para as outras casas, os vãos saem do PDF da mesma forma.

## Vegetação do gramado e jardim de inverno: `retoque_terreo_casae.vegetacao` e `jardim_flores`

Pente fino do Térreo da Casa E, item 7 (escolha do usuário entre as opções de `renders/POE642_CasaE_PH_Terreo_vegetacao_opcoes.jpg`: "opção A"). `vegetacao` (item 53) roda depois da grama (item 42) e do Bege Bahia (item 43), e antes da pedra portuguesa (item 47):
1. **Manchas:** o gramado da base chapada (`GRAMA`) e as manchas de planta dele (`texturas_escala.mascara_grama`, com a cor da grama da amostra). O verde é o gramado mais as manchas.
2. **Restos fora do verde** (`restos_fora_do_verde`): numa faixa de 0,6 m em volta do verde, cada material da base chapada (os px soltos de cor rara ganham o material mais próximo) dá os candidatos: verdes, ou longe da mediana do material (a sombra das folhas). Vale a mancha com folha verde a 3 px ou mais do verde e com até 50 px de lado. A abertura 5x5 tira do núcleo as juntas de grama entre os pisantes (finas). O px refeito copia o próprio material a 12 ou 24 px ao lado (inpaint só no que sobra). Depois, os pontinhos que fogem da mediana 5x5 no miolo do material viram ela. Na pedra portuguesa a cópia é do caramelo, que o item 47 redesenha.
3. **Grama:** a da biblioteca, sob as manchas e onde o gramado não é grama (pontas de folha), com a luz larga (1,5 m) só da grama.
4. **Plantas** (`VEGETACAO["catalogo"]`): as árvores, arbustos e palmeiras de `_texturas/vegetacao` (planta de referência de 19/10), no tamanho real. Em cada mancha entra o maior que cabe primeiro, com a copa a 0,9 do raio dentro do verde e afastadas (0,85 da soma dos raios). As menores ficam por baixo. Sem girar: a sombra vem no desenho (para baixo e à esquerda), e a de `texturas.json` entra por baixo. `sprite_referencia` tira o anel escuro da borda da copa (a sombra recortada junto), só no raio > 0,7 r. Por fim, tudo é recortado no verde.

`jardim_flores` (itens 19 e 54) refaz a floreira do jardim de inverno: forração escura (o desenho da grama, com o contraste aumentado, no tom `JARDIM_FORA["forracao"]`) no miolo, sem a borda escura do item 3. Por cima vêm as plantas tropicais da biblioteca de blocos (`JARDIM_FORA["plantas"]`: bananeira, comigo-ninguém-pode, arbusto e planta com flores, no tamanho real, sem o fio claro do recorte), em duas fileiras desencontradas na ordem de `"ciclo"`, giradas, as maiores por baixo. As da planta de referência (26 px/m) ficavam borradas nos 39 px da floreira. As copas saem só até a borda irregular do item 19 (nunca sobre a escada), com a sombra curta no travertino. As flores tropicais vão por cima. Com `JARDIM_FORA["so_verde"]` (Casa E, 20/10/26: "remova as cores quentes. Mantenha apenas o verde"), as flores não entram e as plantas são só folhagens verdes (bananeira, comigo-ninguém-pode, planta de folhas largas e costela-de-adão). Nas duas últimas (`"sem_fundo_claro"`), o fundo branco da foto que o recorte guardou e o vaso de terracota saem do alfa.

## Esquadrias finas: `retoque_terreo_casae.esquadrias`

Pente fino do Térreo da Casa E, item 8 ("portas vidros e janelas mais delicados e finos?"). No PDF, vidros, folhas e caixilhos estão na ARQ_PAREDE, como brancos finos. `esquadrias_elementos` pega os de até `ESQUADRIAS["espessura_max"]` (12,5 pt) e `comprimento_min` (15 pt) ou mais. Ficam de fora as soleiras de `SOLEIRAS["pdf"]`, as bordas da piscina e do spa e as caixas de `ESQUADRIAS["fora"]` (portas do elevador). Os vizinhos da mesma direção, a 3 pt ou menos, formam um grupo.

`esquadria_limpar` limpa uma faixa de `faixa_px` (3 px) para cada lado, no eixo fino, com o piso logo fora espelhado. Se a fonte for escura (parede), vem o do outro lado.

`esquadria_desenhar` redesenha a zona do grupo (com `folga_pt`), em 8x:
- paredes cinza do PDF em preto;
- os brancos, do maior para o menor: vão com vidro dentro em Bege Bahia (peitoril; sem vidro, a passagem fica no piso); 3,2 a 7 pt em alumínio claro (caixilho); 1,6 a 2,5 pt em cinza bem claro (folha de porta); até 1,6 pt no vidro aprovado;
- os traços do PDF (`l` e `re`) por cima, em cinza médio de 0,3 px, recortados na zona.

No `main`, roda depois do granito (item 50) e antes das soleiras, das projeções e das cortinas.

## Banquetas da ilha gourmet: `retoque_terreo_casae.banquetas`

Pente fino do Térreo da Casa E, item 9 ("na ilha do espaço gourmet, deixe apenas 5 cadeiras", com a foto da banqueta para a biblioteca: `_blocos`, folha_06, bloco "banqueta_linho"). `banquetas(out, p2x)` funciona no retocado (`banquetas_ilha`, item 56) e de novo na final de 3840 px (`final_rotulos`, depois da pedra portuguesa), onde a banqueta tem 24 px e sai nítida.
- **Limpeza:** a faixa das 7 banquetas do motor (`BANQUETAS["faixa"]` px abaixo da ilha, com `folga` para os lados; px do retocado, escalados na final) recebe as linhas de Bege Bahia logo abaixo (`fonte_dy`), com a borda suave e a sombra curta da ilha.
- **Banquetas:** 5 do bloco, no tamanho da banqueta do PDF (`modelo_pdf`, 22,7 pt), centradas em 1/10, 3/10 ... 9/10 do comprimento da ilha, na linha do PDF, com a sombra de `texturas.json`. Só o que fica abaixo da borda da ilha entra: a frente do assento fica sob o tampo, como no PDF.

## Cooktops das ilhas: `retoque_terreo_casae.cooktops`

Pente fino do Térreo da Casa E, item 10 ("melhorar a representação dos cooktops das ilhas, com novo bloco"). Regra da seção 7: cooktop com as bocas do PDF, eletrodomésticos em inox. Os dois cooktops do PDF (`COOKTOPS["pdf"]`, ARQ_LOUÇAS E METAIS, 5 bocas, 49,9 x 28,3 pt) recebem o bloco `cooktop_inox_5_90` da biblioteca. Como as banquetas, roda no retocado (`cooktops_ilhas`, item 57) e de novo na final de 3840 px (`final_rotulos`):
- **Limpeza:** o retângulo do PDF, com `margem` (2,5 px do retocado; o contorno do motor passa do retângulo), volta ao tampo da ilha. A fonte é o tampo logo à esquerda, com a borda suave.
- **Bloco:** gira 180° (`giro`), para os botões ficarem do lado de quem cozinha (o oposto das banquetas). Entra na altura do PDF, com até 10% de alongamento na largura (`esticar`), centrado e em 8x. O anel azul da chama da foto vira inox (`azul`).

## Poltronas do living e da varanda: `retoque_terreo_casae.poltronas`

Pente fino do Térreo da Casa E, item 11 (escolha do usuário: "use a bouclé creme no living e a palhinha na varanda"). As 8 poltronas do PDF ficam em `POLTRONAS["pecas"]`: bloco, centro, ponto para onde olham (pt) e tamanho (m). `frente` diz para onde a frente do assento aponta na folha de cada bloco. Roda no retocado (`poltronas_sociais`, item 58) e de novo na final de 3840 px, só desenhando por cima (`limpar=False`).
- **Limpeza:** a poltrona do motor é a mancha clara perto do centro do PDF. O disco vai no centro dela, com o raio dela + `folga` (ou `raio` x tamanho, o que for maior), mais o disco deslocado da sombra, sem os círculos de `proteger` (a mesa em X).
- **Preenchimento:** o piso vem do deslocamento (`busca` x tamanho, nas `direcoes` quase verticais) que melhor continua o anel em volta. Ficam de fora os que caem sobre outra poltrona ou têm px a mais de `objeto` níveis do piso. A emenda é em gradiente (`cv2.seamlessClone`), e os px soltos viram a mediana 7x7.
- **Bloco:** girado para o ponto, no tamanho do PDF, com a sombra curta (`sombra`). Os vincos da bouclé são clareados (`clarear`).

## Mesas redondas da varanda: `retoque_terreo_casae.mesas`

Pedido do usuário ("mesas e cadeiras para a varanda", com a foto da `_blocos` folha_07, bloco "mesa_redonda_6_couro"). `MESAS_VARANDA["pecas"]` traz bloco, centro (pt), altura (m) e giro de cada conjunto do PDF.
- **Retocado (`mesas_varanda`, item 59):** a mancha do conjunto do motor (o que foge da luz do piso, ligado ao centro, até `alcance` x altura), com `folga` e o disco da sombra, sai. O buraco recebe o Bege Bahia da biblioteca nos parâmetros de `BEGE` (o do item 43), sob a luz larga do piso limpo em volta (`luz_m`), emendado com `cv2.seamlessClone`. O bloco entra com a sombra curta.
- **Final de 3840 px:** só redesenha o bloco por cima (`limpar=False`).

## Mesa de jantar do living: `retoque_terreo_casae.jantar`

Pedido do usuário ("mesa de jantar", com a foto da `_blocos` folha_08, bloco "mesa_jantar_10"; imagem licenciada pelo usuário). `JANTAR["caixa"]` é a caixa do conjunto no PDF (pt). No retocado (`jantar_living`, item 60):
- **Limpeza:** a mancha do motor dentro da caixa (o que foge da luz do travertino em `foge` níveis, ligado ao centro, com os furos preenchidos), dilatada em `folga` px, mais a mesma mancha deslocada em `sombra_motor`.
- **Piso:** o travertino é tecido dos trechos limpos de `fontes` (`retoque_terreo_casad.textura`, image quilting), sob a luz larga do piso limpo, e emendado com `cv2.seamlessClone`.
- **Bloco:** entra no centro, girado `giro`, na medida da biblioteca, com a sombra curta.

Na final de 3840 px, só redesenha o bloco por cima (`limpar=False`).

## Título da folha: `retoque_terreo_casae.titulo_folha`

O texto do título ("0. TÉRREO / ESC.:1:50") não entra nas bases, mas o sublinhado dele, uma linha do PDF sem camada logo abaixo do canto tracejado do lote, pode sobrar. `titulo_folha` volta ao branco a faixa da linha (pt do PDF em `TITULO["linhas"]`, folga de 2 px), só nos px claros, e deixa o tracejado do lote. Para as outras casas, basta achar a linha logo abaixo do título no PDF delas.

## Nomes e áreas da Casa A: `rotulos_casaa.py`

Os rótulos do PDF de cada pavimento da Casa A (`_pdfs_cliente/642 - <PAVIMENTO> - CASA A.pdf`), pela regra da Casa E (`retoque_1pav_casae.rotulos_ambientes`). A imagem aprovada (2000 px) vai ao quadro comum em 3840 px (`rodape_entrega.no_quadro_comum`), e os rótulos são escritos nessa resolução. O granito, onde o texto fica cinza, é achado na própria imagem (`GRANITO`). As notas que não são ambientes ficam fora (`FORA`). Os desvios de cada pavimento estão em `PAVIMENTOS[...]["ajustes"]`, no mesmo formato da Casa E.

```bash
python3 rotulos_casaa.py Subsolo      # -> ../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png (+ _preview.jpg)
python3 rotulos_casaa.py Terreo       # -> ../renders/POE642_CasaA_PH_Terreo_final_rotulos.png
python3 rotulos_casaa.py 1Pavimento   # -> ../renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png
```

Desde o pente fino de 21/10/26 (item 2 do Térreo), os rótulos no granito marrom saem em branco (R6, `cor_granito=R1.ROTULOS["branco"]`; antes, cinza 150), e o "²" logo depois do "m", pela rotina comum (regra de 20/10).
O granito é achado na imagem pela luz (desfocada) baixa e o tom quente (`GRANITO`, luz até 95). No Térreo o limite é 125 (`PAVIMENTOS["Terreo"]["granito_lum_max"]`): o granito da referência (item 10 do pente fino) é mais claro, e com 95 os rótulos da garagem, da despensa e do motorista saíam cinza.
No Térreo, a pedra portuguesa é desenhada de novo na final (`PAVIMENTOS["Terreo"]["pedra"]`, item 11 do pente fino): a máscara gravada pelo `ajustes_casaa.pedra_leque` vai ao quadro pelo mesmo afim da imagem (`no_quadro_fixo(..., mascara=)`), e `ajustes_casaa.pedra_final` desenha nela as pedras de 7 cm (~4 px a 59,7 px/m) e as linhas da DOC_LINHAS do PDF, antes dos rótulos.

## Conferência da Casa A com o PDF: `conferencia_casaa.py`

As divergências entre as imagens aprovadas da Casa A e os PDFs do cliente, em `ITENS` (pontos em px de 2000 do quadro comum), e o mapa numerado de cada pavimento, com a legenda em Inter (acentos corretos).

```bash
python3 conferencia_casaa.py            # -> ../renders/POE642_CasaA_PH_{Terreo,1Pavimento,Subsolo}_conferencia.jpg
python3 conferencia_casaa.py --pente-fino   # -> ../renders/POE642_CasaA_PH_<Pavimento>_pente_fino_mapa.jpg
```

**Pente fino pelas regras (21/10/26):** com `--pente-fino`, o mapa sai sobre a prancha atual (a final com os rótulos, já no quadro comum), com os itens de `PENTE_FINO` e o recorte de `RECORTE_PF`, como o pente fino da Casa E. Os pontos vêm da geometria do PDF levada ao quadro comum (`opcoes_1pav_casae.quadro_pdf`).

## Pente fino da Casa B: `conferencia_casab.py`

O mesmo mapa do pente fino pelas regras (21/10/26), sobre as pranchas de entrega da Casa B (`POE642_CasaB/entrega/POE642_CasaB_PH_<Pavimento>_entrega.png`). Os itens ficam em `PENTE_FINO`, com os pontos em px da prancha de 3840, e o recorte em `RECORTE`. A legenda e o desenho são os do `conferencia_casaa.py` (`fonte`, `quebrar`, `VERMELHO`).

```bash
python3 conferencia_casab.py            # -> ../../POE642_CasaB/renders/POE642_CasaB_PH_{Subsolo,Terreo}_pente_fino_mapa.jpg
python3 conferencia_casab.py Terreo
python3 conferencia_casab.py --escalas  # -> ../../POE642_CasaB/renders/POE642_CasaB_PH_escalas_conferencia.jpg
```

**Escalas (usuário, 21/10/26: "ATENÇÃO ÀS ESCALAS"):** os itens de escala vêm primeiro em `PENTE_FINO`. Com `--escalas`, sai a folha de conferência: cada piso da prancha (`ESCALA_PISOS`, trechos de 1,5 × 1,5 m sem móveis) ao lado do da biblioteca na mesma escala (`_texturas/texturas.textura` a 59,7 px/m), ampliados 6 vezes, e a vegetação (`ESCALA_VEGETACAO`) com uma régua de 1 m. Os itens de `PENTE_FINO` com número `None` são notas sem marca no mapa (os conformes).

Para conferir, o PDF (renderizado a 1,2 px/pt) foi levado ao quadro da prancha pelo alinhamento das paredes (`cv2.findTransformECC`, afim): prancha ≈ PDF × 0,878 + (126,5; −238), nos dois pavimentos.

## Pente fino da Casa C: `conferencia_casac.py`

O mesmo mapa (22/10/26), sobre as pranchas de entrega da Casa C (`POE642_CasaC/entrega/POE642_CasaC_PH_<Pavimento>_entrega.png`), com as escalas primeiro. Os itens ficam em `PENTE_FINO` (pontos em px da prancha de 3840), o recorte em `RECORTE`, e a folha das escalas em `ESCALA_PISOS` e `ESCALA_VEGETACAO`, como no `conferencia_casab.py`. O PDF vai ao quadro da prancha pela cadeia das bases (`opcoes_1pav_casae.quadro_pdf`, config da Casa C, 59,7 px/m).

```bash
python3 conferencia_casac.py            # -> ../../POE642_CasaC/renders/POE642_CasaC_PH_{Subsolo,Terreo}_pente_fino_mapa.jpg
python3 conferencia_casac.py --escalas  # -> ../../POE642_CasaC/renders/POE642_CasaC_PH_escalas_conferencia.jpg
```

## Pente fino da Casa D: `conferencia_casad.py`

O mesmo mapa (22/10/26), sobre as pranchas de entrega da Casa D (`POE642_CasaD/entrega/POE642_CasaD_PH_<Pavimento>_entrega.png`), com as escalas primeiro. Itens em `PENTE_FINO`, recorte em `RECORTE`, folha das escalas em `ESCALA_PISOS` e `ESCALA_VEGETACAO`, como nos das Casas B e C. O PDF vai ao quadro da prancha pela cadeia das bases (`opcoes_1pav_casae.quadro_pdf`, config da Casa D, 59,7 px/m).

```bash
python3 conferencia_casad.py            # -> ../../POE642_CasaD/renders/POE642_CasaD_PH_{Subsolo,Terreo}_pente_fino_mapa.jpg
python3 conferencia_casad.py --escalas  # -> ../../POE642_CasaD/renders/POE642_CasaD_PH_escalas_conferencia.jpg
```

## Ajustes da Casa B pelo pente fino: `ajustes_casab.py`

Os itens dos mapas do pente fino da Casa B (25 no Térreo, 12 no Subsolo), um por vez, sem IA, na imagem de partida de cada pavimento (Térreo: o render retocado de 2000 px; Subsolo: a final de 6905 px reduzida a 2000). Reaproveita as rotinas aprovadas do pente fino da Casa A (`ajustes_casaa.py`):
- `contexto()` aponta as duas (`rotulos_casaa` e `ajustes_casaa`) para a Casa B: o PDF, a config, as imagens aprovadas, o afim do quadro (`AFIM_QR_B`) e a base chapada da legenda B (v2);
- os dicionários de parâmetros recebem as coordenadas e as cores da Casa B: o gramado é o verde da legenda (`gramado_plantas_b`), o granito é #5A4232 e o vinílico, #C8A27C;
- `chave_como` deixa uma rotina que lê um pavimento fixo ("1Pavimento", "Terreo") ler outro;
- as peças sem rotina na Casa A ganharam rotina própria: os jardins (`canteiro`), a bancada da sala íntima, a adega, os cooktops, os portões, as cortinas em ondinhas, as camas deitadas, as soleiras automáticas (`vaos_brancos`), as escadas do Subsolo em cor cheia e a pegada do Subsolo.

A ordem está em `ITENS`. Cada item grava um antes/depois (`renders/POE642_CasaB_PH_<Pavimento>_<item>_antes_depois.jpg`), e as etapas ficam em cache (`$TMPDIR/poe642_casab_etapas`). `--final` monta a imagem de 3840 px no quadro comum:
- no Térreo, com a pedra portuguesa redesenhada pela máscara;
- no Subsolo, com o que não mudou vindo da imagem de 6905 px e o terreno hachurado a partir do Térreo final;
- nos dois, refeitos na resolução da prancha (desde 22/10/26), porque o ajustado em 2000 px e ampliado engrossa:
  - o travertino da biblioteca (`travertino_final` → `trocar_travertino`), na máscara da base chapada menos os objetos do PDF e as escadas (no Subsolo, só na pegada);
  - as esquadrias (`esquadrias_final` → `esquadrias_pdf`, com a faixa de limpeza na escala);
- só no Térreo:
  - as bordas entre a grama e os pisos (`bordas_grama`: o contorno da legenda, liso, com a grama de um lado e o piso do outro);
  - a cobertura da entrada (`cobertura_final`: o tracejado da ARQ_PAREDE, a pérgola entre o jardim do hall e a garagem);
- nos dois, com os rótulos, os desvios da R7 em `PAVIMENTOS_B[...]["ajustes"]`.

Pedidos de 22/10/26, além dos itens do mapa:
- **Térreo:**
  - guarda-roupas com cabides da R11 (`guarda_roupas_terreo`), no lugar da marcenaria;
  - riscos do motor nos pisos fora (`riscos_terreo`: escuros finos ou pontuais, longe das linhas e dos objetos do PDF, por inpaint).
- **Nos dois pavimentos:** as ilhas e bancadas passaram pela pedra fina de tom sóbrio (`pedra_bancadas`: `carrara_bancadas` com `fontes_procedurais.pedra_fina`); na final de 3840 px (`final3840_casab.py`), elas são agora a pedra tom areia humanizada, com as cubas brancas.
- **Subsolo:**
  - o deck em L e a escada de 9 degraus vão para a hachura (não são do Subsolo);
  - o chuveiro na ducha (`chuveiro_ducha`);
  - as bancadas com o contorno fino do PDF (`bancadas_subsolo`);
  - os riscos fora (`riscos_subsolo`).

```bash
python3 ajustes_casab.py Terreo                 # todos os itens (ou --ate <item>, --de <item>)
python3 ajustes_casab.py Terreo --final         # = final3840_casab.py Terreo (seção seguinte)
python3 ajustes_casab.py Subsolo && python3 ajustes_casab.py Subsolo --final
python3 rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --no-quadro \
    --render Terreo=../../POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png \
    --render Subsolo=../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final_rotulos.png
python3 pdf_entrega.py --config ../../POE642_CasaB/config_bases.json
```

## A final da Casa B em 3840 px: `final3840_casab.py`

Pedido do usuário (22/10/26): "TEM MUITOS BORRÕES NA IMAGEM. MOBÍLIAS DESGASTADAS E MAL DESENHADAS. PRECISO QUE REVISE ITEM A ITEM E DEIXE A IMAGEM COM OS CONTORNOS PERFEITOS". O que os ajustes desenhavam em 2000 px e a final ampliava saía mole, então a final passou a ser desenhada direto no quadro da prancha (3840 × 2160, ~59,7 px/m), pelo PDF (vetor) e pela base chapada da legenda (6905 px, reduzida por vizinho: as máscaras de material ficam exatas). `ajustes_casab.py --final` chama este módulo.

- `Quadro(chave)`: o PDF e o seu mapeamento para o quadro (`p2q`; `p2q2000` para os rótulos), a escala, a base chapada e as máscaras (`cor`, `preencher` com antialias, `caminhos`).
- `afim_render`: o afim do render de 2000 px para o quadro (SIFT, como o `no_quadro_fixo`; em cache), de onde saem as cores dos móveis e o lugar das plantas e dos carros.
- **Etapas do Térreo** (`passos_terreo`):
  - `pisos`: cada material na máscara da legenda, com a textura da biblioteca na escala; o preto da base fica fora (as paredes), menos o traço dos arcos das portas (`arcos_porta`, `ARCOS_F`: os 25 do Térreo e os 4 do Subsolo, da ARQ_PAREDE), que entra no piso em volta, sem restos do arco do render; e as manchas soltas de cada material na legenda que outro piso cobre (`soltos`, `SOLTOS_F`: menos de 40 px e a mais de 2 px de uma mancha grande do mesmo material, o antialias dos traços, como o do arco sobre o vinílico, que caía na cor do granito) ficam com o piso em volta (as que não têm outro piso em volta, como a pedra portuguesa junto aos carros, ficam): a textura sai na máscara inteira (o mesmo desenho de antes) e só não é pousada nelas;
  - `bordas`: grama e piso;
  - `vegetacao`: as plantas da biblioteca nos lugares do gramado; a floreira; e os dois jardins (`jardins`, `JARDINS_F`):
    - o de inverno: o canteiro na sala inteira, sem moldura de travertino (`JARDINS_F["inverno"]["canteiro_pt"]`): da face de baixo do vidro de cima (rente ao vinílico) à de cima do vidro de baixo, da parede da direita às folhas de correr (a de dentro até 1042,5 pt, a de fora daí para baixo), sem transbordo; o travertino só do lado de fora das portas, como a legenda pinta;
    - o do hall: o canteiro no retângulo do PDF (sem transbordo, a borda limpa contra o travertino) e a faixa de baixo, sob os brises, em travertino;
    - nos dois, só plantas verdes da biblioteca, a forração mais fechada e o chão em verde-escuro; a faixa do hall sob o vidro de baixo do jardim de inverno volta a travertino (`limpar_pt`, com `travertino_em`);
  - `bancadas`;
  - `pecas`: os móveis, os tapetes e as louças pelo desenho do PDF; nas zonas de `PECAS["humanizar"]` (o estar da varanda gourmet), os estofados com volume de almofada, a trama do bouclé e o traço mais leve, e a madeira com o veio mais marcado; sem as marcações técnicas dos tampos (`PECAS["marcas"]`: os traços na cor laranja do PDF, os cantos tracejados da mesa de jantar do living, do aparador e das mesas redondas, e as duas elipses no meio da mesa de jantar, `fora_pt`);
  - `tampas`: o desenho do tampo da mesa redonda do hall interno (`desenho_mesa`, `MESA_HALL_F`: as linhas do PDF por cima, nítidas, com relevo leve); e a tampa fechada em todos os vasos sanitários (`tampas_vasos`, `TAMPAS_F`). Os vasos são o "D" branco da ARQ_LOUÇAS E METAIS de 0,45 a 0,62 x 0,30 a 0,42 m sem outra louça dentro (`vasos_sanitarios`; o centro de massa puxado para o lado reto separa o vaso das cubas e das máquinas e dá o lado da parede). A tampa é o contorno recuado 1,2 cm, da dobradiça (17% do comprimento a partir da parede) à frente, em louça branca com volume, o traço das louças e a sombra curta sobre o aro; também no Subsolo;
  - `biblioteca`: guarda-roupas, camas, cooktops, banquetas, inox, adega e elevador, pelas rotinas dos ajustes dentro de `em_quadro`, que as faz desenhar no quadro; depois, a cama da suíte master e o banco aos pés dela (`cama_master`, `CAMA_MASTER_F`): da silhueta do PDF, por faixas, a placa, o lençol, os travesseiros, as almofadas bordô, o rolo e o cobre-leito em matelassê com a peseira; o banco, que no PDF está na camada DOC_TEXTOS, estofado em linho greige com as costuras e os rolos;
  - `carros`;
  - `deck`: o banco em L, em bronze fosco (`BANCO_DECK`), e o chuveiro;
  - `boxes`: nos banhos de granito, o vidro do box em faixa cinza-clara (`boxes_granito`, `vidros_box`, `BOXES_F`);
  - `paredes`: as pretas, e os pilares redondos em cinza; os muros na sequência das portas de correr da área de serviço descoberta (`PAREDES_F["muros_pt"]`); os brises do jardim do hall em grafite, com a aresta clara, o contorno e a sombra (`brises`); o guarda-corpo de vidro da varanda da suíte master (`guarda_corpo`), antes do preto: as três lâminas do PDF (em cima, à esquerda e o fechamento em pé à direita, até a parede), cada uma passando 0,6 px das pontas para as quinas fecharem, e o lábio de travertino por fora do vidro da esquerda (`labio_pt`) sem os px escuros da legenda junto à quina;
  - `soleiras`: os vãos brancos de porta do PDF (`ajustes_casab.vaos_brancos`), cada um ajustado às faces e às pontas das paredes do PDF (`_soleira_no_pdf`, em 8 x), em Bege Bahia nítido com as faces em cinza fino (`SOLEIRAS_F`); também no Subsolo;
  - `esquadrias`: antes, as ondinhas do PDF que marcam as cortinas saem do piso (`ondas_fora`, `ONDAS_F`): perto do traço do PDF (`ajustes_casab.onda_cortina_b`), o px que destoa da mediana do piso da mesma linha toma o valor dela (a parede preta fica). Sem isso, o espelho das esquadrias levava as ondas para junto do vidro. Depois (`esquadrias_terreo`), os dois jardins voltam como estavam (`alfa_canteiros`): o espelho troca o px escuro de um lado da faixa pelo do outro, e nas folhagens escuras junto ao vidro trazia o vinílico e o travertino para dentro do canteiro, em pintas. Também volta a faixa sob a folha aberta da porta da suíte 3 (o espelho copiava o topo do guarda-roupa) e a faixa entre o sofá do living e as portas de correr do jardim de inverno (`ESQUADRIAS_F["de_volta_pt"]`: o espelho copiava a borda do sofá junto à porta), e ela fica em travertino (`travertino_pt`, no tom do travertino logo abaixo, `ref_pt`);
  - `cortinas`: as de linho da biblioteca (`ajustes_casab.cortinas_b`), depois das esquadrias: desenhadas antes, o espelho das esquadrias as copiava e saíam duplicadas;
  - `escadas`: antes, a pedra grande e as 6 lajes em cascata à esquerda do deck (`degraus_blocos`, `BLOCOS_F`: os blocos de 4 lados da ARQ_CONTRAPISO na `caixa_pt`, cada um em Bege Bahia com uma semente e um tom, na ordem de pintura do PDF, com o bocel no contorno e a sombra curta sobre o de baixo e a grama; e o triângulo da R14 no deck, com a ponta na borda da laje da direita, apontando para ela, `triangulos_pt`: a ponta e o sentido); depois, as duas escadas (os degraus do PDF em Bege Bahia, `degraus_bege`, com as linhas da R14) e as projeções;
  - `cobertura`;
  - `rotulos`.
- **Etapas do Subsolo** (`passos_subsolo`), as mesmas onde cabem: `pisos` (só na pegada), `bancadas`, `sauna` (os bancos em travertino, `bancos_sauna`, `SAUNA_F`), `pecas`, `tampas`, `vasos` (o vaso do BH sauna em marrom, `vasos_cor`, `VASOS_COR`), `biblioteca` (o chuveiro da ducha), `boxes` (os vidros contínuos do PDF, `boxes_vidro`, `BOXES_VIDRO`), `paredes` (em cinza 80, `PAREDES_F["cinza"]`), `soleiras`, `esquadrias` (com os batentes em cinza 80: `esquadrias_final(..., parede=)`), `escadas` (a de 6 degraus em Bege Bahia, sem linhas, com o sombreamento de subida e o S: `escada_sombreada`, `ESCADA_SOMBRA`), `hachura` (o terreno hachurado, a partir do Térreo final: rode o Térreo antes) e `rotulos` (com o SHAFT do PDF).
- **Subsolo, auditoria e banhos de 26/10** ("ok, aplique a lista"; "banho sauna: sanitário marrom, cuba esculpida em mármore travertino bruto e e pedra da bancada da cuba em granito marrom; banho serviço: cuba branca, pedra da pia em marrom granito, sanitário branco."): o motor é o mesmo das Casas C e D, então o que é só deste Subsolo vai por argumento em `passos_subsolo`, nunca por global: `bancadas(Q, img, borda=BANCADAS_F["borda_e9"], pedra="granito", cuba=cuba_travertino)` (o granito marrom de `fontes_procedurais.granito_referencia` nas duas bancadas; a cuba da ARQ_BANCADAS esculpida em travertino bruto pela `final3840_casaa.cuba_pedra`, `BANCADAS_F["cuba_travertino"]`; o `Quadro` ganhou o `q2p`, que a `Tela` da Casa A usa), `paredes(Q, img, cor=PAREDES_F["cinza"])`. O rótulo CIRCULAÇÃO vai pelo `PAVIMENTOS_B["Subsolo"]["ajustes"]` (corpo 1,0). Depois ("melhore o aspecto do marmore travertino bruto"): `pisos(..., bruto={"travertino": "piso"})` e `bancos_sauna(..., bruto="bancada")` trocam a foto lisa do travertino pelo travertino bruto da Casa A (`final3840_casaa.travertino_bruto`, estilos de `TRAVERTINO`), na luz do próprio piso; `piso_textura` só recebe `bruto` quando ele vem (as Casas C e D trocam o `piso_textura` por um de assinatura própria). E ("melhore a representação da cuba esculpida com o marmore travertino, mais claro"): `cuba_travertino` é uma rotina própria na `Tela` da Casa A (`BANCADAS_F["cuba_travertino"]`: o tom claro, o desenho calmo do travertino bruto, a borda larga com a quina, a bacia arredondada com a luz e a sombra por dentro, a válvula e a sombra curta); `bancadas(..., cuba=)` a desenha no contorno de fora do aro do PDF e tira esse retângulo da pedra da bancada. O chuveiro do deck da ducha (`ajustes_casab.CHUVEIRO_DUCHA`, que o PDF do Subsolo não tem) segue o chuveiro do deck do PDF do Térreo (`CHUVEIRO_DECK`) em relação ao canto do deck: a mesma distância da parede da sauna que lá da borda do deck, com o braço até a parede de baixo (usuário: "corrija o local da ducha externa da planta do subsolo, conforme está na planta do térreo" e "a ducha fica mais no canto"). Antes e depois: `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_2610_<trecho>_antes_depois.jpg`.
- **Bancadas** (pedido de 22/10: "troque o cinza das bancadas pelo tom areia", "cubas em branco", "preciso que as pedras estejam humanizadas"):
  - a pedra é a foto do Bege Bahia da biblioteca, na escala e levada ao tom areia (`BANCADAS_F`: `tom`, `contraste`), em toda peça da ARQ_BANCADAS;
  - as cubas da ARQ_BANCADAS (`cubas_bancada`: o retângulo com o aro fino nos quatro lados) são louça branca, com a bacia de cantos arredondados e a sombra interna; as da ARQ_LOUÇAS (cozinha, gourmet e bar) também saem brancas (`TERREO["inox_pt"]` vazio).
- **Peças do PDF** (`pecas_pdf`): na ordem de pintura do PDF, com o mapa de quem está por cima, então só aparece o traço que fica por cima. A cor é a mediana do render no miolo da peça. Cada peça tem um tipo:
  - tapete: grande e simples;
  - louça branca, ou metal nos detalhes miúdos;
  - madeira, com veio;
  - planta em vaso, que vira a planta da biblioteca;
  - o resto é objeto.
  Todas levam volume na borda, sombra curta para baixo e à esquerda e o traço fino do PDF; as hachuras densas ficam mais leves.
  As louças são lisas (sem a trama do tecido), com o traço mais leve (o aro de dentro da cuba, quase só o tom). A bacia (a louça dentro de outra, com 40 a 95% da área dela) é achada pela geometria, porque o aro é pintado depois e a cobre; ela leva a sombra interna do lado da luz e o fundo um tom abaixo. As banquetas da bancada gourmet são as `banqueta_linho` da biblioteca nos círculos do PDF (`BANQUETAS_PT`, `centros_banquetas`), entrando sob o tampo (a pedra cobre a parte delas que fica sob a bancada).
- **Rótulos** (`rotulos`, `ROTULOS_F`):
  - a caixa exata do texto (`_caixa_texto`, medida em cada opção de corpo e de quebra) procura, em até 3 m do ponto do PDF, o lugar livre mais perto, sempre dentro do seu ambiente e sem tocar objeto nem outro rótulo;
  - onde não cabe, quebra em duas linhas e depois desce o corpo (o corpo cheio vale mais que a distância, `corpo_custo`);
  - `ambientes_rotulos`: as paredes escuras do PDF, com os vãos entre trechos alinhados fechados até `vao_max_m` (portas e passagens); a região livre com mais de um ponto do PDF é repartida pela distância andando por dentro;
  - sem halo: o texto é preto ou branco pelo fundo (`cor_do_fundo`, luminância relativa do WCAG); os jardins, em branco;
  - o vidro do box divide o banho, e o lado do chuveiro (`duchas_box`: a ducha do PDF ao lado do vidro) fica fora de todo ambiente; o ponto que cai no box passa ao piso seco do mesmo banho;
  - `ROTULOS_F["textos"]`: o nome escrito no lugar do do PDF ("BH. GOURMET"); `ROTULOS_F["pontos"]`: o ponto (pt) de onde a busca parte (a prainha, abaixo das espreguiçadeiras).
- **Cache de etapas:** `<$POE642_CACHE ou a pasta temporária>/poe642_casab_etapas/final3840/<Pavimento>_<etapa>.png`. `--de <etapa>` recomeça daquela etapa com a anterior do cache.

```bash
python3 final3840_casab.py Terreo                  # -> ../../POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png
python3 final3840_casab.py Subsolo                 # depois do Térreo (a hachura vem dele)
python3 final3840_casab.py Terreo --de bancadas    # refaz só dali em diante
# depois, rodape_entrega.py e pdf_entrega.py como acima
```

## A final da Casa C em 3840 px: `final3840_casac.py`

Pedido do usuário (22/10/26), às perguntas dos mapas do pente fino da Casa C: "1. BANCO EM BRONZE FOSCO; 2. OK; 3. DE ACORDO; 4. PEDRA AREIA; 5. EM 3840 PX". A Casa C tem a mesma folha, o mesmo recorte, a mesma escala e as mesmas cores de legenda da Casa B, então a final usa o motor do `final3840_casab.py` (e o dos `ajustes_casab.py`) como está. `contexto_c()` aponta os dois módulos para a Casa C e troca o que é da casa:
- **Pastas e fontes:** a config, o PDF, a base chapada (v2 16x9) e o render retocado e aprovado de 14/10 (`PAVIMENTOS_C`), levado ao quadro (`quadro_inicial_c`, em cache); o afim do render (`AFIM_QR_C`).
- **Pisos** (`PISOS_C`, `piso_textura_c`): os da legenda da Casa C, e o granito, o Bege Bahia e a grama levados ao tom das finais da Casa B (`TONS_C`: a mediana da textura na máscara vai ao tom).
- **Arcos das portas** (`arcos_porta_c`, `ARCOS_C`, R3): os da ARQ_PAREDE de 15 a 130 pt (entra a pivotante do hall, de 121,9 pt) e os das portas dos boxes dos BH master 1 e 2, que o PDF da Casa C desenha na ARQ_BANCADAS: 30 no Térreo e 3 no Subsolo, no piso em volta.
- **Peças do PDF** (`pecas_c`): os tapetes grandes por baixo dos móveis (`tapetes_por_baixo`); ficam como no render (`FORA_PECAS_C`) as banquetas sob o braço da bancada gourmet (decisão de 14/10), os dois conjuntos do estar e a sala TV (no PDF, o tapete orgânico é um desenho de 210 traços que cobria o sofá curvo, e as poltronas e os sofás são só contorno); o aparador comprido da circulação não é tapete (`NAO_TAPETE_C`).
- **Camas e bancos** (usuário: "PODE MANTER O JOGO DE CAMA QUE ESTAVA ANTES." e "MANTENHA OS BANCOS QUE ESTAVAM EM FRENTE AS CAMAS TAMBÉM"): os do render aprovado, colados sobre a final com a sombra curta (`camas_render`, `CAMAS_C`, `BANCOS_C`).
- **Peças do render sobre o piso novo** (`pecas_do_render`, com a máscara `neutro` ou `verde`): onde a legenda pinta o piso por dentro do contorno do PDF, os pisos cortavam a peça do render que fica; entram os px dela (os aparelhos da academia; os dois vasos junto ao sofá curvo, `VASOS_C`), com a sombra curta. E, no estar e na sala TV, `restos_piso`: o piso novo em manchas de até 400 px entre as linhas dos estofados volta ao render.
- **Biblioteca:** guarda-roupas com cabides (`GUARDA_ROUPAS_C`, 11 peças), cooktops de 5 bocas (`COOKTOPS_C`), as 4 banquetas de linho da ilha sob o tampo (`banquetas_c`, `BANQUETAS_C`), carros prata alinhados (`CARROS_C`, nos retângulos do PDF, `CARROS_PT`).
- **Bancadas** (`bancadas_c`): a pedra areia e as cubas brancas da Casa B, sem os arcos das portas dos boxes que estão na ARQ_BANCADAS.
- **Deck:** o banco em L em bronze fosco (o `BANCO_DECK` da Casa B) e o chuveiro (`CHUVEIRO_C`).
- **Jardins** (`jardins_c`, `JARDINS_C`, `alfa_canteiros_c`): jardim de inverno, jardim de inverno 2 e jardim 1, só verdes, no canteiro do PDF.
- **Guarda-corpos de vidro** (`GUARDA_CORPOS_C`): as 4 lâminas da ARQ_ELEMENTOS FIXOS.
- **Projeções** (`PROJECOES_C`, `PROJECOES_JARDINS_C`, `PROJECOES_TRACO_C`): claraboia, closets e o X do BH master 2 em cinza escuro sobre os pisos claros; os X dos jardins e da área descoberta em cinza claro sobre o verde e o granito.
- **Esquadrias** (`VIDROS_FORA_C`): no deck, na piscina, na prainha e no spa, as paredes estruturais da ARQ_PAREDE são brancas e finas como vidro e não são esquadria; com as bordas de fora e o vidro da borda infinita, formavam uma esquadria do tamanho da piscina, e o redesenho clareava os degraus da prainha. A zona fica fora; o vidro da borda infinita é o do render.
- **Escadas** (`escadas_c`, `degraus_linhas`, R14): no Térreo, os degraus largos (`DEGRAUS_LARGOS_T`, triângulo no 10 apontando para cima) e a estreita (`ESCADA_ESTREITA_T`, triângulo junto ao deck apontando para a esquerda); no Subsolo (`escadas_s`), os largos com o triângulo no 1 apontando para baixo (`DEGRAUS_LARGOS_S`) e a estreita esmaecida com o triângulo no 11 apontando para a direita (`TRIANGULO_ESTREITA_S`).
- **Soleira do elevador** (`soleira_elevador`, `SOLEIRA_ELEVADOR_C`): em inox escovado, entre os batentes do PDF, nos dois pavimentos (não é vão branco do PDF, então a etapa das soleiras não a pegava).
- **Subsolo** (`passos_subsolo_c`): pisos só na pegada (`pegada_subsolo`: o Subsolo, o pátio, os degraus largos e o caminho, e a escada estreita esmaecida), a floreira junto à sauna (`floreira_s`, `FLOREIRA_S`), os bancos da sauna em travertino (`bancos_sauna_c`, `SAUNA_C`), os aparelhos da academia do render aprovado (etapa `aparelhos`, `pecas_do_render` com `FORA_PECAS_S`: pelo PDF saíam silhuetas cinza chapadas; entram os px neutros do render, sobre o vinílico novo, com a sombra curta), o rótulo da VARANDA SUBSOLO (o filtro dos títulos da folha, `A.FORA`, passa a ser "1º SUBSOLO"), e o resto do lote na hachura do Térreo final (`AJ.subsolo_hachurado`).
- **Cache de etapas:** `<$POE642_CACHE ou a pasta temporária>/poe642_casac_etapas/final3840/<Pavimento>_<etapa>.png`.

```bash
python3 final3840_casac.py Terreo               # -> ../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png
python3 final3840_casac.py Subsolo              # depois do Térreo (a hachura vem dele)
python3 final3840_casac.py Terreo --de pecas    # refaz só dali em diante; --ate <etapa> para nela
# depois, rodape_entrega.py --no-quadro e pdf_entrega.py, com a config da Casa C
```

## A final da Casa D em 3840 px: `final3840_casad.py`

Pedido do usuário (22/10/26), às perguntas dos mapas do pente fino da Casa D: "1. Igual ao das outras casas 2. Em Madeira 3. Sim, para os 3 4. Areia 5. Os do render 6. Hachura". A Casa D tem a mesma folha, o mesmo recorte, a mesma escala e as mesmas cores de legenda das Casas B e C: usa o motor do `final3840_casab.py` e as rotinas do `final3840_casac.py` (`C.`), que `contexto_d()` aponta para a Casa D. O que é da casa:
- **Fontes:** o render retocado e aprovado do Térreo com o Barlavento (2000 px) e a final do Subsolo de 15/10 (3840 px), levados ao quadro (`PAVIMENTOS_D`, `AFIM_QR_D`).
- **Pisos** (`PISOS_D`, `piso_textura_d`): travertino, vinílico, granito, Bege Bahia e grama no Térreo (sem deck nem pedra portuguesa; o acesso de veículos é granito); no tom das finais das Casas B e C (`TONS_D`: resposta 1). A luz do granito sai sem os carros do render (o grafite e o azul-marinho, quase no tom do granito, deixavam manchas escuras em volta dos carros novos).
- **Carros** (`carros_d`, `CARROS_D`, R12): o carro branco do meio do render é o modelo, achado pelo que foge do granito em volta (o granito do render é quase neutro, e o filtro neutro das Casas B e C juntava os três carros); prata, 4,70 x 1,85 m, alinhados nos centros do PDF.
- **Vegetação** (`plantas_do_gramado_d`, `VEGETACAO_D`, item 1): as plantas da biblioteca nos lugares das do render, só nos cantos da esquerda, junto à piscina e junto à suíte 3; saem as fileiras que o achado tirava da sombra do muro de cima e dos X tracejados na grama, e as árvores de 4 m junto à suíte 3.
- **Jardins** (`jardins_d`, `JARDINS_D`): o do lavabo e o da sala íntima, só verdes; os dois dão para o gramado, e a grama e o traço em volta voltam como eram depois do canteiro (a limpeza das folhas do motor tomava a grama por folha).
- **Peças:** camas e bancos do render (`CAMAS_D`, `BANCOS_D`, resposta 5); o estar da suíte 3 do render (`FORA_PECAS_D`: no PDF, o sofá está na INS_INSTALAÇÕES HIDRÁULICAS e a mesa na DOC_LINHAS, e o tapete os cobria); os vasos do hall e a planta da bancada gourmet do render (`VASOS_D`).
- **Cubas** (`cubas_bancada_d`, `CUBAS_EXTRA_D`): as do banho master, do lavabo e do WC DCE, que o PDF desenha sem o aro, entram em louça branca com as outras. No Subsolo, a bancada do vestiário com a cuba vem da final aprovada (`CUBA_VESTIARIO_S`; no PDF, só traço).
- **Biblioteca:** cooktops de 5 bocas (`COOKTOPS_D`) e as 4 banquetas da ilha gourmet sob o tampo (`banquetas_d`: no PDF da Casa D, desenhos de traço da ARQ_LOUÇAS E METAIS).
- **Brises em madeira** (`brises_madeira`, `BRISES_D`, resposta 2): cada ripa da ARQ_ELEMENTOS FIXOS (preenchimento branco pequeno) na madeira da biblioteca, com o veio no comprimento, um tom por ripa, o contorno fino e a sombra curta, nas 10 caixas (garagem, hall, suíte master, suíte 3, fachada de baixo, gourmet).
- **Guarda-corpos de vidro** (`GUARDA_CORPOS_D`): o L do terraço junto aos blocos e o vão da escada.
- **Projeções** (`PROJECOES_D`, `PROJECOES_CLARAS_D`, `COBERTURA_D`): os X do banho master em cinza escuro; os da garagem, da faixa abaixo dela, da área descoberta e do jardim do lavabo, e a cobertura da garagem, em cinza claro.
- **Escadas** (resposta 3): a de 16 degraus (`ESCADA_T`, triângulo no 16 para a esquerda; no Subsolo, `ESCADA_S`, cheia até o corte do degrau 7 e esmaecida depois, triângulo no 1 para a direita) e os 10 blocos em cascata (`BLOCOS_D`, `F.degraus_blocos`, triângulo no terraço para a esquerda).
- **Rótulos:** os títulos das folhas são "0. TÉRREO" e "-1. 1º SUBSOLO" (`A.FORA`, para o DCE TÉRREO e o WC DCE TÉRREO ficarem); a SUÍTE MASTER e a GARAGEM partem de outro ponto (`ROTULOS_PONTOS_D`).
- **Subsolo** (`passos_subsolo_d`): os aparelhos da academia do render, uma caixa por grupo (`FORA_PECAS_S`), a cama do DCE 1 do render (`CAMAS_S`) e, em cor cheia, só o Subsolo e o pátio (`pegada_subsolo`, sem os traços finos: o tracejado da laje fechava a faixa verde, que vai para a hachura, resposta 6).
- **Cache de etapas:** `<$POE642_CACHE ou a pasta temporária>/poe642_casad_etapas/final3840/<Pavimento>_<etapa>.png`.

```bash
python3 final3840_casad.py Terreo               # -> ../../POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png
python3 final3840_casad.py Subsolo              # depois do Térreo (a hachura vem dele)
python3 rodape_entrega.py --config ../../POE642_CasaD/config_bases.json --no-quadro \
    --render Terreo=../../POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png \
    --render Subsolo=../../POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_final_rotulos.png
python3 pdf_entrega.py --config ../../POE642_CasaD/config_bases.json
```

## Ajustes da Casa A depois da conferência: `ajustes_casaa.py`

Os itens da conferência (e, desde 21/10/26, os do pente fino pelas regras, com o prefixo `pf` em `ITENS`) corrigidos, um por vez, na imagem aprovada (2000 px). Saída `../renders/<imagem aprovada>_ajustes.png` (+ `_camada.png`), que o `rotulos_casaa.py` usa no lugar da aprovada. O alinhamento ao quadro comum continua vindo da imagem aprovada (`PAVIMENTOS[...]["aprovada"]`, `no_quadro_fixo`), para que só os trechos ajustados mudem na prancha. O PDF de cada pavimento chega à imagem pelo quadro comum e pelo afim `AFIM_QR` do pavimento (`pdf_pavimento`). Depois: `rotulos_casaa.py`, `rodape_entrega.py --no-quadro` e `pdf_entrega.py`.

```bash
python3 ajustes_casaa.py Subsolo      # itens 1 a 13: chuveiro e vidro do banho de serviço; banco da sauna; escada; portas de vidro da academia; janelas; traço da circulação; juntas; cubas; boxes; divisória dos banhos; Bege Bahia; bancada do banho de serviço; gramado junto à escada (roda na ordem 1, 2, 7, 11, 3 a 10, 12, 13)
python3 rotulos_casaa.py Subsolo
python3 rodape_entrega.py --no-quadro --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png
python3 ajustes_casaa.py Terreo       # itens 1, 2 e 8 (pilares em preto; sala de estar; jardim verde), os rejuntes do piso interno, os tanques, o gás (piso e porta), a porta do jardim, os portões da área descoberta, a escada caracol, as portas no granito (folhas do PDF, arcos em cinza fino), os eletrodomésticos em inox a bancada gourmet (área molhada, divisória, cuba e torneira) a bancada da cozinha em pedra (área molhada, cubas e torneiras) o estar sob a projeção (item 3: 4 poltronas em X e a mesa triangular) e o lavabo (item 5: bancada com a cuba esculpida, vaso suspenso e a claraboia; os rótulos PROJ. CLARABOIA e SHAFT entram pela lista `incluir` do `rotulos_casaa.py`), a porta pivotante até o hall externo, com o arco pequeno, a escada interna (cheia até o corte no 7º degrau, esmaecida depois, no gramado aprovado) o motorista (itens 11 e 12: cama, bancada com a cuba, box e chuveiro) e os carros (cada um numa cor, desalinhados), e por último as portas sem os arcos (`sem_arcos`: os arcos da ARQ_PAREDE saem, as folhas ficam; a porta camarão sem o cinza do motor)
python3 rotulos_casaa.py Terreo
python3 rodape_entrega.py --no-quadro --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_rotulos.png
python3 pdf_entrega.py
```

**Pente fino pelas regras, Térreo (21/10/26):**
- item 1, escadas (R14): `escada_interna` e `caracol` ganharam a R14 (`ESCADA_INT["r14"]`, `CARACOL["r14"]`: linha suave nos bocéis cheios, esmaecidos tracejados, sem a linha de corte, triângulo no degrau 1); `escadas_externas_r14` faz a do deck para o Subsolo (os traços escuros do motor saem por mediana; `retoque_terreo_casae.escada_linhas` com o corte do PDF do Subsolo) e a larga (o L de cada bloco do ARQ_CONTRAPISO sobre o de baixo, com a linha e a sombra curta; triângulo no degrau 12). Funções comuns da R14: `R14`, `r14_linha`, `r14_tracejado`, `r14_poligono`, `r14_triangulo`.
- item 3, carros (R12): `CARROS_A["r12"]` e `carros_r12_a`: os três carros saem como antes e o carro branco do render, levado ao prata do carro da Casa E (quantis de luminância e o tom levemente frio), entra a 4,70 x 1,85 m no centro de cada carro do PDF, alinhados na mesma linha.
- item 4, projeções (R8, R9): `PROJECOES_A` e `projecoes_a`, o último item do Térreo: o L da cobertura (o tracejado da ARQ_CONTRAPISO) e a laje superior em volta da caracol (DOC_LINHAS E PROJEÇÕES), no traço das projeções do Térreo da Casa E, por cima de tudo menos das paredes.
- item 5, vidros finos: `VIDROS_A` e `vidros_finos`, com as funções do item 8 do pente fino do Térreo da Casa E (`retoque_terreo_casae.esquadria_limpar` e `esquadria_desenhar`) e a cadeia PDF -> imagem da Casa A: as quatro portas de correr entre a varanda e as salas, em dois planos; no vão da pivotante do hall, só a limpeza.
- item 6, armários até o teto: `ARMARIOS_A` e `armarios_teto`. Os quatro retângulos com diagonal do PDF na marcenaria areia com o veio de um armário aprovado da Casa D (no comprido de cada peça, espelhado até cobrir), sem a diagonal, menos as paredes pretas do render; contorno fino nas faces livres, como na Casa E; a sombra de móvel baixo sai do granito face a face (perfil contra o patamar, como na Casa D). O braço da bancada dos tanques (ARQ_BANCADAS), também lilás, entra no quartzo.
- item 7, grama na escala: `GRAMA_A` e `grama_escala`, como o item 42 do Térreo da Casa E (`texturas_escala.mascara_grama` e `trocar_grama`, no tom do render). O gramado é o branco da base (o lote da Casa A é branco nela) dentro do lote, em manchas grandes e verdes no render; o jardim interno fica. As plantas verde-sálvia saem pelo desenho das folhas: `mascara_grama` aceita agora `est_lim`, `lum` e `verde_max` (padrões da Casa E; aqui 4, (35, 125) e 130). Os tracejados escuros do motor (afastamento, trechos da cobertura) são achados no render e voltam depois da troca.
- item 8, deck: `DECK_A` e `deck_referencia`. A madeira da referência (`_texturas/madeira.jpg`), régua a régua (cada régua do deck é uma régua inteira da foto, sorteada, deslocada e espelhada ao acaso, na largura de ~20 cm da referência), deitada, com a luz larga e as sombras do lugar; o deck é a mancha da madeira da base (`base_terreo`, a base levada à imagem, usada também pela grama).
- item 9, Bege Bahia: `BEGE_A` e `bege_referencia_a`, como o item 43 do Térreo da Casa E (`retoque_terreo_casae.BEGE`; pontinhos escuros fora e `texturas_escala.retexturizar` no tom da foto), no #E8E8E8 da base (fechado onde o render é piso claro); o anel que o `retexturizar` deixa em volta dos objetos vira o piso novo de perto. Roda antes das escadas externas.
- item 10, granito marrom: `GRANITO_A` e `granito_referencia_a`, a rotina do granito do Térreo da Casa E (`retoque_terreo_casae.granito_tom`, constantes `GRANITO_TOM`): pontos claros fora, a grade de manchas do motor fora e o desenho e o tom da referência do usuário (`texturas_escala.trocar_granito`), na mancha do granito da base (#BFA79E, traços fechados e buracos de até 20 mil px preenchidos, para o anel entre os carros do PDF e os da R12 entrar).
- item 11, pedra portuguesa: `PEDRA_A`, `pedra_leque` (o último item do Térreo) e `pedra_final` (chamada pelo `rotulos_casaa.py` na final). O item 47 do Térreo da Casa E (`retoque_terreo_casae.PEDRA`, `texturas_escala.trocar_pedra_portuguesa`, fonte "leque", com a franja da borda), na pedra da base (#B98A55, com folga) onde o px ainda é o caramelo do motor; as linhas da DOC_LINHAS E PROJEÇÕES (o X da área descoberta, o afastamento) entram por cima em cinza-escuro fino (`linhas_sobre_pedra`). A máscara vai para `renders/POE642_CasaA_PH_Terreo_pedra_mascara.png`.
- item 12, vegetação: `VEG_A` e `vegetacao_a`, a opção A do Térreo da Casa E (`retoque_terreo_casae.VEGETACAO`, `sprite_referencia` e `pousar_planta`) nas cinco manchas grandes de planta do gramado (as do item 7, `gramado_plantas`, na imagem aprovada). As folhas do motor fora do verde (só as ligadas às manchas por px verdes) e, perto delas, os fragmentos e as sombras sobre os pisos viram o material da base copiado ao lado (`copiar_material`; no Bege Bahia, sem os traços finos da base, como o contorno dos carros, nem a sombra junto às paredes da casa); fora do lote, branco; sobre o muro, o perfil da própria linha. Sob as manchas, a grama do item 7 (mesmo desenho e semente); por cima, as plantas da referência no tamanho real, com a copa dentro do verde.
- item 13, mesa de jantar oval: `MESA_A` e `mesa_oval`. O tampo oval do PDF (ARQ_MARCENARIA, 3,00 x 1,20 m) no lugar do retangular chanfrado do motor, com a madeira do render estendida linha a linha em espelho, por cima da frente das cadeiras; as 8 cadeiras do render ficam (o PDF tem 8); o piso que sobra vem do entorno e a sombra curta passa ao contorno novo pela razão entre a sombra nova e a velha.
- item 14, escritório: `ESCRITORIO_A` e `escritorio_cadeira`. As duas cadeiras do motor em cima da mesa saem: cada linha do travertino volta entre o piso dos dois lados, com o grão de um trecho limpo. A cadeira de escritório entra no contorno do PDF (ARQ_LAYOUT HUMANIZAÇÃO: o assento, recortado sem o pino e as alavancas, a faixa do encosto e os braços), em grafite, com o volume, o vinco e a sombra das poltronas do estar sob a projeção, e o tampo da mesa por cima. As duas de visita do render ficam.
- item 15, banho da varanda: `BANHO_VARANDA` e `banho_varanda`. A bacia do motor e a faixa pontilhada do trilho saem (o piso de cada coluna entre as linhas de cima e de baixo; no lugar da bacia, o piso da mesma linha à esquerda, no tom de cada coluna). Entram as duas folhas do box e o chuveiro de parede do PDF com `retoque_subsolo_casae.vidro_box` e `chuveiro`, como no banho de serviço do Subsolo.
- item 16, soleiras (R13): `SOLEIRAS_A` e `soleiras_a`. As 13 portas de giro conferidas contra o vão branco do PDF; nos quatro que têm soleira (escritório, lavabo, gás e jardim), o vão exato em Bege Bahia na escala, no tom do item 9, com as faces da parede em cinza fino, como as soleiras do Térreo da Casa E. Nas outras nove, o piso atravessa o vão, e nada muda.

**Pente fino pelas regras, Subsolo (21/10/26):**
- item 10, o "²" dos rótulos: só o ciclo, sem mudança de código (o Subsolo ainda não tinha passado pela rotina comum dos rótulos de 20/10).
- item 1, só o Subsolo com o terreno hachurado (R2): `SUBSOLO_R2`, `so_subsolo` (o último item do Subsolo) e `subsolo_hachurado`. No ajuste, a pegada do Subsolo (as peças cheias da ARQ_CONTRAPISO e da ARQ_PAREDE na caixa do Subsolo, a escada do deck e o gramado do item 13) fica e o resto vira branco; a máscara vai para `renders/POE642_CasaA_PH_Subsolo_pegada_mascara.png`. Na final, o `rotulos_casaa.py` (chave `pegada`) a leva ao quadro e hachura, fora dela, o lote do Térreo final (`renders/POE642_CasaA_PH_Terreo_final_rotulos.png`), como `retoque_subsolo_casae.contexto_hachura`. O Subsolo depende da final do Térreo.
- item 2, gramado: `GRAMADO_ESCADA["fonte"]` passa do Térreo aprovado ao Térreo com os ajustes (a grama da referência do item 7 do Térreo), com a mancha verde da fonte fechada e preenchida (as folhas claras da referência não passam no teste de verde). O Subsolo depende também dos ajustes do Térreo.
- item 3, escada do deck (R14): `ESCADA_DECK_SUB` e `escada_deck_subsolo`, com `retoque_terreo_casae.escada_linhas` (a rotina da mesma escada no Térreo, com a cadeia do Subsolo): lado vivo à direita do corte, com a linha suave e a sombra curta nos bocéis (a sombra de espelho de `ESCADA` passa a 0); depois do corte, o creme esmaecido e liso, tracejado; triângulo no 1º degrau, apontando para a esquerda.
- item 4, portas sem arcos (R3): `SEM_ARCOS_SUB` e `sem_arcos_subsolo`. Os 5 arcos da ARQ_PAREDE numa faixa de 4 px, refeitos por inpaint de raio 2 (aqui os arcos do render são traços de 1 px; o `arcos.remover_arcos` do Térreo quebrava a grade da pastilha do banho de serviço).
- item 5, portas, vidros e janelas finos: `VIDROS_SUB`, `vidros_subsolo`, `vidro_fino` e `espelhar_faixa`. A porta de correr entre a circulação interna e a externa: o traço preto do motor sai (uma faixa de 6 px; a metade de cima recebe o Bege Bahia de cima em espelho, a de baixo o de baixo) e entram as duas folhas de vidro desencontradas do PDF, no vidro das portas da academia, com a borda de 0,25 px de cada lado (no Bege Bahia, a de 1/8 px não lia) e as pontas em alumínio. As 5 folhas das portas de giro (R3): o bloco cinza do depósito e os traços escuros do banho de serviço, da sauna e dos banhos feminino e masculino saem pela mesma faixa espelhada, e entram as folhas do PDF, brancas (`retoque_subsolo_casae.PORTA`), com o contorno de 0,25 px. A janela entre o depósito e a academia: o vão da parede em vidro claro. O vidro de cima da sauna: em cada linha, a mediana do trecho, sem as duas marcas do montante.
- item 6, Bege Bahia como a referência (seção 18): `BEGE_SUB` e `bege_subsolo`, antes do item 5. A máscara é a do item 11 de 19/10 (`bege_mascaras`, extraída de `bege_bahia` sem mudar o resultado), sem o verde do gramado. O piso vai ao desenho da biblioteca na escala e ao tom da foto pela rotina do item 9 do Térreo, agora em `bege_na_referencia` (extraída de `bege_referencia_a`; o Térreo sai igual px a px): os pontinhos escuros do motor saem antes, e o anel em volta do que foge da luz vai ao piso novo depois. A borda de 1 a 2 px da máscara, que `retexturizar` não troca (junto às paredes, ao vidro da sauna e ao gramado), vai ao piso novo de perto, só onde é claramente piso (luminância de 170 para cima).
- item 7, travertino na escala (R1 e seção 18): `TRAV_SUB` e `travertino_subsolo`, antes do item 5, como o Subsolo da Casa E (`retoque_subsolo_casae.texturas_na_escala`). A fonte são dois trechos limpos do travertino do Térreo com os ajustes, tecidos por `retoque_bege_bahia_terreo.quilting` com os espelhos que mantêm o veio na horizontal; o desenho inteiro entra (força 1,4) sobre a luz do lugar (raio de 1 m). A máscara é o travertino da base de entrega do Subsolo (#DCD9CA; `base_terreo` passa a aceitar o pavimento) no hall, na sauna com a antessala e nos banhos, com os traços finos da base fechados (3 x 3) e a faixa da sauna junto ao vidro (na base, na cor do pátio). Os objetos saem pelo PDF (ARQ_LOUÇAS E METAIS e ARQ_BANCADAS, com o que os traços fecham; a divisória; o branco dos vasos que toca as louças do PDF), e não pela luz: `texturas_escala.retexturizar` ganhou `fugir=False` (o padrão continua `True`), porque fugindo da luz os riscos escuros do motor ficavam e o piso saía em retalhos. A borda de 1 a 2 px vai ao piso novo de perto. Os vidros dos boxes (`vidro_box`) e a borda do banco da sauna (`banco_sauna`) são redesenhados por cima.
- item 8, shafts e projeções (R8): `PROJECOES_SUB` e `projecoes_subsolo`, depois do item 5, como `retoque_1pav_casae.projecoes_1pav`. Nos dois shafts, o retângulo de dentro do PDF, arredondado para dentro, fica branco onde não é parede preta (luminância acima de 30), e o X entra com os traços tracejados do próprio PDF (DOC_LINHAS E PROJEÇÕES), em cinza médio, só no branco. Os três retângulos da mesma camada (junto às paredes de cima e da direita do depósito e à de baixo da academia) entram em traço contínuo de 0,6 px: cinza médio no Bege Bahia, cinza claro na madeira. O elevador fica como está.
- item 9, soleiras (R13): `SOLEIRAS_SUB` e `soleiras_subsolo`, com `desenhar_soleiras` (extraída de `soleiras_a`, que sai igual px a px, e agora com `fora`: o que fica por cima do vão). Conferidas as 10 portas no PDF: só dois vãos são brancos, o da academia para o hall (com as folhas de vidro e os batentes do item 4 de 19/10 por cima, em `fora`) e o do elevador. Nas outras oito, o piso atravessa o vão.

**Pente fino pelas regras, 1º Pavimento (21/10/26):**
- a cadeia de ajustes, como a dos outros pavimentos: a imagem aprovada é `renders/POE642_CasaA_PH_1Pavimento_v7_final2.png` (`APROVADAS`), a saída `..._v7_final2_ajustes.png`, que o `rotulos_casaa.py` lê (chave `aprovada` para o afim do quadro). O afim quadro -> imagem (`AFIM_QR["1Pavimento"]`) foi medido como os outros (SIFT entre a base de entrega reduzida a 2000 px e a imagem: 107 pontos, 0,4 px; o mesmo cálculo reproduz o do Subsolo).
- item 16, o "²" dos rótulos: só o ciclo, sem mudança de código; na prancha mudam só os 21 "²".
- item 1, o Térreo nublado em volta (seção 11): `PEGADA_1PAV` e `so_1pavimento` (o último item do 1º Pavimento) e, no `rotulos_casaa.py`, a chave `nublado`, `final_imagem` (a final sem os rótulos; o `final_rotulos` escreve os rótulos sobre ela), `nublar` e `tracejado_lote`. A pegada sai do próprio render aprovado, como em `entorno_esmaecido.pegada` (o que tem algum canal abaixo de 215, em manchas grandes, fechado 9 x 9, sem furos, aberto 5 x 5): o PDF do 1º Pavimento traz o Térreo nas mesmas camadas. Ela vai a `renders/POE642_CasaA_PH_1Pavimento_pegada_mascara.png`, e fora dela o ajuste fica branco. Na final, fora da pegada, o Térreo final sem rótulos (`final_imagem("Terreo")`, no mesmo quadro) nublado com o `NUBLADO` do `entorno_esmaecido` (70% de branco, 80% da saturação, desfoque de 1,2 px), e por cima as linhas tracejadas do lote, do PDF (os traços de 0,85 pt da camada sem nome, em cinza 140, 1,2 px): no render estavam quase brancas e sumiam no nublado. O 1º Pavimento depende da final do Térreo.
- item 2, portas sem arcos (R3): `SEM_ARCOS_1PAV` e `sem_arcos_1pav`, com `sem_arcos_pdf(out, chave, busca)` (a do Subsolo, item 4, que com `busca=None` sai igual px a px) e `inpaint_sem_parede`. Os 11 arcos da ARQ_PAREDE numa faixa de 4 px, refeitos por inpaint de raio 2, sem servir de fonte nem mudar: a parede (luminância abaixo de 60, com 1 px de folga; o preto do batente virava mancha no banho 3), as linhas retas do desenho (o escuro, 8 abaixo da mediana de 9 px, em fio de 15 px ou mais, em pé ou deitado: a borda da bancada do banho 2, as folhas) e, na faixa de 9 px de cada arco, o piso 30 mais claro que a mediana dela (a circulação entrava como um dente no vinílico da suíte 1). Segunda passada, na mesma faixa: o que ainda é escuro (alguns arcos do render passam 2 a 3 px para dentro do arco do PDF), a mais de 2 px dos batentes do PDF; junto às folhas do PDF (os brancos de 12 px ou mais, 3 vezes mais compridos que largos), a até 4 px, fica só a linha da folha (o escuro em fio de 7 px no sentido dela), e sai o toco do arco que chega à ponta.
- item 3, escadas (R14 e seção 5): `escadas_1pav` = `escada_u_1pav` (config `ESCADA_U_1PAV`) e `caracol_1pav` (`CARACOL_1PAV`). Escada em U: no PDF do 1º Pavimento ela desce daqui (o "D" junto ao degrau 20, que é o piso da circulação), inteira, sem corte: lance de baixo da esquerda para a direita (19 a 11), patamar (10), lance de cima de volta (9 a 1). Os lances e o patamar do PDF recebem o travertino da escada do Térreo (`ESCADA_INT`: o mesmo trecho do hall do Térreo aprovado, tecido por `quilting`, na mesma cor); em cada bocel, a linha suave e a sombra curta no degrau de baixo (`R14`, como `retoque_terreo_casae.escada_linhas`): à direita no lance de baixo, à esquerda no de cima, e o bocel do degrau 11 sombreia o patamar; o degrau 1, junto ao guarda-corpo, fica sem linha. Contorno da escada e do vão em cinza (o do render, limpo, 0,9 px). O triângulo (24 x 26 cm) no degrau 19, a 10 cm do início, apontando para a direita. A ponta de seta e o "D" do motor, junto ao guarda-corpo, saem antes (inpaint, com o guarda-corpo, o escuro em fio vertical de 15 px, como fixo). Caracol da saleta: o "D" e a seta do PDF ficam no degrau junto ao 0°, apontando para baixo (desce no sentido horário). No trecho cheio do render (de 0,6° a 93,1°, cinco degraus de madeira), os riscos do motor saem por inpaint e entram os bocéis do PDF (19,1°, 37,6°, 56,1° e 74,6°) com a linha suave e a sombra da R14 no lado horário; o triângulo a 70% e a 38 pt do centro (como na caracol do Térreo), no degrau do "D", apontando para a descida. No resto, o branco limpo (sem a linha de percurso nem o símbolo do corte) e os 14 bocéis do PDF tracejados no cinza da R14. Guardas (0° e 93,1°), anel do corrimão, pilar e contorno ficam.
- item 4, guarda-roupas com cabides (R11): `GUARDA_ROUPAS_1PAV` e `guarda_roupas_1pav`, como `retoque_1pav_casae.guarda_roupas` (item 5 da Casa E, de onde vêm os tons `miolo` e `moldura`). No PDF do 1º Pavimento da Casa A, os guarda-roupas são os retângulos com diagonal da DOC_LINHAS E PROJEÇÕES (os do closet 3, 2 e 1 em L, dois trechos; o do closet master em U, três; o canto fica num dos trechos). Cada trecho recebe o `_texturas/elementos.guarda_roupa` (aberto, visto de cima, cabides a cada ~12 cm, `barra=True`), no tamanho do PDF, em 4x, girado com as portas do lado do closet (aqui dado em cada trecho: `direita`, `baixo`, `esquerda` ou `cima`). Os retângulos com diagonal da circulação e do quarto de serviço são armários até o teto (item 5).
- item 5, armários até o teto (seção 7): `ARMARIOS_1PAV` e `armarios_1pav`, com `armarios_ate_o_teto(out, chave, q)`, a rotina do Térreo (item 6) generalizada (`armarios_teto` a chama com `ARMARIOS_A`, e o Térreo sai igual px a px; o braço da bancada dos tanques só entra se a config tiver `bancada`). Os dois retângulos com diagonal da DOC_LINHAS que não são guarda-roupa: o da circulação, sob o banho 3 (faces livres embaixo e à direita, junto ao guarda-corpo da escada), e o do quarto de serviço (face livre à esquerda). A sombra de móvel baixo do motor sai do vinílico nas faces livres (7 px, até 42%, na circulação; 3 px no quarto de serviço), a marcenaria areia aprovada entra com o veio no comprido, e o contorno fino nas faces livres. Na sala íntima o PDF não tem retângulo com diagonal (o painel de madeira é o da TV, o retângulo branco com a TV no PDF) e ele fica.
- item 6, bancos ao pé das camas (seção 8): `BANCOS_1PAV` e `bancos_1pav`, como `retoque_1pav_casae.bancos_camas` (item 12 da Casa E; os números vêm de lá, `BANCOS`, e a sombra é a do banco do Térreo, `BANCO_VARANDA`). No PDF (ARQ_LAYOUT HUMANIZAÇÃO): um banco de 90,7 x 22,7 pt no pé de cada cama de casal (suíte 3, abaixo da cama; suíte 2 e master, acima) e um banquinho de 51 x 17 pt no pé de cada cama de solteiro da suíte 1. Cada um entra no pé da cama do render (a primeira queda de luz depois do edredom, na coluna do meio), a 1 px dela, na largura e na altura do PDF, estofado em bege com a almofada da Casa E (`almofada`: o assento do meio do sofá do render da Casa E, o mesmo trecho que ela usou), a trama fina e o contorno bege escuro. No `rotulos_casaa.py`, os rótulos das suítes 3 e 2, que caíam sobre os bancos, vão ao piso livre mais próximo (R7): o da 3 abaixo do banco, no tapete, entre ele e a bancada; o da 2 à direita da cama, antes do guarda-roupa.
- item 7, criados-mudos da suíte 3: `CRIADOS_1PAV` e `criados_1pav`. No PDF, dois círculos brancos de 34 pt (60 cm) da ARQ_LAYOUT HUMANIZAÇÃO, junto à parede, dos dois lados da cama; o motor fez quadrados de ~45 cm com a sombra forte à esquerda e embaixo. O quadrado e a sombra saem: cada linha da caixa recebe o vinílico limpo da mesma linha, ao lado (`piso`, as colunas entre a cortina e o criado-mudo, ou depois dele), espelhado até cobrir, porque as réguas correm na horizontal (o inpaint puxava o branco da cama para a fresta); a parede preta fica. Entram os círculos do PDF na madeira do próprio quadrado (o miolo dele, ampliado), com o contorno na mesma madeira a 72% (0,45 px) e a sombra curta do banco do Térreo (`BANCO_VARANDA`), a dos bancos do item 6.
- item 8, quarto de serviço: `QUARTO_SERV_1PAV` e `quarto_servico_1pav`. No PDF (ARQ_LAYOUT HUMANIZAÇÃO), a cama de solteiro junto à parede da esquerda, cabeceira em cima, e o criado-mudo à direita dela, junto à parede de cima; o motor fez uma faixa clara com dois quadrados brancos e um risco no piso. A faixa e o risco saem (`faixas`: cada linha recebe o vinílico limpo da mesma linha, à direita, espelhado; a parede fica). Entram a cama da direita e o criado-mudo do meio da suíte 1, que no PDF têm as mesmas medidas (56,7 x 113,4 pt e 31,2 x 22,7 pt), tirados da imagem aprovada e espelhados na vertical (`cv2.warpAffine` com o mapa inverso; a dobra do edredom fica à direita, como no PDF), no retângulo do PDF, com a sombra curta dos bancos.
- item 9, banheira do banho master (seção 6, item 7 da conferência de 19/10): `BANHEIRA_1PAV` e `banheira_1pav`. No PDF, a banheira é oval (95,5 x 50,7 pt, 1,68 x 0,89 m, o polígono cheio da DOC_TEXTOS) e tem a torneira de piso na ponta da esquerda (ARQ_LOUÇAS E METAIS: a base junto à borda e a bica horizontal entrando 9,5 pt na banheira); o motor fez uma banheira retangular de cantos arredondados, com sombra, sem a torneira. A banheira do motor e a sombra saem (`apagar`): o piso limpo do banho à direita (`fonte_piso`) tecido com `quilting`, ajustado linha a linha à luz da faixa de 6 px junto à caixa (o piso clareia de cima para baixo), com a borda fundida (0,8 px) e as folhas da floreira por cima. Entra o bloco `banheira_oval` da biblioteca (`_blocos/blocos.py`, a do banho master da Casa E) só com o corpo: a torneira de bancada do recorte e o ladrão saem (`corpo`, `cols_torneira`: a borda de cima refeita na horizontal entre as colunas de fora e o contorno de cima espelhando o de baixo), no retângulo da elipse do PDF, em 4x. A torneira de piso entra no lugar do PDF, no cromo dos chuveiros aprovados (`CROMO_ESCURO`, `CROMO`, `CROMO_CLARO`), como a `torneira_banheira` da Casa E: base redonda de 3,5 pt de raio e bica de 1,47 pt até 1226,6 pt. As duas com a sombra curta dos bancos (`BANCO_VARANDA`).
- item 10, cortinas de linho nas quatro suítes (seção 8, com o trilho de fora a fora de 20/10): `CORTINAS_1PAV` e `cortinas_1pav`, como `retoque_1pav_casae.cortinas_linho` (item 10 da Casa E; os trechos vêm de `trechos_cortina` e a peça é posta com `retoque_terreo_casae.pousar_cortina`). No PDF, cada suíte tem dois trechos de linha ondulada (ARQ_LOUÇAS E METAIS, 0,85 pt) junto às portas de vidro; o motor os fez como uma coluna de tracinhos escuros no vinílico. Os tracinhos saem (`limpar`): numa faixa de 9 px no eixo de cada trecho, do começo ao fim dele (5 px antes, 8 depois), cada linha recebe as duas beiradas da faixa ligadas em linha reta (as réguas correm na horizontal), só onde o piso está 20 mais escuro que isso; a beirada fora do tom do vinílico do trecho (a mediana da faixa; a poltrona da suíte 2, o caixilho da suíte 1, o vidro do item 14) dá lugar à outra, e sem beirada no tom a linha fica; a parede e o caixilho (a 7 px do eixo) ficam. Esse passo é `tracinhos_cortina`, que o item 14 chama antes. Entram o pano da biblioteca em cada trecho do PDF (o eixo do tecido no eixo da linha, na mesma extensão) e, em cada suíte, o trilho de parede a parede, do lado do vidro (à esquerda nas suítes 3, 2 e master; à direita na 1, `vidro_direita_pt`), até a parede preta achada numa coluna 3 px para dentro do quarto.
- item 11, vinílico na escala (R4: "réguas de ~20 cm, claras, em tons alternados"): `vinilico_1pav`, com os números e as réguas da Casa E (`retoque_1pav_casae.VINILICO` e `reguas_vinilico`, item 11 de lá). A área é o laranja do vinílico da base chapada da entrega (o mesmo da legenda da Casa E), levada à imagem pelo quadro comum (`base_terreo(forma, "1Pavimento")`), e, dentro dela, só o que é piso no render: os objetos saem por fugir da luz do piso (mais claros, ou mais escuros com outra cor), a sombra fica como piso. As folhas das portas do PDF (os brancos compridos da ARQ_PAREDE, com o critério do item 2) ficam fora, com 2 px de folga (`VINILICO_1PAV`): o motor as fez em traço duplo fino no tom da madeira, e a porta da suíte 3 para o closet sumia. As réguas de 20 cm, 1,2 a 1,8 m, em fiadas com as juntas desencontradas, cada uma num tom, com o veio do próprio vinílico, na luz do lugar; o escurecido sobe 70% do caminho até a luz mediana (135; até +5%). Na lista `ITENS`, o pf11 roda logo depois do pf3, antes dos móveis dos itens 4 a 10 (como na Casa E, onde vinha antes dos outros passos): bancos, criados-mudos, cama e cortinas são postos sobre o piso novo.

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
- **`retangulos` com `proteger_layers` e `apagar_linhas_layer`:** para piso branco sem polígono no PDF (os banhos da Casa D, brancos com hachura). O miolo branco das peças das layers protegidas (louças, bancadas, móveis) não muda, e os traços da hachura da layer indicada viram o material. Com `"apagar_hachura_quente": true`, a hachura em tom quente claro (o pontilhado rosado dos banhos do 1º Pavimento da Casa E, que não é cinza) também vira o material, fora das peças protegidas.
- **`texturizar_base.py` sem `esmaecer`:** a planta inteira recebe textura. Use `tolerancia` 4: com 12, o vidro #D6D6D3 entra no travertino #DCD9CA.

## Limitações conhecidas

- Os PDFs da Casa A que estão no Drive (001 Layout, 004, 005, 006, 021) **não têm** a layer `ARQ_PAREDE` nem o cinza 0.357. O PDF que gerou as bases atuais foi enviado direto na conversa e precisa ser trazido para cá. Sem ele, o script gera só a base sem texto e avisa que a v3 não foi gerada.
- As zonas do Térreo foram medidas sobre aquela base original (6001×3884). Se o PDF novo tiver outro enquadramento, confira no `_debug.png` antes de usar a v3.

## Teste

Validado num PDF sintético com layer `ARQ_PAREDE`: paredes, vidro fino branco, divisória de vidro em traço, traço sobre parede, folha de porta com arco, vidro na faixa do muro e texto. Resultado esperado e obtido: 1 vidro-forma, 1 vidro-traço, 1 descarte de cada tipo (parede, porta, muros), texto removido sem apagar a linha que estava sob ele, nenhum pixel azulado e rotação de 180° idêntica.

## Auditoria das especificações de 26/10 (`auditoria_2610.py`)

Desenha os mapas numerados das 11 especificações do usuário de 26/10 (E1 a E11, `POE642_REGRAS.md`, seção 19) sobre as pranchas de entrega das 12 plantas. Só aponta; não altera nenhuma imagem.
- Cada planta tem a sua lista em `ITENS`, com a especificação, o texto e os pontos em px do quadro de 3840 × 2160.
- O recorte é a área construída: os rótulos do PDF no quadro, com folga.
- A cor do círculo é a da especificação.

```
python auditoria_2610.py            # os 12 mapas
python auditoria_2610.py D Terreo   # uma planta
```

Saída: `POE642_Casa?/renders/POE642_Casa?_PH_<pav>_auditoria_2610.jpg`.

## Subsolo da Casa A em 3840 px com os pedidos de 26/10 (`final3840_casaa.py`)

Pedidos do usuário de 26/10/26 para o Subsolo da Casa A (travertino bruto, banco da sauna, cabine do elevador, chuveiros, armários do depósito em marcenaria, folhas contínuas dos boxes, os banhos feminino e masculino com as cubas em granito marrom, a bancada em travertino e os vasos marrons, a divisória entre eles como parede em cinza 80, o banho de serviço em Bege Bahia com a bancada em granito marrom e a cuba branca) e os ajustes da auditoria (E3, E7, E8, E9, E10 em cinza 80, E11). A final aprovada, sem os rótulos, no quadro de 3840 px (`rotulos_casaa.final_imagem`) é redesenhada etapa por etapa, pelo PDF e pela base chapada, com o motor das Casas B a D (`final3840_casab.py`, `retoque_subsolo_casae.py`):

| Etapa | O que faz |
|---|---|
| `pisos` | travertino bruto (foto da biblioteca na escala, no creme das Casas B a D, veios e poros: `travertino_bruto`), Bege Bahia no tom das Casas B a D, a madeira da academia nas réguas do vinílico; as peças da ARQ_PAREDE que a final mostra ficam (`nao_piso`), a soleira da academia para o hall fica |
| `banhos` | bancadas em travertino bruto (E9), cubas em granito marrom, torneiras, vasos marrons e descargas; no banho de serviço, bancada em granito marrom, cuba branca, vaso branco; os três chuveiros; os boxes (duas folhas do PDF e o trilho) |
| `sauna` | o banco em travertino bruto, com a quina boleada e a sombra de contato |
| `elevador` | a cabine de aço com os corrimãos e a porta telescópica, e a soleira em inox |
| `deposito` | os dois armários da DOC_LINHAS em freijó, contínuos, sem linhas nem marcações, com a sombra curta |
| `portas` | as portas de vidro de correr da academia pelo PDF: do pátio, 4 folhas em 2 planos com os montantes e os batentes; do hall, 2 folhas sobre a soleira de Bege Bahia refeita; o vidro fixo em L da sauna, com o caixilho e as linhas do PDF, até a parede; a porta de giro da sauna (a folha aberta para a antessala, no estilo do vidro fixo, e os batentes brancos; sem o arco) |
| `paredes` | cinza 80 nas paredes do PDF e na divisória dos banhos; na porta da sauna, o vão entre o batente e a parede entra como parede (`encostos`) |
| `escada` | os degraus em Bege Bahia, sem linhas, com o sombreamento de subida (esmaecidos depois do corte), e o S do PDF, sem o triângulo |
| `rotulos` | `F.rotulos` com os boxes da Casa A e a divisória como parede; o BANHO SERV. no piso seco |

```bash
export POE642_CACHE=/caminho/do/cache                      # as etapas ficam em $POE642_CACHE/poe642_casaa_etapas
python3 final3840_casaa.py                                 # a final: renders/POE642_CasaA_PH_Subsolo_final_rotulos.png
python3 final3840_casaa.py --de banhos --ate paredes       # recomeça e para numa etapa (só grava a final no fim)
python3 final3840_casaa.py --de rotulos --antes antes.png  # e os antes e depois: renders/..._Subsolo_2610_<item>_antes_depois.jpg
python3 rodape_entrega.py --no-quadro --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png
python3 pdf_entrega.py
```

## Térreo da Casa A em 3840 px com a auditoria de 26/10 (`final3840_casaa_terreo.py`)

A lista do Térreo aprovada pelo usuário em 26/10/26 ("aplique a lista"; o travertino fica o de hoje): E2, E3, E4, E5, E7, E8, E9, E10 (cinza 80) e E11 (o granito). A final aprovada, sem os rótulos, no quadro de 3840 px (`rotulos_casaa.final_imagem`) é redesenhada etapa por etapa com as rotinas do `final3840_casaa.py`:

| Etapa | O que faz |
|---|---|
| `granito` | o granito das Casas B a D na cor malva da base chapada, só no piso, até a borda dos objetos (sem folga; as pintas soltas do granito antigo são piso); as sombras e o tracejado das projeções ficam; o banho do motorista em Bege Bahia; a faixa em volta das bancadas refeitas em granito troca inteira |
| `travertino` | o travertino bruto do Subsolo no piso de travertino da base, até a borda de cada móvel, px a px (`alfa_objetos`: mais claro, de outra cor ou muito escuro que o piso antigo é objeto; a sombra, mais escura e acinzentada, é piso e passa como luz; as manchas fracas e os restos rosados são piso); as peças cheias da base, as esquadrias e as portas ficam |
| `motorista` | o armário do quarto com os cabides e o box do banho em vidro contínuo |
| `loucas` | os vasos marrom-escuros (lavabo, WC, banho varanda); a bancada do lavatório em travertino bruto com a cuba esculpida em granito; a bancada do banho do motorista em granito mais escuro, cuba branca, chuveiro |
| `ilha` | a ilha em U do gourmet em granito mais escuro, com a área molhada rebaixada, o degrau do balcão e as laterais em cascata, a cuba de inox redesenhada (`cuba_inox`) e o cooktop de 5 bocas do PDF (`cooktop`) |
| `cozinha` | a ilha e a bancada da pia da cozinha em granito mais escuro, com as laterais em cascata e o cooktop da ilha, a área molhada rebaixada e as duas cubas de inox |
| `lavabo` | a borda e a sombra da bancada (E9) |
| `paredes` | cinza 80 nas paredes do PDF; a linha preta dos muros do lote da própria final em cinza 80 |
| `deck` | o lance do deck em Bege Bahia, sem linhas, com o sombreamento, esmaecido depois do corte; o D no degrau de cima |
| `pisantes` | os degraus escalonados em Bege Bahia, sem contorno, com a sombra de cada um no de baixo; o D no de cima |
| `escada_u` | a escada interna sem linhas, com o sombreamento (cheia até o corte do 7º degrau, esmaecida depois); o S no 1º degrau |
| `caracol` | os degraus em leque sem linhas, com o sombreamento, o pilar preto e o corrimão; cheia até o corte, esmaecida depois; o S do PDF |
| `projecoes` | o tracejado das projeções do PDF, nítido, em preto nos fundos claros e em branco nos escuros |
| `seta` | a seta da entrada principal no hall externo, apontando para a porta pivotante |
| `rotulos` | os rótulos com os desvios aprovados; LAVABO no corpo do PDF, SALA DE ESTAR fora do tapete, B. MOTORISTA no meio do piso seco |

```bash
export POE642_CACHE=/caminho/do/cache                            # as etapas ficam em $POE642_CACHE/poe642_casaa_etapas
python3 final3840_casaa_terreo.py                                # a final: renders/POE642_CasaA_PH_Terreo_final_rotulos.png
python3 final3840_casaa_terreo.py --de paredes --ate caracol     # recomeça e para numa etapa (só grava a final no fim)
python3 final3840_casaa_terreo.py --de rotulos --antes antes.png # e os antes e depois: renders/..._Terreo_2610_<item>_antes_depois.jpg
python3 rodape_entrega.py --no-quadro --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_rotulos.png
python3 pdf_entrega.py
```

Os antes e depois: os da 1ª lista (`planta`, `granito`, … `sala_estar`) contra a final aprovada antes da auditoria; os dos pedidos seguintes (`travertino`, `banhos_varanda`, `ilha_gourmet`, `banho_motorista`, `projecoes`) contra a versão deles; os da limpeza dos contornos (`contornos_moveis`, `contornos_estar`, `contornos_banhos`, `contornos_lavabo`, `contornos_hall`, `ilha_cooktop`, `cozinha_bancadas`) contra a versão anterior a ela (`antes_depois(..., chaves=[...])`).

## 1º Pavimento da Casa A em 3840 px com a auditoria de 26/10 (`final3840_casaa_1pav.py`)

A lista do 1º Pavimento aprovada pelo usuário em 26/10/26 (os 12 itens do mapa `renders/POE642_CasaA_PH_1Pavimento_auditoria_2610_v2.jpg`, com "A. Sim." e "B. mantem"), mais os pedidos seguintes: a descida da escada em U com a linha de corte do Térreo e a parte do Térreo nublada; as cubas dos banhos em travertino bruto e os vasos brancos; o B. serviço com a bancada em granito marrom, a cuba e o vaso brancos. A partida é a imagem do pavimento com os ajustes no quadro de 3840 px, antes do Térreo nublado (`rotulos_casaa.no_quadro_fixo`, com a pegada e as janelas do Térreo, em cache: `1Pavimento_ini.png` e `1Pavimento_mascaras.npz`); o Térreo nublado entra no fim, a partir da final nova do Térreo:

| Etapa | O que faz |
|---|---|
| `pisos` | travertino bruto (circulação, sala íntima, banhos), vinílico nas réguas das Casas B a D (suítes, closets) e Bege Bahia (quarto de serviço, saleta, B. serviço), cada um na sua cor da base chapada, até a borda das peças (`T.alfa_objetos`); nos banhos, as bancadas, as cubas, os vasos e os chuveiros a refazer viram piso, com as louças antigas fora do lugar do PDF e as linhas dos boxes antigos; a luz em volta das peças refeitas vem do piso limpo (inpaint); a banheira do master fica inteira (`PECAS_BRANCAS_1P`) |
| `armario` | o armário do quarto de serviço com os cabides e o cabideiro, portas para o quarto |
| `banhos` | as muretas do banho master em cinza 80; bancadas em travertino bruto com as cubas esculpidas no mesmo travertino (`FA.cuba_pedra`, `TRAV_CUBA`) e os vasos brancos; o B. serviço com a bancada em granito marrom no polígono do PDF, a cuba branca, o vaso branco e a descarga; os chuveiros e registros do PDF; os boxes em vidro contínuo |
| `paredes` | cinza 80 nos preenchimentos pretos da ARQ_PAREDE, sem o limite de 300 pt do Térreo (aqui não há muros do lote, e as paredes compridas ficavam pretas) |
| `escada_u` | os 19 degraus sem linhas e sem triângulo, no travertino bruto no tom do piso, com o sombreamento de subida; o D no degrau 19; o contorno fino do vão |
| `caracol` | os cinco degraus do 1º Pavimento (0,6° a 93,1°) no travertino da caracol do Térreo, sombreados; o resto do círculo em branco limpo (o Térreo nublado); o anel, o pilar preto e o D do PDF |
| `nublado` | o Térreo novo até a caracol, sem as letras (`terreo_sem_letras`, em cache: `Terreo_nublado_base.png`), nublado fora da pegada, nas janelas e, inteiro, nos degraus 1 a 7 da escada em U, recortados pela linha de corte do PDF do Térreo (`CORTE_U`), desenhada por cima em cinza escuro; o tracejado do lote |
| `projecoes` | os traços do PDF em preto ou branco pelo fundo (`T.preto_branco`): a cobertura (as retas aprovadas, `AJ.PROJECOES_1PAV`), o pergolado e os X dos vazios; nas paredes, o traço some |
| `rotulos` | os rótulos com os desvios aprovados; BANHO 3 e B. SERVIÇO longe do box, SALA ÍNTIMA fora do tapete (`AJUSTES_1P`) |

```bash
export POE642_CACHE=/caminho/do/cache                          # as etapas ficam em $POE642_CACHE/poe642_casaa_etapas
python3 final3840_casaa_1pav.py                                # a final: renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png
python3 final3840_casaa_1pav.py --de banhos --ate caracol      # recomeça e para numa etapa (só grava a final no fim)
python3 final3840_casaa_1pav.py --de rotulos --antes antes.png # e os antes e depois: renders/..._1Pavimento_2610_<item>_antes_depois.jpg
python3 rodape_entrega.py --no-quadro --render 1Pavimento=../renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png
python3 pdf_entrega.py
```

O 1º Pavimento depende da final do Térreo: depois de mudar o Térreo, rodar o `final3840_casaa_1pav.py --de nublado` (o `Terreo_nublado_base.png` se refaz quando o `Terreo_paredes.png` do cache é mais novo). Rodar `rotulos_casaa.py 1Pavimento` sobrescreveria a final com a versão antiga.


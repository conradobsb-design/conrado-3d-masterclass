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
- `cortina(comp_m, px_por_m, aberta=False)`: a cortina de linho vista de cima, na horizontal (o trilho do lado do vidro, em cima da peça). Desde 27/10/26, fechada, é o pano franzido (`pano_franzido`) com o trilho; aberta, ou só o trilho (`com_pano=False`), continua a de antes.
- `pano_franzido(comp_m, px_por_m)`: o pano fechado (aprovado nos quartos do Térreo da Casa C e adotado em todas as casas em 27/10/26): o lado do vidro quase reto, o do ambiente em ondas (`passo_m` 0,15, `festa` 0,018 m), as pregas em luz e sombra, a dobra da frente e a sombra curta no piso. Peça de 0,17 m com o eixo do tecido no meio, como a antiga.
- `cortina_ondulada(...)`: o desenho anterior (a linha fina em zigue-zague e o trilho), que a `cortina` usa para a cortina aberta e para o trilho.

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
- **Térreo, auditoria de 26/10** ("ok, aplique a lista. pilares em preto", e os banhos do usuário): `passos_terreo` passa `pisos(..., bruto=)` (e `TRAV_BRUTO` para as faixas de `travertino_em`), `bancadas(..., borda=, pedra=pedra_banhos(Q), cuba=cuba_terreo)` (a pedra por peça: travertino bruto onde a peça tem cuba do PDF; `BANHOS_T`: as cubas do lavatório gourmet em granito, `cuba_esculpida(..., "granito")`; as peças com o centro em `BANHOS_T["granito_pt"]`, a cozinha e a varanda gourmet, em `"granito_escuro"`: `fontes_procedurais.granito_referencia` na mediana do piso de granito da imagem vezes `BANCADAS_F["granito_escuro"]["escurecer"]`), a etapa `vasos` (`VASOS_COR["Terreo"]`), `boxes_vidro`, `paredes(..., cor=, pilar="preto")`, `esquadrias_terreo(..., parede=)` (a limpeza da faixa do vidro reconhece a parede pela cor: `esquadrias_final(..., limpar_cor=True)`, `ESQUADRIAS["parede_limpar"]`), `cortinas(..., paredes_pdf=True)` (o trilho para no 1º px de parede do PDF: `cortinas_b(..., paredes=)`), `escadas_e3` (`degraus_blocos(..., linhas=False, letra_="D")` e `escada_sombreada(..., no_alto=True)`; a de 9 degraus com `pedra="travertino"`: `final3840_casaa.travertino_bruto` no tom mediano do travertino da legenda), `projecoes_r8` (`PROJ_B`; `final3840_casaa_terreo.preto_branco`), `seta_b` (`SETA_B`) e o SHAFT nos rótulos. As Casas C e D chamam as mesmas funções sem esses argumentos e não mudam.
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
  - `ambientes_rotulos(todas=True)` (29/10): o recinto, fechado também pelos vidros, caixilhos e batentes (os preenchimentos claros e os traços da ARQ_PAREDE); `ROTULOS_F["pontos"]` aceita a chave (nome, x, y do ponto do PDF arredondados) além do nome, para nomes repetidos;
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
- **Escadas** (`escadas_c`, `degraus_linhas`, R14): no Térreo, os degraus largos (`DEGRAUS_LARGOS_T`, triângulo no 10 apontando para cima) e a estreita (`ESCADA_ESTREITA_T`, triângulo junto ao deck apontando para a esquerda). No Subsolo, desde a auditoria de 26/10, sem linhas e sem triângulo (E3, E8): `degraus_largos_s` (`LARGOS_S`: o número do degrau de cada px pelos bocéis retos e em L, `sombras_degraus`, o S no degrau 1) e `escada_estreita_s` (`ESTREITA_S`: o Bege Bahia no tom da planta com o sombreamento, esmaecido; a linha de corte do PDF e o trecho depois dela nevoado; o S esmaecido no degrau 11).
- **Soleira do elevador** (`soleira_elevador`, `SOLEIRA_ELEVADOR_C`): em inox escovado, entre os batentes do PDF, nos dois pavimentos (não é vão branco do PDF, então a etapa das soleiras não a pegava).
- **Subsolo** (`passos_subsolo_c`): pisos só na pegada (`pegada_subsolo`: o Subsolo, o pátio, os degraus largos e o caminho, e a escada estreita esmaecida), a floreira junto à sauna (`floreira_s`, `FLOREIRA_S`), os bancos da sauna em travertino (`bancos_sauna_c`, `SAUNA_C`), os aparelhos da academia do render aprovado (etapa `aparelhos`, `pecas_do_render` com `FORA_PECAS_S`: pelo PDF saíam silhuetas cinza chapadas; entram os px neutros do render, sobre o vinílico novo, com a sombra curta), o rótulo da VARANDA SUBSOLO (o filtro dos títulos da folha, `A.FORA`, passa a ser "1º SUBSOLO"), e o resto do lote na hachura do Térreo final (`AJ.subsolo_hachurado`).
- **Subsolo, auditoria de 26/10** ("ok, aplique a lista"; aprovado depois da limpeza: "Aprovado"): `passos_subsolo_c` passa `F.pisos(..., bruto={"travertino": "piso"})`, `bancadas_c(..., borda=, pedra="granito", cuba=F.cuba_granito)`, `bancos_sauna_c(..., bruto="bancada")`, as etapas `vasos` (`VASOS_COR_C`, em `F.VASOS_COR` pelo `contexto_c`), `chuveiros` (`chuveiros_s`, `CHUVEIROS_S`: `final3840_casaa.chuveiro` sem o braço), `boxes` (`boxes_s`: `final3840_casaa.boxes`, as folhas do box de correr e o trilho) e `elevador` (`elevador_s`, `ELEVADOR_S`: `final3840_casaa.elevador` com o desenho da Casa C), `F.paredes(..., cor=cinza)`, `esquadrias_final(..., parede=cinza)` e `janelas_s` (o vão escuro da janela fica claro), as escadas novas e `ROTULOS_S` (a folga de 4 px e o ponto do SAUNA). Depois, a limpeza pedida pelo usuário: `limpeza_s` logo depois dos pisos (`LIMPEZA_S`: as linhas finas da base entre os pisos por `cv2.inpaint`; os brancos pequenos do PDF e a zona da floreira na pedra clara, sem os restos do render), `sem_verde_s` (a mureta da floreira e o peitoril até o vidro inteiros de volta à pedra clara, e os px esverdeados que a limpeza das esquadrias espelhava do canteiro para o vão do vidro) e `portas_academia_s` (`PORTA_ACADEMIA_S`, `final3840_casaa.portas_vidro`: a soleira, as 4 folhas, os batentes; a parede de volta nas pontas e os tiquinhos cinza na madeira); a cuba do BH academia em granito (`F.cuba_granito`) com a torneira (`torneira_s`, `TORNEIRA_S`). A limpeza das linhas finas pega também os traços pretos finos do PDF. O Térreo da Casa C não muda.
- **Térreo, auditoria de 26/10** ("Aplique a lista. No item 8, siga a recomendação."): `passos_terreo_c` passa `F.pisos(..., bruto={"travertino": "piso"})`; `bancadas_t` (`bancadas_c` com a borda do E9, `pedra_terreo_c`: travertino bruto onde há cuba, granito escurecido na cozinha e no gourmet, `BANHOS_TC["granito_pt"]`; `cuba_terreo_c`: as esculpidas em travertino, as dos lavabos masc. e fem. em granito; `cubas_terreo_c` troca os retângulos que juntam bacia e prateleira no BH master 1 pelas duas bacias); a etapa `vasos` (`VASOS_COR_C["Terreo"]`); `chuveiros_t` (`CHUVEIROS_T`, `final3840_casaa.chuveiro`); `boxes_t` (os de correr por `final3840_casaa.boxes`, menos o do BH serviço; `VIDROS_TC` por `F.boxes_vidro` e `F.boxes_granito`); `elevador_t` (`ELEVADOR_S` com `ELEVADOR_T`); `F.paredes(..., cor=cinza)`; `janelas_s(..., JANELAS_T)` depois das esquadrias; `F.cortinas(..., paredes_pdf=True)`; `degraus_largos_t` e `escada_estreita_t` (`ESCADAS_TC`, o D); `projecoes_t` (com a claraboia do BH master 1 em `PROJECOES_C`); `seta_t` (`SETA_TC`); `rotulos_t` (`vidros_box_t`: os boxes que fecham o chuveiro até a parede, para o lado do chuveiro sair dos ambientes; os rótulos saem duas vezes, a segunda sobre o fundo sem o tracejado embaixo dos textos, da etapa das escadas). O armário do quarto externo em `GUARDA_ROUPAS_C`; `jardins_c` não deixa um canteiro refazer o vizinho já pintado; `restos_piso` só junto às peças do PDF. Em `ajustes_casab.cortinas_b`, os trilhos só se juntam quando se sobrepõem (dois trilhos de ex vizinhos viravam um só, de ponta a ponta da casa). O Subsolo, rodado de novo da hachura, sai igual ao aprovado (0 px diferentes).
- **Térreo, pedidos de 26/10 vendo a final** (cortinas, travertino, claraboias, rótulos, lavabos, BH serviço e externo, soleiras, ilha, cooktops, escritório, adega, elevador, jardins, paredes atrás das portas): `F.pisos(..., incluir=VAOS_TC + carros, bruto={"travertino": "estratos"})` — `piso_textura_c` desenha o travertino em estratos (`travertino_estratos`, `TRAVERTINO_TC`) e `final_3840_c` troca `final3840_casaa.travertino_bruto` por `travertino_bruto_tc` no Térreo (bancadas e cubas no mesmo desenho, mais calmo); `VAOS_TC`, os vãos onde o piso passa (porta de correr da área descoberta, BH serviço, escritório, adega, claraboia da varanda, vidros dos jardins); `floreira_lavabo_t` (`FLOREIRA_LAVABO_T`) depois de `bancadas_t`, com `pedra_terreo_c`/`cuba_terreo_c` pelas zonas de `MATERIAIS_TC`; `COOKTOPS_C` girados 180º; `chuveiros_tc` (`chuveiro_teto`, `CHUVEIRO_TETO_T`); `elevador_t` com o poço branco (`POCO_ELEVADOR_T`); `soleiras_t` (`SEM_SOLEIRA_TC`); `pos_esquadrias_t` (`POS_ESQUADRIAS_TC`: as paredes cortadas pela limpeza das folhas voltam, os portões, a ilha, as faixas onde o piso passa, a janela da cozinha e as portas de correr do escritório e da adega por `final3840_casaa.portas_vidro`); `cortinas_t` (o pano de `pano_cortina`, `CORTINA_TC`, no lugar de `blocos.cortina(..., com_trilho=False)`); `projecoes_t` só com os X dos jardins e da área descoberta, e `claraboias_t` (`CLARABOIAS_T`); `jardins_c` com as plantas sem a franja do recorte (`sprite_limpo`); `rotulos_t` com o nome em SemiBold (`ROTULOS_TC["fonte_nome"]`, que `retoque_1pav_casae.rotulos_ambientes` lê de `ROTULOS["fonte_nome"]`; sem ele, nada muda nas outras casas) e o JARDIM DE INVERNO 2 em duas linhas.
- **Térreo, cortinas do estar (27/10):** no PDF da Casa C, as cortinas do estar (junto aos vidros do canto do hall e da fachada de baixo) estão na ARQ_MOBILIÁRIO, não na ARQ_LOUÇAS E METAIS onde `B.onda_cortina_b` procura, e ficavam como as bolinhas do render. `trechos_cortina_tc` (`CORTINAS_MOB_TC`) junta essas ondas aos trechos de `B.trechos_cortina_b` (a camada, trechos de pelo menos 30 pt, o lado do vidro pelo traço comprido da ARQ_PAREDE mais perto); `cortinas_t` o põe no lugar de `B.trechos_cortina_b` enquanto roda. `pano_cortina` agora só chama `blocos.pano_franzido`.
- **Térreo, pedidos de 27/10 (cadeiras, closet, garagem):** a etapa `cadeiras` (depois da `biblioteca`), `cadeiras_mesas_t` com `CADEIRAS_MESAS_TC` (os pares cadeira/mesa do PDF: as mesas são faixas da DOC_LINHAS E PROJEÇÕES): a mesa volta por cima da parte da cadeira que fica sob o tampo, na largura toda do tampo e com 1 px da borda; o tom de cada coluna passa de uma ponta à outra e o veio fino vem de um trecho livre da mesa, sem a componente que atravessa a mesa (juntas); a sombra curta do tampo só na silhueta da cadeira. Nos rótulos (`rotulos_t`), `ROTULOS_TC["pontos"]` (o ponto de onde a busca parte: a GARAGEM no meio do vão entre os carros, o CLOSET MASTER 1 no meio do piso livre) e `quebras` (CLOSET / MASTER 1), e os guarda-roupas (`GUARDA_ROUPAS_C`) e as claraboias (`CLARABOIAS_T`) como obstáculo, pela chave nova `obstaculos_pt` do `final3840_casab.rotulos` (retângulos em pt por pavimento; sem ela, nada muda nas outras casas).
- **Térreo, banco do deck (27/10, "banco bronze fosco, sem falhas."):** a etapa `deck` chama `deck_detalhes_c` (`BANCO_DECK_TC`) no lugar do `F.deck_detalhes`: a moldura do banco no PDF (os px cinza da base, brancos, de traço ou de antialias, a até `frente_px` do assento grande, longe da pedra e da grama, que são a faixa de trás) ganha, por um instante, a cor do assento na base chapada, e o `F.deck_detalhes` pinta o L inteiro em bronze fosco, com o escovado, a quina, o contorno e a sombra; a base volta ao que era.
- **Térreo, vidros dos jardins (27/10, "corrija esses riscos brancos dentro da área verde, no contorno interno, logo depois das portas de vidro."):** a etapa `esquadrias` termina com `jardins_vidros_t` (`JARDINS_VIDROS_TC`): em cada jardim de inverno (a cor da vegetação na base, com mais de `area_min_px`), linha a linha em cada lado (sem os cantos), da borda das plantas para fora até a primeira linha comprida do vidro desenhado; o claro ali (e nos 3 px da borda das plantas) vira a vegetação de dentro, copiada a 16 a 40 px; onde a base tem soleira (branco ou travertino entre as plantas e o vidro), a borda das plantas, com a sombra, é deslocada até o vidro, com a emenda em transição de 6 px. Sem vidro em 10 px, a linha fica como está.
- **Térreo, portas dos jardins (27/10, "melhore o aspecto das portas de vidro dos jardins de inverno"):** depois do `jardins_vidros_t`, ainda na etapa `esquadrias`, `portas_jardins_t` (`PORTAS_JARDINS_TC`: a faixa do vidro, o lado das plantas, os batentes e as folhas do PDF, como em `POS_ESQUADRIAS_TC["portas"]`) refaz o fundo da faixa (a metade de fora com o piso de fora, a de dentro com as plantas, cada uma copiada logo além da faixa) e desenha as folhas e os batentes pelo `final3840_casaa.portas_vidro`.
- **Térreo, vidro fixo do JARDIM 1 (27/10, "aplique o mesmo desenho no vidro fixo também"):** mais uma entrada em `PORTAS_JARDINS_TC` (uma folha sem correr, os dois quadrados do caixilho como batentes) com `"espelho": True`: o fundo da faixa é refletido nas bordas, em vez de copiado a `fundo_px` além dela (a cópia pegava o vaso do lado de fora).
- **Térreo, soleira da área de serviço (27/10, "aplique a correção na soleira."):** o vão da porta de correr entre a cozinha e a área de serviço (`VAO_COZINHA_SERVICO_T`) entra no granito dos `pisos` (`VAOS_TC`) e em `POS_ESQUADRIAS_TC["faixas_piso"]`; `POS_ESQUADRIAS_TC["vao_cozinha"]` troca, no vão, o que a chapada não tem em branco (o traço do contrapiso e a folha) pelo granito da cozinha `desloca_px` ao lado. Mudou `VAOS_TC`: rodar desde `--de pisos` (17 min).
- **Térreo, adega (27/10, "adicione a prateleira de vinhos como fizemos na outra casa, ao fundo da adega"; "as garrafas em escala"):** `adega_c` (`ADEGA_C`: o retângulo da prateleira em pt, os módulos e as medidas da garrafa em metros, convertidas por `Q.px_m`), no fim de `biblioteca_c`; o retângulo entra nos `obstaculos_pt` dos rótulos. O rótulo da ADEGA sai a 85% do corpo (`ROTULOS_TC["corpos"]`, um ajuste `corpo` por nome) a partir do ponto do meio do piso livre (`ROTULOS_TC["pontos"]`).
- **Cache de etapas:** `<$POE642_CACHE ou a pasta temporária>/poe642_casac_etapas/final3840/<Pavimento>_<etapa>.png`.

```bash
python3 final3840_casac.py Terreo               # -> ../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png
python3 final3840_casac.py Subsolo              # depois do Térreo (a hachura vem dele)
python3 final3840_casac.py Terreo --de pecas    # refaz só dali em diante; --ate <etapa> para nela
python3 final3840_casac.py Terreo --de moveis   # (28/10) as poltronas, os pufes e as mesas laterais no modelo da Casa D
# desde 28/10, o Térreo tem por cima o turquesa e as bordas da piscina (`piscinas_turquesa.py`): depois do motor,
# python3 piscinas_turquesa.py C-Terreo && python3 piscinas_turquesa.py C-Terreo --bordas --rede <a saída do motor>
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
- **Cubas** (`cubas_bancada_d`, `CUBAS_EXTRA_D`): as do banho master, do lavabo e do WC DCE, que o PDF desenha sem o aro, entram em louça branca com as outras. No Subsolo, até 27/10 a bancada do vestiário com a cuba vinha da final aprovada (`CUBA_VESTIARIO_S`; no PDF, só traço).
- **Biblioteca:** cooktops de 5 bocas (`COOKTOPS_D`) e as 4 banquetas da ilha gourmet sob o tampo (`banquetas_d`: no PDF da Casa D, desenhos de traço da ARQ_LOUÇAS E METAIS).
- **Brises em madeira** (`brises_madeira`, `BRISES_D`, resposta 2): cada ripa da ARQ_ELEMENTOS FIXOS (preenchimento branco pequeno) na madeira da biblioteca, com o veio no comprimento, um tom por ripa, o contorno fino e a sombra curta, nas 10 caixas (garagem, hall, suíte master, suíte 3, fachada de baixo, gourmet).
- **Guarda-corpos de vidro** (`GUARDA_CORPOS_D`): o L do terraço junto aos blocos e o vão da escada.
- **Projeções** (`PROJECOES_D`, `PROJECOES_CLARAS_D`, `COBERTURA_D`): os X do banho master em cinza escuro; os da garagem, da faixa abaixo dela, da área descoberta e do jardim do lavabo, e a cobertura da garagem, em cinza claro.
- **Escadas** (resposta 3): a de 16 degraus (`ESCADA_T`, triângulo no 16 para a esquerda; no Subsolo, `ESCADA_S`, cheia até o corte do degrau 7 e esmaecida depois, triângulo no 1 para a direita) e os 10 blocos em cascata (`BLOCOS_D`, `F.degraus_blocos`, triângulo no terraço para a esquerda).
- **Rótulos:** os títulos das folhas são "0. TÉRREO" e "-1. 1º SUBSOLO" (`A.FORA`, para o DCE TÉRREO e o WC DCE TÉRREO ficarem); a SUÍTE MASTER e a GARAGEM partem de outro ponto (`ROTULOS_PONTOS_D`).
- **Subsolo** (`passos_subsolo_d`): os aparelhos da academia do render, uma caixa por grupo (`FORA_PECAS_S`), a cama do DCE 1 do render (`CAMAS_S`) e, em cor cheia, só o Subsolo e o pátio (`pegada_subsolo`, sem os traços finos: o tracejado da laje fechava a faixa verde, que vai para a hachura, resposta 6).
- **Subsolo, auditoria de 26/10 (27/10; "ok, aplique a lista. no item 7, siga a recomendação"):** as etapas `vasos`, `armario` e `banhos` entram depois das peças, e as paredes, as esquadrias, a escada e os rótulos mudam: `F.paredes(..., cor=cinza)` e `C.janelas_s` (`JANELAS_SUB_D`, sem os batentes do elevador); `escada_sub_d` (`C.escada_estreita_s` com `ESCADA_SUB_D`: sem esmaecer antes do corte, nevoada depois, o S no degrau 1; o corte reto, sem a linha, e `sombra_corte`, a sombra suave no lugar dela: pedido de 27/10, "remova a linha técnica em diagonal"); `armario_dce_d` (`ARMARIO_DCE_S`, o `elementos.guarda_roupa`); `banhos_sub_d` (`BANHOS_SUB_D`: as bancadas pelos retângulos, porque no PDF do Subsolo a ARQ_BANCADAS é só traço, com `final3840_casaa.bancada_pedra` em granito, a do WC DCE no tom do piso escurecido; `cuba_branca`, `F.cuba_granito`, `torneira`; `CHUVEIROS_SUB_D` com o braço e a canopla) e `box_wc_dce_d` (`BOX_WC_DCE_S`: a faixa cinza da base refeita com o granito logo acima, e `final3840_casaa.boxes`); o vaso do vestiário, marrom até o pedido de 27/10 e branco desde então (`VASOS_SUB_D`, vazio, em `F.VASOS_COR`); a cuba esculpida do vestiário em Bege Bahia (`F.cuba_esculpida(..., "bege")`, desde 27/10); `nicho_d` (`NICHO_VESTIARIO_S`, na pedra clara das soleiras); `portas_academia_sub_d` (`C.portas_academia_s` com `PORTA_ACADEMIA_SUB_D`); `rotulos_sub_d` (os arcos das portas fora dos obstáculos; o WC DCE parte de `ROTULOS_SUB_D["pontos"]`). As placas e os braços dos chuveiros, as bancadas, a cuba do WC DCE e a faixa do box ficam fora das `pecas`. A bancada do vestiário do render (`CUBA_VESTIARIO_S`) saiu.
- **Subsolo, pedidos de 27/10 (portas, paredes, batentes, riscos do WC DCE, cama):** a etapa `esquadrias` termina com `pos_esquadrias_sub_d(Q, img, antes)` (`POS_ESQUADRIAS_SUB_D`; `antes` é a entrada da etapa, as soleiras): para cada peça de `pecas` (as folhas das portas de giro e o caixilho das janelas, em pt; as verticais na imagem transposta), `_faixas_folha` refaz as `faixa_px` de cada lado fora da peça (as linhas que ela cobre em até `cobre`) e da parede com a etapa anterior, e onde lá estava a folha antiga (foge do piso do anel logo depois da faixa em `velho`, ou do anel do outro lado, se o seu é parede) com o piso da etapa anterior a `desloca_px` dela; `so_antes` (o lado de dentro da janela do DCE 1, com a cama e o criado-mudo) volta tudo à etapa anterior. Depois, a parede do PDF (dilatada 1 px, o traço da face) volta onde lá era o cinza ou o traço, neutros, e as esquadrias puseram cor (`paredes`, menos `fora`: o box do vestiário). A etapa `tampas` termina com `cama_dce_d` (`CAMA_DCE_S`: `elementos.roupa_de_cama` tipo "motorista" no colchão do DCE 1, cabeceira embaixo).
- **Térreo, auditoria de 26/10 (27/10; "Aprovo a lista e sigamos no item 9 com a recomendação"):** `passos_terreo_d` com as rotinas do Térreo aprovado da Casa C (os 15 itens, no comentário antes de `MATERIAIS_TD`). Pisos com `piso_estratos_d` (o travertino em estratos, `C.piso_textura_c`) e `bruto={"travertino": "estratos"}`; `bancadas_terreo_d` (`C.bancadas_c` com a borda E9, a pedra por bancada em `MATERIAIS_TD`, a cuba esculpida (`F.cuba_esculpida`); desde os pedidos de 27/10, o lavabo e o banho gourmet em travertino bruto e os banhos das suítes em quartzito Aura (`MATERIAIS_TD`; as chapas da biblioteca nas bancadas e cubas por `CHAPAS_D` e `CUBAS_CHAPA_D`, que `contexto_d` põe em `F.BANCADAS_F`: `F.bancadas` e `F.cuba_esculpida` aceitam agora uma chapa, `_chapa_luz`, num tom), `FA.travertino_bruto = travertino_bruto_d` (desde o pedido de 27/10, "Melhore o aspecto do travertino bruto": `TRAVERTINO_BRUTO_D`, os estratos de `C.travertino_estratos` mais marcados, com mais poros, no comprido da peça, e os tons creme da bancada e da cuba em `F.BANCADAS_F`; antes, `C.travertino_bruto_tc`); a cuba branca de parede do WC DCE por `final3840_casaa.cuba_branca`); o piso dos banhos das suítes em quartzito Aura (`quartzito_banhos_d`, `QUARTZITO_TD`: a mancha de Bege Bahia de cada banho a partir do rótulo do PDF, com a luz larga do render e o desenho da chapa); os vasos marrons do lavabo e do banho gourmet (`VASOS_TD`); `cama_dce_d` também no Térreo (`CAMA_DCE_S["camas"]["Terreo"]`); `biblioteca_terreo_d` (os guarda-roupas `GUARDA_ROUPAS_TD` pelo `B.guarda_roupas_terreo`, `banco_varanda_d` com a madeira da mesa da suíte 3/escritório em `BANCO_VARANDA_TD["fonte_pt"]`, e `C.adega_c` com `ADEGA_TD`); `chuveiros_terreo_d` (`CHUVEIROS_TD`, a canopla na ponta do braço junto à parede); `boxes_terreo_d` (a faixa tracejada refeita com o piso 7 px acima, `BOX_FAIXA_TD`, e `final3840_casaa.boxes` com as folhas de `BOXES_TD`); `F.paredes(..., cor=cinza)`; `pos_esquadrias_d` no Térreo (`POS_ESQUADRIAS_D["Terreo"]`: só a parede de volta, sem peças), sem `C.janelas_s` (aqui pegava as faixas brancas da ARQ_PAREDE nas ilhas e no jardim da sala íntima); `F.cortinas(..., paredes_pdf=True)`; `escadas_terreo_d` (`C.sombras_degraus` no Bege Bahia da escada, o D em `ESCADA_DESCIDA_TD["d_pt"]`; `F.degraus_blocos` sem bocel e sem triângulo, o D no meio do bloco de cima, `d_blocos_pt`); `projecoes_terreo_d` (as projeções de `escadas_d`, que saiu); `seta_terreo_d` (`final3840_casaa_terreo.seta` com `SETA_TD`); `rotulos_terreo_d` (duas passadas, como `C.rotulos_t`, com o tracejado embaixo dos textos de volta à etapa das escadas; o WC DCE parte de `ROTULOS_TD["pontos"]`, os arcos das portas fora dos obstáculos, como `rotulos_sub_d`; os guarda-roupas, o banco e a adega como obstáculo). As placas e os braços dos chuveiros ficam fora das `pecas`. Depois: `python3 final3840_casad.py Subsolo --de hachura`.
- **Térreo, pedidos de 27/10, 2º lote (portas de vidro, projeções da laje, carros, planta, linha marrom, beiral, quadrado, armário):** a etapa `esquadrias` termina com `portas_vidro_td` (`PORTAS_VIDRO_TD`, as portas pelo `final3840_casaa.portas_vidro`: a do living para a varanda, 4 folhas em dois planos, e a de correr da cozinha para o living, cada uma sobre a soleira de Bege Bahia do vão do PDF; depois, `RESTOS_PORTAS_TD`, os px mais escuros que o piso em volta da ponta da folha antiga da cozinha e dos puxadores antigos do living voltam ao piso logo acima, e `NICHOS_BEIRAL_TD`, os nichos das duas janelas da fachada de baixo à esquerda, recebem o Bege Bahia do beiral logo abaixo); a etapa `projecoes` termina com `projecoes_lajes_td` (`PROJ_LAJES_TD`: os 9 vãos da laje da garagem e da faixa de grama abaixo dela com o X, o contorno fino dos vãos no gramado, as bordas e as linhas tracejadas da laje, pelo `C._tracejado`, em branco quente, fora das paredes; antes, o tracejado escuro do render ao longo das duas linhas de cima da garagem volta ao granito de 6 px acima); essas zonas saíram de `PROJECOES_CLARAS_D` e `COBERTURA_D`. `carros_d` tira a silhueta do carro do meio da final aprovada da Casa C (`CARROS_D["fonte"]`, `janela_fonte`: o que não tem o tom do granito, `croma_max`, `lum_min`) e a leva à medida da R12, sem recolorir. `BRISES_D` sem a faixa sob a porta de vidro do hall e sem a do beiral da fachada de baixo à esquerda (ripas que o PDF tem por baixo do piso); `SEM_PLANTA_TD` (a planta da bancada gourmet, fora também de `VASOS_D`) e `PECAS_OCULTAS_TD` (o quadrado escondido da circulação da ala íntima) entram no `fora` das peças; `GUARDA_ROUPAS_TD` com o armário à esquerda do corredor do banho master (aberto para a direita).
- **Térreo, pedidos de 27/10, 3º lote (móveis, floreiras, banquetas, box gourmet, recolhimento, beiral, paredes atrás das folhas):** a etapa nova `moveis` (depois da `biblioteca`), `moveis_td` com `MOVEIS_TD`: as mesas de madeira das zonas de `madeiras` (os preenchimentos de tom quente) pelo `madeira_d` (a madeira do miolo levada até a borda, o chanfro e a borda macia; as que ele pega, com R − B acima de `quente`, ficam fora dos estofados: a mesa de centro redonda tem o lado das poltronas); os estofados de `estofados` (nome, zona em pt, lado em pt, `unir`, costura mínima) pelo `estofado_d` (a silhueta dos preenchimentos do PDF em 4x, as almofadas entre os traços de dentro com altura, luz e vale, a trama do bouclé e a borda macia no lugar do contorno; `conchas`: a poltrona da sala íntima com o assento como um círculo puxado para `frente`); `cadeiras_mesas_d` (os pares de `cadeiras_mesas`: a cadeira do render sai, com o piso da etapa dos pisos fora da mesa, ou o de um deslocamento `(dx, dy)` na suíte master, onde a etapa dos pisos ainda tem as pontas dos braços; o tampo refeito sob ela por `_refaz_tampo`; a `banqueta_linho` em 0,56 m girada por `_cadeira_bloco` para a mesa, 1/3 sob o tampo, com a sombra do tampo só sobre ela); `jogos_mesa_d` (`jogos`: o jogo inteiro sai com o piso da etapa dos pisos; as 6 cadeiras da ARQ_LAYOUT HUMANIZAÇÃO em volta, viradas para o centro, e a mesa redonda por cima, em freijó, `_freijo` e `freijo`); `diagonais_armarios_d` (`diagonais`: ao longo de cada diagonal da DOC_LINHAS com mais de `min_pt`, o px mais claro que a mediana em pé e a deitada, ou que os 4 vizinhos, toma a média do par de vizinhos mais parecido; duas passadas); e `floreiras_td` (`FLOREIRAS_TD`: o miolo de cada caixote pelo `C.floreira_lavabo_t`, com `C.FLOREIRA_LAVABO_T` trocado enquanto roda). `_cadeira_bloco` gira a `banqueta_linho` com a frente do assento em cima (`blocos.json`: "a frente do assento fica em cima e o encosto embaixo"); `BANQUETAS_D["giro"]` passou de 180 a 0 (as banquetas da ilha gourmet ficavam de costas para ela), `vasos_sanitarios_d` (no lugar de `F.vasos_sanitarios`, pelo `contexto_d`) tira dos vasos os desenhos na caixa das banquetas, e `banquetas_d` põe o piso da etapa dos pisos na caixa de cada uma, fora do tampo, antes dela. `boxes_terreo_d` chama `box_gourmet_d` (`BOX_GOURMET_TD`: o traço do render sai, com o granito `desvio_px` ao lado, e entra o vidro claro com as faces). No fim de `portas_vidro_td`, `RECOLHE_TD` (o vão de recolhimento de baixo recebe o de cima, refletido e repetido) e `BEIRAL_BEGE_TD` (a faixa do beiral de baixo à direita, da face das paredes à grama, com as colunas do trecho mais comprido só de Bege Bahia em `fonte_px`, em espelho alternado); `NICHOS_BEIRAL_TD` com os 2 nichos das janelas desse beiral; `BRISES_D` sem a faixa desse beiral e sem as duas peças giradas junto à gourmet. `pos_esquadrias_d` com `claro` (Térreo): a parede escura do PDF que a limpeza das folhas clareou em tiras finas (`fino_px`) e compridas (`longo_px`) volta (os recortes atrás das folhas abertas); a etapa `esquadrias` passa `im.copy()` ao `F.esquadrias_terreo`, que muda a entrada (sem a cópia, a referência de antes já vinha recortada). Rodar desde `--de tampas`.
- **Térreo, pedidos de 27/10, 4º lote (jogos da varanda, mesa de jantar, vincos das poltronas, poltrona da suíte 2, bancada dos tanques, tracejado junto ao gás, plantas do hall):** `jogos_mesa_d` agora põe o conjunto `mesa_redonda_6_couro` inteiro (`MOVEIS_TD["conjunto_varanda"]`: o tampo do bloco, `tampo_px` a `px_m_bloco`, levado ao diâmetro da mesa do PDF; o segundo jogo girado 180°, `giro`), em 4x e reduzido ao quadro, pelo `_pousar`; o freijó procedural (`_freijo`) saiu. Embaixo do jogo do render, a etapa dos pisos ainda tem as cadeiras dele: `bege_limpo_d` refaz o Bege Bahia na caixa (o `textura("bege_bahia")` com o retângulo e a semente de `F.piso_textura`, 700 + o índice do bege em `F.PISOS`, cortado e guardado em `F.ETAPAS` como `<Pav>_bege_<caixa>.npy`, porque a textura inteira leva ~45 s; a luz é o piso dividido pelo desenho, liso, levado para dentro por convolução normalizada, `luz_px`). `jantar_d` (`JANTAR_TD`, depois de `cadeiras_mesas_d`): as 10 cadeiras do PDF em volta da mesa do living saem (o piso de cada caixa é o travertino da etapa dos pisos ao lado, nas mesmas linhas, do primeiro deslocamento cuja origem é toda travertino na legenda) e entra o recorte da cadeira de cima da `mesa_jantar_10` (`recorte`, a frente embaixo), com o linho levado ao bege quente e a madeira mantida pela saturação (`linho`), o alfa 1 px menor (o halo da foto), girado para a mesa, na largura da cadeira do PDF, com a borda `sob_px` sob o tampo e a sombra do tampo por cima. `estofado_d` ganhou os vincos (`vincos`: os traços de dentro de `vinco_min_pt` para cima, ou da costura mínima da peça, longe da borda, e a costura da concha): a sombra macia (`vinco`, `vinco_sig_px`) puxada para o lado oposto à luz e a borda clara do lado da luz (`realce`, `realce_px`); `MOVEIS_TD["estofados"]` com a poltrona e o puff da suíte 2. `MATERIAIS_TD["granito_escuro"]` com a bancada dos tanques da área de serviço. `PROJ_LAJES_TD["garagem"]`: a linha de 559,4 pt (tracejada e limpeza) desde 2214 pt, a ponta da floreira (antes, 2335,7). A etapa `tampas` chama `plantas_vaso_d` no lugar do `C.pecas_do_render(..., C.verde, ...)`: as folhas por `folhas_d` (o verde e o escuro abaixo de `PLANTAS_VASO_TD["escuro"]` ligado a ele; o `C.verde` levava o quadrado cinza da sombra do render, abaixo de 170) e a sombra curta mais leve (`PLANTAS_VASO_TD["sombra"]`, no lugar de `F.PECAS["sombra"]` enquanto roda). Rodar desde `--de bancadas`.
- **Térreo, pedidos de 27/10, 5º lote (cooktops, recolhimento do elevador, tracejado da ilha, tapete da suíte master, trilho da cortina, tom dos jogos da varanda):** `COOKTOPS_D` com `giro` 180 nos dois. `RECOLHE_ELEV_TD` (em `portas_vidro_td`, etapa `esquadrias`): o vão deitado da parede de cima do elevador recebe o vão de cima do living (`RECOLHE_TD["fonte_pt"]`, as últimas linhas, junto da porta) transposto e reduzido (`cv2.resize`, INTER_AREA) à espessura do vão. `sem_tracejado_ilha_d` (`TRACEJADO_ILHA_TD`, na etapa `pisos`, depois de `quartzito_banhos_d`): na faixa da borda de baixo do granito do gourmet, a 2ª linha vai para o granito de cima onde está mais perto dele que do Bege Bahia de `ref_px` abaixo, e as outras ao Bege Bahia onde estão mais escuras (`escuro`); as banquetas, que copiam o piso da etapa dos pisos, já pegam a faixa limpa. `tapete_suave_d` (`TAPETE_SUITE_TD`, na etapa `pecas`, depois de `C.pecas_c`): na faixa de `faixa_px` em volta do retângulo do tapete (pt), cada px é a passagem macia (`suave_px`) do tapete, `fonte_px` para dentro, ao piso, a mesma distância para fora (pelo lado mais perto), com a `beira` e a `sombra`; ficam de fora as peças por cima (`Q.preencher` das CAMADAS_PECAS com mais de `peca_pt`, dilatado). `sem_trilho_fora_d` (`TRILHO_FORA_TD`, na etapa `cortinas`): no retângulo fora da suíte master, a imagem de antes das cortinas (o trilho de `cortinas_b` atravessava o canto de vidro). `tons_varanda_d` (`MOVEIS_TD["conjunto_varanda"]["tons"]`, em `jogos_mesa_d`): o bloco em três partes, o tampo (o disco de `tampo_px` no centro), o vidro (no tampo, saturação abaixo de `sat_vidro`) e o couro (fora do tampo), passagem suave em `borda_px`; cada uma no seu `tom` BGR, na luz da foto (`(L/mediana)**gama`). Rodar desde `--de pisos`. A proposta do estar do living (só apresentação, não entra na final) é montada fora do motor, por um script de rascunho, a partir da final e dos blocos `poltrona_boucle`, `poltrona_madeira`, `mesas_centro_redondas`, `mesa_lateral_raiada`, `mesa_lateral_rattan`, `sofa_reto_cinza`, `sofa_2_lugares` e `aparador_madeira`.
- **Térreo, pedidos de 27/10, 6º lote (ripas em L, tracejado da laje, soleira da cozinha, rótulo do WC DCE, sofá do living, laje da lateral e do jardim):** `pos_vidros_d` (etapa `esquadrias`, depois de `portas_vidro_td`): nas caixas de `BRISES_DE_VOLTA_TD`, as ripas do PDF (`brises_pdf_d`, pela máscara do `Q.preencher`) voltam da imagem de antes das esquadrias (a limpeza delas as apagava diante das portas de vidro); e as soleiras de `SOLEIRAS_EXTRA_TD` (pt, o vão do PDF entre as faces) com `final3840_casaa.soleira_bege`. `PROJ_LAJES_TD["garagem"]`: a linha de 559,4 pt desde 1147,3 pt (os 209 traços da ARQ_PAREDE). `PROJ_LAJES_TD["lateral"]` (zona sem os X, `vaos` False): o retângulo tracejado da ARQ_PAREDE junto ao brise da sala íntima em branco, e `limpar_v` (as linhas de pé: o escuro da faixa volta ao que está `desvio_px` à direita); as zonas em `ZONAS_LAJE_TD`. `laje_jardim_d` (`LAJE_JARDIM_TD`, etapa `projecoes`): a faixa da EST_LAJE na borda do jardim da sala íntima recebe a faixa de laje da lateral (`fonte_pt`, de antes das projeções), deitada e espelhada, mais lisa (`variacao`: em volta do corte mediano). `F.rotulos` aceita `ROTULOS_F["fixos"][pav][nome]` (`corpo`, `quebra`, `pt` opcional): o rótulo vai ao ponto do PDF sem a busca, com a cor pelo fundo; `ROTULOS_TD["fixos"]` com o WC DCE TÉRREO (corpo 0,62, em duas linhas mais a área), passado em `rotulos_terreo_d`. `sofa_living_d` (`SOFA_LIVING_TD`, em `moveis_td`, depois de `jogos_mesa_d`): o fundo do sofá antigo (o tapete das linhas livres de cima, em espelho; o travertino das mesmas linhas, à esquerda da mesa lateral) e o `sofa_reto_cinza` de 3 lugares (cortado em `emenda_px`; o lugar da esquerda, o mesmo sem o braço e o da esquerda espelhado), girado 180°, no retângulo do PDF, em 4x, pelo `_pousar`. Rodar desde `--de moveis`.
- **Térreo, pedidos de 27/10, 7º lote (beiral num tom só, fechamento do tracejado, box e adega em U):** `BEIRAL_BEGE_TD` (em `portas_vidro_td`) vale agora de fora a fora (`x_pt` de 1252,3 a 2284,3 pt, também sob o jardim da sala íntima); nas colunas de `grama_x_pt`, as `grama_px` linhas logo abaixo do beiral recebem a grama de baixo (o fio cinza do render sai). `laje_jardim_d` e `LAJE_JARDIM_TD` saíram (o cinza claro na borda do jardim deu lugar ao beiral claro); a etapa `projecoes` volta a ser `projecoes_lajes_td(Q, projecoes_terreo_d(Q, im))`. `PROJ_LAJES_TD["garagem"]["tracejadas"]` ganhou o fechamento da ponta esquerda do PDF (as linhas de pé em 1147,3 e 1158,6 pt e o trecho de 570,7 pt até 1195,6 pt). `BOX_GOURMET_TD["pt"]` começa em 579,8 pt (a parede de cima; antes 603,3), como as duas linhas tracejadas do PDF. `adega_u_d` (`ADEGA_U_TD`: `lados`, (parede, retângulo pt), e `modulos`): as prateleiras das paredes de cima e de baixo com o mesmo `C.adega_c` da prateleira do fundo, na imagem girada (`np.rot90`) para a parede de cada uma ficar à direita, pela `_QGirado` (só `p2q` e `px_m`); roda no fim da etapa `esquadrias` (na etapa da biblioteca, a limpeza das esquadrias espelhava a ponta da prateleira junto do vidro). `rotulos_terreo_d` põe os retângulos de `ADEGA_U_TD` nos obstáculos. Rodar desde `--de biblioteca`.
- **Térreo, pedidos de 27/10, 8º lote (beiral em L, porta da suíte 2, sofá anterior, rótulo da adega):** `beiral_l_td` (`BEIRAL_L_TD`, etapa `projecoes`, depois de `projecoes_lajes_td`): a faixa entre a face da parede do escritório (2275,6 pt) e o tracejado (2284,3 pt), do pé do brise (1645,5 pt) até a linha da face do beiral, recebe o beiral de junto do canto, de pé (as linhas de baixo da face, o trecho de mesmo comprimento à esquerda da faixa); a coluna da face da parede e a do tracejado ficam. Vai depois das projeções porque o `limpar_v` da zona `lateral` compara com a faixa vizinha e, com o claro, mexia no tracejado. `PORTAS_VIDRO_TD` ganhou a de correr da suíte 2 (a soleira até 1889,8 pt, `faces` False, os batentes e as três folhas do PDF em "x", cada uma no plano dela); `BEIRAL_SEM_FACE_TD` (x0, x1 em pt): nesses vãos, a linha da face do beiral (a de cima da tira, em `portas_vidro_td`) recebe a linha de baixo dela. `sofa_living_d` e `SOFA_LIVING_TD` saíram (o usuário recusou o sofá da biblioteca: "muito artificial"); o estar volta ao sofá de `moveis_td`, igual ao de antes do 6º lote. `ROTULOS_TD["fixos"]["ADEGA"]` com `pt` (2181,3, 1035,6), o meio do piso livre do U. Rodar desde `--de moveis`.
- **Térreo, pedidos de 27/10, 9º lote (beiral diante do brise, pia, tracejado do deck, rótulos, almofadas de lã, pisante, poltrona da suíte master):** `BEIRAL_L_TD["brise"]` (x 2280,2 pt, a face de fora das lâminas, e y 1497,7 pt): `beiral_l_td` leva o beiral de pé também à faixa estreita entre as lâminas e o tracejado, do canto da laje ao pé do brise (o mesmo trecho do beiral, mais comprido). `BANCADAS_DE_VOLTA_TD` (em `pos_vidros_d`): a faixa da bancada da pia da cozinha entre a janela e a cuba da esquerda volta da imagem de antes das esquadrias (a limpeza delas espelhava a cuba ali); as `espelho_px` linhas de cima, em espelho das de baixo. `PROJ_LAJES_TD["garagem"]`: a linha de pé de 1147,3 pt só até 570,7 pt e sem a de 1158,6 pt (o deck as cobre no PDF). `ROTULOS_TD["fixos"]["DESPENSA"]` (1906,5, 805,4) e `ROTULOS_TD["brancos"]` (o DCE TÉRREO); `F.rotulos` aceita `ROTULOS_F["brancos"][pav]` (nomes em branco qualquer que seja o fundo, nos fixos e na busca). `almofadas_d` (`ALMOFADAS_TD`, em `moveis_td`, depois dos estofados): as 3 almofadas do sofá do living em duas peças (a de trás acima de `corte_pt`), cada uma pelos contornos fechados do PDF (`binary_fill_holes` e a abertura de `abre_px`), tom sobre tom do tecido em volta (`tom`), com o contorno fino e a sombra curta, e o tricô da almofada de lã do `sofa_reto_boucle` (`_textura_la`: o recorte girado 45°, o relevo dele na escala real, tecido pelo `texturas.quilting` com as variantes sem giro) e o volume. `pisante_reto_td` (`PISANTE_RETO_TD`, etapa `projecoes`): nas colunas do pisante junto ao hall em que o claro passa da borda de baixo do PDF (1347,2 pt), as 2 linhas da borda vêm das certas, em espelho. `MOVEIS_TD["estofados"]`: a poltrona e o apoio da suíte master, com o mínimo das costuras em 0,1 pt (no PDF vêm picadas). Rodar desde `--de moveis`.
- **Cache de etapas:** `<$POE642_CACHE ou a pasta temporária>/poe642_casad_etapas/final3840/<Pavimento>_<etapa>.png`.

```bash
python3 final3840_casad.py Terreo               # -> ../../POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png
python3 final3840_casad.py Subsolo              # depois do Térreo (a hachura vem dele)
python3 rodape_entrega.py --config ../../POE642_CasaD/config_bases.json --no-quadro \
    --render Terreo=../../POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png \
    --render Subsolo=../../POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_final_rotulos.png
python3 pdf_entrega.py --config ../../POE642_CasaD/config_bases.json
```

- Etapa `moveis` da Casa C (28/10, "NO TERREO DA CASA C, ALTERE AS POLTRONAS E MESAS LATERAIS PARA O NOVO MODELO QUE ADOTAMOS"): `final3840_casac.moveis_tc`, com `MOVEIS_TC`, chama `final3840_casad.estofado_d` e `madeira_d` em cada zona. São a suíte master 1, o quarto 1, a sala TV e as 2 poltronas do estar. Os estofados (lado de 30 a 60 pt) saem em bouclé com volume e as costuras como vincos; as mesas laterais (12 a 25 pt) saem em madeira, só as que a final mostra no tom quente.
- Mesa de jantar do living (28/10, "AS CADEIRAS DA MESA ESTÃO INVERTIDAS?"): em `jantar_d`, o giro de cada cadeira estava trocado, com o encosto virado para a mesa. No recorte, a frente fica embaixo; agora a de cima fica como está, a de baixo gira 180° e as dos lados giram 90° para a mesa.

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
| `elevador` | a cabine de aço com os corrimãos e a porta telescópica, e a soleira em inox; desde 29/10, `ELEVADOR["corrimaos"]` (as paredes sem porta; o padrão, em cima, à direita e embaixo) e `ELEVADOR["faces_soleira"]` ("v": as faces dos batentes à esquerda e à direita, com a porta em cima ou embaixo), e a caixa de trabalho é a união do poço com a soleira (a mesma nas Casas A e C) |
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
| `box_varanda` | (28/10) o box de correr do banho varanda: `final3840_casaa.boxes(..., so=)` só com o box horizontal de `BOX_VARANDA["meio"]` (as duas folhas de vidro contínuas e o trilho no vão até a parede) |
| `limpeza_2810` | (28/10) a borda de cima do Bege Bahia junto à grama sem as pecinhas cinza-rosadas (`LIMPEZA_2810["bege_topo"]`: a cada coluna, o que não é grama logo acima da linha da borda, refeito com uma coluna limpa ao lado; os tracejados brancos da projeção protegidos); a placa da ponta direita do caminho (`remendos`): a faixa rosada fora do lote no branco da prancha, o tufo na borda de cima e o risco na grama entre as placas |
| `varanda_baixo` | (28/10) a borda de baixo da varanda junto à grama, entre o pilar e a parede do WC (`VARANDA_BAIXO`: x 1251 a 1476): reta na linha do PDF (1786,5 pt, 1643 px); a cada coluna, as 6 linhas de cima com o travertino espelhado de logo acima, as 6 de baixo com a grama espelhada de logo abaixo, a linha da beira no meio-termo do antialias |

```bash
export POE642_CACHE=/caminho/do/cache                            # as etapas ficam em $POE642_CACHE/poe642_casaa_etapas
python3 final3840_casaa_terreo.py                                # a final: renders/POE642_CasaA_PH_Terreo_final_rotulos.png
python3 final3840_casaa_terreo.py --de paredes --ate caracol     # recomeça e para numa etapa (só grava a final no fim)
python3 final3840_casaa_terreo.py --de rotulos --antes antes.png # e os antes e depois: renders/..._Terreo_2610_<item>_antes_depois.jpg
python3 final3840_casaa_terreo.py --so box_varanda,limpeza_2810,varanda_baixo  # só estas etapas, sobre a final atual (no lugar)
python3 rodape_entrega.py --no-quadro --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_rotulos.png
python3 pdf_entrega.py
```

Desde 28/10, a final do Térreo tem por cima o turquesa e as bordas retas da piscina (`piscinas_turquesa.py A-Terreo` e `--bordas`), que o motor não refaz: as etapas novas entram com `--so` sobre a final; se o motor rodar inteiro, rodar de novo o `piscinas_turquesa.py` (o turquesa e as bordas, com `--rede` na saída do motor).

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

## Cortinas franzidas em todas as casas (`cortinas_franzidas.py`)

Pedido do usuário (27/10/26), vendo as cortinas dos quartos do Térreo da Casa C: "adote esses modelos de cortinas para as todas as casas. corrija as cortinas das casas A, B, E." O pano franzido foi para a biblioteca (`blocos.pano_franzido`, e `blocos.cortina` fechada passou a usá-lo; ver "Biblioteca de blocos e cortina"), e as finais já aprovadas trocam só o pano, sem rodar de novo os motores:

- cada pano antigo sai do lugar exato em que a rotina daquela planta o pôs: os mesmos trechos do PDF, no mesmo quadro (Casas B e D: `ajustes_casab.trechos_cortina_b` no `final3840_casab.Quadro("Terreo")`, os horizontais na imagem transposta, como em `cortinas_b`; Casa A, 1º Pavimento: `ajustes_casaa.trechos_cortina_1pav` no `final3840_casaa.QuadroA`; Casa E Térreo: `retoque_terreo_casae.CORTINAS` e Casa E 1º Pavimento: `retoque_1pav_casae.trechos_cortina`, os dois pelo `opcoes_1pav_casae.quadro_pdf`), pelo que ele ocupava (alfa da `blocos.cortina_ondulada` acima de `TROCA["limiar"]`, 1 px mais largo onde a final veio de 2000 px, `FOLGA_PX`), sem tocar no trilho;
- o lugar dele é refeito com o piso a 0,20 m dali, no ambiente (`tirar`); o px que não é piso (mais de `piso_dif` da mediana do que veio: um arranjo de flores, a roupa de cama, um criado-mudo) vem de outro ponto (`outros`) ou, se nenhum servir, do inpaint;
- o pano franzido entra no mesmo eixo e no mesmo comprimento (`retoque_terreo_casae.pousar_cortina`); o resto da imagem não muda.

O lado do vidro: o pano franzido não é simétrico (o lado reto e o trilho vão para o vidro), e `ajustes_casab.trechos_cortina_b` supunha o vidro sempre em cima nos trechos horizontais. Agora ele lê o lado no PDF (`lado_vidro_pdf`: o traço comprido da ARQ_PAREDE paralelo mais perto, até 14 pt; sem traço, a regra antiga). Nas Casas B e C nada muda; no Térreo da Casa D, as 4 janelas das fachadas de baixo (8 panos) têm o vidro embaixo: `virar` tira os panos e o trilho de parede a parede do lado do ambiente e põe o trilho e os panos do lado do vidro (os panos da mesma janela, no mesmo eixo e a menos de `janela_m`, dividem o trilho).

```bash
# de POE642_CasaA/scripts/; a final é regravada no lugar (--antes guarda uma cópia da anterior)
python3 cortinas_franzidas.py A-1Pavimento      # 8 panos
python3 cortinas_franzidas.py B-Terreo          # 10
python3 cortinas_franzidas.py D-Terreo          # 12 (8 virados)
python3 cortinas_franzidas.py E-Terreo          # 5
python3 cortinas_franzidas.py E-1Pavimento      # 10
# a Casa C já desenha o pano franzido no motor: python3 final3840_casac.py Terreo --de cortinas
# depois, as pranchas e os PDFs (rodape_entrega.py --no-quadro --render <Pavimento>=<final> e pdf_entrega.py, com a config de cada casa)
```

Rodar de novo sobre uma final que já tem o pano franzido não serve: o script procura o pano antigo. Para refazer, volte a final anterior (a do commit de 27/10, antes das cortinas) e rode de novo. Os Subsolos não mudam: a hachura deles usa só o contorno do lote do Térreo. Antes e depois: `renders/..._cortinas2710_antes_depois.jpg` em cada casa.

## As finais da Casa E em 3840 px com a auditoria de 26/10 (`final3840_casae.py`)

Pedido do usuário (28/10/26): "PODE COMEÇAR COM O SUBSOLO, NA SEQUENCIA O TERREO E DEPOIS O PRIMEIRO PAVIMENTO [...] ELENQUE AS ALTERAÇÕES, APLIQUE-AS E AMANHÃ CEDO EU VALIDO." A lista de cada planta está no handoff ("Casa E · rodada de 28/10/26").

Como funciona:
- **Ponto de partida.** A final aprovada de cada pavimento, lida do git: o commit fica em `PAV_E[...]["aprovada"]`, porque a final é regravada no lugar (`final_aprovada`).
- **Rótulos.** Saem pela conta inversa da composição (`sem_rotulos`): a rotina dos rótulos da Casa E (`retoque_1pav_casae.rotulos_ambientes`, com os ajustes de cada pavimento) é rodada num quadro preto e num branco, o que dá o alfa e a cor de cada px do texto. O fundo é tirado do px da final; onde o alfa passa de 0,8, é refeito pelos vizinhos. No fim, os rótulos são escritos de novo, com os ajustes desta rodada (`AJUSTES_E`, que substituem os de mesmo nome).
- **Quadro.** `QuadroE` é o `final3840_casab.Quadro` com os caminhos da Casa E: PDF, base 16:9 e base chapada da legenda.

Etapas do Subsolo (`passos_subsolo`):
- `pisos`: os pisos nas texturas e escalas das Casas B a D (`troca_piso`, com `F.piso_textura`), na mancha da legenda (`legenda`, sem as manchas soltas de menos de 300 px).
  - As peças ficam: as do PDF (`objetos_pdf`, `CAMADAS_OBJ`, cheias por dentro) e o que a final mostra com outra cor ou muito escuro junto a elas (`_piso_e_peca`, `_pecas_final`, `PECAS_E`).
  - A sombra e o reflexo do render (a mesma cromaticidade do piso, mais escura ou mais clara) saem com o piso velho. As peças que o PDF só traça (`camadas_tracos`, os aparelhos da academia) contam só onde a final não mostra a cor do piso.
  - Por fim, a sombra curta de cada peça.
- `escada`: `escada_e`. Os degraus do PDF na pedra da escada, com o sombreamento de `F.ESCADA_SOMBRA`, sem linhas e sem triângulo. Depois do corte, o trecho nevoado, sem a linha e com a sombra suave no lugar. A letra do PDF (`F.letra`) vai no 1º degrau.
- `armario`: `armario_cabides`, o guarda-roupa aberto com os cabides (`elementos.guarda_roupa`) no retângulo do PDF.
- `bancada`: `bancada_e9`, a borda no tom escurecido da pedra (só fora das paredes) e a sombra curta.
- `paredes`: `paredes_e`, as paredes em cinza 80 nos preenchimentos escuros da ARQ_PAREDE que a final mostra escuros.
  - Desde 28/10, todas as peças entram numa máscara só, desenhada em 4x e reduzida uma vez (sem as juntas claras e escuras entre peças vizinhas).
  - A peça escura pequena (até `PAREDES_E["coberta_max_pt2"]`) que o PDF cobre depois com um branco da mesma camada (`pecas_cobertas`) e que a final já mostra clara sai: os dentes junto ao vidro da piscina do Subsolo, onde a piscina pinta a borda e o degrau por cima (`PISCINA_E["dentes"]`).
  - `sempre`: caixas (pt) onde toda peça escura é parede, sem a conta do escuro (no Subsolo, a caixa da piscina, onde o render pintou água sobre as pontas das paredes).
  - O fundo de toda a parede e do antialias dela é refeito pelo piso de fora (inpaint), para a borda sair regular.
  - `ini` (a final aprovada sem os rótulos; no Subsolo): a sobra cinza da parede antiga do render em volta da nova (os px a até `folga_px` iguais aos da final aprovada e mais escuros que `sobra` do piso claro de perto) sai também.
  - `tirar` e `por`: retângulos (pt) cujas peças escuras saem e que entram na parede (no Subsolo, `PAREDES_SUB_E`: o dente da ponta da parede da sauna trocado pela face reta). `PAREDES_SUB_E` também põe a ARQ_REVESTIMENTOS (as faixas de 0,57 pt das faces) nas camadas.
  - `_uniao` junta os retângulos numa máscara só (em 8x), sem a junta a 50% entre vizinhos.
  - Antes, a franja preta antiga a até 3 px é refeita pelos vizinhos, e também a franja escura de pouca cor (`PAREDES_E["franja"]`).
  - O preto que sobra até 15 px das paredes vai ao cinza pela conta do alfa contra o piso de perto.
  - Os pilares da EST - Pilar ficam pretos.
- `rotulos`: `escrever_rotulos`.

```bash
# de POE642_CasaA/scripts/
python3 final3840_casae.py Subsolo              # -> ../../POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_final.png (+ _preview.jpg)
python3 final3840_casae.py Subsolo --de rotulos # recomeça de uma etapa (as anteriores no cache, $POE642_CACHE ou /tmp/poe642_casae_etapas)
C=../../POE642_CasaE
python3 rodape_entrega.py --config $C/config_bases.json --no-quadro --render Subsolo=$C/renders/POE642_CasaE_PH_Subsolo_v1_final.png
python3 pdf_entrega.py --config $C/config_bases.json
```

Etapas do Térreo (`passos_terreo`):
- `pisos`: só o granito (`PISOS_TER_E`). As projeções da DOC_LINHAS e os elementos fixos ficam por cima (`linhas_pdf`).
- `escadas`: as duas escadas do PDF (`escada_e`, `ESCADAS_TER_E`; `letra_no_alto`: o D no degrau de cima) e os degraus em blocos do deck (`blocos_e`, `BLOCOS_TER_E`).
  - Nos blocos, os retângulos da ARQ_CONTRAPISO são pintados do de baixo ao de cima (`inverter`).
  - Cada bloco é um pouco mais escuro que o de cima (`tom`) e leva a sombra curta dele.
- `armario`: o DCE, aberto para a direita.
- `box`: o WC DCE 1 (`box_e`, as folhas do `AJ.folhas_box` dentro de `BOX_WC_DCE1`, desenhadas por `final3840_casaa.boxes`).
- `bancadas`: `BANCADAS_TER_E`.
- `paredes`: a ARQ_PAREDE e a ARQ_ELEMENTOS FIXOS (`PAREDES_E["camadas"]`; os brises de madeira ficam porque a final não os mostra escuros).
- `seta`: `seta_e`, a do `final3840_casaa_terreo.seta`, com a ponta em `SETA_TER_E`.
- `piscina` (28/10): `piscina_terreo_e`, a água no turquesa do Subsolo pela `piscinas_turquesa.turquesa`, com as duas folhas de vidro do lado esquerdo protegidas (`PISCINA_TER_E`: os traços claros e neutros em pé).
- `rotulos`: com o WC DCE 1 em `AJUSTES_E["Terreo"]`.

```bash
python3 final3840_casae.py Terreo
python3 rodape_entrega.py --config $C/config_bases.json --no-quadro --render Terreo=$C/renders/POE642_CasaE_PH_Terreo_v1_final.png
python3 pdf_entrega.py --config $C/config_bases.json
```

Etapas do 1º Pavimento (`passos_1pav`):
- `nublado`: `nublado_novo`.
  - O contexto antigo (`entorno_esmaecido.contexto_render` do `opcoes_1pav_casae.TERREO`, o retocado de 2000 px) é trocado pelo nublado do Térreo novo (`terreo_para_nublado`: as etapas do Térreo a partir dos pisos, sem as letras, a seta e os rótulos, com a piscina no turquesa, em cache).
  - Fora da pegada (`entorno_esmaecido.pegada` da base do 1º Pavimento, com o `FORA` das opções) a troca é direta; nos vazios, entra a razão novo/antigo.
- `pisos`: o vinílico (`PISOS_1PAV_E`), com as peças da final que o PDF não desenha em `FICAM_1PAV_E`.
- `escada`: `ESCADA_1PAV_E`, o D no degrau de cima.
- `bancadas`: `BANCADAS_1PAV_E`.
- `paredes`.
- `varanda` (28/10, "CORRIJA ESSES RESQUICIOS NO PISO, RENTE AO GUARDA CORPO DA VARANDA DO 1º PAV DA CASA E"): `VARANDA_1PAV_E`. A linha dupla do render logo depois do guarda-corpo da esquerda da varanda grande sai onde aparece (o fio claro mais claro que o escuro em `dif`), com o piso logo depois, espelhado. No canto de baixo (`cantos`), o piso do render em volta dos dois vasos e da planta e o L escuro da base do vaso vêm do Bege Bahia 170 px acima, com as emendas esfumadas; os vasos e a planta (`_planta_vaso`: o verde-oliva, as folhas escuras, o terracota; sem manchas de menos de `mancha_min` px) ficam por cima, com a sombra curta.
- `rotulos`.

No Térreo, a etapa `cortinas` (28/10, "VAMOS ALTERAR O MODELO DAS CORTINAS PARA A QUE ADOTAMOS COMO PADRÃO"; depois, "ESSE É O MODELO DE CORTINA A SER ADOTADO EM TODAS AS CASAS", com as dos quartos da Casa D): `CORTINAS_TER_E`, depois da `seta`.
- O pano já era o franzido de 27/10, mas no travertino claro ele quase sumia e lia-se como a linha em zigue-zague antiga.
- Cada um dos 5 panos sai inteiro (a pegada do `blocos.pano_franzido`, com o piso do ambiente) e volta no mesmo eixo, com o linho um pouco mais fechado (`linho`), o contorno do tecido mais escuro (`contorno`) e a sombra curta mais marcada (`sombra`).
- A corda do render entre o trilho e a primeira folha de vidro do living (`limpar`) sai, com o travertino das mesmas colunas 300 px acima.

A borda das peças vai junto com elas na troca dos pisos (`PECAS_E["borda_px"]`, `borda_desvio`). Os rótulos do 1º Pavimento são escritos de novo com os ajustes aprovados (`retoque_1pav_casae.ROTULOS`).

```bash
python3 final3840_casae.py Terreo --de cortinas      # as cortinas, a piscina e os rótulos do Térreo
python3 final3840_casae.py 1Pavimento
python3 final3840_casae.py 1Pavimento --de varanda  # só a limpeza da varanda e os rótulos
python3 rodape_entrega.py --config $C/config_bases.json --no-quadro --render 1Pavimento=$C/renders/POE642_CasaE_PH_1Pavimento_v1_final.png
python3 pdf_entrega.py --config $C/config_bases.json
```

Depois de mudar o Térreo, apagar o `Terreo_nublado_fonte.png` do cache e rodar o 1º Pavimento de novo.

Pedidos de 28/10 no Subsolo, vendo a final. As etapas novas de `passos_subsolo`:
- `piscina`: `piscina_e`, com a água em `agua_e` e o Barlavento de `fontes_procedurais.barlavento`.
- `sauna`: `sauna_e`.
- `vestiario`: `vestiario_e`, que usa `final3840_casaa`: `bancada_pedra`, `torneira`, `vaso` e `chuveiro`; e `F.cuba_esculpida` com o travertino de `travertino_e`.
- `aparelhos`: `aparelhos_e`, com o material de cada peça em `_material_ap` e o volume em `_sombreado`.
- `portas`: `portas_e`, com as soleiras em `final3840_casaa.soleira_bege` e as de correr em `final3840_casaa.portas_vidro`.

Nos `pisos`:
- O travertino é o `travertino_e`, pelo `piso_textura_e`.
- As `zonas` dos aparelhos e das louças (`zonas_academia`) tiram as peças antigas e enchem os buracos da legenda de piso.
- O `incluir` (`zonas_portas`) põe na legenda de cada piso o quadrante de cada porta e as faixas de `PORTAS_E["limpar"]`.

A etapa `paredes` recebe `extra=` um filtro dos desenhos (a ARQ - Parede das cabines do vestiário), que entram na mesma máscara das paredes.

Pedidos de 28/10, 2ª rodada, no Subsolo:
- `PISCINA_E["agua_extra"]`: a faixa entre a piscina e a parte de baixo, à esquerda do vidro, vira água (sem a divisória), na mesma máscara da água do PDF.
- `DUCHA_AMBIENTE_E` (na etapa `vestiario`): o chuveiro da ducha do ambiente pelo PDF (`final3840_casaa.chuveiro`) e o nicho da parede atrás dele em travertino (`nicho_ducha`). A `zona` dele entra em `zonas_academia`, onde o piso passa inteiro, sem o cálice do render.
- `AJUSTES_E["Subsolo"]`: a casa de máquinas da direita (5,83 m²) no corpo 0,85, no centro do cômodo; o ELEVADOR no centro da cabine, no corpo do PDF.
- `PISCINA_E`: a coluna de Bege Bahia desce até o fundo do degrau da sauna (uma quina só no vidro); a água sem a divisória vai só até a coluna (`agua_extra`); `dentes`, as pecinhas cobertas sob a parede da academia, onde a borda e o degrau passam por cima.
- Etapa nova `elevador` (antes dos `rotulos`): `cabine_elevador_e` refaz a borda direita da cabine sob o rótulo antigo (`ELEVADOR_SUB_E`).
- No `vestiario`, a parede do PDF volta inteira em volta da bancada e do vaso (a borda e a sombra deles não passam para a face da parede).
- `PORTAS_E["vidros"]` (5ª rodada): a porta da cabine do chuveiro do vestiário sai das folhas de giro e entra nos vidros. Fica aberta, como no PDF, no padrão da porta da ducha do ambiente. O 5º elemento opcional do item, `{"batentes": [...]}`, desenha os batentes brancos, como nas de giro. O vidro fica na metade de fora da folha do PDF, com o piso entre ele e a divisória. O quadrante (`arco`) continua em `zonas_portas`.

```bash
python3 final3840_casae.py Subsolo --de pisos     # ~3 min (os pisos); as outras etapas, segundos
```

## O tom da piscina em todas as casas (`piscinas_turquesa.py`)

Pedido de 28/10/26: "APLIQUE ESSE TOM DE PISCINA EM TODAS AS PISCINAS DE TODAS AS CASAS". A água dos Térreos vai ao turquesa do Subsolo da Casa E (`final3840_casae.PISCINA_E`), com a rede das cáusticas dele. Como as piscinas das Casas A a D vêm dos renders de 2000 px, o script troca só a água nas finais aprovadas e as regrava no lugar, como `cortinas_franzidas.py`.

- `turquesa(img, px_m, semente, q, proteger)` acha cada piscina pelo miolo azul (`TURQUESA["ciano"]`, manchas de pelo menos `area_min` px) e vai até a beira quente (o Bege Bahia, a madeira: `quente_br`), a até `beira_px` do miolo.
- Ficam como estão: as peças claras e neutras grandes (`peca_croma`, `peca_px`: as espreguiçadeiras da Casa B) e os px de `proteger`.
- Os traços escuros (`escuro_rel`: os rótulos, os tracejados) são separados da água antiga pelo miolo do traço e postos sobre a nova, sem halo.
- O desenho da água antiga passa ao turquesa com `ganho` (peças, rejunte, degraus, sombra das bordas). Depois entram a sombra curta das beiras (`sombra`) e a rede das cáusticas (`causticas_px` longe das beiras).

```bash
# de POE642_CasaA/scripts/
python3 piscinas_turquesa.py A-Terreo   # e B-Terreo, C-Terreo, D-Terreo; --antes <png> guarda a final anterior
# a Casa E: a etapa "piscina" do Térreo (final3840_casae.py Terreo --de piscina) e o 1º Pavimento de novo
```

### As bordas retas pelo PDF (`--bordas`)

Pedido de 28/10/26, no Térreo da Casa A: "corrija as bordas deixando as perfeitas". `bordas_retas(img, agua_px, pedra_px, pedra_tom, pedra_grao, rede)` refaz as beiras nos retângulos do PDF de `BORDAS[planta]` (pt, levados ao quadro pelo `p2q`):
- `agua`: o preenchimento azul da ARQ_CONTRAPISO (a piscina com a prainha, o spa); a cobertura de cada px vem por supersample (`ss`), para a beira nítida.
- Na faixa de `faixa_px` junto à beira, a água é refeita: o fundo, pelo espelho da água de dentro sem os fios claros; a rede das cáusticas, a mesma que `turquesa` pôs (`rede_turquesa`, refeita da final de antes do turquesa: `--rede`), contínua até a beira e sumindo junto a ela; a sombra curta (`sombra`, a do `PISCINA_E`) a partir da beira exata.
- Fora da água, o piso de fora é espelhado sobre a água que passava e o fio claro antigo; o alcance é medido em cada lado (até `fora_px`, pela diferença da linha ao piso de mais longe, `fora_dif`), para não dobrar os fios do piso numa linha paralela à beira.
- `pedra`: as faixas entre as linhas do PDF (entre o deck e a piscina, o anel do spa), na pedra clara lisa (`pedra_tom`, `pedra_grao`).
- Os traços escuros e neutros por cima (os tracejados de projeção, `traco`) ficam.

Desde o pedido seguinte ("aplique nas bordas das outras casas também"), a rotina vale para todas as casas:
- `agua` em `BORDAS[planta]`: os corpos d'água, cada um um retângulo ou a lista dos retângulos que o formam (a piscina com a prainha; o L da Casa B, com a faixa à esquerda do braço, que é água na base da legenda). As distâncias à beira são medidas pelos eixos na união dos retângulos (`_distancias`); nos cantos para dentro, o espelho segue a direção da beira mais perto; por fora dos cantos, o piso só é espelhado quando os dois lados que se encontram ali são limpos.
- `proteger`: os px que ficam como estão (`_bordas_px` desenha as `CAMADAS_PROTEGIDAS` do PDF perto da água: o muro fino ao lado da piscina da Casa C). `BORDAS["D-Terreo"]["proteger"] = ()`: a parede fina da piscina da Casa D virou no render um contorno borrado e sai.
- `quadro(planta)`: o quadro da prancha de cada casa (o `p2q` do PDF).
- A Casa E faz as bordas na etapa `piscina` do motor (`final3840_casae.piscina_terreo_e`), logo depois do turquesa, com a mesma rede e os vidros protegidos; depois, apagar o `Terreo_nublado_fonte.png` do cache e rodar o 1º Pavimento.

```bash
# de POE642_CasaA/scripts/; o antes do turquesa sai do git (o commit anterior a 3041093)
git show 3041093^:projetos/POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_rotulos.png > /tmp/a_pre_turquesa.png
python3 piscinas_turquesa.py A-Terreo --bordas --rede /tmp/a_pre_turquesa.png   # e B-Terreo, C-Terreo, D-Terreo
python3 final3840_casae.py Terreo --de piscina && python3 final3840_casae.py 1Pavimento   # a Casa E
```

### Os vidros da borda no desenho da Casa C (`--vidros`)

Pedidos de 28/10/26: "faça a representação do vidro borda da piscina da casa B igual ao da Casa C. Na verdade, na casa B são dois vidros na borda"; "faça o mesmo na piscina da casa E, com duas bordas em vidro". `vidros_borda(img, vidros_px, q, pontas)` desenha cada vidro de `VIDROS_BORDA[planta]` (pt do PDF e o lado da água) com o perfil do vidro da borda infinita da Casa C na final (`VIDRO`, a mediana de 135 linhas):
- de fora para a água: o fio claro do topo (1 px), o corpo turquesa escuro (3 px, mais claro para dentro), o fio escuro da face junto à água (2 px) e a passagem clara (1 px), num vidro de `larg_ref` = 7 px; num vidro mais fino, tudo na proporção; num mais largo, os fios ficam e o corpo estica;
- as faces e as pontas com a cobertura exata de cada px (`ss`); o corpo acompanha de leve a luz da água ao lado (`luz_agua`);
- `pontas=True` (Casa E): as `ponta_px` linhas da pedra logo acima e abaixo do vidro, onde o cinza do vidro antigo avançava sobre o Bege Bahia, refeitas com a pedra espelhada na mesma coluna.

`VIDROS_BORDA`:
- `B-Terreo`: a faixa branca de 17 pt entre o deck e o braço (sem divisões no PDF) leva dois vidros de 5,7 pt (a largura do da Casa C), um junto ao deck e outro junto ao braço, com a água entre eles; do fim da pedra de cima ao bloco de pedra de baixo.
- `E-Terreo`: as duas lâminas da ARQ_PAREDE (1,7 + 5,1 + 1,7 pt) do lado esquerdo da piscina, na altura da água; entram na etapa `piscina` do motor (`final3840_casae.piscina_terreo_e`), depois das bordas.

```bash
# de POE642_CasaA/scripts/, depois das bordas
python3 piscinas_turquesa.py B-Terreo --vidros
python3 final3840_casae.py Terreo --de piscina && python3 final3840_casae.py 1Pavimento   # a Casa E (apagar antes o Terreo_nublado_fonte.png do cache)
```

## Os boxes dos chuveiros fechados, sem tracejado (`final3840_casaa.boxes`, `colar_boxes.py`)

Pedido de 28/10/26, com o recorte dos BH 1 e 2 da Casa C: "MELHORE A REPRESENTAÇÃO DOS BOX DOS CHUVEIROS COM FOLHA CONTÍNUA, SEM TRACEJADO. REVEJA TODOS OS BOX DE TODOS OS AMBIENTES". Os boxes de correr (`AJ.folhas_box`) das Casas A, C, D e E saem todos de `final3840_casaa.boxes`, que desenhava as duas folhas do PDF e o trilho tracejado no vão de passagem, por cima do tracejado do render. Agora o box vai fechado:
- `vao_box(Q, box)`: o vão ao longo do box (pt), de cada ponta das folhas até a face mais perto do que é escuro no PDF e cruza a linha do vidro (a parede ou o perfil do box junto a ela; preenchimentos com o cinza médio até `escuro`), procurada até o fim do trilho mais `encaixe_pt`. A primeira parede a partir das folhas para o vão: na Casa A, o trilho que `AJ.folhas_box` junta à antessala segue, no mesmo alinhamento, até o banho feminino, do outro lado da parede.
- `limpar_box(Q, out, box, v0, v1)`: a faixa de `limpa_px` = 4 px de cada lado da linha, de ponta a ponta do vão, volta ao piso (cada metade é o piso logo ao lado dela, espelhado; a emenda do meio fica sob o vidro). Saem o traço e o tracejado antigos do render e o desenho anterior do box, de modo que a rotina vale também sobre uma final pronta.
- as duas folhas desencontradas (`afasta_px`), cada uma com metade do vão e a sobreposição de `sobrepoe` = 10% no meio; a que começa antes no PDF fica na ponta de cima (ou da esquerda). Faces finas e sombra curta como antes; sem o trilho.

Nos motores:
- Casa A: no Subsolo e no 1º Pavimento, os boxes passam a ser a etapa `boxes` (depois de `banhos`); no Térreo, o box do banho do motorista sai da etapa `motorista` para a `box_motorista` (também `FA.boxes`, no lugar do desenho próprio de folhas e trilho contínuo). Os três motores aceitam `--so` (as etapas sobre a final atual, no lugar), que é como as finais da Casa A foram refeitas (o motor da Casa A não tem cache):
  `python3 final3840_casaa.py Subsolo --so boxes`, `python3 final3840_casaa_terreo.py --so box_motorista,box_varanda`, `python3 final3840_casaa_1pav.py --so boxes`.
- Casas C e D: `boxes_t`, `boxes_s`, `boxes_terreo_d` e `box_wc_dce_d` seguem chamando `FA.boxes`.
- Casa E: a etapa `box` do Térreo (`boxes_terreo_e`) desenha também o box do banho gourmet (`BOX_GOURMET_E`), que vinha do retoque só com as duas folhas e o vão até a parede de cima vazio; o Térreo esmaecido do 1º Pavimento (`terreo_para_nublado`) usa a mesma rotina.

`colar_boxes.py`: os motores das Casas C, D e E, refeitos da etapa dos boxes, redesenham também as paredes, com o antialias das bordas 1 px diferente do da final aprovada (e, nas Casas C e D, saem antes do turquesa e das bordas da piscina). A final aprovada recebe da refeita só a faixa de cada box (o vão de `vao_box` com `folga_px` nas pontas, `meia_px` = 8 px de cada lado da linha):

```bash
# de POE642_CasaA/scripts/
python3 final3840_casac.py Terreo --de boxes          # e Subsolo; Casa D: Terreo --de boxes, Subsolo --de banhos
python3 final3840_casae.py Terreo --de box            # e, sem o Terreo_nublado_fonte.png no cache, 1Pavimento
git show HEAD:projetos/POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png > /tmp/c_antes.png
cp ../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png /tmp/c_motor.png
python3 colar_boxes.py C-Terreo --antes /tmp/c_antes.png --nova /tmp/c_motor.png \
    --saida ../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png
# no 1º Pavimento da Casa E, os boxes do Térreo esmaecido: python3 colar_boxes.py E-Terreo com as finais do 1º Pavimento
```

Ficam como estavam: os boxes da Casa B (`F.boxes_vidro`, já um vidro só de parede a parede), os vidros fixos e as portas de vidro dos BH master da Casa C (`F.boxes_vidro`), os boxes no granito (`F.boxes_granito`, `box_gourmet_d`), o box do Subsolo da Casa E (`retoque_subsolo_casae.vidro_box`) e os do 1º Pavimento da Casa E (`retoque_1pav_casae.boxes_continuos`), todos já contínuos e sem tracejado.

### A porta do WC DCE da Casa D e o nicho da cabine do vestiário da Casa E (28/10)

- `final3840_casad.entre_porta_box_td` (na etapa `esquadrias` do Térreo, depois de `pos_esquadrias_d`): a limpeza das esquadrias (`F.esquadrias_terreo`) espelhava o vidro do box, logo abaixo da folha aberta da porta do WC DCE, sobre a folha antiga do render, e ficava uma segunda folha a 5 px da porta. Entre a face de baixo da folha do PDF e a linha do box (`ENTRE_PORTA_BOX_TD`), o piso volta ao de antes das esquadrias, com as colunas das duas pontas da folha; na ponta junto à parede, o piso da coluna ao lado. Aplicado sobre a final com a etapa `soleiras` do cache como o "antes" (o resto da final não muda).
- `final3840_casae.nicho_ducha(Q, img, q)`: o nicho em travertino também com o fundo à direita (`"fundo": "direita"`: a sombra curta do fundo e da lateral de cima). `NICHO_CABINE_E`, na etapa `vestiario` do Subsolo, antes do chuveiro da cabine: o nicho do PDF na parede da direita, onde o braço chega, no lugar da moldura escura do render. `python3 final3840_casae.py Subsolo --de vestiario` (só o nicho muda).

### A revisão do Subsolo da Casa E (28/10): contorno da piscina, barra de alongamento e batentes do elevador

Os três itens da revisão do Subsolo, com o OK do usuário (no item 2, a correção dele: não é TV, é uma barra de alongamento):
- **Contorno da piscina** (`PISCINA_E["contorno"]`, `piscina_e`, `paredes_e(..., brancos=...)`): os retângulos brancos que o PDF pinta por cima da parede, depois dela, em volta do fundo da piscina (a faixa da esquerda até o fim, a de baixo, o degrau e a faixa sob a parte da direita até o degrau da sauna). Em `piscina_e`, eles saem da parede (`par`) e entram na borda de Bege Bahia. A janela da piscina desce até `fundo_pt`, mas a água e o degrau da sauna continuam desenhados na janela de antes (o mesmo ruído e as mesmas pastilhas). A textura do Bege Bahia, tecida mais alta, mantém as linhas de cima iguais. Antes da borda, a franja preta e borrada da parede antiga do render, até 3 px para fora do contorno (mais escura que `franja` × o claro de perto), é refeita pelo fundo de fora (inpaint). Em `paredes_e`, `brancos` tira esses retângulos da máscara da parede (`a`), por subtração da área. A parede fica só nas faixas cinza do PDF.
- **Barra de alongamento** (`ACADEMIA_E["moldura"]`, `aparelhos_e`): o aparelho de tipo `alongamento` pega também a moldura da ARQ_MARCENARIA em volta das barras da ARQ_ MOB COMUM. Cada célula vai no material pela camada da peça de baixo: a moldura em `madeira` (bisel), as barras do meio em `cromo` (cilindro). A zona do piso continua a caixa das barras com 0,45 m de folga, que já cobria a moldura.
- **Batentes do elevador** (`PAREDES_SUB_E["por"]`, `PORTAS_E["limpar"]`): as duas tiras cinza do PDF, da face da parede até 1014,1 pt, entram na parede (a final as mostrava claras, e as peças ficavam de fora). O vinílico diante da porta é refeito antes, nos pisos (`incluir`, pelas `zonas_portas`). A faixa de 3,6 pt logo abaixo da face da parede fica fora da legenda do vinílico (a linha do contrapiso do PDF): numa zona da academia ela não entrava, e a mancha do render ficava.
- Na emenda da borda com a coluna de cima e nas beiras do contorno, a parede entra em `piscina_e` pela área do PDF (`Q._par`), e não pela máscara de >5 %. O contorno está nas coordenadas exatas do PDF e é rasterizado como os preenchimentos dele (`_ret_pdf`: fillPoly a 4×, o mesmo de `Q.preencher` e das peças de `paredes_e`). Com a máscara, ou com o retângulo a 8× (`_uniao`), a borda comum caía em outro subpixel, e a linha da emenda ficava com ~12 % de parede, uma linha mais escura.

Rodado de `--de pisos`. Na final aprovada entram só as três regiões, porque o resto da rodada tem a deriva do antialias das paredes.

### A revisão do Térreo da Casa E (28/10): adega, pisantes, curva da pedra portuguesa e projeção da cobertura

Os quatro itens da revisão do Térreo, com o OK do usuário ("pode aplicar os 4"), na etapa `revisao` de `passos_terreo` (`revisao_terreo_e`, antes dos rótulos; config `REVISAO_TE`). A final das etapas em cache é anterior aos acertos feitos direto na final aprovada, e por isso a etapa vai sobre a final: `python3 final3840_casae.py Terreo --sobre-final revisao` (`sobre_final`: lê a final, aplica só a etapa e regrava a final e a prévia).
- **Adega** (`adega_porta_te`, `REVISAO_TE["adega"]`): a faixa do vão, do fim das prateleiras ao travertino limpo do hall (`faixa_pt`), volta ao travertino do hall (as linhas logo abaixo, em espelho), com as paredes do PDF por cima (`Q._par`, no cinza de `PAREDES_E`). A porta vai por `final3840_casaa.portas_vidro`, em duas entradas: o vidro fixo da esquerda (a linha do PDF em 1004,6 pt, sem montantes), com a soleira de Bege Bahia e os três batentes, e as duas folhas de correr, nos planos do PDF, com os montantes de 2,84 pt.
- **Pisantes** (`pisantes_te`, `REVISAO_TE["pisantes"]`): os 9 retângulos cinza da ARQ_CONTRAPISO do caminho (`_ret_pdf`, a 8×), em Bege Bahia da biblioteca (`textura("bege_bahia")`, força 0,75, no tom do miolo dos pisantes antigos, cada peça ±1,5 %), com a sombra curta na grama. Em volta, o que não é verde perto das pedras (a borda clara, os restos da pedra antiga) e as próprias pedras saem e voltam pela grama vizinha (inpaint). Na pedra grande do acesso (o preenchimento 197), nas `faixas` junto à borda da direita e ao canto de baixo, as manchas (verde, escuro ou o verde quase no vermelho) e as 3 últimas colunas ou linhas vêm em espelho da pedra mais para dentro (a linha de espelho a 18 e 14 px da borda), e a borda vai na reta do PDF; fora das faixas, a pedra grande fica como estava.
- **Curva da pedra portuguesa** (`curva_pedra_te`, `REVISAO_TE["curva"]`): o preenchimento 35463 da ARQ_CONTRAPISO, com as curvas amostradas a 64 pontos por Bézier (`AJ.caminhos_pdf(..., passos=64)`). A distância com sinal à curva (`distanceTransform` a 4×) dá a normal. De cada lado, a faixa de `d0_px` vem em espelho de logo além dela (`espelho`: a pedra de dentro, a grama de fora), composta com o antialias do PDF, só onde do lado de fora há grama (`grama_min` do verde em volta). Onde a grama de fora é estreita (o espelho cai num pisante), a grama vem da vizinha (inpaint). Antes, o que não é pedra até `mancha_px` dentro da curva, junto à grama (verde, ou abaixo de `escuro`; a pedra portuguesa não desce de ~155), vem em espelho da pedra mais para dentro: a mancha escura junto ao arbusto de cima.
- **Projeção da cobertura** (`projecao_cobertura_te`, `REVISAO_TE["projecao"]`): o tracejado do retoque (`retoque_terreo_casae.PROJECOES`: traço de 8,5 pt, vão de 4,25 pt, cinza 150, força 0,85), na largura da varanda na prancha (1,1 px), nas linhas do PDF: a da laje da garagem (687,8 pt) e a borda de cima (516,3 pt) com a lateral direita (2763,5 pt) até a pedra portuguesa. Nada sobre as paredes (`Q._par` com 1 px de folga). O granito refeito em 28/10 (01:47) tinha levado o tracejado que estava sobre ele.
- **O Térreo nublado do 1º Pavimento**: `terreo_para_nublado` passa a aplicar `revisao_terreo_e` antes de gravar a fonte em cache. Na final do 1º Pavimento, `python3 final3840_casae.py 1Pavimento --sobre-final nublado_revisao` (`nublado_revisao_te`, em `SO_SOBRE_FINAL`) soma só a diferença entre o nublado da fonte em cache e o dela com a revisão, onde a final mostra o Térreo (`_onde_terreo`, `_trocar_nublado`, as mesmas de `nublado_novo`), e regrava a fonte com a revisão.

### A seta da entrada e o rótulo do hall do Térreo da Casa E (28/10)

Pedido do usuário: "A seta em preto deve ficar em frente a porta, um pouco mais acima de onde ela está. e o rótulo do hall de entrada não pode ficar sobre o tracejado".
- **Seta** (`SETA_TER_E`): a ponta vai ao meio do vão da porta pivotante do PDF (entre os batentes de 1488,3 e 1638,6 pt; o meio, 1563,5 pt, cai em y = 1408 px). Antes, em `SETA_TER_E_ANTES` (y = 1542 px), ela apontava para o vidro fixo abaixo da porta.
- **Rótulo** (`AJUSTES_E["Terreo"]`, "HALL DE ENTRADA"): o desvio (35,4; −20,3) em px de 2000 leva o rótulo à direita do cruzamento do X tracejado, entre ele e a porta, no corpo de sempre (1,3). É o lugar do hall com mais folga (~10 px) do tracejado da DOC_LINHAS, das paredes e dos objetos (a planta, o banco, a folha da porta), achado numa busca da caixa do rótulo sobre a final sem os rótulos. O outro lugar livre, sob a folha da porta, tinha ~7 px de folga.
- **Na final** (`seta_rotulo_hall_te`, em `SO_SOBRE_FINAL["Terreo"]`; `python3 final3840_casae.py Terreo --sobre-final seta_hall`): a seta antiga sai (a máscara dela, com 2 px de folga e a borda esfumada, recebe o Bege Bahia de 38 px acima, nas mesmas colunas), e a nova é desenhada por `seta_e`. Para o rótulo, a final sem os rótulos (`sem_rotulos`) recebe todos de novo (`escrever_rotulos`), e só as caixas do rótulo do hall (a de antes e a nova, com 4 px de folga) voltam à final. Numa rodada do zero, as etapas `seta` e `rotulos` já usam os valores novos.

### Os tracejados do Térreo da Casa E (28/10): a borda da varanda reta e o preto ou branco

Pedidos do usuário, vendo a borda de baixo da varanda: "não existe esse dente. o tracejado é em linha reta"; e depois, "os tracejados são ou brancos ou pretos, a depender do fundo".
- **A borda reta** (`dente_varanda_te`, `DENTE_VARANDA_TE`, no fim de `revisao_terreo_e`): no retoque, o L (`retoque_terreo_casae.PROJECOES`) seguia a borda da varanda do 1º Pavimento (ARQ_CONTRAPISO, 1694,1 pt) até 1204,5 pt e, dali até a sala, a face da parede da suíte 3 (1688,5 pt), com o degrau de 10 cm. A projeção vai na borda da laje: o retângulo do trecho da direita e do degrau recebe o piso de `desvio_px` acima, com as emendas de cima e de baixo esfumadas, e a planta do canto e a sombra dela ficam (`poupa_px`). Os traços cinza seguem retos até 1380 pt no molde do trecho da esquerda: o alfa médio dos 17 traços inteiros, na mesma fase. Esse cinza fica por baixo do preto da etapa seguinte.
- **Preto ou branco** (`tracejados_pb_te`, `TRACEJADOS_TE`, a etapa `tracejados`, antes dos rótulos): os traços nítidos (1,5 px), como `final3840_casaa_terreo.PROJ`, por cima do cinza antigo e nos mesmos traços:
  - as projeções da cobertura do retoque, com a borda de baixo reta: traço de 8,5 pt, vão de 4,25 pt, cada reta começando num traço (`_tracos_te`);
  - as cadeias da DOC_LINHAS E PROJEÇÕES (`cadeias_tracejadas`), menos as linhas do lote (`max_doc_pt`) e o que fica acima de `topo_q`;
  - fora: o traço com o meio numa parede do PDF (`folga_px`); as paredes voltam por cima;
  - a cor traço a traço, pela mediana da luminância numa faixa de `fundo_px` (sem o traço e sem as paredes), com a mediana dos 5 vizinhos da mesma reta: a cor troca onde o piso troca e não pisca sobre a divisa de dois fundos.
- **Na final** (`tracejados_sobre_final_te`, `--sobre-final tracejados_final`): o cinza da projeção da revisão (o de `projecao_cobertura_te`, que saiu de `revisao_terreo_e`) é desfeito pelo alfa dele (`_alfa_projecao_te`), a borda fica reta, e os traços vão na final sem os rótulos desta rodada (`sem_rotulos(..., novos=True)`), com os rótulos de novo por cima. Na final, só a faixa dos traços muda.
- **O nublado do 1º Pavimento** (`nublado_tracejados_te`, `--sobre-final nublado_tracejados`): como no 1º Pavimento da Casa A, o Térreo nublado não leva as projeções do Térreo. Sai o tracejado cinza que tinha entrado com a revisão, e a borda da varanda fica reta, pela diferença entre a fonte do nublado em cache e ela sem esse tracejado. `terreo_para_nublado` aplica `revisao_terreo_e`, mas não os tracejados.
- **Ordem na final do Térreo:** a final de d262d99 → `tracejados_final` → `vao_servico` (abaixo). `tracejados_final` refaz o dia de ce2429a: o vão e o rótulo novo da área de serviço ficam fora dele (`vaos=False` e `sem_ajustes`).

### O X aberto sob o rótulo da área de serviço descoberta (28/10)

Pedido do usuário (opção A): "abrir o X embaixo do rótulo, com o tracejado parando numa folga em volta do texto e o rótulo no centro", como o X do shaft da Casa B (`final3840_casab.PROJ_B["vaos_texto"]`). O ambiente é estreito e o X ocupa tudo; com o rótulo inteiro, não há lugar livre.
- **O rótulo** (`ROTULO_SERVICO_TE`, em `AJUSTES_E["Terreo"]`): o desvio (−38,6; 3,9) em px de 2000 leva o centro do bloco (as três linhas) ao cruzamento do X, (2060,4; 496,5) px da final, achado pelas retas das duas diagonais da DOC_LINHAS.
- **O vão** (`TRACEJADOS_TE["vaos"]`, `_vaos_te`): a caixa do texto escrito (`caixas_rotulos`, o rótulo sozinho num fundo preto) com `folga_px` (8 px, ~13 cm). Em `tracejados_pb_te`, cada traço é cortado na borda da caixa (`_fora_das_caixas`, Liang-Barsky); o pedaço com menos de `min_px` sai.
- **A limpeza** (`_limpa_tracos`): dentro das caixas, os px das linhas tracejadas (`limpa_px` de cada lado, os vãos entre os traços incluídos) recebem o mesmo granito deslocado (`deslocs`, o primeiro deslocamento que cai no granito do PDF, fora das linhas e das paredes), sem mancha; o que sobra iria ao inpaint (0 px aqui).
- **Na final** (`vao_rotulo_servico_te`, `--sobre-final vao_servico`): a final sem os rótulos (o da área de serviço no lugar de antes, `sem_ajustes`), a limpeza no vão e no lugar velho do rótulo (as letras de alfa > 0,8 também, no lugar do inpaint de `sem_rotulos`), os traços com o vão e os rótulos de novo; na final, só essas duas caixas mudam. Numa rodada do zero, as etapas `tracejados` e `rotulos` já fazem isso.

### Os tracejados do 1º Pavimento da Casa E em preto ou branco (28/10)

Pedido do usuário ("os tracejados são ou brancos ou pretos, a depender do fundo"; para o 1º Pavimento, "pode").
- **Os traços** (`TRACEJADOS_1P["grupos"]`, `_tracos_1p`): os da DOC_LINHAS E PROJEÇÕES que o retoque desenhava em cinza, sem os repetidos: os X dos dois vazios (`retoque_1pav_casae.VAZIOS`: o da escada e o do hall, o cinza multiplicado pelo Térreo nublado) e os grupos de `retoque_1pav_casae.PROJECOES_1P` (o X do shaft, o desenho da rouparia, os X rasos do banho master sobre o vaso e o box).
- **A limpeza** (`_limpa_tracos` com `trechos` e `fonte`): o cinza sai com o fundo ao lado, tirado do mesmo grupo (nos vazios, só do vazio, `_onde_terreo`), com deslocamentos menores (`limpa_px` 2).
- **O traço** (`tracejados_pb_te` com `trechos`): o mesmo do Térreo (1,5 px, a cor pelo fundo, a mediana dos 5 vizinhos): 104 traços em preto (os vazios, o shaft, o banho master) e 18 em branco (a rouparia, no vinílico).
- **Na final** (`tracejados_1p_sobre_final`, `python3 final3840_casae.py 1Pavimento --sobre-final tracejados_final`): a final sem os rótulos, os traços, os rótulos de novo; na final, só a faixa dos traços. Numa rodada do zero, a etapa `tracejados` (antes de `rotulos`) faz o mesmo.
- **O Subsolo** não desenha tracejado de projeção (as curvas de nível, a escada e as linhas da academia do PDF ficam fora da final): nada a mudar.
- **A rouparia** (usuário, opção A, como na área de serviço do Térreo): `TRACEJADOS_1P["vaos"]` (`pavimento` 1Pavimento, `rotulos` ROUPARIA, `folga_px` 4). O texto (54 px) é mais largo que o desenho (48 px); com 4 px (~7 cm) ficam a borda de cima, a de baixo e o pé das pernas. `tracejados_pb_te` corta os traços na caixa também quando recebe `trechos` (a limpeza, aí, é de quem chama).
- **A limpeza fora dos vazios** (`_limpa_tracos` com `mesmo` e `media`): o fundo vem da caixa do grupo com `fonte_px` (10) de folga, no mesmo material do PDF que o px refeito (o código de cor de `Q.chapada`: o vinílico no vinílico, o vaso no vaso, o quartzito no quartzito), primeiro pela média dos dois lados da faixa (o px deslocado para um lado e para o outro, que segue o degradê) e depois pelo px de um lado só. Na rouparia, `limpa_px` 3 tira também o halo escuro que o render deixou a ±3 px do traço antigo.
- **Os vazios** (`_bordas_vazio`): as linhas e as colunas a até `borda_px` (10) da borda cuja mediana de luz se afasta mais de `borda_tol` (30) da do miolo (a linha do degrau, o vidro, a face da parede), com 1 px em volta, são refeitas só ao longo delas: as de cima e de baixo com `deslocs_linha` (na horizontal), as dos lados com `deslocs_coluna` (na vertical). O resto do vazio (o nublado, a sombra da parede) vai pela média dos dois lados e, onde não há par, pelo inpaint (`so_media`). Assim a faixa não puxa o tom da escada ou do vidro para dentro do vazio, e as linhas da borda ficam inteiras. O X vai de canto a canto (cortado só no vazio, `_onde_terreo`, menos 1 px).
- **O Térreo nublado nos vazios**: os traços do Térreo (`_tracos_te` do QuadroE do Térreo, levados ao quadro do 1º Pavimento) com o meio num vazio saem pela mesma limpeza; no vazio do hall, a linha da esquerda do X do hall do Térreo (a de 90°), que aparecia fraca.
- **Na final:** a final de ce2429a (antes de ee4c56e) → `--sobre-final tracejados_final`, que agora faz tudo numa passada.

### O sofá da sala íntima, a poltrona da suíte master e as poltronas do living da Casa E (28/10)

Pedidos do usuário: "corrija a imperfeição no sofá gerada pelo piso. no primeiro pavimento da casa E"; "corrija o contorno do encosto da poltrona da suite master"; "vamos aplicar essa poltrona da sala íntima do primeiro pavimento da casa e em substituição das poltronas a todas as 6 poltronas do terreo, também da casa E".
- **O sofá** (`SOFA_1P`, `sofa_sala_intima_1p`, etapa `sofa` do 1º Pavimento): a borda de cima do encosto tinha dois entalhes do render junto às emendas das almofadas. Em cada `remendos` (x0, x1, y0, y1 em px da final, `dx`), o topo do encosto e a sombra fina dele vêm da mesma linha, das colunas a `dx` px, com `suave_px` de transição: a borda fica reta (y = 1199 px).
- **A poltrona da suíte master** (`POLTRONA_MASTER_1P`, `poltrona_master_1p` → `contorno_peca`, etapa `poltrona_master`): a peça é o estofado claro (R − B abaixo de `rb_max`, luz acima de `lum_min`) ligado à `semente`, fora do meio-plano `corte` (a reta pela quina de cima: o tapete e a mesa lateral ficam fora), com os furos cheios; a silhueta alisada (desfoque de `sigma` px) leva os entalhes ao estofado mais perto e os calombos e a franja (o que, a até `franja_px` da peça, não é vinílico: `piso_rb`, `piso_lum`) ao vinílico mais perto. Só muda uma faixa fina da borda, a mais de 2 px do corte (junto dele, a borda alisada levava o vinílico para a quina do encosto).
- **As poltronas do living** (`POLTRONAS_TE`, `poltronas_living_te`, etapa `poltronas` do Térreo, depois de `tracejados`):
  - o modelo (`_modelo_poltrona_1p`): a concha da sala íntima recortada da final do 1º Pavimento (`modelo`: o estofado claro fechado pelo envoltório convexo, mais a borda sombreada do encosto do lado do vinílico, à direita de `borda_x`), com o alfa antisserrilhado; `frente` é para onde a abertura aponta no recorte;
  - as 6 bouclé de `retoque_terreo_casae.POLTRONAS` (`bloco_velho`): cada uma redesenhada como na final (girada, no tamanho do PDF) dá a máscara da peça velha, com `folga_px`;
  - nas 4 da mesa redonda, mais o disco de `raio_mesa` (1,15) x tamanho e o deslocado da sombra do motor (`sombra_motor`): o halo escuro do retoque acaba a ~1,1 x tamanho; a mesa (`POLTRONAS["proteger"]`, com `mesa_folga_px`) fica. O buraco recebe o travertino deslocado (`_melhor_desloc`: `busca` x tamanho nas `direcoes`, sem px de outra peça nem das máscaras ainda por fazer, o veio vertical pesando contra o lado) por cópia direta, com o tom corrigido pela mediana do anel (`_fonte_tom`) e a borda esfumada em `esfuma_px` (o clone de Poisson puxava o escuro da mesa e do halo para dentro). Depois, a sombra da mesa (`mesa_sombra`) é refeita só sobre o piso novo;
  - nas 2 do tapete (`no_tapete`), só a bouclé com `folga_tapete_px`. O tapete é a luz desfocada entre `tapete_lum` (185 a 213); o travertino, acima. A borda do tapete dentro do buraco segue o contorno do tapete (`_borda_tapete`, abaixo; antes, puxada do anel por `cv2.inpaint`, ela fazia um dente atrás da poltrona de cima). Cada material vem de `_material_por_ladrilhos`: o tom pelo desfoque (`tom_px`) só do material limpo em volta e o grão (o que sobra do desfoque de 3 px) em ladrilhos de `ladrilho_px` com meia sobreposição e janela de Hann, cada um do trecho mais perto em que cabe todo no material (até `busca_max` x tamanho); não há trecho limpo de tapete do tamanho do buraco;
  - a poltrona nova (`_girar_peca`, `T.pousar_planta`): no centro e no tamanho do PDF (o maior lado), virada para o ponto do PDF, com a `sombra` (opacidade 0,6) e o `sombra_contato`, para a concha creme não sumir no travertino claro.
- **Na final:** 1º Pavimento: a final de da8fecd → `--sobre-final sofa` → `--sobre-final poltrona_master`. Térreo: a final de da8fecd → `--sobre-final poltronas_living` (`poltronas_living_sobre_final_te`: a final sem os rótulos, as poltronas, os rótulos de novo; na final, só a área mudada).
- **O Térreo nublado do 1º Pavimento** (usuário: "pode refazer o nublado"; `nublado_poltronas_te`, `python3 final3840_casae.py 1Pavimento --sobre-final nublado_poltronas`): a fonte do nublado em cache (`Terreo_nublado_fonte.png`, o Térreo sem rótulos) passa por `poltronas_living_te`, e entra na final só a diferença entre ela nublada antes e depois (`_trocar_nublado`): 4267 px, na faixa abaixo da sala íntima. O cache fica com as poltronas novas; numa rodada do zero, `terreo_para_nublado` já as põe (depois de `revisao_terreo_e`).
- **Na final do 1º Pavimento:** depois de `poltrona_master`, `--sobre-final nublado_poltronas`.

### O contorno do tapete atrás das poltronas do living e o sofá da varanda da Casa E (28/10)

Pedidos do usuário: "precisa aprimorar o contorno do tapete na parte onde incluimos as poltronas, logo atrás dela. seguindo a direção correta e dando a impressão de continuidade"; "você consegue substituir o sofá da varanda da casa e pelo sofá da sala íntima do primeiro pavimento, deixando apenas a parte horizontal? teria que remover o último módulo do L para dar certo".
- **O contorno do tapete** (`_borda_tapete`, em `poltronas_living_te`): o tapete do render (a luz entre `tapete_lum`) só dentro do tapete do PDF (o branco dos móveis do estar da chapada, com as linhas fechadas, mais `tapete_folga_px`); do centro dele, direção a direção (`passo_graus`, até `raio_max_px`), a distância ao último px de tapete no raio. Onde esse px encosta num buraco (as poltronas na borda), a distância vem das direções vizinhas, interpolada no ângulo e alisada em `suave_graus`; a borda nova vai com `tapete_borda_px` de transição. Assim a borda passa atrás das duas poltronas na diagonal do tapete, sem o dente. `_material_por_ladrilhos` passou a usar o px de antes onde não há material limpo por perto para o tom (o que dava preto na faixa esfumada).
- **O sofá da varanda** (`SOFA_VARANDA_TE`, `sofa_varanda_te`, etapa `sofa_varanda` do Térreo, depois de `poltronas`):
  - o modelo (`_modelo_sofa_1p`): o sofá em L da sala íntima recortado da final do 1º Pavimento ("modelo": em cada linha, do primeiro ao último px do estofado claro, luz acima de `lum_min` e R − B abaixo de `rb_max`, até a frente dos assentos, `frente_y`); a perna do L sai com o módulo do canto, e no lugar dele vai o módulo da direita inteiro (`modulo_x`, da costura ao fim do braço, com a almofada creme e a marrom) espelhado (usuário: "por que não pegar todo o modulo da direita e espelhar para a esquerda, usando as almofadas?"); o módulo do meio (`meio_x`, entre as costuras) fica entre os dois, com a beirada esquerda (`meio_borda_px`, que tinha o brilho da costura do canto e a sombra das almofadas dele) vinda da beirada direita, espelhada, para as duas costuras ficarem iguais. Antes (b5d85bc e as versões anteriores) o canto ficava, com as duas almofadas creme, e o braço da esquerda era feito à parte (o encosto da perna com a ponta do braço da direita). O alfa é antisserrilhado, com a cor do estofado até a borda;
  - o sofá antigo sai com a sombra e o halo claro de cima (`buraco`, até x 1538: com 1531, um resto cinza do sofá antigo, logo fora do retângulo, voltava refletido como uma manchinha à direita do braço): o Bege Bahia de fora, refletido no lado mais perto do retângulo (as faixas que ficam à vista são estreitas; nos cantos, os dois lados misturados junto à diagonal, em `canto_px`), com a borda esfumada em `esfuma_px`. Os ladrilhos (`_material_por_ladrilhos`) alisavam as manchas da pedra numa faixa visível;
  - o tamanho: o sofá vai no fundo `fundo_px` (63 px, 1,06 m), na mesma proporção do modelo (240 x 69 px): 219 x 63 px (3,67 x 1,06 m), com o encosto na linha de trás do PDF e centrado no comprimento dele (3,4 m). Histórico: no comprimento do PDF o fundo ficava em 58 px (0,97 m); o usuário pediu "pode aumentar o sofá para ter a mesma altura, preservando a proporcionalidade" (70 px, 1,17 m, o do sofá anterior e do PDF: 4,07 m de comprimento) e depois "diminua um pouco o tamanho" (10% a menos). Esticar só o fundo afinava as almofadas;
  - a sombra (usuário: "jogue um leve efeito de sombra para mostrar que o sofá está integrado ao piso"; antes, "remover a sombra"): a das poltronas (`T.pousar_planta`, deslocada para baixo e para a esquerda, mais a de contato), mais fraca (`sombra` 45%, `sombra_contato` 30%), medida em fração do fundo do sofá. O sofá vai com uma margem em volta (30% do fundo) para o desfoque da sombra não ser cortado na caixa dele (sem ela, a sombra saía como um retângulo de borda dura). O contorno ainda leva a beirada do estofado escurecida em `beirada` (12%) até `beirada_px` para dentro, e a cor ganha `nitidez` (máscara de nitidez de 1 px).
- O sofá e as poltronas do tapete ficam sob a laje do 1º Pavimento: o Térreo nublado não muda. `terreo_para_nublado` já põe o sofá novo numa rodada do zero.
- **Na final do Térreo:** a final de da8fecd → `--sobre-final poltronas_living` → `--sobre-final sofa_varanda` (refeita do mesmo jeito depois da troca do braço e da sombra, e de novo com o braço da esquerda refinado: "consegue refinar mais ainda esse braço da esquerda do sofá?"; "corrija também a parte interna do braço").

### O tracejado da borda de baixo da garagem da Casa E em branco (28/10)

Pedido do usuário, com o recorte da garagem do Térreo: "esse tracejado em branco". A borda de baixo da laje da garagem (`TRACEJADOS_TE["cobertura"]["laje da garagem"]`, o 3º trecho) corre sobre a divisa do granito com a pedra portuguesa do acesso de veículos; a cor de cada traço vem da mediana do fundo em volta, que ali é metade pedra clara, e os traços saíram pretos; entre eles aparecia a linha cinza antiga do retoque.
- **`TRACEJADOS_TE["brancos"]`:** os trechos (pelo nome, `"laje da garagem (3)"`) que vão sempre em branco; `tracejados_pb_te` não troca a cor deles pelo fundo.
- **`tracejado_branco_te`** (etapa `tracejado_branco` do Térreo, logo depois de `tracejados`; sobre a final, `--sobre-final tracejado_branco`): os px da linha que já estava ali (os traços pretos e o cinza embaixo, `vaos["limpa_px"]` de cada lado) ganham o piso do mesmo material ao lado (`_limpa_tracos` com `fonte` = o granito e a pedra portuguesa da chapada naquela caixa, e `mesmo` = o material de cada px, com os px da linha do PDF no material mais perto), e os traços voltam em branco, nos mesmos lugares. Mudam só as linhas 907 a 913 da final, de x 2455 a 3045.

### O rótulo da SUÍTE 1 do 1º Pavimento da Casa E (28/10)

Na revisão do 1º Pavimento ("1º pavimento da casa E"), o único ponto: o rótulo da SUÍTE 1, no ponto do PDF, passava o "m²" sobre a borda do tapete. Com o OK do usuário ("ok"):
- **`AJUSTES_E["1Pavimento"]`:** `("SUÍTE 1", (1192.7, 623.4), (-9, 8.5))` (centro e desvio em px de 2000, como em `retoque_1pav_casae.ROTULOS["ajustes"]`): 17 px para a esquerda e 16 px para baixo na final, no piso livre entre o aparador e o tapete.
- **`rotulos_ajustados_sobre_final(chave, img, nomes)`** (etapa `rotulo_suite1` do 1º Pavimento, `--sobre-final rotulo_suite1`): a final sem os rótulos como estavam (`sem_rotulos`, `novos=False`), os rótulos com os ajustes, e na final só as caixas desses rótulos (a de antes e a nova, com 6 px de folga) mudam.

### A parte de baixo da piscina do Subsolo da Casa E (28/10)

Pedidos do usuário: "na parte de baixo da piscina está invertido: a parede é a parte de baixo e a borda da piscina a parte de cima. entendeu?"; e, vendo a borda de Bege Bahia passada para junto da água (5418bb9): "o subsolo ficou horrivel, deixe apenas parede na parte de baixo sem borda". O PDF tem ali um bloco cheio (preto, com as linhas tracejadas da seção); o render tinha a parede junto à água e uma faixa de Bege Bahia por fora.
- **A parede** (`PISCINA_BORDA_SUB`, `piscina_borda_sub`, etapa `piscina_borda` do Subsolo, antes dos rótulos): na `caixa`, de `topo_y` para baixo, a parede (luz abaixo de `parede_lum`, cinza) e o Bege Bahia (R − B acima de 15), com a emenda antisserrilhada entre eles (fechamento de 5 px), viram parede, no cinza mediano dela. Fica só a borda da esquerda ao lado da água (o px com água a até `lado_px` à direita na mesma linha), até o fundo da água. O bloco fica reto: na parte funda, do lado de fora da borda da esquerda até o degrau; na rasa, até a parede da direita.
- **Na final:** a final do Subsolo de 4e4108d → `python3 final3840_casae.py Subsolo --sobre-final piscina_borda`.

### O vão da porta da circulação para a sala íntima da Casa D (28/10)

Pedido do usuário, com o recorte da porta: "tem uma segunda porta colada na parede em tom cinza que precisa ser removida". No vão, o render deixou a folha fechada (uma faixa clara de ponta a ponta) e a etapa `soleiras` desenhou por cima a soleira de Bege Bahia com as faces cinza (o vão é branco no PDF): ao lado da folha aberta, ela se lia como uma segunda folha, fechada.
- `final3840_casad.vao_sem_soleira_td` (`VAO_SEM_SOLEIRA_TD`), no fim da etapa `soleiras` do Térreo: o vão entre os batentes (`vao_pt`, 1246,6 a 1255,2 x 1509,2 a 1561,4 pt), 2 px mais largo à esquerda (`alarga_px`: a soleira saía 1,2 px à esquerda do vão do PDF, com a face em 1438 e 1439), recebe o vinílico dos dois lados, cada metade espelhada do seu lado e as duas fundidas no meio (as réguas são deitadas). Nas linhas da folha aberta (`folha_y_pt`, com 2 px de folga) só o lado da sala íntima, para a folha não entrar no vão. A folha e os batentes ficam.
- **Na final:** aplicado sobre a final aprovada (`vao_sem_soleira_td(Q, final)`): 672 px mudam, só no vão (x 1438 a 1449, y 1350 a 1405). O Subsolo não muda.

### A revisão da Casa D de 28/10: os 7 itens

Com o OK do usuário ("pode aplicar os 7"), no motor (`final3840_casad.py`) e sobre as finais aprovadas (`aplica7_d`: as funções chamadas direto nas finais, sem rodar o motor de novo):
1. **X do banho master em preto:** `PROJECOES_TRACO_D["pisos"]` passa a (30, 30, 30), força 1,0, na mesma largura (1,48 px); `projecoes_terreo_d(Q, img, so_pisos=True)` redesenha só os dois X sobre a final, por cima do cinza (o mesmo traço cobre o de antes).
2. e 3. **Hall, porta ao lado da adega** (`hall_porta_td`, `HALL_PORTA_TD`, no fim da etapa `projecoes`): o fio pontilhado da folha sai (o travertino de junto, espelhado, de 2267,1 a 2272,6 pt; a face da parede da adega fica); os traços do PDF das duas linhas da laje (ARQ_PAREDE, 1081,0 e 1092,3 pt) de 2267,0 a 2366,3 pt entram em preto nítido (`_tracos_d`, 1,5 px, antialias a 8×); por cima, a folha de vidro (2268,6 a 2270,9 x 987,4 a 1082,9 pt) por `final3840_casaa.portas_vidro`.
4. e 5. **Resto da folha antiga** (`restos_folha_td`, `RESTOS_FOLHA_TD`, na etapa `esquadrias`, depois de `entre_porta_box_td`): nas duas faixas (suíte master; sala íntima → circulação da suíte 2) o piso volta ao da etapa `soleiras` (na final, o `Terreo_soleiras.png` do cache).
6. **WC DCE ↔ DCE 1 do Subsolo** (`VAO_SEM_SOLEIRA_SD`, na etapa `soleiras` do Subsolo): `vao_sem_soleira_td` vale para os dois pavimentos (pela `Q.chave`); o vão inteiro do PDF, 1 px mais largo à direita (a face escura da coluna 930), só do lado do DCE 1 (`so_lado`: o rótulo do WC DCE encosta no vão pela esquerda), e os batentes do PDF (`batentes`) por `portas_vidro` (claros, contorno fino).
7. **Parede tracejada dupla do pátio** (`parede_patio_sd`, `PAREDE_PATIO_SD`, na etapa `hachura`, depois dela): os traços da ARQ_PAREDE dentro de `caixa_q` com as duas pontas fora da pegada dilatada 2 px (396 traços: as duas linhas à esquerda, as duas embaixo até o canto da academia e a de fora no alto), em preto, 1,2 px.

Na final: Térreo, 3351 px mudam (só nos itens 1 a 5); Subsolo, 8746 px (o vão e as linhas do pátio).

### A sombra dos jogos da varanda e as poltronas no modelo da Casa E (Casa D, 28/10)

- `final3840_casad.sombra_jogos_d` (`SOMBRA_JOGOS_D`), no fim de `moveis_td`, depois de `jogos_mesa_d`: o alfa de cada conjunto (`_jogo_q`, a geometria que `jogos_mesa_d` passou a usar: o bloco em 4×, o tampo no diâmetro da mesa do PDF, o giro) deslocado e desfocado em duas sombras, a macia (−0,10 / +0,10 m, σ 0,09 m, 42%) e a de contato (−0,02 / +0,02 m, σ 0,03 m, 35%), somadas (1 − Π(1 − s)) e só fora das peças.
- `final3840_casad.poltronas_modelo_e_d` (`POLTRONAS_E_D`), no fim de `moveis_td`: as 4 peças do PDF (ARQ_LAYOUT HUMANIZAÇÃO) saem com `folga_px` e a sombra antiga (`sombra_px`, para baixo e à esquerda), sem tocar a madeira da mesinha (R − B acima de `madeira_rb`). O buraco é refeito por material: o tapete (dentro do retângulo do PDF, aquém da borda) e o Bege Bahia de fora em ladrilhos de grão com o tom do anel (`final3840_casae._material_por_ladrilhos`, fonte: o material dentro de `tol_lum` da mediana, longe dos buracos e das peças); o travertino do living na mesma linha, `fora_desloc` ao lado (estratos deitados); a borda escura de 1 px do tapete com a cor dos trechos limpos dela. Por cima, a concha da sala íntima do 1º Pavimento da Casa E (`final3840_casae._modelo_poltrona_1p`, `_girar_peca`), no centro e no maior lado da peça, virada para `frente`, com `POLTRONAS_TE["sombra"]` e `["sombra_contato"]` (`retoque_terreo_casae.pousar_planta`).
- **Na final:** as duas funções chamadas direto na final do Térreo (sem rodar o motor de novo); mudam só a varanda (os jogos e as duas poltronas) e o canto esquerdo do estar do living.

### O entorno das poltronas, a trama do tapete da varanda e o contorno das cadeiras do escritório (Casa D, 29/10)

- **Entorno das poltronas (`poltronas_modelo_e_d`):** o tom do material no buraco vem de `_tom_em_escalas` (a média só do material livre, em desfoques crescentes): antes, no miolo do buraco, longe do material livre, `final3840_casae._material_por_ladrilhos` caía no px original e a poltrona antiga ficava por baixo da nova. O Bege Bahia de fora (`"bege": True` no tapete da varanda) é o desenho do piso (`bege_desenho_d`, separado de `bege_limpo_d`: a textura da biblioteca com a semente do piso) na luz do Bege Bahia em volta, também em escalas crescentes. A exclusão da madeira (R − B acima de `madeira_rb`) só vale na caixa da mesinha do living (`madeira_pt`): o Bege Bahia também é quente, e a exclusão comia o contorno da antiga e a borda do tapete. O tapete liso tem a tolerância curta (`tol_lum["tapete"]` 12), sem a sombra da mesinha.
- **Trama do tapete (`tapete_trama_d`, `TAPETE_TRAMA_D`, no fim de `moveis_td`):** o relevo do trecho limpo do tapete do bloco `conjunto_estar_tapete` (o tom dividido pelo desfoque de `sigma_px`), na escala real (`px_m_foto` = 317 px / 3,1 m), tecido por image quilting (os espelhos, sem giros), com `forca` 1,4 e limitado a ±6%, multiplicado só nos px da cor do tapete, dentro do retângulo do PDF recuado 3 px.
- **Contorno das cadeiras do escritório (`cadeiras_mesas_d`, `MOVEIS_TD["cadeira"]["contorno"]`):** no bloco em 4x (`_cadeira_bloco(..., contorno=)`), a cor da beira é a do miolo mais perto (a franja clara do recorte sai), o alfa recua 1 px e fica macio, e a silhueta ganha o aro mais escuro (3 px em 4x, a 74% da cor); o piso em volta vem das réguas da mesma fileira (`fundo` (−36, 0) nas de visita, (28, 0) na da mesa); o traço cinza da beira do tampo (`borda_mesa`) volta por cima delas. `cadeiras_mesas_d(..., nomes=("escritório",))` refaz só essas.
- **Na final:** `poltronas_modelo_e_d` e `tapete_trama_d` sobre a final de 8c2a52b com `sombra_jogos_d`; depois `cadeiras_mesas_d(Q, final, final, nomes=("escritório",))`. Mudam só o tapete da varanda, o canto esquerdo do estar do living e a mesa do escritório.

### Banquetas da ilha, cadeiras das suítes e a trama nos tapetes do living e das suítes (Casa D, 29/10)

- **Banquetas (`banquetas_d`, `BANQUETAS_D`):** com `contorno`, o bloco vem de `_cadeira_bloco(..., contorno=, m=)` (o mesmo 4x limpo das cadeiras do escritório, na largura das banquetas); com `piso` "bege", a caixa de cada uma (fora do tampo) é refeita no desenho do Bege Bahia (`bege_desenho_d`) na luz do Bege Bahia em volta (`_tom_em_escalas`), não na etapa dos pisos, que ainda tem as banquetas do render (o aro cinza em volta das novas).
- **Cadeiras das suítes (`cadeiras_mesas_d`):** `contorno["nomes"]` inclui "suíte master" e "suíte 1"; a da suíte 1 ganhou `fundo` (58, 0) (as réguas à direita); `borda_mesa["nomes"]` só "escritório" (as mesas das suítes não têm traço de borda). `refaz_tampo=False` refaz as cadeiras numa imagem em que o tampo já foi refeito.
- **Tapetes (`tapete_trama_d`, `TAPETE_TRAMA_D["tapetes_pt"]`):** agora (nome, retângulo pt): varanda, living, suíte master, suíte 1, suíte 2 e suíte 3/escritório; fora a varanda, a cor de referência do tapete é a da faixa de `anel_px` junto à borda (a cama cobre o miolo). `nomes=` aplica só nos tapetes pedidos; a semente de cada um é a da posição na lista (a varanda segue igual).
- **Na final:** `banquetas_d` (em `F.em_quadro`), `cadeiras_mesas_d(Q, final, final, nomes=("suíte",), refaz_tampo=False)` e `tapete_trama_d(Q, final, nomes=(living e as 4 suítes))` sobre a final de 9c8a711.
- **Tapete da sala íntima (29/10, usuário: "faltou a textura no tapete da sala intima do terreo da casa D. adicione-a."):** o da ARQ_LOUÇAS E METAIS (1310,1, 1563,4, 1480,2, 1790,2 pt) no fim de `TAPETE_TRAMA_D["tapetes_pt"]` (a semente dos outros não muda), com a cor da faixa junto à borda. Na final: `tapete_trama_d(Q, final, nomes=("sala íntima",))` sobre a final de cf6e28d. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_2910c_tapete_sala_intima_textura_antes_depois.jpg`.

### A porta do Louceiro 2: a soleira e sem a segunda linha (Casa C, 29/10)

- **Soleira (`soleiras_t`, `SOLEIRAS_MAIS_TC`):** o vão da porta do Louceiro 2 (pt, entre os batentes) entra na lista de `B.vaos_brancos` só durante `F.soleiras` (o branco dele emenda no retângulo branco do louceiro, na ARQ_LAYOUT HUMANIZAÇÃO, e a busca dos vãos não o achava); `F._soleira_no_pdf` acha as faces das paredes (2394,3 a 2459,9 px) e a soleira vai como as outras. Vai no fim da lista: as sementes das 19 de antes não mudam.
- **Segunda linha (`restos_folha_tc`, `RESTOS_FOLHA_TC`, no fim da etapa das esquadrias):** o espelho de `F.esquadrias_terreo` copiava a coluna de antialias da parede da direita (cinza 140, em 2464) para 2461, no meio da faixa entre a folha e a parede; e na linha 881 ficava a ponta da folha antiga do render. Nas duas faixas (pt), o travertino das mesmas linhas, `desloca_px` (−12) à esquerda.
- **Na final:** o motor do Térreo de `soleiras` em diante, sem salvar (`final_3840_c("Terreo", salvar=False, de="soleiras")`); as etapas novas só mudam em volta da porta (2390–2468, 807–886 px), e esse trecho (2382–2476, 798–895) foi colado na final, que tem os pós-processos da piscina fora do motor.

### A revisão de 29/10 aplicada (Casa C, Térreo)

- **Claraboias (`claraboias_t`, `CLARABOIAS_T`):** `fundo` por retângulo ("claro" ou "madeira") e `tracos` com a cor e a força de cada um: preto (30) a 0,95 nos pisos claros, branco (234) a 0,92 na madeira; antes, cinza 78 em todas.
- **Trilho do hall (`trilho_hall_tc`, `TRILHO_HALL_TC`, na etapa das cortinas):** na faixa `pt` (2386–2393 x 1199–1454 px), volta a imagem de antes de `cortinas_t`: o trilho da cortina de pé do vidro do jardim (2389,8 pt) que `F.cortinas` levava até a parede de cima, pelo hall.
- **Portas (`restos_folha_tc`, `RESTOS_FOLHA_TC`, no fim das esquadrias):** `rets` agora com o deslocamento de cada faixa, (dx, dy) px; mais as do Louceiro 1 (o traço na ponta da folha, a linha fraca em 2278, os pontos sob as orelhas dos batentes, as frestas entre batente e parede com a soleira ao lado, a faixa escura do render nas linhas 631–632 sob as paredes), do Quarto 2 (as colunas 1684–1686, a borda do armário espelhada) e do BH master 1 (a pinta em 887–888 e o fim da folha antiga do closet em 904–909); `colunas` (x, linhas, linhas de referência): a beira da folha no tom mediano dela mais acima; `batentes` (pt): os dois do Louceiro 1, com as orelhas, por `final3840_casaa.portas_vidro`.
- **Cadeiras (`cadeiras_contorno_tc`, `CADEIRAS_CONTORNO_TC`, na etapa das cadeiras, depois de `cadeiras_mesas_t`):** as peças da ARQ_LAYOUT HUMANIZAÇÃO dentro da caixa de cada cadeira, em 4x: os preenchimentos dão a silhueta e os traços, as costuras (só as de dentro, a mais de `aro_px4` da beira). O estofado vem do miolo mais perto (`distance_transform_edt`), sem os px dos traços velhos (os do PDF, 1 px mais largos); a beira a `aro_tom` 0,58 e as costuras a 0,70; o piso por `cv2.inpaint` só nos px dos traços velhos fora da silhueta. O tampo da mesa, com 1 px de borda, não muda.
- **Na final:** o motor do Térreo de `cadeiras` em diante, sem salvar; as etapas novas mudam 14 trechos (as 5 claraboias, as 3 cadeiras, as portas e o trilho), conferidos iguais ao cache antigo na final antes de colar.

### Os brises de bronze nas portas das suítes (Casa C, 29/10)

- **`brises_suites_tc` (`BRISES_SUITES_TC`, no fim da etapa das esquadrias, depois de `restos_folha_tc`):** as folhas do plano de fora das portas de correr dos Quartos 1, 2 e 3 e da Suíte Master (`folhas_pt`, por suíte: no PDF, cada folha são duas tiras brancas de 1,4 pt da ARQ_PAREDE, coladas). Cada uma em 8x: a sombra curta (`retoque_1pav_casae.sombra`), o bronze (74, 106, 139) com o escovado (ruído desfocado 6 px no comprido e 0,3 px na espessura, a 7%), o brilho no meio (0,4 px) e o contorno escuro (0,35 px), `folga_px` 0,3 além da folha, por cima do vidro das esquadrias. As do plano de dentro ficam em vidro.
- **Na final:** o motor do Térreo de `esquadrias` em diante, sem salvar; 4 trechos (as 3 portas de cima e a da Suíte Master) colados na final, conferidos iguais ao cache antigo.

### O traço entre a cortina e o vidro (Casa C, 29/10)

- **`RESTOS_FOLHA_TC`:** mais duas faixas, sob a folha de vidro da direita das portas dos Quartos 3 (1341–1427 x 335–340 px) e 2 (1533–1618 x 335–340), entre ela e a face da parede do quarto (549,3 pt): o caixilho claro do render (174–195), que a limpeza das esquadrias deixava. Vem a madeira 7 px abaixo (`(0, 7)`, o passo das réguas, com as juntas no lugar). Os montantes das pontas (1428–1433 e 1619–1624) ficam.
- **Na final:** o motor de `esquadrias` em diante, sem salvar; os 2 trechos (e 1 px junto à parede entre os quartos, que a etapa das cortinas mudou em 21) colados na final.

### As cadeiras da varanda gourmet (Casa C, 29/10)

- **`jogos_varanda_tc` (`JOGOS_VARANDA_TC`, na etapa dos móveis, depois de `moveis_tc`):** nas duas mesas redondas da varanda gourmet (`mesas_pt`, as da ARQ_MOBILIÁRIO), as 6 cadeiras do PDF (ARQ_LAYOUT HUMANIZAÇÃO, 28–40 pt, a menos de 80 pt do centro da mesa) dão lugar às do bloco `mesa_redonda_6_couro`, com os parâmetros e os tons do conjunto da varanda da Casa D (`final3840_casad.MOVEIS_TD["conjunto_varanda"]`, `tons_varanda_d`) e sem o tampo do bloco (tirado a `tampo_folga_px` além do raio dele): a mesa de madeira do render fica. A beira das cadeiras vem na cor do couro de dentro (`miolo_px`, pelo `distance_transform_edt`), sem a franja clara do recorte da foto. Pousadas por `D._jogo_q` e `D._pousar` no centro da mesa do PDF, nos `giros` 0 e 180.
- **O piso:** na caixa de cada cadeira antiga (`folga_px`: esquerda, cima, direita, baixo), o travertino da mesma fileira deslocado na horizontal: o menor |dx| em `busca_px` com a fonte livre das peças do PDF (dilatadas `livre_px`) e de bordas em pé da imagem (Sobel x acima de `borda_sx`; o travertino só tem estratos deitados, e assim a esquadria da varanda à direita não é copiada), com a passagem `suave_px` e fora do tampo.
- **A sombra:** a de `D.SOMBRA_JOGOS_D` (a macia e a de contato), só no piso, fora das cadeiras e do tampo.
- **Na final:** o motor de `moveis` em diante, sem salvar; os 2 trechos das mesas colados na final, conferidos iguais ao cache antigo.

### A revisão de 29/10 da Casa B: `revisao_casab_2910.py`

A final do Térreo da Casa B não sai mais só do motor (`final3840_casab.final_3840`): depois dele vieram as cortinas franzidas (`cortinas_franzidas.py`) e os acertos da piscina. Os 8 itens da revisão (OK do usuário: "aprovados os itens"; no item 2, "desenhe as folhas como na casa C, aplicando o mesmo padrão") entram como retoques locais sobre a final, rodados uma vez sobre a final de 175b56e (`python3 revisao_casab_2910.py [--antes png] [--saida png]`; o padrão lê e grava a final), com as funções da Casa C, que passam a receber a configuração de cada casa (para a Casa C, o resultado é o mesmo: as etapas `cadeiras` e `moveis` conferidas iguais ao cache):

- **`final3840_casac`:** `jogos_varanda_tc(Q, img, q=None)` (`q["camada"]`: a camada das cadeiras do PDF, a ARQ_LAYOUT HUMANIZAÇÃO na Casa C); `brises_suites_tc(Q, img, q=None)`; `cadeiras_contorno_tc(Q, img, pares=None, camadas=("ARQ_LAYOUT HUMANIZAÇÃO",))`.
- **Item 1 (`JOGOS_VARANDA_TB`):** as mesas da varanda gourmet da Casa B (ARQ_MOBILIÁRIO, 102 pt = 1,80 m) e as cadeiras do PDF na ARQ_MOBILIÁRIO; o conjunto entra na escala da mesa.
- **Item 2 (`BRISES_SUITES_TB`):** as folhas do plano de fora (pt) das suítes 1 e 2 (fachada de cima, 2 por plano), da suíte 3 (lateral direita, 2) e da suíte master (lateral esquerda, 3, em degrau). A sala íntima fica em vidro.
- **Itens 3 a 6 (`FOLHAS_LINHAS_TB`, `folhas_linhas_tb`):** em px da final, cada faixa com o deslocamento de onde vem o piso: banho 1 (1929–1932 x 478–527, o contorno fino de 4 px entre a folha e a parede; o travertino 12 px à esquerda), banho 3 (2535–2577 x 843–846; as 4 linhas de baixo: à direita, junto à parede, há uma peça clara), BH motorista (o fio de 1 px em x 2965; o de 2968 é a face da parede e fica), banho master (1507–1550 x 515–517, a cópia do vidro do box; a madeira 50 px à esquerda).
- **Item 7 (`CADEIRAS_MESAS_TB`):** cadeira e mesa (pt) da suíte 1, da suíte 2 e da suíte master (esta na ARQ_MOBILIÁRIO).
- **Item 8 (`ROTULOS_JARDINS_TB`, `rotulos_jardins_tb`):** nas caixas dos dois jardins, o fundo sem os rótulos vem da etapa `seta` do cache do motor (26/10; igual à final nos jardins, conferido) e o tracejado embaixo do texto (`folga_px` 4) volta à etapa `escadas`; o traço que encosta no texto sai inteiro (o miolo dele, diferença acima de `forte` 60, até `traco_max_px` 120, com 1 px de halo; os do X do jardim de inverno se cruzam e não saem juntos). O JARDIM deixa os `livres` e passa a rótulo `fixo`, em branco, no `pt` (o meio do jardim, entre as plantas e os tracejados); os rótulos são escritos de novo por `final3840_casab.rotulos`, e só as caixas dos jardins vão para a final.

- **Depois da revisão: só as 4 folhas (`VAOS_SUITES_TB`, `vaos_suites_tb`, antes de `brises_suites_tc`):** por trecho de cada porta (pt: a folha de fora e a de dentro; `eixo`, `lado` do quarto), a faixa das duas folhas e do vão é refeita com a cor da madeira do quarto em cada linha das réguas (os primeiros `amostra_px` px de madeira a até `busca_px` para dentro, pulando a cortina; `_madeira`: R − B > 35 e o tom entre 100 e 165), alisada no comprido quando a faixa corre com as réguas (`liso_px`), a folha de dentro em vidro fino (miolo `vidro`, borda `borda` de `larg_borda_px`) e, na sala íntima, a de fora também; o bronze vem depois. A final foi refeita do zero a partir da de 175b56e (`--antes`), com a revisão inteira.
- **As garrafas da adega (`ajustes_casab.adega_b`, `--adega`):** em metros (`garrafa_m`, as da Casa C), por nicho e no trecho depois deles; `sombra_fora=False` refaz só a prateleira, sem a sombra dela no piso, que a final já tem.
- **Os pedidos depois da revisão (`pedidos_tb`, `--pedidos`, uma vez sobre a final de d83aee4):**
  - **Tapetes (`TAPETES_TB`):** `final3840_casad.tapete_trama_d(Q, img, nomes=None, q=None)` recebe agora a configuração (`miolo`: os tapetes cuja cor é a mediana de todo o miolo; a Casa D, só a varanda, como antes); na Casa B, os 7 tapetes do PDF, com `miolo` nos estares da varanda e do living.
  - **Madeira (`MADEIRA_TB`, `TONS_TB`; `_veio_tb`, `_relevo_tb`, `_pintar_tb`, `_sombra_piso_tb`):** o veio desenhado (ruído alongado no sentido das fibras, em metros: `veio_m` ao longo, `fio_m` através, e as faixas largas), girado no ângulo da peça; o chanfro (a quina virada para o alto à direita mais clara), o aro fino; a máscara do PDF em ss 8, levada ao quadro em área; a sombra macia e a de contato de `D.SOMBRA_JOGOS_D`, fora da peça.
  - **Mesa do hall (`MESA_HALL_TB`, `mesa_hall_tb`):** o tampo (ARQ_MOBILIÁRIO) e as linhas dele (ARQ_MOBILIÁRIO e ARQ_LAYOUT HUMANIZAÇÃO) em ss; as partes entre as linhas (componentes conexos) até `centro_r` do raio e além de `aro_r` em nogueira, as do meio (os painéis) em castanho com o veio na tangente do centro de cada uma; as linhas e as lascas tomam a madeira vizinha (EDT) e viram friso.
  - **Tampos (`TAMPOS_TB`, `tampos_tb`):** a mesa de jantar (nogueira) e as duas mesas redondas da varanda (marrom): a luz de cada px sobre a mediana do tampo, na potência `gama`, no tom novo, dentro do preenchimento do PDF recuado `recuo_px`.
  - **Cadeiras do jantar (`JANTAR_TB`):** `final3840_casad.jantar_d(Q, img, piso, q=None)` com as opções novas (sem elas, a Casa D como antes): `lado_norm` (o lado de cada cadeira pela posição relativa à mesa, para a oval), `passos` (até quantas cadeiras adiante procurar o travertino limpo na mesma linha), `mesa_pdf` (o tampo que cobre as cadeiras é a forma do PDF, não a caixa) e `linho["absoluto"]` (o estofado no `tom` na luz da foto). O `piso` é a própria final (a etapa dos pisos do cache ainda tem as cadeiras do render).
  - **Máquinas (`INOX_TB`, `maquinas_inox_tb`):** dos dois quadrados da ARQ_LAYOUT HUMANIZAÇÃO sob a bancada, só a ponta até a borda da bancada (`bancada_x_pt`), em inox escovado (de trás para a frente), com o painel da porta (`frente_pt`); a bancada fica por cima do resto.
  - **Soleiras (`SOLEIRAS_TB`, `soleiras_tb`):** a janela da pia da cozinha e a porta de correr da área de serviço para a área descoberta, por `final3840_casaa.portas_vidro` com `PORTAS_VIDRO` trocado por um momento (`portas`: a soleira de Bege Bahia, os batentes e as folhas em pt, cada uma no plano dela); antes, as linhas do tubo da folha antiga que passam do vão (`limpa_px`) recebem o granito em espelho, de cima ou de baixo. Substitui a `janela_pia_tb` (o granito no lugar do caixilho antigo, que a soleira agora cobre).
  - **Sofá do living (`SOFA_LIVING_TB`, `sofa_living_tb`):** logo depois dos tapetes, nas três peças do PDF (ARQ_MOBILIÁRIO): o sofá de antes da trama (`antes`, a imagem da entrada de `pedidos_tb`), no `tom` (cada px sobre a mediana do sofá) e com a trama do tapete (a mesma geração de `D.tapete_trama_d`, com `TAPETES_TB`), em alfa antisserrilhado.
  - **Ilha gourmet (`LINHA_ILHA_TB`, `linha_ilha_tb`):** as linhas da tira do PDF (px 1301–1547 x 1339–1343) recebem o granito de logo acima, em espelho.
  - **Espreguiçadeiras (`ESPREGUICADEIRAS_TB`, `espreguicadeiras_tb`):** em cada peça (ARQ_LAYOUT HUMANIZAÇÃO), a zona de `zona_px` em volta tecida de novo (`texturas.quilting` da água limpa de `fonte_px`, no tom da água de fora da zona); a sombra deslocada e desfocada com a `tinta` por canal (mais no vermelho); o corpo submerso (a peça dilatada `corpo_px`, alfa `corpo["alfa"]`); a linha d'água (o anel de `linha["larg_px"]`, quebrado por ruído largo); o tampo em ss 8 (volume pela distância à borda, o encosto do lado de `encosto` depois de `vinco_x_pt` a `encosto_tom`, o vinco e o aro).
  - **Peças de madeira (`PECAS_MADEIRA_TB`, `pecas_madeira_tb`):** criado-mudo do motorista (freijó), criados-mudos da suíte master (ocre, `TONS_TB["ocre"]`) e mesas de apoio dos recamiers (freijó, `sobre`: só a sombra curta, estão sobre o assento; `vaos`: o vão da alça na sombra); os traços do PDF de dentro da peça viram friso (`FRISO_TB`).
  - **Recamiers (`RECAMIERS_TB`, `recamiers_tb`):** as peças da ARQ_LOUÇAS E METAIS de cada caixa num `D.estofado_d` (linho off-white, volume, trama, vincos), com a sombra no piso antes.
  - **Poltronas da varanda (`POLTRONAS_VARANDA_TB`, `poltronas_varanda_tb`):** a concha da Casa E (`final3840_casae._modelo_poltrona_1p`, `_girar_peca`, `retoque_terreo_casae.pousar_planta` com `POLTRONAS_TE["sombra"]` e `["sombra_contato"]`), como `D.poltronas_modelo_e_d`, nas duas peças da ARQ_MOBILIÁRIO (`frente`: para a mesa de centro). O buraco da antiga é refeito linha a linha: no tapete (até a 1ª coluna da borda escura, `borda_px` colunas), o trecho da mesma linha à esquerda todo livre (sem as peças do PDF de menos de `objetos_m2`, dilatadas `perto_px`), ou, sem ele, o trecho livre mais perto em vai e vem (`recurso_px`); fora, o da mesma linha à direita no travertino da legenda; a borda, da linha limpa mais perto na mesma coluna.
  - **Poltrona redonda (`POLTRONA_REDONDA_TB`, `poltrona_redonda_tb`):** `D.estofado_d` na peça da ARQ_MOBILIÁRIO, com os traços como costuras e vincos.
  - **Encostos do living (`ENCOSTOS_LIVING_TB`, `encostos_living_tb`):** em ss 8, a peça menos os traços dela em partes conexas; o encosto são as partes com o centro a menos de `encosto_x` da largura (do lado das costas) e as tiras finas da casca (até `casca_px` x 2); o bordô (`tom`) na luz de cada px sobre a mediana do encosto; os traços só entre partes do encosto entram no tom.
  - **Floreiras (`FLOREIRAS_TB`):** `final3840_casad.floreiras_td(Q, img, q=None)` recebe a configuração; com `passo_m`, uma planta a cada `passo_m` do caixote (a Casa D, `n` 18 em cada, como antes). Os miolos (pt) são os retângulos brancos dentro das paredes da fachada de cima.
  - **Cama da suíte master (`CAMA_MASTER_TB`):** `final3840_casab.cama_master(Q, img, q=None)` com as opções novas (sem elas, o motor como antes): `so_cama` (só a cama volta, no contorno dela, sobre a final: o banco e a sombra de fora ficam), `acolchoado` (o relevo de cada losango do matelassê, também no rolo) e `rolo_vol` (o volume do rolo: largura em m e força).
  - **Folhas de bronze da sala íntima (`BRISES_SALA_INTIMA_TB`):** `Cc.brises_suites_tc` com as duas folhas de fora da porta da sala íntima em brise de bronze, por cima do vidro de fora.
  - **Estofados (`estofados_pdf_tb(Q, img, q, onde)`; `SALA_INTIMA_TB`, `ESTOFADOS_SUITES_TB`):** cada peça (nome, retângulos dos preenchimentos do PDF, opções) num `D.estofado_d` (linho, volume, trama), com a sombra no piso antes (`_sombra_piso_tb`); os traços da camada dentro da caixa da peça, só os desenhados depois do preenchimento dela (`seqno` maior: a linha de x = 1593,6 pt fica sob o sofá da sala íntima no PDF), a partir de `costura_min_pt` como costuras e de `vinco_min_pt` (por peça, `{"vinco_min_pt": 0.0}` na poltrona de concha, cujo arco vem em segmentos de 1 a 3 pt) como vincos. `sala_intima_tb` = os estofados da sala íntima (sofá em L, poltrona, pufe) e as três mesas por `pecas_madeira_tb` (`tom: "atual"`: a mediana da peça; `veio_graus`); as suítes, o sofá aos pés da cama da suíte 1 e os dois bancos aos pés das camas de solteiro da suíte 2.
  - **Encostos do living, estofados (`ENCOSTOS_LIVING_TB["linho"]`):** com `linho`, a peça inteira passa por `D.estofado_d` duas vezes (no linho e no bordô, com as costuras a partir de `costura_min_pt`) e as duas se juntam pela máscara do encosto; sem `linho`, só o encosto em bordô, como antes.
  - **Piso sob a cortina (`PISO_CORTINA_TB`, `piso_cortina_tb`):** na caixa (px 2627-2641 x 800-819, junto ao criado-mudo da suíte 3), o vinílico de cada linha vem da faixa limpa da mesma linha (`fonte_x`), as linhas retas (`linhas_x`: o contorno do tapete e o trilho) da linha de cima, e o pano é pousado de novo (`blocos.cortina` + `retoque_terreo_casae.pousar_cortina` em `F.em_quadro`, o trecho de `F.B.trechos_cortina_b` mais perto de `trecho`).
  - **Marcenaria (`MARCENARIA_TB`, `marcenaria_tb`):** cada peça como lista de braços (retângulos em pt): a marcenaria areia (`ADEGA_B["madeira"]`) com o veio no comprido de cada braço, o contorno fino só por fora da união (o anel da máscara em ss) e sem sombra: o armário ao lado dos refrigeradores e os armários em L do louceiro e da despensa.
  - **Sombra dos blocos (`SOMBRA_BLOCOS_TB`, `sombra_blocos_tb`):** os blocos de `F.BLOCOS_F` na ordem do PDF; para cada um, a sombra de contato (a máscara crescida `cresce_m` e esfumada `sig_m`, força `forca`) menos a sombra curta que `F.degraus_blocos` já deu, só sobre os blocos pintados antes e fora dos de depois; um fator só, multiplicado na final.
  - **Ordem dos blocos (`ORDEM_BLOCOS_TB`, `_blocos_tb`, `ordem_blocos_tb`):** `sobre`, os pares (a de cima, a de baixo) pedidos, em pt; a ordem de pintura é a ordenação que respeita esses pares e a ordem do PDF nos blocos que se sobrepõem (mais de `sobrepoe_px` px em ss), com o empate pela ordem do PDF (hoje `[3, 5, 0, 2, 4, 1, 6]`). Os blocos são refeitos como em `F.degraus_blocos` (textura, tom e sombra curta de cada um), na ordem do PDF e na nova, e a final recebe a razão entre as duas nos px que mudam; `sombra_blocos_tb` usa a mesma ordem.
  - **Elevador (`ELEVADOR_TB`, `elevador_tb`):** `final3840_casaa.elevador` com o desenho do PDF do Térreo (INS_INSTALAÇÕES HIDRÁULICAS): `externo`, `interno`, `vao` e as 4 `folhas` da porta embaixo, a `soleira` no vão da parede de baixo, o `anel` entre as paredes do PDF, `corrimaos` à esquerda, em cima e à direita, `faces_soleira` "v".
  - **Rótulos (`ROTULOS_CENTRO_TB`, `rotulos_centro_tb`):** a rodada de 26/10 refeita sobre `Terreo_seta` (com um espião em `R1.rotulos_ambientes`) dá a etapa `Terreo_rotulos` sem 1 px de diferença (`assert`), e cada rótulo antigo é desenhado sozinho para ter a máscara dele; o texto antigo sai com o fundo de `Terreo_seta` nos px em que a final está entre o texto e esse fundo (`entre`, `tol`). A busca parte do centro do piso livre do recinto (`F.ambientes_rotulos(todas=True)`, menos os obstáculos do PDF e os `carros_pt`); se o recinto passa de `vazou` vezes a área escrita no rótulo (ambiente aberto para o terreno), do ponto do PDF; `pontos_px` fixa o da garagem. Depois `F.rotulos` só com os que se movem, os carros e as caixas dos que ficam (`manter`) em `obstaculos_pt`, e os pontos de partida por (nome, x, y do PDF), que separam os dois BANHO GOURMET.
  - **Opções por rótulo (`ROTULOS_CENTRO_TB["opcoes"]`):** entram como um ajuste à mão a mais (no ponto do PDF), o último do rótulo: o QUARTO MOTORISTA em duas linhas.
  - **Matelassê (`MATELASSE_TB`, `matelasse_camas_tb`):** em cada cama de `ajustes_casab.CAMAS_B` fora a master, o fator do matelassê de `F.cama_master` (o pesponto em losangos de `passo_m`, na grade do PDF, e o relevo `acolchoado` de `CAMA_MASTER_TB`) multiplicado no edredom: da dobra do lençol aos pés, menos a manta (as medidas de `elementos.ROUPA_CAMA` do tipo, com `folga_m`), dentro do colchão, em ss.
- **O tracejado junto às folhas do living (`TRACEJADO_LIVING_TB`, `tracejado_living_tb`, item 27, `--tracejado`, uma vez sobre a final de f14d295):** em cada faixa (caixa em px da final, `desloc`, `limiar`), os px com o cinza abaixo do limiar recebem o travertino da mesma linha, `desloc` px à direita: o tracejado preto (px 1561-1563, da 1ª junção ao pilar de baixo; o lado esquerdo do retângulo tracejado da ARQ_BANCADAS, x = 1362,6 pt) e, na 4ª folha, a faixa acinzentada com o segundo tracejado (px 1557-1560, inteira). As junções 1 (px 893-897) e 3 (1123-1125) ficam fora das linhas. Depois, com o OK do usuário ("pode tirar o outro tracejado da casa B também"), o lado direito do retângulo (x = 1396,6 pt, px 1597-1599, de 778 a 1243, a faixa inteira, com o travertino 4 px à direita). Refeito sobre a final de f14d295 ou sobre a de 15174e3, dá a mesma imagem. Antes e depois (os dois lados, contra f14d295): `..._2910b_tracejado_folhas_living_antes_depois.jpg`.

### O Subsolo da Casa B antes do OK: `subsolo_casab_2910.py` (29/10)

Pedido do usuário, vendo o Subsolo antes do OK da Casa B: "preciso que represente nevoado as partes que constam no pdf, correspondente fora do subsolo. o resto do terreno permanece hachurado." Rodado uma vez sobre a final de f6ea4b6 (`python3 subsolo_casab_2910.py [--antes png] [--terreo png] [--saida png]`; o padrão lê e grava a final do Subsolo e lê a final do Térreo):

- **As peças (`NEVOADO_SB["pecas_pt"]`):** os preenchimentos do PDF do Subsolo fora do subsolo, pelo rect em pt: a pedra grande e as 6 lajes (ARQ_CONTRAPISO, o bege a 50%), o deck em L abaixo da ducha (ARQ_CONTRAPISO) e os 8 degraus da escada que desce ao deck (ARQ_ESCADAS E RAMPAS). A máscara é a do contorno delas (`final3840_casad._mascara_pdf`, em `ss`), menos as peças do Subsolo que encostam nelas (`ficam_pt`: os 5 degraus da escada da ducha, que avançam 1,7 pt sobre a pedra grande, e o deck da ducha).
- **O Térreo:** os dois PDFs têm as mesmas coordenadas e os dois quadros, o mesmo enquadramento, então o px do Térreo final cai no mesmo lugar. As letras D das escadas saem antes (`_sem_letras`: as manchas de px escuros e neutros do tamanho de uma letra, com folga, por inpaint), e o trecho vai ao nublado do 1º Pavimento (`entorno_esmaecido.NUBLADO`: desfoque de 1,2 px a 3840, 80% da saturação, 70% de branco).
- **Conferência:** só mudam os px dentro das peças (px 299–1093 x 597–1093 do quadro); a hachura, a escada e o deck da ducha ficam iguais. A prancha do Térreo sai igual.
- **A conferência (`--revisao`, uma vez sobre a final de 2cad7fa; OK do usuário: "altere"):**
  - **Rótulos (`ROTULOS_CENTRO_SB`, `rotulos_centro_sb`):** como `revisao_casab_2910.rotulos_centro_tb`, no Subsolo: a rodada de 26/10 refeita sobre a etapa `Subsolo_hachura` (com o espião em `R1.rotulos_ambientes`) dá a etapa `Subsolo_rotulos` sem 1 px de diferença (é a final de f6ea4b6). Os de `mover` (DEPÓSITO, ACADEMIA e SAUNA) saem (o fundo sem rótulos, só onde a final ainda é a etapa) e voltam do meio do piso livre do recinto (`F.ambientes_rotulos(..., todas=True)` menos as camadas de obstáculo e `obstaculos_pt`, o banco da sauna, que está na ARQ_CONTRAPISO); os outros 8 ficam e entram como obstáculo. DEPÓSITO (1758, 394) → (1699, 409) px, ACADEMIA (1527, 569) → (1560, 626), SAUNA (1059, 680) → (1056, 657).
  - **Armário da academia (`MARCENARIA_SB`):** `revisao_casab_2910.marcenaria_tb(Q, img, q=None)` recebe agora a configuração (sem ela, a do Térreo, como antes); a peça é o retângulo da ARQ_LAYOUT HUMANIZAÇÃO junto ao shaft (1481,7–1515,7 x 731,3–844,7 pt), na marcenaria areia do armário da cozinha do Térreo, com o veio no comprido e o contorno fino, sem sombra.
  - **Conferência:** só mudam os 3 rótulos (onde estavam e onde ficaram) e o armário. A prancha do Térreo sai igual.
- **Os pedidos vendo o Subsolo (`--pedidos`, `pedidos_sb`, uma vez sobre a final de 29ce96b):**
  - **Porta do BH sauna (`LINHA_PORTA_BHS_SB`):** o traço de uma folha antiga da base entre a folha aberta e a face da parede (px 1250–1297 x 607–612; já vinha das etapas do motor) recebe o travertino de `dy` px abaixo (os estratos são deitados).
  - **Parede do depósito (`PAREDE_DEPOSITO_SB`):** sobre a folha aberta, as linhas 325–329 copiadas da coluna `modelo_x` da parede ao lado (a face reta, com o fio escuro); embaixo do vão, o começo da parede de baixo (`pe_px`) com a linha `pe_modelo_y` dela.
  - **Soleira do depósito e vidro da sauna (`SOLEIRA_DEPOSITO_SB`, `VIDRO_SAUNA_SB`, `portas_vidro_sb`):** `final3840_casaa.portas_vidro` com `PORTAS_VIDRO["portas"]` trocado por um momento, como `revisao_casab_2910.soleiras_tb`: a soleira de Bege Bahia com as faces (R13) e os 6 batentes do PDF; o vidro fixo em L no padrão do da Casa A (o vão dos dois braços em Bege Bahia sem as faces, as duas folhas com o caixilho e a linha do meio, os 3 montantes).
  - **Canto do vidro da sauna (`ARCO_VAO_SAUNA_SB`, `arco_vao_sauna_sb`; depois: "remova esse \"arco\" no piso"):** o traço escuro da base em L, de canto redondo, no canto de fora do vão (o topo do vão, y 596 px, e a borda do deck, x 954 px, até 606), sai por inpaint (o Bege Bahia da garagem e do vão, a madeira do deck); rodado dentro de `pedidos_sb`, depois do vidro.
  - **Bancos da sauna (`BANCOS_SAUNA_SB`, `bancos_sauna_sb`):** a mesma textura de `F.bancos_sauna` (o travertino bruto, a semente de `SAUNA_F`), com `nivel` (piso, frente, trás), a sombra de contato de cada banco no de baixo (`sombra`, exponencial em `larg_m`; no piso só ela, entre as bordas dos bancos), o espelho a `espelho`, o fio do pé (`pe`) e o brilho da quina (`quina`); as paredes (px abaixo de `parede_max`) não mudam.
  - **Elevador (`elevador_sb`):** `final3840_casaa.elevador` com `revisao_casab_2910.ELEVADOR_TB` (a caixa e a porta do PDF do Subsolo estão nas mesmas coordenadas da do Térreo); depois, `rotulos_centro_sb` só com o ELEVADOR (o texto antigo já ficou sob a cabine nova): o rótulo vai ao meio da cabine, no corpo da regra e em preto.
  - **Conferência:** só mudam os 4 trechos (a porta do BH sauna, a porta do depósito, a sauna, o elevador). A prancha do Térreo sai igual.

### O book de entrega: `book_entrega.py` (29/10)

- **Áreas das Casas D e E (01/11/26):** as do usuário (D: Subsolo 185,09 m², Térreo 868,53 m²; E: Subsolo 217,68 m², Térreo 490,15 m², 1º Pavimento 375,69 m²), com o Total (a soma), em `CASAS` e na chave `entrega.areas` das configs das duas casas; as pranchas saem de `rodape_entrega.py` como antes (só o quadro do rodapé muda).

Modelo 2 (editorial), escolhido pelo usuário ("modelo 2"). Junta as 12 plantas aprovadas das Casas A–E num PDF A3 deitado: `POE642_Book/POE642_Book_Plantas_Humanizadas.pdf`, mais a prévia `POE642_Book_previa.jpg`.

As páginas são desenhadas em PIL a 200 dpi (3307 × 2339 px). O desenho é feito em unidades de uma página de 1600 px e convertido por `z()`. O PDF é montado com pymupdf; cada página entra como JPEG em memória.

- **Fonte das plantas:** `planta(c, pav)` lê a prancha de entrega e pega as 2160 linhas de cima, a final sem o rodapé. Nada é redesenhado.
- **Enquadramento (`caixa_planta(c, pav)`):**
  - Térreo e 1º Pavimento: a caixa de tudo o que não é branco (`min < 235`), somada nos dois e com 20 px de folga. A mesma caixa nas duas páginas, como as coordenadas das pranchas.
  - Subsolo: as manchas cheias (`min < 250`, abertura 9 × 9, componentes acima de 2000 px; a hachura e as linhas finas somem) com 120 px de folga. Assim as peças nevoadas do Térreo entram inteiras, como na Casa B.
  - Sumário: `caixa_cor` usa só o que tem cor (saturação acima de 22), sem a faixa branca até a linha do lote.
- **Recortes ampliados:**
  - `CAPA`, `ABERTURA` (um por casa) e `DETALHES` (dois por casa) guardam o pavimento, a caixa em px e a legenda.
  - As legendas foram conferidas com os nomes à vista no recorte.
  - `cobrir` preenche o quadro cortando o excesso; `caber` encaixa com fundo.
- **Textos:**
  - `CASAS[c]["texto"]` lista o programa pelos nomes dos ambientes dos PDFs do cliente, sem número de vagas nem posição; é provisório.
  - `quebrar` faz a quebra pela largura.
  - Áreas como nas pranchas: sem dado, "não informado" e sem total.
- **Marca e fonte (29/10, pedido do usuário: "quero o logotipo oficial e a fonte Poppins do site deles em vez da Inter"):**
  - `F(peso, t)` carrega a Poppins (`assets/fontes/Poppins-*.ttf`, OFL, com `LICENCA_Poppins_OFL.txt`).
  - `logo_po(altura)` devolve o `logo_paulo_octavio.png` do rodapé das pranchas sem alteração. O fundo claro dos cantos, ou seja as manchas claras que tocam a borda, fica transparente, com a franja suave pela claridade.
  - O logotipo vai na capa (embaixo à direita) e na contracapa (em cima à direita; a New Air fica embaixo à direita).
- **Uso:** `python3 book_entrega.py` grava o PDF e a prévia. Com `--paginas`, grava também cada página em JPG em `POE642_Book/paginas` (no `.gitignore` da pasta).

### A revisão de 29/10 da Casa A: `revisao_casaa_2910.py`

Retoques locais sobre as finais aprovadas, como o `revisao_casab_2910.py` da Casa B.
- **Portas das suítes do 1º Pavimento (`--portas`, sobre a final aprovada de antes das portas).** Pedidos do usuário: "note que é o mesmo caso da casa B: 4 folhas na varanda, sendo duas de vidro e duas de bronze", "e que cobrem o banho master: as de bronze" e "e atenção ao piso entre as folhas de vidro e de bronze".
  - **As folhas (`VAOS_SUITES_TA`, `BRISES_SUITES_TA`):** em pt do PDF, cada uma são duas tiras brancas de 1,4 pt da ARQ_PAREDE. São pares (de fora, de dentro) por trecho, nas suítes 3, 2 e master (varanda à esquerda, `lado` +1) e 1 (varanda à direita, -1). Mais as 2 folhas de fora na frente do banho master, só em bronze.
  - **O piso entre as folhas (`piso_entre_folhas_ta`, `PISO_ENTRE_FOLHAS_TA`):**
    - Abrange a faixa da face de fora do bronze à de dentro do vidro, mais `folga_dentro_px` para o quarto, que leva os nós dos caixilhos antigos, em todo o vão.
    - Recebe um bloco de réguas limpo do próprio quarto, do mesmo tamanho, procurado a até `busca_px` da porta. Só valem px de madeira (`revisao_casab_2910._madeira`) a até `tol_cor` da cor mediana do piso: fora a cortina, a sombra dela, os tapetes e as camas. Escolhe-se o bloco mais limpo e, entre os limpos, o mais perto.
    - Na Casa B, a faixa ia na cor média de cada linha; aqui ficava chapada e rosada, porque junto à porta a cortina cobre o piso.
    - Do lado de fora, `folga_fora_px` px junto à face recebem o piso da varanda da mesma linha, `fora_de_px` mais longe.
  - **Depois:** `vidros_dentro_ta` desenha o plano de dentro em vidro fino, com o miolo e as bordas da Casa B; `bronzes_fora_ta` desenha o de fora em bronze escovado, com o bronze, o escovado, o brilho, o contorno e a sombra de `final3840_casac.brises_suites_tc`.
  - **As junções (`JUNCOES_TA`).** Pedido do usuário: "Preciso que as portas de vidro tanto de vidro quanto de bronze tenhas as junções, na origem e na extremidade conectando as duas  de seus respectivos matérias (vidro com vidro e bronze com bronze)".
    - São as peças de 2,8 x 4,5 pt da ARQ_PAREDE em cada plano, em pt do PDF, por suíte: `fora` e `dentro`. Na origem, do batente à primeira folha; no encontro das folhas, as duas peças lado a lado, unidas num retângulo só; na extremidade, da última folha ao batente.
    - Cada plano é uma máscara só (`_plano_ss`, a 8 x): as folhas e as junções unidas. O vidro leva a borda em volta dela toda e o miolo pela máscara erodida. O bronze leva o contorno centrado na borda da máscara; o brilho fica só nas folhas.
    - Na suíte master, `BRISES_SUITES_TA["folhas_pt"]["Suíte Master"]` junta as 2 folhas de fora do quarto e as 2 da frente do banho master: o plano segue de um para o outro, com as duas peças em fila entre eles.
    - `batentes`: a face de cada batente (y, pt). O piso entre as folhas vai até eles, para limpar os caixilhos antigos das pontas. Com a faixa mais comprida, o bloco de réguas já não sai 100% limpo; os poucos px que não são madeira limpa são refeitos com `cv2.inpaint`, a partir da madeira em volta.
  - **Como refazer:** sempre sobre a final aprovada de antes das portas (commit 29588a5), passada em `--antes`. Sobre a final atual, as portas sairiam duas vezes.
  - **`revisao_casab_2910.vaos_suites_tb(Q, img, q=None)`:** passou a aceitar a configuração. Sem ela, faz o mesmo de antes na Casa B.
- **Mapas da revisão:** `renders/POE642_CasaA_PH_<pavimento>_2910_revisao_mapa.jpg`. A base do PDF é rasterizada no quadro de 3840 px pela afim do `QuadroA` (`p2q`), na escala 4 do pymupdf, e posta ao lado da final.
- **Os itens 1 a 10 da revisão (`--revisao`; OK do usuário: "No item 4, preencha com tom Branco sem tracejado. Itens de 1 a 10 ok.").** `revisao_ta(chave, img, terreo=None)` aplica os itens por pavimento; o `main` faz o Térreo primeiro, porque o Subsolo nevoa as peças dele.
  - **Rótulos (itens 1 a 3):** `_rotulos_pav`, `_rotulo` e `_alfa_rotulo` desenham de novo o alfa de um rótulo da final, sozinho; `_sem_rotulo` tira o texto (o fundo é (img - cor·a) / (1 - a); onde o texto é cheio, inpaint) e `_com_rotulo` o põe de volta. `jardins_ta` (`JARDINS_TA`): sob o JARDIM de 4,79 m², o tracejado da projeção sai na caixa do texto mais `folga_px`; o JARDIM de 17,46 m² vai para o branco. `servico_ta` (`SERVICO_TA`): o X da DOC_LINHAS E PROJEÇÕES na janela `janela_pt` é refeito aberto em volta do rótulo, como na Casa E.
  - **A faixa entre o hall externo e o jardim (item 4, `faixa_branca_ta`, `FAIXA_BRANCA_TA`):** o retângulo do PDF em branco, a 8 x com a beira suave, sem tracejado; no anel de `anel_px` em volta, os px mais claros que a parede (`claro_acima`), restos do X antigo, recebem a cor mediana dela.
  - **Elevador e shafts (item 5, `ELEVADOR_TA`):** `elevador_ta` desenha a cabine de aço de `final3840_casaa.elevador` (a do Subsolo de 26/10, a mesma da Casa B) e o rótulo ELEVADOR por cima. `shafts_ta`: nos shafts de `shafts_pt`, o X cinza sai (os px a até `faixa_px` de cada perna, com o fundo do entorno) e os traços do PDF entram em preto (`final3840_casaa_terreo.preto_branco`), só no miolo, abertos em volta do rótulo SHAFT (`folga_px`).
  - **Subsolo nevoado (item 6, `nevoado_ta`, `NEVOADO_TA`):** as peças do Térreo que o PDF do Subsolo desenha na `caixa_pt` (os preenchimentos da ARQ_CONTRAPISO nas `cores`, mais o deck, `deck_pt`) e que estão na hachura da final recebem o Térreo novo, sem os rótulos e sem as letras escuras pequenas (inpaint), nublado como em `entorno_esmaecido.NUBLADO` (`_nublar_ta`).
  - **Varanda (item 7):** `mesas_varanda_ta` mede o raio do tampo de madeira do render em `n_raios` direções (onde o b* do Lab cai abaixo de `madeira_b`) e o amplia em volta do centro até o círculo do PDF, com a beira de `beira_px`; depois `final3840_casac.jogos_varanda_tc` com `JOGOS_VARANDA_TA`.
  - **Jantar (item 8, `jantar_ta`, `JANTAR_TA`):** as cadeiras do PDF estão na ARQ_LAYOUT HUMANIZAÇÃO e a mesa na ARQ_MARCENARIA; `_QCamadas` passa um quadro com essas peças na ARQ_MOBILIÁRIO para `final3840_casad.jantar_d`. Antes, `_piso_ao_lado` põe no lugar de cada cadeira o travertino da mesma linha, do primeiro trecho livre (fora das peças, dos rótulos e dos traços mais escuros que `traco_cinza`). `passos=0`: sem a cópia do piso do próprio `jantar_d`, que trazia o rótulo da sala de jantar.
  - **Poltronas (item 9, `POLTRONAS_TA`, `POLTRONAS_PARAM_TA`):** por pavimento, as `pecas` (nome, camada, retângulo pt, frente, lado em pt nas giradas), os `tapetes`, `folga_px` por peça (as antigas do render maiores que as do PDF), `recorte_pt` (o buraco da suíte 2 não passa da cortina) e `sombra_parede`.
    - `tirar_poltronas_ta`: o buraco (a peça com a folga e a sombra para baixo e à esquerda), menos o que fica (as outras peças do PDF, os rótulos e, nos pisos claros, a madeira das mesas por contraste de b*). No piso, `_tapar_linhas`: cada trecho de 28 px de cada linha vem do trecho da mesma linha e do mesmo material, o melhor de 8 deslocamentos pelo casamento com os vizinhos; os traços escuros (cinza < `escuro_abs` ou `escuro_rel` abaixo da mediana local) não são origem. No tapete, `_tapete_limpo` e `_tapete_por_perfil`: o tom limpo do miolo (convolução normalizada) e o perfil da borda pela distância à linha do tapete do PDF. As falhas vão para o inpaint; `_emenda_macia` tira o degrau de baixa frequência na beira, sem escurecer mais que 3 níveis.
    - `poltronas_ta`: `final3840_casae._modelo_poltrona_1p`, girado para a frente de cada peça, com a sombra e o contato da Casa E (`retoque_terreo_casae.pousar_planta`).
  - **Sofás e tapetes (item 10):** `estofados_ta` (`ESTOFADOS_TA`) com `revisao_casab_2910.estofados_pdf_tb`; `tapetes_ta` (`TAPETES_TA`) com `final3840_casad.tapete_trama_d`. No 1º Pavimento, `miolo=()`: os tapetes das suítes ficam sob as camas.
  - **Tracejados:** `tracejados_ta` põe de novo por cima, em preto ou branco pelo fundo, os traços das projeções que cruzam as peças trocadas no Térreo (`tracejados_zonas_ta`: os retângulos das poltronas ± 12 pt).
  - **Antes e depois:** `antes_depois_ta` grava os recortes de `ANTES_DEPOIS_TA` em `renders/POE642_CasaA_PH_<pavimento>_2910_<item>_antes_depois.jpg`.
  - **Como refazer:** `python3 revisao_casaa_2910.py --revisao --pasta_antes <pasta>`, com as três finais aprovadas do commit 1ccaaa3 na pasta (os mesmos nomes). Sem `--pasta_antes`, lê as próprias finais e as sobrescreve: sobre as finais atuais, os itens sairiam duas vezes. Depois, `rodape_entrega.py`, `pdf_entrega.py` e `book_entrega.py`.
  - **O item 11 (o piso entre o bronze e o vidro das suítes 1 e 2) não foi aprovado** e não está no `--revisao`.

### Os pedidos de 29/10 à noite da Casa A (Térreo): `pedidos_terreo_casaa_2910.py`

Retoques locais sobre as finais da revisão (commit 219b22b). Cada pedido veio com um recorte do Térreo; cada um é um passo de `pedidos_terreo_ta`, nesta ordem. Os rótulos saem antes dos passos que refazem pisos e móveis e voltam no fim.

- **Ferramentas comuns:**
  - `copiar_textura`: o buraco recebe o mesmo material de outro lugar, trecho a trecho, no deslocamento em que o anel em volta casa melhor (`cv2.matchTemplate` com máscara).
  - `espelhar_faixa`: uma faixa fina, encostada numa parede ou borda, recebe o material de fora dela, refletido.
  - `piso_refeito` (da 2ª leva, abaixo): a zona dos móveis inteira recebe o travertino tecido de novo, emendado ao piso de fora pela membrana. Substituiu o `_piso_suave` da 1ª leva (o tom médio do entorno e os veios de uma faixa ao lado), que deixava a marca da zona.
- **A despensa (`despensa_ta`, `DESPENSA_TA`):** sem o armário em L do render. Cada braço (`pecas_px`) recebe um trecho inteiro de granito limpo da cozinha ou da área gourmet, o de cor e pintas mais perto do granito da despensa (`_peca_granito`). A rampa com o granito da despensa é de `transicao_px`; as paredes ficam. Roda antes de tirar os rótulos, porque o DESPENSA estava sobre o armário.
- **Os rótulos (`rotulos_tirar_ta`, `rotulos_centro_ta`, `ROTULOS_CENTRO_TA`):**
  - Saem com o piso copiado do entorno (`copiar_textura`). A subtração pela cor deixava o texto fantasma, porque a final suavizou os rótulos depois de escritos.
  - Voltam no centro do piso livre do ambiente: o recinto do PDF (`final3840_casab.ambientes_rotulos`, com os boxes e a divisória da Casa A) menos os móveis, as louças, as bancadas, os carros, os tracejados e os rótulos que ficam. Os tapetes maiores que `tapete_m2` não são obstáculo.
  - Nos ambientes abertos (`alvo_pdf`: sala de estar, hall interno, sala de jantar, varanda), o alvo é o ponto do texto do PDF. Onde o recinto vaza (`vazou`), o rótulo fica onde está.
  - Cor: branco sobre o granito e a grama, o cinza dos rótulos no resto.
  - Ficam onde estão os de `manter`: os jardins, a área de serviço descoberta, a piscina, a prainha, o spa, o deck, o shaft, o elevador e a claraboia.
- **As paredes (`paredes_limpas`, `PAREDES_LIMPAS`):**
  - No anel de `anel_px` em volta das paredes do PDF (ARQ_PAREDE escura), os px cinza ou escuros (dentes, franjas, quinas) recebem o piso ou a grama de fora, refletidos.
  - A parede é posta de novo no contorno do PDF, com a cobertura de borda.
  - Ficam de fora os muros do lote e a faixa branca do item 4 da revisão.
- **As janelas (`janelas_ta`, `JANELAS_TA`):** 5 janelas de novo no desenho do PDF: a do jardim de 17,46 m², as duas do escritório, a da quina da varanda e a da pia da cozinha (duas folhas de correr desencontradas). O padrão é o da janela da garagem: o vão no cinza do peitoril com as faces num fio escuro, e o vidro claro com o contorno fino e a sombra curta.
- **A ilha da varanda (`ilha_ta`):** a linha escura no meio da pedra sai; a faixa recebe a pedra de logo acima e de logo abaixo, em espelho.
- **A borda da piscina (`piscina_ta`):** o fio lilás no Bege Bahia junto à borda de baixo sai, com o Bege Bahia de logo abaixo. Ele aparecia só num trecho.
- **Os tracejados (`tracejados_ta`, `TRACEJADOS_TA`, em duas etapas):**
  - `apagar`: saem as duas retas da hachura da pedra que atravessavam a pista (`nao_existe_q`) e o fio antigo do afastamento (`_apagar_faixa`, só do mesmo material: na pista, a pedra vem da pedra e a grama da grama).
  - `desenhar`: o afastamento do PDF (DOC_LINHAS E PROJEÇÕES, as 4 retas) inteiro e o contorno de dentro da laje (ARQ_CONTRAPISO, paralelo ao de fora, `laje_dentro`) entram, em preto ou branco pelo fundo. O contorno de fora da laje junto ao canteiro da pista volta em preto (`laje_fora_pista`).
  - As paredes e o portão ficam por cima dos traços, como no PDF.
- **A borda da pista (`borda_pista_ta`, `BORDA_PISTA_TA`):** entre as duas etapas dos tracejados. A borda da pedra portuguesa com a grama é refeita no contorno do PDF (`ajustes_casaa.acesso_alfa`), do portão à garagem. A faixa é de `faixa_px` do lado da pedra e `faixa_grama_px` do lado da grama: cada lado é refletido, a borda vai na cobertura exata do contorno e a linha fina do PDF passa por cima, contínua.
- **O box do banho varanda (`box_varanda_ta`, `BOX_VARANDA_TA`):** a linha do box volta ao piso (`final3840_casaa.limpar_box`). Entra uma folha só, reta, na linha do PDF, de face a face das paredes, menos `recuo_px`; as pontas do vidro antigo na aresta da parede são limpas.
- **As espreguiçadeiras (`espreguicadeiras_ta`, `ESPREG_TA`):**
  - Saem as do render; a zona recebe o Bege Bahia por quilting, sem tocar na água.
  - Entram as 2 do PDF (ARQ_LAYOUT HUMANIZAÇÃO, 2,00 x 0,60 m): a estrutura em freijó (veio, chanfro, aro), a almofada de linho off-white com volume, o encosto do lado da dobra um tom acima e o vinco da dobra.
  - A sombra macia e a de contato vêm dos jogos da Casa D.
- **As cadeiras do jantar (`jantar_marrom_ta`, `JANTAR_MARROM_TA`):**
  - O modelo padrão (`final3840_casad.jantar_d`), com o assento em couro marrom (`linho`).
  - Em volta da mesa e das cadeiras, até `margem_px`, o travertino é refeito inteiro (`piso_refeito`, na 2ª leva). O tampo fica, com a beira na cor do miolo e a sombra macia das mesas grandes (`SOMBRA_MESA_TA`).
- **O estar da varanda (`varanda_estar_ta`, `banco_estofado_ta`, `VARANDA_TA`):** refeito do piso para cima.
  - O piso: `piso_refeito` na zona dos móveis, até `margem_px` deles. Na 1ª leva era o quilting sem a membrana, e ficava a marca em L da sombra antiga do banco.
  - O sofá curvo: de novo por cima (`_estofado`), depois do tapete.
  - O tapete do PDF: com a trama da biblioteca (`final3840_casad.TAPETE_TRAMA_D`), a faixa de acabamento da borda um tom abaixo e a sombra curta.
  - As duas mesas de centro sobrepostas, em carvalho: a de baixo no tom médio e a de cima no sobretom mais claro. A de cima faz sombra na de baixo.
  - As 2 mesinhas redondas de madeira: entre as poltronas e na ponta do sofá.
  - As 2 poltronas no modelo padrão, de contorno limpo (`poltronas_limpas_ta`).
  - O banco estofado (DOC_TEXTOS): o quadro em madeira, o assento de linho em 3 partes, com os vincos nas costuras do PDF, e as 2 almofadas das pontas, um tom acima e mais altas.
  - A planta junto à ponta do sofá fica (`fora_px`).
- **As mesinhas e a poltrona da sala de estar:** na 1ª leva eram `mesinhas_ta` e `poltrona_estar_ta`. Na 2ª leva, cada ambiente é refeito inteiro (`projecao_varanda_ta`, `sala_estar_ta`): as mesinhas de madeira do PDF (`_peca_madeira_pdf`: veio, chanfro, aro e sombra) e as poltronas limpas entram sobre o piso refeito.
- **O matelassê (`matelasse_ta`, `MATELASSE_TA`):** o das camas da Casa B (`revisao_casab_2910.MATELASSE_TB`) sobre o edredom de cada cama, da dobra aos pés, dentro do colchão. No Térreo é a cama do motorista (`ajustes_casaa.CAMA_MOTORISTA`); no 1º Pavimento, as 6 camas (`CAMAS_1PAV`). As faixas e almofadas bordô e os traços escuros ficam lisos.
- **A 2ª leva (os pedidos vendo a entrega da 1ª):** o usuário apontou o piso imperfeito em volta das mesinhas, das cadeiras do jantar, das poltronas e do tapete da sala, a marca em L atrás do banco da varanda, o entorno borrado da mesa lateral do escritório, os rótulos desorganizados (a GARAGEM e o Q. MOTORISTA), o marrom no banho do motorista e a poltrona do terraço gourmet que não tinha girado. A seção 13 do script refaz cada ambiente do piso para cima.
  - **O piso (`piso_refeito`, `PISO_TA`):**
    - O tecido: quilting (`texturas.quilting`) do travertino limpo de `fontes_px`, só com os espelhos na horizontal, para os estratos ficarem deitados.
    - A emenda: a diferença entre o piso real e o tecido, na borda da zona, suavizada (`suave_px`) e levada para dentro pela membrana harmônica (`_membrana`, `scipy.sparse`).
    - Só vale como borda o piso de fora: perto do tom das fontes (`tom_tol`), sem as paredes, as plantas, os móveis, os traços e os pontos (`salto`).
    - Assim, o tom chega à borda igual ao de fora, sem degrau e sem mancha, e dentro o desenho é o do travertino.
  - **A zona de cada ambiente:**
    - A pegada dos móveis, até `margem_px`, com as sombras e os restos das peças antigas. A pegada das poltronas antigas é exata (`_pegada_poltronas`: elas desenhadas de novo num quadro neutro).
    - Menos as paredes e os pilares do PDF (`_paredes_fixas`), as plantas (`_plantas`) e os outros móveis (`_outros_moveis`).
    - Os traços das projeções que passam na zona voltam por cima (`_tracejados_zona`).
  - **As poltronas (`poltronas_limpas_ta`, `POLTRONA_LIMPA_TA`):** o modelo padrão com o contorno limpo (`_modelo_limpo`). A silhueta é alisada, a beira de `beira_px` recebe a cor do estofado de dentro (sem a franja castanha do bouclé da foto) e a borda leva um fio um pouco mais escuro (`escurecer`).
  - **As sombras:** `_sombra_piso` e `_pintar` arredondam a cor (o `astype` truncava e escurecia a caixa da peça em 1 nível). A margem é de `SOMBRA_FOLGA_PX`, para a sombra não ser cortada na caixa. As mesas de tampo grande levam `SOMBRA_MESA_TA`, mais curta e mais leve.
  - **As mesas redesenhadas do PDF (`_mesa_contorno_pdf`):** o contorno do PDF fechado e alisado, no tom da mesa da final (`_peca_da_final`: a mediana do miolo), com a borda nítida, o chanfro e a sombra macia. Valem para a mesa de centro da sala de estar e a mesa triangular do estar em X; a da final, de beira borrada, sai com o piso.
  - **Os ambientes:**
    - `jantar_marrom_ta`: o piso em volta da mesa e das cadeiras; o tampo colado de novo (`_colar_peca`); as cadeiras no modelo padrão.
    - `varanda_estar_ta`: o piso (sem a marca em L), o tapete, o sofá curvo, as 2 mesas de centro, as 2 mesinhas, as 2 poltronas e o banco estofado.
    - `projecao_varanda_ta` (`PROJECAO_TA`): as 2 poltronas sob a projeção e a mesinha de madeira entre elas; o caco cinza sai.
    - `sala_estar_ta` (`SALA_ESTAR_TA`): o tapete redondo (a trama, a faixa da borda, a sombra), o sofá curvo, a mesa de centro do PDF, as 3 mesinhas de madeira e as 3 poltronas. A da direita do tapete fica na diagonal do PDF (`giro`).
    - `estar_x_ta` (`ESTAR_X_TA`): o piso do estar inteiro, a mesa triangular do PDF e as 4 poltronas.
    - `escritorio_ta` (`ESCRITORIO_TA`): a mesa lateral do PDF (dois tampos redondos de madeira, no tom e no sobretom) e a poltrona.
    - `gourmet_poltrona_ta` (`GOURMET_POLTRONA_TA`): a poltrona do terraço gourmet, junto aos brises, girada como no PDF (`frente`, o encosto no alto à esquerda, de frente para a mesa de centro). Na 1ª leva, o giro foi feito por engano na poltrona da sala de estar.
    - `banho_motorista_ta` (`BANHO_MOTORISTA_TA`): o fio marrom em volta do vaso e o granito do quarto no vão da porta e sob a folha saem com o Bege Bahia do próprio banho (`piso_refeito` com as fontes dele). O vaso volta com a beira na cor do miolo, um aro um pouco mais escuro e a sombra de contato leve.
  - **Os rótulos (`rotulos_tirar_ta`, `rotulos_centro_ta`):**
    - Ao tirar: depois da cópia do entorno, o buraco recebe o tom do piso de fora (média normalizada de `tom_sigma_px`, sem o buraco e os traços); do trecho copiado fica só o desenho fino. Assim não fica o remendo creme onde estava o rótulo.
    - O corpo: o padrão (1,3) onde cabe no piso livre; senão, o nome de duas palavras em duas linhas no mesmo corpo (como o BANHO VARANDA); só então 1,15 e 1,0 (`corpos`). Os rótulos ficam do mesmo tamanho sempre que cabem.
    - O lugar: o px mais perto do alvo onde a caixa cabe inteira no livre. O alvo é `alvos_px` (a GARAGEM no meio do carro do centro, acima dos carros; o Q. MOTORISTA no piso abaixo da cama), senão o texto do PDF nos ambientes abertos, senão o centro do recinto.
    - A região: `regioes_px` (a faixa livre da garagem). Nos ambientes que vazam, o rótulo anda no máximo `aberto_px`.
    - O script imprime o corpo de cada rótulo e se foi em duas linhas.
  - **O 1º Pavimento:** o nublado do Térreo, onde ele mudou, acompanha as mudanças (`nublado_1pav_ta`).
- **A 3ª leva (os pedidos vendo a entrega da 2ª, e os achados aprovados):** seções 15 a 17 do script.
  - **As paredes do motorista (`paredes_motorista_ta`, `PAREDES_MOTORISTA_TA`):** conferidas uma a uma contra o PDF; as paredes estavam no contorno dele, e as falhas estavam nas pontas e junto delas.
    - Em cada ponta de parede nos vãos das portas (`pontas_pt`: a da garagem, as duas do banho e as duas do quarto), o piso em volta é refeito do material de junto (`copiar_textura`). Entram a parede e os batentes do PDF (`batentes_pt`, as peças brancas da ARQ_PAREDE), no cinza das folhas, com o fio escuro. As folhas (`folhas_pt`) ficam como estão.
    - O nicho do box do banho volta no desenho do PDF: as laterais e o fundo na cor da parede, a abertura no Bege Bahia do banho, um pouco mais claro, com o fio.
    - Por fora da parede da direita do quarto, os tracinhos claros de um caixilho do render saem com o jardim de logo ao lado, refletido (`fora_px`).
  - **O terraço gourmet (`gourmet_cadeiras_ta`):** as duas poltronas de baixo e a mesinha do render (rosadas) saem com o piso refeito. Entram as poltronas de contorno limpo, de frente para o sofá (a abertura para cima, como no PDF), e a mesinha em madeira.
  - **O aparador do escritório (`aparador_ta`):** a peça de borda áspera sai com o piso. Volta no retângulo do PDF, em madeira, no tom dela.
  - **A mesa de centro da sala de estar:** em madeira (`SALA_ESTAR_TA["mesa_madeira"]`; `_mesa_contorno_pdf` com `madeira`: o veio no comprido sobre o tom).
  - **As poltronas do 1º Pavimento (`poltronas_1pav_ta`):** as 3 no modelo de contorno limpo.
    - O lugar delas é refeito como na revisão: da final de antes dela (`--antes_1pav`), os passos de `revisao_casaa_2910` até os tapetes, as poltronas limpas e os sofás.
    - Só os px que mudam entre as poltronas da revisão e as limpas passam para a final. Fora delas, a reconstrução é igual à final px a px; o script imprime quantos px fugiram disso (0).
  - **As frentes dos banhos das suítes 1 e 2 (`banhos_1pav_ta`, `BANHOS_1PAV_TA`):** no PDF, o plano de fora das portas segue na frente do banho (duas folhas na suíte 1, uma na suíte 2, com as junções e a peça do canto). Estavam em vidro.
    - A faixa entre a parede do banho e as folhas (`faixa_pt`) recebe o Bege Bahia da varanda de logo ao lado, refletido.
    - A sombra curta é só a das peças novas. O plano inteiro é pintado de novo no bronze escovado (`revisao_casaa_2910.bronzes_fora_ta`, com as folhas e as junções novas).
    - As janelas dos banhos voltam no padrão das janelas do Térreo (`janelas_ta` com `JANELAS_BANHOS_1PAV_TA`): o vão no cinza do peitoril, os requadros da parede nas pontas (`requadros`) e as duas folhas de vidro desencontradas.
  - **O Subsolo:**
    - O deck nevoado ganha o trecho de baixo, à esquerda da escada, até a linha do gramado: a 3ª caixa do `deck_pt` em `revisao_casaa_2910.NEVOADO_TA`.
    - `grama_escada_ta` (`GRAMA_ESCADA_TA`): a grama encontra a escada e o deck numa linha reta, a do PDF (`linha_pt`). As primeiras linhas da grama recebem a grama de logo abaixo, refletida (`grama_px`); as últimas da escada e do deck, as de logo acima. Sai o fio claro com pintas que ficava entre elas.
- **Os rótulos do 1º Pavimento e do Subsolo (seção 18; `rotulos_pavimento_ta`, `ROTULOS_1PAV_TA`, `ROTULOS_SUBSOLO_TA`):** o método dos rótulos do Térreo, só nos rótulos da lista (`so`; "NOME|área" quando o nome se repete, como as varandas).
  - No 1º Pavimento: BANHO 2, CLOSET 2, VARANDA de 7,15 m², SUÍTE 2, SUÍTE 3 (estava sobre o tapete) e B. SERVIÇO. No Subsolo: BANHO FEM. e BANHO SERV.
  - O rótulo é achado na imagem pela forma do texto (`_achar_rotulo`): entre o desenho dos ajustes e as variantes de corpo e de quebra, o de melhor correlação, até 90 px em volta. No Subsolo, o motor das Casas B a D tinha posto os rótulos fora dos ajustes (o BANHO SERV. em duas linhas).
  - As sobras de rótulos antigos em volta do texto (`fantasmas_em`: no BANHO 2, um "I" e um "A" de uma cópia deslocada) entram no buraco: os px escuros e neutros, bem mais escuros que o piso (`fantasma_dif`), numa faixa em volta (`fantasma_px`), fora dos objetos do PDF. A folga em volta do texto não leva os px escuros vizinhos (`escuro_folga`: o tracejado da borda da varanda, que o motor do 1º Pavimento desenhou e o PDF não tem, fica).
  - Nos quartos e nos banhos (`linhas_em`: réguas, tapetes e travertino, de desenho deitado), o buraco é tapado pela mesma linha deslocada até o primeiro lugar livre do mesmo material (`revisao_casaa_2910._tapar_linhas`, `tol_linhas`), sem a correção de tom, que marcava a forma do texto na borda do tapete. Na varanda (o Bege Bahia, numa faixa estreita), pela cópia de trechos com o tom do entorno, como no Térreo.
  - A volta: os tapetes são obstáculo (`tapete_m2` sem limite); os vidros dos boxes fecham o recinto (`com_vidros`); as paredes são obstáculo (`sem_paredes`); o alvo é o centro do piso livre do recinto (`alvo_livre`); nos banhos com box, o piso seco basta com 0,3 da área do PDF (`minimo`).
  - O B. SERVIÇO fica no lugar dele, centrado na largura do banho, a 1,15×: o piso seco ao lado do vaso tem uns 46 px, menos que o texto em qualquer corpo.
- **Os outros pavimentos:**
  - 1º Pavimento: `nublado_1pav_ta`, onde o Térreo mudou, sem os rótulos e sem os tracejados novos da pista (`fora_px`). Fora da pegada, soma a diferença entre o Térreo novo e o antigo, nublados (`entorno_esmaecido.NUBLADO`). Nos vazios, aplica a razão entre eles. Depois, o matelassê.
  - Subsolo: `revisao_casaa_2910.revisao_ta("Subsolo", ...)` sobre a final de antes da revisão, com o Térreo novo, para as peças nevoadas.
- **Antes e depois:**
  - `antes_depois_pedidos_ta` grava as caixas de `ANTES_DEPOIS_PEDIDOS_TA` em `renders/POE642_CasaA_PH_<pavimento>_2910b_<trecho>_antes_depois.jpg`, contra as finais da revisão.
  - Com `--pasta_comparar`, grava também as caixas de `ANTES_DEPOIS_2A_TA` em `..._2910c_<trecho>_antes_depois.jpg`, contra as finais da 1ª leva (commit 387a97f).
  - Com `--pasta_comparar_3a`, as de `ANTES_DEPOIS_3A_TA` em `..._2910d_<trecho>_antes_depois.jpg`, contra as finais da 2ª leva (commit cb0b471).
  - Com `--pasta_comparar_4a`, as de `ANTES_DEPOIS_4A_TA` em `..._2910e_<trecho>_antes_depois.jpg` (os rótulos), contra as finais da 3ª leva (commit 0a17741).
- **Como refazer:**

  ```bash
  # de POE642_CasaA/scripts/; <pasta> com as três finais do commit 219b22b, <pasta_1a> com as do 387a97f e <pasta_2a>
  # com as do cb0b471 e <pasta_3a> com as do 0a17741 (os mesmos nomes)
  python3 pedidos_terreo_casaa_2910.py --pasta_antes <pasta> --antes_subsolo <a final do Subsolo do commit 1ccaaa3> \
      --antes_1pav <a final do 1º Pavimento do commit 1ccaaa3> --pasta_comparar <pasta_1a> --pasta_comparar_3a <pasta_2a> \
      --pasta_comparar_4a <pasta_3a>
  python3 rodape_entrega.py --no-quadro --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png \
      --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_rotulos.png \
      --render 1Pavimento=../renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png
  python3 pdf_entrega.py
  python3 book_entrega.py
  ```

  - Sem `--pasta_antes`, o script lê as próprias finais e as sobrescreve; sobre as finais atuais, os pedidos sairiam duas vezes.
  - O `final3840_casaa_1pav.inicial` (a pegada e os vazios do 1º Pavimento) fica no cache de `POE642_CACHE`, se a variável estiver definida.

### As alterações do cliente no Subsolo da Casa A: `cliente_subsolo_casaa_0511.py` (05/11)

Pedidos do cliente (Paulo Octávio), cada um com o recorte da planta do Subsolo: "Diminuir a escala da grama"; "Colocar a seta na escada e a descrição - Sobe para o Deck." (o usuário: "seta na escada é assim", com o triângulo cheio na escada); "Tirar a representação do deck e da piscina superior. Deixar apenas o subsolo mesmo."; "Representar as prateleiras com uma cor neutra única, sem textura"; "Deixar sem hachura. Deixar na cor branca. Sem fundo."; "Deixar a representação do Bege Bahia menos manchado (para melhor representação)"; e do usuário, com o recorte da madeira da academia: "remover essas linhas". Um passo por pedido, sobre a final de c1f7ff5, na ordem de `cliente_subsolo_cs`:

- **Entorno em branco (`fundo_branco_cs`, `pegada_quadro`):** a pegada de R2 (`ajustes_casaa.SUBSOLO_R2`, a máscara do ajuste) levada ao quadro por `rotulos_casaa.no_quadro_fixo`; fora dela, branco (saem a hachura, o contorno do lote e as peças do Térreo nevoadas: deck, piscina, spa, pisantes e espreguiçadeiras). Nos px da borda, a hachura sai pela conta dela (as mesmas diagonais de `subsolo_hachurado`).
- **Borda (`BORDA_CS`, `borda_cs`):** a pegada passa uns px do desenho do Subsolo; fora do desenho do PDF (as peças cheias da ARQ_CONTRAPISO e da ARQ_PAREDE na caixa de R2, os degraus de `DEGRAUS_A` e a grama crescida `grama_px`), só a sobra vira branco: o claro neutro (a hachura) ou azulado (o nevoado da piscina). O Bege do pátio, a grama e as paredes ficam.
- **Academia (`PROJECAO_CS`, `projecao_cs`):** a projeção em U junto à parede de baixo (`final3840_casaa.PROJECAO_ACADEMIA`) foi pintada com cobertura vezes 0,75; a madeira volta pela conta inversa, fora da parede (e no px da borda dela que não ficou escuro, acima de `parede_lum`).
- **Bege Bahia (`BEGE_CS`, `bege_cs`):** o desenho D da foto da biblioteca (`final3840_casab.piso_textura`, "bege", máscara e semente de `PISOS_A`, com a marca de `MARCAS_BEGE`) é refeito igual ao da final e trocado por 1 + `forca` (D − 1), a 45%: as manchas com menos contraste, a luz, as sombras e o tom iguais. Os objetos pintados depois do piso (onde a final dividida por D foge da luz em volta, `desvio`) ficam de fora. Na faixa das prateleiras (a cobertura delas crescida `faixa_px`; usuário: "tem um borrão antigo do material anterior" no L), o piso é refeito pelo modelo: a luz de cada canal no piso limpo em volta vezes o desenho suavizado (sem a borda do freijó nem a sombra antiga). Precisa de `final3840_casaa.inicial` (o cache de `POE642_CACHE` ou do tmp).
- **Prateleiras (`PRATELEIRAS_CS`, `prateleiras_cs`):** os dois braços de `final3840_casaa.DEPOSITO` como um L só, numa cor só, o cinza quente claro (RGB ~195, 191, 186), sem o veio do freijó, sobre o piso refeito, com a sombra curta de novo (a do L inteiro, sem a de um braço no outro).
- **Grama (`GRAMA_CS`, `grama_cs`):** a grama da biblioteca (`texturas.textura("grama")`) na resolução da prancha e na metade da escala real (`escala` 0,5), no verde da caixa dele, no tom mediano `tom`: o verde-oliva acinzentado da referência do usuário (RGB ~121, 127, 101; usuário: "traga o tom da grama para mais próximo dessa referência"); na borda da pegada, com o branco de fora na mesma proporção.
- **Degraus (`degraus_cs`; usuário: "suavize também os degraus da escada"):** o desenho do Bege Bahia dos degraus (`final3840_casaa.degraus_bege`, na janela da tela deles) é refeito igual e trocado pela mesma fração do piso (`BEGE_CS["forca"]`); o tom de cada degrau, a sombra dos espelhos e o trecho esmaecido ficam. As duas linhas de baixo vêm de 4 px acima, como em `grama_escada_ta`.
- **Escada (`ESCADA_CS`, `escada_cs`):** o S de `ESCADA_A` sai (o pátio das mesmas colunas, `desloc_s` abaixo); o triângulo cheio no degrau de baixo, com a ponta para onde a escada sobe; "SOBE PARA O" / "DECK" no lugar do S, em duas linhas (usuário: "quebre a linha em 'Sobe para o / Deck'"; `entrelinha_px`), na fonte, no corpo e na cor do S, com o meio do bloco na altura do triângulo.
- **Pedais (`PEDAIS_CS`, `pedais_cs`; usuário: "ficou faltando o pedal do lado direito da bicleta ergométrica"):** em cada bicicleta, o pé de vela com o pedal de baixo (o escuro ligado na `caixa`, com a borda esfumada, na cor dos px mais escuros dele) girado 180° em torno do eixo do pedivela (`eixo2`, o dobro do eixo: no meio do quadro, na coluna do pé de vela) e pousado do outro lado, com a sombra curta de `APARELHOS["sombra"]`.
- **Antes e depois:** `ANTES_DEPOIS_CS` em `renders/POE642_CasaA_PH_Subsolo_0511_{planta,escada_grama,deposito,academia_linhas,bicicletas}_antes_depois.jpg`, contra a final de c1f7ff5 (só quando grava a final).
- **Como refazer:** `python3 cliente_subsolo_casaa_0511.py --antes <a final do Subsolo de c1f7ff5>` (sem `--antes`, lê a própria final e os passos sairiam duas vezes); depois `rodape_entrega.py --no-quadro --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png`, `pdf_entrega.py` e `book_entrega.py`.


### A ampliação A3 do Subsolo da Casa A pelo Nano Banana Pro: `ampliacao_a3_casaa.py` (05/11)

Pedido do usuário: "preciso que você gere uma imagem ampliada em A3, ocupando a A3 inteira da prancha A em 4k pelo nano banana pro. só a imagem em alta resolução." A final do Subsolo (`renders/POE642_CasaA_PH_Subsolo_final_rotulos.png`) vai à A3 deitada a 300 dpi (4961 x 3508 px), só a imagem (sem rodapé), com a planta na largura toda (`A3["margem_px"]` de cada lado; a planta é mais larga que a A3, sobra branco em cima e embaixo). Escala: 2,784 x a final.

- **Os textos saem antes da IA (`preparar`):** a IA redesenha texto miúdo errado (troca números de área). Cada rótulo da final é achado na própria imagem (`ajustar_rotulos`: o corpo e a quebra entre as opções das buscas e o desvio que casam o desenho de `retoque_1pav_casae.rotulos_ambientes` com o escuro da imagem, correlação 0,98 a 0,996; o BANHO FEM. da final está um pouco borrado e casa a 0,81); o fundo sob o texto sai pela conta do alfa e o miolo do traço pelo entorno (`tirar`); o BANHO FEM. sai linha a linha, com o piso logo acima. A seta e o "SOBE PARA O / DECK" saem pela mesma conta, com o desenho de `cliente_subsolo_casaa_0511.escada_cs`. A entrada da IA é o recorte da planta sem textos em 4:3 (a proporção do Nano Banana Pro mais perto de √2), `renders/POE642_CasaA_PH_Subsolo_A3_entrada_ia.png`; os ajustes dos rótulos e os recortes em `renders/POE642_CasaA_PH_Subsolo_A3_rotulos.json`.
- **A IA:** Nano Banana Pro no Higgsfield, 4K, 4:3, a entrada como referência e o prompt de ampliação fiel (mesma composição, nada acrescentado nem tirado, sem texto; só resolução e textura dos materiais). Saída 4800 x 3584: `renders/POE642_CasaA_PH_Subsolo_A3_saida_nano_banana_pro.png` (job f3b47b34-78c0-40a6-b327-f0f8aff0c07e). O ambiente da sessão precisou liberar upload.higgsfield.ai e a CDN do resultado.
- **A montagem (`montar`):** a saída alinhada à entrada (ECC afim; deu quase identidade, a IA não mexeu na geometria), recortada em √2 e levada a 4961 x 3508; os tons da final aprovada de volta (a baixa frequência, `tom_sigma_px`, vem da entrada ampliada e o detalhe fino fica o da IA: ela tinha clareado a madeira da academia e mudado o cinza do depósito e o elevador); o X tracejado dos shafts (`SHAFTS_PT`; a IA o fez contínuo) da entrada ampliada; o fundo fora da planta em branco puro; os rótulos e a escada desenhados de novo no corpo da A3, nítidos.
- **Conferência:** a final ampliada sem IA ao lado da A3, em recortes, `renders/POE642_CasaA_PH_Subsolo_A3_conferencia_{academia_banhos,escada_grama,deposito_circulacao,hall_elevador}.jpg`; prévia em `renders/POE642_CasaA_PH_Subsolo_A3_4K_previa.jpg`.
- **Saída:** `entrega/POE642_CasaA_PH_Subsolo_A3_4K.png` (4961 x 3508, 300 dpi).
- **Como refazer:** `python3 ampliacao_a3_casaa.py preparar` (se a final mudar); a entrada no Nano Banana Pro (4K, 4:3); `python3 ampliacao_a3_casaa.py montar <saída da IA>`.

### Subsolo da Casa A: a grama padrão e o banco da sauna (`cliente_subsolo_casaa_0511.py`, 07/11)

- **Grama padrão (`GRAMA_CS`, `grama_cs`; usuário, com a planta de um quintal: "USE ESSA ESCALA E COR DE GRAMA. USAREMOS ESSA GRAMA COMO PADRÃO PARA AS DEMAIS"):** a textura `grama_padrao` da biblioteca (`_texturas/texturas.py --so grama_padrao`: tecida dos recortes limpos do gramado de `originais/referencia_grama_padrao.webp`, a 62 px/m medidos nos 10 pés dele), na escala real e na cor dela (RGB ~79, 75, 39), sem retoque de tom nem desfoque (`tom` None). As outras plantas recebem a mesma grama uma a uma, quando o usuário pedir.
- **Banco da sauna (`SAUNA_CS`, `sauna_cs`; usuário, com uma referência anotada: "fazer esse jogo de cores para destacar o que está mais em cima e mais embaixo"; "TANTO O BANCO QUANTO O PISO DA SAUNA SÃO EM TRAVERTINO BRUTO"):** o banco (`final3840_casaa.SAUNA`) passa a 3% acima do tom do piso, canal a canal (os veios, a quina boleada e a aresta como estavam); o piso da sauna (`piso_px`, entre os vidros, a parede da direita e a frente do banco) a 93%; no piso, ao longo da frente do banco, a sombra de contato um pouco mais larga (`contato`). O banco foi de RGB ~212, 193, 176 para ~242, 229, 213 e o piso, de ~235, 222, 207 para ~218, 207, 193.
- **Antes e depois (contra a final de 97fd532):** `renders/POE642_CasaA_PH_Subsolo_0711_{grama,sauna}_antes_depois.jpg`.
- A ampliação A3 (`ampliacao_a3_casaa.py`) fica para o fim, com os materiais fechados (usuário: "AO TERMINAR FAREMOS UM UPSCALE"); a de 05/11 em `entrega/` é anterior a esta rodada.

### Rótulos em letra manuscrita, opção B (`rotulos_manuscritos_casaa.py`, 10/11)

Pedido do usuário, com o recorte do título "Katherine Backyard" da referência do quintal: "E ME MANDE UMA VERSÃO TAMBÉM COM TIPO DE FONTE. QUERO TER DUAS OPÇÕES. COM A FONTE ATUAL E A FONTE DA LETRA IGUAL A ESSA A DA IMAGEM". A opção A é a final como está (Inter); a B tem os rótulos e o "SOBE PARA O / DECK" na **Kalam Regular** (OFL, `entrega/assets/fontes/Kalam-Regular.woff`, com a licença), a mais parecida com a letra da referência entre dez manuscritas livres comparadas na mesma largura (Architects Daughter, Caveat, Coming Soon, Delius, Gloria Hallelujah, Handlee, Indie Flower, Kalam, Patrick Hand, Sue Ellen Francisco): traço de marcador, levemente inclinada, o "a" de um bojo e o "y" de perna reta.

- Os rótulos da final são achados na imagem e tirados como na ampliação A3 (`ampliacao_a3_casaa.ajustar_rotulos`, `tirar`); cada linha volta na Kalam no mesmo meio e na mesma linha de base da Inter, com as maiúsculas 1,12 x a altura delas (`MANUSCRITA["altura"]`) e o traço engrossado 0,25 px de cada lado (`reforco_px`, o peso de marcador da referência); a área num texto só ("A: 6,83 m²"). A seta da escada fica; o texto dela vai na Kalam, preso pela esquerda.
- Saídas: `renders/POE642_CasaA_PH_Subsolo_final_rotulos_manuscrita.png`, a prancha `entrega/POE642_CasaA_PH_Subsolo_entrega_manuscrita.png` e a comparação `renders/POE642_CasaA_PH_Subsolo_rotulos_opcoes_A_B.jpg`. O PDF e o book continuam com a opção A até o usuário escolher.
- Como refazer: `python3 rotulos_manuscritos_casaa.py` (depois de qualquer mudança na final do Subsolo).

### Rótulos do Subsolo: BH. e todos no centro do ambiente (`rotulos_subsolo_casaa.py`, 10/11)

Pedidos do usuário, vendo as duas opções de letra: "PARA BANHO USE BH."; "CENTRALIZE "SAUNA" DENTRO DO AMBIENTE"; "CENTRALIZE TODOS OS RÓTULOS". O último passo do `cliente_subsolo_casaa_0511.py` (`RS.aplicar`) acha os rótulos na imagem, monta a especificação deles (`renders/POE642_CasaA_PH_Subsolo_rotulos_spec.json`: nome, ponto do PDF, corpo, quebra, desvio, cor e o texto trocado), aplica os pedidos e desenha de novo os que mudam, no desenho da Inter de sempre:
- **BH. (`PEDIDOS_ROT["abreviar"]`):** BANHO SERV./FEM./MASC. viram BH. SERV./FEM./MASC.; a origem do nome anda para o meio ficar onde estava; o do banho de serviço sai da quebra (numa linha só, a área embaixo).
- **Centro (`CENTRO`, `centralizar`):** o recinto de cada rótulo pelas paredes e vidros do PDF (`final3840_casab.ambientes_rotulos`, o box de fora); os obstáculos são as peças do PDF, as prateleiras do depósito e o banco da sauna; o rótulo vai ao ponto mais perto do centro do piso livre onde o bloco cabe com folga. Mudaram: ELEVADOR (ao centro da cabine), HALL, ACADEMIA, DEPÓSITO, CIRCULAÇÃO, SAUNA (20 px abaixo, no meio entre o vidro e o banco), BH. FEM. e BH. MASC.; o BH. SERV. não cabe livre mais perto do centro e fica onde estava.
- A opção manuscrita (`rotulos_manuscritos_casaa.py`) e a ampliação (`ampliacao_a3_casaa.py`) leem a mesma especificação.
- Antes e depois: `renders/POE642_CasaA_PH_Subsolo_1011_{rotulos,rotulos_banhos_sauna}_antes_depois.jpg`.

### O JPG em 12K das duas opções de letra e a A3 refeita (`ampliacao_a3_casaa.py`, 10/11)

Pedido do usuário: "PODE GERAR O ARQUIVO JPG 12K DAS DUAS OPÇÕES" (antes: "VOU PRECISAR DA IMAGEM, SÓ DA IMAGEM, EM JPG PARA O CLIENTE PODER TRABALHAR EM CIMA DELA PARA O BOOK DELA. [...] QUERO UM JPG EM 12K"). Só a imagem do Subsolo, sem rodapé, na proporção da A3 deitada, nas duas opções de letra.

- **A entrada da IA de novo (`preparar`):** da final atual (grama padrão, banco da sauna, BH. e rótulos no centro), os textos fora pela especificação (`rotulos_subsolo_casaa.ler_spec`).
- **Nano Banana Pro, 4K, 4:3:** 4800 x 3584 (job 03df474f-c4c0-4b5d-8e35-ec043b2948d3).
- **O que a IA inventou, corrigido antes de ampliar (`corrigir`, `CORRIGIR_PX`):** o mapa das diferenças de estrutura (passa-banda) entre a saída e a entrada ampliada mostrou a sauna com bancos em degraus em L (o PDF tem um banco só), a bancada de granito do BH. SERV. com veio de madeira e os chuveiros quadrados (com a grade de furos) trocados. Nesses cinco trechos entra a entrada ampliada (Lanczos, com nitidez), com a borda esfumada; o resto (os aparelhos da academia, fiéis e mais nítidos) fica o da IA. A saída corrigida é `renders/POE642_CasaA_PH_Subsolo_A3_saida_nano_banana_pro.png`.
- **A A3 em 4K refeita (`montar`):** da saída corrigida, com os materiais e os rótulos atuais (opção A): `entrega/POE642_CasaA_PH_Subsolo_A3_4K.png` (4961 x 3508, 300 dpi). Conferência e prévia como antes (`renders/POE642_CasaA_PH_Subsolo_A3_*`).
- **4K a 12K:** Topaz no Higgsfield (`topaz_image`, High Fidelity V2, saída 12288 x 9175; job 5bfe6125-bbcd-4d93-b694-869f411650e7). A saída (96 MB) não vai para o git.
- **A montagem em 12K (`montar12k`, `GRANDE`, `montar_grande`):** a saída do Topaz alinhada à entrada (ECC afim), recortada na A3 deitada, 12288 x 8689 px (6,896 x a final); os tons da final de volta (a correção sai na escala da entrada e é ampliada em faixas, sem passar a imagem inteira por float); o X tracejado dos shafts; o fundo fora da planta em branco puro; os rótulos e o "SOBE PARA O / DECK" desenhados direto no corpo de 12K, numa janela em volta de cada um: na Inter (opção A) e na Kalam (opção B, com o reforço do traço na escala). JPG qualidade 95, sem subamostragem de cor, 743 dpi na A3.
- **Saídas:** `entrega/POE642_CasaA_PH_Subsolo_12K_opcao_A.jpg` (Inter) e `..._12K_opcao_B.jpg` (Kalam), 15,1 MB cada; prévias `renders/POE642_CasaA_PH_Subsolo_12K_opcao_{A,B}_previa.jpg` e conferências (a final ampliada sem IA ao lado) `renders/POE642_CasaA_PH_Subsolo_12K_opcao_{A,B}_conferencia_{academia_banhos,escada_grama,deposito_circulacao,hall_elevador}.jpg`.
- **Como refazer:** `python3 ampliacao_a3_casaa.py preparar`; a entrada (`renders/POE642_CasaA_PH_Subsolo_A3_entrada_ia.png`) no Nano Banana Pro (4K, 4:3); `python3 ampliacao_a3_casaa.py corrigir <saída da IA> <corrigida>` (antes, conferir no mapa das diferenças se a IA inventou outro trecho e acrescentá-lo a `CORRIGIR_PX`); `python3 ampliacao_a3_casaa.py montar <corrigida>` (a A3 em 4K); a corrigida no Topaz (High Fidelity V2, 12288 x 9175); `python3 ampliacao_a3_casaa.py montar12k <saída do Topaz>`.

### Subsolo: as pontas de parede nos portais e o banco da sauna mais escuro (`cliente_subsolo_casaa_0511.py`, 10/11)

Pedidos do usuário, com os recortes do JPG em 12K: "1- CORRIGIR ESSA FALHA NA PAREDE (NO PORTAL)" (a parede entre a academia e o BH. FEM./BH. MASC. e a do BH. SERV.); "2- O TOM MAIS ESCURO É EM CIMA (NO BANCO), NÃO NO PISO DA SAUNA. ESSA É A REGRA, NA PARTE DE CIMA, SE FOR O MESMO MATERIAL, O TOM FICA MAIS ESCURO."

- **Portais (`PORTAIS_CS`, `portais_cs`, depois da sauna):** nos portais, o PDF tem o marco da porta (o batente no vão e as guarnições de 4,2 x 1,2 px saindo das faces da parede); sem a folha da porta, esses restos ficavam na ponta da parede como um risco escuro, que a IA da ampliação transformou num pé inclinado. Nos portais do BH. SERV., do BH. FEM. e do BH. MASC. (as duas pontas de cada um), as peças brancas do marco (crescidas 1,5 px, fora da parede e do px de contorno das faces) voltam a ser o piso em volta (inpaint, com a parede também como desconhecida); a ponta fica reta, no desenho do PDF. Os outros dois portais com o mesmo resto (o do depósito e o do BH. da sauna) ficam como estão até o OK do usuário.
- **Sauna (`SAUNA_CS`):** o banco a 0,90 do tom do piso, canal a canal (de RGB ~212, 193, 176 para ~211, 200, 186), e o piso no tom dele (~235, 222, 207, como o dos banhos); a sombra de contato fica. Na versão de 07/11 era o contrário (o banco 1,03 x o piso e o piso a 0,93). Regra atualizada no `POE642_REGRAS.md` (seção 3), e a das pontas de parede nos portais, nova (seção das portas).
- **A face esquerda da parede do BH. SERV. (`PORTAIS_CS["faixas"]`):** do nicho ao portal, a face tinha um traço esverdeado a 1 px dela, que a IA tinha feito ondulado e com um ponto escuro junto ao nicho (de uma linha de 5 px do nicho saindo da parede); a face é refeita com o mesmo contorno das outras, inclusive ao lado do vão de recolhimento (a peça branca grande da parede ali), e fica como está a linha do vidro do box que encosta nela.
- **Como as pontas são refeitas:** o passo roda por último, com os rótulos já no lugar (o alfa deles fica fora da área refeita); o piso por baixo é copiado do piso vizinho, de 6 em 6 px para longe da peça de parede mais perto, só de px de piso (claros, `piso_min`); a parede, das peças cinza do PDF no cinza da final, com o contorno escuro de 1 px; as divisórias de vidro (as outras peças brancas grandes do PDF) e os vidros desenhados na final (cinza frio e claro, `vidro_min`) ficam como estão.
- **Prateleiras do depósito (`PRATELEIRAS_CS`; usuário, com o recorte do Térreo marcado "Usar essa cor padronizada para as prateleiras e armários": "USAR ESSE TOM DE COR PARA PRATELEIRA DO DEPÓSITO. ELA VAI SER PADRÃO PARA OS ARMARIOS E PRATELEIRAS DA CASA A."):** o tom do armário comprido junto ao lavabo do Térreo (a mediana do miolo dele na final do Térreo), RGB 208, 178, 156, ainda numa cor só, sem textura (antes, o cinza quente claro RGB ~195, 191, 186). Regra no `POE642_REGRAS.md` (armários); os outros armários e prateleiras da Casa A, com o OK do usuário.
- **Antes e depois (contra a final de 32959cc):** `renders/POE642_CasaA_PH_Subsolo_1011_{portais_bh_fem_masc,portal_bh_serv,sauna,prateleiras_deposito}_antes_depois.jpg`.
- **Ampliação:** `CORRIGIR_PX` (`ampliacao_a3_casaa.py`) ganhou as seis pontas de parede dos portais e a face do BH. SERV. (a saída do Nano Banana Pro tinha os pés, a face ondulada e o ponto) e as prateleiras do depósito, que vêm da final; a sauna já vinha da final. Refeitos: a entrada da IA (`preparar`), a saída corrigida (`corrigir`, sobre a mesma saída do Nano Banana Pro, job 03df474f), a A3 em 4K (`montar`), o Topaz (High Fidelity V2, 12288 x 9175, job 468ce09b-64e3-4cef-9c4a-6e4a052e95e0) e os JPGs em 12K (`montar12k`).
- **Como refazer:** `python3 cliente_subsolo_casaa_0511.py --antes <a final do Subsolo de c1f7ff5>`; `rodape_entrega.py --no-quadro --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png`; `rotulos_manuscritos_casaa.py`; `pdf_entrega.py`; `book_entrega.py`; e a ampliação como em "O JPG em 12K das duas opções de letra".

### Subsolo: os portais do depósito e do BH. da sauna, e as portas ligadas à ponta da parede (10/11)

- **OK do usuário: "PODE CORRIGIR OS DOIS PORTAIS TAMBÉM":** `PORTAIS_CS["portais"]` ganhou o portal do depósito e o do BH. da sauna, com a mesma limpeza das pontas.
- **"NÃO PODEMOS TER PORTAS "FLUTUANTES", ELAS PRECISAM ESTAR COM A SUA PONTA LIGADA A PONTA DA PAREDE." (`_ligar_folha`):** em todos os portais, a folha da porta (a peça branca grande da ARQ_PAREDE que encosta no marco: a folha das portas de abrir, desenhada aberta a 90°, e a das portas de correr) ligava na parede pelo batente; sem ele, ficava a ~3 px da ponta. A peça branca pequena alinhada com a folha, na ponta dela, passa a ser parte da folha (fica, como ela); e a ponta da parede avança, na espessura dela, até a face de fora da folha (as pontes: BH. SERV. 1190,1–1199,0 x 1034,6–1040,0; BH. FEM. 1494,6–1500,0 x 1499,7–1514,7; BH. MASC. 1859,4–1864,8 x 1499,7–1514,7; depósito 1333,4–1345,3 x 1022,5–1027,9; BH. da sauna 1378,2–1387,1 x 1563,0–1568,4). As guarnições, que formavam o pé, continuam fora. Os vidros desenhados na final ficam até a face da parede (sem o contorno por cima).
- **Ampliação:** `CORRIGIR_PX` ganhou os portais do depósito e do BH. da sauna; Topaz de novo (job 1a3ec854-ee1c-4362-9183-0d58083600a4).
- **Antes e depois (contra a final de 32959cc):** `renders/POE642_CasaA_PH_Subsolo_1011_{portais_bh_fem_masc,portal_bh_serv,portal_deposito,portal_bh_sauna}_antes_depois.jpg`.

- **Depois: vértice com vértice (usuário: "QUERO QUE O VÉRTICE DA PORTA ENCONTRE COM O VÉRTICE DA PAREDE. [...] NÃO ENCOSTE O LADO, MAS SIM O VÉRTICE COM VÉRTICE."):** a ponte da parede vai só até a face de dentro da folha (não mais até a de fora): a quina da folha encontra a quina da ponta da parede e as duas se tocam só no vértice. As pontes: BH. SERV. 1190,1–1199,0 x 1037,0–1040,0; BH. FEM. 1494,6–1497,6 x 1499,7–1514,7; BH. MASC. 1861,8–1864,8 x 1499,7–1514,7; depósito 1333,4–1345,3 x 1024,9–1027,9; BH. da sauna 1378,2–1387,1 x 1565,4–1568,4. Topaz de novo (job 75de5331-92e7-4ef1-8fa6-01f40b3f9685).


### Subsolo: as peças da biblioteca do usuário (`biblioteca_subsolo_casaa_1211.py`, 12/11)

O usuário montou uma biblioteca de objetos da Casa A (PNG com transparência, vista de cima, gerados no Higgsfield; o
pacote veio pelo Google Drive) e pediu: "VEJA NA PASTA O QUE PODEMOS SUBSTITUIR NA PLANTA E GANHAR MAIS REALISMO".
No repositório ficam só a pasta `POE642_CasaA/biblioteca-objetos/01-subsolo`, as duas amostras de
`04-materiais/pisos-internos` (o vinílico da academia), o `LEIA-ME.md` e o `catalogo.json` (o
pacote inteiro, com o Térreo, o 1º Pavimento e os materiais, tem 270 MB e fica fora do git). A proposta (a planta de
hoje ao lado das peças) foi aprovada assim: "1. SIGO COM A SUA RECOMENDAÇÃO. SEM ALTERAR A COMPOSIÇÃO; 2. VASO BRANCO E
DEMAIS RECOMENDAÇÕES; 3. BH SERV. MESMO BATENDO USE OS ITENS DA BIBLIOTECA E SUA RECOMENDAÇÃO PARA O CHUVEIRO QUADRADO;
4. OPÇÃO A; 5. DEPÓSITO: FICA COMO ESTÁ; 6. NÃO MEXA NOS PISOS."

- **Academia (`ACADEMIA`):** esteira-a (2), bicicleta-b (2) e banco-supino, cada um no retângulo do PDF da peça que
  substitui, com o console para a esquerda como no PDF; no supino, a barra alongada até o comprimento do PDF (1,72 m)
  pela repetição de uma coluna da barra e do travessão do rack de cada lado do banco. O vinílico volta exato por baixo
  das peças antigas e da sombra delas: as réguas da final (`renders/POE642_CasaA_PH_Subsolo_vinilico_reguas_academia.png`,
  o piso no alfa) foram refeitas pelo `vinilico_foto.trocar` sobre a final de 7723238 (a de antes do vinílico), com
  diferença zero contra a final; no buraco, as réguas vezes a luz do piso em volta (média normalizada). As peças antigas
  são o que foge do piso esperado perto dos retângulos (até `busca_px`), sem os rótulos da especificação. Sombra curta
  de `final3840_casaa.APARELHOS`. Depois, a pedido do usuário ("VAMOS TER QUE AUMENTAR A DIMENSÃO DAS BICICLETAS POIS
  FICARAM PEQUENAS"; "AUMENTE O SUPINO NA MESMA PROPORCIONALIDADE"; "AUMENTA UM POUQUINHO AS ESTEIRAS / DIMUNUI UM POUCO O
  SUPINO PARA 1,60"), os aparelhos com o retângulo do PDF ampliado em volta do centro (`escala`, ou até a largura
  `largura_m`): as esteiras 1,10 vez (1,60 x 0,70 m para 1,76 x 0,77 m), as bicicletas 1,45 vez (0,85 x 0,35 m para
  1,23 x 0,51 m) e o supino com o banco de 1,60 m (1,35 x 1,72 m para 1,60 x 2,04 m, a barra na mesma proporção).
- **BH. FEM. e BH. MASC.:** a bacia Carrara branca no retângulo do vaso do PDF (o retângulo antes no tom do piso em volta,
  `sob_peca`, sem o marrom na borda), a descarga cromada de novo; a cuba esculpida da biblioteca no retângulo da cuba do
  PDF, fatiada (os cantos e o meio com a torneira na escala da altura, as faixas lisas esticadas), no granito marrom da
  especificação com o sombreado da peça (as bordas chanfradas, a sombra por dentro) e a torneira cromada dela; a bancada
  de travertino bruto fica.
- **BH. SERV.:** a bacia Monte Carlo branca; a bancada no polígono do PDF com o granito da peça `cuba-servico-granito`
  (tecido das faixas só de granito dela), a borda de antes e sem sombra nova; a cuba branca e a torneira da peça no
  retângulo da cuba do PDF (passa da bancada, como no PDF).
- **Chuveiros (antessala, BH. FEM., BH. SERV.):** a placa quadrada da `chuveiro-quadrado` com o braço e a canopla da
  `chuveiro-quadrado-parede`, o braço do comprimento do PDF até a parede; o braço antigo, mais largo, vira o piso do lado.
- **Sauna:** o banco reto de travertino da biblioteca (as pontas na escala, o meio esticado no veio), no tom do banco de
  antes (0,90 do piso; regra de 10/11); a sombra de contato fica.
- **Vinílico da biblioteca (pedido seguinte: "Use o vinílico da biblioteca"):** no piso da academia, a amostra
  `biblioteca-objetos/04-materiais/pisos-internos/madeira-academia-render.png` (7,2 x 4,8 m, 24 fiadas), fiada a fiada,
  cada fiada deslocada ao acaso (semente 1211) e repetida no comprimento, a emenda escurecida como junta
  (`VINILICO_BIB`, `vinilico_biblioteca`), vezes a luz de antes (as sombras e o rodapé ficam). A outra amostra da pasta,
  `madeira-academia.png`, é mais escura.
- **Esquadrias pretas ("As esquadrias dos box, portas de vidro e janelas são pretas"; `ESQUADRIAS`, `esquadrias`):** os
  perfis dos 3 boxes (pelo `FA.boxes` com a face preta), das portas de vidro de `FA.PORTAS_VIDRO` (folhas e batentes),
  dos caixilhos das janelas de `ajustes_casaa.JANELAS` e da porta de correr da circulação para o pátio (a faixa do
  render, duas barras cinza, volta ao piso em espelho; as 2 folhas e os 4 batentes do PDF entram) em preto, com o vidro
  claro por dentro. As portas de giro e o nicho do depósito ficam.
- **Ficam:** os outros pisos, as paredes, os rótulos, o depósito e as prateleiras.
- **Antes e depois:** `renders/POE642_CasaA_PH_Subsolo_1211_{academia,banhos_sauna,bh_serv}_antes_depois.jpg` (contra a
  final de `ANTES_COMMIT`) e `renders/POE642_CasaA_PH_Subsolo_1211b_{academia_vinilico,esquadrias_norte,esquadrias_sul}_antes_depois.jpg`
  (só o vinílico e as esquadrias, contra a final de d35fd16) e `renders/POE642_CasaA_PH_Subsolo_1211c_aparelhos_antes_depois.jpg`
  (os aparelhos maiores, contra a final de b9d8625).
- **Antes e depois (contra a final de 028a12f):** `renders/POE642_CasaA_PH_Subsolo_1211_{academia,banhos_sauna,bh_serv}_antes_depois.jpg`.
- **Como refazer:** `python3 biblioteca_subsolo_casaa_1211.py` (sem `--antes`, parte da final de `ANTES_COMMIT`);
  `rodape_entrega.py --no-quadro --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png`;
  `rotulos_manuscritos_casaa.py`; `pdf_entrega.py`; `book_entrega.py`. O 12K do Subsolo (A e B) e a A3 4K ainda trazem as
  peças antigas: a refazer com `ampliacao_a3_casaa.py corrigir --antes_final` (as peças novas vêm da entrada) e Topaz,
  depois do OK.

### O prompt fotorrealista do Nano Banana Pro (`ampliacao_a3_casaa.PROMPT_FOTO`, 12/11)

Pedido do usuário: "NA HORA DE GERAR O 4K, PRECISO QUE TRAGA REALISMO AOS MATERIAIS. DESCREVA O PROMPT PARA O NANO
BANANA PRO DE FORMA QUE TRAGA O MÁXIMO DE FOTOREALISMO [...] MAS MANTENDO PROPORÇÃO, ESCALA, MATERIAIS E QUALIDADE." O
prompt (em inglês, a língua em que o modelo segue melhor as restrições) tem quatro blocos: (1) a trava: a entrada é o
mapa exato de posição, escala e material, alinhada px a px, nada acrescentado, tirado, girado ou redesenhado, sem texto;
(2) a meta: render de path tracer (qualidade Corona/V-Ray) visto de cima, com iluminação neutra e uniforme, sem luz natural
(usuário: "TEM UM DETALHE NO PROMPT QUE NÃO PODE TER: ILUMINAÇÃO NATURAL"; a 1ª versão pedia luz do dia nublada do alto
à direita, e a IA pôs fachos de luz em diagonal nos banhos), só a física acrescentada (microtextura na escala real, relevo, oclusão nos cantos, sombras de contato curtas,
reflexos leves), sem mudar cor, brilho e contraste; (3) cada material no lugar dele e na escala real (paredes grafite
lisas; vinílico de carvalho claro em fiadas de 20 cm na horizontal, com a régua "a largura de uma esteira cobre umas 4
fiadas"; os aparelhos; Bege Bahia sem juntas; travertino bruto; louças, metais, granito marrom das cubas; vidros com
perfil preto fino; prateleiras; elevador; escada; grama na escala); (4) o que evitar (perspectiva, efeitos de lente,
grão, ar de ilustração, mudança de tom, linhas tortas, peças a mais ou a menos, juntas onde não há).

**A rodada (12/11, "APROVADO. VAMOS VER COMO FICA"):** `preparar` (a entrada sem textos, com a academia nova); Nano Banana
Pro 4K 4:3 com `PROMPT_FOTO`, duas variações por vez. Com o prompt da luz do dia (jobs 11e7ffdd-7173-40ba-ab44-4da65c3c895d
e 06ca9535-d4f4-4de4-904d-bf46a028ebcb), materiais bem mais reais, mas fachos de luz, sombra em volta da casa e trechos
redesenhados (um ambiente novo fora da casa, o depósito virando outro ambiente). Com o prompt sem luz natural (jobs
29e35837-a5f3-441d-b643-5047121d1429 e 7320ac0b-7eda-45c0-a04b-d7573c0816b8): luz uniforme, nada fora da casa; a 2ª
ainda dividiu o depósito em ambientes; a 1ª manteve a planta (só o elevador e os shafts escureceram e o supino e as
bicicletas mudaram de desenho). Ficou a 29e35837 (a saída bruta fica fora do git; a corrigida é
`renders/POE642_CasaA_PH_Subsolo_A3_saida_nano_banana_pro.png`), com
`corrigir --estrutura` (`ESTRUTURA`, `mascara_estrutura`): onde a estrutura (passa-banda) foge mais que 7, crescido 3 px,
mais os aparelhos inteiros, a escada e os buracos pequenos da máscara, vem da entrada (21,9% da casa: paredes, portas,
vidros, louças, bancadas, peças); antes de juntar, os tons da IA casados com os da entrada (sem isso, a borda da máscara
virava um contorno claro ondulado). Da IA ficam os pisos (vinílico, Bege Bahia, travertino) e a grama, nos tons da final.
O fundo fora da planta volta ao branco no `montar`. Depois, Topaz High Fidelity V2 a 12288 x 9175 (job
559ee4dc-750a-47e9-9b89-ebce22d49e71, fora do git) e `montar12k` (A e B).

### Os defeitos do Subsolo de 12/11 (no `biblioteca_subsolo_casaa_1211.py`, depois das peças)

Recortes do usuário (do 12K B): a parede de baixo do hall com uma linha clara embaixo; "OS X PRECISAM SER EM CINZA COM
TRAÇOS MAIS FINOS E DELICADOS. ALÉM DISSO, LIMPE RESÍDUOS DE SUJEIRA" (elevador e shafts); "DEIXAR O CONTORNO EM VOLTA
DOS VASOS PERFEITOS." (BH. FEM., BH. MASC.); "DEIXAR AS PAREDES RETAS" (a parede entre a academia e os banhos). Ordem no
`aplicar`: peças, esquadrias, `paredes_retas` (as peças desta rodada protegidas), `sujeira`, shafts.

- **Paredes retas (`PAREDES_RETAS`, `paredes_retas`):** a parede é o cinza 80 da própria final, só perto das paredes do PDF
  (os aparelhos e os rótulos têm o mesmo cinza); fechamento e abertura 3x3 (entalhes de até 2 px viram parede; pontas
  saem); na faixa de 3 px em volta, o que é cor de parede ou linha neutra clara (por dentro, só a mais clara que o piso em
  15; por fora, tudo o que não é branco) vira o que está a 5 px na normal (o piso; fora da casa, o branco) — some a linha
  clara sob a parede do hall; por último a aresta: nos 2 px junto à parede, o pixel que foge mais que 28 da mediana de 7
  vizinhos ao longo da parede vira a mediana (os pontinhos claros e as falhas da borda). Ficam o preto das esquadrias e o
  elevador.
- **Sujeira (`SUJEIRA_PX`, `sujeira`):** as manchas na caixa (1832, 1502)-(1857, 1520), junto à parede da academia,
  refeitas pelo piso em volta (inpaint).
- **Shafts (`SHAFTS_X`, `segs_shaft`, `miolos_shafts`, `desenhar_shafts`):** o miolo de cada shaft (o maior pedaço que não
  é parede e não toca a borda da caixa do PDF) em branco e os traços do PDF (DOC_LINHAS E PROJEÇÕES, o tracejado dele) em
  cinza 128, 0,8 px, antisserrilhados (8x). A ampliação (`ampliacao_a3_casaa.montar` e `montar_grande`) desenha o mesmo X
  na escala dela (`desenhar_shafts(img, miolos, s, X0, Ya3)`), em vez de copiar o miolo da entrada ampliada.
- **Vasos (`BANHOS_BIB["vasos"][...]["fonte"]`, `sob_peca`, `costura`):** o retângulo do vaso antigo, que ia num tom
  chapado (o retângulo claro em volta da bacia), recebe o piso de verdade: BH. FEM. o piso logo à direita (`dir`), BH.
  MASC. cada metade espelhada do seu lado (`espelho`), BH. SERV. o de cima (`cima`); o que não é piso no trecho copiado
  (o vidro do box, um cromado: desvio > 24 da mediana ou azulado) sai por inpaint; `costura` casa o tom com as bordas
  (a diferença para o piso de fora, esquerda/direita e cima/baixo, em rampa por dentro; a parede não conta). Na
  ampliação, `VASOS_IA` e `rampa_vasos`: a IA foi feita com o retângulo chapado (e desenhou a bacia antiga maior); o
  trecho que vem da entrada (`MUDOU`) entra com uma rampa de 6 px para fora do retângulo, sem a borda reta à vista no 12K.

**A rodada:** `python3 biblioteca_subsolo_casaa_1211.py` (a final e os antes/depois de 1211); `preparar`; `corrigir
<saída bruta 29e35837> ../renders/POE642_CasaA_PH_Subsolo_A3_saida_nano_banana_pro.png --estrutura --antes_final <a final
de d19082d>`; `montar`; Topaz High Fidelity V2 12288 x 9175 (job 67888e24-f5a8-4f88-a21c-ae0d174feaff, fora do git);
`montar12k`; `rodape_entrega.py --no-quadro --render Subsolo=...`, `rotulos_manuscritos_casaa.py`, `pdf_entrega.py`,
`book_entrega.py`.

### As mesmas regras no Térreo e no 1º Pavimento: `regras_1211_casaa.py` (12/11)

Usuário: "PODE APLICAR NO TÉRREO E 1º PAVIMENTO DA CASA A" (o X cinza fino dos shafts, as paredes retas e o contorno dos
vasos, como no Subsolo). Sobre a final de cada pavimento (a de 1415b75):

- **Shafts (`SHAFTS`, `vaos_shafts`, `desenhar_x`):** no 1º Pavimento, os 4 vãos de `um_pav_casaa_1111.SHAFTS_1P` (o de
  cima, o junto ao elevador e os dois da suíte master; o X ia em cinza 60); no Térreo, o vão do shaft junto ao elevador,
  achado na final dentro da caixa do PDF (`revisao_casaa_2910.ELEVADOR_TA["shafts_pt"]["Terreo"]`, paredes no cinza 53;
  o fundo era rosado e o X escuro). O vão no claro (246) e o X de canto a canto em cinza 128, 0,8 px, tracejado 3,4/2,2
  px, simétrico (um traço cruza o centro). A claraboia do lavabo e os vazios seguem com o X fino da regra de 10/11.
  A borda de parede em volta de cada vão (`limpar_aro`, 1,5 px): em cada lado e a cada distância da beira, o px cinza
  que foge mais de 12 da mediana da faixa volta a ela (no 1º Pavimento havia um risco claro na beira de cima do shaft
  de cima e dois pontinhos claros nos cantos de baixo, que no 12K viravam pontos brancos); o mesmo no 12K.
- **Paredes retas (`PAREDES`; `biblioteca_subsolo_casaa_1211.paredes_retas` com os parâmetros do pavimento):** no Térreo,
  o cinza 53 (tolerância 14) e o preto das esquadrias abaixo de 35; no 1º Pavimento, o 80 do Subsolo. Duas proteções
  novas, achadas no primeiro teste: o que o PDF desenha e não é parede (`OBJETOS`, `objetos_pdf`: louças, mobiliário,
  elementos fixos, bancadas, marcenaria, layout, escadas, pilares; e as folhas e esquadrias da ARQ_PAREDE fora do cinza das
  paredes) fica de fora (a 1ª versão apagava a grelha da churrasqueira, a borda das geladeiras junto ao pilar e trechos
  das folhas das portas); e `fora_fundo`: só o branco ligado à borda da imagem é o lado de fora (no 1º Pavimento, o
  vidro branco do vazio da escada em U tinha a borda comida como se fosse o fundo). No Térreo, os muros do lote perdem a
  franja clara do antisserrilhado e os pontos brancos junto às paredes saem; no 1º Pavimento, pouca coisa (as paredes já
  estavam limpas).
- **Vasos (`VASOS`, `vasos`):** os vasos dos dois pavimentos não tinham o retângulo chapado do Subsolo; o que havia era o
  ponto claro na beira do vaso do lavabo do Térreo, junto à parede: nos vasos escuros, o px claro na beira junto à
  parede é refeito pelo entorno (inpaint); e a mancha clara pequena no miolo da louça (até `miolo_max_px` 40 px, sem
  encostar na caixa: o ponto cinza de 4x4 px junto à parede e um ponto solto no vaso do lavabo).

- **Claraboia sem o X (`CLARABOIA`, `claraboia_sai`, `claraboia`; usuário: "Na claraboia não precisa do X, apenas os
  traços na horizontal"):** na caixa da claraboia do lavabo do Térreo, a camada dos tracejados finos do 12K
  (`renders/POE642_CasaA_PH_Terreo_12K_tracejados.png`) mantém só a linha horizontal (as linhas com traço em ao menos
  25% da largura da caixa); o resto (as diagonais, o X do meio e os resíduos junto às faces das paredes) sai. Na final,
  o piso por baixo do que saiu volta da entrada da IA do 12K (fora dos traços, idêntica à final), fora das faces das
  paredes; no 12K, `montar12k` zera esses traços na camada. Passo final de `aplicar` no Térreo.

**O 12K (A e B), sem IA nova:** `regras_1211_casaa.py <pav> --entrada12k <cópia da entrada de antes>` grava a final e
passa à entrada da IA do 12K o que mudou na final (fora dos textos e tracejados que a entrada não tem). Térreo: a saída
corrigida da IA (`renders/POE642_CasaA_PH_Terreo_12K_saida_nano_banana_pro.png`) remendada onde a entrada mudou
(`--remendar <corrigida de antes> <destino> <entrada de antes>`); 1º Pavimento: a saída da IA (job 09c2bb19) corrigida de
novo (`ampliacao_12k_1pav_casaa.py corrigir <saída> <corrigida> --entrada_antes <a entrada que a IA viu, de 036e633>`).
Topaz High Fidelity V2 a 12288 x 6858 (Térreo: job 3272a7a5-ae57-4ef0-aa97-a4ea957d79d3; 1º Pavimento: job
24b977d2-82f2-4189-ad27-07fbfc776183; fora do git); `montar12k --opcao AB`, que agora desenha os shafts direto no 12K
(`regras_1211_casaa.shafts_12k`: o mesmo X e a mesma borda limpa, na escala do 12K) e refaz o vaso do lavabo do
Térreo (`vasos_12k`, `DOZE["vasos_entrada"]`: a IA tinha borrado a borda esquerda da bacia em pinceladas e deixado
pontinhos claros na face da parede): o vaso, o trecho até a parede e uma faixa de 5 px junto à face da parede, do alto
do lavabo até 15 px abaixo do vaso, com a final sem textos ampliada; o contorno liso pela cobertura do vaso sobre o
piso (a projeção de cada px no eixo piso -> vaso, ampliada em cúbico, suavizada e recortada) entre a camada da louça e
a do piso; antes dos tracejados e dos textos. Na mesma faixa os tracejados finos não entram (a camada
`..._12K_tracejados.png` tinha resíduos na sombra da face da parede, que viravam quadradinhos claros). Depois `rodape_entrega.py --no-quadro --render
Terreo=...` e `--render 1Pavimento=...`, `pdf_entrega.py` e `book_entrega.py`. Antes e depois em
`renders/POE642_CasaA_PH_{Terreo,1Pavimento}_1211_*_antes_depois.jpg`.

### As peças da biblioteca no Térreo: `biblioteca_terreo_casaa_1211.py` (12/11)

**Pedido:** "eu também quero que você me faça a proposta para substituição dos elementos, né, baseado na biblioteca de
objetos. Vamos concentrar os esforços agora na planta do térreo"; a proposta (`renders/POE642_CasaA_PH_Terreo_1211_proposta_biblioteca_{1,2,3}.jpg`)
aprovada com "OK"; depois "NÃO ALTERE OS CARROS. DEXE COMO ESTAR." (a garagem fica como estava), "PRECISA DIMINUIR O
TAMANHO DA CHURRASQUEIRA PARA CABER NA BANCADA SEM FICAR POR CIMA DA PAREDE." e "AS BANQUETAS FICAM PARCIALMENTE POR
DEBAIXO DA BANCADA, NÃO SOBRE ELAS.". Os vasos sanitários ficam marrons (o usuário não escolheu o branco da biblioteca).

**Como foi feito:** a biblioteca (`biblioteca-objetos/02-terreo`, PNG vistos de cima com transparência; no git só as 41
peças usadas; o pacote inteiro vem do Drive, fora do git) entra peça a peça no lugar da antiga, sem mudar a composição:
centro, tamanho e giro do PDF (caixas das camadas ARQ_MOBILIÁRIO, ARQ_LAYOUT HUMANIZAÇÃO e ARQ_LOUÇAS E METAIS, e as
poses das poltronas das rodadas anteriores) ou da peça da final onde ela diverge do PDF. `AMBIENTES` lista, por
ambiente, as zonas a refazer (`ret`, `disco`, `rot`, `pol`, `pdf` = o preenchimento do PDF numa caixa mais a folga,
`polt` = a pegada das poltronas), as fontes do piso, o que fica (`manter`) e as peças `(png, cx, cy, wt, ht, ang,
sombra, corte)`. Em `aplicar`: (1) a pegada das peças antigas, com a sombra, volta ao piso de cada lugar
(`pedidos_terreo_casaa_2910.piso_refeito`; o tapete da varanda pelo `tecido`, no tom do anel do tapete, com a sombra da
borda); (2) as peças novas, renderizadas a 4x e reduzidas, com a sombra curta (`SOMBRAS`: móvel, mesa, baixa, tapete);
cadeiras e banquetas cortadas pela borda da mesa ou da bancada (`corte`); (3) as plantas em vaso de volta por cima, com
a sombra (`plantas_de_volta`); (4) a beira clara da churrasqueira antiga junto à parede no tom da bancada
(`beira_da_churrasqueira`); (5) os tracejados finos da camada do 12K de volta nas zonas. Ambientes: estar da varanda
(sofá curvo externo, tapete, poltronas, mesinhas), sala de estar (sofá curvo, tapete redondo, poltronas, mesas de apoio),
estar sob a projeção (poltronas), as duas mesas redondas e o jantar (cadeiras da biblioteca), escritório (mesa, cadeira,
poltrona), gourmet e cozinha (banquetas, cooktops de 4 bocas, grelha, cubas inox Franke, tanques), lounge dos brises
(poltronas, bancos), piscina (espreguiçadeiras no polígono do PDF), banhos (chuveiros com braço, bacia Monte Carlo, cuba
compacta só a louça, cama de solteiro do motorista) e lavabo (cuba esculpida). A garagem e os carros não mudam.

**Desvios da proposta (a confirmar com o usuário):** a pia da cozinha com duas cubas inox simples (`cuba-franke-inox-link`)
no lugar da cuba dupla, para manter as duas bacias do desenho; a cuba compacta do banho só com a louça (`so_louca`), no
granito que já estava; os cooktops de 60 cm, 4 bocas, no lugar dos antigos.

**O 12K (A e B):** `montar12k` chama `pecas_12k` depois de `vasos_12k`: nas zonas refeitas (`renders/POE642_CasaA_PH_Terreo_12K_biblioteca_zona.png`:
azul a zona, verde o que fica; o registro das peças em `..._12K_biblioteca.json`), a final ampliada sobre a saída da
IA (o tapete inteiro da varanda e as plantas inteiras vêm da final), e as peças desenhadas nítidas na escala do 12K,
direto dos PNG. Nas bancadas onde saíram a grelha e os cooktops antigos, o próprio granito da saída da IA, tecido e no tom
do entorno (`bancadas_12k`), e a beira da grelha antiga limpa também no 12K (`beira_da_churrasqueira_12k`). A entrada da
IA não muda (a correção de tom usa a entrada que a IA viu). Sem IA nova (Topaz 3272a7a5).

**Como refazer:** depois de `regras_1211_casaa.py Terreo`, `python3 biblioteca_terreo_casaa_1211.py` (parte da final de
`ANTES_COMMIT` = baf4362; sem `--saida` grava a final, o registro do 12K e os antes e depois
`renders/POE642_CasaA_PH_Terreo_1211b_<ambiente>_antes_depois.jpg`); depois `ampliacao_12k_terreo_casaa.py montar12k
<saída do Topaz> --opcao AB`, `rodape_entrega.py --no-quadro --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_rotulos.png`,
`pdf_entrega.py` e `book_entrega.py`.

### Térreo: os pedidos de 12/11 à noite (`pedidos_terreo_casaa_1211c.py`, `bege_pergolado_casaa_1211.py`)

Vendo a planta com as peças da biblioteca, o usuário mandou, cada um com um recorte (aplicados direto):
- **Sofá da sala** ("DIMUNUIR O TAMANHO DO SOFÁ"; "TALVEZ ROTACIONANDO O SOFÁ, RESOLVA"; no `biblioteca_terreo_casaa_1211.py`):
  o sofá curvo da biblioteca era maior que o do PDF (65% de sobreposição com o contorno dele). O giro, o tamanho e o
  centro de maior sobreposição (87%): 15° no sentido horário, 186 px (era 206, 10% menor), centro (1982, 443). A pegada
  do sofá de antes também volta ao piso (a forma `peca` de `mascara_formas`), senão o sofá antigo do render aparecia.
- **Bege Bahia do pergolado** ("PRECISAMOS MELHORAR O ASPECTO DO MARMORE BEGE BAHIA NESSA REGIÃO"; `bege_pergolado_casaa_1211.py`):
  sob o pergolado, junto à prainha, o Bege tinha saído acinzentado e rosado, com manchas brancas (o refazimento de 10/11
  emendava o tecido ao piso de fora pela membrana, e as bordas no travertino da varanda e do lounge puxavam o tom). O
  Bege (o cinza 232 da chapada) de dentro do pergolado e a faixa entre a prainha e a linha do guarda-corpo, tecido do
  deck bom (`fontes_px`), emendado só ao Bege bom de fora (a água, a linha e o travertino com a borda livre); os
  tracejados de volta por cima. No 12K (`pergolado_12k`): o tecido do deck da própria saída da IA, com a correção de tom
  calculada na escala da final e ampliada.
- **Riscos entre os brises** ("REMOVA ESSES RISCOS PRETOS ENTE OS BRISES"; `brises`): as seis marquinhas na linha do
  guarda-corpo, entre os brises do lounge (na final, cinza-claras; no 12K, traços pretos), saem: cada coluna da caixa
  entre a linha de cima e a de baixo (a linha vertical continua); no 12K, com o grão do piso de volta.
- **Porta do banho varanda** ("CORRIJA ESSA PORTA."; `porta`): a folha borrada (uma barra rosada larga) sai, o piso de
  baixo é tecido do de logo abaixo, e a folha entra nítida no retângulo do PDF (ARQ_PAREDE, 1617,0–1670,7 x
  1545,1–1547,5, aberta junto à parede da esquerda), no desenho das portas do Térreo (o cinza claro 222, a face 92 e a
  sombra curta); no 12K, a folha em 8x na escala dele.
- **Contorno do deck e da escada** ("CORRIJA ESSE CONTORNO DO DECK E ESCADAS"; `deck`): no PDF, o deck de madeira e a
  escada para o Subsolo terminam na mesma reta (y 1130); a última régua tinha uma faixa clara com tracinhos e a borda
  ondulava. O deck vai até a reta com a régua de cima (12 px acima; no 12K, o passo medido pela autocorrelação, 43 px),
  a escada com os degraus de logo acima e a beira um tom abaixo, e o gramado começa logo abaixo (o próprio gramado,
  refletido na borda dele).
- **Rótulo do JARDIM** ("DIMINUA A FONTE PARA CABER NO VÃO, SEM ENCOSTAR NAS BORDAS."; `jardim`): o JARDIM A: 17,46 m²,
  entre as linhas da floreira (25 px), no corpo 0,9 (antes 1,3): 39 x 17 px, no meio da faixa, no mesmo centro na
  horizontal; o fundo é a floreira de 70 px à esquerda (as linhas continuam), e o "17,46" com a vírgula dos outros. O
  desenho vai aos dados do 12K (`..._12K_dados.json`, com o de antes em `_antes`); no 12K, a mancha que a IA fez sob o
  rótulo antigo sai com a floreira de 72 px à esquerda (`jardim_12k`).
- **Rótulo da claraboia** ("ESCREVA O RÓTULO DA CLARABOIA DENTRO DO ESPAÇO DESTINADO PARA CLARABOIA, COM UMA FONTE MAIS
  REDUZIDA. ELA FICA DENTRO DO TRACEJADO E PAREDE DA JANELA"; `claraboia`): o CLARABOIA, que ficava abaixo do tracejado,
  sai (o piso do lavabo ao lado, `terreo_casaa_1011._tapar_rotulo`) e volta no corpo 0,9, no meio do trecho livre da
  claraboia (entre a face da janela, y 356, e o tracejado, y 383, à esquerda da bacia); o desenho vai aos dados do 12K
  e ao `..._rotulos_lavabo.json`.
- **Bancada do lavabo** ("A BANCADA É NO MESMO TOM DA CUBA ESCULPIDA. CORRIJA"; `bancada`): a pedra abaixo da cuba
  (ARQ_BANCADAS) no tom da cuba esculpida: o fator do tom mediano da borda da cuba sobre o da pedra, px a px (o desenho,
  a luz e o contorno da pedra ficam); no 12K, o mesmo com os tons do 12K.
- **Vaso do lavabo** ("MELHORE A REPRESENTAÇÃO DESSE VASO"; no `biblioteca_terreo_casaa_1211.py`): o bloco marrom
  chapado sai (o piso do lavabo de logo abaixo) e entra a bacia Carrara da biblioteca (`02-terreo/lavabo/bacia-carrara.png`)
  no retângulo do PDF (a caixa acoplada junto à parede, a frente para a esquerda), no marrom-escuro dos vasos do Térreo
  (`marrom`: o branco da peça levado à faixa 0,80–1,22 do tom, com as linhas da tampa e da caixa reforçadas). Na
  camada dos tracejados, os resíduos do X da claraboia não voltam (`regras_1211_casaa.claraboia_sai`).

- **Rótulos da caracol e da GARAGEM** ("COLOCA ESSE RÓTULO ACIMA DA ESCADA"; "COLOCA ESSE RÓTULO MAIS PARA DIREITA OU
  DIMINUA O TAMANHO DA FONTE"; `caracol`, `garagem`): o SOBE PARA O 1º PAVIMENTO da caracol da área de serviço, que ficava
  à esquerda dela, centrado acima dela (no piso livre entre as máquinas e o topo da escada; a anotação nos dados do
  12K); o GARAGEM, espremido entre a parede e o carro do meio, no mesmo corpo, à direita, sobre o vão entre o carro do
  meio e o da direita (~20 px de cada carro, 13 px da ponta da parede; os carros não mudam); o fundo de antes é o mesmo
  trecho 95 px à esquerda (a parede reta continua). No 12K, a IA já tinha o piso limpo sob os dois.
- **Guarda-corpo do deck** ("CORRIJA ESSE GUARDA CORPO"; `guarda_corpo`): na borda de cima do deck, junto ao gramado, a
  barra cinza com os pontinhos escuros sai (a faixa volta ao piso de 10 px abaixo) e entra a lâmina de vidro do PDF
  (ARQ_ELEMENTOS FIXOS, 1082,6–1590,1 x 337,8–339,3) no desenho das guardas do Térreo (`vidro_ret`, o mesmo de
  `terreo_casaa_1011.vidro_laminas`, com os números da escada do jardim), na final e no 12K.
- **Soleira da janela do escritório** ("FALTOU A SOLEIRA DE UM DOS LADOS DA JANELA"; `soleira`): na janela de canto, o
  vão da direita (ARQ_PAREDE, 2593,2–2605,2 x 355,2–429,1) mostrava o gramado; entra a soleira da janela de cima,
  girada (a face de fora junto ao gramado), tirada da própria imagem (na final e no 12K, cada um com a sua de cima).

- **Folha do box do B. MOTORISTA** ("DEIXE RETO A FOLHA DO BOX. ESTÁ MUITO TORTO"; `box`): a linha de vidro tinha um
  degrau no meio e um puxador torto (na final) e saía inclinada e quebrada no 12K. A faixa volta ao piso do box (9 px à
  esquerda, a emenda da direita esfumada) e a folha entra reta, de parede a parede (y 1216–1305,6), no eixo das duas
  folhas de correr do PDF (ARQ_LOUÇAS E METAIS, x 2297,65), no desenho do vidro do box do banho varanda (a face cinza,
  o vidro claro e a face cinza, 1 px da final cada, com um halo leve), na final e no 12K.

- **S e D das escadas** ("ADICIONE AS ESCADAS O "S" OU "D" DE SUBIR OU DESCER, LOGO ABAIXO DA SETA"; `letras`): o D
  (os degraus que descem para o deck e a escada para o Subsolo) e o S (a escada do jardim e a caracol) centrados sob o
  triângulo de cada escada, 2,5 px abaixo da ponta de baixo, no corpo (11 px) e na cor (45) das descrições; nos dados
  do 12K como anotações "txt" (refeitas a cada rodada: as de antes saem antes). A seta da entrada não é escada.
- **S e D no Subsolo e no 1º Pavimento** ("APLIQUE O S E D NO SUBSOLO E 1º PAVIMENTO"; `letras_escadas_casaa_1211.py
  <Subsolo|1Pavimento>`, da final de `ANTES_COMMIT` = f37669e): no Subsolo, o S sob a seta do SOBE PARA O DECK, na
  fonte, no corpo (17 px) e na cor da descrição: a última camada de `ampliacao_a3_casaa.escada_camadas`
  (`cliente_subsolo_casaa_0511.ESCADA_CS["letra"]`), que a final, a A3 4K, o 12K A e a retirada dos textos usam; na
  Kalam (`letra_kalam`), na manuscrita e no 12K B. No 1º Pavimento, o D sob a seta da escada em U (DESCE PARA O HALL
  INTERNO) e da caracol (DESCE PARA A ÁREA DE SERVIÇO), como as do Térreo (anotações "txt" nos dados do 12K do
  1º Pavimento). Depois: `rotulos_manuscritos_casaa.py Subsolo`, as pranchas, `ampliacao_a3_casaa.py montar
  ../renders/POE642_CasaA_PH_Subsolo_A3_saida_nano_banana_pro.png` e `montar12k <Topaz 67888e24>`,
  `ampliacao_12k_1pav_casaa.py montar12k <Topaz 24b977d2> --opcao AB`, PDF e book.

**Como refazer:** `regras_1211_casaa.py Terreo`, `biblioteca_terreo_casaa_1211.py` (a final, do commit `ANTES_COMMIT`),
`pedidos_terreo_casaa_1211c.py --antes_depois <a final de 2c1c21d>` (lê a final que o anterior gravou; os antes e depois
em `renders/POE642_CasaA_PH_Terreo_1211c_<pedido>_antes_depois.jpg`); o 12K pelo `montar12k` (que chama
`pedidos_terreo_casaa_1211c.doze` depois do `pecas_12k`); depois prancha, PDF e book. Atenção: o `preparar` do 12K acha
os rótulos da final pelas buscas de corpo; o JARDIM no corpo 0,9 fica gravado direto nos dados.

### As peças da biblioteca no 1º Pavimento: `biblioteca_1pav_casaa_1211.py` (12/11)

**Pedido:** "Vamos revisar os mobiliários do 1° pavimento da casa A"; a proposta
(`renders/POE642_CasaA_PH_1Pavimento_1211_proposta_biblioteca_{1,2,3}.jpg`) aprovada com "OK, pode aplicar as
recomendadas". Nas perguntas abertas, o recomendado: as camas da biblioteca (A, creme) no lugar das de manta bordô; os
vasos sanitários brancos (bacia Carrara); os closets como estão (os cabides).

**Como foi feito:** a biblioteca `biblioteca-objetos/03-primeiro-pavimento` (no git, a pasta inteira, 43 PNG) entra
peça a peça no retângulo da peça do PDF (o centro, o tamanho e o giro dele), com `pousar`, `preparar` e as sombras do
Térreo (`biblioteca_terreo_casaa_1211`). `AMBIENTES`: por ambiente, as zonas (retângulos da pegada das antigas com a
folga da sombra), o que fica (`manter`: as cadeiras de madeira e linho, o rack da TV da suíte 3, as mesinhas
redondas da suíte master e da suíte 2) e o que volta recortado por cima (`recolar`: a mesa de centro de nogueira da
sala íntima, o banco aos pés da cama king, o laptop da suíte 1, a TV da suíte 2). Os rótulos e as anotações (dados do
12K) não são refeitos nem cobertos.
- **O piso por baixo (`piso_de_volta`):** na planta-base os móveis e os tapetes são brancos; cada px da zona fora dos
  tapetes que ficam (`TAPETES_FICAM`: os das suítes 1, 2 e 3) leva o material do piso mais perto (vinílico,
  travertino ou Bege Bahia). Vinílico e travertino saem do próprio gerador (`um_pav_casaa_1111.pisos_1111e`, com a zona
  marcada no material numa cópia da planta-base, `forcar_px` nas caixas da zona e a luz do entorno por baixo, inpaint):
  a mesma semente e a mesma paginação, as réguas continuam. O Bege Bahia (banho e quarto de serviço) e os tapetes que
  ficam, do tecido do próprio material (`PT.piso_refeito`, fontes no mesmo tom, `fontes_auto`).
- **As peças:** sala íntima (sofá em L A, espelhado na antidiagonal para o L do PDF; poltrona A; 3 mesas laterais;
  tapete; vaso de folhagem); suíte master (cama king A, 2 criados, poltrona, pufe no lugar do pufe antigo, tapete);
  suíte 1 (2 camas de solteiro A, 3 criados, a bancada da escrivaninha); suíte 2 (cama de casal A, 2 criados
  retangulares como no PDF, a bancada do rack, a poltrona A); suíte 3 (cama de casal A, 2 criados redondos, a bancada
  da escrivaninha); quarto de serviço (cama de solteiro A); banho master (bancada dupla esculpida do render, banheira
  oval A com o misturador de piso no lugar do PDF, bacia Carrara, 2 chuveiros quadrados, a floreira de cactos e
  folhagem); banhos 1, 2 e 3 (cuba esculpida em travertino na bancada do PDF, `cuba_na_bancada`: a cuba no lugar do
  PDF, só os lados lisos esticados, `MIOLO_CUBA`; bacia Carrara; chuveiro quadrado com o braço até a parede); banho
  de serviço (cuba no granito na bancada do PDF, bacia Monte Carlo, chuveiro redondo). Os closets e as mesinhas
  redondas ficam.
- **O 12K (A e B):** `montar12k` chama `pecas_12k` no 1º Pavimento: a final ampliada na zona refeita sobre a saída da IA
  e as peças nítidas dos PNG (registro em `renders/POE642_CasaA_PH_1Pavimento_12K_biblioteca.json` e
  `..._12K_biblioteca_zona.png`). Sem IA nova (Topaz 24b977d2).

**Revisão das poltronas (12/11, "Revisão de poltronas e rotação necessária"):** todos os PNG da biblioteca têm a
frente para baixo (`girar_pt`); a frente de cada poltrona é a do símbolo do PDF (o encosto é o lado das linhas grossas;
a frente, a borda reta do assento ou a linha entre os pés da frente). No 1º Pavimento, a da sala íntima e a da suíte
master estavam ~120° fora: as duas a -150° (a normal da borda reta do assento: para a mesa de centro e para o pufe);
a da suíte 2 estava certa. No Térreo, a creme da sala de estar a -56° (a linha entre os pés da frente; era -72,5°, a
pose de 29/10); as oliva, as 4 caramelo (para a mesinha do meio), a dos brises e a de leitura estavam certas; as da
varanda não têm símbolo no PDF (as poses de 29/10). Antes e depois em
`renders/POE642_CasaA_PH_{Terreo,1Pavimento}_1211_poltronas_antes_depois.jpg`.

**Mesas laterais da sala íntima (12/11, "Tem mesa redonda sobre o sofá, em vez de estar ao redor"):** o sofá em L da
biblioteca é mais fundo que o do PDF (a chaise até y 1022, o braço desde x 2111), e as duas mesas laterais, no lugar
do PDF, caíam sobre ele; vão ao lado: à esquerda da chaise, no tapete (2044, 992), e por fora do braço, junto à ponta
da mesa de centro (2100, 1140). A terceira, ao lado da poltrona, fica. No 12K, os recortes do que fica (`recolar`: a mesa de
centro, o banco, o laptop, a TV) entram no registro e voltam por cima das peças nítidas (antes, o tapete novo desenhado
no 12K cobria a mesa de centro e o banco), recortados da final de `ANTES_COMMIT` e ampliados em Lanczos; o laptop e a
TV pelo retângulo exato da peça (`cheio`, a TV pelo escuro, `escuro`), sem a sombra e o tampo antigos em volta.

**Criados das suítes (12/11, "Melhore a representação dos criados das suítes"):** os criados retangulares da biblioteca
saíam no tom do vinílico e sumiam no piso; vão ao tom da madeira das bancadas das suítes (`TOM_BANCADA`, a mediana do
`bancada-suites`, com o veio do criado: `tom_bancada`), com a sombra de volume (`movel`); os redondos da suíte 3 num
círculo de 0,60 m, como no PDF (o PNG não é quadrado e saía oval); e um abajur visto de cima em cada criado
(`abajur`, `ABAJUR`, `"abajures"` por ambiente: a cúpula de linho com a borda fina, o miolo aceso em âmbar claro, a luz
no meio e a sombra curta), desenhado em 8x e, no 12K, na escala dele (nítido). Antes e depois em
`renders/POE642_CasaA_PH_1Pavimento_1211_criados_antes_depois.jpg`. Junto, o piso ao lado das camas: na planta-base, partes dos móveis e
os tapetes usam o mesmo cinza 232 do Bege Bahia, e o px junto da cama ia para o tecido do Bege (saía uma faixa clara
em degrau ao lado da cama); o Bege agora é só o dos ambientes de serviço (`BEGE_AMBIENTES`, `_bege_piso`), e a luz
por baixo do vinílico refeito vem só do piso de verdade em volta (a cama antiga sobre o tapete também é apagada no
inpaint). No 12K, a pegada das peças antigas sobre os tapetes que ficam é o tecido do próprio tapete da IA
(`tapetes_12k`, no tom dele; a final ampliada era lisa e clara ao lado da trama da IA). Na suíte 3, a zona vai até o
banco (y 486): o pé da cama antiga passava do retângulo do PDF e ficava uma faixa branca.

**Bancos de pé de cama (12/11, "NÃO TEMOS NA BIBLIOTECA OS BANCOS QUE FICAM NA FRENTE DAS CAMAS?" / "GERE UM BANCO NOVO
NO HIGGSFIELD"):** a biblioteca não tinha o banco; gerado no Higgsfield (gpt_image_2, 2k, 4 variantes: jobs d25a4b71,
17b88afb, 5b12574e e 90c387c0; escolhida a d25a4b71: duas almofadas de linho cru numa moldura fina de carvalho, visto de cima)
e recortado do fundo branco: `biblioteca-objetos/03-primeiro-pavimento/suite-master/banco-pe-de-cama.png` e, para as
camas de solteiro, `suite-1/banco-pe-de-cama-solteiro.png` (uma almofada só: a metade esquerda até a costura do
meio, mais a ponta direita da moldura). No retângulo do PDF aos pés de cada cama: suíte master (1506, 1308; 95,5 x 23,9 px), suíte 2 (1765,5,
1072) e suíte 3 (1742, 488), e um banco de solteiro (53,7 x 17,9 px) aos pés de cada cama da suíte 1 (2338 e 2443,
1439), com a sombra de volume (`movel`). O banco antigo da master (antes recortado da final, `recolar`) sai; as zonas
das suítes 1, 2 e 3 cobrem o banco antigo com a sombra dele (uns 10 px a mais do lado da sombra; na suíte 3, de x 1666 a
1810 e até y 522, com a linha de sombra do pé da cama antiga), que dá lugar ao vinílico refeito.

**Floreira do banho master (12/11, "VAMOS ALTERAR ESSA VEGETAÇÃO MAIS ALTA POR" + a foto de espadas-de-são-jorge e
folhagem alta na janela):** a floreira de cactos troca pela gerada no Higgsfield com a caixa antiga de referência
(gpt_image_2, 4 variantes: jobs 3247a15d, 1679d02c, 9f219839 e 0b1daa9c; escolhida a 9f219839): a mesma caixa de
concreto claro com quatro touceiras de espada-de-são-jorge de borda amarela, duas folhagens altas de folha larga
(tipo dracena) e forração miúda, vista de cima
(`biblioteca-objetos/03-primeiro-pavimento/banho-master/floreira-espada-de-sao-jorge-e-folhagem.png`). A caixa cai no
lugar exato da antiga (166,4 x 35,0 px, centro 1369,2/1546,5: a peça em 1365,13/1546,5, 166,35 x 43,35, 90°); as folhas
passam da caixa para o lado da parede (como os cactos) e, do lado do vidro do banho, param na borda da caixa. (Depois,
ainda em 12/11, a caixa vai ao retângulo do PDF, com as folhas dentro dela: ver "Floreira e janela do banho master".)

**Chuveiros (12/11, "OS CHUVEIROS PRECISAM SER REFEITOS. ESTÃO MUITO APAGADOS"):** os PNG da biblioteca são fotos de
cromado claro; reduzidos a 12 px sobre o travertino claro, viravam um quadrado cinza-claro liso (os furos somem), e o
redondo de parede é foto em perspectiva (saía oval). `chuveiros_planta_casaa_1211.py` desenha os chuveiros vistos de
cima e grava na biblioteca, ao lado dos originais, `banho-master/` e `banho-3/chuveiro-quadrado-planta.png`, `banho-1/`
e `banho-2/chuveiro-quadrado-parede-planta.png` e `banho-de-servico/chuveiro-redondo-parede-planta.png`: a placa em
inox escovado médio (o cinza que se lê no travertino) com o degradê da luz do alto à direita, o chanfro da borda (claro
em cima e à direita, escuro embaixo e à esquerda), o contorno escuro fino, o crivo mais escuro com a grade de furos (ou
os anéis, no redondo) e, nos de parede, o braço em tubo com o brilho do lado da luz e a canopla. A mesma posição e o
mesmo tamanho de antes; a sombra `chuveiro` (o chuveiro fica no alto: mais longe e mais forte que a de uma louça). Em
`chuveiro`, a placa dos desenhos `-planta` começa logo abaixo do tubo (no redondo, a calota de cima não estica com o
braço). As zonas dos chuveiros antigos vão um pouco além, com a sombra deles. Antes e depois em
`renders/POE642_CasaA_PH_1Pavimento_1211_chuveiros_antes_depois.jpg`.

**Piso refeito no tom do entorno (12/11, junto com os chuveiros):** o piso que sai do gerador vinha mais claro que o da
final em volta (até uns 10 tons no travertino: a final passou por outros acertos de tom depois do gerador) e a pegada
da peça antiga aparecia como um quadrado claro em volta do chuveiro novo. No vinílico (`tom_do_entorno`), cada mancha
refeita vai ao tom do piso de verdade em volta (a razão, por canal, da mediana do anel de fora na final de antes pela
da beira de dentro no gerado, entre 0,88 e 1,12); no travertino (`luz_do_entorno`), a luz de fundo inteira: a final
borrada no anel de fora, levada para dentro por inpaint, sobre a do gerado borrada (o desenho da pedra fica).

**Tapete da suíte 2 (12/11, "CORRIGIR O TAPETE NA SUITE 2"):** o tapete do render ficava (`TAPETES_FICAM`), com a pegada
das peças antigas refeita no tecido dele: a beira da esquerda dobrada (do render), degraus na borda de baixo onde a
zona da cama começava e, no 12K, uma colcha de retalhos (a faixa lisa e clara da IA em cima e à direita, o tecido
refeito no miolo). Agora sai inteiro, com a sombra (zona 1658,1041 a 1875,1168; não está mais em `TAPETES_FICAM`): o
vinílico volta do gerador e entra o tapete da biblioteca (`sala-intima/tapete`, de trama fina) no tom do de antes
(BGR 210, 218, 227: `("tom", b, g, r)` em `preparar`), no retângulo do PDF (ARQ_LAYOUT HUMANIZAÇÃO, 1662,0/1044,9 a
1871,0/1164,3: 3,50 x 2,00 m), por baixo da cama, do banco e da poltrona; no 12K, nítido do PNG. Antes e depois em
`renders/POE642_CasaA_PH_1Pavimento_1211_tapete_suite_2_antes_depois.jpg`. Depois ("PODE APLICAR NOS TAPETES DAS SUÍTES
1 E 3"), o mesmo nas suítes 1 e 3 (`TAPETES_FICAM` fica vazio): os tapetes do render saem inteiros, com a sombra (zonas
2280,1394 a 2497,1533 e 1633,384 a 1850,529), e entra o da biblioteca no tom de cada um (suíte 1, BGR 210, 217, 227;
suíte 3, 206, 214, 225, a mediana das faixas livres do tapete antigo), nos retângulos do PDF (suíte 1, 2283,6/1397,9 a
2492,6/1529,2; suíte 3, 1636,7/387,8 a 1845,7/525,2), por baixo das camas, dos bancos e dos criados; o rótulo da suíte 1
fica por cima. Antes e depois em `renders/POE642_CasaA_PH_1Pavimento_1211_tapetes_suites_1_3_antes_depois.jpg`.

**Floreira e janela do banho master (12/11, "CORRIJA AS FOLHAS DE VIDRO PARA SE ENCONTRAREM, CORRIJA O CONTORNO DA
FLOREIRA E NÃO DEIXE AS PLANTAS VERDES PASSAREM PELAS JANELAS"):** pelo PDF (ARQ_PAREDE), a floreira fica entre a
janela da fachada (face de dentro em x 1345,3) e a janela do banho (face de fora em x 1376,7), de parede a parede
(y 1463,9 a 1631,1): 167,2 x 31,4 px. A caixa ia de 1351,7 a 1386,7, por cima da janela do banho, e as folhas passavam
da caixa e apareciam entre as folhas de vidro. `floreira_caixa_casaa_1211.py <saída do Higgsfield>` refaz o PNG da
floreira (o mesmo nome): só a caixa (as folhas param na borda de fora dela) e comprida até a proporção do PDF (5,3:1;
a imagem é 4:1) pelo miolo, sem achatar as plantas (358 costuras verticais de menor energia, que passam pela terra e
pela forração entre as touceiras, duplicadas: seam carving). A peça entra no retângulo do PDF (1361,0/1547,5, 0,6 px a
mais de cada lado para a beira macia não deixar o verde do render; as paredes e as janelas ficam). A janela é
redesenhada pelo PDF (`janela_floreira`, `JANELA_FLOREIRA`): o vão de 1376,7 a 1387,5 (depois, "PODE APLICAR UMA
SOLEIRA PARA AS JANELAS A DIREITA DA FLOREIRA. O TOM DE PAREDE NÃO PODE SER": não no cinza das paredes, mas na soleira
das portas do 1º Pavimento, a de `ajustes_casaa.desenhar_soleiras`: Bege Bahia na escala, no tom da referência, com as
faces da parede, os lados compridos, em cinza fino; antes e depois em
`renders/POE642_CasaA_PH_1Pavimento_1211_soleira_janela_floreira_antes_depois.jpg`; "SEM AVANÇAR SOBRE A PAREDE DE
CIMA": a soleira só no vão, da face da parede de cima, y 1463,9, à de baixo, 1631,1; e a beira da caixa da floreira junto
às paredes, onde a máscara das paredes não deixava a peça pintar e sobrava 1 a 2 px do verde do render, vai ao
concreto da caixa, da face da parede para dentro, `floreira_beiras`, com o canto de baixo à esquerda, onde o marco da
janela da fachada entra na floreira) e as três folhas de correr em trilhos escalonados (x 1384,5, 1381,5 e 1378,5; 3 px cada), cada
uma de montante a montante, de modo que os montantes de duas folhas vizinhas ficam lado a lado (as folhas se
encontram); o vidro claro com as duas faces e o contorno fino. Desenhada depois das peças, nítida na final e no 12K
(`pecas_12k`, pela cobertura exata de cada retângulo). O verde do render do lado de dentro da janela volta ao
travertino (zona 1387,1464 a 1391,1631). Antes e depois em
`renders/POE642_CasaA_PH_1Pavimento_1211_floreira_janela_antes_depois.jpg`.

**Como refazer:** `python3 chuveiros_planta_casaa_1211.py` e `python3 floreira_caixa_casaa_1211.py <a saída 9f219839 do
Higgsfield, fora do git>` (os PNG da biblioteca, já no git); `python3 biblioteca_1pav_casaa_1211.py` (parte da final de `ANTES_COMMIT` = 127eabc; sem `--saida`
grava a final, o registro do 12K e os antes e depois `renders/POE642_CasaA_PH_1Pavimento_1211b_<ambiente>_antes_depois.jpg`);
depois `ampliacao_12k_1pav_casaa.py montar12k <Topaz> --opcao AB`, `rodape_entrega.py --no-quadro --render
1Pavimento=../renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png`, `pdf_entrega.py` e `book_entrega.py`.

### As correções do cliente no Térreo da Casa A: `terreo_casaa_1011.py` (10/11)

Lista do cliente (Paulo Octávio) com os recortes da planta do Térreo, e as respostas do usuário. Um passo por pedido, sobre a final do Térreo do commit 58ea098 (a mesma de 0a17741), na ordem de `PASSOS`:

- **Tracejados (`TRACEJADOS_TA`, `tracejados_ta`; cliente: "Remover as linhas tracejadas [...] Deixar apenas as que representam 'vazios'"; "Não representar as linhas tracejadas do telhado"):** saem todos, pela reta inteira do PDF (`_retas_tracejadas`): os afastamentos (DOC_LINHAS E PROJEÇÕES), os dois contornos da laje da cobertura (ARQ_CONTRAPISO, `laje_px`, e o lado esquerdo do terraço gourmet, `laje_extra_px`), a grade do pergolado (ARQ_PERGOLADO) e os X e as molduras. Por grupo de direção (`_orientacao`), com as pontas esticadas `ponta_px`: no piso, a faixa do traço recebe o piso do mesmo material a 2h+2 px dali, na normal (`apagar_retas`); sobre móveis e carros (`moveis_pdf` e o neutro claro), só os px do traço, por inpaint. O pergolado é refeito inteiro com `pedidos_terreo_casaa_2910.piso_refeito` (Bege Bahia tecido de `pergolado_fontes_px`). Nas pontas das diagonais (o render engrossava o traço em ponta de seta), o que é bem mais escuro que o piso no disco de `canto_px` (18) sai por inpaint; sobre os montantes cinza do PDF, só o preto do traço (`preto_traco`). Na grama e na água, nada (são refeitas nos passos delas).
- **Gramado (`GRAMADO_TA`, `gramado_ta`; usuário: "USE O MESMO TOM DE GRAMA DO SUBSOLO"; cliente: "No terreno não precisa representar muitas árvores [...] Representar arbustos que são menores"; usuário: "Arbustos e 4 árvores"):** a grama padrão (`texturas.textura("grama_padrao")`) no gramado inteiro do lote (`gramado_mascara`: o branco da base chapada fechado e o verde do render, sem os carros, `verde_azul`); 4 árvores pequenas nos cantos (`arvores`) e arbustos de 0,85–1,25 m a cada 4,8–7,0 m junto aos muros; o jardim interno no tom da grama nova. No jardim de 4,79 m² (cliente: "Deixar melhor representada as plantas, pode diferenciar os tamanhos"), três plantas da biblioteca em tamanhos diferentes (`jardim_479`), recortadas dentro das paredes.
- **Água (`PISCINA_TA`, `piscina_ta`; cliente: "Deixar o tom de azul para a piscina mais sóbrio"; usuário: "USAR COMO REFERENCIA O TOM DA PISCINA E PRAINHA DA IMAGEM 3. E O REVESTIMENTO BARLAVENTO PORTOBELO"):** a piscina e o spa no tom da água da foto (BGR 118, 117, 106) e a prainha (abaixo do degrau do PDF, `prainha_y_pt`) no cinza claro dela (141, 145, 146); o desenho do Barlavento fica (a razão da luminância a uma referência local); os traços sobre a água saem.
- **Bege Bahia (`BEGE_TA`, `bege_ta`; usuário: "Isso vai se repetir para todas as plantas da casa, de todas as casas daqui para frente"):** a regra do Subsolo (`BEGE_CS`): nos pisos de Bege Bahia (o cinza 232 da base chapada e o banho do motorista), as manchas a 45% do contraste. O tom do lugar é a mediana de 25 px da imagem com as peças tapadas; o desenho é a imagem sobre o tom, e cai para 0,45; nas arestas do tom (bordas dos degraus e das sombras) fica o px de antes. Sob os rótulos (e 2 px em volta), o piso vem da imagem tapada e o rótulo volta por cima, no alfa dele, só onde o piso foi refeito (compor sobre o rótulo antigo engrossava a borda das letras; o ELEVADOR, sobre a cabine, fica como estava).
- **Piso marrom (`PISO_MARROM_TA`, `piso_marrom_ta`; cliente: "Trocar a representação do piso por essa amostra [...] mais uniforme [...] mais sóbrio"; "deixar a tonalidade do piso mais claro"):** no granito do piso (a cor malva da base chapada, menos o banho do motorista), a amostra do cliente (`_texturas/originais/amostra_piso_marrom_cliente_1011.png`, RGB ~135, 108, 87) tecida por image quilting; a luz da final passa ao piso novo (só o que escurece além de `limiar`); as peças ficam e a borda delas é refeita pela fração; os rótulos voltam em branco. As bancadas em marrom tabaco ficam.
- **Bancadas (`BANCADAS_TA`, `bancadas_ta`):** a ilha e a bancada da pia da cozinha e a bancada dos tanques (`ajustes_casaa.TANQUES` e `ARMARIOS_A`, sem os tanques) em Dekton Danae (`DANAE`, `danae`: bege-areia claro e fosco, de grão fino; o tom é o da descrição do fabricante, BGR 172, 189, 200, porque a foto não pôde ser baixada); o lavatório (bancada e cuba) em marrom tabaco, a cuba mais escura (`cuba_esc` 0,78); a churrasqueira (`churrasqueira_pt`, o retângulo do PDF na bancada de trás da área gourmet: aro de inox, grelha escura com as barras); no lavabo (cliente: "A cuba e a pedra lateral são da mesma cor"), a pedra lateral no tom mediano da bancada da cuba, de grão liso (`lavabo_camadas`).
- **Banquetas (`BANQUETAS_TA`, `banquetas_ta`; cliente: "Colocar só 5 banquetas. E com um tom um pouco mais destacado em relação ao piso"):** as 6 do render saem (piso refeito); entram 5, espaçadas por igual em `x_px`, a banqueta de linho da biblioteca virada para a ilha, no tom `tom` (mais escuro que o travertino), com a sombra curta.
- **Pilar (`PILAR_TA`, `pilar_ta`; cliente: "Falha na representação do pilar."):** o quadrado preto do PDF (EST - Pilar) no canto do terraço gourmet, sem a mancha em volta.
- **Soleiras (`SOLEIRAS_TA`, `soleiras_ta`):** na entrada, a soleira como a da Casa C (`entrada_px`: textura bege com as faces cinza); entre a sala e o escritório (cliente: "Não tem soleira"), o claro da soleira volta a ser o piso (`escritorio_px`).
- **Entrada (`ENTRADA_TA`, `entrada_ta`; cliente: "Centralizar a seta com a abertura da porta"; usuário: "USAR O TRIANGULO COMO SETA E REMOVER A SETA QUE HAVIA"):** a seta antiga sai (piso refeito); o triângulo cheio, apontando para dentro, no meio da abertura da porta.
- **Escadas (`ESCADAS_TA`, `escadas_ta`; cliente: "Colocar a seta em todas as escadas e a descrição"):** o triângulo e a descrição no modelo do Subsolo, em duas linhas: pisantes, "DESCE PARA O / DECK" (a letra D sai); lance abaixo do spa, "DESCE PARA O / SUBSOLO"; escada do jardim, "SOBE PARA O / 1º PAVIMENTO", com o guarda-corpo de vidro (cliente: "Representar o guarda-corpo"); caracol (cliente: dashes só nos degraus, sem a linha de corte), redesenhada (`caracol_novo`): os degraus em linhas radiais, cheias até o corte e tracejadas depois, o contorno e o pilar preto, o triângulo no 1º degrau e "SOBE PARA O / 1º PAVIMENTO" em branco ao lado.
- **Shaft (`SHAFT_TA`, `shaft_ta`; cliente: "Tirar o nome shaft"):** o rótulo SHAFT sai. Nos dois vazios pequenos (a claraboia do lavabo e o shaft), o X antigo, curto e inclinado, não sai inteiro no passo dos tracejados (a faixa vizinha cai no outro braço do X ou na moldura; no shaft, o rótulo protegia os traços junto dele): o que sobra dentro de `caixas_px` (fora das paredes), neutro e bem mais escuro ou mais claro que o piso de perto, sai por inpaint.
- **Tracejados finos (`FINOS_TA`, `tracejados_finos_ta`; cliente, no pergolado e na área de serviço descoberta: "mais finas e mais claras"):** os X e as molduras dos vazios (varanda e sala de estar, área de serviço descoberta, claraboia, shaft, `vazios_px`) e o pergolado voltam do PDF (`preto_branco`), com 0,9 px, em cinza 112 no piso claro e 205 no escuro, fora dos rótulos e dos móveis. Antes, os pontinhos escuros que sobraram nas pontas dos X (manchas de até `pontos_area` px no disco de `pontos_px`) saem (`_pontos_cantos`).
- **Antes e depois (`ANTES_DEPOIS_1011`, contra a final de 58ea098):** `renders/POE642_CasaA_PH_Terreo_1011_{planta,vazios_varanda_estar,pergolado,pisantes_deck,piscina_prainha,escada_subsolo,gourmet,cozinha_servico,caracol,entrada_escritorio,lavabo_shaft,escada_jardim,jardim_479}_antes_depois.jpg`.
- **1º Pavimento (`NUBLADO_1011`, `terreos_sem_anotacoes`, `nublado_1pav_1011`; com `--um_pav`; ainda não aplicado: usuário, "DEIXE O 1 º PAVIMENTO PARA SEQUENCIA. FOQUE NO TERREO"):** o Térreo nublado em volta do 1º Pavimento e nos vazios é refeito onde o Térreo mudou, pela conta de `pedidos_terreo_casaa_2910.nublado_1pav_ta` (a diferença entre o Térreo novo e o antigo, nublados), com os dois Térreos sem o que o nublado não leva: o antigo é o passo dos tracejados (sem nenhum tracejado), sem as letras S e D, a seta da entrada e o nome SHAFT; o novo é o passo do shaft refeito sem os triângulos e as descrições (`ANOTAR`), antes dos tracejados finos. A caracol e o shaft ficam com o desenho do 1º Pavimento (`fora_px`).
- **Como refazer:** `python3 terreo_casaa_1011.py --antes <a final do Térreo de 58ea098> --passos <pasta> --antes_depois` (grava a final em `renders/POE642_CasaA_PH_Terreo_final_rotulos.png`; `--de`/`--ate <passo>` e `--saida` para testar um trecho; com `--um_pav <a final do 1º Pavimento de ab9a071>`, também a do 1º Pavimento em `renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png`); depois `rodape_entrega.py --no-quadro --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_rotulos.png`, `pdf_entrega.py` e `book_entrega.py`.

### O gramado até o muro e a soleira da entrada da Casa C (Térreo, `terreo_casaa_1011.py`, 10/11)

- **Gramado até o muro (usuário: "VAMOS CORRIGIR O GRAMADO ATÉ O MURO"):** a máscara do gramado (`gramado_mascara`) passou a usar a caixa `mascara_px` (262, 140, 3450, 1960), além dos muros: o limite é o verde do render, que vai até a face de dentro dos muros e até a linha do lote (antes, a caixa `lote_px` deixava uma faixa da grama antiga junto aos muros). Junto aos muros o render passa uns px da base do PDF: o verde do render colado ao gramado entra até `muro_px` (8) px, fora do branco da base; o muro (cinza neutro) segue como limite. `lote_px` fica só para os arbustos.
- **Soleira da entrada (cliente: "Representar uma soleira na entrada igual a casa C"):** a faixa da soleira da entrada da Casa C (da final dela, 13 x 121 px: a face fina de cada lado e a pedra clara lisa), guardada em `_texturas/originais/soleira_entrada_casac.png`, esticada no comprimento do vão (`SOLEIRAS_TA["entrada_px"]` 2444–2457 x 686–843). Antes era a textura do Bege Bahia com as faces cinza.

### Térreo: a leva de 10/11 à noite (`terreo_casaa_1011.py`, piscina, soleiras, bancadas, escadas e o passo 14, `contornos`)

Pedidos do usuário, com os recortes da planta (todos de 10/11): "A SOLEIRA VAI DE FORA A FORA. NÃO PARA NA PORTA"; "CORRIGIR CONTORNO DO CARRO E O ERRO NA GARAGEM, NA PARTE DE BAIXO TEM UM DENTE QUE NÃO EXISTE"; "FALTOU A BOA REPRESENTAÇÃO DO GUARDA CORPO NO CONTORNO"; "CORRIGIR OS ERROS NAS PEDRAS"; "CORRIGIR CONTORNO DO ACESSO À GARAGEM DESDE O INÍCIO E O MURO (NA PARTE DE BAIXO)"; "REMOVER OS TRACEJADOS E CORRIGIR CONTORNOS"; "CORRIGIR CONTORNO DA ESCADA E DECK (SE HOUVER)"; "CORRIGIR BATENTE E A PEDRA DO HALL EXTERNO. ELA É RENTE A PAREDE."; "CONSEGUIMOS DEIXAR O TOM DA PISCINA E DA PRAINHA/SPA MAIS PARECIDO COM ESTES" (3 fotos); "MELHORAR A BANCADA [do lavabo] ... DEVERIA IR E FAZER UM CONTORNO EM VOLTA DA CUBA ESCULPIDA. ALÉM DISSO, MELHORE O RÓTULO E CENTRALIZE-O ... O RÓTULO DA CLARABOIA NÃO DÁ PARA LER DIREITO"; "O TOM DAS PAREDES PRECISA FICAR UM CINZA MAIS ESCURO"; "FALTOU REPRESENTAR A JANELA AQUI"; "AQUI TEM UM GUARDA CORPO" (com o PDF); "LIMPA ESSE ERRO AO LADO DA PLANTA"; "MELHORAR A REPRESENTAÇÃO DO MARMORE BEGE BAHIA ENTRE OS QUADRADOS"; "MELHORAR A REPRESENTAÇÃO DA PAREDE ATRÁS DA PORTA DA ÁREA DE SERVIÇO"; "NESSAS PIAS: ÁREA GOURMET, COZINHA PRECISAMOS REPRESENTAR O RALO DE CADA UMA DELAS".

- **Piscina (`piscina_ta`, `PISCINA_TA`):** a água feita de novo, sem a rede grande de cáusticas antiga: a funda no azul-ardósia das fotos (BGR 106, 99, 80) com o grão fino do revestimento, manchas largas de luz, as cáusticas finas e curtas em grupos e a sombra das bordas (mais forte na esquerda e em cima); a rasa (a prainha e o banco do spa, o anel em volta do fundo do PDF) no cinza neutro das fotos (BGR 137, 140, 139), com mais grão; o degrau da prainha com a sombra fina do lado fundo.
- **Bancada do lavabo (`bancadas_ta`):** uma peça só em L (a parte larga da cuba e a estreita de baixo), sem a linha entre elas, na cor da cuba; a cuba esculpida dentro da parte larga, com a borda da bancada em volta, o fundo côncavo, o ralo e a torneira na parede.
- **Soleiras (`soleiras_ta`):** os batentes da porta pivotante no desenho do PDF, na cor das paredes (como os da entrada da Casa C); a soleira de batente a batente na largura deles; a pedra do hall externo até a parede de baixo (sem a faixa de grama).
- **Escada do jardim (`escadas_ta`, `vidro_laminas`):** o guarda-corpo nas lâminas de vidro do PDF (ARQ_ELEMENTOS FIXOS) em todo o contorno e em volta da floreira, no desenho da regra [22/10] (o da Casa B).
- **Passo 14, `contornos_ta` (antes dos tracejados finos):** o 3º carro e o piso em volta (o bloco do 2º; sem o anel do granito antigo e sem o dente na pedra portuguesa); a 5ª pedra do acesso (a 1ª, de mesma largura) e a 4ª sem o filete branco; o início da pista até a borda do lote, com as curvas continuadas; o muro de baixo inteiro (a cunha cinza vira grama) e com a ponta reta; o tracejado branco da borda do gramado junto à garagem e os pontinhos nas pontas dos X e dos portões fora; o deck rente à base da escada do Subsolo e a faixa rosada ao lado da escada em grama; os guarda-corpos de vidro do terraço (a borda de cima, a esquerda e as de baixo); a janela da parede de cima da sala de estar (o peitoril com o vidro); LAVABO no corpo padrão, no centro do piso livre, e PROJ. CLARABOIA numa linha, na altura das letras de LAVABO, abaixo da projeção (gravados em `renders/POE642_CasaA_PH_Terreo_rotulos_lavabo.json` para o 12K); o resto do desenho da planta do PDF junto ao vidro da sala de jantar; a parede atrás da porta da área de serviço (o granito limpo entre a parede e a folha, a folha nítida e a sombra lisa); os ralos das cubas da área gourmet e da cozinha (os do PDF); o Bege Bahia das faixas das vigas do pergolado com a textura de dentro dos quadrados; e as paredes, os batentes e os muros no cinza 52 (antes 79).
- **Depois, mais pedidos da mesma noite:** "MELHORE A REPRESENTAÇÃO DESSA CUBA" (o lavatório: `cuba_esculpida`, a bacia lisa de cantos redondos na própria pedra, um tom abaixo, o fundo côncavo, o lábio claro, o ralo e a torneira); "MELHORE A REPRESENTAÇÃO DESSAS MESAS REDONDAS LATERAIS, PONHA UM TOM O SOBRETOM NELAS. E ALTERE O TOM DO ARMARIO PARA O TOM JÁ DEFINIDO. E MELHORE A REPRESENTAÇÃO DA PORTA DO ESCRITÓRIO" (`_escritorio`: o aparador no tom padrão dos armários, RGB 208, 178, 156, quase liso; as duas mesinhas do PDF, a de baixo no sobretom claro e a de cima em nogueira, com a sombra; a folha da porta nítida, do batente ao fim do vão). Respostas do usuário às perguntas: o X da área de serviço descoberta fica fino e claro; o rasgo branco na viga entre o hall externo e o jardim vira vazio, no Bege do hall, com o X fino (`_vazio_viga` e `FINOS_TA["vazios_px"]`); o spa com o banco cinza e o fundo azul.
- **12K (`ampliacao_12k_terreo_casaa.py`):** `preparar` parte de `passo_contornos.png`; `montar12k --opcao AB` grava as duas opções de letra, `entrega/POE642_CasaA_PH_Terreo_12K_opcao_A.jpg` (Inter) e `..._opcao_B.jpg` (Kalam, `rotulos_manuscritos_casaa`; as descrições das escadas também na Kalam), regra de 10/11.

### O JPG em 12K do Térreo: `ampliacao_12k_terreo_casaa.py` (10/11)

Pedido do usuário: "GERE A IMAGEM EM 12K JPG. ISSO É REGRA PARA TODAS AS PLANTAS". Só a imagem, sem rodapé, na A3 deitada (12288 x 8689 px, 743 dpi na A3), como a do Subsolo.

- **`preparar --passos <pasta>`:** a entrada da IA parte do passo do shaft de `terreo_casaa_1011.py` (a final sem os tracejados finos); o alfa e a cor dos tracejados finos (a final contra esse passo) ficam em `renders/POE642_CasaA_PH_Terreo_12K_tracejados.png`. Saem os 27 rótulos (achados na final pela forma, com o corpo, a quebra e o desvio de cada um, `rotulos`), as 4 descrições e os 5 triângulos das escadas e da entrada (`anotacoes`), pela conta do alfa (`ampliacao_a3_casaa.tirar`); a área de cada texto, com 2 px de folga, vem toda do entorno (onde o desenho achado não casava px a px com a final, sobrava a sombra do texto). O recorte da planta em 16:9 (a planta do Térreo é mais larga que a A3): `renders/POE642_CasaA_PH_Terreo_12K_entrada_ia.png` (3371 x 1896, a partir de 166, 98 da final); os dados em `renders/POE642_CasaA_PH_Terreo_12K_dados.json`.
- **Nano Banana Pro, 4K, 16:9:** 5504 x 3072 (job ba8f9e7e-d89d-45a3-b7ba-f79e289fce9c), com o prompt `PROMPT`.
- **`diferencas` e `corrigir`:** no mapa das diferenças (`renders/POE642_CasaA_PH_Terreo_12K_diferencas.jpg`) e nos recortes, a IA tinha: posto todos os degraus da caracol em linha cheia; trocado os dois cooktops (bocas quadradas) e a cuba do lavabo; alisado o marrom tabaco da bancada gourmet; feito a prainha com uma grade forte de pastilhas e a piscina sem o desenho; trocado o leque da pedra portuguesa por um cascalho claro. Esses trechos voltam da entrada ampliada (Lanczos, com nitidez): as caixas de `CORRIGIR_PX` (caracol, cooktop da cozinha, área gourmet, lavabo) e as máscaras de `CORRIGIR_MASCARAS` (a água, `agua_mascara`; a pedra portuguesa, a cor 85, 138, 185 da base). As árvores, as plantas e os móveis (mais nítidos e fiéis) ficam os da IA. A saída corrigida: `renders/POE642_CasaA_PH_Terreo_12K_saida_nano_banana_pro.png`.
- **Topaz (High Fidelity V2), 12288 x 6858:** job 96695f57-3407-4a57-9d51-7cb931516061 (a saída, 114 MB, não vai para o git).
- **`montar12k`:** a saída do Topaz alinhada à entrada (ECC afim), na A3 deitada (o 16:9 fica no meio; acima e abaixo, o branco); os tons da final (a baixa frequência, na escala da entrada, ampliada em faixas); o fundo fora da planta em branco puro; os tracejados finos de volta (o alfa ampliado, na cor deles); os rótulos (`alfa_rotulo`, o desenho da final na escala de 12K), as descrições e os triângulos (`alfa_anotacao`) desenhados direto em 12K, numa janela em volta de cada um. JPG qualidade 95, sem subamostragem de cor: `entrega/POE642_CasaA_PH_Terreo_12K.jpg` (28,4 MB); prévia `renders/POE642_CasaA_PH_Terreo_12K_previa.jpg` e conferências (a final ampliada sem IA ao lado) `renders/POE642_CasaA_PH_Terreo_12K_conferencia_{piscina_deck,varanda_estar,gourmet_cozinha,hall_lavabo_escritorio,garagem}.jpg`.
- **Como refazer:** `python3 ampliacao_12k_terreo_casaa.py preparar --passos <pasta dos passos>`; a entrada no Nano Banana Pro (4K, 16:9, `PROMPT`); `python3 ampliacao_12k_terreo_casaa.py diferencas <saída da IA>` (e acrescentar a `CORRIGIR_PX` o que ela inventou); `python3 ampliacao_12k_terreo_casaa.py corrigir <saída da IA> <corrigida>`; a corrigida no Topaz (High Fidelity V2, 12288 de largura); `python3 ampliacao_12k_terreo_casaa.py montar12k <saída do Topaz>`.

### O 12K do Térreo da leva de 10/11 à noite (opções A e B)

- **Entrada:** `preparar --passos <run>` com o passo `contornos` (a piscina, as paredes, os guarda-corpos e o escritório novos); o recorte da IA 166,98 3371 x 1896 (16:9).
- **IA:** Nano Banana Pro 4K 16:9 (job 8a8ae02c-f1ff-4a3b-9d56-28bf067fcb1a), o prompt de ampliação fiel com as paredes em grafite, a água funda azul-ardósia com o grão e as cáusticas finas, a rasa e o banco do spa em cinza claro e os guarda-corpos de vidro. Saída 5504 x 3072.
- **`corrigir`:** além de caracol, cooktop da cozinha, área gourmet e lavabo (a caixa agora sobe até a cuba, y 350), voltam da entrada: `elevador_motorista` (a IA tirou o X e os puxadores do elevador, trocou a roupa de cama e a cuba do motorista), `escritorio_mesas` (juntou as duas mesinhas), `escritorio_aparador` (listrou), `lavatorio` (cuba trocada por um ralo linear), `pias_cozinha` (tirou os ralos), `prateleiras_garagem` (virou um armário rosado), `janela_estar` e `vidro_estar` (um puxador no vidro) e `vidro_jardim` (parte do vidro apagada). A água e a pedra portuguesa seguem pelas máscaras. A saída corrigida: `renders/POE642_CasaA_PH_Terreo_12K_saida_nano_banana_pro.png`.
- **Topaz:** High Fidelity V2 a 12288 x 6858 (job 970a2e90-ea8b-4132-ad89-c2732e3cbc69); fica fora do git.
- **`montar12k --opcao AB`:** `entrega/POE642_CasaA_PH_Terreo_12K_opcao_{A,B}.jpg` (12288 x 8689), prévias `renders/POE642_CasaA_PH_Terreo_12K_opcao_{A,B}_previa.jpg` e conferências `..._opcao_{A,B}_conferencia_{piscina_deck,varanda_estar,gourmet_cozinha,hall_lavabo_escritorio,garagem}.jpg`. Na opção B, cada linha na Kalam tem no máximo a largura que tinha na Inter (a Kalam é mais larga na mesma altura das maiúsculas; o PROJ. CLARABOIA passava por cima da parede do lavabo).
- **CLARABOIA (10/11, resposta do usuário: "APENAS 'CLARABOIA'"):** numa linha no corpo 1,3, o PROJ. CLARABOIA ocupava o vão inteiro do lavabo. O rótulo passou a ser só CLARABOIA: `CONTORNOS_TA["lavabo"]["claraboia"]["texto"] = ["CLARABOIA"]`, que `_lavabo_rotulos` passa como `quebra` de uma linha (o texto trocado, centrado no nome do PDF) e grava em `renders/POE642_CasaA_PH_Terreo_rotulos_lavabo.json`, de onde o 12K (A e B) o desenha. Refeito pelo passo `contornos` (`--antes <passo_shaft> --de contornos`), sem nova ida à IA: o `preparar` tira os rótulos da entrada, e a saída do Topaz serve como estava.
- **Os dois resíduos (10/11, OK do usuário: "PODE LIMPAR OS DOIS RESÍDUOS TAMBÉM"):** no fim do passo `contornos`, `_residuos_finos` com `CONTORNOS_TA["residuos_finos"]`: o traço escuro de 2 px na ponta direita da pedra do hall externo (x 2598-2599, y 867-878) refeito pela pedra das colunas dos lados, linha a linha; a mancha clara no granito abaixo da ponta da parede atrás da porta da área de serviço (x 2043-2049, y 1459-1461) refeita pelo granito 6 px abaixo. Os tracejados finos não passam nesses pontos, então aplicar a limpeza sobre a final dá o mesmo que rodar o passo de novo (conferido).

### A piscina em turquesa sobre o Barlavento visível (Térreo, 10/11)

- **Pedido:** "Preciso que o revestimento das piscinas apareça na planta humanizada" (o item do prompt v34) e "E A PISCINA?"; na pergunta do tom, "Turquesa #7CC8D4 do item novo" (no lugar do azul-ardósia das 3 fotos).
- **`PISCINA_TA` e `pastilhas_rel`:** a água funda no turquesa #7CC8D4 um pouco mais intenso (BGR 204, 192, 114), a rasa (prainha e banco do spa) no turquesa misturado ao tom da pastilha (BGR 207, 203, 150); por cima, o Barlavento relativo: peças de 14,5 cm (8,7 px), cada uma num tom (±2,5%), o grão fino, as juntas a 7,5% da peça de cada lado escurecidas a 0,84, a grade de cada tanque a partir do seu canto (a piscina e a prainha numa grade só, o spa na dele), levemente ondulada pela refração (deslocamento suave de 0,35 px); as pastilhas a 55% no fundo e a 100% na parte rasa; as cáusticas fracas; o esfumado das bordas mínimo e o fio do degrau da prainha.
- **Como refazer:** `terreo_casaa_1011.py --antes <run7/passo_gramado> --de piscina --passos <pasta>` (os passos 3 a 14); depois o 12K (`preparar`, `corrigir` sobre a mesma saída do Nano Banana Pro, porque a água volta da entrada pela máscara, e um Topaz novo), a prancha, o PDF e o book.
- **12K da piscina nova:** o `preparar` põe a água sem os rótulos (`piscina_ta(..., com_rotulos=False)`, o mesmo desenho, porque a semente é fixa) no lugar do texto tirado de cima das pastilhas, que borrava a grade; o `corrigir` sobre a mesma saída do Nano Banana Pro (a água volta da entrada pela máscara) e um Topaz novo.

### Térreo: os retoques de 11/11 (`terreo_casaa_1011.py`, `RETOQUES_1111`, e o 12K)

Pedidos do usuário com os recortes (todos aplicados direto, por serem pedidos dele): "CORRIGIR ESSA FALHA" (as duas bordas da curva do acesso); "REMOVER ESSE TRACEJADO JUNTO AO CONTORNO / TRACEJADO NA HORIZONTAL" (junto ao WC, ao jardim de 4,79 m² e ao gás); "TIRAR O ROTULO DE CIMA DA PORTA. COLOQUE UM POUCO MAIS ACIMA DE ONDE ESTÁ, CENTRAL." (LAVABO); "CORRIGIR ACABAMENTO DO ARMARIO E RETOQUE NA PAREDE"; "ADICIONAR RALO EM CADA UMA DAS PIAS DA COZINHA"; "ADICIONAR RALO NA PIA DO GOURMET"; "TOM MAIS CLARO PARA PARTE DA ESCADA QUE PERTENCE AO 1º PAVIMENTO."; "CORRIGIR BORRÃO E RETOCAR O PISO DA GARAGEM, REMOVENDO RESIDUOS DO PISO ANTERIOR"; "RETOCAR PAREDE" (embaixo do aparador do hall interno); "RETOCAR AS PEDRAS E SUAS BORDAS" (as 5 pedras do acesso, no 12K); "NÃO PODEMOS TER NENHUMA PORTA 'FLUTUANTE'. REVISE TODAS E GARANTA QUINA A QUINA ENTRE A PORTA E A PAREDE."

- **Curva do acesso (`_acesso`):** o degrau em x 3377 vinha do ajuste antigo, que copiava a pedra de 18 px à esquerda (a grama da coluna de lá entrava na borda de cima) e ajustava a borda de baixo numa faixa cortada em y 1640. As bordas são as parábolas das bordas reais de x 3300-3413 (cima) e 3300-3429 (baixo), refeitas de x 3340 até a borda do lote; a pedra nova vem da mesma coluna, mais para dentro da pista, e a grama de mais para fora.
- **Rótulo do LAVABO:** centro em (2285,5, 440) px, centrado no piso livre entre a parede e a bancada, acima da folha da porta.
- **Ralos:** os do PDF (1 pt) ficavam sob a base da torneira; agora 5 px (~9 cm), cromados, no eixo da bica, logo depois da ponta dela (`ralos_px`).
- **Caracol (`ESCADAS_TA["caracol"]`):** os degraus inteiros acima do corte (do 9º em diante, os tracejados) clareados 45% para o véu claro (`degrau_1pav`, `claro_1pav`). Por isso a rodada parte do passo `escadas`.
- **`retoques_1111`, no fim do passo `contornos`:** o tracejado (a última linha do travertino alternava com a grama; o filete branco entre a parede e a grama do jardim e a ponta clara da parede do gás); o armário do lavabo (retângulo limpo na madeira dele, espelhada nas bordas, contorno fino, encostado na parede; a parede no cinza das paredes onde o PDF tem parede cheia); a parede do hall (topo reto na linha do PDF, meia cobertura em 878 e cheia de 879 para baixo, o piso acima limpo e a sombra de contato sob o aparador); a grama do motorista (os dois borrões viram a grama 50 px à direita; a faixa roxa do piso antigo sai: grama até 1313, piso da garagem de 1314); as pedras (retângulos limpos em y 608-866, o miolo espelhado nas bordas, a 4ª refeita da 2ª espelhada, sem a emenda; a grama em volta sem restos claros); as portas (as de abrir 1, 3, 6, 7, 9, 13 e 18 com a ponta da parede avançando até a face de dentro da folha, por `cliente_subsolo_casaa_0511.portais_cs` com a configuração do Térreo, e os px claros que a cópia do piso deixava nas quinas tirados; a ponta da parede da garagem sem o marco claro; a porta de correr entre a cozinha e o hall fechada de batente a batente, a parte que corria junto à parede tirada; a folha da porta do lavabo, que estava apagada pela metade, redesenhada nítida no retângulo do PDF, e a ponta da parede de baixo até a quina dela).
- **12K:** `preparar --passos <run9>`, `corrigir` sobre a mesma saída do Nano Banana Pro com as caixas novas de `CORRIGIR_PX` (os trechos retocados voltam da entrada nova), um Topaz novo (High Fidelity V2, 12288×6858) e `montar12k --opcao AB`.
- **Como refazer:** `terreo_casaa_1011.py --antes <run8/passo_entrada> --de escadas --passos <pasta>`; os antes e depois em `renders/POE642_CasaA_PH_Terreo_1111_<trecho>_antes_depois.jpg` (`ANTES_DEPOIS_1111`, contra a final de 41f6731); depois `rodape_entrega.py --no-quadro --render Terreo=...`, `pdf_entrega.py`, `book_entrega.py` e o 12K.
- **1º Pavimento:** fica para a sequência (o Térreo nublado nele ainda é o de antes desses retoques; `--um_pav` refaz quando for a vez dele).


### Térreo: a 2ª leva de 11/11 (deck, água C, rótulos, traços; `terreo_casaa_1011.py` e o 12K) e a água C nas outras casas

Pedidos do usuário com os recortes: "traga mais realismo para essa madeira no deck" e "a madeira do deck não pode parecer velha"; "consegue trazer esse efeito de água para a piscina? sem alterar o piso da nossa piscina ... vamos ver duas opções para eu decidir", "para as piscinas teremos que trazer mais um tom de sol ... o sol traz diversos pontos brilhantes", "traga mais uma opção com base nessa imagem de referência mais ampliada", "gostei da opção C da piscina", "essa opção vai ser utilizada para todas as piscinas de todas as casas"; "limpe residuos e alinhe os rotulos"; "centralize e alinhe os rótulos. mantenha os mesmos tamanho de fonte, sempre que possível"; "ainda tem um tracejado na horizontal que precisa ser removido"; "corrija o local do guarda corpo de forma que fique igual em todos os lados. mantenha o guarda corpo na parte mais extrema da escada"; "as descrições de sobe/desce podem ter fontes de tamanho menores, semelhante as demais"; "corrija as imperfeições desse portão em vidro"; "limpe residuos e corrija o piso de acesso a garagem"; "corrija essa imperfeição sem gerar outra imperfeição no acesso à garagem".

- **Deck (`deck_madeira_ta`, `DECK_TA`, passo `deck` depois do `piso_marrom`):** réguas de ~20 cm (regras, seção 3) no sentido do PDF, peças de 1,6 a 3,4 m com os topos desencontrados, o tom de madeira nova recém-oleada (o mel de `tom`), veio e grão discretos, juntas e topos leves, a luz da final (sem as faixas antigas); o rótulo por cima.
- **Água (`AGUA_OPCOES`, `AGUA_OPCAO = "C"`, `agua_caustica`, `ondas_brilho`):** o Barlavento fica igual (a mesma grade e a mesma semente); a água no cinza-esverdeado da foto, as ondinhas finas e curvas com o brilho do sol em manchas, um resto da rede de cáusticas e uns poucos pontos brilhantes. As opções A e B ficam no código (cáusticas leves e marcadas, com sol).
- **Rótulos (`rotulos_1111`, `ROTULOS_1111`, no fim do passo `contornos`):** cada rótulo de `centros` sai do lugar (o piso de baixo vem de um trecho do mesmo piso, linha a linha do texto, pelo deslocamento que melhor casa a borda; sem trecho bom, do entorno) e volta centrado e alinhado com o vizinho (VARANDA e SALA DE ESTAR, ÁREA GOURMET e COZINHA, ÁREA DE SERVIÇO e DESPENSA, LAVATÓRIO e BANHO VARANDA, os dois HALL; SALA DE JANTAR e DECK DE MADEIRA no meio do ambiente); o B. MOTORISTA no corpo de todos (1,3). O desenho vai para `renders/POE642_CasaA_PH_Terreo_rotulos_1111.json`, que o `preparar` do 12K usa. As descrições das escadas no corpo `ESCADAS_TA["corpo_desc_px"]` (11 px), também no 12K; no 12K B, a Kalam num fator só para todos os rótulos (`fator_manuscrita`; só a PROJ. CLARABOIA, em `kalam_estreitos`, pode ficar menor).
- **Traços:** a linha de cima da moldura da área descoberta sai dos tracejados finos (`FINOS_TA["sem_horizontais_px"]`) e o resto escuro sob as soleiras do gás e do serviço vira pedra (`RETOQUES_1111["tracejado"]["gas_*"]`); a borda do lote na pista (`_acesso`, `borda_lote_px`) sem a faixa branca.
- **Pisos claros (`pisos_1111`, `PISOS_1111`, no passo `contornos`, depois dos retoques; OK do usuário aos 3 itens):** o travertino do lavabo, do lavatório, do banho varanda e do WC vai ao tom da varanda e da sala (a luz local do piso, só nos px dele, fora das paredes e das peças, só clareando e esfumada para fora dos retângulos, sem emenda nos vãos abertos); o banho do motorista segue em Bege Bahia; as pedras do acesso e o hall externo ficam (as manchas são as do deck).
- **Partes rasas das piscinas (`AGUA_OPCOES["C"]["rasa"]`, `_degraus`; nas outras casas `RASAS` e `profundidade`):** a prainha e o banco do spa mais claros e transparentes, as pastilhas nítidas, a rede de cáusticas do fundo raso, menos ondinhas e brilhos; os degraus contínuos (a sombra do lado fundo, a quina clara do lado raso), sem nada por cima; a escadinha da Casa C em 4 faixas.
- **Guarda-corpo da escada do jardim (`ESCADAS_TA["jardim"]["guarda_corpo_px"]`):** a face de fora de cada lâmina na borda da escada (cima 912, direita 2489,5, baixo 1082,5; floreira 986,2, 1010,2 e 2417,1), todas com 2,4 px.
- **12K:** caixas novas em `CORRIGIR_PX` (`deck_1111`, `guarda_corpo_1111`, `faixa_baixo_1111` com o portão e o acesso à garagem, `varanda_sala_1111`), sobre a mesma saída do Nano Banana Pro; Topaz novo e `montar12k --opcao AB`.
- **As outras casas (`piscinas_turquesa.py <planta> --agua-c`, `AGUA_C`):** nos Térreos das Casas B a E e no Subsolo da Casa E, sobre a final: a luz de cada px sem a cor (sem o claro das cáusticas antigas), o Barlavento da Casa A redesenhado em cada piscina, o tom da C e as mesmas ondinhas. Antes e depois em `POE642_Casa{B,C,D,E}/renders/*_piscina_aguaC_antes_depois.jpg`. O Térreo esmaecido dos 1º Pavimentos (A e E) fica para quando eles forem refeitos.
- **Como refazer:** `terreo_casaa_1011.py --antes <run7/passo_gramado> --de piscina --passos <pasta>`; depois `rodape_entrega.py --no-quadro --render Terreo=...`, `pdf_entrega.py`, `book_entrega.py` e o 12K.


### Térreo: a 3ª leva de 11/11 (a sala da vista 3D e a área verde B; `sala_1111.py`, `paisagismo.py`)

Pedidos do usuário: "precisamos mudar o tom do tapete para que não se confunda com o piso"; "a área verde precisa ter coerencia entre arvores e arbustos, 80% da área é grama. se conseguir melhorar o aspecto da grama, trazendo mais realismo, também é bem vindo"; "sem exageros no paisagismo, pois o cliente que comprar a casa ainda vai contratar. preserve 80% da área em grama realista no tom que já temos"; "segue vista interna em 3d da sala da casa A, para usar tons de poltrona e sofá e tapete"; "opção B na área verde e a sala ok. na opção B remova a árvore da frente da casa. se for manter, traga uma oliveira e na parte superior uma palmeira. no fundo coloque menos arbusto em volta das árvores"; "nestas poltronas, apenas o encosto delas em terracota. nas quatro. e precisa ficar perfeito, sem borrões e bem preenchido dentro da área de encosto"; "somente o contorno do encosto, igual a imagem que enviei de referência no render"; "contorno externo, não próximo ao assento".

- **Área verde (`paisagismo.py`, chamado no passo `gramado` com `GRAMADO_TA["paisagismo"] = "B"` e `paisagismo_plantas`):** a grama do padrão com a variação de tom em manchas (1,5, 4 e 9 m), o fio com mais contraste e a sombra de contato junto ao que não é grama e aos maciços; a média do tom volta à de antes (`grama_realista`). As plantas: as duas árvores do fundo (`arvore_3` em cima, `arvore_2` embaixo, 3 m, com a nitidez de volta) com maciços de 2,1 m; a palmeira desenhada (`palmeira`: folhas pinadas em duas camadas, a luz do alto à direita) no canto de cima da frente, com maciço de 2,5 m; sem a árvore da frente (junto ao acesso). Os arbustos são o bloco `arbusto` da biblioteca, tingido nos verdes das copas (`_tingir`: a borda escura, o volume), sem floridos; a sombra da biblioteca para todas. As opções A (faixa em trechos junto aos muros) e B ficam no código.
- **Sala (`sala_1111.py`, no passo `contornos`, depois de `pisos_1111`):** os tapetes por `tapetes_1111` (opção A, taupe: o tapete é o preenchimento do PDF menos as peças; perto delas, um classificador; o tapete entra na sombra das peças; os furinhos claros fechados); o redondo com o desenho da vista 3D (`_desenho_tapete`); o sofá curvo e a poltrona avulsa em creme e o par em verde (a peça é o que não é tapete); nas 4 poltronas em X, o contorno externo do encosto em terracota: a concha separada no modelo da poltrona (`concha_modelo`: o vinco e as pontas levadas até a borda), a faixa de fora até a crista (`fracao_ext`), o modelo recolorido posto de novo com o mesmo giro, a escala e o centro de `revisao_casaa_2910.poltronas_ta`, a borda com o bouclé reforçada; a mesa de centro em nogueira e as mesinhas em grafite.
- **12K:** `CORRIGIR_PX["sala_1111"]` e a máscara do gramado (`CORRIGIR_MASCARAS["gramado"]`, `gramado_mascara` sobre a final) trazem a sala e o gramado da entrada nova, sobre a mesma saída do Nano Banana Pro. A grama realista tem manchas mais oliva (o verde um pouco abaixo do vermelho) que o limite da máscara (`verde` -4): ali ela furava e dois arbustos antigos da IA ficavam no gramado do fundo (vistos no mapa das diferenças); a máscara do 12K é agora a união da de sempre com a de limite `CORRECAO["gramado_verde"]` (-10), quase igual à do passo do gramado. Topaz High Fidelity V2 a 12288 x 6858 (job bbc419d4-b585-4c68-a0fb-4b1060311559; fora do git) e `montar12k --opcao AB`. Na opção B, `_itens_manuscrita(..., fator="tetos")` multiplicava o corpo pela palavra "tetos" (erro de tipo): com "tetos" o corpo fica no fator 1 e só os tetos são devolvidos; a Kalam saiu no fator 0,925 em todos os rótulos.
- **Como refazer:** `terreo_casaa_1011.py --antes <run7/passo_tracejados> --de gramado --passos <pasta>`; os antes e depois em `renders/POE642_CasaA_PH_Terreo_1111c_<trecho>_antes_depois.jpg`; depois `rodape_entrega.py --no-quadro --render Terreo=...`, `pdf_entrega.py`, `book_entrega.py` e o 12K.

### 1º Pavimento: os 17 pedidos do cliente de 11/11 (`um_pav_casaa_1111.py`)

Pedidos em `pedidos_cliente/1Pavimento_1111/` (LEIA.md e os 17 recortes), mais as regras do Térreo aprovado que valem aqui ("Térreo aprovado, inicie o 1°"). A partida é a final do commit ab9a071; os passos rodam em ordem (`PASSOS`) e cada um pode ser refeito sozinho (`--de`/`--ate`, `--passos <pasta>` grava um PNG por passo):

1. **`nublado`:** o Térreo aprovado (o limpo da entrada do 12K, sem rótulos) nublado como `entorno_esmaecido.NUBLADO` fora da pegada (a pegada aberta em 25 px, `pegada_1p`: sem os dentes das pontas das vigas do pergolado e as lascas da borda da varanda de 14,6 m²; vale também para o pergolado e o contorno), nos 2 vazios, no poço da escada em U e nos degraus 1 a 7; a linha de corte da escada e o contorno do vão por cima (`NUBLADO_1P`).
2. **`tracejados`** (itens 5 e 17): saem as retas da cobertura e do afastamento de baixo (ARQ_CONTRAPISO com 10 traços ou mais, DOC_LINHAS) e o topo do L da varanda de 6,36 m² (`extras_px`), pelo `terreo_casaa_1011.apagar_retas`; depois a `costura` (só nas retas verticais): sobre a cama e a banheira da suíte/banho master a faixa de 4 px de cada lado recebe a interpolação dos dois lados, com as pontas fora das paredes; o resto do afastamento dentro da janela da saleta (`restos_px`) e o rótulo VARANDA 6,36 m², que encostava na reta (`rotulo_px`).
2b. **`bege`** (regra de 10/11; usuário, 11/11: "Reduzir manchas do bege Bahia, da mesma forma que fizemos"): o Bege Bahia das 4 varandas, do quarto de serviço, da saleta e do B. serviço (o cinza 232 da chapada, na pegada, fora do nublado e das paredes) com as manchas a 45% do contraste, pelo `terreo_casaa_1011.bege_ta` (que ganhou o argumento `zona`).
3. **`pergolado`** (item 7; usuário, vendo a final: "Pergolado esfumaçado, conforme orientação, por estar abaixo do 1° pavimento"): as 7 vigas do ARQ_PERGOLADO na madeira do deck, esfumaçadas (62% de branco, bordas desfocadas a 2,2 px, grão largo e leve, sombra difusa), cada uma até a borda da casa (`_ate_a_casa`), só onde o Térreo aparece.
4. **`contorno`** (item 1): o contorno de fora da pegada (`pegada_1p`, aberta em 25 px) em 2,2 px cinza-escuro, com a sombra para fora.
5. **`vazios`** (itens 4, 6 e 12): os X e as molduras dos 2 vazios em traço fino e claro (`FINOS_TA` + `preto_branco`), o X novo do vazio junto ao elevador e o do shaft de cima; a janela do shaft vira parede; o guarda-corpo de vidro do vazio junto à circulação.
5b. **`shafts`** (usuário, 11/11: "melhore a representação do x tracejado"; regra: X dos shafts em preto): os 4 shafts (o de cima, o junto ao elevador e os dois da suíte master; `SHAFTS_1P`, o vão de cada um como está na final: o de cima é o do render, mais alto que o do PDF) com o fundo branco limpo (sem os retângulos e os riscos do render) e o X tracejado redesenhado de canto a canto, fino (0,85 px) e simétrico (um traço cruza o centro, o mesmo passo para os dois lados); a parede dos shafts da suíte master de volta ao desenho do PDF (o dente da quina de cima à esquerda) e a quina junto ao shaft de cima sem os px pretos do render.
6. **`folhas`** (usuário, 11/11: "aqui são duas folhas amadeiradas" na suíte 2, "quatro folhas" na master, "corrija o amadeirado aqui também" na suíte 1): no lugar dos painéis de ripado contínuo, o plano de fora das portas das 4 suítes folha por folha (as folhas e as junções de `revisao_casaa_2910.BRISES_SUITES_TA`/`JUNCOES_TA` e as dos banhos de `pedidos_terreo_casaa_2910.BANHOS_1PAV_TA`), em ripado de nogueira com a junta, a luz do lado da varanda, o contorno fino e a sombra curta; antes, a faixa é limpa (`_limpar_faixa`): fora do trilho e em frente aos banhos o Bege Bahia da varanda de logo ao lado; entre os trilhos, no vão do quarto, o piso do quarto das 3 primeiras colunas livres depois do trilho de vidro; sem copiar o rótulo VARANDA (a mesma coluna, em outra linha).
6b. **`guarda_corpos`** (usuário, 11/11: "melhore a representação do guarda corpo aqui", varandas de 7,15 e 6,36 m²; "o guarda corpo vai até o final, encostando na parede", varanda de 39 m²): os 11 trechos de vidro do PDF nas 4 varandas (`GUARDA_CORPOS_1P`, com o lado de fora de cada um), o de baixo da varanda de 39 m² até a parede do B. serviço, no desenho dos vidros (`terreo_casaa_1011.vidro_laminas`); antes, a borda entre o vidro e o contorno da casa (o contorno fica inteiro) e 3 px para dentro recebem o Bege Bahia de logo para dentro (junto a um rótulo, o da mesma faixa umas linhas antes ou depois).
7. **`bancada`** (item 11): a bancada do quarto de serviço em Dekton Danae (`TA.danae`), em volta da cuba redonda; depois (usuário, 11/11: "Melhore a representação da Cuba, torneira e ralo da Cuba"), a cuba redesenhada (`_cuba_redonda`: a aba de louça, a bacia em degradê da borda ao fundo com a sombra por dentro do lado da luz, a sombra curta na bancada, o ralo cromado com o miolo escuro e o brilho) e a torneira de mesa atrás, do lado da parede (`_torneira_mesa`: a base redonda, a bica até o terço de trás da bacia e a alavanca, com `final3840_casaa.torneira` e `placa_cromada`).
7b. **`cubas`** (usuário, 11/11: "melhore a representa das cubas esculpidas em marmore travertino bruto. e a torneira precisa fica mais bem representada"): as bancadas dos banhos 1, 2, 3 e master no travertino bruto (`final3840_casaa.travertino_bruto`, sem repetir a sombra) e as 5 cubas esculpidas nelas (`terreo_casaa_1011.cuba_esculpida`, com a aba de 2,2 pt e, novo, `poros`: 70% da textura da pedra fica na bacia, os poros e os estratos do travertino bruto); as torneiras de mesa redesenhadas (`_torneira_melhor`: a bica mais larga, a base, o arejador escuro na ponta e a alavanca cromada de lado), também a do B. serviço.
8. **`tapete`** (item 10): o tapete da sala íntima no tom A (taupe) do Térreo (`TA.tapetes_1111`).
8b. **`sala_intima`** (usuário, 11/11: "vamos melhorar esse mobiliário, contorno, sofá, trazendo mais realismo"): o tapete inteiro refeito com a trama de um trecho limpo dele (`amostra_tapete_px`: faixas de linhas da amostra, as listras são horizontais, em ladrilhos espelhados; o debrum um pouco mais escuro; a poltrona fica) e o anel do piso em volta do sofá limpo (`_anel`); o sofá em L do PDF peça a peça em bouclé creme (o creme da sala do Térreo): o encosto alto, as almofadas do encosto com o vinco, as 4 almofadas do assento separadas pela costura funda, os 2 braços, cada peça com o volume (`_volume`) e a trama; 3 almofadas soltas (terracota e areia) encostadas no encosto; a mesa de centro do render em nogueira (veio e chanfro) e as 3 mesinhas redondas (as 2 do PDF junto aos braços e a da poltrona) em grafite; a sombra macia (`final3840_casad.SOMBRA_JOGOS_D`), também a da poltrona no tapete novo, e o contorno fino.
9. **`closets`** (itens 3 e 9): os 4 guarda-roupas (closets 1, 2, 3 e master) refeitos numa peça só, em L ou U: os cabides de cada trecho até o canto, os varões se encontrando no centro do canto, sem a lateral entre os trechos; a moldura ocre só nas bordas de fora.
9b. **`armarios`** (usuário, 11/11: "melhore o contorno de todos os armarios. revise-os e corrija-os"): em volta dos 4 guarda-roupas e do armário do quarto de serviço, o anel de 10 px do render (a faixa escura e as manchas da sombra antiga junto às portas) recebe o piso de logo ao lado (`_anel`, sem paredes e rótulos); a mesma sombra curta e macia em todos e o contorno fino e nítido onde a peça encontra o piso.
9c. **`bancos`** (usuário, 11/11: "vamos representar esses bancos em frente as camas com mais realismo"): os 5 bancos de pé de cama (suítes 3, 2, master e os 2 da suíte 1; as caixas do render, `BANCOS_1P`) estofados: a base de nogueira num aro fino, o assento de linho caramelo com volume (a borda mais escura do lado oposto à luz), o vivo da costura, o vinco entre as 2 almofadas nos bancos longos, a trama e a sombra macia no tapete (não na cama); antes, o anel do banco antigo recebe o tapete de logo ao lado, menos do lado da cama.
9d. **`mesinhas_master`** (usuário, 11/11: "melhore a representação da mesa redonda, da parede e limpe resíduos da imagem"): o par de mesinhas encaixadas do PDF junto à poltrona da suíte master em nogueira (a de cima mais clara, com a sombra de contato na de baixo), a sombra macia e o contorno fino; o anel em volta limpo sem tocar a poltrona. A parede dos shafts vem no passo `shafts`.
10. **`portas`** (item 15): as 11 folhas de giro presas à ponta da parede, quina a quina (`cliente_subsolo_casaa_0511.portais_cs` com as caixas de `PORTAS_1P`).
11. **`escadas`** (itens 13 e 16): na escada em U o triângulo e "DESCE PARA O HALL INTERNO"; na caracol o triângulo no sentido da descida e "DESCE PARA A ÁREA DE SERVIÇO"; sem o "D"; os guarda-corpos de vidro da escada em U e da abertura da caracol. A linha de corte da escada em U (usuário: "pode remover a linha preta, mas preserve a divisão. ou suavize a linha preta") vai mais fina e cinza (`NUBLADO_1P["corte"]`, no passo `nublado`).
12. **`floreira`** (item 17): a folhagem grande do banho master sai (o travertino de volta pela faixa vizinha, a torneira fica), a forração verde com 3 plantas pequenas dentro do canteiro e a divisória de vidro.
13. **`pisos_1111e`** (usuário, 11/11 à noite: "melhore o aspecto do piso vinílico e do marmore travertino bruto. sem mexer nos demais pisos"; "traga mais realismo, mantendo-os novos e limpos"): só nas áreas desses dois materiais da base chapada (o vinílico das 4 suítes e dos closets; o travertino bruto da circulação, da sala íntima e dos banhos 1, 2, 3 e master) e só no que é piso: fora as peças do PDF (layout, louças, bancadas, elementos fixos e escadas, cheias por dentro: camas, tapetes, sofá, bancadas, a escada em U), as paredes e o que foge do tom do piso do lugar (`final3840_casab.luz_robusta`); a sombra dos móveis fica como fator (o px mais escuro no mesmo matiz, perto das peças). Os rótulos saem antes (`ampliacao_a3_casaa.tirar`, com o alfa de `ampliacao_12k_terreo_casaa.rotulos`) e voltam desenhados por cima. Vinílico (`_reguas_1111e`): réguas de 20 cm, de 1,1 a 1,8 m, em fiadas com os topos desencontrados, deitadas (como as tábuas do render, inclusive nas faixas dos vãos das portas), cada régua num tom (alternado, ±3,5%) com o veio largo e os fios finos no comprido, a junta fina entre as fiadas com o bisel claro e a junta de topo, em 4x e reduzido. Travertino bruto: a foto da biblioteca (`final3840_casaa.travertino_bruto`, estratos na horizontal e poros finos), sem manchas e sem rejuntes. A luz é a do lugar achatada 60% para o tom mediano de cada ambiente. A poltrona antiga da escrivaninha da suíte 1 sai aqui (`forcar_px`: o vinílico novo por cima). Números em `PISOS_1111E`. **Vinílico da foto (11/11)** (usuário, com a foto de um vinílico de carvalho claro: "vamos trazer esse piso vinílico em sua respectiva escala para os ambientes que possuem piso vinílico. vamos testar e se der certo adotaremos para todas as outras plantas"; vendo o teste, de 20 cm: "sim, aplique em todas as plantas com vinílico, mas com uma escala mais reduzida" -> `regua_foto_m` 0,12, e as outras plantas por `vinilico_foto.py`): com `PISOS_1111E["vinilico"]["amostra"]`, o vinílico sai da própria foto (`_texturas/originais/amostra_vinilico_carvalho_1111.png`, o recorte sem os botões da tela): as fiadas da foto (20,8 px de largura, a partir de x = 7, medidas pela autocorrelação das bordas) cortadas em réguas inteiras de junta de topo a junta de topo (`_pecas_amostra`: 52 réguas, de 18 a 400 px), cada régua sorteada (sem repetir as 6 últimas, às vezes girada 180°) e emendada junta a junta nas fiadas deitadas, com a largura da régua da foto em `regua_foto_m` (12 cm; o 1º teste tinha 20 cm) (`_reguas_amostra`); a cor é a da foto e do lugar fica só a luz, relativa, e a sombra dos móveis. Entram também os vãos das portas de correr (na chapada, vão) que tinham o vinílico do render (entre a folha e a cortina), ligados ao ambiente (`vao_px`, `vao_croma`, `vao_r`). Sem `amostra`, volta o desenho de antes (`_reguas_1111e`). Os antes e depois em `..._1111g_<trecho>_antes_depois.jpg` (`ANTES_DEPOIS_1111G_1P`, contra a final de 0e5d084).
14. **`retoques_1111e`** (usuário, com recortes: "corrija o vidro/guardacorpo", "corrija o guarda corpo aqui também", "melhore o aspecto dessa poltrona junto a escrivaninha e a representação do lapt top"): a janela de vidro entre a circulação e o vão da escada e o guarda-corpo do vazio da direita (as 4 faixas de `faixas_px`) limpos, cada px com o de 9 px para o lado do material dele (fugindo das paredes e das diagonais do X do vazio), as diagonais do X redesenhadas só na faixa (a borda do vazio é o próprio guarda-corpo) e o vidro no desenho das regras (`terreo_casaa_1011.vidro_laminas`); na escrivaninha da suíte 1, o laptop antigo (as manchas pretas) sai com o tampo de logo ao lado, emendado sem costura (`cv2.seamlessClone`), entra a cadeira de madeira e linho da biblioteca (`final3840_casad._cadeira_bloco`, a das mesas de trabalho das outras casas), virada para a mesa, 1/3 sob o tampo e com a sombra curta dele, e um laptop aberto visto de cima (a base de alumínio com o teclado em grade e o trackpad, a dobradiça escura, a tampa inclinada para trás e a sombra curta). Números em `RETOQUES_1111E`. A poltrona da sala íntima, inteira sobre o tapete (usuário: "poltrona deve ficar sobre o tapete, na sua integridade"), vem do passo `sala_intima` (o recorte `bases/POE642_CasaA_1Pavimento_poltrona_sala_intima.png`, colado depois do tapete).
15. **`degraus_1111e`** (usuário: "sim, aplique o mesmo acabamento nos degraus da escada em U"): os 19 degraus coloridos e o patamar da escada em U (o que é pedra quente e lisa dentro da caixa `caixa_px`, fora das linhas dos bocéis, dos enevoados, do guarda-corpo, do triângulo e do texto) no travertino bruto do passo `pisos_1111e` (`final3840_casaa.travertino_bruto`), uma textura por peça, com o veio no comprimento e o tom médio igual em todas (a média da textura normalizada em cada peça); a luz do lugar achatada para o tom mediano. Os poros antigos (manchinhas de até 30 px) não contam como linhas. Números em `DEGRAUS_1111E`.
16. **`retoques_1111f`** (usuário, com recortes: "revise portas e remova os arcos de movimento delas"; "a sombra de descida para esquerda não ficou bom. até acho que está ao contrário. corrija"; "essa porta precisa ser representada novamente"; "melhore a representação dessas portas de vidro e remova os resíduos existentes"; "faltou a representação dessa cadeira de escritório"): (1) a caracol desce para a esquerda (do 0°, junto ao D do PDF, para o 93°): o degrau do 0° no tom cheio e cada um 1,6% mais escuro até o último (84%), com a sombra do espelho no lado de quem desce; o triângulo do passo `escadas` virado no mesmo sentido (`ESCADAS_1P["caracol"]["sentido"] = -1`); (2) as 11 folhas de giro (`folhas_px`) redesenhadas sobre o piso novo, sem arco: o piso sob a folha refeito com o de 12 px para o lado de fora da parede (a parede do PDF e a pintada ficam), a folha em madeira clara com o veio no comprido, o contorno fino e a sombra curta; a da suíte 3, que o passo dos pisos tinha apagado, volta; (3) as portas de vidro da saleta: o vão limpo numa soleira de travertino com as faces finas da parede, os batentes e os perfis das duas folhas de correr (desencontradas, como no PDF) em alumínio e o vidro no desenho das regras (`terreo_casaa_1011.vidro_laminas`); (4) a cadeira da escrivaninha da suíte 3: a mancha branca antiga sai (o piso de 46 px ao lado) e entra a cadeira de madeira e linho da biblioteca, virada para a mesa e 1/3 sob o tampo, como a da suíte 1 (`_cadeira_mesa`). Números em `RETOQUES_1111F`.

Ajudantes: `_anel` (o anel em volta de uma máscara recebe, px a px, o que está mais para fora na normal da borda, pulando o que é proibido), `_rotulos_mascara` (os px dos rótulos achados na imagem) e `_cobertura` (a cobertura exata de um retângulo fracionário em cada px).

**Como refazer:** `um_pav_casaa_1111.py --antes <final de ab9a071> --saida <png> --passos <pasta>` (os passos em ordem; `--de`/`--ate` para refazer só um trecho); a final instalada em `renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png`. Os antes e depois: os 17 pedidos contra a final de ab9a071 em `renders/POE642_CasaA_PH_1Pavimento_1111_<trecho>_antes_depois.jpg`; a 2ª leva (bege e pergolado, contra 216506b) em `..._1111b_...`; a cuba Danae em `..._1111c_...`; a 4ª leva (folhas, guarda-corpos, cubas, sala íntima, bancos, shafts, mesinhas, armários; contra a final de e3cb9cf) em `..._1111d_<trecho>_antes_depois.jpg` (`ANTES_DEPOIS_1111D_1P`); a 5ª leva (poltrona da sala íntima, vidros da circulação e do vazio, escrivaninha da suíte 1, pisos de vinílico e travertino; contra a final de 17670fa) em `..._1111e_<trecho>_antes_depois.jpg` (`ANTES_DEPOIS_1111E_1P`, com `--antes_ref <final instalada>`); a 6ª leva (degraus da escada em U, caracol, folhas sem arcos, saleta e cadeira da suíte 3; contra a final de 279ec5c) em `..._1111f_<trecho>_antes_depois.jpg` (`ANTES_DEPOIS_1111F_1P`, o padrão de `--antes_depois`). Depois `rodape_entrega.py --no-quadro --render 1Pavimento=../renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png`, `pdf_entrega.py` e `book_entrega.py`.

**O vinílico da foto nas outras plantas (`vinilico_foto.py`, 11/11):** o mesmo piso (as réguas da foto, 12 cm, `VINILICO_FOTO`) sobre a final instalada de cada planta com vinílico (`PLANTAS`: Térreos e Subsolos das Casas B, C e D, 1º Pavimento e Subsolo da Casa E, academia do Subsolo da Casa A; o Térreo da Casa E não tem vinílico). O quadro de cada casa (`quadro`: `final3840_casab.Quadro` com o `contexto_c`/`contexto_d` das Casas C e D, `final3840_casae.QuadroE`, `final3840_casaa.QuadroA`); o vinílico é a cor dele na base chapada (`Q.cor`, BGR 124, 162, 200 nas Casas B a D e 79, 120, 168 na Casa E; na Casa A, o retângulo da madeira de `PISOS_A`), mais os vãos das portas com o vinílico do render; só o que é piso (fora as peças do PDF, as paredes e o que foge do tom do piso do lugar); a luz e as sombras dos móveis da final como fator; a direção das tábuas pela da final (`auto`). Os rótulos e os riscos escuros sobre o piso (peças cinza-escuras de até 40 px) ficam: a cobertura de cada px é medida contra a luz do piso antigo e o texto volta, na mesma cor, sobre o piso novo. `python3 vinilico_foto.py <planta> --antes_depois` (sem `--saida`, grava por cima da final; rodar sobre a final de antes do vinílico, a do commit 2e52cdf); o antes e depois em `renders/POE642_Casa<X>_PH_<pavimento>_vinilico_foto_antes_depois.jpg` da casa. Depois, as pranchas (`rodape_entrega.py --config <casa> --no-quadro --render ...`), os PDFs (`pdf_entrega.py --config <casa>`) e o book.

**O 12K do 1º Pavimento (`ampliacao_12k_1pav_casaa.py`):** o roteiro do Térreo (`ampliacao_12k_terreo_casaa.py`, que agora tem `PAV`/`NOME_PAV` e `quadro()` para servir aos dois) com os nomes, o prompt e as caixas do 1º Pavimento. Na preparação, os triângulos e as descrições das escadas saem refazendo os passos `escadas` e `floreira` a partir do passo `portas` com `terreo_casaa_1011.ANOTAR` desligado (o que eles mudam contra o passo `floreira` com as anotações entra na final, que já tem os pisos e os retoques de 11/11); os rótulos saem pela conta do alfa; os tracejados finos ficam na entrada da IA (o alfa dos tracejados é vazio). Depois: Nano Banana Pro (4K, 16:9) com `PROMPT`, `diferencas`, `corrigir`, Topaz (High Fidelity V2, 12288 de largura) e `montar12k --opcao AB` (A na Inter, B na Kalam), em `entrega/POE642_CasaA_PH_1Pavimento_12K_opcao_{A,B}.jpg` (no git, como os do Subsolo e do Térreo; as saídas do Topaz ficam fora). Na rodada de 11/11 à noite (sobre a final com os pisos novos; Nano Banana Pro job 09c2bb19-3fe0-4a16-b3fe-66d1d0658771, 5504 x 3072), a IA tinha trocado cortinas, folhas, camas, cubas, ralos, o canteiro do banho master, a cadeira e o laptop da escrivaninha, a janela da circulação e trechos de parede; por isso, em vez de caixas, a correção usa a máscara `pecas` (`_mascara_1p`, números em `PECAS_12K`): dentro da pegada (`Q.pegada`), tudo o que não é piso volta da entrada (os móveis, as louças, as bancadas, as portas, os vidros, as paredes, as escadas, os vazios); da IA ficam os pisos (vinílico, travertino bruto e Bege Bahia, no que é piso: o matiz do piso do lugar, fora das peças do PDF, com as juntas fechadas) e o entorno (o Térreo nublado e o pergolado). Topaz High Fidelity V2 a 12288 x 6858 (job 379a7a3c-dd25-49b3-8270-bcb301632b1b; fora do git).

**Os 12K da Casa A com o vinílico da foto (11/11, usuário: "gere os 12K da Casa A"):** o Térreo não tem vinílico (o 12K dele fica). O Subsolo e o 1º Pavimento reaproveitam a mesma saída do Nano Banana Pro de cada um (a IA não roda de novo) e trazem da entrada nova tudo o que mudou na final desde que a IA a viu:
- **`vinilico_foto.py`, rótulos da especificação (`ROTULOS_SPEC`, `camadas_spec`):** no Subsolo da Casa A, os rótulos têm especificação (`rotulos_subsolo_casaa`, mais as descrições da escada de `ampliacao_a3_casaa.escada_camadas`), e o 12K e a letra manuscrita os tiram da final pela conta do alfa. O vinílico novo trocado com eles na imagem deixava, nessa conta, o fantasma branco das letras sobre o piso novo: agora `trocar(..., camadas=...)` tira os rótulos antes (`ampliacao_a3_casaa.tirar`) e os redesenha no fim pela especificação (`pintar`), os que caem no piso novo; os outros ficam como estavam. E, em todas as plantas, o piso antigo que ainda sobra dentro do contorno das peças do PDF (a peça desenhada na final é menor que o contorno, como os aparelhos da academia) entra no piso novo quando está no tom dele e ligado ao piso de fora (`folga_pdf`, `binary_propagation`).
- **Subsolo (`ampliacao_a3_casaa.py corrigir ... --antes_final <final de antes do vinílico>`):** `MUDOU` (limiar 6, folga de 2 px): o que difere entre a final de quando a IA foi feita e a final nova vem da entrada nova, px a px, além das caixas de `CORRIGIR_PX`; os aparelhos da academia, que não mudaram, ficam os da IA. A A3 em 4K (`montar`), o Topaz (High Fidelity V2, 12288 x 9175, job 2977e9b6-094a-45ab-bd08-9f505920cdd0; fora do git) e os JPGs `montar12k` (A e B).
- **1º Pavimento (`ampliacao_12k_1pav_casaa.py`):** o `preparar` passa a versão sem as anotações também pelos passos de depois (`U.correcoes(sem, "pisos_1111e")`: pisos, retoques, degraus da escada em U, caracol), e o trecho das anotações vem dali. `corrigir ... --entrada_antes <a entrada que a IA viu>` junta duas máscaras às `pecas`: `mudou` (`MUDOU_12K`, limiar 10, folga de 3 px: o que mudou na entrada nova contra a que a IA viu, ou seja, os degraus, a caracol, as folhas das portas, a saleta, a cadeira da suíte 3 e o vinílico) e `arcos` (`ARCOS_12K`: o setor de cada arco de porta do PDF, camada `ARQ_PAREDE`, de 15 a 90 pt, com o centro no canto da caixa mais longe do meio do arco, crescido 4 px; a IA tinha desenhado os arcos no piso, e a regra R3 é sem arcos). Sobre a mesma saída do Nano Banana Pro (job 09c2bb19); Topaz High Fidelity V2 a 12288 x 6858 (job fcc3ada5-2292-4c70-9dbd-a0624b4d930c; fora do git) e `montar12k --opcao AB`.

**A correção do vinílico da foto (12/11; achado ao abrir o Subsolo da Casa B: o rótulo ACADEMIA saía picotado):** o `vinilico_foto.py` estragava rótulos e peças pequenas nas plantas sem especificação de rótulos (Térreos e Subsolos das Casas B, C e D, 1º Pavimento e Subsolo da Casa E) e os pedais das bicicletas do Subsolo da Casa A. Duas causas, na proteção do texto: o núcleo das letras exigia o cinza (a borda das letras finas pega a cor da madeira; no ACADEMIA, só 35 px passavam) e o lado maior de cada mancha até 40 px (as letras de uma palavra se tocam e a palavra inteira saía); o resto das letras virava "fiapo" do piso antigo (buraco pequeno) e recebia o vinílico. Agora o núcleo é só o escuro (abaixo de 0,62 do tom do piso; o veio do piso nunca chega lá), com o lado menor até 40 px e o maior até `largura_max` (260 px), e o fiapo só entra se tiver o tom e a cor do piso (`fiapo_r` 0,8 e `fiapo_croma` 0,06): as letras, os aparelhos escuros e as sombras de contato ficam. Todas as plantas refeitas a partir das finais de antes do vinílico, conferidas px a px contra elas (o escuro que clareou: 0 a 15 px nas Casas A a D; na Casa E, só os contornos escuros do piso antigo junto às peças); antes e depois, pranchas, PDFs e book refeitos. O Subsolo da Casa A: a A3 em 4K e os 12K de novo (a correção sobre a mesma saída do Nano Banana Pro, com `--antes_final`; Topaz High Fidelity V2 a 12288 x 9175, job 6b5c99d9-4d23-45cc-9288-1d0f7492459c, fora do git; `montar12k`).

### Subsolo da Casa B, pedidos de 12/11: `pedidos_subsolo_casab_1211.py`

Os pedidos do usuário vendo o Subsolo da Casa B (com os recortes), sobre a final de 21fa118, em passos (`PASSOS`, cada um documentado no script com as falas do usuário):
- **pisos:** Bege Bahia menos manchado (a foto da biblioteca, manchas a 45%) e travertino bruto novo (o do 1º Pavimento da Casa A de 11/11), refeitos pelo `vinilico_foto.trocar` generalizado (`gerar`, `apagar`, `incluir`); a circulação do BH serviço e a faixa acima do BH serviço e da circulação ("O piso continua nessa demarcação") no mesmo Bege da garagem, numa peça só (12/11, "melhorar a representação dos contornos e o piso": antes a faixa era a garagem espelhada e a emenda aparecia).
- **deck:** o deck do Térreo da Casa A (réguas de 20 cm), com o chuveiro da ducha redesenhado.
- **fundo:** o entorno em branco (sem hachura, lote e peças do Térreo nevoadas).
- **perimetro:** o traço de 3 px onde a borda da casa não é parede (contínuo e reto de ponta a ponta na faixa da garagem, até a parede da direita) e o pilar redondo de 30 cm no canto da garagem ("Tem um pilar aqui"; o diâmetro não está no PDF).
- **portas:** as quatro portas de giro (BH serviço, depósito, sauna, BH sauna) com a folha em madeira clara quina a quina com a ponta da parede (as pontas achadas na imagem, que não batiam com o PDF: 1 a 6 px de piso entre a parede e o marco), sem o marco antigo, com soleira de travertino na sauna, no BH serviço e no BH sauna; o "?" do box do BH serviço (o tique do PDF) sai.
- **bancos:** os dois níveis da sauna no travertino novo, em cima mais escuro (frente 0,93, trás 0,86 do piso, espelho 0,78), sombra de contato e pé.
- **ralo:** o ralo cromado na cuba do BH sauna.
- **escada:** o S sai; a seta no degrau de baixo e "SOBE PARA O / JARDIM" abaixo da escada (o modelo do Subsolo da Casa A; no alto, no Térreo, fica a pedra grande junto ao jardim).
- **armario:** o armário da academia na cor padrão da Casa A (RGB 208, 178, 156), liso; o SHAFT sem o nome, com o X tracejado preto.
- **academia:** os aparelhos da Casa B e o retângulo junto à parede de baixo saem (o vinílico refeito nas caixas, preenchidas antes no tom do piso); entram os da final do Subsolo da Casa A (2 esteiras, 2 bicicletas, o supino espelhado; a mesma escala) pelo alfa (`_alfa_aparelho`) com a sombra curta, e a bola de pilates presa na parede ("No lugar dessas linhas, representar uma bola presa na parede. Tirar linhas.": 0,68 m, suporte em U grafite).
- **rotulos:** os rótulos apagados voltam no meio do piso livre de cada ambiente (o recinto do PDF sem os obstáculos, os bancos e os aparelhos novos; nos ambientes abertos, `recorte_px`); o corpo cai só onde não cabe (BH SERVIÇO a 0,72).

**O S sob a seta (13/11, "COLOQUE O S ABAIXO DA SETA"):** a letra da escada, como no Subsolo da Casa A
(`cliente_subsolo_casaa_0511.ESCADA_CS["letra"]`): `ESCADA_SB["letra"]` e `letra_sb`, no fim do passo `escada`: o S
centrado no triângulo, `letra_folga_px` (2,5) abaixo da ponta de baixo, na fonte, no corpo e na cor da descrição (no
degrau de baixo, x 750–758, y 646–658). No 12K, a letra vai aos dados (`_escada_dados`, `escada["letra"]`) e
`_escada_12k` a desenha (A na Inter, B na Kalam, no corpo da descrição). Antes e depois em
`POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_1311_letra_escada_antes_depois.jpg`. (O PDF do cliente do Subsolo da Casa B,
que o `montar12k` lê, vem do Drive para `_pdfs_cliente/642 - SUBSOLO - CASA B.pdf`, fora do git.)

**Os rótulos alinhados (13/11, "ALINHE OS RÓTULOS", com os recortes das duas fileiras):** no passo `rotulos`, as
caixas de todos os rótulos são achadas primeiro (o meio do piso livre de cada ambiente) e, por fileira
(`ROTULOS_SB2["alinhar"]`), o meio de todos vai a uma mesma linha: a linha (y) em que todos cabem livres (sem tocar em
peça, parede ou traço, dentro do ambiente), cada um podendo correr na horizontal até `alinhar_dx_px`, o mais perto de
onde estavam. Fileira de cima: GARAGEM, BH SERVIÇO e DEPÓSITO em y 393 (a CIRCULAÇÃO de cima, acima do vidro, só cabe
com o meio entre y 348 e 357, e o BH SERVIÇO, entre a cuba e a porta, só entre 385 e 393: ela fica no espaço dela);
de baixo: DUCHA, SAUNA, CIRCULAÇÃO, BH SAUNA e ACADEMIA em y 675. Os aparelhos da academia vêm da final do Subsolo da
Casa A do commit de 744adec (`ACADEMIA_SB["final_a_commit"]`, `_final_a`), para o passo refeito dar os mesmos de antes
(a de hoje tem os aparelhos da biblioteca). Refeito desde a final de 21fa118 (só os rótulos mudaram), e a biblioteca de
novo por cima (`biblioteca_subsolo_casab_1311.py --antes <a saída>`); no 12K, os rótulos novos nos dados
(`POE642_CasaB_PH_Subsolo_12K_dados.json`). Antes e depois em
`POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_1311_rotulos_alinhados_antes_depois.jpg`.

**A biblioteca no Subsolo da Casa B (13/11, `biblioteca_subsolo_casab_1311.py`; "VAMOS REVISAR OS MOBILIÁRIOS DO
SUBSOLO DA CASA B", a proposta `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_1311_proposta_biblioteca_{1,2}.jpg`
aprovada com "OK, PODE APLICAR AS RECOMENDADAS"):** as escolhas do Subsolo da Casa A (as funções de
`biblioteca_subsolo_casaa_1211.py`) e os chuveiros desenhados do 1º Pavimento da Casa A, sobre a final de df9a29e:
- sauna: o banco reto de travertino nos dois bancos do PDF (`final3840_casab.SAUNA_F`, o da frente e o de trás; o
  espelho entre eles fica), cada um no tom do de antes (`SAUNA`, `banco`);
- BH sauna: a cuba esculpida esculpida no granito da bancada (`cuba_bhs`: a `cuba_esculpida` da Casa A feita na
  janela girada, porque a parede está à direita, e girada de volta; no tom do granito da bancada em volta, fora a
  torneira cromada), no retângulo da cuba do PDF com a faixa até a parede; a sobra da cuba branca de antes (1 a 3 px
  fora do PDF) vai antes ao piso e ao granito da bancada; a bacia Carrara branca no retângulo do vaso do PDF (a caixa
  na parede da direita), sobre o travertino logo à esquerda (`piso_desloc`, com a costura);
- BH serviço: a bancada no polígono do PDF com o granito da cuba de serviço da biblioteca e a cuba branca com a
  torneira dela (a `servico` da Casa A, com os retângulos da Casa B, `SERVICO`); a bacia Monte Carlo (sem válvula) no
  retângulo do vaso do PDF (a caixa na parede da esquerda; por baixo, o inpaint do piso);
- chuveiros (`CHUVEIROS`, `chuveiro_pos`: o desenho em planta com o braço até a parede em cima, embaixo, à esquerda ou
  à direita): o quadrado de parede na ducha do deck (`ajustes_casab.CHUVEIRO_DUCHA`) e no chuveiro ao lado da sauna,
  o redondo de parede no chuveiro ao lado do BH serviço; os de antes viram o piso do lado; a sombra `chuveiro`; na
  ducha do deck ("CORRIJA O PISO AO INCLUIR NOVO CHUVEIRO": o deck copiado do lado aparecia como um remendo, com as
  juntas fora do lugar), o chuveiro de antes não é mais desenhado no passo do deck de `pedidos_subsolo_casab_1211`
  (`DECK_SB["chuveiro"]` False) e o novo entra direto sobre o deck do gerador, com as réguas contínuas;
- academia: na proposta, sem troca (os aparelhos eram os da Casa A de 12/11, ainda os do render); depois ("E O
  SUPINO? QUERO QUE TROQUE, MANTENDO A BOLA") as 2 esteiras (`esteira-a`), as 2 bicicletas (`bicicleta-b`) e o supino
  (`banco-supino`) da biblioteca no tamanho da Casa A (`ACADEMIA`, `aparelho`: a escala, o banco de 1,60 m e a barra
  alongada vêm de `biblioteca_subsolo_casaa_1211.ACADEMIA`; esteiras 1,76 x 0,77 m, bicicletas 1,23 x 0,51 m, supino
  1,60 x 2,04 m), cada um com o meio no meio do símbolo do PDF da Casa B (a caixa dos traços da ARQ_LAYOUT
  HUMANIZAÇÃO, do tamanho dos da Casa A), o console para a esquerda, o supino espelhado (a barra à direita do banco,
  como no PDF), a sombra curta da Casa A. Os aparelhos de antes saem com a sombra (o alfa deles, como os pedidos
  colaram, mais 6 px, dentro da sala: o vinílico da base com os buracos dos símbolos fechados, porque os pedais das
  bicicletas são cheios no PDF): o vinílico volta com as mesmas réguas (`reguas_academia`: as do `vinilico_foto.trocar`
  dos pedidos, pegas por um espião; a razão final / réguas no piso fica lisa, alta frequência 0,0011) vezes a luz do
  piso em volta (média normalizada). A bola (um disco de 28 px em volta dela) e o armário ficam: a bola e o rótulo
  ACADEMIA com 0 px de diferença; o supino a 16 px do rótulo.
No 12K, `montar12k` chama `pecas_12k` antes dos rótulos: a zona que mudou na final
(`renders/POE642_CasaB_PH_Subsolo_12K_biblioteca_zona.png`) vem da final ampliada sobre a saída do Topaz e as peças de
PNG (bancos, bacias, chuveiros e aparelhos, `renders/POE642_CasaB_PH_Subsolo_12K_biblioteca.json`) entram nítidas na
escala do 12K. Antes e depois em `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_1311_<trecho>_antes_depois.jpg`. Como refazer:
`python3 pedidos_subsolo_casab_1211.py --antes <a final de 21fa118> --saida <png>` e `python3 biblioteca_subsolo_casab_1311.py
--antes <png>` (sem `--saida`, grava a final, o registro do 12K e os antes e depois), depois
o 12K (`ampliacao_12k_subsolo_casab.py montar12k <Topaz ecd1a9e8> --opcao AB`), a prancha, o PDF da Casa B e o book.

**Como refazer:** `python3 pedidos_subsolo_casab_1211.py --antes <a final do Subsolo da Casa B de 21fa118> --antes_depois` (sem `--saida`, grava a final em `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final_rotulos.png`; `--de`/`--ate <passo>` e `--passos <pasta>` para testar um trecho); os antes e depois em `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_1211_<trecho>_antes_depois.jpg`. Depois `rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --no-quadro --render Subsolo=../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final_rotulos.png`, `pdf_entrega.py --config ../../POE642_CasaB/config_bases.json` e `book_entrega.py`. O 12K (opções A e B): `ampliacao_12k_subsolo_casab.py`, abaixo.

**O 12K do Subsolo da Casa B (`ampliacao_12k_subsolo_casab.py`; usuário, 12/11: "gere os 12K do subsolo da casa B"):** o roteiro dos 12K da Casa A (`ampliacao_12k_terreo_casaa.py` para o recorte, o alinhamento e os rótulos em 12K; a correção pelos pisos, como a de `ampliacao_12k_1pav_casaa.py`), com os rótulos da Casa B no lugar dos da Casa A (`_usar_rotulos_b`).
- **`preparar --passos <pasta>`:** a entrada da IA sem textos, a partir do passo `academia` de `pedidos_subsolo_casab_1211.py` (a final antes dos rótulos): o trecho da escada do passo `ralo` só com o S tirado (a seta e o "SOBE PARA O / JARDIM" saem), o vão do shaft sem o X, o ELEVADOR tirado pela conta do alfa. Os 8 rótulos (`renders/POE642_CasaB_PH_Subsolo_rotulos_1211.json`, gravado agora pelo passo `rotulos`) e o ELEVADOR, a escada e o shaft vão para `renders/POE642_CasaB_PH_Subsolo_12K_dados.json`. Recorte 16:9 com a margem da A3: `renders/POE642_CasaB_PH_Subsolo_12K_entrada_ia.png`.
- **Nano Banana Pro (4K, 16:9, `PROMPT`):** job 85520e81-740d-4ce4-955b-ea2337419b0d (5504 x 3072). A IA acinzentou o BH serviço, escureceu o BH sauna e a sauna, pôs bancos de madeira em L na sauna e redesenhou as juntas do deck da ducha, tortas.
- **`corrigir <saída da IA> <corrigida>`:** dentro da casa, tudo o que não é piso volta da entrada (`mascara_pecas`: paredes, portas, soleiras, louças, bancadas, os bancos da sauna, os aparelhos, a bola, o armário, a escada, o elevador); os tons da IA casados com os da entrada (`tom_sigma_px`); ambiente por ambiente, o piso cuja cor (ΔE mediano no Lab) foge mais que 15 volta inteiro da entrada (BH serviço, BH sauna, sauna, depósito, circulações); onde a estrutura foge, também. Ficam da IA a garagem (ΔE 6,4) e a academia (13,5). O deck da ducha volta sempre da entrada (`CORRECAO["da_entrada_px"]`; usuário, 12/11: "as linhas das tábuas de madeira não podem sair tortas"): no mesmo tom (o ΔE passava), a IA tinha refeito as juntas onduladas e com outra paginação. Saída: `renders/POE642_CasaB_PH_Subsolo_12K_saida_nano_banana_pro.png`.
- **Topaz (High Fidelity V2, 12288 x 6858):** job ecd1a9e8-7c47-41f1-8cbf-3b73d30514e6 (o de antes, f24e9a5d, com o deck torto, descartado); a saída fica fora do git.
- **`montar12k <saída do Topaz> --opcao AB`:** a saída alinhada à entrada, na A3 deitada (12288 x 8689, 743 dpi); os tons da final; o fundo em branco puro; o X tracejado do shaft; os rótulos, o ELEVADOR, a seta e "SOBE PARA O / JARDIM" desenhados em 12K (A na Inter; B na Kalam, fator 0,910 em todos). `POE642_CasaB/entrega/POE642_CasaB_PH_Subsolo_12K_opcao_{A,B}.jpg`, prévias `renders/POE642_CasaB_PH_Subsolo_12K_opcao_{A,B}_previa.jpg` e conferências (a final ampliada ao lado) `..._conferencia_{garagem_escada,sauna_bh_sauna,academia,bh_servico_deposito}.jpg`.

**O 12K do Térreo da Casa B (`ampliacao_12k_terreo_casab.py`; usuário, 12/11: "pode fazer o 12K do Térreo da Casa B"):** o roteiro do 12K do Subsolo da Casa B (da IA só os pisos; o resto da casa volta da entrada ampliada) com os textos e os símbolos do Térreo desenhados em 12K, como no da Casa A.
- **A planta sem os textos (`sem_anotacoes_casab.py <passo_bege_escadas.png> <saída> <pasta>`):** os passos de `pedidos_terreo_casab_1211.py` de `escadas` ao fim, de novo, sem as anotações (`terreo_casaa_1011.ANOTAR`: os triângulos e as descrições das 3 escadas e o triângulo da entrada) e sem desenhar os rótulos (`ROTULOS_TB["desenhar"] = False`: os antigos saem como na final, os novos não entram). Conferida contra a final: só os 66 trechos de texto e símbolo mudam. O passo `rotulos` agora grava o desenho de cada rótulo em `renders/POE642_CasaB_PH_Terreo_rotulos_1211.json` (32 rótulos; a final refeita a partir de `passo_pontos` sai idêntica).
- **`preparar <a planta sem os textos>`:** os rótulos que a final traz de antes (`ROTULOS_TB["manter"]`: ELEVADOR, JARDIM DE INVERNO, JARDIM, SPA, PRAINHA, PISCINA) achados na final pela forma (`_achar_rotulos`, notas 0,87 a 0,97) e tirados pela conta do alfa, com o miolo refeito do entorno; no 12K eles voltam pelo PDF (a final tinha o "10,83" e o "m⁴" com o tracejado por cima; o 12K escreve "10,89 m²"). O redesenho dos 32 rótulos e das 7 anotações contra a final: diferença máxima de 1. O recorte é a planta pelas linhas e colunas com mais de 50 px não brancos (`RECORTE`; uns pontos claros soltos acima e abaixo do lote esticavam a caixa): `renders/POE642_CasaB_PH_Terreo_12K_entrada_ia.png` (3426 x 1927, a partir de 190, 28 da final); os dados em `renders/POE642_CasaB_PH_Terreo_12K_dados.json`.
- **Nano Banana Pro (4K, 16:9, `PROMPT`):** job f0a2b150-b3fc-41f7-8a47-fdf608ca8aa3 (5504 x 3072). A IA trocou a pedra portuguesa do leque por um calçamento cinza rachado, em outra escala, e redesenhou as árvores; o resto ficou fiel.
- **`corrigir`:** da IA só os pisos (`PISOS_12K`: travertino, Bege Bahia, vinílico, o marrom, o deck e o gramado, na cor da base, fora das peças do PDF e no tom do piso do lugar; todos passaram no ΔE, de 2,4 a 9); a pedra portuguesa, a água, os móveis, as camas, os carros, as árvores, os tracejados e o resto voltam da entrada ampliada; sob os 6 rótulos de antes fica a textura da IA, nos tons da corrigida (a entrada tinha ali o miolo borrado). Saída: `renders/POE642_CasaB_PH_Terreo_12K_saida_nano_banana_pro.png`.
- **Topaz (High Fidelity V2, 12288 x 6858):** job b44e8511-a768-449b-aba7-fd92ea2e5bdc; a saída fica fora do git.
- **`montar12k <saída do Topaz> --opcao AB`:** `ampliacao_12k_terreo_casaa.montar12k` com os nomes da Casa B (sem os tracejados finos, que vêm da entrada): a A3 deitada (12288 x 8689), os tons da final, o fundo em branco puro, os 38 rótulos, os 4 triângulos e as 3 descrições em 12K (A na Inter; B na Kalam). `POE642_CasaB/entrega/POE642_CasaB_PH_Terreo_12K_opcao_{A,B}.jpg`, prévias `renders/POE642_CasaB_PH_Terreo_12K_opcao_{A,B}_previa.jpg` e conferências `..._conferencia_{varanda_piscina,suites,living_hall,cozinha_servico,garagem_motorista}.jpg`.

### Térreo da Casa B, as regras da Casa A (13/11): `regras_terreo_casab_1311.py`

Usuário: "VAMOS REVISAR OS MOBILIÁRIOS DO TÉRREO DA CASA B E REALIZAR AS ALTERAÇÕES FEITAS NA CASA A LISTADAS ACIMA".
Sobre a final de 4574dc9 (a de 12/11), sem IA nova:
- **letras:** o D sob a seta das 3 escadas (SUBSOLO, DECK, JARDIM), no corpo e na cor das descrições, como no Térreo
  da Casa A; também nos dados do 12K (`POE642_CasaB_PH_Terreo_12K_dados.json`), que o `montar12k` desenha (A na Inter,
  B na Kalam);
- **shafts:** os 2 vãos (`SHAFTS_TB`) no claro com o X cinza fino tracejado e a borda de parede limpa
  (`regras_1211_casaa.desenhar_x`, `limpar_aro`); no 12K, `shafts_12k`;
- **chuveiros (`CHUVEIROS_TB`):** os 10 desenhados em planta: os 2 de teto do banho master, os quadrados de parede dos
  banhos 1, 2 e 3, dos 2 BH gourmet e da ducha do deck, os redondos de parede do BH serviço e do BH motorista; a placa no
  quadrado do PDF, o braço até a face da parede (medida na final); os de antes viram o piso do lado
  (`biblioteca_subsolo_casab_1311.piso_desloc`); na ducha do deck, cada linha das tábuas vem das duas laterais, em
  degradê (`piso_linhas`: copiado de um lado só, o trecho aparecia como uma faixa de outro tom);
- **paredes retas:** `biblioteca_subsolo_casaa_1211.paredes_retas` no cinza 80, com as proteções do Térreo da Casa A
  (objetos do PDF, folhas e esquadrias da ARQ_PAREDE fora do cinza, só o branco ligado à borda é fora) e o elevador
  (`ELEVADOR_TB`): 45 px de entalhes, 6345 px de dentes e linhas soltas, 173 px de aresta;
- **tapetes das suítes (`TAPETES_TB`, `tapetes`; "NÃO VOU QUERER TROCAR AS CAMAS QUE EU JÁ COLOQUEI, MAS QUERO O RETOQUE
  EM VOLTA DO CONTORNO E NOS TAPETES"):** o tapete do PDF de cada suíte (master, 1, 2 e 3) refeito inteiro com o da
  biblioteca no tom de hoje; as camas de 12/11, os bancos, o sofá e os criados por cima pelo contorno do PDF de cada
  peça, com a sombra curta dos móveis (o halo da IA em volta das camas saiu); na master, a dobra do edredom do PDF passa
  da cama da IA e ali entra o tapete (`fora_px`);
- **esquadrias pretas (`ESQUADRIAS_TB`, `esquadrias`):** a 1ª tentativa (o traço neutro escurecido pela cor) ficou
  irregular; a prévia (`POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_previa_esquadrias_pretas.jpg`) desenhava os
  traços do PDF (ARQ_PAREDE e, nas louças, os vidros dos boxes, longos e finos) em preto onde a final mostra vidro ou
  alumínio neutro; o usuário: "FAÇA APENAS O CONTORNO DA ESQUADRIA EM PRETO": o traço fino (0,5 px), só o contorno, o
  vidro claro por dentro; a madeira das portas de giro, o bronze dos brises e os chuveiros não mudam; no 12K o contorno
  é redesenhado na escala dele (`esquadrias_12k`, onde a final aceitou o perfil: o canal 2 de `REG_MASC`).
No 12K, `ampliacao_12k_terreo_casaa.montar12k` com `PAV` "Terreo_CasaB" chama `regras_terreo_casab_1311.pecas_12k`
(a zona que mudou, `renders/POE642_CasaB_PH_Terreo_12K_regras_zona.png`, da final ampliada, e os chuveiros nítidos;
`biblioteca_subsolo_casab_1311.pecas_12k` agora aceita o registro e a zona de outro pavimento e um `peca(it)` para os
tipos novos) e `shafts_12k`. Topaz b44e8511 baixado de novo (fora do git). Antes e depois em
`POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_{letras_escadas,shafts,chuveiros_banhos,chuveiros_servico}_antes_depois.jpg`.
Como refazer: `python3 regras_terreo_casab_1311.py` (sem `--antes`, parte da final de `ANTES_COMMIT`), `python3
ampliacao_12k_terreo_casab.py montar12k <Topaz b44e8511> --opcao AB`, a prancha, o PDF da Casa B e o book.

**As peças do Higgsfield, o jardim de inverno e os rótulos em grade (13/11, no mesmo `regras_terreo_casab_1311.py`):**
- a geladeira inox (G2) nos 3 retângulos da cozinha, a frente para a ilha; o banco estofado capitonê (B1) no closet
  master ("NO CLOSET MASTER TEM UM BANCO ESTOFADO QUE PRECISA SER REPRESENTADO COMO BANCO ESTOFADO");
- os recamiers da suíte master ("PRECISO TROCAR OS RECAMIERS DA SUITE MASTER TAMBÉM", "GOSTO DO RECAMIER COM MAIS
  GLAMOUR", "CUIDADO COM A PROPORÇÃO DO RECAMIER E MESA LATERAL", "PODEMOS USAR OUTRO MODELO DE RECAMIER QUE TENHA AS MESMAS
  DIMENSÕES DO ORIGINAL?", "R11"): o R11, gerado na medida do original (0,70 x 1,50 m), espelhados; o de antes achado na
  imagem (o branco do bouclé ligado ao retângulo do PDF, mais 8 px de sombra) e o piso por baixo em espelho, linha a
  linha, dentro da madeira contígua (até 16 px de cada lado: o reflexo não alcança a janela nem a cortina); as mesinhas
  de encaixe de volta por cima, no tamanho do PDF;
- a cortina de linho em ondas (C4) nos trilhos do PDF (`ajustes_casab.trechos_cortina_b`, os que se sobrepõem unidos,
  de parede a parede), o trilho grafite do lado do vidro, sobre o piso em espelho;
- o jardim de inverno com um X só, de canto a canto, interrompido em volta do rótulo; as 3 folhas de baixo encostadas;
- os rótulos SUÍTE 1/2 e CIRCULAÇÃO/SUÍTE 3 em grade (y 560 e 695; x 2135 e 2416); no 12K, os desvios novos nos dados;
- as esquadrias pretas só com os traços da ARQ_PAREDE e, das louças, só os vidros dos boxes (até 80 px de um chuveiro):
  os traços longos das camas e dos recamiers, na mesma camada, ficavam pretos.
No 12K, o texto dos rótulos movidos e o do JARDIM DE INVERNO ficam fora da zona trazida da final (o 12K os desenha
nítidos) e o X do jardim é redesenhado na escala dele. As peças recortadas por `pecas_higgsfield_1311.py`.

**O mobiliário decidido (13/11, no mesmo `regras_terreo_casab_1311.py`, 1ª etapa: as trocas no lugar):** as 15
respostas, uma a uma, com as peças e as convenções da Casa A (`MOBILIARIO_TB`, `mobiliario`), no retângulo do PDF de cada
peça; o giro pela parede (0: a parede em cima; 180: embaixo; 90: à esquerda; -90: à direita):
- criados da Casa A no tom da madeira das bancadas, com o abajur visto de cima (`ABAJURES_TB`): retangulares na master, na
  suíte 2 (em pé, entre as camas) e na 3; redondos na suíte 1, como o PDF;
- banho master: a bancada dupla esculpida (as 2 cubas caem nas do PDF) e as 2 bacias Carrara brancas;
- banhos 1, 2 e 3: a cuba esculpida de travertino na bancada inteira, a cuba no lugar da do PDF
  (`biblioteca_1pav_casaa_1211.cuba_na_bancada`: o c conta da ponta direita do PNG), e a bacia Carrara branca;
- lavabo: a cuba esculpida de poros e a bacia no marrom dos vasos; BH gourmet: as bacias marrons e, no lavatório, a cuba
  esculpida de travertino em cada bloco do PDF (mais estreita que o PNG: `cuba_estreita`, os lados viram um aro fino);
- BH serviço e BH motorista: só a louça da cuba (`BT.so_louca`; "A BANCADA DO BH. MOTORISTA É MARROM TABACO": a bancada
  fica) e a bacia Monte Carlo;
- cozinha e gourmet: o cooktop de 4 bocas no meio do de 5, o resto vira bancada (`balcao`: cada metade com o granito do
  lado, deslocado ao longo da bancada, a emenda e a borda em rampa; a costura de tom do `piso_desloc` manchava os pontos
  do granito); as cubas Franke da pia, a cuba com misturador e a grelha da Casa A (62 x 32 px) no meio da churrasqueira
  do PDF; os tanques Franke na área de serviço;
- "FALTOU A CADEIRA DE ESCRITORIO NAS ESCRIVANINHAS": a cadeira de escritório da Casa A (34 px) nas 3 escrivaninhas (suítes
  master, 1 e 2), 1/3 por baixo da mesa, o encosto para fora (`CADEIRAS_TB`, `cadeiras`); a de antes sai (o piso em
  espelho, sem tirar da madeira da mesa) e a mesa volta por cima, com a sombra curta dela só na cadeira (`mesa_sobre`).
No 12K: as peças nítidas do PNG (`peca_12k`, tipo "bib"); os abajures e as mesas por cima das cadeiras vão em `topo` do
registro (`topo_12k`): a mesa da saída do Topaz, pelo alfa do PDF ampliado. O contorno das esquadrias no 12K não passa por
cima das peças novas. Corrigido junto: na final de ca1ed82 os 4 rótulos em grade saíram em dobro (a 2ª rodada lia dos
dados os desvios já movidos e tirava o rótulo de antes no lugar novo); o desvio de partida agora vem dos dados do
`ANTES_COMMIT`. Antes e depois em `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_mob_<trecho>_antes_depois.jpg`.
**A 2ª etapa ("PODE FAZER A 2ª ETAPA"; `SALA_INTIMA_TB`, `JANTAR_TB`, `ESPREG_TB`, `BANQUETAS_TB`):** o que refaz o
piso por baixo das peças de antes (`piso_saltando`: linha a linha ou coluna a coluna, pulando o que não é piso até
achar a fonte; `ancorar` deixa as emendas das tábuas em pé numa beira inclinada; um lado com menos de 4 px de fonte, a
beira escura junto a uma parede, não serve):
- sala íntima: o tapete, o sofá em L A (o "anti_t" da Casa A: o corpo comprido contra a parede da direita e a ponta em
  cima; com os traços finos do encosto do PDF, 92% de sobreposição com o L), as 2 mesas laterais redondas nos círculos
  do PDF e a poltrona A no símbolo do PDF (o encosto para o elevador, a frente para a sala; 225°, 50 x 52 px); a mesa de
  centro redonda fica (de volta por cima, pelo contorno do PDF). O PDF tem uma poltrona só (a proposta dizia 2).
  Depois ("PÕE UM BANCO ESTOFADO, COMO SE FOSSE UM PUFF NA FRENTE DA POLTRONA"): o retângulo girado do PDF na frente
  dela (0,62 x 0,43 m, de través: o pufe da poltrona), que o render tinha feito de mesa de madeira, é o pufe estofado da
  Casa A (`03-primeiro-pavimento/suite-master/pufe`, 45°); o piso refeito em volta no tom do entorno
  (`tom_do_entorno`: a fonte de longe, perto da janela, é mais clara; a beira junto às paredes fica fora da fonte);
- jantar: as 10 cadeiras oliva da Casa A (30 px) no centro de cada cadeira do PDF, viradas para a mesa (o travertino
  refeito coluna a coluna em cima e embaixo, linha a linha nas pontas); a mesa e o aparador ficam, a mesa de volta por
  cima com a sombra curta nas cadeiras (`mesa_por_cima`; no 12K, a da saída do Topaz);
- prainha: as 2 espreguiçadeiras A (`02-terreo/deck-piscina/espreguicadeira-a.png`, trazida do pacote da biblioteca) no
  retângulo do PDF, a cabeceira à direita (a parte menor do PDF);
- gourmet: as 5 banquetas B (25 px) no lugar das 5 de hoje (o PDF desenha 4, desiguais), ~40% por baixo da bancada (a
  borda em y 1319,3): as linhas do PNG além dela saem (`corte_y`, também no 12K).
Antes e depois em `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_mob_{sala_intima,jantar,prainha,banquetas}_antes_depois.jpg`.

**A proposta do mobiliário (13/11):** `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_proposta_biblioteca_{1,2,3}.jpg`
(17 trechos; as escolhas da Casa A marcadas). O usuário: "NÃO VOU QUERER TROCAR AS CAMAS QUE EU JÁ COLOQUEI, MAS QUERO
O RETOQUE EM VOLTA DO CONTORNO E NOS TAPETES" (as camas de 12/11 ficam; os tapetes refeitos e o contorno limpo); peças
novas geradas no Higgsfield (a biblioteca não tem): geladeira, recamier da suíte master, banco estofado do closet master e
cortina, 4 variantes de cada em `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_pecas_higgsfield.jpg`, para a escolha.

### Térreo da Casa B, pedidos de 12/11: `pedidos_terreo_casab_1211.py`

Os pedidos do usuário vendo o Térreo da Casa B (com os recortes da prancha), sobre a final de 21fa118, em passos (`PASSOS`, cada um documentado no script com as falas do usuário):
- **marrom:** o granito marrom do piso (cozinha, louceiro, despensa, serviço, motorista, área descoberta) trocado pela amostra do cliente (a mesma da Casa A), tecido por quilting, com a luz da final; as bancadas em marrom tabaco ficam no tom escuro; as letras brancas dos rótulos ficam (`texto_claro`).
- **bancadas:** a ilha da cozinha, a bancada da esquerda do serviço e os tanques em Dekton Danae; as bancadas dos BH serviço e motorista em marrom tabaco (a cuba em outro tom); as prateleiras do louceiro e da despensa lisas, na cor neutra da Casa A; as duas máquinas de lavar sem bancada por cima; a bancada da pia gourmet sem os traços dos armários ("Não precisa representar os armários inferiores ou superiores").
- **gourmet:** a churrasqueira e as 5 banquetas altas (linho) num tom que destaca do piso.
- **deck:** os decks na madeira do Térreo da Casa A, com a linha de instalação do chuveiro (e o braço) no deck da ducha.
- **portas:** as 21 portas de giro com a folha em madeira clara quina a quina com a parede (`cliente_subsolo_casaa_0511.portais_cs`), sem o marco antigo; louceiro e despensa sem soleira.
- **escadas:** o D sai das três (6 degraus, 9 degraus, blocos de pedra); o triângulo no degrau de cima e "DESCE PARA O / SUBSOLO", "DESCE PARA O / DECK", "DESCE PARA O / JARDIM".
- **entrada:** a soleira da entrada da Casa C de batente a batente, sob a folha da porta pivotante, com os batentes na cor da parede; a seta antiga sai e o triângulo fica no centro do vão.
- **tracejados:** o retângulo tracejado de fora do lote, o tracejado da borda da direita e a ponta do muro de baixo saem; os dois shafts pequenos e o do elevador no fundo claro, com o X de canto a canto (sem o nome SHAFT); o pergolado antigo sai (volta no passo `pergolado`).
- **moveis:** os sofás da varanda e do living e o pufe sem o contorno (o tecido de novo, com vincos suaves); a barra de madeira sobre o sofá da varanda sai (a mesinha fica); o banco branco vira mesa de centro de madeira; a mesa em gota sem a cruz do pé.
- **closets:** o closet master em U e os guarda-roupas em L das suítes 1, 2 e 3 numa peça só, sem a divisão no canto (`um_pav_casaa_1111._closet`).
- **banco:** o banco estofado no meio do closet master (o banco da varanda da Casa A).
- **espreguicadeiras:** a textura de tecido no tampo das duas da prainha.
- **folhas:** as 11 folhas de correr de madeira (suíte master, fachada de cima, suíte 3) folha por folha, em ripado de nogueira (o desenho das folhas do 1º Pavimento da Casa A), com a faixa até o vidro no piso de fora.
- **gramado:** a grama do Térreo da Casa A e o paisagismo B (`paisagismo.py`): 3 plantas nos cantos e maciços pequenos, sem as árvores do render.
- **jardins:** o jardim de inverno e o de 4,62 m² como o jardim interno da Casa A (a grama e poucas plantas menores; no de inverno, o X fino e claro, fora do rótulo); a planta em vaso do hall vira uma palmeira pequena; a floreira do lavatório gourmet com 7 arbustos verdes iguais, igualmente espaçados.
- **perimetro:** o traço de 2 px no cinza das paredes onde o piso da casa encosta na grama sem parede.
- **pergolado:** (usuário: "representar o pontilhado em preto também, deixando as linhas do pergolado mais finas e mais claras, tudo na mesma cor") os traços do PDF de novo, finos (0,8 px) e numa cor só, em preto (cinza 22), também sobre a grama.
- **vidros_agua:** (usuário: "Corrigir o tom da água entre os vidros") o canal entre os dois vidros da borda esquerda da piscina, que estava no turquesa saturado de antes da água C, no tom da água da piscina ao lado (média e desvio de cada canal casados com os dela, o desenho da água mantido; os fios dos vidros ficam).
- **defeito:** (usuário, sobre o "?" na ponta das paredes do BH gourmet da esquerda: "deve ser um defeito a ser removido") a caixa cinza do nicho acima do BH (no PDF, o retângulo do "Ref." com o tracejado de armário) sai; o nicho fica no travertino da varanda.
- **floreiras:** (usuário: "Deixar o tom da vegetação dos jardins nas janelas diferente do terreno"; "para floreira use como inspiração um trecho da imagem anexa") as 4 floreiras da fachada de cima com a folhagem do trecho da referência (`_texturas/originais/floreira_flores_brancas_ref.png`, a floreira em pé do quintal de referência): deitada, na escala da planta, tecida por quilting, mais verde e viva (matiz, saturação e brilho acima) e com as flores brancas miúdas salpicadas; a sombra de contato junto à caixa.
- **bege_escadas:** (usuário: "reduzir as manchas do bege bahia nas escadas") a faixa média (as manchas) do Bege Bahia dos blocos e da escada de 6 degraus a 45%, sem mexer nas bordas, nas sombras curtas e nas letras.
- **ralos:** (usuário: "adicionar ralos das pias") 5 ralos (pia da cozinha, pia gourmet, tanques), o desenho dos ralos da Casa A (`terreo_casaa_1011._ralos`).
- **portas_fechadas:** (usuário: "feche as portas"; "Não precisa representar as portas abertas") a porta de duas folhas da área de serviço: as folhas abertas saem e as duas entram fechadas no vão.
- **cozinha:** (usuário: "corrija os erros do cooktop"; "alterar a cor da bancada para dekton danae"; "alterar para o tom de madeira padrão de armario"; "melhorar a representação da cuba e o contorno da bancada em marrom granito") o cooktop de 5 bocas da biblioteca de novo sobre o Danae da ilha; a bancada da pia em Dekton Danae; o armário junto ao nome no tom padrão de armário; BH serviço e BH motorista com a bancada em marrom tabaco, o contorno, a cuba de louça branca e a torneira cromada.
- **quina:** (usuário: "não há batentes, apenas parede. porta com a quina da parede, quina a quina"; "remova todos os batentes e faça parede") as 22 portas de giro quina a quina: no lugar dos batentes, a parede (42 trechos) do fim da parede até a face da folha e, do outro lado, da ponta da folha até a parede; a porta do corredor da adega entra.
- **tapete:** (usuário: "remova essas linhas vermelhas do tapete") os dois fios laranja do tapete da suíte master saem.
- **poltronas:** (usuário: "faça o mesmo que fizemos na casa A com as poltronas. apenas o revestimento do encosto em terracota") o encosto vinho das 2 poltronas do living no terracota da Casa A (`sala_1111.SALA_1111["terracota"]`), pela diferença por px (a luz fica).
- **sofa_living:** (usuário: "traga realismo para esse sofá"; "corrija os erros de acabamento dessa mesa de centro. tem uns pontos pretos") o sofá do living em L peça a peça (encosto, almofadas, 4 assentos, braço, 3 almofadas soltas) com a sombra macia; a mesa de centro em gota sem os pontos pretos, a beira antisserrilhada.
- **cadeiras:** (usuário: "revise as cadeiras das escrivaninhas e traga mais realismo para elas. se for o caso, substitua-as.") as 3 cadeiras chapadas (suíte master, suíte 1, suíte 2) saem e entra a de madeira e linho da biblioteca (a da escrivaninha da suíte 3 do 1º Pav da Casa A), virada para a mesa, 1/3 sob o tampo.
- **varanda_ia:** (usuário: "vamos trazer mais realismo para esses mobiliarios, preservando-os, mas trazendo do 3D para a planta humanizada. use o higgsfield") o estar da varanda pelo Nano Banana Pro (Higgsfield): o recorte 5:4 foi 4x maior com o pedido de manter lugar, tamanho e cor de cada peça (o sofá virado para as mesas, encosto embaixo); a variante escolhida, alinhada por ECC afim, fica em `POE642_CasaB/renders/ia/POE642_CasaB_Terreo_varanda_estar_nbp_alinhado.png`; entram o tapete e as 8 peças nas silhuetas do PDF, cada uma com o ganho do próprio tom; em volta, só a sombra da IA sobre o piso original limpo dos restos das peças velhas.
- **poltronas_varanda:** (usuário: "ainda está diferente do que eu esperava. segue o que eu espero dessas poltronas") as 2 poltronas da direita do estar da varanda no modelo das poltronas do living (concha terracota, assento branco): a poltrona do living recortada pela silhueta do PDF, girada e escalada até cobrir a silhueta de cada uma (IoU 0,88), 1 px maior na beira; a sombra curta da IA fica. Na mesma leva, a sombra da poltrona redonda: a sombra da IA não conta mais como peça (a beira em degrau sai).
- **brises:** (usuário: "corrija os brises") a faixa dos 11 brises junto ao jardim de 4,62 m² refeita (lâminas velhas e restos escuros fora), o tracejado do pergolado de volta só nela e as lâminas do PDF desenhadas por `final3840_casab.brises` (alumínio grafite, aresta de luz, contorno fino, sombra curta).
- **despensa:** (usuário: "corrija o erro na prateleira da despensa") o dente claro da prateleira da direita sobre o piso refeito das mesmas colunas acima.
- **pontos:** (usuário: "remova o ponto preto"; "remova o vestígio da cuba referente ao tracejado branco, bem na lateral") o puxador escuro do box do banho master, que saía para o piso como um ponto; a aba branca na lateral da cuba da pia gourmet (a borda refeita da linha limpa, o granito de baixo).
- **living_ia:** (usuário: "vamos substituir por um sofá mais realista que seja semelhante ao proposto, bem como a mesa lateral e a luminária de parede? traga-me duas opções para aprovar."; "opção A, pode instalar"; "gostei da poltrona assim, gostei da sombra da mesa de centro assim, gostei da mesa lateral assim e da luminária de parede. pode aplicar?") o estar do living pelo Nano Banana Pro (Higgsfield), em três camadas, cada uma alinhada ao seu recorte (a IA volta no mesmo enquadramento; ajuste fino por correlação de gradientes, ≤ 1 px): (1) o sofá em L da opção A (bouclé off-white), `POE642_CasaB/renders/ia/POE642_CasaB_Terreo_living_sofa_nbp_opA_alinhado.png`, na pegada do `SOFA_LIVING_TB`; (2) a mesa lateral de travertino e a arandela preta da opção B (`..._opB_alinhado.png`; o sofá de linho greige dela não entra), PDF 78383 e 63984; (3) as 2 poltronas inteiras em terracota e a mesa de centro sem o contorno cinza, com a sombra macia, de uma geração nova do recorte maior do estar (x 1660–1980, y 805–985, já com o sofá A) com a opção B de referência (`..._living_estar_nbp_alinhado.png`), PDF 64047, 64139 e 64285, e a sombra da IA até 7 px em volta. Em cada camada, cada peça + 2 px e o que a IA desenhou encostado nela, com o ganho do fundo; o que uma camada anterior pôs fica; as linhas escuras de fora (o caixilho do vidro) ficam. As opções em `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1211d_living_{opcoes_antes_A_B,opcao_A,opcao_B}.jpg`.
- **estar_varanda:** (usuário: "mantenha o realismo, mas corrija a posição do encosto e adicione o encosto para o outro lado também. Ao aplicar o realismo, não podemos alterar a composição e dimensões existentes no PDF base..."; "melhore o aspecto com mais realismo nessas poltronas") duas camadas do Nano Banana Pro pelo `_living_camada`: o sofá de dois lados da varanda (PDF 64428) gerado com o desenho do PDF do sofá de referência, na mesma escala (encosto no meio, almofadas e assentos dos dois lados, pufe à direita), `POE642_CasaB/renders/ia/POE642_CasaB_Terreo_varanda_sofa2lados_nbp_alinhado.png`, com a mesa lateral 66895 protegida e a tábua que a IA inventou no assento refeita do módulo ao lado (`remendos_ia`); e as 2 poltronas terracota giradas (66910, 67076) realistas, `..._varanda_poltronas_nbp_alinhado.png`.
- **pontos (12/11, 4ª leva):** o botão escuro do registro do BH gourmet da esquerda (o piso de cima e a beira do registro); o registro da ducha da direita do banho master como o espelho do da esquerda (`espelho_x`; usuário: "volte o registro da ducha à direita. deve ficar igual ao registro do lado esquerdo").
- **rotulos (COZINHA):** fixo com `cx` e `fundo` (usuário: "suba mais esse rótulo"), no meio do piso livre acima da ilha.
- **bancada_cozinha (depois dos rótulos):** (usuário: "corrija esses erros na bancada da cozinha"; "corrija o erro na bancada da ilha da cozinha") a beira esquerda da perna vertical do L (PDF 24219, x 1786,2) sem o tracejado do armário antigo (piso e bancada das colunas ao lado, a coluna da beira na cobertura do PDF) e a mancha clara à direita da ilha (o remendo do rótulo antigo) refeita de 24 px abaixo.
- **living_ia, 4ª camada:** (usuário: "OPÇÃO BANCO b") o banco trançado do living na opção B (estrutura de nogueira e trama de cordão de papel off-white), na silhueta do PDF (67349), com a IA da opção (`renders/ia/POE642_CasaB_Terreo_opcao_bancoB_nbp_alinhado.png`); antes e depois em `..._1211g_banco_living_antes_depois.jpg`.
- **camas_ia (depois do living_ia):** (usuário: "gostei da cama com a cabeceira cinza e o jogo de cama com metalessa"; "já atualize o sofá na frente da cama de casal com realismo e os bancos/sofá onde tem, também, em frente as camas"; "na suíte 3, não há banco e nem sofá em frente a cama de casal") a combinação das opções de cama (cabeceira e base estofadas em linho cinza claro da A; colcha matelassê branca, almofadas e peseira de veludo bordô da B) em todas as camas, quarto a quarto pelo Nano Banana Pro com a combinação de referência, junto com o que há aos pés da cama em linho cinza claro (o banco com 2 rolos da suíte master, o sofá de 2 lugares da suíte 1, os 2 bancos da suíte 2; a suíte 3 sem nada), cada camada em `CAMAS_TB` pelo `_living_camada` nas silhuetas do PDF (`renders/ia/POE642_CasaB_Terreo_cama_<quarto>_nbp_alinhado.png`), com os criados-mudos de antes (`protege`). Duas opções novas do `_living_camada`: `estica_ia` (a cabeceira da master esticada na largura da cabeceira do PDF, atrás dos criados-mudos) e `corta_px` (os cantos onde a peça da IA é menor que a silhueta voltam ao fundo limpo, sem a sombra escura da IA). O ganho do fundo, sem tapete nem piso claro (os quartos de piso marrom), vem do piso fora das peças; as silhuetas do PDF ficam em cache (`_SIL_CACHE`).
- **Opções para aprovar (12/11):** o banco trançado do living (A: carvalho e palhinha; B: nogueira e cordão de papel off-white) e as camas (A: cabeceira estofada greige e edredom de linho; B: carvalho e matelassê), em `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1211e_{banco,cama_casal,cama_solteiro}_opcoes_antes_A_B.jpg`; as IAs alinhadas em `renders/ia/POE642_CasaB_Terreo_opcao_*_nbp_alinhado.png`.
- **pedras:** (usuário: "corrija os contornos das pedras") as 9 pedras do acesso como os retângulos do PDF, a beira antisserrilhada, o aro fino da Casa A, topo e base alinhados; os restos claros da beira velha viram grama.
- **rotulos:** (usuário: "centralize todos os rótulos e deixe-os alinhados") os 32 rótulos (menos os da água, dos jardins e o ELEVADOR) saem e voltam no meio do piso livre de cada ambiente, alinhados pela linha de baixo do texto em 7 faixas (banhos, suítes, closet e sala íntima, living e halls, louceiro/despensa/área de serviço, BH e quarto de serviço, banhos e lavatório gourmet) e numa coluna (depósito, quarto e BH do motorista); onde não cabe, cai a 0,85 e 0,72; o BH SERVIÇO fica no lugar achado (`no_lugar`); depois (usuário: "alinhe sala intima com circulação"; "coloque o rótulo da varanda/gourmet mais a direita sem ficar na sombra do sofá, mas alinhado com o rótulo do living"; "corrija o rótulo do louceiro para cor branca e centralizado"): SALA ÍNTIMA na faixa da CIRCULAÇÃO, que não sai do lugar (`ancoras`); VARANDA/GOURMET entre a sombra do sofá e a linha da varanda, a 0,92, na linha do LIVING (`fixos`); LOUCEIRO branco no meio do piso marrom (`fixos`).

**Como refazer:** `CACHE_TB=<pasta> python3 pedidos_terreo_casab_1211.py --antes <a final do Térreo da Casa B de 21fa118> --antes_depois` (sem `--saida`, grava a final em `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png`; `--de`/`--ate <passo>` e `--passos <pasta>` para testar um trecho; `CACHE_TB` guarda os tecidos demorados); os antes e depois em `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1211_<trecho>_antes_depois.jpg`; a 2ª leva (do bege das escadas aos rótulos, contra a final de 90dca67) em `..._1211b_<trecho>_antes_depois.jpg`; a 3ª (poltronas da varanda, rótulos, brises, despensa, pontos, contra a final de 0239e34) em `..._1211c_<trecho>_antes_depois.jpg`. A 4ª (o estar do living, contra a final de db4cbf8) em `..._1211d_{living_estar,varanda_living}_antes_depois.jpg`. A 5ª (varanda, cozinha, registros, contra a final de f76d874) em `..._1211e_<trecho>_antes_depois.jpg`. A 6ª (as camas, contra a final de 87dab88) em `..._1211f_{camas_suite_master,camas_suites_1_2,camas_suite_3,cama_quarto_servico,cama_quarto_motorista}_antes_depois.jpg`. Depois `rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --no-quadro --render Terreo=../../POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png`, `pdf_entrega.py --config ../../POE642_CasaB/config_bases.json` e `book_entrega.py`.

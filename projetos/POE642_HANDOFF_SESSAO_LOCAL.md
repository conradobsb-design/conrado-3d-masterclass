# POE 642 · Casas A e B — handoff para continuar no computador local
_14/10/2026. Estado ao fim da sessão na nuvem. Branch: `claude/poe642-casa-a-handoff-jmchm3`. PR: conradobsb-design/conrado-3d-masterclass#1 (rascunho)._

Este arquivo é o ponto de partida da sessão no computador. Ele resume o que já foi feito, as decisões do cliente, como o trabalho é feito, os comandos de cada script e o que falta. A sessão nova não traz o histórico da conversa: tudo o que importa está aqui e nos arquivos citados.

---

## 1. Como trabalhamos (preferências fixas)

- **Prompts:**
  - depois de qualquer mudança, entregar o prompt completo, nunca só o trecho alterado;
  - cada prompt tem duas partes: a versão de validação em PT, só para leitura, e o prompt para o motor em EN, para colar inteiro;
  - nunca chamar o retorno do cliente de "correções" dentro do prompt;
  - cada versão é um arquivo `.md` novo (v1, v2…), e os ajustes sobre um render aprovado viram `_ajuste`.
- **Motor:** Higgsfield Nano Banana Pro, image-to-image, 2K, 16:9, PNG, com uma única imagem de entrada: a base do pavimento.
- **Visual:**
  - luz chapada, clara e uniforme, sem sombra projetada;
  - fundo branco puro;
  - vista de cima ortográfica, sem texto.
- **Materiais:** sempre os definidos pelo cliente.
- **Bases:** saem sempre dos PDFs do cliente, pelo `gerar_bases.py`.
- **Escala:** manter a escala existente. A planta não pode ser aproximada, recortada nem centralizada, porque todas as plantas da mesma folha caem no mesmo quadro.
- **Quando o render chega perto:** retocar localmente, sem IA, com os scripts de retoque, em vez de rodar o motor de novo. O Nano Banana Pro não aceita máscara e redesenha a imagem inteira a cada edição.
- **Imagem final (desde a Casa B):** a base em alta resolução vira a final. Do render vêm só os elementos fotorrealistas, nas posições da base. Onde o render não tem elemento para trocar, fica o que a base tem.

**Erros recorrentes do motor, e o que já funciona contra cada um:**

| Erro | O que resolve |
|---|---|
| Inventa ambientes, cômodos e objetos | "Nothing is added", ambientes descritos por posição e portas contadas |
| Erra chuveiros (teto ou parede, parede errada) | Descrever banho por banho, com o tipo e a parede. Na base, os chuveiros de teto viram placas cinza. |
| Lê o eixo das janelinhas como registro ou chuveiro | `eixo_janela_max_pt` no `gerar_bases.py` |
| Cria banco em L na sauna | Dizer que há só o banco reto. Se insistir, retoque local. |
| Pinta o entorno esmaecido com a cor cheia | Retoque local com a base |
| Some com os arcos das portas | Retoque local com a base |
| Aproxima a planta para preencher o quadro | Item "SCALE AND FRAMING" no prompt |
| Usa madeira laranja | "never orange" |
| Deixa o Bege Bahia manchado | "uniforme, quase liso, sem manchas" |

---

## 2. Onde está cada coisa

```
projetos/
  POE642_HANDOFF_SESSAO_LOCAL.md      ← este arquivo
  POE642_CasaA/
    POE642_CasaA_HANDOFF_ClaudeCode.md   handoff original da Casa A
    METODO_Planta_Humanizada.md          método em 5 etapas (base → render → trava → retoque → pós)
    PESQUISA_IA_Plantas_Humanizadas.md
    POE642_CasaA_PH_<Pavimento>_vN.md    prompts (PT + EN) e ajustes
    bases/                               bases geradas dos PDFs (Térreo v4–v6, Subsolo v1–v4, 1º Pav v1–v3)
    renders/                             renders do motor e versões retocadas
    entrega/                             pranchas, rodapés, PDF do cliente, GIF, assets (logos, norte, fontes)
    scripts/                             todos os scripts (servem às duas casas) + README.md + config da Casa A
  POE642_CasaB/
    config_bases.json                    config da Casa B (usa os scripts da Casa A)
    POE642_CasaB_PH_Subsolo_v1.md, v2.md prompts
    bases/                               Subsolo v1 (cores do PDF), v2 (legenda) e v3_texturas
    renders/                             render do motor (v2) e a imagem final
```

O `scripts/README.md` documenta cada opção do `config_bases.json` e todos os scripts.

---

## 3. Preparar o computador

1. **Trazer o trabalho:**
   ```bash
   git fetch origin claude/poe642-casa-a-handoff-jmchm3
   git checkout claude/poe642-casa-a-handoff-jmchm3
   ```
2. **Instalar as dependências**, com Python 3.10 ou mais novo:
   ```bash
   pip install pymupdf numpy scipy pillow opencv-python-headless pyflakes
   ```
3. **Fontes:** o rodapé usa a Inter, que já vem no projeto em `POE642_CasaA/entrega/assets/fontes/` (licença SIL OFL). Não precisa instalar nada.
4. **PDFs do cliente:** eles não estão no repositório. Crie uma pasta local, por exemplo `projetos/_pdfs_cliente/`, que não vai para o git, e coloque nela:
   - **Casa A:**
     - Térreo: o PDF com a layer `ARQ_PAREDE`, que foi enviado direto na conversa;
     - `642-_SUBSOLO_CASA_A_1.pdf`;
     - `642-_1__PAVIMENTO_CASA_A_1.pdf`.
   - **Casa B:** `642 - SUBSOLO - CASA B.pdf` e `642 - TÉRREO - CASA B.pdf`.
   - **Casa C:** `642 - SUBSOLO - CASA C.pdf`.
   - **Referência (Drive do cliente):** pasta `10UABd77xZ9V2R3G85xkOdnvg1kCgrsMj`, com `642-ARQ-EX-001-…-LAYOUT-R01.pdf` (folha de layout, de onde vieram o norte e o carimbo), 002, 005, 006 e 021. Esses PDFs **não** têm a layer `ARQ_PAREDE`, por isso não servem para gerar base.
5. **Conferir:** rode os scripts de dentro de `projetos/POE642_CasaA/scripts/`, porque os caminhos são relativos a essa pasta.

---

## 4. Os scripts, na ordem do método

Todos ficam em `projetos/POE642_CasaA/scripts/` e servem à Casa A e à Casa B. Para a Casa B, passe `--config ../../POE642_CasaB/config_bases.json`.

| Etapa | Script | O que faz |
|---|---|---|
| 1. Base | `gerar_bases.py` | Faz a base a partir do PDF. Ver os detalhes abaixo. |
| 1b. Texturas | `texturizar_base.py` | Troca as cores da legenda pelas texturas aprovadas da Casa A, para a base já mostrar os pisos ao motor. |
| 2. Render | (motor) | Prompt `.md` + base `_16x9`. |
| 4. Retoques | `elementos_do_render.py` | Faz da base a imagem final, trazendo do render só os objetos fotorrealistas. Onde não há objeto, fica a base. |
| 4. Retoques | `acabamentos_finais.py` | Troca os símbolos do PDF que sobraram (chuveiros, cuba, linha do banco) por objetos vistos de cima e pagina as pedras. |
| 4. Retoques | `retoque_chuveiros_1pav.py`, `retoque_base_1pav.py`, `retoque_bege_bahia_terreo.py`, `retoque_subsolo.py` | Retoques pontuais da Casa A, feitos sem IA. |
| 4. Retoques | `piscinas_barlavento.py` | Barlavento nas piscinas de um render já retocado (Casas A a D), no mesmo tratamento da Casa E. |
| 5. Entrega | `rodape_entrega.py` | Monta o rodapé no padrão do carimbo e as pranchas, com o render alinhado ao quadro comum. Lê os dados da casa na chave `entrega` da config (`--config`). |
| 5. Entrega | `pdf_entrega.py` | Junta as pranchas num PDF para o cliente (mesma chave `entrega`). |

**O que o `gerar_bases.py` faz:**
- **Preparo:** tira o texto, esconde as layers (`layers_ocultas`), pinta as paredes de preto e deixa os vidros neutros.
- **Legenda de cores:** `poligonos`, `trocas_cor`, `hachuras`, `retangulos` (com os modos `so_branco` e `so_cores`) e `setores`.
- **Entorno:** esmaece o que fica fora da cor cheia (`esmaecer`).
- **Saída:** gera a versão 16:9.

**Comandos da Casa B · Subsolo, como referência:**
```bash
cd projetos/POE642_CasaA/scripts
# 1. base (cores da legenda)
python gerar_bases.py Subsolo "../../_pdfs_cliente/642 - SUBSOLO - CASA B.pdf" --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/bases
#    (renomeie a saída ..._v3_vidros_neutros(.png|_16x9.png) para ..._v2(.png|_16x9.png))
# 1b. prévia de texturas
python texturizar_base.py Subsolo ../../POE642_CasaB/bases/POE642_CasaB_BASE_Subsolo_v2.png --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/bases --nome POE642_CasaB_BASE_Subsolo_v3_texturas
# 4. imagem em alta (base + objetos do render)
python elementos_do_render.py Subsolo ../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_v2_render.webp ../../POE642_CasaB/bases/POE642_CasaB_BASE_Subsolo_v3_texturas_16x9.png --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/renders --nome POE642_CasaB_PH_Subsolo_elementos
# 4b. acabamentos finais (chuveiros, cuba, aresta do banco, armário, piso da academia)
python acabamentos_finais.py Subsolo ../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_elementos.png --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/renders --nome POE642_CasaB_PH_Subsolo_final
# 5. rodapés e prancha
python rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --render Subsolo=../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final.png

# Térreo da Casa B: base (renomeie a saída para ..._Terreo_v2) e prévia de texturas
python gerar_bases.py Terreo "../../_pdfs_cliente/642 - TÉRREO - CASA B.pdf" --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/bases
python texturizar_base.py Terreo ../../POE642_CasaB/bases/POE642_CasaB_BASE_Terreo_v2.png --config ../../POE642_CasaB/config_bases.json --saida ../../POE642_CasaB/bases --nome POE642_CasaB_BASE_Terreo_v3_texturas
```

**Coordenadas:** todos os retângulos das configs (`*_vis`) estão na prévia de 1800 px da base sem margem. A conversão é `vis = (pdf − recorte) × 1800 / (0,94 × largura da folha)`. Na base 16:9 de 6905 px, isso dá `px = vis × 6001/1800 + 452`.

---

## 5. Casa A — concluída e entregue

**Dados do carimbo:**
- **Cliente:** Paulo Octávio.
- **Endereço:** ML 10 – Conjunto 02, Lotes 17, Unidade A.
- **Projeto:** Casa A · Unidade Autônoma "A".
- **Data inicial:** 14/10/26.
- **Áreas:**

  | Pavimento | Área |
  |---|---|
  | Subsolo | 160,40 m² |
  | Térreo | 427,40 m² |
  | 1º Pavimento | 263,25 m² |
  | Total | 851,05 m² |

- **Assinatura do render:** New Air, com Render 3D, Projetos com IA e Conrado Cortez.
- **Marca do cliente:** Paulo Octávio.

**Imagens finais:**

| Pavimento | Imagem final | Como foi feita |
|---|---|---|
| Térreo | `renders/POE642_CasaA_PH_Terreo_final_bege.png` | Render da v33 com o Bege Bahia igualado ao do 1º Pavimento |
| 1º Pavimento | `renders/POE642_CasaA_PH_1Pavimento_v7_final2.png` | Render da v7 com o ajuste, mais retoques sem IA: chuveiros, escada em U, saleta da caracol, vãos em branco, cuba da entrada da suíte master e entorno igual à base |
| Subsolo | `renders/POE642_CasaA_PH_Subsolo_final.png` | Render da v6 com o banco da sauna virando piso, tom mais claro e fundo branco |

**Entregue em `entrega/`:**
- as três pranchas em PNG, todas com 2000 × 1354 px, no mesmo quadro;
- o PDF `POE642_CasaA_Plantas_Humanizadas.pdf`, em A3 de largura;
- os rodapés e o GIF das pranchas alternando.

**Pendência opcional:** as pranchas estão em 2000 px porque os renders chegaram comprimidos pelo chat. Com os PNGs originais do motor, rode de novo os retoques e o `rodape_entrega.py` em resolução cheia.

---

## 6. Casa B — em andamento

**Subsolo (pisos definidos pelo cliente):**
- **Mármore Bege Bahia:** todo o malva #BFA79F do PDF.
  - garagem;
  - circulação até a sauna;
  - circulação de cima;
  - BH de serviço e o chuveiro dele.
- **Vinílico:** academia, com o mesmo piso da área íntima do 1º Pavimento da Casa A (Durafloor City Petra).
- **Deck de madeira:** ducha.
- **Mármore travertino:** todo o resto.
  - depósito;
  - sauna e banco em dois níveis;
  - BH sauna e o chuveiro dele;
  - pedra grande de acesso;
  - escada que desce até a ducha.

**Entorno:**
- **Com a cor cheia:** o subsolo, a ducha, a escada que desce até ela e a pedra grande.
- **Esmaecido:** o resto do Térreo.

**Escada:** desce da pedra grande para a ducha, da esquerda para a direita, e a seta aponta só nesse sentido.

**Estado:**
- **Bases:** v1 (cores do PDF), v2 (legenda) e v3_texturas (prévia dos materiais), em `POE642_CasaB/bases/`.
- **Prompt:** a v2 é a atual e já tem o item de escala.
- **Render do motor:** `renders/POE642_CasaB_PH_Subsolo_v2_render.webp`. O motor mudou o layout da academia, fez um banco em L na sauna, mexeu nas paredes da circulação e do chuveiro, pintou o entorno e apagou os arcos das portas.
- **Imagem final:** `renders/POE642_CasaB_PH_Subsolo_final.png`, com 6905 × 3884 px.
  - É a base com os objetos do render: esteiras, bicicletas, supino, bacias, bancada do BH sauna e cabine do elevador (etapa intermediária: `_elementos.png`).
  - Depois vêm os acabamentos:
    - chuveiros e registros cromados de parede no BH de serviço e no BH sauna;
    - cuba branca com torneira no BH de serviço;
    - aresta fina no degrau do banco da sauna;
    - armário ao lado do elevador, no tom da marcenaria dos closets da Casa A;
    - soleira do elevador no mesmo tom neutro da soleira da porta da sauna (copiada dela, girada);
    - a peça branca comprida da academia, que era erro do PDF, virou piso vinílico.
    - no BH sauna: soleira da porta no travertino do piso, rebaixo da bancada com a mesma textura do tampo (copiada dele) e sem os traços pretos, sem a linha preta que passava na frente da pia e piso uniforme em volta da bacia.
  - **Decisões do usuário:** a pedra grande fica lisa, sem paginação; a garagem fica sem carros.
  - `_camada.png` tem só as alterações dos acabamentos, para o Photoshop.
- **Prancha:** `entrega/POE642_CasaB_PH_Subsolo_entrega.png`, em 3840 px (`entrega.largura_prancha` na config; a imagem final da Casa B tem 6905 px), com os rodapés da Casa B (Térreo e Subsolo) em `entrega/`.
- **PDF para o cliente:** `entrega/POE642_CasaB_Plantas_Humanizadas.pdf`, com as duas pranchas (Subsolo e Térreo), em A3 de largura.
- **Pranchas:** `entrega/POE642_CasaB_PH_Subsolo_entrega.png` e `..._Terreo_entrega.png`, em 3840 × 2600 px, no mesmo quadro da folha do cliente (o elevador do Subsolo cai sobre o do Térreo). O Térreo vem do render 2K ampliado com Lanczos.
  - Áreas, do quadro do cliente: Térreo 638,70 m², Subsolo 79,05 m², total 717,75 m². A Casa B tem só esses dois pavimentos.
  - **Confirmados pelo usuário:** endereço e unidade (ML 10 – Conjunto 02, Lotes 17, Unidade B) e o norte, o mesmo da Casa A (a folha da Casa B não tem norte).
  - O quadro é a folha inteira do cliente, então a casa fica pequena no canto. Quando chegar o Térreo, definir um recorte comum aos dois pavimentos.

**Térreo (materiais definidos pelo usuário em 14/10/26):**
- **Vinílico da Casa A:** o laranja #CC9966 (suítes, sala íntima, closet master e circulação íntima).
- **Pedra portuguesa caramelo, igual à da Casa A:** garagem e acesso de carros (no PDF, cinza com hexágonos; os hexágonos saem).
- **Garagem:** com os 3 carros do PDF.
- **Entorno:** grama e paisagismo dentro do lote, entre os dois muros (o `gramados` do `gerar_bases.py` pinta o branco que chega à borda do lote).
- **Granito Marrom Tabaco, como na Casa A:** todas as áreas delimitadas em malva #BFA79F (cozinha, faixa da bancada gourmet, louceiro, despensa, serviço, área descoberta e bloco do motorista). No Térreo, o malva **não** é Bege Bahia (isso vale só para o Subsolo).
- **Pelas regras do Subsolo:** oliva = travertino; decks listrados = madeira; borda das piscinas e pedras cinza = travertino.

**Estado do Térreo:**
- **Bases:** v1 (cores do PDF), v2 (legenda) e v3_texturas (prévia), em `POE642_CasaB/bases/`.
- **Prompt:** `POE642_CasaB_PH_Terreo_v5.md` (PT + EN, com escala) é o atual. A v3 trocou o Bege Bahia pelo granito marrom nas áreas em malva; a v4 pôs a borda infinita; a v5 tirou a calha e o transbordo.
- **Borda infinita:** o lado esquerdo do braço de cima da piscina, junto ao deck em L (a faixa branca de 30 cm sem borda cinza no PDF). A água vai até a linha do deck, na mesma cor da piscina; **não há calha nem transbordo** (decisão do usuário).
- **Imagem final do Térreo = o render, retocado** (o usuário quer a humanização na imagem final, não na base):
  - render do motor (prompt v4): `renders/POE642_CasaB_PH_Terreo_v4_render.webp`;
  - final: `renders/POE642_CasaB_PH_Terreo_v4_retocado.png`, pelo `retoque_terreo_casab.py`, que tira o transbordo inventado pelo motor, põe gramado no vão abaixo da escada de cima ("área verde"), troca o símbolo de planta do hall por uma touceira do próprio render pinta a bancada do lavatório gourmet no quartzo das bancadas da cozinha e humaniza as duas cubas;
  - em aberto: a peça branca comprida abaixo do lavatório gourmet, do lado de fora (na layer de parede, 50 cm de fundo).
- **Respostas do usuário (v2):** a peça em L do deck grande é um banco em tom bronze (#7A5A3C na base); o jardim de inverno é jardim com floreira (#4F7A3A na base, textura das touceiras tropicais do Térreo da Casa A), com o X tracejado da abertura por cima.
- **Depois do render:** `elementos_do_render.py` (móveis, carros, louças e as touceiras de plantas) e `acabamentos_finais.py`, como no Subsolo.

**Próximos passos:**
1. **Casa B entregue** (Subsolo e Térreo, pranchas e PDF). Falta só a resposta do usuário sobre a peça branca comprida abaixo do lavatório gourmet, do lado de fora; com ela, retocar a imagem final do Térreo e refazer a prancha e o PDF:
   `python rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --render Subsolo=../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final.png --render Terreo=../../POE642_CasaB/renders/POE642_CasaB_PH_Terreo_v4_retocado.png && python pdf_entrega.py --config ../../POE642_CasaB/config_bases.json`
2. **Opcional, mais nitidez nos objetos:** passar o render num upscaler de IA (Higgsfield `upscale_image`) antes do `elementos_do_render.py`. Isso gasta créditos, então só com autorização.

---

## 6b. Casa C — em andamento

**Subsolo (definido pelo usuário em 14/10/26):**
- **Vinílico da Casa A:** academia (laranja #CC9966).
- **Travertino:** varanda do subsolo, sauna, ducha e BH da academia (oliva #BAB596); banco da sauna em dois tons mais escuros, como na Casa B.
- **Bege Bahia:** depósito (#E0E0E0) e toda a área externa cinza (#E4E4E4): pátio, faixa de degraus largos e caminho.
- **Floreira:** a faixa do lado de fora da parede esquerda da sauna.
- **BH da academia:** bancada com cuba na parede da direita; os dois quadradinhos (ducha e box) são chuveiros de teto.
- **Esmaecida:** só a escada numerada (degraus 11 a 21), abaixo da sauna.

**Estado:**
- **Config:** `POE642_CasaC/config_bases.json` (prefixo `POE642_CasaC`).
- **Bases:** v1 (cores do PDF), v2 (legenda) e v3_texturas, em `POE642_CasaC/bases/`.
- **Prompt:** `POE642_CasaC/POE642_CasaC_PH_Subsolo_v3.md` é o atual; a v2 diz que os degraus largos descem para o pátio e a v3 põe a escala logo na abertura, com a posição da planta medida na base (x ~9,5%–49%, y ~11%–77%).
- **Base corrigida:** a legenda tem `setas` (recurso novo do `gerar_bases.py`), que desenha a linha de caminhamento dos degraus largos com a seta para cima, rumo ao pátio.
- **Render (prompt v1):** `renders/POE642_CasaC_PH_Subsolo_v1_render_marcado.webp` (com a seta vermelha do usuário; o render limpo não chegou como arquivo).
- **Primeiro retoque (render do prompt v1):** `renders/POE642_CasaC_PH_Subsolo_v1_retocado.png`, pelo `retoque_subsolo_casac.py`: tira a marca vermelha e inverte o sentido de descida dos **degraus largos da esquerda** (descem para cima, rumo ao pátio; a sombra de cada aresta passa para o lado de cima). A escada curta numerada não muda (pedido do usuário).
- **Render (prompt v3):** `renders/POE642_CasaC_PH_Subsolo_v3_render.webp`. Planta em L, mesma escala da base (afim 1,0008 x 1,0095).
- **Imagem final = o render v3, retocado:** `renders/POE642_CasaC_PH_Subsolo_v3_retocado.png` (+ `_camada.png`), pelo `retoque_subsolo_casac_v3.py`.
  - **Bege Bahia:** o motor clareou o mármore (cerca de 235/224/212 contra 226/211/200). Pátio, degraus largos, caminho e depósito recebem o Bege Bahia aprovado (varandas do 1º Pavimento da Casa A, tecido por quilting na escala do render). Contornos, a porta do depósito e as plantas ficam como estão.
  - **Degraus largos:** as arestas do render são redesenhadas com o perfil espelhado; a sombra fica do lado do pátio.
    - **Degraus em L (pedido do usuário):** como no PDF, são 9 arestas. A de cima, que o motor não fez, entra com o perfil médio das outras. As 2 de baixo viram em L e descem até o fim do pátio: uma na coluna 231, a outra na 246, emendando no contorno do caminho.
  - **Banco da sauna (pedido do usuário):** o motor fez um banco em U de madeira; fica o da base, em travertino em L e em dois níveis, nos tons do banco aprovado da Casa B.
    - Degrau da frente em L: 0,91 do piso. Assento junto à parede de baixo: 0,867 do piso.
    - O travertino é o do próprio piso da sauna, com os veios verticais continuados; onde era o braço esquerdo do U, volta a ser piso.
    - Arestas de 0,5 px em #7B796C.
  - **Porta do elevador (pedido do usuário):** a porta de abrir (arco e folha) que o motor pôs no acesso ao elevador sai; vira o vinílico da academia ao lado. O vão, o batente e a soleira ficam.
  - **Chuveiros de teto (pedido do usuário):** na ducha e no box do BH, cada um no centro do quadradinho da base, com a placa quadrada aprovada na Casa A (banho 3 do 1º Pavimento).
    - Na ducha, sai a placa grande fora do centro, com haste até a parede.
    - No box, sai o metal na parede da esquerda.
- **Diferenças do render v3 para a base, não pedidas (ficam como estão até o usuário pedir):**
  - a linha de caminhamento com a seta não aparece.
- **Entrega do Subsolo (14/10/26):** prancha `entrega/POE642_CasaC_PH_Subsolo_entrega.png` (3840 x 2600) e PDF para o cliente `entrega/POE642_CasaC_Plantas_Humanizadas.pdf` (A3, só o Subsolo, a pedido do usuário; o Térreo entra quando for feito).
  - **Rodapé (chave `entrega` da config):** áreas do quadro do usuário: Térreo 798,89 m², Subsolo 113,81 m², total 912,70 m².
  - **Confirmados pelo usuário:** endereço "ML 10 – Conjunto 02, Lotes 17, Unidade C", unidade C e o norte da Casa A.

**Térreo (PDF `642 - TÉRREO - CASA C.pdf`, recebido em 14/10/26; materiais definidos pelo usuário no mesmo dia):**
- **Travertino:** todo o oliva (áreas sociais, circulações, halls, varandas, BH master 1, lavabos e borda das piscinas).
- **Vinílico da Casa A:** o laranja (suíte master, quartos, closets e escritório).
- **Granito Marrom Tabaco:** todo o malva (cozinha, louceiro, serviço, área de serviço descoberta, quarto e BH externos, a faixa da bancada gourmet e a garagem, com os 3 carros). A garagem começou em pedra portuguesa e passou para o granito a pedido do usuário.
- **Pedra portuguesa caramelo, sem os hexágonos:** só o acesso de carros.
- **Bege Bahia:** o cinza dos banhos (BH 1, 2, 3 e BH master 2) e da área externa (pátio, degraus largos, caminho, pisantes) e a escada estreita ao lado do deck.
- **Deck de madeira:** a faixa listrada entre a escada e a piscina.
- **Grama:** o entorno. **Floreiras:** jardim 1 e os dois jardins de inverno. **Banco em L junto ao deck:** bronze, como na Casa B (por analogia; confirmar com o usuário).
- **Degraus largos:** numerados no PDF de 1 (junto ao pátio) a 10 (junto ao caminho), seguindo na escada estreita de 11 a 21 até o deck; descem para cima, rumo ao pátio. A base traz a linha de caminhamento com a seta para cima (`setas`, como no Subsolo).
- **Bases:** v1 (cores do PDF), v2 (legenda) e v3_texturas, em `POE642_CasaC/bases/`.
  - Nas texturas, a amostra da pedra portuguesa e a da floreira foram estreitadas: a da Casa B pegava gramado (manchas verdes no acesso) e fundo branco (faixas brancas no jardim de inverno).
- **Piscina sem bordas a mais (pedido do usuário):** as paredes estruturais da piscina, da prainha, do spa, dos degraus e do deck estão na layer ARQ_PAREDE com preenchimento branco e viravam faixas de vidro em volta de tudo. Elas saíram da detecção de vidro (`zonas_excluidas`). Ficam só a borda de travertino, os dois degraus (linhas finas na prainha) e o vidro da borda infinita (linha dupla no lado esquerdo da piscina comprida).
- **Prompt:** `POE642_CasaC/POE642_CasaC_PH_Terreo_v3.md` é o atual (v2: piscina sem as faixas; v3: garagem em granito). Escala na abertura e posição do lote medida na base (x ~8%–91%, y ~2,5%–85%).
- **Render (prompt v3):** `renders/POE642_CasaC_PH_Terreo_v3_render.webp`. Mesma escala da base (afim 1,0001 x 1,0072).
- **Retoque, erro por erro (pedido do usuário):** `renders/POE642_CasaC_PH_Terreo_v3_retocado.png`, pelo `retoque_terreo_casac.py`.
  1. **Chuveiros de teto:** os boxes do BH master 1, BH 3, BH 2, BH 1 e BH master 2 estavam vazios. Cada um recebeu a placa aprovada da Casa A, no centro do símbolo do PDF. Depois, a pedido do usuário, a ducha entre os lavabos (onde o motor pôs um ralo redondo) recebeu a mesma placa, no centro do símbolo do PDF. Feito.
  2. **Plantas fora do lote:** a faixa de palmeiras passava da linha tracejada em todo o lado esquerdo e dos muros nos cantos. Fora do lote volta a ser a base (fundo branco e linha tracejada) e os trechos de muro cobertos são refeitos com o muro do próprio render. Feito.
  3. **Jardins de inverno:** as plantas passavam dos vidros, sobre o piso, a caixa do elevador e os próprios vidros. Ficam só dentro das floreiras; a parede do elevador é refeita com o perfil de um trecho limpo; o piso em volta é trocado pelo piso limpo ao lado, com emenda suave. As portas de correr de vidro (folhas em dois planos: 2 à esquerda, 2 à direita, 3 embaixo e 2 em cima do jardim 2, com os montantes) vêm da base alinhada, que coincide com o render nos montantes. Na primeira versão o vidro saiu num perfil uniforme e as portas sumiram; o usuário notou e elas voltaram. Feito.
  4. **Cozinha:** bancadas e ilha tinham saído no granito do piso, com uma cuba só. Bancadas e ilha ficam no quartzo claro da bancada gourmet do próprio render (image quilting), com o cooktop (contorno escuro, como o traço grosso do PDF) e as 4 banquetas como estavam. Os dois armários altos do PDF (retângulo com diagonal: o de baixo na bancada da esquerda e o junto à geladeira) viram tampo de marcenaria areia, com contorno nas faces livres e sem a diagonal, como nas Casas A e B. Entre a geladeira e esse armário volta o vão de piso do PDF. As duas cubas do PDF são desenhadas como as do lavatório gourmet da Casa B, com a torneira do lado da parede. A geladeira de inox fica. Feito.
  5. **Quarto externo:** a cama de solteiro do PDF tinha virado dois eletrodomésticos e o criado-mudo, uma caixa branca. A cama vem de uma das camas de solteiro do quarto 2 do próprio render, virada para a cabeceira ficar na parede da direita (como no PDF), encurtada no cobertor e na largura do PDF; o criado-mudo vem do da suíte. Feito.
  6. **Tanques da área de serviço (pedido do usuário, fora da lista):** a bancada tinha saído no granito do piso, com os tanques escuros. A bancada fica no quartzo da cozinha e os dois tanques são os aprovados da Casa B (louça branca, torneira do lado da parede), na mesma escala, nas posições da base. Feito.
  7. **Estar:** as duas poltronas a mais acima do tapete saem, com a sombra. O piso volta continuando os veios verticais de cima, em espelho; a borda de cima do tapete vem do trecho limpo da mesma borda; o tapete logo abaixo vem das linhas limpas de baixo. Feito.
  8. **Estar conforme o PDF (pedido do usuário):** o aparador comprido que o motor inventou abaixo do sofá saiu (vira travertino); a mesa de centro, feita numa peça só, virou as duas do PDF (contornos nas linhas 726–744 e 747–766 do render); as mesas laterais quadradas viraram as orgânicas do PDF (par de seixos, o menor atrás), com a forma tirada do PDF levado ao render pela mesma cadeia da base (`pdf_no_render`), no tampo de madeira da mesa de centro. O piso que volta é tecido do travertino limpo do estar. Na primeira versão, o piso do aparador cobriu um trecho da cortina sobre a janela; o usuário notou e o trecho voltou como no render. Feito.
  9. **Gourmet:** as cinco banquetas embaixo da bancada do cooktop saem (no PDF não há nenhuma). O piso volta continuando os veios de baixo, em espelho, e a sombra da bancada é refeita com o perfil dos trechos limpos da mesma borda. Feito.
  10. **Cooktops (pedido do usuário):** o motor fez os dois com 6 bocas; no PDF os dois têm 5. Na gourmet saiu a boca do meio de cima (2 em cima e 3 embaixo). O da ilha da cozinha é o mesmo desenho girado (3 bocas na coluna da esquerda e 2 na da direita) e virou o cooktop da gourmet corrigido, girado 90° e levado à caixa do da ilha. Feito.
  11. **Box do BH master 2:** a porta de giro voltou como no PDF (layer ARQ_BANCADAS): folha de vidro aberta junto à parede de cima e o arco do giro até o batente de baixo, no traço das portas do render; o chuveiro de teto fica por cima do arco. O vão ao lado do chuveiro (retângulo de ~32 x 98 cm com dois X tracejados, layer DOC_LINHAS E PROJEÇÕES) ficou tracejado sobre o piso, como no PDF, por escolha do usuário (os X vêm do PDF levado ao render; o lado livre ganhou contorno tracejado). Feito.
  12. **Escada estreita abaixo do box (pedido do usuário):** no PDF são 10 degraus (11 a 20, subindo para a direita); o motor fez 6. As arestas internas do motor saíram e entraram 9, repartidas por igual entre a primeira e a última aresta do render, com o perfil de sombra das arestas do próprio render. Feito.
  13. **Elevador:** a caixa tinha saído no travertino do hall. A caixa fica branca e a cabine, no tom da cabine do Subsolo da Casa B (pedido do usuário): é a própria cabine de lá, sem a soleira, girada para a porta ficar à esquerda e levada à cabine do PDF (quase a mesma escala). Feito.
  14. **Chuveiro externo (pedido do usuário):** no pisante junto ao muro de baixo, o motor fez uma cruz escura que ainda atravessava o muro. A cruz saiu e entrou o chuveiro do PDF: ducha quadrada de ~19 cm (a placa aprovada da Casa A, reduzida), braço cromado até o muro e canopla. Feito.
  15. **Degraus largos (pedido do usuário):** a seta da base saiu e a sombra de cada aresta, que o motor pôs do lado de baixo (lia como subida), passou para o lado de cima, com o perfil da mesma escada no Subsolo aprovado; as duas arestas em L ficam com a sombra à esquerda (o nível mais baixo). Feito.
  16. **Aparador do hall de entrada (pedido do usuário):** o motor o fez comprido até a ponta da parede; no PDF ele termina antes e ao lado fica uma mesa redonda. O aparador foi encurtado (a ponta, com borda e sombra, foi para o fim do PDF), o resto voltou a ser travertino e entrou a mesa redonda, no tampo de madeira do aparador. Feito.
  17. **Lavabo ao lado da adega e adega (pedido do usuário):** o motor fez duas cubas; no PDF a de cima é só bancada e virou a bancada lisa do trecho de baixo (a cuba de baixo fica). Na adega, o móvel comprido de madeira junto à parede da direita, que não existe no PDF, virou o piso da adega. O móvel do topo do lavabo (malva no PDF, que o motor pintou no granito do piso e se confundia com piso) virou marcenaria areia, como os armários da cozinha, com contorno embaixo. Feito.
  18. **Escritório (pedido do usuário):** no vão da parede de cima é uma janela, não a porta de correr que o motor fez. A folha de correr saiu e o vão recebeu a janela das próprias janelas da parede esquerda do escritório, girada, com dois panos e montante. Feito.
  19. **Cadeiras das escrivaninhas (pedido do usuário):** o PDF tem cadeira na escrivaninha do Quarto 1, do quarto das duas camas e da suíte do canto; o motor fez as escrivaninhas sem elas. Entrou a cadeira de visitante do escritório (por máscara; a sombra só escurece), um pouco maior como no PDF, girada e centrada no símbolo do PDF, com a frente por baixo da escrivaninha (o tampo por cima e a sombra da mesa sobre a cadeira). Feito.
  20. **Área molhada da bancada das cubas da cozinha (pedido do usuário):** o retângulo da layer ARQ_BANCADAS foi demarcado com traço cinza fino nos lados livres. Feito.
  21. **Torneiras dos banheiros (pedido do usuário):** no BH master 1 o motor fez duas cubas soltas com a torneira na lateral; no PDF é uma cuba esculpida longa, com duas bacias e as torneiras nas pontas (em cima e embaixo). As cubas saíram e entraram as duas bacias do PDF, em louça branca, com a pedra da bancada entre elas (na primeira versão o meio saiu em louça branca; o usuário pediu a textura da bancada). No BH master 2 a torneira também estava na lateral; a cuba foi redesenhada com a torneira no meio da borda de cima, como no PDF. Nos outros banheiros as torneiras já estavam no lado certo. Feito.
  22. **Porta pivotante principal (pedido do usuário):** o motor cortou a folha na soleira; no PDF ela vai de ponta a ponta, passando para fora até o arco. A folha foi estendida com o próprio trecho dela, e a ponta recebeu o arremate da ponta de dentro. Feito.
  23. **Arcos das portas sobre o granito (pedido do usuário):** no granito marrom o arco escuro não aparecia. Os 8 arcos de porta que caem no granito (serviço descoberto, cozinha/serviço, quarto e BH externos, acesso pela garagem) foram redesenhados em cinza claro e traço fino (o usuário pediu cinza no lugar do branco, e linha fina, para ficar discreto) com a geometria do PDF, só onde o piso é granito (máscara pela cor exata da base chapada). Feito.
  24. **Bancos ao pé das camas (pedido do usuário):** o PDF tem banco ao pé da cama da suíte master, do Quarto 1, do Quarto 3 e das duas camas de solteiro do Quarto 2; o motor não fez os bancos e esticou as camas dos Quartos 1, 2 e 3 por cima deles. Essas camas voltaram ao comprimento do PDF e entraram os bancos do Térreo da Casa B (o de duas almofadas nas camas de casal, girado na suíte master; o liso nas de solteiro), levados ao retângulo do PDF, com a sombra. Feito.
  25. **Vaso do lavabo masculino (pedido do usuário):** o motor fez um vaso cinza, fora do padrão. Saiu, e entrou o vaso suspenso branco do lavabo ao lado da adega, espelhado e levado ao retângulo do PDF. Feito.
  - Todos os erros da lista estão feitos. Observação ainda não pedida: dentro do box do BH master 2 o piso saiu em dois tons (metade lisa, metade pontilhada).
- **Entrega (feita após a aprovação da prévia final pelo usuário):** o Térreo entrou em `entrega.pavimentos` (TÉRREO, linha 0 do quadro de áreas, base `v3_texturas_16x9`) e em `pdf.ordem` (Subsolo, Térreo); título do PDF "Casa C – Plantas Humanizadas (Subsolo e Térreo)". Pranchas `entrega/POE642_CasaC_PH_Terreo_entrega.png` e `..._Subsolo_entrega.png` (3840 × 2600 px, mesmo quadro; Térreo alinhado com 179 pontos, erro mediano 0,92 px) e `entrega/POE642_CasaC_Plantas_Humanizadas.pdf` (2 páginas A3, 12,9 MB).

```bash
cd projetos/POE642_CasaA/scripts
python gerar_bases.py Subsolo "../../_pdfs_cliente/642 - SUBSOLO - CASA C.pdf" --config ../../POE642_CasaC/config_bases.json --saida ../../POE642_CasaC/bases
python texturizar_base.py Subsolo ../../POE642_CasaC/bases/POE642_CasaC_BASE_Subsolo_v2.png --config ../../POE642_CasaC/config_bases.json --saida ../../POE642_CasaC/bases --nome POE642_CasaC_BASE_Subsolo_v3_texturas
```

## 7. Avisos

- **Check-in agendado:** havia um check-in agendado do PR na sessão da nuvem. Ele só verifica o PR e não mexe em nada.
- **Commits:** sempre no branch `claude/poe642-casa-a-handoff-jmchm3`.
- **Teste de regressão do `gerar_bases.py`:** num PDF sintético com `ARQ_PAREDE`, o resultado esperado é 1 vidro-forma, 1 vidro-traço e 1 descarte de cada tipo (parede, porta, muros), com `pyflakes` sem avisos. O PDF sintético ficou na nuvem. Se precisar, ele é fácil de refazer: duas paredes cinza 0,357, um vidro fino branco, um traço de vidro, uma porta com arco e um texto.

## Casa D · Térreo

- **PDF:** `_pdfs_cliente/642 - TÉRREO - CASA D.pdf` (mesma folha, recorte e enquadramento das Casas A, B e C). Config em `POE642_CasaD/config_bases.json`.
- **Cores do PDF:** oliva #BAB596 (living, jantar, hall, adega, lavabo), laranja #CC9966 (suítes, sala íntima, circulações, quarto de serviço), terracota #995F4C (cozinha, gourmet, banho gourmet, despensa, louceiro, serviço, área descoberta, garagem e acesso de veículos), cinza #E4E4E4 (varanda gourmet, piscina, escadas, deck lateral), piscina azul. Os banhos são brancos com hachura (sem polígono de piso).
- **Materiais (definidos pelo usuário em 15/10/26, como na Casa C):** travertino no oliva; vinílico no laranja; Granito Marrom Tabaco em todo o terracota, inclusive a garagem e o acesso de veículos (o usuário pediu o acesso igual à garagem, sem pedra portuguesa); Bege Bahia no cinza, nos banhos, na escada branca junto às suítes e nos pisantes; grama no entorno; floreira nos dois jardins.
- **Bases:** `bases/POE642_CasaD_BASE_Terreo_v1` (cores do PDF) e `_v2` (legenda). Para os banhos, o `gerar_bases.py` ganhou `proteger_layers` e `apagar_linhas_layer` nos retângulos; para os pisantes e a faixa com X, `fechados_apos_gramado`. A piscina entrou em `zonas_excluidas` (sem faixas de vidro em volta da água).
- **Prévia de texturas:** `bases/POE642_CasaD_BASE_Terreo_v3_texturas(_16x9)`, com os materiais aprovados das Casas A, B e C (sem deck e sem pedra portuguesa, que a Casa D não tem).
- **Prompt:** `POE642_CasaD/POE642_CasaD_PH_Terreo_v1.md` (PT de validação + EN para o motor), com a base `v3_texturas_16x9` como única entrada. Escala: lote em x ~9,5%–88% e muros em ~6,5% e ~89,5% da altura (medidos na base).
- **Próximo passo:** o usuário roda o prompt v1 no Nano Banana Pro e traz o render; o retoque segue erro por erro, como na Casa C.
- **Render (prompt v1):** `renders/POE642_CasaD_PH_Terreo_v1_render.webp` (afim 1,0001 x 1,0076, como na Casa C). Erros levantados, numerados em `renders/POE642_CasaD_PH_Terreo_v1_render_marcado.jpg` (a corrigir erro por erro, na ordem que o usuário escolher):
  1. muro preto inventado na borda esquerda do lote (no PDF é a linha tracejada);
  2. plantas passando do lote e dos muros nos cantos de cima e de baixo à esquerda;
  3. faixa com X à direita do hall virou canteiro (base: grama com a projeção tracejada);
  4. ponta direita do acesso de veículos em piso cinza (resto em granito);
  5. projeção tracejada em X sobre a entrada da garagem sumiu;
  6. portas sobre o granito sem arco (banho gourmet, louceiro, despensa, serviço → garagem, porta dupla da área descoberta);
  7. vaso sanitário inventado na área descoberta e X tracejado apagado;
  8. tanques com uma cuba (PDF: duas);
  9. DCE sem a cama de solteiro e o criado-mudo (viraram marcenaria em L);
  10. ilha da cozinha sem o cooktop de 5 bocas;
  11. cooktop da gourmet com 4 bocas nos cantos e uma no meio (PDF: 2 em cima e 3 embaixo);
  12. bancada da pia da gourmet em madeira (deve ser quartzo);
  13. adega virou lavabo (cuba e vaso inventados);
  14. lavabo sem o vaso e sem a bancada com cuba;
  15. banco capitonê à direita do estar virou duas poltronas;
  16. mesa redonda maior, tapete orgânico redondo e as duas mesinhas laterais sumiram;
  17. plantas inventadas sobre as mesas (jantar, mesa redonda, varanda gourmet, escritório);
  18. degrau interno do spa só em dois lados (PDF: quatro);
  19. degrau estreito entre a piscina e a prainha virou faixa de água escura;
  20. escada junto à suíte master com 11 degraus (PDF: 16);
  21. suítes 1 e 2 sem o banco ao pé da cama (camas esticadas);
  22. escrivaninha do escritório com 6 cadeiras (PDF: 2 de visita e 1 de trabalho);
  23. elevador fora do padrão (cabine no tom do Subsolo da Casa B, como na Casa C).
- **Retoque (`POE642_CasaA/scripts/retoque_terreo_casad.py`, sem IA, na ordem pedida pelo usuário):** saída em `renders/POE642_CasaD_PH_Terreo_v1_retocado.png` (e `_camada.png`, só os px alterados).
  1. porta pivotante principal (hall de entrada ↔ estar): a folha, cortada pelo motor no alinhamento da parede, vai até o fim do PDF, do lado do hall (mesmo caso da Casa C);
  2. chuveiros do banho master: a barra de parede a parede do motor sai e entram as duas duchas do PDF, cada uma num braço que sai da parede lateral (placa da Casa A reduzida, braço cromado e canopla).
  3. armários até o teto (retângulos com diagonal no PDF): tom areia da Casa C com o veio do próprio armário do render (pedido do usuário), sem a sombra de móvel baixo no piso; embaixo dos armários junto a bancada (cozinha e vizinho ao gás), piso refeito em granito tecido.
  4. área molhada da bancada da pia da cozinha: traço cinza fino nos lados livres (esquerda e embaixo), como na Casa C.
  5. eletrodomésticos da cozinha (os dois volumes ao lado do armário do canto) em inox, com o sombreado do render.
  6. porta de correr do abrigo de gás: a soleira larga do motor sai e entram as duas folhas do PDF, em dois planos.
  7. carros em tons diferentes: grafite (esquerda), branco perolado (meio) e azul-marinho (direita), por curva de tom na silhueta, com vidros, reflexos e lanternas do render.
  8. erros 1 e 2 da lista: o muro preto da esquerda vira grama até a linha tracejada; fora do lote volta a base; os muros de cima e de baixo, cobertos pelas plantas dos cantos, são refeitos com uma coluna limpa.
  9. erro 3 da lista: o canteiro à direita do hall vira grama tecida do gramado do render, com sombra dos muros e as linhas do PDF (retângulos com X e tracejados) em cinza claro.
  10. erro 4 da lista: a ponta direita do acesso de veículos, em cinza, vira o granito da garagem (quilting com o perfil de luz do granito ao lado).
  11. erro 5 da lista: a projeção com X e o contorno tracejado sobre a entrada da garagem, em cinza e traço fino, só sobre o granito.
  12. erro 6 da lista: arcos das portas sobre o granito em cinza e traço fino, como na Casa C (banho gourmet, louceiro, despensa, serviço → garagem e porta dupla da área descoberta).
  13. erro 7 da lista: o vaso inventado na área descoberta sai (granito na luz do entorno) e entra o X tracejado do PDF, em cinza fino.
  14. erro 8 da lista: a cuba única do serviço vira os dois tanques da Casa B, girados (torneira do lado da parede).
  15. erro 9 da lista: no DCE, a marcenaria em L vira piso (sem a sombra alta) e entram a cama de solteiro e o criado-mudo da Casa C, nas caixas do PDF.
  16. erros 10 e 11 da lista: cooktop de 5 bocas (2 em cima, 3 embaixo) na ilha da cozinha e na gourmet, com o cooktop corrigido da Casa C, nas caixas do PDF.
  17. erro 12 da lista: a bancada da pia da gourmet, em madeira, vira quartzo com a luz da própria bancada; a cuba fica.
  18. erro 13 da lista: a adega volta a ser vazia (travertino), sem o lavabo inventado.
  19. erro 14 da lista: lavabo com a bancada de quartzo e cuba junto à parede da direita (onde a base tinha pintado jardim) e o vaso suspenso da Casa C.
  20. erro 15 da lista: as duas poltronas à direita do estar saem e entra o banco capitonê do PDF (tecido do sofá, losangos com botões).
  21. segunda imagem do motor (`renders/POE642_CasaD_PH_Terreo_v1_render_fonte2.webp`, trazida pelo usuário): fonte de elementos prontos. Armários dos quartos: os closets com cabides dela, no tom areia.
  22. erro 16 da lista: mesa redonda, tapete e poltronas da segunda imagem (mesa no diâmetro do PDF), sem a planta, e as duas mesinhas do PDF. O tapete segue redondo (no PDF é orgânico).
  23. erro 17 da lista: plantas fora das mesas (gourmet e escrivaninha com os tampos da segunda imagem; jantar por interpolação vertical no veio).
  24. erros 18 e 19 da lista: a água da piscina, da prainha e do spa vem da segunda imagem (degrau do spa nos quatro lados; o degrau estreito sem a faixa escura).
  25. erro 20 da lista: a escada junto à suíte master com os 16 degraus da segunda imagem.
  26. erro 21 da lista: camas das suítes 1 e 2 no comprimento do PDF e os bancos de duas almofadas da Casa B ao pé delas.
  27. erro 22 da lista: na escrivaninha do escritório ficam as 2 cadeiras de visita e a de trabalho do PDF (saem 3).
  28. erro 23 da lista: elevador com a cabine do Subsolo da Casa B, porta à direita, ocupando a caixa inteira (pedido do usuário: sem o branco largo em volta).
  29. degrau de canto da prainha removido (pedido do usuário): placas da mesma fileira, com a sombra da borda.
  30. louceiro e despensa sem as prateleiras do motor (no PDF o L é só um preenchimento branco na layer de projeções): granito com a sombra das paredes.
  31. banho gourmet: divisória do box em cinza e chuveiro do PDF (ducha, braço e canopla), como no banho master.
  32. bancada da pia da gourmet: área molhada em traço cinza fino e o suporte de utensílios decorativo do PDF (vaso grafite com a folhagem do render).
  33. tapete da mesa redonda no contorno orgânico do PDF (o que sobra vira travertino).
  34. máquinas da área de serviço em inox, como os eletrodomésticos da cozinha.
  35. bancada da sala íntima: quartzo com cuba redonda e torneira na parede, área molhada em traço cinza fino e frigobar em inox (o armário de cima fica em madeira).
  36. chuveiros dos banhos 2 e 3: o texto ilegível do motor sai e entram as duchas do PDF com braço até a parede do meio, como no banho master.
  37. louceiro e despensa: os armários em L do PDF voltam (areia, com veio, sem sombra de móvel baixo).
  38. veios de madeira no armário e no criado-mudo do DCE (veio da escrivaninha da segunda imagem).
  39. pisantes de cima com o Bege Bahia do deck (veios suaves); a fileira junto à garagem já tinha veios.
  40. torneiras do PDF nas duas cubas da cozinha (cromado, no eixo de cada cuba).
  41. spa com o segundo contorno interno (o degrau em volta do fundo), no perfil das arestas do render.
  42. paisagismo: canteiros com as touceiras do render nos dois gramados junto à escada da piscina (acima e abaixo dela).
  43. lavatório junto ao banho gourmet: torneira lateral do PDF, legível sobre a bancada branca, e o contorno da cuba.
  44. WC DCE: o disco branco do motor vira o chuveiro do PDF (ducha, braço e canopla).
- **Entrega (após a aprovação da imagem final pelo usuário, 15/10/26):** chave `entrega` em `POE642_CasaD/config_bases.json` (só o Térreo; endereço ML 10 – Conjunto 02, Lotes 17, Unidade D, confirmado; área do Térreo não informada pelo usuário: o quadro mostra "NÃO INFORMADO"; sem linha de total). Prancha `entrega/POE642_CasaD_PH_Terreo_entrega.png` (3840 × 2600 px, mesmo quadro das outras casas; render alinhado com 70 pontos, erro mediano 0,93 px) e `entrega/POE642_CasaD_Plantas_Humanizadas.pdf` (1 página A3, 10,8 MB). Os objetos pessoais e decorativos (prompt `POE642_CasaD_PH_Terreo_v1_objetos.md`) não entram: o usuário testou no Higgsfield e o resultado não ficou a contento (15/10/26). A entrega fica como está.

## Casa D · Subsolo

- **PDF:** `_pdfs_cliente/642 - SUBSOLO - CASA D.pdf` (recebido em 15/10/26; mesma folha e enquadramento). Pavimento `Subsolo` na `POE642_CasaD/config_bases.json` (curvas de nível ocultas).
- **Ambientes:** DCE 1 (6 m²), WC DCE (2,88 m², com chuveiro), depósito/casa de máquinas (20,02 m²), academia (72,23 m²), vestiário (6,41 m²), sauna (6,55 m²), ducha, elevador, escada (17 degraus, sobe) e a circulação. Cores do PDF: terracota #995F4C (DCE 1, WC DCE e depósito) e laranja #CC9966 (academia); sauna, ducha, vestiário, circulação e escada sem preenchimento (brancos). À esquerda da academia (janelas), uma área externa sem preenchimento.
- **Base v1** (cores do PDF): `bases/POE642_CasaD_BASE_Subsolo_v1(_16x9)` e a prévia `_16x9_preview.jpg`.
- **Materiais (usuário, 15/10/26):** granito Marrom Tabaco #5A4232 no terracota (DCE 1, WC DCE, depósito), como as áreas de serviço do Térreo; vinílico #C8A27C na academia, como na Casa C; Bege Bahia #E8E8E8 na sauna, ducha, vestiário (com WC e chuveiro), circulação, escada e no pátio externo em L à esquerda (contorno ARQ_CONTRAPISO sem preenchimento: faixa ao lado do DCE e da escada + área à esquerda da academia e da sauna). Banco da sauna em dois tons de Bege Bahia mais escuros (#DCDCDC degrau da frente, #D0D0D0 assento), como os bancos aprovados das Casas B e C. Elevador branco. A divisória do box do WC DCE (faixa ARQ_REVESTIMENTOS que saía tracejada e avermelhada) virou cinza cheio #5B5B5B. A parede tracejada de fora do pátio (ARQ_PAREDE) fica como no PDF.
- **Base v2** (legenda): `bases/POE642_CasaD_BASE_Subsolo_v2(_16x9)` e a prévia `_16x9_preview.jpg`.
- **Base v3 (texturas):** `bases/POE642_CasaD_BASE_Subsolo_v3_texturas(_16x9)` e a prévia; as mesmas fontes do Térreo da Casa D, e o banco da sauna com o Bege Bahia escurecido (0,93 e 0,88), preso ao retângulo do banco.
- **Prompt v1:** `POE642_CasaD_PH_Subsolo_v1.md` (entrada: `bases/POE642_CasaD_BASE_Subsolo_v3_texturas_16x9.png`). A planta ocupa de ~12,5% a ~40,5% da largura e de ~46% a ~82% da altura. Pontos do PDF que o prompt descreve:
  - a antessala da sauna é aberta para a academia, sem parede nem porta;
  - a porta da sauna fica no alto da parede da direita;
  - os três chuveiros (WC DCE, ducha da antessala e box do vestiário) são duchas num braço que sai da parede, como no Térreo;
  - o armário do DCE 1 vai até o teto;
  - o elevador ocupa quase toda a caixa.
- **Render v1:** `renders/POE642_CasaD_PH_Subsolo_v1_render.webp` (2000 x 1116). O motor manteve o layout, mas aproximou a planta (~2,73 x a base reduzida a 2000 px); o alinhamento render→base deu 68 pontos e erro mediano de 0,74 px. O elevador do Subsolo cai a 1 px do elevador do Térreo na base de 6000 px: as duas folhas têm o mesmo enquadramento. Mapa dos erros: `renders/POE642_CasaD_PH_Subsolo_v1_erros.jpg`. Decisões do usuário: banco da sauna em Bege Bahia; juntas gigantes do depósito removidas; a imagem final na escala e na posição do Térreo.
- **Retoque** (`POE642_CasaA/scripts/retoque_subsolo_casad.py`, sem IA; saída `renders/POE642_CasaD_PH_Subsolo_v1_retocado.png`, `_camada.png` e `_previa.jpg`):
  1. depósito: a faixa areia do motor junto à parede da esquerda (armário que não existe no PDF) virou granito (textura tecida do próprio piso, luz do entorno em várias escalas).
  2. depósito: as juntas de placas gigantes (~1,9 m; linhas claras de 2 px em x 1182 e 1334, y 228 e 389) e as quatro manchas claras saíram (pedido do usuário); a folha da porta no fim da escada e os arcos ficam, e a luz do entorno não usa as peças claras.
  3. WC DCE: o piso da área do chuveiro (acima da divisória), mais claro e acinzentado, voltou ao tom do granito do resto do banheiro (ganho por canal; a textura do render fica).
  4. WC DCE: o símbolo do CAD virou o chuveiro do Térreo (placa aprovada da Casa A, braço cromado até a parede da esquerda e canopla), na geometria do PDF levada ao render pela cadeia da base (`pdf_cadeia`); sombra e brilho na escala do render (~2,73 x a do Térreo).
  5. DCE 1: o armário até o teto (o da diagonal), quase branco no render, virou a madeira areia dos armários até o teto do Térreo retocado (tecida por quilting, ampliada 2,73 x, o mesmo aspecto que ela tem na prancha), com o veio no comprido, sem a diagonal; os contornos escuros do render ficam. A mancha clara do piso acima do criado-mudo saiu.
  6. sauna: o braço do banco em L que o motor subiu junto ao vidro saiu; ali voltou o piso de Bege Bahia.
  7. sauna: o banco de madeira do motor ficou em Bege Bahia (pedido do usuário), em dois tons como na base (degrau da frente 0,93, assento junto à parede 0,88), com as linhas do PDF (bordas e linha dupla de cada nível, ARQ_ELEMENTOS FIXOS). O miolo da sauna foi refeito em Bege Bahia tecido do pátio, na luz do piso que já era Bege Bahia.
  8. ducha da antessala: o símbolo do CAD (quadrado, braço e a cruz branca pintada sobre a parede de baixo) virou o chuveiro, com o braço vertical saindo da parede de baixo; a parede voltou ao preto do próprio miolo (praticamente 0).
  9. box do vestiário: o mesmo, com o braço saindo da parede da direita; o toco da cruz que passou para o vinílico da academia saiu. Nos pisos de Bege Bahia a luz do apagamento vem só de px acima de 150 (a borda da parede sombreava a emenda) e os traços escuros do símbolo também são trocados.
  10. vestiário: a cuba da bancada, só um contorno cinza no render, virou uma cuba branca (aba, bacia com a borda mais escura indo ao fundo claro, válvula cromada), com a torneira cromada (contorno escuro e sombra curta, como no lavatório do Térreo) saindo da faixa junto à parede, na geometria do PDF.
  11. esteiras: os letreiros que o motor escreveu nas lonas saíram (sem texto na planta); a lona foi tecida da própria lona, na luz dela.
  12. pátio: a parede tracejada dupla de fora (à esquerda, embaixo e no alto), que o motor apagou ou cortou, voltou: os 419 traços do PDF (ARQ_PAREDE, fora da planta) desenhados direto no quadro comum.
- **Escala (pedido do usuário):** a imagem final `renders/POE642_CasaD_PH_Subsolo_v1_final.png` sai no quadro comum das bases (3840 x 2160, a folha 16:9 inteira, o mesmo das pranchas), com fundo branco puro fora da planta. Conferência (`renders/POE642_CasaD_PH_Subsolo_v1_sobreposicao_terreo.jpg`, paredes do Subsolo em vermelho sobre o Térreo): a caixa do elevador cai a -0,3 / +0,5 px da do Térreo na prancha de 3840 px, e a escada fica sob a do Térreo; a rotina das pranchas (`no_quadro_comum`) realinha a final com 158 pontos e erro mediano de 0,44 px (praticamente a identidade).
  - Correção da final (usuário: faltavam cama, criado-mudo, armário e elevador): a mancha da planta tirada da base não tinha os buracos preenchidos, e tudo o que é branco na base (cama, criado-mudo, armário, cabine do elevador, aparelhos da academia, louças) virava fundo branco. Agora `binary_fill_holes` antes da folga: só o fundo de fora da planta fica branco.
  13. arcos das portas sobre o granito (pedido do usuário): os cinco (WC DCE, DCE 1, porta dupla do depósito e porta do depósito no fim da escada) ficaram em cinza (160, 161, 160) e traço fino, como no Térreo; o arco preto do render (~1,5 px) sai antes (granito tecido, só no granito da base chapada) e o cinza vem das curvas do PDF.
  14. escada (pedido do usuário): só sombreamento de descida, sem linhas nem tracejados. O Bege Bahia foi refeito (some a linha de caminhamento, o círculo, a marca de corte, o tracejado e as linhas dos degraus); os 16 pisos do PDF (27,1 px) escurecem até 12% para baixo (a escada sobe do pátio, à esquerda, para a direita) e cada espelho joga uma sombra curta (20%, decaimento de 5 px) no piso de baixo, à esquerda dele, inclusive o 1º no pátio.
  15. bancos da sauna (pedido do usuário: mármore Bege Bahia): os dois tons acinzentados e as linhas escuras saíram; o banco é o mesmo mármore Bege Bahia do piso, com o veio (degrau 0,97, assento 1,0), e os níveis se leem pela sombra curta de cada borda no nível de baixo (18%, 4 px) e por um brilho leve (5%) na quina de cima. A luz do miolo da sauna passou a ser chapada (a mediana do piso limpo): a sombra que o motor pôs junto ao braço em L deixava um fantasma.
  16. sanitários (pedido do usuário: mais bem representados, com o tampo): os vasos do WC DCE e do WC do vestiário, chapados e com o contorno do CAD, foram desenhados em 8 x no polígono exato do PDF: louça com volume (borda 0,88), contorno fino e sombra curta no piso; o tampo fechado cobre a bacia da linha da dobradiça do PDF (5,7 px da parede) à frente, recuado 1,2 px, com volume, contorno e sombra leve sobre a louça. Parafusos e dobradiças ficaram de fora (com 1 a 2 px viravam manchas).
  17. portas de vidro de acesso à academia (pedido do usuário: mais finas): as quatro folhas de correr (dois trilhos), cápsulas cinza de ~10 px no render, foram refeitas em 8 x na espessura do PDF (3,4 px): vidro claro com a linha central fina, montantes de alumínio nas pontas, contorno fino e batentes; o vão (a faixa branca entre as folhas e o vinílico) virou soleira de Bege Bahia, no tom do pátio. A janela alta no canto da academia e o vidro da sauna continuam como o render fez.
  18. vidro da sauna e janela alta da academia (pedido do usuário: finos como as portas): as barras grossas do render saíram; o vidro fixo foi refeito na espessura do PDF (vidro claro, linha central, caixilhos de alumínio e contorno fino), peitoril e soleira em Bege Bahia, retornos da parede em preto e as faces da parede em traço fino e claro (como no PDF); na janela, a faixa de vinílico que a barra cobria voltou.
  19. entrada do elevador (pedido do usuário): as duas folhas da porta recolhidas no poço, cápsulas cinza de ~8 px no render, saíram (cinza do poço) e foram redesenhadas na espessura do PDF (4,2 px), em inox com contorno fino; a soleira branca virou a de entrada de elevador: inox escovado no sentido da porta, com os dois frisos-guia, entre os batentes de alumínio.
  20. área verde (pedido do usuário, com um trecho do Térreo como referência): a faixa entre o pátio e a parede tracejada de fora (à esquerda, e a faixa estreita embaixo, até o tracejado de dentro) virou jardim no quadro comum: a da esquerda recebe o jardim vizinho do Térreo retocado na mesma altura (grama em cima, touceiras de samambaias e palmeiras embaixo; 66 px à esquerda no quadro de 3840) e a de baixo, grama tecida da grama limpa do Térreo. Só o fundo branco fora da planta muda.
  21. janelas do WC DCE e do DCE 1 (pedido do usuário: vidros finos): as cápsulas grossas do render, que passavam 3 px do vão para o cômodo e para a circulação, saíram (granito em cima, Bege Bahia embaixo, luz só do próprio piso) e as janelas entraram no desenho fino dos outros vidros: peitoril em Bege Bahia, vidro na espessura do PDF com linha central, caixilhos de alumínio, retornos da parede em preto e as faces em traço fino.
  22. portas de giro (pedido do usuário: mais finas e elegantes): as 10 folhas (WC DCE, DCE 1, as duas do depósito, a do fim da escada, sauna, ducha, vestiário, WC e box do vestiário), barras de 10 a 12 px com contorno preto no render, e os arcos saíram (piso tecido do próprio cômodo; protegidas só as paredes grossas na base e no render) e entraram do PDF: a folha na espessura do PDF (3,4 px) em branco suave com contorno fino, e o arco em traço fino (cinza claro no granito, cinza médio no Bege Bahia).
  23. mancha escura na frente das janelas do WC DCE e do DCE 1 (pedido do usuário): a borda de baixo da cápsula antiga ia até a linha 263 e a luz do piso refeito puxava esse escuro; o piso foi refeito até a linha 265, com a luz só do Bege Bahia limpo (acima de 200). Fica a linha fina da face da parede, como no PDF.
  - Correção da área verde: o retângulo do jardim pegava também o recorte branco entre o depósito e o elevador (fora da planta) e punha grama ali; agora o jardim fica só na faixa da esquerda (x < 166 vis) e na de baixo (y > 940 vis).
- **Aprovado pelo usuário (15/10/26):** `renders/POE642_CasaD_PH_Subsolo_v1_final.png` (quadro comum 3840 x 2160, na escala e na posição do Térreo). Próximo passo: prancha e PDF de entrega com o Térreo e o Subsolo.
- **Entrega (15/10/26, depois da aprovação):** a chave `entrega` da `POE642_CasaD/config_bases.json` ganhou o Subsolo (base `POE642_CasaD_BASE_Subsolo_v3_texturas_16x9.png`, linha 1 do quadro). Quadro de áreas, por decisão do usuário: Térreo e Subsolo "NÃO INFORMADO", sem linha de total. Pranchas `entrega/POE642_CasaD_PH_Subsolo_entrega.png` e `..._Terreo_entrega.png` (3840 × 2600 px; a final do Subsolo realinhada com 89 pontos, erro mediano 0,44 px, sob o Térreo) e `entrega/POE642_CasaD_Plantas_Humanizadas.pdf` (2 páginas A3, Subsolo e Térreo, 12 MB). No `rodape_entrega.py`, a linha de total agora é a que se chama "TOTAL" (as Casas A, B e C não mudam) e o quadro reduz a fonte só quando um nome e um valor não cabem com 40 px de respiro (na Casa D, "SUBSOLO" e "NÃO INFORMADO"; nas outras casas fica em 31).

## Casa E · Térreo

- **PDF:** `_pdfs_cliente/642 - TÉRREO - CASA E.pdf` (recebido em 15/10/26; mesma folha 3370 × 2384 pt e mesmo enquadramento das outras casas). Config nova `POE642_CasaE/config_bases.json` (as chaves globais da Casa D; pavimento `Terreo` com as curvas de nível ocultas).
- **Ambientes (textos do PDF):** living e sala de jantar (89,87 m²), circulações (21,23 e 7,11 m²), escritório (13,59 m²), lavabo (6,21 m²), hall de entrada (16,63 m², com X tracejado), jardim interno (7,08 m², junto à escada), louceiro, adega, despensa, CPD, elevador; cozinha (31,27 m²), área de serviço (16,34 m²) e área de serviço descoberta (8,17 m², com X), gás, DCE (6,08 m²) e WC DCE 1 (3,04 m²); garagem (64,54 m², 3 carros) e a circulação de cima (67,87 m²); área gourmet (39,78 m²), circulação gourmet (57,04 m²), BH gourmet e lavabo gourmet; varanda (78,14 m²), deck (44,67 m²), piscina, prainha e spa; escada externa de 18 degraus no alto, escada interna de 20 degraus (sobe) e uma escada de 11 degraus à esquerda; acesso de veículos curvo em hexágonos à direita e pisantes embaixo à direita.
- **Cores do PDF:** rosa #BFA79F (cozinha, gourmet, circulações de cima, serviço, DCE, banhos do gourmet, garagem), oliva #BAB596 (living, jantar, circulações internas, escritório, lavabo, hall, louceiro), cinza #E4E4E4 (varanda, deck, piscina em volta), cinza #E0E0E0 (WC DCE 1 e blocos à esquerda), piscina #7FDFFF, escadas #DDDACB e pilares rosa-choque (layer EST - Pilar) na varanda. Layer nova `ARQ_LAYOUT HUMANIZAÇÃO` (móveis e plantas do layout).
- **Base v1** (cores do PDF): `bases/POE642_CasaE_BASE_Terreo_v1(_16x9)` e a prévia `_16x9_preview.jpg`.
- **Materiais (usuário, 15/10/26):** granito Marrom Tabaco #5A4232 em todo o rosa; travertino #DCD9CA em todo o oliva; Bege Bahia #E8E8E8 no cinza (varanda, deck, blocos e degraus à esquerda, pisantes) e no WC DCE 1; pedra portuguesa caramelo #C49A6C no acesso de veículos curvo (sem os hexágonos); pilares pretos, como as paredes; jardim interno (floreira) no retângulo abaixo da escada; louceiro (marcenaria areia #CBB89E) na faixa acima da escada; bancos em bronze fosco #76604A (o L embaixo à esquerda e o retângulo entre a piscina e os degraus); piscina #DFF6FE; grama com paisagismo no entorno. Legenda na `POE642_CasaE/config_bases.json`.
- **Base v2** (legenda): `bases/POE642_CasaE_BASE_Terreo_v2(_16x9)`; a piscina sem faixas de vidro (zona excluída, como nas Casas C e D); os hexágonos do acesso somem na pedra portuguesa.
- **Base v3 (texturas):** `bases/POE642_CasaE_BASE_Terreo_v3_texturas(_16x9)`; as fontes da Casa D Térreo, mais duas geradas por código (`POE642_CasaA/scripts/fontes_procedurais.py`, saída em `bases/fontes/`): pedra portuguesa caramelo (Voronoi de pedrinhas de ~6,5 cm em tons de caramelo, ocre e creme, juntas de areia) e bronze fosco (escovado fino); o louceiro com a madeira areia dos armários até o teto do Térreo retocado da Casa D, girada (veio no comprido). As duas escadas (#DDDACB) entram no travertino.
- **Prompt v1:** `POE642_CasaE_PH_Terreo_v1.md` (entrada: `bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png`). O lote vai de ~7% a ~90% da largura e do topo da imagem (muro de cima) a ~83,5% da altura (muro de baixo).
- **Render v1:** `renders/POE642_CasaE_PH_Terreo_v1_render.webp` (2000 × 1116), na escala da base: SIFT + afim com 182 pontos, escala 0,9998 × 1,0066, deslocamento de 0,3 e -2,8 px. Os 11 itens a retocar estão marcados em `renders/POE642_CasaE_PH_Terreo_v1_erros.jpg`.
- **Retoque** (`POE642_CasaA/scripts/retoque_terreo_casae.py`, sem IA, um item por vez; saída `renders/POE642_CasaE_PH_Terreo_v1_retocado.png`, `_camada.png` e `_previa.jpg`):
  1. lote: a vegetação que o motor passou para fora do lote (à esquerda, embaixo e no alto à direita) saiu, e as linhas tracejadas do lote voltaram: fora do lote ficou a base alinhada (o branco, a linha tracejada da esquerda, a da direita e o retângulo tracejado embaixo). Os muros de cima e de baixo, onde as folhas passavam por cima, voltaram ao preto (cada linha do muro é a mediana dela num trecho limpo).
  2. faixa à direita dos pisantes: o Bege Bahia que o motor inventou entre o gramado e a linha tracejada da direita (branco no PDF) voltou ao branco da base, no mesmo passo do item 1.
  3. jardim interno: as plantas, que o motor espalhou para fora da floreira (por cima da escada e no travertino em volta, com a sombra delas), ficaram só no retângulo da floreira do PDF. Fora dele voltaram a escada (os degraus tracejados copiados da mesma coluna logo acima, sem a diagonal; onde a diagonal ocupa a fonte, dois degraus para o lado) e o travertino (da mesma coluna, mais abaixo, pois os veios correm na vertical); a diagonal da escada segue fina até a floreira, como no PDF, e a borda da floreira entrou em traço fino cinza-escuro.
  4. tapete do estar da varanda: o motor fez um tapete redondo (uma elipse de 60,5 × 65 px); no PDF ele é orgânico (polígono branco da ARQ_MOBILIÁRIO), com o recorte em volta da ponta esquerda do sofá. O tapete tomou a forma do PDF: o que sai virou travertino (as mesmas colunas da faixa limpa acima do tapete, na luz do travertino em volta e com a sombra dos móveis), o que entra virou tapete tecido do próprio tapete, com uma borda fina por fora; sofá, poltronas, mesas, aparador e mesinhas (os polígonos brancos do PDF, com 2 px de folga) ficaram.
  5. varanda: as quatro barras a 45° à esquerda das poltronas (ARQ_ELEMENTOS FIXOS, ~28 × 2,7 px), que o motor apagou, voltaram na geometria do PDF (o retângulo girado de cada mancha, com a largura pela área mais o traço do contorno), no cinza em que aparecem na base (148, 150, 153), com a face de cima um pouco mais clara, contorno fino e sombra curta no piso.
  6. elevador: o motor fez a caixa num piso de pedra clara, com um contorno de cabine solto no meio. Como nas Casas C e D: caixa branca e a cabine do Subsolo da Casa B aprovado (a porta já fica embaixo, como no PDF, sem girar), ocupando a caixa inteira com 1 a 2 px de folga (46 × 42 px); as folhas da porta e a soleira do render ficaram.
  7. CPD: o vaso sanitário que o motor pôs junto à parede da direita (no PDF o CPD não tem louça) saiu, com a sombra; ali voltou o granito tecido do próprio CPD (`apagar_largo`, luz do piso em volta).
  8. área de serviço: as duas máquinas do PDF (os dois quadrados de ~21,7 px da ARQ_LAYOUT HUMANIZAÇÃO ao lado do tanque duplo), que o motor juntou num bloco de madeira, voltaram como as máquinas em inox do Térreo aprovado da Casa D (cada uma, uma metade do par de lá, levada ao quadrado do PDF), com contorno fino e sombra curta; o resto do bloco virou o granito tecido do piso (a parede de cima e a bancada ficaram).
  9. área de serviço descoberta: o X tracejado do PDF (41 traços da DOC_LINHAS E PROJEÇÕES: as duas diagonais e a linha de baixo), que o motor apagou, voltou como a projeção da garagem da Casa D: cinza (160, 161, 160), traço fino (0,45 px), força 0,7, só sobre o granito.
  10. DCE: o motor fez a cama como uma laje de pedra, o criado-mudo como um armário alto e o armário até o teto (o da diagonal) como uma pia. As três peças do render saíram (granito tecido do próprio quarto; paredes, janela e porta ficaram) e entraram as do DCE do Térreo aprovado da Casa D, nos retângulos do PDF (ARQ_LAYOUT HUMANIZAÇÃO): a cama de solteiro (girada, cabeceira na parede da direita, onde o PDF tem o travesseiro) e o criado-mudo, com sombra curta, e o armário até o teto em areia com veio, sem sombra de móvel baixo; contorno fino nas três.
  11. WC DCE 1: o motor pôs um segundo vaso no alto, onde o PDF tem o chuveiro. O vaso saiu (Bege Bahia tecido do próprio WC, com a luz só do piso limpo; a linha do box ficou) e entrou o chuveiro do PDF (ARQ_LOUÇAS E METAIS) no desenho do WC DCE da Casa D: ducha quadrada com a placa da Casa A, braço cromado até a parede da direita e canopla, com sombra curta.
  12. arcos das portas sobre o granito (pedido do usuário): os 11 arcos sobre o Marrom Tabaco (o motor quase não os fez; só o do DCE, apagado e escuro) ficaram como nas Casas C e D: o arco escuro que houvesse saiu (granito tecido, só no granito da base chapada) e entrou o arco das curvas do PDF (ARQ_PAREDE) em cinza (160, 161, 160) e traço fino (0,45 px).
  13. pontos claros do granito (pedido do usuário: muitos, espalhados; tirar alguns): dos pontinhos claros compactos (2 a 16 px) que o motor salpicou no Marrom Tabaco, saíram os 67 que se destacavam (30 ou mais acima da mediana do granito em volta); ficaram os mais fracos e o grão fino. Cada um virou o granito de um trecho vizinho sem ponto, com borda suave; só onde o retoque não tinha mexido (arcos e X ficam).
  14. pilar à direita do lavabo (pedido do usuário): o retângulo cinza da ARQ_ELEMENTOS FIXOS (78 × 20 px), que o motor fez como uma peça cinza-taupe com folhas por cima, é um pilar: ficou no preto das paredes (o da parede do lavabo ao lado), na geometria do PDF, cobrindo as folhas.
  15. lavabo (pedido do usuário): cuba esculpida, com a torneira vindo do lado esquerdo. A cuba branca e a torneira preta que o motor pôs no meio da bancada saíram (as mesmas linhas de quartzo limpo da bancada, à esquerda e à direita em espelho); na metade esquerda da bancada do PDF entrou a cuba esculpida no próprio quartzo (fundo inclinado escurecendo até 12% para trás, fenda do ralo junto à parede, sombra curta das bordas de cima e da direita e traço fino na borda). A torneira do PDF sai da parede da esquerda: canopla e bica cromadas, com brilho e sombra curta.
  16. escritório (pedido do usuário): atrás do sofá é um arranjo de flores (o círculo do PDF, ARQ_LAYOUT HUMANIZAÇÃO); o motor tinha feito uma bola verde. Entrou o arranjo com a estrelítzia do próprio jardim do render (folhas em leque e as flores laranja, as mesmas do paisagismo), reduzida ao círculo do PDF (raio 7,2 px), com sombra curta.
  17. louceiro (pedido do usuário): veios aparentes de marcenaria. O motor deixou a madeira lisa; o veio veio do tampo da mesa de jantar do próprio render (veio no comprido), girado para correr no comprimento do louceiro e realçado 2,2 ×, como no mobiliário do DCE da Casa D; o tom e as bordas ficaram.
  18. escada interna (pedido do usuário): só sombreamento de subida, da direita para a esquerda, sem linhas. O travertino da escada foi refeito sem os tracejados dos degraus, a linha de corte e a diagonal (as mesmas colunas do travertino limpo abaixo da floreira); os 19 pisos do PDF (9,38 px) clareiam para a esquerda (o de baixo, à direita, 10% mais escuro) e cada espelho joga uma sombra curta (18%, decaimento de 2 px) no piso de baixo, à direita dele, inclusive o primeiro, no piso da sala. A diagonal do item 3 saiu junto.
  19. jardim de inverno (pedido do usuário): as plantas saem levemente da floreira, sem exagero: nunca por cima da escada (a borda de cima fica), até ~3,5 px para os lados e até ~6,5 px para baixo, com o limite irregular e as pontas sumindo num degradê de 2 px; só os px de folha do render original voltam (sem o halo claro), por cima do traço da floreira, com sombra curta desenhada no travertino. Entraram 5 flores tropicais espalhadas: as estrelítzias do jardim do render (laranja) e as mesmas em vermelho, rosa e amarelo (matiz girado).
  20. estar da varanda (pedido do usuário): ali não tem tapete. O tapete retangular que o motor pôs sob o sofá, as poltronas, a mesa de centro e o banco saiu (Bege Bahia tecido da própria varanda, na luz do piso em volta); os móveis (os polígonos brancos do PDF com 1 px de folga e o contorno escuro do render) ficaram, com a sombra curta deles no piso refeito.
  21. escada externa do alto (pedido do usuário): sem linhas, com sombreamento de descida da direita para a esquerda. Mesma rotina da interna (`escada`, agora com o lado de baixo como parâmetro): o travertino refeito sem as linhas (o da sala, veios verticais), os 17 pisos do PDF (9,32 px) escurecendo até 10% para a esquerda e a sombra curta de cada espelho no piso de baixo, à esquerda dele, inclusive o último, no deck.
  22. vaso do banho gourmet (pedido do usuário: com tampo): o motor deixou o símbolo do CAD (caixa com parafusos e bacia pontilhada). Ele saiu (granito tecido) e o vaso foi desenhado em 8 x no polígono do PDF, como os do Subsolo da Casa D, na escala deste render: louça com volume, contorno fino, sombra curta e o tampo fechado, da linha da dobradiça (junto à caixa, na parede de cima) à frente. Os outros três vasos (lavabo gourmet, lavabo e WC DCE 1) já tinham o tampo fechado no render.
  23. banho gourmet (pedido do usuário): faltavam a bancada da pia e a torneira. A bancada do PDF (ARQ_BANCADAS, 49 × 13 px, encostada na parede de baixo) é em granito marrom, como o piso: entrou pelo contorno cinza fino (160, 161, 160; o dos arcos sobre o granito), com o tampo 7% mais claro (polido) e sombra curta no piso; no painel do meio, a cuba esculpida no próprio granito (a mesma rotina da do lavabo, `cuba_esculpida`, com a fenda escura) e, no painel da esquerda, a torneira cromada do PDF (base redonda e bica até a cuba).
  24. porta do hall externo (pedido do usuário): faltavam a extensão e o arco. A porta do PDF tem duas folhas: a grande (que o render fez, com o arco para baixo) e a pequena, à direita (22 px), que abre para cima. A folha pequena entrou na espessura do PDF, no desenho da grande (traço escuro em cima, médio embaixo, miolo claro, os tons medidos nela), com o encontro das duas marcado, e o arco dela, da curva do PDF, no traço fino do arco da grande.
  25. brises da janela do escritório (pedido do usuário: em tons de madeira, do lado de fora): os 7 retângulos da ARQ_ELEMENTOS FIXOS junto à janela (6,8 × 4,6 px), que o motor apagou na grama, entraram como réguas de madeira (cada uma um trecho diferente do veio da mesa de jantar do render, deitado, num tom de 0,8 a 1,0), com contorno fino marrom-escuro e sombra curta na grama.
  26. carros (pedido do usuário: não precisam estar 100% alinhados): cada carro foi recortado (a silhueta do render), o granito voltou no lugar dele e da sombra (tecido, na luz em volta) e o carro voltou com deslocamento e giro leves, diferentes para cada um (branco: 6 px para baixo, -2,5°; prata: 4 px para cima, +1,5°; grafite: 2 px para baixo, -1°), com a sombra curta desenhada de novo.
  27. adega (pedido do usuário): prateleira de vinhos em U, não um armário em U. No polígono do PDF (ARQ_LAYOUT HUMANIZAÇÃO: braço de cima e os dois dos lados, ~12,5 px de fundo), a madeira lisa do motor ganhou o veio (o da mesa de jantar, no comprido de cada braço) e 40 garrafas deitadas em fileiras (passo 2,6 px), com o gargalo para a parede de cada braço, em vidro escuro verde, âmbar e vinho alternados, com o brilho no comprido e sombra curta na madeira.
  28. área de serviço (pedido do usuário): a faixa junto à parede de baixo é em parte armário e em parte bancada para roupas; o motor tinha feito tudo em madeira lisa. À esquerda, o armário do PDF (ARQ_LAYOUT HUMANIZAÇÃO, 25 × 19 px) ficou em marcenaria areia com o veio (o mesmo do louceiro); à direita, a bancada (ARQ_BANCADAS, 45 × 19 px) virou o quartzo do tanque (tecido das pontas limpas da bancada dele, no tom dela), com contorno fino nas duas peças.
  29. cozinha, fileira junto à parede de baixo (pedido do usuário): ao centro, dois eletrodomésticos (ou a geladeira) em inox; nas laterais, armários. Os dois quadrados do centro (ARQ_LAYOUT HUMANIZAÇÃO, ~25 px) receberam os eletrodomésticos em inox da cozinha aprovada da Casa D (cada um, uma metade do par de lá), com sombra curta; os dois trechos dos lados viraram armários em marcenaria areia com o veio do louceiro, sem sombra de móvel baixo; contorno fino em todas as peças.
  30. spa (pedido do usuário): mais um degrau na parte de dentro, formando um quadrado. No PDF o spa tem dois contornos internos (o degrau, em volta, e o fundo); o render só tinha o do fundo. Entrou o contorno de fora do degrau (ARQ_PAREDE, 4,3 px para fora do fundo), como na Casa D, com o perfil de luz das arestas do próprio render (medido na aresta do fundo: sombra larga em cima e à direita, traço fino à esquerda e embaixo), a 80%.
  31. piscina, lado esquerdo (pedido do usuário): são duas folhas de vidro. As duas faixas brancas que o motor fez ficaram como as folhas do PDF (ARQ_PAREDE, 2,8 px cada, com o vão de água entre elas), no desenho dos vidros finos do Subsolo da Casa D: vidro claro, linha central fina e contorno fino.
  32. paisagismo logo abaixo das escadas (pedido do usuário): o bolsão de grama entre as pedras, os degraus e o banco de bronze ganhou um canteiro, como os da Casa D: um trecho das costelas-de-adão do próprio render (o canto do lote, sem a pedra), espelhado, com o contorno orgânico onde o trecho corta a touceira, só sobre a grama (pedras e banco ficam), emendando nas plantas que já existiam embaixo.
  33. garagem, lateral direita (pedido do usuário): faltavam os brises. Os 8 retângulos da ARQ_ELEMENTOS FIXOS (6,9 × 4,6 px, a cada 10,9 px) sobre o granito, acima do trecho de parede, entraram no mesmo desenho dos brises do escritório: réguas de madeira em tons variados, contorno fino marrom-escuro e sombra curta.
  34. banco do estar da varanda (pedido do usuário): banco de madeira sem encosto. O encosto de madeira que o motor pôs embaixo do banco saiu (Bege Bahia tecido da varanda, com a sombra dele); o banco, no retângulo do PDF (68 × 19 px), virou um tampo de madeira (a da mesa de jantar do render, veio no comprido) em 4 ripas com juntas finas, contorno fino e sombra curta, sem as almofadas.
  35. piscinas (pedido do usuário, com a legenda do cliente: "revestimento Barlavento piscina"): o Barlavento é a linha da Portobello que reproduz a pedra hijau, em peças de 14,5 × 14,5 cm (tom Caribbean, entre o azul e o verde). A água turquesa saturada do motor, com a rede de reflexos brancos marcada, virou a pedra das peças (gerada por código, `fontes_procedurais.barlavento`: ~4,5 px por peça, tons verde-acinzentados e azulados alternados com variação sutil, grão fino e juntas finas) sob uma água verde-azulada clara (BGR 214, 222, 172). Ajustes pedidos: sem as manchas escuras de sombra (davam aspecto de sujo), luz chapada com só uma sombra curta junto às bordas e o degrau da prainha (x = 510,4) marcado de leve; e efeitos da água para não parecer vazia: a grade ondulada pela refração (~1 px), a rede de cáusticas do próprio render mais suave (só clareia) e um brilho difuso na diagonal. Piscina, prainha e spa (a mancha da água na base chapada); o degrau do spa e as folhas de vidro vêm depois, por cima.
- **Aprovado pelo usuário (15/10/26):** `renders/POE642_CasaE_PH_Terreo_v1_retocado.png` (itens 1 a 34); depois da aprovação, o item 35 (Barlavento nas piscinas) e a prancha e o PDF refeitos com ele.
- **Entrega (15/10/26, depois da aprovação):** chave `entrega` na `POE642_CasaE/config_bases.json`, por decisão do usuário: endereço ML 10 – Conjunto 02, Lotes 17, Unidade E (projeto CASA E · UNIDADE AUTÔNOMA "E"), norte o mesmo das outras casas, quadro de áreas com Térreo "NÃO INFORMADO" e sem total. Só o Térreo (o PDF do Subsolo não veio; se vier, entra como na Casa D). Prancha `entrega/POE642_CasaE_PH_Terreo_entrega.png` (3840 × 2600 px; o retocado realinhado à base com 132 pontos, erro mediano 0,77 px), rodapé `entrega/POE642_CasaE_rodape_Terreo.png` e `entrega/POE642_CasaE_Plantas_Humanizadas.pdf` (1 página A3, 12,5 MB).

## Casa E · 1º Pavimento

- **PDF:** `_pdfs_cliente/642 - 1º PAVIMENTO - CASA E.pdf` (recebido em 15/10/26; mesma folha 3370 × 2384 pt e mesmo enquadramento). Pavimento `1Pavimento` na `POE642_CasaE/config_bases.json` (curvas de nível ocultas).
- **Ambientes (textos do PDF):** sala íntima (44,94 m²), circulação (19,3 m²), copinha (3,85 m²), suíte master (28,89 m²) com closet master (10,56 m²) e banho master (19,72 m², banheira), rouparia (3,6 m²), elevador; suítes 1 e 2 (17 m² cada) com closets (3,78 m²), banhos (5,94 m²) e varandinhas (5,2 m²); suítes 3 e 4 (19,98 m²) com closets (3,15 m²) e banhos (4,95 e 4,92 m²); varanda grande à esquerda (65,75 m²); escada de 20 degraus; o vazio do hall de entrada embaixo à direita (X tracejado).
- **Cores do PDF:** laranja #CC9966 (suítes, sala íntima, circulação, closet master, rouparia), cinza #E4E4E4 (as três varandas); banhos brancos com hachura fina; closets das suítes 1 a 4, copinha, escada e elevador brancos.
- **Base v1** (cores do PDF): `bases/POE642_CasaE_BASE_1Pavimento_v1(_16x9)` e a prévia `_16x9_preview.jpg`.
- **Materiais (usuário, 16/10/26):** vinílico #A8784F (o mesmo da área íntima do 1º Pavimento da Casa A, Durafloor City Petra) em todo o laranja (suítes, closets, closet master, rouparia, sala íntima, circulação); quartzito Aura #EAD4BF (a cor pêssego da legenda do cliente, `images/1.png`) nos cinco banhos; Bege Bahia #E8E8E8 nas três varandas e na bancada da copinha. Padrões das outras casas: armários (brancos com diagonal) em marcenaria areia #CBB89E; escada em travertino #DCD9CA, como a do Térreo; vazios em #4A4A4A com o X claro (sobre o jardim interno do Térreo, abaixo da escada, e o pé-direito duplo do hall de entrada), como na Casa A. Legenda na `POE642_CasaE/config_bases.json`.
- **Base v2** (legenda): `bases/POE642_CasaE_BASE_1Pavimento_v2(_16x9)` e a prévia. Os banhos são retângulos `so_branco` com as louças, bancadas, plantas e o layout protegidos e a hachura do contrapiso apagada (como os banhos da Casa D); a cuba da copinha fica branca. O pontilhado rosado da hachura dos banhos (não é cinza) some no quartzito com a opção nova `apagar_hachura_quente` do `gerar_bases.py`.
- **Base v3 (texturas):** `bases/POE642_CasaE_BASE_1Pavimento_v3_texturas(_16x9)` e a prévia. Vinílico das suítes do 1º Pavimento da Casa A, Bege Bahia das varandas da Casa A, travertino do hall do Subsolo da Casa A (escada), marcenaria areia do Térreo retocado da Casa D (armários) e o quartzito Aura gerado por código (`fontes_procedurais.quartzito_aura`, saída `bases/fontes/quartzito_aura.png`: placas de 90 cm, pêssego claro #EAD4BF com nuvens suaves, veios finos e fluidos claros e alguns dourados, juntas finas).

## Casas A a D · Barlavento nas piscinas

Pedido do usuário (15/10/26), depois do item 35 da Casa E: as piscinas das Casas A, B, C e D no mesmo revestimento Barlavento, com os mesmos efeitos de água, e as pranchas e os PDFs refeitos.

- **Script:** `scripts/piscinas_barlavento.py`. Usa os números aprovados na Casa E (cor da água BGR 214, 222, 172; sombra curta só junto às bordas; refração de ~1 px; cáusticas do render suavizadas; brilho difuso na diagonal) e a mesma pedra (`fontes_procedurais.barlavento`).
- **Água:** achada pela cor do próprio render (azulada, B acima de R), em manchas grandes. Ficam por cima, como estavam: bordas, espreguiçadeiras (Casa B, sem o halo claro da sombra antiga) e os tracejados de projeção (Casa A). O contorno escuro de 1 px junto às bordas entra na água, para não sobrar em entalhes.
- **Degraus e contornos internos:** as linhas do projeto dentro da água, tiradas da base chapada da casa alinhada ao render (SIFT + afim) e reduzidas por área (as linhas de 1 px da base não somem na redução). Marcadas de leve, numa linha fina: degrau da prainha e anel do spa (A); faixa junto ao deck e anel do spa (B); os três degraus da prainha e o anel do spa (C); o degrau duplo da prainha e o anel duplo do spa (D).
- **Imagens:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_bege_barlavento.png`, `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_v4_retocado_barlavento.png`, `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_v3_retocado_barlavento.png` e `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento.png` (as anteriores ficam como estavam).
- **Entrega refeita:** a prancha do Térreo de cada casa (`entrega/POE642_CasaX_PH_Terreo_entrega.png`) e o PDF (`entrega/POE642_CasaX_Plantas_Humanizadas.pdf`); os outros pavimentos não mudam. Na Casa A, o GIF `POE642_CasaA_pranchas_perfiladas.gif` não foi refeito.

```bash
# da pasta projetos/
python3 POE642_CasaA/scripts/piscinas_barlavento.py POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png \
    POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento.png \
    --base POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v3_texturas_16x9.png --chapada POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v2_16x9.png
# Casa A: --base e --chapada = POE642_CasaA/bases/POE642_CasaA_BASE_Terreo_v6_16x9.png
# depois, de POE642_CasaA/scripts/: rodape_entrega.py --render Terreo=<..._barlavento.png> e pdf_entrega.py (com --config das Casas B, C e D)
```

- **Casa D, ajuste da piscina (15/10/26):** pedido do usuário: "não gostei da finalização da piscina. precisa melhorar a borda da piscina, degraus internos [...]. pode fazer uma borda com dreno" e "o dreno é apenas uma linha contínua fina. somente na parte externa da piscina". Script `scripts/piscina_dreno_casad.py` (parte do render retocado, sem o Barlavento v1):
  - **borda:** a água vai até o contorno do projeto, sem sombra de parede, só com uma leve definição junto ao piso;
  - **dreno:** uma linha contínua fina e escura no piso (~2 cm), a ~6 cm da água, só no contorno de fora do conjunto piscina + spa (a faixa entre os dois não leva), com cantos em esquadro;
  - **degraus internos:** as linhas duplas pareciam um rasgo no fundo. Agora cada nível tem a sua profundidade (fundo 1,40 m, degrau da prainha 0,80, prainha 0,30; banco do spa 0,45, degrau 0,65, fundo 0,90): a água fica mais clara no raso e o degrau é a troca de tom, com uma luz fina na quina e uma sombra curta ao pé. O fundo da piscina segue no tom aprovado;
  - imagem `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v2.png`; prancha do Térreo e PDF da Casa D refeitos com ela.
- **Casa D, borda da piscina conforme a referência (15/10/26):** o usuário mandou um render de como é a borda ("segue um render de como é a borda dessa piscina") e: "são duas linhas de borda, entendeu?". Em volta do conjunto piscina + spa, uma capa de pedra da largura da faixa entre os dois (~8 px, ~26 cm), levemente mais clara que o piso; na borda de fora dela, o dreno em duas linhas finas paralelas contínuas (as bordas do canal, ~2,4 px entre elas), cantos em esquadro; a faixa entre a piscina e o spa é capa, sem dreno. A água volta a ter a sombra curta aprovada da borda (0,12; 1,6 px). Degraus em níveis como no ajuste anterior. Imagem `POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v3.png` (a v2, de uma linha só junto à água, fica como estava); prancha do Térreo, PDF e a prévia `renders/POE642_CasaD_PH_Terreo_piscina_antes_depois.jpg` refeitos.
- **Casa D, borda alta (15/10/26):** pedido do usuário: "preciso que a borda rente a água seja mais alta que a água. preciso que tenha uma borda mesmo". A capa de pedra (~26 cm, ×1,03 do piso) fica acima da água (~12 cm): projeta na água uma sombra limpa e uniforme do lado da luz (força 0,28, 3,2 px, penumbra 0,45 px; as sombras do render caem para baixo à esquerda, então ela fica junto às bordas de cima e da direita da piscina e do spa e à esquerda da faixa entre os dois), com a linha fina do desnível junto à água em volta toda (0,20; 0,55 px) e a quina da capa iluminada (×1,07, 0,8 px). Reflexos mais fracos na sombra. Dreno em duas linhas e degraus em níveis como antes. Imagem `POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v4.png` (v3 fica como estava); prancha do Térreo, PDF e prévia antes × depois refeitos.

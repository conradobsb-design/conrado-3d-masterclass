# POE 642 · Casas A e B — handoff para continuar no computador local
_14/10/2026. Estado ao fim da sessão na nuvem. Branch: `claude/poe642-casa-a-handoff-jmchm3`. PR: conradobsb-design/conrado-3d-masterclass#1 (rascunho)._

**Regras de representação: `POE642_REGRAS.md` (consolidadas em 19/10/26). Elas valem mais que as decisões antigas registradas aqui.**

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

**Pendência opcional:** os renders da Casa A chegaram comprimidos pelo chat (2000 px). Desde os nomes e áreas (18/10/26) as pranchas saem em 3840 px, com a imagem ampliada e os rótulos nítidos (ver "Casa A · nomes e áreas dos ambientes"). Com os PNGs originais do motor, rode de novo os retoques, o `rotulos_casaa.py` e o `rodape_entrega.py`.

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
  36. nomes e áreas dos ambientes (pedido do usuário, 16/10/26: "vamos voltar no térreo da Casa E e adicionar os rótulos com área. seguindo o padrão que determinamos"). A regra do 1º Pavimento e do Subsolo: cada linha igual ao PDF, na posição do PDF, no corpo do PDF 30% maior, em Inter Regular preta; no granito Marrom Tabaco, cinza (150); sobre móvel ou peça, o piso livre mais próximo.
     - Escritos na imagem final `renders/POE642_CasaE_PH_Terreo_v1_final.png` (3840 × 2160): o retocado levado ao quadro comum, como na prancha, mais os rótulos. O retocado de 2000 px fica sem rótulos, porque é o contexto do 1º Pavimento na opção P&B. Comando: `--so-final` sobre o retocado aprovado; o retocado não é regravado (o script inteiro o reproduz com diferença máxima de 1 nível).
     - 29 rótulos. Ficam fora as sete notas "PROJ. COBERTURA" (projeção da cobertura, não são ambientes) e o título da folha.
     - Os nomes em duas linhas no PDF ("LIVING E SALA DE / JANTAR", "ÁREA DE SERVIÇO / DESCOBERTA", "CIRCULAÇÃO / GOURMET") entram como um rótulo só. Separadas, cada linha crescia em volta do próprio centro e as duas se encostavam. A junção está em `retoque_1pav_casae.rotulos_pdf`; o 1º Pavimento e o Subsolo saem idênticos.
     - Deslocados ao piso livre: garagem (estava sobre o carro do meio: abaixo dos carros, no granito), varanda (nas cadeiras da mesa redonda: entre elas e o sofá), DCE (encostado na cama), área de serviço (nas máquinas), cozinha (nos bancos da ilha) e a circulação de 7,11 m² (na parede do escritório), estes quatro só alguns px.
     - WC DCE 1: o "1" caía no chuveiro e o 1,3× não cabe no piso livre do box. Fica no corpo do PDF (1,0×), um pouco à esquerda, como o WC DCE 2 do Subsolo.
     - Lavabo gourmet: o ambiente é uma faixa estreita entre o banco e a parede, e "LAVABO GOURMET" passava por cima dos dois. O nome entra em duas linhas ("LAVABO" / "GOURMET"), no 1,3×, no meio da faixa.
     - Jardim interno: todo planta, e no verde escuro o preto e o cinza somem. Fica na posição do PDF, em branco (250).
     - Louceiro: o rótulo fica sobre a peça, que é o próprio ambiente (não há piso livre nele).
     - `rotulos_ambientes` aceita nos ajustes um dicionário de opções: `corpo`, `quebra` (o nome em mais linhas, centradas) e `cor`.
     - Entrega refeita: a prancha do Térreo agora usa a imagem final (`--no-quadro`); só os rótulos mudaram, em 23.658 px, e o rodapé ficou igual. Os dois PDFs (opções P&B e linhas, Subsolo, Térreo e 1º Pavimento) foram refeitos.
  - **Regras de 19 e 20/10 (`POE642_REGRAS.md`), um item por vez (20/10/26).** Ordem pedida pelo usuário: "Pode seguir para o térreo da casa E. Depois, vamos voltar para o subsolo." Os itens entram depois do retocado aprovado (itens 1 a 35), e a imagem final passa a ser alinhada nele (`referencia=`, como no Subsolo): cada item novo muda só a área dele.
  37. box do banho gourmet (R5: "representar o boxe no banho gourmet, pois não está representado"). No PDF (ARQ_LOUÇAS E METAIS) o box é de correr, com duas folhas de vidro: a fixa, junto à parede de baixo (736,9 a 784,1 pt), e a de correr, por dentro (725,0 a 772,3 pt), sobrepostas no meio; o vão fica em cima, junto à parede da janela. O motor tinha feito só um traço escuro de parede a parede (x = 673 px); ele saiu (a coluna virou a do granito 2 px à direita, com a mesma textura). As folhas entraram no desenho do box da referência (`_texturas/elementos.py`): linha clara de vidro (226, 229, 230), sem montantes nem pontos, a borda cinza fina do lado do chuveiro e a sombra suave no piso do box. Na escala do render (0,55 px/pt) o vidro de 1 cm teria 0,3 px; cada folha vai com 0,8 px, no eixo dela. Conferência: no retocado mudou só a coluna do box (5 × 50 px); na imagem final e na prancha, só o trecho do box (20 × 98 px). Prancha do Térreo e os três PDFs refeitos; o rodapé ficou igual. Antes e depois: `renders/POE642_CasaE_PH_Terreo_box_gourmet_antes_depois.jpg`. As montagens do 1º Pavimento (que usam o Térreo como contexto) serão refeitas uma vez, no fim dos itens do Térreo.
  38. portas sem os arcos (R3: "Não mostrar arco da porta"). Os 16 arcos de porta do PDF (ARQ_PAREDE). Os 11 no granito eram o cinza fino do item 12, desenhado pelo próprio script, e o da folha pequena do hall era o do item 24: os dois itens deixam de desenhá-los (o arco escuro que o motor fez no DCE continua saindo, no item 12). Os 4 que o motor fez no travertino e no Bege Bahia (lavabo, hall de entrada, lavabo gourmet e WC DCE 1) saem pelo `arcos.remover_arcos`, o mesmo do Subsolo, só nos arcos fora do granito, com faixa de ±2 px e o tracejado do PDF protegido, para o X do hall seguir inteiro. Ficam as folhas e os batentes. Junto aos arcos do granito saíram 3 pontinhos claros que o traço do arco protegia no item 13 (69 de 71 pontos fortes, antes 67). Como a R3 muda itens antigos (12 e 24), o alinhamento da imagem final passou a vir do arquivo do aprovado, `renders/POE642_CasaE_PH_Terreo_v1_retocado_aprovado.png` (o retocado de 15/10, itens 1 a 35); com ele, a final do item 37 sai idêntica, px a px. Conferência: no retocado, na final e na prancha mudaram só as 16 áreas dos arcos. Prancha do Térreo e os três PDFs refeitos; rodapé igual. Antes e depois: `renders/POE642_CasaE_PH_Terreo_sem_arcos_antes_depois.jpg`.
  39. escadas com linhas e o triângulo de orientação (R14), como no Subsolo da mesma casa. O sombreamento dos itens 18 e 21 ("só sombreamento, sem linhas", pedido anterior) sai, pois a regra de 19/10 ("escadas com linhas") o substitui; fica o travertino limpo deles. Na geometria do PDF (ARQ_ESCADAS E RAMPAS): em cada bocel uma linha suave (20% mais escura, 0,55 pt) e, logo depois, a sombra curta (16%, 10 cm) no degrau de baixo; o triângulo cheio cinza-escuro (24 × 26 cm, a 10 cm do início, no meio da largura) no início do percurso. Interna (19 pisos): sobe da direita para a esquerda (o "S" do PDF à direita); depois do corte (o do PDF, depois do 7º degrau), esmaecida, com os bocéis e o contorno tracejados, como o PDF. Externa do alto (17 pisos): toda viva; o sentido ficou invertido em relação ao PDF (ver abaixo). Os degraus soltos de Bege Bahia junto à piscina (5 a 11 no PDF) não têm S/D no PDF e ficaram como estavam. Conferência: só as duas escadas mudaram (retocado, final e prancha). Prancha e os três PDFs refeitos. Antes e depois: `renders/POE642_CasaE_PH_Terreo_escadas_r14_antes_depois.jpg`.
    - Sentido da externa do alto: ela fica exatamente sobre a do Subsolo (mesma caixa no PDF, 972 a 1263 pt), que sobe da direita para a esquerda (decisão do usuário, contra o PDF). Primeiro saiu descendo da direita para a esquerda (o "D" do PDF e o pedido do item 21); perguntado se era o mesmo lance, o usuário respondeu (20/10/26): "pode inverter". Agora desce da esquerda para a direita: o triângulo à esquerda, apontando para a direita, e a sombra à direita de cada bocel (`baixo` e `inicio` em `ESCADA_LINHAS`). Só a escada externa mudou. Antes e depois: `renders/POE642_CasaE_PH_Terreo_escada_externa_invertida_antes_depois.jpg`.
  40. rótulos (R6: "Apresentar os rótulos em branco quando for piso marrom granito"; R7: "Proibido apresentar rótulos sobre objetos"). Os 12 rótulos sobre o Marrom Tabaco (circulação de cima, garagem, área de serviço e a descoberta, DCE, gás, despensa, CPD, cozinha, área gourmet, circulação gourmet e BH gourmet) passaram do cinza 150 ao branco (250), como no Subsolo (`cor_granito`); os outros ficaram iguais. Os 29 rótulos foram conferidos um a um: nenhum fica sobre móvel ou peça (os desvios do item 36 já os levavam ao piso livre). Exceção: o LOUCEIRO fica sobre a marcenaria, que ocupa o ambiente inteiro (não há piso livre nele). Conferência: retocado igual; na final e na prancha mudaram só os 12 rótulos. Prancha e os três PDFs refeitos. Antes e depois: `renders/POE642_CasaE_PH_Terreo_rotulos_granito_antes_depois.jpg`.
  41. carros (R12: "todos os carros de todas as plantas devem estar alinhados, serem do mesmo tamanho e da mesma cor"; prata, 4,70 × 1,85 m). O item 26 (carros em três cores, levemente desalinhados, pedido anterior) passa a: apagar os três carros como antes (granito tecido) e pôr, no centro de cada carro do PDF (ARQ_LAYOUT HUMANIZAÇÃO, as duas metades de cada um; os três na mesma linha, y = 863,2 pt), o carro prata do render (o do meio) como modelo único, levado a 4,70 m de comprimento e 1,85 m de carroceria sem os retrovisores (146 × 58 px a 31,1 px/m; o modelo tinha 140 × 55 px), sem giro, com a sombra curta. Conferência: só a garagem mudou (os três carros); o rótulo GARAGEM continua abaixo deles. Prancha e os três PDFs refeitos. Antes e depois: `renders/POE642_CasaE_PH_Terreo_carros_r12_antes_depois.jpg`.
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
- **Prompt v1:** `POE642_CasaE_PH_1Pavimento_v1.md` (entrada: `bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png`). A casa vai de ~30% a ~69% da largura e de ~20% a ~74% da altura; as linhas tracejadas do lote ficam a ~7% e ~92,5% da largura e a ~95% da altura. Fundo branco (sem entorno do Térreo, como na base). Ambientes descritos por posição, porque o texto do PDF sai da base.
- **Entorno (pedido do usuário, 16/10/26):** vegetação no entorno da residência, com o Térreo esmaecido em volta, como no 1º Pavimento da Casa A (opção escolhida entre: Térreo esmaecido, Térreo em cor cheia ou só grama).
  - **Base v4:** `bases/POE642_CasaE_BASE_1Pavimento_v4_entorno_16x9.png` e a prévia. É a v3 com texturas, mais o render aprovado do Térreo (`renders/POE642_CasaE_PH_Terreo_v1_retocado.png`, com o Barlavento) em volta da pegada do 1º Pavimento.
    - O Térreo vai ao quadro comum (106 pontos, erro mediano 1,28 px na largura da base), 75% mais claro e 60% menos saturado (o usuário pediu "temos que esmaecer mais"; antes, 50% e 40%; comparados 50, 65 e 75%).
    - A área branca abaixo da sala íntima, fora da casa, também mostra o contexto (`--fora 912 752 1096 816`). Antes a área começava em x 820 e levava junto a parte de baixo da escrivaninha da suíte de baixo à esquerda (branca na base); corrigido na montagem com o render retocado, e a base v4 e a camada recortada foram refeitas.
    - Script novo: `scripts/entorno_esmaecido.py`.
  - **Prompt v2:** `POE642_CasaE_PH_1Pavimento_v2.md` (entrada: a base v4). O fundo branco virou o Térreo esmaecido, mantido exatamente como está; a vegetação fica só nele; em cor cheia, só o 1º Pavimento.
  - **Fluxo escolhido (usuário, 16/10/26):** para a fidelidade, o Térreo não passa pelo motor (nem como imagem 02, que arrisca desalinhar e misturar os pavimentos). O motor renderiza só o 1º Pavimento em fundo branco (base v3 + prompt v1). Depois, o `entorno_esmaecido.py` com `--base-cima` põe o Térreo aprovado esmaecido em volta, e o render do 1º Pavimento por cima, integralmente ("na parte do 1º pavimento, sobrepor integralmente"). A pegada sai da base (geometria do projeto), não do render. A base v4 e o prompt v2 ficam como alternativa.
  - **Camada do Térreo recortado:** `bases/POE642_CasaE_1Pavimento_entorno_terreo_recortado.png` (3840 × 2160, RGBA): o Térreo esmaecido com a área do 1º Pavimento transparente, para montar por cima (opção `--recorte`). Teste com a base v3 no lugar do render: 787 pontos, erro mediano 0,16 px.
- **Render v1:** `renders/POE642_CasaE_PH_1Pavimento_v1_render.webp` (2000 × 1116; base v3 + prompt v1, fundo branco), na escala da base: SIFT + afim com 56 pontos, escala 0,9997 × 1,0085. O que diverge da base está marcado em `renders/POE642_CasaE_PH_1Pavimento_v1_erros.jpg`.
- **Retoque** (`POE642_CasaA/scripts/retoque_1pav_casae.py`, sem IA, um item por vez; saída `renders/POE642_CasaE_PH_1Pavimento_v1_retocado.png`, `_camada.png` e `_previa.jpg`):
  1. banho master, floreira: as três plantas do PDF junto à janela da parede da esquerda; o motor deixou o piso liso. Entram as plantas tropicais do jardim interno do Térreo aprovado (um trecho girado para a vertical), no retângulo do PDF, com contorno fino da floreira e sombra curta;
  2. banho master, chuveiros: o motor pôs uma ducha de parede com braço e um registro no piso; saem (quartzito tecido do próprio banho) e entram as duas placas de teto de 30 cm da Casa A nos centros dos quadradinhos do PDF;
  3. banhos das duas suítes da esquerda: sem retoque. As bacias parecem uma peça só atravessando a parede, mas o PDF desenha assim: duas bacias suspensas, costas com costas na parede entre os banhos. O render ficou fiel (um redesenho testado ficou pior, com halo, e saiu);
  4. copinha: o motor pintou a bancada em areia, como o armário ao lado, e não pôs a cuba. A bancada do PDF (da parede da esquerda ao armário) virou o Bege Bahia da varanda da esquerda do próprio render, na luz da bancada do render; a cuba redonda da Casa A entrou no círculo do PDF (34 cm), com a torneira atrás, no cromo das cubas do Térreo. O armário à direita fica em areia;
  5. vazios (abaixo da escada, sobre o jardim de inverno do Térreo, e no hall de entrada): o motor deixou o cinza-escuro liso. Primeiro entrou o X tracejado do PDF sobre o cinza; depois, a pedido do usuário ("use a cor branca, em vez de cinza escuro"), os vazios ficaram brancos (250, como os da Casa A), com o X do PDF em cinza médio (cada traço da DOC_LINHAS E PROJEÇÕES na posição exata: 34 e 35 traços) e o guarda-corpo de vidro que isola os vazios (usuário: "tem um guarda corpo de vidro isolando essas áreas vazadas"): os retângulos de 2 cm da ARQ_ELEMENTOS FIXOS, na base e à esquerda do vazio da escada e à esquerda do vazio do hall, numa faixa fina no vidro fino aprovado. Nos lados com guarda-corpo o vazio vai até o vidro do PDF (o motor tinha deixado o piso entrar até 4 px);
  6. arcos das portas: o motor desenhou as folhas, mas nenhum arco. Entraram os 12 arcos do PDF (curvas da ARQ_PAREDE) no padrão aprovado no Térreo (cinza (160, 161, 160), traço de 0,45 px). Sobre o vazio do hall entrou também a folha da porta pivotante P1 do hall do Térreo (vista pelo vazio), que faltava;
  7. cortinas (usuário: "desenhe as cortinas"): as linhas onduladas do PDF ao longo das janelas das suítes (10 trechos, 160 arcos da ARQ_LOUÇAS E METAIS) entraram nas posições exatas como cortina de linho off-white, em traço fino, com a sombra curta aprovada (um branco puro testado antes ficou forte demais);
  8. vasos nas varandas: ficam (usuário: "mantenha os vasos");
  9. shaft (usuário: "preciso da marcação em x para sinalizar o shaft ... pode desenhar em cor cinza"): o PDF tem um shaft dentro da parede grossa de cima da suíte master (retângulo e X tracejado, 10 traços da DOC_LINHAS E PROJEÇÕES), que sumia no preto da parede; entrou em cinza (147), fino;
  10. fachadas das suítes (usuário: "temos 3 camadas: cortinas, portas de vidro finas e delicadas de correr e brises em bronze"; "brise de bronze mais a externa da fachada"; "portas/folhas de vidro de correr nas varandas, mais finas e melhor representadas"): o motor fez um caixilho largo e cinza na faixa da janela e nenhum brise. A faixa da parede foi refeita pelo PDF: parede em preto, vão como soleira no Bege Bahia da varanda, as folhas de correr do PDF (9 na fachada da esquerda, 6 na da direita, com os montantes) e as 2 janelas dos banhos da esquerda no vidro fino; o sombreado do caixilho no piso de dentro saiu. Os brises entraram como faixa de bronze nas duas colunas do PDF: a fachada da esquerda (na frente das suítes e dos banhos) e a borda de fora das varandas da direita;
  11. cubas no lugar do PDF: nos banhos das suítes da direita (usuário: "cuba posicionada mais à direita da bancada da pia") a cuba fica no lado direito da bancada, junto ao vaso, e o motor a pôs no meio: foi 10,8 e 10,7 px para a direita. Nos dois banhos da esquerda, costas com costas (usuário: "ambas as cubas estão mais à esquerda, do que centralizadas nas bancadas"), a cuba fica no lado esquerdo da bancada e o motor a centralizou: foi 9,6 px para a esquerda. A cuba é a do próprio render, com a torneira; o tampo onde ela estava foi refeito com o trecho limpo do lado;
  12. bancos em frente às camas (usuário: "faltando os bancos em frente às camas"): o PDF tem um banco no pé de cada cama das cinco suítes, na largura da cama; o motor não desenhou e fez as camas um pouco mais compridas (3 a 5 px; a da master, 22 px). Cada banco entrou no pé da cama do render, com a folga do PDF, na largura e altura do PDF, primeiro no banco de madeira em ripas aprovado no Térreo e depois, a pedido do usuário ("para os bancos em frente às camas use o tom bege"), estofados em bege; depois (usuário: "precisam ter textura de estofados") com almofadas lado a lado (3 na master, 2 nas outras) que levam o tecido, o volume e as costuras da almofada do assento do sofá da sala íntima do próprio render, uma trama fina de tecido, contorno bege escuro e a sombra curta;
  13. torneira de piso da banheira do banho master (usuário: "faltou a torneira de piso da banheira"): a do PDF fica no canto de cima, à esquerda, da banheira (base redonda de ~16 cm logo fora da borda e a bica em diagonal sobre ela). A banheira do render é maior que a do PDF (semi-eixos 19,0 x 37,2 px contra 13,9 x 26,2); a torneira entrou na mesma posição relativa ao contorno da banheira do render, no tamanho do PDF, no cromo aprovado e com sombra curta;
  14. nomes e áreas dos ambientes (usuário: "insira as cotas nos ambientes"; o PDF não tem linhas de cota, e o usuário escolheu nome + área do PDF). Histórico dos pedidos: a primeira versão, maior e em seminegrito, ficou "grosseira" → "no tamanho de como está no PDF" → "em piso ... na cor preta; no granito marrom, cinza" → "um pouco maior a fonte" → "na mesma posição [do PDF] e com leitura visível". → "nesses casos em que o escrito fica sobre algum mobiliário, está autorizado deslocar para outro local do piso". Versão atual: cada linha dos 23 rótulos igual ao PDF (texto "SUÍTE 1 / A: 17 m²"), na posição do PDF, no corpo do PDF 30% maior, em Inter Regular preta (a Light ficava fraca). Os seis que caíam sobre móvel foram ao piso livre mais próximo: suíte master (estava sobre o banco: abaixo dele, fora do tapete e do pufe), banho master (na ponta da banheira: logo abaixo), sala íntima (no braço do sofá: à esquerda), closet 2 e closet 3 (na borda do armário: para dentro do piso) e copinha (sobre a bancada: no piso em frente). **Regra para os próximos pavimentos:** posição e texto do PDF; sobre móvel, o piso livre mais próximo; texto preto; no granito marrom, cinza (150). O script salva também `renders/POE642_CasaE_PH_1Pavimento_v1_retocado_sem_rotulos.png`: é ela que vai à montagem com o Térreo esmaecido, e os rótulos são escritos de novo em 3840 px (pendente: cor ou P&B).
- **Opções para o cliente (usuário, 16/10/26: "vou apresentar ao cliente duas opções: em preto e branco e só com as linhas do PDF"):** `POE642_CasaA/scripts/opcoes_1pav_casae.py`, em 3840 × 2160.
  - `renders/POE642_CasaE_PH_1Pavimento_v1_final_pb.png` (e `_preview.jpg`): o Térreo aprovado em volta, 75% mais claro e em preto e branco.
  - `renders/POE642_CasaE_PH_1Pavimento_v1_final_linhas.png` (e `_preview.jpg`): o Térreo só com as linhas do PDF (sem as camadas de piso, curvas de nível, textos e zonas), em cinza.
  - Nas duas, o 1º Pavimento retocado entra por cima integralmente e os nomes e áreas são reescritos em 3840 px (nítidos), com as mesmas regras. Os rótulos longos saíam cortados no fim ("CLOSET MASTE…"): a área de desenho do texto ficou mais larga, também na imagem de 2000 px.
- **Pranchas e PDFs das duas opções (usuário, 16/10/26: "prepare as pranchas para cada uma delas e os PDFs"):**
  - **Config:** o 1º Pavimento entrou na chave `entrega` da `POE642_CasaE/config_bases.json` (título "1º PAVIMENTO", linha 1 do quadro de áreas, base `POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png`). O quadro de áreas ficou com Térreo e 1º Pavimento "NÃO INFORMADO", sem total, como no Térreo (o PDF traz só as áreas dos ambientes). Em `pdf.ordem`: Térreo e 1º Pavimento.
  - **Scripts:** `rodape_entrega.py` ganhou `--sufixo` (versões da mesma prancha) e `--no-quadro` (a montagem já está no quadro comum, em 3840 px: entra como está, sem realinhar nem reamostrar). `pdf_entrega.py` ganhou `--prancha PAVIMENTO=ARQUIVO`, `--titulo` e usa `--nome`.
  - **Pranchas (3840 × 2600 px):** `entrega/POE642_CasaE_PH_1Pavimento_entrega_pb.png` e `..._entrega_linhas.png`. A do Térreo (`..._Terreo_entrega.png`) foi refeita só pelo rodapé novo (o quadro de áreas agora tem as duas linhas); a imagem é a mesma (realinhada com 128 pontos, erro mediano 0,78 px; diferença máxima de 1 nível para a anterior). Rodapés `entrega/POE642_CasaE_rodape_Terreo.png` e `..._rodape_1Pavimento.png`.
  - **PDFs (2 páginas A3 cada: Térreo e 1º Pavimento):** `entrega/POE642_CasaE_Plantas_Humanizadas_opcao_PB.pdf` (18,1 MB) e `entrega/POE642_CasaE_Plantas_Humanizadas_opcao_Linhas.pdf` (16,2 MB). O PDF anterior, só do Térreo (`POE642_CasaE_Plantas_Humanizadas.pdf`), saiu da pasta: as duas opções o substituem (está no histórico do git).
  - **Faixa abaixo da suíte 3 (usuário, 16/10/26: "corrija esse defeito. deveria ser linhas apenas"):** abaixo da parede de baixo da suíte 3, uma faixa branca da base, fechada pela linha fina do PDF, caía dentro da pegada, e lá aparecia uma barra cinza do render. Ela entrou numa segunda área `FORA` do `opcoes_1pav_casae.py` (822, 800, 912, 816 em px de 2000), que começa abaixo da parede para não pegar a escrivaninha. Agora a faixa mostra o entorno: as linhas do Térreo na opção linhas, o Térreo esmaecido na P&B. Só essa faixa mudou (cerca de 3.300 px). As duas montagens, as duas pranchas do 1º Pavimento e os dois PDFs foram refeitos.
  - **Opção nublado (usuário, 19/10/26, com uma planta humanizada de referência: "referência com o piso inferior mais 'nublado'. Usaremos para as plantas dos 1º pavimentos das casas"):**
    - A referência está em `_texturas/originais/referencia_1pav_nublado.png`. Nela, o Térreo fica sob um véu branco, em tons pastel (gramado RGB 205, 209, 195; palmeira 195, 203, 181), sem virar cinza.
    - **Calibragem:** `entorno_esmaecido.NUBLADO` = 70% de branco, 80% da saturação e um desfoque de 1,2 px a 3840 px.
      - Medida no gramado do Térreo aprovado da Casa E, RGB (85, 107, 43): a luminância vai de 78 a 203, e o G − B de 64 a 14.
      - Na montagem, o gramado saiu em (203, 209, 193).
      - O 1º Pavimento continua por cima, integralmente e nítido, como nas outras opções.
    - **Arquivos:**
      - `opcoes_1pav_casae.py` ganhou a opção `nublado` (`--opcao` escolhe quais rodar). A P&B e a de linhas foram rodadas de novo e saíram iguais, byte a byte.
      - Saídas: `renders/POE642_CasaE_PH_1Pavimento_v1_final_nublado.png` (e `_preview.jpg`), a prancha `entrega/POE642_CasaE_PH_1Pavimento_entrega_nublado.png` e o PDF `entrega/POE642_CasaE_Plantas_Humanizadas_opcao_Nublado.pdf` (3 páginas A3, 21,9 MB).
    - **Para os próximos 1º Pavimentos:** `entorno_esmaecido.py --nublado`.
  - **Depois da escolha do cliente:** rodar o `rodape_entrega.py` da opção escolhida sem `--sufixo` (gera `..._PH_1Pavimento_entrega.png`) e o `pdf_entrega.py` sem `--prancha`/`--nome` (gera `POE642_CasaE_Plantas_Humanizadas.pdf`). Comandos no README dos scripts, em "Pranchas de entrega".

## Casa E · Subsolo

- **PDF:** `_pdfs_cliente/642 - SUBSOLO - CASA E.pdf` (recebido em 16/10/26; mesma folha 3370 × 2384 pt e mesmo enquadramento: o elevador cai a 2 pt do elevador do Térreo). Pavimento `Subsolo` na `POE642_CasaE/config_bases.json` (curvas de nível ocultas).
- **Ambientes (textos do PDF):**
  - academia (85,5 m²), no centro;
  - piscina (14,76 m²) à esquerda, em dois tanques: um comprido junto à academia, com um vidro entre os dois, e um embaixo, dividido em dois por um vidro;
  - sauna (4,62 m², banco em dois níveis), uma antessala com ducha e o vestiário (6 m², com bancada e cuba, vaso e chuveiro);
  - circulação (38,37 m²) na faixa de cima, com a escada (18 degraus, sobe);
  - depósito (12,65 m², porta dupla);
  - DCE (8,4 m², cama e armário) e WC DCE 2 (3,36 m², com chuveiro);
  - duas casas de máquinas (5,83 m² à direita, 15,07 m² embaixo);
  - elevador.
  - A faixa da circulação não tem parede no alto, à esquerda da escada (só a borda do piso).
- **Cores do PDF:**
  - laranja #CC9966 em réguas: a academia;
  - oliva #BAB596: sauna, antessala, ducha e vestiário;
  - rosa #BFA79F: DCE e a casa de máquinas de baixo;
  - cinza #E0E0E0: circulação, depósito, casa de máquinas da direita e WC DCE 2;
  - azul #7FDFFF: a piscina;
  - escada em #DDDACB;
  - em branco: banco da sauna, armário do DCE, elevador.
- **Base v1** (cores do PDF): `bases/POE642_CasaE_BASE_Subsolo_v1(_16x9)` e a prévia `_16x9_preview.jpg`.
- **Respostas do usuário (16/10/26):**
  - "não tem parede": a circulação fica aberta no alto, à esquerda da escada, só com a borda do piso.
  - "parte da piscina e ofurô": o tanque comprido e o de baixo à esquerda são a piscina; o tanque pequeno de baixo à direita, junto à sauna, é o ofurô.
  - Os materiais propostos, no código de cores do Térreo e do 1º Pavimento, ficaram como estavam.
- **Materiais:**
  - vinílico #A8784F, o do 1º Pavimento, no laranja da academia; as réguas do PDF ficam, como no 1º Pavimento;
  - travertino #DCD9CA no oliva (sauna, antessala com ducha, vestiário) e na escada;
  - granito Marrom Tabaco #5A4232 no rosa (DCE e casa de máquinas de baixo);
  - Bege Bahia #E8E8E8 no cinza (circulação, depósito, casa de máquinas da direita, WC DCE 2);
  - piscina e ofurô em #DFF6FE, como a piscina do Térreo;
  - banco da sauna em dois tons de Bege Bahia mais escuros (#DCDCDC no degrau, #D0D0D0 no assento), como na Casa D;
  - armário do DCE em marcenaria areia #CBB89E; elevador branco.
- **Base v2** (legenda): `bases/POE642_CasaE_BASE_Subsolo_v2(_16x9)` e a prévia.
  - Como no Térreo, as bordas brancas da piscina e do ofurô (ARQ_PAREDE de 8 pt) entram em `zonas_excluidas` e não viram vidro.
  - O visor de vidro entre a piscina e a academia, que continua até o ofurô, fica como vidro fino.
- **Base v3 (texturas):** `bases/POE642_CasaE_BASE_Subsolo_v3_texturas(_16x9)` e a prévia.
  - As mesmas fontes do Térreo e do 1º Pavimento da Casa E: vinílico das suítes do 1º Pavimento da Casa A, travertino do hall do Subsolo da Casa A, granito da cozinha do Térreo da Casa A, Bege Bahia das varandas da Casa A, água da piscina do Térreo da Casa A e marcenaria areia do Térreo retocado da Casa D.
  - O banco da sauna leva o Bege Bahia escurecido (0,93 e 0,88), preso ao retângulo do banco, como na Casa D.
- **Prompt v1:** `POE642_CasaE_PH_Subsolo_v1.md` (entrada: `bases/POE642_CasaE_BASE_Subsolo_v3_texturas_16x9.png`).
  - A planta ocupa de ~22% a ~54% da largura e de ~14% a ~51% da altura; as linhas tracejadas do lote ficam a ~7% e ~92,5% da largura e a ~95% da altura.
  - Ambientes descritos por posição.
  - Pontos que o prompt reforça:
    - a circulação sem parede no alto, à esquerda da escada;
    - a piscina (tanque comprido e o de baixo à esquerda) e o ofurô (o pequeno junto à sauna), com bordas brancas e o visor de vidro fino para a academia, sem escadas nem degraus na água;
    - a antessala da sauna aberta para a academia;
    - os três chuveiros (WC DCE 2, ducha da antessala, box do vestiário) num braço que sai da parede desenhada;
    - o armário do DCE até o teto;
    - o elevador ocupando quase toda a caixa;
    - nenhuma vegetação.
- **Render v1:** `renders/POE642_CasaE_PH_Subsolo_v1_render.webp` (2000 × 1116; base v3 + prompt v1, fundo branco).
  - Está na escala da base: SIFT + afim com 38 pontos, escala 0,9996 × 1,0066.
  - O que diverge da base e do PDF está marcado em `renders/POE642_CasaE_PH_Subsolo_v1_erros.jpg` (15 itens).
- **Retoque** (`POE642_CasaA/scripts/retoque_subsolo_casae.py`, sem IA, um item por vez; saída `renders/POE642_CasaE_PH_Subsolo_v1_retocado.png`, `_camada.png` e `_previa.jpg`):
  1. **Circulação e depósito:** o motor fez a faixa da esquerda da circulação em travertino, com uma junta, e pôs uma parede preta na borda da esquerda (o PDF não tem; usuário: "não tem parede"). O resto saiu num Bege Bahia com veios em nuvem e sombras longas das paredes.
     - O piso da circulação e do depósito (o Bege Bahia da base chapada) vira a textura aprovada da base v3, alinhada ao render e na cor do Bege Bahia do próprio render.
     - Na borda da esquerda fica só a linha fina do contorno, como a de cima.
     - A porta dupla do depósito é redesenhada pelo PDF (folhas e arcos finos), com o vão em piso contínuo.
  2. **Escada:** o motor desenhou linhas pretas fortes, seta nas duas pontas, a marca de corte e uma cunha de sombra.
     - É a mesma escada externa do Térreo, no mesmo lugar da folha, já aprovada lá (item 21 do Térreo: sem linhas, sombreamento de descida da direita para a esquerda).
     - O trecho dela vem do Térreo retocado, levado a este render pelas duas bases (128 pontos; cai em x 599,4 a 759,0 e y 210,7 a 247,8, os degraus do PDF).
     - A sombra curta do primeiro espelho cai na circulação, à esquerda. Sai também a linha que o render fazia em volta da escada.
  3. **WC DCE 2:** o motor fez o piso em granito (é Bege Bahia), uma bancada comprida que ocupava também o lugar da bacia, pôs a bacia no lugar do chuveiro e não desenhou o chuveiro. O ambiente é refeito pelo PDF:
     - piso inteiro no Bege Bahia aprovado; o que o render deixava sobre as paredes em volta volta ao preto;
     - porta (folha e arco finos) vinda do DCE;
     - bancada em quartzo claro #ECE8E1 com a cuba retangular branca (aba, bacia da borda ao fundo, válvula) e a torneira cromada saindo da parede da direita;
     - bacia no contorno do PDF, na parede da direita, com volume, contorno fino, sombra curta e o tampo fechado;
     - divisória de vidro do box, fina;
     - chuveiro: ducha quadrada, braço cromado até a parede da direita e canopla.
  4. **Casa de máquinas da direita:** o motor fez o piso em granito; é Bege Bahia (o cinza do PDF, como o depósito). O ambiente vira o Bege Bahia aprovado, com o vão da porta, e a porta vinda do depósito é a do PDF.
  5. **Elevador:** o motor fez a caixa com piso de mármore e um quadrado claro, sem cabine. É o mesmo elevador do Térreo, no mesmo lugar da folha e com a porta para o mesmo lado (para baixo). O miolo da caixa e o vão da porta, até a face de fora da parede, vêm do Térreo aprovado: cabine em inox com a moldura branca e a soleira.
  6. **Suporte de halteres:** o motor pôs um armário alto de madeira no lugar do suporte do PDF (dois andares de halteres sextavados, dez pares, com o quadro e os pés).
     - O armário e a sombra dele saem: entra o vinílico das mesmas linhas, logo à esquerda (as réguas são horizontais e continuam).
     - Entra o suporte desenhado pelas peças do PDF (ARQ_ MOB COMUM): quadro, trilhos e pés em grafite, cabeças em borracha preta, pegadores cromados e a sombra curta.
  7. **Elípticos:** os dois aparelhos pequenos do PDF são elípticos vistos de cima (trilhos, pedais, braços e console); o motor desenhou dois halteres grandes.
     - Os halteres e as sombras saem. Cada linha recebe o vinílico da mesma linha, deslocado até um trecho limpo (`vinilico`: as réguas do render não coincidem com as da base), com a luz acertada pelo vinílico em volta.
     - Entram os elípticos pelo PDF (ARQ_ MOB COMUM): silhueta em grafite, os traços do desenho em preto e a sombra curta.
  8. **Piscina e ofurô:** o motor fez degraus e bancos dentro dos tanques (o PDF não tem), a água num turquesa forte e, embaixo, a borda da piscina diferente do PDF; o vidro entre a piscina de baixo e o ofurô virou parede branca.
     - A água dos três tanques, tirada da base chapada (sem as bordas brancas), vira a água aprovada nas piscinas: Barlavento (`piscinas_barlavento`), com a pedra das peças sob a água verde-azulada clara, a grade ondulada, o brilho na diagonal e a sombra curta junto às bordas. Fica sem degraus e sem as cáusticas do render, que eram os degraus.
     - O visor de vidro entre os tanques e a academia volta inteiro, como na base: vidro fino com os caixilhos.
  9. **Sauna:** o motor fez um banco em L de ripas de madeira, subindo pela parede da esquerda. O banco do PDF tem dois níveis, só ao longo da parede de baixo (ARQ_ELEMENTOS FIXOS).
     - A sauna vem da base (`pela_base`): o travertino do piso, no tom do travertino do render (ganho por canal) e sem os contornos da base.
     - O banco é de travertino. Usuário (16/10/26): "os bancos da sauna devem ficar em mármore travertino também, com a devida separação com a linha em sombreamento discreto para dar a entender que o de baixo está mais alto que o de cima, que por sua vez está mais alto do que o piso". Recebe o travertino do piso da sauna, espelhado. A primeira versão, nos dois tons de Bege Bahia da Casa D, saiu.
     - Os níveis se separam por uma linha fina (cinza, força 0,22) com uma sombra discreta no lado mais baixo de cada borda (até 14%, em 1,8 pt) e um brilho leve na quina de cima. O assento junto à parede é o mais alto, o degrau da frente fica no meio e o piso é o mais baixo.
  10. **Antessala:** o motor pôs uma bacia sanitária entre a ducha e o vestiário (o PDF não tem), além de sombras longas e arcos tracejados.
     - A antessala e a ducha vêm da base (o travertino), no tom do render; o vinílico da academia, logo acima da abertura, fica.
     - As portas da sauna e da ducha são as do PDF, com folha e arco finos. O chuveiro da ducha entra no item 11.
  11. **Chuveiros:** os da ducha da antessala e do box do vestiário saíram fora do padrão aprovado (um símbolo solto; um círculo com manchas).
     - O box é refeito pela base (travertino, sem as sombras longas), com a porta do PDF.
     - Os dois chuveiros entram como o do WC DCE 2: ducha quadrada, braço cromado até a parede desenhada (a de baixo, na ducha; a da direita, no box) e canopla.
  12. **Portas do vestiário:** o motor fez arcos tracejados e sombras longas. O vestiário é refeito pela base (travertino), com:
     - as portas do PDF: a do vestiário, vinda da antessala, e a do WC;
     - a bancada de quartzo com a cuba e a torneira da parede da direita;
     - a bacia na parede da esquerda, com o tampo fechado, como as outras peças desta planta.
     - As portas do DCE e da casa de máquinas de baixo, que estavam sem arco, entram com o granito, no item 13.
  13. **Granito:** o motor fez o DCE e a casa de máquinas de baixo num mármore marrom com veios claros; o aprovado é o granito Marrom Tabaco em grão, o do Térreo.
     - O piso vira o granito da base (a fonte aprovada na Casa A), no tom do granito do Térreo retocado (mediana BGR 52, 59, 83).
     - No DCE ficam a cama, o criado-mudo e o armário do render (o que é claro e grande), com a sombra curta.
     - As portas do DCE e da casa de máquinas entram pelo PDF, com o arco cinza fino aprovado no granito.
  14. **Sombras longas no vinílico da academia:** as das paredes, sob a parede de cima, sob a parede do DCE e à direita do vestiário, eram faixas de sombra dura, uniformes ao longo da parede.
     - Cada linha (ou coluna) do vinílico ganha a razão entre a luz do vinílico logo depois da faixa (o quartil de cima) e a dela. A conta é local ao longo da parede, em janelas de 31 px, porque a faixa muda de largura.
     - As peças (cinza, preto, branco e o móvel baixo junto ao DCE) não mudam, e as sombras curtas das peças do render ficam.
     - Duas tentativas descartadas: um ganho por campo de luz, que deixou halos e manchas laranja no grão do vinílico, e a troca automática das manchas, que apagou partes da estação de musculação.
  15. **Imagem final no quadro comum** (3840 × 2160, a mesma folha do Térreo e do 1º Pavimento): o motor tinha deslocado um trecho da linha tracejada do lote, à direita.
     - A planta retocada vai ao quadro comum (64 pontos, erro mediano 0,66 px) e entra inteira na pegada da base (`entorno_esmaecido.sobrepor`).
     - Fora dela, o fundo é branco e as linhas tracejadas do lote são as da base, nas posições exatas do PDF.
     - Saída `renders/POE642_CasaE_PH_Subsolo_v1_final.png` e `_final_preview.jpg`.
  16. **Bordas da piscina e vidros (usuário, 16/10/26):** "as bordas da piscina são em mármore bege bahia. a folha de vidro entre a academia e a piscina e a folha de vidro entre a piscina e a sauna também são finas e elegantes". O usuário confirmou depois que o segundo vidro é o que fica entre o ofurô e a piscina. O render deixava as bordas brancas.
     - O branco junto à água (lum > 212, pouca saturação, até 17 px dela), dentro do contorno de fora das bordas no PDF (694,2, 679,3 a 888,9, 1130,0 pt), e a faixa do visor viram o Bege Bahia tecido da circulação, no tom dela. O pilar entre os dois trechos do visor fica preto.
     - Os dois trechos de vidro do visor (812,2 a 815,0 pt de largura) entram como uma folha fina, em vidro claro com contorno fino: o de cima, entre a academia e a piscina; o de baixo, depois do pilar, entre a piscina e o ofurô.
  17. **Linhas do PDF no fundo branco (usuário, 16/10/26: "coloque as linhas do PDF no fundo branco"):** o PDF do Subsolo não tem nada fora da planta além do tracejado do lote. Por isso, fora da pegada entram as linhas do PDF do Térreo (a casa de cima), em cinza, como na opção "linhas" do 1º Pavimento.
     - Usa `opcoes_1pav_casae.contexto_linhas`: sem terreno, contrapiso, zonas e textos, com 70% do traço.
     - As linhas caem no lugar: a escada e o elevador do Térreo coincidem com os do Subsolo.
     - O tracejado do lote continua o da base, e a planta retocada entra inteira na pegada.
  18. **Nomes e áreas (usuário, 16/10/26: "vamos adicionar os nomes e áreas, conforme regras que adotamos anteriormente para o 1º pavimento da casa E"):** a regra do 1º Pavimento, escrita na imagem final (3840 px), depois das linhas do fundo; o retocado de 2000 px fica sem rótulos.
     - Os 11 rótulos do PDF: circulação, depósito, DCE, WC DCE 2, as duas casas de máquinas, elevador, academia, piscina, sauna e vestiário. Cada linha entra igual ao PDF ("ACADEMIA" / "A: 85,5 m²"), na posição do PDF, no corpo do PDF 30% maior, em Inter Regular preta. O título da folha ("-1. 1º SUBSOLO") não entra.
     - No granito Marrom Tabaco (DCE e casa de máquinas de baixo) o texto fica cinza (150).
     - Dois ambientes estreitos ficam no corpo do PDF (1,0×), porque o 1,3× não cabe no piso livre. Na casa de máquinas da direita, "CASA DE MÁQUINAS" encostava nas duas paredes. No WC DCE 2, o "m²" caía sobre o chuveiro, e o rótulo foi também 6 px para a esquerda, para o piso livre do box.
     - `retoque_1pav_casae.rotulos_ambientes` ganhou `ajustes=` (os desvios de outro pavimento, cada um com o corpo opcional). As duas montagens do 1º Pavimento saem idênticas às anteriores.
  19. **Piscina, ofurô e sauna (pedido do cliente, trazido pelo usuário em 19/10/26, com a planta marcada e uma vista 3D da fachada da academia):**
      - Pedido: "remova as bordas onde está apontado. Note que entre a sauna e o furô temos um vidro, sem base. Já a piscina, fica sem divisória. Esses comandos vieram do cliente, contrariando o PDF original. Por isso, vamos adotar conforme nos solicitaram".
      - Na marcação: "A representação da esquadria precisa ser mais evidente, e não terá parede abaixo dela".
      - Item `piscina_cliente` do `retoque_subsolo_casae.py`, depois do 16:
        - **Piscina sem divisória:** sai a faixa de Bege Bahia entre a piscina e a parte de baixo (o X da marcação). A piscina vira uma água só.
        - **Vidro sem base no visor:** no trecho de baixo (entre a piscina e o ofurô), a faixa de Bege Bahia em volta da folha vira água, dos dois lados.
        - **Vidro sem base entre o ofurô e a sauna:** a faixa de Bege Bahia sai, e a água do ofurô vai até um vidro na face da sauna.
        - **Esquadrias mais evidentes, como na vista 3D:** folha de vidro clara, perfis em grafite dos dois lados e montantes a cada ~1,1 m. Isso vale no visor inteiro (fachada da academia e trecho de baixo) e no vidro da sauna.
        - **Água:** é a mesma do item 8 (a mesma pedra Barlavento na mesma janela), com a luz de borda refeita para o contorno novo.
        - **Fica como estava:** a borda de Bege Bahia no alto do ofurô, junto à parede.
      - **Alinhamento estável:** o alinhamento da imagem final passa a ser medido no retocado dos itens 1 a 16 (`no_quadro_comum(..., referencia=)`). Sem isso, o retoque novo mudava o afim em fração de pixel e a imagem inteira se mexia. Agora só a região do item muda.
  20. **Rótulo "AMBIENTE" (usuário, 19/10/26: "Adicione o rótulo 'Ambiente', entre a sauna e vestuário"):** a antessala entre a sauna e o vestiário não tem rótulo no PDF.
      - Entra pela lista `ROTULOS["extras"]`: na linha dos nomes da sauna e do vestiário, no piso livre à direita da porta da sauna, no corpo e na regra dos outros.
      - Fica sem área, porque o PDF não a dá e o ambiente é aberto para a academia.
      - **Conferência:** na prancha, só a piscina e o rótulo mudaram (15.203 px, 2 regiões). A prancha do Subsolo e os três PDFs da casa foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_piscina_cliente_antes_depois.jpg`.
  21. **R2, só o Subsolo com o terreno hachurado (regra nova de 19/10/26 para todas as casas: "Quando representar a planta de subsolo, mostrar somente o subsolo com o restante do terreno hachurado"):** substitui o item 17 (as linhas do PDF do Térreo no fundo).
      - Fora da pegada do Subsolo, o terreno do lote fica hachurado em diagonais finas a 45° (/), em cinza-claro (198), a cada 0,40 m (24 px na prancha), com traço de 1,3 px. A hachura foi escolhida pelo usuário.
      - O lote é o do Térreo aprovado, no mesmo quadro: tudo o que não é branco nele, fechado e com os furos preenchidos. Ele leva um contorno cinza fino (165).
      - Fora do lote fica o branco, com as linhas tracejadas da base (as do PDF).
      - `HACHURA`, `lote_do_terreo` e `contexto_hachura` no `retoque_subsolo_casae.py`.
      - Na prancha, só o fundo mudou (a planta do Subsolo e o rodapé ficaram iguais). A prancha e os três PDFs foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_terreno_hachurado_antes_depois.jpg`.
  22. **R3, portas sem arcos (regra de 19/10/26: "Não mostrar arco da porta"):** os 11 arcos de porta do PDF saíram; as folhas e os batentes ficam.
      - Os arcos estão em três camadas: ARQ_PAREDE (as portas), "ARQ - Parede" (as duas portas de dentro do vestiário) e ARQ_REVESTIMENTOS (a porta de vidro da ducha da antessala).
      - A remoção virou um módulo comum, `scripts/arcos.py` (`remover_arcos`). O `ajustes_casaa.sem_arcos` da Casa A agora o usa, e o resultado lá ficou igual, px a px.
      - Opção nova `so_folha=True`: a reta do centro a uma ponta do arco só é protegida se lá houver mesmo uma folha. Na porta dupla do depósito, a ponta do arco fechado sobrava como um tracinho no meio do vão.
      - **Conferência:** na prancha, só as 9 regiões das portas mudaram (6.880 px). A prancha e os três PDFs foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_sem_arcos_antes_depois.jpg`.
  23. **Escada com linhas e o triângulo de orientação (regras de 19/10/26: "escadas com linhas" e R14):** a escada sobe para a direita, com 17 degraus de 30 cm. A linha de corte do PDF passa em diagonal pelos degraus 7 e 8. Item `escada_r14`, que substitui o sombreado do item 2.
      - O piso é o travertino da base v3, sem os traços do PDF (removidos por inpaint), na cor do render.
      - **Antes do corte:** em cada bocel, uma linha cinza suave (80%) e a sombra curta de 10 cm no degrau de baixo. Nenhum traço preto.
      - **Depois do corte:** esmaecida (80%), com os bocéis e o contorno tracejados do PDF. Ficam de fora a linha de percurso, a linha de corte e o símbolo dela, como nas escadas aprovadas.
      - **Triângulo:** cheio, cinza-escuro, de 24 × 26 cm, no 1º degrau, a 10 cm do início, apontando para a subida.
      - **Conferência:** na prancha, só a escada mudou (22.994 px, 1 região). A prancha e os três PDFs foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_escada_antes_depois.jpg`.
  24. **Rótulos no granito em branco (R6, 19/10/26: "Apresentar os rótulos em branco quando for piso marrom granito"):** no DCE e na casa de máquinas de baixo, o texto passou do cinza (150) ao branco (250).
      - `retoque_1pav_casae.rotulos_ambientes` ganhou `cor_granito=` (e `ROTULOS["branco"]`), para cada pavimento passar ao branco quando for refeito. O padrão continua o cinza, para nenhuma outra prancha mudar sem pedido.
      - **R7 (nenhum rótulo sobre objeto):** conferido nos 12 rótulos; todos estão no piso livre. Na piscina e no elevador, o rótulo fica sobre o próprio ambiente.
      - **Conferência:** na prancha, só os dois rótulos mudaram (1.188 px). A prancha e os três PDFs foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_rotulos_granito_antes_depois.jpg`.
  25. **Texturas na escala (R1, 19/10/26: "textura, imprescindível que seja representada na escala"):** medidas no render, que tem 31,1 px/m.
      - **Já estavam na escala e ficaram:** o vinílico da academia (réguas de 20 a 25 cm) e o granito (grão fino).
      - **Mudaram:**
        - Bege Bahia (circulação, depósito, casa de máquinas da direita, WC DCE 2): estava em manchas de 0,5 a 1 m, com riscos claros do motor;
        - travertino (sauna, antessala, vestiário): tinha estrias verticais que liam como madeira.
        - Os dois passam ao desenho da biblioteca (`_texturas`), na escala do render, com a luz e a cor do lugar e força 0,6. A escada do item 23 fica.
      - **Módulo novo, comum às casas:** `scripts/texturas_escala.py` (`retexturizar`).
        - A luz do lugar é a média local do piso, num raio de ~25 cm, sem o que é mais escuro que ela (traços, folhas, objetos). Os riscos claros do motor viram piso.
        - O desenho é o detalhe da textura da biblioteca abaixo de ~25 cm.
      - **Conferência:** na prancha, só os pisos de Bege Bahia e travertino mudaram (nada fora da planta). A prancha e os três PDFs foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_texturas_escala_antes_depois.jpg`.
  26. **Soleiras conferidas com o PDF (R13, 19/10/26: "atenção às soleiras, representar onde tem e evitar adicionar onde não tem"):** no PDF, a soleira é o vão da porta na espessura da parede deixado em branco, entre os batentes. Onde o piso de um dos lados atravessa o vão, não há soleira.
      - **Com soleira no PDF:**
        - o DCE e o WC DCE 2 já tinham soleira na imagem;
        - no depósito (porta dupla), o Bege Bahia passava direto: a soleira entrou;
        - na casa de máquinas de baixo, o motor tinha deixado o vinílico e dois triângulos cinza no vão: a soleira entrou.
      - **Sem soleira no PDF:** a casa de máquinas da direita, a sauna, o vestiário e as portas de dentro do vestiário e da ducha. Nenhuma tinha soleira na imagem, e assim ficam.
      - **Como é a soleira:** Bege Bahia na escala (a textura da biblioteca na cor do Bege Bahia do render, força 0,5), com as duas faces da parede em traço cinza fino, como no PDF. Item `soleiras` (`SOLEIRAS`).
      - **Conferência:** na prancha, só os dois vãos mudaram. A prancha e os três PDFs foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_soleiras_antes_depois.jpg`.
  - **Subsolo da Casa E fechado pelas regras de 19/10:** R2, R3, escadas com linhas e R14, R6/R7, R1 e R13. Os pedidos do cliente (piscina, vidros, rótulo AMBIENTE) também foram feitos.
  27. **Ajustes do usuário (20/10/26), revisando o Subsolo fechado:**
      - **Ofurô** ("REMOVA ESSA BORDA EM PEDRA NA PARTE DE CIMA E O VIDRO DA SAUNA À DIREITA"): saem a borda de Bege Bahia no alto do ofurô e o vidro que eu tinha posto na face da sauna (item 19). A água vai até a parede de cima e até a borda da sauna. Fica só o vidro do visor, entre a piscina e o ofurô.
      - **Travertino** ("PISO EM TRAVERTINO", com o recorte da sauna, da antessala e do vestiário): a foto da biblioteca, reduzida à escala do render, fica quase lisa (os veios somem), e o piso lia como Bege Bahia.
        - Passa a ser o travertino aprovado do Térreo da mesma casa, na mesma escala: trechos limpos da sala, tecidos por image quilting, com os veios na vertical, o desenho inteiro (força 1,4) sobre a luz do lugar.
        - `texturas_escala.retexturizar` ganhou `pronta=` (uma textura já na escala, de outro pavimento).
      - **Escada** ("TÁ INVERTIDA. O TRIANGULO É DA DIREITA PARA ESQUERDA. SUBINDO DA DIREITA PARA ESQUERDA, COM A PARTE DA DIREITA VIVA, E A PARTE DA ESCADA À ESQUERDA ESMAECIDA [...] COM TRACEJADO À ESQUERDA, NÃO À DIREITA"): a escada sobe da direita para a esquerda.
        - Viva à direita do corte do PDF, com a sombra curta à direita de cada bocel (o degrau de baixo).
        - Esmaecida à esquerda, com os bocéis e o contorno tracejados no tracejado do PDF (5,7 pt de traço, 2,8 de vão).
        - O triângulo fica no 1º degrau da direita, apontando para a esquerda.
        - **Atenção:** o PDF traz o "S" e o tracejado do outro lado. Vale o que o usuário definiu.
      - **Bege Bahia** ("A REPRESENTAÇÃO DO MARMORE BEGE BAHIA CONFORME A REFERENCIA DEFINIDA ESTÁ ADEQUADA?"): comparado com a foto de referência na mesma escala, não estava.
        - O desenho tinha ~40% do contraste da foto (desvio 0,014 contra 0,037) e o tom estava acinzentado: RGB (222, 207, 190) contra (231, 211, 187).
        - Agora o desenho entra inteiro (força 1, suavização 0,4 px) e o tom vai ao da foto: desvio 0,030; RGB (228, 209, 184). A luz do lugar fica.
        - Comparação em `renders/POE642_CasaE_PH_Subsolo_bege_bahia_vs_referencia.jpg`.
        - **Regra para as outras casas:** o Bege Bahia segue a foto de referência (desenho em nuvens visível, tom quente). Isso substitui o "quase liso, sem manchas" antigo.
      - Na prancha, só mudaram a planta do Subsolo (os pisos, a escada e o ofurô); nada fora dela. A prancha e os três PDFs foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_ajustes_20out_antes_depois.jpg`.
  28. **Visor em folha contínua (usuário, 20/10/26: "ESSE VIDRO É UMA FOLHA CONTINUA. TALVEZ ESSES PONTOS PRETOS PODEM DAR A IMPRESSÃO DE QUE SÃO VÁRIAS FOLHAS"):** saem os montantes do visor (`PISCINA_CLIENTE["montantes"] = False`). Fica a folha de vidro com os perfis em grafite dos dois lados.
      - Na prancha, só os 7 pontos mudaram. A prancha e os três PDFs foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_visor_folha_continua_antes_depois.jpg`.
      - **Regra:** vidro em folha contínua no PDF é desenhado sem montantes.
- **Entrega (16/10/26, depois da aprovação do usuário: "prancha e o PDF. aprovado."):** a casa passa a ter três pavimentos, na ordem da Casa A (Subsolo, Térreo, 1º Pavimento).
  - **Config:** o Subsolo entrou na chave `entrega` da `POE642_CasaE/config_bases.json` (título "SUBSOLO", linha 0 do quadro de áreas, base `POE642_CasaE_BASE_Subsolo_v3_texturas_16x9.png`). O Térreo passou à linha 1 e o 1º Pavimento à linha 2. O quadro de áreas tem os três "NÃO INFORMADO", sem total. Em `pdf.ordem`: Subsolo, Térreo e 1º Pavimento; título "Casa E – Plantas Humanizadas (Subsolo, Térreo e 1º Pavimento)".
  - **Pranchas (3840 × 2600 px):** `entrega/POE642_CasaE_PH_Subsolo_entrega.png`, nova. A imagem final, já no quadro comum e com os rótulos, entra com `--no-quadro`, sem realinhar. A do Térreo (realinhada com 128 pontos, erro mediano 0,78 px) e as duas do 1º Pavimento (`_pb` e `_linhas`) foram refeitas só pelo rodapé novo, com a linha do Subsolo no quadro de áreas. Rodapés `entrega/POE642_CasaE_rodape_{Subsolo,Terreo,1Pavimento}.png`.
  - **PDFs (3 páginas A3: Subsolo, Térreo e 1º Pavimento):** `entrega/POE642_CasaE_Plantas_Humanizadas_opcao_PB.pdf` (20,6 MB) e `..._opcao_Linhas.pdf` (18,6 MB). Só a página do 1º Pavimento muda entre as duas opções. Comandos no README dos scripts, em "Pranchas de entrega".
  - **Depois da escolha do cliente** (o 1º Pavimento continua em duas opções): como no 1º Pavimento, rodar o `rodape_entrega.py` da opção escolhida sem `--sufixo` e o `pdf_entrega.py` sem `--prancha`/`--nome`; sai `POE642_CasaE_Plantas_Humanizadas.pdf` com os três pavimentos.

## Casa A · nomes e áreas dos ambientes

Pedido do usuário (18/10/26): "vamos fazer os ajustes nas plantas da casa A", os mesmos da Casa E, ou seja, os nomes e as áreas dos ambientes em cada pavimento, depois as pranchas e o PDF.

- **PDFs:** os da Casa A não estavam no repositório. Vieram do Drive do usuário, da pasta onde estão os que geraram as bases ("642- SUBSOLO CASA A.pdf", "642- TÉRREO CASA A.pdf" e "642- 1° PAVIMENTO CASA A (1).pdf"). Foram salvos em `_pdfs_cliente/642 - <PAVIMENTO> - CASA A.pdf`, fora do git, como os das outras casas.
- **Script:** `POE642_CasaA/scripts/rotulos_casaa.py <Pavimento>`. Usa a regra da Casa E (`retoque_1pav_casae.rotulos_ambientes`): cada linha do rótulo do PDF igual, na posição do PDF, no corpo do PDF 30% maior, em Inter Regular preta; no granito marrom, cinza (150); sobre móvel ou peça, o piso livre mais próximo.
  - Ficam fora as notas que não são ambientes (projeções, shafts, floreira, afastamentos, divisa, muros, limite do lote, acessos) e o título da folha.
  - As imagens aprovadas da Casa A têm 2000 px, e nelas o rótulo ficaria com ~6 px de corpo, ilegível. A imagem vai ao quadro comum em 3840 px (ampliada com Lanczos, como nas pranchas), e os rótulos são escritos nessa resolução.
  - O granito é achado na própria imagem (luminância desfocada abaixo de 95, tom quente), porque a base da Casa A não tem a cor da legenda.
- **Subsolo** (`renders/POE642_CasaA_PH_Subsolo_final_rotulos.png`, 3840 × 2160): 9 rótulos (hall, academia, depósito, circulação, banho de serviço, sauna, banho feminino, banho masculino e elevador).
  - Banho de serviço: no PDF o rótulo passava da parede da direita e encostava no vaso. Foi para o piso livre de cima do banho, no 1,3×.
  - Banho masculino: 4 px à esquerda, para não encostar no arco da porta.
- **Térreo** (`renders/POE642_CasaA_PH_Terreo_final_rotulos.png`, a partir da imagem com o Barlavento): 26 rótulos. No granito (cozinha, área gourmet, área de serviço, despensa, garagem e bloco do motorista) o texto fica cinza.
  - Garagem: os três carros ocupam a garagem, então o rótulo vai no corpo do PDF (1,0×), no vão entre o primeiro e o segundo carro.
  - Sala de estar: estava sobre a mesa de centro. Foi para baixo dela, no tapete, antes das poltronas.
  - Quarto do motorista: estava sobre a cama. Foi para o piso abaixo dela, em cinza. A caixa do texto pega parte da cama, então a cor vai dada no ajuste.
  - Banho do motorista, WC, banho da varanda e despensa: estreitos, no corpo do PDF (1,0×), no piso livre entre as peças. O banho da varanda cruza o arco da porta, uma linha fina, como o hall interno.
  - Varanda (encostava na poltrona: um pouco acima), lavabo (na bancada) e sala de jantar (no vidro): alguns px.
  - Jardim da escada (17,46 m²): fica na posição do PDF, sobre a faixa verde, em preto (o verde é claro e chapado, e o preto se lê).
- **1º Pavimento** (`renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png`): 22 rótulos (suítes, closets, banhos, sala íntima, circulação, quarto e banho de serviço, saleta, as quatro varandas e o elevador).
  - Suítes 3 e 2: estavam sobre a cama. Foram para o tapete, abaixo da cama (suíte 3) e acima dela (suíte 2).
  - Suíte master: estava sobre o pufe. Foi para o piso acima dele, fora do tapete.
  - Sala íntima: estava sobre a mesa de centro. Foi para o espaço entre ela e o sofá.
  - Banho de serviço: o "m²" caía no vaso. Foi para o piso livre de cima do banho.
  - Banho 1 (no vaso) e closet master (no armário): alguns px.
- **Entrega refeita:** as três pranchas agora usam as imagens com rótulos (`--no-quadro`) e passaram de 2000 para 3840 px de largura, como as das outras casas (`entrega.largura_prancha` = 3840 na config da Casa A). Os rodapés também saem em 3840 px, com o mesmo quadro de áreas. O PDF `entrega/POE642_CasaA_Plantas_Humanizadas.pdf` (3 páginas A3: Subsolo, Térreo e 1º Pavimento) tem 15,9 MB. O GIF `POE642_CasaA_pranchas_perfiladas.gif` não foi refeito.

## Texturas de referência · todas as casas

Pedido do usuário (19/10/26): "vamos inserir as referências de imagem das texturas (que devem simular pedra, não porcelanato) a serem utilizadas em todas as casas. lembrando da importância de aplicar a devida escala aos renders. 1- Bege bahia. 2- Travertino 3- Quartzito Aura 4- Pedra Portuguesa 5- Marrom granito (deixar mais liso e menos escuro)".

- **Pasta:** `projetos/_texturas/`, a mesma para as cinco casas.
  - `originais/`: as fotos como vieram.
  - `texturas.json`: cada material com a largura real que a imagem cobre (a escala) e o tratamento.
  - `texturas.py`: prepara tudo e faz a cartela.
- **Escala:** o PDF é 1:50 (1 pt = 17,64 mm; conferido pela área do lavabo da Casa A, 4,05 m²). A planta da Casa A em 2000 px tem 31,45 px/m; na prancha de 3840 px, 60 px/m.
- **Largura real de cada foto (estimada pelo que se vê; ajustar no `texturas.json` se o usuário passar a medida):**
  - Bege Bahia: 0,60 m (manchas de 10 a 20 cm);
  - travertino: 1,20 m;
  - quartzito Aura: 3,00 m (a chapa inteira, 3,00 x 1,95 m);
  - pedra portuguesa: 1,14 m;
  - granito: 0,60 m.
- **Tratamentos:**
  - pedra portuguesa: a foto é de uma calçada em perspectiva. Vira vista de cima por homografia: as bordas da grama e do meio-fio se encontram no ponto de fuga, e fica só a faixa do meio. Com a calçada de ~2 m, as pedras dão 6 a 8 cm;
  - granito: mais liso (ruído fino x 0,25, manchas x 0,6) e menos escuro (x 1,25).
- **Sem cara de porcelanato:** na escala da planta, a foto de 60 cm vira ~36 px, e o quilting direto só a repetia em espelho, como um piso impresso. De cada material sai primeiro uma amostra de 3 x 3 m tecida a 320 px/m, com retalhos de 10 cm (`amostras/`). É dela que a textura sai em qualquer escala (`textura(nome, px_por_m, alto, largo)`), tecida de novo, sem repetição visível.
- **Cartela:** `_texturas/cartela_texturas.jpg`, com a foto, a textura de uso, um trecho de 3 x 2 m na escala da prancha e o mesmo ampliado.
- **Madeira, vinílico, grama e vegetação externa (19/10/26).** Pedido do usuário: "para o madeira e o vinílico, use a imagem de referência. use também a vegetação externa como referencia dessa imagem também. Importante preservar a escala. Use a grama como referência também".
  - A referência é uma planta humanizada de outra casa (`_texturas/originais/referencia_planta.webp`).
  - **Escala medida nela mesma: 26 px/m.** A cama king (1,93 x 2,03 m) tem 50 x 53 px; o sedã (4,55 m), 118 px; a picape grande (6,0 m), 158 px; a porta (0,85 m), 22 px. É quase a escala dos renders (a Casa A em 2000 px tem 31,45 px/m).
  - As texturas saem de recortes limpos, sem móveis, sombra ou tapete. As caixas estão em `texturas.json`, e a cartela as marca na miniatura.
    - **madeira:** o deck da piscina, réguas de ~15 cm;
    - **vinílico:** o piso dos quartos (quatro trechos), réguas de ~20 cm, mais claras e de tons alternados;
    - **grama:** o gramado fora da sombra das árvores.
  - A amostra de cada uma é tecida na escala da própria referência (10 a 12 m de lado, retalhos de ~50 cm): a foto tem pouca resolução, e ampliá-la só borraria. Madeira e vinílico têm as réguas na vertical da imagem; para aplicar, girar conforme o ambiente.
  - **Vegetação:** `vegetacao()` recorta 9 plantas com fundo transparente, em `_texturas/vegetacao/` a 52 px/m:
    - 3 árvores de copa redonda (4,5, 4,5 e 3,4 m);
    - 3 arbustos redondos (~1,1 m);
    - 3 palmeiras baixas (1,2 a 1,6 m).
    - **Contorno:** sai da textura fina das folhas, de dentro para fora pelo raio, suavizado em volta, sem a grama na sombra e sem o piso.
    - **Para aplicar:** `pousar(fundo, nome, cx, cy, px_por_m)` põe a planta no render no tamanho real, com a sombra da referência (luz do alto à direita: a sombra cai para baixo e à esquerda).
  - A cartela ganhou as linhas 6 a 9; a 9 mostra as plantas sobre a grama, no tamanho real, na escala da prancha.

- **Guarda-roupas, escadas, box e portas (19/10/26).** Pedido do usuário, com duas plantas de um duplex: "referencia dos guarda-roupas e escadas, box e portas".
  - **Fonte:** as plantas estão em `_texturas/originais/referencia_elementos_{superior,inferior}.png`. A escala foi medida nas camas: 36 px/m.
  - **Código:** `_texturas/elementos.py` desenha cada elemento em metros, na escala de qualquer render (supersampling 4 x). Cada função devolve cor e alfa, na horizontal; para aplicar, girar e pousar.
  - **Cartela:** `_texturas/cartela_elementos.jpg` mostra a referência ao lado da nossa versão, na escala da prancha.
  - **guarda_roupa:** o armário visto de cima, aberto.
    - Moldura branca fina (portas e laterais) com contorno cinza.
    - Miolo cinza-claro, mais escuro junto às portas.
    - Cabides em traços cinza de través, a cada ~12 cm, com pequenas diferenças.
  - **escada:** degraus claros.
    - Em cada bocel, uma linha cinza suave e uma sombra de ~10 cm no degrau de baixo; nenhum traço preto.
    - Depois do corte, levemente esmaecida, com os bocéis pontilhados (a projeção) e o corrimão fino.
  - **box:** piso contínuo, o vidro em linha fina clara com sombra cinza ao lado, e o chuveiro de teto como disco cinza a ~35 cm da parede, com o braço curto até ela.
  - **porta_correr:** caixilho em faixa branca de 5 cm com contorno cinza, e as folhas em duas linhas sobrepostas. Os batentes (nas pontas e no encontro das folhas) são quadradinhos brancos de 8 cm.
  - **porta_giro:** folha branca fina aberta a 90°, sem arco. Decisão do usuário (19/10/26): "remover os arcos, escadas com linhas".
  - **Escadas com linhas (mesma decisão):** o bocel em linha cinza suave, como na referência.

## Casa A · conferência item a item com o PDF

Pedido do usuário (19/10/26): "vamos fazer a conferência de item a item do render da casa A, conforme fizemos com a casa E. Pegar o PDF da casa A e rever item a item com o render."

- **Como:** cada pavimento, PDF e imagem aprovada no quadro comum, comparados lado a lado em recortes com a mesma grade.
- **Script:** `POE642_CasaA/scripts/conferencia_casaa.py`. Os itens ficam em `ITENS`, com pontos em px de 2000 do quadro comum. Os mapas numerados, com a legenda, são `renders/POE642_CasaA_PH_{Terreo,1Pavimento,Subsolo}_conferencia.jpg`.
- **Térreo (12 itens):**
  1. Pilares da varanda e o pilar junto ao gourmet em marrom; no PDF são os pilares estruturais. No padrão da Casa E, pretos como as paredes.
  2. Sala de estar: faltam a poltrona da direita e os dois vasos de plantas junto ao sofá. O sofá curvo do PDF acompanha o tapete pela esquerda; o render o pôs ao longo do alto.
  3. Estar sob a projeção do pavimento superior: no PDF são 4 poltronas em X com a mesa triangular no centro; o render fez uma mesa retangular com 6 cadeiras.
  4. Sala de jantar: a mesa do PDF é oval; a do render é retangular chanfrada.
  5. Lavabo: faltam o vaso sanitário e o X tracejado da claraboia; no lugar, uma peça estranha com um arco.
  6. Escritório: no PDF a mesa tem uma cadeira em cima (de escritório) e duas embaixo; o render pôs duas em cima.
  7. Banho da varanda: uma bacia sanitária no lugar do chuveiro.
  8. Jardim (4,79 m²): sem as três touceiras do PDF.
  9. Área de serviço: a escada caracol saiu só como um traço fino sobre o granito.
  10. Área de serviço: a porta da direita, no alto, sem o arco.
  11. Quarto do motorista: a cama virou um bloco lilás.
  12. Banho do motorista: o chuveiro e a divisória do box viraram um bloco lilás.
- **1º Pavimento (7 itens):**
  1. Suíte 3: os criados-mudos do PDF são redondos; os do render, quadrados.
  2. a 5. Suítes 3, 2, master e 1: falta o banco ao pé da cama (na Casa E o usuário pediu esses bancos).
  6. Quarto de serviço: faltam a cama de solteiro e o criado-mudo.
  7. Banho master: a banheira do PDF é oval; a do render, retangular de cantos arredondados.
- **Subsolo (2 itens):**
  1. Banho de serviço: faltam o chuveiro e a divisória de vidro do box.
  2. Sauna: o banco do PDF, horizontal, ao longo da parede de baixo, virou piso na v6, por decisão anterior. Usuário (19/10/26): o banco não é em L; a faixa vertical à esquerda, no tom do piso da piscina, é a passagem da sauna para a piscina e fica como piso.
- **Conferidos sem divergência:** cozinha, garagem (carros), hall interno e externo, escada interna e jardim da escada, piscina, prainha, spa, deck e escada do deck, gourmet, lavatório e WC, garagem e acesso; no 1º Pavimento, banhos 1, 2 e 3, closets, circulação, sala íntima, saleta com a caracol e as varandas; no Subsolo, academia (2 esteiras, 2 bicicletas e o banco com a barra), depósito, circulação, hall, banhos feminino e masculino e elevador.
- **Próximo passo:** o usuário confirma a lista; o retoque segue um item por vez, sem IA, como na Casa E.
- **Ajustes (`POE642_CasaA/scripts/ajustes_casaa.py`, sem IA, um item por vez):** saem em `renders/<imagem aprovada>_ajustes.png` (+ `_camada.png`). O `rotulos_casaa.py` usa a imagem com ajustes, e dela saem as pranchas e o PDF.
  - **Subsolo 2, banco da sauna (usuário, 19/10/26: "Eu quero que você traga esse banco de volta"):** na v6 o banco virou piso; sobrou só uma faixa um pouco mais clara, sem a borda. O banco volta de parede a parede, ao longo da parede de baixo (x 625,0 a 717,5 px; borda em y 826,7 px na imagem de 2000 px, a linha do PDF levada pelo afim da base).
    - Marcado como o banco da sauna da Casa E: a linha fina da borda, a sombra discreta no piso (o lado mais baixo) e um brilho leve na quina. O tampo fica 3% mais claro.
    - Os números da Casa E quase não apareciam nesta imagem de 2000 px, ampliada para 3840 na prancha. Ficaram: linha 0,35 em 0,6 px e sombra 0,18 em 1,6 px.
    - A faixa vertical à esquerda (passagem para a piscina) continua como piso.
    - Saídas: `renders/POE642_CasaA_PH_Subsolo_final_ajustes.png`, o rótulo, a prancha do Subsolo (só a sauna mudou: cerca de 7 mil px) e o PDF de entrega refeitos. Antes e depois em `renders/POE642_CasaA_PH_Subsolo_sauna_antes_depois.jpg`.
  - **Subsolo 3, escada que desce do deck para a circulação (usuário, 19/10/26):** "tem uma linha diagonal discriminando até onde tem o esmaecimento [...] até o terceiro degrau de uma pessoa que está vindo de cima para baixo é esmaecido. Do terceiro degrau, depois dessa linha diagonal, já tem que ter a cor do subsolo, a cor do degrau, a cor da textura do degrau, de forma visível. [...] essa linha em diagonal não precisa estar desenhada".
    - A diagonal é a linha de corte da escada no PDF da Casa A (ARQ_ESCADAS E RAMPAS), de (479,9; 551,0) a (498,7; 588,6) no quadro comum. Antes dela, os degraus ficam esmaecidos, com o deck; a linha não é desenhada.
    - Depois dela, os degraus são refeitos nos espelhos do PDF (x 489,2 a 563,9; a v6 tinha um degrau a menos no fim). Textura: o travertino da circulação do Subsolo. Cor: o creme desta escada na legenda (#D8CDB4), no tom em que o travertino saiu na imagem.
    - Sem linhas e com o sombreamento de descida das Casas D e E: cada degrau 6% mais escuro de cima para baixo e a sombra curta de cada espelho no degrau de baixo, à direita (0,25 em 2,5 px). A circulação recebe a sombra do último espelho.
    - O `rotulos_casaa.py` passou a alinhar a imagem com ajustes pelo afim da imagem aprovada (`no_quadro_fixo`). O SIFT na imagem ajustada achava um afim um pouco diferente, e a prancha inteira mudava por reamostragem. Agora, contra a prancha de antes dos ajustes, só mudam a escada e a sauna.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_escada_antes_depois.jpg`; prancha do Subsolo e PDF de entrega refeitos.
  - **Subsolo 1, chuveiro do banho de serviço (usuário, 19/10/26: "siga com o chuveiro do banho de serviço"):** faltavam o chuveiro e o vidro do box.
    - No PDF da Casa A (ARQ_LOUÇAS E METAIS), o chuveiro sai da parede da esquerda (canopla, braço e ducha). O box é fechado por duas folhas de vidro de correr sobrepostas, da parede da esquerda até 982,3 pt; o resto, até a parede da direita, é a passagem.
    - Entram como os aprovados da Casa E (`chuveiro` e `vidro_box` do `retoque_subsolo_casae.py`): a ducha quadrada de 20 cm (11,2 pt), centrada na ducha do PDF, o braço cromado até a parede e a canopla; cada folha de vidro fina, com as bordas finas.
    - O rótulo "BANHO SERV.", que estava no piso de cima do banho, caía sobre o chuveiro. Foi para a direita da ducha, dentro do box, no corpo do PDF (1,0×); o resto do banho é vaso, bancada e o arco da porta.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_banho_servico_antes_depois.jpg`. Prancha do Subsolo e PDF de entrega refeitos; contra a prancha de antes dos ajustes, só mudam o banho de serviço, a escada e a sauna.
  - **Térreo 1, pilares (usuário, 19/10/26: "siga com os pilares do térreo"):** os três pilares redondos da varanda e o quadrado junto ao gourmet tinham saído em marrom. No PDF da Casa A são os pilares estruturais (camada EST - Pilar).
    - Ficam no preto das paredes (BGR 2, 2, 3, medido nas paredes do banho da varanda e do WC), como o pilar do Térreo da Casa E, na geometria do PDF: o contorno preenchido de cada pilar, levado à imagem pelo quadro comum e pelo afim do Térreo (SIFT, 45 pontos, 0,6 px), com a borda antisserrilhada. O círculo só traçado da mesma camada é o eixo da escada caracol e não entra.
    - O marrom do motor saiu ~1 px maior que o PDF (raio ~7,3 px contra 6,3 px). No anel de até 2,5 px fora do contorno, a parte marrom de cada pixel sai e fica o piso (ou a grama) do lugar; o veio do piso e a grama não são tocados.
    - Imagem com ajustes: `renders/POE642_CasaA_PH_Terreo_final_bege_barlavento_ajustes.png`. O `rotulos_casaa.py` passou a usá-la, alinhada pelo afim da imagem aprovada (como no Subsolo).
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_pilares_antes_depois.jpg`. Prancha do Térreo e PDF de entrega refeitos; contra a prancha anterior, só mudam os quatro pilares.
  - **Térreo 2, sala de estar (usuário, 19/10/26: "siga com o item 2 do térreo"):** no PDF da Casa A (ARQ_LAYOUT HUMANIZAÇÃO) o sofá curvo acompanha o tapete redondo pela esquerda, das 12h às 7h, com o encosto na borda do tapete (um pouco para fora) e o assento em C. Sobre o assento há duas almofadas e duas almofadas redondas com pregas: são os círculos com raios, que a conferência tinha lido como vasos. Na ponta de cima do sofá fica uma mesinha redonda; à direita, a poltrona voltada para a mesa de centro. O motor pôs o sofá ao longo do alto do tapete, até a direita, sem a mesinha e sem a poltrona.
    - O sofá do motor sai: o tapete volta copiado em volta do centro dele, no mesmo raio (a borda fica contínua), de um setor livre à direita (de −40° a 15°), em espelho.
    - O sofá do PDF entra no estilo do render: tecido creme; rolo do encosto mais claro; face do encosto escurecendo no vinco com o assento; frente arredondada; sombra suave no tapete, da luz do alto à direita, como a da mesa de centro. As divisões do encosto do PDF viram costura fina. As almofadas têm volume e sombra curta; as redondas, as pregas e o botão.
    - A poltrona da direita é a poltrona de baixo à direita do render, girada 226,5° (o ângulo que melhor cobre o contorno do PDF, com o encosto para a borda do tapete). A mesinha é a mesinha redonda entre as poltronas de baixo. O pufe/mesinha do render junto ao sofá (o contorno grosso do PDF ali) volta por cima. Cada clone tem sombra nova, na mesma luz.
    - Mesa de centro, poltronas de baixo, rótulo e tapete fora do sofá velho ficam como estavam.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_sala_estar_antes_depois.jpg`. Prancha do Térreo e PDF refeitos; só muda a sala de estar.
  - **Térreo, rejuntes (usuário, 19/10/26: "Precisamos remover os rejuntes"; escopo escolhido por ele: o piso interno do Térreo, sem o deck da piscina, o Subsolo nem o 1º Pavimento):** o travertino da varanda, das salas, do hall interno, da área gourmet e dos cômodos tinha saído em placas grandes, com a junta marcada (linhas finas verticais e horizontais) e cada placa num tom (até 15 de luminância de diferença). O piso volta contínuo, com a textura e a luz do próprio render (`ajustes_casaa.rejuntes`).
    - Onde: o travertino da legenda (#DCD9CA na base v6, levada à imagem pelo afim do Térreo), sem a escada interna. Dentro dele, só o que é piso pela cor (claro e quente como o travertino).
    - O que fica: móveis, tapetes, paredes e os traços desenhados. Os traços vêm do PDF (DOC_LINHAS E PROJEÇÕES, ARQ_PAREDE, ARQ_ESCADAS E RAMPAS e ARQ_PERGOLADO: tracejados de projeção, arcos e folhas de porta), mais o que for 35 ou mais mais escuro que o piso em volta. Em volta de tudo isso, um anel de 3 px também fica. As juntas do motor chegam a −25 e não entram nessa regra.
    - Textura: 35 miolos de 32 px do próprio piso, sem junta vertical (os veios horizontais do travertino são a textura e ficam) e sem os pontinhos escuros. Cada miolo é dividido pela luz do lugar e tecido por image quilting.
    - Luz: o tom do piso em volta, suavizado (sigma 12 px) o bastante para os degraus entre placas sumirem. As sombras dos móveis ficam: o que é 2 a 7% ou mais mais escuro que a luz do lugar.
    - No anel em volta dos móveis e dos traços, o piso original fica, mas no tom do piso refeito ao lado (sem isso a borda do anel marcava um degrau). O que sobrou de junta vertical ali vira a média dos dois lados. Onde uma junta cruza um tracejado, sobra um toco de 2 a 3 px junto ao tracejado.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_rejuntes_antes_depois.jpg` e `..._rejuntes_detalhe.jpg`. Prancha do Térreo e PDF refeitos.
  - **Novos pedidos do usuário para o Subsolo (19/10/26), com recortes da prancha:** "portas de vidro não pretas da sauna da casa A. melhore o aspecto das janelas. Esse traço preto no fim da área de circulação não existe. As marcações de juntas não existem na área de depósito e nem na circulação interna (entre banho de serviço e depósito). as cubas dos banhos femininos e masculinos são maiores." Ficam como os itens 4 a 8 do Subsolo, um por vez.
  - **Subsolo 4, portas de vidro da academia:** nos dois lados da academia (para a circulação e para o hall), o motor fez as portas de correr como um traço preto com dentes, e no lado da circulação com os dentes ao contrário do PDF.
    - No PDF da Casa A (ARQ_PAREDE) são folhas de vidro de 2,83 pt (~1,6 px), desencontradas duas a duas: quatro do lado da circulação (as duas do meio mais para dentro da academia) e duas do lado do hall, com o batente fino em cima e embaixo.
    - O traço sai: em cada linha de pixel, o trecho escuro em volta do px mais escuro (abaixo de 120 de luminância, mais 1 px de cada lado) recebe em espelho o piso do seu lado (travertino da circulação, madeira da academia, soleira e travertino do hall).
    - As folhas entram claras, como o vidro da sauna: vidro (226, 228, 228), a borda fina e escura (70, 72, 74, 0,35 px), que faz o vidro se ler, e a linha do meio do PDF (as duas metades da folha) mais clara. Batentes em alumínio, com a mesma borda.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_portas_academia_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos; contra a prancha anterior, só mudam os dois lados da academia.
  - **Subsolo 5, janelas:** a do banho de serviço (para a circulação) e a da circulação para o depósito. O motor fez cada uma como uma peça cinza de cantos arredondados, com a borda grossa e borrada, um pouco para fora da parede.
    - No PDF da Casa A (ARQ_PAREDE) é o vão na parede com o vidro fino no meio, os caixilhos nas pontas, os retornos da parede e as faces da parede passando pelo vão (o peitoril).
    - Entram nessa geometria: o peitoril claro (o quartzo das bancadas, #ECE8E1), as duas faces em linha fina (0,35 px), o vidro como o das portas da academia, os caixilhos em alumínio e os retornos no preto das paredes; acima e abaixo do vão, a parede preta. Fora do vão, a borda escura da peça do motor volta ao piso do lado.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_janelas_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos; só mudam as duas janelas.
  - **Subsolo 6, traço preto no fim da circulação:** ao longo da borda esquerda da circulação, ~5 px para dentro do travertino, o motor fez um traço preto vertical, da escada do deck até a parede de baixo. No PDF da Casa A a circulação só termina, sem linha.
    - O traço sai como o das portas da academia (`tirar_traco`): em cada linha, o trecho escuro (abaixo de 140) e 1 px de cada lado recebem em espelho o travertino de cada lado. A última linha antes da parede de baixo fica fora, para a parede não ser tocada.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_circulacao_traco_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos; só muda a borda da circulação.
  - **Subsolo 7, juntas do depósito e da circulação interna:** o piso desses dois ambientes (Bege Bahia na legenda) saiu como placas de ~44 × 22 px, cada uma num tom, com a junta marcada (linhas em x 661, 749, 793, 837, 880 e 925 e em y 478, 496 e 522 px).
    - O piso volta contínuo, com a textura do próprio render: tecida por image quilting (como o Bege Bahia aprovado do Térreo, `retoque_bege_bahia_terreo.quilting`) de dez miolos de placas, longe das juntas, cada um normalizado pelo seu tom.
    - A textura vai na luz do render: o tom do piso em volta, suavizado (sigma 14 px em x e 8 px em y) o bastante para as placas sumirem e a sombra junto à parede da direita ficar.
    - Ficam como estão as paredes, as janelas, a porta do depósito com o arco (traço fino, protegido) e a peça junto à parede de baixo do depósito.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_juntas_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos; só mudam os pisos do depósito e da circulação interna.
  - **Subsolo 8, cubas dos banhos feminino e masculino:** o motor fez em cada bancada uma cuba branca pequena (~16 × 10 px). No PDF da Casa A (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS) a cuba é uma calha de ~32 × 15 px, quase da largura da bancada e de toda a profundidade, com uma faixa plana junto à parede do fundo, onde fica a torneira.
    - Entra nessa geometria, como as cubas aprovadas da Casa E (`retoque_subsolo_casae.bancada_cuba`): louça branca com o contorno fino, a bacia escurecendo da borda ao fundo, a válvula no meio e a torneira cromada saindo da parede do fundo, com a sombra curta. A bancada do render fica.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_cubas_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos; só mudam as duas cubas.
  - **Novos pedidos do usuário para o Subsolo (19/10/26), com recortes do PDF e da prancha:** "essa divisória não é parede. é outra coisa! esse piso da circulação é marmore bege bahia. Inclusive melhore a representação do bege bahia no depósito e na área de circulação"; "faltando a representação dos boxes dos chuveiros, em vidro"; "faltou a bancada da pia, com a cuba; ambos em suas respectivas dimensões" (banho de serviço). Ficam como os itens 9 a 12 do Subsolo, um por vez.
  - **Subsolo 9, boxes dos chuveiros:** a ducha ao lado da sauna e o chuveiro do banho feminino. No PDF da Casa A (ARQ_LOUÇAS E METAIS) cada box é de correr: o trilho tracejado de parede a parede e duas folhas de vidro desencontradas; onde não há folha é a entrada do box (na ducha, à direita; no banho feminino, embaixo).
    - O render não tinha o vidro: na ducha, nada; no banho feminino, um traço escuro de cima a baixo, que sai (o travertino de cada lado continua, `tirar_traco`).
    - As folhas entram como as do box do banho de serviço (`vidro_box`): cada uma na metade do trilho do PDF (1,4 pt), fina, clara e com a borda fina.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_boxes_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos; só mudam os dois boxes.
  - **Subsolo 10, divisória entre os banhos feminino e masculino:** o motor a fez como parede preta (~3 px). No PDF da Casa A ela não está na camada das paredes: está na das bancadas (ARQ_BANCADAS), com o miolo branco (na ARQ_PAREDE o trecho é branco, vão) e as peças finas em cinza por dentro, em degrau, como as placas de pedra das bancadas; ~19 cm no total.
    - Entra na geometria do PDF (x 883,8 a 889,7 px) como peça clara, no tom das bancadas do render (BGR 192, 209, 222), com a borda fina e as peças finas do PDF em cinza; o registro pequeno do lado do banho feminino, cromado. O preto do motor sai antes (o piso de cada lado continua); em cima e embaixo ficam as paredes.
    - O material não está escrito no PDF: se não for pedra, muda só a cor (`DIVISORIA["pedra"]`).
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_divisoria_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos; só muda a divisória.
  - **Subsolo 11, Bege Bahia:** a área de circulação ao longo da academia (do pé da escada do deck até a parede de baixo) tinha saído em travertino; o depósito e a circulação interna, num bege fosco sem cara de mármore (no item 7, sem as juntas). No PDF a circulação tem a hachura do mármore.
    - Os três passam ao Bege Bahia aprovado da Casa A: o mármore das varandas do 1º Pavimento, que já foi ao Térreo (`textura_bege`: os trechos `FONTES_1PAV` de `renders/POE642_CasaA_PH_1Pavimento_v7_final2.png`, tecidos por image quilting), na cor dele.
    - A sombra suave do render fica, como no Térreo: a textura nova escurece onde o piso do render era mais escuro que o piso em volta (mediana 7 px, suavização 6 px, até 14%).
    - Ficam: as paredes, as janelas, a sauna, as folhas de vidro da academia (a faixa vai até elas, linha a linha), a folha da porta do depósito com a peça junto à parede, e o arco da porta, que volta por cima do mármore como escurecimento relativo. A soleira da porta do depósito também é Bege Bahia.
    - A escada que desce do deck (item 3) passa a tirar a textura do degrau do mesmo Bege Bahia, no creme dela (a legenda já dava a escada como Bege Bahia, creme forte).
    - Ordem de execução no `ajustes_casaa.py`: 1, 2, 7, 11, 3, 4, 5, 6, 8, 9, 10 (e depois 12). O Bege Bahia vem antes da escada (a sombra do último espelho cai nele) e antes dos itens que apagam traços em espelho (o piso de cada lado já é o mármore).
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_bege_bahia_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos.
  - **Subsolo 12, bancada e cuba do banho de serviço:** o motor fez só um quadrado claro junto à parede da esquerda.
    - No PDF da Casa A a bancada (ARQ_BANCADAS) tem 22,7 × 51,0 pt (x 577,0 a 589,4 px, y 513,1 a 541,1 px), da parede da esquerda, com um recorte onde entra a cuba (ARQ_LOUÇAS E METAIS): quadrada, de cantos arredondados, 22,6 pt (x 580,7 a 593,1 px, y 520,9 a 533,3 px), avançando além da bancada, com a bacia à direita e a torneira monocomando no lado da parede, com a bica para a direita.
    - Entram nessas medidas, no padrão das cubas aprovadas (item 8 e Casa E): a bancada no tom das bancadas do render, com a borda fina e a sombra curta; a cuba de louça com o contorno fino, a bacia escurecendo da borda ao fundo e a válvula; a torneira cromada. O que sobrava do quadrado do motor à direita da bancada volta ao piso.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_banho_servico_bancada_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos; só muda a bancada.
  - **Subsolo 13, gramado junto à escada do deck (usuário, 19/10/26, com o recorte da prancha do Térreo):** "ao termino dos degraus no sentido do subsolo, ou seja, a escada desce, no último degrau, após ele, há um gramado, que separa o último degrau da área de circulação do subsolo". Abaixo da escada, entre a borda do deck esmaecido e a circulação, a prancha do Subsolo estava em branco; no Térreo ali é o gramado.
    - Entra o gramado do próprio Térreo aprovado, no mesmo lugar: as duas imagens vão ao quadro comum, e o afim de uma à outra passa por ele. Fica na cor dele, só onde o Subsolo está em branco: da escada até a parede de baixo do Subsolo (x 376 a 575, y 584 a 849 px), da borda esquerda do deck esmaecido até a circulação.
    - A borda com o branco é suave. Na emenda com a circulação, o px claro da borda dela vira a média dos dois lados.
    - Fica em cor plena, não esmaecido como o deck: o gramado está no nível do pátio do Subsolo, junto à circulação.
    - Antes e depois em `renders/POE642_CasaA_PH_Subsolo_gramado_escada_antes_depois.jpg`. Prancha do Subsolo e PDF refeitos.
  - **Novos pedidos do usuário para o Térreo (19/10/26), com recortes da prancha:** "aqui é um jardim verde com plantas" (o jardim de 4,79 m²); "aqui são dois tanques de água com torneiras, na área de serviço"; "piso da área do Gás é marrom granito"; "faltando a representação da porta do gás e seu arco"; "faltando também as duas portas da área de jardim e seus arcos"; "representar os portões, de ambos os lados, da área descoberta". Seguem um por vez.
  - **Térreo 8, jardim de 4,79 m² (usuário: "aqui é um jardim verde com plantas"; item 8 da conferência):** o motor fez o jardim como piso claro, vazio. No PDF da Casa A ele tem a forração (a hachura de grama) até a faixa de piso junto à porta da direita, e três touceiras.
    - Entra o gramado do próprio Térreo (um trecho do gramado ao lado, do tamanho do canteiro: x 783 a 890, y 856 a 898 px), com a sombra curta das paredes em volta (mais forte junto à de cima e à da direita: a luz vem do alto à direita). A faixa de piso junto à porta fica.
    - As três touceiras entram nas posições e no tamanho do PDF (raio 14,5 px): clones da palmeira em estrela do jardim lateral do render, já sobre a grama e com a sua sombra. Cada clone é recortado do gramado pela cor (distância em Lab ao gramado limpo), girado e espelhado para não repetir, com uma sombra curta a mais.
    - As plantas de vaso da varanda e da sala foram testadas antes, mas sobre a grama ficaram desbotadas, com uma orla clara.
    - O rótulo "JARDIM" fica em branco (ajuste no `rotulos_casaa.py`), que se lê sobre a grama e as palmeiras.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_jardim_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, tanques (usuário: "aqui são dois tanques de água com torneiras, na área de serviço"):** o motor fez duas peças lilás com um símbolo estranho. No PDF da Casa A (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS) é a bancada junto à parede de cima (x 916,7 a 962,3, y 755,2 a 777,2 px), com dois tanques de louça lado a lado. Cada tanque tem o esfregador (a faixa de cima) e a bacia funda, e a torneira de parede no meio, com a bica descendo até o esfregador.
    - Entram nessas medidas, no padrão das cubas aprovadas: a bancada no quartzo claro das bancadas (#ECE8E1), com a borda fina e a sombra curta; cada tanque de louça branca com o contorno fino, as nervuras do esfregador, a bacia escurecendo da borda ao fundo e a válvula; a torneira cromada, da parede.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_tanques_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, gás (usuário: "piso da área do Gás é marrom granito" e "faltando a representação da porta do gás e seu arco"):** o motor fez o piso do gás em lilás e a porta como uma faixa cinza, sem folhas nem arcos. No PDF da Casa A o gás tem porta de duas folhas, que abrem para a área de serviço descoberta.
    - Entra o granito marrom da área de serviço (um trecho limpo dela, no tom dela), do fundo do gás até a face de fora da parede (x 899,3 a 932,4, y 836,9 a 855,7 px).
    - Entram as duas folhas abertas, nas medidas do PDF, com os arcos finos (como as portas aprovadas, `desenhar_porta`). Os arcos ficam num cinza mais escuro (92, 94, 96) que o dos arcos sobre o granito, para se lerem sobre a pedra portuguesa.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_gas_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, porta do jardim (usuário: "faltando também as duas portas da área de jardim e seus arcos"):** no PDF da Casa A, o jardim de 4,79 m² abre para a área de serviço descoberta por uma porta de uma folha, no vão da parede da direita, que abre para fora. A folha aberta fica junto à parede de baixo. As duas folhas ao lado são as do gás, feitas no item anterior. O render tinha só o vão.
    - Entram a folha aberta e o arco (centro em x 899,3, y 894,5 px; raio 25 px), como a porta do gás.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_porta_jardim_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, portões (usuário: "representar os portões, de ambos os lados, da área descoberta"):** no PDF da Casa A (ARQ_PAREDE), cada lado da área de serviço descoberta tem um portão de correr de duas folhas desencontradas, com os batentes nas pontas. À esquerda, ele dá para o gramado; à direita, para o acesso de pedestres. O render tinha só uma faixa clara com uma borda escura.
    - A faixa sai (`refazer_faixa`): em cada linha, o piso de cada lado continua em espelho (a grama e a pedra portuguesa).
    - Entram as folhas nas medidas do PDF, em metal (o alumínio das portas de vidro do Subsolo, 150, 153, 156), com a borda fina escura, a linha do meio de cada folha e uma sombra curta.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_portoes_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo 9, escada caracol da área de serviço (usuário: "somente uma parte será representada, sendo a outra esmaecida. note onde o arco está em destaque"; item 9 da conferência):** o motor fez só um círculo com doze raios escuros sobre o granito. No PDF da Casa A (ARQ_ESCADAS E RAMPAS e ARQ_ELEMENTOS FIXOS), a escada sobe da direita (o "S"), no sentido anti-horário. Os degraus 1 a 7, até a linha de corte, são cheios, com o corrimão de madeira cheio por fora; do 8 em diante, acima do corte, é tracejado.
    - O círculo do motor sai: o granito em volta, tecido de um trecho limpo dele (image quilting) e na luz do lugar (mediana do anel em volta, sem a parede e a porta).
    - Degraus 1 a 7 (de 0° a 131,4°, os raios do PDF): pisos de madeira clara (a da mesa do render, com o veio no sentido do raio), do pilar central à borda. Levam o sombreamento de subida das escadas aprovadas, sem linhas: cada degrau um pouco mais claro que o de baixo (de 0,86 a 1) e a sombra curta de cada espelho no degrau de baixo. Por fora, o corrimão de madeira, cheio; no granito, a sombra curta da escada.
    - Degraus 8 em diante: os mesmos pisos, esmaecidos (22% sobre o granito), com os espelhos em traço claro.
    - No centro, o pilar em metal, com um brilho.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_caracol_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, portas no granito (usuário: "melhorar a representação dos arcos e portas. lembrando que os arcos das portas no marrom granito são em cinza, com traço fino"; e, no banho do motorista, "o arco da porta de entrada [...] está imperceptível, devendo ser em cinza, como de regra"):** as quatro portas de giro sobre o granito (da cozinha para a área de serviço, da despensa, do banho e do quarto do motorista). O motor fez as folhas grossas, claras e um pouco fora do lugar, e os arcos quase não se viam.
    - A folha do motor sai: os px claros (30 acima do granito do lugar) na faixa dela, 3 px para cada lado, viram o granito logo ao lado, de fora da faixa.
    - Entram a folha e o arco do PDF (ARQ_PAREDE), como as portas aprovadas, com o arco em cinza fino (160, 161, 160; 0,45 px), a regra das Casas C, D e E.
    - Rótulos: o arco novo do banho do motorista cortava o texto, e o da despensa pegava o "DE". O B. MOTORISTA sobe e vai à esquerda, entre o vaso e o arco; o DESPENSA desce para baixo do arco, como no PDF; os dois um pouco menores (0,9).
    - Na prancha, só as três regiões das portas mudaram (a da cozinha e a da despensa ficam juntas).
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_portas_granito_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, eletrodomésticos em inox (usuário: "eletrodomésticos em inox", com a fileira de baixo da cozinha e do gourmet):** o motor fez os volumes no lilás dos armários. No PDF (ARQ_LAYOUT HUMANIZAÇÃO), os quadrados sem diagonal são eletrodomésticos: dois no fim da bancada do gourmet, dois na cozinha e as duas máquinas da área de serviço, logo abaixo (estas entraram também, como na Casa D).
    - Cada um recebe o inox aprovado da Casa D, levado ao quadrado: no gourmet e na cozinha, as metades do par da cozinha retocada da Casa D; na área de serviço, as máquinas de lá. Com a sombra curta e o contorno fino, como na cozinha e nas máquinas da Casa E.
    - O volume do motor passava até 2 px do quadrado do PDF, para fora (com um brilho na quina de cima). O inox cobre os dois, para não sobrar moldura lilás. Os armários com diagonal (até o teto) ficam como estão.
    - Na prancha, só a fileira dos eletrodomésticos mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_inox_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, bancada gourmet (usuário: "melhore a representação da área molhada e divisoria da bancada"):** o motor fez, no braço de baixo da bancada, duas caixas: uma com um "texto" ilegível e outra com a cuba.
    - No PDF (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS):
      - a área molhada é o retângulo em volta da cuba, a 2,3 pt da borda e da ponta da bancada, até a parede;
      - a divisória é a linha que corta a área molhada de lado a lado, interrompida pela cuba;
      - a cuba é retangular, de aba fina;
      - a torneira gourmet tem a base e a alavanca junto à parede e a mola até a bica, sobre a cuba.
    - As duas caixas saem: no lugar delas entra a bancada logo à esquerda, coluna a coluna, na mesma luz.
    - Entram:
      - a área molhada e a divisória em traço cinza fino, o da área molhada das Casas C e D, com a área 3% mais escura que a bancada para se ler como uma zona (o lado de cima fica a 1 px da borda e se lê junto com ela);
      - a cuba em inox (aba, bacia da borda ao fundo, contorno);
      - a torneira cromada (base, alavanca, mola e bica com o arejador), com a sombra curta.
    - Na prancha, só a bancada mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_gourmet_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, bancada da cozinha (usuário: "melhore as representações das pias e bancada, com a área molhada bem representada. além disso, preciso de aspecto de bancada de pedra na cozinha"):** o motor fez a bancada da parede da direita no lilás dos armários, chapada, com duas cubas borradas. No prompt, todas as bancadas, inclusive as da cozinha, são de quartzo claro com pontilhado fino.
    - No PDF (ARQ_BANCADAS e ARQ_LOUÇAS E METAIS):
      - a bancada vai da parede de cima à de baixo;
      - a área molhada é o retângulo em volta das duas cubas, até a parede;
      - as cubas são retangulares, de aba fina;
      - cada cuba tem a válvula e a torneira de bica reta, com a base e a alavanca junto à parede.
    - A bancada passa a ser de pedra: o quartzo do próprio render (o da ilha e da bancada gourmet), com o desenho do Bege Bahia aprovado (manchas em nuvem e pontinhos) só na luz, para se ler como pedra clara. Leva o contorno fino e a sombra curta.
    - A área molhada fica como na bancada gourmet: traço cinza fino nos lados livres e 3% mais escura.
    - Entram as cubas em inox, com as válvulas, e as torneiras cromadas, com a sombra curta.
    - Na prancha, só a bancada mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_cozinha_pias_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo 3, estar sob a projeção (usuário: "melhorar a representação dessa área. não é mesa de jantar. área de estar."; item 3 da conferência):** o motor pôs uma mesa retangular com 6 cadeiras. No PDF (ARQ_LAYOUT HUMANIZAÇÃO e ARQ_MOBILIÁRIO) são 4 poltronas em X, de encosto curvo que abraça o assento até os braços, voltadas para uma mesa triangular de cantos arredondados no centro, sob o X tracejado da projeção.
    - A mesa e as cadeiras saem, com as sombras. O travertino volta, tecido (image quilting) de um trecho limpo à direita do quadrado, na luz do piso em volta.
    - As poltronas entram no contorno do PDF, no estilo do sofá aprovado da sala:
      - assento e encosto com os braços, divididos pelas linhas do PDF;
      - cada parte com o volume arredondado e o vinco nas linhas;
      - nas cores do sofá, com a sombra na mesma luz.
    - Por que não um clone: a poltrona aprovada da sala é de outro desenho e só cobria 59% do contorno.
    - A mesa triangular entra no contorno do PDF, no carvalho da mesa do motor, com o contorno fino e a sombra curta.
    - O X tracejado volta por cima, como o render o desenha: os traços do PDF, no passo e na fase dos traços do render em volta (medida: −4,5 px numa diagonal e +1,25 px na outra), na cor e na largura deles.
    - Na prancha, só o quadrado da projeção mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_estar_projecao_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo 5, lavabo (usuário: "melhorar cuba e sua posição e tamanho. representar a bancada da cuba. representar o sanitário. representar e gerar o rótulo da claraboia"; item 5 da conferência):**
    - O que o motor fez: no alto, uma peça estranha com um arco e um bloco claro (onde ficam a claraboia e o vaso); à direita, uma cuba branca solta, menor que a bancada e longe da parede.
    - O que o PDF tem (ARQ_BANCADAS, ARQ_LOUÇAS E METAIS e DOC_LINHAS E PROJEÇÕES):
      - a bancada na parede da direita, com a cuba esculpida (a bacia, a fenda do ralo junto à parede e um friso atrás) e a torneira saindo da parede;
      - o vaso suspenso na parede da direita, no alto;
      - a projeção da claraboia: o retângulo tracejado com o X, no alto, e a nota "PROJ. CLARABOIA" logo abaixo.
    - As peças do motor saem; o travertino é tecido do próprio lavabo, na luz dele.
    - Entram:
      - a bancada em quartzo, como a da cozinha;
      - a cuba esculpida no próprio quartzo, como a do lavabo aprovado da Casa E: o fundo escurece para a fenda, junto à parede; as bordas de cima e da direita fazem sombra curta para dentro; traço fino na borda;
      - a torneira cromada saindo da parede;
      - o vaso suspenso no contorno do PDF, como os aprovados (louça com volume e o tampo fechado);
      - o tracejado da claraboia, como o do estar sob a projeção.
    - Rótulo: `rotulos_casaa.py` ganhou a lista `incluir`, de notas do PDF que entram mesmo sendo projeção. "PROJ. CLARABOIA" fica logo abaixo do tracejado, em duas linhas, no corpo do PDF (numa linha só encostava na parede e no vaso).
    - Na prancha, só o lavabo mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_lavabo_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, porta pivotante (usuário: "melhorar a representação da porta pivotante, mostrando-a até o hall externo com seus respectivos arcos"):** o motor parou a folha no batente entre os dois halls e só fez o arco grande, no hall interno. No PDF (ARQ_PAREDE) a folha passa do pivô e entra 0,65 m no hall externo, e esse trecho tem o arco pequeno, do lado de lá.
    - A folha e o arco grande do render ficam: estão no lugar do PDF.
    - Entram, no mesmo desenho deles:
      - o resto da folha até a ponta do PDF, com as três linhas da folha do render (contorno, miolo claro, contorno) e o contorno na ponta;
      - o arco pequeno, do fim da folha ao batente de cima, centrado no pivô, no cinza e na largura do arco grande.
    - Na prancha, só esse trecho mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_pivotante_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, escada interna e o jardim em volta (usuário: "não há uma barreira de subida. precisamos representar a parte colorida até o 7 degrau, onde tem a linha em diagonal. sendo esmaecida a partir desse degrau, pois já está na região do 1º pavimento. e a área verde ao redor precisa ter um aspecto melhor"):**
    - O que o motor fez: a escada em U inteira cheia, com as linhas dos degraus e um retângulo de traço por cima (a "barreira"), e o jardim num verde chapado.
    - O que o PDF tem (ARQ_ESCADAS E RAMPAS):
      - a escada sobe do degrau 1, à esquerda do lanço de cima, para a direita;
      - a linha de corte (o traço em diagonal com o X) passa no 7º degrau;
      - do 8º em diante (o resto do lanço de cima, o patamar e o lanço de baixo) é tracejado, acima do corte;
      - o jardim (17,46 m²) inclui a área da escada: ela sobe de dentro dele.
    - Feito como na escada caracol:
      - o jardim inteiro, com a área da escada, vira o gramado aprovado (o da grama ao lado do jardim de 4,79 m², tecido por image quilting, no tom dele), com a sombra curta das paredes;
      - os degraus 1 a 7, até a linha de corte, ficam cheios: o travertino do piso interno, com o sombreamento de subida das escadas aprovadas e sem linhas. Cada degrau é um pouco mais claro que o de baixo (de 0,86 a 1), com a sombra curta de cada espelho no degrau de baixo, e a escada faz sombra curta no gramado;
      - do 8º degrau em diante, os mesmos pisos esmaecidos sobre o gramado (30%), com os espelhos e o contorno em traço claro;
      - a linha de corte do PDF (o traço com o X), fina.
    - A barreira do motor sai junto.
    - Na prancha, só o jardim com a escada mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_escada_interna_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, rótulo do shaft (usuário: "trazer o rótulo do shaft"):**
    - O "SHAFT" do PDF, ao lado do elevador, ficava fora, com as outras notas que não são ambientes.
    - Entrou pela lista `incluir` do `rotulos_casaa.py`, na posição do PDF, em corpo 0,85, porque o shaft tem ~15 px de largura.
    - Na prancha, só o rótulo mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_shaft_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo 11 e 12, quarto e banho do motorista (usuário: "representar a cama no quarto do motorista. representar a cuba e bancada da pia corretamente no banho do motorista. representar o box e o chuveiro adequadamente. o rótulo do quarto do motorista está no local errado. o arco da porta de entrada do banho do motorista está imperceptível"):**
    - O que o motor fez: a cama e o box como blocos lilás, e a pia como uma cuba solta, sem bancada.
    - O que o PDF tem (ARQ_LAYOUT HUMANIZAÇÃO, ARQ_BANCADAS e ARQ_LOUÇAS E METAIS):
      - a cama de solteiro encostada na parede de cima, com o travesseiro e o edredom com a ponta dobrada;
      - no banho, a bancada na parede de cima e na da direita, com a cuba quadrada de apoio (passa da frente da bancada) e a torneira saindo da parede de cima;
      - o box na ponta da esquerda, até as duas folhas de vidro de correr, com o chuveiro de braço na parede de cima.
    - Os blocos do motor viram o granito, tecido de um trecho limpo do quarto, na luz do lugar.
    - Entram, na geometria do PDF:
      - a cama: lençol e edredom brancos com volume, a ponta dobrada mostrando o avesso, o travesseiro e a sombra curta;
      - a bancada de quartzo com a cuba de louça, a válvula e a torneira cromada;
      - as folhas de vidro do box e o chuveiro, como os aprovados.
    - O arco da porta do banho já tinha entrado em cinza fino, nas portas no granito.
    - Rótulo: o Q. MOTORISTA vai para o lado da cama, como no PDF, no piso livre entre a cama e o armário (~26 px). Fica em corpo 0,8, porque a Inter é mais larga que a fonte do PDF, e em cinza no granito.
    - Na prancha, só o bloco do motorista mudou.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_motorista_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - **Térreo, carros (usuário: "mude as cores, deixe cada carro com uma única cor e deixe os carros desalinhados"):** o motor fez o da esquerda branco e os outros dois no mesmo lilás, alinhados. Feito como nas Casas D e E (aprovadas):
    - Cada carro fica numa cor só, a da paleta da Casa D: branco perolado (esquerda), grafite (meio) e azul-marinho (direita).
      - A cor vem de uma curva de tom na luminância do próprio carro. A ordem do render fica: vidros mais escuros que a lataria, reflexos.
      - A cor entra só nos tons médios e claros; o vidro escuro fica neutro.
      - O lilás dos retrovisores, que caía no filtro de lanternas, também muda; só luz vermelha ou âmbar fica.
    - Cada carro sai do lugar com um deslocamento e um giro leves (até 5 px e 2°), para quebrar o alinhamento:
      - o carro sai com a sombra dele (15 px em volta) e o granito volta, tecido por image quilting de trechos limpos, na luz do lugar;
      - ele entra no lugar novo, com a sombra curta.
    - Na prancha, só a garagem mudou.
  - **Térreo, sem arcos (decisão do usuário, 19/10/26, com as plantas de referência dos elementos: "remover os arcos, escadas com linhas"):** item `sem_arcos`, o último da lista.
    - **Quais arcos saíram:** os do PDF da Casa A, que são as curvas da camada ARQ_PAREDE: 16 portas de giro (com os dois arcos da pivotante) e os 12 arcos rasos da porta camarão da varanda. Saíram os arcos do motor e também os que os itens anteriores desenharam no lugar do PDF (gás, jardim, portas no granito, pivotante, motorista). As folhas e os batentes ficam.
    - **Portas de giro:** o círculo passa pelas pontas e pelo meio do arco.
      - Numa faixa de ±3 px em volta dele, onde o traço passa, a faixa inteira vira a textura do mesmo piso logo depois dela, na mesma direção. O afastamento usado é, de quatro, o mais parecido com o piso em volta, e a borda é suave, para não sobrar fantasma do traço.
      - Onde nenhum afastamento serve, entra inpaint.
      - A folha, o batente (as retas do centro às pontas) e o que é preto ficam.
      - 14 dos 16 tinham traço na imagem.
    - **Porta camarão:** o motor tinha pintado de cinza o setor entre cada folha e o arco. Esse setor volta a ser travertino: tecido de trechos limpos da varanda, normalizado e vezes o campo de luz do piso em volta. Ficam as folhas em zigue-zague, as sombras delas e o trilho.
    - **Conferência:** só as regiões das portas mudaram (5.946 px na imagem, 19 regiões; na prancha, 20 regiões).
    - **Antes/depois:** `renders/POE642_CasaA_PH_Terreo_sem_arcos_antes_depois.jpg`. A prancha e o PDF foram refeitos.
    - **Regra nova para todas as casas:** porta sem arco (só a folha e o batente) e escada com o bocel em linha cinza suave, como na referência. `_texturas/elementos.py` segue isso: `porta_giro` sem arco.
    - Antes e depois em `renders/POE642_CasaA_PH_Terreo_carros_antes_depois.jpg`. Prancha do Térreo e PDF refeitos.
  - Mais pedidos (19/10/26): "vamos melhorar a representação da escada. não há uma barreira de subida. precisamos representar a parte colorida até o 7 degrau, onde tem a linha em diagonal. sendo esmaecida a partir desse degrau, pois já está na região do 1º pavimento. e a área verde ao redor precisa ter um aspecto melhor"; "trazer o rótulo do shaft". E ainda: "representar a cama no quarto do motorista. representar a cuba e bancada da pia corretamente no banho do motorista. representar o box e o chuveiro adequadamente. o rótulo do quarto do motorista está no local errado. o arco da porta de entrada do banho do motorista está imperceptível, devendo ser em cinza, como de regra" (o arco já foi, nas portas no granito); "mude as cores, deixe cada carro com uma única cor e deixe os carros desalinhados".
  - Pedidos seguintes do usuário (19/10/26): "melhorar a representação dessa escada caracol. somente uma parte será representada, sendo a outra esmaecida [...] onde o arco está em destaque"; "melhorar a representação dos arcos e portas. lembrando que os arcos das portas no marrom granito são em cinza, com traço fino"; "eletrodomésticos em inox"; "melhore a representação da área molhada e divisoria da bancada" (gourmet); "melhore as representações das pias e bancada, com a área molhada bem representada. além disso, preciso de aspecto de bancada de pedra na cozinha"; "melhorar a representação dessa área. não é mesa de jantar. área de estar" (item 3); "melhorar cuba e sua posição e tamanho. representar a bancada da cuba. representar o sanitário. representar e gerar o rótulo da claraboia" (lavabo); "melhorar a representação da porta pivotante, mostrando-a até o hall externo com seus respectivos arcos".

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

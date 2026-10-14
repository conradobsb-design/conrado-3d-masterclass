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
- **Prompt:** `POE642_CasaC/POE642_CasaC_PH_Subsolo_v1.md`.
- **Render (prompt v1):** `renders/POE642_CasaC_PH_Subsolo_v1_render_marcado.webp` (com a seta vermelha do usuário; o render limpo não chegou como arquivo).
- **Imagem final = o render, retocado:** `renders/POE642_CasaC_PH_Subsolo_v1_retocado.png`, pelo `retoque_subsolo_casac.py`: tira a marca vermelha e inverte o sentido de descida dos **degraus largos da esquerda** (descem para cima, rumo ao pátio; a sombra de cada aresta passa para o lado de cima). A escada curta numerada não muda (pedido do usuário).
- **Próximos passos:** rodapé (chave `entrega` na config: pedir ao usuário as áreas da Casa C, a unidade e se o endereço segue o padrão das outras casas) e PDF.

```bash
cd projetos/POE642_CasaA/scripts
python gerar_bases.py Subsolo "../../_pdfs_cliente/642 - SUBSOLO - CASA C.pdf" --config ../../POE642_CasaC/config_bases.json --saida ../../POE642_CasaC/bases
python texturizar_base.py Subsolo ../../POE642_CasaC/bases/POE642_CasaC_BASE_Subsolo_v2.png --config ../../POE642_CasaC/config_bases.json --saida ../../POE642_CasaC/bases --nome POE642_CasaC_BASE_Subsolo_v3_texturas
```

## 7. Avisos

- **Check-in agendado:** havia um check-in agendado do PR na sessão da nuvem. Ele só verifica o PR e não mexe em nada.
- **Commits:** sempre no branch `claude/poe642-casa-a-handoff-jmchm3`.
- **Teste de regressão do `gerar_bases.py`:** num PDF sintético com `ARQ_PAREDE`, o resultado esperado é 1 vidro-forma, 1 vidro-traço e 1 descarte de cada tipo (parede, porta, muros), com `pyflakes` sem avisos. O PDF sintético ficou na nuvem. Se precisar, ele é fácil de refazer: duas paredes cinza 0,357, um vidro fino branco, um traço de vidro, uma porta com arco e um texto.

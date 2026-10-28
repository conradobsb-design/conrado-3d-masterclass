# POE 642 · Casas A e B — handoff para continuar no computador local
_14/10/2026. Estado ao fim da sessão na nuvem. Branch: `claude/poe642-casa-a-handoff-jmchm3`. PR: conradobsb-design/conrado-3d-masterclass#1 (rascunho)._

**Regras de representação: `POE642_REGRAS.md` (consolidadas em 19/10/26). Elas valem mais que as decisões antigas registradas aqui.**

**Agora (26/10/26):** o usuário mandou 11 especificações para todas as casas (`POE642_REGRAS.md`, seção 19) e pediu para apresentar as inconformidades antes de alterar. A auditoria das 12 plantas está pronta (seção "Auditoria das especificações de 26/10", no fim). Respostas: paredes em cinza 80; o tapete conta como objeto para os rótulos; aprovação planta por planta. **Feito:** o Subsolo da Casa A, com os pedidos do usuário para ele e a auditoria (seção "Casa A · Subsolo com os pedidos de 26/10", no fim; `final3840_casaa.py`). **Próximo:** aguardar o OK do usuário no Subsolo da Casa A e seguir, planta por planta, com as outras 11.

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
- **Pente fino pelas regras (21/10/26), feito:** os 25 itens do Térreo e os 12 do Subsolo (seção "Casa B · os ajustes do pente fino, feitos", no fim), com as pranchas e o PDF refeitos a partir das finais com rótulos (`..._final_rotulos.png`, `--no-quadro`). A peça branca abaixo do lavatório gourmet virou floreira (proposta do pente fino). Próximo, pela ordem da seção 17 das regras: a Casa C.
1. **Casa B entregue** (Subsolo e Térreo, pranchas e PDF), comandos na seção do pente fino.
2. **Opcional, mais nitidez nos objetos:** passar o render num upscaler de IA (Higgsfield `upscale_image`) antes do `elementos_do_render.py`. Isso gasta créditos, então só com autorização.

---

## 6b. Casa C — em andamento

**Agora (22/10/26):** as finais do Térreo e do Subsolo refeitas em 3840 px com os itens do pente fino e as respostas do usuário (`final3840_casac.py`; seção "Casa C · a final refeita em 3840 px", no fim). Pranchas e PDF refeitos.

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

**Agora (25/10/26):** finais do Térreo e do Subsolo em 3840 px pelo motor das Casas B e C (`final3840_casad.py`), com as respostas do usuário aos mapas do pente fino; pranchas e PDF refeitos (seção "Casa D · final em 3840 px", no fim). Aguarda a revisão do usuário.

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
  42. grama na escala da referência (R1, R4: "representar a escala da madeira conforme modelo referência apresentado, bem com o da grama, garantindo textura"). A grama do render tinha grão fino de carpete (o detalhe fino com o triplo do da referência) e manchas fora de escala. Duas opções foram ao usuário (A, no tom da referência, RGB 71, 85, 42; B, o desenho da referência no verde do render, RGB 84, 107, 41: `renders/POE642_CasaE_PH_Terreo_grama_opcoes.jpg` e `_opcoes_inteira.jpg`); ele escolheu "OPÇÃO B". Rotinas novas em `texturas_escala`, para as outras casas: `mascara_grama` (o gramado da base chapada sem as plantas: manchas grandes que não são grama, medidas a mais de 4 px da borda do gramado, fechadas e com os vãos entre folhas; mais os px verdes junto aos pisos e nos vãos entre os pisantes) e `trocar_grama` (a luz larga do lugar, raio 1,5 m; as sombras das plantas, razão entre a luz de 0,25 m e a larga, só onde escurece mais de 7%; e o desenho inteiro da grama da biblioteca, na escala de 31,1 px/m). A cor da grama para a máscara é medida num trecho limpo (`GRAMA["amostra"]`): a mediana do gramado inteiro puxava para a das palmeiras, e as folhas claras viravam grama. Conferência: mudaram 460 mil px do retocado, todos no gramado (até 4 px da borda dele); plantas, pisos, piscinas e o branco de fora do lote ficaram; o rodapé da prancha ficou igual. Prancha e os três PDFs refeitos (um pouco menores: a grama nova comprime melhor). Antes e depois: `renders/POE642_CasaE_PH_Terreo_grama_antes_depois.jpg`.
  43. Bege Bahia como a referência (R1; a regra de 20/10 do Subsolo: a foto de referência, nublada, quente, com o contraste dela). No Térreo ele estava rosado e claro (RGB 232, 217, 203, contra 230, 211, 186 da foto), em placas grandes com veios brancos soltos e pontinhos escuros do motor. Como no Subsolo da mesma casa (os mesmos parâmetros do item 24 de lá): os pontinhos escuros pequenos (até 4 px, 14 níveis abaixo da luz em volta; 2.707 px) viram a luz do lugar; o desenho da biblioteca entra inteiro (força 1, suavização 0,4 px), na escala de 31,1 px/m, no tom da foto, com a luz do lugar (raio 0,25 m: as sombras dos móveis, das barras e dos pilares ficam). Áreas: o #E8E8E8 da base chapada (varanda, deck, blocos e degraus da esquerda, pisantes e WC DCE 1). O travertino do Térreo fica como está: é o travertino aprovado da casa, de onde vem o do Subsolo. Conferência: mudaram 219 mil px do retocado, todos no Bege Bahia; rodapé igual. Prancha e os três PDFs refeitos. Antes e depois: `renders/POE642_CasaE_PH_Terreo_bege_bahia_antes_depois.jpg`.
  44. projeções da cobertura (R8, R9). Pedido do usuário: o tracejado cinza fino sobre as bordas das notas "PROJ. COBERTURA" (a varanda do 1º Pavimento como referência, os brises da garagem e a linha do PDF na garagem), com duas fotos (fachada posterior: "o L fica na varanda + espaço gourmet"; fachada frontal: a garagem). Três coberturas, no esquema aprovado ("Esquema está certo", `renders/POE642_CasaE_PH_Terreo_projecoes_esquema.jpg`): o L da laje baixa do espaço gourmet + varanda (borda de cima e esquerda do gourmet, do PDF do Térreo; a do topo da piscina até a varanda; a esquerda e a de baixo da varanda, do contorno da varanda e da suíte 3 do 1º Pavimento, no mesmo quadro); a laje da garagem (a linha do PDF em cima, a lateral direita junto aos brises e a borda de baixo, para o acesso de veículos); e a faixa de cima. Os pilares da varanda ficam dentro do L, com folga de 32 a 60 pt (conferido por `pointPolygonTest`); o quarto pilar do PDF (x = 1421 pt) é o de dentro da sala. O usuário chegou a pedir os pilares "internos a linha" e a borda de baixo foi estendida pela parede da suíte 3; logo depois ele esclareceu ("os pilares já estão internos a linha. eu me confundi com os círculos"), e a borda voltou a parar na fachada da sala (x = 1380 pt), como no esquema aprovado. Tracejado: traço de 15 cm e vão de 7,5 cm, 0,55 px, cinza (150), força 0,85, por cima de tudo, menos nas paredes pretas. Retocado e imagem final refeitos; a prancha e os PDFs ficam para depois das próximas alterações (pedido do usuário: "ainda não precisa ir pra o PDF"). Imagem: `renders/POE642_CasaE_PH_Terreo_projecoes_cobertura.jpg`.
  45. conferências sem mudança na imagem. Soleiras (R13: "atenção às soleiras, representar onde tem e evitar adicionar onde não tem"): o critério do Subsolo (a soleira é o vão da porta na espessura da parede deixado em branco no PDF, entre os batentes; onde o piso atravessa o vão, não há). As 16 portas de giro e a do hall de entrada têm o vão branco no PDF (as faixas brancas da ARQ_PAREDE junto de cada arco) e, no render, a soleira clara no vão; no gás, o vão dá para o interior do abrigo, também branco no PDF, sem soleira à parte. Nenhuma soleira inventada. Vidros contínuos sem montantes (regra de 20/10): as duas folhas da piscina (pedido do usuário, item 31), o box de correr de duas folhas (item 37) e as fachadas de vidro da sala, que no PDF são portas de correr de várias folhas: nada a mudar.
  46. cortinas (pente fino, item 1; "confirmado, pode começar pelo 1"). Feito com a cortina de linho da biblioteca (`_blocos/blocos.py`, aprovada em 20/10), e o trilho entrou por regra nova do usuário: "trilhos da cortina tem que ser de fora a fora. somente a cortina pode estar a meia distancia, totalmente recolhida ou totalmente fechada" (registrada no `POE642_REGRAS.md`, seção 8). O trilho é uma linha cinza fina, de parede a parede, do lado do vidro; o pano de linho cru fica em ondas por dentro, com a sombra leve. `blocos.cortina` ganhou `com_pano` e `com_trilho`, para o trilho e os panos saírem em separado.
    - **Escritório:** o PDF (ARQ_LOUÇAS E METAIS) tem a linha ondulada junto à janela da direita, em dois trechos (1,79 e 1,59 m, a meia distância); o motor tinha feito só tracinhos brancos. A faixa dos tracinhos volta ao travertino (as mesmas colunas, do vão entre os dois trechos, espelhado; a parede preta fica). O trilho vai da parede de cima à de baixo, e os dois panos ficam nos trechos do PDF, com o eixo do tecido na linha dele.
    - **Living, vidro da varanda:** pedido do usuário no meio do item, com um recorte ("Representar a cortina"); o PDF não tem cortina ali. As quatro folhas de correr são escalonadas (a de baixo chega a x = 1385,9 pt). O trilho fica logo por dentro delas (x = 1390 pt), da parede de cima até a linha do trilho da fachada de baixo (y = 1694,4 pt), e o pano fica fechado no vão todo, como o retângulo marcado.
    - **Living, fachada de baixo (pente fino, item 2):** o usuário mandou um recorte: "corrija as cortinas aqui também". No PDF (ARQ_MOBILIÁRIO) são dois trechos de linha ondulada, a meia distância: x de 1394 a 1560 pt e de 1703 a 1874 pt. O motor tinha feito um zigue-zague cinza no primeiro e tracinhos no segundo, e os dois saíram: as duas linhas de travertino logo acima entram espelhadas, porque o veio corre na vertical.
      - As quatro folhas de correr são escalonadas, e a da direita sobe até y = 1694,1 pt. Por isso o trilho fica logo acima delas (y = 1693,3 pt), do trilho do vidro da varanda (fecha o L no canto) até a parede da direita (x = 1870,1 pt). O eixo do tecido fica 1 pt acima da linha do PDF.
      - O trilho do vidro da varanda passou a terminar nessa linha, e o pano dele, logo antes do pano de baixo.
      - Conferência: mudou só a faixa do L (o vidro da varanda e a fachada de baixo). Antes e depois: `renders/POE642_CasaE_PH_Terreo_cortinas_fachada_antes_depois.jpg`.
  47. pedra portuguesa do acesso de veículos (pente fino, item 3; "Siga para o item 3"). A regra (R1; seção 3: "pedras de 6 a 8 cm") e o material da casa (pedra portuguesa caramelo, base v3). O motor fez pedras de 12 a 15 cm (7 a 9 px na final de 3840 px).
    - **Por que na final:** na escala certa, uma pedra de 7 cm tem ~2 px no retocado (2000 px). Ampliada para a final, vira grão de areia: testada, a textura da biblioteca, bege, ficou assim no tom caramelo, com força 1,0 e 1,8. Por isso as pedras são desenhadas de novo na própria final, depois do quadro comum e antes dos rótulos. Lá cada pedra tem ~4 px. No retocado entra o mesmo desenho, na escala dele, para os dois ficarem coerentes.
    - **Desenho:** as pedras caramelo, ocre e creme do `fontes_procedurais.pedra_portuguesa` (o mesmo da base v3), agora com a escala da imagem como parâmetro (`cm_por_px`). Pedras de 7 cm; juntas de 0,6 px, escurecidas a 0,78, porque as juntas de areia clara da base sumiam nesse tamanho; contraste 0,85, para as pedras creme não saltarem.
    - **Luz:** a luz larga do lugar (raio de 1,5 m), no tom caramelo que já estava lá, com as sombras dele: a razão entre a luz de 0,25 m e a larga, só onde escurece mais de 7%. É a `texturas_escala.trocar_pedra_portuguesa`, nova, que vale para as outras casas.
    - **Área:** o caramelo #C49A6C da base chapada, com folga, só onde o px é caramelo. As plantas que passam por cima do acesso e a grama ficam.
    - **Conferência:** só o acesso mudou (uma região, no retocado e na final). Antes e depois: `renders/POE642_CasaE_PH_Terreo_pedra_portuguesa_antes_depois.jpg`.
    - **Refeito com a foto (20/10/26).** O usuário escolheu "opção 1, tom da foto".
      - **O que não serviu:** a foto espelhada em blocos virou caleidoscópio, e a textura tecida da biblioteca, cara de granito. Com 7 cm em ~4 px, o leque some nas duas.
      - **O que entrou:** o leque desenhado por código, em `texturas_escala.pedra_portuguesa_leque`. As escamas têm 1,2 m de raio, em fiadas desencontradas; as pedras de 7 cm seguem arcos concêntricos, com contornos irregulares de ~8 mm; as juntas são claras de areia (1,2 cm). As cores das pedras são sorteadas do miolo das pedras da foto (bege, cinza e rosado; tom médio RGB ~190, 172, 152). A luz do lugar entra só como relativa, com as sombras.
      - **Franja da borda:** os px de mistura entre o caramelo do motor e a grama deixavam um fio laranja. Cada um recebe a troca de tom na fração de caramelo que tem, pelo r - g.
      - **Final:** a área é só a da base, porque o retocado já chega com a pedra nova.
      - **Conferência:** contra o estado anterior ao item 3, só o acesso mudou, no retocado e na final. Antes e depois, com a foto ao lado: `renders/POE642_CasaE_PH_Terreo_pedra_portuguesa_antes_depois.jpg`. A regra (seção 3) passa a citar a foto, o leque e o tom.
    - **Pergunta do usuário: "qual é a referencia da pedra portuguesa?"** A referência é a foto de 19/10 (`_texturas/originais/pedra_portuguesa.webp`; na biblioteca, vista de cima, `_texturas/pedra_portuguesa.jpg`). O item 47 usou dela só a escala. A cor foi o caramelo de 15/10 ("igual à da Casa A"), e o desenho saiu do gerador por código, com pedras soltas. A foto tem pedras bege e rosadas, juntas claras de areia e o assentamento em leque. Comparação: `renders/POE642_CasaE_PH_Terreo_pedra_portuguesa_referencia.jpg`. Proposta ao usuário: refazer o item com o desenho da foto, a 6 a 8 cm, desenhado na final; ele escolheu o tom da foto (acima).
  48. título da folha (pente fino, item 4; "siga para o item 4"). A regra (seção 12: o título da folha não entra). O texto "0. TÉRREO / ESC.:1:50" já não entrava, mas o sublinhado dele sobrou no canto de baixo à esquerda, logo abaixo do canto tracejado do lote: uma linha do PDF sem camada, de x = 136,4 a 181,9 pt, em y = 2187,0 pt. A faixa dessa linha (folga de 2 px) volta ao branco, que é o fundo fora do lote, só nos px claros. O tracejado do lote, 7 px acima, fica. Conferência: só esse trecho mudou (78 px no retocado, 291 na final). Antes e depois: `renders/POE642_CasaE_PH_Terreo_titulo_folha_antes_depois.jpg`.
  49. "m²" dos rótulos (pente fino, item 5; "siga para o item 5"). Na rotina comum (`retoque_1pav_casae.rotulos_ambientes`), o "2" ficava na posição do PDF, e o "A: ... m" sai em Inter, com outra largura: com números largos ele encostava no "m"; com os "1" estreitos ("7,11") sobrava um vão. Agora o "2" fica logo depois do fim do "m", medido na própria fonte, com a mesma folga em todos (7% do corpo da linha, `ROTULOS["folga_m2"]`), na altura de sobrescrito do PDF. A regra foi registrada no `POE642_REGRAS.md` (seção 12). Conferência: o retocado ficou idêntico; na final mudaram só os 27 "2" (regiões de até 21 × 18 px). Os outros pavimentos e casas usam a mesma rotina e passam a sair assim quando forem refeitos. Antes e depois: `renders/POE642_CasaE_PH_Terreo_m2_antes_depois.jpg`.
  50. granito marrom menos escuro (pente fino, item 6; pedido do usuário: "o piso marrom menos escuro?"). Hoje está em RGB 83, 59, 52 (mediana); o da biblioteca (`_texturas`, "mais liso e menos escuro") está em 151, 119, 100. Opções levadas ao usuário, na imagem final, por ganho de cor só no granito: a área de granito da base chapada, com peso pelo croma (perto do marrom) e pela luminosidade (de 40% a 150% da mediana). Assim ficam de fora carros, inox, móveis, paredes e rótulos, e as sombras ficam proporcionais.
    - A: RGB 104, 77, 66 (+25%);
    - B: RGB 124, 95, 81 (+50%);
    - C: o tom da biblioteca, RGB 151, 119, 100. Nessa opção, os rótulos brancos sobre o granito perdem contraste.
    - Imagens: `renders/POE642_CasaE_PH_Terreo_granito_opcoes.jpg` (cozinha e serviço) e `..._opcoes_inteira.jpg`.
    - **Escolha do usuário: "opção B, sem pontos os grandes brancos".** Feito no retocado, antes das projeções (`granito_tom`).
      - **Pontos:** os claros do motor (mais de 10 níveis acima da mediana de 7 px em volta, até 40 px e 8 × 8 px) viram a mediana em volta: 6.141 pontos.
      - **Proteções:** os traços cinza neutros (as folhas de porta), as linhas da DOC_LINHAS E PROJEÇÕES e as bordas de objetos (retrovisores) ficam, a 2 px. O primeiro teste apagava trechos do X tracejado da área descoberta; com as linhas do PDF desenhadas como máscara, ele ficou inteiro.
      - **Tom:** ganho por canal de RGB 82, 58, 51 a 124, 95, 81 (na final, mediana 124, 94, 80), só nos px de granito.
      - **Correção junto:** o granito mais claro passou a passar no teste de caramelo da pedra portuguesa (item 47), na borda do acesso, e mudava a luz relativa do acesso inteiro. A máscara da pedra agora exclui o granito da base.
      - **Conferência:** no retocado e na final, tudo o que mudou está no granito (0 px fora no retocado, 1 px na final). Regra da seção 3 atualizada.
      - **Grade de manchas (20/10/26):** na planta inteira, o granito mais claro mostrou a grade de manchas claras e escuras que o motor repete (cara de porcelanato). O usuário: "sim, corrija o granito antes do 7". A variação entre ~3 cm e ~1 m sai inteira: a razão entre a média de 30 px e a de 1 px do granito, nos px com a luz de granito e não neutros, inclusive as manchas claras rosadas. Ela vale a mais de 12 px de objeto e parede; de 5 a 12 px some aos poucos, e as sombras ficam. O grão de 1 px fica. Os pontos claros passam a sair até 80 px e 12 × 12 px.
      - **Referência do usuário (20/10/26):** "use essa referencia de granito marrom", com a foto de um granito marrom com lascas de agregado. A foto veio só na conversa, sem arquivo, então o desenho foi reproduzido por código (`fontes_procedurais.granito_referencia`):
        - base marrom quente (BGR 68, 88, 118) com nuvens suaves de ~15 cm (±4,5%) e mosqueado de 3 cm;
        - lascas irregulares de três tamanhos: 3.200/m² de 2 a 7 mm, 320/m² de 7 a 22 mm e 22/m² de 22 a 55 mm, em marrom escuro e claro, creme, bege, ferrugem, cinza e quase preto, com desfoque leve;
        - a foto tem ~60 cm de largura, estimado pelas lascas.
      - **Aplicação (`texturas_escala.trocar_granito`):** a luz do lugar (média de 2,5 px nos px de granito, relativa à mediana) vezes o desenho, no lugar do ganho de cor da opção B. Os traços do PDF e os cinza neutros ficam. Num primeiro teste ficou um halo escuro em volta do X tracejado; agora esses traços recebem a troca de tom na fração de granito que têm, e o halo sumiu.
      - **Resultado:** tom final na planta RGB 118, 89, 69. Só o granito mudou (0 px fora no retocado e na final). Regra da seção 3 atualizada. Antes e depois, com o desenho de perto: `renders/POE642_CasaE_PH_Terreo_granito_antes_depois.jpg`.
      - **Conferência da grade:** só o granito mudou (0 px fora no retocado e na final); tom final RGB 124, 95, 81. Antes e depois, com o estado antes do item 6, a 1ª versão da opção B e a atual: `renders/POE642_CasaE_PH_Terreo_granito_antes_depois.jpg`.
  51. rótulo da adega (pedido do usuário, com um recorte: "o rótulo não pode estar sobre objeto. nesse caso, escreva no piso, dentro da adega"; R7). O "ADEGA / A: 2,59 m²" ficava no alto do U da prateleira de vinhos, com o nome sobre a moldura. O piso livre dentro do U vai de x = 2112 a 2189 e de y = 782 a 815 na final de 3840 px. O rótulo desce 6,4 px (em px de 2000) e fica centrado nele, no corpo de sempre (1,3x), que cabe. É um ajuste em `ROTULOS["ajustes"]`. Conferência: o retocado ficou idêntico, e na final mudou só o rótulo. Antes e depois: `renders/POE642_CasaE_PH_Terreo_rotulo_adega_antes_depois.jpg`.
  52. soleiras (pedido do usuário: "revisar todas as soleiras"; R13). As 16 portas de giro do PDF, conferidas pelo arco de cada uma, contra o vão branco da ARQ_PAREDE na espessura da parede:
    - **Com soleira no PDF (12):** BH gourmet, lavabo gourmet, área de serviço descoberta, WC DCE 1, DCE, área de serviço/cozinha, circulação/garagem (de cima e de baixo), despensa, CPD, cozinha/circulação e lavabo.
    - **Sem soleira:** as duas portas do gás abrem para o interior do abrigo, branco no PDF e sem soleira à parte; a pivotante do hall fica na fachada de vidro.
    - **Os outros 15 vãos brancos da mesma espessura** são janelas (as do BH gourmet, do DCE, do banho gourmet, da cozinha e da fachada do living) ou bordas da piscina e do spa: não são soleiras.
    - **Na imagem, antes:** as soleiras eram as do motor, desiguais. No granito eram cremes lisas, de larguras variadas; no travertino, quase sumidas (cozinha/circulação, circulação/garagem de baixo e lavabo).
    - **Agora:** todas iguais, como no Subsolo da mesma casa. O vão exato do PDF em Bege Bahia na escala, no tom da referência, e as duas faces da parede (os lados compridos) em traço cinza fino.
    - **Conferência:** mudaram só os 12 vãos, no retocado e na final. Folha de comparação de todos os vãos com o PDF e antes e depois: `renders/POE642_CasaE_PH_Terreo_soleiras_antes_depois.jpg`.
  53. vegetação do gramado (pente fino, item 7; pedido do usuário: "a vegetação e grama?"; R1, R4). A grama já era a aprovada (item 42). A vegetação do motor estava fora de escala: folhas de costela-de-adão de ~1,2 m e touceiras de 5 a 8 m. Ela também passava do verde, sobre a pedra portuguesa do acesso e os pisantes.
    - **Opções levadas ao usuário,** nas mesmas manchas de hoje: A, árvores, arbustos e palmeiras da planta de referência de 19/10 (`_texturas/vegetacao`); B, jardim tropical em maciços com os blocos da biblioteca. Na B, a costela-de-adão e a planta de folhas largas ficaram de fora, porque mostram o vaso. A folha está em `renders/POE642_CasaE_PH_Terreo_vegetacao_opcoes.jpg`. Escolha do usuário: "opção A".
    - **Feito (`vegetacao`):**
      - As folhas do motor que passavam do verde saem, numa faixa de 0,6 m. Cada px volta ao material da base chapada, copiado do próprio material ao lado. Na pedra portuguesa, o item 47 redesenha.
      - A grama da referência entra sob as manchas.
      - Entram 60 plantas da referência no tamanho real (árvores de 4,5 e 3,4 m, palmeiras e arbustos de 1,1 a 1,6 m), com a copa dentro do verde. Elas não giram: a sombra vem no desenho, para baixo e à esquerda.
    - **Conferência:** no retocado mudaram só o verde (255 mil px), a faixa em volta (4,5 mil px) e o jardim de inverno (item 54); fora disso, 0 px.
  54. jardim de inverno (pedido do usuário durante o item 7: "precisamos alterar também o jardim de inverno interno da casa E"). A floreira tem 5,7 x 1,25 m, e as folhagens do motor, cerca de 1 m cada.
    - **Feito (`jardim_flores`):** forração escura, com plantas tropicais da biblioteca de blocos por cima: bananeira, comigo-ninguém-pode, arbusto e planta com flores, no tamanho real. São 11, em duas fileiras desencontradas. As copas saem um pouco da floreira (como no item 19), nunca sobre a escada, e as 5 flores tropicais ficam.
    - **Por que blocos:** as plantas da planta de referência (26 px/m) ficaram borradas nos 39 px da floreira.
    - **Imagens:** antes e depois dos itens 53 e 54 em `renders/POE642_CasaE_PH_Terreo_vegetacao_antes_depois.jpg`. A prancha e os PDFs ficam para o fim da lista.
  55. esquadrias finas (pente fino, item 8; pedido do usuário: "portas vidros e janelas mais delicados e finos?"). O motor desenhou caixilhos largos e brancos, com duas ou três linhas, nas janelas, nos vidros da fachada do living e da varanda, no escritório e no hall. No PDF não há camada de esquadria: vidros, folhas e caixilhos estão na ARQ_PAREDE, como brancos finos.
    - **O que entra (`esquadrias`):** os 78 brancos finos da ARQ_PAREDE, com até 12,5 pt de espessura e 15 pt ou mais de comprimento. Ficam de fora as 12 soleiras do item 52, as bordas da piscina e do spa e as portas do elevador (item 6). Eles se juntam em 41 esquadrias, pela vizinhança na mesma direção.
    - **Limpeza:** cada esquadria é limpa numa faixa de 3 px no eixo fino, com o piso de fora espelhado. Do lado de uma parede, vem o piso do outro lado.
    - **Redesenho pelo PDF, em 8x:**
      - paredes em preto;
      - vão de janela com vidro dentro em Bege Bahia, como peitoril; a passagem sem nada (a do escritório) fica no piso;
      - caixilho em alumínio claro; folha de porta em cinza bem claro; vidro no vidro aprovado;
      - os traços do PDF por cima, em cinza médio de 0,3 px.
    - **Ordem:** roda depois do granito (item 50) e antes das soleiras, das projeções e das cortinas, que ficam por cima.
    - **Conferência:** no retocado mudaram 15,2 mil px nas esquadrias e 30 px fora delas (uma coluna de 1 px junto ao vidro do escritório). Antes e depois de cada trecho: `renders/POE642_CasaE_PH_Terreo_esquadrias_antes_depois.jpg`.
  56. ilha do espaço gourmet com 5 banquetas (pente fino, item 9). Pedido do usuário: "na ilha do espaço gourmet, deixe apenas 5 cadeiras". O PDF e o motor tinham 7 banquetas de 22,7 pt, a cada 34 pt. No meio do item, o usuário mandou uma foto: "referencia de banqueta pra ser utilizada e inserida na biblioteca".
    - **Biblioteca:** a foto entrou em `_blocos/originais/folha_06_banqueta_linho.jpg`, como o bloco "banqueta_linho" (madeira clara e linho cru, 0,45 m). O recorte é do `blocos.recortar` (fundo branco). A cartela foi refeita.
    - **Feito (`banquetas`):** a faixa das 7 voltou ao Bege Bahia, com a sombra curta da ilha. Entraram 5 banquetas da referência, no tamanho da do PDF e espaçadas por igual ao longo da ilha (a cada 28,6 px no retocado). Estão de frente para a ilha, com a frente do assento sob o tampo, e a sombra é a da biblioteca.
    - **Nitidez:** no retocado a banqueta tem 12 px e ficava borrada ao ampliar. Por isso, na final de 3840 px, ela é redesenhada (24 px), como a pedra portuguesa.
    - **Conferência:** só a faixa sob a ilha mudou: 2,6 mil px no retocado e 10,2 mil px na final. Antes e depois, com a referência: `renders/POE642_CasaE_PH_Terreo_ilha_gourmet_antes_depois.jpg`.
  57. cooktops das ilhas (pente fino, item 10; pedido do usuário: "melhorar a representação dos cooktops das ilhas, com novo bloco"). O motor tinha feito um retângulo cinza manchado nas ilhas gourmet e da cozinha, sem bocas. No PDF as duas têm o mesmo cooktop de 5 bocas, de 0,88 x 0,50 m.
    - **Bloco:** `cooktop_inox_5_90` da biblioteca: inox, 5 bocas, 90 cm. Segue a regra da seção 7 (bocas do PDF, eletrodomésticos em inox).
    - **Feito (`cooktops`):**
      - o retângulo do motor voltou ao tampo da ilha;
      - o bloco entrou na altura do PDF, centrado, girado de 180° para os botões ficarem do lado de quem cozinha (o oposto das banquetas);
      - o anel azul da chama da foto ficou em inox;
      - na final de 3840 px o cooktop é redesenhado, para sair nítido.
    - **Conferência:** só os dois cooktops mudaram, no retocado e na final. Antes e depois: `renders/POE642_CasaE_PH_Terreo_cooktops_antes_depois.jpg`.
  58. poltronas dos ambientes sociais (pente fino, item 11; pedido do usuário: "vamos melhorar os aspectos das poltronas desses ambientes sociais"). No meio do item o usuário mandou uma folha com 9 poltronas vistas de cima e escolheu: "use a bouclé creme no living e a palhinha na varanda". A folha chegou só como imagem, sem arquivo. Por isso entraram os blocos mais próximos da biblioteca: `poltrona_boucle` (bouclé creme) e `poltrona_rattan` (palhinha com madeira). Ao chegar o arquivo, o modelo exato da folha troca o bloco.
    - **As 8 do PDF (`POLTRONAS["pecas"]`):**
      - 2 de palhinha na varanda, junto ao banco;
      - 2 bouclé junto à mesa de centro do living;
      - 4 bouclé em X em volta da mesa redonda.
      - Para cada uma: centro e ponto para onde olha, em pt; tamanho do PDF, em m.
    - **A do motor sai (`poltronas`):**
      - ele a desenhou maior e um pouco fora do lugar do PDF. O disco de limpeza vai no centro da mancha clara dela, com o raio dela, mais o disco da sombra;
      - a mesa em X fica protegida;
      - o piso vem de um ponto próximo, quase vertical, para o veio do travertino seguir, sem nenhum px de outra peça, emendado em gradiente (`cv2.seamlessClone`).
    - **A nova entra** virada para a mesa, com a sombra curta, e na final de 3840 px é redesenhada por cima, nítida.
    - **Orientação:** o usuário perguntou: "as poltronas estão viradas para fora?". Estavam: nas bouclé eu tinha invertido a frente do bloco (na folha, o encosto fica em cima). Corrigido; as de palhinha já estavam certas.
    - **Conferência:** só os três grupos de poltronas mudaram. Antes e depois: `renders/POE642_CasaE_PH_Terreo_poltronas_antes_depois.jpg`.
  59. mesas redondas da varanda (pedido do usuário depois do pente fino, com uma foto: "mesas e cadeiras para a varanda"). A foto é de uma mesa redonda de madeira com tampo central cinza e 6 cadeiras de couro marrom, na mesma disposição das do PDF: uma em cima, uma embaixo e quatro nas diagonais.
    - **Biblioteca:** entrou como `_blocos/originais/folha_07_mesa_redonda_couro.jpg`, bloco "mesa_redonda_6_couro" (2,4 m). A foto tem fundo cinza em degradê, e por isso entraram dois modos novos no `blocos.recortar`: fundo "cinza" (o que não tem cor é fundo) e "preencher" (o disco cinza do centro entra). A cartela foi refeita.
    - **Feito (`mesas`):**
      - os dois conjuntos do motor (mesa clara com vaso e cadeiras brancas) saem, com a sombra;
      - o buraco recebe o Bege Bahia da biblioteca no tom do item 43, sob a luz do piso em volta, emendado em gradiente;
      - entram os blocos no centro e na altura dos conjuntos do PDF, com sombra curta; o segundo é girado 180° para o tampo cinza variar;
      - na final, os conjuntos são redesenhados, nítidos.
    - **Conferência:** só a faixa das duas mesas mudou. Antes e depois, com a referência: `renders/POE642_CasaE_PH_Terreo_mesas_varanda_antes_depois.jpg`.
  60. mesa de jantar do living (pedido do usuário, com uma foto: "mesa de jantar"). A foto é uma prévia do Shutterstock (2279721019), com a marca d'água no rodapé. Perguntei antes de usar, e o usuário confirmou: "tenho a licença, pode usar".
    - **Biblioteca:** `_blocos/originais/folha_08_mesa_jantar_10.jpg`, bloco "mesa_jantar_10": mesa de madeira com 10 cadeiras estofadas em cinza claro, 4 de cada lado e uma em cada cabeceira, como no PDF; 3,75 m. A caixa do bloco fica acima do rodapé, e a marca d'água não entra no recorte. A cartela foi refeita.
    - **Feito (`jantar`):**
      - o conjunto do motor sai: a mancha dele dentro da caixa do PDF, com a sombra;
      - o buraco recebe o travertino tecido dos trechos limpos em volta (image quilting), sob a luz do piso, emendado em gradiente;
      - o bloco entra no centro da caixa do PDF, girado 90° (cabeceiras em cima e embaixo), com sombra curta;
      - na final, a mesa é redesenhada, nítida.
    - **Conferência:** só a área da mesa mudou. Antes e depois: `renders/POE642_CasaE_PH_Terreo_mesa_jantar_antes_depois.jpg`.
  61. prancha do Térreo (pedido do usuário: "siga para a prancha do Térreo"). Refeita pelo `rodape_entrega.py --no-quadro` (comando no README dos scripts, em "Pranchas de entrega") com a imagem final atual: itens 44 a 60, o pente fino inteiro, mais as mesas da varanda e a mesa de jantar.
    - **Conferência:** a área da imagem é a final, px a px (diferença 0). O rodapé e os três arquivos de rodapé ficaram idênticos. A prancha anterior era a do item 43.
    - **Imagens:** prancha `entrega/POE642_CasaE_PH_Terreo_entrega.png` (3840 × 2600 px). Antes e depois: `renders/POE642_CasaE_PH_Terreo_prancha_antes_depois.jpg`.
    - **Ainda não estão na prancha:** os carros SUV bronze (R12, só na Casa E), que aguardam o arquivo da foto do usuário. Os três PDFs e as montagens do 1º Pavimento (que usam o Térreo como contexto) são o próximo passo.
  62. escada que desce, esmaecida a partir da diagonal (usuário, olhando a prancha: "Faltou o esmaecimento parcial da escada que desce. A partir da linha diagonal discriminada no PDF base"). É a externa do alto, que desce da esquerda para a direita (item 39).
    - **A diagonal:** o PDF do Térreo não tem linha de corte nessa escada (só a seta e o "D"); quem tem é o PDF do Subsolo, no mesmo lance e na mesma caixa (972 a 1263 pt): entre o 7º e o 8º degrau contados da esquerda, de (1073,8; 616,4) a (1108,1; 685,0). No Subsolo, o trecho à esquerda dela (o de cima) está esmaecido e tracejado; no Térreo, o inverso.
    - **Feito (`escada_linhas`, opções novas `viva`, `apos` e `esmaecer` por escada):** viva à esquerda da diagonal (o trecho de cima, no Térreo, com o triângulo). Depois dela, já no Subsolo, a escada fica esmaecida, com os bocéis e as sombras. Não há tracejado, pois o trecho fica por baixo e não é projeção. A linha de corte não é desenhada, como nas outras escadas.
    - **Intensidade:** o 0,8 da interna, sem o tracejado, quase não aparece no travertino claro. Testei 0,8, 0,6, 0,45 e 0,3 e fiquei com 0,45: o esmaecimento fica claro e os degraus continuam legíveis.
    - **Conferência:** no retocado, na final e na prancha, mudou só a escada (110 × 46 px no retocado, 214 × 90 na final); rodapé igual.
    - **Imagens:** prancha refeita. Antes e depois: `renders/POE642_CasaE_PH_Terreo_escada_desce_esmaecida_antes_depois.jpg`.
  63. jardim de inverno só no verde (usuário: "No jardim de inverno remova as cores quentes. Mantenha apenas o verde"). Os quentes vinham de três fontes:
    - as 5 flores tropicais (laranja, vermelha, rosa e amarela);
    - a planta com flores rosa da biblioteca (57% de px quentes);
    - o arbusto amarelo-oliva.
    - **Feito (`jardim_flores`, `JARDIM_FORA["so_verde"]`):** as flores não entram. Nas mesmas posições (mesma semente), a planta com flores virou a costela-de-adão (0,7 m) e o arbusto, a planta de folhas largas (0,8 m); bananeiras e comigo-ninguém-pode ficam.
    - **As duas plantas novas (`"sem_fundo_claro"`):** o recorte delas tinha o fundo branco da foto no vão do meio e o vaso de terracota da costela, e os dois saem do alfa (aparece a forração escura). Na comigo-ninguém-pode isso furaria as listras claras, e ela não entra.
    - **Conferência:** no recorte do jardim, os px quentes passaram de 2.495 a 2. No retocado, na final e na prancha, só o jardim mudou (3 trechos dentro da floreira); rodapé igual.
    - **Imagens:** prancha refeita. Antes e depois: `renders/POE642_CasaE_PH_Terreo_jardim_so_verde_antes_depois.jpg`.
  64. montagens do 1º Pavimento e os três PDFs (usuário: "siga com as montagens do 1º Pavimento e os PDFs"), com o Térreo do pente fino (itens 44 a 63). O `opcoes_1pav_casae.py` refez as três opções; comandos no README dos scripts, em "Pranchas de entrega".
    - **P&B e nublado:** o contexto é o retocado novo do Térreo, realinhado com 73 pontos (erro mediano 0,72 px). Mudou só o entorno, e o 1º Pavimento por cima ficou igual.
    - **Linhas:** o contexto é o PDF e não mudou. Mudaram só os 22 "²" dos rótulos, pela rotina comum do item 49 (o "2" logo depois do "m"), que vale para os outros pavimentos quando são refeitos; o mesmo vale nas outras duas opções.
    - **Pranchas `entrega/POE642_CasaE_PH_1Pavimento_entrega_{pb,linhas,nublado}.png`:** a área da imagem é a montagem, px a px; rodapé igual.
    - **PDFs `entrega/POE642_CasaE_Plantas_Humanizadas_opcao_{PB,Linhas,Nublado}.pdf`:** 3 páginas A3 cada (Subsolo, Térreo e o 1º Pavimento da opção), iguais px a px às pranchas; 18,9, 17,7 e 20,2 MB.
    - **Antes e depois das montagens:** `renders/POE642_CasaE_PH_1Pavimento_montagens_antes_depois.jpg`.
    - **Ainda pendentes:**
      - a prancha do Subsolo, que é a mesma: o terreno hachurado dela ainda vem do Térreo de antes do pente fino (tarefa: refazê-lo a partir da final do Térreo; feito em 21/10/26, item 29 do Subsolo);
      - os carros SUV bronze, que aguardam o arquivo da foto (cancelado em 21/10/26: "Mantenha os carros. Não vamos alterar mais."; ficam os prata da R12).
    - **Conferência do item 1:** no retocado e na final, mudaram só as duas faixas (escritório e vidro da varanda). A prancha e os PDFs ficam para o fim da lista (pedido do usuário: "ainda não precisa ir pra o PDF"). Antes e depois: `renders/POE642_CasaE_PH_Terreo_cortinas_antes_depois.jpg`.
    - **Novos pedidos do usuário durante o item (20/10/26):** entram na lista do pente fino, depois dos itens 2 a 5. Para fazer um por vez:
      - "o piso marrom menos escuro?";
      - "a vegetação e grama?";
      - "portas vidros e janelas mais delicados e finos?";
      - "na ilha do espaço gourmet, deixe apenas 5 cadeiras" (hoje são 7 banquetas);
      - "melhorar a representação dos cooktops das ilhas, com novo bloco" (da biblioteca `_blocos`).
      - "vamos melhorar os aspectos das poltronas desses ambientes sociais" (living e varanda; com os blocos da biblioteca).
- **Pente fino da prancha (20/10/26).** Pedido do usuário: "liste todas as regras que elencamos e vamos passar um pente fino na prancha do terreo da casa E". A prancha foi montada só para a conferência, com a final atual (até o item 44), sem mexer na entrega. Ela foi conferida trecho a trecho contra o `POE642_REGRAS.md` e o PDF.
  - **Conforme:** arcos (R3), escadas com linhas e triângulo (R14), rótulos brancos no granito e fora dos objetos (R6, R7; o LOUCEIRO sobre a marcenaria é a exceção do item 40), carros (R12), grama, Bege Bahia e travertino aprovados (R1, R4), pilares e projeções (R8, R9), soleiras e vidros (R13), box do banho gourmet (R5), lote e fundo branco, louças, cozinha, adega, despensa, DCE e WC DCE 1.
  - **Mapa numerado** (`renders/POE642_CasaE_PH_Terreo_pente_fino_mapa.jpg`, detalhes em `..._pente_fino_detalhes.jpg`), aguardando a confirmação do usuário:
    1. escritório: o PDF tem a cortina nos dois trechos da janela da direita (ARQ_LOUÇAS E METAIS), e o render tem só tracinhos brancos;
    2. living: a cortina da fachada de baixo é um zigue-zague cinza do motor. A regra pede linho off-white, e a cortina da biblioteca foi aprovada;
    3. acesso de veículos: as pedras portuguesas saem com ~12 a 15 cm na prancha (7 a 9 px a 60 px/m), e a regra pede 6 a 8 cm;
    4. canto de baixo à esquerda do lote: sobrou o traço do título da folha ("título da folha não entra");
    5. rótulos: o "m²" da circulação de 7,11 m² sai com o "2" afastado; nos outros, ele encosta no "m" (o "2" fica na posição do PDF e o "m", 30% maior, chega até ele). Uniformizar.
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

- **Pente fino pelas regras (20/10/26).** Pedido do usuário: "Vamos às alterações no primeiro pavimento da casa E. Adotar as regras que elencamos." A imagem final nublada (a opção padrão, seção 11 do `POE642_REGRAS.md`), com o Térreo do pente fino em volta, foi conferida trecho a trecho contra as regras e o PDF (`_pdfs_cliente/642 - 1º PAVIMENTO - CASA E.pdf`). Nada foi retocado ainda.
  - **Conforme:**
    - rótulos: nenhum outro fica sobre objeto, e o "m²" segue a regra de 20/10 (o do banho master: ver abaixo);
    - vazios brancos com o X e o guarda-corpo de vidro;
    - shaft da suíte master;
    - brises em bronze;
    - bancos no pé das camas;
    - torneira de piso da banheira;
    - cubas e copinha;
    - entorno nublado;
    - não há pilares nem projeções de cobertura no PDF deste pavimento (sem camada EST - Pilar).
  - **Mapa numerado** (`renders/POE642_CasaE_PH_1Pavimento_pente_fino_mapa.jpg`), aguardando a confirmação do usuário:
    1. arcos das portas (R3): o item 6 de 16/10 desenhou os 12 arcos do PDF; saem todos, e também o da porta pivotante P1 vista pelo vazio do hall e o da porta pequena junto ao vazio. Ficam as folhas e os batentes;
    2. escada (R14 e "escadas com linhas"): o motor desenhou ~10 degraus, e o PDF tem 19 mais o patamar (o 20). Ela desce da esquerda para a direita (o "D" do PDF à esquerda; é o mesmo lance da interna do Térreo, que sobe da direita para a esquerda). Leva os bocéis em linha suave com a sombra curta e o triângulo no topo (à esquerda), apontando para a direita. No PDF ela é toda viva, sem corte;
    3. boxes com folha contínua (R10): nos banhos 1 e 2 o vidro vai só até o meio; nos banhos 3 e 4 falta o trecho junto às paredes; no banho master a linha está falhada. O vidro fino vai de parede a parede, como no PDF;
    4. banhos 3 e 4: os chuveiros são discos redondos, e o PDF tem a ducha quadrada de parede, com o braço saindo da parede entre os banhos. Os vasos parecem uma peça só atravessando a parede; o PDF tem dois suspensos, costas com costas, cada um no seu banho (regra do vaso: tampo fechado, volume, sombra curta);
    5. guarda-roupas com cabides (R11): os armários do closet master (dois) e dos closets 1 a 4. A rouparia fica em marcenaria areia;
    6. projeções em tracejado (R8, camada DOC_LINHAS E PROJEÇÕES): o shaft estreito entre o elevador e a rouparia (no render, uma faixa de marcenaria), o retângulo com X da rouparia e os X rasos no fundo do box e do vaso do banho master;
    7. porta de correr da rouparia (P10): no render há só duas peças cinza nos batentes; entra a folha de correr do PDF;
    8. soleiras (R13): nas portas dos banhos, o PDF deixa o vão em branco entre os batentes (há soleira); nas portas das suítes o vinílico atravessa (não há). A conferência é porta a porta, no item;
    9. esquadrias finas (como o item 8 do pente fino do Térreo): as janelas dos banhos 1 a 4 (E23), da sala íntima (E17 e E20) e do vazio do hall (E8 e E9) estão em caixilho cinza grosso;
    10. cortinas: os 10 trechos do PDF estão em zigue-zague branco; entram com o bloco de linho da biblioteca e o trilho de fora a fora (regra de 20/10);
    11. vinílico na escala (R4): as réguas do render têm ~35 a 40 cm; a referência tem ~20 cm, claras, em tons alternados. O tom vai em opções (o #A8784F escolhido em 16/10 ou o claro da referência);
    12. Bege Bahia das três varandas como a referência (seção 18), como o item 43 do Térreo;
    13. floreira do banho master: tem uma flor laranja; fica só o verde, como o jardim de inverno do Térreo (pedido de 20/10);
    14. a plantinha sobre o aparador da sala íntima não está no PDF ("nada inventado"): sai. A do canto, junto ao vazio, está no PDF e fica.
  - **No fim:** o nublado vira a opção única (seção 16). A prancha sai sem sufixo, e o PDF único `POE642_CasaE_Plantas_Humanizadas.pdf`.
  - **Rótulo do banho master (feito; usuário: "O escrito do banho master não pode ficar sobre a banheira").** No mapa ele tinha passado como conforme, mas encostava na banheira: o texto começava em y = 592 e a banheira terminava em y = 591 (na final de 3840 px). O desvio em `retoque_1pav_casae.ROTULOS["ajustes"]` passou de (0, 8) a (0, 35) px de 2000, e ele foi para o meio do piso livre entre a banheira e o vidro do box (y ≈ 600 a 712).
    - **Conferência:** nas três montagens mudou só o rótulo (as duas áreas, a de antes e a de agora); rodapé igual.
    - **Refeitos:** as três pranchas do 1º Pavimento e os três PDFs. O retocado de 2000 px com rótulos (que não vai à entrega) sai assim na próxima rodada do `retoque_1pav_casae.py`.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_rotulo_banho_master_antes_depois.jpg`.
  - **Novas anotações do usuário (20/10/26, sobre a prancha), na lista:**
    15. vazios com o Térreo nevoado: "Mostrar a jardineira de baixo mais nevoada" (o vazio sob a escada, sobre o jardim de inverno) e "Mostrar o andar de baixo nevoado" (o vazio do hall). Hoje os dois são brancos (pedido de 16/10: "use a cor branca, em vez de cinza escuro");
    16. quartzito dos banhos: "Textura do quartzito está errada - é um tom mais entre o branco e o cinza" (hoje pêssego, o #EAD4BF da legenda);
    - sobre a opção linhas: "Mostrar o térreo humanizado, mas de forma enevoada e não técnica". Confirma o fecho já previsto: o nublado vira a opção única.
  - **Item 1, portas sem os arcos (R3), feito.** No `retoque_1pav_casae.py`, `ARCOS["sem_arco"]`: o item 6 de 16/10 não desenha mais os arcos do PDF (o motor não tinha feito nenhum: volta o piso do render). Ficam as folhas, os batentes e a folha da pivotante P1 vista pelo vazio do hall.
    - **Porta pequena à direita do vazio do hall:** sem o arco, sobrava o setor branco. Ele entrou em `FORA` (`opcoes_1pav_casae.SETOR_PORTA`) e mostra o entorno; os px do traço do arco recebem o entorno depois da montagem; o caixilho e a folha ficam.
    - **Floreira do banho master (fonte fixa):** ela é tirada do retocado do Térreo, que mudou hoje (jardim só no verde). Para não mudar fora do item, a fonte passou a ser o Térreo aprovado de 15/10 (`TERREO_FLOREIRA`); o miolo dela sai igual, px a px. Ela muda no item 13.
    - **Alinhamento fixo na montagem:** o SIFT refeito a cada rodada mexia na pegada inteira, por reamostragem. Agora o afim vem da versão entregue (`renders/POE642_CasaE_PH_1Pavimento_v1_retocado_aprovado.png`), como no Térreo.
    - **Conferência:** no retocado sem rótulos, mudaram só as 12 áreas dos arcos (fora elas, diferenças de 1 nível, de arredondamento). Nas três montagens e nas três pranchas, também só as 12 áreas; rodapé igual. As três pranchas e os três PDFs foram refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_sem_arcos_antes_depois.jpg`.
  - **Item 15, vazios com o Térreo nevoado, feito.** Na montagem (`opcoes_1pav_casae.nevoar_vazios`), o branco dos dois vazios passa a mostrar o Térreo de baixo, no mesmo entorno da montagem (no nublado, o Térreo nublado):
    - no vazio sob a escada, a jardineira (o jardim de inverno, já só no verde);
    - no do hall, o piso e a planta do hall de entrada.
    - **Como:** os vazios são o cinza (74) da base v3, fechados e com o X preenchido, com 3 px de folga (`VAZIOS`). O peso vem do branco do render (de 205 a 245), e o Térreo é multiplicado pelo tom do render. Assim, o X tracejado, o guarda-corpo de vidro e a folha da pivotante P1 ficam por cima, como num papel transparente.
    - **Conferência:** nas três montagens e nas três pranchas, só os dois vazios mudaram; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_vazios_nevoados_antes_depois.jpg`.
  - **Item 16, quartzito dos banhos como a referência, feito.** O usuário indicou a referência: "quartzito dos banhos está no quadro de referências já enviado". É a foto do quadro de 19/10, `_texturas/originais/quartzito_aura.jpg` (chapa de 3,00 m, branco-acinzentada, RGB ~221, 215, 211). Os cinco banhos tinham saído no pêssego da legenda (#EAD4BF). Feito em `retoque_1pav_casae.quartzito_referencia`, nas áreas de quartzito da base chapada:
    - **o tom:** a parte pêssego de cada px vai ao tom da foto. A fração vem do R − B do px contra o do piso: as sombras acompanham, e as bordas de louças, vidros, placas e metais não ganham halo. Uma razão de cor única, testada antes, deixava um halo azulado nessas bordas;
    - **o desenho:** a chapa da biblioteca, na escala (31,1 px/m), só na luz. A foto tem uma faixa bege, e o tom pedido é entre o branco e o cinza. Entra só no piso limpo, fora dos traços medidos antes da troca de tom (o vidro dos boxes fica).
    - **Conferência:** no retocado, mudaram só os cinco banhos; nas montagens e nas pranchas, só as quatro áreas dos banhos (os 3 e 4 juntos); rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_quartzito_antes_depois.jpg`.
  - **Rótulo do banho 3 (feito; usuário: "afasta um pouco o rótulo do sanitário").** Estava colado no vaso, logo acima dele: o vaso terminava em y ≈ 1253 e o texto começava em 1256, na final de 3840 px. Em `ROTULOS["ajustes"]` entrou ("BANHO 3", (785,1; 659,4), (0, 7)). O rótulo foi para o meio do piso livre até a parede de baixo (texto de 1269 a 1290), com a folga que o do banho 4 tem do vaso dele (~15 px).
    - **Conferência:** só o rótulo mudou, no retocado com rótulos, nas montagens e nas pranchas; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_rotulo_banho3_antes_depois.jpg`.
  - **Item 2, escada com linhas e o triângulo de orientação (R14), feito.** O motor desenhou ~10 degraus, com o último terço liso. Os dois PDFs têm a mesma escada: caixa de 1659,2 a 1984,0 pt, 19 pisos e o patamar, bocéis a cada 17 pt. No 1º Pavimento ela desce da esquerda para a direita (o "D" do PDF à esquerda).
    - **O piso:** o travertino limpo do Térreo aprovado logo abaixo do jardim (veio no sentido dos pisos) foi copiado para a caixa do PDF, com borda suave. É a mesma limpeza da escada do Térreo (itens 18 e 21 de lá).
    - **As linhas:** `retoque_terreo_casae.escada_linhas`, que ganhou o parâmetro `p2r` (a cadeia deste PDF; sem ele, o Térreo segue igual). Em cada bocel, a linha suave e a sombra curta no degrau de baixo (à direita); o triângulo fica no topo, à esquerda, apontando a descida.
    - **Esmaecida depois do corte:** o PDF deste pavimento não tem corte. Como na escada que desce do Térreo (pedido do usuário de 20/10: "o esmaecimento parcial da escada que desce, a partir da linha diagonal discriminada no PDF base"), ela fica viva até o corte do outro pavimento: o do Térreo, entre o 7º e o 8º degrau contados da direita. Depois dele, esmaecida (0,45), com os bocéis e as sombras, sem tracejado, porque fica por baixo.
    - **Passo novo:** `retoque_1pav_casae.escada_r14` (config `ESCADA`), antes dos vazios: o guarda-corpo de vidro do vazio entra por cima.
    - **Conferência:** no retocado, nas montagens e nas pranchas, só a caixa da escada mudou; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_escada_r14_antes_depois.jpg`.
  - **Pedidos do usuário durante o item 2 (20/10/26):** "complementar os boxes de banhos de forma contínua, fora a fora" (o item 3) e "representar as cortinas da mesma forma que fizemos no terreo" (o item 10). Vão nessa ordem, logo depois.
  - **Item 3, boxes em folha contínua de parede a parede (R10), feito.** O vidro de cada box no PDF (ARQ_LOUÇAS E METAIS) vai de uma parede à outra:
    - banho master: horizontal, em y = 907,5 pt, de 1621,7 a 1719,8;
    - banhos 2 e 1: vertical, em x ≈ 2247, de 764,9 a 865,8 e de 1113,6 a 1214,5;
    - banhos 4 e 3: vertical, em x = 1276,4, de 1286,5 a 1370,4 e de 1382,9 a 1466,8.
    - **Antes:** o motor fez só trechos (nos banhos 1 e 2, até o meio; nos 3 e 4, sem as pontas; no master, falhado).
    - **Feito (`retoque_1pav_casae.boxes_continuos`, config `BOXES`):** o traço do motor sai. Numa faixa de 2,5 px em volta do eixo do PDF, cada px que foge da média dos dois lados (a 5 px) vira essa média. Depois entra o vidro do box do banho gourmet do Térreo: a linha clara fina (226, 229, 230; 0,8 px), sem montantes nem marcas no meio (regra de 20/10: folha contínua), com a borda cinza fina e a sombra suave do lado do chuveiro. O passo roda depois do quartzito.
    - **Conferência:** no retocado, nas montagens e nas pranchas, só as linhas dos cinco boxes mudaram; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_boxes_antes_depois.jpg`.
  - **Carros (Térreo):** a foto do SUV chegou de novo só na conversa (sem arquivo na pasta de imagens recebidas); continua pendente. Cancelado em 21/10/26 (usuário: "Mantenha os carros. Não vamos alterar mais.").
  - **Item 10, cortinas como no Térreo, feito** (usuário: "representar as cortinas da mesma forma que fizemos no terreo"). O item 7 de 16/10 (as ondas do PDF em zigue-zague branco) deu lugar à cortina de linho da biblioteca (`_blocos/blocos.cortina`), posta com o `pousar_cortina` do Térreo (`retoque_1pav_casae.cortinas_linho`, config `CORTINAS_LINHO`):
    - **panos:** em cada um dos 10 trechos de linha ondulada do PDF (ARQ_LOUÇAS E METAIS), na mesma extensão (a meia distância, como no PDF), com o eixo do tecido no eixo da linha do PDF;
    - **trilhos:** um por quarto, de parede a parede, do lado do vidro (regra de 20/10), 5 ao todo: suítes master, 4 e 3 na fachada da esquerda; 2 e 1 na da direita. O fim do trilho é a parede preta do render, procurada numa coluna 3 px para dentro do quarto. No eixo do tecido, colado ao vidro, o montante escuro de uma folha de correr parava a busca no meio da suíte 2. Os trilhos do mesmo lado que se sobrepõem viram um só.
    - **Conferência:** no retocado, nas montagens e nas pranchas, só as faixas das cortinas mudaram, mais uma sombra fraca da cortina antiga (até 6 níveis) junto ao criado-mudo da suíte 2; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_cortinas_antes_depois.jpg`.
  - **Pedido do usuário durante o item 10 (21/10/26):** "melhorar as representações de portas e janelas e vidros". São os itens 9 (esquadrias finas) e 7 (porta de correr da rouparia), os próximos.
  - **Itens 9 e 7, portas, janelas e vidros finos, feitos** (`retoque_1pav_casae.esquadrias_1pav`, config `ESQUADRIAS_1P`, depois do quartzito e antes dos boxes). É o item 8 do pente fino do Térreo: os brancos finos da ARQ_PAREDE de cada zona (vidros, folhas e caixilhos) são limpos e redesenhados pelo PDF com o `esquadria_desenhar` do Térreo. São 36 peças em 21 esquadrias:
    - **janelas:** banho master (E24, junto à floreira), banhos 2 e 1 (E23), sala íntima (E17 e E20) e vazio do hall (E8 e E9). O caixilho cinza grosso do motor dá lugar ao peitoril em Bege Bahia, ao caixilho em alumínio claro e ao vidro fino;
    - **portas de giro** (suítes, banhos e closet master): a folha na espessura do PDF, em branco suave com contorno fino, no estilo aprovado no Subsolo da Casa E (folha 236, contorno 96 a 0,35 px). O cinza do Térreo sumia no quartzito claro;
    - **portas de correr:** a embutida do banho master (P11), a do closet master (P13; o retângulo azulado do motor entre as folhas saiu) e a da rouparia (P10, item 7: o render tinha só duas peças cinza nos batentes).
    - **Ficam:** as fachadas das suítes (item 10 de 16/10), a folha da pivotante do vazio, as portas do elevador (inox) e os retângulos brancos das paredes dos banhos.
    - **A limpeza (`esquadria_limpar_1p`), com quatro ajustes em relação ao Térreo:**
      - parede é só o escuro grosso que não é verde (as paredes do render puxam para o marrom; o verde e os pontos escuros das floreiras viravam manchas brancas);
      - a parede do render fora do retângulo do PDF fica (a faixa de 3 px comia a face da parede junto às folhas e toda a parede da porta embutida);
      - do lado de uma parede, vem o piso mais perto do outro lado (o espelhado de longe era mais claro e virava uma faixa branca junto à parede);
      - faixa e fonte por zona: 1 px para fora nas E23, para não apagar o brise de madeira da fachada; 1 px para dentro no vazio do hall, para não espelhar o X tracejado; o vão da P13 no quartzito do banho.
    - **Conferência:** no retocado sem rótulos, nas montagens e nas pranchas, só as 18 áreas das esquadrias mudaram; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_esquadrias_antes_depois.jpg`.
  - **Pedido do usuário durante os itens 9 e 7 (21/10/26):** "precisamos corrigir a escala do vinílico". É o item 11, o próximo.
  - **Item 11, vinílico na escala (R4), feito** (`retoque_1pav_casae.vinilico_escala`, config `VINILICO`, logo depois da cadeia do PDF, antes dos outros passos). O motor fez réguas de ~40 cm; agora são de 20 cm, como na referência. No meio do item, o usuário pediu: "clareia um pouquinho o vinílico onde está escurecido".
    - **Onde:** nas áreas de vinílico da base chapada (as linhas da hachura do PDF fechadas), só no que é piso no render: o marrom do vinílico, fora tapetes e móveis claros. Os objetos no tom da madeira (mesinhas, almofadas, criados) saem por fugir da luz do piso: mais claros, ou mais escuros com outra cor. A sombra escurece sem mudar a cor e fica como piso; os nós e riscos pequenos do motor também.
    - **A luz:** a média do piso, mais larga atravessando as réguas (o tom de cada régua velha sai) que ao longo delas. O tom do render fica (#A8784F, escolhido em 16/10).
    - **As réguas (`reguas_vinilico`, em 4x):** 20 cm de largura, 1,2 a 1,8 m de comprimento, em fiadas com as juntas de topo desencontradas. Cada régua tem um tom (claro ou escuro, de 1,5 a 4,5%) e o veio do próprio vinílico do render: o detalhe fino ao longo das réguas, de um trecho limpo, sem junta velha no meio. As juntas são linhas finas. O vinílico da biblioteca (da referência, de 26 px/m) foi testado antes; na escala do render, ele ficava borrado e em blocos.
    - **Clarear o escurecido:** onde a luz larga do piso (~1 m) fica abaixo da mediana (119), ela sobe 70% do caminho, em todo o vinílico, com o que está sobre ele (até +20%). Isso vale para o closet master, a rouparia, os closets 1 e 2 e a circulação junto a eles. Com metade do caminho, testada antes, a mudança mal aparecia (+4 níveis no closet master).
    - **Conferência:** no retocado sem rótulos, só o vinílico mudou (fora dele, 55 px da limpeza da porta da rouparia, que espelha o piso novo). Os outros passos saem iguais (mesmos registros de bancos, cortinas e esquadrias). Nas montagens e nas pranchas, só a área do vinílico; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_vinilico_antes_depois.jpg`.
  - **Item 4, chuveiros e vasos dos banhos 3 e 4, feito** (usuário: "Siga pelo item 4"; `retoque_1pav_casae.banhos34_limpar` e `banhos34_pecas`, config `BANHOS_34`, logo depois do quartzito).
    - **O render:** as duchas eram discos redondos, com registros soltos até a parede. O vaso era uma cápsula só, atravessando a parede entre os banhos e ~4 px mais comprida que o vaso do PDF de cada lado. A parede tinha um bloco cinza inteiro no lugar dos dois nichos.
    - **O PDF (ARQ_LOUÇAS E METAIS):** em cada banho, a ducha quadrada com o braço saindo da parede do meio (canopla na face dela) e um vaso suspenso, costas com costas com o do outro banho. Na parede, dois nichos (ARQ_PAREDE em branco), um de cada lado, com o miolo da parede entre eles.
    - **A limpeza:** os discos, os registros e a cápsula saem. Fica a luz do piso em volta (sem paredes, nicho, bancadas e o vidro do box; longe de piso limpo, a luz vem de mais longe), com o desenho da chapa do quartzito logo ao lado, na mesma coluna, longe da parede do meio. Limpar antes do quartzito (o primeiro teste) mudava a média do piso dele e mexia de leve no tom dos outros banhos.
    - **As peças, como as aprovadas no Subsolo da Casa E:**
      - os dois nichos no tom do quartzito, um pouco mais escuro, com contorno fino, e o miolo da parede em preto;
      - `retoque_subsolo_casae.chuveiro`: a ducha quadrada (a placa da Casa A), o braço cromado e a canopla;
      - `retoque_subsolo_casae.vaso`: louça com volume, contorno fino, sombra curta e o tampo fechado. Ele ganhou a dobradiça junto à parede de cima ou de baixo ("cima"/"baixo"); o Subsolo segue igual.
    - **Conferência:** no retocado sem rótulos, nas montagens e nas pranchas, só as duas áreas (duchas com nichos, e vasos) mudaram; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_banhos34_antes_depois.jpg`.
  - **Pedido do usuário depois do item 4 (21/10/26):** "siga por todos os itens, sem me perguntar. se precisar pausar ou alterar algo, eu te aviso." Os itens restantes seguem na ordem do mapa, um commit por item, cada um com o antes e depois, as pranchas e os PDFs refeitos.
  - **Item 5, guarda-roupas com cabides (R11), feito** (`retoque_1pav_casae.guarda_roupas`, config `GUARDA_ROUPAS`, depois das esquadrias). O motor tinha feito caixas lisas de marcenaria.
    - **Onde:** no closet master (dois armários retos) e nos closets 1 a 4 (em L). Cada trecho reto do PDF é o retângulo de uma diagonal da ARQ_LAYOUT HUMANIZAÇÃO; os em L são dois trechos. São 10 trechos.
    - **Como:** `_texturas/elementos.guarda_roupa` (a referência de 19/10: visto de cima, aberto; moldura branca fina com contorno cinza; miolo cinza-claro, mais escuro junto às portas; cabides a cada ~12 cm), no tamanho do PDF, em 4x. As portas ficam do lado comprido que encosta no vinílico do closet.
    - **Ficam em marcenaria:** a rouparia, o armário da copinha e o do banho master (R11 vale só para guarda-roupa).
    - **Conferência:** no retocado, nas montagens e nas pranchas, só as três áreas dos closets mudaram; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_guarda_roupas_antes_depois.jpg`.
  - **Item 6, projeções em tracejado (R8), feito** (`retoque_1pav_casae.projecoes_1pav`, config `PROJECOES_1P`, depois dos boxes). Os traços da DOC_LINHAS E PROJEÇÕES que o motor apagou voltam como no PDF. Ficam por cima de tudo, menos das paredes pretas, no traço das projeções do Térreo (0,6 px, força 0,85).
    - **Shaft entre o elevador e a rouparia:** no PDF, um vão entre duas paredes, com o X; o motor tinha feito ali uma faixa de marcenaria. O vão fica branco, como os vazios, com o X em cinza médio (147).
    - **Rouparia:** o retângulo com X, sobre o vinílico, em cinza claro (226); o cinza médio sumia na madeira. O rótulo da rouparia fica dentro dele, como no PDF.
    - **Banho master:** os X rasos no fundo, sobre o vaso e o box, em cinza médio (150) sobre o quartzito.
    - **Conferência:** no retocado, nas montagens e nas pranchas, só as três áreas mudaram; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_projecoes_antes_depois.jpg`.
  - **Pedido do usuário depois do item 6 (21/10/26):** "o tom dos armários guarda-roupas, pode ser bege dentro e na borda o ocre". O `elementos.guarda_roupa` ganhou `miolo` e `moldura` (BGR; sem eles, o cinza da referência, como antes), e `GUARDA_ROUPAS` passou a pedir bege no miolo (RGB 228, 212, 191) e ocre na moldura (RGB 196, 148, 88). O usuário perguntou qual é a referência de guarda-roupa da biblioteca (a planta do duplex de 19/10, `_texturas/originais/referencia_elementos_*.png`, linha 1 de `_texturas/cartela_elementos.jpg`; as imagens foram mostradas). Depois pediu "aplique o bege e o ocre e siga com os itens" e, antes da rodada, "tem uma barra metallica no meio do armario para prender o cabide". O `guarda_roupa` ganhou `barra` (o cabideiro: tubo de ~2 cm no meio da profundidade, de lateral a lateral, borda escura, brilho no meio e a sombra curta, por cima dos cabides), ligado no 1º Pavimento.
    - **Conferência:** no retocado, nas montagens e nas pranchas, só os guarda-roupas mudaram; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_guarda_roupas_tons_antes_depois.jpg`.
  - **Item 8, soleiras (R13), feito** (`retoque_1pav_casae.soleiras_1pav`, config `SOLEIRAS_1P`, depois das esquadrias). As portas foram conferidas uma a uma no PDF: o vão entre os dois batentes da ARQ_PAREDE e o que a base tem dentro dele.
    - **Com soleira (vão branco):** os banhos 1 a 4, o banho master (a porta embutida da suíte master, P11, e a do closet master, P13) e a rouparia (P10). São sete.
    - **Sem soleira:** as portas das suítes, onde o vinílico atravessa o vão, e a P12 do banho master, onde atravessa o quartzito.
    - **Como, igual ao Térreo e ao Subsolo da casa:** o vão exato do PDF em Bege Bahia na escala (o desenho da biblioteca, no tom da referência), com as duas faces da parede (os lados compridos) em traço cinza fino. A folha da P11, embutida dentro do vão, fica por cima.
    - **Conferência:** no retocado, nas montagens e nas pranchas, só os sete vãos mudaram; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_soleiras_antes_depois.jpg`.
  - **Item 12, Bege Bahia das três varandas como a referência, feito** (`retoque_1pav_casae.varandas_bege`, config `VARANDAS_BEGE`, logo depois do vinílico). As três varandas são a comprida da fachada da esquerda e as das suítes 2 e 1. Antes, o Bege Bahia era claro, quase liso, com pontinhos do motor (RGB ~231, 222, 211).
    - **Como (seção 18 e item 43 do Térreo):** o desenho da biblioteca entra inteiro, na escala, no tom da foto (~230, 211, 186), com os parâmetros do Térreo e a luz do lugar.
    - **O que fica e o que vira piso:**
      - ficam os vasos, as plantas e as peças de fachada: o que sai da cor do piso (outra proporção entre R, G e B) ou fica bem mais claro, com os vãos pequenos entre as folhas;
      - a sombra deles (escurece sem mudar a cor) e os pontinhos do motor viram piso;
      - na borda dos objetos, o próprio px vai ao tom e ao desenho.
    - **Testes descartados:**
      - o `bege_referencia` do Térreo como estava deixava a sombra dos vasos de fora, com um halo do tom antigo em volta;
      - a luz medida com as plantas dentro marcava como objeto o piso claro em volta delas;
      - um limiar de cor estreito marcava a sombra rosada dos vasos de terracota.
    - **Junto:** a bancada da copinha (o item 4 de 16/10 tece o Bege Bahia dela da varanda) e as soleiras das fachadas das suítes (item 10 de 16/10, do mesmo Bege Bahia) seguem o novo.
    - **Conferência:** no retocado, nas montagens e nas pranchas, mudaram as três varandas, a bancada da copinha e as soleiras das fachadas dos banhos 3 e 4; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_bege_varandas_antes_depois.jpg`.
  - **Item 13, floreira do banho master só no verde, feito** (`retoque_1pav_casae.floreira`). A floreira vem do jardim do Térreo aprovado de 15/10 (`TERREO_FLOREIRA`, que fica, porque a escada também copia dele). Antes de pousar, as flores laranja e vermelhas saem: os 46 px quentes (R mais de 25 acima de G e de B), com 1 px de folga, são preenchidos pela folhagem em volta (`cv2.inpaint`). É o mesmo pedido do jardim de inverno do Térreo (20/10).
    - **Conferência:** no retocado, nas montagens e nas pranchas, só a floreira mudou; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_floreira_verde_antes_depois.jpg`.
  - **Item 14, sem a plantinha do aparador da sala íntima, feito** (`retoque_1pav_casae.aparador_sem_planta`, config `APARADOR`, depois das projeções). A plantinha (e a sombra dela no tampo) fica num retângulo de 20 × 12 px do render (x 988 a 1008, y 734 a 746). O tampo é liso, com o veio na horizontal: cada linha é a interpolação entre o px limpo logo à esquerda e o logo à direita, na mesma linha. A borda escura do aparador e a parede abaixo não mudam. A planta do canto, junto ao vazio, está no PDF e fica.
    - **Primeira versão descartada:** o retângulo de 16 px ainda pegava a sombra da planta nos dois lados, e o tampo ficava com uma mancha um pouco mais escura. Ele cresceu 1 px à esquerda e 3 px à direita.
    - **Conferência:** no retocado, nas montagens e nas pranchas, só o tampo do aparador mudou; rodapé igual. Pranchas e PDFs refeitos.
    - **Antes e depois:** `renders/POE642_CasaE_PH_1Pavimento_aparador_antes_depois.jpg`.
  - **No fim do pente fino, o nublado como opção única (seção 16), feito (21/10/26).** Como previsto na regra 13 ("depois da escolha, regerar sem sufixo") e na tabela da seção 15 ("os arquivos das opções ficam no histórico"):
    - **`opcoes_1pav_casae.py`:** sem `--opcao`, faz só o nublado e grava `renders/POE642_CasaE_PH_1Pavimento_v1_final.png` (e `_preview.jpg`), sem sufixo, como o Subsolo e o Térreo. O P&B e as linhas ainda saem quando pedidos (`--opcao pb`, `--opcao linhas`), com o sufixo.
    - **Prancha:** `entrega/POE642_CasaE_PH_1Pavimento_entrega.png`, pelo `rodape_entrega.py --no-quadro` sem `--sufixo`.
    - **PDF único:** `entrega/POE642_CasaE_Plantas_Humanizadas.pdf` (20,5 MB, 3 páginas A3: Subsolo, Térreo e 1º Pavimento), pelo `pdf_entrega.py` só com a config (nome e título da `entrega.pdf`).
    - **Saíram da pasta (ficam no histórico do git):** as pranchas `..._1Pavimento_entrega_{pb,linhas,nublado}.png`, os PDFs `..._opcao_{PB,Linhas,Nublado}.pdf` e as montagens `renders/..._1Pavimento_v1_final_{pb,linhas,nublado}.png` (com as prévias).
    - **Conferência:** a imagem final e a prancha são iguais, px a px, às do nublado depois do item 14; as três páginas do PDF único têm as mesmas imagens do PDF da opção nublado (muda só o título nos metadados).

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
  29. **Terreno hachurado a partir do Térreo final (usuário, 21/10/26: "siga com o terreno hachurado do Subsolo"):** a tarefa deixada no item 64 do Térreo. O lote da hachura (`HACHURA["terreo"]`) já lia `renders/POE642_CasaE_PH_Terreo_v1_final.png`, mas a imagem final do Subsolo não tinha sido refeita depois do pente fino do Térreo.
      - **Fontes fixas:** a escada (`ESCADA`) e o travertino (`TEXTURAS`) tiram trechos do retocado do Térreo, que também mudou no pente fino. Passaram a ler o Térreo aprovado de 15/10 (`TERREO_APROVADO`, `renders/POE642_CasaE_PH_Terreo_v1_retocado_aprovado.png`), que é igual px a px ao retocado que o Subsolo usou até aqui. Com isso, o retocado do Subsolo sai idêntico (0 px).
      - **O que mudou na final:** a borda direita do lote, que acompanha o Térreo final (uns 3 px, x ≈ 3452 a 3462, y ≈ 388 a 611), e o "²" dos 12 rótulos, que agora sai logo depois do "m" pela rotina comum do item 49 do Térreo (antes encostava no "m"). O resto da hachura não muda: o lote é o contorno do que não é branco no Térreo, e o pente fino mexeu dentro dele.
      - **Conferência:** na prancha, 862 px em 18 regiões; a área da imagem é a final, px a px; rodapé igual. A prancha do Subsolo e o PDF único foram refeitos.
      - **Antes/depois:** `renders/POE642_CasaE_PH_Subsolo_terreno_terreo_final_antes_depois.jpg`.
      - **Regra:** vidro em folha contínua no PDF é desenhado sem montantes.
- **Entrega (16/10/26, depois da aprovação do usuário: "prancha e o PDF. aprovado."):** a casa passa a ter três pavimentos, na ordem da Casa A (Subsolo, Térreo, 1º Pavimento).
  - **Config:** o Subsolo entrou na chave `entrega` da `POE642_CasaE/config_bases.json` (título "SUBSOLO", linha 0 do quadro de áreas, base `POE642_CasaE_BASE_Subsolo_v3_texturas_16x9.png`). O Térreo passou à linha 1 e o 1º Pavimento à linha 2. O quadro de áreas tem os três "NÃO INFORMADO", sem total. Em `pdf.ordem`: Subsolo, Térreo e 1º Pavimento; título "Casa E – Plantas Humanizadas (Subsolo, Térreo e 1º Pavimento)".
  - **Pranchas (3840 × 2600 px):** `entrega/POE642_CasaE_PH_Subsolo_entrega.png`, nova. A imagem final, já no quadro comum e com os rótulos, entra com `--no-quadro`, sem realinhar. A do Térreo (realinhada com 128 pontos, erro mediano 0,78 px) e as duas do 1º Pavimento (`_pb` e `_linhas`) foram refeitas só pelo rodapé novo, com a linha do Subsolo no quadro de áreas. Rodapés `entrega/POE642_CasaE_rodape_{Subsolo,Terreo,1Pavimento}.png`.
  - **PDFs (3 páginas A3: Subsolo, Térreo e 1º Pavimento):** `entrega/POE642_CasaE_Plantas_Humanizadas_opcao_PB.pdf` (20,6 MB) e `..._opcao_Linhas.pdf` (18,6 MB). Só a página do 1º Pavimento muda entre as duas opções. Comandos no README dos scripts, em "Pranchas de entrega".
  - **Depois da escolha do cliente** (o 1º Pavimento continua em duas opções): como no 1º Pavimento, rodar o `rodape_entrega.py` da opção escolhida sem `--sufixo` e o `pdf_entrega.py` sem `--prancha`/`--nome`; sai `POE642_CasaE_Plantas_Humanizadas.pdf` com os três pavimentos.
  - **Feito em 21/10/26:** o nublado virou a opção única (seção 16 das regras); a entrega é `entrega/POE642_CasaE_Plantas_Humanizadas.pdf`, com a prancha `..._1Pavimento_entrega.png` (ver "Casa E · 1º Pavimento", no fim do pente fino).

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
    - **madeira:** o deck da piscina, réguas de ~15 cm (**[21/10] medidas de novo: ~20 cm**, 5,12 px a 26 px/m);
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

## Biblioteca de blocos · todas as casas

Pedido do usuário (20/10/26), com um pin do Pinterest: "adicione esse https://br.pinterest.com/pin/653022015002943564/ à nossa biblioteca de blocos a serem utilizados e oferecidos, dentro do escopo do projeto das casas. temos várias opções. quero que você escolha dentro do que está nos pdfs base das casas. e encontre uma cortina para usarmos." O Pinterest não abre desta sessão (proxy 403, DNS), e o usuário mandou as folhas como imagem.

- **Pasta:** `projetos/_blocos/`, a mesma para as cinco casas.
  - `originais/`: as 5 folhas que chegaram como arquivo (`folha_01_cozinha`, `folha_02_estar_madeira`, `folha_03_banho_jantar`, `folha_04_sofas_organicos`, `folha_05_externo_plantas`).
  - `blocos.json`: cada bloco com a folha, a caixa em px, a medida real, a categoria e onde ele entra nos PDFs; o que ficou de fora e por quê.
  - `blocos.py`: recorta tudo, desenha a cortina e faz a cartela (`python3 blocos.py`).
  - `recortes/`: 60 blocos em PNG com transparência, na resolução da folha, mais as duas cortinas.
  - `cartela_blocos.jpg`: os blocos por categoria, na medida real, 2 x a escala da prancha (60 px/m).
- **Escolha:** só entram peças que têm correspondente no mobiliário dos PDFs base, conferido nas camadas ARQ_MOBILIÁRIO, ARQ_LAYOUT HUMANIZAÇÃO, ARQ_LOUÇAS E METAIS e ARQ_MARCENARIA das 12 plantas:
  - **estar:** sofás orgânicos, curvos e retos, poltronas (em X e de leitura), mesas de centro e laterais, um tapete curvo e um estar com tapete;
  - **jantar e ilha:** mesas de 8, 6 e oval de 6, mesa redonda de 4 (nos PDFs, 6 lugares), ilha com banquetas, banqueta;
  - **cozinha:** cooktops de inox (4, 5 e 5 bocas de 90 cm, como os eletrodomésticos) e pretos para o gourmet, cubas de inox e de granito;
  - **banho:** vasos sanitários, cubas de apoio, bancada com cuba de pedra, banheira oval (banho master do 1º Pav. da Casa E);
  - **escritório:** escrivaninhas e aparador; **externo:** mesa de teca de 8, mesa redonda de teca, poltrona de rattan, sofá de 2 lugares; **paisagismo:** 9 plantas e jardineiras.
  - **Extras** (oferecidos, não estão nos PDFs): três guarda-sóis e um sofá de couro caramelo.
- **Fora:**
  - o banco de teca, que tem a marca d'água "dreamstime" (banco de imagens);
  - a bancada gourmet de inox (o layout é o do PDF e já está nos renders);
  - o sofá e as poltronas rosa (fora da paleta);
  - coifas, geladeira, petiscos e cafés (não aparecem em planta);
  - a grama (a aprovada é a opção B).
- **Recorte (sem IA generativa):** o fundo da folha (branco, cinza 232 ou o xadrez de "PNG falso") ligado à borda da caixa e os bolsões de fundo liso entre mesa e cadeiras são fundo certo; a sombra da foto ligada a ele, fundo provável (o bloco sai sem sombra e recebe a do render); o GrabCut do OpenCV decide o resto pela cor e pelas bordas. Nas louças e pedras brancas como o fundo, o contorno vem da envoltória convexa (`convexo`) ou de uma área marcada como peça (`certo_ret`, `certo_elipse`). Conferido sobre fundo escuro, verde e claro.
- **Para aplicar:** `bloco(id, px_por_m)` devolve cor e alfa na medida real; a medida do JSON se ajusta ao bloco do PDF na hora de aplicar.
- **Cortina:** nenhuma folha traz cortina, e nos PDFs ela é a linha ondulada junto aos vidros (quartos do 1º Pav. A e E, Térreo B). Por isso é desenhada em `cortina(comp_m, px_por_m, aberta=False)`:
  - o trilho em linha cinza fina junto ao vidro;
  - o tecido de linho cru (RGB 233, 227, 215) em prega wave de 14 cm de passo e 3,5 cm de amplitude, com luz nas cristas e uma sombra leve para dentro;
  - `aberta=True`: o tecido franzido em dois maços nas pontas (18% do vão cada) e só o trilho no meio.
- **Folhas que faltam:** as 6 folhas mandadas no meio da execução chegaram só como imagem na conversa, não como arquivo, e não dá para recortá-las. Estão nelas as camas com criados, o sofá em L, o guarda-roupa, as máquinas de lavar, os carros e o cooktop de 4 bocas preto. Basta reenviá-las numa mensagem nova.
- **Estado:** nada aplicado aos renders. A cartela aguarda a aprovação do usuário.

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

## Casa A · pente fino pelas regras (21/10/26)

Pedido do usuário: "siga com a Casa A" (a ordem da seção 17 das regras: Casa E, Casa A, Casa B, Casa C, Casa D). Cada prancha atual foi conferida trecho a trecho contra o PDF e as regras (`POE642_REGRAS.md`, com a seção 16, o inventário). Os mapas numerados saem do `conferencia_casaa.py --pente-fino`: `renders/POE642_CasaA_PH_{Subsolo,Terreo,1Pavimento}_pente_fino_mapa.jpg`. Nada foi retocado ainda; a lista aguarda a confirmação do usuário (seção 1 das regras).

- **Subsolo (10 itens):**
  1. só o Subsolo, com o resto do terreno hachurado (R2): saem o deck, a piscina, o spa, a escada larga e as espreguiçadeiras, que são do Térreo;
  2. o gramado abaixo da escada do deck (item 13 de 19/10): a proposta é que fique, com a grama da referência. A confirmar;
  3. escada do deck, 11 degraus (R14): sobe da circulação (o "S" do PDF); linhas nos bocéis, triângulo no 1º degrau apontando para a esquerda, degraus 9 a 11 esmaecidos e tracejados;
  4. portas sem arcos (R3): as 5 do PDF;
  5. portas, vidros e janelas finos: a porta de vidro de correr da circulação interna (hoje um traço preto grosso), a janela entre o depósito e a academia, os vidros da sauna sem montantes e a folha da porta do depósito;
  6. Bege Bahia como a referência (seção 18) na circulação externa, na interna e no depósito;
  7. travertino na escala: o do Térreo da Casa A, no hall, na sauna, na antessala e nos banhos;
  8. shafts brancos com o X tracejado; os três retângulos da DOC_LINHAS E PROJEÇÕES que faltam (paredes de cima e da direita do depósito, parede de baixo da academia). A confirmar o que são;
  9. soleiras (R13), porta a porta;
  10. o "²" dos 9 rótulos pela regra de 20/10.
  - **Conformes:** academia (réguas de ~20 cm e os aparelhos do PDF), banho de serviço, cubas, divisória, boxes, banco da sauna; não há pilares no PDF.
- **Térreo (16 itens):**
  1. as quatro escadas com linhas e triângulo (R14): a interna em U, a caracol, a larga do deck (degraus 12 a 19; o sentido a confirmar, proposta: sobe do deck) e a do deck para o Subsolo (desce);
  2. rótulos em branco no granito (R6) e o "²";
  3. carros prata, alinhados e iguais (R12);
  4. projeções da cobertura, do pergolado e da laje superior em tracejado bem visível (R8, R9);
  5. vidros finos: o da varanda para as salas e o do hall (hoje um tubo cinza com montantes);
  6. armários até o teto em marcenaria areia, sem a diagonal (cozinha, área de serviço, quarto do motorista);
  7. grama na escala da referência;
  8. deck de madeira em réguas de ~15 cm, na madeira da referência;
  9. Bege Bahia como a referência (entorno da piscina, pátio, hall externo, pisantes);
  10. granito marrom no desenho e no tom da referência;
  11. pedra portuguesa em leque, no tom da foto;
  12. vegetação da biblioteca, no tamanho real, só dentro do lote (a do motor está fora de escala e passa do lote);
  13. a mesa de jantar oval (item 4 da conferência de 19/10);
  14. o escritório com a cadeira de escritório em cima e as duas de visita embaixo (item 6);
  15. o banho da varanda com o chuveiro e o box no lugar da bacia (item 7);
  16. soleiras (R13), porta a porta.
  - **Conformes:** pilares, portas sem arcos (feito em 19/10; o item 10 da conferência deixa de valer), sala de estar, estar sob a projeção, lavabo, bancadas, inox, tanques, jardim, motorista, piscina em Barlavento.
- **1º Pavimento (16 itens):**
  1. o Térreo nublado em volta (seção 11), com a final do Térreo depois do pente fino;
  2. portas sem arcos (R3): os 11 do PDF;
  3. escadas (R14): a em U desce daqui, com o triângulo no topo (degrau 20); a caracol, só o trecho do pavimento cheio, com o triângulo;
  4. guarda-roupas com cabides (R11) nos closets 3, 2, 1 e master. A cor a confirmar (proposta: a da Casa E, bege dentro, ocre na borda e o cabideiro);
  5. armários até o teto em marcenaria areia (circulação, sala íntima, quarto de serviço);
  6. bancos ao pé das camas nas suítes 3, 2, master e 1 (itens 2 a 5 da conferência);
  7. criados-mudos redondos na suíte 3 (item 1);
  8. cama de solteiro e criado-mudo no quarto de serviço (item 6);
  9. banheira oval no banho master (item 7);
  10. cortinas de linho da biblioteca, com o trilho de parede a parede, nas quatro suítes;
  11. vinílico na escala da referência;
  12. Bege Bahia das quatro varandas como a referência;
  13. projeções da cobertura e do pergolado em tracejado;
  14. portas de vidro de correr finas, em dois planos, das suítes para as varandas;
  15. soleiras (R13), porta a porta;
  16. o "²" dos 22 rótulos.
  - **Conformes:** vazios brancos com o X, sala íntima, banhos, rótulos fora dos objetos.
- **Ordem proposta:** Térreo, Subsolo e 1º Pavimento, porque o terreno hachurado do Subsolo e o entorno nublado do 1º Pavimento saem do Térreo final.
- **Confirmação (21/10/26):** "confirmado, pode seguir pela ordem proposta". As quatro propostas valem: o gramado do Subsolo fica; os retângulos da DOC_LINHAS entram em traço cinza fino, como no PDF; a escada larga do Térreo sobe do deck (triângulo no degrau 12); os guarda-roupas do 1º Pavimento como na Casa E (bege dentro, ocre na borda, cabideiro).
- **Ciclo de cada item:** `ajustes_casaa.py <Pavimento>`, `rotulos_casaa.py <Pavimento>`, `rodape_entrega.py --no-quadro --render <Pavimento>=...` e `pdf_entrega.py`; conferência nos ajustes e na prancha (só a região do item muda, rodapé igual). Antes de começar, o ciclo foi rodado sem mudança: os ajustes saíram iguais, px a px, e na prancha mudaram só os "²" (rotina de 20/10).
- **Térreo, item 2, rótulos brancos no granito (R6), feito.** No `rotulos_casaa.py`, `cor_granito=R1.ROTULOS["branco"]`, a cor da Casa E, e o Q. MOTORISTA (cor dada no ajuste) também em branco. Junto, o "²" logo depois do "m" em todos os 28 rótulos. Feito antes do item 1, porque toda nova rodada dos rótulos muda os "²".
  - **Conferência:** na imagem com ajustes, nada; na prancha, só os rótulos (4.721 px em 25 regiões: os 8 do granito inteiros e os "²" dos outros); rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_rotulos_granito_antes_depois.jpg`.
- **Térreo, item 1, escadas com linhas e triângulo (R14, seção 5), feito** (`ajustes_casaa.py`):
  - **Interna em U** (`ESCADA_INT["r14"]`): nos degraus 1 a 7, a linha suave em cada bocel (a da Casa E: 20% mais escuro em 0,55 pt), com a sombra de subida que já havia; do 8º em diante, os bocéis e o contorno tracejados (a projeção, no traço da Casa E); a linha de corte deixa de ser desenhada (seção 5); o triângulo no degrau 1 (o "S" do PDF), apontando para a direita.
  - **Caracol** (`CARACOL["r14"]`): a linha suave nos bocéis dos degraus 1 a 7; os espelhos acima do corte tracejados, a 55% no granito escuro (o cinza claro inteiro marcava demais); o triângulo no degrau 1, apontando para a subida (anti-horário), a 70% do tamanho da regra, porque o degrau de 18° não o comporta inteiro.
  - **Do deck para o Subsolo** (`ESCADA_DECK`, em `escadas_externas_r14`): no Térreo o PDF marca "D" junto ao deck. Os bocéis e a linha do meio, que o motor fez em traço escuro, saem (mediana de 7 px em x e de 5 px em y, só dentro da escada, de 1230,9 a 1299,0 pt). Entram os bocéis em linha suave com a sombra curta, viva do deck até o corte do PDF do Subsolo (a diagonal no 9º degrau, prolongada) e esmaecida depois (0,65; com o 0,45 da Casa E ficava uma mancha branca no Bege Bahia), e o triângulo no topo, apontando para a descida.
  - **Larga, do deck ao pátio** (`ESCADA_LARGA`): os sete blocos desencontrados do ARQ_CONTRAPISO (degraus 12 a 18) e o pátio (19). O bocel de cada degrau é o L do bloco de cima sobre o de baixo, com a linha suave e a sombra curta; o triângulo no degrau 12, apontando para a direita (sobe do deck, como confirmado).
  - **Conferência:** na imagem com ajustes e na prancha, só as quatro escadas mudaram; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_escadas_r14_antes_depois.jpg`.
- **Térreo, item 3, carros (R12), feito** (`ajustes_casaa.carros_a` com `CARROS_A["r12"]`, função `carros_r12_a`). Substitui o pedido de 19/10 (cada carro numa cor e desalinhados), como na Casa E.
  - Os três carros saem como antes (o granito tecido dos vãos, na luz do lugar).
  - **Modelo:** o carro da esquerda do render (o branco). A luminância dele vai aos quantis do carro prata do Térreo da Casa E (5, 25, 50, 75 e 95%: 63, 101, 163, 189 e 214), no tom dele, um cinza levemente frio; as lanternas ficam.
  - **Escala e posição:** 4,70 m de comprimento e 1,85 m de carroceria (148 x 58 px; o modelo tinha 141 x 54), sem giro, no centro de cada carro do PDF (ARQ_LAYOUT HUMANIZAÇÃO: x 2028,6, 2186,7 e 2347,2 pt), os três na mesma linha (y 1637,3 pt, a média dos três), com a sombra curta.
  - **Conferência:** na imagem com ajustes, só os três carros; na prancha, os carros (o rótulo GARAGEM continua livre entre o primeiro e o segundo); rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_carros_r12_antes_depois.jpg`.
- **Térreo, item 4, projeções (R8, R9), feito** (`ajustes_casaa.projecoes_a`, config `PROJECOES_A`, o último item do Térreo, para ficar por cima de tudo).
  - **Onde estão no PDF da Casa A:** as das notas "PROJ. COBERTURA" estão na ARQ_CONTRAPISO, em tracejado: o L da laje, de 1290 a 2381 pt em x e de 511 a 1815 pt em y, com o braço de baixo até 1038 pt (a partir de 1344 pt) e a linha de 1290 pt descendo até 1860 pt. A "PROJ. DA LAJE SUPERIOR" está na DOC_LINHAS E PROJEÇÕES, em volta da caracol. O retângulo grande da DOC_LINHAS (pt 303 a 2965 x 539 a 1787) é o afastamento obrigatório, e as linhas de fora são a divisa: não são projeções e ficam como o motor fez.
  - **Como:** no traço das projeções do Térreo da Casa E (8,5 pt de traço, 4,25 de vão, 0,55 px, cinza 150, força 0,85), por cima de tudo, menos das paredes pretas. Antes só havia trechos sobre a grama.
  - **Ficam:** os X do pavimento superior na varanda, o pergolado e a claraboia, que já estavam no render.
  - **Conferência:** na imagem com ajustes, só as linhas das projeções; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_projecoes_antes_depois.jpg`.
- **Térreo, item 5, vidros finos (seções 4 e 18), feito** (`ajustes_casaa.vidros_finos`, config `VIDROS_A`, antes das projeções). O motor fez dois "tubos" cinza grossos, com nós escuros (montantes).
  - **Entre a varanda e as salas:** no PDF (ARQ_PAREDE) são quatro portas de vidro de correr, cada uma com duas folhas de 1,4 pt lado a lado, em dois planos (585,8 a 1269,5 pt). O tubo sai (`esquadria_limpar` da Casa E: cada coluna da faixa recebe o piso do seu lado, em espelho, com os X tracejados da varanda continuando) e as 15 peças brancas do PDF entram finas, como o item 8 do pente fino do Térreo da Casa E (`esquadria_desenhar`: o vidro claro e o contorno fino; os batentes em quadradinhos).
  - **Entre o hall interno e o externo:** entre os dois batentes o PDF não tem vidro; é o vão da porta pivotante, com a folha aberta. O tubo sai e o piso de cada lado continua (o travertino do hall interno e o Bege Bahia do externo); os batentes ficam.
  - **Conferência:** na imagem com ajustes e na prancha, só os dois trechos; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_vidros_antes_depois.jpg`.
- **Térreo, item 6, armários até o teto (seção 7), feito** (`ajustes_casaa.armarios_teto`, config `ARMARIOS_A`, depois das escadas externas e antes dos vidros). O motor fez os quatro armários do PDF (os retângulos com diagonal da DOC_LINHAS E PROJEÇÕES: na cozinha, junto à parede de cima e ao lado dos eletrodomésticos; na área de serviço; no quarto do motorista) em lilás, com a diagonal desenhada, e jogou no granito a sombra de móvel baixo.
  - **Marcenaria:** a dos armários até o teto aprovados da Casa D (o tom areia do painel da Casa C com o veio do render): o trecho liso de um deles (`POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v4.png`, x 1128 a 1143, y 740 a 797), com o veio no comprido de cada peça (deitado nos da cozinha, em pé nos outros), espelhado até cobrir, sem a diagonal. Entra no retângulo do PDF, menos as paredes pretas do render (a da esquerda do armário de cima da cozinha está 3,5 px mais grossa que no PDF e fica).
  - **Contorno:** linha fina (0,4 px, cinza-escuro) na face do PDF, só nas faces livres, como os armários da cozinha da Casa E. A borda escurecida da Casa D, que lá era sobre o vinílico, no granito escuro virava uma faixa intermediária e a borda parecia borrada.
  - **Sombra:** sai do granito como na Casa D. Em cada face com piso, o perfil (por canal, mediana ao longo da face) contra o patamar logo depois dela: 45% embaixo do armário de cima da cozinha, 51% à esquerda e 40% embaixo do do motorista (que desce além do canto e entra à esquerda dele). As linhas que não são sombra (o traço preto do motor à direita do armário dos eletrodomésticos, a sobra lilás de meio px além do PDF) repetem a primeira linha válida, já sem sombra.
  - **Bancada da área de serviço:** o braço da bancada dos tanques acima do armário (ARQ_BANCADAS, 1499,6 a 1530,8 pt; uma peça branca no PDF) também estava lilás, como um armário. Entra no quartzo das bancadas, como a dos tanques (sombra curta e contorno fino).
  - **Conferência:** na imagem com ajustes e na prancha, só os quatro armários (e o braço da bancada); rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_armarios_antes_depois.jpg`.
- **Térreo, item 7, grama na escala da referência (R1, R4), feito** (`ajustes_casaa.grama_escala`, config `GRAMA_A`, depois dos armários). Como o item 42 do Térreo da Casa E, na opção escolhida lá (B): o desenho da grama da biblioteca, na escala (31,46 px/m), no verde do próprio render, com a luz larga do lugar e as sombras das plantas (`texturas_escala.mascara_grama` e `trocar_grama`). A grama do motor tinha grão fino de carpete e manchas fora de escala.
  - **Gramado:** a base da Casa A tem o lote em branco (o gramado é do motor). Vale o branco da base levada à imagem, dentro do lote (do muro de cima ao de baixo; da linha preta da esquerda até onde o verde acaba, à direita), em manchas grandes e verdes no render: os brancos dos móveis, dos carros e da floreira do lavabo ficam de fora. O jardim interno da escada fica como está, porque a escada esmaecida está desenhada sobre a grama dele.
  - **Plantas:** as da Casa A são verde-sálvia, de cor perto da da grama, e a grama é mais clara que a da Casa E. O que separa as duas é o desenho das folhas: energia de 1 a 3 px em torno de 5 nas plantas, contra 1,7 na grama. Por isso `mascara_grama` ganhou parâmetros (os padrões são os números da Casa E): aqui `est_lim` 4 (lá 9), a faixa de luz da grama de 35 a 125 (lá até 102) e o verde até 130 (lá 115). Junto às bordas do gramado, onde `mascara_grama` não procura planta (a cor se mistura com a do piso), as folhas que encostam numa planta também ficam. As plantas não mudam (a vegetação é o item 12).
  - **Tracejados:** os do motor sobre a grama ficam: o afastamento obrigatório, em traço escuro (até 21 px fora da linha do PDF), e trechos da projeção da cobertura (a 2 px da do item 4). São achados no próprio render como linhas retas, finas e longas, escuras, a mais de 8 px da borda do gramado (junto às bordas, a sombra dos pisos e dos muros dava linhas falsas) e longe das plantas. Ficam seis (o afastamento em x 257 e 1711 e em y 854, em dois trechos, e a cobertura em x 1388 e y 147), com contraste de 16 a 22, contra 6 a 9 das falsas. Cada um segue mais 40 px nas pontas, e os px do traço voltam depois da troca. As projeções do item 4 continuam por cima.
  - **Conferência:** na imagem com ajustes e na prancha, só o gramado (483 mil px de grama nova); plantas, pisos, deck, pedra portuguesa e o jardim interno ficaram; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_grama_antes_depois.jpg`.
- **Térreo, item 8, deck de madeira (R4), feito** (`ajustes_casaa.deck_referencia`, config `DECK_A`, depois da grama). O motor fez as réguas num marrom avermelhado (RGB ~170, 124, 93), com as juntas fundas. A madeira passa à da referência (`_texturas/madeira.jpg`, o deck da piscina da planta de referência: RGB ~188, 157, 130, réguas contínuas, de juntas finas).
  - **Escala:** já batia. Medidas por FFT, as réguas da referência têm ~20 cm (5,12 px a 26 px/m) e as do render, ~19 cm. Os "~15 cm" da nota da biblioteca, das regras e do mapa do pente fino eram uma conta errada; as três notas foram corrigidas (com a data), e vale a régua da referência, como diz a R4.
  - **Como:** o deck é a mancha da madeira da base (#AE8863, com o traço das réguas, #8C6A4A). Régua a régua, deitadas como no PDF, em 4x: cada régua do deck é uma régua inteira da foto (de uma junta à seguinte; são 7), sorteada, com deslocamento e espelho ao acaso, na largura da referência. Sem quilting: as emendas dos retalhos (`textura("madeira")`) liam como faixas atravessando as réguas. A luz larga do lugar e as sombras (dos degraus, da borda da piscina) ficam, como na grama.
  - **Conferência:** na imagem com ajustes e na prancha, só o deck; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_deck_antes_depois.jpg`.
- **Térreo, item 9, Bege Bahia como a referência (seção 18), feito** (`ajustes_casaa.bege_referencia_a`, config `BEGE_A`, antes das escadas externas). O entorno da piscina, o pátio de cima, a faixa junto aos brises, o hall externo, os cinco pisantes e os degraus das escadas externas (o #E8E8E8 da base) estavam no Bege Bahia das varandas do 1º Pavimento, claro e rosado (RGB ~225, 209, 198).
  - **Como:** o item 43 do Térreo da Casa E, com os números de lá (`retoque_terreo_casae.BEGE`). Os pontinhos escuros pequenos do motor viram a luz do lugar; depois o desenho da biblioteca entra inteiro, na escala (31,46 px/m), no tom da foto (RGB 230, 211, 186), com a luz do lugar. As sombras dos móveis ficam; o que foge da luz (móveis, portas, traços) fica como está.
  - **Mancha:** o #E8E8E8 da base, sem os riscos finos (os contornos dos carros), fechada em 5 x 5 onde o render é piso claro. As linhas da base (o arco e a folha da pivotante no hall externo) recortavam a mancha, e o arco ficava no tom antigo. A grama entre os pisantes não entra.
  - **Anel:** o `retexturizar` deixa um anel de 2 px no tom antigo em volta do que foge da luz. Ele vira o piso novo de perto (média só do piso novo, sem a cor do objeto), e só onde há piso novo bastante em volta (sem isso, os cantos estreitos ficavam pretos).
  - **Ordem:** antes das escadas externas (item 1), que desenham os bocéis por cima, e dos vidros (item 5), que levam o piso de cada lado para o vão do hall.
  - **Conferência:** na imagem com ajustes e na prancha, só o Bege Bahia; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_bege_antes_depois.jpg`.
- **Térreo, item 10, granito marrom (seção 3), feito** (`ajustes_casaa.granito_referencia_a`, config `GRANITO_A`, depois do deck). O granito do render estava quase preto (RGB ~88, 65, 60), com a grade de manchas que o motor repete e pontos claros.
  - **Como:** a rotina do granito do Térreo da Casa E (`retoque_terreo_casae.granito_tom`, com as constantes de lá, `GRANITO_TOM`). Saem os pontos claros pequenos do motor (621) e a grade de manchas de média escala (longe de objetos e paredes; as sombras ficam). Entra o desenho e o tom da referência do usuário (`fontes_procedurais.granito_referencia`, base RGB ~118, 89, 69), com a luz do lugar (`texturas_escala.trocar_granito`). Os traços do PDF e os cinza neutros ficam, com a troca de tom na fração de granito que têm. O peso de granito (cor e luz perto da mediana) deixa de fora armários, inox, bancadas, carros, portas e a caracol.
  - **Mancha:** o #BFA79E da base, com os traços finos fechados e os buracos de até 20 mil px preenchidos. Os carros do PDF são buracos maiores que os carros da R12, e o anel entre os dois ficava escuro, no tom antigo, em volta do terceiro carro.
  - **Rótulos:** no `rotulos_casaa.py`, o limite de luz do granito passa a valer por pavimento; no Térreo, 125 (`granito_lum_max`). Com o granito mais claro, o limite de 95 deixava os rótulos da garagem, da despensa e do motorista em cinza; agora voltam ao branco (R6). Subsolo e 1º Pavimento seguem com 95.
  - **Conferência:** na imagem com ajustes e na prancha, só o granito (cozinha, área gourmet, área de serviço, despensa, gás, garagem e motorista) e os rótulos sobre ele; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_granito_antes_depois.jpg`.
- **Térreo, item 11, pedra portuguesa (seção 3), feito** (`ajustes_casaa.pedra_leque`, config `PEDRA_A`, o último item do Térreo; e `pedra_final`, na final). O motor fez pedras caramelo de 12 a 15 cm no acesso de veículos e na área de serviço descoberta.
  - **Como:** o item 47 do Térreo da Casa E, com as constantes de lá (`retoque_terreo_casae.PEDRA`) e `texturas_escala.trocar_pedra_portuguesa`, fonte "leque". São pedras de 7 cm assentadas em leque, com juntas claras e as cores sorteadas das pedras da foto, sobre a luz relativa e as sombras do lugar. A franja da borda (caramelo misturado com a grama) recebe a troca de tom.
  - **Área:** a pedra da base (#B98A55, com folga), só onde o px ainda é o caramelo do motor. As plantas, os portões, as folhas do gás e a projeção da cobertura ficam; por isso o item vem depois das projeções.
  - **Linhas:** os traços que o motor fez sobre o caramelo (o X tracejado da área descoberta e o afastamento) saíam com ele. Entram as linhas da DOC_LINHAS E PROJEÇÕES do PDF por cima da pedra nova, em cinza-escuro fino, tracejadas como no PDF.
  - **Na final:** como na Casa E, as pedras são desenhadas de novo nos 3840 px, onde as de 7 cm têm ~4 px e se leem (no ajuste de 2000 px, ~2 px). A máscara do ajuste (`renders/POE642_CasaA_PH_Terreo_pedra_mascara.png`) vai ao quadro pelo mesmo afim da imagem (`rotulos_casaa.no_quadro_fixo(..., mascara=)`), e `pedra_final` desenha nela as pedras e as linhas, antes dos rótulos.
  - **Conferência:** na imagem com ajustes e na prancha, só a pedra; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_pedra_antes_depois.jpg`.
- **Térreo, item 12, vegetação (seção 10; R1, R4), feito** (`ajustes_casaa.vegetacao_a`, config `VEG_A`, depois da grama). As folhagens do motor estavam fora de escala (folhas de 1 a 1,3 m) e passavam do lote nos quatro cantos (sobre o muro e no branco de fora) e sobre a pedra do acesso.
  - **Como:** a opção A do Térreo da Casa E (item 53 de lá: `retoque_terreo_casae.VEGETACAO`, `sprite_referencia` e `pousar_planta`). As árvores, arbustos e palmeiras da planta de referência (`_texturas/vegetacao`) entram no tamanho real, o maior que cabe primeiro, com a copa dentro do verde: nada sai do lote nem dos pisos. São 77 plantas nas cinco manchas grandes.
  - **Manchas:** as de planta do gramado do item 7 (`gramado_plantas`, achadas na imagem aprovada), só as de 5 mil px ou mais: os quatro cantos e o jardim lateral. As pequenas, de até 600 px, são sombra de parede e de degrau e ficam.
  - **Folhas fora do verde:** só as verdes ligadas às manchas por px verdes. Uma parede, um caixilho ou a água cortam a ligação; a rotina de restos da Casa E pegava a borda do spa, o caixilho do escritório e um vaso dentro da sala.
  - **Sobre os pisos:** as folhas e a sombra delas (3 px em volta) e, a até 1,3 m das manchas, os fragmentos de folha e as sombras soltas viram o material da base copiado de 12 a 24 px ao lado (`copiar_material`, como na Casa E). Na pedra, o que não é o caramelo do motor (o item 11 o troca depois); no Bege Bahia, o cinza ou o verde, fora os traços finos da base no mesmo cinza (o contorno dos carros ficava pontilhado) e a sombra das paredes da casa, a até 6 px delas (a faixa embaixo de um pisante virava bege num trecho só). O inpaint misturava a grama e deixava uma faixa suja na curva da pedra. As linhas da DOC_LINHAS (os pisantes, o afastamento) ficam.
  - **Lote:** fora dele, o branco de fora; sobre o muro (as linhas pretas de cima, de baixo e da esquerda), o perfil da própria linha num trecho limpo.
  - **Grama:** a do item 7 sob as manchas, com o mesmo desenho (a mesma textura, recorte e semente: sem emenda) e a luz larga da grama em volta.
  - **Ficam:** a floreira do lavabo (JARDIM, 4,79 m²) e o jardim interno da escada, que não são do gramado.
  - **Conferência:** na imagem com ajustes e na prancha, só a vegetação e o que estava em volta dela (os pisos, o muro e o branco de fora); rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_vegetacao_antes_depois.jpg`.
- **Térreo, item 13, mesa de jantar oval (item 4 da conferência de 19/10), feito** (`ajustes_casaa.mesa_oval`, config `MESA_A`, depois dos vidros). O tampo do PDF (ARQ_MARCENARIA, a peça branca de 1717,9 a 1888,0 x 1123,2 a 1191,2 pt) é oval, de pontas em semicírculo, com 3,00 x 1,20 m. O do motor era retangular chanfrado e menor (2,86 x 1,08 m).
  - **Cadeiras:** o PDF tem 8 (3 de cada lado e uma em cada cabeceira), e não 10, como dizia o mapa do pente fino (texto corrigido em `conferencia_casaa.py`; a imagem do mapa fica a de 21/10). As 8 do render já estão onde o PDF as põe e ficam.
  - **Tampo:** refeito no contorno do PDF, em 8x, com a madeira do próprio render estendida linha a linha em espelho (o veio corre no comprido). Fica por cima da frente das cadeiras, como no PDF (1 a 3 px).
  - **Piso e sombra:** onde o tampo velho cobria e o novo não cobre, o piso vem do entorno. A sombra curta da mesa no piso (a do motor, medida em volta: deslocada -3, +2 px, desfoque de 3 px, força 0,5) passa do contorno velho ao novo pela razão entre as duas; nas cadeiras, nada muda.
  - **Conferência:** na imagem com ajustes e na prancha, só a mesa e a sombra dela; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_mesa_jantar_antes_depois.jpg`.
- **Térreo, item 14, escritório (item 6 da conferência de 19/10), feito** (`ajustes_casaa.escritorio_cadeira`, config `ESCRITORIO_A`, depois da mesa de jantar). No PDF (ARQ_LAYOUT HUMANIZAÇÃO), a mesa tem a cadeira de escritório em cima, no centro, com o assento metido sob o tampo, e as duas de visita embaixo. O motor pôs duas cadeiras iguais em cima e duas embaixo.
  - **As de cima saem**, com as sombras. O travertino corre em faixas horizontais: cada linha volta entre o piso logo à esquerda e logo à direita dela, com o grão de um trecho limpo do escritório.
  - **A cadeira de escritório** entra no contorno do PDF (0,62 x 0,59 m), peça a peça: o assento, a faixa do encosto e os dois braços. É grafite, com o volume e o vinco das poltronas do estar sob a projeção e a sombra curta delas, e o tampo da mesa fica por cima. O pino atrás do encosto e as alavancas dos lados (1 a 2 px nesta escala) ficaram de fora: na primeira prova, liam como as alças de uma panela.
  - **As de baixo ficam:** já estão no lugar das duas de visita do PDF. No PDF elas abrem 10° para cada lado; no render, ficam retas.
  - **Visto de passagem, fora do item:** junto à poltrona do canto, o PDF tem duas mesinhas redondas de 30 cm, sobrepostas; o render, uma só, maior. Fica como está.
  - **Conferência:** na imagem com ajustes e na prancha, só a faixa acima da mesa do escritório; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_escritorio_antes_depois.jpg`.
- **Térreo, item 15, banho da varanda (item 7 da conferência de 19/10; seção 6), feito** (`ajustes_casaa.banho_varanda`, config `BANHO_VARANDA`, depois do escritório). No PDF (ARQ_LOUÇAS E METAIS), o vaso fica em cima (o render já o tem) e, embaixo, o box: duas folhas de vidro de correr desencontradas, da parede da esquerda até 0,87 m, com o trilho tracejado; e o chuveiro de parede, na parede da direita: a ducha quadrada de 20 cm, o braço e a canopla. O motor pôs uma bacia branca arredondada no lugar do chuveiro e fez o trilho como uma faixa pontilhada, sem o vidro.
  - **Saem:** a faixa pontilhada (cada coluna entre o piso logo acima e logo abaixo dela, com o grão do piso abaixo) e a bacia, com a sombra. No lugar da bacia, cada linha recebe o piso da mesma linha mais à esquerda, no tom de cada coluna; a sombra junto à parede da direita fica.
  - **Entram,** como no banho de serviço do Subsolo (item 1 de 19/10): as duas folhas do box (`vidro_box`, 1,3 pt cada, empilhadas) e o chuveiro (`chuveiro`: a placa da Casa A, o braço cromado do centro da ducha à parede e a canopla), nas medidas do PDF.
  - **Conferência:** na imagem com ajustes e na prancha, só o box e o chuveiro do banho da varanda; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_banho_varanda_antes_depois.jpg`.
- **Térreo, item 16, soleiras (R13), feito** (`ajustes_casaa.soleiras_a`, config `SOLEIRAS_A`, depois do banho da varanda). As 13 portas de giro do PDF (os arcos da ARQ_PAREDE, fora a porta camarão) foram conferidas uma a uma, numa folha de recortes do PDF ao lado do render. A soleira é o vão da porta na espessura da parede deixado em branco no PDF; onde o piso de um dos lados atravessa o vão, não há.
  - **Com soleira no PDF (4):**
    - escritório e lavabo: o vão branco da ARQ_PAREDE; no render, o travertino atravessava;
    - gás, porta de duas folhas: o vão branco; no render, o granito do item do gás de 19/10 vinha até a face de fora, com a última linha do trecho copiado escura (não era soleira de propósito);
    - jardim, para a área descoberta: o vão sem parede, branco; no render, uma faixa clara e outra branca.
  - **Sem soleira (9):** área de serviço, despensa, motorista, banho da varanda, WC, pivotante do hall e as três da garagem e da área de serviço. O piso de um dos lados atravessa o vão no PDF e no render: nada a mudar.
  - **Como:** igual às soleiras do Térreo da Casa E (item 52 de lá): o vão exato do PDF em Bege Bahia na escala (o desenho da biblioteca, no tom do item 9), com as duas faces da parede (os lados compridos) em traço cinza fino.
  - **Conferência:** na imagem com ajustes e na prancha, só os quatro vãos; rodapé igual. Prancha do Térreo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_soleiras_antes_depois.jpg`.
- **Térreo do pente fino fechado (21/10/26):** os 16 itens do mapa estão feitos. O próximo é o Subsolo (10 itens), cujo terreno hachurado sai do Térreo final, e depois o 1º Pavimento (16 itens).
- **Pergunta do usuário durante o item 16 (21/10/26):** "O piso marrom granito será atualizado? A madeira do deck também precisa estar na escala, ok?". Os dois já estavam feitos: o granito no item 10 (desenho e tom da referência, na escala) e o deck no item 8 (réguas de ~20 cm da referência). Os antes e depois foram reenviados. O Subsolo (hachurado) e o 1º Pavimento (nublado) herdam os dois do Térreo final.
- **Subsolo do pente fino (usuário, 21/10/26: "pode seguir com o Subsolo").** O ciclo é o mesmo do Térreo (`ajustes_casaa.py Subsolo`, `rotulos_casaa.py Subsolo`, prancha e PDF).
- **Subsolo, item 10, o "²" dos rótulos, feito primeiro.** A prancha do Subsolo ainda não tinha passado pela rotina comum dos rótulos de 20/10 (o "²" logo depois do "m"; antes ele encostava no "m"). Rodado o ciclo sem nenhuma mudança de código: a imagem com ajustes saiu igual px a px, e na prancha mudaram só os 8 rótulos com área (o elevador não tem); rodapé igual. Com isso, a base dos outros nove itens fica limpa.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_m2_antes_depois.jpg`.
- **Subsolo, item 1, só o Subsolo com o terreno hachurado (R2, seção 11), feito** (`ajustes_casaa.so_subsolo` e `subsolo_hachurado`, config `SUBSOLO_R2`; no `rotulos_casaa.py`, a chave `pegada` do Subsolo). A imagem do Subsolo trazia, esmaecidos, o deck, a piscina, o spa, a escada larga e as espreguiçadeiras do Térreo (o PDF do Subsolo os desenha em cinza).
  - **Pegada (no ajuste):** os pisos e as paredes do Subsolo no PDF: as peças cheias da ARQ_CONTRAPISO e da ARQ_PAREDE dentro da caixa do Subsolo (de 900 a 2400 x 1040 a 1800 pt), 406 peças, com a circulação externa. As do Térreo ficam à esquerda e acima dessa caixa. Entram também a escada do deck (a caixa da ARQ_ESCADAS E RAMPAS) e o gramado abaixo dela (o verde do item 13 de 19/10; confirmado em 21/10: fica). A pegada é fechada em 5 x 5, para as costuras de 1 a 2 px entre o gramado, a escada e a circulação não abrirem em branco; na faixa de 2 px em volta dela, o preto das paredes do render fica.
  - **Fora da pegada:** branco no ajuste (131 mil px do Térreo saem). A máscara vai para `renders/POE642_CasaA_PH_Subsolo_pegada_mascara.png`.
  - **Na final (3840 px):** o `rotulos_casaa.py` leva a máscara ao quadro pelo mesmo afim da imagem (`no_quadro_fixo(..., mascara=)`, como a pedra portuguesa do Térreo). Fora dela, o lote do Térreo final no mesmo quadro (o que não é branco em `POE642_CasaA_PH_Terreo_final_rotulos.png`, fechado e sem furos: 68,4% do quadro) fica em diagonais finas a 45° (/), cinza 198, a cada 0,40 m (23,9 px), com traço de 1,3 px e o contorno do lote em cinza fino (165), como no Subsolo da Casa E. Fora do lote, branco.
  - **Dependência:** a hachura lê a final do Térreo; refazer o Subsolo depois de mexer no contorno do Térreo.
  - **Conferência:** na imagem com ajustes, só o contexto do Térreo (e o px claro da borda de fora da parede do hall e do elevador); na prancha, o fundo hachurado em volta do Subsolo, que ficou igual; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_hachurado_antes_depois.jpg`.
- **Subsolo, item 2, gramado na grama da referência, feito** (`ajustes_casaa.gramado_escada`, `GRAMADO_ESCADA["fonte"]`). Confirmado em 21/10: o gramado abaixo da escada do deck fica. Ele vinha do Térreo aprovado, na grama de carpete do motor; a fonte passa ao Térreo com os ajustes do pente fino, onde esse trecho é a grama da referência na escala (item 7 do Térreo; sem plantas ali), no mesmo lugar e pelo mesmo afim.
  - A grama da referência tem folhas claras que não passavam no teste de verde e ficavam brancas: a mancha verde da fonte é fechada (7 x 7) e preenchida antes da cópia.
  - **Dependência:** o Subsolo passa a ler `POE642_CasaA_PH_Terreo_final_bege_barlavento_ajustes.png`; rodar o Térreo antes.
  - **Conferência:** na imagem com ajustes e na prancha, só o gramado; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_gramado_referencia_antes_depois.jpg`.
- **Subsolo, item 3, escada do deck (R14, seção 5), feito** (`ajustes_casaa.escada_deck_subsolo`, config `ESCADA_DECK_SUB`). No PDF do Subsolo, a escada sobe da circulação (o "S"), da direita para a esquerda, até o deck. O corte é a diagonal da ARQ_ESCADAS E RAMPAS (de 754,1; 1230,9 a 788,2; 1299,0 pt), e o trecho depois dele, junto ao deck (os degraus 9 a 11), é a projeção, tracejada no PDF.
  - **Degraus do Subsolo:** os do item 3 de 19/10 (no creme da escada, com a textura do Bege Bahia) perdem a sombra de espelho (`ESCADA["sombra"]` vai a 0), que lia como linha. Ganham a linha suave em cada bocel, com a sombra curta: `retoque_terreo_casae.escada_linhas`, a mesma rotina e os mesmos bocéis (a cada 17 pt) da escada no Térreo.
  - **Depois do corte:** o creme esmaecido e liso (as linhas antigas saem), com os bocéis e o contorno tracejados por cima.
  - **Triângulo:** no 1º degrau, junto à circulação, apontando para a esquerda (a subida).
  - **Conferência:** na imagem com ajustes e na prancha, só a escada; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_escada_r14_antes_depois.jpg`.
- **Subsolo, item 4, portas sem arcos (R3), feito** (`ajustes_casaa.sem_arcos_subsolo`, config `SEM_ARCOS_SUB`). Os 5 arcos de porta do PDF do Subsolo (as curvas da ARQ_PAREDE: depósito, banho de serviço, sauna e banhos feminino e masculino) saem; as folhas e os batentes ficam.
  - **Como:** aqui os arcos do render são traços de 1 px. A rotina do Térreo (`arcos.remover_arcos`, que refaz uma faixa de ±3 px com a textura do piso ao lado) quebrava a grade da pastilha do banho de serviço e deixava uma mancha na sauna. Sai só o traço: o arco do PDF numa faixa de 4 px (1057 px), refeito por inpaint de raio 2. A grade da pastilha e o travertino continuam por cima dele (com 3 px sobrava um resto do arco junto à folha do banho de serviço).
  - **Conferência:** na imagem com ajustes e na prancha, só os 5 arcos; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_sem_arcos_antes_depois.jpg`.
- **Subsolo, item 5, portas, vidros e janelas finos (seções 4 e 18), feito** (`ajustes_casaa.vidros_subsolo`, config `VIDROS_SUB`).
  - **Porta de correr entre a circulação interna e a externa:**
    - Antes: o motor a fez como um traço preto grosso, com um degrau no meio.
    - No PDF (ARQ_PAREDE): duas folhas de vidro de 2,83 pt desencontradas, com as pontas brancas.
    - O traço sai com a sombra dele: numa faixa de 6 px, a metade de cima recebe o Bege Bahia de cima em espelho, e a de baixo, o de baixo.
    - Entram as duas folhas no vidro das portas da academia (claras, com a linha do meio), com as pontas em alumínio.
    - A borda das folhas fica com 0,25 px de cada lado. Com a de 1/8 px das portas da academia, a folha some no Bege Bahia; na madeira da academia, aquela basta.
  - **Folhas das portas de giro (R3: brancas, finas, com contorno fino):**
    - O item 5 do mapa citava só a do depósito, um bloco cinza de ~5 px logo abaixo da folha do PDF.
    - Na conferência, as outras quatro também estavam fora da R3: as do banho de serviço, da sauna e dos banhos feminino e masculino eram um traço escuro de 1 a 3 px. Entram junto, porque o item 4 já pedia "folhas finas e brancas".
    - O bloco e os traços saem pela mesma faixa espelhada (no banho de serviço, a parede fica 2 px abaixo, e o traço recebe só o piso de baixo).
    - Entram as folhas do PDF (2,27 pt, com as pontas), brancas (a folha das Casas D e E), com o contorno de 0,25 px de cada lado, pelo mesmo motivo da porta de correr.
  - **Janela entre o depósito e a academia:** o vão no meio da parede (de 1156,66 a 1224,69 pt) estava cinza-escuro; entra o vidro claro, com a borda fina e a linha do meio. A parede em volta fica preta.
  - **Vidros da sauna (folha contínua, seção 18):** o de cima tinha um montante (duas marcas escuras a um terço) e os dois trechos em tons diferentes. Em cada linha do vidro, entra a mediana do trecho. O da esquerda já era contínuo.
  - **Conferência:** na imagem com ajustes, só as 5 regiões (1.319 px); na prancha, as mesmas; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_portas_vidros_antes_depois.jpg`.
- **Subsolo, item 6, Bege Bahia como a referência (seção 18), feito** (`ajustes_casaa.bege_subsolo`, config `BEGE_SUB`).
  - **Antes:** a circulação externa, a interna e o depósito estavam no Bege Bahia do 1º Pavimento (item 11 de 19/10): rosados, com veios grandes, fora de escala.
  - **Agora:** o desenho da biblioteca, na escala do render (31,07 px/m), e o tom da foto (RGB 230, 211, 186), com a luz do lugar. É a mesma rotina e são as mesmas constantes do item 9 do Térreo e do Subsolo da Casa E.
  - **Como:**
    - A máscara é a do item 11 (as três áreas, sem paredes, vidros, janela e folhas), sem o verde do gramado.
    - Os pontinhos escuros do motor saem antes da troca, e o anel em volta do que foge da luz vai ao piso novo depois. Sem isso, os pontinhos e a borda ficavam no rosado antigo, que lia como cinza no tom novo.
    - A borda de 1 a 2 px junto às paredes, ao vidro da sauna e ao gramado também vai ao piso novo de perto, só onde é claramente piso; as quinas meio parede ficam.
    - Roda antes do item 5: a porta de correr e as folhas entram por cima do piso novo.
  - **Código:** a rotina do Térreo virou `bege_na_referencia`, usada pelos dois pavimentos; a máscara do item 11 virou `bege_mascaras`. Conferido: o Térreo e o item 11 saem iguais px a px.
  - **Conferência:** na imagem com ajustes e na prancha, só as três áreas de Bege Bahia; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_bege_referencia_antes_depois.jpg`.
- **Subsolo, item 7, travertino na escala (R1 e seção 18), feito** (`ajustes_casaa.travertino_subsolo`, config `TRAV_SUB`).
  - **Antes:** no hall, os veios do motor estavam na vertical, com riscos escuros; na sauna, na antessala e nos banhos, em faixas largas.
  - **Agora:** o travertino aprovado do Térreo da Casa A (veio horizontal, sem rejuntes), na mesma escala (31,1 px/m no Subsolo, 31,5 no Térreo, o mesmo quadro), com a luz do lugar. É o caminho do Subsolo da Casa E.
  - **Fonte:** dois trechos limpos do Térreo com os ajustes (a circulação junto ao jardim e a passagem abaixo do escritório), tecidos por image quilting, com os espelhos que mantêm o veio na horizontal. O desenho inteiro entra (força 1,4) sobre a luz do lugar (raio de 1 m, que tira o desenho antigo).
  - **Máscara:**
    - O travertino da base de entrega do Subsolo (#DCD9CA) no hall, na sauna com a antessala e nos dois banhos. O pátio, da mesma cor na base, é Bege Bahia desde o item 11 de 19/10 e fica de fora, assim como as portas de vidro entre a academia e o hall.
    - Os arcos e as folhas das portas, que furam a base, são fechados (3 x 3). Entra a faixa da sauna junto ao vidro da esquerda, que na base ficou na cor do pátio; no render, a sauna é toda travertino.
  - **Objetos:**
    - Saem da máscara pelo PDF, e não pela luz: as louças e bancadas (cubas, vasos, chuveiros, ralos), a divisória dos banhos e o branco dos vasos que toca as louças do PDF.
    - Primeiro tentei o critério de sempre (o que foge da luz do lugar fica): os riscos escuros do motor também fugiam, e o piso saiu em retalhos. Por isso `texturas_escala.retexturizar` ganhou a opção `fugir=False`; o padrão continua o de antes, e as outras casas não mudam.
    - Os vidros dos boxes e a borda do banco da sauna não ficam protegidos: na faixa deles ficava a sombra antiga junto às paredes, que lia como risco escuro. O piso troca por baixo, e os dois são redesenhados por cima, com as rotinas dos itens 9 e 2.
    - A borda de 1 a 2 px junto às paredes e aos objetos vai ao piso novo de perto, como no item 6.
  - **Conferência:** na imagem com ajustes e na prancha, só o hall, a sauna com a antessala e os banhos; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_travertino_antes_depois.jpg`.
- **Subsolo, item 8, shafts e projeções (R8), feito** (`ajustes_casaa.projecoes_subsolo`, config `PROJECOES_SUB`), como as projeções do 1º Pavimento da Casa E.
  - **Shafts:**
    - Antes: os dois junto ao elevador (o de cima, largo, e o da direita, estreito) estavam cheios, de marrom e de cinza, com o X contínuo.
    - Agora: o vão branco, como no PDF, com o X tracejado nos traços do próprio PDF (DOC_LINHAS E PROJEÇÕES), em cinza médio.
    - O retângulo do PDF é arredondado para dentro, e clareia tudo que não é parede preta, inclusive a borda escura do render junto à parede. Com o retângulo arredondado ao px mais perto, a parede ganhava um dente branco de 1 px; com o X pintado sobre a borda escura, o canto ficava com um traço escuro. Por isso o X entra só no branco.
    - O elevador fica como está: o mapa não o apontou.
  - **Retângulos da DOC_LINHAS (confirmados em 21/10: "em traço cinza fino, como no PDF"):**
    - São três: junto às paredes de cima e da direita do depósito (0,5 e 0,7 m de fundo) e junto à parede de baixo da academia (3,5 x 0,4 m).
    - Entram em traço contínuo de 0,6 px, como no PDF: cinza médio no Bege Bahia do depósito; cinza claro na madeira da academia, onde o cinza médio sumia (como na rouparia da Casa E). Nas paredes pretas, o traço some.
  - **Conferência:** na imagem com ajustes e na prancha, só os shafts e os retângulos; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_projecoes_antes_depois.jpg`.
- **Subsolo, item 9, soleiras (R13), feito** (`ajustes_casaa.soleiras_subsolo`, config `SOLEIRAS_SUB`). Conferidas as 10 portas no PDF (o vão na espessura da parede: branco entre os batentes é soleira; com o piso de um dos lados atravessando, não).
  - **Sem soleira (como já estavam):**
    - banho de serviço: o Barlavento entra no vão;
    - depósito e porta de correr da circulação: o piso da circulação;
    - sauna: o travertino;
    - banhos feminino e masculino: a madeira da academia e o travertino se encontram no vão;
    - academia para a circulação: o piso da circulação vai até a madeira.
  - **Com soleira (o vão branco no PDF):**
    - academia para o hall: o vão inteiro, de 1655,55 a 1666,89 pt, com as duas folhas de vidro de correr por cima. O render tinha ali uma faixa clara lisa entre a madeira e as folhas. As folhas e os batentes (item 4 de 19/10) ficam;
    - elevador: o vão entre o hall e a cabine, de 2012,72 a 2021,22 pt. O render tinha o travertino antigo.
  - **Desenho:** o das soleiras do Térreo (item 16): Bege Bahia na escala, no tom da referência, com as faces da parede em cinza fino. A rotina virou `desenhar_soleiras`, comum aos dois pavimentos, com a opção de deixar de fora o que fica por cima do vão; o Térreo sai igual px a px.
  - **Conferência:** na imagem com ajustes e na prancha, só os dois vãos; rodapé igual. Prancha do Subsolo e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_soleiras_antes_depois.jpg`.
- **Subsolo do pente fino fechado (21/10/26):** os 10 itens do mapa estão feitos. O próximo é o 1º Pavimento (16 itens), cujo entorno nublado sai do Térreo final.
- **1º Pavimento do pente fino.** O 1º Pavimento ainda não tinha a cadeia de ajustes (a prancha lia direto o render `v7_final2`). Passa a ter a mesma dos outros dois: `ajustes_casaa.py 1Pavimento` (a aprovada é a `v7_final2`), saída `renders/POE642_CasaA_PH_1Pavimento_v7_final2_ajustes.png`, que o `rotulos_casaa.py` lê, com o afim do quadro vindo da aprovada. O afim quadro -> imagem (`AFIM_QR["1Pavimento"]`) foi medido como os outros (107 pontos, 0,4 px; o mesmo cálculo reproduz o do Subsolo).
- **1º Pavimento, item 16, o "²" dos rótulos, feito primeiro.** Sem mudança de código: a imagem com ajustes saiu igual à aprovada, e na prancha mudaram só os 21 "²" (agora logo depois do "m"); rodapé igual. Com isso, a cadeia nova fica conferida: a prancha não mudou fora dos rótulos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_m2_antes_depois.jpg`.
- **1º Pavimento, item 1, o Térreo nublado em volta (seção 11), feito** (`ajustes_casaa.so_1pavimento`, config `PEGADA_1PAV`; no `rotulos_casaa.py`, a chave `nublado`).
  - **Antes:** o entorno era o do motor, quase apagado (o deck, a piscina e os pisantes em traço claro).
  - **Pegada (no ajuste):** sai do próprio render aprovado, como no `entorno_esmaecido.pegada` da Casa E: o que tem cor cheia (algum canal abaixo de 215), em manchas grandes, fechado e sem furos (os vazios com o X e a escada entram), 17,6% do quadro. O PDF do 1º Pavimento não serve para isso: traz o Térreo nas mesmas camadas. Fora da pegada, branco; a máscara vai para `renders/POE642_CasaA_PH_1Pavimento_pegada_mascara.png`.
  - **Na final (3840 px):** fora da pegada, o Térreo final sem rótulos, no mesmo quadro, nublado como o `entorno_esmaecido.py --nublado` (70% de branco, 80% da saturação, desfoque leve); o 1º Pavimento por cima, integralmente.
  - **Linhas do lote:** como na referência da Casa E, as linhas tracejadas do lote do 1º Pavimento continuam por cima. Vêm do PDF (os traços de 0,85 pt da camada sem nome), em cinza 140: no render estavam quase brancas e sumiam no nublado. As divisas dos vizinhos (1,13 pt), que o render não tinha, ficam fora. A projeção da cobertura é o item 13.
  - **Dependência:** o 1º Pavimento passa a ler a final do Térreo; refazer o 1º Pavimento depois de mexer no Térreo.
  - **Conferência:** na prancha, só o entorno muda; rodapé igual. Prancha do 1º Pavimento e PDF refeitos (o PDF foi de 16,8 a 19,9 MB, pelo desenho do Térreo em volta).
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_nublado_antes_depois.jpg`.
- **1º Pavimento, item 2, portas sem arcos (R3), feito** (`ajustes_casaa.sem_arcos_1pav`, config `SEM_ARCOS_1PAV`). Os 11 arcos de porta do PDF (as curvas da ARQ_PAREDE) saem; as folhas, os batentes e a borda das bancadas ficam.
  - **Rotina:** a do Subsolo (item 4), generalizada em `sem_arcos_pdf(out, chave, busca)`: o arco do PDF numa faixa de 4 px, refeito por inpaint de raio 2. Com `busca` (só o 1º Pavimento; o Subsolo sai igual px a px), o inpaint (`inpaint_sem_parede`) não usa nem muda a parede, as linhas retas do desenho (o escuro em fio de 15 px ou mais) e, na faixa de cada arco, o piso bem mais claro que o dele.
  - **Segunda passada:** alguns arcos do render passam 2 a 3 px para dentro do arco do PDF (o do banho 3 ficava como um arco claro); numa faixa de 9 px, sai o que ainda é mais escuro que o piso em volta, longe das paredes e dos batentes do PDF. Junto às folhas do PDF, fica só a linha da folha (o escuro em fio no sentido dela), e sai o toco do arco que chega à ponta.
  - **O que foi corrigido no caminho:** a mancha preta junto ao batente do banho 3 (o inpaint puxava a parede), o toco do arco na ponta da folha do banho 3, a borda da bancada do banho 2 cortada onde o arco a cruzava e o dente da circulação clara no vinílico da suíte 1.
  - **Conferência:** na imagem com ajustes e na prancha, só as 11 portas (11 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_sem_arcos_antes_depois.jpg`.
- **1º Pavimento, item 3, escadas (R14 e seção 5), feito** (`ajustes_casaa.escadas_1pav`: `escada_u_1pav` e `caracol_1pav`).
  - **Escada em U:** no PDF ela desce daqui (o "D" no degrau 20, o piso da circulação), inteira e sem corte. O motor fez os bocéis, a linha de percurso com a volta no patamar e as pontas de seta em cinza-escuro. Entram o travertino da mesma escada no Térreo (mesmo trecho e mesma cor), a linha suave e a sombra curta de 10 cm em cada bocel (lance de baixo descendo para a direita, lance de cima para a esquerda, a sombra do degrau 11 no patamar), o contorno limpo e o triângulo no degrau 19, apontando para a descida. A seta e o "D" do motor saem; o guarda-corpo fica.
  - **Caracol da saleta:** pelo PDF, o "D" e a seta ficam no degrau junto ao 0° e apontam para baixo: desce no sentido horário. O trecho cheio do render (o quarto de 0,6° a 93,1°, cinco degraus em madeira) fica, sem os riscos escuros do motor, com os bocéis do PDF em linha suave e a sombra curta do lado horário, e o triângulo (a 70%, como no Térreo) no degrau do "D". No resto, o branco limpo, sem a linha de percurso e sem o símbolo do corte (seção 5: "a linha de corte não é desenhada"), com os 14 bocéis tracejados da R14. **A confirmar:** a leitura do sentido e do trecho cheio veio do "D" e da seta do PDF; se o trecho cheio for outro (os degraus logo abaixo da laje, 20 em diante, no sentido horário a partir do 0°), basta trocar `CARACOL_1PAV["cheio"]`.
  - **Conferência:** na imagem com ajustes e na prancha, só as duas escadas (2 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_escadas_antes_depois.jpg`.
- **1º Pavimento, item 4, guarda-roupas com cabides (R11), feito** (`ajustes_casaa.guarda_roupas_1pav`, config `GUARDA_ROUPAS_1PAV`).
  - **Antes:** o motor fez armários de madeira com riscos escuros nos quatro closets.
  - **Onde:** os retângulos com diagonal da DOC_LINHAS E PROJEÇÕES no PDF: closet 3 e closet 1 em L, closet 2 em L, closet master em U (nove trechos). Os da circulação e do quarto de serviço são armários até o teto (item 5) e ficaram fora.
  - **Como:** o guarda-roupa da biblioteca (`elementos.guarda_roupa`), aberto, visto de cima, com os cabides e o cabideiro de metal, no tamanho do PDF, com as portas do lado do closet; os tons da Casa E (bege dentro, ocre na borda), como confirmado pelo usuário em 21/10.
  - **Conferência:** na imagem com ajustes e na prancha, só os quatro closets (4 regiões); os rótulos não mudam; rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_guarda_roupas_antes_depois.jpg`.
- **1º Pavimento, item 5, armários até o teto (seção 7), feito** (`ajustes_casaa.armarios_1pav`, config `ARMARIOS_1PAV`).
  - **Onde:** os dois retângulos com diagonal da DOC_LINHAS E PROJEÇÕES que não são guarda-roupa: na circulação, sob o banho 3 (o motor o fez bege liso, com a sombra de móvel baixo no vinílico), e no quarto de serviço (em madeira, com a diagonal).
  - **Como:** a rotina do Térreo (item 6), generalizada em `armarios_ate_o_teto(out, chave, q)`; o Térreo sai igual px a px. A sombra do motor sai do piso nas faces livres, a marcenaria areia aprovada entra com o veio no comprido, sem a diagonal, e o contorno fino fica nas faces livres.
  - **Sala íntima:** o mapa citava um armário ali, mas o PDF não tem retângulo com diagonal; o painel de madeira junto à parede é o da TV (no PDF, o retângulo branco com a TV) e ficou como está.
  - **Conferência:** na imagem com ajustes e na prancha, só os dois armários (2 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_armarios_antes_depois.jpg`.
- **1º Pavimento, item 6, bancos ao pé das camas (seção 8), feito** (`ajustes_casaa.bancos_1pav`, config `BANCOS_1PAV`).
  - **Onde:** os bancos do PDF (ARQ_LAYOUT HUMANIZAÇÃO): um no pé de cada cama de casal (suítes 3, 2 e master) e dois banquinhos no pé das camas de solteiro da suíte 1. O motor não desenhou nenhum.
  - **Como:** como os da Casa E (item 12 de lá): no pé da cama do render, a 1 px, na largura e altura do PDF, estofados em bege com a mesma almofada (o assento do sofá do render da Casa E), trama fina, contorno bege escuro e a sombra curta do banco do Térreo.
  - **Rótulos (R7):** "SUÍTE 3" e "SUÍTE 2" caíam sobre os bancos novos; foram ao piso livre mais próximo (o da 3 abaixo do banco, no tapete; o da 2 à direita da cama).
  - **Conferência:** na imagem com ajustes, só os cinco bancos; na prancha, os bancos e os dois rótulos; rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_bancos_antes_depois.jpg`.
- **1º Pavimento, item 7, criados-mudos da suíte 3, feito** (`ajustes_casaa.criados_1pav`, config `CRIADOS_1PAV`).
  - **Antes:** quadrados de ~45 cm em madeira clara, com sombra forte; no PDF, redondos de 60 cm.
  - **Como:** o quadrado e a sombra saem (cada linha recebe o vinílico limpo da mesma linha, ao lado, espelhado: as réguas correm na horizontal); entram os círculos do PDF na madeira do próprio quadrado, com contorno na mesma madeira mais escura e a sombra curta dos bancos.
  - **Conferência:** na imagem com ajustes e na prancha, só os dois criados-mudos (2 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_criados_mudos_antes_depois.jpg`.
- **1º Pavimento, item 8, quarto de serviço, feito** (`ajustes_casaa.quarto_servico_1pav`, config `QUARTO_SERV_1PAV`).
  - **Antes:** uma faixa clara junto à parede com dois quadrados brancos, e um risco no piso; no PDF, a cama de solteiro e o criado-mudo.
  - **Como:** a faixa e o risco saem (o vinílico limpo da mesma linha, espelhado); entram a cama e o criado-mudo da suíte 1 (mesmas medidas no PDF), espelhados na vertical, no retângulo do PDF, com a sombra curta. O rótulo do quarto continua no piso livre.
  - **Conferência:** na imagem com ajustes e na prancha, só o quarto de serviço (1 região); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_quarto_servico_antes_depois.jpg`.
- **1º Pavimento, item 9, banheira do banho master, feito** (`ajustes_casaa.banheira_1pav`, config `BANHEIRA_1PAV`).
  - **Antes:** banheira retangular de cantos arredondados, com sombra, sem torneira; no PDF, oval (1,68 x 0,89 m) com a torneira de piso na ponta da esquerda.
  - **Como:** a banheira do motor e a sombra saem (o piso limpo do banho, à direita, tecido e ajustado à luz de cada linha; as folhas da floreira ficam); entra a banheira oval da biblioteca de blocos (a da Casa E, só o corpo, sem a torneira de bancada do recorte) no retângulo da elipse do PDF, e a torneira de piso do PDF em cromo (base redonda e bica entrando na banheira), as duas com a sombra curta.
  - **Conferência:** na imagem com ajustes e na prancha, só a banheira (1 região); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_banheira_antes_depois.jpg`.
- **1º Pavimento, item 10, cortinas de linho, feito** (`ajustes_casaa.cortinas_1pav`, config `CORTINAS_1PAV`).
  - **Antes:** nas quatro suítes, uma coluna de tracinhos escuros no vinílico, no lugar das linhas onduladas do PDF; sem trilho.
  - **Como:** os tracinhos saem (o vinílico das beiradas, na mesma linha); entram o pano de linho da biblioteca em cada um dos 8 trechos do PDF (a meia distância, como lá) e o trilho de parede a parede do lado do vidro, um por suíte, como no 1º Pavimento da Casa E.
  - **Conferência:** na imagem com ajustes e na prancha, só as quatro fachadas das suítes (4 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_cortinas_antes_depois.jpg`.
- **1º Pavimento, item 11, vinílico na escala (R4), feito** (`ajustes_casaa.vinilico_1pav`, com `VINILICO` e `reguas_vinilico` da Casa E).
  - **Antes:** réguas de ~40 cm.
  - **Como:** o mesmo da Casa E: nas áreas de vinílico da base chapada, só no que é piso no render, réguas de 20 cm, 1,2 a 1,8 m, em tons alternados, com o veio do próprio render, na luz do lugar; o escurecido sobe 70% do caminho até a mediana. As folhas das portas do PDF ficam (sem isso, a da suíte 3 para o closet sumia). Roda logo depois dos itens 2 e 3, antes dos móveis (4 a 10), que são postos sobre o piso novo.
  - **Conferência:** na imagem com ajustes e na prancha, só as quatro suítes e os closets (6 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_vinilico_antes_depois.jpg`.
- **1º Pavimento, item 12, Bege Bahia das quatro varandas, feito** (`ajustes_casaa.bege_varandas_1pav`, config `BEGE_VARANDAS_1PAV`).
  - **Antes:** bege claro e rosado, com veios grandes de mármore, nas varandas das suítes 3, 2, master e 1.
  - **Como:** a rotina do item 9 do Térreo (`bege_na_referencia`): o desenho da biblioteca, na escala, no tom da foto (RGB 230, 211, 186), com a luz do lugar; os caixilhos e a linha do guarda-corpo ficam. O tom saiu igual ao do Bege do Térreo. As varandas são escolhidas por um ponto em cada uma, porque o hall da caracol e o quarto e o banho de serviço têm o mesmo cinza na base.
  - **Conferência:** na imagem com ajustes e na prancha, só as quatro varandas (4 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_bege_varandas_antes_depois.jpg`.
- **1º Pavimento, item 13, projeções da cobertura e do pergolado (R8, R9), feito** (`ajustes_casaa.projecoes_1pav_final`, config `PROJECOES_1PAV`, chamada na final por `rotulos_casaa.final_imagem`).
  - **Antes:** o motor não as desenhou; o pergolado só aparecia no Térreo nublado.
  - **No PDF:** a cobertura na ARQ_CONTRAPISO, em dois contornos fechados tracejados (o de fora é o L do Térreo; o de dentro, 34 pt para dentro), com dois trechos curtos entre eles à direita; o pergolado na ARQ_PERGOLADO, a grade de vigas de 20 cm à esquerda da suíte 2.
  - **Como:** as retas saem do PDF e entram em tracejado, no traço das projeções do Térreo (8,5 pt de traço, 4,25 de vão, cinza 150), por cima do Térreo nublado e do pavimento, menos nas paredes pretas. Entram na final porque quase tudo cai fora da pegada do pavimento.
  - **Conferência:** a imagem com ajustes não muda; na prancha, só as linhas das projeções (10 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_projecoes_antes_depois.jpg`.
- **1º Pavimento, item 14, portas de vidro de correr finas, feito** (`ajustes_casaa.vidros_1pav`, config `VIDROS_1PAV`).
  - **Antes:** em cada fachada de suíte, um "tubo" branco de ~8 px com contorno cinza; no PDF, dois planos de folhas de correr finas (o de fora junto à varanda e o de dentro).
  - **Como:** os vidros do Térreo (item 5): o tubo sai (o piso de cada lado, em espelho, do plano de fora para o de dentro; entre os planos fica o Bege Bahia da varanda) e as peças do PDF entram finas. Na master, o plano de fora segue pela frente do banho master. Ficam como estão as janelas dos banhos 1 e 2 e a da escada.
  - **Ordem:** o Bege Bahia das varandas (item 12) passou para logo depois do vinílico (resultado igual), e este item roda antes das cortinas (item 10), como na Casa E. Os tracinhos das cortinas saem antes do espelho. Na limpeza deles, o tom do vinílico passou a ser a mediana da faixa: com o vidro novo numa beirada e a poltrona na outra, a faixa da cortina de cima da suíte 2 saía cinza.
  - **Conferência:** na imagem com ajustes e na prancha, só as quatro fachadas (5 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_vidros_antes_depois.jpg`.
- **1º Pavimento, item 15, soleiras (R13), feito** (`ajustes_casaa.soleiras_1pav`, config `SOLEIRAS_1PAV`).
  - **Conferência porta a porta** (folha de recortes do PDF, da base e do render, e a cor do próprio PDF no meio de cada vão):
    - **sem soleira:** as 11 portas de giro (o piso de um dos lados atravessa o vão) e o elevador (no 1º Pavimento o travertino do hall vai até a cabine; a seção 4 pede soleira de inox no elevador, mas pela R13 só entra onde o PDF tem);
    - **com soleira:** a porta de correr da saleta para o quarto de serviço (o vão branco, com a folha dentro); o motor fez uma caixa clara ocupando o vão;
    - **janelas, não portas:** os vãos brancos do banho 3 (parede de fora) e do banho de serviço (parede da varanda) ficam como estão.
  - **Como:** o vão em Bege Bahia na escala, com as faces da parede em cinza fino (`desenhar_soleiras`), e a folha de correr fina por cima, no retângulo do PDF.
  - **Conferência:** na imagem com ajustes e na prancha, só a porta da saleta (1 região); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_soleiras_antes_depois.jpg`.
- **1º Pavimento, item 16, o "²" dos 22 rótulos, conferido.** A regra de 20/10 (o "2" sobrescrito logo depois do "m") está na rotina compartilhada dos rótulos e roda em todo ciclo: os 22 rótulos (o elevador sem área) já saem certos na prancha. Nada a mudar.
- **1º Pavimento do pente fino fechado (21/10/26):** os 16 itens do mapa estão feitos. Ordem de execução na lista `ITENS["1Pavimento"]`: pf2, pf3, pf11, pf12, pf4 a pf9, pf14, pf10, pf15 e pf1; a projeção (pf13) entra na final, no `rotulos_casaa.py`.
  - **Fora do mapa, a decidir com o usuário:** as janelas dos banhos 1, 2, 3 e de serviço, a da escada e o vidro da saleta e do quarto de serviço para fora (na fachada de baixo) continuam como o motor fez, em "tubo" claro. O mapa pedia só as portas das suítes (item 14); pela seção 4 ("vidros e janelas finos e elegantes"), podem passar pela mesma rotina.
- **Pedidos do usuário depois do pente fino (21/10/26):** "pode fazer as janelas finas também"; mostrar o Térreo nublado nos vazios, na faixa branca entre os lances da escada em U (o jardim do Térreo) e no trecho da escada que é do Térreo; a caracol sem o branco (o trecho do 1º Pavimento cheio, o resto nublado, os degraus dentro do círculo); e os cobre-leitos humanizados com as referências da biblioteca.
- **1º Pavimento, janelas finas (complemento do item 14), feito** (`ajustes_casaa.janelas_1pav`, config `JANELAS_1PAV`, pf14b).
  - **Como:** a mesma rotina das portas: em cada vão branco da janela, as peças finas do PDF saem (de fora para dentro) e o vão é redesenhado: vidro claro, caixilho de alumínio, peitoril em pedra e os batentes em quadradinhos. Banhos 3, 2, 1 e de serviço, a janela da escada e o vidro da fachada de baixo (saleta e quarto de serviço); no banho 2, também o vidro do plano de fora.
  - **Conferência:** na imagem com ajustes e na prancha, só as sete janelas (6 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_janelas_antes_depois.jpg`.
- **1º Pavimento, o Térreo nublado por dentro e a caracol, feito** (`ajustes_casaa.TERREO_1PAV`, máscaras gravadas no `so_1pavimento`; na final, `rotulos_casaa.nublar`; a caracol em `ajustes_casaa.caracol_1pav`).
  - **Vazios:** o branco dá lugar às salas do Térreo, nubladas; o X tracejado fica por cima.
  - **Escada em U:** a faixa entre os lances e as de cima e de baixo mostram o jardim do Térreo, nublado; os degraus 1 a 7 (até a diagonal do corte do Térreo) mostram os degraus coloridos do Térreo, nublados; do corte em diante, os do 1º Pavimento.
  - **Caracol:** o trecho cheio do 1º Pavimento (o quarto de 0,6° a 93,1°) para no anel do corrimão, a 52 pt como no PDF (a madeira do motor passava do círculo); por fora do anel, nesse quarto, o travertino da chegada. O resto do círculo e a abertura em volta mostram o Térreo nublado (a caracol do Térreo, com o trecho cheio de lá), com os bocéis em traço suave, para ler como escada.
  - **Como entra:** nas caixas dos vazios, do poço e da caracol, o que é cinza neutro claro (o branco e os traços) multiplica o Térreo nublado; nos degraus 1 a 7, o Térreo nublado entra inteiro.
  - **Conferência:** na imagem com ajustes, só a caracol; na prancha, os vazios, o poço da escada, a caracol e os traços em volta; rodapé igual. Prancha do 1º Pavimento e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_terreo_nublado_antes_depois.jpg`.
- **1º Pavimento, cobre-leitos humanizados, feito** (`ajustes_casaa.camas_1pav`, config `CAMAS_1PAV`, chave `cl`; a roupa de cama em `_texturas/elementos.roupa_de_cama`).
  - **O quê:** nas seis camas (casal nas suítes 3, 2 e master; solteiro nas duas da suíte 1 e no quarto de serviço), o desenho técnico do PDF (retângulo branco, contorno dos travesseiros, dobra em triângulo) dá lugar à roupa de cama da referência da biblioteca (linha 5 da cartela de elementos): lençol e edredom brancos, travesseiros cinza-claros com os bordô na frente, a dobra do lençol e a manta bordô na metade dos pés (no solteiro, a faixa bordô). A cabeceira fica do lado dos travesseiros do PDF.
  - **Encaixe:** o colchão é o retângulo do PDF; nos lados e nos pés, a borda segue a moldura do render (deslocada 1 a 2 px do PDF; na suíte 3, os pés 5 px além), para não cobrir a moldura nem deixar fresta.
  - **Conferência:** na imagem com ajustes e na prancha, só as seis camas (6 regiões); rodapé igual. Prancha do 1º Pavimento e PDF refeitos. A cartela de elementos (`_texturas/cartela_elementos.jpg`) mostra, na linha 5, a nossa ao lado da referência.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_cobre_leitos_antes_depois.jpg`.
- **Térreo, cama do motorista com a mesma roupa de cama, feito** (pedido do usuário, 21/10/26: "aplique a mesma roupa de cama"; `ajustes_casaa.cama_motorista`, config `CAMA_MOTORISTA`, chave `cl` do Térreo, logo depois dos itens 11 e 12).
  - **Como:** a rotina das camas do 1º Pavimento virou `pousar_camas(out, pavimento, config)`, usada pelos dois. Na cama do motorista, a cabeceira fica em cima, contra a parede; o colchão é o retângulo da cama do PDF menos a borda de 1,7 pt, sem a busca da moldura (a cama ali foi desenhada por nós no retângulo do PDF).
  - **Conferência:** no Térreo, só a cama (1 região) na imagem com ajustes e na prancha; rodapé igual. O 1º Pavimento, refeito com o Térreo novo (ajustes, final e prancha), ficou idêntico pixel a pixel (a refatoração não mudou as seis camas, e a cama do motorista não aparece no Térreo nublado da prancha do 1º Pavimento). Pranchas e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_cama_motorista_antes_depois.jpg`.
- **Quartzito Carrara nas ilhas e bancadas, nos três pavimentos, feito** (pedido do usuário, 21/10/26; `ajustes_casaa.carrara_bancadas`, config `CARRARA_BANCADAS`, chave `carrara` em cada pavimento; a pedra em `fontes_procedurais.quartzito_carrara`).
  - **A pedra:** feita por código (não há foto do Carrara na biblioteca), como o granito da referência: branca levemente acinzentada, com nuvens cinza muito suaves e veios cinza esfumados, ondulados, de largura variável, que somem e voltam; na escala (veios principais a cada ~30 cm, secundários a cada ~9 cm), ao longo do lado maior de cada peça.
  - **Onde:** as peças da ARQ_BANCADAS do PDF, menos os peitoris (estreitos). Térreo: ilha gourmet, ilha e bancada da cozinha, lavatório, bancada dos tanques, lavabo e banho do motorista. 1º Pavimento: as bancadas dos banhos e a da cuba redonda na circulação, junto ao quarto de serviço. Subsolo: banhos feminino, masculino e de serviço.
  - **O que fica:** a luz do lugar (sombras curtas, a sombra junto às paredes, a cuba esculpida do lavabo) e, por cima, cubas, torneiras, inox, cooktops e as linhas da área molhada.
  - **Conferência:** só as bancadas mudam nos três pavimentos; rodapés iguais. Pranchas e PDF refeitos.
  - **A decidir com o usuário:** no PDF, a ilha gourmet do Térreo tem um cooktop de 5 bocas que o render não desenhou; ficou o Carrara, como no resto da ilha.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_carrara_antes_depois.jpg`, `..._1Pavimento_carrara_antes_depois.jpg` e `..._Subsolo_carrara_antes_depois.jpg`.
- **Térreo, ilha da cozinha, feito** (pedido do usuário, 21/10/26: "troque as banquetas, melhore a representação da ilha e troque o cooktop"; `ajustes_casaa.ilha_cozinha_limpar` antes do Carrara e `ilha_cozinha_pecas` depois, config `ILHA_COZINHA`; na final, `ilha_cozinha_final`).
  - **Banquetas:** as três manchas brancas do motor saem (o granito volta) e entram três banquetas de madeira e linho da biblioteca (a referência da ilha gourmet da Casa E), no tamanho e no centro das do PDF (0,40 m), de frente para a ilha, metade sob o tampo, com sombra curta.
  - **Cooktop:** o do motor sai e entra o de inox de 5 bocas da biblioteca (o do PDF: 0,88 x 0,50 m), com os botões do lado de quem cozinha.
  - **Ilha:** Carrara, com o contorno fino e as duas laterais em cascata do PDF marcadas.
  - **Final:** contorno, cooktop e banquetas redesenhados nítidos na prancha de 3840 px.
  - **Conferência:** só a ilha muda no Térreo (1 região); o 1º Pavimento fica idêntico; rodapé igual. Pranchas e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_ilha_cozinha_antes_depois.jpg`.
- **Boxes dos chuveiros com folhas contínuas, nos três pavimentos, feito** (pedido do usuário, 21/10/26; `ajustes_casaa.boxes_continuos`, config `BOXES_CONTINUOS`, chave `boxes` em cada pavimento).
  - **O quê:** nos 10 boxes da casa (3 no Subsolo, 2 no Térreo, 5 no 1º Pavimento), as duas folhas de vidro de correr do PDF, inteiras e contínuas, com a sombra cinza fina ao lado, e o trilho em tracejado no vão até a parede, como no PDF.
  - **O que saiu:** o vidro do render no 1º Pavimento (falhado, quase sumindo nos banhos 1 e de serviço, com um trecho escuro e uma linha com degrau no master, 2 a 3 px fora do PDF) e os restos de vidros antigos no Subsolo e no Térreo; o piso volta pelo piso dos dois lados, sem tocar nas paredes, nos vasos e na planta do master.
  - **Conferência:** só os boxes mudam (2 regiões no Térreo, 5 no Subsolo, com o trilho comprido da ducha, e 5 no 1º Pavimento); rodapés iguais. Pranchas e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_boxes_antes_depois.jpg`, `..._Subsolo_boxes_antes_depois.jpg` e `..._Terreo_boxes_antes_depois.jpg`.
- **Paredes pretas revistas nos três pavimentos, feito** (pedido do usuário, 21/10/26; `ajustes_casaa.paredes_perfeitas`, config `PAREDES_PDF`, chave `paredes`).
  - **O quê:** as paredes são repintadas no contorno exato do PDF (os preenchimentos cinza da ARQ_PAREDE, paredes e pilares), pretas, com bordas retas e cantos nítidos; as falhas do motor (a grama dentro da parede da garagem do Térreo e outras) somem, e o preto que sobrava para fora (pontas tortas, pés) volta ao piso ou à grama em volta.
  - **Conferência:** no Térreo, as paredes e, por tabela, o assentamento da pedra portuguesa do acesso (redesenhada depois, com o muro do lote ao lado mudado); no Subsolo e no 1º Pavimento, só as paredes. Janelas, vãos e portas intactos. Rodapés iguais. Pranchas e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_paredes_antes_depois.jpg`, `..._1Pavimento_paredes_antes_depois.jpg` e `..._Subsolo_paredes_antes_depois.jpg`.
- **Térreo, bordas do acesso de veículos, feito** (pedido do usuário, 21/10/26; `ajustes_casaa.pedra_final`, `acesso_alfa`, config `ACESSO_BORDA`, na final).
  - **O quê:** junto à grama, a borda da pedra portuguesa segue o contorno vetorial do PDF, com a curva lisa e a linha cinza fina do limite; a franja clara de pedra sobre a grama e os degraus da máscara ampliada sumiram. Junto ao muro do lote e à garagem, como estava.
  - **Conferência:** só o acesso muda na prancha do Térreo (e no Térreo nublado do 1º Pavimento); rodapés iguais. Pranchas e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_acesso_bordas_antes_depois.jpg`.
- **Térreo, sem os traços verticais das juntas antigas, feito** (pedido do usuário, 21/10/26; `ajustes_casaa.juntas_verticais`, config `JUNTAS_VERTICAIS`, chave `juntas`).
  - **O quê:** os tracinhos verticais que sobraram da grade de juntas do motor (no anel em volta dos tracejados das projeções, dos móveis e das portas de vidro, onde o item dos rejuntes não mexeu) voltam ao piso, linha a linha, com o travertino dos dois lados; os veios horizontais continuam. As linhas do PDF ficam.
  - **Conferência:** só pontos do travertino mudam (varanda, salas, hall); rodapé igual; o 1º Pavimento muda só no Térreo nublado. Pranchas e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_juntas_antes_depois.jpg`.
- **Térreo, quarto do motorista, feito** (pedido do usuário, 21/10/26; `_texturas/elementos.ROUPA_CAMA["motorista"]`, `ajustes_casaa.CAMA_MOTORISTA`, e o ajuste do rótulo no `rotulos_casaa`).
  - **Cama:** o edredom em linho claro (o lençol e a dobra junto aos travesseiros continuam brancos), e a peseira bordô nos pés da cama, com dobras e o pesponto claro junto às bordas (antes, uma faixa no meio do edredom branco).
  - **Rótulo:** "Q. MOTORISTA / A: 7,4 m²" maior (corpo 1,2, como os outros, em vez de 0,8) e no piso livre abaixo da cama, centrado no quarto.
  - **Conferência:** só a cama e o rótulo mudam no Térreo; o 1º Pavimento fica idêntico; rodapé igual. Prancha e PDF refeitos.
  - **Antes e depois:** `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_quarto_motorista_antes_depois.jpg`.
- **Fila de 21/10/26 concluída.** As 6 camas do 1º Pavimento continuam com a faixa bordô no meio (as de solteiro) e o edredom branco; podem receber o mesmo tratamento do motorista, se o usuário quiser.

## Casa B · pente fino pelas regras (21/10/26)

Pedido do usuário: "SEGUIMOS PARA A CASA B" (a ordem da seção 17 das regras: Casa E, Casa A, Casa B, Casa C, Casa D). As duas pranchas de entrega atuais (`POE642_CasaB/entrega/POE642_CasaB_PH_{Subsolo,Terreo}_entrega.png`) foram conferidas trecho a trecho contra os PDFs do cliente e o `POE642_REGRAS.md` (com a seção 16, o inventário: B · Subsolo e B · Térreo). Nada foi retocado ainda; a lista aguarda a confirmação do usuário (seção 1 das regras).

- **Como foi conferido:** o PDF de cada pavimento, renderizado a 1,2 px/pt, foi levado ao quadro da prancha pelo alinhamento das paredes (ECC afim): prancha ≈ PDF × 0,878 + (126,5; −238), igual nos dois pavimentos. Lado a lado, trecho a trecho, e com as camadas DOC_LINHAS E PROJEÇÕES, ARQ_ELEMENTOS FIXOS, EST_PILAR e ARQ_ESCADAS E RAMPAS desenhadas por cima da prancha.
- **Mapas:** `conferencia_casab.py` (em `POE642_CasaA/scripts/`), com os itens em `PENTE_FINO` (pontos em px da prancha de 3840): `POE642_CasaB/renders/POE642_CasaB_PH_{Subsolo,Terreo}_pente_fino_mapa.jpg`.
- **Leitura das escadas no PDF:** as duas escadas externas aparecem nos dois PDFs, com "S" no Subsolo e "D" no Térreo. A de 6 degraus liga a ducha (embaixo) à pedra grande (em cima); a de 9 degraus liga o deck em L ao lado da piscina (embaixo, no nível da ducha, sem degrau entre eles) à varanda (em cima).
- **"ATENÇÃO ÀS ESCALAS" (usuário, depois do primeiro mapa):** a conferência foi refeita medindo as escalas, que passaram para o topo das listas.
  - **Quadro:** 59,7 px/m nos dois pavimentos (o PDF a 1:50); o elevador do Subsolo cai sobre o do Térreo.
  - **Pisos:** cada piso da prancha foi posto ao lado do da biblioteca na mesma escala (`texturas.textura`, trechos de 1,5 × 1,5 m, com régua de 1 m). Folha: `POE642_CasaB/renders/POE642_CasaB_PH_escalas_conferencia.jpg` (`conferencia_casab.py --escalas`).
  - **Vegetação:** medida folha a folha com a régua de 1 m.
  - **Móveis, louças e carros:** os contornos do PDF (ARQ_MOBILIÁRIO, ARQ_LAYOUT HUMANIZAÇÃO, ARQ_LOUÇAS E METAIS, ARQ_BANCADAS, marcenaria e elementos fixos) foram desenhados por cima da prancha: camas, bancos, criados, sofás, poltronas, mesas, cadeiras, bacias, cubas, tanques, espreguiçadeiras e aparelhos da academia batem com o PDF. Os carros são o bloco do PDF, de ~4,4 × 1,8 m.
- **Térreo (25 itens):**
  1. vegetação de 1,5 a 3 vezes o tamanho real: costela-de-adão com folhas de ~1,5 m (a real chega a ~0,9 m), samambaias com frondes de ~2,6 m, estrelícias com a flor de ~1,2 m, leques de palmeira de ~2,2 m no jardim de inverno; e passa do muro e do lote. Entram as plantas da biblioteca no tamanho real, só dentro do lote;
  2. pedra portuguesa: hoje uma trama regular de quadrinhos de ~15 cm, em caramelo; a pedra é de 6 a 8 cm, em leque, no tom da foto;
  3. granito marrom: hoje quase liso, com estrias verticais, sem grão e mais escuro (~90, 60, 58); a referência tem nuvens e lascas, em ~118, 89, 69;
  4. travertino: hoje estrias verticais contínuas de vários metros; a placa é de 1,20 m, com veios horizontais de 5 a 20 cm;
  5. vinílico (suítes, closet, sala íntima, circulação): hoje liso, sem réguas; as réguas são de ~20 cm, claras, em tons alternados (R4);
  6. grama (grão miúdo e mais clara que a referência, que tem manchas de 0,5 a 1 m) e o tom do deck (as réguas já estão na escala, ~19 cm; o tom é avermelhado). A confirmar a troca do tom do deck, também na ducha do Subsolo;
  7. carros prata, alinhados, de 4,70 × 1,85 m (R12; hoje o bloco do PDF, de ~4,4 × 1,8 m, em três cores);
  8. rótulos novos (seção 12): 37 ambientes com nome e área, mais o elevador; brancos no granito (R6); nenhum sobre objeto (R7: SUÍTE 3, PRAINHA e LAVABO caem sobre a cama, a espreguiçadeira e a bancada). A confirmar: o "SUÍTE 2 · 15,71 m²" solto atrás da suíte master (proposta: não entra) e o banho da suíte master, que no PDF se chama "SUÍTE MASTER · 13,7 m²";
  9. portas sem arcos (R3): as ~25 de giro e a pivotante do hall, com a folha até a ponta do PDF;
  10. as duas escadas com linhas e triângulo (R14): no Térreo, as duas descem (triângulo no topo);
  11. os 2 pilares redondos da EST_PILAR no bloco do motorista, em preto (R8; hoje não aparecem);
  12. o X tracejado do jardim de inverno por cima das plantas (R8); sai o X que o motor desenhou no hall interno, em volta do pufe;
  13. os portões em zigue-zague da ARQ_ELEMENTOS FIXOS (jardim do hall e área descoberta, os dois para a garagem). A confirmar se são portões ou brises, e a cor;
  14. armários até o teto sem a diagonal (closet master, suítes 1, 2 e 3);
  15. eletrodomésticos em inox (os quadrados sem diagonal da cozinha e o "Ref." do gourmet);
  16. cooktops com as 5 bocas do PDF (gourmet e ilha da cozinha);
  17. adega com a prateleira de vinhos (hoje um banco bege);
  18. sala íntima: a bancada clara com cuba do PDF (hoje um móvel de madeira com um enfeite);
  19. elevador com a porta e a soleira em inox; proposta: a cabine do Subsolo, como nas Casas C, D e E;
  20. portas, vidros e janelas finos;
  21. cortinas de linho com trilho de parede a parede (suíte master, sala íntima, suítes 1, 2 e 3);
  22. paredes pretas no contorno do PDF (seção 2, 21/10);
  23. soleiras (R13), porta a porta;
  24. pedidos de 21/10 na Casa A, a confirmar para a Casa B: roupa de cama, quartzito Carrara, boxes com as folhas contínuas e banquetas de linho;
  25. a peça branca comprida abaixo do lavatório gourmet (pendente desde a entrega): a confirmar o que é.
  - **Conformes:** o quadro; camas, bancos, criados, sofás, poltronas, mesas e cadeiras, bacias, cubas, tanques e espreguiçadeiras no contorno do PDF; réguas do deck (~19 cm); piscina em Barlavento com o spa e a prainha; pufe do hall; banco em L de bronze no deck; pisantes; shafts com o X.
- **Subsolo (12 itens):**
  1. só o Subsolo, com o resto do terreno hachurado (R2). A confirmar o que fica em cor cheia; proposta: a ducha, o deck em L e o início das duas escadas (o nível do Subsolo); a pedra grande e as pedras da esquerda, no nível do Térreo, vão para a hachura (hoje a pedra grande está em cor cheia, decisão de 14/10);
  2. Bege Bahia: hoje liso e rosado, sem as nuvens de 10 a 20 cm da placa de 0,60 m (seção 18), com riscos brancos na garagem; na garagem, nas circulações e no BH serviço;
  3. travertino: hoje estrias verticais de vários metros; placa de 1,20 m, veios horizontais (depósito, sauna e banco, BH sauna, pedra grande);
  4. academia: piso (~20 cm) e aparelhos na escala do PDF, mas com retângulos de piso de outro tom em volta das bicicletas e do supino (sobras da colagem);
  5. escada de 6 degraus: sobe da ducha para a pedra grande, triângulo no 1º degrau junto à ducha;
  6. escada de 9 degraus: sobe do deck em L, triângulo no 1º degrau, cheia até o corte (depende do item 1);
  7. portas sem arcos (R3): as 4 do PDF;
  8. vidros finos: a parede de vidro entre a garagem e a academia, os vidros da sauna e o box do BH serviço;
  9. rótulos novos: 9 ambientes mais o elevador; o "BH SERVIÇO" do PDF cai sobre a bacia (R7);
  10. soleiras (R13);
  11. paredes pretas no contorno do PDF;
  12. os 2 pilares da EST_PILAR caem no terreno, sob o bloco do motorista; proposta: não desenhar no Subsolo. A confirmar.
  - **Conformes:** o quadro; réguas da ducha (~18 cm); esteiras, bicicletas e supino no tamanho do PDF; elevador com a cabine, shaft com o X, armário ao lado do elevador sem diagonal, banco da sauna em dois níveis, louças e chuveiros, garagem sem carros (o PDF não tem; decisão do usuário).
- **Ordem proposta:** o Térreo primeiro, porque o lote hachurado do Subsolo sai do Térreo final (como nas Casas A e E). A imagem final do Térreo da Casa B é o render retocado (`renders/POE642_CasaB_PH_Terreo_v4_retocado_barlavento.png`, 2000 × 1116), e a do Subsolo, a final em 6905 px; os retoques vão precisar de um `ajustes_casab.py` próprio, que reaproveita as rotinas da Casa A.

### Casa B · os ajustes do pente fino, feitos (21/10/26)

Pedido do usuário: "PERCORRA TODOS OS AJUSTES DE TODAS AS PLANTAS DA CASA B, SEM ME PERGUNTAR OU PEDIR APROVAÇÃO". Os 25 itens do Térreo e os 12 do Subsolo foram feitos, um por vez, sem IA. Nos pontos "a confirmar", valeu a proposta dos mapas, listada abaixo.

**Script:** `POE642_CasaA/scripts/ajustes_casab.py`. Reaproveita as rotinas aprovadas do pente fino da Casa A (`ajustes_casaa.py`); `contexto()` faz a troca:
- `rotulos_casaa` e `ajustes_casaa` passam a ler o PDF, a config, as imagens e a base chapada (v2, as cores da legenda) da Casa B;
- os parâmetros de cada rotina recebem as coordenadas da Casa B;
- as peças que a Casa A não tem ganharam rotina própria.

**Imagens de partida:**
- Térreo: `renders/POE642_CasaB_PH_Terreo_v4_retocado_barlavento.png` (2000 × 1116);
- Subsolo: a final de 6905 px reduzida a 2000 (`..._Subsolo_final_2000.png`). Na final, o que não mudou volta da imagem de 6905 px.

**Saídas:**
- `renders/POE642_CasaB_PH_{Terreo,Subsolo}_ajustes.png`, com `_camada.png` e um `..._<item>_antes_depois.jpg` por item;
- as finais de 3840 px com os rótulos: `renders/POE642_CasaB_PH_{Terreo,Subsolo}_final_rotulos.png`;
- as pranchas e o PDF: `entrega/POE642_CasaB_PH_{Terreo,Subsolo}_entrega.png` e `entrega/POE642_CasaB_Plantas_Humanizadas.pdf`.

**Decisões nos pontos "a confirmar" (pela proposta):**
- **Térreo 6:** o tom do deck passa ao da referência, também na ducha do Subsolo.
- **Térreo 8:** o "SUÍTE 2 · 15,71 m²" solto não entra; o banho da suíte master vira "BANHO MASTER · 13,7 m²".
- **Térreo 13:** são portões, em alumínio.
- **Térreo 19:** o elevador recebe a cabine do Subsolo.
- **Térreo 24:** entram os pedidos da Casa A (roupa de cama, boxes contínuos e banquetas de linho); o Carrara deu lugar, em 22/10, à pedra fina de tom sóbrio e, no mesmo dia, à pedra tom areia humanizada, com as cubas brancas (seção da final em 3840 px, abaixo).
- **Térreo 25:** a peça branca é uma floreira (caixa de paredes finas de 9 cm, com 40 cm de miolo).
- **Subsolo 1:** em cor cheia, a ducha e a escada de 6 degraus; o deck em L, a escada de 9 (desde 22/10, a pedido), a pedra grande e as pedras da esquerda vão para a hachura.
- **Subsolo 12:** os pilares não são desenhados no Subsolo.

**Térreo, na ordem de execução:**
- **1, vegetação:**
  - jardim de inverno e jardim de 4,62 m² do hall: terra, forração e as plantas da biblioteca no tamanho real (costela-de-adão de 0,9 m e outras);
  - gramado: rotinas da Casa A (`grama_escala`, `vegetacao_a`), com o gramado lido do verde da legenda (#6E9150) e não do branco do lote;
  - as manchas do motor saem e entram 56 plantas da referência no tamanho real, com a copa dentro do verde;
  - as folhas que passavam do muro, do lote e para os pisos voltam ao material de cada lugar. Na pedra e no granito as sobras saem por inpaint, e esses pisos são refeitos nos itens 2 e 3;
  - fora do lote, o vulto das sombras some e a linha tracejada da divisa volta inteira.
- **25:** a floreira junto ao lavatório gourmet.
- **6:** a grama da referência e o deck na madeira da referência, régua a régua, nos dois decks.
- **3:** granito da referência (`granito_referencia_a`, com a cor #5A4232 da legenda B).
- **4:** travertino no desenho do aprovado da Casa A, com veio horizontal, na luz do lugar. Tapetes, móveis e objetos do PDF ficam.
- **5:** vinílico em réguas de 20 cm deitadas (`vinilico_1pav`, com a cor #C8A27C).
- **7 (R12):**
  - os carros do motor (achados pelo que não é caramelo) saem para a pedra tecida;
  - entram os três carros prata da R12: 4,70 × 1,85 m (146 × 58 px), alinhados nos centros do PDF e com o carro do meio como modelo.
- **9 (R3):** 28 arcos fora (`sem_arcos_pdf`, com a busca do 1º Pavimento da Casa A).
- **10 (R14):**
  - a de 6 degraus desce da pedra grande para a ducha, com o triângulo à esquerda;
  - a de 9 degraus desce da varanda para o deck em L, com o triângulo à direita;
  - as setas do motor saem por mediana.
- **11:** os 2 pilares da EST_PILAR em preto.
- **14:** 10 trechos de guarda-roupa com cabides (R11; closet master em U; suítes 1, 2 e 3), sem a diagonal (em 21/10 eram marcenaria areia; trocado a pedido em 22/10).
- **15:** três quadrados em inox na cozinha e o refrigerador do gourmet.
- **18:** a bancada da sala íntima com a cuba.
- **24, bancadas:** 18 ilhas e bancadas (em 21/10, quartzito Carrara; em 22/10, pedra fina de tom sóbrio e depois pedra tom areia humanizada, com as cubas brancas).
- **16:** cooktops de 5 bocas.
- **17:** a adega com a prateleira, 3 nichos e 36 garrafas.
- **19:** o elevador com a cabine.
- **24, banquetas:** 4 banquetas de linho na bancada gourmet.
- **13:** os portões em zigue-zague.
- **20:**
  - 199 vidros e folhas do PDF (os brancos da ARQ_PAREDE até 3,2 pt), limpos e redesenhados finos em 125 esquadrias;
  - ficam fora o elevador e os portões.
- **21:**
  - no PDF da Casa B cada pano é uma cadeia de ondinhas de 2 × 6 pt; vieram 10 panos de linho;
  - 5 trilhos de parede a parede;
  - os panos deitados da fachada de cima usam a imagem transposta.
- **24, camas:** a roupa de cama da biblioteca nas 7 camas, com a cabeceira do lado do PDF; há camas deitadas na planta.
- **24, boxes:** 9 boxes contínuos.
- **23 (R13):** 20 vãos que são brancos na base, junto à ponta de um arco do PDF, recebem a soleira de Bege Bahia.
- **22:** as paredes no contorno do PDF.
- **12:** sai o X do motor no hall; entram os três painéis com o X tracejado do PDF sobre o jardim de inverno.
- **2:**
  - a pedra portuguesa de 7 cm em leque, no tom da foto (bege, cinza e rosado), só nas manchas grandes da legenda: garagem e acesso;
  - na final de 3840 px ela é redesenhada de novo pela máscara.
- **8 (rótulos, na final):**
  - "SUÍTE 3" sai da cama, "PRAINHA" da espreguiçadeira, "GARAGEM" do carro, "BANHO 2" da bacia e "QUARTO MOTORISTA" da luminária;
  - nos dois jardins o texto vai em branco;
  - os desvios ficam em `PAVIMENTOS_B["Terreo"]["ajustes"]`.

**Subsolo, na ordem de execução:**
- **3:** o travertino do Térreo.
- **2:**
  - Bege Bahia da referência (`bege_referencia_a`, lendo o Subsolo);
  - a circulação de 1,16 m², branca no PDF e aberta em cima, entra em Bege Bahia.
- **4:** academia em réguas de 20 cm, com o piso contínuo.
- **1, deck:** a ducha e o deck em L na madeira da referência, em cor cheia (com luz uniforme, porque o deck em L estava esmaecido).
- **5 e 6:**
  - as escadas em cor cheia (o travertino aprovado), com as linhas da R14;
  - a de 6 degraus sobe da ducha, com o triângulo à direita apontando para a esquerda, e fica inteira abaixo do plano de corte;
  - a de 9 degraus sobe do deck em L, com o triângulo à esquerda; fica cheia até o corte, a 1,20 m (depois do 7º degrau, na diagonal), e esmaecida depois.
- **7:** os 4 arcos fora.
- **8:** 23 vidros finos.
- **10:** 1 vão branco com soleira; nas outras portas o piso atravessa.
- **11:** as paredes.
- **1 (R2):**
  - a pegada do Subsolo, com os poços fechados (elevador e shaft);
  - fora dela, branco na imagem e o terreno hachurado na final, a partir do lote do Térreo final da Casa B.
- **9 (rótulos):** "BH SERVIÇO" em duas linhas, fora da bacia.

**Para refazer** (da pasta `POE642_CasaA/scripts/`; as etapas ficam em cache em `$TMPDIR/poe642_casab_etapas`, e `--de <item>` recomeça dali):

```
python3 ajustes_casab.py Terreo && python3 ajustes_casab.py Terreo --final
python3 ajustes_casab.py Subsolo && python3 ajustes_casab.py Subsolo --final     # o Subsolo depois: a hachura vem do Térreo final
python3 rodape_entrega.py --config ../../POE642_CasaB/config_bases.json --no-quadro \
    --render Terreo=../../POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png \
    --render Subsolo=../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final_rotulos.png
python3 pdf_entrega.py --config ../../POE642_CasaB/config_bases.json
```

### Casa B · pedidos de 22/10/26, depois do pente fino

Pedidos do usuário vistos nas pranchas, todos feitos sem IA no `ajustes_casab.py`:
- **"E OS GUARDA-ROUPAS?"** (Térreo 14, R11): os 10 trechos do closet master e das suítes 1, 2 e 3 são guarda-roupas com cabides (`elementos.guarda_roupa`, com as portas do lado do quarto), não marcenaria. A marcenaria areia fica para os armários de cozinha e serviço.
- **"MELHORE O ASPECTO DO TRAVERTINO" / "REMOVA OS RISCOS":**
  - o travertino é refeito na final de 3840 px (`travertino_final` → `trocar_travertino`), com a foto da biblioteca (`_texturas/travertino.jpg`, tecida sem repetição) na luz larga do lugar (3 m);
  - a máscara é a da base chapada, menos os objetos e as escadas do PDF e o que foge da luz local (móveis, sombras, cortinas);
  - as emendas, os traços verticais e as manchas do motor saem com o piso antigo;
  - nos outros pisos, `riscos_terreo` e `riscos_subsolo` tiram por inpaint os riscos escuros finos ou pontuais, longe das linhas e dos objetos do PDF.
- **"PORTAS, JANELAS E VIDRO MAIS FINO E ELEGANTES":** as esquadrias são redesenhadas na final de 3840 px (`esquadrias_final`), com a faixa de limpeza na escala; antes vinham de 2000 px e engrossavam na ampliação.
- **"MELHORE ESSAS BORDAS":** as bordas entre a grama e os pisos do Térreo são refeitas na final (`bordas_grama`). O contorno vem da legenda (verde #6E9150), liso; numa faixa de 4 px, a grama que invadia o piso e o claro que sobrava na grama viram o material do seu lado, com a transição de 1 px.
- **"E ONDE ESTÃO AS PROJEÇÕES DE COBERTURA?":**
  - a cobertura da entrada (a pérgola entre o jardim de 4,62 m², o hall e a garagem: o contorno e as seis vigas) está no PDF da Casa B como tracejado da ARQ_PAREDE (traços de 5,7 pt), e não na DOC_LINHAS E PROJEÇÕES;
  - entra na final (`cobertura_final`), nos traços do próprio PDF, em cinza escuro e fino, por cima de tudo menos das paredes.
- **"ESSE CARRARA NÃO ESTÁ BOM. VAMOS UTILIZAR UMA PEDRA FINA E TOM SÓBRIO":** as 18 ilhas e bancadas do Térreo e as do Subsolo passam à pedra fina (`fontes_procedurais.pedra_fina`): quartzo de grão miúdo em cinza quente (RGB ~177, 170, 164), sem veios. Entra pelo mesmo `carrara_bancadas`, que ganhou o parâmetro `pedra`; a Casa A continua em Carrara.
- **Subsolo:**
  - "essa parte não faz parte do Subsolo": o deck em L e a escada de 9 degraus saem da pegada e vão para a hachura (ficam a ducha e a escada de 6);
  - "cadê o chuveiro?": o chuveiro na ducha, na parede da sauna (o PDF não tem chuveiro ali);
  - "esse contorno preto da bancada está grosseiro": o contorno grosso do motor sai e entra o contorno fino do PDF;
  - "diminua a fonte para caber o rótulo": "CIRCULAÇÃO" em corpo 0,8.
- **Térreo, "escrito mais abaixo no piso, não pode estar no tapete":** "SALA ÍNTIMA" desce para o vinílico, fora do tapete.

### Casa B · a final refeita em 3840 px (22/10/26)

Pedido do usuário, vendo a prancha do Térreo: "TEM MUITOS BORRÕES NA IMAGEM. MOBÍLIAS DESGASTADAS E MAL DESENHADAS. PRECISO QUE REVISE ITEM A ITEM E DEIXE A IMAGEM COM OS CONTORNOS PERFEITOS".
- **A causa:** tudo o que os ajustes desenhavam em 2000 px (grama, árvores, texturas, móveis do motor, louças, peças da biblioteca) a final ampliava para 3840 px, e a ampliação borrava.
- **A solução:** a final passa a ser desenhada direto no quadro da prancha (~59,7 px/m), pelo PDF (que é vetor) e pela base chapada da legenda, no módulo novo `scripts/final3840_casab.py`. O `ajustes_casab.py --final` chama esse módulo.
- **Pisos e grama:** na máscara exata da legenda, com a textura da biblioteca reduzida da amostra, sem desfoque.
- **Vegetação:** as mesmas plantas da biblioteca, nos mesmos lugares.
- **Móveis, tapetes e louças:** redesenhados pelo próprio desenho do PDF (ARQ_MOBILIÁRIO, ARQ_LAYOUT HUMANIZAÇÃO, ARQ_LOUÇAS E METAIS e ARQ - Marcenaria), na ordem de pintura dele, com:
  - a cor do material tirada do render;
  - volume suave na borda;
  - veio na madeira;
  - o traço fino do PDF;
  - a sombra curta.
- **Peças da biblioteca:** guarda-roupas, camas, cortinas, cooktops, inox, adega, elevador e carros, desenhados no quadro.

Os pedidos que vieram depois, item a item:
- **"EXISTEM DOIS PILARES REPRESENTADOS POR BOLAS. PRECISAMOS DEIXAR EM CINZA PARA DESTACÁ-LOS":** os dois pilares redondos da EST_PILAR (na varanda) em cinza médio, com o contorno escuro fino; os retangulares seguem pretos.
- **"MELHORE OS RÓTULOS E NÃO OS SOBREPONHA OS OBJETOS":** cada rótulo vai para o lugar livre mais perto do ponto do PDF, dentro do próprio ambiente e sem tocar objeto, parede, esquadria, escada nem outro rótulo. Onde não cabe, quebra em duas linhas e depois desce o corpo. O texto leva um halo suave do tom do fundo.
  - Nos banhos pequenos (lavabo, BH serviço, BH motorista e os dois banhos gourmet), no menor corpo, o rótulo ainda encosta um pouco nas peças: não há piso livre do tamanho do texto.
- **"MELHORE AS REPRESENTAÇÕES DE CUBAS, PIAS, TANQUES. ALÉM DISSO, NÃO PERMITA QUE A PEDRA FIQUE BORRADA":** as louças do PDF em louça (cerâmica branca, com a bacia funda e a sombra interna do lado da luz); os detalhes miúdos em metal; a pedra das bancadas sem desfoque.
- **"MELHORE A REPRESENTAÇÃO DO CHUVEIRO. MELHORE O CONTORNO DO PISO DE MADEIRA":**
  - o chuveiro do deck em cromado, no lugar do PDF;
  - o banco em L do deck em réguas, um tom abaixo do deck, com o contorno fino e a sombra;
  - o deck no contorno exato da legenda.
- **"REMOVA BORRÕES DO PISO E OS BORRÕES NOS DEGRAUS":**
  - os pisos refeitos na escala da prancha;
  - as duas escadas do Térreo, a de 6 e a de 9 degraus (da varanda para o deck em L), com os bocéis em linha suave, a sombra curta e o triângulo no início.
- **As banquetas da bancada gourmet:**
  - as `banqueta_linho` estavam sendo postas pelos números de 2000 px e caíam no pé da escada de 6 degraus;
  - agora vão nos centros dos quatro círculos do PDF (ARQ_LAYOUT HUMANIZAÇÃO), com a sombra curta das peças;
  - os círculos do PDF não saem mais como aros transparentes sobre a pedra.
- **"TROQUE O CINZA DAS BANCADAS PELO TOM AREIA" / "CUBAS EM BRANCO" / "PRECISO QUE AS PEDRAS ESTEJAM HUMANIZADAS":**
  - a pedra cinza sai. Entra a foto do Bege Bahia da biblioteca (a placa real, com as nuvens de 10 a 20 cm), na escala da prancha, com 80% do contraste e levada ao tom areia (RGB ~233, 217, 198).
  - A pedra vai em toda peça da ARQ_BANCADAS, nos dois pavimentos (18 peças no Térreo, 3 no Subsolo):
    - as bancadas brancas do PDF;
    - as peças bege do Subsolo (a bancada da cuba esculpida e o banco da sauna, que antes mostravam o render);
    - a peça estreita de 10 cm do banho master.
  - **Cubas:** todas em louça branca, com a bacia de cantos arredondados, a sombra interna, um contorno fino só (sem o aro duplo do PDF) e a sombra curta na pedra:
    - as da cozinha, do gourmet e do bar, que estavam em inox; nessas, a bacia (pintada no PDF por baixo do aro) ganhou a sombra interna pela geometria, e o aro duplo ficou leve;
    - as cubas da ARQ_BANCADAS: as compridas, que a regra antiga perdia (lavabo, banho 2 e banho 3), e a cuba esculpida do Subsolo.
  - **A regra nova da cuba na ARQ_BANCADAS:** é o retângulo com o aro fino nos quatro lados. A peça de pedra entre as duas cubas do lavatório gourmet, que antes saía branca, volta a ser pedra, e a peça solta de 0,51 × 0,48 m junto ao louceiro também.
- **Imagens:** `POE642_CasaB/renders/POE642_CasaB_PH_{Terreo,Subsolo}_final_rotulos.png`. Pranchas e PDF refeitos. Os antes/depois estão nos `AD2_*.jpg` enviados na conversa.
- **"INVERTA O LADO DO COOKTOP PARA QUE OS BOTÕES FIQUEM VIRADOS PARA O OUTRO LADO"** (a ilha da cozinha): o cooktop de 5 bocas fica em pé, girado a 270° (`COOKTOPS_B`, era 90°), com os botões para a direita; o do gourmet não muda. Prancha do Térreo e PDF refeitos.
- **"RÓTULOS NÃO PODEM TER SOMBRA. USE A COR PRETA OU BRANCA, A DEPENDER DO FUNDO. E OS RÓTULOS DEVEM ESTAR DENTRO DE SEUS RESPECTIVOS AMBIENTES":**
  - **Cor:** sai o halo, e cada rótulo é preto ou branco pelo fundo da caixa (luminância relativa): 26 pretos e 12 brancos no Térreo (granito, jardins), 10 pretos no Subsolo.
  - **Ambientes:** antes eram as regiões entre todas as linhas do PDF. A passagem sem porta da circulação do Subsolo juntava a circulação à garagem, e o rótulo saía metade na garagem. A folha de porta e o vidro do box cortavam o banho gourmet ao meio. Agora:
    - as paredes escuras definem os ambientes, com os vãos alinhados fechados até 2 m;
    - as áreas abertas são repartidas entre os pontos do PDF.
  - **Erro achado:** a medida da caixa do texto ignorava o corpo e a quebra; o centro da opção era comparado na largura errada. Por isso os rótulos de banho saíam por cima da parede em vez de quebrar em duas linhas. Corrigido, os 48 rótulos ficam dentro dos ambientes.
  - **Ainda encosta:** a circulação de 1,16 m² do Subsolo encosta 1 px numa peça.
- **"AS PEDRAS DA SAUNA, EM FORMA DE BANCOS, SÃO EM TRAVERTINE":**
  - os dois níveis do banco (o retângulo da ARQ_CONTRAPISO; o de trás saiu da pedra das bancadas) no travertino da biblioteca, no tom e no veio do piso da sauna;
  - o nível de trás um pouco mais claro, o espelho e a frente em linha fina, e a sombra discreta junto ao espelho.
- **"E OS DEGRAUS EM PEDRA BEGE BAHIA NA LATERAL ESQUERDA DA IMAGEM???":**
  - as escadas externas da esquerda em Bege Bahia, nos degraus do PDF: a de 6 degraus nos dois pavimentos e a de 9 no Térreo;
  - as linhas e o triângulo vão por cima;
  - a mediana que limpava os degraus (e borrava a pedra) saiu.
- **"O BANCO EM L DO DECK É EM BRONZE FOSCO":** as réguas de madeira saem; o banco fica em bronze fosco (`BANCO_DECK`):
  - a cor chapada do bronze, com um escovado bem leve ao longo de cada braço;
  - a quina do lado da luz um pouco mais clara e a do outro lado um pouco mais escura;
  - o contorno fino e a sombra curta no deck.
- **"O RÓTULO DA PRAINHA PODE FICAR ABAIXO DAS DUAS ESPREGUIÇADEIRAS":** a busca do rótulo parte de um ponto abaixo da segunda espreguiçadeira (`ROTULOS_F["pontos"]`).
- **"O RÓTULO DO BANHO GOURMET ESTÁ SOBRE O CHUVEIRO. PODE ESCREVER ASSIM 'BH. GOURMET', E NÃO PRECISA FICAR DENTRO DO BOX":**
  - os dois rótulos passam a "BH. GOURMET" (`ROTULOS_F["textos"]`, no centro do nome do PDF);
  - nenhum rótulo vai para dentro de um box: o vidro (`vidros_box`) divide o banho, e o lado da ducha do PDF (`duchas_box`) fica fora;
  - o BH serviço do Térreo, cujo ponto no PDF cai dentro do box, passa ao piso seco do mesmo banho.
- **"AS BANQUETAS DEVEM APARECER PARCIALMENTE, ATRÁS DA BANCADA"** (a ilha gourmet): as quatro banquetas entram sob o tampo; a pedra da ARQ_BANCADAS cobre a parte delas que fica sob ele (ficam o encosto e a frente do assento), e a sombra não cai sobre a pedra (`banquetas`).
- **"CORRIGIR AS SOLEIRAS":**
  - **O problema:** a final de 3840 px não redesenhava as soleiras; ficavam as dos ajustes de 2000 px, ampliadas: moles, de borda borrada, com restos em volta (a do portão do hall com pontos e mancha; as da garagem para o serviço, brilhosas).
  - **Agora:** etapa `soleiras` nos dois pavimentos, nos 20 vãos brancos do Térreo e no do Subsolo (`vaos_brancos`). Cada soleira vai da ponta de uma parede à da outra, na espessura exata da parede do PDF, nítida, em Bege Bahia com as faces em cinza fino; batentes e folhas por cima.
- **"PRECISO QUE OS BOXES DOS BANHOS ONDE TEM PISO MARROM GRANITO EM CINZA CLARO. TEM QUE ESTAR VISÍVEL":** no BH serviço e no BH motorista, o vidro do box sai como faixa cinza-clara contínua, de parede a parede (etapa `boxes`); antes, os traços do PDF sobre o granito davam uma linha escura que quase sumia.
- **"CORRIJA A CORTINA QUE ESTÁ DUPLICADA"** (sala íntima):
  - **O problema:** as cortinas eram desenhadas na etapa `biblioteca`, antes das esquadrias. A limpeza das esquadrias espelha o piso de junto do vidro sobre a faixa dele e levava a cortina junto: duas fileiras de ondas na sala íntima e ondas cruzadas na suíte 1, na master e na suíte 3. As ondinhas do PDF que marcam o pano também vinham riscadas de leve no piso, e o espelho as copiava para junto do vidro.
  - **Agora:** antes das esquadrias, as ondinhas do PDF saem do piso (`ondas_fora`); a cortina passou para a etapa `cortinas`, logo depois das esquadrias. Cada janela tem um pano só, sobre o piso limpo, nas 10 cortinas do Térreo.
  - **Antes e depois:** enviado na conversa (`AD8_cortinas.jpg`, da sala íntima, das suítes 1 e 2, da master e da suíte 3).

## Casa C · pente fino pelas regras (22/10/26)

Pedido do usuário: "Casa C" (a ordem da seção 17 das regras: Casa E, Casa A, Casa B, Casa C, Casa D). As duas pranchas de entrega atuais (`POE642_CasaC/entrega/POE642_CasaC_PH_{Subsolo,Terreo}_entrega.png`) foram conferidas trecho a trecho contra os PDFs do cliente e o `POE642_REGRAS.md` (com a seção 16, o inventário: C · Subsolo e C · Térreo), com as escalas primeiro. Nada foi retocado ainda; a lista aguarda a confirmação do usuário (seção 1 das regras).

- **Como foi conferido:** o PDF de cada pavimento vai ao quadro da prancha pela cadeia das bases (`opcoes_1pav_casae.quadro_pdf`, com a config da Casa C): 59,7 px/m, as paredes do PDF caem sobre as da prancha e o elevador do Subsolo sobre o do Térreo. Lado a lado, trecho a trecho, e com as camadas DOC_LINHAS E PROJEÇÕES, ARQ_ELEMENTOS FIXOS, ARQ_PAISAGISMO e ARQ_ESCADAS E RAMPAS desenhadas por cima. O PDF da Casa C não tem a EST_PILAR.
- **Mapas e escalas:** `conferencia_casac.py` (em `POE642_CasaA/scripts/`), com os itens em `PENTE_FINO`: `POE642_CasaC/renders/POE642_CasaC_PH_{Subsolo,Terreo}_pente_fino_mapa.jpg`; a folha das escalas (pisos da prancha ao lado dos da biblioteca, trechos de 1,5 × 1,5 m com régua de 1 m, e a vegetação) em `POE642_CasaC/renders/POE642_CasaC_PH_escalas_conferencia.jpg` (`--escalas`).
- **Leitura das escadas no PDF:** degraus largos numerados de 1 (junto ao pátio) a 10 (junto ao caminho) e a escada estreita de 11 a 21 até o deck. O Térreo tem o "D" no degrau 21 (desce do deck); o Subsolo tem o "S" no degrau 11.
- **Térreo (23 itens):**
  1. vegetação grande demais (leques de palmeira de ~2 m, folhas de costela-de-adão de ~1 m);
  2. pedra portuguesa: pedras arredondadas regulares de ~10 a 12 cm, em caramelo; a pedra é de 6 a 8 cm, em leque;
  3. granito marrom quase liso e escuro (~82, 61, 55; a referência ~118, 89, 69, com nuvens e lascas);
  4. travertino com estrias verticais contínuas (o da biblioteca, veios horizontais de 5 a 20 cm);
  5. vinílico liso, sem réguas (réguas de ~20 cm);
  6. Bege Bahia liso e rosado (~229, 212, 198), sem as nuvens nem o tom quente (~230, 211, 186);
  7. grama de grão miúdo e clara; deck avermelhado (troca do tom como na Casa B);
  8. carros prata, alinhados, de 4,70 × 1,85 m (hoje ~4,47 × 1,91 m, em três cores);
  9. a final refeita em 3840 px como a da Casa B (`final3840_casac.py`), guardando as decisões de 14/10 (itens 1 a 25);
  10. rótulos: os 46 ambientes e o elevador; no PDF, SUÍTE MASTER, QUARTO 1 e QUARTO 3 caem sobre a cama e GOURMET sobre a bancada;
  11. portas sem arcos (25 de giro, os portões da área descoberta e a pivotante);
  12. escadas com linhas e triângulo (a estreita desce do deck, triângulo junto ao deck apontando para a esquerda; os largos descem do caminho para o pátio, triângulo no 10 apontando para cima);
  13. guarda-corpos de vidro da ARQ_ELEMENTOS FIXOS, hoje ausentes: o L da varanda master (7,2 m em cima, 9,7 m à esquerda), a borda da varanda dos quartos (6,3 m) e a da varanda 1 (2,9 m);
  14. **a confirmar:** o L junto ao deck é floreira em L no PDF (ARQ_PAISAGISMO, mureta de ~10 cm); hoje é o banco de bronze da Casa B, posto por analogia em 14/10;
  15. projeções tracejadas: claraboias da varanda master e dos closets master 1 e 2, os X dos jardins de inverno e da área descoberta, os armários da DOC_LINHAS conferidos um a um;
  16. jardins (inverno 1 e 2, jardim 1) só verdes, plantas na escala, sem passar dos vidros e paredes;
  17. as 7 cortinas do PDF em linho, um pano por janela;
  18. esquadrias finas (portas de correr das varandas e da suíte master, janelas da cozinha e da área descoberta);
  19. todas as bacias com tampa e cubas brancas;
  20. tapete da sala TV no contorno do PDF;
  21. paredes pretas no contorno do PDF;
  22. soleiras (R13), a do elevador em inox;
  23. banquetas da ilha sob o tampo e box no granito em cinza claro (regras de 22/10); **a confirmar:** bancadas em pedra areia humanizada, como na Casa B.
- **Subsolo (13 itens):**
  1. R2 com a hachura do lote do Térreo final; **a confirmar** o que fica em cor cheia (proposta: Subsolo, pátio, degraus largos e caminho, o cinza cheio do PDF do Subsolo);
  2. a 4. Bege Bahia, travertino e vinílico na escala;
  5. floreira junto à sauna: as folhas passam por cima dos degraus largos;
  6. escadas (R14): **a confirmar** o triângulo no degrau 1 (largos, sobe do pátio) e no 11 (estreita, esmaecida);
  7. as 3 portas sem arcos;
  8. vidros finos (parede da academia e porta da sauna);
  9. rótulos (5 ambientes e o elevador);
  10. bacia com tampa;
  11. soleiras;
  12. paredes;
  13. a final refeita em 3840 px.

### Casa C · a final refeita em 3840 px (22/10/26)

Respostas do usuário às perguntas dos mapas: "1. BANCO EM BRONZE FOSCO; 2. OK; 3. DE ACORDO; 4. PEDRA AREIA; 5. EM 3840 PX". Ou seja:
- o L junto ao deck fica banco em bronze fosco;
- no Subsolo, em cor cheia o Subsolo, o pátio, os degraus largos e o caminho, e o resto do lote na hachura do Térreo final;
- os triângulos das escadas como propostos;
- bancadas e ilhas em pedra areia com cubas brancas, como na Casa B;
- as duas finais refeitas em 3840 px, guardando as decisões de 14/10.

Depois, vendo a final do Térreo: "PODE MANTER O JOGO DE CAMA QUE ESTAVA ANTES." e "MANTENHA OS BANCOS QUE ESTAVAM EM FRENTE AS CAMAS TAMBÉM": as camas e os bancos ao pé delas voltam a ser os do render aprovado, sem a roupa de cama da biblioteca.

- **Como:** módulo novo `scripts/final3840_casac.py`. A Casa C tem a mesma folha, o mesmo recorte, a mesma escala e as mesmas cores de legenda da Casa B, então ele usa o motor do `final3840_casab.py` como está e só troca o que é da casa (`contexto_c`): pastas, config, PDF, base chapada, o render aprovado de 14/10 como partida e as coordenadas em pt do PDF da Casa C. Comandos no README dos scripts ("A final da Casa C em 3840 px").
- **Térreo, item a item:**
  1. vegetação da biblioteca no tamanho real, nos lugares das plantas do render;
  2. a 7. pisos da biblioteca na escala: pedra portuguesa, granito, travertino, vinílico, Bege Bahia, grama e deck (granito, Bege Bahia e grama no tom das finais da Casa B);
  8. os 3 carros prata, alinhados, no retângulo do PDF;
  9. tudo desenhado no quadro da prancha;
  10. 47 rótulos, pretos nos pisos claros e brancos no granito e nos jardins, fora dos objetos;
  11. sem arcos: os 30 do PDF, inclusive o da pivotante do hall (2,1 m, maior que o limite do motor da Casa B) e os das portas dos boxes dos BH master 1 e 2, que o PDF da Casa C desenha na ARQ_BANCADAS;
  12. as duas escadas com a linha suave nos bocéis, a sombra curta e o triângulo: a estreita junto ao deck, apontando para a esquerda; os largos no degrau 10, apontando para cima;
  13. os 4 guarda-corpos de vidro da ARQ_ELEMENTOS FIXOS;
  14. o banco em L em bronze fosco;
  15. projeções em tracejado: claraboia, closets e o X do BH master 2 em cinza escuro; os X dos jardins e da área descoberta em cinza claro;
  16. jardim de inverno, jardim de inverno 2 e jardim 1 só verdes, no canteiro do PDF;
  17. cortinas de linho nos 8 trechos de ondas do PDF (2 na suíte master e 2 em cada quarto; o mapa contava 7), com os trilhos de parede a parede;
  18. esquadrias finas;
  19. tampa em todas as bacias e cubas brancas;
  20. tapete da sala TV (o conjunto da sala TV fica o do render, ver abaixo);
  21. paredes pretas no contorno do PDF;
  22. soleiras nos vãos brancos do PDF; a do elevador em inox escovado, entre os batentes (no PDF não é vão branco, e ali ficava o travertino);
  23. banquetas da ilha sob o tampo, cooktops de 5 bocas, guarda-roupas com cabides e bancadas em pedra areia.
- **O que fica como no render aprovado** (as peças do PDF saíam piores que o render):
  - os dois conjuntos do estar e a sala TV: no PDF, o tapete orgânico do estar é um desenho de 210 traços que cobria o sofá curvo, e as poltronas e os sofás são só contorno (o sofá da sala TV saía sem as almofadas);
  - as banquetas sob o braço da bancada gourmet (decisão de 14/10, item 9);
  - as camas e os bancos (pedido do usuário).
  - os dois vasos junto ao sofá curvo do estar: a planta da biblioteca saía com manchas claras em volta; entram as folhas do render, com a sombra curta;
  - nas zonas do estar e da sala TV, os pedacinhos de piso novo que entravam entre as linhas dos estofados (a legenda tem travertino ali) e davam pintas amareladas no sofá voltam ao render.
- **Piscina:** no deck, na piscina, na prainha e no spa, as paredes estruturais da ARQ_PAREDE são brancas e finas como vidro; com as bordas de fora e o vidro da borda infinita, o motor as tomava por uma esquadria do tamanho da piscina e clareava os degraus da prainha. A zona fica fora das esquadrias (`VIDROS_FORA_C`), e o vidro da borda infinita é o do render, fino.
- **Lavabo junto à adega:** a faixa de 1,6 × 0,6 m junto à parede de cima sai em granito: o PDF a pinta com o preenchimento da cozinha e da gourmet, e a legenda também (o render a fazia em madeira).
- **Fora do lote:** as marcas muito claras abaixo do lote vêm do render aprovado e já estavam na entrega anterior; ficaram como estavam.
- **Subsolo, item a item:**
  1. cor cheia no Subsolo, no pátio, nos degraus largos e no caminho (com a escada estreita esmaecida); o resto do lote do Térreo final na hachura;
  2. a 4. Bege Bahia, travertino (veios horizontais) e vinílico (réguas deitadas) na escala;
  5. floreira junto à sauna com as plantas da biblioteca, dentro do canteiro (nada sobre os degraus);
  6. degraus largos em Bege Bahia, com a linha suave, a sombra curta e o triângulo no degrau 1 (para baixo); a estreita esmaecida, com o triângulo no 11 (para a direita);
  7. as 3 portas sem arcos;
  8. a parede de vidro da academia e a porta da sauna finas;
  9. 6 rótulos: varanda subsolo, academia, depósito, sauna, BH academia e elevador (a VARANDA SUBSOLO saía junto com o título da folha, "-1. 1º SUBSOLO", no filtro por "SUBSOLO"; agora o filtro é o título exato);
  10. a bacia do BH academia com a tampa e a cuba branca;
  11. as 3 soleiras dos vãos brancos e a do elevador em inox escovado;
  12. paredes pretas no contorno do PDF;
  13. tudo no quadro da prancha; o banco da sauna em L, em dois níveis de travertino.
  - **Os aparelhos da academia ficam os do render:** pelo PDF, as esteiras, as bicicletas e os supinos saíam como silhuetas cinza chapadas, sem a lona e sem as barras. Entram os px neutros do render sobre o vinílico novo, com a sombra curta.
- **Imagens:** `POE642_CasaC/renders/POE642_CasaC_PH_{Terreo,Subsolo}_final_rotulos.png`; pranchas `entrega/POE642_CasaC_PH_{Terreo,Subsolo}_entrega.png` e o PDF `entrega/POE642_CasaC_Plantas_Humanizadas.pdf`. Antes e depois enviados na conversa.

**Para refazer** (da pasta `POE642_CasaA/scripts/`; as etapas ficam em cache em `$TMPDIR/poe642_casac_etapas`, e `--de <etapa>` recomeça dali):

```
python3 final3840_casac.py Terreo
python3 final3840_casac.py Subsolo      # depois do Térreo: a hachura vem do Térreo final
python3 rodape_entrega.py --config ../../POE642_CasaC/config_bases.json --no-quadro \
    --render Terreo=../../POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png \
    --render Subsolo=../../POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_final_rotulos.png
python3 pdf_entrega.py --config ../../POE642_CasaC/config_bases.json
```

## Casa D · pente fino pelas regras (22/10/26)

Pedido do usuário: "Casa D" (a última da ordem da seção 17 das regras: Casa E, Casa A, Casa B, Casa C, Casa D). As duas pranchas de entrega atuais (`POE642_CasaD/entrega/POE642_CasaD_PH_{Subsolo,Terreo}_entrega.png`, de 15/10) foram conferidas trecho a trecho contra os PDFs do cliente e o `POE642_REGRAS.md`, com as escalas primeiro. Nada foi retocado ainda; a lista aguarda a confirmação do usuário (seção 1 das regras).

- **Como foi conferido:** o PDF de cada pavimento vai ao quadro da prancha pela cadeia das bases (`opcoes_1pav_casae.quadro_pdf`, config da Casa D): 59,7 px/m; as paredes do PDF caem sobre as da prancha e o elevador do Subsolo sobre o do Térreo. Lado a lado, trecho a trecho, e com as camadas DOC_LINHAS E PROJEÇÕES, ARQ_ELEMENTOS FIXOS, EST_LAJE e ARQ_ESCADAS E RAMPAS desenhadas por cima. O PDF da Casa D não tem a EST_PILAR.
- **Mapas e escalas:** `conferencia_casad.py` (em `POE642_CasaA/scripts/`), com os itens em `PENTE_FINO`: `POE642_CasaD/renders/POE642_CasaD_PH_{Subsolo,Terreo}_pente_fino_mapa.jpg` e a folha das escalas `POE642_CasaD/renders/POE642_CasaD_PH_escalas_conferencia.jpg` (`--escalas`).
- **O que o PDF tem e a prancha não mostra:** 12 panos de cortina (ondas da ARQ_LOUÇAS E METAIS); os brises de ripas da ARQ_ELEMENTOS FIXOS (dos dois lados da porta pivotante do hall, na lateral direita da garagem, na lateral da suíte 3 / escritório e em duas faixas da fachada de baixo), com o tracejado da cobertura ao lado; os guarda-corpos de vidro em volta do vão da escada e na borda do terraço da piscina; os X tracejados do banho master e do jardim do lavabo (DOC_LINHAS); 22 arcos de porta no Térreo e 10 no Subsolo a tirar; os rótulos (33 ambientes e o elevador no Térreo, 6 e o elevador no Subsolo).
- **Leitura da escada:** a de 16 degraus junto à suíte master sobe do Subsolo ("S" no degrau 1, junto ao pátio, numerada de 1 a 16 da esquerda para a direita; no Subsolo, cheia até a marca de corte no degrau 7). No Térreo é a chegada: triângulo no degrau 16 apontando para a esquerda; no Subsolo, no degrau 1 apontando para a direita.
- **Térreo (23 itens):**
  1. vegetação grande demais (leques de ~2 m), avançando ~2,5 m pelo gramado junto à suíte 3;
  2. **a confirmar:** granito no desenho e no tom da referência das outras casas (~118, 89, 69) ou no Marrom Tabaco de 15/10 (~90, 66, 50); hoje escuro (~75, 56, 49) com pontos brancos, e o do Subsolo em outro tom;
  3. travertino com estrias verticais contínuas;
  4. vinílico em réguas largas e lisas (réguas de ~20 cm, deitadas como no PDF);
  5. Bege Bahia liso e rosado com riscos brancos;
  6. grama clara e de grão miúdo;
  7. carros em três cores (15/10) e de ~4,3 a 5,1 m: prata, alinhados, 4,70 × 1,85 m (R12);
  8. a final refeita em 3840 px como as das Casas B e C, guardando as decisões de 15/10;
  9. rótulos (GARAGEM cai sobre o carro do meio no PDF);
  10. portas sem arcos (22);
  11. escada de 16 degraus com linhas e triângulo;
  12. blocos em cascata à esquerda da piscina em Bege Bahia, com contorno e sombra; **a confirmar:** o triângulo descendo;
  13. guarda-corpos de vidro (vão da escada e borda do terraço);
  14. brises de ripas com o tracejado da cobertura; **a confirmar:** a cor (madeira ou grafite);
  15. projeções tracejadas (os X do banho master e do jardim do lavabo, os da garagem e da área descoberta mais visíveis);
  16. jardins da sala íntima e do lavabo só verdes, plantas na escala;
  17. as 12 cortinas;
  18. esquadrias finas;
  19. bacias com tampa e cubas brancas (as da cozinha e do serviço hoje em inox);
  20. paredes pretas;
  21. soleiras (R13) e a do elevador em inox;
  22. banquetas sob o tampo e box do banho gourmet em cinza claro; **a confirmar:** bancadas em pedra areia, como nas Casas B e C;
  23. **a confirmar:** camas e bancos do render (como na Casa C) ou a roupa de cama da biblioteca.
- **Subsolo (10 itens):**
  1. R2 com a hachura do lote do Térreo final, em cor cheia o Subsolo e o pátio; **a confirmar:** a área verde de 15/10 fica verde ou entra na hachura;
  2. a 4. Bege Bahia, vinílico e granito na escala (o granito igual ao do Térreo);
  5. escada com linhas, cheia até o degrau 7 e esmaecida depois, triângulo no degrau 1;
  6. as 10 portas sem arcos;
  7. rótulos (6 ambientes e o elevador);
  8. soleiras;
  9. paredes;
  10. a final refeita em 3840 px.
- **Respostas do usuário (22/10):** "1. Igual ao das outras casas 2. Em Madeira 3. Sim, para os 3 4. Areia 5. Os do render 6. Hachura". Granito no tom e no desenho da referência (o das Casas B e C); brises em madeira; os três triângulos (escada do Térreo no degrau 16 para a esquerda, a do Subsolo no degrau 1 para a direita, os blocos para a esquerda); bancadas e ilhas em pedra areia; camas e bancos do render; no Subsolo, em cor cheia só o Subsolo e o pátio, e a faixa verde na hachura. Registradas na seção 14 das regras.

## Casa D · final em 3840 px (25/10/26)

Os 23 itens do Térreo e os 10 do Subsolo do pente fino, com as respostas de 22/10, pelo motor das Casas B e C: `POE642_CasaA/scripts/final3840_casad.py` (detalhes no README, seção "A final da Casa D em 3840 px").

- **Térreo:**
  1. pisos da biblioteca na escala (travertino, vinílico, granito e Bege Bahia no tom da referência das Casas B e C, grama); o granito sem as manchas dos carros antigos;
  2. vegetação da biblioteca no tamanho real, só nos cantos da esquerda, junto à piscina e junto à suíte 3 (sem as árvores de 4 m avançando no gramado);
  3. jardins do lavabo e da sala íntima só verdes, com a grama em volta limpa;
  4. 3 carros prata de 4,70 x 1,85 m, alinhados (modelo: o carro branco do render);
  5. móveis, louças e bancadas pelo PDF, em pedra areia com as cubas brancas (também as do banho master, do lavabo e do WC DCE, que o PDF desenha sem o aro);
  6. camas e bancos do render (suíte master, suítes 1 e 2, DCE); o estar da suíte 3, os vasos do hall e a planta da bancada gourmet do render;
  7. cooktops de 5 bocas e 4 banquetas sob o tampo da ilha gourmet;
  8. brises das 10 caixas da ARQ_ELEMENTOS FIXOS em madeira (1.186 ripas), guarda-corpos de vidro (terraço e vão da escada);
  9. paredes pretas, soleiras e a do elevador em inox, esquadrias finas, 12 cortinas de linho;
  10. escada de 16 degraus com as linhas e o triângulo no degrau 16 (para a esquerda), os 10 blocos em cascata em Bege Bahia com o triângulo no terraço (para a esquerda);
  11. projeções em tracejado (X do banho master em cinza escuro; garagem, faixa abaixo dela, área descoberta e jardim do lavabo em cinza claro; a cobertura da garagem);
  12. 34 rótulos dentro dos ambientes, sem tocar objeto (a SUÍTE MASTER saía para o terraço: parte do piso livre à direita da cama; a GARAGEM, do PDF sobre o carro do meio: parte da faixa de cima).
- **Subsolo:** pisos na escala (Bege Bahia, vinílico, granito); aparelhos da academia, cama do DCE 1 e bancada do vestiário com a cuba branca da final aprovada; escada cheia até o corte do degrau 7 e esmaecida depois, triângulo no degrau 1 (para a direita); soleira do elevador em inox; 7 rótulos; em cor cheia só o Subsolo e o pátio, e o resto do lote (com a faixa verde) na hachura do Térreo final.
- **Imagens:** `POE642_CasaD/renders/POE642_CasaD_PH_{Terreo,Subsolo}_final_rotulos.png`; pranchas `entrega/POE642_CasaD_PH_{Terreo,Subsolo}_entrega.png` e o PDF `entrega/POE642_CasaD_Plantas_Humanizadas.pdf`. Antes e depois enviados na conversa.

**Para refazer** (da pasta `POE642_CasaA/scripts/`; as etapas ficam em cache em `$TMPDIR/poe642_casad_etapas`, e `--de <etapa>` recomeça dali):

```
python3 final3840_casad.py Terreo
python3 final3840_casad.py Subsolo      # depois do Térreo: a hachura vem do Térreo final
python3 rodape_entrega.py --config ../../POE642_CasaD/config_bases.json --no-quadro \
    --render Terreo=../../POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png \
    --render Subsolo=../../POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_final_rotulos.png
python3 pdf_entrega.py --config ../../POE642_CasaD/config_bases.json
```

## Casas A a D · Barlavento nas piscinas

Pedido do usuário (15/10/26), depois do item 35 da Casa E: as piscinas das Casas A, B, C e D no mesmo revestimento Barlavento, com os mesmos efeitos de água, e as pranchas e os PDFs refeitos.

- **"TODOS OS SANITÁRIOS PRECISAM TER A SUA RESPECTIVA TAMPA":**
  - **O problema:** 9 dos 12 vasos (os suspensos de 0,51 x 0,35 m do PDF, nos banhos das suítes, no lavabo, nos dois BH. gourmet e num banho do Subsolo) saíam abertos, com a abertura e o ralo à mostra. Os 3 de 0,55 x 0,38 m (BH serviço, BH motorista e o serviço do Subsolo) já tinham a tampa no PDF, mas só em traço.
  - **Agora:** etapa `tampas`, logo depois das peças, nos dois pavimentos. Os 12 vasos levam a mesma tampa fechada: da dobradiça à frente, recuada do contorno (fica o aro fino), em louça branca com volume, traço fino e a sombra curta sobre o aro. Só os vasos mudaram na imagem.
  - **Antes e depois:** enviado na conversa (`AD9_tampas_vasos.jpg`).
- **"AQUI SÃO DEGRAUS"** (a área de pedra à esquerda do deck, no Térreo):
  - **O problema:** no PDF, a pedra grande (o patamar no alto da escada de 6 degraus) e as 6 lajes em volta dela são 7 blocos de pedra sobrepostos em cascata (ARQ_CONTRAPISO). A legenda os dava como travertino, e a imagem saía um piso liso, só com o contorno recortado contra a grama.
  - **Agora:** cada bloco é uma peça de Bege Bahia, como os degraus das escadas (`degraus_blocos`, na etapa `escadas`, antes da escada de 6 degraus). Cada um tem uma semente de textura e um tom levemente diferentes, a linha fina do bocel no contorno e, na ordem de pintura do PDF, a sombra curta sobre o bloco de baixo e a grama. O contorno é o do PDF: a pedra grande cobre o canto do deck que a legenda pintava de madeira (no PDF, as tábuas começam à direita dela). No Subsolo, muda só a faixa da hachura que vem do Térreo.
  - **Antes e depois:** enviado na conversa (`AD10_degraus_blocos.jpg`).
- **"NA SEQUÊNCIA DAS PORTAS DE CORRER, EXISTE MURO (EM PRETO)"** (área de serviço descoberta): nas duas laterais, o trecho fino do PDF que segue a porta de correr até o muro de divisa saía como linha cinza na grama; agora é muro preto, na espessura do caixilho (`PAREDES_F["muros_pt"]`).
- **Jardim de inverno** ("TEMOS VIDRO EM CIMA E EMBAIXO E PORTAS DE VIDRO NA LATERAL ESQUERDA. NOTE QUE O PISO EM TRAVERTINO ESTÁ PRESENTE NAS BORDAS. SEM CORES QUENTES, APENAS VERDE"):
  - **O problema:** o canteiro ocupava a sala inteira e passava por cima do vidro de baixo e da porta de correr; tinha a planta com flores rosadas e a comigo-ninguém-pode (creme), e terra marrom à mostra; sob o vidro de baixo ficavam dois borrões escuros do render.
  - **Depois (refeito, ver abaixo):** a sala em travertino (o piso do PDF), com o canteiro recuado 0,30 m dos vidros e das paredes; só plantas verdes (costela-de-adão, folhas largas, palmeiras, arbustos), forração fechada e chão verde-escuro; vidros e porta de correr limpos; a faixa sob o vidro de baixo em travertino (`jardins`).
- **Jardim do hall (4,62 m²)** ("VAMOS MELHORAR AS BORDAS DO TRAVERTINO E A PORTA DE VIDRO DE CORRER. NA PARTE DE BAIXO DO JARDIM, PRECISAMOS DO TRAVERTINO E OS BRISES BEM DESENHADOS"):
  - o canteiro no retângulo exato do PDF, sem planta passando para o travertino, com só plantas verdes;
  - a faixa de baixo, até a pedra portuguesa, em travertino (no PDF era branca e a imagem tinha plantas borradas);
  - os 11 brises nítidos, em grafite, com a aresta da luz mais clara, o contorno fino e a sombra curta (`brises`).
- **"VAMOS HUMANIZAR ESSES MOBILIÁRIOS. SEM QUE ELES PERCAM AS CARACTERÍSTICAS"** (estar da varanda gourmet): mesmas formas, cores e lugares do PDF; os estofados (sofá, almofadas, poltronas, pufe) com volume de almofada e trama de bouclé, o traço técnico mais leve, e a madeira (mesa de centro, banco) com o veio mais marcado (`PECAS["humanizar"]`).
- **"VAMOS REPRESENTAR MELHOR ESSA CAMA E SEU COBRE LEITO. ESTÁ FALTANDO O BANCO QUE ESTÁ ACIMA DA CAMA"** (suíte master):
  - **O problema:** a roupa de cama da biblioteca ia só no colchão; a sobra do cobre-leito do PDF (mais largo que a cama) saía em dois "calombos" brancos; o banco está no PDF, mas na camada DOC_TEXTOS, que as peças não liam.
  - **Agora:** a cama na silhueta do PDF: placa da cabeceira, lençol, dois travesseiros cinza, duas almofadas bordô, o cobre-leito em matelassê off-white dobrado em rolo junto aos travesseiros e caindo dos lados, e a peseira bordô. O banco aos pés, estofado em linho greige, com os três assentos, as costuras tracejadas e os dois rolos (`cama_master`).
- **"PRECISO DO DESENHO SOBRE A MESA"** (mesa redonda do hall interno): o desenho do tampo do PDF (o anel, os cinco painéis e o círculo do meio) saía apagado, lido como hachura; agora por cima, em linha fina nítida, com relevo leve (`desenho_mesa`).
- **"FALTOU A REPRESENTAÇÃO DO GUARDA-CORPO EM L DA VARANDA EM VIDRO"** (varanda da suíte master): as lâminas de vidro do PDF (ARQ_ELEMENTOS FIXOS) na borda do travertino, em cima e à esquerda, que nenhuma etapa desenhava; agora como os vidros das esquadrias, com a sombra curta (`guarda_corpo`).
- **Antes e depois:** enviados na conversa (`AD11_*.jpg`).
- **Jardim de inverno, refeito** ("NÃO HÁ ESSA MOLDURA DE TRAVERTINO. É SOMENTE NA LATERAL ESQUERDA. TEM FOLHAS DE VIDRO EM CIMA E EMBAIXO. SENDO EM CIMA RENTE AO VINILICO. NA LATERAL ESQUERDA, TEMOS AS DUAS FOLHAS DE VIDRO DE CORRER E DEPOIS TRAVERTINO, JÁ PROXIMO AO BRAÇO DO SOFÁ E RENTE AO TAPETE"):
  - **O problema:** a moldura de travertino de 0,30 m em volta do canteiro, por dentro dos vidros, não existe.
  - **Agora:** o canteiro é a sala inteira: do vidro de cima (o da ARQ_PAREDE, encostado no vinílico) ao vidro de baixo, da parede da direita às duas folhas de correr da esquerda, sem planta passando dos vidros. O travertino fica só do lado de fora das portas, entre elas, o braço do sofá e o tapete (`JARDINS_F["inverno"]["canteiro_pt"]`).
  - Com o canteiro encostado nos vidros, o espelho das esquadrias (que troca o px escuro de um lado da faixa do vidro pelo do outro, para não copiar parede preta) trazia o vinílico e o travertino para as folhagens escuras junto ao vidro, em pintas; agora os dois jardins voltam como estavam depois das esquadrias (`esquadrias_terreo`).
- **"NO GUARDA CORPO, TEM UMA FALHA LOGO PERTO DA DOBRA, NA QUINA, E ESTÁ FALTANDO O FECHAMENTO DESSE GUARDA CORPO NO LADO DIREITO"** (varanda da suíte master):
  - **O problema:** o PDF tem três lâminas de vidro (ARQ_ELEMENTOS FIXOS), e só as duas do L entravam; a terceira, em pé à direita, fecha a varanda da quina de cima até a parede. Na quina, por fora do vidro da esquerda, a legenda deixava um toco cinza-escuro de ~10 px no lábio de travertino (a laje passa 2,3 pt do vidro), e as pontas das lâminas deixavam um dente de meio px.
  - **Agora:** as três lâminas, com as pontas passando 0,6 px para as quinas fecharem (a da direita encosta na parede, que é pintada por cima); o lábio por fora do vidro da esquerda fica contínuo, no tom do travertino, até a quina (`PAREDES_F["guarda_corpo"]`).
- **Antes e depois:** enviados na conversa (`AD12_*.jpg`: jardim de inverno, guarda-corpo, a quina e o fechamento da direita).
- **"TEM DUAS LINHAS EM DESTAQUE. UMA DELAS SERIA UMA LINHA SUAVE DO BRAÇO DO SOFÁ, QUE TERMINA ANTES. E A LINHA DA DIREITA NÃO EXISTE"** (sofá do living, junto às portas de correr do jardim de inverno):
  - **O problema:** o espelho que limpa os vidros das esquadrias copia uma faixa de ~5 px de cada lado de cada folha. A borda do sofá está a 5 px da porta: a faixa a copiava junto à porta (a linha da direita, que não existe), levava a linha de baixo do braço até a porta e apagava o fim da borda junto à folha de baixo. Entre o sofá e a porta, o render deixava o tecido do sofá.
  - **Agora:** a faixa entre o sofá e a porta volta como estava antes do espelho (`ESQUADRIAS_F["de_volta_pt"]`) e fica em travertino, como no PDF (`travertino_pt`). O sofá termina na borda do PDF, com uma linha só, e a do braço para nela.
- **"REMOVA ESSAS MARCAÇÕES TÉCNICAS SOBRE O TAMPO DA MESA"** (mesa de jantar do living): os cantos tracejados em laranja (ARQ_MOBILIÁRIO) e as duas elipses no meio (ARQ_LAYOUT HUMANIZAÇÃO) saíam como linhas escuras na madeira. Saem todos os traços laranja do PDF (também os dois do aparador abaixo da mesa; os das mesas redondas da varanda já não apareciam, porque elas vêm da biblioteca) e as duas elipses (`PECAS["marcas"]`).
- **"ADICIONE O TRIANGULO DESCENDO NESSE DEGRAU"** (a laje da direita da cascata de pedra, que sai da pedra grande para a grama junto ao deck): primeiro entrou no alto da laje, apontando para baixo. O usuário marcou o lugar certo ("O TRIÂNGULO É ONDE EU APONTEI"): no deck, junto à borda direita da laje, apontando para ela (a descida é do deck para a laje). Agora fica ali, com a ponta a 1,5 pt da borda (447 pt), a 1097,7 pt de altura, no tamanho e na cor dos das escadas (`BLOCOS_F["triangulos_pt"]`: a ponta e o sentido).
- **"TEM UM ERRO NESSA PORTA"** (a porta da suíte 3, junto ao guarda-roupa e ao lavabo):
  - **O problema:** dois defeitos. (1) Sob a folha aberta, uma lasca bege com a borda ocre: o espelho que limpa as esquadrias copia ~6 px de cada lado de cada folha, e 7 px abaixo da folha começa o guarda-roupa. (2) Pintas escuras na linha do arco que saiu (R3): na base chapada o arco é uma linha tracejada; os px de antialias dele sobre o vinílico, marrom-escuros (45, 68, 91), caíam na tolerância do granito (50, 66, 90) e viravam granito; e o preto do traço ficava fora do piso.
  - **Agora:** a faixa sob a folha volta como estava antes do espelho (`ESQUADRIAS_F["de_volta_pt"]`); e o traço dos arcos das portas do PDF entra no piso em volta (`arcos_porta`, `ARCOS_F`), em todas as portas: 25 no Térreo e 4 no Subsolo. Em cada material, as manchas soltas da legenda que outro piso cobre (antialias de traço com a cor de outro piso, `soltos`) ficam com o piso em volta; as soltas junto a uma peça, sem outro piso ali (a pedra portuguesa junto aos carros), ficam como estavam. A textura de cada piso continua a mesma (sai na máscara inteira e só não é pousada nelas). As portas das suítes 1 e 2 e do closet, também junto a guarda-roupas, foram conferidas e não tinham a lasca.
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

## Auditoria das especificações de 26/10 (todas as casas)

Pedido do usuário (26/10/26), as 11 especificações (E1 a E11) estão na seção 19 do `POE642_REGRAS.md`. Ele disse: "Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."

- **Método:**
  - cada PDF do cliente posto no quadro da prancha (o `quadro_pdf` do `opcoes_1pav_casae.py`), a 59,7 px/m;
  - checagens automáticas: cor das paredes (os preenchimentos escuros da ARQ_PAREDE), cor dos pilares (EST_PILAR), arcos de porta visíveis, bancada x piso (ΔE no Lab), escadas;
  - conferência visual trecho a trecho (prancha em cima, PDF embaixo), porta a porta (soleiras e raios) e piso a piso (as escalas lado a lado, com barra de 1 m).
  - Os scripts de conferência ficaram no rascunho da sessão (não entram no fluxo); o que entra no repositório é o mapa.
- **Mapas:** `POE642_CasaA/scripts/auditoria_2610.py` (as listas `ITENS`, em px do quadro) desenha os 12 mapas numerados em `POE642_Casa?/renders/POE642_Casa?_PH_<pav>_auditoria_2610.jpg`. Só aponta; não altera nenhuma imagem.
- **Prévia do estilo proposto** (Casa B, Térreo; só para aprovação, as pranchas não mudaram): `_auditoria_2610/POE642_proposta_estilo_2610.jpg` e os tons de parede em `_auditoria_2610/POE642_proposta_tons_parede.jpg`. Mostra:
  - paredes em RGB 70 e pilares pretos;
  - as linhas dos degraus do PDF em cinza-escuro, com a linha de percurso do PDF e a letra S/D do PDF no lugar do triângulo;
  - a seta da entrada;
  - a borda e a sombra da bancada.
  - Os PDFs trazem S ou D em todas as escadas (texto de 6,4 pt): A Subsolo S; A Térreo S, S, D; A 1º Pav D, D, D; B Subsolo S, S; B Térreo D, D; C Subsolo S; C Térreo D; D Subsolo S; D Térreo D; E Subsolo S; E Térreo D, S; E 1º Pav D.
- **Resultado:**
  - E1 (soleiras) e E6 (raios) conformes em todas as plantas;
  - E10 (paredes pretas) e E3/E8 (triângulos) inconformes em todas;
  - E4: nenhuma das 5 entradas tem seta;
  - E2, E5, E7 e E9 por planta, nos mapas;
  - E11: madeiras e granito das Casas A e E mais largos e borrados que os de B, C e D (`_auditoria_2610/POE642_escala_pisos_casas_A_a_E.jpg`);
  - fora das 11: uma linha tracejada vertical espúria (x = 1472 px) na suíte master e no banho master do 1º Pav da Casa A.
- **Perguntas em aberto:**
  - o tom de cinza das paredes (50, 70 ou 90);
  - se o tapete conta como objeto para os rótulos;
  - o OK por item ou por planta.

## Casa A · Subsolo com os pedidos de 26/10 (final em 3840 px)

**Aprovado** pelo usuário (26/10/26): "OK, subsolo da casa A aprovado". Próxima planta da auditoria: Casa A · Térreo.

**Casa A · Térreo (apresentado para o OK, nada alterado ainda):** a lista do mapa (`renders/POE642_CasaA_PH_Terreo_auditoria_2610.jpg`) com o que mudou desde a auditoria (paredes em cinza 80; escadas sem linhas, com o sombreamento e a letra do PDF: S na escada interna do jardim, S na caracol, D no lance do deck; os pisantes não têm letra no PDF, proposta D no degrau de cima; o rótulo SALA DE ESTAR fora do tapete) e a folha das texturas `_auditoria_2610/POE642_CasaA_Terreo_texturas_2610.jpg` (mesma ampliação, barra de 1 m): o Bege Bahia e o deck já estão no padrão das Casas B a D; o granito está mais borrado e com pintas maiores (E11); o travertino do Térreo é rosado e quase liso, sem os veios do Subsolo aprovado e da Casa B (pergunta ao usuário: igualar ao da Casa B, levigado, no creme do Subsolo, ou manter).

Pedidos do usuário (26/10/26), além da auditoria:
- "Subsolo da casa A: Melhore o aspecto do Mármore travertino bruto em suas respectivas áreas; Melhore a representação do banco em mármore travertino bruto da sauna; Note que você usou o travertino na área do elevador. Essa área ficou bem representada no mármore, mas deveria ter um elevador, assim como fizemos em outras casas; Melhore a representação dos chuveiros; Melhore a representação dos armários do depósito - em marcenaria; Melhore a representação das folhas contínuas dos boxes; E faça os ajustes da auditoria."
- "Ainda para o subsolo da casa A: Cubas dos banhos de serviço em marrom granito: Mantem a bancada das cubas em mármore travertino bruto. Sanitarios em marrom, não branco. A parede que divide os banhos masculino e feminino deve ser representado como parede em cinza 80."
- "Já o banho serviço tem piso em mármore bege bahia; cuba branca, bancada da cuba em marrom granito e chuveiro bem representado." e "louças de metais" (as louças e os metais do banho de serviço, nítidos).
- Respostas às perguntas da auditoria: paredes em cinza 80; "O tapete conta como objeto, sim."; "vou aprovar planta por planta".

Leitura: os "banhos de serviço" do primeiro pedido são os banhos feminino e masculino (os que têm as cubas na bancada de travertino); o banho de serviço tem o pedido próprio. O vaso do banho de serviço fica branco (não foi pedido em marrom).

**Como foi feito** (`POE642_CasaA/scripts/final3840_casaa.py`, no motor das Casas B a D): a final aprovada, sem os rótulos, no quadro de 3840 px (`rotulos_casaa.final_imagem("Subsolo")`), redesenhada etapa por etapa pelo PDF e pela base chapada:
1. `pisos`: travertino bruto (hall, sauna, antessala, banhos fem. e masc.) na escala das Casas B a D, no creme delas (a sauna da Casa B; o da Casa A estava rosado), com os veios horizontais e os poros; Bege Bahia (pátio, circulação, depósito e banho de serviço, que era Barlavento) no tom das Casas B a D; a madeira da academia nas réguas do vinílico das Casas B a D (E11), com os aparelhos da final e a sombra curta. As peças da ARQ_PAREDE que a final mostra (parede, vidro, batente) ficam; as que ela mostra como piso (as folhas de porta que a base tirou) viram piso. A soleira da academia para o hall fica.
2. `banhos`: bancadas em travertino bruto mais marcado que o piso (E9: o desenho mais forte, o tom mais fundo, a borda no tom escurecido da pedra e a sombra curta); cubas em granito marrom (borda polida, bacia funda com a sombra por dentro, válvula); torneiras cromadas; vasos marrons; descargas; no banho de serviço, bancada em granito marrom (o polígono do PDF), cuba branca de semiencaixe, torneira, vaso branco; os três chuveiros (placa cromada de ~19 cm com os furinhos, braço e canopla; o do banho de serviço, de 7 cm no PDF, vira a placa das outras no mesmo centro); os boxes com as duas folhas contínuas do PDF (`AJ.folhas_box`), mais visíveis, e o trilho tracejado até a parede.
3. `sauna`: o banco em travertino bruto, com a quina boleada na frente e a sombra de contato no piso.
4. `elevador`: a cabine de aço (paredes, piso escovado com o brilho, painel, X fraco, corrimãos, folhas telescópicas à esquerda) e a soleira em inox no vão; o poço em volta em cinza.
5. `deposito`: os dois armários da DOC_LINHAS em freijó (usuário: "para o armário do deposito use a madeira feijó" e "sem linhas e marcações"): o bege-dourado do freijó com o veio reto e fino e as listras mais escuras no comprido de cada braço, uma peça contínua, sem os módulos das portas, sem a linha da frente e sem contorno; só a sombra curta no piso. Um defeito da foto do Bege Bahia da biblioteca (uns tracinhos escuros) que caía no piso logo abaixo do armário foi coberto com a pedra ao lado (`MARCAS_BEGE`).
5b. `portas` (pergunta do usuário: "as portas de vidro de correr que fecham a academia estão bem representadas?"; não estavam: vinham de 2000 px, uma linha cinza borrada): as duas portas de correr da academia redesenhadas pelo PDF na resolução da prancha, na regra da porta de correr: do pátio, as 4 folhas nos 2 planos, com os montantes e os batentes (o piso do pátio passa por baixo, sem soleira); do hall, as 2 folhas desencontradas sobre a soleira de Bege Bahia refeita nítida (R13). Comparação com o PDF em `renders/POE642_CasaA_PH_Subsolo_2610_portas_vidro_antes_depois_pdf.jpg`. Na mesma etapa, o vidro fixo em L da sauna (usuário: "corrija essa falha ao final da esquadria"; o fim do vidro junto à parede da esquerda saía esfumado, com um vão claro e um dente no canto da parede): redesenhado pelo PDF, com o caixilho branco entre as faces escuras e a linha do vidro no meio (na largura do vidro aprovado, ~5 px), os montantes do canto e das pontas e o vão da parede em pedra; a ponta de baixo chega limpa na parede. Depois (usuário: "remova os riscos do contorno do vidro que não fazem parte"), o vão vai sem as faces em cinza: o Bege Bahia dele continua o do pátio, e o contorno é só o do caixilho. E a porta de giro da sauna, que faltava (usuário: "faltou a representação da porta da sauna"; a base tinha tirado a folha e a final aprovada já saía só com o vão): a folha aberta para a antessala, encostada na parede de baixo, como no PDF (~80 cm, com os blocos das pontas), no estilo do vidro fixo da sauna (o caixilho branco entre as faces escuras e a linha do meio), e os dois batentes brancos com o contorno fino; sem o arco (R3).
6. `paredes`: cinza 80 nos preenchimentos escuros da ARQ_PAREDE e na divisória dos banhos (agora parede; substitui o item 94 de 19/10), com a franja preta antiga refeita antes. Na porta da sauna, o vão de ~1,4 pt entre cada batente e a ponta da parede (preto na final) entra como parede (`encostos`), para o batente encostar limpo no cinza.
7. `escada`: sem o triângulo; os degraus em Bege Bahia (usuário: "os degraus da escada que sobem são em mármore bege bahia"; eram o creme chapado da legenda), a foto da biblioteca na escala e no tom das Casas B a D, cada degrau com o tom um pouco diferente, esmaecidos depois da marca de corte como antes; sem linhas (usuário: "a escada e seus degraus ainda estão representados de forma técnica, sem humanização. não precisa constar linhas, mas sim sombras denotando que o sentido é de subida"): o sombreamento de subida das escadas aprovadas da Casa A (cada degrau um pouco mais claro que o de baixo, de 0,84 a 1, e a sombra curta de cada espelho no degrau de baixo e a do 1º no pátio); o S do PDF em Inter SemiBold fica (E3).
8. `rotulos`: `F.rotulos`, com os boxes da Casa A (as duas folhas e o trilho) e a divisória como parede; o BANHO SERV. vai para o piso seco, fora do box (E7).

**Arquivos:** `renders/POE642_CasaA_PH_Subsolo_final_rotulos.png` (+ `_preview.jpg`), `entrega/POE642_CasaA_PH_Subsolo_entrega.png`, `entrega/POE642_CasaA_Plantas_Humanizadas.pdf`; antes e depois em `renders/POE642_CasaA_PH_Subsolo_2610_<item>_antes_depois.jpg` (planta, banhos_sauna, porta_patio, porta_hall, vidro_sauna, porta_sauna, banho_servico, elevador_hall, deposito, academia, escada).

**Atenção:** a final do Subsolo agora sai do `final3840_casaa.py`. Rodar `rotulos_casaa.py Subsolo` sobrescreveria a final com a versão antiga.

**Comandos** (da pasta `POE642_CasaA/scripts/`; o cache das etapas fica em `$POE642_CACHE/poe642_casaa_etapas`):
```bash
python3 final3840_casaa.py --antes <final aprovada antes, PNG>   # a final, com os antes e depois
python3 final3840_casaa.py --de banhos                            # recomeça de uma etapa
python3 rodape_entrega.py --no-quadro --render Subsolo=../renders/POE642_CasaA_PH_Subsolo_final_rotulos.png
python3 pdf_entrega.py
```

## Casa A · Térreo com a auditoria de 26/10 (final em 3840 px)

**Pedido:** a lista do Térreo apresentada para o OK (o mapa `renders/POE642_CasaA_PH_Terreo_auditoria_2610.jpg` e a folha das texturas `_auditoria_2610/POE642_CasaA_Terreo_texturas_2610.jpg`). Respostas do usuário (26/10/26): no travertino, "B" (fica o de hoje); "e aplique a lista". **Aprovado pelo usuário (com os pedidos seguintes e a limpeza dos contornos): "terreo aprovado".**

**Como foi feito** (`POE642_CasaA/scripts/final3840_casaa_terreo.py`, com as rotinas do `final3840_casaa.py`): a final aprovada, sem os rótulos, no quadro de 3840 px (`rotulos_casaa.final_imagem("Terreo")`), redesenhada etapa por etapa:
1. `granito`: o granito das Casas B a D (`fontes_procedurais.granito_referencia`) na cor malva da base chapada, só nos px que a final mostra como piso (os objetos ficam: carros, bancadas, armários, inox, a cama; as pintas claras do granito antigo não contam como objeto). A luz da final passa ao granito novo só onde escurece mais que o desenho da pedra antiga (as sombras dos carros e das bancadas ficam). O tracejado claro das projeções (a laje superior sobre a área de serviço) fica o da final.
2. `motorista`: o armário com os cabides (`_texturas/elementos.guarda_roupa`, os tons dos closets da Casa A, portas para o quarto) e o box em vidro contínuo (as duas folhas do PDF e o trilho, na faixa cinza-clara).
3. `lavabo`: a borda e a sombra da bancada (E9); a pedra, a cuba e a torneira ficam as da final.
4. `paredes`: cinza 80 (`final3840_casaa.paredes`, agora com os parâmetros por pavimento); os muros do lote do PDF (faixas de mais de 300 pt) ficam de fora, porque a linha preta da final fica uns 5 px fora deles: ela mesma passa a cinza 80 (`MUROS`).
5. `deck`, `pisantes`, `escada_u`, `caracol`: as escadas sem triângulo e sem linhas, com o sombreamento e as letras (S na interna e na caracol, D no lance do deck e nos escalonados). O lance do deck reaproveita o `degraus_bege` do Subsolo (agora com o lado esmaecido e a sombra no pátio opcionais).
6. `seta`: a seta da entrada no hall externo.
7. `rotulos`: os desvios aprovados do `rotulos_casaa.py`, com LAVABO no corpo do PDF e SALA DE ESTAR fora do tapete.

**Arquivos:** `renders/POE642_CasaA_PH_Terreo_final_rotulos.png` (+ `_preview.jpg`), `entrega/POE642_CasaA_PH_Terreo_entrega.png`, `entrega/POE642_CasaA_Plantas_Humanizadas.pdf`; antes e depois em `renders/POE642_CasaA_PH_Terreo_2610_<item>_antes_depois.jpg` (planta, granito, motorista, lavabo, degraus_escalonados, lance_deck, escada_interna, caracol, entrada, sala_estar).

**Atenção:**
- a final do Térreo agora sai do `final3840_casaa_terreo.py`; rodar `rotulos_casaa.py Terreo` sobrescreveria a final com a versão antiga;
- o 1º Pavimento usa o Térreo nublado (`rotulos_casaa.final_imagem("Terreo")`, a versão antiga): quando ele passar pela auditoria, trocar pelo Térreo novo (sem os rótulos: a etapa `seta` do cache).

**Comandos** (da pasta `POE642_CasaA/scripts/`; o cache das etapas fica em `$POE642_CACHE/poe642_casaa_etapas`, com o prefixo `Terreo_`):
```bash
python3 final3840_casaa_terreo.py --antes <final aprovada antes, PNG>   # a final, com os antes e depois
python3 final3840_casaa_terreo.py --de paredes                            # recomeça de uma etapa
python3 rodape_entrega.py --no-quadro --render Terreo=../renders/POE642_CasaA_PH_Terreo_final_rotulos.png
python3 pdf_entrega.py
```

### Casa A · Térreo, pedidos seguintes (26/10/26)

**Pedidos do usuário**, depois da lista da auditoria: "melhorar o aspecto do travertino bruto no piso do térreo."; "sanitário do lavabo em marrom escuro."; "nos banheiros da varanda gourmet: sanitários no marrom escuro, cuba esculpida no marrom granito, pedra bancada cuba em mármore travertino bruto levemente escurecido para distinguir do piso."; "Banho serviço: piso em mármore bege bahia, pedra pia em marrom granito levemente escurecida para distinguir do piso."; "o escrito do b. motorista pode ficar mais abaixo e centralizado."; e, durante o trabalho, "pedra da ilha em U da vanrada gourmet é marrom granito, igual ao piso. deixe-a levemente escurecida para distinguir do piso." e "a projeção em tracejado precisa ficar evidente. Em fundos escuros, faça a projeção com tom branco; para tons claros, marque-as com tom preto tracejado."

**Leitura:** no Térreo não há "banho serviço" no PDF; o banho de serviço é o do motorista (o único banho da ala de serviço). **A confirmar com o usuário.**

**Como foi feito** (novas etapas do `final3840_casaa_terreo.py`):
- `granito`: o banho do motorista em Bege Bahia (`GRANITO_T["bege"]`), na mesma máscara e na mesma luz; a bancada e a cuba antigas viram piso (`refaz`);
- `travertino` (nova): o travertino bruto do Subsolo (`final3840_casaa.travertino_bruto`, tom e força do Subsolo) na cor de travertino da base chapada; os móveis são os brancos da base (com 2 px de folga) e o que a final mostra fora do tom do piso (mais claro, de outra cor ou muito escuro); as sombras passam como luz; o tracejado das projeções fica; as louças e a bancada refeitas viram piso antes;
- `loucas` (nova): os vasos marrom-escuros (lavabo, WC, banho varanda), a bancada do lavatório em travertino bruto mais marcado com a cuba esculpida em granito e a torneira, a bancada do banho do motorista em granito mais escuro com a cuba branca, a torneira e o chuveiro;
- `ilha` (nova): a ilha em U em granito mais escuro, com a área molhada rebaixada e a cuba de inox da final;
- `escada_u`: o trecho cheio no travertino novo;
- `projecoes` (nova): os traços tracejados do PDF (`cadeias_tracejadas`: traços colineares com vãos) redesenhados em preto ou branco pelo fundo: DOC_LINHAS (sem os afastamentos e os limites do lote, as linhas dentro das paredes e os X do elevador e do shaft), ARQ_PERGOLADO e o contorno de fora da cobertura (ARQ_CONTRAPISO);
- `rotulos`: o B. MOTORISTA no meio do piso seco.

**Antes e depois** (contra a versão anterior do Térreo): `renders/POE642_CasaA_PH_Terreo_2610_{travertino,banhos_varanda,ilha_gourmet,banho_motorista,projecoes}_antes_depois.jpg`; os de antes (planta, granito, …) seguem contra a final aprovada antes da auditoria.

### Casa A · Térreo, limpeza dos contornos, cooktop da ilha gourmet e bancadas da cozinha (26/10/26)

**Pedidos do usuário:** "faça uma limpeza em contornos. apareceram alguns erros em volta de pisos, bancadas, sanitários, cubas, etc. faça uma auditoria e corrija."; "Me parece que você removeu um cooktop da bancada da ilha da varanda gourmet."; "as bancadas em pedra da cozinha também são no granito marrom, levemente escurecido."

**Auditoria (o que estava errado):** a troca do piso deixava uma folga de 2 a 4 px em volta de cada peça (o piso antigo, rosado, como um anel em volta dos móveis, das louças e das bancadas); os px de traço da base chapada (o antialias entre o piso e a peça) não entravam em nenhuma troca; o miolo branco da base (as louças refeitas) ficava fora da caixa a refazer (o fantasma do vaso antigo no banho varanda); a cuba de inox da ilha era recortada da final com a moldura branca do quartzito; o px da borda das bancadas refeitas levava o branco antigo; a luz do piso caía a zero nos px sem piso por perto (os pontos escuros na divisa dos halls); manchas fracas e restos rosados do render antigo eram tomados por objeto; e o agrupamento do tracejado partia as retas longas (os primeiros traços das diagonais ficavam rosados). O cooktop: o PDF tem um de 5 bocas no braço de cima da ilha em U, e a final aprovada nunca o mostrou.

**Como foi corrigido** (`final3840_casaa_terreo.py`):
- `travertino`: o piso troca até a borda de cada móvel, px a px (`alfa_objetos`); a sombra (mais escura e acinzentada) passa ao piso novo como luz; as manchas fracas são piso; as peças cheias da base (bancadas, armários), as esquadrias e as portas (`paredes_pdf`) ficam; os px de traço da base entram (`traco_chapada`); as caixas a refazer trocam inteiras, menos as paredes (`refazer`), com a luz do piso em volta; a textura é gerada com folga (`travertino_t(..., borda=8)`);
- `granito`: os objetos sem folga (manchas claras ou neutras de 60 px ou mais, com os furos), as pintas soltas do granito antigo são piso; a faixa em volta das bancadas refeitas em granito troca inteira (`anel_bancadas`);
- `nconv2`: nos px sem piso no raio, a luz de um raio maior;
- `ilha`: o cooktop da biblioteca (`cooktop`, o mesmo da ilha da cozinha), a cuba de inox redesenhada (`cuba_inox`) e as linhas do degrau do balcão e das laterais em cascata (`linhas_pedra`);
- `cozinha` (nova): a ilha e a bancada da pia em granito mais escuro, com o cooktop, as laterais, a área molhada e as duas cubas de inox;
- `cadeias_tracejadas`: a distância à origem pela direção do próprio traço, com as faixas vizinhas juntas.

**Decidido com o usuário:** a bancada em L da área de serviço (com os tanques) continua em Carrara (o pedido falou só da cozinha; perguntado, ele respondeu "mantem").

**Antes e depois** (contra a versão anterior): `renders/POE642_CasaA_PH_Terreo_2610_{contornos_moveis,contornos_estar,contornos_banhos,contornos_lavabo,contornos_hall,ilha_cooktop,cozinha_bancadas}_antes_depois.jpg`.


### Casa A · 1º Pavimento, auditoria para o OK (26/10/26)

Pedido do usuário: "1º pavimento da casa A" (a próxima planta, depois do Térreo). Pela regra dele ("Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."), a lista foi apresentada sem alterar a imagem. O mapa numerado: `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_auditoria_2610_v2.jpg` (sobre a final atual, `..._1Pavimento_v7_final_rotulos.png`).

Os pisos pela base do PDF (`bases/POE642_CasaA_BASE_1Pavimento_v3.png`): travertino (oliva) na circulação, na sala íntima e nos banhos 1, 2, 3 e master; vinílico (laranja) nas suítes e closets; Bege Bahia (cinza) no quarto de serviço, na saleta, no B. serviço e nas varandas.

Os 12 itens: (1) paredes em cinza 80 e pilares pretos (E10); (2) escada em U sem triângulos e sem linhas, com o sombreamento de descida e o D do PDF, o trecho dos degraus 1 a 7 do Térreo novo (E3, E8); (3) caracol da saleta, idem (E3, E8); (4) armário do quarto de serviço com os cabides (E2); (5) boxes em vidro contínuo com o trilho (banho master só tracejado; conferir os banhos 1, 2, 3 e o B. serviço) (E5); (6) chuveiros pelo PDF no padrão do Subsolo e do Térreo; (7) rótulos BANHO 3 e B. SERVIÇO longe da linha do box, SALA ÍNTIMA fora do tapete (E7); (8) bancadas dos banhos mais marcadas que o piso (E9), com a pergunta da linguagem dos banhos; (9) pisos na escala (E11): travertino bruto, vinílico nas réguas das Casas B a D, Bege Bahia; (10) a linha tracejada espúria da suíte master e do banho master; (11) projeções tracejadas evidentes, em preto ou branco pelo fundo (R8); (12) o Térreo nublado refeito a partir do Térreo novo. Mais a limpeza dos contornos na troca dos pisos (seção 3).

Perguntas ao usuário: a linguagem dos banhos 1, 2, 3 e master (como nos banhos do Subsolo e no lavatório do Térreo: bancada em travertino bruto mais escuro, cuba esculpida em granito marrom, vaso marrom-escuro) ou o Carrara com louça branca e só a borda (E9); o B. serviço como o banho de serviço do Térreo (pia em granito marrom mais escuro, cuba e vaso brancos).

### Casa A · 1º Pavimento, os 12 itens aplicados (26/10/26)

**Respostas do usuário:** "A. Sim." (banhos 1, 2, 3 e master com a bancada em travertino bruto mais marcado) e "B. mantem"; durante o trabalho: "na descida da escada U é preciso saber onde ela fica nevoada, já no terreo. representando aquela linha em diagonal e enovoar a parte que pertence ao terreo." e "No banho 1 e 2 e 3 e master, a(s) cuba(s) é(são) em mármore travertino bruto e o sanitário branco. No banho serviço a cuba é branca, com bancada da pia em marrom granito e sanitário branco." (o último substitui o "B. mantem" no B. serviço). **Aprovado pelo usuário: "1º pavimento da casa A aprovado".**

**Como foi feito** (`POE642_CasaA/scripts/final3840_casaa_1pav.py`, novo, com as rotinas do `final3840_casaa.py` e do `final3840_casaa_terreo.py`; etapas e comandos no README):
- pisos na escala até a borda das peças (a limpeza dos contornos do Térreo): travertino bruto, vinílico nas réguas, Bege Bahia; nos banhos, as peças antigas viram piso antes; a luz em volta delas vem do piso limpo por inpaint (sem a mancha cinza do chuveiro antigo do banho 3 e as manchas escuras nos boxes do master); a banheira do master protegida (a borda de cima, clara como o travertino novo, era tomada por piso); no 1º Pavimento os traços da DOC_LINHAS não ficam com o piso antigo (viravam tracinhos claros junto à guarda do vazio);
- banhos: cubas em travertino bruto (`FA.cuba_pedra`, a rotina da cuba de granito com outra pedra; a de granito ficou idêntica), vasos brancos; B. serviço como o banho de serviço do Subsolo;
- paredes em cinza 80, sem o limite de 300 pt do Térreo;
- escada em U: os degraus 8 a 19 no travertino do piso, com o sombreamento e o D no 19; os degraus 1 a 7 com o Térreo nublado, recortados pela linha de corte do PDF do Térreo (a diagonal com a quebra), desenhada em cinza escuro; caracol com os cinco degraus do pavimento no travertino da caracol do Térreo e o D;
- o Térreo nublado a partir da final nova do Térreo (as etapas até a caracol, sem as letras);
- projeções em preto ou branco pelo fundo (`T.preto_branco`, separado do `T.projecoes`; o Térreo ficou idêntico), sumindo nas paredes;
- rótulos: BANHO 3 no piso seco, B. SERVIÇO no meio do box (corpo do PDF), SALA ÍNTIMA acima do sofá.

**Item 10, para o OK:** a "linha tracejada espúria" da suíte master e do banho master é, no PDF, o contorno de dentro da cobertura (ARQ_CONTRAPISO, x = 1281,4 pt), a mesma que fecha nos outros lados; ficou como projeção, em preto. Perguntado se sai, o usuário respondeu "mantem": fica.

**Arquivos:** `renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png` (+ `_preview.jpg`), `entrega/POE642_CasaA_PH_1Pavimento_entrega.png`, `entrega/POE642_CasaA_Plantas_Humanizadas.pdf`; antes e depois (contra a final de 21/10) em `renders/POE642_CasaA_PH_1Pavimento_2610_{planta,pisos,banho_master,banho_1,banho_2,banho_3,b_servico,armario,escada_u,caracol,sala_intima,projecoes}_antes_depois.jpg`.

## Casa B · Subsolo, auditoria para o OK (26/10/26)

Pedido do usuário: "prossiga com o subsolo da casa B" (a Casa A está aprovada inteira: Subsolo, Térreo e 1º Pavimento). Pela regra dele ("Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."), a lista foi apresentada sem alterar a imagem. O mapa numerado: `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_auditoria_2610_v2.jpg` (sobre a prancha atual; a v1, de antes, segue em `..._auditoria_2610.jpg`).

A conferência foi trecho a trecho, a final em cima e o PDF no mesmo quadro embaixo. Os pisos pela base chapada: Bege Bahia (232) na garagem, nas duas circulações e no BH serviço; travertino (202, 217, 220) na sauna, no BH sauna com a ducha e no depósito; deck na ducha; madeira na academia.

Conformes: E1 (soleiras), E6 (raios), E2 (não há armário cortado no Subsolo), E11 (as texturas da Casa B são a referência das escalas), os contornos (a final é desenhada pelo PDF) e os demais rótulos.

Os 6 itens: (1) paredes pretas em cinza 80, com o muro que sobe na hachura acima do depósito (E10; não há pilares); (2) escada da ducha, 6 degraus em Bege Bahia, sem o triângulo e sem as linhas, com o S do PDF e o sombreamento de subida do 1º degrau (junto ao deck) ao 6º (E3, E8); (3) os boxes do BH sauna (o vidro entre a ducha e o banho) e do BH serviço (entre o vaso e a ducha) em vidro contínuo com as faces, a sombra e o trilho, como na Casa A (E5); (4) a borda e a sombra das bancadas do BH serviço e do BH sauna (E9); (5) o rótulo CIRCULAÇÃO (2,23 m²) no meio do corredor, sem encostar nas paredes (E7); (6) o rótulo SHAFT do PDF, como no Térreo da Casa A.

## Casa B · Subsolo, a lista aplicada e os materiais dos banhos (26/10/26)

O usuário aprovou a lista ("ok, aplique a lista") e, no meio da aplicação, pediu os materiais dos banhos: "banho sauna: sanitário marrom, cuba esculpida em mármore travertino bruto e e pedra da bancada da cuba em granito marrom; banho serviço: cuba branca, pedra da pia em marrom granito, sanitário branco."

Aplicado na final de 3840 px (`final3840_casab.py Subsolo --de bancadas`; o motor é compartilhado com as Casas C e D, então tudo vai por argumento em `passos_subsolo`):
1. **Paredes em cinza 80** (E10), com o muro que sobe na hachura. As esquadrias passaram a ler a parede cinza (`esquadrias_final(..., parede=)`): antes, a limpeza espelhava o cinza para dentro da faixa da porta e os batentes saíam pretos.
2. **Escada da ducha** (E3, E8): 5 degraus em Bege Bahia sem linhas e sem triângulo, com o sombreamento de subida, a sombra do 1º degrau no deck e o S no 1º degrau (`escada_sombreada`).
3. **Boxes** do BH sauna e do BH serviço em vidro contínuo, com as faces finas e a sombra curta (E5, `boxes_vidro`).
4. **Bancadas** com a borda no tom escurecido da pedra e a sombra curta (E9). Agora em granito marrom, pelo pedido dos banhos.
5. **CIRCULAÇÃO** (2,23 m²) no meio do corredor, no corpo 1,0, sem encostar nas paredes (E7).
6. **SHAFT**, o rótulo do PDF.
7. **Banhos:** BH sauna com as prateleiras em granito marrom, a cuba esculpida em travertino bruto (a rotina da cuba do 1º Pavimento da Casa A) e o vaso marrom (`vasos_cor`, no contorno do PDF); BH serviço com a bancada em granito marrom, a cuba branca e o vaso branco.

Antes e depois: `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_2610_{planta,escada_ducha,bh_sauna,bh_servico,shaft,muro_hachura}_antes_depois.jpg`. A prancha (`POE642_CasaB/entrega/POE642_CasaB_PH_Subsolo_entrega.png`) e o PDF da Casa B (`POE642_CasaB_Plantas_Humanizadas.pdf`) foram refeitos; o Térreo da Casa B não mudou. Aguarda o OK do usuário para o Subsolo; depois, a auditoria do Térreo da Casa B.

### Depois: "melhore o aspecto do marmore travertino bruto" (26/10/26)

O travertino da Casa B era a foto lisa da biblioteca, só com as nuvens. O piso de travertino do Subsolo (sauna, BH sauna com a ducha, depósito) e os bancos da sauna passaram ao travertino bruto aprovado na Casa A (`final3840_casaa.travertino_bruto`: os veios horizontais longos e os poros pequenos), na luz e no creme de antes (`pisos(..., bruto=)`, `bancos_sauna(..., bruto=)`; rodado com `--de pisos`). Os bancos levam o desenho mais marcado das bancadas e mantêm os dois níveis, a linha fina e a sombra discreta. A cuba do BH sauna já era desse travertino. Antes e depois: `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_2610_travertino_{sauna,deposito}_antes_depois.jpg` (os demais antes/depois foram refeitos sobre a final nova). Prancha e PDF da Casa B refeitos. Aguarda o OK do Subsolo.

### Depois: "melhore a representação da cuba esculpida com o marmore travertino, mais claro" (26/10/26)

A cuba do BH sauna saía acinzentada e escura (o tom das bancadas de travertino da Casa A, com a bacia a 0,82), com muitos poros, uma borda de pouco mais de 1 px e um contorno marrom em volta: as tiras do aro, no PDF, eram pintadas como granito, com a borda escura do E9. Agora `cuba_travertino` é uma rotina própria: uma peça só de travertino claro, um pouco mais clara que o piso, com o desenho calmo do travertino bruto; a borda larga (2 pt) com a quina clara do lado da luz; a bacia de cantos bem arredondados e funda, com a parede de cima e da direita na sombra e a de baixo e da esquerda na luz; o contorno fino no tom da pedra, a válvula cromada e a sombra curta na bancada. O retângulo da cuba, com o aro, sai da pedra da bancada. Antes e depois: `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_2610_cuba_travertino_antes_depois.jpg`. Prancha e PDF da Casa B refeitos. Aguarda o OK do Subsolo.

**Aprovado** (26/10/26): "subsolo da casa B aprovado". Próxima planta: o Térreo da Casa B, com a lista apresentada antes de alterar.

### Depois da aprovação: "corrija o local da ducha externa da planta do subsolo, conforme está na planta do térreo. atualize as pranchas" (26/10/26)

O PDF do Subsolo não tem o chuveiro da ducha; ele entrou em 22/10 ("CADÊ O CHUVEIRO?") na parede da sauna, à direita do deck. O PDF do Térreo tem o chuveiro do deck (`final3840_casab.CHUVEIRO_DECK`), e os dois PDFs têm as mesmas coordenadas: `ajustes_casab.CHUVEIRO_DUCHA` passou a esse lugar (a ducha em 690,8–702,0 x 930,4–941,6 pt, o braço até a canopla na parede de baixo, em 958,2 pt), no meio do deck. Rodado com `final3840_casab.py Subsolo --de pecas`. Prancha e PDF da Casa B refeitos.

Depois, com um recorte do Térreo: "a ducha fica mais no canto". No Térreo, o deck visível termina em x 730,5 pt (ali começa a suíte master), e a ducha fica a 28,5 pt dessa borda, com o braço até a borda de baixo; no Subsolo, o deck da ducha vai até a parede da sauna (x 787,2 pt), então nas mesmas coordenadas a ducha caía no meio. Agora ela fica no canto de baixo à direita, a 28,5 pt da parede da sauna (a ducha em 747,5–758,7 x 930,4–941,6 pt), com o braço até a parede de baixo (a face em y 958,0 pt). Antes (na parede da sauna) e depois: `POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_2610_ducha_antes_depois.jpg`. Prancha e PDF da Casa B refeitos.

Ficou em aberto, interrompida por este pedido: a auditoria do Térreo da Casa B (achados até aqui, ainda sem o mapa: paredes pretas (E10); as três escadas com triângulo e linhas, os pisantes NO, os pisantes O e a escada 1-9 da varanda, com o D do PDF em duas delas (E3, E8); os pilares redondos em cinza 130 (pedido de 22/10) contra o preto do E10; a seta da entrada principal (E4); as bancadas da mesma cor do piso, nos banhos master, 1, 2 e 3, no lavabo, no lavatório e na ilha gourmet e na bancada da sala íntima (E9); os boxes em linha fina, não como os vidros do Subsolo (E5); as projeções em cinza (R8 pede preto ou branco pelo fundo); o travertino do piso ainda liso (o Subsolo passou ao bruto); uma linha vertical fina, que não existe no PDF, atravessando a suíte 3 e o banho 3, em x ≈ 2639 px).

## Casa B · Térreo, auditoria para o OK (26/10/26)

Pedido do usuário: "sim, termine a auditoria do térreo da casa B" (o Subsolo está aprovado: "subsolo da casa B aprovado"). Pela regra dele ("Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."), a lista foi apresentada sem alterar a imagem. O mapa numerado: `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_auditoria_2610_v2.jpg` (sobre a prancha atual; a v1 segue em `..._auditoria_2610.jpg`), feito com `auditoria_2610.mapa` e os itens trocados em memória.

A conferência foi em 9 recortes da final a 1:1 e trecho a trecho com o PDF no mesmo quadro (banho 3 e suíte 3, entrada e hall, serviço e garagem, motorista, sala íntima, escadas e deck, suíte master e banho master, suítes 1 e 2), e com os 42 rótulos do PDF.

Conformes: E1 (soleiras), E6 (raios), E2 (cabides nas suítes e nos closets), E7 (nenhum rótulo sobre objeto; nos jardins, em branco), E11 (as texturas da Casa B são a referência), carros (R12). A bancada da sala íntima (o bar com a cuba redonda) é pedra areia sobre a madeira: contraste bom, fora do E9.

Os 13 itens:
1. (E10) paredes pretas em cinza 80, com os muros do lote;
2. (pergunta) os pilares redondos da garagem e do quarto do motorista: cinza (pedido de 22/10) ou preto (E10)? Recomendado: preto;
3. (E4) a seta da entrada principal no HALL, apontando para a porta pivotante do HALL INTERNO;
4. (E3, E8) a escada de 6 degraus (pisantes NO), com o D do PDF;
5. (E3, E8) a escada de 9 degraus, da varanda ao deck, com o D do PDF;
6. (E3, E8) os pisantes O: o PDF não marca o sentido; o D vai no lugar do triângulo de hoje;
7. (E9) as bancadas areia sobre o travertino (banhos master, 1, 2 e 3, lavabo, lavatório gourmet, ilha gourmet), com a borda e a sombra;
8. (E5) os boxes em linha fina (banho master ×2, banhos 1, 2 e 3, BH gourmet ×2), em vidro contínuo como no Subsolo; os do granito (BH serviço e BH motorista) ficam na faixa cinza-clara de 22/10;
9. (R8) as projeções em cinza (pérgola do hall e da garagem, cobertura junto ao living e à sala íntima) em preto ou branco pelo fundo;
10. o rótulo SHAFT do PDF junto ao elevador e o X do shaft ao lado da sala íntima;
11. a linha vertical fina que não existe no PDF, da janela da suíte 3 atravessando o banho 3 (x ≈ 2639 px);
12. o travertino do piso no travertino bruto do Subsolo aprovado;
13. (pergunta) os materiais dos banhos do Térreo: hoje cubas brancas na bancada areia e vasos brancos (22/10). Mantém ou segue algum padrão?

### Térreo da Casa B, a lista aplicada (26/10/26)

Respostas do usuário: "ok, aplique a lista. pilares em preto" e os banhos ("lavabo: cuba esculpida e pedra da bancada da pia em marmore travertino bruto. Sanitário em marrom; banhos varanda gourmet: cubas esculpidas em marrom granito, pedra da bancada da pia em marmore travertino bruto, sanitários em marrom; banho 1, 2 e 3 e banho master - cuba e pedra da pia em marmore travertino bruto, sanitario branco"). Final refeita inteira (`final3840_casab.py Terreo --de pisos`), depois `--de esquadrias`; o Subsolo rodado de novo da hachura sai igual ao aprovado (0 px diferentes).

Os 12 itens e os banhos estão nas REGRAS (seção 19, Casa B · Térreo, e seção 6). Na conferência, três acertos além da lista:
- o trilho da cortina da suíte 3 parava só depois de 6 px seguidos de parede, e a parede do banho 3 tem 4 px ali: a linha "que não existe no PDF" era ele; agora para no 1º px de parede do PDF;
- com a parede em cinza 80, a limpeza da faixa do vidro (que subia o limiar de parede para 95) passava a tratar o granito marrom como parede e manchava o piso junto às portas do motorista e do depósito; no Térreo a parede é reconhecida pela cor;
- no PDF, a linha da cobertura (ARQ_BANCADAS, traços de 5,7 pt) corre também sobre o vidro da porta de correr do living: sai, pela R8; os X dos dois shafts pequenos (diagonais de 36 a 39 pt) entraram baixando o mínimo das cadeias para 30 pt; o X do shaft do elevador abre embaixo do rótulo.

Antes e depois: `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_2610_{planta,escadas,banho_master,banho_1,banho_2,suite3_banho3,lavabo,gourmet,entrada,motorista,shafts,jardim_inverno,living}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa B refeitos. Aguarda o OK do Térreo.

### Depois: "as pedras das bancadas e ilhas da varanda e cozinha são marrom granito. escureça levemente para distinguir do piso" (26/10/26)

As 5 peças da cozinha e da varanda gourmet (a ilha e a bancada do gourmet; a ilha, a bancada da pia e a peça pequena da cozinha) saem da pedra areia para o granito marrom: o desenho do granito de referência (`fontes_procedurais.granito_referencia`), no tom mediano do piso de granito da própria imagem, a 86% (`BANCADAS_F["granito_escuro"]`), com a borda e a sombra curta das bancadas (E9). A escolha é por peça (`pedra_banhos`): as que têm cuba do PDF seguem em travertino bruto; as de centro dentro de `BANHOS_T["granito_pt"]` vão para o granito; as demais (serviço, BH serviço, motorista, adega, bar) ficam na pedra areia. Rodado `final3840_casab.py Terreo --de bancadas`.

### Depois: "essa escada é em marmore travertino bruto" (26/10/26)

A escada de 9 degraus, da varanda para o deck (`B.ESCADAS_S[1]`, com o D à direita), sai do Bege Bahia para o travertino bruto do piso (`final3840_casaa.travertino_bruto`, com os parâmetros do piso, no tom mediano do travertino da legenda na imagem), com o mesmo sombreamento (cada degrau mais claro que o de baixo) e o D no degrau de cima: `escada_sombreada(..., pedra="travertino")`. A de 6 degraus, da pedra grande para a ducha, fica no Bege Bahia. Rodado `Terreo --de escadas`; o Subsolo, de novo da hachura, sai igual (0 px diferentes).

Antes e depois: `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_2610_granito_cozinha_gourmet_antes_depois.jpg` e `..._escada_travertino_antes_depois.jpg` (o antes de cada um é a final anterior ao pedido); `..._{planta,escadas,gourmet}_antes_depois.jpg` refeitos contra a final de antes da auditoria. Prancha do Térreo e PDF da Casa B refeitos. Aguarda o OK do Térreo.

**Aprovado** (26/10/26): "térreo da casa B aprovado". Casa B fechada: Subsolo e Térreo aprovados, prancha dos dois e PDF (`POE642_CasaB/entrega/POE642_CasaB_Plantas_Humanizadas.pdf`) na versão final. Próxima planta: a que o usuário indicar (pela ordem, o Subsolo da Casa C), com a lista apresentada antes de alterar.

## Casa C · Subsolo, auditoria para o OK (26/10/26)

Pedido do usuário: "prossiga com o subsolo da casa C" (a Casa B está aprovada inteira: "subsolo da casa B aprovado" e "térreo da casa B aprovado"). Pela regra dele ("Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."), a lista foi apresentada sem alterar a imagem. O mapa numerado: `POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_auditoria_2610_v2.jpg` (sobre a prancha atual; a v1 segue em `..._auditoria_2610.jpg`), feito com `auditoria_2610.mapa` e os itens trocados em memória.

A conferência foi trecho a trecho, a final em cima e o PDF no mesmo quadro (sauna e BH academia, depósito, degraus largos, escada estreita, varanda, academia e elevador), e com os 7 rótulos do PDF. Os pisos pela base chapada: travertino na varanda, na sauna, na ducha e no BH academia; Bege Bahia no pátio, nos degraus largos, no caminho e no depósito; madeira na academia.

Conformes: E1 (soleiras), E2 (não há armário cortado), E6 (sem raios), as escalas do Bege Bahia, da madeira e da hachura (as da Casa B), a floreira junto à sauna e os rótulos VARANDA SUBSOLO, ACADEMIA, DEPÓSITO e ELEVADOR. O PDF não tem SHAFT no Subsolo da Casa C.

Os 12 itens:
1. (E10) paredes pretas em cinza 80 (não há pilares);
2. (E11) o travertino liso (a foto antiga, só com as nuvens) na varanda, na sauna, na ducha e no BH academia no travertino bruto do Subsolo aprovado da Casa B; os bancos da sauna no travertino bruto mais marcado;
3. (E3, E8) degraus largos (pátio para o caminho, 1 a 10, com os dois em L): o triângulo vira S (o PDF não marca o sentido; vai no lugar do triângulo, subindo do pátio), sem as linhas, com o sombreamento de subida;
4. (E3, E8) escada estreita (11 a 21, esmaecida desde 14/10): o triângulo vira o S do PDF no degrau 11, sem as linhas, com o sombreamento; saem os restos do render (o anel e o traço laranja no degrau 18, a diagonal fraca no 11, o pontinho no 19);
5. (pergunta) a escada estreita depois da linha de corte do PDF (19 a 21): nevoar mais, com a diagonal, como a escada em U do 1º Pavimento da Casa A? Recomendado: sim;
6. (E5) o box do BH academia (hoje só um tracejado cinza) em vidro contínuo, com as faces, a sombra curta e o trilho, como na Casa B;
7. (E9) a bancada do BH academia (pedra areia sobre o travertino) com a borda e a sombra curta;
8. (pergunta) os materiais do BH academia: hoje bancada areia, cuba branca e vaso branco. Recomendado: como o BH sauna da Casa B (bancada em granito marrom, cuba esculpida em travertino bruto, vaso marrom);
9. (E7) o rótulo BH ACADEMIA encosta na linha do box (3 px), na parede da direita e quase no vaso: corpo menor, no piso livre;
10. (E7) o rótulo SAUNA encosta no banco (3 px): no meio do piso livre;
11. os chuveiros de teto da ducha e do BH academia (placa branca com miolo cinza, parecem ralo) em placa cromada com os furinhos, como nas Casas A e B;
12. a cabine do elevador, branca, em aço, como nas Casas A e B.

## Casa C · Subsolo, a lista aplicada (26/10/26)

Resposta do usuário: "ok, aplique a lista" (as perguntas 5 e 8 seguem a recomendação: a escada estreita nevoada depois da linha de corte; o BH academia como o BH sauna da Casa B). Final refeita inteira (`final3840_casac.py Subsolo`); o Térreo da Casa C não muda (a prancha do Térreo sai igual).

Os 12 itens estão nas REGRAS (seção 19, Casa C · Subsolo, e seção 6). Na aplicação:
- a escada estreita não tem preenchimento na ARQ_ESCADAS E RAMPAS do Subsolo (a `F.escada_sombreada` não serve): `escada_estreita_s` pinta o retângulo do PDF inteiro (o que tira os restos do render), pelos bocéis; a linha de corte é a do PDF (três traços com a quebra), como a `CORTE_U` da Casa A;
- os degraus largos estão dentro do Bege Bahia contínuo do pátio e do caminho: `degraus_largos_s` só multiplica o tom de cada degrau; uma projeção do PDF que corta o pátio fica na base chapada como linha fina, e o primeiro recorte pelo Bege Bahia da legenda deixava uma linha clara vertical nos degraus: a máscara é fechada (`F.fechar`);
- o box do BH academia é de correr (os traços tracejados e as duas folhas da ARQ_LOUÇAS E METAIS): não é pego por `F.vidros_box`, mas `ajustes_casaa.folhas_box` o acha (as duas folhas e o trilho); os traços do PDF saem das peças;
- o poço do elevador da Casa C é largo à direita da cabine (17 pt): o anel cinza da rotina da Casa A ficou estreito (~4,5 pt) e o resto do poço branco, como os shafts;
- com a parede em cinza 80, o vão da janela da ducha do BH academia (preenchimento branco da ARQ_PAREDE, que o render tinha preto) aparecia como uma barra preta: `janelas_s` deixa claros os vãos brancos do PDF que estão quase todos escuros (não os batentes do elevador).

Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_2610_{planta,banhos,degraus_largos,escada_estreita,elevador,varanda}_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa C refeitos. Aguarda o OK do Subsolo da Casa C.

### Depois: a limpeza, as portas de vidro da academia e a cuba em granito com a torneira (26/10/26)

Pedidos do usuário, com dois recortes da prancha: "limpeza necessária, vários micro imagens em erro" (a floreira, o vidro da sauna e o pátio), "alguns retoques no piso e nas portas de vidro" (as portas de correr da academia), "a cuba esculpida do banho é em marrom granito" e "faltou a torneira metalica da cuba".

A causa dos micro erros: onde a base chapada não tem a cor de um piso da legenda (as linhas finas do PDF, os brancos das muretas, dos vãos e das louças), a etapa dos pisos não pinta, e ficavam os px do render de 14/10 (a linha lilás entre o pátio e a varanda, as folhas antigas fora da floreira, a mancha branca no canto do vidro). Agora:
- `limpeza_s`, logo depois dos pisos: as linhas finas (até 4 px) junto aos pisos são refeitas pelos pisos em volta (`cv2.inpaint`); os brancos pequenos do PDF e a zona da floreira (o que não é canteiro nem parede, com os traços pretos finos) vão à pedra clara, o Bege Bahia nítido das soleiras; as placas dos chuveiros ficam no piso em volta. As etapas seguintes (bancadas, peças, chuveiros, paredes, soleiras, esquadrias) desenham por cima, como antes;
- a limpeza da faixa do vidro nas esquadrias espelha o lado do canteiro para dentro do vão: `sem_verde_s` leva os px esverdeados fora do canteiro à pedra clara;
- as portas de correr da academia: a faixa da parede (no PDF, as 4 folhas em escada) tinha o travertino e a madeira em degraus e uma faixa bege do render, e a limpeza das esquadrias espelhava os pisos para dentro dela. Depois das esquadrias, `portas_academia_s` refaz a porta pela rotina da Casa A (`final3840_casaa.portas_vidro`): a soleira de Bege Bahia na faixa toda, com as faces da parede, os batentes, as 4 folhas nos planos do PDF com os montantes; nas pontas, a parede do PDF de volta (as esquadrias desenhavam um batente listrado sobre ela) e, junto à faixa, os tiquinhos cinza na madeira refeitos pela madeira em volta;
- a cuba do BH academia em granito marrom (`F.cuba_granito`) e a torneira cromada na prateleira de trás, entre o aro e a parede, no meio da cuba (`torneira_s`, a rotina da Casa A).

Antes e depois (o antes é a final enviada antes destes pedidos): `POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_2610_{limpeza_floreira,portas_academia,banho_cuba_granito,emenda_patio_varanda,planta_limpeza}_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa C refeitos. Aguarda o OK do Subsolo da Casa C.

### Depois: "ainda tem restos a serem limpos" (26/10/26, recorte da floreira e do vidro da sauna)

Sobravam, junto à floreira: pontinhos olivas nas bordas da mureta, pontinhos verdes no vão do vidro da sauna e, do lado de dentro da sauna, uma faixa cinza com manchas escuras junto ao vidro (o vidro e as folhas do render de 14/10). Eram px em traços pretos finos do PDF (a borda do vão do vidro, os lados da mureta), que a limpeza não pegava, e a faixa de 4 px junto ao vidro, larga demais para a regra das linhas finas. Agora:
- `limpeza_s` refaz pelos pisos em volta também os traços pretos finos do PDF (as paredes são grossas e as etapas seguintes redesenham as finas, as peças e os vidros), com as linhas até 6 px e a até 4 px de um piso (`LIMPEZA_S`);
- `sem_verde_s`, depois das esquadrias, volta a mureta da floreira e o peitoril até o vidro (`vidro_pt`) inteiros à pedra clara (fora o canteiro e as paredes grossas), e o teste do verde pega também o verde acinzentado (a borda do canteiro, que a limpeza das esquadrias espelhava para o vão).

Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_2610_limpeza_floreira_2_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa C refeitos. Aguarda o OK do Subsolo da Casa C.

**Aprovado** (26/10/26): "Aprovado", depois da segunda limpeza. Subsolo da Casa C fechado: prancha do Subsolo e PDF (`POE642_CasaC/entrega/POE642_CasaC_Plantas_Humanizadas.pdf`) na versão final. Próxima planta: o Térreo da Casa C, com a lista apresentada antes de alterar.

## Casa C · Térreo, auditoria para o OK (26/10/26)

Pedido do usuário: "Aprovado" (o Subsolo da Casa C); a próxima planta, pela ordem, é o Térreo. Pela regra dele ("Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."), a lista foi apresentada sem alterar a imagem. O mapa numerado: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_auditoria_2610_v2.jpg` (sobre a prancha atual; a v1 segue em `..._auditoria_2610.jpg`), feito com `auditoria_2610.mapa` e os itens trocados em memória.

A conferência foi trecho a trecho, a final em cima e o PDF no mesmo quadro (suíte master e BH master 1 e 2, quartos 1 a 3 e BH 1 a 3, cozinha e serviço, garagem, quarto e BH externos, escadas e deck, gourmet e sala TV, elevador e jardins de inverno, sala de almoço, lavabo, adega e escritório, estar e hall, piscina e lavabos, pisantes), com as projeções da DOC_LINHAS E PROJEÇÕES postas sobre a final e com as letras do PDF (só um D, no degrau 21 da escada estreita).

Conformes: E1 (soleiras), E6 (raios), E2 nos closets e nos quartos 1 a 3, os carros, os rótulos fora dos objetos (menos os itens 12 e 13), as escalas dos pisos (as da Casa B). O PDF do Térreo não tem pilares (nenhum EST_PILAR) nem SHAFT. As folhas abertas das portas em linha cinza fina seguem o padrão aprovado na Casa B.

Os 16 itens:
1. (E10) paredes pretas em cinza 80, com os muros do lote;
2. (E11) o travertino liso de 22/10 (só as nuvens, com um veio solto no estar) no travertino bruto do Subsolo aprovado (varandas, BH master 1, sala TV, circulações, jantar, estar, hall, varanda gourmet, lavabos);
3. (E4) a seta da entrada principal junto à porta pivotante do HALL DE ENTRADA (acesso pelos pisantes do leste), apontando para dentro;
4. (E3, E8) degraus largos (1 a 10): sem as linhas e sem o triângulo, com o sombreamento de descida e o D no degrau de cima (o PDF não marca o sentido ali);
5. (E3, E8) escada estreita (11 a 21, do deck ao caminho): sem as linhas e sem o triângulo, com o sombreamento e o D do PDF no degrau 21;
6. (E5) os boxes em vidro contínuo com as faces e a sombra curta: BH master 1, BH master 2, BH 1, 2 e 3 e a ducha entre os lavabos; os do granito (BH serviço e BH externo) na faixa cinza-clara, como na Casa B;
7. (E9) as bancadas claras sobre o travertino e o Bege Bahia com a borda e a sombra curta: BH master 1 e 2, BH 1, 2 e 3, lavabo, lavabos masc. e fem.;
8. (pergunta) os materiais: hoje bancadas em pedra areia, cubas e vasos brancos; a ilha e as bancadas da cozinha e do gourmet em pedra areia. Recomendado, o padrão do Térreo aprovado da Casa B: lavabo com a cuba esculpida e a bancada em travertino bruto e o vaso marrom; lavabos masc. e fem. (da varanda gourmet) com as cubas esculpidas em granito marrom, a bancada em travertino bruto e os vasos marrons; BH 1, 2 e 3 e BH master 1 e 2 com a cuba e a bancada em travertino bruto e o vaso branco; BH serviço e BH externo (no granito) na pedra areia com as louças brancas; a ilha e as bancadas da cozinha e a bancada do gourmet em granito marrom no tom do piso, escurecido (86%);
9. os chuveiros de teto (placa branca com o miolo cinza, parecem ralo) na placa cromada com os furinhos, como no Subsolo aprovado (BH master 1 e 2, BH 1, 2 e 3, ducha, BH serviço, BH externo, ducha do deck);
10. a cabine do elevador, branca (do render), em aço, como no Subsolo aprovado;
11. (E2) o armário cortado do quarto externo (só com a diagonal) com os cabides, como nos closets;
12. (E7) o rótulo BH SERVIÇO, dentro da área do chuveiro e junto à placa, para o piso livre, em corpo menor;
13. (E7) os X tracejados que passam por cima dos rótulos A. SERVIÇO DESCOBERTA, JARDIM DE INVERNO e JARDIM DE INVERNO 2 abrem embaixo do rótulo, como o do shaft na Casa B;
14. (R8) a claraboia sobre o chuveiro e o vaso do BH master 1 (o retângulo tracejado com o X do PDF, 592,1 a 728,2 x 538,0 a 563,6 pt) não aparece: em cinza-escuro, como as dos closets;
15. a linha fina que não existe no PDF atravessando o BH 2 e o BH 1 (y ≈ 338 px; aparece na etapa das cortinas: o trilho da cortina do quarto passando pelas paredes, o caso que a Casa B corrigiu em 26/10, depois da final de 22/10 da Casa C) sai;
16. a faixa escura e borrada no alto do jardim de inverno, junto à parede do elevador, na mesma folhagem do resto do jardim.

## Casa C · Térreo, a lista aplicada (26/10/26)

Resposta do usuário: "Aplique a lista. No item 8, siga a recomendação." (os materiais no padrão do Térreo aprovado da Casa B). Final refeita inteira (`final3840_casac.py Terreo`), depois `--de tampas`; o Subsolo, rodado de novo da hachura, sai igual ao aprovado (0 px diferentes).

Os 16 itens estão nas REGRAS (seção 19, Casa C · Térreo, e seção 6). Na aplicação:
- os boxes de correr (BH 1, 2 e 3, ducha) não são achados por `F.vidros_box` (7 traços ou mais), e sim por `AJ.folhas_box` (como no Subsolo); os dos BH master 1 e 2 são o vidro fixo (o preenchimento cinza de 3 cm da ARQ_BANCADAS) e a porta de vidro no vão (`VIDROS_TC`);
- nos rótulos, só os boxes que fecham o chuveiro até a parede entram como barreira (BH master e BH serviço): os de correr e o do BH externo param antes da parede, o lado do chuveiro vazava para o banho inteiro e os rótulos BH 1, 2, 3, BH EXTERNO e QUARTO EXTERNO iam para fora;
- a linha sobre os BH 1 e 2 era o trilho da cortina: `cortinas_b` juntava trilhos de ex vizinhos sem testar a sobreposição (o do quarto 3 e o do quarto 1 viravam um só); agora só junta os que se sobrepõem;
- a faixa escura do jardim de inverno vinha do canteiro do jardim de inverno 2: a limpeza das folhas fora dele refazia a borda do jardim de inverno já pintado; agora o que já foi pintado volta;
- com o travertino bruto, `restos_piso` (os pedacinhos de piso entre as linhas dos estofados do estar e da sala TV) devolvia ao render manchas do piso aberto em volta do tapete: só junto às peças do PDF;
- a janela do chuveiro do BH master 2 ficava como uma barra preta com a parede em cinza 80: `janelas_s` com `JANELAS_T` (só os vãos quase todos escuros);
- no BH master 1, a peça esculpida tem duas bacias (as de cima e de baixo, com as torneiras do PDF) e a prateleira no meio (antes, três cubas brancas).

Antes e depois (o antes é a final de 22/10): `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_2610_{planta,banhos_master,bh_1_2_3,lavabos,lavabo,cozinha,gourmet,escadas,jardim_elevador,entrada,servico_externo,estar}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa C refeitos. Aguarda o OK do Térreo da Casa C.


## Casa C · Térreo, pedidos de 26/10 vendo a final (27/10/26)

Pedidos do usuário, um a um, sobre a final da lista aplicada: "melhorar o aspecto das cortinas"; "melhorar o aspecto do marmore travertino bruto"; "melhorar a representação da claraboia"; "melhorar a representação dos rótulos de toda a planta"; "lavabo: pedra da bancada e cuba esculpida em marrom granito. na parte de cima temos uma floreira. igual a imagem a outra imagem anexa."; lavabos masc. e fem.: "pedra das pias em marrom granito. cubas em marmore travertino bruto."; "banho serviço: pedra da pia em marrom granito e cuba branca."; "banho externo: pedra da pia em marrom granito e cuba branca."; os portões da área descoberta: "atras das portas tem uma soleira. remova-as."; "remova soleira clara de uma das portas"; "tem uma soleira atras da porta do quarto serviço. remova-a."; "remova essa "soleira" da janela da cozinha."; a ilha: "essas duas linhas claras não existem na bancada. e o cooktop precisa ser girado em 180º para ficar corretamente."; "melhorar a representação dos chuveiros de teto dos banhos"; "gire o cooktop da varanda em 180º"; "remover sujeiras e riscos do escritório. fazer a limpeza"; o elevador e os jardins de inverno: "remover as sujeiras, limpar as sujeiras e corrigir os erros dos contornos"; "corrija as paredes atrás das portas. alguma sombra ou efeito recortou as paredes."; "corrija as portas da adega".

Feito no `final3840_casac.py` (descrito nas REGRAS, seções 6 e 19, e no README da Casa C), final do Térreo refeita inteira:
- travertino em estratos (`travertino_estratos`): faixas largas e finas levemente onduladas, as linhas finas de alguns encontros, poros alongados e poucos (a primeira versão, com 12 poros por m², parecia sujeira: 6 por m², mais claros), a foto da biblioteca calma por baixo; nas bancadas e cubas, o mesmo desenho mais calmo (as faixas finas fortes liam como réguas de madeira);
- as cortinas com o pano franzido (`pano_cortina`, no lugar do pano de `blocos.cortina` só no Térreo da Casa C);
- as claraboias desenhadas por `claraboias_t` (o tracejado do PDF saía irregular e o X partido; a da varanda ficava branca);
- os rótulos com o nome em SemiBold (hook `fonte_nome` em `retoque_1pav_casae.rotulos_ambientes`, desligado nas outras casas);
- as causas das "soleiras" e das linhas claras: a etapa das esquadrias redesenha os preenchimentos brancos da ARQ_PAREDE como caixilhos e vidros (a faixa entre o trilho e a folha dos portões, o vão sob as folhas da porta de correr e da janela da cozinha, os dois preenchimentos ao longo da ilha); a do quarto de serviço era uma soleira de `F.soleiras` (o vão do BH serviço); as paredes recortadas atrás das portas também vinham das esquadrias (a limpeza da faixa das folhas trocava pela cor do piso a parede junto à folha aberta);
- as plantas dos jardins com a franja clara do recorte da biblioteca (o "erro de contorno"): `sprite_limpo` aperta a borda do alfa e pinta a borda com a cor das folhas de dentro.

Conferido na final: nenhuma parede do PDF com a cor do piso (a mesma busca achava 3 a 4 px ao longo de 1 m junto às folhas dos BH 1, 2 e 3 e as pontas de parede junto aos batentes); o Subsolo, rodado de novo da hachura, sai igual ao aprovado (0 px diferentes). Antes e depois (o antes é a final da lista aplicada): `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_pedidos2610_{planta,cortinas_claraboias,closets_banhos_master,bh_1_2_3,lavabo,lavabos,bh_servico_externo,portoes_porta_correr,cozinha_ilha,gourmet,escritorio_adega,jardins_elevador,estar}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa C refeitos. O travertino em estratos, as cortinas, as claraboias, os rótulos em SemiBold, os chuveiros e a limpeza das plantas valem só para o Térreo da Casa C por enquanto (podem ser levados ao Subsolo e às outras casas, com o OK do usuário). Aguarda o OK do Térreo da Casa C.

## Cortinas franzidas em todas as casas (27/10/26)

Pedidos do usuário, vendo a final do Térreo da Casa C: "e essas cortinas? corrija-as." (as do estar, junto ao vidro do hall, ainda como as bolinhas do render) e, com a imagem das cortinas dos quartos da Casa C, "adote esses modelos de cortinas para as todas as casas. corrija as cortinas das casas A, B, E." Passos e comandos no README dos scripts ("Cortinas franzidas em todas as casas") e regra nas REGRAS (seção 8, "Cortinas", e seção 15).

- **Biblioteca:** o pano franzido da Casa C virou `blocos.pano_franzido` (`_blocos/blocos.py`), e `blocos.cortina` fechada passou a ser ele com o trilho; o desenho antigo (zigue-zague) ficou em `blocos.cortina_ondulada`, para a cortina aberta e o trilho. O `pano_cortina` da Casa C só chama a biblioteca (a final da Casa C não muda por isso).
- **Casa C, estar:** as cortinas do estar estão na ARQ_MOBILIÁRIO do PDF (as outras, na ARQ_LOUÇAS E METAIS): `final3840_casac.trechos_cortina_tc` junta essas ondas aos trechos do motor, com o lado do vidro pelo traço da parede mais perto. Final refeita pelo motor (`--de cortinas`).
- **Casas A (1º Pavimento), B (Térreo), D (Térreo) e E (Térreo e 1º Pavimento):** `cortinas_franzidas.py` troca, nas finais já aprovadas, só o pano: cada pano antigo sai do lugar exato em que a rotina daquela planta o pôs (os mesmos trechos do PDF, no mesmo quadro), o lugar é refeito com o piso do ambiente, e o pano franzido entra no mesmo eixo e comprimento. 8, 10, 12, 5 e 10 panos. O resto da imagem não muda.
- **Lado do vidro (inconformidade achada no caminho):** o pano franzido não é simétrico, e o motor das Casas B, C e D supunha o vidro sempre em cima nas cortinas horizontais. `ajustes_casab.trechos_cortina_b` agora lê o lado no PDF (`lado_vidro_pdf`). Nas Casas B e C todos os lados já estavam certos; no Térreo da Casa D, as 4 janelas das fachadas de baixo (8 panos) têm o vidro embaixo e estavam com o trilho do lado do ambiente: viraram (panos e o trilho de parede a parede do lado do vidro). Não é uma escolha de desenho, é o que o PDF mostra, por isso foi corrigido junto, sem esperar OK.
- **Limpeza:** no primeiro passe, onde o piso a 0,20 m do pano não era piso, a limpeza copiava o que estava lá (o arranjo de flores do escritório da Casa E, a roupa de cama de um quarto da Casa B, criados-mudos no 1º Pavimento da Casa E); agora o px que não é piso vem de outro ponto (`tirar`, `piso_dif`, `outros`). Conferido px a px contra o primeiro passe: só esses pontos mudaram, todos para melhor.
- **Subsolos:** não mudam (a hachura usa só o contorno do lote do Térreo).

Antes e depois (o antes é a final do commit anterior): `POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_cortinas2710_antes_depois.jpg`, `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_cortinas2710_antes_depois.jpg`, `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_cortinas2710_antes_depois.jpg`, `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_cortinas2710_antes_depois.jpg`, `POE642_CasaE/renders/POE642_CasaE_PH_{Terreo,1Pavimento}_cortinas2710_antes_depois.jpg`. Pranchas dessas plantas e os PDFs das cinco casas refeitos. Aguarda o OK do usuário (e continua aguardando o do Térreo da Casa C).

## Casa C · Térreo, pedidos de 27/10 vendo a final (27/10/26)

Pedidos do usuário, um a um, sobre a final do Térreo da Casa C: "As cadeiras precisam ficar parcialmente abaixo da mesa de escritório."; "corrija esse rótulo para que não fique sobre o guarda roupas" (CLOSET MASTER 1); "corrija o rótulo da garagem para que não fique muito próximo do carro". Feito no motor (`final3840_casac.py Terreo --de cadeiras`), detalhes no README dos scripts e regras nas seções 8 e 12.

- **Cadeiras:** no PDF, as cadeiras dos quartos 1 e 3 e da suíte master entram cerca de 1/3 sob o tampo (11 de 35 pt), mas as mesas são faixas da DOC_LINHAS E PROJEÇÕES, pintadas antes, e as cadeiras saíam inteiras por cima. A etapa nova `cadeiras` põe a mesa por cima da parte sob o tampo. O primeiro jeito (copiar um trecho do tampo) deixava costuras e faixas de tom; ficou o tom de cada coluna passando de uma ponta à outra, com o veio fino de um trecho livre, sem as juntas, e a sombra do tampo só sobre a cadeira.
- **CLOSET MASTER 1:** os guarda-roupas da Casa C (faixas da DOC_LINHAS) e as claraboias não eram obstáculo para os rótulos; agora são (`obstaculos_pt`). O piso livre do closet tem 2,1 m (124 px) e o nome, numa linha, 116 px: foi para duas linhas (CLOSET / MASTER 1), no meio do piso livre. O CLOSET MASTER 2 se afastou 7 px do tracejado da claraboia; os outros rótulos não mudaram.
- **GARAGEM:** no PDF o texto está sobre o carro do meio, e o lugar livre mais perto encostava no retrovisor dele (4 px). A busca parte do meio do vão entre o carro do meio e o da direita: ~0,2 m de cada um.

Conferido na final: só essas 6 regiões mudaram (as 3 cadeiras e os 3 rótulos). Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_pedidos2710_{cadeiras,closets,garagem}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa C refeitos. Aguarda o OK do Térreo da Casa C.

- **Depois, o banco do deck** ("banco bronze fosco, sem falhas.", com a imagem do deck de 32,38 m²): no PDF, o banco em L é o assento (a cor escura da legenda) com uma moldura branca fina na frente e nas pontas; a etapa do deck pintava de bronze só o assento, e a moldura ficava com a madeira do render, mais larga que o banco do PDF. Daí as falhas: o reflexo claro sob o braço de cima, o degrau na ponta de cima, a peça clara e o traço escuro na de baixo e o quadrado escuro no canto de dentro. `deck_detalhes_c` junta a moldura ao assento (a faixa de trás, junto à pedra e à grama, fica) e o L sai inteiro em bronze fosco, com o contorno e a sombra curta. Na primeira tentativa, pedacinhos com a cor do banco no alto da planta também ganharam moldura; a moldura agora é só a do assento grande. Conferido: só a região do banco mudou. Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_pedidos2710_banco_deck_antes_depois.jpg`. Prancha e PDF refeitos.

- **Depois, os vidros dos jardins de inverno** ("corrija esses riscos brancos dentro da área verde, no contorno interno, logo depois das portas de vidro."): a faixa do vidro na base é mais larga que o vidro fino desenhado pelas esquadrias, e a parte de dentro ficava com manchinhas claras de travertino; embaixo do JARDIM DE INVERNO, a base tem uma soleira estreita entre as plantas e o vidro, que saía como um risco claro contínuo. `jardins_vidros_t`, no fim da etapa das esquadrias, varre cada lado dos jardins linha a linha até a linha comprida do vidro: o claro vira a vegetação de dentro; a soleira vira a borda das plantas deslocada até o vidro. A primeira tentativa (por distância ao vidro, sem varrer as linhas) passava o verde para o lado de fora nos cantos, e a segunda deixava a sombra da borda antiga como uma linha escura embaixo; as duas foram descartadas. Conferido: só as bordas dos três jardins com vidro mudaram (o JARDIM DE INVERNO, o 2 e o jardim junto ao closet master). Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_pedidos2710_jardins_vidros_antes_depois.jpg`. Prancha e PDF refeitos.
- **O traço atrás do banco do deck:** o usuário pediu para tirá-lo do fim do banco para baixo ("vai até a metade da piscina e não deveria"); ao saber que é a mureta do PDF, que desce até ali, respondeu "então preserve." Ficou como está.
- **Depois, as portas de vidro dos jardins de inverno** ("melhore o aspecto das portas de vidro dos jardins de inverno"): eram os traços finos e falhados que as esquadrias desenham. `portas_jardins_t` as refaz como as do escritório e da adega (`final3840_casaa.portas_vidro`), nos planos do PDF: no JARDIM DE INVERNO, 2 folhas em cada lateral e 3 embaixo; no JARDIM DE INVERNO 2, 2 em cima; com os batentes. Por trás das folhas, a metade de fora da faixa é travertino e a de dentro, plantas (sem o risco claro do pedido anterior). Conferido: só os dois jardins mudaram. Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_pedidos2710_portas_jardins_antes_depois.jpg`. Prancha e PDF refeitos.
- **Depois, o vidro fixo do JARDIM 1** ("aplique o mesmo desenho no vidro fixo também"): o vidro fixo do JARDIM 1 (4,44 m², o jardim junto ao closet master 2) entra em `PORTAS_JARDINS_TC` com o mesmo desenho das portas: no PDF, o painel branco de 4,3 pt (o vidro e o caixilho) entre os dois arremates cinza da parede, com os quadrados brancos do caixilho nas pontas; vira uma folha sem correr, com os montantes nas pontas e os dois quadrados como batentes. O fundo da faixa é refletido nas bordas (`espelho`): na primeira rodada, a cópia a 13 px pegava a ponta da costela-de-adão do vaso ao lado e deixava um fio verde do lado do travertino. As plantas vão até o vidro, sem a faixa clara que havia entre elas e o vidro. Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_pedidos2710_vidro_fixo_jardim1_antes_depois.jpg`.
- **Depois, a soleira da área de serviço** ("aplique a correção na soleira."; "a soleira é da área de serviço."): a porta de correr entre a cozinha e a área de serviço tinha no vão, entre os batentes, uma faixa clara bege rosada que vinha do render (não do `F.soleiras`: o vão não está entre os `B.vaos_brancos`). A mesma correção da porta do quarto de serviço: o vão de dentro (`VAO_COZINHA_SERVICO_T`, sem os batentes) entra no granito dos `pisos` (`VAOS_TC`) e nas faixas que voltam ao piso depois das esquadrias; junto à folha, onde a base tem o traço do contrapiso e o cinza da folha, os pisos guardavam a faixa clara (na primeira rodada sobrou um fio de 3 px na metade de baixo), e ali entra o granito da cozinha, 12 px ao lado (`POS_ESQUADRIAS_TC["vao_cozinha"]`). A folha de correr e os batentes ficam como estão. Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_pedidos2710_soleira_servico_antes_depois.jpg`.
- Conferido nos dois: fora do vão e da faixa do vidro fixo, nenhuma diferença acima de 20 níveis (a rodada desde os `pisos` deixou só variações de 1 nível no granito, de arredondamento). Prancha e PDF refeitos; o Subsolo não muda (a hachura vem só da silhueta do lote).
- **Depois, a adega** ("adicione a prateleira de vinhos como fizemos na outra casa, ao fundo da adega. não sobreponha o rotulo nessa prateleira"; "as garrafas em escala"): no PDF da Casa C a adega (1,26 x 4,30 m, as folhas de vidro na parede da esquerda) não tem nada dentro. `adega_c` (`ADEGA_C`, no fim da etapa `biblioteca`) põe a prateleira na parede do fundo, a da direita, de ponta a ponta, como a da Casa B: marcenaria areia com o veio no comprido, o contorno fino, 6 módulos em traço fino e 42 garrafas deitadas, o gargalo junto à parede. As garrafas na escala real (0,075 m de diâmetro, 0,29 m de comprimento, a cada 0,09 m; as da Casa B, no quadro de 3840 px, ficaram com a metade disso); a prateleira com 0,30 m de fundo, o comprimento delas. Ela entra como obstáculo dos rótulos. Ao lado dela o piso livre tem 0,96 m e a área do rótulo 0,90 m: no corpo cheio, o "A:" encostava na porta de vidro (1 px). Apresentado ao usuário, ele escolheu o rótulo menor: só o da ADEGA a 85% do corpo (`ROTULOS_TC["corpos"]`), no meio do piso livre (6 px de cada lado; `ROTULOS_TC["pontos"]`). Conferido: nada mudou fora da adega. Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_pedidos2710_adega_antes_depois.jpg`. Prancha e PDF refeitos.

**Aprovado** (27/10/26): "ok, casa C térreo aprovada", depois da adega. Casa C fechada: Subsolo e Térreo aprovados, prancha dos dois e PDF (`POE642_CasaC/entrega/POE642_CasaC_Plantas_Humanizadas.pdf`) na versão final (commit 15a613f). Próxima planta: a que o usuário indicar (pela ordem, o Subsolo da Casa D), com a lista apresentada antes de alterar. As cortinas franzidas das Casas A (1º Pavimento), B, D e E seguem aguardando o OK.

## Casa D · Subsolo, auditoria para o OK (27/10/26)

Pedido do usuário: "prossiga com o subsolo da casa D" (a Casa C está aprovada inteira: "Aprovado" e "ok, casa C térreo aprovada"). Pela regra dele ("Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."), a lista foi apresentada sem alterar a imagem. O mapa numerado: `POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_auditoria_2610_v2.jpg` (sobre a prancha atual; a v1 segue em `..._auditoria_2610.jpg`), feito com `auditoria_2610.mapa` e os itens trocados em memória.

A conferência foi trecho a trecho, a final em cima e o PDF no mesmo quadro (WC DCE, DCE 1 e depósito; a escada de 16 degraus; o elevador; a academia e as portas do pátio; a sauna, a ducha e o vestiário), com os 7 rótulos do PDF e as texturas lado a lado com as do Subsolo aprovado da Casa C. Os pisos pela legenda de 15/10: granito no DCE 1, no WC DCE e no depósito; vinílico (a madeira das Casas B e C) na academia; Bege Bahia na sauna, na ducha, no vestiário, na circulação, na escada e no pátio.

Conformes: E1 (soleiras), E6 (sem raios), E11 (Bege Bahia, granito e madeira na escala das Casas B e C), a cabine do elevador em aço, os bancos da sauna nos dois tons de Bege Bahia, os rótulos DCE 1, DEPÓSITO/CASA DE MÁQUINAS, ELEVADOR, ACADEMIA, SAUNA e VESTIÁRIO. O PDF do Subsolo não tem pilares (nenhum EST_PILAR) nem SHAFT.

Os 10 itens:
1. (E10) paredes pretas em cinza 80 (não há pilares);
2. (E3) escada de 16 degraus: o triângulo vira o S do PDF; a origem do texto cai no pátio, fora do degrau, e a letra fica centrada no degrau 1;
3. (E8) a escada sem os traços dos bocéis, com o sombreamento de subida; a linha de corte do PDF (no degrau 7) em cinza fino e os degraus 8 a 16 nevoados, como no Subsolo aprovado da Casa C (hoje esses degraus são só ~3% mais claros que os de baixo);
4. (E2) DCE 1: o armário cortado (madeira lisa) com os cabides, como nos closets;
5. (E5) WC DCE: o box (uma faixa cinza tracejada) em vidro contínuo, com as faces finas, a sombra curta e o trilho;
6. (E9) as bancadas do WC DCE (só o contorno cinza, com o granito do piso aparecendo por dentro) e do vestiário (clara, quase no tom do Bege Bahia) com a borda no tom escurecido da pedra e a sombra curta;
7. (pergunta) os materiais: hoje bancadas claras, cubas e vasos brancos. Recomendado: o WC DCE como o BH serviço das Casas B e C (bancada em granito marrom levemente escurecido, cuba e vaso brancos); o vestiário como o BH academia do Subsolo da Casa C (bancada e cuba esculpida em granito marrom, torneira cromada, vaso marrom);
8. os chuveiros do WC DCE, da ducha da sauna e do vestiário (placa branca com o miolo azul) na placa cromada com os furinhos, o braço e a canopla, como nas Casas A, B e C;
9. as portas de vidro do pátio para a academia (os vidros fixos com retângulos rosados, a folha num traço fino) refeitas como as do Subsolo aprovado da Casa C: a soleira de Bege Bahia na faixa da parede, as folhas e os vidros fixos nos planos do PDF, com os montantes e os batentes;
10. (E7) WC DCE: o rótulo fica a 3 px do vaso, e um ponto claro do granito colado no W faz ler "*WC": no meio do piso livre, sem o ponto.

Aguarda a resposta do usuário (o OK da lista e a pergunta 7).

## Casa D · Subsolo, a lista aplicada (27/10/26)

Resposta do usuário: "ok, aplique a lista. no item 7, siga a recomendação". Final refeita inteira (`final3840_casad.py Subsolo`, 2 min), depois `--de soleiras`; o Térreo da Casa D não muda (a prancha do Térreo fica como está).

Os 10 itens estão nas REGRAS (seção 19, Casa D · Subsolo). Na aplicação, com as rotinas do Subsolo aprovado da Casa C:
- no PDF do Subsolo da Casa D as bancadas são só traços (a ARQ_BANCADAS sem preenchimento): o `F.bancadas` não as acha, e elas entram pelos retângulos do PDF (`BANHOS_SUB_D`), com a rotina das bancadas dos banhos da Casa A (`final3840_casaa.bancada_pedra`); a bancada do vestiário que vinha do render (`CUBA_VESTIARIO_S`) saiu;
- a cuba do vestiário é a bacia do PDF com a prateleira de trás, junto à parede: a cuba esculpida em granito (`F.cuba_granito`) vai só na bacia, e a torneira na prateleira, como a do BH academia da Casa C;
- o box do WC DCE é de correr (as duas folhas e o trilho da ARQ_LOUÇAS E METAIS, que `ajustes_casaa.folhas_box` acha); a faixa cinza da divisória, pintada na base (a config da Casa D) e no render, é refeita com o granito 7 px acima antes do vidro;
- a escada é a rotina da escada estreita da Casa C (`C.escada_estreita_s`) com a geometria da Casa D (`ESCADA_SUB_D`), sem esmaecer o trecho de antes do corte (cheio desde 15/10);
- o rótulo do WC DCE: com a folga de 4 px da Casa C ele não cabia e o VESTIÁRIO saía do ambiente (ficou a folga de sempre); o arco da porta do PDF, que não aparece, ocupava o piso livre no mapa de obstáculos e mandava o rótulo para o lado do chuveiro: os arcos das portas saem dos obstáculos dos rótulos do Subsolo (`rotulos_sub_d`), e o rótulo parte do meio do piso livre (`ROTULOS_SUB_D`);
- com as paredes em cinza, o nicho do chuveiro do vestiário (um retângulo da ARQ_BANCADAS dentro da parede da direita, antes escondido no preto) aparecia branco: entra na pedra clara das soleiras (`nicho_d`).

Conferido na final: as mudanças ficam só dentro da planta (fora dela, nenhum px muda). Antes e depois (o antes é a final de 22/10): `POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_2610_{planta,dce_wc,escada,banhos,portas_academia}_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa D refeitos. Aguarda o OK do Subsolo da Casa D.

### Depois: "remova a linha técnica em diagonal. deixe apenas uma sombra no lugar." (27/10/26)

Na escada de 16 degraus, a linha de corte do PDF (cinza fino, com o zigue-zague da quebra) saiu: a divisa com o trecho nevoado é a diagonal reta do corte (do primeiro ao último ponto do PDF) e, no lugar da linha, uma sombra suave sobre os degraus de antes dela (`ESCADA_SUB_D["sombra_corte"]`: 30%, caindo em ~4 px). A rotina da Casa C (`C.escada_estreita_s`) ganhou essa opção; sem ela, desenha a linha como antes (o Subsolo aprovado da Casa C não muda). Conferido: só a escada mudou. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_pedidos2710_escada_corte_antes_depois.jpg` (os `..._2610_{planta,escada}_antes_depois.jpg` refeitos sobre a final nova). Prancha do Subsolo e PDF da Casa D refeitos. Aguarda o OK do Subsolo da Casa D.

### Depois: portas, paredes, batentes, riscos do WC DCE e a cama do DCE 1 (27/10/26)

Pedidos, vendo a final: "corrija as portas e seus contornos, além da parede na parte de baixo." (as portas do depósito); "corrija os erros nas paredes" (a parede entre a academia e o vestiário); "corrija esse erro na parede. complete a parte que ficou faltando no batente da porta do banho"; "limpe o risco atrás da porta e os riscos em frente a janela no piso." (o WC DCE); "melhore o aspecto da roupa de cama para dar mais clareza de se trata de uma cama" (o DCE 1).

A causa dos riscos é a mesma: a limpeza das esquadrias (`B.esquadrias_final`) refaz a faixa em volta das folhas e das janelas espelhando a vizinhança, e no Subsolo trazia o que não é piso — o cinza da parede acima da folha da porta da escada para o depósito, o Bege Bahia da soleira num bloco acima da folha de baixo da porta dupla do depósito (e o granito no lugar da parede logo abaixo), o traço do box atrás da folha da porta do WC DCE, os pedaços do Bege Bahia de fora no piso diante da janela do WC DCE, a cama esticada diante da janela do DCE 1, os recortes de Bege Bahia na parede do vestiário (acima da folha e do batente da porta) e uma faixa de granito mais clara ao lado da folha da porta do DCE 1. `pos_esquadrias_sub_d` (no fim da etapa `esquadrias`): em volta de cada folha e do caixilho de cada janela, o piso volta à etapa anterior (onde lá estava a folha antiga, entra o piso um pouco mais longe, do mesmo lado; diante da janela do WC DCE o granito vai até o caixilho); a parede do PDF volta inteira onde as esquadrias a cortaram, com o traço da face — o batente da porta do vestiário fica encostado na parede, inteiro. O vão entre as folhas do box do vestiário fica como estava (ali as esquadrias abrem o vão de propósito). O trilho do box do WC DCE, no vão do box, fica.

A cama do DCE 1 (`cama_dce_d`, `CAMA_DCE_S`): no colchão, a roupa de cama da biblioteca do tipo da cama do motorista da Casa A, aprovada em 21/10 ("está tudo muito brancão"): lençol branco com a dobra, travesseiro, edredom em linho claro e peseira bordô nos pés, com o pesponto; a cabeceira embaixo, contra a parede da janela; a moldura de madeira do render fica.

Conferido: as mudanças ficam nas portas, nas paredes junto a elas, nas duas janelas e na cama (e no traço da face de algumas paredes cortado pela mesma limpeza, junto ao elevador, à sauna e ao vestiário). Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_pedidos2710_{portas_deposito,wc_dce,parede_vestiario,cama_dce1}_antes_depois.jpg` (o `..._2610_planta_antes_depois.jpg` refeito sobre a final nova). Prancha do Subsolo e PDF da Casa D refeitos. Aguarda o OK do Subsolo da Casa D.

## Casa D · Térreo, auditoria para o OK (27/10/26)

Pedido do usuário: "Vamos para o térreo da casa D" (depois das correções do Subsolo, sem o OK explícito dele, que segue em aberto). Pela regra dele ("Caso apareça alguma inconformidade, me apresente antes de alterar. Eu dou OK e você altera."), a lista foi apresentada sem alterar a imagem. O mapa numerado: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_auditoria_2610_v2.jpg` (sobre a prancha atual; a v1 segue em `..._auditoria_2610.jpg`), feito com `auditoria_2610.mapa` e os itens trocados em memória.

A conferência foi trecho a trecho, a final ao lado do PDF no mesmo quadro (banho gourmet e gourmet, cozinha, louceiro e despensa, serviço, gás, WC DCE e DCE, área descoberta, garagem, piscina, deck e blocos em cascata, varanda gourmet, living/jantar, adega, hall e lavabo, suíte master, banho master e closet, escada de 16 degraus, elevador, sala íntima e jardim, suítes 1, 2 e 3 e banhos 1, 2 e 3), com as cores da base da legenda (travertino no living/jantar, no hall e no lavabo; Bege Bahia nos banhos, no deck e na varanda) e as letras do PDF (só um D, no degrau 16 da escada).

Conformes: E1 (soleiras), E6 (sem raios), os carros (prata, alinhados, R12), as camas e os bancos do render nas suítes (resposta 5 de 22/10), os brises em madeira (também as duas peças giradas no deck, junto à gourmet, que são da ARQ_ELEMENTOS FIXOS), as cortinas franzidas, a cabine do elevador em aço, os closets com cabides da suíte master e das suítes 1 e 2, as escalas dos pisos. O PDF do Térreo não tem pilares nem SHAFT. O chuveiro do banho master fica aberto, sem box (o PDF não desenha vidro ali; a v1 apontava a falta).

Os 15 itens:
1. (E10) paredes e muros do lote pretos em cinza 80;
2. (E11) o travertino liso de 22/10 (living/jantar, hall de entrada, lavabo) no travertino do Térreo aprovado da Casa C (em estratos);
3. (E4) a seta da entrada principal junto à porta pivotante do hall (acesso pelos pisantes do leste), apontando para dentro;
4. (E3, E8) escada de 16 degraus: sem as linhas e sem o triângulo, com o sombreamento de descida e o D do PDF no degrau 16;
5. (E3, E8) blocos em cascata à esquerda da piscina: sem o triângulo, com o sombreamento de descida e o D no bloco de cima (o PDF não marca o sentido ali);
6. (E2) armários cortados sem cabides: DCE, suíte 3/escritório e o módulo ao lado do banho master (hoje com o desenho borrado do render) com os cabides, como nos closets;
7. (E5) os boxes dos banhos 1, 2 e 3 e do WC DCE (só tracejados) em vidro contínuo, com as faces finas e a sombra curta;
8. (E9) as bancadas claras sobre o piso claro (lavabo, banho master, banhos 1, 2 e 3) com a borda e a sombra curta;
9. (pergunta) os materiais: hoje bancadas em pedra areia e cubas e vasos brancos; ilha e bancadas da cozinha e da gourmet em pedra areia (resposta "Areia" de 22/10). Recomendado, o padrão do Térreo aprovado da Casa C: lavabo com a bancada e a cuba esculpida em granito marrom e o vaso marrom; banho master e banhos 1, 2 e 3 com a cuba e a bancada em travertino bruto e o vaso branco; banho gourmet e WC DCE com a bancada em granito marrom e a cuba branca; a ilha e as bancadas da cozinha e da gourmet em granito marrom no tom do piso, escurecido (86%), como nas Casas B e C;
10. os chuveiros (placa branca com o miolo cinza: banho master, banhos 1, 2 e 3, WC DCE, banho gourmet, ducha do deck) na placa cromada com os furinhos, o braço e a canopla, como nos Subsolos;
11. (E7) os X tracejados que cortam os rótulos GARAGEM, ÁREA DESCOBERTA e JARDIM (do lavabo) abrem embaixo do rótulo, como na Casa C;
12. (E7) WC DCE TÉRREO: o rótulo, na área do chuveiro e junto à placa, para o piso livre;
13. DCE: a cama branca do render com a roupa de cama da biblioteca, como no DCE 1 do Subsolo (pedido de 27/10);
14. varanda gourmet: o banco comprido do PDF, à esquerda do estar (no tapete), não aparece;
15. a adega vazia ganha a prateleira de vinhos ao fundo, como nas Casas C e E.

Depois de aplicar, o Subsolo roda de novo da hachura (o lote vem do Térreo final). Aguarda a resposta do usuário (o OK da lista e a pergunta 9).


## Casa D · Térreo, a lista aplicada (27/10/26)

Resposta do usuário: "Já já reviso o subsolo. Aprovo a lista e sigamos no item 9 com a recomendação". Final refeita inteira (`final3840_casad.py Terreo`, ~7 min), depois `--de biblioteca`; o Subsolo roda de novo da hachura (`--de hachura`: o lote vem do Térreo final).

Os 15 itens estão nas REGRAS (seção 19, Casa D · Térreo) e no comentário antes de `MATERIAIS_TD`. Na aplicação, com as rotinas do Térreo aprovado da Casa C:
- o travertino em estratos entra pelo `F.piso_textura` (`piso_estratos_d`, o ramo dos estratos de `C.piso_textura_c`); as bancadas e cubas de travertino bruto saem no mesmo desenho (`FA.travertino_bruto = C.travertino_bruto_tc`);
- as bancadas: `C.bancadas_c` com a borda E9 e a pedra de cada bancada pelo centro dela (`MATERIAIS_TD`); as duas cubas brancas (a da bancada da gourmet e a de parede do WC DCE) saem da lista das esculpidas e vão por `final3840_casaa.cuba_branca`;
- os boxes: a faixa tracejada da base é refeita com o piso 7 px acima antes do vidro; `AJ.folhas_box` juntava as folhas dos banhos 1, 2 e 3 (estão na mesma linha) e foi trocado pelas folhas pareadas de `BOXES_TD`;
- os guarda-roupas novos, o banco e a prateleira da adega entram como obstáculo dos rótulos;
- a escada de 16 degraus e as projeções: o sombreamento sai de `C.sombras_degraus` no Bege Bahia da escada; as projeções que estavam em `escadas_d` passaram à etapa `projecoes` (para os rótulos acharem o tracejado embaixo dos textos).

Conferido na final, trecho a trecho, contra a final anterior (`T_antes`) e o PDF. Na primeira rodada apareceram e foram corrigidos:
- uma linha branca de ponta a ponta nas ilhas da cozinha e da gourmet e uma faixa branca manchada na borda do jardim da sala íntima: a limpeza dos vãos escuros das janelas da Casa C (`C.janelas_s`, que eu tinha posto na etapa das esquadrias) pegava as faixas brancas da ARQ_PAREDE dentro das ilhas (agora em granito escuro) e no guarda-corpo do jardim. Saiu: no Térreo da Casa D nenhuma janela de verdade precisava dela;
- um traço cinza vertical atravessando o closet da suíte master até o muro: o trilho da cortina da janela da suíte master não parava mais na parede (procurava o preto). `F.cortinas(..., paredes_pdf=True)`, como na Casa B (auditoria de 26/10, item 11);
- o banco da varanda saía xadrez: a textura do piso de madeira tem as juntas das réguas. Agora a madeira é a do tampo da mesa da suíte 3/escritório (já na imagem, `BANCO_VARANDA_TD["fonte_pt"]`), com o veio no comprido, a 80%;
- o D dos blocos em cascata ficava no lugar do triângulo, na borda do bloco de cima, metade no deck: vai ao meio do bloco de cima (`ESCADA_DESCIDA_TD["d_blocos_pt"]`);
- o rótulo do WC DCE voltava para dentro do box: o arco da porta do PDF, que a final não desenha, fechava o piso livre entre a cuba, o vaso e a porta. Os arcos das portas saem dos obstáculos dos rótulos do Térreo, como no Subsolo (`rotulos_sub_d`).

Conferido de novo na final: as diferenças para a final anterior ficam só nos 15 itens (paredes e muros, travertino, bancadas e louças, boxes, chuveiros, guarda-roupas, cama, banco, adega, seta, escadas, rótulos e os X); nos dois jardins, só o contorno claro em volta das plantas em vaso saiu e, no do lavabo, o X abre embaixo do JARDIM. As ilhas e bancadas em granito escurecido ficam, como recomendado, quase no tom do piso, marcadas pela borda e pela sombra. O Subsolo, rodado de novo da hachura, não muda (0 px: a hachura usa só o contorno do lote). Antes e depois (o antes é a final anterior, com as cortinas franzidas de 27/10): `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_2610_{planta,servico,social,intima,escadas,varanda,garagem}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa D refeitos. Aguarda o OK do Térreo e do Subsolo da Casa D.

**Aprovado** (27/10/26): "subsolo da casa D aprovado". Subsolo da Casa D fechado: prancha do Subsolo e PDF (`POE642_CasaD/entrega/POE642_CasaD_Plantas_Humanizadas.pdf`) na versão final (a lista do Térreo, aplicada depois, não o mudou: 0 px). Aguarda o OK do Térreo da Casa D; depois, pela ordem, a Casa E.

### Depois: o banho gourmet em travertino bruto, com o vaso marrom (27/10/26)

Pedido, vendo a final do Térreo (o usuário avisou "Existem vários ajustes a fazer" e mandou o primeiro): "Banho gourmet: sanitário marrom, bancada da pia e Cuba esculpida no mármore travertino bruto". `MATERIAIS_TD`: a bancada do banho gourmet passa do `granito_escuro` ao `travertino` e a cuba sai das `cubas_brancas` (vira a cuba esculpida em travertino bruto, como as dos banhos; a torneira do PDF segue na etapa das peças); `VASOS_TD` ganha o vaso do banho gourmet (1272,3 a 1292,3 x 640,8 a 669,9 pt), marrom como o do lavabo.

No PDF, essa bancada tem o pontilhado do granito (466 pontos da ARQ_BANCADAS, traços de comprimento zero), e o contorno do PDF que `F.bancadas` redesenha por cima das peças os trazia de volta: no granito escuro não se viam; no travertino, eram poros escuros densos. `bancadas_terreo_d` tira esses pontos (`MATERIAIS_TD["sem_pontilhado"]`) só durante as bancadas; as outras bancadas não têm pontilhado.

Rodado `final3840_casad.py Terreo --de bancadas`. Conferido: só o vaso e a bancada do banho gourmet mudam (a bancada da pia da gourmet, do lado de fora, segue em granito escurecido); o Subsolo não muda (a hachura usa só o contorno do lote). Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710_banho_gourmet_antes_depois.jpg` (os `..._2610_{planta,servico}_antes_depois.jpg` refeitos sobre a final nova). Prancha do Térreo e PDF da Casa D refeitos. Aguarda os outros ajustes do Térreo da Casa D.

### Depois: o lavabo em travertino, os banhos das suítes em quartzito Aura e o vestiário do Subsolo (27/10/26)

Pedidos: "Lavabo: bancada e Cuba esculpida no mármore travertino bruto, sanitário marrom"; "Banhos suítes: piso quartzo aura, bancada e pia esculpida no quartzo aura e sanitário branco"; "Vestiário: mármore bege Bahia no piso e Cuba esculpida, bancada da pia no granito marrom, sanitário branco". O vestiário é do Subsolo, aprovado pouco antes: o pedido o reabre.

- Lavabo: em `MATERIAIS_TD`, a bancada passa do `granito` ao `travertino` (a cuba esculpida vai junto, em travertino); o vaso já era marrom.
- Banhos das suítes (banho master e banhos 1, 2 e 3): o piso em quartzito Aura (`quartzito_banhos_d`, na etapa dos pisos, logo depois de `F.pisos`): a mancha de Bege Bahia de cada banho (a máscara dos pisos, sem as paredes, a componente que tem o rótulo do PDF), com a luz larga do render (o Bege Bahia de antes) e o desenho da chapa da biblioteca (`_texturas/amostras/quartzito_aura.jpg`, só a luz, sem a cor), no tom entre o branco e o cinza dos banhos do 1º Pavimento da Casa E (BGR 211, 215, 221). As bancadas e as cubas esculpidas no mesmo quartzito: `F.bancadas` e `F.cuba_esculpida` (no `final3840_casab.py`) aceitam agora uma chapa da biblioteca num tom (`_chapa_luz`; `BANCADAS_F["chapas"]` e `BANCADAS_F["cuba_<material>"]` com `chapa`), que `contexto_d` liga só para a Casa D (`CHAPAS_D`, `CUBAS_CHAPA_D`); as outras casas não mudam. A bancada fica no tom do piso, marcada pela borda e pela sombra (E9); a cuba, um pouco mais clara. O vaso já era branco. O nicho com a cuba redonda junto à suíte 2 é a bancada da sala íntima, não um banho: fica.
- Vestiário (Subsolo): a cuba esculpida em Bege Bahia (`F.cuba_esculpida(..., "bege")`, `CUBAS_CHAPA_D["cuba_bege"]`), o vaso branco (`VASOS_SUB_D` vazio); o piso já era Bege Bahia e a bancada, granito marrom.

Rodados `final3840_casad.py Subsolo --de vasos` e `final3840_casad.py Terreo` (inteira, o piso dos banhos é da primeira etapa). Conferido: no Térreo, as mudanças ficam no lavabo e nos quatro banhos (72.553 px de piso, cerca de 20 m²), mais diferenças de 1 a 2 px nos caixilhos de três janelas da fachada de baixo (a rodada inteira refaz a limpeza das esquadrias), que não se veem; no Subsolo, só a cuba e o vaso do vestiário. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710_{lavabo,banhos_suites}_antes_depois.jpg` e `POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_pedidos2710_vestiario_antes_depois.jpg` (os `..._Terreo_2610_*_antes_depois.jpg` refeitos sobre a final nova). Pranchas do Térreo e do Subsolo e PDF da Casa D refeitos. Aguarda os outros ajustes da Casa D.

### Depois: "Melhore o aspecto do travertino bruto." (27/10/26)

Entendido como as bancadas e as cubas esculpidas de travertino bruto (lavabo e banho gourmet, os pedidos anteriores); os pisos de travertino em estratos (living/jantar, hall, lavabo) ficam. Antes, com o desenho da Casa C (`C.travertino_bruto_tc`), elas saíam num rosado quase de madeira clara (BGR 172, 190, 210), lisas, com poucos poros. Comparadas variantes lado a lado com a foto da biblioteca (`_texturas/originais/travertino.webp`, RGB ~228, 221, 204): ficou a do creme da foto, um pouco mais escuro na bancada (BGR 186, 204, 216) que na cuba (200, 217, 228), com os estratos mais marcados (`amp` 1,5, as faixas finas inteiras), 1,6 vez os poros e 1,85 vez a força deles, e o veio no comprido da peça (`travertino_bruto_d`, `TRAVERTINO_BRUTO_D`; na bancada em pé do lavabo, na vertical). Só na Casa D (`contexto_d` troca os tons em `F.BANCADAS_F`; `final_3840_d` liga `FA.travertino_bruto = travertino_bruto_d`).

Rodado `final3840_casad.py Terreo --de bancadas`. Conferido: só as duas bancadas e as duas cubas mudam. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710_travertino_bruto_antes_depois.jpg`. Prancha do Térreo e PDF da Casa D refeitos.

### Depois: portas de vidro, projeções da laje, carros, planta, linha marrom, beiral, quadrado e armário (27/10/26)

Pedidos, vendo a final do Térreo (cada um com um recorte da imagem): "corrija a representação dessas portas de vidro" (living/varanda); "faltou a representação correta dessas projeções" (o gramado abaixo da garagem); "melhorar a representação dessas projeções em branco" (a garagem); "melhorar a representação dos veículos"; "remova esse elemento decorativo do gourmet" (a planta sobre a bancada); "representar a soleira e a porta de correr adequadamente" (cozinha/living); "não existe essa linha marrom"; "armário à esquerda com cabides."; "esse beiral é todo no bege bahia. remova o vinilico daqui"; "esse quadrante pontilhado não existe aqui". O pedido dos móveis ("melhorar a representação dos mobiliários [...] revise uma a uma e entregue com primor") fica para depois deste lote, com uma amostra para aprovar o padrão.

- Portas: `portas_vidro_td` no fim da etapa `esquadrias`, com `final3840_casaa.portas_vidro` e `PORTAS_VIDRO_TD` (do PDF: a soleira, os batentes e as folhas de cada porta). No living, a soleira de Bege Bahia de 1589,1 a 1597,6 pt, os dois batentes e as 4 folhas em dois planos (as das pontas por fora, 1595,3 a 1597,6; as do meio, 1593,0 a 1595,3); na cozinha, a soleira no vão (1757,2 a 1861,6 x 868,4 a 876,9) e a folha de correr do lado da cozinha (1744,2 a 1851,9 x 865,8 a 868,1), sem batentes (no PDF a parede encosta na soleira). Desenhada como as outras folhas de correr (alumínio e vidro). `RESTOS_PORTAS_TD`: a ponta escura da folha antiga do render, à direita da folha nova da cozinha, e os três puxadores antigos nas emendas das folhas do living (do lado do living) voltam ao piso 6 px acima (os px mais escuros que a mediana do retângulo menos 25).
- Projeções da laje: `projecoes_lajes_td` no fim da etapa `projecoes` (`PROJ_LAJES_TD`). Os 9 vãos do PDF (EST_LAJE; x de 2420,1 a 2868,1 pt, na garagem de 570,7 a 661,4 e no gramado de 995,9 a 1081,0) com o X tracejado; no gramado, o contorno de cada vão (topo e lados) e a borda da laje à esquerda (x 2383,3) em traço fino contínuo, e as duas linhas tracejadas de baixo (1081,0 e 1092,3, a partir da grama); na garagem, as duas linhas de cima (559,4 e 570,7), a de baixo (662,0), as bordas da direita (2899,3 e 2910,6, até o brise) e a da esquerda (2383,3, abaixo do gás). No PDF os contornos dos vãos da garagem existem, mas o piso os cobre: não entram. O tracejado do render nas duas linhas de cima da garagem (escuro, desde a etapa dos pisos) sai antes: na faixa de ±2 px, os px mais escuros que o granito em volta voltam ao granito 6 px acima (3159 px). O tracejado é o de `C._tracejado` (0,10 m de traço, 0,05 m de vão, 1,1 px; o contínuo, 0,7 px), em branco quente (BGR 228, 233, 236), fora das paredes (o cinza 80, dilatado 1 px). As zonas da garagem e do gramado saíram de `PROJECOES_CLARAS_D` e `COBERTURA_D`.
- Carros: `carros_d` com o carro do meio da final aprovada da Casa C (prata, nítido, na mesma escala; a silhueta é o que não tem o tom do granito), levado à medida da R12 (escala 1,08 x 1,02) em cada centro do PDF, com a sombra curta; antes, o carro branco do render de 2000 px da Casa D, recolorido em prata (vidros com ruído, borda irregular).
- Planta da bancada gourmet: saiu de `VASOS_D` (o render não volta ali) e o desenho dela no PDF fica fora das peças (`SEM_PLANTA_TD`): fica a bancada.
- Linha marrom e beiral: as duas eram brises de `BRISES_D` (a faixa à direita da escada, sob a porta de vidro do hall, e a faixa da fachada de baixo à esquerda). No PDF, as ripas dessas duas caixas (ARQ_ELEMENTOS FIXOS, preenchimentos brancos de 1,7 x 4 pt) estão por baixo do piso, pintadas antes dele, e não aparecem; nas outras caixas aparecem. As duas caixas saíram: ali fica o Bege Bahia dos pisos. Nos nichos das duas janelas desse beiral (entre o caixilho e a face de fora da parede, brancos no PDF), o brise escondia o desenho antigo da janela do render: `NICHOS_BEIRAL_TD` copia neles o Bege Bahia do beiral logo abaixo.
- Quadrado da circulação: um preenchimento branco de 0,8 m da ARQ_LAYOUT HUMANIZAÇÃO (1677,7 a 1723,5 x 1512,5 a 1558,2 pt) que o PDF pinta antes do vinílico, escondido; entrava como peça, com o contorno tracejado do render. `PECAS_OCULTAS_TD` o tira das peças.
- Armário: `GUARDA_ROUPAS_TD` ganha o armário à esquerda do corredor do banho master (787,4 a 821,5 x 1806,6 a 1880,3 pt), aberto para o corredor (à direita), com os cabides, como o do outro lado.

A regra geral entrou no `POE642_REGRAS.md` (seção 9): só o que aparece no PDF entra; os vãos de laje com o contorno onde o PDF o mostra. O brise da fachada de baixo à direita (1793,5 a 2063,1 pt) aparece no PDF (as ripas por cima do beiral) e fica em madeira; as duas peças giradas junto à gourmet (`BRISES_D`, 1141,2 a 1201,0 x 760,1 a 879,7) também estão escondidas no PDF: ficam até o usuário decidir.

Rodados `final3840_casad.py Terreo --de pecas` e, com a limpeza dos restos e dos nichos, `--de esquadrias`. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710_{portas_vidro_living,porta_cozinha,projecoes_garagem,projecoes_gramado,carros,planta_gourmet,linha_marrom,beiral,quadrado_circulacao,armario_cabides}_antes_depois.jpg`. Conferido contra a final anterior: as mudanças ficam nos itens pedidos; fora deles, só o tom das ripas dos brises que vêm depois das duas caixas tiradas (a lateral da suíte 3, a fachada de baixo à direita e as duas peças junto à gourmet) muda de leve, porque o sorteio do tom por ripa andou (não se vê). O Subsolo, rodado de novo da hachura, não muda (0 px). Prancha do Térreo e PDF da Casa D refeitos.

### Depois: móveis, floreiras, banquetas, beiral, box gourmet, recolhimento e paredes atrás das portas (27/10/26)

Respostas às perguntas do lote anterior: "1. sim, todo em bege bahia. 2. remova. 3. vidro ok". Pedidos, vendo a final do Térreo (cada um com um recorte): "nesses "caixotes" externos temos floreiras. adicione o verde para termos as floreiras"; "melhore a aparencia das cadeiras e as coloque parcialmente sob as mesas"; "melhore a aparencia dessa poltrona. revestimento, textura" (sala íntima); "as banquetas ficam parcialmente sob a bancada da ilha"; "melhore o aspecto dessas poltronas. essas linhas marcantes devem sair e termos algo mais humanizado com textura e revestimento" (living); "melhore o aspecto das poltronas e da mesa de centro. as linhas marcam muito. traga textura, revestimento, efeito humanizado" (estar junto à mesa de jantar); "tem um risco branco no meio do guarda roupa. precisamos limpar esses resíduos da planta"; "marca com um tom claro esse box do banho gourmet."; "a parte de baixo onde se recolhe todas as portas de vidro deve ficar igual ao espaço de cima. o branco do espaço vazio sai para o tom acinzentado igual da parte de cima"; "melhore o aspectos desses jogos de mesa. adicione um freijó às mesas e cadeiras mais realistas e humanizadas."; "corrija as paredes que estão atrás das portas. existe um recorte na imagem que precisa ser preenchido com a parede."

- Beiral de baixo à direita: `BRISES_D` sem a faixa dele e sem as duas peças giradas junto à gourmet; `BEIRAL_BEGE_TD` no fim de `portas_vidro_td` leva à faixa toda (da face das paredes à grama, 1596,0 a 2057,2 pt) o Bege Bahia do beiral da esquerda (as colunas do trecho mais comprido só de Bege Bahia, em espelho alternado); `NICHOS_BEIRAL_TD` ganhou os 2 nichos das janelas desse lado. A porta da cozinha segue em vidro.
- Floreiras: `floreiras_td` (`FLOREIRAS_TD`), os dois miolos dos caixotes da fachada de cima (2,6 x 0,19 m) com 18 plantas de folha larga cada, pelo `C.floreira_lavabo_t`, sem seixos.
- Móveis: a etapa nova `moveis` (`moveis_td`, `MOVEIS_TD`). As 4 poltronas em X, as 2 redondas do living e a da sala íntima em bouclé (`estofado_d`: a silhueta do PDF em 4x, as almofadas com volume e luz, a trama e a borda macia, sem os traços); a da sala íntima como concha, com o assento puxado para a mesa de centro (`conchas`). A mesa de centro, as laterais e a do living em madeira até a borda, sem o contorno escuro (`madeira_d`); as peças de madeira (R − B acima de 28) ficam fora dos estofados (com 20, a mesa de centro, do tamanho das poltronas, virava bouclé, e com a exclusão as duas poltronas da esquerda viravam madeira). As cadeiras da suíte master, da suíte 1 e do escritório (a da mesa e as duas de visita): a do render sai e entra a de madeira e linho da biblioteca, de frente para a mesa, 1/3 sob o tampo (`cadeiras_mesas_d`); na suíte master, a etapa dos pisos ainda tinha as pontas dos braços da cadeira do render, e o piso vem do vinílico livre 40 px à esquerda. Os dois jogos da varanda gourmet: a mesa redonda de 1,60 m em freijó (`_freijo`: o dourado claro, o veio reto, as tábuas de 0,16 m, o chanfro e o brilho) por cima das 6 cadeiras de madeira e linho, viradas para o centro (`jogos_mesa_d`).
- Frente da cadeira: na folha da `banqueta_linho`, a frente do assento fica em cima e o encosto embaixo (`blocos.json`). `_cadeira_bloco` partia da frente embaixo e as cadeiras novas saíam de costas para a mesa; corrigido. As banquetas da ilha gourmet (`BANQUETAS_D["giro"]` 180) também estavam de costas para a ilha: agora `giro` 0, a frente sob o tampo e o encosto à vista.
- Armários até o teto: `diagonais_armarios_d` tira os pontos brancos do render ao longo das 16 diagonais (114 px): o px mais claro que a mediana em pé e a deitada, ou que os 4 vizinhos, toma a média do par de vizinhos mais parecido. A primeira versão (a mediana de 11 x 11) escurecia os vãos entre os cabides e os cantos junto às paredes.
- Box do banho gourmet: `box_gourmet_d` (`BOX_GOURMET_TD`), o vidro fixo do PDF (as duas linhas tracejadas da ARQ_LOUÇAS E METAIS, 1252,3 a 1255,1 pt) em faixa clara com as faces finas, no lugar do traço cinza-escuro do render.
- Recolhimento das folhas do living: `RECOLHE_TD`, o vão de baixo (1367,3 a 1489,2 pt, branco) recebe o de cima, refletido e repetido.
- Paredes atrás das portas: `pos_esquadrias_d` com `claro` (Térreo): a parede escura do PDF que a limpeza das folhas clareou em tiras finas e compridas volta (1969 px; os entalhes dos banhos 2 e 3 e os das outras portas de giro). A etapa `esquadrias` passa `im.copy()` ao `F.esquadrias_terreo`, que muda a entrada: sem a cópia, a referência já vinha recortada e nada voltava.

Rodado `final3840_casad.py Terreo` (desde as etapas mudadas, por último `--de moveis`). Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710b_{beiral_direita,floreiras,banquetas,cadeiras_suite_master,cadeiras_suite1,cadeiras_escritorio,jogos_mesa,poltronas_estar,poltronas_living,poltrona_intima,armarios,box_gourmet,recolhimento_porta,parede_banhos}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa D refeitos; o Subsolo, rodado de novo da hachura.

Achado para o OK do usuário (não alterado): no Térreo aprovado da Casa C, as 4 banquetas à esquerda da ilha gourmet (`BANQUETAS_C["giro"]` 270) estão de costas para a ilha (a frente do assento para fora, o encosto sob o tampo). Nas Casas A, B e E estão de frente. A correção seria `giro` 90 e rodar o Térreo da Casa C desde a etapa das banquetas.

### Depois: jogos da varanda, cadeiras do jantar, vincos das poltronas, suíte 2, bancada dos tanques, tracejado e plantas (27/10/26)

Pedidos, vendo a final do Térreo (cada um com um recorte): "preciso que os tampos das mesas estejam em escala" (jogos da varanda); "altere o tom da bancada para o marrom granito" (a dos tanques da área de serviço); "aprimore o revestimento dessa poltrona e seu apoio. as linhas deixam muito técnicos, precisamos de sombras e textura" (suíte 2); "você tirou as linhas, mas não deixou o contorno delas em formato de sombra para deixar claro as partes e encosto da poltrona" (as 4 em X); "melhore o aspecto das cadeiras, sem repetir o modelo das demais da planta" (mesa de jantar do living); "mantenha o tracejado branco até o fim, removendo o tom preto" (a linha da laje junto ao gás); "o sombreado das plantas ficou muito carregado. suavize mais." (os vasos do hall). Depois, vendo o conjunto de mesa redonda de madeira com 6 cadeiras de couro da biblioteca (a referência do usuário das mesas da varanda da Casa E), mostrado na conversa como opção de cadeira: "USE ESSA MESA E CADEIRAS NA VARANDA, NO LUGAR DAQUELAS".

- Jogos da varanda: `jogos_mesa_d` põe o conjunto `mesa_redonda_6_couro` inteiro no centro de cada mesa do PDF, com o tampo no diâmetro dela (1,60 m; o tampo do bloco tem 705 px a 400 px/m), o segundo girado 180° (como na Casa E), com a sombra curta. O freijó procedural saiu. Antes de responder ao "em escala" com o conjunto, o freijó tinha passado a medidas reais (fio de 4 mm e 0,9 m, listras de 2 m, tábuas de 12 cm, como o do depósito da Casa A); com o conjunto, o desenho da madeira é o da foto, levado ao tamanho da peça.
- Piso sob os jogos: a etapa dos pisos guarda o render sob as peças (as cadeiras brancas antigas, maiores que as novas), que aparecia em volta das cadeiras de couro como um halo. `bege_limpo_d` refaz o Bege Bahia na caixa de cada jogo: o mesmo `textura("bege_bahia")` de `F.piso_textura` (semente 703, o retângulo do Bege na legenda), na luz do piso em volta (o piso dividido pelo desenho é liso; é levado para dentro). Conferido: sem emenda. A textura inteira leva ~45 s; o recorte de cada caixa fica guardado em `F.ETAPAS`.
- Mesa de jantar: com o couro na varanda, a cadeira de couro no jantar repetiria o modelo. `jantar_d` usa a cadeira de cima da `mesa_jantar_10` (estofada em linho, com o quadro de madeira), com o linho levado ao bege quente (na foto, cinza-esverdeado e na sombra da mesa) e a madeira mantida, o alfa 1 px menor (o halo da foto), de frente para a mesa, 1/3 sob o tampo. O piso sob as cadeiras antigas (também na etapa dos pisos) vem do travertino ao lado, nas mesmas linhas (os estratos são deitados). Na planta ficam três modelos: a de madeira e linho (mesas de trabalho e banquetas), a de linho com quadro de madeira (jantar) e a de couro (varanda).
- Poltronas: `estofado_d` com os vincos (os traços de dentro do PDF de 2,5 pt para cima, longe da borda, como uma sombra macia com a borda clara do lado da luz): as partes (assento, encosto, braços) aparecem nas 4 em X, nas 2 redondas do living e na da suíte 2; na concha da sala íntima, só o vinco do assento (o desenho miúdo do PDF fica fora). A poltrona girada e o puff da suíte 2 entraram nos estofados.
- Bancada dos tanques da área de serviço: em granito marrom escurecido, como as da cozinha (`MATERIAIS_TD["granito_escuro"]`); antes caía na pedra clara padrão.
- Tracejado junto ao gás: no PDF, a linha de 559,4 pt começa na ponta da floreira (2213 pt); o tracejado branco e a limpeza do escuro do render começavam em 2335,7. Agora desde 2214.
- Plantas do hall: `plantas_vaso_d`, só as folhas do render (`folhas_d`: o verde e o escuro abaixo de 95 ligado a ele; o `C.verde` levava o quadrado cinza da sombra do render) e a sombra curta mais leve e aberta.

Rodado `final3840_casad.py Terreo --de bancadas` e, com o conjunto da varanda e as cadeiras do jantar, `--de moveis`. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710c_{jogos_varanda,bancada_servico,poltrona_suite2,poltronas_estar,poltronas_living,poltrona_intima,cadeiras_jantar,tracejado_gas,plantas_hall}_antes_depois.jpg`. O Subsolo, rodado de novo da hachura, não muda (0 px). Prancha do Térreo e PDF da Casa D refeitos.


### Depois: cooktops, recolhimento do elevador, tracejado da ilha, tapete, trilho da cortina e tom dos jogos da varanda (27/10/26)

O usuário deu "OK" e, logo depois: "ainda não tem ok para o térreo da casa d". O Térreo da Casa D segue sem aprovação; a Casa E vem depois dele. Pedidos, vendo a final (cada um com um recorte): "você precisa girar 180º os dois cooktops"; "suavize as bordas do tapete da suite master"; "essa linha não existe no meio da imagem" (no Bege Bahia junto à grama); "esse vão para entrada das portas de vidro para a esquerda não pode ser branco. faça como fizemos para as portas de vidro do living. são meio acinzentadas, por isso aplique aqui também"; "tem tracejados embaixo da ilha. precisamos removê-los"; "conseguimos deixar o tom desses mobiliários mais próximo do tom das outras mobílias? não queria que destoasse" (os jogos da varanda); e, sem aplicar, "vamos melhorar esse mobiliario. encontre na nossa biblioteca o que tem de semelhante e me apresente como proposta" (o estar do living).

- Cooktops: os dois girados 180° (`COOKTOPS_D`): 3 bocas em cima, 2 embaixo, os botões do lado de quem cozinha.
- Recolhimento do elevador: o vão deitado na parede de cima do elevador, onde as folhas de vidro da sala íntima se recolhem, era o branco do PDF; recebe o vão de cima do living, girado (seção 4 das regras).
- Tracejado da ilha: não há linha no PDF ali. É um tracejado cinza do render na borda de baixo do granito do gourmet, da esquerda da ilha até a parede do living, que a etapa dos pisos guardava (a borda fica fora da legenda). Sai na etapa dos pisos; a divisa fica granito em cima e Bege Bahia embaixo.
- Tapete da suíte master: no PDF (ARQ_LOUÇAS E METAIS), as franjas dos dois lados são traços juntos, pintados como hachura (faixa cinza de 4 px), com o contorno escuro. Agora a borda é macia (o tapete passa ao vinílico em ~3 px, com a beira um pouco mais escura e a sombra curta), sem mexer na cabeceira, na cama e nos criados.
- A linha no Bege Bahia: era o trilho da cortina da esquerda da suíte master. O trilho vai de parede a parede, e o canto de cima da suíte é de vidro: ele subia pelo deck até a faixa da cobertura. Agora para na face da suíte.
- Jogos da varanda: o tampo de nogueira escura no mel do aparador e da mesa de jantar, as cadeiras de couro escuro no areia do linho e do bouclé, o vidro fumê do centro em cinza claro; o desenho da foto fica (seção 8).
- Proposta do estar do living (não aplicada): `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_proposta_estar_living.jpg`, o atual ao lado de duas composições com a biblioteca, nas posições do PDF. Proposta A: 4 poltronas bouclé, o par de mesas de centro redondas (no carvalho claro), o sofá reto de 3 lugares com almofadas, as mesas laterais raiadas e, no lugar do banco xadrez, o aparador de madeira (a biblioteca não tem banco). Proposta B: bouclé em cima e as de madeira e linho à esquerda, o mesmo centro e sofá, e no lugar do banco o sofá de 2 lugares. Aguardando a escolha.

Rodado `final3840_casad.py Terreo --de pisos`. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710d_{cooktop_gourmet,cooktop_cozinha,tracejado_ilha,recolhimento_elevador,tapete_suite_master,trilho_cortina,jogos_varanda}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa D refeitos.

### Depois: ripas em L, tracejado da laje, soleira, rótulo do WC DCE, sofá do living e lajes em cinza claro (27/10/26)

Pedidos, vendo a final (cada um com um recorte): "volta as cadeiras que estavam antes" (os jogos da varanda, vendo as cadeiras no areia; a correção, as cadeiras de volta ao couro da foto, foi recusada antes de rodar e a pergunta de qual versão ficou sem resposta: em aberto, as cadeiras seguem no areia); "esse revestimento em marrom em L e em volta das portas de vidro é contínuo. de uma parede a outra"; "esse pontilhado branco se estende até depois do banho gourmet"; "a soleira que divide a cozinha da área de serviço precisa ser melhor representada. ela é mais larga do que foi apresentado aqui"; "o rótulo aqui está sobre a porta. preciso que coloque dentro do box como está no pdf, com fonte mais reduzida" (WC DCE); "represente melhor esse sofá e almofadas, mais humanizado" (o estar do living); "vamos melhorar a representação da projeção tracejada em branco. tem a laje aqui em cinza claro" (a lateral da sala íntima, junto ao brise); "vamos representar a laje em tom cinza claro aqui, na borda do jardim da sala íntima".

- Ripas em L da suíte master: a etapa das paredes as desenha inteiras (o brise da fachada da suíte), mas a limpeza das esquadrias, que espelha o piso de junto do vidro, as apagava diante das portas de vidro (em cima, e embaixo à esquerda). Voltam depois das esquadrias, só as ripas do PDF.
- Tracejado da laje da fachada de cima: no PDF, os traços de 559,4 pt vão de 1147,3 a 2298,8 pt (passam o banho gourmet, a grama e as duas floreiras); a linha branca começava na ponta da floreira (2214 pt).
- Soleira da cozinha para a área de serviço: o vão da parede no PDF tem 8,5 × 53 pt (a espessura inteira); a etapa das soleiras não o achava e ficava um fio rosado do render. Agora a soleira de Bege Bahia no vão inteiro, com as faces finas.
- Rótulo do WC DCE: no ponto do PDF, dentro do box, a 62% do corpo, em duas linhas e a área (o motor ganhou os rótulos fixos, `ROTULOS_F["fixos"]`). A regra de 22/10 (o rótulo não vai para o box) segue nos outros banhos.
- Sofá do living: o sofá reto de 3 lugares da biblioteca (o das duas propostas do estar), montado com um lugar a mais e os dois braços iguais, no retângulo do PDF (3,03 × 1,02 m), o encosto embaixo, com as 3 almofadas. O resto do estar segue como estava, aguardando a escolha da proposta A ou B.
- Laje da lateral da sala íntima: no PDF, além da faixa de laje (o cinza claro, que fica), um retângulo tracejado de 2284,3 a 2295,6 pt, de 1497,7 a 1894,5 pt; o render o desenhava em preto. Agora em branco, como os da garagem, com o preto limpo.
- Laje da borda do jardim da sala íntima: a faixa da EST_LAJE sob o jardim (onde o render tinha as plantas e um fio cinza) no cinza claro da faixa de laje da lateral, deitada e mais lisa.

Rodado `final3840_casad.py Terreo --de moveis`. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710e_{ripas_suite_master,tracejado_banho_gourmet,soleira_cozinha_servico,rotulo_wc_dce,sofa_living,laje_lateral,laje_jardim_sala_intima}_antes_depois.jpg`. O Subsolo, rodado de novo da hachura, não muda (0 px). Prancha do Térreo e PDF da Casa D refeitos.

Segue em aberto (do lote anterior): as banquetas do Térreo aprovado da Casa C de costas para a ilha (`BANQUETAS_C["giro"]` 270; a correção seria 90), aguardando o OK do usuário.

### Depois: beiral num tom só, fechamento do tracejado, box do banho gourmet e adega em U (27/10/26)

Pedidos, vendo a final (cada um com um recorte): "vamos manter o beiral no mesmo tom claro e uniforme de fora a fora" (o beiral de baixo, do jardim da sala íntima à suíte 2); "faltou o fechamento da projeção em tracejado branco." (a ponta esquerda da laje da fachada de cima, junto ao banho gourmet); "faz o fechamento do box" (o banho gourmet); "faz a adega em u".

- Beiral de baixo: o Bege Bahia claro e uniforme de fora a fora, também sob o jardim da sala íntima. Substitui o cinza claro da borda do jardim, do lote anterior (a regra foi revista nas REGRAS, seção 9); a faixa de laje da lateral, junto ao brise, segue em cinza claro. Logo abaixo do beiral, onde o render tinha um fio cinza, a grama.
- Fechamento do tracejado: no PDF, a projeção da laje fecha na ponta esquerda com duas linhas de pé (1147,3 e 1158,6 pt) e um trecho de volta (570,7 pt); agora em branco, como o resto.
- Box do banho gourmet: o vidro fixo vai da parede de cima à de baixo, como as duas linhas tracejadas do PDF (antes começava uns 0,4 m abaixo da parede).
- Adega em U: além da prateleira do fundo, as das paredes de cima e de baixo, no mesmo desenho (marcenaria areia com veio, 2 módulos cada, 20 garrafas na escala, o gargalo para a parede), da prateleira do fundo até perto das folhas de vidro; o rótulo fora delas. Elas entram depois das esquadrias: a limpeza das esquadrias, que espelha o piso de junto do vidro, copiava a ponta da prateleira de baixo para o vão.

Rodado `final3840_casad.py Terreo --de biblioteca`. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710f_{beiral_esquerda,beiral_direita,fechamento_projecao,box_banho_gourmet,adega_u}_antes_depois.jpg`. O Subsolo, rodado de novo da hachura, não muda (0 px). Prancha do Térreo e PDF da Casa D refeitos.

Seguem em aberto, aguardando o usuário: as cadeiras dos jogos da varanda ("volta as cadeiras que estavam antes": qual versão), a proposta A ou B do estar do living, a faixa branca vertical à esquerda do elevador (manter ou cinza) e as banquetas do Térreo aprovado da Casa C (`BANQUETAS_C["giro"]` 270 → 90, sem mexer na Casa C sem o OK). O Térreo da Casa D segue sem o OK.

### Depois: beiral em L, porta da suíte 2, o sofá anterior e o rótulo da adega (27/10/26)

Pedidos, vendo a final (cada um com um recorte): "o beiral também sobe formando o L. segue o bege no lugar desse cinza claro com falhas. remova o cinza e substitua por bege. não altere paredes e nem o tracejado." e, depois, "é somente esse trecho até o brise marrom." (a lateral do escritório); "na suite 2, abaixo da porta de vidro à direita tem uma linha preta que não deveria existir, remova-a. são três folhas que se movem para esquerda. folhas únicas, sem estarem duplicadas."; "volte o sofá anterior. esse não ficou bom, muito artificial." (o estar do living); "centralize o rótulo" (a adega).

- Beiral em L: a faixa cinza com falhas entre a parede do escritório e o tracejado da laje, do pé do brise até o beiral, agora no Bege Bahia do beiral, de pé e contínuo com ele no canto. A parede e o tracejado ficaram idênticos (0 px de diferença); para isso o L entra depois das projeções (a limpeza do tracejado da lateral comparava com a faixa e, com o claro, mexia nele).
- Porta da suíte 2: a soleira de Bege Bahia no vão do PDF e as três folhas, uma em cada plano (a da direita por dentro, a da esquerda por fora), cada uma numa folha só, como as do living (o render as desenhava em dois traços, num bloco cinza e num fio). A linha preta embaixo do vão (a face da soleira e a do beiral) saiu: o Bege da soleira passa direto ao beiral.
- Sofá do living: o sofá da biblioteca saiu; voltou o anterior, igual, pixel a pixel, ao de antes do 6º lote. O resto do estar segue aguardando a proposta A ou B (as duas usavam o sofá da biblioteca; se uma for escolhida, o sofá fica o anterior, salvo novo pedido).
- Rótulo da adega: no meio do piso livre do U (entre o vidro e a prateleira do fundo, e entre as de cima e de baixo).

Rodado `final3840_casad.py Terreo --de moveis`. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710g_{beiral_l,porta_suite_2,sofa_living,rotulo_adega}_antes_depois.jpg`. O Subsolo, rodado de novo da hachura, não muda (0 px). Prancha do Térreo e PDF da Casa D refeitos.

Seguem em aberto, aguardando o usuário: as cadeiras dos jogos da varanda ("volta as cadeiras que estavam antes": qual versão), a proposta A ou B do estar do living, a faixa branca vertical à esquerda do elevador (manter ou cinza) e as banquetas do Térreo aprovado da Casa C (`BANQUETAS_C["giro"]` 270 → 90, sem mexer na Casa C sem o OK). O Térreo da Casa D segue sem o OK.

### Depois: beiral diante do brise, pia da cozinha, tracejado do deck, rótulos, almofadas de lã, pisante e poltrona da suíte master (27/10/26)

Pedidos, vendo a final (cada um com um recorte): "corrija só um trecho fino do beiral que ficou com vestígios antigos em cinza. esse beiral passa em frente ao brise marrom, mas em uma faixa estreita."; "entre a cuba e a jardineira tem uma faixa branca que não deveria estar ali. o contorno da pia é em marrom granito igual a pia da direita. acima da pia esquerda tem esse item em branco que não existe" (a pia da cozinha); "dentro da área do bege bahia não tem tracejado. ele termina logo acima, no encontro com o piso bege bahia. dali para baixo já não tem mais, assim como o pdf" (o fechamento junto à ducha do deck); "corrija a posição do rótulo, de forma que não fique sobre o armário. centralize no piso." (despensa); "deixe ao menos as almofadas em um tom sólido, sem linhas.", "nas almofadas deixe evidente os contornos para que saibamos que existem uma na frente da outra", "pode ser até tom sobre tom para cada uma das almofadas. sendo uma mais escura atrás e outra mais clara na frente" e "traga um revestimento com textura pra dar efeito almofada de lã" (o sofá do living); "tem um traço branco no contorno de baixo do bloco de pedra no acesso a casa. formando um dente que não existe. corrija, deixando-o reto."; "rótulo em branco" (DCE TÉRREO); "aplique na poltrona e suporte da suíte master o mesmo revestimento estofado da poltrona da suíte."

- Beiral diante do brise: a faixa de 3 px entre as lâminas do brise e o tracejado, do canto da laje até o pé do brise, no Bege Bahia do beiral, contínua com o L. O brise e o tracejado não mudam.
- Pia da cozinha: o branco em cima da cuba da esquerda vinha da limpeza das esquadrias (espelhava a cuba junto à janela); agora o granito com a torneira, como na da direita.
- Tracejado do deck: no PDF, o deck cobre as linhas de pé; a de fora vai só até a borda do Bege Bahia e a de dentro saiu. A linha de dentro, sobre a borda, fica (o PDF a mostra).
- Rótulos: o da despensa no meio do piso livre, entre a folha da porta aberta e o armário em L; o do DCE TÉRREO em branco (o motor ganhou os rótulos brancos por pedido).
- Almofadas do sofá do living: cada uma em duas peças, a de trás mais escura e a da frente mais clara, num tom só cada, com o contorno fino e a da frente por cima; o revestimento é o tricô da almofada de lã da biblioteca, na escala, com as carreiras deitadas e o volume de almofada.
- Pisante junto ao hall: a parte da esquerda passava 2 px da borda de baixo do PDF (o traço claro do dente); agora a borda é reta, como a da direita.
- Poltrona e apoio da suíte master: o estofado da suíte 2 (bouclé com volume, o assento, o encosto e os braços em vincos). No PDF, as costuras dela vêm picadas em segmentos curtos; todos contam.

Rodado `final3840_casad.py Terreo --de moveis`. Antes e depois: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_pedidos2710h_{beiral_brise,pia_cozinha,tracejado_deck,rotulo_despensa,almofadas_sofa,pisante_hall,rotulo_dce,poltrona_suite_master}_antes_depois.jpg`. O Subsolo, rodado de novo da hachura, não muda (0 px). Prancha do Térreo e PDF da Casa D refeitos.

Apresentado ao usuário, sem alterar (aguardando o OK): os tanques da área de serviço têm o mesmo branco da limpeza das esquadrias entre a janela e as cubas. A pergunta "consegue trazer essa textura de sofá para o nosso?" chegou sem imagem: perguntado qual textura (a lã das almofadas no sofá todo, ou outra).

Seguem em aberto, aguardando o usuário: as cadeiras dos jogos da varanda ("volta as cadeiras que estavam antes": qual versão), a proposta A ou B do estar do living, a faixa branca vertical à esquerda do elevador (manter ou cinza) e as banquetas do Térreo aprovado da Casa C (`BANQUETAS_C["giro"]` 270 → 90, sem mexer na Casa C sem o OK). O Térreo da Casa D segue sem o OK.

**Aprovado** (28/10/26): "APROVADA", logo depois do 9º lote. Térreo da Casa D fechado, como está na final (`POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png`), na prancha e no PDF da Casa D (`POE642_CasaD/entrega/POE642_CasaD_Plantas_Humanizadas.pdf`, Subsolo e Térreo). A Casa D está fechada (o Subsolo foi aprovado em 27/10). Com a aprovação, ficam como estão os itens da Casa D que esperavam resposta: os tanques da área de serviço (o branco entre a janela e as cubas, apresentado sem alterar), as cadeiras dos jogos da varanda (no areia), o estar do living (sem a proposta A ou B; o sofá anterior com as almofadas de lã), a faixa branca à esquerda do elevador e a textura do sofá (a pergunta sem imagem). Segue em aberto, de outra casa, as banquetas do Térreo aprovado da Casa C (`BANQUETAS_C["giro"]` 270 → 90, sem mexer na Casa C sem o OK). A seguir, a Casa E (Subsolo, Térreo e 1º Pavimento), planta por planta: a lista de inconformidades de cada uma para o OK antes de alterar.

## Casa E · rodada de 28/10/26 (auditoria de 26/10, planta por planta, sem esperar o OK)

Pedido do usuário (28/10/26), logo depois de aprovar o Térreo da Casa D: "PODE COMEÇAR COM O SUBSOLO, NA SEQUENCIA O TERREO E DEPOIS O PRIMEIRO PAVIMENTO. VOU DORMIR AGORA E QUERO QUE ELENQUE AS ALTERAÇÕES, APLIQUE-AS E AMANHÃ CEDO EU VALIDO. SÓ FINALIZE APÓS QUE APLICAR A ÚLTIMA ALTERAÇÃO DA ÚLTIMA PLANTA QUE É O 1º PAVIMENTO." Desta vez a lista não espera o OK: cada planta tem a lista e a aplicação, e o usuário valida de manhã.

A lista de cada planta é a da auditoria de 26/10 (`POE642_CasaE/renders/POE642_CasaE_PH_<pav>_auditoria_2610.jpg`) com as regras que as Casas A a D já aprovaram (`POE642_REGRAS.md`, seção 19). Motor novo: `POE642_CasaA/scripts/final3840_casae.py`. Ele parte da final aprovada de cada pavimento, lida do git (o commit está em `PAV_E`), tira os rótulos pela conta inversa da composição (a mesma rotina dos rótulos sobre um quadro preto e um branco dá o alfa e a cor de cada px do texto) e, no fim, escreve os rótulos de novo pela rotina aprovada da Casa E (`retoque_1pav_casae.rotulos_ambientes`), com os ajustes desta rodada (`AJUSTES_E`).

### Subsolo (28/10/26)

Lista aplicada:
1. **E11, pisos** nas texturas e escalas das Casas B a D (`F.piso_textura`, na resolução da prancha):
   - o vinílico da academia nas réguas do 1º Pavimento e das Casas B a D, no tom dele;
   - o granito do DCE e da casa de máquinas de baixo no granito de referência das Casas B a D (o do Térreo da Casa E, RGB ~116, 87, 68). Era o Marrom Tabaco escuro (~83, 59, 52) que vinha do render de 2000 px;
   - o Bege Bahia (circulação, depósito, casa de máquinas da direita e WC DCE 2) na foto da biblioteca, no tom das Casas B a D;
   - o travertino da sauna, do ambiente e do vestiário na foto da biblioteca, no tom do travertino do Térreo.
   As peças ficam as da final aprovada: as do PDF (móveis, louças, bancadas, marcenaria) e o que a final mostra com outra cor que não a do piso. As sombras e os reflexos antigos do render (o piso mais escuro ou mais claro, na mesma cor) saem com o piso velho, e cada peça ganha a sombra curta de novo. Os aparelhos da academia, que o PDF só traça (e o render pôs um pouco fora do traço), contam onde a final não mostra a cor do piso.
2. **E3, E8, escada da circulação**: sem as linhas e sem o triângulo. Os 17 degraus são em travertino, com o sombreamento de subida da direita para a esquerda (o sentido do triângulo aprovado em 20/10: "subindo da direita para esquerda, com a parte da direita viva"). O trecho depois do corte do PDF, à esquerda, fica nevoado, sem a linha de corte; no lugar dela, só uma sombra suave, como no Subsolo aprovado da Casa D. O S do PDF fica no 1º degrau, o da direita.
3. **E2, armário do DCE**: o retângulo com a diagonal junto à parede de baixo tem os cabides e o cabideiro (o guarda-roupa aberto dos closets), aberto para o quarto.
4. **E9, bancada do WC DCE 2**: a borda no tom escurecido da pedra e a sombra curta.
5. **E10, paredes** em cinza 80, no contorno do PDF; a franja preta antiga em volta foi refeita. Os 15 trechos do PDF que a final mostra claros ficam como estão (vidros, o fundo do poço do elevador). Não há pilares no Subsolo: os da EST - Pilar são do Térreo, fora da pegada.
6. **E7, rótulo do WC DCE 2**: sai da área do chuveiro para o meio do piso seco, entre a porta, a bancada e o vaso, no corpo 0,85 do PDF.

O resto fica como estava: boxes, louças, elevador, piscina, banco da sauna, portas e a hachura do lote. As alterações ficam só dentro da pegada do Subsolo (x 858 a 2082, y 303 a 1106 no quadro).

Rodado `python3 final3840_casae.py Subsolo`. Antes e depois: `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_2810_{planta,escada,dce_wc,academia,sauna_vestiario}_antes_depois.jpg`. Prancha `POE642_CasaE/entrega/POE642_CasaE_PH_Subsolo_entrega.png` e PDF `POE642_CasaE_Plantas_Humanizadas.pdf` refeitos.

### Térreo (28/10/26)

Lista aplicada:
1. **E11, granito** (cozinha, serviço, circulações, banho gourmet, DCE, garagem e a faixa de cima): o granito de referência das Casas B a D, na resolução da prancha. O tom já era o delas; o desenho vinha do render de 2000 px, largo e borrado. As projeções da DOC_LINHAS e os elementos fixos ficam por cima. O travertino, o Bege Bahia, a pedra portuguesa e a grama ficam como estavam: a auditoria só apontou as madeiras e o granito.
2. **E3, E8, escadas** sem as linhas e sem o triângulo:
   - **Circulação gourmet** (a mesma do Subsolo): o trecho vivo à esquerda, com o sombreamento de descida para a direita. O trecho depois do corte fica nevoado, sem a linha. O D do PDF vai no degrau de cima, à esquerda, onde estava o triângulo.
   - **Interna, do jardim**: sobe da direita para a esquerda. O S do PDF vai no 1º degrau, à direita; o trecho depois do corte, à esquerda, fica nevoado.
   - **Degraus em blocos à direita do deck**: os quatro blocos do PDF (ARQ_CONTRAPISO) em Bege Bahia, sem o contorno. Cada um é um pouco mais escuro que o de cima e recebe a sombra curta dele, descendo da direita para a esquerda (o sentido aprovado em 20/10). O D vai no bloco de cima. Na planta, o bloco de cima cobre o de baixo; antes, a final mostrava só os contornos sobrepostos dos quatro.
3. **E2, armário do DCE**: o retângulo com a diagonal junto à parede da esquerda tem os cabides e o cabideiro, aberto para o quarto.
4. **E5, box do WC DCE 1**: as duas folhas de correr do PDF em vidro contínuo, com as faces finas, a sombra curta e o trilho no vão (antes, uma linha fraca).
5. **E9, bancadas**: a do banho gourmet (granito sobre o granito do piso), a do WC DCE 1 e a do lavabo têm a borda no tom escurecido da pedra e a sombra curta.
6. **E10, paredes e muros** em cinza 80: os da ARQ_PAREDE e os da ARQ_ELEMENTOS FIXOS, entre eles o muro junto ao lavabo e as linhas do lote em cima e embaixo. Os brises de madeira ficam. Os pilares redondos da varanda seguem pretos.
7. **E4, seta da entrada principal**: cheia, preta, de 1,5 m, no Bege Bahia de fora, com a ponta junto à porta pivotante do HALL DE ENTRADA, apontando para ela.
8. **E7, rótulo do WC DCE 1**: sai da área do chuveiro para o meio do piso seco, entre o box, o vaso, a bancada e a folha da porta, no corpo 0,85.

Rodado `python3 final3840_casae.py Terreo`. Antes e depois: `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_{planta,escada_gourmet,escada_interna,degraus_deck,dce_wc,banho_gourmet,lavabo_hall,cozinha_gourmet,garagem}_antes_depois.jpg`. Prancha `POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_entrega.png` e PDF refeitos.

Hachura do Subsolo: o lote vem do Térreo final. Recalculado com o Térreo novo, ele muda só 23 px, no canto de baixo à esquerda do lote: as linhas do lote ficaram cinza. Na final do Subsolo, esses px ficam sob a linha do lote da base, então ela não muda.

### 1º Pavimento (28/10/26)

Lista aplicada:
1. **Térreo nublado em volta**, refeito a partir do Térreo novo desta rodada (paredes em cinza 80, granito, escadas), sem as letras das escadas, a seta e os rótulos. É o mesmo nublado de antes: 70% de branco, 80% da saturação, desfoque leve. Só muda onde a final mostra o Térreo: fora da pegada do 1º Pavimento e nos vazios, onde o X e o vidro ficam por cima. Antes, o nublado vinha do retocado de 2000 px do Térreo, com o triângulo da escada gourmet e as paredes pretas. O nublado anterior foi conferido contra a final aprovada (diferença máxima de 1,6, só arredondamento) antes da troca.
2. **E11, vinílico** (suítes, closets, circulação, sala íntima) nas réguas das Casas B a D, na resolução da prancha. Vinha do retocado de 2000 px, ampliado. As peças ficam as da final, com a borda delas. A mesinha redonda de madeira ao lado do sofá da sala íntima, que o PDF não desenha e tem a cor do vinílico, fica protegida (`FICAM_1PAV_E`).
3. **E3, E8, escada interna**: sem as linhas e sem o triângulo. O trecho do 1º Pavimento, à esquerda, tem o sombreamento de descida para a direita. Os degraus depois do corte, que são do Térreo, à direita, ficam nevoados. O D do PDF vai no degrau de cima, à esquerda, onde estava o triângulo.
4. **E9, bancadas** dos banhos master, 1, 2, 3 e 4 (claras sobre o porcelanato claro): a borda no tom escurecido da pedra e a sombra curta.
5. **E10, paredes** em cinza 80. Não há pilares no 1º Pavimento.

O resto fica como estava: rótulos, cortinas franzidas de 27/10, camas, guarda-roupas com cabides, boxes, quartzito Aura dos banhos e Bege Bahia das varandas.

Rodado `python3 final3840_casae.py 1Pavimento`. Antes e depois: `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_{planta,escada,banhos_3_4,banho_master,banhos_1_2,suites,sala_intima,nublado}_antes_depois.jpg`. Prancha `POE642_CasaE/entrega/POE642_CasaE_PH_1Pavimento_entrega.png` e PDF `POE642_CasaE_Plantas_Humanizadas.pdf` (Subsolo, Térreo e 1º Pavimento) refeitos.

Sobre o Subsolo depois do 1º Pavimento: o motor ganhou ajustes durante o Térreo e o 1º Pavimento:
- a proteção das linhas de projeção;
- o ARQ_ELEMENTOS FIXOS nas paredes;
- a borda de 2 px das peças;
- os círculos `FICAM`.

Rodar `python3 final3840_casae.py Subsolo` hoje dá uma variante quase igual à final entregue (commit 87f558e). Mudam o grão do granito na Casa de Máquinas e no DCE, e um anel de 2 px em volta das esteiras e dos aparelhos da academia, sem ganho visível. A final do Subsolo fica a de 87f558e.

### Subsolo, pedidos de 28/10/26 vendo a final

O usuário, sobre a final do Subsolo:
- "MELHORE A REPRESENTAÇÃO DOS APARELHOS DE ACADEMIA E O CONTORNO DO PISO EM VOLTA DESSES APARELHOS";
- "MELHORE O ASPECTO DO MARMORE TRAVERTINO";
- "AS BORDAS EXISTENTES DA PISCINA SÃO EM MARMORE BEGE BAHIA. ESSA BORDA É QUASE IMPERCEPTÍVEL NA VISTA";
- "VESTIARIO: PISO EM MARMORE TRAVERTINO BRUTO, CUBA ESCUPLIDA EM MARMORE TRAVERTINO BRUTO, PEDRA DA PIA EM MAGRANITO MARROM TABACO ESCOVADO, VASO SANITÁRIO EM BRANCO E METAIS CROMADOS";
- "VAMOS REVISAR E AJUSTAR REPRESENTAÇÃO DAS PORTAS";
- com a vista de cima da sauna no modelo 3D: "TEM UM DEGRAU NO MESMO NIVEL DO PISO DA SAUNA E VAI ATÉ A BORDA DO VIDRO, FORMANDO UM BANCO DENTRO DA PISCINA, MAS AINDA DENTRO DO AMBIENTE DA SAUNA. NOTE TAMBÉM O TOM DA PISCINA QUE ADOTAREMOS"; "OS DEGRAUS EM FORMA DE BANCO NO MARMORE TRAVERTINO DENTRO DA SAUNA TEM DENTES APARENTES PARA DIZER QUAL DEGRAU ESTÁ ACIMA E OUTRO ABAIXO".

O que foi feito (`final3840_casae.py`, novas etapas do Subsolo):
1. **Aparelhos da academia** (`aparelhos_e`), redesenhados pelo PDF na resolução da prancha. Eram os do render: borrados, serrilhados, um pouco fora do PDF e com lascas escuras no vinílico em volta.
   - São 11 blocos: os elípticos, as esteiras, as bolas de pilates com os acessórios, a barra de parede, a estação de musculação, a prateleira junto ao DCE, o suporte de halteres, o supino com a barra e o banco regulável.
   - Cada peça do PDF vai num material, pela forma e pelo aparelho: estrutura grafite, tubos, estofado preto, borracha, cromado (a barra do supino, os pegadores dos halteres, a barra de parede), o alumínio das laterais da esteira, a lona e o painel.
   - As peças têm o volume do material, os traços do PDF por cima, finos, e as bolas vão como esferas.
   - Embaixo e em volta de cada aparelho (0,45 m), o vinílico novo passa inteiro e entra a sombra curta e macia.
2. **Travertino** (`TRAVERTINO_E`, `travertino_e`): o travertino bruto em estratos das Casas C e D, com os veios marcados e os poros abertos, sem o tom rosado, no creme claro da referência.
   - Os veios correm na vertical, como na sauna da referência.
   - Vale nos pisos da sauna, do ambiente e do vestiário, nos degraus da escada da circulação, nos bancos da sauna e no degrau da piscina.
3. **Piscina** (`piscina_e`):
   - A água fica no turquesa da referência: as peças de 14,5 cm do Barlavento, com o contraste das pastilhas, a variação do fundo e as cáusticas.
   - As bordas, os brancos da ARQ_PAREDE em volta da água, vão em Bege Bahia com a quina e a sombra curta na água. Antes eram um bege pálido; a faixa entre as duas partes da piscina ia como água.
   - Dentro da sauna, a faixa de cima da piscina interna, do vidro até a sauna, e a da beira junto ao piso são o degrau no nível do piso, em travertino. É o banco dentro da piscina, ainda no ambiente da sauna.
   - Os vidros finos foram redesenhados por cima.
4. **Sauna** (`sauna_e`): os dois bancos do PDF em degrau, no travertino do piso, com o veio deitado e o de cima mais claro.
   - Os dentes: a quina clara do degrau de cima, o fio do espelho e a sombra curta no nível de baixo.
   - Nas pontas, junto ao degrau da piscina, a sombra de cada banco, mais longa no mais alto.
5. **Vestiário** (`vestiario_e`):
   - o piso em travertino bruto;
   - a bancada do PDF em granito Marrom Tabaco escovado: o granito de referência calmo e fosco, no tom do Marrom Tabaco (RGB ~88, 64, 50), com o risco fino do escovado, a borda e a sombra;
   - a cuba esculpida em travertino bruto, mais clara;
   - a torneira cromada saindo da parede;
   - o vaso em louça branca;
   - o chuveiro de teto com o braço e a canopla cromados.
6. **Portas** (`portas_e`; R3 e seção 4 das regras):
   - As 10 portas de giro vinham como tubos cinza do render, sem batentes; a do DCE tinha um "L" a mais e a da sauna estava quase sumida. Agora levam a folha na posição e na espessura do PDF, em branco com o contorno fino e a sombra curta, e os batentes. Antes disso, o piso novo passa inteiro no quadrante de cada porta.
   - As 7 soleiras dos vãos brancos são de Bege Bahia. No WC DCE 2 havia uma faixa marrom no lugar.
   - As duas portas de vidro de correr da circulação para a academia e a janela de correr do DCE seguem a Casa D: as duas folhas nos planos do PDF, sobre a soleira de Bege Bahia, com os batentes.
   - A porta e o vidro fixo da ducha do ambiente vão em vidro fino.
   - As paredes das cabines do vestiário (a ARQ - Parede do PDF, que a E10 não pegava) vão em cinza 80.

Ordem das etapas: pisos, escada, armário, bancada, piscina, sauna, paredes, vestiário, aparelhos, portas, rótulos. Antes e depois (o antes é a final de 87f558e): `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_pedidos2810_{planta,academia,piscina_sauna,sauna_degraus,vestiario,portas_dce_wc_deposito,portas_academia,porta_casa_maquinas,travertino_escada}_antes_depois.jpg`. Prancha e PDF refeitos.

Pendente nesta altura (resolvido logo abaixo): o Térreo da Casa E seguia com o Barlavento sob a água verde-azulada clara de antes.

### Pedidos de 28/10/26, 2ª rodada: o tom da piscina em todas as casas, paredes, divisória, chuveiro e rótulo

O usuário, vendo a final do Subsolo:
- "APLIQUE O TOM DA PISCINA NO TÉRREO TAMBÉM" e "APLIQUE ESSE TOM DE PISCINA EM TODAS AS PISCINAS DE TODAS AS CASAS";
- com o recorte do rótulo da casa de máquinas da direita: "CENTRALIZE O RÓTULO PARA NÃO ENCOSTAR NAS BORDAS";
- com o recorte da ducha do ambiente: "MELHORE A REPRESENTAÇÃO DO CHUVEIRO, AO LADO DA SAUNA";
- com o recorte dos tocos de parede entre o ambiente e a casa de máquinas: "CORRIJA A REPRESENTAÇÃO DAS PAREDES";
- com o recorte da faixa entre a piscina e a parte de baixo: "REMOVA ESSA DIVISÓRIA DA PISCINA";
- com o recorte da parede junto ao vidro da piscina: "CORRIJA ESSA IMPERFEIÇÃO NA PAREDE. NÃO ESSE DENTE".

O que foi feito:
1. **O tom da piscina em todas as casas** (`piscinas_turquesa.py`, novo): a água dos Térreos no turquesa do Subsolo da Casa E, com as pastilhas do Barlavento, a rede das cáusticas e a sombra curta das beiras.
   - As piscinas dos Térreos das Casas A a D vêm dos renders de 2000 px. Por isso o script troca só a água nas finais já aprovadas, sem rodar os motores, como as cortinas (`cortinas_franzidas.py`). Cada final é regravada no lugar: `python3 piscinas_turquesa.py A-Terreo` (e `B-`, `C-`, `D-Terreo`).
   - O desenho da água antiga fica, com mais contraste: as peças e o rejunte, os degraus da prainha e do spa, a sombra das bordas.
   - A água vai até a beira quente (o Bege Bahia, a madeira). Por isso a faixa clara que o render deixou junto às bordas da prainha da Casa D entra.
   - Ficam como estão as espreguiçadeiras (Casa B), os tracejados de projeção (Casa A) e os rótulos. Cada px de traço escuro é separado da água antiga e posto sobre a nova, então os rótulos não ganham halo.
   - No Térreo da Casa E é a etapa nova "piscina" do motor (`piscina_terreo_e`, antes dos rótulos), com as duas folhas de vidro do lado esquerdo protegidas. Ela entra também no Térreo esmaecido do 1º Pavimento (`terreo_para_nublado`), que foi refeito.
   - Áreas de água: A 36,5 e 8,9 m²; B 35,3 e 9,3; C 32,2 e 7,9; D 36,9 e 6,4; E 22,3, 1,3 e 6,7 (piscina e prainha, a faixa entre os vidros, spa).
2. **Paredes** (`paredes_e`, vale para os três pavimentos da Casa E):
   - As peças do PDF entram numa máscara só, desenhada em 4x e reduzida uma vez. Antes, cada peça vinha com o próprio antialias, e a junta de duas peças vizinhas deixava ver o fundo: fios claros e escuros nos encontros dos tocos, nas diagonais das pontas e na parede de baixo da piscina.
   - A franja escura do render que passava do contorno (até 3 px, escura e com pouca cor) é refeita pelo piso em volta.
   - As cabines do vestiário (ARQ - Parede) entram na mesma máscara.
3. **O dente** (`PAREDES_E["coberta"]`): embaixo da parede da academia, junto ao vidro da piscina, havia duas pecinhas escuras de 1,7 pt que o PDF cobre com um branco desenhado depois. Agora sai a peça escura coberta por um branco da mesma camada que a final já mostra clara.
   - A faixa branca embaixo da piscina, que a final mostra como parede, fica.
4. **A divisória da piscina** (`PISCINA_E["agua_extra"]`): a faixa de Bege Bahia entre a piscina e a parte de baixo, à esquerda do vidro, vira água contínua. O degrau da sauna, à direita do vidro, fica.
5. **O chuveiro da ducha do ambiente** (`DUCHA_AMBIENTE_E`, `nicho_ducha`):
   - O do PDF, como o do vestiário: a placa quadrada cromada com os furinhos, o braço descendo até a parede e a canopla.
   - O cálice do render saiu, com o piso de travertino inteiro em volta.
   - O nicho da parede atrás dele, que o render pintou como uma grelha escura, vai em travertino com a sombra curta do recuo.
6. **O rótulo da casa de máquinas da direita (5,83 m²)** (`AJUSTES_E["Subsolo"]`): passou ao corpo 0,85, no centro do cômodo, entre as paredes e da soleira à parede de baixo. No corpo 1,0 o nome ia de parede a parede.

Antes e depois (o antes é a final de 17c2f1b):
- `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_pedidos2810b_{planta,piscina_divisoria_parede,chuveiro_paredes,rotulo_casa_maquinas}_antes_depois.jpg`;
- `POE642_Casa{A,B,C,D,E}/renders/POE642_Casa*_PH_Terreo_piscina_turquesa_antes_depois.jpg`;
- `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_piscina_turquesa_antes_depois.jpg`.

Pranchas e PDFs das cinco casas refeitos. Os Subsolos das Casas B a D, que usam o Térreo final no terreno hachurado, não foram rodados de novo: lá a piscina não aparece.

Segue em aberto, de outra casa: as banquetas do Térreo da Casa C (`BANQUETAS_C["giro"]` 270 → 90, sem mexer sem o OK).

### Pedidos de 28/10/26, 3ª rodada: rótulo do elevador, falhas das paredes, o dente e a quina das bordas

O usuário, vendo a prancha do Subsolo:
- com o recorte da cabine: "CENTRALIZE O RÓTULO" (o ELEVADOR);
- com o recorte da parede embaixo da piscina: "CORRIJA O ACABAMENTO DAS PAREDES, SEM FALHAS";
- "NÃO EXISTE ESSE DENTE NA PAREDE. ELA É RETA";
- com o recorte do encontro da coluna de Bege Bahia com o degrau da sauna, no vidro: "JUNTE AS BORDAS, FORMANDO APENAS UMA QUINA".

O que foi feito (`final3840_casae.py`):
1. **Rótulo do elevador** (`AJUSTES_E["Subsolo"]`): no centro da cabine, no corpo do PDF. No ponto do PDF e no corpo 1,3 ele ia à direita e encostava no contorno da cabine.
   - A borda direita da cabine, que o "R" do rótulo antigo cobria e a retirada dos rótulos deixou borrada, foi refeita pelas linhas de cima (etapa nova `elevador`, `cabine_elevador_e`).
2. **O dente**: a pecinha de 1,7 pt sob a ponta da parede da academia, junto ao vidro, já não era pintada de cinza, mas o escuro do render ficava embaixo.
   - Agora a borda e o degrau da piscina passam por cima dela (`PISCINA_E["dentes"]`), e a parede fica reta.
   - A regra das peças cobertas por um branco do PDF passou a valer só para pecinhas (`coberta_max_pt2`, 10 pt²) que a final já mostra claras. Na rodada anterior ela também tirava a ponta da parede no canto de baixo à esquerda da piscina e deixava uma faixa clara entre a parede e a água; essa faixa voltou a ser parede.
3. **Falhas das paredes**:
   - Na caixa da piscina (`sempre=[PISCINA_E["caixa_pt"]]`), toda peça escura do PDF entra, mesmo onde o render pintou água por cima: o entalhe no canto do degrau da parede de baixo fechou.
   - O fundo do antialias das paredes vem do piso de fora (antes vinha do preto antigo de dentro e deixava a borda irregular).
   - A borda da bancada do vestiário e o vaso não pintam mais a face da parede.
   - Conferido px a px com o PDF (as paredes da final contra as do PDF): o que sobra são só os encontros de propósito (as folhas das portas e os batentes sobre a face da parede).
4. **A quina das bordas** (`PISCINA_E`): a coluna de Bege Bahia à direita da piscina desce até o fundo do degrau da sauna e encontra o degrau no vidro, numa quina só. Na rodada anterior, ao tirar a divisória, a água tinha entrado também sob a coluna; agora a água sem divisória vai só entre as duas partes da piscina, até a coluna.

Antes e depois (o antes é a final de 3041093): `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_pedidos2810c_{planta,quina_bordas_dente,piscina_paredes,rotulo_elevador}_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa E refeitos.

### Pedidos de 28/10/26, 4ª rodada: o toco do ambiente e a parede da sauna, retos

O usuário, vendo a prancha do Subsolo:
- com o recorte do toco entre a ducha e o ambiente: "A PAREDE AQUI NÃO ESTÁ PERFEITA. PRECISO DELA RETA E SEM DENTE";
- "ESSA PAREDE DA SAUNA TEM UM DENTE TAMBÉM QUE PRECISA DE CORREÇÃO" e "é uma imperfeição no meio da parede".

As causas e o que foi feito (`final3840_casae.py`):
1. **A sobra da parede antiga**: o render desenhava as paredes ~1 px mais largas que o preenchimento do PDF e com um chapéu claro nas pontas. A limpeza da franja só pegava o preto puro, e essa sobra cinza ficava em volta das paredes novas, como um contorno irregular.
   - Agora `paredes_e(..., ini=)` tira a sobra: os px a até 3 px da parede que nenhuma etapa redesenhou desde a final aprovada e que são mais escuros que o piso claro de perto (`PAREDES_E["sobra"]`, 0,88). Eles são refeitos pelo piso.
2. **As faixas de revestimento das faces** (`PAREDES_SUB_E`): os preenchimentos escuros da ARQ_REVESTIMENTOS (0,57 pt), que o PDF desenha como parte da parede, entram na máscara. Sem elas, o topo do toco saía em degrau e as paredes mais finas que o desenho.
3. **A ponta da parede da sauna junto à porta**: o dente de 1,4 pt (o encaixe do batente) sai (`tirar`), e a face de baixo segue reta até a porta (`por`).
4. **No meio da parede da sauna**:
   - O tique escuro onde o degrau da piscina encontra o piso da sauna fechou: o degrau vai 1,1 pt além.
   - O fio ciano na emenda das duas partes do degrau sumiu. `_uniao` agora junta os retângulos numa máscara só, sem a junta a 50%.

Antes e depois (o antes é a final de 50a24e1): `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_pedidos2810d_{planta,toco_ambiente,parede_sauna}_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa E refeitos.

### Pedidos de 28/10/26, 5ª rodada: a porta da cabine do chuveiro do vestiário

O usuário, com o recorte da cabine do chuveiro do vestiário: "represente melhor a porta desse ambiente de chuveiro". Depois, vendo as tentativas: "pode fazer aberta mesmo" e "no mesmo padrão que adotamos para as demais".

- **Antes:** a folha branca de giro, aberta contra a divisória, colava no traço escuro dela e não se lia como porta.
- **Tentativas descartadas:**
  - o vidro no centro da folha do PDF: some junto à divisória;
  - o vidro fechado no vão, sobre a soleira, com a dobradiça e o puxador cromados: o usuário preferiu a porta aberta, sem ferragens a mais.
- **Agora** (`final3840_casae.PORTAS_E["vidros"]`):
  - a porta sai das folhas de giro e entra nos vidros: aberta, como no PDF, no padrão da porta da ducha do ambiente (o vidro fino com as faces e a sombra curta, sem arco);
  - os batentes brancos na soleira (o 5º elemento do item, `{"batentes": [...]}`);
  - o vidro fica na metade de fora da folha do PDF, com um fio de piso entre ele e a divisória;
  - o quadrante da folha (`arco`) continua nas `zonas_portas`, e o piso passa limpo onde estava a folha branca.

Antes e depois (o antes é a final de 4124497): `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_pedidos2810e_{planta,porta_cabine_chuveiro}_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa E refeitos.

### Pedido de 28/10/26: as bordas da piscina da Casa A, perfeitas

O usuário, com o recorte da piscina do Térreo da Casa A (piscina, prainha e spa) no tom novo: "casa A -terreo: corrija as bordas deixando as perfeitas".

- **O que havia:**
  - a água do render de 2000 px passava até 3 px do desenho do PDF, com a beira ondulada, pingos ciano fora dela, cantos arredondados e um fio claro em volta;
  - no topo do spa, a beira dobrada (uma lasca de água acima do traço escuro);
  - as faixas de pedra entre o deck e a piscina e em volta do spa variavam de largura, com uma franja ciano por dentro, e o deck de madeira invadia o anel do spa.
- **O que foi feito** (`piscinas_turquesa.py --bordas`, `BORDAS["A-Terreo"]`):
  - a água exatamente nos retângulos do PDF (ARQ_CONTRAPISO, o preenchimento azul), com a beira nítida;
  - junto à beira, o fundo refeito pelo espelho da água de dentro, a mesma rede de cáusticas do turquesa, contínua e sumindo junto à beira (refeita da final de antes do turquesa), e a sombra curta da água de referência (`PISCINA_E["sombra"]`);
  - as faixas de pedra do PDF (907,2 a 918,5 pt entre o deck e a piscina; o anel de 11,4 pt do spa) com largura constante, na pedra clara do render, lisa;
  - fora, o piso espelhado sobre a água que passava e o fio claro, com o alcance medido em cada lado; os tracejados de projeção por cima.

Antes e depois (o antes é a final de a680667): `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_bordas_piscina_antes_depois.jpg` e `..._bordas_piscina_spa_detalhe_antes_depois.jpg`. Prancha do Térreo e PDF da Casa A refeitos.

### Pedidos de 28/10/26 no Térreo da Casa A: o box do banho varanda e os resquícios do Bege Bahia

O usuário, vendo a prancha do Térreo da Casa A:
- "na casa A terreo: faltou o box do banho varanda. incluir.";
- com o recorte da placa de pedra da ponta direita do caminho: "na casa A terrea - limpe esses resquicios";
- com o recorte da borda de cima do Bege Bahia junto à grama, perto da projeção tracejada: "Casa A - terreo: corrija o contorno do marmore bege bahia, removendo esses resquicios".

O que foi feito (`final3840_casaa_terreo.py`, duas etapas novas no fim de `passos_terreo`, aplicadas sobre a final atual com `--so`, porque a final já tem o turquesa e as bordas da piscina):
- **`box_varanda`:** o box de correr do PDF (horizontal, a 1712,8 pt, entre o vaso e o chuveiro), de que o render só deixou um traço azul fraco. Usa `final3840_casaa.boxes`, que ganhou o filtro `so=`: as duas folhas de vidro contínuas, desencontradas, com as faces finas e a sombra curta, e o trilho no vão até a parede (seção 6 das regras).
- **`limpeza_2810`:**
  - na borda de cima do Bege Bahia (x 1083 a 1512, linha 340), três pecinhas cinza-rosadas que avançavam sobre a grama (em x ~1401, ~1466 e ~1489-1506) foram refeitas com a borda e a grama de uma coluna limpa ao lado; o tracejado branco da projeção que cruza a borda ficou;
  - na placa da ponta direita do caminho: a faixa rosada fora do lote (x 3430 a 3442) no branco da prancha, o tufo de folhas sobre a borda de cima e o risco claro na grama entre as placas.

Antes e depois (o antes é a final de a7dbda8): `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_2810_{box_banho_varanda,contorno_bege_bahia,placa_pedra}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa A refeitos.

Notado e não alterado (aguarda o OK): na borda de baixo da varanda (travertino) junto à grama, entre x ~1253 e ~1459, há tiquinhos claros parecidos. (Corrigido depois, a pedido; ver a seção da borda da varanda.)

### Pedido de 28/10/26: as bordas das piscinas das outras casas

O usuário, depois das bordas da Casa A: "aplique nas bordas das outras casas também".

`piscinas_turquesa.bordas_retas` passou a aceitar corpos d'água de vários retângulos (a união: a piscina com a prainha, o L da Casa B) e px protegidos; `BORDAS` ganhou os Térreos das Casas B a E (pt do PDF, os preenchimentos azuis da ARQ_CONTRAPISO). O que havia e o que ficou, casa a casa:
- **Casa B** (1295 px de água fora do PDF a até 8 px da beira, e o fio cinza antigo na quina da prainha): as beiras retas. A faixa de 17 pt à esquerda do braço da piscina, contornada no PDF mas sem o azul, é água na base da legenda aprovada (a mesma cor do braço) e na final: entrou no corpo e continua água.
- **Casa C** (614 px fora): as beiras retas; o muro fino (ARQ_PAREDE) ao lado esquerdo da piscina ficou, protegido.
- **Casa D** (a parede fina da piscina, 3,1 pt da ARQ_PAREDE colada na água, virou no render um contorno cinza-azulado borrado em volta da água): sem proteção; a água encontra a borda de pedra direto, com a beira reta, como nas outras casas.
- **Casa E** (1452 px fora, um fio cinza no topo da água, cantos arredondados): as bordas na etapa `piscina` do motor, logo depois do turquesa, com a mesma rede das cáusticas (`semente` 2851) e os vidros da lateral protegidos; o Térreo foi refeito de `--de piscina`, e o 1º Pavimento de novo (o Térreo esmaecido vem do Térreo).

Antes e depois (o antes é a final de b39850f): `POE642_Casa{B,C,D,E}/renders/POE642_Casa*_PH_Terreo_bordas_piscina_antes_depois.jpg` e `..._detalhe_antes_depois.jpg`. Pranchas do Térreo e PDFs das Casas B a E refeitos (e a do 1º Pavimento da Casa E).

### Pedido de 28/10/26: a borda de baixo da varanda da Casa A

O usuário: "pode corrigir a borda de baixo da varanda também" (o que eu tinha notado junto ao contorno do Bege Bahia).

O que havia: entre o pilar preto da varanda e a parede do WC, a beira do travertino contra a grama era uma faixa cinza-rosada de 2 a 4 px, com entalhes em V a cada ~20 px, trechos mais altos (dentes) e riscos escuros soltos (o maior junto à parede).

O que foi feito: a etapa nova `varanda_baixo` em `final3840_casaa_terreo.py` (`VARANDA_BAIXO`, aplicada com `--so varanda_baixo` sobre a final atual). De x 1251 a 1476, a beira fica reta na linha do PDF (o fim do piso da varanda, 1786,5 pt = 1643 px): a cada coluna, as 6 linhas de cima recebem o travertino espelhado de logo acima, as 6 de baixo a grama espelhada de logo abaixo, e a linha da beira o meio-termo do antialias. O pilar, a parede e o tracejado branco da projeção não mudam (2878 px alterados, todos entre y 1637 e 1649).

Antes e depois (o antes é a final de c28fa80): `POE642_CasaA/renders/POE642_CasaA_PH_Terreo_2810_borda_varanda_antes_depois.jpg`. Prancha do Térreo e PDF da Casa A refeitos.

### OK de 28/10/26: as banquetas da ilha da Casa C

O usuário: "pode girar as banquetas da casa C" (o achado que aguardava o OK desde o 4º lote da Casa D).

O que foi feito: `BANQUETAS_C["giro"]` de 270 para 90 em `final3840_casac.py`. Na folha da `banqueta_linho`, a frente do assento fica em cima; com 90 ela vai para a direita, para a ilha, com o encosto à vista e a frente sob o tampo, como nas Casas A, B, D e E. O Térreo foi refeito de `--de biblioteca`; o cache das etapas era o mesmo da final antes do turquesa (idêntico ao do git). Por cima, o turquesa e as bordas de novo:
- `piscinas_turquesa.py C-Terreo`;
- `--bordas --rede` com a saída do motor.

Conferido contra a final de antes: mudaram só as 4 banquetas (2104 px; nada na piscina). O Subsolo da Casa C não muda, porque ali a cozinha está sob a hachura branca.

Antes e depois: `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_2810_banquetas_antes_depois.jpg`. Prancha do Térreo e PDF da Casa C refeitos.

### Pedidos de 28/10/26: os vidros da borda das piscinas das Casas B e E como o da Casa C

O usuário, com os recortes da borda da Casa C (a grama, o vidro e a água) e do braço da piscina da Casa B (o deck e a água):
- "faça a representação do vidro borda da piscina da casa B igual ao da Casa C. Na verdade, na casa B são dois vidros na borda.";
- "faça o mesmo na piscina da casa E, com duas bordas em vidro."

O vidro da Casa C é o do render: a lâmina da ARQ_PAREDE de 0,6 + 5,1 pt à esquerda da piscina, que o turquesa deixou como uma lâmina fina. Medido na final (mediana de 135 linhas), de fora para a água:
- um fio claro;
- 3 px de turquesa escuro;
- 2 px de fio escuro;
- 1 px de passagem clara.

`piscinas_turquesa.vidros_borda` desenha esse perfil (`VIDRO`) nos vidros de `VIDROS_BORDA`:
- **Casa B:** no PDF, a faixa de 17 pt entre o deck e o braço da piscina é branca, contornada e sem divisões; até aqui ia como água. Os dois vidros pedidos entram na largura do da Casa C (5,7 pt): um junto ao deck e outro junto ao braço, com a água entre eles (como a faixa entre os vidros da Casa E), do fim da pedra de cima ao bloco de pedra de baixo. Aplicado sobre a final (`--vidros`).
- **Casa E:** as duas lâminas do PDF (1,7 + 5,1 + 1,7 pt) do lado esquerdo da piscina, que estavam em cinza metálico, passam ao desenho da Casa C. Os fios ficam na largura dos da Casa C, e o corpo turquesa estica até os 9 px do PDF. As pontas cinza do vidro antigo, que avançavam até 3 px sobre o Bege Bahia de cima e de baixo, saíram (a pedra espelhada na mesma coluna). Feito na etapa `piscina` do motor; o Térreo foi refeito de `--de piscina` e o 1º Pavimento de novo (o Térreo esmaecido).

Antes e depois (o antes é a final de 3cfa560):
- `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_vidros_borda_{,detalhe_}antes_depois.jpg`;
- `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_vidros_borda_{,detalhe_}antes_depois.jpg`;
- `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_vidros_borda_antes_depois.jpg`.

Pranchas e PDFs das Casas B e E refeitos (na Casa E, o Térreo e o 1º Pavimento).

Escolha a confirmar com o usuário: na Casa B, os dois vidros ficaram nas duas beiras da faixa, com a água entre eles. A alternativa seria os dois vidros juntos. Resposta: "pode deixar os vidros da casa B como estão".

### Pedidos de 28/10/26: cadeiras da Casa D, cortinas e varanda da Casa E, poltronas da Casa C

O usuário, vendo as pranchas:
- com o recorte da mesa de jantar do living da Casa D: "AS CADEIRAS DA MESA ESTÃO INVERTIDAS? CONTINUE";
- "NO TERREO DA CASA E, VAMOS ALTERAR O MODELO DAS CORTINAS PARA A QUE ADOTAMOS COMO PADRÃO";
- com um recorte da varanda grande do 1º Pavimento da Casa E: "CORRIJA ESSES RESQUICIOS NO PISO, RENTE AO GUARDA CORPO DA VARANDA DO 1º PAV DA CASA E. NOTE QUE TEM UNS TRAÇOS QUE NÃO FAZEM PARTE DA IMAGEM. ESSES TRACÇOS APARECEM NA VERTICAL E NA HORIZONTAL ABAIXO DO VASO";
- com três recortes das poltronas dos quartos da Casa C: "NO TERREO DA CASA C, ALTERE AS POLTRONAS E MESAS LATERAIS PARA O NOVO MODELO QUE ADOTAMOS";
- com o recorte das cortinas dos quartos da Casa D: "ESSE É O MODELO DE CORTINA A SER ADOTADO EM TODAS AS CASAS".

O que foi feito:

**Casa D, cadeiras da mesa de jantar.** Estavam invertidas, com o encosto curvo virado para a mesa. No recorte da `mesa_jantar_10` (a cadeira de cima da foto), a frente fica embaixo; o giro de `jantar_d` supunha o contrário. Agora a cadeira de cima fica como está, a de baixo gira 180° e as dos lados giram 90° para a mesa. Refeito de `--de moveis`; por cima, o turquesa e as bordas de novo. Só as 10 cadeiras mudaram.

**Casa E Térreo, cortinas.** O modelo já era o pano franzido de 27/10, o mesmo do recorte da Casa D; os motores das cinco casas o usam (`blocos.cortina` fechada). No travertino claro, porém, o linho quase sumia e o pano se lia como a linha em zigue-zague antiga. Na janela de baixo do living, a corda do render entre o trilho e a primeira folha de vidro ainda estava lá. Nova etapa `cortinas` no motor (`CORTINAS_TER_E`):
- a corda sai;
- os 5 panos voltam no mesmo eixo, com o linho um pouco mais fechado, o contorno do tecido e a sombra curta mais marcados.

O 1º Pavimento foi refeito (o Térreo esmaecido).

**Casa E 1º Pavimento, varanda grande.** Nova etapa `varanda` (`VARANDA_1PAV_E`):
- a linha dupla do render (um fio claro e um escuro) logo depois do guarda-corpo da esquerda, em vários trechos, sai com o piso espelhado;
- no canto de baixo, o piso do render em volta dos vasos (mais claro e liso, em quadrados) e o L escuro da base quadrada do vaso de baixo vêm do Bege Bahia de cima, com as emendas esfumadas;
- os vasos e a planta ficam, com a sombra curta.

No canto de cima, em volta da outra planta, só a linha saiu: refazer o piso deixava a borda clara da planta como contorno.

**Casa C Térreo, poltronas e mesas laterais.** Nova etapa `moveis` (`MOVEIS_TC`), com o estofado e a madeira da Casa D (`final3840_casad.estofado_d`, `madeira_d`):
- a poltrona, o pufe e a mesa lateral da suíte master 1 e do quarto 1;
- a poltrona e a mesa lateral da sala TV (a outra mesa do PDF, junto ao sofá, não aparece na final e não entra);
- as 2 poltronas do estar.

Refeito de `--de moveis`; por cima, o turquesa e as bordas.

Antes e depois:
- `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_2810_cadeiras_jantar_antes_depois.jpg`;
- `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_cortinas_{living,detalhe,escritorio}_antes_depois.jpg`;
- `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_varanda_{guarda_corpo,inteira}_antes_depois.jpg`;
- `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_2810_{poltrona_suite_master,poltrona_quarto1,poltrona_sala_tv,poltronas_estar}_antes_depois.jpg`.

Pranchas e PDFs das Casas C, D e E refeitos.

### Pedido de 28/10/26: boxes dos chuveiros fechados, sem tracejado (todas as casas)

O usuário, com o recorte da faixa de cima do Térreo da Casa C (VARANDA, BH 2, BH 1): "MELHORE A REPRESENTAÇÃO DOS BOX DOS CHUVEIROS COM FOLHA CONTÍNUA, SEM TRACEJADO. REVEJA TODOS OS BOX DE TODOS OS AMBIENTES".

Revisão das 12 plantas (todos os boxes que o PDF desenha, nas finais):
- **Com tracejado:** os boxes de correr das Casas A, C, D e E. A mesma rotina (`final3840_casaa.boxes`) desenhava as duas folhas do PDF e o trilho tracejado no vão de passagem, e o tracejado do render ficava por baixo.
- **Incompleto:** o box do banho gourmet da Casa E (Térreo), que não chegava à parede de cima.
- **Já contínuos, sem tracejado, e ficam:** os da Casa B; os vidros fixos e as portas de vidro dos BH master da Casa C; os boxes no granito (BH serviço e BH externo da Casa C, banho gourmet da Casa D); o Subsolo e o 1º Pavimento da Casa E.

O que foi feito: o box de correr vai fechado. As duas folhas de vidro, desencontradas, cobrem o vão inteiro, de parede a parede, cada uma com metade dele e uma sobreposição curta no meio. Ficam as faces finas e a sombra curta; sai o trilho tracejado. Antes, a faixa de 4 px de cada lado da linha volta ao piso, sem o traço e o tracejado antigos. O vão para na primeira parede a partir das folhas: na Casa A, o trilho da antessala seguia no PDF, no mesmo alinhamento, até o banho feminino; na primeira tentativa, o vidro atravessou a parede, e a regra foi corrigida.

Boxes refeitos:
- **Casa A.** Subsolo: banho de serviço, antessala, banho feminino. Térreo: banho do motorista, banho varanda. 1º Pavimento: banhos 1, 2, 3, master e de serviço.
- **Casa C.** Térreo: BH 1, 2 e 3 e a ducha entre os lavabos. Subsolo: BH academia.
- **Casa D.** Térreo: banhos 1, 2 e 3 e WC DCE. Subsolo: WC DCE.
- **Casa E.** Térreo: WC DCE 1 e banho gourmet. Os mesmos dois aparecem no Térreo esmaecido do 1º Pavimento.

Como:
- **Casa A:** as etapas aplicadas sobre as finais, no lugar (`--so`); o motor da Casa A não tem cache.
- **Casas C, D e E:** os motores refeitos da etapa dos boxes. Eles redesenham também as paredes, com o antialias das bordas 1 px diferente do da final aprovada, e nas Casas C e D saem antes do turquesa. Por isso as finais aprovadas recebem só a faixa de cada box (`colar_boxes.py`), sem o turquesa e as bordas de novo.
- **Conferência:** fora das faixas dos boxes, nenhum px mudou nas finais.

Comandos no README dos scripts, em "Os boxes dos chuveiros fechados, sem tracejado".

Antes e depois (o antes é a final de 42c3dda): `POE642_Casa{A,C,D,E}/renders/POE642_Casa*_PH_*_2810_boxes_*_antes_depois.jpg`.

Pranchas e PDFs das Casas A, C, D e E refeitos.


### Pedidos de 28/10/26: porta do WC DCE da Casa D e nicho da cabine da Casa E

O usuário:
- com o OK pendente: "ok, pode corrigir o nicho da cabine da casa E";
- com o recorte do WC DCE do Térreo da Casa D: "CORRIJA A EXISTÊNCIA DE UMA SEGUNDA PORTA, ATRÁS DA PRINCIPAL. REMOVA ESSA PORTA QUE ESTÁ ATRÁS"; depois, "REMOVA ESSE TRACEJADO NA PONTA DA PORTA".

**Casa D, WC DCE.** A porta é de giro e está aberta junto ao box. A segunda folha era uma cópia do vidro do box: a limpeza das esquadrias leva a folha antiga do render ao piso espelhando o que está ao lado, e ao lado estava o box. Entre a folha do PDF e o box, o piso volta ao de antes das esquadrias (`entre_porta_box_td`). O "tracejado na ponta da porta" eram as colunas das duas pontas da folha, que ficavam fora da faixa, em claro e escuro alternados; entraram também. Conferido no resto da Casa D e na Casa C: só o WC DCE tinha a cópia.

**Casa E, Subsolo, nicho da cabine.** Na parede da direita da cabine do chuveiro do vestiário, onde chega o braço, o nicho do PDF (o branco na espessura da parede) estava como um retângulo de moldura escura do render. Agora é travertino, como o nicho da ducha do ambiente: um pouco mais escuro que o piso, com a sombra curta do fundo e da lateral de cima. O chuveiro da cabine vem por cima. Refeito de `--de vestiario`; só o nicho mudou.

Antes e depois:
- `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_2810_wc_dce_segunda_porta_antes_depois.jpg`;
- `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_2810_nicho_cabine_antes_depois.jpg`.

Pranchas e PDFs das Casas D e E refeitos.

### Revisão de 28/10/26 do Subsolo da Casa E: contorno da piscina, barra de alongamento e batentes do elevador

O usuário: "VAMOS REVISAR O SUBSOLO DA CASA E". A revisão contra o PDF e as regras achou 3 inconformidades, apresentadas antes de alterar (folha com a final e o PDF lado a lado). A resposta: "ITEM 1: OK / ITEM 2: NÃO É TV É UMA BARRA COM BARRAS AO MEIO PARA ALONGAMENTO / ITEM 3: OK".

1. **Contorno da piscina.** No PDF, a borda branca (11,4 pt) contorna a piscina inteira: desce pela esquerda até o fim, passa sob a parede de baixo, sobe em degrau e segue sob a parte da direita até o degrau da sauna. Ela é pintada por cima da parede, depois dela. Na final, a borda de Bege Bahia da esquerda parava no meio e o canto todo era parede cinza, num bloco grosso. Agora a borda vai em Bege Bahia até o fim, como o resto, e a parede fica só nas faixas cinza do desenho, entre a água e a borda. Do lado de fora, a hachura chega até a pedra, sem a franja da parede antiga.
2. **Barra de alongamento** (não é TV). Junto à parede do DCE, ia só a barra escura do meio, e parecia uma TV solta no vinílico. Agora vai a moldura do PDF (ARQ_MARCENARIA) em madeira, presa na parede, e as barras do meio cromadas, como tubos, com os traços finos e a sombra curta.
3. **Batentes do elevador.** O da esquerda era um toco marrom largo, com uma mancha escura ao lado, e o da direita quase não aparecia. Agora os dois são finos e iguais, no cinza das paredes, como no PDF e na entrada do elevador do Subsolo da Casa D, com o vinílico inteiro em volta.

Conferido sem inconformidade: circulação e depósito; DCE, WC DCE 2 e o box; portas e soleiras; aparelhos da academia; sauna, ambiente e vestiário; as duas casas de máquinas; cabine e rótulo do elevador; escada.

Antes e depois: `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_2810_revisao_{piscina_contorno,barra_alongamento,elevador_batentes}_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa E refeitos.

### Revisão de 28/10/26 do Térreo da Casa E: adega, pisantes, curva da pedra portuguesa e projeção da cobertura

O usuário: "VAMOS REVISAR O TÉRREO DA CASA E". A revisão contra o PDF e as regras achou 3 inconformidades, apresentadas antes de alterar: a porta da adega, os pisantes e a curva da pedra portuguesa. O usuário respondeu "pode". Depois perguntou de qual prancha a revisão tinha partido ("a última tinha os tracejados das projeções"). A comparação com a prancha de 27/10 mostrou que o tracejado da projeção da cobertura sobre o granito tinha sumido na rodada de 28/10, 01:47, quando o granito foi refeito. Isso entrou como item 4. A resposta: "pode aplicar os 4". Durante a aplicação, o usuário pediu ainda: "essas manchas nas pedras da vegetação antiga precisam ser removidas".

1. **Porta da adega.** No vão, o render deixou uma faixa cinza borrada e um dente claro no lugar da porta. Agora vai a porta de vidro de correr do PDF, como as do Subsolo: a soleira de Bege Bahia, os batentes, o vidro fixo da esquerda e as duas folhas de correr nos seus planos, com os montantes. O travertino do hall vai até a porta.
2. **Pisantes.** Os 9 pisantes do caminho estão nos retângulos do PDF, com a borda reta, em Bege Bahia limpo e com a sombra curta. Saíram os dentes, as bordas claras e as manchas da vegetação antiga. Na pedra grande do acesso, à esquerda dos pisantes, saíram as folhas sobre a borda da direita e sobre o canto de baixo, e a borda ficou na reta do PDF. A grama em volta ficou sem a borda clara e sem os restos da pedra.
3. **Curva da pedra portuguesa.** A borda contra a grama era em degraus. Agora segue a curva do PDF, lisa, nas duas curvas. Saiu a mancha escura junto ao arbusto de cima.
4. **Projeção da cobertura.** O tracejado cinza fino voltou nas linhas do PDF, como na prancha de 27/10 e na varanda: a laje da garagem sobre a circulação, a borda de cima do granito e a lateral direita. Ele não passa sobre as paredes.

O 1º Pavimento mostra o Térreo nublado em volta. Ali entraram os pisantes, a curva e o tracejado novos. A adega fica sob a pegada.

Antes e depois:
- Térreo: `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_revisao_{adega_porta,pisantes,curva_pedra_portuguesa,curva_mancha,projecao_cobertura,projecao_cobertura_canto}_antes_depois.jpg`;
- 1º Pavimento: `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_revisao_terreo_nublado_antes_depois.jpg`.

Pranchas do Térreo e do 1º Pavimento e PDF da Casa E refeitos.

### Pedido de 28/10/26: a seta da entrada e o rótulo do hall do Térreo da Casa E

O usuário, com o recorte do hall: "A seta em preto deve ficar em frente a porta, um pouco mais acima de onde ela está. e o rótulo do hal de entrada não pode ficar sobre o tracejado."
- **Seta.** No PDF, o vão da porta pivotante vai do batente de cima (1488,3 pt) ao de baixo (1638,6 pt). A seta apontava para o vidro fixo, abaixo dele. Agora a ponta fica no meio do vão, 134 px (~2,2 m) acima de onde estava. No lugar antigo ficou o Bege Bahia da pedra.
- **Rótulo do HALL DE ENTRADA.** Ele estava sobre a diagonal do X tracejado. Agora fica à direita do cruzamento do X, entre ele e a porta, no mesmo corpo dos outros rótulos. É o lugar do hall com mais folga do tracejado, das paredes e dos objetos (~10 px). O outro lugar livre, abaixo da folha da porta, ficava mais apertado (~7 px). Na parte de baixo do X, o rótulo cairia sobre a planta.

Antes e depois: `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_seta_rotulo_hall_antes_depois.jpg`. Prancha do Térreo e PDF da Casa E refeitos. O 1º Pavimento não muda: o Térreo nublado não leva a seta nem os rótulos.

### Pedidos de 28/10/26: a borda reta da varanda e os tracejados em preto ou branco (Térreo da Casa E)

O usuário, com o recorte da borda de baixo da varanda: "não existe esse dente. o tracejado é em linha reta". Depois: "os tracejados são ou brancos ou pretos, a depender do fundo".
- **Borda reta.** O tracejado da laje da varanda vinha do retoque. Ele seguia a borda da varanda do 1º Pavimento e, a partir de 1204,5 pt, a face da parede da suíte 3, 10 cm acima, com um degrau entre as duas. Agora segue a borda da laje (a do PDF do 1º Pavimento, 1694,1 pt), reto até a fachada da sala. A planta do canto e a sombra dela ficam.
- **Preto ou branco.** Todos os tracejados de projeção do Térreo estavam em cinza: o L da varanda e do gourmet, a laje da garagem, a borda de cima e a lateral do granito, o X do hall e o X da área de serviço descoberta. Agora são traços nítidos em preto nos pisos claros (Bege Bahia, travertino, pedra portuguesa) e em branco no granito e nas bordas contra a grama, como nas Casas A e B. A cor troca onde o piso troca: na borda de cima, preto no Bege Bahia do gourmet e branco no granito. As linhas do lote não mudam.
- **1º Pavimento.** Como no 1º Pavimento da Casa A, o Térreo nublado não leva as projeções do Térreo. O tracejado da cobertura que tinha entrado ali com a revisão saiu.
- **Inconformidade apresentada (resolvida abaixo, opção A):** o rótulo da ÁREA DE SERVIÇO DESCOBERTA fica sobre o X tracejado (o nome em duas linhas e a área). Com o rótulo inteiro, não há lugar livre do X no cômodo (a busca achou no máximo 2 px de folga). Imagem: `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_area_servico_rotulo_sobre_x.jpg`.

Antes e depois: `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_{varanda_borda_reta,tracejados_varanda_gourmet,tracejados_hall,tracejados_granito}_antes_depois.jpg` e `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_nublado_sem_projecoes_antes_depois.jpg`. Pranchas do Térreo e do 1º Pavimento e PDF da Casa E refeitos.

### Pedidos de 28/10/26: o X aberto sob o rótulo da área de serviço e os tracejados do 1º Pavimento (Casa E)

O usuário, sobre as duas perguntas da rodada anterior: "item 1: A. item 2: pode".
- **Área de serviço descoberta (Térreo), opção A.** O rótulo (o nome em duas linhas e a área, no corpo de sempre) foi para o cruzamento do X tracejado, e o X se abre em volta dele: os traços param numa folga de ~13 cm do texto, como no X do shaft da Casa B. Os traços que estavam no vão e as letras no lugar antigo do rótulo saíram sem mancha (o granito ao lado).
- **Tracejados do 1º Pavimento.** Estavam em cinza: os X dos dois vazios (o da escada e o do hall, sobre o Térreo nublado), o X do shaft, o desenho da rouparia e os X rasos do banho master, sobre o vaso e o box. Agora são traços nítidos, em preto nos fundos claros e, na rouparia (sobre o vinílico), em branco. O cinza antigo saiu antes, com o fundo ao lado. Os rótulos ficam por cima.
- **Subsolo.** A final do Subsolo não desenha tracejado de projeção (as curvas de nível, a escada e as linhas da academia do PDF ficam fora), então não mudou.
- **Inconformidades vistas, apresentadas ao usuário (resolvidas abaixo, com o OK):**
  1. o rótulo ROUPARIA (1º Pavimento) fica sobre o desenho tracejado da rouparia, como estava o da área de serviço; proposta: a mesma opção A (o tracejado parando numa folga em volta do texto);
  2. no vazio do hall (1º Pavimento), na borda da esquerda, aparece bem fraco um tracejado vertical do Térreo nublado (a linha da esquerda do X do hall do Térreo); pela regra do nublado sem as projeções do Térreo, ele sairia.
  Imagem: `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_inconformidades_rouparia_vazio_hall.jpg`.

Antes e depois: `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_area_servico_vao_x_antes_depois.jpg` e `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_tracejados_{planta,banho_master,shaft_rouparia,vazio_escada,vazio_hall}_antes_depois.jpg`. Pranchas do Térreo e do 1º Pavimento e PDF da Casa E refeitos.

### Pedidos de 28/10/26: rouparia e Térreo nublado no vazio do hall (1º Pavimento da Casa E)

O usuário, sobre as duas inconformidades: "item 1: A. item 2: pode".
- **Rouparia, opção A.** O desenho tracejado da rouparia agora para numa folga em volta do rótulo, como o X da área de serviço do Térreo. O texto é mais largo que o desenho, então a folga é proporcional (~7 cm): ficam a borda de cima, a de baixo e o pé das pernas do desenho. O halo escuro que o render deixava em volta do traço antigo também saiu.
- **Vazio do hall.** O tracejado fraco do Térreo (a linha da esquerda do X do hall do Térreo) saiu do nublado; o X do vazio é só o do 1º Pavimento.
- **Cantos dos vazios.** Revendo de perto, os cantos dos dois vazios tinham restos do cinza antigo e o tom da escada ou do vidro puxado para dentro (já na entrega anterior). A limpeza agora preserva as linhas da borda (a linha do degrau, o vidro, a face da parede) e o degradê do nublado; o X vai de canto a canto.

Antes e depois (o antes é a entrega anterior, ee4c56e): `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_{rouparia_vao,vazio_hall_sem_terreo,vazio_escada_bordas}_antes_depois.jpg`. Prancha do 1º Pavimento e PDF da Casa E refeitos.

### Pedidos de 28/10/26: sofá da sala íntima, poltrona da suíte master e poltronas do living (Casa E)

O usuário: "corrija a imperfeição no sofá gerada pelo piso. no primeiro pavimento da casa E"; "corrija o contorno do encosto da poltrona da suite master"; "vamos aplicar essa poltrona da sala íntima do primeiro pavimento da casa e em substituição das poltronas a todas as 6 poltronas do terreo, também da casa E".
- **Sofá da sala íntima (1º Pavimento).** Os dois entalhes do piso no topo do encosto saíram; a borda do encosto fica reta de ponta a ponta, com as emendas das almofadas logo abaixo.
- **Poltrona da suíte master (1º Pavimento).** O contorno ficou liso, sem os calombos, o serrilhado e a franja clara de baixo; o tapete e a mesa lateral não mudam.
- **Poltronas do living (Térreo).** As 6 bouclé (as 2 no tapete, junto à mesa de centro, e as 4 em volta da mesa redonda) agora são a poltrona da sala íntima do 1º Pavimento, cada uma no tamanho e na posição do PDF, de frente para a mesa, com uma sombra curta mais marcada para não sumir no travertino. As bouclé saíram com o halo escuro que o retoque tinha deixado em volta; o travertino volta contínuo, com o veio, e o tapete com o grão e a borda; a sombra da mesa redonda foi refeita.
- **Inconformidade vista, apresentada ao usuário (resolvida abaixo, com o OK):** no 1º Pavimento, a faixa do Térreo nublado logo abaixo da sala íntima ainda mostra, esmaecidas, as 2 bouclé de baixo da mesa redonda (o nublado vem do Térreo de antes); proposta: refazer o nublado com o Térreo novo, para mostrar as poltronas novas. Imagem (em cima o 1º Pavimento, embaixo o Térreo novo): `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_inconformidade_nublado_poltronas.jpg`.

Antes e depois (o antes é a entrega anterior, da8fecd): `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_{sofa_sala_intima,poltrona_suite_master}_antes_depois.jpg` e `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_poltronas_living_antes_depois.jpg`. Pranchas do Térreo e do 1º Pavimento e PDF da Casa E refeitos.

### Pedido de 28/10/26: o Térreo nublado do 1º Pavimento com as poltronas novas (Casa E)

O usuário, sobre a inconformidade: "pode refazer o nublado".
- **Térreo nublado.** A faixa do Térreo nublado logo abaixo da sala íntima agora mostra as poltronas novas do living, no lugar das 2 bouclé antigas, com o halo delas fora. Só esse trecho do 1º Pavimento mudou.

Antes e depois (o antes é a entrega anterior, d0357e5): `POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_2810_nublado_poltronas_antes_depois.jpg`. Prancha do 1º Pavimento e PDF da Casa E refeitos.

### Pedidos de 28/10/26: contorno do tapete atrás das poltronas e sofá da varanda (Térreo da Casa E)

O usuário: "precisa aprimorar o contorno do tapete na parte onde incluimos as poltronas, logo atrás dela. seguindo a direção correta e dando a impressão de continuidade"; "você consegue substituir o sofá da varanda da casa e pelo sofá da sala íntima do primeiro pavimento, deixando apenas a parte horizontal? teria que remover o último módulo do L para dar certo".
- **Tapete do living.** Atrás das duas poltronas sobre o tapete, a borda agora segue a curva do tapete de um lado ao outro, em diagonal, contínua por trás delas (antes fazia um dente atrás da poltrona de cima).
- **Sofá da varanda.** No lugar do sofá branco com as almofadas cor de palha entrou o sofá da sala íntima do 1º Pavimento, só a parte reta: os três módulos de cima, sem o último módulo do L; o encosto da esquerda termina arredondado, como o braço da direita. Ele está na medida do sofá do PDF (3,4 x 1,2 m), com as almofadas do modelo e a sombra curta. O Bege Bahia em volta foi refeito contínuo, sem o halo do sofá antigo.
- O sofá e as poltronas do tapete ficam sob a laje do 1º Pavimento: o Térreo nublado do 1º Pavimento não muda.

Antes e depois (o antes é a entrega anterior, 218727c): `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_{tapete_poltronas,sofa_varanda}_antes_depois.jpg`. Prancha do Térreo e PDF da Casa E refeitos.

### Pedidos de 28/10/26: sofá da varanda sem sombra (Térreo) e borda da piscina do Subsolo (Casa E)

O usuário: "subsolo da casa e"; "precisamos melhorar o aspecto do sofá e remover a sombra"; "na parte de baixo da piscina está invertido: a parede é a parte de baixo e a borda da piscina a parte de cima. entendeu?".
- **Sofá da varanda (Térreo).** As duas pontas agora são iguais: no lugar do encosto que seguia na perna do L entrou o braço da direita, espelhado. O sofá está na proporção do modelo (antes estava esticado para a profundidade do PDF, o que afinava as almofadas), no comprimento do PDF, sem sombra no piso; a beirada do estofado, um pouco mais escura, marca o contorno sobre o Bege Bahia.
- **Piscina do Subsolo.** Na parte de baixo, a faixa de Bege Bahia (a borda) passou para junto da água, nas duas partes da piscina (a funda e a do degrau), com os cantos retos, e a parede escura ficou por fora, fechando também o canto de baixo à esquerda.
- **Revisão do Subsolo.** Revendo o Subsolo inteiro de perto (circulação, academia, DCE e WC DCE 2, depósito, casas de máquinas, sauna, ambiente, vestiário, elevador), não apareceu outra inconformidade além da piscina.

Antes e depois (o antes é a entrega anterior, 4e4108d): `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_sofa_varanda_sem_sombra_antes_depois.jpg` (a imagem da troca da borda saiu; a piscina foi refeita abaixo). Pranchas do Subsolo e do Térreo e PDF da Casa E refeitos.

### Pedido de 28/10/26: só parede embaixo da piscina do Subsolo (Casa E)

O usuário, vendo a borda de Bege Bahia passada para junto da água: "o subsolo ficou horrivel, deixe apenas parede na parte de baixo sem borda".
- **Piscina do Subsolo.** A parte de baixo da piscina agora é só parede, um bloco reto como o do PDF, sem a faixa de Bege Bahia, nas duas partes (a funda e a do degrau). A borda de Bege Bahia do lado esquerdo continua ao lado da água até o fundo dela. A troca anterior foi desfeita (refeito a partir do Subsolo de 4e4108d).

Antes e depois (o antes é a entrega anterior, 5418bb9): `POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_2810_piscina_so_parede_antes_depois.jpg`. Prancha do Subsolo e PDF da Casa E refeitos.

**Aprovado** (28/10/26): "subsolo da casa E aprovado", com a parte de baixo da piscina só em parede (883d600). A final do Subsolo da Casa E fica como está; o Térreo e o 1º Pavimento da Casa E seguem aguardando a validação.

### Pedidos de 28/10/26: braço da esquerda do sofá da varanda (Térreo da Casa E)

O usuário, com o recorte do sofá da varanda: "consegue refinar mais ainda esse braço da esquerda do sofá?"; e, com o recorte da junção do braço com o assento: "corrija também a parte interna do braço".
- **Braço da esquerda.** Antes era o braço da direita espelhado e esticado, com a faixa da almofada marrom alisada: lia como uma tira chapada e clara. Agora o braço é o próprio estofado do render (o encosto que seguia na perna do L), com o rolo de fora, o vinco e o canto arredondado de cima ligado ao encosto de trás. Só a ponta de baixo, o arredondado, vem do braço da direita espelhado, numa passagem suave.
- **Parte interna do braço.** Da almofada para baixo, a junção do braço com o assento e a quina da frente do assento vêm do lado direito espelhado, no tom do assento do canto (que fica à sombra das almofadas). Saíram a costura do módulo da perna do L, o vinco escuro em Y no pé do braço e o fio marrom ao lado da almofada.
- O sofá fica sob a laje do 1º Pavimento: o Térreo nublado não muda.
- **Para o OK (nada alterado; feito na seção seguinte, com o OK):** à direita do braço da direita, no Bege Bahia, sobrou uma manchinha clara e vertical (cerca de 4 x 18 px), resto do sofá antigo logo fora do retângulo refeito. Proposta: alargar 4 px o retângulo à direita (`SOFA_VARANDA_TE["buraco"]`) para o Bege Bahia cobrir a mancha.

Antes e depois (o antes é a entrega anterior, 6d0183a): `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_sofa_varanda_braco_antes_depois.jpg` (o sofá inteiro) e `..._2810_sofa_varanda_braco_detalhe_antes_depois.jpg` (o braço ampliado). Prancha do Térreo e PDF da Casa E refeitos.

### Pedidos de 28/10/26: sofá da varanda simétrico e a manchinha ao lado do braço (Térreo da Casa E)

O usuário: "ok, pode alargar e tirar a mancha"; e, enquanto isso: "por que não pegar todo o modulo da direita e espelhar para a esquerda, usando as almofadas?".
- **Sofá simétrico.** No lugar do módulo do canto (com as duas almofadas creme e o braço montado a partir do encosto do L) entrou o módulo da direita inteiro, espelhado: o braço, a almofada creme e a marrom. O módulo do meio ficou entre os dois, com a beirada esquerda igualada à direita, para as duas costuras ficarem iguais (a da esquerda tinha um fio claro e a sombra das almofadas do canto).
- **Medida.** O sofá continua no comprimento do PDF (3,4 m). Com os dois módulos de ponta, que são mais largos que o do canto, ele fica com 0,97 m de fundo (antes 1,04 m; o PDF tem 1,2 m). Alternativa, se preferir mais fundo: estreitar o assento do meio (ele ficaria cerca de 1/4 mais estreito que os das pontas) para o sofá voltar a 1,04 m de fundo.
- **Manchinha.** Com o OK, o Bege Bahia em volta do sofá foi refeito até 7 px mais à direita (4 px não bastavam, porque o reflexo puxava o próprio resto cinza); a mancha saiu.
- O sofá fica sob a laje do 1º Pavimento: o Térreo nublado não muda.

Antes e depois (o antes é a entrega anterior, b5d85bc): `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_sofa_varanda_simetrico_antes_depois.jpg`. Prancha do Térreo e PDF da Casa E refeitos.

**Aprovado** (28/10/26): "pode deixar assim, está aprovado", o sofá da varanda simétrico como está (e2d6c84), com os 0,97 m de fundo (sem estreitar o assento do meio). O resto do Térreo e o 1º Pavimento da Casa E seguem aguardando a validação.

### Pedido de 28/10/26: sofá da varanda no fundo do anterior (Térreo da Casa E)

O usuário: "o sofá ficou nas dimensões do anterior?". Medido na planta: o anterior tinha ≈ 3,45 x 1,19 m (o PDF, 3,39 x 1,17 m), e o simétrico ≈ 3,35 x 0,95 m, no comprimento do PDF e mais raso (o sofá da sala íntima, com as duas pontas, tem 4,0 m e foi reduzido inteiro). Resposta do usuário: "pode aumentar o sofá para ter a mesma altura, preservando a proporcionalidade".
- **Sofá da varanda.** Aumentado na mesma proporção até o fundo do anterior (1,17 m, o do PDF): fica com 4,07 x 1,17 m, centrado no lugar do sofá do PDF. Passa uns 30 cm de cada lado do sofá anterior; em volta continua livre: o brise à esquerda fica a ~0,85 m, o guarda-corpo de vidro à direita a ~0,55 m e o banco embaixo a ~0,8 m; o encosto fica na mesma linha, abaixo do rótulo da varanda, como antes.
- O sofá fica sob a laje do 1º Pavimento: o Térreo nublado não muda.

Antes e depois (o antes é a entrega anterior, 3e0b48c): `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_sofa_varanda_fundo_antes_depois.jpg`. Prancha do Térreo e PDF da Casa E refeitos.

### Pedido de 28/10/26: sofá da varanda um pouco menor e com sombra leve (Térreo da Casa E)

O usuário: "diminua um pouco o tamanho" e "jogue um leve efeito de sombra para mostrar que o sofá está integrado ao piso".
- **Tamanho.** 10% menor, na mesma proporção: 3,67 x 1,06 m (antes 4,07 x 1,17 m; o PDF tem 3,39 x 1,17 m), com o encosto na mesma linha e centrado no lugar do sofá do PDF.
- **Sombra.** A mesma sombra das poltronas novas do living (curta, para baixo e para a esquerda, mais a de contato), mais fraca (45% e 30%, contra 60% e 30% nas poltronas) e suave, sem borda dura. Na primeira prova ela saía cortada num retângulo, porque o desfoque ficava preso à caixa do sofá; o sofá passou a ir com uma margem em volta.
- O sofá fica sob a laje do 1º Pavimento: o Térreo nublado não muda.

Antes e depois (o antes é a entrega anterior, 24743ab): `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_sofa_varanda_sombra_antes_depois.jpg`. Prancha do Térreo e PDF da Casa E refeitos.

**Aprovado** (28/10/26): "ficou bom, sofá aprovado", o sofá da varanda como está (964186a): simétrico, 3,67 x 1,06 m, com a sombra leve. O tapete atrás das poltronas, o resto do Térreo e o 1º Pavimento da Casa E seguem aguardando a validação.

### Pedido de 28/10/26: tracejado da borda de baixo da garagem em branco (Térreo da Casa E)

O usuário, com o recorte da garagem: "esse tracejado em branco".
- **Tracejado da garagem.** A borda de baixo da laje da garagem corre sobre a divisa do granito com a pedra portuguesa do acesso; os traços tinham saído pretos (a cor vem do fundo em volta, ali metade pedra clara) e entre eles aparecia a linha cinza antiga do retoque, que de longe parecia um tracejado branco. Agora os traços são brancos, nos mesmos lugares, e a linha cinza saiu: entre os traços, o granito de um lado e a pedra do outro. Os outros lados da laje (o de cima e o da direita, sobre o granito) já eram brancos.
- O Térreo nublado do 1º Pavimento não leva as projeções do Térreo: não muda.

Antes e depois (o antes é a entrega anterior, f798821): `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_2810_tracejado_garagem_antes_depois.jpg`. Prancha do Térreo e PDF da Casa E refeitos.

**Aprovado** (28/10/26): "ok, aprovado", o tracejado da borda de baixo da garagem em branco (e058833). O tapete atrás das poltronas, o resto do Térreo e o 1º Pavimento da Casa E seguem aguardando a validação.

**Térreo da Casa E aprovado** (28/10/26): "térreo da casa E aprovado". A final `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png` fica como está (0c64bd4), com tudo o que estava em validação: a revisão de 28/10, os tracejados em preto ou branco, a seta e os rótulos, as cortinas, as poltronas do living e o tapete atrás delas, o sofá da varanda, o tracejado da garagem, a piscina (tom, bordas e vidros) e o box do banho gourmet. Na Casa E, o Subsolo e o Térreo estão aprovados; o 1º Pavimento segue aguardando a validação.

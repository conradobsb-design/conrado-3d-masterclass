# Método — planta humanizada fiel a partir da imagem do cliente
_Conrado 3D Studio · consolidado no POE 642 · Casa A, 13/10/2026._

## O princípio
A IA não garante geometria. Nenhum prompt garante que paredes, vidros e móveis fiquem exatamente onde o cliente desenhou:
- prompt longo faz o motor redesenhar a planta;
- prompt curto de edição deixa a planta vazia;
- edição sem máscara altera o que já estava aprovado.

Por isso a fidelidade fica em etapas **determinísticas**, antes e depois da IA. A IA entra só no que faz bem: textura de piso, vegetação, água e acabamento de móveis.

| Etapa | Quem faz | Garante |
|---|---|---|
| 1. Base limpa | script (PDF) ou Photoshop (PNG/JPG) | leitura sem ambiguidade |
| 2. Render | IA, uma passada | realismo e estilo |
| 3. Trava de fidelidade | script | geometria idêntica à base |
| 4. Retoques locais | IA **com máscara** | mudança só onde precisa |
| 5. Pós | Photoshop | norte, escala, setas |

## 1. Base limpa (o que a IA recebe)
Regras que valem para qualquer projeto:
- **Paredes em preto puro #111111.** Nada de cinza: parede cinza com contorno preto é lida como vidro. Foi o que aconteceu com a parede do estar no POE 642.
- **Vidro e janela** como linha cinza-claro #D6D6D3 entre dois caixilhos pretos. Nunca azul.
- **Cada material numa cor chapada única**, conforme a legenda do projeto (travertino, granito, madeira, Bege Bahia, piscina…).
- **Sem texto:** nem cotas, nem nomes, nem carimbo.
- **Tela 16:9 com margem branca**, porque o motor trabalha em 16:9 e não deve reenquadrar.

Como fazer:
- **PDF do cliente:** `scripts/gerar_bases.py` (remove texto, pinta paredes, separa vidro, gera a versão 16:9). Antes, rode `--listar-layers` em todo PDF novo.
- **PNG/JPG do cliente:** no Photoshop, ~20 min. Use o balde de tinta por ambiente com as cores da legenda, pinte as paredes de preto, os vidros de cinza-claro com caixilho preto, e apague os textos.

## 2. Render com IA (uma passada)
- **Nano Banana Pro, 2K, 16:9, duas imagens:**
  1. a base;
  2. a **referência de estilo do estúdio**. A planta aprovada do POE 642 pode virar o padrão visual para todos os projetos.
- **Prompt-modelo:** `POE642_CasaA_PH_Terreo_v25.md`. É um prompt de edição com seis blocos: pisos por cor, jardins, móveis, marcenaria e bancadas, paredes e vidros, luz. Para outro projeto, troque só a tabela de materiais e os ambientes.
- **Aceite pequenas derivas de geometria.** A etapa 3 corrige.

## 3. Trava de fidelidade (determinística)
Um script alinha o render à base e recoloca por cima, **a partir da base**:
- paredes;
- vidros e janelas;
- gradis;
- portas;
- o traço dos móveis.

Assim a geometria final é idêntica à do cliente, enquanto pisos, vegetação e acabamentos continuam vindo da IA. O script também aponta onde a IA trocou o material de uma zona, por exemplo grama sobre piso ou piso cinza onde deveria ser pedra.
_Status: a construir. Precisa da base e de um render reais para calibrar o alinhamento e os limiares._

## 4. Retoques locais — sempre com máscara
Para mudar um ponto de uma imagem aprovada (cor de marcenaria, bancada, um piso):
- **Photoshop, Preenchimento generativo:** só a seleção muda. Para troca de cor pura, use camada de cor, sem IA.
- **Higgsfield, Nano Banana 2 com inpaint e máscara.** O Nano Banana Pro não aceita máscara.
- Uma área por vez. Prompts prontos em `POE642_CasaA_PH_Terreo_v25_ajuste_mascara.md`.

## 5. Pós-produção
Norte, escala gráfica, setas de subida das escadas e eventuais legendas, sempre fora do motor.

## Checklist de entrega
- [ ] Paredes, vidros, janelas, gradis e portas conferidos contra o desenho do cliente (sobreposição em modo *Diferença*).
- [ ] Cada piso no material da legenda, sem cor chapada sobrando.
- [ ] Vegetação só dentro do lote e fora de pisos, decks e piscina.
- [ ] Móveis com o desenho do cliente, sem troca de modelo.
- [ ] Sem texto do motor, sem sombras e sem perspectiva.
